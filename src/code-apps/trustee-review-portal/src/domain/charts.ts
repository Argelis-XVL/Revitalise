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
 *
 * ## Revision 8 (2026-08-31, wbs:6.9) — THE PIVOT TURNED OVER; THE DATA SOURCE DID NOT
 *
 * The reviewer asked, against the live DEV portal, for "one chart, three vertical-bar
 * groups (one per question) each showing its answer-label percentages". That is the
 * OPPOSITE pivot of Revision 3's: the x-axis was the six response categories with one
 * series per question, and it is now the three questions with one series per response
 * category. `buildWellbeingComparisonData` below is rewritten accordingly.
 *
 * **The paragraph above is untouched by that, and this is the point.** The withdrawn
 * FR-061 benchmark is a second DATA SOURCE — "this round vs. a prior one" — and there
 * is still no prior-round figure anywhere in this response contract to draw one from.
 * Turning the axis over redistributes the SAME `wellbeingLastYear.questions` array
 * across a different pair of axes; it adds no series this response did not already
 * carry, and it reinstates no withdrawn scope. Both shapes are legal against the same
 * contract, and the reviewer picked the second one.
 *
 * Two consequences the rewrite carries deliberately:
 *
 *   - **Every value is now a PERCENTAGE, not a count.** The flow already emits
 *     `percentage` beside `count` per category (`dataverse/types.ts`'s `CategoryCount`),
 *     so this is a change of which field is read, never a derivation here — the same
 *     rule `domain/landing.ts`'s `SeriesRow.percentage` states: "as the response
 *     computed it. Never derived here from count/population." Three questions with
 *     three different populations cannot be compared on a count axis at all, which is
 *     what makes the percentage the correct measure for THIS pivot specifically.
 *   - **A category is a SERIES now, so it needs a colour, and the six responses are an
 *     ORDINAL scale rather than six identities.** See `AGREEMENT_SCALE_RAMP` below.
 */
import { AGREEMENT_RESPONSE_LABELS, WELLBEING_QUESTION_HEADINGS, optionLabel } from "../dataverse/schema";
import type { WellbeingLastYear } from "../dataverse/types";

/**
 * The Recharts row key each response category's percentage sits under.
 *
 * A synthesised `"response1".."response6"` rather than the raw option-set integer,
 * because a Recharts `dataKey` is a property-path string and a bare numeric key would
 * be read as an ARRAY INDEX on the row object. Prefixed and centralised here so the
 * builder and the chart cannot drift apart on the spelling.
 */
export function wellbeingResponseKey(value: number): string {
  return `response${String(value)}`;
}

/**
 * One wellbeing QUESTION, with each response category's percentage under its own key —
 * Recharts' "long-format pivoted to wide" shape, one row per question and one property
 * per series. The transpose of Revision 3's row, for the reason this file's header gives.
 */
export interface WellbeingComparisonRow {
  /** The response's own column name (`WellbeingQuestion.column`) — the row's identity. */
  column: string;
  /** `WELLBEING_QUESTION_HEADINGS[column]`, or the raw column name on drift. */
  label: string;
  [responseKey: string]: string | number | null;
}

/** One series of the comparison chart — a response category's key and its label. */
export interface WellbeingSeriesDefinition {
  /** `wellbeingResponseKey(value)` — the property each row's percentage sits under. */
  key: string;
  /** `AGREEMENT_RESPONSE_LABELS`' own wording for this category, via `optionLabel`. */
  heading: string;
  /** The option-set integer, kept so the chart can colour by POSITION on the scale. */
  value: number;
}

export interface WellbeingComparisonData {
  rows: WellbeingComparisonRow[];
  series: WellbeingSeriesDefinition[];
}

/**
 * Pivots FR-062's "last year" wellbeing questions into one Recharts-ready dataset:
 * **one row per question, one series per `AGREEMENT_RESPONSE_LABELS` category.**
 *
 * `null`/no questions in, `null` out — the same absence rule every other
 * round-statistics figure follows (TAD §3.3 point 3): a chart with no data behind it
 * renders nothing, not an empty frame.
 *
 * The SERIES list is `AGREEMENT_RESPONSE_LABELS`'s own six values, in that map's order,
 * regardless of which categories any one question's response happened to carry — so
 * every question is broken down on the SAME six-way scale, in the same order, and the
 * three groups are read against each other bar-position by bar-position. That is the
 * same alignment guarantee Revision 3's category axis gave, expressed on the other axis.
 *
 * **A category a question did not report reads as `null`, not as `0`.** This is the one
 * behaviour that changes meaning-wise in the transpose, and it changes toward the rule
 * the rest of this screen already follows (TAD §3.3 point 3, "a zero is a finding; a
 * null is an absence"). Recharts draws no bar for a null, which is the honest rendering:
 * a 0%-height bar and a not-reported category are the same picture, and only one of them
 * is a finding. Revision 3 wrote `0` because a MISSING PROPERTY on a wide-format row
 * would have silently misaligned the other questions' bars against the axis; a `null`
 * property is present, aligns identically, and does not assert a measurement.
 */
export function buildWellbeingComparisonData(
  wellbeing: WellbeingLastYear | null,
): WellbeingComparisonData | null {
  if (wellbeing === null || wellbeing.questions.length === 0) return null;

  const categoryValues = Object.keys(AGREEMENT_RESPONSE_LABELS)
    .map(Number)
    .sort((a, b) => a - b);

  const series: WellbeingSeriesDefinition[] = categoryValues.map((value) => ({
    key: wellbeingResponseKey(value),
    heading: optionLabel(AGREEMENT_RESPONSE_LABELS, value),
    value,
  }));

  const rows: WellbeingComparisonRow[] = wellbeing.questions.map((question) => {
    const row: WellbeingComparisonRow = {
      column: question.column,
      label: WELLBEING_QUESTION_HEADINGS[question.column] ?? question.column,
    };
    for (const value of categoryValues) {
      const match = question.categories.find((category) => category.value === value);
      row[wellbeingResponseKey(value)] = match?.percentage ?? null;
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

/**
 * The five-step ORDINAL ramp for the agreement scale — Revision 8, and it is a
 * different KIND of palette from `CHART_PALETTE` above, not more slots of it.
 *
 * `skills/dataviz`'s `references/color-formula.md` splits these explicitly: "if swapping
 * the category order would change the meaning... it is **ordinal** and takes a one-hue
 * ramp so the reader sees the order in the color." Strongly Disagree -> Disagree ->
 * Neutral -> Agree -> Strongly Agree is exactly that — reordering it destroys the
 * meaning — so colouring it with five CATEGORICAL hues would spend the identity channel
 * on a scale that already has an order, and `CHART_PALETTE` only has three validated
 * slots anyway: wrapping it would have painted "Strongly Disagree" and "Agree" the same
 * magenta, which is the one thing a Likert chart must never do.
 *
 * Every step is a shade this app already ships — `theme.ts`'s `brandRamp` at 100, 80,
 * 60, 50 and 30 — so no new colour VALUE enters the app (TAD §8.2's rule for this
 * screen), and lightness carries the position: light = disagreement, dark = agreement.
 *
 * Verified command, the ordinal checkset rather than the categorical six:
 * `node <dataviz-skill-base>/scripts/validate_palette.js
 * "#ff66ab,#ed008c,#ac0064,#8c0050,#51002c" --ordinal --mode light --surface "#ffffff"`
 * — reports `ALL CHECKS PASS` (lightness monotone; every adjacent dL >= 0.06; light end
 * #ff66ab at 2.71:1 against the white page surface, clearing the 2.0:1 ordinal floor;
 * single hue, spread 0 degrees). Re-run that command before changing any of these five.
 *
 * Light mode only, stated rather than implied: `theme.ts` builds `createLightTheme` and
 * nothing else, so this app has no dark surface to validate a second set of steps
 * against. That is the app's scope, not an omission from the check.
 */
export const AGREEMENT_SCALE_RAMP = ["#ff66ab", "#ed008c", "#ac0064", "#8c0050", "#51002c"] as const;

/**
 * "Not sure" — `AGREEMENT_RESPONSE_LABELS`' sixth option — is NOT a step on the scale
 * above, and is deliberately not coloured as one.
 *
 * It is a non-answer sitting beside a five-point ordinal scale, the same role a
 * diverging palette's neutral midpoint plays: giving it a sixth magenta step would put
 * it past "Strongly Agree" in the reader's eye and assert an opinion nobody expressed.
 * `--ink-400` #8a8a8a is the design system's own neutral, measures 3.45:1 against the
 * white page surface — clearing WCAG 1.4.11's 3:1 UI-graphic floor — and is the value
 * ADR-037 correction 2 bars from carrying TEXT, which this never does: it fills a bar
 * whose identity is carried by the legend's own words beside it.
 */
export const AGREEMENT_OFFSCALE_COLOR = "#8a8a8a";

/**
 * The fill for one agreement-response category, by its option-set value.
 *
 * Values 1-5 index the ordinal ramp in scale order; anything else — the "Not sure"
 * sixth option, and any category this build has never declared — takes the off-scale
 * neutral. That fallback is the colour counterpart of `optionLabel`'s `Unknown (n)`:
 * option-set drift shows up as a grey bar under a visibly odd legend entry rather than
 * being silently painted as a point on a scale it is not on.
 */
export function agreementResponseColor(value: number): string {
  return AGREEMENT_SCALE_RAMP[value - 1] ?? AGREEMENT_OFFSCALE_COLOR;
}
