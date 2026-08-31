# provisioning/

Idempotent scripts for everything a feature needs that **cannot ship in a Power Platform
solution**. Written by the development-agent (via `identity-agent` / `m365-agent`
sub-agents), executed by the pipeline-agent via `config/<slug>-pipeline.yml`.

```
provisioning/
├── common/             ← shared helpers dot-sourced by every script (contract implementation)
├── deploymentSettings/ ← <env>-settings.json per environment (copy dev-settings.example.json)
├── entra/              ← app registrations, admin consent, security groups
├── dataverse/          ← group teams, role bindings, document locations, app sharing
├── sharepoint/         ← site creation + PnP site templates (templates/ subfolder)
└── teams/              ← team provisioning, Teams app catalog publish + install
```

## Script Inventory

| Folder | Script | Purpose | Verify counterpart |
|---|---|---|---|
| `dataverse/` | `ensure-schema.ps1` | **DEV ONLY, run once.** Creates the entire Phase 1 Dataverse schema — 16 global option sets, the 4 tables and every column, the applicant→application relationship, the two security roles with full privilege depth, and the REV_TrusteeRestricted field security profile with all 34 field permissions — through the Web API metadata endpoints, never solution import (creating these component types from scratch via import is unsupported: https://learn.microsoft.com/en-us/power-platform/alm/when-edit-customization-file). Reads the orphaned-but-authoritative XML under `src/solutions/RevitaliseGrantAutomation/{Entities,OptionSets,Roles,Other}` at run time via `ensure-schema-helpers.psm1` rather than re-encoding it as PowerShell literals. Power Platform Pipelines (TAD ADR-007) promotes the resulting schema to TST/ACC and PRD from then on. | — |
| `entra/` | `create-self-signed-cert.ps1` | Mints the client-certificate credential an app registration needs for certificate-based app-only auth (e.g. `PROVISION_APP_ID`'s own credential) — cross-platform (.NET `CertificateRequest`, no Windows-only `New-SelfSignedCertificate`). Run by hand, never from a pipeline; see exemption note below | — |
| `entra/` | `ensure-app-registration.ps1` | App registrations + service principals + federated credentials, least-privilege permissions from settings | `verify-entra.ps1` |
| `entra/` | `grant-admin-consent.ps1` | Tenant-wide admin consent (appRoleAssignments / oauth2PermissionGrants) for declared permissions | `verify-entra.ps1` |
| `entra/` | `ensure-groups.ps1` | Entra security groups, one per persona per environment (existence only — membership is business/IAM-owned) | `verify-entra.ps1` |
| `entra/` | `ensure-intake-client.ps1` | The intake endpoint's OAuth caller identity (Alex's WordPress site) **plus the two identifiers its authentication needs**: the service principal *object* id for the trigger's Allowed users list, and the application *client* id for `rev_IntakeAllowedClientId`. Asserts a pre-existing registration really carries the declared Flow Service permission | `verify-intake-endpoint-auth.ps1` |
| `entra/` | `verify-intake-endpoint-auth.ps1` | Read-only: POSTs to the intake endpoint with no credential and with an invalid bearer token, asserts 401/403 **and** that the rejection happened before the workflow definition ran (C-TECH-006 `Verify By`) → `PASS`/`FAIL` | — |
| `entra/` | `verify-entra.ps1` | Read-only: apps, SPs, consent, groups → `PASS`/`FAIL` | — |
| `dataverse/` | `ensure-group-teams.ps1` | Dataverse group teams (AAD Security Group type) backed by Entra groups | `verify-role-bindings.ps1` |
| `dataverse/` | `bind-roles-to-groups.ps1` | Group teams **plus** security-role bindings (superset of `ensure-group-teams.ps1` — the script pipelines call; C-TECH-040) | `verify-role-bindings.ps1` |
| `dataverse/` | `ensure-document-locations.ps1` | `sharepointsites` + `sharepointdocumentlocations` records for document management | `verify-role-bindings.ps1` (Dataverse) / `verify-sharepoint.ps1` (site side) |
| `dataverse/` | `ensure-column-security-profile-members.ps1` | Group teams → member of the column security (field security) profiles that ship in the solution; the profile is solution content, its membership is not | `verify-role-bindings.ps1` |
| `dataverse/` | `ensure-auditing.ps1` | Organisation auditing + audit retention period (`organizations`), plus table-level auditing via `EntityDefinitions` metadata | — |
| `dataverse/` | `ensure-bulk-delete-jobs.ps1` | Recurring `BulkDelete` jobs that enforce the retention schedule; periods and recurrence come from settings | — |
| `dataverse/` | `seed-settings.ps1` | Upserts the configuration rows read by the flows, keyed on the table's alternate key; fails fast before any write on an unresolved `{{...}}` token | — |
| `dataverse/` | `seed-round-statistics-request.ps1` | Seeds the single, ever-present `rev_roundstatisticsrequest` row (key `CURRENT`) — the trustee portal's **ASK**: the app writes `rev_triggeredon` on it and the Dataverse-triggered flow triggers on that column (IMP-0359, IMP-0365). Keyed upsert on the table's alternate key, same mechanism as `seed-settings.ps1`. The app and the flow's own security role both have no create privilege on this table by design, so the row has to exist before either can touch it. **Writes `rev_name` and nothing else, corrected 2026-08-28** — it previously also PATCHed `rev_status`, one of the three ADR-038-superseded columns whose own shipped `<Description>` says nothing writes them (`IMP-0438`); `rev_status` on the row the app actually reads is seeded by `seed-round-statistics-result.ps1` | — |
| `dataverse/` | `seed-round-statistics-result.ps1` | Seeds the single, ever-present `rev_roundstatisticsresult` row (key `CURRENT`) — ADR-038's request/result split (TAD section 3.9, WBS 6.9): the flow's ANSWER moved off `rev_roundstatisticsrequest` onto this new table so a trustee's Write on the ask can never reach the answer. Keyed upsert on the table's alternate key, same mechanism as `seed-round-statistics-request.ps1`. Neither the app nor the flow's own security role holds Create on this table, so the row has to exist before either can touch it — and it must exist before the first trigger fires (§5.1.1 point 4) | — |
| `dataverse/` | `seed-round-statistics-test-data.ps1` | **DEV/TST only** — refuses `acc`/`prd` at runtime. Writes a fully-populated, realistic response straight into **`rev_roundstatisticsresult.rev_resultjson`** (the same fixture shape `src/test/harness.tsx`'s `makeAllMetrics()` uses) so the trustee portal's charts can be looked at with real figures without waiting on the flow — which currently computes only `applicationsReceived`, every other metric being explicit `null` by design (TAD ADR-030 §5.1). `roundKey` is read live from whichever round is open, never hardcoded, so the landing screen's own reconciliation check does not hide the figures. **UPDATE-ONLY**: reports FAILED naming `seed-round-statistics-result.ps1` when the row is absent, rather than upserting a second row into a one-row-ever table. Overwrites whatever the flow itself last wrote. **Target table corrected 2026-08-28** — it previously wrote the three ADR-038-superseded columns on `rev_roundstatisticsrequest`, which succeeded and left the charts empty | — |
| `dataverse/` | `share-apps.ps1` | Model-driven apps → role association; Code/Canvas apps → share with persona Entra groups | `verify-role-bindings.ps1` |
| `dataverse/` | `reconcile-flow-statecodes.ps1` | Read-only, two modes: `-Mode Capture` snapshots every cloud flow's statecode before an import; `-Mode Diff` re-queries after and reports exactly which flows the import deactivated (IMP-0136 — two consecutive imports deactivated 2 of 4 flows, not all four and not zero, and nothing had compared before against after) | — |
| `dataverse/` | `verify-environment-access.ps1` | Read-only, one `WhoAmI` per environment: proves the provisioning identity is an application user **in that exact org**, not merely that Entra issued a token (C-TECH-065). A Dataverse application user is created per environment, so the same credential resolves a `UserId` against DEV and returns `0x80072560` against TST/ACC → `PASS`/`FAIL` | — |
| `dataverse/` | `verify-role-bindings.ps1` | Read-only: teams, Entra binding, role bindings, no direct user assignments (C-TECH-040) → `PASS`/`FAIL` | — |
| `dataverse/` | `verify-access-test-identity.ps1` | Read-only pre-flight for the column-security access test, run immediately before the test is handed to its named human rather than at deploy time, because the state it reads is live. Enumerates the field-security profiles **live** (never a list in settings) and checks all four routes by which the identity under test could still read the columns the test asserts are hidden: direct `systemuserprofiles` membership, membership via any team it belongs to (`teamprofiles` intersected with its own teams), a security role beyond the declared permitted set, and the two controls being the same identity. Also asserts the comparison identity really *is* released those columns, so an empty result can be told apart from a control that is simply absent (C-TECH-068, IMP-0228/IMP-0110). Reads `dataverse.accessTest` from a dedicated per-environment file — `dev-access-test-settings.json` for DEV, since `Get-ProvisioningSettings -Env dev` throws by design → `PASS`/`FAIL` | — |
| `dataverse/` | `seed-test-data.ps1` | **DEV/TST only.** Loads the synthetic cases in `src/tests/data/scoring-test-data.json` into `rev_applicant` + `rev_application`, which is what fires the scoring flow (its trigger is row *created*). Validates every case before writing anything, and refuses to load while any REV flow is in Draft — a row created against an inactive flow is never scored and never will be. Not an upsert: a case whose submission id exists is reported `EXISTS` and skipped, because a keyed PATCH would not fire the create trigger | `verify-test-data.ps1` |
| `dataverse/` | `verify-test-data.ps1` | Read-only: reads each seeded row back and compares status, circumstance score, income flag, whether `rev_scoredon` was stamped, and named phrases in `rev_scorebreakdown`; plus two cross-case checks no single row can make — the special-category A/B pair, and the daily-summary counters computed the way the summary flow computes them → `PASS`/`FAIL` | — |
| `dataverse/` | `remove-test-data.ps1` | **DEV/TST only.** Teardown for the above, by the two markers `seed-test-data.ps1` writes (`rev_sourcesubmissionid` prefix `TESTDATA-`, `rev_applicant.rev_lastcontactdate` = `1900-01-01`). Applications before applicants, since the lookup is required. Dry run unless `-Force`; `rev_errorlog` rows are kept unless `-IncludeErrorLogs`, because that table is an audit trail | — |
| `dataverse/` | `test-data-common.psm1` | Pure/read-only module shared by the three `*-test-data.ps1` scripts: the two teardown markers, the flow catalogue, environment resolution and case validation, defined once so the loader and the remover cannot drift apart. A `.psm1`, not a `.ps1`, for the same reason as `ensure-schema-helpers.psm1` — a function library, not an entry point, and therefore exempt from the Script Contract below. It deliberately reports nothing: the failure counter lives in the scope that dot-sourced `provisioning-common.ps1`, so status lines stay in the entry scripts | — |
| `sharepoint/` | `ensure-site.ps1` | Site collection + PnP template from `templates/` + persona groups into site groups | `verify-sharepoint.ps1` |
| `sharepoint/` | `verify-sharepoint.ps1` | Read-only: site, template libraries, group access → `PASS`/`FAIL` | — |
| `teams/` | `ensure-team.ps1` | Team (standard template) + channel set via Graph | `verify-teams.ps1` |
| `teams/` | `publish-teams-app.ps1` | Publish/update the Teams app package in the org catalog | `verify-teams.ps1` |
| `teams/` | `install-teams-app.ps1` | Install the catalog app into the target team | `verify-teams.ps1` |
| `teams/` | `verify-teams.ps1` | Read-only: team, channels, catalog publication, installation → `PASS`/`FAIL` | — |
| `common/` | `provisioning-common.ps1` | Dot-sourced helpers: settings loading, `{{PLACEHOLDER}}` fail-fast, status lines, app-only Graph/PnP/Dataverse auth | — |
| `dataverse/` | `ensure-schema-helpers.psm1` | Pure, network-free module: parses `src/solutions/RevitaliseGrantAutomation/**` XML into Dataverse Web API metadata payloads for `ensure-schema.ps1`. A `.psm1`, not a `.ps1`, so it is a function library rather than an entry-point script and is exempt from the Script Contract below (no `-Env`, no `Exit-Provisioning`). | — |
| `deploymentSettings/` | `dev-settings.example.json` | Example per-environment settings file — copy to `<env>-settings.json`, replace every `{{PLACEHOLDER}}` | — |

All per-environment values (URLs, object IDs, app IDs) live in
`deploymentSettings/<env>-settings.json` — the example file uses `{{PLACEHOLDER}}` tokens
and every script fails fast on an unresolved token (C-TECH-031/047). Settings files hold
identifiers only, never secrets: the provisioning app id and certificate thumbprint come
from the `PROVISION_APP_ID` / `PROVISION_CERT_THUMBPRINT` environment variables (CI secrets).

## Execution Points

| Block in `pipeline.yml` | When | Gate |
|---|---|---|
| `tenant_prerequisites` | Once, before any environment deployment (Stage 0) | `APPROVE TENANT` |
| `environments.<env>.post_deploy` | After each solution import, before smoke tests | The environment's gate |

Tenant-level scripts (`entra/*`, `teams/publish-teams-app.ps1`, first run of
`sharepoint/ensure-site.ps1`) also take `-Env`: it selects which settings file supplies
the per-environment definitions (e.g. persona groups per environment). Run them once per
target environment's settings file — idempotency makes repeat runs report `EXISTS`.

## Script Contract

Every script in this directory must:

1. **Be idempotent** (`C-TECH-042`) — check before create; safe to re-run on pipeline
   retry. Never fail because the resource already exists.
2. **Print one line per resource**: `CREATED | EXISTS | FAILED — <resource name>`.
   The pipeline-agent copies these into the Deployment Summary.
3. **Exit non-zero on any `FAILED`** — the pipeline halts on the first failing step.
4. **Take `-Env <dev|test|acc|prd>`** and resolve all environment-specific values
   (URLs, group object IDs, team IDs) from `deploymentSettings/<env>-settings.json`
   or environment variables — never hardcode them (`C-TECH-047`).
5. **Authenticate app-only**: Graph PowerShell / PnP.PowerShell with
   `PROVISION_APP_ID` + certificate; Dataverse Web API with the deployment service
   principal. No interactive logins, no client secrets outside CI secrets
   (see `knowledge/technology/entra-id.md`).

`entra/create-self-signed-cert.ps1` is exempt from rules 1 and 4 above, for the same
reason `ensure-schema-helpers.psm1` is exempt: it mints a local cryptographic artifact
(a certificate + private key), not a tenant resource looked up via Graph, so there is
nothing to check-before-create against a `-Env`-scoped settings file — regenerating is a
deliberate, rare, human-triggered action (rotation or provisioning a new app
registration), never a pipeline retry. It still prints `CREATED | EXISTS | FAILED` and
still never hardcodes a secret (its output is gitignored under `provisioning/certs/` and
its password is never printed, per `C-TECH-001`).

Verification counterparts (`verify-*.ps1`) assert the expected state and are reused as
pipeline smoke tests and by the test-agent's Provisioning layer. They are strictly
read-only, print `PASS | FAIL — <check>` per check, and exit non-zero on any `FAIL`.
`verify-intake-endpoint-auth.ps1` is read-only in effect rather than by method — it
sends an HTTP POST — and its own header explains why every possible outcome of that
POST writes nothing.

## Automated tests

`src/tests/provisioning/` holds the Pester suite for this directory: contract tests over
every `.ps1` file (the numbered rules above, asserted mechanically), unit tests for
`common/provisioning-common.ps1`, behavioural tests that run the Phase 1 scripts against
mocked Graph and Dataverse Web API calls, and invariant tests over the
`deploymentSettings/` files. No test makes a real API call. Run them with
`pwsh -NoProfile -File src/tests/Invoke-Tests.ps1`; the build runs the same suite with
code coverage (`config/revitalise-grant-automation-build.yml` → step `unit-tests`).
A new script in this directory is covered by the contract tests the moment it is added —
if it breaches the contract, the suite fails without anyone having to remember to
write a test for it.

### PIN PESTER 5.7.1 — a bare `Invoke-Pester` gives a content-independent false failure

```powershell
Import-Module Pester -RequiredVersion 5.7.1   # BEFORE Invoke-Pester, every time
Invoke-Pester -Path src/tests/provisioning/EnsureSchema.Tests.ps1
```

Pester **6.1.0** — the version this machine resolves by default — mis-parses a labelled
`break`/`continue` in these files' PowerShell and fails with a label crash, sometimes alongside a
misleading *"Cannot bind argument to parameter Path"*. **Three files are affected, not the two
originally recorded** (`IMP-0393`, `IMP-0411`):

| File | Why it matters |
|---|---|
| `src/tests/provisioning/DataverseScripts.Tests.ps1` | 56-test container |
| `src/tests/provisioning/EntraScripts.Tests.ps1` | — |
| **`src/tests/provisioning/EnsureSchema.Tests.ps1`** | **the file TAD A-R46 and §12.3 step 3 both name as the credential-free check to run BEFORE any live `ensure-schema.ps1` command** |

The third is the dangerous one: a crash there reads exactly like a real test failure caused by
whatever schema change you just made. Under 5.7.1 the same file yields real per-test results.
**Prove it is the runner and not your change with `git stash` and a re-run before debugging
yourself** — that is how the affected set was confirmed content-independent.

## Skeleton

```powershell
param([Parameter(Mandatory)][ValidateSet("dev","test","acc","prd")][string]$Env)
$settings = Get-Content "deploymentSettings/$Env-settings.json" | ConvertFrom-Json

$name = "[PREFIX] Case Workers"
$existing = <query for $name>
if ($existing) {
  Write-Output "EXISTS — $name"
} else {
  try   { <create>; Write-Output "CREATED — $name" }
  catch { Write-Output "FAILED — $name : $_"; exit 1 }
}
```

The concrete scripts implement this skeleton via `common/provisioning-common.ps1`
(dot-sourced): `Get-ProvisioningSettings` resolves the settings file relative to
`provisioning/` so scripts work from any working directory, `Write-ResourceStatus` /
`Write-CheckResult` emit the contract lines, and per-resource `try/catch` blocks let the
loop continue past one failing resource before `Exit-Provisioning` returns the non-zero
exit code.

## Runtime Requirements

- PowerShell 7+ (`pwsh`)
- Modules by area: `Microsoft.Graph.Authentication` (+ `.Applications`, `.Groups`,
  `.Teams`, `.Identity.SignIns`) for `entra/` and `teams/`; `PnP.PowerShell` for
  `sharepoint/`; `MSAL.PS` for the Dataverse Web API token and
  `Microsoft.PowerApps.Administration.PowerShell` for app sharing in `dataverse/`.
- The provisioning certificate (matching `PROVISION_CERT_THUMBPRINT`) installed in the
  runner's `CurrentUser` or `LocalMachine` certificate store.
