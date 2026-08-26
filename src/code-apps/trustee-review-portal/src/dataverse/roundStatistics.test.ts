/**
 * The statistics contract — TAD §3.3.
 *
 * What this proves: that every field of the response contract is typed and parsed, that a
 * missing or malformed metric becomes an ABSENCE rather than a zero, and that a response
 * with no status is refused rather than rendered.
 *
 * What it does NOT prove: that the flow returns any of this. The flow is not live in any
 * environment and `pa app add flow` has never run, so the invocation shape is an open
 * assumption (A-LAND-2) and no test here asserts it — asserting a guess is how a guess
 * becomes permanent (`IMP-0111`). The tests below inject a fake service and exercise the
 * parse, which is the half that IS fully specified.
 */
import { describe, expect, it, vi } from "vitest";
import {
  extractResponseText,
  fetchRoundStatistics,
  isKnownStatus,
  missingFlowService,
  parseRoundStatisticsResponse,
  RoundStatisticsError,
} from "./roundStatistics";

/** A minimal `ok` document. Every test below starts from this and changes one thing. */
function document(overrides: Record<string, unknown> = {}): string {
  return JSON.stringify({
    status: "ok",
    roundKey: "2026-Q4",
    computedOn: "2026-08-25T13:05:11Z",
    populationReceived: 434,
    metrics: { applicationsReceived: { count: 434 } },
    ...overrides,
  });
}

describe("parseRoundStatisticsResponse — the envelope", () => {
  it("reads every top-level field of the TAD §3.3 contract", () => {
    const response = parseRoundStatisticsResponse(document());
    expect(response.status).toBe("ok");
    expect(response.roundKey).toBe("2026-Q4");
    expect(response.computedOn).toBe("2026-08-25T13:05:11Z");
    expect(response.populationReceived).toBe(434);
    expect(response.metrics.applicationsReceived).toEqual({ count: 434 });
  });

  it("refuses a document with no status rather than guessing whether figures are safe", () => {
    // `status` is the flow's own verdict on that question. Without it there is no safe
    // default: rendering the figures assumes ok, and hiding them assumes a failure.
    expect(() => parseRoundStatisticsResponse(document({ status: undefined }))).toThrow(
      RoundStatisticsError,
    );
    expect(() => parseRoundStatisticsResponse(document({ status: "" }))).toThrow(
      /no status/i,
    );
  });

  it("keeps an unrecognised status verbatim instead of normalising it away", () => {
    // The flow is a separately-deployed artefact. A failure path added to it after this
    // build shipped can introduce a status nobody here has seen, and the screen must be
    // able to quote it.
    const response = parseRoundStatisticsResponse(document({ status: "flow-failed" }));
    expect(response.status).toBe("flow-failed");
    expect(isKnownStatus(response.status)).toBe(false);
  });

  it("recognises exactly the five statuses the contract names", () => {
    for (const status of [
      "ok",
      "no-open-round",
      "ambiguous-round",
      "truncated",
      "threshold-unset",
    ]) {
      expect(isKnownStatus(status)).toBe(true);
    }
    expect(isKnownStatus("OK")).toBe(false);
    expect(isKnownStatus("")).toBe(false);
  });

  it("throws a readable error for a body that is not JSON, and for JSON that is not a document", () => {
    expect(() => parseRoundStatisticsResponse("not json at all")).toThrow(/could not read/i);
    expect(() => parseRoundStatisticsResponse("[1,2,3]")).toThrow(/not a document/i);
    expect(() => parseRoundStatisticsResponse("42")).toThrow(/not a document/i);
  });

  it("reports every metric as null when the document carries no metrics object", () => {
    const metrics = parseRoundStatisticsResponse(document({ metrics: undefined })).metrics;
    expect(Object.values(metrics).every((metric) => metric === null)).toBe(true);
  });
});

describe("parseRoundStatisticsResponse — a null is an absence, never a zero", () => {
  it("reports an explicitly null metric as null", () => {
    // TAD §3.3 point 3, and the state the flow's FIRST version is actually in for every
    // metric but one.
    const metrics = parseRoundStatisticsResponse(
      document({
        metrics: {
          applicationsReceived: { count: 434 },
          applicationsPerDay: null,
          genderDistribution: null,
          breakTypeProfile: null,
        },
      }),
    ).metrics;
    expect(metrics.applicationsPerDay).toBeNull();
    expect(metrics.genderDistribution).toBeNull();
    expect(metrics.breakTypeProfile).toBeNull();
    expect(metrics.applicationsReceived).toEqual({ count: 434 });
  });

  it("reports a distribution with an empty category array as absent, not as an empty table", () => {
    // TAD §3.3's own example shows `"categories": [ ]`. A heading over an empty table
    // reads as "we counted and found none", which for a metric nobody computed is false.
    const metrics = parseRoundStatisticsResponse(
      document({ metrics: { genderDistribution: { population: 434, categories: [] } } }),
    ).metrics;
    expect(metrics.genderDistribution).toBeNull();
  });

  it("drops a category with no option-set value or no count rather than rendering a zero", () => {
    const distribution = parseRoundStatisticsResponse(
      document({
        metrics: {
          ageRangeDistribution: {
            population: 10,
            categories: [
              { value: 5, count: 4, percentage: 40 },
              { count: 6 }, // no value: cannot be labelled
              { value: 6 }, // no count: is not a count
              "nonsense",
            ],
          },
        },
      }),
    ).metrics.ageRangeDistribution;
    expect(distribution?.categories).toEqual([{ value: 5, count: 4, percentage: 40 }]);
  });

  it("keeps a category percentage as null when the response omitted it, and never derives one", () => {
    const distribution = parseRoundStatisticsResponse(
      document({
        metrics: {
          ageRangeDistribution: { population: 10, categories: [{ value: 5, count: 4 }] },
        },
      }),
    ).metrics.ageRangeDistribution;
    // 4 of 10 is plainly 40%. Computing it here would put a second, independently-derived
    // percentage on a screen whose whole claim is that every figure came from one pass over
    // one population.
    expect(distribution?.categories[0]?.percentage).toBeNull();
  });

  it("reports a distribution's missing population as null rather than inventing a denominator", () => {
    const distribution = parseRoundStatisticsResponse(
      document({
        metrics: { ageRangeDistribution: { categories: [{ value: 5, count: 4 }] } },
      }),
    ).metrics.ageRangeDistribution;
    expect(distribution?.population).toBeNull();
  });

  it("reports applicationsPerDay as absent when it carries no value", () => {
    const metrics = parseRoundStatisticsResponse(
      document({ metrics: { applicationsPerDay: { openedOn: "2026-08-01", days: 30 } } }),
    ).metrics;
    expect(metrics.applicationsPerDay).toBeNull();
  });

  it("keeps applicationsPerDay's own openedOn and days when they arrive", () => {
    const perDay = parseRoundStatisticsResponse(
      document({
        metrics: { applicationsPerDay: { value: 14.47, openedOn: "2026-08-01", days: 30 } },
      }),
    ).metrics.applicationsPerDay;
    expect(perDay).toEqual({ value: 14.47, openedOn: "2026-08-01", days: 30 });
  });
});

describe("parseRoundStatisticsResponse — FR-059, FR-060, FR-062", () => {
  it("parses the exceptional-funding summary and reports its optional halves as null", () => {
    const summary = parseRoundStatisticsResponse(
      document({ metrics: { exceptionalFundingSummary: { population: 434, anyCount: 41 } } }),
    ).metrics.exceptionalFundingSummary;
    expect(summary).toEqual({
      population: 434,
      anyCount: 41,
      anyPercentage: null,
      averageAmountRequested: null,
    });
  });

  it("reports the exceptional-funding summary as absent with no anyCount", () => {
    const summary = parseRoundStatisticsResponse(
      document({ metrics: { exceptionalFundingSummary: { population: 434 } } }),
    ).metrics.exceptionalFundingSummary;
    expect(summary).toBeNull();
  });

  it("parses the break-type profile, including its total row", () => {
    const profile = parseRoundStatisticsResponse(
      document({
        metrics: {
          breakTypeProfile: {
            population: 434,
            rows: [
              {
                value: 1,
                count: 300,
                averageCost: 1500,
                averageAmountRequested: 1100,
                percentageOfCost: 73.3,
              },
            ],
            total: { count: 434, averageCost: 1160 },
          },
        },
      }),
    ).metrics.breakTypeProfile;
    expect(profile?.rows).toHaveLength(1);
    expect(profile?.total).toEqual({
      count: 434,
      averageCost: 1160,
      averageAmountRequested: null,
      percentageOfCost: null,
    });
  });

  it("reports the TAD's own empty total object as no total row at all (A-LAND-4)", () => {
    // TAD §3.3 shows `"total": { }`. Four blank cells under a table look like a rendering
    // fault, not like a total.
    const profile = parseRoundStatisticsResponse(
      document({
        metrics: {
          breakTypeProfile: { population: 434, rows: [{ value: 1, count: 300 }], total: {} },
        },
      }),
    ).metrics.breakTypeProfile;
    expect(profile?.total).toBeNull();
  });

  it("reports the break-type profile as absent when it has no usable row", () => {
    const profile = parseRoundStatisticsResponse(
      document({ metrics: { breakTypeProfile: { population: 434, rows: [] } } }),
    ).metrics.breakTypeProfile;
    expect(profile).toBeNull();
  });

  it("parses the wellbeing questions and keeps each question's own denominator", () => {
    const wellbeing = parseRoundStatisticsResponse(
      document({
        metrics: {
          wellbeingLastYear: {
            questions: [
              {
                column: "rev_wellbeinganswer8",
                population: 400,
                categories: [{ value: 4, count: 300, percentage: 75 }],
              },
              { column: "rev_wellbeinganswer9", population: 380, categories: [] },
            ],
          },
        },
      }),
    ).metrics.wellbeingLastYear;
    // The second question has no usable category, so it is dropped rather than rendered as
    // an empty chart.
    expect(wellbeing?.questions).toHaveLength(1);
    expect(wellbeing?.questions[0]?.population).toBe(400);
  });

  it("reports a proportion as absent unless it carries a percentage or both halves", () => {
    const metrics = parseRoundStatisticsResponse(
      document({
        metrics: {
          highHoursCareProportion: { percentage: 22.5 },
          lowLifeSatisfactionProportion: { count: 90, population: 400 },
          unableToTakeBreakProportion: { count: 90 },
        },
      }),
    ).metrics;
    expect(metrics.highHoursCareProportion?.percentage).toBe(22.5);
    expect(metrics.lowLifeSatisfactionProportion?.count).toBe(90);
    // A numerator with no denominator is not a proportion.
    expect(metrics.unableToTakeBreakProportion).toBeNull();
  });
});

describe("ethnicGroupDistribution", () => {
  it("is null even when the response carries a value for it (A-R24)", () => {
    // FR-061's ethnicity half has no data source and never has. If the flow ever emitted
    // one it would be a defect in the flow, and this app must not become the first thing to
    // render an Article 9 category the charity has not decided to collect.
    const metrics = parseRoundStatisticsResponse(
      document({
        metrics: {
          ethnicGroupDistribution: {
            population: 434,
            categories: [{ value: 1, count: 100, percentage: 23 }],
          },
        },
      }),
    ).metrics;
    expect(metrics.ethnicGroupDistribution).toBeNull();
  });
});

describe("extractResponseText", () => {
  it("accepts the document as a bare string", () => {
    expect(extractResponseText('{"status":"ok"}')).toBe('{"status":"ok"}');
  });

  it("unwraps an IOperationResult around either accepted shape", () => {
    expect(extractResponseText({ success: true, data: '{"status":"ok"}' })).toContain("ok");
    expect(
      extractResponseText({ success: true, data: { statistics: '{"status":"ok"}' } }),
    ).toContain("ok");
  });

  it("accepts the single text output under whatever name the flow gave it", () => {
    // The output NAME is chosen in the flow designer and is not knowable from here, so the
    // count is what is relied on: TAD §3.3 chose one text output carrying one document.
    expect(extractResponseText({ anyNameAtAll: '{"status":"ok"}' })).toContain("ok");
  });

  it("fails loudly when there is not exactly one text output", () => {
    expect(() => extractResponseText({ a: "one", b: "two" })).toThrow(/2 text outputs/);
    expect(() => extractResponseText({})).toThrow(/0 text outputs/);
  });

  it("reports a failed IOperationResult with the connector's own reason", () => {
    expect(() =>
      extractResponseText({ success: false, error: { message: "Flow is turned off." } }),
    ).toThrow("Flow is turned off.");
  });

  it("reports a failed IOperationResult that gave no reason", () => {
    expect(() => extractResponseText({ success: false })).toThrow(/gave no reason/);
  });

  it("rejects an empty body and a non-object payload", () => {
    expect(() => extractResponseText("   ")).toThrow(/empty response body/);
    expect(() => extractResponseText(null)).toThrow(/no readable response body/);
    expect(() => extractResponseText(7)).toThrow(/no readable response body/);
  });
});

describe("fetchRoundStatistics", () => {
  it("invokes the service and parses what it returns", async () => {
    let calls = 0;
    const response = await fetchRoundStatistics({
      Run: () => {
        calls += 1;
        return Promise.resolve({ success: true, data: { statistics: document() } });
      },
    });
    expect(calls).toBe(1);
    expect(response.status).toBe("ok");
    expect(response.metrics.applicationsReceived?.count).toBe(434);
  });

  it("passes a non-ok status through as a successful result, not as a failure", async () => {
    // The screen decides what a non-ok status means. Throwing here would collapse four
    // distinct diagnostic states into one error message.
    const response = await fetchRoundStatistics({
      Run: () => Promise.resolve(document({ status: "truncated" })),
    });
    expect(response.status).toBe("truncated");
  });

  it("turns a thrown error into a RoundStatisticsError carrying its message", async () => {
    await expect(
      fetchRoundStatistics({ Run: () => Promise.reject(new Error("Timed out.")) }),
    ).rejects.toMatchObject({ name: "RoundStatisticsError", message: "Timed out." });
  });

  it("turns a thrown non-Error into a RoundStatisticsError with a readable message", async () => {
    // The shape that would otherwise reach a trustee as an empty diagnostic panel. Built
    // with `mockRejectedValue` rather than a bare `Promise.reject("…")`, which is the same
    // way `client.test.ts` produces this fixture: a non-Error rejection is exactly what
    // `prefer-promise-reject-errors` exists to stop being WRITTEN, and suppressing the rule
    // to test surviving one would read as an exemption rather than as a fixture.
    const Run = vi.fn().mockRejectedValue("just a string") as () => Promise<unknown>;
    await expect(fetchRoundStatistics({ Run })).rejects.toThrow(/could not be reached/);
  });

  it("defaults to the missing-flow service, which says so rather than pretending", async () => {
    // A-LAND-2. Until `pa app add flow` runs there is no generated service to call, and
    // this is the message whoever wires it up will read.
    await expect(fetchRoundStatistics()).rejects.toThrow(/pa app add flow/);
    await expect(missingFlowService.Run()).rejects.toBeInstanceOf(RoundStatisticsError);
  });
});
