# Handoff: Trustee portal — Application detail (card layout)

Target: `Argelis-XVL/Revitalise`, branch `deploy-first-learning-and-item-closure`, app `src/code-apps/trustee-review-portal/` (React + Vite, Power Apps Code App, CSS Modules).

## Overview
This is a visual redesign of the individual Application detail screen (`pages/ApplicationDetailPage.tsx`). The **data, section order and labels stay exactly as they are today**: the Trustee Pack's five sections from `domain/applicationDetailLayout.ts`, then Staff recommendation, then the verdict. What changes is presentation. Each section's rows render as scannable blocks (fact tiles, a cost receipt, free-text answer cards, a wellbeing scale and answer pills, and a restricted-fields list) instead of one long `<dl>`.

## About the design files
The files in `reference/` are **design references written as in-browser React with inline styles**. They show the intended look and are not production code. Recreate them in the existing app using its patterns: CSS Modules in `styles/app.module.css`, the `ds/*` components, `Panel`, `StateMessage`, and the existing domain/format functions. Do not copy the inline styles, the `window.*` globals or the mock data.

## Fidelity
**High fidelity.** Final colours, type, spacing and radii. All values are the design system's tokens (listed below; `tokens/` has the source). The app already publishes these tokens through `styles/ds-tokens.css`.

## Non-negotiables (existing contracts — keep them)
1. **Rendering is driven by the layout spec.** Keep rendering from `APPLICATION_DETAIL_LAYOUT`. Don't hardcode rows in JSX. Add a presentation hint per row instead (see "Implementation approach").
2. **Redaction states are unchanged.** `redactedTextState()` in `domain/visibility.ts` still decides between `withheld`, `released-empty` and `released`. The new answer card is only a new look for those three states. `released` shows the text through `MultilineText` (keep the 75ch measure).
3. **Restricted rows** still use `RESTRICTED_VALUE_TEXT`. Never request a secured column.
4. **Conditional rows** (`D11a`, `A3a`, `A3b`) still use `isRowVisible()`.
5. **Semantics and tests.** Every row keeps a `data-field="<row id>"` attribute. Label/value pairs stay `<dt>`/`<dd>` inside a `<dl>`: tiles can be `<div>`s wrapping `<dt>`+`<dd>` inside one `<dl>`, which is valid HTML. Keep one `<h2>` per section (via `Panel`) and use `<h3>` for sub-blocks.
6. **Order.** `applicationDetailLayout.test.ts` pins rows to Pack order, and this design groups rows by display type within a section. Either (a) keep each section's DOM order equal to Pack order and group only where the rows are already contiguous, or (b) update the order test to assert order *within each display group*. Agree which one with the reviewer; option (b) changes a pinned contract, so record it.
7. **Print.** Add `print.css` rules keyed on `data-print` attributes (as today) so the tiles print as plain black on white: no gradients, no shadows, borders at 1px `#000`. The 0–10 scale must print with its value as text.
8. **Accessibility.** 44px minimum targets on the buttons (already handled by `ds/Button`). Text contrast of at least 4.5:1: all the pairings below pass. The 0–10 scale needs its value in text as well as colour: `role="img"` with `aria-label="Answer: N out of 10"`, or a visually hidden text node. Don't use `--text-muted` (#8a8a8a) for text (ADR-037).

## Implementation approach
Extend `DetailRow` in `applicationDetailLayout.ts` with an optional presentation hint:

```ts
display?: "fact" | "cost" | "costTotal" | "answer" | "scale" | "likert" | "restricted" | "score";
```

`DetailSectionPanel` then partitions each group's visible rows by `display` and renders the matching small component: `FactTiles`, `CostReceipt`, `AnswerCards`, `ScoreBar`, `LifeScale`, `AnswerList` or `RestrictedList`. The Summary section renders as `SummaryHero` instead of a `Panel`. Default to `"fact"` when the hint is absent.

Row → display mapping used in the design:

| Section | fact | cost / costTotal | answer (redacted) | other |
|---|---|---|---|---|
| Summary (hero) | S0a Status (pill), S0b, S1, S2, S4, S5, S6, S7 | | | S3 → hero score badge |
| Application Details | D1, D2, D3, D4, D11 | D5, D6, D7, **D8 total**, D9, D10 | D11a, D12, D13 | |
| About Applicant | A1, A2, A3 (chips), A5, A7 | | A3a, A3b, A4, A6 | |
| Current Circumstances | | | | C1 score bar · C2 0–10 scale · C3–C9 and C10–C12 likert |
| Financial Eligibility | F4, F6 | | F5 | F1, F2, F3 restricted |

## Screen: Application detail

### Page order
1. `<h1>Application {reference}</h1>` (unchanged)
2. `.actionRow`: "Print this case" (secondary) and the conditional "Back to group {code}" (secondary) (unchanged)
3. Summary hero
4. Application Details panel
5. About Applicant panel
6. Current Circumstances panel
7. Financial Eligibility panel
8. Staff recommendation panel (unchanged content)
9. Verdict panel (unchanged behaviour)

Gap between blocks: 24px (`--space-6`). Page background: `--grey-50` #f8f7f7.

### Panel (card)
- Background #ffffff. Radius 16px. Padding 32px (`--space-8`).
- Shadow: `0 1px 2px rgba(43,43,43,.04), 0 6px 20px rgba(43,43,43,.07)`. On hover: `0 2px 4px rgba(43,43,43,.05), 0 16px 40px rgba(43,43,43,.12)` with `translateY(-2px)`, 200ms standard easing. The hover lift is optional and should be off under `prefers-reduced-motion`.
- Internal layout: flex column, gap 20px (`--space-5`).
- **Eyebrow** above the `<h2>`: 12px, weight 700, letter-spacing .08em, uppercase, colour #49345b, with an 8px circle dot of the same colour and an 8px gap before the text. Eyebrow copy (new, design-only; mark it `aria-hidden` or keep it as decorative text): Application Details → "The break"; About Applicant → "Who they are"; Current Circumstances → "How they are doing"; Financial Eligibility → "Money"; Staff recommendation → "From the team"; Verdict → "Your decision" (brand pink #e6027f dot and text).
- **`<h2>`**: Playfair Display, 24px (`--text-xl`), #2b2b2b, margin 0. The Pack heading is used verbatim.
- **Sub-block `<h3>`** ("Costs", "In their words", "Not visible to trustees", "Life satisfaction", "In the last 2 weeks…", "In the last year…"): Nunito Sans 15px, weight 700, letter-spacing .02em, #4b4b4b. There is 12px between the sub-heading and its content. "Life satisfaction", "In the last 2 weeks…" and "In the last year…" are existing group headings in the spec. "Costs", "In their words" and "Not visible to trustees" are new presentation headings for the reviewer to approve.

### Summary hero (replaces the Summary panel)
- Card with radius 20px, padding 32px, background `linear-gradient(135deg, #ede8f1 0%, #fdf1f8 100%)`, same shadow as a panel. Flex row, wraps, gap 32px, items centred.
- **Score badge**: a 120×120 white circle with shadow `0 6px 20px rgba(73,52,91,.14)`. Inside, a label "Score" (12px, 700, uppercase, .08em, #49345b) and the value (Playfair 46px, line-height 1.05, #e6027f; 30px if the value is longer than 3 characters). The value is S3 `circumstanceScore`, or "—" when null.
- **Right column** (flex 1 1 320px): eyebrow "Summary" (#49345b), then `<h2>` in Playfair 32px (`--text-2xl`). The heading reads "{score} out of 60 circumstance points", or "Not scored yet" when null. This is design copy; the S3 row label stays available to assistive tech through the chips or as visually hidden text.
- **Row 1**: status pill (S0a) followed by fact chips for S0b "Review round", S1 "Application ID" and S2 "Are you?".
- **Row 2**: fact chips for S4 "Start Date", S5 "End Date", S6 and S7 "Exceptional Funding Amount". The design shortens S6's chip label to "Total requested inc. exceptional funding"; the spec's full label is "Individual Total Amount Requesting Revitalise inc. Exceptional Funding". Confirm with the reviewer or put the full label in the chip.
- **Fact chip**: inline flex column with a 2px gap, background `rgba(255,255,255,.85)`, radius 12px, padding 8px 14px, shadow `0 1px 3px rgba(73,52,91,.08)`. Label is 12px #5a5a5a; value is 15px weight 700 #2b2b2b.
- **Status pill**: radius 999px, padding 4px 12px 4px 10px, 13px weight 700, with a 7px dot and a 6px gap. Tones:
  - Eligible for Panel: bg #fdf1f8, fg #9e0057, dot #e6027f
  - Under Review: bg #ede8f1, fg #49345b, dot #49345b
  - Borderline: bg #e7f6f8, fg #00505a, dot #14adbb
  - other statuses: bg #f0eeee, fg #4b4b4b, dot #8a8a8a

### Fact tiles
- A `<dl>` grid: `repeat(auto-fill, minmax(220px, 1fr))`, gap 12px.
- Each tile: radius 14px, padding 16px 20px, background #f8f7f7 with a 1.5px transparent border, flex column with a 4px gap.
- `<dt>`: 15px #4b4b4b. It wraps, which matters because long Pack questions such as A2 need several lines.
- `<dd>`: 17px weight 700 #2b2b2b.
- **Absent value** ("Not recorded"): transparent background, 1.5px dashed #e0dede border, `<dd>` in italic weight 400 #5a5a5a.
- **A3 conditions**: the value renders as chips instead of a "; "-joined string. Each chip is white with a 1px #e0dede border, radius 999px, padding 2px 10px, 13px weight 700, 6px gap, wrapping. For a carer with both profiles, keep the "You: … / The person you support: …" distinction as two labelled chip rows.

### Cost receipt (D5–D10)
- Container: background #f8f7f7, radius 14px, padding 8px 20px.
- Each line: flex space-between, gap 16px, padding 10px 0, 1px #f0eeee top border (none on the first line). The label is #4b4b4b. The amount is weight 700, #2b2b2b, `font-variant-numeric: tabular-nums`, no wrap, right-aligned.
- Line order: D5, D6, D7, then **D8 Total Estimated Cost** with a 2px #e0dede top border and its label in weight 700 #2b2b2b, then D9 and D10.
- "Not recorded" amounts are italic #5a5a5a.
- Use `formatAmount()` for every value.

### Answer cards (redacted free text)
- Grid: `repeat(auto-fill, minmax(280px, 1fr))`, gap 12px.
- Card: radius 14px, 1.5px dashed #ddd3e6 border, background `linear-gradient(135deg, rgba(237,232,241,.45), rgba(253,241,248,.45))`, padding 16px 20px, flex column with an 8px gap.
- Question (the row label): 15px weight 700 #2b2b2b, `text-wrap: pretty`.
- **withheld**: a pill reading "Withheld until released" (`WITHHELD_HEADING`): white background, #49345b text, 13px weight 700, radius 999px, padding 3px 10px, with a 7px #49345b dot. Under it, 13px #4b4b4b text. The design shows only the first sentence of `WITHHELD_EXPLANATION` ("This answer has not been released for trustee review yet.") to avoid repeating the full paragraph on every card. Either export that first sentence as its own constant or show the full explanation once per section. Don't write new wording.
- **released-empty**: the same card with a `quiet` tone: solid #e0dede border, no gradient, pill text "Nothing recorded" (`RELEASED_EMPTY_HEADING`) in #4b4b4b on #f0eeee, then the explanation.
- **released**: a solid 1.5px #e0dede border on a white background, the question, then the text through `MultilineText` (17px #5a5a5a, pre-wrap, max 75ch).
- Keep the answer states as notes (`role="note"`), never alerts.

### Current Circumstances
Blocks are separated by 32px (`--space-8`). This keeps the reviewer's WI-0008 "three distinct sections with more white space" requirement.
- **C1 score bar**: a tile (#f8f7f7, radius 14px, padding 16px 20px). The top line has the label (15px #4b4b4b) on the left and the value on the right: "{n} / 60" in Playfair 24px #2b2b2b, or "Not recorded". Below it is a 10px track (#f0eeee, radius 999px) with a fill of `linear-gradient(90deg, #49345b, #e6027f)` at a width of score/60.
- **C2 life satisfaction**: the question text in 17px #5a5a5a, then 11 circles labelled 0–10, each 34×34 with 13px weight 700 text and a 6px gap, wrapping. The answered value is a filled #e6027f circle with white text. The others are #f8f7f7 with a 1px #e0dede border and #5a5a5a text. Label with `optionLabel(LIFE_SATISFACTION_LABELS, …)`. When the answer is null, show "Not recorded" text instead of the circles.
- **C3–C9 and C10–C12 answer list**: rows with a flex space-between layout that wraps, padding 12px 0, and a 1px #f0eeee divider between rows. The question (flex 1 1 260px) is 17px #5a5a5a. The answer pill is #ede8f1 with #49345b text, 13px weight 700, radius 999px, padding 4px 12px, no wrap. Use the existing `wellbeing()` labels. An unanswered question shows "Not recorded" in the same pill with italic text.

### Restricted list (F1–F3)
- Each row: flex space-between, wrapping, radius 12px, 1.5px dashed #e0dede border, padding 10px 16px, 8px gap between rows.
- The question is 15px weight 700 #2b2b2b.
- The pill reads "Restricted" on #f0eeee, in #4b4b4b, 13px weight 700, radius 999px, padding 4px 12px.
- Below the list, 13px #4b4b4b text: `RESTRICTED_VALUE_TEXT`, shown once. Screen readers still need each `<dd>` to contain the full text, so give every row a visually hidden copy of it.

### Staff recommendation and Verdict
The content and behaviour are unchanged. They are restyled as panels with the eyebrows above. The notes textarea has a 12px radius, a 1.5px #e0dede border, a #f8f7f7 background and 12px 14px padding.

## Responsive behaviour
- Everything reflows through `auto-fill` grids and wrapping flex. There is no horizontal page scroll at 320px (WCAG 1.4.10); `application-detail-layout.visual.spec.ts` already checks 320, 390 and 1280px, so extend it to cover the new blocks.
- Below 480px the hero stacks, with the badge above the text, and the panel padding can drop to 20px.
- Use `overflow-wrap: anywhere` on values.

## State management
There is no new state; `useApplication` and `useReview` are unchanged. Visibility of `D11a`, `A3a` and `A3b` still comes from `isRowVisible`.

## Design tokens
- **Brand pink**: `--brand-primary` #e6027f; pink-50 #fdf1f8; pink-800 #9e0057.
- **Purple**: #49345b (not a named token in `ds-tokens.css`). Add it through `styles/brand.css` as `--rev-color-secondary` or reuse the existing secondary if it matches.
- **Lavender**: lavender-100 #ede8f1; lavender-200 #ddd3e6.
- **Teal**: #14adbb (dot only) and its tint #e7f6f8.
- **Neutrals**: grey-50 #f8f7f7, grey-100 #f0eeee, grey-200 #e0dede, white #ffffff.
- **Ink**: ink-900 #2b2b2b (headings), ink-700 #4b4b4b, ink-600 #5a5a5a (body).
- **Type**: Playfair Display for headings, Nunito Sans for body. Sizes: 13 / 15 / 17 / 20 / 24 / 32px (`--text-xs` to `--text-2xl`).
- **Spacing**: 4 / 8 / 12 / 16 / 20 / 24 / 32 / 48px (`--space-1` to `--space-12`).
- **Radii**: pills 999px; chips 12px; tiles 14px; panels 16px; hero 20px.
- **Shadows**: the panel and hero values given above.

## Assets
None. There are no images or icons; the dots are CSS circles.

## Files
(The `.jsx.txt` extension keeps these reference copies out of the design-system build — read them as JSX.)
- `reference/ApplicationDetail.jsx.txt`: the design for this screen (all blocks).
- `reference/Shared.jsx.txt`: `Panel`, `HeroBand`, `FactChips`, `StatusPill`, `Definitions` (the fact tiles) and `StateMessage`.
- `reference/AppFrame.jsx.txt`: the nav bar, in order: Round overview, Group applications, Individual applications, Application detail.
- `reference/index.html`: the `.rv-card` shadow and hover CSS. It runs from the design project (it loads `../../_ds_bundle.js` and `../../styles.css`); inside this bundle it is a style reference only.
- `tokens/*.css`: the token sources.
- Repo files to change: `src/domain/applicationDetailLayout.ts` (add `display`), `src/components/CasePanels.tsx` (`DetailSectionPanel` plus the new sub-components), `src/styles/app.module.css`, `src/styles/print.css`, and the tests `applicationDetailLayout.test.ts`, `ApplicationDetailPage.test.tsx`, `CasePanels.test.tsx` and `application-detail-layout.visual.spec.ts`.
