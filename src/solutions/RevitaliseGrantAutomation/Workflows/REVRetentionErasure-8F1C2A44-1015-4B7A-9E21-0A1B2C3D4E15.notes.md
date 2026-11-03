# REVRetentionErasure - REV | Retention | Retention & Erasure Helper (erasure), mode 2

Design: TAD rev 34 section 5.12.2, ADR-089 items 5 to 8, decisions D2 and D3. Change order CO-011 (`wbs:0.13`).
FR-051, FR-052, FR-054, FR-055.

## What it does, in order

1. **Confirmation (A-ERA-1).** Exactly one applicant selected, and the typed reference equals its reference
   (trimmed, case-insensitive). Anything else terminates "ReferenceMismatch" before any read. The row read back
   from Dataverse is checked against the typed value a second time.
2. **Who started it (A-SAR-8).** The caller's address from the trigger header, resolved to a staff user. If it
   cannot be identified the run stops before the case is read: the log must name the starter.
3. **Locate** (child flow, shared with mode 3).
4. **Hold rule D2.** Any grant with no `rev_finalpaymentdate` stops the run: one row Retained (hold), the
   requester emailed (fixed wording), the process owner told the grant references, terminate Succeeded. Nothing is
   deleted. A case with no grant is unaffected.
5. **Snapshots and Scheduled rows first**, so a run that stops half-way leaves evidence: one per application
   (after its snapshot), the applicant, each signed PDF (with its path), the mailbox messages.
6. **Deletes** in one scope: each signed PDF (metadata by path, then Delete file; a 404 is "already gone",
   A-ERA-3), each service-mailbox message to or from the applicant and each referee message whose subject carries
   that application's reference (A-ERA-4, A-SAR-12; a 404 on delete is "already gone"), then ONE Dataverse delete
   of the applicant row; the parental cascades remove the rest (A-ERA-2).
7. **Outcomes.** Every Scheduled erasure row of the case (this run's and any a stopped run left) set to Deleted;
   one QuickBooks row per paid grant, Retained (finance), until final payment + 72 months (ADR-088 item 6); one
   Audit history row (D3 option a).
8. **Requester email** (FR-052) from the service mailbox, references and computed dates only; **DPO email** to the
   `ErasureNotificationEmail` setting when it holds an address; **Teams** to the process owner with the
   references, whether each email went, and any DocuSign envelope still in progress to void by hand.

## Decisions worth knowing

* **Audit history row outcome: Retained (audit) (8).** TAD 5.12.2 step 8, as amended at the rev 37 approval
  (reviewer, 2026-10-30, verbatim *"Build Retained (audit)"*): outcome 8, `rev_retaineduntil` = the erasure date
  (`Compose_erasure_date`) + 6 years (decision D3). *Previously built: Not due (3), a judgement the TAD left open;
  Not due keeps its mode 1 meaning.*
* **The literal "@" in a condition is written "@@".** A plain "@" is parsed as an (empty) expression; the
  simulator caught it before any import.
* **The only Dataverse delete in the helper** is `Delete_the_applicant_row` (unit-tested), on rows the service
  identity can delete only because of the privileges added for this mode (REV Service Automation.xml).

## Assumptions open in this definition

Each is a row in `docs/development/retention-erasure-helper-dev-summary.md` section 10 and closes in the DEV
session named in `config/revitalise-grant-automation-pipeline.yml` (dev post_deploy, wbs:0.13). The marker sits in
the description of the action that makes the guess.

## Tests

`src/tests/solutions/retention_helper/test_retention_helper_flows.py` reads this definition as values and runs it
with the repository's WDL executor (`src/tests/narrative/wdl_sim.py`) over in-memory stores; wired into the HARD
`unit-tests` build step through `src/tests/solutions/RetentionHelper.Tests.ps1`. V2 at most: nothing ran on the
platform.
