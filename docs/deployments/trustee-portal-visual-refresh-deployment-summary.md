# Deployment Summary — Trustee Portal Visual Refresh and Round-Statistics Landing Screen

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** build/artifacts/trustee-portal-visual-refresh-20260901-2/
**Date:** 2026-09-01
**WBS:** 6.9 (`contract/change-orders/CO-001.md`)

---

## Environment Results
| Environment | Deployed At | Status | Notes |
|---|---|---|---|
| Dev | 2026-09-01 23:08–23:21 | SUCCESS (V3) | Solution import + Code App push, both re-run once cleanly |
| Test/Acc | — | NOT ATTEMPTED | Out of scope — reviewer requested DEV only |
| Prd | — | NOT ATTEMPTED | Out of scope — reviewer requested DEV only |

## Test Gate — Reviewer Decision Carried Into This Deploy

`test-agent` approved Test Report v8 (result FAIL, on `C-TECH-053`/`C-TECH-064` only) with an explicit APPROVED-to-Pipeline decision, citing the standing `C-TECH-058` OVERRIDE recorded 2026-08-30 (`logs/pipeline.log:41`) as already covering the failing rows — a pre-existing round-statistics flow-trigger registration gap, unrelated to this build's own scope (statistics-visual percentage/chart/layout changes only, per `manifest.json` and the WBS 6.9 diff). This dispatch did not re-litigate that decision; it re-checked the override's rows are still open and none newly contradicted (below), per the same procedure every prior deploy in this chain has followed.

## Tenant-Level Operations
None this dispatch. `tenant_prerequisites` (`config/revitalise-grant-automation-pipeline.yml:188`) were satisfied and approved in earlier sessions; nothing in build -2's diff touches a tenant-level resource.

## Environment Prerequisites (C-TECH-050, C-TECH-051)
| Environment | Step | Result | Ids reconciled |
|---|---|---|---|
| Dev | All `environment_prerequisites` (`pipeline.yml:561`) | N/A — not this environment's first deploy; build -2's diff adds no new Entity/OptionSet/Role/FieldSecurityProfile | N/A |

## Access Preflight (C-TECH-065)
`PROVISION_APP_ID`/`PROVISION_CERT_THUMBPRINT` (the reviewer-held CI credential) are not set in this session — expected; they are CI secrets, correctly not committed locally. Per the precedent already recorded for builds -5/-8 (`logs/pipeline.log`), `pac org who` against the already-authenticated `svc_grantapplications@revitalise.org.uk` profile (already targeting `REV-GrantApplications-DEV`) was used as the equivalent read-only access proof:

```
PREFLIGHT: pac org who -Env dev — PASS (UserId 137f408b-2393-f111-b8db-70a8a5069b66)
```

## Post-Deployment Configuration
| Environment | Step | Result |
|---|---|---|
| Dev | `pac solution import` (unmanaged, `--force-overwrite --publish-changes --activate-plugins`) | SUCCEEDED — Import ID `e2773d62-49a6-f111-aaad-7ced8d43e1b4`, async 00:04:08.3, publish 00:00:53.3 |
| Dev | Re-run for idempotency (C-TECH-053) | SUCCEEDED cleanly — Import ID `910cfe81-4aa6-f111-aaad-7ced8d43e87d` |
| Dev | `pac code push --solutionName RevitaliseGrantAutomation` (`src/code-apps/trustee-review-portal`) | SUCCEEDED first attempt (app `70869c95-92e5-442f-b5b9-44b3d3e549f6`) |
| Dev | Re-run for idempotency | SUCCEEDED cleanly |

Pre-push, `diff -rq src/code-apps/trustee-review-portal/dist build/artifacts/trustee-portal-visual-refresh-20260901-2/code-app/` confirmed byte-identical content before pushing — the artifact pushed is the artifact built.

## Post-Deployment Smoke Tests
None declared for `dev` beyond the verification block below.

## Verification (C-TECH-053)

| Item | Pre-write (prior known state) | Post-write (measured this dispatch) | Result |
|---|---|---|---|
| `solutioncomponent` count for `RevitaliseGrantAutomation` | 66 | 66 (unchanged — expected: no new schema in this build) | PASS |
| `REV \| Portal \| Round Statistics` workflow | Activated, modified 8/31/2026 7:47 PM | Activated, modified 9/1/2026 9:19 PM — CLI reported *"The original workflow definition has been deactivated and replaced"* | PASS (accepted, same class as every prior import of this flow) |
| `rev_setting.RoundStatisticsStaleAfterSeconds` | 300 | 300 (unchanged) | PASS |
| `canvasapp` (Code App) `appversion`/`lastmodifiedtime`/`lastpublishtime` | 2026-08-31T19:52:08Z | 2026-09-01T21:21:25Z (both push and its idempotent re-run) | PASS |
| `callbackregistration` for `rev_roundstatisticsrequest` | `createdon` 2026-08-27 18:22 (`b184204a-44a2-f111-b8de-70a8a5079a1b`) | **UNCHANGED** — still 2026-08-27 18:22 | **STALE — carried forward, see below** |

All five rows measured by live `pac org fetch` query against DEV this dispatch, not inferred from any CLI exit code or prior session's log line.

**Level reached: DEV DEPLOYED (V3)** for the solution import and the Code App push — accepted by target, both re-run cleanly, every figure above confirmed by live query.

**Not reached: V4.** No named human has opened the flow, the Code App, or the model-driven app forms since this build's import.

### Known-broken surface carried forward (C-TECH-053 deploy-side rung)

Because this import again replaced the flow definition, the `callbackregistration` for `rev_roundstatisticsrequest` still predates the definition it is supposed to be watching — the same [IMP-0104](../../logs/known-failure-modes.md#L202)/[IMP-0114](../../logs/known-failure-modes.md#L207) mechanism recorded on every prior build in this chain (builds -5, -8, and now -2). This cannot be fixed via the Web API or by toggling `statecode`; it requires a named human opening the flow in the Power Automate **designer** (never the Solutions list), per [`config/revitalise-grant-automation-pipeline.yml:894-921`](../../config/revitalise-grant-automation-pipeline.yml#L894).

```
REVIEWER ACTION REQUIRED  |  feature:trustee-portal-visual-refresh  |  env:dev
Shell: the Power Automate maker portal — NOT a terminal
Open "REV | Portal | Round Statistics" in the Power Automate DESIGNER (never the Solutions
list). Turn it OFF, confirm the callbackregistration row for rev_roundstatisticsrequest
DISAPPEARS, then turn it ON FROM THE DESIGNER and confirm a row with a NEW createdon appears.
Verify afterwards with:
  pac org fetch --xmlFile <a file containing:>
  <fetch><entity name="callbackregistration"><attribute name="createdon"/>
  <filter><condition attribute="entityname" operator="eq" value="rev_roundstatisticsrequest"/>
  </filter></entity></fetch>
Expect createdon strictly after 2026-09-01T21:21 (this import's publish time).
```

Until that step runs, the round-statistics landing screen's live recompute path remains unproven end-to-end in this build, matching the standing `IMP-0511`/`A-R48` residual and the standing `C-TECH-058` OVERRIDE recorded 2026-08-30 (`logs/pipeline.log:41`) for `A-FLOW-03, A-FLOW-06, A-FLOW-09, A-FLOW-11, A-FLOW-13, A-LAND-3, A-LAND-4, A-TR-13` — all eight re-checked OPEN in [`docs/development/trustee-portal-visual-refresh-dev-summary.md` §10](../development/trustee-portal-visual-refresh-dev-summary.md) this dispatch (grepped directly against the live document, not assumed), none newly closed, none newly contradicted. This override is the reviewer's own standing instruction, already applied to the test-agent gate that authorised this dispatch — it is not re-decided here, only re-verified.

## Deployment Warnings Triaged (C-TECH-055)
No new warnings this dispatch. Manifest carries `8 total, 1 resolved, 7 accepted, 0 untriaged` (`build/artifacts/trustee-portal-visual-refresh-20260901-2/manifest.json`), all triaged in the current feature's Dev Summary (lines cited per-warning in the manifest itself).

## Rollback Availability
Previous artifact: `build/artifacts/trustee-portal-visual-refresh-20260831-8/` (last confirmed live DEV state before this deploy).
Rollback route (first-release posture, `rollback_artifact: ""` at [`pipeline.yml:182`](../../config/revitalise-grant-automation-pipeline.yml#L182)): re-import build -8's unmanaged zip and re-push its `dist/`; DEV carries no managed-solution rollback path yet.

## Issues Encountered
- `pac solution import` (both runs) exceeded the harness's foreground command timeout and was auto-moved to a background OS task by the tool itself (not requested); each was waited on to completion by polling its own output file before proceeding — no step was left unresolved, no dangling `WRITE_BEGUN:` line, no Monitor created against this dispatch's own background child (per this dispatch's brief).
- `pac org fetch --xml "<inline string>"` failed with an unrelated `System.Xml.XmlException` in this session even for a syntactically valid query; writing the identical FetchXML to a file and using `--xmlFile` worked every time. Recorded as a tooling quirk of this local pac 2.4.1 install, not a data or deploy defect — every verification query in this document used the file form.

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | The stale-callback-registration outcome is the already-documented IMP-0104/IMP-0114/IMP-0511 mechanism, anticipated by the standing C-TECH-058 override — not a new lesson. The inline `--xml` failure is a first observation in this repo's log (not previously recorded) but did not block or retry any deploy step, and `--xmlFile` is now the established working form for future sessions — recorded here rather than as a separate improvement-log entry, since no gate, deploy step, or reviewer expectation was affected. |

Digest regenerated: NO — no entry appended, so `logs/known-failure-modes.md` is unchanged this dispatch.

---

## HANDOFF

```
HANDOFF | from:pipeline-agent | to:pm-agent | feature:trustee-portal-visual-refresh | status:READY | doc:logs/pipeline.log (2026-09-01 23:08-23:21 entries)
HANDOFF | from:pipeline-agent | to:commercial-agent | feature:trustee-portal-visual-refresh | status:READY | doc:logs/pipeline.log (2026-09-01 23:08-23:21 entries)
```

WBS deliverables landed: `6.9` — statistics-visual percentage/chart/layout changes (solution import, flow definition replacement as a side effect of any import, and Code App push), both re-run cleanly. Level reached: **DEV DEPLOYED (V3)**. V4 outstanding: named human open-and-save on the flow (designer re-registration, above) and on the Code App. Promotion beyond DEV **not attempted** — reviewer's stated scope for this dispatch was DEV only.
