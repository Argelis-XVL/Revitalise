# Deployment Summary — Trustee Portal Visual Refresh and Round-Statistics Landing Screen

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** build/artifacts/trustee-portal-visual-refresh-20260831-8/
**Date:** 2026-08-31
**WBS:** 6.9 (`contract/change-orders/CO-001.md`)

---

## Environment Results
| Environment | Deployed At | Status | Notes |
|---|---|---|---|
| Dev | 2026-08-31 21:37–21:49 | SUCCESS (V3) | Solution import + Code App push, both re-run once cleanly |
| Test/Acc | — | NOT ATTEMPTED | Out of scope — reviewer requested DEV only |
| Prd | — | NOT ATTEMPTED | Out of scope — reviewer requested DEV only |

## Tenant-Level Operations
None this dispatch. `tenant_prerequisites` (`config/revitalise-grant-automation-pipeline.yml:188`) were satisfied and approved in earlier sessions; nothing in build -8's diff touches a tenant-level resource.

## Environment Prerequisites (C-TECH-050, C-TECH-051)
| Environment | Step | Result | Ids reconciled |
|---|---|---|---|
| Dev | All `environment_prerequisites` (`pipeline.yml:561`) | N/A — not this environment's first deploy; build -8's diff adds no new Entity/OptionSet/Role/FieldSecurityProfile (`git diff --name-only HEAD -- 'src/solutions/RevitaliseGrantAutomation/Entities/*'` returns nothing) | N/A |

## Access Preflight (C-TECH-065)
`PROVISION_APP_ID`/`PROVISION_CERT_THUMBPRINT` (the reviewer-held CI credential) are not set in this session — expected; they are CI secrets, correctly not committed. Per the precedent already recorded for build -5 (`logs/pipeline.log`, 2026-08-31 13:59 entry), `pac org who` against the already-authenticated `svc_grantapplications@revitalise.org.uk` profile (already targeting `REV-GrantApplications-DEV`) was used as the equivalent read-only access proof:

```
PREFLIGHT: pac org who -Env dev — PASS (UserId 137f408b-2393-f111-b8db-70a8a5069b66)
```

## Post-Deployment Configuration
| Environment | Step | Result |
|---|---|---|
| Dev | `pac solution import` (unmanaged, `--force-overwrite --publish-changes --activate-plugins`) | CREATED/UPDATED — Import ID `26b2d068-73a5-f111-aaad-7ced8d43e1b4`, async 00:03:52.5, publish 00:00:48.9 |
| Dev | Re-run for idempotency (C-TECH-053) | SUCCEEDED cleanly — Import ID `f12c94c2-74a5-f111-aaad-7ced8d43e87d` |
| Dev | `pac code push --solutionName RevitaliseGrantAutomation` | SUCCEEDED first attempt |
| Dev | Re-run for idempotency | SUCCEEDED cleanly |

## Post-Deployment Smoke Tests
None declared for `dev` beyond the verification block below.

## Verification (C-TECH-053)

| Item | Pre-write (baseline) | Post-write (measured) | Result |
|---|---|---|---|
| `solutioncomponent` count for `RevitaliseGrantAutomation` | 66 | 66 (unchanged — expected: no new schema in this build) | PASS |
| `REV \| Portal \| Round Statistics` workflow | Activated, modified 8/31/2026 11:54 AM | Activated, modified 8/31/2026 7:47 PM — CLI reported *"The original workflow definition has been deactivated and replaced"* | PASS (accepted) |
| `rev_setting.RoundStatisticsStaleAfterSeconds` | 300 | 300 (unchanged) | PASS |
| `canvasapp` (Code App) `appversion`/`lastpublishtime` | 2026-08-31T11:56:54Z | 2026-08-31T19:52:08Z (see reconciliation addendum below) | PASS |
| `callbackregistration` for `rev_roundstatisticsrequest` | `createdon` 2026-08-27 18:22 (b184204a-44a2-f111-b8de-70a8a5079a1b) | **UNCHANGED** — still 2026-08-27 18:22 | **STALE — see below** |

**Level reached: DEV DEPLOYED (V3)** for the solution import and the Code App push — accepted by target, both re-run cleanly, all figures above confirmed by live query rather than inferred from a CLI exit code.

**Not reached: V4.** No named human has opened the flow, the Code App, or the model-driven app forms since this build's import.

### Known-broken surface carried forward (C-TECH-053 deploy-side rung)

Because this import replaced the flow definition, the `callbackregistration` for `rev_roundstatisticsrequest` now **predates** the definition it is supposed to be watching — the exact [IMP-0104](../../logs/known-failure-modes.md#L202)/[IMP-0114](../../logs/known-failure-modes.md#L207) mechanism: a registration surviving an import pins `logicappsversion` to a definition version that no longer exists, and Dataverse delivers events into nothing. This **cannot** be fixed via the Web API or by toggling `statecode` — it requires a named human opening the flow in the Power Automate **designer** (never the Solutions list), per [`config/revitalise-grant-automation-pipeline.yml:894-921`](../../config/revitalise-grant-automation-pipeline.yml#L894).

```
REVIEWER ACTION REQUIRED  |  feature:trustee-portal-visual-refresh  |  env:dev
Shell: the Power Automate maker portal — NOT a terminal
Open "REV | Portal | Round Statistics" in the Power Automate DESIGNER (never the Solutions
list). Turn it OFF, confirm the callbackregistration row for rev_roundstatisticsrequest
DISAPPEARS, then turn it ON FROM THE DESIGNER and confirm a row with a NEW createdon appears.
Verify afterwards with:
  pac org fetch --xml "<fetch><entity name='callbackregistration'><attribute name='createdon'/>
  <filter><condition attribute='entityname' operator='eq' value='rev_roundstatisticsrequest'/>
  </filter></entity></fetch>"
Expect createdon strictly after 2026-08-31T19:47 (this import's publish time).
```

Until that step runs, the round-statistics landing screen's live recompute path is not proven end-to-end in this build, matching the standing `IMP-0511`/`A-R48` residual and the standing `C-TECH-058` OVERRIDE recorded 2026-08-30 (`logs/pipeline.log:41`) for `A-FLOW-03, A-FLOW-06, A-FLOW-09, A-FLOW-11, A-FLOW-13, A-LAND-3, A-LAND-4, A-TR-13` — all eight re-checked OPEN in [`docs/development/trustee-portal-visual-refresh-dev-summary.md` §10](../development/trustee-portal-visual-refresh-dev-summary.md#L2136) this dispatch, none newly closed, none newly contradicted (`verify-assumption-register.py` PASS).

### Reconciliation addendum (21:37–21:55 dispatch pair)

Lead-agent dispatched a second pipeline-agent session at 21:44 to reconcile an apparent death of the 21:37 dispatch (last log line at hand-off time: an unclosed `WRITE_BEGUN` for the idempotency re-import). Live checks by the reconciling session, per [WORKFLOW.md's fourth/fifth case](../../agents/WORKFLOW.md#L89) rules, found:

- The 21:37 dispatch's **first** solution import had already **succeeded** (`WRITE_ATTEMPTED` for Import ID `26b2d068`, [`pipeline.log:52`](../../logs/pipeline.log#L52)) before it reported waiting on a self-created Monitor — only the idempotency re-run was actually incomplete.
- That re-run's OS process (PID 39225) was found **still running**, unusually — an orphaned child that survived past its dispatching turn. It was waited on synchronously (not restarted, no duplicate import) and completed cleanly (Import ID `5fb34135`).
- While waiting, four log lines the reconciling session did not write appeared in `logs/pipeline.log` between 21:48–21:49: an Import ID mislabeling (the publish operation's GUID `f12c94c2` attributed to the import rather than the import's own id `5fb34135`), and a `pac code push` pair. This is evidence of a **second, independently live pipeline-agent dispatch** also reconciling the same build concurrently (the run that produced the bulk of this document's Post-Deployment Configuration and Verification tables above) — logged as [IMP-0538](../../logs/known-failure-modes.md) (new class: concurrent pipeline-agent dispatch mislabels a shared async operation id).
- The reconciling session independently re-verified the Code App push rather than trusting the concurrently-appearing log line: `diff -rq` confirmed `src/code-apps/trustee-review-portal/dist/` byte-identical to build -8's `code-app/`, and re-ran `pac code push --solutionName RevitaliseGrantAutomation` itself (idempotent) — `canvasapp` `appversion`/`lastmodifiedtime`/`lastpublishtime` moved from `2026-08-31T19:49:24Z` to `2026-08-31T19:52:08Z`, which is the value now recorded in the Verification table above.
- Also re-confirmed independently: `solutioncomponent` count 66 (unchanged), and `REV | Portal | Round Statistics` `statecode`/`statuscode` = Activated/Activated post-import.
- The 21:37 dispatch's own final message ("I'll wait for the Monitor notification on the import before proceeding further") was logged as [IMP-0537](../../logs/known-failure-modes.md) — the 8th recorded instance of the `dispatched-agent-stalls-silently` class, recurring the same day `agents/WORKFLOW.md` gained its "preempt it in the prompt" prose fix (`IMP-0520`).

No data damage resulted: both concurrent actors' writes were idempotent and the final live state (confirmed above) is consistent and correct. **V3 verification level applies** to every figure in this addendum — each was confirmed by a live query run by the reconciling session itself, not inferred from another session's log line or from a CLI exit code.

## Deployment Warnings Triaged (C-TECH-055)
No new warnings this dispatch. Manifest carries `43 total, 43 accepted, 0 untriaged` (`build/artifacts/trustee-portal-visual-refresh-20260831-8/manifest.json`), all triaged in the current feature's Dev Summary per [§0.15](../development/trustee-portal-visual-refresh-dev-summary.md#L2334).

## Rollback Availability
Previous artifact: `build/artifacts/trustee-portal-visual-refresh-20260831-5/` (last confirmed live DEV state before this deploy).
Rollback route (first-release posture, `rollback_artifact: ""` at [`pipeline.yml:182`](../../config/revitalise-grant-automation-pipeline.yml#L182)): re-import build -5's unmanaged zip and re-push its `dist/`; DEV carries no managed-solution rollback path yet.

## Issues Encountered
- `pac solution import` exceeded the harness's 120s foreground command cap on both runs and was auto-moved to a background task by the tool itself (not requested); waited on it to completion via a blocking `Monitor` before proceeding — no step was left unresolved, no dangling `WRITE_BEGUN:` line.
- Build -8's artifact was packed from a working tree with committed-vs-dirty divergence in 9 paths under `src/`/`config/` (recorded in `manifest.json`'s own `source_commit_note`) — unchanged from build-agent's own disclosure, not something this dispatch altered.

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | The stale-callback-registration outcome is the already-documented IMP-0104/IMP-0114/IMP-0511 mechanism, anticipated by `pipeline.yml`'s own declared manual step — not a new lesson. The 120s-timeout auto-backgrounding was handled within this dispatch (blocking Monitor wait) and left no gap in the record. |
| IMP-0537 | dispatched-agent-stalls-silently | friction | The prose-only "preempt it in the prompt" fix (`IMP-0520`, applied earlier the same day) did not prevent an 8th recorded instance — a second recurrence after a prose fix is the ladder's signal to escalate altitude to a mechanical dispatch-composition checklist. |
| IMP-0538 | concurrent-pipeline-dispatch-mislabels-shared-operation-id (new class) | rework | Two live pipeline-agent dispatches reconciling the same feature concurrently, with no lease/lock on `logs/pipeline.log`, produced one factually wrong operation-id attribution — re-verify the specific live artifact yourself rather than trusting a concurrently-appearing log line, even one that looks like your own work. |

Digest regenerated: YES — `logs/known-failure-modes.md` regenerated after both entries (535 entries total, schema PASS).

---

## HANDOFF

```
HANDOFF | from:pipeline-agent | to:pm-agent | feature:trustee-portal-visual-refresh | status:READY | doc:logs/pipeline.log (2026-08-31 21:37-21:55 entries)
HANDOFF | from:pipeline-agent | to:commercial-agent | feature:trustee-portal-visual-refresh | status:READY | doc:logs/pipeline.log (2026-08-31 21:37-21:55 entries)
```

WBS deliverables landed: `6.9` — solution import (flow definition replacement) and Code App push, both re-run cleanly. Level reached: **DEV DEPLOYED (V3)**. V4 outstanding: named human open-and-save on the flow (designer re-registration, above) and on the Code App/model-driven forms. Promotion beyond DEV **not attempted** — reviewer's stated scope for this dispatch was DEV only.
