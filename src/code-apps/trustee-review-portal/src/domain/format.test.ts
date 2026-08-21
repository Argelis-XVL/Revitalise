/**
 * Formatting. The rule under test throughout: a missing value renders as words, never
 * as an empty string, because a blank cell on a decision screen is ambiguous between
 * "nothing recorded" and "you may not see this".
 */
import { describe, expect, it } from "vitest";
import {
  dateSortKey,
  formatAmount,
  formatDate,
  formatDateRange,
  formatRegion,
  formatScore,
  formatText,
  NOT_AVAILABLE,
  NOT_RECORDED,
} from "./format";

describe("no formatter ever returns an empty string", () => {
  const empties = [null, undefined, "", "   "];
  it("formatText", () => {
    for (const value of empties) {
      expect(formatText(value as string | null)).toBe(NOT_RECORDED);
    }
  });
  it("formatDate", () => {
    for (const value of [null, undefined, "", "   "]) {
      expect(formatDate(value as string | null)).toBe(NOT_RECORDED);
    }
  });
  it("formatScore and formatAmount", () => {
    expect(formatScore(null)).toBe("Not scored");
    expect(formatAmount(null)).toBe(NOT_RECORDED);
  });
  it("the two absent-value words are distinct, because they mean different things", () => {
    expect(NOT_RECORDED).not.toBe(NOT_AVAILABLE);
  });
});

describe("formatScore", () => {
  it("renders zero as zero, not as absent", () => {
    // A genuine score of 0 is a fact about the application; rendering it as "Not scored"
    // would misreport it.
    expect(formatScore(0)).toBe("0");
  });
});

describe("formatDate", () => {
  // Fixtures avoid September deliberately: en-GB `month: "short"` abbreviates it as
  // "Sept" on current ICU and as "Sep" on older ones, so a September literal makes the
  // test fail on an ICU upgrade rather than on a defect.
  it("renders an ISO date in en-GB day-month-year", () => {
    expect(formatDate("2026-10-05T00:00:00Z")).toBe("5 Oct 2026");
  });

  it("returns unparseable input unchanged rather than inventing a date", () => {
    expect(formatDate("not-a-date")).toBe("not-a-date");
  });

  it("reads the date in UTC, so a stored date does not shift by timezone", () => {
    expect(formatDate("2026-01-01T00:30:00Z")).toBe("1 Jan 2026");
  });
});

describe("formatDateRange", () => {
  it("renders both ends as a range", () => {
    expect(formatDateRange("2026-10-05T00:00:00Z", "2026-10-12T00:00:00Z")).toBe(
      "5 Oct 2026 to 12 Oct 2026",
    );
  });
  it("renders a one-ended range without pretending the other end exists", () => {
    expect(formatDateRange("2026-10-05T00:00:00Z", null)).toBe("From 5 Oct 2026");
    expect(formatDateRange(null, "2026-10-12T00:00:00Z")).toBe("Until 12 Oct 2026");
  });
  it("renders no dates as absent", () => {
    expect(formatDateRange(null, null)).toBe(NOT_RECORDED);
  });
});

describe("dateSortKey", () => {
  it("returns null for anything unsortable, so nulls can be forced last", () => {
    expect(dateSortKey(null)).toBeNull();
    expect(dateSortKey("")).toBeNull();
    expect(dateSortKey("nonsense")).toBeNull();
  });
  it("orders two real dates", () => {
    const earlier = dateSortKey("2026-01-01T00:00:00Z");
    const later = dateSortKey("2026-02-01T00:00:00Z");
    expect(earlier).not.toBeNull();
    expect(later).not.toBeNull();
    expect(Number(earlier)).toBeLessThan(Number(later));
  });
});

describe("formatRegion", () => {
  it("renders a known region as its label", () => {
    expect(formatRegion({ kind: "known", value: 9 })).toBe("South West");
  });

  it("distinguishes 'we read it and there is none' from 'we could not read it'", () => {
    // The distinction that matters. Collapsing these would tell a trustee a region is
    // missing when it is actually withheld from them.
    expect(formatRegion({ kind: "not-recorded" })).toBe(NOT_RECORDED);
    expect(formatRegion({ kind: "unavailable" })).toBe(NOT_AVAILABLE);
    expect(NOT_RECORDED).not.toBe(NOT_AVAILABLE);
  });

  it("renders an option value absent from the transcribed map rather than blanking it", () => {
    expect(formatRegion({ kind: "known", value: 99 })).toBe("Unknown (99)");
  });
});

describe("formatAmount", () => {
  it("renders a number as a currency string", () => {
    expect(formatAmount(1200)).toMatch(/1,200/);
  });
  it("renders zero, not absent", () => {
    expect(formatAmount(0)).not.toBe(NOT_RECORDED);
  });
});
