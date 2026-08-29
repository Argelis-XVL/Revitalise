/**
 * One distribution: a real data table, and a bar chart drawn from the same array.
 *
 * ADR-029 / TAD §8.1, and the ordering in that heading is the decision, not a preference:
 *
 *   - **The table is the content.** It satisfies WCAG 1.1.1 (text alternative) and 1.3.1
 *     (info and relationships) properly, with real `<th scope>` cells — not with an `alt`
 *     string that paraphrases a picture.
 *   - **The chart is drawn from the SAME array the table renders.** One `Series`, two
 *     renderings, so they are structurally incapable of disagreeing. A chart and a table
 *     showing different numbers is a defect class this component cannot exhibit.
 *   - **No charting library.** A single-series bar chart of at most thirteen categories is
 *     one `<rect>` per row, and adding a dependency would walk into the unaudited
 *     licence/provenance gap `C-TECH-074`'s advisory half does not cover (TAD §8.1).
 *   - **One series.** FR-061's benchmark comparison is withdrawn (TAD §0.1 item 4, ADR-029
 *     as amended), so there is no second bar, no second column and no comparison anywhere
 *     in this file — and one fewer contrast pair to verify (§8.2).
 *   - **Every value is present as text.** Colour is never the only carrier (1.4.1): the
 *     count and the percentage are in the table cells, so a colour-blind trustee and one
 *     reading a monochrome print-out lose nothing at all.
 *
 * The denominator is on the page beside the percentages, always (TAD §3.3 point 1): "a
 * percentage whose denominator is not on the page is not auditable."
 *
 * ## `visual` — Fix 3 (2026-08-27), one optional additive slot
 *
 * A caller may pass a `visual` node, rendered ABOVE the table-and-bar layout below,
 * inside this SAME `<section>` and under this SAME heading. It exists so
 * `components/RoundStatisticsCharts.tsx`'s Recharts figures (a grouped bar, a pie) can
 * sit alongside this component's guaranteed-accessible content without inventing a
 * second heading for the same data — see that file's own header for why a second
 * `role="img"` for one dataset would be a duplicate announcement, not new information.
 * This component still uses no charting library itself, and still renders every value
 * as real text; `visual` is a slot for something else's picture, not a new one of its
 * own. No test in this file passes it, so every assertion made against the shape below
 * is exactly as true as it was before this slot existed.
 *
 * ## Revision 4 (2026-08-27) — RESTYLED IN PLACE, AND NOT ONE LINE BELOW THIS COMMENT MOVED
 *
 * TAD §8.5 point 4 is explicit that this component is restyled and **not** replaced, and the
 * restyle turned out to need no code at all: every visual rule this file uses is a class in
 * `styles/app.module.css`, so the section chrome — heading type, spacing, the rule around the
 * block — changed there and the markup, the ARIA and the geometry are byte-identical.
 *
 * Three things a reviewer should be able to confirm by diffing this file and finding nothing:
 *
 *   - `role="img"` + `aria-label={chartSummary(…)}` + `focusable="false"` on the SVG, and the
 *     real `<table>` with its `<caption>`, three `<th scope="col">` and a `<th scope="row">`
 *     per row, are all unchanged — so is the "one array, two renderings" property that makes
 *     the table and the chart structurally incapable of disagreeing, which
 *     `DistributionChart.test.tsx:69-81` asserts as arithmetic rather than as intent.
 *   - **A null percentage still renders as the words `"Not recorded"`, never `0%`** — a 0%
 *     here would be a fabricated figure.
 *   - **`.chartBar`'s fill is unchanged**, still `var(--colorCompoundBrandBackground)`
 *     (brand[80] `#ed008c`, 4.22:1 against white, clearing WCAG 1.4.11's 3:1 UI-graphic
 *     floor). §8.5 point 4 both lists the fill among the things that change and then states
 *     that it stays; the explicit sentence governs, and `app.module.css`'s `.chartBar`
 *     comment carries the arithmetic. `print.css:169-171` still forces it black on paper.
 *
 * NO CHARTING LIBRARY WAS ADDED. The design system ships no chart component of any kind and
 * the supplied `RoundOverview.jsx` mockup contains no chart at all, so there was nothing here
 * to adopt — and inventing one would have walked into the unaudited licence/provenance gap
 * TAD §8.1 exists to avoid. Net dependency change for this whole pass is zero.
 */
import { useId } from "react";
import type { ReactNode } from "react";
import { formatCount, formatPercentage, NOT_RECORDED } from "../domain/format";
import { chartSummary } from "../domain/landing";
import type { Series } from "../domain/landing";
import styles from "../styles/app.module.css";

/** Bar geometry, in the SVG's own user units. The CSS scales the whole thing. */
const BAR_HEIGHT = 8;
const BAR_GAP = 4;
const TRACK_WIDTH = 100;

export function DistributionChart({
  title,
  series,
  countHeading = "Applications",
  visual,
}: {
  title: string;
  series: Series;
  /** What the count column counts. Overridden where the unit is not an application. */
  countHeading?: string;
  /** An additional, purely decorative visual for this same data — see this file's header. */
  visual?: ReactNode;
}) {
  const headingId = useId();
  const height = series.rows.length * (BAR_HEIGHT + BAR_GAP) - BAR_GAP;

  return (
    <section className={styles.chartBlock} aria-labelledby={headingId} data-print="block">
      <h3 id={headingId} className={styles.fieldHeading}>
        {title}
      </h3>

      {/* The denominator, as text, before the figures it divides. */}
      <p className={styles.hint}>
        {series.population === null
          ? "The number of applications these figures are counted over was not reported."
          : `Counted over ${formatCount(series.population)} applications in this round.`}
      </p>

      {visual}

      <div className={styles.chartLayout}>
        <div className={styles.tableScroll}>
          <table className={styles.table}>
            <caption className={styles.srOnly}>
              {title}. {countHeading} and share of the round, by category.
            </caption>
            <thead>
              <tr>
                <th scope="col" className={styles.plainHeaderCell}>
                  Category
                </th>
                <th scope="col" className={styles.plainHeaderCell}>
                  {countHeading}
                </th>
                <th scope="col" className={styles.plainHeaderCell}>
                  Share of round
                </th>
              </tr>
            </thead>
            <tbody>
              {series.rows.map((row) => (
                <tr key={row.value}>
                  {/* A row header, not a data cell: it is what identifies the row, so a
                      screen reader announces it with each figure (WCAG 1.3.1). */}
                  <th scope="row" className={styles.categoryCell}>
                    {row.label}
                  </th>
                  <td className={styles.numeric}>{formatCount(row.count)}</td>
                  <td className={styles.numeric}>
                    {row.percentage === null ? (
                      <span className={styles.notAvailable}>{NOT_RECORDED}</span>
                    ) : (
                      formatPercentage(row.percentage)
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/*
          `role="img"` with a summarising label, per ADR-029 — the picture is announced as
          a picture, and the label says where the numbers are rather than reciting them.
          `focusable="false"` because an SVG is a tab stop in some engines and a
          non-interactive graphic must not be one (WCAG 2.4.3).
        */}
        <svg
          className={styles.chart}
          viewBox={`0 0 ${String(TRACK_WIDTH)} ${String(height)}`}
          role="img"
          aria-label={chartSummary(title, series)}
          focusable="false"
          data-print="chart"
          preserveAspectRatio="xMinYMin meet"
        >
          {series.rows.map((row, index) => (
            <rect
              key={row.value}
              x={0}
              y={index * (BAR_HEIGHT + BAR_GAP)}
              width={Math.max(0, (row.count / series.maxCount) * TRACK_WIDTH)}
              height={BAR_HEIGHT}
              className={styles.chartBar}
            />
          ))}
        </svg>
      </div>
    </section>
  );
}
