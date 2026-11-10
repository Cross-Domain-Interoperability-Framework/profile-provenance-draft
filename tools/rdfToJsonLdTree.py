#!/usr/bin/env python3
"""
RDF to tree-shaped JSON-LD

Converts any RDF document (Turtle, or JSON-LD such as a flattened @graph) into compacted,
tree-shaped JSON-LD, so the provenance approaches in examples/ can be compared in the JSON-LD form
CDIF's RDF implementations use.

Usage:
    python tools/rdfToJsonLdTree.py SRC OUT [--base IRI] [--root IRI]

    --base  base IRI for relative @ids (e.g. an RO-Crate's "./"); they are written back relative.
    --root  IRI or CURIE of the node to root the tree on, overriding the Dataset rule.

Layout:
- The root is the --root node, else the schema:Dataset when there is one. A node not reached from it
  that points into the tree (an RO-Crate metadata descriptor's schema:about, a DDI-CDI agent's
  ProcessingAgent_performs_Activity) is nested with @reverse under the node nearest the root that it
  points at, and
  anything still unconnected goes in the root's @included, so the root is the one top-level object.
  Otherwise roots are the named nodes nothing else points at, largest tree first, in @graph when
  there are several.
- A node is described in full where it is first reached and is an {"@id"} reference after that.
  Blank nodes are nested; one gets an @id only if it is referenced more than once.
- Prefixes come from the source (Turtle @prefix lines, plus common namespaces under their usual
  prefixes). Properties appear in the order they first occur in the source.
- Literals keep their exact datatype: a datatype used uniformly by one property is coerced in
  @context, otherwise the value is written {"@value", "@type"}.

The output is checked: rdflib and pyld must both read it back as a graph isomorphic to the source;
the script exits 1 if either does not.
"""
import sys, json, re, argparse
import rdflib, rdflib.compare
from rdflib import BNode, Literal, URIRef
from rdflib.namespace import RDF, XSD
from collections import Counter, defaultdict
rdflib.NORMALIZE_LITERALS = False

ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('out'); ap.add_argument('--base')
ap.add_argument('--root', help='IRI or CURIE of the node to root the tree on (overrides the Dataset rule)')
a = ap.parse_args()
text = open(a.src, encoding='utf-8').read()
is_ttl = a.src.endswith('.ttl')
g = rdflib.Graph().parse(data=text, format='turtle' if is_ttl else 'json-ld', publicID=a.base)

KNOWN = {'schema': 'http://schema.org/', 'prov': 'http://www.w3.org/ns/prov#', 'xsd': str(XSD),
         'rdf': str(RDF), 'rdfs': 'http://www.w3.org/2000/01/rdf-schema#', 'dcterms': 'http://purl.org/dc/terms/',
         'ex': 'https://example.org/cdif-prov/', 'bios': 'https://bioschemas.org/'}
if is_ttl:
    PFX = dict(re.findall(r'^@prefix\s+(\w*):\s*<([^>]+)>', text, re.M))
else:                                   # a JSON-LD source's own prefixes, when its @context is inline
    ctx0 = json.loads(text).get('@context')
    PFX = {k: v for k, v in ctx0.items() if isinstance(v, str) and not k.startswith('@')} if isinstance(ctx0, dict) else {}
for k, v in KNOWN.items():              # a known namespace keeps its usual prefix (not e.g. schema1)
    for k2 in [k2 for k2, v2 in PFX.items() if v2 == v and k2 != k]: del PFX[k2]
    if k not in PFX: PFX[k] = v

def q(u):
    u = str(u)
    if a.base and u.startswith(a.base): return u[len(a.base):] or './'
    best = max(((p, ns) for p, ns in PFX.items() if u.startswith(ns)), key=lambda x: len(x[1]), default=None)
    return f'{best[0]}:{u[len(best[1]):]}' if best else u
used_pfx = set()
def qq(u):
    s = q(u)
    if ':' in s and s.split(':', 1)[0] in PFX: used_pfx.add(s.split(':', 1)[0])
    return s

# order of first appearance in the source text (Turtle CURIEs, or JSON-LD keys / full IRIs)
def first_pos(term):
    s = q(term); cands = [s, str(term)] + ([] if is_ttl else [s.split(':', 1)[-1]])
    hits = [m.start() for c in cands for m in [re.search(r'(?<![\w/#])' + re.escape(c) + r'(?![\w])', text)] if m]
    return min(hits) if hits else len(text)

named = {x for x in set(g.subjects()) | set(g.objects()) if isinstance(x, URIRef) and (x, None, None) in g}
incoming = Counter(o for s, p, o in g if p != RDF.type and not isinstance(o, Literal))
roots = sorted((n for n in named if incoming[n] == 0), key=first_pos)
roots += sorted((b for b in set(g.subjects()) if isinstance(b, BNode) and incoming[b] == 0), key=lambda b: 0)
def reach(r):                           # biggest tree first, so the main record leads
    seen, todo = set(), [r]
    while todo:
        x = todo.pop()
        if x in seen: continue
        seen.add(x); todo += [o for p, o in g.predicate_objects(x) if p != RDF.type and not isinstance(o, Literal)]
    return len(seen)
roots.sort(key=lambda r: -reach(r))

# coercion: a property whose literals all share one non-string datatype
lit_types = defaultdict(set)
for s, p, o in g:
    if isinstance(o, Literal):
        lit_types[p].add(('lang', o.language) if o.language else ('dt', o.datatype))
coerce = {p: next(iter(ts))[1] for p, ts in lit_types.items()
          if len(ts) == 1 and next(iter(ts))[0] == 'dt' and next(iter(ts))[1] not in (None, XSD.string)}

done, bn_ids, desc = set(), {}, {}      # desc: node -> the dict that describes it in full
reserved = set()                        # nodes to be placed under the root with @reverse; a reference until then
def val(o, p):
    if isinstance(o, Literal):
        if o.language: return {'@value': str(o), '@language': o.language}
        if o.datatype in (None, XSD.string): return str(o)
        if coerce.get(p) == o.datatype: return str(o)
        return {'@value': str(o), '@type': qq(o.datatype)}
    if o in done or o in reserved:
        return {'@id': bn_ids[o] if isinstance(o, BNode) else qq(o)}
    if isinstance(o, BNode) or o in named: return node(o)
    return {'@id': qq(o)}
def node(s, skip=None):                 # skip: a (predicate, object) to leave out, stated by @reverse instead
    done.add(s); n = {}; desc[s] = n
    if isinstance(s, URIRef): n['@id'] = qq(s)
    elif incoming[s] > 1: bn_ids[s] = f'_:b{len(bn_ids)}'; n['@id'] = bn_ids[s]
    ts = sorted(g.objects(s, RDF.type), key=first_pos)
    if ts: n['@type'] = qq(ts[0]) if len(ts) == 1 else [qq(t) for t in ts]
    for p in sorted({p for p in g.predicates(s) if p != RDF.type}, key=lambda p: (first_pos(p), q(p))):
        objs = sorted(g.objects(s, p), key=lambda o: (first_pos(o) if not isinstance(o, (Literal, BNode)) else 0))
        objs = [o for o in objs if (p, o) != skip]
        if not objs: continue
        vs = [val(o, p) for o in objs]
        n[qq(p)] = vs[0] if len(vs) == 1 else vs
    return n

# The root is the node named by --root, else a schema:Dataset (CDIF records are rooted on the Dataset).
# A node that is not reached from it but points into the tree (an RO-Crate metadata descriptor's
# schema:about, a DDI-CDI agent's ProcessingAgent_performs_Activity) is nested with @reverse under the
# node nearest the root that it points at. Nodes that point at the root itself (a DDI-CDI run's agent,
# PROV steps that are dcterms:isPartOf the run) are reserved and placed directly under it, so the forward
# walk cannot bury them deeper in the tree. Anything still unconnected goes in the root's @included, so
# the root stays the one top-level object.
DATASET = URIRef('http://schema.org/Dataset')
def expand(t):
    pre, _, local = t.partition(':')
    return URIRef(PFX[pre] + local if pre in PFX and not t.startswith('http') else t)
if a.root:
    main = expand(a.root)
    if main not in named: sys.exit(f'--root {a.root}: no such node in {a.src}')
else:
    datasets = sorted((n for n in named if (n, RDF.type, DATASET) in g), key=lambda r: -reach(r))
    main = datasets[0] if datasets else None
trees = []
if main is not None:
    targets = set(g.objects(main))
    direct = sorted({(s, p) for s, p in g.subject_predicates(main)
                     if s in named and s != main and s not in targets}, key=lambda sp: first_pos(sp[0]))
    reserved.update(s for s, _ in direct)
    tree = node(main)
    for s, p in direct:
        reserved.discard(s)
        if s in done: continue
        rev = tree.setdefault('@reverse', {}); k = qq(p); child = node(s, skip=(p, main))
        rev[k] = child if k not in rev else (rev[k] if isinstance(rev[k], list) else [rev[k]]) + [child]
    while True:
        cands = [(first_pos(s), s, p, o) for s, p, o in g if s in named and s not in done
                 and p != RDF.type and o in desc]
        if not cands: break
        _, s, p, o = min(cands, key=lambda c: (list(desc).index(c[3]), c[0]))   # nearest the root first
        rev = desc[o].setdefault('@reverse', {}); k = qq(p); child = node(s, skip=(p, o))
        rev[k] = child if k not in rev else (rev[k] if isinstance(rev[k], list) else [rev[k]]) + [child]
    rest = [node(r) for r in sorted((x for x in named if x not in done), key=first_pos) if r not in done]
    if rest: tree['@included'] = rest
    trees.append(tree)
trees += [node(r) for r in roots if r not in done]
left = [x for x in named if x not in done]          # nodes only reachable inside a cycle
while left:
    left.sort(key=first_pos); trees.append(node(left[0])); left = [x for x in named if x not in done]

ctx = {k: PFX[k] for k in PFX if k in used_pfx or any(qq(dt).startswith(k + ':') for dt in coerce.values())}
for p, dt in sorted(coerce.items(), key=lambda x: q(x[0])): ctx[qq(p)] = {'@type': qq(dt)}
ctx = {k: PFX[k] for k in PFX if k in used_pfx} | {k: v for k, v in ctx.items() if k not in PFX}
doc = {'@context': ctx, **trees[0]} if len(trees) == 1 else {'@context': ctx, '@graph': trees}
s = json.dumps(doc, indent=2, ensure_ascii=False) + '\n'
s = re.sub(r'\{\n\s*("@(?:id|type)": "[^"]+")\n\s*\}', r'{\1}', s)
open(a.out, 'w', encoding='utf-8', newline='\n').write(s)

r = rdflib.Graph().parse(data=s, format='json-ld', publicID=a.base)
from pyld import jsonld
opts = {'format': 'application/n-quads'}
if a.base: opts['base'] = a.base
p = rdflib.Graph().parse(data=jsonld.to_rdf(json.loads(s), opts), format='nt')
# pyld writes xsd:double / xsd:float in canonical E-notation ("46.95" -> "4.695E1"), so those compare by
# value; every other literal (e.g. a 'Z' timestamp) must match exactly as written.
FLOATS = (XSD.double, XSD.float)
def by_value(gr):
    out = rdflib.Graph()
    for s_, p_, o_ in gr:
        out.add((s_, p_, Literal(repr(float(o_)), datatype=o_.datatype)
                 if isinstance(o_, Literal) and o_.datatype in FLOATS else o_))
    return out
G, R, P = by_value(g), by_value(r), by_value(p)
iso_r, iso_p = rdflib.compare.isomorphic(G, R), rdflib.compare.isomorphic(G, P)
ok = iso_r and iso_p
print(f'{a.out}: {len(trees)} root(s) | triples src {len(g)} rdflib {len(r)} pyld {len(p)} | isomorphic rdflib',
      iso_r, 'pyld', iso_p)
sys.exit(0 if ok else 1)
