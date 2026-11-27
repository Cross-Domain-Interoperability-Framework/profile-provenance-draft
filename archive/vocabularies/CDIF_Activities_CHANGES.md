# CDIF Provenance Activities – review of the draft (2026-11-04)

Files: `CDIF_Activities.json` (JSON-LD) and `CDIF_Activities.ttl` (Turtle, same graph).
Source: `CDIF_Activities_draft.json` (Arofan, from Flavio's enhanced spreadsheet).
Reproduce with `python scripts/skos/fix_cdif_activities.py CDIF_Activities_draft.json CDIF_Activities.json`.
Check with `python scripts/skos/check_skos.py CDIF_Activities.json --against GSBPM_5_2_SKOS.json`.

Result: 40 concepts, 271 triples. Passes the SKOS integrity checks: one prefLabel per
language, every concept in the scheme, broader/narrower symmetric with no cycles,
hasTopConcept ⇔ topConceptOf, every mapping target exists in GSBPM 5.2, and no
literal values on link properties.

## Changes

| | Change |
|---|---|
| IRIs | Removed the brackets: `Extraction(Sample)` → `SampleExtraction`, `QualityControl(Data)` → `QualityControlData`, `QualityControl(Metadata)` → `QualityControlMetadata`. Labels keep the brackets. |
| Typos | "Disclosure cControl", "characterisc", "desireable" ×2, "a entity's", "representations data integration" (added "for"), trailing space in Cataloguing |
| Scheme | Added `skos:hasTopConcept` (31) and `skos:topConceptOf`; English language tags on the scheme label and definition |
| Mappings | Added `skos:closeMatch` from the GSBPM-derived concepts to their GSBPM 5.2 sub-processes: Data Classification and Coding → 5.2, Variable and Unit Derivation → 5.5, Weighting → 5.6, Output Interpretation and Explanation → 6.3, Disclosure Control → 6.4 |
| Hierarchy | Data Cleaning `broader` Data Transformation (its definition calls it "a data transformation") |
| References | Overarching Activities cites both GAMSO and GSIM. The GSBPM source file had the `references` key twice, so GAMSO had been lost. |
| Context | Removed the unused `cact` prefix; added terms for `exactMatch` and `closeMatch`; typed `inScheme`, `hasTopConcept` and `topConceptOf` as `@id` |

## Open points for the group

- Possible hierarchy that the definitions don't state: Measurement and Count under Observation;
  Derivation, Data Harmonisation and Format Standardization under Data Transformation;
  Archiving and Digital Preservation.
- Most CDIF-native concepts have no `dct:references` yet.
- The overarching activities use IRIs under `…/GSBPM-5.2/activity/` but are in the CDIF scheme.
  They are kept as they are, with `exactMatch` to the UNECE GSBPM concepts.
