# Test Report — Trustee Portal Visual Refresh (v14)

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** `build/artifacts/trustee-portal-visual-refresh-20260920-4/`
**Date:** 2026-09-20
**Status:** PASS (source/V1–V2, gated for pipeline) — new flow mechanism not yet at V2/designer-save, tracked openly, not a violation

---

**Scope of this cycle:** Dev Summary Revisions 1.12–1.17 (`wbs:6.10`, plus `6.3`/`6.4` panel
fixes carried in 1.12) — FR-080 (all-history month-by-month application recompute), FR-081
(trailing-six-month anomaly flag, ADR-050), FR-082 (two new `rev_setting` rows), EF-08/04/05/10/02
(panel rename/reorder/removal, mandatory notes on Reject/Defer), and three reconciliation fixes
(`IMP-0794`→`IMP-0796` generalised settings-key count, `IMP-0799` D-15 descent-depth test repair,
`IMP-0800`→ a documentation-only citation correction). Every figure in §1 below was **independently
re-run by this test-agent session**, not taken from `build-agent`'s or `development-agent`'s
report, per `IMP-0364`.

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit (code app) | `npx vitest run` (`src/code-apps/trustee-review-portal`) | 786 | 0 | 0 |
| Unit (Pester, full suite) | `pwsh -NoProfile -File src/tests/Invoke-Tests.ps1` | 1036 | 0 | 1 |
| Unit (Pester, this cycle's two touched files) | `DeploymentSettings.Tests.ps1` + `RoundStatisticsContract.Tests.ps1` | 103 | 0 | 1 |
| Integration | Covered by the Pester suite above (Dataverse-shape/flow-JSON structural tests) | — | — | — |
| End-to-End | Not reachable — source/packaged only, no environment import yet (see §7.2) | — | — | — |
| Regression | Full local gate chain re-run directly this cycle (below) | 6/6 gates | 0 | 0 |
| Security | No new auth/input surface this scope | N/A | N/A | N/A |
| Accessibility | EF-05's validation reuses Fluent `Field`'s existing accessible-error wiring (WCAG 3.3.1/1.4.1); no new markup pattern to re-check | N/A (see §2) | — | — |
| Performance | Not in scope this cycle | — | — | — |
| Provisioning | `rev_setting` seed rows only, on the existing generic upsert mechanism — see §6 | — | — | — |
| Compliance | No special-category/PII surface touched — `domain-invariants` re-run, unaffected | PASS | 0 | — |
| **Total** | | **1925** | **0** | **2** |

Independently re-run by this test-agent this cycle:

```
npx vitest run (src/code-apps/trustee-review-portal)                → 786/786, 42 files
pwsh Invoke-Tests.ps1 (full suite)                                   → 1036 passed, 0 failed, 1 skipped
pwsh Pester, DeploymentSettings.Tests.ps1 + RoundStatisticsContract.Tests.ps1
                                                                      → 103 passed, 0 failed, 1 skipped
python3 scripts/verify-improvement-log.py                            → OK (schema), 799 entries
python3 scripts/verify-improvement-log.py --check                    → OK (schema+triggers), rc=0, 9 warnings (none new/blocking — see §5)
python3 scripts/verify-field-length-limits.py src/solutions/RevitaliseGrantAutomation
                                                                      → OK, 497 flow descriptions ≤256 chars, 0 settings-row violations
python3 scripts/verify-source-derived-test-counts.py                 → 8 fragile literals of 10 (tier-1 SOFT, unchanged — DeploymentSettings.Tests.ps1 no longer among them)
python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation
                                                                      → OK, 8 flows clean, same 3 pre-existing dated exceptions
python3 scripts/verify-assumption-markers.py                         → PASS, 27 OPEN rows across 7 documents, every one carrying its source marker
python3 scripts/verify-assumption-register.py                        → PASS, 89 rows/29 registers/8 documents, 48 open, none contradicted
python3 scripts/verify-tad-coverage.py                               → OK, 177 columns/13 tables, 8 owned deferrals, 2 pre-existing baselined findings (unrelated to this scope)
python3 scripts/verify-domain-invariants.py src/solutions/RevitaliseGrantAutomation --register constraints/domain/special-category-register.yml --build-config config/revitalise-grant-automation-build.yml
                                                                      → PASS, 21 special-category columns verified, unaffected by this scope
python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml
                                                                      → PASS, 84 steps, 65 gates
python3 scripts/run-source-gates.py config/revitalise-grant-automation-build.yml
                                                                      → OK, 16/16 cheap source gates pass
python3 scripts/verify-coverage-threshold.py build/artifacts/.../test-results/coverage.xml --threshold 80 --exclusions config/coverage-exclusions.json
                                                                      → 1778 of 2187 lines = 81.3% (threshold 80.0%), 27 files counted, 4 excluded with reasons
```

All figures reconcile exactly against the build-agent HANDOFF and the artifact's own
`manifest.json`/`pester-results.xml`/`coverage.xml`/`solution-checker` log — 1037 total Pester in
the artifact's own CI-mode run (vs. 1036 in this session's local run; the one-test delta is the
`auth` step's out-of-context deferral the manifest itself declares, not a discrepancy), Solution
Checker `0 Critical / 0 High / 0 Medium / 0 Low / 0 Informational`, coverage 81.3% ≥ 80%.

## 2. Requirement Coverage

| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| FR-080 (all-history month-by-month recompute, ADR-049) | `historicApplicationsByMonth` construction inside `Apply_to_each_historic_month` | JSON well-formedness, `field-length-limits`, `flow-definition-language` (structural), plus the D-15 failure-diagnosis descent tests confirming the new containers fail loud — [`RoundStatisticsContract.Tests.ps1`](../../src/tests/solutions/RoundStatisticsContract.Tests.ps1#L851-887) | **PASS at V1 (well-formed, structurally sound). NOT V2 (no designer save has occurred — nothing has been imported to any environment) and NOT V4/V5 (no live run).** No Pester test can execute a Power Automate flow's arithmetic — this is the honest boundary `C-TECH-052`/`C-TECH-053` exist to track, not a gap this dispatch introduced (see §7.1) |
| FR-081 (trailing-six-month anomaly flag, ADR-050) | `Trailing1`..`Trailing6` shift, `Compose_trailing_mean`, `Compose_month_anomaly` fail-safe priority order | Same structural gates as FR-080; `anomaly` literal `null` confirmed as the correct fail-safe default per TAD §5.1.3 point 2 while OQ-049 was open, now superseded by ADR-050's threshold | **PASS at V1.** V4/V5 (TAD's own A-R61 row: seed six known months in DEV, hand-compute the trailing mean, assert `anomaly` matches, including a threshold-boundary case) is explicitly **not yet due** — no import has occurred |
| FR-082 (two `rev_setting` rows) | `RoundStatisticsHistoryStartDate` (`2026-02-16`), `RoundStatisticsHistoryPriorApplicationCount` (`0`) in `provisioning/deploymentSettings/dev-scoring-settings.json`, mirrored to test/prd settings files | `verify-field-length-limits.py` (0 settings-row violations), [`DeploymentSettings.Tests.ps1`](../../src/tests/provisioning/DeploymentSettings.Tests.ps1) 40/1 skip/0 failed, confirming `21` keys derived from source, not hand-typed | **PASS.** Seed values match TAD OQ-050's own 2026-02-16 reference date; `0` confirmed as a genuine seeded value, not an unseeded sentinel (row absence is) |
| EF-08/EF-04 (panel rename + reorder to match the delivered Trustee Pack) | Panel heading and render order in `CasePanels.tsx`/`ApplicationDetailPage.tsx` | `ApplicationDetailPage.test.tsx`, `CasePanels.test.tsx` — part of the 786/786 code-app run | PASS |
| EF-05 (notes mandatory on Reject/Defer) | `VerdictForm.tsx` conditional `Field` validation | Six new tests (label text per verdict, blocked-save on empty/whitespace notes for Reject/Defer, saved-with-notes, Approve stays optional) — part of the 786/786 run | PASS |
| EF-10 (Helper/referee panel removed) | `HelperRefereeContactPanel` deleted from `CasePanels.tsx`/`ApplicationDetailPage.tsx`; eight panels not nine | `ApplicationDetailPage.test.tsx` panel-order assertion — part of the 786/786 run | PASS |
| `IMP-0794`/`IMP-0796` — settingRows key count derived from source | `DeploymentSettings.Tests.ps1`'s `$expectedCount` (DEV key count minus `acceptedDevOnly`), replacing a sixth hand-typed literal | Re-run standalone this cycle: 40 passed, 1 pre-existing skip, 0 failed; `verify-source-derived-test-counts.py` — file no longer appears in its fragile-literal output | PASS |
| `IMP-0799` — D-15 regression brought to FR-081's actual descent depth | Two new `It` blocks at the two levels FR-081 added, plus corrected leaf paths in the two that were failing | Re-run standalone this cycle (filtered to the D-15 `Describe`): 9 passed, 0 failed (previously 2 of 9 failing on this dead-dispatch tree) | PASS |
| `IMP-0800`/`IMP-0801` — stale `C-TECH-055` citation figure | Dev Summary §11 row for `@vitest/mocker`/GHSA-82fw-gwwq-j7x9, glob@10.5.0 row's stale clause removed | Documentation-only — no test applies; confirmed by direct read of both rows and the `manifest.json` `warnings_detail[]` entry (matches, IMP-0802 below) | PASS (fix applied and read; `IMP-0800`/`IMP-0801` themselves still need `improvement-agent` to move `status`, not this dispatch's or this cycle's to do) |

## 3. Failed Tests

None.

## 4. Defects Raised

None new. `IMP-0802` (build-agent's own finding, a stale citation count of 14 vs. the correct 17,
in this feature's own `C-TECH-055` triage row for the `pack-managed`/`pack-unmanaged` warning) is
already recorded in the artifact `manifest.json`, already marked `accepted`/non-blocking, and is
not re-raised here — see §5.

## 5. Constraint & Compliance Verification

See the `CONSTRAINT CHECK` block below. No HARD violation and no HARD `UNEVALUABLE` row found in
test-agent's scope. Two HARD rows resolve to `deferred-to-pipeline`, not `PASS` or `VIOLATION`,
per `skills/how-to-apply-constraints.md`'s "could the evidence exist yet?" test:

- **`C-TECH-058`** (an OPEN Dev Summary §10 assumption blocks deployment into an environment where
  it could close) — `A-FLOW-15` and the two new `A-FLOW-13` call sites are genuinely OPEN, and no
  environment where they could close exists yet (this flow has never been imported). Deferred to
  `pipeline-agent`'s Stage 0.5 gate, which lists every OPEN row before the DEV deploy this cycle
  is headed for.
- **`C-TECH-064`** (environment state solution source cannot express is verified live) — nothing
  is live yet to verify; the check is due after import, not before it.

`IMP-0800`'s own queue entry carries a live `verify-improvement-log.py --check` warning — corrected
by `IMP-0801` but not yet processed by an improvement review, so it "still counts toward
`C-TECH-061`'s blocker and batch triggers" per the script's own text. This is **not** a violation
this cycle (`--check` exits 0, the entries in question are `friction`/`rework`, not `blocker`, and
neither is unread-and-unrelated the way `IMP-0787`/`IMP-0791` were in Revisions 1.13–1.16) — it is
a live risk to the **next** build's `improvement-log-check` step, flagged in §8 for the reviewer
and `improvement-agent`, not held against this gate.

**Improvement-log queue state, checked live rather than carried from the Dev Summary's own
narrative (`IMP-0219`'s discipline):** the two pre-existing `blocker`-severity entries Revisions
1.13–1.16 reported as unread (`IMP-0787`, `IMP-0791`) are **no longer blocking** —
`IMP-0787` is `APPLIED`, and `IMP-0791` now carries a recorded `deferred_reason` and sits among the
176 reviewer-deferred entries `--check` accepts. `IMP-0794` is `APPLIED` (closed by `IMP-0796`,
Revision 1.15). This is a **real improvement in queue state since Revision 1.16's own report**, not
this test-agent's own work — confirmed by direct read of `logs/improvement-log.jsonl`, not assumed
from the Dev Summary's stale "FAILED" language in Revisions 1.14–1.16, which describe the state at
the time those revisions ran and are now superseded by later `improvement-agent` processing.

## 6. Provisioning Verification

| Item (TAD §12 / §6.1) | Expected | Verified Via | Result |
|---|---|---|---|
| `RoundStatisticsHistoryStartDate` / `RoundStatisticsHistoryPriorApplicationCount` seed rows | Present in `dev-scoring-settings.json`, mirrored (unpushed) to test/prd, on the existing generic `seed-settings.ps1` upsert — no new provisioning script or `CONVERGENCE:` declaration needed | `verify-field-length-limits.py` (0 settings-row violations); direct read of `dev-scoring-settings.json`/`test-settings.json`/`prd-settings.json` confirming both keys present with matching values; `DeploymentSettings.Tests.ps1` 40/1/0 | PASS — V1 (source), not yet V3 (no import) |
| No new `CONVERGENCE:`-bearing create step | FR-082 reuses the settings-array upsert every prior `rev_setting` addition (e.g. `RoundStatisticsStaleAfterSeconds`, `EscalationDays`) already used | Grepped: no new numbered step added to any `provisioning/**/*.ps1` this scope | PASS |
| Live DEV seeding of the two new settings, several months in the past, to close `A-FLOW-15`/`A-R61` | Not yet performed — this is the DEV deploy's own purpose | N/A this cycle | **OPEN, deferred to pipeline-agent's V4/V5 work — see §8** |

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| `A-FLOW-15` (Dev Summary §10) | `range()` with a run-time count, `addToTime()` over a `Date`-only value, and bare-component `formatDateTime()` all behave as documented | OPEN | (1) V2 designer save, (2) V4/V5 live run seeded several months in the past | No — flow never imported | Source marker present at all 6 declared call sites (`verify-assumption-markers.py`) | OPEN, correctly recorded, not yet closeable |
| `A-FLOW-13` (TAD §5.1.3/§12.2, two new call sites this scope) | `result()` on the two new nested containers behaves per platform docs | OPEN | Same ladder as `A-FLOW-15` | No | Marker present at both new call sites; D-15 tests confirm the *structural* descent (not the platform-contract question) | OPEN, correctly recorded |
| `A-R61` (TAD, ADR-050) | `Trailing1`..`Trailing6` left-shift order is correct across iterations | Not yet in Dev Summary §10 (TAD-only row) | V4/V5, must be **provoked**: 6+ known months seeded, hand-computed trailing mean compared, including a threshold-boundary case | No | TAD row read directly; no source marker required since this is author-composed logic, not a platform guess (TAD's own distinction) | OPEN, correctly recorded |

**One id-collision finding carried, not re-litigated.** `A-FLOW-15`/`A-FLOW-13`'s naming
mismatch between the Dev Summary register and the TAD's own §5.1.3/§12.2/A-R60 prose (`IMP-0792`,
already logged by `development-agent`, `friction` severity) is unchanged this cycle and does not
block — the register itself has one row per claim, correctly, under the corrected id.

**No orphan hand-authored artefact found** (`C-TECH-052`) — `verify-assumption-markers.py` confirms
every OPEN row across all 7 documents carries its source marker, and reports zero source markers
with no register row.

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11 / manifest) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Whole build artifact | V2 — packaged; layout accepted by the packer, content unverified | **Confirmed V2** | `manifest.json`: `constraint_check: PASS`, `preflight: PASS — 84 steps, 65 gates`, `status: SUCCESS`, Solution Checker `0/0/0/0/0` | PASS at claimed level |
| FR-080/FR-081's `Apply_to_each_historic_month` mechanism (`A-FLOW-15`, `A-FLOW-13`, `A-R61`) | Not claimed above V1 by Dev Summary §11 — "not pushed to any environment" stated explicitly in every one of Revisions 1.13–1.17 | **Confirmed at exactly V1** — well-formed, structurally gated (`flow-definition-language`, `field-length-limits`), no overclaim found | Direct read of Revisions 1.13/1.14's own Verification checklists; `run-source-gates.py` 16/16 | PASS — claim matches confirmed level exactly |
| `DeploymentSettings.Tests.ps1` / `RoundStatisticsContract.Tests.ps1` fixes | V1 (test-file-only, re-run and passing) | **Confirmed** | Standalone Pester run this cycle, 103/1 skip/0 failed | PASS |
| `provisioning/dataverse/verify-solution-components.ps1` (carried, unchanged since v13) | V2 — behavioural, against a fixture | Not re-run this cycle — unaffected by any Revision 1.12–1.17 change | v13's own re-run stands | Unchanged, carried forward |

- **Idempotency:** N/A this cycle — no new provisioning create-only step (§6).
- **V4 designer/editor open + save:** not performed — nothing in this scope has been imported to
  any environment. This is the reviewer's own stated intent (DEV-only deployment **after** this
  gate), not an omission.
- **Cross-OS (C-TECH-054):** the new/edited Pester files were authored and re-run on macOS by both
  `development-agent` and this test-agent session; no OS-specific API (`Cert:` PSDrive,
  `Get-CimInstance`, `\`-separator) was introduced this scope — grepped clean. CI-runner-OS
  execution remains a pipeline-stage concern, unchanged from every prior cycle's finding on this
  feature → **N/A this cycle, carried forward for pipeline-agent/CI**.
- **Warnings triaged (C-TECH-055):** manifest shows 8 total, 1 resolved, 7 accepted, **0
  untriaged** → PASS. One accepted row (`pack-managed`/`pack-unmanaged`) carries a stale figure of
  its own (14 vs. 17, `IMP-0802`) — the row is still triaged (a count within an accepted rationale
  can be stale without the rationale itself becoming wrong), not untriaged; already logged, not
  re-logged here.
- **Diagnostic components removed (C-TECH-056):** none created this scope → PASS, N/A.

**Per `skills/how-to-apply-constraints.md`'s "could the evidence exist yet?" test:** V2 designer
save and V4/V5 for the new flow mechanism genuinely are not yet due — nothing in `wbs:6.10`'s scope
has been imported anywhere. Recorded as `deferred-to-pipeline`, not a violation, exactly as §5
states for `C-TECH-058`/`C-TECH-064`. This is the correct place for the boundary the HANDOFF asked
this test-agent to state explicitly: **everything in §1–§7 is reachable at V1–V2 without a live
environment; V3 (accepted by DEV), V4 (designer open+save) and V5 (a real trustee/live run reading
`historicApplicationsByMonth` against a hand-count) are `pipeline-agent`'s and the reviewer's next
step, not a gap in this test cycle.**

## 8. Recommendations

1. **The DEV deploy this cycle is headed for is also the only thing that can close `A-FLOW-15`,
   the two new `A-FLOW-13` call sites and `A-R61`.** `pipeline-agent`'s Stage 0.5 gate should list
   all three explicitly (`C-TECH-058`), and the live check TAD §12.2/A-R61 itself specifies should
   be **provoked, not waited for**: seed `RoundStatisticsHistoryStartDate` several months in the
   past in DEV, seed six-plus consecutive months of known, distinct application counts, then read
   `historicApplicationsByMonth.months` and hand-verify the month span, boundary keys, and (for
   `A-R61`) the trailing-six-month `anomaly` value at a threshold-boundary month.
2. **`IMP-0800`'s queue entry is a live risk to the next build, not this one.** `--check` reports
   it uncorrected-in-review, and its own text states the next build reaching `unit-tests` fails on
   it under `C-TECH-061`'s blocker/batch trigger. This gate does not fail on it (rc=0, `friction`
   severity, this build already completed), but an improvement review should process `IMP-0800`
   (and `IMP-0794`'s sibling housekeeping is already done) before the *next* dispatch reaches that
   step — flagged for the reviewer, not `test-agent`'s to action.
3. **`npm run test:visual` is still not wired into either build or pipeline config** — unchanged
   from v13's finding 2, restated because it remains true and this cycle added no code-app/CSS
   surface that would have prompted re-checking it, not because it is new.
4. **CO-005's own two remaining halves (FR-081's DEV verification, and the admin-facing surface
   for the two new settings, if any is planned) are unaffected by this cycle** — this dispatch
   built the mechanism CO-005 asked for; nothing here changes that scope.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | This cycle independently re-ran every figure claimed by `build-agent`/`development-agent` (no drift found), confirmed the improvement-log queue's real state directly from the log rather than from the Dev Summary's own now-superseded narrative, and found no new instance of any defect class. No capture trigger from `skills/how-to-log-an-improvement.md` applies. |

Digest regenerated: **NO** (no new entry this cycle; `logs/known-failure-modes.md` already
reflects the log state as of its own last generation, and nothing here changes it).

---

CONSTRAINT CHECK
Domain   HARD: 6 / 6 of 6   |  violations: NONE
                            |  unevaluable: NONE
Domain   SOFT: 0 in scope   |  warnings:   NONE
Tech     HARD: 28 / 28 of 28  |  violations: NONE
                            |  unevaluable: NONE
                            |  deferred-to-pipeline: C-TECH-058, C-TECH-064 (evidence available after DEV import — see §5/§7.2)
Tech     SOFT: 1 in scope   |  warnings:   NONE (C-TECH-067 — generalised this cycle, IMP-0794/IMP-0796)
Overall: PASS

---

TEST REVIEW REQUIRED — docs/tests/trustee-portal-visual-refresh-test-report-v14.md  |  Result: PASS
Respond APPROVED to proceed to Pipeline, REQUEST RETEST to re-run, or give feedback for dev fixes.
