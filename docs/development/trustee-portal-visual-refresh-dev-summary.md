# Dev Summary Document — Trustee Portal Visual Refresh and Round-Statistics Landing Screen

**Feature Slug:** `trustee-portal-visual-refresh`
**TAD Reference:** `docs/architecture/trustee-portal-visual-refresh-architecture.md` — **Revision 7** built
this dispatch, on the reviewer's own dispatch instruction ("Yes please, combine into one build") rather than a
`APPROVED` reply recorded on the TAD document itself — the TAD's own header still reads "Not yet reviewed" as
of this reading; flagged here rather than silently treated as formally approved, and not a thing this document
edits (the TAD is `architect-agent`'s). Revision 7 adds **ADR-040** (a persistent view-switching nav bar),
**ADR-041** (the stat-tile grid widens with a container-query shrink-to-fit) and **ADR-042** (the heading
typeface adopts Playfair Display, self-hosted; the heading colour stays navy on explicit reviewer override),
closing **OQ-040**. §0.15 is this revision's own section. Revision 6, APPROVED as of revision 1.1 of this
document, adds **ADR-039** (the four money averages get a mechanism —
a guarded `xpath(xml(…),'sum(…)')`) and records the reviewer's answer to **OQ-043** (`k = 5`, the minimum
own-population at which a money average is published). Revision 5 and everything below it are unchanged. Revision 5 supersedes ADR-030 with **ADR-038** on live evidence: the flow becomes
Dataverse-row-triggered, the request/result slot splits into two tables so the trustee cannot write the
aggregate every trustee reads, and freshness becomes an age bound rather than a request identity. Revision 4
(design-system adoption, ADR-033–ADR-037) is unchanged and untouched by this dispatch. **One factual
correction to the approved text is reported rather than absorbed — §0.9.1: ADR-038's
`subscriptionRequest/message: 2` is Deleted, not Updated, and the flow ships `3`.** *(Revisions 0.1–0.7 below
were written against Revision 3 and 0.8 against Revision 4; all are left as they stand.)*
**Parent Dev Summary:** `docs/development/revitalise-grant-automation-dev-summary.md` — unchanged, not reproduced.
**Date:** 2026-08-25 · **revision 0.2 (`rev_roundfinance` Code App data source registered, A-LAND-1 closed)** 2026-08-26
· **revision 0.3 (D-10 fixed — `Respond_error` no longer fires on the success path)** 2026-08-26
· **revision 0.4 (two independent defect fixes: `rev_roundfinance` wired into the Grant Administration
model-driven app; a loading indicator added to the landing screen's "Refresh figures" control)** 2026-08-26
· **revision 0.5 (FR-035's remaining structured fields wired: type of break, the structured
care-support pair, applicant-type context, and a genuine OQ-031 total-funding-requested gap found and
fixed — closes the §7 gap this document itself flagged)** 2026-08-27
· **revision 0.6 (Amendment A-05 — the trustee detail screen now carries every remaining board-pack field:
nine unconditional Group A columns, the eleven Group B columns via ADR-032's build-derived field catalogue,
and the five new ADR-031 redacted counterparts)** 2026-08-27
· **revision 0.7 (the flow's second version — `genderDistribution`, `ageRangeDistribution`,
`applicantTypeDistribution`, `wellbeingLastYear`, `lifeSatisfactionDistribution` computed; and a
`blocker`-severity finding that the flow's own trigger mechanism is stale against a concurrent,
uncommitted redesign — §0.7)** 2026-08-27
· **revision 0.8 (TAD Revision 4 implemented in full: the supplied design system adopted as a typed
component and token layer, the applications list brought into scope for the first time, five contrast
corrections shipped, and the A-R38 stylesheet-loading risk closed with a falsified gate — §0.8)** 2026-08-27
· **revision 0.9 (TAD Revision 5 / ADR-038 implemented: the flow becomes Dataverse-row-triggered over a split
request/result pair, freshness becomes an age bound, two asserted disclosure properties become a HARD build
gate, the live DEV flow is captured and reconciled first — and the approved TAD's
`subscriptionRequest/message: 2` is corrected to `3` on live measurement — §0.9)** 2026-08-28
· **revision 1.1 (TAD Revision 6 / ADR-039 implemented: the four money-average measures composed with a
guarded `xpath(…,'sum(…)')`, the `k = 5` minimum-population disclosure gate read from `rev_setting`, three
app-side parsers moved to `{ value, population }`, `UR-002`/`UR-003` cleared — and TWO corrections to the
approved text reported rather than absorbed: ADR-039's literal expression is `NaN` on an empty subset, and a
HARD build gate rejected the approved mechanism — §0.12)** 2026-08-28
· **revision 1.2 (`IMP-0485` and `IMP-0486` closed: `rev_roundstatisticsresult` registered as a real Code
App data source and the interim stand-in deleted; `A-RESULT-1`/`A-FLOW-07`/`A-RES-1` close at E1; the
entire design-system conversion committed to `git` for the first time; two CSS defects fixed —
`.statTileValue` now wraps instead of overflowing, and the three filter `Select`s are re-sized to match
`ds/Input` — §0.13)** 2026-08-29
· **revision 1.5 (TAD Revision 7 implemented in full — `IMP-0510`: the persistent nav bar (ADR-040), the
wider shrink-to-fit stat-tile grid (ADR-041), the self-hosted Playfair Display heading face (ADR-042,
closes OQ-040 and A-R53 on real, OFL-licensed font files), the header-band padding correction (§0.10.1),
and the "Figures of this round" subheading (§0.10.2). Builds on the already-committed `IMP-0509` line-height
fix rather than redoing it. A-R54 (container-query support) verified in real Chromium via Playwright, not
in the host's own WebView2 — stays open exactly where TAD §12.2 put it — §0.15)** 2026-08-30
**Status:** DRAFT
**WBS:** `6.1`, `6.2`, `6.3`, `6.5` (accepted, `contract/wbs.json`), `6.9` (created by `contract/change-orders/CO-001.md`,
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

### 0.5 This revision — FR-035's remaining structured fields wired: type of break, care-provided type,
care hours per week, applicant-type context (reviewer directive, 2026-08-27, `wbs:6.3`)

**Closes the exact gap this document itself flagged in §7:** *"TAD §3.2 describes `rev_careprovidedtype`,
`rev_carehoursperweek` and `rev_applicanttype` as 'already shipped' and trustee-visible, but none of the
three is actually wired anywhere in `trustee-review-portal` today."* The reviewer's instruction that
triggered this revision — *"the trustee portal application detail screen is still missing some
information, look at the round 4 individual applications pdf, include all of those fields"* — is read as
authorising exactly the already-approved FR-035 field list (Amendment A-02,
[`docs/plans/revitalise-grant-automation-plan.md:203-213`](../plans/revitalise-grant-automation-plan.md#L203)),
not literally every PDF field: Amendment A-02 Finding 1
([`plan.md:186-197`](../plans/revitalise-grant-automation-plan.md#L186)) already adjudicated the rest of
the PDF field-by-field, and that adjudication is unchanged and unrevisited by this revision.

**Four fields, all schema-only work — no new Dataverse column, no new role grant.** All three source
columns were already live on `rev_application`/`rev_applicant` from an earlier pass (§3 above), all three
already `IsSecured=0`, and the tables that carry them were already fully readable by `REV Trustee`. The gap
was entirely in the code app: nothing read or rendered them.

1. **Type of break (`rev_breaktype`)** — already read into `ApplicationDetail.breakType`
   ([`types.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/types.ts):81) and
   `BREAK_TYPE_LABELS` already populated
   ([`schema.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/schema.ts):303). Only
   `HolidayPanel` never rendered it —
   [`CasePanels.tsx`](../../src/code-apps/trustee-review-portal/src/components/CasePanels.tsx):105 now
   does, as the first `Definitions` row, matching the PDF's own field order.
2. **The structured care-support pair (`rev_careprovidedtype`, `rev_carehoursperweek`)** — new columns in
   `ApplicationDetail`, `APPLICATION_DETAIL_EXTRA_COLUMNS` and `mapDetail()`
   ([`types.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/types.ts):98-114,
   [`schema.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/schema.ts):111-138,
   [`repository.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/repository.ts):101-126). Two
   new label maps, transcribed from `OptionSets/rev_careprovidedtype.xml` (11 options) and
   `OptionSets/rev_carehoursband.xml` (5 bands) and re-derived from the same source in
   `schema.test.ts`, per this app's own `IMP-0019`/`IMP-0330` convention rather than trusted by eye.
   Rendered in `CareSupportPanel`, **unconditionally** — not behind `careSupportState`'s
   `redactionReleased` gate, which stays exactly as it was for the three `…redacted` free-text columns.
   TAD §3.2 states the basis directly: both are `IsSecured=0` structured facts, the same basis
   `rev_amountrequested` already renders unconditionally on.
3. **Applicant-type context (`rev_applicant.rev_applicanttype`)** — resolved to be exactly the column TAD
   §3.2 names (the PDF's "Are you...?" field, three options, confirmed against the live form 2026-08-16),
   correcting Amendment A-02 Finding 1's own note that no column "corresponds cleanly" — that note
   predates the TAD's correction and is superseded by it, not contradicted. Read via a NEW, detail-only
   applicant query (`APPLICANT_DETAIL_COLUMNS` = `APPLICANT_REGION_COLUMNS` + `rev_applicanttype`,
   [`schema.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/schema.ts):179-197) and a new
   `resolveApplicantDetail()` in
   [`repository.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/repository.ts):238-267 — a
   single-id `getRecord` read, not a widening of `resolveRegions()`/`APPLICANT_REGION_COLUMNS`, so the
   SUMMARY list's own applicant query is untouched and stays at its documented two columns. Rendered in
   `CareSupportPanel` alongside the structured pair, not on its own panel: applicant type is what makes
   "type of care provided"/"hours of support per week" legible (self-care vs. care given to someone else),
   so the three read as one topic to a trustee.

**New assumption, `A-TR-13` (§10).** `rev_careprovidedtype` is a `multiselectpicklist`; Dataverse's Web
API convention returns it as a comma-separated string of option values over OData, but this has not been
observed live through this app's connector — the same unverified-connector-shape class as `A-TR-7`. A new
`asNumberArray()` helper
([`odata.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/odata.ts):53-77) accepts either
that string or an array of numbers, marked `A-TR-13` at the point of the guess, per `C-TECH-052`.

**Explicitly not reopened — Amendment A-02 Finding 1's other adjudications stand.** Financial eligibility
(§7.1, special category, never shown), the condition/illness checklist and health narrative (FR-016/031),
helper/referee/emergency-contact details (FR-036), and `rev_unabletofundexplanation`/the
exceptional-circumstance detail/amount columns (**`OQ-011` stays OPEN** — this revision does not read today's
reviewer instruction as also resolving it, and says so here rather than guessing) are all unchanged. The
wellbeing/"last 2 weeks"/"last year" survey item-by-item breakdown stays exactly as Finding 1 left it —
"unverified, not a confirmed gap" — because this revision did not get access to a live DEV record's
`rev_scorebreakdown` content to check what it actually reproduces; that check is still open, not performed
here, not assumed either way.

**Total funding requested (OQ-031) — checked, and it was NOT actually satisfied. Fixed, not merely
confirmed.** The handoff asked to verify whether the existing "Amount requested" + "Total costs" two-line
render already satisfied FR-035's adopted wording — *"the total funding requested for the grant round,
including any exceptional funding requested"* — or needed collapsing to one figure. It did not: neither
`rev_additionalamountrequested` (the exceptional-funding top-up) nor `rev_exceptionalfundingrequested` (the
flag TAD §3.2 names) was read anywhere in the app, so "Amount requested" silently excluded any exceptional
top-up whenever one existed — a real, if narrow, gap in an already-approved FR-035 field, not new scope.
Fixed: both columns added to `ApplicationDetail`
([types.ts](../../src/code-apps/trustee-review-portal/src/dataverse/types.ts):83-93) and
`APPLICATION_DETAIL_EXTRA_COLUMNS`
([schema.ts](../../src/code-apps/trustee-review-portal/src/dataverse/schema.ts):130-131); a new
`totalFundingRequested()` helper
([domain/format.ts](../../src/code-apps/trustee-review-portal/src/domain/format.ts)) sums them
unconditionally, per the TAD's own wording that the flag is "so the total is explicable rather than just
larger" — not an arithmetic gate. `HolidayPanel` now shows one "Total funding requested" line plus an
"Includes exceptional funding" Yes/No line, replacing the old "Amount requested" line
([CasePanels.tsx](../../src/code-apps/trustee-review-portal/src/components/CasePanels.tsx):133-166).
**`rev_costs` ("Total costs") is deliberately KEPT, not removed:** TAD §3.1 classifies it as an FR-060
column (the round-level cost aggregate), not FR-035's — it was already on the screen from an earlier,
separate decision, and removing already-shown information was not asked for by anything in this dispatch's
scope. Both new columns are `IsSecured=0` and already TAD §3.1-classified as FR-035-visible (Tier 3, no
security), so no new role grant or `A-nnn` guess was needed — this is application logic over
already-ground-truthed schema, not a new platform contract.

**Verification, this revision.** `npm run typecheck` / `npm run lint` / `npm test -- --coverage` in
`src/code-apps/trustee-review-portal` — all clean: **460/460 tests across 24 files, 98.37% statement/line
coverage** (92.91% branches, 94.27% functions — all above the 80% bar), up from the prior 372/372, 21
files, 96.27%. `python3 scripts/verify-code-app-column-bindings.py src/code-apps/trustee-review-portal
src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml` → OK, unchanged (all five new
columns are `IsSecured=0`, so the forbidden set — derived from `FieldSecurityProfiles.xml` — does not
grow). `python3 scripts/verify-assumption-markers.py` → PASS, `A-TR-13` present with its marker
(`odata.ts:53`). `python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml` and
`python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml` → both PASS,
unchanged — this revision is a pure code-app source change against already-live, already-unsecured
columns; no build or pipeline config edit is needed. No live Code App push was performed (V2 only — see
§11); no new Dataverse schema, role grant or provisioning step, so there is nothing for a live push to
verify beyond what §11 already lists as open for the rest of this feature.

**A second, unrelated pre-existing issue this revision's own `C-TECH-066` constraint check surfaced and
fixed, not caused.** `python3 scripts/verify-tad-coverage.py` FAILED: `contract/tad-deferrals.json`'s
`TD-005` (deferring `rev_applicant.rev_ethnicgroup` pending SDD OQ-027) matched no absent TAD column,
because a concurrent session had already built `rev_ethnicgroup` live in `Entities/rev_applicant/Entity.xml`
(`IMP-0363`) without deleting the now-satisfied deferral entry. Fixed per that file's own documented
`_stale_entries_fail` procedure — the identical one WBS 0.4 used for `TD-001`–`004`/`TD-009` in an earlier
pass — by deleting `TD-005` and recording the clearance in the file's own `_not_deferred` note. Re-run:
`verify-tad-coverage.py` → **OK**. Not this dispatch's own deliverable and not billed to `wbs:6.3` — logged
as `IMP-0366` (`stale-deferral-uncaught-across-sessions`, friction) since the underlying gap (nothing
prompts a schema-adding session to reconcile `contract/tad-deferrals.json` in the same change) is a real,
reusable lesson, not routine gate operation.

**A pre-existing, unrelated tooling gotcha surfaced and resolved during this revision's OWN verification,
not a defect in the code above.** `npm test` initially failed 7 suites (none of them touched by this
revision) with `Cannot find module '.../dist/data/multiSelectPicklistUtils'` — the exact symptom
`vitest.config.ts`'s own `server.deps.inline` comment already documents fixing. The cause was a stale
`node_modules/.vite` dependency-optimization cache, not a regression: deleting it and re-running made all
24 suites pass clean on the genuinely untouched `node_modules`. Logged as `IMP-0365`
(`stale-tool-cache-masquerades-as-real-defect`, `friction`) so the next session does not spend the same
time re-diagnosing it as an unfixable upstream package defect.

**Scope check.** `wbs:6.3` — the same task this whole FR-035 field list already belongs to (per the
`HANDOFF` that dispatched this revision). No change-order routing needed (`C-COM-002`): closing a
documented gap in an already-accepted task's own field list is not new scope.

**Hours proposal — addendum for `commercial-agent` behind `APPROVE TIMESHEET`.** No figure from
`contract/wbs.json` or `contract/service-agreement.json` is restated here (`C-COM-008`):

| WBS | Proposed actual | Evidence |
|---|---|---|
| `6.3` | 1.4 h | Four fields wired across `types.ts`/`schema.ts`/`repository.ts`/`odata.ts`/`CasePanels.tsx` (one new detail-only applicant read, one new multiselect parser, two new option-set label maps re-derived from source), plus a genuine OQ-031 gap found on inspection and fixed (`domain/format.ts`'s `totalFundingRequested()`, two more columns wired), 5 test files extended (`odata.test.ts`, `schema.test.ts`, `CasePanels.test.tsx`, `repository.test.ts`, `format.test.ts`), full typecheck/lint/460-test verification, one pre-existing HARD constraint violation found and fixed (`C-TECH-066`/`TD-005`, unrelated to this WBS task — see below), one unrelated stale-cache diagnosis, two improvement-log entries, and this Dev Summary's §0.5/§7/§9/§10/§11/Findings/Checklist updates |

A proposal for `commercial-agent` to confirm, not a booking.

---

### 0.6 This revision — Amendment A-05: every remaining board-pack field (2026-08-27)

**What the reviewer's own words settled, and what this dispatch had to derive.** Amendment A-05 reverses
A-02's three data-minimisation exclusions and adds FR-078/FR-079; the TAD (Revision 3) resolves them into
three groups per SDD §7.1b, and ADR-031/ADR-032 decide the two genuinely new mechanisms. This dispatch
implements exactly those three groups on the app side — no schema change (Entity.xml is already architect-
agent's, Revision 3) — and adds the one build-time mechanism ADR-032 asks for but does not build itself.

**Group A — nine columns, `IsSecured=0`, bound and rendered unconditionally**, the same basis as
`rev_amountrequested` on `HolidayPanel`: `rev_incomeflag`, `rev_incomeband`, `rev_savingsover6000`
(`FinancialEligibilityPanel`, new); `rev_conditionprofile`, `rev_supportrecipientconditionprofile`
(`ConditionProfilePanel`, new — reuses the `optionLabels`/`asNumberArray` pattern `careProvidedType` already
established, one shared option set for both columns); `rev_helperorganisation`, `rev_helperrelationship`,
`rev_helperdeclarationconsent`, `rev_helperdeclarationconsentdate` (`HelperRefereeContactPanel`, new). The
two tri-state booleans (`rev_savingsover6000`, `rev_helperdeclarationconsent`) needed a new wire-format
helper, `asNullableBoolean()` (`dataverse/odata.ts`) — deliberately **not** `asAffirmativeBoolean`, which
exists only for the two visibility-gate columns and collapses everything short of an affirmative `true` to
`false`. Both source columns' own `Entity.xml` descriptions state that an absent answer is normal and must
stay distinguishable from an explicit "No", so `asNullableBoolean` returns `true`/`false`/`null` and a new
`formatYesNo()` (`domain/format.ts`) renders the three states as "Yes"/"No"/`NOT_RECORDED`. Neither reads a
new platform wire shape: both source columns are `bit`, the same type `rev_eligibleforround` already
proves the true/false/1/0/"true"/"false" convention against, so no new §10 row is needed for the shape
itself.

**Group B — eleven secured columns, never queried, rendered from a build-derived catalogue (ADR-032).**
Benefit status, employment status, and the eight helper/referee/emergency-contact identity columns are all
`IsSecured=1` inside `REV_TrusteeRestricted`. ADR-032's whole point is that this app must not bind them —
the process owner IS a profile member, so a bound query would show her their real values on a screen
designed to be anonymous, and `no-secured-columns-in-code-app` (HARD) would fail the build on the reference
regardless. `scripts/generate-trustee-field-catalogue.py` (new) reads `Other/FieldSecurityProfiles.xml` and
`Entities/rev_application/Entity.xml` at generation time — the identical technique the build gate itself
already uses for its forbidden set — and validates a short, owned eleven-entry manifest against them: each
column must still be secured under `REV_TrusteeRestricted`, and each label is read from the column's own
`<displayname>`, never hand-typed. It fails loudly (not silently) if either check no longer holds. The
generated output, `src/generated/trusteeRestrictedFieldCatalogue.ts`, deliberately carries **no Dataverse
logical column name at all** — only a stable `key`, a `label`, a `group` and `restricted: true` — which is a
stronger property than merely sitting in a directory the security gate excludes from its scan: the shipped
app bundle never contains the eleven forbidden strings anywhere, in any form. `domain/fieldCatalogue.ts`
(new, hand-authored) turns a group name into `Definitions` rows sharing one FR-078 sentence
(`RESTRICTED_VALUE_TEXT`). `FinancialEligibilityPanel` renders its three; `HelperRefereeContactPanel`
renders its eight; `ConditionProfilePanel` renders none — every secured column in that board-pack group is
free text with a redacted counterpart (Group C, below), not a Group B identity column, which the SDD's own
§7.1b table shows and this pass's tests assert (`fieldCatalogue.test.ts`).

**Group C — the five further redacted counterparts ADR-031 adds**, wired exactly like the three existing
care-support ones: gated by `rev_redactionreleased`, three first-class states (`withheld` /
`released-empty` / `released`), reusing `careSupportState`'s exact shape and reasoning. Two new
`domain/visibility.ts` functions carry them — `financialFreeTextState` (one column, on
`FinancialEligibilityPanel`) and `conditionFreeTextState` (four columns, on `ConditionProfilePanel`) —
rather than widening `careSupportState` itself, because the five belong to two different board-pack panels,
not one. Every one of the five renders `NarrativePanel`'s convention: today, on every row, as "not yet
redacted" — `rev_redactionreleased` is false on every row and Automation #5 (`wbs:5.2`) remains deferred
(`EX-003`) — never as an empty value and never as "not recorded".

**A defect found and fixed that predates this dispatch, not caused by it.** Running the full suite before
presenting this gate (per this agent's own activation instructions) surfaced
`repository.test.ts`'s `"resolves the region on the detail path too"` failing. Root cause: an EARLIER pass
in this same dispatch chain (the revision 0.5 work that added `resolveApplicantDetail`, §0.5) replaced the
detail screen's applicant read from a `listRecords`-based call to a `getRecord`-based one, so `getApplication`
now calls `getRecord` TWICE — once for the application row, once for the applicant row — but this one test
still mocked only `getRecord.mockResolvedValue(...)` once (answering both calls with the same
application-shaped object) and separately mocked the now-unused `listRecords`. The mock mismatch, not the
product code, was wrong: fixed by chaining `.mockResolvedValueOnce(...)` twice, matching the real call
order. Logged as `IMP-0375` below (a second, later change silently invalidating an earlier test's own
mocking assumption — `IMP-0111`'s class, from the other side).

**What this pass does not touch, per the TAD's own instruction (§3.2.2/§3.2.3, this document's §0 header
convention) and per the reviewer's directive at the top of this dispatch:** no `Entity.xml` edit (already
architect-agent's, Revision 3); no change to any column's `IsSecured` value or profile membership; no
change to `FieldSecurityProfiles.xml` beyond what architect-agent already committed; `rev_exceptionalcircumstance`
stays exactly as wired before this pass (it is pre-existing FR-059/round-statistics scope, unsecured, and
SDD §7.1b's row about it documents existing state rather than asking for new wiring — confirmed by grep
before this pass began, not assumed).

**Scope check.** `wbs:6.3` — the same task FR-035/FR-078/FR-079 already carry (SDD §7.1b, TAD §3.2.2/§3.2.3
Serves column). No change-order routing needed (`C-COM-002`): this is the continuation the reviewer's own
"Build" directive authorised for the same task, not new scope.

**Hours proposal — addendum for `commercial-agent` behind `APPROVE TIMESHEET`.** No figure from
`contract/wbs.json` or `contract/service-agreement.json` is restated here (`C-COM-008`):

| WBS | Proposed actual | Evidence |
|---|---|---|
| `6.3` | 2.6 h | Fourteen columns wired across three new panels (`FinancialEligibilityPanel`, `ConditionProfilePanel`, `HelperRefereeContactPanel`), one new build-time generation script plus its generated output and build-config wiring (ADR-032), two new `domain/visibility.ts` state functions, one new tri-state boolean helper and one new formatter, one new `domain/fieldCatalogue.ts` module, eight test files new or extended (`odata.test.ts`, `format.test.ts`, `visibility.test.ts`, `schema.test.ts`, `repository.test.ts`, `CasePanels.test.tsx`, `ApplicationDetailPage.test.tsx`, `fieldCatalogue.test.ts` — new), one pre-existing test/implementation mismatch found and fixed (unrelated to this pass's own product code), full typecheck/lint/coverage re-verification, and this Dev Summary's §0.6/§1/§2/§6/§7/§8/§9/§10/§11/Findings/Checklist updates |

A proposal for `commercial-agent` to confirm, not a booking.

---

### 0.7 This revision — the flow's second version, and a `blocker` finding read before writing a line of it

**Read first, because it changes what "done" means for this dispatch.** This dispatch's own handoff
scoped the work to five metrics inside `Compute_statistics` — `genderDistribution`, `ageRangeDistribution`,
`applicantTypeDistribution`, `wellbeingLastYear`, `lifeSatisfactionDistribution` — against TAD ADR-030/§5.1's
PowerApps-trigger/`Response` design. That work is done and verified (below). But activation step 0 of this
agent (`logs/known-failure-modes.md`) and this agent's own habit of reading the Code App source the handoff
pointed at (`src/code-apps/trustee-review-portal/src/dataverse/roundStatistics.ts` — the handoff's own
instruction was "verify that claim against the current source rather than assuming it's still true") surfaced
something the handoff did not know: **the flow this dispatch was asked to extend cannot currently be invoked
by the Code App at all, regardless of this dispatch's own changes.**

`logs/improvement-log.jsonl` `IMP-0358`/`IMP-0359`/`IMP-0365` record the `shared_logicflows`/PowerApps-V1-
trigger mechanism ADR-030 chose crashing the Code App's boot ("The app didn't start correctly"), reproduced
twice, independently, in private-session tests. `IMP-0359`'s own lesson: do not re-attempt it without a
genuinely new variable. A concurrent, **uncommitted** session has since abandoned that mechanism entirely —
confirmed live in this working tree, not inferred: `git status --porcelain` at this dispatch's activation
showed `roundStatistics.ts` modified and `Entities/rev_roundstatisticsrequest/` +
`provisioning/dataverse/seed-round-statistics-request.ps1` untracked, none of it touching `HEAD` (`5b8b985`).
`roundStatistics.ts`'s own rewritten header describes the new design in full: the app now writes
`rev_triggeredon` onto a single, ever-present `rev_roundstatisticsrequest` row and polls it for
`rev_status`/`rev_resultjson`/`rev_computedon`, expecting a **Dataverse-row-triggered** flow to compute in
the background and write those three columns back — not a synchronous Power-Apps-triggered call at all.
**No flow JSON anywhere in this solution references `rev_roundstatisticsrequest`, `rev_triggeredon` or
`rev_resultjson`** (grepped, clean) — the flow side of this redesign has not been started by anyone.

**What this dispatch did about it.** Logged as `IMP-0377` (`blocker`) rather than fixed unilaterally: rewriting
the flow's trigger and response mechanism is an architecture decision (ADR-030 needs a superseding ADR, the
same way ADR-030 itself superseded ADR-025), not a continuation of the approved design this dispatch was
handed, and it would mean hand-authoring a brand-new, never-before-used trigger shape
(`Dataverse row-modified`, writing back via `UpdateRecord` rather than responding via `Response`) directly
inside a dispatch scoped to metric computation — exactly the kind of unscoped, un-reconciled work `C-COM-002`
exists to stop. **The metric work below is deliberately additive and self-contained**: every new action sits
inside the existing `Compute_statistics` Scope, and the trigger/`Response`/failure-path outer shell is
byte-for-byte unchanged from the FIRST VERSION, specifically so it carries over cleanly to whichever trigger
shape the superseding ADR eventually chooses, and so this dispatch's own uncommitted work does not collide
with the concurrent session's. **The flow, with or without this revision's changes, is not yet reachable by
the Code App.** Closing that is the next thing this feature needs, and it is architect-agent's decision, not
this dispatch's to make.

**The five metrics, in outline** (full account: the flow's own `.notes.md`, "SECOND VERSION" section).
`rev_wellbeinganswer8/9/10` and `rev_feelingscaleanswer` live directly on `rev_application` — no join needed.
`rev_gender`/`rev_agerange`/`rev_applicanttype` live on `rev_applicant`, reached from `List_applications_in_round`
via a new `$expand=rev_applicantid($select=rev_gender,rev_agerange,rev_applicanttype)` parameter — **ground-
truthed live against DEV this session**, not guessed: the lookup's navigation property name
(`rev_applicantid`, identical to its own logical name) was read from
`EntityDefinitions(LogicalName='rev_application')/ManyToOneRelationships`, and the exact nested-object shape
`$expand` returns was confirmed with a live `rev_applications?$select=...&$expand=rev_applicantid($select=
rev_gender,rev_agerange,rev_applicanttype)&$top=2` call. What remains unverified is narrower and named —
**`A-FLOW-06`** (§10): whether the `List rows` connector's `OpenApiConnection` action accepts a literal
`"$expand"` parameter key the same way it already accepts `"$select"`/`"$filter"`/`"$top"` in this exact
action, which no flow in this solution has exercised before. Tallying uses 46 `Query`-type (Filter array)
actions, one per category value across the five metrics — matching TAD A-R36's own "~40 array expressions"
estimate — because the TAD's own suggested `length(filter(...))` phrase is wrong against this project's
already-ground-truthed `IMP-0124` (no `filter()` expression exists; Filter array is an action). **A real
defect was found and fixed before shipping, not accepted on faith**: logged as `IMP-0378` (`friction`) —
`if()` in this language evaluates all three arguments eagerly (Microsoft's own docs: "Parameters are
evaluated from left to right"), so a first-draft zero-population percentage guard still divided by zero;
fixed with `max(population,1)` as the divisor, verified by writing a small evaluator for the exact expression
text this file ships and running it against both a realistic 271-row synthetic round (every category sums to
population, minus deliberately-injected nulls) and a genuinely empty one (every category resolves to
`count:0`/`percentage:0`, no error). A third finding, unrelated to this dispatch's own correctness — `IMP-0379`
(`friction`) — records that TAD §3.4/A-R24 ("`rev_ethnicgroup` was deliberately never built", quoted by this
dispatch's own handoff) is now stale against the same document's own §12.1 warning box and against
`Entity.xml`, both of which confirm the column was built on 2026-08-27 to resolve SDD OQ-027; only the field
permission is still missing. `ethnicGroupDistribution` stays `null` regardless — out of this dispatch's scope
either way — but the next reader of §3.4/A-R24 alone should not conclude no path exists.

**Hours proposal — addendum for `commercial-agent` behind `APPROVE TIMESHEET`.** No figure from
`contract/wbs.json` or `contract/service-agreement.json` is restated here (`C-COM-008`):

| WBS | Proposed actual | Evidence |
|---|---|---|
| `6.9` | 3.1 h | Five metrics computed across 46 new Filter-array actions + 8 assembling Compose actions (54 new actions total) inside the existing `Compute_statistics` Scope, one modified `List_applications_in_round` (`$select`/`$expand`), one rewritten `Compose_response_body`; ground-truthed live against DEV (the `$expand` navigation property name and its exact nested shape, two independent live Web API calls) rather than guessed; a hand-built expression evaluator written and run twice (realistic-data and zero-population) to prove the shipped expression text — not just its JSON shape — before any import; `pac solution pack` (both package types) and the hosted Solution Checker (0/0/0/0/0) re-run clean; `verify-flow-definition-language.py`/`verify-field-length-limits.py`/`verify-assumption-markers.py` all re-run; one `blocker`-severity architecture finding (`IMP-0377`) investigated, evidenced and logged rather than either ignored or fixed out of scope; two further findings (`IMP-0378`, `IMP-0379`) logged; this document's §0.7/§1/§2/§4/§7/§10/§11/Findings/Checklist updated |

A proposal for `commercial-agent` to confirm, not a booking.

---

### 0.8 This revision — TAD Revision 4: the supplied design system, adopted in full (2026-08-27)

**What was authorised.** The reviewer replied `APPROVED` to TAD Revision 4 (`logs/routing.log`, 22:25). Two
open brand-authority questions resolved to their stated defaults on reviewer silence — the heading colour
stays the supplied navy `#002060` (OQ-040) and the brand pink stays the supplied `#ED008C` (OQ-041) — and the
recommended-default question resolved to **REFUSED**: no licensed display serif is sourced, headings stay in
the supplied sans stack, and **ADR-036 (no Google Fonts import, no CDN font loading) is binding, not
optional**.

**What changed, in one sentence: the app gained a typed design-system component and token layer, and eleven
screens and components were restyled onto it. No query, no `$select`, no schema, no role, no flow and no
column changed — not one.** That is Revision 4's own stated boundary and this revision holds it exactly:
nothing under `src/domain/` or `src/dataverse/` was opened, and the `Entity.xml` tree was not touched.

**The four decisions this pass made that were not spelled out for it.**

| # | Decision | Why |
|---|---|---|
| **1** | **`ds-tokens.css` copies the design system's `:root` blocks and NONE of `tokens/effects.css`'s element rules.** That file also carries `body{…}`, `h1,h2,h3,h4{…}`, `a{…}` and `*{box-sizing:border-box}` after its custom properties | Copying them would fight `brand.css`'s own `h1..h6` rule (which applies the supplied heading font and the 44px title), restyle every Fluent link, and change box-sizing app-wide. §2.1.2 asks for the custom properties; a verbatim file copy would have taken four element rules with them. Now asserted — `ds-tokens.test.ts` fails on any selector in that file other than `:root` |
| **2** | **The brand alias values are pinned to `theme.ts`'s ramp by import, not by a retyped hex.** `--brand-primary`/`-hover`/`-active` are asserted equal to `brandRamp[70]`/`[60]`/`[30]` | ADR-037 correction 1 routes the button ladder through the *supplied* sixteen-shade ramp. Two files naming the same colour is the drift risk `theme.test.ts` already guards for `brand.css`; the same guard now covers the second stylesheet |
| **3** | **`.chartBar`'s fill token is UNCHANGED.** §8.5 point 4 first lists the fill as one of two things that change, then states plainly *"The fill stays `var(--colorCompoundBrandBackground)`"* — an internal tension in the approved text, resolved in favour of the explicit sentence | That token is `brand[80]` at 4.22:1 against white (clearing the 3:1 UI-graphic floor), its arithmetic is documented at `app.module.css`'s own `.chartBar` comment, it is pinned by `theme.test.ts`, and `print.css` forces it to `#000` on paper. Changing it would have moved a documented, tested contrast decision to no requirement's benefit. **Flagged for the reviewer** rather than silently chosen |
| **4** | **Fluent's `Radio` is KEPT, against §2.1.4's table, which lists it as replaced.** Measured, not assumed | `RadioGroup` publishes `name` and the derived `checked` through a React context only Fluent's own `Radio` consumes. Rendering three `ds/Radio`s inside one `<RadioGroup value="2">` yields `name` of `null` on all three and `checked` false on all three, against `["radiogroup-r1",…]` and `[false,true,false]` for Fluent's. The shared `name` is what the *browser* uses for single-selection, arrow-key traversal and the roving tabindex, so a look-alike child loses all three (WCAG 1.3.1, 2.1.1, 4.1.2) — and because the group's root still fires on any bubbled change, the verdict would appear to register on the first click and then diverge from state. **A partly-working control, not a visible break**, which is the worst kind. §2.1.4's table cell needs correcting; `VerdictForm.tsx` carries the measurement and its test now pins the properties rather than the implementation, so a future `ds/Radio` that reads the context would pass |

**The one risk the TAD flagged as highest-impact is closed, and the gate was falsified before it was
trusted.** A-R38 predicted that a new global stylesheet imported only from `main.tsx` would leave hundreds of
tests asserting markup the running app never produces, because the test harness never loads it. Both halves
are now in place and, more importantly, **both halves can now fail**:

- `ds-tokens.css` is side-effect imported from `main.tsx` and from `src/test/harness.tsx`.
- `ds-tokens.test.ts` reads both new stylesheets off disk and computes the contrast arithmetic — the same
  technique `theme.test.ts` and `print.test.ts` already use, and the only one that works here, because
  `vitest.config.ts` sets no `css` option, so **vitest processes no CSS import at all and jsdom resolves no
  `var()`**. The harness import keeps the two module graphs identical and proves nothing further; that is
  stated in the file rather than left to be assumed.
- **The gap that mitigation still left open was closed in this dispatch.** Every token assertion reads the
  file off disk, so deleting the `main.tsx` import would have left all of them passing while the running app
  rendered every `var(--space-6)` as nothing — A-R38's exact failure mode, invisible to A-R38's own
  mitigation. Three assertions now cover the import itself, and one covers ADR-034's locational boundary
  (nothing under `src/` may resolve a reference into `Designsystem/`). All four were verified by mutation:
  deleting the `main.tsx` import fails 3 tests, deleting the harness import fails 2, and a real ES import or
  CSS `@import` from the design system's directory fails 1 each. A guard nobody has broken on purpose is a
  guess, and this project has recorded "a gate that cannot fail" 33 times.

**The five contrast corrections shipped, and each one is now a test rather than a paragraph.** Every ratio was
recomputed with the WCAG 2.1 formula before being pinned, and all nine of the TAD's stated rows reproduced.
One did not: the design system's warning-tone title measures **3.16:1**, not the 3.18:1 §8.4.1 states. It
changes no decision — correction 5 does not ship that tone at all — and is recorded rather than acted on.

**Pairings the TAD did not enumerate were checked before shipping, not assumed from ADR-037.** The supplied
navy passes on all six design-system surfaces (15.27 · 14.28 · 13.21 · 12.66 · 12.73 · 13.90), and the
corrected link colour passes on all six too, with its thinnest margin at **4.54:1 on `--surface-band`** —
comfortably above the floor but worth knowing, because it is the pairing a future surface change would break
first. Both are pinned per-surface rather than against white alone.

**WBS 6.2 entered scope for the first time and its eight tested behaviours all survive.** The supplied mockup
for that screen has five hardcoded rows, no loading state, no error state, no empty state, no sorting, no
filtering and no live region; where it and the shipped behaviour disagreed, the shipped behaviour won every
time. The four `useMemo`s that filter and sort over the complete round are byte-identical, there is no paging
control because there is no paging, the 500-row truncation still fails loudly through the generic error path,
both distinct empty states are still distinct, the live region and its wording-switching caption are intact,
and row navigation is still a `<button>` rather than the mockup's `<a href="#">`.

**The two security-critical rendering controls are held, and one is now visibly better.** The three-state
redaction rendering is wired through a single mapping function used by all four panels, so `withheld` and
`released-empty` take two different visual treatments instead of collapsing into one grey box — which is what
§8.5 point 1 asks for, because *"you may not see this"* and *"this has not been scrubbed yet"* are different
facts about Article 9 data. The FR-078 restricted-field catalogue is untouched: its build-time generator, its
build step and its output are unchanged, `Definitions` keeps its `<dl>`/`<dt>`/`<dd>` markup, and the
mockup's `<div><strong>…</strong><span>…</span></div>` — which is not a programmatic label-value association
at all — was **refused** rather than adapted. The tests that pin those two controls (the exact
`released-empty` sentence, that it does not contain the word "withheld", and the catalogue's 3 and 8 row
counts) pass **unmodified**.

**No `config/revitalise-grant-automation-build.yml` or `-pipeline.yml` change is needed, and that is a
finding rather than an omission.** The new drift guard runs inside the existing HARD `code-app-unit-tests`
step, which invokes `npm run coverage` — so both the assertions and the 80/80 coverage threshold already
gate it. Adding a second build step naming the same test file would be a gate that duplicates a gate. The
`no-secured-columns-in-code-app` step needed no widening either: it derives its forbidden set from
`FieldSecurityProfiles.xml` at check time and now passes over **99** authored files (up from 97) against 63
forbidden columns, with the new stylesheets and seven components inside its scanned extension set.

**Hours proposal — addendum for `commercial-agent` behind `APPROVE TIMESHEET`.** No figure from
`contract/wbs.json` or `contract/service-agreement.json` is restated here (`C-COM-008`):

| WBS | Proposed actual | Evidence |
|---|---|---|
| `6.1` | 4.4 h | The design-system layer: seven `.jsx` prototype components converted to typed, linted, 100%-covered `.tsx` modules with a barrel; two new stylesheets (`ds-tokens.css` 336 lines, `ds.module.css` 449 lines) with ADR-037's five corrections applied and commented at the values they change; the nine supplied contrast rows independently recomputed and six further un-enumerated pairings measured across all six surfaces before shipping; a 33-assertion disk-read drift guard written and falsified eleven ways by mutation (seven by the implementing session, four by this one) rather than trusted green; `main.tsx`/`harness.tsx` wiring for A-R38 plus the three assertions that close the half A-R38's own mitigation left open |
| `6.2` | 1.6 h | The applications list restyled against the design system for the first time — filters onto the converted `Input` with all six external `<Label htmlFor>` pairings preserved, action buttons onto the converted `Button` with the 44px target the mockup's `size="sm"` would have lost, table rule/header type/row padding moved into the stylesheet so **no line of the table's markup changed**, and the error state re-rendered through the new `Notice` with `role="alert"` supplied by the call site because the component deliberately sets none; each of §2.2.1's eight behaviours re-verified against its existing test rather than assumed |
| `6.3` | 1.2 h | The eight detail-screen panels restyled; the three-state redaction rendering given two visually distinct tones through one shared mapping function typed against `visibility.ts`'s own union (so a fourth state would be a compile error, not a silently-defaulted box); the FR-078 catalogue and `Definitions`' `<dl>` markup held against a mockup that would have destroyed both; `A-DS-1` opened and marked in source |
| `6.9` | 0.9 h | The landing screen and finance panel restyled; `StatTileRow` re-implemented over the converted `StatTile` keeping its `{label,value}[]` contract and its `<dl>`, with a new `absent` state so "Not recorded" stops being typeset as a 32px display figure; the two screens' deliberately **opposite** null behaviours preserved and re-tested; `DistributionChart`'s markup, ARIA and geometry left byte-identical with only its chrome restyled |

A proposal for `commercial-agent` to confirm, not a booking. Two commercial items are flagged in the TAD and
neither is resolved here: **A-R43** (6.2's accepted hours were quoted to *build* the list screen, not to
restyle it) and **A-R28** (CO-001-A1's sizing basis). Both are `commercial-agent`'s call and should land in
one re-confirmation. No figure is restated (`C-COM-004`, `C-COM-008`).

---

### 0.9 This revision — TAD Revision 5 (ADR-038): the request/result split, an age-bound freshness rule, and the one place the approved TAD is factually wrong (2026-08-28)

**Read the last item first, because building the approved document literally would have shipped a
permanently dead feature.**

TAD [Revision 5](../architecture/trustee-portal-visual-refresh-architecture.md#L2770) supersedes ADR-030 on live evidence:
the synchronous `shared_logicflows` transport was built, pushed twice and crashed the portal's boot both
times, which is the `blocker` [IMP-0377](../../logs/improvement-log.jsonl) demanded an architecture decision
for. That decision now exists, and this revision builds it — a Dataverse-row-triggered flow, a second table
so the answer lands somewhere a trustee cannot write, and freshness as an age bound rather than a request
identity.

#### 0.9.1 `subscriptionRequest/message: 2` means DELETED, not Updated. The flow ships `3`.

[ADR-038 decision part 1](../architecture/trustee-portal-visual-refresh-architecture.md#L2816) and
[§5.1.1](../architecture/trustee-portal-visual-refresh-architecture.md#L1423) both specify
`subscriptionRequest/message`: **2** *(Updated)*. Measured live in REV-GrantApplications-DEV on 2026-08-28,
the `callbackregistration.message` option set reads:

| value | label | | value | label |
|---|---|---|---|---|
| 1 | Added | | 5 | Added or Deleted |
| **2** | **Deleted** | | 6 | Modified or Deleted |
| **3** | **Modified** | | 7 | Added or Modified or Deleted |
| 4 | Added or Modified | | | |

Read from the `stringmap` table through the active `pac` profile, and corroborated end to end in both
directions on this tenant: `REVScoringCalculateAndFlag`'s `subscriptionRequest/message: 1`
([`:64`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVScoringCalculateAndFlag-8F1C2A44-1002-4B7A-9E21-0A1B2C3D4E02.json#L64))
has a live `callbackregistration` reading **Added**, and the live DEV round-statistics flow's `message: 3`
has one reading **Modified**. The connector parameter passes straight through.

**So the flow is authored with `message: 3`, and this is not a re-derivation of a settled design.** The ADR's
*intent* is unambiguous — it labels the value *(Updated)*, says *"changing only `message` (1 → 2)"*, and
instructs that the trigger shape be **copied from the one proven live**. `3` is the only value that satisfies
all three. Building the literal `2` would register a *delete* trigger on a row nothing ever deletes: the flow
would never fire, the app would poll and time out, and every trustee would be told *"still working"* forever
with every source-side gate green — which is exactly failure mode
[A-R47](../architecture/trustee-portal-visual-refresh-architecture.md#L2915). Logged as a finding; the TAD needs a Revision 6
erratum on §5.1.1, ADR-038 part 1 and §12.3 step 2, and that is `architect-agent`'s edit, not this dispatch's.

#### 0.9.2 §12.3 step 1 — the live-versus-source reconciliation, in full

[§12.3 step 1](../architecture/trustee-portal-visual-refresh-architecture.md#L3086) is the one step whose order cannot
change: the live DEV flow was hand-edited in the designer and disagrees with source, so authoring the new
trigger and importing it would overwrite whatever else that session changed. Performed with
`pac solution export` + `pac solution unpack` against REV-GrantApplications-DEV (read-only; no write of any
kind attempted or made). **This table is the only artefact of what the 2026-08-27 designer session did.**

| # | Difference | Which side is ahead | Decision |
|---|---|---|---|
| 1 | **Trigger.** Live: `OpenApiConnectionWebhook` / `SubscribeWebhookTrigger` on `shared_commondataserviceforapps`, named `When_a_row_is_added,_modified_or_deleted`, `message: 3`, `entityname: rev_roundstatisticsrequest`, `scope: 4`, `runas: 3`. Source: `type: "Request"`, `kind: "PowerApp"`, named `manual` | **Live** | Source adopts the Dataverse trigger, with live's `message: 3` (§0.9.1) and a descriptive hand-authored name replacing the designer's comma-bearing default — the convention the scoring flow already uses |
| 2 | **54 compute actions** — 46 `Filter_*` Query actions, 7 `Compose_*_categories`, `Compose_wellbeing_questions` — present in source, **absent live** | **Source, by a wide margin** | Keep source's. Live is still the flow's **first** version; revision 0.7's second version was never imported |
| 3 | **`Compose_response_body`.** Live emits `genderDistribution`/`ageRangeDistribution`/`applicantTypeDistribution`/`wellbeingLastYear`/`lifeSatisfactionDistribution` as `null`; source emits them populated | **Source** | Keep source's |
| 4 | **`List_applications_in_round`.** Live: `$select=rev_applicationid` only, **no `$expand`**. Source: the four wellbeing/life-satisfaction columns plus `$expand=rev_applicantid(...)` | **Source** | Keep source's |
| 5 | **The five `Response` actions are byte-identical** between live and source — `Respond_ok`, `Respond_error`, `Respond_no_open_round`, `Respond_ambiguous_round`, `Respond_truncated`, all still `type: "Response"` / `kind: "PowerApp"` | Neither | **TAD §12.3's preamble is wrong**: it says *"the trigger **and its final action**"* were changed by hand. Only the trigger was. All five are replaced by write-backs in this pass |
| 6 | **`definition.description`** is `null` live, populated in source — the designer strips it | Source | Keep and update source's |
| 7 | **`properties.templateName: ""`** appears live and in **no** source flow in this solution | — | Designer artefact. Not adopted |
| 8 | **`metadata.operationMetadataId` GUIDs** on live actions, absent from every source action | — | Designer artefacts. Not adopted |
| 9 | **`.json.data.xml`:** live `StateCode 1 / StatusCode 2` (Activated); source `0 / 1` (Draft) | — | Keep source's Draft — the deliberate convention for all five flows in this solution |
| 10 | **Packer casing/ordering variance** — live `AsyncAutodelete` and `ModernFlowType`; source `AsyncAutoDelete` and `BusinessProcessType` | — | Cosmetic; source matches the other four flows. Nothing changed |

**[A-R50](../architecture/trustee-portal-visual-refresh-architecture.md#L2918)'s specific fear did not materialise.** It
predicted a silently-altered trigger `scope` (`4` Organization → `1` User, which has happened on this
project before). Live `scope` is `4`. There is exactly **one** hand-edit and **one** loss, and nothing that
session did is now unrecorded.

**Pre-import baselines captured before any write, per `IMP-0133`.** The live `callbackregistration` for this
flow: `entityname rev_roundstatisticsrequest`, `message Modified`, `scope Organization`, `createdon
2026-08-27 18:22`, id `b184204a-44a2-f111-b8de-70a8a5079a1b` — it **predates** the import this rollout
performs, so it is stale by construction and must be recreated at
[§12.3 step 6](../architecture/trustee-portal-visual-refresh-architecture.md#L3091). `rev_roundstatisticsresult` does not
exist in DEV. The `RoundStatisticsStaleAfterSeconds` `rev_setting` row does not exist, which is the correct
fail-safe state (OQ-042). The request row `CURRENT` exists (id `40f46317-44a2-f111-b8de-70a8a5079a1b`).

#### 0.9.3 A second stale privilege the ADR does not name

[A-R49](../architecture/trustee-portal-visual-refresh-architecture.md#L2917) records that
`provisioning/dataverse/ensure-schema.ps1` grants privileges and revokes none — it declares the gap in its
own step-5 convergence line at
[`:747-750`](../../provisioning/dataverse/ensure-schema.ps1#L747) — so
`prvWriterev_roundstatisticsrequest` stays live on `REV Service Automation` after this change ships.
Measured live on 2026-08-28: it does, at `privilegedepthmask` 8 (Global), `roleprivilegeid`
`83a7aa39-40a2-f111-b8de-7ced8d43e1b4`.

**There is a second one, of the same class, that ADR-038 withdraws but does not sequence for revocation.**
`prvReadWorkflow` was removed from `REV Trustee`'s source on 2026-08-27 and is **still bound live** at
Global, `roleprivilegeid` `ea54378b-87a0-f111-b8de-70a8a5079a1b`. Both are in the pipeline config's
`post_deploy` revoke step, by name, with the read-back that proves each — and the second is flagged here for
the reviewer to ratify rather than folded in silently. Neither touches the general revoke mechanism, which
[§6.1.1](../architecture/trustee-portal-visual-refresh-architecture.md#L1698) and
[§12.3's closing note](../architecture/trustee-portal-visual-refresh-architecture.md#L3096) both put outside this dispatch.

#### 0.9.4 Hours proposal — addendum for `commercial-agent` behind `APPROVE TIMESHEET`

No figure from `contract/wbs.json` or `contract/service-agreement.json` is restated here (`C-COM-008`), and no
rate or fee appears anywhere in this document (D-3, `C-COM-004`).

| WBS | Proposed actual | Evidence |
|---|---|---|
| `6.9` | 5.8 h | The transport rewrite end to end: §12.3 step 1 performed for real (live export + unpack, both action graphs flattened and diffed in all three directions, ten differences accounted for) rather than taken from the document's own account of it, which turned out wrong in two places; the approved TAD's `message` value disproved against the live `stringmap` option set and corroborated in both directions before a line was authored; the flow's trigger, result-row guard, freshness read, two new alert paths and five write-backs authored and packed clean against both package types with a 0-finding hosted Solution Checker run; a new table, its four attributes, its alternate key, three superseding descriptions, the hand-kept entity list, `Solution.xml`, four settings files and a new seed script; the role split that closes `IMP-0401`, plus a **second** stale live privilege found by query that the ADR does not name; the app's read moved to the result table and its freshness rewritten from request identity to an age bound, with the surviving mutation that disproved the TAD's own inexpressibility claim; and the nine-step rollout order transcribed into the pipeline config with five superseded steps marked rather than deleted |
| `6.1` | 0.4 h | The one screen-level change Revision 5 requires: the **Refresh figures** live-region announcement now states the freshness stamp rather than the action, because inside the window the control legitimately returns without recomputing and *"Figures refreshed"* would be false in the common case; and `pending` joins the diagnostic states through `StateMessage` with `role="note"` rather than `role="alert"` |
| `system` | 1.3 h | Not client work, marked as tooling per this agent's own rule. The new HARD gate `flow-reads-no-trigger-body` — a 15-case selftest, two on-disk known-bad fixtures, five Pester blocks, and check B's derive-from-source taint analysis with fixpoint propagation; the stale `flow-definition-language` comment corrected after measuring it against `HEAD`; the stray Pester fixture that had a HARD gate red and a 56-test container unrunnable, removed after a sub-agent's identical `rm` was refused; and twelve improvement-log findings, two of them corrections to what this repository already believed |

A proposal for `commercial-agent` to confirm, not a booking. **A-R28** and **A-R43** are unchanged and still
open, and Revision 5 moves A-R28's basis a fourth time — `CO-001-A1` priced a synchronous flow and a code-app
flow data source, neither of which is built, and in their place sit a second table, a second seed script, a
second auditing switch, a manual privilege revoke and a poll loop. `wbs:6.9` remains a covered id
(`contract/change-orders/CO-001.md`, APPROVED), so **no new change order is needed for the work to proceed** —
this is a sizing question, not a scope one, and it should land in one re-confirmation with A-R43.

### Revision 0.10 — hours proposal, addendum for `commercial-agent` behind `APPROVE TIMESHEET`

No figure from `contract/wbs.json` or `contract/service-agreement.json` is restated here (`C-COM-008`), and no
rate or fee appears anywhere in this document (D-3, `C-COM-004`).

| WBS | Proposed actual | Evidence |
|---|---|---|
| `6.9` | 1.6 h | The coverage unblock and the two defects it exposed: 25 behavioural `It` blocks across three new `Describe` blocks, written against the existing fake-Web-API harness so each runs the real seeder unmodified; the wrong-table defect corroborated three ways (the `Entity.xml` superseding descriptions, the app's own `schema.ts` constant and its test, `provisioning/README.md`) before a line was changed; the StrictMode/null-column contract verified in isolation rather than assumed; both fixes falsified by mutation (6 and 4 kills) and the file confirmed byte-identical afterwards; the full 941-test Pester run plus the `coverage-threshold` gate re-run as the build invokes it; and §2/§5/§11/Checklist corrections including the false 56/56 claim |
| `system` | 0.4 h | Not client work, marked as tooling per this agent's own rule. Establishing that `forms-and-views-reachable`'s verdict depends on untracked working-tree files by reproducing CI's 14-warning result against an `rsync` copy; re-running all 20 mechanical constraint verifiers bare to capture exit codes honestly; and four improvement-log findings, two of which propose the leading per-file gate that would have made this whole dispatch unnecessary |

A proposal for `commercial-agent` to confirm, not a booking. **This is remedial work inside an already-covered
id, not new scope** — no change order is implied, and it is deliberately proposed *below* the two-defect-fix
sizing of Revision 0.9's own `system` line, because the tests were written against a harness that already
existed rather than built from nothing.

### Revision 0.11 — `IMP-0438`: the request seeder stops writing `rev_status`, and three artefacts that still said it should (2026-08-28)

**The fix is one line, and it is done: [`seed-round-statistics-request.ps1`'s PATCH body](../../provisioning/dataverse/seed-round-statistics-request.ps1#L139) is now `@{ rev_name = $requestKey }` and nothing else.** The HARD build step [`superseded-column-writers`](../../config/revitalise-grant-automation-build.yml#L195) — wired by improvement review 37 and the gate that found this — reports `OK, 3 marked column(s) examined across 38 writer candidate(s), 0 finding(s)`, and [`DataverseScripts.Tests.ps1`](../../src/tests/provisioning/DataverseScripts.Tests.ps1#L1110) is 81/81 with the corrected behaviour asserted rather than merely no longer broken.

**`rev_resultjson` and `rev_computedon` were checked rather than assumed, as the dispatch required, and this script never wrote either.** `grep -rn "rev_resultjson\|rev_computedon" provisioning/ src/solutions/` puts both names in this file exactly once, in the header prose explaining why they are *not* written; every live write of those two columns is the flow's, against `rev_roundstatisticsresults`. So the defect was one column in one script, and it is the whole of the code change.

**The write's stated justification was false in both directions, which is why the header was rewritten and not just trimmed.** The old header claimed `rev_status = 2` fed *"the landing screen's first-ever read"*. [`ROUND_STATISTICS_REQUEST_COLUMNS`](../../src/code-apps/trustee-review-portal/src/dataverse/schema.ts#L368) is that row's primary key and nothing else, so no screen ever read it; and the resting state the landing screen does read comes from [`seed-round-statistics-result.ps1`'s own `rev_status = 2`](../../provisioning/dataverse/seed-round-statistics-result.ps1#L116) on the result row.

**Three further artefacts in the same ADR-038 blast radius still asserted the answer lives on the request table. All three are corrected here, and this is the one part of this revision that goes beyond the dispatch's literal ask** — reported plainly rather than folded in, because it changes shipped metadata:

| Artefact | What it said | Why it could not be left |
|---|---|---|
| [`rev_roundstatisticsrequest/Entity.xml` entity-level `<Description>`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_roundstatisticsrequest/Entity.xml#L51) | *"the flow writes `rev_status`, `rev_resultjson` and `rev_computedon` when it finishes"* | Shipped metadata contradicting [its own attribute descriptions](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_roundstatisticsrequest/Entity.xml#L100) 49 lines below, in the one file whose truthfulness this dispatch exists to restore |
| [`OptionSets/rev_roundstatisticsrequeststatus.xml` `<Description>`](../../src/solutions/RevitaliseGrantAutomation/OptionSets/rev_roundstatisticsrequeststatus.xml#L25) | *"State of the single `rev_roundstatisticsrequest` row's most recent computation cycle"* | TAD §3.9.2 cites this description as recording that the set keeps its `…request…` name while living on the result table. It did not say so; now it does |
| [the flow's `notes.md` §5](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.notes.md#L424) | *"`rev_roundstatisticsrequest.rev_status` … is the seeded row's resting state"* | Points the next reader at the table this dispatch just stopped writing |

**One divergence is recorded, not repaired.** The live DEV request row (key `CURRENT`, id `40f46317-44a2-f111-b8de-7ced8d43e87d`) already carries `rev_status = 2` from the pre-fix script, and this seeder is create-only (`C-TECH-042`), so it reports `EXISTS` and no re-run will clear it. No live write was attempted and none is proposed: the column is read by nothing, and clearing it would mean an extra live PATCH against a column the solution declares unused. `IMP-0449` is the record so the next session to query that table does not read the value as a live writer.

**`IMP-0446` describes this dispatch's mutation-test state, not its output.** A concurrent `improvement-agent` session read [the PATCH body](../../provisioning/dataverse/seed-round-statistics-request.ps1#L139) at 15:33 while it held a deliberate mutant (`rev_resultjson` + `rev_computedon` + `rev_triggeredon`), logged it as a `blocker` and set `corrects` on `IMP-0438`. The mutant lived about 90 seconds, was reverted to a file byte-identical to its pre-mutation `sha256` (`91806d32…8cfc`, verified with `shasum -c`), and `IMP-0438`'s diagnosis stands — confirmed by the gate, not argued. `IMP-0447` corrects it, and the digest now renders **⚠ CORRECTED by `IMP-0447`** against its lesson. `IMP-0446` was moved to `APPLIED` by that same concurrent session mid-dispatch, and nothing wrong was built on the observation: its own `proposed_change` was `type: none`, and the durable half it credits — review 37's `superseded-column-writers` gate — is correct and is what proves this fix.

#### Revision 0.11 — hours proposal, addendum for `commercial-agent` behind `APPROVE TIMESHEET`

No figure from `contract/wbs.json` or `contract/service-agreement.json` is restated here (`C-COM-008`), and no rate or fee appears anywhere in this document (D-3, `C-COM-004`).

| WBS | Proposed actual | Evidence |
|---|---|---|
| `6.9` | 0.8 h | One-line code fix, plus what made it verifiable and honest: `rev_resultjson`/`rev_computedon` checked against the corpus rather than assumed clean; the existing regression test rewritten to assert the corrected column set by name and falsified by **three** mutants (the real defect, three superseded columns at once, and an unforbidden fourth column) with the file confirmed byte-identical afterwards; the 81-test suite, the full Pester run and the `coverage-threshold` gate re-run exactly as the build invokes it; 17 mechanical gates re-run bare; the `C-TECH-042` convergence declaration this seeder never carried, which is what turns the DEV residue into a recorded decision at the point of the code; three stale prose artefacts corrected across `Entity.xml`, `OptionSets/` and the flow's `notes.md`; and this section |
| `system` | 0.3 h | Not client work, marked as tooling. Establishing that `IMP-0446` observed a mutation window rather than shipped state, and the four findings — including the proposal that a source-auditing gate state the universe it measured (second instance of that class in one day after `IMP-0445`) and the convergence gate's unfollowable remediation text, found by following it |

A proposal for `commercial-agent` to confirm, not a booking. Remedial work inside an already-covered id (`wbs:6.9`, `contract/change-orders/CO-001.md`, APPROVED) — no change order is implied.

---

### Revision 1.1 — TAD Revision 6 (ADR-039): the four money averages, the `k = 5` gate, and two corrections to the approved text (2026-08-28)

**All four money-average measures now compose, `k = 5` gates them, and `UR-002`/`UR-003` are deleted as
satisfied.** FR-059's `averageAmountRequested` and FR-060's `averageCost`, `averageAmountRequested` and
`percentageOfCost` were literal `null` on every row and on the total; each is now `{ value, population }`
where its own population is at least `k`, and the JSON literal `null` below it, with the row's `count` still
published. That is `wbs:6.9`, on a covered change-order id, and it closes the last of test report v4's D-11
keys. **Verification reaches V1 and no further** — `xml()` and `xpath()` have never executed on this tenant.

**Two things in the approved document are wrong, and both are reported rather than absorbed. Neither changes
a decision.**

#### 0.12.1 ADR-039's literal expression returns `NaN` on an empty subset, and the `NaN` escapes

§5.1.2 writes the sum as
`xpath(xml(concat('<r><v>', join(body('Select_<m>_values'), '</v><v>'), '</v></r>')), 'sum(/r/v)')`.
`join()` over an **empty** array yields `''`, so that builds `<r><v></v></r>` — a node set containing one
**empty element** — whenever a presence subset is empty. Measured against **libxml2**, a conformant XPath 1.0
engine, on the exact shapes this construction produces:

| XML | `sum(/r/v)` |
|---|---|
| `<r><v>10.5</v><v>20.25</v></r>` | `30.75` |
| `<r></r>` | `0` |
| `<r><v></v></r>` | **`NaN`** |
| `<r><v>10</v><v></v></r>` | **`NaN`** |

§0.9 point 3 already records that `NaN` is not valid JSON and would *"take all thirteen metrics off the
screen"*. What it does not say is that the presence `Filter array` **does not prevent this case**: the filter
removes blank *values* inside a subset, and an entirely *empty* subset is a different thing that the literal
shape converts into the `NaN` case. And the `NaN` **escapes the per-measure guard** — the total row sums the
five per-type sums with a nested `add()`, so one break type with no costed application makes `rev_resultjson`
unparseable. TAD §12.2 deliberately seeds a round with exactly that break type.

**What shipped** carries no `<v>` at all when the subset is empty, so `sum()` sees an empty node set and
returns `0`, which the average guard withholds:

```
@xpath(xml(concat('<r>', if(empty(body('Select_<m>_values')), '',
                            concat('<v>', join(body('Select_<m>_values'), '</v><v>'), '</v>')),
                  '</r>')), 'sum(/r/v)')
```

Both branches of that `if()` are plain string concatenation, so neither can throw whichever
argument-evaluation order the platform uses (`IMP-0378` / `IMP-0412`). **The guard is enforced in two
independent places rather than written down once:** `RoundStatisticsContract.Tests.ps1` asserts the template
byte-for-byte, and the HARD build gate `flow-reads-no-trigger-body` treats **only** this exact template as a
scalar reduction — with an on-disk known-bad fixture for the unguarded form and a `BuildGates.Tests.ps1`
block holding the line. Reproduced by mutation: removing the guard brought the total row's `averageCost` back
as `NaN`.

#### 0.12.2 A HARD build gate rejected the approved mechanism, and was extended rather than bypassed

`scripts/verify-flow-trigger-body-isolation.py` check **B1** — *the result document is composed from an
enumerated field list, never from a serialised row object* — **failed on the first run against the new
actions**, measured before any fix. The sum traverses the round's rows, so `Select_<m>_values` is row-bearing
and the taint propagated through every downstream `Compose` to `item/rev_resultjson`.

§5.1.2 has a paragraph headed *"Two things development-agent must not infer from the above"* naming exactly
**one** gate interaction — `verify-flow-definition-language.py` check 1, the `select(` regex — and stating
correctly that it does not fire. It is silent on B1, which is the gate that did.

The gate now recognises one additional reduction, on a one-sentence safety argument: **an XPath `sum()`
returns an XPath number, and a number cannot carry a row** — which holds whatever the feeding `Select`
projects, because a `Select` projecting whole rows would make `sum(/r/v)` return `NaN`, never a row.
`xpath`, `join` and `xml` were deliberately **not** added to the reducing-function allow-list: that would
have exempted `join(body('List_applications_in_round'), ',')`, which serialises rows into a column a trustee
reads. Instead one **anchored template** matches a `Compose`'s whole input expression, with the same `Select`
named in both `body()` positions and the XPath expression pinned to the literal `sum(/r/v)`. Five selftest
cases hold the boundary — a node-returning `'/r/v'`, two different source actions, the unguarded form, and
the template plus one extra reference in the same expression are all still rejected. Selftest: **15 cases →
20**, and the build config's own coverage comment corrected with them.

#### 0.12.3 One requirement reading this dispatch had to take, and it is registered rather than assumed

SDD FR-060 asks for *"the average grant amount requested **(including exceptional funding)**"*, and TAD §3.1
maps `rev_additionalamountrequested` to **FR-060** as well as FR-059. So the per-row value summed is
`rev_amountrequested` **+** `rev_additionalamountrequested` — the identical arithmetic the app's own approved
`totalFundingRequested` already performs for FR-035, which is why the two screens cannot disagree about what
a grant ask is. **The competing reading is not obviously wrong:** ADR-039's cost paragraph says *"five
break-type rows × two money columns"*, which reads as `rev_costs` and `rev_amountrequested` alone. That is a
costing phrase rather than a contract and the count of thirteen sums holds either way, but a reviewer
sentence settles it. Carried as **A-FLOW-12, OPEN**, marker at the five presence filters; the fix if it is
wrong is one expression per break type.

#### 0.12.4 Three figures corrected, and one exception that got worse

- **ADR-039 costs the mechanism at ~40 added actions and 145 total. The measured figures are 88 and 193.**
  The estimate counted only the sums; it did not count a presence `Filter` per measure (which §5.1.2
  property 2 establishes as the *arithmetic*, not an optimisation), a second `Select` and a second sum per
  `percentageOfCost` ratio, the `k` read chain, or the total row's population/sum helpers. **The decision is
  unaffected** — 88 is ~11× below the rejected candidate's ~950, nothing iterates, and 193 is far inside the
  documented 500-action limit — but an estimate is not a measurement, and this project's own *cite, never
  restate* rule holds for a technical figure exactly as it does for a baseline one.
- **The `k` sentinel is `999999999`, not a negative number, and that is a parse-safety decision.** `int()` is
  applied **once**, to digits only, so it cannot throw on either branch of the validity test. An absent,
  empty or non-numeric setting therefore yields a threshold no round can reach under the 1000-row page cap
  and **every money measure is withheld** — the direction §12.1 calls fail-safe-but-not-approved, which is
  why the row is seeded in all three environment settings files rather than left to the default.
- **The declared check-7 exception on this flow now hides 84 more actions than when it was declared.**
  `result('Compute_statistics')` does not descend into `Switch_on_open_round_count`, so a failure inside any
  of the 88 new actions reaches the alert as the wrapper message *"An action failed. No dependent actions
  succeeded."* ADR-039 describes A-FLOW-11's residual as **fail-loud**, and that claim leans on the alert
  naming the action that failed. **Deliberately not fixed here** — `IMP-0346` records a failure path fixed
  without a source-level regression test, and the P1 that fix introduced passed an 876-test suite — but the
  widening is recorded, and the exception's own clearing action is dated 2026-09-30.

### 0.13 This revision — `IMP-0485` and `IMP-0486` closed (`wbs:6.9`, 2026-08-29)

Two reviewer-reported defects, both already logged with full evidence before this dispatch started:
`IMP-0485` (the Round overview screen's hard "Data source not found" error) and `IMP-0486` (the design-system
refresh never reaching anything the reviewer could see, plus two CSS defects that would reproduce the
reviewer's exact symptoms even once shipped). Ground-truthed live rather than taken from either finding's own
prose, per this project's own `IMP-0381` rule.

**Fix 1 — `rev_roundstatisticsresult` registered as a real Code App data source.** The table's live existence
was independently re-confirmed rather than trusted from `logs/pipeline.log`'s 2026-08-29 entry alone:
`pa connection list -e 2f7ce6a9-fdb7-e10b-a40a-07f5022ee453 --json` was run first to find a WORKING
connection, because the connection id every prior addition in this app's history used
(`f31ddadfbe874e50a34054df668e75cf`) turned out to no longer exist live — see the new finding below. With a
live connection confirmed, from `src/code-apps/trustee-review-portal`:

```
pa app add data-source --connector dataverse --table rev_roundstatisticsresult \
  -u https://orge2b20d13.crm17.dynamics.com -c 8b4307acb81d4463be4fd96792363f2f --non-interactive
```

Succeeded — `Data source added successfully`. `.power/schemas/appschemas/dataSourcesInfo.ts` gained a real
`"rev_roundstatisticsresults"` entry (`dataSourceType: "Dataverse"`, `primaryKey:
"rev_roundstatisticsresultid"`); `power.config.json` gained matching `databaseReferences` entries for **both**
`roundstatisticsrequests` and `roundstatisticsresults` (the first was missing from that file even though its
`dataSourcesInfo.ts` entry and app usage already existed — a pre-existing gap this run closed as a side
effect, not something this dispatch went looking for); and
`src/generated/{models,services}/Rev_roundstatisticsresults*` are now real, generated, and committed.

[`client.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts#L270)'s `READ_SERVICES` entry
now points at the generated `Rev_roundstatisticsresultsService` instead of the interim
`Rev_roundstatisticsresultsStandInService`; `roundStatisticsResultReadService.ts` and its test are **deleted**
— unlike `rev_roundfinances`'s stand-in (kept on purpose per revision 0.2), this table never had a period
where a generated service existed alongside an undeleted stand-in, because the dispatching instruction asked
for the swap directly. [`schema.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/schema.ts#L11)'s
`A-RES-1` comments are marked CLOSED (E1) in place, and [`client.test.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/client.test.ts#L94)'s
"five of seven / two of seven" accounting is corrected to six of seven. `schema.test.ts`'s hand-kept
`landingFiles` list named the now-deleted stand-in file and was the one test failure this revision's deletion
caused (`ENOENT`) — fixed by removing that entry, not by touching the guard it belongs to.

`scripts/verify-code-app-data-sources.py src/code-apps/trustee-review-portal` → **OK — 7 registration(s), 7
Dataverse source(s) declared** (was 6/7 with one declared allowance). The `--allow "rev_roundstatisticsresults=…"`
line on the `code-app-data-sources` build step
([`config/revitalise-grant-automation-build.yml`](../../config/revitalise-grant-automation-build.yml#L1293))
is **removed in this same change**, per that step's own comment's clearing action. A concurrent
`improvement-agent` session independently found this exact removal outstanding (`IMP-0487`, correcting
`IMP-0485`'s own root-cause text, which had wrongly claimed no such gate existed) while this dispatch was
already mid-flight; this paragraph is the confirmation that the removal is actually done, re-verified by
re-running the gate standalone above, not merely claimed.

**A-RESULT-1, A-FLOW-07 and A-RES-1 all close at E1 on this one run** (§10) — all three were the same
platform-assigned pair of names (`rev_roundstatisticsresults`, `rev_roundstatisticsresultid`) guessed in three
places, and the CLI's own echo confirms every guess was correct, matching the read-only
`EntityDefinitions(rev_roundstatisticsresult)` query `pipeline.log` already recorded the same day.

**A finding this dispatch is the first to record: a documented connection id had gone stale.** Every prior
`pa app add data-source`/`pac code add-data-source -c <connection-id>` call this app's history documents
(revision 0.2 above, `docs/development/trustee-portal-org-url-fix-dev-summary.md`,
`knowledge/technology/code-apps.md`'s own worked examples) names `f31ddadfbe874e50a34054df668e75cf`. Live on
2026-08-29 that id is absent from `pa connection list`'s 5-row result entirely — the maker's Dataverse
connection was evidently deleted and recreated (twice: `8b4307acb81d4463be4fd96792363f2f` "Dataverse" and
`69894ebbc98e4ce58c83c0a9a11fd7cc` "Dataverse_new", both created 2026-08-26, thirteen minutes apart) sometime
during this feature's own recorded org-url-null troubleshooting, with nothing recording the change. The
actively-renewed one (`8b4307acb81d4463be4fd96792363f2f`, last modified the same day; "Dataverse_new" expired
2026-08-27 and untouched since) was used. This changes nothing about how the table resolves for a real
signed-in trustee — a `"Dataverse"`-type source is bound per-user at app-run time from launch metadata, never
from the connection id used to generate it (`knowledge/technology/code-apps.md` → "Invalid organization URL",
step 3) — so nothing here is at risk; it is logged (`IMP-0489`) so the next agent does not copy a dead id
out of a document and lose a cycle to an opaque connection-not-found failure.

**Fix 2 — the design-system conversion committed, plus two CSS defects.** `git status`/`git diff --stat`
confirmed `IMP-0486`'s own claim before touching anything: `src/components/ds/`, `src/styles/ds-tokens.css`,
`ds.module.css`, `brand.css` and every consuming component (`main.tsx` already imports `ds-tokens.css`;
`ApplicationFilters.tsx` already imports from `./ds`) were entirely untracked/uncommitted against `HEAD`
`5b8b985`. Nothing about the conversion's SHAPE was wrong or incomplete — revision 0.8 (2026-08-27) already
implemented TAD Revision 4 in full and this dispatch found no contradiction worth stopping for — the defect
was purely that none of it had ever reached `git log`, which is exactly the gap `IMP-0486` names. This
dispatch's own commit (see §8) is what closes that gap; §11 records it as the citation a "shipped" claim now
has to point at.

Two concrete CSS defects, fixed inside that same uncommitted tree before committing it:

- [`ds.module.css`](../../src/code-apps/trustee-review-portal/src/styles/ds.module.css#L319)'s `.statTileValue`
  gained `overflow-wrap: break-word`. Checked `Designsystem/Revitalise Design System/components/content/`'s
  own `StatTile.jsx` and `StatTile.prompt.md` first, per this dispatch's instruction not to guess: neither
  states any overflow behaviour at all, and the prompt's only worked example is the 5-character `"1,000"` —
  so wrapping is this app's own addition for its own, longer figures (`RoundFinancePanel.tsx`'s currency
  values, e.g. `formatAmount` producing `"£550,000.00"`), not a conversion of anything supplied. Wrapping was
  chosen over truncation deliberately: an ellipsis on a board-pack money figure would silently hide part of
  the amount, which is worse than a two-line tile, and the same property already does this job for prose at
  `app.module.css`'s `.preserveLines` (`IMP-0486`'s own citation).
- [`ApplicationFilters.tsx`](../../src/code-apps/trustee-review-portal/src/components/ApplicationFilters.tsx#L14)'s
  own header comment (Revision 4, TAD §2.1.4/§2.2.2 item 1) already establishes that Fluent's `Select` STAYS
  deliberately — the design system has no `Select` at all — so the defect was a STYLE mismatch only, never
  the wrong component choice. Read the installed `@fluentui/react-select` package's own compiled source
  (`getPartitionedNativeProps` in `@fluentui/react-utilities`, `useSelectStyles.styles.raw.js`) rather than
  guessing: a top-level `className` on `<Select>` is routed to the outer wrapper `<span>` and explicitly
  excluded from the `<select>` element itself, while the border/height/background this fix needs to change
  all live on the `select` SLOT. Fixed with Fluent v9's own supported slot-override mechanism —
  `select={{ className: styles.filterSelect }}` — on all three controls, never a top-level `className`. The
  new `.filterSelect` rule in
  [`app.module.css`](../../src/code-apps/trustee-review-portal/src/styles/app.module.css#L163) reuses
  `ds/Input`'s exact tokens (`min-height: 44px`, `--border-strong`, `--radius-sm`, `--focus-ring`) but
  deliberately leaves horizontal padding untouched — Fluent reserves `padding-right` for its own absolutely
  positioned chevron icon, and overriding it risks the icon overlapping a long option label.

**Regression tests, per this project's own rule that a fix without one is guarded by nothing (`IMP-0346`).**
New file
[`ApplicationFilters.test.tsx`](../../src/code-apps/trustee-review-portal/src/components/ApplicationFilters.test.tsx)
(4 tests): the three `Select`s' rendered `<select>` elements carry the `filterSelect` class key (the
component-level half `IMP-0386` allows — a class KEY, never the stylesheet, since vitest processes no CSS);
the Region control still disappears when no region is readable; and two stylesheet-level tests read
`app.module.css` off disk (the technique `theme.test.ts`/`ds-tokens.test.ts` already use) to assert
`.filterSelect`'s actual rule body, never through the CSS-Modules test stub. `ds-tokens.test.ts` gained one
new `describe` block reading `ds.module.css` off disk for `.statTileValue`'s `overflow-wrap`, and asserting
the absence of a truncating alternative (`text-overflow: ellipsis`, `white-space: nowrap`).

**Full re-verification, `src/code-apps/trustee-review-portal`:** `npm run typecheck` clean; `npm run lint`
clean; `npm run coverage` → **677/677 tests across 38 files, 98.53% statement/line coverage, 93.39% branch,
94.9% function** — up from the 372/372 revision 0.2 last cited directly; the delta is other concurrent work
already in this tree across revisions 0.3–1.1 plus this revision's own 6 new tests, none of it touched by
this dispatch beyond the fixes above; `npm run build` → clean (`vite build`, one pre-existing >500 kB
chunk-size advisory, unrelated to and unchanged by this dispatch). `code-app-data-sources` → OK, 7/7, 0
exemptions (above).

**Not pushed to DEV.** Per this dispatch's own instruction, `pac code push` stays `pipeline-agent`'s next
step, deliberately held until the improvement-log queue clears (`C-TECH-061`). This dispatch's own gate
therefore closes at a clean local build (source + commit), not at a deployment.

### 0.14 This revision — `IMP-0349`'s own instance cleared, the check-7 exception removed rather than renewed (`wbs:6.9`, `IMP-0483`, 2026-08-30)

**The reviewer was offered two ways to handle §0.12.4's growing exception and rejected both.** Improvement
review 43 (`docs/improvements/2026-08-29-improvement-review-3.md` §6) measured the declared
`("REVPortalRoundStatistics", "Compute_statistics")` check-7 exception hiding **167** descendant actions
against a declared blast radius of 83, and put exactly two options to the reviewer: (a) re-declare the
exception at `hides_at_declaration: 167`, keeping the build green and folding the growth into the baseline;
or (b) hold the line at 83 and accept a red build until the descent was written. **Neither was chosen**
(`routing.log` 2026-08-30 10:13) — the reviewer took a third option outside both offered: close the
underlying gap for real, with the descent it names as its own clearing action, and remove the exception
entirely rather than widen or renew it. This section is that fix.

**What changed, concretely, in
[`REVPortalRoundStatistics-…json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json):**
`Describe_the_failure` (previously a flat `Scope` wrapping one `Set_failure_detail`) is now an `If`, gated on
whether `Find_the_failed_action`'s result names `Switch_on_open_round_count` — the one container child
`Compute_statistics` has. When it does, `Find_the_failed_step_inside_Switch_on_open_round_count` (a `Query`
over `@result('Switch_on_open_round_count')`, mirroring `REVIntakeWordPressToDataverse`'s
`Find_the_failed_step_inside_Read_configuration` exactly) reaches the Switch's own failed step. That step can
itself be `Condition_page_cap` — the Switch's own only container child, established by direct inspection of
the flow's source (its `Exactly_one_open_round` case has exactly three immediate actions:
`Compose_round_key`, `List_applications_in_round`, `Condition_page_cap`, and everything else Revision 6 added
sits inside `Condition_page_cap`'s two branches, both flat, no further container) — so a second, identically
gated `If` (`Describe_the_switch_failure`) descends once more via
`Find_the_failed_step_inside_Condition_page_cap`. Three `Set_failure_detail*` leaves now exist, one per depth,
so `Alert_on_failure`'s `text_2` always carries the true leaf's action name, platform error code and message —
never the Switch's or the If's own opaque wrapper.

**The platform contract this rests on is ground-truthed, not assumed, and the result is a genuine gap, not a
guess resolved.** Before writing any of this, Microsoft's own documentation was checked directly (four pages:
the `result()` function reference, the *"Get context and results for failures"* walkthrough, the Switch and
Condition how-to guides, and the control-workflow-action schema reference) for whether `result()` accepts a
Switch or an If action's own name the way it accepts a `Scope`/`For_each`/`Until`. **Every worked example
names only those three; none confirms or denies a Switch or If by name**, and the one explicit caveat that
exists — *"not from deeper nested actions such as switch or condition actions"* — describes a switch/condition
**nested inside** the named scope, not one passed **as** the name. This is now recorded once, for the next
session, as `IMP-0496` (`platform-fact-groundtruthed`), and as a new **`A-FLOW-13, OPEN`** row in §10: the
construction above is the established, already-shipped pattern for a `Scope` (`Read_configuration`),
generalised by analogy to two container types nobody has separately confirmed. It is the deliberately safest
available construction given that a live deploy is out of this dispatch's scope: every `result()` call
carrying the open assumption is gated behind a name check that only evaluates it once the platform has
already told us (via `Find_the_failed_action`'s or the prior step's own result) that this exact action is the
one that ran and failed — the same technique that makes the existing `Read_configuration` descent safe one
flow over — so a wrong assumption degrades to the pre-fix generic message rather than throwing a new failure.
Closing A-FLOW-13 needs one live run (V4/V5); nothing in this dispatch performs one.

**Verified live, not by inspection alone.**
`python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation` now reports
**zero** findings for `REVPortalRoundStatistics` — the fix satisfies check 7 on its own merits, not via
suppression — and the two untouched flows' exceptions (`REVIntakeWordPressToDataverse`,
`REVScoringCalculateAndFlag`) still print exactly as before. The script's own `--selftest` (22/22) and
`src/tests/solutions/RoundStatisticsContract.Tests.ps1`'s new *"D-15 regression"* `Describe` block (7/7, full
file 54/54) both pass — the latter is the source-level regression test `IMP-0346` requires for a hand-authored
flow-definition fix, asserting the exact branch structure, the gating expressions, the leaf-vs-wrapper message
content on all three paths, and that `verify-flow-definition-language.py` itself reports this flow clean with
the exception's dict key gone (not merely that some other suppression produced the same exit code).

**The `("REVPortalRoundStatistics", "Compute_statistics")` key is deleted from
[`verify-flow-definition-language.py`](../../scripts/verify-flow-definition-language.py)'s
`_CHECK7_EXCEPTIONS`** — not renewed, not widened — per the reviewer's explicit instruction. The two other
flows' exceptions are untouched (different scope; `REVIntakeWordPressToDataverse`/`REVScoringCalculateAndFlag`
are `automation-agent`'s to close separately). `IMP-0483` (`gate-reassures-wrongly`) stays `NEW` for
`improvement-agent` to close: its own `revisit_when` names exactly this outcome — descent written, the entry
removed, the gate exiting 0 with two exceptions rather than three — and all three are now true, verified
above rather than merely claimed.

**Out of scope, unchanged:** the other two flows' check-7 exceptions (§0.12.4, review 43 §6 table) and every
item §0.12.3/§0.12.4 already left open (`A-FLOW-11`, `A-FLOW-12`, the `k` seeding gap). None of this dispatch's
work touches them.

### 0.15 This revision — TAD Revision 7 implemented in full: the persistent nav bar (ADR-040), the wider
shrink-to-fit stat-tile grid (ADR-041), the self-hosted Playfair Display heading face (ADR-042), the header
padding correction (§0.10.1) and the "Figures of this round" subheading (§0.10.2) (`wbs:6.9`, `IMP-0510`,
2026-08-30)

**Built on top of the already-committed `IMP-0509` fix (commit `6ae5bf6`), not redone.** That commit added
`line-height: var(--leading-tight)` to `.statTileValue`
([`ds.module.css:353`](../../src/code-apps/trustee-review-portal/src/styles/ds.module.css#L353)) to stop a
wrapped currency value overlapping its own second line. This revision's ADR-041 work adds a **second,
independent** `font-size` rule to the same class ([`ds.module.css:376`](../../src/code-apps/trustee-review-portal/src/styles/ds.module.css#L376)) and both the code comment and the test suite (below) now say explicitly that
the two must not be conflated or one deleted while touching the other.

**Six pieces, all six built and all six passing the full local gate chain (tsc, eslint, 689 vitest tests
across 38 files, `npm run coverage` at 98.52% statements against an 80% floor, a clean `vite build`):**

1. **ADR-040 — the persistent nav bar.** [`App.tsx:192-249`](../../src/code-apps/trustee-review-portal/src/App.tsx#L192)
   adds a `<nav aria-label="Screen navigation">` with one `<button type="button">` per screen, rendered on
   every view. Named "Screen navigation" rather than reusing `LandingPage`'s own "Portal sections" landmark —
   the two are on screen at the same time on the landing view, and two landmarks sharing one accessible name
   are indistinguishable by a screen-reader user navigating by landmark. `aria-current="page"` marks the
   active tab; the "Application detail" tab carries `aria-disabled` (never the native `disabled` attribute,
   so the tab order never changes size between states) plus a visible caption, "Open a case first"
   ([`App.tsx:237-247`](../../src/code-apps/trustee-review-portal/src/App.tsx#L237)) — A-R55's own condition,
   `view.name !== "detail"`, implemented literally. The old contextual "Back to the round overview" `<button>`
   is retired ([`App.tsx:174-175`](../../src/code-apps/trustee-review-portal/src/App.tsx#L174) records why);
   `ApplicationDetailPage`'s own "back to the list" is untouched. Both colour pairings the tab bar uses —
   white on `--brand-primary` and `--text-heading` on `--grey-100` — were already asserted passing by
   `ds-tokens.test.ts` before this change, so no new, unchecked contrast pair is introduced.
2. **ADR-041, part 1 — the stat-tile grid widens.** [`app.module.css:865`](../../src/code-apps/trustee-review-portal/src/styles/app.module.css#L865)
   raises the `minmax` floor from `160px` to `240px`. `auto-fit` still reflows to fewer columns as the
   viewport narrows and to one column under 320px, so the WCAG 1.4.10 guarantee `app.module.css`'s own prior
   comment established is unchanged in kind — only the desktop column count changes (typically 4, matching
   the ui_kit).
3. **ADR-041, part 2 — the shrink-to-fit container query.** [`ds.module.css:309`](../../src/code-apps/trustee-review-portal/src/styles/ds.module.css#L309)
   sets `container-type: inline-size` on `.statTile`; [`ds.module.css:376`](../../src/code-apps/trustee-review-portal/src/styles/ds.module.css#L376)
   changes `.statTileValue`'s `font-size` from the fixed `var(--text-2xl)` to
   `clamp(var(--text-lg), 6cqi, var(--text-2xl))`. **Verified live in real Chromium** (Playwright 1.62.1, not
   jsdom — the same technique `IMP-0509` used), against the actual built stylesheet: a tile in a 900px-wide
   container rendered its value at the full 32px; the SAME markup in a 260px-wide container rendered it at
   20px — the clamp responds to the tile's own width exactly as designed. `document.fonts`/`CSS.supports`
   confirmed `container-type: inline-size` is genuinely supported and exercised by this Chromium build, not
   silently ignored. **This is evergreen-Chromium evidence, not proof for the Power Apps Code App host's own
   embedded WebView2 build** — TAD §12.2's own row already says so, and closes it. See §11 below.
4. **§0.10.1 — the header-band padding correction.** [`app.module.css:57`](../../src/code-apps/trustee-review-portal/src/styles/app.module.css#L57)
   adds `padding-top: var(--space-5)` to `.page`, leaving the shorthand `padding` (bottom, and the fluid
   horizontal clamp) untouched — the mismatch table named the header band's own vertical figure specifically,
   not the page's bottom padding, which no row found a mismatch in.
5. **ADR-042 — Playfair Display, self-hosted, real files.** `--font-display`
   ([`ds-tokens.css:378`](../../src/code-apps/trustee-review-portal/src/styles/ds-tokens.css#L378)) becomes
   `"Playfair Display", Georgia, Cambria, "Times New Roman", Times, serif`; two `@font-face` rules
   ([`ds-tokens.css:359`](../../src/code-apps/trustee-review-portal/src/styles/ds-tokens.css#L359),
   [`:367`](../../src/code-apps/trustee-review-portal/src/styles/ds-tokens.css#L367)) declare weights 400 and
   700 as `data:font/woff2;base64,…` URIs — never a relative `url()` to a separate built asset file, per the
   `A-BRAND-1` precedent (`App.tsx`'s own header) that this Code App host does not reliably resolve a second
   fetched file at runtime. **A-R53 (the "unmet external dependency" TAD §11 raised) is CLOSED, not merely
   worked around**: the real font files came from `@fontsource/playfair-display@5.3.0` on the public npm
   registry — the canonical Google Fonts-published distribution of the exact typeface the design system
   names, under the SIL Open Font License 1.1, which explicitly permits this. The two files (400/700, latin,
   normal style — the only weights any `--font-display` call site in this app actually renders) are also kept
   as real files under
   [`src/assets/fonts/playfair-display/`](../../src/code-apps/trustee-review-portal/src/assets/fonts/playfair-display)
   with the licence text beside them, for provenance. `--text-heading` is untouched — `#002060` navy, exactly
   as ADR-042 records as the reviewer's deliberate override of the design system's own "never navy"
   instruction. Logged as a reusable capability (`IMP-0513`, `logs/improvement-log.jsonl`): before recording
   a *named, open-source* typeface as blocked on the reviewer supplying files, check whether an
   `@fontsource/<slug>` package already is that supply — this does not apply to a proprietary face like
   Aptos, where the reviewer genuinely is the only route.
6. **§0.10.2 — the "Figures of this round" subheading.** [`LandingPage.tsx:315`](../../src/code-apps/trustee-review-portal/src/pages/LandingPage.tsx#L315)
   adds a plain `<h2>Figures of this round</h2>` immediately before `<RoundStatistics>`, inside the
   `kind === "figures"` branch only — never in the `"loading"` or `"diagnostic"` branches, and never inside
   `RoundStatistics.tsx` itself, which keeps its own unconditional `.freshness` line unchanged directly
   beneath it. No new type rule: the heading inherits the same global `--font-display`/`--text-heading` rule
   every other heading on this screen already carries.

**A-R54 (the container-query platform-contract question) is genuinely NOT closed, and this document does not
claim it is.** TAD §12.2 names the actual closing step as opening the live Code App as a real signed-in
trustee and inspecting the computed `font-size` at two column counts — a V4 step this dispatch has no access
to perform (no live credential, per `IMP-0512`'s own finding, and no signed-in browser session). What this
dispatch DID verify — real Chromium, real built CSS, the actual clamp responding to width — is evidence that
the mechanism is correct and that evergreen Chromium (which the host's WebView2 is built on) supports it; it
is not evidence about the specific WebView2 build the host embeds. The declared failure mode if that build
predates container-query support remains exactly as ADR-041 describes it: a safe, silent degrade to the
unclamped `--text-2xl` (today's already-shipped, `IMP-0509`-fixed behaviour), never a broken render.

**No new `§10` register row.** Every platform-contract question this revision touches (container-query
support, the Playfair Display licence) is already tracked as a TAD-level risk (`A-R53`, `A-R54`) rather than
a hand-authored Dataverse/flow shape this dispatch guessed at — `C-TECH-052`'s register is for platform
contracts THIS dispatch authored blind, and CSS container queries are a versioned, publicly-documented web
platform feature, not a shape this project's own build tooling assigns. `A-R53` is closed above on real
evidence (a real, licensed, redistributable font file); `A-R54` stays open exactly where the TAD already put
it, awaiting the V4 step named there.

**No sub-agent fan-out performed — reason disclosed, per `agents/development-agent.md`'s Sub-Agents table.**
The dispatch instruction did not name a specific sub-agent, and the six pieces above are one coherent CSS/
component-token pass across four files that share the same token vocabulary (`ds-tokens.css`) and the same
component (`ds/StatTile`, `App.tsx`'s shell) — splitting the font self-hosting research (npm registry,
licence terms, the A-BRAND-1 bundling precedent) from the CSS change it justifies would have re-derived the
same context twice, and `frontend-agent` would have needed the identical TAD/ADR reading this session already
holds. Judged inseparable, not decided silently.

## 1. Implementation Summary

Five pieces, now all built at source level; only live-environment verification remains open:

1. **Schema (WBS 6.3, 6.9) — built and V4-verified live in DEV, an earlier session.** The new `rev_roundfinance`
   table (13 attributes, one alternate key), the three `rev_application` `…redacted` care-support columns
   (WBS 6.3, ADR-027 amended), and the associated security-role privilege grants across all three roles.
   Unchanged by this revision.
2. **The flow (WBS 6.9) — authored as solution source, packed, and Solution-Checker-clean; not yet live, and
   not yet reachable by the Code App at all (§0.7).**
   `REV | Portal | Round Statistics` now computes six of the thirteen non-`ethnicGroup` metrics:
   `applicationsReceived` (first version) plus, **this revision**, `genderDistribution`,
   `ageRangeDistribution`, `applicantTypeDistribution`, `wellbeingLastYear`, `lifeSatisfactionDistribution`.
   Every remaining metric responds `null`, declared as such, not silently omitted. **This revision does NOT
   touch the trigger/`Response`/failure-path outer shell** — deliberately: `IMP-0358`/`IMP-0359`/`IMP-0365`
   (§0.7) establish that shell cannot currently boot the Code App at all, a concurrent uncommitted session has
   already moved the app's own invocation mechanism to a design this flow does not yet implement, and
   resolving that is an architecture decision (`IMP-0377`, logged this revision) this dispatch did not make
   unilaterally. **This revision closed D-02 in an earlier pass**: the flow catches a genuine action failure
   (either `List_the_open_round` or `List_applications_in_round` failing), calls `REV | Ops | Failure Alert`
   (writes `rev_errorlog`, alerts the process owner), and always responds with a JSON body —
   `status: "error"` — so the caller never receives a bare, unhandled platform failure, and every action this
   revision adds sits inside that same `Compute_statistics` Scope, so the existing coverage reaches it
   unchanged. §0.7, §4, §10 A-FLOW-05/A-FLOW-06, §11.
3. **The UI — all three slices now built.** ADR-026's brand theme (WBS 6.1) and FR-035's redacted-column
   wiring on `ApplicationDetailPage.tsx` (WBS 6.3) were already complete from earlier dispatches on this
   feature and are unchanged. **This revision closes D-01**: `LandingPage.tsx` and the FR-057–FR-063 content
   (WBS 6.9, `wbs:6.1`'s navigation-shell half) are now built — against the flow's defined §3.3 response
   contract and `rev_roundfinance`'s confirmed-live schema, with no live flow call yet (the flow itself is
   not live — see §7, §10 A-FLOW-01/05, A-LAND-2). **`rev_roundfinance`'s own Code App data source is now
   registered** (§0.2, 2026-08-26) — `pa app add data-source` has been run and `dataSourcesInfo.ts` carries
   a real `"rev_roundfinances"` entry; A-LAND-1 is CLOSED. FR-059/FR-060 (`exceptionalCircumstanceMix`,
   `exceptionalFundingSummary`, `breakTypeProfile`) and FR-062's three headline proportions still render as
   **absent**, because the flow still emits `null` for them; FR-061's gender/age-range/applicant-type
   distributions and the wellbeing/life-satisfaction halves of FR-062 will render real figures **once the
   flow is actually reachable by the Code App** (§0.7 — it is not, yet, regardless of this revision's own
   computation work) — the screen was already built against the *whole* contract, so nothing on the UI side
   changes for this revision's five new metrics.
4. **The trustee detail screen's remaining board-pack fields (WBS 6.3, Amendment A-05) — built this
   revision, source-level only; schema deploy pending (§7, §10).** Every field the printed board pack
   carries and the app did not yet show: nine unconditional Group A columns across three new panels
   (`FinancialEligibilityPanel`, `ConditionProfilePanel`, `HelperRefereeContactPanel`); the eleven Group B
   secured columns rendered from ADR-032's build-derived field catalogue, with **no `$select` naming any of
   them anywhere in the app**; the five further Group C `…redacted` counterparts (ADR-031), gated by
   `rev_redactionreleased` exactly as the existing three care-support ones are. §0.6, §2, §6, §10.

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

### This revision (FR-035 structured fields, 2026-08-27)

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| `src/dataverse/types.ts` | Code App data | `ApplicationDetail` gains `careProvidedType`, `careHoursPerWeek`, `applicantType`, `additionalAmountRequested`, `exceptionalFundingRequested` | FR-035 |
| `src/dataverse/schema.ts` | Code App data | `APPLICATION_DETAIL_EXTRA_COLUMNS` +5 columns; new `APPLICANT_DETAIL_COLUMNS`; new `CARE_PROVIDED_TYPE_LABELS`/`CARE_HOURS_BAND_LABELS` maps; new `optionLabels()` helper | FR-035 |
| `src/dataverse/repository.ts` | Code App data | `mapDetail()` extended; new `resolveApplicantDetail()` (single-id detail-only applicant read, separate from `resolveRegions()`) | FR-035 |
| `src/dataverse/odata.ts` | Code App data | New `asNumberArray()` — the multiselect wire-shape parser, marked `A-TR-13` | FR-035 |
| `src/domain/format.ts` | Code App logic | New `totalFundingRequested()` — FR-035's single combined figure (OQ-031 fix) | FR-035 |
| `src/components/CasePanels.tsx` | Code App UI | `HolidayPanel`: type of break, one combined "Total funding requested" + "Includes exceptional funding" (replaces the old two-line "Amount requested"/no-exceptional-funding render). `CareSupportPanel`: unconditional applicant-type/structured care-support `Definitions` block added alongside the existing gated free-text trio | FR-035 |
| `src/pages/ApplicationDetailPage.tsx` | Code App UI (comment only) | Corrected the stale panel-order header comment (`CareSupportPanel` had been unnamed since an earlier pass) | — |
| `src/test/harness.tsx` | Test | `makeDetail()` defaults extended for the five new fields | — |
| `src/dataverse/{odata,schema,repository}.test.ts`, `src/components/CasePanels.test.tsx`, `src/domain/format.test.ts` | Test | New/extended coverage for every field above, including the multiselect parser, the two re-derived option-set maps, and the OQ-031 combined-total fix | — |
| `contract/tad-deferrals.json` | Contract bookkeeping | `TD-005` deleted — stale (matched no absent TAD column; see §0.5). Not this WBS task's own deliverable | — |

### This revision (round-statistics second version, 2026-08-27)

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| `Workflows/REVPortalRoundStatistics-…json` (+`.notes.md`) | Cloud flow | 46 new `Query` (Filter array) actions, one per category value across `genderDistribution`/`ageRangeDistribution`/`applicantTypeDistribution`/`wellbeingLastYear`×3/`lifeSatisfactionDistribution`; 8 new `Compose` actions assembling each metric's `categories`/`questions` JSON; `List_applications_in_round`'s `$select` extended and a new `$expand` parameter added (`A-FLOW-06`); `Compose_response_body` rebuilt to splice the five metrics in. Trigger/`Response`/failure-path shell **unchanged** (§0.7) | FR-061, FR-062 (partial) |
| `logs/improvement-log.jsonl` | Findings | `IMP-0377` (blocker — flow unreachable by the Code App, §0.7), `IMP-0378` (friction — `if()` eager-evaluation division-by-zero, found and fixed pre-import), `IMP-0379` (friction — TAD §3.4/A-R24 stale against its own §12.1) | — |
| `logs/known-failure-modes.md` | Generated digest | Regenerated — 378 entries | — |

### This revision (TAD Revision 4 — design-system adoption, 2026-08-27)

Forty-three files under `src/code-apps/trustee-review-portal/`. **No file under `src/domain/` or
`src/dataverse/` was opened**, and neither was `theme.ts`, `theme.test.ts`, `brand.css`, `print.css`,
`print.test.ts`, `vitest.config.ts` or `package.json`.

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| `src/styles/ds-tokens.css` | **NEW** global stylesheet, 336 lines | The design system's `:root` custom properties merged from `tokens/colors.css`, `spacing.css`, `typography.css` and the `:root` block **only** of `effects.css`, with ADR-037's five corrections applied and each commented at the value it changes. `--brand-primary`/`-hover`/`-active` publish the supplied ramp's `brand[70]`/`[60]`/`[30]`; `--text-heading` publishes the supplied `#002060` (OQ-040); `--focus-ring` is `#000000`; `--text-muted` is retained but restricted to non-text use; `--success`/`--warning` are not declared at all. `--font-body`/`--font-display` carry the supplied Aptos stacks — **no `@import`, no `@font-face`, no font file** (ADR-036) | NFR-026, NFR-024 |
| `src/styles/ds.module.css` | **NEW** CSS Module, 449 lines | One class per component variant. Every button size carries `min-height: 44px` including `sm`; form-control boundaries use `--border-strong` (3.45:1) and never `--border-default` (1.34:1); no `outline: none` anywhere; no raw hex in any declaration. Carries the `A-DS-1` marker | NFR-026, NFR-024 |
| `src/components/ds/{Button,Notice,StatTile,Card,Input,Radio,Checkbox}.tsx` + `index.ts` + `classNames.ts` | **NEW**, 7 converted components | ADR-034. Props are each component's supplied `.d.ts` shape **intersected with** the DOM interface of the element rendered. All seven forward `data-print` and `role` and hardcode neither. `Button` defaults `type="button"` overridably; `Input` renders a bare `<input>` with no wrapper when given no `label`, so the existing external `<Label htmlFor>` pairings keep owning the accessible name; `StatTile` gains an `absent` state; `Notice` ships `muted`/`info`/`quiet` and **no `warning`**. No inline `style` survives on any of them | NFR-026 |
| `src/styles/ds-tokens.test.ts` | **NEW** test, 33 assertions | The A-R38 drift guard. Reads both new stylesheets off disk, strips comments, resolves `var()` alias chains, and recomputes every ratio with `theme.test.ts`'s own formula and its three fixed-point sanity checks. Makes all five ADR-037 corrections and ADR-036 mechanical; asserts the `main.tsx` and `harness.tsx` imports and ADR-034's `Designsystem/` boundary. **Falsified by eleven mutations** | NFR-024 |
| `src/components/ds/*.test.tsx`, `classNames.test.ts`, `index.test.ts` | **NEW**, 9 test files | `data-print` and `role` forwarding, the default button type, `Input`'s no-wrapper behaviour, `StatTile`'s absent path, and that each rendered element carries **no `style` attribute** — the property that keeps `print.css` winning the cascade | — |
| `src/components/Panel.tsx` + **NEW** `Panel.test.tsx` | Restyled, not replaced | `StateMessage` gains `tone` and an overridable `role` (default still `note`), rendering through the converted `Notice` as visual treatment only; `data-print="state"` unchanged. `Definitions` keeps `<dl>`/`<dt>`/`<dd>` — the mockup's markup is **refused** (§8.5 point 2). `StatTileRow` re-implemented over `StatTile`, keeping its `{label,value}[]` contract and its `<dl>`, selecting `absent` by comparing against `format.ts`'s own two absence constants, imported rather than retyped | FR-035, FR-078, FR-063 |
| `src/components/CasePanels.tsx` | Tone wiring only | One `withheldOrEmptyTone` function, typed against `visibility.ts`'s own union, used by all four redaction panels: `withheld` → filled, `released-empty` → unfilled. No domain file opened; the catalogue rendering is untouched | FR-035, FR-078, FR-079 |
| `src/pages/ApplicationsListPage.tsx`, `src/components/ApplicationsTable.tsx`, `src/components/ApplicationFilters.tsx`, `src/App.tsx` | Restyled — **WBS 6.2, first design pass** | The four changes §2.2.2 names and nothing else. All eight §2.2.1 behaviours preserved and re-verified; `role="alert"` on the error state now comes from the call site because the converted `Notice` sets none | FR-034, FR-039 |
| `src/pages/LandingPage.tsx`, `src/pages/ApplicationDetailPage.tsx`, `src/components/VerdictForm.tsx` (+ **NEW** `VerdictForm.test.tsx`), `VerdictDialog.tsx` | Restyled | Buttons onto the converted component; Fluent `Spinner`, `Dialog*`, `Field`, `Label`, `RadioGroup`, `Textarea`, `Select` and the toast all **stay** (§2.1.4). **Fluent's `Radio` also stays** — see §0.8 decision 4 | FR-035, FR-037 |
| `src/components/DistributionChart.tsx`, `RoundStatistics.tsx`, `RoundFinancePanel.tsx` | Header comments only — **no code change** | §8.5 points 3 and 4. The chart's markup, ARIA and geometry are byte-identical; every visual rule it uses is a class, so its chrome restyle happened entirely in the stylesheet. `present()` and the two screens' opposite null behaviours are untouched | FR-061, FR-063 |
| `src/styles/app.module.css` | Restyled onto the design system's tokens | `.stateMessage`/`.stateHeading`/`.stateExplanation` removed (the box is now entirely the converted `Notice`'s, so the two CSS Modules declare no property in common and the result cannot depend on which stylesheet the bundler emits first). No raw hex introduced. `.tallTarget`, `.srOnly`, `.rowLink`, `.sortButton`, `.chartBar`, `.errorBox`, `.preserveLines`, `.definitions`, `.statTiles` all retained | NFR-026 |
| `src/main.tsx`, `src/test/harness.tsx` | Stylesheet wiring | `ds-tokens.css` side-effect imported before `brand.css` before `print.css`, in **both** roots (A-R38) | — |

### This revision (TAD Revision 5 — ADR-038, 2026-08-28)

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| `Entities/rev_roundstatisticsresult/Entity.xml` | **NEW** Dataverse table | Tier 2, `OrganizationOwned`, entity-level `IsAuditEnabled=1`, alternate key `rev_roundstatisticsresult_name`, the D-018 empty `<FormXml />`/`<SavedQueries />` markers. Four attributes: `rev_name`, `rev_status` (reusing the **existing** global option set, so no new relabelling risk on import), `rev_resultjson` (`MaxLength` **100000** — carried forward from the value **proven live**, where the documented 1048576 ceiling failed `0x80040216`), `rev_computedon`. No relationship to anything. Carries the `A-RESULT-1` marker | FR-057–FR-063 |
| `Entities/rev_roundstatisticsrequest/Entity.xml` | Descriptions only | `rev_status`/`rev_resultjson`/`rev_computedon` get superseding `<Description>`s naming all five facts §3.9.2 requires. **Not deleted** — they are live in DEV, and a metadata delete would be the first irreversible one this project has ever performed, for three unread columns on a one-row table | — |
| `Other/Solution.xml`, `ensure-schema-helpers.psm1`, `provisioning/deploymentSettings/*.json` | Provisioning wiring | `RootComponent type="1"`; the logical name appended to `Get-RevEntityLogicalNames` (**A-R46** — two of the last three tables were caught by that hand-kept list, and the previous omission printed neither `EXISTS` nor `CREATED` nor `FAILED`); `auditedTables` in every settings file carrying the key | — |
| `provisioning/dataverse/seed-round-statistics-result.ps1` + `provisioning/README.md` | **NEW** provisioning script | One row, key `CURRENT`, check-before-create, `Write-ResourceStatus`'s `CREATED`/`EXISTS`/`FAILED`, `# CONVERGENCE:` per step, `Exit-Provisioning`. **Must run before the first trigger** — neither flow nor app holds Create on the table | — |
| `Workflows/REVPortalRoundStatistics-…json` (+ `.notes.md`, + a comment-only `.data.xml` edit) | Cloud flow — transport rewritten | Trigger replaced with `OpenApiConnectionWebhook`/`SubscribeWebhookTrigger`, `message` **3**, `entityname rev_roundstatisticsrequest`, `scope` 4, `runas` 3. New `Read_the_result_row` + row-count guard + two distinct alert paths (a missing row and an unreadable table have different remedies). New `Read_the_freshness_bound` on `rev_setting` with a null-safe integer parse. **All five `Response` actions replaced by `Update a row` write-backs with `item/<column>` keys flat** — the nested form writes nothing while succeeding. The 46 `Filter_*`, 8 `Compose_*`, `$expand` and `Secure Outputs` are **untouched**. Zero occurrences of `triggerBody`/`triggerOutputs`/`@triggerBody`/`rev_triggeredon`. Carries `A-FLOW-07` | FR-057–FR-063 |
| `Roles/REV Trustee/…`, `Roles/REV Service Automation/…` | Security roles | Trustee gains **Read only** on the result table; the service identity gains Read+Write on it and **loses** `prvWriterev_roundstatisticsrequest`. A stale `REV Trustee.xml` comment still asserting `prvReadWorkflow` was granted is corrected | — |
| `src/dataverse/{schema,types,client,roundStatistics,repository}.ts`, **NEW** `roundStatisticsResultReadService.ts`, `domain/landing.ts`, `pages/LandingPage.tsx` + 7 test files | Code App | Result table registered in `ENTITY_SETS`/`PRIMARY_KEYS`/`READ_SERVICES` behind an interim stand-in; the request select narrowed to the id alone; `staleAfterSeconds` added to the response contract; the poll rewritten from request identity to an age bound; the **Refresh figures** announcement changed to state the stamp, never the action. Carries `A-RES-1` | FR-056–FR-063, NFR-019, NFR-024 |
| `scripts/verify-flow-trigger-body-isolation.py` + 2 known-bad fixtures + 5 `BuildGates.Tests.ps1` blocks | **NEW** HARD build gate | `flow-reads-no-trigger-body`. Check A: the four trigger-body tokens, the trigger's own name, and `rev_triggeredon` anywhere in the definition. Check B: no reference to a **row-bearing** action reaching `item/rev_resultjson` except inside `length`/`empty`, with row-bearing **derived** from `Entities/*/Entity.xml` and propagated to a fixpoint. Fails on a missing, unparseable, trigger-less or Power-Apps-triggered target, and on an incomplete seed | §6.3.1, §6.3.3 |
| `config/…-build.yml`, `config/…-pipeline.yml`, `EnsureSchema.Tests.ps1` | Configs and counts | The new gate step; one `--allow` on `code-app-data-sources` with an owner and a clearing action; a stale comment claiming `flow-definition-language` is expected to be red **corrected**; §12.3's nine-step order transcribed with five superseded steps marked in place; the `auditOff` allowlist gains the moved column | — |
| `logs/improvement-log.jsonl`, `logs/known-failure-modes.md` | Findings | 12 entries, `IMP-0406`–`IMP-0417`; digest regenerated (414 entries) | — |

### This revision (the C-TECH-014 coverage unblock, 2026-08-28)

Dispatched after `build-agent` halted at `coverage-threshold`: 75.39% line coverage against the HARD 80% bar,
the whole gap being three seeders this feature added that no test executed (0/31, 0/31, 0/99 lines).

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| `src/tests/provisioning/DataverseScripts.Tests.ps1` | Tests — **25 new `It` blocks** in 3 new `Describe` blocks | Behavioural tests over all three round-statistics seeders, running each real script unmodified against the existing `ProvisioningTestHarness.psm1` fake Web API — the same shape the `seed-settings.ps1` block above already uses. Asserts **the request sent**: entity set, keyed PATCH never a POST, the exact column set, create-only non-reconciliation, 403-is-not-404, the DEV/TST-only refusal with **zero** calls made, the open-round guard, and the ISO-8601 wire format. Suite **56/56 → 81/81** | — |
| `provisioning/dataverse/seed-round-statistics-test-data.ps1` | **Defect fix ×2 + one behaviour change** | (1) Target table corrected `rev_roundstatisticsrequests` → **`rev_roundstatisticsresults`**: ADR-038 moved the three columns it writes, and because the request table's copies were retained-not-deleted the wrong target **succeeded silently** and left the charts empty. (2) StrictMode-safe probe: the Web API omits a null column from a response, so `$before.rev_resultjson` was a terminating `PropertyNotFoundException` on the script's own primary path. (3) A 404 on the probe now reports FAILED naming `seed-round-statistics-result.ps1` instead of upserting a second row into a one-row-ever table | FR-057–FR-063 |
| `provisioning/README.md` | Correction | Row 38's description named `rev_resultjson` without its table and omitted both the update-only contract and the `acc`/`prd` refusal | — |
| `docs/development/trustee-portal-visual-refresh-dev-summary.md` | Corrections | §5's false *"56/56 PASS discharges `IMP-0244`"* claim replaced with a citation to tests that execute the scripts; the same stale figure corrected in §11 and in the Code Review Checklist; two `forms-and-views-reachable` rows added to §11 for the two statistics tables; a split markdown table closed | — |
| `logs/improvement-log.jsonl`, `logs/known-failure-modes.md` | Findings | 4 entries, `IMP-0434`–`IMP-0437`; digest regenerated | — |

### This revision (`IMP-0438` — the request seeder's PATCH body, 2026-08-28)

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| [`provisioning/dataverse/seed-round-statistics-request.ps1`](../../provisioning/dataverse/seed-round-statistics-request.ps1#L139) | **Defect fix** | PATCH body reduced to `@{ rev_name = $requestKey }`. It previously also set `rev_status = 2` on one of the three ADR-038-superseded columns whose shipped `<Description>` reads *"Written by nothing and read by nothing"* — so the description was false about the repository that shipped it. `rev_resultjson` and `rev_computedon` were verified never to have been written by this script. Header, inline comment and the `CREATED` detail string rewritten to state what the body now is and why; the `SYNOPSIS`'s *"read and write"* claim corrected — from ADR-038 the flow never writes this table | FR-057–FR-063 |
| [`src/tests/provisioning/DataverseScripts.Tests.ps1`](../../src/tests/provisioning/DataverseScripts.Tests.ps1#L1110) | Tests — **1 `It` rewritten as a named regression lock, 1 stale assertion removed** | The `rev_status = 2` expectation deleted from the keyed-PATCH test; the column-set test rewritten to assert the four forbidden columns **by name and first** (so a failure says which one returned, not only that a count moved) and then the closed set. Suite count unchanged at **81/81** — no new `It` was needed, and none was added to avoid a count that teaches nothing | — |
| [`provisioning/dataverse/seed-round-statistics-request.ps1`](../../provisioning/dataverse/seed-round-statistics-request.ps1#L101) | **`C-TECH-042` convergence declaration added** | The script had **no** numbered step marker, so `provisioning-step-convergence` reported it `UNCLASSIFIABLE` — *"Not a pass … convergence here is unrecorded"* — and this is the dispatch where that mattered, because removing a write is the direction a create-only step can never converge. Now carries `# ── 1. …` plus a `# CONVERGENCE:` declaration stating exactly what survives in DEV and why it is deliberately left. Gate now reports **PASS — 36 numbered step(s) … 9 create-only and every one carrying a CONVERGENCE declaration** | — |
| [`provisioning/dataverse/seed-round-statistics-result.ps1`](../../provisioning/dataverse/seed-round-statistics-result.ps1#L27) | Correction | Its header justified its own `rev_status = 2` as *"identical reasoning to `seed-round-statistics-request.ps1`'s own `rev_status=2` write"* — a cross-reference to a write that no longer exists. Now states that it is the only seeder writing that column | — |
| [`Entities/rev_roundstatisticsrequest/Entity.xml`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_roundstatisticsrequest/Entity.xml#L51) | **Shipped metadata correction** | Entity-level `<Description>` said the flow writes the three answer columns on this table, contradicting the attribute descriptions 49 lines below; the file header's *"READS `rev_status`/`rev_resultjson`/`rev_computedon` back"* corrected the same way. **Beyond the dispatch's literal ask — see §0.11** | — |
| [`OptionSets/rev_roundstatisticsrequeststatus.xml`](../../src/solutions/RevitaliseGrantAutomation/OptionSets/rev_roundstatisticsrequeststatus.xml#L25) | **Shipped metadata correction** | `<Description>` described the request row's cycle. Now names `rev_roundstatisticsresult.rev_status` as the live column it types and records the deliberate `…request…` naming mismatch — which TAD §3.9.2 already claimed this description recorded | — |
| [`Workflows/…RoundStatistics….notes.md`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.notes.md#L424) | Correction | §5 named the request table's `rev_status` as the seeded resting state; now names the result table's | — |
| [`provisioning/README.md`](../../provisioning/README.md#L36) | Correction | Row 36 said the portal and flow *"read/write"* this row; now states the ask/trigger split and the `rev_name`-only body, with the correction dated | — |
| `logs/improvement-log.jsonl`, `logs/known-failure-modes.md` | Findings | 4 entries, `IMP-0447`–`IMP-0450`; digest regenerated (447 entries, 446 distinct lessons) | — |

### This revision (TAD Revision 6 — ADR-039, the four money averages and the `k = 5` gate, 2026-08-28)

| Component | Type | Change | WBS |
|---|---|---|---|
| `Workflows/REVPortalRoundStatistics-…json` | Cloud flow | **88 actions added, 105 → 193.** 84 inside `Condition_page_cap` → `else`: 15 presence `Filter array`, 20 `Select`, 20 `Compose` sums, 15 per-break-type measure composes, 10 total-row composes, 4 for FR-059. 4 more at `Compute_statistics` level: the `k` read chain. `$select` widened by exactly the three money columns; `Switch_on_open_round_count.runAfter` gains the `k` chain; `Compose_exceptional_funding_summary`, `Compose_breaktype_rows` and `Compose_breaktype_total` rewritten to splice measures **unquoted**; `A-FLOW-08`'s three markers removed as RESOLVED | `6.9` |
| `Workflows/…RoundStatistics….notes.md` | Documentation | **FIFTH VERSION section** — the action inventory, the measured XPath table, both corrections, the `k` mechanism, and what the pass did and did not prove | `6.9` |
| `scripts/verify-flow-trigger-body-isolation.py` | HARD build gate | **Check B1 extended by one anchored template** (§0.12.2), 5 new selftest cases, selftest 15 → 20, and the B1 violation message now names the template so the rejection is actionable | `6.9` |
| `src/tests/fixtures/known-bad/flow-reads-no-trigger-body/UnguardedXPathSum.json` | Known-bad fixture | **NEW.** The near-miss a future author is most likely to write, because §5.1.2 shows it literally | `6.9` |
| `src/tests/build/BuildGates.Tests.ps1` | Test | One `It` block registering the new fixture; the Describe now holds **six** blocks | `6.9` |
| `config/revitalise-grant-automation-build.yml` | Build config | The `flow-reads-no-trigger-body` comment records the exemption, its safety argument, why the allow-list route was refused, and the corrected coverage counts (20 selftest cases, 3 fixtures, 6 `It` blocks) | `6.9` |
| `src/tests/solutions/RoundStatisticsContract.Tests.ps1` | Test | **34 → 47 assertions.** The `A-FLOW-08` Describe **replaced** as its own comment instructed, not deleted; the money-column `$select` assertion **inverted** with its premise stated; a new assertion that every selected column has a reader; suppression asserted in **both** directions; the reduction template asserted byte-for-byte; one `$profile` automatic-variable warning fixed | `6.9` |
| `src/dataverse/types.ts` | Code App types | `MoneyMeasure { value, population }` added; seven fields moved from `number \| null` to `MoneyMeasure \| null` | `6.9` |
| `src/dataverse/roundStatistics.ts` | Code App parser | `parseMoneyMeasure` added — **rejects a bare number**, because a mean with no denominator is what §3.3 property 8 forbids; three parsers updated | `6.9` |
| `src/domain/format.ts` | Code App formatting | `NOT_SHOWN` — a third absence token, for money measures only, because *"Not recorded"* asserts nobody entered a value and that is false for a suppressed figure; two measure formatters rendering value **and** population | `6.9` |
| `src/components/RoundStatistics.tsx` | Code App UI | The break-type table's three money columns and the total row, plus the exceptional-funding item, render `{ value, population }`; a **threshold-agnostic** explanatory sentence in the table caption and beside the exceptional-funding figure — the app cannot name `k`, which does not travel in the document | `6.9` |
| `provisioning/deploymentSettings/{dev-scoring,test,prd}-settings.json` | Settings | `RoundStatisticsMoneyMeasureMinimumPopulation` = `5`, `Whole Number`, in **all three** — a divergence here would make the same round render differently in two environments | `6.9` |
| `provisioning/deploymentSettings/settings-rows.notes.md` | Documentation | The derivation, and why an absent row is fail-safe **but not approved** | `6.9` |
| `src/tests/provisioning/DeploymentSettings.Tests.ps1` | Test | 14 → 15 rows, plus a **cross-environment** assertion that the key is `5` in every file — the divergence is the failure this row exists to prevent | `6.9` |
| `config/revitalise-grant-automation-pipeline.yml` | Pipeline config | The `post_deploy` seeding narrative distinguishes this **decided, seeded** disclosure control from `RoundStatisticsStaleAfterSeconds`, which awaits OQ-042 and is deliberately unseeded | `6.9` |
| `contract/tad-deferrals.json` | Contract register | `UR-002` and `UR-003` **deleted** as satisfied on their own `clears_when`; `_ur_002_and_ur_003_cleared` records the five things a later reader should not have to infer | `6.9` |
| `docs/architecture/…-architecture.md` | TAD Appendix A | FR-059 and FR-060 rows corrected to **DELIVERED IN FULL**, each stating V1 and naming A-FLOW-11 — paired with the register deletion in the **same change**, which is what `_undelivered_requirements_is_read_by_no_gate` names as the condition | `6.9` |

### This revision (TAD Revision 7 — ADR-040/041/042, §0.15, 2026-08-30)

| Component | Type | Change Description | FR/ADR Reference |
|---|---|---|---|
| [`src/App.tsx`](../../src/code-apps/trustee-review-portal/src/App.tsx#L192) | Code App UI | Persistent `<nav aria-label="Screen navigation">` bar, one `<button>` per screen, `aria-current="page"` on the active one, `aria-disabled` + visible caption on "Application detail" until a case is open. Old contextual "Back to the round overview" `<button>` removed | ADR-040 |
| [`src/App.test.tsx`](../../src/code-apps/trustee-review-portal/src/App.test.tsx#L112) | Test | 1 existing test updated (the old contextual button reference), 4 new tests: landmark naming, `aria-current` on exactly one tab, disabled→enabled transition with visible reason, lateral move detail→list | ADR-040 |
| [`src/styles/app.module.css`](../../src/code-apps/trustee-review-portal/src/styles/app.module.css#L57) | Stylesheet | `.page` gains `padding-top: var(--space-5)` (header band correction, §0.10.1); `.statTiles` minmax floor `160px` → `240px` (ADR-041 part 1); new `.viewNav`/`.viewNavButton`/`.viewNavButtonSelected`/`.viewNavButtonDisabled`/`.viewNavCaption` classes, reusing already-verified colour pairs only; `.backNav` retired | ADR-040, ADR-041 |
| [`src/styles/ds.module.css`](../../src/code-apps/trustee-review-portal/src/styles/ds.module.css#L309) | Stylesheet | `.statTile` gains `container-type: inline-size`; `.statTileValue`'s `font-size` becomes `clamp(var(--text-lg), 6cqi, var(--text-2xl))` — independent of, and does not touch, `IMP-0509`'s `line-height` fix on the same class | ADR-041 |
| [`src/styles/ds-tokens.css`](../../src/code-apps/trustee-review-portal/src/styles/ds-tokens.css#L359) | Stylesheet | Two `@font-face` rules (Playfair Display, weights 400/700, local `data:` URIs); `--font-display` repointed at the Playfair Display stack; header comment rewritten from "REFUSED" to the ADR-042 decision | ADR-042 |
| [`src/theme.ts`](../../src/code-apps/trustee-review-portal/src/theme.ts#L215) | Code App source | `REV_FONT_FAMILY_HEADING` changes from the named Aptos Display stack to the self-hosted Playfair Display stack; header comment ("THE FONT LICENCE FINDING") extended to explain why the two font constants are now treated differently | ADR-042 |
| [`src/styles/brand.css`](../../src/code-apps/trustee-review-portal/src/styles/brand.css#L38) | Stylesheet | `--rev-font-family-heading` (the global `h1`–`h6` rule) repointed the same way, kept byte-identical to `theme.ts` per the file's own guard | ADR-042 |
| [`src/assets/fonts/playfair-display/`](../../src/code-apps/trustee-review-portal/src/assets/fonts/playfair-display) | New asset | Real Playfair Display woff2 files (400, 700, latin, normal) plus `OFL-LICENSE.txt`, sourced from `@fontsource/playfair-display@5.3.0` (npm) — kept for provenance; the bytes actually shipped are the base64 copies embedded in `ds-tokens.css` | ADR-042 |
| [`src/pages/LandingPage.tsx`](../../src/code-apps/trustee-review-portal/src/pages/LandingPage.tsx#L315) | Code App UI | `<h2>Figures of this round</h2>` added immediately before `<RoundStatistics>`, `kind === "figures"` branch only | §0.10.2 |
| [`src/pages/LandingPage.test.tsx`](../../src/code-apps/trustee-review-portal/src/pages/LandingPage.test.tsx#L342) | Test | 3 new tests: heading present and precedes `RoundStatistics`'s own freshness line; absent while loading; absent on a diagnostic state | §0.10.2 |
| [`src/styles/ds-tokens.test.ts`](../../src/code-apps/trustee-review-portal/src/styles/ds-tokens.test.ts#L354) | Test | Font guard rewritten (permits the new local `@font-face`, still forbids `@import`/`googleapis`/a remote `url()`); new describe block asserting the container-query clamp's shape; `IMP-0509`'s line-height test generalised to check both ends of the clamp, not one fixed size; the `:root`-only structural check now also permits `@font-face` | ADR-041, ADR-042 |
| [`src/theme.test.ts`](../../src/code-apps/trustee-review-portal/src/theme.test.ts#L254) | Test | The single "both stacks end in sans-serif, contain 'Segoe UI'" test split into two — body (unchanged) and heading (now asserts a serif fallback chain and the Playfair Display name) — plus the `brand.css` cross-check's expected first family updated | ADR-042 |
| `logs/improvement-log.jsonl`, `logs/known-failure-modes.md` | Findings | 1 entry, `IMP-0513` (a reusable capability — the `@fontsource` font-self-hosting route); digest regenerated (510 entries, 509 distinct lessons) | — |

## 3. Data Model Changes

Per TAD §3.5 and §3.2.1, both closed with live evidence this session (not merely authored):

- **`rev_roundfinance`** — Tier 2, `OrganizationOwned`, no relationship to any other table. Live: 13
  attributes confirmed via `EntityDefinitions(LogicalName='rev_roundfinance')/Attributes`; alternate key
  `rev_roundfinance_name` confirmed `EntityKeyIndexStatus=Active` (no async wait needed); `EntitySetName`
  confirmed `rev_roundfinances`, `PrimaryIdAttribute` `rev_roundfinanceid`.
- **`rev_application.rev_caresupportdescriptionredacted` / `rev_careprovidedexampleredacted` /
  `rev_othercareprovidedtyperedacted`** — `ntext`, `MaxLength` 4000, `IsSecured=0`, `IsAuditEnabled=1`, shape
  copied from `rev_narrativeredacted`. Live: all three confirmed present on `rev_application`.

### Revision 0.9 — one table becomes two, and the boundary is the control

**`rev_roundstatisticsresult`** (TAD §3.9.3) — Tier 2, `OrganizationOwned`, one row, alternate key on
`rev_name`, no relationship to anything. Four attributes: `rev_name`, `rev_status` (the **existing** global
option set `rev_roundstatisticsrequeststatus`, so no new option set and no new import-relabelling risk),
`rev_resultjson` (`ntext`, `MaxLength` 100000, unaudited), `rev_computedon`. **Not personal data** — no data
subject, no application or applicant reference, no free text, which is §3.3 property 6 restated as a schema
fact. **V2 only: the table does not exist in DEV**, and `C-TECH-050` means no import will create it.

**`rev_roundstatisticsrequest` keeps `rev_name` + `rev_triggeredon` and loses nothing.** Its `rev_status`,
`rev_resultjson` and `rev_computedon` stay declared with superseding descriptions. That is not tidiness
deferred — a live metadata delete is irreversible, is performed by no script in `provisioning/`, and would be
the first this project has ever executed, which is a poor trade for three unread columns on a one-row table.

**Why a table boundary and not column-level write control, stated because the obvious fix looks available.**
Dataverse has `CanUpdate`, and this solution already authors it. It governs only `IsSecured=1` columns — and
securing a column the trustee must *read* requires the trustee group team to join a field security profile,
which `no-trustee-in-column-security-profile` forbids and which is the entire substance of ADR-002;
independently, securing a column the app `$select`s fails `no-secured-columns-in-code-app`. Two HARD gates,
pointing the same way, both correct. So the control is a **table privilege** — and it is the better one:
enforced by the coarsest thing in this security model, needing no profile membership, no column flag and no
per-environment state, and it removes the self-trigger hazard by construction because the flow never writes
the table it triggers on.

**What this actually closes.** `IMP-0401` recorded that any trustee could overwrite the aggregate every other
trustee sees, on one Organization-owned row with Global Write, with `IsAuditEnabled=0` on the document itself
— so the one overwrite that matters left no audit trail at all. After the split the only identity that can
write `rev_resultjson` is the service identity, which is why the same audit flag was a defect yesterday and
is a documented decision today.

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

**This revision (round-statistics second version, 2026-08-27) — five more metrics, no shell change.**
`List_applications_in_round`'s `$select` gains `rev_wellbeinganswer8/9/10,rev_feelingscaleanswer` (already
live on `rev_application`, no join) and its `parameters` gains one new key,
`$expand: "rev_applicantid($select=rev_gender,rev_agerange,rev_applicanttype)"` — ground-truthed live against
DEV (the lookup's navigation property name via `ManyToOneRelationships`, and the exact nested-object shape
via a live `$expand` call returning `rev_applicantid: {rev_gender, rev_agerange, rev_applicanttype}` on each
row), but **the connector's own acceptance of a literal `"$expand"` parameter key remains open** — no flow in
this solution has used `$expand` before (`A-FLOW-06`, §10). Inside the `else` branch of `Condition_page_cap`,
46 new `Query`-type (Filter array) actions tally one category value each — `equals(item()?['rev_applicantid']
?['rev_gender'], N)` and equivalents — run in parallel (`runAfter: {}`, no connector I/O), followed by 7
`Compose` actions assembling each metric's `categories` JSON array from `length(body('Filter_...'))`, plus one
more (`Compose_wellbeing_questions`) wrapping the three wellbeing questions into §3.3's `questions` array.
`Compose_response_body` is rebuilt to splice all five in; every literal it previously carried is unchanged.
**None of this touches the trigger, the `Response` actions, or the D-02/D-10 failure path** — every new
action lives inside the existing `Compute_statistics` Scope, so `Find_the_failed_action` → `Alert_on_failure`
covers it without modification.

**Percentage arithmetic — a genuine defect caught before import, not accepted on faith.** A first draft
guarded the zero-population case with `if(equals(population,0),0,mul(div(float(count),float(population)),
100))`. Microsoft's own function reference states `if()`'s "Parameters are evaluated from left to right" —
all three arguments are evaluated regardless of which is returned — so that draft still divided by a literal
zero on a genuinely empty round. Shipped instead: `mul(div(float(count),float(max(population,1))),100)`,
which never divides by zero and gives the same correct answer whenever population is zero. Verified by
writing a small evaluator for the exact expression vocabulary this file's new actions use and running it
twice: against a 271-row synthetic round with three deliberately-null genders (every category summed to
population exactly, except gender, which summed to population minus the three nulls — proving a null answer
is neither miscounted nor silently absorbed into a real category), and against a genuinely empty round (every
category resolves to `count:0`/`percentage:0`, no error). Logged as `IMP-0378`.

**`rev_setting` — deliberately not read this revision.** The handoff names `rev_setting` (FR-062 thresholds)
alongside the read list, inherited from TAD §5.1's own "Reads" row, but none of the five metrics this
revision adds is one of the three OQ-039 proportions those thresholds gate. Reading it here would add a live
call for a value nothing in this revision's scope consumes; left for whichever dispatch closes OQ-039.

### Revision 0.9 — the transport is rewritten; the computation is not touched

**Trigger:** `OpenApiConnectionWebhook` / `SubscribeWebhookTrigger` on `shared_commondataserviceforapps`,
`message` **3**, `entityname rev_roundstatisticsrequest`, `scope` **4**, `runas` **3**. `scope` and `runas`
are copied verbatim from the shape proven live on `REVScoringCalculateAndFlag`, not re-derived — `runas: 4`
packs, imports and reports `Activated` while registering no webhook at all. `message` is **3 and not the
ADR's 2**, on live measurement (§0.9.1).

**`filteringattributes` is deliberately absent.** It appears in no flow in this solution, so it is an
unverified connector parameter, and after the split it would narrow a single-element set: `rev_triggeredon` is
the only mutable column left on the trigger table, and the flow writes a different table entirely. Recorded in
the flow's `notes.md` so a later session does not add an unproven parameter to solve a problem the schema
already solved.

**Four things added, and one thing deleted five times over.** `Read_the_result_row` (`List rows`,
`rev_name eq 'CURRENT'`, `$top: 2`) with a row-count guard — never `Get a row by ID` on the alternate key,
which the connector rejects and which cost the scoring flow all eleven of its first live runs.
`Read_the_freshness_bound` on `rev_setting`, null-safe, emitting a JSON number when present and the literal
`null` when absent or non-numeric. `staleAfterSeconds` spliced into **all five** documents, beside `metrics`
and never inside it. And two distinct alert paths, because a missing seed row and an unreadable table have
different remedies and one message would send whoever is on call to the wrong place — without the second, a
missing privilege on the new table would have been a bare run failure with no alert at all, since this read is
now the flow's first Dataverse call. Deleted: all five `Response` actions, replaced by `Update a row`
write-backs with `item/<column>` keys **flat beside** `entityName` and `recordId`.

**The `item/` flattening is the single most dangerous line in this revision.** The connector is asymmetric —
`CreateRecord` accepts a nested `"item": { … }`, `UpdateRecord` does not, and the nested form renders in the
designer as an action with *no properties configured* and **writes nothing while succeeding**. A green run and
an empty column is the only symptom. It is verified structurally rather than by eye, by
`verify-flow-definition-language.py` check 3 and by a local validator, and the live confirmation is named in
the pipeline's own verification step: after the first observed effect, read `rev_resultjson` and confirm it is
non-empty.

**`rev_status` per path, read from the option set rather than assumed** —
`OptionSets/rev_roundstatisticsrequeststatus.xml`: `Write_ok_result` writes **2** (Complete); the four
diagnostic and failure paths write **3** (Error). `1` (Pending) is written by nothing: the flow never claims to
be starting, only to have finished. The three business outcomes take Error rather than Complete because §3.3
property 4 makes any non-`ok` status a no-figures state, and calling that Complete would put the one *audited*
column in disagreement with the document beside it — the precise reason always lives in `rev_resultjson.status`,
which carries all five values.

**The 54 compute actions, the `$expand` and `Secure Outputs` are untouched.** Only `Compose_response_body`
changed inside the computation, to splice one field. `Secure Outputs` stays on the row-reading actions and is
deliberately **not** on the write-backs, so the non-personal aggregate remains the run-history record of what
a board was shown.

**One accepted deviation from this dispatch's own instruction, and it is the right one.** The instruction said
`Read_the_result_row` must be the flow's *first action*; §3.3 property 5 says `computedOn` is captured *before
any read*. Read literally, both cannot hold. The flow does `Capture_computedOn` → `Initialise_failure_detail`
→ `Compose_run_link` → `Read_the_result_row`: nothing before the read touches Dataverse, so the stamp is still
before every read **and** the result row is still the first table read, a whole scope ahead of the privileged
one — which is what §5.1.1 point 4's stated purpose actually requires. Accepted.

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

### Revision 0.9 — the rollout order is the deliverable, so the config says so

| Key | Environment | Notes |
|---|---|---|
| `dataverse.auditing.auditedTables` | dev, test, prd | `rev_roundstatisticsresult` appended to **every** settings file that carries the key. A-R30's sequence applied to a second table: the switch is entity metadata no import sets or clears, so a table absent from this list is a table nobody switches on |
| `rev_setting` row `RoundStatisticsStaleAfterSeconds` | — | **Deliberately not added anywhere.** OQ-042 is open and the TAD's stated default is to leave the row unseeded, which makes the freshness bound `null` and reproduces Revision 2's recompute-every-mount behaviour exactly. Confirmed absent in DEV. `settingRows` is a flat array of `{key, value, dataType, description}` and `seed-settings.ps1` validates every row before writing any, so there is no mechanism to declare a key without a value — and inventing a number would put a figure of unknown provenance in front of a board |

| Script | Purpose | Pipeline Block | Idempotency Check |
|---|---|---|---|
| `seed-round-statistics-result.ps1 -Env <env>` | The single `rev_roundstatisticsresult` row, key `CURRENT`. **Must exist before the first trigger fires** — the flow updates it and holds no Create privilege on the table, and neither does the app | `dev.post_deploy` (§12.3 step 4b) | Check-before-create, `CREATED`/`EXISTS`/`FAILED` via `Write-ResourceStatus`, `# CONVERGENCE:` per step, `Exit-Provisioning`. **Behaviourally tested, mocked Dataverse:** 8 `It` blocks in [`DataverseScripts.Tests.ps1`'s own `Describe`](../../src/tests/provisioning/DataverseScripts.Tests.ps1#L1216) execute the script's real logic — the keyed-PATCH upsert (never a POST), the columns it writes and the two it must not, the create-only non-reconciliation, the 403-is-not-404 rethrow, and both `-Env dev` paths |

**Correction, 2026-08-28 — the claim this row used to make was false, and it is the exact shape `logs/known-failure-modes.md` warns about.** It read *"Not asserted — measured: `Invoke-Pester DataverseScripts.Tests.ps1` → 56/56 PASS, which is `IMP-0244`'s requirement discharged."* That suite's 56 tests never executed a single line of any of the three round-statistics seeders: `grep -rln "seed-round-statistics" src/tests/` returned nothing, and the container only checked generic conventions (calls `Exit-Provisioning`, uses the right status vocabulary, appears in the README). Line coverage measured **0 of 31, 0 of 31 and 0 of 99 executed lines**, which is what took C-TECH-014 to 75.39% and halted the build. `IMP-0433` is that lesson, recorded before this dispatch began; the citation is now to tests that run the scripts.

**Seven pipeline steps replace five, and the ORDER is what the TAD calls the deliverable.** TAD §12.3's
nine-step sequence is transcribed into `dev`'s `environment_prerequisites`, `post_deploy` and `verification`
blocks with each step's own reason for being where it is. The five superseded steps — flow-creation-in-
solution, the designer save with run-only sharing, the *"run only users"* connection setting, `pa app add
flow`, and the tenant DLP confirmation — are **marked in place, not deleted**, because a deleted step takes
with it the record of what was tried, and that record is what stops a third attempt at a mechanism that has
already crashed this app's boot twice.

**Three closures worth naming, because each removes work rather than adding it.** The DLP step is closed by
**removing the connector that raised it**, not by reading the policy: every connector in this feature, on both
sides, is now `shared_commondataserviceforapps`, so `C-TECH-045` becomes a positive statement with nothing
pending. `pa app add flow` is replaced by `pa app add data-source --table rev_roundstatisticsresult` — the
same verb on the same connector, one more table, an operation already performed on this app without incident.
And the *"run only users"* setting simply does not exist for a row-triggered flow, so **A-R33 retires** and its
control moves from unexpressible environment state into `subscriptionRequest/runas: 3`, which travels in the
workflow JSON and is diffable. A-R33's falsifiable **check** is carried forward verbatim as A-R45 rather than
retired with it.

`python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml` passes — **104
steps across 3 environments, 46 executable / 58 manual**, every `.ps1` parameter resolved against the
script's own `param()` block and every repo path resolved.

### Revision 0.11 — the request seeder's PATCH body, and the one thing a re-run cannot fix

| Script | Purpose | Pipeline Block | Idempotency / Convergence Check |
|---|---|---|---|
| [`seed-round-statistics-request.ps1 -Env <env>`](../../provisioning/dataverse/seed-round-statistics-request.ps1#L139) | Seeds the single ask row. **Body reduced to `rev_name` only** (`IMP-0438`) | `dev.environment_prerequisites` (already run; the pipeline's own STEP 4b note records the row live) | Create-only, unchanged and still correct: a run that finds the row reports `EXISTS` and issues no PATCH. **That is also why this fix does not converge DEV** — the live row keeps the `rev_status = 2` the old body wrote, and no re-run will clear it (`C-TECH-042`'s create-only clause, the `IMP-0259` shape). Recorded as `IMP-0449`, deliberately not repaired: the column is read by nothing, and clearing it means a live PATCH against a column this solution declares unused |

No settings file, pipeline step or `auditedTables` entry changed in this revision.

**And one thing the corrected `<Description>` text does *not* do: reach DEV.** `ensure-schema.ps1`'s global-option-set step and its entity/attribute step are both declared [`# CONVERGENCE: UNRESOLVED`](../../provisioning/dataverse/ensure-schema.ps1#L358) — an existing option set or entity is reported `EXISTS` and its labels are never re-PUT. The request table and its option set already exist in DEV (created 2026-08-27), so DEV keeps the pre-ADR-038 wording until a solution **import** carries the new text. That is the same create-only mechanism as the `rev_status` residue above, one level up in the metadata, and it is stated here rather than left for someone to discover by opening the table in the maker portal.

### Revision 1.1 — one seeded setting, and it is a disclosure control rather than a tunable

`RoundStatisticsMoneyMeasureMinimumPopulation` = **`5`**, `Whole Number`, in all three environment settings
files, seeded by the existing `seed-settings.ps1` upsert (no script change — the row is data). Three
properties worth stating, because the surrounding rows do not share them:

- **It is seeded, not left unseeded.** An absent row withholds all four money measures, which is fail-safe
  and is **not** the approved behaviour (TAD §12.1). `RoundStatisticsStaleAfterSeconds` is the opposite case
  and stays unseeded, because OQ-042 is open and unseeded is *its* documented fail-safe.
- **It is not the process owner's to change.** The three FR-062 thresholds and the freshness bound are
  tunables. This is a disclosure control answering OQ-043, and changing it is a reviewer decision (§6.3.5).
- **A DEV/TST divergence would make the same round render differently in two environments**, which is why
  `DeploymentSettings.Tests.ps1` now asserts the value across all three files rather than counting rows.

**Not verified: that the row exists in any environment.** Seeding is a `post_deploy` step and no source-side
gate can see it. Until it runs, a real trustee sees every count and no money figure — correct behaviour,
withholding, and indistinguishable from a genuine below-threshold round.

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

### Revision 0.9 — the write boundary becomes a table privilege, and one control gets teeth

| TAD §6 control | Implementation | Verified |
|---|---|---|
| **The write boundary (§3.9, §6.3.2) — this is what closes `IMP-0401`** | Two tables, not one. `REV Trustee` holds Read+Write on `rev_roundstatisticsrequest` and **Read only** on `rev_roundstatisticsresult`; `REV Service Automation` holds Read on the request table and **Read+Write only on the result table**, with `prvWriterev_roundstatisticsrequest` removed from source. Neither party writes the other's table, and the flow never writes the table it triggers on. Enforced by a **table privilege** — the coarsest and least bypassable control in this model, needing no profile membership, no column flag and no per-environment state | Source: `verify-role-privilege-ownership.py` PASS (92 privileges / 3 roles); `EnsureSchema.Tests.ps1` **45/45** under Pester 5.7.1. **Live: NOT yet** — the privileges do not exist in DEV because the table does not, and two stale grants still need the manual revoke at §12.3 step 8 (§0.9.3) |
| Column-level write control was the obvious fix, and it is unreachable | Recorded rather than attempted. `CanUpdate` is a real `FieldPermission` element this solution already authors, but it governs only `IsSecured=1` columns — and securing a column the trustee must *read* needs the trustee team in a profile, which `no-trustee-in-column-security-profile` forbids and which is the entire substance of ADR-002; independently, securing a column the app selects fails `no-secured-columns-in-code-app`. Two HARD gates, pointing the same way, both correct | `verify-column-security-membership.py` PASS — **no profile membership changed at all** this revision |
| **No caller-supplied value reaches the privileged computation (§1.5 point 4, §6.3.1)** | The flow reads **nothing** from its trigger body. Zero occurrences of `triggerBody`, `triggerOutputs`, `@triggerBody` or `rev_triggeredon` in the definition — it re-reads what it needs by its own queries | **Now a HARD build gate, not a sentence.** `flow-reads-no-trigger-body` (`scripts/verify-flow-trigger-body-isolation.py`) — checks A1/A2/A3, PASS |
| **The result document is aggregate-only (§3.3 property 6, §6.3.3)** | Every key composed by name; no action puts a `List rows` item, or anything derived from one, into `rev_resultjson` | **Check B of the same gate**, PASS. Its personal-data seed is **derived** from `Entities/*/Entity.xml` (any table with an `IsSecured=1` attribute) rather than hand-typed, and an incomplete derivation fails the gate rather than passing quietly. **The live half is `test-agent`'s** — assert the produced document's key set equals §3.3's, every leaf a number, `null`, or an ISO timestamp or round key. No read-side column gate in this repository could ever see a row serialised into this column |
| Auditing on the new table (`C-DOM-010`/`011`, `C-TECH-064`) | `IsAuditEnabled=1` on three of four attributes; `rev_resultjson` deliberately off, and now a **documented decision rather than a default** — what makes it acceptable is the write boundary, not the description: after the split the only identity that can write it is the service identity, so *"who changed this"* has exactly one possible answer. Under the single-table shape it had as many answers as there are trustees | `domain-invariants` PASS, reporting the exclusion as a NOTE — the gate working as designed, an exclusion visible rather than silent. **Table-level switch: not yet live** (A-R30, §12.3 step 4a) |
| `prvReadWorkflow` | **Withdrawn.** §6.1 called it *"the one place this feature widens a trustee's platform reach"*; nothing invokes a flow any more, so the role's reach returns to tables only and `C-TECH-046` is not even considered | Source: absent. **Live: still bound** — §0.9.3, and the post_deploy read-back is expected to fail until the manual `$ref` delete |
| Least privilege (`C-DOM-020`) | Strictly stronger than §6.4 recorded: five narrow grants become four, one of them read-only, and the one class that widened platform reach is gone | `verify-role-privilege-ownership.py` PASS |

## 7. Known Limitations / Deferred Items

### Revision 0.9 — what is built, and the four things that are not

1. **The observed-effect assertion has not been performed, and nothing in this dispatch could perform it.**
   TAD §12.3 step 7: write `rev_triggeredon`, wait, assert `rev_computedon` on the **result** row changed.
   Everything cheaper is inadmissible — `statecode`, a `callbackregistration`'s existence or `createdon`,
   `scope`, `runas`, and a **Resubmit** (`C-TECH-064` clause (a)). This matters more than usual because of
   **A-R47**: an unregistered trigger and a slow computation are indistinguishable from the screen, both
   rendering `pending`, so a permanently dead feature would report *"still working"* to every trustee forever
   with every source-side gate green.
2. **Two stale privileges are live in DEV** and cannot be revoked by any script here (§0.9.3). The read-back
   that proves it is expected to fail first — that is the point.
3. **`rev_roundstatisticsresult` does not exist in DEV**, so `A-RESULT-1` (its platform-assigned entity set
   name) stays OPEN, the app ships an interim hand-written stand-in read service on
   `roundFinanceReadService.ts`'s precedent, and §12.3 step 9's `pa app add data-source` is what closes both.
4. **`staleAfterSeconds` is `null` everywhere**, deliberately (OQ-042). The screen therefore behaves exactly
   as Revision 2's did — every mount recomputes — and the concurrency collapse ADR-038 buys is available but
   unexercised. Nothing blocks on it and it needs no deployment to introduce.

**Item 3 above is CLOSED by revision 1.2 (2026-08-29, `IMP-0485`).** `rev_roundstatisticsresult` now exists
live in DEV, `A-RESULT-1` closes at E1, and the interim stand-in is deleted — `client.ts`'s `READ_SERVICES`
now points at the generated `Rev_roundstatisticsresultsService`. See §0.13, §10 and §11 for the full record;
left above unedited as the state that was true when this revision was written.

**One item this revision CLOSES from §0.7, and it is the one that mattered.** The `blocker` `IMP-0377` said
the flow *"cannot currently be invoked by the Code App at all"* and that closing it *"needs a superseding ADR
(ADR-030 superseded or amended) before any session hand-authors the flow's new trigger shape."* ADR-038 is
that decision and this revision is its implementation: the flow no longer needs to be invoked, because
nothing invokes it. The paragraph below is left as the record of the state that produced the finding.

**New, revision 0.7 (2026-08-27), and the most important item in this section:** **the flow cannot currently
be invoked by the Code App at all**, regardless of this revision's own metric-computation work — see §0.7.
`IMP-0358`/`IMP-0359`/`IMP-0365` establish that the trigger/`shared_logicflows` mechanism this flow still
carries has twice crashed the Code App's boot, and a concurrent, uncommitted session has already moved the
app's own invocation mechanism to a Dataverse-row-trigger/write-back design (`rev_roundstatisticsrequest`)
this flow does not yet implement. Logged as `IMP-0377` (`blocker`). Resolving it needs a superseding ADR
(ADR-030 is now the wrong design) and a rewrite of the flow's trigger/`Response` shell — an architecture
decision, not something this dispatch made unilaterally. Everything else in this section describes the flow
as it stands; none of it is reachable by a real trustee until this is resolved.

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
- ~~The flow still computes only `applicationsReceived`.~~ **PARTIALLY CLOSED, revision 0.7 (2026-08-27,
  §0.7).** `genderDistribution`, `ageRangeDistribution`, `applicantTypeDistribution`, `wellbeingLastYear` and
  `lifeSatisfactionDistribution` are now computed. Still `null` by design: `ethnicGroupDistribution` (no
  data source in scope, A-R24), `applicationsPerDay`, `exceptionalCircumstanceMix`,
  `exceptionalFundingSummary`, `breakTypeProfile`, and the three OQ-039 proportions (thresholds still unset).
  The landing screen was already built against the full contract, so nothing on the UI side blocks any of
  this revision's five metrics appearing — **but the flow itself is not reachable by the Code App at all
  yet**, so none of them will actually reach a trustee's screen until the new item at the top of this
  section is resolved.
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
- ~~A gap FR-035's own frontend-agent dispatch surfaced and correctly left alone: TAD §3.2 describes
  `rev_careprovidedtype`, `rev_carehoursperweek` and `rev_applicanttype` as "already shipped" and
  trustee-visible, but none of the three is actually wired anywhere in `trustee-review-portal` today.~~
  **CLOSED, revision 0.5 (2026-08-27), reviewer directive.** All three are now wired: type of break renders
  on `HolidayPanel`; the structured care-support pair and applicant-type context render unconditionally on
  `CareSupportPanel`, alongside the still-gated `…redacted` free-text trio. TAD §3.2's "already shipped"
  claim is therefore now true rather than corrected — the columns were always live; the app-side wiring is
  what was missing, and it is what this revision built. See §0.5 for the full account, including the new
  `A-TR-13` assumption and the four fields' exact placement.
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

### Revision 1.0 — what the four statistics metrics do and do not now deliver (`wbs:6.9`, 2026-08-28)

**FR-058 is delivered in full. FR-059 and FR-060 are PARTIAL, and the partial half is one bounded platform
limit rather than four separate gaps.** Erratum 5.3 recorded these four response fields as literal `null`
(D-11). The reviewer directed the build; what follows is exactly what shipped, stated so that no Appendix A
row can read above its evidence a second time.

| Requirement | Delivered this revision | Still `null`, and why |
|---|---|---|
| **FR-058** | `applicationsPerDay` — `{value, openedOn, days}`, the round's count over whole elapsed days since `rev_roundopenedon`, floored at 1 | **Nothing.** Complete. `UR-001` deleted from `contract/tad-deferrals.json` |
| **FR-059** | `exceptionalCircumstanceMix` complete (4 `Filter array` actions, values from `OptionSets/`); `exceptionalFundingSummary`'s `population`, `anyCount`, `anyPercentage` | `exceptionalFundingSummary.averageAmountRequested` — FR-059's third ask. `UR-002` narrowed, not deleted |
| **FR-060** | Per-break-type application **count** (5 `Filter array` actions) and a real **total-row count** | `averageCost`, `averageAmountRequested`, `percentageOfCost` — 3 of FR-060's 4 measures. `UR-003` narrowed, not deleted |

**One cause for all four remaining nulls, and it is a platform limit, not a scope choice.** The workflow
definition language's math functions are `add, div, max, min, mod, mul, pow, rand, range, sub`, and `add`
takes exactly **two** operands. A sum over a **fixed** operand count is expressible by nesting `add()` —
which is precisely why FR-060's five-operand total-row count *is* delivered — and a sum over a
**variable-length** array is not expressible at all. Every remaining null is a mean or ratio over a filtered
subset of the round. TAD §5.1's *"tallies them with array expressions (`length(filter(...))` and
equivalents)"* is where this went unnoticed: there is no equivalent for a sum, and the word "equivalents"
carried an assumption nobody had tested.

**This is now an architecture decision and was deliberately not taken here.** Three mechanisms exist and
each costs something the reviewer should weigh, so `architect-agent` owns it (TAD §0.8.1, A-FLOW-08):
an `Apply to each` accumulation is proven mechanically but turns a declarative tally into roughly 900
sequential action executions and would break TAD §3.3 point 5's *"reads as seconds old"*;
`xpath(xml(...),'sum(...)')` is one action but unverified on this tenant, and a silent `0` on malformed input
would put a **wrong money figure on a board pack**, which is worse than an absence; reopening ADR-030's
rejection of a Dataverse Custom API is the third. Picking one trades a load-bearing property of an approved
design against an unverified platform contract.

**A disclosure consequence worth reading before that decision, not after it.** The three money columns
(`rev_costs`, `rev_amountrequested`, `rev_additionalamountrequested`) are deliberately **not** in the flow's
`$select` today, because nothing computes over them — the privileged read grew by exactly three unsecured
categorical columns and by nothing else. Whichever mechanism is chosen **will** widen that read, and TAD
§6.3.3's own tripwire (*"suppression becomes mandatory the moment any filter, cross-tabulation or round
selector enters this mechanism"*) deserves re-reading at that moment: a per-break-type conditional **mean**
is arguably not the one-dimensional marginal the reviewer's no-suppression decision was reasoned about.

**No small-cell suppression was added, and that was not an oversight.** The dispatch asked for "no cell
smaller than a safe threshold". SDD NFR-027 was **withdrawn by an explicit reviewer risk-acceptance decision
dated 2026-08-25**, and SDD FR-059's own requirement text states *"No minimum-cell-size rule applies"*. TAD
§6.3.3 records the same decision as twice-given, and §6.3.4 argues that suppression would not even help the
residual risk it accepts. Adding a threshold would have re-imposed a control the reviewer overrode, changed
what a trustee sees, and contradicted three approved documents. Raised at the gate rather than actioned
silently in either direction.

### Revision 1.1 — what the four money measures now deliver, and the five things still open (`wbs:6.9`, 2026-08-28)

**Delivered:** all four measures compose, each as `{ value, population }` carrying its **own** denominator,
each gated on `k`. `UR-002` and `UR-003` are deleted from `contract/tad-deferrals.json` as satisfied and TAD
Appendix A's FR-059/FR-060 rows now read DELIVERED IN FULL with V1 stated. **Open, and each is a different
kind of open:**

1. **`A-FLOW-11` — `xml()` and `xpath()` have never run on this tenant.** The single thing between these
   figures and a screen. Closable by one live run, and §12.2's own wording is why the test works: *"A
   populated average alone proves nothing — it is the shape a naive unguarded expression also produces on
   data that happens to be complete."* Three residuals inside it, and they fail differently: an `xpath()`
   return type `float()`/`div()` reject **throws** (fail-loud, no wrong number possible); a money value
   serialised in **exponent** notation, or arriving as a non-numeric string, makes the sum `NaN` and the
   document unparseable, which reaches a trustee as `pending` — bounded rather than eliminated, because .NET
   only formats a double that way at magnitudes far outside any grant amount.
2. **`A-FLOW-12` — FR-060's *"including exceptional funding"* is a reading** (§0.12.3). One reviewer sentence
   closes it; one expression per break type if the answer is the base ask alone.
3. **The `k` row is not seeded in any environment yet**, because seeding is `post_deploy`. Until it runs
   every money figure is withheld, which is correct and is **indistinguishable from a genuine
   below-threshold round** — so a first live look showing no money figures is not evidence of a defect.
4. **The screen cannot name the threshold.** `k` does not travel in the response document, so the
   explanatory sentence is threshold-agnostic — *"shown only where enough applications in that row carry a
   figure"* — rather than *"fewer than 5"*. Deliberate: the alternative is the app hardcoding a disclosure
   control it does not own. If the reviewer wants the number on screen, `k` becomes a field in §3.3's
   contract and that is an architecture change, not an app change.
5. **`A-R52`'s second exposure is unchanged and remains accepted by record.** `k = 5` closes the
   population-of-one case completely. It does **not** bound the two-poll delta, because that arithmetic works
   on differences between whole published sums at any value of `k` — and with a money mean the delta yields
   an exact figure rather than one of five categories. Nothing in this dispatch presents the threshold as
   doing more, which is §6.3.4's own warning applied to `k`.

**Out of scope and flagged rather than fixed:** the declared check-7 exception on this flow's
`Find_the_failed_action` now hides 84 more actions than when it was declared (§0.12.4), so a failure in any
of the new actions reaches the alert as a wrapper message. Clearing it is two `Query` actions **plus** a
source-level regression test in the same change — `IMP-0346`'s recorded shape — and it is dated 2026-09-30.

### This revision — TAD Revision 7 (§0.15, 2026-08-30)

1. **`A-R54` — container-query support in the Code App host's own WebView2 build stays genuinely unverified.**
   Confirmed in real evergreen Chromium (Playwright) that the mechanism works exactly as designed — see §11 —
   but that is not evidence about the specific WebView2 build this host embeds. TAD §12.2's own closing step
   (open the live app as a real trustee, compare a tile's computed `font-size` at two column counts) is a V4
   step this dispatch had no live credential or signed-in session to perform. The declared failure mode if
   unsupported is a safe, silent degrade to the unclamped `--text-2xl` — never a broken render.
2. **`A-R53` is CLOSED, not deferred** — see §0.15 point 5. Recorded here only so a reader scanning "Known
   Limitations" does not mistake it for still open.
3. **The TAD's own header still reads "Not yet reviewed" for Revision 7.** This dispatch built against the
   reviewer's dispatch instruction to combine ADR-040/041/042 into one build, not against a recorded
   `APPROVED` reply on the TAD document itself. Flagged rather than silently treated as a formal approval;
   not a gap this document can close, since editing the TAD is `architect-agent`'s.
4. **No live, signed-in verification of any of the six Revision 7 pieces.** Everything in §11 below is V1–V3
   plus one V4-equivalent check against a static harness in real Chromium — never the actual Power Apps Code
   App host. The eight §8.5 accessibility properties and the `<dt>`/`<dd>` term-definition pairing were
   re-read against this revision's changes and none of the underlying markup moved (only CSS values and one
   new heading/nav were added), but a human opening the live app is still the only V4 evidence for any of it.

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

**This revision (round-statistics second version, 2026-08-27) needs no `build.yml`/`pipeline.yml` change
either.** No new artifact type, no new flow (the count stays 5, one flow's content changed), no new
platform-imposed limit the packer does not already enforce (the new `$expand` parameter is scanned by the
same `field-length-limits` and `flow-definition-language` gates every other action already passes through).
Re-run this revision: `python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml`
→ **PASS, 60 steps, 45 gates** (the two-step difference from the FR-035 revision's own 58/44 is a concurrent
session's own addition, not this revision's — grepped, neither new step names `roundstatistic` or
`$expand`).

**Revision 1.2 (2026-08-29) changes one thing in `build.yml`: the `code-app-data-sources` step's `--allow`
line is removed**, per that step's own comment's clearing action — the exemption it named is no longer true.
No step added or removed, no artifact type changed. Re-run this revision: `python3 scripts/verify-build-
config.py config/revitalise-grant-automation-build.yml` → **PASS — 67 steps, 52 gates** (the difference from
the Revision 1.1 figure above is concurrent sessions' own additions across this same feature's build config,
not this revision's — this revision's own edit is a 12-line comment addition and one flag removal on one
already-existing step, confirmed by `git show 2d34e9a -- config/revitalise-grant-automation-build.yml`).
`python3 scripts/verify-code-app-data-sources.py src/code-apps/trustee-review-portal` → **OK — 7
registration(s), 7 Dataverse source(s) declared, 0 exemptions** (was 6/7 with one declared allowance).

**This dispatch's own commit: `2d34e9a`** — `src/code-apps/trustee-review-portal/**` in full (the design-
system conversion and every revision built on it, none of it previously in `git log`), this document, the
one `build.yml` hunk above, and `logs/improvement-log.jsonl`/`logs/known-failure-modes.md`. This is the
citation `IMP-0486`'s own `proposed_change` asks a "shipped"/"implemented in full" claim to carry.

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
- **Revision 0.5 (2026-08-27) re-run:** `npm run typecheck` / `npm run lint` / `npm test -- --coverage` —
  **460/460 tests across 24 files, 98.37% statement/line coverage** (92.91% branches, 94.27% functions),
  up from the prior 372/372, 21 files, 96.27% — the delta is this revision's own five new/extended test
  files (`odata.test.ts`, `schema.test.ts`, `CasePanels.test.tsx`, `repository.test.ts`, `format.test.ts`)
  plus the other concurrent work already on this tree (App/DistributionChart/RoundStatisticsCharts/
  roundStatistics/landing/LandingPage suites this revision did not touch). `python3
  scripts/verify-code-app-column-bindings.py` re-run, unchanged result (the three newly-bound columns are
  all `IsSecured=0`). See §0.5 for the stale-`node_modules/.vite`-cache diagnosis this re-run surfaced and
  resolved (`IMP-0365`), unrelated to this revision's own code.
- **When the flow is live:** test-agent's V4/V5 work is exactly TAD §12.2's rows — reconcile the gender
  distribution as a real trustee once the applicant-side metrics are built (this version has none secured
  enough to need that check yet, since it emits no distributions at all). Additionally now needed:
  `pa app add flow`/`pa app add data-source --table rev_roundfinance`, then delete
  `roundStatistics.ts`'s/`roundFinanceReadService.ts`'s stand-ins (A-LAND-1, A-LAND-2) and reconcile the two
  inferred shapes (A-LAND-3, A-LAND-4) against a real response.

### This revision — TAD Revision 7 (2026-08-30)

- **`npm run typecheck` / `npm run lint` / `npm test -- --run` / `npm run coverage`** — **689/689 tests across
  38 files**, up from 685/685 (four new tests, one test file's assertions rewritten to generalise rather than
  add a count). Coverage **98.52% statements/lines** (93.49% branches, 94.49% functions) against the 80%
  floor. `npx vite build` clean.
- **The one thing test-agent cannot re-derive from source alone: the container-query V4 check.** TAD §12.2's
  row asks for "a tile holding a long currency value at a narrow column count versus a wide one" — inspect a
  live app. This dispatch's own evidence (§11) used a **static HTML harness loading the actual built
  `ds-tokens.css`/`ds.module.css`**, not the live Code App, because no live credential was available. If
  test-agent has host access, re-running that exact comparison (a tile at ~900px width vs. ~260px) inside the
  real Power Apps Code App is the one step that actually closes `A-R54`; this dispatch's own check is real
  Chromium but not this host.
- **Regression risk to watch for specifically:** any future change to `.statTileValue`'s `font-size` or
  `line-height` should be checked against BOTH `ds-tokens.test.ts` describe blocks that guard this class
  (the container-query shape, and the `IMP-0509` line-height-vs-font-size invariant) — they are independent
  and a change satisfying one can still break the other.

## 10. Unvalidated Assumptions Register (C-TECH-052)

| ID | Claim | Where in source | Evidence | Why not verified | Cheapest verification | Status |
|---|---|---|---|---|---|---|
| A-FLOW-01 | A Power Apps trigger (`kind: "PowerApp"`) and a `Response`/`kind: "PowerApp"` action, hand-authored in `REVPortalRoundStatistics-…json`, are well-formed and will be accepted by the Power Automate designer without a save error | [`src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json), `properties.definition.description` — marked `A-FLOW-01` | E3 (general knowledge of a stable, long-unchanged platform shape; this solution's other 4 flows have no example to copy) | This solution's other flows are all Dataverse-row-triggered or scheduled; Microsoft's public docs describe the CLI surface around this mechanism but not the raw JSON | `pac solution pack`/`pac solution check` both already passed clean (V1→V2, this session). Next: a human opens the flow in the Power Automate designer after import and saves it | OPEN |
| A-FLOW-02 | `prvReadWorkflow` at `Global` level is sufficient (and not excessive) for a trustee to invoke this specific flow | `Roles/REV Trustee/REV Trustee.xml`, comment beside the grant — marked `A-FLOW-02` | E3 (Microsoft's own note says only "the App Opener security role or an equivalent role") | No live invocation as a real trustee has been attempted | Grant `prvReadWorkflow` and nothing else, invoke as a real trustee once the flow is live; narrow the level if a lower one still works | OPEN |
| A-FLOW-03 | `Secure Outputs` (`runtimeConfiguration.secureData.properties: ["outputs"]`) actually hides row data from run history the way the designer's "Secure Outputs" checkbox does, for a hand-authored flow (never opened in the designer) | [`src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json), `properties.definition.description` — marked `A-FLOW-03` (shares the top-level marker with A-FLOW-01/04; the specific action is `List_applications_in_round`) | E3 (stable, documented Logic-Apps-family property; not confirmed for THIS hand-authored file specifically) | No live run has occurred yet | Once live, run the flow once and read its own run history as an owner: confirm row data is absent, response body present (TAD §12.2's own row for the same question) | OPEN |
| A-FLOW-04 | The service connection reference (`rev_SharedDataverse`) this flow reuses will bind correctly to a Power-Apps-triggered flow the same way it already binds to the four Dataverse-row-triggered/scheduled flows | [`src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json), `properties.definition.description` — marked `A-FLOW-04` (shares the top-level marker with A-FLOW-01/03; the specific field is `properties.connectionReferences`) | E2 (the mechanism is the same connection reference object; the trigger type is new) | No live import/activation yet | Confirm at the same designer-save step as A-FLOW-01 | OPEN |
| A-FLOW-05 | **Corrected, revision 0.3 (2026-08-26), per test-agent's D-10 finding that the original wording was one-sided.** Two claims, not one: (a) a `Response`/`kind: "PowerApp"` action (`Respond_error`), reached via a `runAfter: ["Failed","TimedOut"]` chain off `Alert_on_failure`, will actually execute and return a body to the calling code app on a genuine failure — no flow in this solution had previously exercised a `Response` action reached via a failure path under this specific trigger kind (`REVOpsFailureAlert`'s own always-respond action is `kind: "Http"`, not `kind: "PowerApp"`); (b) it does **not** execute on a successful run — **closed statically, this revision**: `Skipped` was removed from the `runAfter` condition list (D-10's fix), so `Respond_error` cannot fire when `Alert_on_failure` is skipped by design, which is exactly the successful-run case. Only claim (a) remains open | [`src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json), `properties.definition.description` and `Respond_error`'s own `description` — both marked `A-FLOW-05` | Claim (a): E2 (the `Response` action's own shape is E3-precedented via A-FLOW-01; what is new here is reaching it from a `runAfter:["Failed",…]` chain specifically). Claim (b): E4 — proven by direct inspection of the corrected `runAfter` list, deterministic from the platform's own documented `Skipped`-status semantics, no live run needed | Claim (a): this solution's other 4 flows have no Power-Apps-triggered failure path to copy; none is imported/live | Claim (a) only: once live, force a failure of `List_the_open_round` (e.g. a temporary bad `$filter`), invoke as the code app, and confirm a `status:"error"` body is received rather than a bare platform failure. Claim (b) needs nothing further — see the Evidence cell above | OPEN — claim (a) only; see the Claim cell for the other half |
| ~~A-LAND-1~~ | ~~A hand-written stand-in (`roundFinanceReadService.ts`) — calling `getClient(dataSourcesInfo).retrieveMultipleRecordsAsync("rev_roundfinances", …)` on the `"Dataverse"`-type path — behaves the same way the real generated `Rev_roundfinancesService` will once `pa app add data-source --table rev_roundfinance` is run; no such service exists yet to compare against~~ **CLOSED (E1), 2026-08-26** — `pa app add data-source --connector dataverse --table rev_roundfinance -u https://orge2b20d13.crm17.dynamics.com -c f31ddadfbe874e50a34054df668e75cf` was run (`IMP-0329`'s gate found the gap first); the generated `Rev_roundfinancesService.getAll`/`.get` are the identical calls the stand-in already made, confirmed by direct comparison, not inference. `READ_SERVICES` still points at the stand-in on purpose (§0.2) — closing the assumption did not require swapping it. | [`src/code-apps/trustee-review-portal/src/dataverse/roundFinanceReadService.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/roundFinanceReadService.ts):4, referenced from [`client.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts):199 | E1 (platform-generated file compared directly against the stand-in) | — | Optional cleanup, not required for correctness: swap the `READ_SERVICES` entry in `client.ts` for `Rev_roundfinancesService` and delete `roundFinanceReadService.ts` | **CLOSED** |
| ~~A-LAND-2~~ | ~~A hand-written stand-in (`fetchRoundStatistics`'s default) calls the eventual generated flow service correctly — a static no-argument `Run()` returning an `IOperationResult`-shaped result, with the §3.3 JSON arriving as the single string property of the payload~~ **CLOSED (E1/E2 mixed), 2026-08-26, by pipeline-agent** — `pa app list-flows` found the flow live in DEV (`1242b7f9-14fc-4246-7c97-7a851e362dd2`, status Active); `pa app add flow --flow-id 1242b7f9-14fc-4246-7c97-7a851e362dd2` was run and `src/generated/services/REV_Portal_RoundStatisticsService.ts` now exists. Both original guesses settled: the zero-argument `Run()` guess was **wrong** (real signature takes one argument, `Run(input: ManualTriggerInput)`, corrected in code) and the `IOperationResult`/`{success,data}` envelope guess was **confirmed** direct from the SDK's own `.d.ts` (E1). `fetchRoundStatistics`'s default now calls the real generated service (`roundStatistics.ts`:160, wired at `roundStatistics.ts`:448) instead of `missingFlowService`. One new, narrower question replaces the old one — the generated type says `Run()` resolves `void` (a 202/no-body contract) while the flow's own Response actions return real 200-with-body JSON — logged as `IMP-0356`, not asserted either way in code. **Not claimed: V4.** No live invocation was attempted or observed from this session — the flow's `shared_logicflows` connection is resolved per signed-in user by the host at app-run time (A-R34/`IMP-0188`'s already-documented mechanism), so there is no connection for this shell to call through. `pac code push` also surfaced and this session fixed a separate live defect (`pa app add flow`'s `workflowDetails` field rejected by `pac code push`, `IMP-0355`) — see `power.config.json`'s current committed shape. | [`src/code-apps/trustee-review-portal/src/dataverse/roundStatistics.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/roundStatistics.ts):36 (file header, rewritten this session), `:160` (`roundStatisticsFlowService`), `:448` (the default) | E1 for the envelope shape (SDK `.d.ts`, direct read); E2 for the response-body question (`IMP-0356`, unconfirmed either way) | — | Once the flow's connection is established as a real trustee (V4): call the app, and confirm the landing screen either renders figures or a clean "unavailable" diagnostic, never a raw platform error | **CLOSED** |
| A-LAND-3 | FR-062's three headline proportions (high-hours care, low life satisfaction, unable to take a break) are each shaped `{ population, count, percentage }` once populated | [`src/code-apps/trustee-review-portal/src/dataverse/types.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/types.ts):305 | E3 (TAD §3.3 shows all three only as `null`; the populated shape is inferred to match every other auditable figure on the screen — numerator, denominator, percentage — not read from any example) | TAD §3.3 never shows one populated; OQ-039 (the three thresholds) is still open, owner Emily | Once OQ-039 supplies the thresholds and the flow emits one populated proportion, compare its actual shape against this inferred one | OPEN |
| A-LAND-4 | FR-060's break-type profile total row mirrors a data row (per break-type value) minus the category field, with every field optional and rendered only when present | [`src/code-apps/trustee-review-portal/src/dataverse/roundStatistics.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/roundStatistics.ts):287 and [`types.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/types.ts):274 | E3 (TAD §3.3 shows `"total": {}`, an empty object naming no field at all) | TAD §3.3 never shows a populated total row | Once the flow emits a real `breakTypeProfile`, compare its actual `total` shape against this inferred one | OPEN |
| A-FIN-03 | The classid `{C3EBB6DA-CE32-4df0-8534-30B624E393CF}` is the correct "Decimal Number" field control for `rev_roundfinance`'s five `Decimal` attributes (`rev_amountcommitted`, `rev_grantgivingcapacity`, `rev_suggestedmaximumspend`, `rev_monthlydisbursement`, `rev_remaininglegacyfund`) on its new main form | [`Entities/rev_roundfinance/FormXml/main/{94936d70-da48-49e0-8778-ede28317a6f5}.xml`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_roundfinance/FormXml/main/%7B94936d70-da48-49e0-8778-ede28317a6f5%7D.xml) — marked `A-FIN-03` in the file's own header comment, at every one of the five `<control classid="{C3EBB6DA-...}">` occurrences | E3 (a documented, stable classic Dataverse control id; not confirmed against THIS solution's own already-shipped forms — grepped, and no Decimal-typed attribute anywhere in this solution's committed FormXml has a form yet: `rev_payment.rev_amount` is this solution's only other Decimal column and it is schema-only) | Ground-truthing it the way `AppModuleSiteMap.xml`/`AppModule.xml` were ground-truthed (build the real component in DEV, export, unpack) needs a human in the maker portal's form designer — an agent session has no browser and cannot drag a field onto a form to observe what classid the designer assigns | Once imported to DEV, a human opens this form once (the same V4 "open and save" step every new form needs anyway per `C-TECH-053`) and confirms all five Decimal fields render as numeric editors, not blank/text controls; if wrong, `pac solution export` + `pac solution unpack` after the correction will show the real id, the same procedure already used twice in this solution (`AppModuleSiteMap.xml`, `AppModule.xml` headers) | OPEN |
| A-TR-13 | `rev_careprovidedtype` (a `multiselectpicklist`) arrives over OData through this app's connector as EITHER a comma-separated string of option values (Dataverse's documented Web API convention) OR an array of numbers — the exact wire shape has not been observed live through THIS app's connector, the same unverified-connector-shape class as `A-TR-7` | [`src/code-apps/trustee-review-portal/src/dataverse/odata.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/odata.ts):53, `asNumberArray()` — marked `A-TR-13` | E3 (documented platform convention for the string form; the array form is a defensive alternative, not independently evidenced) | No live Code App push/read has been performed for this revision (V2 only — see §11) | Once live, read `rev_careprovidedtype` for one populated application row through the app and log the raw value's `typeof`; if it is neither shape, `asNumberArray()` returns `null` (fails safe to "not recorded", never a wrong value) | OPEN |
| A-FLOW-06 | The Dataverse `List rows` connector's `OpenApiConnection` action accepts a literal `"$expand"` key in `parameters`, the same way it already accepts `"$select"`/`"$filter"`/`"$top"` in this exact action (`List_applications_in_round`), with the value `rev_applicantid($select=rev_gender,rev_agerange,rev_applicanttype)` | [`Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json), `List_applications_in_round.description` — marked `A-FLOW-06` | E1 on the raw Web API contract (both the navigation-property name and the exact nested-object shape confirmed live against DEV this session — see §11); E2 on the DESIGNER's abstraction of `$expand` (Microsoft's own docs describe the simplified entry syntax for a different action, `Get a row by ID`, and a different navigation property — not this connector parameter's literal JSON key for `List rows`) | No flow in this solution has used `$expand` before, and no live import/designer-save of this specific parameter has occurred | Same ladder as A-FLOW-01: (1) import (V1→V2, done — clean pack + 0/0/0/0/0 Solution Checker), (2) open in the designer and save without a validation error, (3) a real invocation reconciling `genderDistribution` against an admin-side tally — this also closes A-R33's own V5 check in the same pass | OPEN |
| A-DS-1 | The `muted` and `quiet` state treatments are distinguishable **to a sighted trustee on a real screen**, not merely structurally distinct. TAD §8.5 point 1 requires two *visually* distinct treatments so that "withheld by column security" and "released but nothing recorded" do not collapse into one box — a disclosure-honesty control over Article 9 data, not a cosmetic. What is proven is two classes with two different declared backgrounds; the two fills differ by only **1.07:1** (`--surface-muted` `#f8f7f7` against `--surface-card` `#ffffff`), which is a deliberately quiet distinction and may prove too quiet | [`src/code-apps/trustee-review-portal/src/styles/ds.module.css`](../../src/code-apps/trustee-review-portal/src/styles/ds.module.css) — marked `A-DS-1` in the `.noticeQuiet` rule's own header comment | E4 for the structural claim (asserted by `ds-tokens.test.ts` and by `CasePanels.test.tsx`'s tone tests, both falsified by mutation). **No evidence at all for the visual claim** — jsdom computes no CSS, so no test in this app can see a rendered pixel | The app has never been rendered in a browser at all (A-R39): ADR-026's brand theme is still at V2 and this is a second visual layer on top of it | One signed-in trustee, in a private/incognito window, opening one detail screen that shows both states at once and saying whether they read as two different things. If they do not, the fix is that one CSS rule and nothing else — the state machine, the sentences and the roles all stay exactly as they are | OPEN |

Two rows the TAD itself carried as OPEN are now CLOSED by this session's live work, not repeated here as
open: `rev_roundfinance`'s `EntitySetName`/`PrimaryIdAttribute` (TAD §12.2), and A-FIN-02 (the `decimal`
attribute branch in `ensure-schema-helpers.psm1`, previously never run against a live environment) — see
`IMP-0316`.

**Revision 0.8 adds exactly one row, and deliberately no more.** The design-system adoption hand-authors no
platform artefact — no solution XML, no flow JSON, no manifest, no API payload — so the class of guess
`C-TECH-052` exists to catch does not arise here. Every contrast figure in this pass is arithmetic over
values that are on disk, which is E4 and not an assumption. The one thing that is genuinely unproven is
whether the rendered result looks the way the arithmetic says it does, and A-DS-1 is the narrowest true
statement of that.

### Revision 0.9 — four rows this revision closes because their subject no longer exists, and three rows added

**These four are closed, not deferred, and the distinction is the whole point: the mechanism each was an
assumption *about* has been deleted from the design.** Recorded with the reason rather than struck out, on
the precedent the TAD applies to ADR-025/ADR-026/ADR-030. `verify-assumption-markers.py` reads the **last**
table row naming an id, so this table is what sets their current status:

| ID | What it claimed | Why it is closed | Status |
|---|---|---|---|
| A-FLOW-01 | A hand-authored `kind: "PowerApp"` trigger and a `Response`/`kind: "PowerApp"` action are well-formed and will be accepted by the Power Automate designer | Neither exists in the flow any more. The trigger is `OpenApiConnectionWebhook` **copied from a shape proven live** on `REVScoringCalculateAndFlag`, and all five `Response` actions are gone. What replaces the question is not an assumption but a **verification** no document can close: the observed-effect assertion at TAD §12.3 step 7 | **SUPERSEDED** by ADR-038 |
| A-FLOW-02 | `prvReadWorkflow` at Global is sufficient, and not excessive, for a trustee to invoke this flow | Nothing invokes a flow. The grant is withdrawn from `REV Trustee` (§0.9.3), so the question has no subject. TAD §12.2 closes its matching row for the same reason — *closed as moot*, never carried as a guess | **SUPERSEDED** by ADR-038 |
| A-FLOW-04 | The `rev_SharedDataverse` connection reference will bind to a **Power-Apps-triggered** flow the way it already binds to the four row-triggered ones | The flow is now row-triggered, which is exactly the case the four existing flows already prove. The novel half is the half that disappeared | **SUPERSEDED** by ADR-038 |
| A-FLOW-05 | A `Response`/`kind: "PowerApp"` action reached via a `runAfter: ["Failed","TimedOut"]` chain executes and returns a body on a genuine failure | There is no `Response` action and no caller waiting on one. The failure path now writes `rev_status`/`rev_resultjson` to the result row through the **same** `UpdateRecord` shape as the success path, so it is no longer a second, separately-unproven contract. A real robustness gain, not a deferral | **SUPERSEDED** by ADR-038 |

**A-FLOW-03 is NOT closed, and A-FLOW-06 is not either.** A-FLOW-03 (`Secure Outputs` storage semantics and
run-history retention) is untouched and still OPEN: the flow still reads applicant rows, still sets
`runtimeConfiguration.secureData` on the row-reading actions, and the platform's actual semantics are still
unverified — TAD A-R35 carries it and ADR-038 changes nothing about it. A-FLOW-06 (`$expand` as a literal
`List rows` parameter key) is likewise unaffected: the read it qualifies is unchanged. Both keep their
markers in the flow file, which is why `verify-assumption-markers.py` reports no orphan for either.

**Rows added by Revision 0.9:**

| ID | Claim | Where in source | Evidence | Why not verified | Cheapest verification | Status |
|---|---|---|---|---|---|---|
| A-RESULT-1 | `rev_roundstatisticsresult`'s `EntitySetName` is `rev_roundstatisticsresults` | [`Entities/rev_roundstatisticsresult/Entity.xml`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_roundstatisticsresult/Entity.xml#L129) — marked `A-RESULT-1` at the element | E3 — pluralised by the same convention the sibling table's set name was **matched to after the platform echoed it**, which is precedent rather than proof for this table. TAD §12.2 states plainly that the value is platform-assigned and must not be hand-authored | The table does not exist in DEV — confirmed live 2026-08-28 — so there is nothing to read the name back from yet | `EntityDefinitions(LogicalName='rev_roundstatisticsresult')?$select=EntitySetName,PrimaryIdAttribute` at the first prerequisite run, then `pa app add data-source --table rev_roundstatisticsresult`, which echoes the platform's own name (TAD §12.3 step 9) | OPEN |
| A-FLOW-07 | The same two names as seen from the **flow** side: the entity set `rev_roundstatisticsresults` in five `Update a row` actions and one `List rows`, and the primary id `rev_roundstatisticsresultid` in the `recordId` expression | [`Workflows/REVPortalRoundStatistics-…json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L214) — marked `A-FLOW-07` in `Compose_result_row_id`'s own `description`, which is the only comment surface a flow JSON has | **E1 on the pattern**, from a platform-generated file on this tenant: [`.power/schemas/dataverse/roundstatisticsrequests.Schema.json`](../../src/code-apps/trustee-review-portal/.power/schemas/dataverse/roundstatisticsrequests.Schema.json#L10) carries `"x-ms-dataverse-primary-id": "rev_roundstatisticsrequestid"` for the sibling table. E3 for **this** table | Same reason as A-RESULT-1 — the table does not exist live, so nothing has echoed its names back | Closes by **reading**, not running: the §12.3 step 3 post-run sweep and step 9's `pa app add data-source` both echo the platform's real names before step 5's import. If either differs, six string literals change and nothing else | OPEN |
| A-RES-1 | The app's own copy of the same two names — `ENTITY_SETS.roundStatisticsResult` and `PRIMARY_KEYS.roundStatisticsResult` — plus the interim hand-written stand-in read service registered against them | [`src/dataverse/schema.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/schema.ts#L72) (marked at both `ENTITY_SETS` and `PRIMARY_KEYS`) and [`roundStatisticsResultReadService.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/roundStatisticsResultReadService.ts#L60) | E3, same basis as A-RESULT-1. The guessed string is written **once** and referenced from `ENTITY_SETS` rather than re-spelt, so there is one place to correct | Same — nothing has echoed the names back because the table does not exist | Same query, and step 9 additionally **replaces** the stand-in with the CLI-generated typed service, at which point the names come from the platform rather than from this file | **CLOSED (E1)** |

**Three rows for one fact, deliberately.** `A-RESULT-1`, `A-FLOW-07` and `A-RES-1` are the same
platform-assigned pair of names hand-authored in three independent places — the `Entity.xml`, the flow JSON
and the Code App's `schema.ts` — and `C-TECH-052` wants a marker **at the point of the guess**, not one
marker for a fact guessed three times. They also close at different moments: the `Entity.xml`'s copy is
echoed back by the first `ensure-schema.ps1` run, the app's by `pa app add data-source`, and the flow's by
**neither** — it closes only when someone compares it against what those two echoed, which is why it is the
one of the three that needs saying out loud. Collapsing them into one row would leave two markers orphaned
and the flow's copy checked by nothing.

**No assumption row is added for `subscriptionRequest/message: 3`, and that is the point.** It is not a guess:
it was measured live from the `callbackregistration.message` option set and corroborated in both directions
on this tenant (§0.9.1). It belongs in §11 as E1 evidence and in the improvement log as a correction to the
approved TAD — not here. Writing it as an assumption would be recording a fact as a doubt, which makes the
register less useful, not more.

### Revision 1.0 — three rows added for the four statistics metrics (`wbs:6.9`, 2026-08-28)

**Rows added by Revision 1.0:**

| ID | Claim | Where in source | Evidence | Why not verified | Cheapest verification | Status |
|---|---|---|---|---|---|---|
| A-FLOW-08 | The four money-average measures are composed as literal `null` **because the workflow definition language cannot express a sum over a variable-length array** — not because they were skipped. The claim being registered is the *negative* platform fact: that `add, div, max, min, mod, mul, pow, rand, range, sub` is the complete math-function set, that `add` is strictly binary, and that no other WDL construct (no `sum`, no aggregate on `Filter array`, no `$apply` through the Dataverse connector's `ListRecords`, no `aggregate` in its `fetchXml`) yields a total over a filtered subset | [`Workflows/REVPortalRoundStatistics-…json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json) — marked `A-FLOW-08` in the `description` of `Compose_exceptional_funding_summary`, `Compose_breaktype_rows` and `Compose_breaktype_total`, i.e. at each of the three actions carrying a null | **E2.** The function list is E1 — read this session from Microsoft's own *Reference guide to functions in expressions for workflows in Azure Logic Apps and Power Automate*, math-functions table. What keeps it off E1 overall is the exhaustiveness half: "no OTHER construct achieves it" is a negative over a surface nobody can enumerate completely, and the `$apply` half rests on TAD §5.1's earlier ground-truthing of the `fetchXml` parameter, which is adjacent evidence rather than the same measurement | Proving a negative needs the alternatives tried, and two of the three candidates are themselves unverified on this tenant. Attempting them to disprove the claim would mean shipping one — which is the architecture decision this row exists to route, not to pre-empt | **Do not verify this row — resolve it.** It closes when `architect-agent` picks a mechanism (TAD §0.8.1 costs the three candidates: `Apply to each` accumulation, `xpath(xml(...),'sum(...)')`, or reopening ADR-030's Custom API rejection). If the answer is that FR-059/FR-060's money measures are withdrawn instead, the row closes as moot. A cheap partial check meanwhile: search the WDL function reference for `sum` and confirm the only hit is XPath's `sum()` inside `xpath()` · **RESOLVED 2026-08-28 by `architect-agent` (TAD Revision 6, ADR-039, TAD §5.1.2).** The mechanism is a guarded `xpath(xml(concat(…join(…)…)),'sum(/r/v)')`: a presence `Filter array` first so no empty element can enter the XML, the XML built explicitly with `join()` rather than by `xml(json(…))`, and `if(empty(…), null, div(…))` so the empty-node-set `0` never reaches the document. `Apply to each` was rejected on documented constants (unparallelisable accumulator; ~950 actions; ~42 computations/24h against the 40,000 request limit; ~4× over the 12 s poll bound). ADR-030's Custom API rejection was re-examined and **re-affirmed unchanged**. **The registered negative claim itself is NOT falsified** — there is still no `sum()` over a variable-length array in the WDL, and `add` is still binary; `xpath` reaches XPath's `sum()`, which is a different language reached through a string. **Two things replace this row rather than closing with it:** `A-FLOW-11` (whether `xml()`/`xpath()` behave as documented on this tenant — `development-agent` adds that register row **in the same change that writes the marker into source**, per `IMP-0366`, never ahead of it) and `OQ-043` (a disclosure decision for the reviewer, TAD §6.3.5) — **`OQ-043` is itself now ANSWERED: `k = 5`, reviewer, 2026-08-28, TAD §0.9.1**, so a money measure is emitted only where its own population is ≥ 5. **A-FLOW-11 is therefore the ONLY thing still standing between these four figures and a screen**, and it is closable by one live run | **RESOLVED 2026-08-28 — TAD ADR-039, APPROVED** |
| A-FLOW-09 | `applicationsPerDay`'s denominator convention — **whole elapsed days since `rev_roundopenedon`, floored at 1, with the opening day counting as day 1** — is what FR-058's *"the average applications received per day"* means | [`Workflows/REVPortalRoundStatistics-…json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json) — marked `A-FLOW-09` in `Compose_applications_per_day`'s `description` | **E3.** SDD FR-058 (line 1123) says only *"the average applications received per day"* and names no convention; TAD §3.5 fixes the numerator's start date as an entered calendar fact but is silent on how the denominator counts. Three readings are defensible (elapsed days, inclusive calendar days, or days the round has been *open* excluding a closed date) and they differ by one day's worth — material on a short round, negligible on a long one | Nobody has been asked. It is a charity-reporting convention, not a platform contract, so no amount of measurement settles it | One sentence from the reviewer or Emily. Until then the figure is directionally right and cannot be off by more than one day's worth of applications. If the answer is inclusive calendar days, the fix is `add(...,1)` in one expression · **REVIEWED AND DELIBERATELY LEFT OPEN, 2026-08-28, `architect-agent` (TAD Revision 6).** This row was examined in the same dispatch that resolved A-FLOW-08 and is **not** an architecture decision: it is a charity-reporting definition, and this row's own *"nobody has been asked"* is the whole of it. Closing it by picking the most defensible of three readings would be the *"platform contract assumed rather than ground-truthed"* failure transposed onto a business definition, which is the one thing that dispatch existed to avoid. It was put to the reviewer alongside `OQ-043`, hoping to be answered in the same pass. **`OQ-043` came back answered (`k = 5`) on 2026-08-28 and this did not** — so it needs a question of its own and no longer rides on anything. **Do not read the Revision 6 approval as covering it.** If the answer changes what FR-058 means, `plan-agent` records it in the SDD | OPEN — reviewer/Emily, asked once and unanswered; needs re-asking on its own |
| A-FLOW-10 | `ticks()` accepts `rev_roundopenedon`'s value as it arrives from the Dataverse connector — a `Date`-typed column with no time part — and `formatDateTime` renders it as `yyyy-MM-dd`; and the whole expression is safe when the column is empty | [`Workflows/REVPortalRoundStatistics-…json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json) — marked `A-FLOW-10` in `Compose_round_opened_on`'s `description` | **E3.** No flow in this solution has ever called `ticks()` — grepped, this is the first. `formatDateTime` is used elsewhere, but not on a `Date`-without-time column. The empty-column half is **E4 by construction**: the date is defaulted to the `computedOn` stamp before it reaches either date function, so neither can be handed a null regardless of whether this runtime evaluates both branches of a conditional — a question this repository has recorded contradictory findings on and which is itself still open | No run. `ticks()` on a malformed or empty input throws, and a throw here fails `Compute_statistics`, fires the failure alert and takes **every** figure off the landing screen — which is why the defaulting is there rather than a bare guard | First real run against a round whose `rev_roundopenedon` is populated: read `rev_resultjson` and confirm `applicationsPerDay.openedOn` is a `yyyy-MM-dd` string and `days` is a plausible positive integer. Then blank the date and confirm the metric degrades to `null` while every other figure still renders · **REVIEWED AND DELIBERATELY LEFT OPEN, 2026-08-28, `architect-agent` (TAD Revision 6).** Examined in the same dispatch as A-FLOW-08 and unchanged by ADR-039: this is a `V1 → V4` question that only a run can settle, not a design question, so there is nothing an architecture decision can add to it. Its own `verify_by` is correct as written and is **not** amended. Explicitly **not** pre-empted: the `concat(…,'T00:00:00Z')` fix this row's source notes describe stays unapplied, because stacking a second guess on the first is what would make `concat` on an already-full timestamp the new broken case. **It now shares a live run with `A-FLOW-11`** (TAD §12.2), so it costs no extra pass | OPEN — closable only by the first live run |

**Why A-FLOW-08 is a register row at all, when it is a fact rather than a doubt.** The §10 convention set two
subsections above says a measured fact belongs in §11, not here — `subscriptionRequest/message: 3` is the
precedent. A-FLOW-08 is deliberately treated the other way, and the distinction is the exhaustiveness half.
"These ten functions are the math set" is a fact and is cited as one. **"Therefore no mechanism exists"** is
an inference over a surface this session did not exhaust, and it is load-bearing: it is the entire
justification for three requirement-measures shipping as `null`. If it is wrong — if some construct does sum
an array — then FR-059 and FR-060 were under-delivered for a reason that was not true, and the register is
where a claim of that shape belongs. `IMP-0463` records the same point from the design side: TAD §5.1's
*"and equivalents"* generalised from a verified fact to an unverified one inside one sentence.

### Revision 1.1 — two rows added for the money-average mechanism, and A-FLOW-08 stays RESOLVED (`wbs:6.9`, 2026-08-28)

**Both rows land in the SAME change that writes their markers into source**, per TAD §5.1.2's closing
paragraph and `IMP-0366`: `verify-assumption-markers.py` resolves every OPEN row's *Where* target and
requires the id to appear in it, so a row added ahead of the expressions it describes fails the gate rather
than documenting anything.

| ID | Claim | Where in source | Evidence | Why not verified | Cheapest verification | Status |
|---|---|---|---|---|---|---|
| A-FLOW-11 | Three claims about the Logic Apps wrapper around XPath, none of which any flow in this solution has ever exercised: that **`xml()` accepts a ~5 KB hand-built string** and parses it as this construction assumes; that **`xpath(…, 'sum(/r/v)')` returns a value `float()` and `div()` accept** as a number rather than a node set or an unparseable string; and that both behave as documented over a node set of up to ~1000 elements. XPath 1.0's own `sum()` semantics are **not** part of this claim — they are a standard and were measured this dispatch against libxml2 (`<r></r>` → `0`; any empty element → `NaN`), which is why both dangerous cases are removed at source rather than assumed away | [`Workflows/REVPortalRoundStatistics-…json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json) — marked `A-FLOW-11` in the `description` of **all 21** `Compose_*_sum` actions, i.e. at every point the guess is made | **E2, and the halves are deliberately separated.** The *pattern* is E1-adjacent — first-party documented, function reference Example 7. The *arithmetic* is E2 — Microsoft names the engine as the .NET XPath library, so XPath 1.0 governs, and its two dangerous cases were measured. What is evidence for **nothing** is the wrapper: `grep` confirms no flow in this solution has ever called `xml()` or `xpath()`, and a conformant local engine is a model of the runtime, not the runtime — the same limitation the local evaluator that closed the count metrics carries | No import, no designer save, no run. The expressions are first read by the platform at TAD §12.3 step 6 | **Fail-loud, so the ladder is cheap.** (1) designer save without a validation error (V2, §12.3 step 6); (2) one live run against a round seeded so that **one break type has zero applications**, **one has every `rev_costs` blank**, and **one has a mix**, then read `rev_resultjson` and assert `null` for the first two and, for the third, a `value` reconciling to a **hand-computed** mean over those same rows with a `population` **lower** than the row's `count`; (3) the `NaN` case must be **provoked**, not waited for — a document containing `NaN` is unparseable, so the falsifiable check is that the app still renders every other figure. **A populated average alone proves nothing** (§12.2's own wording) | OPEN |
| A-FLOW-12 | FR-060's *"the average grant amount requested **(including exceptional funding)**"* means the mean of `rev_amountrequested` **+** `rev_additionalamountrequested` per row — not of `rev_amountrequested` alone — with presence being **either** column populated and an absent column summing as zero | [`Workflows/REVPortalRoundStatistics-…json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json) — marked `A-FLOW-12` in the `description` of the five `Filter_breaktype<n>_requested_present` actions, which are where the reading is expressed | **E3, and it is a reading of a requirement rather than a platform contract.** Three things point the same way and none is an instruction: SDD FR-060's own parenthesis; TAD §3.1's column table, which maps `rev_additionalamountrequested` to **FR-060** as well as FR-059; and the app's already-approved `totalFundingRequested` (`src/code-apps/trustee-review-portal/src/domain/format.ts`), which performs this identical sum for FR-035 — *"summed UNCONDITIONALLY … one populated and the other absent sums as if the absent one were zero."* Against them, ADR-039's cost paragraph says *"five break-type rows × two money columns"*, which reads as the base ask alone; that is a costing phrase, not a contract, and the count of thirteen sums holds either way | **Was** unasked at the time this row was written; **since answered.** One sentence from the reviewer or Emily. If the answer is the base ask alone, the fix is one expression per break type and nothing else changes — the presence filter, the population and the disclosure gate are all unaffected. Note the consequence of being wrong in this direction: including exceptional funding makes the figure **larger**, so it cannot under-report a grant ask on a board pack | **CLOSED — reviewer confirmed, 2026-08-28 21:22** ([`logs/routing.log:372`](../../logs/routing.log#L372) — Xander Lykopoulos: *"A-FLOW-12 confirmed (sum both funding columns, matching the built implementation, no rework needed)"*). The reading this row registered is exactly the one shipped; nothing in source changes |

**`A-FLOW-08` stays RESOLVED and its markers are GONE from source**, which is a deliberate pairing. Its last
status row above reads RESOLVED, so `verify-assumption-markers.py` requires no marker for it — and leaving
one behind would be a register entry pointing at a settled question, teaching the next reader that it is
still open. `RoundStatisticsContract.Tests.ps1` asserts the absence.

**No row is added for the `k = 5` threshold, and that is the point.** It is not a guess: it is a reviewer
decision recorded at TAD §0.9.1 and seeded as data. Writing it as an assumption would record a decision as a
doubt, which is the same mistake as recording a measured fact as one — the precedent §10 set for
`subscriptionRequest/message: 3`.

**No row is added for the XPath 1.0 semantics either.** They were measured against a conformant engine this
dispatch, which is evidence, and they belong in §11.

### Revision 1.2 — three rows closed on one live run (`wbs:6.9`, `IMP-0485`, 2026-08-29)

`pa app add data-source --connector dataverse --table rev_roundstatisticsresult -u
https://orge2b20d13.crm17.dynamics.com -c 8b4307acb81d4463be4fd96792363f2f --non-interactive` echoed the
platform's own `EntitySetName`/`PrimaryIdAttribute` for `rev_roundstatisticsresult` into
`.power/schemas/appschemas/dataSourcesInfo.ts`, agreeing exactly with the independent read-only
`EntityDefinitions(rev_roundstatisticsresult)` query `logs/pipeline.log` already recorded the same day. All
three rows guessing this one platform-assigned pair of names close together:

| ID | What it claimed | Why it is closed | Status |
|---|---|---|---|
| A-RESULT-1 | `rev_roundstatisticsresult`'s `EntitySetName` is `rev_roundstatisticsresults` | Confirmed E1 by the CLI's own echo into `dataSourcesInfo.ts`, agreeing with `pipeline.log`'s independent `EntityDefinitions` read | **CLOSED (E1)** |
| A-FLOW-07 | The entity set `rev_roundstatisticsresults` and primary id `rev_roundstatisticsresultid`, as seen from the flow side | Same evidence as A-RESULT-1 — the flow's own copy was never independently checkable except by comparison, and both platform-assigned names it hardcodes now agree with what the platform echoed | **CLOSED (E1)** |
| A-RES-1 | The app's own copy of the same two names (`ENTITY_SETS.roundStatisticsResult`, `PRIMARY_KEYS.roundStatisticsResult`), plus the interim stand-in registered against them | The guess was confirmed correct, not merely unfalsified: `dataSourcesInfo.ts`'s generated `"rev_roundstatisticsresults"` entry and `primaryKey: "rev_roundstatisticsresultid"` match `schema.ts`'s pre-existing values exactly. The stand-in is deleted in the same change ([`client.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts#L270) now points at the generated `Rev_roundstatisticsresultsService`) | **CLOSED (E1)** |

### Revision 1.3 — one row added: `A-FLOW-13` (`wbs:6.9`, `IMP-0349`, `IMP-0483`, `IMP-0496`, 2026-08-30)

**Row added:**

| ID | Claim | Where in source | Evidence | Why not verified | Cheapest verification | Status |
|---|---|---|---|---|---|---|
| A-FLOW-13 | `result()`, called with a `Switch` or `If` action's own name, resolves to the top-level actions of whichever case/branch actually executed — the same behaviour Microsoft documents for `Scope`/`For_each`/`Until` | [`Workflows/REVPortalRoundStatistics-…json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json) — marked `A-FLOW-13` in the `description` of both `Find_the_failed_step_inside_Switch_on_open_round_count` and `Find_the_failed_step_inside_Condition_page_cap` | **E2 at most, and honestly closer to none.** Four Microsoft Learn pages were read directly this dispatch (`result()`'s own function reference, the *"Get context and results for failures"* walkthrough, the Switch and Condition how-to guides, the control-workflow-action schema reference) and every worked example names only `Scope`/`For_each`/`Until`. Neither confirms nor denies a Switch or If by name — this is a genuine documentation gap, not a read that fell short (`IMP-0496`) | No import, no designer save, no run. Deploying to test it live was explicitly out of this dispatch's scope | **Bounded by construction, not merely declared.** Every call this row covers is gated behind a name check confirming the platform already reported this exact action as the one that ran and failed (the same technique that makes the shipped `Read_configuration` descent — a confirmed `Scope` — safe one flow over), so a wrong answer degrades to the pre-fix generic wrapper message rather than a new failure mode. Closes on: (1) designer save without a validation error (V2); (2) one live run that fails inside `Condition_page_cap` and the alert names the true leaf, not the Switch or the If | OPEN |

**Not a fourth row for the same fact.** Unlike `A-RESULT-1`/`A-FLOW-07`/`A-RES-1` above (one platform-assigned
pair of names, hand-authored in three files), this is ONE claim about the platform's own expression language,
made at two call sites inside one file — so one row, two markers, matching how `A-FLOW-11` already covers
all 21 `Compose_*_sum` actions with a single id.

### Revision 1.4 — the eleven rows Test Report v6 named against `C-TECH-058`, checked against live DEV rather than accepted (`wbs:6.9`, 2026-08-30)

**Test Report v6 (`T-C1`/`D-19`) is right that eleven rows sit `OPEN` while DEV has held schema for the
tables they touch since 2026-08-27/29 — but "schema exists" and "the row's own stated closing precondition is
met" are not the same claim, and treating them as the same claim is what this pass checked rather than assumed.**
Each of the eleven was re-verified against DEV this dispatch, live, not against the Test Report's own §7.1
table (per this dispatch's own instruction not to take that table as ground truth without checking):

- **`callbackregistration` for the round-statistics flow** (`b184204a-…`) re-queried via `pac env fetch`:
  `createdon` is still `2026-08-27 6:22 PM`, unchanged from every prior read in `logs/pipeline.log`. The
  designer save (TAD §12.3 step 6) genuinely has not happened. This is out of this dispatch's scope — the
  flow trigger and `C-TECH-053` for it are held for the Pipeline stage — so **`A-FLOW-03`, `A-FLOW-06`,
  `A-FLOW-11`, `A-FLOW-13` stay OPEN**, correctly, and are not touched here.
- **`rev_roundstatisticsresult`'s CURRENT row and `rev_roundstatisticsrequest`'s CURRENT row both carry a
  populated `rev_resultjson`** (queried live this dispatch) — but both are **seeded, not flow-produced**:
  `createdby` on both is `REV-MS-Provisioning` (the schema-provisioning service principal `seed-round-
  statistics-result.ps1` runs as — `logs/pipeline.log`'s own 2026-08-29 entry names this exact seeder), never
  a flow run identity, and the result row's `rev_computedon` (`2026-08-27T19:09:00Z`) **predates** the request
  row's own `rev_triggeredon` (`8/29/2026 1:08 PM`) by two days — the reverse of what a real trigger → compute
  sequence would produce. Both rows' own `highHoursCareProportion`/`lowLifeSatisfactionProportion`/
  `unableToTakeBreakProportion` are `null` in the seeded JSON too. Because each row's own closing precondition
  names *"a real"* / *"the flow emits"* a populated shape, seed data does not satisfy it — **`A-LAND-3` and
  `A-LAND-4` stay OPEN**, and the register's own wording ("never observed populated") is corrected here to
  "observed populated only in seed data, which is not the flow" rather than left to read as untested.
- **`A-TR-13`** (`rev_careprovidedtype`'s wire shape): a live `pac env fetch` across every `rev_application`
  row filtered on `rev_careprovidedtype not-null` returned **zero rows** — there is no populated value for
  this column in DEV at all, not merely an unread one. Test Report v6 §7.1 called this row "closeable NOW" on
  the strength of "data source live, no signed-in read yet"; that is imprecise; there is nothing to read yet
  either way. **Stays OPEN**, register corrected to say so.
- **`A-FIN-03`** (Decimal control classid on the `rev_roundfinance` form): the live `systemform` row (queried
  by `formid`) confirms the platform has stored and accepted `classid="{C3EBB6DA-CE32-4df0-8534-30B624E393CF}"`
  on all five Decimal controls exactly as authored — the import succeeded and the form is live. That is not
  the row's own closing precondition, though: it asks whether "all five Decimal fields render as numeric
  editors," which needs a human to open the form and look, and no such session is recorded anywhere in
  `logs/pipeline.log` or `logs/routing.log` since the form was pushed. **Stays OPEN** — environment-ready,
  human step genuinely not yet performed.
- **`A-DS-1`** (muted/quiet visual distinction, sighted-user judgement): no mechanism exists to verify this
  from this session (no browser, no visual perception) and no V4 sign-in session is recorded in either log.
  **Stays OPEN** — nothing to close it with yet.
- **`A-FLOW-09`** (applications-per-day denominator convention): re-asked of the reviewer at TAD Revision 6 and
  explicitly **not** answered — `logs/routing.log:364` records `architect-agent`'s own note that "`A-FLOW-09`
  and `A-FLOW-10` remain OPEN and unaffected." **Stays OPEN** — still needs its own question.
- **`A-FLOW-12`** (FR-060 reading, base ask vs. + exceptional funding): **CLOSED.** `logs/routing.log:372`
  records the reviewer's own answer the same day the row was raised — *"A-FLOW-12 confirmed (sum both funding
  columns, matching the built implementation, no rework needed)"* — which this pass had simply never carried
  back into the register table above. Closed there, cited to the log line, no rework.

**Net effect of this pass: one row closes (`A-FLOW-12`, on a reviewer decision already on record but not yet
reflected here); ten stay OPEN, two of them (`A-LAND-3`/`A-LAND-4`) with a corrected reason (seed data observed,
not flow output) and one (`A-TR-13`) with a corrected reason (no data exists to read, not merely unread).
`T-C1`/`D-19`'s premise — "DEV holding schema" — does not, by itself, make any of the remaining ten rows'
own stated closing precondition true; nine of the ten name either the out-of-scope flow trigger/designer-save
(`A-FLOW-03/06/11/13`, `A-LAND-3/4`), a still-unanswered reviewer question (`A-FLOW-09`), or a human V4 step
with no recorded session (`A-FIN-03`, `A-DS-1`) — and `A-TR-13` names data that does not exist yet either way.**

## 11. Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

### Verification level reached

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| `rev_roundfinance` table + 13 attributes + alternate key | **V4** | DEV (macOS, cert-based Web API) | `ensure-schema.ps1 -Env dev` exit 0; live GET confirms 13 attribute names, `EntityKeyIndexStatus=Active`, `EntitySetName=rev_roundfinances` |
| 3 redacted columns on `rev_application` | **V4** | DEV | Live GET confirms all three present; `pa app refresh data-source --name applications` regenerated the TS model with them (`grep redacted` on `Rev_applicationsModel.ts`) |
| Role privilege grants (3 roles) | **V4** | DEV | Live `roles(<id>)/roleprivileges_association` confirms each named privilege on each named role |
| Table auditing on `rev_roundfinance` | **V4** | DEV | Live GET `IsAuditEnabled=true` |
| `REV \| Portal \| Round Statistics` flow | **V2** | Local (SolutionPackager + hosted Solution Checker) | `pac solution pack --packagetype Unmanaged` exits 0, flow listed under "Processing Component: Workflows"; `pac solution check` (hosted, Europe) returns 0/0/0/0/0 across all severities |
| `pa app list-flows` / `pa app add flow` mechanism | **V3 (accepted by target, generated service exists, idempotent push), not V4 (a working flow for a signed-in trustee)** | DEV, live | 2026-08-26: `pa app list-flows` found `REV \| Portal \| Round Statistics` live (flow id `1242b7f9-14fc-4246-7c97-7a851e362dd2`, status Active); `pa app add flow --flow-id 1242b7f9-...` ran and generated `REV_Portal_RoundStatisticsService.ts`; `pac code push --solutionName RevitaliseGrantAutomation` succeeded (after removing the `workflowDetails` member `pa app add flow` wrote, which `pac code push` rejects — `IMP-0355`) and re-ran cleanly a second time (idempotency, `C-TECH-053`). No live invocation of the flow itself was attempted or observed (A-LAND-2's closure note, §10) |
| ADR-026 brand theme | **V2** | Local | `npm run typecheck`/`lint`/`test` pass; no live Code App push performed |
| FR-035 redacted-column UI (`CareSupportPanel`) | **V2** | Local | `npm run typecheck`/`lint`/`test` pass (246/246, 16 files); `scripts/verify-code-app-column-bindings.py` confirms only the 3 redacted columns are bound, not their secured sources; no live Code App push performed |
| **The flow's failure path** (`Compute_statistics` scope, `Alert_on_failure`, `Respond_error`) | **V2**, plus one property proven by static inspection alone (no level needed — see note) | Local (SolutionPackager + hosted Solution Checker, re-confirmed independently by development-agent; D-10 fix re-verified this revision, source inspection only, no packer re-run needed — §0.3) | `pac solution pack` (both package types) exits 0; `pac solution check` 0/0/0/0/0 (automation-agent's run); `verify-flow-definition-language.py` OK, 5 flow definitions clean, re-run again after the D-10 fix with the same result; every action `description` ≤256 chars, checked programmatically. No live import — A-FLOW-05's claim (a) (§10) is the untested half. **A-FLOW-05's claim (b)** — that `Respond_error` does NOT fire on a successful run — is settled by direct inspection of the corrected `runAfter` list, not by any verification level on the V1–V5 ladder: the platform's own documented `Skipped`-status semantics make the absence deterministic once the condition is removed, the same basis test-agent used to rate the original D-10 defect a certainty rather than a guess |
| **`LandingPage.tsx` + `RoundStatistics`/`RoundFinancePanel`/`DistributionChart`** | **V2** | Local | `npm run typecheck`/`lint`/`test -- --coverage` pass, 372/372 across 21 files, 96.27% stmt/line coverage (re-confirmed unchanged after §0.2's fix); `verify-code-app-column-bindings.py` OK with `rev_roundfinance`/`rev_setting` in scope. No live Code App push, no live flow binding — A-LAND-2 (§10, the flow) is the remaining untested half; A-LAND-1 (the table read) is now CLOSED, see the next row |
| `rev_roundfinance` Code App data source (`pa app add data-source`, §0.2) | **V3 (the binding), not V4 (a real signed-in user's read)** | DEV, live | Platform accepted the call and returned real metadata: `dataSourcesInfo.ts`'s new `"rev_roundfinances"` entry reports `primaryKey: "rev_roundfinanceid"`, matching `IMP-0316`'s live-confirmed value exactly; `scripts/verify-code-app-data-sources.py src/code-apps/trustee-review-portal` → OK, 5/5. Not V4: no real signed-in trustee has opened the app since — same residual `verify-code-app-data-sources.py`'s own docstring states (a declared source can still have a broken connection underneath) |
| **FR-035's remaining structured fields** (type of break render, structured care-support pair, applicant-type context, the OQ-031 total-funding-requested fix, §0.5) | **V2** | Local | `npm run typecheck`/`lint`/`test -- --coverage` pass, 460/460 across 24 files, 98.37% stmt/line coverage; `verify-code-app-column-bindings.py` OK, unchanged (all five newly-bound columns `IsSecured=0`); `schema.test.ts` re-derives both new option-set label maps from `OptionSets/rev_careprovidedtype.xml`/`rev_carehoursband.xml` directly, not transcribed by eye. No live Code App push performed — the multiselect wire shape (`A-TR-13`) and the applicant-type/exceptional-funding value rendering are both untested against a real signed-in trustee |
| **The flow's `$expand` navigation-property name and nested-object shape** (`A-FLOW-06`, §0.7) | **E1 (live Web API, both halves)** — narrower than a numbered V-level, because this is a metadata/shape fact, not a run of the flow itself | DEV, live (cert-based Web API, same identity/method IMP-0083 establishes) | `EntityDefinitions(LogicalName='rev_application')/ManyToOneRelationships?$filter=ReferencingAttribute eq 'rev_applicantid'` → `ReferencingEntityNavigationPropertyName: "rev_applicantid"`; `rev_applications?$select=rev_applicationid,...&$expand=rev_applicantid($select=rev_gender,rev_agerange,rev_applicanttype)&$top=2` → returns exactly the nested `rev_applicantid: {rev_gender, rev_agerange, rev_applicanttype, rev_applicantid}` shape this file's `$expand` parameter and every `item()?['rev_applicantid']?['rev_gender']`-style `where` clause assumes. **Not verified: the connector's own acceptance of the literal `"$expand"` key** (`A-FLOW-06` stays OPEN) |
| **The five new metrics' expression text** (46 `Query` actions + 8 `Compose` actions, `Compose_response_body` rebuilt) | **V2, plus a level beyond V2 this project has not previously used for a flow: the shipped expression TEXT was evaluated, not just its JSON shape** | Local (`pac solution pack` both package types exit 0; hosted Solution Checker 0/0/0/0/0, re-run this revision; `verify-flow-definition-language.py` OK, 5 definitions clean; `verify-field-length-limits.py` OK, 238 flow descriptions ≤256 chars) plus a purpose-built evaluator (not shipped) for the exact WDL function vocabulary these 54 actions use (`concat`/`string`/`length`/`body`/`outputs`/`if`/`equals`/`mul`/`div`/`float`/`max`/`item()?[...]`), run against a 271-row synthetic round (every category sums to population, minus three deliberately-injected nulls on gender, which summed correctly to population−3) and a genuinely empty round (every category resolves `count:0`/`percentage:0`, no error — proving the `max(population,1)` fix). This is evidence about the ARITHMETIC and JSON STRUCTURE only — it is not a Power Automate run, and does not touch A-FLOW-01/03/04/05/06's own open questions about the trigger/`Response`/`$expand` shapes | No live import, no designer save, no real invocation — same open half as A-FLOW-01/06 |
| **The design-system component and token layer** (ADR-033/034/037, §0.8) — 7 converted components, 2 new stylesheets, 11 restyled screens/components | **V2** — local typecheck, lint, tests, coverage and a clean production bundle. **Not V3, not V4, and the distinction matters more here than usual** | Local (macOS) | `npm run typecheck` exit 0; `npm run lint` exit 0; `npx vitest run` **637 passed / 637 across 37 files, 0 failures** (baseline before this revision: 496/25); `npm run coverage` **98.45% statements, 98.45% lines** against the 80/80 threshold, with `src/components/ds` at 100% on all four measures; `npm run build` exit 0. HARD gates re-run individually: `verify-code-app-column-bindings.py` OK over **99** authored files against 63 forbidden columns; `verify-code-app-data-sources.py` OK, 6 registrations / 6 declared; `generate-trustee-field-catalogue.py --check` OK, 11 entries across 2 groups unchanged; `verify-assumption-markers.py` PASS. **The print cascade was verified in the BUILT bundle rather than reasoned about**: in `dist/assets/index-*.css`, `@media print` is emitted at offset 13464, after `.noticeMuted` (1823), `.noticeQuiet` (2208), `.statTile` (2462) and `.errorBox` (8943) — so `[data-print="state"] { background: none }` still wins at equal specificity and a withheld state still prints as a bordered box. That was the sharpest risk in putting a filled component behind the print stylesheet. **What none of this proves:** jsdom computes no CSS and vitest processes no CSS import, so **no test result in this revision is evidence that any token resolves, that any contrast pairing renders as measured, or that any screen looks correct.** Every contrast figure here is arithmetic over declared values. A-R39 stands: two unverified visual layers now stack, and one V4 sign-in in a private window closes both at once |
| **The A-R38 mitigation itself** (that the guard can actually fail) | **V4 by mutation** — the gate was falsified, not assumed | Local | Eleven deliberate mutations, each reverted and re-confirmed green. Seven by the implementing session (reverting the primary to the design system's `#e6027f`; adding `color: var(--text-muted)`; deleting `sm`'s 44px; reintroducing `--warning`; weakening the input boundary to `--border-default`; setting `outline: none`; adding a remote font import) — each failed between 1 and 5 assertions. Four by development-agent on the assertions added in this dispatch: deleting `main.tsx`'s `ds-tokens.css` import → **3 failures**; deleting `harness.tsx`'s → **2**; a real ES import from `Designsystem/` inside `src/` → **1**; a CSS `@import` from it → **1**. The first of those four is the one that matters: without it, deleting the import would have left all 29 token assertions passing while the running app rendered every token as nothing — A-R38's own failure mode, invisible to A-R38's own mitigation |

#### Revision 0.9 — what was executed, and what each result does not prove

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| **§12.3 step 1 — the live-versus-source reconciliation** | **E1, live, read-only** — not a numbered V-level, because this is a fact about an environment's current state rather than a run of anything | REV-GrantApplications-DEV, live (macOS, `pac` auth profile — no cert, no keychain, no write) | `pac solution export --name RevitaliseGrantAutomation --overwrite` then `pac solution unpack --packagetype Unmanaged`, both exit 0; both action graphs flattened to a path-keyed map, designer-only keys stripped, and all three difference directions reported. Result: the ten-row table at §0.9.2. Also read live: `callbackregistration` (1 row for this flow, `message Modified`, `scope Organization`, `createdon 2026-08-27 18:22`), `stringmap` for `callbackregistration.message` (the 1–7 enumeration at §0.9.1), `entity` (`rev_roundstatisticsresult` ABSENT), `rev_setting` (`RoundStatisticsStaleAfterSeconds` ABSENT), `rev_roundstatisticsrequest` (row `CURRENT` present), and `roleprivileges` joined to `privilege` (both stale Global grants present, with their `roleprivilegeid`s). **What it does not prove:** nothing about whether the new definition works — it is a snapshot of what is there now |
| **`subscriptionRequest/message: 3`** | **E1, measured and corroborated in both directions** | DEV, live | `stringmap` filtered `attributename eq 'message'` returns 2 = **Deleted** and 3 = **Modified**; the scoring flow's `message: 1` has a live registration reading `Added`; this flow's live `message: 3` has one reading `Modified`. **What it does not prove:** that the authored trigger fires — that is the observed-effect assertion, and no metadata read substitutes for it (`C-TECH-064` clause (a)) |
| **The flow's new trigger, guard, freshness read and five write-backs** | **V2**, and one property beyond it — the shipped expression **text** was evaluated, not only its JSON shape | Local (macOS) | `pac solution pack` **both** package types exit 0 with the flow under "Processing Component: Workflows"; `pac solution check` on the packed managed zip, wrapped in an explicit client-side timeout, **0 findings across all five severities in 35 s, no hang**; `verify-flow-definition-language.py` OK over 5 definitions; `verify-field-length-limits.py` OK, 257 descriptions ≤256 chars; `no-hardcoded-thresholds` clean; a local validator confirming the JSON parses, every `runAfter` resolves to a sibling at the same nesting level, and **no `Response` action remains**; and a 13-case simulation of the three `staleAfterSeconds` expressions confirming every document parses with the field typed `number` or `null`. **What none of it proves:** that the trigger fires, that the write-backs write (a green run with an empty `rev_resultjson` is the signature of the nested-`item` form), or that any expression evaluates — `pack` and `import` accept a malformed expression silently, and the designer save at §12.3 step 6 is the first thing that reads them |
| **`flow-reads-no-trigger-body` — the new HARD gate** | **V4 by mutation, and by discrimination against the real prior state** | Local | `--selftest` **15/15**, covering all four A-checks, both B-cases, a reverted Power Apps trigger, a trigger-less definition, a missing file, an unparseable file, a definition with no `properties.definition`, an unparseable `Entity.xml` in the seed, and an absent `Entities/` tree — the last two because an incomplete seed would let check B pass vacuously. Two on-disk known-bad fixtures under `src/tests/fixtures/known-bad/flow-reads-no-trigger-body/` each exit 1. Five `It` blocks in `BuildGates.Tests.ps1`. **And it discriminates rather than passing vacuously:** run against this same file's **pre-edit** state from `git show HEAD:` it exits **1**; against the shipped state, **0**. `verify-build-config.py` PASS — 61 steps, **46** gates (was 45) |
| **The `.json.data.xml` deviation** | **E4 — proven by direct comparison, no level needed** | Local | `automation-agent` edited that file's comment block after being told to change nothing in it, on the ground that it instructed a human to pin the retired A-R33 *"run only users"* control. Verified rather than accepted: both versions parsed and canonicalised to (tag-path, attributes, text) triples — **23 nodes each, identical set**. Draft `StateCode 0`/`StatusCode 1` kept, casing untouched. **Deviation accepted:** a stale instruction to configure a control that no longer exists, in the file a deployer reads, is worse than the overstep |
| **`rev_roundstatisticsresult` + 4 attributes + alternate key, the superseding descriptions, the entity list, `Solution.xml`, `auditedTables`, the seed script, parent TAD §3.1** | **V2** | Local | `pac solution pack` both package types exit 0, unpacked `customizations.xml` carrying the new entity; `root-components-resolve` PASS (70 components, every one resolving both ways); `component-shape` PASS; `tad-coverage` PASS (174 column specs across 13 table blocks); `audited-tables` PASS; `field-security-coverage` PASS (68 secured columns, **unchanged** — the new table adds none); `role-privilege-ownership` PASS (92 privileges / 3 roles); `domain-invariants` PASS; `forms-and-views-reachable` PASS with exactly the two expected schema-only-table warnings; `EnsureSchema.Tests.ps1` **45/45**; `DataverseScripts.Tests.ps1` **81/81** (was 56/56 — the 25 added tests are the first that execute the three seeders' own logic; the 56/56 figure this row originally carried proved nothing about "the seed script" it names, see §5's correction note). **What it does not prove:** that any of it exists in an environment. The table is absent from DEV and `C-TECH-050` means no import will create it |
| **The rollout order itself** | **V1 — a config that preflights is not a config that has run** | Local | `verify-pipeline-config.py` PASS — 104 steps across 3 environments, 46 executable / 58 manual, every `.ps1` parameter resolved against the script's own `param()` block, artifact path resolved per run, PRD rollback declared. **What it does not prove:** anything about the nine steps' outcomes. Steps 3–9 are all live actions nobody has taken |
| **The Code App's result-table read and the age-bound freshness cycle** | **V2** | Local (macOS) | `npm run typecheck` 0; `npm run lint` 0; `npx vitest run` **662/662 across 38 files** (was 637/37); `npm run coverage` **98.52% statements / 98.52% lines / 93.32% branches** against the 80/80 threshold — the **figure** checked, not the pass count (A-R41, `IMP-0132`); `npm run build` 0. `verify-code-app-column-bindings.py` OK over **101** authored files against 63 forbidden columns, now scoped across 9 tables including the new one. `code-app-data-sources` passes **only with the `--allow` line** below. **What none of it proves:** the tests mock the SDK and a mock never resolves a data source, so nothing here is evidence that any read or write reaches Dataverse |
| **The freshness predicate — falsified, and one mutation SURVIVED** | **V4 by mutation** | Local | Four mutations to `isCurrent`/`ageInSeconds`: `<=`→`>=` killed (5 failures); a null bound reading as always-fresh killed (3); deleting the on-mount short-circuit killed (2); and **making a null `rev_computedon` age as `0` instead of `NaN` SURVIVED with 41 tests passing.** That is precisely the null-check trap TAD §5.3.1 says an age comparison *"cannot express"* — the claim is true of the comparison and false of the helper feeding it. Two cases were added (a parseable document *with* a bound but a null or unparseable stamp), the mutation re-run and killed, and the file confirmed byte-identical to its pre-mutation original. **This is the most useful result in the revision**: three careful readings of that claim found nothing, and one mutation run found the gap |
| **The `--allow` allowance on `code-app-data-sources`** | **V2, and it is ordering rather than debt** | Local | The gate correctly fails on `rev_roundstatisticsresults` being registered in `READ_SERVICES` and absent from the generated `dataSourcesInfo.ts` — because **the table does not exist live**, and `pa app add data-source` reads a table's metadata from the environment. Neither generated file was edited (`grep -c rev_roundstatisticsresult` → **0** in both `dataSourcesInfo.ts` and `power.config.json`), because hand-authoring there fabricates platform-assigned connector metadata (`C-TECH-051`) in the one file whose value is that the platform wrote it. The step's own documented escape hatch is used instead, with an owner and a clearing action in the reason string. **First use of `--allow` in this project** |

#### Revision 0.10 — the C-TECH-014 coverage unblock, and the two defects the tests found (2026-08-28)

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| **25 new behavioural tests over the three round-statistics seeders** | **V2, and the only level that answers the question that halted the build** | Local (macOS, Pester 5.7.1, fake Dataverse Web API) | `Invoke-Pester src/tests/provisioning/DataverseScripts.Tests.ps1` → **81/81 PASS** (was 56/56): [7 `It` blocks for the request seeder](../../src/tests/provisioning/DataverseScripts.Tests.ps1#L1091), [8 for the result seeder](../../src/tests/provisioning/DataverseScripts.Tests.ps1#L1216), [10 for the test-data seeder](../../src/tests/provisioning/DataverseScripts.Tests.ps1#L1318). Each runs the real script unmodified via `& $path -Env <env>` and asserts **the request it sent** — entity set, keyed-PATCH-not-POST, the exact column set written, the create-only non-reconciliation, the 403-is-not-404 rethrow, the DEV/TST-only refusal, and the open-round guard. **What it does not prove:** every Dataverse call is a fake. No seeder has been run against any environment in this dispatch |
| **C-TECH-014 back over the bar** | **V2 — a measured figure, not a pass count** | Local | `pwsh src/tests/Invoke-Tests.ps1 -CodeCoverage` → **941 passed / 1 failed / 1 skipped** in 105.5 s, then the gate exactly as the build invokes it: `python3 scripts/verify-coverage-threshold.py <dir>/coverage.xml --threshold 80 --exclusions config/coverage-exclusions.json` → **`1711 of 2059 line(s) covered = 83.1%`, exit 0**, 26 files counted / 4 excluded. Per-file JaCoCo LINE counters for the three: **30/31, 30/31, 104/106 — 96.8%, 96.8%, 98.1%**, from 0/31, 0/31, 0/99. **No entry was added to `config/coverage-exclusions.json`** — this was a real gap, not an untestable script. The single red is the pre-existing improvement-queue trigger described above, unchanged in kind and now worse in degree (see below) |
| **DEFECT FOUND AND FIXED — the test-data seeder wrote to the wrong table** | **V4 by mutation** | Local | `seed-round-statistics-test-data.ps1` PATCHed `rev_status`/`rev_resultjson`/`rev_computedon` on **`rev_roundstatisticsrequests`**. ADR-038 moved all three to `rev_roundstatisticsresult`, but the request table's copies were **retained, not deleted** (TAD §3.9.2), each carrying a shipped `<Description>` reading *"UNUSED FROM REVISION 5 (ADR-038). Written by nothing and read by nothing."* So the PATCH succeeded, the script printed `CREATED`, exited 0, and the charts stayed empty — the app reads the answer from the result table ([`schema.ts`'s `ROUND_STATISTICS_REQUEST_COLUMNS`](../../src/code-apps/trustee-review-portal/src/dataverse/schema.ts#L339) is that row's primary key and nothing else, pinned by `schema.test.ts`). Corroborated three ways before changing anything: the `Entity.xml` descriptions, the app's own schema constant plus its test, and `provisioning/README.md`. **Proven able to fail:** re-introducing the old entity set kills **6** of the 10 test-data tests; reverting leaves the file byte-identical (`diff` clean) and the suite green |
| **DEFECT FOUND AND FIXED — StrictMode on the Dataverse null shape** | **V4 by mutation** | Local | The Web API **omits** a null-valued column from a response body rather than sending it as `null`, so on the first run after `seed-round-statistics-result.ps1` the probe answers with no `rev_resultjson` property at all — and `$before.rev_resultjson` under `Set-StrictMode -Version Latest` is a **terminating** `PropertyNotFoundException`, not `$null`. Verified in isolation first (`pwsh` one-liner: *"The property 'rev_resultjson' cannot be found on this object"*), not assumed. The exception fell into the surrounding `catch` and reported **FAILED on the one path the script exists to serve**. Fixed with a `PSObject.Properties.Name -contains` guard. **Proven able to fail:** restoring the unguarded access kills **4** tests |
| **A third correction, no level needed** | **E4 — direct comparison** | Local | The same script would have **upserted the result row into existence** on a 404, because a keyed PATCH is a create. `rev_roundstatisticsresult` holds exactly one row ever and establishing it belongs to `seed-round-statistics-result.ps1`, so the 404 is now reported as FAILED naming that script. This is a behaviour **change**, not a bug fix, and it is called out separately for that reason |

**Two things about `verify-improvement-log.py --check` that the next reader needs, and they point in opposite directions.** Run **bare** it exits **0** — the log is structurally valid, and my five appended entries are well-formed. Run with `--check`, which is how the HARD `improvement-log-check` build step invokes it, it exits **1**, because **43 findings sit unread against a batch trigger of 10**. That is not a defect in anything this revision produced and it cannot be cleared from here: only `improvement-agent`, behind `APPROVE IMPROVEMENTS`, closes a finding, and stamping a `deferred_reason` to unblock one's own build is explicitly forbidden. It is reported at the gate as a routing obligation rather than left to be discovered 33 steps into a build (`IMP-0285`). The same single failure is the only red in `BuildGates.Tests.ps1`'s **111/112**.

#### Revision 0.11 — `IMP-0438`: the request seeder's `rev_status` write removed (2026-08-28)

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| **The fix itself** | **V1 — source-level, and V1 is the honest ceiling** | Local (macOS) | [PATCH body](../../provisioning/dataverse/seed-round-statistics-request.ps1#L139) is `@{ rev_name = $requestKey }`. The HARD gate that found the defect, run exactly as [the build invokes it](../../config/revitalise-grant-automation-build.yml#L195): `python3 scripts/verify-superseded-column-writers.py` → **`OK — 3 marked column(s) examined across 38 writer candidate(s); 0 finding(s), 0 baselined`**, exit 0. **What it does not prove:** no seeder was run against any environment in this dispatch, and the gate resolves co-occurrence within a file rather than per statement (its own stated residual) |
| **`rev_resultjson` / `rev_computedon` — checked, not assumed** | **E4 — direct comparison against the corpus** | Local | The dispatch named `rev_status` and required the other two be verified. `grep -rn "rev_resultjson\|rev_computedon" provisioning/ src/solutions/` puts both in this script exactly once each, in header prose explaining why they are not written (line 24 of the pre-fix file); every live write of either is the flow's, to `rev_roundstatisticsresults` ([5 write actions](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L1113)). Both were already clean |
| **The corrected behaviour is asserted, not merely un-broken** | **V4 by mutation — three mutants, each killed by name** | Local (Pester 5.7.1, fake Dataverse Web API) | [The regression lock](../../src/tests/provisioning/DataverseScripts.Tests.ps1#L1110) asserts the forbidden columns **by name first**, then the closed set. Mutant A — the real defect, `rev_status = 2` restored — killed, message: *"Expected 'rev_status' to not be found in collection @('rev_status', 'rev_name') … but it was found."* Mutant B — `rev_resultjson` + `rev_computedon` + `rev_triggeredon` — killed, naming `rev_resultjson`. Mutant C — `statecode`, a column on **no** forbidden list — killed by the closed-set assertion (*"Expected 1 … but got 2"*), which is what catches a column nobody thought to forbid. Each mutant was exactly one line; the file was restored and confirmed byte-identical by `shasum -a 256 -c` (`91806d32…8cfc`), and the suite re-run green afterwards |
| **The suite the last dispatch left green** | **V2 — a measured figure** | Local | `Invoke-Pester src/tests/provisioning/DataverseScripts.Tests.ps1` → **81/81 PASS, 0 failed**, unchanged in count: one `It` was rewritten and one stale assertion deleted, and **no `It` was added**, because the existing suite already had the right shape for this defect |
| **C-TECH-014 re-verified, not assumed** | **V2 — the figure checked, not the pass count (`IMP-0132`)** | Local | `pwsh -NoProfile -File src/tests/Invoke-Tests.ps1 -CodeCoverage` → **942 passed / 0 failed / 1 skipped**, then the gate as the build invokes it: `python3 scripts/verify-coverage-threshold.py <dir>/coverage.xml --threshold 80 --exclusions config/coverage-exclusions.json` → **`1711 of 2059 line(s) covered = 83.1%`, exit 0**, 26 counted / 4 excluded. Per-file JaCoCo LINE counters for the three seeders: **30/31, 30/31, 104/106** — identical to Revision 0.10. **No new test lines were needed and none were added**, which is what the dispatch asked be confirmed rather than assumed. **The full suite is green for the first time in this feature**, and not by anything this revision did: the single long-standing red was the `verify-improvement-log --check` CI-gate test, and a concurrent `improvement-agent` session stamped the queue mid-dispatch (`IMP-0434`/`IMP-0439`/`IMP-0446` now carry dispositions). Measured, not inferred: an earlier run in this same dispatch, 20 minutes before, was **941 / 1 / 1** |
| **`C-TECH-042` — the convergence declaration this script never had** | **V1** | Local | `python3 scripts/verify-provisioning-step-convergence.py .` → **`PASS — 36 numbered provisioning step(s): 21 read-only, 6 reconciling, 9 create-only and every one of those carrying a CONVERGENCE declaration`**, exit 0. Before this revision the seeder was one of three round-statistics scripts the gate reported `UNCLASSIFIABLE` — *"Not a pass: add markers, or accept that convergence here is unrecorded"* — and it is now classified, with the residue named in the declaration itself. **Still `UNCLASSIFIABLE`, deliberately out of this dispatch's scope:** [`seed-round-statistics-result.ps1`](../../provisioning/dataverse/seed-round-statistics-result.ps1#L88) (which carries a `# CONVERGENCE:` line the gate cannot see for want of a numbered marker) and `seed-round-statistics-test-data.ps1` |
| **Two shipped `<Description>` values got longer, and the limit governing them is precedent, not proof** | **E3 — precedent inside this solution; NOT a verified platform limit** | Local | The corrected entity description is **687** chars and the option-set description **839**. Three descriptions already committed in this same solution are longer — `rev_likertresponse` **1699**, `rev_application` **1434**, `rev_agreementresponse` **1265** — and all travel the same `ensure-schema.ps1` `Description` label path. `field-length-limits` passes but **does not examine metadata description length at all** (its own output enumerates flow descriptions and settings-row values), and a Microsoft Learn search returned no categorical figure for a metadata `Description` label, so **no limit figure is claimed here**. Stated as a residual rather than closed: the honest position is that these two values are well inside what this solution already ships, not that a ceiling was verified |
| **Nothing else in the build's source-side gates moved** | **V1/V2** | Local | 16 gates re-run bare, all exit 0: `superseded-column-writers`, `shipped-content`, `tad-coverage` (174 column specs / 13 tables), `root-components-resolve` (70 components), `audited-tables`, `field-length-limits`, `component-shape` (36 files / 2 shapes), `guid-syntax`, `source-validate` (91 XML well-formed, 5 flows parse), `provisioning-step-convergence`, `declared-property-reaches-creation-path`, `metadata-write-verbs` (73 calls / 36 scripts), `provisioning-test-presence`, `source-reader-plurality`, `assumption-markers` (14 OPEN rows, every marker present), `preflight-build-config`. **What this does not prove:** every one is source-vs-source, which is precisely the class that passed over this defect for three days |
| **DEV divergence — recorded, not repaired** | **not verified live, and deliberately so** | — | The live request row keeps `rev_status = 2` from the pre-fix body; the seeder is create-only so it reports `EXISTS` and never rewrites it. No live write attempted, none proposed, `IMP-0449` is the record. Anyone wanting the live value has one query: `rev_roundstatisticsrequests(rev_name='CURRENT')?$select=rev_status` |

#### Revision 1.5 — TAD Revision 7: ADR-040/041/042 (2026-08-30)

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| **Nav bar, grid width, header padding, subheading — all source-level component/markup changes** | **V2** | Local (macOS) | `npm run typecheck` 0; `npm run lint` 0; `npx vitest run` **689/689 across 38 files** (was 685/685); `npm run coverage` **98.52% statements / 98.52% lines / 93.49% branches / 94.49% functions** against the 80/80 threshold; `npx vite build` 0, chunk-size warning unchanged (§ below). `verify-code-app-column-bindings.py`, `verify-code-app-composition-root.py`, `verify-code-app-data-sources.py` all re-run, all exit 0, no change in shape |
| **The self-hosted `@font-face` — a real font file, licence checked, not merely "no error"** | **V2, plus a direct check of the shipped bytes** | Local | The built `dist/assets/index-*.css` contains exactly **2** `@font-face` rules and exactly **2** `data:font/woff2;base64,` occurrences, and **0** occurrences of `googleapis`/`gstatic` — checked with `grep -o` against the actual production bundle, not the source file alone. The two font files under `src/assets/fonts/playfair-display/` are byte-identical to the files inside `@fontsource/playfair-display@5.3.0`'s own `files/` directory (same npm package, same weights, same script style — `playfair-display-latin-{400,700}-normal.woff2`), and that package's own `LICENSE` file (SIL Open Font License 1.1, copied alongside as `OFL-LICENSE.txt`) explicitly permits embedding |
| **The container-query shrink-to-fit clamp — V4-EQUIVALENT, but against evergreen Chromium, NOT the Code App's own WebView2 host** | **V4-equivalent against real Chromium; NOT V4 against the actual host** | Local, Playwright 1.62.1 (Chromium) | A static HTML harness loading the real, built `dist/assets/index-*.css` and the exact hashed CSS-module class names it emits (`_statTile_woc2t_289`, `_statTileValue_woc2t_296`) rendered a tile in a ~900px-wide container at computed `font-size: 32px`, and the identical markup in a ~260px-wide container at computed `font-size: 20px` — the clamp genuinely reads the container's own width, exactly as designed, not merely "declared and hoped." `CSS.supports("container-type","inline-size")` → `true` in this Chromium build. **What this does NOT prove:** anything about the specific WebView2 build the Power Apps Code App host embeds — TAD §12.2's own closing step (a real signed-in trustee, the live app) is unperformed and is the only thing that can close `A-R54` |
| **The nav bar's colour pairings — reused, not new, and re-confirmed via the same real-Chromium harness** | **V4-equivalent against real Chromium** | Local, Playwright | The same harness's computed styles: the selected tab renders `rgb(204,0,120)` background / `rgb(255,255,255)` text (white on `--brand-primary`, already asserted 5.47:1 by `ds-tokens.test.ts`); the unselected tabs render `rgb(240,238,238)` background / `rgb(0,32,96)` text (`--text-heading` on `--grey-100`, already asserted passing by the same suite) — matching what was declared, not merely what compiled |
| **§8.5's eight accessibility properties and the `<dt>`/`<dd>` StatTile pairing — re-checked against source, not re-derived from scratch** | **V1/V2 — a source re-read, not a fresh audit** | Local | None of `StatTile.tsx`'s markup moved (still `<div><dt>…</dt><dd>…</dd></div>`, unchanged this revision); `Panel.tsx`'s `Definitions`/`StatTileRow` are untouched; `.table`'s `scope`/`aria-sort` markup is untouched; `print.css`'s `data-print` selectors are untouched and the new nav bar carries `data-print="hide"` on the same pattern as the control it replaced; the new `<h2>` uses the same global heading rule every other `<h2>` on the screen already used. **No test asserts a rendered screenshot of any of this** — that remains a V4 step |

### Tool warnings triaged (C-TECH-055)

| Warning | Source step | Resolved / Accepted | Rationale if accepted |
|---|---|---|---|
| `pac solution pack` reports 14 `RootComponent`/`EnvironmentVariableDefinition` entries "not defined in customizations" | `pac solution pack --packagetype Unmanaged` | Accepted, pre-existing | Present before this dispatch's changes (relationship/environment-variable declarations from earlier work), unrelated to `rev_roundfinance` or the new flow; not touched by this WBS scope |
| None from `pac solution check` | hosted Solution Checker | Resolved | 0 Critical/High/Medium/Low/Informational |
| `verify-forms-and-views-reachable.py`: 2× on `rev_roundfinance` — `Entity.xml` declares empty `<FormXml />` and `<SavedQueries />` markers with no matching folder content | `forms-and-views-reachable` (build step, `scripts/verify-forms-and-views-reachable.py src/solutions/RevitaliseGrantAutomation`) | Accepted | Same warning shape already accepted with recorded rationale for the 4 WBS-0.4 finance/record-only tables — `rev_bankaccount`, `rev_payment`, `rev_provider`, `rev_anonymisedstatistic` (see [parent Dev Summary, "Tool warnings" note](docs/development/revitalise-grant-automation-dev-summary.md#L5446)). `rev_roundfinance` is likewise a schema-only, organization-owned table (TAD ADR-028): it carries no form or view because no UI is in `wbs:6.9`'s scope — the round-statistics landing screen reads it only through the new flow's typed service, never through a Dataverse form. Not a defect. |
| `verify-forms-and-views-reachable.py`: 2× on `rev_roundstatisticsrequest` — `Entity.xml` declares empty `<FormXml />` / `<SavedQueries />` markers with no matching folder content | `forms-and-views-reachable` | Accepted | Identical warning shape, and identical rationale, to the four WBS-0.4 record-only tables already accepted in the row above. `rev_roundstatisticsrequest` is a one-row, schema-only table holding the trustee's *ask*: the app writes `rev_triggeredon` through the Code App's typed service and the flow triggers on it, so no form and no view is in `wbs:6.9`'s scope. The empty markers are **required, not incidental** — `IMP-0006`: without them SolutionPackager drops the folders silently at pack time. Not a defect. |
| `verify-forms-and-views-reachable.py`: 2× on `rev_roundstatisticsresult` — same shape | `forms-and-views-reachable` | Accepted | Same rationale again, for ADR-038's answer table (TAD §3.9). Read by the app only through `dataSourcesInfo.ts`'s generic connector, written only by the flow; no UI in scope. |
| `vite build`: "Some chunks are larger than 500 kB after minification" | `code-app-build` (`npm run build`, re-run this revision) | Accepted, pre-existing and **not worsened by this revision** | Fluent UI v9's own bundle is what crosses the threshold; it predates this pass. The design-system adoption adds **zero npm dependencies** (ADR-033) and its whole contribution to the bundle is the CSS — 9.51 kB — so this warning is not attributable to it and is no larger because of it. Splitting the vendor chunk is a build-configuration change with its own risk against a Preview host, outside this revision's WBS scope. Recorded rather than left untriaged (`C-TECH-055`) |
| `npm ci` reports `npm warn deprecated glob@10.5.0` | `code-app-install` (`npm ci`) | Accepted | Same warning, same dependency chain, already accepted with recorded rationale in the parent Dev Summary: it is a **dev/test-only transitive dependency** — `@vitest/coverage-v8` → `test-exclude@7.0.2` → `glob@10.5.0`, confirmed with `npm ls glob` — absent from the shipped `dist/` bundle entirely, and `npm audit` reports 0 vulnerabilities at every severity (see [parent Dev Summary, "Tool warnings" note](docs/development/revitalise-grant-automation-dev-summary.md#L4893), item 2). It clears when Vitest updates its own dependency; not introduced by this revision and nothing in this repository pins it. Not a defect. |
| `npm run coverage` (build step `code-app-unit-tests`) prints repeated *"Keyborg instance kN is being disposed incorrectly."* to stderr | `code-app-unit-tests` (`npm run coverage`) | Accepted | Same warning, same root cause, already accepted with recorded rationale in the parent Dev Summary: a `console.error` from a Fluent UI internal — `node_modules/keyborg/dist/index.js:365`, reached when `disposeKeyborg(id)` is called for an id no longer in its refs map — and it is **guarded by `if (process.env.NODE_ENV !== "production")`**, so it cannot reach the shipped bundle (see [parent Dev Summary, "Tool warnings" note](docs/development/revitalise-grant-automation-dev-summary.md#L4893), item 3). Test-harness-only, zero production impact; not introduced by this revision. Not a defect. |

**One caveat on the `rev_roundfinance` row, found while adding the two above (2026-08-28), and it is the
`IMP-0410` shape.** Run here today the gate emits **12** warnings across 6 tables and `rev_roundfinance` is
**not** among them; run against a clean checkout it emits **14** across 7 and `rev_roundfinance` is. The
difference is that `Entities/rev_roundfinance/FormXml/main/` and `SavedQueries/` (two view files) exist in
this working tree as **untracked** files — `git status` reports both directories `??`. So the gate's verdict
currently depends on local filesystem state that no commit carries, exactly the class `IMP-0410` records for
`verify-audited-tables.py`. Measured rather than reasoned: the 14-warning figure comes from running the gate
against an `rsync` copy of the solution tree with those two untracked directories excluded. **The
`rev_roundfinance` row above is therefore correct for CI and stale locally**, and the untracked files are
another session's in-flight work — left untouched, not deleted, and flagged here rather than silently
reconciled.

**Revision 0.11 — `C-TECH-055` for this fix: zero new warnings, five pre-existing outputs re-observed and owned elsewhere.** Every SOFT or advisory line seen while re-running the gates was present before this dispatch and is unchanged by it, so each is recorded here rather than left untriaged: `derived-counts` **3 drifted prose claims** (one is `REV Trustee.xml:73` saying 51 secured columns against source's 52 — another session's row); `source-derived-test-counts` **11 fragile literals of 14 source-coupled assertions across 10 files**, identical before and after my test edit, so this revision added none; `provisioning-step-convergence` **15 open-or-unclassifiable items**, now one fewer than before; `declared-property-reaches-creation-path`'s **`$lookupBody` `IsAuditEnabled` known gap**, latent (all 12 lookups declare 1); `provisioning-test-presence` **4 baselined scripts**, each dated and owned. And one gate output that is a warning about itself: `IMP-0450`, below — `provisioning-step-convergence`'s remediation text prints a marker its own parser rejects.

**Revision 1.5 — TAD Revision 7: zero new warnings.** `npx vite build`'s "Some chunks are larger than 500 kB"
line is unchanged in cause and unworsened by this pass — the ~60KB of base64 font data landed in the **CSS**
bundle (76.43KB total, up from ~16KB before this revision), not the JS chunk the warning names, and the CSS
size is unrelated to that warning's own threshold. `npm ci`'s `glob@10.5.0` deprecation and the Keyborg
disposal stderr lines are the same pre-existing, already-accepted outputs recorded above, re-observed
unchanged.

### Diagnostic components created and removed (C-TECH-056)

None in DEV or any live environment. Every live create in DEV this session (`rev_roundfinance`, its
attributes, the 3 redacted columns, the role privileges, table auditing) is the actual feature deliverable,
not a throwaway probe.

**Revision 1.5 — two temporary local files, created purely to obtain the container-query ground truth above,
both removed.** `scripts/tmp_verify_harness.html` (the static HTML page loading the built stylesheet) and
`scripts/tmp_verify.mjs` (the Playwright script that rendered it and read computed styles), both under
`src/code-apps/trustee-review-portal/`. **Verified removed:** `git status --short` for that directory shows
neither file, and `find src/code-apps/trustee-review-portal -iname 'tmp_verify*'` returns nothing. The `dist/`
directory the verification also used is gitignored (`src/code-apps/trustee-review-portal/.gitignore:4`) and
was rebuilt clean afterwards by `npm run build` for the `verify-build-config.py` preflight below, so no stale
copy is left uncommitted or unaccounted for.

**Revision 0.8 — eleven temporary source mutations, all reverted, recorded here because C-TECH-056 covers
temporary artefacts created during investigation and not only components created in an environment.** Proving
a gate can fail means breaking the thing it guards, so this revision deliberately introduced defects and
checked the suite went red: reverting the primary colour to the design system's own pink; adding a
`color: var(--text-muted)` rule; deleting the `sm` button's 44px minimum; reintroducing `--warning`;
weakening the input boundary to `--border-default`; setting `outline: none`; adding a remote font import;
deleting `main.tsx`'s `ds-tokens.css` import; deleting `harness.tsx`'s; and adding a real ES import and a CSS
`@import` from the `Designsystem/` directory (via one throwaway file, `src/leak.tmp.ts`). Every mutation
failed between 1 and 5 assertions, every one was reverted, and the tree was re-confirmed green afterwards —
637/637. **Verified removed:** no `.tmp`, `.bak` or `leak` file exists anywhere under the app's `src/`, and
`git status` lists none.

**Revision 0.10 — two temporary source mutations, both reverted, and nothing created in any environment.**
No live call of any kind was made in this dispatch, so there is no environment component to remove. Two
deliberate mutations to `provisioning/dataverse/seed-round-statistics-test-data.ps1`, each to prove the new
regression locks can fail rather than assuming it: (1) restoring the `rev_roundstatisticsrequests` entity set
→ **6** of the 10 test-data tests failed; (2) restoring the unguarded `$before.rev_resultjson` access →
**4** failed. **Verified removed:** the file was restored from a pre-mutation copy and `diff` against that
copy reports **identical**, with the full suite re-confirmed at 81/81 afterwards. Working files (the settings
fixtures, the pre-mutation copy, the `rsync` tree used to reproduce CI's `forms-and-views-reachable` verdict,
and the coverage artifact directory) were all written under `/tmp` and removed; `provisioning/deploymentSettings/acc-settings.json`
— the harness fixture `IMP-0410` warns about — is confirmed **absent** after the run, and `audited-tables`
exits 0.

**Revision 0.11 — three temporary source mutations, all reverted, and one of them was read by another session
while it was live.** No live call of any kind was made in this dispatch. Three deliberate one-line mutations to
[`seed-round-statistics-request.ps1`](../../provisioning/dataverse/seed-round-statistics-request.ps1#L139), each
to prove the rewritten regression lock can fail: (1) `rev_status = 2` restored — the real defect — killed the
lock naming `rev_status`; (2) `rev_resultjson` + `rev_computedon` + `rev_triggeredon` added, killed naming
`rev_resultjson`; (3) `statecode`, on no forbidden list, killed by the closed-set assertion. **Verified
removed:** `shasum -a 256 -c` against the pre-mutation digest reports `OK` (`91806d32…8cfc`) and the suite is
81/81 afterwards. Working files (the digest file, the coverage artifact directories, the four finding JSONs)
were written under this session's scratchpad, not the repository, and `provisioning/deploymentSettings/acc-settings.json`
is confirmed **absent**. **The `C-TECH-056` lesson this adds:** a mutation window on a real provisioning script
is visible to any concurrent session, because the Pester harness invokes the script by its real path and the
mutation cannot be made anywhere else. Mutation 2 was read at 15:33 by a concurrent `improvement-agent` and
logged as a `blocker` (`IMP-0446`); the corrective mechanism is on the observer side, and `IMP-0447` proposes
it. Removing the practice would be the wrong fix — the three kills above are the only reason the lock is known
to work.

### Revision 1.0 — the four statistics metrics (`wbs:6.9`, 2026-08-28)

**Highest level executed: V1 (definition-level), and nothing above it.** No pack, no import, no designer
save, no run, no live figure reconciled against an admin-side tally. Every expression added this revision is
first exercised by a designer save. Stated plainly because three requirement rows in Appendix A now read
"delivered" on the strength of what is below, and `C-TECH-053` requires the level executed, not the level
hoped for.

| # | What was executed | Result | What it does and does not prove |
|---|---|---|---|
| 1 | `json.load` on the flow definition | Parses | The file is well-formed JSON. Says nothing about whether the platform accepts the definition |
| 2 | Independent composition simulation, written in this session and **not** reusing the sub-agent's evaluator | All 6 new `Compose` documents and `Compose_response_body` parse as valid JSON; §3.3 key order exact and unchanged | The response document's **shape** is sound whatever the expressions evaluate to. Deliberately dumb by design — it concatenates the literal skeleton and substitutes stand-ins, so it cannot be fooled by an expression bug it shares with the author. Does **not** prove any arithmetic is right |
| 3 | `verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation` | exit 0, 5 definitions clean | No `select()`/`filter()` expression, no alternate-key Row ID, no nested `item` on an `UpdateRecord`, no `InitializeVariable` below top level. 3 pre-existing declared check-7 exceptions printed and unchanged by this revision |
| 4 | `verify-flow-trigger-body-isolation.py --solution … <flow>` | exit 0, checks A1/A2/A3/B1 clean | No trigger-body read. **Note the invocation:** with no arguments this gate prints usage and exits 2 — a bare run is not a result, and one was nearly reported as one this dispatch |
| 5 | `verify-assumption-markers.py` | PASS — 18 OPEN rows, every marker in source (was 15) | `C-TECH-052` satisfied **mechanically**, not by re-reading the register. A-FLOW-08/09/10 each carry their token at the point of the guess |
| 6 | `verify-tad-coverage.py` (HARD, `C-TECH-066`) | exit 0, after a gate fix — see below | TAD §3.1's 174 column specs all present or deferred; 7 OK-document null keys all acquitted, 3 of them against register `UR-002`/`UR-003` |
| 7 | New Pester suite `src/tests/solutions/RoundStatisticsContract.Tests.ps1` | **35 of 35 pass**, re-run independently in this session | The source-level regression test D-11 required. Option-set integers are **derived from `OptionSets/*.xml` at test time**, not hardcoded — mutating the XML alone fails 6 assertions, which is the proof they are derived |
| 8 | Code App suite `npx vitest run --coverage` | **662 tests, 38 files, all pass; 98.52% statements / 98.52% lines** | Well clear of the HARD 80% (`C-TECH-014`). No app file was changed this revision, so this is a no-regression result, not new coverage |

**The HARD gate failed first, and the reason is the most important thing in this section.** `verify-tad-coverage.py`
exited 1 on the first run. Its null-detection classifies a key by the statuses composed inside the narrowest
enclosing action: an action composing `"status":"ok"` builds the OK document, anything else is a non-ok
document and is correctly ignored. **A status-free helper `Compose` matched neither** — its status set is
empty, which is `!= {"ok"}` — so the moment the four money nulls moved out of `Compose_response_body` into
`Compose_breaktype_rows`, `Compose_breaktype_total` and `Compose_exceptional_funding_summary`, all three
became **invisible to the gate**, and it read `breakTypeProfile` as delivered while three of FR-060's four
measures were null one action away. That is this repository's `gate-reassures-wrongly` class, created by this
revision's own change.

Fixed by attributing a status-free fragment to the document(s) that **consume** it, transitively via
`outputs('<name>')`, with a cycle guard. `Compose_error_document` and `Compose_no_open_round_document`
compose their own non-ok status, so they are still classified directly and never inherit.

**And the fix was falsified rather than trusted, because "I made the gate stricter" is exactly the claim that
should not be taken on its author's word.** Four mutants, every file restored and confirmed byte-identical by
`shasum -a256`:

- **UR-003 deleted** → gate still passed. The register is not the only acquittal path; Appendix A's `partial`
  marker acquitted it.
- **FR-060's Appendix A row rewritten to read "delivered"** → gate still passed. The register acquitted it.
- **Both removed** → gate *still* passed, which contradicted the expectation. Cause found by reading the
  code: assertion (d) skips a null key that **no Appendix A row mentions at all** (line 851), and the mutant
  row no longer named the keys.
- **Register acquittal removed AND an Appendix A row that names the keys but reads "delivered"** → **exit 1,
  three errors, one per money null.** This is the real failure condition, and it was **impossible before the
  fix**, because those keys sat in the ignored non-ok set.

**`C-TECH-057` is discharged by a committed test, not by that mutation cycle.** An ad-hoc mutation proves a
gate can fail *today*; it leaves nothing behind to stop the blindness returning. `verify-tad-coverage.py`'s
own selftest had 29 cases and **none** exercised `flow_null_response_keys` at all, so the fragment path was
guarded by nothing. Three cases were added (`--selftest` now reports **32**, 19 known-bad rejected, 13 valid
accepted): a null in a status-free fragment the OK document consumes **must fail**; the same null with a
declaring Appendix A row **must not** fire (the over-firing control); and a reference cycle between two
fragments **must terminate**. The fixture helper gained a `fragment_nulls`/`cyclic` parameter to build them.

Then the cases were themselves falsified against the pre-fix logic — reverting the one classification line
and re-running: `DID NOT BEHAVE null-in-a-status-free-fragment-the-OK-document-consumes → exit 0, 0
violation(s)`, and the selftest as a whole exits 1. The blindness reproduces exactly on demand, which is what
makes these negative tests rather than a restatement of the fix. Script restored byte-identical
(`shasum -a256`).

Two residual weaknesses in that gate are **reported, not fixed**: a null key mentioned in no
Appendix A row is silently skipped (assertion (d) line 851), and matching is by **leaf key name** rather than
by path, so registering `averageAmountRequested` once satisfies both its FR-059 and FR-060 occurrences. Both
are noted in `contract/tad-deferrals.json`'s `_response_fields_note` and proposed in `IMP-0461`; redesigning
a HARD gate's null-detection mid-dispatch is not a development-agent's call, and the second would need a
baseline pass for pre-existing unmentioned nulls.

**One correction to this dispatch's own brief, recorded because a stale premise is worth more than a
successful task.** The brief stated that no gate reads `undelivered_requirements`, so nothing would catch a
stale entry. That was true when Erratum 5.3 wrote it and is **false now** — `verify-tad-coverage.py` reads the
key, validates every `response_fields` name against the flow, and fails a dead promise. It caught this
dispatch's first attempt, which used dotted paths. `contract/tad-deferrals.json`'s own
`_undelivered_requirements_is_read_by_no_gate` key still asserts the opposite and is now the stale statement.

#### Revision 1.0 hours proposal — addendum for `commercial-agent` behind `APPROVE TIMESHEET`

No figure from `contract/wbs.json` or `contract/service-agreement.json` is restated here (`C-COM-008`, D-3),
and this is a **proposal**, never a booking — `logs/worklog.jsonl` is `commercial-agent`'s alone.

| WBS task | Proposed actual | Evidence behind the figure |
|---|---|---|
| `6.9` | 2.6 h | Ground-truthing the WDL math-function set and both option sets; one `automation-agent` dispatch producing 17 flow actions across 4 metrics; independent re-verification of its output (JSON parse, `$select`, key order, markers, an independently-written composition simulation); the `verify-tad-coverage.py` null-attribution fix plus a 4-mutant falsification cycle; TAD Appendix A/§0.8.1/§3.3/A-R51 corrections; `UR-001` cleared and `UR-002`/`UR-003` narrowed; this Dev Summary's §7/§10/§11 revisions; 3 gate re-runs and 2 test suites |
| `system` | 0.5 h | The `scripts/verify-tad-coverage.py` null-attribution fix and its falsification cycle are tooling for this repository's own gate, not the client's deliverable — separated per this document's own rule rather than billed to `6.9` |

Neither figure equals a WBS estimate (D-6). `wbs:6.9` is a covered id
(`contract/change-orders/CO-001.md`, APPROVED), so this work needed no new change order — but A-R28's sizing
re-confirmation is unaffected and remains `commercial-agent`'s.

---

### Revision 1.1 — the four money measures and the `k` gate (`wbs:6.9`, 2026-08-28)

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| **The 88 new flow actions** (15 `Filter array`, 20 `Select`, 49 `Compose`, 1 `List rows`) | **V1, plus the expression-level evaluation this project first used for the count metrics — and this time it was FALSIFIED FOUR TIMES rather than trusted** | Local (macOS); no live call of any kind | **Structure:** JSON parses; every `outputs()`/`body()`/`result()` reference resolves to a real action (derived, 0 unresolved); every `runAfter` key is a sibling at the same nesting level (0 violations); 193 descriptions ≤ 256 (`verify-field-length-limits.py` exit 0). **Gates:** `verify-flow-definition-language.py` exit 0 over all five flows — the `Select` **action** is not the non-existent `select(` **expression** its check 1 rejects, and a `"select":` JSON key does not match its regex, **confirmed by running it rather than by reading it**; `verify-flow-trigger-body-isolation.py` exit 0 **after the gate was extended, because it rejected the approved design** (§0.12.2). **Simulation:** a scratchpad evaluator over the shipped expression text, `xpath`/`sum` handed to **libxml2**, and **both `if()` branches always evaluated** so an untaken-branch throw is a failure — **31 assertions across six scenarios**, all pass: `k = 5` · `k` unseeded · `k` mistyped (`'five'`) · `k = 1` · `k = 0` · an empty round. The `k = 5` round carries simultaneously a break type with 8 costed rows **reconciled against a hand-computed mean**, one with **every** `rev_costs` blank, one with a **mix** (population 5 < count 9), one **below** `k` (count 3 published, all three money measures `null` — §3.3's worked example exactly), and one with **no applications at all**. **Falsified by mutation, four times, each reverted and re-confirmed green:** removing the empty guard from the XML → the total row's `averageCost` came back **`NaN`**; deleting one `max(…,1)` → **divide-by-zero**; using the row count as the denominator instead of the presence subset → the mean moved 900 → 500 and the population 5 → 9, which is §3.3 property 8's *"the one thing that will silently be false"* caught mechanically; deleting the `empty()` clause → **caught only by the `k = 0` scenario**, which is why that scenario was added. **What none of this proves:** no pack, no import, no designer save, no run. `xml`, `xpath`, `join`, `int`, `trim` and `startsWith` over these inputs are all first exercised by the platform at TAD §12.3 step 6 — **A-FLOW-11, OPEN** |
| **XPath 1.0 `sum()` semantics over this construction's own XML shapes** | **E1 by measurement against a conformant engine — narrower than a V-level, because it is a language fact rather than a run of anything** | Local (libxml2 via `lxml`) | `<r><v>10.5</v><v>20.25</v></r>` → `30.75`; `<r></r>` → **`0`**; `<r><v></v></r>` → **`NaN`**; `<r><v>10</v><v></v></r>` → **`NaN`**. This is what establishes §0.12.1's correction, and it is the reason the empty guard is inside the XML construction rather than only in the average's `if()`. **Not evidence about the Logic Apps wrapper** — a conformant local engine is a model of the runtime, and that distinction is the whole of A-FLOW-11 |
| **The source-level regression test** (`src/tests/solutions/RoundStatisticsContract.Tests.ps1`) | **V1, and the test itself was falsified by the same four mutations** | Local | **47 assertions, 0 failed** (was 34). The `A-FLOW-08` Describe was **replaced rather than deleted**, exactly as its own comment instructed — *"THIS TEST IS MEANT TO FAIL THE DAY SOMEONE BUILDS THEM … update these assertions, do not delete them."* Every break-type integer is still **derived** from `OptionSets/rev_breaktype.xml`, so a sixth option added to the XML reddens the suite rather than shipping a break type whose money figures nobody computes. New assertions of substance: the reduction template byte-for-byte; every measure's denominator **and** emitted population are its own presence subset, never the row count; `percentageOfCost` reads only the both-present sums; exactly thirteen composes read `k` and **no categorical compose does**; every selected column has an `item()?['…']` reader; every `Select` projects a scalar and none names a secured column. **Two of my own assertion defects found and fixed by running it** — `-BeLike` is wildcard matching and `item()?['rev_x']` carries `[ ]` (`IMP-0475`), and a `+` continuation inside a `-Because` argument sent the piped subject as `$null` (`IMP-0476`) |
| **The extended B1 gate — that it can still fail** | **V4 by mutation, over the boundary rather than the happy path** | Local | `--selftest` **20 cases, all PASS** (was 15). Five are new and four of them are *rejections*: a node-returning `'/r/v'` in place of `'sum(/r/v)'`; two different `Select` actions in the template's two `body()` positions; the **unguarded** form; and the template plus one extra row reference in the same expression. Plus an on-disk known-bad fixture (`UnguardedXPathSum.json`) confirmed rejected as a standalone run, and a `BuildGates.Tests.ps1` block holding it — **113 assertions, 0 failed**. The gate was **measured failing on the real flow before the extension**, which is the evidence that the extension was necessary rather than convenient |
| **The Code App parsers and rendering** | **V2 — local typecheck, lint, tests and coverage. Not V3, not V4** | Local (macOS) | `npm run typecheck` exit 0; `npm run lint` exit 0; `npm run coverage` — **676 passed / 676 across 38 files**, **98.53% statements / 98.53% lines** against the 80/80 threshold (`vitest.config.ts`). The **figure** is reported, not the pass count (`IMP-0132`). `verify-code-app-column-bindings.py` OK over 101 authored files against 63 forbidden columns; `verify-assumption-markers.py` PASS. **Falsified by mutation, twice, both reverted:** reverting `parseMoneyMeasure` to coerce a bare number → exactly the two *"rejects a bare number"* tests failed and nothing else; deleting the population from the rendered string → exactly the four population-visibility assertions failed, across both the unit and the integration layer. The harness fixture's break-type row 2 was changed to a **below-`k` example** (count 3, three `null` measures) so the suppressed shape is exercised end to end, not only in the parser unit tests. **What none of this proves:** jsdom computes no CSS and no live push was performed, so no result here is evidence that any figure renders correctly for a signed-in trustee — **A-R39** stands |
| **The seeded `k` row** | **V1 — source only. Explicitly NOT V3** | Local | JSON parses in all three settings files; `RoundStatisticsMoneyMeasureMinimumPopulation` = `5`, `Whole Number`, description 404 chars (under `rev_setting.rev_description`'s 500-char cap, `IMP-0009`); `DeploymentSettings.Tests.ps1` **39 passed / 0 failed / 1 skipped**, including a new cross-environment assertion, **falsified** by setting one file to `4` and confirmed to fail on that file specifically. `verify-audited-tables.py` OK, `verify-pipeline-config.py` OK (104 steps across 3 environments). **Not verified: that the row exists in any environment.** Seeding is `post_deploy` and no source-side gate can see it |
| **`UR-002`/`UR-003` cleared and Appendix A corrected** | **V1 — and the gate was measured failing first** | Local | `verify-tad-coverage.py` **exit 1 before**, with four assertion-(f) dead-promise violations naming `averageAmountRequested`, `averageCost` and `percentageOfCost`; **exit 0 after**, reporting *0 undelivered-requirement entry(ies)*. The register deletion and the Appendix A correction are in the **same change**, which is the condition `_undelivered_requirements_is_read_by_no_gate` names — deleting the entries alone would produce the mirror-image overclaim, a traceability row reading UNDELIVERED for a field that has a producer. `verify-doc-line-links.py` OK. The deferrals file's sha256 was recorded before editing and the edit was a surgical slice validated by `json.loads`, not a round-trip reformat |

**Revision 1.1 — `C-TECH-055`: one new warning class, triaged, and one gate output that is about this dispatch.**

- **`verify-code-app-data-sources.py` reports FAILED when run bare** — `rev_roundstatisticsresults` is
  registered in `READ_SERVICES` and not declared in `dataSourcesInfo.ts`. **Pre-existing and correctly
  handled, not a finding:** the build config invokes it with an owned, dated `--allow` naming TAD §12.3
  step 9 as the clearing action, and with that flag it exits 0. Recorded because a bare run of a HARD gate
  reading FAILED is exactly the shape someone re-verifies in a panic — **run it the way the build runs it.**
- **`verify-flow-definition-language.py` check 7 reports three real, suppressed findings**, one of them on
  this flow. All three are declared, owned and dated 2026-09-30, and all three predate this dispatch. **What
  this dispatch changed is the blast radius of one of them** (§0.12.4) — recorded rather than fixed, with the
  reason.
- **Zero new SOFT or advisory outputs** from any other gate. `derived-counts`, `source-derived-test-counts`,
  `provisioning-step-convergence`, `declared-property-reaches-creation-path` and `provisioning-test-presence`
  are unchanged in count and content from revision 0.11's triage.

**Revision 1.1 — `C-TECH-056`: six temporary source mutations, all reverted, nothing created anywhere.**
Four on the flow definition (the unguarded XML; one deleted `max(…,1)`; the row count as a denominator; the
deleted `empty()` clause) and two on the app (a coercing `parseMoneyMeasure`; a rendered string without its
population). Each was applied to a **temporary copy** or reverted immediately and re-confirmed green. One
scratchpad generator and one scratchpad evaluator were written and are **not shipped** — the durable
equivalents are `RoundStatisticsContract.Tests.ps1` and the extended B1 gate, which is deliberate: a
simulator nobody runs again teaches nothing.

#### Revision 1.1 hours proposal — addendum for `commercial-agent` behind `APPROVE TIMESHEET`

A proposal, never a booking. `logs/worklog.jsonl` is `commercial-agent`'s alone.

| WBS | Proposed actual | Evidence behind the figure |
|---|---|---|
| `6.9` | **3.4 h** | The flow's 88 actions authored through a deterministic generator rather than by hand (one script, three correctness iterations — a filter-name mismatch the existing contract test caught, one over-long description, one XML-guard correction); the XPath semantics measured against libxml2; a six-scenario expression evaluator built and falsified by four mutations; the B1 gate extended with five selftest cases and one on-disk fixture after it rejected the approved design; the contract test taken 34 → 47 assertions with two of its own assertion defects found by running it; `UR-002`/`UR-003` cleared and two Appendix A rows corrected against a gate measured failing first; the flow's notes.md FIFTH VERSION section; this document's §0.12/§2/§5/§7/§10/§11 and the six findings |
| `6.9` | **1.1 h** *(sub-agent, `frontend-agent`)* | `MoneyMeasure` and seven field-type changes; `parseMoneyMeasure` rejecting a bare number; a third absence token and two measure formatters; the break-type table's three money columns, the total row and the exceptional-funding item; a threshold-agnostic sentence in two places; the harness fixture moved to a below-`k` row; two mutation falsifications; 676 tests at 98.53% |
| `6.9` | **0.4 h** *(sub-agent, `config-agent`)* | One `rev_setting` row in three settings files with a 404-character description inside the 500 cap; the `settings-rows.notes.md` derivation; `DeploymentSettings.Tests.ps1` 14 → 15 rows plus a cross-environment assertion falsified by mutation; the pipeline config's `post_deploy` narrative |
| `system` | **0.3 h** | The B1 gate extension itself is arguably tooling rather than delivery — it is a `scripts/` change — but it was required to ship an approved design and its five selftest cases guard this feature's own disclosure boundary, so the bulk sits under `6.9` above and only the digest/log bookkeeping (six findings appended, validator, generator) is marked `system` |

**No figure here equals a WBS estimate**, per D-6, and no fee, rate or currency amount appears anywhere in
this revision (`C-COM-004`, D-3). Contracted hours and dates are **cited, never restated** (`C-COM-008`):
`contract/wbs.json` and `contract/service-agreement.json` are the baseline.

### Revision 1.2 — `IMP-0485`/`IMP-0486` (`wbs:6.9`, 2026-08-29)

**Highest level executed: V2 (packaged/built, locally verified) for the app; V1 (live, read-only) for the
platform-contract confirmation.** No `pac code push` this dispatch — deliberately held, see §0.13.

| # | What was executed | Result | What it does and does not prove |
|---|---|---|---|
| 1 | `pa connection list -e <env-id> --json`, live | 5 connections; the documented id absent, two others present | The connection landscape drifted since it was last documented (`IMP-0489`). Proves nothing about the app itself — establishes which id was safe to reuse |
| 2 | `pa app add data-source --connector dataverse --table rev_roundstatisticsresult -u <org-url> -c <connection-id> --non-interactive`, live | `Data source added successfully`; `dataSourcesInfo.ts`/`power.config.json`/`src/generated/*` regenerated | The platform's own `EntitySetName`/`PrimaryIdAttribute` echo, agreeing with `pipeline.log`'s independent read. Proves the data source is now DECLARED — not that a real signed-in trustee's read succeeds; that remains V4, unattempted this dispatch (unchanged residual, same class `IMP-0224` already named for this app) |
| 3 | `python3 scripts/verify-code-app-data-sources.py src/code-apps/trustee-review-portal` | OK — 7/7, 0 exemptions | The HARD gate this app already carries for exactly this defect class (`IMP-0329`) now passes with nothing waived |
| 4 | `npm run typecheck` / `npm run lint` / `npm run coverage` / `npm run build`, all local | Clean / Clean / 677/677, 98.53% stmt/line / Clean | Compiles, type-checks, passes every test with the SDK mocked, and bundles. Says nothing about a real signed-in user's session — the same residual every prior revision of this document has stated for this app |
| 5 | `git status`/`git diff --stat` before and after committing | Confirmed the design-system tree was 100% untracked beforehand; confirmed the commit's file list matches `src/code-apps/trustee-review-portal/**` plus this dispatch's own config/log/doc changes afterward | Proves the code now exists in `git log` — the fact a "shipped"/"implemented in full" claim requires (`IMP-0486`). Does **not** prove a browser has ever rendered it (A-R39, still OPEN, unchanged) |

#### Revision 1.2 hours proposal — addendum for `commercial-agent` behind `APPROVE TIMESHEET`

A proposal, never a booking. `logs/worklog.jsonl` is `commercial-agent`'s alone.

| WBS | Proposed actual | Evidence behind the figure |
|---|---|---|
| `6.9` | **1.6 h** | Live connection re-discovery after the documented id proved stale (`IMP-0489`, one new finding logged, allocated and validated); the `pa app add data-source` run and its four downstream file updates; `client.ts`/`client.test.ts`/`schema.ts`/`schema.test.ts` edits and the one test failure the stand-in's deletion caused, diagnosed and fixed; the `code-app-data-sources` `--allow` line removed and re-verified standalone; two CSS defects diagnosed against `@fluentui/react-select`'s own compiled source and `Designsystem/`'s actual spec rather than guessed; `app.module.css`/`ds.module.css` edits; a new `ApplicationFilters.test.tsx` (4 tests) and one new `ds-tokens.test.ts` block; the full local suite re-run (typecheck/lint/677 tests/build); committing the entire accumulated design-system tree for the first time; this document's §0.13/§10/§11/Findings Logged/Checklist and hours proposal |

**No figure here equals a WBS estimate**, per D-6, and no fee, rate or currency amount appears anywhere in
this revision (`C-COM-004`, D-3). Contracted hours and dates are **cited, never restated** (`C-COM-008`):
`contract/wbs.json` and `contract/service-agreement.json` are the baseline.

### Revision 1.3 — the failure-diagnosis descent (`wbs:6.9`, `IMP-0349`, `IMP-0483`, `IMP-0496`, 2026-08-30)

**Highest level executed: V2 (definition-level, self-consistency proven by an independent test suite) for the
descent; V1 (documentation-only) for the platform contract it rests on.** No pack, no import, no designer
save, no run — this dispatch is source/config-only by its own instruction, and `A-FLOW-13` above states
plainly what closing it needs.

| # | What was executed | Result | What it does and does not prove |
|---|---|---|---|
| 1 | Four Microsoft Learn pages read directly (`result()` function reference; *"Get context and results for failures"*; the Switch and Condition how-to guides; the control-workflow-action schema reference) | No worked example or prose passage names a `Switch` or `If` action as a `result()` target; only `Scope`/`For_each`/`Until` are ever shown | Establishes the assumption is a genuine, searched-for documentation gap, not an inference from silence nobody checked. Proves nothing about runtime behaviour either way (`IMP-0496`) |
| 2 | Structural analysis of the flow's own JSON (`python3`, ad hoc) | `Switch_on_open_round_count`'s only container child is `Condition_page_cap`; `Condition_page_cap`'s own 159 actions (2 true-branch, 157 else-branch) are all leaves — no third nesting level exists anywhere under it | Establishes the descent needs exactly two levels, not an open-ended recursion, and that nothing was left undescended by omission |
| 3 | `python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation` | exit 0. `REVPortalRoundStatistics` reports **zero** check-7 findings — no exception applied, none needed. The two untouched flows' exceptions print exactly as before (6 and 12 hidden descendants, unchanged) | The fix satisfies check 7 on the shape's own merits. Per the script's own residual, still proves only that the descent EXISTS, never that it produces a useful message on a real failure (`IMP-0109`) |
| 4 | `python3 scripts/verify-flow-definition-language.py --selftest` | 22/22 pass, including the two check-7 corpus assertions (now worded "two declared exceptions", was "three") | The gate itself can still fail (`C-TECH-057`), and the corpus assertions are live against the real tree, not only synthetic fixtures |
| 5 | `Invoke-Pester src/tests/solutions/RoundStatisticsContract.Tests.ps1` | **54/54 pass** (47 pre-existing + 7 new). New `Describe 'D-15 regression …'` asserts the exact branch structure, both gating expressions, that all three `Set_failure_detail*` leaves assemble the identical `Action:/Code:/Reason:` shape, that no `InitializeVariable` is nested (`IMP-0137`), and — re-invoking check 7 from inside the test — that the flow passes with the exception's dict key **gone**, not merely that some other suppression produced the same exit code | The source-level regression test `IMP-0346` requires for a hand-authored flow-definition fix. Falsified once during writing: the first draft indexed `Describe_the_failure` off `$script:Compute` (`Compute_statistics`'s own nested actions) instead of `$script:Flow`'s top level, where it actually lives as a sibling — it returned `$null` silently until the assertions caught it, which is exactly the class of self-deceiving green this project's own reporting rules warn about |
| 6 | `python3 -c "json.load(...)"` over the edited flow file, plus a recursive description-length walk | Parses; every `description` ≤ 256 chars (`C-TECH-060`) | Structural well-formedness only (V1) |
| 7 | `python3 scripts/verify-improvement-log.py` then `generate-known-failure-modes.py` | OK (schema), 493 entries → digest regenerated, 585 lines | `IMP-0496` appended cleanly. Its `evidence_grep` was corrected mid-dispatch after the validator itself flagged the needle as already-satisfied (see Findings Logged) |

#### Revision 1.3 hours proposal — addendum for `commercial-agent` behind `APPROVE TIMESHEET`

A proposal, never a booking. `logs/worklog.jsonl` is `commercial-agent`'s alone.

| WBS | Proposed actual | Evidence behind the figure |
|---|---|---|
| `6.9` | **1.1 h** | Ground-truthing `result()` against four Microsoft Learn pages before writing anything; structural analysis of the flow's container nesting; the `Describe_the_failure`/`Describe_the_switch_failure` JSON rewrite (two new `Query` actions, two new nested `If`s, three `SetVariable` leaves); the `_CHECK7_EXCEPTIONS` entry removal and two stale-count corrections in `verify-flow-definition-language.py`; a new 7-test Pester `Describe` block, including diagnosing and fixing its own `$script:Compute`/`$script:Flow` indexing defect and a Pester v6 `return`-in-`It` crash; `IMP-0496` logged, validated (twice, after correcting the needle) and the digest regenerated; this document's §0.14/§10/§11/Findings Logged/Checklist and hours proposal |

**No figure here equals a WBS estimate**, per D-6, and no fee, rate or currency amount appears anywhere in
this revision (`C-COM-004`, D-3). Contracted hours and dates are **cited, never restated** (`C-COM-008`):
`contract/wbs.json` and `contract/service-agreement.json` are the baseline.

## Findings Logged

**Revision 1.3 (`wbs:6.9`, 2026-08-30) — 2 entries:**

| ID | Class | Severity | Lesson in one line |
|---|---|---|---|
| `IMP-0496` | `platform-fact-groundtruthed` | `friction` | Microsoft documents `result()` for `Scope`/`For_each`/`Until` only; four pages read directly neither confirm nor deny a `Switch` or `If` action's own name as a target — a genuine gap, recorded so the next session does not re-run the same four searches, closing behind `A-FLOW-13` |
| `IMP-0498` | `agent-instructions-describe-a-topology-that-changed` | `friction` | This dispatch's own opening instruction said to fan out to `automation-agent` for the flow-definition editing; development-agent did the JSON/script/test edit directly instead, judging the ground-truthing and the construction it justified inseparable. Logged rather than silently done, per `agents/WORKFLOW.md`'s Session Boundaries rule |

**Validator first, then the generator** — `python3 scripts/verify-improvement-log.py` → **OK (schema), 495
entries**; `python3 scripts/generate-known-failure-modes.py` → 495 entries, 494 distinct lessons, 587 lines.
The validator caught the identical mistake on BOTH of this revision's entries at first append: each
`evidence_grep` originally pointed at a needle that was already true for a reason unrelated to the
`proposed_change` — `IMP-0496`'s at *this document's own* `A-FLOW-13` mention (true because I had just
written it, not because `knowledge/technology/power-automate.md` was edited), `IMP-0498`'s at
`logs/routing.log` containing `automation-agent` (true because that log names the sub-agent in hundreds of
unrelated dispatches, not because `agents/development-agent.md` carries the proposed sentence). Both needles
now point at the actual, currently-unedited target of each `proposed_change` — this is the validator doing
its job, not a defect in either finding.

**Revision 1.1 (`wbs:6.9`, 2026-08-28) — 6 entries, plus one a sub-agent logged:**

| ID | Class | Severity | Lesson in one line |
|---|---|---|---|
| `IMP-0472` | `gate-scope-mismatch` | `rework` | A HARD build gate rejected APPROVED ADR-039's mechanism on the first run; an ADR that names one gate has usually checked one gate, and a gate widened for an approved design must be widened by an **anchored template**, never by adding a function name to an allow-list |
| `IMP-0473` | `platform-contract-guessed-not-groundtruthed` | `blocker` | XPath 1.0 `sum()` is `NaN` over a node set containing **any** empty element, `join()` over an empty array is `''`, and a nested `add()` carries one group's `NaN` into a total — so ADR-039's literal expression ships an unparseable document whenever a break type has no costed application |
| `IMP-0474` | `hand-maintained-count-drifts-from-source` | `friction` | An action count in an ADR's cost table is an estimate; ~40 measured 88. *Cite, never restate* holds for a technical figure exactly as for a baseline one |
| `IMP-0475` | `gate-cannot-fail` | `friction` | In Pester, `-BeLike` is wildcard matching and `item()?['rev_x']` carries `[ ]`; use `-Match ([regex]::Escape(…))`. `-BeLike` fails loudly, **`-Not -BeLike` passes vacuously**, so the dangerous half is the absence test |
| `IMP-0476` | `two-invocation-paths-disagree` | `friction` | `IMP-0142`'s trap is a PowerShell **parse** property, not a `Write-Output` property: a `+` continued across a line break inside any cmdlet parameter argument re-parses the statement and a piped subject arrives as `$null`. Marked `contests: IMP-0142` |
| `IMP-0477` | `hard-gate-red-on-pre-existing-debt` | `rework` | A declared `result()`-descent exception's blast radius grew from 20 actions to 104 in one dispatch, and a *fail-loud* claim resting on the alert naming the failing action is weaker than it was. Not fixed here — `IMP-0346` |
| `IMP-0470` | *(logged by `frontend-agent`)* | — | `verify-code-app-column-bindings.py` takes **two** positional arguments; the one-argument form in this dispatch's own instruction exits 2 printing the docstring |

**Validator first, then the generator** — `python3 scripts/verify-improvement-log.py` → **OK (schema), 474
entries**; `python3 scripts/generate-known-failure-modes.py` → 474 entries, 473 distinct lessons, 582 lines.
The validator rejected three of these six on first append (`severity: "minor"` is not in
`blocker|friction|rework`) and they were corrected before anything read them — which is the whole argument
for running the validator rather than the generator, since the generator would have exited 0 over them.

**Revision 1.0 (`wbs:6.9`, 2026-08-28) — 5 entries, one of them a sub-agent's:**

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0460 | `two-recorded-lessons-contradict-each-other` | rework | *(`automation-agent`'s own)* This dispatch's brief cited `if()` lazy-branch evaluation as settled via `IMP-0124`; `IMP-0378` (APPLIED) says the opposite and `IMP-0412` records the question as OPEN — so the date guard was rewritten to be total under either semantics rather than to depend on one |
| IMP-0461 | `gate-reassures-wrongly` | **blocker** | A status-free helper `Compose` is a FRAGMENT, not a non-ok document — `verify-tad-coverage.py` filed all three as non-ok and went blind to the four money nulls the moment they moved out of `Compose_response_body`. Fixed by transitive attribution through `outputs('<name>')`; two residual weaknesses reported, not fixed |
| IMP-0462 | `finding-diagnosis-unverified` | rework | A response METRIC is not a response FIELD — `IMP-0459` proposed deleting UR-002/UR-003 as dead promises on the strength of the top-level keys going non-null, while four sub-fields are still null. Narrowed instead of deleted, per UR-002's own half-closed branch |
| IMP-0463 | `requirement-names-data-the-solution-cannot-supply` | rework | The WDL has **no `sum()` over an array** and `add()` is binary, so TAD §5.1's *"`length(filter(...))` and equivalents"* promised a mechanism that does not exist — after the same design had ruled out FetchXML `aggregate` and a Custom API |
| IMP-0464 | `dispatch-instruction-contradicts-an-approved-document` | rework | Small-cell suppression is out of scope by explicit twice-given reviewer risk-acceptance (NFR-027 withdrawn 2026-08-25); the brief asked for it citing §6.3.4, which argues the opposite. Not implemented |

**Two of these five are the same shape and that is the signal worth keeping:** `IMP-0460` and `IMP-0464` are
both a fact cited in this dispatch's own brief with an authority the cited source does not carry — one a
platform semantic, one a disclosure control. Neither was caught by a gate; both were caught by reading the
cited source before building against it.

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

### This revision (FR-035 structured fields, 2026-08-27)

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0365 | `stale-tool-cache-masquerades-as-real-defect` | friction | A stale `node_modules/.vite` dependency-optimization cache reproduced the exact pre-fix "Cannot find module .../multiSelectPicklistUtils" symptom `vitest.config.ts`'s own `server.deps.inline` setting already fixes; `rm -rf node_modules/.vite` resolved it with no source change needed — capability recorded so a future session does not re-diagnose it as an unfixable upstream package defect |
| IMP-0366 | `stale-deferral-uncaught-across-sessions` | friction | A concurrent session built `rev_ethnicgroup` (resolving SDD OQ-027) without deleting `contract/tad-deferrals.json`'s now-satisfied `TD-005` entry, so `verify-tad-coverage.py` (`C-TECH-066`) failed against an unrelated dispatch's own constraint check; fixed per the file's own `_stale_entries_fail` procedure — a schema-adding session should reconcile a deferral it satisfies in the same change, not leave it for the next gate run to discover |

**2 entries appended — `IMP-0365`, `IMP-0366`.** Neither is a defect in this revision's own code: `IMP-0365`
concerns 7 suites this revision did not touch (a second-attempt-with-changed-input case, `skills/how-to-log-
an-improvement.md` §1 triggers 1 and 6); `IMP-0366` concerns a concurrent session's own unreconciled schema
work, surfaced only because this revision's own `C-TECH-066` constraint check happened to run
`verify-tad-coverage.py` (trigger 2, reality contradicted a document). Digest regenerated: YES —
`python3 scripts/generate-known-failure-modes.py` → 363 entries, 497 lines. `python3
scripts/verify-improvement-log.py` reports 3 pre-existing structural errors on `IMP-0363`/`IMP-0364` — both
`lead-agent` entries from a concurrent session already on this tree before this dispatch started (confirmed:
`logs/improvement-log.jsonl` and this very document were both already `git`-dirty at activation), not
appended or touched by this dispatch, and not this dispatch's to fix.

### This revision (round-statistics second version, 2026-08-27)

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0377 | `approved-document-internally-inconsistent` | **blocker** | The flow's TAD-specified trigger (`shared_logicflows`/PowerApps V1) has twice crashed the Code App's boot (`IMP-0358`/`IMP-0359`/`IMP-0365`); a concurrent, uncommitted session has already moved the app to a Dataverse-row-trigger/write-back design this flow does not implement. Needs a superseding ADR before any session hand-authors the new trigger shape |
| IMP-0378 | `platform-fact-groundtruthed` | friction | `if()` in this expression language evaluates all three arguments eagerly (Microsoft's own docs: "Parameters are evaluated from left to right") — an `if(equals(x,0),0,div(...,x))` guard still divides by zero. Use `max(divisor,1)` instead. Found and fixed before import, by writing a small evaluator for the shipped expression text and running it against a zero-population round |
| IMP-0379 | `approved-document-internally-inconsistent` | friction | TAD §3.4/A-R24 ("rev_ethnicgroup was deliberately never built") is stale against the same document's own §12.1 warning box and against `Entity.xml` — the column was built 2026-08-27 to resolve SDD OQ-027; only its field permission is missing. `ethnicGroupDistribution` stays `null` regardless (out of scope either way), but §3.4/A-R24's wording should be reconciled |

**3 entries appended — `IMP-0377`, `IMP-0378`, `IMP-0379`.** `IMP-0377` is trigger 2 (reality — the Code App's
own source — contradicted the TAD this dispatch was handed) and trigger 5 (a gate this dispatch's own reading
of `roundStatistics.ts` found, that no existing gate catches). `IMP-0378` is trigger 1 (a second attempt —
the first draft's guard — with changed input, the `max()` rewrite) found before any live run, so it is
`friction` rather than `rework`: nothing shipped wrong. `IMP-0379` is trigger 2 again, on a smaller scale.
Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py` → **378 entries, 377 distinct
teaching lessons (1 rejected, excluded), 498 lines**. `python3 scripts/verify-improvement-log.py` reports
**11 pre-existing structural errors, none on `IMP-0377`/`IMP-0378`/`IMP-0379`** (all three pass the schema
check cleanly) — the 11 are malformed `observable_at` values and two duplicate ids (`IMP-0368`/`IMP-0369`,
each `also on line 366/367`) on entries from `IMP-0363` onward, all from concurrent sessions on this same
synced tree (`revitalise-15`/`revitalise-43`, per this dispatch's own handoff), not appended or touched by
this dispatch, and not this dispatch's to fix — continuing exactly the pattern the FR-035 revision above
already recorded for `IMP-0363`/`IMP-0364`.

---

### This revision (TAD Revision 4 — design-system adoption, 2026-08-27)

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0386 | `gate-cannot-fail` family | friction | Under this app's vitest config a CSS-Modules import resolves to a **Proxy that invents a class name for any key**, so `expect(el).toHaveClass(styles.doesNotExist)` passes. A class assertion in a component test cannot see the stylesheet — assert key names as substrings and let the disk-read test assert the rules |
| IMP-0387 | `approved-document-internally-inconsistent` | friction | TAD §2.1.3 prescribes `Record<Variant, string>` for the converted variant maps; that does not compile, because `vite/client.d.ts` types a CSS Module as an index signature and `noUncheckedIndexedAccess` makes every lookup `string \| undefined`. Shipped as `Record<Variant, string \| undefined>` with a filtering join rather than weakening the tsconfig |
| IMP-0388 | `platform-contract-guessed-not-groundtruthed` | friction | TAD §2.1.4's table lists Fluent's `Radio` as replaced while keeping its `RadioGroup`. Measured: `RadioGroup` publishes `name` and the derived `checked` through a React context only Fluent's own `Radio` consumes, so a look-alike child gets `name: null` and `checked: false` on every option and loses single-selection, arrow-key traversal and the roving tabindex |
| IMP-0389 | `hand-maintained-count-drifts-from-source` | friction | Three new files cite this app's layout stylesheet by **line number**, two of them already transposed before this pass and all three moved by it. Cite the class name, not the line |
| IMP-0390 | `gate-cannot-fail` | friction | **A disk-read stylesheet test proves what a file says, never that anything loads it** — so A-R38's own prescribed mitigation could not detect A-R38's own failure. Assert the side-effect import too, and prove it by deleting the import and watching the test fail |
| IMP-0391 | `approved-document-internally-inconsistent` | friction | TAD §8.5 point 4 says both that the chart fill changes and that it stays. Resolve such a contradiction in favour of the specific reasoned sentence over the summarising lead-in, prefer the option that preserves an already-tested value, and report it rather than absorbing it |

**6 entries appended this revision — `IMP-0386` and `IMP-0387` (Package A), `IMP-0388` and `IMP-0389`
(Package B), `IMP-0390` and `IMP-0391` (development-agent).** Digest regenerated: 390 entries.

The two `gate-cannot-fail` entries are the ones worth acting on, and they are the same shape from opposite
ends: `IMP-0386` is a stub permissive enough to satisfy any claim made against it, `IMP-0390` is a guard that
cannot see the condition it was written for. Both were found by **deliberately breaking things and checking
the suite went red**, not by reading the code — eleven mutations in total across this revision, every one
reverted and re-confirmed green. That technique is the only reason either is in this table.

`python3 scripts/verify-improvement-log.py` still reports **11 pre-existing problems** across 390 entries —
duplicate ids and non-ladder `observable_at` values on entries written by other concurrent sessions this
evening (`IMP-0363`, `0364`, `0365`, `0367`, `0368`, `0369`, `0375`). **None of the six entries above is among
them**, each was validated individually, and they are deliberately not fixed here: they belong to other
sessions' work and `logs/known-failure-modes.md` records that repairing another session's log entries is how
duplicate ids got created in the first place.

### This revision (TAD Revision 5 — ADR-038, 2026-08-28)

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0406 | `platform-contract-guessed-not-groundtruthed` | **blocker** | `subscriptionRequest/message` is **not** `{1 Create, 2 Update, 3 Delete}` — measured live, 2 is **Deleted** and 3 is **Modified**; the approved TAD's `2` would have registered a delete trigger on a row nothing deletes |
| IMP-0407 | `platform-state-divergence` | rework | A privilege removed from a role's SOURCE stays live, because `ensure-schema.ps1` grants and revokes nothing — diff role source against the live privilege set for every role a feature touched, not only the one the design document reasoned about |
| IMP-0408 | `platform-state-divergence` | friction | Reconcile a hand-edited live artefact against source MECHANICALLY and in BOTH directions — source was 54 actions ahead while the document said live was ahead |
| IMP-0409 | `platform-fact-groundtruthed` (capability) | friction | `pac solution export` + `pac solution unpack` reads a live flow definition from this Mac, unrefused, no cert; `pac env fetch` truncates `clientdata` to a table column and cannot |
| IMP-0410 | `gate-scope-mismatch` | **blocker** | A gate that globs a directory must exclude what the repository ignores — a Pester fixture at `provisioning/deploymentSettings/acc-settings.json` had a HARD gate red and a 56-test container unrunnable |
| IMP-0411 | `untriaged-tool-warning` | friction | Pester 6.1.0's label false positive affects a **third** file — `EnsureSchema.Tests.ps1`, the one TAD A-R46 names as the pre-flight check; `-RequiredVersion 5.7.1` routes around it |
| IMP-0412 | `finding-diagnosis-unverified` | rework | Two recorded lessons contradict each other on whether `if()` short-circuits; write guarded arithmetic correct under either, and settle it with one live run |
| IMP-0413 | `finding-diagnosis-unverified` | friction | `pac solution check --outputDirectory` writes nothing regardless of path — tested with no spaces; `IMP-0010`/`IMP-0079`'s space-in-path cause is wrong, and re-observing a symptom is not evidence about its cause |
| IMP-0414 | `gate-reassures-wrongly` | rework | Never leave a build config saying a step is EXPECTED to fail — the sentence outlives the condition and teaches the next reader to wave a real regression through |
| IMP-0415 | `finding-diagnosis-unverified` | rework | When a design document says a bug class is structurally inexpressible, mutate the code to write that bug — the claim covered the comparison and not the helper feeding it, and the mutation survived with 41 tests green |
| IMP-0416 | `test-coupled-to-absolute-counts` | friction | A count assertion that enumerates its own subjects detects removals only and is blind to additions — sixth instance of the class and the first that fails by staying **green** |
| IMP-0417 | `platform-fact-groundtruthed` (capability) | friction | `--allow ENTITY=REASON` is the sanctioned way to carry a `READ_SERVICES` registration whose table does not exist yet; hand-authoring `dataSourcesInfo.ts` and deleting the step are both forbidden |

**Two of the twelve correct something this repository already believed, and that is the point of the log
rather than an embarrassment.** `IMP-0413` sets `corrects: IMP-0079` and disproves a cause three separate
entries had recorded as established; `IMP-0412` records that two lessons contradict each other and does not
pretend to settle it. `IMP-0406` is the one to read first: it corrects an **approved** document, and building
that document literally would have produced a feature that reports *"still working"* to every trustee forever
with every source-side gate green.

**Validated, not assumed.** `python3 scripts/verify-improvement-log.py` (bare — the authoritative form) exits
**0** over 414 entries with **no duplicate ids**, and the digest was regenerated afterwards, in that order.
`--check` exits 1 for one reason that has nothing to do with these entries: 43 findings were already unread
against a batch trigger of 10 before this dispatch appended anything. That is a routing obligation for
`improvement-agent`, reported at the gate.

### This revision (the C-TECH-014 coverage unblock, 2026-08-28)

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| `IMP-0434` | `no-assertion-on-shipped-content` (**17th**, joining `IMP-0433`) | **blocker** | When an ADR splits a table and the superseded columns are RETAINED rather than deleted, the old columns stay valid write targets and every stale writer keeps succeeding silently — grep `provisioning/` and the flow definitions for the OLD entity set after any such split, and never trust a `<Description>` saying *"written by nothing"*, because nothing checks it |
| `IMP-0435` | `platform-contract-guessed-not-groundtruthed` (**49th**) | **blocker** | The Dataverse Web API **omits** a null-valued column from a response body — `$select` names what you asked for, not what comes back — and under `Set-StrictMode -Version Latest` reading that absent property is a **terminating** error, not `$null`. Guard with `PSObject.Properties.Name -contains`, and make test fakes **omit** the property, because a `$null`-valued fake passes while the real API throws. Flagged `capability: true` |
| `IMP-0436` | `declared-policy-not-mechanically-enforced` (**20th**) | rework | An aggregate coverage percentage is a **lagging** indicator that cannot name the untested file — it fires only once the gap is big enough to move the total, and then it blocks packaging rather than authoring. Proposes a one-second leading gate: every `provisioning/{common,entra,dataverse}/**/*.ps1` must be named by some file under `src/tests/`. **Verified no such gate exists today** |
| `IMP-0437` | `gate-scope-mismatch` (**9th**, generalising `IMP-0410`) | friction | `IMP-0410`'s class cuts **both** ways: a gitignored file can turn a gate red, and an **untracked** file can turn one quiet. Measured 12 warnings here vs 14 on a clean tree. Before transcribing any gate's warning count into a document, run `git status --porcelain` over the paths it reads |

**Two of the four are `blocker`, which routes to `improvement-agent` immediately rather than waiting for a
batch** — and both are the same underlying shape: a wrong thing that **succeeded**. Neither would have been
found by any gate in this repository, and neither was found by reading the scripts; both surfaced within
minutes of writing the first test that actually executed them.

**On altitude, and why no instance patch is proposed for the two blockers.** `IMP-0434` is the 17th
`no-assertion-on-shipped-content` and lands directly beside `IMP-0433`, the finding this dispatch was sent to
act on. `IMP-0436` and `IMP-0437` therefore both propose **general** mechanisms — a per-file test-presence
gate, and resolving every glob-driven gate's inputs through `git` in a shared `scripts/lib/` helper — rather
than a third and fourth patch aimed at these particular files. Per `skills/how-to-promote-a-finding.md` that
call belongs to `improvement-agent` behind `APPROVE IMPROVEMENTS`, and none of it is applied here.

**Validated, not assumed, and in the required order.** `python3 scripts/verify-improvement-log.py` (bare, the
authoritative form) exits **0** over **434** entries, then
`python3 scripts/generate-known-failure-modes.py` exits **0** and wrote 572 lines / 433 distinct lessons. All
four lessons confirmed present in the digest with their class counts incremented.

**`--check` still exits 1, and the figure earlier revisions of this document quote is now stale — measured, not
carried forward.** It reports **14 unread** of 86 NEW (72 reviewer-deferred), against a batch trigger of 10.
Ten of those fourteen are pre-existing — `IMP-0420`, `IMP-0421`, `IMP-0422`, `IMP-0425`, `IMP-0426`,
`IMP-0428`, `IMP-0429`, `IMP-0430`, `IMP-0432`, `IMP-0433` — so **the trigger was already met before this
dispatch appended anything**, and my four made the queue longer rather than tripping it. The §0.9 text above
saying *"43 unread … now 55"* described a moment before `2026-08-28-improvement-review-6.md` processed the
backlog; it should not be read as current. Unchanged in kind: only `improvement-agent`, behind
`APPROVE IMPROVEMENTS`, clears this, stamping a `deferred_reason` to unblock one's own build is forbidden, and
**a build dispatched before that runs will halt at `improvement-log-check`** (`IMP-0285`).

### This revision (`IMP-0438` — the request seeder's `rev_status` write, 2026-08-28)

| ID | Class | Severity | One-line lesson |
|---|---|---|---|
| `IMP-0447` | `finding-diagnosis-unverified` (**13th**) | rework | Mutation-falsifying a provisioning script leaves the **real** file deliberately broken for the length of a test run, because the Pester harness invokes it by its real path — so a concurrent session's gate can catch a body that will never ship. Re-read the file before logging such an observation, and never set `corrects` or `blocker` on a root cause your own entry calls possibly transient. `corrects: IMP-0446`. Gate-side half: give `verify-superseded-column-writers.py` the `--committed-only` flag and scope line that improvement review 37 change 4 already gave `verify-forms-and-views-reachable.py` — **second instance of "verdict computed from a working tree" in one day** after `IMP-0445` |
| `IMP-0448` | `no-assertion-on-shipped-content` (**19th**) | rework | When an ADR moves columns off a table but **retains** them, sweep the artefacts that describe the **table**, not only the writers and readers of the columns: the entity-level `<Description>`, the global option set's `<Description>`, and the flow's notes all still said the answer lived on `rev_roundstatisticsrequest` three days after ADR-038 — one of them eight lines from an attribute description saying the opposite. And never cite a shipped `<Description>` as saying something without grepping it: TAD §3.9.2 did, and it did not |
| `IMP-0449` | `platform-state-divergence` (**12th**) | friction | Dropping a write from a **create-only** seeder does not clear what it already wrote. DEV's request row keeps `rev_status = 2`; the seeder reports `EXISTS` and re-running changes nothing. Do not read that value as evidence something still writes the column, and do not "fix" it with a live PATCH |
| `IMP-0450` | `output-shape-defeats-the-reader` (**9th**) | friction | `verify-provisioning-step-convergence.py`'s step marker is `# ── <n>. <title> ────` with **box-drawing U+2500**, not the `# -- <n>. ` its own `UNCLASSIFIABLE` message and docstring print. A marker written as the message dictates changes nothing and the gate repeats itself. Copy the shape from a script that already passes. General form: a remediation sentence that ASCII-flattens the exact token it demands is an instruction that cannot be followed |

**Validated in the required order, and the validator is authoritative.** `python3 scripts/allocate-improvement-id.py --append` allocated each id inside its lock (never from `tail -1`, `IMP-0080`); `python3 scripts/verify-improvement-log.py` bare exits **0** over **447** entries; `python3 scripts/generate-known-failure-modes.py` then exits 0 (**447 entries, 446 distinct lessons, 576 lines**) and `--check` reports the digest current. The digest renders **⚠ CORRECTED by `IMP-0447`** against `IMP-0446`'s lesson, which is the correction mechanism working rather than an argument in prose.

**`--check` now exits 0, and that is a change since this dispatch began — measured, not assumed.** A concurrent `improvement-agent` session stamped the backlog while this fix was in progress: the 4 unread `blocker`s (`IMP-0434`, `IMP-0435`, `IMP-0439`, `IMP-0446`) now carry dispositions, and the only unread entries left are my four, all below the batch trigger of 10. **`IMP-0446` is already `APPLIED`** — so `IMP-0447`'s correction is informational rather than a queue obligation, and nothing wrong was built on the transient observation: review 37's change 1 (the gate) is correct and green, and `IMP-0446`'s own `proposed_change` was `type: none`.

### This revision (TAD Revision 7 — ADR-040/041/042, 2026-08-30)

| ID | Class | Severity | One-line lesson |
|---|---|---|---|
| `IMP-0513` | `reusable-font-self-hosting-technique` (new class) | friction | Before recording a NAMED typeface as an unmet external-dependency blocker, check whether it is a published Google Font available via an `@fontsource/<slug>` npm package (SIL OFL 1.1, redistribution-safe) — this closed `A-R53` in minutes rather than waiting on the reviewer, and does not apply to a proprietary face like Aptos, where the reviewer remains the only route. When bundling for this Code App host, embed the result as a literal base64 `data:` URI inside the CSS `@font-face` rule itself, per the `A-BRAND-1` precedent — never a relative `url()` to a second built asset file |

`python3 scripts/allocate-improvement-id.py` allocated `IMP-0513` (not `tail -1`, `IMP-0080`); `python3
scripts/verify-improvement-log.py` → **OK (schema) — 510 entries (108 NEW, 401 APPLIED, 1 REJECTED)**;
`python3 scripts/generate-known-failure-modes.py` → **510 entries, 509 distinct lessons, 594 lines**, digest
current.

## Code Review Checklist
- [x] **TAD Revision 4 implemented in full** — design system adopted as a typed component and token layer
      (ADR-033/034), five contrast corrections shipped and each made mechanical (ADR-037), no Google Fonts
      import and no font file anywhere (ADR-036, asserted), WBS 6.2's screen designed against for the first
      time (§2.2) with all eight of its tested behaviours preserved, and all eight §8.5 preservation points
      held. Two deviations from the approved text, both reported rather than absorbed: Fluent's `Radio` is
      kept (§0.8 decision 4, measured) and `.chartBar`'s fill token is unchanged (§0.8 decision 3).
- [x] **A-R38 closed, and the gate falsified before it was trusted** — `ds-tokens.css` is imported by
      `main.tsx` and `harness.tsx`; `ds-tokens.test.ts` guards both new stylesheets by disk read; and the
      import itself is now asserted, which A-R38's own mitigation did not cover. Eleven mutations, each
      caught, each reverted (§11).
- [x] **The two security-critical rendering controls verified by mutation, not by inspection** — collapsing
      the two redaction tones fails 2 tests, inverting them fails 1, porting the mockup's non-associative
      label markup into `Definitions` fails 2, and dropping the list's `role="alert"` fails 2. The tests that
      pin the exact `released-empty` sentence, that it does not contain the word "withheld", and the
      catalogue's 3 and 8 row counts all pass **unmodified**.
- [x] **No schema, query, `$select`, role, flow or column changed** — `src/domain/` and `src/dataverse/`
      were not opened; `theme.ts`, `theme.test.ts`, `brand.css`, `print.css` and `print.test.ts` were not
      edited; net npm dependency change is zero.
- [ ] **A-DS-1 is OPEN and is the one thing a reviewer should look at rather than read about** — whether the
      two withheld/empty treatments are actually distinguishable on a real screen. The fills differ by
      1.07:1 by design; if that reads as one box, the fix is one CSS rule (§10).
- [x] **D-10 (P1, test-agent's re-test) fixed** — `Respond_error`'s `runAfter` no longer accepts `Skipped`
      on `Alert_on_failure`, matching `REVIntakeWordPressToDataverse`'s `Respond_500_intake_failed` exactly
      (§0.3, §4). Re-verified: JSON parses, `verify-flow-definition-language.py` OK (5 clean), no other
      "Skipped" occurrence remains in the flow's `runAfter` conditions (grepped). A-FLOW-05's one-sided
      framing (the root cause test-agent named for why D-10 was missed, `IMP-0347`) is corrected in §10 —
      the row now states both directions and closes the negative one statically.
- [ ] All FR IDs covered — **improved, still partial**: **FR-035 is now COMPLETE** (revision 0.5, §0.5) — the
      redacted-text trio, the structured care-support pair, applicant-type context and type-of-break all
      render; the only genuinely open half of FR-035 is `OQ-011` (the exceptional-circumstance/
      `rev_unabletofundexplanation` redaction scope), which is a reviewer decision, not a build gap.
      FR-056 (landing shell) and FR-063 (finance figures) built and rendering real data; FR-057/058 partial
      (`applicationsReceived` real, `applicationsPerDay` still `null`). **FR-061 improved this revision**:
      gender/age-range/applicant-type distributions now computed (ethnicity stays `null`, A-R24). **FR-062
      improved this revision**: the two distribution halves (`wellbeingLastYear`,
      `lifeSatisfactionDistribution`) now computed; the three headline proportions stay `null` (OQ-039's
      thresholds unset). FR-059/060 unchanged — still `null`. **None of FR-059–062 will reach a real
      trustee yet regardless of this revision**: the flow itself is not reachable by the Code App (§0.7,
      `IMP-0377`) — still open, worse-understood than before this revision, in the sense that the blocker
      is now named rather than latent.
- [x] No hardcoded secrets
- [x] Security controls from TAD §6 implemented — Secure Outputs is applied to the flow's two row-reading
      actions (unchanged) and the new failure path carries no personal data (§6); not enforced as a repo-wide
      gate for the two pre-existing flows outside this WBS's scope (see §7, `IMP-0320`)
- [x] Every TAD §12 item has an idempotent provisioning script wired into `config/revitalise-grant-automation-pipeline.yml`
- [x] Role assignments via group teams only in Test/Acc/Prd — unchanged by this revision
- [x] No hardcoded environment-specific IDs/URLs
- [x] Every guessed platform contract is in §10 and commented in source — **this document now carries 12
      rows** (`A-FLOW-01..06`, `A-LAND-1..4`, `A-FIN-03`, `A-TR-13`); 10 OPEN, 2 CLOSED (`A-LAND-1`,
      `A-LAND-2`). Re-run this revision: `python3 scripts/verify-assumption-markers.py` →
      **PASS — 15 OPEN row(s) checked, every one carrying its marker in source; 36 row(s) total, 13
      closed, 8 unresolvable, 0 exempt, across 4 document(s)** (the "overall" figures span all four
      documents the script scans, not just this one; `A-FLOW-06`'s own marker is confirmed present at
      `REVPortalRoundStatistics-...json`'s `List_applications_in_round.description` — this is the run,
      not a self-assessed re-read of the table, per this project's own `IMP-0299`/`IMP-0286`/`IMP-0307`
      lesson)
- [x] Ground truth used over guessing everywhere a live environment existed (schema fully V4; the flow's
      packaging and checker pass are V2 — the trigger/Response and failure-path shapes remain §10's
      A-FLOW-01/03/04/05; the new `$expand` mechanism's navigation-property name and nested shape are E1,
      live against DEV — only the connector's own acceptance of the literal `"$expand"` key remains
      unverified, A-FLOW-06; `rev_roundfinance` now has a generated Code App data source (§0.2, A-LAND-1
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
- [x] Unit tests written — code app: **460/460 passing, 24 files, 98.37% stmt/line coverage** (92.91%
      branches, 94.27% functions), re-run this revision (up from 372/372, 21 files, 96.27% before this
      revision; the delta includes this revision's own five new/extended test files plus other concurrent
      work already on this tree that this revision did not touch — see §0.5, §9); provisioning: 874/875/1
      skipped as of the prior revision, not re-run by this revision (scoped to the code app only, per the
      dispatching handoff) — the one failure (`'verify-improvement-log --check' passes against the real
      log`) is expected: this revision's own `IMP-0365` append adds one more unread entry, and two
      pre-existing unrelated entries (`IMP-0363`/`IMP-0364`) already fail the underlying structural check
      (see Findings Logged)
- [x] **This revision (round-statistics second version) touched no Code App source** — only the flow JSON, so
      the Vitest suite above is unaffected by it (unchanged from the prior revision's own run). Verification
      for this revision instead: `pac solution pack` (both package types) exit 0; hosted Solution Checker
      0/0/0/0/0; `verify-flow-definition-language.py` OK (5 clean); `verify-field-length-limits.py` OK (238
      flow descriptions ≤256 chars); `verify-assumption-markers.py` PASS (15 OPEN, all marked);
      `verify-build-config.py` PASS (60 steps, 45 gates); plus a purpose-built expression evaluator (§11) run
      twice against the actual shipped `inputs` text of all 54 new actions, catching one real
      division-by-zero defect before any import (`IMP-0378`).

### Revision 0.9 (TAD Revision 5 — ADR-038)
- [x] **§12.3 step 1 done first, and it changed what was built** — the live DEV definition captured by
      `pac solution export` + `unpack` and diffed mechanically in all three directions, with all ten
      differences accounted for (§0.9.2). Two of the document's own premises turned out wrong: the five
      `Response` actions were **not** hand-edited, and **source was 54 actions ahead of live**, so a
      one-directional reconciliation would have silently reverted five metrics. A-R50's specific fear (a
      silently altered trigger `scope`) did not materialise.
- [x] **The approved TAD's `subscriptionRequest/message: 2` is corrected to `3`, on live measurement**
      (§0.9.1) — 2 is Deleted, 3 is Modified, read from the `stringmap` option set and corroborated in both
      directions on this tenant. **This needs an architect-agent erratum** at TAD §5.1.1, ADR-038 part 1 and
      §12.3 step 2. Building the literal value would have shipped A-R47 verbatim.
- [x] **The write boundary is a table privilege, which is what closes `IMP-0401`** — trustee Read-only on
      the result table, service identity Write-only on it, neither party writing the other's table, and the
      flow never writing the table it triggers on. Column-level write control was considered and is
      unreachable here, for two independently sufficient reasons, both recorded (§3).
- [x] **Two asserted disclosure properties became a HARD build gate** — `flow-reads-no-trigger-body`, with a
      15-case selftest, two on-disk known-bad fixtures, five Pester blocks, and a check-B taint analysis whose
      personal-data seed is **derived from `Entities/*/Entity.xml`** rather than hand-typed. It **fails** on a
      missing, unparseable, trigger-less or Power-Apps-triggered target, and it **discriminates**: red against
      this file's pre-edit state from `git show HEAD:`, green against the shipped state.
- [x] **Two live-proven connector traps handled by copying, not re-deriving** — `runas: 3` (4 registers no
      webhook while reporting Activated) and `item/<column>` flattened on every `UpdateRecord` (the nested
      form writes nothing while succeeding). Verified structurally, and the live confirmation is a named
      pipeline step rather than an assumption.
- [x] **A second stale live privilege found by query, beyond what the ADR names** — `prvReadWorkflow` is
      still bound Global to `REV Trustee` while source no longer declares it. Added to the revoke step by
      name, with its `roleprivilegeid`, and **flagged for the reviewer to ratify** rather than folded in.
      The general revoke mechanism in `ensure-schema.ps1` is untouched, per A-R49.
- [x] **The mutation that mattered was the one that survived** — TAD §5.3.1's claim that an age bound
      *"cannot express"* the null-check trap is true of the comparison and false of the helper feeding it. Two
      test cases added, the mutation killed, the file confirmed byte-identical to its pre-mutation original.
- [x] **Unit tests** — code app **662/662 across 38 files, 98.52% statements/lines** (the *figure* checked,
      not the pass count); `EnsureSchema.Tests.ps1` **45/45**; `DataverseScripts.Tests.ps1` **81/81**;
      `BuildGates.Tests.ps1` **111/112**, the one red being the pre-existing improvement-queue trigger below.
- [x] **C-TECH-014 line coverage back over the bar: 83.1% (1711/2059), gate exit 0** — up from the **75.39%**
      that halted the build. The whole gap was three untested seeders (**0/31, 0/31, 0/99** executed lines),
      now **96.8% / 96.8% / 98.1%**. Full Pester run **941 passed / 1 failed / 1 skipped**, the single red
      being the same pre-existing improvement-queue trigger. **This replaces this row's earlier claim that
      `DataverseScripts.Tests.ps1`'s 56/56 discharged `IMP-0244` for those scripts — it did not**, and the
      pass count going up while the coverage figure went down is exactly what `IMP-0132` says to watch for.
- [x] **Configs preflight** — `verify-build-config.py` PASS (61 steps, **46** gates);
      `verify-pipeline-config.py` PASS (104 steps, 46 executable / 58 manual). One `--allow` added to
      `code-app-data-sources` with an owner and a clearing action, because the table cannot be bound to the
      app before it exists; neither generated file was edited.
- [ ] **NOT DONE, and not doable from here: every live step of §12.3.** Steps 3–9 are all live actions —
      schema, auditing, both seed rows, the import, the designer-only trigger re-registration, the
      observed-effect assertion, the privilege revoke and the app push. **The observed-effect assertion is
      the one that decides whether any of this works**, and `statecode`, a `callbackregistration`'s existence
      or `createdon`, `scope`, `runas` and a **Resubmit** are all inadmissible as evidence for it.
- [ ] **NOT DONE: `improvement-log-check` is red, and it is a routing obligation, not a defect here.** 43
      findings were unread against a batch trigger of 10 before this dispatch appended anything (now 55).
      Only `improvement-agent`, behind `APPROVE IMPROVEMENTS`, can clear it, and stamping a
      `deferred_reason` to unblock one's own build is forbidden. **A build dispatched before that runs will
      halt at that step.**

### Revision 0.11 (`IMP-0438` — the request seeder's `rev_status` write)

- [x] **The write is gone and the gate that found it is green** — [PATCH body](../../provisioning/dataverse/seed-round-statistics-request.ps1#L139) is `rev_name` only; `verify-superseded-column-writers.py` → OK, 0 findings, exit 0.
- [x] **The other two columns were checked, not assumed** — `rev_resultjson` and `rev_computedon` were never written by this script; grepped against `provisioning/` and `src/solutions/` rather than inferred from the finding's wording.
- [x] **The corrected behaviour is asserted** — the regression lock names all four forbidden columns and was falsified by three mutants, including the real defect; file confirmed byte-identical afterwards by `shasum -c`.
- [x] **C-TECH-014 re-confirmed by measurement** — 83.1% line coverage, exit 0, per-file counters unchanged; no new test lines needed, and none added.
- [x] **Every shipped `<Description>` about these three columns is now true of this repository** — including the entity-level and option-set descriptions the dispatch did not name, which is called out in §0.11 as beyond its literal ask.
- [ ] **NOT TRUE OF DEV, and not repairable from here** — the live request row keeps `rev_status = 2` from the pre-fix body; the seeder is create-only. `IMP-0449` records it; no live write proposed.
- [x] **`C-TECH-042` convergence is now recorded for this script** — `# ── 1.` marker plus a `# CONVERGENCE:` declaration naming exactly what survives in DEV; `provisioning-step-convergence` → PASS, 9 create-only steps all declared.
- [x] **`IMP-0446` accounted for** — a `blocker` describing this dispatch's 90-second mutation-test state as shipped output, with `corrects` on `IMP-0438`. It is now `APPLIED`, `IMP-0447` corrects it, and the digest carries the correction marker. Nothing wrong was built on it.
- [ ] **The other two round-statistics seeders are still `UNCLASSIFIABLE`** to `provisioning-step-convergence` — out of this dispatch's scope, named here so the next pass on either file knows the one-line fix.

### Revision 1.1 (TAD Revision 6 — ADR-039, the four money averages and the `k = 5` gate)

**Read §0.12 first.** Two statements in the approved TAD are wrong, both measured, and neither changes a
decision — the reviewer should confirm the corrections rather than discover them.

- [ ] **The `NaN` correction (§0.12.1).** ADR-039's literal expression is `NaN` on an empty subset and the
      `NaN` escapes through the total row's nested `add()`. Confirm the shipped guard, and that pinning it
      into the B1 gate's template (rather than only into a test) is the right level of enforcement.
- [ ] **The gate extension (§0.12.2).** One anchored template, on the argument that an XPath `sum()` returns
      a number and a number cannot carry a row. Confirm that the allow-list route was correctly refused —
      adding `join` would have exempted `join(body('List_applications_in_round'), ',')`.
- [x] **A-FLOW-12 (§0.12.3) — answered.** FR-060's *"average grant amount requested (including exceptional
      funding)"* is the **sum** of `rev_amountrequested` and `rev_additionalamountrequested`, matching what
      shipped — confirmed by the reviewer 2026-08-28 21:22 ([`logs/routing.log:372`](../../logs/routing.log#L372)),
      carried into the §10 register at Revision 1.4.
- [ ] **`k = 5` binds four measures and nothing else.** Every categorical distribution stays unsuppressed;
      the contract test asserts both directions. Confirm this is not read as reviving NFR-027.
- [ ] **A below-threshold row publishes its count and no money figures**, and the screen says so in a
      **threshold-agnostic** sentence because `k` does not travel in the response document. Confirm the
      wording, and whether you want the number itself on screen (that is a contract change, not an app one).
- [ ] **A-R52's second exposure is unchanged.** `k = 5` closes the population-of-one case and does **not**
      bound the two-poll delta. Nothing here presents it as doing more.
- [ ] **The `k` row is seeded in all three environments and is a disclosure control, not a tunable.**
      Unseeded withholds everything — fail-safe, not approved.
- [ ] **`UR-002`/`UR-003` deleted and Appendix A corrected in the same change**, on a gate measured failing
      first, then passing.
- [ ] **Verification is V1.** No import, no designer save, no run. §12.2's live test is what closes
      A-FLOW-11, and its own wording is why: *a populated average alone proves nothing.*
- [ ] **Out of scope, flagged:** the check-7 exception on this flow now hides 84 more actions (§0.12.4).
      Clearing it needs a source-level regression test in the same change and is dated 2026-09-30.

### Revision 1.2 (`IMP-0485`/`IMP-0486`, `wbs:6.9`, 2026-08-29)

- [x] **`IMP-0485` closed** — `rev_roundstatisticsresult` registered as a real Code App data source
      (`pa app add data-source`, live), `client.ts`'s `READ_SERVICES` swapped from the stand-in to the
      generated `Rev_roundstatisticsresultsService`, the stand-in and its test deleted. `A-RESULT-1`,
      `A-FLOW-07` and `A-RES-1` close at E1 (§10). `code-app-data-sources` → OK, 7/7, 0 exemptions (was 6/7
      with one declared allowance) — the `--allow` line on that build step is **removed in this same change**,
      independently confirmed against a concurrent `improvement-agent` finding (`IMP-0487`) that named the
      identical removal as outstanding.
- [x] **`IMP-0486` closed** — the entire design-system conversion (`src/components/ds/`, `ds-tokens.css`,
      `ds.module.css`, `brand.css`, every consuming component) committed for the first time, confirmed
      untracked against `HEAD` before committing. Two CSS defects fixed: `.statTileValue` wraps a long
      currency figure instead of overflowing its tile; the three filter `Select`s are re-sized via Fluent's
      own `select` slot override to match `ds/Input`, diagnosed from the installed package's compiled source
      rather than guessed.
- [x] **New finding, not previously recorded:** the connection id every prior data-source addition in this
      app's history documented (`f31ddadfbe874e50a34054df668e75cf`) no longer exists live — logged as
      `IMP-0489`, no runtime risk (per-signed-in-user resolution, unaffected).
- [x] **Regression tests added for both CSS fixes** — new `ApplicationFilters.test.tsx` (4 tests, component +
      stylesheet-off-disk halves per `IMP-0386`) and one new `ds-tokens.test.ts` block for `.statTileValue`.
- [x] **Full local suite re-verified** — typecheck clean, lint clean, **677/677 tests, 98.53% stmt/line
      coverage**, `vite build` clean.
- [ ] **Not pushed to DEV.** `pac code push` stays `pipeline-agent`'s next step, deliberately held for the
      improvement-log queue (`C-TECH-061`). This dispatch's own gate closes at a clean local build and commit,
      not a deployment — V4 (a real signed-in trustee opening the Round overview screen and the applications
      list) remains the open verification for both fixes.

### Revision 1.3 (`IMP-0349`'s own instance, `IMP-0483`, `wbs:6.9`, 2026-08-30)

- [x] **The reviewer's two offered options (re-declare at 167, or hold the line and go red) were both
      rejected** (improvement review 43 §6) in favour of a third: close the gap for real. This dispatch is
      that third option, not a renewal or a widening of the exception.
- [x] **`REVPortalRoundStatistics`'s `Describe_the_failure` descends `result()` into
      `Switch_on_open_round_count`, then again into `Condition_page_cap`** — the exact clearing action the
      exception recorded against itself. Three `Set_failure_detail*` leaves, one per depth, so
      `Alert_on_failure` always names the true failing action, never a Switch's or an If's own opaque wrapper.
- [x] **Ground-truthed first, not guessed.** Four Microsoft Learn pages read directly; `result()` is
      documented for `Scope`/`For_each`/`Until` only, and neither confirms nor denies a `Switch`/`If` by name.
      Declared as `A-FLOW-13, OPEN` (§10) rather than assumed silently, and logged once for the next session
      (`IMP-0496`) rather than re-discovered the same way twice.
- [x] **The `("REVPortalRoundStatistics", "Compute_statistics")` key is DELETED from
      `verify-flow-definition-language.py`'s `_CHECK7_EXCEPTIONS`**, per the reviewer's explicit instruction —
      not renewed, not widened. Verified live: the gate reports this flow clean **on its own merits**, exit 0,
      before the deletion was even made (the finding disappears once the descent exists) and after (the
      `--selftest` corpus assertions, relabelled "two" from "three", both still pass).
- [x] **Regression test added** — `RoundStatisticsContract.Tests.ps1` gains a 7-test `Describe 'D-15
      regression …'` block (`IMP-0346`'s obligation for a hand-authored flow-definition fix), asserting the
      branch structure, both gating expressions, all three leaf messages, no nested `InitializeVariable`
      (`IMP-0137`), and that the gate itself reports this flow clean with the exception's key gone. Full file:
      **54/54 pass.**
- [x] **The other two flows' check-7 exceptions are untouched** — different scope, `automation-agent`'s to
      close separately. Their stale-count references in this same script (`"three declared exceptions"`,
      `"all three are pre-existing"`) are corrected to two, since only two remain, but the exception records
      themselves are not touched.
- [ ] **Not pushed to DEV; no import, no designer save, no run.** Source/config-only, per this dispatch's own
      instruction. `A-FLOW-13`'s own closing conditions (V2 designer save; V4/V5 a deliberate live failure
      inside `Condition_page_cap`) remain the open verification.
- [x] **Disclosed, not silently done: no `automation-agent` fan-out.** This dispatch's own opening instruction
      named `automation-agent` for the flow-definition editing (`agents/development-agent.md`'s Sub-Agents
      table). The JSON edit, the gate-script edit and the Pester test were all written directly in this
      development-agent session instead — judged inseparable from the Microsoft Learn ground-truthing and the
      structural analysis that had to precede them, not decided lightly. Logged rather than left implicit
      (`IMP-0498`), per `agents/WORKFLOW.md`'s Session Boundaries rule.

### Revision 1.5 (TAD Revision 7 — ADR-040/041/042, `IMP-0510`, `wbs:6.9`, 2026-08-30)

- [x] **Built on the already-committed `IMP-0509` line-height fix, not redone or reverted.** `.statTileValue`
      gains an independent `font-size` clamp; the existing `line-height` rule and comment are untouched, and
      both the code comment and the test suite now say explicitly not to delete one while touching the other.
- [x] **ADR-040's nav bar** — persistent, on every view, `aria-current` on exactly the current tab, the
      "Application detail" tab `aria-disabled` (not `disabled`) with a visible caption until a case is open.
      Named "Screen navigation" specifically to avoid a duplicate accessible landmark name with `LandingPage`'s
      own "Portal sections" nav, which is on screen at the same time on the landing view.
- [x] **ADR-041's grid widens (`160px`→`240px`) and gains a container-query shrink-to-fit clamp**, verified
      to actually respond to a tile's own rendered width in real Chromium (32px at ~900px, 20px at ~260px) —
      not merely declared and assumed to work.
- [x] **ADR-042's Playfair Display is self-hosted with real, licensed files — `A-R53` CLOSED**, not left as an
      external dependency. Sourced from `@fontsource/playfair-display@5.3.0` (SIL OFL 1.1); embedded as base64
      `data:` URIs per the `A-BRAND-1` precedent, never a relative `url()` to a separate asset. `--text-heading`
      untouched (stays navy, per the reviewer's explicit override, recorded in ADR-042).
- [x] **§0.10.1's header padding correction and §0.10.2's subheading**, both scoped exactly as the ADR
      describes — the padding change touches only the header band's top, not the page's bottom; the heading
      renders only in the `"figures"` branch, never `"loading"`/`"diagnostic"`.
- [x] **`A-R54` (container-query support in the host's own WebView2) is honestly reported as NOT closed.**
      Real-Chromium evidence is not evidence about the specific embedded WebView2 build; TAD §12.2's own V4
      step (a live signed-in trustee) is the only thing that closes it, and this dispatch had no route to
      perform it.
- [x] **No new `§10` register row** — both platform-contract questions this revision touches (the font
      licence, container-query support) are TAD-level risks (`A-R53`/`A-R54`), not a hand-authored Dataverse/
      flow shape this dispatch guessed at; `A-R53` closes above on real evidence, `A-R54` stays open where the
      TAD already put it.
- [x] **689/689 tests, 98.52% statement/line coverage against an 80% floor, clean tsc/eslint/`vite build`.**
      Full local gate chain re-run: `verify-code-app-column-bindings.py`, `verify-code-app-composition-root.py`,
      `verify-code-app-data-sources.py`, `verify-assumption-markers.py`, `verify-build-config.py` — all exit 0.
- [x] **Two temporary local files (a static verification harness, a Playwright script), created purely to
      obtain the container-query ground truth, removed — confirmed by `git status` and `find`** (C-TECH-056).
- [x] **1 improvement logged (`IMP-0513`, a reusable capability), validator run before the digest, digest
      regenerated.**
- [ ] **No `automation-agent`/`frontend-agent` fan-out — disclosed, not silent**, per §0.15's own closing
      paragraph: judged inseparable from the font-licence research this pass also had to do.
- [ ] **Not pushed to any environment.** Source-only, per this dispatch's own instruction — build-agent
      packages this next as one combined build alongside the concurrent work already on this feature.

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`
