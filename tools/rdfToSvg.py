#!/usr/bin/env python3
"""Draw an RDF graph as an SVG node-link diagram, with Graphviz (`dot` on the PATH).

Every IRI or blank node that is a subject, or the object of a predicate other than rdf:type, is a
box. Its header is its compact IRI (none for a blank node) and its types; below that is one row per
property with a literal value ("predicate: value"). A value longer than --width characters is cut,
and the full value is the row's tooltip. Every other triple is an arrow labelled with its predicate.
schema:additionalProperty is left out, with the nodes only it reaches (a parameter or setting and
what hangs off it), and so is each schema:PropertyValue in schema:object (where an RO-Crate lists a
step's parameter values, beside its real inputs): the diagram shows how the record's resources
link, not each parameter value.
A leaf that several nodes point to (a node with no literals and no links of its own, such as a role,
an action status or a Wikidata kind term) is drawn once per reference, with a dashed border, so it
does not pull arrows across the whole diagram.

With --rooted (or --root IRI) the diagram is laid out from a root: the --root node, else the
schema:Dataset that is not a catalog record (the node a CDIF record describes, and the root of its
JSON-LD tree), else the named node nothing links to that reaches the most others. An arrow that points
back toward the root (a ProvONE step's provone:wasPartOf its run, a catalog record's schema:about) is laid out
from the root's side, its arrowhead still at its object, so the root is the first box and each node
follows the one nearer the root that it is linked to. Without either option, arrows alone set the
layout (the longest chain of arrows runs left to right).

--omit PREDICATE (repeatable) leaves out that predicate's links, and every node reachable only
through them, with its own triples: --omit schema:additionalProperty drops each parameter
PropertyValue and its values, so the diagram shows the topology of the record's resources. A node
something else still links to stays. PREDICATE@TYPE leaves out only the links whose object has that
type: an RO-Crate lists parameter values as PropertyValues in schema:object, beside the real inputs,
so --omit schema:object@schema:PropertyValue drops just those.

Boxes take the PROV-O colours: entities yellow, activities blue (a prov:Activity, or any schema.org
Action type, such as an RO-Crate's CreateAction), agents orange. The nodes of a
qualified relation (prov:Usage, prov:Generation, prov:Association, ...) are grey, and anything else
is white.

usage:
    python tools/rdfToSvg.py SRC OUT.svg [--base IRI] [--prefix PFX=IRI ...] [--rooted | --root IRI]
                             [--omit PREDICATE[@TYPE] ...] [--rankdir LR|RL|TB|BT] [--width N]
                             [--dot OUT.dot]
SRC is Turtle (.ttl) or JSON-LD (any other extension). With --base, an IRI under the base is shown
relative to it (an RO-Crate's root as ./), as rdfToJsonLdTree.py writes it. --prefix binds a prefix
the source does not (an RO-Crate's remote context binds none of the record's own).
The SVG has no fixed size, so a browser fits it to the window; zoom in with Ctrl + mouse wheel.
"""
import argparse
import collections
import html
import re
import subprocess
import sys

import rdflib
from rdflib import RDF, BNode, Literal, URIRef
from rdflib.compare import to_canonical_graph

PROV = rdflib.Namespace("http://www.w3.org/ns/prov#")
SCHEMA = ("http://schema.org/", "https://schema.org/")
ENTITY, ACTIVITY, AGENT, INFLUENCE = "#FFFC87", "#9FB1FC", "#FED37F", "#E8E8E8"
AGENTS = {PROV.Agent, PROV.Person, PROV.Organization, PROV.SoftwareAgent}
ACTIVITIES = {PROV.Activity}
# (predicate, object type or None) left out of every diagram
OMIT = ([(URIRef(ns + "additionalProperty"), None) for ns in SCHEMA]
        + [(URIRef(ns + "object"), URIRef(ns + "PropertyValue")) for ns in SCHEMA])
INFLUENCES = {PROV[n] for n in ("Usage", "Generation", "Association", "Attribution", "Delegation",
                                "Derivation", "Invalidation", "Start", "End", "Communication",
                                "Influence", "Revision", "Quotation", "PrimarySource")}


def fill(types):
    names = {str(t) for t in types}
    if types & INFLUENCES:
        return INFLUENCE
    if types & AGENTS or any(n.endswith(("/Person", "/Organization")) and n.startswith(SCHEMA)
                             for n in names):
        return AGENT
    if types & ACTIVITIES or any(n.endswith("Action") and n.startswith(SCHEMA) for n in names):
        return ACTIVITY
    if PROV.Entity in types or PROV.Plan in types:
        return ENTITY
    return "#FFFFFF"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--base", help="base IRI for relative @ids (an RO-Crate: http://rocrate.invalid/crate/)")
    ap.add_argument("--prefix", action="append", default=[], metavar="PFX=IRI",
                    help="bind a prefix for compact IRIs (repeatable)")
    ap.add_argument("--omit", action="append", default=[], metavar="PREDICATE[@TYPE]",
                    help="leave out this predicate's links (only those to a TYPE node, with @TYPE), "
                         "and what is reachable only through them (repeatable)")
    ap.add_argument("--rooted", action="store_true",
                    help="lay the diagram out from its root (the schema:Dataset that is not a catalog record)")
    ap.add_argument("--root", help="IRI or CURIE of the node to lay the diagram out from (implies --rooted)")
    ap.add_argument("--rankdir", default="LR", choices=["LR", "RL", "TB", "BT"])
    ap.add_argument("--width", type=int, default=48, help="longest literal shown in full (characters)")
    ap.add_argument("--dot", help="also write the Graphviz source here")
    args = ap.parse_args()

    g = rdflib.Graph().parse(args.src, format="turtle" if args.src.endswith(".ttl") else "json-ld",
                             publicID=args.base)
    # parsers label blank nodes at random (JSON-LD differently on every run); canonical labels keep
    # the node order, and so the drawing, the same from run to run
    canon = rdflib.Graph()
    for t in to_canonical_graph(g):
        canon.add(t)
    for prefix, ns in g.namespaces():
        canon.bind(prefix, ns, override=True, replace=True)
    g = canon
    nm = g.namespace_manager
    for b in args.prefix:
        pfx, _, ns = b.partition("=")
        nm.bind(pfx, ns, override=True, replace=True)
    # rdflib binds schema: to https; CDIF uses http://schema.org/, which would show as schema1:
    if any(str(t).startswith(SCHEMA[0]) for tr in g for t in tr if isinstance(t, URIRef)):
        nm.bind("schema", SCHEMA[0], override=True, replace=True)
    # leave out the OMIT links and each node only they reach, and what only those reach
    drop = [(s, p, o) for p, typ in OMIT for s, o in g.subject_objects(p)
            if typ is None or (o, RDF.type, typ) in g]
    gone = [o for _, _, o in drop]
    for t in drop:
        g.remove(t)
    while gone:
        n = gone.pop()
        if isinstance(n, Literal) or any(p != RDF.type for p in g.predicates(None, n)):
            continue
        gone += [o for p, o in g.predicate_objects(n) if p != RDF.type]
        g.remove((n, None, None))

    # --omit: drop the predicate's triples, then each object nothing else links to, with its own
    # triples, recursively (a PropertyValue and its values; a shared vocabulary term stays)
    omitted = 0
    def iri(name):
        return URIRef(name) if name.startswith(("http:", "https:")) else URIRef(nm.expand_curie(name))
    for spec in args.omit:
        name, _, typ = spec.partition("@")
        pred = iri(name)
        drop = [(s, o) for s, o in g.subject_objects(pred)
                if not typ or (not isinstance(o, Literal) and (o, RDF.type, iri(typ)) in g)]
        todo = [o for _, o in drop if not isinstance(o, Literal)]
        omitted += len(drop)
        for s, o in drop:
            g.remove((s, pred, o))
        while todo:
            n = todo.pop()
            if any(p != RDF.type for _, p in g.subject_predicates(n)):
                continue  # still linked from elsewhere
            kids = [o for p, o in g.predicate_objects(n) if p != RDF.type and not isinstance(o, Literal)]
            omitted += len(list(g.triples((n, None, None))))
            g.remove((n, None, None))
            todo += kids

    def curie(t):
        if args.base and isinstance(t, URIRef) and str(t).startswith(args.base):
            return str(t)[len(args.base):] or "./"
        try:
            return nm.normalizeUri(t) if isinstance(t, URIRef) else str(t)
        except Exception:
            return str(t)

    def esc(s):
        return html.escape(s, quote=True).replace("\n", " ")

    nodes = {s for s in g.subjects() if not isinstance(s, Literal)}
    nodes |= {o for p, o in g.predicate_objects() if p != RDF.type and not isinstance(o, Literal)}
    ids = {n: f"n{i}" for i, n in enumerate(sorted(nodes, key=lambda n: (isinstance(n, BNode), str(n))))}

    links = [(s, p, o) for s, p, o in sorted(g, key=lambda t: (str(t[0]), str(t[1]), str(t[2])))
             if p != RDF.type and not isinstance(o, Literal)]
    has_out = {s for s, _, o in g if not isinstance(o, Literal) and _ != RDF.type} |               {s for s, _, o in g if isinstance(o, Literal)}
    refs = {}
    for _, _, o in links:
        refs[o] = refs.get(o, 0) + 1
    split = {n for n in nodes if n not in has_out and refs.get(n, 0) > 1}

    # distance of each node from the root, following links either way
    if args.root:
        root = URIRef(nm.expand_curie(args.root)) if ":" in args.root and not args.root.startswith(
            ("http:", "https:")) else URIRef(args.root)
        if root not in nodes:
            sys.exit(f"--root {args.root}: no such node in {args.src}")
    elif args.rooted:
        datasets = [n for n in g.subjects(RDF.type, URIRef(SCHEMA[0] + "Dataset"))
                    if not any(str(t).endswith("CatalogRecord") for t in g.objects(n, RDF.type))]
        root = min(datasets, key=str) if datasets else None
        if root is None:
            # no dataset (plain PROV-O): the named node nothing links to that reaches the most nodes
            out_links = collections.defaultdict(set)
            for s, _, o in links:
                out_links[s].add(o)
            targets = {o for _, _, o in links}

            def reach(n):
                seen, todo = {n}, [n]
                while todo:
                    for m in out_links[todo.pop()] - seen:
                        seen.add(m); todo.append(m)
                return len(seen)
            tops = [n for n in nodes if isinstance(n, URIRef) and n not in targets]
            root = min(tops, key=lambda n: (-reach(n), str(n))) if tops else None
    else:
        root = None
    dist = {}
    if root is not None:
        nbrs = collections.defaultdict(set)
        for s, _, o in links:
            nbrs[s].add(o); nbrs[o].add(s)
        dist[root] = 0
        queue = collections.deque([root])
        while queue:
            n = queue.popleft()
            for m in sorted(nbrs[n], key=str):
                if m not in dist:
                    dist[m] = dist[n] + 1
                    queue.append(m)

    out = [f'digraph G {{ rankdir={args.rankdir}; nodesep=0.3; ranksep=0.6;',
           '  node [shape=plain, fontname="Helvetica", fontsize=10];',
           '  edge [fontname="Helvetica", fontsize=9, color="#555555", fontcolor="#333333"];']
    def box(n, i, dashed=False):
        types = set(g.objects(n, RDF.type))
        rows = []
        if isinstance(n, URIRef):
            rows.append(f'<TR><TD ALIGN="CENTER"><B>{esc(curie(n))}</B></TD></TR>')
        if types:
            rows.append(f'<TR><TD ALIGN="CENTER"><I>{esc(", ".join(sorted(curie(t) for t in types)))}</I></TD></TR>')
        for p, o in sorted(((p, o) for p, o in g.predicate_objects(n) if isinstance(o, Literal)),
                           key=lambda po: (curie(po[0]), str(po[1]))):
            v = str(o)
            short = v if len(v) <= args.width else v[:args.width - 1] + "…"
            tip = f' TOOLTIP="{esc(v)}" HREF="#"' if short != v else ""
            rows.append(f'<TR><TD ALIGN="LEFT"{tip}>{esc(curie(p))}: {esc(short)}</TD></TR>')
        if not rows:
            rows.append('<TR><TD> </TD></TR>')
        style = ' STYLE="dashed"' if dashed else ""
        out.append(f'  {i} [label=<<TABLE BORDER="1"{style} CELLBORDER="0" CELLSPACING="0" CELLPADDING="3" '
                   f'BGCOLOR="{fill(types)}">{"".join(rows)}</TABLE>>];')

    for n, i in ids.items():
        if n not in split:
            box(n, i)
    for k, (s, p, o) in enumerate(links):
        target = ids[o]
        if o in split:
            target = f"{ids[o]}_{k}"
            box(o, target, dashed=True)
        if o not in split and dist.get(o, -1) >= 0 and dist[o] < dist.get(s, dist[o]):
            # o is nearer the root: lay the arrow out from o, drawn pointing at o as before
            out.append(f'  {target} -> {ids[s]} [label="{esc(curie(p))}", dir=back];')
        else:
            out.append(f'  {ids[s]} -> {target} [label="{esc(curie(p))}"];')
    out.append("}")
    dot = "\n".join(out) + "\n"
    if args.dot:
        open(args.dot, "w", encoding="utf-8", newline="\n").write(dot)
    r = subprocess.run(["dot", "-Tsvg"], input=dot.encode("utf-8"), capture_output=True)
    if r.returncode:
        sys.exit(r.stderr.decode("utf-8", "replace"))
    # drop dot's fixed width and height (thousands of points for a large graph): with only the
    # viewBox, a browser fits the whole diagram to the window instead of opening on an empty corner
    svg = re.sub(rb'<svg width="[^"]*" height="[^"]*"', b"<svg", r.stdout, count=1)
    open(args.out, "wb").write(svg)
    if args.omit:
        print(f"{args.out}: omitted {omitted} triples ({', '.join(args.omit)})")
    print(f"{args.out}: root {curie(root) if root is not None else 'none'}, "
          f"{len(ids)} nodes ({len(split)} shared leaves drawn per reference), "
          f"{len(links)} links, {len(g)} triples")


if __name__ == "__main__":
    main()
