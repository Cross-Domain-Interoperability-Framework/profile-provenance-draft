# Scenario: a computational workflow run

The second scenario of the provenance-approach comparison (the first is the Dagstuhl quantitative
scenario in [APPROACHES.md](APPROACHES.md)). It is written first in cdifProv and mapped from there;
[MAPPING.md](MAPPING.md) has the construct-by-construct table.

## The story

On 23 October 2024 an analyst ran the Galaxy workflow *FeS2 Analysis* on two inputs: a
room-temperature Fe K-edge absorption spectrum of FeS2 (pyrite) and the crystal structure of
FeS2 as a CIF file. Galaxy 24.1 ran four Larch tools (0.9.75+galaxy0):

1. **Normalize the absorption spectrum** (larch_athena), from the spectrum, with its pre-edge and
   normalization ranges; it produced an Athena project and a plot.
2. **Compute scattering paths from the structure** (larch_feff), from the CIF, for the first Fe
   atom within 4 Å; it produced the FEFF output.
3. **Select the paths to fit** (larch_select_paths), from the FEFF output: three paths, chosen by
   hand, with their starting S02, E0, ΔR and σ²; it produced the fit variables and the paths.
4. **Fit the paths to the spectrum** (larch_artemis), from the Athena project, the FEFF output and
   the selected paths, in R space with a Kaiser window; it produced the fit report and two plots.

Steps 1 and 2 are independent; step 3 needs step 2, and step 4 needs steps 1 to 3. The record
describes the fit results (the report and the plots) and how they came to be.

## Where it comes from, and what is illustrative

It is based on the Galaxy run in [`../examples/FeS2-Analysis.actions.cdifprov.json`](../examples/FeS2-Analysis.actions.cdifprov.json)
(from the crate in `examples/ROCRATE/FeS2-Analysis.rocrate.json`): the workflow name, the four
tools and their versions, the input and output file names, the parameter values and the step
times are that run's. Three things are changed, because that file cannot be mapped as it is:

- **The wiring is corrected.** The converted file attaches the right tool and parameters to each
  step but the wrong inputs and outputs: the fitting step's outputs sit on the FEFF step, and one
  step reads outputs no step produces. The steps here have the inputs and outputs those tools take
  and make, in the order an EXAFS fit runs. That looks like a fault in
  `tools/galaxyROCrateToCDIFActions.py`'s input/output mapping, not yet confirmed.
- **The parameters are flat `schema:PropertyValue`s.** In the converted file they are nested
  `schema:StructuredValue`s whose keys (`pre_edge`, `pre1`, ...) have no prefix and no `@vocab`, so
  JSON-LD drops them: none of them reaches RDF, PROV-O or an RO-Crate. Here each is a name, a
  numeric value, a unit where there is one, and its Galaxy parameter path as `schema:propertyID`.
- **The inputs have one identifier each.** In the converted file the run's input and the step's
  input are two different `@id`s for the same file.

**Invented:** the analyst (Sam Rivera, an ORCID-shaped placeholder), the dataset's DOI, the file
descriptions, and the run's end time (the converted file's run ends before its steps start; here it
ends with the last step).

## Files

| approach | file | how it was made | checked with |
|---|---|---|---|
| **cdifProv** (master) | [cdifprov-schemaorg/cdif\_provenance\_workflow.json](cdifprov-schemaorg/cdif_provenance_workflow.json) | hand-written: one activity whose `schema:actionProcess` HowTo has the four steps as `[schema:HowToStep, schema:Action]` | `FrameAndValidate.py -v` against cdifProvenance 2.0: passes; conformance consistent (core 2.0, provenance 2.0); 297 triples, all kept by framing; `provenanceRules.shacl` (advanced): 0 violations, 0 warnings, 1 info (the person has no contact point); key counts = triple counts |
| **PROV-O, qualified** | [prov-o-qualified/cdif\_provenance\_workflow.ttl](prov-o-qualified/cdif_provenance_workflow.ttl), [.jsonld](prov-o-qualified/cdif_provenance_workflow.jsonld) | generated: `python tools/cdifProvToProvO.py <cdifProv> <out.ttl>` | 377 triples: 14 usages, 9 generations, 1 association with its plan, 4 steps in the run's `dcterms:hasPart`; the tree is isomorphic under rdflib and pyld |
| **PROV-O, plain** | [prov-o-unqualified/cdif\_provenance\_workflow.ttl](prov-o-unqualified/cdif_provenance_workflow.ttl), [.jsonld](prov-o-unqualified/cdif_provenance_workflow.jsonld) | generated: the same with `--unqualified` | 312 triples: 14 `prov:used`, 9 `prov:wasGeneratedBy` + `prov:generatedAtTime`, 1 `prov:wasAssociatedWith`. The tool's `--unqualify` reproduces the quantitative scenario's plain file exactly (isomorphic, 124 triples) |
| **RO-Crate, Provenance Run Crate 0.5** | [ro-crate/cdif\_provenance\_workflow/ro-crate-metadata.json](ro-crate/cdif_provenance_workflow/ro-crate-metadata.json), [tree](ro-crate/cdif_provenance_workflow.jsonld) | written from the cdifProv file | 65 entities, no duplicate or dangling `@id`s within the crate; 376 triples; the tree is isomorphic. `rocrate-validator` 0.14.0, `-p provenance-run-crate-0.5 -m` (metadata only): every REQUIRED check passes; 13 RECOMMENDED checks fail, listed below |

The RECOMMENDED checks the crate fails either need facts the cdifProv file does not hold, or come
from its `example.org` IRIs. None was filled in with invented values:

- **Facts the cdifProv file does not hold:**
  - the workflow file's `url`, `version` and `encodingFormat`, and its Bioschemas
    ComputationalWorkflow conformance (inputs and outputs as `FormalParameter`s, a creator);
  - a `description` on each step;
  - the crate's `author` and `publisher`;
  - a `README.md`.
- **From the `example.org` IRIs:** each data entity is web-based, so it is flagged as unavailable
  (12 entities), and each file as lacking `contentSize` and `sdDatePublished` (11 files).
- **A trailing `/` on the described dataset's IRI:** RO-Crate treats a `Dataset` data entity as a
  directory, and recommends its IRI end in `/`. The IRI is kept, so the files can be loaded together.

To meet the profile, the crate generator makes three changes to the cdifProv values:

- **Times:** Process Run Crate wants milliseconds and an offset, so the times are cut to
  milliseconds with `+00:00` added. Galaxy records naive UTC.
- **actionStatus:** it stays the string `http://schema.org/CompletedActionStatus`, which is what the
  profile's shape accepts.
- **Arrays:** singleton arrays are written as single values.

The described dataset (`ex:fes2FitResults`) keeps its own IRI, as in the minimal scenario: it is a
`Dataset` data entity in the root's `hasPart`, with the three result files as its `hasPart`, and the
run's `CreateAction` lists it in `result` with those files.

The crate also adds three things the cdifProv file only implies:

- each step's agent, which is the run's agent;
- each tool's Tool Shed page, derived from its tool id, as its `url`;
- the step actions in the root's `mentions`.

All files use the cdifProv file's IRIs (`https://example.org/cdif-prov/…`), so they can be loaded
together.

## Findings

- **A HowTo step cannot take an activity type.** On an activity, `schema:additionalType` holds
  `{@id}`s, so a CDIF activity-vocabulary IRI works; on a `schema:HowToStep` the schema types it as an
  array of strings, so the same IRI would be a literal. The steps here have no activity type; the
  run's is `cdifact:Analysis`.
- **PROV-O has nowhere for the procedure as performed.** The steps become activities that are part of
  the run, and the plan (`schema:isBasedOn`) becomes `prov:hadPlan`; the HowTo itself, its name and
  its description, have no counterpart.
- **A plan needs an agent in PROV-O.** `prov:hadPlan` sits on a `prov:Association`, which needs a
  `prov:agent`. The run has one; a step with a plan and no agent could not keep it.
- **Software is used, not responsible.** CDIF records a tool as a step's `schema:instrument`, so it
  maps to a usage with the role `ex:Software`. PROV-O's own reading would make each tool a
  `prov:SoftwareAgent` associated with its step (as the quantitative master does for its analysis
  software); the mapping keeps CDIF's.
- **RO-Crate separates plan from execution more than cdifProv does.** Each step is a `HowToStep` of
  the workflow and a `CreateAction`, joined by a `ControlAction`; the Galaxy engine's run is an
  `OrganizeAction` whose result is the workflow run. cdifProv folds the plan step and its execution
  into one `[schema:HowToStep, schema:Action]` node, and names the engine as one more instrument.
