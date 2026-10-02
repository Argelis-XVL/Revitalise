/**
 * The landing screen's decisions, with no React in them (WBS 6.9, FR-056..FR-063).
 *
 * Two jobs, both pure:
 *
 *   1. `deriveLandingView` — given what the direct `rev_roundfinance` read found and what
 *      the statistics flow returned, decide what each region of the screen shows. TAD
 *      §5.4's three steps, and every diagnostic state §5.3 names.
 *   2. `buildSeries` — turn one distribution into ONE array, which the data table and the
 *      SVG bar chart both render. ADR-029: "chart drawn from the same array — the two can
 *      never disagree."
 *
 * They live here rather than in the page for the reason every other `src/domain/` module
 * does: the branch that decides whether a trustee sees a figure or a diagnostic is the
 * part worth testing exhaustively, and it should be testable without rendering anything.
 */
import {
  APPLICANT_GENDER_LABELS,
  AGE_RANGE_LABELS,
  APPLICANT_TYPE_LABELS,
  optionLabel,
} from "../dataverse/schema";
import { isKnownStatus } from "../dataverse/roundStatistics";
import type {
  Distribution,
  OpenRoundResult,
  RoundFinance,
  RoundStatisticsResponse,
} from "../dataverse/types";

/** A first-class informational state, rendered through `StateMessage` (`role="note"`). */
export interface DiagnosticMessage {
  heading: string;
  explanation: string;
}

/** What the FR-063 financial block shows. */
export type FinanceOutcome =
  | { kind: "loading" }
  | { kind: "figures"; round: RoundFinance }
  | { kind: "diagnostic"; message: DiagnosticMessage };

/** What the FR-058..FR-062 statistics blocks show. */
export type StatisticsOutcome =
  | { kind: "loading" }
  | { kind: "figures"; response: RoundStatisticsResponse }
  | { kind: "diagnostic"; message: DiagnosticMessage };

export interface LandingView {
  /** The round this screen is about, when anything knows. Drives the `<h1>`. */
  roundName: string | null;
  finance: FinanceOutcome;
  statistics: StatisticsOutcome;
}

/** The state of one of the screen's two asynchronous reads. */
export type QueryPhase = "loading" | "loaded" | "error";

export interface OpenRoundInput {
  phase: QueryPhase;
  /** Present when `phase` is `"loaded"`. */
  result?: OpenRoundResult;
  /** Present when `phase` is `"error"`. */
  errorMessage?: string;
}

export interface StatisticsInput {
  phase: QueryPhase;
  /** Present when `phase` is `"loaded"` — for ANY status, including a non-`ok` one. */
  response?: RoundStatisticsResponse;
  errorMessage?: string;
}

/** The sentence every diagnostic on this screen ends with. The list is still reachable. */
const LIST_IS_STILL_REACHABLE =
  "The applications list is unaffected and you can still open it from the link above.";

/**
 * Wording for the flow's own verdict — TAD §5.3's row, one state at a time.
 *
 * The `default` branch is not a formality. The flow is a separately-deployed artefact with
 * its own change history, and a failure path added to it after this build shipped can
 * introduce a status string this code has never seen. TAD §3.3 point 4 governs regardless:
 * anything other than `ok` means the diagnostic state and no figures at all. So an
 * unrecognised status renders §5.3's generic "figures unavailable" wording and quotes the
 * value verbatim, which is what makes it diagnosable rather than mysterious.
 */
export function describeStatisticsStatus(status: string): DiagnosticMessage {
  switch (status) {
    case "pending":
      // Not one of TAD §3.3's five flow-reported statuses (`KNOWN_ROUND_STATISTICS_STATUSES`
      // deliberately excludes it) — synthesised by `fetchRoundStatistics` itself
      // (IMP-0359, IMP-0365) when its bounded poll times out before the Dataverse-triggered
      // flow finishes. Routed through this same switch anyway, because a trustee reading
      // the screen needs wording, not an architectural distinction between "the flow said
      // so" and "this app inferred it".
      //
      // **It is a DIAGNOSTIC state, not an error state** (TAD §8.3's Revision 5 bullet). It
      // therefore renders through `StateMessage` like the other five — `role="note"`, never
      // `role="alert"` — because a computation still running is not something to interrupt a
      // screen-reader trustee about. `describeStatistics` below routes every non-`ok` status
      // here and `LandingPage.tsx` renders every one of them through `StateMessage`, so
      // `pending` inherits that role rather than declaring one.
      //
      // The wording says nothing about who asked. Under ADR-038 a recomputation is triggered
      // by a MOUNT whose document was stale just as often as by the button, and a trustee who
      // never pressed anything must not be told "a refresh was requested" as though they had.
      return {
        heading: "Figures are being recalculated",
        explanation:
          "The statistics service is still computing this round's figures and has not " +
          "finished yet. No figures are shown rather than out-of-date ones. Press Refresh " +
          "figures in a moment to look again. " +
          LIST_IS_STILL_REACHABLE,
      };
    case "no-open-round":
      return {
        heading: "No round is open",
        explanation:
          "The statistics service found no grant round marked as open, so it computed no " +
          "figures. The round's figures appear here once the process owner opens a round. " +
          LIST_IS_STILL_REACHABLE,
      };
    case "ambiguous-round":
      return {
        heading: "More than one round is open",
        explanation:
          "The statistics service found more than one grant round marked as open and will " +
          "not choose between them, so no figures are shown. Ask the process owner to " +
          "leave exactly one round open. " +
          LIST_IS_STILL_REACHABLE,
      };
    case "truncated":
      return {
        heading: "Too many applications to summarise",
        explanation:
          "This round holds more applications than the statistics service will summarise " +
          "in one pass. No figures are shown rather than a partial set, because a " +
          "percentage over some of the round would read exactly like a percentage over all " +
          "of it. " +
          LIST_IS_STILL_REACHABLE,
      };
    case "threshold-unset":
      return {
        heading: "Round figures are unavailable",
        explanation:
          "The statistics service is missing a threshold it needs before it will report " +
          "any figure, so it returned none rather than a partial set. Ask the process " +
          "owner to set the round-statistics thresholds. " +
          LIST_IS_STILL_REACHABLE,
      };
    default:
      return {
        heading: "Round figures are unavailable",
        explanation:
          `The statistics service reported a state this screen does not recognise ("${status}"), ` +
          "so no figures are shown. " +
          LIST_IS_STILL_REACHABLE,
      };
  }
}

/**
 * The reconciliation failure — TAD §5.4 step 3.
 *
 * Applied to BOTH regions, which is the whole point of it: showing FR-063's financial
 * position for one round beside FR-058..FR-062's application figures for another would be
 * wrong in a way no reader could detect, because each half is internally consistent and
 * neither carries the other's round key.
 */
const ROUND_MISMATCH: DiagnosticMessage = {
  heading: "The round changed while these figures were being read",
  explanation:
    "The round record and the statistics service do not name the same round, so no " +
    "figures are shown at all. Mixing one round's financial position with another " +
    "round's application figures would look completely normal and be wrong. Use " +
    "Refresh figures to read both again. " +
    LIST_IS_STILL_REACHABLE,
};

function describeOpenRound(input: OpenRoundInput): FinanceOutcome {
  if (input.phase === "loading") return { kind: "loading" };

  if (input.phase === "error") {
    return {
      kind: "diagnostic",
      message: {
        heading: "The round record could not be read",
        explanation:
          (input.errorMessage ?? "The portal could not read the round record.") +
          " The round's calendar and financial position are not shown. " +
          LIST_IS_STILL_REACHABLE,
      },
    };
  }

  const result = input.result;
  if (result === undefined) {
    // Defensive: a caller claiming "loaded" with nothing loaded. Reported as a diagnostic
    // rather than crashed on, because a blank region is the one outcome this screen must
    // never produce.
    return {
      kind: "diagnostic",
      message: {
        heading: "The round record could not be read",
        explanation:
          "The portal reported the round record as loaded but returned nothing. " +
          LIST_IS_STILL_REACHABLE,
      },
    };
  }

  switch (result.kind) {
    case "one":
      return { kind: "figures", round: result.round };
    case "none":
      return {
        kind: "diagnostic",
        message: {
          heading: "No round is open",
          explanation:
            "No grant round is currently marked as open, so there is no round calendar " +
            "and no financial position to show. " +
            LIST_IS_STILL_REACHABLE,
        },
      };
    case "ambiguous":
      return {
        kind: "diagnostic",
        message: {
          heading: "More than one round is open",
          explanation:
            `${String(result.count)} grant rounds are marked as open. This screen will not ` +
            "choose between them, so no round figures are shown. Ask the process owner to " +
            "leave exactly one round open, then use Refresh figures. " +
            LIST_IS_STILL_REACHABLE,
        },
      };
  }
}

function describeStatistics(input: StatisticsInput): StatisticsOutcome {
  if (input.phase === "loading") return { kind: "loading" };

  if (input.phase === "error") {
    return {
      kind: "diagnostic",
      message: {
        heading: "Round figures are unavailable",
        explanation:
          (input.errorMessage ?? "The statistics service could not be reached.") +
          " No figures are shown rather than a partial set. Use Refresh figures to try " +
          "again. " +
          LIST_IS_STILL_REACHABLE,
      },
    };
  }

  const response = input.response;
  if (response === undefined) {
    return {
      kind: "diagnostic",
      message: {
        heading: "Round figures are unavailable",
        explanation:
          "The statistics service reported success but returned nothing. " +
          LIST_IS_STILL_REACHABLE,
      },
    };
  }

  // TAD §3.3 point 4. `ok` is the ONLY value that shows a figure — including for a status
  // this build does not recognise, which `describeStatisticsStatus` handles by name.
  if (response.status !== "ok") {
    return { kind: "diagnostic", message: describeStatisticsStatus(response.status) };
  }
  return { kind: "figures", response };
}

/**
 * Can the two halves be shown side by side? TAD §5.4 step 3.
 *
 * A null on either side is treated as a MISMATCH, not as a pass. The assertion the TAD
 * asks for is `response.roundKey === financeRow.rev_name`; a null cannot satisfy it, and
 * "we could not check" must not render as "we checked and it agreed".
 *
 * **Revision 5 makes this check load-bearing rather than defensive** (TAD §5.4's Revision 5
 * note: *"step 3 matters more now, not less"*). Freshness is an age bound and not a request
 * identity (§5.3.1), so the document a trustee reads may have been computed for someone
 * else's ask, minutes before their own finance row was read. This comparison is now the
 * ONLY thing standing between that and a financial position from one round rendered beside
 * application figures from another — an outcome in which each half is internally consistent
 * and no reader could detect the mismatch.
 */
function roundKeysAgree(round: RoundFinance, response: RoundStatisticsResponse): boolean {
  return (
    round.roundKey !== null &&
    response.roundKey !== null &&
    round.roundKey === response.roundKey
  );
}

/**
 * The whole screen's state, from the two reads — TAD §5.4.
 *
 * The two reads are deliberately INDEPENDENT: a finance read that fails degrades the
 * financial block and nothing else, and a flow call that fails degrades the statistics
 * blocks and nothing else. That is the same rule `repository.ts`'s region lookup already
 * follows — "a failure here degrades the region column and NOTHING else" — and it matters
 * most in the state this feature will actually ship into, where the trustee role's new
 * `prvReadrev_roundfinance` grant may have reached one environment and not another.
 *
 * The one thing that couples them is reconciliation, and only when both actually have
 * figures to show.
 */
export function deriveLandingView(
  roundInput: OpenRoundInput,
  statisticsInput: StatisticsInput,
): LandingView {
  let finance = describeOpenRound(roundInput);
  let statistics = describeStatistics(statisticsInput);

  if (
    finance.kind === "figures" &&
    statistics.kind === "figures" &&
    !roundKeysAgree(finance.round, statistics.response)
  ) {
    finance = { kind: "diagnostic", message: ROUND_MISMATCH };
    statistics = { kind: "diagnostic", message: ROUND_MISMATCH };
  }

  const roundName =
    finance.kind === "figures"
      ? finance.round.roundKey
      : statistics.kind === "figures"
        ? statistics.response.roundKey
        : null;

  return { roundName, finance, statistics };
}

/**
 * True when the flow reported a status this build knows about. Re-exported so the page can
 * say so without importing the dataverse layer directly.
 */
export { isKnownStatus };

/* ------------------------------------------------------------------------------------- *
 * Charts — ADR-029, TAD §8.1
 * ------------------------------------------------------------------------------------- */

/** One row of a distribution: a table row and a bar, from the same object. */
export interface SeriesRow {
  /** The option-set integer, verbatim from the response (TAD §3.3 point 2). */
  value: number;
  /** Resolved through this app's own transcribed map. `Unknown (n)` on drift. */
  label: string;
  count: number;
  /** As the response computed it. Never derived here from count/population. */
  percentage: number | null;
}

export interface Series {
  rows: SeriesRow[];
  /** The denominator, on the page beside the percentages (TAD §3.3 point 1). */
  population: number | null;
  /**
   * The scale the bars are drawn against. At least 1, so an all-zero series draws flat
   * rather than dividing by zero.
   */
  maxCount: number;
}

/**
 * Builds the ONE array a distribution's table and chart both render.
 *
 * Returns `null` for an absent distribution, which is how every FR-059..FR-062 section
 * renders today: the flow's first version emits `null` for all of them, so the section is
 * not rendered at all — no heading over an empty body, no zero (TAD §3.3 point 3).
 *
 * Labels come from `labels`, never from the response. TAD §3.3 point 2: categories carry
 * the raw integer and nothing else, so there is no label in the payload to trust, and
 * `optionLabel`'s `Unknown (n)` makes option-set drift visible instead of rendering
 * plausible wrong text (`IMP-0019`).
 */
export function buildSeries(
  distribution: Distribution | null,
  labels: Readonly<Record<number, string>>,
): Series | null {
  if (distribution === null || distribution.categories.length === 0) return null;
  const rows: SeriesRow[] = distribution.categories.map((category) => ({
    value: category.value,
    label: optionLabel(labels, category.value),
    count: category.count,
    percentage: category.percentage,
  }));
  const maxCount = Math.max(1, ...rows.map((row) => row.count));
  return { rows, population: distribution.population, maxCount };
}

/** FR-061's three delivered distributions, and the label map each is rendered through. */
export const APPLICANT_DISTRIBUTION_LABELS = {
  gender: APPLICANT_GENDER_LABELS,
  ageRange: AGE_RANGE_LABELS,
  applicantType: APPLICANT_TYPE_LABELS,
} as const;

/**
 * The one-sentence headline an SVG chart carries as its `aria-label` (ADR-029).
 *
 * The table beside it is the accessible content and satisfies 1.1.1 and 1.3.1 properly, so
 * this label's job is not to re-read the data — it is to tell a screen-reader user what
 * the picture they are being told about shows, and that the numbers are in the table. A
 * label that paraphrased all thirteen rows would be the `alt`-string anti-pattern ADR-029
 * exists to avoid.
 */
export function chartSummary(title: string, series: Series): string {
  const leader = series.rows.reduce((best, row) => (row.count > best.count ? row : best));
  const denominator =
    series.population === null
      ? ""
      : ` out of ${String(series.population)} applications in this round`;
  return (
    `Bar chart: ${title}. ${String(series.rows.length)} categories. ` +
    `Largest is ${leader.label}, ${String(leader.count)}${denominator}. ` +
    "Every value is in the table beside this chart."
  );
}
