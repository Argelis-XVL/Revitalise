/**
 * Recharts-built visuals for the round-statistics screen — Fix 3 of the 2026-08-27
 * "close the visual gap" pass (the app compared against `Round 3 Stats.pptx` /
 * `Round 4.pptx` read as "v0.1, not v0.9" — real charts, not plain tables).
 *
 * Every component here is DECORATIVE and never the only rendering of a figure: each
 * is composed alongside the existing, audited `DistributionChart`
 * (`components/DistributionChart.tsx`) through its `visual` slot, or (for
 * `WellbeingComparisonChart`) beside the three per-question `DistributionChart`s that
 * already render underneath it. ADR-029's rule — "the table is the content... every
 * value it depicts is text in the table beside it" — extends to these unchanged:
 * nothing here is the only place a number lives, and a screen reader is never asked
 * to make sense of an SVG bar or pie slice.
 *
 * ## Why `aria-hidden`, not a second `role="img"` with a label
 *
 * `DistributionChart`'s own inline SVG earns `role="img"` plus `chartSummary()` (its
 * own hand-written label) because it IS the one picture describing that data. A
 * Recharts figure placed beside it draws the SAME numbers a second time, for a
 * sighted trustee's benefit — a literal comparison view, not a new fact. Exposing a
 * second "image" landmark for the same data would be a duplicate announcement, not a
 * second source of information, so the whole figure — chart AND its hand-rolled
 * legend — is taken out of the accessibility tree with `aria-hidden="true"` instead.
 *
 * ## Why no charting-library `<Legend>` and no `<ResponsiveContainer>`
 *
 * Recharts v3's own `<Legend>` renders through a `createPortal` plus a
 * measured-size path that never resolves under this app's jsdom test run
 * (`getBoundingClientRect` is all-zero there), so it would ship UNTESTED — the
 * `IMP-0111` trap this project already has a name for ("a test written from the same
 * assumption as the code locks the assumption in rather than verifying it" applies
 * just as much to a chart nobody actually saw draw in a test). `ChartLegend` below is
 * a plain `<ul>` of coloured swatches instead: real DOM, trivially rendered, trivially
 * tested — and this app already prefers hand-rolled markup over a library surface for
 * exactly this reason (`DistributionChart` itself uses no charting library at all).
 *
 * `<ResponsiveContainer>` needs `ResizeObserver`, which this app's test environment
 * does not provide either. Every chart below takes a FIXED pixel size instead and
 * sits inside `styles.tableScroll` — the identical `overflow-x: auto` container this
 * app's wide tables already use — so a chart wider than a narrow viewport scrolls
 * sideways in its own box rather than the page (WCAG 1.4.10's own table/diagram
 * exception, already relied on here for tables).
 *
 * ## Two Recharts props every chart below sets, and why
 *
 *   - `isAnimationActive={false}` — Recharts defers a shape's first paint to its
 *     entrance animation, which never completes under jsdom's test renderer (nothing
 *     advances its `requestAnimationFrame` loop), so an animated chart renders NO
 *     bars or slices in a test. Off everywhere, not only in tests, because a chart
 *     that renders differently under test than in the app is exactly the trap the
 *     paragraph above names.
 *   - `accessibilityLayer={false}` (chart root) / `rootTabIndex={-1}` (`Pie`) —
 *     Recharts v3 makes a chart keyboard-focusable by default (a real, if novel,
 *     built-in accessibility feature). Left on, it plants a `tabindex="0"` element
 *     INSIDE this file's `aria-hidden` wrapper — content hidden from assistive
 *     technology that a keyboard user can still tab to, which is the exact defect
 *     automated accessibility checkers flag. Turning both off keeps a decorative
 *     figure decorative in both directions: invisible to a screen reader AND absent
 *     from the tab order, rather than half-hidden.
 *
 * Every colour is one of `domain/charts.ts`'s three validated `CHART_PALETTE` slots,
 * assigned in the same fixed order every time — never picked per chart, including
 * `WellbeingComparisonChart` as of Revision 10 below (it colours by QUESTION, and FR-062
 * declares at most three of them — see that file's own header for why the ordinal ramp
 * Revision 8 introduced for the opposite axis assignment is gone rather than left unused).
 *
 * ## Revision 8 (2026-08-31, wbs:6.9) — three reviewer corrections, against the live DEV portal
 *
 * **1. Percentage, not count.** Every bar and every slice label now reads the response's
 * own `percentage` field. The flow has always emitted it beside `count`
 * (`Compose_*_categories` in `REVPortalRoundStatistics-...json`), and it reaches here
 * through `CategoryCount.percentage` and `Series`'s `SeriesRow.percentage` already, so
 * nothing is derived here — `domain/landing.ts`'s rule ("as the response computed it,
 * never derived here from count/population") is unchanged and is why this was a
 * one-field change rather than an arithmetic one. A `null` percentage draws NO BAR,
 * which is the same absence the table beside it renders as the words "Not recorded":
 * a zero-height bar would assert a measurement of 0%, and on this screen "a zero is a
 * finding; a null is an absence" (TAD §3.3 point 3).
 *
 * **2. Vertical bars.** `CategoryBarChart` previously passed `layout="vertical"`, which
 * in Recharts names the CATEGORY AXIS's direction and therefore drew HORIZONTAL bars —
 * the inversion that makes this prop a standing trap. Both bar charts below now use
 * Recharts' default (`layout="horizontal"`, left implicit): category on x, value on y,
 * bars growing upward.
 *
 * **3. `WrappedCategoryTick`, and why flipping the axis needed one.** The old horizontal
 * layout put category labels on the y-axis, where a 190px-wide `YAxis` absorbed
 * `APPLICANT_GENDER_LABELS`' "Describes themselves another way" and
 * `APPLICANT_TYPE_LABELS`' full-sentence options without rotating or truncating
 * anything — the property the old `CategoryBarChart` docstring called out by name. Moving
 * those labels to the x-axis takes that away: a 46-character applicant-type label is
 * ~300px of single-line text over a column ~160px wide. Recharts' own answers are to
 * rotate (`angle`), which at 46 characters needs ~170px of axis height and still reads
 * badly, or to truncate, which silently hides part of a category name. Neither is
 * acceptable for a label that IS the category's identity, so the tick below WRAPS
 * instead: real `<tspan>` lines, every character of every label kept, nothing rotated.
 * Beyond `TICK_MAX_LINES` the label is ellipsised — the only lossy path, reachable today
 * by no option set this app declares, and safe when it is reached only because the table
 * beside the chart carries every label in full (ADR-029).
 *
 * **4. `WellbeingComparisonChart` is transposed and takes the ORDINAL ramp.** One row per
 * question, one series per response category — `domain/charts.ts`'s Revision 8 header
 * carries the reasoning for the pivot itself. What lands HERE is the colouring: a series is
 * now a point on the agreement scale rather than an identity, so the fill comes from
 * `agreementResponseColor(series.value)` and NOT from `categoricalColor(index)`. Painting a
 * Likert scale with three wrapped categorical hues would have given "Strongly Disagree" and
 * "Agree" the same magenta, which is the one thing a scale chart must never do.
 *
 * **"Not sure" IS RENDERED, as a sixth grey bar, and is not dropped.** The
 * `AGREEMENT_RESPONSE_LABELS` sixth option carries real counts in the source deck's own
 * chart5, so silently omitting it would understate every other category's context. It is
 * drawn off-scale (`AGREEMENT_OFFSCALE_COLOR`) rather than as a sixth step of the ramp, for
 * the reason `domain/charts.ts` states: a non-answer painted past "Strongly Agree" asserts
 * an opinion nobody expressed. The legend names all six in words, so the off-scale status is
 * never carried by hue alone (WCAG 1.4.1).
 *
 * ## Revision 8 addendum — where the accessible text for these figures now lives
 *
 * `DistributionChart`'s `figures="share-only"` mode (see that file) is what the "Who applied
 * in this round" panel now composes these charts inside. In that mode the table drops its
 * COUNT column and its own hand-rolled SVG, keeping the category labels and the share
 * figures as real text plus the stated denominator. Nothing about THIS file's `aria-hidden`
 * contract changes: every figure here is still decorative, still out of the tab order, and
 * still never the only rendering of a value — the share-only table beside it carries every
 * label and every percentage this chart draws.
 *
 * ## Revision 9 (2026-09-01, wbs:6.9) — reviewer item 2, the tick type size
 *
 * The labels on the age-range, gender, ethnic-group and wellbeing charts were 12px, below
 * every step of this app's own scale. They are now 15px (`--text-sm`), on BOTH axes, and four
 * further constants moved in the same change so that they could: see `TICK_FONT_SIZE`'s own
 * block below for the arithmetic and for why changing the size alone would have overlapped
 * every wrapped label (`IMP-0509`, `C-TECH-076` check A).
 *
 * **This file's accessibility contract is untouched by that, and by Revision 9's item 1.**
 * Everything here is still `aria-hidden` and still decorative. `DistributionChart`'s table is
 * now clipped off screen by default rather than drawn under the chart — but it is still in the
 * DOM and still in the accessibility tree, so "never the only rendering of a value" holds
 * exactly as before. Nothing in this file may become the sole carrier of a figure.
 *
 * ## Revision 10 (2026-09-02, wbs:6.8) — the wellbeing pivot turned back over, and the
 * category-column width bug this exposed on every wrapping chart, not only this one
 *
 * Two independent reviewer findings, against the live DEV portal:
 *
 *   1. **`WellbeingComparisonChart` is transposed back**: category (response option) on the
 *      x-axis, one bar per QUESTION within each group. `domain/charts.ts`'s own Revision 10
 *      header carries the full reasoning; what lands here is that it now colours by
 *      `categoricalColor(index)` — a question is a plain identity, and FR-062 never declares
 *      more than three of them, which is `CHART_PALETTE`'s own validated slot count exactly.
 *   2. **X-axis labels were overlapping their neighbours on every chart that wraps a long
 *      category label** — gender's "Describes themselves another way", ethnic group's
 *      multi-word options. ROOT CAUSE: `BAR_COLUMN_WIDTH` (85px) was scaled from the OLD
 *      68px by the same 15/12 ratio `TICK_FONT_SIZE` grew by (Revision 9), but that ratio
 *      answers "how much bigger is the type", not "how wide is a WRAPPED LINE of it" — and
 *      nothing before this revision checked the second question against `wrapTickLabel`'s
 *      own `TICK_CHARS_PER_LINE` budget. 18 characters at this app's sans stack renders
 *      roughly 150-160px wide, comfortably wider than an 85px column, so two neighbouring
 *      wrapped ticks drew on top of each other. `COMPARISON_GROUP_WIDTH` (190px) never showed
 *      this defect because its OWN comment already did that arithmetic and landed over the
 *      line — the bug was that `BAR_COLUMN_WIDTH` never did the same sum, not that one chart's
 *      renderer differs from another's: every chart below shares the one `WrappedCategoryTick`,
 *      so a column sized without checking the wrap budget produces this on EVERY chart whose
 *      category labels are long enough to wrap, which is what "not only this one" means in the
 *      dispatch that raised it. `MIN_CATEGORY_COLUMN_WIDTH` below is the fix: both per-category
 *      width constants are now DERIVED from `TICK_CHARS_PER_LINE`, not guessed independently of
 *      it, so the two constants cannot drift apart the way they did here. Invisible to every
 *      test in this file before this revision — jsdom computes no layout — which is the same
 *      class `C-TECH-076`'s own header names and the same way `IMP-0509` was found: by eye, on
 *      a rendered screen, not by a red test.
 *
 * ## Revision 11 (2026-09-02, wbs:6.8) — three reviewer items, one piece of arithmetic
 *
 * Items 1, 4 and 5 of the third live-DEV review round all land in this file, and 1 and 5 are
 * the same defect seen on two axes: **every size constant here was a FLOOR with no ceiling
 * anywhere, and the axis band's own height was one term short.**
 *
 *   - **Item 1 — "charts sometimes overflow the screen with scrollbars; scale them down so both
 *     charts in a row are fully visible side by side."** `categoryAxisPlan` is the answer: a
 *     stated `CHART_WIDTH_BUDGET` (620px, measured off `.applicantGrid`'s own cell at the width
 *     this portal is read at), a per-chart wrap budget derived from it, and a column derived
 *     from the longest line the chart's OWN labels actually wrap to rather than from the worst
 *     label set in the app. `TICK_FONT_SIZE` drops 15 → 13 as the reviewer explicitly permitted,
 *     which is `--text-xs` — still ON this app's type scale, unlike the 12px Revision 9 rejected.
 *     **Neither `IMP-0577`'s derivation nor `IMP-0509`'s coupling is reverted; both are
 *     tightened** — `TICK_LINE_HEIGHT`, `TICK_GLYPH_WIDTH_PX`, `TICK_DESCENDER_SLACK`,
 *     `CATEGORY_AXIS_HEIGHT` and both chart HEIGHTS are now computed from `TICK_FONT_SIZE`
 *     rather than hand-adjusted beside it one revision at a time. `MIN_CATEGORY_COLUMN_WIDTH`,
 *     named in the Revision 10 paragraph above, is gone as a constant and survives as
 *     `categoryAxisPlan`'s column arithmetic, which is the same sum with real labels in it.
 *   - **Item 4 — the applicant-type pie's data labels are clipped.** Its box is now 400×280
 *     rather than 280×280: a `<Pie label>` draws OUTSIDE `outerRadius`, so a square box the size
 *     of the circle's own diameter has no room for a horizontal-flank label at all. The legend
 *     half of the same finding is `app.module.css`'s `.chartLegend`, now a column.
 *   - **Item 5 — x-axis labels overlap the bottom of the plot area.** `CATEGORY_AXIS_HEIGHT` was
 *     `TICK_MAX_LINES * TICK_LINE_HEIGHT + 20`, and the tick's own first-line `dy` already spends
 *     that 20: the band reserved nothing for the LAST line's descenders. It is now offset +
 *     lines + `TICK_DESCENDER_SLACK`, and both charts' `margin.bottom` goes 8 → 16 so the band
 *     itself is not flush against the edge of the SVG.
 *
 * As ever, jsdom paints nothing, so this revision's tests assert the ARITHMETIC — the budget,
 * the derivations, the axis sum — and not the rendered result. `C-TECH-076`'s own class.
 */
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, Tooltip, XAxis, YAxis } from "recharts";
import { categoricalColor } from "../domain/charts";
import type { WellbeingComparisonData } from "../domain/charts";
import type { Series } from "../domain/landing";
import styles from "../styles/app.module.css";

/** A hand-rolled legend — see this file's header for why it is not Recharts' own. */
function ChartLegend({ items }: { items: { label: string; color: string }[] }) {
  // "a single series needs no legend box — the title names it" (dataviz skill).
  if (items.length < 2) return null;
  return (
    <ul className={styles.chartLegend}>
      {items.map((item) => (
        <li key={item.label} className={styles.chartLegendItem}>
          <span className={styles.chartLegendSwatch} style={{ backgroundColor: item.color }} />
          {item.label}
        </li>
      ))}
    </ul>
  );
}

/* ------------------------------------------------------------------------------------- *
 * The wrapped category tick — see this file's header, Revision 8 point 3.
 * ------------------------------------------------------------------------------------- */

/**
 * How many `<tspan>` lines a category label may occupy before it is ellipsised.
 *
 * **3 → 4 in Revision 11 (2026-09-02, wbs:6.8), and it is the counterweight to that
 * revision's narrower per-chart wrap budget, not an independent change.** Item 1 buys chart
 * WIDTH back by wrapping long category labels tighter (`categoryAxisPlan` below computes a
 * per-chart `charsPerLine` as low as `MIN_TICK_CHARS_PER_LINE`), and a tighter wrap needs more
 * lines to hold the same characters: `ETHNIC_GROUP_LABELS`' longest option, "Black, African,
 * Caribbean or Black British" (42 characters), takes four lines at a 13-character budget and
 * would otherwise have hit the ellipsis branch — the one lossy path in this file, and the one
 * `TICK_CHARS_PER_LINE`'s own comment has always existed to keep unreachable.
 */
const TICK_MAX_LINES = 4;

/**
 * REVIEWER ITEM 2 (Revision 9, 2026-09-01, wbs:6.9) — THE TICK TYPE SIZE, AND THE FOUR
 * CONSTANTS THAT MOVE WITH IT.
 *
 * The reviewer read the age-range, gender, ethnic-group and wellbeing charts against the live
 * DEV portal and found the category labels too small. They were 12px — below every step of
 * this app's own type scale, which starts at `--text-xs` 13px.
 *
 * **15px, which is `--text-sm` in `styles/ds-tokens.css`.** An SVG `fontSize` takes a raw
 * number and cannot read a CSS custom property, so the token is named here rather than
 * referenced: 15px is the value `--text-sm` declares, and it is the same step
 * `.viewNavButton`, `ds/Button`'s whole size ladder and `.inputLabel` already set their type
 * at. `--text-base` (17px) was rejected: it is the app's BODY size, and an axis tick that
 * equals body text competes with the figures it labels rather than annotating them.
 *
 * **`TICK_LINE_HEIGHT` MOVES IN THE SAME CHANGE, AND THAT IS THE POINT (`IMP-0509`,
 * `C-TECH-076` check A).** This constant is the `dy` between wrapped `<tspan>` lines — the
 * line box, in SVG user units — so raising the glyph size without raising it paints 15px
 * glyphs into a 12px line box and every two- and three-line category label overlaps itself.
 * That defect is invisible here: jsdom computes no layout, `tsc` and eslint see two unrelated
 * numbers, and the only place it shows is a rendered screen — which is exactly how `IMP-0509`
 * was found (a wrapped `StatTile` value overlapping its own second line) one revision ago.
 * 20 is `--leading-snug` (1.3) applied to 15px, rounded to a whole user unit: 19.5 → 20, the
 * same ratio `.panelHeading` uses for the same reason.
 *
 * `CATEGORY_AXIS_HEIGHT` is derived from `TICK_LINE_HEIGHT` below, so it follows on its own —
 * but the two CHART HEIGHTS do not: the axis grows by 24px (56 → 80) and the chart heights
 * are fixed, so each chart's plot area is raised by the same 24px rather than being silently
 * shortened.
 */
/**
 * REVISION 11 (2026-09-02, wbs:6.8), REVIEWER ITEM 1 — 15px → 13px, WHICH IS A SCALE-DOWN
 * WITHIN THE APP'S OWN TYPE SCALE AND NOT A REVERSAL OF REVISION 9.
 *
 * The reviewer's words this round: *"Charts sometimes overflow the screen with scrollbars —
 * not desirable. Scale the charts down so both charts in a row are fully visible side by side;
 * scale down label text size on those specific charts if needed."* That is an explicit licence
 * to move this constant, and it trades directly against Revision 9's own item 2 (12px → 15px),
 * so the trade is stated rather than made quietly:
 *
 *   - **Revision 9's complaint was that 12px is BELOW EVERY STEP of this app's type scale**,
 *     which starts at `--text-xs` 13px. 13px is that first step. The label size therefore
 *     stays ON the scale — it is not a return to the off-scale 12px Revision 9 rejected.
 *   - **What is NOT reverted**: the derivation. `IMP-0577`'s rule (one shared pixel-width
 *     basis, never independent per-chart heuristics) and `IMP-0509`'s rule (a font-size change
 *     carries its line box with it) are both stronger after this change than before, because
 *     `TICK_LINE_HEIGHT` and `TICK_GLYPH_WIDTH_PX` below are now COMPUTED from this constant
 *     rather than being two further numbers a later editor has to remember to move.
 *
 * The width this buys is roughly 13% per column, and it is only part of item 1's answer — the
 * rest is `categoryAxisPlan`'s per-chart wrap budget and `CHART_WIDTH_BUDGET`, below.
 */
const TICK_FONT_SIZE = 13;

/**
 * Line box for a `TICK_FONT_SIZE` tick label, in SVG user units — `--leading-snug` (1.3)
 * applied to the glyph size and rounded up to a whole unit.
 *
 * **DERIVED, not a literal, as of Revision 11.** It was a hand-kept 20 beside a hand-kept 15,
 * with a comment reading "NEVER edit this without editing `TICK_FONT_SIZE`, or the reverse" —
 * which is exactly the coupling `IMP-0509` exists to enforce and exactly the shape that fails
 * the moment somebody edits one of them. Computing it removes the instruction and the
 * opportunity together.
 */
const TICK_LINE_HEIGHT = Math.ceil(TICK_FONT_SIZE * 1.3);

/**
 * REVISION 12 (2026-09-02) — THE GAP BETWEEN THE PLOT AREA AND THE FIRST LABEL LINE, NAMED AND
 * TIED TO THE SAME FIGURE THE REST OF THE APP ALREADY USES FOR "ROOM BELOW ONE CONTROL BEFORE
 * THE NEXT" — `--space-4` (16px), the collapsed margin `app.module.css`'s `.landingNav` and
 * `.refreshBar` leave between "Open the applications list" and "Refresh figures".
 *
 * The reviewer's complaint was that the x-axis label text still overlaps the bottom of the
 * chart despite Revision 11 item 5's fix. That fix reserved room by BASELINE — the tick's
 * first `<text>` had `dy={TICK_LINE_HEIGHT}` (17), which is a LINE HEIGHT, not a designed gap,
 * and a baseline 17px below the axis line puts the GLYPH TOPS only `17 - TICK_ASCENT_PX` below
 * it, because a baseline offset leaves the ascent sitting above it. `TICK_ASCENT_PX` estimates
 * that ascent the same way `TICK_DESCENDER_SLACK` already estimates the equivalent space below
 * the last line's baseline — a sans-serif face's ascent is conventionally ~0.8em.
 *
 * `AXIS_LABEL_GAP` is what closes that: the first line's `dy` is now
 * `AXIS_LABEL_GAP + TICK_ASCENT_PX`, so the visible white space from the plot's lower edge to
 * the top of the first glyph is `AXIS_LABEL_GAP` itself — 16px, matching `BAR_CHART_MARGIN`'s
 * and `COMPARISON_CHART_MARGIN`'s own `bottom: 16` below by the same figure, not a coincidence:
 * both sides of the axis band now carry the identical, named, `--space-4` gap.
 */
export const AXIS_LABEL_GAP = 16;

/** The ascent `AXIS_LABEL_GAP` has to clear above the first line's own baseline — see that
    constant's comment. Same 0.8em heuristic in spirit as `TICK_DESCENDER_SLACK`'s 0.35em. */
const TICK_ASCENT_PX = Math.ceil(TICK_FONT_SIZE * 0.8);

/** The first wrapped line's `dy` from the axis line — `AXIS_LABEL_GAP`'s own comment has the
    arithmetic. Every subsequent line still steps by the plain `TICK_LINE_HEIGHT`. */
const FIRST_TICK_LINE_DY = AXIS_LABEL_GAP + TICK_ASCENT_PX;

/**
 * The greedy wrap budget, in characters.
 *
 * A character budget rather than a measured one BY NECESSITY: `getComputedTextLength` is the
 * only exact answer and jsdom implements none of the SVG text-measurement API, so a measured
 * tick would be untestable — the same `IMP-0111` trap this file's header names for
 * Recharts' own `<Legend>`.
 *
 * **DELIBERATELY UNCHANGED AT 18 BY REVISION 9's TYPE-SIZE INCREASE.** 18 characters × 3 lines
 * is a 54-character budget, and `APPLICANT_TYPE_LABELS`' longest option is 46 — so no label in
 * any option set this app declares reaches the ellipsis branch today. Cutting the budget to
 * hold the same PIXEL width at 15px would need ~15 characters per line, a 45-character budget,
 * and would push that 46-character label into the one lossy path this file has. The width the
 * labels need is bought below instead, by scaling the chart's own width constants by the same
 * 15/12 the type grew by — the axis gets wider, not the labels shorter.
 */
const TICK_CHARS_PER_LINE = 18;

/**
 * The floor `categoryAxisPlan` clamps a per-chart wrap budget to.
 *
 * Below about eight characters a greedy word wrap stops being a wrap and starts being a column
 * of single words — `AGE_RANGE_LABELS`' "75 and over" would become three lines of one word
 * each — and the axis grows taller faster than it grows narrower. Eight is where the four
 * option sets this app declares still wrap at word boundaries a reader recognises.
 */
const MIN_TICK_CHARS_PER_LINE = 8;

/**
 * REVIEWER ITEM 1 (Revision 11, 2026-09-02, wbs:6.8) — THE PIXEL BUDGET A CHART IS FITTED
 * INTO, AND THE ONE FIGURE EVERY PER-CHART WIDTH BELOW IS NOW DERIVED FROM.
 *
 * The reviewer read the live DEV portal and found charts overflowing their `.tableScroll` box
 * and scrolling sideways, where two charts in an `.applicantGrid` row should both be fully
 * visible. The root cause is that every width constant in this file was a FLOOR (`Math.max`
 * against a per-category column) with no ceiling anywhere: an eleven-score or nine-band axis
 * multiplied a fixed column width and produced whatever it produced, and nothing in the file
 * knew how much room the grid cell it lands in actually has.
 *
 * 620px is that missing figure. It is measured, not guessed: at the 1440px width this portal
 * is read at, `.page`'s padding clamps to `--space-12` (48px) a side, `.panel` adds
 * `--space-6` (24px) a side, and `.applicantGrid` splits what is left in two across a
 * `--space-8` (32px) gap — 1440 − 96 − 48 − 32, halved, is 632.
 *
 * **IT IS A BUDGET, NOT A CLAMP, AND THAT DISTINCTION IS DELIBERATE.** `categoryAxisPlan`
 * below wraps a chart's labels TIGHTER until the chart fits the budget, and stops at
 * `MIN_TICK_CHARS_PER_LINE`; it never returns a column narrower than the label line it has to
 * hold. Truncating the width instead would reproduce, exactly, the overlapping labels
 * `IMP-0577` was raised for. A label set long enough to blow the budget at the minimum wrap
 * therefore still overflows — and still scrolls inside `.tableScroll`, never the page (WCAG
 * 1.4.10) — which is the correct failure direction: unreadable-because-scrolling beats
 * unreadable-because-overlapping. No option set this app declares reaches it (the widest,
 * `ETHNIC_GROUP_LABELS`' six options, lands at 612px).
 */
const CHART_WIDTH_BUDGET = 620;

/**
 * Greedy word wrap for one category label. Exported for its own unit test — the ellipsis
 * branch is the only place in this file that can lose a character, so it is asserted
 * directly rather than inferred from rendered `<tspan>`s.
 *
 * A word longer than the budget is never broken mid-word: it takes a line of its own and
 * overflows it. Hyphenating `APPLICANT_TYPE_LABELS`' wording would invent a word that is not
 * the category's name.
 */
export function wrapTickLabel(
  text: string,
  charsPerLine: number = TICK_CHARS_PER_LINE,
  maxLines: number = TICK_MAX_LINES,
): string[] {
  const words = text.split(/\s+/).filter((word) => word.length > 0);
  if (words.length === 0) return [];

  const lines: string[] = [];
  let current = "";
  for (const word of words) {
    const candidate = current === "" ? word : `${current} ${word}`;
    if (current === "" || candidate.length <= charsPerLine) {
      current = candidate;
    } else {
      lines.push(current);
      current = word;
    }
  }
  lines.push(current);

  if (lines.length <= maxLines) return lines;
  const kept = lines.slice(0, maxLines);
  const last = kept[maxLines - 1] ?? "";
  kept[maxLines - 1] = `${last.slice(0, Math.max(0, charsPerLine - 1)).trimEnd()}…`;
  return kept;
}

/**
 * Recharts clones the element passed as `tick` with the axis' own `x`/`y`/`payload`, so
 * these props are all optional: nothing in this file ever constructs one with values.
 */
interface CategoryTickProps {
  x?: number;
  y?: number;
  payload?: { value?: string | number };
  /**
   * The per-chart wrap budget `categoryAxisPlan` computed for THIS chart (Revision 11, item
   * 1). Passed by the call site as a prop on the element handed to `<XAxis tick={…}>`;
   * Recharts clones that element with its own `x`/`y`/`payload` and merges rather than
   * replaces, so a prop set here survives the clone. It defaults to `TICK_CHARS_PER_LINE`,
   * which is what the tick wrapped to before a plan existed at all.
   *
   * **The chart's width and its ticks MUST take the same figure**, which is why it travels as
   * one plan object rather than as two call sites each choosing a number — a column sized to
   * one budget and a label wrapped to another is `IMP-0577`'s defect with extra steps.
   */
  charsPerLine?: number;
}

/** A category-axis tick that wraps rather than rotating or truncating. */
export function WrappedCategoryTick({
  x = 0,
  y = 0,
  payload,
  charsPerLine = TICK_CHARS_PER_LINE,
}: CategoryTickProps) {
  const lines = wrapTickLabel(String(payload?.value ?? ""), charsPerLine);
  return (
    <g transform={`translate(${String(x)},${String(y)})`}>
      {/*
       * REVISION 13 (2026-09-03, wbs:6.8) — THE GAP MOVES FROM THE OUTER `<text>` TO THE
       * FIRST `<tspan>`, BECAUSE A REAL CHROMIUM RENDER (Playwright, not jsdom) SHOWS THE
       * OUTER ELEMENT'S `dy` IS SILENTLY IGNORED HERE.
       *
       * Confirmed by measurement, not by re-deriving the arithmetic Revision 12 already
       * checked (IMP-0581/IMP-0584 both warned against trusting the symbolic dy sum a third
       * time). A minimal `<text dy="27"><tspan dy="0">…` fixture, rendered in real Chromium
       * with no Recharts and no React involved, places the tspan at the SAME vertical
       * position a bare `dy="0"` would — the outer `<text>`'s `dy` contributes nothing the
       * moment its first child `<tspan>` declares its OWN `dy`, even `0`. `getBoundingClientRect`
       * on `tspan` is the only thing that can see this: jsdom computes no SVG text layout at
       * all, so no vitest assertion — including Revision 11 item 5's own translateY+dy check —
       * could ever have caught it; that check reads the SAME two attributes this bug leaves
       * numerically self-consistent, which is exactly why it passed throughout.
       *
       * The fix: give the FIRST tspan the `dy` `FIRST_TICK_LINE_DY` used to carry on `<text>`,
       * and set nothing on `<text>` itself. Every subsequent tspan's `dy={TICK_LINE_HEIGHT}`
       * is unaffected — SVG cumulative tspan-to-tspan `dy` is confirmed working by the same
       * real-browser fixture (a lone tspan with its own `dy` renders where its `dy` says).
       */}
      <text textAnchor="middle" fontSize={TICK_FONT_SIZE} fill="#4a4a4a">
        {lines.map((line, index) => (
          <tspan
            key={`${String(index)}-${line}`}
            x={0}
            dy={index === 0 ? FIRST_TICK_LINE_DY : TICK_LINE_HEIGHT}
          >
            {line}
          </tspan>
        ))}
      </text>
    </g>
  );
}

/**
 * Descender slack under the last wrapped line — the part of a glyph that hangs BELOW its
 * baseline, which `TICK_MAX_LINES * TICK_LINE_HEIGHT` alone does not account for because a
 * line box is measured baseline to baseline.
 */
const TICK_DESCENDER_SLACK = Math.ceil(TICK_FONT_SIZE * 0.35);

/**
 * Axis height for `TICK_MAX_LINES` wrapped lines plus the tick's own first-line offset plus
 * the last line's descenders. DERIVED, never a literal, so a `TICK_FONT_SIZE` change carries
 * it without a second edit — the coupling `IMP-0509` exists to enforce.
 *
 * **REVIEWER ITEM 5 (Revision 11, wbs:6.8) IS THE `TICK_DESCENDER_SLACK` TERM AND THE `bottom`
 * MARGINS BELOW, NOT THIS MULTIPLICATION.** The reviewer saw x-axis labels running into the
 * bottom of the plot area. The old figure was `TICK_MAX_LINES * TICK_LINE_HEIGHT + 20` — at
 * Revision 10's values, 3 × 20 + 20 = 80, where the tick's own first-line `dy` already spends
 * 20 of it: the axis band reserved room for the offset and for three baselines and for nothing
 * at all after the third, so the last line's descenders sat outside the band Recharts had
 * subtracted from the plot. That is the overlap, and it is arithmetic rather than a rendering
 * quirk: the "+20" was the first-line offset wearing the descender's clothes.
 *
 * REVISION 12 replaces the leading `TICK_LINE_HEIGHT` term with `FIRST_TICK_LINE_DY`
 * (`AXIS_LABEL_GAP`'s own comment, above, has the reasoning): the band's first term is now the
 * actual first-line offset the tick renders at, not a second, independent guess at it.
 */
const CATEGORY_AXIS_HEIGHT =
  FIRST_TICK_LINE_DY + TICK_MAX_LINES * TICK_LINE_HEIGHT + TICK_DESCENDER_SLACK;

/**
 * The width one CHARACTER of a wrapped tick line renders at, in pixels — `IMP-0577`'s single
 * shared basis, now derived from `TICK_FONT_SIZE` rather than being a second hand-kept number
 * beside it (0.6 em is the conventional average advance width for a sans-serif face, and at
 * the previous 15px it produced exactly the 9px this constant was hand-set to).
 *
 * Not a measured value — `getComputedTextLength` is unavailable under jsdom, the same reason
 * `wrapTickLabel` stays character-budgeted rather than pixel-budgeted.
 */
const TICK_GLYPH_WIDTH_PX = TICK_FONT_SIZE * 0.6;

/** What `categoryAxisPlan` hands a chart: one wrap budget, one width, agreed by construction. */
export interface CategoryAxisPlan {
  /** The budget BOTH the tick's wrap and the chart's width were computed from. */
  charsPerLine: number;
  /** The chart's own `width` prop, in pixels. */
  width: number;
}

/**
 * REVIEWER ITEM 1 (Revision 11, 2026-09-02, wbs:6.8) — FIT A CHART TO `CHART_WIDTH_BUDGET` BY
 * WRAPPING ITS LABELS TIGHTER, AND SIZE ITS COLUMNS FROM THE LABELS IT ACTUALLY HAS.
 *
 * Two defects in one function, and they are the same defect from opposite ends:
 *
 *   1. **Every chart paid for the WORST label set in the app.** `MIN_CATEGORY_COLUMN_WIDTH`
 *      was `TICK_CHARS_PER_LINE * TICK_GLYPH_WIDTH_PX` — 162px, the width of a FULL 18-character
 *      line — applied to every chart including `LIFE_SATISFACTION_LABELS`, whose eleven labels
 *      are "0" to "10" and never exceed two characters. Eleven 162px columns is 1782px of
 *      chart for a two-character axis. Sizing from the longest line the chart's OWN labels
 *      actually wrap to is not a per-chart heuristic — `IMP-0577`'s prohibition — it is the
 *      SAME formula (`characters × TICK_GLYPH_WIDTH_PX`) applied to real data instead of to a
 *      worst case, and both per-chart constants still resolve through this one function.
 *   2. **Nothing had a ceiling.** See `CHART_WIDTH_BUDGET` above. The budget divided by the
 *      category count gives the per-column pixels available, and dividing THAT by the glyph
 *      width gives the characters a line may hold — so the wrap budget is chosen by the space
 *      the chart has, and the column is then sized to hold the result. `MIN_TICK_CHARS_PER_LINE`
 *      stops that spiralling into one word per line on a many-category axis.
 *
 * `minColumnWidth` is the caller's floor for the BARS rather than for the labels — a
 * two-character label needs 16px of text and a legible bar needs more than that — so it is
 * the one figure a caller supplies and the reason this takes a parameter at all.
 *
 * Exported for its own unit test: it is arithmetic that jsdom cannot observe rendered, so it
 * is asserted directly rather than inferred from a chart's `width` attribute alone.
 */
export function categoryAxisPlan(
  labels: string[],
  minColumnWidth: number,
  minChartWidth: number,
): CategoryAxisPlan {
  const count = Math.max(1, labels.length);
  const charsPerLine = Math.min(
    TICK_CHARS_PER_LINE,
    Math.max(
      MIN_TICK_CHARS_PER_LINE,
      Math.floor(CHART_WIDTH_BUDGET / count / TICK_GLYPH_WIDTH_PX),
    ),
  );
  const longestLine = labels
    .flatMap((label) => wrapTickLabel(label, charsPerLine, TICK_MAX_LINES))
    .reduce((longest, line) => Math.max(longest, line.length), 0);
  const columnWidth = Math.max(minColumnWidth, Math.ceil(longestLine * TICK_GLYPH_WIDTH_PX));
  return { charsPerLine, width: Math.max(minChartWidth, count * columnWidth) };
}

/**
 * The Y-axis tick's type size. The same 15px `--text-sm` step as the category ticks, and it
 * is a SEPARATE literal in Recharts' API (`tick={{ fontSize }}` on `<YAxis>`, an object, not
 * this file's `WrappedCategoryTick` element) — which is precisely why it is named here rather
 * than typed twice: the reviewer's "chart label font size" covers both axes, and two
 * hardcoded 12s in one file is how one of them gets missed.
 *
 * No coupled line-height: a percentage tick ("100%") is a single line that never wraps.
 */
const VALUE_AXIS_TICK = { fontSize: TICK_FONT_SIZE };

/* ------------------------------------------------------------------------------------- *
 * The percentage axis, shared by both bar charts.
 * ------------------------------------------------------------------------------------- */

/**
 * `[0, "auto"]`, not `[0, 100]`.
 *
 * The integrity rule is that a bar's baseline is ZERO — a truncated baseline makes a 2-point
 * difference look like a doubling, and it is the one axis choice that actively misleads. The
 * TOP is left to the data: `LIFE_SATISFACTION_LABELS`' eleven scores each land near 9%, and
 * pinning that axis at 100 would draw eleven near-invisible stubs in the name of a rigour the
 * zero baseline already supplies. Every value is also text in the table beside the chart, so
 * the absolute figure is never read off the axis in the first place.
 */
const PERCENT_DOMAIN: [number, "auto"] = [0, "auto"];

function percentTick(value: number): string {
  return `${String(value)}%`;
}

/**
 * The tooltip's own formatter. Typed against Recharts' `ValueType` — which is
 * `number | string | (number | string)[] | undefined` — rather than `number`, because that is
 * genuinely what a tooltip can be handed: a `null` percentage arrives here as `undefined`,
 * and it must render as an em dash rather than as the string "undefined%". Narrowing the
 * parameter to `number` does not typecheck, and casting it would have hidden exactly the case
 * this app cares most about (TAD §3.3 point 3).
 */
function percentTooltip(value: unknown): string {
  return typeof value === "number" ? percentTick(value) : "—";
}

/**
 * Revision 9's item 2 raised this floor 440 → 550 to buy room for bigger labels. Revision 11's
 * item 1 lowers it to 460, which is the same lever pulled the other way at the reviewer's own
 * direction: a floor of 550 in a 620px budget left a four-category chart nearly as wide as the
 * grid cell it sits in for no reason, since it is a FLOOR and not a measurement of anything.
 * `categoryAxisPlan` sizes every chart above it from its own labels; this only stops a
 * two-category distribution rendering as a pair of stripes.
 */
const BAR_CHART_MIN_WIDTH = 460;

/**
 * The narrowest a single-series bar's own column may be, whatever its label needs.
 * `LIFE_SATISFACTION_LABELS`' "0"–"10" wrap to two characters, ~16px, and a 16px column is a
 * bar nobody can read — so the BAR sets this floor, not the label. 44px is this app's own
 * target-size step (WCAG 2.5.5's figure, borrowed here as a legibility floor rather than as a
 * hit area: nothing in these charts is interactive).
 */
const MIN_BAR_COLUMN_WIDTH = 44;

/**
 * PLOT AREA HEIGHT — the drawing area itself, held CONSTANT across every revision that has
 * moved the axis band around it.
 *
 * Revision 9 and Revision 10 both hand-adjusted a total chart height each time the axis grew
 * ("300 → 324, the same +24 `CATEGORY_AXIS_HEIGHT` takes"), which is the arithmetic that goes
 * wrong the once nobody does it. The total is now derived from this figure, the margins and
 * `CATEGORY_AXIS_HEIGHT` instead, so item 5's taller axis band cannot be paid for out of the
 * plot area by accident. 228 is exactly what Revision 10's 324 total resolved to.
 */
const BAR_PLOT_AREA_HEIGHT = 228;

/**
 * REVIEWER ITEM 5 (Revision 11, wbs:6.8) — `bottom` 8 → 16. The other half of "move the labels
 * down so they render clearly below the chart": `CATEGORY_AXIS_HEIGHT` gives the tick lines
 * room WITHIN the axis band, and this gives the band itself room below the plot area, so the
 * bottom-most line is not flush against the edge of the SVG.
 */
const BAR_CHART_MARGIN = { top: 8, right: 16, bottom: 16, left: 8 };
const BAR_CHART_HEIGHT =
  BAR_PLOT_AREA_HEIGHT + BAR_CHART_MARGIN.top + BAR_CHART_MARGIN.bottom + CATEGORY_AXIS_HEIGHT;

/**
 * A single-series VERTICAL bar chart — category on the x-axis, share of the round on the
 * y-axis, bars growing upward. Row order is `series.rows`' own, unchanged from the table
 * beside it.
 *
 * `dataKey="percentage"`, not `count` (Revision 8 point 1). A row whose percentage is `null`
 * draws NO BAR at all, which is the same absence the table beside it renders as the words
 * "Not recorded" — a zero-height bar would assert a measurement of 0%, and on this screen
 * "a zero is a finding; a null is an absence" (TAD §3.3 point 3).
 *
 * One series only — see this file's header and `domain/charts.ts`'s own header for why
 * gender, age range and life satisfaction stay single-series here.
 */
export function CategoryBarChart({ series }: { series: Series }) {
  const plan = categoryAxisPlan(
    series.rows.map((row) => row.label),
    MIN_BAR_COLUMN_WIDTH,
    BAR_CHART_MIN_WIDTH,
  );
  return (
    <div className={styles.tableScroll} aria-hidden="true" data-print="chart">
      <BarChart
        width={plan.width}
        height={BAR_CHART_HEIGHT}
        data={series.rows}
        margin={BAR_CHART_MARGIN}
        accessibilityLayer={false}
      >
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis
          dataKey="label"
          interval={0}
          height={CATEGORY_AXIS_HEIGHT}
          tick={<WrappedCategoryTick charsPerLine={plan.charsPerLine} />}
        />
        <YAxis domain={PERCENT_DOMAIN} tickFormatter={percentTick} tick={VALUE_AXIS_TICK} />
        <Tooltip formatter={percentTooltip} />
        <Bar
          dataKey="percentage"
          name="Share of round"
          fill={categoricalColor(0)}
          isAnimationActive={false}
          radius={[4, 4, 0, 0]}
        />
      </BarChart>
    </div>
  );
}

/**
 * REVIEWER ITEM 4 (Revision 11, 2026-09-02, wbs:6.8) — THE PIE'S BOX IS NOW WIDER THAN IT IS
 * TALL, BECAUSE ITS DATA LABELS ARE DRAWN OUTSIDE THE CIRCLE AND WERE BEING CLIPPED.
 *
 * The reviewer: *"The Applicant Type pie chart's legend/data labels don't have enough width for
 * their text — it's being clipped or wrapped badly."* Two separate causes, and both are fixed
 * (the legend half is in `app.module.css`'s `.chartLegend`):
 *
 * A `<Pie label={…}>` renders each slice's text OUTSIDE `outerRadius`, on a leader line, with
 * the text anchored away from the centre. On a 280×280 square with `cx="50%"` the centre is at
 * 140 and the radius is 100, so a label on the 3-o'clock flank starts at ~125px from centre and
 * runs outward — past the 140px the box actually has. Every horizontal-flank label was
 * therefore clipped at the SVG edge. The circle is unchanged; the BOX around it is wider, which
 * is the only thing the labels were short of. It stays inside `CHART_WIDTH_BUDGET`.
 *
 * The height stays 280 — a pie's vertical flank labels sit at 12 and 6 o'clock where the anchor
 * is centred and the overflow is one line of type, not a whole label's width.
 */
const PIE_WIDTH = 400;
const PIE_HEIGHT = 280;
const PIE_OUTER_RADIUS = 100;

/**
 * A composition pie — applicant type's three-way split (FR-061), the one distribution
 * this pass' deck shows as a pie rather than a bar. `series.rows`' own order supplies
 * slice order, so the pie and the accessible table beside it list categories the same
 * way; colour is assigned by that same order, in `CHART_PALETTE`'s fixed sequence.
 *
 * `dataKey="percentage"` (Revision 8 point 1), and the slice LABEL is the row's own
 * `percentage` rather than Recharts' computed `percent`. The two are not the same number:
 * `percent` is this slice's share of the values actually plotted, so a distribution whose
 * categories do not sum to the whole round — one category reported `null`, or the flow
 * having withheld one — would relabel every remaining slice to sum to 100% and read as a
 * complete picture of the round. Rendering the response's own figure keeps the arithmetic
 * the flow computed and lets the slices sum to less than 100% when that is the truth.
 */
export function CompositionPieChart({ series }: { series: Series }) {
  const legendItems = series.rows.map((row, index) => ({
    label: row.label,
    color: categoricalColor(index),
  }));
  return (
    /*
     * `styles.tableScroll`, ADDED IN REVISION 11 — and it is a CORRECTION, not a new decision.
     * This file's own header has always said that "every chart below takes a FIXED pixel size
     * instead and sits inside `styles.tableScroll` … so a chart wider than a narrow viewport
     * scrolls sideways in its own box rather than the page (WCAG 1.4.10)". Every chart except
     * this one did. A fixed-width SVG in a grid cell narrower than itself overflows its
     * container, and with no `overflow-x` anywhere between it and `.page` that overflow reaches
     * the page body — the exact failure the sentence promises does not happen. It was latent at
     * 280px and item 4's 400px would have made it reachable at more widths, so it is fixed here
     * rather than left for the next reviewer to find. Logged separately as a
     * `document-contradicts-source` finding; see the Dev Summary.
     */
    <div className={styles.tableScroll} aria-hidden="true" data-print="chart">
      <PieChart width={PIE_WIDTH} height={PIE_HEIGHT} accessibilityLayer={false}>
        <Pie
          data={series.rows}
          dataKey="percentage"
          nameKey="label"
          cx="50%"
          cy="50%"
          outerRadius={PIE_OUTER_RADIUS}
          stroke="#fff"
          strokeWidth={2}
          isAnimationActive={false}
          rootTabIndex={-1}
          label={({ payload }: { payload?: { percentage?: number | null } }) => {
            const share = payload?.percentage;
            // A null percentage labels nothing — never "0%", which would be a figure the
            // response did not report. Same rule as the bar charts above.
            return share === null || share === undefined ? "" : `${share.toFixed(1)}%`;
          }}
        >
          {series.rows.map((row, index) => (
            <Cell key={row.value} fill={categoricalColor(index)} />
          ))}
        </Pie>
        <Tooltip formatter={percentTooltip} />
      </PieChart>
      <ChartLegend items={legendItems} />
    </div>
  );
}

/** 560 → 480, Revision 11 item 1 — the same lever, and the same reason, as `BAR_CHART_MIN_WIDTH`. */
const COMPARISON_CHART_MIN_WIDTH = 480;
/**
 * The narrowest a RESPONSE-CATEGORY group may be, whatever its label needs — the counterpart to
 * `MIN_BAR_COLUMN_WIDTH` above, and larger than it because a group here holds THREE bars (one
 * per FR-062 question) rather than one. Three legible bars plus the gutters between them is
 * where 96 comes from; the label floor is `categoryAxisPlan`'s job, not this constant's.
 */
const MIN_COMPARISON_GROUP_WIDTH = 96;
/** The comparison chart's own plot area, held constant the same way `BAR_PLOT_AREA_HEIGHT` is. */
const COMPARISON_PLOT_AREA_HEIGHT = 268;
/** Item 5's `bottom` step, identical to `BAR_CHART_MARGIN`'s and for the identical reason. */
const COMPARISON_CHART_MARGIN = { top: 8, right: 16, bottom: 16, left: 8 };
const COMPARISON_CHART_HEIGHT =
  COMPARISON_PLOT_AREA_HEIGHT +
  COMPARISON_CHART_MARGIN.top +
  COMPARISON_CHART_MARGIN.bottom +
  CATEGORY_AXIS_HEIGHT;

/**
 * FR-062's genuinely multi-series chart, pivoted back in Revision 10 (wbs:6.8): **one vertical
 * bar GROUP per agreement-response category, one bar per wellbeing question** — exactly three
 * bars per group, one per question (reviewer item 3) — so a trustee reads each response
 * option's whole across-question shape in one group and compares the six groups against each
 * other bar-position by bar-position. `domain/charts.ts`'s own Revision 10 header carries the
 * axis-assignment reasoning; this is Revision 3's original shape, restored.
 *
 * See `domain/charts.ts`'s header for why this is NOT the withdrawn FR-061 benchmark shape:
 * the pivot redistributes the SAME `wellbeingLastYear.questions` array across a pair of axes
 * and adds no series the response did not already carry.
 *
 * **It colours by QUESTION IDENTITY, `categoricalColor(index)`, not by scale position.** A
 * question is a plain identity here, not a point on an ordered scale — the property that made
 * Revision 8's ordinal ramp correct belonged to the OTHER axis assignment, where a series was a
 * response category. FR-062 never declares more than three questions, which is exactly
 * `CHART_PALETTE`'s validated slot count, so no wrap is ever reached in practice.
 *
 * **Its values are percentages, so three questions with three different populations are
 * comparable at all.** A count axis could not compare them; that is what makes the percentage
 * the correct measure for this pivot.
 */
export function WellbeingComparisonChart({ data }: { data: WellbeingComparisonData }) {
  const legendItems = data.series.map((series, index) => ({
    label: series.heading,
    color: categoricalColor(index),
  }));
  const plan = categoryAxisPlan(
    data.rows.map((row) => row.label),
    MIN_COMPARISON_GROUP_WIDTH,
    COMPARISON_CHART_MIN_WIDTH,
  );
  return (
    <div className={styles.tableScroll} aria-hidden="true" data-print="chart">
      <BarChart
        width={plan.width}
        height={COMPARISON_CHART_HEIGHT}
        data={data.rows}
        margin={COMPARISON_CHART_MARGIN}
        accessibilityLayer={false}
      >
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        {/* The category axis is the RESPONSE OPTIONS again (reviewer item 3) — their own
            literal wording, via the same wrapped tick every other chart in this file uses. */}
        <XAxis
          dataKey="label"
          interval={0}
          height={CATEGORY_AXIS_HEIGHT}
          tick={<WrappedCategoryTick charsPerLine={plan.charsPerLine} />}
        />
        <YAxis domain={PERCENT_DOMAIN} tickFormatter={percentTick} tick={VALUE_AXIS_TICK} />
        <Tooltip formatter={percentTooltip} />
        {data.series.map((series, index) => (
          <Bar
            key={series.key}
            dataKey={series.key}
            name={series.heading}
            fill={categoricalColor(index)}
            isAnimationActive={false}
            radius={[4, 4, 0, 0]}
          />
        ))}
      </BarChart>
      <ChartLegend items={legendItems} />
    </div>
  );
}
