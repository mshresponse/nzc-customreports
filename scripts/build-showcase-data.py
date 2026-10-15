"""Regenerate sample-data/showcase/: a larger, realistic dataset for demos and screenshots.

    sf data import tree --plan sample-data/showcase/plan.json --target-org <alias>

sample-data/ itself is a test fixture: six sites, every row chosen so each report has a
known answer. That makes it a good check and a thin demo. This is the demo: 34 sites and 22
vehicles on three continents, three reporting years with footprints moving through their
stages, a few hundred energy use records trending down, and the kind of gaps a real
inventory has — sites not onboarded yet, consumption not collected, footprints with no
asset, energy use whose footprint was deleted. Then Scope 3: suppliers, spend-based
procurement in eight categories, and business travel (flights, hotels, taxis, commuting) for
three regions, with the factor sets and inflation rates Net Zero Cloud needs to calculate
them on save. It is generated rather than hand-written,
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
    ('Auckland Office', 'Auckland', 'NZ', 'APAC', 'Office', 1.2, None, 'not onboarded'),
    ('Melbourne Office', 'Melbourne', 'AU', 'APAC', 'Office', 1.4, None, 'energy use, no footprint'),
    ('Seoul Office', 'Seoul', 'KR', 'APAC', 'Office', 1.6, None, 'not onboarded'),
    ('Gdańsk Biuro', 'Gdańsk', 'PL', 'EMEA', 'Office', 0.9, None, 'energy use, no footprint'),
    ('Denver Retail Store', 'Denver', 'US', 'AMER', 'Retail', 0.8, None, 'not onboarded'),
    ('Phoenix Retail Store', 'Phoenix', 'US', 'AMER', 'Retail', 0.9, None, 'not onboarded'),
    ('Lima Almacén', 'Lima', 'PE', 'AMER', 'Warehouse', 1.3, None, 'not onboarded'),
    ('Bogotá Bodega', 'Bogotá', 'CO', 'AMER', 'Warehouse', 1.1, '2024', 'no energy use'),
    ('Porto Armazém', 'Porto', 'PT', 'EMEA', 'Warehouse', 1.0, '2024', 'no energy use'),
    ('Hanoi Factory', 'Hanoi', 'VN', 'APAC', 'Factory', 4, '2024', 'no energy use'),
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
    ('Mahindra Bolero Pune 17', 'Pune', 'Fleet Vehicle', 'InternalCombustionEngine', 'Diesel', 2_600, 13.0, 'not onboarded'),
    ('Hyundai Porter Seoul 18', 'Seoul', 'Fleet Vehicle', 'InternalCombustionEngine', 'Diesel', 3_000, 12.0, 'not onboarded'),
    ('Shuttle Bus Auckland 19', 'Auckland', 'Company Shuttle', 'InternalCombustionEngine', 'Diesel', 12_800, 4.0, 'not onboarded'),
    ('Isuzu D-Max Bangkok 20', 'Bangkok', 'Fleet Vehicle', 'InternalCombustionEngine', 'Diesel', 2_900, 12.5, 'energy use, no footprint'),
    ('Shuttle Bus Lyon 21', 'Lyon', 'Company Shuttle', 'InternalCombustionEngine', 'Diesel', 13_900, 4.0, 'no energy use'),
    ('Ford Ranger Santiago 22', 'Santiago', 'Fleet Vehicle', 'InternalCombustionEngine', 'Diesel', 3_100, 11.8, 'no energy use'),
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
    build_scope3(r, rng, noise)
    return r


# Scope 3. Spend-based procurement factors in tCO2e per million spent, by category, then
# who is bought from and roughly how much a year. All illustrative.
PCMT_FACTORS = [
    ('IT services and software', 'Purchased Goods and Services', 'Information technology', 120),
    ('Professional services', 'Purchased Goods and Services', 'Professional services', 95),
    ('Office supplies and furniture', 'Purchased Goods and Services', 'Office goods', 310),
    ('Facilities and cleaning', 'Purchased Goods and Services', 'Facilities management', 210),
    ('Computers and servers', 'Capital Goods', 'Computer equipment', 380),
    ('Construction and fit-out', 'Capital Goods', 'Construction', 450),
    ('Freight and logistics', 'Upstream Transportation and Distribution', 'Freight transport', 720),
    ('Waste collection and treatment', 'Waste Generated In Operations', 'Waste management', 650),
]
SUPPLIERS = [   # supplier, factor it buys, annual spend in USD, what is bought
    ('Nordlicht IT Services', 'IT services and software', 1_150_000, ['Cloud hosting', 'Software licences', 'Managed service desk']),
    ('Halvorsen Consulting', 'Professional services', 640_000, ['Audit and assurance', 'Sustainability advisory']),
    ('Atlas Office Supply', 'Office supplies and furniture', 210_000, ['Office furniture', 'Stationery']),
    ('Clearwater Facilities', 'Facilities and cleaning', 480_000, ['Cleaning contract', 'Building maintenance']),
    ('Kestrel Hardware', 'Computers and servers', 920_000, ['Server refresh', 'Laptop fleet']),
    ('Summit Fit-Out', 'Construction and fit-out', 1_600_000, ['Office fit-out']),
    ('Meridian Freight', 'Freight and logistics', 830_000, ['Inbound freight', 'Last-mile delivery']),
    ('GreenCycle Waste Services', 'Waste collection and treatment', 140_000, ['Waste collection', 'E-waste recycling']),
]
UNFACTORED = [   # purchases nobody has matched to a factor yet: spend with no Scope 3 attached
    ('Atlas Office Supply', 'Promotional merchandise', 'Marketing', '2024', 38_000),
    ('Halvorsen Consulting', 'Legal fees', 'Legal services', '2024', 96_000),
    ('Kestrel Hardware', 'Spare parts', 'Maintenance', '2023', 22_000),
    ('Meridian Freight', 'Customs brokerage', 'Freight services', '2024', 17_500),
]
UNTRACKED_SOURCES = [   # Scope 3 sources set up with no footprint yet
    ('Employee Commuting - Global', 'Employee Commuting', 'EMEA', 'GB'),
    ('Downstream Distribution - AMER', 'Downstream Transportation', 'AMER', 'US'),
    ('Leased Warehouses - APAC', 'Upstream Leased Assets', 'APAC', 'SG'),
]
TRAVEL_SUPPLIERS = ['Skyward Airlines', 'Polar Air', 'Harbor Hotels Group', 'CityCab Network']
COST_CENTERS = ['Sales', 'Engineering', 'Operations', 'Executive', 'Sustainability']
TRAVEL_REGIONS = [   # region, country, flights a year as (from, to, km), hotel country
    ('EMEA', 'GB', [('LHR', 'JFK', 5540), ('LHR', 'FRA', 650), ('ZRH', 'SIN', 10300), ('CDG', 'MAD', 1060)], 'US'),
    ('AMER', 'US', [('ORD', 'GRU', 8400), ('DFW', 'YYZ', 1950), ('ORD', 'LHR', 6350), ('ATL', 'MEX', 2140)], 'BR'),
    ('APAC', 'JP', [('HND', 'SIN', 5320), ('SYD', 'AKL', 2160), ('BLR', 'SIN', 3180), ('HND', 'ICN', 1210)], 'SG'),
]


def build_scope3(r, rng, noise):
    for supplier in [s[0] for s in SUPPLIERS] + TRAVEL_SUPPLIERS:
        account = r.add('Account', {'Name': supplier}, key=('Account', supplier))
        r.add('Supplier', {'Name': supplier, 'AccountId': account, 'CompanyRelationshipType': 'Value Chain Supplier'})
    pcmt_set = r.add('PcmtEmssnFctrSet', {
        'Name': 'Showcase Spend-Based Factors', 'CurrencyCode': 'USD', 'EmissionFactorUpdateYear': '2023',
        'EmissionFactorDataSource': 'Illustrative only, for demo data. Replace with factors from your own source before reporting.'})
    for name, category, sector, per_million in PCMT_FACTORS:
        r.add('PcmtEmssnFctrSetItem', {'Name': name, 'PcmtEmssnFctrSetId': pcmt_set, 'Scope3GhgCategory': category,
                                       'EconomicSectorCategory': sector, 'TotScpe3EmssnPerMillionSpent': per_million})
    air = r.add('AirTravelEmssnFctr', {
        'Name': 'Showcase Air Travel Factors', 'DistanceUnit': 'Kilometers', 'EmissionFactorUpdateYear': '2023',
        'ShortHaulMaximumDistance': 1000, 'MediumHaulMaximumDistance': 3700, 'LongHaulMinimumDistance': 3700,
        'Co2PsgrKmShortHaulInKg': 0.15, 'Co2PsgrKmMediumHaulInKg': 0.13, 'Co2PsgrKmLongHaulInKg': 0.11,
        'Ch4PsgrKmShortHaulInKgCo2e': 0.0001, 'Ch4PsgrKmMediumHaulInKgCo2e': 0.0001, 'Ch4PsgrKmLongHaulInKgCo2e': 0.0001,
        'N2oPsgrKmShortHaulInKgCo2e': 0.0015, 'N2oPsgrKmMediumHaulInKgCo2e': 0.0012, 'N2oPsgrKmLongHaulInKgCo2e': 0.0011,
        'EmissionFactorDataSource': 'Illustrative only, for demo data.'})
    hotel = r.add('HotelStayEmssnFctr', {'Name': 'Showcase Hotel Factors', 'EmissionFactorUpdateYear': '2023',
                                         'HotelStayEmssnInKgCo2eNight': 15, 'EmissionFactorDataSource': 'Illustrative only, for demo data.'})
    ground = r.add('GroundTravelEmssnFctr', {
        'Name': 'Showcase Ground Travel Factors', 'DistanceUnit': 'Kilometers', 'CurrencyCode': 'USD',
        'EmissionFactorUpdateYear': '2023', 'TaxiEmssnInKgCo2eDstnUnit': 0.15, 'TaxiRateForDstnUnit': 2.0,
        'TrainEmssnInKgCo2eDstnUnit': 0.035, 'TrainRateForDstnUnit': 0.3, 'PersCarEmssnInKgCo2eDstnUnit': 0.17,
        'EmissionFactorDataSource': 'Illustrative only, for demo data.'})
    # A procurement summary won't save without an inflation rate for its year and currency:
    # spend is deflated to the factor set's year before the factor is applied.
    for year, rate in [('2022', 8.0), ('2023', 4.1), ('2024', 2.9)]:
        r.add('InflationRate', {'CurrencyCode': 'USD', 'CalendarYear': year, 'InflationRate': rate,
                                'DataSource': 'Illustrative only, for demo data.'}, key=('InflationRate', year))

    stage = {'2022': 'Completed', '2023': 'Completed', '2024': 'Data Validation'}
    procurement = r.add('Scope3EmssnSrc', {'Name': 'Procurement - Global', 'Scope3EmissionSourceType': 'Procurement',
                                           'BusinessRegion': 'EMEA', 'Country': 'GB'})
    items, summaries = [], {}
    for year in YEARS:
        footprint = r.add('Scope3CrbnFtprnt', {'Name': f'Procurement {year}', 'Scope3EmssnSrcId': procurement,
                                               'ReportingYear': year, 'FootprintStage': stage[year]})
        summary = r.add('Scope3PcmtSummary', {'Name': f'Procurement Summary {year}', 'Scope3CrbnFtprntId': footprint,
                                              'Scope3EmssnSrcId': procurement, 'CalendarYear': year,
                                              'CurrencyCode': 'USD', 'PcmtEmssnFctrId': pcmt_set})
        summaries[year] = summary
        for supplier, factor, annual, purchases in SUPPLIERS:
            if factor == 'Construction and fit-out' and year != '2023':
                continue   # a one-off project
            category = next(c for n, c, *_ in PCMT_FACTORS if n == factor)
            for purchase in purchases:
                items.append({'Name': f'{purchase} {year}', 'ProcurementSummaryId': summary,
                              'PcmtEmssnFctrSetItemId': r.refs[('PcmtEmssnFctrSetItem', factor)],
                              'SupplierId': r.refs[('Supplier', supplier)], 'Scope3GhgCategory': category,
                              'SpendingCategory1': factor, 'SpendingCategory2': purchase,
                              'SpentAmount': round(annual / len(purchases) * TREND[year] * noise(), -2),
                              'SpentDate': f'{year}-{rng.randint(1, 12):02d}-15'})
    for supplier, purchase, category, year, spend in UNFACTORED:
        items.append({'Name': f'{purchase} {year}', 'ProcurementSummaryId': summaries[year],
                      'SupplierId': r.refs[('Supplier', supplier)], 'SpendingCategory1': category,
                      'SpendingCategory2': purchase, 'SpentAmount': spend, 'SpentDate': f'{year}-09-30'})
    for item in items:
        r.add('Scope3PcmtItem', item, key=('item', item['Name']))

    flights, stays, rides = [], [], []
    airlines = [r.refs[('Supplier', 'Skyward Airlines')], r.refs[('Supplier', 'Polar Air')]]
    for region, country, routes, hotel_country in TRAVEL_REGIONS:
        source = r.add('Scope3EmssnSrc', {'Name': f'Business Travel - {region}', 'Scope3EmissionSourceType': 'Business Travel',
                                          'BusinessRegion': region, 'Country': country,
                                          'AirTravelEmssnFctrId': air, 'HotelStayEmssnFctrId': hotel,
                                          'GroundTravelEmssnFctrId': ground})
        for year in YEARS:
            footprint = r.add('Scope3CrbnFtprnt', {'Name': f'Business Travel {region} {year}', 'Scope3EmssnSrcId': source,
                                                   'ReportingYear': year, 'FootprintStage': stage[year]})
            for trip, (origin, dest, km) in enumerate(routes * 2, start=1):
                month = rng.randint(1, 12)
                flights.append({'Name': f'{origin}-{dest} {year} #{trip}', 'Scope3EmssnSrcId': source,
                                'Scope3CrbnFtprntId': footprint, 'AirTravelEmssnFctrId': air,
                                'SupplierId': airlines[trip % 2], 'CostCenter': rng.choice(COST_CENTERS),
                                'SegmentDistance': km * 2, 'SegmentDistanceUnit': 'Kilometers',
                                'SourceCountry': country, 'TravelerBaseCountry': country,
                                'StartDate': f'{year}-{month:02d}-03', 'EndDate': f'{year}-{month:02d}-07'})
            for stay in range(1, 5):
                month, nights = rng.randint(1, 12), rng.randint(2, 5)
                stays.append({'Name': f'Hotel {region} {year} #{stay}', 'Scope3EmssnSrcId': source,
                              'Scope3CrbnFtprntId': footprint, 'HotelStayEmssnFctrId': hotel,
                              'SupplierId': r.refs[('Supplier', 'Harbor Hotels Group')], 'CostCenter': rng.choice(COST_CENTERS),
                              'RoomCount': 1, 'StayNightsCount': nights, 'HotelCountry': hotel_country,
                              'StartDate': f'{year}-{month:02d}-10', 'EndDate': f'{year}-{month:02d}-{10 + nights}'})
            for ride in range(1, 7):
                month = rng.randint(1, 12)
                rides.append({'Name': f'Taxi {region} {year} #{ride}', 'Scope3EmssnSrcId': source,
                              'Scope3CrbnFtprntId': footprint, 'GroundTravelEmssnFctrId': ground,
                              'SupplierId': r.refs[('Supplier', 'CityCab Network')], 'ExpenseType': 'Taxi',
                              'Scope3GhgCategory': 'BusinessTravel', 'Distance': rng.randint(10, 45),
                              'DistanceUnit': 'Kilometers', 'CostCenter': rng.choice(COST_CENTERS),
                              'StartDate': f'{year}-{month:02d}-12', 'EndDate': f'{year}-{month:02d}-12'})
            for car in range(1, 3):
                rides.append({'Name': f'Commuting {region} {year} #{car}', 'Scope3EmssnSrcId': source,
                              'Scope3CrbnFtprntId': footprint, 'GroundTravelEmssnFctrId': ground,
                              'ExpenseType': 'PersonalCarDistance', 'Scope3GhgCategory': 'EmployeeCommuting',
                              'Distance': rng.randint(1200, 4000), 'DistanceUnit': 'Kilometers',
                              'CostCenter': rng.choice(COST_CENTERS),
                              'StartDate': f'{year}-{6 * car - 5:02d}-01', 'EndDate': f'{year}-{6 * car:02d}-28'})
    for f in flights:
        r.add('AirTravelEnrgyUse', f)
    for s in stays:
        r.add('HotelStayEnrgyUse', s)
    for g in rides:
        r.add('GroundTravelEnrgyUse', g)
    for name, kind, region, country in UNTRACKED_SOURCES:
        r.add('Scope3EmssnSrc', {'Name': name, 'Scope3EmissionSourceType': kind, 'BusinessRegion': region, 'Country': country})


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
