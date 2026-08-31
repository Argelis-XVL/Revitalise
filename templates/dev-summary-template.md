# Dev Summary Document — <Feature Name>

**Feature Slug:** <slug>
**TAD Reference:** docs/architecture/<slug>-architecture.md
**Date:** <YYYY-MM-DD>
**Status:** DRAFT | APPROVED

---

## 1. Implementation Summary
<!-- What was built, in plain language -->

## 2. Components Changed / Created
| Component | Type | Change Description | FR Reference |
|---|---|---|---|

## 3. Data Model Changes
<!-- Tables / fields / migrations applied. Reference TAD §3 -->

## 4. Automation / Workflow Changes
<!-- Async processes, jobs, event handlers implemented -->

## 5. Configuration & Provisioning Changes
| Key | Environment | Notes |
|---|---|---|

### Provisioning Scripts
<!-- One row per TAD §12 item. Scripts live in provisioning/; every script is
     idempotent (C-TECH-042) and wired into config/<slug>-pipeline.yml. -->

| Script | Purpose | Pipeline Block (tenant_prerequisites / post_deploy:<env>) | Idempotency Check |
|---|---|---|---|

## 6. Security Controls Implemented
<!-- Map each TAD §6 security control to its implementation.
     Include the TAD §6.1 role/group bindings: roles in the solution,
     group teams + role association in provisioning scripts (C-TECH-040). -->

## 7. Known Limitations / Deferred Items

## 8. Build Instructions
<!-- Used by build-agent. Must be complete enough to populate config/<slug>-build.yml -->

## 9. Test Guidance
<!-- Edge cases, known risks, required test data setup. Read by test-agent. -->

## 10. Unvalidated Assumptions Register (C-TECH-052)
<!-- Load skills/how-to-verify-a-platform-contract.md before completing this section.

     One row per hand-authored platform contract NOT confirmed against ground truth (an
     artefact the platform itself produced: an export+unpack of a working instance, a live
     GET, a metadata response). Serialisation shapes, file layouts, field limits, id
     assignment, what a deploy can create vs only update, host-OS APIs.

     Evidence levels — only E1 is verification:
       E1 platform-produced artefact | E2 first-party docs for THIS tool version
       E3 docs for another version / decompiled source / blog / similar component | E4 inference

     Each row also carries an `A-nnn` comment at the point of the guess in source, so the
     next person editing that file sees it without reading this document.

     This is a work list, not a disclaimer. When the first real environment appears, close
     the whole register in ONE sweep before the first deploy — not one deploy failure at a
     time (skill §6). Be specific: vague rows catch nothing.

     A ROW ABOUT A CONDITIONAL OR ERROR BRANCH IS WORDED IN BOTH DIRECTIONS. Added
     2026-08-28, IMP-0347. State the claim AND its verification as two halves:
       - it FIRES WHEN IT SHOULD, and
       - it DOES NOT FIRE WHEN IT SHOULD NOT.

     A one-sided row can be closed CONFIRMED by a test that exercises only the happy half,
     which certifies the opposite defect as verified. That happened: A-FLOW-05 claimed
     Respond_error "will actually execute and return a body to the calling code app", and
     its cheapest-verification step — force a failure, confirm a status:error body — would
     have PASSED while a success-path double-response defect survived underneath it. The
     flow replied twice on every successful run, and the row would have read CONFIRMED over
     a live P1.

     So, for a conditional branch:
       Claim:        "Respond_error fires when Compute_statistics fails, AND does not fire
                      on a successful run (the failure chain is Skipped and Skipped is not
                      an accepted runAfter status)."
       Verification: "Force a failure -> status:error body. THEN run the success path and
                      confirm exactly ONE response body is sent."
     -->

| ID | Claim (one sentence — BOTH directions if it is a conditional) | Where in source | Evidence | Why not verified | Cheapest verification (BOTH directions) | Status |
|---|---|---|---|---|---|---|
| A-001 | | | E2 / E3 / E4 | | | OPEN / VERIFIED <date> / CORRECTED <ref> |

## 11. Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

### Verification level reached
<!-- Per component or component group. Never claim a level not actually executed.
     V1 well-formed · V2 packages · V3 accepted by target (+ re-run for idempotency)
     · V4 opened AND saved by a human in the designer/editor · V5 executed end-to-end
     Where it was proven matters: DEV ≠ TST/PRD, unmanaged ≠ managed, macOS ≠ the CI runner. -->

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|

### Tool warnings triaged (C-TECH-055)
<!-- Every warning from build, pack, or deploy: resolved, or accepted with a stated reason.
     None may be carried silently. "No warnings emitted" is a valid entry. -->

| Warning | Source step | Resolved / Accepted | Rationale if accepted |
|---|---|---|---|

### Diagnostic components created and removed (C-TECH-056)
<!-- Anything built in an environment purely to obtain ground truth or to investigate.
     Left in place, it ships to every downstream environment. "None" if not applicable. -->

| Component | Environment | Purpose | Removed (date / how) |
|---|---|---|---|

---

## Findings Logged

Every finding raised while producing this document, per
`skills/how-to-log-an-improvement.md`. `none` is a valid answer; an empty section is not.

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-nnnn | `<class_instance_of>` | friction / rework / blocker | <the imperative sentence that reached the digest> |

Digest regenerated: YES / NO — `python3 scripts/generate-known-failure-modes.py`

---

## Code Review Checklist
- [ ] All FR IDs covered
- [ ] No hardcoded secrets
- [ ] Security controls from TAD §6 implemented
- [ ] Every TAD §12 item has an idempotent provisioning script wired into `config/<slug>-pipeline.yml` (C-TECH-042)
- [ ] Role assignments via group teams only — no direct user assignments in Test/Acc/Prd (C-TECH-040)
- [ ] No hardcoded environment-specific IDs/URLs — environment variables or deployment settings (C-TECH-047)
- [ ] Every guessed platform contract is in §10 **and** commented `A-nnn` in source (C-TECH-052)
- [ ] Where an environment existed, ground truth was used instead of a guess — two failed guesses is the signal to stop guessing
- [ ] Every platform limit the packer/compiler does not enforce has a build gate in `config/<slug>-build.yml`
- [ ] Verification levels in §11 are the levels actually executed, not the levels expected (C-TECH-053)
- [ ] Scripts run on the CI runner's OS — no OS-specific APIs, drives, or path assumptions (C-TECH-054)
- [ ] Every tool warning triaged in §11 (C-TECH-055); no diagnostic components left in the solution (C-TECH-056)
- [ ] Accessibility requirements met (if UI)
- [ ] No dead code or debug statements
- [ ] Unit tests written

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`
