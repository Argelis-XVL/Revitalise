# Deployment Summary — Trustee Portal Visual Refresh and Round-Statistics Landing Screen

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** build/artifacts/trustee-portal-visual-refresh-20260903-3/
**Date:** 2026-09-03
**WBS:** 6.8

---

## Environment Results
| Environment | Deployed At | Status | Notes |
|---|---|---|---|
| Dev | 2026-09-03 16:29–16:44 (local) / 14:29–14:44 UTC | SUCCESS (V3) | **Fourth** attempt at the identical reviewer-reported symptom — x-axis category-label overlap on the round-statistics charts (`IMP-0509`, `IMP-0577`, `IMP-0581`, `IMP-0584`) — but the first backed by an independently reproduced real-Chromium measurement (three separate sessions: frontend-agent, development-agent, test-agent; consistent -4px broken / +23px fixed). Solution import + Code App push, both re-run once cleanly. **V4 NOT reached this dispatch — see "The one check this dispatch exists for" below** |
| Test/Acc | — | NOT ATTEMPTED | Out of scope — reviewer requested DEV only |
| Prd | — | NOT ATTEMPTED | Out of scope — reviewer requested DEV only |

## Test Gate — Reviewer Decision Carried Into This Deploy

`test-agent` sent APPROVED against [`docs/tests/trustee-portal-visual-refresh-test-report-v13.md`](../tests/trustee-portal-visual-refresh-test-report-v13.md) — **Status: PASS**, only the already-accepted `C-TECH-067` SOFT warning outstanding. This cycle is the first in the chain backed by a real Chromium `getBoundingClientRect()` Playwright visual-regression measurement (`src/code-apps/trustee-review-portal/src/test/visual/round-statistics-charts.visual.spec.ts`), independently re-run by test-agent itself: 2/2 PASS on the delivered tree, 2/2 FAIL at exactly `-4px` when the fix hunk is reverted, 2/2 PASS again once restored. This is the strongest evidence this defect has had across all four rounds. Reviewer responded APPROVED to proceed to Pipeline.

**Known, stated gap — not this dispatch's to close.** The new Playwright visual-regression spec exists and passes locally (verified independently by three sessions) but is **not yet wired into** `config/revitalise-grant-automation-build.yml` or `config/revitalise-grant-automation-pipeline.yml`. This dispatch's own pipeline-config-preflight checks do not reference it, and that absence is not read here as a defect in this deploy — it is a known follow-up, flagged for whoever next touches those two configs.

## The one check this dispatch exists for — and why it is not marked done

Even with the strongest evidence this defect has had — a real-Chromium measurement independently reproduced by three separate sessions — a signed-in DEV render remains the reviewer's own step per `C-TECH-053(c)`. This dispatch's brief states this explicitly and does not treat the Playwright evidence as a substitute for it: the human open-and-save/look (V4) step is still the only thing that can close the x-axis category-label overlap defect on `CategoryBarChart`/`WellbeingComparisonChart`, across all four categorical breakdowns (gender, age-range, ethnic-group, applicant-type) plus the wellbeing comparison chart, on the live app.

**This pipeline-agent session did not perform that check, and says so by name rather than reporting generic V4 completion.** The reason is a capability gap, not an oversight: this session holds no browser, no screenshot tool, and no authenticated route into a signed-in Power Apps session — the Microsoft 365 MCP connector is unauthenticated this session (OAuth cannot be completed non-interactively), and no other tool in this session's toolset can render or view a live web UI.

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
pipeline-agent dispatch: "clears" or "still overlaps" for each of the five. This is expected to be the
closing step of this whole chain, given the strength of this round's evidence — but it is still the
reviewer's own step, not something this dispatch can claim on its behalf.
Verify by looking at the rendered screen. A clean vitest run, a clean Playwright run, or this dispatch's
own live queries below are NOT evidence either way for this specific check.
```

Until that outcome is recorded, this environment stays at **DEV DEPLOYED (V3)**, not V4, for this chart.

## Confirmed live, not assumed from the Dev Summary or the test report: this is a Code-App-only change

- `RevitaliseGrantAutomation.zip` content (md5) **differs** from the already-deployed `20260903-2` build (`65590b94…` vs `428b0cab…`) — the `code-app/` `dist/` differs by design (new hashed asset `index-COpvohZh.js` replacing `index-dxqwn_UB.js`; `index.html` differs to match).
- `solutioncomponent` count for `RevitaliseGrantAutomation` measured **before** this dispatch's writes (66, unchanged since `20260902-1`) and **after** (66) — unchanged. Confirms the zip difference is packaging/timestamp-level, not a new schema/flow/security component.
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
| Dev | `pac solution import` (unmanaged, `--force-overwrite --publish-changes --activate-plugins`) | SUCCEEDED — Import ID `2d9206a4-9b91-459a-b706-b5f97f5d6465` (createdon 2026-09-03T14:30Z UTC, completedon 14:32Z) |
| Dev | Re-run for idempotency (C-TECH-053) | SUCCEEDED cleanly — Import ID `f0479d66-efc2-4319-b13f-f8e4063cc4e7` (createdon 2026-09-03T14:38Z UTC, completedon 14:41Z) |
| Dev | `pac code push --solutionName RevitaliseGrantAutomation` (`src/code-apps/trustee-review-portal`) | SUCCEEDED first attempt (app `70869c95-92e5-442f-b5b9-44b3d3e549f6`) |
| Dev | Re-run for idempotency | SUCCEEDED cleanly |

Pre-push, `diff -rq src/code-apps/trustee-review-portal/dist build/artifacts/trustee-portal-visual-refresh-20260903-3/code-app/` confirmed byte-identical content before pushing — the artifact pushed is the artifact built. Both `pac solution import` calls exceeded the harness's default foreground command timeout (120s) and were moved by the tool itself to a background OS task; each was polled to completion via a background watcher on its own output file rather than assumed from the client-side timeout. Import IDs were not printed by this `pac` version's stdout (unlike some earlier sessions' captures) and were instead read back live via `pac env fetch` against the `importjob` table, filtered on `solutionname` and `createdon` (`today`), matched to this dispatch's own wall-clock window — not attributed from any other session's log line, per the "never re-attribute an operation id you did not capture yourself" rule.

## Post-Deployment Smoke Tests
None declared for `dev` beyond the verification block below.

## Verification (C-TECH-053)

| Item | Pre-write (measured before this dispatch's first write) | Post-write (measured this dispatch) | Result |
|---|---|---|---|
| `RevitaliseGrantAutomation.zip` content (md5) vs. already-deployed `20260903-2` | differs (`65590b94…` vs `428b0cab…`) | — | Expected — Code App dist changed; see note above |
| `solutioncomponent` count for `RevitaliseGrantAutomation` | 66 | 66 (unchanged — no new schema in this build) | PASS |
| `canvasapp` (Code App) `appversion`/`lastmodifiedtime`/`lastpublishtime` | 2026-09-03T12:14:00Z (from `20260903-2`'s deploy) | 2026-09-03T14:42:39Z (both push and its idempotent re-run) | PASS |
| `callbackregistration` for `rev_roundstatisticsrequest` | `createdon` 2026-08-27 18:22 (`b184204a-44a2-f111-b8de-70a8a5079a1b`) | **UNCHANGED** — still 2026-08-27 18:22 | **STALE — pre-existing, carried forward, see below** |

All four rows measured by live `pac env fetch` query against DEV this dispatch, not inferred from any CLI exit code or prior session's log line.

**Level reached: DEV DEPLOYED (V3)** for the solution import and the Code App push — accepted by target, both re-run cleanly, every figure above confirmed by live query.

**Not reached: V4.** For the flow/registration surface, no named human has re-registered the trigger since this build's import in this dispatch (carried-forward finding, see below). For the round-statistics chart overlap specifically — the actual point of this dispatch — see "The one check this dispatch exists for" above: this session cannot itself perform it, and it is handed to the reviewer by name rather than silently omitted or reported as generic V4 completion.

### `dev.verification[5]` (component-type completeness) — also not run live this session

`provisioning/dataverse/verify-solution-components.ps1 -Env dev` needs `PROVISION_APP_ID`/`PROVISION_CERT_THUMBPRINT`, neither of which is present in this local session (confirmed by checking, not merely unattempted) — carried forward unresolved for the same reason as the prior two dispatches on this feature. **REVIEWER ACTION REQUIRED** — with `PROVISION_APP_ID`/`PROVISION_CERT_THUMBPRINT` set to the DEV provisioning identity's credential, run:
```
pwsh provisioning/dataverse/verify-solution-components.ps1 -Env dev
```
and record here the date, the name of whoever ran it, and every PASS/FAIL line the script printed.

### Known-broken surface carried forward (C-TECH-053 deploy-side rung) — not this revision's defect

Because this import again replaced the flow definition, the `callbackregistration` for `rev_roundstatisticsrequest` still predates the definition it is supposed to be watching — the same [IMP-0104](../../logs/known-failure-modes.md#L217)/[IMP-0114](../../logs/known-failure-modes.md#L213) mechanism recorded on every prior build in this chain. This is pre-existing (unrelated to this UI-only revision) and is covered by the standing `C-TECH-058` OVERRIDE recorded at `logs/pipeline.log:41` for `A-FLOW-03, A-FLOW-06, A-FLOW-09, A-FLOW-11, A-FLOW-13, A-LAND-3, A-LAND-4, A-TR-13` — re-checked this dispatch via `python3 scripts/verify-assumption-register.py` (PASS — 35 rows OPEN project-wide, none contradicted), none newly closed, none newly contradicted. This override is the reviewer's own standing instruction, already applied to the four prior deploy cycles on this feature; per this dispatch's own brief it is cited, not re-diagnosed.

```
REVIEWER ACTION REQUIRED  |  feature:trustee-portal-visual-refresh  |  env:dev
Shell: the Power Automate maker portal — NOT a terminal
Open "REV | Portal | Round Statistics" in the Power Automate DESIGNER (never the Solutions
list). Turn it OFF, confirm the callbackregistration row for rev_roundstatisticsrequest
DISAPPEARS, then turn it ON FROM THE DESIGNER and confirm a row with a NEW createdon appears.
Verify afterwards with:
  pac env fetch --xmlFile <a file containing:>
  <fetch><entity name="callbackregistration"><attribute name="createdon"/>
  <filter><condition attribute="entityname" operator="eq" value="rev_roundstatisticsrequest"/>
  </filter></entity></fetch>
Expect createdon strictly after 2026-09-03T14:32Z (this import's publish time).
```

## Deployment Warnings Triaged (C-TECH-055)
No new warnings this dispatch. Manifest carries `8 total, 1 resolved, 7 accepted, 0 untriaged` (`build/artifacts/trustee-portal-visual-refresh-20260903-3/manifest.json`), all triaged in the current feature's Dev Summary (lines cited per-warning in the manifest itself).

## Rollback Availability
Previous artifact: `build/artifacts/trustee-portal-visual-refresh-20260903-2/` (last confirmed live DEV state before this deploy).
Rollback route (first-release posture, `rollback_artifact: ""` at `config/revitalise-grant-automation-pipeline.yml:182`): re-push `20260903-2`'s `code-app/dist` via `pac code push`; the solution zip itself carries no schema/flow/security difference between the two builds (`solutioncomponent` count unchanged, 66) so no re-import is needed for rollback. DEV carries no managed-solution rollback path yet.

## Issues Encountered
- Both `pac solution import` calls exceeded the harness's foreground command timeout and were auto-moved to a background OS task by the tool itself; each was waited on to completion via a background watcher on its own output file.
- This `pac` version's stdout did not print an Import ID for either call (unlike some earlier sessions on this feature) — both ids were instead recovered by live `pac env fetch` query against `importjob`, matched to this dispatch's own wall-clock window, not attributed from a differently-timed session's log line.

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | Every deploy-mechanical outcome matched the already-documented pattern from the prior deploy cycles on this feature (unchanged `solutioncomponent` count, stale callback registration under the standing override). The V4 chart-overlap check and the `dev.verification[5]` live run remain outstanding for the same already-documented reasons (no browser/render capability in this session; no live provisioning credential in this session) — neither is a new lesson. `verify-improvement-log.py --check` confirmed OK — 589 entries (145 NEW, 441 APPLIED, 3 REJECTED), 0 unread blocker-severity findings. |

Digest regenerated: NO — no entry appended, so `logs/known-failure-modes.md` is unchanged this dispatch.

---

## HANDOFF

```
HANDOFF | from:pipeline-agent | to:pm-agent | feature:trustee-portal-visual-refresh | status:READY | doc:logs/pipeline.log (2026-09-03 16:29-16:44 entries)
HANDOFF | from:pipeline-agent | to:commercial-agent | feature:trustee-portal-visual-refresh | status:READY | doc:logs/pipeline.log (2026-09-03 16:29-16:44 entries)
```

WBS deliverables landed: `6.8` — this build's Code App dist carries Revision 1.11 (`IMP-0590` fix, the x-axis tick/tspan `dy` composition defect), independently confirmed in a real Chromium render by three separate sessions before this deploy, and now deployed and live at DEV (canvasapp `appversion` moved to `2026-09-03T14:42:39Z`). Solution import and flow-definition replacement occurred as a side effect of any import (content-verified unchanged component count); Code App push carried the actual content change. Both writes re-run cleanly. **Level reached: DEV DEPLOYED (V3).** V4 outstanding, named explicitly: (1) the round-statistics chart x-axis overlap check across all five named charts on the live, signed-in DEV app — this is the specific defect this dispatch was sent to close, evidence is now the strongest it has been across all four rounds, and this session still could not perform the live-render step itself (no render/browser capability) — handed to the reviewer above as the expected closing step; (2) the flow designer re-registration (carried forward, pre-existing); (3) `dev.verification[5]` live component-completeness run (carried forward, missing credential). Promotion beyond DEV **not attempted** — reviewer's stated scope for this dispatch was DEV only.
