# Scenario: minimal

The smallest record the cdifProvenance profile accepts that still says what was done, by whom, with
what, from what, and to what plan. It is written first in cdifProv and mapped from there;
[MAPPING.md](MAPPING.md) has the construct-by-construct table, and
[SCENARIO_workflow.md](SCENARIO_workflow.md) is the fuller computational-workflow scenario.

## The story

Between 10 January and 20 March 2025, Maria Garcia processed the raw shot gathers of seismic
line 07 with Seismic Unix 44R27, following the group's standard reflection-processing flow
(deconvolution, stacking and migration). The record describes the processed dataset that came out.

It has one activity and no steps:

- **The agent** is one person.
- **The software** is one `schema:instrument`.
- **The input** is one file in `schema:object`.
- **The plan** is only an `{@id}` in `schema:actionProcess`. The flow is named but not described.
- **The output** is the record's own dataset, the root, which names the activity in
  `prov:wasGeneratedBy`. There is no `schema:result`, because nothing else came out.

## Where it comes from, and what is illustrative

It is based on [`../examples/exampleCdifProvenance.json`](../examples/exampleCdifProvenance.json).
The person, the software and its version, the dates, the DOI, the license and the description of
the processing are that example's. That file is smaller still: it has no input, no plan and no
`@id` on its activity. The scenario adds those, so that each part of an activity is shown once.
It also tidies four things:

- **Software type:** the software is typed `schema:SoftwareApplication` only, not
  `[schema:Product, schema:Thing, schema:SoftwareApplication]`.
- **ORCID:** the person's ORCID is a `schema:PropertyValue` with `propertyID` and `url`, not a bare
  string.
- **actionStatus:** it is the full IRI `http://schema.org/CompletedActionStatus`, which both
  cdifProvenance and the schema.org validator accept.
- **Conformance:** the record declares core 2.0 as well as provenance 2.0, which is what
  FrameAndValidate detects.

**Invented:**
- the line name (line 07);
- the input file `line07_raw.segy` and its description;
- the plan's IRI (`ex:reflectionProcessingFlow`);
- the activity type `cdifact:DataTransformation`.

## Files

| approach | file | how it was made | checked with |
|---|---|---|---|
| **cdifProv** (master) | [cdifprov-schemaorg/cdif\_provenance\_minimal.json](cdifprov-schemaorg/cdif_provenance_minimal.json) | hand-written | `FrameAndValidate.py -v` against cdifProvenance 2.0: passes; conformance consistent (core 2.0, provenance 2.0); 48 triples, all kept by framing; `provenanceRules.shacl` (advanced): conforms, no results; key counts = triple counts |
| **PROV-O, qualified** | [prov-o-qualified/cdif\_provenance\_minimal.ttl](prov-o-qualified/cdif_provenance_minimal.ttl), [.jsonld](prov-o-qualified/cdif_provenance_minimal.jsonld) | generated: `python tools/cdifProvToProvO.py <cdifProv> <out.ttl>` | 66 triples: 2 usages (input, software), 1 generation (the dataset), 1 association with its plan; the tree is isomorphic under rdflib and pyld |
| **PROV-O, plain** | [prov-o-unqualified/cdif\_provenance\_minimal.ttl](prov-o-unqualified/cdif_provenance_minimal.ttl), [.jsonld](prov-o-unqualified/cdif_provenance_minimal.jsonld) | generated: the same with `--unqualified` | 53 triples: 2 `prov:used`, 1 `prov:wasGeneratedBy` + `prov:generatedAtTime`, 1 `prov:wasAssociatedWith`; the plan is lost; the tree is isomorphic |
| **RO-Crate, Process Run Crate 0.5** | [ro-crate/cdif\_provenance\_minimal/ro-crate-metadata.json](ro-crate/cdif_provenance_minimal/ro-crate-metadata.json), [tree](ro-crate/cdif_provenance_minimal.jsonld) | written from the cdifProv file | 10 entities; 48 triples; the tree is isomorphic. `rocrate-validator` 0.14.0, `-p process-run-crate-0.5 -m` (metadata only): every REQUIRED check passes; 7 RECOMMENDED checks fail, listed below |

The crate is a Process Run Crate rather than a Provenance Run Crate because there is no workflow,
only one tool run.

The 7 RECOMMENDED failures, none filled in with invented values:

- **The crate's `author` and `publisher`:** the cdifProv record names neither.
- **A trailing `/` on the output dataset's IRI:** RO-Crate treats a `Dataset` data entity as a
  directory, and recommends its IRI end in `/`. The IRI is kept as it is, so the four files can be
  loaded together.
- **The two `example.org` data entities:** each is web-based, so it is flagged as unavailable. The
  input file is also flagged for having no `contentSize` and no `sdDatePublished`.

To meet the profile, the crate writes the times with `+00:00` in place of `Z`.

## Findings

- **A plan named only by `{@id}` is thin in every form.**
  - **PROV-O, qualified:** it becomes a `prov:Plan` with nothing said about it, on the agent's
    association.
  - **PROV-O, plain:** it is lost.
  - **RO-Crate:** Process Run Crate has no slot for a plan; Workflow Run Crate's slot is the run's
    `instrument`, which only fits a workflow. The crate keeps `actionProcess`, but that term is not
    in the RO-Crate 1.1 context and JSON-LD drops it without warning. The crate's `@context` adds
    it, and the plan becomes a contextual `HowTo` entity with no properties.
- **The output needs no `schema:result`.** The root names its generating activity, and that is the
  output. PROV-O gives it a generation at the activity's end time. In the RO-Crate, the root `./` is
  the crate, not the dataset, so the dataset becomes a `Dataset` data entity in `hasPart` and the
  `result` of the `CreateAction`. It has to be in `hasPart`: as a contextual entity only, the crate
  fails a REQUIRED check.
- **The two crates place the described dataset differently.**
  - **This crate** keeps the dataset as an entity with its own IRI, so it joins with the cdifProv
    and PROV-O files.
  - **The workflow crate** uses the root `./` for the dataset and lists the result files, so its
    dataset IRI (`ex:fes2FitResults`) does not appear.

  One convention should be chosen for the remaining scenarios.
