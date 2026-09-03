# Deployment Summary — Trustee Portal Visual Refresh and Round-Statistics Landing Screen

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** build/artifacts/trustee-portal-visual-refresh-20260903-2/
**Date:** 2026-09-03
**WBS:** 6.8

---

## Environment Results
| Environment | Deployed At | Status | Notes |
|---|---|---|---|
| Dev | 2026-09-03 14:02–14:14 | SUCCESS (V3) | Third attempt at the identical reviewer-reported symptom — x-axis category-label overlap on the round-statistics charts (`IMP-0509`, `IMP-0577`, `IMP-0581`). Solution import + Code App push, both re-run once cleanly. **V4 NOT reached this dispatch — see "The one check this dispatch exists for" below** |
| Test/Acc | — | NOT ATTEMPTED | Out of scope — reviewer requested DEV only |
| Prd | — | NOT ATTEMPTED | Out of scope — reviewer requested DEV only |

## Test Gate — Reviewer Decision Carried Into This Deploy

`test-agent` sent APPROVED against [`docs/tests/trustee-portal-visual-refresh-test-report-v12.md`](../tests/trustee-portal-visual-refresh-test-report-v12.md) — **Status: PASS (source/V2, gated for pipeline) — with one residual explicitly NOT closed.** The one accepted SOFT technology warning is `C-TECH-067`, already triaged. Test-agent's own words on the residual (its §7.2/row 104): `RoundStatisticsCharts.tsx`'s `AXIS_LABEL_GAP`/`TICK_ASCENT_PX`/`FIRST_TICK_LINE_DY` constants are "confirmed at E4/V2 only, and NO HIGHER LEVEL IS CLAIMABLE FROM THIS SESSION" — `jsdom` computes no font-metric layout, so no vitest assertion and no `verify-css-arithmetic.py` run can close it, and this is the **third** attempt at the identical symptom, each of the prior two "caught only by a human on a rendered screen after a green suite" (`IMP-0509`, `IMP-0577`, `IMP-0581`). Reviewer responded APPROVED to proceed to Pipeline.

## The one check this dispatch exists for — and why it is not marked done

This dispatch's brief was explicit: the human open-and-save (V4) step is the *only* thing that can actually close the x-axis category-label overlap defect on `CategoryBarChart`/`WellbeingComparisonChart`, across all four categorical breakdowns (gender, age-range, ethnic-group, applicant-type) plus the wellbeing comparison chart.

**This pipeline-agent session did not perform that check, and says so by name rather than reporting generic V4 completion.** The reason is a capability gap, not an oversight: this session holds no browser, no screenshot tool, and no authenticated route into a signed-in Power Apps session — the Microsoft 365 MCP connector is unauthenticated this session (OAuth cannot be completed non-interactively), and no other tool in this session's toolset can render or view a live web UI. C-TECH-053(c) requires a **named human** for exactly this reason: three of the fifteen historical failures on this project were invisible to source-consistency checks and query-based verification alike, and this is the fourth-and-counting instance of that same class on this specific chart.

```
REVIEWER ACTION REQUIRED  |  feature:trustee-portal-visual-refresh  |  env:dev
Shell: a browser, signed in as a real trustee (or any account holding only REV Trustee) — NOT a terminal
Open https://apps.powerapps.com/play/e/2f7ce6a9-fdb7-e10b-a40a-07f5022ee453/app/70869c95-92e5-442f-b5b9-44b3d3e549f6
  (the exact URL `pac code push` returned this dispatch, confirming this build's app version)
Open the landing screen's round-statistics section and look, for EACH of the following five charts, at
whether the x-axis category labels now clear the bottom of the plot area with visible whitespace, or
still touch/overlap it:
  1. CategoryBarChart — gender breakdown
  2. CategoryBarChart — age-range breakdown
  3. CategoryBarChart — ethnic-group breakdown
  4. CategoryBarChart — applicant-type breakdown
  5. WellbeingComparisonChart
State the outcome per chart, explicitly and by name, in the round-trip back to this feature's next
pipeline-agent dispatch: "clears" or "still overlaps" for each of the five. "Still overlaps" is an
expected-possible outcome given this is the third attempt at this symptom — it is not itself a
dispatch failure, and it is exactly the answer this check exists to be able to give.
Verify by looking at the rendered screen. A clean vitest run, a clean verify-css-arithmetic.py run, or
this dispatch's own live queries below are NOT evidence either way for this specific check — test-agent's
own report says so explicitly, and that is why this step is manual.
```

Until that outcome is recorded, this environment stays at **DEV DEPLOYED (V3)**, not V4, for this chart.

## Confirmed live, not assumed from the Dev Summary or the test report: this is a Code-App-only change

- `RevitaliseGrantAutomation.zip` content (md5) **differs** from the already-deployed `20260902-5` build (`65590b94…` vs `d30c9720…`) — the `code-app/` `dist/` differs by design (source confirmed this session to carry the `AXIS_LABEL_GAP`/`TICK_ASCENT_PX`/`FIRST_TICK_LINE_DY` constants at `RoundStatisticsCharts.tsx` lines 330–338).
- `solutioncomponent` count for `RevitaliseGrantAutomation` measured **before** this dispatch's writes (66, unchanged since `20260902-1` through `20260902-5`) and **after** (66) — unchanged. Confirms the zip difference is packaging/timestamp-level, not a new schema/flow/security component.
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
| Dev | `pac solution import` (unmanaged, `--force-overwrite --publish-changes --activate-plugins`) | SUCCEEDED — Import ID `5870906b-8fa7-f111-aaad-7ced8d43e1b4`, async 00:03:32.34, publish `5f1b3deb-8fa7-f111-aaad-7ced8d43e1b4` 00:00:40.69 |
| Dev | Re-run for idempotency (C-TECH-053) | SUCCEEDED cleanly — Import ID `dd621465-90a7-f111-aaad-7ced8d43e1b4`, publish `140c22bf-90a7-f111-aaad-7ced8d43e1b4` 00:00:32.58 |
| Dev | `pac code push --solutionName RevitaliseGrantAutomation` (`src/code-apps/trustee-review-portal`) | SUCCEEDED first attempt (app `70869c95-92e5-442f-b5b9-44b3d3e549f6`) |
| Dev | Re-run for idempotency | SUCCEEDED cleanly |

Pre-push, `diff -rq src/code-apps/trustee-review-portal/dist build/artifacts/trustee-portal-visual-refresh-20260903-2/code-app/` confirmed byte-identical content before pushing — the artifact pushed is the artifact built. The first `pac solution import` call, and separately the first idempotency re-run, each exceeded the harness's default foreground command timeout (120s) and were moved by the tool itself to a background OS task; each was confirmed still alive by `ps -p`/`pgrep` before being polled to completion via a Monitor watch on its own output file. **One earlier attempt at the re-run import was killed client-side** (a `&`/`wait` shell construct inside a single foreground Bash call hit the same 120s ceiling and was sent SIGTERM) **before it produced any output** — `ps aux` confirmed no `pac solution import` process was still running afterwards, so nothing was left silently in flight, and the re-run was then relaunched correctly via the harness's own `run_in_background` and captured its own distinct Import ID (`dd621465…`, above). No dangling `WRITE_BEGUN:` line resulted for that killed attempt because it never reached a state worth logging as begun — the logged `WRITE_BEGUN`/`WRITE_ATTEMPTED` pair for the re-run is the one that actually ran.

## Post-Deployment Smoke Tests
None declared for `dev` beyond the verification block below.

## Verification (C-TECH-053)

| Item | Pre-write (measured before this dispatch's first write) | Post-write (measured this dispatch) | Result |
|---|---|---|---|
| `RevitaliseGrantAutomation.zip` content (md5) vs. already-deployed `20260902-5` | differs (`d30c9720…` vs `65590b94…`) | — | Expected — Code App dist changed; see note above |
| `solutioncomponent` count for `RevitaliseGrantAutomation` | 66 | 66 (unchanged — no new schema in this build) | PASS |
| `canvasapp` (Code App) `appversion`/`lastmodifiedtime`/`lastpublishtime` | 2026-09-02T14:09:52Z (from `20260902-5`'s deploy) | 2026-09-03T12:14:00Z (both push and its idempotent re-run) | PASS |
| `callbackregistration` for `rev_roundstatisticsrequest` | `createdon` 2026-08-27 18:22 (`b184204a-44a2-f111-b8de-70a8a5079a1b`) | **UNCHANGED** — still 2026-08-27 18:22 | **STALE — pre-existing, carried forward, see below** |

All four rows measured by live `pac org fetch` query against DEV this dispatch, not inferred from any CLI exit code or prior session's log line.

**Level reached: DEV DEPLOYED (V3)** for the solution import and the Code App push — accepted by target, both re-run cleanly, every figure above confirmed by live query.

**Not reached: V4.** For the flow/registration surface, no named human has re-registered the trigger since this build's import in this dispatch (carried-forward finding, see below). For the round-statistics chart overlap specifically — the actual point of this dispatch — see "The one check this dispatch exists for" above: this session cannot itself perform it, and it is handed to the reviewer by name rather than silently omitted or reported as generic V4 completion.

### `dev.verification[5]` (component-type completeness) — also not run live this session

`provisioning/dataverse/verify-solution-components.ps1 -Env dev`'s static half re-ran clean this session: `PASS - 70 root components declared in Solution.xml, every one has a definition on disk, and nothing on disk is undeclared` / `PASS — Solution source is internally consistent (root-components-resolve)`. The live half then threw on the same missing credential as the access preflight above (`PROVISION_APP_ID` not set) — this session holds neither `PROVISION_APP_ID` nor `PROVISION_CERT_THUMBPRINT`, confirmed by checking rather than merely unattempted, so per the "Reviewer-Executed Operations" absent-credential branch this was not retried in a different execution context. **REVIEWER ACTION REQUIRED** — with `PROVISION_APP_ID`/`PROVISION_CERT_THUMBPRINT` set to the DEV provisioning identity's credential, run:
```
pwsh provisioning/dataverse/verify-solution-components.ps1 -Env dev
```
and record here the date, the name of whoever ran it, and every PASS/FAIL line the script printed. This is carried forward from the prior dispatch on this feature (`docs/development/trustee-portal-visual-refresh-dev-summary.md`, WBS 6.8), unresolved for the same reason.

### Known-broken surface carried forward (C-TECH-053 deploy-side rung) — not this revision's defect

Because this import again replaced the flow definition, the `callbackregistration` for `rev_roundstatisticsrequest` still predates the definition it is supposed to be watching — the same [IMP-0104](../../logs/known-failure-modes.md#L217)/[IMP-0114](../../logs/known-failure-modes.md#L213) mechanism recorded on every prior build in this chain. This is pre-existing (unrelated to this UI-only revision) and is covered by the standing `C-TECH-058` OVERRIDE recorded at `logs/pipeline.log:41` for `A-FLOW-03, A-FLOW-06, A-FLOW-09, A-FLOW-11, A-FLOW-13, A-LAND-3, A-LAND-4, A-TR-13` — all eight re-checked OPEN this dispatch via `python3 scripts/verify-assumption-register.py` (PASS — 35 rows OPEN project-wide, none contradicted), none newly closed, none newly contradicted. This override is the reviewer's own standing instruction, already applied to the four prior deploy cycles on this feature; per this dispatch's own brief it is cited, not re-diagnosed.

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
Expect createdon strictly after 2026-09-03T14:07 (this import's publish time).
```

## Deployment Warnings Triaged (C-TECH-055)
No new warnings this dispatch. Manifest carries `79 total, 14 resolved, 65 accepted, 0 untriaged` (`build/artifacts/trustee-portal-visual-refresh-20260903-2/manifest.json`), all triaged in the current feature's Dev Summary (lines cited per-warning in the manifest itself).

## Rollback Availability
Previous artifact: `build/artifacts/trustee-portal-visual-refresh-20260902-5/` (last confirmed live DEV state before this deploy).
Rollback route (first-release posture, `rollback_artifact: ""` at `config/revitalise-grant-automation-pipeline.yml:182`): re-push `20260902-5`'s `code-app/dist` via `pac code push`; the solution zip itself carries no schema/flow/security difference between the two builds (`solutioncomponent` count unchanged, 66) so no re-import is needed for rollback. DEV carries no managed-solution rollback path yet.

## Issues Encountered
- The first `pac solution import` and the first idempotency re-run of it each exceeded the harness's foreground command timeout and were auto-moved to a background OS task by the tool itself; each was waited on to completion via a Monitor watch on its own output file.
- **One re-run attempt was killed client-side** (see Post-Deployment Configuration above) by a shell construct that itself hit the same 120s foreground ceiling. Confirmed via `ps aux` that no orphaned `pac solution import` process survived it before relaunching correctly. No live state was left ambiguous by this — the relaunched re-run produced its own distinct, freshly-captured Import ID.

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | Every deploy-mechanical outcome matched the already-documented pattern from the four prior deploy cycles on this feature (unchanged `solutioncomponent` count, stale callback registration under the standing override). The V4 chart-overlap check and the `dev.verification[5]` live run remain outstanding for the same already-documented reasons (no browser/render capability in this session; no live provisioning credential in this session) — neither is a new lesson. `verify-improvement-log.py` confirmed OK — 586 entries, 0 unread blocker-severity findings. |

Digest regenerated: NO — no entry appended, so `logs/known-failure-modes.md` is unchanged this dispatch.

---

## HANDOFF

```
HANDOFF | from:pipeline-agent | to:pm-agent | feature:trustee-portal-visual-refresh | status:READY | doc:logs/pipeline.log (2026-09-03 14:02-14:14 entries)
HANDOFF | from:pipeline-agent | to:commercial-agent | feature:trustee-portal-visual-refresh | status:READY | doc:logs/pipeline.log (2026-09-03 14:02-14:14 entries)
```

WBS deliverables landed: `6.8` — this build's Code App dist carries the `AXIS_LABEL_GAP`/`TICK_ASCENT_PX`/`FIRST_TICK_LINE_DY` fix (source-confirmed present at `RoundStatisticsCharts.tsx` lines 330–338), deployed and live at DEV (canvasapp `appversion` moved to `2026-09-03T12:14:00Z`). Solution import and flow-definition replacement occurred as a side effect of any import (content-verified unchanged component count); Code App push carried the actual content change. Both writes re-run cleanly. **Level reached: DEV DEPLOYED (V3).** V4 outstanding, named explicitly: (1) the round-statistics chart x-axis overlap check across all five named charts — this is the specific defect this dispatch was sent to close, and this session could not perform it (no render/browser capability) — handed to the reviewer above; (2) the flow designer re-registration (carried forward, pre-existing); (3) `dev.verification[5]` live component-completeness run (carried forward, missing credential). Promotion beyond DEV **not attempted** — reviewer's stated scope for this dispatch was DEV only.
