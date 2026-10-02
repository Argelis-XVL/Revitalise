Brand-aligned recreation of the Power Platform Code App "REV Trustee Review Portal", rebuilt from the real source at `src/code-apps/trustee-review-portal/` (Argelis-XVL/Revitalise, main @ 638ce23f38fe).

Screens (view state mirrors `App.tsx`): Round overview → Applications list → Group applications → Group detail → Application detail.

What the 2026-09-30 sync picked up from the source:
- Persistent "Screen navigation" bar with four tabs: Round overview, Applications list, Group applications (new, EF-43 Δ5), plus Application detail, shown only on the detail view.
- Every screen opens with its `<h1>` directly under the nav bar; action rows sit underneath.
- Applications list: the Region filter/column is removed (EF-02). "Exceptional circumstance" column added, headers sort, and "Record verdict" opens a dialog in place.
- Group applications screen and Group detail (group summary + members table), with "Back to group …" on a member's detail page.
- Application detail: the "Back to the list" button is removed. Panels follow the Trustee Pack order: Summary, Anonymised narrative, Application Details, Condition and circumstance, Care-support description, Current circumstances, Financial eligibility, Staff recommendation, Your verdict.
- Round overview: "Figures of this round" section (Round progress, Exceptional circumstances, Type of break, Who applied, Level of need) above the hand-entered financial position.

All figures are mock data. The Power Apps platform chrome is out of scope.
