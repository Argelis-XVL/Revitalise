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
 * assigned in the same fixed order every time — never picked per chart.
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

const BAR_ROW_HEIGHT = 32;
const BAR_CHART_WIDTH = 480;
const BAR_CHART_MIN_HEIGHT = 120;
const BAR_CHART_MARGIN = { top: 8, right: 28, bottom: 8, left: 8 };

/**
 * A single-series horizontal bar — one bar per row, longest label first no more than
 * any other order (the row order is `series.rows`' own, unchanged from the table
 * beside it). Horizontal, like `DistributionChart`'s own hand-rolled bars, so a long
 * option label (`APPLICANT_GENDER_LABELS`' "Describes themselves another way", for
 * one) never needs rotating or truncating.
 *
 * One series only — see this file's header and `domain/charts.ts`'s own header for
 * why gender, age range and life satisfaction stay single-series here.
 */
export function CategoryBarChart({ series }: { series: Series }) {
  const height = Math.max(BAR_CHART_MIN_HEIGHT, series.rows.length * BAR_ROW_HEIGHT + 24);
  return (
    <div className={styles.tableScroll} aria-hidden="true" data-print="chart">
      <BarChart
        width={BAR_CHART_WIDTH}
        height={height}
        data={series.rows}
        layout="vertical"
        margin={BAR_CHART_MARGIN}
        accessibilityLayer={false}
      >
        <CartesianGrid strokeDasharray="3 3" horizontal={false} />
        <XAxis type="number" allowDecimals={false} />
        <YAxis type="category" dataKey="label" width={190} tick={{ fontSize: 12 }} interval={0} />
        <Tooltip />
        <Bar
          dataKey="count"
          name="Applications"
          fill={categoricalColor(0)}
          isAnimationActive={false}
          radius={[0, 4, 4, 0]}
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
          dataKey="count"
          nameKey="label"
          cx="50%"
          cy="50%"
          outerRadius={PIE_OUTER_RADIUS}
          stroke="#fff"
          strokeWidth={2}
          isAnimationActive={false}
          rootTabIndex={-1}
          label={({ percent }) => (percent === undefined ? "" : `${(percent * 100).toFixed(1)}%`)}
        >
          {series.rows.map((row, index) => (
            <Cell key={row.value} fill={categoricalColor(index)} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
      <ChartLegend items={legendItems} />
    </div>
  );
}

const COMPARISON_CHART_WIDTH = 560;
const COMPARISON_CHART_HEIGHT = 320;
const COMPARISON_CHART_MARGIN = { top: 8, right: 16, bottom: 56, left: 8 };

/**
 * FR-062's genuinely multi-series chart: every "last year" wellbeing question the
 * flow returned, grouped by response category so a trustee can see the three
 * questions' shapes side by side. See `domain/charts.ts`'s header for why this is NOT
 * the withdrawn benchmark shape — every series here is a real, already-collected
 * distribution, not a synthetic comparator.
 */
export function WellbeingComparisonChart({ data }: { data: WellbeingComparisonData }) {
  const legendItems = data.series.map((series, index) => ({
    label: series.heading,
    color: categoricalColor(index),
  }));
  return (
    <div className={styles.tableScroll} aria-hidden="true" data-print="chart">
      <BarChart
        width={COMPARISON_CHART_WIDTH}
        height={COMPARISON_CHART_HEIGHT}
        data={data.rows}
        margin={COMPARISON_CHART_MARGIN}
        accessibilityLayer={false}
      >
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis
          dataKey="label"
          tick={{ fontSize: 12 }}
          angle={-20}
          textAnchor="end"
          interval={0}
          height={70}
        />
        <YAxis allowDecimals={false} />
        <Tooltip />
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
