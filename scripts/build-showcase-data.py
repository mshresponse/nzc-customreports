"""Regenerate sample-data/showcase/: a larger, realistic dataset for demos and screenshots.

    sf data import tree --plan sample-data/showcase/plan.json --target-org <alias>

sample-data/ itself is a test fixture: six sites, every row chosen so each report has a
known answer. That makes it a good check and a thin demo. This is the demo: 24 sites and 16
vehicles on three continents, three reporting years with footprints moving through their
stages, a few hundred energy use records trending down, and the kind of gaps a real
inventory has — sites not onboarded yet, consumption not collected, footprints with no
asset, energy use whose footprint was deleted. It is generated rather than hand-written,
deterministically, so rerunning the script changes nothing unless the script changes.

Load it into an org that has had sample-data/org-setup deployed, instead of the fixture
rather than on top of it: scripts/check-reports.py expects the fixture alone. All of it is
fictional, and the emission factors are illustrative only.
"""
import json
import random
from pathlib import Path

OUT = Path('sample-data/showcase')
MAX_PER_FILE = 200   # sObject Tree API limit per request
YEARS = ['2022', '2023', '2024']

# name, city, country, business region, asset type, size (scales consumption),
# first reporting year, and what is deliberately missing.
SITES = [
    ('Zürich Süd Rechenzentrum', 'Zürich', 'CH', 'EMEA', 'Data Center', 9, '2022', None),
    ('Frankfurt Rechenzentrum', 'Frankfurt', 'DE', 'EMEA', 'Data Center', 8, '2022', None),
    ('Dublin Data Centre', 'Dublin', 'IE', 'EMEA', 'Data Center', 7, '2022', None),
    ('London Head Office', 'London', 'GB', 'EMEA', 'Office', 3, '2022', None),
    ('Paris La Défense Bureau', 'Paris', 'FR', 'EMEA', 'Office', 2.5, '2022', None),
    ('Malmö Kontor', 'Malmö', 'SE', 'EMEA', 'Office', 1, '2022', None),
    ('Kraków Magazyn', 'Kraków', 'PL', 'EMEA', 'Warehouse', 1.5, '2022', None),
    ('Rotterdam Distributiecentrum', 'Rotterdam', 'NL', 'EMEA', 'Warehouse', 2, '2024', 'no energy use'),
    ('Milano Stabilimento', 'Milano', 'IT', 'EMEA', 'Manufacturing', 6, '2022', None),
    ('Lyon Usine', 'Lyon', 'FR', 'EMEA', 'Factory', 5, '2022', None),
    ('São Paulo Fábrica', 'São Paulo', 'BR', 'AMER', 'Factory', 6, '2022', None),
    ('Peña Verde Oficina', 'Ciudad de México', 'MX', 'AMER', 'Office', 1.2, '2022', None),
    ('Monterrey Planta', 'Monterrey', 'MX', 'AMER', 'Manufacturing', 5, '2023', None),
    ('Chicago Regional Office', 'Chicago', 'US', 'AMER', 'Office', 2, '2022', None),
    ('Dallas Data Center', 'Dallas', 'US', 'AMER', 'Data Center', 8, '2023', None),
    ('Toronto Warehouse', 'Toronto', 'CA', 'AMER', 'Warehouse', 1.8, '2022', 'footprint deleted 2024'),
    ('Santiago Bodega', 'Santiago', 'CL', 'AMER', 'Warehouse', 1.2, None, 'not onboarded'),
    ('Atlanta Retail Hub', 'Atlanta', 'US', 'AMER', 'Retail', 1, None, 'not onboarded'),
    ('Ōsaka Seizōsho', 'Ōsaka', 'JP', 'APAC', 'Manufacturing', 6, '2022', None),
    ('Tōkyō Honsha', 'Tōkyō', 'JP', 'APAC', 'Office', 2.5, '2022', None),
    ('Singapore Data Centre', 'Singapore', 'SG', 'APAC', 'Data Center', 7, '2022', None),
    ('Sydney Office', 'Sydney', 'AU', 'APAC', 'Office', 1.5, None, 'energy use, no footprint'),
    ('Bengaluru Campus', 'Bengaluru', 'IN', 'APAC', 'Office', 3, '2023', None),
    ('Shenzhen Factory', 'Shenzhen', 'CN', 'APAC', 'Factory', 5, '2023', 'no energy use'),
]

# Fuel, unit and annual consumption per unit of site size, by asset type.
FUELS = {
    'Data Center': [('Electricity', 'kWh', 1_150_000), ('Diesel', 'Liters', 900)],
    'Office': [('Electricity', 'kWh', 185_000), ('NaturalGas', 'Therms', 3_100)],
    'Warehouse': [('Electricity', 'kWh', 140_000), ('Propane', 'Liters', 4_200)],
    'Factory': [('Electricity', 'kWh', 520_000), ('NaturalGas', 'Therms', 38_000), ('FuelOil', 'Liters', 5_500)],
    'Manufacturing': [('Electricity', 'kWh', 480_000), ('NaturalGas', 'Therms', 41_000)],
    'Retail': [('Electricity', 'kWh', 160_000)],
}
FUEL_LABEL = {'NaturalGas': 'Natural Gas', 'FuelOil': 'Fuel Oil'}

# name, city, vehicle type, fleet vehicle type, fuel, litres a year, km per litre, gap.
VEHICLES = [
    ('Fourgon Citroën Lyon 01', 'Lyon', 'Fleet Vehicle', 'InternalCombustionEngine', 'Diesel', 3_200, 12.8, None),
    ('Lastbil Volvo Göteborg 02', 'Göteborg', 'Fleet Vehicle', 'InternalCombustionEngine', 'Diesel', 11_800, 8.1, None),
    ('Camión Peñarol Montevideo 03', 'Montevideo', 'Fleet Vehicle', 'InternalCombustionEngine', 'Diesel', 7_400, 8.4, None),
    ('Kleinwagen Škoda München 04', 'München', 'Fleet Vehicle', 'InternalCombustionEngine', 'Gasoline', 1_100, 15.5, 'no energy use'),
    ('Ford Transit London 05', 'London', 'Fleet Vehicle', 'InternalCombustionEngine', 'Diesel', 3_600, 11.9, None),
    ('Mercedes Sprinter Frankfurt 06', 'Frankfurt', 'Fleet Vehicle', 'InternalCombustionEngine', 'Diesel', 3_900, 11.2, None),
    ('Isuzu Elf Tōkyō 07', 'Tōkyō', 'Fleet Vehicle', 'InternalCombustionEngine', 'Diesel', 4_700, 9.6, None),
    ('Toyota HiAce Sydney 08', 'Sydney', 'Fleet Vehicle', 'InternalCombustionEngine', 'Diesel', 3_300, 11.5, None),
    ('Ram ProMaster Chicago 09', 'Chicago', 'Fleet Vehicle', 'InternalCombustionEngine', 'Gasoline', 4_100, 7.9, None),
    ('Chevrolet Express Dallas 10', 'Dallas', 'Fleet Vehicle', 'InternalCombustionEngine', 'Gasoline', 4_400, 7.1, None),
    ('Tata Ace Bengaluru 11', 'Bengaluru', 'Fleet Vehicle', 'InternalCombustionEngine', 'Diesel', 2_100, 14.2, 'energy use, no footprint'),
    ('Volkswagen Crafter Milano 12', 'Milano', 'Fleet Vehicle', 'InternalCombustionEngine', 'Diesel', 3_700, 11.0, 'no energy use'),
    ('Shuttle Bus Dublin 13', 'Dublin', 'Company Shuttle', 'InternalCombustionEngine', 'Diesel', 14_500, 3.9, None),
    ('Shuttle Bus Singapore 14', 'Singapore', 'Company Shuttle', 'InternalCombustionEngine', 'Diesel', 13_200, 4.1, 'not onboarded'),
    ('Toyota Prius Toronto 15', 'Toronto', 'Fleet Vehicle', 'Hybrid', 'Gasoline', 950, 22.0, None),
    ('Corolla Hybrid São Paulo 16', 'São Paulo', 'Fleet Vehicle', 'Hybrid', 'Gasoline', 1_050, 20.5, None),
]

# Where each year's footprints sit in the process: closed years done, the current one spread.
STAGES_2024 = ['Data Collection', 'Data Gap Filling', 'Data Validation', 'Data Validation',
               'Internal Audit', 'Internal Audit', 'External Audit']
FLEET_STAGES_2024 = ['Data Collection', 'Data Validation', 'Data Validation', 'Internal Audit', 'External Audit']
TREND = {'2022': 1.0, '2023': 0.965, '2024': 0.93}   # efficiency programme, roughly


class Records:
    def __init__(self):
        self.by_object = {}
        self.refs = {}

    def add(self, sobject, fields, key=None):
        items = self.by_object.setdefault(sobject, [])
        ref = f'Show{sobject}{len(items) + 1}'
        record = {'attributes': {'type': sobject, 'referenceId': ref}}
        record.update({k: v for k, v in fields.items() if v is not None})
        items.append(record)
        self.refs[key or (sobject, fields.get('Name'))] = '@' + ref
        return '@' + ref


def build():
    rng = random.Random(2026)
    noise = lambda: rng.uniform(0.94, 1.06)
    r = Records()

    factors = r.add('OtherEmssnFctrSet', {
        'Name': 'Showcase Fleet Factors',
        'EmissionFactorDataSource': 'Illustrative only, for demo data. Replace with factors from your own source before reporting.'})
    for fuel, co2, cv in [('Diesel', 2.68, 10.0), ('Gasoline', 2.31, 9.1)]:
        r.add('OtherEmssnFctrSetItem', {'ParentEmissionFactorId': factors, 'FuelType': fuel,
                                        'Co2EmissionFactor': co2, 'Co2EmissionFactorUnit': 'KG_PER_L',
                                        'CalorificValue': cv, 'CalorificValueUnit': 'KWH_PER_L'}, key=('item', fuel))

    footprints, energy = [], []
    for name, city, country, region, kind, size, first, gap in SITES:
        asset = r.add('StnryAssetEnvrSrc', {'Name': name, 'City': city, 'Country': country,
                                            'BusinessRegion': region, 'StationaryAssetType': kind})
        years = YEARS[YEARS.index(first):] if first else []
        for year in years:
            if gap == 'footprint deleted 2024' and year == '2024':
                continue
            stage = 'Completed' if year < '2023' else (
                rng.choice(['Completed', 'Completed', 'External Audit']) if year == '2023' else rng.choice(STAGES_2024))
            footprints.append((asset, year, r.add('StnryAssetCrbnFtprnt', {
                'Name': f'{name} {year}', 'StnryAssetEnvrSrcId': asset, 'ReportingYear': year, 'FootprintStage': stage})))
        if gap == 'no energy use':
            continue
        consumption_years = years + (['2024'] if gap in ('footprint deleted 2024', 'energy use, no footprint') else [])
        for year in sorted(set(consumption_years)):
            footprint = next((f for a, y, f in footprints if a == asset and y == year), None)
            for fuel, unit, per_size in FUELS[kind]:
                energy.append({'Name': f'{name} {FUEL_LABEL.get(fuel, fuel)} {year}', 'StnryAssetEnvrSrcId': asset,
                               'StnryAssetCrbnFtprntId': footprint, 'FuelType': fuel,
                               'FuelConsumption': round(per_size * size * TREND[year] * noise()),
                               'FuelConsumptionUnit': unit})
    for name, year in [('Leeds Office', '2023'), ('Leeds Office', '2024'), ('Imported Footprint', '2022')]:
        r.add('StnryAssetCrbnFtprnt', {'Name': f'{name} {year}', 'ReportingYear': year,
                                       'FootprintStage': 'Completed' if year < '2024' else 'Data Validation'})
    for record in energy:
        r.add('StnryAssetEnrgyUse', record)

    fleet_energy = []
    for name, city, vtype, ftype, fuel, litres, km_per_l, gap in VEHICLES:
        vehicle = r.add('VehicleAssetEmssnSrc', {'Name': name, 'City': city, 'VehicleType': vtype,
                                                 'FleetVehicleType': ftype})
        if gap in ('not onboarded', 'energy use, no footprint'):
            years = []
        else:
            years = ['2023', '2024']
        fps = {}
        for year in years:
            stage = rng.choice(['Completed', 'Completed', 'External Audit']) if year == '2023' else rng.choice(FLEET_STAGES_2024)
            fps[year] = r.add('VehicleAssetCrbnFtprnt', {'Name': f'{name} {year}', 'VehicleAssetEmssnSrcId': vehicle,
                                                         'ReportingYear': year, 'FootprintStage': stage})
        if gap in ('no energy use', 'not onboarded'):
            continue
        for year in (years or ['2024']):
            used = round(litres * TREND[year] * noise())
            fleet_energy.append({'Name': f'{name} {fuel} {year}', 'VehicleAssetEmssnSrcId': vehicle,
                                 'VehicleAssetCrbnFtprntId': fps.get(year), 'OtherEmssnFctrId': factors,
                                 'FuelType': fuel, 'FuelConsumption': used, 'FuelConsumptionUnit': 'LITERS',
                                 'Distance': round(used * km_per_l * noise())})
    r.add('VehicleAssetCrbnFtprnt', {'Name': 'Retired Van 2023', 'ReportingYear': '2023', 'FootprintStage': 'Completed'})
    for record in fleet_energy:
        r.add('VehicleAssetEnrgyUse', record)
    return r


def main():
    records = build()
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob('*.json'):
        old.unlink()
    plan = []
    for n, (sobject, items) in enumerate(records.by_object.items(), start=1):
        files = []
        for part, start in enumerate(range(0, len(items), MAX_PER_FILE), start=1):
            name = f'{n}_{sobject}' + (f'_{part}' if len(items) > MAX_PER_FILE else '') + '.json'
            chunk = {'records': items[start:start + MAX_PER_FILE]}
            (OUT / name).write_text(json.dumps(chunk, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            files.append(name)
        resolves = any(isinstance(v, str) and v.startswith('@') for rec in items for v in rec.values())
        plan.append({'sobject': sobject, 'saveRefs': True, 'resolveRefs': resolves, 'files': files})
    (OUT / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n', encoding='utf-8')
    print(', '.join(f'{len(v)} {k}' for k, v in records.by_object.items()))


if __name__ == '__main__':
    main()
