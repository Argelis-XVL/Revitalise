# REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json - full descriptions

> **Read the last section first: "TAD rev 15 (2026-10-02)".** The flow no longer has
> `Create_and_send_the_envelope` or `Compose_template_tab_values`. Every section below that
> describes them (the `SendEnvelope` wire shape, `signers` keys, per-signer `tabs`, A-DS-12) is kept
> as history and no longer describes the source. The trigger, the three reads, the reminder cadence
> and the write-back sections still apply.

Same 256-character constraint as every other flow in this solution (see the Scoring flow's
notes.md). This file carries the reasoning the condensed on-file descriptions could not.

`wbs:3.2`, Automation #3, **DEV only**. Authorised by pm-agent's handoff quoting
`contract/known-exceptions.json` EX-006 (waives the 3.1 predecessor-review gate — the reviewer
built the DocuSign template himself) and EX-007 (acceptance-letter-template dependency satisfied
direct from Revitalise; DocuSign-licence dependency stays outstanding, so this authorises
DEV-only build/test against the existing DEV DocuSign connection, not a production promotion).

## Why this is the FIRST flow in this solution to trigger on `rev_grant`, not `rev_application`

TAD 5.7/5.8 together read *"Application/Grant status becomes Approved"*, which is ambiguous on
its face — `rev_applicationstatus` has a literal option 7 named "Approved", `rev_grantstatus`
has no option of that name. Resolved from source, not from re-reading the TAD sentence harder:

- `REV | Portal | Finalise Decisions` (flow #7, TAD 5.7) **creates Grant rows for approvals** —
  a Grant's very existence is the approval event.
- `rev_grantstatus.xml`'s own comment on option 1: *"Awarded. The board approved the application
  and the grant exists. Nothing has been sent to the applicant yet."* That is the "Approved"
  state the flow table's row is describing, for the Grant entity.
- `rev_grant/Entity.xml`'s own `rev_docusignenvelopeid` and `rev_acceptanceissuedon` descriptions
  both read *"Ships EMPTY... nothing writes it until WBS 3.2"* / *"Written by WBS 3.2"* — this
  task, by name, in source, from before this dispatch existed.
- `rev_grantstatus.xml`'s comment on option 2: *"Acceptance Issued... Set by WBS 3.2, which is
  not built yet."* — the same source assigns this flow the transition out of Awarded.

So the trigger is **Grant row CREATED** (default status 1, Awarded), and this flow's own
terminal write moves it to 2 (Acceptance Issued). This is source-grounded, not a blind guess —
but it was never spelled out as a trigger design anywhere, so it is still recorded as **A-DS-3**
in Dev Summary section 10 rather than treated as settled, because the compound sentence in TAD
5.7/5.8 could in principle have meant something else and no live test has confirmed this reading.

## `/properties/definition/triggers/When_a_grant_is_created`

`subscriptionRequest/message: 1` (Added — IMP-0406's own ground-truthed stringmap, read live from
`REV-GrantApplications-DEV` on 2026-08-28: 1=Added, not a row-updated value), `scope: 4` (org),
`runas: 3` (flow owner — IMP-0108's proven value; 4 packs and imports but registers no
`callbackregistration` and the flow never fires). None of these three values is new to this
project; they are the same constants `REV | Scoring | Calculate & Flag` already uses, copied
rather than re-derived.

## Reading a LOOKUP off a trigger body — new to this project (A-DS-3, continued)

Every existing flow in this solution triggers on `rev_application`, whose own primary key
(`rev_applicationid`) happens to share its name with the lookup attribute other tables use to
reference it — so `triggerOutputs()?['body/rev_applicationid']` in those flows reads the
**triggering row's own id**, never a lookup's target id. This flow is the first to read an
actual LOOKUP off a trigger body: `rev_grant.rev_applicationid` and `rev_grant.rev_providerid`
are both lookups, not primary keys. The Dataverse Web API's well-documented convention for a
bound lookup navigation property is `_<attributename>_value` (e.g. `_rev_applicationid_value`),
and that is what this flow reads. This is a widely and consistently documented Dataverse Web API
behaviour (E2: not this-project-specific, but never exercised by a flow in this repository), so
it is flagged rather than assumed silently. Cheapest verification: trigger the flow once in the
DEV designer with **Check Definition** / a test run, and read the raw trigger outputs pane
directly — no code change needed to check it, only a look.

## `Get_the_application`, `Get_the_applicant`, `Get_the_provider` — read by ListRecords, not Get-a-row-by-id

Deliberately NOT the connector's Get-a-row-by-id action, even though a real GUID is available in
every case here (unlike `IMP-0112`'s alternate-key misuse). Two independent reasons stack:

1. `IMP-0112`/the Scoring flow's own header comment record that this connector's Get-a-row-by-id
   action has already cost this project real production failures once (all 11 first runs of the
   intake flow), and the fix adopted project-wide was to standardise on `ListRecords` with a
   `$filter` for every read. Departing from that house pattern for this flow alone would
   reintroduce a class of risk this project has already paid to eliminate elsewhere, for a
   single-row read that costs nothing extra done the proven way.
2. No flow in this solution has ever used a "get single row" action of ANY name, so there is no
   ground-truthed `operationId` for one in this project's own history to copy — inventing one
   (an earlier draft of this file used `"GetItem"`) would be exactly the E3/E4 guess
   `skills/how-to-verify-a-platform-contract.md` warns against, for no benefit over the proven
   `ListRecords` route.

`Get_the_provider` sits inside `Skip_provider_lookup_if_none_is_set` because `rev_providerid` is
`RequiredLevel=None` on `rev_grant` (WBS 0.4 remainder) — a Grant can exist with no provider yet.
`Compose_provider_name` falls back to a placeholder string rather than failing the run over a
field the TAD does not make mandatory. A genuine READ FAILURE on the provider lookup (as opposed
to it being legitimately empty) still fails the whole run and reaches `Alert_on_failure` — the
same fail-closed shape every other flow in this solution uses for a failed upstream read, not a
special case invented for this flow.

## `Create_and_send_the_envelope` — the largest open assumption in this flow (A-DS-1, A-DS-2)

DocuSign's own connector reference (`https://learn.microsoft.com/connectors/docusign/`, fetched
2026-09-06) documents the action used here as **"Create envelope using template with
recipients"**, `operationId: SendEnvelope`, with a `signers` parameter described only as
*"dynamic — the signers of the document"*. That page does not — cannot, from documentation
alone — say what shape the connector's dynamic schema resolves to for THIS template
(`b832b15e-489d-4b13-a78b-0abef700803a`): a template's roles are read by the connector from
DocuSign at design time, in the flow designer, against the live template. No environment route
was available in this session to resolve that dynamic schema for real:

- `pac connection list` was attempted against the live, authenticated DEV connection
  (`REV-GrantApplications-DEV`) and produced no output before being stopped; no other command in
  this session's toolset reaches the connector's dynamic-schema resolution endpoint directly.
- Microsoft's own connector reference page is E2 evidence for the STATIC parameters
  (`accountId`, `templateId`, `status`, `emailSubject`, `emailBody` — all committed with
  confidence) and cannot be E1 evidence for the dynamic ones.

So `signers` is authored here as a plain JSON array of `{roleName, routingOrder, name, email}`
objects — the shape the DocuSign API itself documents for a template role assignment, and a
reasonable reading of "dynamic collection of signer objects".

**UPDATE, same day — the reviewer supplied the template's own anchor-tag table.** This is real
ground truth (the live template's own configured merge fields, quoted verbatim from
`b832b15e-489d-4b13-a78b-0abef700803a`), not documentation-level E2, and it resolves part of
A-DS-2 while leaving the rest exactly as open as before. Three separate things came out of it,
and they must not be blurred together:

1. **Role names.** The template's own role headers name the signers **"Grant Acceptor"** and
   **"Grant Referee"**, not the `"Applicant"`/`"Referee"` this file guessed from the TAD's prose
   description of the signing sequence. `roleName` is corrected to match. **This is still NOT
   promoted to VERIFIED** — the reviewer's anchor-tag documentation names the template's role
   headers, but nothing in this session has read those role names back from the connector's own
   dynamic schema resolution (the flow designer, against the live `rev-docusign` connection),
   which is the only E1 route for this specific claim (per `IMP-0614`). A-DS-2 stays OPEN until
   that designer step runs.
2. **Top-of-document merge fields ARE wired, from data this flow already reads.**
   `Compose_template_tab_values` sources `p_name` from the SAME expression already bound for
   Signer 1 (`first(body('Get_the_applicant')?['value'])?['rev_fullname']` — not re-derived),
   `p_amt`/`p_dates` straight off this run's own trigger body (`rev_amountawarded`,
   `rev_holidaystart`, `rev_holidayend` — `rev_grant` is the triggering entity, so no extra read
   was needed), and `p_type`/`p_venue` from two columns added to `Get_the_application`'s
   `$select`: `rev_breaktype` (Choice — "Holiday Type", `Entities/rev_application/Entity.xml`,
   `PhysicalName="rev_breaktype"`) and `rev_breaklocation` (Text — "Break Location or Activity",
   same file, `PhysicalName="rev_breaklocation"`, described in its own `<Description>` as
   **"Where the applicant wants to go... TRUSTEE-VISIBLE ON PURPOSE"**, which is exactly
   "Destination"). All four fields the reviewer named as presumably-available are in fact
   available on records this flow already reads or trivially extends to.
   `rev_breaktype`'s FORMATTED (label) value is read via the connector's own
   `<attribute>@OData.Community.Display.V1.FormattedValue` convention, with a fallback to the raw
   numeric value — this specific convention is E2 (documented, standard Dataverse connector
   behaviour) and has not been exercised by any flow in this project before now, so treat it as
   an unstated fourth sub-item of A-DS-2 rather than a settled fact.
3. **The per-signer personal-detail tabs (Title/First/Last/Phone/Email/Address/Town/Postcode for
   both signers) are deliberately left UNPOPULATED.** Several of them duplicate data this flow
   already holds (Signer 1's name and email, in particular), but whether the product intent is
   to prefill them for the signer to confirm, or leave them blank for the signer to type live, is
   a decision for the reviewer, not something to default silently. Recorded as a new, distinct
   open item in Dev Summary section 10 (NOT an `A-DS-n` row — it is a product decision, not a
   guessed platform contract) — see the Dev Summary revision for the exact wording.

## UPDATE, same session — Signer 2 (Grant Referee) prefill: the reviewer-accepted final design

`ADR-043` (architect-agent) recommended against adding ANY new schema for the referee's
Title/Address/Town-City/Postcode — those tabs have no `FR` behind them and a stored referee
address can go stale before signing anyway. The reviewer accepted that recommendation and
CO-002 is being closed as not needed. What's left is narrower than the original open item: **use
whatever referee data already exists in Dataverse, invent nothing.**

`rev_application`'s only referee columns are `rev_refereename`
([`Entity.xml#L1084`](src/solutions/RevitaliseGrantAutomation/Entities/rev_application/Entity.xml#L1084)),
`rev_refereeemail`
([`#L1100`](src/solutions/RevitaliseGrantAutomation/Entities/rev_application/Entity.xml#L1100))
and `rev_refereephone`
([`#L1116`](src/solutions/RevitaliseGrantAutomation/Entities/rev_application/Entity.xml#L1116)) —
confirmed by the reviewer directly against this file before writing the brief, and re-confirmed
here. `rev_refereephone` is added to `Get_the_application`'s `$select`. Against the template's
own Signer 2 anchor tags (`t2` Title, `f2` First name, `l2` Last name, `ph2` Phone, `j2` Job
title, `o2` Organisation, `e2` Organisation email, `a2` Address, `c2` Town/City, `pc2` Postcode,
`n2` Print name, `d2`/`s2` date/signature — platform-populated, not this flow's concern):

- **`ph2` ← `rev_refereephone`.** Clean match, no ambiguity.
- **`t2`, `j2`, `o2`, `a2`, `c2`, `pc2` — left BLANK, signer-entered, per `ADR-043`.** No
  Dataverse column backs any of these; inventing a placeholder value would be worse than an
  empty tab, since a signer reads a pre-filled field as already-checked.
- **`n2` ← `rev_refereename` (whole string). `f2`/`l2` left BLANK — new register row `A-DS-4`.**
  `rev_refereename` is one free-text column (the referee's name as the applicant typed it); the
  anchor table's own row for `n2` is documented as a **"Full Name tab"**, which is exactly what
  this column is, with no split needed. `f2`/`l2` are separate First/Last tabs and there is no
  reliable, general way to split an arbitrary free-text name into first/last components (a
  double-barrelled surname, a title embedded in the string, a name given "Last, First" — this
  project has no evidence of the actual data shape and splitting on the first space is a guess
  that WILL be wrong for some referees). Filling the one tab the data cleanly fits, and leaving
  the two it does not, is the choice made here — recorded as `A-DS-4` (Confidence: the mapping
  onto `n2` is solid; leaving `f2`/`l2` blank rather than attempting a split is a judgement call,
  not a platform-contract guess, and is exactly what was asked to be stated rather than assumed).
- **`e2` ← `rev_refereeemail`, WITH AN EXPLICIT LABEL-MISMATCH FLAG — new register row `A-DS-5`.**
  The template's own anchor table names this tab **"Organisation email"**; `rev_refereeemail`'s
  own displayname and description
  ([`Entity.xml#L1100`](src/solutions/RevitaliseGrantAutomation/Entities/rev_application/Entity.xml#L1100))
  both say only **"Referee Email"** — the applicant's own account of the referee's contact
  email, with no field anywhere distinguishing a personal address from an organisational one.
  Since `ADR-043` rules out adding a new column for this, and this is the only email Dataverse
  holds for the referee, it is used for `e2` here — but **this is an assumption that the two
  concepts coincide for this referee, not a confirmed fact**, and is recorded as such rather than
  treated as a clean match the way `ph2` is.

Both new rows sit alongside `A-DS-1/2/3` in Dev Summary section 10. Neither is a platform-contract
guess in the sense the others are (nothing here depends on an unread connector or template
schema) — they are judgement calls about how one Dataverse column maps onto one DocuSign tab,
made explicit rather than defaulted, per the reviewer's own instruction.

## What is still exactly as open as before — the connector wire shape (item 5, unchanged)

This is the one thing the anchor-tag table cannot settle: it says WHAT to populate, not HOW the
connector expects tab values structured on the wire. `Compose_template_tab_values`'s output and
Signer 2's new `tabs` object are both passed the same way, as a `tabs` parameter on
the `SendEnvelope` action — but `SendEnvelope`'s own documented parameter list (`accountId`,
`templateId`, `status`, `signers`, `emailSubject`, `emailBody`) **does not include a `tabs`
parameter at all**. Three live possibilities, none confirmed:

- `SendEnvelope` silently accepts an extra `tabs` property the reference page does not enumerate
  (some connectors do; some do not; this project has no evidence either way for this one);
- the correct action is actually **"Create envelope using template with recipients and tabs"**
  (`operationId: SendEnvelopeWithRecipientFields`), whose name explicitly promises tab support —
  not switched to here, because guessing a DIFFERENT operationId with the same confidence as a
  documented one would be a NEW, larger guess, not a smaller one, and its own parameter list
  (`accountId`, `templateId`, `recipients`, `merge_roles_on_draft`, `emailSubject`) is equally
  silent on where document-level (non-per-signer) fields like `p_amt`/`p_venue`/`p_dates` go;
- a second, follow-up call is needed after the envelope exists — `Update envelope prefill tabs`
  (`operationId: UpdateEnvelopePrefillTabs`) or `Update recipient tab values on an envelope`
  (`operationId: UpdateRecipientTabsValues`) — both of which key by `tabId` (a DocuSign-assigned
  identifier), which the anchor-tag table does not supply and this flow has no way to resolve
  without first reading the created envelope's own tab list back (`Get document tabs from
  envelope` / `Get recipient tabs from envelope`), a step this revision deliberately does NOT
  add, because doing so would be building a second unverified mechanism on top of the first
  rather than naming the gap plainly.

`Compose_template_tab_values`'s object is therefore a **placeholder wire shape** carrying
ground-truthed VALUES to the connector call, not a verified parameter. **This is the same V4 gap
named before, unchanged in kind, only smaller in what it still has to resolve** — the cheapest
verification is exactly what `skills/how-to-verify-a-platform-contract.md` calls for when no
live design surface is reachable: open this action in the DEV flow designer against the real
`rev-docusign` connection and the real template, let the designer resolve the actual action,
parameter names and per-role tab schema, correct this file to match, save, then
`pac solution export` + `unpack` and reconcile per the skill's three-direction diff procedure.
Until that happens this action — role names included — should be treated as **authored, not
verified** — V1/V2 only.

## `Write_the_envelope_id_and_issue_date`

Writes `rev_status: 2` as a literal, not a lookup into `rev_setting` — deliberately, because this
is a fixed lifecycle transition on a global option set (`rev_grantstatus`), the same class of
value `REV | Scoring | Calculate & Flag` writes literal status codes for, not a business
threshold FR-017/NFR-019 puts in the board's hands. `envelopeId` is read from
`body('Create_and_send_the_envelope')?['envelopeId']` per the DocuSign connector's own documented
`CreateEnvelopeResponse` shape (E2, same evidence class as the rest of the static parameters).

## `Alert_on_failure`

Same shape as every other flow's failure alert: passes the GRANT reference, never the row, to
`REV | Ops | Failure Alert` (workflow reference `8f1c2a44-1004-4b7a-9e21-0a1b2c3d4e04`, unchanged
from the existing child flow). A failure here leaves the grant at status 1 (Awarded) with no
envelope sent — the safe resting state, since nothing has reached the applicant yet.

## What this flow deliberately does NOT do

- **No OAuth binding.** The `rev_docusign` connection reference is bound to the existing DEV
  DocuSign connection as a manual `post_deploy` step (TAD section 12, line ~1644), out of scope
  for this dispatch per pm-agent's handoff.
- **No escalation or completion handling.** Those are flows #9 and #10 (WBS 3.3/3.4), not built
  here. **Reminders ARE now built here** — see the section below, added 2026-09-06 (`IMP-0618`
  resolution) — a correction to this flow's own original scope statement, which had reminders as
  entirely out of scope for the whole solution.

## `Read_reminder_days` / `Parse_reminder_days` / `Compose_reminder_cadence` / `Set_reminder_cadence` — IMP-0618 resolution, A-DS-11 (added 2026-09-06)

**The coordinator relayed a specific, checkable reviewer question, not a preference:** does the
DocuSign connector expose a way to set reminder cadence per-envelope, at send time, overriding the
template's own static configuration — and if so, use `rev_setting`'s seeded `[3,7]` and discard
the reviewer's own 2/5-day template values entirely.

Checked directly, not assumed either way: `Create_and_send_the_envelope`'s own action
(`SendEnvelope`) has no notification/reminder parameter of any kind — confirmed against its full,
documented parameter list. But the connector's action catalogue (same reference,
`learn.microsoft.com/connectors/docusign/`) separately lists `Add reminders for an envelope`
(operationId `AddReminders`), which does exactly what was asked: a per-envelope call, made after
the envelope exists, that sets `reminderEnabled`/`reminderDelay`/`reminderFrequency`/`expireAfter`.
This is a genuine dynamic-override path, distinct from a parameter on the create action — the
reviewer's question ("does the create action expose it") is answered NO; the broader question
("does a dynamic override path exist at all") is answered YES, one action later.

**`Read_reminder_days`** reads `Setting.ReminderDays` — `ListRecords` with a `$filter`, the house
pattern for this connector, never Get-a-row-by-id even keyed by `rev_name` (IMP-0112/IMP-0116).
**`Parse_reminder_days`** falls back to `[3,7]` — the TAD's own literal — if the row is ever
absent, same resilience choice as A-DS-6 (`EscalationDays`) on the wbs:3.3 flow.

**`Compose_reminder_cadence` is where the real platform-shape gap lives.** `AddReminders` takes a
`reminderDelay` (days after send to the FIRST reminder) and a `reminderFrequency` (days between
EVERY subsequent reminder) — there is no "send exactly two reminders, at day 3 and day 7, then
stop" primitive. `[3,7]` is read as `reminderDelay=3`, `reminderFrequency=4` (the gap between the
two configured days), which reproduces "day 3, day 7" as the first two firings but then keeps
repeating every 4 days after that — `expireAfter` bounds the whole envelope's lifetime, not just
the reminder count, so it cannot be used to stop reminders alone without also voiding the
envelope. This is a genuine, honestly-recorded platform limitation, not a guess about the wire
shape — recorded as part of `A-DS-11` below. **Reviewer-accepted 2026-09-06**: the repeat past
day 3/day 7, until WBS 3.3's escalation takes over at day 14, is confirmed as the intended
design, not a defect to work around.

**`Set_reminder_cadence`** calls `AddReminders` with `envelopeId` read straight off
`Create_and_send_the_envelope`'s own response (`envelopeId`, per `CreateEnvelopeResponse`, the
same E2 evidence class as the rest of that action's static parameters — no new guess here).
**Whether this override actually takes precedence over the template's own static 2/5-day setting
is asserted from DocuSign's own well-known platform model (envelope-level notification settings
override template-level ones), not yet confirmed live against this specific template and tenant**
— ground-truth the first time a real envelope is sent in DEV: read the envelope's actual
reminder configuration back (no connector action for this exists in the catalogue checked; the
DocuSign web UI's own envelope detail view is the fallback route) and confirm it shows 3/4, not
2/5.

**New register row:**

| ID | Assumption | Confidence | Basis | Verification | Status |
|---|---|---|---|---|---|
| A-DS-11 | **(b) CLOSED — reviewer-accepted 2026-09-06.** The repeat-every-4-days behaviour past day 3/day 7 (until wbs:3.4's escalation takes over at day 14) is the confirmed, intended design, not a defect. **(a) Still OPEN**: whether `AddReminders` actually overrides the template's static config, live, for this tenant | (b) Settled by reviewer decision; (a) E2/E3 - well-known DocuSign platform behaviour, not confirmed live against this template | (b) Reviewer confirmed the cadence `AddReminders`'s own parameter model produces from `[3,7]` is acceptable as designed; (a) DocuSign's precedence model for envelope- vs template-level notification settings is standard but unverified for this tenant | (a) only: send one real envelope in DEV, read its actual reminder configuration back (via the DocuSign web UI - no connector action for this was found in the catalogue checked), confirm the template's own setting is actually overridden | **PARTIALLY CLOSED — (b) CLOSED reviewer-accepted; (a) OPEN** |
- **No TST/ACC or PRD wiring.** EX-007 leaves the DocuSign licence dependency outstanding for
  those environments; this flow, its connection reference and its two environment variables are
  DEV-only artefacts until that dependency closes.

## UPDATE 2026-09-25 — reviewer opened this flow in the live DEV designer; it would not save (E1, real ground truth)

Three verbatim designer errors, all on `Create_and_send_the_envelope`. This is the live-designer
schema validation this file's own §"largest open assumption" section (A-DS-1/A-DS-2) said was
the only route that could settle the `SendEnvelope` wire shape — it has now partially settled it,
by disproof rather than confirmation, which is exactly as informative.

**1. "tabs of the sent envelope action is not part of the operation" — RESOLVED, E1.**
The top-level `tabs` parameter this file's own "what is still exactly as open as before" section
named as the first of three live possibilities is now confirmed WRONG: `SendEnvelope` does not
accept a top-level `tabs` property at all. Removed. **This closes that possibility outright** —
of the three candidates listed there, this is the one the designer has now ruled out with real
evidence, not documentation-level inference.

**2. "Signers is expecting an object and not an array" — RESOLVED, E1; the object's KEYING is a
declared assumption, still open.** The designer confirms `signers` must be a keyed object, not a
JSON array literal — `A-DS-2`'s original authoring (a plain array) is now known WRONG, not merely
unconfirmed. `signers` is re-keyed as `{"0": {...}, "1": {...}}` here — numeric-string keys are
this session's one best-effort guess at the actual key scheme the connector's resolved dynamic
schema uses; no live route in this session reaches that resolution (same gap A-DS-2 always named).
**New register row A-DS-12**: the numeric-string keys are UNVERIFIED and must be corrected to
whatever the DEV designer actually resolves them to, per the same "open the action, let the
designer resolve it, correct, save, export/unpack, reconcile" procedure A-DS-2/8/9/10 already use.

Because the top-level `tabs` parameter (item 1) is gone, the document-level merge fields
(`p_name`/`p_amt`/`p_type`/`p_venue`/`p_dates`, previously carried by that parameter) needed a new
home. Since the designer did NOT flag Signer 2's own nested `tabs` object as invalid, per-signer
`tabs` is inferred to be accepted — `Compose_template_tab_values`'s output is now wired as signer
`"0"`'s (Grant Acceptor's) own `tabs`, on the reasoning that document-level anchor tabs render
against whichever recipient's page context includes them, and the first/only-required signer is
the safest default. **This placement is UNVERIFIED and part of A-DS-12** — it may turn out these
fields need to sit elsewhere (e.g. split across both signers, or a still-different top-level
property this session has not found). Confirming it is the same DEV-designer step as the keying
question above, not a second, separate guess.

**3. "In the Apply-to-each over signers, the referee's name/email cannot be selected" — RESOLVED
by inspection; NOT independently re-verified live.** No `Apply-to-each`/`Foreach` exists anywhere
in this flow's source — `signers` has always been authored as a flat structure with the referee
(now `"1"`) reading `rev_refereename`/`rev_refereeemail` directly off `Get_the_application`'s own
output, never off an iteration item over the applicant collection. The reviewer's description of
"the loop" does not match anything in this source as it stands. The most likely explanation,
consistent with error 2: the designer's own UI, faced with an array where its resolved schema
expects an object, rendered `signers` using its generic "unrecognized array" editing surface,
which can present as a repeating/loop-like control and default its per-item pickers to whatever
collection the surface guessed at (plausibly `Get_the_applicant`'s `value` array, the nearest
array-shaped output in scope) — never actually the intended binding. Converting `signers` to the
correctly-typed object (fix 2) removes the array the confused rendering depended on. **This is
inference, not confirmation** — it is very plausible this designer symptom disappears as a side
effect of fix 2 rather than needing any change of its own, but that has not been observed live.
Flagged so the reviewer knows to specifically re-check the referee picker on re-open, not just
whether the flow saves.

**New register row A-DS-12** (Dev Summary §10, to be added there by development-agent):

| ID | Assumption | Confidence | Basis | Verification | Status |
|---|---|---|---|---|---|
| A-DS-12 | `signers` object keys are numeric strings (`"0"`/`"1"`); document-level template merge fields (`p_name`/`p_amt`/`p_type`/`p_venue`/`p_dates`) are carried inside signer `"0"`'s own `tabs`, not a top-level parameter | Low — a single best-effort correction after two live designer errors, not a resolved schema | E1 (designer confirms object, not array; designer does not flag per-signer `tabs` as invalid) for the shape class; the specific keys and field placement are inference, not read from the resolved schema | Open `Create_and_send_the_envelope` in the DEV designer against the real `rev-docusign` connection/template, let it resolve the real key names and confirm where the merge fields actually belong, correct and save, then `pac solution export`/`unpack` and reconcile (`skills/how-to-verify-a-platform-contract.md`) | **OPEN — supersedes the wire-shape half of A-DS-2, named as a mandatory pre-activation step in `config/revitalise-grant-automation-pipeline.yml`'s DEV `post_deploy`** |

**A-DS-2 status: role names half remains CLOSED as before (reviewer-supplied anchor-tag table);
the wire-shape half is superseded by A-DS-12 above, since two of its three named live
possibilities are now settled by real designer evidence rather than still being three open
guesses.**

**Human open-and-save (V4) still required.** These fixes are source-level corrections against
real E1 error text, not a live save — the reviewer must re-open this flow in the DEV designer and
attempt to save it again to confirm errors 1–3 are actually gone and no new one surfaces (the
`signers` object keying in particular is exactly the kind of thing the designer may still reject).

## Run history is secured (C-DOM-004, NFR-012; reviewer ruling 2026-09-30, IMP-0951, EX-004)

The reviewer ruled on 2026-09-30 that `rev_refereename`, `rev_refereeemail`, `rev_refereephone`, `rev_fullname` and `rev_email` are personal data. `rev_breaktype` and `rev_breaklocation` are not. Before this change nothing in this flow was secured, so the applicant's name and email and the referee's name, email and phone were readable in run history for 28 days by anyone with access to the flow, outside Dataverse's own column security.

`runtimeConfiguration.secureData.properties` is now set on every action that names one of those columns or reads a secured action's output, the same rule the intake flow follows (`IntakeContract.Tests.ps1`, ADR-051 item 7):

- `Get_the_application` and `Get_the_applicant`: `["inputs","outputs"]`. The first reads the referee's name, email and phone; the second's filter carries the applicant id read from the first.
- `Compose_template_tab_values`: `["inputs"]`, which also hides its outputs. It carries the applicant's full name.
- `Create_and_send_the_envelope`: `["inputs","outputs"]`. It carries both signers' names and emails and the referee's phone.
- `Find_the_failed_action`: `["inputs","outputs"]`, as in intake, because it reads `result()` of the scope holding the four actions above.

Left readable on purpose: `Set_reminder_cadence` and `Write_the_envelope_id_and_issue_date` read only `body('Create_and_send_the_envelope')?['envelopeId']`, a DocuSign-generated identifier, so a lost envelope can still be found from a run; and `Alert_on_failure`, which passes the grant reference and never a person. `Get_the_provider` and the two settings reads select no personal column. Protection does not propagate through a Compose, which is why each action carries its own setting.

Secured inputs and outputs are still available to later actions in the same run, so no expression changed. No column was newly secured, so C-DOM-033 needs no register row. Asserted by `src/tests/solutions/AcceptanceEnvelopeContract.Tests.ps1`. This is source-level only; that the DEV run history now shows redacted values is not yet observed (Dev Summary section 11).

## TAD rev 15 (2026-10-02) — draft, bind, fill, check, send (ADR-067 C1-C10 option A, ADR-068)

**Why.** The reviewer reported that the single `SendEnvelope` call can no longer create, fill and
send in one step. Emily Sheardown's test of 2026-10-02 found that a forwarded referee email could be
signed by someone else and recorded as the referee. The reviewer then directed (verbatim, 2026-10-02):
*"The whole point is that I gave the actions necessary to add to the current workflow "Rev acceptance
create envelope. Not a seperate flow. These steps would then land in the build the envelope scope."*
So the DocuSign operations from his DEV flow `TEST_Docusign` (v2c, designer-saved, never run) are now
inside `Build_the_envelope`, shaped by TAD rev 15 §5.8–5.10. **TAD rev 15 is at ARCHITECTURE REVIEW
REQUIRED and has not been approved; this is reviewer-directed implementation.**

**Unchanged:** the trigger, `Get_the_application`, `Get_the_applicant`, the provider lookup,
`Compose_provider_name`, `Read_reminder_days` / `Parse_reminder_days` / `Compose_reminder_cadence`,
the `UpdateRecord` write-back and the failure-detail / `Alert_on_failure` pattern.

### The sequence

| TAD 5.8 step | Actions | Operation | Note |
|---|---|---|---|
| 1 | `Read_acceptance_email_settings`, `Filter_applicant_email_setting`, `Filter_referee_email_setting`, `Compose_acceptance_email_texts` | `ListRecords` on `rev_settings`, 2 Query, Compose | `{subject, body}` per signer. `{grantReference}` becomes `rev_grant.rev_name`. A missing row gives empty text; invalid JSON fails here, before any draft |
| 1 | `Select_referee_phone_digits`, `Compose_referee_phone_digits` | Select over `range()`, Compose `join` | Keeps every digit, drops everything else, not only a fixed list of characters |
| 1 | `Set_referee_details_problem`, `Check_referee_details_are_present` | SetVariable, If (alert, Terminate) | Names the first missing item in words: a settings row, an empty subject or body, a subject over 100 characters, the referee's name, email, or a phone with fewer than six digits |
| 2 | `Compose_access_code`, `Compose_tab_values` | Compose | Code = last six digits. Tab values: awarded amount `N2`, dates `d MMMM yyyy`, keyed by Data Label and by placeholder text |
| 3 | `Create_the_draft_envelope`, `Set_draft_envelope_id` | C1 `CompositeTemplates` (`status: Created`) | Nobody is emailed by a draft |
| 4 | `List_the_envelope_recipients`, `Filter_the_applicant_signer`, `Filter_the_referee_signer` | C2 `GetRecipientStatus`, 2 Query | Ids are read from the draft by `roleName` |
| 7 (C5) | `Find_the_document` | C5 `ListTemplateDocuments` | The template's only document |
| — | `Set_draft_shape_problem`, `Check_the_draft_matches_the_template` | SetVariable, If (alert, Terminate) | Exactly one signer per role and one document |
| 5 | `Bind_the_applicant`, `Bind_the_referee` | C3 `UpdateEnvelopeRecipient` | Routing 1 / 2, own subject and body, `English UK (en_GB)`, no `phoneNumber` |
| 6 | `Require_referee_access_code` | C4 `AddVerificationToRecipient`, `Access Code` | |
| 7 | `Read_the_tabs` | C6 `GetEnvelopeDocumentTabs` | |
| 8 | `Select_tab_matches`, `Filter_tabs_to_fill`, `Select_tab_array` | Select, Query, Select | One `{tabType, tabId, value}` array |
| 9 | `Fill_the_tabs` | C7-A `UpdateEnvelopePrefillTabs` | Option A |
| 10 | `Re_read_the_tabs`, `Select_re_read_values`, `Select_found_tab_ids`, `Filter_missing_tabs`, `Filter_unfilled_tabs`, `Select_unfilled_tab_ids`, `Set_tab_fill_problem`, `Check_every_tab_was_filled` | C8 `GetEnvelopeDocumentTabs`, Selects, Queries, If (alert, Terminate) | Every expected tab found, and holding the value sent |
| 11 | reminder actions, `Set_reminder_cadence` | C9 `AddReminders` | Now on the draft, before the send |
| 12 | `Send_the_envelope` | C10 `SendDraftEnvelope` | |
| 13 | `Write_the_envelope_id_and_issue_date` | `UpdateRecord` | Status 1 → 2 only after the send |

### Where this source differs from `TEST_Docusign` v2c, and why

The reviewer's flow is E1 for operation ids, static parameter names and the literals the designer
writes. Its values are test artefacts. Each difference below follows TAD rev 15.

1. **Referee routing order is `2`**, not `1` (FR-042; ADR-067 design requirement 1).
2. **No `phoneNumber` on the referee.** It is an SMS delivery channel for the signing link, not a
   contact field (ADR-067 design requirement 3).
3. **The access code is the last six DIGITS** after every non-digit is removed. v2c took the last six
   characters of the raw value. A phone with fewer than six digits, or none, stops the run and
   alerts (ADR-068 item 4).
4. **Subjects and bodies come from the two settings rows**, not literals (ADR-068 item 3). v2c's
   applicant subject also carried the applicant's name; the rows substitute only the grant reference.
5. **Amount is `rev_grant.rev_amountawarded` formatted `N2`**, not the application's
   `rev_amountrequested`. **Dates are the grant's holiday start and end formatted `d MMMM yyyy`**, not
   the application's raw `rev_breakstart`/`rev_breakend` (ADR-067 design requirement 2).
6. **The applicant's name is `rev_fullname`**, as this flow already composed it, not
   `rev_firstname + ' ' + rev_lastname`.
7. **Reads stay house `ListRecords`** by primary key, not Get-a-row-by-id (IMP-0112). v2c's
   hard-coded record id is not copied.
8. **`secureData` on every action that carries personal data** (C2–C4, C6–C8 and each Select/Query
   after the draft; Composes inputs only). v2c secures nothing.
9. **The tab array is built with `Select`**, not `AppendToArrayVariable` inside a loop: a variable
   action cannot be secured (TAD 5.8).
10. **Tabs are matched by Data Label, then by placeholder text** within their owner (prefill or the
    referee). v2c switched on the placeholder `value` only.
11. **The document is the template's only document**, checked by count. v2c filtered on the file
    name `Grant Acceptance Form.docx` (ADR-067 design requirement 7).
12. **Signers are found with two Filter arrays, not a `Foreach` + `Switch`.** Same operations and the
    same `roleName` keys, but a missing or doubled role now stops the run before anyone is bound,
    where the loop would silently skip it (ADR-068 H2). It also avoids two containers in the scope.
13. **`ListTemplateDocuments` runs before the binding**, not after it, so the shape check can stop
    the run before any signer is bound. It is a read; the order of the calls that change the draft
    is the TAD's.
14. **Recipient ids are never typed in**: every `recipientId` reads `Filter_the_*_signer`. v2c's
    access-code action read the id from the bind action's response.
15. **The template and account ids stay environment variables** (C-TECH-047). v2c held DEV values
    as parameter defaults.
16. **Reminders (`AddReminders`) are set before the send.** v2c had no reminder call.
17. **A read-back check (C8) runs before the send.** v2c had none.
18. **Every template tab is filled, except signature, full name and sign date** (reviewer decision at code
    review, 2026-10-02, which overrides TAD §5.8 step 2; see the last section). *Withdrawn wording, retained:*
    "Only the TAD's expected tab set is filled (five prefill tabs and the referee's `n2`, `e2`, `ph2`)."

### Open platform contracts (Dev Summary §10)

- **A-DS-14** — the draft carries both template roles as placeholder signers; `UpdateEnvelopeRecipient`
  fills them rather than adding signers; `SendDraftEnvelope` sends the draft as filled.
- **A-DS-15** — whether tabs carry `tabLabel` and `recipientId` in the connector's read; which tabs
  are prefill; that the template's document id is the envelope's. `n2` is documented in the
  anchor-tag table as a *Full Name* tab. If DocuSign fills it from the bound name, the read-back
  still passes because the name sent is the same; if the read does not return it at all, C8 stops
  the run naming `n2`.
- **A-DS-16** — option A updates recipient tabs; which `tabType` string the update accepts (the read's
  own value is passed through, per §12.5 R3); `English UK (en_GB)` is accepted; `AddReminders` works
  on a draft.
- **A-DS-17** — a six-digit code conforms to the account's access-code format, and the link asks for it.
- **A-DS-18** — an envelope from a template whose *Allow recipients to change signing responsibility*
  option is off inherits it. No connector action can set it (ADR-068 item 2); it is a template or
  account setting, checked by §12.5 M4 and M6.

### What a person sees when it stops

- **Before the draft** (`Check_referee_details_are_present`, or any failure up to
  `Create_the_draft_envelope`): nobody is emailed and nothing exists in DocuSign. The process owner's
  alert names what is missing.
- **After the draft, before the send**: nobody is emailed. The alert names the draft's envelope id so
  it can be deleted in DocuSign (risk A-R74). A re-run makes a new draft.
- **After the send**: `Write_the_envelope_id_and_issue_date` is the only action left. If it fails, the
  envelope has gone out and the alert says so ("Unless Send_the_envelope succeeded it is an unsent
  draft").

### Run history

Unchanged rule, wider set. See the "Run history is secured" section above for the reasoning.
Secured `["inputs","outputs"]`: `Get_the_application` and `Get_the_applicant`, `Select_referee_phone_digits`,
`List_the_envelope_recipients`, both signer filters, both binds, `Require_referee_access_code`, both tab
reads, `Fill_the_tabs`, every Select and Query after the draft, and `Find_the_failed_action`. Secured
`["inputs"]`: `Compose_referee_phone_digits`, `Compose_access_code`, `Compose_tab_values`. Left
readable: the settings reads and `Compose_acceptance_email_texts` (no personal value),
`Create_the_draft_envelope`, `Find_the_document`, `Set_reminder_cadence`, `Send_the_envelope` and the
write-back (they read only the envelope id, from the variable `draftEnvelopeId`), and every alert. The
three `Set_*_problem` variables carry words only, never a value; a variable action cannot be secured
and does not need to be here.

Asserted by `src/tests/solutions/AcceptanceEnvelopeContract.Tests.ps1`, which also executes the guards,
the access code and the tab matching on chosen inputs through `_harness/WdlExpression.psm1`.

## Code-review revision (2026-10-02) — every tab filled, matched without assuming which signer holds which set

**Reviewer decisions, verbatim, 2026-10-02:**

- *"The array with tabs are all the tabs on the template. Skipping them is not ok. They should all be populated by
  the workflow. Except the signer full name, sign date and signature for both recipients."*
- *"It's a checkbox for the applicant. Not the referee. To agree with the grant."*
- *"On the template there are pre-fill tabs, acceptor tabs and referee tabs. In this order."*

These override TAD §5.8 step 2's tab set. The TAD is architect-agent's to amend; it is not edited here.

**Why the matching does not assume a role.** The reviewer's pasted `GetEnvelopeDocumentTabs` output groups tabs by
type, under two recipient ids. The checkbox statement puts the group holding the checkbox on the applicant; the
layout statement can be read the other way. So the flow does not depend on knowing it. **Both roles accept the union
of placeholders, both spellings included.** The role, resolved at run time from `GetRecipientStatus` (`roleName` →
`recipientId`), decides only which Dataverse value a matched placeholder gets. Which recipient group carries which
placeholder set is unmeasured and is read on the first DEV run (A-DS-15).

**What is sent.** Every tab except `signHereTabs`, `fullNameTabs`, `dateSignedTabs` and `tabGroups`.
`Compose_connector_tab_types` is the one place the read's tab type meets the connector's enum, and it holds the
never-send list. A tab group is a validation group: it holds no value, and the connector enum is not known to accept
it, so it is not sent (A-DS-16). Any other tab the flow cannot map stops the run before the send, naming its
placeholder text, because the reviewer requires every tab to be filled.

| Role | Tab (placeholder, or tab type) | Source | Notes |
|---|---|---|---|
| prefill | Name | `rev_applicant.rev_fullname` | |
| prefill | Amount | `rev_grant.rev_amountawarded`, `N2` | awarded, not requested |
| prefill | Holiday type | `rev_application.rev_breaktype`, formatted | |
| prefill | Holiday destination | `rev_application.rev_breaklocation` | |
| prefill | Dates | `rev_grant.rev_holidaystart` – `rev_holidayend`, `d MMMM yyyy` | |
| Grant Acceptor | First name / Last name | `rev_firstname` / `rev_lastname` | column-secured |
| Grant Acceptor | Title | `rev_title`, formatted label | column-secured |
| Grant Acceptor | Email; `emailAddressTabs` | `rev_email` | |
| Grant Acceptor | Phone | `rev_phone` | |
| Grant Acceptor | Postcode | `rev_postcode` | |
| Grant Acceptor | Address / Adress | `rev_addressline` + ", " + `rev_addressline2` when present | |
| Grant Acceptor | Town/City / City/Town | `rev_towncity` | |
| Grant Acceptor | Job title; `companyTabs` | `""` | no column |
| Grant Acceptor | `checkboxTabs` | `false` (unticked) | the grant agreement; never ticked by the flow |
| Grant Referee | First name / Last name | `rev_refereename`, split at the first space | one-word or empty name: last name `""`. Last name is `join(skip(split(name,' '),1),' ')` — the earlier `substring(name+' ', indexOf+1)` started at `length` for a one-word or empty name and failed the whole `Compose_tab_values` (2026-10-03) |
| Grant Referee | Email; `emailAddressTabs` | `rev_refereeemail` | |
| Grant Referee | Phone | `rev_refereephone`, as typed | |
| Grant Referee | Title, Postcode, Address / Adress, Town/City / City/Town | `""` | ADR-043, no column |
| Grant Referee | Job title; `companyTabs` | `""` | no column |
| Grant Referee | `checkboxTabs` | `false` (unticked) | only if a checkbox turns out to sit on the referee |
| either | `signHereTabs`, `fullNameTabs`, `dateSignedTabs` | not sent | reviewer |
| either | `tabGroups` | not sent | no value; validation group |

`""` clears the template's placeholder text so the signer types the value. The read-back requires the five prefill
tabs and, for each signer, first name, last name, title, postcode and phone (the tabs both placeholder sets share).
Every other tab is covered by the no-mapping stop, and every tab sent must hold the value sent. A checkbox is read
back from `selected`, lower-cased.

**A new pre-send check.** The applicant's email and first name must be readable. Every applicant column above is
column-secured (`REV_TrusteeRestricted`), so if the service identity is not a member of that profile they read empty
and the tabs would be cleared silently; the run now stops instead and says so.

**Register effect.** `A-DS-4` (leave the referee's first/last name blank) is closed by the reviewer's decision to
split the name. `A-DS-5` stands: `rev_refereeemail` now fills the referee's email tabs. `A-DS-15` gains the
role-to-placeholder-set question; `A-DS-16` gains the `Checkbox`, `Company` and `EmailAddress` enum strings, the
checkbox's `selected` read-back, and whether an `emailAddressTabs` update is honoured.
