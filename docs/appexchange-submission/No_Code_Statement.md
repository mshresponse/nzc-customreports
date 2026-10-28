# Statement: No Custom Code in This Package

**Solution:** NZC Reports and Dashboards
**Package version under review:** 1.0.0.2, subscriber package version Id `04thm000003NZY1AAO`
**Namespace:** `evirt` (Dev Hub org 00Dhm000004OFTdEAO, Everything Virtually LLC)
**Date:** 2026-10-19

## Statement

The managed package NZC Reports and Dashboards contains **no custom code of any kind**. It has no
Apex classes, Apex triggers, Visualforce pages or components, Lightning Web Components, Aura
components, Flows, or static resources containing script. The Checkmarx Source Code Scanner
requirement is therefore not applicable to this submission, as described in the Partner Security
Portal FAQ for declaratively built packages.

## What the package contains

| Metadata type | Count |
|---|---|
| Custom report types (`ReportType`) | 22 |
| Reports (`Report`) | 32 |
| Dashboards (`Dashboard`) | 4 |
| Report folder and dashboard folder | 2 |
| List views (`ListView`) on Net Zero Cloud standard objects | 6 |
| Apex, Visualforce, LWC, Aura, Flow, static resources, custom objects, custom fields, permission sets, connected apps, named credentials, remote site settings | 0 |

All components read Salesforce's own Net Zero Cloud standard objects through the platform report
engine, which enforces object, field and record-level security for the running user. The package
makes no callouts and stores no data outside the subscriber's Salesforce org. A full description is
in the accompanying *Architecture and Data Flow* document.

## Independent confirmation

Salesforce Code Analyzer 5.15.0 was run on the package source on 2026-10-19 with the rule selectors
required for AppExchange submissions (`AppExchange` and `Recommended:Security`) and all engines
enabled. Result: **0 violations**, with no scannable code files found. The report
(`CodeAnalyzerReport.html`) is attached to this submission.

The package source is public at https://github.com/mshresponse/nzc-customreports (MIT licence),
where the absence of code directories under `force-app/` can be verified directly.

Signed: Michael Hintze, Everything Virtually LLC, partners@everythingvirtually.com
