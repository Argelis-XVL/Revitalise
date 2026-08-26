# Testing Tools — Power Platform

## Tool Stack

| Layer | Tool | Notes |
|---|---|---|
| Unit (business logic) | Dataverse Web API tests (PowerShell or C#) | Invoke plugins, custom APIs, and validate data outcomes |
| Unit (Code Apps) | Vitest + React Testing Library | Component and hook tests; mock Dataverse responses |
| Flow testing | Power Automate Test Studio | Where available; supplement with manual trigger + audit verification |
| UI / E2E (MDA) | EasyRepro (Selenium-based) | Automates MDA forms; runs against Test environment |
| UI / E2E (Code Apps) | Playwright | Full browser automation for Code App flows against Test environment |
| Solution quality | PAC Solution Checker (`pac solution check`) | Integrated into build pipeline; zero Critical/High permitted |
| Performance | JMeter / k6 against Dataverse Web API | Validate NFR thresholds at Test environment load |
| Accessibility | Accessibility Insights for Web (axe-core) | Run on every new/changed MDA form and Code App page |
| Security | Manual penetration test checklist | Prior to every Prd release |
| Provisioning verification | Microsoft Graph PowerShell + Dataverse Web API asserts | Verify TAD §12 items: sites, teams, groups, group teams + role bindings, app sharing |

## Provisioning Verification

Assert every TAD §12 item and §6.1 mapping row after `post_deploy` runs — the
expected-state queries are defined in the Verification sections of
`security-model.md`, `sharepoint.md`, and `teams.md`. Typical asserts:

```powershell
# Group team exists and is bound to the right Entra group
$team = (Invoke-RestMethod -Headers $auth `
  -Uri "$envUrl/api/data/v9.2/teams?`$filter=name eq '[PREFIX] Case Workers'&`$expand=teamroles_association").value
if (-not $team -or $team.azureactivedirectoryobjectid -ne $expectedGroupId) { exit 1 }

# No direct user role assignments in Test/Acc/Prd (C-TECH-040)
# SharePoint site + document locations exist (see sharepoint.md)
# Teams app installed in target team at expected version (see teams.md)
```

Scripts live in `provisioning/**/verify-*.ps1` and are reused as pipeline smoke tests.

## Vitest + React Testing Library (Code Apps)

```bash
# Install (per Code App)
npm install -D vitest @testing-library/react @testing-library/user-event @testing-library/jest-dom jsdom
```

```typescript
// vite.config.ts — add test block
export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./src/setupTests.ts",
  },
});
```

```typescript
// src/setupTests.ts
import "@testing-library/jest-dom";
```

Tests live in `src/code-apps/<app-slug>/src/__tests__/`.
Run via `npm test` (Vitest watch) or `npm run test:ci` (single pass) in CI.

Mock Dataverse responses at the service layer — never make real API calls in unit tests.

## Playwright (Code Apps E2E)

```bash
npm install -D @playwright/test
npx playwright install
```

```typescript
// playwright.config.ts
import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  use: {
    baseURL: process.env.ENV_URL_TEST,
  },
});
```

E2E tests live in `src/code-apps/<app-slug>/e2e/`.
Run via `npx playwright test` in CI against the Test environment.
All E2E tests must pass before build-agent raises a READY handoff.

## EasyRepro Setup

```powershell
# Install NuGet package
Install-Package Microsoft.PowerApps.UIAutomation.Sample

# Configure test settings
# tests/EasyRepro/TestSettings.json
{
  "OnlineUsername": "$env:TEST_USER",
  "OnlinePassword": "$env:TEST_PASS",
  "OnlineCrmUrl": "$env:ENV_URL_TEST",
  "AzureKey": "$env:APPLICATIONINSIGHTS_KEY"
}
```

EasyRepro tests live in `src/tests/EasyRepro/`.
Run via `dotnet test src/tests/EasyRepro/` in CI.

## Dataverse Web API Tests

Use PowerShell + `Invoke-RestMethod` or the `Microsoft.Xrm.Sdk` to:
- Create test data
- Invoke custom API actions
- Assert column values, relationship records, audit entries

Test scripts live in `src/tests/dataverse/`.

## Test Data Strategy

- All test data created programmatically at test start; cleaned up at test end
- No personal data — use synthetic data generators
- Sensitive test data uses clearly marked fake identities (e.g. `TEST_*` prefix)
- Test data isolated per test run using a unique run ID column

## Flow Test Approach

1. Trigger the flow with a test Dataverse record
2. Poll for completion (check `[prefix]_flowexceptionlog` and target record state)
3. Assert: expected record state, expected notifications sent (mock connector), no exception log entries
4. Verify domain-specific controls (defined in `knowledge/domain/compliance-requirements.md`)

## Solution Checker in CI

```powershell
pac solution check `
  --path build/artifacts/$slug-managed.zip `
  --geo Europe `
  --outputDirectory docs/architecture/

# Parse result — fail build if any Critical or High issues found
$result = Get-Content docs/architecture/checker-result.json | ConvertFrom-Json
if ($result.Issues | Where-Object { $_.Severity -in 'Critical','High' }) {
  Write-Error "Solution Checker: Critical/High issues found. Build halted."
  exit 1
}
```

---

## Verifying live Dataverse state

Established 2026-08-19. Two working paths from this Mac. The Platform Contract and
Verification Level test layers need this, and both were being rebuilt from scratch each round.

**FetchXML against the active `pac` profile** — for ordinary tables (`stringmap`, `sitemap`,
`entitykey`, `systemform`, `savedquery`):

```bash
pac env fetch --xmlFile query.xml
```

The query must carry **no paging attributes** — a `top="20"` on `<fetch>` fails with
*"The top attribute can't be specified with paging attribute page"*.

**The Web API, for metadata** — `EntityDefinitions`, `GlobalOptionSetDefinitions`,
`Keys`/`EntityKeyIndexStatus`, `organizations`, `fieldpermissions`. FetchXML cannot reach these.
Use the provisioning identity's certificate, which is already in this Mac's login keychain:

```powershell
. ./provisioning/common/provisioning-common.ps1
Import-Module ./provisioning/common/provisioning-cert.psm1 -Force
$auth = [pscustomobject]@{
  TenantId       = '735a23b1-97d7-4c81-85f7-35c50321138a'
  AppId          = '077f1f90-3218-4a06-bc90-887464353aa7'
  CertThumbprint = 'A6F94E1801D1C62B7A82AE75E1AA5AD243ECC7FE'
}
$token = Get-DataverseAccessToken -Auth $auth -EnvironmentUrl $url
Invoke-DataverseApi -Method GET -EnvironmentUrl $url -AccessToken $token -Path $path
```

Put the PowerShell in a **file** and run `pwsh -NoProfile -File`. Inlining it in
`pwsh -Command` inside a shell string mangles the `$select` / `$expand` escaping.

**The block above is PowerShell and only runs inside `pwsh`.** It builds `$auth` in-session
because this recipe *is* a `pwsh` session — it is not the pattern for running a
`provisioning/**` script, which reads the same two values from the **outer** shell. That shell
is zsh here, the syntax is `export VAR=value`, and the canonical copy-pasteable block lives in
`knowledge/technology/build-and-deploy.md` → *First Import Into a New Environment*. Never
translate this example into an instruction for a human by keeping its `$env:` / `$auth` syntax:
in zsh, `$env:PROVISION_APP_ID` silently mis-parses into a garbled path error that hides the
real cause (`IMP-0253`).

### Three traps, each of which cost a cycle

**`startswith(objecttypecode, 'rev_')` fails** on `systemform` and `savedquery` with an Int32
conversion error, even though the column is a string holding the logical name. Use equality
instead: `objecttypecode eq 'rev_grant'`.

**`IsAuditEnabled` is a `BooleanManagedProperty`, not a bool.** The flag is `.Value`; the
sibling `.CanBeChanged` says whether the managing solution permits a change at all. Reading
the object itself gives you a truthy value regardless of the setting.

**Reads are permitted; writes may not be.** Every query above runs freely. The metadata
`PATCH` that would switch auditing on was refused by the session's own safety classifier under
an explicit `APPROVE TENANT`. Establish the permission before promising a live change — see
`agents/pipeline-agent.md` → *Reviewer-executed operations*.

### What a live sweep should cover

Derive the list from source, never by hand (`IMP-0013`): one query per entity folder under
`Entities/`, one per file under `OptionSets/`, every `IsSecured=1` column against
`fieldpermissions`, `systemuserroles` for direct role assignments, and the two audit switches.
`C-TECH-064` is the constraint that requires it.

### Reading a form, and reading column metadata — two corrections, both verified 2026-08-21

**A form is filtered by `formid`, never by `objecttypecode`.** The recipe recorded earlier in this
project said `objecttypecode eq 'rev_grant'` works on `systemform` where `startswith()` fails. It
does not. Any string value in a *condition* on that column raises
`System.FormatException ... convert input value to attribute 'systemform.objecttypecode'. Expected
type: System.Int32`, through both `pac env fetch` and `pac org fetch` — the column selects fine and
cannot be filtered on. `systemformid` is not an attribute name either. What works:

```xml
<filter><condition attribute="formid" operator="eq" value="6a6004bd-..." /></filter>
```

Take the form id from the source file name under `Entities/<table>/FormXml/main/`. Verified: 77 KB
of live `formxml` returned for `rev_application`'s main form, which is how the 14 multi-line cells
were counted before and after an import.

**Column length and format are metadata, and FetchXML cannot see them.** Use the Web API path,
and cast to the right metadata type or you get a 404 that looks like a missing column:

```
EntityDefinitions(LogicalName='rev_setting')/Attributes(LogicalName='rev_description')
  /Microsoft.Dynamics.CRM.StringAttributeMetadata?$select=LogicalName,MaxLength,FormatName
```

**The 404 trap:** that cast is for `String` (nvarchar) only. A `Memo` (ntext) column — which is
what `rev_conditions`, `rev_impactreport`, `rev_manualacceptancenote` and `rev_errormessage` all
are — returns **404 Not Found** under `StringAttributeMetadata`, indistinguishable from a column
that does not exist. Before concluding a column is missing, query
`Attributes?$select=LogicalName,AttributeType` without a cast and read the type first.

### Writing ANY metadata is PUT, not PATCH — and the cast does not carry over

**This rule is about the endpoint family, not about columns.** It was first written here scoped to
*column* metadata, because a column write was what had failed (`IMP-0272`). *Table* metadata failed
next, the same day, with a different error code (`IMP-0276`). The rule below governs every
Dataverse Web API metadata collection — `EntityDefinitions`, the `Attributes` collection nested
under it, `GlobalOptionSetDefinitions`, `RelationshipDefinitions` and `EntityKeyDefinitions` —
whether or not anyone has written against that one yet. It is enforced by
`scripts/verify-metadata-write-verbs.py` (`C-TECH-073`), so a new instance fails a build rather
than a live run.

**The trap is that a data record and a metadata endpoint are indistinguishable in this codebase.**
`organizations`, `fieldpermissions` and `rev_setting` are ordinary records and take normal `PATCH`
semantics; `EntityDefinitions` is metadata and never does. Both are written by the same helper,
sometimes a few lines apart in the same script — `ensure-auditing.ps1` does exactly this, and the
organisation-level `PATCH` above its table loop is correct while the table-level `PATCH` below it
never worked.

**`PATCH` is not a supported verb on `EntityDefinitions(...)/Attributes(...)`.** It returns
`{"error":{"code":"","message":"The requested resource does not support http method 'PATCH'."}}`
— a verb rejection, with no hint about casts or types. Verified live in DEV on 2026-08-24 against
five lookup columns (`IMP-0272`).

The documented update shape, from Microsoft's own *Update a column* worked example (`IMP-0273`):

1. **GET the whole object through the concrete cast, with no `$select`** —
   `.../Attributes(LogicalName='x')/Microsoft.Dynamics.CRM.LookupAttributeMetadata`. The cast is
   needed here, and the full object is needed because step 3 replaces it wholesale.
2. Mutate the one property, add `@odata.type`, and remove `@odata.context` — that is a read-only
   response annotation and must not be echoed back.
3. **PUT the entire object to the UNCAST URI** — `.../Attributes(LogicalName='x')`, with
   `MSCRM.MergeLabels: true`. **The cast segment belongs on the GET only; it does not carry over
   to the write.** A partial body is the same mistake as PATCH, aimed at a different verb.

**`MSCRM.MergeLabels: true` is not boilerplate — omitting it is a DESTRUCTIVE write.** The header
tells Dataverse to *merge* the localised label collections of the object being written
(`DisplayName`, `Description`, and every `LocalizedLabel` under them). Without it the platform
*replaces* them with exactly what the body carries. A full-object `PUT` assembled from a `GET`
made in one language therefore deletes every other language's labels on that column or table —
silently, with a 204, on a call whose whole intent was to flip one boolean. The default is the
dangerous one, which is why `verify-metadata-write-verbs.py` warns on any metadata `PUT` in a file
that never sets it. No finding recorded this; it comes from the platform documentation, and it is
written down here because the corrected scripts set the header and nothing said why.

**Two traps that read identically and have different fixes.** A wrong cast on the read side fails
with a **404**; an unsupported verb on the write side fails with a **method** error. Both look
like "the naive call was wrong", and `IMP-0272` pattern-matched the second onto the first —
diagnosing a missing cast segment and proposing `PATCH` + cast, which would have failed a third
time on the same five columns. Fetch the platform's own worked example before modelling one
metadata write on another.

**Why the wrong precedent looked right, and then stopped looking right (`IMP-0276`):**
`ensure-auditing.ps1` used to PATCH `EntityDefinitions(LogicalName='x')` to set entity-level
`IsAuditEnabled`, and every prior run reported success — but only because `IsAuditEnabled` was
already `true` on all six pre-existing tables and the script's own idempotency check skipped the
write every time. The first run that actually needed the write to happen (four new WBS 0.4
finance tables, all `IsAuditEnabled=false`) failed live on every one, with `0x80060888`
"Operation not supported on EntityMetadata" — the identical PUT-only rule this section
documents for `Attributes`, generalised to `EntityDefinitions` itself: **entity metadata is
PUT-only too, not merely the attribute metadata nested under it.** `ensure-auditing.ps1` is now
fixed onto the same GET-full-object → mutate → PUT-uncast-URI shape; unlike `Attributes`,
`EntityDefinitions` is not polymorphic (one concrete type, `EntityMetadata`), so its fix needs no
cast segment at all, on either the GET or the write.

Live confirmation of both PUT-based fixes is still outstanding — Dev Summary §10 rows `A-FIN-06`
(the attribute-level fix) and `A-FIN-07` (this entity-level fix), open until the reviewer's
re-runs report `CREATED`/`EXISTS` with zero `FAILED` lines and a read-back confirms the flag.

The auth triplet and the `Get-DataverseAccessToken -Auth <object> -EnvironmentUrl` /
`Invoke-DataverseApi -Method -EnvironmentUrl -AccessToken -Path` signatures are in
`provisioning/common/provisioning-common.ps1`. Note `-Auth` takes an **object** with `TenantId`,
`AppId` and `CertThumbprint` — not three separate string parameters. The environment URL comes from
`provisioning/deploymentSettings/dev-schema-settings.json`, never from a literal in a script
(`C-TECH-047`).
