# Deployment Summary — Trustee Portal Visual Refresh and Round-Statistics Landing Screen

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** build/artifacts/trustee-portal-visual-refresh-20260902-2/
**Date:** 2026-09-02
**WBS:** 6.8

---

## Environment Results
| Environment | Deployed At | Status | Notes |
|---|---|---|---|
| Dev | 2026-09-02 12:00–12:09 | SUCCESS (V3) | Round-2 reviewer feedback rework, redeployed over the already-DEV-deployed `20260902-1` build (commit `c09804e`). Solution import + Code App push, both re-run once cleanly |
| Test/Acc | — | NOT ATTEMPTED | Out of scope — reviewer requested DEV only |
| Prd | — | NOT ATTEMPTED | Out of scope — reviewer requested DEV only |

## Test Gate — Reviewer Decision Carried Into This Deploy

`test-agent` sent APPROVED against [`docs/tests/trustee-portal-visual-refresh-test-report-v10.md`](../tests/trustee-portal-visual-refresh-test-report-v10.md) (PASS, no HARD violations against this revision's own scope — eight round-2 reviewer feedback items against the round-overview and application-detail screens). [C-TECH-064](../tests/trustee-portal-visual-refresh-test-report-v10.md#L76) (round-statistics flow trigger registration staleness) is pre-existing and unrelated to this UI-only revision — the test report confirms the packaged solution zip is byte-for-byte content-identical to the already-deployed `20260902-1` build, so this condition is unchanged, not new — and is covered by the standing [C-TECH-058 OVERRIDE](../../logs/pipeline.log) recorded at `logs/pipeline.log:41`, already applied to the two prior cycles on this feature. This dispatch did not re-decide or re-diagnose that override; it cited it and re-confirmed, live, that the condition is unchanged.

## Confirmed live, not assumed from the Dev Summary or the test report: this is a UI-only change

- `md5` of the unzipped `RevitaliseGrantAutomation.zip` content matched exactly between `build/artifacts/trustee-portal-visual-refresh-20260902-1/` and `-20260902-2/`, confirmed **before** the first write.
- `solutioncomponent` count for `RevitaliseGrantAutomation` measured **before** this dispatch's writes (66, unchanged since `20260902-1`) and **after** (66) — unchanged.
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
| Dev | `pac solution import` (unmanaged, `--force-overwrite --publish-changes --activate-plugins`) | SUCCEEDED — Import ID `f27003b1-c5a6-f111-aaad-7ced8d43e87d`, async 00:03:19.67, publish `b12cff24-c6a6-f111-aaad-7ced8d43e87d` 00:00:40.73 |
| Dev | Re-run for idempotency (C-TECH-053) | SUCCEEDED cleanly — Import ID `ce0c7063-c6a6-f111-aaad-7ced8d43e87d`, publish `db1921ba-c6a6-f111-aaad-7ced8d43e87d` |
| Dev | `pac code push --solutionName RevitaliseGrantAutomation` (`src/code-apps/trustee-review-portal`) | SUCCEEDED first attempt (app `70869c95-92e5-442f-b5b9-44b3d3e549f6`) |
| Dev | Re-run for idempotency | SUCCEEDED cleanly |

Pre-push, `diff -rq src/code-apps/trustee-review-portal/dist build/artifacts/trustee-portal-visual-refresh-20260902-2/code-app/` confirmed byte-identical content before pushing — the artifact pushed is the artifact built. Both `pac solution import` calls exceeded the harness's default foreground timeout and were held open synchronously by this dispatch (polled to completion, per this dispatch's brief not to background or Monitor its own work) — neither step was left unresolved.

## Post-Deployment Smoke Tests
None declared for `dev` beyond the verification block below.

## Verification (C-TECH-053)

| Item | Pre-write (measured before this dispatch's first write) | Post-write (measured this dispatch) | Result |
|---|---|---|---|
| `RevitaliseGrantAutomation.zip` content (md5 of unzipped tree) vs. already-deployed `20260902-1` | identical | identical | PASS — confirms this deploy carries no schema/flow/security change |
| `solutioncomponent` count for `RevitaliseGrantAutomation` | 66 | 66 (unchanged — expected: no new schema in this build) | PASS |
| `canvasapp` (Code App) `appversion`/`lastmodifiedtime`/`lastpublishtime` | 2026-09-02T09:14:04Z (from `20260902-1`'s deploy) | 2026-09-02T12:07:59Z (both push and its idempotent re-run) | PASS |
| `callbackregistration` for `rev_roundstatisticsrequest` | `createdon` 2026-08-27 18:22 (`b184204a-44a2-f111-b8de-70a8a5079a1b`) | **UNCHANGED** — still 2026-08-27 18:22 | **STALE — pre-existing, carried forward, see below** |

All four rows measured by live `pac org fetch` query against DEV this dispatch, not inferred from any CLI exit code or prior session's log line.

**Level reached: DEV DEPLOYED (V3)** for the solution import and the Code App push — accepted by target, both re-run cleanly, every figure above confirmed by live query.

**Not reached: V4.** No named human opened the flow, the Code App, or any form since this build's import in this dispatch.

### Known-broken surface carried forward (C-TECH-053 deploy-side rung) — not this revision's defect

Because this import again replaced the flow definition, the `callbackregistration` for `rev_roundstatisticsrequest` still predates the definition it is supposed to be watching — the same [IMP-0104](../../logs/known-failure-modes.md#L217)/[IMP-0114](../../logs/known-failure-modes.md#L213) mechanism recorded on every prior build in this chain. This is pre-existing (unrelated to this UI-only revision) and is covered by the standing `C-TECH-058` OVERRIDE recorded at `logs/pipeline.log:41` for `A-FLOW-03, A-FLOW-06, A-FLOW-09, A-FLOW-11, A-FLOW-13, A-LAND-3, A-LAND-4, A-TR-13` — all eight re-checked OPEN this dispatch via `python3 scripts/verify-assumption-register.py` (PASS — 33 rows OPEN project-wide, none contradicted), none newly closed, none newly contradicted. This override is the reviewer's own standing instruction, already applied to the two prior deploy cycles on this feature; per this dispatch's own brief it is cited, not re-diagnosed.

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
Expect createdon strictly after 2026-09-02T12:07 (this import's publish time).
```

## Deployment Warnings Triaged (C-TECH-055)
No new warnings this dispatch. Manifest carries `4 total, 1 resolved, 3 accepted, 0 untriaged` (`build/artifacts/trustee-portal-visual-refresh-20260902-2/manifest.json`), all triaged in the current feature's Dev Summary (lines cited per-warning in the manifest itself).

## Rollback Availability
Previous artifact: `build/artifacts/trustee-portal-visual-refresh-20260902-1/` (last confirmed live DEV state before this deploy — solution content identical, only the Code App dist differs).
Rollback route (first-release posture, `rollback_artifact: ""` at `config/revitalise-grant-automation-pipeline.yml:182`): re-push `20260902-1`'s `code-app/dist` via `pac code push`; the solution zip needs no re-import since it is content-identical. DEV carries no managed-solution rollback path yet.

## Issues Encountered
- `pac solution import` (both runs) exceeded the harness's foreground command timeout and was auto-moved to a background OS task by the tool itself (not requested); each was waited on to completion synchronously (polling its own output file) before proceeding — no step was left unresolved, no dangling `WRITE_BEGUN:` line, no Monitor created against this dispatch's own background child, per this dispatch's brief.

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | Every outcome matched the already-documented pattern from the two prior deploy cycles on this feature (byte-identical solution content, stale callback registration under the standing override). Nothing surprised this dispatch, retried on changed input, or required a human correction. |

Digest regenerated: NO — no entry appended, so `logs/known-failure-modes.md` is unchanged this dispatch.

---

## HANDOFF

```
HANDOFF | from:pipeline-agent | to:pm-agent | feature:trustee-portal-visual-refresh | status:READY | doc:logs/pipeline.log (2026-09-02 12:00-12:09 entries)
HANDOFF | from:pipeline-agent | to:commercial-agent | feature:trustee-portal-visual-refresh | status:READY | doc:logs/pipeline.log (2026-09-02 12:00-12:09 entries)
```

WBS deliverables landed: `6.8` — eight round-2 reviewer feedback items on the round-overview and application-detail screens (chart overflow, whitespace, stray chart bar, legend clipping, axis-label overlap, title position, button removal, action-row control), plus one incidentally-found defect (`IMP-0579`, `CompositionPieChart` scroll container). Solution import and flow-definition replacement occurred as a side effect of any import (content unchanged); Code App push carried the actual content change. Both writes re-run cleanly. Level reached: **DEV DEPLOYED (V3)**. V4 outstanding: named human open-and-save on the flow (designer re-registration, above) and on the Code App. Promotion beyond DEV **not attempted** — reviewer's stated scope for this dispatch was DEV only.
