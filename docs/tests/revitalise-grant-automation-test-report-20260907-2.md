# Test Report — Revitalise Grant Automation (DocuSign Acceptance Workflow Batch, Phase-1 Variant)

**Feature Slug:** revitalise-grant-automation
**Artifact:** build/artifacts/revitalise-grant-automation-20260907-2/
**Date:** 2026-09-07
**Status:** PASS
**WBS:** 3.2 (Create Envelope), 3.3 (Reminders & Escalation), 3.4 (Completion) — phase-1 two-import
Dataverse workaround variant of the same automation validated in build `-20260906-3`

---

**Scope note.** This is not a re-test of the whole DocuSign batch. Everything except one column's
Field Security Profile permission is identical to `-20260906-3`
([test report](revitalise-grant-automation-test-report-20260906-3.md)), which this dispatch already
validated PASS-worthy at V2 (its FAIL there was a since-resolved process gate, not a defect in the
DocuSign content — see below). This report verifies only what changed: the deliberate, temporary
absence of `rev_grant.rev_escalatedon`'s `FieldPermission`, and re-confirms the level claim.

## 1. Test Summary
| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit (Pester) | Yes | 1022 | 0 | 1 |
| Regression | Yes | Solution Checker 0 Critical/High/Medium/Low/Informational | 0 | — |
| Security (field security coverage) | Yes | `field-security-coverage` PASS via baselined exception, re-run live | 0 | — |
| Platform Contract | Yes | No new orphans this batch; A-DS register unchanged from `-3` (not re-litigated per scope) | — | — |
| **Verification Level** | Yes | V2 confirmed; V3/V4 correctly not yet claimed (§7.2) | 0 | — |
| **Process gate** (`improvement-log-check`) | Yes | Re-run live: `-3`'s 3 blocking findings (IMP-0627/0628/0629) are now reviewer-deferred, not unread | 0 | — |
| **Total** | | 1022 (Pester) + 1 (field-security-coverage) + 1 (solution checker) | 0 | 1 |

## 2. Requirement Coverage
| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| wbs:3.2 | `rev_grant` created → DocuSign envelope via `REVAcceptanceCreateEnvelope` | Unchanged from `-3`; not re-tested this dispatch (out of scope delta) | PASS at V1/V2, carried from `-3` |
| wbs:3.3 | Reminders/escalation, including `rev_escalatedon` column | `verify-field-security-coverage.py src/solutions/RevitaliseGrantAutomation`, re-run live this dispatch | PASS — column ships `IsSecured=1`, permission correctly, deliberately absent under a scoped baseline (§5, §7.1) |
| wbs:3.4 | Completion → signed PDF to SharePoint | Unchanged from `-3`; not re-tested this dispatch | PASS at V1/V2, carried from `-3` |

## 3. Failed Tests
None.

## 4. Defects Raised
None. `-3`'s single defect (D-TEST-1, the `improvement-log-check` process-gate FAIL over IMP-0627/0628/0629
being unread) is resolved: re-running `python3 scripts/verify-improvement-log.py --check` live now reports
those three ids as **reviewer-deferred** (accepted deferral, not unread) — confirmed directly, not taken on
the manifest's word, per the exact discipline `-3`'s own D-TEST-1 demanded.

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-TECH-052 | Every hand-authored platform artefact has a register row | PASS | No new hand-authored artefact this batch beyond `-3`'s already-registered A-DS-1…11 rows; the FieldPermission removal is a baseline-file entry, not an unregistered artefact |
| C-TECH-053 | Reported only at the level actually executed | PASS | `logs/pipeline.log` has no successful import for `revitalise-grant-automation` after the [2026-09-07 00:52 FAILED entry](../../logs/pipeline.log) (async `f79e8d1b`, "Object reference not set to an instance of an object" on Field Security Profile import) — this build has not been imported anywhere; manifest's own `"verification_level": "V2 — packaged; layout accepted by the packer, content unverified"` is honest, not overstated (contrast `-3`'s corrected finding, `IMP-0631`) |
| C-DOM-030/031/032 | Special-category exclusion / secured / audited | PASS | `rev_grant.rev_escalatedon` register row confirmed present at [`constraints/domain/special-category-register.yml:308`](../../constraints/domain/special-category-register.yml#L308); `Entity.xml` unchanged (`IsSecured=1` throughout) |
| `field-security-coverage` (HARD, this dispatch's actual gate) | Every secured column released or covered by a dated, owned baseline | PASS (via baseline) | Re-run live: `python3 scripts/verify-field-security-coverage.py src/solutions/RevitaliseGrantAutomation` → `PASS — 69 secured column(s) … 1 baselined UNREADABLE finding(s)`, naming `rev_grant.rev_escalatedon`, `[BASELINED until 2026-09-14, owner development-agent, IMP-0638]` |
| Process gate: `improvement-log-check` | Every build gate must pass when re-run | PASS | See §4 |

**Deliberate-absence scoping confirmed, three ways, not one:** the same fact is recorded consistently
in [`config/gate-baselines.json:84-92`](../../config/gate-baselines.json#L84) (gate key, match string,
owner `development-agent`, expiry `2026-09-14`, `clears_when`, finding `IMP-0638`), in the live gate
output quoted above, and in a source-level comment at
[`Other/FieldSecurityProfiles.xml:587`](../../src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L587)
that additionally states the exact `FieldPermission` block to restore verbatim for phase 2. All three
agree on owner, scope and clearing condition — this is not a silent gap.

**One imprecision found, not blocking.** The source comment at line 587 states the DEV import "failed
identically twice" ("attempts 1-2"); `logs/pipeline.log` records exactly one matching FAILED entry
([2026-09-07 00:52](../../logs/pipeline.log)). The underlying justification (a real, logged, root-caused
platform null-reference on Field Security Profile import) stands on that one entry alone — the count
does not change the validity of the workaround — so this is not a defect, and is recorded as a friction
finding, `IMP-0646`.

## 6. Provisioning Verification
Not applicable to this delta — no new security role, group team, or app-sharing surface. Unchanged
from `-3` §6.

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure
Unchanged from `-3`'s [§7.1](revitalise-grant-automation-test-report-20260906-3.md#L91) (A-DS-1
through A-DS-11) — per this dispatch's brief, not re-litigated here. The only new item this batch
introduces is the baselined `field-security-coverage` exception above, which is a gate baseline, not
a Dev Summary §10 assumption, and does not add a row to that register.

### 7.2 Verification levels achieved

| Component | Level claimed (manifest) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Solution package (managed + unmanaged) | `V2 — packaged; layout accepted by the packer, content unverified` | **V2 confirmed** | Solution Checker ran live, correlation `234adde4-...`, `0 Critical/High/Medium/Low/Informational` ([`solution-checker/pac-solution-check-stdout.log`](../../build/artifacts/revitalise-grant-automation-20260907-2/solution-checker/pac-solution-check-stdout.log)); `logs/pipeline.log`'s last entry for this feature is the 00:52 FAILED import of the *previous* attempt (before this phase-1 workaround existed) — no entry shows this build's content accepted anywhere | PASS — honestly reported, matches `-3`'s corrected shape (`IMP-0631`) |
| `rev_grant.rev_escalatedon` field security | Deliberately unreleased, phase 1 of 2 | **Confirmed absent by design, not by accident** | `field-security-coverage` gate output above, plus source comment and baseline entry all agreeing | PASS |

- Idempotency: N/A this dispatch — no import has succeeded for this content.
- V4 designer/editor open + save: not reached, correctly not claimed — unreachable before a deploy.
- Cross-OS (C-TECH-054): `build_os: Darwin 25.6.0 arm64 (macOS, local build)` per manifest — local run, not CI; no cross-OS-specific script newly added this batch — N/A.
- Warnings triaged (C-TECH-055): manifest shows 8 warnings total, 1 resolved, 7 accepted — **0 untriaged** (contrast `-3`'s 2 untriaged). Each accepted warning cites a Dev Summary line and is recorded as pre-existing and unrelated to wbs:3.2/3.3/3.4 (`change-order-requirements`, `routing-reconciliation`, `review-document`, `commercial-events`, `derived-counts`, plus the two `EnsureSchema.Tests.ps1` literal-count assertions the dispatch brief named as C-TECH-067). Result: **PASS**.

## 8. Recommendations

1. Proceed to `pipeline-agent` for a DEV deploy of this phase-1 variant. A successful import is the
   only way to confirm the phase-1 workaround actually clears the "Object reference not set to an
   instance of an object" failure logged at [`logs/pipeline.log`, 2026-09-07 00:52](../../logs/pipeline.log)
   — that confirmation has not happened yet and is not claimed here.
2. Once phase 1 imports cleanly to DEV, dispatch the phase-2 build restoring `rev_grant.rev_escalatedon`'s
   `FieldPermission` per the verbatim block already recorded at
   [`FieldSecurityProfiles.xml:587`](../../src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L587),
   before the baseline's 2026-09-14 expiry.
3. When phase 2 touches that comment block, correct "failed identically twice"/"attempts 1-2" to match
   the single logged failure, or cite the second attempt if one occurred outside this session's visible log.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0646 | `source-comment-overstates-log-evidence` | friction | Before writing a specific repeat-count into a source comment or report, grep `logs/pipeline.log` for the matching entries and cite what is actually there. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`
