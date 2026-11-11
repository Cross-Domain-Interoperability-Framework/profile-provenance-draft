# Coverage workbook vs draft profile: requirements comparison

2026-11-11. This compares two documents:

- **The workbook:** `cdif_provenance_coverage.xlsx`, from the 2026 Dagstuhl week, "03 Provenance/Outputs". Its Coverage sheet has 38 rows. It checks each provenance element against what CDIF Core and Discovery already provide, and proposes a status for the provenance profile.
- **The draft:** [`CDIF prov profile - draft.docx`](CDIF%20prov%20profile%20-%20draft.docx), dated 2026-01-30. It sets out competency questions and a content model with cardinalities.

It also checks both against the implementation agreed in
[PROPOSAL_2026-11-11_activity_used_resources.md](PROPOSAL_2026-11-11_activity_used_resources.md).

In the workbook only row A8 has decision state *Agreed*. The other 37 are *Not yet set*, so its statuses are proposals.

## Agreement

Each of these is a Gap or Partial in the workbook and an explicit requirement in the draft:

| topic | workbook | draft |
|---|---|---|
| agents and their role in each activity | A2, A8 | "identify the agents involved in the activity; include the role"; actor and role |
| instruments: make, model, identifier, configuration, parts | G1 | instruments section |
| software and version | G9, P4 | software name, version, identifier |
| protocols and SOPs | G8 | procedure: protocol name and identifier |
| calibrations | G6 | procedures: calibrations and configuration; question about standard materials |
| activities with inputs and outputs, in sequence | P2, P3 | workflow as an ordered sequence of activities, with input and output |
| adjustments, aggregation, anomalous values | P7 | competency question 28 |
| quality | P6, S6 | quality metric definition and result |

## In the draft, not in the workbook

The workbook has no row for any of these:

- Purpose of, or reasons for, the data collection. This is in the draft's content model. The draft says Discovery covers purpose, but the workbook does not check that.
- Mode of acquisition (1..\*): instrument, human observation, analysis of existing data, or survey mode.
- Activity type (1..\*, from a controlled vocabulary). It appears only in passing in P2 and G8.
- A free-text provenance description for people.
- Agents' qualifications and training.
- Constants and assumptions, algorithm references, and the treatment of sentinel values. S7 only marks missing-value conventions as *Verify*.
- Factors that might affect data quality.
- Dependencies between variables (competency question 27).
- The comparability and integration questions (22–26).
- Paradata, background knowledge, and the requirement for shared vocabularies.

## In the workbook, not in the draft's content model

- **Activity timestamps (A6).** The draft's activity has no time at all. This is the largest omission: the workbook calls an activity timestamp necessary.
- **Version lineage and supersession (A5, L2).**
- **Instrument-to-variable association (G5).** The draft only raises it as a question, in item 18 and in "mechanism for attaching metadata properties … to the components".
- **Sampling design (G7).** The draft has only the object of study.
- **Data processing level (P5).** The workbook proposes *Out of scope*.
- **Rights, ethics and permits, citation, checksum, format** (rows R and S). These are mostly already covered by Core, or out of scope.

## Cardinality conflicts

| element | draft | workbook | current implementation |
|---|---|---|---|
| actor per activity | **1..\*** (required) | Recommended (A8, Agreed) | optional |
| activity type | **1..\*** (required) | no row | optional (`schema:additionalType`) |
| output per activity | **1..\*** (required) | no row | optional (`schema:result`) |
| mode of acquisition | **1..\*** (required) | no row | not modelled |
| what the activity used | input 0..\* | no row | at least one of `schema:instrument`, `schema:object`, `schema:actionProcess` |
| procedure | 0..1; a description is required if it is not a defined protocol | Gap (G8) | `schema:actionProcess` (the `{@id}` form is the plan) |

The draft requires three things that neither the workbook nor the current schema requires: actor, activity type and output. The rule the implementation does require, at least one of `schema:instrument`, `schema:object` or `schema:actionProcess`, is not a stated requirement in either document.

## Workbook schema.org mappings to update for the current model

| row | workbook mapping | current model |
|---|---|---|
| G1 | `wasGeneratedBy…prov:used…schema:instrument` / `bios:computationalTool` (the retired role wrapper) | `wasGeneratedBy.schema:instrument`, with a Wikidata kind term in `schema:additionalType` (instrument Q3099911, software Q7397, reagent Q2356542) |
| G2 | `prov:wasGeneratedBy..prov:used..prov:Plan` | `schema:actionProcess` `{@id}`; when the activity also has an inline procedure, the HowTo's `schema:isBasedOn` |
| A6 | `schema:Activity.schema:endDate` | `schema:endTime` on the Action. schema.org has no Activity class, and `endDate` is defined on Event and CreativeWork |
| A8 | `…schema:step…schema:agent` | `schema:agent` / `schema:participant` on the activity, with `schema:Role` for the role, not on a HowTo step |
| P2, P3, P6, P7 | `schema:actionProcess.schema:step` | Executed steps are separate `prov:wasGeneratedBy` activities, chained output to input with `schema:result` → `schema:object`, each linked to its plan step with `p:correspondsToStep`. HowTo steps describe the plan. The workbook mixes up the two. |
| G5 | `variableMeasured.PropertyValue.measurementTechnique` | Does not link an instrument to a variable. Still a gap in the implementation. |

## Actions

- **Draft:** add activity timestamps.
- **For the team to settle:**
  - Should actor, activity type and output be required, as the draft has them?
  - Should the implementation's at-least-one-of rule be stated as a requirement?
- **Workbook:**
  - Add rows for purpose, mode of acquisition and activity type.
  - Rewrite the schema.org mapping column for G1, G2, A6, A8 and P2–P7 to match the current model.
