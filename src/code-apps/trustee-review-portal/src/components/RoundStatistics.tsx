/**
 * FR-058 to FR-062 — every figure the statistics flow computed, and nothing else.
 *
 * This component is reached only when `status === "ok"` (TAD §3.3 point 4), so there is no
 * branch in here for a diagnostic state: by the time it renders, the decision that figures
 * are safe to show has already been made in `domain/landing.ts`.
 *
 * ## The rule every section in this file obeys
 *
 * **A `null` metric renders as nothing at all.** Not a zero, not an error, and not a
 * heading with an empty body — TAD §3.3 point 3: "a zero is a finding; a null is an
 * absence." So every section below is built as a list of the figures that actually arrived
 * and is skipped entirely when that list is empty.
 *
 * This is not a corner case being handled defensively. It is the state the screen is in
 * TODAY: the flow's first version emits `applicationsReceived` and `null` for every other
 * metric, so on the day this ships one section renders and the rest are absent. The whole
 * contract is built out anyway, so the day the flow's next version starts emitting them
 * the screen is already correct with no code change — which is the same reasoning ADR-027
 * used for the redacted care-support columns.
 *
 * One metric is still expected never to arrive, and is treated exactly like any other
 * absence rather than being special-cased into a visible apology:
 *
 *   - FR-062's three proportions — `null` until OQ-039 supplies three thresholds nobody
 *     has stated (TAD §5.2, A-R29). They are rendered by the same code as any other
 *     metric; nothing here sets a threshold or offers to.
 *
 * `ethnicGroupDistribution` used to be listed here as the second such metric, described as
 * permanently `null` with no column behind it. TAD §0.11 (Revision 8, 2026-08-31) records
 * that as false: the data is captured, and the reviewer risk-accepted showing it as a share
 * of the round on the same reasoning already accepted for gender, age range and applicant
 * type. It is now built exactly like those three, under "Who applied in this round", and it
 * needs no special case at all — where the flow does not send it, the null rule above
 * renders nothing, which is what every environment outside DEV still gets (TAD §0.11 point
 * 3 scopes this to DEV; TST/ACC/PRD stay gated on OQ-030's DPIA sign-off, `EX-005`).
 *
 * And one thing that is deliberately absent everywhere: **no suppression or grouping of a
 * low-count category.** NFR-027 was withdrawn by the reviewer twice, and TAD §6.3's final
 * paragraph records that the acceptance covers this aggregate path with no control. Every
 * row carries its denominator so a reader can see what a small number is small against;
 * that is the whole of it.
 *
 * ## Fix 3 (2026-08-27) — charts and KPI tiles alongside the tables above
 *
 * The reviewer compared this screen against `Round 3 Stats.pptx` / `Round 4.pptx` and
 * found it "feels like v0.1, not v0.9": real bar/pie charts and a KPI dashboard, where
 * this screen showed plain tables. Every `DistributionChart` below now also gets a
 * `visual` — a bar chart for gender/age range/life satisfaction/each wellbeing question,
 * a pie for applicant type (`components/RoundStatisticsCharts.tsx`) — and "Round progress"
 * renders as `StatTileRow`'s KPI tiles instead of a `Definitions` list. Every one of
 * those tables, headings and figures is UNCHANGED beneath its new picture: nothing here
 * is the only place a number lives, per that file's own header.
 *
 * The deck also shows gender and age range as TWO-series grouped bars (this round vs. a
 * prior one) and an ethnic-group chart. The grouped second series is still not built: it is
 * FR-061's benchmark comparison, withdrawn by the reviewer's own decision
 * (`domain/landing.ts`'s `Distribution` doc, ADR-029 as amended, and
 * `LandingPage.test.tsx`'s own "renders no benchmark, second series or comparison column"
 * assertion) — there is no "prior round" figure in this response to draw a second bar from,
 * and reinstating that withdrawn scope is a commercial/architecture decision, not a
 * chart-polish one. `domain/charts.ts`'s header carries the same explanation.
 *
 * **The ethnic-group chart IS built, as of TAD §0.11 (Revision 8, 2026-08-31)** — the one
 * half of this paragraph Revision 8 turns over. It is a single-series share-of-round bar
 * chart beside the other three, not a second series on any of them, so the withdrawn
 * benchmark stays withdrawn either way.
 *
 * ## Revision 4 (2026-08-27) — the null rule is untouched, and that is the point
 *
 * TAD §8.5 point 3. Not a line of this file changed in the visual refresh: `present()` at
 * the top of the component is still the only gate on whether a figure appears, so a `null`
 * metric still renders **as nothing at all** — not a zero, not an error, and not a heading
 * with an empty body. `StatTileRow` beneath "Round progress" is now drawn by `ds/StatTile`
 * rather than by hand, which changes the tile's surface and type and nothing else: the same
 * `<dt>`/`<dd>` pairs, in the same `<dl>`, with the same `formatCount`/`formatRate` text.
 *
 * The `absent` state `ds/StatTile` gained is unreachable from this file BY CONSTRUCTION, and
 * deliberately so: `present()` has already removed every null before a tile is built, so no
 * absence word can reach a tile here. It is reachable only from `RoundFinancePanel`, which
 * is the panel that renders a row with no figure in it on purpose — the two opposite null
 * behaviours TAD §8.5 point 3 asks to be preserved, still opposite.
 */
import { useId, useState } from "react";
import type { ReactNode } from "react";
import {
  formatCount,
  formatMoneyMeasureAmount,
  formatMoneyMeasurePercentage,
  formatPercentage,
  formatRate,
  NOT_RECORDED,
} from "../domain/format";
import { buildSeries } from "../domain/landing";
import type { Series } from "../domain/landing";
import { buildWellbeingComparisonData } from "../domain/charts";
import type { WellbeingComparisonData } from "../domain/charts";
import {
  APPLICANT_GENDER_LABELS,
  AGE_RANGE_LABELS,
  APPLICANT_TYPE_LABELS,
  BREAK_TYPE_LABELS,
  CIRCUMSTANCE_SCORE_BAND_LABELS,
  ETHNIC_GROUP_LABELS,
  EXCEPTIONAL_CIRCUMSTANCE_LABELS,
  LIFE_SATISFACTION_LABELS,
  optionLabel,
} from "../dataverse/schema";
import type {
  BreakTypeProfile,
  ProportionMetric,
  RoundStatisticsResponse,
} from "../dataverse/types";
import { Button } from "./ds";
import { classNames } from "./ds/classNames";
import { Definitions, Panel, ProgressTiles } from "./Panel";
import { DistributionChart } from "./DistributionChart";
import { CategoryBars } from "./CategoryBars";
import { ColumnChart, DonutChart, GroupedColumnChart } from "../cards/charts";
import {
  LEVEL_OF_NEED_SENTENCE,
  WHO_APPLIED_SENTENCE,
  exceptionalSentence,
  roundProgressSentence,
} from "../cards/sentences";
import { computedOnStamp } from "../cards/stamp";
import styles from "../styles/app.module.css";

interface Item {
  label: string;
  value: string;
}

/** Keeps a definition row out of the list when its metric did not arrive. */
function present(label: string, value: string | null): Item[] {
  return value === null ? [] : [{ label, value }];
}

/**
 * The break-type table's caption — the one place a reader meets a blank money cell for the
 * first time, so the explanation that it is a deliberate withholding (not an error, not a
 * zero) belongs here rather than in a tooltip (ADR-039, TAD §6.3.5).
 *
 * Threshold-agnostic BY DESIGN: `k` (`RoundStatisticsMoneyMeasureMinimumPopulation`) lives in
 * `rev_setting`, is read only by the flow, and never travels in the response document — so
 * this screen has no number to name and must not guess or hardcode one.
 */
function breakTypeCaption(population: number | null): string {
  const lead =
    population === null
      ? "Applications, average cost and average grant requested, by type of break."
      : `Applications, average cost and average grant requested, by type of break, ` +
        `over ${formatCount(population)} applications in this round.`;
  return (
    lead +
    " Average cost, average grant requested and grant share are shown only where enough " +
    "applications in that row carry a figure; where they are not shown, the number of " +
    "applications still is."
  );
}

/** FR-060 — the break-type breakdown. A table, not a chart: §8.1 scopes charting to FR-061/062. */
function BreakTypeTable({ profile }: { profile: BreakTypeProfile }) {
  return (
    <div className={styles.tableScroll}>
      <table className={`${styles.table} ${styles.statTable}`}>
        <caption className={styles.tableCaption}>{breakTypeCaption(profile.population)}</caption>
        <thead>
          <tr>
            <th scope="col" className={styles.plainHeaderCell}>
              Type of break
            </th>
            <th scope="col" className={`${styles.plainHeaderCell} ${styles.numeric}`}>
              Applications
            </th>
            <th scope="col" className={`${styles.plainHeaderCell} ${styles.numeric}`}>
              Average total cost
            </th>
            <th scope="col" className={`${styles.plainHeaderCell} ${styles.numeric}`}>
              Average grant requested
            </th>
            <th scope="col" className={`${styles.plainHeaderCell} ${styles.numeric}`}>
              Grant as share of cost
            </th>
          </tr>
        </thead>
        <tbody>
          {profile.rows.map((row) => (
            <tr key={row.value}>
              <th scope="row" className={styles.categoryCell}>
                {optionLabel(BREAK_TYPE_LABELS, row.value)}
              </th>
              <td className={styles.numeric}>{formatCount(row.count)}</td>
              <td className={styles.numeric}>{formatMoneyMeasureAmount(row.averageCost)}</td>
              <td className={styles.numeric}>
                {formatMoneyMeasureAmount(row.averageAmountRequested)}
              </td>
              <td className={styles.numeric}>
                {formatMoneyMeasurePercentage(row.percentageOfCost)}
              </td>
            </tr>
          ))}
        </tbody>
        {/* FR-060's total row. Rendered only when the response carried one — a total row
            of five blanks reads as a rendering fault, not as a total. */}
        {profile.total === null ? null : (
          <tfoot>
            <tr>
              <th scope="row" className={styles.categoryCell}>
                All types
              </th>
              <td className={styles.numeric}>{formatCount(profile.total.count)}</td>
              <td className={styles.numeric}>
                {formatMoneyMeasureAmount(profile.total.averageCost)}
              </td>
              <td className={styles.numeric}>
                {formatMoneyMeasureAmount(profile.total.averageAmountRequested)}
              </td>
              <td className={styles.numeric}>
                {formatMoneyMeasurePercentage(profile.total.percentageOfCost)}
              </td>
            </tr>
          </tfoot>
        )}
      </table>
    </div>
  );
}

/** One of FR-062's three headline proportions, as a sentence with its own denominator. */
function proportionValue(metric: ProportionMetric | null): string | null {
  if (metric === null) return null;
  const share = formatPercentage(metric.percentage);
  if (metric.count === null || metric.population === null) return share;
  return `${share} (${formatCount(metric.count)} of ${formatCount(metric.population)})`;
}

/**
 * The accessible text alternative for `WellbeingComparisonChart` (Revision 10, wbs:6.8,
 * reviewer item 2) — a real `<table>`, drawn from the SAME `WellbeingComparisonData` the
 * chart draws, per ADR-029's "the table is the content" rule this app applies to every other
 * chart it draws.
 *
 * **Why this exists now and did not before.** Before this revision the "Level of need" panel
 * also rendered three separate per-question `DistributionChart`s beneath the comparison
 * chart, and THEIR tables were this figure's accessible content
 * (`RoundStatisticsCharts.tsx`'s own header: "the three per-question `DistributionChart`s that
 * already render underneath it"). The reviewer asked those three removed as duplicate content
 * now that the combined chart already shows them — which is correct for a SIGHTED reader, but
 * removing them with nothing in their place would have left the combined chart's data with no
 * text alternative at all, a WCAG 1.1.1 failure this component exists to prevent.
 *
 * Same disclosure UX as `DistributionChart`'s own (Revision 9, reviewer item 1): hidden behind
 * `.srOnly` by default, one "Show the data table" toggle, printed regardless via
 * `data-print="datatable"`/`print.css`'s `!important` override — this is the "other
 * statistics tables" default reviewer item 1 (this file, below) preserves for every section
 * except the one it names.
 */
function WellbeingComparisonTable({ data }: { data: WellbeingComparisonData }) {
  const tableId = useId();
  const [tableOnScreen, setTableOnScreen] = useState(false);
  return (
    <>
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
      <div
        id={tableId}
        className={classNames(styles.tableScroll, tableOnScreen ? undefined : styles.srOnly)}
        data-print="datatable"
      >
        <table className={styles.table}>
          <caption className={styles.srOnly}>
            Wellbeing, last year, all questions. Share of responses, by answer option and
            question.
          </caption>
          <thead>
            <tr>
              <th scope="col" className={styles.plainHeaderCell}>
                Response
              </th>
              {data.series.map((series) => (
                <th key={series.key} scope="col" className={`${styles.plainHeaderCell} ${styles.numeric}`}>
                  {series.heading}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.rows.map((row) => (
              <tr key={row.value}>
                <th scope="row" className={styles.categoryCell}>
                  {row.label}
                </th>
                {data.series.map((series) => {
                  const value = row[series.key];
                  return (
                    <td key={series.key} className={styles.numeric}>
                      {typeof value === "number" ? (
                        formatPercentage(value)
                      ) : (
                        <span className={styles.notAvailable}>{NOT_RECORDED}</span>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

export function RoundStatistics({
  response,
  roundOpenedOn = null,
  roundClosedOn = null,
}: {
  response: RoundStatisticsResponse;
  /** The open round's dates from the direct read, for the Round progress sentence's *d* (R16). */
  roundOpenedOn?: string | null;
  roundClosedOn?: string | null;
}) {
  const metrics = response.metrics;

  // FR-061's four delivered distributions — ethnicity joined the other three at TAD §0.11
  // and is built by the same two lines as each of them, deliberately: it is not a special
  // case in this file and must not become one. `visual` is Fix 3's chart, composed
  // alongside each `DistributionChart` — its own header explains why the pair share one
  // heading. Where the flow sends no ethnic-group distribution (every environment outside
  // DEV today) `buildSeries` returns `null` and the block is absent, same as any other.
  const genderSeries = buildSeries(metrics.genderDistribution, APPLICANT_GENDER_LABELS);
  const ageSeries = buildSeries(metrics.ageRangeDistribution, AGE_RANGE_LABELS);
  const applicantTypeSeries = buildSeries(
    metrics.applicantTypeDistribution,
    APPLICANT_TYPE_LABELS,
  );
  const ethnicGroupSeries = buildSeries(metrics.ethnicGroupDistribution, ETHNIC_GROUP_LABELS);
  const applicantCharts: { title: string; series: Series; visual: ReactNode }[] = [
    ...(genderSeries === null
      ? []
      : [{ title: "Gender", series: genderSeries, visual: <CategoryBars series={genderSeries} figures="share-only" /> }]),
    ...(ageSeries === null
      ? []
      : [{ title: "Age range", series: ageSeries, visual: <ColumnChart series={ageSeries} colorIndex={1} /> }]),
    ...(applicantTypeSeries === null
      ? []
      : [
          {
            title: "Applicant type",
            series: applicantTypeSeries,
            visual: <DonutChart series={applicantTypeSeries} />,
          },
        ]),
    // `CategoryBarChart`, not `CompositionPieChart`: six categories is past the point a pie
    // can be read by angle, and — unlike applicant type — these six are not a three-way
    // whole-population split a reader compares as parts of one circle. The bar chart also
    // plots `percentage` (`RoundStatisticsCharts.tsx`'s `dataKey="percentage"`), which is
    // the measure TAD §0.11 approved: a share of the round's applications, never a raw
    // count. Nothing here derives that share — it is the value the flow computed.
    ...(ethnicGroupSeries === null
      ? []
      : [
          {
            title: "Ethnic group",
            series: ethnicGroupSeries,
            visual: <CategoryBars series={ethnicGroupSeries} figures="share-only" />,
          },
        ]),
  ];

  const lifeSatisfactionSeries = buildSeries(
    metrics.lifeSatisfactionDistribution,
    LIFE_SATISFACTION_LABELS,
  );
  // EF-12 second half — reviewer-waived C-COM-002 2026-09-18, bundled with EF-43. Same
  // buildSeries/DistributionChart pattern as lifeSatisfactionSeries above; `null` whenever
  // the flow response does not carry the key, same absence rule as every other distribution.
  const circumstanceScoreSeries = buildSeries(
    metrics.circumstanceScoreDistribution,
    CIRCUMSTANCE_SCORE_BAND_LABELS,
  );
  // FR-062's three "last year" agreement-scale questions, combined into the one multi-series
  // chart every question's own figures now live in (Revision 10, wbs:6.8, reviewer item 2) —
  // `domain/charts.ts`'s header explains the axis assignment; `WellbeingComparisonTable` above
  // is this figure's accessible content, replacing the three separate per-question
  // `DistributionChart`s a prior revision drew underneath it. `null` when the flow sent no
  // questions at all, same absence rule as everything else on this screen.
  const wellbeingComparison = buildWellbeingComparisonData(metrics.wellbeingLastYear);

  const progressItems: Item[] = [
    ...present(
      "Applications received",
      metrics.applicationsReceived === null
        ? null
        : formatCount(metrics.applicationsReceived.count),
    ),
    ...present(
      "Applications per day",
      metrics.applicationsPerDay === null ? null : formatRate(metrics.applicationsPerDay.value),
    ),
    // "Days the round has been open" is NOT shown in the card app (reviewer R14, WI-0012,
    // ADR-066 decision 3); the first app keeps it until WI-0012 is built there.
  ];

  const exceptionalItems: Item[] = [
    ...present(
      "Applications citing any exceptional circumstance",
      metrics.exceptionalFundingSummary === null
        ? null
        : formatCount(metrics.exceptionalFundingSummary.anyCount),
    ),
    ...present(
      "Share of the round citing any exceptional circumstance",
      metrics.exceptionalFundingSummary === null
        ? null
        : formatPercentage(metrics.exceptionalFundingSummary.anyPercentage),
    ),
    ...present(
      "Average exceptional funding requested",
      metrics.exceptionalFundingSummary === null
        ? null
        : formatMoneyMeasureAmount(metrics.exceptionalFundingSummary.averageAmountRequested),
    ),
  ];
  const exceptionalSeries = buildSeries(
    metrics.exceptionalCircumstanceMix,
    EXCEPTIONAL_CIRCUMSTANCE_LABELS,
  );

  const proportionItems: Item[] = [
    ...present(
      "Carers providing high-hours care",
      proportionValue(metrics.highHoursCareProportion),
    ),
    ...present(
      "Reporting low life satisfaction",
      proportionValue(metrics.lowLifeSatisfactionProportion),
    ),
    ...present(
      "Unable to take a break when needed",
      proportionValue(metrics.unableToTakeBreakProportion),
    ),
  ];

  const hasNeedContent =
    wellbeingComparison !== null ||
    lifeSatisfactionSeries !== null ||
    circumstanceScoreSeries !== null ||
    proportionItems.length > 0;

  const receivedCount = metrics.applicationsReceived?.count ?? null;
  const now = new Date();

  return (
    <>
      {/* "Figures of this round" and the computedOn stamp as a white pill beside it
          (RoundOverview.jsx lines 218-221). The stamp's wording is the card app's (R11,
          ADR-066): "Computed on {date} at {time}". It still prints (FR-039, TAD §6.4: the
          printed pack is the only durable record of what a board saw), and the denominator
          stays on the page beneath it. */}
      <div className={styles.figuresHeader}>
        <h2 className={styles.figuresHeading}>Figures of this round</h2>
        <p className={styles.stampPill} data-print="stamp">
          {computedOnStamp(response.computedOn)}
        </p>
      </div>
      {response.populationReceived === null ? null : (
        <p className={styles.stampDenominator}>
          These figures are counted over {formatCount(response.populationReceived)} applications
          received in this round.
        </p>
      )}
      {progressItems.length === 0 ? null : (
        <Panel
          heading="Round progress"
          eyebrow="Round progress"
          sentence={roundProgressSentence(receivedCount, roundOpenedOn, roundClosedOn, now)}
        >
          <ProgressTiles items={progressItems} />
        </Panel>
      )}
      {exceptionalItems.length === 0 && exceptionalSeries === null ? null : (
        <Panel
          heading="Exceptional circumstances"
          eyebrow="Exceptional circumstances"
          sentence={exceptionalSentence(
            metrics.exceptionalFundingSummary?.anyCount ?? null,
            metrics.exceptionalFundingSummary?.population ?? null,
          )}
        >
          {exceptionalItems.length === 0 ? null : <ProgressTiles items={exceptionalItems} />}
          {metrics.exceptionalFundingSummary === null ? null : (
            <p className={styles.cardNote}>
              The average exceptional funding requested is shown only where enough
              applications citing exceptional circumstances carry a figure.
            </p>
          )}
          {exceptionalSeries === null ? null : (
            <DistributionChart
              title="Exceptional circumstance cited"
              series={exceptionalSeries}
              alwaysShowTable
              visual={<CategoryBars series={exceptionalSeries} />}
            />
          )}
        </Panel>
      )}
      {metrics.breakTypeProfile === null ? null : (
        <Panel heading="Type of break">
          <BreakTypeTable profile={metrics.breakTypeProfile} />
        </Panel>
      )}
      {applicantCharts.length === 0 ? null : (
        <Panel
          heading="Who applied in this round"
          eyebrow="Who applied in this round"
          eyebrowTone="purple"
          sentence={WHO_APPLIED_SENTENCE}
        >
          <div className={styles.applicantGrid}>
            {applicantCharts.map((chart) => (
              <DistributionChart
                key={chart.title}
                title={chart.title}
                series={chart.series}
                figures="share-only"
                visual={chart.visual}
              />
            ))}
          </div>
        </Panel>
      )}
      {!hasNeedContent ? null : (
        <Panel heading="Level of need" eyebrow="Level of need" sentence={LEVEL_OF_NEED_SENTENCE}>
          <div className={styles.applicantGrid}>
            {wellbeingComparison === null ? null : (
              <section className={styles.chartBlock}>
                <h3 className={styles.fieldHeading}>Wellbeing, last year (all questions)</h3>
                <GroupedColumnChart data={wellbeingComparison} />
                <WellbeingComparisonTable data={wellbeingComparison} />
              </section>
            )}
            {lifeSatisfactionSeries === null ? null : (
              <DistributionChart
                title="Life satisfaction, 0 to 10"
                series={lifeSatisfactionSeries}
                countHeading="Responses"
                visual={<ColumnChart series={lifeSatisfactionSeries} height={200} />}
              />
            )}
            {circumstanceScoreSeries === null ? null : (
              <DistributionChart
                title="Circumstance score, 0 to 60"
                series={circumstanceScoreSeries}
                countHeading="Applications"
                visual={<ColumnChart series={circumstanceScoreSeries} height={200} />}
              />
            )}
          </div>
          {proportionItems.length === 0 ? null : <Definitions items={proportionItems} />}
        </Panel>
      )}
    </>
  );
}
