# Deployment Summary — Narrative Scrubbing (DEV), build 20261020-1

**Feature Slug:** revitalise-narrative-scrubbing (pipeline config: revitalise-grant-automation)
**Artifact:** build/artifacts/revitalise-narrative-scrubbing-20261020-1/ (unscoped; supersedes 20261019-1)
**Date:** 2026-10-20
**WBS:** 5.3, 5.4, 5.6, 5.7 (the scrub work). The other-workstream content below carries no WBS id from this dispatch.
**Target:** DEV only. No promotion attempted. Items carried: none (manifest `items` is empty).
**Reviewer instruction:** "Deploy as is", 2026-10-20.

## What this artifact carries beyond the narrative-scrubbing fix

The reviewer was told, and accepted, that this pack also holds uncommitted work from another workstream:

- **New flow `REV | Portal | Finalise Decisions` (`8f1c2a44-1012-...`).** First time it exists in DEV.
- **`REV | Scoring | Calculate & Flag` (1002)**: rev 26 / ADR-079 changes.
- **`REV | Acceptance | Create Envelope` (1006)**: changes.
- **`REV | Narrative | Scrub Free-Text` (1011)**: the IMP-1156 fix (Compose_raw_classes `secureData` on inputs only), which is why this build replaces 20261019-1.

The retired RedactionAutoRelease stage and was not created. No `RedactionAutoRelease` setting row exists.

## Environment Results

| Environment | Deployed At | Status | Live version | Notes |
|---|---|---|---|---|
| Dev (REV-GrantApplications-DEV) | 2026-10-20 12:43-12:52 UTC | PARTIAL, level DEPLOYED (V3) | unmanaged import | Import and idempotent re-run clean. Nothing is V4. Three flows are Draft |
| Test/Acc | not queried | NOT QUERIED | not queried | Only the DEV pac profile was used |
| Prd | not queried | NOT QUERIED | not queried | |

Production guard: `verify-improvement-log.py --check --target-env dev` exit 0 (0 deploy-lane blockers, 0 governance, 4 fixed-in-flight). Not applicable to PRD, not reached.

## Flow state after import (Dataverse fetch, `category = 5`)

| Flow | Before | After | Reviewer must |
|---|---|---|---|
| REV \| Narrative \| Scrub Free-Text (1011) | Draft | **Draft** | Open in the DEV designer, save, turn on |
| REV \| Portal \| Finalise Decisions (1012) | absent | **Draft (new)** | Open in the designer, save, turn on; share run-only with the process owner; V4 with test identities only |
| REV \| Intake \| WordPress to Dataverse (1001) | Draft | Draft | Unchanged by this deploy; its own turn-on decision |
| REV \| Local Authority Register \| Watch (1010) | Draft | Draft | Unchanged; the register feature is paused |
| Scoring Calculate & Flag (1002), Daily Summary (1003), Ops Failure Alert (1004), Portal Round Statistics (1005), Acceptance Create Envelope (1006), Reminders & Escalation (1007), Completion (1008), Safeguarding Action Completion (1009) | Activated | Activated (modifiedon 12:51 UTC) | See callback note below for 1002 and 1006 |

## Tenant-Level Operations
None. No `APPROVE TENANT` operation in this dispatch.

## Environment Prerequisites
Not this environment's first deploy. Not run, no PROVISION credential in the session (`PROVISION_APP_ID`, `PROVISION_CERT_THUMBPRINT` absent): access preflight, `ensure-schema.ps1`, `reconcile-flow-statecodes.ps1`, `seed-settings.ps1`, intake-callback-url Capture. Owner: reviewer. Whether this diff touches schema-shaping source (new column, relationship, field permission) was NOT assessed by this dispatch; if it does, `ensure-schema.ps1` is owed before the build is relied on. The seed was not re-checked in this dispatch; the 13:35 dispatch of build 20261020-2 recorded all 15 rows 1002 reads present in DEV.

## Post-Deployment Configuration

| Step | Result |
|---|---|
| Solution import (`--force-overwrite --publish-changes --activate-plugins`), started 12:43 UTC | SUCCEEDED |
| Idempotent re-run, same zip and flags | SUCCEEDED |
| code-app-push, trustee-review-portal (70869c95) | SUCCEEDED, appversion 2026-10-20T12:52:14Z; `dist/` byte-identical to the artifact's `code-app/` |
| code-app-push, trustee-review-portal-cards (b0483396) | SUCCEEDED, appversion 2026-10-20T12:52:20Z; `dist/` byte-identical to the artifact's `code-app-cards/` |
| flow-definition-reread | PASS, 12 live / 12 expected, none modified after the import. Compared with the ARTIFACT's 12 workflow JSON files: all 12 are byte-identical to the working-tree source, so a pass against source is a pass against the artifact (IMP-1155) |
| intake-callback-url Capture / Compare | NOT RUN, needs PROVISION cert, owner reviewer. callbackregistrations are unchanged (5 rows, same ids and createdon as before this import) |
| Manual entries (group-team bindings, sharing, DocuSign, SharePoint, privilege revoke, etc.) | Outstanding, owner reviewer; unchanged by this dispatch |

## Evidence

- **Components.** 12 flows live matching 12 in source; 1012 now exists. Code apps both republished 12:52 UTC. Not re-derived this dispatch: the full RootComponents query (option sets, roles, entities) done for 20261019-1 and 20261020-2; the root-component list in this pack is the same solution. Reported as not re-run, not as passed.
- **rev_setting.** Five Redaction rows present, none modified by the deploy. No RedactionAutoRelease row.
- **Callback registrations (5):** rev_application x3 (8/20, 10/9 10:55, 10/9 14:40), rev_roundstatisticsrequest (9/22), rev_grant (10/3). **None was recreated by this import**, and 1002 (rev_application) and 1006 (rev_grant) were both replaced at 12:51 UTC. A registration older than its flow's modifiedon can deliver into nothing (IMP-0114). Only a real new row proves 1002 and 1006 fire. Finalise Decisions has no registration; it is a manual flow.
- **Human open-and-save (V4):** OUTSTANDING for every flow and both apps. Level is DEPLOYED (V3).

## Assumption register
Dev Summary section 10 rows for the scrub flow (A-NS-1, 2, 3, 5, 8, 9, 12, 13, 15, 16, 18, 19, 40) and the Finalise Decisions rows (A-FD-*) remain OPEN. They need the flows turned on in DEV; none was closeable in this deploy because the flows are Draft. This is the deploy that makes them closeable. No OVERRIDE was needed.

## Reviewer action outstanding

1. Open `REV | Narrative | Scrub Free-Text` in the DEV designer, save, turn on. This is the check IMP-1095, IMP-1098 and IMP-1156 wait on. Report whether the save succeeds.
2. Open `REV | Portal | Finalise Decisions` in the designer, save, turn on; share run-only with the process owner; test with TEST identities only, before any real board round.
3. Open and save `REV | Scoring | Calculate & Flag` and `REV | Acceptance | Create Envelope`, or create one real test row for each (an application; a grant) and confirm they fire.
4. Optional: PROVISION-credentialed steps listed above, including the intake callback Capture/Compare.

Log note: the idempotency re-run's `WRITE BEGUN:` line was swallowed into the preceding `WRITE ATTEMPTED:` line by a two-line `log-line.py` heredoc (the tool writes one line per call). The re-run did happen and succeeded.

---

# Earlier deployment, build 20261019-1 (superseded by the above; kept as record)

# Deployment Summary — Narrative Scrubbing (DEV), build 20261019-1

**Feature Slug:** revitalise-narrative-scrubbing (pipeline config: revitalise-grant-automation)
**Artifact:** build/artifacts/revitalise-narrative-scrubbing-20261019-1/ (unscoped, V2 at pack)
**Date:** 2026-10-20
**WBS:** 5.3, 5.4, 5.6, 5.7
**Target:** DEV only. No promotion attempted.

## Environment Results

| Environment | Deployed At | Status | Live version | Notes |
|---|---|---|---|---|
| Dev (REV-GrantApplications-DEV) | 2026-10-20 ~07:29 UTC | PARTIAL, level DEPLOYED (V3) | unmanaged import | Import and idempotent re-run clean; flow REV Narrative Scrub Free-Text is Draft, not on |
| Test/Acc | not queried | NOT QUERIED | not queried | Only the DEV pac profile was used |
| Prd | not queried | NOT QUERIED | not queried | |

Production guard: `verify-improvement-log.py --check --target-env dev` exit 0 (3 fixed-in-flight, 0 deploy-lane blockers open). Not applicable to PRD, not reached.

## Tenant-Level Operations
None.

## Environment Prerequisites
N/A: not this environment's first deploy. The access preflight (`verify-environment-access.ps1`), `ensure-schema.ps1`, `reconcile-flow-statecodes.ps1`, `seed-settings.ps1` and the intake callback capture were NOT RUN: this session holds no PROVISION_APP_ID / PROVISION_CERT_THUMBPRINT. Owner: reviewer. No schema-shaping source in scope. The seed is create-only and the DEV RedactionNameRules row already holds the A-11 value, so skipping it loses nothing.

## Post-Deployment Configuration

| Step | Result |
|---|---|
| Solution import (async 291b6c0c-57cc-f111-a05c-7ced8d43e1b4, 1m42s) | SUCCEEDED |
| Idempotent re-run (async df0ce1ee-57cc-f111-a05c-7ced8d43e87d, 45s) | SUCCEEDED |
| code-app-push, trustee-review-portal (70869c95) | SUCCEEDED, appversion 2026-10-20T07:37:42Z (was 2026-10-07T17:44:23Z) |
| code-app-push, trustee-review-portal-cards (b0483396) | SUCCEEDED, appversion 2026-10-20T07:37:54Z (was 2026-10-07T17:44:35Z) |
| flow-definition-reread | Live 11/11 equals the artifact's flow json. Against src: 1 DIFFERS (1002 Scoring, source edited after the pack, not in this artifact; IMP-1155) |
| intake-callback-url Capture/Compare | NOT RUN, needs PROVISION cert, owner reviewer. Indirect evidence: callbackregistrations identical before and after (5 rows, same ids and createdon) |
| Manual entries (SharePoint library, group-team bindings, sharing, field-security membership, privilege revoke) | Outstanding, owner reviewer; unchanged by this dispatch |

## Evidence

- **Flow statecodes before and after (Dataverse fetch).** Before: Scrub Free-Text (1011) Activated, 1001 Draft, 1010 Draft, all others Activated. After: **1011 Draft**, 1001 Draft, 1010 Draft, all others Activated. 1011 was turned off by the import of its changed definition.
- **Scrub Free-Text definition.** Live equals source for 1011 (no DIFFERS). The 1011 source was last edited before the pack.
- **rev_setting.** Five Redaction rows before and after, none modified by the deploy (RedactionNameRules modifiedon 10/19 2:49 PM kept). No RedactionAutoRelease row exists. No rev_redactionreleased write.
- **Prompts.** REV Narrative Redaction Prompt (122be8e0, same id), Spelling Prompt (763cff31) and Rewrite Prompt (e853d7c8) all present, modifiedon 10/20 7:27.
- **Components by query, derived from Solution.xml RootComponents.** Workflows 11/11, option sets 34/34, environment variable definitions 9/9, roles 4/4, AI projects 3/3, canvas apps 2/2, field security profiles 2/2, site map 1/1. Entities: 16 live against 15 root entries, the extra one is a platform-added table, not a missing one. The narrative form tab `tab_narrativescrubbing` is present in a live Application form. Saved views and the Review Required view were not individually confirmed by id (two fetch attempts failed on query syntax).
- **Option-set members, human open-and-save (V4):** not run. OUTSTANDING.

## Assumption register
A-NS-40 (first/last/indexOf on strings) is OPEN. It cannot be closed before this flow version exists in DEV; it closes by TD-13 after the flow is on. No other OPEN rows in iteration 12.

## Reviewer action outstanding

1. Open REV | Narrative | Scrub Free-Text in the DEV designer, save, and turn it on. It is Draft now. Opening and saving it also discharges the V4 step that IMP-1095 and IMP-1098 wait on.
2. After it is on, re-run TD-13 to close A-NS-40.
3. Optional: the PROVISION-credentialed steps listed under Environment Prerequisites.
