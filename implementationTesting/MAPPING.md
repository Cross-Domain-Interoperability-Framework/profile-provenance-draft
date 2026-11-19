# cdifProv to PROV-O and RO-Crate: the mapping

How each cdifProvenance construct is written in PROV-O with qualified relations, in PROV-O with
plain relations, and in an RO-Crate: a Provenance Run Crate 0.5 for a workflow, a Process Run Crate 0.5
for one software run, and plain RO-Crate 1.1 for a laboratory process. The PROV-O columns are what
[`tools/cdifProvToProvO.py`](../tools/cdifProvToProvO.py) does; the RO-Crate column is how the
scenario crates are written. The table grows as each scenario adds constructs; the last column
names the first scenario that uses each row. A scenario in parentheses is planned: the tool
handles the row, but no scenario file exercises it yet, so its RO-Crate column is provisional.

A cdifProv record describes one resource (the root `schema:Dataset`) and the activity that
generated it, in `prov:wasGeneratedBy`. The activity names the entities it drew on (`schema:object`)
and what it used to do so (`schema:instrument`); the steps of its procedure name the same entities
as their inputs.

| cdifProv | PROV-O, qualified | PROV-O, plain | RO-Crate | scenario |
|---|---|---|---|---|
| root `schema:Dataset` | `prov:Entity` | `prov:Entity` | a `Dataset` data entity with the same IRI, in the root's `hasPart`; the crate's root `./` is the crate, not the dataset | workflow, minimal |
| root `prov:wasGeneratedBy` activity | `prov:qualifiedGeneration [prov:activity; prov:atTime` = activity end`]` | `prov:wasGeneratedBy` + `prov:generatedAtTime` | `CreateAction` in the root's `mentions`; the dataset is in its `result` | workflow, minimal |
| several root `prov:wasGeneratedBy` activities, chained (one's `schema:result` is a later one's `schema:object`) | each a `prov:Activity`; only the last (whose results no listed activity takes as input) generates the root | same | each a `CreateAction` in the root's `mentions`; the dataset is the last one's `result` | field sample |
| root `schema:subjectOf` catalog record | copied (no PROV term) | copied | `ro-crate-metadata.json` descriptor (not the same thing: it describes the crate file) | workflow |
| activity `[prov:Activity, schema:Action]` | `prov:Activity` | `prov:Activity` | `CreateAction` | workflow |
| `schema:additionalType` (activity vocabulary IRI) | `rdf:type` | `rdf:type` | `additionalType` (lab protocol); the workflow crate leaves it out | workflow, lab protocol |
| `schema:startTime`, `schema:endTime` | `prov:startedAtTime`, `prov:endedAtTime`; a date with no time becomes midnight of that date | same | `startTime`, `endTime`, with milliseconds at most and a `+HH:MM` offset (not `Z`) | workflow, field sample |
| `schema:location` (a `schema:Place`, with `schema:geo`) | `prov:atLocation`; the place is also a `prov:Location`, and keeps its name and coordinates | same | `location`, a `Place` entity with a `GeoCoordinates` entity | field sample |
| `schema:actionStatus` | copied, as an IRI (no PROV term) | copied | `actionStatus` | workflow |
| `schema:FailedActionStatus` with `schema:error` | both copied (PROV has no failed activity); the failed step is an activity like any other | copied | `actionStatus` and `error` on the step's `CreateAction` | lab measurement |
| `schema:agent` (Person) | `prov:qualifiedAssociation [prov:agent]`; the agent is a `prov:Person` | `prov:wasAssociatedWith` | `agent` | workflow |
| `schema:agent` (Organization) | the same; the agent is a `prov:Organization` | `prov:wasAssociatedWith` | `agent` | lab protocol, field sample |
| `schema:agent` as `schema:Role` | the Role's agent in `prov:agent`, its `roleName` in `prov:hadRole` (an IRI as it is; a `DefinedTerm`'s `termCode` or a string becomes an `ex:` role) | `prov:wasAssociatedWith` (role lost) | `agent`, the Role's agent; the role is lost (RO-Crate 1.1 has no Role pattern) | lab measurement |
| `schema:participant` as `schema:Role` | a second `prov:qualifiedAssociation` with that role and no plan | `prov:wasAssociatedWith` | `participant`, the Role's agent; the role is lost | lab measurement |
| plan: HowTo `schema:isBasedOn` | `prov:hadPlan` on the agent's association; a `prov:Plan` | lost | the workflow: `instrument` of the run's `CreateAction`, and the root's `mainEntity` | workflow |
| plan: an `{@id}` `schema:actionProcess` | `prov:hadPlan` on the agent's association; a `prov:Plan` with no other statements | lost | `actionProcess` on the `CreateAction`, a term the crate's `@context` adds (it is not in the RO-Crate 1.1 context); the plan is a contextual `HowTo` | minimal |
| inline `schema:actionProcess` HowTo | no counterpart (its name and description are lost, and so are a procedure's `url`, `prepTime`, `performTime` and `estimatedCost`) | none | the workflow `ComputationalWorkflow`, also typed `HowTo` (workflow); a `HowTo` entity, the run's `actionProcess`, with `isBasedOn` the plan (lab protocol) | workflow, lab protocol |
| HowTo step `[schema:HowToStep, schema:Action]` | `prov:Activity` + `dcterms:isPartOf` the activity; `schema:position` copied | same | workflow: a `HowToStep` of the workflow (`position`, `workExample` → its tool), a `ControlAction` (instrument → the step, object → the step's run) and a `CreateAction` (the step's run). Lab protocol: one entity typed `[HowToStep, CreateAction]` | workflow, lab protocol |
| a step's own `schema:actionProcess` HowTo (a sub-procedure) | its `schema:isBasedOn` is the step's `prov:hadPlan`; the HowTo itself has no counterpart. A step with no agent of its own is associated with its activity's agent | none (the plan is lost) | a `HowTo` entity, the step's `actionProcess` | lab protocol |
| text-only `schema:HowToStep` (no `schema:Action`) | lost | lost | a `HowToStep` in its HowTo's `step` | lab protocol |
| `schema:object` (an input) | `prov:qualifiedUsage [prov:entity; prov:hadRole ex:InputData]` | `prov:used` | `object` | workflow |
| `schema:object` that is a sampled feature (a `schema:Place`) | the same usage; nothing says the result is a sample of it | `prov:used` | `object`, a `Place` entity | field sample |
| `schema:instrument`, software kind (Q7397) | `prov:qualifiedUsage [prov:hadRole ex:Software]`; the tool is a `prov:Entity`, not an agent (CDIF: software that runs a step is used, not responsible) | `prov:used` | `instrument`; the tool is a `SoftwareApplication`, in the workflow's `hasPart` | workflow |
| `schema:instrument`, instrument kind (Q3099911) | `prov:qualifiedUsage [prov:hadRole ex:Instrument]` | `prov:used` | `instrument`, a `Product`; the crate is plain RO-Crate 1.1, because Process Run Crate requires a software instrument | lab protocol |
| `schema:instrument`, reagent kind (Q2356542) | `prov:qualifiedUsage [prov:hadRole ex:Reagent]` | `prov:used` | `object` (consumed) | lab protocol |
| the run's engine (`schema:instrument` of the run) | `prov:qualifiedUsage [prov:hadRole ex:Software]` | `prov:used` | `instrument` of an `OrganizeAction` whose `result` is the run | workflow |
| `schema:result` of a step | `prov:qualifiedGeneration [prov:activity` = step; `prov:atTime` = step end`]` | `prov:wasGeneratedBy` + `prov:generatedAtTime` | `result` of the step's `CreateAction` | workflow |
| `schema:result` of the activity, when a step produced it | dropped: the step's generation stands (an entity has one generation) and the step is part of the activity | same | `result` of the run's `CreateAction` | workflow |
| `schema:additionalProperty` (a parameter value) | copied, as a `schema:PropertyValue` (PROV has no parameters) | copied | a `PropertyValue` in the step `CreateAction`'s `object`; its `propertyID` names the protocol's formal parameter where there is one (lab protocol) | workflow, lab protocol |
| names, descriptions, versions, identifiers, `encodingFormat` | copied | copied | the same schema.org terms | workflow |

## What each form cannot say

- **cdifProv:** a plan's own content. `schema:isBasedOn` is a reference only, so a protocol's
  equipment, formal parameters and sub-protocols can be named but not described. Derivation:
  there is no `prov:wasDerivedFrom`, so that a dataset comes from a sample follows only from a chain
  of inputs and outputs.
- **PROV-O, qualified:** the procedure as performed (the HowTo) as a thing in its own right, at any
  level; text-only steps; step order (kept only as the `schema:position` annotation); parameters
  and status (annotations).
- **PROV-O, plain:** in addition, every role and the plan: `prov:hadPlan` and `prov:hadRole` live
  only on qualification nodes.
- **RO-Crate:** roles on agents; a plan for a run that is not a workflow, except through a term
  added to the context; a laboratory process in a run-crate profile, since Process Run Crate requires
  software instruments. For a workflow, Provenance Run Crate separates the plan (the workflow and its
  steps) from the execution (the actions) more fully than cdifProv: a step is both a `HowToStep` of
  the workflow and a `CreateAction`, joined by a `ControlAction`.
