# Dev Summary Document — Trustee Portal Visual Refresh and Round-Statistics Landing Screen

**Feature Slug:** `trustee-portal-visual-refresh`
**TAD Reference:** `docs/architecture/trustee-portal-visual-refresh-architecture.md` (APPROVED, Revision 2)
**Parent Dev Summary:** `docs/development/revitalise-grant-automation-dev-summary.md` — unchanged, not reproduced.
**Date:** 2026-08-25 · **revision 0.2 (`rev_roundfinance` Code App data source registered, A-LAND-1 closed)** 2026-08-26
· **revision 0.3 (D-10 fixed — `Respond_error` no longer fires on the success path)** 2026-08-26
**Status:** DRAFT
**WBS:** `6.1`, `6.3`, `6.5` (accepted, `contract/wbs.json`), `6.9` (created by `contract/change-orders/CO-001.md`,
resized by `CO-001-A1.md`; **not yet in `contract/wbs.json`** — TAD §0.3, unresolved by this dispatch, a
`pm-agent`/`commercial-agent` reconciliation, not a build blocker per `C-COM-002`). **This revision's own two
fixes carry `wbs:6.9`** — the WBS-scope disagreement across this document, the build manifest and the
dispatch handoff (test report defect D-08) is not resolved here; it stays `pm-agent`/`commercial-agent`'s to
reconcile, and nothing below changes any figure toward that reconciliation.

---

## 0. The TAD's sequencing instruction, and how this dispatch answered it

The dispatching handoff asked one thing first, before the rest of `wbs:6.9`: **can this code app actually
call a solution-aware instant flow the way ADR-030 assumes?** This is answered as far as a session with no
interactive Power Automate designer access can answer it — see §10 row A-FLOW-01 and §11. The short version:
the CLI mechanism is confirmed live; the flow itself is authored, packs cleanly, and passes the hosted
Solution Checker with zero findings; it has not yet been imported into DEV or turned on, because that is a
full unmanaged solution import (this project's real DEV deploy mechanism) and doing it directly, outside
build-agent/pipeline-agent's normal gates, was judged a disproportionate risk to the schema this same session
had just verified live by a different mechanism. **Nothing here indicates ADR-025's fallback is needed** —
every check that has run has passed.

### 0.1 This revision — closing test-agent's two P2 defects (reviewer directive, 2026-08-25, not an open decision)

Test-agent's report (`docs/tests/trustee-portal-visual-refresh-test-report.md`, Status: FAIL) was **APPROVED
by the reviewer with the FAIL verdict standing** — the reviewer chose to fix defects D-01/D-02 rather than
accept them, and gave two explicit, direct instructions rather than open questions. Both are closed in this
revision:

1. **D-02 / TC-SEC-06 (the flow's missing failure path, TAD §5.1's "On failure" row) — fixed** by a scoped
   `automation-agent` dispatch. §4, §10 row A-FLOW-05, §11.
2. **D-01 (the build manifest's false "LandingPage/charts UI" claim) — now true**, not just corrected in the
   manifest: the landing screen (`FR-056`–`FR-064`, `NFR-026`–`028`) is built by a scoped `frontend-agent`
   dispatch, against the flow's defined response contract, with no live call (the flow is still V2 — see §11).
   §1, §2, §7, §10 rows A-LAND-1..4.

Neither sub-dispatch touched `ApplicationDetailPage.tsx`'s FR-035 wiring, `CasePanels.tsx`, `theme.ts` or the
schema/role work from the prior pass in this same feature — those are unchanged and not reproduced here.

### 0.2 This revision — `rev_roundfinance` Code App data source registered; A-LAND-1 closed (2026-08-26)

Improvement review 29 (`docs/improvements/2026-08-25-improvement-review-3.md`) applied `IMP-0329` as a HARD
build step, `scripts/verify-code-app-data-sources.py`, now wired into `config/revitalise-grant-automation-build.yml`
ahead of typecheck/lint/tests/build. Running it against `src/code-apps/trustee-review-portal` found exactly
the gap `IMP-0329`/A-LAND-1 predicted: `READ_SERVICES` registers `rev_roundfinances` for reading, and it was
absent from the generated `.power/schemas/appschemas/dataSourcesInfo.ts` the SDK actually resolves against.

**Fixed the standard way** — `pa app add data-source --connector dataverse --table rev_roundfinance -u
https://orge2b20d13.crm17.dynamics.com -c f31ddadfbe874e50a34054df668e75cf --non-interactive`, run from
`src/code-apps/trustee-review-portal` against the same DEV org/connection the app's four existing per-table
sources were added against (§9 of the parent Dev Summary, 2026-08-22). Succeeded: `power.config.json` gained
a `roundfinances` entry, `dataSourcesInfo.ts` gained a `"rev_roundfinances"` entry
(`dataSourceType: "Dataverse"`, `primaryKey: "rev_roundfinanceid"` — matching the live metadata `IMP-0316`
already confirmed), and `src/generated/{models,services}/Rev_roundfinances*` are now real and committed.
`scripts/verify-code-app-data-sources.py src/code-apps/trustee-review-portal` now reports **OK — 5
registration(s), 5 Dataverse source(s) declared** (was 5/4, 1 violation).

**A-LAND-1 closed at E1**, not merely unfalsified: the generated `Rev_roundfinancesService.getAll`/`.get`
are the identical `getClient(dataSourcesInfo).retrieve…Async("rev_roundfinances", …)` calls the hand-written
stand-in already made — compared directly, side by side, not inferred. `client.ts`'s `READ_SERVICES` entry
is deliberately **not** swapped to the generated class in this dispatch: both paths now resolve identically
for a real signed-in user once the entity set is declared, and the swap-plus-deletion of
`roundFinanceReadService.ts` is a separate, one-file cleanup the reviewer can take independently (comments
updated in both files to say so precisely, rather than left stale per `IMP-0330`'s class).

**Scope check.** `wbs:6.9` (created by `contract/change-orders/CO-001.md`, resized by `CO-001-A1.md`; still
not in `contract/wbs.json` — unresolved by this dispatch, unchanged from the header note above) already
carries the round-finance/landing-page work this fix completes a gap in — this is additive to that existing
build, not new billable scope: no code-app feature, table or screen was added, only a provisioning step the
TAD's own §5.4 instruction (quoted verbatim in `IMP-0329`) already named as required. No change-order
routing needed (`C-COM-002`); confirmed rather than assumed, since `wbs:6.9`'s own acceptance status is
itself an open pm-agent/commercial-agent reconciliation this dispatch does not touch either way.

**Hours proposal — addendum for `commercial-agent` behind `APPROVE TIMESHEET`.** No figure from
`contract/wbs.json` or `contract/service-agreement.json` is restated here (`C-COM-008`); this is this
dispatch's own proposed actual, not a contracted estimate:

| WBS | Proposed actual | Evidence |
|---|---|---|
| `6.9` | 0.3 h | One diagnostic gate run, one `pa app add data-source` call against DEV, re-verification (`verify-code-app-data-sources.py`, `verify-assumption-markers.py`, `verify-build-config.py`, `verify-pipeline-config.py`, full code-app typecheck/lint/372-test suite), and Dev Summary §0.2/§1/§2/§7/§8/§9/§10/§11/Findings/Checklist updates |

Additive to `wbs:6.9`'s existing build, not new scope — a proposal for `commercial-agent` to confirm, not a
booking.

**Re-verified nothing else broke:** `npm run typecheck`, `npm run lint`, `npm run coverage` in
`src/code-apps/trustee-review-portal` — all clean, **372/372 tests across 21 files, 96.27% statement/line
coverage**, identical to the figures already recorded in §9/§11 below (this fix touched no test-observable
behaviour — only comments and the generated/config files the gate itself checks).
`python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml` → PASS, 93 steps
(re-run after annotating the now-partially-done manual post-deploy step at line ~794 — the data-source half
is done, the `pa app add flow` half still awaits the flow going live).

### 0.3 This revision — closing test-agent's P1 defect D-10 (reviewer directive, 2026-08-26, not an open decision)

Test-agent's re-test (`docs/tests/trustee-portal-visual-refresh-test-report-v2.md`, Status: FAIL) found that
the D-02 fix (§0.1) itself introduced a P1: `Respond_error`'s `runAfter` accepted `"Skipped"` on its
predecessor `Alert_on_failure`. On a **successful** run the whole failure chain is skipped by design, so
`Respond_error` fired anyway — after `Respond_ok` (or one of the other three business-outcome `Respond_*`
actions) had already replied. A four-`Response` flow therefore responded twice on its happy path. The
reviewer gave one explicit, direct instruction rather than an open question: remove `"Skipped"`, matching
`REVIntakeWordPressToDataverse`'s own `Respond_500_intake_failed` pattern exactly — the only other
multi-`Response` flow in this solution with the identical `Alert_on_failure` predecessor, which already
omits `Skipped` for exactly this reason.

**The fix, verbatim.** `Respond_error`'s `runAfter` in
[`Workflows/REVPortalRoundStatistics-…json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L304)
now reads `Alert_on_failure: ["Succeeded","Failed","TimedOut"]` — `"Skipped"` removed, nothing else
changed to the flow's behaviour. One token, no new action, no new Solution.xml entry.

**A second gate caught a second, self-inflicted defect before this went anywhere.** The action's
`description` was first extended in place with the full D-10 fix rationale, which pushed it to 436
characters — 180 over Power Automate's 256-char hard save limit (`C-TECH-060`,
[`verify-field-length-limits.py`](../../scripts/verify-field-length-limits.py)). Caught by re-running
that gate before presenting this dispatch, not by inspection. Fixed the way this file's own
`.notes.md` convention requires: the JSON `description` was condensed back to one citation line
(`…D-10 fix (2026-08-26): Skipped removed from runAfter - see notes.md.`, 217 chars) and the full
root-cause/fix/residual account moved to
[`REVPortalRoundStatistics-….notes.md`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.notes.md),
keyed by `/properties/definition/actions/Respond_error/description` — the same pattern this file
already uses for A-FLOW-01 through A-FLOW-05. Re-run after the fix: `field-length-limits: OK — 183
flow description(s) within 256 chars`.

**Root cause, as test-agent's report traced it (§4 of the v2 report, D-02 section).** The notes cited
`REVScoringDailySummary` as this shape's source, but that flow has no `Respond_error` at all — it is
scheduled, with no caller. The wiring actually copied was `REVOpsFailureAlert`'s
`Respond_to_calling_flow`, which is safe with `Skipped` in its `runAfter` only because that flow has
**exactly one** `Response` action total — nothing else to collide with. `REVPortalRoundStatistics` has
**four**. Copying an "always respond regardless of status" shape without checking how many terminal
`Response` actions the source flow has reproduces the shape without the precondition that makes it safe.

**Verification, this dispatch:**

- The edited JSON still parses cleanly (`python3 -m json.load` equivalent, run directly against the file).
- `python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation/Workflows` →
  **OK — 5 flow definition(s)** clean (no `select()`/`filter()`, no alternate-key Row ID, no nested `item`
  on an `UpdateRecord`, no nested `InitializeVariable`, every Dataverse-reading flow's failure branch
  reaches the error-recording path). This check proves the failure branch **exists**, not that it is
  correctly gated (`IMP-0109`'s own caveat) — it does not by itself prove D-10 is closed; that is a
  property of the specific `runAfter` edit, verified by direct inspection above, not by this gate.
- `grep -n "Skipped" Workflows/REVPortalRoundStatistics-…json` → the only remaining occurrence is the
  descriptive text inside `Respond_error`'s own `description`, not a `runAfter` condition.
- `python3 scripts/verify-field-length-limits.py src/solutions/RevitaliseGrantAutomation` → **OK — 183
  flow description(s) within 256 chars** (re-run after condensing `Respond_error`'s `description`, see
  the callout above; the first attempt at that same edit failed this gate at 436 chars).
- `python3 scripts/verify-assumption-markers.py` and `verify-assumption-register.py` — both **PASS**,
  re-run after the A-FLOW-05 correction below; the marker string `A-FLOW-05` survives the condensed
  description, so the row's `Where` citation is still satisfied.
- `pac solution pack`/`pac solution check` were **not** re-run by this dispatch — no artifact type,
  component count or packaged shape changed (one string value inside one existing action), so neither
  tool's prior clean result (§8, §9, §11) is stale. `--expect-flows` stays 5; `verify-solution-root-
  components.py` stays 66.

**A-FLOW-05 corrected, not merely left OPEN (§10).** The row previously asked only whether `Respond_error`
"will actually execute and return a body" — the one-sided framing test-agent named as D-10's real cause
(the v2 report, §4, "the assumption register frames this risk in only one direction"). The claim is now
stated in both directions and the negative half is closed **statically, deterministically** (the same
basis on which test-agent rated the original defect a certainty, not a guess): `Respond_error`'s `runAfter`
no longer accepts `Skipped`, so it cannot fire when `Alert_on_failure` is skipped by design — i.e., on any
successful run. The positive half (does it fire, and does the caller receive its body, on a genuine
failure) remains OPEN and unverifiable without a live environment, unchanged from before.

**What is deliberately not touched.** Test-agent's report separately noted, as a residual worth checking
rather than a defect it raised (no defect id assigned): `Find_the_failed_action`'s own `runAfter` on
`Compute_statistics` accepts only `["Failed","TimedOut"]`, not `Skipped` — so if `Compute_statistics`
itself were ever skipped (only possible if `Capture_computedOn` or `Initialise_failure_detail`, both
earlier top-level actions with trivial, near-failure-proof bodies, themselves failed or were skipped),
no response of any kind would reach the caller. This is structurally identical to
`REVIntakeWordPressToDataverse`'s own accepted precedent shape (the flow the reviewer named as the correct
pattern to copy) and is not part of this dispatch's scope — the reviewer's instruction was the one-token
`Skipped` removal, "no design decision involved." Left here as an explicit, named residual rather than
silently carried, per `IMP-0330`'s class (a limitation known and not recorded is worse than one recorded).

**Improvement log.** Test-agent already logged this defect and its two related process gaps in full —
`IMP-0345` (the defect itself: root cause, gate proposal), `IMP-0346` (no regression test guarded the
fixed D-02 behaviour), `IMP-0347` (the one-sided assumption-register framing, matching the A-FLOW-05
correction above) — all `status: NEW`, unprocessed. This dispatch's own fix matches `IMP-0345`'s predicted
lesson exactly and surfaces nothing new; **0 entries appended** by this revision (would duplicate an
already-logged finding, which `skills/how-to-log-an-improvement.md` §1 explicitly excludes). Neither
`IMP-0345`'s proposed build-gate nor `IMP-0346`'s proposed regression test was implemented here: both are
`proposed_change` entries awaiting `improvement-agent`/`APPROVE IMPROVEMENTS`, not this dispatch's to apply.

**Scope check.** `wbs:6.9` — same task this flow's whole D-02 fix already carries (§0.1 header); a
one-token correction to already-in-scope flow content, not new scope. No change-order routing needed
(`C-COM-002`).

**Hours proposal — addendum for `commercial-agent` behind `APPROVE TIMESHEET`.** No figure from
`contract/wbs.json` or `contract/service-agreement.json` is restated here (`C-COM-008`):

| WBS | Proposed actual | Evidence |
|---|---|---|
| `6.9` | 0.2 h | One flow-JSON edit (one token removed, one description extended), `verify-flow-definition-language.py` re-run, JSON-parse check, `grep` confirmation, A-FLOW-05 register correction, and this Dev Summary's §0.3/§2/§4/§7/§9/§10/§11/Findings/Checklist updates |

Additive to `wbs:6.9`'s existing build, not new scope — a proposal for `commercial-agent` to confirm, not
a booking.

---

## 1. Implementation Summary

Four pieces, now all built at source level; only live-environment verification remains open:

1. **Schema (WBS 6.3, 6.9) — built and V4-verified live in DEV, an earlier session.** The new `rev_roundfinance`
   table (13 attributes, one alternate key), the three `rev_application` `…redacted` care-support columns
   (WBS 6.3, ADR-027 amended), and the associated security-role privilege grants across all three roles.
   Unchanged by this revision.
2. **The flow (WBS 6.9) — authored as solution source, packed, and Solution-Checker-clean; not yet live.**
   `REV | Portal | Round Statistics`, computing only `applicationsReceived` in this first version; every
   other §3.3 metric responds `null`, declared as such, not silently omitted. **This revision closes D-02**:
   the flow now catches a genuine action failure (either `List_the_open_round` or `List_applications_in_round`
   failing), calls `REV | Ops | Failure Alert` (writes `rev_errorlog`, alerts the process owner), and always
   responds with a JSON body — `status: "error"` — so the caller never receives a bare, unhandled platform
   failure. §4, §10 A-FLOW-05, §11.
3. **The UI — all three slices now built.** ADR-026's brand theme (WBS 6.1) and FR-035's redacted-column
   wiring on `ApplicationDetailPage.tsx` (WBS 6.3) were already complete from earlier dispatches on this
   feature and are unchanged. **This revision closes D-01**: `LandingPage.tsx` and the FR-057–FR-063 content
   (WBS 6.9, `wbs:6.1`'s navigation-shell half) are now built — against the flow's defined §3.3 response
   contract and `rev_roundfinance`'s confirmed-live schema, with no live flow call yet (the flow itself is
   not live — see §7, §10 A-FLOW-01/05, A-LAND-2). **`rev_roundfinance`'s own Code App data source is now
   registered** (§0.2, 2026-08-26) — `pa app add data-source` has been run and `dataSourcesInfo.ts` carries
   a real `"rev_roundfinances"` entry; A-LAND-1 is CLOSED. Every FR-059–FR-062 metric still renders as
   **absent**, not zero and not an error, because the flow's current first version still emits `null` for
   all of them — the screen is built against the *whole* contract so nothing further changes when the
   flow's next version starts populating them.

## 2. Components Changed / Created

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| `Entities/rev_roundfinance/Entity.xml` | Dataverse entity | New. 13 attributes, alternate key on `rev_name`. | FR-057, FR-058, FR-063 |
| `Entities/rev_application/Entity.xml` | Dataverse attributes | +3 `…redacted` columns | FR-035 |
| `Other/Solution.xml` | Solution manifest | +1 `RootComponent type="1"` (rev_roundfinance), +1 `RootComponent type="29"` (the new flow) | — |
| `Roles/REV Trustee/REV Trustee.xml` | Security role | + `prvReadrev_roundfinance` (Global), + `prvReadWorkflow` (Global, A-FLOW-02) | FR-057, FR-058, FR-063 |
| `Roles/REV Service Automation/REV Service Automation.xml` | Security role | + `prvReadrev_roundfinance` (Global, read-only) | FR-057–062 |
| `Roles/REV Admin/REV Admin.xml` | Security role | + Create/Read/Write on `rev_roundfinance` | FR-063 |
| `Workflows/REVPortalRoundStatistics-…json` (+`.data.xml`, `.notes.md`) | Cloud flow | New. Power Apps trigger, no inputs, one `List rows` + `Respond` | FR-057, FR-058 |
| `provisioning/dataverse/ensure-schema-helpers.psm1` | Provisioning helper | `rev_roundfinance` added to `Get-RevEntityLogicalNames` | — |
| `provisioning/deploymentSettings/{dev-auditing,test,prd}-settings.json` | Settings | `rev_roundfinance` added to `auditedTables` | C-TECH-064 |
| `docs/architecture/revitalise-grant-automation-architecture.md` | Parent TAD | §3.1 gained the new table's block and the 3 redacted columns' rows (per delta TAD §3.0's ordering instruction) | — |
| `src/code-apps/trustee-review-portal/src/theme.ts` (new), `main.tsx`, `styles/app.module.css` | Code App UI | ADR-026 brand theme, full-width shell | NFR-026 |
| `src/code-apps/trustee-review-portal/src/pages/ApplicationDetailPage.tsx`, `src/components/CasePanels.tsx`, `src/domain/visibility.ts`, `src/dataverse/{types,schema,repository}.ts` | Code App UI | FR-035 redacted care-support panel — `CareSupportPanel`, three-state gating (withheld / released-empty / released) | FR-035 |
| `src/tests/provisioning/EnsureSchema.Tests.ps1` | Test | Generalised two hardcoded-count fixtures (see §Findings) | — |
| `src/tests/build/BuildGates.Tests.ps1`, `config/revitalise-grant-automation-build.yml` | Test / build config | `--expect-flows` 4 → 5 | — |
| `config/revitalise-grant-automation-pipeline.yml` | Pipeline config | 11 new `dev.environment_prerequisites` entries (see §5) | — |

### This revision (D-01/D-02 fixes)

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| `Workflows/REVPortalRoundStatistics-…json` (+`.notes.md`) | Cloud flow | **D-02 fix.** Added `Initialise_failure_detail` (top-level variable), wrapped the read/compute body in a new `Compute_statistics` `Scope`, and added `Find_the_failed_action` / `Describe_the_failure` / `Compose_run_link` / `Alert_on_failure` (calls `REV \| Ops \| Failure Alert`, no Solution.xml change — already a root component) / `Respond_error` (unconditional `Response`, `status: "error"`), following the `REVScoringDailySummary` precedent exactly | FR-057–062, TAD §5.1 |
| `src/pages/LandingPage.tsx` (+ `.test.tsx`) | Code App UI | **New — D-01 fix.** FR-056 navigation shell; composes `RoundStatistics`, `RoundFinancePanel`, diagnostic states | FR-056–063 |
| `src/components/RoundStatistics.tsx` | Code App UI | New. FR-058–062 content — every metric rendered against the full §3.3 contract; all but `applicationsReceived` render as absent today | FR-058–062 |
| `src/components/RoundFinancePanel.tsx` | Code App UI | New. FR-063 — direct `rev_roundfinance` read, own `rev_figuresasat` freshness statement | FR-063 |
| `src/components/DistributionChart.tsx` (+ `.test.tsx`) | Code App UI | New. ADR-029 — table-first, hand-rolled inline SVG bar chart from the same array, single series, no library | FR-061, FR-062, NFR-024 |
| `src/domain/landing.ts` (+ `.test.ts`) | Code App logic | New. All landing-screen decision logic (status handling, reconciliation, series-building) — no React, per this app's existing `domain/` convention | — |
| `src/dataverse/roundStatistics.ts` (+ `.test.ts`) | Code App data | New. §3.3 response type + parser + isolated flow-invocation stand-in (`A-LAND-2`) | FR-057–062 |
| `src/dataverse/roundFinanceReadService.ts` (+ `.test.ts`) | Code App data | New. Isolated stand-in read service for `rev_roundfinance` (`A-LAND-1`) — no generated service exists yet | FR-057, FR-063 |
| `src/dataverse/{schema,types,client,repository}.ts`, `src/hooks/queries.ts` | Code App data | Extended: `ENTITY_SETS.roundFinance`, `ROUND_FINANCE_COLUMNS`, option-set label maps; `getOpenRound()`/`getRoundStatistics()` on `TrusteeRepository`; `useOpenRound()`/`useRoundStatistics()` hooks | FR-057–063 |
| `src/App.tsx` (+ `.test.tsx`) | Code App UI | Landing is now the entry view (`{ name: "landing" }`), with a `<nav>` back to it from the list (FR-056) | FR-056 |
| `src/styles/{app.module.css,print.css}` (+ `print.test.ts`) | Code App UI | `data-print` convention extended to the new landing blocks and chart SVGs (FR-039, §8.2) | FR-039 |

### This revision (`rev_roundfinance` data source registration, 2026-08-26)

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| `power.config.json`, `.power/schemas/appschemas/dataSourcesInfo.ts`, `.power/schemas/dataverse/roundfinances.Schema.json`, `src/generated/models/Rev_roundfinancesModel.ts` (new), `src/generated/services/Rev_roundfinancesService.ts` (new) | Code App data (platform-generated) | `pa app add data-source --connector dataverse --table rev_roundfinance` run against DEV; closes `IMP-0329`'s gate finding | FR-057, FR-063 |
| `src/dataverse/client.ts`, `client.test.ts`, `src/dataverse/roundFinanceReadService.ts` | Code App data (comments only) | Updated to record A-LAND-1 CLOSED and that `READ_SERVICES` still deliberately points at the stand-in — no behaviour change | — |
| `config/revitalise-grant-automation-pipeline.yml` | Pipeline config | Annotated the combined `pa app add flow` / data-source manual post-deploy step: the data-source half is done and must not be re-run | — |

### This revision (D-10 fix, 2026-08-26)

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| `Workflows/REVPortalRoundStatistics-…json` | Cloud flow | **D-10 fix.** Removed `"Skipped"` from `Respond_error`'s `runAfter` on `Alert_on_failure`; extended the action's `description` to record the fix and its precedent | TAD §5.1 |

## 3. Data Model Changes

Per TAD §3.5 and §3.2.1, both closed with live evidence this session (not merely authored):

- **`rev_roundfinance`** — Tier 2, `OrganizationOwned`, no relationship to any other table. Live: 13
  attributes confirmed via `EntityDefinitions(LogicalName='rev_roundfinance')/Attributes`; alternate key
  `rev_roundfinance_name` confirmed `EntityKeyIndexStatus=Active` (no async wait needed); `EntitySetName`
  confirmed `rev_roundfinances`, `PrimaryIdAttribute` `rev_roundfinanceid`.
- **`rev_application.rev_caresupportdescriptionredacted` / `rev_careprovidedexampleredacted` /
  `rev_othercareprovidedtyperedacted`** — `ntext`, `MaxLength` 4000, `IsSecured=0`, `IsAuditEnabled=1`, shape
  copied from `rev_narrativeredacted`. Live: all three confirmed present on `rev_application`.

## 4. Automation / Workflow Changes

`REV | Portal | Round Statistics` (Category 5, `PrimaryEntity=none`, imports Draft like every other flow in
this solution). Reads `rev_roundfinance` (open-round lookup), `rev_application` (all rows in the round, no
eligibility filter, `Secure Outputs` ON). Responds with the §3.3 JSON contract; **this first version emits
`applicationsReceived` only**, with every other metric explicitly `null` and a stated reason in the flow's own
`notes.md`. Not yet imported into DEV — see §10 A-FLOW-01 and §7.

**This revision adds the failure path TAD §5.1 specifies and test-agent's D-02/TC-SEC-06 found missing.**
Before this fix, every action ran `runAfter: ["Succeeded"]` only, so a genuine failure of either
`OpenApiConnection` action (`List_the_open_round`, `List_applications_in_round`) terminated the run with no
`Response` ever reached — the code app would have received a bare, unhandled platform failure. The fix,
authored by a scoped `automation-agent` dispatch, follows this solution's own existing pattern
(`REV | Scoring | Daily Summary`'s `Summarise`/`Find_the_failed_action`/`Describe_the_failure`/
`Compose_run_link`/`Alert_on_failure` shape) rather than inventing a new one:

| Added | Type | Behaviour |
|---|---|---|
| `Initialise_failure_detail` | `InitializeVariable` (top level — `IMP-0137`'s nesting rule) | Default failure-detail string |
| `Compute_statistics` | `Scope` | Wraps the original body (`List_the_open_round` through `Switch_on_open_round_count`) as one catch point |
| `Find_the_failed_action` | `Query` | `runAfter: Compute_statistics:["Failed","TimedOut"]` — the failed child by `status`, not `result()[0]` (`IMP-0106`'s lesson) |
| `Describe_the_failure` → `Set_failure_detail` | `Scope` / `SetVariable` | Human-readable action/code/message string |
| `Compose_run_link` | `Compose` | Deep link to this run, from `workflow()` |
| `Alert_on_failure` | `Workflow` (calls `8f1c2a44-1004-4b7a-9e21-0a1b2c3d4e04`, `REV \| Ops \| Failure Alert`) | Writes the `rev_errorlog` row and alerts the process owner — no new Solution.xml entry needed, already a root component. Severity `Warning`: a failed on-demand read costs one dashboard reload, no data lost, no application blocked — smaller than `REV \| Scoring \| Daily Summary`'s own `Warning` case |
| `Respond_error` | `Response`, `kind: "PowerApp"` | ~~`runAfter: Alert_on_failure:["Succeeded","Failed","TimedOut","Skipped"]` — fires unconditionally~~ **corrected, revision 0.3 (D-10)**: `runAfter: Alert_on_failure:["Succeeded","Failed","TimedOut"]` — `Skipped` removed, so it fires only when the failure chain actually ran, not on every successful run (see §0.3). `status: "error"` — does not collide with the four TAD §3.3 already names (`no-open-round`/`ambiguous-round`/`truncated`/`threshold-unset`); `roundKey` is deliberately omitted (the catch spans a point both before and after the round key is known) |

The four existing business-outcome `Respond_*` actions and `List_applications_in_round`'s `Secure Outputs`
setting are unchanged. New assumption: **A-FLOW-05** (§10) — no flow in this solution had previously exercised
a `Response`/`kind:"PowerApp"` action reached via a `runAfter:["Failed",…]` chain.

**Revision 0.3 (D-10 fix, 2026-08-26).** The original wiring above included `Skipped` in `Respond_error`'s
`runAfter`, copied from `REVOpsFailureAlert`'s `Respond_to_calling_flow` — safe there only because that flow
has exactly one `Response` action; unsafe here, where it is one of four, because `Alert_on_failure` is
skipped by design on every successful run, which then let `Respond_error` fire a second, unwanted response
after a business-outcome `Respond_*` had already replied. Fixed by removing `Skipped`, matching
`REVIntakeWordPressToDataverse`'s `Respond_500_intake_failed` — the solution's other multi-`Response` flow
with the identical `Alert_on_failure` predecessor — exactly. See §0.3 for the full account.

No existing flow's *behaviour* changed. `REV | Narrative | Scrub Free-Text`'s eventual extension (Automation
#5, deferred) to the three new redacted columns is unchanged scope, not built here (TAD §5.5).

## 5. Configuration & Provisioning Changes

| Key | Environment | Notes |
|---|---|---|
| `dataverse.auditing.auditedTables` | dev, test, prd | `rev_roundfinance` appended |

### Provisioning Scripts

| Script | Purpose | Pipeline Block | Idempotency Check |
|---|---|---|---|
| `ensure-schema.ps1 -Env dev` | `rev_roundfinance` + attributes + key; 3 redacted columns; role privileges | `dev.environment_prerequisites` | Run live twice this session. First run created everything (exit 0). **Second run: exit 0, 459 `EXISTS` lines, 0 `FAILED`**, including every one of this feature's own resources by name (table, 13 columns, alternate key, 3 redacted columns, 5 role privileges) — idempotency re-confirmed by observation, not merely asserted |
| `ensure-auditing.ps1 -Env dev` | Table auditing on `rev_roundfinance` | `dev.environment_prerequisites` | `IsAuditEnabled` read back `true` live |

11 new `dev.environment_prerequisites` entries were added to `config/revitalise-grant-automation-pipeline.yml`
covering the schema/role/audit work (DONE, this session) and the flow's remaining manual steps (designer
save + connection binding + turn-on; `pa app add flow`; the tenant DLP check; the FR-062 threshold seed
blocked on OQ-039; the first `rev_roundfinance` row; the brand-ramp extraction) — each with an `owner` and a
clear statement of what blocks it. `python3 scripts/verify-pipeline-config.py
config/revitalise-grant-automation-pipeline.yml` passes (93 steps, 43 executable / 50 manual).

## 6. Security Controls Implemented

| TAD §6 control | Implementation | Verified |
|---|---|---|
| Least privilege (`C-DOM-020`) | Trustee: read-only on `rev_roundfinance` + `prvReadWorkflow` (invoke-only). Service identity: read-only on `rev_roundfinance`, nothing else added. REV Admin: Create/Read/Write only (no Delete/Assign/Share) | Live, all three roles |
| `no-secured-columns-in-code-app` | The three new redacted columns are `IsSecured=0`; the three source columns they redact remain `IsSecured=1` and are not bound anywhere in this dispatch's own changes | `python3 scripts/verify-shipped-content.py` and the Pester suite both pass |
| Table auditing (`C-DOM-010`/`011`, `C-TECH-064`) | `rev_roundfinance.IsAuditEnabled=true` | Live GET, this session |
| Secure Outputs on personal-data reads (`C-DOM-004`, TAD §6.4) | Set on the new flow's `List_applications_in_round` action. **Not** enforced as a build gate repo-wide — see §7 and Findings Logged: doing so surfaced 6 pre-existing violations in two flows outside this WBS's scope | Manual inspection of the authored JSON only (V1) |
| `prvReadWorkflow` minimum level | Granted at Global as a starting candidate | **A-FLOW-02, OPEN** — §10 |
| Failure path carries no personal data (`C-DOM-004`, NFR-012) | `Alert_on_failure`'s body is the flow name, run name, action/code/message string and a run link — no row, no applicant/application reference | Manual inspection of the authored JSON (V1) |
| Landing screen never reads `rev_applicant`/`rev_application` directly (§1.1, §6.3's basis) | `src/dataverse/repository.ts`'s new `getOpenRound()`/`getRoundStatistics()` query only `rev_roundfinance` and the flow's response; grepped — no `listRecords`/`getRecord` call against either table appears anywhere in `src/pages/LandingPage.tsx`, `src/components/RoundStatistics.tsx` or `src/components/RoundFinancePanel.tsx` | `python3 scripts/verify-code-app-column-bindings.py src/code-apps/trustee-review-portal src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml` — OK, 7 tables now in scope (adds `rev_roundfinance`, `rev_setting`), 0 forbidden references |

## 7. Known Limitations / Deferred Items

**Closed by revision 0.3 (2026-08-26), not carried forward:** "the D-02 fix responds twice on the success
path" (D-10 — §0.3, §4, §10 A-FLOW-05). **Explicitly named, not fixed, by the same revision** (out of this
dispatch's scope — the reviewer's instruction was the one-token `Skipped` removal only): `Find_the_
failed_action`'s `runAfter` on `Compute_statistics` accepts only `Failed`/`TimedOut`, not `Skipped` — if
`Compute_statistics` itself were ever skipped (only reachable if one of the two earlier top-level actions,
`Capture_computedOn`/`Initialise_failure_detail`, itself failed or was skipped), no response at all would
reach the caller. Structurally identical to `REVIntakeWordPressToDataverse`'s own accepted precedent shape
— not unique to this flow, and not raised by test-agent as a defect in its own right.

**Closed by revision 0.1**, not carried forward: "the flow has no failure path" (D-02 — §4, §10 A-FLOW-05)
and "`LandingPage.tsx`/the charts are not started" (D-01 — §1, §2). What replaces them:

- **The flow is not yet live in DEV.** `pac solution pack`/`pac solution check` both pass (re-confirmed this
  revision — 0 Critical/High/Medium/Low/Informational, and `verify-flow-definition-language.py` stays clean
  with the new actions); the actual `pac solution import` is build-agent/pipeline-agent's normal deploy step,
  not something this dispatch performed directly (see §0 and §10 A-FLOW-01/A-FLOW-05).
- **The flow still computes only `applicationsReceived`.** Every other §3.3 metric is `null` by design —
  unchanged by this revision, see the flow's own `notes.md` for exactly what remains (an applicant-side
  `List rows` action, a `rev_setting` threshold read, and the array-expression grouping logic). The landing
  screen is now built against the full contract, so nothing on the UI side blocks those metrics appearing —
  only the flow's own next version does.
- **The flow still has no generated Code App data source — `rev_roundfinance` now does (2026-08-26, §0.2).**
  `pa app add flow` has never been run (the flow is not live in any environment yet); `pa app add
  data-source --table rev_roundfinance` has now been run against DEV and A-LAND-1 is CLOSED. The landing
  screen still reads the round-finance table through `src/dataverse/roundFinanceReadService.ts`'s stand-in
  rather than the newly-generated `Rev_roundfinancesService` — deliberately: both now resolve identically for
  a real signed-in user, and the swap is a separate one-file cleanup, not a defect. `src/dataverse/
  roundStatistics.ts` (A-LAND-2, the flow invocation) remains a genuine open gap, unchanged — it cannot be
  registered until the flow itself is live. §10.
- **Two response-contract fields TAD §3.3 leaves genuinely unspecified were given an inferred shape,
  each marked**: FR-062's three proportions (A-LAND-3 — §3.3 shows only `null`, never a populated example)
  and FR-060's break-type total row (A-LAND-4 — §3.3 shows `"total": {}`, naming no field). Both are
  reconciled against a real flow response once one exists, not before.
- **Four genuine open questions the plan and the TAD do not answer**, surfaced only by actually typing the
  §3.3 contract against a UI (reported here rather than guessed past): (1) the flow's single `Text` output
  has no agreed name, so the app currently accepts whichever single string property arrives rather than a
  named one; (2) `threshold-unset`'s diagnostic wording is not authored anywhere — the UI gives it the
  generic "figures unavailable" treatment; (3) FR-058's round-open date has two sources
  (`rev_roundfinance.rev_roundopenedon` direct-read, and the flow's `applicationsPerDay.openedOn`) with
  nothing to reconcile them if they ever disagree — the screen renders the direct-read one and uses only the
  flow's `days` count; (4) `populationReceived` and `metrics.applicationsReceived.count` name the same figure
  twice in one contract — the screen renders the metric as the headline and the population value only as the
  denominator sentence, deriving neither from the other. Logged as `IMP-0331` (below) for architect-agent's
  next TAD revision to pin down, rather than left for the next person to rediscover.
- **A gap FR-035's own frontend-agent dispatch surfaced and correctly left alone:** TAD §3.2 describes
  `rev_careprovidedtype`, `rev_carehoursperweek` and `rev_applicanttype` as "already shipped" and
  trustee-visible, but none of the three is actually wired anywhere in `trustee-review-portal` today. This
  dispatch's WBS 6.3 scope was specifically the three *redacted* columns; the structured pair and
  applicant-type context are a separate, apparently-still-open piece of FR-035 this document does not claim
  done. Flagged for the reviewer to resolve — either a prior claim was inaccurate, or this is unquoted scope.
  **Unchanged by this revision** — out of its scope.
- **A newly-discovered, pre-existing gap, out of this WBS's scope:** `REVIntakeWordPressToDataverse` and
  `REVScoringDailySummary` (Automations #1/#2) read `rev_application`/`rev_applicant` rows without Secure
  Outputs — a real personal-data exposure in already-shipped flows this dispatch did not author. Flagged to
  `commercial-agent`/reviewer via `IMP-0320`, not fixed here.
- **NFR-026's brand half is unmet.** `theme.ts` ships Fluent's own default ramp as an explicit placeholder;
  the real Revitalise brand values are absent from the public site's served markup (A-R26). The new chart
  bars reuse the same placeholder tokens (`var(--colorCompoundBrandBackground)` etc.) and move with the ramp
  when it is supplied — they do not need a second contrast pass, but the one pass still awaits the ramp.
- **The improvement-log backlog that blocked the next build at `C-TECH-061` has since been cleared —
  updated 2026-08-26, not by this dispatch.** The 17-unread figure recorded below was overtaken by
  improvement review 29 (`docs/improvements/2026-08-25-improvement-review-3.md`, applied), which processed
  `IMP-0329` (this section's own gate) among 38 reviewer-deferred entries. `python3 scripts/
  verify-improvement-log.py --check` exits **0 (OK)** every time this revision re-ran it, most recently at
  334 entries (44 NEW, 289 APPLIED, 1 REJECTED) — the exact total keeps moving because this repository is a
  synced path other sessions write to concurrently (`IMP-0080`/`IMP-0213`'s known behaviour; `IMP-0336`/
  `IMP-0337` landed mid-dispatch), so cite the exit code, not the count, as the fact that matters: the
  build's `improvement-log-check` step is no longer blocked. Left here, struck through in substance rather
  than deleted, so the next reader does not re-derive "17 unread" from a stale figure (`IMP-0330`'s class —
  a stale claim contradicting a re-checked source).

## 8. Build Instructions

No new artifact type: the flow ships inside the same `RevitaliseGrantAutomation.zip` (Unmanaged and Managed)
`config/revitalise-grant-automation-build.yml` already packages. One config change made: `--expect-flows`
4 → 5 in the `source-validate` step, matching the fifth flow now on disk. No new build gate was added for
Secure Outputs (see Findings Logged and §7) — a future dispatch should add it once the two pre-existing
flows are fixed or a `known-exceptions.json` entry is reviewer-approved for them.

**This revision needs no `config/revitalise-grant-automation-build.yml` or `-pipeline.yml` change.**
`--expect-flows` stays 5 (the flow's content changed, not its count); `no-secured-columns-in-code-app`
already scoped `rev_roundfinance`/`rev_setting` into its 7-table check from the earlier schema pass and
passes unchanged with the new UI added (§11); `verify-solution-root-components.py` stays at 66 (`Alert_on_
failure` references an existing root component, adds none); the pipeline config's manual post-deploy step
for registering `rev_roundfinance` in the app's data sources (`config/revitalise-grant-automation-pipeline.yml`
line ~799) already anticipated this exact swap-in. `python3 scripts/verify-build-config.py
config/revitalise-grant-automation-build.yml` → PASS, 55 steps, 41 gates (re-run this revision).
**This closes D-01**: the manifest's next build will describe content that now actually exists in the tree.

**§0.2's registration fix (2026-08-26) needed no `build.yml` change either** — `scripts/verify-code-app-
data-sources.py` was wired in by improvement review 29, not by this dispatch, and it is a source-consistency
check, not a table/step count this fix touches. `config/revitalise-grant-automation-pipeline.yml` got an
annotation-only edit (§0.2, §2) — no step added or removed. Re-run this revision: `python3 scripts/
verify-build-config.py config/revitalise-grant-automation-build.yml` → **PASS, 58 steps, 44 gates** (up
from 55/41 — the three-step difference is improvement review 29's own additions, not this fix's);
`python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml` → PASS, 93
steps, unchanged. `python3 scripts/verify-code-app-data-sources.py src/code-apps/trustee-review-portal` →
**OK — 5 registration(s), 5 Dataverse source(s) declared** (was FAILED, 1 violation, before this fix).

## 9. Test Guidance

- Full Pester suite: `pwsh -NoProfile -File src/tests/Invoke-Tests.ps1` — **874 passed, 1 failed, 1 skipped**
  (re-run by development-agent, this revision). The one failure is `'verify-improvement-log --check' passes
  against the real log`, and it is **not** a regression in the code this revision touched: test-agent's own
  cycle had this figure at 875/0/1, after the backlog had been read down under the 10-entry batch trigger.
  Seven findings have landed since (test-agent's own four, plus this revision's `IMP-0329`/`IMP-0330`/`IMP-0331`),
  pushing the unread count to 17 and the gate back to failing — exactly §7's newly flagged blocker for the
  next build.
- `python3 scripts/verify-tad-coverage.py`, `verify-solution-root-components.py
  src/solutions/RevitaliseGrantAutomation` (66, unchanged), `verify-audited-tables.py`,
  `verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation` (re-run in revision 0.1 — OK, 5
  flow definitions clean, including the new failure-path actions; **re-run again in revision 0.3 after the
  D-10 fix — OK, unchanged, 5 flow definitions clean**), `verify-shipped-content.py
  src/solutions/RevitaliseGrantAutomation`, `verify-field-length-limits.py
  src/solutions/RevitaliseGrantAutomation`, `verify-assumption-markers.py` (re-run twice this revision —
  first after adding the 5 new §10 rows: PASS, 15 OPEN rows across 4 documents, every one carrying its
  source marker, 33 rows total, 11 closed. Re-run again after §0.2's registration fix closed A-LAND-1: PASS,
  **14 OPEN, 12 closed**, 33 rows total, 7 unresolvable, 0 exempt) — all PASS.
- `pac solution pack --packagetype Unmanaged` (re-run by development-agent this revision, independent of
  automation-agent's own Managed+Unmanaged run) → packs clean, same 14-line pre-existing "not defined in
  customizations" warning, unrelated to this fix. `pac solution check` re-confirmed by automation-agent at
  0 Critical/High/Medium/Low/Informational; not re-run against the hosted checker a third time in this
  session.
- Code app: `npm run typecheck` / `npm run lint` / `npm test -- --coverage` in
  `src/code-apps/trustee-review-portal` — **all pass, re-run by development-agent this revision: 372/372
  tests across 21 files, 96.27% statement/line coverage** (93.07% branches, 93.29% functions — all above the
  80% bar), up from the prior 246/246, 16 files, 94.44%. `python3 scripts/verify-code-app-column-bindings.py
  src/code-apps/trustee-review-portal src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml`
  → OK, 7 tables now in scope (`rev_roundfinance`, `rev_setting` newly added), 0 forbidden references, all 3
  fail-closed visibility columns present.
- **When the flow is live:** test-agent's V4/V5 work is exactly TAD §12.2's rows — reconcile the gender
  distribution as a real trustee once the applicant-side metrics are built (this version has none secured
  enough to need that check yet, since it emits no distributions at all). Additionally now needed:
  `pa app add flow`/`pa app add data-source --table rev_roundfinance`, then delete
  `roundStatistics.ts`'s/`roundFinanceReadService.ts`'s stand-ins (A-LAND-1, A-LAND-2) and reconcile the two
  inferred shapes (A-LAND-3, A-LAND-4) against a real response.

## 10. Unvalidated Assumptions Register (C-TECH-052)

| ID | Claim | Where in source | Evidence | Why not verified | Cheapest verification | Status |
|---|---|---|---|---|---|---|
| A-FLOW-01 | A Power Apps trigger (`kind: "PowerApp"`) and a `Response`/`kind: "PowerApp"` action, hand-authored in `REVPortalRoundStatistics-…json`, are well-formed and will be accepted by the Power Automate designer without a save error | [`src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json), `properties.definition.description` — marked `A-FLOW-01` | E3 (general knowledge of a stable, long-unchanged platform shape; this solution's other 4 flows have no example to copy) | This solution's other flows are all Dataverse-row-triggered or scheduled; Microsoft's public docs describe the CLI surface around this mechanism but not the raw JSON | `pac solution pack`/`pac solution check` both already passed clean (V1→V2, this session). Next: a human opens the flow in the Power Automate designer after import and saves it | OPEN |
| A-FLOW-02 | `prvReadWorkflow` at `Global` level is sufficient (and not excessive) for a trustee to invoke this specific flow | `Roles/REV Trustee/REV Trustee.xml`, comment beside the grant — marked `A-FLOW-02` | E3 (Microsoft's own note says only "the App Opener security role or an equivalent role") | No live invocation as a real trustee has been attempted | Grant `prvReadWorkflow` and nothing else, invoke as a real trustee once the flow is live; narrow the level if a lower one still works | OPEN |
| A-FLOW-03 | `Secure Outputs` (`runtimeConfiguration.secureData.properties: ["outputs"]`) actually hides row data from run history the way the designer's "Secure Outputs" checkbox does, for a hand-authored flow (never opened in the designer) | [`src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json), `properties.definition.description` — marked `A-FLOW-03` (shares the top-level marker with A-FLOW-01/04; the specific action is `List_applications_in_round`) | E3 (stable, documented Logic-Apps-family property; not confirmed for THIS hand-authored file specifically) | No live run has occurred yet | Once live, run the flow once and read its own run history as an owner: confirm row data is absent, response body present (TAD §12.2's own row for the same question) | OPEN |
| A-FLOW-04 | The service connection reference (`rev_SharedDataverse`) this flow reuses will bind correctly to a Power-Apps-triggered flow the same way it already binds to the four Dataverse-row-triggered/scheduled flows | [`src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json), `properties.definition.description` — marked `A-FLOW-04` (shares the top-level marker with A-FLOW-01/03; the specific field is `properties.connectionReferences`) | E2 (the mechanism is the same connection reference object; the trigger type is new) | No live import/activation yet | Confirm at the same designer-save step as A-FLOW-01 | OPEN |
| A-FLOW-05 | **Corrected, revision 0.3 (2026-08-26), per test-agent's D-10 finding that the original wording was one-sided.** Two claims, not one: (a) a `Response`/`kind: "PowerApp"` action (`Respond_error`), reached via a `runAfter: ["Failed","TimedOut"]` chain off `Alert_on_failure`, will actually execute and return a body to the calling code app on a genuine failure — no flow in this solution had previously exercised a `Response` action reached via a failure path under this specific trigger kind (`REVOpsFailureAlert`'s own always-respond action is `kind: "Http"`, not `kind: "PowerApp"`); (b) it does **not** execute on a successful run — **closed statically, this revision**: `Skipped` was removed from the `runAfter` condition list (D-10's fix), so `Respond_error` cannot fire when `Alert_on_failure` is skipped by design, which is exactly the successful-run case. Only claim (a) remains open | [`src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json), `properties.definition.description` and `Respond_error`'s own `description` — both marked `A-FLOW-05` | Claim (a): E2 (the `Response` action's own shape is E3-precedented via A-FLOW-01; what is new here is reaching it from a `runAfter:["Failed",…]` chain specifically). Claim (b): E4 — proven by direct inspection of the corrected `runAfter` list, deterministic from the platform's own documented `Skipped`-status semantics, no live run needed | Claim (a): this solution's other 4 flows have no Power-Apps-triggered failure path to copy; none is imported/live | Claim (a) only: once live, force a failure of `List_the_open_round` (e.g. a temporary bad `$filter`), invoke as the code app, and confirm a `status:"error"` body is received rather than a bare platform failure. Claim (b) needs nothing further — see the Evidence cell above | OPEN — claim (a) only; see the Claim cell for the other half |
| ~~A-LAND-1~~ | ~~A hand-written stand-in (`roundFinanceReadService.ts`) — calling `getClient(dataSourcesInfo).retrieveMultipleRecordsAsync("rev_roundfinances", …)` on the `"Dataverse"`-type path — behaves the same way the real generated `Rev_roundfinancesService` will once `pa app add data-source --table rev_roundfinance` is run; no such service exists yet to compare against~~ **CLOSED (E1), 2026-08-26** — `pa app add data-source --connector dataverse --table rev_roundfinance -u https://orge2b20d13.crm17.dynamics.com -c f31ddadfbe874e50a34054df668e75cf` was run (`IMP-0329`'s gate found the gap first); the generated `Rev_roundfinancesService.getAll`/`.get` are the identical calls the stand-in already made, confirmed by direct comparison, not inference. `READ_SERVICES` still points at the stand-in on purpose (§0.2) — closing the assumption did not require swapping it. | [`src/code-apps/trustee-review-portal/src/dataverse/roundFinanceReadService.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/roundFinanceReadService.ts):4, referenced from [`client.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts):199 | E1 (platform-generated file compared directly against the stand-in) | — | Optional cleanup, not required for correctness: swap the `READ_SERVICES` entry in `client.ts` for `Rev_roundfinancesService` and delete `roundFinanceReadService.ts` | **CLOSED** |
| A-LAND-2 | A hand-written stand-in (`fetchRoundStatistics`'s default) calls the eventual generated flow service correctly — a static no-argument `Run()` returning an `IOperationResult`-shaped result, with the §3.3 JSON arriving as the single string property of the payload | [`src/code-apps/trustee-review-portal/src/dataverse/roundStatistics.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/roundStatistics.ts):36 (also `:115`, `:124`, `:420`) | E2 (mirrors the shape of the app's other generated services; the flow-invocation service specifically has never been generated) | `pa app add flow` has never been run — the flow is not live in any environment | `pa app list-flows` → `pa app add flow --flow-id <id>`; replace the default in `fetchRoundStatistics` (`roundStatistics.ts:420`) with the generated service and reconcile `extractResponseText` against its actual output property name | OPEN |
| A-LAND-3 | FR-062's three headline proportions (high-hours care, low life satisfaction, unable to take a break) are each shaped `{ population, count, percentage }` once populated | [`src/code-apps/trustee-review-portal/src/dataverse/types.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/types.ts):305 | E3 (TAD §3.3 shows all three only as `null`; the populated shape is inferred to match every other auditable figure on the screen — numerator, denominator, percentage — not read from any example) | TAD §3.3 never shows one populated; OQ-039 (the three thresholds) is still open, owner Emily | Once OQ-039 supplies the thresholds and the flow emits one populated proportion, compare its actual shape against this inferred one | OPEN |
| A-LAND-4 | FR-060's break-type profile total row mirrors a data row (per break-type value) minus the category field, with every field optional and rendered only when present | [`src/code-apps/trustee-review-portal/src/dataverse/roundStatistics.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/roundStatistics.ts):287 and [`types.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/types.ts):274 | E3 (TAD §3.3 shows `"total": {}`, an empty object naming no field at all) | TAD §3.3 never shows a populated total row | Once the flow emits a real `breakTypeProfile`, compare its actual `total` shape against this inferred one | OPEN |

Two rows the TAD itself carried as OPEN are now CLOSED by this session's live work, not repeated here as
open: `rev_roundfinance`'s `EntitySetName`/`PrimaryIdAttribute` (TAD §12.2), and A-FIN-02 (the `decimal`
attribute branch in `ensure-schema-helpers.psm1`, previously never run against a live environment) — see
`IMP-0316`.

## 11. Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

### Verification level reached

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| `rev_roundfinance` table + 13 attributes + alternate key | **V4** | DEV (macOS, cert-based Web API) | `ensure-schema.ps1 -Env dev` exit 0; live GET confirms 13 attribute names, `EntityKeyIndexStatus=Active`, `EntitySetName=rev_roundfinances` |
| 3 redacted columns on `rev_application` | **V4** | DEV | Live GET confirms all three present; `pa app refresh data-source --name applications` regenerated the TS model with them (`grep redacted` on `Rev_applicationsModel.ts`) |
| Role privilege grants (3 roles) | **V4** | DEV | Live `roles(<id>)/roleprivileges_association` confirms each named privilege on each named role |
| Table auditing on `rev_roundfinance` | **V4** | DEV | Live GET `IsAuditEnabled=true` |
| `REV \| Portal \| Round Statistics` flow | **V2** | Local (SolutionPackager + hosted Solution Checker) | `pac solution pack --packagetype Unmanaged` exits 0, flow listed under "Processing Component: Workflows"; `pac solution check` (hosted, Europe) returns 0/0/0/0/0 across all severities |
| `pa app list-flows` / `pa app add flow` mechanism | **V3 (connectivity), not V4 (a working flow)** | DEV, live | `pa app list-flows --non-interactive` from `src/code-apps/trustee-review-portal` returned a real result ("No flows found") against the real DEV environment, not a refusal — confirms the CLI/auth path works; no flow has been added yet because none is live |
| ADR-026 brand theme | **V2** | Local | `npm run typecheck`/`lint`/`test` pass; no live Code App push performed |
| FR-035 redacted-column UI (`CareSupportPanel`) | **V2** | Local | `npm run typecheck`/`lint`/`test` pass (246/246, 16 files); `scripts/verify-code-app-column-bindings.py` confirms only the 3 redacted columns are bound, not their secured sources; no live Code App push performed |
| **The flow's failure path** (`Compute_statistics` scope, `Alert_on_failure`, `Respond_error`) | **V2**, plus one property proven by static inspection alone (no level needed — see note) | Local (SolutionPackager + hosted Solution Checker, re-confirmed independently by development-agent; D-10 fix re-verified this revision, source inspection only, no packer re-run needed — §0.3) | `pac solution pack` (both package types) exits 0; `pac solution check` 0/0/0/0/0 (automation-agent's run); `verify-flow-definition-language.py` OK, 5 flow definitions clean, re-run again after the D-10 fix with the same result; every action `description` ≤256 chars, checked programmatically. No live import — A-FLOW-05's claim (a) (§10) is the untested half. **A-FLOW-05's claim (b)** — that `Respond_error` does NOT fire on a successful run — is settled by direct inspection of the corrected `runAfter` list, not by any verification level on the V1–V5 ladder: the platform's own documented `Skipped`-status semantics make the absence deterministic once the condition is removed, the same basis test-agent used to rate the original D-10 defect a certainty rather than a guess |
| **`LandingPage.tsx` + `RoundStatistics`/`RoundFinancePanel`/`DistributionChart`** | **V2** | Local | `npm run typecheck`/`lint`/`test -- --coverage` pass, 372/372 across 21 files, 96.27% stmt/line coverage (re-confirmed unchanged after §0.2's fix); `verify-code-app-column-bindings.py` OK with `rev_roundfinance`/`rev_setting` in scope. No live Code App push, no live flow binding — A-LAND-2 (§10, the flow) is the remaining untested half; A-LAND-1 (the table read) is now CLOSED, see the next row |
| `rev_roundfinance` Code App data source (`pa app add data-source`, §0.2) | **V3 (the binding), not V4 (a real signed-in user's read)** | DEV, live | Platform accepted the call and returned real metadata: `dataSourcesInfo.ts`'s new `"rev_roundfinances"` entry reports `primaryKey: "rev_roundfinanceid"`, matching `IMP-0316`'s live-confirmed value exactly; `scripts/verify-code-app-data-sources.py src/code-apps/trustee-review-portal` → OK, 5/5. Not V4: no real signed-in trustee has opened the app since — same residual `verify-code-app-data-sources.py`'s own docstring states (a declared source can still have a broken connection underneath) |

### Tool warnings triaged (C-TECH-055)

| Warning | Source step | Resolved / Accepted | Rationale if accepted |
|---|---|---|---|
| `pac solution pack` reports 14 `RootComponent`/`EnvironmentVariableDefinition` entries "not defined in customizations" | `pac solution pack --packagetype Unmanaged` | Accepted, pre-existing | Present before this dispatch's changes (relationship/environment-variable declarations from earlier work), unrelated to `rev_roundfinance` or the new flow; not touched by this WBS scope |
| None from `pac solution check` | hosted Solution Checker | Resolved | 0 Critical/High/Medium/Low/Informational |
| `verify-forms-and-views-reachable.py`: 2× on `rev_roundfinance` — `Entity.xml` declares empty `<FormXml />` and `<SavedQueries />` markers with no matching folder content | `forms-and-views-reachable` (build step, `scripts/verify-forms-and-views-reachable.py src/solutions/RevitaliseGrantAutomation`) | Accepted | Same warning shape already accepted with recorded rationale for the 4 WBS-0.4 finance/record-only tables — `rev_bankaccount`, `rev_payment`, `rev_provider`, `rev_anonymisedstatistic` (see [parent Dev Summary, "Tool warnings" note](docs/development/revitalise-grant-automation-dev-summary.md#L5446)). `rev_roundfinance` is likewise a schema-only, organization-owned table (TAD ADR-028): it carries no form or view because no UI is in `wbs:6.9`'s scope — the round-statistics landing screen reads it only through the new flow's typed service, never through a Dataverse form. Not a defect. |

### Diagnostic components created and removed (C-TECH-056)

None. Every live create in DEV this session (`rev_roundfinance`, its attributes, the 3 redacted columns, the
role privileges, table auditing) is the actual feature deliverable, not a throwaway probe.

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0311 | (frontend-agent's own — see `logs/improvement-log.jsonl`) | — | `.preserveLines` (the narrow-measure class) was already applied by `MultilineText`/`Panel.tsx` — reused rather than re-invented for the brand theme's full-width shell |
| IMP-0313 | `harness-blocks-destructive-call` | friction | An Agent-tool dispatch describing a live write can be refused before the sub-agent starts; do not retry the identical dispatch — do the operation directly if the dispatching agent already has working live access this session |
| IMP-0314 | `harness-blocks-destructive-call` | friction | A primary agent's own foreground Bash-tool cert-based pwsh live write succeeded, unrefused, under Auto Mode — narrows IMP-0287's blanket claim |
| IMP-0315 | `test-coupled-to-absolute-counts` | rework | Grep the WHOLE test tree for a hardcoded schema count, not just the file most recently generalised for this class — four separate locations existed |
| IMP-0316 | `platform-fact-groundtruthed` | friction | The `decimal` attribute branch (A-FIN-02) and `rev_roundfinance`'s `EntitySetName`/`PrimaryIdAttribute` are now confirmed live — close both open assumptions |
| IMP-0317 | `platform-fact-groundtruthed` | friction | `pa` (not `pac`) is the real CLI for code-app flow integration, confirmed live; a cloud flow needs its own `RootComponent type="29"` entry, not covered by `behavior="0"` |
| IMP-0320 | `no-assertion-on-shipped-content` | **blocker** | Two already-shipped flows read personal data with no Secure Outputs — a real, pre-existing exposure, out of this WBS's scope to fix; flagged for commercial-agent/reviewer, new gate deliberately NOT wired in yet |
| IMP-0321 | (frontend-agent's own — see `logs/improvement-log.jsonl`) | — | `schema.test.ts`'s "no secured column" check used substring matching, which false-flagged the new redacted columns (each is its secured source's name + `redacted`, no separator); corrected to the real gate's whole-identifier regex |

### This revision (D-01/D-02 fixes)

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0329 | `unbuildable-instruction` | friction | TAD §5.4 requires registering `rev_roundfinance` in `READ_SERVICES` with "its generated per-table service", but no provisioning item produces one (§12's table lists the flow's `pa app add flow` verb but no data-source verb for the table) — a new table read by an existing code app needs the same explicit provisioning item a new flow needs |
| IMP-0330 | `stale-comment-contradicts-source` | friction | `BREAK_TYPE_LABELS` was an empty stub whose comment claimed the option set was a placeholder; five real labels existed in source. `schema.test.ts` now re-derives all six option-set label maps from `OptionSets/*.xml` rather than trusting the transcription |
| IMP-0331 | `response-contract-underspecified` | friction | An approved TAD's worked-JSON-example response contract (§3.3) left four things unresolved that only surfaced when a UI was actually built against it: an unnamed flow output, one status with no authored wording, two sources for one fact with nothing to reconcile them, and one figure named twice. A worked example is not a complete field-by-field specification |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py` → 328 entries, 486 lines.
`verify-improvement-log.py --check` → structurally OK (0 duplicate/malformed ids); the batch-trigger note is
carried in §7, not a defect in the log itself.

### This revision (`rev_roundfinance` data source registration, 2026-08-26)

**0 entries appended.** None of the standing triggers fired: this was not a second attempt at anything, no
document was contradicted by reality (the fix matched `IMP-0329`'s own prediction exactly, and A-LAND-1's
guess closed CONFIRMED rather than WRONG), the status below is a normal `CODE REVIEW REQUIRED`, and the gate
`IMP-0329` produced (`scripts/verify-code-app-data-sources.py`) caught exactly the gap it was built to catch
— a success for that gate, not a failure of it. `logs/known-failure-modes.md` is unchanged by this revision
(already current, per its own 2026-08-26 generation timestamp, from improvement review 29's own processing).

### This revision (D-10 fix, 2026-08-26)

**0 entries appended.** Test-agent already logged this defect and both of its related process gaps in
full before this dispatch started: `IMP-0345` (the defect's own root cause and a proposed build-gate),
`IMP-0346` (no regression test guarded the fixed D-02 behaviour), `IMP-0347` (A-FLOW-05's one-sided
framing — the same correction applied to that row in §10 above). All three remain `status: NEW`,
unprocessed by `improvement-agent`. This dispatch's fix matches `IMP-0345`'s predicted lesson exactly and
surfaces nothing new; logging a fourth entry for the same defect would duplicate an already-logged finding,
which `skills/how-to-log-an-improvement.md` §1 explicitly excludes ("do not log... anything already
recorded"). Neither `IMP-0345`'s proposed build-gate (a check-6 addition to
`verify-flow-definition-language.py`) nor `IMP-0346`'s proposed regression test was implemented by this
dispatch — both are `proposed_change` entries awaiting `improvement-agent`/`APPROVE IMPROVEMENTS`, not a
development-agent's to apply unilaterally. `logs/known-failure-modes.md` is unchanged by this revision —
no new entry to fold in, and `IMP-0345`/`IMP-0346`/`IMP-0347` were already folded into the digest before
this dispatch started (confirmed by grep: all three appear in the current file, generated 2026-08-26).

---

## Code Review Checklist
- [x] **D-10 (P1, test-agent's re-test) fixed** — `Respond_error`'s `runAfter` no longer accepts `Skipped`
      on `Alert_on_failure`, matching `REVIntakeWordPressToDataverse`'s `Respond_500_intake_failed` exactly
      (§0.3, §4). Re-verified: JSON parses, `verify-flow-definition-language.py` OK (5 clean), no other
      "Skipped" occurrence remains in the flow's `runAfter` conditions (grepped). A-FLOW-05's one-sided
      framing (the root cause test-agent named for why D-10 was missed, `IMP-0347`) is corrected in §10 —
      the row now states both directions and closes the negative one statically.
- [ ] All FR IDs covered — **improved, still partial**: FR-056 (landing shell) and FR-063 (finance figures)
      now built and rendering real data; FR-057/058 partial (`applicationsReceived` real, `applicationsPerDay`
      still `null`); FR-059–062 built against the full contract but render as absent (flow emits `null` for
      all of them today, by the flow's own declared first-version scope); FR-035's redacted-text half done
      (schema + UI); FR-035's structured `rev_careprovidedtype`/`rev_carehoursperweek`/`rev_applicanttype`
      half is unwired and flagged as an open question (§7, unchanged by this revision).
- [x] No hardcoded secrets
- [x] Security controls from TAD §6 implemented — Secure Outputs is applied to the flow's two row-reading
      actions (unchanged) and the new failure path carries no personal data (§6); not enforced as a repo-wide
      gate for the two pre-existing flows outside this WBS's scope (see §7, `IMP-0320`)
- [x] Every TAD §12 item has an idempotent provisioning script wired into `config/revitalise-grant-automation-pipeline.yml`
- [x] Role assignments via group teams only in Test/Acc/Prd — unchanged by this revision
- [x] No hardcoded environment-specific IDs/URLs
- [x] Every guessed platform contract is in §10 and commented in source — 9 rows total (`A-FLOW-01..05`,
      `A-LAND-1..4`); 8 OPEN, `A-LAND-1` CLOSED (revision 0.2); every OPEN one still carries its source
      marker (`verify-assumption-markers.py` PASS — re-run again this revision (0.3), **unchanged at
      14 OPEN/12 closed overall**: `A-FLOW-05` stays counted OPEN for the marker gate — one of its two
      claims settled statically this revision (§0.3, §10), the other genuinely still open — so neither the
      OPEN nor the closed count moves)
- [x] Ground truth used over guessing everywhere a live environment existed (schema fully V4; the flow's
      packaging and checker pass are V2 — the trigger/Response and failure-path shapes remain §10's
      A-FLOW-01/03/04/05; `rev_roundfinance` now has a generated Code App data source (§0.2, A-LAND-1
      CLOSED) — only the flow's (A-LAND-2) remains ungenerated, blocked on the flow going live)
- [ ] Every platform limit the packer/compiler does not enforce has a build gate — **known gap, unchanged**:
      the Secure Outputs check was built, found 6 pre-existing violations outside this WBS's scope, and was
      deliberately reverted rather than shipped as a build-breaking gate (Findings Logged, IMP-0320). **The
      gap this revision's own prior pass surfaced (`IMP-0329`) is now CLOSED**: improvement review 29 wired
      `scripts/verify-code-app-data-sources.py` into `config/revitalise-grant-automation-build.yml` as a HARD
      step ahead of typecheck/lint/tests/build, and this revision's fix is what makes it pass (5/5, was 5/4).
- [x] Verification levels in §11 are the levels actually executed
- [x] Scripts run on the CI runner's OS — no changes to that surface
- [x] Every tool warning triaged; no diagnostic components left in the solution
- [x] Accessibility requirements met for what is built — table-first charts (ADR-029), live region + `role`
      discipline for async/diagnostic states (§8.3), `data-print` extended to the new blocks (§8.2); contrast
      still rides on `theme.ts`'s placeholder ramp (A-R26, unchanged)
- [x] No dead code or debug statements
- [x] Unit tests written — code app: **372/372 passing, 21 files, 96.27% stmt/line coverage**, re-confirmed
      unchanged by this revision (up from 246/246, 16 files, 94.44% before the D-01/D-02 revision);
      provisioning: 874/875/1 skipped as of the prior revision — the one failure (`'verify-improvement-log
      --check' passes against the real log`) is **no longer expected to fail**: the backlog it was failing
      on was cleared by improvement review 29 (§7), and `python3 scripts/verify-improvement-log.py --check`
      now exits 0 when run directly (the exact command that Pester test invokes); the full 875-test Pester
      suite itself was not re-run this revision, which is scoped to the code app only

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`
