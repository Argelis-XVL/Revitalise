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
 */
import { formatAmount, formatCount, formatDateTime, formatPercentage, formatRate } from "../domain/format";
import { buildSeries } from "../domain/landing";
import type { Series } from "../domain/landing";
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
import { Definitions, Panel } from "./Panel";
import { DistributionChart } from "./DistributionChart";
import styles from "../styles/app.module.css";

interface Item {
  label: string;
  value: string;
}

/** Keeps a definition row out of the list when its metric did not arrive. */
function present(label: string, value: string | null): Item[] {
  return value === null ? [] : [{ label, value }];
}

/** FR-060 — the break-type breakdown. A table, not a chart: §8.1 scopes charting to FR-061/062. */
function BreakTypeTable({ profile }: { profile: BreakTypeProfile }) {
  return (
    <div className={styles.tableScroll}>
      <table className={styles.table}>
        <caption className={styles.tableCaption}>
          {profile.population === null
            ? "Applications, average cost and average grant requested, by type of break."
            : `Applications, average cost and average grant requested, by type of break, ` +
              `over ${formatCount(profile.population)} applications in this round.`}
        </caption>
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
              <td className={styles.numeric}>{formatAmount(row.averageCost)}</td>
              <td className={styles.numeric}>{formatAmount(row.averageAmountRequested)}</td>
              <td className={styles.numeric}>{formatPercentage(row.percentageOfCost)}</td>
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
              <td className={styles.numeric}>{formatAmount(profile.total.averageCost)}</td>
              <td className={styles.numeric}>
                {formatAmount(profile.total.averageAmountRequested)}
              </td>
              <td className={styles.numeric}>
                {formatPercentage(profile.total.percentageOfCost)}
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
  // absent from — see this file's header.
  const genderSeries = buildSeries(metrics.genderDistribution, APPLICANT_GENDER_LABELS);
  const ageSeries = buildSeries(metrics.ageRangeDistribution, AGE_RANGE_LABELS);
  const applicantTypeSeries = buildSeries(
    metrics.applicantTypeDistribution,
    APPLICANT_TYPE_LABELS,
  );
  const applicantCharts: { title: string; series: Series }[] = [
    ...(genderSeries === null ? [] : [{ title: "Gender", series: genderSeries }]),
    ...(ageSeries === null ? [] : [{ title: "Age range", series: ageSeries }]),
    ...(applicantTypeSeries === null
      ? []
      : [{ title: "Applicant type", series: applicantTypeSeries }]),
  ];

  // FR-062 — the three "last year" agreement-scale questions, plus life satisfaction.
  const wellbeingCharts: { title: string; series: Series }[] = (
    metrics.wellbeingLastYear?.questions ?? []
  ).flatMap((question) => {
    const series = buildSeries(
      { population: question.population, categories: question.categories },
      AGREEMENT_RESPONSE_LABELS,
    );
    if (series === null) return [];
    // A question whose column this build does not know still renders, under its own raw
    // column name. Dropping a question the flow chose to send would be a silent omission.
    return [{ title: WELLBEING_QUESTION_HEADINGS[question.column] ?? question.column, series }];
  });
  const lifeSatisfactionSeries = buildSeries(
    metrics.lifeSatisfactionDistribution,
    LIFE_SATISFACTION_LABELS,
  );

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
        : formatAmount(metrics.exceptionalFundingSummary.averageAmountRequested),
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
          <Definitions items={progressItems} />
        </Panel>
      )}

      {exceptionalItems.length === 0 && exceptionalSeries === null ? null : (
        <Panel heading="Exceptional circumstances">
          {exceptionalItems.length === 0 ? null : <Definitions items={exceptionalItems} />}
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
          {applicantCharts.map((chart) => (
            <DistributionChart key={chart.title} title={chart.title} series={chart.series} />
          ))}
        </Panel>
      )}

      {!hasNeedContent ? null : (
        <Panel heading="Level of need">
          {wellbeingCharts.map((chart) => (
            <DistributionChart
              key={chart.title}
              title={chart.title}
              series={chart.series}
              countHeading="Responses"
            />
          ))}
          {lifeSatisfactionSeries === null ? null : (
            <DistributionChart
              title="Life satisfaction, 0 to 10"
              series={lifeSatisfactionSeries}
              countHeading="Responses"
            />
          )}
          {proportionItems.length === 0 ? null : <Definitions items={proportionItems} />}
        </Panel>
      )}
    </>
  );
}
