# Test Report — <Feature Name>

**Feature Slug:** <slug>
**Artifact:** build/artifacts/<slug>-<YYYYMMDD>-<n>/
**Date:** <YYYY-MM-DD>
**Status:** PASS | FAIL | PARTIAL

---

## 1. Test Summary
| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit | | | | |
| Integration | | | | |
| End-to-End | | | | |
| Regression | | | | |
| Security | | | | |
| Accessibility | | | | |
| Performance | | | | |
| Provisioning | | | | |
| Compliance | | | | |
| **Total** | | | | |

## 2. Requirement Coverage
| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|

## 3. Failed Tests
| Test ID | Layer | Description | Expected | Actual | Severity |
|---|---|---|---|---|---|

## 4. Defects Raised
| Defect ID | Severity | Description | Linked Test |
|---|---|---|---|

## 5. Constraint & Compliance Verification
<!-- Constraint check: one row per in-scope domain and technology constraint. -->

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|

<!-- Compliance: confirm each item in skills/compliance-checklist.md was checked;
     record results in the verification table from §3 of that file. -->

## 6. Provisioning Verification
<!-- One row per TAD §12 item and §6.1 mapping row. Verified via Graph / Dataverse
     Web API queries — see the Verification sections of security-model.md,
     sharepoint.md, and teams.md. -->

| Item (TAD §12 / §6.1) | Expected | Verified Via | Result |
|---|---|---|---|

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)
<!-- Load skills/how-to-verify-a-platform-contract.md. The test-agent is the final verifier
     of the Dev Summary §10 register and of the verification levels claimed in §11. -->

### 7.1 Assumption register closure
<!-- One row per Dev Summary §10 row. An OPEN row against an environment that now exists is
     a defect, not a note: the environment is the means of closing it (skill §6). Also
     report ORPHANS — hand-authored contracts with no register row (C-TECH-052 violation).

     RECORD EACH ROW'S CLOSING PRECONDITION SEPARATELY FROM ITS STATUS (IMP-0219). A row's
     OPEN/CLOSED value is accurate for the date its report was written and can be stale a day
     later purely because the ENVIRONMENT moved, with no source change to prompt a re-read.
     Six rows here were correctly deferred as "not closeable until the Code App is pushed to
     DEV"; the app was pushed, and nothing re-evaluated them because the trigger lived in
     prose. So state the precondition as its own fact and answer it at the START of every test
     cycle touching this feature — do not re-derive it from last cycle's narrative. -->

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|

### 7.2 Verification levels achieved
<!-- Confirm, do not assume. V2 (packages) says nothing about V3 (accepted); V3 says nothing
     about V4 (a human can open and save it). V4 is a human step with a named owner and
     cannot be automated away — record who performed it and when. -->

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|

- Idempotency: deploy re-run against an already-deployed target → result: `<PASS / FAIL>`
- V4 designer/editor open + save, performed by `<name>` on `<date>` → result: `<PASS / FAIL>`
- Cross-OS (C-TECH-054): pipeline/CI scripts executed on the CI runner OS → result: `<PASS / FAIL / N-A>`
- Warnings triaged (C-TECH-055) and diagnostic components removed (C-TECH-056) → result: `<PASS / FAIL>`

## 8. Recommendations

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

Every finding raised while producing this document, per
`skills/how-to-log-an-improvement.md`. `none` is a valid answer; an empty section is not.

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-nnnn | `<class_instance_of>` | friction / rework / blocker | <the imperative sentence that reached the digest> |

Digest regenerated: YES / NO — `python3 scripts/generate-known-failure-modes.py`
