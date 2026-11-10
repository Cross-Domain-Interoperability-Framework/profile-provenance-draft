#!/usr/bin/env python3
"""
RDF to tree-shaped JSON-LD

Converts any RDF document (Turtle, or JSON-LD such as a flattened @graph) into compacted,
tree-shaped JSON-LD, so the provenance approaches in examples/ can be compared in the JSON-LD form
CDIF's RDF implementations use.

Usage:
    python tools/rdfToJsonLdTree.py SRC OUT [--base IRI]

    --base  base IRI for relative @ids (e.g. an RO-Crate's "./"); they are written back relative.

Layout:
- The root is the schema:Dataset when there is one. Anything pointing at it that is not otherwise
  reached (e.g. an RO-Crate metadata descriptor's schema:about) is nested under it with @reverse.
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
a = ap.parse_args()
text = open(a.src, encoding='utf-8').read()
is_ttl = a.src.endswith('.ttl')
g = rdflib.Graph().parse(data=text, format='turtle' if is_ttl else 'json-ld', publicID=a.base)

KNOWN = {'schema': 'http://schema.org/', 'prov': 'http://www.w3.org/ns/prov#', 'xsd': str(XSD),
         'rdf': str(RDF), 'rdfs': 'http://www.w3.org/2000/01/rdf-schema#', 'dcterms': 'http://purl.org/dc/terms/',
         'ex': 'https://example.org/cdif-prov/', 'bios': 'https://bioschemas.org/'}
if is_ttl:
    PFX = dict(re.findall(r'^@prefix\s+(\w*):\s*<([^>]+)>', text, re.M))
else:
    PFX = {}
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

done, bn_ids = set(), {}
def val(o, p):
    if isinstance(o, Literal):
        if o.language: return {'@value': str(o), '@language': o.language}
        if o.datatype in (None, XSD.string): return str(o)
        if coerce.get(p) == o.datatype: return str(o)
        return {'@value': str(o), '@type': qq(o.datatype)}
    if o in done:
        return {'@id': bn_ids[o] if isinstance(o, BNode) else qq(o)}
    if isinstance(o, BNode) or o in named: return node(o)
    return {'@id': qq(o)}
def node(s, skip=None):                 # skip: a (predicate, object) to leave out, stated by @reverse instead
    done.add(s); n = {}
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

# A schema:Dataset is the preferred root (CDIF records are rooted on the Dataset). Whatever points at
# it and is not otherwise reached (e.g. an RO-Crate metadata descriptor's schema:about) is nested
# under it with @reverse, so the record stays one tree.
DATASET = URIRef('http://schema.org/Dataset')
datasets = sorted((n for n in named if (n, RDF.type, DATASET) in g), key=lambda r: -reach(r))
trees = []
if datasets:
    main = datasets[0]; tree = node(main); rev = defaultdict(list)
    for s, p in sorted(g.subject_predicates(main), key=lambda sp: first_pos(sp[0])):
        if s not in done: rev[qq(p)].append(node(s, skip=(p, main)))
    if rev: tree['@reverse'] = {k: v[0] if len(v) == 1 else v for k, v in rev.items()}
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
ok = rdflib.compare.isomorphic(g, r) and rdflib.compare.isomorphic(g, p)
print(f'{a.out}: {len(trees)} root(s) | triples src {len(g)} rdflib {len(r)} pyld {len(p)} | isomorphic rdflib',
      rdflib.compare.isomorphic(g, r), 'pyld', rdflib.compare.isomorphic(g, p))
sys.exit(0 if ok else 1)
