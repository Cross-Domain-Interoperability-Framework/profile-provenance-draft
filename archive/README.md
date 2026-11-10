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
