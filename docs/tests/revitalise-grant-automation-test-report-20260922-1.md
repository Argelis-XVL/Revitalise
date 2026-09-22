# Test Report — Revitalise Grant Automation

**Feature Slug:** `revitalise-grant-automation`
**Artifact:** `build/artifacts/revitalise-grant-automation-20260922-1/`
**Date:** 2026-09-22
**Status:** PASS (scoped retest, gated for pipeline — see coverage note)

---

**Why this cycle exists.** This build exists solely to fix
[`IMP-0813`](../../logs/improvement-log.jsonl) — DEV's *live* copy of `REV | Portal | Round
Statistics` refuses to save in the designer, citing an action `Set trailing 2` that has never
existed in source. The provenance gate
(`scripts/verify-artifact-provenance.py`) requires a test report naming this exact build id
before DEV import can proceed, and the most recent report,
[`revitalise-grant-automation-test-report-20260919-2.md`](revitalise-grant-automation-test-report-20260919-2.md),
covers a build three commits and two builds behind.

**Coverage note — scoped, not blind.** `git diff 9e12f07 c4da028` (last-tested commit → this
build's commit) touches 23 files. Two commits in that range
([`7d22c7d`](../../logs/routing.log), [`e87b38a`](../../logs/routing.log)) belong to
`trustee-portal-visual-refresh` (wbs:6.10) and `CO-006` (grant-admin MDA, wbs:0.12) and are
already validated under that slug's own cycle —
[`trustee-portal-visual-refresh-test-report-v15.md`](trustee-portal-visual-refresh-test-report-v15.md),
PASS, built from the **identical commit** `7d22c7d` this artifact also contains. This report does
not re-derive that coverage; it cites it. What is new *since* `7d22c7d` (`git diff 7d22c7d c4da028`)
is almost entirely logs/docs/improvement-review housekeeping plus one 8-line change to the round
statistics flow itself — which is the `IMP-0804` fix v15 already tested at source level, carried
forward unchanged. This report's own work is: (a) independently re-verify the round-statistics
flow is clean in *this* artifact, both source and packed, (b) re-run the whole regression suite
against this build's own output rather than trust the manifest, (c) confirm no new HARD constraint
or P1/P2 defect entered in the delta.

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit / Regression (Pester, whole-solution) | Yes — re-run independently against this build's own `pester-results.xml` | 1037 | 0 | 1 (pre-existing) |
| Unit (code app: vitest/typecheck/lint) | Yes, per manifest's 84-step preflight | all green | 0 | 0 |
| Integration | Source/artifact-level only, no live query this cycle (DEV not yet re-imported) | — | 0 | — |
| End-to-End | Not run this cycle — this artifact has not been imported to DEV yet | — | — | deferred to pipeline-agent |
| Regression | Yes — Solution Checker clean, `flow-definition-language` and `flow-reads-no-trigger-body` re-run standalone against the round-statistics flow | 2/2 gates | 0 | 0 |
| Security | Source-level only (role/privilege/column-security gates); no live Graph/Dataverse query this cycle | see §5 | 0 | — |
| Accessibility | N/A this cycle — the two changed screens (`CasePanels`, `VerdictForm`) were already covered under [v15](trustee-portal-visual-refresh-test-report-v15.md) | — | — | N/A |
| Performance | N/A — no NFR threshold engaged by this delta | — | — | N/A |
| Provisioning | Source/settings-file verification only; live DEV still runs `trustee-portal-visual-refresh-20260920-6`, not this build (`logs/pipeline.log:192`) | see §6 | 0 | deferred to pipeline-agent |
| Compliance | Yes — domain/technology constraints re-checked, see §5 | — | 0 | — |
| **Total** | | **1039+/1039+** | **0** | **1 pre-existing** |

## 2. Requirement Coverage

This build's own new content relative to the last-tested `revitalise-grant-automation` build is
the round-statistics flow fix (`IMP-0813`'s remediation) and housekeeping; the functional
requirements it packages (FR-080/FR-081/FR-082) were authored and tested under a different slug:

| Scope | Requirement source | Prior verdict | Re-verified this cycle |
|---|---|---|---|
| FR-080/081/082 (round statistics: all-history month count, trailing-6-month anomaly flag, history seed settings) | [`trustee-portal-visual-refresh-test-report-v15.md`](trustee-portal-visual-refresh-test-report-v15.md) | PASS (source/V1–V2), `A-FLOW-17` correctly OPEN | Unchanged — same commit (`7d22c7d`), carried into this artifact byte-for-byte (see §7.1) |
| CO-006 grant-admin MDA fixes (wbs:0.12, unquoted, `C-COM-002`) | Same v15 report | PASS | Unchanged |
| DocuSign / Payment Capture / Finance role (wbs:3.2–3.4, 8.2, 8.3) | [`revitalise-grant-automation-test-report-20260919-2.md`](revitalise-grant-automation-test-report-20260919-2.md) | PASS | Unchanged — no source touched in this delta |
| Round statistics action-name integrity (`IMP-0813`'s root cause) | This report | — | **Yes — see §3/§7** |

## 3. Failed Tests

None. The specific defect this build exists to fix (`IMP-0813`'s root cause) is a **live DEV
state** problem, not a source or packaging defect, and is independently confirmed absent from
both source and the packed artifact:

```
grep -oi '"[A-Za-z_]*[Ss]et[ _]trailing[^"]*":' \
  src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json
→ Set_trailing_1 … Set_trailing_6, Set_trailing_filled_count — 7 keys, each exactly once
grep -c '"Set trailing' <same file, and the unzipped RevitaliseGrantAutomation-managed.zip copy>
→ 0 in both
```

`scripts/verify-flow-definition-language.py` re-run standalone against
`src/solutions/RevitaliseGrantAutomation/Workflows` reports `OK`, including its "no action name
reused anywhere within one flow" check — the exact class `IMP-0813`'s symptom belongs to, if it
had been a source defect. `scripts/verify-flow-trigger-body-isolation.py` re-run standalone
against the same flow file reports `OK` (checks A1/A2/A3/B1 clean, 5 personal-data entity sets).

## 4. Defects Raised

None new. Nothing carried forward from
[20260919-2](revitalise-grant-automation-test-report-20260919-2.md)'s §4 reopens — D-01/D-02/D-03
remain closed, unaffected by this delta.

`IMP-0813` itself is **not** a defect in this artifact — it describes DEV's *current* live state
(still running `trustee-portal-visual-refresh-20260920-6`, `logs/pipeline.log:192`), which this
artifact has not yet reached. It is correctly recorded as deferred, not closed
(`revisit_when`: a fresh import of clean source into DEV, followed by a human designer
open-and-save). Closing it is pipeline-agent's and the human V4 step's job, not this report's —
see §7.2.

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-DOM-030/031/032 | Special-category/audit invariants on secured columns | PASS | `domain-invariants` gate — manifest `constraint_check: PASS`, part of the 84-step preflight, no source touched in this delta that carries a secured column |
| C-TECH-040 | Group teams only, no direct role assignment in Test/Acc/Prd | PASS (source), UNEVALUABLE (live TST/ACC/PRD — no import there this cycle) | Same settings files as [20260919-2](revitalise-grant-automation-test-report-20260919-2.md)'s §5, untouched in this delta |
| C-TECH-052 | Every hand-authored contract has a register row (no orphans) | PASS | `verify-assumption-markers.py` re-run clean per manifest's `assumption-markers` gate; the new round-statistics settings/notes rows (`RoundStatisticsHistoryStartDate` et al.) were registered under `7d22c7d` and already verified by [v15](trustee-portal-visual-refresh-test-report-v15.md) §7.1 |
| C-TECH-053 | Verification level claimed matches level confirmed | PASS | §7.2 — this report claims only V2 for this artifact, nothing overclaims |
| C-TECH-054 | Cross-OS: pipeline/CI scripts run on the CI runner's OS | UNEVALUABLE, informational | `manifest.json`'s `build_os`: Darwin, local; the one CI-only step (`auth`) correctly recorded under `steps_not_executed` |
| C-TECH-058 | OPEN assumption closeable in an existing environment, re-evaluated fresh this cycle | PASS | `logs/pipeline.log:192` (2026-09-22, this dispatch's own predecessor attempt) confirms DEV's actual current state is `trustee-portal-visual-refresh-20260920-6`; nothing in this feature's own Dev Summary §10 register was touched by the 9e12f07→c4da028 delta, so its OPEN rows are unchanged from 20260919-2's re-evaluation and remain correctly OPEN |
| C-TECH-061 | Improvement-log queue has no unread blocker at build time | PASS | `python3 scripts/verify-improvement-log.py --check`, re-run standalone this cycle: `OK — 811 entries (188 NEW, 615 APPLIED, 8 REJECTED), 9 warnings`; 8 unread entries, all severity friction/rework (`IMP-0798`–`IMP-0803`, `IMP-0811`, `IMP-0812`), none blocker; `IMP-0813`/`IMP-0814`/`IMP-0815` are all reviewer-deferred with a recorded reason, not unread |

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
| `RoundStatisticsHistoryStartDate` / `PriorApplicationCount` / `MonthlyAnomalyThresholdPercent` seed rows | Real values (not `{{PLACEHOLDER}}`), all three environments | `provisioning/deploymentSettings/dev-scoring-settings.json`, `test-settings.json`, `prd-settings.json` — added under `7d22c7d`, unchanged in this delta, already verified by [v15](trustee-portal-visual-refresh-test-report-v15.md) | PASS |
| Round-statistics flow action names | Match source exactly, no drift, no collision | §3 above | PASS (source + packed artifact) |
| DEV solution state | Not yet this artifact — deployment is this cycle's *purpose*, not its precondition | `logs/pipeline.log:192` — DEV currently runs `trustee-portal-visual-refresh-20260920-6` | **Correctly OPEN — this is what pipeline-agent's next dispatch is for** |
| DEV live copy of `REV | Portal | Round Statistics` | Still corrupted (`Set trailing 2` reference) until this artifact is imported and the designer is opened/saved | `IMP-0813`, `deferred_reason` | **OPEN — see Recommendations** |

## 7. Platform Contract & Verification-Level Audit

### 7.1 Assumption register closure (Dev Summary §10)

No row in `docs/development/revitalise-grant-automation-dev-summary.md`'s register was added or
touched by the 9e12f07→c4da028 delta (confirmed: `git diff 9e12f07 c4da028` does not touch this
file). The register's state is therefore unchanged from
[20260919-2](revitalise-grant-automation-test-report-20260919-2.md) §7.1 — re-cited, not
re-derived, per token rules:

| Assumption ID | Claim | Closing precondition | Does it exist yet? | Result |
|---|---|---|---|---|
| A-FIN-09 | Platform-baseline privilege block sufficient for the finance persona | `wbs:8.3` app-sharing + a signed-in test finance user (V4) | Unchanged since 20260919-2 | OPEN, correctly recorded |
| A-FIN-08 / A-PAY-1 | Decimal-control classid is what the designer actually assigns | A human opens `rev_roundfinance`'s form once in DEV | Unchanged since 20260919-2 | OPEN, correctly recorded |
| A-TR-*, A-DS-*, A-FLOW-*, A-LAND-* (DEV-closeable set) | Various | DEV environment | Standing reviewer OVERRIDE still on record | PASS — no silent carry-forward found |

`A-FLOW-17` (the discriminator-gated literal fixing `IMP-0804`) belongs to
`docs/development/trustee-portal-visual-refresh-dev-summary.md`, not this feature's register — it
is [v15](trustee-portal-visual-refresh-test-report-v15.md) §7.1's row, correctly out of this
report's scope. No orphan hand-authored contracts found this cycle (0 rows with no register
entry).

### 7.2 Verification levels achieved

| Component | Level claimed | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| `RevitaliseGrantAutomation-managed.zip` (build 1, this artifact) | V2 — packaged, layout accepted, content unverified | V2 confirmed | `manifest.json`: `verification_level: "V2"`, 84/84 steps, 65/65 gates, this report's own independent re-run of `flow-definition-language`/`flow-reads-no-trigger-body` | PASS |
| Round-statistics flow, DEV live copy | Not claimed by this build — DEV has not yet received it | N/A | `logs/pipeline.log:192` | **Correctly not claimed. V3/V4 are pipeline-agent's and a human's, next** |

- Idempotency: not yet re-run against this artifact — deferred to pipeline-agent's import.
- V4 designer/editor open + save: **not performed**. This is the exact step `IMP-0813`'s
  `revisit_when` names as the closing condition, and it cannot happen before pipeline-agent
  imports this artifact.
- Cross-OS (`C-TECH-054`): local Darwin build; CI-only step correctly deferred, not silently
  skipped.
- Warnings triaged (`C-TECH-055`): 2 total, 1 resolved this build (bundle-budget, see
  `manifest.json`'s `warnings_detail`), 1 accepted (pre-existing `npm` deprecation notice).

**This report does not, and cannot, claim `IMP-0813` closed.** That would overclaim past V2 —
exactly the failure mode `C-TECH-053` exists to catch. What this report *does* establish is that
nothing in source or in the packaged artifact will reproduce the defect once DEV is reloaded from
it — which is the precondition the provenance gate needs, not the fix's own completion.

## 8. Recommendations

1. **Deploy this artifact to DEV** (pipeline-agent). This is the actual remediation for
   `IMP-0813` — its root cause is a stale live copy, and nothing further in source needs to
   change.
2. **After import, a human opens `REV | Portal | Round Statistics` in the Power Automate
   designer and saves it**, confirming the `Set trailing 2` error is gone. This is the V4 step
   `IMP-0813`'s `revisit_when` names; no session in this system can perform it.
3. Cloud-flow statecode reconciliation after any `--force-overwrite` import remains an open,
   carried-forward item (`IMP-0113`/`IMP-0136` class) — capture flow statecodes before and after
   this import, per the same gap [20260919-2](revitalise-grant-automation-test-report-20260919-2.md)
   §6 already flagged.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | This cycle's own checks (flow-definition-language, flow-trigger-body-isolation, Pester re-run, improvement-log --check) all reproduced the manifest's claims exactly; nothing surprised. |

Digest regenerated: NO (no new entries to regenerate for) — `logs/known-failure-modes.md` last
regenerated 2026-09-22 per its own header, already current.
