# Test Report — Trustee Portal Visual Refresh (Revision 1.10 — IMP-0581 fix)

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** build/artifacts/trustee-portal-visual-refresh-20260902-5/
**Date:** 2026-09-02
**Status:** PASS
**WBS:** `6.8` (`contract/wbs.json`)

Scope: Revision 1.10 of the Dev Summary ([dev-summary#L3697](../development/trustee-portal-visual-refresh-dev-summary.md#L3697)) — one reviewer post-deploy feedback item (`IMP-0581`): x-axis category-tick labels still touched the plot's bottom edge after Revision 1.9's fix, because the first wrapped line's `dy` reserved a baseline position, not a visible gap. This artifact packages Revision 1.10 on top of the already-DEV-deployed Revision 1.9 (commit `186f7d3`, [pipeline.log:517](../../logs/pipeline.log)); `build/artifacts/trustee-portal-visual-refresh-20260902-3/` and `-4/` are a stuck prior session and a preflight-blocked re-attempt respectively ([build.log:70-71](../../logs/build.log)), left untouched as evidence — `-5/` is the first complete, clean build of this revision.

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit | `npm test -- --run --coverage` (independently re-run this session) | 771 | 0 | 0 |
| Integration | (same suite — Dataverse client, chart data-transform tests included) | 771 | 0 | 0 |
| End-to-End | N/A — no live Code App session this cycle (V4 not reached, correctly not claimed) | — | — | — |
| Regression | `RoundStatisticsCharts.test.tsx`, `charts.test.ts`, `layout.test.ts`, `App.test.tsx`, `ApplicationDetailPage.test.tsx` | 771 | 0 | 0 |
| Security | Secret scan (build manifest, C-TECH-001); no new input surface | PASS | 0 | — |
| Accessibility | WCAG 2.1 AA — no new/changed screen structure this revision (SVG tick geometry only) | PASS | 0 | — |
| Performance | Bundle budget (C-TECH-055) | PASS | 0 | — |
| Provisioning | No new TAD §12 item — SVG-arithmetic-only change | N/A | — | — |
| Compliance | C-DOM-004/010/011/030/031/032 — unaffected, no schema/logging change | PASS | 0 | — |
| **Total** | | **771** | **0** | **0** |

Independently re-run in the foreground this session (not taken from the Dev Summary's own report, per `IMP-0364`):
- `npm run typecheck` (`tsc --noEmit`) — clean
- `npx eslint .` — clean
- `npm test -- --run --coverage` — **771/771 passed, 39/39 files, 98.47% statements/lines, 93.57% branches, 93.77% functions** — matches manifest `test_results.code_app_unit_tests` and [dev-summary#L3719](../development/trustee-portal-visual-refresh-dev-summary.md#L3719) exactly
- `python3 scripts/verify-css-arithmetic.py` — PASS, 5 stylesheets — N/A to this revision's actual change (see §7.1 note below; the fix is SVG `dy`, not a CSS rule, so this gate does not reach it)
- `python3 scripts/verify-assumption-markers.py` — PASS, 17 OPEN of 44 total, unchanged — no new hand-authored platform guess
- `python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml` — PASS, 72 steps/57 gates
- `python3 scripts/verify-improvement-log.py` — OK, 581 entries (139 NEW/439 APPLIED/3 REJECTED)
- Source inspection of [`RoundStatisticsCharts.tsx#L330-338,#L501-502`](../../src/code-apps/trustee-review-portal/src/components/RoundStatisticsCharts.tsx#L330) against the Dev Summary's own description — matches exactly: `AXIS_LABEL_GAP` (16px), `TICK_ASCENT_PX` (`ceil(fontSize * 0.8)`), `FIRST_TICK_LINE_DY = AXIS_LABEL_GAP + TICK_ASCENT_PX`, `CATEGORY_AXIS_HEIGHT` derived from the same term
- `diff -rq` of `code-app/` and `git diff c09804e..186f7d3 -- src/code-apps/` — solution zip (`RevitaliseGrantAutomation*.zip`) content-identical between `-2/` and `-5/`; the code-app JS bundle differs only in Vite's content-hash filename and minifier-internal naming (43-byte size delta), CSS byte-identical, `index.html` differs only in the referenced script filename — no source commit sits between the two builds, confirming both packaged the same uncommitted working tree at different points in the pipeline commit sequence
- `pac solution check` (from artifact) — 0 Critical/High/Medium/Low/Informational

## 2. Requirement Coverage

| Item (reviewer feedback) | Source | Test Case(s) | Result |
|---|---|---|---|
| `IMP-0581` — x-axis tick labels still overlap the plot's bottom edge after Revision 1.9 | [dev-summary#L3699](../development/trustee-portal-visual-refresh-dev-summary.md#L3699) | `AXIS_LABEL_GAP`/`TICK_ASCENT_PX`/`FIRST_TICK_LINE_DY` arithmetic, [source#L330-338](../../src/code-apps/trustee-review-portal/src/components/RoundStatisticsCharts.tsx#L330); pre-existing geometry test at [RoundStatisticsCharts.test.tsx#L594-639](../../src/code-apps/trustee-review-portal/src/components/RoundStatisticsCharts.test.tsx#L594) still passes | PASS, with a coverage gap noted below (not a fail condition — see §7.1) |

## 3. Failed Tests

None.

## 4. Defects Raised

None open. See **Findings Logged** below (`IMP-0584`) for a coverage gap raised against the test suite itself, not against the fix — the arithmetic in source matches the Dev Summary's description exactly and was verified by direct inspection.

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-TECH-001](../../constraints/technology/technology-constraints.md#L34) | No hardcoded secrets | PASS | Build manifest secret-scan clean, 20.72MB scanned ([build.log:72](../../logs/build.log)) |
| [C-TECH-004](../../constraints/technology/technology-constraints.md#L37) | Input validation | N/A this revision | No new input surface |
| [C-TECH-006](../../constraints/technology/technology-constraints.md#L39) | Auth enforced on non-public routes | PASS (unchanged) | No auth-surface change |
| [C-TECH-014](../../constraints/technology/technology-constraints.md#L52) | Unit coverage threshold | PASS | 98.47% against 80% floor, re-run directly this session |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Every hand-authored platform guess registered | PASS | `verify-assumption-markers.py` — 44 total, unchanged; no new §10 row (arithmetic against an already-stated design token, not a new platform guess) |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Verification level reported accurately | PASS | See §7.2 — V2 claimed and confirmed; V3/V4 correctly not claimed |
| [C-TECH-054](../../constraints/technology/technology-constraints.md#L109) | Scripts run on CI runner OS | N/A | No new script introduced |
| [C-TECH-055](../../constraints/technology/technology-constraints.md#L110) | Tool warnings triaged | PASS | Manifest `warnings_detail[]` — 4 warnings, all triaged, each with a Dev Summary citation ([build.log:72](../../logs/build.log)) |
| [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) | OPEN §10 assumption blocks deploy | **STANDING OVERRIDE** (unchanged) | 8 rows re-checked OPEN, none newly closed or contradicted — covered by the reviewer's standing override at [pipeline.log:41](../../logs/pipeline.log) |
| [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) | Environment state a source check cannot express is verified live | **STANDING OVERRIDE** (unchanged, pre-existing) | Round-statistics flow trigger registration staleness, condition unchanged — this revision's solution zip touches no flow/schema surface (SVG-only), so the condition necessarily still applies; not re-diagnosed, same override cited per pipeline.log's own precedent |
| [C-TECH-076](../../constraints/technology/technology-constraints.md#L146) | CSS arithmetic (line-height, column-count) checked mechanically | **N/A to this revision's actual change** | `verify-css-arithmetic.py` PASS, but the fix is SVG `dy`/ascent arithmetic in a `.tsx` component, not a CSS rule — outside this gate's stated scope. See §7.1 and `IMP-0584` |
| [C-DOM-004](../../constraints/domain/domain-constraints.md#L37) | No PII in logs | PASS (unchanged) | No logging surface touched |
| [C-DOM-010](../../constraints/domain/domain-constraints.md#L47) | Audit logging on sensitive entities | PASS (unchanged) | No schema/entity change |
| [C-DOM-011](../../constraints/domain/domain-constraints.md#L48) | Audit log schema | PASS (unchanged) | As above |
| [C-DOM-030/031/032](../../constraints/domain/domain-constraints.md#L92) | Special-category data/column rules | PASS (unchanged) | No scoring-flow or schema change |
| [C-TECH-040/042/045/046/048/051/056/057/059/060/065/066/067/069/070/071/073](../../constraints/technology/technology-constraints.md#L82) | Security-role, provisioning, connector, id-fabrication, diagnostic-component, gate-provability, artefact-isolation and metadata-write rules | PASS (unchanged) | All govern Dataverse schema, security, provisioning or metadata surfaces — none touched; solution zip content-identical to the already-deployed `20260902-1`/`-2` builds |

A HARD constraint failure would be a P1 defect; none is open. The two STANDING OVERRIDE rows are pre-existing, reviewer-accepted conditions unrelated to this revision's one-item change, carried forward rather than re-opened.

## 6. Provisioning Verification

N/A this revision — no new TAD §12 item, no new solution component, no CSS or schema surface touched. `pac solution check` (artifact) confirms 0 findings all severities.

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

No new §10 row this revision (`verify-assumption-markers.py` — 44 total, unchanged from Revision 1.9). The 8 rows under the standing `C-TECH-058` override are re-checked, not re-derived from narrative:

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| A-FLOW-03/06/09/11/13, A-LAND-3/4, A-TR-13 | (unchanged from v10, see [test-report-v10#§7.1](trustee-portal-visual-refresh-test-report-v10.md)) | OPEN (all 8) | Live flow run / designer save / reviewer answer, per row | No — no run this revision (SVG-arithmetic-only) | Re-checked, unchanged | OPEN, covered by override |

**Additional finding, not a §10 row (`IMP-0584`, logged this session):** `C-TECH-076` exists precisely because SVG/CSS arithmetic defects are invisible to jsdom and were previously only ever found by a human on a rendered screen ([constraint text](../../constraints/technology/technology-constraints.md#L146)) — but its stated scope is "an authored CSS declaration," and the actual defect this revision fixes (`IMP-0581`) is SVG tick `dy`/baseline arithmetic in a `.tsx` component, which the gate's own text does not reach. This is the third instance of the identical failure shape in this same file (`IMP-0509`, `IMP-0577`, `IMP-0581`), and the fix itself ships with no vitest assertion naming `AXIS_LABEL_GAP`/`TICK_ASCENT_PX`/`FIRST_TICK_LINE_DY` — the pre-existing "Revision 11 item 5" test at [RoundStatisticsCharts.test.tsx#L594-639](../../src/code-apps/trustee-review-portal/src/components/RoundStatisticsCharts.test.tsx#L594) only asserts internal self-consistency between the tick's own `dy` and `CATEGORY_AXIS_HEIGHT`, a property already true under the pre-fix arithmetic. **Not a FAIL** — verified correct by direct source inspection against the Dev Summary's stated design (§1 above), not claimed above V2, and no HARD constraint's stated scope actually covers this arithmetic today. Logged as `IMP-0584`, proposing to broaden `C-TECH-076` with a check C the same way it was broadened from line-height to auto-fit on 2026-08-31 (`IMP-0526`).

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11 / Revision 1.10 checklist) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| `RoundStatisticsCharts.tsx` (this revision's one change) | V2 — source-level, packaged, not pushed | **V2 confirmed** | Build manifest `status: SUCCESS`, `verification_level: "V2"`; `dist/` in artifact matches source-level build output; no import/push this cycle | PASS |
| `RevitaliseGrantAutomation` solution | Unchanged from already-deployed V3 (`20260902-2`) | **V3, carried, not re-claimed as new** | Solution zip content-identical to `-2/` (`diff -rq` on unzipped trees) | PASS |
| Round-statistics flow trigger registration | Not claimed above V3; V4/V5 explicitly not reached | **Confirmed still stale (pre-existing)** | Content-identical to the build already confirmed stale live ([pipeline.log](../../logs/pipeline.log)) | PASS — accurately reported |

- Idempotency: N/A this dispatch — no pack/import/push performed (source-level only); manifest records `preflight: PASS`.
- V4 designer/editor open + save: **NOT reached this cycle** — no live push occurred. Correctly not claimed.
- Cross-OS (C-TECH-054): N/A — no new script introduced.
- Warnings triaged (C-TECH-055) and diagnostic components removed (C-TECH-056): PASS — 4 `warnings_detail[]` entries all triaged with citations, 0 untriaged.

**PARTIAL is not the correct status.** This artifact is honestly reported at V2 (packaged, not yet pushed) and has not been "accepted by the target" and then left short of V5 — it is a clean, fully-tested source-level build awaiting pipeline-agent's deploy.

## 8. Recommendations

1. Proceed to pipeline-agent for DEV deployment (V2 → V3), then the standing V4 human open-and-save step — this is the step that will actually confirm the visible 16px gap the reviewer asked for, since no mechanical check can see it (`IMP-0584`).
2. `IMP-0584` (broaden `C-TECH-076` with a check C for SVG dy/baseline arithmetic) is worth prioritising ahead of a fourth instance in this file — three defects in the same arithmetic class (`IMP-0509`, `IMP-0577`, `IMP-0581`) have now each been caught only by a human on a rendered screen.
3. `A-FLOW-09` (the `applicationsPerDay` denominator convention) remains unanswered across four revisions now — still worth a direct, single-question follow-up to the reviewer/Emily.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0584 | `no-assertion-on-shipped-content` | friction | SVG/canvas baseline-offset (dy) arithmetic against a stated design-token gap is the same unassertable-in-jsdom class C-TECH-076 was written for; broaden it with a check C rather than trusting a rendered-screen human check a fourth time in this file. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py` (581 entries, 578 distinct lessons).
