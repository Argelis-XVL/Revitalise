# Microsoft Teams — Provisioning, App Surfacing, Notifications

> 📝 Replace `[PREFIX]` with your project's publisher prefix (from `stack-overview.md`).
> Teams and Teams apps are **not solution components**. Teams are provisioned per
> environment scope by idempotent scripts in `provisioning/teams/`; publishing an app to
> the **org-wide app catalog** is a tenant-level operation → `APPROVE TENANT` gate.
> Dataverse for Teams (built-in Teams environments) is explicitly **out of scope** —
> all apps run in the standard Dev/Test/Acc/Prd environments.

## What Teams Is Used For

| Use | Pattern |
|---|---|
| Notifications from flows | Teams connector + Adaptive Cards into a channel |
| Approvals | Power Automate Approvals — surfaced natively in Teams |
| Collaboration workspace per domain | Provisioned team with standard channels |
| Surfacing apps to users | Teams app (manifest) with the MDA / Code App as a tab |

## Team Provisioning (Microsoft Graph)

```
Naming:  [PREFIX]-<Purpose>            e.g. [PREFIX]-CaseManagement
Channels: General + 📝 define your standard channel set per project
```

```powershell
Connect-MgGraph -ClientId $env:PROVISION_APP_ID `
  -CertificateThumbprint $env:PROVISION_CERT_THUMBPRINT -TenantId $env:TENANT_ID

# Idempotent: check before create (C-TECH-042)
$name = "[PREFIX]-CaseManagement"
$existing = Get-MgGroup -Filter "displayName eq '$name' and resourceProvisioningOptions/any(x:x eq 'Team')"
if (-not $existing) {
  New-MgTeam -BodyParameter @{
    "template@odata.bind" = "https://graph.microsoft.com/v1.0/teamsTemplates('standard')"
    displayName = $name
    description = "[Purpose]"
  }
}
```

- Provisioning a team also creates its **Teams-connected SharePoint site** — do not
  provision a separate site for team file storage (see `sharepoint.md`).
- Team owners: the persona's admin group. Membership: business/IAM-managed, mirroring
  the Entra groups from `security-model.md` — the pipeline only ensures existence.
- Team and channel **IDs** are environment-specific values → Dataverse environment
  variables / deployment settings, never hardcoded (`C-TECH-047`).

## Teams App Package (surfacing an app as a tab)

The Teams app manifest lives in source control:

```
src/teams-apps/<app-slug>/
├── manifest.json        ← staticTabs.contentUrl points to the app URL (env-specific)
├── color.png            ← 192×192 icon
└── outline.png          ← 32×32 icon
```

Rules:
- `manifest.json` version is bumped every release; the packaged zip is a **build
  artifact** (`build.yml` → `artifacts` block), produced by zipping the folder.
- Environment-specific URLs in the manifest are tokenised and substituted at
  package time from deployment settings — one package per target environment.
- **Publish to the org app catalog** (tenant-level, `APPROVE TENANT`):

```powershell
# Publish (first time) or update (subsequent versions)
$pkg = "build/artifacts/<slug>-<date>-<n>/teams-app-<env>.zip"
# Graph: POST /appCatalogs/teamsApps (new) or POST /appCatalogs/teamsApps/{id}/appDefinitions (update)
```

- **Install into a team** (per environment scope, post_deploy step):
  Graph `POST /teams/{team-id}/installedApps` with the catalog app ID, then pin the
  tab to a channel where the design requires it.
- Availability is scoped via Teams admin center app permission policies to the same
  persona groups — app access itself is still enforced by Dataverse security roles
  (`security-model.md`); the Teams tab is only a window.

## Notification Design Rules (flows → Teams)

- Use **Adaptive Cards**, not free-text chat messages; card templates versioned in
  the solution alongside the flow.
- Target team/channel resolved from **environment variables** — never a hardcoded ID.
- **No Tier 3/4 data in cards** (see `skills/data-classification.md`): cards carry the
  record name, status, and a **deep link** into the app — the app enforces access.
- The Teams connector does not support service-principal connections — use a
  dedicated **service account** connection in non-Dev environments, documented in
  TAD §4 (exception to the service-principal rule in `power-automate.md`).

## Verification (test-agent)

1. Team exists with required channels; owners are the intended admin group.
2. Teams app is published in the catalog at the expected version and installed in
   the target team.
3. Notification flow posts a card into the correct channel (integration test);
   card contains no Tier 3/4 data (compliance check).
4. Deep link opens the record in the app for an authorised persona; unauthorised
   users are blocked by Dataverse security (not by the card).
