# Dev Summary Document — Retention & Erasure Helper (modes 1, 2 and 3)

**Feature Slug:** retention-erasure-helper (a part of `revitalise-grant-automation`; builds into the same solution and
build configuration)
**TAD Reference:** `docs/architecture/revitalise-grant-automation-architecture.md` rev 33/34, and rev 36/37 approved
2026-10-30 with the approval amendment: §4.2 (item 8), §5.12, §5.12.1, §5.12.2 (step 8), §5.12.3, §5.12.4, `ADR-088`,
`ADR-089`, `ADR-091` (item 5 as amended twice at approval), §12 (rev 33, rev 34 and rev 37 rows), §12.11 (`A-SAR-4`,
`A-SAR-13`, `A-SAR-14`, `A-SAR-15`), §12.12
**SDD Reference:** `docs/plans/revitalise-grant-automation-plan.md` (FR-048 to FR-055, §10)
**Change order:** [CO-011](../../contract/change-orders/CO-011.md), approved **unbilled** (`EX-013`)
**WBS task id:** `wbs:0.13` (exists in `contract/change-orders/` only); the QuickBooks step depends on `wbs:7.1`
**Date:** 2026-10-26; revised 2026-10-30 (reviewer decisions 1 and 3, §13); revised again 2026-10-30 (TAD rev 36/37, §14);
revised a third time 2026-10-30 (TAD rev 37 second amendment: signed PDFs attached, size gate, §15)
**Status:** DRAFT
**Branch:** `retention-automation`

---

## 1. Implementation Summary

The whole `REV | Retention | Retention & Erasure Helper` is built in solution source as five cloud flow definitions,
one new table, four global choices, new role privileges, two settings keys, one environment variable, pipeline steps
and the process owner's runbook. Nothing has run on the platform: the definitions are read as values and executed by
the repository's workflow-language simulator against in-memory stores (V2), and the unmanaged solution packs (V2).

1. **Mode 1, the weekly sweep**, records every deletion the bulk-delete jobs make. Each Monday at 00:30 UTC it lists the
   applications whose retention clock passes within 8 days (the jobs' own three rules and periods, held equal to
   `dataverse.bulkDeleteJobs` by a test), writes the Not Granted snapshot where one is owed, logs each as Scheduled,
   then marks a row Deleted once the job has removed the case, deletes that case's signed PDF, and flags Overdue at
   35 days. First Monday of the month it lists stale open cases. **It contains no Dataverse delete.**
2. **Mode 2, erasure**, starts from the Flow menu on one applicant with the reference typed. A wrong reference stops it
   before anything is read. A grant with no final payment stops it with nothing deleted (decision D2). Otherwise it
   writes snapshots and Scheduled rows first, deletes the signed PDFs and the service-mailbox messages, then deletes the
   applicant row once (the cascades remove the rest), records the outcomes and emails the requester and the DPO.
3. **Mode 3, the SAR extract**, starts from the Flow menu and is read-only on every business table. It writes one HTML
   file with a section per store into the secured SAR folder, copies the signed documents beside it, logs the run and
   tells the process owner the file name. **Then it delivers (option B, `ADR-091`):** when the new setting
   `rev_SarProtectedSender` holds the dedicated SAR mailbox's address, the applicant has an email on record and the
   files fit under the `SarEmailMaxAttachmentMB` setting (15), it emails the extract **and every signed PDF copy** in
   one message from that mailbox, which a tenant mail rule encrypts. Otherwise (including a size or limit it cannot
   read), or if the send fails, it sends nothing, never part of the set, does not retry and tells the process owner
   to use option A, naming every file. The log row records which. The setting ships
   empty everywhere, so every environment starts on option A until the DEV check passes (§14).
4. **Two child flows**: *locate* (the applicant's whole case, shared by modes 2 and 3) and *snapshot* (the FR-055 Not
   Granted statistic, shared by modes 1 and 2).
5. **`rev_retentionlog`**, the evidence log every mode writes: references, rule, outcome and dates, never personal
   data; read by the process owner in the app; nobody can delete it.

## 2. Components Changed / Created

| Component | Type | Change Description | FR / WBS |
|---|---|---|---|
| [Workflows/REVRetentionSweep-…1014.json](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionSweep-8F1C2A44-1014-4B7A-9E21-0A1B2C3D4E14.json) (+ `.json.data.xml`, `.notes.md`) | Cloud flow, new | Mode 1, weekly Recurrence, 80 actions | FR-048, FR-049, FR-054, FR-055, NFR-010 · `wbs:0.13` |
| [Workflows/REVRetentionErasure-…1015.json](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionErasure-8F1C2A44-1015-4B7A-9E21-0A1B2C3D4E15.json) (+ data, notes) | Cloud flow, new | Mode 2, When a row is selected + typed reference, 83 actions; audit-history row *Retained (audit)* (§14) | FR-051, FR-052, FR-054, FR-055 · `wbs:0.13` |
| [Workflows/REVRetentionSarExtract-…1016.json](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionSarExtract-8F1C2A44-1016-4B7A-9E21-0A1B2C3D4E16.json) (+ data, notes) | Cloud flow, new | Mode 3, When a row is selected, read-only on business tables, 101 actions (option B delivery block, §14; attachments and size gate, §15) | FR-053, FR-054 · `wbs:0.13` (QuickBooks step `wbs:7.1`) |
| [Workflows/REVRetentionLocate-…1017.json](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionLocate-8F1C2A44-1017-4B7A-9E21-0A1B2C3D4E17.json) (+ data, notes) | Child flow, new | Returns the applicant's whole case, 17 actions | FR-051, FR-053 · `wbs:0.13` |
| [Workflows/REVRetentionSnapshot-…1018.json](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionSnapshot-8F1C2A44-1018-4B7A-9E21-0A1B2C3D4E18.json) (+ data, notes) | Child flow, new | One Not Granted statistic where owed, 15 actions | FR-055 · `wbs:0.13` |
| [Entities/rev_retentionlog/Entity.xml](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_retentionlog/Entity.xml#L179), main form, `AllRetentionLogs.xml` view | Table, new | 12 columns per TAD §5.12.3, organisation-owned, audited, nothing secured; `rev_signedpdfpath` and `rev_detail` 2000 characters (§14) | FR-054 · `wbs:0.13` |
| `OptionSets/rev_retentionruntype.xml`, `rev_retentiondatatype.xml`, `rev_retentionrule.xml`, [`rev_retentionoutcome.xml`](../../src/solutions/RevitaliseGrantAutomation/OptionSets/rev_retentionoutcome.xml#L44) | Global choices, new | Values 1..n in the TAD's order; outcome gains 8 *Retained (audit)* (§14) | FR-054 |
| [environmentvariabledefinitions/rev_SpoSarFolderUrl](../../src/solutions/RevitaliseGrantAutomation/environmentvariabledefinitions/rev_SpoSarFolderUrl/environmentvariabledefinition.xml) (+ README row) | Environment variable, new | Required, no default | FR-053 |
| [environmentvariabledefinitions/rev_SarProtectedSender](../../src/solutions/RevitaliseGrantAutomation/environmentvariabledefinitions/rev_SarProtectedSender/environmentvariabledefinition.xml) (+ README row, `Solution.xml` root component) | Environment variable, new | **Not required, no default**: empty is the designed "option B off" state (§14) | FR-053 · `ADR-091` item 4 |
| [Roles/REV Service Automation](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Service%20Automation/REV%20Service%20Automation.xml#L244) | Security role, changed | Log create/read/update/append, `prvAppendToUser`, read on `rev_review`, delete on applicant and its five cascade children, audit read | `ADR-089` item 7, `A-ERA-2`, `A-SAR-11` |
| [Roles/REV Service Automation](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Service%20Automation/REV%20Service%20Automation.xml#L262) (revision 2026-10-30) | Security role, changed | `prvWriterev_review` for REV \| Portal \| Finalise Decisions' review stamp; a separate change, not part of the helper | `wbs:6.6`, `IMP-1257` |
| [Roles/REV Admin](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Admin/REV%20Admin.xml#L190) | Security role, changed | Read on the log | TAD §5.12.3 |
| `Other/Solution.xml` | Manifest, changed | 1 table, 4 choices, 5 flows, 1 variable declared | — |
| `AppModules/…/AppModule.xml`, `AppModuleSiteMaps/…/AppModuleSiteMap.xml` | App, changed | Retention Log in the Operations group | `ADR-089` consequence 4 |
| `provisioning/dataverse/ensure-schema-helpers.psm1` | Provisioning helper, changed | Table added to the create list; `rev_startedby` mapped to `systemuser` | C-TECH-050 |
| `provisioning/deploymentSettings/{dev-scoring,test,prd}-settings.json` | Settings, changed | `RetentionStaleCaseMonths` (12), `ErasureNotificationEmail` ("not set") and `SarEmailMaxAttachmentMB` (15, §15), create-only, category *Data retention and erasure*; table added to `auditedTables` (also in `dev-auditing-settings.json`). 51 rows in each file | `ADR-089`, `ADR-091` item 5 |
| `provisioning/deploymentSettings/pac-import-{tstacc,prd}.json` | Deployment values, changed | `rev_SpoSarFolderUrl` placeholders; `rev_SarProtectedSender` placeholders `{{SAR_PROTECTED_SENDER_TSTACC}}` / `_PROD`, each commented "replace with an empty string until the check passes" | C-TECH-047, `ADR-091` item 4 |
| `config/revitalise-grant-automation-pipeline.yml` | Pipeline, changed | 5 DEV (two of them the `ADR-091` prerequisite and check, carrying `{{SAR_PROTECTED_SENDER_DEV}}`; the check gains the attachment, size-gate and `A-SAR-15` parts, §15), 2 TST/ACC and 2 PRD steps; two row-count sentences 48 → 50 → 51 | §12 |
| [docs/training/subject-access-request-procedure.md](../training/subject-access-request-procedure.md) | Runbook, new | SAR, erasure and the weekly summary, for the process owner | `ADR-088` item 8 |
| `src/tests/solutions/retention_helper/test_retention_helper_flows.py`, `src/tests/solutions/RetentionHelper.Tests.ps1` | Tests, new | 57 Python tests (static and executed), 12 Pester tests | — |
| `src/tests/solutions/FinaliseDecisions.Tests.ps1` (revision 2026-10-30) | Test, changed | 3 tests: every Dataverse operation Finalise Decisions makes, derived from its definition, has its privilege on REV Service Automation; shown to fail without `prvWriterev_review` | `wbs:6.6` |
| `src/tests/narrative/test_solution_flows.py` | Test, changed | `DeleteRecord` classified for the trigger-loop proof; a test that no flow triggers on a delete | — |
| TAD §3.1 | Design document, changed | A `rev_retentionlog` block folded in from §5.12.3 (no design change) so the coverage gate reads it | C-TECH-066 |
| `docs/development/revitalise-grant-automation-dev-summary.md` | Dev Summary, changed | Two stale "no SAR mechanism" rows pointed here | `ADR-088` words retired |

## 3. Data Model Changes

`rev_retentionlog` exactly as TAD §5.12.3: `rev_name` (autonumber `RL-{DATETIMEUTC:yyyy}-{SEQNUM:6}`), `rev_runtype`,
`rev_recordreference` (text 40, not a lookup), `rev_datatype`, `rev_ruleapplied`, `rev_outcome`, `rev_scheduledon` and
`rev_retaineduntil` (date only), `rev_actionedon` (date and time), `rev_signedpdfpath` and `rev_detail` (text **2000**,
shown as a text area, as the shipped-content gate requires above 250 characters; reviewer 2026-10-30, *"paths can get
much longer. make it 2000"*), `rev_startedby` (lookup to `systemuser`).
Organisation-owned, table auditing on, no column secured, so no special-category register row is needed. Choice values:

| Choice | Values |
|---|---|
| Run type | 1 Retention sweep, 2 Erasure, 3 SAR extract |
| Data type | 1 Applicant (with Bank Account), 2 Application (with Review, Grant, Payment), 3 Signed PDF, 4 Mailbox messages, 5 QuickBooks record, 6 Audit history, 7 SAR extract |
| Rule applied | 1 Paid 6 years, 2 Rejected 12 months, 3 Withdrawn or incomplete 6 months, 4 Orphaned applicant, 5 Erasure request, 6 Hold, 7 SAR access |
| Outcome | 1 Scheduled, 2 Deleted, 3 Not due, 4 Overdue, 5 Retained (hold), 6 Retained (finance), 7 Extract written, 8 Retained (audit) |

Created through the existing prerequisite path (`ensure-schema.ps1`, C-TECH-050), never by import. **That path is
check-then-create** (its own step 2 header: no attribute or option converges once it exists). Nothing here exists in
any environment yet (no import has happened), so the 2000 lengths and value 8 are created as built. Had either reached
an environment at 400 or with seven values, ensure-schema would print EXISTS and leave it.

## 4. Automation / Workflow Changes

| Definition | Trigger | Actions built | TAD estimate |
|---|---|---|---|
| sweep (mode 1) | Recurrence, Week, Monday 00:30 UTC | 80 | 33 |
| erasure (mode 2) | When a row is selected on `rev_applicant`, one typed text input, no splitOn | 83 | 40 |
| SAR extract (mode 3) | When a row is selected on `rev_applicant`, one run per row | 101 | 42 (TAD rev 37 amended: about 84) |
| locate (child) | Child flow, one text input (applicant id) | 17 | 8 |
| snapshot (child) | Child flow, one text input (application id) | 15 | 7 |
| **Total** | | **296** | **about 130** |

The difference is the failure path the TAD itself specifies (a Failure Alert and a stop after each guarded read, a
"not read" branch per store, log look-ups that make re-runs idempotent, counters for the summary), not extra
function. Every count is well inside the platform's 500-action and 8-level limits (the solution-wide limits test).
CO-011 names "higher action counts in DEV" as a re-price trigger; the change order is unbilled.

Each definition's reasoning, action by action, is in its `.notes.md` beside it. Points a reviewer should know:

* **Mode 1** reads its periods from one Compose keyed by `jobKey`, so the test compares it with both settings files.
  8 and 35 days are constants of the weekly schedule (`ADR-089` gate interactions); the stale-case months are a
  setting, and a missing setting is said in the summary rather than failing.
* **Mode 2** fails safe twice before reading the case: the typed reference (checked on the trigger and again on the
  row) and the identity of the starter (the log must name who started an erasure). The only Dataverse delete in the
  helper is its `Delete_the_applicant_row`. A re-run after a half-way failure marks the stopped run's Scheduled rows
  Deleted too, so none is left behind.
* **Mode 3's delivery block (`ADR-091` item 5)** is 8 actions against the TAD's "about 5": a route token
  (`Compose_delivery_route`: `send`, `off` or `no email`) so the email address appears in one secured action and not
  in the condition, the send, the two option A Teams messages, an outcome token (`Compose_delivery_outcome`) so
  `rev_detail` is written from a fixed vocabulary only, the `rev_detail` update, and a Failure Alert if that update
  fails, as for every other write in the flow. The send has retry policy **none**, *Sensitivity* empty, and is the
  flow's only send; the flow adds no mailbox action that reads or deletes a sent copy (`ADR-091` item 7, tested).
* **Mode 3's attachments and size gate (`ADR-091` item 5, second amendment)** are 17 actions against the TAD's "about
  3". Four variables, because one InitializeVariable may declare only one (`IMP-0821`); per written file (library
  copy, envelope copy, extract) one append of `{Name, ContentBytes}` to the attachments array that is passed whole to
  the send, and one of `{Name, Size}` to a list the gate measures; the gate scope (a loop adding every `Size` with
  `int(string())`, the setting read, the limit as `int(trim())`, and one `SetVariable` that writes `fits` or `too
  large` only when both succeeded); and a Select of the file names for the option A messages. The check variable
  starts as `not measured`, so any failure inside the gate leaves the route at `too large` and no send action runs.
* **Mode 3** builds one file from per-store scopes; an unreachable store writes "Not read" and why in its section and
  in the log row's stores list. A failed file write or log write sends no "extract ready" message. Trustee identities
  are removed from reviews by column (owner, created/modified by, the two trustee lookups and their annotations), and
  the audit section leaves out who made each change.
* **QuickBooks (mode 3 section 8)** is a section built from the payment rows' own QuickBooks references, amounts and
  dates, with the statement that the QuickBooks copy was not read because the connection does not exist yet
  (`wbs:7.1`). An action on a connection reference that does not exist would stop the whole flow from being turned
  on; the lookup by `rev_qboreference` is added when `wbs:7.1` delivers the connection.

## 5. Configuration & Provisioning Changes

| Key | Environment | Notes |
|---|---|---|
| `RetentionStaleCaseMonths` | DEV, TST/ACC, PRD | Whole Number 12, create-only, *Data retention and erasure* |
| `ErasureNotificationEmail` | DEV, TST/ACC, PRD | Text "not set", create-only; the process owner enters the DPO's mailbox. No address is committed |
| `SarEmailMaxAttachmentMB` | DEV, TST/ACC, PRD | Whole Number 15, create-only, *Data retention and erasure*, beside the two above (§15). Empty, non-numeric or missing: nothing is emailed |
| `rev_SpoSarFolderUrl` | DEV current value by hand; TST/ACC and PRD in the Pipelines pane | Placeholders `SPO_SAR_FOLDER_URL_TSTACC` / `_PROD` in the pac-import files |
| `rev_SarProtectedSender` | all three; **empty until the `ADR-091` check passes there** | DEV: current value by hand during the check (`{{SAR_PROTECTED_SENDER_DEV}}` in the pipeline step; no DEV pac-import file exists, so the TAD's "placeholders in the pac-import files" can hold only `_TSTACC` and `_PROD`). Same address in every environment, never committed |
| `auditedTables` += `rev_retentionlog` | all three | Switched on by the existing `ensure-auditing.ps1` step |

### Provisioning Scripts

No new script. The table, choices, lookup and privileges ride on `ensure-schema.ps1`; the settings rows on
`seed-settings.ps1`; auditing on `ensure-auditing.ps1`; the existing pipeline steps already run all three in every
environment. The SAR folder is manual by design (TAD §12 row). The new pipeline steps:

| Step | Purpose | Pipeline Block | Idempotency Check |
|---|---|---|---|
| SAR folder + `rev_SpoSarFolderUrl` current value | TAD §12, `A-SAR-9` | post_deploy: dev | manual, read back |
| Turn on the five flows, children first; run-only share of erasure and SAR extract with "Use this connection" | TAD 5.12 Runs as | post_deploy: dev | manual |
| DEV verification on synthetic applicants | TAD §12.11, §12.12 | post_deploy: dev | manual |
| Dedicated SAR mailbox + encrypt rule (no Send As yet, setting stays empty) | TAD §12 rev 37 row, `ADR-091` items 1-3 | post_deploy: dev (tenant-wide, once) | manual, tenant administrator |
| `ADR-091` check: (a) empty → option A; (b) before Send As → failed send, option A; (c) after Send As → encrypted arrival; (d) where the sent copy lands | §12.11 `A-SAR-4`, `A-SAR-13`, `A-SAR-14` | post_deploy: dev | manual; a found copy returns to the reviewer before the setting is filled |
| SAR folder, variables, flows on, run-only share; `rev_SarProtectedSender` empty until the check passed upstream (TST/ACC repeats check (c) once) | §12, `ADR-091` item 4 | post_deploy: tst_acc, prd | manual |
| DPO mailbox entered in the setting | `ADR-089` item 8 | post_deploy: tst_acc, prd | manual, create-only row |

**Build configuration: this feature amends the existing `config/revitalise-grant-automation-build.yml` and needs no
edit to it.** Every gate that reads flows, roles, entities and settings reads all of them (flow-definition-language,
source-validate with `--expect-flows manifest`, field-length-limits, domain-invariants, role-privilege-ownership,
tad-coverage, audited-tables), and the HARD `unit-tests` step runs every `*.Tests.ps1`, which now includes
`RetentionHelper.Tests.ps1` and through it the Python suite. No new script under `scripts/`, so nothing new to wire.

## 6. Security Controls Implemented

| Control | Implementation |
|---|---|
| Run history holds no content (C-DOM-004) | Secure inputs and outputs on every content-carrying action; a test derives the set mechanically and has a case proving it can fail |
| The log names no data subject (C-DOM-004, FR-054) | References, rule, outcome, dates; `rev_detail` only from the file name and the stores-read list (tested); the only person named is the staff member who started a run |
| Mode 3 read-only (`ADR-088` item 1) | No delete, no business-table update; the only Dataverse writes are the log row and its `rev_detail` update, files only to the SAR folder (tested) |
| The extract is never sent unencrypted (TAD §4.2 item 8, `ADR-091`) | One send, From = `rev_SarProtectedSender` only, on the `send` route only, no retry; empty setting, no address or a failed send → no email and the option A message (tested both ways, mutation-checked). What the flow cannot see, the tenant rule switched off later, is `A-R112`, accepted by the reviewer |
| One message or none (`ADR-091` item 5, second amendment) | The send carries every file the run wrote or does not run: the route is `send` only when the size check says `fits`; over the limit, an unreadable limit or a missing size → no send action, option A naming every file, `rev_detail` with the total (tested under, at, one byte over, and with the limit or a size empty, missing or non-numeric; mutation-checked) |
| Mode 1 deletes no row (`ADR-089` item 2) | No `DeleteRecord`; the only delete is the PDF of a case already gone (tested) |
| Destructive erasure guarded (`ADR-089` items 5, 7) | Started by a person from the Flow menu, typed reference, one applicant only, starter identified or the run stops, Scheduled rows before deleting |
| Least privilege (C-DOM-020) | Delete granted on exactly the six tables the cascade touches; log create/read/update only (D5); audit read without audit delete (C-DOM-012); REV Admin read only |
| Group-team role assignment (C-TECH-040) | Unchanged: the new privileges reach the service identity through its existing group team |

## 7. Known Limitations / Deferred Items

**SDD changes owed:** none. No reviewer decision taken during this build changes an FR.

**Sequencing (lead-agent's reading, recorded here as instructed; not in the TAD).** Until mode 1 is on in PRD, any
bulk-delete job run there deletes applications with no FR-055 snapshot, no FR-054 log row, and leaves the signed PDFs
in SharePoint. Mode 1 must reach PRD before the first real retention clock passes; the earliest is withdrawn or
incomplete, six months after last contact. The PRD pipeline step repeats this.

| Item | State |
|---|---|
| **Delivery option B: built** (§14) | The ARCH_GAP raised in the first 2026-10-30 revision is answered by TAD rev 37 (`ADR-091`, Accepted). Built as designed; live only after the DEV check |
| **Signed documents under option B** (`IMP-1261`) | **Answered and built** (reviewer 2026-10-30, *"Also attach the signed pdf's off course"*; TAD rev 37 second amendment). The one email carries the extract and every signed PDF copy, all or nothing, under the `SarEmailMaxAttachmentMB` gate (§15). Option B no longer delivers less than option A. The size ceiling itself is open (`A-SAR-15`). *Previously read: "a reviewer question … the runbook tells the process owner to send the signed copies by the option A route meanwhile"* |
| **QuickBooks lookup** | Section built from the payment rows with a "not read" statement; the lookup is added with `wbs:7.1` |
| **Audit history row outcome** | **Settled** (reviewer, *"Build Retained (audit)"*): outcome 8, retained until the erasure date + 6 years (§14) |
| **Finalise Decisions privilege gap (`wbs:6.6`)** | **Closed in source 2026-10-30** (reviewer decision 3): `prvWriterev_review` added to REV Service Automation, with a derived test. Live effect waits for the next import |
| **Acceptance variables in TST/ACC and PRD** | The helper reads `rev_SpoSiteUrl`, `rev_SpoSignedAcceptanceUrl` and `rev_DocuSignAccountId`, which the pac-import files do not carry (acceptance is DEV only, EX-006/EX-007). The pipeline steps say to enter them in the pane |
| **DEV has no bulk-delete jobs** (TAD §3.4.1) | The Deleted path is exercised in DEV by deleting a logged synthetic row by hand |
| **A second snapshot after a partial failure** | If a mode 1 run fails after a snapshot and before its log row, next week can write a second Not Granted row for that application. A snapshot carries no reference by design, so it cannot be checked (the same limit Finalise Decisions states) |
| **TAD §3.1 fold-in** | The approved TAD designed the table only in §5.12.3; the coverage gate reads §3.1. A §3.1 block restating §5.12.3 was added as an interim. Reviewer 2026-10-30: architect-agent replaces it (dispatched in parallel); not touched in this revision |
| **DocuSign retention setting (D1, `A-ERA-5`)** | Revitalise's DocuSign administrator; not buildable here |
| **Governance Runbook §7 and Data Governance Framework §4 lines** | `wbs:0.8` / `wbs:0.7` documents in `docs/Import/`; not edited here (TAD §4.2 item 11) |

## 8. Build Instructions

Run the existing build configuration unchanged: `python3 scripts/run-build.py config/revitalise-grant-automation-build.yml`.
A DEV-only iteration may use `--changed-since last-green`; promotion beyond DEV runs the full build. Before the first
import into an environment, its `ensure-schema.ps1` step must create `rev_retentionlog` and the four choices (it
prints CREATED for each, then an ACTION REQUIRED auditing note that the existing `ensure-auditing.ps1` step answers).
Expected pack notice: the standing "root components are not defined in customizations" list grows by two
`EnvironmentVariableDefinition` lines (`rev_SpoSarFolderUrl`, `rev_SarProtectedSender`): 22 lines, measured locally, §11.

## 9. Test Guidance

* **Synthetic applicants only** in DEV and TST/ACC (C-TECH-007). DEV runs every open row of §10 in one session (pipeline
  dev post_deploy, verification step).
* Mode 2 negative cases first: wrong reference, empty reference, two rows selected, a grant without final payment.
  Each must leave every table, file and message as it was.
* Mode 2 positive: count rows in the six tables before and after; the log shows one row per record, all Deleted, a
  QuickBooks row per paid grant with the final payment date + 72 months, an audit row.
* Mode 3: open the extract with every choice column set on the test applicant; confirm the trustee's name is absent
  from the reviews and the audit section; open the SAR folder as a trustee and as a finance test user (denied).
  Option B: every attachment of the one email opens and matches its SAR folder file; with the limit at 1, or empty,
  nothing is emailed and the option A message names every file (pipeline `ADR-091` check (c) to (c3)).
* Mode 1: rows whose clock passes within 8 days, one beyond; run twice and confirm nothing is logged twice; delete a
  logged synthetic application by hand and confirm the next run marks it Deleted and removes its PDF.
* The executed tests (`src/tests/solutions/retention_helper`) name the scenario per test and can be read as a list
  of the behaviours to repeat live.

## 10. Unvalidated Assumptions Register (C-TECH-052)

| ID | Claim (one sentence — BOTH directions if it is a conditional) | Where in source | Evidence | Why not verified | Cheapest verification (BOTH directions) | Status |
|---|---|---|---|---|---|---|
| A-ERA-1 | The When-a-row-is-selected trigger offers a typed text input read as `triggerBody()?['text']`, and the run stops before any read when it does not equal the reference, and goes on when it does | `src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionErasure-8F1C2A44-1015-4B7A-9E21-0A1B2C3D4E15.json` | E4 (TAD §12.12) | No flow in source has a trigger input | DEV: run with a wrong reference (fails, nothing read), then the right one (proceeds). No input offered: CASCADE ARCH_GAP | OPEN |
| A-ERA-2 | With delete on the applicant and its five children, one delete of `rev_applicant` removes applications, reviews, grants, payments and bank accounts through the parental cascades, and removes nothing outside the case | `src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionErasure-8F1C2A44-1015-4B7A-9E21-0A1B2C3D4E15.json` | E3 (relationship XML), simulator | Which child privileges a cascade checks is undocumented here | DEV: erase a synthetic applicant with two applications, a grant, a payment, a bank account; count before and after, and confirm another applicant's rows are untouched | OPEN |
| A-ERA-3 | SharePoint Get file metadata using path then Delete file deletes the signed PDF, and a second attempt fails with a 404 the flow treats as already gone (and any other failure stops the scope) | `src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionSweep-8F1C2A44-1014-4B7A-9E21-0A1B2C3D4E14.json` | E4 | No flow in source deletes a file | DEV: delete a test PDF twice; then point a row at an unreachable site and confirm the scope fails | OPEN |
| A-ERA-4 | The Outlook connection deletes a found message (DeleteEmail_V2 with mailboxAddress) as the service identity, and a message already gone fails with 404 | `src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionErasure-8F1C2A44-1015-4B7A-9E21-0A1B2C3D4E15.json` | E4 | Only SendEmailV2 is used in source | DEV: two test messages, mode 2, both gone; re-run, no error | OPEN |
| A-ERA-5 | Revitalise's DocuSign plan offers account-level retention purging completed, declined and voided envelopes 30 days after they close | none in source: a DocuSign account setting (decision D1) | E4 | External SaaS setting | Revitalise's DocuSign administrator confirms in account settings | OPEN |
| A-SAR-4 | **(rewritten 2026-10-30, TAD rev 37; extended by the second amendment)** A message the flow sends with *From (Send as)* = `rev_SarProtectedSender` arrives at an external address encrypted, the attachments readable only after the recipient authenticates, **and with the signed PDFs attached as well, every attachment opens and matches its SAR folder file**; and with the setting empty, **or the set over `SarEmailMaxAttachmentMB`**, nothing is sent. *Previously read: "until confirmed, mode 3 sends nothing … the mechanism is not designed"; the send step is no longer chosen at build time: it is always built and the setting turns it on* | `src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionSarExtract-8F1C2A44-1016-4B7A-9E21-0A1B2C3D4E16.json` | E2 (mail-flow rule, Microsoft Learn), simulator for the empty-setting half | Nothing has been sent; the mailbox and rule do not exist yet | DEV, pipeline `ADR-091` check (a), (c) and (c2): empty setting → no email and the option A message; filled after Send As → encrypted arrival at an external test mailbox, every attachment matches, message trace shows the rule fired; limit set to 1 (then empty) → no email, the option A message naming every file, `rev_detail` too large (then not measured) with the total; restore 15. Fails: the setting stays empty everywhere, no rebuild | OPEN |
| A-SAR-13 | `SendEmailV2`'s `emailMessage/From` sends as the dedicated mailbox when the `rev_SharedOutlook` connection owner has Send As on it, and fails (nothing sent) when the permission is missing | `src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionSarExtract-8F1C2A44-1016-4B7A-9E21-0A1B2C3D4E16.json` | E2 (connector reference); no other flow in source sets it | No mailbox exists yet | DEV, check (b) then (c): before Send As, a failed send and the option A message; after, check (c). Order not possible: read the first half from any failed send's run history | OPEN |
| A-SAR-14 | A send as `rev_SarProtectedSender` may leave a copy of the extract email, attachment included, in Sent Items of the connection owner's mailbox, the dedicated mailbox, or both; the flow neither reads nor deletes it (`ADR-091` item 7) | `src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionSarExtract-8F1C2A44-1016-4B7A-9E21-0A1B2C3D4E16.json` | E4, nothing verified | Nothing has been sent | DEV, check (d): per mailbox, whether a copy exists, carries the attachment, and any retention. A copy found: setting back to empty and to the reviewer before it is filled anywhere | OPEN |
| A-SAR-15 | **(TAD rev 37 second amendment, `ADR-091` item 5)** (a) The SharePoint create-file response carries `Size` in bytes for each file written to the SAR folder, and when it does the gate sums it; when it does not, `int(string())` fails, the set counts as over the limit and nothing is sent; (b) one `SendEmailV2` message carrying the extract and several PDFs totalling up to 15 MB of raw files is accepted by Exchange and the encryption rule (encrypted-message limit 25 MB, E2), and a larger set fails to send (fail-closed: option A); (c) several attachments in one `SendEmailV2`, built as one array, arrive intact | `src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionSarExtract-8F1C2A44-1016-4B7A-9E21-0A1B2C3D4E16.json` | E2 (Exchange Online limits, the connector reference, read by the architect 2026-10-30); simulator for the gate's arithmetic and every fail-closed branch | Nothing has been sent; no flow in source reads a create-file `Size` | DEV, pipeline `ADR-091` check (c) and (c3): (a) read the `Size` each unsecured `Add_the_*_file` action recorded in run history; (b) a set near 15 MB, then, with the reviewer's agreement, one near 20 MB, recording where it fails; if 15 is wrong the process owner changes the setting, no rebuild; (c) open every attachment. Any of (a) to (c) fails: `rev_SarProtectedSender` stays empty (option A) and the design returns to the architect | OPEN |
| A-RH-3 | `emailMessage/Attachments` takes an array of `{Name, ContentBytes}` with `ContentBytes` base64, passed whole as `@variables('attachments')`; `base64()` of the extract string gives a file that opens identical to the SAR folder copy; **and a PDF's `ContentBytes` is its get-content body's `$content` (SharePoint `GetFileContentByPath`, DocuSign `GetDocumentsV2`), which opens identical to the copy the same body wrote** (extended 2026-10-30, §15) | `src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionSarExtract-8F1C2A44-1016-4B7A-9E21-0A1B2C3D4E16.json` | E4 (no flow in source attaches a file; the simulator decodes it as written) | No send has run | DEV, check (c): open every received attachment, the extract and each PDF, and compare it with its SAR folder file. The designer shows a different shape, or a PDF arrives unreadable: copy the shape from the designer, CASCADE none (a shape fix) | OPEN |
| A-SAR-6 | Get file content using path reads the signed PDF named by `rev_signedpdfurl` (the value Completion stores) and Create file writes it unchanged to the SAR folder | `src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionSarExtract-8F1C2A44-1016-4B7A-9E21-0A1B2C3D4E16.json` | E4 | Not used by any flow in source | DEV: mode 3 on a test applicant with a completed test envelope; compare the copy with the library file | OPEN |
| A-SAR-7 | Create HTML table over Dataverse rows with no `$select` gives readable choices and lookups (formatted-value annotations come back) and an empty list gives an empty table, not a failure | `src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionSarExtract-8F1C2A44-1016-4B7A-9E21-0A1B2C3D4E16.json` | E4 | Not used in source | DEV: open the extract of a test applicant with every choice set and one with no grant | OPEN |
| A-SAR-8 | The When-a-row-is-selected trigger carries the starter's address in the `x-ms-user-email` header; when it does the log names the starter, when it does not both modes stop before reading the case | `src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionSarExtract-8F1C2A44-1016-4B7A-9E21-0A1B2C3D4E16.json` | E4 | Finalise Decisions uses the trigger but reads no user | DEV: run mode 3 as a named test process owner; the log row's Started By names her. Fails "StarterNotIdentified": CASCADE ARCH_GAP | OPEN |
| A-SAR-9 | The service identity's SharePoint connection can create files in a folder with unique permissions, and nobody else can open the folder | `src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionSarExtract-8F1C2A44-1016-4B7A-9E21-0A1B2C3D4E16.json` | E4 | No folder exists yet | DEV: create the folder per §12, run mode 3, open the folder as a trustee and a finance test user (denied) | OPEN |
| A-SAR-10 | The read-only QuickBooks connection (`wbs:7.1`) has an action returning one transaction by `rev_qboreference`; until it exists the section carries the payment rows and a "not read" statement | `src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionSarExtract-8F1C2A44-1016-4B7A-9E21-0A1B2C3D4E16.json` | none | No QuickBooks connection in source | `wbs:7.1`'s feasibility report names the action; then add the step and run mode 3 for a payment with a known reference | OPEN |
| A-SAR-11 | `prvReadAuditSummary` and `prvReadRecordAuditHistory` (names read from DEV, E1) let the service identity list `audits` filtered by `_objectid_value` with `changedata`, and grant no audit delete | `src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionSarExtract-8F1C2A44-1016-4B7A-9E21-0A1B2C3D4E16.json` | E1 (privilege names), E4 (read shape) | No flow reads `audits` | DEV: change a test applicant twice, run mode 3, compare section 7 with the Audit History tab. No values: tenant-administrator fallback, architect told | OPEN |
| A-SAR-12 | GetEmailsV3 with `from` (Inbox) and `to` (Sent Items) and `mailboxAddress` returns the service mailbox's messages to or from an address, with their bodies, in lower-case or capitalised field names | `src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionSarExtract-8F1C2A44-1016-4B7A-9E21-0A1B2C3D4E16.json` | E4 | Only SendEmailV2 in source | DEV: two test emails to and from a test address; mode 3 lists both. Not possible: the process owner searches by hand, architect told | OPEN |
| A-RH-1 | A child flow's `Response` body is the caller's `body('<child action>')`, and a 500 response fails the caller's child-flow action (so a failed locate or snapshot stops the caller) | `src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionLocate-8F1C2A44-1017-4B7A-9E21-0A1B2C3D4E17.json` | E3 (Failure Alert answers 200 the same way) | No caller in source reads a child's body or receives a 500 | DEV: run mode 3 (body arrives); break the locate child's read on a test id and confirm mode 3 stops with its own alert | OPEN |
| A-RH-2 | `$filter` and `$expand` through a lookup's navigation property (`rev_applicationid/rev_status`, `rev_applicantid/rev_lastcontactdate`) select exactly the rows the jobs' rules select, date-only values compared as `yyyy-MM-dd` | `src/solutions/RevitaliseGrantAutomation/Workflows/REVRetentionSweep-8F1C2A44-1014-4B7A-9E21-0A1B2C3D4E14.json` | E3 (Round Statistics expands `rev_applicantid` live; filtering through it is documented) | No flow in source filters through a navigation property | DEV: synthetic rows either side of each cutoff; the sweep logs exactly the due ones | OPEN |

`A-DS-9` (the combined DocuSign document with its certificate of completion), used by mode 3 for an envelope with no
library copy, stays registered in `revitalise-grant-automation-dev-summary.md`.

## 11. Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

### Verification level reached

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| Five flow definitions | **V1**, plus execution in the simulator | macOS, local | `verify-flow-definition-language.py` OK over 18 flows (checks 1-19); every expression in the five (471) parses; 40 Python tests OK, 21 of which run the definitions |
| Whole solution | **V2** (unmanaged) | macOS, pac CLI, local | `pac solution pack --packagetype Unmanaged` → "Packed Solution."; the five workflows, the table and the choices are in the zip |
| Table, roles, settings, pipeline | V1 | macOS | run-source-gates 19/19 PASS; `verify-pipeline-config.py` exit 0; `verify-audited-tables.py` exit 0 |
| Revision 2026-10-30: REV Service Automation `prvWriterev_review`, runbook, mode 3 notes | V1 | macOS, local | `RetentionHelper.Tests.ps1` + `FinaliseDecisions.Tests.ps1` 49/49 pass (the new derived test fails with the privilege removed, restored after); run-source-gates 19/19 PASS; both assumption gates PASS; `verify-build-config.py` exit 0; `verify-improvement-log.py --check` exit 0 |
| Revision 2026-10-30 (2), TAD rev 36/37: option B delivery block, `rev_SarProtectedSender`, outcome 8, 2000-character columns | V1, plus execution in the simulator; **V2** (unmanaged pack) | macOS, local | 47 Python + 12 Pester retention tests pass; six mutations of the new block each fail a test (route forced to send, retry added, From changed, failure branch removed, send unsecured, cap back to 400); full `unit-tests` suite 1524 passed, 0 failed; run-source-gates 19/19 PASS (after condensing four descriptions the 256-character gate caught); `pac solution pack --packagetype Unmanaged` → "Packed Solution.", the packed zip carries `rev_SarProtectedSender`, outcome 8 and `MaxLength 2000` |
| Revision 2026-10-30 (3), TAD rev 37 second amendment: attachments array, size gate, `SarEmailMaxAttachmentMB` seed | V1, plus execution in the simulator; V2 (unmanaged pack), §15 | macOS, local | see §15 for the commands and their results |
| Anything on the platform | **not reached** | — | No import, no run. V3 and above wait for the build and the DEV session |

Human open-and-save (V4): **not yet performed**.

### Tool warnings triaged (C-TECH-055)

| Warning | Source step | Resolved / Accepted | Rationale if accepted |
|---|---|---|---|
| `pac solution pack`: "Following root components are not defined in customizations", **22** `Type=` lines: 9 `EntityRelationship`, 1 `AIModel`, **12** `EnvironmentVariableDefinition` (measured 2026-10-30 after this revision) | pack-unmanaged (local, this change) | Accepted, standing | The standing list triaged at [revitalise-settings-category-dev-summary.md#L129](revitalise-settings-category-dev-summary.md#L129) (20 lines after WI-0154) plus two `EnvironmentVariableDefinition` lines for the new `rev_SpoSarFolderUrl` and `rev_SarProtectedSender`, the same kind as the ten already accepted. No line for the new table, choices or flows |
| The same notice | pack-managed (last SUCCESS build 20261023-2) | Accepted, standing | Triaged at [revitalise-settings-category-dev-summary.md#L129](revitalise-settings-category-dev-summary.md#L129); expected to read 22 with the lines above |
| The same notice | pack-unmanaged (build 20261023-2) | Accepted, standing | Triaged at [revitalise-settings-category-dev-summary.md#L130](revitalise-settings-category-dev-summary.md#L130) |
| Vite "Some chunks are larger than 500 kB" | code-app-build (build 20261023-2) | Accepted, standing | Triaged at [revitalise-settings-category-dev-summary.md#L131](revitalise-settings-category-dev-summary.md#L131); this change touches nothing under `src/code-apps` |

### Diagnostic components created and removed (C-TECH-056)

None. Two read-only `pac env fetch` queries were run against DEV (privilege names; a search for flows with a
selected-row trigger or a mailbox read); nothing was created.

## 12. Work Items — close-out record (C-TECH-079)

No items carried. The dispatch named `wbs:0.13` and `CO-011`; no work item exists for them in `logs/work-items.jsonl`.

Scope check: not applicable (no ids carried). Deferred: none.

---

## 13. Revision 2026-10-30 — reviewer decisions

| # | Decision | What this revision did |
|---|---|---|
| 1 | Protected email: option B is a go (Business Premium available); never send unencrypted | `A-SAR-4` evidence updated to reviewer-stated, still OPEN. Send step not built: `CASCADE: ARCH_GAP` (§7). *Superseded by §14: the ARCH_GAP is answered by TAD rev 37 and the step is built* |
| 2 | Audit-history row outcome | Still with the reviewer; nothing changed. *Settled in §14: Retained (audit)* |
| 3 | `prvWriterev_review` on REV Service Automation | Added, with a test derived from the Finalise Decisions definition (`wbs:6.6`, `fixes` `IMP-1257`) |
| 4 | TAD §3.1 fold-in | architect-agent's; the TAD was not edited |

## 14. Revision 2026-10-30 (2) — TAD rev 36 and rev 37 approved, `ADR-091` Accepted

| # | TAD source | What this revision did |
|---|---|---|
| 1 | `ADR-091` items 4, 5, 7; §4.2 item 8 | Mode 3 delivery block: route token, condition, `Send_the_extract_protected` (`SendEmailV2`, From = `rev_SarProtectedSender`, To = email on record, Reply To = `rev_ServiceMailbox`, extract attached, Sensitivity empty, retry none, secured), two option A Teams messages (setting off or no email; send failed or timed out), outcome token, `rev_detail` update, alert. New variable `rev_SarProtectedSender`, not required, no default, placeholders in both pac-import files and the DEV pipeline step. Two DEV pipeline steps (tenant prerequisite; the four-part check) and the TST/ACC and PRD steps say the value stays empty until the check passed upstream. The flow reads and deletes no sent copy |
| 2 | Approval amendment item 3; §5.12.2 step 8 | `rev_outcome` value 8 *Retained (audit)*; mode 2's audit-history row writes it with `rev_retaineduntil` = `Compose_erasure_date` + 6 years (was *Not due*, and `utcNow()` + 6 years) |
| 3 | Approval amendment item 2; §5.12.3 | `rev_signedpdfpath` and `rev_detail` 2000 characters; both `rev_detail` writes truncate at 2000, and a test reads the cap from `Entity.xml`. No test asserted 400 before |
| 4 | Architect's list of stale wording | "A-SAR-4 selects B or A at build time" rewritten in the runbook (steps 4 and 5), this document (§1, §7, §10, §13), the mode 3 definition's description and notes, and the test module's docstring and tests. Register: `A-SAR-4` rewritten, `A-SAR-13`, `A-SAR-14` and `A-RH-3` added, all OPEN, closing in the DEV check |

Not changed, by instruction: the TAD; WI-0121's evidence drift.

## 15. Revision 2026-10-30 (3) — TAD rev 37 second amendment: signed PDFs attached, size gate

Reviewer, 2026-10-30, verbatim: *"Also attach the signed pdf's off course"* (choice (a) on `IMP-1261`). The architect
amended `ADR-091` item 5, §5.12 mode 3, §4.2 item 8, Consequence 5 and added `A-SAR-15`. Built exactly the list the
amendment says is owed by development-agent:

| # | Owed | What this revision did |
|---|---|---|
| 1 | The send step and the attachment array | `Send_the_extract_protected` attaches `@variables('attachments')`: one array, built by appending one `{Name, ContentBytes}` per file the run writes (library copy, envelope copy, extract) and passed whole, the connector's multi-attachment workaround. The body says the files are the extract and the signed acceptance documents |
| 2 | The size sum and gate | Beside each attachment, `{Name, Size}` is appended to `attachmentFiles` from that file's own create-file response. `Measure_the_attachments` adds every `Size`, reads `SarEmailMaxAttachmentMB` by key, and only when both succeed sets `attachmentCheck` to `fits: <n> MB of files against a limit of <m> MB` or `too large: …`. It starts as `not measured: …`. The route is `send` only on `fits`. Over the limit, or anything unreadable: no send action runs, the option A Teams message names the reference and every file name and gives the check's text, and `rev_detail` records `delivery: option A, not emailed, <check>`, with the total. No split and no extract-only email: there is one send action, and its only route needs the whole set to fit. A run that does send also records `fits: <n> MB…`, which the `A-SAR-15` calibration can read |
| 3 | The seed, all three files | `SarEmailMaxAttachmentMB`, Whole Number, value 15, create-only, category *Data retention and erasure* (the same as `RetentionStaleCaseMonths`), a plain-language description with no document ids. **51 rows** in each file (was 50); both pipeline sentences that state the count say 51, which `verify-derived-counts.py` checks against the files |
| 4 | The runbook | `docs/training/subject-access-request-procedure.md` steps 4 and 5: one message with the extract and the signed documents; a new paragraph *When the files are too large to email*; *Signed documents under option B* rewritten, with the old text kept as *Previously read* |
| 5 | The Dev Summary | §1, §2, §4, §5, §6, §7 (the `IMP-1261` row), §9, §10 (`A-SAR-4` extended, `A-SAR-15` added, `A-RH-3` extended to the PDF content shape), §11, this section |
| 6 | The flow tests | 10 new Python tests (57 in all): every CreateFile has its attachment and its measured size, derived from the definition; the check is set once, inside the gate, after both reads; the limit is read by key and seeded beside the stale-case setting; executed: both files attached and each identical to its SAR folder copy; the envelope copy attached; 16 MB against 15 not sent; exactly at the limit sent and one byte over not; limit empty, blank, non-numeric, decimal or missing not sent; a file size missing or non-numeric not sent; the setting empty makes the size irrelevant. Two mutations shown to fail: a file written but not measured (the static derivation fails, and the length check refuses the send), and a route that ignores the check (the over-limit run then sends) |
| 7 | Pipeline `ADR-091` check | (c) now runs on an applicant with a signed PDF and opens every attachment; (c2) the size gate with the limit at 1 and then empty; (c3) `A-SAR-15` (b), a set near 15 MB and, with the reviewer's agreement, near 20 MB |

**Choices made where the amendment is silent, for the reviewer to see.** (a) The two arrays must have the same length
for `fits`: the size check must measure the set that is sent, so a file attached but not measured never sends. (b) A
decimal limit (`15.5`) is "not a whole number" and counts as over the limit, as the TAD says for non-numeric. (c) MB in
the messages and `rev_detail` is rounded **up** to 0.1, so a set one byte over 15 MB reads 15.1, never 15.0. (d) The
`{Name, Size}` appends are **not** secured, so the DEV check can read each `Size` in run history (`A-SAR-15` (a));
they hold a reference and a number only. (e) The option A messages now list every file name, as `ADR-091` item 5's
"the extract and the PDF copies are in the SAR folder" implies; before, they named the extract only.

**Counts that now read differently elsewhere, not edited here.** The TAD (line 7415, the `WI-0151` row) says the two
rev 34 keys make the live table 52; with this key it is 53. That line is architect-agent's. `CO-012` states the live
table's 50 rows as a dated fact of 2026-10-23 and the files' 48 as they were then: both are true as dated records and
are not stale, so it is not edited and needs no amendment. WI-0121's evidence drift: not touched, as instructed.

**Gate and test results for this revision.**

| Command | Result |
|---|---|
| `python3 src/tests/solutions/retention_helper/test_retention_helper_flows.py` | 57 tests OK |
| `pwsh -NoProfile -File src/tests/Invoke-Tests.ps1` (the `unit-tests` step's suite) | 1524 passed, 0 failed, 1 skipped; exit 0 |
| `python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation` | OK, 18 flows, checks 1-19 |
| `python3 scripts/run-source-gates.py config/revitalise-grant-automation-build.yml` | 19/19 PASS (70 of 89 steps not covered, as it prints) |
| `verify-assumption-markers.py`, `verify-assumption-register.py`, `verify-build-config.py` | PASS, PASS, exit 0 |
| `verify-derived-counts.py` (the 51 in both pipeline sentences), `verify-pipeline-config.py`, `verify-audited-tables.py`, `verify-source-derived-test-counts.py` | exit 0 each |
| `pac solution pack --packagetype Unmanaged` | "Packed Solution."; the packed mode 3 definition carries `Measure_the_attachments` and `SarEmailMaxAttachmentMB`; the root-components notice is unchanged at 22 `Type=` lines |
| `verify-improvement-log.py` then `--check` | OK; 3 warnings, none a blocker (IMP-1261 now fixed by IMP-1263 and awaiting its review) |

## Hours proposal

None. CO-011 is approved **unbilled** (`EX-013`): no worklog session is proposed for `0.13`, and none is to be logged.

`wbs:6.6` (revision 2026-10-30, the `prvWriterev_review` change and its test): **0.25 h** proposed for `commercial-agent` to confirm; evidence: the role diff and the three new tests in `FinaliseDecisions.Tests.ps1`.

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-1254 | `platform-contract-guessed-not-groundtruthed` | friction | Write a literal string that begins with @ in a flow definition as @@; execute a new flow with the simulator before presenting it |
| IMP-1255 | `approved-document-internally-inconsistent` | friction | When a TAD revision designs a new table in any section, add its §3.1 block in the same revision |
| IMP-1256 | `change-order-sizing-without-precedent` | friction | When sizing a flow by action count here, count the failure path too: it roughly doubles the functional count |
| IMP-1257 | `declared-policy-not-mechanically-enforced` | rework | When a flow performs a Dataverse operation as the service identity, check REV Service Automation grants that privilege on that table |
| IMP-1258 | `declared-policy-not-mechanically-enforced` (`fixes` IMP-1257) | friction | When you add a privilege a flow needs, add a test that derives the flow's operations from its definition |
| IMP-1259 | `approved-document-internally-inconsistent` | friction | When a design gates a step on a tenant capability, name the mechanism and its fail-closed check, not only whether it exists |
| IMP-1261 | `delivery-route-delivers-less-than-fallback` (instance of `approved-document-internally-inconsistent`) | friction | When a design adds an automated route beside a manual fallback, list what each route delivers side by side and make them match, or state the difference as a decision |
| IMP-1262 | `flow-size-estimate-omits-variable-plumbing` (instance of `change-order-sizing-without-precedent`) | friction | When estimating a flow change that accumulates values, count one InitializeVariable per variable, one append per producing branch, and a loop plus increment for a sum |
| IMP-1263 | `delivery-route-delivers-less-than-fallback` (`fixes` IMP-1261) | friction | When a delivery route gains attachments, gate the whole set by a tunable size limit and send all of it or none |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`

---

## Code Review Checklist
- [x] All FR IDs covered (FR-048 to FR-055 as TAD §5.12 assigns them; QuickBooks read waits on `wbs:7.1`)
- [x] No hardcoded secrets
- [x] Security controls from TAD §6 and §5.12 implemented (§6 above)
- [x] Every TAD §12 item has a pipeline step (no new script; the SAR folder is manual by design)
- [x] Role assignments via group teams only
- [x] No hardcoded environment-specific IDs/URLs (`no-hardcoded-environment-values` PASS)
- [x] Every guessed platform contract is in §10 **and** commented `A-nnn` in source
- [x] Where an environment existed, ground truth was used (privilege names read from DEV); the rest needs a maker or a run
- [x] Platform limits the packer does not enforce are gated (description length, nesting, action count, expression length)
- [x] Verification levels in §11 are the levels actually executed
- [x] Scripts run on the CI runner's OS (none added)
- [x] Every tool warning triaged; no diagnostic components
- [x] Accessibility: one view and one read-only form on a model-driven table, standard controls
- [x] No dead code or debug statements
- [x] Unit tests written (57 Python, 12 Pester)
- [x] Every carried work item is built or deferred (none carried)

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`
