# Archive

Retired material, kept for reference. Nothing here is maintained, and the example checks over
`examples/` do not cover it.

## Galaxy HowTo/step form

Galaxy workflow runs were first converted in two forms, side by side:

- **HowTo/step** (archived here): one `schema:CreateAction` whose steps are a recipe,
  `schema:actionProcess` → `schema:HowTo` → ordered `schema:step`.
- **One action per step** (current): each workflow step is its own
  `[schema:Action, prov:Activity]`.

The one-action-per-step form was kept because it attaches techniques, agents, inputs and outputs to
the step that used or produced them. Its converter is
[tools/galaxyROCrateToCDIFActions.py](../tools/galaxyROCrateToCDIFActions.py), and its outputs are
`examples/*.actions.cdifprov.json`.

| archived | what it is |
|---|---|
| [tools/galaxyROCrateToCDIF.py](tools/galaxyROCrateToCDIF.py) | the HowTo/step converter |
| [examples/](examples/) | its six outputs (`FeS2-Analysis`, `Paper_1`, `_2`, `_3`, `_5`, `_8`), from the crates in [../examples/ROCRATE/](../examples/ROCRATE/) |

## Vocabulary drafts

Earlier states of the files in [../vocabularies/](../vocabularies/):

| archived | what it is |
|---|---|
| [vocabularies/CDIF_Activities (2).ttl](<vocabularies/CDIF_Activities (2).ttl>) | the CDIF provenance activity vocabulary after the review of the draft (40 concepts, 271 triples, before `skos:notation` was added): the same graph as `vocabularies/CDIF_Activities.ttl` at commit `a059838` |
| [vocabularies/CDIF_Activities_CHANGES.md](vocabularies/CDIF_Activities_CHANGES.md) | that review of the draft: the changes made and the open points for the group |
| [vocabularies/activityTypesv0.1.jsonld](vocabularies/activityTypesv0.1.jsonld), [.ttl](vocabularies/activityTypesv0.1.ttl) | the v0.1 activity types before they were deprecated in commit `2db94d4` |
| [vocabularies/.project](vocabularies/.project) | an Eclipse project file for the folder |
