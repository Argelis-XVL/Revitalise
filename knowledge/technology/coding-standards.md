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

### The `-f` / `+` precedence trap (`IMP-0142`)

`-f` (the format operator) binds **tighter** than `+`. `Write-Output ("a {0} " -f $x) + "b"`
does **not** concatenate the two strings — it sends `"a {0} "` to the pipeline unformatted
(the `-f` on the SECOND line applies to `"b"` alone, which has no placeholder to fill) and then
evaluates a bare `+` against the cmdlet's return value, which prints as its own line. The
symptom is a message split across two lines with a literal `+` between them and an
unsubstituted `{0}` where a value belonged — exactly the shape `Invoke-Tests.ps1`'s
FAILED-coverage branch printed until this was found (`IMP-0134`'s own first draft reproduced
the identical break before it was caught by running the script, not by reading the diff).

```powershell
# WRONG — "a {0} " ships to the pipeline unformatted, "+" prints on its own line
Write-Output ("a {0} " -f $x) +
             "b"

# RIGHT — concatenate the template FIRST, in one set of parens, then format the whole thing
Write-Output (("a {0} " + "b") -f $x)
```

Never trust this by inspection — run the line and read the actual output. A `Should -Match`
assertion on a keyword substring (e.g. `'RESULT: FAILED'`) still passes with a broken `{0}`
beside it; nothing short of reading the printed text catches this.

## TypeScript / React (Power Apps Code Apps)

- **TypeScript strict mode** on for all Code Apps (`"strict": true` in `tsconfig.json`)
- No `any` types — use `unknown` with type guards
- ESLint + Prettier enforced; config in `src/code-apps/<slug>/.eslintrc.json`
- One component per file; filename matches the exported component name (PascalCase)
- React Query for all Dataverse data fetching — no raw `fetch` calls in components
- Fluent UI v9 for Platform-aligned components; CSS Modules or Tailwind for layout/custom styles (set once per project)
- No `console.log` in production code — use the error logging flow instead
- All Dataverse calls wrapped in try/catch with user-visible error feedback

### Matching a Dataverse column name in source text — use a whole-identifier boundary

**Any check that looks for a forbidden column name inside source text matches on identifier
boundaries, never with `String.includes` or a bare substring search.** In this solution a secured
column's name is a strict *prefix* of the safe column that redacts it — the suffix is appended
with no separator — so a substring test reports every safe column as its own secured source.

```ts
// WRONG — rev_carenarrative is a substring of rev_carenarrativeredacted
content.includes(column)

// RIGHT — the same boundary the official gate uses
new RegExp(`(?<![A-Za-z0-9_])${column}(?![A-Za-z0-9_])`).test(content)
```

**`scripts/verify-code-app-column-bindings.py` is the reference implementation.** It was given
this boundary in improvement review 19 (`C-TECH-069`) for exactly this reason. If you are writing
a local Vitest or Pester duplicate of one of its checks, read the regex out of that file rather
than re-deriving it — `IMP-0321` is the drift: `schema.test.ts` carried an older substring copy
and failed three safe `…redacted` bindings that the real gate passed, so the local suite
contradicted the build gate on correct code. Nothing cross-checks a local duplicate against the
official gate, which is the second reason to name the source instead of copying the idea.

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

### Which number, and who decides it — settled 2026-08-21 (`IMP-0132`)

Two things were wrong here, and both are now fixed in the build rather than in this paragraph.

**The metric.** This table says **line** coverage. Pester's own `CoveragePercent` is
command/instruction based, and `Invoke-Tests.ps1` enforced that one. On the 2026-08-21 report
the two differ — 70.00% by line, 67.78% by instruction — so the document and the runner had
been disagreeing about which quantity `C-TECH-014` governs. The build now enforces the **line**
counters, because that is what this table declares. `scripts/verify-coverage-threshold.py` reads
them out of the JaCoCo report.

**Where the decision lives.** `unit-tests` used to carry the test-count gate and the coverage
gate in one step, and a manifest holds one result per step — so on 2026-08-20 three manifests
recorded the test counts, omitted the percentage, and coverage fell from 89.13% to 67.78%
without a single artifact saying so. Coverage is now the separate `coverage-threshold` step, and
`80` appears in that step and nowhere else; `unit-tests` passes `-CoverageThreshold 0`, meaning
*measure and report, do not decide*.

### What is excluded, and what it costs to be excluded

`config/coverage-exclusions.json` enumerates the files that are measured but not counted. There
is exactly one category: **scripts that are themselves verification harness.**
`verify-test-data.ps1` reporting PASS over wrong data is the `gate-cannot-fail` class, and a
demonstration that it reports FAIL on a real discrepancy is a stronger guarantee for that file
than 80% of its lines being executed against a mock.

The exclusion is priced, not free. Every entry carries a `reason` **and** a
`proven_able_to_fail` naming the evidence that substitutes for the coverage; an entry with
neither that nor a dated `deferred_to`/`expires` fails the gate, an expired entry fails the
gate, and the list carries its own `_max_entries` cap so the carve-out cannot become the norm.
Four entries stand today, all four the test-data harness added on 2026-08-20.

Note the boundary this reveals: the coverage **scope** is `**/*.ps1` and Pester's
`RecursePaths` also measures `.psm1`. `test-data-common.psm1` is excluded on that basis alone —
aligning the measurement with the declared scope, not narrowing either. If this table is ever
widened to name `.psm1`, delete that entry rather than re-dating it.

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

### The decision `IMP-0005`/`IMP-0039` deferred four times, now made

Class `test-coupled-to-absolute-counts`. `IMP-0005` (2026-08-16) recorded three schema-count
assertions going stale in one session; `IMP-0039` (2026-08-18) recorded ELEVEN more breaking
from one legitimate table addition, none of them a real defect, and said the decision was
"now due" on the second instance. Both were deferred pending this write-up rather than
silently patched instance by instance. This is that write-up — the discrimination rule, not a
retrofit of the ~45 sites the 2026-08-20 review inventoried (that is scoped implementation
work for whoever next touches `src/tests/`, not something to rewrite wholesale behind an
improvement review).

**The discrimination rule.** A `.Count | Should -Be <n>` (or an `-Exactly <n>` on `Should
-Invoke`) is one of two things, and they get opposite treatment:

| Kind | Example | Treatment |
|---|---|---|
| **A total this project's own solution source declares** | "51 secured columns", "17 global option sets", "88 attributes on `rev_application`", "43 REV Admin privileges" | **Fragile — derive it, do not hardcode it.** It changes on every legitimate schema addition, and a stale literal reads as a regression when it is a maintenance cost. |
| **A fixture's own cardinality** | "this mocked payload has 3 rows", "the fake API was called exactly 2 times in this scenario", "the known-bad fixture declares 1 secured column" | **Stable — leave it as a literal.** It describes a value THIS test authored, not the real schema, and does not move when the solution grows. |

The tell: does the number describe something under `src/solutions/RevitaliseGrantAutomation/`
(fragile), or something under `src/tests/fixtures/` or a mock's own setup (stable)? A `.Count`
against `Get-RevEntityLogicalNames`, `Entities/*/Entity.xml`, `FieldSecurityProfiles.xml` or a
role XML is column 1. A `.Count` against a scriptblock's own literal test data, or
`Get-FakeDataverseCalls` in one specific `It`, is column 2.

**When column 1 cannot be avoided**, prefer, in order:
1. **An invariant that needs no count at all** — `(Compare-Object -ReferenceObject $fromSchema
   -DifferenceObject $fromProfile) | Should -BeNullOrEmpty`, the pattern already in
   `EnsureSchema.Tests.ps1`'s secured-column cross-reference. This is what closed the class for
   THAT assertion: the invariant is the same before and after a column is added, so the test
   does not move.
2. **A count derived from the same source the script reads**, e.g. `(Get-RevEntityLogicalNames
   | ForEach-Object { (Get-RevEntityDefinition ...).Attributes.Count } | Measure-Object -Sum)`
   instead of a literal `88`. Fragile counts kept as literals — because rule 1 or 2 was not
   reachable for that specific assertion — carry a comment stating that plainly (the existing
   convention: *"count-coupled by design and breaks on every legitimate schema addition
   (IMP-0005) — a failure here is a stale number until proven otherwise"*), so the next person
   updating it does not mistake a stale total for a regression.

**What this is not.** Not a mandate to touch all ~45 sites now — most are column 2 and must
stay literal. Not a ban on ever asserting a total: `EnsureSchema.Tests.ps1` keeps
`$securedColumns.Count | Should -Be 51` DELIBERATELY, alongside the count-free
`Compare-Object`, as an extra sanity check with the fragility named in its own comment. The
decision this closes is the RULE for telling the two kinds apart — applying it is ordinary
maintenance the next time each site is touched, not a one-off migration.

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
