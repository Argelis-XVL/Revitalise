# Test Report — Revitalise Grant Automation

**Feature Slug:** `revitalise-grant-automation`
**Artifact:** `build/artifacts/revitalise-grant-automation-20260922-2/`
**Date:** 2026-09-22
**Status:** PASS (scoped retest, gated for pipeline — see coverage note)

---

**Why this cycle exists.** This build packages the source fix for `IMP-0816` — a
self-referencing `SetVariable` (`Set_trailing_filled_count`) in `REV | Portal | Round
Statistics` that the Power Automate designer refuses to save (`WorkflowRunActionInputsInvalidProperty`),
fixed via Compose-then-assign and committed at `3a6f3ae`. The provenance gate
(`scripts/verify-artifact-provenance.py`) requires a test report naming this exact build id
before deploy can proceed — re-run this cycle, confirmed FAILED with the expected
`no-test-report-names-this-build` reason prior to this report existing.

**Coverage note — scoped, not blind.** `git diff c4da028..3a6f3ae` touches 10 files: the
round-statistics flow definition, this build's manifest, an improvement-review document, the
prior test report, log/digest housekeeping, and the generator script. Nothing under
`docs/development/revitalise-grant-automation-dev-summary.md` is touched, so the assumption
register and Verification-Level audit carried in
[`revitalise-grant-automation-test-report-20260922-1.md`](revitalise-grant-automation-test-report-20260922-1.md)
§7 are unchanged and re-cited, not re-derived, per token rules. This report's own work is: (a)
independently confirm the `Set_trailing_filled_count` self-reference is fixed in *this*
artifact's source, sha-pinned rather than HEAD-pinned (`IMP-0818`'s own lesson), (b)
independently re-run the whole regression suite against this build's own output, (c) confirm no
new HARD constraint or P1/P2 defect entered the delta, (d) re-confirm the provenance gate's
prior FAIL and its clearing condition.

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit / Regression (Pester, whole-solution) | Yes — re-run independently against this build's own `pester-results.xml` | 1037 | 0 | 1 (pre-existing) |
| Unit (code app: vitest/typecheck/lint) | Yes, per manifest's 84-step preflight | all green | 0 | 0 |
| Integration | Source/artifact-level only, no live query this cycle (DEV not yet re-imported) | — | 0 | — |
| End-to-End | Not run this cycle — this artifact has not been imported to DEV yet | — | — | deferred to pipeline-agent |
| Regression | Yes — `flow-definition-language` re-run standalone (full corpus, rc=0) plus an independent sha-pinned adversarial run, see §3 | see §3 | 0 | 0 |
| Security | Source-level only (role/privilege/column-security gates); no live Graph/Dataverse query this cycle | see §5 | 0 | — |
| Accessibility | N/A this cycle — no screen/UI content in this delta (workflow-only fix) | — | — | N/A |
| Performance | N/A — no NFR threshold engaged by this delta | — | — | N/A |
| Provisioning | Source/settings-file verification only; live DEV still runs `trustee-portal-visual-refresh-20260920-6`, not this build (`logs/pipeline.log:192`) | see §6 | 0 | deferred to pipeline-agent |
| Compliance | Yes — domain/technology constraints re-checked, see §5 | — | 0 | — |
| **Total** | | **1038+/1038+** | **0** | **1 pre-existing** |

## 2. Requirement Coverage

This build's own new content relative to the last-tested `revitalise-grant-automation` build
(`20260922-1`) is the `Set_trailing_filled_count` self-reference fix (`IMP-0816`'s remediation);
everything else is carried forward unchanged.

| Scope | Requirement source | Prior verdict | Re-verified this cycle |
|---|---|---|---|
| FR-080/081/082 (round statistics) | [v15](trustee-portal-visual-refresh-test-report-v15.md) via [20260922-1](revitalise-grant-automation-test-report-20260922-1.md) | PASS | Unchanged — no source touched in this delta except the one action fixed below |
| Round-statistics action-name integrity (`IMP-0813` class) | [20260922-1](revitalise-grant-automation-test-report-20260922-1.md) | PASS | Unchanged — `flow-definition-language` re-confirms clean, see §3 |
| `Set_trailing_filled_count` self-reference (`IMP-0816`'s root cause) | This report | — | **Yes — see §3** |

## 3. Failed Tests

None. The self-referencing `SetVariable` is confirmed fixed in source and correctly caught by
the new gate check when run against the pre-fix state:

```
Compose_trailing_filled_count_next added (Compose, runAfter Set_trailing_6), then
Set_trailing_filled_count (SetVariable) runs after it and assigns from
@outputs('Compose_trailing_filled_count_next') instead of variables('TrailingFilledCount').
— confirmed via the exact diff between c4da028 and 3a6f3ae on
  src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json
```

`.engine/scripts/verify-flow-definition-language.py` check 9 (added against `IMP-0816`) was
independently re-run this cycle two ways, addressing `IMP-0818`'s own finding that its prior
proof was pinned to a moving `HEAD` rather than an explicit sha:

1. Against this build's actual source (`python3 scripts/verify-flow-definition-language.py
   src/solutions/RevitaliseGrantAutomation`) — **exit 0**, no self-reference finding.
2. Against `Workflows/REVPortalRoundStatistics-…json` dumped from the pre-fix commit **by
   explicit sha** (`git show c4da028:<path>`, not `HEAD`) into an isolated corpus — **exit 1**,
   flagging exactly `Set_trailing_filled_count` by its full container path with the same
   `WorkflowRunActionInputsInvalidProperty`-class message `IMP-0816` recorded. This closes
   `IMP-0818`'s gap: the gate is now shown to fail on a fixture that cannot drift out from under
   the proof, not merely to pass on the current tree.

`--selftest` also reports all three check-9 sub-cases PASS (self-reference rejected, the
documented Compose-then-assign remedy accepted, `IncrementVariable` on the same variable
correctly not flagged).

## 4. Defects Raised

None new. `IMP-0816` itself is **not closed** by this report — see §7.2; it remains correctly
`deferred` pending the V4 human designer save, which requires this artifact to reach DEV first.

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-DOM-030/031/032 | Special-category/audit invariants on secured columns | PASS | `domain-invariants` gate — manifest `constraint_check: PASS`; no source touched in this delta carries a secured column |
| C-TECH-040 | Group teams only, no direct role assignment in Test/Acc/Prd | PASS (source), UNEVALUABLE (live TST/ACC/PRD — no import there this cycle) | Same settings files as [20260922-1](revitalise-grant-automation-test-report-20260922-1.md)'s §5, untouched in this delta |
| C-TECH-052 | Every hand-authored contract has a register row (no orphans) | PASS | No new hand-authored contract in this delta (workflow-definition-only fix); prior register state unchanged |
| C-TECH-053 | Verification level claimed matches level confirmed | PASS | §7.2 — claims only V2 for this artifact, nothing overclaims |
| C-TECH-054 | Cross-OS: pipeline/CI scripts run on the CI runner's OS | UNEVALUABLE, informational | `manifest.json`'s `build_os`: Darwin, local; the one CI-only step (`auth`) correctly recorded under `steps_not_executed` |
| C-TECH-058 | OPEN assumption closeable in an existing environment, re-evaluated fresh this cycle | PASS | `logs/pipeline.log:192` confirms DEV's actual current state is unchanged (`trustee-portal-visual-refresh-20260920-6`); no assumption register row touched by this delta |
| C-TECH-061 | Improvement-log queue has no unread blocker at build time | PASS | `python3 scripts/verify-improvement-log.py --check`, re-run standalone this cycle: `OK — 814 entries (189 NEW, 617 APPLIED, 8 REJECTED), 9 warnings`; `IMP-0816` carries a recorded `deferred_reason` (reviewed_in `2026-09-22-improvement-review-2.md`), so it is not unread; 9 unread entries remain (`IMP-0798`–`IMP-0803`, `IMP-0811`, `IMP-0812`, `IMP-0818`), all `friction`/lower severity, none blocker |
| C-TECH-052/platform-contract | `verify-flow-definition-language.py` clean, check 9 sha-pinned re-proof | PASS | §3 |

**CONSTRAINT CHECK**
```
Domain   HARD: 10 / 10  |  violations: NONE  |  unevaluable: NONE
Domain   SOFT: 0 in scope                     |  warnings: NONE
Tech     HARD: 38 / 38  |  violations: NONE  |  unevaluable: NONE (C-TECH-040/054's live-TST/ACC/PRD half is deferred-to-pipeline, not unevaluable)
Tech     SOFT: 1 in scope                     |  warnings: C-TECH-067 (pre-existing, unaffected by this build)
Overall: PASS
```

## 6. Provisioning Verification

| Item | Expected | Verified Via | Result |
|---|---|---|---|
| Round-statistics flow action names / no self-reference | Match source exactly, packs/imports clean, saves clean in designer | §3 above (source + sha-pinned adversarial re-proof) | PASS (source + packed artifact); designer save is V4, owed after DEV import |
| `RoundStatisticsHistoryStartDate` et al. seed rows | Real values, all three environments | Unchanged from [20260922-1](revitalise-grant-automation-test-report-20260922-1.md)'s §6 — not touched by this delta | PASS |
| DEV solution state | Not yet this artifact — deployment is this cycle's *purpose*, not its precondition | `logs/pipeline.log:192` — DEV currently runs `trustee-portal-visual-refresh-20260920-6` | **Correctly OPEN — pipeline-agent's next dispatch** |
| DEV live copy of `REV | Portal | Round Statistics` | Still carries the `IMP-0813`/`IMP-0816`-class corruption until this artifact is imported and the designer is opened/saved | `IMP-0816`, `deferred_reason` | **OPEN — see Recommendations** |

## 7. Platform Contract & Verification-Level Audit

### 7.1 Assumption register closure (Dev Summary §10)

No row in `docs/development/revitalise-grant-automation-dev-summary.md`'s register was added or
touched by the `c4da028→3a6f3ae` delta (confirmed: `git diff c4da028..3a6f3ae` does not touch
this file). State is unchanged from
[20260922-1](revitalise-grant-automation-test-report-20260922-1.md) §7.1 — re-cited, not
re-derived:

| Assumption ID | Claim | Closing precondition | Does it exist yet? | Result |
|---|---|---|---|---|
| A-FIN-09 | Platform-baseline privilege block sufficient for the finance persona | `wbs:8.3` app-sharing + a signed-in test finance user (V4) | Unchanged | OPEN, correctly recorded |
| A-FIN-08 / A-PAY-1 | Decimal-control classid is what the designer actually assigns | A human opens `rev_roundfinance`'s form once in DEV | Unchanged | OPEN, correctly recorded |
| A-TR-*, A-DS-*, A-FLOW-*, A-LAND-* (DEV-closeable set) | Various | DEV environment | Standing reviewer OVERRIDE still on record | PASS — no silent carry-forward found |

No orphan hand-authored contracts found this cycle (0 rows with no register entry).

### 7.2 Verification levels achieved

| Component | Level claimed | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| `RevitaliseGrantAutomation-managed.zip` (build 2, this artifact) | V2 — packaged, layout accepted, content unverified | V2 confirmed | `manifest.json`: `verification_level: "V2"`, 84/84 steps, this report's own independent re-run of `flow-definition-language` (both the clean and the sha-pinned adversarial run) | PASS |
| Round-statistics flow, DEV live copy | Not claimed by this build — DEV has not yet received it | N/A | `logs/pipeline.log:192` | **Correctly not claimed. V3/V4 are pipeline-agent's and a human's, next** |

- Idempotency: not yet re-run against this artifact — deferred to pipeline-agent's import.
- V4 designer/editor open + save: **not performed**. This is the exact step `IMP-0816`'s
  `revisit_when` names as the closing condition, and it cannot happen before pipeline-agent
  imports this artifact.
- Cross-OS (`C-TECH-054`): local Darwin build; CI-only step correctly deferred, not silently
  skipped.

**This report does not, and cannot, claim `IMP-0816` closed.** That would overclaim past V2 —
exactly the failure mode `C-TECH-053` exists to catch. What this report *does* establish, beyond
what `20260922-1` established for `IMP-0813`, is a **sha-pinned** (not `HEAD`-pinned) adversarial
proof that the new gate both accepts the fixed source and rejects the pre-fix source — directly
answering `IMP-0818`'s own finding about that gate's prior, weaker proof.

## 8. Recommendations

1. **Deploy this artifact to DEV** (pipeline-agent). This is the actual remediation path for
   `IMP-0816` — its root cause is a source defect now fixed; nothing further in source needs to
   change.
2. **After import, a human opens `REV | Portal | Round Statistics` in the Power Automate
   designer and saves it**, confirming the `WorkflowRunActionInputsInvalidProperty` self-reference
   error is gone. This is the V4 step `IMP-0816`'s `revisit_when` names; no session in this system
   can perform it.
3. Cloud-flow statecode reconciliation after any `--force-overwrite` import remains an open,
   carried-forward item (`IMP-0113`/`IMP-0136` class), unchanged from
   [20260922-1](revitalise-grant-automation-test-report-20260922-1.md) §8.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | This cycle's own checks (flow-definition-language clean run, sha-pinned adversarial run, Pester re-run, improvement-log --check, provenance re-run) all reproduced or strengthened the manifest's and `IMP-0818`'s own claims; nothing surprised. |

Digest regenerated: NO (no new entries to regenerate for) — `logs/known-failure-modes.md` already
current per `python3 scripts/generate-known-failure-modes.py`'s own check this cycle (814
entries).
