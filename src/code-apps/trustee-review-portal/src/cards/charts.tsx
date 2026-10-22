/**
 * The round overview's chart shapes — card app only (TAD trustee-portal-design-2 §13.2,
 * WI-0086..WI-0088). Design: `RoundOverview.jsx` `Columns` (lines 119-138), `GroupedColumns`
 * (140-160) and `Donut` (162-184), recreated as HTML and CSS exactly as the kit draws them
 * (the kit's own comments name Recharts as the production analogue; the HTML form is what the
 * design renders, so it is what is matched).
 *
 * All three are `aria-hidden` decorations beside a table that stays the accessible content
 * (ADR-029, parent Revision 9): `DistributionChart` renders the table and its "Show the data
 * table" toggle unchanged. Figures come from the same series the table renders — share-only
 * where the first app is share-only (parent Revision 8) — and colours from the kit's own five-step
 * palette (`cards/palette.ts`), with only the two marks TAD §8.3 rejects substituted. Widths and heights are the only inline styles,
 * each computed at runtime from the data.
 */
import { useState } from "react";
import type { WellbeingComparisonData } from "../domain/charts";
import { markColor } from "./palette";
import type { Series } from "../domain/landing";
import { formatCount, formatPercentage } from "../domain/format";
import styles from "../styles/cards.module.css";

/** Each row's plotted value: its share when the response carried one, else its count. */
function plotted(row: { count: number; percentage: number | null }): number {
  return row.percentage ?? row.count;
}

/**
 * Vertical columns with rounded tops, quarter-height gridlines, a 1.5px baseline and a hover
 * tooltip "label · share" with the other columns dimmed to .55 (`Columns`). `height` is the
 * kit's own: 180px for age range, 200px for life satisfaction.
 */
export function ColumnChart({ series, colorIndex = 0, height = 180 }: { series: Series; colorIndex?: number; height?: number }) {
  const [hover, setHover] = useState<number | null>(null);
  const max = Math.max(1, ...series.rows.map(plotted));
  const color = markColor(colorIndex);
  return (
    <div className={styles.columns} aria-hidden="true" data-print="chart">
      <div className={styles.columnsPlot} data-chart-series="true" style={{ height: `${String(height)}px`, backgroundSize: `100% ${String(height / 4)}px` }}>
        {series.rows.map((row, index) => {
          const value = plotted(row);
          return (
            <div
              key={row.value}
              className={styles.column}
              onMouseEnter={() => {
                setHover(index);
              }}
              onMouseLeave={() => {
                setHover(null);
              }}
            >
              {hover === index ? (
                <span className={styles.columnTip} style={{ bottom: `calc(${String((value / max) * 100)}% + 8px)` }}>
                  {row.label} · {row.percentage === null ? formatCount(row.count) : formatPercentage(row.percentage)}
                </span>
              ) : null}
              <div
                className={styles.columnBar}
                data-chart-mark="true"
                data-dimmed={hover !== null && hover !== index ? "true" : undefined}
                data-empty={value === 0 ? "true" : undefined}
                style={{ height: `${String((value / max) * 100)}%`, backgroundColor: color }}
              />
            </div>
          );
        })}
      </div>
      <div className={styles.columnLabels}>
        {series.rows.map((row) => (
          <span key={row.value} className={styles.columnLabel}>
            {row.label}
          </span>
        ))}
      </div>
    </div>
  );
}

/**
 * Grouped columns, one colour per wellbeing question, and a legend of pills (`GroupedColumns`).
 * Series names are `domain/charts.ts`'s own (WI-0013), never the kit's "Question 8/9/10".
 */
export function GroupedColumnChart({ data, height = 200 }: { data: WellbeingComparisonData; height?: number }) {
  const values = data.rows.flatMap((row) => data.series.map((series) => row[series.key]));
  const max = Math.max(1, ...values.map((value) => (typeof value === "number" ? value : 0)));
  return (
    <div className={styles.grouped} aria-hidden="true" data-print="chart">
      <div className={styles.groupedPlot} style={{ height: `${String(height)}px`, backgroundSize: `100% ${String(height / 4)}px` }}>
        {data.rows.map((row) => (
          <div key={row.value} className={styles.groupedCategory}>
            {data.series.map((series, index) => {
              const value = row[series.key];
              const number = typeof value === "number" ? value : 0;
              return (
                <div
                  key={series.key}
                  className={styles.groupedBar}
                  data-chart-mark="true"
                  data-empty={number === 0 ? "true" : undefined}
                  title={`${series.heading}: ${typeof value === "number" ? formatPercentage(value) : "Not recorded"}`}
                  style={{ height: `${String((number / max) * 100)}%`, backgroundColor: markColor(index) }}
                />
              );
            })}
          </div>
        ))}
      </div>
      <div className={styles.groupedLabels}>
        {data.rows.map((row) => (
          <span key={row.value} className={styles.columnLabel}>
            {row.label}
          </span>
        ))}
      </div>
      <ul className={styles.groupedLegend}>
        {data.series.map((series, index) => (
          <li key={series.key} className={styles.legendPill} data-chart-series="true">
            <span className={styles.legendSwatch} style={{ backgroundColor: markColor(index) }} />
            {series.heading}
          </li>
        ))}
      </ul>
    </div>
  );
}

/**
 * The applicant-type donut (`Donut`): a 160px conic-gradient ring with a 100px white centre
 * carrying the population and "applications", and a legend of share and label. Share-only, as
 * the first app's pie is (parent Revision 8): the legend shows percentages, not counts; the
 * centre shows the denominator the "Counted over" line already states.
 */
export function DonutChart({ series }: { series: Series }) {
  const total = series.rows.reduce((sum, row) => sum + plotted(row), 0);
  let start = 0;
  const stops = series.rows
    .map((row, index) => {
      const size = total === 0 ? 0 : (plotted(row) / total) * 100;
      const stop = `${markColor(index)} ${String(start)}% ${String(start + size)}%`;
      start += size;
      return stop;
    })
    .join(", ");
  return (
    <div className={styles.donut} aria-hidden="true" data-print="chart">
      <div className={styles.donutRing} data-chart-mark="true" style={{ background: total === 0 ? undefined : `conic-gradient(${stops})` }}>
        <div className={styles.donutCentre}>
          <div>
            <div className={styles.donutCount}>{formatCount(series.population)}</div>
            <div className={styles.donutCaption}>applications</div>
          </div>
        </div>
      </div>
      <ul className={styles.donutLegend}>
        {series.rows.map((row, index) => (
          <li key={row.value} className={styles.donutLegendRow}>
            <span className={styles.donutSwatch} style={{ backgroundColor: markColor(index) }} />
            <span className={styles.donutShare}>{row.percentage === null ? "—" : formatPercentage(row.percentage)}</span>
            <span className={styles.donutLabel}>{row.label}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
