# Test Report — Trustee Portal Visual Refresh (v15)

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** `build/artifacts/trustee-portal-visual-refresh-20260920-6/`
**Date:** 2026-09-20
**Status:** PASS (source/V1–V2, gated for pipeline) — the live DEV import this cycle exists to enable, and specifically whether the fix resolves it, is genuinely V3 and cannot be established from this artifact

---

**Why this cycle exists.** Build 4's live DEV import failed
([`logs/pipeline.log:182`](../../logs/pipeline.log)): `pac solution import` collided on
`Compose_historic_months_array` being declared on both branches of a `Condition` — a flow-wide
action-name collision (`IMP-0804`). Development-agent's Revision 1.18 fixed it and a new HARD
gate (check 8 of `verify-flow-definition-language.py`) was wired in the same pass to catch this
class going forward. Build 6 is the first build to re-run that gate against the fix. This
cycle's job is to confirm what the fix and the new gate actually prove, and to state plainly
what they do not.

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit (code app) | `npx vitest run` (`src/code-apps/trustee-review-portal`) — re-run by build-agent, cross-checked against `manifest.json` | (carried in artifact; no code-app source changed this revision) | 0 | 0 |
| Unit (Pester, full suite) | `pwsh -NoProfile -File src/tests/Invoke-Tests.ps1`, independently re-run this cycle against `build/artifacts/trustee-portal-visual-refresh-20260920-6/test-results/pester-results.xml` | 1036 | 0 | 1 |
| Integration | Covered by the Pester suite above (Dataverse-shape/flow-JSON structural tests) | — | — | — |
| End-to-End | Not reachable — no import of this build has been attempted (see §7.2) | — | — | — |
| Regression | Full local gate chain re-run directly this cycle (below) | 5/5 gates | 0 | 0 |
| Security | No new auth/input surface this scope — a description/expression edit inside an existing flow | N/A | N/A | N/A |
| Accessibility | No UI surface touched this scope | N/A | — | — |
| Performance | Not in scope this cycle | — | — | — |
| Provisioning | No schema/provisioning change this scope | — | — | — |
| Compliance | No special-category/PII surface touched | N/A | — | — |
| **Total** | | **1036** | **0** | **1** |

Independently re-run by this test-agent this cycle, against the checked-out tree (matches the
artifact — `manifest.json`'s `source_commit` is `7d22c7d4`, current `HEAD` is the same):

```
python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation
    → OK — 8 flow definitions, no action name reused anywhere within one flow (check 8 clean)
python3 scripts/verify-flow-definition-language.py --selftest
    → OK — 24 checks, including the two new check-8 fixtures (duplicate-across-If must fail,
      same-name-in-two-flows must pass); wrapper selftest OK — the gate can fail
python3 scripts/verify-field-length-limits.py src/solutions/RevitaliseGrantAutomation
    → OK — 497 flow descriptions ≤256 chars (the two condensed this revision are inside the limit)
python3 scripts/verify-assumption-markers.py
    → PASS — 28 OPEN rows across 7 documents, every one carrying its source marker, incl. new A-FLOW-17
python3 scripts/verify-assumption-register.py
    → PASS — 89 rows/29 registers/8 documents, 48 open, none contradicted
python3 scripts/verify-improvement-log.py            → OK (schema), 807 entries
python3 scripts/verify-improvement-log.py --check     → OK (schema+triggers), exit 0, 9 warnings
                                                          (none new/blocking — see §5)
python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml
    → PASS, 84 steps, 65 gates
python3 scripts/run-source-gates.py config/revitalise-grant-automation-build.yml
    → OK, 16/16 cheap source gates pass
python3 scripts/verify-coverage-threshold.py build/artifacts/trustee-portal-visual-refresh-20260920-6/test-results/coverage.xml --threshold 80 --exclusions config/coverage-exclusions.json
    → 1778 of 2187 lines = 81.3%, 27 files counted / 4 excluded
```

All figures reconcile against the build-agent HANDOFF and the artifact's own `manifest.json` /
`pester-results.xml` (`total="1037" errors="0" failures="0" skipped="1"` — 1036 executed, matching
the HANDOFF's "1036 Pester tests (0 failed, 1 skipped)") and `solution-checker/pac-solution-check-stdout.log`
(`0 Critical / 0 High / 0 Medium / 0 Low / 0 Informational`).

## 2. Requirement Coverage

| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| FR-080/FR-081 (`historicApplicationsByMonth`, ADR-049/ADR-050) — the specific fix this cycle verifies | `Compose_historic_applications_by_month`'s `months` key, [`REVPortalRoundStatistics-…json:3084`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json) — `if(empty(outputs('Compose_history_start_raw')), '[]', outputs('Compose_historic_months_array'))` | **PASS at V1/V2 only.** JSON well-formed, `flow-definition-language` check 8 confirms the renamed else-branch action (`Compose_historic_months_array_empty`, [line 3061](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json)) no longer collides with its if-branch sibling. **Not V3**: this exact fix has never been imported — build 4 imported the pre-fix shape and failed; this build has not yet been imported at all |
| `A-FLOW-17` (new §10 row, Dev Summary [L4796](../../docs/development/trustee-portal-visual-refresh-dev-summary.md)) — the discriminator-gated literal avoids referencing `outputs()` against an action on the untaken branch, rather than relying on any particular resolution behaviour | Source marker present at the one call site; `verify-assumption-markers.py` confirms it | **OPEN, correctly recorded.** The claim is that the fix *avoids* an unground-truthed platform behaviour, not that the avoidance itself has been exercised live. Closing action per the row: seed `RoundStatisticsHistoryStartDate` unset (forcing the `else` path) after import and confirm `months` resolves to `[]` with no flow failure |
| FR-080/FR-081's own arithmetic (`A-FLOW-15`, `A-FLOW-13`, `A-R61`) | Unchanged this revision — carried from v14 | **Unchanged: PASS at V1, OPEN at V4/V5.** This cycle made no change to the month-grouping or trailing-mean logic itself, only to the collision the import rejected |

## 3. Failed Tests

None.

## 4. Defects Raised

None new. `IMP-0811` (build-agent's own finding — a stale citation-count gap in this feature's
own C-TECH-055 triage table) is already recorded in `manifest.json`'s `improvement_log_entries`
and explicitly named in this dispatch's HANDOFF as non-blocking and not this cycle's to fix — not
re-raised here.

## 5. Constraint & Compliance Verification

See the `CONSTRAINT CHECK` block below. No HARD violation and no HARD `UNEVALUABLE` row found in
test-agent's scope. One HARD row resolves to `deferred-to-pipeline`, matching v14's precedent
exactly:

- **`C-TECH-058`** (an OPEN Dev Summary §10 assumption blocks deployment into an environment
  where it could close) — `A-FLOW-17` (new), plus the carried-forward `A-FLOW-15`/`A-FLOW-13`×2/
  `A-R61`, are genuinely OPEN, and the environment that could close them is the DEV deploy this
  gate is headed for — the import that has not yet been attempted against this build. Deferred to
  `pipeline-agent`'s Stage 0.5 gate, per `skills/how-to-apply-constraints.md`'s "could the
  evidence exist yet?" test.

`IMP-0804` (`blocker`) is parked `awaiting-approval`/reviewer-deferred behind
`docs/improvements/2026-09-20-improvement-review-3.md`, not a fresh unread blocker — confirmed
live: `verify-improvement-log.py --check` exits 0, and `IMP-0804` appears in the 178-entry
reviewer-deferred list, not the 7-entry unread list. The two duplicate-id race entries from
Revision 1.18 (`IMP-0805` APPLIED, `IMP-0807` reviewer-deferred) are likewise not blocking. None
of the 7 currently-unread findings (`IMP-0798`–`IMP-0803`, `IMP-0811`) carries `blocker` severity
— all `friction`/`rework` — confirmed by direct read of each entry's `severity` field, not
inferred from the count.

## 6. Provisioning Verification

No schema, role, or provisioning change in this revision — `rev_setting`/`rev_roundstatisticsresult`
and every role grant are unchanged from v14's build. Not re-audited; nothing in this scope could
have moved it.

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| `A-FLOW-17` (new, [Dev Summary L4796](../../docs/development/trustee-portal-visual-refresh-dev-summary.md)) | The discriminator-gated literal has zero dependence on `outputs()`-against-untaken-branch resolution behaviour | OPEN | Live run with `RoundStatisticsHistoryStartDate` unset, confirming `months` resolves `[]` with no failure | No — this build has never been imported | Source marker present at the one call site (`verify-assumption-markers.py`) | OPEN, correctly recorded, not yet closeable |
| `A-FLOW-15`/`A-FLOW-13`×2/`A-R61` (carried) | `range()`/`addToTime()`/`formatDateTime()` and the trailing-six-month shift behave as documented | OPEN | V2 designer save + V4/V5 live run | No | Unchanged from v14 — markers present, D-15 structural tests still pass | OPEN, correctly recorded |

**No orphan hand-authored artefact found** (`C-TECH-052`) — `verify-assumption-markers.py`
confirms every OPEN row across all 7 documents carries its source marker.

### 7.2 Verification levels achieved

| Component | Level claimed (manifest / Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Whole build artifact | V2 — packaged; layout accepted by the packer, content unverified | **Confirmed V2** | `manifest.json`: `constraint_check: PASS`, `preflight: PASS — 84 steps`, `verification_level: "V2"`, Solution Checker `0/0/0/0/0` | PASS at claimed level |
| The `IMP-0804` fix itself (renamed else-branch action + discriminator-gated `months` expression) | Dev Summary §11 explicitly claims **only** V1/V2 — "no live import" ([Revision 1.18 checklist](../../docs/development/trustee-portal-visual-refresh-dev-summary.md)) | **Confirmed at exactly V1/V2.** No overclaim: neither the Dev Summary nor the manifest asserts this fix has been imported | `flow-definition-language` check 8 clean (self-run above); `manifest.json` verification_level unchanged from prior builds at "V2" | PASS — claim matches confirmed level exactly |
| **The one thing this cycle cannot establish, and the HANDOFF asked this be stated explicitly: does the fix actually resolve the live import** | Not claimed above V2 anywhere in source | **Cannot be confirmed below V3.** Check 8 is a strong, purpose-built signal — it directly encodes the failure mode the async operation reported — but a static check passing is not platform acceptance. This project's own signature failure (640 green tests, fifteen rejected imports) is exactly the shape of trusting a static pass as a live result | No re-import has been attempted against build 6 or any successor. The only way to close this is `pipeline-agent` re-running `pac solution import` | **OPEN — genuinely V3, not derivable from this artifact** |

- **Idempotency:** N/A this cycle — no new provisioning create-only step.
- **V4 designer/editor open + save:** not performed — nothing in this scope has been imported to
  any environment yet.
- **Cross-OS (`C-TECH-054`):** no script changed this revision — N/A, carried forward for
  `pipeline-agent`/CI.
- **Warnings triaged (`C-TECH-055`):** `manifest.json` shows 9 total, 0 resolved, 9 accepted, 0
  untriaged → PASS.
- **Diagnostic components removed (`C-TECH-056`):** none created this scope → PASS, N/A.

**The honest boundary, stated per the HANDOFF's own request:** everything in §1–§7 above is
reachable at V1–V2 from source and the packaged artifact alone, with no live environment.
Whether Revision 1.18's fix actually clears the collision that failed build 4's import is **V3**,
and only a real `pac solution import` against this build (or a successor built from the same
source) answers it. This test cycle's gate output does not, and should not, be read as answering
that question — it answers "is the fix well-formed and does the new gate now catch this class,"
which it is and does.

## 8. Recommendations

1. **The very next live action should be the re-import**, not a further static pass. The new
   check 8 gate closes the class going forward but is not evidence about this instance's outcome.
2. **`A-FLOW-17`'s closing check should run in the same DEV session as the import**, before any
   other `wbs:6.10` verification: seed `RoundStatisticsHistoryStartDate` unset (forcing the
   `else` path) immediately after import succeeds, and confirm `historicApplicationsByMonth.months`
   resolves to `[]` with no flow failure — this is the one branch the naive version of the fix
   would have broken, per the Dev Summary's own reasoning.
3. **`IMP-0800`'s queue entry remains a live risk to the next build reaching `unit-tests`**
   (unchanged from v14's finding 2) — an improvement review should process it; not this gate's to
   action.
4. **`docs/improvements/2026-09-20-improvement-review-3.md` is parked awaiting the reviewer's own
   `APPROVE IMPROVEMENTS` keyword** — flagged for visibility, not requested here; per this
   session's own standing instruction, that keyword is never bundled with a test/review request.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | This cycle independently re-ran every figure claimed by `build-agent` (no drift found) and confirmed the new check-8 gate fails on the pre-fix shape and passes on the fixed shape via its own `--selftest`. No capture trigger from `skills/how-to-log-an-improvement.md` applies. |

Digest regenerated: **NO** (no new entry this cycle; `logs/known-failure-modes.md` already
reflects current log state).

---

CONSTRAINT CHECK
Domain   HARD: 6 / 6 of 6   |  violations: NONE
                            |  unevaluable: NONE
Domain   SOFT: 0 in scope   |  warnings:   NONE
Tech     HARD: 28 / 28 of 28  |  violations: NONE
                            |  unevaluable: NONE
                            |  deferred-to-pipeline: C-TECH-058 (evidence available after DEV import — see §5/§7.2)
Tech     SOFT: 1 in scope   |  warnings:   NONE
Overall: PASS

---

TEST REVIEW REQUIRED — docs/tests/trustee-portal-visual-refresh-test-report-v15.md  |  Result: PASS
Respond APPROVED to proceed to Pipeline, REQUEST RETEST to re-run, or give feedback for dev fixes.
