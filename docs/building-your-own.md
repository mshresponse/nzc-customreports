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

