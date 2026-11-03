# REVRetentionLocate - REV | Retention | Retention & Erasure Helper (locate), child flow

Design: TAD 5.12 (locate step, shared by modes 2 and 3), ADR-088 item 1. Change order CO-011 (`wbs:0.13`).

Given an applicant id, returns `{found, applicant, applications, reviews, grants, payments, bankaccounts}`: every
column of every row (no `$select`, so a column added later is gathered without a change here). Reviews and grants
by the applications' ids, payments by the grants' ids, bank accounts by the applicant and by every bank account a
payment names. An empty list uses the zero GUID so a read returns nothing rather than failing on an empty filter.
Read-only (unit-tested). On a failed read it alerts and answers 500, so the caller's child-flow action fails and
the caller stops instead of working from an empty case (A-RH-1). Every read and the response are secured.

## Assumptions open in this definition

Each is a row in `docs/development/retention-erasure-helper-dev-summary.md` section 10 and closes in the DEV
session named in `config/revitalise-grant-automation-pipeline.yml` (dev post_deploy, wbs:0.13). The marker sits in
the description of the action that makes the guess.

## Tests

`src/tests/solutions/retention_helper/test_retention_helper_flows.py` reads this definition as values and runs it
with the repository's WDL executor (`src/tests/narrative/wdl_sim.py`) over in-memory stores; wired into the HARD
`unit-tests` build step through `src/tests/solutions/RetentionHelper.Tests.ps1`. V2 at most: nothing ran on the
platform.
