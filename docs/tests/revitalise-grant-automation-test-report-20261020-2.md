# Test Report — Revitalise Grant Automation, SDD Amendment A-10 rev 2 / TAD rev 26 / ADR-079

**Artifact:** `build/artifacts/revitalise-grant-automation-20261020-2/` (packed from a dirty tree, 39 uncommitted paths, per its manifest)
**Date:** 2026-10-20  **Tester:** test-agent (standard tier)  **WBS:** 2.4, 2.7 (Test results deliverables feed task 2.8)
**Items:** WI-0033, WI-0036, WI-0047, WI-0117 to WI-0124. WI-0125 is out of scope (needs a DEV run).
**Result: PARTIAL.** No defect found. Highest level reached is V2 (packaged) plus V1 executed tests. Nothing was deployed or run on the platform.

## 1. Test Summary

| Layer | Result | Evidence |
|---|---|---|
| Unit / Integration (static, evaluator-executed) | PASS | Full Pester suite re-run by test-agent: 1418 passed, 0 failed, 1 skipped (`src/tests/Invoke-Tests.ps1`). Scoped files re-run alone: ScoringInvariants 164, ScoringOriginalAsks 4, DeploymentSettings 49, DataverseScripts 87, all green |
| Artifact fidelity | PASS | Both zips (unmanaged and managed) contain the new flow actions `Derive_eligibility_rules`, `Parse_amount_limits`, `Compose_reason_lines`, the switch guard and all seven new setting names; the unmanaged zip's flow is byte-identical to source |
| Source gates | PASS | `run-source-gates.py` 19 of 19 (exit 0); flow-definition-language OK (11 flows, incl. check 11); `verify-guid-syntax` and `verify-tad-coverage` OK; assumption markers and register PASS; improvement log schema OK |
| Build / pipeline preflight | PASS | Build run result: build-config preflight 102 steps, pipeline preflight 133 steps. Solution Checker: 0 critical, 0 high, 1 medium (standing REVSafeguardingActionCompletion row, equal to the previous build) |
| Regression, Automation #5 (narrative scrubbing) | PASS on static evidence | Same 1418-test run covers the narrative tests. Shared files (`seed-settings.ps1`, the three settings files, `Entity.xml`) were edited by both changes; no failing test. Not run on the platform |
| Security | PASS (static) | Flow reads no special-category column: no reference to employment status, additional amount or exceptional-funding detail (grep count 0 each). New reads are amount, break type, exceptional tick, savings answer, plus the existing benefits read confined to the income flag |
| Accessibility, Performance | N/A | No screen changed; one added Compose chain in a create-triggered flow |
| Cross-OS | PASS | Tests ran on macOS here; CI runs the same suite on its own runner (not executed by this agent) |

## 2. Requirement Coverage (A-10 worked examples, run through the flow's own expressions)

| Requirement | Evidence | Result |
|---|---|---|
| FR-014 five rules, any one rejects | `Derive_status` is `or()` of the five rule outputs, then the band | PASS |
| FR-102 amount (strictly greater; £500 / £100 by type; tick lifts; blank does not reject; additional amount never compared) | `Derive_eligibility_rules.amount`; examples 1 to 5, 14, 15 and boundary cases executed | PASS |
| FR-015 income (benefits Yes never rejects; blank band not rejected; employment not read) | `Derive_income_flag` unchanged, rule reads value 2 only; examples 6 to 9, 16, 17 | PASS |
| FR-103 savings, FR-104 prior funding, each with a switch | Rule reads switch and answer; examples 10, 11, 18 | PASS |
| FR-017 every parameter in `rev_setting` | Seven rows seeded create-only in DEV, TST/ACC and PRD, defaults match the SDD (20, 21 to 30, 25,000, 500/100/100/500/500, true, true); four older FR-017 rows now create-only | PASS |
| FR-105 every reason, in order, under 1,000 characters | `Compose_reason_lines`; example 11 four lines in order; longest-reason test | PASS |
| FR-022 withhold, no rule fires, no reason | Limits parsed after the withhold gate; only `Write_score_and_status` names the reason column (examples 12, 13 structural) | PASS |
| FR-016 / C-DOM-030 no special-category input | See Security row | PASS |
| US-006 AC-4, 5, 7, 13 to 18, 20 | Covered by the above | PASS (static) |

Examples 1 to 11 and 14 to 19 are executed with exact reason text. 12 and 13 are structural by design.

## 3. Failed Tests
None.

## 4. Defects Raised
None (no P1 to P4). Observations, not defects: the unmanaged option-set label for Holiday accommodation carries a parenthetical ("Holiday accommodation (hotel, cottage, caravan, holiday park)"); the reason text uses the SDD's short label, which matches the approved worked examples. Reasons use hard-coded labels in `Compose_reason_labels`, so a renamed option needs that Compose edited.

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-DOM-030 | No special-category column influences an automated outcome | PASS | Flow reads listed above; employment, additional amount, funding detail unread; flow-definition check 11 OK |
| C-DOM-001 to 004, 010 to 012, 020 to 022, 031 to 033 | Classification, audit, access, secured columns | PASS | Dev Summary rev 26 states no column secured, added or changed; `rev_autorejectreason` is `IsSecured=0`, shown on the admin form only (reviewer ruling 2026-10-19); register unchanged |
| C-DOM-005 | Subject access path | SOFT, carried, accepted by reviewer 2026-10-20 | Dev Summary rev 26 section 7 |
| C-TECH-052 | Hand-authored contracts have a register row | PASS | A-FLOW-18 to A-FLOW-22 recorded; markers verified by `verify-assumption-markers` |
| C-TECH-053 | Level reported as executed | PASS | Dev Summary section 6 claims V1 only; manifest claims V2 |
| C-TECH-055 | Tool warnings triaged | PASS | Manifest: 5 warnings, 0 untriaged |
| C-TECH-058 | OPEN assumptions block deployment where closable | PASS for DEV | Each of A-FLOW-18 to A-FLOW-22 names a run in DEV as its own check, so it does not block the DEV deploy; each blocks every environment after DEV until closed |
| Remaining C-TECH rows scoped to test-agent | Build gates | PASS | Rely on the build run's gate results above; not individually re-derived |

## 6. Provisioning Verification
Seven new `rev_setting` rows: confirmed in source and in the three settings files (48 rows each). **Not confirmed in any live environment.** Deploy order matters: `seed-settings.ps1 -Env dev` must run before the solution import, or the new flow stops every new application (pipeline config has the pre-import step; preflight PASS). PRD seed still stops on its pending OQ-001 to OQ-003 tokens, by design.

## 7. Platform Contract & Verification-Level Audit

### 7.1 Assumption register closure

| ID | Claim | Status |
|---|---|---|
| A-FLOW-18 | `formatNumber` 'N2' and 'N0' render `1,250.00` / `25,000` on the tenant | OPEN (DEV run, wording only) |
| A-FLOW-19 | Trigger delivers amount as a JSON number, blank as null | OPEN (DEV run) |
| A-FLOW-20 | Resubmitting a failed run re-reads current settings | OPEN (DEV run) |
| A-FLOW-21 | `int('')` and `int('£150')` throw, stopping scoring with an alert | OPEN (DEV run) |
| A-FLOW-22 | `join(skip(split(...),1),NL)` yields `''` for `''` | OPEN (DEV run) |

A-FLOW-19 carries the highest risk to correctness: if a blank amount arrives as something other than null, the amount rule could misfire. A-FLOW-22 matters for every Auto-pass and Borderline write.

### 7.2 Verification levels achieved

| Component | Claimed | Confirmed | Note |
|---|---|---|---|
| Scoring flow and rules | V1 | V1, and V2 (packaged in both zips) | Not imported (V3), not run (V5) |
| Seed rows | V1 | V1 | Not run against any environment |
| Pipeline wording and pre-import step | V1 | V1 | Preflight only |

Per the Fail Conditions, a component accepted at V2 and not yet executed gives PARTIAL, never PASS. WI-0125 is the step that closes it.

## 8. Recommendations
1. Approve as PARTIAL and proceed to DEV deployment only after the other session's deploy of `revitalise-narrative-scrubbing-20261019-1` finishes, so the older build does not land on top of this one.
2. Run the Dev Summary section 4 DEV checks (a) to (c) as WI-0125; close each row with the observed text.
3. Optional: the manifest says the artifact was packed from a dirty tree; commit before the deploy so the source commit identifies what shipped.

## Approval
**APPROVED (PARTIAL) by Xander Lykopoulos, 2026-10-20**, reviewer's words: "Approved". No commit was requested; the artifact stays as packed. A-FLOW-18..22 remain open for the DEV run (WI-0125).

## Findings Logged
None.
