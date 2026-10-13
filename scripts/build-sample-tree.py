"""Regenerate sample-data/tree/ from the CSVs in sample-data/.

The CSVs are the source of truth; the tree files exist so the whole set loads with one
command, parents before children, with lookups resolved by reference instead of by Id:

    sf data import tree --plan sample-data/tree/plan.json --target-org <alias>

A column named `<Relationship>.Name` is a lookup to the row of that name in the parent
file, and becomes `<Relationship>Id` pointing at the parent's reference. Files load in
filename order, which is why the emission factor files are numbered 0a and 0b. Run from the
repository root after editing any CSV; CI fails if the tree files are stale.
"""
import csv
import json
from pathlib import Path

SRC = Path('sample-data')
OUT = SRC / 'tree'
NUMERIC = {'FuelConsumption', 'Distance', 'Co2EmissionFactor', 'CalorificValue'}
# Lookups whose relationship name is not the parent object's name.
PARENT_OBJECT = {'ParentEmissionFactor': 'OtherEmssnFctrSet', 'OtherEmssnFctr': 'OtherEmssnFctrSet'}


def number(value):
    as_float = float(value)
    return int(as_float) if as_float.is_integer() else as_float


def main():
    OUT.mkdir(exist_ok=True)
    refs = {}   # (object, Name) -> referenceId
    plan = []
    for path in sorted(SRC.glob('*.csv')):
        sobject = path.stem.split('_', 1)[1]
        with path.open(encoding='utf-8', newline='') as f:
            rows = list(csv.DictReader(f))
        records, resolves = [], False
        for i, row in enumerate(rows, start=1):
            ref = f'{sobject}Ref{i}'
            if 'Name' in row:
                refs[(sobject, row['Name'])] = ref
            record = {'attributes': {'type': sobject, 'referenceId': ref}}
            for column, value in row.items():
                if value == '':
                    continue
                if column.endswith('.Name'):
                    relationship = column[:-len('.Name')]
                    parent = PARENT_OBJECT.get(relationship, relationship)
                    record[f'{relationship}Id'] = '@' + refs[(parent, value)]
                    resolves = True
                elif column in NUMERIC:
                    record[column] = number(value)
                else:
                    record[column] = value
            records.append(record)
        name = f'{path.stem}.json'
        text = json.dumps({'records': records}, ensure_ascii=False, indent=2) + '\n'
        (OUT / name).write_text(text, encoding='utf-8')
        plan.append({'sobject': sobject, 'saveRefs': True, 'resolveRefs': resolves, 'files': [name]})
    (OUT / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
