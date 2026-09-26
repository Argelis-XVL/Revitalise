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

## UPDATE 2026-09-25 — reviewer opened this flow in the live DEV designer; it would not save (E1, real ground truth)

Three verbatim designer errors, all on `When_the_envelope_completes` (the `CreateHookEnvelopeV4`
trigger this file's own A-DS-8 section already flagged as carrying one unconfirmed value). Same
class of finding as the Create Envelope flow's own designer failure, checked the same session.

**1 and 2. "'Name' is no longer present in the operation schema... remove it" (reported once on
"the relevant action's inputs", once specifically tied to the trigger's `events` property) —
RESOLVED as ONE finding, E1.** This flow's source has exactly one `name` property inside a
connector-operation's inputs: the trigger's own `"name": "REV Acceptance Completion"`, a sibling
of `events` in the same `parameters` object — which fits both descriptions at once (a trigger is
loosely "an action" in plain language, and it sits directly beside `events`). No second `name`
property exists anywhere else in this flow that plausibly matches (the only other candidate,
`Upload_the_signed_pdf`'s `name` parameter, is the SharePoint `CreateFile` action's own required
file-name input — a live, necessary, non-deprecated property for every published example of this
connector action; changing it on inference alone would trade a confirmed designer error for an
unconfirmed regression, so it is untouched). Removed the trigger's `name` property; `events` is
byte-for-byte unchanged, so A-DS-8's own still-open question (whether `"envelope-completed"` is
the connector's real resolved value) is neither re-guessed nor accidentally disturbed.

**3. "Connect configuration name is missing" — NOT independently resolved; DECLARED ASSUMPTION,
new register row A-DS-13.** The dispatch instruction asked this to be checked against this flow's
`connectionReferences` block versus Create Envelope's — done: the two blocks' `shared_docusign`
entries are byte-for-byte identical in shape (same `runtimeSource`, `connection.connectionReferenceLogicalName`,
`api.name`). There is no difference for a "matching shape" fix to produce, which rules out the
most direct route the instruction anticipated. The more coherent reading, combining errors 1/2
with error 3: DocuSign's own "Connect Configuration" is literally what `CreateHookEnvelopeV4`
creates, and the connector's current schema appears to have MOVED or RENAMED the property that
carries the configuration's own name, rather than dropped the concept — the old key (`name`) is
rejected (errors 1/2, now fixed), and something (unnamed) is required to supply the configuration
name (error 3). **No source in this session names the current key** — this is the same "no live
route to the connector's dynamic/resolved schema" gap A-DS-8 already lives in, one property over.
Rather than invent a replacement key (a guess with nothing to ground it, and the second such guess
in one finding, which is exactly the "stop guessing" line), the trigger is left with `accountId`
and `events` only. **This will very likely still fail to save on this specific error** until a
human opens the DEV designer and lets it resolve the actual required property for the Connect
configuration's name.

**New register row A-DS-13** (Dev Summary §10, to be added there by development-agent):

| ID | Assumption | Confidence | Basis | Verification | Status |
|---|---|---|---|---|---|
| A-DS-13 | `CreateHookEnvelopeV4`'s Connect-configuration-name parameter is NOT the removed `name` key; its current key/shape is undetermined from any source available this session | None — explicitly undetermined, not a placed guess | E1: the designer both rejects `name` (errors 1/2) and separately reports the configuration name missing (error 3) on the same trigger, which is only coherent if the concept moved rather than disappeared | Open `When_the_envelope_completes` in the DEV designer against the real `rev-docusign` connection, let it resolve the actual required property, add it, save, then `pac solution export`/`unpack` and reconcile (`skills/how-to-verify-a-platform-contract.md`) | **OPEN — named as a mandatory pre-activation step in `config/revitalise-grant-automation-pipeline.yml`'s DEV `post_deploy`, alongside A-DS-8/A-DS-9/A-DS-10** |

**A-DS-8 status: unchanged, still OPEN** — this update touches only the sibling `name` property,
not the `events` value A-DS-8 itself is about.

**Human open-and-save (V4) still required, and almost certainly still blocked.** Errors 1 and 2
are corrected against real E1 evidence; error 3 (A-DS-13) is explicitly NOT resolved and this flow
should be expected to still fail to save in the live designer until a human resolves A-DS-13
there directly — this fix narrows what the designer will complain about, it does not clear the
gate.
