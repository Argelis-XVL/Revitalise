# Test Report — Revitalise Grant Automation (TAD rev 14: intake trigger mode, flat Dataverse writes, callback-URL compare; wbs:4.2, 4.3)

**Feature Slug:** revitalise-grant-automation
**Artifact:** build/artifacts/revitalise-grant-automation-20261002-1/
**Date:** 2026-10-02
**Status:** PARTIAL
**WBS:** `4.2` (field mapping) and `4.3` (intake flow). Task `4.5` (test results / sign-off) is **not** discharged by this report: it needs the live intake run in section 3.
**Target:** DEV import of the unmanaged solution, then the post-import checks in section 3.
**Previous cycle:** [20260930-6 report](revitalise-grant-automation-test-report-20260930-6.md) (a different change; nothing carried over)

---

## 1. Test Summary

**PARTIAL: the packaged change is exactly what TAD rev 14 asks for and every static check passes, but nothing has been seen on a live platform, so three platform assumptions are still open.** I unzipped both solution zips and read the three flat writes, the trigger mode and the retained secure outputs from inside the package, not from source. The suites reproduce on my machine. The open assumptions can only be closed by the DEV import itself, and that is the step the reviewer is being asked to approve.

**Waiting on you:** approve the DEV import, with the explicit override described in section 7.1 (decision 1), then the post-import sequence in section 3 decides whether this becomes a pass.

| Layer | Result | Evidence |
|---|---|---|
| Static content of the package | PASS | Section 2, rows 1 to 5 |
| Unit and contract suites (Pester) | PASS | Solutions 364 of 364, provisioning 762 of 762 (1 skipped), re-run by me |
| Source gates | PASS | `run-source-gates.py`, 17 of 17 |
| Pipeline config | PASS | `verify-pipeline-config.py` exit 0, same on the HEAD version |
| Platform Contract | **OPEN** | `A-INT-11`, `A-INT-12`, `A-INT-13` still OPEN |
| Verification level | V2 (packaged) | Highest level executed. Not V3, V4 or V5 |
| Security | Not run live | Both probes need a signed URL and a live trigger |
| Accessibility, Performance | Not applicable | No screen and no NFR threshold changed |
| Cross-OS | PASS | The new scripts use `Join-Path`, `[Convert]::ToHexString` and `Invoke-RestMethod`; no `Cert:` drive or backslash path. Run on macOS only; the CI runner OS was not exercised |

---

## 2. Requirement Coverage

| # | Requirement (TAD rev 14) | Result | Where I looked |
|---|---|---|---|
| 1 | The intake trigger declares `triggerAuthenticationType: "All"` as the first key of `inputs` | PASS in both zips | Unmanaged and managed zip, [source L59](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L59). The zip file is byte-identical to source |
| 2 | `secureData` on the trigger and the caller check are retained | PASS in both zips | [source L357](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L357); trigger `runtimeConfiguration` reads concurrency 1 plus `secureData` outputs |
| 3 | `Create_application` is flat: 81 `item/` keys, with `item/rev_applicantid@odata.bind` | PASS in both zips | Measured in the packed JSON: 82 parameters (`entityName` plus 81), no nested `item`. [source L2863](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L2863) |
| 4 | `Create_new_applicant` is flat: 20 keys | PASS in both zips | 21 parameters, no nested `item`. [source L2794](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L2794) |
| 5 | `Write_error_log_row` is flat: 8 keys | PASS in both zips | 9 parameters, no nested `item`. [source L136](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVOpsFailureAlert-8F1C2A44-1004-4B7A-9E21-0A1B2C3D4E04.json#L136) |
| 6 | No Dataverse write anywhere in the solution nests `item` | PASS | I walked all 10 flows in each zip: zero nested `CreateRecord`, `UpdateRecord` or `UpdateOnlyRecord` |
| 7 | Two probe scripts and the callback-URL hash compare exist and are wired to the right environments | PASS for wiring, not executed | Probes: [TST/ACC](../../config/revitalise-grant-automation-pipeline.yml#L2131) and [PRD](../../config/revitalise-grant-automation-pipeline.yml#L2345). Capture: [L1109](../../config/revitalise-grant-automation-pipeline.yml#L1109). Compare: [L1553](../../config/revitalise-grant-automation-pipeline.yml#L1553) |
| 8 | The nested-`item` regression test can fail | Taken from the Dev Summary, **not re-run by me** | The development-agent ran it against the pre-change Ops flow from HEAD and it named `Write_error_log_row`. I did not repeat that mutation |

One observation that is not a defect. The lookup value is `/rev_applicants(<guid>)` with no quotes, while the designer's own throwaway flow quoted the GUID. The Dev Summary says the unquoted form ran on 2026-09-29, but that was in the nested shape. The flat shape with this value has never run, so the live check in section 3 asserts the lookup column specifically.

---

## 3. Post-import checks the pipeline must run in DEV (the contracted deliverable of this dispatch)

Run in this order. Each step names what it closes and what a failure means. **The order matters:** the pipeline's DEV stage has no flow-state capture or reactivation step, and an unmanaged force-overwrite import switches every cloud flow off, so the intake flow may be off when the first checks run.

| Step | Check | Closes | Pass looks like | Failure means |
|---|---|---|---|---|
| 0, before | **Close every designer tab on the intake flow without saving**, and record the intake flow's `statecode`. This is a manual precondition | IMP-1010 cause | Reviewer confirms tabs closed | A saved old tab can overwrite the import, as on 2026-09-29 |
| 0, before | Existing step: [callback-URL capture](../../config/revitalise-grant-automation-pipeline.yml#L1109) writes the hash only | `A-INT-13` (b) | Exit 0 and a snapshot file | FAIL naming `A-INT-13` means the read API was refused. Use the manual fallback in the step text: read the URL from the trigger card, hash it locally, never print it |
| 0, before | Query `rev_application` for `rev_sourcesubmissionid` values already in DEV, and pick a fresh entry id | V5 validity | An unused id | See the warning under step 5 |
| 1 | Import with the async-wait protocol | V3 | Import job completed | Stop |
| 2 | `python3 scripts/verify-live-flow-definitions.py --env dev` **immediately after the import, before any reactivation** | `A-INT-11`; also confirms `secureData` and the three flat writes | 0 differences. The script diffs the whole `properties.definition`, so the trigger mode, secure outputs and every flat key are covered | DIFFERS on the trigger: the import dropped or moved `triggerAuthenticationType` and `A-INT-11` is refuted, so the TAD needs a new decision. DIFFERS on an action: the import reshaped the write. MODIFIED: something wrote the flow after the import |
| 3 | Existing step: [callback-URL compare](../../config/revitalise-grant-automation-pipeline.yml#L1553) | `A-INT-13` (a) and (b) | PASS: same hash before and after | FAIL with `REVIEWER ACTION REQUIRED`: the website must be given the new URL. Report PARTIAL, do not roll back |
| 4 | Confirm the intake flow is **on**. If it is off, turn it on without saving in the designer. Then re-run step 2 and read any MODIFIED line against the reactivation time | V5 precondition | Flow on; the second re-read differs from the first only by `modifiedon` | Content differences after reactivation mean the reactivation rewrote the definition |
| 5 | **Live intake runs** (below) | `A-INT-12`, V5 for 4.2 and 4.3 | All assertions pass | See each row |

**The live intake runs.** The signed URL is a credential, so the reviewer supplies it from the trigger card at the moment of the run and nothing writes it down. Fixture: [intake-payloads.json](../../src/tests/data/intake-payloads.json). Use a **fresh** entry id in every body.

| Run | Body | Expected response | Row assertions (read-only query afterwards) |
|---|---|---|---|
| R1 | [IN-01](../../src/tests/data/intake-payloads.json#L18) with a fresh entry id | **201** with a reference | One `rev_application` for that id. All 45 values in the case's `expected.rev_application` match. `rev_name` set, `rev_status` 1, `rev_submittedon` within a minute of the post. **`_rev_applicantid_value` is not null and equals the new `rev_applicant` row's id** (this is the first run of the flat lookup). The `rev_applicant` row has all 14 expected values. A run that "succeeded" with an empty row is the exact failure this change exists to catch, so assert on the row and never on the run status or the HTTP code |
| R2 | R1 again, byte for byte | **200**, original reference | Still exactly one row for the id |
| R3 | [IN-03](../../src/tests/data/intake-payloads.json#L331) (required key absent) | **400** | No `rev_application` for the id. One `rev_errorlog` row with **all 8** columns populated and no applicant name, email, postcode or date of birth in any column (C-DOM-004). This is the only run that exercises the flat `Write_error_log_row` |
| R4 | [IN-04](../../src/tests/data/intake-payloads.json#L576) (wrong `x-rev-client-id`) | **401** with `"error":"unauthorised"` | Nothing written. Proves the second control survived the import |
| R5 | Signed URL with `sig` removed, no header | **401 or 403 from the platform**, not the flow's body | The flow's run list gains **no** new run. Proves `A-INT-12`. `verify-intake-endpoint-auth.ps1` cannot do this in DEV (finding below), so it is a by-hand probe and the run list is read by hand |

R1 is the minimum for the contracted "one real submission producing a populated row". R3 is needed because it is the only run that touches the third converted action. R5 closes `A-INT-12` early, instead of leaving it for TST/ACC.

**Warning for R1.** The intake flow's duplicate guard is the alternate key on `rev_sourcesubmissionid`. The DEV log records at least one resent WordPress entry that produced an empty application on 2 October. If R1 reuses that entry id, the flow answers 200 with the original reference and writes nothing, and the result reads as a pass for the guard and tells you nothing about the new write shape. Check the id first, and treat an R1 that returns 200 as a **failed run**.

**What this sequence still cannot show.** A designer save is never performed, so the original IMP-1010 failure mode (a save emptying the nested bag) is excluded by construction, not tested. That exclusion is the point of the change, but the report should not claim it was exercised.

---

## 4. Failed Tests

None. 364 of 364 solutions tests, 762 of 762 provisioning tests (1 skipped, as before), 17 of 17 source gates.

---

## 5. Defects Raised

| ID | Sev | Defect | Where |
|---|---|---|---|
| D-01 | P3 | The fixture's run instructions still describe the retired route: obtain a client-credentials bearer token and send `Authorization: Bearer`. The R1 to R4 runs cannot follow them. Logged as `IMP-1017` | [intake-payloads.json#L10](../../src/tests/data/intake-payloads.json#L10); [README.md#L197](../../src/tests/data/README.md#L197) |
| D-02 | P3 | `verify-intake-endpoint-auth.ps1 -Env dev` is accepted by the script but throws at the settings load (I ran it). DEV has no intake settings block, so the probes cannot run in DEV and the pipeline correctly does not call them there. The DEV pipeline therefore has no automated probe A or B. Logged as `IMP-1018` | [ValidateSet](../../provisioning/entra/verify-intake-endpoint-auth.ps1#L75) |
| D-03 | P3 | The DEV pipeline stage has no flow-state capture or reactivation. The TST/ACC and PRD stages have both. After an unmanaged force-overwrite import the intake flow may be off, which would make every run in section 3 fail for a reason unrelated to this change | [DEV post_deploy](../../config/revitalise-grant-automation-pipeline.yml#L1115) |
| D-04 | P3 | TAD section 12.3 row `A-INT-15` still reads "None" although the Dev Summary records it closed with live evidence. Architect-owned and already flagged by the development-agent; not repeated as a new finding | TAD section 12.3, `A-INT-15` |

No P1 or P2 defect is open. D-01 to D-03 do not block the DEV import; they block a clean run of section 3, so they should be fixed or accepted before the sequence is executed.

---

## 5a. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-DOM-004 | Personal data not written to logs | PASS (static) | `Write_error_log_row` carries 8 columns, none from the special-category register; the `domain-invariants` gate passes. Live check is R3 |
| C-DOM-010, C-DOM-011 | Audit logging on sensitive entities | NOT AFFECTED | No entity, column or audit setting changed |
| C-DOM-030, C-DOM-031, C-DOM-032 | Special-category register | PASS | `no-special-category-data-in-scoring` and `domain-invariants` gates pass in the 17 of 17 |
| C-TECH-001 | No secrets in tracked files | PASS | The callback script hashes and never prints or stores the URL; the probe script prints scheme, host and path only; settings files hold the variable name, not the value |
| C-TECH-004 | Input validation | NOT AFFECTED | No validation logic changed; R3 and R4 exercise it live |
| C-TECH-006 | Authentication on non-public routes | **UNEVALUABLE LIVE** | The control changed (signed URL plus header). Verified statically only; probes A and B are PASS-by-wiring. Live proof is R4 and R5 |
| C-TECH-014 | Unit test coverage threshold | NOT AFFECTED | No code-app change |
| C-TECH-040, C-TECH-046 | Group teams, out-of-box roles | NOT AFFECTED | No security change |
| C-TECH-042 | Idempotent scripts, convergence | PASS | New callback script's Capture overwrites its snapshot and Compare is read-only; both re-runnable |
| C-TECH-045 | DLP-compliant connectors | NOT AFFECTED | No connector added |
| C-TECH-048, C-TECH-051 | Code app data source, fabricated ids | NOT AFFECTED | |
| C-TECH-052 | Platform contract register | PASS (recorded) | Every rev 14 hand-authored contract has a row: `A-INT-11`, `A-INT-12`, `A-INT-13`, `A-INT-15`. `A-INT-14` is in the TAD only |
| C-TECH-053 | Verification level claimed | PASS | Dev Summary claims V2 and I confirm V2 and no more |
| C-TECH-054 | Cross-OS scripts | PASS (static) | See section 1 |
| C-TECH-056 | Temporary ground-truth components recorded | PASS | The reviewer's `TEST_Binding` flow is outside the solution and was not touched; its removal remains hers to record |
| C-TECH-057 | Gates proven able to fail | PASS | Build-config verifier and pipeline verifier exit 0 |
| C-TECH-058 | OPEN assumptions block deployment | **OVERRIDE NEEDED** | `A-INT-11`, `A-INT-12`, `A-INT-13` are OPEN. See 7.1 |
| C-TECH-059 | Learning substrate intact | PASS | Artifact in its own dated directory; three findings appended |
| C-TECH-060 | Text length limits | PASS | The three rewritten descriptions are 256 characters or fewer, per the field-length gate |
| C-TECH-064 to C-TECH-079 | Remaining rows scoped to test-agent | NOT AFFECTED | None concern intake auth, flow write shape or the callback script |

---

## 6. Provisioning Verification

Not applicable to this change: no site, team, app registration, group team or app share changed. `ensure-intake-client.ps1` now prints different text only; it provisions nothing new. The retained `rev-wordpress-intake` registration and its client secret are untouched, and revoking the secret remains the reviewer's action.

---

## 7. Platform Contract & Verification-Level Audit

### 7.1 Assumption register closure

| ID | Claim | Status | How it closes |
|---|---|---|---|
| A-INT-11 | An import honours the declared `inputs.triggerAuthenticationType: "All"` | **OPEN** | Step 2: 0 differences on the intake flow |
| A-INT-12 | Under *Anyone*, a POST without a valid `sig` is refused by the platform before a run is created | **OPEN** | R5, plus the run list read by hand. Also probe A in TST/ACC |
| A-INT-13 | `listCallbackUrl` (path, api-version, app-only token) returns the URL in `response.value` or `value`; and what an import does to the URL | **OPEN** | Steps 0 and 3. Never executed. I did not run it, because it needs the provisioning certificate and would be a live call outside this dispatch |
| A-INT-15 | The flat key for the Applicant lookup bind | CLOSED | Live designer-written evidence in DEV, 2026-10-02. The key matches the source. The **value** form is not covered by that evidence (see section 2) and is asserted by R1 |

Per [C-TECH-058](../../constraints/technology/technology-constraints.md#L128), an OPEN assumption blocks deployment into any environment where it could be closed. Here the only environment is DEV, and the only way to close `A-INT-11` is the DEV import. Read literally the rule forbids the experiment, so I am not treating it as a silent pass: the reviewer's explicit override is requested below, and the rule gap is logged as `IMP-1019`.

### 7.2 Verification levels achieved

| Component | Claimed | Confirmed | Not yet |
|---|---|---|---|
| Intake trigger mode in the package | V2 | V2, from the zips | V3 (`A-INT-11`) |
| Three flat Dataverse writes | V2 | V2, from the zips | V3 import, V5 run (R1, R3) |
| Both probe scripts | V1 | V1 (suites) | V5 against a live trigger; DEV cannot run them |
| Callback-URL compare script | V1 | V1 (suites) | V3 (`A-INT-13`) |
| Designer open-and-save (V4) | Not performed | Not performed, deliberately | Operating rule: this flow is never saved in the designer. The usual V4 step is therefore replaced by "reread shows 0 differences", which is evidence of a different kind |

**Result is PARTIAL, not PASS**, because V3 has not happened and V5 has not happened. It is not FAIL because the environment that could close the assumptions is the next step in the chain.

---

## 8. Recommendations

1. Add a DEV flow-state capture before the import and a check after it (D-03), or put "intake flow is on" in the step 4 manual list as written above.
2. Fix the fixture run instructions (D-01) before anyone follows them.
3. Narrow the probe script's `-Env` list to the three environments it works for (D-02).
4. After R1 to R5 pass, record V5 for tasks 4.2 and 4.3 and re-dispatch test-agent for a closing report; the same results then feed the TST/ACC smoke tests, which already carry probe A and B.

### What you need to decide

**1. Approve the DEV import of this artifact, with an explicit override of the three open assumptions?**

**Problem** — The rule says an open assumption blocks deployment where it could be closed, and the DEV import is the only thing that can close these three.
**Suggested fix** — Reply `OVERRIDE A-INT-11, A-INT-12, A-INT-13` with the reason "closed by the DEV import and section 3 of this report", for DEV only.
**What happens if you don't** — The DEV import does not run, and none of the three assumptions can ever be measured.
[C-TECH-058](../../constraints/technology/technology-constraints.md#L128)

---

**2. Who runs R1 to R5, and who supplies the signed URL?**

**Problem** — The signed URL is a credential that exists only on the trigger card, and I may not read or store it.
**Suggested fix** — You post the five bodies (or ask Alex's site to post R1), and the pipeline-agent reads the rows afterwards with the read-only queries in section 3.
**What happens if you don't** — Tasks 4.2 and 4.3 stay at V2 and cannot be carried into the phase acceptance pack.
[Section 3](#3-post-import-checks-the-pipeline-must-run-in-dev-the-contracted-deliverable-of-this-dispatch)

---

**3. Fix D-03 first, or accept it and handle reactivation by hand?**

**Problem** — The DEV stage does not record or restore flow state, and an unmanaged import may leave the intake flow off.
**Suggested fix** — Handle it by hand this once through step 4, and add the capture and diff to the DEV stage afterwards.
**What happens if you don't** — A flow that is simply switched off looks like a failed import in every later step.
[DEV post_deploy](../../config/revitalise-grant-automation-pipeline.yml#L1115)

---

## Verification actually performed

Re-run by me: Pester solutions 364 of 364, Pester provisioning 762 of 762 (1 skipped), `run-source-gates.py` 17 of 17, `verify-pipeline-config.py` exit 0 on the working tree and on the HEAD version, `verify-live-flow-definitions.py --selftest` passed. Read by me: both solution zips, member by member, for the trigger, the four flat-write actions, and every other Dataverse write. Ran `verify-intake-endpoint-auth.ps1 -Env dev` once to confirm D-02; it failed at settings load before any network call.

**Not verified, and why:** nothing against a live endpoint. I did not run the callback-URL script (needs the provisioning certificate), either probe (needs a signed URL), the regression-test mutation, the CI runner OS, or any DEV query. Highest level reached: V2.

## Approval

Reviewer: ____________  Date: ____________

## Findings Logged

[IMP-1017, IMP-1018 and IMP-1019](../../logs/improvement-log.jsonl): fixture instructions describe the retired token route, a probe script accepts an `-Env` it cannot run for, and C-TECH-058 forbids the experiment that closes the assumptions it guards.
