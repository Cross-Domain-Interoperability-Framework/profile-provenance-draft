# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This is the **CDIF Provenance profile release repo**: the published artifacts for the `cdifProvenance`
building block (`prov:wasGeneratedBy` as an array of `cdifProvActivity` activities), plus design
notes comparing provenance vocabularies and converters that turn RO-Crates into cdifProv documents.
It is one of the `profile-*` release repos under `C:\GithubC\CDIF\`; the canonical source is
`metadataBuildingBlocks` (mBB).

## Branches

Work targets **`main`**: the repo is a draft, `reviewRevision202606` was merged into it (2026-10-28),
and GitHub Pages serves `main`, so whatever lands there is what the w3id IRIs resolve to. Branch from
`main` and PR into it. (mBB's `sync_release_repos.py` docstring says release repos now use an
`updates` branch; this repo has no such branch, so check what is checked out before syncing.)

## What is generated, and where to fix it

Most of the root is NOT authored here. Edit the source, never the copy:

| file | source | how it gets here |
|---|---|---|
| `cdifProvenanceStructuredSchema.json` | mBB `_sources/profiles/cdifProfile/cdifProvenance/resolvedSchema.json` | `python tools/sync_release_repos.py --apply --repo profile-provenance`, run **in mBB** |
| `provenanceRules.shacl` | mBB `validate_shacl --emit-shapes` over the same block | same sync |
| `examples/exampleCdifProvenance.json`, `examples/exampleEPMAProvenance.json` | mBB block's `example*.json` | same sync |
| `FrameAndValidate.py` | `Cross-Domain-Interoperability-Framework/validation` `tools/FrameAndValidate.py` | `python tools/sync_frameandvalidate.py --apply` in that repo. Carries a DO-NOT-EDIT banner; CI (`check-frameandvalidate.yml`) fails on any body drift from the normative copy |
| `examples/*.cdifprov.json` (Galaxy, Bennu) | `examples/ROCRATE/*` | the converters in `tools/` — fix the converter and regenerate, not the output |
| `vocabularies/activityTypes.ttl`, `vocabularies/activityType/*.{jsonld,ttl}` | `vocabularies/activityTypes.jsonld` | `python tools/buildVocabularyFiles.py vocabularies/activityTypes.jsonld`, committed with the source change; CI (`vocabulary-pages.yml`) fails a PR whose copies are stale |
| `vocabularies/docs/` | `vocabularies/activityTypes.ttl` | the iSamples `vocab2mdCacheV2.py` markdown writer plus Quarto, run and committed by `vocabulary-pages.yml` on push to `main`; never by hand |

Authored here: `cdifProvenance-frame.jsonld`, the converters in `tools/`, `ODIS_provExampleJulesVerne.json`,
the docs (`README.md`, `ProvenanceOptions.md`, `agents.md`, `PROV_Classes.ttl`), and
`vocabularies/activityTypes.jsonld`, the activity-type vocabulary for workflow steps. Validate a change to it
against the CDIF concept-scheme profile: `profile-conceptscheme`'s `FrameAndValidate.py -v` plus pyshacl
with its `conceptSchemeRules.shacl`. Keep each `skos:exactMatch`/`skos:broadMatch` pointing at a class that
exists in `PROV_Classes.ttl`, and each concept's IRI local name equal to its `skos:notation` (the w3id rules
map the last IRI segment straight onto `vocabularies/activityType/<name>.*`; the build fails otherwise).
`CDIFProvenanceImplementationGuide.md` is an auto-generated draft from the StructuredSchema.
Note `agents.md` here is a design analysis of *provenance agents*, not an agent-instructions file.

## Commands

Dependencies (unpinned; no requirements file): `pyld`, `jsonschema`, `rdflib`, `pyshacl`, and
`PyYAML` for the Galaxy converters.

```bash
# Frame + validate one document against the profile schema (schema and frame auto-detected beside the script)
python FrameAndValidate.py examples/exampleCdifProvenance.json -v

# Also detect conformance from content and rewrite dcterms:conformsTo (needs detect_conformance.py from the validation repo)
python FrameAndValidate.py <doc.json> -v --conformance -o framed.json

# SHACL
pyshacl -s provenanceRules.shacl -df json-ld -f human <doc.json>

# Converters (RO-Crate -> cdifProv)
python tools/WRROCToCdifProv.py examples/ROCRATE/<crate>.json -o examples/<name>.cdifprov.json -v
python tools/galaxyROCrateToCDIF.py <crate.zip|dir> -o examples/<name>.cdifprov.json -v                 # HowTo/HowToStep form
python tools/galaxyROCrateToCDIFActions.py <crate.zip|dir> -o examples/<name>.actions.cdifprov.json -v  # one Action per step
```

There is no test suite; "the tests" are FrameAndValidate `-v` plus pyshacl over every file in
`examples/`. A sync is judged by both staying where they were (all examples pass the schema; SHACL
violation counts unchanged).

## Two traps that report PASS while wrong

- **Framing picks the node matching the frame's root `@type` (`schema:Dataset`).**
  `ODIS_provExampleJulesVerne.json` has an `Action` root, so its framed output describes a different
  node — that is the one expected mismatch, and the frame must not be widened for it. Any other
  example whose framed `@id` differs from its source root `@id` means the validator is reporting on
  the wrong node. The selection (`pick_main_entity`) is fixed in the validation repo, never here.
- **An `@id` that is not a valid IRI silently drops the node and its incoming triple** during RDF
  expansion, after the JSON Schema gate has passed. Galaxy crates carry spaces and pipes in `@id`s;
  the converters percent-encode definitions and references together. When adding an example, parse
  it and compare a property's triple count to its key count in the JSON — they must be equal.

Both converters must also keep `OrganizeAction` (the Galaxy engine run) OUT of
`prov:wasGeneratedBy`; it is recorded as a `bios:computationalTool` role entry instead. See the
README changelog for the evidence.

## Modelling conventions the converters and examples follow

- `prov:used` holds role-keyed wrappers (`schema:instrument`, `bios:computationalTool`,
  `bios:reagent`) alongside string / `{@id}` / inline `prov:Entity`; profiles pin a wrapper's shape
  with a constraint-only `if/then`, never a narrowed `anyOf`.
- Bare reference slots are sealed `{@id}` objects (`additionalProperties: false`, `required: ['@id']`).
- Agents: `schema:agent` for the primary agent, `schema:participant` for the rest, `schema:Role`
  (AgentInRole) for qualified roles; software that runs steps is a `bios:computationalTool`, not an
  agent. Rationale in `agents.md`; the full vocabulary comparison is `ProvenanceOptions.md`.
- Bioschemas terms use the `bios:` prefix (`https://bioschemas.org/`).
