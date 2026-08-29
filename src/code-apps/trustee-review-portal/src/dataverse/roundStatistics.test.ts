/**
 * The statistics contract — TAD §3.3 — plus the age-bound read-then-maybe-trigger cycle over
 * the SPLIT request/result pair (ADR-038, TAD §5.3.1; previously IMP-0359, IMP-0365).
 *
 * What `parseRoundStatisticsResponse` and its helpers prove: that every field of the
 * response contract is typed and parsed, that a missing or malformed metric becomes an
 * ABSENCE rather than a zero, and that a response with no status is refused rather than
 * rendered. This half has no platform contract — it is a pure function over a string.
 *
 * What `fetchRoundStatistics` proves, with `./client` mocked:
 *
 *   - it READS `rev_roundstatisticsresult` through the typed per-table path, and WRITES
 *     `rev_triggeredon` on `rev_roundstatisticsrequest` through the generic connector — two
 *     tables, two paths, never one (TAD §5.4's Revision 5 note). It does not re-implement
 *     either transport; `client.test.ts` owns proving `updateRecord` itself is correct;
 *   - **freshness is an AGE and not a request identity.** The seven cases below are the ones
 *     that actually bite: `computedOn` null · older than `S` · inside `S` · `S` null · `S`
 *     present but the document unparseable · a poll satisfied by ANOTHER session's
 *     computation · a timeout returning `pending` rather than the stale document;
 *   - a mount inside the window writes NOTHING and triggers NOTHING (§5.3.1 step 1), which
 *     is asserted as `updateRecord` never being called — the observable form of "no flow run,
 *     no privileged read".
 *
 * Uses fake timers throughout so the poll loop's real-world ~12s bound costs nothing in test
 * time, and `vi.setSystemTime` so an "age" is a fact of the test rather than of the clock.
 */
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const listRecords = vi.fn();
const updateRecord = vi.fn();

vi.mock("./client", () => ({
  listRecords: (...args: unknown[]) => listRecords(...args) as unknown,
  updateRecord: (...args: unknown[]) => updateRecord(...args) as unknown,
}));

const {
  fetchRoundStatistics,
  isKnownStatus,
  parseRoundStatisticsResponse,
  RoundStatisticsError,
} = await import("./roundStatistics");

const REQUEST_ID = "dddddddd-dddd-4ddd-8ddd-dddddddddddd";
const RESULT_ID = "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee";

/** The wall-clock instant every age below is measured against. */
const NOW = "2026-08-28T12:00:00.000Z";

/** A `rev_roundstatisticsrequest` row — the ASK. Only its id is ever selected now. */
function requestRow(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return { rev_roundstatisticsrequestid: REQUEST_ID, ...overrides };
}

/** A `rev_roundstatisticsresult` row — the ANSWER, as `listRecords` would return it. */
function resultRow(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    rev_roundstatisticsresultid: RESULT_ID,
    rev_status: 2,
    rev_resultjson: null,
    rev_computedon: null,
    ...overrides,
  };
}

beforeEach(() => {
  listRecords.mockReset();
  updateRecord.mockReset();
  vi.useFakeTimers();
  vi.setSystemTime(new Date(NOW));
});

afterEach(() => {
  vi.useRealTimers();
});

/** A minimal `ok` document. Every test below starts from this and changes one thing. */
function document(overrides: Record<string, unknown> = {}): string {
  return JSON.stringify({
    status: "ok",
    roundKey: "2026-Q4",
    computedOn: "2026-08-25T13:05:11Z",
    staleAfterSeconds: null,
    populationReceived: 434,
    metrics: { applicationsReceived: { count: 434 } },
    ...overrides,
  });
}

/**
 * Routes `listRecords` by the entity set the call names, rather than by call ORDER.
 *
 * Order-based mocking was viable when one table served both halves; it is actively
 * misleading now that the cycle reads one table and writes another, because "the second
 * call" is a different table depending on whether the mount hit the freshness window. Every
 * test below states what each TABLE returns and lets the code decide how often it asks.
 */
function routeReads(options: {
  result: Record<string, unknown> | null;
  request?: Record<string, unknown> | null;
}): void {
  listRecords.mockImplementation((request: { entityName: string }) => {
    if (request.entityName === "rev_roundstatisticsresults") {
      return Promise.resolve({
        rows: options.result === null ? [] : [options.result],
        truncated: false,
      });
    }
    const ask = options.request === undefined ? requestRow() : options.request;
    return Promise.resolve({ rows: ask === null ? [] : [ask], truncated: false });
  });
}

/** An ISO stamp `seconds` before `NOW`. */
function secondsAgo(seconds: number): string {
  return new Date(Date.parse(NOW) - seconds * 1000).toISOString();
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
                // ADR-039 (Revision 6) — `{ value, population }`, never a bare number.
                averageCost: { value: 1500, population: 298 },
                averageAmountRequested: { value: 1100, population: 295 },
                percentageOfCost: { value: 73.3, population: 293 },
              },
            ],
            total: { count: 434, averageCost: { value: 1160, population: 428 } },
          },
        },
      }),
    ).metrics.breakTypeProfile;
    expect(profile?.rows).toEqual([
      {
        value: 1,
        count: 300,
        averageCost: { value: 1500, population: 298 },
        averageAmountRequested: { value: 1100, population: 295 },
        percentageOfCost: { value: 73.3, population: 293 },
      },
    ]);
    expect(profile?.total).toEqual({
      count: 434,
      averageCost: { value: 1160, population: 428 },
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

describe("parseRoundStatisticsResponse — the ADR-039 money measures, {value, population} (Revision 6)", () => {
  it("parses a well-formed money measure as {value, population}", () => {
    const summary = parseRoundStatisticsResponse(
      document({
        metrics: {
          exceptionalFundingSummary: {
            population: 434,
            anyCount: 41,
            averageAmountRequested: { value: 780, population: 39 },
          },
        },
      }),
    ).metrics.exceptionalFundingSummary;
    expect(summary?.averageAmountRequested).toEqual({ value: 780, population: 39 });
  });

  it("REJECTS a bare number rather than coercing it into a MoneyMeasure", () => {
    // Before ADR-039 (Revision 6) every one of these four fields was a plain `number | null`.
    // A flow still on that shape — or any document this build has not anticipated — must not
    // have its bare number silently reinterpreted as `{ value, population: null }`: that
    // would put a mean on screen with NO denominator beside it, which is exactly what TAD
    // §3.3 property 8 exists to forbid, and it is a worse failure than showing nothing at
    // all because it looks correct. Dropped, the same as any other malformed metric.
    const summary = parseRoundStatisticsResponse(
      document({
        metrics: {
          exceptionalFundingSummary: { population: 434, anyCount: 41, averageAmountRequested: 780 },
        },
      }),
    ).metrics.exceptionalFundingSummary;
    expect(summary?.averageAmountRequested).toBeNull();
  });

  it("drops a measure whose population failed to parse, rather than rendering a value with no denominator", () => {
    const summary = parseRoundStatisticsResponse(
      document({
        metrics: {
          exceptionalFundingSummary: {
            population: 434,
            anyCount: 41,
            averageAmountRequested: { value: 780 },
          },
        },
      }),
    ).metrics.exceptionalFundingSummary;
    expect(summary?.averageAmountRequested).toBeNull();
  });

  it("renders a below-threshold break-type row as count-present, money-absent (TAD §3.3's own example)", () => {
    // The literal shape TAD §3.3 shows for a break type below k: the count still arrives,
    // all three money measures are null. Not an error, and not rendered as one.
    const profile = parseRoundStatisticsResponse(
      document({
        metrics: {
          breakTypeProfile: {
            population: 434,
            rows: [
              {
                value: 4,
                count: 3,
                averageCost: null,
                averageAmountRequested: null,
                percentageOfCost: null,
              },
            ],
          },
        },
      }),
    ).metrics.breakTypeProfile;
    expect(profile?.rows).toEqual([
      {
        value: 4,
        count: 3,
        averageCost: null,
        averageAmountRequested: null,
        percentageOfCost: null,
      },
    ]);
  });

  it("rejects a bare-number money measure on a break-type row the same way", () => {
    const profile = parseRoundStatisticsResponse(
      document({
        metrics: {
          breakTypeProfile: {
            population: 434,
            rows: [{ value: 1, count: 300, averageCost: 1500 }],
          },
        },
      }),
    ).metrics.breakTypeProfile;
    expect(profile?.rows[0]?.averageCost).toBeNull();
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

describe("parseRoundStatisticsResponse — staleAfterSeconds (ADR-038, TAD §3.3 property 7)", () => {
  it("reads the bound as a number when the flow supplied one", () => {
    expect(parseRoundStatisticsResponse(document({ staleAfterSeconds: 120 }))
      .staleAfterSeconds).toBe(120);
  });

  it("reports an absent bound as null — the shipping default, and 'always recompute'", () => {
    // No `RoundStatisticsStaleAfterSeconds` rev_setting row exists (2026-08-28); OQ-042 is
    // open and its own stated default is to leave it unseeded. Nothing here may substitute a
    // number: treating an unbounded age as fresh would put a figure of unknown age in front
    // of a board (TAD §3.3 property 7).
    expect(parseRoundStatisticsResponse(document({ staleAfterSeconds: undefined }))
      .staleAfterSeconds).toBeNull();
    expect(parseRoundStatisticsResponse(document({ staleAfterSeconds: null }))
      .staleAfterSeconds).toBeNull();
    expect(parseRoundStatisticsResponse(document({ staleAfterSeconds: "soon" }))
      .staleAfterSeconds).toBeNull();
  });

  it("sits beside metrics and never inside it", () => {
    // ADR-038 is explicit that §3.3's `metrics` object gains no key and loses none. A bound
    // that drifted into `metrics` would be rendered as a figure by the screen's own
    // "render every metric that arrived" loop.
    const response = parseRoundStatisticsResponse(document({ staleAfterSeconds: 120 }));
    expect(response.staleAfterSeconds).toBe(120);
    expect(Object.keys(response.metrics)).not.toContain("staleAfterSeconds");
  });

  it("gives the synthetic pending document a null bound like every other absence", () => {
    // `fetchRoundStatistics` builds `{"status":"pending"}` and routes it through this
    // function precisely so it inherits the contract's shape for free — adding
    // `staleAfterSeconds` in Revision 5 needed no edit to that call site.
    const pending = parseRoundStatisticsResponse(JSON.stringify({ status: "pending" }));
    expect(pending.staleAfterSeconds).toBeNull();
    expect(pending.computedOn).toBeNull();
  });
});

describe("fetchRoundStatistics — freshness is an age bound (TAD §5.3.1, ADR-038)", () => {
  /** Advances past every remaining poll, driving the loop's own `await sleep(...)` calls. */
  async function runAllPolls(): Promise<void> {
    // MAX_POLLS x POLL_INTERVAL_MS in roundStatistics.ts (6 x 2000ms) — advanced in one
    // jump rather than per-poll, since every test either resolves on an EARLIER poll (the
    // extra time never gets consumed) or is deliberately testing the timeout itself.
    await vi.advanceTimersByTimeAsync(6 * 2000);
  }

  /** How many times the RESULT table was read, ignoring reads of the request table. */
  function resultReads(): number {
    return (listRecords.mock.calls as [{ entityName: string }][]).filter(
      ([request]) => request.entityName === "rev_roundstatisticsresults",
    ).length;
  }

  // ── The two tables and the two transports ──────────────────────────────────────────

  it("reads the RESULT row by its fixed key, with only the four allow-listed columns", async () => {
    routeReads({ result: resultRow() });
    updateRecord.mockResolvedValue(undefined);
    const promise = fetchRoundStatistics();
    await runAllPolls();
    await promise;

    const read = (listRecords.mock.calls as [
      { entityName: string; select: readonly string[]; filter: string; top: number },
    ][])[0];
    if (read === undefined) throw new Error("listRecords was never called");
    expect(read[0].entityName).toBe("rev_roundstatisticsresults");
    expect(read[0].filter).toBe("rev_name eq 'CURRENT'");
    expect(read[0].top).toBe(1);
    expect([...read[0].select]).toEqual([
      "rev_roundstatisticsresultid",
      "rev_status",
      "rev_resultjson",
      "rev_computedon",
    ]);
  });

  it("writes rev_triggeredon on the REQUEST table through the generic-connector updateRecord", async () => {
    // The write path is not free to move. TAD §5.4's Revision 5 note: the typed per-table
    // path and the generic connector live under different keys in `dataSourcesInfo.ts`, one
    // can work while the other is broken, and `UpdateOnlyRecordWithOrganization` is the only
    // one of the two with live evidence behind it (Save Verdict).
    routeReads({ result: resultRow() });
    updateRecord.mockResolvedValue(undefined);
    const promise = fetchRoundStatistics();
    await runAllPolls();
    await promise;

    expect(updateRecord).toHaveBeenCalledTimes(1);
    const call = (updateRecord.mock.calls as [
      { entityName: string; recordId: string; item: Record<string, unknown> },
    ][])[0];
    if (call === undefined) throw new Error("updateRecord was never called");
    expect(call[0].entityName).toBe("rev_roundstatisticsrequests");
    expect(call[0].recordId).toBe(REQUEST_ID);
    expect(typeof call[0].item.rev_triggeredon).toBe("string");
    // The ask carries nothing else. TAD §6.3.1 row 2: no caller-supplied value reaches a
    // query, and `rev_triggeredon` exists only as a change for the row trigger to fire on.
    expect(Object.keys(call[0].item)).toEqual(["rev_triggeredon"]);
  });

  it("selects only the id from the request table, never the three superseded columns", async () => {
    // TAD §3.9.2: `rev_status`, `rev_resultjson` and `rev_computedon` are UNUSED from
    // Revision 5 and live on the RESULT table now. Still selecting them here would leave a
    // future reader one plausible edit from reading the aggregate off the table a trustee
    // can WRITE — the defect §3.9.1 exists to close.
    routeReads({ result: resultRow() });
    updateRecord.mockResolvedValue(undefined);
    const promise = fetchRoundStatistics();
    await runAllPolls();
    await promise;

    const ask = (listRecords.mock.calls as [{ entityName: string; select: readonly string[] }][])
      .find(([request]) => request.entityName === "rev_roundstatisticsrequests");
    if (ask === undefined) throw new Error("the request table was never read");
    expect([...ask[0].select]).toEqual(["rev_roundstatisticsrequestid"]);
  });

  // ── The freshness predicate: the seven cases that bite ─────────────────────────────

  it("case 1 — computedOn null: stale, so it asks (nothing has ever been computed)", async () => {
    routeReads({ result: resultRow({ rev_computedon: null }) });
    updateRecord.mockResolvedValue(undefined);
    const promise = fetchRoundStatistics();
    await runAllPolls();
    const response = await promise;

    expect(updateRecord).toHaveBeenCalledTimes(1);
    expect(response.status).toBe("pending");
  });

  it("case 1b — a parseable document WITH a bound but no computedOn stamp: still stale", async () => {
    // Found by mutation, not by reading the spec: replacing the null-`computedOn` arm of
    // `ageInSeconds` with `0` — i.e. "an unstamped document is zero seconds old", the exact
    // null-check trap TAD §5.3.1 says an age comparison cannot express — survived every
    // other test in this file. Case 1 could not catch it because that row carries no
    // document either, so the bound was already NaN and the age never got to matter.
    //
    // The state is real: `rev_resultjson` and `rev_computedon` are two columns, written by
    // one flow, and a run that sets the first and not the second is one designer mistake
    // away (a nested `item` on an update writes nothing while succeeding — TAD §12.2). A
    // document nobody stamped has an UNKNOWN age, and an unknown age is not a young one.
    routeReads({
      result: resultRow({
        rev_computedon: null,
        rev_resultjson: document({ staleAfterSeconds: 120 }),
      }),
    });
    updateRecord.mockResolvedValue(undefined);
    const promise = fetchRoundStatistics();
    await runAllPolls();
    const response = await promise;

    expect(updateRecord).toHaveBeenCalledTimes(1);
    expect(response.status).toBe("pending");
    expect(response.metrics.applicationsReceived).toBeNull();
  });

  it("case 1c — an unparseable computedOn is an unknown age, not a fresh one", async () => {
    // `Date.parse` returns NaN for anything it cannot read, and NaN fails the comparison for
    // the same reason a null does. A stamp the app cannot read is the same fact as no stamp.
    routeReads({
      result: resultRow({
        rev_computedon: "not a timestamp",
        rev_resultjson: document({ staleAfterSeconds: 120 }),
      }),
    });
    updateRecord.mockResolvedValue(undefined);
    const promise = fetchRoundStatistics();
    await runAllPolls();
    const response = await promise;

    expect(updateRecord).toHaveBeenCalledTimes(1);
    expect(response.status).toBe("pending");
  });

  it("case 2 — computedOn OLDER than S: stale, so it asks, and the old document is not shown", async () => {
    routeReads({
      result: resultRow({
        rev_computedon: secondsAgo(600),
        rev_resultjson: document({ staleAfterSeconds: 120 }),
      }),
    });
    updateRecord.mockResolvedValue(undefined);
    const promise = fetchRoundStatistics();
    await runAllPolls();
    const response = await promise;

    expect(updateRecord).toHaveBeenCalledTimes(1);
    // Ten minutes old against a two-minute bound. The figures in that document are real and
    // are still not shown.
    expect(response.status).toBe("pending");
    expect(response.metrics.applicationsReceived).toBeNull();
  });

  it("case 3 — computedOn INSIDE S: renders it, writes nothing, triggers nothing", async () => {
    // TAD §5.3.1 step 1, and the assertion that matters is the NEGATIVE one: no flow run and
    // no privileged read means no traverse of the Art. 9 columns for this mount. A mount
    // inside the window is one row read.
    routeReads({
      result: resultRow({
        rev_computedon: secondsAgo(10),
        rev_resultjson: document({ staleAfterSeconds: 120 }),
      }),
    });
    updateRecord.mockResolvedValue(undefined);

    const response = await fetchRoundStatistics();

    expect(response.status).toBe("ok");
    expect(response.metrics.applicationsReceived?.count).toBe(434);
    expect(updateRecord).not.toHaveBeenCalled();
    expect(resultReads()).toBe(1);
    expect(listRecords).toHaveBeenCalledTimes(1);
  });

  it("case 4 — S null: always recompute, even over a document one second old", async () => {
    // The SHIPPING configuration (no rev_setting row, OQ-042 open). `null` is the fail-safe
    // direction and reproduces Revision 2's behaviour exactly: every mount asks.
    routeReads({
      result: resultRow({
        rev_computedon: secondsAgo(1),
        rev_resultjson: document({ staleAfterSeconds: null }),
      }),
    });
    updateRecord.mockResolvedValue(undefined);
    const promise = fetchRoundStatistics();
    await runAllPolls();
    const response = await promise;

    expect(updateRecord).toHaveBeenCalledTimes(1);
    expect(response.status).toBe("pending");
  });

  it("case 5 — S present but the document unparseable: no bound, so stale, and no throw", async () => {
    // TAD §3.3's closing paragraph: "after a failed computation there is no parseable
    // document and therefore no bound, and the app treats the result as stale." The parse
    // failure must NOT propagate here — a first-ever mount would otherwise show an error
    // where it should show a computation being requested.
    routeReads({
      result: resultRow({ rev_computedon: secondsAgo(1), rev_resultjson: "{ not json" }),
    });
    updateRecord.mockResolvedValue(undefined);
    const promise = fetchRoundStatistics();
    await runAllPolls();
    const response = await promise;

    expect(updateRecord).toHaveBeenCalledTimes(1);
    expect(response.status).toBe("pending");
  });

  it("case 5b — a parseable document with no status is treated the same way: stale", async () => {
    // `parseRoundStatisticsResponse` refuses a document with no status, and that refusal is
    // swallowed at the freshness layer for the same reason as case 5.
    routeReads({
      result: resultRow({
        rev_computedon: secondsAgo(1),
        rev_resultjson: JSON.stringify({ roundKey: "2026-Q4", staleAfterSeconds: 120 }),
      }),
    });
    updateRecord.mockResolvedValue(undefined);
    const promise = fetchRoundStatistics();
    await runAllPolls();
    const response = await promise;

    expect(response.status).toBe("pending");
  });

  it("case 6 — a poll is satisfied by ANOTHER session's computation", async () => {
    // The sharp test, and the one a request-identity comparison FAILS. The document that
    // satisfies this poll was computed 30 seconds BEFORE the trigger this call wrote, by
    // somebody else's ask. `computedOn >= requestedAt` would reject it and keep polling to a
    // timeout; the age bound accepts it, which is exactly TAD §5.3.1 step 3's "whoever
    // caused it" and why §6.3.1 can answer the cross-request question with a design property.
    let read = 0;
    listRecords.mockImplementation((request: { entityName: string }) => {
      if (request.entityName !== "rev_roundstatisticsresults") {
        return Promise.resolve({ rows: [requestRow()], truncated: false });
      }
      read += 1;
      // Read 1 is the mount (stale, ten minutes old). From read 2 — the first poll — a
      // neighbouring session's finished computation is on the row.
      const computedOn = read === 1 ? secondsAgo(600) : secondsAgo(30);
      return Promise.resolve({
        rows: [
          resultRow({
            rev_computedon: computedOn,
            rev_resultjson: document({ staleAfterSeconds: 120, roundKey: "2026-Q4" }),
          }),
        ],
        truncated: false,
      });
    });
    updateRecord.mockResolvedValue(undefined);

    const promise = fetchRoundStatistics();
    await runAllPolls();
    const response = await promise;

    expect(response.status).toBe("ok");
    expect(response.roundKey).toBe("2026-Q4");
    // Resolved on the FIRST poll: the mount read plus one poll read, and no more.
    expect(resultReads()).toBe(2);
    expect(updateRecord).toHaveBeenCalledTimes(1);
  });

  it("case 7 — a timeout returns pending, never the stale document presented as current", async () => {
    // The document on the row is a perfectly good `ok` document with real figures in it. It
    // is 30 minutes old against a 60-second bound, and every one of the six polls sees the
    // same thing. TAD §5.3.1 step 4.
    routeReads({
      result: resultRow({
        rev_computedon: secondsAgo(1800),
        rev_resultjson: document({ staleAfterSeconds: 60, populationReceived: 434 }),
      }),
    });
    updateRecord.mockResolvedValue(undefined);
    const promise = fetchRoundStatistics();
    await runAllPolls();
    const response = await promise;

    expect(response.status).toBe("pending");
    expect(response.metrics.applicationsReceived).toBeNull();
    expect(response.populationReceived).toBeNull();
    expect(response.computedOn).toBeNull();
    // Six polls plus the mount read — the bound was actually exhausted rather than
    // short-circuited.
    expect(resultReads()).toBe(7);
  });

  // ── Statuses and provisioning gaps ─────────────────────────────────────────────────

  it("passes a non-ok status through as a successful result, not as a failure", async () => {
    // The screen decides what a non-ok status means. Throwing here would collapse five
    // distinct diagnostic states into one error message. Note this document is INSIDE its
    // own bound: the flow's verdict is not a reason to recompute.
    routeReads({
      result: resultRow({
        rev_computedon: secondsAgo(5),
        rev_resultjson: document({ status: "truncated", staleAfterSeconds: 120 }),
      }),
    });
    updateRecord.mockResolvedValue(undefined);

    const response = await fetchRoundStatistics();
    expect(response.status).toBe("truncated");
    expect(updateRecord).not.toHaveBeenCalled();
  });

  it("throws a named error naming the seed script when no RESULT row exists yet", async () => {
    // A provisioning gap, not a "pending". Waiting will never fix it, so telling a trustee
    // the service is still working would be false and would hide the one action that helps.
    routeReads({ result: null });
    const promise = fetchRoundStatistics();
    await expect(promise).rejects.toBeInstanceOf(RoundStatisticsError);
    await expect(promise).rejects.toThrow(/seed-round-statistics-result\.ps1/);
    expect(updateRecord).not.toHaveBeenCalled();
  });

  it("throws a named error naming the other seed script when no REQUEST row exists yet", async () => {
    routeReads({ result: resultRow({ rev_computedon: null }), request: null });
    const promise = fetchRoundStatistics();
    await expect(promise).rejects.toBeInstanceOf(RoundStatisticsError);
    await expect(promise).rejects.toThrow(/seed-round-statistics-request\.ps1/);
    expect(updateRecord).not.toHaveBeenCalled();
  });

  it("throws rather than writing to an unidentified row when the request row has no id", async () => {
    routeReads({
      result: resultRow({ rev_computedon: null }),
      request: { rev_roundstatisticsrequestid: null },
    });
    const promise = fetchRoundStatistics();
    await expect(promise).rejects.toThrow(/has no id/);
    expect(updateRecord).not.toHaveBeenCalled();
  });
});

describe("fetchRoundStatistics — the request identity is GONE, not bypassed", () => {
  it("names neither requestedAt nor isFresh anywhere in its executable source", () => {
    // TAD §6.3.1 row 3 answers cross-request contamination with the ABSENCE of a request
    // identity in the mechanism, and §5.3.1 with the claim that an age comparison "cannot
    // express" the null-check bug the previous draft had. Both are properties of what is NOT
    // in this file, and a behavioural test cannot see an absence — a poll satisfied by
    // another session (case 6 above) proves the age bound works, but a belt-and-braces
    // `isFresh` flag left in place beside it would pass every one of these tests.
    //
    // Comments are stripped first, on the pattern `schema.test.ts` already uses: this file's
    // own header explains what an `isFresh` flag WAS and why it is gone, and that explanation
    // is the point of it.
    const source = readFileSync(
      join(dirname(fileURLToPath(import.meta.url)), "roundStatistics.ts"),
      "utf8",
    );
    const code = source.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/[^\n]*/g, "");
    expect(code).not.toMatch(/requestedAt/);
    expect(code).not.toMatch(/isFresh/);
    // And the age bound IS what the code reads.
    expect(code).toMatch(/staleAfterSeconds/);
  });
});
