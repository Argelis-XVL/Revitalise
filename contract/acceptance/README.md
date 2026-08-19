# contract/acceptance/ — phase acceptance records

Empty by design as at 2026-08-19. **No phase has been accepted and no warranty window has started.**

## Why that matters more than it looks

Build Terms **B5** opens three routes to acceptance, and only the first needs anyone to do anything:

1. the Client confirms acceptance in writing
2. **ten business days pass after the Consultant submits the phase for acceptance**, with no
   specific written objection
3. **putting a Deliverable into live operational use** also constitutes acceptance of it

Routes 2 and 3 start a 60-day warranty window with nobody recording a thing. That is why
`scripts/warranty-clock.py` reads all three and reports the **earliest** as operative.

## The current position, confirmed by the reviewer on 2026-08-19

| | |
|---|---|
| Live operational use | **None.** Everything is in development. Route 3 has not fired for any deliverable |
| Client acceptance | **Deferred.** It comes after the Client has tested in the acceptance environment |
| Testing this week | Revitalise begin testing Phase 2 at the end of the week — columns, views and form layout |

## The distinction that must not be blurred

**Handing work to the Client to test is NOT submitting the phase for acceptance.** If it were, route
2's ten-business-day clock would start, and silence during testing would accept the phase by default.

So this week's Phase 2 test is recorded as a **V4 review** (a named person opens the components and
looks at them), not as a submission. Nothing in `contract/acceptance/` is created for it, and
`Submitted for acceptance:` stays unset until a phase is deliberately submitted.

When a phase *is* submitted, fill in `Submitted for acceptance:` on its record from
`templates/phase-acceptance-template.md` — that is the field that starts route 2's clock, and it is
the reason the field exists.

## One thing outstanding for acceptance to be possible at all

Acceptance is to follow testing **in the acceptance environment**. Under TAD ADR-006, Test and
Acceptance are one environment (`tst_acc`), and nothing has been promoted beyond DEV: promotion
DEV → TST/ACC is a manual step in the Power Platform Pipelines UI (ADR-007), not automated here. So
the sequence is: promote to TST/ACC → Client tests there → Client accepts → warranty starts.
