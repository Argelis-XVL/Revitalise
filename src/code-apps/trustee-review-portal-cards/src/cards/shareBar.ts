/**
 * The round hero's application-share bar — ADR-065 of TAD trustee-portal-design-2 (reviewer R13,
 * R15: "Yes that is exactly what it means"). Card app only; replaces the design's close-date bar.
 *
 * n = this round's `applicationsReceived.count`; p = the seeded count of applications received
 * before the portal (`RoundStatisticsHistoryPriorApplicationCount`, read from
 * `historicApplicationsByMonth.priorApplicationCount`); total T = n + p ONLY — earlier rounds
 * already in Dataverse and the flow's `months` array are not used. The fill is n / T.
 *
 * Returns what the hero shows, for every row of the ADR-065 table. The bar itself is decorative
 * (`aria-hidden`); the lines are the content.
 */
import { formatCount, formatPercentage, NOT_RECORDED } from "../domain/format";
import type { HistoricApplications } from "../dataverse/types";

export interface ShareBar {
  /** 0..1, or `null` when no bar is drawn. */
  readonly fill: number | null;
  /** The text lines under the bar, in order. Empty when nothing is shown. */
  readonly lines: readonly string[];
}

function thisRound(n: number): string {
  return `This round: ${n === 1 ? "1 application" : `${formatCount(n)} applications`}`;
}

export function shareBar(count: number | null, history: HistoricApplications | null): ShareBar {
  if (count === null) return { fill: null, lines: [] };
  const prior = history === null || history.understatedTotal ? null : history.priorApplicationCount;
  if (prior === null) {
    return { fill: null, lines: [thisRound(count), `All applications: ${NOT_RECORDED}`] };
  }
  const total = count + prior;
  if (total === 0) return { fill: null, lines: [thisRound(0), "All applications: 0"] };
  const share = (count / total) * 100;
  return {
    fill: count / total,
    lines: [
      thisRound(count),
      `All applications: ${formatCount(total)}, including ${formatCount(prior)} from before the portal`,
      `${formatPercentage(share)} of all applications`,
    ],
  };
}
