# Scenario: a qualitative assessment

A finding made by human judgement, with no instrument and no software. It is the 2026 Dagstuhl
"qualitative" scenario: a free-text response is processed, coded and synthesized into a theme,
and the theme is validated. It is written first in cdifProv and mapped from there;
[MAPPING.md](MAPPING.md) has the construct-by-construct table.

## The story

1. **Text processing.** On 5 November 2026, from 09:00 to 09:10 UTC, Researcher A cleaned a
   submitted response and split it into segments, following a processing guide.
2. **Coding.** Researcher A coded a response segment with version 2 of the codebook.
3. **Two activities use the codes:**
   - **theme development:** Researcher A synthesized the codes into theme 01, following an
     analytical framework;
   - **coding uncertainty assessment:** Researcher B coded the segment independently, and the
     agreement between the two codings is the coding uncertainty.
4. **Validation.** Researcher B checked the theme against the coded data, taking the coding
   uncertainty into account, and accepted it. The outcome is the record's dataset.

The record:

- **The activities are not one chain.** They are the five activities in `prov:wasGeneratedBy`,
  linked by `@id`: the code assignment is an input of two activities, and the validation takes
  the results of both. This is the first scenario whose activities branch and join.
- **No instruments.** No activity has a `schema:instrument`. Each has a `schema:object`, which is
  what the schema requires when there is no instrument or procedure.
- **Plans, three ways:**
  - the processing guide and the analytical framework are `schema:actionProcess` `{@id}`s;
  - the coding has an inline HowTo of three text steps, which names the codebook in
    `schema:isBasedOn`;
  - the assessment and the validation follow no named plan.
- **Agents:** every activity has a `schema:agent` that is a `schema:Role`. The role is a string
  (data processor, coder, analyst, assessor, validator), not a vocabulary term.
- **A quality result:** the coding uncertainty carries the inter-coder agreement as a
  `schema:additionalProperty` value (Cohen's kappa 0.78).
- **Types:** each activity has a CDIF activity term, such as `cdifact:DataClassificationAndCoding`,
  and keeps the source's own `ex:` types. Each entity keeps its `ex:` types, such as `ex:Theme`
  and `ex:Finding`.

## Where it comes from, and what is illustrative

It is based on [`../examples/cdif_provenance_qualitative.jsonld`](../examples/cdif_provenance_qualitative.jsonld),
a PROV-O JSON-LD tree. These are that file's:
- the five activities, their order and their types;
- the entities and their types;
- Researcher A and the roles in the first three activities;
- the three plans;
- the text-processing times.

**Invented:**

- **Researcher B**, as the agent of the assessment and the validation. The source names no agent
  for them, and the profile's SHACL warns when an activity has none. A second, independent coder is
  how coding uncertainty is usually measured.
- **The names, descriptions and email addresses.** The source has `@id`s and types only.
- **The coding's HowTo steps and its coding-unit parameter.**
- **The agreement value**, and that the validation accepted the theme.

**Changed:** the entities are `schema:Thing`s, not `schema:CreativeWork`s. The profile's SHACL
warns when a `CreativeWork` has no `schema:url`, and these intermediate results have none. Until
metadataBuildingBlocks#112 that was a Violation.

## Files

| approach | file | how it was made | checked with |
|---|---|---|---|
| **cdifProv** (master) | [cdifprov-schemaorg/cdif\_provenance\_qualitative.json](cdifprov-schemaorg/cdif_provenance_qualitative.json) | hand-written | `FrameAndValidate.py -v` against cdifProvenance 2.0: passes; conformance consistent (provenance 2.0; not core 2.0, since the source gives the result no identifier); 149 triples, all kept by framing; `provenanceRules.shacl` (advanced): conforms, no results; key counts = triple counts |
| **PROV-O, qualified** | [prov-o-qualified/cdif\_provenance\_qualitative.ttl](prov-o-qualified/cdif_provenance_qualitative.ttl), [.jsonld](prov-o-qualified/cdif_provenance_qualitative.jsonld) | generated: `python tools/cdifProvToProvO.py <cdifProv> <out.ttl>` | 172 triples: 5 activities, 5 generations (the dataset only by the validation), 6 usages, 5 associations (3 with a plan); the tree is isomorphic under rdflib and pyld |
| **PROV-O, plain** | [prov-o-unqualified/cdif\_provenance\_qualitative.ttl](prov-o-unqualified/cdif_provenance_qualitative.ttl), [.jsonld](prov-o-unqualified/cdif_provenance_qualitative.jsonld) | generated: the same with `--unqualified` | 120 triples; the plans and roles are lost; the tree is isomorphic |
| **RO-Crate 1.1** | [ro-crate/cdif\_provenance\_qualitative/ro-crate-metadata.json](ro-crate/cdif_provenance_qualitative/ro-crate-metadata.json), [tree](ro-crate/cdif_provenance_qualitative.jsonld) | written from the cdifProv file | 27 entities; 137 triples; the tree is isomorphic. `rocrate-validator` 0.14.0, `-p ro-crate-1.1 -m` (metadata only): every REQUIRED check passes; 4 RECOMMENDED checks fail, listed below |

**The crate** is plain RO-Crate 1.1:
- each activity is a `CreateAction` in the root's `mentions`;
- a Role agent becomes its agent, and the role is lost;
- the three plans are `HowTo` entities with no properties.

Process Run Crate would also fail here: it requires every action to have a software instrument,
and these actions have none.

The 4 RECOMMENDED failures, none filled in with invented values:

- **The crate's `author` and `publisher`:** the cdifProv record names neither.
- **A trailing `/` on the dataset's IRI:** RO-Crate recommends it for a `Dataset`. The IRI is kept.
- **The `example.org` dataset:** it is flagged as unavailable.

## The PROV-O against the source

The source is itself qualified PROV-O. The generated file has the same activities, generations,
plans and agents, and these differences:

- **No derivations.** The source has four `prov:wasDerivedFrom`, and a qualified derivation that
  names the activity. cdifProvenance has no derivation, so none of the four forms says that the
  theme is derived from the codes.
- **No attribution.** The source attributes the codes and the theme to Researcher A
  (`prov:wasAttributedTo`). cdifProv has only the activity's agent.
- **Plans are only plans.** In the source, each plan is also a used entity, with its own role
  (`ex:CodingSpecification`, …). In cdifProv a plan is the activity's `schema:actionProcess` or a
  HowTo's `schema:isBasedOn`, so it becomes `prov:hadPlan` only.
- **One input role.** The source's input roles (`ex:SourceResponse`, `ex:AnalyticalInput`) become
  `ex:InputData`, because `schema:object` has no role.
- **Entity types are annotations.** The source's `rdf:type`s on entities (`ex:Theme`, …) come out as
  `schema:additionalType` values, which the tool copies but does not turn into types. Activity
  types are turned into types.

## Findings

- **A join and a branch need nothing new.** The tool's chain rule (the root is generated only by an
  activity whose results no other listed activity uses) picks the validation alone, so the root has
  one generation.
- **A quality result has no slot.** The agreement value is a `schema:additionalProperty` on the
  coding uncertainty, an annotation in every form. Nothing links it to a quality metric, the gap
  APPROACHES.md already lists under the draft profile's quality provisions.
- **A role from a vocabulary is optional.** The roles here are strings, and the tool mints `ex:`
  roles from them. A `schema:DefinedTerm` (as in the lab-measurement scenario) would carry a term
  set.
- **The profile's SHACL asks for a `schema:url` on every `schema:CreativeWork`.** The shape
  (`cdifd:CDIFLabeledLinkShape`) is meant for labeled links, but it targets the class, so it also
  applies to an intermediate result typed `CreativeWork` with no URL. The results here were typed
  `schema:Thing` because that was a Violation. Since metadataBuildingBlocks#112 it is a Warning, so
  a `CreativeWork` without a URL now passes, with a warning.
