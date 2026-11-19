# Scenario: a laboratory measurement

The Dagstuhl quantitative scenario of [APPROACHES.md](APPROACHES.md), recorded in cdifProv the way
the later scenarios are and mapped from there. APPROACHES.md compares nine provenance approaches,
with the hand-written PROV-O Turtle as its master. This page covers only the cdifProv file, the
PROV-O generated from it, and the RO-Crate. [MAPPING.md](MAPPING.md) has the construct-by-construct
table.

## The story

The story is the one in [APPROACHES.md](APPROACHES.md#the-scenario): a river-water sample,
measured by absorbance, gives a validated concentration. In cdifProv it is two activities chained by
`@id` in `prov:wasGeneratedBy`:

1. **The sampling.** Its result is the water sample.
2. **The concentration determination run**, with the sample as its `schema:object`. Its
   `schema:actionProcess` is the procedure as performed: a HowTo whose `schema:isBasedOn` is the
   laboratory's plan. That HowTo has seven steps, each typed `[schema:HowToStep, schema:Action]`:
   1. instrument calibration;
   2. a first absorbance measurement, which failed;
   3. the absorbance measurement;
   4. blank correction;
   5. calibration-based derivation;
   6. uncertainty assessment;
   7. validation, whose result is the record's dataset.

The record:

- **Used resources:** each step names what it used:
  - instruments: the spectrophotometer, the cuvette and the analysis software;
  - reagents: the certified calibration standards and the colour reagent;
  - inputs (`schema:object`): the previous steps' outputs.
- **Plans:** four steps follow their own procedure, a HowTo whose `schema:isBasedOn` is the
  master's plan for that step: the absorbance procedure, the blank-correction, calibration and
  uncertainty specifications.
- **Agents:** every step has a role. The analyst's `schema:agent` is a `schema:Role` with a
  DataCite contributor type: data collector, researcher or supervisor. The laboratory is a
  participant in the measurement, as the hosting institution.
- **Failure:** the failed attempt has `schema:FailedActionStatus` and a `schema:error`.

## What changed from the earlier cdifProv file

The file was hand-written for the comparison in APPROACHES.md before the scenario conventions were
settled. It now follows them:

- **The steps are part of the run.** Before, the run and its seven activities were listed side by
  side in `prov:wasGeneratedBy`. The run's plan listed seven text steps, and each activity pointed
  to its step with P-Plan's `p:correspondsToStep`. Now the activities *are* the steps of the run's
  HowTo, so the `p:` term and the step list are gone.
  - **Gained:** that each step is part of the run, which cdifProv could not say before.
  - **Lost:** the two absorbance attempts no longer share one planned step; each is a step of what
    was performed.
- **The sampling is not part of the run**, as in the PROV-O master. The run now starts with the
  calibration, at 09:40 on 5 November, not at the sampling.
- **Instruments and reagents are not repeated in `schema:object`.** That holds only the inputs.
- **Plans are named, not described.** Each HowTo used to carry the plan's IRI as its `@id`. Now the
  HowTo is the procedure as performed, with its own `@id` and the plan in `schema:isBasedOn`. Its
  name, description, URL, times and cost stay on the HowTo.
- **Steps have no activity types.** A step's `schema:additionalType` is string-only, so the CDIF
  activity types that each activity had (`cdifact:Calibration`, `cdifact:Measurement`, and so on)
  would be literals there, and are left out. The run keeps `cdifact:Analysis` and the sampling
  `cdifact:Sampling`.
- **Added:** a `propertyID` on every parameter value, and a contact point for the analyst.

## Files

| approach | file | how it was made | checked with |
|---|---|---|---|
| **cdifProv** (master for this page) | [cdifprov-schemaorg/cdif\_provenance\_quantitative.json](cdifprov-schemaorg/cdif_provenance_quantitative.json), [run-rooted tree](cdifprov-schemaorg/cdif_provenance_quantitative.run-rooted.jsonld) | hand-written, then restructured as above | `FrameAndValidate.py -v` against cdifProvenance 2.0: passes; conformance consistent (provenance 2.0; not core 2.0, since the dataset has no identifier); 404 triples, all kept by framing; `provenanceRules.shacl` (advanced): conforms, no results; key counts = triple counts |
| **PROV-O, qualified** | [prov-o-qualified/cdif\_provenance\_quantitative.from-cdifprov.ttl](prov-o-qualified/cdif_provenance_quantitative.from-cdifprov.ttl), [.jsonld](prov-o-qualified/cdif_provenance_quantitative.from-cdifprov.jsonld) | generated: `python tools/cdifProvToProvO.py <cdifProv> <out.ttl>` | 431 triples: 9 activities (the 7 steps `dcterms:isPartOf` the run), 7 generations, 20 usages, 10 associations (5 with a plan), 2 `prov:atLocation`; the tree is isomorphic under rdflib and pyld |
| **PROV-O, plain** | [prov-o-unqualified/cdif\_provenance\_quantitative.from-cdifprov.ttl](prov-o-unqualified/cdif_provenance_quantitative.from-cdifprov.ttl), [.jsonld](prov-o-unqualified/cdif_provenance_quantitative.from-cdifprov.jsonld) | generated: the same with `--unqualified` | 315 triples; the plans and roles are lost; `--unqualify` of the qualified file gives the same graph; the tree is isomorphic |
| **RO-Crate 1.1** | [ro-crate/cdif\_provenance\_quantitative/ro-crate-metadata.json](ro-crate/cdif_provenance_quantitative/ro-crate-metadata.json), [tree](ro-crate/cdif_provenance_quantitative.jsonld) | written from the cdifProv file | 64 entities; 345 triples; the tree is isomorphic. `rocrate-validator` 0.14.0, `-p ro-crate-1.1 -m` (metadata only): every REQUIRED check passes; 6 RECOMMENDED checks fail, listed below |

The PROV-O files are named `.from-cdifprov` because the comparison's master,
[prov-o-qualified/cdif\_provenance\_quantitative.ttl](prov-o-qualified/cdif_provenance_quantitative.ttl),
and its plain form keep their names. The DDI-CDI, P-Plan, ProvONE and SOSA files are built on that
master, so it is unchanged.

**The crate** replaces the hand-written Process Run Crate, which failed a REQUIRED check: Process Run
Crate requires every action's instrument to be software, and the spectrophotometer is not. Like the
lab-protocol and field-sample crates, it is plain RO-Crate 1.1:

- the sampling and the run are `CreateAction`s, and each step is one entity typed
  `[HowToStep, CreateAction]`;
- the consumed reagents are each action's `object`, not its `instrument`;
- a Role agent becomes its agent, and its role is lost;
- the plans are `HowTo` entities with no properties;
- every node the cdifProv file holds in place is a separate entity, with an `@id` made from its
  parent's where it has none.

The 6 RECOMMENDED failures, none filled in with invented values:

- **The crate's `author` and `publisher`:** the cdifProv record names neither.
- **A `url`** for the laboratory and for the spectrophotometer's manufacturer.
- **A trailing `/` on the dataset's IRI:** RO-Crate recommends it for a `Dataset`. The IRI is kept.
- **The `example.org` dataset:** it is flagged as unavailable.

## The generated PROV-O against the master

**Only the master has these:**

- **Derivations.** Three qualified derivations (`prov:wasDerivedFrom`, with the activity that did
  the deriving): cdifProvenance has no derivation.
- **Consumption.** The reagent's `prov:qualifiedInvalidation` at 10:19: cdifProv cannot say that a
  reagent was used up.
- **The software as an agent.** The master has a `prov:SoftwareAgent` acting in the data steps. CDIF
  records software as a used `schema:instrument`, and the analyst as the responsible agent.
- **Acting on behalf of the laboratory** (`prov:actedOnBehalfOf`). cdifProv has the analyst's
  `schema:affiliation` instead, and names the laboratory as a participant of the measurement.
- **Types:** the Dagstuhl activity types on the steps (`ex:Processing`, `ex:Derivation`, …), and
  the entity types (`ex:SourceData`, `ex:DerivedQuantity`, …).
- **The procedure's documentation**, preparation and performance time and cost. In cdifProv they
  are on the HowTo, which has no PROV counterpart.

**Only the generated file has these:** the calibration and the failed attempt as activities, the
instrument's description (model, manufacturer, serial number, parts), and a role on every step's
association.

## Findings

- **A run's own result was generated twice.** The run lists the dataset as its `schema:result`, and
  so does its validation step. `tools/cdifProvToProvO.py` dropped the run's own generation in favour
  of the step's, but then gave the root a second generation by the run, as the last activity of the
  chain. It now does that only when the activity does not list the root as its result. The other
  scenarios' outputs are unchanged.
- **Role names kept their case.** A DataCite `termCode` such as `DataCollector` became
  `ex:Datacollector`; it is now `ex:DataCollector`.
- **"Step is part of the run" is now expressible in cdifProv**, through the step form; the matrix in
  APPROACHES.md changes from ✘ to ✔. The cost is that a planned step done twice is two steps.
- **A step cannot be typed.** As in the lab-protocol scenario, a step's `schema:additionalType` is
  a string, so the steps lose the activity types that the separate activities had.
