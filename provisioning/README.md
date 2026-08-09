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
| `entra/` | `ensure-app-registration.ps1` | App registrations + service principals + federated credentials, least-privilege permissions from settings | `verify-entra.ps1` |
| `entra/` | `grant-admin-consent.ps1` | Tenant-wide admin consent (appRoleAssignments / oauth2PermissionGrants) for declared permissions | `verify-entra.ps1` |
| `entra/` | `ensure-groups.ps1` | Entra security groups, one per persona per environment (existence only — membership is business/IAM-owned) | `verify-entra.ps1` |
| `entra/` | `verify-entra.ps1` | Read-only: apps, SPs, consent, groups → `PASS`/`FAIL` | — |
| `dataverse/` | `ensure-group-teams.ps1` | Dataverse group teams (AAD Security Group type) backed by Entra groups | `verify-role-bindings.ps1` |
| `dataverse/` | `bind-roles-to-groups.ps1` | Group teams **plus** security-role bindings (superset of `ensure-group-teams.ps1` — the script pipelines call; C-TECH-040) | `verify-role-bindings.ps1` |
| `dataverse/` | `ensure-document-locations.ps1` | `sharepointsites` + `sharepointdocumentlocations` records for document management | `verify-role-bindings.ps1` (Dataverse) / `verify-sharepoint.ps1` (site side) |
| `dataverse/` | `share-apps.ps1` | Model-driven apps → role association; Code/Canvas apps → share with persona Entra groups | `verify-role-bindings.ps1` |
| `dataverse/` | `verify-role-bindings.ps1` | Read-only: teams, Entra binding, role bindings, no direct user assignments (C-TECH-040) → `PASS`/`FAIL` | — |
| `sharepoint/` | `ensure-site.ps1` | Site collection + PnP template from `templates/` + persona groups into site groups | `verify-sharepoint.ps1` |
| `sharepoint/` | `verify-sharepoint.ps1` | Read-only: site, template libraries, group access → `PASS`/`FAIL` | — |
| `teams/` | `ensure-team.ps1` | Team (standard template) + channel set via Graph | `verify-teams.ps1` |
| `teams/` | `publish-teams-app.ps1` | Publish/update the Teams app package in the org catalog | `verify-teams.ps1` |
| `teams/` | `install-teams-app.ps1` | Install the catalog app into the target team | `verify-teams.ps1` |
| `teams/` | `verify-teams.ps1` | Read-only: team, channels, catalog publication, installation → `PASS`/`FAIL` | — |
| `common/` | `provisioning-common.ps1` | Dot-sourced helpers: settings loading, `{{PLACEHOLDER}}` fail-fast, status lines, app-only Graph/PnP/Dataverse auth | — |
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

Verification counterparts (`verify-*.ps1`) assert the expected state and are reused as
pipeline smoke tests and by the test-agent's Provisioning layer. They are strictly
read-only, print `PASS | FAIL — <check>` per check, and exit non-zero on any `FAIL`.

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
