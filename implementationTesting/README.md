# implementationTesting: how the files are made

Each scenario is one provenance record, written several ways so the approaches can be compared. This
page says which files are written by hand and how every other file is generated from them. What
the scenarios are and what the comparison found are in [APPROACHES.md](APPROACHES.md) and the
`SCENARIO_*.md` pages; [MAPPING.md](MAPPING.md) maps each cdifProv construct to PROV-O and RO-Crate.

**Never edit a generated file.** Fix its source (a hand-written file, or a tool in [`../tools/`](../tools/))
and regenerate. All commands below run from the repository root.

## The scenarios

| scenario | page | cdifProv record (hand-written) | PROV-O name | RO-Crate |
|-|-|-|-|-|
| laboratory measurement | [SCENARIO\_lab\_measurement.md](SCENARIO_lab_measurement.md), [APPROACHES.md](APPROACHES.md) | `cdif_provenance_quantitative.json` | `cdif_provenance_quantitative.from-cdifprov` (the plain name is the hand-written master) | `cdif_provenance_quantitative/` |
| computational workflow | [SCENARIO\_workflow.md](SCENARIO_workflow.md) | `cdif_provenance_workflow.json` | `cdif_provenance_workflow` | `cdif_provenance_workflow/` |
| minimal record | [SCENARIO\_minimal.md](SCENARIO_minimal.md) | `cdif_provenance_minimal.json` | `cdif_provenance_minimal` | `cdif_provenance_minimal/` |
| laboratory protocol | [SCENARIO\_lab\_protocol.md](SCENARIO_lab_protocol.md) | `cdif_provenance_lab_protocol.json` | `cdif_provenance_lab_protocol` | `cdif_provenance_lab_protocol/` |
| field sample to data product | [SCENARIO\_field\_sample.md](SCENARIO_field_sample.md) | `cdif_provenance_field_sample.json` | `cdif_provenance_field_sample` | `cdif_provenance_field_sample/` |
| qualitative assessment | [SCENARIO\_qualitative.md](SCENARIO_qualitative.md) | `cdif_provenance_qualitative.json` | `cdif_provenance_qualitative` | `cdif_provenance_qualitative/` |

The laboratory measurement is also written in DDI-CDI, P-Plan, ProvONE, SOSA/SSN and PROV-JSON.

## What is hand-written and what is generated

| folder | hand-written | generated |
|-|-|-|
| `cdifprov-schemaorg/` | every `cdif_provenance_<name>.json` (the cdifProv records, the source of nearly everything else); `…quantitative.before-schemaorg-validator.json` is a superseded snapshot | `…quantitative.run-rooted.jsonld`; the diagrams |
| `prov-o-qualified/` | `cdif_provenance_quantitative.ttl`, the master of the laboratory measurement (the Dagstuhl Turtle plus additions marked `# + illustrative`) | every other `.ttl`, from cdifProv; every `.jsonld` tree; the diagrams |
| `prov-o-unqualified/` | none | every `.ttl` (from cdifProv, or from the qualified master), every `.jsonld` tree, the diagrams |
| `ro-crate/` | each `<name>/ro-crate-metadata.json`, written from its cdifProv record; `cdif_provenance_quantitative.cdif-parts.json`, a CDIF rendering of the earlier Process Run Crate | each `<name>.jsonld` tree, the run-rooted tree, the diagrams |
| `ddi-cdi/`, `provone/` | the `.ttl` | the `.jsonld` tree and the run-rooted tree |
| `p-plan/`, `sosa/` | the `.ttl` (overlays on the master) | the `.jsonld` tree |
| `prov-json/` | see below | `cdif_provenance_quantitative.json` |

## PROV-O from cdifProv

[`tools/cdifProvToProvO.py`](../tools/cdifProvToProvO.py) writes the qualified PROV-O and, with
`--unqualified`, the plain relations (each qualified relation replaced by its plain form; plans
and roles are lost). The mapping is [MAPPING.md](MAPPING.md).

```bash
python tools/cdifProvToProvO.py implementationTesting/cdifprov-schemaorg/cdif_provenance_workflow.json implementationTesting/prov-o-qualified/cdif_provenance_workflow.ttl
python tools/cdifProvToProvO.py implementationTesting/cdifprov-schemaorg/cdif_provenance_workflow.json implementationTesting/prov-o-unqualified/cdif_provenance_workflow.ttl --unqualified
```

The same for each scenario; the laboratory measurement writes `cdif_provenance_quantitative.from-cdifprov.ttl`.
The plain master comes from the qualified master:

```bash
python tools/cdifProvToProvO.py --unqualify implementationTesting/prov-o-qualified/cdif_provenance_quantitative.ttl implementationTesting/prov-o-unqualified/cdif_provenance_quantitative.ttl
```

The converter's Turtle orders blank nodes differently from run to run. The graph is the same, but
a regenerated `.ttl`, and the trees made from it, show a large textual diff. Compare graphs, not text.

## JSON-LD trees

[`tools/rdfToJsonLdTree.py`](../tools/rdfToJsonLdTree.py) turns any RDF (Turtle, or flattened
JSON-LD such as a crate) into one compacted, nested JSON-LD tree, and exits 1 unless rdflib and
pyld both read the output back as a graph isomorphic to the source. It roots the tree on the
`schema:Dataset` that is not a catalog record, or on `--root`.

```bash
# qualified PROV-O, from its Turtle
python tools/rdfToJsonLdTree.py implementationTesting/prov-o-qualified/cdif_provenance_workflow.ttl implementationTesting/prov-o-qualified/cdif_provenance_workflow.jsonld
# plain PROV-O, in the key order of its qualified counterpart, so the pair reads side by side
python tools/rdfToJsonLdTree.py implementationTesting/prov-o-unqualified/cdif_provenance_workflow.ttl implementationTesting/prov-o-unqualified/cdif_provenance_workflow.jsonld --order-like implementationTesting/prov-o-qualified/cdif_provenance_workflow.jsonld
# RO-Crate, with the crate's relative @ids, in the key order of its cdifProv record
python tools/rdfToJsonLdTree.py implementationTesting/ro-crate/cdif_provenance_workflow/ro-crate-metadata.json implementationTesting/ro-crate/cdif_provenance_workflow.jsonld --base http://rocrate.invalid/crate/ --order-like implementationTesting/cdifprov-schemaorg/cdif_provenance_workflow.json
```

- **The masters** (`prov-o-*/cdif_provenance_quantitative.jsonld`) have no `schema:Dataset` and take
  `--root ex:validationResult`; the plain one also `--order-like` the qualified one.
- **Run-rooted trees** take `--root ex:concentrationRun`: the two masters (`….run-rooted.jsonld`,
  plain `--order-like` qualified), `cdifprov-schemaorg/`, `ddi-cdi/`, `provone/`, and the crate
  (`--base` as above, `--order-like cdifprov-schemaorg/cdif_provenance_quantitative.run-rooted.jsonld`).
- **DDI-CDI, ProvONE, P-Plan, SOSA/SSN** trees take no options.

## Diagrams

[`tools/rdfToSvg.py`](../tools/rdfToSvg.py) draws a graph with Graphviz (`dot` on the PATH): a box
per resource with its literal properties, an arrow per link. Each record has up to two diagrams,
beside its source and with the same name:

| file | options | what it shows |
|-|-|-|
| `<name>.svg` | none | the whole graph; the longest chain of arrows runs left to right |
| `<name>.rooted.svg` | `--rooted` | the whole graph, laid out from the record's root (the dataset first), as its tree is |

```bash
python tools/rdfToSvg.py implementationTesting/prov-o-qualified/cdif_provenance_workflow.ttl implementationTesting/prov-o-qualified/cdif_provenance_workflow.svg
python tools/rdfToSvg.py implementationTesting/prov-o-qualified/cdif_provenance_workflow.ttl implementationTesting/prov-o-qualified/cdif_provenance_workflow.rooted.svg --rooted
```

- **Which records:** every cdifProv record (from its `.json`) and every PROV-O `.ttl` has both.
  The cdifProv run-rooted tree is the same graph as its record, and the superseded snapshot is not
  drawn.
- **The masters** take `--root ex:validationResult` in place of `--rooted`.
- **RO-Crates** have both, drawn from `ro-crate-metadata.json` with
  `--base http://rocrate.invalid/crate/ --prefix ex=https://example.org/cdif-prov/`. The run-rooted
  crate tree is the same graph as the quantitative crate, so it has only
  `cdif_provenance_quantitative.run-rooted.rooted.svg`, with `--root ex:concentrationRun` in place
  of `--rooted`.
- **Parameters:** every diagram leaves out `schema:additionalProperty` and the PropertyValues in a
  crate step's `object`, with the values only they reach; `--omit PREDICATE[@TYPE]` leaves out more.
  `--parameters` keeps them.

## PROV-JSON

`prov-json/cdif_provenance_quantitative.json` was generated from the master with the `prov` Python
package (3.3.0) and then fixed by hand, because `prov`'s RDF reader drops agents (see the PROV-JSON
findings in [APPROACHES.md](APPROACHES.md)). Changes to the master since then have been made in it
by hand: keep it in step with the master.

## Checks

There is no test suite. After a change:

- **cdifProv records:** `python FrameAndValidate.py implementationTesting/cdifprov-schemaorg/<name>.json -v`
  passes, and `pyshacl -s provenanceRules.shacl -df json-ld -f human <file>` shows no new results.
- **Generated PROV-O:** regenerating from cdifProv gives a graph isomorphic to the committed one
  (`rdflib.compare.isomorphic`), unless the converter or the record changed on purpose.
- **Trees:** `rdfToJsonLdTree.py` prints `isomorphic rdflib True pyld True`, or exits 1.
- **Diagrams:** `rdfToSvg.py` output depends only on the graph and the options, so an unchanged
  graph redraws byte for byte.
- **The scenario pages:** their triple and entity counts still hold, and their links resolve.
