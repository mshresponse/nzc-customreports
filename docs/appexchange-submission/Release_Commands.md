# Release Commands — NZC Reports and Dashboards (2GP managed, namespace `evirt`)

Exact command sequence to build, test, promote and hand off version 1.0.0. Run everything from
the repository root. Flags were checked against Salesforce CLI 2.150.6 with the `code-analyzer`
5.15.0 plugin on 2026-10-16.

| Org | Alias | Org Id | Role |
|---|---|---|---|
| Partner Business Org | `ev-dev` | 00Dhm000004OFTdEAO | Dev Hub: owns the package, builds versions, holds the namespace link |
| Namespace org | `dev2` | 00Dfj00000KuY1tEAF | Developer Edition where `evirt` is registered. Not used by any command below |

The CLI resolves `--target-dev-hub` by **alias or username**, never by org Id, so every command
uses `ev-dev`. `sfdx-project.json` already carries `"namespace": "evirt"`, the package directory
settings and `"definitionFile": "config/project-scratch-def.json"`, which is what gives the 2GP
build org the `SustainabilityApp` feature and the Net Zero Cloud settings.

---

## 0. One-time checks (2 minutes)

```bash
sf org list
```

```bash
sf config set target-dev-hub=ev-dev
```

```bash
sf data query -q "SELECT NamespacePrefix FROM NamespaceRegistry" --target-org ev-dev
```

Expect `evirt` in the result (confirmed 2026-10-16, registered 2026-09-21).

```bash
sf limits api display --target-org ev-dev | grep -E "ActiveScratchOrgs|DailyScratchOrgs|Package2VersionCreates"
```

`Package2VersionCreates` is 40 per day on this Dev Hub; validated builds count against it,
`--skip-validation` builds count against the separate 500 limit.

## 1. Pre-flight: prove the source deploys under the namespace (optional, ~10 minutes)

This is the same shape as the 2GP build org (same definition file, `evirt` namespace). It was
run on 2026-10-16; rerun it after any metadata change.

```bash
sf org create scratch --definition-file config/project-scratch-def.json --alias nzc-ns --duration-days 1 --wait 25 --target-dev-hub ev-dev
```

```bash
sf org assign permset --name NetZeroAdmin --name NetZeroManager --target-org nzc-ns
```

```bash
sf project deploy start --source-dir force-app --target-org nzc-ns --wait 30
```

```bash
sf project deploy start --metadata-dir sample-data/org-setup --target-org nzc-ns --wait 10
```

```bash
sf data import tree --plan sample-data/tree/plan.json --target-org nzc-ns
```

```bash
python3 scripts/check-reports.py --target-org nzc-ns
```

```bash
sf org delete scratch --target-org nzc-ns --no-prompt
```

## 2. Code Analyzer report for the security review (1 minute)

Required by the review even for a package with no code. The exact command from the ISVforce
guide, writing the report next to the other submission files:

```bash
sf code-analyzer run --rule-selector AppExchange --rule-selector Recommended:Security --output-file docs/appexchange-submission/CodeAnalyzerReport.html
```

Result on 2026-10-16: **0 violations** (Code Analyzer 5.15.0, all engines). The repository's
`code-analyzer.yml` names `python3.12` for the Flow Scanner engine, which needs Python 3.10 or
newer; edit the value if your interpreter has another name. Without it the engine fails to start
and the report shows one critical *engine error* instead of a clean result. The HTML report is
git-ignored because it embeds local paths: keep it local and upload it in the wizard.

## 3. Create the package (once, ~1 minute)

```bash
sf package create --name "NZC Reports and Dashboards" --package-type Managed --path force-app --description "22 custom report types, 32 reports, 4 dashboards and 6 list views for Salesforce Net Zero Cloud. Declarative only." --target-dev-hub ev-dev
```

The CLI writes a `packageAliases` entry (`"NZC Reports and Dashboards": "0Hohm0000000WKrCAM"`)
into `sfdx-project.json` **and rewrites the package directory** (seen 2026-10-16): it set
`"default": false`, reset `versionName` to `ver 0.1` and `versionNumber` to `0.1.0.NEXT`, and
dropped `definitionFile`. Put all four back before building, or the build org has no Net Zero
Cloud and the version number is wrong:

```bash
git diff sfdx-project.json
```

Package created 2026-10-16: Id `0Hohm0000000WKrCAM`. Package name and description can be changed
later with `sf package update`; the namespace cannot.

## 4. Build version 1.0.0 (validated, promotable, ~10–20 minutes)

```bash
sf package version create --package "NZC Reports and Dashboards" --installation-key-bypass --code-coverage --definition-file config/project-scratch-def.json --version-name "ver 1.0" --wait 30 --target-dev-hub ev-dev
```

- `--code-coverage` is required for a version that will be promoted. With no Apex it records
  coverage as not applicable and the promote succeeds.
- `--installation-key-bypass` makes the install link work without a key (free app).
- `--definition-file` is also set in `sfdx-project.json`; passing it explicitly is harmless and
  survives a stale project file.
- **Do not use `--skip-validation` for a build you intend to promote**: skipped-validation
  versions can never be promoted. It is fine for quick iteration:

```bash
sf package version create --package "NZC Reports and Dashboards" --installation-key-bypass --skip-validation --definition-file config/project-scratch-def.json --wait 20 --target-dev-hub ev-dev
```

If the build fails, read the full error list:

```bash
sf package version create report --package-create-request-id 08c... --target-dev-hub ev-dev
```

Then confirm the result:

```bash
sf package version list --packages "NZC Reports and Dashboards" --verbose --target-dev-hub ev-dev
```

```bash
sf package version report --package "NZC Reports and Dashboards@1.0.0-2" --target-dev-hub ev-dev
```

The CLI adds `"NZC Reports and Dashboards@1.0.0-2": "04t..."` to `packageAliases`. The `04t`
Id is the subscriber package version Id used by install links and the listing.

Build history:

| Build | 04t | Status |
|---|---|---|
| 1.0.0.1 (2026-10-16) | `04thm000003NZWPAA4` | **Superseded. Do not promote.** Its four dashboards were dynamic (LoggedInUser), which counts against the subscriber org's dynamic-dashboard cap. Left in place; betas cannot be deleted without asking the owner. |
| 1.0.0.2 (2026-10-16) | `04thm000003NZY1AAO` | Dashboards run as a specified user. Validated with code coverage (check passed), build 95 s, package version Id 05ihm0000001FoDAAU, request 08chm0000001TWDAA2. The version to test, promote and list. |

## 5. Install the beta into a clean subscriber-shaped org and run the checks (~15 minutes)

A scratch org **without** the namespace behaves like a customer org. A beta version cannot be
upgraded to another beta, so each new beta goes into a **fresh** org (or uninstall the previous
beta first). The 1.0.0.1 test used `nzc-sub`; 1.0.0.2 uses `nzc-sub2`.

```bash
sf org create scratch --definition-file config/project-scratch-def.json --no-namespace --alias nzc-sub2 --duration-days 7 --wait 25 --target-dev-hub ev-dev
```

```bash
sf org assign permset --name NetZeroAdmin --name NetZeroManager --target-org nzc-sub2
```

```bash
sf package install --package "NZC Reports and Dashboards@1.0.0-2" --target-org nzc-sub2 --wait 20 --publish-wait 20 --no-prompt
```

```bash
sf package installed list --target-org nzc-sub2
```

```bash
sf project deploy start --metadata-dir sample-data/org-setup --target-org nzc-sub2 --wait 10
```

```bash
sf data import tree --plan sample-data/tree/plan.json --target-org nzc-sub2
```

```bash
python3 scripts/check-reports.py --target-org nzc-sub2
```

Then open the org, share the two folders, enable inline editing and click through the four
dashboards once by hand:

```bash
sf org open --target-org nzc-sub2
```

Also confirm the dashboards: all four should be `SpecifiedUser` with the installing user as
running user, and the package should contribute zero dynamic dashboards.

```bash
sf data query -q "SELECT DeveloperName, Type, RunningUserId, RunningUser.Username FROM Dashboard WHERE FolderName = 'NZC Dashboards'" --target-org nzc-sub2
```

```bash
sf data query -q "SELECT COUNT() FROM Dashboard WHERE NamespacePrefix = 'evirt' AND Type != 'SpecifiedUser'" --target-org nzc-sub2
```

1.0.0.1 in `nzc-sub` (2026-10-16): install succeeded, 32 reports, 4 dashboards and 22 report
types under `evirt`, `check-reports.py` 58 ok, 0 failures, no script change needed.

**1.0.0.2 in `nzc-sub2`** (2026-10-16, expires 2026-10-23): install succeeded; 32 reports, 4
dashboards, 6 list views and 22 report types under `evirt`; all four dashboards `SpecifiedUser`
with the installing user (`test-9l8gntlw7qz0@example.com`) as running user; zero packaged
dashboards of any other type; `check-reports.py` 58 ok, 0 failures; each of the four dashboards
opened once in Lightning and rendered its components. Keep the org: it is also the quickest demo
org for screenshots while the listing is drafted.

## 6. Promote 1.0.0 to released (irreversible, ~1 minute)

Needs the *Promote a package version to released* user permission on `ev-dev`. Once promoted,
the version number, namespace and component API names are locked forever.

```bash
sf package version promote --package "NZC Reports and Dashboards@1.0.0-2" --target-dev-hub ev-dev --no-prompt
```

```bash
sf package version list --packages "NZC Reports and Dashboards" --released --target-dev-hub ev-dev
```

## 7. Record the release

```bash
git add sfdx-project.json && git commit -m "Release NZC Reports and Dashboards 1.0.0 (evirt)" && git tag v1.0.0 && git push && git push --tags
```

Install link to put on the README and the website once 1.0.0.2 is promoted:

```
https://login.salesforce.com/packaging/installPackage.apexp?p0=04thm000003NZY1AAO
```

Use `https://test.salesforce.com/packaging/installPackage.apexp?p0=04t...` for sandboxes.

## 8. Security-review test org

The reviewers need an org with Net Zero Cloud, the released version installed, sample data loaded
and the folders shared. A scratch org expires in at most 30 days, which can be shorter than a
review, so use a **Partner Developer Edition org from Environment Hub** with Net Zero Cloud
licences (request them through a Partner Support case before submitting). Then, against that
org's alias (`nzc-review`):

```bash
sf package install --package 04t... --target-org nzc-review --wait 20 --publish-wait 20 --no-prompt
```

```bash
sf org assign permset --name NetZeroAdmin --name NetZeroManager --target-org nzc-review
```

```bash
sf project deploy start --metadata-dir sample-data/org-setup --target-org nzc-review --wait 10
```

```bash
sf data import tree --plan sample-data/showcase/plan.json --target-org nzc-review
```

Then re-save every energy use so Net Zero Cloud rolls the Scope 1 and 2 totals up into the
footprints (a tree import does not trigger that calculation; without this step the footprint
totals stay empty):

```bash
echo "update [SELECT Id FROM StnryAssetEnrgyUse]; update [SELECT Id FROM VehicleAssetEnrgyUse];" | sf apex run --target-org nzc-review
```

Create a dedicated reviewer user (System Administrator profile plus the two NZC permission sets),
share both folders with it, enable inline editing, and enter its login in the wizard's
test-environment step. Do not reuse your own credentials.

## 9. Next version (after 1.0.0 is promoted)

Edit `sfdx-project.json`: set `"versionNumber": "1.1.0.NEXT"`, `"versionName": "ver 1.1"`, and add
`"ancestorVersion": "HIGHEST"` to the `force-app` directory so the new version upgrades 1.0.0.
Then repeat steps 4 to 7. Remember that packaged reports and dashboards are **not** replaced on
upgrade: ship changed ones as new components with release notes.

## 10. Undo paths

- A **beta** (unpromoted) version can be deleted: `sf package version delete --package 04t... --target-dev-hub ev-dev`.
- The **package** can be deleted only while it has no promoted version: `sf package delete --package 0Ho... --target-dev-hub ev-dev`.
- A **promoted** version cannot be deleted or un-promoted; it can be deprecated from the Dev Hub
  UI once a newer version exists.
- Scratch orgs: `sf org delete scratch --target-org <alias> --no-prompt`.
