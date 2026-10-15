# Listing on AgentExchange (formerly AppExchange)

The plan for listing this package for free, with what has been checked and what is still
an owner decision. Salesforce renamed AppExchange to AgentExchange in 2026; the developer
docs use the new name and the old URLs redirect.

Facts below were read from Salesforce's documentation on 2026-10-13 and from the
OrgTriage packaging record (`orgtriage-package/docs/PACKAGING.md`), which went through the
same Dev Hub. Each source is linked where it is used.

## What a listing needs

- **A managed package.** A listing for a Salesforce platform solution is a *Packaged
  Solution | Salesforce Platform Package*, and the docs describe that choice as the way
  "to list a Salesforce managed package"
  ([Select a Listing Type](https://developer.salesforce.com/docs/platform/isvforce/guide/appexchange-select-listing-type.html)).
  A source deploy — what this repository is today — can't be listed, and an unlocked
  package can't either.
- **A security review pass.** Managed packages distributed on AgentExchange "must pass our
  security review", free or paid
  ([Pass the Security Review](https://developer.salesforce.com/docs/platform/isvforce/guide/security-review-guidelines.html)).
  A free solution pays no review fee.
- **Partner Program enrollment**, with the Dev Hub connected to the Partner Console.
- **Listing approval, then a signed Partner Application Distribution Agreement** before
  the listing can be published
  ([Get Your Listing Approved](https://developer.salesforce.com/docs/platform/isvforce/guide/appexchange-listing-approvals.html)).

Pricing: **Free**. The package needs Net Zero Cloud, which is a Salesforce licence the
customer already pays Salesforce for, not a payment to us. That should keep it in the Free
model rather than *Paid Add-On Required*; confirm it when the listing is reviewed.

## What changes for someone who installs the package instead of deploying the source

From [Components Available in Second-Generation Managed Packages](https://developer.salesforce.com/docs/platform/pkg2-dev/guide/packaging-packageable-components.html):

| Component | Customer can edit | Customer can delete | Updated by a package upgrade |
|---|---|---|---|
| Report type | No (only the developer) | No | Yes |
| Report | Yes, everything but the unique name | Yes | **No** |
| Dashboard | Yes, everything but the unique name | Yes | **No** |

Three consequences worth knowing before release:

- **Report and dashboard fixes don't reach existing installs.** An upgrade updates the
  report types and leaves the reports and dashboards as first installed. A fix like the
  2026-10 cross-filter correction to the Missing reports would reach new installs only;
  to reach everyone it would have to ship as new reports, or as release notes telling
  admins what to change. Get the reports right before 1.0. `scripts/check-reports.py` is
  the gate.
- **Customers can't add columns to the report types.** Today they can, because the source
  deploy makes the report types theirs. With the package they build their own report type
  if they need a field these don't carry.
- **Every API name gets the namespace prefix**: `<ns>__Footprints_with_Energy_Uses`, the
  folders, the list views. Labels don't change, so users see the same `NZC:` names.

The source deploy stays. The two don't collide, because the package's names are prefixed,
but installing both gives two of every report type under the same label, so the README
should tell people to pick one.

## Not waiting for the listing

A promoted package version can be installed by anyone from a Salesforce-hosted link,
before and regardless of the security review:

```
https://login.salesforce.com/packaging/installPackage.apexp?p0=04t...
```

(`test.salesforce.com` for a sandbox.) That link can go on the README and the website the
day 1.0 is promoted. It is a better one-click route than GitHub Salesforce Deploy for most
admins: Salesforce's own installer, no third-party sign-in, and an uninstall button.

## Steps

Owner steps happen in a browser; the rest are commands in this repository.

1. **Choose the namespace (owner, permanent).** Either a new product namespace registered
   in a fresh Developer Edition org and linked to the `ev-dev` Dev Hub through Namespace
   Registries, or `evirt`, which is already registered and linked and has no package on
   it since 2026-09-22. The OrgTriage record's rule was a product namespace for anything
   listed on its own, with `evirt` kept for internal packages; the counter-argument here is
   that this package has no objects, fields or permission sets, so the prefix appears
   almost nowhere an admin looks.
2. **Set it in `sfdx-project.json`** — `"namespace"` plus a `package` and `versionNumber`
   (`1.0.0.NEXT`) on the `force-app` directory — and prove it deploys with the prefix to a
   scratch org created after the change.
3. **Create the package (once):**

   ```bash
   sf package create --name "NZC Custom Reports" --package-type Managed --path force-app --target-dev-hub ev-dev
   ```

   The CLI sets `"default": false` on the package directory when it writes the alias back;
   set it to `true` again (seen twice on OrgTriage).
4. **Create a beta version:**

   ```bash
   sf package version create --package "NZC Custom Reports" --installation-key-bypass --definition-file config/project-scratch-def.json --code-coverage --wait 30 --target-dev-hub ev-dev
   ```

   The definition file switches Net Zero Cloud on, which is what lets the build org
   resolve the six standard objects the report types reference. `--code-coverage` is
   required for a version that will be promoted even though there is no Apex.
5. **Install the beta into a fresh scratch org created with `--no-namespace`**, then
   deploy `sample-data/org-setup`, import the sample data and run
   `scripts/check-reports.py`. The script finds reports by folder label and developer name,
   which a namespace leaves unchanged.
6. **Promote 1.0** (needs the *Promote a package version to released* permission; can't be
   undone): `sf package version promote --package "NZC Custom Reports@1.0.0-1"`. Put the
   install link on the README and the website.
7. **Security review (owner):** enroll the solution in the Partner Console, connect the
   Dev Hub, run Code Analyzer (no code, so it should be empty) and the Partner Security
   Portal scan, and give the reviewers a test org. **The test org needs Net Zero Cloud
   for the whole review**, and a 30-day trial can expire partway through; ask Partner
   Support for Net Zero Cloud licences in a Partner Developer Edition org before
   submitting.
8. **Listing (owner):** create a *Packaged Solution | Salesforce Platform Package* listing,
   priced Free, with screenshots of the four dashboards and the Missing reports; submit for
   approval; sign the PADA; publish. Then swap the website's install button for the
   listing.
