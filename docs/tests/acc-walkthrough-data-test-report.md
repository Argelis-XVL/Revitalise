# Test Report — TST/ACC Walkthrough Data (operational support, not a build)

**Feature Slug:** acc-walkthrough-data
**Artifact:** n/a — no build artifact; this is a data-seeding/verification action against an
already-deployed environment
**Date:** 2026-08-21 (re-run of the 2026-08-21 BLOCKED attempt, same day)
**Status:** BLOCKED — different reason than the first attempt. Both prior blockers are fixed;
data was seeded; the scoring flow did not fire.

---

## 1. Summary

Both blockers named in §3 of the first attempt are **confirmed fixed** — ground-truthed, not
assumed. Test data seeded cleanly: all 12 cases (TD-01..TD-12) created in
REV-GrantApplications-ACC (`test`). But `REV | Scoring | Calculate & Flag` did not fire for any
of them — 0 of 12 scored, 9 minutes after seeding, despite every documented precondition
passing. This is new, live evidence of a different defect from the identity/tenant problem the
first attempt hit. Emily's walkthrough still cannot show scoring outcomes or Teams review
cards; it can show the application forms/views, which have no test-data dependency.

## 2. What this session verified before touching data

1. **`provisioning/deploymentSettings/test-settings.json` line
   [28](../../provisioning/deploymentSettings/test-settings.json#L28)** — read directly: `"tenantId":
   "735a23b1-97d7-4c81-85f7-35c50321138a"`. No `{{TENANT_ID}}` placeholder remains. Confirmed by
   a plain file read, not inferred.
2. **The provisioning application user in REV-GrantApplications-ACC** — confirmed with a live
   `WhoAmI` call (per `knowledge/technology/testing-tools.md` lines
   [168-177](../../knowledge/technology/testing-tools.md#L168), the auth-triplet method), not
   inferred from DEV. It succeeded: `UserId=c8b2169f-5e9d-f111-b8de-7ced8d5f6ccb`,
   `OrganizationId=d92f0aeb-8697-f111-996a-002248daca61`. Its roles in TST/ACC are **System
   Administrator, System Customizer** — one short of DEV's **System Administrator, System
   Customizer, Environment Maker**, but System Administrator alone is what
   [test-data-common.psm1#L63-L67](../../provisioning/dataverse/test-data-common.psm1#L63) says
   this identity's writes rely on (it bypasses column security), so the missing Environment
   Maker role does not affect this task.

Both findings from the first attempt (`IMP-0145`, `IMP-0146`) are therefore evidenced as
resolved this session — recorded in prose here, not by editing their log entries, which is
`improvement-agent`'s decision to make.

## 3. What was then attempted, per IMP-0126's sequence

3. **Six IMP-0126 preconditions**, checked live against `test` before writing anything: all
   four REV flows Activated; a `callbackregistration` on `rev_application` exists (count 1,
   `createdon` 2026-08-21T12:12:56Z); `rev_ProcessOwnerUpn` = `esheardown@revitalise.org.uk`. All
   five `rev_*` environment variables read back as **value rows**, not definition defaults, so
   none are at risk from the next import
   ([known-failure-modes.md#L159](../../logs/known-failure-modes.md#L159), IMP-0121). All green.
4. **`remove-test-data.ps1 -Env test -Force`** — `Nothing to remove`, environment was already
   clean.
5. **`seed-test-data.ps1 -Env test`** — all 12 cases `CREATED` cleanly (REV-2026-1000 through
   REV-2026-1011), manifest written to `build/exports/test-data-seed-test.json`.
6. **Waited ~30s, then `verify-test-data.ps1 -Env test`** — **12 of 12 FAIL**. Every case reports
   `rev_scoredon is empty, so the scoring flow has not run against this row`. `TD-09` alone
   prints `PASS`, but that is not evidence the flow ran: TD-09's expected state (status 6,
   score empty) is what the seed data itself writes for the process-owner-already-decided case,
   not an outcome the flow produces.
7. **Re-checked after a further 2 minutes (9 minutes total since the earliest row)** — unchanged.
   Zero of 12 scored.

## 4. Ground truth gathered on why it did not fire

Not a guess — each of these is a live query, per
`skills/how-to-verify-a-platform-contract.md`:

- **`asyncoperations` regarding any of the 12 created applications: 0 rows**, and 0 rows of
  operation type Workflow in the whole environment in the last hour. Dataverse did not attempt
  to call the flow — this is not a run that failed, it is a run that never started.
- **`rev_errorlogs` created in the same window: 0 rows** (checked without the `TESTDATA-` prefix
  filter this time, since
  [remove-test-data.ps1#L116-L122](../../provisioning/dataverse/remove-test-data.ps1#L116) notes
  the scoring flow logs by the application's own name, not the submission id — still zero).
- **The `callbackregistration` is not stale by IMP-0114's own test**
  ([known-failure-modes.md#L157](../../logs/known-failure-modes.md#L157)): its `createdon`
  (2026-08-21T12:12:56Z) equals the workflow's `modifiedon`, not before it.
- **The live `subscriptionRequest` matches source exactly**: `scope=4` (Organization),
  `runas=3` (flow owner), `message=1` (Create), `entityname=rev_application` — identical to
  [REVScoringCalculateAndFlag...json#L64-L67](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVScoringCalculateAndFlag-8F1C2A44-1002-4B7A-9E21-0A1B2C3D4E02.json#L64).
  No drift between what was authored and what is live.
- **Writes and auditing are working normally** — a live `audits` row exists for the TD-01 create
  (see §6), which rules out a wholesale Dataverse outage; the failure is specific to this one
  trigger.
- **The flow's owner is a real, enabled service account** (`svc_grantapplications@revitalise.org.uk`),
  distinct from the identity these scripts authenticate as, with `runas=3` meaning the flow
  should execute as its owner regardless of who created the row — so this is not the
  ownership/scope trap
  [known-failure-modes.md#L155](../../logs/known-failure-modes.md#L155) (IMP-0106) describes.
- **`logs/pipeline.log` has no entry at all for the `tst_acc` stage.** This environment's
  `post_deploy` steps — including the named flow-reactivation diff step at
  [pipeline.yml#L834-L838](../../config/revitalise-grant-automation-pipeline.yml#L834) — were
  applied by a route this project's own logging does not capture, so there is no record of
  *how* the flow was last turned on in this environment.

None of this proves the root cause; it rules out several plausible ones (staleness, ownership,
subscription drift, a general outage) and leaves the Power Automate designer — which this
session has no route to — as the next diagnostic step, exactly as
[known-failure-modes.md#L153](../../logs/known-failure-modes.md#L153) (IMP-0104) and
[#L157](../../logs/known-failure-modes.md#L157) (IMP-0114) prescribe. Logged as
[IMP-0148](../../logs/improvement-log.jsonl) — the 13th recorded instance of the class
`exit-zero-does-not-mean-created`.

## 5. Who needs to fix what

- **A human with Power Automate maker access to REV-GrantApplications-ACC** must open `REV |
  Scoring | Calculate & Flag` in the designer and save it — or turn it off, confirm the
  `callbackregistration` row disappears, then turn it on from the designer and confirm a **new**
  `createdon` appears — per
  [known-failure-modes.md#L153](../../logs/known-failure-modes.md#L153) and
  [#L157](../../logs/known-failure-modes.md#L157). Never by toggling state or `PATCH`ing
  `statecode` via the Web API
  ([known-failure-modes.md#L175](../../logs/known-failure-modes.md#L175), IMP-0113) — this
  session did not attempt that, deliberately.
- **The 12 rows seeded this session are left in TST/ACC**, not torn down, so whoever does the
  designer fix can inspect them directly. They cannot be scored retroactively — a row-CREATED
  trigger never replays — so after the fix, `remove-test-data.ps1 -Env test -Force` then a fresh
  `seed-test-data.ps1 -Env test` is required before re-verifying.
- **Both blockers from the first attempt are closed** — no further action on the tenant-id
  placeholder or the missing application user.
- **Flagged, not re-logged**: `test-settings.json` (and `prd-settings.json`) still carry several
  unresolved `{{...}}` tokens outside `tenantId` — for example
  `dataverse.groupTeams[].entraGroupObjectId` at
  [test-settings.json#L213](../../provisioning/deploymentSettings/test-settings.json#L213) and
  [#L220](../../provisioning/deploymentSettings/test-settings.json#L220) — which
  [IMP-0147](../../logs/improvement-log.jsonl) already records would fail
  `bind-roles-to-groups.ps1 -Env test`, the first `tst_acc` `post_deploy` step. Unrelated to why
  this task's flow did not fire (this identity's scripts never read that path), but worth the
  same owner's attention before that step is next run for real.

## 6. WBS mapping — flagged, not resolved here (unchanged from the first attempt)

This task does not map to one WBS task id. `src/tests/data/scoring-test-data.json` line
[4](../../src/tests/data/scoring-test-data.json#L4) ties the underlying fixture to tasks `2.8`,
`4.5` and `0.9` (all "Test results / sign-off" or the Failure Alert deliverable per
`contract/wbs.json`), but a general walkthrough for Emily is explicitly **not** the WBS 2.8
formal "real data" sign-off the handoff distinguished it from. Per `PM-R30`, this is flagged for
`commercial-agent`'s normal billing pass rather than resolved here — a commercial question does
not halt delivery, and it has not halted this one; the block above is unrelated to it.

## 7. What Emily's walkthrough would exercise, once unblocked (topology unchanged from the first attempt)

The reviewer's four topics map to two Dataverse-triggered actions and one scheduled one, not
four independent things — this mapping does not change with today's finding, only the reason
it is still unreachable does:

- **Application forms/views/columns** — the `rev_application`/`rev_applicant` main forms and
  views already deployed with the solution; no test-data dependency. **Showable today,
  independent of §4's finding.**
- **Scoring outcome** — `REV | Scoring | Calculate & Flag`. Blocked by §4/§5 above.
- **Teams review cards** — sent by the *same* scoring flow (two `PostCardToConversation`
  actions), so blocked for the same reason.
- **Daily summary** — a separate flow on a Recurrence trigger (07:00 UTC, Monday–Friday). Even
  once the scoring flow is fixed and re-seeded, this flow still will not fire from seeding alone;
  Emily would need to wait for the next scheduled run or have a maker trigger a manual test run
  from the designer.

## 8. Constraint Verification

This task added no code and no solution component; it seeded data and ran live diagnostics.
Scope is the same as the first attempt's: constraints this specific action's evidence can now
speak to.

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Component reported only at the verification level actually executed | PASS | V3 confirmed live (12/12 rows created and independently queryable back). V5 **attempted and not achieved** — re-verified at T+9min, 0/12 scored. Reported at the level reached; V5 is not claimed, and V6 (the next environment) is not applicable here |
| [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) | Environment state that solution source cannot express is verified live | PASS (narrow) | `organizations?$select=isauditenabled` = true; `EntityDefinitions(rev_application/rev_applicant)?$select=IsAuditEnabled` = true for both; flow statecode/callbackregistration/subscriptionRequest all read live (§4). The full per-entity/optionset/fieldpermission sweep this constraint asks for after a deploy is `pipeline-agent`'s job and is not re-run by this data-seed action |
| [C-DOM-010](../../constraints/domain/domain-constraints.md#L47) | Create/update/delete on sensitive entities is audit-logged | PASS | Live `audits` row for the TD-01 create: `auditid=e0db3584-e607-445b-929f-2f74a9d3b75f`, `action=1` (Create), `_userid_value` populated, `changedata` carries every field written |
| [C-DOM-011](../../constraints/domain/domain-constraints.md#L48) | Audit log records carry timestamp/actor/action/entity id/before-after | PASS | Same audit row: `createdon=2026-08-21T12:55:37.485Z` (timestamp), `_userid_value` (actor), `action`/`operation` (action), `objecttypecode`/implicit record id (entity), `changedata` old→new per attribute (before/after) |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Every hand-authored platform contract has an Unvalidated Assumptions Register row | PASS | No new hand-authored platform artefact was introduced by this task — vacuously satisfied |

`C-TECH-001, 004, 006, 014, 040, 042, 045, 046, 048, 051, 054, 056-060` and `C-DOM-004, 030-032`
are in test-agent's scope but govern source/build content this task did not touch — not
re-evaluated here, not claimed PASS on today's evidence. `C-TECH-040` is deliberately not
scored against the provisioning application user's direct System Administrator assignment
confirmed in §2: that identity is a single-tenant provisioning/service principal, not a TAD §6.1
persona, its role was not created by this session, and the equivalent DEV assignment was already
accepted at the feature's own full test cycle
(`docs/tests/revitalise-grant-automation-test-report.md`) — re-adjudicating it here would be
outside this action's scope.

```
CONSTRAINT CHECK
Domain   HARD: 2 / 2 of 2  |  violations: NONE  |  unevaluable: NONE
Domain   SOFT: 0 in scope  |  warnings: NONE
Tech     HARD: 3 / 3 of 3  |  violations: NONE  |  unevaluable: NONE
Tech     SOFT: 0 in scope  |  warnings: NONE
Overall: PASS
```

The constraint check is clean; the **test result is not** — §1/§4 record a live functional
defect (the scoring flow not firing) that no constraint row above governs directly. `CONSTRAINT
CHECK: PASS` and report `Status: BLOCKED` are both correct at once: they measure different
things.

## 9. Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-0148](../../logs/improvement-log.jsonl) | `platform-state-divergence` (`exit-zero-does-not-mean-created`, now **x13**) | blocker | A non-stale `callbackregistration` plus a subscriptionRequest matching source exactly is still not proof a trigger fires — only creating a real row and watching it score is |

`IMP-0145` and `IMP-0146` (the first attempt's two blockers) are evidenced **resolved** by §2
above; no new log line for that, since it confirms rather than teaches something new.

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py` (145 entries, 395
lines).

---

## Approval

**Reviewed by:** ___________  **Date:** ___________  **Response:** a Power Automate designer
fix to `REV | Scoring | Calculate & Flag` in TST/ACC is required before this can be re-run
(§4/§5) — not a retest of test-agent's own work. The two provisioning blockers from the first
attempt do not need to be revisited.
