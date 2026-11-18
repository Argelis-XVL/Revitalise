# REVRetentionSarExtract - REV | Retention | Retention & Erasure Helper (SAR extract), mode 3

Design: TAD rev 33 sections 4.2 and 5.12, ADR-088; delivery option B per TAD rev 37, ADR-091; rebuilt to TAD rev 38,
ADR-092 (2026-11-04): content only in actions that can be secured. Change order CO-011 (`wbs:0.13`). FR-053, FR-054.

## What it does

Started by the process owner from the Flow menu of an applicant, after the identity check. Reads the applicant,
identifies the starter (A-SAR-8, fail-safe as in mode 2), calls the locate child, then builds one HTML extract
store by store, each in its own scope ending in one secured section Compose, with a "Not read, and why" line
chosen at assembly when that Compose did not run: (1-6) the six Dataverse tables,
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

* **No variable carries content (ADR-092, TAD rev 38).** The designer refuses secureData on any variable action
  (`IMP-1267`), so the extract text and the attachment array no longer live in variables. Only `attachmentBytes` (a
  number) and `attachmentCheck` (a fixed text with sizes) remain. Each store's scope ends in
  `Compose_<store>_section` (secure inputs). `Compose_extract_document` (secure inputs) takes
  `coalesce(actions('Compose_<store>_section')?['outputs'], '<fixed Not read text>')` per store: a scope that failed
  never ran its section Compose, so `actions()` returns null outputs without an error and the fixed line is used
  (`A-SAR-16` (4), measured). Each store scope runs after the one before in any state.
* **Loops are flat and read back with `result()` (ADR-092 item 4).** The mailbox loop's children are the two reads,
  the Select, the Table and `Compose_mailbox_table`; the two document loops (library copies, then envelope copies,
  each over a list made beforehand by a secured Filter) are get, save and one Compose of `{Name, ContentBytes,
  Size}`. No If in any loop. After each loop a Filter (secure both ways) keeps the record of the loop's Compose from
  `result('<loop>')`, and a Select (secure both ways) projects each iteration's `outputs`. The shape is the one
  `A-SAR-16` measured in DEV on 2026-11-04: one record per first-level child, `outputs` an array of per-iteration
  records, and a Compose's per-iteration `outputs` is its plain value. **A Compose, not the Table, is the child read
  back**, although `ADR-092` item 4 names `Create_mailbox_table`: the probe measured the Compose record and not a
  Table's, so reading a Compose costs one action per loop and guesses nothing. **Every consumer of `result()` is
  secured itself:** the probe showed an unsecured Compose over `result()` printing the secured values in plain run
  history (`IMP-1269`). A test fails any flow in the solution that breaks this.
* **Signed-document lines come from the grant list, never from loop output.** `Select_signed_document_lines` writes one
  line per grant (library copy, envelope copy, or none); the section is used only when the whole scope succeeded, so
  "copied" is true. `Select_document_file_names` makes the PDF file names from the two grant lists before the loops,
  so the option A message can name them even when a copy fails.
* **A failed signed-document copy sends nothing and says why (ADR-092 item 7, reviewer Decision B).**
  `Compose_delivery_route` yields `copy failed` before any other token when `Copy_signed_documents` did not succeed;
  the option A message then says the documents could not all be copied and that the process owner copies them from
  the library and sends the extract and documents by hand; `rev_detail` records `delivery: option A, the
  signed-document copy failed and nothing was sent`. No new action: the existing option A message carries it.

* **Read-only, checkable from source:** no delete, no update, the only Dataverse write is the log row, files only
  to the SAR folder (unit-tested).
* **Delivery: option B, fail-closed to option A (TAD rev 37, ADR-091 item 5).** The send step is always built;
  the environment variable `rev_SarProtectedSender` turns it on per environment. After the log row and the ready
  message, `Compose_delivery_route` yields a fixed token: `send` only when the setting and the applicant's email on
  record are both non-empty after trimming **and the size check says `fits`**, else `off`, `no email` or `too
  large` (and `copy failed` first, above). On `send`, `Send_the_extract_protected` (`SendEmailV2`, `rev_SharedOutlook`)
  sends the extract and every signed PDF copy, attached as one array (`@outputs('Compose_the_attachments')`, ADR-092
  item 5), with *From (Send as)* = the setting
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
  2026-10-30, "Also attach the signed pdf's off course"; rebuilt by ADR-092 items 5 and 6).** Each PDF copy's loop
  records `{Name, ContentBytes, Size}` in a secured Compose (a PDF's `ContentBytes` is its get-content body's
  `$content`, A-RH-3; `Size` is that create-file response's, A-SAR-15 (a)); `Select_document_copies` gathers them.
  On the `send` route only, `Select_document_attachments` projects `{Name, ContentBytes}` and
  `Compose_the_attachments` (secure inputs) puts the extract first (`base64()` of the file written, A-RH-3). The
  size gate's `Select_attachment_sizes` projects `Size` only, from the copies and the extract's create-file
  response: the one action over content left unsecured on purpose (ADR-092 item 6), so each size is readable in run
  history; its inputs are hidden by the platform because they use a secured Select's outputs.
  `Measure_the_attachments` adds every `Size` (`int(string(...))`, so a missing or non-numeric size fails the loop),
  reads the `SarEmailMaxAttachmentMB` setting (`int(trim(...))`) and only when both succeed sets `attachmentCheck` to
  `fits: …` or `too large: …` (sizes rounded up to 0.1 MB). `attachmentCheck` starts as `not measured: …`, so every
  failure in the gate, a failed copy included, leaves the route short of `send`: no send action runs, no part of the
  set is emailed. If the attachments cannot be built on the `send` route, the send is skipped and the "send failed"
  message still goes. The option A Teams messages name the extract and every PDF file and give the reason;
  `rev_detail` records it. *Previously read: "Every CreateFile is followed by two appends … `{Name, ContentBytes}` to
  `attachments` … `{Name, Size}` to `attachmentFiles` … the two arrays must have the same length": variable actions,
  which cannot be secured (`IMP-1267`).*
* **Action count: 94** (ADR-092: about 92; 101 before it). Gone: 3 variables, 14 append actions, the nested If
  pair, the file-name Select. Added: one section Compose per store (5); in the mailbox loop one Compose, after it a
  Filter and a Select; for the documents two grant-list Filters, the file-name Select, a second loop, a Compose per
  loop, two Filters over `result()`, the copies Select and the lines Select; in the delivery block the attachments
  Select and Compose; the Size Select. Two over the TAD's estimate: the in-loop mailbox Compose (the measured shape,
  above) and `Select_document_file_names` (the option A message must name the files when a copy failed). *Previously
  read: "101 (76 before rev 37, 84 after it) …"*
* **QuickBooks** is a placeholder section by design, not a missing step: an action on an unbuilt connection
  reference would stop the whole flow from being turned on. The lookup by `rev_qboreference` is added with
  `wbs:7.1`.
* **No partial file is announced.** A failed file write or log write alerts and stops before the Teams message.
* **Trustee identities removed mechanically** from reviews: owner, created/modified by (and on-behalf-of), owning
  user/team/business unit and the two trustee lookups, with their annotations. The audit section leaves out who
  made each change for the same reason (TAD 4.2 item 7).

## Assumptions open in this definition

A-SAR-4, A-SAR-13, A-SAR-14 and A-RH-3 sit on `Send_the_extract_protected`. A-SAR-15 and A-RH-3 sit on the two
in-loop Composes (`Compose_signed_pdf_attachment`, `Compose_envelope_attachment`) and `Add_the_file_size`; A-RH-3
also on `Compose_the_attachments`. A-SAR-16 (`result()` and `actions()` shapes) is closed: verified by the reviewer's
DEV probe on 2026-11-04.

Each is a row in `docs/development/retention-erasure-helper-dev-summary.md` section 10 and closes in the DEV
session named in `config/revitalise-grant-automation-pipeline.yml` (dev post_deploy, wbs:0.13). The marker sits in
the description of the action that makes the guess.

## Tests

`src/tests/solutions/retention_helper/test_retention_helper_flows.py` reads this definition as values and runs it
with the repository's WDL executor (`src/tests/narrative/wdl_sim.py`, whose `result()` on a loop returns the shape
`A-SAR-16` measured) over in-memory stores, and checks every recorded input and output of a full run for content
under the platform's hiding rules. Two tests scan every flow in `Workflows/`: no variable action carries secureData,
and every consumer of `result()` over a loop with a secured child is secured itself. Wired into the HARD
`unit-tests` build step through `src/tests/solutions/RetentionHelper.Tests.ps1`, which also evaluates the Filters
and Selects after the loops in the PowerShell harness. V2 at most: nothing of this definition ran on the platform.
