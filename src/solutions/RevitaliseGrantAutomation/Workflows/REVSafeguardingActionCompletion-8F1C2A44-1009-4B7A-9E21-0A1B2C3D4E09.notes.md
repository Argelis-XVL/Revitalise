# REVSafeguardingActionCompletion-8F1C2A44-1009-4B7A-9E21-0A1B2C3D4E09.json — full descriptions and the open assumption

Power Automate caps every `description` field (flow, trigger, action, parameter, schema
property) at 256 characters — exceeding it blocks the flow from being saved in the designer at
all. The descriptions actually shipped in this file keep the essential fact; the fuller
reasoning is here, keyed by the same JSON path.

---

## Why this flow exists at all

EF-27 (`docs/plans/emily-review-feedback-2026-09-plan.md:1082`), from the reviewer's (Anna
Southern) post-deployment feedback sheet, row 31: *"The field is there, but when I select yes
the date field (safeguarding completed on) and the safeguarding completed by fields are not
populated."*

Before building anything, the columns were checked rather than assumed absent (the plan's own
instruction, since the reviewer confirmed only the checkbox exists). They were not absent:

- `rev_safeguardingactioncompleted`, `rev_safeguardingactioncompletedon` and
  `rev_safeguardingactioncompletedby` are all declared in
  `Entities/rev_application/Entity.xml` (added in an earlier, uncommitted pass — the comment
  immediately above them already reads *"the date is set by the platform on tick and is
  read-only on the form"*).
- All three are `IsSecured=1` in `FieldSecurityProfiles.xml`, same basis as
  `rev_safeguardingflag`/`rev_safeguardingnotes`.
- `rev_safeguardingactioncompletedby`'s lookup-to-systemuser relationship is already registered
  in `ensure-schema-helpers.psm1`'s `Get-RevSyntheticRelationship` allowlist (same shape as
  `rev_overriddenby`).
- All three controls are already placed on the Casework tab's Safeguarding section in
  `Entities/rev_application/FormXml/main/{6a6004bd-bba9-498b-8ca4-fafdd254bded}.xml`.

**Two real defects, not one.** The reviewer's report is precise: the checkbox works, the other
two fields do not populate. Reading the FormXml found why, in two parts:

1. `rev_safeguardingactioncompletedon` and `rev_safeguardingactioncompletedby` were both
   `disabled="false"` — editable, not read-only, contradicting the column's own Entity.xml
   comment and the plan's explicit requirement ("read-only on the form, so it cannot be
   backdated"). Fixed in the same dispatch as this flow, in the FormXml file above — both now
   `disabled="true"`, matching `rev_scoredon`'s existing read-only pattern.
2. **Nothing wrote either field at all.** No flow in this solution referenced
   `safeguardingactioncompleted` before this dispatch (`grep -c` over every `Workflows/*.json`
   returned 0 for all eight existing flows). The column comments promised a mechanism; the
   mechanism did not exist. This flow is that mechanism.

This is a `declared-policy-not-mechanically-enforced` shape: the Entity.xml comment stated the
intended behaviour, the schema and the security model were built to support it, and the one
piece that makes it true — a flow, a business rule, or a plugin — was never added. Logged as an
improvement finding; see the paired Dev Summary revision for the id.

---

## Design choice: which existing mechanism this follows

The plan's own instruction was to find what this project already uses for "platform sets a date
on tick, read-only on the form" rather than invent a new mechanism. Two candidates existed and
were checked, not assumed:

- `rev_overriddenon` (Override section) — **not this shape**. It is entered by hand by the
  process owner; nothing in this solution sets it automatically, and its form control is not
  disabled. EF-27's own spec text explicitly rules this column out as a model to imitate
  ("Specifically not `rev_decisiondate`... nor `rev_overriddenon`").
- `rev_scoredon` (Scoring section) — **this is the real precedent.** It is written by
  `REVScoringCalculateAndFlag`'s `UpdateRecord` action (`item/rev_scoredon: @utcNow()`) and its
  form control carries `disabled="true"`. Same "platform writes it, form cannot" shape EF-27
  asks for.

This flow follows `rev_scoredon`'s pattern: a Dataverse row trigger, `UpdateRecord` with
`item/<column>: @utcNow()`, and a disabled form control — not a business rule, not a plugin.
Power Automate is the only automation mechanism this solution has ever used for a
platform-set field; nothing here introduces a new one.

**Why a separate flow rather than extending an existing one.** Every existing Dataverse-
triggered flow in this solution fires on a different condition than "the safeguarding checkbox
was just ticked": `REVScoringCalculateAndFlag` fires on Create only (a re-fire on every edit
would fight its own override guard — see its own trigger description), and
`REVPortalRoundStatistics` triggers on a different table entirely. Folding this into either
would mean adding an Update trigger to a flow whose whole design deliberately excludes one, or
reading `rev_application` fields from a flow scoped to `rev_roundstatisticsrequest`. A new,
narrowly-scoped flow keeps each trigger's contract exactly what its own file already documents.

---

## `/properties/definition/triggers/When_the_application_is_modified/description`

Row MODIFIED on `rev_application`. `message: 3` is the same enum value already ground-truthed
live 2026-08-28 for `REVPortalRoundStatistics` (`callbackregistration` option set; `2` is
Deleted) — read from a real Dataverse instance, not re-guessed for this flow. `scope: 4`,
`runas: 3` copy the same two other Dataverse-triggered flows in this solution already use.

**This trigger fires on every field edit to every application, not only a safeguarding tick.**
That is deliberate and matches how `REVPortalRoundStatistics` and every Modified-trigger flow in
this solution already behaves — Dataverse offers no "fire only when column X changes" filter on
this trigger shape in this solution's existing usage (no flow here declares a
`subscriptionRequest/filteringattributes` parameter). The `If` guard immediately inside the
flow, not the trigger, is what makes an irrelevant edit (and the write this very flow performs)
a no-op.

---

## `/properties/definition/actions/Check_the_action_was_just_ticked/actions/Set_the_completion_date_and_owner/description` — A-SG-1 (OPEN)

**The guess.** `item/rev_safeguardingactioncompletedby` is set from
`triggerOutputs()?['body/_modifiedby_value']` — reading the trigger row's own `_modifiedby_value`
lookup reference, on the reasoning that at the instant the checkbox is ticked and saved, the
record's `modifiedby` **is** the person who ticked it. `_modifiedby_value` is the documented
Dataverse Web API convention for a lookup column's raw value (the same `_<name>_value` shape
already relied on informally throughout this project's knowledge of the platform), and
`modifiedby` itself is confirmed to exist on `rev_application` — visible as `"modifiedby"` in
the Trustee Portal's own live-exported connector schema,
`src/code-apps/trustee-review-portal/.power/schemas/dataverse/applications.Schema.json:90`.

**What is NOT ground-truthed.** Whether Dataverse's `SubscribeWebhookTrigger` webhook payload
for `rev_application` actually includes `_modifiedby_value` in the row body it hands to this
specific flow, in this tenant, without an explicit column selection — no flow in this solution
declares a `subscriptionRequest/select` (or equivalent) parameter today, so the working
assumption is that the trigger returns the full row, matching every other flow's unfiltered
read of `triggerOutputs()?['body/...']`. This has not been confirmed against a real trigger fire
for this flow, because no environment was available to this dispatch to create one (Hand-
Authoring Platform Artefacts step 1 — ground truth beats inference, but only when an environment
exists to get it from).

**Close this the moment DEV exists for this flow.** Tick the checkbox on a real application as a
signed-in user other than the flow's own service account, then read
`rev_safeguardingactioncompletedby` back and confirm it names that user, not the service
account and not empty. If it is empty or wrong, the fallback is
`triggerOutputs()?['body/_ownerid_value']` (record owner) or a `Get_a_row_by_ID` on the
`systemusers` table keyed by whatever identity claim the payload does carry — do not guess a
second time without checking the raw trigger payload first (Hand-Authoring Platform Artefacts
step 2: two failed guesses is the signal to stop guessing).

---

## `/properties/definition/actions/Check_the_action_was_just_ticked/description`

The loop guard, spelled out in full: this flow's own `UpdateRecord` action is itself a Modify of
`rev_application`, so without a guard this flow would re-trigger itself indefinitely. The guard
is the `rev_safeguardingactioncompletedon`-is-empty test, not a `filteringattributes` restriction
on the trigger (this solution has no precedent for that parameter — see the trigger note above).
On the second and every subsequent Modified trigger after the write, the date is no longer
empty, the `If` condition is false, and the flow takes the empty `else` branch and ends. This is
the same shape `Stop_if_the_process_owner_has_overridden_this_application` uses in
`REVScoringCalculateAndFlag` (a state-based short-circuit at the top of the flow), applied here
to a boolean-plus-timestamp pair instead of a single override flag.

---

## `/properties/definition/actions/Check_the_action_was_just_ticked/actions/Alert_completion_write_failed/description`

Same fail-closed reasoning as every other write in this solution: if the `UpdateRecord` fails
after retries, the checkbox is left ticked with no completion date — an application a
caseworker can immediately see is *"ticked but not evidenced"*, never a silent, wrongly-dated
write. Alerts through the shared `REV | Ops | Failure Alert` child flow
(`8f1c2a44-1004-4b7a-9e21-0a1b2c3d4e04`), the same mechanism every other flow in this solution
uses, and terminates the run as Failed so a monitoring view never reads this as a clean success.
