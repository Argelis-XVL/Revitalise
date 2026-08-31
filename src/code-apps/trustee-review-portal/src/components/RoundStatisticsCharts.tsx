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
 * assigned in the same fixed order every time — never picked per chart. The one
 * exception is `WellbeingComparisonChart`, which paints an ORDINAL scale and takes
 * `AGREEMENT_SCALE_RAMP` instead — see that file for why a Likert scale is not six
 * identities.
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
 */
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, Tooltip, XAxis, YAxis } from "recharts";
import { agreementResponseColor, categoricalColor } from "../domain/charts";
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

/** How many `<tspan>` lines a category label may occupy before it is ellipsised. */
const TICK_MAX_LINES = 3;
/** Line box for a 12px tick label, in SVG user units. */
const TICK_LINE_HEIGHT = 12;
/**
 * The greedy wrap budget, in characters.
 *
 * A character budget rather than a measured one BY NECESSITY: `getComputedTextLength` is the
 * only exact answer and jsdom implements none of the SVG text-measurement API, so a measured
 * tick would be untestable — the same `IMP-0111` trap this file's header names for
 * Recharts' own `<Legend>`. 18 characters is ~110px at this file's 12px tick size, which is
 * inside the ~120px column a 6-category chart gives each label at `BAR_CHART_MIN_WIDTH`.
 */
const TICK_CHARS_PER_LINE = 18;

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
}

/** A category-axis tick that wraps rather than rotating or truncating. */
export function WrappedCategoryTick({ x = 0, y = 0, payload }: CategoryTickProps) {
  const lines = wrapTickLabel(String(payload?.value ?? ""));
  return (
    <g transform={`translate(${String(x)},${String(y)})`}>
      <text textAnchor="middle" fontSize={12} fill="#4a4a4a" dy={TICK_LINE_HEIGHT}>
        {lines.map((line, index) => (
          <tspan key={`${String(index)}-${line}`} x={0} dy={index === 0 ? 0 : TICK_LINE_HEIGHT}>
            {line}
          </tspan>
        ))}
      </text>
    </g>
  );
}

/** Axis height for `TICK_MAX_LINES` wrapped lines plus the tick's own offset. */
const CATEGORY_AXIS_HEIGHT = TICK_MAX_LINES * TICK_LINE_HEIGHT + 20;

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

const BAR_CHART_MIN_WIDTH = 440;
/** Per-category column width, so an 11-score axis scrolls instead of crushing its ticks. */
const BAR_COLUMN_WIDTH = 68;
const BAR_CHART_HEIGHT = 300;
const BAR_CHART_MARGIN = { top: 8, right: 16, bottom: 8, left: 8 };

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
  const width = Math.max(BAR_CHART_MIN_WIDTH, series.rows.length * BAR_COLUMN_WIDTH);
  return (
    <div className={styles.tableScroll} aria-hidden="true" data-print="chart">
      <BarChart
        width={width}
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
          tick={<WrappedCategoryTick />}
        />
        <YAxis domain={PERCENT_DOMAIN} tickFormatter={percentTick} tick={{ fontSize: 12 }} />
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

const PIE_SIZE = 280;
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
    <div aria-hidden="true" data-print="chart">
      <PieChart width={PIE_SIZE} height={PIE_SIZE} accessibilityLayer={false}>
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

const COMPARISON_CHART_MIN_WIDTH = 560;
/** Width per QUESTION group — six bars plus the group's own gutter. */
const COMPARISON_GROUP_WIDTH = 190;
const COMPARISON_CHART_HEIGHT = 340;
const COMPARISON_CHART_MARGIN = { top: 8, right: 16, bottom: 8, left: 8 };

/**
 * FR-062's genuinely multi-series chart, transposed in Revision 8: **one vertical bar
 * GROUP per "last year" wellbeing question, one bar per agreement-response category**, so a
 * trustee reads each question's whole answer shape in one group and compares the three
 * groups against each other bar-position by bar-position.
 *
 * See `domain/charts.ts`'s header for why this is NOT the withdrawn FR-061 benchmark shape:
 * the transpose redistributes the SAME `wellbeingLastYear.questions` array across a
 * different pair of axes and adds no series the response did not already carry.
 *
 * Two things this chart does that no other chart in this file does:
 *
 *   - **It colours by POSITION ON A SCALE, not by identity.** `agreementResponseColor` maps
 *     the option-set value to `AGREEMENT_SCALE_RAMP`'s five ordinal steps, with the "Not
 *     sure" sixth option off-scale in the design system's neutral grey. `categoricalColor`
 *     is deliberately not used here — see this file's header, Revision 8 point 4.
 *   - **Its values are percentages, so three questions with three different populations are
 *     comparable at all.** A count axis could not compare them; that is what makes the
 *     percentage the correct measure for THIS pivot specifically.
 */
export function WellbeingComparisonChart({ data }: { data: WellbeingComparisonData }) {
  const legendItems = data.series.map((series) => ({
    label: series.heading,
    color: agreementResponseColor(series.value),
  }));
  const width = Math.max(COMPARISON_CHART_MIN_WIDTH, data.rows.length * COMPARISON_GROUP_WIDTH);
  return (
    <div className={styles.tableScroll} aria-hidden="true" data-print="chart">
      <BarChart
        width={width}
        height={COMPARISON_CHART_HEIGHT}
        data={data.rows}
        margin={COMPARISON_CHART_MARGIN}
        accessibilityLayer={false}
      >
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        {/* The category axis is now the QUESTIONS, whose headings are the longest labels
            anywhere in this file — the wrapped tick is what makes that legible. */}
        <XAxis
          dataKey="label"
          interval={0}
          height={CATEGORY_AXIS_HEIGHT}
          tick={<WrappedCategoryTick />}
        />
        <YAxis domain={PERCENT_DOMAIN} tickFormatter={percentTick} tick={{ fontSize: 12 }} />
        <Tooltip formatter={percentTooltip} />
        {data.series.map((series) => (
          <Bar
            key={series.key}
            dataKey={series.key}
            name={series.heading}
            fill={agreementResponseColor(series.value)}
            isAnimationActive={false}
            radius={[4, 4, 0, 0]}
          />
        ))}
      </BarChart>
      <ChartLegend items={legendItems} />
    </div>
  );
}
