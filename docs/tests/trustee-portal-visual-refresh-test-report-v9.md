# Test Report — Trustee Portal Visual Refresh

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** build/artifacts/trustee-portal-visual-refresh-20260902-1/
**WBS:** 6.8 (Process feedback + rework — third round of reviewer post-deploy UI fixes; the
6.9 tag on this feature's earlier revisions is a pre-existing mismatch tracked separately, `IMP-0576`)
**Date:** 2026-09-02
**Status:** FAIL (C-TECH-064, pre-existing, unrelated to this revision, covered by the standing `C-TECH-058` OVERRIDE at `pipeline.log:41` — same shape as Test Report v8)

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit | 39 files | 750 | 0 | 0 |
| Integration | (same suite — dataverse client/repository/queries) | — | — | — |
| End-to-End | 0 (no live push of this artifact this cycle) | — | — | — |
| Regression | `domain/charts.test.ts`, `RoundStatisticsCharts.test.tsx`, `LandingPage.test.tsx` re-run/rebased | included above | 0 | 0 |
| Security | no auth/input-surface change this revision (UI/CSS/domain-transform only) | N/A | — | — |
| Accessibility | WCAG 1.1.1/1.3.1/2.4.1 spot-checks (§7 below) | 4 checked | 0 | 0 |
| Performance | bundle budget (`C-TECH-055`) | 1 | 0 | 0 |
| Provisioning | N/A — no new hand-authored platform artefact this revision | — | — | — |
| Compliance | N/A — no PII/audit-surface change | — | — | — |
| **Total** | | 750+5 gate scripts | 0 | 0 |

All figures **independently re-run by test-agent**, synchronously, in the foreground, against
`src/code-apps/trustee-review-portal` (not taken on build-agent's report alone, per `IMP-0364`):

```
npx tsc --noEmit -p .        → exit 0
npx eslint .                 → exit 0
npx vitest run --coverage    → 39 files passed (39), 750 tests passed (750)
                                98.45% stmts / 93.54% branch / 93.77% funcs — matches Dev Summary §11 exactly
npm run build                → exit 0, dist/assets/index-*.js 1,205,610 B, *.css 77,210 B
diff -rq dist/ vs artifact's code-app/  → IDENTICAL (packaged content matches the fresh build byte-for-byte)
```

## 2. Requirement Coverage — the six reviewer items (Dev Summary Revision 1.8, `wbs:6.8`)

| Item | Requirement | Test Case(s) | Result |
|---|---|---|---|
| 1 | Circumstance-score table always visible | `alwaysShowTable` prop confirmed live on the "Exceptional circumstances" panel — [`RoundStatistics.tsx#L489`](../../src/code-apps/trustee-review-portal/src/components/RoundStatistics.tsx#L489) | PASS — **with a caveat, see §8 D-1** |
| 2/3 | Wellbeing row reduced to two combined charts side-by-side, each with its own accessible table | `WellbeingComparisonTable` confirmed live — [`RoundStatistics.tsx#L251`](../../src/code-apps/trustee-review-portal/src/components/RoundStatistics.tsx#L251), wired at [`#L554`](../../src/code-apps/trustee-review-portal/src/components/RoundStatistics.tsx#L554) | PASS |
| 3 | Level-of-need chart: three vertical bars, one per question, x-axis = answer options | `buildWellbeingComparisonData` pivot re-tested in `domain/charts.test.ts` and `RoundStatisticsCharts.test.tsx` (both in the 750/750 run) | PASS |
| 4 | X-axis data labels across charts (root cause, not patched) | `MIN_CATEGORY_COLUMN_WIDTH` now the single source both `BAR_COLUMN_WIDTH` and `COMPARISON_GROUP_WIDTH` derive from — confirmed live — [`RoundStatisticsCharts.tsx#L398-401,518`](../../src/code-apps/trustee-review-portal/src/components/RoundStatisticsCharts.tsx#L398) | PASS |
| 5 | Subsection title 20px→28px | `.panelHeading` confirmed live at 28px with its pre-existing explicit unitless `line-height` intact — [`app.module.css#L493`](../../src/code-apps/trustee-review-portal/src/styles/app.module.css#L493); `verify-css-arithmetic.py` re-run, PASS | PASS |
| 6 | Applications-overview title position | `<h1>` relocation confirmed live, present in every early-return branch — [`ApplicationsListPage.tsx#L100`](../../src/code-apps/trustee-review-portal/src/pages/ApplicationsListPage.tsx#L100) | PASS |

## 3. Failed Tests

None. 0 failing tests in the independently re-run suite.

## 4. Defects Raised

None new this cycle. See §8 for one open interpretation risk (not a defect) and the carried-forward
pre-existing gap in §7.1.

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-TECH-014 | Coverage threshold (80%) | PASS | 98.45% stmts, re-run independently |
| C-TECH-052 | Every E2/E3/E4 contract has a register row; no orphans | PASS | `verify-assumption-markers.py` — 17 OPEN, all carrying source markers, 44 total; this revision adds no new hand-authored platform artefact so no new row is required |
| C-TECH-053 | Verification level claimed is confirmed; V4 human step recorded | **PARTIAL — see §7.2** | This artifact is V2 (packaged) only; V3/V4/V5 for it are not yet due (no Pipeline run yet) |
| C-TECH-055 | Tool warnings triaged or resolved | PASS | Bundle budget PASS at 1,205,610/77,210 B against the declared 1,241,000/79,500 B budget; the recharts >500kB chunk warning is the same pre-triaged one from build #1 of this revision (Dev Summary §11 row 4-5), unchanged |
| C-TECH-058 | An OPEN §10 assumption blocks deploy into an environment where it could be closed, absent an explicit override | **Standing OVERRIDE applies — see §7.1** | `pipeline.log:41`, re-checked most recently 2026-09-01 23:24 (`pipeline.log` line ~71), unrelated to this UI-only revision |
| C-TECH-064 | Live audit/trigger registration evidence, not a proxy signal | **FAIL, carried forward, covered by standing override** | `callbackregistration` for `rev_roundstatisticsrequest` still `createdon` 2026-08-27 — stale since the 2026-08-31 flow-definition replacement; re-confirmed as still stale at the last DEV deploy (2026-09-01 23:24), which is more recent than this artifact and unrelated to its scope |
| C-TECH-076 | CSS arithmetic — a font-size increase carries an explicit line-height | PASS | `verify-css-arithmetic.py`, re-run — PASS, `.panelHeading`'s `var(--leading-snug)` unaffected by the 20px→28px change |
| C-TECH-061 | Improvement log has no unread blocker sitting without a deferred_reason | PASS | `verify-improvement-log.py --check` — exit 0, 15 unread (all non-blocker), 0 unread blockers |
| C-DOM-004 / C-DOM-010 / C-DOM-011 | Personal-data logging / audit trail on sensitive entities | N/A — not evaluated | No entity, log, or audit-surface change this revision (UI/CSS/domain-transform against data the flow already emits) |

```
CONSTRAINT CHECK
Domain   HARD: 0 / 0 of 0  |  violations: NONE                              |  unevaluable: NONE
Domain   SOFT: 0                                                            |  warnings:   NONE
Tech     HARD: 6 / 7 of 8  |  violations: C-TECH-064 (pre-existing, unrelated, standing OVERRIDE) |  unevaluable: NONE
                                                                              |  deferred-to-pipeline: C-TECH-053 (V3/V4/V5 not yet due — no Pipeline run this cycle)
Tech     SOFT: 0                                                            |  warnings:   NONE
Overall: WARN (HARD violation present but pre-existing and reviewer-overridden per pipeline.log:41 — not this revision's defect)
```

No domain constraint is in scope: this revision touches no entity, log, PII surface, or audit control.

## 6. Provisioning Verification

N/A — this revision hand-authors no new provisioning artefact, security role, group team, or app-sharing
change. `verify-build-config.py` re-confirmed PASS (72 steps, 57 gates) against the shared build config,
unaffected.

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

This revision adds no new §10 row (`verify-assumption-markers.py` PASS, 17 OPEN unchanged, all carrying
source markers). The one row relevant to this artifact's deploy path is not a §10 row at all — it is the
**standing environment fact** every prior test/pipeline cycle on this feature has carried:

| What | Claim | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|
| `REV \| Portal \| Round Statistics` trigger registration | `callbackregistration` for `rev_roundstatisticsrequest` reflects the current flow definition | A human re-opens the flow in the Power Automate designer, turns it off, confirms the registration row disappears, turns it on, confirms a new `createdon` | **Yes — DEV has existed since 2026-08-26 and this specific staleness has been re-confirmed at every deploy since 2026-08-31** | Not re-queried live by this test-agent session (this artifact has not been deployed; the most recent live re-check, 2026-09-01 23:24, post-dates this artifact's own source and found it still stale) | **OPEN, unrelated to this revision, covered by the standing `C-TECH-058` OVERRIDE at `pipeline.log:41`** |

**This is not this revision's defect and this revision cannot close it** — it touches no flow file. It is
restated here, rather than silently carried, because the instruction for this cycle asked explicitly whether
the standing override still applies: it does, on the same terms as Test Report v8 (reviewer's prior
`APPROVED` against that report), and nothing in the environment or in this revision's source has changed
that fact. Per `skills/how-to-apply-constraints.md`'s deferred-to-pipeline rule, re-confirming it live is
pipeline-agent's normal pre-deploy step, not a reason to hold this UI-only artifact at Test.

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Code App build (this artifact) | V2 (source-level, "no pack, no import, no designer save, no live push" — Dev Summary §11 Revision 1.8) | **V2, confirmed** | `diff -rq` of a fresh `npm run build` against the artifact's `code-app/` — byte-identical; `tsc`/`eslint`/`vitest`/coverage all independently re-run, matching Dev Summary figures exactly | PASS |
| Solution package (`RevitaliseGrantAutomation.zip`/`-managed.zip`) | V2 (packaged by build-agent, Solution Checker 0 findings) | Not re-run by test-agent (no source change to the solution this revision; build-agent's own re-run at gate 505 in `routing.log` already confirms 72/57 PASS) | `logs/routing.log:505` | PASS (by build-agent's independently-reported figures, not re-verified a third time — no change to re-verify) |
| DEV deploy of *this* artifact | Not yet claimed — no Pipeline run this cycle | N/A | — | **Not yet due** (deferred-to-pipeline) |

- Idempotency: N/A this cycle — no import performed against this artifact.
- V4 designer/editor open + save: **not yet due** for this artifact (no import yet); the feature's
  pre-existing V4 residual (A-DS-1, and the flow-designer re-save above) predates and is independent of this
  revision.
- Cross-OS (`C-TECH-054`): N/A — no new script this revision.
- Warnings triaged (`C-TECH-055`) and diagnostic components removed (`C-TECH-056`): PASS — the one warning
  (recharts >500kB chunk) is triaged in Dev Summary §11 and unchanged by this revision; no diagnostic
  component was added.

**Result: PARTIAL, not PASS, and not FAIL.** Everything this artifact's own scope can prove at V1/V2 is
proven, independently, by this test-agent session. Nothing beyond V2 is claimed, because nothing beyond V2
has happened to this specific artifact yet — nothing in this revision required it, and asking for it now
would be asking the reviewer to open a screen that has not been deployed (`skills/how-to-apply-constraints.md`).
The one HARD item genuinely FAILing today (`C-TECH-064`) is pre-existing, unrelated to this revision's own
change, and already carries a reviewer override on the same terms as Test Report v8.

## 8. Recommendations

**D-1 — item 1's target is an interpretation, not a confirmed fact (`IMP-0578`, `friction`).** This
dispatch's own instruction named "circumstance-score table" and the implementation applied
`alwaysShowTable` to the "Exceptional circumstances" panel — the only panel in this screen whose name is
close to that phrase. If the reviewer meant a different panel, this is a one-line prop change, not a
rework. Flagged here rather than silently accepted, per the Dev Summary's own note at
[Revision 1.8 checklist item 1](../development/trustee-portal-visual-refresh-dev-summary.md#L3546).

**D-2 — re-confirm the flow-designer re-registration live at the next Pipeline dispatch**, since this test
cycle did not re-query it (this artifact has not been deployed and the last live check already post-dates
this artifact's source). Not a new instruction — the same standing action every prior Deployment Summary on
this feature has already named.

Recommend: **APPROVED to proceed to Pipeline**, on the same standing-override terms as Test Report v8 —
the one HARD failure is pre-existing, unrelated to this revision, and already reviewer-accepted; this
revision's own six items are all independently confirmed against source and all local gates pass clean.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | This test cycle re-confirmed every claim in Dev Summary Revision 1.8 against live source with no disagreement; the pre-existing `C-TECH-064` gap was already known and logged (`IMP-0104`/`IMP-0114`/`IMP-0511`) and no new instance of it was found here |

Digest regenerated: NO — no new entry this cycle, nothing to regenerate.
