# Test Report — Revitalise Grant Automation, ADR-083 retention delete jobs (wbs:0.7), retest v4

**Feature Slug:** revitalise-grant-automation
**Artifact:** none. Source-level change, not packed. Scope: D-ADR083-4, exact recurrence-drift detection restored after the reviewer chose option (a) on v3. Earlier rounds: [v1](revitalise-grant-automation-test-report-20261022-adr083.md), [v2](revitalise-grant-automation-test-report-20261022-adr083-v2.md), [v3](revitalise-grant-automation-test-report-20261022-adr083-v3.md).
**Date:** 2026-10-22  **Tester:** test-agent, strategic tier  **WBS:** 0.7  **Items:** WI-0142
**DEV access this round:** read-only. No write was made.
**Status:** **PARTIAL, APPROVED for Pipeline by the reviewer 2026-10-22 (*"approved."*).** D-ADR083-4 is fixed, and no P1, P2 or P3 defect is open. Every branch of the new drift logic is pinned by a test. DEV accepts the script's own existence query. The result stays PARTIAL for v3's reason: the script has not yet created a job anywhere. One new P4 note goes to you (decision 1).

## Summary

The exact drift check is back and correct. The script's own query, run against DEV, returns the recurrence pattern of each live recurring job. Each of seven mutations of the new logic made at least one test fail. One unknown remains, and only the first TST/ACC run can settle it: whether the platform stores our pattern exactly as sent. DEV holds the same daily schedule in two spellings, with and without a trailing `;`. If ours is stored differently, the script warns about drift on every run. It never creates a duplicate.

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped | Evidence |
|---|---|---|---|---|---|
| Unit: the three named suites | 597 | 596 | 0 | 1 | `DataverseScripts` 96/0, `DeploymentSettings` 50/0/1, `ScriptContract` 450/0 |
| Regression: whole `src/tests/provisioning` | 799 | 798 | 0 | 1 | Matches development-agent's 798 |
| Mutation check on the new drift logic | 7 | 7 caught | 0 | | §3. Script restored byte-identical (sha1 `84039d1ee697` before and after) |
| Live, read-only: the existence query taken verbatim from source | 4 | 4 | 0 | | §6 |

## 2. Requirement Coverage

| Requirement | Test case | Result |
|---|---|---|
| Reviewer option (a) on v3 decision 1: a job on the wrong schedule is reported | M1, M2, M4 + DEV read | **PASS at V1 + V3 (read)** |
| Idempotency (C-TECH-042): no duplicate job on re-run | M7 + DEV read (completed one-off returns 0 rows; live recurring job returns 1) | **PASS** |
| FR-048, NFR-010, ADR-083 items 1 and 2 | Unchanged since v3 (bodies equal to those DEV ran in v2) | **PASS**, as v3 |

## 3. Mutation results

| # | Mutation | Tests failing |
|---|---|---|
| M1 | Pattern-drift branch disabled | 1 |
| M2 | Pattern comparison inverted | 2 |
| M3 | `$expand=asyncoperationid(...)` removed | 1 |
| M4 | Live pattern ignored (settings value compared with itself) | 1 |
| M5 | "Not recurring" branch disabled | 1 |
| M6 | Unknown column inside the `$expand` | 15 |
| M7 | `statecode ne 3` flipped to `eq 3` | 2 |

## 4. Defects Raised

| Defect ID | Severity | Status |
|---|---|---|
| D-ADR083-4 | P4 | **Closed.** [Existence query](../../provisioning/dataverse/ensure-bulk-delete-jobs.ps1#L450) expands the system job's `recurrencepattern`; a mismatch reports `EXISTS` with drift text |
| D-ADR083-5 | P4 | **Accepted and deferred by the reviewer, 2026-10-22: *"option B."*** The exact-string comparison stays. **Revisit when:** the second `ensure-bulk-delete-jobs.ps1 -Env test` run in TST/ACC, the first run after the script created the jobs, shows whether any job it created reports `⚠ recurrence drift`. If it does, development-agent normalises the comparison. Register row `A-RET-2` in §7.1. *Background: the comparison is an exact string match, and DEV stores daily schedules both as `FREQ=DAILY` and `FREQ=DAILY;INTERVAL=1;`* |

No P1, P2 or P3 defect is open.

## 5. Constraint & Compliance Verification

v3 §5 stands. Changes:

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-TECH-042](../../constraints/technology/technology-constraints.md#L84) | Idempotent provisioning | PASS | §6; M7 |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Every guess has a register row | PASS, one note | "The stored pattern equals the submitted string" is a guess with no row. Decision 1 |
| [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) | OPEN rows closable in an existing environment | PASS | Closing that guess needs a recurring job, which DEV may not hold (reviewer D-1). Its first chance is the TST/ACC run |

## 6. Provisioning Verification: read-only in DEV

2026-10-22, as `REV-MS-Provisioning`, GET only. The query format string was read from the source line at runtime, so the request was exactly the one the script sends.

| Job name in the filter | Result |
|---|---|
| `Delete Plug-in Trace Log Records` (platform, recurring) | Accepted. 1 row, state 1, `isrecurring` true, pattern `FREQ=DAILY` |
| `Bulk Delete Conversation Transcript Records Older Than 1 Month` (platform, recurring) | Accepted. 1 row, pattern `FREQ=DAILY;INTERVAL=1;` (trailing `;`) |
| `REV Retention - Paid Grant Applications` | 0 rows (no REV job in DEV, by design) |
| `ZZSYNTH-ADR083-oneoff-aiEvents-20261022` (v2's completed one-off) | 0 rows: completed history is ignored |

## 7. Platform Contract & Verification-Level Audit

### 7.1 Assumption register

A-RET-1 and A-NS-47 stay closed (v2). Orphans: none. New row, added by the reviewer's option B:

| Assumption ID | Claim | Evidence | Closing precondition | Owner | Status |
|---|---|---|---|---|---|
| A-RET-2 | `BulkDelete` stores a submitted `RecurrencePattern` (e.g. `FREQ=MONTHLY;INTERVAL=1`) on the system job exactly as sent, so the script's exact-string drift check raises no false warning | E3. DEV holds platform jobs spelt both `FREQ=DAILY` and `FREQ=DAILY;INTERVAL=1;` | Second `ensure-bulk-delete-jobs.ps1 -Env test` run in TST/ACC: each job line reads `EXISTS` with no `⚠ recurrence drift` text. If drift text appears for a job the script itself created, the claim is false and D-ADR083-5 goes to development-agent | pipeline-agent records the observation in the TST/ACC Deployment Summary; test-agent closes the row | **OPEN, deferred by reviewer** (2026-10-22, *"option B."*); not closable in DEV (D-1, no recurring job) |

### 7.2 Verification levels achieved

| Component | Claimed | Confirmed | Result |
|---|---|---|---|
| Existence query with `$expand` | V1 | **V3 (read accepted in DEV)** | PASS |
| Drift comparison | V1 | V1 (pinned by M1, M2, M4, M5) | PASS |
| Create path, the script end to end | V1 | V1 | **PARTIAL**: first live run is the pipeline's TST/ACC step |

## What you needed to decide (decided)

**Decided 2026-10-22: *"option B."*** Recorded as A-RET-2 (§7.1) and D-ADR083-5 (§4). The original question follows.

**1. Make the drift comparison tolerant of spelling, or check it on the first TST/ACC run?**

**Problem** — DEV holds the same daily schedule spelt two ways, and the script compares patterns as exact strings.
**Suggested fix** — (a) development-agent normalises both sides before comparing (upper-case, drop `INTERVAL=1` and any trailing `;`) and adds a register row (recommended; a few lines, no live write needed); or (b) leave it, and on the second TST/ACC run check whether the script prints a drift warning for a job it has just created.
**What happens if you don't** — Worst case, every pipeline run warns that each retention job has drifted when it has not. People learn to ignore that warning, including when it is real. No job is duplicated and no data is affected.

---

## 8. Recommendations

1. pipeline-agent: on the second TST/ACC run of the bulk-delete step, record in the Deployment Summary whether any job line carries `⚠ recurrence drift`, and name A-RET-2. The first run creates the jobs, so it cannot show this.

---

## Approval
**Reviewed by:** reviewer (via lead-agent, [routing.log](../../logs/routing.log) 16:01)  **Date:** 2026-10-22  **Response:** `APPROVED`, verbatim *"approved."*. The PARTIAL result is accepted for Pipeline. D-ADR083-5: *"option B."*

## Findings Logged

None this round.

Verification: 596 targeted and 798 full-suite tests passed, 0 failed; 7 of 7 mutations caught; 4 read-only DEV queries accepted, verbatim from source. Not verified: the script creating a job, how the platform stores a submitted recurrence pattern, Linux execution, TST/ACC or PRD state.
