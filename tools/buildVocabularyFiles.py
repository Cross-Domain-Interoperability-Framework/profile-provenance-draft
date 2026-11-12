#!/usr/bin/env python3
"""
Build the published files for a SKOS vocabulary from its JSON-LD source.

The JSON-LD file is the only file anyone edits. Two source layouts are accepted:
  - a nested tree (activityTypes.jsonld, the deprecated v0.1 vocabulary): the scheme
    is the root object and concepts hang from skos:hasTopConcept / skos:narrower, with
    CURIE @ids;
  - a flat @graph (CDIF_Activities.json, the CDIF provenance activity vocabulary): one
    node per concept or scheme, with full-IRI @ids, in more than one namespace
    (https://w3id.org/cdif/concepts/provenance/activity/ and
    https://w3id.org/cdif/concepts/GSBPM-5.2/activity/).

From it this writes:
  - <name>.ttl beside it: the whole scheme in Turtle. This is the input the
    iSamples vocabulary action (isamplesorg/vocabularies) renders to HTML, and
    what w3id serves for the scheme IRI on a text/turtle request.
  - one .jsonld and .ttl file per concept, holding that concept's own statements,
    with its broader/narrower concepts and its scheme as {"@id"} references. w3id
    serves these for a concept IRI, so each IRI dereferences to its own skos:Concept
    rather than to the whole scheme. Nested tree: <folder>/<scheme's last
    segment>/<localName>.*. Flat graph: <folder>/concepts/<IRI path after
    https://w3id.org/cdif/concepts/>.*, e.g.
    vocabularies/concepts/provenance/activity/Sampling.jsonld.

The concept's local name (the part of its IRI after the scheme namespace) must
equal its skos:notation; the build fails otherwise, because the w3id rules map
the IRI's last segment straight onto the file name.

`anchors` patches the HTML the iSamples action renders. That action gives each
concept an anchor made by LOWERCASING its local name (#samplepreparation), but
links "Child of" entries by the local name as written (#samplePreparation), so
for camelCase names those links go nowhere, and a w3id redirect to
page.html#<localName> would miss too. This adds an anchor with the local name as
written next to each lowercased one.

Usage:
    python tools/buildVocabularyFiles.py vocabularies/activityTypes.jsonld
    python tools/buildVocabularyFiles.py vocabularies/activityTypes.jsonld --check
    python tools/buildVocabularyFiles.py vocabularies/activityTypes.jsonld --anchors vocabularies/docs/activityTypes.html
    python tools/buildVocabularyFiles.py vocabularies/CDIF_Activities.json [--check]
"""

import argparse
import copy
import json
import os
import re
import sys

import rdflib

# The concept files sit in a folder named after the scheme IRI's last segment,
# matching the IRIs: https://w3id.org/cdif/provenance/activityType/<localName>.
# The extra prefix lets the iSamples action name the scheme as a CURIE.
EXTRA_PREFIXES = {"cdifprov": "https://w3id.org/cdif/provenance/",
                  "cdifact": "https://w3id.org/cdif/concepts/provenance/activity/",
                  "gsbpm": "https://w3id.org/cdif/concepts/GSBPM-5.2/activity/"}

# Flat-graph concept files mirror the IRI path below this root.
CONCEPTS_ROOT = "https://w3id.org/cdif/concepts/"


def dump_jsonld(x, ind=0):
    """JSON in the source files' style: flat objects and single-item lists inline."""
    def flat(v):
        return not isinstance(v, (dict, list))

    def inline_dict(d):
        return isinstance(d, dict) and all(flat(v) for v in d.values())

    p = '  ' * ind
    if isinstance(x, dict):
        if inline_dict(x):
            return json.dumps(x, ensure_ascii=False)
        items = [f'{p}  {json.dumps(k, ensure_ascii=False)}: {dump_jsonld(v, ind + 1)}' for k, v in x.items()]
        return '{\n' + ',\n'.join(items) + '\n' + p + '}'
    if isinstance(x, list):
        if len(x) <= 1 and all(flat(i) or inline_dict(i) for i in x):
            return '[' + ', '.join(dump_jsonld(i) for i in x) + ']'
        return '[\n' + ',\n'.join(p + '  ' + dump_jsonld(i, ind + 1) for i in x) + '\n' + p + ']'
    return json.dumps(x, ensure_ascii=False)


def to_turtle(doc):
    g = rdflib.Graph()
    g.parse(data=json.dumps(doc), format='json-ld')
    for prefix, ns in list(doc['@context'].items()) + list(EXTRA_PREFIXES.items()):
        if isinstance(ns, str) and ns.endswith(('/', '#')):
            g.bind(prefix, ns, override=True, replace=True)
    return g.serialize(format='turtle')


def concepts(nodes):
    for c in nodes:
        yield c
        yield from concepts(c.get('skos:narrower', []))


def graph_concepts(doc):
    """The concept nodes of a flat @graph source."""
    return [n for n in doc['@graph'] if n.get('@type') in ('skos:Concept', 'Concept')]


def build_flat(source, doc, concept_dir=None):
    """concept_dir, when given, holds every concept file flat (<concept_dir>/<localName>.*),
    for a vocabulary outside https://w3id.org/cdif/concepts/ such as the geochemistry
    activity types (https://w3id.org/geochem/vocabulary/<localName>)."""
    folder, name = os.path.split(source)
    ctx = doc['@context']
    out = {os.path.join(folder, os.path.splitext(name)[0] + '.ttl'): to_turtle(doc)}
    root = concept_dir or os.path.join(folder, 'concepts')
    for c in graph_concepts(doc):
        iri = c['@id']
        local = iri.rstrip('/').rsplit('/', 1)[1]
        notation = c.get('skos:notation') or c.get('notation')
        if local != notation or not (concept_dir or iri.startswith(CONCEPTS_ROOT)):
            sys.exit(f"{iri}: its local name must equal skos:notation ({notation!r}), "
                     f"and without --concept-dir it must lie under {CONCEPTS_ROOT}")
        base = (os.path.join(root, local) if concept_dir
                else os.path.join(root, *iri[len(CONCEPTS_ROOT):].split('/')))
        node = {'@context': ctx, **c}
        out[base + '.jsonld'] = dump_jsonld(node) + '\n'
        out[base + '.ttl'] = to_turtle(node)
    return out, root


def build(source, concept_dir=None):
    """Return {relative path: file text} for every generated file."""
    doc = json.load(open(source, encoding='utf-8'))
    if '@graph' in doc:
        return build_flat(source, doc, concept_dir)
    ctx = doc['@context']
    scheme = doc['@id']
    folder, name = os.path.split(source)
    concept_dir = scheme.rstrip('/').rsplit('/', 1)[1]
    ns_prefix = next(p for p, ns in ctx.items() if ns == scheme + '/')

    out = {os.path.join(folder, os.path.splitext(name)[0] + '.ttl'): to_turtle(doc)}
    for c in concepts(doc['skos:hasTopConcept']):
        local = c['@id'].split(':', 1)[1]
        if not c['@id'].startswith(ns_prefix + ':') or local != c['skos:notation']:
            sys.exit(f"{c['@id']}: local name must equal skos:notation ({c['skos:notation']!r})")
        node = copy.deepcopy(c)
        if 'skos:narrower' in node:
            node['skos:narrower'] = [{'@id': n['@id']} for n in node['skos:narrower']]
        node = {'@context': ctx, **node}
        base = os.path.join(folder, concept_dir, local)
        out[base + '.jsonld'] = dump_jsonld(node) + '\n'
        out[base + '.ttl'] = to_turtle(node)
    return out, os.path.join(folder, concept_dir)


def add_anchors(source, html_path):
    doc = json.load(open(source, encoding='utf-8'))
    html = open(html_path, encoding='utf-8').read()
    nodes = graph_concepts(doc) if '@graph' in doc else concepts(doc['skos:hasTopConcept'])
    for c in nodes:
        local = c.get('skos:notation') or c.get('notation')
        if local == local.lower() or f'id="{local}"' in html:
            continue
        html, n = re.subn(f'(<span id="{local.lower()}"></span>)', rf'\1<span id="{local}"></span>', html, count=1)
        if not n:
            sys.exit(f'{html_path}: no anchor #{local.lower()} for {c["@id"]}')
    open(html_path, 'w', encoding='utf-8', newline='\n').write(html)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('source', help='the vocabulary JSON-LD file')
    ap.add_argument('--check', action='store_true', help='fail if the generated files are not up to date')
    ap.add_argument('--anchors', metavar='HTML', help='add case-preserving concept anchors to the rendered HTML')
    ap.add_argument('--concept-dir', metavar='DIR',
                    help='flat @graph only: write every concept file to DIR/<localName>.* '
                         '(needed for a vocabulary outside https://w3id.org/cdif/concepts/)')
    a = ap.parse_args()

    if a.anchors:
        add_anchors(a.source, a.anchors)
        return 0

    files, concept_dir = build(a.source, a.concept_dir)
    existing = ({os.path.join(d, f) for d, _, fs in os.walk(concept_dir) for f in fs}
                if os.path.isdir(concept_dir) else set())
    stale = sorted(existing - set(files))
    changed = [p for p, text in files.items()
               if not os.path.exists(p) or open(p, encoding='utf-8').read() != text]
    if a.check:
        for p in changed:
            print(f'out of date: {p}')
        for p in stale:
            print(f'no longer generated: {p}')
        if changed or stale:
            print(f'Run: python tools/buildVocabularyFiles.py {a.source}')
            return 1
        print(f'{len(files)} generated files up to date')
        return 0

    for p in changed:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8', newline='\n').write(files[p])
    for p in stale:
        os.remove(p)
    print(f'{len(files)} files: {len(changed)} written, {len(stale)} removed')
    return 0


if __name__ == '__main__':
    sys.exit(main())
