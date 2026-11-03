# CDIF Provenance Options

**Date:** 2026-10-25
**Status:** Draft for review.  October 2026 Update: Building Blocks, External Profiles and PROV-JSONLD
**Based on:** [ProvenanceOptions.md](ProvenanceOptions.md) (2026-03-11), which is left unchanged. This document carries that comparison forward. The changes are listed in [§15](#15-changes-from-provenanceoptionsmd).

## 1\. Overview

CDIF provides multiple building blocks for describing the activities that produce datasets. All follow the W3C PROV pattern: `Dataset --prov:wasGeneratedBy--> Activity`. Each building block uses a different primary vocabulary while describing the same provenance concepts: what was done, who did it, what was used, what was produced, and how it was done.

In addition to the native CDIF building blocks, the research community has developed RO-Crate-based provenance profiles — particularly the **Workflow Run RO-Crate (WRROC)** family and the **ARC Workflow Run RO-Crate** profile — that describe computational and laboratory workflows. This document compares all approaches and discusses how WRROC and ARC provenance can be integrated into CDIF. It also covers the 2024 W3C Member Submission **PROV-JSONLD** ([§13](#13-prov-jsonld-w3c-member-submission-2024)), and how a domain profile, the ADA geochemistry profile in geochemBuildingBlocks, builds on cdifProvActivity ([§12](#12-a-domain-profile-built-on-cdifprovactivity-geochemistry-ada)).  Note that cdifProvActivity is a draft proposal for consideration and review, but was needed for the ADA geochemistry and XAS profile work.

### CDIF Building Blocks

|Building Block|Primary Vocabulary|Activity Type|Location|
|-|-|-|-|
|**cdifProvActivity**|schema.org + PROV-O|`\["schema:Action", "prov:Activity"]`|[cdifDataType/cdifProvActivity](https://github.com/Cross-Domain-Interoperability-Framework/metadataBuildingBlocks/tree/main/_sources/cdifDataType/cdifProvActivity)|
|**provActivity**|W3C PROV-O|`\["prov:Activity"]`|[provProperties/provActivity](https://github.com/Cross-Domain-Interoperability-Framework/metadataBuildingBlocks/tree/main/_sources/provProperties/provActivity)|
|**ddicdiActivity** *(archived)*|DDI-CDI 1.0|`cdi:Activity`|[archive/ddiProperties/ddicdiActivity](https://github.com/Cross-Domain-Interoperability-Framework/metadataBuildingBlocks/tree/main/archive/ddiProperties/ddicdiActivity)|

On 2026-10-05 the whole `ddiProperties` tree in metadataBuildingBlocks was moved to `archive/` as "reference-only, referenced by nothing active" (commit `aec9bcca81`). ddicdiActivity is kept in this comparison because DDI-CDI is an important model to consider.

### External Provenance Profiles and Serializations

|Profile|Vocabulary|Activity Type|Specification|
|-|-|-|-|
|**Process Run Crate**|schema.org|`schema:CreateAction`|[w3id.org/ro/wfrun/process/0.5](https://w3id.org/ro/wfrun/process/0.5)|
|**Workflow Run Crate**|schema.org|`schema:CreateAction` + `schema:OrganizeAction`|[w3id.org/ro/wfrun/workflow/0.5](https://w3id.org/ro/wfrun/workflow/0.5)|
|**Provenance Run Crate**|schema.org + CWLProv|`schema:CreateAction` + `schema:OrganizeAction`|[w3id.org/ro/wfrun/provenance/0.1](https://w3id.org/ro/wfrun/provenance/0.1)|
|**ARC WR RO-Crate**|schema.org + Bioschemas|`schema:CreateAction` + `LabProcess`|[nfdi4plants/arc-wr-ro-crate-profile](https://github.com/nfdi4plants/arc-wr-ro-crate-profile)|
|**PROV-JSONLD** *(W3C Member Submission, 2024)*|PROV-DM / PROV-O|`Activity` (qualified relations as their own objects)|[SUBM-prov-jsonld-20240825](https://www.w3.org/submissions/2024/SUBM-prov-jsonld-20240825/)|

PROV-JSONLD is not an application profile like the RO-Crate profiles. It is a JSON-LD *serialization of the PROV data model itself*, so it is compared separately in [§13](#13-prov-jsonld-w3c-member-submission-2024).

[Activity Streams 2.0](https://www.w3.org/TR/activitystreams-core/) is another activity vocabulary, noted here for completeness; it is not otherwise compared.

### Links to Schemas and Examples

|Building Block|Resolved Schema|Example Instance|
|-|-|-|
|cdifProvActivity|[resolvedSchema.json](https://github.com/Cross-Domain-Interoperability-Framework/metadataBuildingBlocks/blob/main/_sources/cdifDataType/cdifProvActivity/resolvedSchema.json)|[exampleCdifProvActivity.json](https://github.com/Cross-Domain-Interoperability-Framework/metadataBuildingBlocks/blob/main/_sources/cdifDataType/cdifProvActivity/exampleCdifProvActivity.json)|
|provActivity|[provActivitySchema.json](https://github.com/Cross-Domain-Interoperability-Framework/metadataBuildingBlocks/blob/main/_sources/provProperties/provActivity/provActivitySchema.json)|[exampleProvActivity.json](https://github.com/Cross-Domain-Interoperability-Framework/metadataBuildingBlocks/blob/main/_sources/provProperties/provActivity/exampleProvActivity.json)|
|ddicdiActivity *(archived)*|[ddicdiActivitySchema.json](https://github.com/Cross-Domain-Interoperability-Framework/metadataBuildingBlocks/blob/main/archive/ddiProperties/ddicdiActivity/ddicdiActivitySchema.json)|[exampleDdicdiActivity.json](https://github.com/Cross-Domain-Interoperability-Framework/metadataBuildingBlocks/blob/main/archive/ddiProperties/ddicdiActivity/exampleDdicdiActivity.json)|
|PROV-JSONLD|[schema.json](https://openprovenance.org/prov-jsonld/schema.json) (JSON Schema draft-07)|[context.jsonld](https://openprovenance.org/prov-jsonld/context.jsonld)|

WRROC conversion examples (Galaxy workflow RO-Crates from [Zenodo record 13842780](https://zenodo.org/records/13842780) and Bennu py-GC-MS analytical workflow) are available in the [prov-context-quality/Examples](./examples/) folder.

## 2\. CDIF Building Block Design

### cdifProvActivity — Schema.org-first with PROV-O linkage

The cdifProvActivity building block is the current draft CDIF implementation. It follows the approach developed by the [ODIS Architecture](https://github.com/iodepo/odis-arch/blob/414-update-provenance-recommendations/book/thematics/provenance/common-provenance-cases.md) provenance recommendations, mapping schema.org `Action` to `prov:Activity` and using schema.org properties to describe provenance in a vocabulary already familiar to web developers and search engines.

Activity nodes carry dual types `\["schema:Action", "prov:Activity"]` so that:

* Schema.org-aware consumers (search engines, web crawlers) see a well-typed `Action`
* PROV-aware consumers (provenance trackers, RDF reasoners) see a `prov:Activity`
* The `prov:used` property provides backward-compatible input listing

Key properties: `schema:agent`, `schema:participant`, `schema:object` (inputs), `schema:result` (outputs), `prov:used` (what was used, including instruments; see below), `schema:actionProcess` → `schema:HowTo` (methodology), `schema:additionalProperty` (parameters), `schema:startTime`, `schema:endTime`, `schema:location`, `schema:actionStatus`, `schema:error`.

**How `prov:used` items are shaped (2026-08 to 2026-10).** The base `generatedBy` block admits five kinds of `prov:used` item:

1. a string (URI or free-text reference);
2. an `{@id}` reference, which is the sealed [objectReference](https://github.com/Cross-Domain-Interoperability-Framework/metadataBuildingBlocks/tree/main/_sources/cdifDataType/objectReference) building block (`additionalProperties: false`, `required: \['@id']`);
3. an inline entity whose `@type` array includes `prov:Entity`;
4. a **role-keyed wrapper** under one of three recognized role names: `schema:instrument`, `bios:computationalTool` or `bios:reagent` (`prov:reagent` until 2026-10-25; see [§14](#14-open-issues) item 1);
5. *(since 2026-10-22, metadataBuildingBlocks #52)* a role-keyed wrapper under **any** prefixed role name, admitted by shape rather than by name.

The wrapper names the role through the property key, e.g. `"prov:used": \[{"schema:instrument": \[ {…Instrument…} ]}]`. cdifProvActivity then *pins* the `schema:instrument` wrapper's value to an array of its Instrument definition, using a constraint-only `if/then`. It deliberately does not narrow the base `anyOf`, because an `allOf` intersection with a narrowed `anyOf` would silently exclude the other base shapes. Domain profiles are expected to **close** the set of role names they accept (see [§12](#12-a-domain-profile-built-on-cdifprovactivity-geochemistry-ada)).

cdifProvActivity itself has no activity-level `schema:instrument` property; instruments are reached through the `prov:used` wrapper. All 0..*/1..* properties are JSON arrays, and `@type` is always an array, including on inline `schema:Thing` objects (2026-10-03).

The RDF consequence of the wrapper is discussed in [§13.3](#133-what-the-comparison-shows-about-cdif).

### provActivity — PROV-O-first with schema.org fallbacks

Prioritizes W3C PROV-O vocabulary, using native PROV-O properties where they exist (`prov:wasAssociatedWith`, `prov:generated`, `prov:startedAtTime`, `prov:wasInformedBy`) and falling back to schema.org for concepts PROV-O does not cover (name, description, instrument, methodology, status). Appropriate for communities invested in PROV-O tooling or where formal provenance reasoning is needed.

### ddicdiActivity — DDI-CDI native workflow description 

Uses the [DDI-CDI 1.0](https://ddialliance.org/Specification/DDI-CDI/1.0/) vocabulary natively, generated from the DDI-CDI Enterprise Architect UML model with all structured data types resolved. Designed for communities using DDI-CDI for statistical and survey data, with detailed workflow modeling capabilities (Steps, Parameters, data flow between steps). Includes `cdi:definition` (InternationalString), `cdi:start`/`cdi:end` (timestamps), and `cdi:hasInternal` (ControlLogic) properties not present in the earlier ddicdiProv building block. Companion building blocks `ddicdiAgent` (Individual, Machine, Organization, ProcessingAgent) and `ddicdiValueDomain` (SubstantiveValueDomain, SentinelValueDomain) cover related DDI-CDI classes.

## 3\. Workflow Run RO-Crate (WRROC) Profiles

The [Workflow Run RO-Crate](https://www.researchobject.org/workflow-run-crate/) specification defines three profile levels for capturing retrospective provenance of computational and analytical workflows. All build on the [RO-Crate 1.1](https://w3id.org/ro/crate/1.1) packaging standard and use schema.org as the primary vocabulary.

### 3.1 Profile Hierarchy

**Process Run Crate** (`https://w3id.org/ro/wfrun/process/0.5`)
The minimal level. Captures a single tool execution as a `schema:CreateAction` with:

* `object`: input files (File/MediaObject)
* `result`: output files
* `instrument`: the SoftwareApplication that was run
* `agent`: the Person who ran it
* `actionStatus`: CompletedActionStatus, FailedActionStatus, etc.
* `startTime`, `endTime`: execution timestamps
* `error`: error message if the action failed

**Workflow Run Crate** (`https://w3id.org/ro/wfrun/workflow/0.5`)
Extends Process Run Crate for multi-step workflows. Adds:

* `schema:OrganizeAction`: a top-level action orchestrating sub-actions (linked from `instrument` pointing to a `ComputationalWorkflow`)
* `schema:CreateAction` per workflow step (linked via `instrument` pointing to a `HowToStep`)
* `ComputationalWorkflow` entity with `input`/`output` arrays of `FormalParameter`, `programmingLanguage`, `hasPart` (sub-steps)
* `FormalParameter` entities describing expected inputs/outputs with types, format constraints, default values

**Provenance Run Crate** (`https://w3id.org/ro/wfrun/provenance/0.1`)
Extends Workflow Run Crate with CWLProv-style detailed provenance:

* `schema:ControlAction` for workflow engine orchestration
* Per-step resource usage, container images, environment details
* Connections between step inputs/outputs via `exampleOfWork` references to FormalParameters

### 3.2 WRROC's Relationship to CDIF

WRROC is designed for **retrospective provenance** — describing what actually happened when a workflow was executed. This aligns directly with CDIF's purpose: documenting how a dataset was generated. However, WRROC also captures **prospective provenance** (workflow definitions, FormalParameters) which serves as valuable context.

Key alignment points:

* Both use schema.org as the primary vocabulary
* Both describe activities with inputs, outputs, agents, and instruments
* Both support multi-step activity chains
* Both capture temporal bounds and completion status

Key differences:

* WRROC uses `schema:CreateAction` (no PROV-O dual typing); cdifProvActivity uses `\["schema:Action", "prov:Activity"]`
* WRROC uses `schema:object`/`schema:result` for action I/O; cdifProvActivity uses `prov:used` for inputs (inherited from the `generatedBy` base building block), with `schema:object` for inputs and  `schema:result` for outputs
* WRROC uses `schema:instrument` at the action level for the tool/workflow; cdifProvActivity places instruments in a role-keyed `prov:used` wrapper (`{"schema:instrument": \[...]}`)
* WRROC defines methodology implicitly through the workflow structure; cdifProvActivity uses explicit `schema:actionProcess` → `schema:HowTo` for methodology

## 4\. ARC Workflow Run RO-Crate Profile

The [ARC (Annotated Research Context) Workflow Run RO-Crate profile](https://github.com/nfdi4plants/arc-wr-ro-crate-profile) extends WRROC for laboratory analytical workflows. Developed by [DataPLANT/nfdi4plants](https://nfdi4plants.org/), it adds [Bioschemas](https://bioschemas.org/) types to capture the structured, parameterized nature of lab processes.

### 4.1 Key Additions Over Standard WRROC

|Concept|Standard WRROC|ARC Profile|
|-|-|-|
|Activity type|`CreateAction`|`CreateAction` + `LabProcess`|
|Methodology|`ComputationalWorkflow`|`ComputationalWorkflow` + `LabProtocol`|
|Process parameters|Not captured|`parameterValue` → `PropertyValue` array|
|Lab equipment|`instrument` (generic)|`labEquipment` on LabProtocol|
|Samples|`File`/`MediaObject`|`Sample` (Bioschemas type)|
|Protocol execution|`instrument` → workflow|`executesLabProtocol` → `LabProtocol`|
|Instrument detail|`SoftwareApplication`|`DefinedTerm` (physical instruments)|

### 4.2 ARC Entity Types

**LabProcess** (extends `CreateAction`)
A lab process execution. Carries `executesLabProtocol` pointing to the protocol followed, and `parameterValue` arrays with the actual measurement parameters used (temperature, pressure, flow rate, etc.).

**LabProtocol** (extends `CreativeWork`)
Describes how a lab process should be carried out. Contains:

* `labEquipment`: instruments and equipment used (DefinedTerm references)
* `intendedUse`: purpose description
* `measurementMethod`: analytical method
* `input`/`output`: expected parameters (FormalParameter references)

**Sample** (Bioschemas type)
Represents physical samples with `additionalProperty` for sample-specific metadata (mass, preparation method, container type).

**DefinedTerm** (for instruments)
Physical lab equipment described with name, description, identifier, and URL. Unlike `SoftwareApplication` used for computational tools, `DefinedTerm` captures instruments that don't have software versions.

**PropertyValue** (via `parameterValue`)
Actual parameter values used during execution: temperature (600°C), ramp rate (10°C/ms), scan range (m/z 50–500), column dimensions, etc. Each PropertyValue has `value`, `unitText`, and optionally `propertyID` linking to a controlled vocabulary term.

### 4.3 Bennu py-GC-MS Example

The [Bennu-py-GC-MSarc](./examples/ROCRATE/Bennu-py-GC-MSarc-ro-crate-metadata.json) example demonstrates the ARC profile for a multi-step analytical workflow: pyrolysis-GC-MS/MS analysis of asteroid sample OREX-803003-0 from the OSIRIS-REx mission. The workflow chains five activities:

1. **Sample Preparation** → quartz tube loading, mass measurement
2. **Flash Pyrolysis** → 600°C at 10°C/ms ramp rate, He carrier gas
3. **GC Separation** → Rtx-5ms column, temperature program 35°C→310°C
4. **MS Detection (Full Scan)** → m/z 50–500, EI positive mode
5. **MS Detection (MRM/SRM)** → 38 targeted compounds, timed transitions

Each step carries rich `parameterValue` arrays with actual instrument settings. Equipment (`DefinedTerm` entities: pyrolysis oven, gas chromatograph, TSQ triple-quad mass spectrometer) is declared on the protocol and referenced by steps.

The [converted cdifProvActivity output](./examples/Bennu-py-GC-MSarc.cdifprov.json) demonstrates how all ARC concepts map cleanly to cdifProvActivity vocabulary.

## 5\. Mapping WRROC/ARC to cdifProvActivity

A converter tool ([tools/WRROCToCdifProv.py](tools/WRROCToCdifProv.py) in this repository; also in the [packaging](https://github.com/Cross-Domain-Interoperability-Framework/packaging/tree/main/tools) repository) transforms WRROC and ARC RO-Crate files into cdifProvActivity-compatible `@graph` documents. Two Galaxy-specific converters, [tools/galaxyROCrateToCDIF.py](tools/galaxyROCrateToCDIF.py) and [tools/galaxyROCrateToCDIFActions.py](tools/galaxyROCrateToCDIFActions.py), produce the HowTo/step form and the one-Action-per-step form respectively ([§6](#6-representing-multi-step-provenance)).

### 5.1 Property Mapping

|WRROC / ARC|cdifProvActivity|Notes|
|-|-|-|
|`@type: CreateAction`|`@type: \["schema:Action", "prov:Activity"]`|Original type preserved in `schema:additionalType`|
|`@type: LabProcess`|`schema:additionalType: \["schema:LabProcess"]`|ARC-specific action subtype|
|`@type: OrganizeAction`|not a generator; recorded as a `bios:computationalTool` role entry on the workflow execution|Corrected 2026-10-01: the Galaxy engine run is never the root's `mentions` and has no `object` or `result`, so it does not belong in `prov:wasGeneratedBy`|
|`object` (inputs)|`prov:used`|cdifProvActivity inherits `prov:used` from base|
|`result` (outputs)|`schema:result`|Direct mapping|
|`instrument` (tool)|`schema:instrument` on the activity, or `schema:actionProcess`|Depends on type — workflows become actionProcess. See §5.4 on the placement difference from the role-keyed wrapper|
|`agent`|`schema:agent`|Direct mapping (Person, Organization)|
|`startTime` / `endTime`|`schema:startTime` / `schema:endTime`|Direct mapping|
|`actionStatus`|`schema:actionStatus`|Normalized to prefixed form|
|`error`|`schema:error`|Direct mapping|
|`executesLabProtocol`|`schema:actionProcess`|Protocol → HowTo methodology; the converter also keeps `bios:executesLabProtocol`|
|`parameterValue`|`schema:additionalProperty`|PropertyValue objects preserved; the converter also keeps `bios:parameterValue`|
|`labEquipment`|`schema:instrument` (on actionProcess node)|Equipment on protocol, not action|
|`ComputationalWorkflow`|`schema:SoftwareApplication`|With additionalType preserving original|
|`LabProtocol`|`schema:HowTo`|Methodology description|
|`FormalParameter`|`schema:MediaObject`|With `additionalType: \["schema:FormalParameter"]`|
|`Sample`|`schema:Thing`|With `additionalType: \["bios:Sample"]`|
|`DefinedTerm` (instrument)|`\["schema:Thing", "schema:DefinedTerm"]`|Physical instrument description|

### 5.2 Structural Transformation

The converter produces a `@graph` array where each execution action (CreateAction, OrganizeAction, LabProcess) becomes a top-level node. All referenced entities — instruments, files, parameters, samples, agents — are inlined at their first occurrence within an activity node. Subsequent references use `{"@id": "..."}` only.

```
RO-Crate flat @graph:          cdifProvActivity nested @graph:
  CreateAction₁                  Activity₁
  CreateAction₂                    +-- prov:used \[inline entities]
  OrganizeAction                   +-- schema:result \[inline entities]
  ComputationalWorkflow            +-- schema:actionProcess \[inline workflow]
  FormalParameter₁                 +-- schema:agent \[inline person]
  FormalParameter₂                 +-- schema:additionalProperty \[params]
  SoftwareApplication            Activity₂
  Person                           +-- prov:used \[inline or @id refs]
  File₁ ... FileN                  +-- ...
```

### 5.3 What Maps Cleanly

* **Activities**: CreateAction, OrganizeAction, and LabProcess all map naturally to cdifProvActivity's dual-typed `\["schema:Action", "prov:Activity"]` pattern. The original action subtype is preserved in `schema:additionalType`.
* **Temporal bounds**: `startTime`/`endTime` are direct mappings.
* **Agents**: Person and Organization inline directly as `schema:agent`.
* **Action status**: Maps directly with URI normalization.
* **Parameter values**: ARC's `parameterValue` PropertyValue arrays map cleanly to `schema:additionalProperty`, preserving value, unitText, and propertyID.
* **Lab protocols**: `executesLabProtocol` → `schema:actionProcess` is a natural fit, as both describe the methodology an activity follows.
* **Lab equipment**: `labEquipment` on protocols maps to `schema:instrument` on the methodology node.
* **Samples**: Bioschemas `Sample` maps to `schema:Thing` with `schema:additionalType`.

### 5.4 What Requires Interpretation

* **FormalParameter → MediaObject**: WRROC's `FormalParameter` (which describes expected I/O slots) has no direct schema.org equivalent. Since `schema:object`/`prov:used` and `schema:result` expect `schema:CreativeWork` or similar, and most FormalParameters describe file-like entities, `schema:MediaObject` with `additionalType: \["schema:FormalParameter"]` is used.
* **Instrument placement**: WRROC places `instrument` directly on the action; cdifProvActivity places instruments in the role-keyed `prov:used` wrapper. The converters currently follow WRROC: they put `schema:instrument` directly on the activity (68 occurrences across the examples here) or on the `schema:actionProcess` node. cdifProvActivity is an open schema, so this validates, but it is not the placement CDIF documents. Software tools, by contrast, are already emitted in the wrapper form (`prov:used` → `bios:computationalTool`). **Open item:** either move the converters' instruments into the wrapper, or document activity-level `schema:instrument` as an accepted alternative.
* **Workflow as methodology vs. instrument**: In WRROC, the `ComputationalWorkflow` is the `instrument` of an `OrganizeAction`. In cdifProvActivity, it's more natural to treat it as `schema:actionProcess` (methodology). The converter maps it to `schema:actionProcess` for actions that `executesLabProtocol`, and as `schema:instrument` context otherwise.
* **Bioschemas vocabulary**: Terms like `LabProcess`, `LabProtocol`, `Sample` are Bioschemas extensions not in the core schema.org vocabulary. These are preserved as `additionalType` values with the `bios:` prefix (`https://bioschemas.org/`). CDIF defines the Bioschemas properties it uses (`bios:executesLabProtocol`, `bios:parameterValue`, `bios:labEquipment`, `bios:computationalTool`, `bios:reagent`) in the [cdifBioschemasProperties](https://github.com/Cross-Domain-Interoperability-Framework/metadataBuildingBlocks/tree/main/_sources/bioschemasProperties/cdifBioschemasProperties) building block.
* **`@id`s that are not valid IRIs**: Galaxy crates carry spaces and pipes in `@id`s (`#input-Sn Foil`). A JSON-LD processor drops such a node *and its incoming triple*, after the JSON Schema check has already passed. The converters now percent-encode `@id`s, applying the same encoding to definitions and references so they still match (2026-10-01).

### 5.5 Conversion Examples

Six Galaxy workflow RO-Crates from [Zenodo record 13842780](https://zenodo.org/records/13842780) have been converted, demonstrating computational workflow provenance (FeS2 analysis, Pt3Sn catalyst, Au colloids, LaMnO3 catalytic behaviour, EXAFS fitting, Diphosphine workflow). The Bennu py-GC-MS example demonstrates both standard WRROC and ARC profile conversion for laboratory analytical workflows.

All examples are in the [examples](./examples/) folder. Source RO-Crates are in [examples/ROCRATE](./examples/ROCRATE/), and the converted documents are the `.cdifprov.json` (HowTo/step form) and `.actions.cdifprov.json` (one Action per step) files beside them.

## 6\. Representing Multi-Step Provenance

When a dataset is produced by a multi-step process (analytical workflow, computational pipeline), there are two structural options within cdifProvActivity for representing the steps.

### Option A: Activity list in `prov:wasGeneratedBy`

Each step is a separate `\["schema:Action", "prov:Activity"]` node in the `@graph` array. The dataset's `prov:wasGeneratedBy` points to all of them (or to the final activity, which chains backward via `schema:object` referencing prior activities' `schema:result`).

```json
{
  "@type": "schema:Dataset",
  "prov:wasGeneratedBy": \[
    { "@id": "#step1" },
    { "@id": "#step2" },
    { "@id": "#step3" }
  ]
}
```

**Advantages:**

* Each step is a full `prov:Activity`, enabling independent provenance queries
* Activity chaining via `schema:object`/`schema:result` captures data flow between steps
* Maps directly to WRROC's flat action model — each CreateAction becomes a graph node
* Allows different agents, instruments, and temporal bounds per step
* Supports partial provenance: consumers can process individual steps without understanding the whole chain

**Disadvantages:**

* No explicit ordering unless chained through `schema:object`/`schema:result` references
* The overall workflow structure (which steps belong to which workflow) is less visible
* Multiple activity nodes increase document complexity

### Option B: Steps as `schema:step` in `schema:actionProcess`

A single `\["schema:Action", "prov:Activity"]` represents the overall process. The detailed steps are `schema:HowToStep` entries within a `schema:HowTo` linked via `schema:actionProcess`.

```json
{
  "@type": \["schema:Action", "prov:Activity"],
  "schema:actionProcess": {
    "@type": "schema:HowTo",
    "schema:name": "Py-GC-MS/MS analysis protocol",
    "schema:step": \[
      {
        "@type": "schema:HowToStep",
        "schema:name": "Sample preparation",
        "schema:position": 1,
        "schema:text": "Load 0.5mg sample into quartz tube..."
      },
      {
        "@type": "schema:HowToStep",
        "schema:name": "Flash pyrolysis",
        "schema:position": 2,
        "schema:text": "Heat at 600°C, 10°C/ms ramp rate..."
      }
    ]
  }
}
```

**Advantages:**

* Compact: single activity node with embedded methodology
* Explicit ordering via `schema:position`
* Clear that steps belong to a single process
* Human-readable: steps read like a protocol
* Search engines understand `schema:HowTo` / `schema:HowToStep`

**Disadvantages:**

* `HowToStep` is not a `prov:Activity` — step-level provenance queries are not possible
* Cannot capture per-step agents, instruments, temporal bounds, or parameter values
* Steps are prospective (how it *should* be done) rather than retrospective (what *was* done)
* Less information: actual parameter values, error states, and execution metadata cannot be attached to individual steps

### Recommendation

Both approaches are valid cdifProvActivity. The choice depends on the level of detail:

* **Use Option A** (activity list) when each step has its own instruments, parameters, agents, temporal bounds, or when step-level provenance queries matter. This is the natural mapping for WRROC and ARC conversions where each action carries rich execution metadata.
* **Use Option B** (HowTo steps) when the methodology is the primary concern and step-level execution detail is not needed — e.g., describing a standard operating procedure without per-step timestamps or parameter values.
* **Combine both**: Use Option A for the retrospective provenance (what was done) and include `schema:actionProcess` on each activity pointing to the protocol/methodology (how it should be done). This is what the ARC profile naturally produces — `LabProcess` activities with `executesLabProtocol` → `LabProtocol`.

The Galaxy examples here exist in both forms for side-by-side comparison. `galaxyROCrateToCDIF.py` produces Option B, and `galaxyROCrateToCDIFActions.py` produces Option A. In the Option A output, each step is linked to its upstream steps with `prov:wasInformedBy` and back to the parent workflow action with `prov:wasInfluencedBy`.

The geochemistry profile ([§12](#12-a-domain-profile-built-on-cdifprovactivity-geochemistry-ada)) takes the "combine both" route one step further. The procedure is a separately published **plan** carrying the HowTo steps, and the analysis record is an activity that references that plan.

## 7\. Property Mapping Across All Approaches

|Concept|cdifProvActivity|provActivity|ddicdiActivity *(archived)*|WRROC|ARC Profile|PROV-JSONLD|
|-|-|-|-|-|-|-|
|**Activity type**|`\["schema:Action", "prov:Activity"]`|`\["prov:Activity"]`|`cdi:Activity`|`CreateAction`|`CreateAction` + `LabProcess`|`Activity`|
|**Name**|`schema:name`|`schema:name`|`cdi:name`|`name`|`name`|`label` (`rdfs:label`)|
|**Description**|`schema:description`|`schema:description`|`cdi:description`|`description`|`description`|prefixed attribute (flat value)|
|**Inputs**|`prov:used`|`prov:used`|`cdi:entityUsed`|`object`|`object`|`Usage` object (`activity`, `entity`)|
|**Outputs**|`schema:result`|`prov:generated`|`cdi:entityProduced`|`result`|`result`|`Generation` object (`entity`, `activity`)|
|**Agent**|`schema:agent`|`prov:wasAssociatedWith`|`cdi:ProcessingAgent`|`agent`|`agent`|`Association` object (`activity`, `agent`)|
|**Agent role**|`schema:Role` wrapper|—|implicit|—|—|`role` on `Association` (`prov:hadRole`)|
|**Instrument**|`prov:used` → `{"schema:instrument": \[...]}`|`schema:instrument` (in `prov:used`)|`cdi:entityUsed`|`instrument`|`labEquipment` (on protocol)|`Usage` with `role`|
|**Methodology**|`schema:actionProcess` → `HowTo`|`schema:actionProcess` → `HowTo`|`cdi:has\_Step`|`ComputationalWorkflow`|`executesLabProtocol` → `LabProtocol`|`plan` on `Association` (`prov:hadPlan`)|
|**Start time**|`schema:startTime`|`prov:startedAtTime`|`cdi:start`|`startTime`|`startTime`|`startTime` (or a `Start` object)|
|**End time**|`schema:endTime`|`prov:endedAtTime`|`cdi:end`|`endTime`|`endTime`|`endTime` (or an `End` object)|
|**Parameters**|`schema:additionalProperty`|—|`cdi:Parameter`|—|`parameterValue`|— (flat prefixed attributes only)|
|**Status**|`schema:actionStatus`|`schema:actionStatus`|—|`actionStatus`|`actionStatus`|—|
|**Error**|`schema:error`|`schema:error`|—|`error`|`error`|—|
|**Activity chain**|`schema:object`/`result`; `prov:wasInformedBy` (multi-activity converter output)|`prov:wasInformedBy`|`cdi:receives`/`produces`|`object`/`result`|`object`/`result`|`Communication` object, or `Usage` of a generated entity|
|**Samples**|`schema:Thing` (as `prov:used` or `schema:object`)|`prov:Entity`|`cdi:entityUsed`|`File`|`Sample`|`Entity`|

## 8\. Benefits and Challenges

### cdifProvActivity

**Benefits:**

* Broadest interoperability with web infrastructure: schema.org Action is understood by Google Dataset Search, web crawlers, and general-purpose JSON-LD consumers
* Aligned with [ODIS/OIH provenance recommendations](https://github.com/iodepo/odis-arch/blob/414-update-provenance-recommendations/book/thematics/provenance/common-provenance-cases.md)
* Dual typing bridges schema.org and PROV-O worlds
* Compact single-node or multi-node serialization
* `schema:actionProcess` → `HowTo` → `HowToStep` provides human-readable methodology
* Cleanly accommodates WRROC and ARC profile content through conversion

**Challenges:**

* `schema:actionProcess` is present on the schema.org website (V29.4+) but not yet in downloadable RDF vocabulary files
* Dual typing adds a concept (`schema:Action`) less familiar to provenance specialists

### provActivity

**Benefits:**

* Canonical W3C PROV-O property names enable direct use with PROV-O reasoning tools
* Supports PROV-O expanded terms (`prov:wasStartedBy`, `prov:wasEndedBy`, `prov:atLocation`)
* Activity-to-activity chaining via `prov:wasInformedBy` is more precise than schema.org's `object`/`result` pattern

**Challenges:**

* PROV-O property names not recognized by search engines
* Mixed `prov:` and `schema:` prefixes may confuse implementers
* No native methodology property in PROV-O outside of qualified associations

### ddicdiActivity 

**Benefits:**

* Native DDI-CDI vocabulary compatible with DDI-CDI statistical infrastructure
* Explicit data-flow modeling via `cdi:Parameter` with `cdi:receives` / `cdi:produces`
* `cdi:Step` nodes with `cdi:script` for executable code references
* `cdi:standardModelMapping` links to standard process models (e.g., GSBPM)
* `cdi:start`/`cdi:end` timestamps for temporal bounds (added from EA model)
* `cdi:definition` (InternationalString) for formal concept definitions

**Challenges:**

* DDI-CDI vocabulary specialized and not widely recognized outside statistical community
* Multi-node graph structure \~2.5× more verbose for the same scenario
* No dedicated instrument class
* Not understood by web search engines
* Archived in metadataBuildingBlocks (2026-10-05); no CDIF profile composes it

### WRROC / ARC

**Benefits:**

* Established community adoption in computational and life science workflows
* Rich retrospective provenance capturing actual execution details
* ARC profile adds structured parameterization well-suited for analytical chemistry
* RO-Crate packaging bundles provenance with the data files it describes
* Conversion to cdifProvActivity is straightforward and largely lossless

**Challenges:**

* Uses unqualified schema.org property names (no namespace prefixes) — requires JSON-LD context processing
* `schema:input`/`schema:output` (Bioschemas properties used in some implementations) are not in core schema.org; the standard properties are `schema:object`/`schema:result`
* `FormalParameter` has no direct schema.org equivalent type
* Bioschemas types (LabProcess, LabProtocol, Sample) are community extensions, not core schema.org
* RO-Crate's flat `@graph` structure requires restructuring for cdifProvActivity's nested inline pattern

## 9\. Implementing ARC Profile Support in CDIF

The ARC Workflow Run RO-Crate profile is particularly relevant for CDIF because it addresses the same domain: describing how scientific datasets were produced through analytical processes with specific instruments and parameters.

### 9.1 Natural Mappings

The ARC profile's core concepts map directly to cdifProvActivity:

|ARC Concept|cdifProvActivity Implementation|
|-|-|
|`LabProcess` execution|Activity node with `additionalType: \["schema:LabProcess"]`|
|`executesLabProtocol`|`schema:actionProcess` → `schema:HowTo` node|
|`parameterValue` array|`schema:additionalProperty` → `PropertyValue` objects|
|`labEquipment`|`schema:instrument` on the methodology (actionProcess) node|
|`Sample`|`schema:Thing` with `additionalType: \["bioschemas:Sample"]` in `prov:used`|
|`DefinedTerm` instruments|`\["schema:Thing", "schema:DefinedTerm"]` with identifier, description|
|Activity chaining (output → input)|`schema:result` on Activity₁ referenced in `prov:used` on Activity₂|

### 9.2 What the Bennu Example Demonstrates

The Bennu py-GC-MS/MS analysis ([standard](./examples/Bennu-py-GC-MS.cdifprov.json) and [ARC](./examples/Bennu-py-GC-MSarc.cdifprov.json) versions) demonstrates:

1. **Multi-step analytical chain**: Five activities linked through their inputs and outputs, capturing the complete analytical pathway from sample preparation through mass spectrometric detection.
2. **Rich parameterization**: Each step carries actual instrument settings as `schema:additionalProperty` PropertyValue objects — pyrolysis temperature (600°C), GC column dimensions (30m × 0.250mm × 0.50µm), MS scan range (m/z 50–500), number of targeted MRM compounds (38). These are preserved losslessly in the cdifProvActivity output.
3. **Protocol-equipment binding**: Instruments (pyrolysis oven, gas chromatograph, TSQ triple-quad mass spectrometer) are declared on the protocol (`schema:actionProcess`) and referenced by the steps that use them. This cleanly separates "what equipment exists" from "which step used it."
4. **Sample tracking**: Bioschemas `Sample` entities track the physical sample through the workflow, with sample-specific metadata (mass, preparation method) carried as `additionalProperty`.

### 9.3 Recommendations for CDIF

1. **Use `WRROCToCdifProv.py` for automated conversion** from existing WRROC/ARC RO-Crate files to cdifProvActivity. The converter handles both standard WRROC (computational workflows) and ARC profile (lab analytical workflows).
2. **For new analytical provenance**, author directly in cdifProvActivity using ARC-inspired patterns:

   * Use `schema:additionalProperty` with PropertyValue objects for instrument parameters
   * Use `schema:actionProcess` → `schema:HowTo` for protocol/methodology
   * Describe physical instruments with the CDIF [instrument](https://github.com/Cross-Domain-Interoperability-Framework/metadataBuildingBlocks/tree/main/_sources/schemaorgProperties/instrument) building block (a `schema:Thing` with `schema:hasPart` for sub-components), under the `schema:instrument` role in `prov:used`. Describe software with `schema:SoftwareApplication` under the `bios:computationalTool` role. A bare `schema:DefinedTerm` is enough when only the kind of instrument is known.
   * Chain activities through `schema:object`/`prov:used` → `schema:result` references
   * If you need a role the three named ones do not cover, define it in your profile as a role-keyed wrapper and close your profile's role set to it ([§12](#12-a-domain-profile-built-on-cdifprovactivity-geochemistry-ada) shows how)
3. **Preserve domain-specific types** via `schema:additionalType`. When converting from ARC, keep `LabProcess`, `LabProtocol`, `Sample` as additionalType values so domain-specific consumers can identify them.

## 10\. When to Use Each Approach

|Use Case|Recommended Approach|
|-|-|
|General CDIF metadata with web discoverability|**cdifProvActivity**|
|Interoperability with ODIS / Ocean InfoHub|**cdifProvActivity**|
|Converting existing WRROC/ARC workflow provenance|**cdifProvActivity** (via converter)|
|PROV-O tooling and formal provenance reasoning|**provActivity**; for exchange with PROV tools, a PROV-JSONLD export (see [§13.4](#134-options-for-cdif))|
|DDI-CDI infrastructure and statistical workflows|**ddicdiActivity** (archived; reference only)|
|Detailed data-flow modeling between processing steps|**ddicdiActivity** (archived), or cdifProvActivity in the multi-activity form (§6 Option A)|
|Lab analytical workflows with rich parameterization|**cdifProvActivity** with ARC-inspired patterns|
|A registered, reusable procedure followed by many analyses|**cdifProvActivity** activity referencing a published plan (see §12)|
|Minimal authoring effort|**cdifProvActivity** or **provActivity**|

Multiple building blocks can coexist. A Dataset's `prov:wasGeneratedBy` can point to an activity described using any approach, and the base `generatedBy` building block provides a minimal common denominator that all PROV-aware consumers can process.

## 11\. Shared Infrastructure

### Base generatedBy building block

Both cdifProvActivity and provActivity extend the [generatedBy](https://github.com/Cross-Domain-Interoperability-Framework/metadataBuildingBlocks/tree/main/_sources/provProperties/generatedBy) building block via JSON Schema `allOf`. The base requires only an `@type` array containing `prov:Activity`. `prov:used` is optional, and it defines the five `prov:used` item shapes described in §2. Any consumer that understands these can extract basic provenance from any CDIF document. The layering is deliberate: **the base is permissive and the profile is restrictive**, which `allOf` composes correctly because an intersection can only narrow.

### objectReference building block

[objectReference](https://github.com/Cross-Domain-Interoperability-Framework/metadataBuildingBlocks/tree/main/_sources/cdifDataType/objectReference) is the strict node reference `{"@id": "..."}`: `@id` required, nothing else allowed. Since 2026-10-09 the building blocks reference it rather than restating it (115 sites). Every `prov:used`, `schema:location` and `schema:actionProcess` slot that accepts "a reference to something defined elsewhere" uses it.

### Instrument building block

The generic [instrument](https://github.com/Cross-Domain-Interoperability-Framework/metadataBuildingBlocks/tree/main/_sources/schemaorgProperties/instrument) building block provides a reusable `schema:Thing`-based instrument description with `schema:hasPart` for hierarchical instrument systems. Since 2026-08-17 its `schema:additionalProperty` accepts a `schema:PropertyValueSpecification` (a setting a plan prescribes) as well as a `schema:PropertyValue` (a setting actually used), which a plan/activity split needs (§12).

### SHACL validation

cdifProvActivity, provActivity and the archived ddicdiActivity each have a companion `rules.shacl` file, with SHACL validation shapes at three severity levels: Violation (required), Warning (recommended) and Info (optional). This repository publishes the merged shapes for the CDIF Provenance profile as [provenanceRules.shacl](provenanceRules.shacl).

## 12\. A Domain Profile Built on cdifProvActivity: Geochemistry (ADA)

The [geochemBuildingBlocks](https://github.com/amds-ldeo/geochemBuildingBlocks) repository (the Astromat Data Archive, ADA) is the most developed consumer of cdifProvActivity. It shows what a domain profile adds once provenance has to describe thousands of real analyses. Several of the 2026 changes to the CDIF base blocks came from this work.

### 12.1 Plan and activity are separate documents

ADA separates the **procedure** from the **analysis that followed it**:

* **The plan.** A registered *Technique-Aligned Protocol Profile* (TAPP) definition is typed `prov:Plan` and `bios:LabProtocol`, together with `cdi:Activity`, `schema:Action` and `ada:TAPPDefinition` for the DDI-CDI process description ([tappDefinition](https://github.com/amds-ldeo/geochemBuildingBlocks/tree/main/_sources/BaseSchema/tappDefinition)). It is published once and referenced by every analysis that followed it. Its workflow is a `schema:actionProcess` → `schema:HowTo` whose `schema:step`s are the standard stages (sample preparation, calibration, data acquisition, data processing, quality control). Because it is a plan, its instruments, `bios:computationalTool`s and `bios:reagent`s are stated directly on the plan as the resources it *prescribes*, not as `prov:used` entities.
* **The activity.** The analysis record's `prov:wasGeneratedBy` item is a cdifProvActivity. It references the plan through `prov:used`, records the instruments, software and reagents *actually used* in that run, and carries `schema:object` (the samples analysed) and `schema:location` (the laboratory).

This is §6's "combine both" pattern at the level of separate documents. A record does not duplicate a plan hundreds of times; it points at the plan.

### 12.2 Role-keyed `prov:used`, closed at the profile

The geochemistry product schema pins four roles in `prov:used`, each with a constraint-only `if/then`:

|role key|pinned value|
|-|-|
|`schema:instrument`|array of the geochem instrument building block|
|`bios:computationalTool`|array of software actually used|
|`bios:reagent`|array of reagents / reference materials actually used|
|`ada:tappDefinition`|the plan: a closed `{@id}` reference, or the plan inline|

The reagent role is spelled `bios:reagent`, the same as on the plan. The profile also **rejects** the old spelling `prov:reagent` outright, with a rejection message that names the new key, and a counterexample keeps that rejection in place ([geochemBuildingBlocks#220](https://github.com/amds-ldeo/geochemBuildingBlocks/pull/220)). Rejecting it needed no record migration first: `prov:reagent` occurred 0 times in every stored ADA document. Without the profile's rejection, the CDIF base would still admit the old key through its generic wrapper branch.

`ada:tappDefinition` is a profile-defined role. It reaches CDIF through the generic wrapper branch added to the base in metadataBuildingBlocks #52, and the profile closes the set to the roles it names. The reason for keying the plan link on a property name rather than on `@type` is that the **role is then readable without dereferencing anything**. An inline `prov:Entity` carries `ada:TAPPDefinition` in its `@type` too, so `@type` could never separate "the plan this run followed" from "a document that happens to be a plan".

The earlier spelling, a `prov:used` item with `@type` containing `ada:TAPPDefinition`, is now **rejected** in both its reference and inline forms (2026-10-24). That was not done until the corpus had moved: 7,263 of 7,447 ADA records used the old reference form, and the schema was tightened only after the migration measured zero remaining in both stores. Any profile retiring a shape that real records use faces the same ordering: migrate the records first, then tighten the schema.

### 12.3 Parameters: prescribed on the plan, actual on the activity

The same split applies to parameters:

|side|node|parameter type|
|-|-|-|
|plan (TAPP)|`schema:additionalProperty` on the plan or a step|`schema:PropertyValueSpecification`: a named, typed setting, optionally with a fixed value|
|activity (analysis)|`schema:additionalProperty`|`schema:PropertyValue`: the value actually used|

This corresponds to ARC's `LabProtocol` (prospective) and `LabProcess.parameterValue` (retrospective), and it is why the CDIF instrument block now accepts both forms (§11).

### 12.4 Step names are identities

A workflow step is matched by its literal name. The vocabulary is sentence-case (`'Sample preparation'`, `'Data acquisition'`, `'Data processing'`), and `'Data processing'` replaced `'Data reduction'` on 2026-10-12. Two spellings for one step silently produce two different steps, and a step-specific constraint written as an `if/then` then does not fire, so a misnamed step validates clean. **Any profile that constrains steps by name needs a controlled step vocabulary.** The CDIF base does not yet provide one.

## 13\. PROV-JSONLD (W3C Member Submission, 2024)

### 13.1 What it is

[*The PROV-JSONLD Serialization*](https://www.w3.org/submissions/2024/SUBM-prov-jsonld-20240825/) (Luc Moreau and Dong Huynh, King's College London; W3C Member Submission, 25 August 2024) is a JSON-LD representation of the PROV Data Model. A Member Submission is **not a W3C Recommendation**: W3C publishes it without endorsing it, and no chartered group has reviewed it. Its stated goals are a serialization that is lightweight, natural, semantic and efficient. It ships with three artifacts:

* a JSON-LD 1.1 context at `https://openprovenance.org/prov-jsonld/context.jsonld`;
* a JSON Schema (draft-07) at `https://openprovenance.org/prov-jsonld/schema.json`;
* a small OWL extension ontology (`provext`) for the PROV relations PROV-O has no qualified form for (specialization, alternate, membership).

The design is **relation-centric**. A document is a flat `@graph` of self-contained objects, one per PROV statement:

* `Entity`, `Activity` and `Agent` objects need an `@id`;
* each *relation* (`Usage`, `Generation`, `Association`, `Derivation`, `Communication`, `Start`, `End`, `Attribution`, `Delegation`, …) is its own object with an `@type`, pointing at its participants by identifier.

JSON-LD 1.1 type-scoped contexts let one short key mean different things depending on the object. For example, `activity` on a `Usage` maps to `@reverse prov:qualifiedUsage`, and on an `Association` to `@reverse prov:qualifiedAssociation`. So every relation expands to the **PROV-O qualified pattern**. `role` maps to `prov:hadRole`, `plan` to `prov:hadPlan`, and `time` to `prov:atTime`. The context defines **no** unqualified relation terms (`used`, `wasGeneratedBy`, `wasAssociatedWith`): PROV-JSONLD emits only qualified forms.

The JSON Schema is closed (`additionalProperties: false` on every statement type). Extension attributes are allowed only as **prefixed keys whose values are flat arrays** of strings, typed values, language strings or `{@id}` references. A nested object, such as a `schema:Person` with an identifier and affiliation, or a `schema:PropertyValue` with a unit, cannot be carried inline.

### 13.2 The same facts in both encodings

Below, the same facts are written in both encodings: a run used an ICP-MS as its instrument and a sample, and followed a plan. Each is followed by the triples it parses to (verified with rdflib).

cdifProvActivity:

```json
{ "@id": "ex:run1", "@type": \["schema:Action", "prov:Activity"],
  "prov:used": \[ {"schema:instrument": \[ {"@id": "ex:icpms"} ]}, {"@id": "ex:sample1"} ] }
```

```turtle
ex:run1 a schema:Action, prov:Activity ;
    prov:used \[ schema:instrument ex:icpms ], ex:sample1 .
```

PROV-JSONLD:

```json
{ "@context": \["https://openprovenance.org/prov-jsonld/context.jsonld", {"ex": "http://example.org/"}],
  "@graph": \[
    { "@type": "Activity", "@id": "ex:run1" },
    { "@type": "Usage", "activity": "ex:run1", "entity": "ex:icpms", "role": \["ex:instrument"] },
    { "@type": "Association", "activity": "ex:run1", "agent": "ex:lab", "plan": "ex:tapp1" } ] }
```

```turtle
ex:run1 a prov:Activity ;
    prov:qualifiedUsage \[ a prov:Usage ; prov:entity ex:icpms ; prov:hadRole ex:instrument ] ;
    prov:qualifiedAssociation \[ a prov:Association ; prov:agent ex:lab ; prov:hadPlan ex:tapp1 ] .
```

### 13.3 What the comparison shows about CDIF

1. **In RDF, the role-keyed wrapper makes the wrapper the used entity.** `prov:used \[ schema:instrument ex:icpms ]` says the activity used an *anonymous node*, and that node's instrument is the ICP-MS. It does not say the activity used the ICP-MS. A SPARQL query for `?activity prov:used ex:icpms` finds nothing. The wrapper is a sound **JSON** device: the role can be read from the key, and JSON Schema can pin each role's value. But its RDF reading is not PROV's. PROV-O expresses "used X in role R" as a qualified usage, `prov:qualifiedUsage \[ prov:entity X ; prov:hadRole R ]`, which is exactly what PROV-JSONLD produces.
2. **The plan link.** In PROV-O an activity follows a plan through its association (`prov:qualifiedAssociation` / `prov:hadPlan`). CDIF expresses this as `schema:actionProcess` (methodology), and the ADA profile also as a `prov:used` role (`ada:tappDefinition`). Saying the run *used* the plan is permissible in PROV, since a plan is a `prov:Entity`, but a PROV consumer looking for `prov:hadPlan` will not find it.
3. **Qualified-only output has its own cost.** A PROV-JSONLD document contains no unqualified `prov:used` / `prov:wasGeneratedBy` triples. Consumers that query the unqualified relations, which is what CDIF's `generatedBy` base and most schema.org-oriented harvesters read, need a rule that derives them.
4. **The two fit different jobs.** PROV-JSONLD is a faithful, lossless carrier for the PROV *graph*. cdifProvActivity is a validatable, nested JSON description of an activity, carrying rich schema.org content. Because of PROV-JSONLD's closed schema and flat attribute values, a CDIF activity's agents, instruments, parameters and HowTo steps cannot be carried in it except as references to nodes it has no way to describe.

### 13.4 Options for CDIF

|option|what it means|cost|
|-|-|-|
|**A. Note only**|Cite PROV-JSONLD; change nothing|Leaves item 1 above unaddressed|
|**B. Export**|A converter from cdifProvActivity to PROV-JSONLD, so CDIF provenance can be handed to PROV tooling (ProvToolbox, PROV validators)|Lossy by design: descriptive content is reduced to references and flat attributes|
|**C. Align provActivity**|Give the PROV-O-first block the qualified forms (`prov:qualifiedUsage` with `prov:hadRole`, `prov:qualifiedAssociation` with `prov:hadPlan`), using PROV-JSONLD's shapes as the reference|provActivity currently has no qualified association ([agents.md §3.2](agents.md)); new schema work|
|**D. Give the wrapper a PROV reading**|Document the mapping from each role key to a `prov:qualifiedUsage` / `prov:hadRole` (and from `ada:tappDefinition` / `schema:actionProcess` to `prov:hadPlan`), and publish it as a SPARQL CONSTRUCT or SHACL rule a consumer can run|Small; keeps every existing record valid|
|**E. Adopt PROV-JSONLD as CDIF's serialization**|Replace the nested activity form|Not recommended: a Member Submission with no endorsement, a closed schema that cannot carry schema.org descriptions, and loss of the search-engine-readable `schema:Action`|

**Recommendation for review: D now, then B, and consider C.** D fixes the semantic gap in item 1 without invalidating any record. B and C give CDIF a standards-shaped path into PROV tooling. cdifProvActivity stays the primary authoring and validation shape.

## 14\. Open Issues

1. **RESOLVED (2026-10-25): the reagent role is now `bios:reagent`.** The role was spelled `prov:reagent`, but PROV-O defines no `reagent` term, while the ADA plan already used `bios:reagent`, which cdifBioschemasProperties defines. The role was renamed to `bios:reagent` everywhere, in two waves:
   - **CDIF base:** the `generatedBy` named wrapper branch and the cdifProvActivity description ([metadataBuildingBlocks#53](https://github.com/Cross-Domain-Interoperability-Framework/metadataBuildingBlocks/pull/53), merged and published to gh-pages).
   - **Downstream:** the ADA profile, which also rejects the old key ([geochemBuildingBlocks#220](https://github.com/amds-ldeo/geochemBuildingBlocks/pull/220)); ddeBuildingBlocks; and the CDIF release repos' synced schemas. These were open as draft PRs at the time of writing.

   Before the rename, `prov:reagent` occurred 0 times in any JSON column of the ADA stores (`ada2`, `ada_subjects`, `method_registry`), and `bios:reagent` was already in 72 of 500 TAPP plans. Plan and activity now spell the role the same way.
2. **The RDF reading of role-keyed wrappers** (§13.3 item 1; option D).
3. **Converter instrument placement** differs from the documented wrapper placement (§5.4).
4. **No controlled step vocabulary** in the CDIF base for `schema:step` names (§12.4).
5. **`schema:actionProcess`** is on the schema.org website (V29.4+) but still not in the downloadable vocabulary files (§8).
6. **ddicdiActivity is archived.** Decide whether DDI-CDI provenance stays in scope for this document or moves to an appendix.

## 15\. Changes from ProvenanceOptions.md

What this document changes relative to [ProvenanceOptions.md](ProvenanceOptions.md), checked against metadataBuildingBlocks `main` at `31b890a802` and geochemBuildingBlocks `main` on 2026-10-25:

* ddicdiActivity marked archived (moved to `archive/ddiProperties/` on 2026-10-05); links repointed.
* §2 and §11: the five `prov:used` item shapes, including role-keyed wrappers and the generic profile-defined wrapper (#52, 2026-10-22); the sealed objectReference; the base requiring only `@type`; array `@type` throughout.
* §5: converter placement of instruments; the `OrganizeAction` and `@id`-encoding corrections of 2026-10-01; `bios:` prefix; converter files in this repository.
* §7: added PROV-JSONLD and agent-role rows.
* New §12 (ADA geochemistry profile), §13 (PROV-JSONLD), §14 (open issues).
* 2026-10-26: the `prov:reagent` → `bios:reagent` rename (§2, §12.2; §14 item 1 marked resolved).

## 16\. Sources and References

### Standards and specifications

* [W3C PROV-O: The PROV Ontology](https://www.w3.org/TR/prov-o/)
* [W3C PROV-DM: The PROV Data Model](https://www.w3.org/TR/prov-dm/)
* [The PROV-JSONLD Serialization](https://www.w3.org/submissions/2024/SUBM-prov-jsonld-20240825/) — W3C Member Submission, 25 August 2024 ([context](https://openprovenance.org/prov-jsonld/context.jsonld), [JSON Schema](https://openprovenance.org/prov-jsonld/schema.json))
* [DDI-CDI 1.0 Specification](https://ddialliance.org/Specification/DDI-CDI/1.0/)
* [schema.org Action](https://schema.org/Action)
* [schema.org actionProcess](https://schema.org/actionProcess) (V29.4+)
* [schema.org HowTo](https://schema.org/HowTo) / [HowToStep](https://schema.org/HowToStep)
* [schema.org instrument](https://schema.org/instrument)
* [RO-Crate 1.1 Specification](https://w3id.org/ro/crate/1.1)

### Workflow Run RO-Crate profiles

* [Process Run Crate 0.5](https://w3id.org/ro/wfrun/process/0.5)
* [Workflow Run Crate 0.5](https://w3id.org/ro/wfrun/workflow/0.5)
* [Provenance Run Crate 0.1](https://w3id.org/ro/wfrun/provenance/0.1)
* [ARC Workflow Run RO-Crate Profile](https://github.com/nfdi4plants/arc-wr-ro-crate-profile)
* [Bioschemas LabProcess](https://bioschemas.org/profiles/LabProcess)
* [Bioschemas LabProtocol](https://bioschemas.org/profiles/LabProtocol)
* [Galaxy RO-Crate workflow examples (Zenodo 13842780)](https://zenodo.org/records/13842780)

### Community recommendations and patterns

* [ODIS Architecture: Common Provenance Cases](https://github.com/iodepo/odis-arch/blob/414-update-provenance-recommendations/book/thematics/provenance/common-provenance-cases.md)
* [Ocean InfoHub (OIH)](https://oceaninfohub.org/)
* [geochemBuildingBlocks](https://github.com/amds-ldeo/geochemBuildingBlocks) — ADA geochemistry profile; [tappDefinition](https://github.com/amds-ldeo/geochemBuildingBlocks/tree/main/_sources/BaseSchema/tappDefinition) (the plan) and [geochemProduct](https://github.com/amds-ldeo/geochemBuildingBlocks/tree/main/_sources/BaseSchema/geochemProduct) (the activity's role-keyed `prov:used`)
* [BBeuster EU-SoGreen-Prov DDI-CDI Provenance Examples](https://github.com/ddialliance/ddi-cdi_provenance-examples)
* [UNECE Generic Statistical Business Process Model (GSBPM) v5.1](https://statswiki.unece.org/display/GSBPM/)

### Schema infrastructure

* [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/schema)
* [OGC Building Blocks](https://opengeospatial.github.io/bblocks/)
* [NERC Vocabulary Server (NVS)](https://vocab.nerc.ac.uk/)

### Tools

* [WRROCToCdifProv.py](tools/WRROCToCdifProv.py) — WRROC/ARC to cdifProvActivity converter
* [galaxyROCrateToCDIF.py](tools/galaxyROCrateToCDIF.py) / [galaxyROCrateToCDIFActions.py](tools/galaxyROCrateToCDIFActions.py) — Galaxy RO-Crate to cdifProvActivity, HowTo/step and multi-activity forms
* [ROCrateToCDIF.py](https://github.com/Cross-Domain-Interoperability-Framework/packaging/tree/main/tools/ROCrateToCDIF.py) — RO-Crate to full CDIF metadata converter

