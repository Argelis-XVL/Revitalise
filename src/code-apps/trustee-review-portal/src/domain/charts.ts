/**
 * Chart-only derivations for the round-statistics screen — Fix 3 of the 2026-08-27
 * "close the visual gap" pass (the app compared against `Round 3 Stats.pptx` /
 * `Round 4.pptx` read as "v0.1, not v0.9").
 *
 * Kept separate from `domain/landing.ts` on purpose: `landing.ts` already carries the
 * FR-056..FR-063 state machine and `Series`/`buildSeries`, both heavily documented and
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
 * The one genuinely multi-series chart this file builds data for —
 * `buildWellbeingComparisonData` — is not that withdrawn shape. Every series in it is
 * a real, already-collected distribution (one per FR-062 "last year" wellbeing
 * question, sharing one response scale), not a synthetic or external comparator.
 */
import { AGREEMENT_RESPONSE_LABELS, WELLBEING_QUESTION_HEADINGS, optionLabel } from "../dataverse/schema";
import type { WellbeingLastYear } from "../dataverse/types";

/**
 * One agreement-response category's count for every wellbeing question, keyed by
 * that question's own column name — Recharts' own "long-format pivoted to wide"
 * shape, one row per category and one property per series.
 */
export interface WellbeingComparisonRow {
  value: number;
  label: string;
  [column: string]: string | number;
}

/** One series of the comparison chart — a question's column name and its heading. */
export interface WellbeingSeriesDefinition {
  /** The response's own column name (`WellbeingQuestion.column`) — also the key each row's count sits under. */
  key: string;
  /** `WELLBEING_QUESTION_HEADINGS[key]`, or the raw column name on drift — same rule `RoundStatistics.tsx` already applies per question. */
  heading: string;
}

export interface WellbeingComparisonData {
  rows: WellbeingComparisonRow[];
  series: WellbeingSeriesDefinition[];
}

/**
 * Pivots FR-062's "last year" wellbeing questions into one Recharts-ready dataset:
 * one row per `AGREEMENT_RESPONSE_LABELS` category, one property per question.
 *
 * `null`/no questions in, `null` out — the same absence rule every other
 * round-statistics figure follows (TAD §3.3 point 3): a chart with no data behind it
 * renders nothing, not an empty frame.
 *
 * The category axis is `AGREEMENT_RESPONSE_LABELS`'s own six values, in that map's
 * order, regardless of which categories any one question's response happened to
 * carry — so two questions are compared on the SAME axis, with a category a question
 * did not report read as 0 for that question rather than the row disappearing from
 * the axis (which would silently misalign the other questions' bars against it).
 */
export function buildWellbeingComparisonData(
  wellbeing: WellbeingLastYear | null,
): WellbeingComparisonData | null {
  if (wellbeing === null || wellbeing.questions.length === 0) return null;

  const series: WellbeingSeriesDefinition[] = wellbeing.questions.map((question) => ({
    key: question.column,
    heading: WELLBEING_QUESTION_HEADINGS[question.column] ?? question.column,
  }));

  const categoryValues = Object.keys(AGREEMENT_RESPONSE_LABELS)
    .map(Number)
    .sort((a, b) => a - b);

  const rows: WellbeingComparisonRow[] = categoryValues.map((value) => {
    const row: WellbeingComparisonRow = {
      value,
      label: optionLabel(AGREEMENT_RESPONSE_LABELS, value),
    };
    for (const question of wellbeing.questions) {
      const match = question.categories.find((category) => category.value === value);
      row[question.column] = match?.count ?? 0;
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
 */
export const CHART_PALETTE = ["#ed008c", "#8e4fc4", "#009aa8"] as const;

/**
 * The fixed-order categorical hue for slot `index` (0-based) — "assign categorical
 * hues in fixed order, never cycled" (`skills/dataviz`).
 *
 * Wrapping past the validated three is a last resort this app's own option sets never
 * actually reach: every distribution charted through this module — gender, age range,
 * applicant type, the three wellbeing questions — is a small, fixed, transcribed set
 * in `dataverse/schema.ts`. A wrap is the same "more categories arrived than this
 * build has ever declared" drift `optionLabel`'s `Unknown (n)` already renders visibly
 * elsewhere, not a new failure mode.
 */
export function categoricalColor(index: number): string {
  return CHART_PALETTE[index % CHART_PALETTE.length] ?? CHART_PALETTE[0];
}
