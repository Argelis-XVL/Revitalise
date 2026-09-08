# Test Report — Revitalise Grant Automation (DocuSign Acceptance Workflow Batch) — v2

**Feature Slug:** revitalise-grant-automation
**Artifact:** build/artifacts/revitalise-grant-automation-20260908-4/
**Date:** 2026-09-08
**Status:** PASS
**WBS:** 3.2 (Create Envelope), 3.3 (Reminders & Escalation), 3.4 (Completion)

---

**Revision note.** Supersedes
[`-20260908-4`](revitalise-grant-automation-test-report-20260908-4.md), which was `BLOCKED` on two
HARD constraint violations: `C-TECH-058` (six `OPEN`, DEV-closeable assumption rows with no
recorded reviewer `OVERRIDE`) and `C-TECH-053`'s deploy-side rung (the same six rows' V4-observable
surface not named as known-not-yet-verified before handover). Both are now discharged by the
reviewer's `OVERRIDE`, relayed by the coordinator and recorded in
[`docs/deployments/revitalise-grant-automation-deployment-summary.md` §"wbs:3.2/3.3/3.4 assumption-register override"](../deployments/revitalise-grant-automation-deployment-summary.md).
Nothing else in the original report changes — §§1–4, 6, and the requirement-coverage table below
are carried forward with their PARTIAL/PASS results unchanged; only §5 and §7 are revised here.

## 1. Test Summary

Unchanged from [`-20260908-4` §1](revitalise-grant-automation-test-report-20260908-4.md) — 1862
tests passed, 0 failed at the test-execution layer. The failures resolved by this revision were
constraint-level, not test-execution-level (see §5).

## 2. Requirement Coverage

Unchanged from [`-20260908-4` §2](revitalise-grant-automation-test-report-20260908-4.md#2-requirement-coverage).
FR-041/042/043/045 remain **PARTIAL** — the override does not manufacture live verification, it
records the reviewer's decision to ship ahead of it. FR-044 remains PASS (no DocuSign dependency).
FR-046 confirmed by design (no flow). FR-047 out of this batch's scope, unchanged.

## 3. Failed Tests

None at the constraint level, following the override recorded in the Deployment Summary addendum
(§5 below). The two rows in [`-20260908-4` §3](revitalise-grant-automation-test-report-20260908-4.md#3-failed-tests)
(T-DS-058, T-DS-053) are resolved, not deleted from the record — see §5.

## 4. Defects Raised

D-DS-01 and D-DS-02 (from `-20260908-4` §4) are **closed by override**, not by a code or config
fix. Recorded as closed-by-risk-acceptance, not closed-by-verification — the underlying wire-shape
assumptions (A-DS-2/3/8/9/10/11a) remain genuinely unverified against a live DocuSign response, per
the override's own reason. Nothing in §2's PARTIAL results should be read as upgraded to PASS by
this closure.

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-TECH-052 | Every hand-authored artefact has a register row | PASS | Unchanged from `-20260908-4` |
| **C-TECH-053** | Reported only at the level actually executed; deploy-side rung for a deferred V4-observable surface | **PASS** | Level reported honestly: V3 in DEV (established by build `-20260907-3`), V4 explicitly **not** performed. The 2026-08-29 amendment's requirement — a deferred V4-observable defect is named as a known-broken surface in the Deployment Summary before further handover — is now satisfied by [the addendum's §0](../deployments/revitalise-grant-automation-deployment-summary.md), which names all six rows and states plainly they remain unverified pending the DocuSign connection binding |
| **C-TECH-058** | OPEN §10 assumption blocks deployment to an environment where it could be closed, absent a recorded `OVERRIDE` | **PASS** | `OVERRIDE A-DS-2, A-DS-3, A-DS-8, A-DS-9, A-DS-10, A-DS-11a` recorded in [`docs/deployments/revitalise-grant-automation-deployment-summary.md`](../deployments/revitalise-grant-automation-deployment-summary.md), naming the reviewer (Xander Lykopoulos / Anna Southern) and the reason (shared precondition: `rev_SharedDocuSign` connection not yet bound to a live DocuSign connection in DEV — a tenant/connection provisioning gap, not a flow-logic defect) |
| C-DOM-033 | `rev_grant.rev_escalatedon` register row | PASS | Unchanged |

All other rows unchanged from [`-20260908-4` §5](revitalise-grant-automation-test-report-20260908-4.md#5-constraint--compliance-verification).

## 6. Provisioning Verification

Unchanged from [`-20260908-4` §6](revitalise-grant-automation-test-report-20260908-4.md#6-provisioning-verification).
The three still-OPEN designer/live-test items (`A-DS-2` wire shape, `A-DS-8`, `A-DS-9`, `A-DS-10`
wire-shape remainder, `A-DS-11a`) are now **overridden**, not closed — the "Result" column there
should be read as "OVERRIDDEN, per the Deployment Summary addendum" rather than "OPEN" as of this
revision, but the underlying provisioning fact (connection not yet bound) is unchanged.

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

Unchanged from [`-20260908-4` §7.1](revitalise-grant-automation-test-report-20260908-4.md#71-assumption-register-closure)
in substance — no row is newly `CLOSED` by this revision, and none should be read as such. The
**Result** column for `A-DS-2`, `A-DS-3`, `A-DS-8`, `A-DS-9`, `A-DS-10`, `A-DS-11(a)` changes from
`FAIL — closeable now, not closed, no OVERRIDE` to **`OVERRIDDEN — reviewer-accepted risk, recorded
in Deployment Summary addendum, 2026-09-08`**. This is a process resolution, not a technical one:
the platform facts these six rows guess at are exactly as unverified after this revision as before
it.

### 7.2 Verification levels achieved

Unchanged from [`-20260908-4` §7.2](revitalise-grant-automation-test-report-20260908-4.md#72-verification-levels-achieved).
V4 is still **NOT PERFORMED** — the override accepts that fact as a documented risk, it does not
retroactively perform the step. Any future report on this feature must keep reporting V4 as not
performed until an actual designer session and test envelope occur, regardless of this override
being on file.

## 8. Recommendations

1. Proceed to `pipeline-agent` — the constraint gate that was `BLOCKED` is now `PASS` per the
   recorded override. No further test-agent action is needed for wbs:3.2/3.3/3.4 at this level.
2. The connection-binding blockage the override names (`rev_SharedDocuSign` not yet bound to a
   live DocuSign connection in DEV) is the actual next action, and it is outside test-agent's
   scope — it is a `post_deploy` manual step per `config/revitalise-grant-automation-pipeline.yml`,
   owned by the reviewer.
3. Once that connection is bound, re-run this Test Report: the six overridden rows are expected to
   move from `OVERRIDDEN` to `CLOSED` at that point, not to stay overridden indefinitely — an
   override is a sequencing decision, not a permanent waiver of C-TECH-052/058.
4. Recommendation 3 from `-20260908-4` (stale test-count citations, `IMP-0669`) still stands,
   unaffected by this revision.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

**0 new entries this revision.** `IMP-0670` (logged against `-20260908-4`) is resolved by the
Deployment Summary addendum, not superseded — its lesson (re-check `C-TECH-058` every cycle
against current environment state, never carry it forward as "unchanged") stands regardless of
this override, and remains open in `logs/improvement-log.jsonl` pending `improvement-agent`
processing.

Digest regenerated: NO — no new finding this revision.
