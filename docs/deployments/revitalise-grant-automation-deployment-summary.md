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
