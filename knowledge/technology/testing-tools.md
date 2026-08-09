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
