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

