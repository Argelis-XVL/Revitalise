/**
 * Sorting, filtering and round derivation — WBS 6.2, FR-034, US-013 AC-2.
 */
import { describe, expect, it } from "vitest";
import {
  applyFilters,
  applySort,
  ariaSortFor,
  DEFAULT_SORT,
  deriveRegions,
  deriveRounds,
  deriveStatuses,
  EMPTY_FILTERS,
  nextSort,
  projectRows,
} from "./listView";
import { makeSummary } from "../test/harness";

const rows = [
  makeSummary({ id: "a", reference: "REV-2026-003", circumstanceScore: 10, status: 3, reviewRound: "2026-Q3", preferredStart: "2026-08-01T00:00:00Z", region: { kind: "known", value: 7 } }),
  makeSummary({ id: "b", reference: "REV-2026-001", circumstanceScore: 55, status: 6, reviewRound: "2026-Q4", preferredStart: "2026-09-01T00:00:00Z", region: { kind: "known", value: 1 } }),
  makeSummary({ id: "c", reference: "REV-2026-002", circumstanceScore: null, status: 6, reviewRound: "2026-Q4", preferredStart: null, region: { kind: "unavailable" } }),
];

describe("deriveRounds — the round comes from the data, never from config", () => {
  it("returns the distinct rounds present, most recent label first", () => {
    expect(deriveRounds(rows)).toEqual(["2026-Q4", "2026-Q3"]);
  });

  it("ignores rows with no round rather than inventing one", () => {
    expect(deriveRounds([makeSummary({ reviewRound: null })])).toEqual([]);
  });
});

describe("deriveStatuses", () => {
  it("offers only statuses that are actually present, with their labels", () => {
    expect(deriveStatuses(rows)).toEqual([
      { value: 3, label: "Borderline" },
      { value: 6, label: "Eligible for Panel" },
    ]);
  });

  it("labels an option value absent from the transcribed map rather than blanking it", () => {
    // Solution import relabels matching option values but does not delete values the new
    // source omits (IMP-0019), so the live set can be a superset of the map.
    expect(deriveStatuses([makeSummary({ status: 99 })])).toEqual([
      { value: 99, label: "Unknown (99)" },
    ]);
  });
});

describe("deriveRegions", () => {
  it("offers only regions with a known value, labelled", () => {
    expect(deriveRegions(rows)).toEqual([
      { value: 1, label: "North East" },
      { value: 7, label: "London" },
    ]);
  });

  it("offers nothing when no region is readable, so no dead control is shipped", () => {
    expect(deriveRegions([makeSummary({ region: { kind: "unavailable" } })])).toEqual([]);
    expect(deriveRegions([makeSummary({ region: { kind: "not-recorded" } })])).toEqual([]);
  });
});

describe("applyFilters", () => {
  it("passes everything through when nothing is set", () => {
    expect(applyFilters(rows, EMPTY_FILTERS)).toHaveLength(rows.length);
  });

  it("filters by round", () => {
    const kept = applyFilters(rows, { ...EMPTY_FILTERS, round: "2026-Q4" });
    expect(kept.map((r) => r.id)).toEqual(["b", "c"]);
  });

  it("filters by region, excluding rows whose region cannot be read", () => {
    expect(applyFilters(rows, { ...EMPTY_FILTERS, region: 7 }).map((r) => r.id)).toEqual(["a"]);
    // Row "c" has an unreadable region: it cannot be shown to satisfy "region is London".
    expect(applyFilters(rows, { ...EMPTY_FILTERS, region: 1 }).map((r) => r.id)).toEqual(["b"]);
  });

  it("filters by status", () => {
    expect(applyFilters(rows, { ...EMPTY_FILTERS, status: 3 }).map((r) => r.id)).toEqual(["a"]);
  });

  it("applies an inclusive score floor and excludes unscored rows", () => {
    // An unscored row is not "score 0". Treating null as zero would put unscored cases
    // inside a floor filter, which is a wrong answer rather than a missing one.
    expect(applyFilters(rows, { ...EMPTY_FILTERS, scoreMin: 10 }).map((r) => r.id)).toEqual([
      "a",
      "b",
    ]);
  });

  it("applies an inclusive score ceiling", () => {
    expect(applyFilters(rows, { ...EMPTY_FILTERS, scoreMax: 10 }).map((r) => r.id)).toEqual(["a"]);
  });

  it("matches the reference case-insensitively on a partial string", () => {
    expect(applyFilters(rows, { ...EMPTY_FILTERS, text: "rev-2026-00" })).toHaveLength(3);
    expect(applyFilters(rows, { ...EMPTY_FILTERS, text: "003" }).map((r) => r.id)).toEqual(["a"]);
  });

  it("combines filters with AND", () => {
    const kept = applyFilters(rows, { ...EMPTY_FILTERS, round: "2026-Q4", scoreMin: 20 });
    expect(kept.map((r) => r.id)).toEqual(["b"]);
  });
});

describe("applySort", () => {
  it("sorts by score descending by default, unscored last", () => {
    expect(applySort(rows, DEFAULT_SORT).map((r) => r.id)).toEqual(["b", "a", "c"]);
  });

  it("puts unscored rows last ascending too — absent is not smallest", () => {
    expect(applySort(rows, { key: "score", direction: "asc" }).map((r) => r.id)).toEqual([
      "a",
      "b",
      "c",
    ]);
  });

  it("sorts by reference", () => {
    expect(applySort(rows, { key: "reference", direction: "asc" }).map((r) => r.id)).toEqual([
      "b",
      "c",
      "a",
    ]);
  });

  it("sorts by preferred start date, undated last", () => {
    expect(applySort(rows, { key: "dates", direction: "asc" }).map((r) => r.id)).toEqual([
      "a",
      "b",
      "c",
    ]);
  });

  it("sorts by region LABEL, with unreadable regions last", () => {
    // London (7) vs North East (1): alphabetical by label, not by option value.
    expect(applySort(rows, { key: "region", direction: "asc" }).map((r) => r.id)).toEqual([
      "a",
      "b",
      "c",
    ]);
  });

  it("sorts by status LABEL, not by the raw option value", () => {
    // A trustee sorting a Status column expects alphabetical text, not the arbitrary
    // order the option set happens to be numbered in.
    expect(applySort(rows, { key: "status", direction: "asc" }).map((r) => r.id)).toEqual([
      "a",
      "b",
      "c",
    ]);
  });

  it("does not mutate its input", () => {
    const before = rows.map((r) => r.id);
    applySort(rows, { key: "reference", direction: "desc" });
    expect(rows.map((r) => r.id)).toEqual(before);
  });

  it("breaks ties on the reference so the order is stable between renders", () => {
    const tied = [
      makeSummary({ id: "x", reference: "REV-2026-009", circumstanceScore: 20 }),
      makeSummary({ id: "y", reference: "REV-2026-004", circumstanceScore: 20 }),
    ];
    expect(applySort(tied, DEFAULT_SORT).map((r) => r.id)).toEqual(["y", "x"]);
  });
});

describe("projectRows — filtering and sorting apply to the whole set (US-013 AC-2)", () => {
  it("filters first, then sorts what survives", () => {
    const projected = projectRows(rows, { ...EMPTY_FILTERS, round: "2026-Q4" }, DEFAULT_SORT);
    expect(projected.map((r) => r.id)).toEqual(["b", "c"]);
  });
});

describe("nextSort and ariaSortFor", () => {
  it("flips direction when the same column is activated again", () => {
    expect(nextSort({ key: "score", direction: "desc" }, "score")).toEqual({
      key: "score",
      direction: "asc",
    });
  });

  it("starts a score column descending and a text column ascending", () => {
    expect(nextSort({ key: "reference", direction: "asc" }, "score").direction).toBe("desc");
    expect(nextSort({ key: "score", direction: "desc" }, "reference").direction).toBe("asc");
  });

  it("reports aria-sort only for the active column", () => {
    const sort = { key: "score", direction: "asc" } as const;
    expect(ariaSortFor(sort, "score")).toBe("ascending");
    expect(ariaSortFor(sort, "reference")).toBe("none");
    expect(ariaSortFor({ key: "score", direction: "desc" }, "score")).toBe("descending");
  });
});
