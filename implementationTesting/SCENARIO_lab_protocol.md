# Scenario: a laboratory protocol with sub-protocols

A laboratory analysis that followed a protocol made of sub-protocols, recorded as one activity whose
procedure has a step for each sub-protocol. Each step has a sub-procedure of its own, and two of
them list their sub-steps. It is written first in cdifProv and mapped from there; [MAPPING.md](MAPPING.md) has
the construct-by-construct table. The other scenarios are [the computational workflow](SCENARIO_workflow.md)
and [the minimal record](SCENARIO_minimal.md).

## The story

On 21 November 2023, NASA Goddard Space Flight Center analysed about 1 mg of Bennu asteroid
sample OREX-803003-0 by pyrolysis-GC-MS/MS. The protocol has four parts, and the run did them in
order, each taking the previous one's product:

1. **Sample preparation.** The sample was loaded into a quartz tube, weighed, and placed in the
   pyrolysis oven. Its sub-procedure lists these three sub-steps.
2. **Flash pyrolysis** at 10 °C/ms to about 600 °C. Helium carried the volatiles through a 300 °C
   transfer line to the GC.
3. **GC separation** on an Rtx-5ms column, split 10:1. Its sub-procedure lists the oven program's
   three sub-steps: hold, ramp and hold.
4. **MS detection** on a TSQ triple-quadrupole: full scan and MRM for 38 compounds. It produced the
   data file, the CDF file the record describes.

The record:

- **The activity** is the analysis session, typed `cdifact:Measurement` and `bios:LabProcess`. Its
  agent is an organization.
- **The input** is the sample, in `schema:object`.
- **The procedure as performed** is the activity's `schema:actionProcess` HowTo. Its
  `schema:isBasedOn` names the protocol.
- **The steps** are that HowTo's four `[schema:HowToStep, schema:Action]` steps:
  - each has its own instruments, its input by `@id`, its product and its parameter values;
  - each parameter value names the protocol's formal parameter in `schema:propertyID`;
  - each has a `schema:actionProcess`, an inline HowTo whose `schema:isBasedOn` names the
    sub-protocol it followed;
  - two of those HowTos have text-only `schema:HowToStep` sub-steps.
- **The kinds:** the four devices are instruments (Wikidata Q3099911), and helium is a reagent
  (Q2356542).

## Where it comes from, and what is illustrative

It is based on [`../examples/Bennu-py-GC-MSarc.cdifprov.json`](../examples/Bennu-py-GC-MSarc.cdifprov.json).
These are that file's: the sample, the organization, the session and method identifiers, the
equipment, the intermediate products, the data file, the parameter values, the protocol and
sub-protocol identifiers, and the descriptions. That file records the run differently:

- **The run is five activities.** They are the session and its four parts, and each part names its
  sub-protocol as `schema:actionProcess`.
- **The protocol is described in place.** `bios:executesLabProtocol` holds a HowTo with its
  equipment, its formal parameters and its sub-protocols in `schema:hasPart`.

The source has to change in several ways to take the steps form:

- **Parameter values once each.** The source repeats each value in `bios:parameterValue` and
  `schema:additionalProperty`, and the session repeats three of its parts' values. Here each value
  is in `schema:additionalProperty` of its step only.
- **Equipment typed as instruments.** The source types the equipment `[schema:Thing,
  schema:DefinedTerm]`; here each device is a `schema:Product` with the instrument kind. The mass
  spectrometer's serial number moves from `schema:identifier` to `schema:serialNumber`.
- **No step times.** Every part in the source ends at `2023-11-21T00:00:00Z`, the instant the
  session starts, so the steps carry no times.
- **The oven program is a sub-procedure.** In the source it is a parameter value with a text value;
  here it is the GC step's three sub-steps.
- **Activity types on steps are left out.** A step's `schema:additionalType` is a string, so
  `bios:LabProcess` there would be a literal, not a type. The session keeps it.

**Added or changed:**

- **Added from the descriptions:**
  - helium as a reagent;
  - the sample-preparation sub-steps.
- **The sample mass:** given as `1` mg. The source has `~1`; the step's description keeps "about".
- **Text propertyIDs:** the two MS parameter values with no formal parameter in the protocol (ion
  source temperature, full scan time) name their property in plain text.
- **`cdifact:Measurement`:** the activity type is new; the source has only `bios:LabProcess`.

**Not declared:** core 2.0. The source gives the dataset no identifier, which core requires, so the
record declares provenance 2.0 only, as the source does.

## Files

| approach | file | how it was made | checked with |
|---|---|---|---|
| **cdifProv** (master) | [cdifprov-schemaorg/cdif\_provenance\_lab\_protocol.json](cdifprov-schemaorg/cdif_provenance_lab_protocol.json) | hand-written | `FrameAndValidate.py -v` against cdifProvenance 2.0: passes; conformance consistent (provenance 2.0); 233 triples, all kept by framing; `provenanceRules.shacl` (advanced): conforms, no results; key counts = triple counts |
| **PROV-O, qualified** | [prov-o-qualified/cdif\_provenance\_lab\_protocol.ttl](prov-o-qualified/cdif_provenance_lab_protocol.ttl), [.jsonld](prov-o-qualified/cdif_provenance_lab_protocol.jsonld) | generated: `python tools/cdifProvToProvO.py <cdifProv> <out.ttl>` | 270 triples: 5 activities (the session and its 4 steps, `dcterms:isPartOf` the session), 5 associations each with its plan (the protocol and the 4 sub-protocols), 12 usages (5 inputs, 5 instruments, 2 of the reagent), 5 generations (the data file by the session, which also lists it as its result, not by the detection step); the tree is isomorphic under rdflib and pyld |
| **PROV-O, plain** | [prov-o-unqualified/cdif\_provenance\_lab\_protocol.ttl](prov-o-unqualified/cdif_provenance_lab_protocol.ttl), [.jsonld](prov-o-unqualified/cdif_provenance_lab_protocol.jsonld) | generated: the same with `--unqualified` | 206 triples; the plans and roles are lost; the tree is isomorphic |
| **RO-Crate 1.1** | [ro-crate/cdif\_provenance\_lab\_protocol/ro-crate-metadata.json](ro-crate/cdif_provenance_lab_protocol/ro-crate-metadata.json), [tree](ro-crate/cdif_provenance_lab_protocol.jsonld) | written from the cdifProv file | 49 entities; 249 triples; the tree is isomorphic. `rocrate-validator` 0.14.0, `-p ro-crate-1.1 -m` (metadata only): every REQUIRED check passes; 6 RECOMMENDED checks fail, listed below |

The crate is plain RO-Crate 1.1, not a Process Run Crate.

- **Why not Process Run Crate:** it requires every action's `instrument` to be software. As a
  Process Run Crate, this crate fails that REQUIRED check on all five actions.
- **What it uses instead:** RO-Crate 1.1's own provenance pattern, a `CreateAction` whose
  `instrument` is the equipment that was used.
- **How each step is written:** as one entity typed `[HowToStep, CreateAction]`, as in cdifProv.
  The workflow crate splits a step into a `HowToStep` and a `CreateAction` joined by a
  `ControlAction`; that is Provenance Run Crate's pattern, for workflows.

The 6 RECOMMENDED failures, none filled in with invented values:

- **The crate's `author` and `publisher`:** the cdifProv record names neither.
- **A trailing `/` on the described dataset's IRI:** RO-Crate recommends it for a `Dataset`. The
  IRI is kept, so the files can be loaded together.
- **The two `example.org` data entities:** each is flagged as unavailable. The data file is also
  flagged for having no `contentSize` and no `sdDatePublished`.

The crate also carries five things differently from the cdifProv file:

- **Reagent:** helium is in each step's `object`, since a consumed reagent is an object of the
  action in RO-Crate.
- **actionProcess:** the term is added to the crate's `@context`, as in the minimal crate.
- **Plans:** the protocol and its sub-protocols are `HowTo` entities with no properties, because
  they are known only by reference.
- **Activity types:** the session keeps its activity types in `additionalType`.
- **Time offset:** the session's times use `+00:00` instead of `Z`.

## Findings

- **cdifProv 2.0 cannot hold the protocol itself.** `schema:isBasedOn` is a sealed `{@id}`
  reference, so the record names the protocol and its sub-protocols but cannot describe them. The
  source describes them in place; that information has nowhere to go:
  - the protocol's equipment list;
  - its formal parameters and their descriptions;
  - the fact that each sub-protocol is part of the protocol;
  - its method name ("Pyrolysis-GC-MS/MS").

  The parameter values keep a reference to their formal parameters, which nothing then describes.
- **A step cannot take an activity type.** The workflow scenario found this too: a HowTo step's
  `schema:additionalType` is a string, so `bios:LabProcess` cannot type a step.
- **PROV-O needs an agent for a step's plan.** `tools/cdifProvToProvO.py` now associates a step
  that has a plan but no agent with its activity's agent. Before, the four sub-protocols were lost.
- **PROV-O has no counterpart for the sub-procedures.** It keeps a sub-procedure's plan, but not
  the sub-procedure (the HowTo) or its text-only sub-steps. The tool now maps only steps typed
  `schema:Action` to activities; before, it also made activities of the six text sub-steps.
- **Process Run Crate is for software.** A laboratory process needs plain RO-Crate 1.1, and the
  crate cannot claim a run-crate profile.
