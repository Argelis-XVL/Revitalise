/**
 * Formatting. The rule under test throughout: a missing value renders as words, never
 * as an empty string, because a blank cell on a decision screen is ambiguous between
 * "nothing recorded" and "you may not see this".
 */
import { describe, expect, it } from "vitest";
import {
  dateSortKey,
  formatAmount,
  formatCount,
  formatDate,
  formatDateRange,
  formatDateTime,
  formatMoneyMeasureAmount,
  formatMoneyMeasurePercentage,
  formatPercentage,
  formatRate,
  formatRegion,
  formatScore,
  formatText,
  formatYesNo,
  NOT_AVAILABLE,
  NOT_RECORDED,
  NOT_SHOWN,
  totalFundingRequested,
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

describe("formatYesNo — the tri-state (Amendment A-05)", () => {
  it("renders true and false as Yes and No", () => {
    expect(formatYesNo(true)).toBe("Yes");
    expect(formatYesNo(false)).toBe("No");
  });

  it("renders null and undefined as NOT_RECORDED, never as No", () => {
    // The whole point: several source columns document an absent answer as normal and
    // distinct from an explicit "No". Rendering null as "No" would erase that fact.
    expect(formatYesNo(null)).toBe(NOT_RECORDED);
    expect(formatYesNo(undefined)).toBe(NOT_RECORDED);
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

describe("totalFundingRequested — FR-035's single total (TAD §3.2, Amendment A-02/OQ-031)", () => {
  it("sums both columns when both are present", () => {
    expect(totalFundingRequested(1200, 300)).toBe(1500);
  });

  it("sums unconditionally — the exceptional-funding flag is display context, not an arithmetic gate", () => {
    // additionalAmountRequested being non-null is itself the signal it was requested; the
    // caller renders the flag separately, this function never reads it.
    expect(totalFundingRequested(1200, 300)).toBe(1500);
  });

  it("treats the absent half as zero, not as making the whole figure absent", () => {
    expect(totalFundingRequested(1200, null)).toBe(1200);
    expect(totalFundingRequested(null, 300)).toBe(300);
  });

  it("is null only when BOTH columns are absent", () => {
    expect(totalFundingRequested(null, null)).toBeNull();
    expect(totalFundingRequested(undefined, undefined)).toBeNull();
  });

  it("renders through formatAmount as words when both are absent, never as £0", () => {
    expect(formatAmount(totalFundingRequested(null, null))).toBe(NOT_RECORDED);
  });
});

describe("the landing screen's formatters (WBS 6.9)", () => {
  it("states a timestamp to the minute, in UTC, and says which zone it is", () => {
    // `formatDate` is not a substitute: the round figures are seconds old under the live
    // design, so two loads five hours apart would render as the same statement. And the
    // zone is labelled because the response's stamp is utcNow() — silently shifting it
    // into the reader's local zone would make two trustees disagree about when the same
    // figures were computed.
    expect(formatDateTime("2026-08-25T13:05:11Z")).toBe("25 Aug 2026, 13:05 UTC");
  });

  it("returns words for an absent timestamp, and the input for an unparseable one", () => {
    expect(formatDateTime(null)).toBe(NOT_RECORDED);
    expect(formatDateTime("  ")).toBe(NOT_RECORDED);
    // Same behaviour as formatDate: showing what arrived beats showing "Invalid Date".
    expect(formatDateTime("not a date")).toBe("not a date");
  });

  it("separates thousands in a count, so a four-digit figure needs no digit-counting", () => {
    expect(formatCount(434)).toBe("434");
    expect(formatCount(1434)).toBe("1,434");
    expect(formatCount(0)).toBe("0");
  });

  it("renders an absent count as words rather than as zero", () => {
    // The distinction the whole landing screen turns on: a zero is a finding, an absence
    // is an absence (TAD §3.3 point 3).
    expect(formatCount(null)).toBe(NOT_RECORDED);
    expect(formatCount(undefined)).toBe(NOT_RECORDED);
    expect(formatCount(Number.NaN)).toBe(NOT_RECORDED);
    expect(formatCount(Number.POSITIVE_INFINITY)).toBe(NOT_RECORDED);
  });

  it("renders a percentage to one decimal place, and an absent one as words not 0%", () => {
    expect(formatPercentage(9.45)).toBe("9.5%");
    expect(formatPercentage(0)).toBe("0.0%");
    // A 0% would assert that nobody in the round fell into a category that may simply
    // never have been counted.
    expect(formatPercentage(null)).toBe(NOT_RECORDED);
    expect(formatPercentage(Number.NaN)).toBe(NOT_RECORDED);
  });

  it("renders a rate to two decimal places — 14.47 applications a day is neither a count nor a percentage", () => {
    expect(formatRate(14.47)).toBe("14.47");
    expect(formatRate(14)).toBe("14.00");
    expect(formatRate(null)).toBe(NOT_RECORDED);
  });
});

describe("formatMoneyMeasureAmount / formatMoneyMeasurePercentage — ADR-039 (Revision 6)", () => {
  it("renders the value with its own population, in the same string", () => {
    // TAD §3.3 property 8: the denominator must be visible IN the cell the value is in, not
    // in a separate column, a tooltip, or a footnote — the two must never be separable.
    const rendered = formatMoneyMeasureAmount({ value: 1500, population: 94 });
    expect(rendered).toMatch(/1,500/);
    expect(rendered).toMatch(/94/);
  });

  it("renders the percentage variant as a percentage, not as currency", () => {
    expect(formatMoneyMeasurePercentage({ value: 73.3, population: 93 })).toBe(
      "73.3% (over 93 applications)",
    );
  });

  it("renders a null measure as NOT_SHOWN — a deliberate suppression, never 0, £0.00, 0% or blank", () => {
    // A below-k break-type row (TAD §6.3.5, ADR-039) arrives as `{ ..., averageCost: null }`.
    // This is the one figure on the landing screen that can be withheld on purpose rather
    // than being genuinely absent, and it must read as neither an absence of data entry
    // (NOT_RECORDED) nor a permissions gap (NOT_AVAILABLE) nor an empty cell.
    expect(formatMoneyMeasureAmount(null)).toBe(NOT_SHOWN);
    expect(formatMoneyMeasurePercentage(null)).toBe(NOT_SHOWN);
    expect(formatMoneyMeasureAmount(null)).not.toBe("");
    expect(formatMoneyMeasureAmount(null)).not.toMatch(/£0\.00|^0$|^0%$/);
    expect(formatMoneyMeasureAmount(null)).not.toBe(NOT_RECORDED);
    expect(formatMoneyMeasureAmount(null)).not.toBe(NOT_AVAILABLE);
  });

  it("NOT_SHOWN is a distinct word from NOT_RECORDED and NOT_AVAILABLE — three different facts", () => {
    // NOT_RECORDED asserts nobody entered a value, which is false for a suppressed money
    // measure: the underlying columns may be fully populated. NOT_AVAILABLE is this app's
    // word for "your role cannot read this column", and the three money columns are
    // IsSecured=0 — a trustee's role is not what withheld the figure. See this constant's
    // own doc in format.ts.
    expect(NOT_SHOWN).not.toBe(NOT_RECORDED);
    expect(NOT_SHOWN).not.toBe(NOT_AVAILABLE);
  });
});
