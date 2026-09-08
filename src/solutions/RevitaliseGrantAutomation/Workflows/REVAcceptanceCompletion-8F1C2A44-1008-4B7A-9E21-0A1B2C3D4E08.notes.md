# REVAcceptanceCompletion-8F1C2A44-1008-4B7A-9E21-0A1B2C3D4E08.json - full descriptions

Same 256-character constraint as every other flow in this solution. This file carries the
reasoning the condensed on-file descriptions could not.

`wbs:3.4`, Automation #3, **DEV only**. Same authorisation as wbs:3.2/3.3 (EX-006/EX-007). Build
held pending the reviewer's batch go-ahead; this dispatch produces source only.

## Trigger: `CreateHookEnvelopeV4`, not the deprecated V1/V2 shape — A-DS-8

Checked directly against the connector reference (`learn.microsoft.com/connectors/docusign/`,
fetched 2026-09-06): three non-deprecated triggers exist for an envelope-status change —
`CreateHookEnvelopeV3` (single-envelope Connect webhook), `CreateHookEnvelopeV4` (account-level,
returns `WebhookEnvelopeResponseV4`), and `CreateOrgHookEnvelope` (organization-level). This flow
uses the account-level V4 trigger: it needs no per-envelope registration (a registration per
grant would mean this flow — or wbs:3.2 — creating one webhook per envelope, which neither TAD
5.10 nor any action in this solution does), and account-level is the narrower, more appropriate
scope than organization-level for a single Dataverse environment's automation.

**What IS ground-truthed (E2, the connector's own documented response shape):**
`WebhookEnvelopeResponseV4`'s body carries `data.envelopeSummary.envelopeId` and
`data.envelopeSummary.status`, read here as `triggerBody()?['data']?['envelopeSummary']?['envelopeId']`.
This is real, current documentation — not the undocumented-dynamic-schema situation A-DS-2 faced
on the Create Envelope flow's `signers` parameter.

**What is NOT ground-truthed:** the `events` parameter is `array of string`, described only as
"Select an event" with a designer-resolved dropdown (the same class of dynamic parameter
A-DS-2/IMP-0614 already named) — no live route in this session reaches that dropdown's actual
values. `"envelope-completed"` is authored here as DocuSign's own well-known Connect event name
for "all recipients have signed" (a reasonable, commonly-published value), but is NOT confirmed
against this connector's own resolved list. Named as a mandatory pre-activation step in
`config/revitalise-grant-automation-pipeline.yml`'s DEV `post_deploy`, same treatment as A-DS-2.

## `Skip_if_already_processed_or_not_found` — the idempotency/safety gate

Two conditions must both hold before this flow acts: a grant is actually found by envelope id,
AND that grant's `rev_status` is still 2 (Acceptance Issued). Either failing is treated as a
**safe no-op, not a failure** (NFR-018) — DocuSign Connect can and does resend the same event
(documented retry behaviour), and a resend of an already-processed completion must not re-fetch
the document, re-upload it, or re-advance the status a second time.

## `Get_the_signed_document` — `documentId: 'combined'` — A-DS-9

DocuSign's own REST API (the platform this connector wraps) documents `documentId=combined` as
the sentinel value for "the whole envelope's documents as one combined PDF, including the
certificate of completion" — a standard, well-known DocuSign convention (E2: not this-project-
specific, but never exercised by a flow in this project before). The connector's own parameter
description ("Enter 'string(document ID)' to get a single document, or select a format") is
consistent with this but does not itself enumerate `combined` as a value, so this is recorded as
an assumption rather than treated as settled.

## `Upload_the_signed_pdf` — SharePoint `CreateFile` — A-DS-10

Two separate things are bundled under one register row, same shape as A-DS-1 (DocuSign's own
connector id):

1. **`connectorid`/`operationId`/parameter names are E3** — widely and consistently attested in
   published Power Automate flow exports for the first-party SharePoint connector's Create file
   action (`dataset` = site URL, `folderPath` = library path, `name` = file name, `body` = raw
   binary content) — not yet ground-truthed against this tenant's own connector catalogue. This
   is the FIRST use of the SharePoint connector anywhere in this solution; every other
   connector reference here (`rev_SharedDataverse`, `rev_SharedTeams`, `rev_SharedOutlook`,
   `rev_SharedDocuSign`) has at least one sibling flow already exercising it, this one has none.
2. **The response property read back for `rev_signedpdfurl`** (`body('Upload_the_signed_pdf')?['Path']`)
   is a guess at the response shape's property name; a `concat(folderPath, '/', fileName)`
   fallback is composed alongside it via `coalesce()` so a wrong or absent `Path` property still
   writes a usable (if potentially not-canonical) URL rather than leaving the column empty.

Both halves close the same way A-DS-2's did: open this action in the DEV designer against the
real `rev-sharepoint` connection and the real site/library, let the designer resolve the actual
parameter names and response shape, correct and save, then `pac solution export`/`unpack` and
reconcile per `skills/how-to-verify-a-platform-contract.md`'s three-direction diff procedure.
Until then this action is **authored, not verified** — V1/V2 only.

## New environment variables: `rev_SpoSiteUrl` (new) and `rev_SpoSignedAcceptanceUrl` (existing, now read)

`rev_SpoSignedAcceptanceUrl` was provisioned 2026-08-18 (WBS 0.4-R) but nothing read it until
now — this flow is that first reader, so its `isrequired` flag is corrected from `0` to `1` (see
`environmentvariabledefinitions/README.md`). `rev_SpoSiteUrl` is new: the SharePoint connector's
`dataset` parameter needs the site's absolute URL, which `rev_SpoSignedAcceptanceUrl` (a
server-relative library path) does not itself carry, and
`provisioning/sharepoint/ensure-site.ps1`'s own rule is one site collection PER environment
(never shared), so the site URL is genuinely environment-specific, not a constant that could be
hardcoded.

## `rev_escalatedon` is untouched by this flow

Completion does not clear or read the escalation stamp WBS 3.3 writes. If a grant escalates on
day 14 and is then signed on day 15, `rev_escalatedon` stays set — it is a historical record of
"this grant was once overdue," not a live flag, and nothing in TAD 5.9/5.10 asks for it to be
cleared. Recorded here as a deliberate non-decision, not an oversight.

## `Write_completion_status` — writes to the grant `Find_the_grant` resolved, not a trigger field

`recordId` reads `first(body('Find_the_grant')?['value'])?['rev_grantid']` — the grant record
found by envelope id — never a value invented off the trigger body. An early draft of this file
composed a `customFields.grantId` path that no action in wbs:3.2 ever writes to the envelope;
corrected before this revision was presented, since inventing a custom field this solution never
sets would have been exactly the kind of fabricated-identifier guess `C-TECH-051` forbids.

## What this flow deliberately does NOT do

- **No manual-acceptance handling.** `rev_manualacceptancerecorded`/`rev_manualacceptancenote`
  (FR-046) are written directly on the Grant record through the Model-Driven App, by design
  (TAD 5.10) — no flow, this one included.
- **No reminders or escalation.** That is flow #9 (WBS 3.3), built alongside this one but as a
  separate flow.
- **No TST/ACC or PRD wiring.** Same DocuSign-licence dependency as wbs:3.2/3.3; DEV-only until
  it closes.
