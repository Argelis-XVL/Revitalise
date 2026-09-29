# Test Report — Revitalise Grant Automation (createArray() zero-argument fix, wbs:4.2/4.3)

**Feature Slug:** revitalise-grant-automation
**Artifact:** build/artifacts/revitalise-grant-automation-20260928-1/
**Date:** 2026-09-28
**Status:** PARTIAL
**WBS:** `4.2` (Appendix C field map, schema), `4.3` (intake flow). Neither task's test-results deliverable (`4.5`) is claimed complete by this report — see §7.2.
**Scope:** Focused, per test-agent's own discretion. This build's *only* content difference from the last-approved build ([revitalise-grant-automation-test-report-20260927-2.md](revitalise-grant-automation-test-report-20260927-2.md), PARTIAL, reviewer-APPROVED 2026-09-28) is the 19-occurrence `createArray()` → `json('[]')` fix inside one flow. Everything else in this cycle's constraint and provisioning scope is carried forward unchanged, not re-derived from scratch.

---

## Summary

**PARTIAL: the packaged fix is exactly what was claimed and nothing else changed, but it has not yet been imported to DEV in this form.** I unzipped both solution zips in this artifact and diffed them byte-for-byte against the last-tested build's zips: the only difference anywhere in the solution is 19 substitutions of `createArray()` for `json('[]')`, across the 14 actions the brief names, inside `REVIntakeWordPressToDataverse`. No other file changed between the two builds, despite 18 dirty working-tree paths existing outside this diff.

**Waiting on you:** re-dispatching pipeline-agent to import this build to DEV (V3), then the designer open-and-save (V4), then one authenticated POST exercising the fixed fallback path with an unticked optional checkbox (V5) — the exact condition that produced ERR-20260928-1022. I logged one finding (below) recommending a build-time gate for this class of defect, since nothing in the static suite would have caught it either before or after this fix.

---

## What was verified

1. **The build's own claim is correct: 0 occurrences of `createArray()`, 19 of `json('[]')`, in both zips.** ([unmanaged Workflows/REVIntakeWordPressToDataverse…json](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L692)). I unzipped `RevitaliseGrantAutomation.zip` and `RevitaliseGrantAutomation-managed.zip` from this artifact and grepped both copies of the workflow JSON directly — not the source tree — for the literal zero-argument `createArray()` and for `json('[]')`. Both zips: 0 and 19 respectively, matching the working-tree source exactly.
2. **The diff between this build and the last-tested one is exactly this fix, and nothing else.** I unzipped the previous artifact (`build/artifacts/revitalise-grant-automation-20260927-2/RevitaliseGrantAutomation.zip`, the build behind the PARTIAL/APPROVED report cited above) and ran a recursive `diff -rq` against this build's unmanaged zip: the only file that differs anywhere in the solution is the one workflow file. A line-by-line `diff` of that file shows 14 changed lines, each swapping `createArray()` for `json('[]')` inside an existing `coalesce(...)` — 19 occurrences counting the three-per-line case at [L2557](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L2557). The 14 actions named in the dispatch brief match: [Return_the_existing_reference_if_this_is_a_replay L680](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L680), [Derive_local_authority_status L1161](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L1161), [Derive_city L1308](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L1308), [Normalise_condition_profile_items L2098](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L2098), [Find_unmatched_condition_profile_labels L2178](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L2178), [Normalise_support_recipient_condition_profile_items L2199](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L2199), [Find_unmatched_support_recipient_condition_profile_labels L2279](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L2279), [Normalise_care_provided_type_items L2313](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L2313), [Find_unmatched_care_provided_type_labels L2393](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L2393), [Normalise_hear_about_us_items L2427](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L2427), [Find_unmatched_hear_about_us_labels L2507](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L2507), [Normalise_contact_method_labels L2528](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L2528), [Derive_preferred_contact_method L2549](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L2549), [Create_or_refresh_the_applicant L2725](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L2725). No entity, form, security-profile, provisioning setting, option set, or test file differs between the two builds — the other ~18 dirty working-tree paths listed in the pack-time manifest note carry no content change relative to what test report `20260927-2` already reviewed and the reviewer approved.
3. **Every substitution is semantically inert — no `createArray(x)` with an argument was touched.** The three `createArray('1')`/`createArray('2')`/`createArray('3')` calls on [L2557](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L2557) are left as-is (valid, one argument), and only the zero-argument fallback branches changed. `json('[]')` and `createArray()` are both empty-array literals in every other respect (`length()`, `first()`, `union()`, `coalesce()` all treat them identically), so this is a pure syntax correction with no logic change.
4. **The build's own automated evidence is consistent with the fix and unchanged elsewhere.** Pester: 1236 total, 0 failures, 1 skipped (`Pester` node attributes in [pester-results.xml](../../build/artifacts/revitalise-grant-automation-20260928-1/test-results/pester-results.xml)) — matching the manifest's 1235/0/1 claim. Coverage: 82.46% against an 80% threshold (`coverage-threshold` build step). The live Solution Checker (Advisor API, run against the managed zip) returned 0 Critical, 0 High, 1 Medium, 0 Low — no regression against the last checked build.
5. **No test in this repository exercises the code path this defect lived in.** I grepped `src/tests/`, `scripts/`, and `constraints/` for `createArray` — zero hits. `scripts/verify-flow-definition-language.py`'s own OK message (`flow-definition-language` build step) lists exactly what it checks: `select()`/`filter()`, alternate-key Row ID, nested `item()` on UpdateRecord, `InitializeVariable` placement, `Response`/`Skipped` shape, duplicate action names, and a failure-branch-exists check. Function-arity validity of `createArray()` is not on that list, and no unit test in `IntakeContract.Tests.ps1` supplies a null value to any of the 14 affected actions. This is why the defect reached DEV as a live Teams error card rather than a build failure — logged as a finding, §Findings Logged below.
6. **The reviewer's separate live-designer verification is corroborating, not substituting, evidence.** He applied the identical edit directly in the DEV designer and successfully POSTed a real intake payload (`docs/Import/2026-09-25-website-intake-payload-sample.json` via Bruno), creating a `rev_application` record with no error. That proves the *fix* works against the live trigger; it does not prove *this packaged artifact* is what will be running once imported — item 2 above closes that gap by diffing the actual zip contents, not by assuming the two copies match.

---

## What this lets me claim, and what it does not

**Can claim: V2 for this build (packaged, and content-diffed against the last build DEV already accepted at V3/V4).** The packaged fix is exactly the intended 19-substitution change and introduces no other difference.

**Cannot claim: V3, V4 or V5 for this specific artifact.** This build has not itself been imported to DEV — `verification_level` in [manifest.json](../../build/artifacts/revitalise-grant-automation-20260928-1/manifest.json) says so directly ("V2 — packaged; layout accepted by the packer and by the live Solution Checker's structural rules"). The reviewer's live-DEV test exercised a manually-edited designer copy of the flow, not this packaged zip. Until pipeline-agent imports this artifact, the packaged fix is verified by content-comparison and platform static analysis only, not by execution.

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit — build's Pester run (cited, re-derived from [pester-results.xml](../../build/artifacts/revitalise-grant-automation-20260928-1/test-results/pester-results.xml), not re-executed) | 1236 | 1235 | 0 | 1 |
| Integration — packaged workflow JSON vs 0/19 createArray()/json('[]') claim, both zips | 4 | 4 | 0 | 0 |
| Integration — this build vs last-tested build, full solution diff | 1 | 1 | 0 | 0 |
| Regression — no `createArray(x)` (argument form) touched | 3 | 3 | 0 | 0 |
| Regression — 0 diff outside the one flow file (entities, forms, security profiles, settings, tests) | 1 | 1 | 0 | 0 |
| Platform Contract — flow-definition-language / workflow-syntax build gates re-read for scope | 2 | 2 | 0 | 0 |
| End-to-End — authenticated POST against the null-fallback path, on THIS artifact (V5) | 0 | 0 | 0 | all — needs DEV import first |
| Security | — | — | — | N/A — no auth/caller-check code touched this cycle; carried forward from 20260927-2 |
| Accessibility | — | — | — | N/A — no UI/form change this cycle |
| Performance | — | — | — | N/A — no NFR threshold touched |
| Provisioning | — | — | — | Carried forward unchanged from 20260927-2 (no provisioning path in this diff) |
| Compliance — source gates re-read (constraint-verifiers, domain-invariants) | 2 | 2 | 0 | 0 |

## 2. Requirement Coverage

| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| FR-007/FR-008 | Application created from a website submission, incl. answers left blank | §"What was verified" items 1–3; not yet exercised end-to-end on this artifact | PARTIAL |
| FR-083 | Every applicant-entered answer stored, nothing form-generated stored | Unaffected by this diff — carried forward from [20260927-2 §2](revitalise-grant-automation-test-report-20260927-2.md) | PASS (carried forward) |

## 3. Failed Tests

None.

## 4. Defects Raised

None new. One P3 (D-05, "Who can trigger the flow?" unset in DEV) remains open from the prior cycle and is unaffected by this diff — see [20260927-2 Summary](revitalise-grant-automation-test-report-20260927-2.md).

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-TECH-004](../../constraints/technology/technology-constraints.md#L37) | User inputs validated before processing | PASS (unaffected by diff) | The fix changes only the empty-array literal on an already-existing `coalesce()` guard; the guard itself is unchanged |
| [C-TECH-014](../../constraints/technology/technology-constraints.md#L52) | Unit test coverage meets threshold | PASS | `coverage-threshold` build step: 82.46% vs 80% threshold |
| [C-TECH-052](../../constraints/technology/technology-constraints.md) | Platform Contract — hand-authored artefact has a register row | PASS | See §7.1 |
| [C-TECH-053](../../constraints/technology/technology-constraints.md) | Verification level claimed matches level confirmed | PARTIAL | See §7.2 — V2 only, for this artifact |
| All other in-scope HARD/SOFT rows (35 total scoped to test-agent) | — | PASS (carried forward, unchanged) | Content-diffed as identical to [20260927-2](revitalise-grant-automation-test-report-20260927-2.md), which re-ran the full suite and was reviewer-approved; this cycle's diff touches none of the areas those rows govern (security, PII, audit, provisioning, forms) |

A HARD constraint failure is a P1 defect. None found.

## 6. Provisioning Verification

No provisioning file differs between this build and the last-tested one (§"What was verified" item 2). Carried forward unchanged from [20260927-2 §6](revitalise-grant-automation-test-report-20260927-2.md) / item 6 of its Summary.

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

No Dev Summary §10 row references this fix — the change has no accompanying Dev Summary revision entry (the fix was applied directly by the reviewer in the live DEV designer and only afterwards packaged by build-agent from the working tree). This is itself a process gap, not a defect in the fix: nothing new is claimed in the register that needs closing, and no orphan hand-authored artefact was introduced (the changed lines are inside an already-registered flow).

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| n/a | No register row exists for this specific fix | — | — | — | Confirmed no orphan: change is inside an already-registered component | PASS |

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| REVIntakeWordPressToDataverse, the 19-substitution fix | Not claimed in Dev Summary (no revision entry) | V2 (packaged, content-diffed) | §"What was verified" items 1–4 | PARTIAL — not yet V3 |

- Idempotency: N/A — not yet imported, nothing to re-run against.
- V4 designer/editor open + save: NOT performed on this artifact. The reviewer's designer session edited and saved a *manually-modified* live copy, not this packaged one — those are not the same event.
- Cross-OS (C-TECH-054): N/A — no new CI/pipeline script in this diff.
- Warnings triaged (C-TECH-055) / diagnostic components removed (C-TECH-056): carried forward, unaffected (manifest: 3 warnings, 0 resolved, 3 accepted — same disposition as prior cycles, none touching this flow).

## 8. Recommendations

**Re-dispatch pipeline-agent to import this exact artifact to DEV**, then perform the V4 designer open-and-save and one authenticated POST that leaves an optional checkbox question unticked (the precise condition ERR-20260928-1022 reproduced) to close V5 on the fix itself. Until that POST succeeds against *this* artifact, the fix is verified by content and static analysis, not by execution.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0949 | `no-assertion-on-shipped-content` | rework | A fallback branch (`coalesce`/`if`) is unverified code until a test supplies the input that actually triggers it — a green build and a passing static-shape gate prove nothing about a function call inside a branch no test ever exercises. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`
