# REVRetentionSnapshot - REV | Retention | Retention & Erasure Helper (snapshot), child flow

Design: TAD rev 34 section 5.12.4, ADR-089 item 1, section 5.13 step 3. Change order CO-011 (`wbs:0.13`). FR-055.

Given an application id: if its latest review outcome is Deferred (2) and its status is not Approved (7), Rejected
(8) or Grant Paid (11), writes ONE Not Granted (2) `rev_anonymisedstatistic` with the same fields Finalise Decisions
writes (age range, location area, the coarse condition areas, the decision month of the deferring panel, the
snapshot date; no amount, no lookup, no reference). Otherwise writes nothing. Answers `{written}`. **What it cannot
do, stated by the TAD:** check that a decided application already has its snapshot, because a snapshot carries no
reference by design; Finalise Decisions writes that one in the run that decides. On failure it alerts and answers
500 (A-RH-1) so the caller stops before logging or deleting that application.

## Assumptions open in this definition

Each is a row in `docs/development/retention-erasure-helper-dev-summary.md` section 10 and closes in the DEV
session named in `config/revitalise-grant-automation-pipeline.yml` (dev post_deploy, wbs:0.13). The marker sits in
the description of the action that makes the guess.

## Tests

`src/tests/solutions/retention_helper/test_retention_helper_flows.py` reads this definition as values and runs it
with the repository's WDL executor (`src/tests/narrative/wdl_sim.py`) over in-memory stores; wired into the HARD
`unit-tests` build step through `src/tests/solutions/RetentionHelper.Tests.ps1`. V2 at most: nothing ran on the
platform.
