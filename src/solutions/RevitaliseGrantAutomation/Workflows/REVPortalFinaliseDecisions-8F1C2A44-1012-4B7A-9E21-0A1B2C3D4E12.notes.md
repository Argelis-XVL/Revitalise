# REVPortalFinaliseDecisions-8F1C2A44-1012-4B7A-9E21-0A1B2C3D4E12.json - notes

`REV | Portal | Finalise Decisions`, flow #7 (Automation #6, wbs:6.6, WI-0129, TAD 5.7 and 5.13 rev 27, ADR-080; FR-037, FR-040, FR-047, FR-055).
Power Automate holds every `description` to 256 characters, so what does not fit there is here. Source-only: nothing here has run (V1).

## Where it starts and what one run is

Emily opens `REV Grant Administration`, Reviews, Awaiting Finalisation, selects reviews and chooses Flow, `REV | Portal | Finalise Decisions`. The trigger is Dataverse *When a row is selected* on `rev_review`: the platform starts **one run per selected row** (Split on cannot be turned off) and a run touches only its own review. Selecting more than 40 rows may fail to start. The flow takes only the review id from the trigger and reads the row again itself.

Rev 1 of this flow was a button acting on every unfinalised review. The reviewer's correction replaced it (ADR-080). The per-review loop, the up-front list, the counters and the per-review failure capture are gone.

## The trigger's shape and the row read (A-FD-10, closed)

Copied exactly from a DEV export of the reviewer's working scratch flow, kept as `src/tests/fixtures/dev-export/record-selected-trigger.json` and compared by `FinaliseDecisions.Tests.ps1`: `type` Request, `kind` ApiConnection, `operationId` RecordSelected, `parameters.entityName` `rev_reviews`, `splitOn` `@triggerBody()['rows']`, a `host.connection.name` expression that reads `$connections`, a definition parameter `dynamicscrmonline.entityName`, and a row schema that declares `rev_name` and `rev_reviewid` (`title` Review, `type` string, `format` guid).

**The row schema matters.** The designer stores, under `rows.items.entity.properties`, only the columns an action references. The first scratch flow referenced none, so flow #7 built from it received `{"entity":{"entity":{}}}` from the Flow menu (reviewer, DEV, 2026-10-20). The reviewer's working flow delivered `{"entity":{"@odata.etag":…,"rev_reviewid":"c11014a4-…","rev_name":"REV-R-01004"}}`, and its export shows `rev_reviewid` stored. A test fails if a column the flow reads from the trigger is not declared.

**The review is read first.** The reviewer's pattern: a *Get a row by ID* straight after the trigger, so everything later works from the full row and not from trigger fields. In the export it is `GetItem`, `entityName` `rev_reviews`, `recordId` `@triggerBody()?['entity']['rev_reviewid']`. `Get_the_review` does the same (with this solution's `authentication` and retry, and a `$select`), and is the first action that touches data. The only trigger field read anywhere is the id. A read that fails, because no id arrived or no such review exists, raises the alert and stops the run Failed (`Alert_review_not_read`, `Stop_review_not_read`), outside the try-scope so nothing else has started; the apply scope waits for the read.

**The top level is one chain** (reviewer, DEV designer, 2026-10-21: "the designer looks not right"). Build -8 started the read in parallel with the variable, and the alert and the apply scope each waited on both the read and the run link, so the designer drew two branches from the trigger and crossing lines. Now: trigger, `Initialise_failure_detail`, `Compose_run_link`, `Get_the_review`; the read's success goes to `Finalise_this_review`, its failure or timeout to `Alert_review_not_read` then `Stop_review_not_read`. Each action waits on exactly one predecessor; the alert still reads the run link, which is earlier in the same chain. The variable and the run link touch no data, so the read is still the first thing that does. No Scope wraps the read: it would add a box and still fork success from failure, the same way `Finalise_this_review` already forks to its own failure branch below. Tests fail if a second action starts from the trigger or any top-level action waits on two.

Not yet proven (A-FD-4): that `GetItem` returns the row's columns directly under `body` and accepts `$select` by that name. Neither is in the export.

## One run, in order

1. The review was read by id straight after the trigger. `Compose_outcome` is 0 if `rev_finalisedon` is set (nothing changes, the per-review double-run guard).
2. Undecided (no `rev_outcome` and fewer than two verdicts): 0, nothing changes, the review stays on the view with its empty verdict visible.
3. A staff-set `rev_outcome` wins. Otherwise the two verdicts decide only when they agree: Approve+Approve is 1 Approved, Defer+Defer is 2 Deferred, Reject+Reject is 3 Rejected (the verdict and outcome option values line up, a test asserts it). **A split is 0: not finalised.** The reviewer: "The splits will get dicussed in the quarterly panel with the trustees." Emily records the panel's decision in `rev_outcome` on the review form and presses it again. Outcome 4 (Non-Qualifying) is left open.
4. Outcomes 1 to 3 only: read the application and applicant, and look for an existing Grant. Approved with no Grant yet creates one (status 1, amount = amount requested, Q-FD-8 confirmed; dates = preferred break dates; provider empty). Approved sets the application to 7. Rejected sets it to 8 and stamps `rev_decisiondate`.
5. Approved and Rejected write one snapshot row (Granted, Not Granted). **Deferred writes none** (Q-FD-3: deferred means not granted and could be granted in future; each application is counted once, at its final outcome, and the retention safety net in 5.13 item 3 covers one never decided again).
6. Stamp `rev_outcome` and `rev_finalisedon` **last**. A run that fails before this leaves the review on the view for another try.

## The hand-off to flow #8

Creating the Grant row is the only hand-off. Flow #8 triggers on a `rev_grant` row being created (A-DS-3), so each approved review starts its own envelope run. This flow has no DocuSign action and no signing order (ADR-077, reviewer 2026-10-19). FR-047 is met as one action by Emily, not as a single run: fifteen selected reviews are fifteen runs of this flow and fifteen envelope runs (A-FD-5, TAD A-R76).

## The snapshot (A-FD-4, A-FD-7)

Outcome, amount (only when granted), age range and location area from the applicant, condition areas, decision month, snapshot date. No lookup, no reference; `rev_name` is `Decision yyyy-MM`. Condition areas map `rev_conditionprofile` 1 to 10 onto the six areas of `rev_conditionareas` (1,2 Sensory; 3,4 Mobility and Dexterity; 5,6 Learning and Cognitive; 7 Mental Health; 8 Long-Term Health Condition; 9 Social or Behavioural; 10 Other), a grouping that file calls an unconfirmed placeholder. The application read is secured both ways because it reads the profile. A retry after a failure between the snapshot and the stamp would repeat a snapshot row; it has no key, by design.

## What Emily sees, and who can run it (A-FD-9, A-FD-11)

The platform tells her only that the flow started; a run-only user cannot open run history. She reads the result on screen: a finalised review leaves Awaiting Finalisation and an approved one has a Grant in Grants. A failure raises `REV | Ops | Failure Alert` with the review id and the step, never a value. `Compose_run_summary` says in words what the run did, for run history.

The flow is shared **run-only** with that environment's process-owner group, as TAD §12.8 names it from the deployment settings files (the names do not follow one pattern): DEV `REV-PP-GrantApplications-DEV`, TST/ACC `REV-PP-GrantApplications-Admins-ACC`, PRD `REV-PP-GrantApplications-Admins-PRD`. It is shared on the flow's own Dataverse connection (*Use this connection*), never *Provided by run-only user*. That share is per-environment state, not solution content, and does not travel with an import (pipeline config, `post_deploy`). It is the control relied on: Finance can open the same app. Trustees cannot open the app (reviewer, DEV, 2026-10-20), a second layer for them only. Whether a user licensed only for the app may run it is A-FD-11.
