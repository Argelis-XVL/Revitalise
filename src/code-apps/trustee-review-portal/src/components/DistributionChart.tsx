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
 * own.
 *
 * **Supplying it now WITHDRAWS this component's own inline SVG bars, in every `figures` mode**
 * — reviewer item 3, Revision 11 below. `visual` was purely additive until then, and that is
 * precisely what produced two pictures of one array under one heading.
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
 *
 * ## Revision 8 (2026-08-31, wbs:6.9) — `figures="share-only"`, for the FR-061 panel only
 *
 * The reviewer asked, against the live DEV portal, to "drop the raw-count tables under 'Who
 * applied in this round', keep the percentage figures". `figures` is that instruction, and
 * it is a MODE rather than a rewrite: `"count-and-share"` is the default and is what every
 * other call site on the screen still gets, byte-for-byte unchanged.
 *
 * In `"share-only"` two things are withdrawn, and it matters which two:
 *
 *   - **The count COLUMN.** The `<th scope="col">` and its cells. This is the reviewer's
 *     literal ask, and it is the only figure removed.
 *   - **This component's own hand-rolled SVG bars.** They are scaled from `count`
 *     (`row.count / series.maxCount`), so leaving them beside a table that no longer shows a
 *     count would be a picture of a quantity the reader can no longer check — the exact
 *     inverse of ADR-029's "every value it depicts is text in the table beside it". They are
 *     also the HORIZONTAL bars the reviewer separately asked to see as vertical; the
 *     `visual` slot's Recharts chart is the vertical, percentage-scaled replacement, and one
 *     dataset does not need three renderings.
 *
 * **THE NULL RULE AND THE ACCESSIBLE CONTRACT ARE BOTH UNTOUCHED, AND THAT IS THE POINT.**
 * This mode is not a weakening of "a zero is a finding; a null is an absence" (TAD §3.3
 * point 3): a null percentage still renders as the words "Not recorded" and never as `0%`,
 * in this mode exactly as in the other. And the table is STILL the accessible content — real
 * `<caption>`, real `<th scope="col">`, real `<th scope="row">` per category — so the
 * `aria-hidden` Recharts figure beside it is still decorative and still never the only
 * rendering of a value. What is removed is a redundant second picture and one column of
 * numbers, not a text alternative.
 *
 * **The denominator is if anything MORE load-bearing here**, so it is unconditional in both
 * modes: the `.hint` line above states the population these shares are counted over. TAD
 * §3.3 point 1 — "a percentage whose denominator is not on the page is not auditable" — is
 * the whole reason a share-only table is allowed to exist at all.
 *
 * ## Revision 9 (2026-09-01, wbs:6.9) — reviewer item 1: THE TABLE IS VISUALLY HIDDEN BY
 * DEFAULT AND IS NOT DELETED, AND THE DISTINCTION IS THE WHOLE ANSWER
 *
 * The reviewer's words, against the live DEV portal: *"in the 'figures of the round' section,
 * every chart currently renders a data table underneath it… only the chart itself should be
 * shown, not the underlying data in tabular form."*
 *
 * Taken literally that instruction deletes the accessible content this component was built
 * around. Everything in this file's header above is one argument — **the table IS the text
 * alternative** (WCAG 1.1.1) and **the structured relationship** (1.3.1) for a picture whose
 * own `aria-label` is deliberately a summary and not a recitation of the data. Deleting it
 * would leave a `role="img"` summary as the only rendering of every figure on the screen, and
 * would leave `figures="share-only"` (which has no `role="img"` at all) rendering a chart that
 * is `aria-hidden` beside nothing whatsoever. That is a WCAG 1.1.1 failure outright, not a
 * contrast miss, and it is not a trade this component may make on a styling instruction.
 *
 * **THE INTERPRETATION SHIPPED HERE, so it can be flagged rather than silently decided.** The
 * table is moved OFF SCREEN with this app's own `.srOnly` class — the same visually-hidden
 * pattern `App.tsx`'s live region and this file's own `<caption>` already use — and a
 * "Show the data table" disclosure brings it back for any trustee who wants the numbers.
 * The choice of `.srOnly` over a `<details>` element is the load-bearing half:
 *
 *   - A collapsed `<details>` is `display: none` for its content, which removes the table
 *     from the ACCESSIBILITY TREE as well as from the screen. A screen-reader user would
 *     then have to find and operate a disclosure before any figure existed at all.
 *   - `.srOnly` clips the table to a 1px box and removes NOTHING: it stays in the DOM, in
 *     the accessibility tree, in the reading order, and in the tab order's own sequence
 *     (a table holds no tab stops). **A screen-reader user's experience of this screen is
 *     byte-for-byte what it was before this revision**, which is what makes the change a
 *     purely visual one and this component's ADR-029 contract genuinely intact rather than
 *     re-argued.
 *
 * So: a sighted trustee sees the chart alone (the reviewer's literal ask), a screen-reader
 * user loses nothing at all (WCAG 1.1.1, 1.3.1), and anyone who wants the figures on screen
 * presses one button. The disclosure carries `aria-expanded` + `aria-controls`, so its state
 * is announced rather than inferred from the label alone (WCAG 4.1.2).
 *
 * **IT PRINTS REGARDLESS OF THE TOGGLE.** `print.css` un-hides `[data-print="datatable"]`
 * with `!important`, because the printed pack is the durable record of what a board saw (TAD
 * §6.4) and a board pack of pictures with no figures is not one. The toggle button itself is
 * `data-print="hide"`, like every other control.
 *
 * **APPLIED IN BOTH MODES, WHICH IS WIDER THAN THE DISPATCH'S LETTER AND MATCHES THE
 * REVIEWER'S.** The dispatch scoped this to the `figures="count-and-share"` call sites, on the
 * reading that the `share-only` panel was already dealt with in Revision 8. It was not:
 * Revision 8 dropped that mode's count COLUMN, and the table itself is still drawn under every
 * chart in "Who applied in this round". The reviewer said *every* chart, so hiding one set of
 * tables and leaving four visible would read as the item half-done. The mechanism is one flag
 * on this component and is therefore identical in both modes.
 *
 * ## Revision 10 (2026-09-02, wbs:6.8) — `alwaysShowTable`, one section's exception to the
 * default this Revision 9 section just established
 *
 * The reviewer's item 1 this round: one statistics section's table must always be on screen,
 * "regardless of whatever collapse/hide state governs the other statistics tables" — every
 * OTHER call site keeps Revision 9's default-hidden disclosure exactly as it is. `alwaysShowTable`
 * seeds `tableOnScreen` `true` and renders NO toggle at all, rather than a toggle a trustee could
 * use to hide it again: a control whose two states look and do the same thing is a WCAG 4.1.2
 * name/state mismatch, not a convenience. `components/RoundStatistics.tsx` is the only call site
 * that sets it, and its own comment names the one section it applies to and why.
 *
 * ## Revision 11 (2026-09-02, wbs:6.8) — reviewer item 3: the stray bar under "Life
 * satisfaction", and why the fix is one condition rather than one call site
 *
 * A magenta bar rendered under the "Show the data table" toggle beneath the Life Satisfaction
 * chart, attached to nothing. It was this component's OWN count-scaled `.chartBar` SVG, drawn
 * beside a table that Revision 9 clipped off screen, under a heading whose picture was already
 * the `visual` slot's Recharts column chart.
 *
 * `showOwnChart` (in the component below) is the fix and carries the full reasoning. The short
 * version: Revision 8 withdrew these bars for the `share-only` MODE, but the property that
 * justified withdrawing them — *"one dataset does not need three renderings"*, and the `visual`
 * is the picture whenever one is supplied — was never a property of that mode. Keyed on the
 * mode, it missed every `count-and-share` call site that also passes a `visual`. It is keyed on
 * the `visual` now, which is the thing it was always about.
 */
import { useId, useState } from "react";
import type { ReactNode } from "react";
import { formatCount, formatPercentage, NOT_RECORDED } from "../domain/format";
import { chartSummary } from "../domain/landing";
import type { Series } from "../domain/landing";
import { Button } from "./ds";
import { classNames } from "./ds/classNames";
import styles from "../styles/app.module.css";

/** Bar geometry, in the SVG's own user units. The CSS scales the whole thing. */
const BAR_HEIGHT = 8;
const BAR_GAP = 4;
const TRACK_WIDTH = 100;

/** Which figures the table carries — see this file's Revision 8 section. */
export type DistributionFigures = "count-and-share" | "share-only";

export function DistributionChart({
  title,
  series,
  countHeading = "Applications",
  figures = "count-and-share",
  visual,
  alwaysShowTable = false,
}: {
  title: string;
  series: Series;
  /** What the count column counts. Overridden where the unit is not an application. */
  countHeading?: string;
  /**
   * `"share-only"` drops the count column AND this component's own count-scaled SVG bars,
   * for the FR-061 "Who applied in this round" panel. Default is unchanged behaviour.
   */
  figures?: DistributionFigures;
  /** An additional, purely decorative visual for this same data — see this file's header. */
  visual?: ReactNode;
  /**
   * Revision 10 (2026-09-02, wbs:6.8), reviewer item 1: keeps this block's data table ON
   * SCREEN unconditionally, with no "Show the data table" toggle to hide it again — for the
   * "Exceptional circumstances" section specifically, so it always renders regardless of the
   * default-hidden disclosure state Revision 9 gave every OTHER statistics table on this
   * screen. Every other call site keeps that default, unchanged.
   */
  alwaysShowTable?: boolean;
}) {
  const headingId = useId();
  const tableId = useId();
  const showCounts = figures === "count-and-share";
  /**
   * REVIEWER ITEM 3 (Revision 11, 2026-09-02, wbs:6.8) — THIS COMPONENT DRAWS ITS OWN BARS
   * ONLY WHEN NOBODY ELSE IS DRAWING THIS DATA, IN EVERY MODE.
   *
   * The reported symptom: *"a stray pink bar renders under the 'Show the data table' link
   * beneath the Life Satisfaction chart."* Confirmed against the rendered output before it was
   * treated as certain, and the diagnosis holds — that block passes BOTH a `visual`
   * (`CategoryBarChart`) and the default `figures="count-and-share"`, so it drew a Recharts
   * column chart AND this component's own count-scaled horizontal `.chartBar` SVG of the same
   * eleven scores. With the table clipped to `.srOnly` since Revision 9, the second picture had
   * nothing beside it and read as a loose magenta bar under the toggle.
   *
   * **This is the reasoning Revision 8 already applied to `share-only`, applied where it
   * actually belongs.** That revision withdrew these bars for one MODE; the property that
   * justified it is not a property of the mode at all — it is that *"one dataset does not need
   * three renderings"* and the `visual` IS the picture whenever a caller supplies one. Keying
   * the withdrawal on the mode left every `count-and-share` call site that also passes a
   * `visual` drawing a duplicate, which is exactly one call site today and would have been the
   * next one added.
   *
   * **The accessible contract is untouched, and by the same argument as Revision 8's.** What is
   * removed is a redundant second picture, never a text alternative: the real `<table>` — its
   * `<caption>`, its `<th scope="col">`, its `<th scope="row">` per category — is still rendered,
   * still in the accessibility tree, and still carries every count and percentage as text
   * (ADR-029). The `role="img"` summary goes with the bars it summarised, exactly as it does in
   * `share-only`, where this component has had no `role="img"` at all since Revision 8.
   */
  const showOwnChart = showCounts && visual === undefined;
  // Revision 9, reviewer item 1 — VISUAL state only. The table is rendered either way; this
  // decides whether it is on screen or clipped to `.srOnly`'s 1px box. See this file's header.
  // `alwaysShowTable` seeds it `true` and there is no control to turn it back off (below).
  const [tableOnScreen, setTableOnScreen] = useState(alwaysShowTable);
  const tableVisible = alwaysShowTable || tableOnScreen;
  const height = series.rows.length * (BAR_HEIGHT + BAR_GAP) - BAR_GAP;
  // The two-column table-beside-chart grid only makes sense while the table occupies a
  // column. `.srOnly` takes it out of flow (`position: absolute`), so with the table hidden
  // the grid would otherwise reserve an empty first track and push the chart into the second.
  // ...and the same is true when this component draws no chart of its own because a `visual`
  // was supplied (reviewer item 3): a two-column grid would reserve a track for a picture that
  // is not there. Keyed on `showOwnChart`, not on `showCounts`, for that reason.
  const layoutClass =
    tableVisible && showOwnChart ? styles.chartLayout : styles.chartLayoutStacked;

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

      {/*
        Reviewer item 1's disclosure. `ghost` because it is a secondary affordance beside the
        figure, not an action the screen exists to offer; `sm` because it sits under every one
        of the screen's ten-odd chart blocks. `ds/Button` guarantees the 44px target at every
        size (WCAG 2.5.5), so "small" here is type and padding, never the hit area.
      */}
      {/* No toggle at all when `alwaysShowTable` — there is nothing to hide, and a control
          whose two states are identical would be a WCAG 4.1.2 name/state mismatch. */}
      {alwaysShowTable ? null : (
        <Button
          variant="ghost"
          size="sm"
          className={styles.dataTableToggle}
          aria-expanded={tableOnScreen}
          aria-controls={tableId}
          data-print="hide"
          onClick={() => {
            setTableOnScreen((shown) => !shown);
          }}
        >
          {tableOnScreen ? "Hide the data table" : "Show the data table"}
        </Button>
      )}

      <div className={layoutClass}>
        {/*
          `data-print="datatable"` — print.css un-hides this with `!important` whatever the
          toggle says, because the printed pack is the durable record of what a board saw
          (TAD §6.4). The id is the disclosure's `aria-controls` target.
        */}
        <div
          id={tableId}
          className={classNames(
            styles.tableScroll,
            tableVisible ? undefined : styles.srOnly,
          )}
          data-print="datatable"
        >
          <table className={styles.table}>
            <caption className={styles.srOnly}>
              {title}.{" "}
              {showCounts ? `${countHeading} and share of the round` : "Share of the round"}, by
              category.
            </caption>
            <thead>
              <tr>
                <th scope="col" className={styles.plainHeaderCell}>
                  Category
                </th>
                {showCounts ? (
                  <th scope="col" className={styles.plainHeaderCell}>
                    {countHeading}
                  </th>
                ) : null}
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
                  {showCounts ? (
                    <td className={styles.numeric}>{formatCount(row.count)}</td>
                  ) : null}
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

          Withdrawn entirely in `share-only`: these bars are scaled from `count`, which that
          mode's table no longer shows, so they would depict a quantity the reader cannot
          check. See this file's Revision 8 section.

          Withdrawn in EVERY mode when a `visual` is supplied (reviewer item 3, Revision 11):
          that node is already this data's picture, and two pictures of one array under one
          heading is what the reviewer saw as a stray bar. See `showOwnChart` above.
        */}
        {showOwnChart ? (
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
        ) : null}
      </div>
    </section>
  );
}
