# Phase Acceptance Record — <Phase N>

> **This document is part of the Agreed Specification.** Build Terms B1 names "the phase acceptance
> record" alongside the Automation Solution Design, the Solution Architecture and the Work Breakdown
> Structure, and *"where these conflict, the most recently accepted version prevails"*. What this
> record says therefore governs. It also starts the warranty clock and fixes the per-phase liability
> cap (B4, B11), so a wrong date here has consequences beyond bookkeeping.
>
> **Verified by:** `python3 scripts/verify-acceptance-pack.py contract/acceptance/PA-<phase>.md`

- Phase: <Phase N — name from the agreement's §03 schedule>
- Contracted hours: <from contract/service-agreement.json — hours only, D-3>
- Contractual date: <from contract/service-agreement.json milestones>
- Go-live: <YYYY-MM-DD — the date the phase's deliverables went live in the client's environment>
- Submitted for acceptance: <YYYY-MM-DD, or leave blank>
- In live use since: <YYYY-MM-DD, or leave blank>
- Accepted by: <full name and role of the Client's authorised contact>
- Accepted on: <YYYY-MM-DD>

**Acceptance has three routes and the earliest one wins (Build Terms B5).** Fill in whichever
applies; `scripts/warranty-clock.py` takes the earliest as operative:

| Route | Field | What starts the clock |
|---|---|---|
| written | `Accepted on:` | the Client confirms in writing |
| silence | `Submitted for acceptance:` | ten business days later, absent a specific written objection |
| use | `In live use since:` | putting a deliverable into live operational use |

**`Submitted for acceptance:` is not "we showed it to them".** Handing work over to be tested is not a
submission — if it were, silence during testing would accept the phase by default. Set this field only
when a phase is deliberately submitted.

**No agent may fill in `Accepted by` or `Accepted on`.** V6 — client accepted — is an act by the
Client's authorised contact, recorded from an explicit `CLIENT ACCEPTED <phase> <date>` input. No
quantity of passing tests substitutes for it (PM-R18).

---

## 1. What is being accepted

One row per WBS task in this phase. `Level` is the highest verification level actually reached, in
the words of the log that recorded it — never a level inferred from a green build.

| WBS | Task | Deliverable | Level | Evidence |
|---|---|---|---|---|
| <0.1> | <task> | <deliverable> | <V3/V4/V5> | <log line, test report section, or commit> |

Levels, from `agents/WORKFLOW.md`: **V2** packaged · **V3** accepted by the target · **V4** a named
person opened and saved it · **V5** executed end-to-end with real inputs · **V6** client accepted.

## 2. Hours

| | Hours |
|---|---|
| Contracted for this phase | <n> |
| Booked to this phase | <n — from scripts/compute-invoice.py> |
| Already invoiced | <n> |
| Variance | <only if EVERY task in the phase is closed; otherwise write "not computed — the phase is still open (IMP-0065)"> |

An invoiced figure below estimate on an unfinished phase says nothing about efficiency. Do not
report a variance until the phase is closed, client testing and feedback included.

## 3. Open items carried into warranty

Anything not finished but accepted anyway, each with the date its warranty cover ends.

| Item | Why it is being carried | Owner | Warranty cover ends |
|---|---|---|---|
| <D-nnn / A-nnn> | <one line> | <name> | <date, or "not computed — D-4"> |

## 4. What this record does not assert

- It does not assert that any third-party platform works. B8 excludes M365, Power Platform,
  Dataverse, Power Automate, Power Apps, AI Builder, DocuSign, QuickBooks Online, and WordPress
  with its form plugin.
- It does not assert a time saving.
- It does not assert that the anonymisation step removes every trace of personal data (B9). The
  Client remains data controller and reviews flagged items before disclosure to trustees.
- It does not accept work outside the Agreed Specification. Unquoted work is a change order.

## 5. Signatures

| | Consultant | Client |
|---|---|---|
| Name | | |
| Role | | |
| Date | | |
