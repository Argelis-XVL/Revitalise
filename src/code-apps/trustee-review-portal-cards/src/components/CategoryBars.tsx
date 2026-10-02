/**
 * Labelled horizontal category bars — ADR-063 of TAD trustee-portal-design-2 (reviewer R9: "The
 * designs bars are intentional. So use them. The bar from earlier today wasn't intentional, but an
 * unwanted artifact"). Card app only. Design: `RoundOverview.jsx` `Bars` (lines 65-83).
 *
 * WHAT MAKES THESE NOT THE WI-0053 ARTEFACT, property by property (ADR-063 table):
 *
 *   - they are a `visual` SUPPLIED to `DistributionChart`, never drawn by it, and they are HTML,
 *     not SVG — so `DistributionChart.test.tsx`'s and `LandingPage.test.tsx`'s WI-0053 cases
 *     (contract, unchanged) still pass: no `svg`, `rect` or `.chartBar` anywhere in the block;
 *   - every bar is LABELLED with its category and its figure as visible text;
 *   - exactly one bar per series category, in series order;
 *   - each fill is PROPORTIONAL: the category's count over the largest count, so the largest is
 *     full width and a zero is an empty track. `CategoryBars.test.tsx` holds these three.
 *
 * The list is `aria-hidden`: the table beneath it is the accessible content (ADR-029), and it is
 * always on screen for "Exceptional circumstance cited" (ADR-063 decision 2). Fill colours are the
 * kit's own five-step palette (`cards/palette.ts`), with only the two marks TAD §8.3 rejects
 * (teal, pink-300) substituted. A fill's
 * width is the one runtime-computed inline style here.
 */
import type { Series } from "../domain/landing";
import { markColor } from "../cards/palette";
import { formatCount, formatPercentage, NOT_RECORDED } from "../domain/format";
import styles from "../styles/cards.module.css";

export function CategoryBars({
  series,
  figures = "count-and-share",
}: {
  series: Series;
  /** `share-only` drops the count from the visible figure (parent Revision 8, TAD §13.2). */
  figures?: "count-and-share" | "share-only";
}) {
  const max = Math.max(1, ...series.rows.map((row) => row.count));
  return (
    <ul className={styles.categoryBars} aria-hidden="true" data-print="chart" data-chart-series="true">
      {series.rows.map((row, index) => {
        const share = row.percentage === null ? NOT_RECORDED : formatPercentage(row.percentage);
        const width = (row.count / max) * 100;
        return (
          <li key={row.value} className={styles.categoryBar} data-category={row.label}>
            <span className={styles.categoryBarLine}>
              <span className={styles.categoryBarLabel}>{row.label}</span>
              <span className={styles.categoryBarValue}>
                {figures === "count-and-share" ? (
                  <>
                    <strong>{formatCount(row.count)}</strong> · {share}
                  </>
                ) : (
                  <strong>{share}</strong>
                )}
              </span>
            </span>
            <span className={styles.categoryBarTrack}>
              <span
                className={styles.categoryBarFill}
                data-chart-mark="true"
                data-width={String(width)}
                style={{ width: `${String(width)}%`, backgroundColor: markColor(index) }}
              />
            </span>
          </li>
        );
      })}
    </ul>
  );
}
