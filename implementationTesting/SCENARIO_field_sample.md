# Scenario: from a field sample to a data product

A dataset whose provenance runs back to a sample taken in the field. It is recorded as a chain of
three activities in `prov:wasGeneratedBy`, each taking the previous one's product as its input:
the fourth way of recording a procedure, after one activity with a plan by reference (the minimal
scenario), an inline HowTo of actions (the workflow), and actions with sub-procedures (the lab
protocol). It is written first in cdifProv and mapped from there; [MAPPING.md](MAPPING.md) has the
construct-by-construct table.

## The story

1. **Drilling.** In 1981 the U.S. Geological Survey drilled core KI81-1 through the crust of the
   Kilauea Iki lava lake, which ponded in Kilauea Iki crater in the 1959 eruption.
2. **Sample preparation.** On 1–3 June 2024, Wei Chen picked olivine grains from the crushed core,
   mounted them in epoxy, ground and polished the mount, and carbon-coated it.
3. **EPMA analysis.** On 10 June 2024, Wei Chen analysed the mount on a JEOL JXA-8530F Plus
   microprobe, following a registered method, and made 142 point analyses. The analyses are the
   dataset the record describes.

The record:

- **The chain:** the three activities are chained by `@id`:
  - the lava lake (a `schema:Place`) is the drilling's `schema:object`;
  - the core is the drilling's `schema:result` and the preparation's `schema:object`;
  - the polished mount is the preparation's `schema:result` and the analysis's `schema:object`.
- **The output:** the dataset (the root) is the analysis's output. As in the minimal scenario, it
  needs no `schema:result`.
- **Places:** the drilling and the analysis each have a `schema:location`. The drilling's has
  coordinates (`schema:geo`).
- **Agents:** an organization did the drilling, and a person did the laboratory work.
- **Procedures:** both laboratory activities have an inline HowTo of text-only steps. The
  analysis's HowTo names the registered method it followed in `schema:isBasedOn`.
- **Kinds:** the vacuum evaporator and the microprobe are instruments. Probe for EPMA, the
  quantification program, is software.

## Where it comes from, and what is illustrative

It is based on [`../examples/exampleEPMAProvenance.json`](../examples/exampleEPMAProvenance.json).
These are that file's: the dataset, its DOI, the analyst, both laboratory activities with their
times, steps, descriptions and parameter values, the microprobe and the laboratory. That file has
four problems, changed here:

- **The analysis listed an activity as its input.** Its `schema:object` included the
  preparation activity itself as well as the mount. Only the mount is kept.
- **The method was the procedure.** The analysis's HowTo had the method's registry IRI as its
  `@id`. Here the HowTo is the procedure as performed, with the method in `schema:isBasedOn`, as in
  the other scenarios. The method's documentation URL (`schema:url`) has nowhere to go, because a
  plan is a reference only, so it is dropped.
- **The analyst's ORCID** is a `schema:PropertyValue`, not a bare string. They are given once, by
  `@id`, and referenced from the second activity.
- **The activity types** are CDIF activity-vocabulary terms (`cdifact:Measurement`), in place of
  `schema:CreateAction`.

**Added from the step text:** the vacuum evaporator and Probe for EPMA, as instruments.

**Invented:** the drilling activity. Everything about it comes only from the core's name (KI81-1,
from Kilauea Iki in 1981):

- the U.S. Geological Survey as its agent;
- its place, with coordinates near the lava lake's centre;
- `cdifact:Sampling` as its type.

It has no start or end time; the description gives the year.

## Files

| approach | file | how it was made | checked with |
|---|---|---|---|
| **cdifProv** (master) | [cdifprov-schemaorg/cdif\_provenance\_field\_sample.json](cdifprov-schemaorg/cdif_provenance_field_sample.json) | hand-written | `FrameAndValidate.py -v` against cdifProvenance 2.0: passes; conformance consistent (core 2.0, provenance 2.0); 179 triples, all kept by framing; `provenanceRules.shacl` (advanced): conforms, no results; key counts = triple counts |
| **PROV-O, qualified** | [prov-o-qualified/cdif\_provenance\_field\_sample.ttl](prov-o-qualified/cdif_provenance_field_sample.ttl), [.jsonld](prov-o-qualified/cdif_provenance_field_sample.jsonld) | generated: `python tools/cdifProvToProvO.py <cdifProv> <out.ttl>` | 176 triples: 3 activities, 3 generations (the core by the drilling, the mount by the preparation, the dataset by the analysis), 6 usages, 3 associations (one with the method as its plan), 2 `prov:atLocation`; the tree is isomorphic under rdflib and pyld |
| **PROV-O, plain** | [prov-o-unqualified/cdif\_provenance\_field\_sample.ttl](prov-o-unqualified/cdif_provenance_field_sample.ttl), [.jsonld](prov-o-unqualified/cdif_provenance_field_sample.jsonld) | generated: the same with `--unqualified` | 142 triples; the plan and roles are lost; the tree is isomorphic |
| **RO-Crate 1.1** | [ro-crate/cdif\_provenance\_field\_sample/ro-crate-metadata.json](ro-crate/cdif_provenance_field_sample/ro-crate-metadata.json), [tree](ro-crate/cdif_provenance_field_sample.jsonld) | written from the cdifProv file | 37 entities; 172 triples; the tree is isomorphic. `rocrate-validator` 0.14.0, `-p ro-crate-1.1 -m` (metadata only): every REQUIRED check passes; 5 RECOMMENDED checks fail, listed below |

The crate is plain RO-Crate 1.1, as in the lab-protocol scenario: two of the three activities are
physical processes, and Process Run Crate requires every action's instrument to be software.

- **Nodes:** every node the cdifProv file holds in place is a separate entity, as RO-Crate
  requires: the places, the coordinates, the steps and the parameter values. A node with no `@id`
  gets one made from its parent's.
- **The plan:** the method is a `HowTo` entity with no properties.
- **The output:** the dataset is the analysis's `result`.

The 5 RECOMMENDED failures, none filled in with invented values:

- **The crate's `author` and `publisher`:** the cdifProv record names neither.
- **A `url` for JEOL**, the microprobe's manufacturer: the source gives only its name.
- **A trailing `/` on the dataset's IRI:** RO-Crate recommends it for a `Dataset`. The IRI is kept.
- **The `example.org` dataset:** it is flagged as unavailable.

## Findings

- **Derivation is implicit.** That the dataset comes from core KI81-1, and the core from the lava
  lake, follows only from the chain of inputs and outputs. cdifProvenance has no
  `prov:wasDerivedFrom`, and PROV-O does not infer a derivation from a usage and a generation, so
  none of the three forms says it directly. A record that wants to say "derived from this sample"
  in one statement cannot.
- **In a chain, only the last activity generates the record's dataset.** Until this scenario,
  `tools/cdifProvToProvO.py` gave the root a generation by every activity in
  `prov:wasGeneratedBy`. That is wrong for a chain, since PROV allows an entity one generation. The
  root is now generated only by an activity whose results no other listed activity takes as input.
- **Places map to PROV-O.** `schema:location` becomes `prov:atLocation`, and the place a
  `prov:Location` that keeps its name and coordinates. The tool used to copy it as an annotation.
- **Dates without times become midnight.** PROV-O times are `xsd:dateTime`, so the preparation's
  dates (`2024-06-01` to `2024-06-03`) become midnight. Its end therefore comes out as the start of
  its last day.
- **A sampled feature is just an input.** The lava lake is the drilling's `schema:object`, so in
  PROV-O it is used with the role `ex:InputData`. Nothing says the core is a sample of it.
