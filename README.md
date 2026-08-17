# nzc-customreports

[![Validate metadata](https://github.com/mshresponse/nzc-customreports/actions/workflows/validate.yml/badge.svg)](https://github.com/mshresponse/nzc-customreports/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**16 custom report types, 16 reports and 2 dashboards for Salesforce Net Zero Cloud**
(Agentforce Net Zero), using core Lightning reporting only. No CRM Analytics, no Einstein,
no managed package, no custom objects or fields. API 67.0.

The reports are laid out for **inline editing**, so a sustainability team can correct data
in the report instead of raising a ticket for a CSV re-upload.

---

## Setup — 4 steps

**1. Check your org has Net Zero Cloud.**
Setup → Object Manager. You need to see `StnryAssetEnvrSrc`, `StnryAssetCrbnFtprnt`,
`StnryAssetEnrgyUse`, `VehicleAssetEmssnSrc`, `VehicleAssetCrbnFtprnt` and
`VehicleAssetEnrgyUse`. A free Developer Edition org and a standard Trailhead Playground
do **not** have these — see [Orgs that work](#orgs-that-work).

**2. Deploy.**

```bash
sf project deploy start --manifest manifest/package.xml --target-org <alias>
```

Or one click, no CLI:

<a href="https://githubsfdeploy.herokuapp.com/app/githubdeploy/mshresponse/nzc-customreports?ref=main">
  <img alt="Deploy to Salesforce" src="https://raw.githubusercontent.com/afawcett/githubsfdeploy/master/deploy.png">
</a>

**3. Enable inline editing.**
Setup → **Reports and Dashboards Settings** → tick **Enable Inline Editing in Reports** → Save.

Off by default in most orgs. Without it the reports still run, but read-only.

**4. Share the two folders.**
Reports tab → All Folders → *NZC Reports* → **Share**. Same for *NZC Dashboards*.

Deployed folders are private to whoever deployed them. Give the sustainability team
**Editor** on the report folder.

That's the whole setup. Nothing else to configure, no permission sets, no post-install
script.

---

## What you get

**5 reports you edit directly** — tabular, narrow, every column editable in place:

| Report | Fix in place |
|---|---|
| Asset Names and Locations | Site names, city, country, asset type |
| Fleet Names and Types | Vehicle names and types |
| Footprint Data Entry | Reporting year, stage, Scope 1 and Scope 2 figures |
| Energy Use Data Entry | Fuel type, consumption, unit |
| Fleet Energy Data Entry | Fuel type, consumption, distance |

**4 reports that find missing records** — outer joins, grouped by asset type:

Stationary Assets Missing Footprints · Stationary Assets Missing Energy Use ·
Fleet Assets Missing Footprints · Fleet Assets Missing Energy Use

**4 reports that find orphans** — child records whose parent lookup is blank, which a join
can never show you:

Orphaned Carbon Footprints · Orphaned Stationary Energy Uses · Orphaned Fleet Footprints ·
Orphaned Vehicle Energy Uses

An orphaned footprint still contributes to a total. It's a number in your disclosure that
nothing explains.

**3 summaries** — Emissions by Reporting Year, Fuel Consumption by Fuel Type, Fleet Fuel by
Fuel Type.

**16 report types** covering both stationary and fleet, in three shapes each — `with`
(inner join), `with/without` (outer join), and standalone. Build your own reports on any of
them; that's rather the point of shipping the source.

**2 dashboards** — NZC Data Quality and NZC Emissions Coverage.

---

## Why this doesn't come with the product

Net Zero Cloud ships **CRM Analytics dashboards**, and those need a separate licence. From
the [Net Zero Cloud Developer Guide, v67.0 Summer '26](https://developer.salesforce.com/docs/atlas.en-us.netzero_cloud_dev_guide.meta/netzero_cloud_dev_guide/netzero_cloud_std_objects_intro.htm),
page 1:

> The Net Zero Cloud Analytics dashboards are available only for Salesforce Net Zero Cloud
> users with CRM Analytics for Net Zero Cloud add-on license.

It ships **no standard Lightning report types** for the emissions objects. You can verify
that in your own org:

```bash
sf data query --use-tooling-api --target-org <alias> --query \
"SELECT QualifiedApiName, IsReportingEnabled FROM EntityDefinition \
 WHERE QualifiedApiName LIKE 'StnryAsset%' OR QualifiedApiName LIKE 'VehicleAsset%'"
```

Every NZC object returns `IsReportingEnabled = false`, which is the flag governing whether
Salesforce auto-generates standard report types. It's read-only on standard objects, so
there's nothing to switch on. A custom report type isn't a refinement here — it's the only
way to report on Net Zero Cloud data at all.

---

## Inline editing: what it can't do

The limits shaped the report layouts, so they're worth knowing before you promise anything:

| Rule | Consequence |
|---|---|
| Tabular, summary and matrix only | No joined reports. None here are joined. |
| 12 editable fields per row, 100 per report | The data-entry reports are narrow on purpose. |
| Grouping fields are not editable | Group by something you don't need to fix. |
| A lookup that's null across the row can't be edited | You can't create a missing record from a report. |
| FLS and validation rules still apply | A failing edit shows the rule's own message. |

That fourth row is why the **Missing** reports are upload worklists, not fix-it-here
reports. If an asset has no footprint record, there's no footprint row to edit. Inline
editing fixes what exists; it doesn't conjure records.

---

<a name="orgs-that-work"></a>
## Orgs that work

| Org | Free? | Lasts | Notes |
|---|---|---|---|
| [NZC trial — Learning org](https://developer.salesforce.com/free-trials/comparison/net-zero-cloud) | Yes | 30 days | Pre-configured with sample data. |
| [NZC trial — Base org](https://developer.salesforce.com/free-trials/comparison/net-zero-cloud) | Yes | 30 days | Licences only. Reports deploy but return nothing until you load data — see [`sample-data/`](sample-data/). |
| [Trailhead promo DE org](https://trailhead.salesforce.com/promo/orgs/net-zero-cloud) | Yes | Check at signup | Licensed for Agentforce Net Zero. |
| Your own licensed org or sandbox | — | — | Deploy to a sandbox first. |

Salesforce's docs list NZC as available in Enterprise, Performance, Unlimited and Developer
Editions. That describes which editions the licence *can be added to*, not what you get on
signup — which is where the afternoon goes.

## What the deploy does

- A **Metadata API deploy of source**, not a package install. Nothing appears under Setup →
  Installed Packages.
- Everything lands as **ordinary metadata you own** — editable, renameable, deletable. No
  uninstall button; delete the components.
- **All-or-nothing** (`rollbackOnError`). A failure leaves nothing behind.
- Deploying user needs **Modify Metadata Through Metadata API Functions** or **Modify All
  Data**.

## Two modelling choices worth knowing

**No combined emissions total.** NZC splits Scope 2 into `TotScope2LocBasedEmissions` and
`TotScope2MktBasedEmissions` — two accounting methods for the *same* emissions, not two
sources. Adding both to Scope 1 double counts. Emissions by Reporting Year reports the
three side by side and leaves the choice of basis to whoever owns the disclosure. Don't
substitute the `SuplScope*` fields; they measure something different, and using them
produces a report that runs cleanly and reports the wrong number.

**Fleet fuel comes from the energy use record.** `VehicleAssetEmssnSrc` has no fuel field —
fuel, consumption and distance all live on `VehicleAssetEnrgyUse`.

## Also in this repo

- [`sample-data/`](sample-data/) — six UTF-8 CSVs with deliberate gaps and orphans, so the
  Missing and Orphaned reports return rows on an empty trial org.
- [`docs/encoding-evidence/`](docs/encoding-evidence/) — why accented site names arrive as
  question marks, and which step is responsible.
- [`docs/building-your-own.md`](docs/building-your-own.md) — the report type metadata
  gotchas, for anyone forking this.

## Continuous integration

`.github/workflows/validate.yml` checks XML well-formedness, that `sf project convert
source` succeeds, and that manifest members have matching files.

**None of that can see a wrong object or field name.** A reference to an object that does
not exist produces well-formed XML that converts cleanly and matches the manifest. This
repo carried a green badge while referencing five objects that don't exist. Only a deploy
against a licensed org proves the names resolve:

```bash
sf project deploy start --manifest manifest/package.xml --target-org <alias> --dry-run
```

## License

MIT.
