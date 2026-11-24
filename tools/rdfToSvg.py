#!/usr/bin/env python3
"""Draw an RDF graph as an SVG node-link diagram, with Graphviz (`dot` on the PATH).

Every IRI or blank node that is a subject, or the object of a predicate other than rdf:type, is a
box. Its header is its compact IRI (none for a blank node) and its types; below that is one row per
property with a literal value ("predicate: value"). A value longer than --width characters is cut,
and the full value is the row's tooltip. Every other triple is an arrow labelled with its predicate.
A leaf that several nodes point to (a node with no literals and no links of its own, such as a role,
an action status or a Wikidata kind term) is drawn once per reference, with a dashed border, so it
does not pull arrows across the whole diagram.

Boxes take the PROV-O colours: entities yellow, activities blue, agents orange. The nodes of a
qualified relation (prov:Usage, prov:Generation, prov:Association, ...) are grey, and anything else
is white.

usage:
    python tools/rdfToSvg.py SRC OUT.svg [--base IRI] [--rankdir LR|RL|TB|BT] [--width N] [--dot OUT.dot]
SRC is Turtle (.ttl) or JSON-LD (any other extension).
"""
import argparse
import html
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
    if types & ACTIVITIES or any(n.endswith("/Action") and n.startswith(SCHEMA) for n in names):
        return ACTIVITY
    if PROV.Entity in types or PROV.Plan in types:
        return ENTITY
    return "#FFFFFF"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--base", help="base IRI for relative @ids (an RO-Crate: http://rocrate.invalid/crate/)")
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
    # rdflib binds schema: to https; CDIF uses http://schema.org/, which would show as schema1:
    if any(str(t).startswith(SCHEMA[0]) for tr in g for t in tr if isinstance(t, URIRef)):
        nm.bind("schema", SCHEMA[0], override=True, replace=True)

    def curie(t):
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
        out.append(f'  {ids[s]} -> {target} [label="{esc(curie(p))}"];')
    out.append("}")
    dot = "\n".join(out) + "\n"
    if args.dot:
        open(args.dot, "w", encoding="utf-8", newline="\n").write(dot)
    r = subprocess.run(["dot", "-Tsvg", "-o", args.out], input=dot.encode("utf-8"), capture_output=True)
    if r.returncode:
        sys.exit(r.stderr.decode("utf-8", "replace"))
    print(f"{args.out}: {len(ids)} nodes ({len(split)} shared leaves drawn per reference), "
          f"{len(links)} links, {len(g)} triples")


if __name__ == "__main__":
    main()
