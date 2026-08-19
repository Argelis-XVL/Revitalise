# Skill: How to Run a Phase Acceptance

Used by `acceptance-agent`. Load it when you assemble the pack.

---

## 1. What you are producing

The artefact Build Terms **B1** names as part of the Agreed Specification, alongside the Solution
Design, the Solution Architecture and the WBS — and *"where these conflict, the most recently
accepted version prevails"*. So this document **governs**. It also starts the 60-day warranty window
and fixes the per-phase liability cap (B4, B11).

Template: `templates/phase-acceptance-template.md`. Gate:
`python3 scripts/verify-acceptance-pack.py <path>` must pass **before** the pack is shown to anyone.

## 2. The two fields no agent may fill in

`Accepted by` and `Accepted on`. V6 is an act by the Client's authorised contact — for this
engagement, the CEO named in the agreement's §01. It is recorded only from an explicit
`CLIENT ACCEPTED <phase> <YYYY-MM-DD>` input.

No amount of green substitutes: not V5, not a passing CI run, not "looks good" in a meeting, not the
phase reaching its contractual date. `verify-acceptance-pack.py` fails without a real date and a
named person.

## 3. Every task in the phase appears, or the pack is incomplete

Build the task list from `contract/wbs.json` filtered by phase — never by hand. `IMP-0013` is why: a
hand-written verification list named four component types correctly and omitted the two that had
silently not been created. A derived list cannot encode what you already suspected.

## 4. A task below its level is carried explicitly, or blocks the pack

A task whose derived state is not complete may be accepted **only** if it appears in *Open items
carried into warranty* with an owner and the date its cover ends. Anything else is a completion claim
above the evidence (`C-COM-006`, PM-R19).

Required level by deliverable type: a deliverable naming a test or sign-off needs **V5**; anything a
maker must open needs **V4**; the rest need their evidence present.

## 5. No variance while the phase is open

`IMP-0065`. Write "not computed — the phase is still open" and mean it.

## 6. State what the record does not assert

Keep the section. It names the B8 platform exclusions (M365, Power Platform, Dataverse, Power
Automate, Power Apps, AI Builder, DocuSign, QuickBooks Online, WordPress and its form plugin), the
absence of any time-saving promise, and B9's limit on the anonymisation step. That section is what
fixes the boundary — dropping it is not a formatting slip, and the gate fails without it.

## 7. After acceptance

Append a `logs/commercial-events.jsonl` line naming the phase, the date, the person and the keyword
used. Then the warranty clock owns the window — once D-4's clause text is in `docs/Import/`.
