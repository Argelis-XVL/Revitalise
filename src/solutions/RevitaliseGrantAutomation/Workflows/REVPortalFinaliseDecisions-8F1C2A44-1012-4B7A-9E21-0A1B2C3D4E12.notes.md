# REVPortalFinaliseDecisions-8F1C2A44-1012-4B7A-9E21-0A1B2C3D4E12.json - notes

`REV | Portal | Finalise Decisions`, flow #7 (Automation #6, wbs:6.6, WI-0129, TAD 5.7 and 5.13 rev 27, ADR-080; FR-037, FR-040, FR-047, FR-055).
Power Automate holds every `description` to 256 characters, so what does not fit there is here. Source-only: nothing here has run (V1).

## Where it starts and what one run is

Emily opens `REV Grant Administration`, Reviews, Awaiting Finalisation, selects reviews and chooses Flow, `REV | Portal | Finalise Decisions`. The trigger is Dataverse *When a row is selected* on `rev_review`: the platform starts **one run per selected row** (Split on cannot be turned off) and a run touches only its own review. Selecting more than 40 rows may fail to start. The flow takes only the review id from the trigger and reads the row again itself.

Rev 1 of this flow was a button acting on every unfinalised review. The reviewer's correction replaced it (ADR-080). The per-review loop, the up-front list, the counters and the per-review failure capture are gone.

## The trigger's shape (A-FD-10)

Copied from a DEV export, not from memory: `pac env fetch` of `workflow.clientdata` for the reviewer's scratch flow "Run a flow for selected rows", 2026-10-20, kept as `src/tests/fixtures/dev-export/record-selected-trigger.json` and compared by `FinaliseDecisions.Tests.ps1`. It is `type` Request, `kind` ApiConnection, `inputs.operationId` RecordSelected, `parameters.entityName` rev_reviews, a `schema` with `rows`, `splitOn` `@triggerBody()['rows']`, and a `host.connection.name` expression that reads `$connections`. The export also declares a definition parameter `dynamicscrmonline.entityName`, kept.

**Not measured by that export:** (1) where the selected row's id sits in `triggerOutputs()`. The scratch flow only holds a Compose of a constant and has never run (no `flowrun` row). `Compose_review_id` tries `body/entity/rev_reviewid` then `body/rev_reviewid`, and `Check_the_review_id_arrived` stops the run Failed with an alert if neither delivers, so a wrong guess fails loudly. (2) Whether the trigger in this form imports against the solution's `rev_SharedDataverse` connection reference (the export's own binding is a user connection id, dropped here) and turns on. The actions keep this solution's `connectionName`/`apiId`/`authentication` form, which DEV has accepted.

## One run, in order

1. Read the review by id. `Compose_outcome` is 0 if `rev_finalisedon` is set (nothing changes, the per-review double-run guard).
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

The flow is shared **run-only** with the Entra group `REV-PP-GrantApplications-Admins-<env>`, on the flow's own Dataverse connection (*Use this connection*), never *Provided by run-only user*. That share is per-environment state, not solution content, and does not travel with an import (pipeline config, `post_deploy`). It is the control relied on: Finance can open the same app. Trustees cannot open the app (reviewer, DEV, 2026-10-20), a second layer for them only. Whether a user licensed only for the app may run it is A-FD-11.
