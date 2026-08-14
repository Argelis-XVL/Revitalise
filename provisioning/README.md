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
| `dataverse/` | `share-apps.ps1` | Model-driven apps → role association; Code/Canvas apps → share with persona Entra groups | `verify-role-bindings.ps1` |
| `dataverse/` | `verify-role-bindings.ps1` | Read-only: teams, Entra binding, role bindings, no direct user assignments (C-TECH-040) → `PASS`/`FAIL` | — |
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
