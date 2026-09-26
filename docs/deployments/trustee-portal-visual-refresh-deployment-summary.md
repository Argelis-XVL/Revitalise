# Deployment Summary — Trustee Portal Visual Refresh and Round-Statistics Landing Screen

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** build/artifacts/trustee-portal-visual-refresh-20260903-3/
**Date:** 2026-09-03
**WBS:** 6.8

---

## Environment Results
| Environment | Deployed At | Status | Notes |
|---|---|---|---|
| Dev | 2026-09-03 16:29–16:44 (local) / 14:29–14:44 UTC | **VERIFIED (V4)** for the chart-overlap defect | **Fourth** attempt at the identical reviewer-reported symptom — x-axis category-label overlap on the round-statistics charts (`IMP-0577`, `IMP-0581`, `IMP-0584`; `IMP-0509` describes a different symptom — see "Findings Logged" below) — the first backed by an independently reproduced real-Chromium measurement (three separate sessions: frontend-agent, development-agent, test-agent; consistent -4px broken / +23px fixed), and now confirmed live by the reviewer. Solution import + Code App push, both re-run once cleanly. **V4 CONFIRMED 2026-09-03 by Xander Lykopoulos — see "The one check this dispatch exists for" below** |
| Test/Acc | — | NOT ATTEMPTED | Out of scope — reviewer requested DEV only |
| Prd | — | NOT ATTEMPTED | Out of scope — reviewer requested DEV only |

## Test Gate — Reviewer Decision Carried Into This Deploy

`test-agent` sent APPROVED against [`docs/tests/trustee-portal-visual-refresh-test-report-v13.md`](../tests/trustee-portal-visual-refresh-test-report-v13.md) — **Status: PASS**, only the already-accepted `C-TECH-067` SOFT warning outstanding. This cycle is the first in the chain backed by a real Chromium `getBoundingClientRect()` Playwright visual-regression measurement (`src/code-apps/trustee-review-portal/src/test/visual/round-statistics-charts.visual.spec.ts`), independently re-run by test-agent itself: 2/2 PASS on the delivered tree, 2/2 FAIL at exactly `-4px` when the fix hunk is reverted, 2/2 PASS again once restored. This is the strongest evidence this defect has had across all four rounds. Reviewer responded APPROVED to proceed to Pipeline.

**Known, stated gap — not this dispatch's to close.** The new Playwright visual-regression spec exists and passes locally (verified independently by three sessions) but is **not yet wired into** `config/revitalise-grant-automation-build.yml` or `config/revitalise-grant-automation-pipeline.yml`. This dispatch's own pipeline-config-preflight checks do not reference it, and that absence is not read here as a defect in this deploy — it is a known follow-up, flagged for whoever next touches those two configs.

## The one check this dispatch exists for — CONFIRMED 2026-09-03

**V4 CONFIRMED.** Xander Lykopoulos confirmed live, on this build (`build/artifacts/trustee-portal-visual-refresh-20260903-3/`, DEV, the exact app version this dispatch's `pac code push` produced), that the round-statistics chart x-axis category-label overlap is fixed. His words: *"its good now."*

- **Who:** Xander Lykopoulos (reviewer)
- **When:** 2026-09-03
- **What kind of check:** a direct visual check of the rendered screen in the live, signed-in DEV app — not a form open/save. The question put to him was specifically "do the x-axis labels clear the plot area", and the answer was yes.
- **Level reached: VERIFIED (V4)** for the round-statistics chart x-axis category-label overlap defect (`IMP-0577`, `IMP-0581`, `IMP-0584` — see "Findings Logged" below for how this closes the chain, and the one id this confirmation does **not** cover).

This closes the fourth and, per the reviewer's own confirmation, final round of this specific symptom — the strongest evidence this defect has had (three independent real-Chromium reproductions pre-deploy, per the Test Gate section above) is now backed by the actual named-human C-TECH-053(c) step.

No further detail beyond the reviewer's statement is recorded here (no per-chart breakdown was given, and none is fabricated) — the confirmation is reported exactly as received: a direct look at the live app, result "its good now."

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

**Level reached: VERIFIED (V4)** for the round-statistics chart x-axis category-label overlap defect specifically — the actual point of this dispatch — per Xander Lykopoulos's live confirmation recorded above (2026-09-03, direct visual check of the live app, "its good now").

**Still not reached: V4 for the flow/registration surface.** No named human has re-registered the trigger since this build's import in this dispatch (carried-forward finding, see below).

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

## Reconciliation note — this dispatch was a RECONCILIATION of a dangling `WRITE_BEGUN`, not a fresh deploy

The 16:29 `WRITE_BEGUN` for this build had no matching `WRITE_ATTEMPTED`, a prior dispatch's final message described waiting on a background-task notification that could never arrive (`agents/WORKFLOW.md` → "the fifth case"), and a subsequent lead-agent foreground attempt was itself refused by the classifier (`logs/pipeline.log`, 16:35 `WRITE_DENIED`), leaving true live status genuinely `UNKNOWN` at the start of this dispatch. This session found a **live, still-running** `pac solution import` OS process for this build (PID 17062) left behind by the dead dispatch's own backgrounded task, let it finish rather than starting a competing import, and verified everything by live query — never by trusting a log line.

Two additional facts surfaced only in this reconciliation, both material:

1. A queued background shell chain (also left behind by the dead dispatch) had already written correct `WRITE_ATTEMPTED — SUCCEEDED` log lines for the real imports and the code push, recovered by exactly the right method (a `solutionname`+`createdon today`-filtered `pac org fetch` against `importjob`, matched to wall-clock, never attributed from another session). This session's own **first** attempt to verify those lines used a broader, unfiltered `pac org fetch` query that silently omitted the live `2d9206a4-…` importjob row, leading this session to append a `CORRECTION` to `logs/pipeline.log` (16:42) wrongly calling that row fabricated. A second, properly-filtered query then produced conclusive evidence it was real, and a second `CORRECTION` (16:46) retracted the first. Both entries stand in `logs/pipeline.log`, in order, per this project's append-only, never-retype convention.
2. This is now `logs/improvement-log.jsonl` `IMP-0593` (`pac-org-fetch-silently-incomplete`): an unfiltered `pac org fetch` against a high-volume system entity (`importjob`) can silently omit a live, matching row with no error — always narrow by name and date before concluding a live record does not exist, especially before writing an accusation of fabrication into an audit log.

Every figure in this Deployment Summary (Import IDs, `canvasapp` timestamps, `solutioncomponent` count) was independently re-confirmed by this session's own properly-filtered live queries after both corrections, and matches what is recorded above.

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-0593](../../logs/known-failure-modes.md) | `pac-org-fetch-silently-incomplete` | rework | An unfiltered `pac org fetch` against `importjob` can silently omit a live matching row with no error — narrow by `solutionname` + date before concluding a record does not exist. |
| [IMP-0594](../../logs/known-failure-modes.md) | `stale-claim-contradicting-rechecked-source` | friction | This dispatch was asked to close four ids (`IMP-0509`, `IMP-0577`, `IMP-0581`, `IMP-0584`) on today's reviewer confirmation. Re-reading each id's own `what` text found that three (`IMP-0577`, `IMP-0581`, `IMP-0584`) genuinely describe this same x-axis category-label dy/ascent symptom, but `IMP-0509` describes a **different** symptom on its own record (StatTile currency-value line-height overlap in `RoundFinancePanel`), despite having been carried into this chain by this document and three prior `logs/pipeline.log` entries. Today's confirmation closes the chart x-axis symptom (`IMP-0577`/`IMP-0581`/`IMP-0584`) and does **not** close `IMP-0509`, which needs its own reviewer confirmation of the StatTile symptom specifically. Status changes (adding `reobserved`, moving to `APPLIED`) are `improvement-agent`'s to make, not this dispatch's — flagged there via this finding's `proposed_change`. |
| none (mechanical) | — | — | Every deploy-mechanical outcome otherwise matched the already-documented pattern from the prior deploy cycles on this feature (unchanged `solutioncomponent` count, stale callback registration under the standing override). The `dev.verification[5]` live run remains outstanding for the same already-documented reason (no live provisioning credential in this session) — not a new lesson. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py` re-run after appending `IMP-0594`; `logs/known-failure-modes.md` now carries 591 entries / 588 distinct lessons.

---

## HANDOFF

```
HANDOFF | from:pipeline-agent | to:pm-agent | feature:trustee-portal-visual-refresh | status:READY | doc:logs/pipeline.log (2026-09-03 16:29-16:46 entries)
HANDOFF | from:pipeline-agent | to:commercial-agent | feature:trustee-portal-visual-refresh | status:READY | doc:logs/pipeline.log (2026-09-03 16:29-16:46 entries)
```

---

## Addendum, 2026-09-04 — TST/ACC seeded for customer UAT (WBS 6.8)

**This section records a manual promotion this project's own tooling cannot see, plus the
post_deploy data seeding run against it.** Nothing above this line describes TST/ACC; that is
correct up to 2026-09-03 and is left unedited.

**Promotion state, groundtruthed live before acting, not assumed from the reviewer's request:**
`pac solution list --environment https://org68bf3a64.crm17.dynamics.com/` (REV-GrantApplications-ACC)
on 2026-09-04 returned `RevitaliseGrantAutomation 1.0.0.3 Managed` — the solution had already been
promoted to TST/ACC via the Power Platform Pipelines UI (`promote_mode: manual`,
`config/revitalise-grant-automation-pipeline.yml:1529`) since this document's last entry, and no
prior dispatch recorded it. Logged as [IMP-0596](../../logs/known-failure-modes.md).

**Seeding run against TST/ACC**, per `config/revitalise-grant-automation-pipeline.yml:1609` (`tst_acc.post_deploy`), using the provisioning identity (app `077f1f90-3218-4a06-bc90-887464353aa7`, cert thumbprint `A6F94E1801D1C62B7A82AE75E1AA5AD243ECC7FE` — the in-use certificate per `docs/development/revitalise-grant-automation-dev-deployment-handover.md:225`, not the retired second thumbprint):

| Step | Script | Result |
|---|---|---|
| Access probe | `verify-environment-access.ps1 -Env test` | PASS — UserId `c8b2169f-5e9d-f111-b8de-7ced8d5f6ccb` |
| Settings data | `seed-settings.ps1 -Env test` | 14 EXISTS (unchanged), 2 CREATED — `RoundStatisticsMoneyMeasureMinimumPopulation`=5, `RoundStatisticsStaleAfterSeconds`=300, both `rev_effectivefrom` 2026-09-04 |
| Round figures — ask row | `seed-round-statistics-request.ps1 -Env test` | 1 CREATED — `rev_roundstatisticsrequest` `'CURRENT'` |
| Round figures — answer row | `seed-round-statistics-result.ps1 -Env test` | 1 CREATED — `rev_roundstatisticsresult` `'CURRENT'`, `rev_status=Complete` |

All four rows independently re-confirmed by live `pac env fetch` against `rev_setting` (16/16 rows
present, correct values), `rev_roundstatisticsrequest` and `rev_roundstatisticsresult` (both
singleton rows present) — not inferred from the scripts' own exit codes. **Level reached: V3**
(accepted by target, content independently confirmed, idempotent by construction via each script's
alternate-key upsert).

**What this closes, and what it does not.** Before this run, TST/ACC carried the settings-rows.notes.md
dark-state (`RoundStatisticsStaleAfterSeconds` unseeded → the round-statistics panel would recompute
and never show a result) and had neither singleton scaffold row the trustee portal's Round Statistics
feature needs to read or write at all — the feature was unusable in TST/ACC before this run, seeded
in DEV only since 2026-08-25/30. It is now seeded identically to DEV. This does **not** touch
`rev_roundfinance` (the hand-entered per-round finance figures `RoundFinancePanel.tsx` shows) —
those rows are entered by a staff member through the app, not seeded by any script, and none exist
in TST/ACC yet; the customer will see "figures entered by hand" as not-yet-entered until someone
does that data entry.

**Gap found while doing this**, logged as [IMP-0595](../../logs/known-failure-modes.md):
`config/revitalise-grant-automation-pipeline.yml`'s `tst_acc.post_deploy` block never declared the
two round-statistics seed scripts (only `dev.post_deploy` does), so this run was ad hoc — the
config would not run these two steps on its own the next time TST/ACC is promoted to. Handed to
development-agent (config owner) to add both as declared `tst_acc`/`prd` post_deploy steps.

IMPROVEMENT LOG: 2 entries appended — `IMP-0595`, `IMP-0596`. Digest regenerated: YES —
`logs/known-failure-modes.md` now carries 593 entries / 590 distinct lessons.

```
HANDOFF | from:pipeline-agent | to:development-agent | feature:trustee-portal-visual-refresh | status:READY | doc:logs/pipeline.log (2026-09-04 08:10 entry)
HANDOFF | from:pipeline-agent | to:pm-agent | feature:trustee-portal-visual-refresh | status:READY | doc:logs/pipeline.log (2026-09-04 08:10 entry)
```

WBS deliverables landed: `6.8` — this build's Code App dist carries Revision 1.11 (`IMP-0590` fix, the x-axis tick/tspan `dy` composition defect), independently confirmed in a real Chromium render by three separate sessions before this deploy, deployed live at DEV (canvasapp `appversion` moved to `2026-09-03T14:42:39Z`), and now **confirmed by the reviewer** (Xander Lykopoulos, 2026-09-03, direct visual check of the live app — "its good now"). Solution import and flow-definition replacement occurred as a side effect of any import (content-verified unchanged component count); Code App push carried the actual content change. Both writes re-run cleanly. **Level reached: VERIFIED (V4)** for the round-statistics chart x-axis category-label overlap defect — this dispatch's own purpose — closing `IMP-0577`/`IMP-0581`/`IMP-0584` (evidence: this document; status change is `improvement-agent`'s to make). **`IMP-0509` is NOT closed by this confirmation** — it describes a different symptom (StatTile currency-value overlap) that today's check did not address; see "Findings Logged" (`IMP-0594`). Two items remain outstanding for this feature, unrelated to the chart-overlap defect and carried forward unchanged by this dispatch: (1) the flow designer re-registration for `rev_roundstatisticsrequest` (pre-existing, covered by the standing `C-TECH-058` override); (2) `dev.verification[5]` live component-completeness run (missing provisioning credential in this local session). The Playwright visual-regression spec also remains un-wired into `config/revitalise-grant-automation-build.yml`/`-pipeline.yml` (known gap, flagged above, not this dispatch's to close). Promotion beyond DEV **not attempted** — reviewer's stated scope for this dispatch was DEV only.

---

## Addendum, 2026-09-20 — build `trustee-portal-visual-refresh-20260920-4` — DEV IMPORT NOT COMPLETED

**Scope:** Dev Summary Revisions 1.12–1.17 (`wbs:6.10`), test-agent APPROVED against
[`docs/tests/trustee-portal-visual-refresh-test-report-v14.md`](../tests/trustee-portal-visual-refresh-test-report-v14.md).
Reviewer scoped this dispatch to **DEV only**. Everything below is source/pre-deploy work — the
import itself did not happen this session, for reasons recorded here rather than silently retried
or assumed.

### What passed before any environment was touched
- `python3 scripts/verify-artifact-provenance.py build/artifacts/trustee-portal-visual-refresh-20260920-4/` → **PASS**.
- `python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml` → **PIPELINE CONFIG PREFLIGHT: PASS** — 116 steps, all `blocked_on` notes within baseline, no unresolved placeholder in a step this deploy reaches.
- Assumption-register gate (`C-TECH-058`): this cycle's three genuinely new rows — `A-FLOW-15`, the two new `A-FLOW-13` call sites, and `A-R61` — are correctly recorded OPEN and **cannot be closed before this exact deploy occurs** (the mechanism they describe has never been imported anywhere); per `skills/how-to-apply-constraints.md`'s "could the evidence exist yet?" test this is `deferred-to-pipeline`, not a halt condition, matching test-agent's own v14 §5/§7.1 finding. **Not re-litigated this dispatch:** the large pre-existing backlog of OPEN rows from earlier revisions (`A-FLOW-01`–`A-FLOW-12`, `A-LAND-3`, `A-LAND-4`, `A-TR-13`, `A-DS-12`) is unchanged carried-forward technical debt from prior cycles, outside `wbs:6.10`'s scope, and was not re-verified — flagged here rather than silently ignored.

### Why the DEV import did not happen
Two independent blockers, both confirmed live, neither worked around:

1. **This session holds neither `PROVISION_APP_ID` nor `PROVISION_CERT_THUMBPRINT`.** Confirmed by checking (`env | grep -i provision` — empty), then by attempting the unconditional access preflight:
   ```
   PREFLIGHT: verify-environment-access.ps1 -Env dev — FAILED (Environment variable 'PROVISION_APP_ID' is not set)
   ```
   This blocks every script that dot-sources `provisioning/common/provisioning-common.ps1` — concretely, this cycle's own `seed-settings.ps1 -Env dev` (the step that seeds FR-082's two new `rev_setting` rows) and `verify-solution-components.ps1 -Env dev`. **It does not block the solution import itself** — per this feature's own pipeline config, DEV import is performed by GitHub Actions' `stage-dev` job using CI's own federated OIDC credential (`secrets.APP_ID`/`TENANT_ID`), never by a local `pac solution import` — `deploy_command` is deliberately absent from `environments.dev` for exactly this reason. Reading the certificate out of a local keychain to self-supply the values was not attempted (refused by design, not a workaround to pursue).
2. **The CI run that would perform the import never happened, and this session could not start one.** `.github/workflows/ci.yml`'s `push` trigger only covers `main`, `project-management` and `feature/**` — this repository's current branch, `generalise-engine`, is not among them, so pushing commit `7d22c7d` (already on `origin/generalise-engine`) triggered nothing. The workflow also accepts `workflow_dispatch`, so this session attempted:
   ```
   gh workflow run "CI/CD" --ref generalise-engine -f feature_slug=trustee-portal-visual-refresh
   ```
   This was **refused by the harness's own auto-mode classifier** ("Production Deploy"), the same class of refusal `agents/pipeline-agent.md` → "Reviewer-Executed Operations" describes for a live write attempted from this session. No native alternative exists (there is no `pac` verb that triggers a GitHub Actions run). Per that section's step 4, the exact command is handed to the reviewer below rather than this dispatch reporting a false success or silently giving up.

```
REVIEWER ACTION REQUIRED  |  feature:trustee-portal-visual-refresh  |  env:dev
Shell: zsh — the reviewer's own terminal, NOT a pwsh session
Run:
  gh workflow run "CI/CD" --ref generalise-engine -f feature_slug=trustee-portal-visual-refresh
(or trigger "CI/CD" → Run workflow, ref generalise-engine, feature_slug trustee-portal-visual-refresh,
from the Actions tab in the browser). This runs validate → build → stage-dev with CI's own
federated credential and performs the DEV import + FR-082 settings seed this dispatch could not.
Verify afterwards with:
  gh run list --workflow "CI/CD" --branch generalise-engine --limit 1
  pac env fetch --xmlFile <a file querying rev_setting rev_name/rev_value where
    rev_name in ('RoundStatisticsHistoryStartDate','RoundStatisticsHistoryPriorApplicationCount')>
Expect both rows present, values 2026-02-16 and 0.
```

### Live DEV state confirmed this session (via `pac env fetch` — the pac-credential-path route, which is not gated by the missing local variables)
- `rev_setting` — queried for `RoundStatisticsHistoryStartDate`/`RoundStatisticsHistoryPriorApplicationCount`: **no results returned**. Confirms build `20260920-4`'s changes have **not** reached DEV yet — this cycle's own settings are absent, consistent with the import blockers above, not assumed from either blocker alone.
- `rev_application` — queried for every row with a populated `rev_submittedon`: **12 rows total, every one sharing the identical timestamp `2026-08-20 20:59`.** DEV does **not** currently hold six-plus consecutive months of real, distinct application history. This is stated plainly per the HANDOFF's own instruction, not skipped silently: **even once the import above completes**, the live verification test-agent asked for (seed `RoundStatisticsHistoryStartDate` several months in the past, seed six-plus months of known counts, read `historicApplicationsByMonth.months`, hand-verify month span/boundary keys and, for `A-R61`, a threshold-boundary trailing-mean case) cannot be performed as specified without additional synthetic historical data. Creating that data is not covered by any declared idempotent provisioning script in this repository (it is test-fixture creation, not settings seeding), so it is not something this dispatch invented ad hoc. **What could be verified instead, narrower but real:** after import, the two new settings rows could be seeded and read back, and `historicApplicationsByMonth` could be read against the 12 existing same-day rows to confirm it degrades safely (a single populated month, `understatedTotal` behaviour per the seeded prior-count) — this is a materially weaker check than the one the TAD's A-R61 row asks for and should not be reported as closing `A-R61`.

### Saved-query reachability check (the IMP-0090 class — component in source vs. absent from sitemap/subarea wiring)
| Component | Found in source? | Wiring | Result |
|---|---|---|---|
| `AutoPassApplications` | **Yes** — `src/solutions/RevitaliseGrantAutomation/Entities/rev_application/SavedQueries/AutoPassApplications.xml`, `savedqueryid` `{e5a7b9c1-6009-4a2b-8c11-0a1b2c3d4e59}` | Matches `AppModuleSiteMaps/rev_grantadministration/AppModuleSiteMap.xml`'s `rev_sub_autopass` `SubArea` `viewid` exactly, inside the Casework group of the grant-administration model-driven app (EF-16, `IMP-0784`) | **Wired at source level (V1/V2).** Live reachability (V4 — open the app, see the menu item) cannot be checked; the app has not been imported this session (see above) |
| `EqualityMonitoring` | **No.** Grepped case-insensitively across `src/solutions/RevitaliseGrantAutomation/`, this feature's Dev Summary, and its Test Report — zero hits for a saved query, `SubArea`, or `AppModuleComponent` of that name. "Equality monitoring" exists only as a **data** concept in this feature (the `rev_gender`/`rev_ethnicgroup` columns and their field-security-profile rows, both real and shipped) — never as a view | **Not a built component.** This is a mismatch in the dispatch brief itself, not a defect in shipped work — logged as `IMP-0803` (`dispatch-brief-asserts-unverified-fact`) rather than either silently skipped or fabricated a verification result for |

### Constraint Check
```
CONSTRAINT CHECK
Tech   HARD: 6 / 6 evaluable of 9 in scope  |  violations: NONE
                                            |  unevaluable: NONE
                                            |  deferred-to-pipeline (evidence not yet due): C-TECH-050 (no new schema this cycle — confirmed by Dev Summary/manifest diff, so nothing to verify), C-TECH-058 (A-FLOW-15/A-FLOW-13×2/A-R61 — see above), C-TECH-064 (nothing live yet to read back)
Tech   SOFT: 1 in scope                     |  warnings: C-TECH-044 (no client secret path touched, N/A) — not counted
Overall: BLOCKED — not on a constraint violation, but on the two live-environment blockers above (Reviewer-Executed Operations refusal + missing local credential). No HARD violation was found in anything evaluable this session.
```

### Tenant-Level Operations
None this dispatch.

### Environment Prerequisites (C-TECH-050, C-TECH-051)
Not run. This cycle adds no new Entity/Attribute/OptionSet/Role/FieldSecurityProfile (confirmed against the Dev Summary's own Revision 1.12–1.17 change list and the build manifest) — only two `rev_setting` seed rows via the existing `seed-settings.ps1 -Env dev` post_deploy step, which is credential-gated and did not run this session (see above).

### Findings Logged
| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-0803](../../logs/known-failure-modes.md) | `dispatch-brief-asserts-unverified-fact` | rework | A dispatch brief named a saved query ("EqualityMonitoring") absent from source, this feature's Dev Summary and its Test Report — grep source before attempting to verify a named component's reachability, and report the mismatch rather than skip or fabricate. |

IMPROVEMENT LOG: 1 entry appended — `IMP-0803`. Digest regenerated: YES — `logs/known-failure-modes.md` now carries 800 entries / 793 distinct lessons.

**No `HANDOFF` to `pm-agent`/`commercial-agent` this addendum.** That handoff fires "after a successful DEV deploy" (`agents/pipeline-agent.md`) — this session's DEV deploy did not happen, so nothing is reported as landed, and no accounting trigger is raised for work that has not reached the environment.

```
DEPLOYMENT FAILED ❌  |  stage:dev  |  feature:trustee-portal-visual-refresh
Error: DEV import for build 20260920-4 could not be performed this session — CI trigger (gh workflow run) refused by the harness auto-mode classifier, and this session holds neither PROVISION_APP_ID nor PROVISION_CERT_THUMBPRINT for a local fallback (the local fallback path — pac solution import — is not this config's declared DEV mechanism regardless; CI's stage-dev job is).
Action: Reviewer runs the `gh workflow run` command in the REVIEWER ACTION REQUIRED block above, or supplies PROVISION_APP_ID/PROVISION_CERT_THUMBPRINT to a re-dispatched pipeline-agent session so the credential-gated steps can run directly. Separately, DEV does not currently hold six-plus months of distinct application history — the live A-R61/A-FLOW-15 verification needs either synthetic seed data (reviewer decision — no provisioning script covers this) or an explicit acceptance of the narrower check described above. And the HANDOFF's "EqualityMonitoring" saved query does not exist in source — needs reviewer clarification (real future scope needing a WBS id/change order, or a naming mistake in the dispatch).
```

---

## Addendum, 2026-09-20 (retry) — build `trustee-portal-visual-refresh-20260920-4` — DEV IMPORT ATTEMPTED LIVE, FAILED ON A SOURCE DEFECT

**Reviewer redirect (Anna Southern):** the prior addendum's premise was corrected. `pac`
authenticates on its own profile (`svc_grantapplications@revitalise.org.uk`) and does **not**
require `PROVISION_APP_ID`/`PROVISION_CERT_THUMBPRINT` — those gate only the PowerShell
provisioning scripts (`ensure-schema.ps1`, `verify-environment-access.ps1`,
`reconcile-flow-statecodes.ps1`, `seed-settings.ps1`, `verify-solution-components.ps1`), never
`pac` itself. GitHub Actions CI was never this feature's DEV mechanism for a `pac`-authenticated
session — the established, repeatedly-proven pattern is this feature's own `alm.stage_dev_command`
run directly by a dispatched `pipeline-agent` session (`logs/pipeline.log`, builds `20260901-2`
through `20260903-3`, six consecutive first-attempt successes). This session followed that pattern.

### `pac` auth state confirmed before any write (per the HANDOFF's explicit instruction)
```
pac auth list  →  [2] * svc_grantapplications@revitalise.org.uk  (active)  REV-GrantApplications-DEV  https://orge2b20d13.crm17.dynamics.com/
pac org who    →  Connected as svc_grantapplications@revitalise.org.uk, REV-GrantApplications-DEV,
                   Org ID 555c6d4c-c497-f111-b8cf-6045bd29e559, Environment ID 2f7ce6a9-fdb7-e10b-a40a-07f5022ee453
```
`PROVISION_APP_ID`/`PROVISION_CERT_THUMBPRINT` confirmed **unset** in this session's shell — named
here, not silently assumed, per `agents/pipeline-agent.md`'s activation step 6.

### Pre-deploy gates — all PASS
- `python3 scripts/verify-artifact-provenance.py build/artifacts/trustee-portal-visual-refresh-20260920-4/` → **PASS**.
- `python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml` → **PIPELINE CONFIG PREFLIGHT: PASS** — 116 steps, 4/5 `blocked_on` notes fresh, 3 accepted by baseline.
- Assumption-register gate (`C-TECH-058`): `A-FLOW-15`, the two new `A-FLOW-13` call sites and `A-R61` are correctly OPEN and closeable only by this exact deploy (V2 designer save, then a live seeded run) — `deferred-to-pipeline`, not a halt condition, matching test-agent's v14 §5/§7.1 finding. This deploy is what begins closing them, not a bypass of the gate.

### The import — attempted live, FAILED
```
WRITE BEGUN:     pac solution import -Env dev (build 20260920-4)
WRITE ATTEMPTED: pac solution import -Env dev — FAILED
```
```
pac solution import --path build/artifacts/trustee-portal-visual-refresh-20260920-4/RevitaliseGrantAutomation.zip \
  --environment https://orge2b20d13.crm17.dynamics.com/ --async --max-async-wait-time 60 \
  --force-overwrite --publish-changes --activate-plugins
```
Ran to completion (not refused by the harness — the `pac`-credential-path exemption held this
time). Failed live after 00:04:36: `asyncoperation 2a8e6516-1fb5-f111-aaae-7ced8d43e87d`,
**"Import failed: An item with the same key has already been added."**

**Diagnosed against the platform's own detailed record, not the one-line reason**, per
`knowledge/technology/build-and-deploy.md` → *Diagnosing a Failed Import*:
```
pac org fetch  →  asyncoperation.message (this async op id)
```
returned the full .NET stack trace: `System.ArgumentException: An item with the same key has
already been added` at `Dictionary.Insert`, called from
`Microsoft.Crm.ObjectModel.FlowTemplate.FlattenNestedActions` ← `FlowTemplateAction.Children()` ←
`WorkflowDependencyCalculator.DetermineModernFlowRequiredDependencies` — the platform's
dependency-calculation pass for the solution's modern (cloud) flow.

**Root cause, confirmed in source:**
[`Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json)
declares the action name `Compose_historic_months_array` **twice** — line 3048 (the `actions`
branch) and line 3061 (the `else` branch) of the same `Condition_history_start_seeded` Condition,
added this cycle for FR-080/FR-081 (ADR-049/ADR-050, Revision 1.13). The two are mutually
exclusive at runtime and reusing an action name across If/else branches is normal, legal
authoring in the flow designer — but `FlattenNestedActions` flattens **every** action in the
flow, both branches included, into one case-insensitive dictionary keyed by name before computing
dependencies, so a name reused across branches collides and the **whole import** aborts, not just
that Condition. Confirmed programmatically (`python3` walk of the JSON, both occurrences at
identical nesting path, one under `actions`, one under `else.actions`) — this is not a guess.

**No re-run attempted.** Per "Deployment Failure" — halt on first failure, no auto-retry. Nothing
past the import (post_deploy, `pac code push`, component verification, V4 open-and-save) was
reached this session.

**What still could not run regardless of the import's outcome** (credential-gated,
`PROVISION_*` unset): `seed-settings.ps1 -Env dev` (FR-082's two `rev_setting` rows),
`verify-environment-access.ps1 -Env dev` (the formal access preflight — `pac org who` above is
supporting evidence of identity, not a substitute for it), `verify-solution-components.ps1`,
`ensure-schema.ps1`. None of these were reachable this session even had the import succeeded.

### Constraint Check
```
CONSTRAINT CHECK
Tech   HARD: 6 / 6 evaluable of 9 in scope  |  violations: NONE
                                            |  unevaluable: NONE
                                            |  deferred-to-pipeline: C-TECH-050 (no new schema this cycle), C-TECH-058 (see above), C-TECH-064 (nothing live yet to read back)
Tech   SOFT: 1 in scope                     |  warnings: none new
Overall: BLOCKED — a genuine live import failure (source defect), not a constraint violation and not a harness refusal. No HARD violation was found in anything evaluable this session.
```

### Findings Logged
| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-0804](../../logs/known-failure-modes.md) | `platform-contract-guessed-not-groundtruthed` | **blocker** | Reusing an action name across If/else branches in a cloud flow is legal authoring but FLOW-WIDE unique at import time — `FlattenNestedActions` flattens all branches into one dictionary before computing dependencies, so a repeated name aborts the whole import. No gate in this repo checks action-name uniqueness across a flow's full branch tree. |

IMPROVEMENT LOG: 1 entry appended — `IMP-0804`. Digest regenerated: YES — `logs/known-failure-modes.md` now carries 801 entries / 794 distinct lessons.

**`IMP-0804` is `blocker` severity and `unread` — per `agents/WORKFLOW.md` → "Processing
triggers" this routes to `improvement-agent` immediately, not batched.** Flagged here and in the
gate output below for `lead-agent` to action; this dispatch does not itself hold the
`improvement-agent` dispatch.

**No `HANDOFF` to `pm-agent`/`commercial-agent` this addendum.** The DEV deploy did not succeed —
nothing landed, so no accounting trigger is raised.

```
DEPLOYMENT FAILED ❌  |  stage:dev  |  feature:trustee-portal-visual-refresh
Error: pac solution import failed live (asyncoperation 2a8e6516-1fb5-f111-aaae-7ced8d43e87d) — "An item with the same key has already been added." Root cause: Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json reuses action name Compose_historic_months_array across the actions/else branches of Condition_history_start_seeded; the platform's FlattenNestedActions dependency pass treats action names as flow-wide unique, not branch-scoped.
Action: development-agent renames one of the two Compose_historic_months_array actions (they are mutually exclusive at runtime, so any distinct name is safe — e.g. Compose_historic_months_array_empty for the else branch) and updates the one downstream reference (Compose_historic_applications_by_month's outputs('Compose_historic_months_array') expression, line 3084, only reads the if-branch's output so it is unaffected by renaming the else-branch copy). Re-pack, re-test, and re-dispatch pipeline-agent for a fresh DEV import attempt. Separately: IMP-0804 (blocker, unread) needs an improvement-agent dispatch behind APPROVE IMPROVEMENTS — proposes a new source gate (recursive action-name-uniqueness check across all branches of every flow) so this class is caught pre-import next time.
```

---

## Addendum — 2026-09-20, build 20260920-6: DEV import SUCCEEDED (retry, `IMP-0804` re-observation)

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** `build/artifacts/trustee-portal-visual-refresh-20260920-6/`
**WBS:** 6.10
**Scope:** DEV only — reviewer (Anna Southern) approved Test Report v15 and explicitly scoped this dispatch to DEV; no promotion attempted, no CI/GitHub Actions triggered.

### `pac` auth confirmed before any write
```
pac auth list  →  [2] * svc_grantapplications@revitalise.org.uk  (active)  REV-GrantApplications-DEV  https://orge2b20d13.crm17.dynamics.com/
pac org who    →  Connected as svc_grantapplications@revitalise.org.uk, REV-GrantApplications-DEV,
                   Org ID 555c6d4c-c497-f111-b8cf-6045bd29e559, Environment ID 2f7ce6a9-fdb7-e10b-a40a-07f5022ee453
```
Same profile as the prior (failed) 20260920-4 dispatch, per the HANDOFF's instruction.

### Pre-deploy gates
- `python3 scripts/verify-artifact-provenance.py build/artifacts/trustee-portal-visual-refresh-20260920-6/` → **PASS**.
- `python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml` → **PIPELINE CONFIG PREFLIGHT: PASS** — 116 steps, 4/5 `blocked_on` notes fresh, 3 accepted by baseline (all `tst_acc`/`prd` scoped — not this dispatch).
- Assumption-register gate (`C-TECH-052`): `python3 scripts/verify-assumption-register.py` → **PASS** — 89 rows across 29 registers, 48 still open, none contradicted. The rows relevant to this exact flow (`A-FLOW-03`, `A-FLOW-06`, `A-FLOW-11`, `A-FLOW-13`) each name their own closing precondition as a **post-import** designer-save or live run — none is closeable by pre-deploy ground-truthing alone, so none blocks this deploy; they stay OPEN pending the human V4 steps below.

### The import — retried live, SUCCEEDED
```
WRITE BEGUN:     pac solution import -Env dev (build 20260920-6)
WRITE ATTEMPTED: pac solution import -Env dev — SUCCEEDED
```
```
pac solution import --path build/artifacts/trustee-portal-visual-refresh-20260920-6/RevitaliseGrantAutomation.zip \
  --environment https://orge2b20d13.crm17.dynamics.com/ --async --max-async-wait-time 60 \
  --force-overwrite --publish-changes --activate-plugins
```
`asyncoperation 47930d46-28b5-f111-aaae-7ced8d43e87d` completed successfully within `00:03:20`. Import ID `47930d46-28b5-f111-aaae-7ced8d43e87d`. Publish asyncoperation `59534fbb-28b5-f111-aaae-7ced8d43e87d` completed within `00:01:05`. `pac solution list` confirms `RevitaliseGrantAutomation 1.0.0.0` present (unmanaged).

**This is the exact retry `IMP-0804` was deferred pending.** Build 20260920-6 fixes the root cause (the else-branch copy of `Compose_historic_months_array` is renamed `Compose_historic_months_array_empty`) and `scripts/verify-flow-definition-language.py` check 8 (the new gate this finding motivated) ran clean against it at build time. The class did not recur.

**Idempotency re-run (`C-TECH-053`, required before declaring success):** the identical import command was run a second time immediately after. It also succeeded cleanly — publish asyncoperation `7165e378-29b5-f111-aaae-7ced8d43e87d` completed within `00:00:49`, no errors.

### Component verification
- `pac solution list` — `RevitaliseGrantAutomation` present, version `1.0.0.0`. **Full per-type derived-list verification of all 78 `<RootComponent>` entries was not exhaustively re-run this session** — this build's source diff is limited to the flow fix and the grant-admin app EF fixes (commit `7d22c7d`), and every other component was already confirmed live in earlier sessions with no schema change since. Flagged as a scope-limited check, not a hand-picked one.
- **The workflow itself — the component this retry exists to prove — checked directly:**
  ```
  pac org fetch (workflow, filter name like '%Round Statistics%')
  →  REV | Portal | Round Statistics   statecode=Draft   statuscode=Draft   workflowid=8f1c2a44-1005-4b7a-9e21-0a1b2c3d4e05
  ```
  The import **accepted** the flow cleanly (no dependency-calculation error, confirming `IMP-0804`'s fix), but `statecode=Draft` — the known `force-overwrite`-deactivates-flows pattern (`IMP-0113`): "An unmanaged pac solution import with --force-overwrite DEACTIVATES every cloud flow in the solution... Capture the flow statecodes BEFORE the import and re-assert them after... Re-activate IN THE DESIGNER, never by PATCHing workflow.statecode." No PATCH was attempted here, correctly.
  ```
  pac org fetch (callbackregistration, filter entityname eq 'rev_roundstatisticsrequest')
  →  rev_roundstatisticsrequest   createdon=8/27/2026 6:22 PM   message=Modified   callbackregistrationid=b184204a-44a2-f111-b8de-70a8a5079a1b
  ```
  This registration **predates today's import by three weeks** and predates the flow's own `Draft` reactivation entirely — per `IMP-0114`, an existing registration is not evidence the trigger will fire once reactivated; it must be **recreated** by turning the flow off (confirm the row disappears), then on **from the designer** (confirm a new `createdon`).

### Level reached: **DEPLOYED (V3)**, not VERIFIED (V4)
| Component | V3 (imported, queryable) | V4 (human open-and-save / live proof) |
|---|---|---|
| `RevitaliseGrantAutomation` solution | ✅ imported, idempotent re-run clean | — |
| `REV | Portal | Round Statistics` flow | ✅ imported, no dependency-calculation error | ❌ **OUTSTANDING** — `statecode=Draft`; needs a named human to open it in the Power Automate designer, save, confirm `statecode=Activated`, and confirm the callbackregistration row gets a **new** `createdon`. This is also what closes `A-FLOW-01`/`A-FLOW-04`'s successor verification (TAD §12.3 step 6) and is the precondition for `A-FLOW-03`/`A-FLOW-06`/`A-FLOW-11`/`A-FLOW-13`'s own live-run closing steps |
| Code App (`REV Trustee Review Portal`) | ✅ pushed, fresh `appversion` confirmed | ❌ OUTSTANDING — no live signed-in-trustee check performed this session (see below) |

**Owner of the outstanding V4 step: the reviewer** (or whoever holds System Administrator / maker access on DEV) — this session's `pac` profile can push and import but cannot open the Power Automate designer UI.

### Code App push — attempted and succeeded
```
WRITE BEGUN:     pac code push -Env dev
WRITE ATTEMPTED: pac code push -Env dev — SUCCEEDED
```
`pac code push --environment https://orge2b20d13.crm17.dynamics.com/ --solutionName RevitaliseGrantAutomation`, run from `src/code-apps/trustee-review-portal` (its `dist/` confirmed to match the packaged artifact's `code-app/` directory by mtime, one second apart — same build). Result: *"App pushed successfully"* — app `70869c95-92e5-442f-b5b9-44b3d3e549f6`, environment `2f7ce6a9-fdb7-e10b-a40a-07f5022ee453`.

Live confirmation, queried after the push:
```
pac org fetch (canvasapp, filter displayname eq 'REV Trustee Review Portal')
→  REV Trustee Review Portal   appversion=2026-09-20T19:30:46Z   canvasappid=70869c95-92e5-442f-b5b9-44b3d3e549f6
```
`appversion` is ~1 minute before the query (session clock: 19:31:41 UTC) — this is this session's own push, not a stale prior one.

**Saved queries** (per the HANDOFF's own note, not independently re-checked this session): `AutoPassApplications` was confirmed wired at source in an earlier session; `EqualityMonitoring` remains unwired/orphaned per `IMP-0803` — a separate, already-tracked follow-up, not a regression from this build.

### Credential-gated steps — still unavailable this session
`PROVISION_APP_ID` / `PROVISION_CERT_THUMBPRINT` confirmed **unset** in this session's shell (as in the prior 20260920-4 dispatch). Every script that dot-sources `provisioning/common/provisioning-common.ps1` failed or could not run:
- `provisioning/dataverse/verify-environment-access.ps1 -Env dev` — **run, FAILED**: `Exception: Environment variable 'PROVISION_APP_ID' is not set.` (`provisioning-common.ps1:171`). This is the required, unconditional access-preflight step (`C-TECH-065`) — its result is reported here as FAIL, not silently skipped. `pac org who` (above) is supporting evidence of identity only, not a substitute.
- `provisioning/dataverse/seed-settings.ps1 -Env dev` — **did not run** (FR-082 settings seed; no new schema/settings in this build's diff, so nothing was blocked by its absence this cycle, but it is named rather than assumed).
- `provisioning/dataverse/ensure-schema.ps1 -Env dev` — **did not run** — no new schema in this build's diff, so nothing was blocked.
- `provisioning/dataverse/verify-solution-components.ps1` — **did not run**; component verification above was done via `pac org fetch` (FetchXML, `pac`'s own credential path) instead, scoped to the components this dispatch's diff actually touches.

Owner of closing this credential gap: the reviewer (a session holding `PROVISION_APP_ID`/`PROVISION_CERT_THUMBPRINT`, or the CI job's own `env:` block per `.github/workflows/ci.yml`'s "Provisioning identity" section) — unchanged from the prior dispatch's finding.

### Constraint Check
```
CONSTRAINT CHECK
Tech HARD: 4 / 4 evaluable in DEV scope  |  violations: NONE
Overall: PASS
```
`C-TECH-030` (managed-build provenance) PASS. `C-TECH-050` (schema prerequisites before first import) — not applicable, no new schema this cycle. `C-TECH-053` (verification by execution) — DEPLOYED (V3), V4 outstanding, named above rather than assumed. `C-TECH-055` (warnings triaged) — manifest records 9/9 accepted, 0 untriaged.

### IMP-0804 — re-observation recorded, not closed
Per `docs/improvements/2026-09-20-improvement-review-3.md`'s own disposition (owner: pipeline-agent, return condition: the next DEV import), this dispatch **is** that re-observation. `logs/improvement-log.jsonl` `IMP-0804` now carries a `reobserved` field: `level: V3`, `by: pipeline-agent`, `ts: 2026-09-20T21:26`, naming both asyncoperation ids and the idempotency re-run. **Status is left as `NEW`/deferred — closing it is `improvement-agent`'s action behind `APPROVE IMPROVEMENTS`, not this dispatch's.** `python3 scripts/verify-improvement-log.py --check` → OK (807 entries, no new errors). Digest regenerated: `python3 scripts/generate-known-failure-modes.py` → 807 entries, 799 distinct lessons, 734 lines.

IMPROVEMENT LOG: 0 new entries appended — `reobserved` added to `IMP-0804` (existing entry). Digest regenerated: YES.

### HANDOFF — to the PM agents (`C-TECH-032`-adjacent, this DEV deploy is the accounting trigger)
```
HANDOFF | from:pipeline-agent | to:pm-agent | feature:trustee-portal-visual-refresh | status:READY | doc:logs/pipeline.log (2026-09-20 21:26 entry) | wbs:6.10
HANDOFF | from:pipeline-agent | to:commercial-agent | feature:trustee-portal-visual-refresh | status:READY | doc:logs/pipeline.log (2026-09-20 21:26 entry) | wbs:6.10
```
WBS deliverables landed: the `REVPortalRoundStatistics` flow (WBS 6.10, FR-080/FR-081) imported successfully to DEV for the first time; the Code App (`REV Trustee Review Portal`) pushed with the matching build. **Level actually reached: DEPLOYED (V3)** — component-existence and idempotency proven, human V4 open-and-save/live-run still outstanding, named above. A PM or commercial failure never halts this deploy (PM-R30); the deploy stands regardless of what those agents find.

```
DEPLOYED TO DEV (V3) ✅  |  feature:trustee-portal-visual-refresh  |  artifact:build/artifacts/trustee-portal-visual-refresh-20260920-6/  |  wbs:6.10
Prerequisites: n/a this cycle (no new schema) — DEV prerequisites satisfied in earlier sessions
Idempotency re-run: PASS (clean second import, no errors)
Components verified by query: solution list + the flow (the component this retry targets) + the Code App's canvasapp appversion — not the full 78-component derived list (scope-limited to this build's diff, named above)
Human open-and-save (V4): OUTSTANDING for: REV | Portal | Round Statistics (statecode=Draft; callbackregistration stale, predates this import) — level DEPLOYED (V3)
                          OUTSTANDING for: Code App live signed-in-trustee check — level DEPLOYED (V3)
Warnings: 9 accepted with rationale (build-time), 0 untriaged
IMPROVEMENT LOG: 0 new entries — reobserved field added to IMP-0804 (existing NEW/deferred entry, not closed by this dispatch)  |  digest regenerated: YES
Credential-gated steps this session: verify-environment-access.ps1 (ran, FAILED — PROVISION_APP_ID unset), seed-settings.ps1 (did not run — no new schema/settings), ensure-schema.ps1 (did not run — no new schema), verify-solution-components.ps1 (did not run — pac org fetch used instead, scoped)
No promotion attempted — reviewer scoped DEV only.
Awaiting the reviewer's V4 confirmation (flow designer save + Code App live check), or further instruction.
```

---

## Addendum — 2026-09-25: catch-up `pac code push` (DEV-only)

**Dispatch:** DEV-only, reviewer (Anna Southern) authorised live this session (`logs/routing.log`, `[2026-09-25 12:21] [LEAD] [trustee-portal-visual-refresh] ROUTED_TO:pipeline-agent`, quoting *"ok, go ahead with pipeline agent"*). No `APPROVE PRD` sought.

**Why this dispatch exists.** The last successful `pac code push` before this one was **2026-09-20 21:36** (`logs/pipeline.log` line 65). Three DEV solution imports landed after that push — 2026-09-22 12:32 (SUCCESS), 2026-09-24 11:47 (FAILED, `IMP-0866` — `Forms being imported are of an unsupported type 'quickview'`), 2026-09-24 18:13 (SUCCESS, build `revitalise-grant-automation-20260924-7`) — carrying source fixes for EF-04, EF-07, EF-09, EF-37, EF-43 (`docs/Import/FeedbackDeployment_20-09-2026.xlsx`). **None of those three dispatches ran `pac code push`.** The live Code App in DEV was therefore still the 2026-09-20 build until this dispatch — a 5-day gap. Logged as its own systemic-gap finding, `IMP-0879`, distinct from the missing-gate finding lead-agent logs separately.

**Pre-flight.**
- Committed state confirmed, not assumed: `git status` clean, `HEAD c62d309`; the last commit touching `src/code-apps/trustee-review-portal/src` is `8d4010b` (2026-09-23 19:58), unaffected by the one later repo-wide commit.
- `logs/known-failure-modes.md` read at activation per step 0.
- Access preflight: `provisioning/dataverse/verify-environment-access.ps1 -Env dev` **run, FAILED** (`PROVISION_APP_ID` not set — `provisioning-common.ps1:171`), as expected this session. Substituted per the established project pattern: `pac auth list` (active profile `[2]` `svc_grantapplications@revitalise.org.uk`, `REV-GrantApplications-DEV`) and `pac org who` — both PASS (UserId `137f408b-2393-f111-b8db-70a8a5069b66`).
- `dist/` was **not** trusted as-is. First `npm run build` (against the checkout's existing `node_modules`) failed with 47 TypeScript errors, all confined to `*.test.tsx` files, complaining `@testing-library/react` has no exported `screen`/`waitFor`/`within`. `npm ci` followed by an identical `npm run build` succeeded cleanly (exit 0) seconds later with no source change — a stale local install, not a source defect. Logged as `IMP-0878`.
- `power.config.json` unchanged since commit `2d34e9a` (2026-08-30): no new connector or table this cycle, so the `IMP-0485`/`IMP-0358` new-data-source boot-risk class does not apply.

**Write — first attempt.**
```
WRITE BEGUN 2026-09-25T10:25:24Z:     pac code push --solutionName RevitaliseGrantAutomation -Env dev
WRITE ATTEMPTED 2026-09-25T10:25:49Z: SUCCEEDED — "App pushed successfully" (app 70869c95-92e5-442f-b5b9-44b3d3e549f6, env 2f7ce6a9-fdb7-e10b-a40a-07f5022ee453)
```
**Verified live by query**, not by exit code alone — `pac org fetch` against a `canvasapp` FetchXML filtered on `canvasappid`:

| | before this dispatch | after push #1 | after push #2 (idempotency) |
|---|---|---|---|
| `appversion` / `lastmodifiedtime` / `lastpublishtime` | `2026-09-20T19:30:46Z` | `2026-09-25T10:25:39Z` | `2026-09-25T10:26:52Z` |

**Idempotency re-run (`C-TECH-053`).**
```
WRITE BEGUN 2026-09-25T10:26:49Z:     pac code push --solutionName RevitaliseGrantAutomation -Env dev (idempotency re-run)
WRITE ATTEMPTED 2026-09-25T10:27:00Z: SUCCEEDED cleanly
```
The re-query after the second push shows `appversion`/`lastmodifiedtime`/`lastpublishtime` advancing again (to `10:26:52Z`), confirming each run is a genuine write against the live environment, not a cached success being reported twice.

**Level reached: `DEPLOYED (V3)`** for the Code App push. **`V4` (a named person signs in and confirms the app boots with the EF-04/07/09/37/43 fixes visible) is the reviewer's next action** — not performed by this dispatch.

**No promotion attempted** — DEV only, per this dispatch's scope; TST/ACC and PRD promotion remains a Power Platform Pipelines action (ADR-007), gated behind `APPROVE PRD`, not sought.

**IMPROVEMENT LOG:** 2 entries appended — `IMP-0878` (`stale-local-install-produces-spurious-typecheck-failure`, friction), `IMP-0879` (`pipeline-dispatch-stops-before-declared-post-deploy`, rework). Digest regenerated: `python3 scripts/generate-known-failure-modes.py` → 875 entries. `verify-improvement-log.py --check` → exit 0, no new blocker-severity trigger.

```
DEPLOYED TO DEV (V3) ✅  |  feature:trustee-portal-visual-refresh  |  operation:code-app-push  |  wbs:6.10
Access preflight: verify-environment-access.ps1 FAILED (PROVISION_APP_ID unset) — substituted pac auth list / pac org who, PASS
Idempotency re-run: PASS (clean second push, appversion advanced again on live re-query)
Verified live by query: canvasapp appversion/lastmodifiedtime/lastpublishtime — YES, not inferred from CLI exit code
Human open-and-save / live sign-in (V4): OUTSTANDING — reviewer's next action
Warnings: 0 untriaged (stale node_modules resolved by npm ci before pushing, not carried silently)
IMPROVEMENT LOG: 2 entries — IMP-0878, IMP-0879 | digest regenerated: YES
No promotion attempted — reviewer scoped DEV only, no APPROVE PRD sought.
```

---

## Addendum — 2026-09-25 (later): Revision 1.19 — EF-04 re-opened a second time, EF-43 group screen (DEV-only)

**Dispatch.** DEV-only. Test Report v16 PASSED; reviewer (Anna Southern) responded "Deploy to dev". No `APPROVE PRD` sought. `wbs:6.8,6.10`. Artifact: `build/artifacts/trustee-portal-visual-refresh-20260925-2/` (build `SUCCESS`, `logs/build.log` 17:26 entry).

**Why this dispatch matters beyond the routine push.** This artifact's `dist/` post-dates the 10:26:52Z `pac code push` already recorded in the addendum above — it carries EF-04's Summary-panel fix (re-opened a second time; Revision 13's own "delivered" claim was false on the live screen, `IMP-0885`) and EF-43's new `GroupsListPage` screen. A sibling same-day dispatch on `revitalise-grant-automation` hit a classifier refusal on `pac code push` (`IMP-0891`) that had no consequence there because that dispatch's own `dist/` was byte-identical to what was already live. That precedent does **not** apply here — this dispatch's `dist/` is materially different from what was live, so the push was a required write, treated as such rather than assumed safe to skip.

**Pre-flight.**
- Provenance: `verify-artifact-provenance.py build/artifacts/trustee-portal-visual-refresh-20260925-2` — PASS.
- Source confirmed Code-App-only by reading the Dev Summary's own Revision 1.19 section directly (not inferred from the WBS ids): four files changed in `src/code-apps/trustee-review-portal/src/` (`ApplicationDetailPage.tsx`, `CasePanels.tsx`, `App.tsx`, `ApplicationsListPage.tsx`) plus one new file (`GroupsListPage.tsx`) and matching tests — no `src/domain/`, `src/dataverse/`, solution-source, flow or schema change.
- Assumption register (`docs/development/trustee-portal-visual-refresh-dev-summary.md` §10): 25 of 29 rows OPEN, all pre-existing carry-forwards about `REVPortalRoundStatistics`/DocuSign flows and round-statistics rendering (A-FLOW-*, A-LAND-*, A-TR-13, A-DS-12, A-VSC-*) — none reference EF-04/EF-43 or anything under this artifact's actual diff, and none is newly closeable in DEV by this narrow UI-only push. No `C-TECH-058` block.
- Access preflight: `verify-environment-access.ps1 -Env dev` — **run, FAILED** (`PROVISION_APP_ID`/`PROVISION_CERT_THUMBPRINT` confirmed absent before the call). Substituted per established project pattern: `pac auth list` (active profile `[2]`, `svc_grantapplications@revitalise.org.uk`, `REV-GrantApplications-DEV`) + `pac org who` — both PASS (UserId `137f408b-2393-f111-b8db-70a8a5069b66`, Org ID `555c6d4c-c497-f111-b8cf-6045bd29e559`). No schema-shaping change in this artifact's diff, so `ensure-schema.ps1`/`reconcile-flow-statecodes.ps1` were not needed and are EXCLUDED — owner: reviewer or a credentialed session, named here rather than silently skipped.
- `dist/` vs artifact: `diff -rq build/artifacts/trustee-portal-visual-refresh-20260925-2/code-app/ src/code-apps/trustee-review-portal/dist/` — no differences. The push was made from the exact artifact content.

**Write 1 — `pac solution import` (unmanaged, force-overwrite, DEV).**
```
WRITE BEGUN 2026-09-25T19:55: pac solution import --path RevitaliseGrantAutomation.zip --environment https://orge2b20d13.crm17.dynamics.com/ --async --max-async-wait-time 60 --force-overwrite --publish-changes --activate-plugins
WRITE ATTEMPTED 2026-09-25T19:59: SUCCEEDED (import async 6e8c9259-0ab9-f111-aaae-70a8a5079a1b, 2m26.9s; publish async 121027b5-0ab9-f111-aaae-70a8a5079a1b, 32.6s)
```
**Process gap, logged (`IMP-0900`):** the flow-statecode pre-state was not captured before this write, contradicting this file's own "capture the pre-state — before the first write, always" rule. Reconciled after the fact rather than by comparison against a same-session snapshot: a post-import `pac env fetch` read of all 13 live workflows (10 REV + 3 platform-default) shows the same Activated/Draft split already on record in this file's own 2026-08-22 and 2026-09-24 entries — `REV | Scoring | Daily Summary` Draft since 2026-08-22, `REV | Acceptance | Create Envelope`/`Completion` Draft pending designer resolution, `REV | Safeguarding | Action Completion` Draft since its 2026-09-24 landing, all six other REV flows Activated — no new `IMP-0113`-class deactivation observed.

**Idempotency re-run (`C-TECH-053`).**
```
WRITE BEGUN 2026-09-25T20:03: pac solution import (identical command, re-run)
WRITE ATTEMPTED 2026-09-25T20:03: SUCCEEDED cleanly (async 30ed1054-0bb9-f111-aaae-70a8a5079a1b, 32.6s; Published All Customizations)
```
Post-re-run flow-statecode read: byte-identical to the first import's read. Clean.

**Write 2 — `pac code push --solutionName RevitaliseGrantAutomation` (from `src/code-apps/trustee-review-portal`).**
```
WRITE BEGUN 2026-09-25T20:03: pac code push --solutionName RevitaliseGrantAutomation
WRITE ATTEMPTED 2026-09-25T20:04: SUCCEEDED — "App pushed successfully" (app 70869c95-92e5-442f-b5b9-44b3d3e549f6, env 2f7ce6a9-fdb7-e10b-a40a-07f5022ee453) — no classifier refusal this run
```
**Verified live by query**, not by exit code: `pac env fetch` against `canvasapp` filtered on `canvasappid`:

| | before this dispatch (recorded above) | after this push |
|---|---|---|
| `appversion` / `lastmodifiedtime` / `lastpublishtime` | `2026-09-25T10:26:52Z` | `2026-09-25T18:04:06Z` |

The timestamp moved forward, confirming this push carried EF-04/EF-43 content live and was not a no-op — the `IMP-0891` precedent (refusal with no consequence because `dist/` was already identical) does **not** apply to this dispatch.

**Level reached: `DEPLOYED (V3)`** for both the solution import (idempotent, verified by live flow-statecode query) and the Code App push (verified by live `canvasapp` query). **`V4`** — a named person signs in, opens the app, and confirms EF-04's Summary panel and EF-43's new Group applications screen render as specified — **is the reviewer's next action, not performed by this dispatch.**

**No promotion attempted** — DEV only, per this dispatch's explicit scope; no `APPROVE PRD` sought.

**IMPROVEMENT LOG:** 1 entry appended — `IMP-0900` (`write-pre-state-not-captured`, friction: flow-statecode pre-state not captured before the first write this dispatch, reconciled after the fact against values already on record; no operational consequence, no unexpected deactivation observed). Digest regenerated: `python3 scripts/generate-known-failure-modes.py` → 896 entries, 887 distinct lessons. `verify-improvement-log.py` → OK, no new blocker.

```
DEPLOYED TO DEV (V3) ✅  |  feature:trustee-portal-visual-refresh  |  artifact:build/artifacts/trustee-portal-visual-refresh-20260925-2/  |  wbs:6.8,6.10
Prerequisites: n/a this cycle (no new schema; DEV prerequisites satisfied in earlier sessions)
Idempotency re-run: PASS (clean second import, no errors; flow-statecode read byte-identical)
Post-deploy: pac solution import — DONE (2 runs, both clean); pac code push — DONE, verified live by canvasapp query (timestamp advanced, confirms real content change, not a no-op)
Components verified by query: pac code list (Code App live), canvasapp appversion/lastmodifiedtime/lastpublishtime, workflow statecode set (13 rows) — not the full solution-component list (scope-limited to this build's Code-App-only diff)
Assumption register: 25 OPEN rows, all pre-existing carry-forwards unrelated to EF-04/EF-43, none newly closeable in DEV by this dispatch, no C-TECH-058 block
Human open-and-save (V4): OUTSTANDING for: EF-04 Summary panel + EF-43 Group applications screen, live signed-in check — level DEPLOYED (V3)
Warnings: 0 new this dispatch (build-time warnings already triaged in the manifest — 2 accepted, 0 untriaged)
IMPROVEMENT LOG: 1 entry — IMP-0900 (process gap: pre-state not captured before write; no operational consequence) | digest regenerated: YES
Credential-gated steps this session: verify-environment-access.ps1 (ran, FAILED — PROVISION_APP_ID/PROVISION_CERT_THUMBPRINT unset, substituted pac auth list / pac org who per established pattern), ensure-schema.ps1/reconcile-flow-statecodes.ps1 (did not run — no schema/flow change this cycle, EXCLUDED, owner: reviewer or a credentialed session)
No promotion attempted — reviewer scoped DEV only, no APPROVE PRD sought.
Awaiting the reviewer's V4 confirmation (sign in, open the app, confirm EF-04/EF-43 render as specified), or further instruction.
```
