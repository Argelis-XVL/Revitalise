# Microsoft Entra ID — App Registrations, Service Principals, Security Groups

> 📝 Replace `[PREFIX]` with your project's publisher prefix (from `stack-overview.md`).
> Entra ID objects are **tenant-level** — they are NOT solution components and never travel
> in a managed solution. They are managed via provisioning scripts behind the
> `APPROVE TENANT` gate (see `agents/WORKFLOW.md`) and recorded in the Deployment Summary.

## When an App Registration Is Required

| Scenario | Registration Needed | Notes |
|---|---|---|
| CI/CD deployment to Dataverse (pac auth) | ✅ One per project | Service principal + application user per environment |
| Flows calling Microsoft Graph via HTTP | ✅ | Application permissions, least privilege |
| Code App / web resource calling a custom external API | ✅ | SPA platform + redirect URIs; MSAL on the client |
| Provisioning scripts (PnP.PowerShell / Graph PowerShell app-only) | ✅ | Certificate credential, never a plain secret |
| Standard connector usage (Dataverse, SharePoint, Teams connectors) | ❌ | Connector handles auth — no registration needed |

## Naming Convention

```
[PREFIX]-<Purpose>-<Scope>

Examples:
  [PREFIX]-Deployment-SP        ← CI/CD service principal (all environments)
  [PREFIX]-Provisioning-SP      ← Graph/PnP app-only provisioning
  [PREFIX]-CasePortal-App       ← Code App calling a custom API
```

## Creating a Deployment Service Principal (Dataverse)

Preferred: PAC CLI creates the registration **and** the application user in one step:

```powershell
# Creates app registration + service principal + application user with a security role
pac admin create-service-principal --environment <environment-id> --name "[PREFIX]-Deployment-SP"
```

Repeat the application-user step per environment (Dev/Test/Acc/Prd) — the registration
is created once, the application user exists **per environment**.

## Creating a General App Registration (Graph PowerShell)

```powershell
Connect-MgGraph -Scopes "Application.ReadWrite.All"

$app = New-MgApplication -DisplayName "[PREFIX]-Provisioning-SP" `
  -SignInAudience "AzureADMyOrg"
New-MgServicePrincipal -AppId $app.AppId
```

Idempotency rule: **check before create** — look the registration up by display name first;
provisioning scripts must be safe to re-run (`C-TECH-042`).

## API Permissions & Admin Consent

- **Least privilege always** (`C-TECH-043`). Request the narrowest permission that works
  (e.g. `Sites.Selected` over `Sites.FullControl.All`; `Group.Read.All` over `Directory.Read.All`).
- Broad permissions (`*.ReadWrite.All`, `Directory.*`) require a documented justification
  in TAD §6 and an ADR.
- **Admin consent is a tenant-level operation** — it runs only behind the `APPROVE TENANT`
  gate and is recorded in the Deployment Summary:

```powershell
az ad app permission admin-consent --id <app-id>
```

## Credentials

| Credential Type | Use For | Rule |
|---|---|---|
| **Federated credential (OIDC)** | GitHub Actions CI/CD | Preferred — no secret to store or rotate |
| **Certificate** | PnP.PowerShell / Graph app-only scripts | Stored in Key Vault; thumbprint via CI secret |
| Client secret | Only where the above are unsupported | Key Vault / CI secrets only; rotation ≤ 180 days (`C-TECH-044`) |

Federated credential for GitHub Actions:

```powershell
New-MgApplicationFederatedIdentityCredential -ApplicationId $app.Id -BodyParameter @{
  name      = "github-actions-main"
  issuer    = "https://token.actions.githubusercontent.com"
  subject   = "repo:<org>/<repo>:ref:refs/heads/main"
  audiences = @("api://AzureADTokenExchange")
}
```

## Security Groups

Security groups carry **personas** — they are the bridge between Entra ID and Dataverse
security roles (see `knowledge/technology/security-model.md` for the role binding).

```
Naming:  [PREFIX]-<Persona>-<Env>
         [PREFIX]-CaseWorkers-Prd, [PREFIX]-Reviewers-Acc, [PREFIX]-Admins-Prd
```

```powershell
# Idempotent creation
$name = "[PREFIX]-CaseWorkers-Prd"
$group = Get-MgGroup -Filter "displayName eq '$name'"
if (-not $group) {
  $group = New-MgGroup -DisplayName $name -SecurityEnabled -MailEnabled:$false `
    -MailNickname ($name.ToLower() -replace '[^a-z0-9]','')
}
```

Rules:
- One group per **persona per environment** — never reuse a Prd group for Test.
- Group **membership** is owned by the business / IAM process, not by the pipeline.
  The pipeline only ensures the group **exists** and is bound to the correct role.
- Group object IDs are environment-specific values → deployment settings / Dataverse
  environment variables, never hardcoded (`C-TECH-047`).

## What Lives Where

| Object | Level | Created By | Gate |
|---|---|---|---|
| App registration + service principal | Tenant | `provisioning/entra/` script | `APPROVE TENANT` |
| Admin consent | Tenant | `provisioning/entra/` script or admin | `APPROVE TENANT` |
| Security group | Tenant | `provisioning/entra/` script | `APPROVE TENANT` |
| Application user (deployment SP) | Per environment | `pac admin create-service-principal` | `APPROVE TENANT` (first run) |
| Group team + role binding | Per environment | `provisioning/dataverse/` script (post_deploy) | Environment gate |

## References

- `knowledge/technology/security-model.md` — binding groups to Dataverse security roles
- `knowledge/technology/build-and-deploy.md` — provisioning script conventions and auth
- `constraints/technology/technology-constraints.md` §5 — C-TECH-041…044, C-TECH-047

## Graph Auth Succeeding Is Not Graph Authorisation

`Connect-MgGraph` with the provisioning certificate succeeds and `Get-MgApplication` then
returns `Authorization_RequestDenied`. Authentication and authorisation are separate failures
with one confusing symptom: a working connection that cannot read anything.

The provisioning app registration holds Dataverse permissions, not Graph application
permissions. Reading or writing app registrations, service principals or security groups needs
`Application.Read.All` / `Application.ReadWrite.All` / `Group.ReadWrite.All` granted **as
application permissions with admin consent** — a tenant-level act, so it runs behind
`APPROVE TENANT`. Until it is granted, every `provisioning/entra/` script that inspects the
directory fails this way, and the error names the permission model rather than the missing
permission (`IMP-0105`).

Diagnose it in one step: if `Connect-MgGraph` succeeded and the first read failed, it is consent,
not credentials. Do not re-issue the certificate.
