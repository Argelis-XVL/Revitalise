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

**UPDATED 2026-09-24 (C-TECH-055 build halt, wbs:0.4).** This trigger previously fired on every
field edit to every application, matching how `REVPortalRoundStatistics` and every other
Modified-trigger flow in this solution behaves — no flow here had declared a
`subscriptionRequest/filteringattributes` parameter. Re-verifying the `If` guard against the
live Solution Checker's `flow-avoid-recursive-loop` finding found that firing on every edit,
not just the loop-guard reasoning, was itself the real gap: it let an unrelated edit to the same
row (by a different user) race this flow's own completion write and pass the guard before that
write landed — see the detailed trace in the `Check_the_action_was_just_ticked` section below.

The trigger now declares `subscriptionRequest/filteringattributes: "rev_safeguardingactioncompleted"`
(the Dataverse connector's "Select columns" trigger condition), so it fires only when that
specific column is part of the changed-attribute set of the update — the first flow in this
solution to use this parameter. This is a deliberate, documented departure from the sibling
flows' pattern, not an inconsistency: `REVPortalRoundStatistics` and `REVScoringCalculateAndFlag`
never write back to their own trigger row's watched condition the way this flow's own
`UpdateRecord` does, so they never needed this. The `If` guard inside the flow is kept as a
second, independent layer — see below.

---

## `/properties/definition/actions/Check_the_action_was_just_ticked/actions/Set_the_completion_date_and_owner/description` — A-SG-1 (CLOSED 2026-10-09)

**Closed against DEV, not inferred.** The reviewer reported that this flow always had the
wrong binding after import and would not turn on, and fixed the binding by hand in DEV. A
read-only `pac solution export` of `RevitaliseGrantAutomation` from `REV-GrantApplications-DEV`
(2026-10-09, re-exported after the reviewer's second hand edit) returned the live definition, and the source now carries exactly its binding:

```
before (source):  "item/rev_safeguardingactioncompletedby": "@triggerOutputs()?['body/_modifiedby_value']"
first DEV fix:    "item/rev_safeguardingactioncompletedby@odata.bind": "/systemusers(@{triggerOutputs()?['body/_rev_safeguardingactioncompletedby_value']})"
DEV (live, now):  "item/rev_safeguardingactioncompletedby@odata.bind": "/systemusers(@{triggerOutputs()?['body/_modifiedby_value']})"
```

The shape is the fix: a lookup column is written as `item/<column>@odata.bind` with a
`/<entityset>(<id>)` value, never as a raw GUID under the bare column name.

**What the DEV diff showed.** Comparing the DEV definition to source, the only definition
differences were (1) this binding, (2) the root `definition.description` (the platform does not
round-trip it), and (3) JSON key order and trigger/action `description` text on the export (the
platform keeps those; no semantic difference). In the solution `customizations.xml` this flow
was `StateCode 0` (draft/off) in DEV at export time, while 8 of the 11 flows were `StateCode 1`
(the other two off are `Intake | WordPress to Dataverse` and `Scoring | Daily Summary`). That fits the reviewer's report that the
flow "doesn't turn on": the activation check rejects the invalid raw-GUID lookup binding. The
export cannot prove the cause by itself, so treat "invalid binding blocks activation" as the
best-supported explanation and confirm it on the next import (the flow should arrive on).

**Who is recorded: the row's modifier, per reviewer.** The first DEV fix read
`_rev_safeguardingactioncompletedby_value`, the column this flow is about to fill, which is empty
on the first tick and so recorded no one. The reviewer then changed DEV to read the row's
`_modifiedby_value`, the user who saved the tick. Source ports that binding exactly. Read-back of
`rev_safeguardingactioncompletedby` after a real tick by a non-service-account user is still the
V-level evidence; nothing in this dispatch has fired the trigger.

**UPDATED 2026-10-09 (reviewer: the flow "can run into a loop", needs guarding).** The trigger now
also carries a trigger condition (`conditions`), so a run is not even created unless the
checkbox is true AND `rev_safeguardingactioncompletedon` is empty:

```
@and(equals(triggerOutputs()?['body/rev_safeguardingactioncompleted'], true),
     empty(coalesce(string(triggerOutputs()?['body/rev_safeguardingactioncompletedon']), '')))
```

Three layers now: (1) the column filter, (2) this trigger condition, (3) the inner `If`. The
flow's own write sets the date, so the condition is false for any event that write causes.
**What the Solution Checker keys on.** Repository measurement, not assumption
(`knowledge/technology/build-and-deploy.md`, IMP-1090/1091): `flow-avoid-recursive-loop` fires
once per write to the trigger's own table and ignores the filter. Whether it also ignores a
trigger `conditions` block has NOT been measured (the checker is live-service only and runs at
the build's `lint` step). So this condition is a real runtime guard that the platform enforces;
it is not promised to silence the checker. If the checker still reports the rule at lint, the
disposition is accepted-with-rationale, decided from the trigger condition and the filter
against the written columns.

---

## `/properties/definition/actions/Check_the_action_was_just_ticked/description`

The loop guard, spelled out in full: this flow's own `UpdateRecord` action is itself a Modify of
`rev_application`, so without a guard this flow would re-trigger itself indefinitely. The guard
is the `rev_safeguardingactioncompletedon`-is-empty test. On the second and every subsequent
Modified trigger after the write, the date is no longer empty, the `If` condition is false, and
the flow takes the empty `else` branch and ends. This is the same shape
`Stop_if_the_process_owner_has_overridden_this_application` uses in `REVScoringCalculateAndFlag`
(a state-based short-circuit at the top of the flow), applied here to a boolean-plus-timestamp
pair instead of a single override flag.

**C-TECH-055 build halt (2026-09-24) — this guard was re-verified, not rubber-stamped, and a
real gap was found and closed.** The live Solution Checker flagged rule
`flow-avoid-recursive-loop` (Medium) on this flow. The question is not "does the guard read
correctly" (it does) but "does it hold under every timing, including a partial write and a
race between two triggers on the same row." Each was traced against the actual JSON:

1. **Normal case — guard is sufficient.** Tick → trigger fires, guard true (checkbox true, date
   empty) → `Set_the_completion_date_and_owner` writes both fields → that write is itself a
   Modify, so a second trigger fires → guard now false (date no longer empty) → `else` (empty)
   → flow ends. Self-terminating exactly as designed.

2. **Partial write (one field written, not the other) — not a real risk, on Dataverse's own
   documented semantics, not assumed.** `Set_the_completion_date_and_owner` is a single
   `UpdateRecord` action, which the Dataverse connector issues as one `PATCH` request against
   one row. Per Microsoft's Web API documentation ("Update and delete table rows using the Web
   API"), a single `PATCH` request is one write to one entity — there is no per-attribute
   partial-commit inside one request; it either lands with every attribute in the payload or it
   fails and none do (a genuine multi-request partial commit exists only across an explicit
   `$batch`/change-set or `ExecuteTransactionRequest`, which this action is not). A timeout
   after the server has actually committed can make the *connector* report Failed when the
   *row* already has both fields — but the connector's retry then reissues the identical
   idempotent `PATCH` (`@utcNow()` re-evaluates to a few seconds later, `_modifiedby_value` is
   unchanged), which does not corrupt the pair and still lands both fields together. No gap.

3. **Race — two Modified triggers on the same row both pass the guard before either write
   lands. This WAS a real, narrow gap, and it is the one this dispatch closes.** Before this
   fix, the trigger fired on *any* edit to `rev_application` (no `filteringattributes`). Sequence:
   caseworker ticks the checkbox (transaction A, `modifiedby` = caseworker) → trigger A fires,
   reads `rev_safeguardingactioncompletedon` as empty (write hasn't landed yet), guard passes.
   Before A's `UpdateRecord` completes, a second, unrelated edit lands on the same row —
   anything: a caseworker note, an address correction, a portal sync — made by a *different*
   user (transaction B). Trigger B fires because the old trigger had no column filter; its
   payload also shows the checkbox true (already committed by A) and the date still empty (A's
   write still in flight), so guard B *also* passes. Two `UpdateRecord` calls race: worst case,
   B's write lands last and stamps `rev_safeguardingactioncompletedby` with the *unrelated
   edit's* user, not the caseworker who actually ticked the box — a wrong attribution on a
   safeguarding record, which is exactly the kind of thing this column exists to get right.
   This is a genuine check-then-act (TOCTOU) race the date-empty guard alone cannot close,
   because both readers observe "empty" before either writer commits.

4. **Self-catching its own write before the guard re-evaluates correctly — not a risk, given
   point 3's fix.** With the trigger now filtered to fire only when
   `rev_safeguardingactioncompleted` itself is part of the changed-attribute set (point 5
   below), the flow's own write — which touches only `rev_safeguardingactioncompletedon`/`by`,
   never the checkbox — does not create a new trigger event at all. The guard is not "re-checked
   quickly enough"; the retrigger this rule warns about now cannot occur.

**The fix, applied to this file.** Two independent, complementary changes:

- **Trigger scoped with `subscriptionRequest/filteringattributes: "rev_safeguardingactioncompleted"`**
  (the Dataverse connector's "Select columns" trigger condition — see
  `docs/development/revitalise-grant-automation-dev-summary.md` §11 for the citation). This is a
  genuinely new pattern for this solution (no other flow here declares it — the trigger note
  above previously said so, and that absence was the gap, not a reason to leave it unscoped).
  Per Microsoft's own documentation for this trigger, the flow now runs only when an update
  request includes that column — which both (a) means the unrelated-edit race in point 3 can no
  longer fire the flow at all, since B's transaction never touches the checkbox column, and (b)
  means the flow's own completion write (date/owner only) never re-fires it, closing point 4
  outright rather than relying on the date field re-evaluating correctly on a second pass.
  Lookup columns are not supported by this filter, but `rev_safeguardingactioncompleted` is a
  Boolean (Two Options) column, so this is a supported use of the parameter.
- **The date-empty guard is kept, not removed** — it is the second, independent layer, and it is
  still the correct defense against the one race the column filter does not fully rule out: two
  users both ticking the checkbox itself in the same narrow window. (Dataverse's optimistic
  concurrency also means one of two truly simultaneous writes to the same row will be rejected
  and retried by the platform, further narrowing this; a belt-and-braces `Scope`-level
  concurrency control was considered and rejected as unnecessary complexity once the trigger is
  column-scoped, since the remaining race is between two legitimate, different tickers of the
  same box, which is a business edge case — "who completed it, if two people click it near-
  simultaneously" — not a data-integrity or infinite-loop risk.)

**A-SG-1 is CLOSED** (binding shape and modifier source per reviewer, 2026-10-09); see that
section above. This fix answers the separate loop-safety question.

---

## `/properties/definition/actions/Check_the_action_was_just_ticked/actions/Alert_completion_write_failed/description`

Same fail-closed reasoning as every other write in this solution: if the `UpdateRecord` fails
after retries, the checkbox is left ticked with no completion date — an application a
caseworker can immediately see is *"ticked but not evidenced"*, never a silent, wrongly-dated
write. Alerts through the shared `REV | Ops | Failure Alert` child flow
(`8f1c2a44-1004-4b7a-9e21-0a1b2c3d4e04`), the same mechanism every other flow in this solution
uses, and terminates the run as Failed so a monitoring view never reads this as a clean success.
