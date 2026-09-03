# Test Report — Trustee Portal Visual Refresh (Round-2 Reviewer Feedback Rework)

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** build/artifacts/trustee-portal-visual-refresh-20260902-2/
**Date:** 2026-09-02
**Status:** PASS
**WBS:** `6.8` (`contract/wbs.json`)

Scope: Revision 1.9 of the Dev Summary ([`docs/development/trustee-portal-visual-refresh-dev-summary.md#L3583`](../development/trustee-portal-visual-refresh-dev-summary.md#L3583)) — eight round-2 reviewer feedback items against the round-overview and application-detail screens as they stood at commit `c09804e` (the build already DEV-deployed, [`logs/pipeline.log:69`](../../logs/pipeline.log)). This artifact is UI/CSS/domain-logic only — the packaged solution zip is byte-for-byte content-identical to the already-deployed `trustee-portal-visual-refresh-20260902-1` build (verified by unzip+diff below), so no schema, flow or security surface changed this round.

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit | `npm test -- --run` | 771 | 0 | 0 |
| Integration | (same suite — component/data-layer interaction tests included) | 771 | 0 | 0 |
| End-to-End | N/A — no live Code App session available this cycle (V4 not reached) | — | — | — |
| Regression | `layout.test.ts`, `charts.test.ts`, `RoundStatisticsCharts.test.tsx`, `DistributionChart.test.tsx`, `App.test.tsx`, `ApplicationsListPage.test.tsx` | 771 | 0 | 0 |
| Security | Secret scan (manual grep, C-TECH-001), input validation unaffected (C-TECH-004/006 out of scope — no new input surface) | PASS | 0 | — |
| Accessibility | WCAG 2.1 AA checklist against the 8 changed items (below) | PASS | 0 | — |
| Performance | Bundle budget (C-TECH-055(a)) | PASS | 0 | — |
| Provisioning | No new TAD §12 item this revision (UI-only) | N/A | — | — |
| Compliance | C-DOM-030/031/032/010/011/004 — unaffected, no schema change | PASS | 0 | — |
| **Total** | | **771** | **0** | **0** |

Independently re-run in the foreground this session (not taken from the Dev Summary's own report, per `IMP-0364`):
- `npm run typecheck` (`tsc --noEmit`) — clean
- `npx eslint .` — clean
- `npm test -- --run --coverage` — **771/771 passed, 39/39 files, 98.47% statements/lines, 93.57% branches, 93.77% functions** — matches the Dev Summary's [Revision 1.9 checklist](../development/trustee-portal-visual-refresh-dev-summary.md#L3662) and the build manifest's `test_results.code_app_unit_tests` exactly
- `npm run build` (`vite build`) — clean; `dist/` diffed byte-for-byte identical against `build/artifacts/trustee-portal-visual-refresh-20260902-2/code-app/`
- `python3 scripts/verify-css-arithmetic.py` — PASS (5 stylesheets, check A and B both clean)
- `python3 scripts/verify-assumption-markers.py` — PASS, 17 OPEN rows, all carrying source markers, 44 total — unchanged count, confirming no new hand-authored platform guess this revision
- `python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml` — PASS, 72 steps, 57 gates
- `python3 scripts/verify-code-app-bundle-budget.py src/code-apps/trustee-review-portal` — PASS
- `python3 scripts/verify-improvement-log.py` — OK, 577 entries, 136 NEW/438 APPLIED/3 REJECTED
- `pac solution check` (from artifact) — 0 Critical/High/Medium/Low/Informational

## 2. Requirement Coverage

| Item (reviewer feedback) | Source | Test Case(s) | Result |
|---|---|---|---|
| 1. Round-overview charts overflow/scrollbars | [dev-summary#L3601](../development/trustee-portal-visual-refresh-dev-summary.md#L3601) | `RoundStatisticsCharts.test.tsx` (categoryAxisPlan / CHART_WIDTH_BUDGET), verified in [source#L364](../../src/code-apps/trustee-review-portal/src/components/RoundStatisticsCharts.tsx#L364) | PASS |
| 2. Whitespace above "Applications list" | [dev-summary#L3614](../development/trustee-portal-visual-refresh-dev-summary.md#L3614) | `layout.test.ts` named exception assertion; CSS at [app.module.css#L760](../../src/code-apps/trustee-review-portal/src/styles/app.module.css#L760) | PASS — on a stated interpretation, flagged for reviewer confirmation |
| 3. Stray pink bar under Life Satisfaction table | [dev-summary#L3622](../development/trustee-portal-visual-refresh-dev-summary.md#L3622) | `showOwnChart` guard, [DistributionChart.tsx#L252](../../src/code-apps/trustee-review-portal/src/components/DistributionChart.tsx#L252) | PASS |
| 4. Applicant Type pie legend clipped | [dev-summary#L3630](../development/trustee-portal-visual-refresh-dev-summary.md#L3630) | CSS `.chartLegend` column layout, [app.module.css#L1065](../../src/code-apps/trustee-review-portal/src/styles/app.module.css#L1065) | PASS |
| 5. X-axis labels overlapping plot area | [dev-summary#L3633](../development/trustee-portal-visual-refresh-dev-summary.md#L3633) | `CATEGORY_AXIS_HEIGHT` derivation, regression test in `RoundStatisticsCharts.test.tsx` | PASS |
| 6. Application-detail title position | [dev-summary#L3645](../development/trustee-portal-visual-refresh-dev-summary.md#L3645) | [`ApplicationDetailPage.tsx#L110`](../../src/code-apps/trustee-review-portal/src/pages/ApplicationDetailPage.tsx#L110) — `<h1>` renders first | PASS |
| 7. "Back to the list" button removed | [dev-summary#L3649](../development/trustee-portal-visual-refresh-dev-summary.md#L3649) | [`App.tsx#L307`](../../src/code-apps/trustee-review-portal/src/App.tsx#L307) — `onBack` prop removed entirely; `tsc`/`eslint` confirm no dangling references | PASS — a stated, documented reversal of a prior ADR-recorded decision, not a silent contradiction |
| 8. "Print this case" as sole action-row control | [dev-summary#L3659](../development/trustee-portal-visual-refresh-dev-summary.md#L3659) | [`ApplicationDetailPage.tsx#L115`](../../src/code-apps/trustee-review-portal/src/pages/ApplicationDetailPage.tsx#L115) | PASS |
| Also found, not requested: `IMP-0579` (`CompositionPieChart` missing `.tableScroll`, WCAG 1.4.10) | [dev-summary#L3638](../development/trustee-portal-visual-refresh-dev-summary.md#L3638) | Set-wide regression test | PASS |

## 3. Failed Tests

None.

## 4. Defects Raised

None. Two interpretation calls are carried forward as open items for reviewer confirmation, not defects:
item 2's literal DOM-order mismatch ([dev-summary#L3614](../development/trustee-portal-visual-refresh-dev-summary.md#L3614)), and item 1's "circumstance score" naming ambiguity from the prior round (`IMP-0578`, unaffected by this round's items).

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-TECH-001](../../constraints/technology/technology-constraints.md#L34) | No hardcoded secrets | PASS | `git diff c09804e` over the 9 changed files grepped for secret-shaped strings — only false-positive hits on the word "token" (design-system meaning) |
| [C-TECH-004](../../constraints/technology/technology-constraints.md#L37) | Input validation | N/A this revision | No new input surface — presentation/layout/domain-transform only |
| [C-TECH-006](../../constraints/technology/technology-constraints.md#L39) | Auth enforced on non-public routes | PASS (unchanged) | No auth-surface change; solution zip content-identical to the already-deployed build |
| [C-TECH-014](../../constraints/technology/technology-constraints.md#L52) | Unit coverage threshold | PASS | 98.47% statements/lines against the 80% floor, re-run directly this session |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Every hand-authored platform guess registered | PASS | `verify-assumption-markers.py` — 17 OPEN, 44 total, unchanged; no new hand-authored platform artefact this revision |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Verification level reported accurately | PASS | See §7.2 — V2 claimed and confirmed; V3/V4 correctly not claimed |
| [C-TECH-054](../../constraints/technology/technology-constraints.md#L109) | Scripts run on CI runner OS | N/A | No new script introduced this revision |
| [C-TECH-055](../../constraints/technology/technology-constraints.md#L110) | Tool warnings triaged | PASS | Manifest `warnings_detail[]` — 4 warnings, all triaged (1 resolved, 3 accepted), each with a Dev Summary citation |
| [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) | OPEN §10 assumption blocks deploy | **STANDING OVERRIDE** (unchanged) | 8 rows (`A-FLOW-03/06/09/11/13`, `A-LAND-3/4`, `A-TR-13`) re-checked OPEN, none newly closed or contradicted — covered by the reviewer's standing override at [`logs/pipeline.log:41`](../../logs/pipeline.log). Not re-opened; cited, not re-diagnosed, per this dispatch's own instruction |
| [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) | Environment state a source check cannot express is verified live | **STANDING OVERRIDE** (unchanged, pre-existing) | The round-statistics flow's `callbackregistration` staleness (last confirmed `createdon` 2026-08-27 18:22, [`pipeline.log`](../../logs/pipeline.log) entries through 2026-09-02) is a live-environment condition on the flow, and this revision's solution zip is byte-for-byte content-identical to the already-deployed 20260902-1 build (`diff -rq` on the unzipped trees, no output) — the flow, its trigger and every other solution component are untouched by this UI-only revision, so the condition necessarily still applies. Not re-diagnosed; same C-TECH-058 override cited, per pipeline.log's own precedent on the two prior cycles |
| [C-TECH-076](../../constraints/technology/technology-constraints.md#L146) | CSS arithmetic (line-height, column-count) checked mechanically | PASS | `verify-css-arithmetic.py` clean; `.panelHeading`'s new 28px carries an explicit unitless `line-height`; two new `auto-fit` surfaces (pie/legend layout) reviewed, container-relative |
| [C-DOM-004](../../constraints/domain/domain-constraints.md#L37) | No PII in logs | PASS (unchanged) | No logging surface touched |
| [C-DOM-010](../../constraints/domain/domain-constraints.md#L47) | Audit logging on sensitive entities | PASS (unchanged) | No schema/entity change — solution content-identical to already-deployed build |
| [C-DOM-011](../../constraints/domain/domain-constraints.md#L48) | Audit log schema | PASS (unchanged) | As above |
| [C-DOM-030](../../constraints/domain/domain-constraints.md#L92) | No special-category data in scoring | PASS (unchanged) | No scoring-flow or schema change |
| [C-DOM-031](../../constraints/domain/domain-constraints.md#L93) | Special-category columns `IsSecured` | PASS (unchanged) | No schema change |
| [C-DOM-032](../../constraints/domain/domain-constraints.md#L94) | Special-category columns `IsAuditEnabled` | PASS (unchanged) | No schema change |
| [C-TECH-040/042/045/046/048/051/056/057/059/060/065/066/067/068/069/070/071/073](../../constraints/technology/technology-constraints.md#L82) | Security-role, provisioning, connector, id-fabrication, diagnostic-component, gate-provability, artefact-isolation and metadata-write rules (17 rows) | PASS (unchanged) | All govern Dataverse schema, security, provisioning or metadata surfaces — none touched this revision. Solution zip content-identical to the already-deployed `20260902-1` build (`diff -rq` on unzipped trees, zero output) is the evidence these surfaces did not move |

A HARD constraint failure would be a P1 defect; none is open. The two STANDING OVERRIDE rows are pre-existing, reviewer-accepted conditions unrelated to this revision's changes, carried forward rather than re-opened, per this dispatch's brief.

## 6. Provisioning Verification

N/A this revision — no new TAD §12 item, no new solution component. `pac solution check` (artifact) confirms 0 Critical/High/Medium/Low/Informational; `diff -rq` on the unzipped solution trees confirms zero content drift from the already-deployed `20260902-1` build.

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

No new §10 row this revision (confirmed: `verify-assumption-markers.py` reports 44 total rows, unchanged count from Revision 1.7/1.8). The 8 rows under the standing `C-TECH-058` override are re-checked below rather than re-derived from narrative, per this project's own `IMP-0219` rule:

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| [A-FLOW-03](../development/trustee-portal-visual-refresh-dev-summary.md#L2276) | Secure Outputs hides row data on a hand-authored flow | OPEN | A live flow run, read back as an owner | No — no run this revision (UI-only) | Re-checked, unchanged | OPEN, covered by override |
| [A-FLOW-06](../development/trustee-portal-visual-refresh-dev-summary.md#L2285) | `$expand` accepted as a literal connector key | OPEN | Designer save + real invocation | No | Re-checked, unchanged | OPEN, covered by override |
| [A-FLOW-09](../development/trustee-portal-visual-refresh-dev-summary.md#L2351) | `applicationsPerDay` denominator convention | OPEN — reviewer/Emily, unanswered | One sentence from the reviewer | No | Re-checked, unchanged | OPEN, covered by override |
| [A-FLOW-11](../development/trustee-portal-visual-refresh-dev-summary.md#L2373) | XPath `sum()`/`xml()` wrapper behaviour on this tenant | OPEN | Live run against a seeded round | No | Re-checked, unchanged | OPEN, covered by override |
| [A-FLOW-13](../development/trustee-portal-visual-refresh-dev-summary.md#L2410) | `result()` resolves correctly inside `Switch`/`If` | OPEN | Designer save + a live failing run | No | Re-checked, unchanged | OPEN, covered by override |
| [A-LAND-3](../development/trustee-portal-visual-refresh-dev-summary.md#L2281) | FR-062 proportion shape | OPEN — blocked on OQ-039 | Thresholds answered + a populated flow run | No | Re-checked, unchanged | OPEN, covered by override |
| [A-LAND-4](../development/trustee-portal-visual-refresh-dev-summary.md#L2282) | FR-060 break-type total row shape | OPEN | A populated flow run | No | Re-checked, unchanged | OPEN, covered by override |
| [A-TR-13](../development/trustee-portal-visual-refresh-dev-summary.md#L2284) | `rev_careprovidedtype` wire shape over OData | OPEN | A live Code App read | No | Re-checked, unchanged | OPEN, covered by override |

No orphans found: `verify-assumption-markers.py` PASS confirms every OPEN row's `A-nnn` marker resolves in source.

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11 / Revision 1.9 checklist) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Code App source (charts, DistributionChart, RoundStatistics, ApplicationDetailPage, App.tsx, CSS) | V2 — source-level, packaged, not pushed | **V2 confirmed** | `dist/` byte-identical to artifact `code-app/`; `pac solution check` clean; no import, no push performed this cycle | PASS |
| `RevitaliseGrantAutomation` solution | Unchanged from already-deployed V3 (20260902-1) | **V3, carried, not re-claimed as new** | `diff -rq` on unzipped solution trees — zero difference | PASS |
| Round-statistics flow trigger registration | Not claimed above V3; V4/V5 explicitly not reached | **Confirmed still stale (pre-existing)** | Content-identical to the build already confirmed stale live at [`logs/pipeline.log`](../../logs/pipeline.log) (2026-09-01/09-02 entries) | PASS — accurately reported, not glossed over |

- Idempotency: N/A this dispatch — no pack/import/push performed (source-level only); the artifact's own manifest records `preflight: PASS`.
- V4 designer/editor open + save: **NOT reached this cycle** — no live push occurred. Correctly not claimed.
- Cross-OS (C-TECH-054): N/A — no new script introduced.
- Warnings triaged (C-TECH-055) and diagnostic components removed (C-TECH-056): PASS — manifest's 4 `warnings_detail[]` entries all triaged with citations; no diagnostic component introduced.

**PARTIAL is not the correct status here.** This artifact is honestly reported at V2 (packaged, not yet pushed) — it has not been "accepted by the target" (V3) and then left short of V5, which is what would make PARTIAL the right word. It is a clean, fully-tested source-level build awaiting pipeline-agent's deploy.

## 8. Recommendations

1. Proceed to pipeline-agent for DEV deployment (V2 → V3), then the standing V4 human open-and-save step.
2. Reviewer to confirm or correct the two interpretation calls flagged in the Dev Summary — item 2's DOM-order reading ([dev-summary#L3614](../development/trustee-portal-visual-refresh-dev-summary.md#L3614)) and the carried-forward `IMP-0578` naming ambiguity — before the next feedback round, to avoid a third re-interpretation pass on the same items.
3. `A-FLOW-09` (the `applicationsPerDay` denominator convention) has now gone unanswered across three revisions — worth a direct, single-question follow-up to the reviewer/Emily rather than carrying it forward again.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | Every claim in the Dev Summary and build manifest was independently re-run and matched exactly; no defect, no re-diagnosis, no correction |

Digest regenerated: NO — no entries appended this session.
