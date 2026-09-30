# Test Report — Revitalise Grant Automation (WI-0052 nav order, Round Statistics fix, run-history masking, flow re-read step; wbs:6.8 / 4.2 / 4.3)

**Feature Slug:** revitalise-grant-automation
**Artifact:** build/artifacts/revitalise-grant-automation-20260930-2/
**Date:** 2026-09-30
**Status:** PARTIAL
**WBS:** `6.8` (WI-0052 nav order), `4.2` / `4.3` (intake and Round Statistics flows). Deliverables `4.5` and the other test-result tasks are not claimed complete by this report; see 7.2.
**Target:** DEV deploy only, no promotion.

---

## Summary

**PARTIAL: the artifact contains exactly what you listed and nothing you did not list except one item, and it is safe to import to DEV. Nothing in it has run on the platform yet.** All automated suites are green (Pester 1245 passed / 0 failed / 1 skipped; code app 798 of 798; 16 of 16 source gates). The unlisted item is that the intake flow (and the scoring and reminders flows) also get a rewritten failure path, not only masking.

**Waiting on you:** approve the import to DEV. After it, the new flow re-read step should report zero differences, and three things still need a human or a live run: a designer open-and-save on the changed flows, one real intake submission, and a look at run history to see the masking.

---

## What was verified

1. **The packaged flows are byte-for-byte the working tree.** I unzipped [RevitaliseGrantAutomation.zip](../../build/artifacts/revitalise-grant-automation-20260930-2/RevitaliseGrantAutomation.zip) and compared all 10 workflow definitions to source: identical, including the same set of secured actions in each. The code app bundle in the artifact is `index-DxpBAQa-.js`, the one the manifest names.
2. **The change to DEV is exactly five flows, and nothing else.** I ran the new [flow re-read step](../../scripts/verify-live-flow-definitions.py) read-only against DEV, twice. Against current source it reports 5 flows differ (1001, 1002, 1005, 1006, 1007). Against the source at HEAD it reports only 1005 differs. So live DEV is HEAD for 1001, 1002, 1006 and 1007, which includes the intake flow you verified yesterday. 1005 is the missing Round Statistics fix, as you already knew. The five that differ are the five this artifact changes.
3. **Nav order (WI-0052).** The new test [orders the bar with Group applications FIRST](../../src/code-apps/trustee-review-portal/src/App.test.tsx#L173) passes in the 798-test run. Its assertion is the full order: Group applications, Round overview, Applications list. The test post-dates the artifact, but `App.tsx` is unchanged since HEAD, so the bundle matches.
4. **Masking (1006, 1007).** [AcceptanceEnvelopeContract.Tests.ps1](../../src/tests/solutions/AcceptanceEnvelopeContract.Tests.ps1) ran in the Pester pass. I also wrote an independent check outside that file: across all 10 flows, no action whose own inputs name `rev_refereename`, `rev_refereeemail`, `rev_refereephone`, `rev_fullname` or `rev_email` lacks `secureData`. Result: none unsecured.
5. **Failure-path rewrite is structurally sound.** In 1001 (3 cases) and 1002 (4 cases), every Switch case value is a real immediate child of the scope that `Find_the_failed_action` reads, and every new Query reads `result()` of that same container. All Set-detail actions and a default branch exist. I checked this by parsing the JSON; it has not run.

---

## What this lets me claim, and what it does not

**Can claim: V2 for the artifact, V1 for the source, plus V3-equivalent knowledge of the delta**: the live-vs-HEAD comparison in item 2 is a real read of DEV, so the size of the change is measured, not assumed.

**Cannot claim: V3, V4 or V5 for anything in this artifact.** It has not been imported. Specifically not observed: that DEV run history shows redacted values; that any of the new Switch cases fires on a real failure; that the changed flows open and save in the designer; that a real intake submission still succeeds.

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit: Pester, re-executed by me on this tree (`src/tests/Invoke-Tests.ps1`) | 1246 | 1245 | 0 | 1 |
| Unit: code app vitest, re-executed | 798 | 798 | 0 | 0 |
| Integration: source gates (`run-source-gates.py`) | 16 | 16 | 0 | 0 |
| Integration: zip vs source, 10 workflows | 10 | 10 | 0 | 0 |
| Integration: live DEV vs source and vs HEAD (read-only) | 2 | 2 | 0 | 0 |
| Regression: full Pester and vitest suites above | included | included | 0 | 0 |
| Security: independent personal-column closure over all flows | 10 | 10 | 0 | 0 |
| Platform Contract: Switch cases match real container names | 2 flows | 2 | 0 | 0 |
| End-to-End: real intake, real failure, run-history look on DEV | 0 | 0 | 0 | all; needs DEV import |
| Accessibility | n/a | n/a | n/a | N/A: nav order only, no new element or control |
| Performance | n/a | n/a | n/a | N/A: no NFR threshold touched |
| Provisioning | n/a | n/a | n/a | N/A: no provisioning file differs; carried forward from [20260928-1](revitalise-grant-automation-test-report-20260928-1.md) |

## 2. Requirement Coverage

| ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| WI-0052 (wbs:6.8) | Group applications first in the trustee portal nav | App.test.tsx order test, 798-test run | PASS at V1; not seen in DEV |
| wbs:4.3 | Round Statistics figures compute when the source list is empty | `RoundStatisticsContract.Tests.ps1` in the Pester run; live DEV lacks the fix per the re-read | PASS at V1; PARTIAL overall until imported |
| NFR-012 / C-DOM-004 | No personal value readable in run history | Contract test plus my closure check | PASS at source; PARTIAL: not seen in a DEV run |
| wbs:4.2 / 4.3 | Intake flow keeps working | Live DEV equals HEAD for 1001; delta is failure path only | PARTIAL: no post-import submission yet |

## 3. Failed Tests

None.

## 4. Defects Raised

None new at P1 or P2. Three observations, none blocking this DEV import:

| ID | Severity | Description | Linked |
|---|---|---|---|
| Obs-1 | P3 | The handoff lists these changes as masking, but 1001, 1002 and 1007 also get a rewritten failure path (`Describe_the_failure` becomes a Switch or gains an If), with no Dev Summary revision and no runtime test. Logged as IMP-0968. | [1001 Switch](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L3086), [1002 Switch](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVScoringCalculateAndFlag-8F1C2A44-1002-4B7A-9E21-0A1B2C3D4E02.json#L900), [1007 If](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceRemindersEscalation-8F1C2A44-1007-4B7A-9E21-0A1B2C3D4E07.json#L388) |
| Obs-2 | P3 | The scoring flow's create trigger has no `secureData`, so the application row (including referee columns if set) is still readable in run history for that flow. Already logged as IMP-0966; it means the masking you approved is complete for the DocuSign flows and intake, not for 1002 or 1009 triggers. | [IMP-0966](../../logs/improvement-log.jsonl#L962) |
| Obs-3 | P3 | `verify-flow-definition-language.py --selftest` fails today, because the failure-path rewrite cleared the last check-7 exception it depends on. The build step runs the plain gate, which passes, so the build is unaffected. Already logged as IMP-0967; the three entries in `config/flow-check7-exceptions.json` are now dead waivers. | [IMP-0967](../../logs/improvement-log.jsonl#L963) |

## 5. Constraint & Compliance Verification

Scope for test-agent: 6 HARD domain rows and 28 HARD + 1 SOFT technology rows. This diff touches run-history masking, flow failure paths, one UI ordering, a lockfile and one pipeline step. I evaluated the rows those areas govern; the rest are carried forward from [20260928-1 §5](revitalise-grant-automation-test-report-20260928-1.md), because none of the areas they govern is in this diff.

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-DOM-004](../../constraints/domain/domain-constraints.md#L37) | Personal data not written to application logs | PASS for the four flows changed; residual noted | Closure check item 4: no unsecured action names a personal column. Residual: the failure-detail text (action name, code, platform message) is set unsecured and can reach run history; pre-existing, accepted earlier, not widened here. Triggers of 1002 and 1009: Obs-2 |
| [C-TECH-001](../../constraints/technology/technology-constraints.md#L34) | No hardcoded secrets | PASS | `no-hardcoded-environment-values` source gate; lockfile change is three version bumps only |
| [C-TECH-014](../../constraints/technology/technology-constraints.md#L52) | Coverage threshold | PASS | Build step `coverage-threshold` ran in the build; Pester unchanged at 1245 passed |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Platform contract register; no orphan artefact | PASS | No new hand-authored contract; changes sit inside registered flows. Register unchanged, 9 OPEN |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Level claimed equals level confirmed | PARTIAL | Dev Summary claims V1; I confirm V1 and V2. No V3 or above, see 7.2 |
| [C-TECH-054](../../constraints/technology/technology-constraints.md#L109) | Pipeline scripts run on the runner's OS | PARTIAL | The new step ran on macOS here. It shells to `pac`, which the runner must have; no Linux run was done |
| [C-TECH-055](../../constraints/technology/technology-constraints.md#L110) | Tool warnings triaged | PASS | Manifest: 5 warnings, 5 accepted with citations, 0 untriaged |
| [C-TECH-057](../../constraints/technology/technology-constraints.md#L127) | Gates proven able to fail | PASS | New re-read step selftest passes (can fail); the flow-definition-language plain gate passes its 29-check selftest; the wrapper selftest failure is Obs-3 |
| All other in-scope rows | | PASS (carried forward) | No file in their area differs from the last approved cycle |

A HARD constraint failure is a P1 defect. None found.

## 6. Provisioning Verification

No file under `provisioning/` changed. Carried forward from [20260928-1 §6](revitalise-grant-automation-test-report-20260928-1.md).

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

Dev Summary section 10 is unchanged by this cycle: 9 OPEN rows, the same 9 as at the last approved cycle ([verification summary](../development/revitalise-grant-automation-dev-summary.md#L11705)). The closing precondition of the rows this artifact could affect (flow save and run behaviour) is "this artifact imported to DEV", and it does not exist yet; the import is the means of closing them, so they are not a defect at this gate. No orphan artefact.

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| Flow-family rows (9 OPEN) | Designer accepts and saves the changed flows; runs behave | OPEN | This artifact imported to DEV, then a human open-and-save | No | Not closeable before import | OPEN, expected |

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary section 11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Trustee portal nav order (WI-0052) | V1 | V1 (order test), V2 (bundle in artifact) | Item 3 | PARTIAL: not V3 |
| Round Statistics flow fix (1005) | V1 | V2; live DEV verified to lack it | Item 2 | PARTIAL: not V3 |
| Run-history masking (1006, 1007) | V1 | V2 | Items 1, 4 | PARTIAL: redaction not observed |
| Intake and scoring failure path (1001, 1002) | not claimed | V2 | Item 5 | PARTIAL: never executed; see Obs-1 |
| Flow re-read step | V1 | V1; ran read-only against DEV successfully, produced the expected findings | Item 2 | PASS for the read itself |
| npm audit lockfile | V1 | V1 (`npm audit --audit-level=high` exit 0 per Dev Summary; vitest 798 green here) | Section 1 | PASS |

- Idempotency: not run; no import yet. Result: `N/A`
- V4 designer open + save: not performed. Owner: reviewer. Result: `OPEN`
- Cross-OS (C-TECH-054): see section 5. Result: `PARTIAL`
- Warnings triaged (C-TECH-055) and diagnostic components removed (C-TECH-056): `PASS`

## 8. Recommendations

1. **Import to DEV, then run the re-read step again.** Expected result is 0 differences; any difference, or a `modifiedon` later than the import, means something else wrote to a flow.
2. **After the import, do three human steps:** open and save 1001, 1002, 1006 and 1007 in the designer; submit one real intake and confirm the application is created; open a run of 1006 and confirm the values show as redacted.
3. **Decide separately** whether the two unsecured Dataverse row triggers (Obs-2) should be masked. They are outside this artifact's scope.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0968 | `handoff-understates-artifact-content` | friction | A handoff that lists an artifact's contents must be reconciled against the workflow diff, because an unlisted failure-path rewrite ships under the reviewer's approval of a different change. |

Also confirmed still open and relevant, not re-logged: IMP-0966 (unsecured row triggers) and IMP-0967 (selftest depends on a live defect).

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`
