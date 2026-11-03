# REVRetentionSarExtract - REV | Retention | Retention & Erasure Helper (SAR extract), mode 3

Design: TAD rev 33 sections 4.2 and 5.12, ADR-088; delivery option B per TAD rev 37, ADR-091. Change order CO-011
(`wbs:0.13`). FR-053, FR-054.

## What it does

Started by the process owner from the Flow menu of an applicant, after the identity check. Reads the applicant,
identifies the starter (A-SAR-8, fail-safe as in mode 2), calls the locate child, then builds one HTML extract
store by store, each in its own scope with a "Not read, and why" line on failure: (1-6) the six Dataverse tables,
every column, reviews without the trustee-identity columns; (7) audit history of every located row (A-SAR-11);
(8) QuickBooks - the payment rows' own QuickBooks references, amounts and dates and a statement that the QuickBooks
copy was not read, because the read-only connection does not exist yet (`wbs:7.1`, A-SAR-10); (9) the service
mailbox, messages from and to the applicant's and referees' addresses (A-SAR-12); (10) the signed documents,
copied beside the extract from the library or, where none exists yet, from DocuSign (A-SAR-6, A-DS-9); (11)
statements for AI Builder records, Teams notifications and the website entry. Writes the file to the SAR folder
(`rev_SpoSarFolderUrl`, A-SAR-9), logs the run (SAR extract, the reference, the starter, `rev_detail` = file name and
stores read) and tells the process owner the reference and file name only. Then delivers (ADR-091 item 5, below):
the extract and every signed PDF copy in one encrypted email, or none, and adds which delivery happened to the log
row's `rev_detail`.

## Decisions worth knowing

* **Read-only, checkable from source:** no delete, no update, the only Dataverse write is the log row, files only
  to the SAR folder (unit-tested).
* **Delivery: option B, fail-closed to option A (TAD rev 37, ADR-091 item 5).** The send step is always built;
  the environment variable `rev_SarProtectedSender` turns it on per environment. After the log row and the ready
  message, `Compose_delivery_route` yields a fixed token: `send` only when the setting and the applicant's email on
  record are both non-empty after trimming **and the size check says `fits`**, else `off`, `no email` or `too
  large`. On `send`, `Send_the_extract_protected` (`SendEmailV2`, `rev_SharedOutlook`) sends the extract and every
  signed PDF copy, attached as one array (`@variables('attachments')`), with *From (Send as)* = the setting
  (A-SAR-13), *To* = the email on record, *Reply To* = `rev_ServiceMailbox`, *Sensitivity* left empty, retry policy
  **none**. A tenant mail-flow rule encrypts every message from that sender (A-SAR-4); the flow cannot see it, which
  is the residual `A-R112` the reviewer accepted. On any other route, or a failed or timed-out send: no email, no
  retry, no other sender, and a Teams message (reference and file name only) tells the process owner to use option
  A. `Record_the_delivery` then updates the log row's `rev_detail` from a fixed vocabulary (`Compose_delivery_outcome`).
  The setting ships empty and stays empty in an environment until the ADR-091 check (A-SAR-4, A-SAR-13, A-SAR-14)
  passes there, so every environment starts on option A. *Previously read: "A-SAR-4 is the build-time selector …
  this build has no send step".*
* **The sent copy (ADR-091 item 7, A-SAR-14).** The flow neither reads nor deletes any copy Exchange may keep of the
  sent message; it adds no mailbox action beyond the one send (unit-tested).
* **The signed PDFs travel with the extract, all or nothing (TAD rev 37 second amendment, ADR-091 item 5; reviewer
  2026-10-30, "Also attach the signed pdf's off course").** Every CreateFile is followed by two appends: `{Name,
  ContentBytes}` to `attachments` (secured; a PDF's `ContentBytes` is its get-content body's `$content`, the extract's
  is `base64()` of the file written, A-RH-3) and `{Name, Size}` to `attachmentFiles` (not secured: a reference and
  the create-file response's `Size`, A-SAR-15 (a), so the DEV check can read it in run history). After the ready
  message the extract joins both. `Measure_the_attachments` then adds every `Size` (`int(string(...))`, so a missing
  or non-numeric size fails the loop), reads the `SarEmailMaxAttachmentMB` setting (`int(trim(...))`, so a missing,
  empty or non-numeric value fails) and only when both succeed sets `attachmentCheck` to `fits: …` or `too large:
  …` (sizes rounded up to 0.1 MB, and the two arrays must have the same length). `attachmentCheck` starts as `not
  measured: …`, so every failure in the gate leaves the route at `too large`: no send action runs, no part of the set
  is emailed, there is no split and no extract-only email. The option A Teams messages list every file name
  (`Select_attachment_file_names`) and give the check's text; `rev_detail` records it. *Previously read: "Only the
  extract is attached … how they reach the requester under option B is not designed".*
* **Action count.** 101 (76 before rev 37, 84 after it); the second amendment adds 17 against the TAD's "about
  3": four variables (one per InitializeVariable, IMP-0821), two appends per file kind (library copy, envelope copy,
  extract), the gate scope with its loop, increment, setting read, limit and check, and the file-name Select. The
  delivery block adds 8 against the TAD's "about 5": a route token
  and an outcome token keep the email address out of the condition's and `rev_detail`'s expressions, and a failed
  `rev_detail` update raises Failure Alert as every other write here does.
* **QuickBooks** is a placeholder section by design, not a missing step: an action on an unbuilt connection
  reference would stop the whole flow from being turned on. The lookup by `rev_qboreference` is added with
  `wbs:7.1`.
* **No partial file is announced.** A failed file write or log write alerts and stops before the Teams message.
* **Trustee identities removed mechanically** from reviews: owner, created/modified by (and on-behalf-of), owning
  user/team/business unit and the two trustee lookups, with their annotations. The audit section leaves out who
  made each change for the same reason (TAD 4.2 item 7).

## Assumptions open in this definition

A-SAR-4, A-SAR-13 and A-RH-3 sit on `Send_the_extract_protected`; A-SAR-14 is stated there and in the ADR-091 check.
A-SAR-15 sits on the `Add_the_*_file` appends, `Add_the_file_size` and the attachments array; A-RH-3 also on the
`Add_the_*_attachment` appends.

Each is a row in `docs/development/retention-erasure-helper-dev-summary.md` section 10 and closes in the DEV
session named in `config/revitalise-grant-automation-pipeline.yml` (dev post_deploy, wbs:0.13). The marker sits in
the description of the action that makes the guess.

## Tests

`src/tests/solutions/retention_helper/test_retention_helper_flows.py` reads this definition as values and runs it
with the repository's WDL executor (`src/tests/narrative/wdl_sim.py`) over in-memory stores; wired into the HARD
`unit-tests` build step through `src/tests/solutions/RetentionHelper.Tests.ps1`. V2 at most: nothing ran on the
platform.
