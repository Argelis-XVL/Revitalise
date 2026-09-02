# Deployment Summary — Trustee Portal Visual Refresh and Round-Statistics Landing Screen

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** build/artifacts/trustee-portal-visual-refresh-20260902-5/
**Date:** 2026-09-02
**WBS:** 6.8

---

## Environment Results
| Environment | Deployed At | Status | Notes |
|---|---|---|---|
| Dev | 2026-09-02 16:01–16:10 | SUCCESS (V3) | Revision 1.10 (`IMP-0581` fix — x-axis category-tick label `dy` arithmetic), redeployed over the already-DEV-deployed `20260902-2` build (commit `186f7d3`). Solution import + Code App push, both re-run once cleanly |
| Test/Acc | — | NOT ATTEMPTED | Out of scope — reviewer requested DEV only |
| Prd | — | NOT ATTEMPTED | Out of scope — reviewer requested DEV only |

## Test Gate — Reviewer Decision Carried Into This Deploy

`test-agent` sent APPROVED against [`docs/tests/trustee-portal-visual-refresh-test-report-v11.md`](../tests/trustee-portal-visual-refresh-test-report-v11.md) (PASS, 771/771 tests, no HARD violations against this revision's own scope — the one reviewer post-deploy feedback item `IMP-0581`: x-axis tick labels still touched the plot's bottom edge after Revision 1.9's fix, because the first wrapped line's `dy` reserved a baseline position, not a visible gap). The reviewer responded APPROVED to proceed to Pipeline. `C-TECH-064` (round-statistics flow trigger registration staleness) is pre-existing and unrelated to this UI-only revision — re-confirmed unchanged, live, this dispatch (see Verification below) — and is covered by the standing [C-TECH-058 OVERRIDE](../../logs/pipeline.log) recorded at `logs/pipeline.log:41`, already applied to the three prior deploy cycles on this feature. This dispatch did not re-decide or re-diagnose that override; it cited it and re-confirmed the condition is unchanged.

## Confirmed live, not assumed from the Dev Summary or the test report: this is a Code-App-only change

- `RevitaliseGrantAutomation.zip` content (md5 of the packed zip) **differs** from the already-deployed `20260902-2` build (`d30c9720…` vs `832514b0…`) — unlike the `-1`→`-2` step, this is NOT a byte-identical solution zip. The `code-app/` `dist/` differs by design (new `dy` constants in `RoundStatisticsCharts.tsx`; only the JS asset filename/content-hash and `index.html`'s script reference actually change — CSS is byte-identical per the test report's own `diff -rq`).
- `solutioncomponent` count for `RevitaliseGrantAutomation` measured **before** this dispatch's writes (66, unchanged since `20260902-1`/`-2`) and **after** (66) — unchanged. Confirms the zip difference is packaging/timestamp-level, not a new schema/flow/security component.
- No `environment_prerequisites` step was run: DEV's first-deploy prerequisites (`pipeline.yml`) were satisfied in earlier sessions, and this build's diff adds no new Entity/OptionSet/Role/FieldSecurityProfile.
- No tenant-level operation was in scope or attempted.

## Tenant-Level Operations
None this dispatch.

## Environment Prerequisites (C-TECH-050, C-TECH-051)
| Environment | Step | Result | Ids reconciled |
|---|---|---|---|
| Dev | All `environment_prerequisites` | N/A — not this environment's first deploy; build's diff adds no new schema (confirmed live, see above) | N/A |

## Access Preflight (C-TECH-065)
`PROVISION_APP_ID`/`PROVISION_CERT_THUMBPRINT` (the reviewer-held CI credential) are not set in this local session — expected; they are CI secrets, correctly not committed locally. Per the precedent recorded for every prior local dispatch on this feature (`logs/pipeline.log`), `pac org who` against the already-authenticated `svc_grantapplications@revitalise.org.uk` profile (already targeting `REV-GrantApplications-DEV`) was used as the equivalent read-only access proof, run before any write:

```
PREFLIGHT: pac org who -Env dev — PASS (UserId 137f408b-2393-f111-b8db-70a8a5069b66)
```

## Post-Deployment Configuration
| Environment | Step | Result |
|---|---|---|
| Dev | `pac solution import` (unmanaged, `--force-overwrite --publish-changes --activate-plugins`) | SUCCEEDED — Import ID `899350c9-d6a6-f111-aaad-7ced8d43e87d`, async 00:02:18.83, publish `4a49211b-d7a6-f111-aaad-7ced8d43e87d` 00:00:36.57 |
| Dev | Re-run for idempotency (C-TECH-053) | SUCCEEDED cleanly — Import ID `3310b441-d7a6-f111-aaad-7ced8d43e87d`, publish `038719a3-d7a6-f111-aaad-7ced8d43e87d` |
| Dev | `pac code push --solutionName RevitaliseGrantAutomation` (`src/code-apps/trustee-review-portal`) | SUCCEEDED first attempt (app `70869c95-92e5-442f-b5b9-44b3d3e549f6`) |
| Dev | Re-run for idempotency | SUCCEEDED cleanly |

Pre-push, `diff -rq src/code-apps/trustee-review-portal/dist build/artifacts/trustee-portal-visual-refresh-20260902-5/code-app/` confirmed byte-identical content before pushing — the artifact pushed is the artifact built. Both `pac solution import` calls exceeded the harness's default foreground timeout and were held open synchronously by this dispatch (polled via Monitor to completion, per this dispatch's brief not to leave a step unresolved) — neither step was left unresolved and no dangling `WRITE_BEGUN:` line resulted.

## Post-Deployment Smoke Tests
None declared for `dev` beyond the verification block below.

## Verification (C-TECH-053)

| Item | Pre-write (measured before this dispatch's first write) | Post-write (measured this dispatch) | Result |
|---|---|---|---|
| `RevitaliseGrantAutomation.zip` content (md5) vs. already-deployed `20260902-2` | differs (`832514b0…` vs `d30c9720…`) | — | Expected — Code App dist changed; see note above |
| `solutioncomponent` count for `RevitaliseGrantAutomation` | 66 | 66 (unchanged — no new schema in this build) | PASS |
| `canvasapp` (Code App) `appversion`/`lastmodifiedtime`/`lastpublishtime` | 2026-09-02T12:07:59Z (from `20260902-2`'s deploy) | 2026-09-02T14:09:52Z (both push and its idempotent re-run) | PASS |
| `callbackregistration` for `rev_roundstatisticsrequest` | `createdon` 2026-08-27 18:22 (`b184204a-44a2-f111-b8de-70a8a5079a1b`) | **UNCHANGED** — still 2026-08-27 18:22 | **STALE — pre-existing, carried forward, see below** |

All four rows measured by live `pac org fetch` query against DEV this dispatch, not inferred from any CLI exit code or prior session's log line.

**Level reached: DEV DEPLOYED (V3)** for the solution import and the Code App push — accepted by target, both re-run cleanly, every figure above confirmed by live query.

**Not reached: V4.** No named human opened the flow, the Code App, or any form since this build's import in this dispatch.

### Known-broken surface carried forward (C-TECH-053 deploy-side rung) — not this revision's defect

Because this import again replaced the flow definition, the `callbackregistration` for `rev_roundstatisticsrequest` still predates the definition it is supposed to be watching — the same [IMP-0104](../../logs/known-failure-modes.md#L217)/[IMP-0114](../../logs/known-failure-modes.md#L213) mechanism recorded on every prior build in this chain. This is pre-existing (unrelated to this UI-only revision) and is covered by the standing `C-TECH-058` OVERRIDE recorded at `logs/pipeline.log:41` for `A-FLOW-03, A-FLOW-06, A-FLOW-09, A-FLOW-11, A-FLOW-13, A-LAND-3, A-LAND-4, A-TR-13` — all eight re-checked OPEN this dispatch via `python3 scripts/verify-assumption-register.py` (PASS — 33 rows OPEN project-wide, none contradicted), none newly closed, none newly contradicted. This override is the reviewer's own standing instruction, already applied to the three prior deploy cycles on this feature; per this dispatch's own brief it is cited, not re-diagnosed.

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
Expect createdon strictly after 2026-09-02T16:04 (this import's publish time).
```

## Deployment Warnings Triaged (C-TECH-055)
No new warnings this dispatch. Manifest carries `4 total, 1 resolved, 3 accepted, 0 untriaged` (`build/artifacts/trustee-portal-visual-refresh-20260902-5/manifest.json`), all triaged in the current feature's Dev Summary (lines cited per-warning in the manifest itself).

## Rollback Availability
Previous artifact: `build/artifacts/trustee-portal-visual-refresh-20260902-2/` (last confirmed live DEV state before this deploy).
Rollback route (first-release posture, `rollback_artifact: ""` at `config/revitalise-grant-automation-pipeline.yml:182`): re-push `20260902-2`'s `code-app/dist` via `pac code push`; the solution zip itself carries no schema/flow/security difference between the two builds (`solutioncomponent` count unchanged, 66) so no re-import is needed for rollback. DEV carries no managed-solution rollback path yet.

## Issues Encountered
- Both `pac solution import` runs exceeded the harness's foreground command timeout and were auto-moved to a background OS task by the tool itself (not requested); each was waited on to completion via a Monitor watch on its own output file before proceeding — no step was left unresolved, no dangling `WRITE_BEGUN:` line.

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | Every outcome matched the already-documented pattern from the three prior deploy cycles on this feature (unchanged `solutioncomponent` count, stale callback registration under the standing override). Nothing surprised this dispatch, retried on changed input, or required a human correction. `verify-improvement-log.py` confirmed OK — 581 entries, 0 unread blocker-severity findings. |

Digest regenerated: NO — no entry appended, so `logs/known-failure-modes.md` is unchanged this dispatch.

---

## HANDOFF

```
HANDOFF | from:pipeline-agent | to:pm-agent | feature:trustee-portal-visual-refresh | status:READY | doc:logs/pipeline.log (2026-09-02 16:01-16:10 entries)
HANDOFF | from:pipeline-agent | to:commercial-agent | feature:trustee-portal-visual-refresh | status:READY | doc:logs/pipeline.log (2026-09-02 16:01-16:10 entries)
```

WBS deliverables landed: `6.8` — Revision 1.10, the `IMP-0581` fix (x-axis category-tick label `dy` arithmetic in `RoundStatisticsCharts.tsx`, reserving a visible gap rather than a baseline position). Solution import and flow-definition replacement occurred as a side effect of any import (content-verified unchanged component count); Code App push carried the actual content change. Both writes re-run cleanly. Level reached: **DEV DEPLOYED (V3)**. V4 outstanding: named human open-and-save on the flow (designer re-registration, above) and on the Code App. Promotion beyond DEV **not attempted** — reviewer's stated scope for this dispatch was DEV only.
