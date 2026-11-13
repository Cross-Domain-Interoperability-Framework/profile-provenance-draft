#!/usr/bin/env python3
"""
Record what a cdifProv activity used with schema:instrument / schema:object, not prov:used.

CDIF's schema.org implementation (cdifProvActivity, metadataBuildingBlocks #81/#82) no longer
accepts role-keyed prov:used wrappers ({"bios:computationalTool": [...]}, {"schema:instrument":
[...]}, {"bios:reagent": [...]}). For every node typed both schema:Action and prov:Activity:

- a wrapper's values, and any bios:computationalTool / bios:reagent / bios:labEquipment placed
  directly on the activity, become schema:instrument items, as does a wrapper found in
  schema:object;
- every other prov:used value (an @id reference, an inline entity, a string) becomes a
  schema:object input, de-duplicated by @id;
- prov:used is removed;
- schema:instrument is always an array, and each item described in place gets exactly one
  Wikidata kind term in schema:additionalType -- software Q7397, reagent Q2356542, otherwise
  instrument Q3099911 -- plus the @type that kind requires when it has none (a reagent typed
  none of DefinedTerm / Product / ChemicalSubstance gets schema:ChemicalSubstance).

Both converters (WRROCToCdifProv.py, galaxyROCrateToCDIFActions.py) call migrate() as their last
step. Run as a script to migrate existing documents in place:

    python tools/usedResources.py examples/*.cdifprov.json
"""
import json
import re
import sys

WD = 'https://www.wikidata.org/entity/'
KIND = {'instrument': WD + 'Q3099911', 'software': WD + 'Q7397', 'reagent': WD + 'Q2356542'}
KIND_TYPE = {'instrument': 'schema:Product', 'software': 'schema:SoftwareApplication'}
# A reagent's @type says what the material is; with none of these, a bulk chemical is assumed.
REAGENT_TYPES = {'schema:DefinedTerm', 'schema:Product', 'schema:ChemicalSubstance'}
ROLE_KIND = {'bios:computationalTool': 'software', 'bios:reagent': 'reagent',
             'bios:labEquipment': 'instrument', 'schema:instrument': None}


def _list(x):
    return x if isinstance(x, list) else [x]


def _types(n):
    return _list(n.get('@type', [])) if isinstance(n, dict) else []


def _kind_of(item, role):
    if role and ROLE_KIND.get(role):
        return ROLE_KIND[role]
    t = _types(item)
    if 'schema:SoftwareApplication' in t:
        return 'software'
    if 'schema:ChemicalSubstance' in t:
        return 'reagent'
    return 'instrument'


def add_kind(item, role=None):
    """Give an in-place item its kind term (and kind @type if it has none); leave {@id} alone."""
    if not isinstance(item, dict) or set(item) <= {'@id'}:
        return item
    at = item.get('schema:additionalType', [])
    at = at if isinstance(at, list) else [at]
    if any(q in json.dumps(at) for q in ('Q3099911', 'Q7397', 'Q2356542')):
        item['schema:additionalType'] = at
        return item
    kind = _kind_of(item, role)
    at.append({'@id': KIND[kind]})
    item['schema:additionalType'] = at
    need = KIND_TYPE.get(kind)
    if need and need not in _types(item):
        item['@type'] = _types(item) + [need]
    if kind == 'reagent' and not set(_types(item)) & REAGENT_TYPES:
        item['@type'] = _types(item) + ['schema:ChemicalSubstance']
    return item


def migrate_activity(a):
    changed = []
    instr = _list(a.get('schema:instrument', [])) if 'schema:instrument' in a else []
    obj = _list(a.get('schema:object', [])) if 'schema:object' in a else []
    had_obj_list = isinstance(a.get('schema:object'), list)
    for role in ('bios:computationalTool', 'bios:reagent', 'bios:labEquipment'):
        if role in a:
            for x in _list(a.pop(role)):
                instr.append(add_kind(x, role))
            changed.append(f'{role} -> schema:instrument')
    # A wrapper can also have been carried into schema:object, when prov:used inputs moved there.
    for i in list(obj):
        roles = [k for k in ROLE_KIND if isinstance(i, dict) and k in i and '@type' not in i]
        if roles:
            obj.remove(i)
            for r in roles:
                for x in _list(i[r]):
                    instr.append(add_kind(x, r))
            changed.append('schema:object wrapper -> schema:instrument')
    for i in _list(a.pop('prov:used', [])):
        roles = [k for k in ROLE_KIND if isinstance(i, dict) and k in i and '@type' not in i]
        if roles:
            for r in roles:
                for x in _list(i[r]):
                    instr.append(add_kind(x, r))
            changed.append('prov:used wrapper -> schema:instrument')
            continue
        if isinstance(i, dict) and i.get('@id') and any(
                isinstance(o, dict) and o.get('@id') == i['@id'] for o in obj):
            changed.append('prov:used entity already in schema:object')
            continue
        obj.append(i)
        changed.append('prov:used entity -> schema:object')
    if instr:
        a['schema:instrument'] = [add_kind(x) for x in instr]
        if not changed:
            changed.append('schema:instrument kind terms')
    if obj:
        a['schema:object'] = obj if (len(obj) > 1 or had_obj_list or 'schema:object' not in a) else obj[0]
    elif 'schema:object' in a:
        del a['schema:object']
    return changed


def migrate(doc):
    """Migrate every schema:Action + prov:Activity node in doc, in place. Returns a change log."""
    log = []

    def walk(o):
        if isinstance(o, dict):
            t = _types(o)
            if 'schema:Action' in t and 'prov:Activity' in t:
                log.extend(migrate_activity(o))
            for v in list(o.values()):
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(doc)
    return log


def main(paths):
    for p in paths:
        raw = open(p, encoding='utf-8').read()
        m = re.search(r'\n( +)"', raw)
        ind = len(m.group(1)) if m else 2
        doc = json.loads(raw)
        log = migrate(doc)
        if log:
            out = json.dumps(doc, indent=ind, ensure_ascii=False) + ('\n' if raw.endswith('\n') else '')
            with open(p, 'w', encoding='utf-8', newline='') as fh:
                fh.write(out.replace('\n', '\r\n') if '\r\n' in raw else out)
        counts = {}
        for c in log:
            counts[c] = counts.get(c, 0) + 1
        print(p, '|', '; '.join(f'{k} x{v}' for k, v in sorted(counts.items())) or 'no change')


if __name__ == '__main__':
    main(sys.argv[1:])
