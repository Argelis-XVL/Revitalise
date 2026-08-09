# SharePoint Online — Sites & Dataverse Document Management

> 📝 Replace `[PREFIX]` with your project's publisher prefix (from `stack-overview.md`).
> SharePoint sites are **not solution components** — they are provisioned per environment
> by idempotent scripts in `provisioning/sharepoint/`, executed via pipeline `post_deploy`
> steps. Creating a **new site collection** is a tenant-level operation → `APPROVE TENANT` gate.

## What SharePoint Is Used For

| Use | Pattern |
|---|---|
| Document storage for Dataverse records | Server-based SharePoint integration + document locations |
| Collaboration / publishing sites | Communication or Team site per purpose |
| Teams file storage | Teams-connected site — provision the **team**, the site comes with it (see `teams.md`) |

## Site Conventions

```
Site name:  [PREFIX]-<Purpose>-<Env>          e.g. [PREFIX]-CaseDocs-Test
Site URL:   https://<tenant>.sharepoint.com/sites/[prefix]-<purpose>-<env>
```

- One site per purpose **per environment** (Dev/Test/Acc/Prd) — never point two
  environments at the same site.
- The site URL is stored as a **Dataverse environment variable**
  (`[prefix]_SpoSiteUrl`) and injected via deployment settings — never hardcoded
  in flows, apps, or scripts (`C-TECH-047`).

## Provisioning (PnP.PowerShell, app-only)

Authenticate with the provisioning app registration + certificate
(see `entra-id.md` — never a plain client secret):

```powershell
Connect-PnPOnline -Url $env:SPO_ADMIN_URL -ClientId $env:PROVISION_APP_ID `
  -Thumbprint $env:PROVISION_CERT_THUMBPRINT -Tenant $env:TENANT_ID

# Idempotent: check before create (C-TECH-042)
$url = "https://<tenant>.sharepoint.com/sites/[prefix]-casedocs-test"
if (-not (Get-PnPTenantSite -Url $url -ErrorAction SilentlyContinue)) {
  New-PnPSite -Type CommunicationSite -Title "[PREFIX]-CaseDocs-Test" -Url $url
}

# Apply structure (libraries, content types, fields) from a versioned template
Connect-PnPOnline -Url $url -ClientId $env:PROVISION_APP_ID `
  -Thumbprint $env:PROVISION_CERT_THUMBPRINT -Tenant $env:TENANT_ID
Invoke-PnPSiteTemplate -Path provisioning/sharepoint/templates/<purpose>-template.xml
```

- Site **structure** (libraries, content types, columns) lives in a PnP site template
  XML committed to `provisioning/sharepoint/templates/` — the template is the source
  of truth, re-applied on change (idempotent by design).
- Prefer `Sites.Selected` Graph/SPO permission granted per site over tenant-wide
  `Sites.FullControl.All` (`C-TECH-043`).

## Permissions

- Map the **same Entra security groups** used for Dataverse personas
  (see `security-model.md`) into the site's Owners / Members / Visitors groups —
  one access model across Dataverse and SharePoint.
- Do not break permission inheritance below library level; item-level unique
  permissions do not scale and defeat auditability. Exceptions documented in TAD §6.

## Dataverse Document Management Integration

Two parts, different lifecycles:

1. **Server-based SharePoint integration** — enabled **once per environment** by an
   admin (Power Platform admin center → Document management). Record this as a
   tenant/environment prerequisite in `pipeline.yml` → `tenant_prerequisites`.
2. **Document locations** — per table + per environment, created in a `post_deploy`
   step via the Dataverse Web API:

```http
POST [org-url]/api/data/v9.2/sharepointsites
{ "name": "[PREFIX] Case Docs", "absoluteurl": "<site-url-from-env-var>" }

POST [org-url]/api/data/v9.2/sharepointdocumentlocations
{
  "name": "Documents on Default Site",
  "relativeurl": "[prefix]_case",
  "regardingobjectid_[prefix]_case@odata.bind": null,
  "parentsiteorlocation_sharepointsite@odata.bind": "/sharepointsites(<site-id>)"
}
```

> Dataverse creates one folder per record (`<name>_<guid>`) inside the library.
> Do not fight this convention with custom folder logic — report on metadata instead.

## Flows Using the SharePoint Connector

- Connection reference: `[prefix]_SharedSharepoint` — defined in the solution,
  connection supplied per environment via deployment settings.
- The SharePoint connector does **not** support service-principal connections —
  use a dedicated **service account** connection in non-Dev environments and
  document it in TAD §4 (exception to the service-principal rule in `power-automate.md`).
- Site address and library name come from environment variables, never literals.

## Governance

- New site collections: `APPROVE TENANT` gate, recorded in the Deployment Summary.
- Retention and sensitivity labels: 📝 define per project in
  `knowledge/domain/compliance-requirements.md`; apply via the site template.
- Site deletion is never automated — human-only, with compliance sign-off.

## Verification (test-agent)

1. Site exists and template artefacts (libraries, content types) are present.
2. `sharepointdocumentlocation` records exist for each table in TAD §12.
3. Uploading a document from the MDA record lands in the correct library (E2E).
4. Persona groups have the intended site access level; others are denied.
