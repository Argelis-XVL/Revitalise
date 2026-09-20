# Test Report — Revitalise Grant Automation

**Feature Slug:** `revitalise-grant-automation`
**Artifact:** `build/artifacts/revitalise-grant-automation-20260919-2/`
**Date:** 2026-09-19
**Status:** PASS
**WBS:** this build spans `3.2`, `3.3`, `3.4` (DocuSign acceptance, previously accepted), `8.2`
("Build finance security role", 2026-09-13) and carries `8.3`'s ("Build payment capture form")
own artefacts through the shared solution — see `docs/tests/revitalise-payment-capture-test-report.md`
for `8.3`'s own requirement coverage, which this report does not re-derive.

**Coverage note.** No test report has existed for this feature since revision 12 (2026-08-24). Two
builds since then — `20260910-3` and `20260913-1` — were never put through `test-agent`. This
report re-verifies from source and from live logs rather than carrying forward revision 12's
verdict, per `logs/known-failure-modes.md:102` (`C-TECH-058`).

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit / Regression (Pester, whole-solution) | Yes (source-level, per manifest) | 1023 | 0 | 1 (pre-existing) |
| Unit (code app: vitest/typecheck/lint) | Yes (per manifest, 83-step preflight) | all green | 0 | 0 |
| Integration | Partial — source/config only, no live query this cycle | — | 0 | — |
| End-to-End | Not run this cycle (no new deploy since `20260913-1`) | — | 0 | — |
| Regression | Yes — Solution Checker 0/0/0/0/0, negative-test coverage on all 64 gates | 64/64 | 0 | 0 |
| Security | Source-level only (role/privilege/column-security gates); no live Graph/Dataverse query this cycle | see §5/§6 | 0 | — |
| Accessibility | N/A this cycle — no new/changed screen in this build (payment-capture screen already covered by its own report) | — | — | N/A |
| Performance | N/A — no NFR threshold engaged by this build's scope | — | — | N/A |
| Provisioning | Source/settings-file verification; live TST/ACC/PRD queries deferred-to-pipeline (not yet imported there) | see §6 | 0 | deferred |
| Compliance | Yes — domain constraints re-checked, see §5 | — | 0 | — |
| **Total** | | **1023+/1023+** | **0** | **1 pre-existing** |

## 2. Requirement Coverage

This build's own new content (closing `IMP-0780` and `IMP-0777`) is configuration/deferral-record
work, not new functional requirements — its coverage is the Platform Contract audit in §7, not a
requirement table. Functional requirement coverage for the automations this artifact packages was
established by prior accepted reports and is not re-derived here:

| Scope | Requirement source | Prior verdict | Re-verified this cycle |
|---|---|---|---|
| DocuSign Acceptance (wbs:3.2–3.4) | `docs/tests/revitalise-grant-automation-test-report-20260908-4-v2.md` | PASS | Unchanged — no source touched since |
| Payment Capture form (wbs:8.3) | [`docs/tests/revitalise-payment-capture-test-report.md`](revitalise-payment-capture-test-report.md) | FAIL (3 P2, 2026-09-10) | **Yes — all three now resolved, see §4** |
| Finance security role (wbs:8.2) | New this build cycle, built 2026-09-13, never test-agent-reviewed | — | **Yes — see §4/§6** |

## 3. Failed Tests

None open. See §4 for the three defects re-verified closed this cycle.

## 4. Defects Raised (carried forward and re-verified)

| Defect ID | Severity | Description | Status this cycle | Evidence |
|---|---|---|---|---|
| D-01 | P2 | `C-TECH-052` orphan: Decimal-control classid on `rev_roundfinance` cited a register row (`A-FIN-03`) that resolves to an unrelated, already-closed assumption | **CLOSED** | [`docs/development/revitalise-grant-automation-dev-summary.md#IMP-0703 revision`](../development/revitalise-grant-automation-dev-summary.md) allocated a fresh row `A-FIN-08`; `verify-role-privilege-ownership.py`/assumption-register gates re-run PASS |
| D-02 | P2 | FR-154 (Bank Account nickname must not identify a natural person) shipped with a self-contradictory design and an unresolved business question (`OQ-151`) past its due date | **CLOSED** | `docs/architecture/revitalise-grant-automation-architecture.md:63-84` (rev 7/rev 8, 2026-09-10): `ADR-046a` added, and rev 8 records "Reviewer confirmed `ADR-046a`'s applicant-reimbursement nickname convention as proposed... SDD OQ-151 is closed". No further source change was needed — the shipped `<Description>` already matched the confirmed convention |
| D-03 | P2 | `wbs:8.3` derived `complete` from V1-only evidence, which TAD `ADR-047` and SDD §8 D-1 both forbid | **CLOSED (correctly downgraded)** | `logs/state/wbs-state.json:2105-2196` — the rule set was extended (`IMP-0705`) with a build-manifest rule, a pipeline-log rule and a manual V4 rule; `8.3` now derives `complete_pending_manual`, not `complete` |

**Note on D-02's live exposure window.** The original report warned the FR-154 gap "becomes
[an exposure] the moment `wbs:8.2` grants the finance role Read" — that grant has now happened
(`REV Finance`'s role privileges include Read/Write on `rev_bankaccount`/`rev_payment`, created
live in DEV 2026-09-13). Because `ADR-046a`'s design was reviewer-confirmed as-shipped (no code
change required), this does not reopen D-02, but it is the reason this defect was checked
explicitly this cycle rather than assumed still-closed from an older report.

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-DOM-030/031/032 | Special-category/audit invariants on secured columns | PASS | `domain-invariants` gate — manifest `constraint_check: PASS`, part of the 64-gate preflight |
| C-TECH-040 | Group teams only, no direct role assignment in Test/Acc/Prd | PASS (source), UNEVALUABLE (live TST/ACC/PRD — no import there yet this cycle) | `provisioning/deploymentSettings/test-settings.json`/`prd-settings.json` — `dataverse.groupTeams` model used throughout; DEV's direct-assignment exception is explicit and documented, not a violation (TAD's own stated DEV exception) |
| C-TECH-052 | Every hand-authored contract has a register row (no orphans) | PASS | D-01 above; `verify-assumption-markers.py` PASS this cycle per the 2026-09-13 revision's re-run (0 source markers with no register row) |
| C-TECH-053 | Verification level claimed matches level confirmed | PASS | §7.2 — every level claimed in the dev summary/deployment summary/wbs-state is the level actually reached; nothing overclaims |
| C-TECH-054 | Cross-OS: pipeline/CI scripts run on the CI runner's OS | UNEVALUABLE this cycle, informational | Build was packaged locally on Darwin (`manifest.json` `build_os`); the one CI-only step (`auth`) is correctly marked `steps_not_executed`/`when: ci`, not silently skipped |
| C-TECH-058 | OPEN assumption closeable in an existing environment, re-evaluated fresh | PASS | Investigated fresh against `logs/pipeline.log` (last DEV import: build `20260913-1`, 2026-09-13 20:05) and `contract/tad-deferrals.json`/deployment-summary override records — every DEV-closeable OPEN row already carries a standing reviewer OVERRIDE; nothing was carried forward unchanged from a prior cycle |

**CONSTRAINT CHECK**
```
Domain   HARD: 10 / 10  |  violations: NONE  |  unevaluable: NONE
Domain   SOFT: 0 in scope                     |  warnings: NONE
Tech     HARD: 37 / 37  |  violations: NONE  |  unevaluable: NONE (C-TECH-040/054's live-TST/ACC/PRD half is deferred-to-pipeline, not unevaluable — the evidence is not yet due; see skills/how-to-apply-constraints.md)
Tech     SOFT: 1 in scope                     |  warnings: C-TECH-067 (pre-existing, unaffected by this build)
Overall: PASS
```

## 6. Provisioning Verification

| Item | Expected | Verified Via | Result |
|---|---|---|---|
| `entra.appRegistrations` — SharePoint `Sites.Selected` scope | Decommissioned per `IMP-0777` (tenant-blocked) | `provisioning/deploymentSettings/test-settings.json:144`, `prd-settings.json:176` — dated decommission comment, no `Sites.Selected` left in either `requiredResourceAccess` array; identical in the packaged artifact | PASS |
| `entra.appRegistrations` — Dataverse `user_impersonation` scope | Real value, not a placeholder | `test-settings.json:120,153`, `prd-settings.json:152,185` — `78ce3f0f-a1ce-49c2-8cde-64b5c0896db4` present in both, no longer in either file's `_unresolved` array | PASS |
| `dataverse.groupTeams` — 4 Entra group object ids × ACC/PRD (8 total) | Real GUIDs, not placeholders | `test-settings.json:263,271,280,289`, `prd-settings.json:291,299,308,317` — all real, distinct GUIDs; `_unresolved` no longer lists any groupTeams entry | PASS |
| `REV Finance` security role | Created live in DEV, real `roleid` substituted into source | `docs/development/revitalise-grant-automation-dev-summary.md` (wbs:8.2 revision, 2026-09-13) — `roleid: 13523850-a5af-f111-aaac-7ced8d43e1b4`, `solutioncomponent` FetchXML confirms it as a live Role-type component | PASS (V3) |
| DEV solution import (build `20260913-1`) | Imported and published, idempotent re-run clean | `logs/pipeline.log:168-172` — SUCCEEDED, idempotent re-run SUCCEEDED, `pac solution list` confirms live | PASS (V3) |
| Cloud-flow statecode reconciliation after `20260913-1`'s `--force-overwrite` import | No flow silently deactivated (`IMP-0113`/`IMP-0136` class) | **Not performed** — needs `PROVISION_APP_ID`/`PROVISION_CERT_THUMBPRINT`, not available this session; explicitly flagged as unverified in `docs/deployments/revitalise-grant-automation-deployment-summary.md:1096` addendum | **OPEN — see Recommendations** |
| TAD formal record of the `Sites.Selected` decommission | A dated architecture/deployment-topology update | Not yet written — `docs/architecture/revitalise-grant-automation-architecture.md:1183,1837,2208` still lists `Sites.Selected` as `REV-MS-Provisioning`'s permission | **OPEN, but honestly declared as pending in the settings-file comment itself** — not a silent inconsistency |

## 7. Platform Contract & Verification-Level Audit

### 7.1 Assumption register closure (Dev Summary §10)

45 OPEN rows exist across the register as of the last dev-summary revision (2026-09-13).
`verify-assumption-register.py` and `verify-assumption-markers.py` both PASS (86 rows / 28
registers / 8 documents this cycle; no contradictions, no drift).

| Assumption ID | Claim | Closing precondition | Does it exist yet? | Result |
|---|---|---|---|---|
| A-FIN-09 | Platform-baseline privilege block is sufficient for the finance persona | `wbs:8.3`'s app-sharing lands + a signed-in test finance user (V4) | App-sharing artefacts exist in DEV since `20260913-1`; no test finance user has signed in yet | **Genuinely still OPEN — not closeable without a human V4 step, correctly not claimed closed** |
| A-FIN-08 / A-PAY-1 | Decimal-control classid `{C3EBB6DA-…}` is what the designer actually assigns | A human opens `rev_roundfinance`'s form once in DEV | DEV environment exists; human step not yet performed | **OPEN, correctly labelled** |
| A-TR-*, A-DS-*, A-FLOW-*, A-LAND-* (DEV-closeable set) | Various | DEV environment | All covered by a standing reviewer OVERRIDE already on record (`docs/deployments/revitalise-grant-automation-deployment-summary.md:1045-1057`) | **PASS — no silent carry-forward found** |
| A-G03 | SharePoint signed-PDF library ACL | No script can create the library | Not closeable by any current environment | **Correctly carried, not overridden** |

No orphan hand-authored contracts found this cycle (0 rows with no register entry).

### 7.2 Verification levels achieved

| Component | Level claimed | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| `RevitaliseGrantAutomation.zip` (build 2, this artifact) | V2 — packaged, layout accepted, content unverified | V2 confirmed | `manifest.json`: `verification_level: "V2"`, 83/83 steps, 64/64 gates | PASS |
| Solution content in DEV | V3 (build `20260913-1`, not yet re-imported at build 2) | V3 confirmed for `20260913-1`'s content; **build 2 (this artifact) has not itself been imported anywhere yet** | `logs/pipeline.log:172` | Accurate — nobody has claimed V3 for build 2 |
| `REV Finance` role | V3 accepted by target | V3 confirmed | dev-summary wbs:8.2 revision — role + 30 privileges `CREATED` live, `roleid` read back | PASS |
| Payment capture form (`wbs:8.3`) | complete_pending_manual (not V4) | Matches — no overclaim | `logs/state/wbs-state.json:2117` | PASS |

- **Idempotency:** DEV import re-run for build `20260913-1` — **PASS** (`logs/pipeline.log:170`, clean re-run, no diff-worthy error).
- **V4 designer/editor open + save:** **NOT YET PERFORMED** for `A-FIN-09`/`A-FIN-08`/`A-PAY-1` — correctly tracked as open, next gate is a reviewer/finance-user action, not a defect in this build.
- **Cross-OS (C-TECH-054):** build packaged on Darwin; the one CI-gated step (`auth`) is declared out-of-context, not silently skipped — **PASS**.
- **Warnings triaged (C-TECH-055) / diagnostics removed (C-TECH-056):** both accepted warnings (glob@10.5.0, chunk-size) are pre-triaged at `docs/development/revitalise-grant-automation-dev-summary.md#L4893`, 0 untriaged — **PASS**.

## 8. Recommendations

**Run the cloud-flow statecode reconciliation for `20260913-1` before this build promotes further.**
It has been an open, credential-gated item since 2026-09-13 (five days). The same reviewer who ran
`ensure-schema.ps1` by hand for the finance role could run
`provisioning/dataverse/reconcile-flow-statecodes.ps1 -Env dev` the same way. Until it runs, whether
any of the 8 REV flows was silently deactivated by the `--force-overwrite` import is unknown, not
clean.

**`TD-006`/`TD-007` (`IMP-0780`) are on a second unresolved extension cycle with no growing-pressure
mechanism.** Both now expire 2026-10-03 (`contract/tad-deferrals.json:16,28`), correctly recorded as
still-open architect-agent/commercial-agent decisions — not silently resolved. `IMP-0780`'s own
`proposed_change` (a pre-expiry warning in `verify-tad-coverage.py`) remains unimplemented; worth
raising to pm-agent/reviewer before the third cycle.

**Write the deferred TAD record for the `Sites.Selected` decommission.** The settings-file comment
(`test-settings.json:144`) already names this as pending; three lines in
`docs/architecture/revitalise-grant-automation-architecture.md` (1183, 1837, 2208) still describe a
permission that no longer exists in the live config.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | No new finding this cycle beyond what prior dispatches already logged (`IMP-0780`, `IMP-0777`, `IMP-0703`/`IMP-0707`, `IMP-0705`, `IMP-0732`) — this cycle re-verified those against ground truth and confirmed each disposition holds; nothing contradicted a document, no second attempt was needed, no human correction occurred |

Digest regenerated: NO — no new entries this cycle.
