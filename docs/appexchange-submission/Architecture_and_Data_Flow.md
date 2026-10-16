# NZC Reports and Dashboards — Architecture and Data Flow

**Document purpose:** Architecture and data-flow description for the AppExchange Security Review.
Upload this document (saved as PDF) in the *Architecture / Data Flow* step of the Security Review
submission in the Partner Console.

| Item | Value |
|---|---|
| Solution name | NZC Reports and Dashboards |
| Publisher namespace | `evirt` |
| Package type | Second-generation (2GP) managed package |
| Version under review | 1.0.0.2 (`04thm000003NZY1AAO`) |
| Listing price | Free |
| Prerequisite | Salesforce Net Zero Cloud (sold as Agentforce Net Zero) licensed and enabled in the subscriber org |
| Source repository | https://github.com/mshresponse/nzc-customreports |
| Prepared | 2026-10-16 |

To produce the PDF: open this file in VS Code and use *Markdown: Print to PDF*, or run
`pandoc Architecture_and_Data_Flow.md -o Architecture_and_Data_Flow.pdf`.

---

## 1. Summary

NZC Reports and Dashboards is a **100% declarative** reporting layer for Salesforce Net Zero Cloud.
It ships custom report types, Lightning reports, Lightning dashboards and list views that read the
standard Net Zero Cloud objects already present in the subscriber's org.

The package contains:

- **no Apex** (no classes, triggers, batch jobs, scheduled jobs or REST resources),
- **no custom UI code** (no Lightning Web Components, Aura components or Visualforce pages),
- **no automation** (no Flows, Process Builder, workflow rules or platform events),
- **no integrations** (no callouts, Named Credentials, Remote Site Settings, Connected Apps,
  Auth. Providers, CSP Trusted Sites, External Services or Canvas apps),
- **no data model changes** (no custom objects, custom fields, custom settings or custom metadata),
- **no permissions** (no profiles, permission sets or permission set groups),
- **no post-install script, no custom settings and no stored secrets.**

Every component executes inside the Salesforce platform's own reporting engine. No data leaves
the subscriber's Salesforce org at any point.

## 2. Component inventory

| Metadata type | Count | Purpose |
|---|---|---|
| `ReportType` (custom report types) | 22 | Define which Net Zero Cloud objects and fields a report can query, including outer joins for "with / without" data-quality reports |
| `Report` | 32 | Tabular, summary and matrix reports: data entry, data quality (missing / orphaned records), Scope 1, Scope 2 and Scope 3 summaries |
| `Dashboard` | 4 | *NZC Emissions Coverage*, *NZC Audit*, *NZC Data Quality*, *NZC Scope 3* |
| `ReportFolder` | 1 | *NZC Reports* (shared folder; the installing admin controls sharing) |
| `DashboardFolder` | 1 | *NZC Dashboards* (shared folder; the installing admin controls sharing) |
| `ListView` | 6 | List views on six Net Zero Cloud standard objects |
| **Everything else** | **0** | No Apex, LWC, Aura, Visualforce, Flow, objects, fields, permission sets, connected apps, named credentials, remote sites, static resources |

Full inventory in the repository: `force-app/main/default/`.

## 3. Standard objects read by the package

All objects are Salesforce-owned Net Zero Cloud standard objects. The package creates no objects
and no fields; it only references these existing ones through custom report types and list views.

| Object API name | Label | Used by |
|---|---|---|
| `StnryAssetEnvrSrc` | Stationary Asset Environmental Source | Scope 1 & 2 report types, list view |
| `StnryAssetCrbnFtprnt` | Stationary Asset Carbon Footprint | Scope 1 & 2 report types, list view |
| `StnryAssetEnrgyUse` | Stationary Asset Energy Use | Scope 1 & 2 report types, list view |
| `VehicleAssetEmssnSrc` | Vehicle Asset Emissions Source | Fleet report types, list view |
| `VehicleAssetCrbnFtprnt` | Vehicle Asset Carbon Footprint | Fleet report types, list view |
| `VehicleAssetEnrgyUse` | Vehicle Asset Energy Use | Fleet report types, list view |
| `Scope3EmssnSrc` | Scope 3 Emissions Source | Scope 3 report types |
| `Scope3CrbnFtprnt` | Scope 3 Carbon Footprint | Scope 3 report types |
| `Scope3PcmtSummary` | Scope 3 Procurement Summary | Scope 3 report types |
| `Scope3PcmtItem` | Scope 3 Procurement Item | Scope 3 report types |
| `AirTravelEnrgyUse` | Air Travel Energy Use | Scope 3 report types |
| `HotelStayEnrgyUse` | Hotel Stay Energy Use | Scope 3 report types |
| `GroundTravelEnrgyUse` | Ground Travel Energy Use | Scope 3 report types |

## 4. Architecture diagram

```
 Subscriber Salesforce org (single trust boundary — nothing crosses it)
 ┌────────────────────────────────────────────────────────────────────────────────────┐
 │                                                                                    │
 │   End user (browser / Salesforce mobile)                                           │
 │        │  standard Salesforce session, MFA, IP ranges, login hours as configured   │
 │        ▼                                                                           │
 │   Lightning Reports & Dashboards UI  (Salesforce-owned UI; nothing custom)         │
 │        │                                                                           │
 │        ▼                                                                           │
 │   ┌──────────────────────────────────────────────────────────────────────┐         │
 │   │  THIS PACKAGE (metadata only)                                        │         │
 │   │   22 custom report types ─ 32 reports ─ 4 dashboards ─ 6 list views  │         │
 │   │   2 folders (NZC Reports, NZC Dashboards)                            │         │
 │   └──────────────────────────────────────────────────────────────────────┘         │
 │        │  interpreted by                                                           │
 │        ▼                                                                           │
 │   Salesforce Report Engine  (enforces object CRUD, field-level security,           │
 │                              org-wide defaults, sharing rules, record access       │
 │                              of the RUNNING USER on every query)                   │
 │        │                                                                           │
 │        ▼                                                                           │
 │   Net Zero Cloud standard objects (13 objects, Salesforce-owned, customer's data)  │
 │                                                                                    │
 └────────────────────────────────────────────────────────────────────────────────────┘

   NO outbound connections · NO external services · NO stored credentials · NO custom code
```

## 5. Data flows

### 5.1 Read path (reports, dashboards, list views)

1. A user opens a report, dashboard or list view in the subscriber org's own Lightning UI.
2. The platform's report engine reads the packaged report type definition and executes the
   query **as the running user**. Object permissions, field-level security and the sharing model
   are enforced natively by Salesforce; the package has no mechanism to bypass them.
3. Results render in the standard UI. Nothing is cached, copied or transmitted by the package.

All four dashboards are configured as **`dashboardType = SpecifiedUser`**, and no running user
is committed in the metadata. On deploy or install the platform sets the running user to the
deploying or installing administrator, so dashboard aggregates are computed at that
administrator's data visibility and every user with access to the folder sees the same totals.
This is deliberate: dynamic (viewer-as-running-user) dashboards count against a per-org cap
(3 in Developer, 5 in Enterprise, 10 in Unlimited Edition) and an install that exceeds the cap
fails with no workaround, whereas a specified-user dashboard can be switched to dynamic by the
subscriber administrator after install because packaged dashboards are subscriber-editable.

Mitigations for the wider aggregate visibility this implies:

- The two packaged folders are **private until the installing administrator shares them**. No
  user sees any packaged dashboard or report before that explicit sharing step, and the
  administrator decides who gets access.
- **Drill-down runs as the viewer.** Every dashboard component opens its underlying report, and
  that report runs as the user who opens it, under their own object, field and record access.
- The administrator can change a dashboard's running user, or set it to run as the dashboard
  viewer (dynamic), from the dashboard's properties at any time.
- The dashboards aggregate emissions, energy-use and procurement figures for the customer's own
  facilities, vehicles and suppliers; they carry no personal-data fields.

### 5.2 Write path (inline editing in reports)

Six tabular reports are laid out for the platform's **standard inline editing** feature
(*Setup → Reports and Dashboards Settings → Enable Inline Editing in Reports*; off by default).

1. The user edits a cell in the report grid (standard Salesforce feature; no code in this package).
2. The platform issues a standard record update as the running user. Object CRUD, field-level
   security, validation rules and the subscriber's own automation all apply exactly as they
   would from the record page.
3. Net Zero Cloud's own platform logic recalculates the dependent footprint totals. This logic
   belongs to Salesforce, not to this package.

The package adds no write logic of its own.

### 5.3 Data at rest, in transit, and outside Salesforce

| Question | Answer |
|---|---|
| Does the package store data outside Salesforce? | No |
| Does the package transmit data outside Salesforce? | No (no callouts of any kind) |
| Does the package create records on install or at runtime? | No (metadata only; no post-install script) |
| Does the package store credentials, keys, tokens or secrets? | No |
| Does the package introduce any encryption, hashing or key management? | No; relies on the platform |
| Does the package process PII beyond what the customer already stores in NZC objects? | No; it only reads what the customer's own users are already permitted to see |

## 6. Security controls (as they apply to a declarative package)

| Control | Implementation |
|---|---|
| Authentication | Salesforce platform login only; nothing custom |
| Authorization — object (CRUD) | Enforced by the report engine for the running user |
| Authorization — field (FLS) | Enforced by the report engine; fields the user cannot read are hidden from the report |
| Authorization — record (sharing) | Reports: enforced by the report engine for the viewer. Dashboards: aggregates are computed as the running user (the installing administrator by default); folders stay private until shared; drill-down reports run as the viewer |
| Folder access | Installed folders are private until the subscriber admin shares them (*Reports → All Folders → Share*). Documented in the README setup steps |
| Injection (SOQL / SOSL / XSS / CSRF) | Not applicable: no code, no user-controlled query strings, no custom markup |
| Secrets management | Not applicable: no secrets |
| Data egress | Not applicable: no network calls |
| Logging / monitoring | Standard Salesforce Setup Audit Trail and report/dashboard access controls |

## 7. Threat model and residual risk

| Threat | Exposure through this package | Mitigation |
|---|---|---|
| Data exfiltration via custom code or callouts | None (no code, no callouts) | — |
| Dashboard totals visible to users whose own record access is narrower than the running user's | Yes, inherent to specified-user dashboards: a user with folder access sees aggregates computed at the installing administrator's visibility | Folders are private until the administrator shares them and the administrator chooses who gets access; drill-down reports always run as the viewer; the administrator can change the running user or switch any dashboard to run as the viewer |
| Over-broad folder sharing after install | Subscriber decision | README instructs sharing with the sustainability team only |
| Report type exposes a field the subscriber wants hidden | Only if the user already has FLS on it | Platform FLS; admin can remove FLS or edit the report |
| Inline edit writes bad data | Same as any record edit | Platform validation rules and NZC's own logic; feature is off by default and admin-controlled |

The package introduces **no attack surface** beyond the standard Salesforce reporting features
that every subscriber already has.

## 8. Install, upgrade and uninstall behaviour

- **Install:** standard managed-package install, no installation key, no post-install Apex.
  Dashboards install as specified-user dashboards running as the installing administrator.
  Report types install as the publisher's (`evirt__…`) and cannot be edited by the subscriber.
  Reports and dashboards install into the two packaged folders and can be edited or deleted by
  the subscriber. List views install on the six standard objects.
- **Upgrade:** report types are upgraded in place. Reports and dashboards are **not** overwritten
  by upgrades (platform behaviour for packaged reports and dashboards); fixes to those ship as
  new components with release notes.
- **Uninstall:** standard uninstall removes all packaged components. The package created no
  records, so no customer data is removed or left behind.

## 9. Quality assurance and validation performed

- **Continuous integration** on every push (`.github/workflows/validate.yml`): XML
  well-formedness, `sf project convert source`, manifest-to-source consistency, and freshness of
  the generated sample data.
- **Functional check**, `scripts/check-reports.py`: runs every packaged report and dashboard in
  an org that already holds the fixture dataset (`sample-data/tree`) and compares the rows
  returned with the rows the fixture was built to produce. The workflow has a second job that
  can run it in a fresh Net Zero Cloud scratch org when the `DEVHUB_SFDX_AUTH_URL` repository
  secret is configured. That secret is not configured today, so the job is skipped in CI and the
  check was run by hand for this release, twice:
  - **Namespaced build check** (2026-10-16): the source deployed to a scratch org created with the
    `evirt` namespace, the same shape as the 2GP build org, and passed the functional check.
  - **Subscriber install check** (2026-10-16): the built version was installed into a scratch org
    without the namespace, the fixture was loaded, and the functional check passed (58 report and
    dashboard checks, 0 failures); all four dashboards were confirmed to run as the installing
    user.
- **Salesforce Code Analyzer 5.15.0** (rule selectors `AppExchange` and `Recommended:Security`,
  all engines enabled) run on 2026-10-16: **0 violations**. No Apex, LWC, Aura, Visualforce or Flow
  files exist to scan. Report (`CodeAnalyzerReport.html`) attached to the submission.

## 10. Publisher contact

| Role | Contact |
|---|---|
| Technical and security contact | Michael Hintze, mike@everythingvirtually.com |
| Dev Hub (Partner Business Org) | 00Dhm000004OFTdEAO |
| Namespace org | 00Dfj00000KuY1tEAF (`evirt`) |
