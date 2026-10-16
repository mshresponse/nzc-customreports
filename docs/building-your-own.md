# Building your own NZC report types

Notes for anyone forking this, or building custom report types on Net Zero Cloud from
scratch. None of this is needed to install the package — see the README for that.

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

A filter on `Parent.Child$Id` fails with `Invalid field name: Parent.Child$Id` unless `Id`
is a column in the report type — even though every record has one. So the four
`with/without` report types carry `Id` on the child object as an unchecked column, and on
the parent too, for the cross filters in the next section. Salesforce's own shipped report
types do the same thing, which is where the pattern came from.

### 4. "Child Id equals blank" does not find parents without children

This one deploys, runs, returns plausible rows, and is wrong — which is why it survived
here for months.

The obvious way to list assets with no footprint is an outer-join report type filtered on
the footprint's `Id` being blank. On a `with/without` report type, that filter is not
applied to the joined rows. It is applied *inside* the join: it removes the footprint rows,
and then every asset still appears, each with a blank footprint. The report returns every
asset you have, and on a dashboard that looks like a large, believable gap.

The construct that means "parents without children" is a **cross filter**:

```xml
<crossFilters>
    <operation>without</operation>
    <primaryTableColumn>StnryAssetEnvrSrc$Id</primaryTableColumn>
    <relatedTable>StnryAssetCrbnFtprnt</relatedTable>
    <relatedTableJoinColumn>StnryAssetEnvrSrc</relatedTableJoinColumn>
</crossFilters>
```

Three things about it you won't guess:

- `primaryTableColumn` is the parent's `Id`, so the report type must expose `Id` on the
  parent or the deploy fails with `Invalid field name: StnryAssetEnvrSrc$Id`.
- `relatedTable` is the child's object API name and `relatedTableJoinColumn` is the
  lookup's relationship name — the same name space as report type joins.
- The Analytics REST API shows the same filter with `primaryEntityField` set to an internal
  key (`072…`), not a field name. Hand-write `StnryAssetEnvrSrc.Id` there and the API
  accepts it, runs the report, and silently ignores the filter. Build it in the report
  builder once and read what comes back.

The test that catches this class of bug isn't a deploy; it is running the report against
data whose answer you already know. That is what `sample-data/` and
`scripts/check-reports.py` are for.

### 5. Net Zero Cloud's own rules shape what an orphan can be

Learned by trying to create the records the Orphaned reports look for:

- A **footprint** can exist without an asset. Those are real orphans, and they still
  contribute to totals.
- An **energy use** cannot. Create one without an asset and you get `insufficient access
  rights on cross-reference id`, even as an admin, and an asset can't be deleted while
  energy use points at it. What does happen is that deleting a *footprint* blanks the
  footprint lookup on every energy use under it. So the Orphaned Energy Use reports look
  for a blank footprint, not a blank everything.
- An **asset** can't be created at all until its object has a record type mapped through
  `StnryAssetEnvSrcCnfg` (or `VehicleAssetEmssnSrcCnfg` for vehicles). Both are Metadata
  API types; `sample-data/org-setup/` has the XML Salesforce emits for them.

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
`IsReportingEnabled = false`, yet all twenty-two report types here deploy and run. The flag
describes whether Salesforce auto-generates a **standard** report type for the object, not
whether the object can be reported on. NZC ships none — which is precisely why a custom
report type is not a refinement here but the only way in.

### Reports don't support wildcards

`<members>*</members>` for `Report` in `package.xml` returns an **empty zip, not an error** —
reports, dashboards, documents and email templates all require named folders. This wastes
an afternoon roughly once per career.

## Matrix reports and dashboard filters

The audit dashboard uses two constructs the rest of the package doesn't.

**A matrix report** is a summary report with a second grouping axis. `groupingsDown` is the
row grouping, `groupingsAcross` the column grouping, and each `<columns>` entry with an
`aggregateTypes` becomes a cell value. Grouping on a lookup column (`…$StnryAssetEnvrSrc`)
groups by the parent's name, which is what you want for one-row-per-asset.

**A dashboard filter** is declared once at the top of the dashboard:

```xml
<dashboardFilters>
    <dashboardFilterOptions>
        <operator>equals</operator>
        <values>2025</values>
    </dashboardFilterOptions>
    <name>Reporting Year</name>
</dashboardFilters>
```

and then each component names *its own* column for that filter, so components on different
report types can share one picker:

```xml
<dashboardFilterColumns>
    <column>VehicleAssetCrbnFtprnt$ReportingYear</column>
</dashboardFilterColumns>
```

The options are literal values, so the year list is hard-coded. Editing it in the dashboard
builder is faster than editing the XML.

## Fuel never shares an axis

Fuel Consumption on an energy use record is in whatever unit its Fuel Consumption Unit says:
kWh for electricity, therms or m³ for gas, liters or gallons for liquid fuels. Summing it
across fuel types produces a number with no unit, and a chart of it puts 170 million kWh on
the same scale as 95 thousand liters. So:

- **Fuel Consumption by Fuel Type** and **Fleet Fuel by Fuel Type** group by fuel type and
  then by unit, so every subtotal is in one unit, and carry `<showGrandTotal>false</showGrandTotal>`
  because there is no meaningful grand total.
- The **Emissions Coverage** dashboard shows them as **tables**, one row per fuel and unit,
  not as charts.
- The two **Orphaned Energy Use** reports carry no sum on consumption, so their dashboard
  charts count records — how many to fix — instead of adding up mixed units.

CO2e is the one measure that does share a unit across fuels, and the Scope 1 and 2 reports and
charts use it. The fuel views stay in physical units because they answer a different question
— how much of each fuel — and because CO2e only exists once an energy use has a factor and a
scope allocation (see *What Net Zero Cloud calculates on save* below).

## Two dashboard formats

NZC Audit and NZC Data Quality are **Classic-format** dashboards: `leftSection`,
`middleSection`, `rightSection`, `isGridLayout` false. NZC Emissions Coverage is
**Lightning-format**: `dashboardGridLayout`, a 12-column grid where each component has
`columnIndex`, `colSpan`, `rowIndex` and `rowSpan`. Both render in Lightning Experience.

The Lightning format exists here because the table component (`FlexTable`, with its
`flexTableColumn` list of groupings and aggregates) is Lightning-only. Opening a Classic
dashboard in the Lightning builder converts it on save; the retrieve then comes back in grid
form with `owner` and `runningUser` stamped in, which have to come out (see below). The
grid's column positions are easier to edit in the XML than by dragging.

## Column labels in report types

Every Net Zero Cloud object's record name field is called Name, so a report on a joined
report type shows two or three columns all headed "Name". `displayNameOverride` on the
report type column renames it for every report built on that type, without touching the
field:

```xml
<columns>
    <checkedByDefault>true</checkedByDefault>
    <displayNameOverride>Asset Name</displayNameOverride>
    <field>Name</field>
    <table>StnryAssetEnvrSrc</table>
</columns>
```

All twenty-two report types here label the name column by object: Asset Name, Vehicle Name,
Footprint Name, Energy Use Name, Procurement Item Name, Scope 3 Source Name and so on.

## What Net Zero Cloud calculates on save

Every scope is calculated on the record as it saves — if the inputs are there. Without them
Net Zero Cloud still computes the gas quantities (CO2 in kg) and leaves every scope field at
zero, which is easy to mistake for "not calculated yet".

- **Stationary energy use** gets Scope 1 or Scope 2 when the record has a factor and its asset
  has a **Carbon Emissions Scope Allocation**. Electricity takes an electricity factor set,
  location- and market-based, whose generation mix adds up to 100%; fuels take an
  other-emissions factor set, per kWh with a calorific value (a per-litre factor computes
  nothing for stationary combustion). The allocation maps each fuel type to a scope —
  electricity to Scope 2, fuels to Scope 1 for an owned site.
- **Vehicle energy use** gets Scope 1 with a per-litre factor and the vehicle's Carbon
  Emissions Scope Allocation picklist set to Scope 1.
- **Scope 3 records** need only their factors. A procurement item gets Final Scope 3 Emissions
  from spend times its factor (deflated to the factor's year, which is why a procurement
  summary refuses to save without an `InflationRate` for its year and currency); a flight gets
  tCO2e from distance and haul band, a hotel stay from nights, ground travel from distance.
- **Roll-ups differ.** Scope 3 footprints filled in by themselves a few minutes after a load.
  Stationary and fleet footprints total their energy use when an energy use is saved — but a
  bulk insert didn't trigger it in testing; saving the records once more did.

## Scope 3
- **The join rule holds even when the lookup isn't named after the parent.** Procurement items
  point at their summary through `ProcurementSummaryId`, but the report type join is still
  `<relationship>Scope3PcmtItem</relationship>`, the child object's API name.
- **Group spend by currency before you total it.** `SpentAmount` is in the currency of its
  procurement summary, so a spend total is only meaningful within one currency — the same
  problem as fuel units. The spend reports group by currency first and carry no grand total;
  tCO2e is the one figure totalled freely.
- **Two dashboard limits the builder enforces and the XML doesn't warn about:** a component
  title is at most 40 characters, and a Metric component needs `indicatorLowColor`,
  `indicatorMiddleColor` and `indicatorHighColor` even when there are no breakpoints.

## Year-over-year change: build it in the UI

The one audit signal deliberately not shipped as metadata is a **% change from the previous
year** column. It's a custom summary formula using `PREVGROUPVAL`, and its metadata form
references columns and groupings by internal keys that can only be confirmed by retrieving a
formula Salesforce itself emitted. Rather than ship a guess that would fail the all-or-nothing
deploy for everyone, add it in the report builder — it takes a minute:

1. Open **Emissions by Reporting Year** → Edit.
2. Columns → **Add Summary Formula**. Name it `Scope 1 YoY change`, format Percent.
3. Formula (grouping level: Reporting Year):

   ```
   IF(ISBLANK(PREVGROUPVAL(StnryAssetCrbnFtprnt.TotScope1EmissionsInTco2e:SUM, StnryAssetCrbnFtprnt.ReportingYear)), 0,
     (StnryAssetCrbnFtprnt.TotScope1EmissionsInTco2e:SUM
      - PREVGROUPVAL(StnryAssetCrbnFtprnt.TotScope1EmissionsInTco2e:SUM, StnryAssetCrbnFtprnt.ReportingYear))
     / PREVGROUPVAL(StnryAssetCrbnFtprnt.TotScope1EmissionsInTco2e:SUM, StnryAssetCrbnFtprnt.ReportingYear))
   ```

   The builder's insert-field picker will substitute the exact keys your org uses if these
   differ.

4. Save, then retrieve the report and commit the `<aggregates>` block Salesforce emitted.

If you do that, please send it back as a pull request — it's the one thing this repo could
not verify without an org.

## List views are a fourth name space

List view `<columns>` entries are neither describe names nor report keys, and the form
depends on the object's vintage. On the classic CRM objects, standard fields take legacy
keys like `ACCOUNT.NAME`, and on custom objects the record name column is `NAME`. On the
Net Zero Cloud objects, **neither applies**: a deploy of `<columns>NAME</columns>` fails with
`Could not resolve list view column: NAME`, and the column that works is the plain field API
name, `Name` — the same form as every other field (`ReportingYear`, `FootprintStage`,
`FuelConsumption`). All six list views in this package deploy against a licensed org on
that pattern. The lesson is the same one as the report type joins: the platform's newer
objects use plain API names in places where its older objects use legacy keys, and only a
deploy tells you which you've got.


## Retrieving overwrites what the source deliberately leaves out

`sf project retrieve start` does not give you back what you deployed. It gives you the
org's rendering of it, and for dashboards that includes two elements this package
deliberately does not carry:

```xml
<owner>someone@example.com</owner>
<runningUser>someone@example.com</runningUser>
```

Salesforce stamps both on every dashboard, whatever the source said and whatever the
dashboard type. Commit them and you have broken the package for everybody else: that username
does not exist in their org, so the deploy fails on a user it cannot resolve. You have also put
your own email address into a public repository, twice per dashboard.

The committed dashboards here carry `<dashboardType>SpecifiedUser</dashboardType>` and no
owner or running user; the deploying user (or, for the managed package, the installing user)
becomes the running user. That omission is the portable form, and it is load-bearing. They are
not dynamic (`LoggedInUser`) dashboards on purpose: dynamic dashboards count against a per-org
cap (Developer 3, Enterprise 5, Unlimited 10) and a deploy or install over the cap fails.

**So: never commit a dashboard retrieve without checking.**

```bash
sf project retrieve start --manifest manifest/package.xml --target-org <alias>
grep -rn "owner\|runningUser" force-app/main/default/dashboards/
```

Anything printed has to come out before you commit. If the rest of the retrieve is
cosmetic — and it usually is — the honest move is to throw the whole thing away and keep
the hand-authored source:

```bash
git checkout -- force-app
```

### What else comes back, and why none of it is worth keeping

The same round trip adds a few dozen lines of defaults across the reports:
`<params><name>co</name><value>1</value></params>`, `<showGrandTotal>`, `<showSubTotals>`.
They change nothing — a deploy from the source without them succeeds — and they make a
report definition longer without making its intent clearer.

The dashboards used to come back with two properties *rewritten* rather than added:
`<expandOthers>` flipped to `false` and `<showTotal>` was dropped altogether. Neither
applies to a bar or column component; Salesforce was normalising settings that were never
doing anything. The committed dashboards no longer carry either element on Bar, Column or
ColumnStacked components. They stay on the three Donut components, where they mean
something: `<showTotal>` puts the total in the centre of the ring, and `<expandOthers>`
decides whether the small slices grouped as "Others" can be opened. When you write a new
component, add those two only for a donut or pie.

The general rule, and it is the same one as everywhere else in this document: a deploy
tells you whether the source is *sufficient*. A retrieve tells you what the org chose to
store, which is a different question, and a noisier answer.
