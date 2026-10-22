/**
 * The card app's computed sentences (ADR-062 B, TAD §13.7), the application-share bar (ADR-065)
 * and the shared status tones (§13.3). Card app only — `src/cards/**` is presentation (ADR-060).
 * Every row of the §13.7 table and of the ADR-065 table has a case here (TAD risk R-D2-14).
 */
import { describe, expect, it } from "vitest";
import {
  daysOpen,
  exceptionalSentence,
  groupTotalSentence,
  roundEyebrow,
  roundHeroSentence,
  roundProgressSentence,
} from "./sentences";
import { shareBar } from "./shareBar";
import { STATUS_LABELS, STATUS_TONE_BY_VALUE, statusToneOf } from "./statusTone";
import { computedOnStamp } from "./stamp";

const NOW = new Date("2026-09-30T15:42:00Z");

describe("daysOpen — R16: inclusive calendar days in UTC", () => {
  it("counts a round opened today as 1, not 0", () => {
    expect(daysOpen("2026-09-30T08:00:00Z", null, NOW)).toBe(1);
  });
  it("counts 1 Sep to 30 Sep as 30 while the round is open (no close date)", () => {
    expect(daysOpen("2026-09-01T00:00:00Z", null, NOW)).toBe(30);
  });
  it("stops at the close date once it has passed", () => {
    expect(daysOpen("2026-08-01T00:00:00Z", "2026-08-31T00:00:00Z", NOW)).toBe(31);
  });
  it("runs to today while the close date is still ahead", () => {
    expect(daysOpen("2026-09-01T00:00:00Z", "2026-10-15T00:00:00Z", NOW)).toBe(30);
  });
  it("is null with no open date, an unreadable one, or one after today", () => {
    expect(daysOpen(null, null, NOW)).toBeNull();
    expect(daysOpen("not a date", null, NOW)).toBeNull();
    expect(daysOpen("2026-10-02T00:00:00Z", null, NOW)).toBeNull();
  });
});

describe("Round progress sentence (§13.7 row 2)", () => {
  it("reads '{n} applications in the last {d} days'", () => {
    expect(roundProgressSentence(48, "2026-09-01T00:00:00Z", null, NOW)).toBe(
      "48 applications in the last 30 days",
    );
  });
  it("uses the singular for one application and for one day", () => {
    expect(roundProgressSentence(1, "2026-09-01T00:00:00Z", null, NOW)).toBe(
      "1 application in the last 30 days",
    );
    expect(roundProgressSentence(3, "2026-09-30T00:00:00Z", null, NOW)).toBe(
      "3 applications in the last day",
    );
  });
  it("says 'No applications yet' for zero", () => {
    expect(roundProgressSentence(0, "2026-09-01T00:00:00Z", null, NOW)).toBe("No applications yet");
  });
  it("falls back to 'in this round' with no open date or one after today", () => {
    expect(roundProgressSentence(48, null, null, NOW)).toBe("48 applications in this round");
    expect(roundProgressSentence(48, "2026-10-05T00:00:00Z", null, NOW)).toBe(
      "48 applications in this round",
    );
  });
  it("shows no sentence (the plain heading) when the count is null", () => {
    expect(roundProgressSentence(null, "2026-09-01T00:00:00Z", null, NOW)).toBeNull();
  });
});

describe("Exceptional circumstances sentence (§13.7 row 3)", () => {
  it("reads '1 in N' for a whole ratio and 'About 1 in N' otherwise", () => {
    expect(exceptionalSentence(12, 48)).toBe("1 in 4 applications cite an exceptional circumstance");
    expect(exceptionalSentence(7, 48)).toBe("About 1 in 7 applications cite an exceptional circumstance");
  });
  it("names none and every", () => {
    expect(exceptionalSentence(0, 48)).toBe("No application cites an exceptional circumstance");
    expect(exceptionalSentence(48, 48)).toBe("Every application cites an exceptional circumstance");
  });
  it("shows the plain heading when the summary or its population is missing or zero — never '1 in Infinity'", () => {
    expect(exceptionalSentence(null, 48)).toBeNull();
    expect(exceptionalSentence(3, null)).toBeNull();
    expect(exceptionalSentence(0, 0)).toBeNull();
  });
});

describe("hero and group sentences, and the round eyebrow (§13.7 rows 1, 7, 8)", () => {
  it("words the round hero from its dates", () => {
    expect(roundHeroSentence("2026-09-01T00:00:00Z", "2026-09-30T00:00:00Z")).toMatch(
      /^Open from 1 Sep.* 2026 to 30 Sep.* 2026$/,
    );
    expect(roundHeroSentence("2026-09-01T00:00:00Z", null)).toMatch(/^Open since 1 Sep.* 2026$/);
    expect(roundHeroSentence(null, "2026-09-30T00:00:00Z")).toBeNull();
  });
  it("words the group total, including zero, and none for null", () => {
    expect(groupTotalSentence(2750)).toBe("£2,750.00 requested together");
    expect(groupTotalSentence(0)).toBe("£0.00 requested together");
    expect(groupTotalSentence(null)).toBeNull();
  });
  it("names the round from the filter, else from rows that share one round, else nothing", () => {
    expect(roundEyebrow("5", [])).toBe("Round 5");
    expect(roundEyebrow("", [{ reviewRound: "5" }, { reviewRound: "5" }])).toBe("Round 5");
    expect(roundEyebrow("", [{ reviewRound: "5" }, { reviewRound: "6" }])).toBeNull();
    expect(roundEyebrow("", [])).toBeNull();
  });
});

describe("the application-share bar — every row of the ADR-065 table", () => {
  it("fills n / (n + p) and states the three figures", () => {
    const bar = shareBar(48, { priorApplicationCount: 715, understatedTotal: false });
    expect(bar.fill).toBeCloseTo(48 / 763, 6);
    expect(bar.lines).toEqual([
      "This round: 48 applications",
      "All applications: 763, including 715 from before the portal",
      "6.3% of all applications",
    ]);
  });
  it("draws a full bar for a seeded zero, and says so", () => {
    const bar = shareBar(48, { priorApplicationCount: 0, understatedTotal: false });
    expect(bar.fill).toBe(1);
    expect(bar.lines[1]).toBe("All applications: 48, including 0 from before the portal");
  });
  it("draws no bar and says 'Not recorded' when p is null, the total is understated, or history is absent", () => {
    for (const history of [
      { priorApplicationCount: null, understatedTotal: false },
      { priorApplicationCount: 715, understatedTotal: true },
      null,
    ]) {
      expect(shareBar(48, history)).toEqual({
        fill: null,
        lines: ["This round: 48 applications", "All applications: Not recorded"],
      });
    }
  });
  it("shows nothing when n is null", () => {
    expect(shareBar(null, { priorApplicationCount: 715, understatedTotal: false })).toEqual({ fill: null, lines: [] });
  });
  it("draws no bar for a zero total", () => {
    expect(shareBar(0, { priorApplicationCount: 0, understatedTotal: false })).toEqual({
      fill: null,
      lines: ["This round: 0 applications", "All applications: 0"],
    });
  });
  it("uses the singular for one application", () => {
    expect(shareBar(1, { priorApplicationCount: 9, understatedTotal: false }).lines[0]).toBe(
      "This round: 1 application",
    );
  });
});

describe("the stamp and the status tones", () => {
  it("words the stamp 'Computed on {date} at {time}', and 'Not recorded' for a null", () => {
    expect(computedOnStamp("2026-08-25T13:05:11Z")).toBe("Computed on 25 Aug 2026 at 13:05 UTC");
    expect(computedOnStamp(null)).toBe("Computed on Not recorded");
  });
  it("tones by the status enumeration's values", () => {
    expect(STATUS_LABELS[6]).toBe("Eligible for Panel");
    expect(STATUS_LABELS[5]).toBe("Under Review");
    expect(STATUS_LABELS[3]).toBe("Borderline");
    expect(Object.keys(STATUS_TONE_BY_VALUE).sort()).toEqual(["3", "5", "6"]);
    expect(statusToneOf(4)).toBe("other");
    expect(statusToneOf(null)).toBe("other");
  });
});
