# Build & Deploy — PAC CLI

> 📝 Replace `<SolutionName>` with your solution's unique name (e.g. `PROJ_CaseManagement`).
> Replace `[prefix]_` with your publisher prefix (e.g. `proj_`, `hr_`).

## Code Apps Build (React / Vite)

Code Apps use the `pac code` toolchain — they are **not** web resources and **not** PCF
controls (see `knowledge/technology/code-apps.md`):

```powershell
# Build and verify (per app, or script across src/code-apps/*)
cd src/code-apps/<app-slug>
npm ci
npm run lint
npm run build   # outputs to dist/

# Publish to the connected (Dev) environment
pac code push
```

> The `dist/` folder and `node_modules/` are gitignored.
> `power.config.json`, `src/**`, and generated data-source services are committed.

The code app is added to the feature solution in Dev, so downstream environments
receive it inside the **managed solution** import — no separate push. If your tenant
does not yet support solution-packaged code apps, run `pac code push` per environment
as a `post_deploy` step instead (document the deviation in TAD §9).

## Core Commands

```powershell
# Authenticate (Service Principal)
pac auth create --name <ProjectName>_Dev --url $env:ENV_URL_DEV `
  --applicationId $env:APP_ID --clientSecret $env:CLIENT_SECRET --tenant $env:TENANT_ID

# Export solution (unmanaged from Dev)
pac solution export --name <SolutionName> --path build/exports/<SolutionName>.zip --managed false

# Unpack into source (commit result to git)
pac solution unpack --zipFile build/exports/<SolutionName>.zip --folder src/solutions/<SolutionName> --processCanvasApps false

# Pack from source
pac solution pack --zipFile build/artifacts/<SolutionName>-managed.zip --folder src/solutions/<SolutionName> --packageType Managed

# Import managed solution to Test/Acc/Prd
pac solution import --path build/artifacts/<SolutionName>-managed.zip --activate-plugins --force-overwrite

# Run Solution Checker
pac solution check --path build/artifacts/<SolutionName>-managed.zip --geo Europe --outputDirectory docs/architecture/

# Publish all customisations (Dev only)
pac solution publish

# List available solutions
pac solution list
```

## Environment Variable Conventions

| Variable | Description |
|---|---|
| `ENV_URL_DEV` | Dev environment URL |
| `ENV_URL_TEST` | Test environment URL |
| `ENV_URL_ACC` | Acc environment URL |
| `ENV_URL_PRD` | Prd environment URL |
| `APP_ID` | Deployment Service Principal application ID |
| `CLIENT_SECRET` | Deployment SP secret (CI secret — prefer federated credentials, see `entra-id.md`) |
| `TENANT_ID` | Microsoft Entra tenant ID |
| `PROVISION_APP_ID` | Provisioning app registration ID (Graph / PnP app-only) |
| `PROVISION_CERT_THUMBPRINT` | Certificate thumbprint for provisioning auth (cert in Key Vault) |
| `SPO_ADMIN_URL` | SharePoint admin site URL (`https://<tenant>-admin.sharepoint.com`) |

All set as GitHub Actions secrets. Never hardcoded in any file.

## Deployment Parameters

Use **deployment settings files** to supply environment-specific values (connection references, environment variables) without modifying the solution:

```json
// deploymentSettings/test-settings.json
{
  "EnvironmentVariables": [
    { "SchemaName": "[prefix]_ApiBaseUrl", "Value": "https://api.test.internal" }
  ],
  "ConnectionReferences": [
    { "LogicalName": "[prefix]_SharedDataverse", "ConnectionId": "/providers/..." }
  ]
}
```

Pass to import:
```powershell
pac solution import --path build/artifacts/<SolutionName>-managed.zip `
  --settings-file deploymentSettings/test-settings.json
```

## Provisioning & Post-Deployment Configuration

Everything the feature needs that **cannot ship in a solution** is scripted, committed,
and executed by the pipeline-agent — never applied by hand:

```
provisioning/
├── entra/          ← app registrations, admin consent, security groups
├── dataverse/      ← group teams, role bindings, document locations, app sharing
├── sharepoint/     ← site creation + PnP site templates (templates/ subfolder)
└── teams/          ← team provisioning, Teams app catalog publish + install
```

| Rule | Detail |
|---|---|
| Idempotent | Every script checks before creating (`C-TECH-042`) — safe to re-run on retry |
| Two execution points | `tenant_prerequisites` (once, gate: `APPROVE TENANT`) and per-environment `post_deploy` blocks in `config/<slug>-pipeline.yml` |
| Auth | Graph PowerShell / PnP.PowerShell app-only with `PROVISION_APP_ID` + certificate; Dataverse Web API with the deployment SP |
| Parameters | Environment-specific values (site URLs, group object IDs, team IDs) come from `deploymentSettings/<env>-settings.json` — never literals (`C-TECH-047`) |
| Output | Each script prints `CREATED` / `EXISTS` / `FAILED` per resource — pipeline-agent records this in the Deployment Summary |

Typical `post_deploy` sequence for a security-role feature:
1. `dataverse/bind-roles-to-groups.ps1` — create group team for the Entra group, associate security role (see `security-model.md`)
2. `dataverse/ensure-document-locations.ps1` — SharePoint document locations (see `sharepoint.md`)
3. `teams/install-teams-app.ps1` — install/update the Teams app in the target team (see `teams.md`)
4. `dataverse/share-apps.ps1` — share Code/Canvas apps with the persona groups

## Solution Checker Quality Gate

Zero **Critical** or **High** severity issues permitted.
Run:
```powershell
pac solution check --path build/artifacts/<SolutionName>-managed.zip --geo Europe
```
Parse the output — if any Critical/High issues exist, build-agent reports FAILED.
Approved exceptions documented in `docs/architecture/<slug>-architecture.md §11`.

## Rollback

Rollback = re-import the previous managed artifact:
```powershell
pac solution import --path build/artifacts/<SolutionName>-<previous-date>-<n>-managed.zip `
  --activate-plugins --force-overwrite `
  --settings-file deploymentSettings/<env>-settings.json
```

Prd rollback requires explicit human instruction — never automatic.
