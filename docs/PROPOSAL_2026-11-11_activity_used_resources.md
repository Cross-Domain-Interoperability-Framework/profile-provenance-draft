# Proposal: drop `prov:used` from the schema.org activity (cdifProvActivity)

Status: draft for discussion, 2026-11-11. No schema has been changed.

**Scope.** Sections 1–7 are CDIF: metadataBuildingBlocks, the `profile-*` release repos and the
validation repo. CDIF has no TAPP. Everything about TAPPs is in **§8**, and applies only in
geochemBuildingBlocks.

**Terms.** "Plan", used on its own here, means the `prov:Plan` an activity followed (§4.4). It never
means this proposal.

## 1. Problem

`prov:used` on a cdifProvActivity is a polymorphic array. An item is a string, an `{@id}`, an inline
`prov:Entity`, or a **role-keyed wrapper**: an untyped object whose single key names the role
(`{"schema:instrument": [...]}`, `{"bios:computationalTool": [...]}`, `{"bios:reagent": [...]}`, or a
profile-defined role).

The wrappers cause recurring trouble:

- validator.schema.org reports each wrapper as an "Unspecified Type": it is a node with no `@type`.
- The open branch for profile-defined roles (`propertyNames` pattern) cannot validate expanded JSON-LD,
  because expansion turns every key into a full IRI.
- A JSON-LD frame has to be kept to `@embed` only, or it silently drops wrappers
  (profile-provenance CLAUDE.md, trap 3).
- In RDF a wrapper is an extra blank node between the activity and the thing used, so every query and
  SHACL path has one more hop than the meaning needs.

The aim is:

- a cdifProvActivity that uses schema.org properties only for what an activity used, and that can
  name the plan it followed (§4.4);
- a separate, pure-PROV `prov:used` in `provActivity`;
- a cdifCore `prov:wasGeneratedBy` returned to its **original definition**: a `prov:Activity` whose
  `prov:used` items are strings or `@id` references. Any further structure belongs to the extending
  profiles (§4.5).

## 2. What the current corpus uses

**CDIF.** Counted on 2026-11-11 over the mBB and `profile-*` example JSON:

- 138 `prov:wasGeneratedBy` activities, all with an array `@type`;
- 196 `prov:used` items: 2 strings, 101 carrying `@id`, and 93 objects without `@id` (wrappers and
  anonymous inline entities);
- 22 activities with `schema:actionProcess`: 18 inline `HowTo`s, 4 `{@id}` references.

**geochemBuildingBlocks**, the largest user of the wrappers. Counted over the 316 `example*.json`
files in `_sources/` that use `prov:used`. The production stores are not yet measured; see §6.

| `prov:used` item | count | proposed home |
|---|---|---|
| `{"schema:instrument": [...]}` | 260 | `schema:instrument` |
| `{"bios:computationalTool": [...]}` | 131 | `schema:instrument`, software kind |
| `{"bios:reagent": [...]}` | 61 | see §4.3 |
| `{"ada:tappDefinition": {...}}` | 68 | the plan link, §8 |
| bare `{@id}` | 1 | `schema:object` |

## 3. Facts the design depends on

Checked on schema.org on 2026-11-11:

- `schema:instrument`: used on **Action**; range **Thing**; "The object that helped the agent perform
  the action."
- `schema:additionalProperty`: used on **MerchantReturnPolicy, Offer, Place, Product, QualitativeValue,
  QuantitativeValue**. **Not Action.**
- `schema:value`: range **Boolean, Number, QualitativeValue, StructuredValue, Text**. A
  ChemicalSubstance, Product or DefinedTerm is not in range.

In the schemas:

- cdifCore uses `provProperties/generatedBy` as its `GeneratedBy` definition
  (`_sources/profiles/cdifProfile/cdifCore/schema.yaml`, `$defs/GeneratedBy`), so any change to that
  block reaches every CDIF record, not only provenance.
- cdifProvActivity's `schema:actionProcess` already accepts an inline `HowTo`, a string, or an
  `objectReference` (sealed `{@id}`).
- `implementationTesting/APPROACHES.md` maps "the plan or procedure the step followed" to
  `schema:actionProcess` in the schema.org approach, and to `prov:hadPlan` in PROV-O.

## 4. Design

### 4.1 Instruments: `schema:instrument` on the activity

As proposed. `schema:instrument` is an array. An instrument item is typed `schema:Product`, and
`schema:additionalType` contains `{"@id": "https://www.wikidata.org/wiki/Q3099911"}`, as the geochem
instrument block already requires.

Dropping `schema:Thing` from the required types is safe: Product is a subclass of Thing. Require
`schema:Product`, and **allow** `schema:Thing`, so existing records stay valid. In CDIF that means the
mBB `schemaorgProperties/instrument` `@type` `allOf contains`. geochem has the same requirement in one
more place (§8).

### 4.2 Samples and inputs: `schema:object`

Already defined on cdifProvActivity. A bare `{@id}` input in `prov:used` moves here.

### 4.3 Software and reagents: also `schema:instrument`, told apart by kind

Every resource the activity used, other than its inputs, becomes a `schema:instrument` item. An
`if/then` on the item's type picks the shape it must have:

| kind | `@type` contains | `schema:additionalType` contains | pinned to |
|---|---|---|---|
| instrument | `schema:Product` | `wd:Q3099911` (measuring instrument) | Instrument |
| software | `schema:SoftwareApplication` | `wd:Q7397` (software) | ComputationalTool |
| reagent / reference material | `schema:DefinedTerm`, `schema:Product` or `schema:ChemicalSubstance` | `wd:Q2356542` (chemical reagent) | Reagent |

Decided 2026-11-11: software and reagents go in `schema:instrument` as these kinds, and the reagent
kind's `additionalType` is `https://www.wikidata.org/wiki/Q2356542`.

**How the kinds are told apart (decided 2026-11-11).**

- **By `schema:additionalType`, not `@type`.** A reagent can be a `schema:Product` (a catalogued
  specimen), just as an instrument is, so `@type` alone is ambiguous. In cdifProvActivity, every
  `schema:instrument` item described in place must carry exactly one of the three Wikidata terms, and
  the `if/then` pins key on that term. This makes Q3099911 required for an instrument in CDIF; until
  now mBB only recommended it, and geochem already requires it.
- **References are accepted.** A `schema:instrument` item may also be a sealed `{@id}` reference to an
  instrument, tool or reagent described elsewhere. It carries no kind, so the kind rule does not apply
  to it.

Wikidata describes Q2356542 as a substance added to a system to bring about a chemical reaction. That
fits the acids and blanks. It is a looser fit for a calibration standard or reference material, such
as BHVO-2: the term marks the kind, and the reagent's role says how it was used.

CDIF defines the three kinds and their minimal shapes. A domain profile adds its own properties, for
example a role property on a reagent.

**Changes from the original proposal:**

- **Software type.** The original proposal typed software as `schema:Product`. This design types it
  `schema:SoftwareApplication`, which is what the cdifProv example and the Bioschemas ComputationalTool
  profile use. SoftwareApplication is a CreativeWork, not a Product; adding `schema:Product`
  alongside it can be allowed but should not be required.
- **No property IRI in `additionalType`.** `bios:computationalTool` is a Bioschemas *property*, so it
  should not appear as an `additionalType` value. Q7397 carries the "this is software" signal.
- **Reagents.** The original proposal put reagents in `schema:additionalProperty`, with `propertyID`
  `bios:reagent`. That doesn't hold up, for three reasons:
  1. `additionalProperty` is not defined on Action (§3), so validator.schema.org flags it. That
     defeats the point of the change. The `schema:additionalProperty` that cdifProvActivity already
     allows, for run parameters, is kept as a known warning (§7, question 6), but that is no reason
     to add reagents to it.
  2. A reagent is a typed node (ChemicalSubstance, DefinedTerm or Product), and those types are not in
     `schema:value`'s range.
  3. Each reagent would gain a PropertyValue node, with `schema:name` and `schema:value` required, so
     the RDF path grows from one hop (the wrapper) to two (`additionalProperty`, then `value`).

  A reagent that helped perform the analysis fits the `schema:instrument` definition, keeps its
  current shape, and needs no wrapper.

**Why not `schema:object` for reagents:** `schema:object` holds what was analysed. Putting standards
in it makes "which samples were measured" ambiguous.

**Alternative considered, not taken:** keep `bios:reagent` and `bios:computationalTool` as
**direct** activity properties. The keys would match the Bioschemas LabProtocol terms, but the
activity would no longer be schema.org-only.

### 4.4 The plan the activity followed

cdifProvActivity should let an activity name the `prov:Plan` it followed: a protocol, method or
workflow definition described elsewhere. **For now the value is an object reference** (a sealed
`{@id}`); CDIF defines no inline plan object.

**Property: `schema:actionProcess`.** It is the schema.org term for "the process by which the action
was performed", it is what APPROACHES.md already maps `prov:hadPlan` to, and cdifProvActivity already
accepts an `objectReference` there. A run that followed a published method says:

```json
"schema:actionProcess": {"@id": "https://example.org/methods/icpms-trace-elements"}
```

**The conflict with inline `HowTo`s.** cdifProvActivity also accepts an inline `HowTo` in the same
property. That is in use: 18 CDIF activities, including the cdifProv example whose activities point at
its HowTo steps with `p:correspondsToStep`. So one property currently means both "the plan this
followed" (a reference) and "the procedure as performed" (inline). A run that needs both cannot have
both. Options:

- **(A) Keep both forms for now.** The `{@id}` form is the plan link, and the inline `HowTo` stays as
  it is. This changes no schema; only the descriptions change. Revisit when an inline plan is
  defined. **Decided 2026-11-11.**
- **(B) Reference only.** Narrow `schema:actionProcess` to `objectReference`, which is the literal
  reading of "not an inline plan object". The 18 inline `HowTo`s would move to separately identified
  nodes and be referenced by `@id`. That is harder in a record that is a single tree rooted on the
  Dataset.
- **(C) A separate plan property.** Keep `schema:actionProcess` for the inline procedure, and link the
  plan with `prov:qualifiedAssociation` → `{"@type": ["prov:Association"], "prov:hadPlan": {"@id":
  …}}`. This is the correct PROV form, and it is what the PROV-O and ProvONE approaches in
  `implementationTesting/` already use. It costs one typed node, and it is not schema.org.

**When a run has both a plan and an inline procedure (decided 2026-11-11):**

- `schema:actionProcess` is the inline `HowTo`.
- That HowTo links the plan with `schema:isBasedOn` → `{@id}`. `isBasedOn` is a CreativeWork property,
  and HowTo is a CreativeWork, so this is valid schema.org.
- In the schema.org implementation this is preferred over the qualified association in (C), which
  stays the form for the PROV-O implementation. This is option (i) from §8, applied to CDIF generally.
  See [tapp-link-candidates/analysis-i-isBasedOn.json](tapp-link-candidates/analysis-i-isBasedOn.json).
- One query finds the plan in both cases:
  `prov:wasGeneratedBy/schema:actionProcess/schema:isBasedOn?`.
- cdifProvActivity's `HowTo` definition gains `schema:isBasedOn`, a sealed `objectReference`, for now.

`prov:hadPlan` directly on the activity is ruled out: its PROV-O domain is `prov:Association`, so an
RDFS reasoner would type the activity as an Association.

**Reference only, all options.** The plan's own description lives in another document or another
node. JSON Schema checks only the reference, so CDIF imposes no type on the plan. A domain profile
may require its plans to be a particular kind (§8).

### 4.5 Block structure: return generatedBy to the core definition

`provProperties/generatedBy` is what cdifCore uses for every `prov:wasGeneratedBy` item. Rather than
deprecate it, **revert it to the original cdifCore definition**, written so that the extending
profiles narrow it and never have to loosen it.

**What it was.** The first version (6026f4f) said: `@type` is the string `prov:Activity`, and each
`prov:used` item is a string or an object with an optional `@id`. Since then, five commits have grown
it:

- d39dabbd: `prov:Entity` on inline entities;
- 4a5f3008: required `@type` on entity nodes;
- f48dda3d: the tightened `@id` references and the wrapper model;
- d310dd1a: the generic role-keyed wrapper (mBB#52);
- a7d4c971: the rename of `prov:reagent` to `bios:reagent` (mBB#53).

Most of that growth served the geochem wrappers.

**Two details of the original would block extension, or check nothing:**

- `@type: {const: prov:Activity}` as a string. A profile that adds `schema:Action` makes `@type` an
  array, which fails a string `const`. The core has to say *contains* `prov:Activity`, so an
  extension can add types.
- The object branch of `prov:used` had no `required` and was open, so it accepted *any* object: the
  wrappers, an inline entity, `{}`. It never failed, but it checked nothing. To be the "`@id`
  reference" it was meant to be, it must require `@id`.

**Proposed core definition:**

```yaml
title: Activity that generated the resource (CDIF core)
type: object                     # open: extending profiles add properties (schema:instrument, schema:object, ...)
required: ['@type']
properties:
  '@type':
    type: array
    items: {type: string}
    minItems: 1
    contains: {const: prov:Activity}   # profiles add schema:Action etc.
  'prov:used':
    type: array
    items:
      anyOf:
      - type: string                   # IRI or free-text name
      - type: object                   # an @id reference to an entity used
        required: ['@id']
        properties:
          '@id': {type: string}
```

**Open `@id` reference (decided 2026-11-11).** The reference branch is deliberately **not** sealed:
there is no `additionalProperties: false`, unlike `objectReference`. The core only promises that each
item *identifies* an entity. An extending profile may describe that entity in place, as long as it
keeps the `@id`. `provActivity`'s inline `prov:Entity` stays valid under the core this way.

Sealing it, by `$ref` to `objectReference`, would make the core reject every inline description. Since
`allOf` can only narrow, no profile could then re-admit one. That is a decision against extension the
core shouldn't make. A profile that wants only bare references can seal the branch itself.

**What the core does not do:**

- It does not require `prov:used`. This keeps the original's optionality; a profile may require it.
- It names no roles, no wrapper branch, no `prov:Entity` typing, no instrument shapes and no plan.

**Consequence for the wrappers.** A role-keyed wrapper has no `@id`, so it is **rejected** by this
core. The revert therefore has to come *after* the wrappers are migrated out of `prov:used` (§6).

**The extending blocks:**

- **`cdifDataType/cdifProvActivity`** (`allOf` generatedBy, as now):
  - **requires** (decided 2026-11-11):
    - `@type` contains `schema:Action`;
    - at least one of `schema:instrument`, `schema:object` or `schema:actionProcess` (revised
      2026-11-11; this replaces the earlier instrument-or-object rule). It goes in the JSON Schema as
      `anyOf: [{required: [schema:instrument]}, {required: [schema:object]}, {required:
      [schema:actionProcess]}]`, and in the SHACL, where it replaces the `prov:used` `minCount 1`
      Violation;
  - measured 2026-11-11 over the examples, counting migrated wrappers and the TAPP link as their new
    properties:
    - CDIF: 1 of 138 activities has none of the three
      (`profile-manifest/examples/tof-htk9-f770-test.json`);
    - geochem: 1 of 391 (`STEM/detail/exampledetail-P1.json`).
  - The 8 CDIF activities without `schema:Action` are in cdifCore, discovery and manifest examples,
    which are not cdifProvActivity documents and are unaffected;
  - remove its `prov:used` pin;
  - add the `schema:instrument` kinds from §4.3;
  - document in `schema:actionProcess` that the `objectReference` form is the link to the plan the
    activity followed, and the inline `HowTo` is the procedure as performed (§4.4, option A);
  - add `schema:isBasedOn` (a sealed `objectReference`) to its `HowTo` definition, for a run that
    has both a plan and an inline procedure (§4.4).

  A `prov:used` the record carries is accepted when it passes the core shape (strings and `@id`
  references), and is checked by nothing more. cdifProvActivity does not close it off after migration
  (decided 2026-11-11). A wrapper fails the core shape, so the old form is still rejected.
- **`provProperties/provActivity`** (`allOf` generatedBy, as now): narrows each `prov:used` item to a
  string, an `{@id}`, or an inline `prov:Entity` that carries its `@id`. No wrappers.
- **`profiles/cdifProfile/cdifCore`:** no change. `$defs/GeneratedBy` keeps pointing at generatedBy,
  which now *is* the core definition.

Each layer only adds constraints (`@type` types, properties, a narrower `prov:used` item shape), so
`allOf` composes in the one direction it can.

### 4.6 Keeping the PROV reading (deferred)

**Deferred 2026-11-11:** this is not addressed now. The PROV implementation has to be settled first.
The text below records the idea for later.

Without `prov:used`, a PROV-only consumer no longer sees what an activity used. Declare, in the CDIF
ontology register or the profile context documentation:

```turtle
schema:instrument rdfs:subPropertyOf prov:used .
schema:object     rdfs:subPropertyOf prov:used .
```

With RDFS entailment, that restores `prov:used` with no change to the JSON. `schema:object` is
arguably closer to `prov:used` than an instrument is; state both or only `schema:object`, as the
group prefers.

## 5. Impact on CDIF

| where | change |
|---|---|
| mBB `generatedBy` (reverted to the core definition), `cdifProvActivity`, `provActivity`, `instrument` | §4; `cdifCore` itself unchanged |
| every CDIF core record | `prov:used` items must be a string or carry `@id`, and `@type` must be an array. Of the CDIF examples (§2), the 93 `prov:used` objects without `@id` would fail. Stored records are not yet measured |
| mBB resolved schemas and examples | regenerate |
| ddeBuildingBlocks | kept aligned (decided 2026-11-11): `DDEproperties/ddeImagery/schema.yaml` and 2 example files use `prov:used` |
| profile-provenance | `provenanceRules.shacl`: the `prov:used` `minCount 1` Violation becomes "has `schema:instrument`, `schema:object` or `schema:actionProcess`", plus `schema:Action` in `@type` (§4.5); examples; the Galaxy and WRROC converters; CLAUDE.md modelling conventions |
| validation repo | `FrameAndValidate` frame and `REFERENCE_ONLY_KEYS`; `detect_conformance` (cdifProvActivity detection keys on `prov:used`) |
| other code under `C:\GithubC\CDIF` that reads or writes `prov:used` | converters (croissant, DCAT, DDI, DDI-CDI, FAIR2), `cdifnexmetadata` `emit.py` and tests, copies of `FrameAndValidate.py` in `cdif-umlmodel` and `cdif-xas-UKDS` (search was cut off at 10 hits; list incomplete) |

## 6. Sequence

**One version (decided 2026-11-11).** There is no formal provenance release yet, so CDIF recognizes
only one version, and there is no transition period in which both forms are accepted. An instance
document still in the superseded form is migrated, not supported.

**Order.** No published schema should reject records that nobody has migrated yet.
geochemBuildingBlocks followed this rule when it closed off `prov:reagent`.

1. **Settle the schemas.** Agree the updated mBB blocks (§4), geochemBaseProfile and tappDefinition
   (§8), and the dde blocks, and have them reviewed. Nothing is published yet.
2. **Measure** every store and example set for the `prov:used` item shapes in §2, the inline-TAPP form
   (§8), and activities that would fail the new requirements.
3. **Migrate** the ADA production stores and the examples in every repo to the new form, as soon as
   step 1 is settled.
4. **Re-measure.** Confirm zero old-form items everywhere.
5. **Publish** the updated schemas together:
   - mBB first, published to gh-pages, since downstream repos resolve mBB refs from there;
   - then geochem, dde and the `profile-*` release repos.
6. **profile-provenance and validation.** SHACL, conformance detection, converters, sync.

## 7. Open questions (CDIF)

1. ~~Software and reagents: `schema:instrument` kinds, or direct `bios:` properties?~~ **Decided
   2026-11-11: `schema:instrument` kinds** (§4.3).
2. ~~The Wikidata term for the reagent kind.~~ **Decided 2026-11-11: `wd:Q2356542`** (chemical
   reagent).
3. ~~After migration, accept or reject `prov:used`?~~ **Decided 2026-11-11: accept** a `prov:used`
   that passes the core shape (§4.5).
4. ~~Core `prov:used` reference branch: open or sealed `{@id}`?~~ **Decided 2026-11-11: open** (§4.5).
5. ~~The plan link (§4.4): (A), (B) or (C)?~~ **Decided 2026-11-11: (A)**. Keep both
   `schema:actionProcess` forms for now; the reference form is documented as the plan link.
6. ~~`schema:additionalProperty` on cdifProvActivity: keep it as a known validator warning, or
   replace it?~~ **Decided 2026-11-11: keep it, as a known warning.**
   - Schema.org does not define it on Action (§3), so validator.schema.org warns.
   - It is how a run records its parameter values, and schema.org has no Action property for those.
   - It is widely used. Counted 2026-11-11: 69 activities in 13 CDIF example files, mostly Galaxy tool
     parameters; and 178 activities plus 165 `actionProcess` steps in the geochem examples.
   - cdifProvActivity's `schema:additionalProperty` description should say the warning is expected.
7. **Decided 2026-11-11: instrument kinds are told apart by `schema:additionalType`.** The Wikidata
   term is required in every `schema:instrument` item described in place (§4.3).
8. **Decided 2026-11-11: `schema:instrument` accepts `{@id}` references** to things described
   elsewhere (§4.3).
9. **Decided 2026-11-11: what a cdifProvActivity requires.** `@type` must contain `schema:Action`,
   and the activity must have at least one of `schema:instrument`, `schema:object` or
   `schema:actionProcess` (§4.5).
10. **Deferred 2026-11-11: the PROV mapping** (§4.6), until the PROV implementation is settled.
11. **Decided 2026-11-11: one version.** No transition period; superseded instances are migrated
    (§6).
12. **Decided 2026-11-11: ddeBuildingBlocks is kept aligned** (§5).

## 8. geochemBuildingBlocks only: TAPPs and ADA records

None of this section is part of CDIF. It records how geochem would adopt §4.

**Facts:**

- geochemBaseProfile **requires** `prov:used`, and pins each role with a constraint-only `if/then`.
  It also closes off two superseded spellings (bare `@type: ada:TAPPDefinition`, and `prov:reagent`)
  after measuring them at zero in the production stores.
- The TAPP plan (`tappDefinition`) and its `WorkflowStep`s currently carry `schema:instrument`,
  `bios:computationalTool` and `bios:reagent` as **direct** properties. They move to the §4.3 kinds;
  see "Other geochem changes" below. The TAPP is typed `prov:Plan`,
  `cdi:Activity`, `schema:Action`, `ada:TAPPDefinition` and `bios:LabProtocol`. It is **not** a
  `schema:HowTo`; its workflow is a HowTo inside its own `schema:actionProcess`.
- `tappDefinition`'s `ComputationalTool` is typed `schema:SoftwareApplication`. Its `Reagent` is typed
  one of `schema:DefinedTerm`, `schema:Product` or `schema:ChemicalSubstance`, with `ada:reagentRole`.
  Both fit the §4.3 kinds; `ada:reagentRole` and `ada:toolRole` stay as geochem additions.
- geochemBaseProfile's comments cite 7,447 ADA records (measured 2026-10-24) whose TAPP link was
  migrated to `ada:tappDefinition`, so this is a production migration, not an example edit.
- 216 geochem example activities carry an inline `schema:actionProcess` `HowTo` (the technique detail
  profiles). None of the 68 activities with an `ada:tappDefinition` link also has one.

**The TAPP link becomes the CDIF plan link (§4.4, option A):**

```json
"schema:actionProcess": {"@id": "ex:capdTAPP-P0"}
```

This replaces the `{"ada:tappDefinition": {...}}` wrapper.

**Inline TAPPs: none in production.** The CDIF plan link is reference-only, which would drop today's
inline-TAPP form. I measured the stores on 2026-11-11, read-only, over `json_table.jsonobject`:

| store | records | TAPP link by reference | inline TAPP | bare `@type` form | no TAPP link |
|---|---|---|---|---|---|
| ada2 | 7,447 | 7,363 | 0 | 0 | 84 |
| ada_subjects | 7,447 | 7,363 | 0 | 0 | 84 |

All 68 example links are references too. So nothing uses the inline form, and it can be dropped
without migration. The "about 184" in the earlier draft came from a pre-migration figure in
geochemBaseProfile's comments, and doesn't describe the stores today.

The 84 records without a TAPP link declare `geochemProduct` plus a legacy profile: `adaLAF` 28,
`adaICPOES` 15, `adaToFSIMS` 4, and the rest `adaProduct` only.

**Stored records do not use the wrappers at all.** Every one of the 7,447 activities, in both stores,
has the same keys:

- `@type`;
- `prov:used`, with one inline instrument as a plain item (not in a `schema:instrument` wrapper),
  typed `schema:Thing`, `schema:Product`, `prov:Entity` and `nxs:base_classes/NXinstrument.html`;
- `schema:object`;
- the location, times and identifier;
- in some records, technique fields such as `ada:edsDeadTime`.

No stored record has a computational tool or reagent. For the new form, the migration must:

- move the instrument from `prov:used` to `schema:instrument`;
- add `wd:Q3099911` to its `schema:additionalType`. None of the 7,447 has it; they carry only the
  NeXus class;
- give it an `@id`. None has one, although the geochem instrument block already requires it;
- turn `{"ada:tappDefinition": {"@id": …}}` into the plan link.

**method_registry** (`method_definitions.definition`, 511 TAPPs):

- 0 have the `schema:HowTo` type yet;
- at the plan level: 133 `bios:computationalTool` entries and 1 `bios:reagent`;
- on steps: 2 `bios:computationalTool` and 106 `bios:reagent`.

All of these move to `schema:instrument`. geochem may then add an `if/then` saying a referenced plan
must be a TAPP, but JSON Schema cannot check that from an `{@id}` alone; SHACL can, when the TAPP is
in the graph.

Two geochem-only issues:

- **Range: the TAPP gets the `schema:HowTo` type (decided 2026-11-11).** `schema:actionProcess` ranges
  over `schema:HowTo`, so `tappDefinition`'s `@type` gains a required `schema:HowTo`, alongside
  `prov:Plan`, `schema:Action`, `ada:TAPPDefinition` and `bios:LabProtocol`. `cdi:Activity` is
  dropped; see "Other geochem changes" below.
  - This means changing the `allOf contains` list. `minItems` stays 5, since one type is added and
    one removed.
  - The TAPPs in method_registry, and the TAPP examples, then need the type added; they are migrated
    before the schema requires it.
  - The TAPP keeps its own `schema:actionProcess` workflow `HowTo`. A node that is both an Action and a
    HowTo is allowed by schema.org, and the plan link points at the TAPP itself.
- **Collision with inline `HowTo`s: open, needs worked examples.** At the analysis tier, a dataset
  description needs **both**:
  - a link to the TAPP (the plan);
  - an `actionProcess` documenting the values this run gave the editable properties the plan allows.

  Under (A), one `schema:actionProcess` holds the TAPP link *or* an inline procedure, not both. Today
  the 216 detail-profile activities carry only the inline procedure, and the 68 TAPP-linked
  activities carry only the link.

  **Decided 2026-11-11: (i).** When the run has a procedure, `schema:actionProcess` is the run's
  inline `HowTo`, and that HowTo points to the TAPP with `schema:isBasedOn`. When it has none,
  `schema:actionProcess` is the bare `{@id}` link to the TAPP, which is valid because the TAPP is
  typed `schema:HowTo`. One query finds the TAPP in both cases (tested with rdflib):

  ```sparql
  ?ds prov:wasGeneratedBy/schema:actionProcess/schema:isBasedOn? ?tapp . ?tapp a ada:TAPPDefinition .
  ```

  Each value in the run's procedure names the TAPP parameter it sets, through `schema:propertyID` →
  the TAPP's `PropertyValueSpecification` `@id`. So the TAPP parameters need stable `@id`s.

  Worked examples of all three candidates are in [tapp-link-candidates/](tapp-link-candidates/): the
  TAPP `tapp-icpms-demo-v1.json`, then `analysis-i-isBasedOn.json` (chosen),
  `analysis-ii-array.json` and `analysis-iii-hadPlan.json`. Each record parses with no triple
  dropped. With the TAPP loaded, each yields the TAPP link and the three editable-parameter values.
  The difference is only in the path: in (ii), `actionProcess` returns both the TAPP and the run's
  HowTo, so a consumer has to tell them apart by type.

  The candidates as written:
  - **(i)** `schema:actionProcess` is the inline `HowTo` of this run, and that HowTo carries
    `schema:isBasedOn` → `{@id: TAPP}`. `isBasedOn` is a CreativeWork property, and HowTo is a
    CreativeWork, so this is valid schema.org. The plan is then reached through the procedure.
  - **(ii)** `schema:actionProcess` takes an array: `[{@id: TAPP}, {inline HowTo}]`. This needs CDIF to
    allow an array there, and a consumer tells the two apart by shape.
  - **(iii)** the qualified `prov:hadPlan` from §4.4 (C) for the plan, with `actionProcess` kept for
    the run's procedure.

  (i) leaves the CDIF decision (A) untouched; (ii) and (iii) would have revisited it.

**Other geochem changes:**

- `geochemBaseProfile`:
  - replace the `prov:used` pins with `schema:instrument` kind pins;
  - drop `required: prov:used`, and rely on the CDIF rule: at least one of `schema:instrument`,
    `schema:object` or `schema:actionProcess` (revised 2026-11-11, replacing the earlier
    instrument-or-actionProcess rule).
    - Measured over the examples: 1 of 391 activities has none of the three
      (`STEM/detail/exampledetail-P1.json`).
    - The technique `detail/exampledetail-P0.json` placeholders pass on their `schema:object`, but
      their activities have no `@type`, so they still fail the `schema:Action` requirement;
  - after migration, add "then use `schema:instrument`" rules and close off the old wrappers, with
    counterexamples that name the new key.
- `tappDefinition`, at the plan level and in `WorkflowStep`:
  - move `bios:computationalTool` and `bios:reagent` into `schema:instrument`, as the software and
    reagent kinds of §4.3;
  - `ComputationalTool` and `Reagent` become the kind pins, adding `wd:Q7397` and `wd:Q2356542` to
    their `schema:additionalType`. `ada:toolRole` and `ada:reagentRole` stay.
  - The plan-level `schema:instrument` is "an Instrument, or an array of Instruments". It becomes an
    array whose items are pinned by kind. The step-level form, "an Instrument or an `{@id}`", keeps
    its `{@id}` branch.
  - Update the descriptions that say a plan's tools and reagents are direct `bios:` properties.
  - Counted 2026-11-11 over the geochem JSON outside the resolved schemas: 97 files, with 98
    computational tools and 6 reagents at the plan level, and 4 tools and 48 reagents on steps. The
    TAPPs in method_registry need the same migration; geochemBaseProfile's comments cite
    `bios:reagent` in 72 of 500 stored TAPP plans.
- **Drop `cdi:Activity` from the TAPP and its steps; keep `schema:Action` for now (decided
  2026-11-11).**
  - *Why:* no TAPP or step carries any DDI-CDI process property (no step links, parameters, sequence
    or names), so the type promises structure a DDI-CDI consumer will not find. In our DDI-CDI test
    example, `cdi:Activity` is also the class of the *run*, which is a different thing from a plan. If
    DDI-CDI alignment is wanted later, it belongs in a proper DDI-CDI serialisation.
  - *Schema:* the TAPP `@type` becomes `prov:Plan`, `schema:Action`, `ada:TAPPDefinition`,
    `bios:LabProtocol` and `schema:HowTo` (`minItems` 5, with `schema:HowTo` added and `cdi:Activity`
    removed). `WorkflowStep` becomes `schema:Action` and `schema:HowToStep` (`minItems` 2).
  - *Also touches:* `tools/build_tapp_examples.py`, `tools/build_laicpms_examples.py`,
    `tools/_tapp_lib.py`, `tools/schema_path_example_emitter.py`, `docs/counterexamples.json` and
    `docs/SCHEMA_PATH_GRAMMAR.md`. All of them emit or mention `cdi:Activity`.
  - *Counted 2026-11-11:*
    - examples: 253 TAPP nodes and 570 TAPP steps;
    - method_registry: all 511 TAPPs and 1,041 steps.
  - **Open:** 455 more `cdi:Activity` nodes in the examples are *outside* any TAPP. These are mainly
    the run-procedure steps under a run's `schema:actionProcess`, which geochemBaseProfile's own
    `WorkflowStep` requires to carry `cdi:Activity`; the example added in geochemBuildingBlocks#273
    is one of them. For consistency they would drop it too, but this decision covered only the TAPP.
- The geochem instrument's inline `schema:hasPart` component requires both `schema:Product` and
  `schema:Thing`; relax it as in §4.1.
- Migrate by script, then regenerate:
  - the 316 example files (58 `schema.yaml` files also mention `prov:used`; review each technique
    profile);
  - the `compositionQC` module and its schemapaths CSV;
  - `schema_path_emitter.py`, `normalize_schema_paths.py`, `docs/SCHEMA_PATH_GRAMMAR.md` and
    CLAUDE.md.
- **Production.** Migrate ada2, ada_subjects and method_registry as soon as the updated schemas are
  settled (decided 2026-11-11). Measure each `prov:used` item shape and the inline-TAPP form first, and
  re-measure before publishing.
  - This needs database access. The repo's database tools, such as
    `tools/check_migration_readiness.py`, need `requirements-db.txt` and a connection, and are not
    run in CI.
  - So whoever holds the store credentials triggers the migration. The migration and measurement
    scripts can be written and reviewed in the repo beforehand.

**geochem questions:**

1. ~~TAPP range: add `schema:HowTo` to the TAPP, or link to its workflow HowTo?~~ **Decided
   2026-11-11: the TAPP gets the `schema:HowTo` type.**
2. ~~Should the TAPP plan and its steps also move `bios:computationalTool` and `bios:reagent` into
   `schema:instrument`?~~ **Decided 2026-11-11: yes.** The plan, its steps and the run all use the
   §4.3 kinds, so they match key for key.
3. ~~`schema:additionalProperty` on TAPP steps has the same domain problem as §3.~~ Follows CDIF
   question 6: **keep it, as a known warning.**
4. ~~Can inline TAPPs be dropped?~~ **Measured 2026-11-11: 0 in ada2 and in ada_subjects**, so
   yes, with no migration.
5. ~~How does an analysis-tier activity carry both its TAPP link and its run procedure?~~ **Decided
   2026-11-11: (i)**, the run's HowTo points to the TAPP with `schema:isBasedOn`.
6. ~~What replaces `required: prov:used`?~~ **Decided 2026-11-11:** the CDIF rule, at least one of
   `schema:instrument`, `schema:object` or `schema:actionProcess`.
7. ~~When are the ADA stores migrated?~~ **Decided 2026-11-11:** as soon as the updated schemas are
   settled, triggered by whoever holds the store credentials.
