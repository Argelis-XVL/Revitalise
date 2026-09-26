# Test Report — Revitalise Grant Automation

**Feature Slug:** revitalise-grant-automation
**Artifact:** `build/artifacts/revitalise-grant-automation-20260924-6/`
**Date:** 2026-09-24
**Status:** FAIL
**WBS:** 6.8, 2.7, 0.4, 4.5, 4.2, 6.9

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit (Pester) | Yes | 1133 | 0 | 1 |
| Integration | Yes | (within Pester total above) | 0 | 0 |
| End-to-End | Not run | — | — | — (blocked, see §7.1) |
| Regression | Yes | 1133 | 0 | 1 |
| Security | Spot-checked (gitleaks, field security) | Pass | 0 | — |
| Accessibility | N/A this dispatch (no new/changed screen; forms are Dataverse FormXml, not the React app) | — | — | — |
| Performance | N/A — no NFR touched by this dispatch | — | — | — |
| Provisioning | Not applicable to this artifact's changes (no new site/team/app-reg) | — | — | — |
| **Platform Contract (§7.1)** | Yes — **this is where the artifact fails** | — | **1 blocker** | — |
| **Total** | | 1133 | **1 (artifact-level, undetected by any Pester test)** | 1 |

**Bottom line: FAIL.** The packed artifact still reproduces the exact live-DEV-import
rejection (`IMP-0866`) it was built to close. Do not proceed to Pipeline.

---

## 2. Requirement Coverage

| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| A-LOC-1 / A-ATYPE-1 / A-AGE-1 (wbs:4.5) | Quick View Forms embedding location area, applicant type, age range on `rev_applicant` | `IntakeContract.Tests.ps1:723` "Quick View Forms on rev_applicant" | **FAIL at artifact level** — source and unit test pass; packed artifact fails (see §7.1) |
| wbs:6.9 | `REVPortalRoundStatistics` `Initialise_trailing_variables` split into 7 actions (`IMP-0820`/`IMP-0821`) | `BuildGates.Tests.ps1` + dev summary §"Re-verification" (line 9803) | PASS — source-level, no artifact-level dependency found |
| wbs:0.4 | `REVSafeguardingActionCompletion` loop guard + two derived-count drifts corrected | dev summary lines 10255–10385 re-verification | PASS |
| wbs:2.7, 6.8, 4.2 | Not the subject of any revision block added since the last approved test report; carried unchanged from `revitalise-grant-automation-test-report-20260924-4.md` | (unchanged) | Carried — not re-tested this cycle; the build's overall status is FAIL regardless (single artifact, single import unit) |

---

## 3. Failed Tests

| Test ID | Layer | Description | Expected | Actual | Severity |
|---|---|---|---|---|---|
| ARTIFACT-QVF-1 | Platform Contract | Packed `build/artifacts/revitalise-grant-automation-20260924-6/RevitaliseGrantAutomation.zip` → `customizations.xml`, the three `rev_applicant` Quick View Forms' `<forms type>` wrapper | `type="quick"` (matching the corrected source and the value Microsoft Learn documents) | `type="quickview"` for all three forms — identical to the string that failed live DEV import in `IMP-0866` | **P1 / blocker** |

No Pester test asserts this — see §7.1 for why.

---

## 4. Defects Raised

| Defect ID | Severity | Description | Linked Test |
|---|---|---|---|
| IMP-0874 | blocker | `pac solution pack` derives the packed `<forms type>` wrapper from the `FormXml/<foldername>/` path segment, not from the split file's own root attribute — so `IMP-0867`'s source-level fix (file content: `quickview`→`quick`) has **no effect** on the packed artifact, because the containing folder is still named `FormXml/quickview/`. Reproduced directly (see §7.1). | ARTIFACT-QVF-1 |

---

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-TECH-049 | Platform limits the packer doesn't enforce get a build gate | **VIOLATION (in effect)** | `formxml-type-values` gate exists and is green, but it reads only `Entities/*/FormXml/**/*.xml` **source** files — never the packed artifact — so it does not enforce the limit that actually rejects the import (see §7.1). The gate closes the wrong half of the contract. |
| C-TECH-052 | Every hand-authored solution component has a register row / ground-truthed shape | VIOLATION on this artifact | A-QVF-1 was closed `CLOSED — WRONG` on the basis of an unverified claim ("folder name is a repository path, not a platform value") that this cycle disproves by direct reproduction |
| C-TECH-053 | Verification level claimed matches level confirmed | VIOLATION | Dev summary §11 (line 10574) itself says V3 was "not yet re-packaged or re-imported to confirm V3 now passes" — this test cycle performed that missing check and it fails |
| C-TECH-050 | FieldPermission Web API route present for a promoted column | PASS (unchanged from build's own gate: `fieldpermissions Web API route: 1/3 environment(s) wired`, tracked separately as accepted `blocked_on` notes, not this dispatch's scope) | `run-build-result.json`, pipeline-config-preflight step |
| C-TECH-054 | Every pipeline/CI script runs on the CI runner OS | PASS | `verify-workflow-syntax.py` OK in `run-build-result.json`; no new OS-specific script this dispatch |
| C-TECH-055 | Tool warnings triaged | PASS | dev summary wbs:0.4 revision (lines 10319–10324) addendum |
| C-TECH-056 | Diagnostic components removed | PASS | no diagnostic component added this dispatch |
| C-DOM-030 | No special-category/safeguarding column influences automated scoring | PASS | `domain-invariants` build step green per `run-build-result.json`; unaffected by this dispatch's FormXml-only change |
| C-COM-002 | Work enters by accepted WBS task id | PASS | all revision blocks in the dev summary carry `wbs:` tags resolving to `contract/wbs.json` tasks 6.8/2.7/0.4/4.5/4.2/6.9 |

All other HARD/SOFT rows in `constraints/technology/technology-constraints.md` and
`constraints/domain/domain-constraints.md` scoped to `test-agent` are unaffected by this
dispatch's change (FormXml root attribute + one Pester assertion) and are carried PASS from
`revitalise-grant-automation-test-report-20260924-4.md`, which this report does not repeat.

---

## 6. Provisioning Verification

Not applicable — this dispatch touches no site, team, app registration, group team, role
binding, or app sharing (TAD §12 / §6.1 unaffected).

---

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| A-QVF-1 | `<forms type="quick">` (source) is the correct, importable value; the `FormXml/quickview/` folder name is "unaffected — a repository path, not a platform value" | **CLOSED — WRONG** (dev summary line 10491) | A live DEV import, or a direct inspection of the packed artifact, confirming the packed `<forms type>` wrapper | **Yes — the artifact under test exists right now** | **Reproduced and disproved.** Two independent checks: (1) unzipped `build/artifacts/revitalise-grant-automation-20260924-6/RevitaliseGrantAutomation.zip`, matched each `<formid>` to its enclosing `<forms type>` wrapper in `customizations.xml` — all three read `type="quickview"`. (2) Copied `src/solutions/RevitaliseGrantAutomation` to a scratch directory, renamed **only** `Entities/rev_applicant/FormXml/quickview/` → `FormXml/quick/` (file contents untouched), ran `pac solution pack --zipfile test.zip --folder src --packagetype Unmanaged`, and the packed wrapper flipped to `type="quick"` for all three forms. This isolates the cause to the **folder name**, not the file content. | **FAIL** |

**Root cause:** `pac solution pack`'s SolutionPackager derives the packed `<forms type>`
wrapper attribute from the `FormXml/<foldername>/` path segment, not from the split source
file's own root `type` attribute. `IMP-0867` corrected the file content; the folder is still
named `quickview`, so the packer keeps writing `quickview` into every artifact this build
config produces, regardless of what the source file says. The three `quickviewcontrol` embeds
on the Application main form are unaffected (they address forms by GUID, confirmed in the dev
summary and unchanged here) — the defect is confined to the standalone forms' own wrapper, exactly
as before, and would produce the **identical** live import error `IMP-0866` recorded.

**Why the new gate didn't catch it:** `scripts/verify-formxml-type-values.py` (introduced by
`IMP-0867`) parses `Entities/*/FormXml/**/*.xml` — the split **source** files — with
`xml.etree.ElementTree`, and correctly reports them all as `quick`. It never opens a packed
`build/artifacts/*/RevitaliseGrantAutomation.zip`. This is a `gate-scope-mismatch` (recurring
class, x25 in `logs/known-failure-modes.md`): the gate's scope is source, the deployable is the
packed zip, and this is exactly the divergence between them.

Filed as `IMP-0874` (blocker), proposing the gate also assert against the packed artifact once
one exists, and naming the concrete fix (rename the folder) as development-agent's to make.

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Quick View Forms (A-LOC-1/A-ATYPE-1/A-AGE-1) | V3 not yet re-confirmed (dev summary line 10574, honestly stated as outstanding) | **V2 only** — packs with exit 0, but the packed content is provably wrong | Direct unzip + reproduction above | **FAIL** — V3 cannot be attempted; a live import of this artifact would fail identically to `IMP-0866` |
| wbs:6.9 (`REVPortalRoundStatistics` action split) | V3 (source + build gates green, no live-environment dependency claimed) | V2 confirmed via build; V3 out of this cycle's scope | `run-build-result.json` pack steps exit 0 | PASS at claimed level |
| wbs:0.4 (`REVSafeguardingActionCompletion` loop guard) | V2 (build-level) | V2 confirmed | `run-build-result.json` | PASS at claimed level |

- Idempotency: not reached — a first live import of this artifact has not occurred (the prior
  attempt, `IMP-0866`, was against an earlier artifact and failed) → `N/A — blocked`
- V4 designer/editor open + save: **NOT PERFORMED** — cannot be performed until V3 (a successful
  import) is reached → `FAIL (blocked, not deferred: the precondition for V3 exists — the artifact
  — but the artifact itself is defective, so V3 would fail again, not merely "not yet attempted")`
- Cross-OS (C-TECH-054): PASS — no new OS-specific script this dispatch
- Warnings triaged (C-TECH-055) / diagnostic components removed (C-TECH-056): PASS — addressed in
  the wbs:0.4 revision, unaffected by this finding

---

## 8. Recommendations

1. **Do not deploy this artifact.** It reproduces `IMP-0866` verbatim; a DEV import attempt would
   fail again with "Forms being imported are of an unsupported type 'quickview'".
2. Rename `src/solutions/RevitaliseGrantAutomation/Entities/rev_applicant/FormXml/quickview/` to
   `FormXml/quick/` (file contents already correct; reproduced as sufficient by scratch-pack test
   in §7.1). Update the three files referencing the old folder name literally:
   `src/tests/solutions/IntakeContract.Tests.ps1` (`$script:QuickViewDir`),
   `src/tests/build/BuildGates.Tests.ps1`'s known-bad fixture path, and the comment in
   `constraints/technology/component-shapes.yml` that currently asserts the folder name is inert.
3. Extend `scripts/verify-formxml-type-values.py` (or add a paired build step) to check the
   **packed** artifact's `customizations.xml`, not only the split source — this is the general
   fix; the specific rename is the immediate one.
4. Re-dispatch build-agent for a fresh artifact once the rename lands, then re-dispatch test-agent.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0874 | `platform-contract-guessed-not-groundtruthed` | blocker | Before trusting a split-source shape fix, ground-truth whether the packer derives the platform value from the file's own content or from its containing folder name — `pac solution pack` keys `<forms type>` to the `FormXml/<foldername>/` path segment, not the file's declared attribute, so `IMP-0867`'s file-content-only fix never reached the packed artifact. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`
