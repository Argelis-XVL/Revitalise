# REVAcceptanceRemindersEscalation-8F1C2A44-1007-4B7A-9E21-0A1B2C3D4E07.json - full descriptions

Same 256-character constraint as every other flow in this solution. This file carries the
reasoning the condensed on-file descriptions could not.

`wbs:3.3`, Automation #3, **DEV only**. Authorised by pm-agent's handoff quoting
`contract/known-exceptions.json` EX-006/EX-007 (both already cover wbs:3.1-3.4; only the
DocuSign-licence dependency remains outstanding for TST/ACC/PRD, unaffected here). Build/deploy
for 3.2+3.3+3.4 is held as a batch pending the reviewer's go-ahead — this dispatch produces
source only, same shape as the wbs:3.2 revisions before it.

## Reminders: RESOLVED 2026-09-06 (`IMP-0618`) — flow-driven from `rev_setting`, but NOT in this flow

**First pass (superseded):** the reviewer stated reminders are template-native ("set on the
Docusign template for 2 and 5 days"), and this file originally concluded no flow logic was
needed for reminders anywhere, since TAD §5.9's "3 and 7 days"/`Setting.ReminderDays` wording
looked stale against that live statement.

**The reviewer's follow-up decision reverses that:** if a dynamic, per-envelope override path
exists in the connector, use `rev_setting`'s seeded `[3,7]` and discard the template's 2/5-day
values entirely — the seeded table wins over a hand-configured template setting. Checked properly
this time, not assumed: `Create_and_send_the_envelope`'s own action (`SendEnvelope`) has no
reminder parameter, but a SEPARATE, documented action — `Add reminders for an envelope`
(`AddReminders`) — does exist and does exactly this. **Reminders are therefore now flow-driven,
built in `REV | Acceptance | Create Envelope` (wbs:3.2) immediately after it creates each
envelope — NOT in this flow.** Full reasoning, the delay/frequency shape mismatch this produces,
and the new `A-DS-11` register row are in that flow's own `.notes.md` and
`provisioning/deploymentSettings/settings-rows.notes.md#ReminderDays`, not repeated here.

**Why reminders do not belong in THIS flow, architecturally:** a per-envelope reminder-cadence
override is a one-time, at-creation-time configuration call, not a recurring check — it belongs
beside `Create_and_send_the_envelope`, the only place that ever creates the envelope, not in a
daily recurrence that would otherwise have to re-apply it needlessly on every run.

## What this flow actually builds: escalation only (FR-044)

TAD 5.9's escalation half — "escalation to the process owner with the applicant's details at 14
days" — has no template-level equivalent: DocuSign's reminder/expiration settings notify the
signer, never a third party, and nothing in the connector's action list (checked against the
full action/trigger list, `learn.microsoft.com/connectors/docusign/`) sends an internal
notification when a recipient has not acted. This half genuinely needs flow logic, and is what
this flow builds.

## Eligibility signal: `rev_status eq 2`, deliberately NOT a DocuSign envelope query

`List_overdue_grants` reads Dataverse alone: `rev_status eq 2` (Acceptance Issued — WBS 3.4
advances it to 3 once both signatures complete) plus `rev_acceptanceissuedon` at or before the
threshold cutoff. This was a deliberate choice against querying DocuSign's own envelope/recipient
status (`List envelopes` / `List recipients from an envelope`, both real, documented actions) for
the same eligibility question: Dataverse's own status column already answers "is this acceptance
still outstanding" without a second unverified wire-shape guess stacked on top of A-DS-2/A-DS-9.
If WBS 3.4 is itself delayed or broken, `rev_status` staying at 2 is exactly the safe,
conservative signal that keeps escalation firing — no DocuSign round-trip can make that signal
more current than the flow that is supposed to have already moved it.

## `Read_escalation_threshold` / `Compose_escalation_threshold_days` — A-DS-6

Reads `Setting.EscalationDays` (rev_setting) the same way `REV | Scoring | Calculate & Flag`
reads its own thresholds — `ListRecords` with a `$filter`, never Get-a-row-by-id, even keyed by
`rev_name` (IMP-0112/IMP-0116's proven pattern for this connector). Unlike the Scoring flow's
settings, this one falls back to `14` — **the TAD's own literal (§5.9/FR-044), not an invented
number** — if the row is ever absent, rather than failing every run. This is deliberately more
forgiving than the Scoring flow's settings (which have no fallback and are expected to always be
seeded before the flow runs): `EscalationDays` is new, DEV-only, and a missing row here should not
silently stop escalation from ever firing while the TAD's own answer is sitting right there.
Recorded as **A-DS-6** in Dev Summary §10 because it is still a resilience choice worth naming,
not because the fallback value itself is a guess.

## `Compose_days_overdue` — ticks-based date arithmetic

The workflow definition language has no built-in date-difference function (confirmed: only
`ticks()`, which converts a datetime to its .NET tick count). `div(sub(ticks(a), ticks(b)),
864000000000)` (ticks per day) is standard, documented WDL, not DocuSign-specific, and has not
been exercised by any flow in this project before now — flagged as E1/E2, not a guess, but new
to this project's own history the same way A-DS-3(b)'s lookup-navigation-property read was.

## `Notify_escalation_card` / `Notify_escalation` — names ARE included, by design

Every other Teams alert in this solution (the Scoring flow's Borderline card, the Ops Failure
Alert) deliberately withholds the applicant's name. This one does not: FR-044's own wording is
"escalation... **with the applicant's details**", so the card includes the applicant's and
referee's names. This is a requirement-driven exception, not an oversight — stated plainly in
both the on-file description and here so a future reviewer of this solution's Teams-alert
pattern does not read it as an inconsistency to fix.

## What this flow deliberately does NOT do

- **No reminder scheduling or DocuSign reminder action of any kind** — see above.
- **No DocuSign envelope/recipient status query** — see above.
- **No TST/ACC or PRD wiring.** Same DocuSign-licence dependency as wbs:3.2; DEV-only until it
  closes.
- **No completion handling.** That is flow #10 (WBS 3.4), built alongside this one but as a
  separate flow.
