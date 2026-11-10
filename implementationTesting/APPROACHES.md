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
responsible for each software step, and starts the run at the sampling, 08:10 on 4 November.

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
|**schema.org / cdifProv**|[cdifprov-schemaorg/cdif\_provenance\_quantitative.json](cdifprov-schemaorg/cdif_provenance_quantitative.json)|hand-written in this repo's conventions, then corrected to pass validator.schema.org|validator.schema.org; `FrameAndValidate.py -v` **fails** on the full-URI `actionStatus` (the profile enum wants CURIEs) and on the Role form, see findings; `provenanceRules.shacl` **fails** the same Role form ("a Role must be filled by a Person, Organization, or IRI reference", it looks for `schema:contributor`), `cdifProvActivity` SHACL Info only (it too expects CURIE status strings), key count = triple count|
|**RO-Crate, Process Run Crate 0.5**|[ro-crate/cdif\_provenance\_quantitative/ro-crate-metadata.json](ro-crate/cdif_provenance_quantitative/ro-crate-metadata.json)|hand-written|`rocrate-validator` 0.13.1, profile `process-run-crate-0.5`: fails one REQUIRED rule on the two lab actions, see findings|
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
|PROV-O, plain relations|[prov-o-unqualified/cdif\_provenance\_quantitative.jsonld](prov-o-unqualified/cdif_provenance_quantitative.jsonld)|3: `ex:validationResult`, plus the two plans, cut off once `hadPlan` is dropped|
|RO-Crate|[ro-crate/cdif\_provenance\_quantitative.jsonld](ro-crate/cdif_provenance_quantitative.jsonld)|1: the crate's root `schema:Dataset` (`./`), with the metadata descriptor nested under `@reverse`|
|DDI-CDI|[ddi-cdi/cdif\_provenance\_quantitative.jsonld](ddi-cdi/cdif_provenance_quantitative.jsonld)|4: the agents (`ProcessingAgent\_performs\_Activity` points from agent to activity)|
|DDI-CDI, rooted on the run|[ddi-cdi/cdif\_provenance\_quantitative.run-rooted.jsonld](ddi-cdi/cdif_provenance_quantitative.run-rooted.jsonld)|1: `ex:concentrationRun` (`--root ex:concentrationRun`). Its steps nest under `cdi:Activity\_has\_Step`; each agent sits under the first activity it performs, with `@reverse`; the laboratory, which nothing in the process model links to (note 11), is in `@included`|
|P-Plan|[p-plan/cdif\_provenance\_quantitative.jsonld](p-plan/cdif_provenance_quantitative.jsonld)|20: each activity and entity of the run, with its step or variable, and the plan, nested inside|
|ProvONE|[provone/cdif\_provenance\_quantitative.jsonld](provone/cdif_provenance_quantitative.jsonld)|1|
|SOSA/SSN|[sosa/cdif\_provenance\_quantitative.jsonld](sosa/cdif_provenance_quantitative.jsonld)|3: the three observations and the sampling|

Each is generated from its source with [`tools/rdfToJsonLdTree.py`](../tools/rdfToJsonLdTree.py)
(`python tools/rdfToJsonLdTree.py SRC OUT`; the RO-Crate also takes `--base http://rocrate.invalid/crate/`
for its relative `@id`s), which checks that rdflib and pyld both read the output back as a graph
isomorphic to the source. The qualified master's copy predates it and was made the same way. A node is described in full where it is first reached and is an `{"@id"}` reference after that;
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

## The matrix

✔ native · ◐ partial, see note · **ann** only as an annotation from another vocabulary
(schema.org, Dublin Core) on the node · ✘ not expressible · PROV: the overlay leaves this to PROV

|feature|PROV-O qualified|PROV-O plain|PROV-JSON|cdifProv|Process Run Crate|DDI-CDI|P-Plan|ProvONE|SOSA|
|-|-|-|-|-|-|-|-|-|-|
|activity start and end time|✔|✔|✔|✔|✔|✘|PROV|PROV|✔ ¹|
|inputs used|✔|✔|✔|✔|✔|✔ ²|PROV|✔|◐ ³|
|**what role each input played** (sample, instrument, reagent, tool, data, method)|✔ `hadRole`|✘|✔ `prov:role`|◐ ⁴|◐ ⁵|◐ ⁶|◐ ⁷|◐ ⁸|◐ ⁹|
|outputs, with time of generation|✔|✔|✔|◐ no time|◐ no time|◐ no time|PROV|✔|✔ `resultTime`|
|output derived from input, and by which activity|✔|◐ activity lost|✔|◐ implied|◐ implied|◐ implied|PROV|◐ implied|✘|
|responsible agent, with role|✔|◐ role lost|✔|✔ ¹⁰|◐ no role|◐ no role|PROV|◐|◐ sensor / sampler|
|person's names and honorific|ann|ann|ann|✔|✔|✔|—|—|—|
|organization the person acts for|✔|✔|✔|◐ affiliation|◐ affiliation|◐ ¹¹|—|—|—|
|software that ran a step|✔|✔|✔|✔ ¹²|✔ (required)|✔ `Machine`|PROV|✔|◐ as sensor|
|instrument|◐ role only|◐ just "used"|◐ role only|✔|✘ ¹³|◐ ¹⁴|◐ ⁷|◐ ⁸|✔ `Sensor`|
|reagent, and that it was used up|✔ role + invalidation|◐ role lost|✔|◐ no consumption|◐ ⁵|◐ ⁶|◐ ⁷|◐ ⁸|✘|
|tool (cuvette)|◐ role only|◐|◐|◐ ¹⁵|◐ ⁵|◐ ⁶|◐ ⁷|◐ ⁸|✘|
|sample, and what it was taken from|◐ ¹⁶|◐|◐|◐ ¹⁶|◐ ¹⁶|◐ ¹⁶|◐ ⁷|◐|✔ `Sample` `isSampleOf`|
|observed property|✘|✘|✘|✘|✘|✘|✘|✘|✔|
|result is about the sample|ann|ann|ann|✔ `about`|✔ `about`|✘|—|—|✔|
|location|✔|✔|✔|◐ ¹⁷|✔|◐ ¹⁸|—|—|◐ platform|
|action status|ann|ann|ann|✔|✔ ¹⁹|✘|—|—|—|
|plan or procedure the step followed|✔ `hadPlan`|✘|✔|✔ `actionProcess`|✘ ²⁰|◐ ²¹|✔|✔ `Program`|✔ `usedProcedure`|
|procedure documentation, prep and perform time, cost|ann|ann|ann|✔ ²²|✘|◐ text|✘|✘|✘|
|**planned steps and their order, before the run**|✘|✘|✘|◐ ²³|✘ ²⁰|✔ `Sequence`|✔ `isPrecededBy`|✔ ²⁴|✘|
|step is part of the overall run|ann|ann|ann|✘|✘|✔ `has\_Step`|✔ plan side|✔ `wasPartOf`|✘|
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
4. Role properties on the activity itself (`schema:instrument`, `bios:reagent`, `bios:computationalTool`), with every input also listed in `prov:used` as a plain `{@id}`. Data inputs are `schema:object`; the method is `schema:actionProcess`. No role for a sample vs a data input. This departs from the profile's role-keyed wrappers *inside* `prov:used` (`{"schema:instrument": \[...]}`): in RDF each wrapper is an untyped blank node, so the activity "uses" the blank node, the instrument is a property of that node rather than of the action, and validator.schema.org reports "Unspecified Type". With the roles on the action no blank node is used and the schema.org validator's type errors go away; the cost is that the profile schema's instrument pin (on the wrapper) no longer checks the instrument description.
5. `instrument` vs `object` only. The reagent goes into `object` with the sample, unlabelled; the cuvette is a second `instrument`.
6. All in `Activity-entityUsed`, unlabelled. `Reference-semantic` could carry a role; not used here.
7. One variable per input, named by its label; the variable has no type for "instrument" or "reagent".
8. One port per input, so the port is the role; ports are not typed either.
9. Sensor and feature of interest are distinguished; reagent and tool have no place.
10. `schema:Role` with `roleName` wrapping the person, the person repeated inside the Role under the same property (`schema:agent` in an agent Role, `schema:participant` in a participant Role), as schema.org's Role pattern and validator.schema.org require. The profile's `AgentInRole` wants `schema:contributor` there instead, so the profile schema rejects this form; the role name can be a `schema:DefinedTerm` from a vocabulary (DataCite contributor types here). `cdifProvActivity` SHACL warns that an activity "should identify a responsible agent" when it has no `schema:agent` at all, which is what a software-only step looks like.
11. `Organization` exists, but nothing in the process model links an individual to it.
12. As `bios:computationalTool` in `prov:used`, not as an agent: this repo's convention (`agents.md`). The person who ran the software is the step's `schema:agent`.
13. Process Run Crate requires every action's `instrument` to be software (`SoftwareApplication`, `SoftwareSourceCode` or `ComputationalWorkflow`). The spectrophotometer is an `IndividualProduct`, so the sampling and measurement actions fail that REQUIRED rule.
14. A `Machine` typed `ProcessingAgent` that performs the measurement: an agent, not an input.
15. A second `schema:instrument`. `schema:tool` is a sub-property of `schema:instrument` but belongs to `HowTo` / `HowToDirection`, with values `HowToTool` or text, so it is wrong on an action.
16. As a derivation (PROV) or as the object → result of a sampling action (schema.org, RO-Crate, DDI-CDI); none of them types the sample as a sample of a feature.
17. `schema:location` is an inline `schema:Place` with name, type, identifier and coordinates, but no `@id`: a reference to the lab node is embedded by the frame and then rejected by the sealed `{@id}` slot (the frame-embed gap), so the link to `ex:laboratory01` is lost.
18. Via the agent: `ProcessingAgent\_operatesOn\_ProductionEnvironment`.
19. As the string `"http://schema.org/CompletedActionStatus"`; the validator rejects an `{@id}`.
20. A Workflow Run Crate (not Process Run) adds a `ComputationalWorkflow` and `HowToStep`s.
21. `Activity-description` text, or `Step-script` for executable code; no plan class.
22. `actionProcess` is a `schema:HowTo`: `url` for the video, `prepTime`, `performTime`, `estimatedCost`.
23. The run's `schema:HowTo` lists ordered `schema:step`s with `schema:position`, but a step is only a name: nothing links it to the activity that carried it out. (Steps as the only record of the run, the HowTo/step form, was retired in this repo; see [../archive/](../archive/).)
24. Programs and their channels; the order follows from the wiring, not a sequence.
25. Steps share the master's IRIs; entities do not: `Reference-uri` is a literal, so a graph merge does not connect them.

## Findings from the validators

* **cdifProv, framing picks the wrong node silently.** With the intermediate results typed `schema:Dataset`, `FrameAndValidate` framed `ex:absorbanceSource` and reported PASS. Retyping them `schema:CreativeWork` made it frame the root, and validation then failed honestly until fixed. This is the first of CLAUDE.md's two traps.
* **cdifProv, every activity needs `prov:used`.** `cdifProvActivity` SHACL (run with RDFS inference, as the conformance detector runs it) makes `prov:used` mandatory. Without it, `--conformance` drops `provenance/1.1` without saying why. `Bennu-py-GC-MS.cdifprov.json` fails for this reason. The fix here follows the Galaxy actions converter: repeat the `schema:object` inputs in `prov:used`.
* **cdifProv, Person needs a contact point** (SHACL Info only).
* **cdifProv, validator.schema.org and the profile schema disagree.** validator.schema.org wants `actionStatus` as a full URI (`"http://schema.org/CompletedActionStatus"`), where the profile enum allows only CURIE strings; and it wants a Role to repeat its parent property inside (`schema:agent` within an agent Role), where the profile's `AgentInRole` requires `schema:contributor`. Both profile SHACL sets make the same assumptions (`provenanceRules` rejects each such Role; `cdifProvActivity` notes each full-URI status). The example follows validator.schema.org; the profile schema and shapes (metadataBuildingBlocks) need changing to accept it. The version before these corrections is [cdifprov-schemaorg/cdif\_provenance\_quantitative.before-schemaorg-validator.json](cdifprov-schemaorg/cdif_provenance_quantitative.before-schemaorg-validator.json).
* **The frame silently dropped content, so FrameAndValidate passed on a trimmed document (fixed 2026-11-10).** In `cdifProvenance-frame.jsonld` the activity sub-frames for `prov:used`, `schema:agent`, `schema:participant`, `schema:actionProcess` and `prov:wasAssociatedWith` named nested properties (`schema:instrument`, `schema:identifier`, `schema:contributor`, `schema:step`, ...). A JSON-LD sub-frame that names properties also *filters*: a value with none of them was left out, so plain `{@id}` inputs, Role agents and stepless procedures never reached the JSON Schema. Those sub-frames are now `@embed` only, and `prov:used` is `@once` (with `@always` the frame copied each earlier output into the next step's `prov:used`, where it matched no branch). Every example keeps its result and frames more of its source (this one: 319 → 424 of 424 triples; FeS2: 132 → 171 of 204). The remaining loss is `schema:result` descriptions, which FrameAndValidate collapses to `{@id}` (`REFERENCE\_ONLY\_KEYS`, validation repo).
* **Software in `prov:used` must be typed `prov:Entity`.** Framing visits `prov:used` before `bios:computationalTool` (properties are processed in IRI order), so the software is embedded first in `prov:used`, where the profile accepts an inline node only if it is a `prov:Entity`. It is typed `\["schema:SoftwareApplication", "prov:Entity"]`, as the Galaxy converter does.
* **Process Run Crate cannot describe a lab step.** See note 13. The validator also rejects `Z` in times (its pattern wants `+hh:mm`), so the crate uses `+00:00`, and it wants `actionStatus` as a string.
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
|activity type (1..\*)|`schema:additionalType` → CDIF `activityType` concepts (`at:sampling`, `at:instrumentCalibration`, `at:dataAcquisition`, `at:dataProcessing`, `at:deriving`, `at:analysing`, `at:qualityControl`)|
|activity description, identifier|`schema:description`; `schema:identifier` as a `PropertyValue` and as a string|
|ordered sequence of activities|the run's plan lists 7 `schema:step`s with `schema:position` (see note 23)|
|input (observation data, external information)|`prov:used` + `schema:object`; external inputs are the certified standards, the calibration curve and the acceptance criterion|
|output: description, file object, identifier linking to the next input|`schema:result` with `schema:description`, `schema:url`, `schema:encodingFormat`; the `@id` is what the next step's `prov:used` cites|
|procedure: description, protocol name and link, constants and assumptions, algorithm, sentinel values|`schema:actionProcess` (`HowTo`: name, description, url, steps); constants, detection limit and the treatment of values below it as activity `schema:additionalProperty`|
|tools: calibration, software, instrument|the calibration activity and its curve; `bios:computationalTool`; `schema:instrument`; `schema:tool`|
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

* **Qualified PROV-O is the most expressive serialization**, and the only one that keeps who and what played which part without inventing keys. Plain PROV-O and Process Run Crate lose exactly that.
* **cdifProv covers the Jules Verne features best** (person, status, procedure details, result about the sample, instrument as a typed thing), but its plan steps are not linked to the activities, there is no part-of, the tool role is weak, and the draft's quality and acquisition-mode provisions have no slot.
* **The overlays answer different questions and combine.** P-Plan or ProvONE adds the plan and wiring that every retrospective form lacks; SOSA adds what was measured (feature, sample, property, sensor) that none of the others can say. Each needs PROV for the rest.
* **DDI-CDI** is strong on structure (steps, sequence, information flow) and weak on the run (no times, roles or status). It needs review by someone who uses it before any conclusion.

