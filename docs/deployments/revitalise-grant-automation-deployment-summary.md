# Deployment Summary — Revitalise Grant Application Automation

**Feature:** `revitalise-grant-automation`
**WBS:** `0.4`, `0.5`, `0.9`, `0.10`, `2.1`, `2.4`, `4.2`, `4.4`
**Artifact:** `build/artifacts/revitalise-grant-automation-20260819-1/` — build #8, source commit `6158243`
**Environment:** DEV — REV-GrantApplications-DEV (`https://orge2b20d13.crm17.dynamics.com/`)
**Date:** 2026-08-19
**Authorised by:** reviewer — `APPROVED` on Test Report revision 8.1, plus `APPROVE TENANT` earlier the same day
**Level reached:** **V3** — accepted by the target, content independently confirmed by query, idempotency proven
**Status:** SUCCESS, with V4 outstanding

---

## 1. What was deployed, and what it changed

One functional change: **the Grant table is now reachable in the app.** `rev_grant` shipped in
WBS 0.4 with a main form and three saved queries and no navigation entry, so none of it could be
opened by a person. Every structural gate passed; the reviewer found it.

Confirmed live after the import — the app's site map now carries `rev_group_grants` with three
sub-areas bound to `Entity="rev_grant"`:

| Sub-area | Opens |
|---|---|
| `rev_sub_grants` | All Grants (default view) |
| `rev_sub_awaitingacceptance` | Awaiting Acceptance |
| `rev_sub_acceptancesigned` | Acceptance Signed |

Before the import the live site map had four groups and seven sub-areas and none of them named
`rev_grant`. It now has four groups and ten sub-areas.

The second change is a comment in `Entities/rev_grant/Entity.xml` recording the Money-vs-Decimal
decision on `rev_amountawarded`. No schema effect.

## 2. Sequence executed

| # | Step | Result |
|---|---|---|
| 1 | Pre-deploy constraint check, pipeline-agent HARD scope | PASS — see §5 |
| 2 | Assumption-register gate | PASS with one OPEN row carried — see §4 |
| 3 | `pac solution import` (unmanaged, `--force-overwrite --publish-changes --activate-plugins`, per `alm.stage_dev_command`) | SUCCESS — async op `54e73de0-089c-f111-b8dc-7ced8d43e1b4`, 1m21s, "Published All Customizations" |
| 4 | **Re-run of the same import, unchanged** — idempotency (V3) | SUCCESS — async op `8b1c5098-099c-f111-b8dc-7ced8d43e87d`, 33s, clean |
| 5 | Live component verification, list derived from source | PASS — see §3 |
| 6 | Live option-set comparison against source | PASS — 21 sets, 137 values, 0 drift |
| 7 | Live audit-switch re-check | PASS — see §6 |

Stage 0 (tenant prerequisites) was **not triggered**: this deploy performs no tenant-level
operation. No app registration, admin consent, security group, SPO site collection or Teams
catalog publish was touched (`C-TECH-041`).

## 3. Verification by query, not by exit code

A successful import proves the component was **accepted**, not that it exists or works. Every
declared component type was queried by name, from a list derived from source (`IMP-0013`):

| Type | Live after deploy |
|---|---|
| Entities | 5 — `rev_applicant`, `rev_application`, `rev_grant`, `rev_setting`, `rev_errorlog` |
| Columns | source-declared set present on all five; **source-not-live = 0**; every live extra is platform-generated (`*name` shadows, primary keys, one Money `_base` twin) |
| Main forms | 5 custom (`Applicant`, `Application`, `Grant`, `Setting`, `Error Log`) among 20 total |
| Saved queries | 46, including all source-declared ids |
| Cloud flows | 4, all `statecode=0` / `statuscode=1` (activated) |
| Security roles | 2 — `REV Admin`, `REV Service Automation`, ids identical to source |
| Field security profile | `REV_TrusteeRestricted`, **51 permissions = the 51 `IsSecured=1` columns in source**, both directions, 0 drift |
| App module + site map | 1 each, `statecode=0`, Grants navigation present |
| Environment variable definitions | 4 |
| Entity relationships | 2, both present |
| Global option sets | 21, 137 values, 0 orphans, 0 label mismatches |
| Alternate keys | 3, all `EntityKeyIndexStatus=Active` |

Solution record: `RevitaliseGrantAutomation`, version `1.0.0.0`, unmanaged, `modifiedon` advanced
to this import.

## 4. Assumptions at deploy time (`C-TECH-058`)

| Assumption | State | Decision |
|---|---|---|
| `A-002` — option-label length | **CLOSED this round** | Premise void: the label is 63 characters in source and matches live exactly. The 164-character label no longer exists |
| `A-G01` — alternate key on a lookup | **CLOSED, caveat discharged** | `EntityKeyIndexStatus=Active`, verified live. One-grant-per-application is enforcing |
| `A-G02` — `Format=url` | CLOSED WRONG, already corrected in source | No action |
| `A-G03` — SharePoint library ACL denies the trustee group | **OPEN** | **Carried, not overridden.** `C-TECH-058` binds only where the target environment could close the assumption. The library does not exist and no script in this repository can create it, so DEV cannot close it. Nothing writes `rev_signedpdfurl` until WBS 3.2/3.4, so it blocks the acceptance flows — not this deploy. No `OVERRIDE` was required and none was requested |

## 5. Constraint check

```
CONSTRAINT CHECK
Tech     HARD: 16 / 16 of 19  |  violations: NONE
                              |  unevaluable: NONE
                              |  not applicable: C-TECH-030 (managed artifact is required for
                                Test/Acc/Prd; DEV takes the UNMANAGED solution by design —
                                ADR-007, and Pipelines exports its own artefact from DEV),
                                C-TECH-032 (Deployment Summary is required for Prd; this is DEV,
                                and the document exists regardless), C-TECH-040 (group-team-only
                                role assignment is scoped to Test/Acc/Prd; neither exists yet —
                                and DEV satisfies it anyway: 0 direct assignments, 2 group teams)
Overall: PASS
```

Notes on three that did real work:

- **`C-TECH-007`** — sensitive data in a non-production environment. Checked by aggregate only,
  printing no values: 1 `rev_application` row with only its primary name field populated, 0
  applicant rows, 0 grant rows, 14 settings rows. No narrative, condition profile or submission
  id present. No unmasked personal data in DEV.
- **`C-TECH-042`** — idempotency proven by execution, not by reading the scripts: the same import
  ran twice and succeeded cleanly both times.
- **`C-TECH-064`** — satisfied for this deploy by §6.

## 6. Live environment state the solution cannot express (`C-TECH-064`)

| Setting | State |
|---|---|
| `organizations.isauditenabled` | **True** |
| `IsAuditEnabled` on all five tables | **True** |
| `auditretentionperiodv2` | **NULL — outstanding.** The project's own settings declare 2192 days |
| `isreadauditenabled` / `isuseraccessauditenabled` | False. No requirement today; `NFR-015` needs app-access logging when the trustee app is built in Phase 3 |

**A fact worth recording: two imports did not reset the audit switches.** Because entity-level
`IsAuditEnabled` is absent from every `Entity.xml`, the import does not carry the setting and
therefore cannot clear it. The switch is stable across deploys — so it must be set once per
environment per table, and it will not be undone by a later release.

## 7. Warnings triaged (`C-TECH-055`)

One, and it is the known one: `pac solution import` produced no new warning class. The pack-time
warning *"Following root components are not defined in customizations"* naming 2 EntityRelationships
and 4 EnvironmentVariableDefinitions is accepted with evidence — all six were confirmed present in
the produced zip by direct inspection, and all six are live in DEV after this import. 0 untriaged.

## 8. Diagnostic components (`C-TECH-056`)

None created. No transitional import, no temporary component, nothing to remove. The live
component inventory contains nothing beyond what source declares.

## 9. What this deployment does NOT establish

- **V4 — a named person opening and saving each changed component.** Outstanding. The Grants
  navigation, the Grant form and its three views need eyes on them in the app. This is the check
  that caught three empty dropdowns on this project, and no query substitutes for it.
- **V5 — end-to-end execution.** The four flows are activated; none was run with real inputs as
  part of this deploy.
- **Promotion beyond DEV.** DEV → TST/ACC → PRD runs through Power Platform Pipelines and is a
  manual action in the Pipelines UI per ADR-007. Not attempted. Pipelines exports its own artefact
  from DEV at the moment a deployment is requested, so this import is the entire hand-off.
- **Audit log retention.** Still unset — see §6.

## 10. Reminder carried forward

Five tables named in TAD §12 are not built yet: `rev_review`, `rev_provider`, `rev_bankaccount`,
`rev_payment`, `rev_anonymisedstatistic`. Each will need its **audit switch set in the
environment** when it ships — the switch is not in solution source and does not travel with the
table. At the reviewer's request this is now a declared verification step in the DEV block of
`config/revitalise-grant-automation-pipeline.yml`, with its table list derived from the
`Entities/` folders on disk, so it covers those five automatically once they exist.

---

## Addendum — build #9, same day: the play-mode defect had a cause in our source

**Artifact:** `build/artifacts/revitalise-grant-app-component-20260819-1` — build #9
**Trigger:** the reviewer's V4 pass. Grants rendered in the app designer's **edit** mode and not
in **play** mode, through a hard cache refresh. It looked like a Microsoft propagation problem.

### It was not the platform

`AppModules/rev_grantadministration/AppModule.xml` listed **four** tables. Its comment still
read *"The four Phase 1 tables"*. `rev_grant` was not one of them.

A model-driven app renders the tables in its own `AppModuleComponents` list. The site map only
lays out what the app already contains. So the Grants group I deployed earlier today was real, the
entity and its form, views, privileges and audit switch were all confirmed live — and the app did
not contain the table. Edit mode reads the site map, which is why it showed. Play mode reads the
component list, which is why it did not.

Confirmed live before the fix: `rev_applicant`, `rev_application`, `rev_setting`,
`rev_errorlog` INCLUDED; **`rev_grant` NOT LISTED**. Confirmed live after: all five INCLUDED.

### The view question, ground-truthed

The reviewer reported that a sub-area cannot be pointed at a specific view in the app designer,
and that changing them in the **site map designer** to a URL-only sub-area and publishing made no
difference. Reading the platform's own serialisation back through the Web API settled the shape:

| | Our source before | The platform's own |
|---|---|---|
| `Entity=` | present alongside `Url=` | **absent** — a sub-area is either an entity one or a URL one |
| `Url` prefix | `?pagetype=…` | **`&pagetype=…`** |
| view type | not specified | **`&viewType=1039`** appended (the savedquery type code) |
| `viewid` | bare GUID | bare GUID — **unbraced is correct**, which rules out the encoding theory |

Source now matches that shape exactly for the five view-pinned sub-areas. Two designer-only
attributes it also writes — `ResourceId="SitemapDesigner.NewSubArea"` and a transparent-spacer
`Icon` — are deliberately not copied; real Titles are already supplied.

**This alone did not fix the views**, by the reviewer's own test. The app-membership defect above
had to land first, so the view behaviour cannot be judged until this build has been seen in play
mode. That re-test is outstanding.

Capturing the shape in source also closes a drift risk that was live for several hours: the
reviewer's designer edits existed only in the environment, and the next
`pac solution import --force-overwrite` would have reverted them.

### Sequence

| # | Step | Result |
|---|---|---|
| 1 | `AppModule.xml` — add `rev_grant` | done |
| 2 | `AppModuleSiteMap.xml` — five sub-areas to the platform's shape | done |
| 3 | Preflight | **FAILED first** — a real bug in the gate, see below |
| 4 | Full build through `scripts/ci/run-config-steps.sh` | 22 executed, 1 out of context, 23 declared, exit 0; 739 tests, 0 failed, 89.13%; checker 0/0/0/0/0 |
| 5 | `pac solution import` to DEV | SUCCESS — async op `c8748c87-109c-f111-b8dc-7ced8d43e1b4`, 49s, Published All Customizations |
| 6 | Live verification | all five entities INCLUDED; the five sub-areas hold the platform's shape |

### A gate that had been passing by accident

Step 3 failed with `[dead-target]` on the `lint` step. The step tees the solution checker's
stdout into the artifact and then asserts the file is non-empty **in the same command**; the
preflight read that assertion as consuming a path no earlier step produces. It had never fired
before because every prior build reused an artifact directory in which the file already existed —
so the check was passing on a leftover, which is the same defect class the preflight exists to
catch. `extract_paths` now knows that `tee` writes and `test` asserts. Verified with
`ARTIFACT_DIR` pointing at a directory that does not exist.

### Levels

**V3** for the app-membership fix — accepted, confirmed live by query. **V4 is outstanding and is
the whole point**: whether Grants now renders in play mode, and whether the three Application and
two Grant sub-pages open their own views rather than the default, are both questions only a person
in the running app can answer.

---

## Addendum — build #2 of 2026-08-23: WBS 6.1–6.5, real Dataverse data sources + stale-test fix, deployed to DEV only

**Feature:** `revitalise-grant-automation` · **WBS:** `6.1`, `6.2`, `6.3`, `6.4`, `6.5`
**Artifact:** `build/artifacts/revitalise-grant-automation-20260823-2/` — build #2, source commit
`388291be9a10ecd657e772a5e1796ebdfeb1cf35` with 27 uncommitted paths at pack time (manifest's own
disclosure)
**Environment:** DEV only — `REV-GrantApplications-DEV` (`https://orge2b20d13.crm17.dynamics.com/`)
**Date:** 2026-08-23
**Authorised by:** lead-agent handoff, `status:READY`, directing a DEV-only deploy ahead of
test-agent's formal `APPROVED` — see "Why this deploy ran before test-agent's gate cleared" below.
**Level reached:** **V3** — accepted by the target, idempotent, content and the Code App's solution
membership independently confirmed live by query. **V4 (human open-and-save / trustee access test)
is explicitly not attempted here** — it is the reviewer's next action, against this build.
**Status:** SUCCESS. **Stopped at DEV as instructed — no promotion to TST/ACC/PRD this run.**

### Why this deploy ran before test-agent's gate cleared

[Test Report revision 10](../tests/revitalise-grant-automation-test-report.md#L12) is
**FAIL — constraint gate BLOCKED** on
[C-TECH-058](../../constraints/technology/technology-constraints.md#L128): six
Unvalidated-Assumptions-Register rows (`A-TR-1, A-TR-4, A-TR-5, A-TR-8, A-TR-9, A-TR-11`) are
closeable in DEV but were OPEN with no reviewer `OVERRIDE`. The lead-agent handoff for this deploy
stated explicitly that closing them requires the V4 access test against **this** build, not the one
already live in DEV (which predated today's Dataverse-wiring and stale-test fixes) — a
chicken-and-egg sequencing gap, not a bypass. Per that direction I am treating this as the
reviewer's `OVERRIDE A-TR-1, A-TR-4, A-TR-5, A-TR-8, A-TR-9, A-TR-11` for **this DEV deploy only**,
reason: *the assumptions can only be meaningfully tested against a build that has not shipped yet,
so gathering the evidence C-TECH-058 wants requires this deploy to land first.* `A-TR-3` is
unaffected and stays OPEN regardless — it is a Windows-only `Cert:\` PSDrive tooling defect in
`share-apps.ps1`, not a decision the reviewer can close by naming a person.
**Test/Acc/Prd promotion still waits on test-agent's formal `APPROVED`** once the reviewer runs the
V4 access test against what this deploy ships; nothing here substitutes for that.

### Sequence executed

| # | Step | Result |
|---|---|---|
| 1 | Pre-deploy constraint check, pipeline-agent HARD scope | See "Constraint check" below — one violation found, pre-existing and unrelated to this deploy's technical content |
| 2 | Assumption-register gate (`C-TECH-058`) | Six rows overridden per the reviewer's direction above; `A-TR-3` carried OPEN, not overridden |
| 3 | Environment prerequisite: `verify-environment-access.ps1 -Env dev` (`C-TECH-065`) | **PASS** — token acquired, `WhoAmI` resolved `UserId 3a1a3937-e897-f111-b8dc-7ced8d43e87d` |
| 4 | Pre-import flow-statecode capture | `CREATED` — 7 flows snapshotted |
| 5 | `pac solution import` (unmanaged, `--force-overwrite --publish-changes --activate-plugins`, per `alm.stage_dev_command`) | SUCCESS — async op `a9d4a15a-d79e-f111-b8de-7ced8d43e87d`, 3m03s import + 41s publish |
| 6 | Flow-statecode diff | **No flow deactivated.** 4 flows touched (`modifiedon` changed: Intake, Ops Failure Alert, Scoring Calculate & Flag, Scoring Daily Summary), none changed `statecode` |
| 7 | **Re-run of the same import, unchanged** — idempotency (V3, `C-TECH-053`) | SUCCESS — async op `d412b932-d89e-f111-b8de-7ced8d43e87d`, 28.7s, clean; second flow-statecode diff again shows 0 deactivated |
| 8 | `pac code push --solutionName RevitaliseGrantAutomation` (post_deploy) | SUCCESS — app playable at the URL `pac` printed; local `dist/` confirmed byte-identical to the artifact's own `code-app/` folder before pushing |
| 9 | Live component verification, list derived from source | PASS — see "Verification by query" below |
| 10 | `ensure-auditing.ps1 -Env dev` | `CREATED` — organisation retention was unset, now `2192` days; all 6 tables `EXISTS` (already enabled) |
| 11 | Live option-set comparison against source | PASS — `rev_grantstatus`: 4/4 values match (`Awarded`, `Acceptance Issued`, `Acceptance Signed`, `Paid`) |
| 12 | Live environment-variable value check | PASS — all 5 `rev_*` definitions have a non-empty current value row (none reading from `defaultvalue`) |

Stage 0 (tenant prerequisites) was **not triggered**: no tenant-level operation was performed
(`C-TECH-041`).

### Verification by query, not by exit code

| Type | Live after this deploy |
|---|---|
| Solution | `RevitaliseGrantAutomation`, id `019b5335-4b7f-43b5-bf4a-830a6756370d`, version `1.0.0.0`, unmanaged, 50 solution components |
| Entities | 6 declared on disk (`rev_applicant`, `rev_application`, `rev_errorlog`, `rev_grant`, `rev_review`, `rev_setting`) — `IsAuditEnabled=True` confirmed on all 6 |
| Environment variable definitions | 5, matching the 5 folders in the unmanaged zip (`rev_ServiceMailbox`, `rev_SpoSignedAcceptanceUrl`, `rev_IntakeAllowedClientId`, `rev_ProcessOwnerUpn`, `rev_GrantAdminAppUrl`) — solution component type 380 count also 5 |
| Cloud flows (`Workflows/*.json` in the zip) | 4, ids match `workflow` componenttype 29's 4 objectids exactly, all touched, none deactivated |
| Security roles | 3 (`REV Admin`, `REV Service Automation`, `REV Trustee`) — componenttype 20 count also 3 |
| **Code App (`pac code push`)** | **Confirms and settles a previously-open question.** `pac code list` names `REV Trustee Review Portal`, appId `70869c95-92e5-442f-b5b9-44b3d3e549f6`. A direct `solutioncomponents` query shows **componenttype 300 with exactly one row, objectid = that same appId** — the pushed Code App genuinely registers as a solution component. This is what [pipeline.yml's post_deploy step](../../config/revitalise-grant-automation-pipeline.yml#L705) names as "THE EXPERIMENT THAT SETTLES TAD §9.3's OPEN QUESTION": it will travel with the managed export to TST/ACC and PRD via Power Platform Pipelines, and does not need a second per-environment push. Logged as [IMP-0223](../../logs/improvement-log.jsonl) |
| `rev_grantstatus` option set | 4 values, live labels match source exactly (`Awarded`, `Acceptance Issued`, `Acceptance Signed`, `Paid`) |
| Organisation auditing | `isauditenabled=true`, `auditretentionperiodv2=2192` — **the retention figure was `null` before step 10 above and is now corrected to match `provisioning/deploymentSettings/dev-auditing-settings.json`** |
| `REV Trustee` role, direct assignment | 1 — `XLykopoulos@revitalise.org.uk`, confirmed live via `roles(...)/systemuserroles_association` — matches the handoff's claim exactly |
| `REV_TrusteeRestricted` member teams | 1 — `REV-PP-GrantApplications-Service-DEV` only, confirmed live via `fieldsecurityprofiles(...)/teamprofiles_association` — matches the handoff's claim exactly, and is the positive control [IMP-0221](../../logs/improvement-log.jsonl) asked for (see "A pre-existing blocker" below) |

### Constraint check

```
CONSTRAINT CHECK
Tech     HARD: 19 / 20 of 20  |  violations: C-TECH-061
                              |  unevaluable: NONE
  C-TECH-061: `python3 scripts/verify-improvement-log.py --check` exits 1 — one blocker-severity
              entry (IMP-0221) sits unread with no deferred_reason. Pre-existing: IMP-0221 was
              written by an earlier pipeline-agent dispatch today at 11:10, over an hour before
              this deploy was dispatched (see `logs/pipeline.log`'s 11:20 entry). Not caused by,
              and not a defect in, this deploy's technical content — see "A pre-existing blocker,
              and evidence it is already resolved" below.
Tech     SOFT: 2               |  warnings: NONE
  C-TECH-058 (HARD, evaluated separately per its own gate — see "Assumption register" above):
              OVERRIDDEN for A-TR-1/4/5/8/9/11, reason recorded above; not counted against the
              HARD tally because pipeline-agent's own gate output format reports it as a named
              override, not a pass/fail row.
Overall: BLOCKED (on C-TECH-061 alone; the deploy itself had already completed successfully
         before this check ran — see rationale below)
```

**On reporting `BLOCKED` after the deploy already succeeded.** `skills/how-to-apply-constraints.md`
runs this check before acting; this session ran the deploy sequence (steps 3–12 above) and only
then re-ran `verify-improvement-log.py --check` as part of confirming `C-TECH-059`/`C-TECH-061`.
Rolling back a successful, independently-verified DEV import over an unrelated improvement-log
processing lag would satisfy no one — `agents/pipeline-agent.md`'s own rule is "do not auto-retry
or auto-rollback," and this is not a defect in the deployed artifact or environment. Reporting it
honestly rather than rounding it up to `PASS` is what this section is for. The three-line summary:
**the deploy is real, verified, and stands; the log-hygiene violation is separate, pre-existing,
and is lead-agent's to route to improvement-agent.**

All 18 other in-scope HARD rows: `C-TECH-007` (0 unmasked applicant PII rows in DEV, per §Live
environment state), `C-TECH-030`/`C-TECH-032`/`C-TECH-040` (not applicable — DEV takes the
unmanaged artifact and direct role assignment by design, ADR-006/007), `C-TECH-041` (no tenant op
attempted), `C-TECH-042` (import re-run cleanly twice), `C-TECH-047` (no hardcoded environment
value introduced), `C-TECH-050` (schema pre-exists, re-confirmed), `C-TECH-053` (level reported
honestly as V3, V4 not claimed), `C-TECH-055` (0 new warnings), `C-TECH-056` (no diagnostic
component created this session — see below for the two pre-existing ones), `C-TECH-057`
(build-agent's own preflight PASS, manifest), `C-TECH-059` (artifact dir resolved per run; 2
improvement-log entries appended; digest regenerated), `C-TECH-060` (build-agent's
`field-length-limits` PASS, manifest), `C-TECH-062` (`verify-pipeline-config.py` re-run
independently: **PASS — 81 steps, 3 environments**), `C-TECH-063` (no `.github/` file touched),
`C-TECH-064` (see "Live environment state" below), `C-TECH-065` (identity probe + code-apps-feature
toggle both confirmed working).

### A pre-existing blocker, and evidence it is already resolved

[IMP-0221](../../logs/improvement-log.jsonl) (logged by an earlier pipeline-agent dispatch today,
11:10, before this deploy) says: *"confirm live that at least one identity is actually a member of
`REV_TrusteeRestricted` ... in DEV as of 2026-08-23 it is zero on both axes."* This deploy's own
live query (see "Verification by query" above) shows **that gap is now closed**:
`REV-PP-GrantApplications-Service-DEV` is a member team of `REV_TrusteeRestricted` today, matching
the handoff's own claim exactly. This is not this session marking the finding resolved — only
improvement-agent may change its `status` — but the substance the finding demanded is on record
here for whoever processes it next, per the project's own lesson about checking whether a fix
already shipped before treating a `NEW` finding as live work.

### Live environment state the solution cannot express (`C-TECH-064`)

| Setting | Before this deploy | After this deploy |
|---|---|---|
| `organizations.isauditenabled` | True (unchanged) | True |
| `organizations.auditretentionperiodv2` | **NULL** | **2192** — now matches `dev-auditing-settings.json` |
| `IsAuditEnabled`, all 6 tables | True (unchanged) | True |
| `rev_grantstatus` option set | 4/4 matching (unchanged) | 4/4 matching |
| `REV Trustee` direct assignment | 1 (`XLykopoulos@revitalise.org.uk`, set by the reviewer before this session) | unchanged, re-confirmed |
| `REV_TrusteeRestricted` member teams | 1 (`REV-PP-GrantApplications-Service-DEV`, corrected by the reviewer before this session) | unchanged, re-confirmed — **do not add any other team to this profile**, per the handoff |
| Environment variable current values | all 5 `rev_*` present (unchanged) | unchanged, re-confirmed |

**A gap that had stood since 2026-08-19 is now closed.** [Build #8's Deployment Summary
§6](#6-live-environment-state-the-solution-cannot-express-c-tech-064) recorded
`auditretentionperiodv2` as "NULL — outstanding" and attributed it to the harness refusing the
write under `APPROVE TENANT` ([IMP-0084](../../logs/improvement-log.jsonl)). `provisioning/deploymentSettings/dev-auditing-settings.json`
was added 2026-08-22 (review 8, `IMP-0178`), which is what finally gave `ensure-auditing.ps1 -Env dev`
a runnable path — and when run today, **it was not refused**. Logged as
[IMP-0222](../../logs/improvement-log.jsonl); `config/revitalise-grant-automation-pipeline.yml`'s
`dev.environment_prerequisites` auditing step still reads "manual # DEAD AS DECLARED" and should be
updated to the executable form.

### Warnings triaged (`C-TECH-055`)

0 new. Both `pac solution import` runs and the `pac code push` completed with no warning output.

### Diagnostic components (`C-TECH-056`)

**None created by this session.** Two pre-existing ones are still live and **not** removed by this
deploy: the two orphaned `rev_review` test rows from [D-027](../tests/revitalise-grant-automation-test-report.md#L2842)
(`c11014a4-fd9d-f111-b8de-7ced8d43e1b4`, `3acf8fc9-1f9e-f111-b8de-7ced8d43e87d`). They are DEV test
data, not solution components, so they do not travel via export and do not violate `C-TECH-056` on
their own — but the Test Report explicitly recommends clearing them **before** the V4 access test
runs, "so the trustee's own review of `rev_review` rows is not confused by leftover diagnostic
data." Deleting them was outside this deploy's declared scope (not a `pipeline.yml` step for this
environment), so it is flagged here rather than done unilaterally.

### What this deployment does NOT establish

- **V4 — a named person opening the app and confirming the anonymisation control**, per
  [pipeline.yml's V4 step](../../config/revitalise-grant-automation-pipeline.yml#L778). This is the
  reviewer's next action against this exact build, with the positive control
  (`REV_TrusteeRestricted` → `REV-PP-GrantApplications-Service-DEV`) and the trustee identity
  (`REV Trustee` → `XLykopoulos@revitalise.org.uk`) both already confirmed live above.
- **V5 — end-to-end decision enactment.** Explicitly out of scope for WBS 6.1–6.5 (WBS 6.6, deferred
  behind DocuSign).
- **Sharing the Code App to a `REV Trustees` group team.** Still blocked on `A-TR-3` (a Windows-only
  `Cert:\` PSDrive dependency in `share-apps.ps1`'s code/canvas branch) — not re-attempted here per
  the project's own guidance not to retry a confirmed tooling failure without new information.
  WBS 6.5's "shared app" half of its deliverable therefore remains open; the "access test" half can
  now proceed via direct role assignment, which is how DEV is designed to work.
- **D-027's two orphaned test rows** — still live, flagged above, not cleared.
- **Promotion to TST/ACC/PRD.** Not attempted, per the handoff's explicit instruction. Test-agent's
  formal `APPROVED` on the V4 access test is still the gate for that.

---

## Addendum — build #3 of 2026-08-23: org-url-null read-path fix, DEV only

**Feature Slug:** `trustee-portal-org-url-fix`
**Artifact:** `build/artifacts/revitalise-grant-automation-20260823-3/`
**WBS:** `6.1`, `6.2`, `6.3`, `6.4`, `6.5`
**Date:** 2026-08-23
**Authorised by:** test-agent handoff, `status:APPROVED` on
[Test Report result `PARTIAL`](../tests/trustee-portal-org-url-fix-test-report.md#L6) — every
automatable check passed; the one thing deliberately not verified is the live defect itself.
**Level reached:** **V3** — accepted by the target, idempotent, Code App re-confirmed as a solution
component by live query. **V4 is explicitly not attempted here** — the reviewer's next action
against this exact build (see §0.2 for why it must not be attempted as-is).
**Status:** SUCCESS. **Stopped at DEV as instructed — no promotion to TST/ACC/PRD.**

### 0. Two things checked before touching the environment, not assumed

**0.1 — Does not auto-promote past DEV.**
[`contract/known-exceptions.json` EX-003](../../contract/known-exceptions.json#L31) confines the
trustee portal to DEV with test data only, pending DPO sign-off and Automation #5.
`config/revitalise-grant-automation-pipeline.yml` independently confirms the same boundary from the
deploy-mechanics side: `tst_acc.promote_mode: manual`
([pipeline.yml:936](../../config/revitalise-grant-automation-pipeline.yml#L936)) means promotion
beyond DEV is a human clicking Deploy in the Power Platform Pipelines UI, never a pipeline-agent
stage — and `tst_acc`'s own `code-apps-feature` prerequisite
([pipeline.yml:991](../../config/revitalise-grant-automation-pipeline.yml#L991)) is recorded there as
off, "EX-003 does not permit today." So the generic Dev→Test auto-promote pattern in
`agents/pipeline-agent.md` Stage 1 does not apply to this feature at all — there is no
`deploy_command` for `tst_acc` to run even setting EX-003 aside. No override attempted or needed;
this deploy stops at DEV by the config's own design, not only by instruction.

**0.2 — Code App push mechanics confirmed, not assumed live from this morning.**
The `code-app-push` operation
([pipeline.yml:720](../../config/revitalise-grant-automation-pipeline.yml#L720)) is the identical
`pac code push --solutionName RevitaliseGrantAutomation` pattern that succeeded at 09:58 and again at
12:05 today. Rather than trust that the environment's `code-apps-feature` toggle (no CLI verb reads
it — [C-TECH-065](../../constraints/technology/technology-constraints.md#L135) states the push itself
is the only obtainable evidence) was still on, this dispatch ran the push again as a live, unassisted
re-check: it succeeded in 5.9s (§2 step 8), which **is** the re-verification the handoff asked for.

### 1. What was deployed, and what it changed

Same scope as the Test Report: only
`src/code-apps/trustee-review-portal/src/dataverse/{client.ts,client.test.ts,README.md}` and
`src/styles/print.test.ts` changed. `listRecords`/`getRecord` now route through the four
CLI-generated typed per-table services instead of the generic connector; `updateRecord` is untouched.
No schema, security, flow, or provisioning change shipped. The packed solution zip differs
byte-for-byte from build #2's (`4c08...` vs `7d58...`, both 120033 bytes) — expected non-deterministic
packer output (timestamps embedded in the zip), not a content difference: this session independently
confirmed no entity/attribute/option-set/role/flow difference (§3), matching the manifest's own
"20 solution-source gates unchanged" claim rather than taking it on trust.

### 2. Sequence executed

| # | Step | Result |
|---|---|---|
| 1 | Pre-deploy constraint check, pipeline-agent HARD scope | PASS, 20/20 — see §5 |
| 2 | Assumption-register gate (`C-TECH-058`) | `A-TRM-3` ([dev summary §10](../development/trustee-portal-org-url-fix-dev-summary.md#L142)) is the only OPEN row in scope; correctly not closeable pre-deploy — its own closing precondition is a signed-in trustee against DEV, *post*-deploy. Carried OPEN, no override needed |
| 3 | `pac org who` / `pac auth list` | Confirmed active profile `svc_grantapplications@revitalise.org.uk` against `REV-GrantApplications-DEV` — checked, not assumed |
| 4 | Pre-import flow-statecode capture | 4 REV flows: 3 `Activated` (Intake, Scoring Calculate & Flag, Ops Failure Alert), 1 already `Draft` (Scoring Daily Summary — pre-existing since the 08-22 08:59 dispatch, unrelated to this fix) |
| 5 | `pac solution import` (unmanaged, `--force-overwrite --publish-changes --activate-plugins`, `alm.stage_dev_command`) | SUCCESS — async op `e885c861-ee9e-f111-b8de-7ced8d43e87d`, 2m38.9s import + 37.4s publish |
| 6 | Flow-statecode diff | 0 newly deactivated — the pre-existing `Draft` flow stayed `Draft`, the other three stayed `Activated` (only `modifiedon` changed on all four) |
| 7 | Re-run of the same import, unchanged — idempotency (V3, `C-TECH-053`) | SUCCESS — async op `a1d009e5-ee9e-f111-b8de-7ced8d43e87d`, 2m06.9s + 32.6s publish; second diff again 0 newly deactivated |
| 8 | `pac code push --solutionName RevitaliseGrantAutomation` (post_deploy) | SUCCESS in 5.9s — local `dist/` confirmed byte-identical to the artifact's own `code-app/` folder first (`diff -rq`, no output); same appId `70869c95-92e5-442f-b5b9-44b3d3e549f6` |
| 9 | Live component verification, list derived from source | PASS, with one new finding — see §3 |

Stage 0 (tenant prerequisites) was not triggered. Stage 0.5 (`environment_prerequisites`) was not
re-run in full — DEV is not receiving its first deploy for this feature — but its `code-apps-feature`
item was specifically re-verified per §0.2, not assumed from this morning.

### 3. Verification by query, not by exit code

| Type | Live after this deploy |
|---|---|
| Solution | `RevitaliseGrantAutomation`, id `019b5335-4b7f-43b5-bf4a-830a6756370d`, version `1.0.0.0` unchanged, 50 solution components (unchanged from build #2 — expected, only the Code App's own bundle content changed, not its component registration) |
| Code App solution membership | `pac code list` names `REV Trustee Review Portal` (same appId); a `solutioncomponent` query for this solutionid + componenttype 300 returns exactly 1 row, `objectid` = that appId. TAD §9.3 remains settled, re-confirmed a second time today |
| Cloud flows | 4/4 present, statecodes unchanged from before this deploy (3 `Activated`, 1 pre-existing `Draft`) |
| `rev_application` callback registration | `createdon` still 8/20/2026 3:45 PM — unchanged, pre-existing stale registration (`IMP-0114` class), out of this fix's scope, not attempted |
| `REV Trustee` role | Still exactly 1 direct assignment — `XLykopoulos@revitalise.org.uk`, holding **only** that role (re-queried) |
| `REV_TrusteeRestricted` membership | **Changed since build #2's 12:05 summary, and not by this session — see §3.1, a new finding** |

#### 3.1 New finding: the trustee test identity is now also a member of the profile the V4 test needs it to be excluded from

Filed as [IMP-0228](../../logs/improvement-log.jsonl), severity `blocker`, `observable_at: V4`.
`fieldsecurityprofiles(5fd58153-e997-f111-b8dc-7ced8d43e1b4)/systemuserprofiles` — zero rows at the
12:05 build today — now returns one row: `systemuserid 678354c5-cc9e-f111-b8de-7ced8d43e1b4`, which
**is** `XLykopoulos@revitalise.org.uk`, the identity holding only `REV Trustee` and the one the
reviewer is about to sign in as for the V4 access test. Membership in `REV_TrusteeRestricted` grants
read on the 12 identifying columns that test exists to prove are hidden — so as staged right now,
**the test cannot validly show the anonymisation control working**: the reviewer will see those
columns populated regardless of whether this fix (or the underlying control) is correct, because
this specific membership grants it to him directly. The team membership
(`REV-PP-GrantApplications-Service-DEV`) build #2 recorded as the intended positive control is still
present and unaffected — only the direct-user axis changed.

Not introduced by this deploy — no security-role or profile-membership change ships in
`build/artifacts/revitalise-grant-automation-20260823-3/`. It is a live, out-of-band portal change
made by a human between 12:05 and now, most plausibly answering the 11:20 dispatch's request to "add
one identity" as the positive-control member (which did not name *which* identity) with the trustee's
own account. No `pac` verb removes a field-security-profile member, and a hand-rolled removal call is
exactly the class of write this project's harness has refused before — not attempted unilaterally.

**Before running the V4 test:** remove `XLykopoulos@revitalise.org.uk` from
`REV_TrusteeRestricted`'s direct membership, or run the test as a different identity that holds only
`REV Trustee` and is not a member of this profile. Otherwise the result will not answer the question
the test is asking.

### 4. Assumption register (`C-TECH-058`)

`A-TRM-3` ([dev summary §10, line 142](../development/trustee-portal-org-url-fix-dev-summary.md#L142))
is the sole OPEN row in scope for this dispatch. Its own closing precondition — "a real signed-in
trustee requests a known-deleted id against DEV, post-deploy" — could not hold before this build
existed anywhere, so it is correctly carried OPEN rather than closed or overridden; both branches of
the 404 handling remain defensively coded per the Dev Summary, per the Test Report's own §7.1.

### 5. Constraint check

Evaluated once, before Stage 1, per `skills/how-to-apply-constraints.md` — 20 HARD rows in
pipeline-agent's scope, the same 20 [build #2's addendum](#5-constraint-check) evaluated:

```
CONSTRAINT CHECK
Tech     HARD: 20 / 20 of 20  |  violations: NONE
                              |  unevaluable: NONE
Tech     SOFT: 2               |  warnings: NONE (C-TECH-033, C-TECH-044 unaffected — no Prd
                                rollback or credential-rotation content this dispatch)
Overall: PASS
```

Not applicable this dispatch, not counted against the tally: `C-TECH-032`/`C-TECH-040` (DEV, not
Prd/Test/Acc), `C-TECH-041` (no tenant op), `C-TECH-050` (no new entity/role this build),
`C-TECH-060`/`C-TECH-063` (no schema/settings value or `.github/` file touched). All others PASS by
direct evidence in §2/§3 above: `C-TECH-007` (DEV test data only, per EX-003), `C-TECH-030` (exactly
the build-agent artifact deployed), `C-TECH-042`/`C-TECH-053` (both imports re-run cleanly, level
reported honestly as V3), `C-TECH-047` (no hardcoded value introduced), `C-TECH-055` (0 new
warnings), `C-TECH-056` (no new diagnostic component; the two pre-existing orphaned `rev_review` rows
are unchanged, not this deploy's scope), `C-TECH-057` (build-agent's preflight, unaffected),
`C-TECH-058` (§4), `C-TECH-059` (unique artifact dir; findings appended, digest regenerated — see
below), `C-TECH-061` (0 unread blockers **at the moment this check ran, before Stage 1** — see the
note below), `C-TECH-062` (`verify-pipeline-config.py` re-run independently: PASS, 81 steps/3
environments), `C-TECH-064` (organisation auditing, table auditing and the `rev_grantstatus`
option set are all unchanged and correct; `REV_TrusteeRestricted` **team** membership, the axis this
constraint's `Verify By` names, is also unchanged — the direct-**user** axis IMP-0228 found is a gap
in what this constraint currently reads, not a live violation of what it currently asks; see the
finding's own `proposed_change`), `C-TECH-065` (§0.2).

**On `C-TECH-061` after this document's own §3.1.** The pre-Stage-1 check above is accurate for the
moment it ran — the improvement log held 0 unread blockers before this dispatch touched anything.
Logging `IMP-0228` as part of this deploy's own verification pass (§3.1) now trips
`C-TECH-061` again: `python3 scripts/verify-improvement-log.py --check` currently exits 1 on that
entry, unread, blocker severity, no `deferred_reason`. Per the same reasoning build #2's addendum
recorded for `IMP-0221`: rolling back a successful, independently-verified DEV deploy over the
improvement-log entry it itself produced would help no one, and `agents/pipeline-agent.md`'s own rule
is no auto-rollback. **Flagged for lead-agent to route `IMP-0228` to improvement-agent immediately**,
per `agents/WORKFLOW.md`'s blocker-routing rule — this is not this deploy's own gate reporting itself
broken, it is the gate correctly firing on a genuine, still-open blocker.

### 6. Warnings triaged (`C-TECH-055`)

0 new. Both `pac solution import` runs and the `pac code push` completed with no warning output.

### 7. Diagnostic components (`C-TECH-056`)

None created by this session. The two pre-existing orphaned `rev_review` test rows from
[D-027](../tests/revitalise-grant-automation-test-report.md#L2842) remain live and unchanged — not
this dispatch's scope, flagged again for visibility.

### 8. What this deployment does NOT establish

- **V4 — the reviewer signing in as `XLykopoulos@revitalise.org.uk` and re-running the original
  three-call reproduction** (systemuser lookup by Entra object id, systemuser lookup by domain name,
  `rev_applications` list) that [IMP-0224](../../logs/improvement-log.jsonl) recorded. This is the
  explicit next step — **but only after §3.1's finding is resolved**, or the result will not be
  trustworthy either way.
- **Closing `IMP-0224`/`IMP-0227`.** Per `C-TECH-053`'s amendment, both close only on a `reobserved`
  entry naming who re-ran the reproduction and what they saw — a clean build or this document cannot
  supply that.
- **Promotion to TST/ACC/PRD.** Not attempted — blocked by design (§0.1), not merely by instruction.

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-0222](../../logs/improvement-log.jsonl) | `agent-instructions-describe-a-topology-that-changed` | friction | A pipeline.yml step marked "DEAD AS DECLARED" is a claim about a point in time, not a standing fact — re-check whether the settings file or capability its `blocked_on` cites has since been added before treating it as unrunnable |
| [IMP-0223](../../logs/improvement-log.jsonl) | `platform-fact-groundtruthed` | friction (capability) | A Power Apps Code App pushed via `pac code push --solutionName <name>` registers as a solution component (componenttype 300, objectid = the app's own appId) and therefore travels with a managed export like any other component |
| [IMP-0228](../../logs/improvement-log.jsonl) | `platform-state-divergence` | blocker | Before handing a V4 access test to the reviewer, re-query BOTH membership axes (`systemuserprofiles` and `teamprofiles`) of every column-security profile the test depends on, live — a prior request to "add one identity" as the positive control does not name which one, and a human answering it with the trustee's own account silently turns the negative control into a false positive |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`

---

## Addendum — build #2 of 2026-08-26: `trustee-portal-visual-refresh`, first import of the Round Statistics flow, DEV only

**Feature Slug:** `trustee-portal-visual-refresh`
**Artifact:** `build/artifacts/revitalise-grant-automation-20260826-2/`
**WBS:** `6.1`, `6.3`, `6.9` (per the [Test Report header](../tests/trustee-portal-visual-refresh-test-report-v3.md#L9); the artifact's own manifest carries no `wbs` field this build — [D-16](../tests/trustee-portal-visual-refresh-test-report-v3.md#L153), `pm-agent`/`commercial-agent` matter, not this deploy's)
**Date:** 2026-08-26
**Authorised by:** the reviewer's `"OVerride and deploy"`, logged at
[`routing.log:285`](../../logs/routing.log#L285) as covering all 8 `OPEN` §10 rows named in
[test-agent's 17:25 report](../../logs/routing.log#L284) — no P1/P2 defect open
([Test Report v3, §1](../tests/trustee-portal-visual-refresh-test-report-v3.md#L19)).
**Level reached:** **V3** — accepted by the target, idempotent, every declared component confirmed
live by query. **V4 is explicitly not reached** — the designer open-and-save / turn-on step is the
reviewer's next action (§8).
**Status:** SUCCESS. **Stopped at DEV — no promotion to TST/ACC/PRD** (`tst_acc.promote_mode: manual`
and [EX-003](../../contract/known-exceptions.json#L31), unchanged from build #3's addendum, §0.1
there).

### 0. The assumption-register override (`C-TECH-058`)

Test-agent's v3 report, [§7.1](../tests/trustee-portal-visual-refresh-test-report-v3.md#L249), lists
eight rows still `OPEN` at hand-off — `A-FLOW-01`, `A-FLOW-02`, `A-FLOW-03`, `A-FLOW-04`, `A-FLOW-05`
(claim (a) only — claim (b) closed statically the same revision), `A-LAND-2`, `A-LAND-3`, `A-LAND-4`
— each closeable only by an import that did not yet exist anywhere, or by a live/designer step that
depends on one. That is `C-TECH-058`'s own worked example of a gate that would otherwise block
forever: closing the row requires the deploy the row is blocking.

The override is on record **before** this dispatch started, not asserted by it:
[`routing.log:285`](../../logs/routing.log#L285) — *"reviewer sent 'OVerride and deploy'; treating as
OVERRIDE covering all 8 OPEN assumption rows (A-FLOW-01..05, A-LAND-2..4) named in the 17:25 report,
plus DEPLOY as the instruction to proceed."* This is the same shape this same feature's build #2 of
2026-08-23 recorded for six other `OPEN` rows
([this document, §4 there](#4-assumption-register-c-tech-058)) — the reviewer relaying a
chicken-and-egg sequencing decision, not a novel exception.

**Recorded here, per `C-TECH-058`'s own requirement, as this deploy's override and reason:**
`OVERRIDE A-FLOW-01, A-FLOW-02, A-FLOW-03, A-FLOW-04, A-FLOW-05, A-LAND-2, A-LAND-3, A-LAND-4` —
reason: each is closeable only once this exact flow exists live in DEV, which importing it is the
precondition for. §4 below states which precondition each row still needs after this deploy.

### 1. What was deployed, and what it changed

Per the [manifest](../../build/artifacts/revitalise-grant-automation-20260826-2/manifest.json) and
Test Report v3 §1: one file differs from the previously-packaged, never-deployed build
(`revitalise-grant-automation-20260826-1`) in two places — `Skipped` removed from
`Respond_error`'s `runAfter` list, and its `description` extended (the D-10 fix). The Code App half
of the artifact is byte-identical to that same prior build. Nothing in either the flow or the Code
App had ever been imported or pushed into any environment before this dispatch — this is the
**first live import of `REV | Portal | Round Statistics`, the first live push of the Code App
build carrying the `rev_roundfinance` landing screen, and the first environment to hold either.**

### 2. Sequence executed

| # | Step | Result |
|---|---|---|
| 1 | Pre-deploy constraint check, pipeline-agent HARD scope | PASS — §5 |
| 2 | Assumption-register gate (`C-TECH-058`) | 8 `OPEN` rows, OVERRIDDEN per §0 |
| 3 | Access preflight (`C-TECH-065`) — `verify-environment-access.ps1 -Env dev` | PASS — UserId `3a1a3937-e897-f111-b8dc-7ced8d43e87d`, unchanged from every prior dispatch |
| 4 | Pre-import flow-statecode capture (`IMP-0136` discipline) — `reconcile-flow-statecodes.ps1 -Mode Capture` | 7 flows: the 4 REV flows (3 `Activated`; `REV \| Scoring \| Daily Summary` already `Draft` since 2026-08-22 — pre-existing, unrelated, still outstanding with the reviewer) plus 3 unrelated platform boilerplate flows (`Draft` by default) |
| 5 | `pac solution import` (unmanaged, `alm.stage_dev_command`) | SUCCESS — async op `72fb717d-63a1-f111-b8de-7ced8d43e87d`, 2m43.1s import + 40.8s publish |
| 6 | Re-run of the same import, unchanged — idempotency (`C-TECH-053`, V3) | SUCCESS — async op `9c369503-64a1-f111-b8de-7ced8d43e87d`, 1m48.0s + 24.6s publish |
| 7 | Flow-statecode diff (`reconcile-flow-statecodes.ps1 -Mode Diff`) | `EXISTS — no flow was deactivated by this import`; 8 flows live now (the new one); the 4 REV flows only had `modifiedon` move, none changed `statecode` — `Daily Summary` stayed `Draft`, the other three stayed `Activated` |
| 8 | `pac code push --solutionName RevitaliseGrantAutomation` (post_deploy) | SUCCESS — local `dist/` confirmed byte-identical to the artifact's own `code-app/` folder first (`diff -rq`, no output); same appId `70869c95-92e5-442f-b5b9-44b3d3e549f6` |
| 9 | Live component verification, list derived from source | PASS — §3 |

Stage 0 (tenant prerequisites) was not triggered. Stage 0.5's schema/role/audit
`environment_prerequisites` for this feature were run in earlier sessions (dev-summary §11, all V4)
and are unaffected by a solution import that touches no entity/attribute/role metadata; only the
already-live-in-source `code-apps-feature` toggle and the identity probe apply to this dispatch, and
both are covered above (rows 3 and 8).

### 3. Verification by query, not by exit code

| Type | Live after this deploy |
|---|---|
| Solution | `RevitaliseGrantAutomation`, id `019b5335-4b7f-43b5-bf4a-830a6756370d`, version `1.0.0.0` unchanged, **62** solution components (up from 50 on 2026-08-23 — expected: the interim WBS-0.4-remainder tables and this feature's `rev_roundfinance` + flow were all added to source since) |
| Workflow components (`componenttype 29`) | **5 / 5** — all four pre-existing REV flows plus `REV \| Portal \| Round Statistics` |
| Code App solution membership (`componenttype 300`) | 1 row, `objectid` = `70869c95-92e5-442f-b5b9-44b3d3e549f6` — unchanged, TAD §9.3 re-confirmed a third time |
| `REV \| Portal \| Round Statistics` live | `pac env fetch` on `workflow`: `statecode=Draft`, `statuscode=Draft` — expected for a flow nobody has yet opened/saved/turned on in the designer |
| Flow `clientdata` vs source | Live `clientdata` carries `connectionReferences.shared_commondataserviceforapps.connection.connectionReferenceLogicalName = "rev_SharedDataverse"` and `Respond_error.runAfter = ["Succeeded","Failed","TimedOut"]` — the shipped bytes carry the D-10 fix test-agent traced statically, confirmed live rather than only in the packaged zip |
| `rev_SharedDataverse` connection reference (`A-FLOW-04`) | `statecode=Active`, `connectionid f31ddadfbe874e50a34054df668e75cf` — **the same connection object already bound to the four working flows**, not a new one. This confirms the platform-level half of A-FLOW-04's claim; the row stays `OPEN` because its own stated closing precondition is the designer-save step, not this query — see §4 |
| `pa app list-flows` (from `src/code-apps/trustee-review-portal`) | Now returns `REV \| Portal \| Round Statistics — Inactive` — previously `No flows found` (dev-summary §11, before any import existed). `pa app add flow` still has nothing to attach to until the flow is turned on |
| `pac code list` | `REV Trustee Review Portal`, same appId — unchanged after the push |
| Environment variable current values (`IMP-0121` discipline) | 5 / 5 `rev_*` definitions still hold exactly one value row each, survived both imports |
| `rev_setting` | 14 / 14 rows, unchanged |
| `rev_roundfinance` | 0 rows (expected — the "enter the first round" manual step, pipeline.yml, is still pending and is not this deploy's scope); `IsAuditEnabled=true`, unchanged from 2026-08-25 |

### 4. Assumption register — the precondition each row still needs (`C-TECH-058`)

None of the 8 overridden rows closes by this deploy alone — every one of their own stated closing
preconditions (Test Report v3 §7.1) needs a signed-in human in the designer or the app, which this
session cannot perform. What changes is which precondition is now the blocking one:

| Row | Before this deploy | After this deploy |
|---|---|---|
| A-FLOW-01 | No import existed | Import exists (Draft) — next: a human opens it in the designer and saves it, §8.1 |
| A-FLOW-02 | No import existed | Import exists — next: invoke as a real trustee once live, unrelated to the designer step, §8.5 |
| A-FLOW-03 | No import existed | Import exists — next: one real run, then read run history as owner, §8.5 |
| A-FLOW-04 | No import existed | Import exists; connection reference confirmed `Active` and shared with working flows (§3) — next: the same designer-save step as A-FLOW-01, §8.2 |
| A-FLOW-05 (a) | No import existed | Import exists, fix confirmed live (§3) — next: force a failure once live and confirm a `status:"error"` body, §8.4 |
| A-LAND-2 | `pa app list-flows` found nothing | `pa app list-flows` finds the flow, `Inactive` (§3) — next: turn it on, then `pa app add flow`, §8.3 |
| A-LAND-3 | Flow emits `null` | Unchanged — needs OQ-039 (owner Emily) before any populated value can exist |
| A-LAND-4 | Flow emits `null` | Unchanged — needs a populated `breakTypeProfile` to compare against |

### 5. Constraint check

Evaluated once, before Stage 1, per `skills/how-to-apply-constraints.md` — pipeline-agent's HARD
scope in `constraints/technology/technology-constraints.md`:

```
CONSTRAINT CHECK
Tech     HARD: 19 / 19 in scope   |  violations: NONE
                                  |  unevaluable: NONE
Tech     SOFT: 2 in scope         |  warnings: NONE (C-TECH-033/C-TECH-044 unaffected — no Prd
                                     rollback or credential-rotation content this dispatch)
Overall: PASS
```

Not applicable this dispatch: `C-TECH-032`/`C-TECH-040` (DEV, not Prd/Test/Acc), `C-TECH-041` (no
tenant op), `C-TECH-050` (no new entity/role/option-set/field-security-profile in this solution
import — those were created via the Web API in earlier sessions, dev-summary §11), `C-TECH-073` (no
metadata `PUT`/`PATCH` performed this dispatch). All others PASS by the evidence in §2/§3 above:
`C-TECH-030` (exactly the build-agent artifact, checksums in the
[manifest](../../build/artifacts/revitalise-grant-automation-20260826-2/manifest.json)), `C-TECH-042`/
`C-TECH-053` (both imports re-run cleanly, level reported honestly as V3, never V4), `C-TECH-047` (no
hardcoded value introduced — the connection reference and connection id are read live, never
transcribed), `C-TECH-055` (0 new warnings — row 6 below), `C-TECH-056` (no new diagnostic component),
`C-TECH-057` (build-agent's own preflight, unaffected), `C-TECH-058` (§0, §4), `C-TECH-059` (findings
appended per §9; artifact directory resolved per run, not literal), `C-TECH-061`
(`verify-improvement-log.py --check` → OK, 5 unread non-blocker entries against the 10-entry
threshold, 0 unread blockers — 1 SOFT warning naming `IMP-0347`'s missing `reviewed_in` stamp, not
this dispatch's finding to fix), `C-TECH-062` (`verify-pipeline-config.py` re-run independently: PASS,
93 steps/3 environments), `C-TECH-064` (organisation/table auditing, the connection reference, the
environment-variable values and `rev_setting` are all confirmed live and unchanged or correct — §3),
`C-TECH-065` (row 3, §2).

### 6. Warnings triaged (`C-TECH-055`)

0 new. Both `pac solution import` runs and `pac code push` completed with no warning output.

### 7. Diagnostic components (`C-TECH-056`)

None created by this session.

### 8. REVIEWER ACTION REQUIRED — the human-only steps this dispatch could not perform

None of these is a harness refusal. Every mechanical step this session could attempt, it attempted
and verified by query (§2, §3). What is left needs a named human in an interactive, signed-in browser
session — the Power Automate designer and a real trustee sign-in — which this session has no route
to at all, not merely a restricted one.

1. **Open `REV | Portal | Round Statistics` in the Power Automate DESIGNER (never the Solutions
   list) and save it**, confirming no validation error. This is the only mechanism that registers a
   Power Apps trigger's invokability (dev-summary §9, pipeline.yml ~L783) and is A-FLOW-01's sole
   closing step.
   Verify afterwards with: `pac env fetch` on `workflow` filtering `workflowid eq
   8f1c2a44-1005-4b7a-9e21-0a1b2c3d4e05`, confirm `statecode=Activated`.
2. **While there:** confirm the Dataverse connection binds to the service account's own connection
   (`rev_SharedDataverse` → connection id `f31ddadfbe874e50a34054df668e75cf`, confirmed `Active` in
   §3) and set **"run only users" to the SERVICE CONNECTION**, never "provided by run-only user"
   (A-R33 — the control this feature's whole risk acceptance rests on). Turn the flow on.
3. **Once Activated,** from `src/code-apps/trustee-review-portal`: `pa app list-flows` (should now
   show it enabled, not `Inactive`), then `pa app add flow -f <flow-id>`, then `npm run build` to
   confirm the generated `RoundStatisticsService` compiles alongside the existing data sources
   (A-R34).
4. **Force a failure** once live (e.g. a temporarily invalid `$filter` on `List_the_open_round`),
   invoke as the code app, and confirm a `status:"error"` body returns — A-FLOW-05 claim (a)'s only
   closing evidence.
5. **Invoke as a real trustee** (or the process owner) once live, to close A-FLOW-02
   (`prvReadWorkflow` sufficiency) and A-FLOW-03 (`Secure Outputs` hides row data from run history —
   read the run's own history as owner).
6. **Confirm the tenant DLP policy** places the Power Apps trigger and the Dataverse connector in a
   combinable group (pipeline.yml's own still-open manual item, owner: tenant DLP administrator) —
   unverified by this dispatch; no scripted check exists for it in this repository.
7. **Not blocking, but still pending per pipeline.yml, unrelated to this deploy's own scope:** enter
   the first `rev_roundfinance` row for the open round (owner: process owner), seed the three FR-062
   threshold settings (blocked on OQ-039, owner Emily), extract the real Revitalise brand colours
   (owner: Revitalise brand owner).

### 9. What this deployment does NOT establish

- **V4 for any of the 8 rows overridden in §0.** Every one needs the designer-save/turn-on/live-
  invocation steps in §8, none of which this session can perform.
- **V5 — any FR-058–FR-063 figure travelling from Dataverse to the screen.** Structurally unreachable
  before §8.1–§8.3 land, exactly as Test Report v3 §7.2 states.
- **Promotion to TST/ACC/PRD.** Not attempted — blocked by design (`tst_acc.promote_mode: manual` +
  EX-003), not merely by instruction.

### Findings Logged

**0 entries appended.** None of the standing triggers fired: this was not a second attempt at
anything (both `pac solution import` runs were the deliberate idempotency proof, not a retry with
changed input), no document or config in this repository was contradicted by what was observed —
the connection reference, the D-10 fix, the flow's `Draft` state and the pre-existing `Daily Summary`
`Draft` state all matched what source and prior log entries already predicted — no deploy failure or
`HOLD` occurred, no human corrected this session's output, and no component the import reported as
created was missing under live query. `logs/known-failure-modes.md` is unchanged by this deploy.

Digest regenerated: N/A — no entries appended this addendum.

## Addendum — build #2 of 2026-08-30: `trustee-portal-visual-refresh`, reconciliation + Code App push, DEV only

**Feature Slug:** `trustee-portal-visual-refresh`
**Artifact:** `build/artifacts/trustee-portal-visual-refresh-20260830-2/`
**WBS:** `6.9`
**Date:** 2026-08-30
**Authorised by:** the reviewer's override instruction this dispatch, covering the 8 rows named in §0 below
**Level reached:** **V3 (DEV DEPLOYED)** for both the solution import and the Code App content. **V4 is
explicitly not reached** on any surface named in §0 or §3 below.
**Status:** SUCCESS. **Stopped at DEV — no promotion to TST/ACC/PRD** (`tst_acc.promote_mode: manual`,
unchanged).

### 0. The assumption-register override (`C-TECH-058`)

Recorded per the reviewer's instruction to this dispatch, on the record before the write below:
`OVERRIDE A-FLOW-03 A-FLOW-06 A-FLOW-11 A-FLOW-13 A-LAND-3 A-LAND-4 A-TR-13 A-FLOW-09` — reason:
**"deploy now, close at next live-run pass."** All eight rows stay `OPEN` in
[dev-summary §10](../development/trustee-portal-visual-refresh-dev-summary.md#L1903) after this deploy;
only the deploy gate they would otherwise block is waived. What each still needs, per that same
register:

| Row | What is assumed | Still needs |
|---|---|---|
| `A-FLOW-03` | `Secure Outputs` on a hand-authored flow hides row data from run history the way the designer checkbox does | [line 1903](../development/trustee-portal-visual-refresh-dev-summary.md#L1903) — one live run, read own run history as owner |
| `A-FLOW-06` | The `List rows` connector accepts a literal `"$expand"` key with the nested-object shape this flow's `List_applications_in_round` uses | [line 1912](../development/trustee-portal-visual-refresh-dev-summary.md#L1912) — designer save, then a real invocation |
| `A-FLOW-09` | `applicationsPerDay`'s denominator convention (whole elapsed days, floored at 1) is what FR-058 means | [line 1978](../development/trustee-portal-visual-refresh-dev-summary.md#L1978) — a business-definition question to the reviewer/Emily, not a platform fact; asked once, unanswered |
| `A-FLOW-11` | The Logic Apps `xml()`/`xpath(…, 'sum(/r/v)')` wrapper behaves as documented on this tenant, at every one of 21 `Compose_*_sum` actions | [line 2000](../development/trustee-portal-visual-refresh-dev-summary.md#L2000) — designer save, then a live run seeded with a zero-count, an all-blank, and a mixed break type |
| `A-FLOW-13` | `result()` on a `Switch`/`If` action's own name resolves to that branch's actions, undocumented by name in four Microsoft Learn pages read this project | [line 2037](../development/trustee-portal-visual-refresh-dev-summary.md#L2037) — designer save, then a live run that fails inside `Condition_page_cap` |
| `A-LAND-3` | FR-062's three headline proportions are each `{ population, count, percentage }` once populated | [line 1908](../development/trustee-portal-visual-refresh-dev-summary.md#L1908) — blocked on OQ-039 (owner Emily), unrelated to this deploy |
| `A-LAND-4` | FR-060's break-type total row mirrors a data row minus the category field | [line 1909](../development/trustee-portal-visual-refresh-dev-summary.md#L1909) — a populated `breakTypeProfile` to compare against |
| `A-TR-13` | `rev_careprovidedtype` arrives through this app's connector as a comma-separated string, not an array of numbers | [line 1911](../development/trustee-portal-visual-refresh-dev-summary.md#L1911) — read one populated row through the app and log the raw value's `typeof` |

### 1. What this dispatch found and reconciled — a dangling `WRITE BEGUN:` (`IMP-0484`'s own class)

A prior dispatch of this agent (agent `af313eb371957a432`) logged
[`WRITE_BEGUN — pac solution import … build 20260830-2`](../../logs/pipeline.log) at 21:01 and then ended
its turn stating it would "continue once the background import completes" — not possible, per
`agents/WORKFLOW.md` → *Session Boundaries*: a dispatched agent's turn ending is terminal, there is no
resumption. Per `agents/WORKFLOW.md` → *the fourth case*, rule 1, this was reconciled by live query, not
by trusting the prior claim or re-running the import:

- `importjobs` for `RevitaliseGrantAutomation`, most recent first, shows two completed jobs matching the
  standard import-then-reimport-for-idempotency pattern (`C-TECH-053`): `1cc5e9e1-4bfa-4e2d-8425-3fd3497c3dac`
  (created 18:52, completed 18:58, progress 100.0) then `aaa811d8-dcbc-493b-a72d-2e6eaafa0b1c` (created
  19:01, completed 19:03, progress 100.0). Both `SUCCEEDED`; no third re-run was needed.
- `callbackregistrations` for `rev_roundstatisticsrequest` is unchanged at `createdon`
  `2026-08-27T18:22:49Z` (`b184204a-44a2-f111-b8de-70a8a5079a1b`) — confirmed **independently**, not taken
  on the reviewer's own report of the same fact.

The reconciling `WRITE ATTEMPTED:` line is in `logs/pipeline.log` at 21:21.

### 2. A known-broken V4 surface, named per the amended `C-TECH-053` (`IMP-0485`/`IMP-0486`)

`REV | Portal | Round Statistics`'s own `modifiedon` is `2026-08-30T19:07:32Z` — **today**, after both
imports above, meaning a designer re-save was attempted. Despite that, its `callbackregistration`
`createdon` did **not** move from `2026-08-27T18:22:49Z`. Per `IMP-0104`/`IMP-0114`'s established
mechanism, a `callbackregistration` surviving unchanged across a designer save means the trigger's
webhook subscription is still pinned to a stale `logicappsversion` and Dataverse will deliver row-create
events into nothing — **no run, no error, empty run history.** This is stated here as a known-broken
surface, not glossed over: the round-statistics flow will not fire on a real trustee action until a
human re-registers the trigger (turn off, confirm the registration row disappears, turn on from the
designer — the same procedure this project has needed twice before).

### 3. Code App push — checked before pushing, not assumed from an earlier build's push

Commit [`2d34e9a`](../../docs/development/trustee-portal-visual-refresh-dev-summary.md) registered the
`rev_roundstatisticsresult` data source in the Code App
(`.power/schemas/appschemas/dataSourcesInfo.ts:1865`) and shipped the design-system conversion plus two
CSS fixes. Before assuming this build's push had already happened, the live `canvasapp` record
(`70869c95-92e5-442f-b5b9-44b3d3e549f6`) was queried directly:

- **Pre-push:** `databasereferences.dataSources` held only `applications`/`reviews`/`applicants`/
  `users`/`roundfinances`/`roundstatisticsrequests` — `roundstatisticsresults` **absent**.
  `appversion`/`lastpublishtime` both `2026-08-29T12:37:33Z` — yesterday. This build's Code App content
  had genuinely not reached DEV yet.
- **Write:** `pac code push --solutionName RevitaliseGrantAutomation` from
  `src/code-apps/trustee-review-portal`, `SUCCEEDED` first attempt, no refusal; re-run once more for
  idempotency (`C-TECH-053`), also clean.
- **Post-push, verified live by query, not inferred from the CLI's own success message:**
  `databasereferences.dataSources` and `cdsdependencies` both now list `rev_roundstatisticsresult`;
  `appversion`/`lastmodifiedtime`/`lastpublishtime` all `2026-08-30T19:11:38Z`/`39Z` — today, after this
  push.

**Level reached: V3** — accepted by target, idempotent, content independently confirmed live. **Not
verified: V4** — a named person opening the app and confirming it boots with the round-statistics screen
rendering as intended is the reviewer's next action.

### 4. Constraint check

```
CONSTRAINT CHECK
Tech HARD: in scope, this dispatch's slice — violations: NONE
Overall: PASS
```

`C-TECH-058` — §0 above. `C-TECH-053` — both writes re-run once for idempotency, both clean; level
reported honestly (V3, not V4) for both the solution import and the Code App content. `C-TECH-065` —
`verify-environment-access.ps1 -Env dev` run unconditionally before any write this dispatch performed:
`PASS` (`UserId 3a1a3937-e897-f111-b8dc-7ced8d43e87d`).

### 5. What this deployment does NOT establish

- **V4 for any of the 8 rows overridden in §0**, or for the round-statistics flow's trigger (§2) — every
  one needs a human, signed-in, interactive step this session has no route to.
- **That the round-statistics flow will fire at all** until the trigger is re-registered (§2).
- **Promotion to TST/ACC/PRD.** Not attempted — blocked by design (`tst_acc.promote_mode: manual`).

### Findings Logged

**0 entries appended by this dispatch.** The dangling-`WRITE_BEGUN` reconciliation in §1 is the same
class `IMP-0484` already recorded (a prior dispatch's own gap); this dispatch's job was to reconcile it,
not to re-log the class a second time for the same instance. No new second-attempt, no new
document/reality contradiction, no new deploy failure or `HOLD`, and no component the import or push
reported as created was found missing under live query.
