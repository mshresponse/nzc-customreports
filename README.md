# nzc-customreports

A free, unmanaged, open-source package of basic **Lightning Report Types, Reports, and Dashboards** for **Salesforce Net Zero Cloud** (core Lightning analytics only — no CRM Analytics / Einstein components). Metadata API version **60.0**.

## What's included

| Component | API Name | Details |
|---|---|---|
| Custom Report Type | `Stationary_Assets_with_without_Carbon_Footprints` | `StnryAsstEnvrSrc` with/without `StnryAsstCrbnFprint` (outer join) |
| Custom Report Type | `Footprints_with_Energy_Uses` | `StnryAsstCrbnFprint` with `StnryAsstFossilFuelEnrgyUse` (inner join) |
| Custom Report Type | `Accounts_with_or_without_Supplier_Metrics` | `Account` with/without `SpplrMtrc` (outer join) |
| Custom Report Type | `Standalone_Carbon_Footprints` | Single object: `StnryAsstCrbnFprint` |
| Custom Report Type | `Standalone_Vehicle_Assets` | Single object: `VehicleAsset` |
| Report | `NZC_Reports/Stationary_Assets_Missing_Footprints` | Summary report grouped by asset type (record type), filtered to rows where the related Carbon Footprint Id is blank |
| Dashboard | `NZC_Dashboards/NZC_Emissions_Coverage` | Bar chart of assets missing carbon footprints, by asset type |

All report type layouts are curated to the fields sustainability teams use most (asset name, reporting year, stage, Scope 1 / Scope 2 emissions (tCO2e), fuel type, record type), and every curated column is flagged `checkedByDefault` so it is pre-selected when users build a new report.

> **Note:** The first report type's label is "Stationary Assets with/without Carbon Footprints" (rather than "…with or without…") to stay within the 50-character report type label limit.

## Project structure

```
manifest/package.xml
force-app/main/default/
├── reportTypes/
│   ├── Stationary_Assets_with_without_Carbon_Footprints.reportType-meta.xml
│   ├── Footprints_with_Energy_Uses.reportType-meta.xml
│   ├── Accounts_with_or_without_Supplier_Metrics.reportType-meta.xml
│   ├── Standalone_Carbon_Footprints.reportType-meta.xml
│   └── Standalone_Vehicle_Assets.reportType-meta.xml
├── reports/
│   ├── NZC_Reports.reportFolder-meta.xml
│   └── NZC_Reports/Stationary_Assets_Missing_Footprints.report-meta.xml
└── dashboards/
    ├── NZC_Dashboards.dashboardFolder-meta.xml
    └── NZC_Dashboards/NZC_Emissions_Coverage.dashboard-meta.xml
```

## Prerequisites

- A Salesforce org with the **Net Zero Cloud** license and managed objects enabled (`StnryAsstEnvrSrc`, `StnryAsstCrbnFprint`, `StnryAsstFossilFuelEnrgyUse`, `SpplrMtrc`, `VehicleAsset`).
- Salesforce CLI (`sf`).

## Deploy

```bash
sf project deploy start --manifest manifest/package.xml --target-org <your-org-alias>
```

## Validating API names against your org

Net Zero Cloud field and child-relationship API names can vary slightly by release and license edition. If a deploy fails on a field or relationship name, verify the exact names in your org and adjust the XML:

```bash
sf sobject describe --sobject StnryAsstCrbnFprint --target-org <alias> | jq '.fields[].name'
sf sobject describe --sobject StnryAsstEnvrSrc --target-org <alias> | jq '.childRelationships[] | {relationshipName, childSObject}'
```

The most likely candidates to need adjustment:

- Child relationship names used in the report type joins: `StnryAsstCrbnFprints`, `StnryAsstFossilFuelEnrgyUses`, `SpplrMtrcs`.
- Emissions field spellings on `StnryAsstCrbnFprint` (e.g. `TotalScope2LocationBasedEmissions` / `TotalScope2MarketBasedEmissions`) and metric fields on `SpplrMtrc`.

## License

Free to use, modify, and redistribute.
