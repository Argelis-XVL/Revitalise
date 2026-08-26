/**
 * The landing screen's decisions — TAD §5.3, §5.4, §8.1.
 *
 * This is the file that matters most on this screen. Every branch here decides whether a
 * trustee is shown a figure or told why there isn't one, and the failure that would be
 * hardest to notice is not a crash — it is a plausible number from the wrong round.
 */
import { describe, expect, it } from "vitest";
import {
  buildSeries,
  chartSummary,
  deriveLandingView,
  describeStatisticsStatus,
} from "./landing";
import type { StatisticsInput, OpenRoundInput } from "./landing";
import { APPLICANT_GENDER_LABELS, AGE_RANGE_LABELS } from "../dataverse/schema";
import type { Distribution } from "../dataverse/types";
import { makeRoundFinance, makeRoundStatistics, OPEN_ROUND_KEY } from "../test/harness";

const loadedRound: OpenRoundInput = {
  phase: "loaded",
  result: { kind: "one", round: makeRoundFinance() },
};
const loadedStats: StatisticsInput = { phase: "loaded", response: makeRoundStatistics() };

describe("deriveLandingView — the happy path", () => {
  it("shows both halves and names the round when the two round keys agree", () => {
    const view = deriveLandingView(loadedRound, loadedStats);
    expect(view.roundName).toBe(OPEN_ROUND_KEY);
    expect(view.finance.kind).toBe("figures");
    expect(view.statistics.kind).toBe("figures");
  });

  it("reports each read as loading independently", () => {
    const view = deriveLandingView({ phase: "loading" }, { phase: "loading" });
    expect(view.finance.kind).toBe("loading");
    expect(view.statistics.kind).toBe("loading");
    expect(view.roundName).toBeNull();
  });
});

describe("deriveLandingView — the two reads degrade independently", () => {
  it("keeps the flow's figures when the round record cannot be read", () => {
    // The state this feature will actually ship into: the trustee role's new
    // prvReadrev_roundfinance grant may have reached one environment and not another. A
    // finance read failure must not take FR-058..FR-062 down with it.
    const view = deriveLandingView(
      { phase: "error", errorMessage: "Privilege check failed." },
      loadedStats,
    );
    expect(view.statistics.kind).toBe("figures");
    expect(view.finance.kind).toBe("diagnostic");
    if (view.finance.kind !== "diagnostic") throw new Error("expected a diagnostic");
    expect(view.finance.message.explanation).toContain("Privilege check failed.");
    // With no finance row, the round name still comes from the flow's own response.
    expect(view.roundName).toBe(OPEN_ROUND_KEY);
  });

  it("keeps the round record when the flow call fails", () => {
    const view = deriveLandingView(loadedRound, {
      phase: "error",
      errorMessage: "The flow is turned off.",
    });
    expect(view.finance.kind).toBe("figures");
    expect(view.statistics.kind).toBe("diagnostic");
    if (view.statistics.kind !== "diagnostic") throw new Error("expected a diagnostic");
    expect(view.statistics.message.heading).toBe("Round figures are unavailable");
    expect(view.statistics.message.explanation).toContain("The flow is turned off.");
  });

  it("says every diagnostic leaves the applications list reachable", () => {
    // A trustee told "no figures" must not conclude the portal is down.
    const inputs: [OpenRoundInput, StatisticsInput][] = [
      [{ phase: "error", errorMessage: "x" }, loadedStats],
      [{ phase: "loaded", result: { kind: "none" } }, loadedStats],
      [{ phase: "loaded", result: { kind: "ambiguous", count: 3 } }, loadedStats],
      [loadedRound, { phase: "error", errorMessage: "x" }],
      [
        loadedRound,
        { phase: "loaded", response: makeRoundStatistics({ status: "truncated" }) },
      ],
    ];
    for (const [round, statistics] of inputs) {
      const view = deriveLandingView(round, statistics);
      const message =
        view.finance.kind === "diagnostic"
          ? view.finance.message
          : view.statistics.kind === "diagnostic"
            ? view.statistics.message
            : null;
      expect(message?.explanation).toContain("applications list is unaffected");
    }
  });
});

describe("deriveLandingView — the round count is the answer (FR-057, TAD §5.4 step 1)", () => {
  it("says no round is open for zero rows", () => {
    const view = deriveLandingView({ phase: "loaded", result: { kind: "none" } }, loadedStats);
    if (view.finance.kind !== "diagnostic") throw new Error("expected a diagnostic");
    expect(view.finance.message.heading).toBe("No round is open");
  });

  it("says the round is ambiguous for two rows, and names the count", () => {
    // TAD §5.4: "2 rows means the screen says the round is ambiguous and links to the
    // list, rather than picking one." Picking one would produce a screen that looks
    // completely normal and is about a round the trustee did not ask for.
    const view = deriveLandingView(
      { phase: "loaded", result: { kind: "ambiguous", count: 2 } },
      loadedStats,
    );
    if (view.finance.kind !== "diagnostic") throw new Error("expected a diagnostic");
    expect(view.finance.message.heading).toBe("More than one round is open");
    expect(view.finance.message.explanation).toContain("2 grant rounds");
  });

  it("reports a loaded phase with nothing loaded as a diagnostic rather than crashing", () => {
    const view = deriveLandingView({ phase: "loaded" }, { phase: "loaded" });
    expect(view.finance.kind).toBe("diagnostic");
    expect(view.statistics.kind).toBe("diagnostic");
  });
});

describe("deriveLandingView — status is the flow's verdict (TAD §3.3 point 4)", () => {
  it("shows no figures for any non-ok status", () => {
    for (const status of ["no-open-round", "ambiguous-round", "truncated", "threshold-unset"]) {
      const view = deriveLandingView(loadedRound, {
        phase: "loaded",
        response: makeRoundStatistics({ status }),
      });
      expect(view.statistics.kind).toBe("diagnostic");
    }
  });

  it("shows no figures for a status this build has never seen", () => {
    // The flow's failure path is being extended in a separate change. Whatever status it
    // introduces, "no figures at all" is already the answer.
    const view = deriveLandingView(loadedRound, {
      phase: "loaded",
      response: makeRoundStatistics({ status: "some-new-failure-mode" }),
    });
    if (view.statistics.kind !== "diagnostic") throw new Error("expected a diagnostic");
    expect(view.statistics.message.heading).toBe("Round figures are unavailable");
    // Quoted verbatim, so it is diagnosable rather than mysterious.
    expect(view.statistics.message.explanation).toContain("some-new-failure-mode");
  });

  it("shows figures for ok even when the response carries figures under a non-ok status", () => {
    // Guards the direction that would be a real disclosure of wrong information: a
    // truncated response that still carried a full metrics object must render none of it.
    const view = deriveLandingView(loadedRound, {
      phase: "loaded",
      response: makeRoundStatistics({ status: "truncated" }),
    });
    expect(view.statistics.kind).toBe("diagnostic");
  });

  it("gives each named status its own wording", () => {
    const headings = [
      "no-open-round",
      "ambiguous-round",
      "truncated",
      "threshold-unset",
    ].map((status) => describeStatisticsStatus(status).heading);
    expect(headings).toEqual([
      "No round is open",
      "More than one round is open",
      "Too many applications to summarise",
      "Round figures are unavailable",
    ]);
    // The two that share a heading do not share an explanation.
    expect(describeStatisticsStatus("threshold-unset").explanation).not.toBe(
      describeStatisticsStatus("anything-else").explanation,
    );
  });
});

describe("deriveLandingView — reconciliation (TAD §5.4 step 3)", () => {
  it("shows neither half when the two round keys disagree", () => {
    // The failure this exists for: FR-063's financial position for one round beside
    // FR-058..FR-062's application figures for another. Each half is internally
    // consistent, so nothing on the screen would look wrong.
    const view = deriveLandingView(loadedRound, {
      phase: "loaded",
      response: makeRoundStatistics({ roundKey: "2026-Q3" }),
    });
    expect(view.finance.kind).toBe("diagnostic");
    expect(view.statistics.kind).toBe("diagnostic");
    if (view.statistics.kind !== "diagnostic") throw new Error("expected a diagnostic");
    expect(view.statistics.message.heading).toMatch(/round changed/i);
    expect(view.roundName).toBeNull();
  });

  it("treats a null round key on either side as a mismatch, not as a pass", () => {
    // "We could not check" must never render as "we checked and it agreed".
    const noResponseKey = deriveLandingView(loadedRound, {
      phase: "loaded",
      response: makeRoundStatistics({ roundKey: null }),
    });
    expect(noResponseKey.statistics.kind).toBe("diagnostic");

    const noRowKey = deriveLandingView(
      {
        phase: "loaded",
        result: { kind: "one", round: makeRoundFinance({ roundKey: null }) },
      },
      loadedStats,
    );
    expect(noRowKey.finance.kind).toBe("diagnostic");
  });

  it("does not reconcile when only one half has figures", () => {
    // Nothing can be mixed if only one thing is on screen, so a finance-only screen is
    // not blocked by the flow's round key being unavailable.
    const view = deriveLandingView(loadedRound, { phase: "error", errorMessage: "down" });
    expect(view.finance.kind).toBe("figures");
  });
});

describe("buildSeries — one array for the table and the chart (ADR-029)", () => {
  const distribution: Distribution = {
    population: 434,
    categories: [
      { value: 1, count: 260, percentage: 59.9 },
      { value: 2, count: 150, percentage: 34.6 },
    ],
  };

  it("labels each category through this app's own map, keeping the source integer", () => {
    const series = buildSeries(distribution, APPLICANT_GENDER_LABELS);
    expect(series?.rows).toEqual([
      { value: 1, label: "Female", count: 260, percentage: 59.9 },
      { value: 2, label: "Male", count: 150, percentage: 34.6 },
    ]);
  });

  it("renders an unmapped option value as Unknown (n) rather than as blank text", () => {
    // Solution import RELABELS matching option values but does not delete values the new
    // source omits (IMP-0019), so the live set can be a superset of the transcribed map.
    // That must be visible, not silent.
    const series = buildSeries(
      { population: 10, categories: [{ value: 99, count: 10, percentage: 100 }] },
      AGE_RANGE_LABELS,
    );
    expect(series?.rows[0]?.label).toBe("Unknown (99)");
  });

  it("carries the denominator through, so the page can show it beside the percentages", () => {
    expect(buildSeries(distribution, APPLICANT_GENDER_LABELS)?.population).toBe(434);
    expect(
      buildSeries(
        { population: null, categories: [{ value: 1, count: 1, percentage: null }] },
        APPLICANT_GENDER_LABELS,
      )?.population,
    ).toBeNull();
  });

  it("returns null for an absent or empty distribution, so no section is rendered", () => {
    expect(buildSeries(null, APPLICANT_GENDER_LABELS)).toBeNull();
    expect(buildSeries({ population: 434, categories: [] }, APPLICANT_GENDER_LABELS)).toBeNull();
  });

  it("scales the bars against the largest count, and never divides by zero", () => {
    expect(buildSeries(distribution, APPLICANT_GENDER_LABELS)?.maxCount).toBe(260);
    const allZero = buildSeries(
      {
        population: 0,
        categories: [
          { value: 1, count: 0, percentage: 0 },
          { value: 2, count: 0, percentage: 0 },
        ],
      },
      APPLICANT_GENDER_LABELS,
    );
    expect(allZero?.maxCount).toBe(1);
  });

  it("preserves no benchmark, second series or comparison of any kind", () => {
    // FR-061's benchmark clause is withdrawn (TAD §0.1 item 4, ADR-029 amended). A series
    // row has exactly four fields and none of them is a comparison.
    const row = buildSeries(distribution, APPLICANT_GENDER_LABELS)?.rows[0];
    expect(Object.keys(row ?? {}).sort()).toEqual(["count", "label", "percentage", "value"]);
  });
});

describe("chartSummary — the aria-label on an SVG", () => {
  it("names the chart, its size and its largest category, and points at the table", () => {
    const series = buildSeries(
      {
        population: 434,
        categories: [
          { value: 1, count: 260, percentage: 59.9 },
          { value: 2, count: 150, percentage: 34.6 },
        ],
      },
      APPLICANT_GENDER_LABELS,
    );
    if (series === null) throw new Error("expected a series");
    const summary = chartSummary("Gender", series);
    expect(summary).toContain("Gender");
    expect(summary).toContain("2 categories");
    expect(summary).toContain("Female, 260");
    expect(summary).toContain("out of 434 applications");
    // The table is the accessible content; this label's job is to say so, not to recite
    // thirteen rows (ADR-029).
    expect(summary).toContain("table beside this chart");
  });

  it("omits the denominator when the response did not carry one", () => {
    const series = buildSeries(
      { population: null, categories: [{ value: 1, count: 3, percentage: null }] },
      APPLICANT_GENDER_LABELS,
    );
    if (series === null) throw new Error("expected a series");
    expect(chartSummary("Gender", series)).not.toContain("out of");
  });
});
