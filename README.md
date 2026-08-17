# nzc-customreports

[![Validate metadata](https://github.com/mshresponse/nzc-customreports/actions/workflows/validate.yml/badge.svg)](https://github.com/mshresponse/nzc-customreports/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Custom report types, reports and dashboards for **Salesforce Net Zero Cloud** — now
branded **Agentforce Net Zero** — built on core Lightning analytics only. No CRM
Analytics, no Einstein, no managed package.

## What this is for

**So a sustainability team can fix its own data.**

The usual Net Zero Cloud correction loop is: someone on the ESG team spots a wrong
site name or a missing fuel figure, files a ticket, an admin exports a CSV, someone
edits the CSV, the admin re-uploads it, and a week later the number is right. For a
one-character typo. The alternative is opening records one at a time, which nobody
does for four hundred assets.

Reports with **inline editing** collapse that loop. The ESG team opens a report, edits
the cell, saves, and the record is updated — no ticket, no CSV, no admin. Everything in
this repo exists to make that possible: report types that expose the editable fields,
and reports laid out so the fields are actually editable when you open them.

The gap-finding and orphan reports serve the same end from the other side — they tell
you *which* records need attention before the audit does.

## Why this isn't in the product already

Net Zero Cloud ships with CRM Analytics dashboards. Those look good in a demo, but CRM
Analytics is a separately-licensed add-on with its own deployment story, and plenty of
organisations either don't have it or can't get dataflows through change control. What
NZC does not ship is the unglamorous layer underneath — ordinary Lightning reports that
let you confirm data loaded correctly and fix it when it didn't.

That's the gap this fills. It is deliberately boring technology: report types, reports,
folders. Everything here is metadata you own and can edit.

## Install

```bash
sf project deploy start --manifest manifest/package.xml --target-org <alias>
```

Add `--dry-run` to validate without saving anything.

There are also three narrower manifests — `package-1-report-types.xml`,
`package-2-reports.xml`, `package-3-dashboards.xml` — for landing one layer at a time.
The deploy is all-or-nothing, so a failure tells you nothing about which layer caused it;
deploying in stages narrows that down. Use them when diagnosing, not as the normal path.

### You need an org that actually has Net Zero Cloud

This is the step people lose an afternoon to. **A standard free Developer Edition org
does not include Net Zero Cloud, and neither does a standard Trailhead Playground.**
Salesforce's docs list NZC as available in Enterprise, Performance, Unlimited and
Developer Editions, but that describes which editions the licence *can be added to* —
not what you get when you sign up for a free org. Without the licence the NZC objects
don't exist and the deploy fails on unknown sObjects.

| Org | Free? | Lasts | Notes |
|---|---|---|---|
| [NZC trial — Learning org](https://developer.salesforce.com/free-trials/comparison/net-zero-cloud) | Yes | 30 days | Pre-configured, with sample data. Best for seeing these return actual rows. |
| [NZC trial — Base org](https://developer.salesforce.com/free-trials/comparison/net-zero-cloud) | Yes | 30 days | Licences and permissions only. Reports deploy but come back empty until you load data. |
| [Trailhead promo DE org](https://trailhead.salesforce.com/promo/orgs/net-zero-cloud) | Yes | Check at signup | A DE org licensed for Agentforce Net Zero. Confirm the terms on the signup page. |
| Your own licensed org or sandbox | — | — | Deploy to a sandbox first. |

If you can see `StnryAssetEnvrSrc`, `StnryAssetCrbnFtprnt`, `StnryAssetEnrgyUse`,
`VehicleAssetEmssnSrc`, `VehicleAssetCrbnFtprnt` and `VehicleAssetEnrgyUse` in Setup →
Object Manager, you're good.

### What the deploy actually does

"Unmanaged package" gets used loosely and this is not one:

- It's a **Metadata API deploy of source**, not a package install. Nothing appears under
  Setup → Installed Packages.
- Everything lands as **ordinary org metadata you own** — editable, renameable, deletable.
  There's no uninstall button; to remove it, delete the components.
- Each stage is **all-or-nothing** (`rollbackOnError`). A failed stage leaves nothing behind.
- The deploying user needs **Modify Metadata Through Metadata API Functions** or **Modify
  All Data**. Any System Administrator has this.

## After you install: two things to switch on

### 1. Enable inline editing, or none of this works

Setup → **Reports and Dashboards Settings** → tick **Enable Inline Editing in Reports** → Save.

Without it every report here still runs, but read-only — which removes the entire point.
It is off by default in most orgs.

### 2. Share the folders

Deployed report and dashboard folders land **private to the deploying user**. Nobody else
sees them until you share:

1. Reports tab → **All Folders** → *NZC Reports* → **Share**
2. Dashboards tab → **All Folders** → *NZC Dashboards* → **Share**

Give the ESG team **Editor** on the report folder. Viewer is enough to read but not to
save an edited report layout.

The dashboards run as **the logged-in user**, so there's no running user to fix up — each
viewer sees what their own sharing allows.

## What inline editing can and cannot do

Worth knowing before you promise it to anyone, because the limits are not obvious and
they shaped how these reports are laid out.

| Rule | Consequence |
|---|---|
| Tabular, summary and matrix reports only | Joined reports can't inline edit. None here are joined. |
| Up to **12 editable fields per row**, **100 per report** | Data-entry reports here are kept narrow on purpose. |
| Grouping fields are **not** editable | Group by something you don't need to fix. The gap reports group by asset type for this reason. |
| A lookup that is entirely null on a row can't be edited | You cannot create a missing child record from a report. |
| Field-level security and validation rules still apply | An edit that fails validation fails in the report, with the rule's message. |

That last-but-one row is why the **Missing** reports are described as upload worklists
rather than fix-it-here reports: if an asset has no footprint record at all, there is no
footprint row to edit. You still need a load for creation. Inline editing fixes what
exists; it does not conjure records.

## What's included

### Report types (16)

A deliberate matrix. For both stationary and fleet, and for both the footprint and the
energy-use branch, you get three shapes:

| Shape | Join | Answers |
|---|---|---|
| **with** | inner | "Show me the assets that have this, and let me edit both sides" |
| **with/without** | outer | "Which assets are missing this?" |
| **standalone** | none | "Show me every record of this type, including ones whose parent is gone" |

| API name | Label | Base → child |
|---|---|---|
| `Standalone_Stationary_Assets` | NZC: Assets (all) | `StnryAssetEnvrSrc` |
| `Standalone_Carbon_Footprints` | NZC: Footprints (all) | `StnryAssetCrbnFtprnt` |
| `Standalone_Stationary_Energy_Uses` | NZC: Energy Uses (all) | `StnryAssetEnrgyUse` |
| `Stationary_Assets_with_Carbon_Footprints` | NZC: Assets with Footprints | `StnryAssetEnvrSrc` → `StnryAssetCrbnFtprnt` |
| `Stationary_Assets_with_without_Carbon_Footprints` | NZC: Assets with/without Footprints | same, outer join |
| `Stationary_Assets_with_Energy_Use` | NZC: Assets with Energy Use | `StnryAssetEnvrSrc` → `StnryAssetEnrgyUse` |
| `Stationary_Assets_with_without_Energy_Use` | NZC: Assets with/without Energy Use | same, outer join |
| `Footprints_with_Energy_Uses` | NZC: Footprints with Energy Uses | `StnryAssetCrbnFtprnt` → `StnryAssetEnrgyUse` |
| `Standalone_Vehicle_Assets` | NZC: Fleet Assets (all) | `VehicleAssetEmssnSrc` |
| `Standalone_Vehicle_Carbon_Footprints` | NZC: Fleet Footprints (all) | `VehicleAssetCrbnFtprnt` |
| `Standalone_Vehicle_Energy_Uses` | NZC: Fleet Energy Uses (all) | `VehicleAssetEnrgyUse` |
| `Vehicle_Assets_with_Carbon_Footprints` | NZC: Fleet with Footprints | `VehicleAssetEmssnSrc` → `VehicleAssetCrbnFtprnt` |
| `Vehicle_Assets_with_without_Carbon_Footprints` | NZC: Fleet with/without Footprints | same, outer join |
| `Vehicle_Assets_with_Energy_Use` | NZC: Fleet with Energy Use | `VehicleAssetEmssnSrc` → `VehicleAssetEnrgyUse` |
| `Vehicle_Assets_with_without_Energy_Use` | NZC: Fleet with/without Energy Use | same, outer join |
| `Vehicle_Footprints_with_Energy_Uses` | NZC: Fleet Footprints with Energy Uses | `VehicleAssetCrbnFtprnt` → `VehicleAssetEnrgyUse` |

### Reports (16), in three groups

**Fix it here** — tabular, narrow, every column editable:

| Report | Built on | Use |
|---|---|---|
| Asset Names and Locations | Assets (all) | Correct site names, cities, countries, asset type |
| Fleet Names and Types | Fleet Assets (all) | Correct vehicle names and types |
| Footprint Data Entry | Assets with Footprints | Reporting year, stage, Scope 1 and 2 figures |
| Energy Use Data Entry | Assets with Energy Use | Fuel type, consumption, unit |
| Fleet Energy Data Entry | Fleet with Energy Use | Fuel type, consumption, distance |

**Find the gaps** — summary, grouped, outer joins:

| Report | Built on | Finds |
|---|---|---|
| Stationary Assets Missing Footprints | Assets with/without Footprints | Assets with no footprint record |
| Stationary Assets Missing Energy Use | Assets with/without Energy Use | Assets with no energy use record |
| Fleet Assets Missing Footprints | Fleet with/without Footprints | Vehicles with no footprint record |
| Fleet Assets Missing Energy Use | Fleet with/without Energy Use | Vehicles with no energy use record |

**Find the orphans** — records whose parent lookup is blank, which joins can never show you:

| Report | Built on |
|---|---|
| Orphaned Carbon Footprints | Footprints (all) |
| Orphaned Stationary Energy Uses | Energy Uses (all) |
| Orphaned Fleet Footprints | Fleet Footprints (all) |
| Orphaned Vehicle Energy Uses | Fleet Energy Uses (all) |

Orphans matter because a footprint with no asset still contributes to a total. It's a
number in your disclosure that nothing explains — the kind of thing an assurance provider
finds and you don't.

**Plus two summaries** — Emissions by Reporting Year, and Fuel Consumption by Fuel Type
(stationary) / Fleet Fuel by Fuel Type.

### Dashboards (2)

`NZC_Data_Quality` — coverage and gap counts.
`NZC_Emissions_Coverage` — Scope 1 by reporting year, stationary fuel mix, fleet fuel mix.

## Two deliberate modelling choices

**No combined emissions total.** NZC splits Scope 2 into `TotScope2LocBasedEmissions` and
`TotScope2MktBasedEmissions` — two accounting methods for the *same* emissions, not two
sources. Adding both to Scope 1 double counts. "Emissions by Reporting Year" reports the
three figures side by side and leaves the choice of Scope 2 basis to whoever owns the
disclosure. There is no `TotalCarbonFootprint` field to fall back on, by design.

Do **not** substitute the `SuplScope*` fields. Those are supplemental figures measuring
something different. Mapping them produces a report that runs cleanly and reports the
wrong number, which is worse than a failed deploy.

**Fleet fuel comes from the energy use record.** `VehicleAssetEmssnSrc` carries
`VehicleType` and `FleetVehicleType` but no fuel field — fuel lives on
`VehicleAssetEnrgyUse`, along with `FuelConsumption` and `Distance`.

## Three name spaces, and the traps between them

The most expensive lessons in building this, in the order they cost time. Each one is a
case of the same identifier having a different form depending on which layer is asking.

### 1. Report type joins don't use describe names

**A custom report type does not address objects the way describe does.**

Describe gives you the *child relationship name* — a plural like `StnryAssetCrbnFtprnts`.
That is the correct answer to a different question. Report type metadata wants the **child
object's API name**:

```xml
<join>
    <outerJoin>true</outerJoin>
    <relationship>StnryAssetCrbnFtprnt</relationship>   <!-- object API name, singular -->
</join>
```

And `<table>` chains object API names, one segment per level:

```
StnryAssetEnvrSrc
StnryAssetEnvrSrc.StnryAssetCrbnFtprnt
StnryAssetEnvrSrc.StnryAssetCrbnFtprnt.StnryAssetEnrgyUse
```

Parent lookup columns use the **relationship name with no `Id` suffix** — `AccountName`,
not `AccountNameId`.

### 2. Reports reference report types with a `__c` suffix

A report type deploys under its plain metadata name. `sf org list metadata --metadata-type
ReportType` returns `Standalone_Stationary_Assets`, and the file on disk is
`Standalone_Stationary_Assets.reportType-meta.xml`. But a **report** must address it as:

```xml
<reportType>Standalone_Stationary_Assets__c</reportType>
```

Without the suffix, every report fails with `invalid report type` — and the error points at
the report type, which sends you looking in the wrong place. The report type is fine. The
name is fine. It's the *reference* that's in the wrong name space.

The `__c` does **not** mean a custom object exists. Nothing in this package creates an
object or a field. It marks the report type as custom rather than standard within the
reporting layer, and it applies to any custom report type, including ones built by hand
through the Setup wizard.

To read the names the report builder will actually accept:

```bash
sf api request rest "/services/data/v67.0/analytics/reportTypes" --target-org <alias>
```

That endpoint is the list the report builder itself consults. It is the authoritative
answer and it disagrees with the Metadata API on purpose.

### 3. A report can only filter on columns the report type exposes

The "missing related record" reports work by outer-joining and filtering where the child's
`Id` is blank. That fails with `Invalid field name: Parent.Child$Id` unless `Id` is a
column in the report type — even though every record has one.

So the four `with/without` report types carry `Id` on the child object as an unchecked
column. Salesforce's own shipped report types do the same thing, which is where the
pattern came from.

### The general lesson

None of these is guessable, and none matches the layer above or below it. If you are
building your own and something won't deploy: **build it in the UI, retrieve it, and read
what Salesforce emitted.** That is the only reliable source, and it resolves in ten seconds
what documentation and inference will not resolve at all.

### Where "is this object reportable?" actually lives

Not in describe. It's on `EntityDefinition`, via the Tooling API:

```bash
sf data query --use-tooling-api --target-org <alias> --query \
"SELECT QualifiedApiName, IsReportingEnabled FROM EntityDefinition \
 WHERE QualifiedApiName LIKE '%Crbn%' OR QualifiedApiName LIKE '%EnrgyUse%'"
```

Worth knowing what it does *not* mean. Every Net Zero Cloud object returns
`IsReportingEnabled = false`, yet all sixteen report types here deploy and run. The flag
describes whether Salesforce auto-generates a **standard** report type for the object, not
whether the object can be reported on. NZC ships none — which is precisely why a custom
report type is not a refinement here but the only way in.

### Reports don't support wildcards

`<members>*</members>` for `Report` in `package.xml` returns an **empty zip, not an error** —
reports, dashboards, documents and email templates all require named folders. This wastes
an afternoon roughly once per career.

## Continuous integration

`.github/workflows/validate.yml` checks XML well-formedness, that `sf project convert
source` succeeds, and that every manifest member has a matching file.

**What CI cannot tell you.** None of those can see a wrong sObject or field name — a
reference to an object that does not exist produces perfectly well-formed XML that
converts cleanly and matches the manifest. A green badge means the *structure* is sound,
not that the names resolve. Only a deploy against a licensed org proves that. This repo
shipped a green badge over five fictional object names for some time; the badge was
accurate about what it measured and misleading about what it implied.

Object and field names are verified against the [Net Zero Cloud Developer
Guide](https://developer.salesforce.com/docs/atlas.en-us.netzero_cloud_dev_guide.meta/netzero_cloud_dev_guide/netzero_cloud_std_objects_parent.htm)
for **API 67.0 (Summer '26)**. Salesforce publishes a "New and Changed Objects" section
every release — treat these as version-pinned and re-run a dry run after a major upgrade.

## Project structure

```
manifest/
├── package.xml                    everything, for tooling that wants one manifest
├── package-1-report-types.xml     stage 1
├── package-2-reports.xml          stage 2
└── package-3-dashboards.xml       stage 3
force-app/main/default/
├── reportTypes/                   16
├── reports/NZC_Reports/           16
└── dashboards/NZC_Dashboards/     2
docs/
└── encoding-evidence/             byte-level proof of the CSV export encoding issue
```

## License

MIT. Free to use, modify and redistribute.
