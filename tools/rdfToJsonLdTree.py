#!/usr/bin/env python3
"""
RDF to tree-shaped JSON-LD

Converts any RDF document (Turtle, or JSON-LD such as a flattened @graph) into compacted,
tree-shaped JSON-LD, so the provenance approaches in examples/ can be compared in the JSON-LD form
CDIF's RDF implementations use.

Usage:
    python tools/rdfToJsonLdTree.py SRC OUT [--base IRI] [--root IRI] [--order-like REF.jsonld]

    --base  base IRI for relative @ids (e.g. an RO-Crate's "./"); they are written back relative.
    --root  IRI or CURIE of the node to root the tree on, overriding the Dataset rule.
    --order-like  a tree of the same record (e.g. its qualified PROV-O form) whose key and value order
            to follow, so the two read side by side. A qualified relation in REF stands for its plain
            form (prov:qualifiedUsage's prov:entity for prov:used; a prov:qualifiedGeneration's prov:atTime
            for prov:generatedAtTime). Keys and values REF does not have keep their place after the one
            before them. A node REF leaves blank (an RO-Crate names its Places) is matched by its
            literals.

Layout:
- The root is the --root node, else the schema:Dataset when there is one (not a catalog record, which
  is a schema:Dataset too and nests under the dataset's schema:subjectOf). A node not reached from it
  that points into the tree (an RO-Crate metadata descriptor's schema:about, a DDI-CDI agent's
  ProcessingAgent_performs_Activity) is nested with @reverse under the node nearest the root that it
  points at, and
  anything still unconnected goes in the root's @included, so the root is the one top-level object.
  Otherwise roots are the named nodes nothing else points at, largest tree first, in @graph when
  there are several.
- A node is described in full where it is first reached and is an {"@id"} reference after that.
  Blank nodes are nested; one gets an @id only if it is referenced more than once.
- @type is always an array, and so is every property the cdifProvenance schema types as an array
  (schema:additionalType, schema:instrument, schema:step, dcterms:conformsTo, ...; ARRAY_PROPS), even
  with one value, as CDIF records write them. Any other property with one value is written bare.
- Prefixes come from the source (Turtle @prefix lines, plus common namespaces under their usual
  prefixes). Properties appear in the order they first occur in the source.
- Literals keep their exact datatype. An xsd:integer, xsd:double or xsd:boolean is written as a
  JSON number or boolean, which JSON-LD reads back as that datatype (a JSON Schema checking
  `type: integer` or `number` rejects {"@value", "@type"}); an integer is native only when its
  lexical form is canonical, so it reads back exactly. Any other datatype used uniformly by one
  property is coerced in @context, otherwise the value is written {"@value", "@type"}.

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
ap.add_argument('--order-like', help='a JSON-LD tree of the same record whose key and value order to follow')
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
def native(o):                          # the JSON number / boolean for a literal, or None
    t, lex = o.datatype, str(o)
    if t == XSD.integer and re.fullmatch(r'-?(0|[1-9][0-9]*)', lex): return int(lex)
    if t == XSD.double:
        try: return float(lex)
        except ValueError: return None
    if t == XSD.boolean and lex in ('true', 'false'): return lex == 'true'
    return None
native_ok = {p for p in lit_types if all(native(o) is not None for o in g.objects(None, p) if isinstance(o, Literal))}
coerce = {p: next(iter(ts))[1] for p, ts in lit_types.items()
          if len(ts) == 1 and next(iter(ts))[0] == 'dt' and next(iter(ts))[1] not in (None, XSD.string)
          and p not in native_ok}

# Properties the cdifProvenance schema types as arrays (cdifProvenanceStructuredSchema.json): written as
# an array even with one value, as CDIF records write them. JSON-LD compaction would make a single value
# a bare object. Properties that accept either form (schema:object, schema:result, ...) keep the bare one.
_S, _P, _D = 'http://schema.org/', 'http://www.w3.org/ns/prov#', 'http://purl.org/dc/terms/'
ARRAY_PROPS = {URIRef(u) for u in (
    _S + 'additionalType', _S + 'additionalProperty', _S + 'category', _S + 'hasPart', _S + 'instrument',
    _S + 'relatedLink', _S + 'sameAs', _S + 'step', _P + 'wasGeneratedBy', _P + 'used', _D + 'conformsTo',
    'http://www.w3.org/2004/02/skos/core#broader', 'http://www.w3.org/2004/02/skos/core#narrower')}

# --order-like: follow a reference tree's order. A qualified relation there stands for its plain form.
QUAL = {'prov:qualified' + k: 'prov:' + v for k, v in (
    ('Generation', 'wasGeneratedBy'), ('Usage', 'used'), ('Association', 'wasAssociatedWith'),
    ('Attribution', 'wasAttributedTo'), ('Derivation', 'wasDerivedFrom'), ('Invalidation', 'wasInvalidatedBy'),
    ('Communication', 'wasInformedBy'), ('Start', 'wasStartedBy'), ('End', 'wasEndedBy'),
    ('Delegation', 'actedOnBehalfOf'), ('Influence', 'wasInfluencedBy'), ('Revision', 'wasRevisionOf'),
    ('Quotation', 'wasQuotedFrom'), ('PrimarySource', 'hadPrimarySource'))}
QUAL_TIME = {'prov:qualifiedGeneration': 'prov:generatedAtTime', 'prov:qualifiedInvalidation': 'prov:invalidatedAtTime'}
def as_list(v): return v if isinstance(v, list) else [v]
REF, REF_BY_ID = None, {}               # REF_BY_ID: @id -> the reference dict that describes it in full
if a.order_like:
    REF = json.load(open(a.order_like, encoding='utf-8'))
    def index(x):
        if isinstance(x, dict):
            if '@id' in x and len(x) > len(REF_BY_ID.get(x['@id'], {})): REF_BY_ID[x['@id']] = x
            for k, v in x.items():
                if k != '@context': index(v)
        elif isinstance(x, list):
            for v in x: index(v)
    index(REF)
def ref_layout(ref):                    # the reference's keys in order, and its values for each key
    keys, kids = [], {}
    for k, v in ref.items():
        if k.startswith('@'): continue
        if k in QUAL:
            infl = [x.get('prov:activity') or x.get('prov:entity') or x.get('prov:agent')
                    for x in as_list(v) if isinstance(x, dict)]
            ks = [(QUAL[k], [x for x in infl if x])]
            if k in QUAL_TIME:
                ks.append((QUAL_TIME[k], [x['prov:atTime'] for x in as_list(v) if isinstance(x, dict) and 'prov:atTime' in x]))
        else:
            ks = [(k, as_list(v))]
        for k2, vs in ks:
            if k2 not in kids: keys.append(k2); kids[k2] = vs
    return keys, kids
def follow(items, key_of, order):
    """Stable reorder: an item whose key is in order goes by its index; any other stays after the item before it."""
    out, last = [], -1
    for i, it in enumerate(items):
        k = key_of(it)
        if k is not None and k in order: last = order.index(k); out.append(((last, 0, i), it))
        else: out.append(((last, 1, i), it))
    return [it for _, it in sorted(out, key=lambda x: x[0])]
def scalar(v): return str(v['@value']) if isinstance(v, dict) and '@value' in v else (None if isinstance(v, dict) else str(v).lower() if isinstance(v, bool) else str(v))
def match(objs, kids):                  # each object's place among the reference values, and its reference dict
    pos, used = {}, set()
    for o in objs:
        hit = []
        if isinstance(o, URIRef):
            hit = [i for i, k in enumerate(kids) if isinstance(k, dict) and k.get('@id') == q(o)]
        elif isinstance(o, Literal):
            hit = [i for i, k in enumerate(kids) if scalar(k) == str(o)]
        if not hit and not isinstance(o, Literal):
            # a blank node, or a node the reference leaves blank (an RO-Crate names its Places and
            # PropertyValues): the unnamed reference value sharing most of its literals
            lits = {(q(p), str(v)) for p, v in g.predicate_objects(o) if isinstance(v, Literal)}
            score = [(sum((kp, scalar(kv)) in lits for kp, vs in k.items() if not kp.startswith('@') for kv in as_list(vs)), i)
                     for i, k in enumerate(kids) if isinstance(k, dict) and '@id' not in k and i not in used]
            best = max(score, default=(0, None))
            hit = [best[1]] if best[0] > 0 else []
        hit = [i for i in hit if i not in used]
        if hit: pos[o] = hit[0]; used.add(hit[0])
    return follow(objs, pos.get, list(range(len(kids)))), {o: kids[i] for o, i in pos.items() if isinstance(kids[i], dict)}

done, bn_ids, desc = set(), {}, {}      # desc: node -> the dict that describes it in full
reserved = set()                        # nodes to be placed under the root with @reverse; a reference until then
def val(o, p, ref=None):
    if isinstance(o, Literal):
        if o.language: return {'@value': str(o), '@language': o.language}
        if o.datatype in (None, XSD.string): return str(o)
        if native(o) is not None: return native(o)
        if coerce.get(p) == o.datatype: return str(o)
        return {'@value': str(o), '@type': qq(o.datatype)}
    if o in done or o in reserved:
        return {'@id': bn_ids[o] if isinstance(o, BNode) else qq(o)}
    if isinstance(o, BNode) or o in named: return node(o, ref=ref)
    return {'@id': qq(o)}
def node(s, skip=None, ref=None):       # skip: a (predicate, object) to leave out, stated by @reverse instead
    done.add(s); n = {}; desc[s] = n    # ref: the --order-like dict describing s
    if isinstance(s, URIRef): n['@id'] = qq(s); ref = REF_BY_ID.get(q(s), ref)
    elif incoming[s] > 1: bn_ids[s] = f'_:b{len(bn_ids)}'; n['@id'] = bn_ids[s]
    ts = sorted(g.objects(s, RDF.type), key=first_pos)
    keys, kids = ref_layout(ref) if ref else ([], {})
    if ref: ts = follow(ts, q, as_list(ref.get('@type', [])))
    if ts: n['@type'] = [qq(t) for t in ts]         # CDIF: @type is always an array
    preds = sorted({p for p in g.predicates(s) if p != RDF.type}, key=lambda p: (first_pos(p), q(p)))
    for p in follow(preds, q, keys):
        objs = sorted(g.objects(s, p), key=lambda o: (first_pos(o) if not isinstance(o, (Literal, BNode)) else 0))
        objs = [o for o in objs if (p, o) != skip]
        if not objs: continue
        refs = {}
        if q(p) in kids: objs, refs = match(objs, kids[q(p)])
        vs = [val(o, p, refs.get(o)) for o in objs]
        n[qq(p)] = vs if len(vs) > 1 or p in ARRAY_PROPS else vs[0]
    return n

# The root is the node named by --root, else a schema:Dataset that is not a catalog record (CDIF records
# are rooted on the described Dataset).
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
    # A CDIF record's catalog record is also a schema:Dataset (additionalType dcat:CatalogRecord, with
    # schema:about the described dataset), and it reaches everything through schema:about, so it can tie
    # with or outrank the dataset. It is never the root: it nests under the dataset's schema:subjectOf.
    RECORD = URIRef('http://www.w3.org/ns/dcat#CatalogRecord')
    def is_record(n):
        return (n, RDF.type, RECORD) in g or (n, URIRef('http://schema.org/additionalType'), RECORD) in g
    datasets = sorted((n for n in named if (n, RDF.type, DATASET) in g and not is_record(n)),
                      key=lambda r: -reach(r))
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
if REF and isinstance(REF.get('@context'), dict):
    ctx = {k: ctx[k] for k in follow(list(ctx), lambda k: k, list(REF['@context']))}
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
