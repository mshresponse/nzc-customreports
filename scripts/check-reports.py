"""Run every NZC report and dashboard against an org loaded with sample-data/, and compare.

    python3 scripts/check-reports.py --target-org <alias>

A deploy proves the metadata is valid. It does not prove a report returns the right rows:
the four Missing reports deployed cleanly for months while listing every asset, because a
filter on the child side of an outer join behaves like part of the join. This script is
the check that catches that class of bug. It needs the sample data loaded exactly once
into an otherwise empty org, and the Salesforce CLI logged in to that org.

For each report it compares the first column of every detail row with the rows the sample
data was built to produce. For each dashboard it refreshes, waits, and fails on any
component that errors or comes back empty.
"""
import argparse
import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

API = '/services/data/v67.0/analytics'
ZURICH, SAO_PAULO, KRAKOW = 'Zürich Süd Rechenzentrum', 'São Paulo Fábrica', 'Kraków Magazyn'
PENA_VERDE, MALMO, OSAKA = 'Peña Verde Oficina', 'Malmö Kontor', 'Ōsaka Seizōsho'
CITROEN, VOLVO, PENAROL, SKODA = ('Fourgon Citroën 01', 'Lastbil Volvo 02',
                                  'Camión Peñarol 03', 'Kleinwagen Škoda 04')
FOOTPRINTS = ['FP Zürich 2024', 'FP São Paulo 2024', 'FP Kraków 2024', 'FP Ōsaka 2023',
              'FP Orphan A 2024', 'FP Orphan B 2023']
FLEET_FOOTPRINTS = ['VFP Citroën 2024', 'VFP Volvo 2024', 'VFP Fleet Orphan 2024']
ENERGY_USES = ['EU Zürich Electricity 2024', 'EU Zürich Natural Gas 2024',
               'EU São Paulo Electricity 2024', 'EU São Paulo Diesel 2024',
               'EU Peña Verde Electricity 2024', 'EU Ōsaka Electricity 2023',
               'EU Ōsaka Propane 2023']
FLEET_ENERGY_USES = ['VEU Citroën Diesel 2024', 'VEU Volvo Diesel 2024', 'VEU Peñarol Diesel 2024']

# First-column label of every detail row, or a row count where the first column is a
# figure rather than a name. Order doesn't matter; duplicates do.
EXPECTED = {
    'Asset_Names_and_Locations': [ZURICH, SAO_PAULO, KRAKOW, PENA_VERDE, MALMO, OSAKA],
    'Fleet_Names_and_Types': [CITROEN, VOLVO, PENAROL, SKODA],
    'Footprint_Data_Entry': [ZURICH, SAO_PAULO, KRAKOW, OSAKA],
    'Energy_Use_Data_Entry': [ZURICH, ZURICH, SAO_PAULO, SAO_PAULO, PENA_VERDE, OSAKA, OSAKA],
    'Fleet_Energy_Data_Entry': [CITROEN, VOLVO, PENAROL],
    'Stationary_Assets_Missing_Footprints': [PENA_VERDE, MALMO],
    'Stationary_Assets_Missing_Energy_Use': [KRAKOW, MALMO],
    'Fleet_Assets_Missing_Footprints': [PENAROL, SKODA],
    'Fleet_Assets_Missing_Energy_Use': [SKODA],
    'Orphaned_Carbon_Footprints': ['FP Orphan A 2024', 'FP Orphan B 2023'],
    'Orphaned_Fleet_Footprints': ['VFP Fleet Orphan 2024'],
    'Orphaned_Stationary_Energy_Uses': ['EU Peña Verde Electricity 2024'],
    'Orphaned_Vehicle_Energy_Uses': ['VEU Peñarol Diesel 2024'],
    'Emissions_by_Reporting_Year': FOOTPRINTS,
    'Emissions_by_Asset_and_Year': 6,
    'Footprints_by_Stage': FOOTPRINTS,
    'Footprints_by_Year_and_Stage': FOOTPRINTS,
    'Fleet_Footprints_by_Stage': FLEET_FOOTPRINTS,
    'Fleet_Footprints_by_Year_and_Stage': FLEET_FOOTPRINTS,
    'Fuel_Consumption_by_Fuel_Type': ENERGY_USES,
    'Fleet_Fuel_by_Fuel_Type': FLEET_ENERGY_USES,
}


def sf(org, *args):
    out = subprocess.run(['sf', *args, '--target-org', org], capture_output=True, text=True)
    return out.stdout


def rest(org, path, method='GET', body=None):
    args = ['api', 'request', 'rest', path, '--method', method]
    if body is not None:
        args += ['--body', str(body)]
    return json.loads(sf(org, *args))


def query(org, soql):
    return json.loads(sf(org, 'data', 'query', '--query', soql, '--json'))['result']['records']


def check_reports(org):
    reports = {r['DeveloperName']: r['Id'] for r in query(
        org, "SELECT Id, DeveloperName FROM Report WHERE FolderName = 'NZC Reports'")}
    failures = 0
    for name, expected in EXPECTED.items():
        if name not in reports:
            print(f'FAIL {name}: not found in the NZC Reports folder')
            failures += 1
            continue
        result = rest(org, f'{API}/reports/{reports[name]}?includeDetails=true')
        if isinstance(result, list):
            print(f"FAIL {name}: {result[0].get('message')}")
            failures += 1
            continue
        labels = [row['dataCells'][0]['label']
                  for cell in result['factMap'].values() for row in cell.get('rows', [])]
        if isinstance(expected, int):
            ok, got, want = len(labels) == expected, len(labels), expected
        else:
            ok, got, want = Counter(labels) == Counter(expected), sorted(labels), sorted(expected)
        print(f"{'ok  ' if ok else 'FAIL'} {name}" + ('' if ok else f'\n     got  {got}\n     want {want}'))
        failures += not ok
    missing = sorted(set(reports) - set(EXPECTED))
    for name in missing:
        print(f'FAIL {name}: no expected result defined in this script')
    return failures + len(missing)


def check_dashboards(org, body_file):
    dashboards = query(org, "SELECT Id, DeveloperName FROM Dashboard WHERE FolderName = 'NZC Dashboards'")
    for d in dashboards:
        rest(org, f"{API}/dashboards/{d['Id']}", 'PUT', f'@{body_file}')
    for _ in range(30):
        time.sleep(5)
        statuses = [c for d in dashboards
                    for c in rest(org, f"{API}/dashboards/{d['Id']}/status")['componentStatus']]
        if all(c['refreshStatus'] == 'IDLE' and c['refreshDate'] for c in statuses):
            break
    failures = 0
    for d in dashboards:
        result = rest(org, f"{API}/dashboards/{d['Id']}")
        titles = {c['id']: c.get('title') or c.get('header') for c in result['dashboardMetadata']['components']}
        for component in result['componentData']:
            status = component['status']
            ok = status['componentDataStatus'] == 'DATA' and not status.get('errorMessage')
            failures += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {d['DeveloperName']}: {titles[component['componentId']]}"
                  + ('' if ok else f" ({status['componentDataStatus']} {status.get('errorMessage') or ''})"))
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--target-org', required=True)
    org = parser.parse_args().target_org
    body = Path(__file__).with_name('.empty-body.json')
    body.write_text('{}')
    try:
        failures = check_reports(org) + check_dashboards(org, body)
    finally:
        body.unlink()
    print(f'\n{failures} failure(s)' if failures else '\nAll reports and dashboards match the sample data.')
    sys.exit(1 if failures else 0)


if __name__ == '__main__':
    main()
