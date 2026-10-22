/**
 * The card layout's display map — ADR-058 (and ADR-059's composed constant), card app only.
 *
 * The assertion that matters most is the third block: no display hint, present or absent or
 * wrong, can render a redacted or restricted row as a plain value (TAD risk R-D2-5).
 */
import { describe, expect, it } from "vitest";
import { makeDetail } from "../test/harness";
import { APPLICATION_DETAIL_LAYOUT, isRowVisible } from "./applicationDetailLayout";
import type { DetailCell, DetailRow } from "./applicationDetailLayout";
import {
  CHIP_LABEL,
  GROUP_HEADING,
  HERO_FIRST_ROW,
  HERO_SECTION_ID,
  ROW_DISPLAY,
  SECTION_EYEBROW,
  SECTION_GROUP_ORDER,
  STATUS_LABELS,
  STATUS_TONE_BY_VALUE,
  VERDICT_EYEBROW,
  STAFF_RECOMMENDATION_EYEBROW,
  badgeValue,
  badgeValueIsLong,
  chipRowsOf,
  displayOf,
  groupKindOf,
  heroHeading,
  isAbsentText,
  numberOf,
  partitionRows,
  scaleAnswerText,
  scoreFraction,
  statusToneOf,
} from "./applicationDetailDisplay";
import type { Display } from "./applicationDetailDisplay";
import {
  WITHHELD_EXPLANATION,
  WITHHELD_EXPLANATION_FIRST_SENTENCE,
} from "./visibility";

const ALL_ROWS: readonly { sectionId: string; row: DetailRow }[] = APPLICATION_DETAIL_LAYOUT.flatMap(
  (section) => section.groups.flatMap((group) => group.rows.map((row) => ({ sectionId: section.id, row }))),
);
const ROW_IDS = new Set(ALL_ROWS.map(({ row }) => row.id));

/** Every conditional row visible, and every redacted row released with text, so every row renders. */
const EVERYTHING = makeDetail({
  exceptionalCircumstance: 4,
  conditionProfile: [3, 10],
  supportRecipientConditionProfile: [2, 10],
  redactionReleased: true,
  redactedNarrative: "x",
});

describe("ROW_DISPLAY — the README's mapping table (lines 35-41)", () => {
  it("names only real row ids", () => {
    for (const id of Object.keys(ROW_DISPLAY)) expect(ROW_IDS.has(id), id).toBe(true);
  });

  it("maps every row to the display the design table gives it", () => {
    const expected: Record<string, Display> = {
      S0a: "status", S0b: "fact", S1: "fact", S2: "fact", S3: "score",
      S4: "fact", S5: "fact", S6: "fact", S7: "fact",
      D1: "fact", D2: "fact", D3: "fact", D4: "fact",
      D5: "cost", D6: "cost", D7: "cost", D8: "costTotal", D9: "cost", D10: "cost",
      D11: "fact", D11a: "answer", D12: "answer", D13: "answer",
      A1: "fact", A2: "fact", A3: "chips", A3a: "answer", A3b: "answer", A4: "answer",
      A5: "fact", A6: "answer", A7: "fact",
      C1: "score", C2: "scale",
      C3: "likert", C4: "likert", C5: "likert", C6: "likert", C7: "likert", C8: "likert",
      C9: "likert", C10: "likert", C11: "likert", C12: "likert",
      F1: "restricted", F2: "restricted", F3: "restricted",
      F4: "fact", F5: "answer", F6: "fact",
    };
    expect(new Set(Object.keys(expected))).toEqual(ROW_IDS);
    for (const { row } of ALL_ROWS) {
      expect(displayOf(row, row.cell(EVERYTHING)), row.id).toBe(expected[row.id]);
    }
  });

  it("renders the WI-0060 rows as fact tiles by default (no map entry)", () => {
    for (const id of ["D1", "D2", "D3", "D4", "D11", "A1", "A2", "A5", "A7", "F4", "F6"]) {
      expect(ROW_DISPLAY[id], id).toBeUndefined();
    }
  });
});

describe("a display hint can never render a protected row as a value (ADR-058, R-D2-5)", () => {
  const protectedRows = ALL_ROWS.filter(({ row }) => {
    const kind = row.cell(EVERYTHING).kind;
    return kind === "redacted" || kind === "restricted";
  });

  it("found the protected rows: 8 redacted answers and 3 restricted rows", () => {
    expect(protectedRows.map(({ row }) => row.id)).toEqual([
      "D11a", "D12", "D13", "A3a", "A3b", "A4", "A6", "F1", "F2", "F3", "F5",
    ]);
  });

  it("maps every redacted row to 'answer' and every restricted row to 'restricted'", () => {
    for (const { row } of protectedRows) {
      const cell = row.cell(EVERYTHING);
      expect(ROW_DISPLAY[row.id], row.id).toBe(cell.kind === "redacted" ? "answer" : "restricted");
    }
  });

  it("keeps them protected whatever the map says: every display kind is tried against each", () => {
    // One row id per display kind the map uses, so a protected cell is paired with every hint.
    const idForDisplay = new Map<Display, string>();
    for (const [id, display] of Object.entries(ROW_DISPLAY)) {
      if (!idForDisplay.has(display)) idForDisplay.set(display, id);
    }
    idForDisplay.set("fact", "D1");
    for (const { row } of protectedRows) {
      const cell = row.cell(EVERYTHING);
      for (const [display, id] of idForDisplay) {
        const disguised: DetailRow = { ...row, id };
        expect(displayOf(disguised, cell), `${row.id} under ${display}`).toBe(
          cell.kind === "redacted" ? "answer" : "restricted",
        );
      }
    }
  });

  it("never gives a plain value a protected look it has no state for", () => {
    const value: DetailCell = { kind: "value", text: "x" };
    expect(displayOf({ id: "D12", label: "L", cell: () => value }, value)).toBe("fact");
    expect(displayOf({ id: "F1", label: "L", cell: () => value }, value)).toBe("fact");
    expect(displayOf({ id: "UNMAPPED", label: "L", cell: () => value }, value)).toBe("fact");
  });
});

describe("partitionRows — ADR-057's contract, per section", () => {
  it("declares a group order for every Pack section, and only for those", () => {
    expect(new Set(Object.keys(SECTION_GROUP_ORDER))).toEqual(
      new Set(APPLICATION_DETAIL_LAYOUT.map((section) => section.id)),
    );
  });

  for (const detail of [makeDetail(), EVERYTHING]) {
    it(`renders every visible row exactly once, in its own section (${detail === EVERYTHING ? "all conditional rows" : "defaults"})`, () => {
      for (const section of APPLICATION_DETAIL_LAYOUT) {
        const rendered = section.groups.flatMap((group) =>
          partitionRows(section.id, group.rows, detail).flatMap((g) => g.rows.map((r) => r.row.id)),
        );
        const expected = section.groups.flatMap((group) =>
          group.rows.filter((row) => isRowVisible(row, detail)).map((row) => row.id),
        );
        expect([...rendered].sort(), section.id).toEqual([...expected].sort());
        expect(new Set(rendered).size, section.id).toBe(rendered.length);
      }
    });
  }

  it("keeps Pack order inside each display group, and the groups in the declared order", () => {
    for (const section of APPLICATION_DETAIL_LAYOUT) {
      const packOrder = section.groups.flatMap((group) => group.rows.map((row) => row.id));
      for (const group of section.groups) {
        const groups = partitionRows(section.id, group.rows, EVERYTHING);
        const order = SECTION_GROUP_ORDER[section.id] ?? [];
        expect(groups.map((g) => order.indexOf(g.kind)), section.id).toEqual(
          [...groups.map((g) => order.indexOf(g.kind))].sort((a, b) => a - b),
        );
        for (const g of groups) {
          const ids = g.rows.map((r) => r.row.id);
          expect(ids, `${section.id}/${g.kind}`).toEqual(
            [...ids].sort((a, b) => packOrder.indexOf(a) - packOrder.indexOf(b)),
          );
          for (const r of g.rows) expect(groupKindOf(r.display)).toBe(g.kind);
        }
      }
    }
  });

  it("keeps D8 inside the receipt in Pack order: D5, D6, D7, D8, D9, D10 (ADR-057 decision 3)", () => {
    const details = APPLICATION_DETAIL_LAYOUT.find((s) => s.id === "application-details");
    const groups = partitionRows("application-details", details?.groups[0]?.rows ?? [], EVERYTHING);
    const costs = groups.find((g) => g.kind === "costs");
    expect(costs?.rows.map((r) => r.row.id)).toEqual(["D5", "D6", "D7", "D8", "D9", "D10"]);
    expect(costs?.rows.map((r) => r.display)).toEqual(["cost", "cost", "cost", "costTotal", "cost", "cost"]);
  });

  it("places the conditional rows in their trigger row's section, in Pack order within their group (ADR-057 (d))", () => {
    const about = APPLICATION_DETAIL_LAYOUT.find((s) => s.id === "about-applicant");
    const groups = partitionRows("about-applicant", about?.groups[0]?.rows ?? [], EVERYTHING);
    expect(groups.find((g) => g.kind === "answers")?.rows.map((r) => r.row.id)).toEqual([
      "A3a", "A3b", "A4", "A6",
    ]);
    const details = APPLICATION_DETAIL_LAYOUT.find((s) => s.id === "application-details");
    const dGroups = partitionRows("application-details", details?.groups[0]?.rows ?? [], EVERYTHING);
    expect(dGroups.find((g) => g.kind === "answers")?.rows[0]?.row.id).toBe("D11a");
  });

  it("omits a conditional row when 'Other' is not chosen", () => {
    const ids = APPLICATION_DETAIL_LAYOUT.flatMap((section) =>
      section.groups.flatMap((group) =>
        partitionRows(section.id, group.rows, makeDetail()).flatMap((g) => g.rows.map((r) => r.row.id)),
      ),
    );
    for (const id of ["D11a", "A3a", "A3b"]) expect(ids, id).not.toContain(id);
  });
});

describe("copy and hero data (reviewer R2, R3)", () => {
  it("gives every non-hero Pack section an eyebrow, and the Verdict the brand tone", () => {
    expect(SECTION_EYEBROW["application-details"]?.text).toBe("The break");
    expect(SECTION_EYEBROW["about-applicant"]?.text).toBe("Who they are");
    expect(SECTION_EYEBROW["current-circumstances"]?.text).toBe("How they are doing");
    expect(SECTION_EYEBROW["financial-eligibility"]?.text).toBe("Money");
    expect(SECTION_EYEBROW[HERO_SECTION_ID]?.text).toBe("Summary");
    expect(STAFF_RECOMMENDATION_EYEBROW).toEqual({ text: "From the team", tone: "purple" });
    expect(VERDICT_EYEBROW).toEqual({ text: "Your decision", tone: "brand" });
  });

  it("names the three new sub-headings", () => {
    expect(GROUP_HEADING).toEqual({
      costs: "Costs",
      answers: "In their words",
      restricted: "Not visible to trustees",
    });
  });

  it("shortens only S6's chip, and keeps the Pack label reachable", () => {
    expect(CHIP_LABEL).toEqual({ S6: "Total requested inc. exceptional funding" });
    const s6 = ALL_ROWS.find(({ row }) => row.id === "S6")?.row;
    expect(s6?.label).toBe("Individual Total Amount Requesting Revitalise inc. Exceptional Funding");
  });

  it("puts S0b, S1, S2 in the first chip row and every other hero fact in the second", () => {
    expect([...HERO_FIRST_ROW].sort()).toEqual(["S0b", "S1", "S2"]);
  });

  it("writes the hero heading and badge from the score, or their absence", () => {
    expect(heroHeading(42)).toBe("42 out of 60 circumstance points");
    expect(heroHeading(null)).toBe("Not scored yet");
    expect(badgeValue(42)).toBe("42");
    expect(badgeValue(null)).toBe("—");
    expect(badgeValueIsLong("42")).toBe(false);
    expect(badgeValueIsLong("1000")).toBe(true);
  });
});

describe("raw-value accessors read only their row's own column", () => {
  it("reads the score for S3 and C1, the 0-10 answer for C2, and nothing for any other row", () => {
    const d = makeDetail({ circumstanceScore: 42, lifeSatisfaction: 7 });
    expect(numberOf("S3", d)).toBe(42);
    expect(numberOf("C1", d)).toBe(42);
    expect(numberOf("C2", d)).toBe(7);
    expect(numberOf("D5", d)).toBeNull();
  });

  it("clamps the bar fill to 0..1", () => {
    expect(scoreFraction(null)).toBe(0);
    expect(scoreFraction(30)).toBe(0.5);
    expect(scoreFraction(90)).toBe(1);
    expect(scoreFraction(-5)).toBe(0);
  });

  it("states the scale answer in words", () => {
    expect(scaleAnswerText("7")).toBe("Answer: 7 out of 10");
  });

  it("maps status tones by the existing status enumeration's values, not by new labels", () => {
    expect(STATUS_LABELS[6]).toBe("Eligible for Panel");
    expect(STATUS_LABELS[5]).toBe("Under Review");
    expect(STATUS_LABELS[3]).toBe("Borderline");
    expect(Object.keys(STATUS_TONE_BY_VALUE).sort()).toEqual(["3", "5", "6"]);
    expect(statusToneOf(6)).toBe("eligible");
    expect(statusToneOf(5)).toBe("review");
    expect(statusToneOf(3)).toBe("borderline");
    expect(statusToneOf(7)).toBe("other");
    expect(statusToneOf(null)).toBe("other");
  });

  it("splits A3's conditions into chip rows the way the layout's eitherPerson() labels them", () => {
    expect(chipRowsOf("A3", makeDetail())).toEqual([]);
    expect(chipRowsOf("A3", makeDetail({ conditionProfile: [3] }))).toHaveLength(1);
    expect(chipRowsOf("A3", makeDetail({ conditionProfile: [3] }))[0]?.owner).toBeNull();
    expect(chipRowsOf("A3", makeDetail({ supportRecipientConditionProfile: [2] }))[0]?.owner).toBeNull();
    const both = chipRowsOf("A3", makeDetail({ conditionProfile: [3, 10], supportRecipientConditionProfile: [2] }));
    expect(both.map((r) => r.owner)).toEqual(["You", "The person you support"]);
    expect(both[0]?.labels).toHaveLength(2);
    expect(chipRowsOf("D1", EVERYTHING)).toEqual([]);
  });

  it("treats the app's absence words as absent, and nothing else", () => {
    for (const word of ["Not recorded", "Not available", "Not set", "Not scored"]) {
      expect(isAbsentText(word), word).toBe(true);
    }
    expect(isAbsentText("Yes")).toBe(false);
  });
});

describe("ADR-059 — the withheld first sentence is composed into the full explanation", () => {
  it("keeps the full explanation character for character what it was before the split", () => {
    expect(WITHHELD_EXPLANATION).toBe(
      "This answer has not been released for trustee review yet. Every free-text answer is " +
        "withheld until the process owner has checked its anonymisation and released it, so this " +
        "is the expected state rather than a fault.",
    );
  });

  it("makes the short text the long text's first sentence, by construction", () => {
    expect(WITHHELD_EXPLANATION_FIRST_SENTENCE).toBe(
      "This answer has not been released for trustee review yet.",
    );
    expect(WITHHELD_EXPLANATION.startsWith(`${WITHHELD_EXPLANATION_FIRST_SENTENCE} `)).toBe(true);
  });
});
