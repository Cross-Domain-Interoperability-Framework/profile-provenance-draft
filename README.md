# prov-context-quality

Properties for describing the origin of data, the situation of its creation, and assessment of data quality to inform use.

There is a related [Google drive](https://drive.google.com/drive/folders/1TGToyv72qedgMB5vr8ZImSdn79hH0TMc?usp=drive_link) that contains meeting notes and some other documents.

## Contents

### Documentation

- **[CDIFProvenanceImplementationGuide.md](CDIFProvenanceImplementationGuide.md)** — Implementation guide (auto-generated draft from the StructuredSchema; hand-curated content pending). Properties, classes, and conformance.
- **[ProvenanceOptions.md](ProvenanceOptions.md)** — Comprehensive comparison of provenance approaches available in CDIF: the three native building blocks (cdifProv, provActivity, ddicdiProv) and external RO-Crate-based profiles (WRROC, ARC). Covers property mappings, multi-step provenance patterns, and guidance for implementing ARC profile support in CDIF.
- **[agents.md](agents.md)** — Analysis of how agents (people, organizations, software) are represented across provenance vocabularies used in CDIF, with recommendations for consistent implementation.

### Semantic Resources

- **[PROV_Classes.ttl](PROV_Classes.ttl)** — PROV-based provenance classes as discussed at the Dagstuhl Workshop (November 2025), mapping DDI-CDI provenance activity types to W3C PROV-O. Includes editorial commentary on class naming conventions and agent modeling approaches.
- **[vocabularies/activityTypes.jsonld](vocabularies/activityTypes.jsonld)** — Draft SKOS vocabulary of activity types for workflow steps. The top layer is the 23 activity classes from the Dagstuhl workshop's ProvWork2025 Activity sheet (sampling, observing / measuring, data transforming, calibrating, archiving, ...), each a `skos:exactMatch` to its class in `PROV_Classes.ttl`. Under them sit the laboratory steps used in ADA TAPP plans: sample preparation (narrower: sample digestion, ion milling) under conditioning (intentional), instrument tuning under configuring, instrument calibration under calibrating, data acquisition under observing / measuring, data processing under data transforming, and quality control under quality controlling. A step is typed with one of these concepts through `schema:additionalType`, while its `schema:name` stays free to say what it specifically did (for example, a step named "Laser calibration" has type `at:instrumentCalibration`). Validates against the CDIF concept-scheme profile (JSON Schema and SHACL). Published as a Turtle copy ([activityTypes.ttl](vocabularies/activityTypes.ttl)), one JSON-LD and Turtle file per concept ([vocabularies/activityType/](vocabularies/activityType/)), and an HTML page rendered with the [iSamples vocabulary tooling](https://github.com/isamplesorg/vocabularies) and Quarto, all generated from the JSON-LD.
  - **HTML view:** [activity-type vocabulary](https://cross-domain-interoperability-framework.github.io/profile-provenance-draft/vocabularies/docs/activityTypes.html), served by GitHub Pages; each concept has an anchor named by its notation, for example [sample preparation](https://cross-domain-interoperability-framework.github.io/profile-provenance-draft/vocabularies/docs/activityTypes.html#samplePreparation).
  - **Resolving the IRIs:** the scheme IRI `https://w3id.org/cdif/provenance/activityType` and each concept IRI `https://w3id.org/cdif/provenance/activityType/<notation>` resolve through w3id.org by content negotiation. w3id answers with a 303 redirect into the GitHub Pages copy of this repo, chosen by the request's `Accept` header:

    | Accept | scheme IRI redirects to | concept IRI redirects to |
    |---|---|---|
    | `text/turtle` | `vocabularies/activityTypes.ttl` | `vocabularies/activityType/<notation>.ttl` |
    | `application/ld+json` or `application/json` | `vocabularies/activityTypes.jsonld` | `vocabularies/activityType/<notation>.jsonld` |
    | anything else (a browser) | `vocabularies/docs/activityTypes.html` | `vocabularies/docs/activityTypes.html#<notation>` |

    So a browser following a concept IRI lands on that concept in the HTML view, and an RDF client gets the concept's own SKOS description. The rules are in [ids/cdif/.htaccess](https://github.com/perma-id/w3id.org/blob/master/ids/cdif/.htaccess) of the w3id repo; they map the last IRI segment straight onto a file name, which is why a concept's local name must equal its `skos:notation`. For example, `curl -L -H "Accept: text/turtle" https://w3id.org/cdif/provenance/activityType/samplePreparation` returns that concept in Turtle.
- **[output_uc4 (1).ttl](output_uc4%20(1).ttl)** — PROV-O example: ML model development pipeline (data transformation, model development, model validation) demonstrating `prov:Activity`, `prov:Entity`, and `prov:wasAssociatedWith` patterns.

### Tools

- **[tools/WRROCToCdifProv.py](tools/WRROCToCdifProv.py)** — Converts Workflow Run RO-Crate (WRROC) and ARC Workflow Run RO-Crate files into CDIF cdifProv-compatible `@graph` documents. Supports standard WRROC profiles (Process Run Crate, Workflow Run Crate, Provenance Run Crate) and the ARC profile (LabProcess, LabProtocol, parameterValue, labEquipment, executesLabProtocol). Output uses `bios:` namespace prefix (`https://bioschemas.org/`) for all Bioschemas types and properties.

```bash
# Convert and save
python tools/WRROCToCdifProv.py input-rocrate.json -o output.cdifprov.json

# Verbose output
python tools/WRROCToCdifProv.py input-rocrate.json -o output.cdifprov.json -v

# Print to stdout
python tools/WRROCToCdifProv.py input-rocrate.json
```

- **[tools/galaxyROCrateToCDIF.py](tools/galaxyROCrateToCDIF.py)** — Converts full Galaxy RO-Crate archives (zip or directory) into cdifProv documents with per-step methodology detail. Reads `ro-crate-metadata.json`, CWL abstract workflow (step definitions), Galaxy workflow YAML (input defaults), and `jobs_attrs.txt` (execution records with tool IDs, versions, parameters, and timestamps). Output represents workflow steps as `schema:HowToStep` entries within a `schema:actionProcess` → `schema:HowTo` structure, with `bios:computationalTool` listing all tools used. Grouped parameters with shared prefixes are compacted into `schema:StructuredValue` objects for readability. Requires PyYAML.

```bash
# Convert Galaxy RO-Crate zip
python tools/galaxyROCrateToCDIF.py crate.rocrate.zip -o output.cdifprov.json

# Convert extracted directory
python tools/galaxyROCrateToCDIF.py crate-directory/ -o output.cdifprov.json -v
```

- **[tools/galaxyROCrateToCDIFActions.py](tools/galaxyROCrateToCDIFActions.py)** — Multi-activity variant of the Galaxy converter. Instead of a single `CreateAction` with `HowTo`/`HowToStep` methodology, each workflow step becomes its own `[schema:Action, prov:Activity]` with `prov:wasInformedBy` linking upstream data dependencies and `prov:wasInfluencedBy` linking back to the parent workflow action. Data flow is reconstructed from CWL step declarations when available, falling back to Galaxy job dataset mappings. Produces `.actions.cdifprov.json` files for side-by-side comparison with the HowTo/step approach.

```bash
# Convert Galaxy RO-Crate zip (multi-activity output)
python tools/galaxyROCrateToCDIFActions.py crate.rocrate.zip -o output.actions.cdifprov.json

# Convert extracted directory
python tools/galaxyROCrateToCDIFActions.py crate-directory/ -o output.actions.cdifprov.json -v
```

### Examples

The [Examples/](Examples/) folder contains provenance instance documents in various formats. Source RO-Crate files are in the [Examples/ROCRATE/](Examples/ROCRATE/) subfolder.

| File | Description |
|---|---|
| `ODIS_provExampleJulesVerne.json` | ODIS/OIH provenance example (schema.org Action pattern) |
| `Bennu-py-GC-MS*.json` | Bennu asteroid py-GC-MS/MS analytical workflow — standard WRROC and ARC profile versions, with source RO-Crates and cdifProv conversions |
| `FeS2-Analysis.cdifprov.json` | Galaxy FeS2 workflow — HowTo/step cdifProv conversion |
| `FeS2-Analysis.actions.cdifprov.json` | Galaxy FeS2 workflow — multi-activity cdifProv conversion |
| `Paper_1_Pt3Sn.*.cdifprov.json` | Galaxy Pt3Sn catalyst workflow (both formats) |
| `Paper_2_Diphosphine*.*.cdifprov.json` | Galaxy Diphosphine workflow (both formats) |
| `Paper_3-Au-colloids.*.cdifprov.json` | Galaxy Au colloids workflow (both formats) |
| `Paper_5-LaMnO3*.*.cdifprov.json` | Galaxy LaMnO3 catalytic behaviour workflow (both formats) |
| `Paper_8-EXAFS-fitting.*.cdifprov.json` | Galaxy EXAFS fitting workflow (both formats) |

Galaxy workflow RO-Crates originate from [Zenodo record 13842780](https://zenodo.org/records/13842780). Galaxy `.cdifprov.json` files were generated using [tools/galaxyROCrateToCDIF.py](tools/galaxyROCrateToCDIF.py) (HowTo/step approach) and `.actions.cdifprov.json` files using [tools/galaxyROCrateToCDIFActions.py](tools/galaxyROCrateToCDIFActions.py) (multi-activity approach). Bennu ARC examples were generated using [tools/WRROCToCdifProv.py](tools/WRROCToCdifProv.py).

#### One example reports on a different node, by design

Framing selects the node matching the frame's root `@type`, which in `cdifProvenance-frame.jsonld` is `schema:Dataset`. **`ODIS_provExampleJulesVerne.json` has a root typed `Action`**, so framing does not match it and the framed output describes a different node — `…/Dataset-015481461` rather than the source's `…/Action-00252231.json`.

That is expected: the example exists to exercise the schema.org Action pattern with an Action at the root, and **the frame should not be widened to accommodate it** — a frame's job is to match the shape this profile actually publishes.

Worth knowing because a useful sanity check — frame every example and compare the framed `@id` against the source `@id` — flags this one. It is the only expected mismatch here. Anything else appearing in that check is a real problem: the validator would be reporting on something other than the document it was given, **and reporting PASS while doing so**. That selection lives in `pick_main_entity`, which is generated from the normative source in the [validation](https://github.com/Cross-Domain-Interoperability-Framework/validation) repo — fix it there, never in this copy, which carries a DO-NOT-EDIT banner and a drift hash that CI checks.

#### An `@id` that is not a valid IRI silently loses the triple

Galaxy writes RO-Crate `@id`s containing spaces and pipes (`#input-Sn Foil`,
`…/output-plot_collection|0_flat`). A JSON-LD parser cannot turn those into a usable
IRI, so it drops the node **and the incoming triple with it**. In
`Paper_1_Pt3Sn.actions.cdifprov.json` 28 `prov:used` keys collapsed to 6 subjects in
the graph: 22 activities that do name their inputs looked like activities naming none.

**Nothing warned.** The JSON Schema gate sees the key present and is satisfied, which
is why this survived a clean 17/17 schema run while 12 examples failed conformance —
the loss happens after the gate, during RDF expansion. The converters now
percent-encode `@id`s, applied to definitions and references alike so the two stay in
step; a rename that touched only one side would break the join instead.

When adding an example, check `@id`s against the graph rather than the file: parse it
and compare the triple count for a property against the number of keys in the JSON.
Equal counts are the invariant; a shortfall means a node was dropped.

## Related Repositories

- [usgin/metadataBuildingBlocks](https://github.com/usgin/metadataBuildingBlocks) — CDIF metadata building blocks (cdifProv, provActivity, ddicdiProv schemas and SHACL shapes)
- [Cross-Domain-Interoperability-Framework/packaging](https://github.com/Cross-Domain-Interoperability-Framework/packaging) — CDIF packaging tools including RO-Crate and WRROC converters
- [Cross-Domain-Interoperability-Framework/validation](https://github.com/Cross-Domain-Interoperability-Framework/validation) — CDIF validation schemas and SHACL shapes

## Changelog — reviewRevision202606 (updates since branched from `main`)

This release-review branch has diverged from `main` with the following updates,
synced from the CDIF **metadataBuildingBlocks** source (see
`git log main..reviewRevision202606` for the full per-commit history):

- **Populated from metadataBuildingBlocks** — `*StructuredSchema.json`, merged SHACL,
  JSON-LD frame, examples, and the normative `FrameAndValidate.py` generated from the
  building-block source; `Examples/` renamed to `examples/`.
- **CDIF v1.1** — profile conformance URIs migrated `/1.0` → `/1.1`.
- **License** standardized on CC-BY-4.0.
- **`@id`-reference tightening** — bare `{@id}` reference slots sealed
  (`additionalProperties: false` + `required: ['@id']`); a canonical `objectReference`
  building block introduced as the strict node reference.
- **`prov:used` wrapper reconciliation** — the base `generatedBy.prov:used` accepts
  role-keyed wrappers (`schema:instrument` / `bios:computationalTool` / `prov:reagent`)
  alongside string / `{@id}` / inline `prov:Entity`; profiles pin a wrapper's shape via
  a constraint-only `if/then` (never a narrowed `anyOf`).
- **`skos:notation` → single string** at concept level (consistent with the codelist
  single-notation design).
- **`FrameAndValidate.py`** (normative, drift-checked against
  `Cross-Domain-Interoperability-Framework/validation`) — two-frame root-`@type`
  selection, context-aware `schema:about`, `--conformance` detection, `cdif:`-`@id`
  re-expansion, and (2026-08) reference-collapse on all document types + blank-node
  dedupe + agent `schema:identifier` unwrap, so `@embed:@always`-framed documents
  validate against the tightened schemas.
- **Examples** conformed to the tightened schemas throughout (PrimaryKey →
  `cdi:ComponentPosition`, reference slots → `{@id}`, CVE `hasIntendedDataType` →
  string, `skos:notation` → string, `schema:additionalType` URI → `{@id}`).
- **Galaxy converter corrections (2026-10-01)** — two defects that together failed
  conformance on all 12 Galaxy-derived examples, both fixed in the converters as
  well as the generated files:
  - An `OrganizeAction` is **not** a generator. Both converters swept
    `{CreateAction, OrganizeAction}` into the activity list, so "Run of Galaxy
    workflow engine" became an object of `prov:wasGeneratedBy`. The crate does not
    say that — across all eight source crates the root's `mentions` names the
    `CreateAction` every time and the `OrganizeAction` never. It is also the one
    action with no `object` and no `result` to map, so the `cdifProvActivity`
    `prov:used` Violation was reporting the mis-mapping rather than a missing value.
    The engine is preserved as a `bios:computationalTool` role entry on the workflow
    execution, where it is true.
  - `@id` values carried IRI-illegal characters through from the crate — 170 spaces
    and 31 pipes across 96 distinct `@id`s in 6 files, e.g. `#input-Sn Foil`. See
    the note below; now percent-encoded.


## Development branch

Work happens on `main`: this repo is a draft, and the 2026-06 review branch (`reviewRevision202606`) has been merged into it. GitHub Pages serves `main`, so the HTML view and the w3id IRIs reflect whatever is merged there. New changes should be PRs against `main`.

