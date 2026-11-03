# REVRetentionSweep - REV | Retention | Retention & Erasure Helper (sweep), mode 1

Design: TAD rev 34 section 5.12.1, ADR-089 items 2 to 4. Change order CO-011 (`wbs:0.13`, unbilled). FR-048 (evidence
of it), FR-049, FR-054, FR-055, NFR-010.

## What it does

Every Monday 00:30 UTC: (1) lists every application whose retention clock passes within 8 days, using the three
jobs' own rules and periods (`Compose_retention_periods`, keyed by the `jobKey` of `dataverse.bulkDeleteJobs`; a unit
test holds them equal); (2) for each one not already logged Scheduled or Overdue, calls the snapshot child (FR-055)
and then (3) writes one Scheduled row, plus an applicant row when no other application of that applicant remains
that is not itself due; (4) reconciles every Scheduled or Overdue row whose date has passed: record gone means
delete the signed PDF at the logged path and mark Deleted; still there 35 days after the date means Overdue; an
applicant kept because a new open application arrived is Not due; (5) on the first Monday of a month lists open
cases with no contact for `RetentionStaleCaseMonths` months (D4); (6) posts counts and references to the process
owner.

## Decisions worth knowing

* **No Dataverse delete.** The bulk-delete jobs (ADR-004, ADR-083) delete; this flow records and cleans up. Its only
  delete is the SharePoint file of a case already gone (unit-tested).
* **8 and 35 days are format constants** of the weekly schedule (`Compose_sweep_constants`), not settings
  (ADR-089 gate interactions). `RetentionStaleCaseMonths` is a setting; when missing or not a whole number, the
  summary says so and lists nothing (ADR-089 consequence 2: a stated blackout).
* **The applicant row's date** is the latest due date among that applicant's due applications, because the orphan
  job runs after the application sweeps.
* **"Not due" versus "Overdue"** for an applicant row: an applicant that now has an application in statuses 1 to 7
  stays because a new case arrived (Not due). A still-due application not yet deleted by a monthly job is not an
  "open" application, so it does not mask an overdue applicant.
* **Partial failure.** Each step has its own scope and its own Failure Alert; the next week picks up the rest. A
  run that fails after the snapshot and before the log row can write a second snapshot for that application next
  week: a snapshot carries no reference by design, so this cannot be checked (the same limit Finalise Decisions
  states as A-FD-7).
* **A-RH-2**: the pre-pass filters and expands through the lookups' navigation properties (`rev_applicationid/...`,
  `rev_applicantid/...`), the same names Round Statistics expands live.

## Assumptions open in this definition

Each is a row in `docs/development/retention-erasure-helper-dev-summary.md` section 10 and closes in the DEV
session named in `config/revitalise-grant-automation-pipeline.yml` (dev post_deploy, wbs:0.13). The marker sits in
the description of the action that makes the guess.

## Tests

`src/tests/solutions/retention_helper/test_retention_helper_flows.py` reads this definition as values and runs it
with the repository's WDL executor (`src/tests/narrative/wdl_sim.py`) over in-memory stores; wired into the HARD
`unit-tests` build step through `src/tests/solutions/RetentionHelper.Tests.ps1`. V2 at most: nothing ran on the
platform.
