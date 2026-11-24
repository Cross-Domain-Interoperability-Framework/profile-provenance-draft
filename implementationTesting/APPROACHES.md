# One scenario, every provenance approach

The same data-generation story is written out in each provenance approach CDIF is weighing, so they
can be compared feature by feature. The story is the 2026 Dagstuhl "quantitative" scenario
(absorbance → blank correction → calibration → uncertainty → validation), extended with the
features the ODIS Jules Verne example ([ODIS\_provExampleJulesVerne.json](../examples/ODIS_provExampleJulesVerne.json))
exercises: a sample and what it was taken from, a person with names and an affiliation, an
instrument, a consumed reagent, a tool, a location, an action status, and a procedure with a
documentation link, prep and perform times and a cost.

**The extensions are invented.** Everything not in the Dagstuhl Turtle is marked `# + illustrative`
in the master. The values are plausible, not real.

**More scenarios.** This page is the first of a set, each written in cdifProv and mapped to PROV-O
(qualified and plain) and an RO-Crate, so that between them they cover the cdifProvenance schema:
[a computational workflow run](SCENARIO_workflow.md) is the second, and [a minimal record](SCENARIO_minimal.md) the third, and [a laboratory protocol with sub-protocols](SCENARIO_lab_protocol.md) the fourth, and [a field sample to a data product](SCENARIO_field_sample.md) the fifth. [A qualitative assessment](SCENARIO_qualitative.md) is the sixth. [The laboratory measurement](SCENARIO_lab_measurement.md) brings this page's cdifProv file and crate onto the same conventions, and maps the cdifProv file to PROV-O. [MAPPING.md](MAPPING.md) is the
construct-by-construct table the scenarios share.

## The scenario

The record describes how one number came to be: a validated concentration of a dissolved analyte
in a river-water sample, measured by absorbance. Told in order:

**Sampling.** On 4 November 2026, from 08:10 to 08:15 UTC, Dr Ana Lima, an analyst acting on
behalf of an analytical laboratory, took water from a river reach and filtered it. The filtered
water sample is what everything after it is about.

**The run.** On 5 November she carried out a concentration determination run, as its responsible
analyst, following the laboratory's plan "Determine analyte concentration from absorbance, with
uncertainty and validation". The run began at 10:18 and was completed. It has five steps, each
recorded as part of the run:

1. **Absorbance measurement**, 10:18 to 10:19, in the laboratory. Ana, as operator, followed the
procedure "Absorbance measurement in a 1 cm cuvette" (20 minutes' preparation, 5 minutes to
perform, about 12 USD, with a video showing how). She used the water sample (the sample
measured), a UV-Vis spectrophotometer (the instrument), 2 mL of a colour-forming reagent (used
up by the measurement, at 10:19) and a 1 cm quartz cuvette (a tool). The step produced the raw
absorbance data for the sample at 10:19.
2. **Blank correction**, 10:21:00 to 10:21:04. The analysis software, acting as processing agent,
applied a blank-correction specification to the raw absorbance and produced the blank-corrected
absorbance, which is derived from the raw data.
3. **Calibration-based derivation**, 10:23:14 to 10:23:18. The software, acting as derivation
agent, applied a calibration relationship to the corrected absorbance and produced the analyte
concentration of the water sample, derived from the corrected absorbance.
4. **Uncertainty assessment** (no time recorded). The software used the concentration and an
uncertainty specification to produce the concentration's uncertainty.
5. **Validation** (no time recorded). The software checked the concentration and its uncertainty
against a validation criterion and produced the validation result. That result is the end of the
chain and the root of the record: everything else is reached by following where it came from.

**Which parts come from Dagstuhl.** Steps 2 to 5, the software, the three specifications and the
validation criterion, the raw absorbance data and every entity derived from it are the Dagstuhl scenario

&#x20;(https://drive.google.com/file/d/1doNm2uAHy70bih5HYdeM7SZ8ar-jY3Nx/view?usp=drive\_link, originally from 

Iseult Lynch, via Gemini AI) as written, with its times. The sampling, the absorbance measurement and 

everything it used, Ana, the laboratory, the run and its plan, the roles, "part of the run" and "about 

the sample" are the illustrative additions.

**What only the cdifProv file adds.** Two more steps: an instrument calibration from 09:40 to 10:05,
in which the spectrophotometer measured certified calibration standards to produce the calibration
curve the derivation step uses, and a first absorbance attempt from 10:12 to 10:13 that failed
because an air bubble in the cuvette made the reading unstable. It also names Ana as the person
responsible for each software step, and starts the run at the calibration, 09:40 on 5 November.

**The cdifProv file goes further than the master.** To exercise every slot the cdifProvenance schema
offers, it adds an instrument calibration activity, a failed first measurement, activity types,
identifiers, descriptions, a full instrument description, software version, located places,
procedure steps and constants, and vocabulary roles. These are also illustrative, and the other
approaches do not carry them. See [cdifProv against the draft profile](#cdifprov-against-the-draft-profile).

## Files

|approach|file|how it was made|checked with|
|-|-|-|-|
|**PROV-O, qualified** (master)|[prov-o-qualified/cdif\_provenance\_quantitative.ttl](prov-o-qualified/cdif_provenance_quantitative.ttl)|hand-written: the Dagstuhl Turtle unchanged, plus the extensions|every term and domain/range against PROV-O; contains all 51 named triples and 10 blank nodes of the Dagstuhl source|
|PROV-O, qualified, JSON-LD|[prov-o-qualified/cdif\_provenance\_quantitative.jsonld](prov-o-qualified/cdif_provenance_quantitative.jsonld)|generated from the master; one nested tree rooted at the final output, like `cdif\_provenance\_core.jsonld`|rdflib and pyld both give a graph isomorphic to the master (202 triples)|
|**PROV-O, plain relations**|[prov-o-unqualified/cdif\_provenance\_quantitative.ttl](prov-o-unqualified/cdif_provenance_quantitative.ttl)|generated: each qualified relation replaced by its plain form (`used`, `wasAssociatedWith`, `wasGeneratedBy` + `generatedAtTime`, `wasDerivedFrom`, `wasInvalidatedBy` + `invalidatedAtTime`)|terms; the loss is listed below|
|**PROV-JSON**|[prov-json/cdif\_provenance\_quantitative.json](prov-json/cdif_provenance_quantitative.json)|generated with the `prov` Python package (3.3.0), then three fixes, see findings|read back with `prov` and compared: identical to the master except the `prov:Role` declarations|
|**schema.org / cdifProv**|[cdifprov-schemaorg/cdif\_provenance\_quantitative.json](cdifprov-schemaorg/cdif_provenance_quantitative.json)|hand-written in this repo's conventions, corrected to pass validator.schema.org, then restructured onto the scenario conventions (2026-11-19, [SCENARIO\_lab\_measurement.md](SCENARIO_lab_measurement.md))|validator.schema.org, before the restructuring, see findings; `FrameAndValidate.py -v` against cdifProvenance 2.0 passes, with all 404 triples framed; `provenanceRules.shacl` conforms with no results; key count = triple count|
|PROV-O, qualified and plain, from cdifProv|[prov-o-qualified/cdif\_provenance\_quantitative.from-cdifprov.ttl](prov-o-qualified/cdif_provenance_quantitative.from-cdifprov.ttl), [prov-o-unqualified/…from-cdifprov.ttl](prov-o-unqualified/cdif_provenance_quantitative.from-cdifprov.ttl)|generated from the cdifProv file with [`tools/cdifProvToProvO.py`](../tools/cdifProvToProvO.py)|compared with the master in [SCENARIO\_lab\_measurement.md](SCENARIO_lab_measurement.md#the-generated-prov-o-against-the-master)|
|**RO-Crate 1.1**|[ro-crate/cdif\_provenance\_quantitative/ro-crate-metadata.json](ro-crate/cdif_provenance_quantitative/ro-crate-metadata.json)|written from the cdifProv file (until 2026-11-19 a hand-written Process Run Crate 0.5, see note 13)|`rocrate-validator` 0.14.0, profile `ro-crate-1.1`: every REQUIRED check passes; 6 RECOMMENDED checks fail, see [SCENARIO\_lab\_measurement.md](SCENARIO_lab_measurement.md)|
|**DDI-CDI 1.0** (draft)|[ddi-cdi/cdif\_provenance\_quantitative.ttl](ddi-cdi/cdif_provenance_quantitative.ttl)|hand-written from the DDI-CDI 1.0 ontology|every term and domain/range against the 16 ontology modules. **Not reviewed by a DDI-CDI user.**|
|**P-Plan** + PROV|[p-plan/cdif\_provenance\_quantitative.ttl](p-plan/cdif_provenance_quantitative.ttl)|hand-written overlay on the master|terms and domain/range, with the master merged in for typing|
|**ProvONE** + PROV|[provone/cdif\_provenance\_quantitative.ttl](provone/cdif_provenance_quantitative.ttl)|hand-written overlay on the master|the same|
|**SOSA/SSN** + PROV|[sosa/cdif\_provenance\_quantitative.ttl](sosa/cdif_provenance_quantitative.ttl)|hand-written overlay on the master|the same, with the SOSA-PROV alignment of SSN §6.5|

All files use the master's IRIs (`https://example.org/cdif-prov/…`), so any of them can be loaded
together with the master. P-Plan, ProvONE and SOSA are **overlays**: they add their own layer
(the plan, the wiring, the measurement) and leave the rest to PROV.

### JSON-LD trees for comparison

CDIF's RDF implementations are JSON-LD, so every approach that is RDF also has a compacted,
tree-shaped JSON-LD copy beside its source:

|approach|JSON-LD tree|roots|
|-|-|-|
|PROV-O, qualified|[prov-o-qualified/cdif\_provenance\_quantitative.jsonld](prov-o-qualified/cdif_provenance_quantitative.jsonld)|1: `ex:validationResult`|
|PROV-O, plain relations|[prov-o-unqualified/cdif\_provenance\_quantitative.jsonld](prov-o-unqualified/cdif_provenance_quantitative.jsonld)|1: `ex:validationResult`; the two plans, cut off once `hadPlan` is dropped, are in its `@included`|
|RO-Crate|[ro-crate/cdif\_provenance\_quantitative.jsonld](ro-crate/cdif_provenance_quantitative.jsonld)|1: the crate's root `schema:Dataset` (`./`), with the metadata descriptor nested under `@reverse`|
|DDI-CDI|[ddi-cdi/cdif\_provenance\_quantitative.jsonld](ddi-cdi/cdif_provenance_quantitative.jsonld)|4: the agents (`ProcessingAgent\_performs\_Activity` points from agent to activity)|
|P-Plan|[p-plan/cdif\_provenance\_quantitative.jsonld](p-plan/cdif_provenance_quantitative.jsonld)|20: each activity and entity of the run, with its step or variable, and the plan, nested inside|
|ProvONE|[provone/cdif\_provenance\_quantitative.jsonld](provone/cdif_provenance_quantitative.jsonld)|1|
|SOSA/SSN|[sosa/cdif\_provenance\_quantitative.jsonld](sosa/cdif_provenance_quantitative.jsonld)|3: the three observations and the sampling|

Each is generated from its source with [`tools/rdfToJsonLdTree.py`](../tools/rdfToJsonLdTree.py)
(`python tools/rdfToJsonLdTree.py SRC OUT`; the RO-Crate also takes `--base http://rocrate.invalid/crate/`
for its relative `@id`s; each plain PROV-O tree takes `--order-like` its qualified counterpart, so the two list keys and values in the same order, a qualified relation standing for its plain form, and each RO-Crate tree `--order-like` its cdifProv source in `cdifprov-schemaorg/`), which checks that rdflib and pyld both read the output back as a graph
isomorphic to the source. The two master trees take `--root ex:validationResult`: since the run
lists its steps (`dcterms:hasPart`, 2026-11-23) nothing points at it either, so without the option
it would be a second root; with it, the run is nested under the validation step with `@reverse`. A node is described in full where it is first reached and is an `{"@id"}` reference after that;
the root is the `schema:Dataset` when there is one, as in CDIF records (anything pointing at it that is not otherwise reached is nested under it with `@reverse`); otherwise roots are the nodes nothing else points at, largest tree first, in `@graph` when there are several. Only the RO-Crate has a Dataset; the PROV-O master's root `ex:validationResult` is untyped as to schema.org.
The number of roots is itself a comparison: the overlays point outward from the run's
activities, entities or agents, so they do not form one record. Prefixes are the source's;
datatyped literals keep their datatype (coerced in `@context`).

* **The RO-Crate tree is not an RO-Crate.** RO-Crate requires the flattened `@graph` with its own
context; the tree uses `schema:` CURIEs so it lines up with the cdifProv file. Its relative `@id`s
(`./`, `ro-crate-metadata.json`) resolve against the file's location, as in the crate.
* **PROV-JSON has no tree.** It is not JSON-LD (see the PROV-JSON finding below); its RDF form is
the PROV-O graph the master already gives.
* **cdifProv is already a tree.**
* **The plain-relations Turtle declares schema.org as `schema1:`** (an artefact of how it was
generated); its JSON-LD uses `schema:`.

### Rooted on the run

Where a source has the overall run, `ex:concentrationRun`, a second tree is rooted on it
(`python tools/rdfToJsonLdTree.py SRC OUT --root ex:concentrationRun`). What hangs directly under
the run shows how each approach ties a step to it:

|approach|run-rooted tree|under the run|
|---|---|---|
|PROV-O, qualified|[prov-o-qualified/cdif\_provenance\_quantitative.run-rooted.jsonld](prov-o-qualified/cdif_provenance_quantitative.run-rooted.jsonld)|5 steps, forward, by `dcterms:hasPart` (the sampling is not part of the run; it is reached through the sample)|
|PROV-O, plain relations|[prov-o-unqualified/cdif\_provenance\_quantitative.run-rooted.jsonld](prov-o-unqualified/cdif_provenance_quantitative.run-rooted.jsonld)|the same 5 steps; the two plans no longer linked by `hadPlan` are in `@included`|
|cdifProv|[cdifprov-schemaorg/cdif\_provenance\_quantitative.run-rooted.jsonld](cdifprov-schemaorg/cdif_provenance_quantitative.run-rooted.jsonld)|7 steps, forward, by `schema:actionProcess` → `schema:step`; the sampling is reached through the sample, the run's `schema:object`|
|RO-Crate|[ro-crate/cdif\_provenance\_quantitative.run-rooted.jsonld](ro-crate/cdif_provenance_quantitative.run-rooted.jsonld)|the same 7 steps, by `actionProcess` → `step`|
|DDI-CDI|[ddi-cdi/cdif\_provenance\_quantitative.run-rooted.jsonld](ddi-cdi/cdif_provenance_quantitative.run-rooted.jsonld)|6 steps, forward, by `cdi:Activity\_has\_Step`; the analyst by `@reverse cdi:ProcessingAgent\_performs\_Activity`; the laboratory, which nothing links to (note 11), in `@included`|
|ProvONE|[provone/cdif\_provenance\_quantitative.run-rooted.jsonld](provone/cdif_provenance_quantitative.run-rooted.jsonld)|6 steps, by `@reverse provone:wasPartOf`; `ex:validationResult`, whose only link is a qualified generation (entity → blank node → activity), in `@included`|

Not possible for **P-Plan** and **SOSA/SSN** (overlays that do not contain the run; P-Plan names it
only in a comment) or **PROV-JSON** (not JSON-LD).

A node that points *at* the run (a step that is part of it, an agent that performs it) is placed
directly under the run with `@reverse`; any other node that points into the tree goes under the
nearest node it points at; anything unconnected goes in `@included`. Each file is isomorphic to its
source under rdflib and pyld (`xsd:double` values compared by value: pyld writes them in canonical
E-notation).

### Diagrams

Each PROV-O Turtle file in `prov-o-qualified/` and `prov-o-unqualified/`, and each cdifProv record in
`cdifprov-schemaorg/`, has an SVG diagram beside it with the same name, generated with
[`tools/rdfToSvg.py`](../tools/rdfToSvg.py) (`python tools/rdfToSvg.py SRC OUT.svg`, Graphviz `dot`
on the PATH). The cdifProv run-rooted tree is the same graph as its record, and the
`before-schemaorg-validator` file is a superseded snapshot, so neither has one. Each resource is a box:
its compact IRI and types, then one row per literal-valued property (a long value is cut, and the
full value is its tooltip). Each link between resources is an arrow labelled with its predicate.
Boxes take the PROV-O colours: entities yellow, activities blue, agents orange, and the blank nodes
of qualified relations grey. A leaf that several boxes point to, such as a role or a Wikidata kind
term, is drawn at each reference with a dashed border. `schema:additionalProperty` is left out, with the parameter
values (`schema:PropertyValue`) only it reaches: the diagrams show how the resources link, and the
parameters are in the record. An RO-Crate lists a step's parameters as PropertyValues in its
`object`, beside its inputs; those are left out too. Above each diagram is a legend of the box
colours and borders and, when something was left out, a note saying what. Open a diagram in a browser to zoom it.
For example, [prov-o-qualified/cdif\_provenance\_minimal.svg](prov-o-qualified/cdif_provenance_minimal.svg)
and the lab measurement pair,
[qualified](prov-o-qualified/cdif_provenance_quantitative.from-cdifprov.svg) and
[plain](prov-o-unqualified/cdif_provenance_quantitative.from-cdifprov.svg), with their cdifProv source,
[cdifprov-schemaorg/cdif\_provenance\_quantitative.svg](cdifprov-schemaorg/cdif_provenance_quantitative.svg).

Each diagram also has a `.rooted.svg` beside it (`python tools/rdfToSvg.py SRC OUT.rooted.svg --rooted`),
laid out from the record's root, as its JSON-LD tree is: the dataset is the first box, and each node
follows the node nearer the root that it is linked to. In the other diagrams the longest chain of
arrows sets the layout, so a node that points into the record, such as its catalog record
(`schema:about`), can come before the dataset; until 2026-11-23, when each PROV-O step pointed at
its run (`dcterms:isPartOf`, now the run's `dcterms:hasPart`), a step could. In the rooted ones an arrow that points back toward the root is
laid out from the root's side, its arrowhead unchanged. The two hand-written `quantitative.ttl`
files have no `schema:Dataset`, so they are drawn with `--root ex:validationResult`, the final
output, as their trees are. For example, the workflow:
[qualified](prov-o-qualified/cdif_provenance_workflow.rooted.svg) starts at `ex:fes2FitResults`,
then its generation by `ex:fes2Run`, then the run's steps.

Each RO-Crate in `ro-crate/` has both diagrams beside its tree, `ro-crate/<name>.svg` and
`ro-crate/<name>.rooted.svg`, drawn from its `ro-crate-metadata.json` with the tree's base and the
record's prefix (`--base http://rocrate.invalid/crate/ --prefix ex=https://example.org/cdif-prov/`,
and `--rooted` for the rooted one). The run-rooted crate tree is the same graph as the
quantitative crate, so it has only its rooted diagram. The rooted one starts at the crate's root
dataset, `./`, as the tree does; the run-rooted one starts at `ex:concentrationRun`
(`--root ex:concentrationRun`), as its tree does. A `CreateAction` is coloured as an activity. For
example, the workflow crate, [default](ro-crate/cdif_provenance_workflow.svg) and
[rooted](ro-crate/cdif_provenance_workflow.rooted.svg).

How every file here is made is in [README.md](README.md).

## The matrix

✔ native · ◐ partial, see note · **ann** only as an annotation from another vocabulary
(schema.org, Dublin Core) on the node · ✘ not expressible · PROV: the overlay leaves this to PROV

|feature|PROV-O qualified|PROV-O plain|PROV-JSON|cdifProv|RO-Crate 1.1|DDI-CDI|P-Plan|ProvONE|SOSA|
|-|-|-|-|-|-|-|-|-|-|
|activity start and end time|✔|✔|✔|✔|✔|✘|PROV|PROV|✔ ¹|
|inputs used|✔|✔|✔|✔|✔|✔ ²|PROV|✔|◐ ³|
|**what role each input played** (sample, instrument, reagent, tool, data, method)|✔ `hadRole`|✘|✔ `prov:role`|◐ ⁴|◐ ⁵|◐ ⁶|◐ ⁷|◐ ⁸|◐ ⁹|
|outputs, with time of generation|✔|✔|✔|◐ no time|◐ no time|◐ no time|PROV|✔|✔ `resultTime`|
|output derived from input, and by which activity|✔|◐ activity lost|✔|◐ implied|◐ implied|◐ implied|PROV|◐ implied|✘|
|responsible agent, with role|✔|◐ role lost|✔|✔ ¹⁰|◐ no role|◐ no role|PROV|◐|◐ sensor / sampler|
|person's names and honorific|ann|ann|ann|✔|✔|✔|—|—|—|
|organization the person acts for|✔|✔|✔|◐ affiliation|◐ affiliation|◐ ¹¹|—|—|—|
|software that ran a step|✔|✔|✔|✔ ¹²|✔|✔ `Machine`|PROV|✔|◐ as sensor|
|instrument|◐ role only|◐ just "used"|◐ role only|✔|✔ ¹³|◐ ¹⁴|◐ ⁷|◐ ⁸|✔ `Sensor`|
|reagent, and that it was used up|✔ role + invalidation|◐ role lost|✔|◐ no consumption|◐ ⁵|◐ ⁶|◐ ⁷|◐ ⁸|✘|
|tool (cuvette)|◐ role only|◐|◐|◐ ¹⁵|◐ ⁵|◐ ⁶|◐ ⁷|◐ ⁸|✘|
|sample, and what it was taken from|◐ ¹⁶|◐|◐|◐ ¹⁶|◐ ¹⁶|◐ ¹⁶|◐ ⁷|◐|✔ `Sample` `isSampleOf`|
|observed property|✘|✘|✘|✘|✘|✘|✘|✘|✔|
|result is about the sample|ann|ann|ann|✔ `about`|✔ `about`|✘|—|—|✔|
|location|✔|✔|✔|◐ ¹⁷|✔|◐ ¹⁸|—|—|◐ platform|
|action status|ann|ann|ann|✔|✔ ¹⁹|✘|—|—|—|
|plan or procedure the step followed|✔ `hadPlan`|✘|✔|✔ `actionProcess`|◐ ²⁰|◐ ²¹|✔|✔ `Program`|✔ `usedProcedure`|
|procedure documentation, prep and perform time, cost|ann|ann|ann|✔ ²²|✔ ²²|◐ text|✘|✘|✘|
|**planned steps and their order, before the run**|✘|✘|✘|◐ ²³|◐ ²³|✔ `Sequence`|✔ `isPrecededBy`|✔ ²⁴|✘|
|step is part of the overall run|ann|ann|ann|✔ `step`|✔ `step`|✔ `has\_Step`|✔ plan side|✔ `wasPartOf`|✘|
|**data-flow wiring between steps**|◐ shared entities|◐|◐|◐ `object`/`result`|◐ `object`/`result`|✔ `InformationFlowDefinition`|✔ shared variables|✔ ports and channels|✘|
|links to other graphs by IRI|✔|✔|✔|✔|✔|◐ ²⁵|✔|✔|✔|

### What the plain-relations form loses

Generating it from the master drops **34 facts**: 13 role declarations, 9 roles of inputs, 5 roles
of agents, the 4 plans that steps followed (`absorbanceProcedure`, `blankCorrectionSpec`,
`calibrationRelationship`, `concentrationDeterminationPlan`), and, for 3 derivations, the activity
that did the deriving. Times survive (`generatedAtTime`, `invalidatedAtTime`). That is the whole
cost of skipping the qualified pattern for this scenario: *who and what played which part*.

### Notes

1. `phenomenonTime` (an interval) and `resultTime`, for the measurement only.
2. `Activity-entityUsed`, as a `Reference` structure holding the entity's URI.
3. The feature of interest is an input; data inputs need `prov:used` (SOSA has no term).
4. Since 2026-11 (metadataBuildingBlocks #81) every tool, reagent and instrument is a `schema:instrument` item on the activity, told apart by a Wikidata kind term, and inputs are `schema:object`; `prov:used` is gone. Before that: role properties on the activity itself (`schema:instrument`, `bios:reagent`, `bios:computationalTool`), with every input also listed in `prov:used` as a plain `{@id}`. Data inputs are `schema:object`; the method is `schema:actionProcess`. No role for a sample vs a data input. The profile itself used to put role-keyed wrappers *inside* `prov:used` (`{"schema:instrument": \[...]}`). In RDF each wrapper is an untyped blank node, so the activity "uses" the blank node, the instrument is a property of that node rather than of the action, and validator.schema.org reports "Unspecified Type". #81 removed the wrappers, so the profile now puts the used resources on the action, as this example does, and checks each `schema:instrument` item's description there.
5. `instrument` vs `object` only. The reagent goes into `object` with the sample, unlabelled; the cuvette is a second `instrument`.
6. All in `Activity-entityUsed`, unlabelled. `Reference-semantic` could carry a role; not used here.
7. One variable per input, named by its label; the variable has no type for "instrument" or "reagent".
8. One port per input, so the port is the role; ports are not typed either.
9. Sensor and feature of interest are distinguished; reagent and tool have no place.
10. `schema:Role` with `roleName` wrapping the person, the person repeated inside the Role under the same property (`schema:agent` in an agent Role, `schema:participant` in a participant Role), as schema.org's Role pattern and validator.schema.org require. The profile's `AgentInRole` takes the agent under `schema:contributor`, `schema:agent` or `schema:participant`, so it accepts this form; the role name can be a `schema:DefinedTerm` from a vocabulary (DataCite contributor types here). `cdifProvActivity` SHACL warns that an activity "should identify a responsible agent" when it has no `schema:agent` at all, which is what a software-only step looks like.
11. `Organization` exists, but nothing in the process model links an individual to it.
12. As a `schema:instrument` with the software kind (Q7397), not as an agent: this repo's convention (`agents.md`). The person who ran the software is the step's `schema:agent`.
13. A `CreateAction` whose `instrument` is the equipment, RO-Crate 1.1's own pattern. Process Run Crate requires every action's `instrument` to be software (`SoftwareApplication`, `SoftwareSourceCode` or `ComputationalWorkflow`): the earlier crate of this scenario was a Process Run Crate, and its sampling and measurement actions failed that REQUIRED rule, since the spectrophotometer is not software. The crate is now plain RO-Crate 1.1.
14. A `Machine` typed `ProcessingAgent` that performs the measurement: an agent, not an input.
15. A second `schema:instrument`. `schema:tool` is a sub-property of `schema:instrument` but belongs to `HowTo` / `HowToDirection`, with values `HowToTool` or text, so it is wrong on an action.
16. As a derivation (PROV) or as the object → result of a sampling action (schema.org, RO-Crate, DDI-CDI); none of them types the sample as a sample of a feature.
17. `schema:location` is an inline `schema:Place` with name, type, identifier and coordinates, but no `@id`: a reference to the lab node is embedded by the frame and then rejected by the sealed `{@id}` slot (the frame-embed gap), so the link to `ex:laboratory01` is lost.
18. Via the agent: `ProcessingAgent\_operatesOn\_ProductionEnvironment`.
19. As the string `"http://schema.org/CompletedActionStatus"`; the validator rejects an `{@id}`.
20. `actionProcess`, a term the crate's `@context` adds (it is not in the RO-Crate 1.1 context), to the procedure as performed; that `HowTo` names the plan in `isBasedOn`, and the plan is a `HowTo` with no properties. A Workflow Run Crate adds a `ComputationalWorkflow` and `HowToStep`s, for software only.
21. `Activity-description` text, or `Step-script` for executable code; no plan class.
22. `actionProcess` is a `schema:HowTo`: `url` for the video, `prepTime`, `performTime`, `estimatedCost`.
23. The run's `schema:actionProcess` is the procedure as performed: a `schema:HowTo` whose 7 `schema:step`s, with `schema:position`, are each typed `[schema:HowToStep, schema:Action]` and carry what they did; `schema:isBasedOn` names the plan. The order is therefore the run's, not a plan's before it: the plan is a reference only, and a step done twice (the failed absorbance attempt and its repeat) is two steps. Until 2026-11-19 the activities stood beside the run, each pointing to a planned step with P-Plan's `p:correspondsToStep`, which kept the plan reusable but could not say that a step was part of the run. Unlike the retired HowTo/step form ([../archive/](../archive/)), each step here is an action, with its own agent, inputs and outputs.
24. Programs and their channels; the order follows from the wiring, not a sequence.
25. Steps share the master's IRIs; entities do not: `Reference-uri` is a literal, so a graph merge does not connect them.

## Findings from the validators

* **cdifProv, framing picks the wrong node silently.** With the intermediate results typed `schema:Dataset`, `FrameAndValidate` framed `ex:absorbanceSource` and reported PASS. Retyping them `schema:CreativeWork` made it frame the root, and validation then failed honestly until fixed. This is the first of CLAUDE.md's two traps.
* **cdifProv 1.1: every activity needed `prov:used` (superseded).** In 1.1, `cdifProvActivity` SHACL (run with RDFS inference, as the conformance detector runs it) made `prov:used` mandatory, and without it `--conformance` dropped `provenance/1.1` without saying why. The fix then was to repeat the `schema:object` inputs in `prov:used`. Since metadataBuildingBlocks#81 (cdifProvenance 2.0) `prov:used` is not used. An activity needs at least one of `schema:instrument`, `schema:object` or `schema:actionProcess`, and none of the current files has `prov:used`.
* **cdifProv, Person needs a contact point** (SHACL Info only).
* **cdifProv, validator.schema.org and the profile schema disagreed (resolved 2026-11-17).** validator.schema.org wants `actionStatus` as a full URI (`"http://schema.org/CompletedActionStatus"`), where the profile enum allowed only CURIE strings; and it wants a Role to repeat its parent property inside (`schema:agent` within an agent Role, `schema:participant` within a participant Role), where the profile's `AgentInRole` required `schema:contributor`. The example follows validator.schema.org, and the profile now accepts both forms: the `actionStatus` enum and shapes take the CURIE or the full `http://` / `https://schema.org/` IRI (metadataBuildingBlocks#105), and `AgentInRole` and its Role shape take the agent under `schema:contributor`, `schema:agent` or `schema:participant` (metadataBuildingBlocks#111). FrameAndValidate unwraps a Role's one `schema:participant` from the array it wraps every `schema:participant` in, as it already did for `schema:contributor` (validation#29). The version before these corrections is [cdifprov-schemaorg/cdif\_provenance\_quantitative.before-schemaorg-validator.json](cdifprov-schemaorg/cdif_provenance_quantitative.before-schemaorg-validator.json).
* **The frame silently dropped content, so FrameAndValidate passed on a trimmed document (fixed 2026-11-10).** In `cdifProvenance-frame.jsonld` the activity sub-frames for `prov:used`, `schema:agent`, `schema:participant`, `schema:actionProcess` and `prov:wasAssociatedWith` named nested properties (`schema:instrument`, `schema:identifier`, `schema:contributor`, `schema:step`, ...). A JSON-LD sub-frame that names properties also *filters*: a value with none of them was left out, so plain `{@id}` inputs, Role agents and stepless procedures never reached the JSON Schema. Those sub-frames are now `@embed` only, and `prov:used` is `@once` (with `@always` the frame copied each earlier output into the next step's `prov:used`, where it matched no branch). Every example keeps its result and frames more of its source (this one: 319 → 424 of 424 triples at the time, before its 2026-11-19 restructuring to 404 triples, all framed; FeS2: 132 → 171 of 204). The remaining loss is `schema:result` descriptions, which FrameAndValidate collapses to `{@id}` (`REFERENCE\_ONLY\_KEYS`, validation repo).
* **cdifProv 1.1: software in `prov:used` had to be typed `prov:Entity` (superseded).** Framing visited `prov:used` before `bios:computationalTool` (properties are processed in IRI order), so the software was embedded first in `prov:used`, where the profile accepted an inline node only if it was a `prov:Entity`. Since metadataBuildingBlocks#81, software is a `schema:instrument` item with the software kind (Q7397) and is typed `schema:SoftwareApplication`; neither `prov:used` nor `bios:computationalTool` is involved.
* **Process Run Crate cannot describe a lab step.** See note 13; the crate is now plain RO-Crate 1.1. The validator also rejects `Z` in times (its pattern wants `+hh:mm`), so the crate uses `+00:00`, and it wants `actionStatus` as a string.
* **The `prov` Python package's RDF reader drops agents.** Converting the master to PROV-JSON lost the person, the lab and the software, renamed the `schema` prefix to `schema1`, and rewrote every `Z` as `+00:00`. The file was patched for all three and then read back with the same package to confirm.
* **PROV-JSON is not JSON-LD, and its typed values carry no RDF meaning.** A typed value is written `{"$": "prov:Person", "type": "xsd:QName"}`. To a JSON-LD processor `$` is an ordinary key with no mapping, and the `type` tag (`xsd:QName`, or `prov:QUALIFIED\_NAME` in the PROV-JSON spec's own examples) has no RDF semantics, so loading the file as JSON-LD yields none of these values. This is a limitation of the format, not a defect in this file, and it is what openprov/prov-jsonld issue #7 is about; PROV-JSON has to be read with a PROV-aware parser such as the `prov` package. The `$` key does not mean the file came through XML.
* **`prov` writes `xsd:QName` where the PROV-JSON spec writes `prov:QUALIFIED\_NAME`.** Both parse. The four agent types restored by hand had used the spec's spelling and a one-element list; they now use `prov`'s `xsd:QName` and a bare object, so the file re-serializes through `prov` 3.3.0 unchanged apart from the renumbered relation ids (`\_:idN`) and the restored `Z` times.
* **DDI-CDI has no time, status or role on an activity**, and its entity links are URI strings, not RDF links.

## cdifProv against the draft profile

Checked against the content model and competency questions in `CDIF prov profile - draft.docx`
(draft 2026-01-30).

**Exercised in the example**, with the schema property used:

|draft provision|in the example|
|-|-|
|activity type (1..\*)|`schema:additionalType` → CDIF activity concepts, on the sampling (`cdifact:Sampling`) and the run (`cdifact:Analysis`) only: a step's `schema:additionalType` is string-only|
|activity description, identifier|`schema:description`; `schema:identifier` as a `PropertyValue` and as a string|
|ordered sequence of activities|the run's procedure lists its 7 steps, each an action, with `schema:position` (see note 23)|
|input (observation data, external information)|`schema:object`; external inputs are the certified standards, the calibration curve and the acceptance criterion|
|output: description, file object, identifier linking to the next input|`schema:result` with `schema:description`, `schema:url`, `schema:encodingFormat`; the `@id` is what the next step's `schema:object` cites|
|procedure: description, protocol name and link, constants and assumptions, algorithm, sentinel values|`schema:actionProcess` (`HowTo`: name, description, url, steps); constants, detection limit and the treatment of values below it as activity `schema:additionalProperty`|
|tools: calibration, software, instrument|the calibration step and its curve; `schema:instrument` items with the Wikidata kinds for software, instrument and reagent|
|actor (1..\*): person with name, identifier, affiliation; role|`schema:agent` as a `schema:Role` with a DataCite `DefinedTerm` role; ORCID-shaped `PropertyValue`; `schema:affiliation`; `schema:participant` for the lab|
|location: name, identifier, type|`schema:location` with name, `schema:identifier`, `schema:additionalType`, `schema:geo`|
|instrument: type, model and manufacturer, identifier, configuration, parts|`schema:category`, `schema:model`, `schema:manufacturer`, a serial-number `schema:identifier`, `schema:additionalProperty`, `schema:hasPart`, `schema:owner`|
|software: name, version, identifier|`schema:name`, `schema:softwareVersion`, `schema:identifier`|
|failed activities|`schema:FailedActionStatus` + `schema:error`|

**Passes only because objects are open.** Activity type has no named property in the schema; it is
`schema:additionalType`, as the Bennu examples already use it. `schema:softwareVersion`,
`schema:givenName` / `familyName` / `honorificPrefix`, and `prepTime` / `performTime` /
`estimatedCost` on the procedure are not in the schema either.

**No slot, so not exercised:**

* **Quality.** Factors that might impact quality, a quality metric definition (identifier,
description, value domain), and a metric result linked to its metric. The uncertainty and the
validation outcome are plain `CreativeWork` outputs.
* **Mode of acquisition** (1..\*, controlled vocabulary).
* **Qualifications and training** of a person: free text in `schema:description` only.
* **Variable-level provenance:** what was measured per variable, dependencies between variables,
unit conversions, treatment of anomalous values. Only the SOSA overlay names the observed property.
* **Purpose, funding, target of study, overall text description:** the draft leaves these to the
discovery profile, and this provenance-only example does not repeat them.

**Draft cardinalities the schema does not enforce.** The draft wants at least one type, one actor
and one output per activity. The example meets the first two everywhere, and the third everywhere
except the failed attempt; the schema itself requires none of them.

## What this suggests

* **Qualified PROV-O is the most expressive serialization**, and the only one that keeps who and what played which part without inventing keys. Plain PROV-O and RO-Crate lose exactly that.
* **cdifProv covers the Jules Verne features best** (person, status, procedure details, result about the sample, instrument as a typed thing), but its steps are those of the run as performed (the plan is a reference only, so a planned step done twice is two steps), a step cannot take an activity type (its `schema:additionalType` takes strings only), the tool role is weak, and the draft's quality and acquisition-mode provisions have no slot.
* **The overlays answer different questions and combine.** P-Plan or ProvONE adds the plan and wiring that every retrospective form lacks; SOSA adds what was measured (feature, sample, property, sensor) that none of the others can say. Each needs PROV for the rest.
* **DDI-CDI** is strong on structure (steps, sequence, information flow) and weak on the run (no times, roles or status). It needs review by someone who uses it before any conclusion.

