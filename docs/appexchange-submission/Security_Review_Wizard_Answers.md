# Security Review Wizard Answers — NZC Reports and Dashboards

Paste-ready answers for the AgentExchange (AppExchange) Security Review wizard in the Partner
Console, plus the free-listing fee steps. Facts marked *(guide)* were read from the ISVforce
Guide on 2026-10-16:

- [How the Security Review Works](https://developer.salesforce.com/docs/platform/isvforce/guide/security-review-how-it-works.html)
- [Required Materials](https://developer.salesforce.com/docs/platform/isvforce/guide/security-review-required-materials.html)
- [Scan with Code Analyzer](https://developer.salesforce.com/docs/platform/isvforce/guide/security-review-code-analyzer-scan.html)
- [Listing Readiness](https://developer.salesforce.com/docs/platform/isvforce/guide/security-review-listing-readiness.html)

Salesforce changes the wizard's labels between releases, so the answers are grouped by the
question being asked rather than by screen number. Every answer below is true of the package as
it exists in this repository; if the package ever gains code or a callout, redo this document.

---

## 1. Before you open the wizard

The guide lists these as the conditions for being ready to submit *(guide)*:

| # | Prerequisite | Status | Where |
|---|---|---|---|
| 1 | Solution secured to industry standards | Done: no code, no callouts (see `Architecture_and_Data_Flow.md`) | — |
| 2 | Solution enrolled in the ISV Partner Program | Owner action | Partner Community → Partner Console → Publishing |
| 3 | Solution certified **Lightning Ready** (mandatory for every new submission) | Owner attestation; trivially true, the package is Lightning reports and dashboards only | Listing → Lightning Ready section |
| 4 | Packaging org connected to the Partner Console | Owner action: connect Dev Hub `ev-dev` (00Dhm000004OFTdEAO) | Partner Console → Publishing → Technologies → Connect an org |
| 5 | Provider (company) profile created | Owner action | Partner Console → Publishing → Company Info |
| 6 | Package version is **Managed – Released** (promoted). Beta versions are rejected *(guide)* | Done 2026-10-16: 1.0.0.2 promoted | Technologies → Solutions shows *Security Review Required* next to the version |
| 7 | Listing created and linked to the released version | Owner action | Publishing → Listings → New → *Packaged Solution / Salesforce Platform Package* |

Version to submit: **1.0.0.2 (`04thm000003NZY1AAO`)**; 1.0.0.1 is superseded and must not be promoted. Submit a major or minor version, never a patch; later
versions created with this one as ancestor inherit its listing readiness without a new review
*(guide)*. Do not create more versions while the review is in progress.

## 2. Materials to prepare (upload checklist)

The guide's materials table for a **Salesforce Native Solution** (no Lightning components, no
external services) *(guide)*:

| Material | What to provide | Status |
|---|---|---|
| Developer Edition org with the package installed | Partner Developer Edition org from Environment Hub with Net Zero Cloud licences, version 1.0.0 installed, showcase sample data loaded, both folders shared, inline editing on, a dedicated reviewer user | Owner action: see `Release_Commands.md` step 8 |
| Checkmarx (Source Code Scanner) report | Partner Security Portal → Source Code Scanner → scan an org that holds the **source** (the `nzc-ns` scratch org or any org you deployed `force-app` to; an installed managed package hides its source). With zero Apex/Visualforce the report comes back empty. Save it as PDF and upload it anyway; the table requires it for native solutions | To do once (15 min) |
| Code Analyzer report | `docs/appexchange-submission/CodeAnalyzerReport.html`, generated locally with the guide's exact command (git-ignored: it embeds local paths). Expect zero violations, zero scannable files | Generated 2026-10-16: 0 violations |
| False-positive documentation | Not applicable; there are no findings. Enter "No findings; no false positives" where asked | — |
| Solution documentation | `README.md` exported to PDF (setup, what each report does, folder sharing, inline editing), plus `Architecture_and_Data_Flow.md` as PDF | Export before submitting |
| Company information-security policy | One page is enough for a small publisher; template in section 6 | Write once, reuse |

## 3. Answers by wizard question

### 3.1 Solution and version

| Question | Answer |
|---|---|
| Listing / solution | NZC Reports and Dashboards |
| Package version under review | 1.0.0.2 (`04thm000003NZY1AAO`, namespace `evirt`, 2GP Managed – Released, promoted 2026-10-16) |
| Solution type | Managed package, Salesforce Platform |
| Short description | Lightning report types, reports, dashboards and list views for Salesforce Net Zero Cloud (Agentforce Net Zero). 100% declarative: no Apex, no Lightning components, no integrations. |
| Does the solution require any Salesforce licence or feature? | Yes: Net Zero Cloud (SustainabilityApp feature) must be enabled in the org. The test org provided has it. |
| Is the solution Lightning Ready? | Yes. Every component is a Lightning report, dashboard, report type or list view. No Visualforce, no Classic-only components. |

### 3.2 Architecture questions

| Question | Answer |
|---|---|
| Architecture category | Salesforce Native Solution |
| Does the solution contain Apex? | No |
| Does the solution contain Lightning Web Components, Aura components or Visualforce? | No |
| Does the solution contain Flows or other automation? | No |
| Does the solution make callouts or connect to external web services? | No. No Named Credentials, Remote Site Settings, External Services, CSP Trusted Sites, Auth. Providers or Connected Apps are packaged. |
| Does the solution include an external web application, mobile app, or API-only component? | No |
| Does the solution store, process or transmit Salesforce data outside Salesforce? | No. All processing is the standard Salesforce report engine inside the subscriber org. |
| Does the solution use third-party or open-source libraries or JavaScript? | No |
| Does the solution include a post-install or uninstall script? | No |
| Does the solution create custom objects, fields, custom settings or custom metadata? | No. It references 13 standard Net Zero Cloud objects only. |
| Does the solution include profiles, permission sets or permission set groups? | No |
| Is this an extension package? | No. It depends on Salesforce's own Net Zero Cloud, not on another partner package. |

### 3.3 Data security questions

| Question | Answer |
|---|---|
| How is CRUD / FLS enforced? | Natively, by the Salesforce report engine, for the running user on every query. The package contains no code that could bypass it. |
| How is record-level sharing enforced? | Reports: natively, by the report engine, for the user running the report. Dashboards: see the next two rows. |
| Do any dashboards run as a specified user? | Yes, all four. No running user is packaged; the platform sets it to the installing administrator. Dashboard totals are therefore computed at that administrator's visibility and shown to everyone the administrator gives folder access to. Chosen because dynamic dashboards count against a per-org cap (Developer 3, Enterprise 5, Unlimited 10) and an install over the cap fails outright. |
| What limits the exposure from specified-user dashboards? | (1) The packaged folders are private until the installing administrator shares them, so nobody sees a dashboard without an explicit decision. (2) Every component opens its report, and the report runs as the viewer under their own access. (3) Packaged dashboards are subscriber-editable: the administrator can change the running user or switch any dashboard to run as the viewer. (4) The dashboards aggregate facility, vehicle and supplier emissions figures and carry no personal-data fields. |
| Does any Apex run `without sharing` or use `inherited sharing`? | Not applicable; no Apex. |
| Are SOQL/SOSL queries built from user input? | Not applicable; no code. Report filters are standard platform filters. |
| Does the solution handle authentication, sessions, passwords or tokens? | No. Standard Salesforce login only. |
| Does the solution store secrets, API keys or credentials? | No |
| Does the solution encrypt data or manage keys? | No; nothing is stored outside the platform. |
| Does the solution process PII or sensitive data? | It reads only the Net Zero Cloud records the running user is already permitted to see (facility, vehicle, energy-use, procurement and travel emissions data). It does not copy, export or transmit them. |
| Does the solution write data? | Only through the platform's standard inline editing in reports, which is off by default and admin-controlled; every edit is an ordinary record update subject to CRUD, FLS, validation rules and the subscriber's own automation. |
| Does the solution log or expose data in debug logs, emails or files? | No |
| Lightning Web Security / Locker compliance | Not applicable; no custom components. |

### 3.4 Test environment

| Field | Value |
|---|---|
| Login URL | `https://login.salesforce.com` |
| Username | the dedicated reviewer user created in the test org (System Administrator profile + `NetZeroAdmin` + `NetZeroManager` permission sets) |
| Password | set in the org; never reuse your own |
| Notes for the reviewer | "Net Zero Cloud is enabled. Package `evirt` 1.0.0 is installed. Sample data (fictional) is loaded. Folders *NZC Reports* and *NZC Dashboards* are shared with this user. Inline editing in reports is enabled under Setup → Reports and Dashboards Settings. There are no external components, URLs or credentials beyond this org." |

Keep the org alive for the whole review: verification takes 1–2 weeks and testing 3–4 weeks
*(guide)*, which is why a scratch org (30-day maximum) is the wrong choice.

### 3.5 Scan uploads

| Upload | File |
|---|---|
| Code Analyzer report | `CodeAnalyzerReport.html` |
| Checkmarx report | PDF saved from the Partner Security Portal scan email |
| False positives | none; type "No findings" if the field is mandatory |
| Architecture / data-flow document | `Architecture_and_Data_Flow.pdf` |
| User documentation | `README.pdf` |
| Information security policy | `Information_Security_Policy.pdf` (section 6) |

### 3.6 Attestation text (paste where a free-text justification is requested)

> NZC Reports and Dashboards (namespace evirt, version 1.0.0) is a second-generation managed
> package containing only declarative reporting metadata: 22 custom report types, 32 reports, 4
> dashboards, 2 folders and 6 list views. It contains no Apex classes or triggers, no Lightning
> Web Components, Aura components or Visualforce pages, no Flows, no custom objects or fields, no
> permission sets, no post-install script and no stored secrets. It makes no callouts and
> packages no Named Credentials, Remote Site Settings, Connected Apps, Auth. Providers, External
> Services or CSP Trusted Sites. All data access is performed by the Salesforce report engine as
> the running user, so object, field and record-level security are enforced natively. All four
> dashboards run as a specified user with no running user packaged, so the installing
> administrator becomes the running user; the packaged folders are private until that
> administrator shares them, drill-down reports run as the viewer, and the administrator can
> switch any dashboard to run as the viewer. The package reads 13 standard Net Zero Cloud
> objects and creates no data. Salesforce Code Analyzer (AppExchange and Recommended:Security
> rule selectors) reports zero violations on zero scannable files; the Checkmarx Source Code
> Scanner report is empty for the same reason.

## 4. Free listing: paying no fee

The guide states it directly: "If you plan to distribute your solution for free, you don't pay
the fee" *(guide)*. There is no separate waiver form; the fee step keys off the listing's pricing.

1. Partner Console → Publishing → Listings → *NZC Reports and Dashboards* → **Pricing** tab.
2. Choose **Free**. Do not choose *Paid* or *Freemium*, and do not enable AppExchange Checkout.
   The Net Zero Cloud licence the customer needs is bought from Salesforce, not from you, so it
   does not make the listing *Paid add-on required*; if the listing reviewer disagrees, that is a
   listing-metadata question, not a security-review fee question.
3. Save the listing before starting the security review so the wizard reads the pricing.
4. In the wizard, the payment step shows no fee for a free listing. If it shows a charge, stop,
   do not pay, and open a case: Partner Community → Support → Create Case → *AppExchange and
   Partner Programs* → *Security Review*, stating the listing is Free and asking Security Review
   Operations to zero the fee. They respond within about two business days.
5. If you ever convert the listing to paid, a review fee becomes due at that point.

## 5. After you click Submit

| Stage *(guide)* | Typical time |
|---|---|
| Security Review Operations verifies the submission is complete | 1–2 weeks |
| Product Security tests the solution (first review) | 3–4 weeks |
| Resubmission after fixes | 2–3 weeks |

- Track progress and messages in the wizard; reply there, not by email.
- Expect an operations check that the test org opens, the package is installed and the folders
  are visible. The most common hold for a package like this is an expired test org or a reviewer
  user without the Net Zero Cloud permission sets.
- For questions before or during the review, book **office hours** from the Partner Security
  Portal (Security Review Operations for process, Product Security for findings) *(guide)*.
- On **Approved**: the version becomes *Ready to List* (Technologies → Solutions). Submit the
  listing for listing approval, sign the Partner Application Distribution Agreement when asked,
  then publish.
- Next versions: create them with `"ancestorVersion": "HIGHEST"` from the approved version and
  they inherit listing readiness with no new review *(guide)*.

## 6. One-page information security policy (template)

Save as `Information_Security_Policy.pdf` after filling in the bracketed parts.

> **Information Security Policy — [Everything Virtually / legal entity], publisher of NZC Reports and Dashboards**
>
> *Scope.* This policy covers the development, packaging and distribution of the NZC Reports and
> Dashboards managed package (namespace `evirt`) and the handling of any customer or reviewer
> credentials in connection with it.
>
> *Product security.* The package is declarative Salesforce metadata only. It contains no code and
> performs no network calls, so it processes no customer data outside the customer's Salesforce
> org. Every release is built from a tagged commit in the public GitHub repository
> mshresponse/nzc-customreports, whose full history is open to inspection and to which only
> [number] named maintainers can push, each with MFA. Continuous integration validates the metadata
> on every push; before each release the functional report check is run against a Net Zero Cloud
> scratch org, the package is scanned with Salesforce Code Analyzer, and the version is promoted
> through a Salesforce Dev Hub protected by multi-factor authentication.
>
> *Access control.* Access to the Dev Hub, namespace org, Partner Console and source repository is
> limited to [number] named individuals, each using MFA. Test-org credentials supplied to Salesforce
> are unique, used only for the review, and revoked after it.
>
> *Secrets.* No secrets, keys or customer credentials are stored in the package, the repository or
> build artifacts.
>
> *Vulnerability handling.* Security reports are accepted at [security contact email]. Confirmed
> issues are fixed in a new package version and reported to affected customers via release notes.
>
> *Review.* This policy is reviewed annually and on any architectural change (for example, adding
> code or an integration to the package), which also triggers a new security review submission.
>
> Signed: [name, role], [date]
