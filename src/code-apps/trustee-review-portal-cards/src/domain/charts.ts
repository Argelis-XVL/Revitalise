/**
 * Chart-only derivations for the round-statistics screen — Fix 3 of the 2026-08-27
 * "close the visual gap" pass (the app compared against `Round 3 Stats.pptx` /
 * `Round 4.pptx` read as "v0.1, not v0.9").
 *
 * Kept separate from `domain/landing.ts` on purpose: `landing.ts` already carries the
 * FR-056..FR-062 state machine and `Series`/`buildSeries`, both heavily documented and
 * heavily tested, and none of that needed to change for this pass. Everything here is
 * new, additive, presentation-only shaping consumed by the Recharts visuals in
 * `components/RoundStatisticsCharts.tsx`. It decides what shape of DATA a chart draws;
 * it never decides what a trustee is allowed to see — that remains `Series`/
 * `buildSeries`'s job, unchanged.
 *
 * ## Why there is still no second series here
 *
 * FR-061's benchmark comparison is withdrawn (`domain/landing.ts`'s `Distribution`
 * doc, ADR-029 as amended), and `LandingPage.test.tsx` asserts no chart in this app
 * carries a benchmark, a second series or a comparison column. The deck this pass was
 * measured against shows gender and age range as two-series grouped bars (this round
 * vs. a prior one), but that second series is exactly the withdrawn benchmark shape —
 * there is no "prior round" figure anywhere in this response contract to draw it from.
 * So gender, age range and life satisfaction stay single-series bar charts, matching
 * the SCOPE THIS APP ACTUALLY HAS, not the deck's pre-withdrawal design.
 *
 * `buildWellbeingComparisonData` below is not that withdrawn shape either. Every series
 * in it is a real, already-collected distribution (one per FR-062 "last year" wellbeing
 * question, sharing one response scale), not a synthetic or external comparator.
 *
 * ## Revision 10 (2026-09-02, wbs:6.8) — THE PIVOT TURNED BACK OVER
 *
 * The reviewer asked, against the live DEV portal this round, for exactly the opposite
 * axis assignment Revision 8 (2026-08-31) landed: **the six response categories on the
 * x-axis, one bar per wellbeing question within each category group** — "the x-axis
 * labels must be the literal answer options, not question numbers", "exactly three
 * vertical bars, one per wellbeing question" (per category group). That is Revision 3's
 * original shape, restored, not a new one invented for this round.
 *
 * `buildWellbeingComparisonData` is rewritten accordingly: **one row per
 * `AGREEMENT_RESPONSE_LABELS` category** (the x-axis, in scale order), and **one series
 * per question** (`wellbeing.questions`, in the order the flow sent them). A question is
 * now a SERIES with a plain categorical identity — there are at most three of them, which
 * is exactly `CHART_PALETTE`'s validated slot count, so `categoricalColor(index)` is the
 * correct colouring rule here, not the ordinal agreement ramp Revision 8 introduced for
 * the opposite axis assignment. `AGREEMENT_SCALE_RAMP` / `agreementResponseColor` /
 * `AGREEMENT_OFFSCALE_COLOR` are removed in the same change: nothing in this module calls
 * them once the axis they coloured is gone, and a validated but unused ramp is exactly
 * the "dead code that reads as a live decision" this project's own `App.tsx` Revision 9
 * precedent already refuses to leave behind.
 *
 * **A category a question did not report is still `null`, never `0`** — TAD §3.3 point 3
 * ("a zero is a finding; a null is an absence") is unchanged by which axis carries which
 * value. A `null` property on a wide-format row is present (so it aligns identically with
 * every other question's row) and draws no bar, which is the honest rendering.
 *
 * **Every value is still a PERCENTAGE, never a count** — three questions with three
 * different populations cannot be compared on a count axis, which is the property that
 * made percentage the correct measure under EITHER axis assignment and is untouched by
 * the pivot.
 */
import { AGREEMENT_RESPONSE_LABELS, WELLBEING_QUESTION_HEADINGS, optionLabel } from "../dataverse/schema";
import type { WellbeingLastYear } from "../dataverse/types";

/**
 * One response CATEGORY on the shared agreement scale — the x-axis row, in scale order.
 * Each question's own percentage sits under that question's `column` name, which is
 * already a valid, string-typed object key (`rev_wellbeinganswer8`, …) — unlike a bare
 * option-set integer, a `column` name is never read as an array index, so no synthesised
 * prefix is needed here the way the withdrawn `wellbeingResponseKey` supplied one for the
 * opposite axis assignment.
 */
export interface WellbeingComparisonRow {
  /** The option-set integer this row is — the row's identity. */
  value: number;
  /** `AGREEMENT_RESPONSE_LABELS`' own wording — the x-axis's literal label (reviewer item 3). */
  label: string;
  [questionColumn: string]: string | number | null;
}

/** One series of the comparison chart — a wellbeing question's column and heading. */
export interface WellbeingSeriesDefinition {
  /** `WellbeingLastYear.questions[].column` — the property each row's percentage sits under. */
  key: string;
  /** `WELLBEING_QUESTION_HEADINGS`' own wording, or the raw column name on drift. */
  heading: string;
}

export interface WellbeingComparisonData {
  rows: WellbeingComparisonRow[];
  series: WellbeingSeriesDefinition[];
}

/**
 * Pivots FR-062's "last year" wellbeing questions into one Recharts-ready dataset:
 * **one row per `AGREEMENT_RESPONSE_LABELS` category, one series per question.**
 *
 * `null`/no questions in, `null` out — the same absence rule every other round-statistics
 * figure follows (TAD §3.3 point 3): a chart with no data behind it renders nothing, not
 * an empty frame.
 *
 * The ROW list is `AGREEMENT_RESPONSE_LABELS`'s own six values, in that map's order,
 * regardless of which categories any one question's response happened to carry — so
 * every question is broken down on the SAME six-way scale, in the same order, and the
 * six groups are read against each other bar-position by bar-position.
 *
 * **A category a question did not report reads as `null`, not as `0`** (TAD §3.3 point 3,
 * "a zero is a finding; a null is an absence"). Recharts draws no bar for a null, which is
 * the honest rendering: a 0%-height bar and a not-reported category are the same picture,
 * and only one of them is a finding.
 */
export function buildWellbeingComparisonData(
  wellbeing: WellbeingLastYear | null,
): WellbeingComparisonData | null {
  if (wellbeing === null || wellbeing.questions.length === 0) return null;

  const categoryValues = Object.keys(AGREEMENT_RESPONSE_LABELS)
    .map(Number)
    .sort((a, b) => a - b);

  const series: WellbeingSeriesDefinition[] = wellbeing.questions.map((question) => ({
    key: question.column,
    // A question this build does not recognise still renders, under its own raw column
    // name — dropping a question the flow chose to send would be a silent omission.
    heading: WELLBEING_QUESTION_HEADINGS[question.column] ?? question.column,
  }));

  const rows: WellbeingComparisonRow[] = categoryValues.map((value) => {
    const row: WellbeingComparisonRow = {
      value,
      label: optionLabel(AGREEMENT_RESPONSE_LABELS, value),
    };
    for (const question of wellbeing.questions) {
      const match = question.categories.find((category) => category.value === value);
      row[question.column] = match?.percentage ?? null;
    }
    return row;
  });

  return { rows, series };
}

/**
 * The categorical chart palette — `skills/dataviz`'s `references/color-formula.md`.
 *
 * NOT `theme.ts`'s `REV_SECONDARY` / `REV_ACCENT` literally. Both literal brand hexes
 * fail the skill's own validator (`scripts/validate_palette.js`) for a categorical
 * mark: `#49345b` reads as near-grey (OKLCH chroma 0.070, below the 0.10 floor) and
 * `#14adbb` sits outside the dark-mode lightness band (0.683, band is ~0.48-0.67), with
 * only a 3.12:1 light-mode contrast margin at that. Slots 2 and 3 below are the SAME
 * hue families — 272° purple, 185° teal — re-stepped in lightness/chroma until the
 * validator passes in BOTH modes. That is the skill's own "snap-to-passing" procedure,
 * not a new brand choice: `REV_SECONDARY` and `REV_ACCENT` are untouched and keep
 * their existing uses (the header rule, the accent's verified text pairing).
 *
 * Slot 1 is the literal brand primary — `theme.ts`'s `brandRamp[80]`, already this
 * app's `--colorCompoundBrandBackground` / `.chartBar` fill — and it passes both
 * modes unmodified, so it is not re-stepped.
 *
 * Verified command, both required by the skill before shipping a categorical chart
 * colour: `node <dataviz-skill-base>/scripts/validate_palette.js
 * "#ed008c,#8e4fc4,#009aa8" --mode light` and `--mode dark` — both report
 * `ALL CHECKS PASS`. Re-run that command before changing any of these three values.
 *
 * Exactly three slots, and Revision 10 (above) is why that count is no longer a
 * "last resort past the validated three" for the wellbeing comparison chart specifically:
 * FR-062 declares exactly three "last year" questions, so every series that chart draws
 * fits inside the validated set with no wrap.
 */
export const CHART_PALETTE = ["#ed008c", "#8e4fc4", "#009aa8"] as const;

/**
 * The fixed-order categorical hue for slot `index` (0-based) — "assign categorical
 * hues in fixed order, never cycled" (`skills/dataviz`).
 *
 * Wrapping past the validated three is a last resort this app's own option sets never
 * actually reach: every distribution charted through this module — gender, age range,
 * applicant type, ethnic group, and (as of Revision 10) the three wellbeing questions —
 * is a small, fixed, transcribed set. A wrap is the same "more categories arrived than
 * this build has ever declared" drift `optionLabel`'s `Unknown (n)` already renders
 * visibly elsewhere, not a new failure mode.
 */
export function categoricalColor(index: number): string {
  return CHART_PALETTE[index % CHART_PALETTE.length] ?? CHART_PALETTE[0];
}
