# Test Report — Revitalise Grant Automation (Create Envelope rebuild, TAD rev 15; wbs:3.2, 3.5)

**Feature Slug:** revitalise-grant-automation
**Artifact:** build/artifacts/revitalise-grant-automation-20261003-2/
**Date:** 2026-10-03
**Status:** PARTIAL
**WBS:** `3.2` (acceptance flow) and `3.5` (test results / sign-off). Task `3.5` is **not** discharged by this report: its deliverable needs a DocuSign run, which has not happened.
**Work items:** WI-0107, WI-0109, WI-0111 (built). WI-0108 and WI-0110 are deferred template settings and are not tested here.
**Target:** DEV import of the unmanaged solution, then the DocuSign R1 to R6 run.
**Previous cycle:** [20261002-1 report](revitalise-grant-automation-test-report-20261002-1.md) (a different change, the intake flow; nothing carried over)

---

## 1. Test Summary

**PARTIAL: the packaged flow does what TAD rev 15 and the reviewer's all-tabs direction ask, every static check I re-ran passes, and nothing has been seen on DocuSign, so five platform assumptions stay open.** I unzipped both solution zips and the Create Envelope file inside each is byte-identical to source. I re-ran the whole Pester suite and the source gates myself, and I broke three expressions on purpose to confirm the tests notice.

**Waiting on you:** the explicit override in section 7.1 (decision 1), so the DEV import can run and close the open assumptions.

**TAD status, as found, not resolved.** TAD rev 15 (ADR-067, ADR-068, sections 5.8 to 5.10 and 12.5) still reads "presented for review and not yet approved" in the [TAD header](../architecture/revitalise-grant-automation-architecture.md#L6). The reviewer's "Approved" of 2026-10-02 was given on the Dev Summary, and the [routing log](../../logs/routing.log#L1283) records that the TAD "itself still not formally APPROVED". The Dev Summary quotes her direction to implement ([Dev Summary rev 15 section](../development/revitalise-grant-automation-dev-summary.md#L12223)). I tested against the TAD as written plus her recorded overrides.

| Layer | Result | Evidence |
|---|---|---|
| Unit and contract (Pester, whole `src/tests`) | PASS | 1315 passed, 0 failed, 1 skipped, re-run by me. The build recorded the same, and 1316 in the results file counts the skip |
| Create Envelope contract test | PASS | [61 of 61](../../src/tests/solutions/AcceptanceEnvelopeContract.Tests.ps1#L106) |
| Test can fail (mutation, by me) | PASS | Referee routing 2 put back to 1: 1 failure. Access code taken from the first six digits: 4 failures. Phone threshold loosened from 6 to 3: 1 failure. Source restored byte for byte |
| Source gates | PASS | `run-source-gates.py`, 17 of 17 |
| Flow language, assumption markers, pipeline config, improvement log, work items | PASS | Each re-run by me, section 5 |
| Package content | PASS | Both zips carry the working-tree flow. Section 2, row 12 |
| Integration, End-to-End, Security (live) | **NOT RUN** | Need DocuSign. Section 3 |
| Platform Contract | **OPEN** | `A-DS-14` to `A-DS-18` |
| Verification level | **V2 (packaged)** | Highest level executed. Not V3, V4 or V5 |
| Accessibility, Performance | Not applicable | No screen changed, no threshold in scope. The DocuSign rate limit (about 20 grants in a minute) is measured by the `3.7` bulk test |
| Cross-OS | PASS (static) | No script was added. Run on macOS only; the CI runner OS was not exercised |

---

## 2. Requirement Coverage

All results below are static unless stated. "Static" means the flow's own expressions were executed by the test evaluator or read from the packed JSON, not run against DocuSign.

| # | Requirement | Result | Where I looked |
|---|---|---|---|
| 1 | Envelope created as a draft, send is the last DocuSign call, write-back only after the send | PASS | [draft](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L699), [send](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L1567), [write-back](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L1593). I worked out the action order from the `runAfter` chain myself: 11 DocuSign calls in the TAD order, then one write |
| 2 | Each signer bound to their own role; referee second | PASS | [applicant](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L927) routing 1, [referee](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L969) routing 2. Mutation fails a test |
| 3 | Referee access code is the last six digits of the phone, digits only; fewer than six stops the run before DocuSign | PASS | [code](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L449), [check](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L387), [verification](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L1011). The check runs before the draft exists. Both mutations fail tests |
| 4 | Per-signer subject and body from two settings rows; subject at most 100 characters; referee body states the rule, never the digits | PASS | Rows exist in [DEV](../../provisioning/deploymentSettings/dev-scoring-settings.json#L248), [TST/ACC](../../provisioning/deploymentSettings/test-settings.json#L596) and [PRD](../../provisioning/deploymentSettings/prd-settings.json#L656). I parsed them: subjects 46 and 66 characters, no digits in either body. PRD is withheld behind a declared pending token on purpose. Wording is provisional |
| 5 | Every template tab except signature, full name and sign date is filled, read back, and an unmapped or unfilled tab stops the run before the send | PASS (modelled) | [fill](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L1221), [check](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L1426). The tests run a 31-tab model of the reviewer's template under both role readings. I did not rebuild that model; I ran it. The real template has not been read by anything |
| 6 | The grant-agreement checkbox is never ticked by the flow | PASS | Sent as `false` under either role, per the Dev Summary mapping table, asserted by the same tests |
| 7 | A failed run names the orphaned draft so it can be deleted | PASS | [failure switch](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L1646), [alert](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L1779). The alert reads the envelope id from a variable set right after the draft exists |
| 8 | Action names are unique across the whole flow, including every Switch case | PASS | The platform treats names as flow-wide at import, a known past failure. I counted 72 actions: 0 duplicates, 0 case-insensitive duplicates, 0 broken `runAfter` links, every `InitializeVariable` declares one variable, no `SetVariable` reads itself |
| 9 | No personal value readable in run history | PASS (static) | The closure test in [this suite](../../src/tests/solutions/AcceptanceEnvelopeContract.Tests.ps1#L542) passes. I listed every action's secure settings: every action that reads or builds from the referee or applicant data carries them (the connector reads, the phone and tab expressions, the DocuSign recipient and tab calls). Whether a `Compose` with secure inputs also hides its output is the project's standing assumption, not measured here |
| 10 | Reminders are set on the draft, before the send | PASS for order, **GAP** for content | [reminder call](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L1538). The cadence expression ([L1515](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L1515) onward) is unchanged from before, and no test executes it, with the row seeded or with the `[3,7]` fallback. Low risk: it is simple arithmetic, and the reviewer accepted its result |
| 11 | The tab set is wider than TAD section 5.8 step 2 | Reported, not resolved | The reviewer's verbatim override is in the [Dev Summary](../development/revitalise-grant-automation-dev-summary.md#L12213). The TAD has not been edited; the Dev Summary says the difference is routed to architect-agent. Tests follow the override |
| 12 | The packed artifact holds this flow | PASS | `cmp` of source against the unmanaged zip and the managed zip: identical both times. Warning: the flow is **not in the recorded source commit**, see 7.2 |
| 13 | WI-0108 (Required fields) and WI-0110 (no reassignment) | Not testable | Template or account settings, section 3 step M4 |

**Defects raised: none at P1 or P2.** Two P3 documentation points are in section 4.

---

## 3. What the DEV run must show (closes the contracted deliverable of `3.2` and `3.5`)

The pipeline already carries the steps: the [template check](../../config/revitalise-grant-automation-pipeline.yml#L1385) and the [R1 to R6 run](../../config/revitalise-grant-automation-pipeline.yml#L1402). Order matters because an unmanaged import switches every flow off, so turn this one on before R1, with test identities only.

| Step | Check | Closes | Pass looks like | A failure means |
|---|---|---|---|---|
| M4 | Open the template: each field's Required box and Data Label; the reassignment option | `A-DS-18`, WI-0108, WI-0110 | Labels equal the names the flow matches | Reviewer sets them; labels that differ are caught at run time by the alert |
| R1 | Create a grant; read the draft | `A-DS-14` | Draft holds both roles | Binding fails; nothing sent |
| R2, R3 | Read the tabs after the fill | `A-DS-15`, `A-DS-16` | Every in-scope tab holds its value, including the referee's | Read-back stops the run naming the tab. If it keeps naming referee tabs, the TAD's option B is the fallback |
| R5 | Referee phone with spaces and a `+44` prefix; forward the email; open the link | `A-DS-17` | The link asks for the six digits; a five-digit phone stops the run before DocuSign | Format rejected, or no prompt |
| R6 | Reminders on a draft; send | `A-DS-16` | Reminders attached, email arrives only at the end | Reminder call refused; nothing sent |
| After | Compare each tab's `recipientId` with the role name returned for it | `A-DS-15` (which role holds which placeholder set) | A record only; matching works either way | None |
| After | Delete the draft(s) any failed run left | Orphan risk | None left | Personal data held in a draft |

Not run and not claimed: any DocuSign behaviour, the live access-code prompt, email delivery, any DEV flow run.

---

## 4. Defects Raised

| ID | Severity | Description | Linked test |
|---|---|---|---|
| T-1 | P3 | Dev Summary register row `A-DS-5` still names the removed action `Create_and_send_the_envelope` in its Where column, [row](../development/revitalise-grant-automation-dev-summary.md#L6511). The marker gate passes because it checks the file, not the action | Section 5, assumption markers |
| T-2 | P3 | The Vite size warning from the **cards** code-app build is accepted in the manifest by citing another feature's Dev Summary, and this feature's Dev Summary has no row for it. The amended tool-warning rule asks for a row here. The pack warning (now 17 lines) is triaged in prose, [Dev Summary](../development/revitalise-grant-automation-dev-summary.md#L7814), which does record it with a rationale | Manifest `warnings_detail` |

Neither blocks. Earlier reports passed the same condition on the manifest alone; I am recording rather than failing it, and say so in section 5.

---

## 5. Constraint & Compliance Verification

I assessed the rows this change exercises. The build recorded its own check as PASS; I did not re-derive every in-scope row.

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-DOM-004](../../constraints/domain/domain-constraints.md#L37) | Personal data not exposed in logs | PASS (static) | Closure test, row 9. Live check is the run history after R1 |
| C-DOM-030, C-DOM-031, C-DOM-032 | Special-category register | PASS | `no-special-category-data-in-scoring` and `domain-invariants` in the 17 of 17. No column was added or secured |
| C-TECH-001 | No secrets in tracked files | PASS | Settings rows and wording read; the secret-scan is a build step run by build-agent, not re-run by me |
| C-TECH-004 | Input validation | PASS | The referee phone, names, emails and settings rows are executed on chosen inputs in the contract test's guard cases |
| [C-TECH-006](../../constraints/technology/technology-constraints.md) | Authentication on the signing route | **UNEVALUABLE LIVE** | The control (access code) exists in source. Whether DocuSign enforces it is R5 |
| C-TECH-007 | Test identities only | PASS (static) | The pipeline step says test identities; I did not watch it run |
| C-TECH-047 | Ids are environment variables | PASS | `no-hardcoded-environment-values` passes; the account and template ids are `parameters(...)` |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Platform contract register | PASS | `verify-assumption-markers.py`: 56 OPEN rows checked, each carries its marker, 0 markers without a row. `A-DS-14` to `A-DS-18` appear in source 5, 3, 7, 2 and 0 times in the flow, plus `A-DS-18` in the flow notes |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Verification level | PASS | Manifest claims V2 and I confirm V2 by unzip. Dev Summary section 11 still says V1 and "not packaged" because it was written before the build; V2 is the higher, confirmed level |
| [C-TECH-055](../../constraints/technology/technology-constraints.md#L110) | Tool warnings triaged | PASS with note | Manifest: 6 warnings, 6 accepted, 0 untriaged. See T-2 |
| C-TECH-060 | Text length limits | PASS | `field-length-limits` in the 17 of 17 |
| [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) | OPEN assumptions block deployment | **OVERRIDE NEEDED** | `A-DS-14` to `A-DS-18`. See 7.1 |

```
CONSTRAINT CHECK
Domain   HARD: 4 passed / 4 evaluable of 4 assessed     |  violations: NONE
                                                        |  unevaluable: NONE
Domain   SOFT: 0 assessed                               |  warnings:   NONE
Tech     HARD: 8 passed / 8 evaluable of 10 assessed    |  violations: NONE
                                                        |  unevaluable: C-TECH-006 (live), C-TECH-058 (override)
Tech     SOFT: 0 assessed                               |  warnings:   NONE
Overall: WARN
```

Commands I ran, all from the repository root: `Invoke-Pester src/tests` (1315 passed, 0 failed, 1 skipped); `run-source-gates.py` against the build config (17 of 17); `verify-assumption-markers.py` (PASS); `verify-pipeline-config.py` on the pipeline config (exit 0); `verify-flow-definition-language.py` on the solution (OK); `verify-improvement-log.py --check` (OK, 1028 entries); `verify-work-items.py --check` scoped to WI-0107 to WI-0111 at `built` (OK). `verify-wbs-chain.py` refused to run because the derived task-state file is older than 62 contract and solution files; I did not regenerate it, since regenerating rewrites tracked state outside this dispatch.

---

## 6. Provisioning Verification

| Item | Expected | Verified via | Result |
|---|---|---|---|
| Settings rows `AcceptanceEmailApplicant` and `AcceptanceEmailReferee` | In DEV, TST/ACC and PRD files, valid JSON `{subject, body}` | Parsed all three files | PASS for DEV and TST/ACC. PRD holds a declared pending token, accepted until 2026-12-11 |
| The rows exist in a live environment | Seeded by the DEV settings seed | Not run | **NOT VERIFIED.** The flow stops, naming the row, if they are absent |
| Template Required flags, reassignment off | Set per environment | Not readable by me | **NOT VERIFIED.** Manual step M4 |

No site, team, app registration, group team or app sharing changed.

---

## 7. Platform Contract & Verification-Level Audit

### 7.1 Assumption register closure

The precondition for every row below is the same, and I checked it first: **the rev 15 flow must be imported into DEV and turned on.** It does not exist yet (the DEV import has not been run), so none of these can be closed by anything I can do. The DEV environment exists and is the means of closing them, which is why section 7.1 needs your override rather than a deferral.

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| `A-DS-14` | Draft carries both roles; the recipient update fills them rather than adding signers; the draft sends as filled | OPEN | DEV import, then R1 and R5 | No | No | OPEN |
| `A-DS-15` | Tab read carries label and recipient id; prefill tabs flagged; one document | OPEN | DEV import, R1 and R4 | No | No | OPEN |
| `A-DS-16` | Update accepts the read's own tab types; language string accepted; reminders work on a draft | OPEN | DEV import, R2, R3, R6 | No | No | OPEN |
| `A-DS-17` | A six-digit code is accepted and asked for | OPEN | DEV import, R5 | No | No | OPEN |
| `A-DS-18` | Template reassignment setting carries into the envelope | OPEN | M4, M6 | Template not yet read | No | OPEN |
| `A-DS-2`, `A-DS-12` | Old `SendEnvelope` shapes | CLOSED / WITHDRAWN | None, the action is gone | n/a | Confirmed gone by test | PASS |
| `A-DS-4` | Referee name tabs | CLOSED by reviewer decision | None | n/a | Name is split at the first space in source | PASS |

Orphans: none. **I could not re-check the evidence behind the connector's operation ids.** The Dev Summary and TAD rate them as seen in the reviewer's saved test flow, and that export is not in this repository.

### 7.2 Verification levels achieved

| Component | Level claimed | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Create Envelope flow | V2 (build manifest); V1 (Dev Summary) | **V2** | Unzipped both zips, flow identical to source; build packed 99 of 100 steps | PASS |
| Settings rows | V1 | V1 | Parsed; not seeded | PASS |
| Flow run on DocuSign | none | none | Not run | **PARTIAL** |

- Idempotency: DEV re-import not performed. Result: NOT RUN.
- Human open-and-save (V4): **must not be performed** on this solution flow. The Dev Summary records the risk and replaces it with the R1 to R6 run. Result: N-A by design.
- Cross-OS: no new script. Result: PASS (static).
- Warnings triaged, diagnostic components removed: PASS with note, section 4. No diagnostic component was added.
- **Provenance warning.** The manifest says the source commit is `7cd080c` with 25 uncommitted paths. That commit still holds the old single-send flow; the rev 15 flow, its settings rows and this work are uncommitted. The artifact is correct; a build from a clean checkout would be the old flow.

---

## 8. Recommendations

1. Give the DEV override (decision 1), commit the rev 15 changes first so the DEV run is of a recorded commit, then run section 3.
2. Fix T-1 and T-2 when next in the Dev Summary; add a test that executes the reminder cadence with the row seeded and with the fallback.
3. Out of scope but noticed: the Dev Summary's own flag that WI-0009's evidence has drifted predates this work and I did not touch it. The tree also carries uncommitted trustee-portal and intake-flow changes; none is in this artifact's flow, and I tested none of them.

---

## What you need to decide

**Do you give `OVERRIDE A-DS-14, A-DS-15, A-DS-16, A-DS-17, A-DS-18` for DEV only?**

**Problem** — Five assumptions are open and can only be closed by importing the flow into DEV, which the open-assumption rule blocks without your override.
**Suggested fix** — Reply with the override and the reason "closed by the DEV import and the R1 to R6 run", for DEV only.
**What happens if you don't** — Nothing can be sent to DocuSign from this build, so the Create Envelope rebuild stays at packaged and the `3.5` result stays unwritten.
[C-TECH-058](../../constraints/technology/technology-constraints.md#L128)

---

**How does an envelope get issued after a missing phone or settings row is fixed?** (carried from the Dev Summary, still open)

**Problem** — The flow starts only when a grant is created, so after a stop nothing issues the envelope.
**Suggested fix** — Ask architect-agent to name the route in the TAD (a re-issue trigger, or a DEV test of run-history Resubmit).
**What happens if you don't** — A grant stopped by a missing referee phone stays at Awarded with only the manual print-sign-scan route.
[the check](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L387)

---

Verification: 1315 Pester tests passed (0 failed, 1 skipped), 17 of 17 source gates, 3 of 3 mutations caught, both zips match source. **Not verified:** any DocuSign behaviour, the real template, email delivery, the live access-code prompt, seeded settings rows in any environment, the identity of the one Medium Solution Checker finding, and the CI runner OS.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | | | |

Digest regenerated: NO — nothing was appended.
