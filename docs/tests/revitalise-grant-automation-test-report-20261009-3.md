# Test Report — Revitalise Grant Automation (scoped build, flow REVSafeguardingActionCompletion)

**Feature Slug:** revitalise-grant-automation
**Artifact:** build/artifacts/revitalise-grant-automation-20261009-3/
**Date:** 2026-10-16
**Status:** PARTIAL
**Items / WBS:** WI-0028 (EF-27), wbs:0.4

Conclusion: the packaged flow is correct against its source and every static check passes, but nothing has been executed in an environment. The build is fit for a DEV deploy of this one flow, and that deploy is the only way to close the one open question. It is not fit for promotion.

## 1. Test Summary
| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit (Pester, SafeguardingActionCompletion.Tests.ps1) | 16 | 16 | 0 | 0 |
| Integration (source gates, run-source-gates.py) | 19 | 19 | 0 | 0 |
| Flow-definition language gate | 1 | 1 | 0 | 0 |
| Packaged-vs-source equality (managed zip) | 1 | 1 | 0 | 0 |
| End-to-End (live tick, read back) | 0 | 0 | 0 | 1 (NOT EXECUTED, no live run possible) |
| Security / Accessibility / Performance | 0 | 0 | 0 | 3 (N-A: no UI, no new privilege, no NFR in scope) |
| Provisioning | 0 | 0 | 0 | 1 (N-A: no TAD §12 item touched) |

## 2. Requirement Coverage
| Requirement | Test / evidence | Result |
|---|---|---|
| EF-27 / WI-0028: "An action completed record for safeguarding incidents" | Source: completed-on and completed-by written on tick ([flow L99](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVSafeguardingActionCompletion-8F1C2A44-1009-4B7A-9E21-0A1B2C3D4E09.json#L99)). Pester 16/16. Not executed live | PARTIAL |
| Completed-by bound as `item/rev_safeguardingactioncompletedby@odata.bind` = `/systemusers(<_modifiedby_value>)` | Present in source and in the managed zip definition (definition-equal check) | PASS (static) |
| Trigger `conditions` loop guard (checkbox true AND completed-on empty) | Present in source ([flow L32](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVSafeguardingActionCompletion-8F1C2A44-1009-4B7A-9E21-0A1B2C3D4E09.json#L32)) and in zip; also column filter on the checkbox and an inner If | PASS (static) |
| Failure path leaves checkbox ticked with no date and alerts | Alert and Terminate actions present ([flow L126](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVSafeguardingActionCompletion-8F1C2A44-1009-4B7A-9E21-0A1B2C3D4E09.json#L126)) | PASS (static) |

Fail-safe-default check (IMP-0511): the flow has no configuration default the TAD declares fail-safe. N-A.

## 3. Failed Tests
None.

## 4. Defects Raised
None. Two observations, not defects: (a) un-ticking and re-ticking the box does not rerun the write, because the completed date stays set and the guard needs it empty. That is probably intended; the reviewer should confirm. (b) The Solution Checker Medium (flow-avoid-recursive-loop) stands, accepted at [Dev Summary L10324](../development/revitalise-grant-automation-dev-summary.md#L10324). The rule ignores trigger filters; the writes (completed-on, completed-by) are disjoint from the filtered checkbox, and the condition guard backs it up. I agree with the rationale as far as static reasoning goes; a live tick is what proves no rerun.

## 5. Constraint & Compliance Verification
Scope: constraints whose Verify By is a script or a read of the changed flow. I did not re-walk the full constraint files; rows not listed were not touched by a one-flow change and are NOT claimed as verified.

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-TECH-030 | Deploy only a managed artifact from build-agent, with a test report naming the build | PASS once this report is saved | manifest names itself, status SUCCESS; this report names the build. Re-run verify-artifact-provenance.py --env dev |
| C-TECH-030 (scoped) | Change-scoped artifact goes only to the first environment | PASS (condition) | Manifest is scoped (18 steps skipped-unchanged). DEV only, with --env dev |
| C-TECH-055 | Tool warnings triaged | PASS | 3 warnings, 3 accepted with rationale, 0 untriaged (manifest) |
| Flow-definition language rules | verify-flow-definition-language.py checks 11-13 and the rest | PASS | exit 0, 11 flows |
| Source gates (19) | root components, component shape, guid syntax, domain invariants etc. | PASS | run-source-gates.py exit 0, no FAIL lines |
| C-TECH-052 | Hand-authored artefact has a register row | PASS | A-SG-1 row at [Dev Summary L8922](../development/revitalise-grant-automation-dev-summary.md#L8922) |
| C-TECH-053 | Verification level confirmed as claimed | PARTIAL | see 7.2 |
| Commercial C-COM-002 | Work maps to an accepted WBS task | PASS | wbs:0.4 carried by handoff, work item and manifest |

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure
| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| A-SG-1 | Completed-by can be set from the trigger row's `_modifiedby_value` | CLOSED 2026-10-09 | The deploy of this flow to DEV, then a real tick read back | Environment yes (DEV). The deploy of this build: no | Shape: yes, source equals the reviewer's DEV definition by the Dev Summary's account. Payload carries `_modifiedby_value` and the stored user is the ticker: NO | PARTIAL |

Observation: the register marks A-SG-1 CLOSED, but the closing evidence is a hand edit in the DEV designer and a re-export. That shows the binding shape is accepted. It does not show a triggered run wrote the right user. I treat that half as still open. I am not failing on it, because deploying this build to DEV is the means of closing it.

### 7.2 Verification levels achieved
| Component | Level claimed | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| REVSafeguardingActionCompletion | V2 (packaged), per manifest | V2 | manifest verification_level; zip definition equals source | PASS at V2 |
| Same flow, in this build | not above V2 | V3 to V5 not reached | no import, no run | PARTIAL |

- Idempotency (deploy re-run): NOT EXECUTED
- V4 open-and-save then re-read live: NOT EXECUTED (reviewer's earlier DEV edit predates this build)
- Cross-OS: N-A, no pipeline script changed
- Warnings triaged: PASS. Diagnostic components (C-TECH-056): none in this change

## 8. Recommendations
1. Deploy to DEV as a single-component temp pack, using --env dev.
2. After import, turn the flow on, tick Action Completed on a test application as a signed-in user, and read back completed-on and completed-by. Expect the ticker, and expect exactly one run. That closes A-SG-1 and moves WI-0028 above packaged.
3. Do not promote this artifact: it holds no code-app output. Promotion needs a full unscoped build.
4. Manifest source commit is 9ee9e00. The flow files are unchanged between that commit and HEAD, so the provenance holds for this flow.

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

## Findings Logged
| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | - | - | Register-status observation recorded in 7.1 only |
