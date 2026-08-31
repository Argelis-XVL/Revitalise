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
 * Two metrics will never arrive, and are treated exactly like any other absence rather
 * than being special-cased into a visible apology:
 *
 *   - `ethnicGroupDistribution` — permanently `null`. There is no column and never has
 *     been (TAD §3.4, A-R24). There is no ethnicity heading anywhere in this file, because
 *     a heading that never gets content is worse than no heading.
 *   - FR-062's three proportions — `null` until OQ-039 supplies three thresholds nobody
 *     has stated (TAD §5.2, A-R29). They are rendered by the same code as any other
 *     metric; nothing here sets a threshold or offers to.
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
 * prior one) and an ethnic-group chart. Neither is built: the second series is FR-061's
 * benchmark comparison, withdrawn by the reviewer's own decision (`domain/landing.ts`'s
 * `Distribution` doc, ADR-029 as amended, and `LandingPage.test.tsx`'s own
 * "renders no benchmark, second series or comparison column" assertion) — there is no
 * "prior round" figure in this response to draw a second bar from, and reinstating that
 * withdrawn scope is a commercial/architecture decision, not a chart-polish one. The
 * ethnic-group chart has no data source at all (this file's own header, above) and is a
 * separate, DPO-gated track. `domain/charts.ts`'s header carries the same explanation.
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
import type { ReactNode } from "react";
import {
  formatCount,
  formatDateTime,
  formatMoneyMeasureAmount,
  formatMoneyMeasurePercentage,
  formatPercentage,
  formatRate,
} from "../domain/format";
import { buildSeries } from "../domain/landing";
import type { Series } from "../domain/landing";
import { buildWellbeingComparisonData } from "../domain/charts";
import {
  AGREEMENT_RESPONSE_LABELS,
  APPLICANT_GENDER_LABELS,
  AGE_RANGE_LABELS,
  APPLICANT_TYPE_LABELS,
  BREAK_TYPE_LABELS,
  EXCEPTIONAL_CIRCUMSTANCE_LABELS,
  LIFE_SATISFACTION_LABELS,
  optionLabel,
  WELLBEING_QUESTION_HEADINGS,
} from "../dataverse/schema";
import type {
  BreakTypeProfile,
  ProportionMetric,
  RoundStatisticsResponse,
} from "../dataverse/types";
import { Definitions, Panel, StatTileRow } from "./Panel";
import { DistributionChart } from "./DistributionChart";
import { CategoryBarChart, CompositionPieChart, WellbeingComparisonChart } from "./RoundStatisticsCharts";
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
      <table className={styles.table}>
        <caption className={styles.tableCaption}>{breakTypeCaption(profile.population)}</caption>
        <thead>
          <tr>
            <th scope="col" className={styles.plainHeaderCell}>
              Type of break
            </th>
            <th scope="col" className={styles.plainHeaderCell}>
              Applications
            </th>
            <th scope="col" className={styles.plainHeaderCell}>
              Average total cost
            </th>
            <th scope="col" className={styles.plainHeaderCell}>
              Average grant requested
            </th>
            <th scope="col" className={styles.plainHeaderCell}>
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

export function RoundStatistics({ response }: { response: RoundStatisticsResponse }) {
  const metrics = response.metrics;

  // FR-061's three delivered distributions. Ethnicity is not here and has no slot to be
  // absent from — see this file's header. `visual` is Fix 3's chart, composed alongside
  // each `DistributionChart` — its own header explains why the pair share one heading.
  const genderSeries = buildSeries(metrics.genderDistribution, APPLICANT_GENDER_LABELS);
  const ageSeries = buildSeries(metrics.ageRangeDistribution, AGE_RANGE_LABELS);
  const applicantTypeSeries = buildSeries(
    metrics.applicantTypeDistribution,
    APPLICANT_TYPE_LABELS,
  );
  const applicantCharts: { title: string; series: Series; visual: ReactNode }[] = [
    ...(genderSeries === null
      ? []
      : [{ title: "Gender", series: genderSeries, visual: <CategoryBarChart series={genderSeries} /> }]),
    ...(ageSeries === null
      ? []
      : [{ title: "Age range", series: ageSeries, visual: <CategoryBarChart series={ageSeries} /> }]),
    ...(applicantTypeSeries === null
      ? []
      : [
          {
            title: "Applicant type",
            series: applicantTypeSeries,
            visual: <CompositionPieChart series={applicantTypeSeries} />,
          },
        ]),
  ];

  // FR-062 — the three "last year" agreement-scale questions, plus life satisfaction.
  const wellbeingCharts: { title: string; series: Series; visual: ReactNode }[] = (
    metrics.wellbeingLastYear?.questions ?? []
  ).flatMap((question) => {
    const series = buildSeries(
      { population: question.population, categories: question.categories },
      AGREEMENT_RESPONSE_LABELS,
    );
    if (series === null) return [];
    // A question whose column this build does not know still renders, under its own raw
    // column name. Dropping a question the flow chose to send would be a silent omission.
    return [
      {
        title: WELLBEING_QUESTION_HEADINGS[question.column] ?? question.column,
        series,
        visual: <CategoryBarChart series={series} />,
      },
    ];
  });
  const lifeSatisfactionSeries = buildSeries(
    metrics.lifeSatisfactionDistribution,
    LIFE_SATISFACTION_LABELS,
  );
  // The one genuinely multi-series chart this pass builds — every question compared on
  // the shared agreement-response axis. `domain/charts.ts`'s header explains why this is
  // not the withdrawn benchmark shape. `null` when the flow sent no questions at all,
  // same absence rule as everything else on this screen.
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
    ...present(
      "Days the round has been open",
      metrics.applicationsPerDay?.days === undefined ||
        metrics.applicationsPerDay.days === null
        ? null
        : formatCount(metrics.applicationsPerDay.days),
    ),
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
    wellbeingCharts.length > 0 || lifeSatisfactionSeries !== null || proportionItems.length > 0;

  return (
    <>
      {/*
        The flow's own freshness statement, and it belongs to THESE figures only.
        TAD §8.3: the FR-063 block beside this one carries its own dated statement, and one
        "as at" line covering both would be wrong about one of them. It is text rather than
        a tooltip, and it prints (FR-039, §8.2 — under the live design the printed pack is
        the only durable record of what a board saw, TAD §6.4).
      */}
      <p className={styles.freshness} data-print="stamp">
        Round figures computed on {formatDateTime(response.computedOn)}
        {response.populationReceived === null
          ? "."
          : `, over ${formatCount(response.populationReceived)} applications received in this round.`}
      </p>

      {progressItems.length === 0 ? null : (
        <Panel heading="Round progress">
          {/* Fix 3: `Round 4.pptx`'s own headline figure, "applications received", as a
              KPI tile rather than a definition list — see this file's header. */}
          <StatTileRow items={progressItems} />
        </Panel>
      )}

      {exceptionalItems.length === 0 && exceptionalSeries === null ? null : (
        <Panel heading="Exceptional circumstances">
          {exceptionalItems.length === 0 ? null : <Definitions items={exceptionalItems} />}
          {/* ADR-039, TAD §6.3.5 — the one figure in this list that can be a deliberate
              withholding rather than an absence. Threshold-agnostic: `k` lives in
              `rev_setting`, is read only by the flow, and never travels in the response, so
              this screen has no number to name. */}
          {metrics.exceptionalFundingSummary === null ? null : (
            <p className={styles.hint}>
              The average exceptional funding requested is shown only where enough
              applications citing exceptional circumstances carry a figure.
            </p>
          )}
          {exceptionalSeries === null ? null : (
            <DistributionChart
              title="Exceptional circumstance cited"
              series={exceptionalSeries}
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
        <Panel heading="Who applied in this round">
          {/*
            Revision 8 (2026-08-31, wbs:6.9) — the reviewer's two asks for this panel, and
            they are one change: `figures="share-only"` drops each table's raw-count column
            (and, with it, `DistributionChart`'s own count-scaled horizontal bars — see that
            file's Revision 8 section for why the two go together), and `.applicantGrid` lays
            the remaining visuals out two per row instead of one full-width block each.

            THE DENOMINATOR SURVIVES THE COUNT COLUMN, DELIBERATELY. Every block still opens
            with `DistributionChart`'s unconditional "Counted over N applications in this
            round" line, which is the population these shares are taken over. TAD §3.3 point
            1 — "a percentage whose denominator is not on the page is not auditable" — is
            what makes a share-only table legible at all, so dropping the counts without
            keeping that line would have been the one version of this change that is wrong.

            Only this panel takes the mode. "Level of need" below keeps its counts: FR-062's
            per-question and life-satisfaction blocks count RESPONSES, not applications, and
            a response count is the figure that tells a trustee how many people answered at
            all — the reviewer's instruction named this section and no other.
          */}
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
        <Panel heading="Level of need">
          {/* Fix 3's one multi-series chart — every "last year" question compared on the
              shared response scale. Its own heading (distinct from any per-question one
              below) because it is a genuinely different view of the same figures, not a
              duplicate of one of them — see RoundStatisticsCharts.tsx's header for why it
              is still `aria-hidden`: the three per-question DistributionCharts right
              below already carry this same data as accessible content. */}
          {wellbeingComparison === null ? null : (
            <>
              <h3 className={styles.fieldHeading}>Wellbeing, last year (all questions)</h3>
              <WellbeingComparisonChart data={wellbeingComparison} />
            </>
          )}
          {wellbeingCharts.map((chart) => (
            <DistributionChart
              key={chart.title}
              title={chart.title}
              series={chart.series}
              countHeading="Responses"
              visual={chart.visual}
            />
          ))}
          {lifeSatisfactionSeries === null ? null : (
            <DistributionChart
              title="Life satisfaction, 0 to 10"
              series={lifeSatisfactionSeries}
              countHeading="Responses"
              visual={<CategoryBarChart series={lifeSatisfactionSeries} />}
            />
          )}
          {proportionItems.length === 0 ? null : <Definitions items={proportionItems} />}
        </Panel>
      )}
    </>
  );
}
