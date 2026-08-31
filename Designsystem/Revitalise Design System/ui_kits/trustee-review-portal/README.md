Redesign of the Power Platform Code App "REV Trustee Review Portal" (React + Vite) to fit the Revitalise design system. Recreates the three screens seen in the current app (Round overview, Applications under review, Application detail) using DS components/tokens instead of the app's ad-hoc styling.

Key changes vs the current app (see readme.md "Trustee Review Portal redesign notes" for the full list):
- Headings switched from bold navy sans to Playfair Display in ink-900 (brand has no navy in its palette).
- Secondary buttons switched from navy outline/text to pink outline (`Button variant="secondary"`), matching the primary pink used elsewhere in the app.
- "Not available yet" boxes (grey panel + dark left border) replaced with the new `Notice` component — a flat rounded panel, no left accent bar.
- Stat figures pulled into the new `StatTile` component (serif value, muted label) instead of plain text.
- Radio buttons on the verdict form formalised as the new `Radio` component (already pink-accented in the source app — kept, just componentised).

The Power Apps platform chrome (top black toolbar) is out of scope — it's owned by the platform, not the app.
