# Test Report — Revitalise Grant Automation, ADR-083 retention delete jobs (wbs:0.7), retest v3

**Feature Slug:** revitalise-grant-automation
**Artifact:** none. Source-level change, not packed. Scope: development-agent's fixes in [Dev Summary §12 Revision 2](../../docs/development/revitalise-grant-automation-dev-summary.md#L13320) for D-ADR083-1, -2, -3 and C-TECH-067. Earlier rounds: [v1](revitalise-grant-automation-test-report-20261022-adr083.md), [v2](revitalise-grant-automation-test-report-20261022-adr083-v2.md).
**Date:** 2026-10-22  **Tester:** test-agent, strategic tier  **WBS:** 0.7  **Items:** WI-0142
**DEV access this round:** read-only. The one-off write authority was used up in v2, and no row was written this round.
**Status:** **PARTIAL.** All four items are fixed, and no P1, P2 or P3 defect is open. The fixed script sends exactly the two bodies DEV accepted and ran in v2. DEV accepts its existence query. PARTIAL rather than PASS because the script itself has not yet created a job in any environment. That happens on its first TST/ACC and PRD run.

## Summary

Both P1 defects are fixed and the fix is proven against the platform. In v2, DEV ran the paid-grant and AI Events queries. The fixed script now generates those bodies byte for byte. DEV answers the corrected existence query. The new strict fakes catch every old shape. One behaviour change goes to you: the script now notices a job that has stopped recurring, but no longer a job recurring on the wrong schedule. A read-only test shows the exact check can be restored cheaply.

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped | Evidence |
|---|---|---|---|---|---|
| Unit: the three named suites | 594 | 593 | 0 | 1 | `DataverseScripts` 93/0, `DeploymentSettings` 50/0/1, `ScriptContract` 450/0. The skip is pre-existing |
| Regression: whole `src/tests/provisioning` | 796 | 795 | 0 | 1 | Matches development-agent's 795 |
| Mutation: the old shapes put back into the fixed script | 4 | 4 caught | 0 | | Bare values: 7 tests fail. `recurrencepattern` back in `$select`: 13 fail. `System.String` in place of `System.Int32`: 6 fail. `msdyn_aievent_id` (v1's MUT-7): 1 fails. Script restored byte-identical (sha1 `fa3a81c01af3` before and after) |
| Body equivalence with what DEV accepted | 2 | 2 | 0 | | The `paidGrantApplications` and `aiEvents` QuerySets from the fixed `New-RetentionQuerySet` match v2's accepted bodies once the test-only id guard is removed (key-sorted JSON) |
| Every condition value typed, all six jobs | 6 | 6 | 0 | | Bare-value arrays: 0 in every job. Typed values: 2, 3, 0 (orphan sweep has none), 1, 2, 1 |
| Live, read-only: the fixed existence query, verbatim | 3 | 3 | 0 | | §6 |

## 2. Requirement Coverage

| Requirement | Test case | Result |
|---|---|---|
| [FR-048](../../docs/plans/revitalise-grant-automation-plan.md#L2178) / [NFR-010](../../docs/plans/revitalise-grant-automation-plan.md#L2344): paid-grant applications deleted 6 years after final payment | Body equivalence + v2 §6 run | **PASS.** The body was executed in DEV in v2 (V5, one-off); the script now emits it unchanged |
| ADR-083 item 2: AI Events older than 30 days | Same | **PASS**, same basis. Daily recurrence not run (reviewer D-1) |
| Every retention job created once (C-DOM-003, C-TECH-042) | Existence query read in DEV; Pester EXISTS path | **PASS at V3 (read).** The create path has not run live |

## 3. Failed Tests

None.

## 4. Defects Raised

| Defect ID | Severity | Status |
|---|---|---|
| D-ADR083-2 | P1 | **Closed.** [`New-Int32Value`](../../provisioning/dataverse/ensure-bulk-delete-jobs.ps1#L87) types all eight values |
| D-ADR083-3 | P1 | **Closed.** [Existence `$select`](../../provisioning/dataverse/ensure-bulk-delete-jobs.ps1#L447) names only real columns; DEV accepted it |
| D-ADR083-1 | P4 | **Closed.** [DataverseScripts L955](../../src/tests/provisioning/DataverseScripts.Tests.ps1#L955); MUT-7 is now caught |
| D-ADR083-4 | P4, new | Schedule-drift detection is weaker. A job recurring on the wrong pattern (say yearly instead of monthly) now reports a plain `EXISTS`. Only a job that has stopped recurring is flagged ([L450](../../provisioning/dataverse/ensure-bulk-delete-jobs.ps1#L450)). See decision 1 |

## 5. Constraint & Compliance Verification

The v1 §5 rows stand, except these:

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-DOM-003](../../constraints/domain/domain-constraints.md#L36) | Retention implemented | **PASS at source; live on the first TST/ACC and PRD run** | The bodies are proven in DEV and emitted unchanged |
| [C-TECH-042](../../constraints/technology/technology-constraints.md#L84) | Idempotent provisioning | **PASS** | The existence check (`statecode ne 3`) still finds a live job's pending occurrence. DEV returned exactly one row, state 1, `isrecurring` true, for a platform recurring job. It returned none for a completed one-off. A re-run therefore never creates a duplicate. The drift change (D-ADR083-4) is about reporting, not about duplication |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Report only the level executed | PASS | §7.2 |
| [C-TECH-054](../../constraints/technology/technology-constraints.md#L109) | Runs on the CI runner's OS | NOT VERIFIED | macOS only |
| [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) | No OPEN row closable in an existing environment | PASS | No new register row. The script's first live run belongs to the pipeline, not to DEV (D-1) |
| [C-TECH-067](../../constraints/technology/technology-constraints.md#L137) (SOFT) | Counts not hand-typed | **PASS** (was WARN) | Job counts are derived from the settings files |

## 6. Provisioning Verification: read-only in DEV

2026-10-22, as the provisioning application user `REV-MS-Provisioning`. GET requests only. The path was the script's own format string from [L447](../../provisioning/dataverse/ensure-bulk-delete-jobs.ps1#L447).

| Query (name in the filter) | Expected | Result |
|---|---|---|
| `Delete Plug-in Trace Log Records` (a platform recurring job: positive control) | Accepted; 1 row, recurring | **Accepted.** 1 row, state 1, `isrecurring` true, `nextrun` 2026-10-23 12:43 |
| `ZZSYNTH-ADR083-oneoff-aiEvents-20261022` (v2's completed one-off) | 0 rows: completed history is ignored | **0 rows** |
| A `REV` job name | 0 rows: no REV job in DEV (D-1) | **0 rows** |
| Restoring the exact drift check: `$expand=asyncoperationid($select=recurrencepattern)` on the same row | | **Accepted**, returned `FREQ=DAILY` |

## 7. Platform Contract & Verification-Level Audit

### 7.1 Assumption register

[A-RET-1](../../docs/development/revitalise-grant-automation-dev-summary.md#L13307) and [A-NS-47](../../docs/development/revitalise-grant-automation-dev-summary.md#L13310) were closed in v2 (E1, DEV). The fix emits the measured body, so they stay closed. A-NS-45(c) is accepted by the reviewer. A-NS-46 stays OPEN, PRD only by design. Orphans: none.

### 7.2 Verification levels achieved

| Component | Claimed (Dev Summary §12 Rev 2) | Confirmed | Result |
|---|---|---|---|
| `New-RetentionQuerySet`, all six jobs | V1 | V1, plus E1 equivalence to the bodies DEV executed (V5, one-off) | PASS |
| Existence check | V1 | **V3 (read accepted in DEV)** | PASS |
| Create path, the script end to end | V1 | V1 | **PARTIAL**: first live run is the pipeline's TST/ACC and PRD step |

## What you need to decide

**1. Restore the exact schedule-drift check, or accept the weaker one?**

**Problem** — The fix reports drift only when a job has stopped recurring. A job created on the wrong schedule, for example by hand in the wizard, now reads as a clean `EXISTS`.
**Suggested fix** — (a) development-agent adds `$expand=asyncoperationid($select=recurrencepattern)` to the existence query and compares the pattern again (recommended; DEV accepted this read today); or (b) accept the weaker check as is.
**What happens if you don't** — A hand-made job with the wrong schedule (the A-NS-47 fallback route) goes unflagged, and the retention period can run late without any warning.

---

## 8. Recommendations

1. development-agent: decision 1 (a), if you choose it. P4; it does not block.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

## Findings Logged

None this round.

Verification: 593 targeted and 795 full-suite tests passed, 0 failed; 4 of 4 mutations caught; 2 of 2 bodies match what DEV executed; 4 read-only DEV queries accepted. Not verified: the script creating a job in any environment, recurrence, Linux execution, TST/ACC or PRD state.
