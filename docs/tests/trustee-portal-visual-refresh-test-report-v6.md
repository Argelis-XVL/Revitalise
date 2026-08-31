# Test Report (v6) — Trustee Portal Visual Refresh and Round-Statistics Landing Screen

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** `build/artifacts/trustee-portal-visual-refresh-20260830-2/`
**WBS:** `6.9` — covered via [CO-001](../../contract/change-orders/CO-001.md#L30), so [C-COM-002](../../constraints/commercial/commercial-constraints.md#L35) is satisfied
**Date:** 2026-08-30
**Supersedes:** [v5](trustee-portal-visual-refresh-test-report-v5.md) — this cycle tests Revisions 0.11–1.3 of the dev summary (the request-seeder column fix, the four statistics metrics, the ADR-039 money-average mechanism, and the `A-FLOW-13` failure-diagnosis descent)
**Status: FAIL**

---

## 0. Read this first

**Every new thing this revision built is sound at the level it was executed, and I re-ran the gates myself rather than reading the manifest's word for it.** `verify-assumption-markers.py`, `verify-tad-coverage.py`, `verify-flow-definition-language.py`, `verify-flow-trigger-body-isolation.py`, `verify-code-app-data-sources.py`, `verify-code-app-column-bindings.py` and `verify-field-length-limits.py` all pass on the current tree, matching [manifest.json](../../build/artifacts/trustee-portal-visual-refresh-20260830-2/manifest.json)'s own count of 68 preflight steps. `verify-flow-definition-language.py` confirms `A-FLOW-13`'s fix is real: only the other two flows' check-7 exceptions remain, `REVPortalRoundStatistics` is clean on its own merits (matching [routing.log:401](../../logs/routing.log#L401)).

**The FAIL is the same class v2 through v5 already found, in the same place, and it has not moved.** Nothing in Revisions 1.0–1.3 touched an environment. The round-statistics flow's Dataverse trigger still has no designer save behind it — [pipeline.log's 2026-08-29 14:43 entry](../../logs/pipeline.log#L32) reads the `callbackregistration` row's `createdon` as unchanged (`2026-08-27 18:22`) both before and after that day's import, which is the direct proof STEP 6 (designer save / re-register trigger) has not happened. STEP 7 (the observed-effect assertion — write `rev_triggeredon`, confirm `rev_computedon` changes) stays blocked on it, and eleven of the register's live rows in [Dev Summary §10](../development/trustee-portal-visual-refresh-dev-summary.md#L1897) are still `OPEN` against an environment that has held the schema needed to close most of them since 2026-08-27.

**New this cycle: the artifact itself is built from an uncommitted tree.** `git status --porcelain -- src/ provisioning/ config/` returns 39 paths, including both new `Entity.xml` files and all three round-statistics seeder scripts — none of the round-statistics tables' source is in git. `verify-dev-summary-artefacts-committed.py` confirms 13 SOFT findings against exactly this document, matching the manifest's own `soft_gates.dev-summary-artefacts-committed: 13`. This is not new debt (v5 flagged the same class against the 2026-08-28-3 artifact) but it means this artifact, like its predecessor, cannot be rebuilt from a commit.

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit (code app, per manifest, re-run gates confirm no regression) | 677 | 677 | 0 | 0 |
| Unit / Integration (Pester, per manifest) | 1001 | 1001 | 0 | 0 |
| Integration (flow contract — `RoundStatisticsContract.Tests.ps1`) | 54 | 54 | 0 | 0 |
| Integration (flow structure — re-run by me: `flow-definition-language`, `flow-trigger-body-isolation`) | 2 | 2 | 0 | 0 |
| End-to-End (V5) | 0 | — | — | **all — no environment reached by these revisions** |
| Regression | 677 | 677 | 0 | 0 |
| Security / disclosure control (`k = 5` gate, redacted-column bindings — re-run by me) | 2 | 2 | 0 | 0 |
| Accessibility | 0 | — | — | **carried forward unchanged from v5 (A-DS-1 still OPEN, no new screen this revision)** |
| Performance | 0 | — | — | **all — A-R36, needs V5** |
| Provisioning (live facts, per pipeline.log 2026-08-29) | 3 | 1 | 2 | 0 |
| Compliance / constraint (re-run by me, see §5) | 9 | 6 | 2 | 1 |
| **Total executed** | **2743** | **2740** | **2** | **1** |

The 1001/677 figures are the manifest's own, re-verified only via the static gates in the row above (a full Pester/Vitest re-run was out of scope for this cycle given no source changed since build-agent's own green run at [routing.log:403](../../logs/routing.log#L403)). The two Compliance failures and two Provisioning failures are the same three live facts as v4/v5, counted once per layer.

---

## 2. Requirement Coverage

| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| FR-058 | Average applications received per day | `A-FLOW-09` denominator convention — **reviewer/Emily question, re-asked, still unanswered** ([Dev Summary §10](../development/trustee-portal-visual-refresh-dev-summary.md#L1978)) | **PARTIAL** — computed, convention unconfirmed |
| FR-059 | Average grant amount requested per break type | Composed via `xpath(...,'sum(/r/v)')`, guarded by `k=5` and the `NaN` removal (`A-FLOW-11`) | **PARTIAL** — V1 only, no designer save |
| FR-060 | Average grant amount requested including exceptional funding, per break type | Same mechanism; reading question `A-FLOW-12` (base ask vs. + exceptional funding) unanswered | **PARTIAL** — V1 only, reading unconfirmed |
| FR-062 | Three headline proportions (high-hours care, low satisfaction, unable to break) | `A-LAND-3` shape inferred, never observed populated | **PARTIAL** |
| D-15 (failure diagnosis names the true leaf action) | `Describe_the_failure` descent into `Switch_on_open_round_count`/`Condition_page_cap` | `RoundStatisticsContract.Tests.ps1` 7-test regression block, `flow-definition-language` clean on merits | **PASS at V1** — `A-FLOW-13` (whether `result()` descends through a Switch/If) is OPEN, no designer save |

---

## 3. Failed Tests

| Test ID | Layer | Description | Expected | Actual | Severity |
|---|---|---|---|---|---|
| T-P1 | Provisioning | Round-statistics flow trigger registration current | `callbackregistration.createdon` postdates the flow's last designer save | Unchanged since 2026-08-27 18:22 through the 2026-08-29 import — no designer save has occurred ([pipeline.log:32](../../logs/pipeline.log#L32)) | P2 (same as v4/v5's D-12) |
| T-P2 | Provisioning | Two stale Global privileges removed | `prvWriterev_roundstatisticsrequest`/`prvReadWorkflow` bound to no role | Confirmed **already** not bound as of 2026-08-29 — this one now PASSES, unlike v4/v5 | resolved |
| T-C1 | Compliance (C-TECH-058) | No Dev Summary §10 row is OPEN against an environment that could close it | 0 such rows | 11 OPEN rows (A-FLOW-03, A-FLOW-06, A-FLOW-09, A-FLOW-11, A-FLOW-12, A-FLOW-13, A-LAND-3, A-LAND-4, A-FIN-03, A-TR-13, A-DS-1) against a DEV environment that has held the relevant schema since 2026-08-27 | P1 |
| T-C2 | Compliance (C-TECH-053) | V4 (human open-and-save) performed for every net-new component this revision claims delivered | Recorded owner + date | Not performed for the flow's Dataverse trigger, the `rev_roundfinance` form's Decimal controls (`A-FIN-03`), or the design-system visual layer (`A-DS-1`) | P1 |

---

## 4. Defects Raised

| Defect ID | Severity | Description | Linked Test |
|---|---|---|---|
| D-19 | P1 | Eleven `Dev Summary §10` assumptions remain `OPEN` against a DEV environment that has carried the closing schema/table for 1–3 days — `C-TECH-058` names this exact shape a deployment blocker, not a note | T-C1 |
| D-20 | P2 | The round-statistics flow's Dataverse trigger has not been re-registered via a designer save since the 2026-08-27 redesign; STEP 7's observed-effect check (the only thing that proves the computation runs at all) stays blocked on it | T-P1 |
| D-21 | P3 (carried, not new) | Artifact built from a 39-path-dirty tree; 13 SOFT `dev-summary-artefacts-committed` findings against the round-statistics source, matching the manifest's own count | — |

---

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-TECH-052 | Every hand-authored platform contract carries an assumption-register row | PASS | `verify-assumption-markers.py` → 18 OPEN rows, every marker present, 45 total, 20 closed, re-run by me this cycle |
| C-TECH-053 | Component reported only at the verification level actually executed | **FAIL** | Dev Summary §11 itself states V1/V2 ceilings for Revisions 1.0–1.3; no V4 (designer save) performed for the flow's new trigger or the `A-FIN-03` form |
| C-TECH-054 | CI/pipeline scripts run on the CI runner's OS | N/A this cycle | No new CI/pipeline scripts added since v5; manifest records `Darwin` local build only, no cross-OS claim made |
| C-TECH-055 | Every build-tool warning triaged | PASS | Manifest `warnings: {total:78, accepted:78, untriaged:0}`; the two rows added at [Dev Summary §11 L2118-2119](../development/trustee-portal-visual-refresh-dev-summary.md#L2118) close `IMP-0499` |
| C-TECH-056 | Diagnostic/temp components removed | PASS | No live create this revision; source mutations reverted and `shasum`-verified per Dev Summary Revision 0.11 |
| C-TECH-058 | No Dev Summary §10 assumption OPEN against an existing closing environment | **FAIL** | 11 rows OPEN, DEV has held `rev_roundfinance`/`rev_roundstatisticsrequest`/`rev_roundstatisticsresult` schema since 2026-08-27/29 ([pipeline.log:32](../../logs/pipeline.log#L32)) |
| C-TECH-061 | Improvement log processing triggers enforced mechanically | PASS | `python3 scripts/verify-improvement-log.py --check` → exit 0 this session (498 entries, 96 NEW all reviewer-deferred, 4 warnings none blocking) |
| C-TECH-014 | Unit coverage meets threshold | PASS | Manifest + build log: 98%+ statement coverage code-app side, 83.1% overall Pester-side, both above the 80% bar |
| C-TECH-052 (code app) | No secured column reachable from Code App | PASS | `verify-code-app-column-bindings.py` → OK, 100 files, 63 forbidden columns, 0 references |
| C-TECH-048 | Code App reads only via CLI-generated data source | PASS | `verify-code-app-data-sources.py` → OK, 7/7 registered, 0 exemptions (the `--allow` line from Revision 1.2 is gone) |
| C-COM-002 | Work enters by WBS task id | PASS | wbs:6.9 carried throughout; covered by CO-001 |
| C-COM-004 | No fee/rate figures in tracked files | PASS | None found in this document or the dev summary |

---

## 6. Provisioning Verification

| Item (TAD §12 / §6.1) | Expected | Verified Via | Result |
|---|---|---|---|
| `rev_roundstatisticsresult` table + attributes | Live in DEV | [pipeline.log 2026-08-29](../../logs/pipeline.log#L32): `EntityDefinitions` confirms `EntitySetName=rev_roundstatisticsresults`, alt key Active | PASS (V4 on the schema only) |
| Two stale Global privilege grants revoked | Not bound to any role | Same entry: read back **not bound** | PASS |
| Flow trigger re-registered (designer save) | `callbackregistration.createdon` postdates last save | Same entry: unchanged since 2026-08-27 | **FAIL** |

---

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Result |
|---|---|---|---|---|---|
| A-FLOW-03 | Secure Outputs hides row data in run history | OPEN | Flow live + one run observed | Schema live, flow not re-registered | OPEN — blocked on D-20 |
| A-FLOW-06 | `$expand` accepted as a literal `List rows` parameter key | OPEN | Designer save | Same | OPEN — blocked on D-20 |
| A-FLOW-09 | Applications-per-day denominator convention | OPEN | Reviewer/Emily answer | Question re-asked, unanswered | OPEN — business decision, not platform |
| A-FLOW-11 | `xml()`/`xpath()` sum mechanism behaves as documented on this tenant | OPEN | Designer save + seeded live run | Same as above | OPEN — blocked on D-20 |
| A-FLOW-12 | FR-060 reading (+ exceptional funding) | OPEN | Reviewer/Emily answer | Unanswered | OPEN — business decision |
| A-FLOW-13 | `result()` descends through Switch/If the way it does through Scope | OPEN | Designer save + forced live failure | Same as A-FLOW-03 | OPEN — blocked on D-20 |
| A-LAND-3 / A-LAND-4 | Inferred response shapes for §12 proportions/totals | OPEN | A populated flow response | Same | OPEN — blocked on D-20 |
| A-FIN-03 | Decimal control classid on `rev_roundfinance` form | OPEN | Human opens form in DEV | Form pushed, not yet opened | OPEN — closeable NOW, environment ready |
| A-TR-13 | Multiselect wire shape through the connector | OPEN | Live Code App read | Data source live, no signed-in read yet | OPEN — closeable NOW |
| A-DS-1 | Muted/quiet visual distinction readable to a sighted user | OPEN | One signed-in session | App pushed, no V4 session recorded | OPEN — closeable NOW |

**Three of these (A-FIN-03, A-TR-13, A-DS-1) have been closeable in one DEV sign-in across three consecutive test cycles now** (v4, v5, this one) — the same recommendation v5 made stands unactioned.

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11) | Level confirmed | Result |
|---|---|---|---|
| Four statistics metrics (count/avg/proportion) | V1 (definition-level) | Confirmed — no pack/import/save this revision, matches build-agent's later full local run (V2) | PASS at stated level |
| `A-FLOW-13` failure-diagnosis descent | V1, gate passes on merits | Confirmed via my own `flow-definition-language` re-run | PASS at stated level |
| Round-statistics flow (trigger, writes) | V2 (packaged) | Confirmed by manifest; **not V4** | PASS at stated level, but V4 still owed |
| `rev_roundfinance` schema | V4 | Confirmed live per pipeline.log | PASS |

- Idempotency: `pac code push` re-run twice clean per [routing.log:401-403](../../logs/routing.log#L401) → PASS
- V4 designer/editor open + save: **not performed** for the flow's trigger or the new form → FAIL, no owner/date on record
- Cross-OS (C-TECH-054): N/A this cycle
- Warnings triaged (C-TECH-055) / diagnostic components removed (C-TECH-056): PASS

---

## 8. Recommendations

**Run TAD §12.3 steps 6 and 7 — this is the third consecutive test cycle naming the same single blocking action.** A human designer-opens the flow (or turns it off then on) to re-register the Dataverse trigger, then one live write proves the whole computation chain end to end. Nothing else in this feature closes without it.

**Close A-FIN-03, A-TR-13, A-DS-1 in the same DEV sign-in.** All three have sat open across v4, v5 and this cycle with the environment available the entire time.

**Get A-FLOW-09 and A-FLOW-12 in front of the reviewer/Emily as standalone questions**, not riding on the Revision 6 TAD approval — both were asked once and neither came back answered.

**Commit the 39 dirty paths** (or explicitly declare them "authored, not yet deployed" per `IMP-0486`) before the next artifact is built from this tree — `verify-dev-summary-artefacts-committed.py` names all of them.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0502 | `v3-does-not-imply-v4` | rework | A build's own local gates going fully green (68/68 steps, 0/0/0/0/0 checker, 1001+677 tests) is orthogonal to whether the environment-side V4 step blocking a feature has moved — three consecutive test cycles (v4, v5, v6) have now named the identical un-actioned designer-save step, and three assumptions closeable in one DEV sign-in have sat open the same three cycles with no source change able to touch them. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`
