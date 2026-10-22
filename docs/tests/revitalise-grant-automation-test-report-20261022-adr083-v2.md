# Test Report — Revitalise Grant Automation, ADR-083 retention delete jobs (wbs:0.7), retest v2

**Feature Slug:** revitalise-grant-automation
**Artifact:** none. Source-level change, not packed. Same scope as [v1](revitalise-grant-automation-test-report-20261022-adr083.md).
**Date:** 2026-10-22  **Tester:** test-agent, strategic tier (re-dispatch line in [routing.log](../../logs/routing.log), 13:40)  **WBS:** 0.7
**Items:** WI-0142
**Authority for live writes:** reviewer, verbatim 2026-10-22 13:40: *"1. Allow one off test"*. Synthetic rows only, one non-recurring bulk delete per job, DEV only.
**Status:** **FAIL.** The one-off DEV check found two P1 defects in [ensure-bulk-delete-jobs.ps1](../../provisioning/dataverse/ensure-bulk-delete-jobs.ps1#L422). As written, the script would report FAILED for all six retention jobs in every environment. Both defects date from Phase 1 (2026-08-14), not from ADR-083. The ADR-083 design itself is sound. With the request body corrected, DEV accepted both queries and they deleted exactly the right synthetic rows.

Highest level reached: **V5 for the query logic with a corrected body** (one-off jobs run in DEV and their deletions checked). **V3-refused for the script as written.**

## Summary

The paid-grant query selected exactly one of the five synthetic applications, the right one. Deleting it also removed its grant, review and payment through the cascade. The AI Events query is accepted by `BulkDelete` and removed exactly the one old synthetic row. However, the platform refuses the script's own request body, and it also rejects the column the script uses to check whether a job already exists. So no retention job would ever be created. Both are development-agent fixes. Nothing real in DEV was touched, and no recurring job remains.

## 1. Test Summary

| Layer | Run | Passed | Failed | Evidence |
|---|---|---|---|---|
| Unit and regression (v1, not re-run) | 590 / 792 | 589 / 791 | 0 | v1 §1. No source changed since |
| Live, script body as written (`BulkDelete`) | 2 | 0 | **2 refused (400)** | §3, D-ADR083-2. Nothing was created |
| Live, script existence check as written | 1 | 0 | **1 refused** | §3, D-ADR083-3 |
| Live, one-off jobs with typed values + synthetic-id guard | 2 | 2 | 0 | §6. Both reached Completed/Succeeded, 1 row deleted each, `isrecurring` false |
| Pre-run counts with the production criteria over all of DEV | 2 | 2 | 0 | Each matched only its synthetic target. No real row matched |
| Cleanup and side-effect audit | 1 | 1 | 0 | §6. DEV totals back to baseline; 9 recurring jobs before and after, all Microsoft's own |

## 2. Requirement Coverage

| Requirement | Test case | Result |
|---|---|---|
| [FR-048](../../docs/plans/revitalise-grant-automation-plan.md#L2178) / [NFR-010](../../docs/plans/revitalise-grant-automation-plan.md#L2344): paid-grant applications deleted 6 years after final payment | RET-1: S1 (Grant Paid, final payment 2020-09-22) deleted. Controls kept: S2 (Grant Paid, 2020-11-22), S3 (Grant Paid, no date), S4 (Approved, 2020-09-22), S5 (Grant Paid, no grant) | **PASS (V5) with typed values. FAIL as the script sends it** |
| ADR-083 item 1: the cascade removes Review, Grant and Payment | RET-1: S1's grant, review and payment were gone after the job. The applicant was kept, which is the orphan sweep's job | **PASS (V5)** |
| ADR-083 item 2: `msdyn_aievent` older than 30 days removed | NS-47: E1 (backdated to 2026-09-12) deleted; E2 (today) kept | **PASS (V5) with typed values. FAIL as sent.** Daily recurrence not run, by D-1 |
| Every retention job (C-DOM-003) is created by the pipeline step | Existence check against DEV | **FAIL**: D-ADR083-3 stops every job before it is created |

## 3. Failed Tests

| Test ID | Layer | Description | Expected | Actual | Severity |
|---|---|---|---|---|---|
| LIVE-1 | Integration | `BulkDelete` with the body from [`New-RetentionQuerySet`](../../provisioning/dataverse/ensure-bulk-delete-jobs.ps1#L83), unchanged apart from the synthetic-id condition | Accepted | `0x80040203` *"ConditonOperator.Equal requires 1 value/s, not 0. Parameter Name: rev_status"*, and the same for `OlderThanXDays` on `createdon`. The platform drops bare JSON numbers in `Values` | **P1** |
| LIVE-2 | Integration | The script's existence check `$select=…,recurrencepattern` on `bulkdeleteoperations` ([L422](../../provisioning/dataverse/ensure-bulk-delete-jobs.ps1#L422)) | Returns rows | `0x80060888` *"Could not find a property named 'recurrencepattern' on type bulkdeleteoperation"*. The column is on `asyncoperation`. `bulkdeleteoperation` has `isrecurring` and `nextrun` | **P1** |
| MUT-7 (v1) | Unit | `msdyn_aieventid` is not asserted | | Unchanged | P4 |

## 4. Defects Raised

| Defect ID | Severity | Description | Fix (for development-agent) |
|---|---|---|---|
| D-ADR083-2 | **P1** | Every `ConditionExpression.Values` entry in the script ([L132](../../provisioning/dataverse/ensure-bulk-delete-jobs.ps1#L132), [L318](../../provisioning/dataverse/ensure-bulk-delete-jobs.ps1#L318), [L344](../../provisioning/dataverse/ensure-bulk-delete-jobs.ps1#L344), [L383](../../provisioning/dataverse/ensure-bulk-delete-jobs.ps1#L383) and four more) is a bare number. All six jobs are affected. The Pester fakes accept any body, so 89 tests pass over it | Send each value as `{"@odata.type":"Microsoft.Dynamics.CRM.Object","Type":"System.Int32","Value":"11"}`. This exact shape was accepted in DEV. Update the assertions at [DataverseScripts L914](../../src/tests/provisioning/DataverseScripts.Tests.ps1#L914) and the others to match |
| D-ADR083-3 | **P1** | The existence check selects a column `bulkdeleteoperation` does not have. Every job would report FAILED before it is created. The fakes return `recurrencepattern` ([L963](../../src/tests/provisioning/DataverseScripts.Tests.ps1#L963)) | Drop it from `$select` and read the recurrence from the related `asyncoperation` (`_asyncoperationid_value`). The `statecode ne 3` premise itself holds: in DEV each of the 9 recurring jobs has exactly one row in state 1 |
| D-ADR083-1 | P4 | (v1) No test asserts `msdyn_aieventid` | Recommendation, as before |

## 5. Constraint & Compliance Verification

v1 §5 stands, with these rows changed:

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-DOM-003](../../constraints/domain/domain-constraints.md#L36) | Retention implemented | **FAIL** | D-ADR083-2 and D-ADR083-3: no job can be created by the shipped script |
| [C-TECH-042](../../constraints/technology/technology-constraints.md#L84) | Idempotent provisioning | **FAIL** (was PASS at V1) | The idempotency path is the existence check, and DEV refuses it |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Every guess has a register row | PASS, with gap | The two failing shapes were never register rows; they were assumed by the Phase 1 script. `IMP-1231` |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Report only the level executed | PASS | §7.2 separates the script as written from the corrected body |
| [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) | OPEN rows closable in an existing environment | **PASS** (was FAIL) | `A-RET-1` and `A-NS-47` measured in DEV (§7.1) |
| [C-TECH-067](../../constraints/technology/technology-constraints.md#L137) (SOFT) | Counts not hand-typed | WARN | Unchanged; passed on to development-agent |

## 6. Provisioning Verification: the one-off DEV check

All times are UTC, 2026-10-22. Identity: the provisioning application user `REV-MS-Provisioning` (app `077f1f90…`, System Administrator in DEV). WhoAmI was confirmed before any write. Its certificate was used through `provisioning-common.ps1`. Every row carries the marker `ZZSYNTH-ADR083-20261022` in its name. No real applicant text was used.

**What was run, in order**

1. **Baseline (13:2x, read).** AI Events: 105, none older than 30 days. Recurring bulk-delete jobs: 9, all Microsoft platform jobs, none `REV` or `ZZ`.
2. **Created (13:24).** 1 applicant. Applications S1 to S5 (status 11, 11, 11, 7, 11). Grants for S1 to S4 (`rev_finalpaymentdate` 2020-09-22, 2020-11-22, none, 2020-09-22). A review and a payment under S1. AI Events E1 and E2 (`msdyn_creditconsumed` 0, status Processed). **Backdating contract:** E1 was created with `overriddencreatedon` set to 40 days ago, and the platform stored `createdon` = 2026-09-12. No date override was needed for the grants, because `rev_finalpaymentdate` is a plain Date Only column.
3. **Side effect (see decision 1).** The header `MSCRM.BypassBusinessLogicExecution: CustomSync,CustomAsync` did **not** stop the Dataverse-triggered flows. 10 runs fired:
   - Scoring ×3, which set all five synthetic applications to status 5.
   - Create Envelope ×2, failed with *"Nothing was sent to DocuSign"*.
   - Capture Payment ×1, failed safely.
   - Scrub Free-Text ×3, terminated with no AI Builder call (AI Event count unchanged).
   - **Failure Alert ×2.**

   They also wrote 5 `rev_errorlog` rows, each naming a synthetic record.
4. **Statuses reset (13:26)** with `MSCRM.SuppressCallbackRegistrationExpanderJob: true`. No flow ran (0 runs, checked 45 s later). That header is used for every later write.
5. **Pre-run counts (read).** The production criteria over **all of DEV** returned paid-grant = 1 (S1 only) and AI Events = 1 (E1 only). The same criteria plus the synthetic-id guard returned the same 1 each. DEV totals: applications 30, grants 9, reviews 5, payments 2, AI Events 107.
6. **First submission (13:28), the script's body unchanged + guard:** refused, 400, for both jobs (LIVE-1). Nothing was created. That is why each job was submitted twice; only one run per job executed.
7. **Second submission (13:3x), values typed + guard.** Both were accepted and completed:
   - `ZZSYNTH-ADR083-oneoff-paidGrantApplications-20261022`: async `5acfc591…`, state 3/30, success 1, fail 0, `isrecurring` false.
   - `ZZSYNTH-ADR083-oneoff-aiEvents-20261022`: async `d7dff092…`, same result.

   Guard: an `In` condition on `rev_applicationid` (S1 to S5) or on `msdyn_aieventid` (E1, E2). `RecurrencePattern` was empty.
8. **Post-run.**
   - Gone: S1 and its grant, review and payment, and E1.
   - Present: S2 to S5 with their grants, E2, and the applicant.
   - DEV totals: 29 / 8 / 4 / 1 / 106. Each total fell by exactly the synthetic rows expected.
9. **Cleanup.** The following were deleted with the suppression header:
   - S2 to S5 (their grants went by cascade), E2 and the applicant.
   - The 5 synthetic error-log rows.

   Afterwards no `ZZSYNTH` row remained in any of the 7 tables. DEV totals came back to the real baseline: 25 applications, 5 grants, 4 reviews, 1 payment, 105 AI Events. No flow ran. Recurring jobs: 9, unchanged. The two completed one-off job records remain in system-job history (state Completed, not recurring).

## 7. Platform Contract & Verification-Level Audit

### 7.1 Assumption register closure

| Assumption ID | Claim | Result | Evidence |
|---|---|---|---|
| [A-RET-1](../../docs/development/revitalise-grant-automation-dev-summary.md#L13307) | Paid-grant query accepted by `BulkDelete` and selects exactly the right applications | **REFUTED as written; CLOSED (E1) for the corrected body.** Selection and cascade are proven. The body as built is refused (D-ADR083-2) | §6 steps 5 to 8 |
| [A-NS-47](../../docs/development/revitalise-grant-automation-dev-summary.md#L13310) | `BulkDelete` accepts `msdyn_aievent` with `createdon` `OlderThanXDays` and removes the rows | **CLOSED (E1) for the corrected body, one-off.** The daily recurrence is not run (D-1). The PRD first-run check stays as the recurrence proof | §6 steps 7 and 8 |
| A-NS-45 | (c) service-account reach | **Accepted by reviewer** 2026-10-22 (*"2. Accepted."*); architect-agent records it | Not a test blocker |
| A-NS-46 | Credit reporting | OPEN, PRD only by design | |
| New, unregistered | `bulkdeleteoperation` has a `recurrencepattern` column; bare JSON values bind in `ConditionExpression` | **Both FALSE (E1)** | D-ADR083-3, D-ADR083-2 |

v1 decision 2, about grant `86049ed0…` with its application at Under Review: **dismissed** by the reviewer (*"That was me for testing the narrative flow. This can be ignored."*). It is not a defect.

### 7.2 Verification levels achieved

| Component | Claimed | Confirmed | Result |
|---|---|---|---|
| `paidGrantApplications`, script as written | V1 | V3 **refused** | FAIL |
| `aiEvents`, script as written | V1 | V3 **refused** | FAIL |
| Same queries, values typed (not yet in source) | n/a | V5, one-off, DEV | Proves the design. Not shipped |
| Existence check (all six jobs) | V1 | **refused** | FAIL |

## What you need to decide

**1. Note that synthetic rows briefly triggered DEV flows, including two Failure Alert emails**

**Problem** — The header I used to stop flows did not stop them. 10 DEV flow runs fired on the synthetic rows, and two of them sent a Failure Alert email to the ops recipient.
**Suggested fix** — No action needed beyond reading this. Nothing reached DocuSign. The 5 error-log rows are deleted. The correct header (`MSCRM.SuppressCallbackRegistrationExpanderJob`) is now recorded in `IMP-1232`.
**What happens if you don't** — Whoever receives Failure Alerts may treat the two 13:24 UTC emails as real. Both name `ZZSYNTH-ADR083-20261022` records.

---

## 8. Recommendations (passed to development-agent through lead-agent)

1. **P1, D-ADR083-2 and D-ADR083-3:** type every condition value as `Microsoft.Dynamics.CRM.Object`, and take `recurrencepattern` out of the existence `$select`. Then make the Pester fakes reject both shapes, so these tests catch the defect rather than pin it.
2. P4, D-ADR083-1: assert `msdyn_aieventid` in the `aiEvents` column set.
3. C-TECH-067 (SOFT): mark the literal 5 and 6 at [DeploymentSettings L565](../../src/tests/provisioning/DeploymentSettings.Tests.ps1#L565) *count-coupled by design*, or derive them.
4. After the fix, a retest needs only one live action: run the fixed script's existence check once against DEV (read-only). The query bodies are already proven by this run.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-1231 | `static-test-missed-platform-rejection` | rework | Send a hand-built Web API body once to a live org before trusting it; type QueryExpression values as `Microsoft.Dynamics.CRM.Object` and select only columns the metadata lists. |
| IMP-1232 | `reality-contradicted-doc` | friction | Synthetic writes to an environment with live flows need `MSCRM.SuppressCallbackRegistrationExpanderJob: true`, checked with a flow-run count before and after. |

Digest regenerated: YES

Verification: 2 one-off DEV bulk deletes ran (1 row each, both correct), with 4 controls kept for the paid-grant job and 1 for the AI Events job; 3 live refusals recorded; DEV row totals checked before, after and post-cleanup. Not verified: daily or monthly recurrence, TST/ACC or PRD, Linux execution, whether bulk deletes appear in the audit log.
