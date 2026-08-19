# Coding Standards — Power Platform

> 📝 Replace `[prefix]` and `[PREFIX]` throughout with your project's publisher prefix.
> Set the prefix in `knowledge/technology/stack-overview.md` → Publisher Convention.

## Naming

| Element | Convention | Example |
|---|---|---|
| Solution | `[PREFIX]_<Domain>` | `PROJ_CaseManagement`, `HR_Onboarding` |
| Table schema name | `[prefix]_<entityname>` | `[prefix]_case`, `[prefix]_party` |
| Column schema name | `[prefix]_<columnname>` | `[prefix]_status`, `[prefix]_assignedto` |
| Flow name | `[PREFIX] <Domain> - <Action> - <Trigger>` | `[PREFIX] Cases - Escalate - On Status Change` |
| Web resource | `[prefix]_/<feature>/<filename>` | `[prefix]_/cases/statusValidation.js` |
| Code App folder | `<app-slug>` (kebab-case) | `case-portal`, `onboarding-app` |
| Code App solution component | `[PREFIX]_<AppSlug>` | `PROJ_CasePortal` |
| Code App env var | `VITE_<SCREAMING_SNAKE>` | `VITE_DATAVERSE_URL`, `VITE_API_BASE` |
| Environment variable | `[prefix]_<SettingName>` (PascalCase after prefix) | `[prefix]_ApiBaseUrl`, `[prefix]_NotifyChannel` |
| Connection reference | `[prefix]_Shared<Service>` | `[prefix]_SharedDataverse`, `[prefix]_SharedEmail` |
| Cloud flow action names | Descriptive verb-noun | "Get Active Cases", "Update Record Status" |

## Solution Layering

- One solution per functional domain
- Shared base components (lookup tables, base security roles) in `[PREFIX]_Base` solution
- Never create cross-solution dependencies at runtime — only `[PREFIX]_Base` may be a dependency

## Power Automate

- All action names in English, verb-noun format, no abbreviations
- Every flow has a description explaining its purpose, trigger, and owner team
- **Every `description` field — flow, trigger, action, parameter, schema property — is capped
  at 256 characters** (`C-TECH-049`). This is a platform save limit, not a style preference:
  `pac solution pack` and `pac solution import` both succeed past it and the flow then cannot
  be saved by a maker, naming no field. Keep the description to the essential fact plus its
  FR/NFR/ADR citation; put the full reasoning in a companion `Workflows/<FlowName>.notes.md`
  keyed by JSON path, so nothing is lost. Enforced by the `field-length-limits`
  build step
- Use **variables** at the top of the flow for all values referenced more than once
- Compose actions for data transformations instead of inline expressions where readability suffers
- No plain-text passwords or secrets in flow inputs — use environment variables or Key Vault

## PowerShell / Scripts — Cross-Platform (C-TECH-054)

**The CI runner is Linux. A script that has only ever run on the author's machine is unproven
on the machine that will actually run it.** This is not hypothetical: a provisioning helper
here used `Get-ChildItem -Path 'Cert:\...'` to load a certificate. The `Cert:` PSDrive is
Windows-only, so every provisioning script would have failed on the runner. It was found only
because provisioning was finally executed for real, on a Mac — after months in the repo.

| Don't | Do |
|---|---|
| `Get-ChildItem Cert:\CurrentUser\My` | `[System.Security.Cryptography.X509Certificates.X509Store]` |
| `"$dir\$file"`, hardcoded `\` | `Join-Path`, `[IO.Path]::Combine` |
| `Get-CimInstance`, `Get-WmiObject`, registry access | Cross-platform .NET APIs, or guard + document |
| `$env:USERPROFILE`, `$env:TEMP` | `$HOME`, `[IO.Path]::GetTempPath()` |
| Case-insensitive path assumptions | Exact case — Linux filesystems are case-sensitive |

- Scripts are executed by the test suite **on the CI runner's OS** in CI, not only locally
- Where a platform-specific API is genuinely unavoidable, guard it, state the supported OS in
  the script header, and confirm the pipeline never runs it elsewhere
- The same rule applies to line endings, `pwsh` vs `powershell`, and any tool assumed on PATH

## TypeScript / React (Power Apps Code Apps)

- **TypeScript strict mode** on for all Code Apps (`"strict": true` in `tsconfig.json`)
- No `any` types — use `unknown` with type guards
- ESLint + Prettier enforced; config in `src/code-apps/<slug>/.eslintrc.json`
- One component per file; filename matches the exported component name (PascalCase)
- React Query for all Dataverse data fetching — no raw `fetch` calls in components
- Fluent UI v9 for Platform-aligned components; CSS Modules or Tailwind for layout/custom styles (set once per project)
- No `console.log` in production code — use the error logging flow instead
- All Dataverse calls wrapped in try/catch with user-visible error feedback

## JavaScript Web Resources (MDA only)

- ESLint enforced; config in `src/.eslintrc.json`
- No `console.log` in production code
- All Xrm API calls wrapped in try/catch with user-visible error handling
- Functions documented with JSDoc headers
- One web resource per feature concern — no monolithic files
- Prefer a Code App over a complex JS web resource for any new UX

## Business Rules

- Use descriptive condition and action names
- Document the FR ID this rule implements in the description field
- Rules scoped to **Entity** scope only (not All Forms) unless cross-form enforcement is required

## Test Coverage

> **Added 2026-08-12 to close test-agent defect D-005 / C-TECH-014 (HARD).** C-TECH-014 says
> "unit test coverage must meet the threshold in `coding-standards.md`" and this file defined
> none, so the constraint could not be satisfied as written. This section is the threshold.
>
> ⚠ **This is a Tech Lead decision taken by the development-agent because no Tech Lead was
> available in the session that needed it.** It is documented rather than assumed, and the
> reviewer should confirm or override it — particularly the number. It is not settled by the
> act of having been written down.

### The threshold

| Layer | Scope measured | Threshold | Tool |
|---|---|---|---|
| **Imperative code — PowerShell** | `provisioning/{common,entra,dataverse}/**/*.ps1` | **80% line coverage**, build-failing | Pester `-CodeCoverage`, JaCoCo output |
| **Imperative code — TypeScript / React (Code Apps)** | `src/code-apps/<slug>/src/**` | **80%** statements and lines, build-failing | Vitest `--coverage` |
| **Declarative artefacts** — Dataverse XML, cloud-flow JSON, option sets, roles | not coverage-measurable | **not applicable — replaced by asserted invariants** (below) | Pester static suites under `src/tests/solutions/` |

Run it: `pwsh -NoProfile -File src/tests/Invoke-Tests.ps1 -CodeCoverage -CoverageThreshold 80`.
The build runs the same command (`config/<slug>-build.yml` → step `unit-tests`), so the number
the build enforces is the number a developer sees locally.

### Why coverage is scoped, not global

A percentage over the whole repository would be meaningless in both directions here. Most of
what this project ships is **declarative**: an `Entity.xml` and a cloud-flow `.json` have no
executable lines, cannot be instrumented, and cannot run at all without a live Dataverse
environment. Including them would drive the number with files that can never be "covered",
and the way to raise it would be to delete configuration rather than to test anything.

So coverage is measured over the code that **is** imperative and **can** be executed
off-platform, and the declarative artefacts get a different, stated obligation instead.

### Declarative artefacts: asserted invariants instead of a percentage

For every declarative artefact whose correctness rests on a **relationship** — arithmetic
between seeded configuration values, a structural property a requirement depends on, a
cross-file coupling — that relationship must have a **re-runnable asserted test**, not a
paragraph in a document and not a manual re-check each release. The obligation is
completeness against an enumerated list (recorded in the feature's Dev Summary), not a
percentage. Examples from this project: `FeelingScaleInversion` satisfying `key + value = 10`
for all eleven keys; `MaxCircumstanceScore` reconciling to the maximum the flow can produce;
FR-016's exclusion of every secured column from the scoring flow, derived from `IsSecured=1`
rather than from a hand-kept list.

A test that re-derives a property from the source beats a test that restates a number.

### Why 80% for the PowerShell, and not 90 or 60

Judgement call, stated so it can be argued with:

- **The measured code is the most privileged code in the release.** The provisioning scripts
  create Entra objects, bind security roles and configure audit retention against production.
  They are also ordinary PowerShell with ordinary branching, so there is no technical excuse
  for leaving them untested — test-agent was right to call them "the least-tested and most
  privileged code in the release".
- **Well above 80% is achievable here**, and is the actual position: 92.6% at the time of
  writing, with only `ensure-document-locations.ps1` (a Phase 2 script no Phase 1 pipeline
  step invokes) uncovered. So 80% is a floor with real headroom rather than an aspiration.
- **The last few percent are mostly `catch` blocks whose only realistic trigger is a live API
  failure.** Reaching them means asserting that a mocked HTTP 500 produces a `FAILED` line,
  which is worth doing for the interesting paths and is busy-work for the rest. A threshold
  set at the current actual would fail the build on a refactor that added ten lines of error
  handling — which teaches people to game the metric.
- **This is a small charity automation with one developer/consultant.** A threshold that
  makes the build fail for reasons nobody believes in gets suppressed, and then the gate is
  worth nothing. 80% is high enough that a materially untested new script breaks the build,
  and loose enough to survive a normal week.

**Floor, not target.** 80% is the point below which the build fails. It is not the standard
to aim for, and a pull request that drops coverage from 92% to 81% should be questioned in
review even though the gate passes.

### What a coverage number does not mean

Coverage says a line executed, not that its behaviour is right. The assertions are what
carry the value: the provisioning suites assert the **request** each script sends (a team
created with `teamtype 2`, a role resolved by name rather than by GUID, `rev_effectivefrom`
stamped on create only), because a provisioning defect is almost never mishandling the answer
— it is asking for the wrong thing.

**Nothing in this section covers runtime behaviour against a live Dataverse environment.**
Flow execution, column-security enforcement and audit-record shape are integration concerns
and remain untestable until an environment exists. Coverage of the provisioning scripts must
not be read as coverage of the solution.

## Version Control

- Branch naming: `feature/<slug>`, `fix/<slug>`, `release/<version>`
- Commit messages: `[<ticket-id>] <imperative verb> <what>` e.g. `[PROJ-142] Add status column to Case table`
- Never commit `.zip` files — only unpacked source
- `build/exports/` and `build/artifacts/` are gitignored

## What Never Goes in Source Control

- `.zip` solution files (build outputs)
- Client secrets, passwords, API keys
- Personal connection configurations
- Environment-specific URLs hardcoded in flows
