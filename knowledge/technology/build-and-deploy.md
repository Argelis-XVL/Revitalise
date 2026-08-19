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

## First Import Into a New Environment

The order below is the one that works. Steps 1–2 are the prerequisites whose absence turned a
"just import it" task into a **fifteen-attempt investigation** on this project's first DEV
deployment (`docs/development/revitalise-grant-automation-dev-deployment-handover.md`).
Re-read this before the first import into **each** environment — DEV, TST/ACC and PRD alike.

**1. Create the schema the import cannot create** (`C-TECH-050`)

```powershell
pwsh -NoProfile -File provisioning/dataverse/ensure-schema.ps1 -Env <env>
```

Entities/Attributes, Global OptionSets, Security Roles and Field Security Profiles are
documented by Microsoft as unsupported to create from scratch via solution import. Create
them via the Web API first; import can manage them afterwards. The script is idempotent — a
clean re-run reports `EXISTS` for everything it previously made. Anything else needs
investigating **before** you import.

**2. Reconcile platform-assigned ids into source** (`C-TECH-051`)

Dataverse assigns its own ids to what step 1 created. Read them back and put the real values
in source:

```
GET {env}/api/data/v9.2/roles?$filter=name eq '<Role Name>'&$select=roleid,name
GET {env}/api/data/v9.2/fieldsecurityprofiles?$filter=name eq '<Profile>'&$select=fieldsecurityprofileid,name
```

This makes those files environment-specific, which is why promotion between environments
goes via Pipelines rather than re-importing the same source, and why binding scripts look
components up **by name**. Where a component type allows referencing by `schemaName` instead
of `id`, use it and skip the problem entirely.

**3. Run the build gates locally** — every `verify-*` step in `config/<slug>-build.yml`, plus
the test suite. They are cheap and they name the offending file; the import does not.

**4. Pack and import.** A full clean import of a mid-sized solution takes **60–100 seconds**
plus 20–45s to publish. **Anything that fails in under ~40 seconds failed early, at a
structural stage** — before the platform ever looked at your content.

**5. Verify by execution — three separate things** (`C-TECH-053`):

```
(a) Query each component. Do not infer existence from the import result.
    GET {env}/api/data/v9.2/workflows?$filter=startswith(name,'<PREFIX>')&$select=name,statecode
    GET {env}/api/data/v9.2/appmodules?$filter=uniquename eq '<name>'
    GET {env}/api/data/v9.2/environmentvariabledefinitions?$filter=startswith(schemaname,'<prefix>')
(b) Re-run the same import. It must succeed again cleanly.
(c) Open every flow in the designer and press Save.
```

**(c) cannot be automated away.** Three of the fifteen failures were invisible to (a) and
(b): the solution imported, the flow existed and was queryable, and no maker could open it.

## Diagnosing a Failed Import

`pac solution import` returns a terse one-line reason. It is not the diagnosis. Get the
platform's own record before forming any theory:

```powershell
# Full per-component detail — names the component and the field
pac env fetch --xmlFile importjob-query.xml     # FetchXML over importjob, selecting `data`

# For a generic "An unexpected error occurred", the stack trace names the failing handler
# GET {env}/api/data/v9.2/asyncoperations(<async-op-guid>)?$select=message,friendlymessage,statuscode
```

`asyncoperations.message` carries a full .NET stack trace. Handler names in it
(`ImportAppModulesHandler`, `SourceControlHandler`, `ImportRootComponentsHandler`) identify
the failing component type even when the message itself says nothing useful.

**When a component's shape is the question, build one for real and look at it.** Create a
minimal instance via the Web API — or the maker portal, for things like model-driven apps —
then `pac solution export` + `pac solution unpack` and read how the platform serialises it.
This resolved four of the six import blockers faster than any amount of documentation
research or error-message iteration. Procedure:
`skills/how-to-verify-a-platform-contract.md`.

**Two failed guesses is the signal to stop guessing.** Each import attempt costs a full
cycle and reveals exactly one defect, because the platform stops at the first thing it
dislikes. Ground truth reveals all of them at once.

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

---

## Operating Facts of This Repository and Machine

Applied 2026-08-18 from `logs/improvement-log.jsonl` (IMP-0003, IMP-0010, IMP-0021). Each was
proposed as a knowledge line when it happened and never written down until this review, so each
had to be rediscovered at least once.

**Credential material lives outside the repository, not merely gitignored.** The `secret-scan`
gate reads the **working tree** (`gitleaks detect --no-git`), which is correct and deliberate —
scanning history instead is the defect `IMP-0002` recorded. A real `.pfx`/`.cer`/`.pem` sitting
in `provisioning/certs/` therefore blocks the build even though it is untracked and ignored, and
no version-control leak exists. Keep certificates in the OS keystore or a path outside the repo
root. `IMP-0003`.

**This repository's path contains spaces**, and not every tool handles that. `pac solution check
--outputDirectory` reports a download and silently writes nothing; read the result from **stdout**
instead of expecting the file. Suspect this class first when a CLI reports success and produces no
artefact here. `IMP-0010`.

**Some cleanup operations cannot be executed by an agent in this environment at all.** The
`DeleteOptionValue` metadata call needed to remove option-set values orphaned by import
(`IMP-0019`) was refused by the session's own safety classifier, independently of Dataverse
authorisation. Destructive metadata operations of this shape are routed to the reviewer to perform
in the maker portal, and the request is recorded rather than retried. `IMP-0021`.
