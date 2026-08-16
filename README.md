# nzc-customreports

[![Validate metadata](https://github.com/mshresponse/nzc-customreports/actions/workflows/validate.yml/badge.svg)](https://github.com/mshresponse/nzc-customreports/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A free, open-source set of basic **Lightning Report Types, Reports, and Dashboards** for **Salesforce Net Zero Cloud** — now branded **Agentforce Net Zero** — using core Lightning analytics only, with no CRM Analytics or Einstein components. Source API version **67.0**.

## Install

**One click, no CLI.** Deploys straight from this repo into your org via the
[GitHub Salesforce Deploy Tool](https://github.com/afawcett/githubsfdeploy) — pick
Production/Developer or Sandbox on the page that opens, authorise, and it deploys.

<a href="https://githubsfdeploy.herokuapp.com/app/githubdeploy/mshresponse/nzc-customreports?ref=main">
  <img alt="Deploy to Salesforce" src="https://raw.githubusercontent.com/afawcett/githubsfdeploy/master/deploy.png">
</a>

### Before you install: you need an org that actually has Net Zero Cloud

This is the step people lose an afternoon to. **A standard free Developer Edition
org does not include Net Zero Cloud, and neither does a standard Trailhead
Playground.** Salesforce's own docs list Net Zero Cloud as "available in
Enterprise, Performance, Unlimited, and Developer Editions", but that describes
which editions the licence *can* be added to — it is not what you get when you
sign up for a free org. Without the licence, the NZC objects do not exist and the
deploy fails on unknown sObjects.

Orgs that do work:

| Org | Free? | Lasts | Notes |
|---|---|---|---|
| [Net Zero Cloud trial — Learning org](https://developer.salesforce.com/free-trials/comparison/net-zero-cloud) | Yes | 30 days | Pre-configured, with sample data. Best for seeing these reports return actual rows. |
| [Net Zero Cloud trial — Base org](https://developer.salesforce.com/free-trials/comparison/net-zero-cloud) | Yes | 30 days | Unconfigured. Licences and permissions only, so reports deploy but come back empty until you load data. |
| [Trailhead promo Developer Edition org](https://trailhead.salesforce.com/promo/orgs/net-zero-cloud) | Yes | Check at signup | A special DE org licensed for Agentforce Net Zero, linked from Trailhead's [Configure an Agentforce Net Zero Org](https://trailhead.salesforce.com/content/learn/projects/configure-a-net-zero-cloud-org) project. Some product-specific DE orgs carry a time-limited product licence even though the org itself does not expire — confirm on the signup page. |
| Your own org or sandbox with NZC licensed | — | — | Deploy to a sandbox first. |

The objects the report types build on are `StnryAssetEnvrSrc`,
`StnryAssetCrbnFtprnt`, `StnryAssetEnrgyUse`, `Supplier` and `VehicleAssetEnrgyUse`.
If you can see those in Setup → Object Manager, you are good.

### What the deploy button actually does

Worth being precise, because "unmanaged package" gets used loosely and this is not one:

- It is a **Metadata API deploy of source**, not a package install. Nothing appears
  under Setup → Installed Packages.
- Everything lands as **ordinary org metadata you own** — editable, renameable and
  deletable like anything you built yourself. There is no uninstall button; to
  remove it, delete the components.
- The deploy is **all-or-nothing** (`rollbackOnError`). If your org is missing the
  NZC objects, the deploy fails and leaves nothing behind.
- The deploying user needs **Modify Metadata Through Metadata API Functions** or
  **Modify All Data** — any System Administrator has this.
- The tool converts the whole `force-app` directory with `force:source:convert` and
  generates its own manifest, so `manifest/package.xml` is used by the CLI path and
  by CI, not by the button. Both cover the same 13 components.

### After you install

Deployed report and dashboard folders land **private to the deploying user**.
Nobody else sees them until you share the folders:

1. Reports tab → **All Folders** → *NZC Reports* → **Share**
2. Dashboards tab → **All Folders** → *NZC Dashboards* → **Share**

Give the roles, groups or users who need them **Viewer** access (or **Editor** if
you want them adapting the reports, which is rather the point of shipping the
source).

The dashboard runs as **the logged-in user**, so there is no running user to fix up
after the deploy — each viewer sees what their own sharing allows. On a Base trial
org the reports will deploy and open cleanly but return no rows until you load
data; that is expected, not a failed install.

### Prefer the CLI?

```bash
sf project deploy start --manifest manifest/package.xml --target-org <your-org-alias>
```

Add `--dry-run` to validate without saving anything to the org.

## What's included

| Component | API Name | Details |
|---|---|---|
| Custom Report Type | `Stationary_Assets_with_without_Carbon_Footprints` | `StnryAssetEnvrSrc` with/without `StnryAssetCrbnFtprnt` (outer join) |
| Custom Report Type | `Footprints_with_Energy_Uses` | `StnryAssetCrbnFtprnt` with `StnryAssetEnrgyUse` (inner join) |
| Custom Report Type | `Accounts_with_or_without_Suppliers` | `Account` with/without `Supplier` (outer join) |
| Custom Report Type | `Standalone_Carbon_Footprints` | Single object: `StnryAssetCrbnFtprnt` |
| Custom Report Type | `Standalone_Vehicle_Energy_Uses` | Single object: `VehicleAssetEnrgyUse` |
| Report | `NZC_Reports/Stationary_Assets_Missing_Footprints` | Summary report grouped by `StationaryAssetType`, filtered to rows where the related Carbon Footprint Id is blank |
| Report | `NZC_Reports/Fuel_Consumption_by_Fuel_Type` | Summary report grouped by fuel type, with summed fuel consumption |
| Report | `NZC_Reports/Accounts_Not_Registered_As_Suppliers` | Accounts with no related Supplier record, grouped by industry |
| Report | `NZC_Reports/Emissions_by_Reporting_Year` | Footprints grouped by reporting year, with summed Scope 1 and both Scope 2 accounting bases |
| Report | `NZC_Reports/Fleet_Fuel_by_Fuel_Type` | Vehicle energy use records grouped by fuel type, with summed consumption and distance |
| Dashboard | `NZC_Dashboards/NZC_Emissions_Coverage` | Bar charts for asset and supplier data gaps, column chart of Scope 1 by year, donut of fleet fuel by type |

All report type layouts are curated to the fields sustainability teams use most (asset name, asset type, reporting year, footprint stage, Scope 1 and Scope 2 emissions in tCO2e, fuel type and consumption), and every curated column is flagged `checkedByDefault` so it is pre-selected when users build a new report.

> **Note:** The first report type's label is "Stationary Assets with/without Carbon Footprints" (rather than "…with or without…") to stay within the 50-character report type label limit.

### Two deliberate modelling choices

**No combined emissions total.** Net Zero Cloud splits Scope 2 into
`TotScope2LocBasedEmissions` and `TotScope2MktBasedEmissions`, which are two
accounting methods for the *same* emissions rather than two separate sources. Adding
both to Scope 1 would double count, so "Emissions by Reporting Year" reports the three
figures side by side and leaves the choice of Scope 2 basis to whoever owns the
disclosure. There is no `TotalCarbonFootprint` field on the object to fall back on.

**Fleet fuel comes from the energy use record.** `VehicleAssetEmssnSrc` carries
`VehicleType` and `FleetVehicleType` but no fuel field — fuel lives on
`VehicleAssetEnrgyUse`. The fleet report is therefore built on the energy use object,
which also gives it `FuelConsumption` and `Distance`.

## Verifying relationship names

Three of the five report types join a parent object to its children, and a custom report
type join needs the **child relationship name** — the plural, such as
`StnryAssetCrbnFtprnts`. Salesforce's object reference documents the parent-side
relationship name but never the child-side plural, so the three names in this repo follow
the naming convention rather than a published value. They are marked with a
`VERIFY IN ORG` comment in the XML.

If a deploy fails on one of them, read the real name from your org and replace it in both
the `<relationship>` element and the `<table>` paths of that report type. In Setup →
**Developer Console** → **Debug → Open Execute Anonymous Window**, tick **Open Log** and run:

```apex
for (String o : new List<String>{'StnryAssetEnvrSrc','StnryAssetCrbnFtprnt','Account'}) {
  for (Schema.ChildRelationship cr : Schema.getGlobalDescribe().get(o).getDescribe().getChildRelationships()) {
    if (cr.getRelationshipName() != null) {
      System.debug(LoggingLevel.ERROR, o + ' -> ' + cr.getRelationshipName() + '  (child: ' + cr.getChildSObject() + ')');
    }
  }
}
```

Tick **Debug Only** in the log window to read the results. Or, with the CLI:

```bash
sf sobject describe --sobject StnryAssetEnvrSrc --target-org <alias> \
  | jq -r '.childRelationships[] | select(.relationshipName != null) | "\(.relationshipName) <- \(.childSObject)"'
```

## Project structure

```
manifest/package.xml
force-app/main/default/
├── reportTypes/
│   ├── Stationary_Assets_with_without_Carbon_Footprints.reportType-meta.xml
│   ├── Footprints_with_Energy_Uses.reportType-meta.xml
│   ├── Accounts_with_or_without_Suppliers.reportType-meta.xml
│   ├── Standalone_Carbon_Footprints.reportType-meta.xml
│   └── Standalone_Vehicle_Energy_Uses.reportType-meta.xml
├── reports/
│   ├── NZC_Reports.reportFolder-meta.xml
│   └── NZC_Reports/
│       ├── Stationary_Assets_Missing_Footprints.report-meta.xml
│       ├── Fuel_Consumption_by_Fuel_Type.report-meta.xml
│       ├── Accounts_Not_Registered_As_Suppliers.report-meta.xml
│       ├── Emissions_by_Reporting_Year.report-meta.xml
│       └── Fleet_Fuel_by_Fuel_Type.report-meta.xml
└── dashboards/
    ├── NZC_Dashboards.dashboardFolder-meta.xml
    └── NZC_Dashboards/NZC_Emissions_Coverage.dashboard-meta.xml
```

## Continuous integration

Every push and pull request runs `.github/workflows/validate.yml`, which:

1. Checks that every XML file is well-formed.
2. Runs `sf project convert source` to validate the SFDX project structure and metadata file suffixes (no org required).
3. Cross-checks that every member listed in `manifest/package.xml` has a matching source file.

**What CI cannot tell you.** None of those three checks can see a wrong sObject or field
name — a reference to an object that does not exist produces perfectly well-formed XML
that converts cleanly and matches the manifest. A green badge here means the *structure*
is sound, not that the names resolve. Only a deploy against an org holding the Net Zero
Cloud licence can confirm that:

```bash
sf project deploy start --manifest manifest/package.xml --target-org <alias> --dry-run
```

Object and field names in this repo were verified against the
[Net Zero Cloud Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.netzero_cloud_dev_guide.meta/netzero_cloud_dev_guide/netzero_cloud_std_objects_parent.htm)
for **API 67.0 (Summer '26)**. Salesforce publishes a "New and Changed Objects for Net Zero
Cloud" section every release, so treat these as version-pinned and re-run the dry run after
a major upgrade. The three child relationship names are the exception — see
[Verifying relationship names](#verifying-relationship-names) above.

## License

Free to use, modify, and redistribute.
