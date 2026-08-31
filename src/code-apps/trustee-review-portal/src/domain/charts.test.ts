/**
 * `buildWellbeingComparisonData`, the categorical chart palette and the ordinal agreement
 * ramp — Fix 3 and Revision 8, WBS 6.9.
 *
 * The pivot is the part worth testing exhaustively without rendering anything: it is the one
 * place this pass invents a multi-series shape, and it must break every question down on the
 * SAME six-way scale even when one question's response omits a category another one carries.
 *
 * ## Revision 8 (2026-08-31) — these tests are TRANSPOSED, not relaxed
 *
 * The reviewer asked for one chart of three question groups, which is the opposite pivot of
 * Revision 3's: a row was a response category with one property per question, and a row is
 * now a QUESTION with one property per response category. Every assertion below was rewritten
 * to the new axes, and each one still asserts the same PROPERTY it asserted before —
 * completeness of the six-way scale, stable order, a question named by its heading, an
 * unrecognised question kept rather than dropped, and two questions' figures readable against
 * each other. Nothing was deleted because it became inconvenient.
 *
 * ONE ASSERTION DELIBERATELY CHANGED MEANING, and it is called out where it sits: a category
 * a question did not report is now `null` rather than `0`.
 */
import { describe, expect, it } from "vitest";
import {
  agreementResponseColor,
  AGREEMENT_OFFSCALE_COLOR,
  AGREEMENT_SCALE_RAMP,
  buildWellbeingComparisonData,
  categoricalColor,
  CHART_PALETTE,
  wellbeingResponseKey,
} from "./charts";
import type { WellbeingLastYear } from "../dataverse/types";

describe("buildWellbeingComparisonData", () => {
  it("returns null when there is no wellbeing data at all (TAD §3.3 point 3)", () => {
    expect(buildWellbeingComparisonData(null)).toBeNull();
  });

  it("returns null when the flow reported zero questions", () => {
    expect(buildWellbeingComparisonData({ questions: [] })).toBeNull();
  });

  it("puts one row per question, in the order the flow sent them", () => {
    const wellbeing: WellbeingLastYear = {
      questions: [
        { column: "rev_wellbeinganswer8", population: 400, categories: [] },
        { column: "rev_wellbeinganswer9", population: 380, categories: [] },
        { column: "rev_wellbeinganswer10", population: 390, categories: [] },
      ],
    };
    const result = buildWellbeingComparisonData(wellbeing);
    expect(result?.rows.map((row) => row.column)).toEqual([
      "rev_wellbeinganswer8",
      "rev_wellbeinganswer9",
      "rev_wellbeinganswer10",
    ]);
    expect(result?.rows.map((row) => row.label)).toEqual([
      "Wellbeing question 8, last year",
      "Wellbeing question 9, last year",
      "Wellbeing question 10, last year",
    ]);
  });

  it("breaks every question down on all six AGREEMENT_RESPONSE_LABELS categories, in scale order", () => {
    // The completeness property Revision 3 asserted on the category AXIS, now asserted on the
    // SERIES list: every question is broken down the same six ways, in the same order, so the
    // three groups are read against each other bar-position by bar-position.
    const wellbeing: WellbeingLastYear = {
      questions: [
        {
          column: "rev_wellbeinganswer8",
          population: 400,
          categories: [
            { value: 1, count: 100, percentage: 25 },
            { value: 4, count: 300, percentage: 75 },
          ],
        },
      ],
    };
    const result = buildWellbeingComparisonData(wellbeing);
    expect(result).not.toBeNull();
    expect(result?.series.map((series) => series.value)).toEqual([1, 2, 3, 4, 5, 6]);
    expect(result?.series.map((series) => series.heading)).toEqual([
      "Strongly Disagree",
      "Disagree",
      "Neutral",
      "Agree",
      "Strongly Agree",
      "Not sure",
    ]);
    expect(result?.series.map((series) => series.key)).toEqual([
      "response1",
      "response2",
      "response3",
      "response4",
      "response5",
      "response6",
    ]);
  });

  it("keeps 'Not sure' as a real sixth series, never dropped from the scale", () => {
    // Ground truth: the source deck's chart5 carries real counts for this option. Dropping it
    // would understate the context every other category is read in.
    const wellbeing: WellbeingLastYear = {
      questions: [
        {
          column: "rev_wellbeinganswer8",
          population: 400,
          categories: [{ value: 6, count: 40, percentage: 10 }],
        },
      ],
    };
    const result = buildWellbeingComparisonData(wellbeing);
    const notSure = result?.series.find((series) => series.heading === "Not sure");
    expect(notSure?.value).toBe(6);
    expect(result?.rows[0]?.[wellbeingResponseKey(6)]).toBe(10);
  });

  it("reads a category a question did not report as null, not as 0", () => {
    // THE ONE ASSERTION THAT CHANGED MEANING IN THE TRANSPOSE, and it changed TOWARD the rule
    // the rest of this screen already follows (TAD §3.3 point 3: "a zero is a finding; a null
    // is an absence"). Recharts draws no bar for a null, which is the honest rendering — a
    // 0%-height bar and a not-reported category are the same picture, and only one of them is
    // a finding. Revision 3 wrote `0` because a MISSING PROPERTY on a wide-format row would
    // have misaligned the other rows' bars; a `null` property is present and aligns
    // identically without asserting a measurement.
    const wellbeing: WellbeingLastYear = {
      questions: [
        {
          column: "rev_wellbeinganswer8",
          population: 400,
          categories: [{ value: 1, count: 100, percentage: 25 }],
        },
      ],
    };
    const result = buildWellbeingComparisonData(wellbeing);
    const row = result?.rows[0];
    expect(row?.[wellbeingResponseKey(2)]).toBeNull();
    expect(row?.[wellbeingResponseKey(1)]).toBe(25);
  });

  it("carries the response's own PERCENTAGE, never its count", () => {
    // FR-062, reviewer item 7. Three questions with three different populations cannot be
    // compared on a count axis at all, which is what makes the percentage the correct measure
    // for this pivot specifically. `count` and `percentage` are deliberately different numbers
    // in this fixture so a regression to `count` cannot pass.
    const wellbeing: WellbeingLastYear = {
      questions: [
        {
          column: "rev_wellbeinganswer8",
          population: 400,
          categories: [{ value: 4, count: 300, percentage: 75 }],
        },
        {
          column: "rev_wellbeinganswer9",
          population: 380,
          categories: [{ value: 4, count: 200, percentage: 52.6 }],
        },
      ],
    };
    const result = buildWellbeingComparisonData(wellbeing);
    const agreeKey = wellbeingResponseKey(4);
    expect(result?.rows[0]?.[agreeKey]).toBe(75);
    expect(result?.rows[1]?.[agreeKey]).toBe(52.6);
  });

  it("names a question this build does not recognise by its raw column, never dropping it", () => {
    // Same rule RoundStatistics.tsx already applies per question: dropping a question
    // the flow chose to send would be a silent omission, not a safe default.
    const wellbeing: WellbeingLastYear = {
      questions: [{ column: "rev_wellbeinganswer99", population: 400, categories: [] }],
    };
    const result = buildWellbeingComparisonData(wellbeing);
    expect(result?.rows).toHaveLength(1);
    expect(result?.rows[0]?.column).toBe("rev_wellbeinganswer99");
    expect(result?.rows[0]?.label).toBe("rev_wellbeinganswer99");
  });

  it("uses a prefixed row key, so a bare option-set integer is never read as an array index", () => {
    // A Recharts `dataKey` is a property-path string, and `data[4]` on a row object would be
    // resolved as an index rather than as the "Agree" category.
    expect(wellbeingResponseKey(4)).toBe("response4");
  });
});

describe("agreementResponseColor — an ordinal scale, not six identities", () => {
  it("maps the five scale points onto the ramp in scale order", () => {
    for (const value of [1, 2, 3, 4, 5]) {
      expect(agreementResponseColor(value)).toBe(AGREEMENT_SCALE_RAMP[value - 1]);
    }
  });

  it("paints 'Not sure' off-scale, never as a sixth step past Strongly Agree", () => {
    // A non-answer given a sixth magenta step would sit past "Strongly Agree" in the reader's
    // eye and assert an opinion nobody expressed.
    expect(agreementResponseColor(6)).toBe(AGREEMENT_OFFSCALE_COLOR);
    expect(AGREEMENT_SCALE_RAMP).not.toContain(AGREEMENT_OFFSCALE_COLOR);
  });

  it("paints an option this build has never declared off-scale too — the colour counterpart of `Unknown (n)`", () => {
    expect(agreementResponseColor(99)).toBe(AGREEMENT_OFFSCALE_COLOR);
    expect(agreementResponseColor(0)).toBe(AGREEMENT_OFFSCALE_COLOR);
  });

  it("is the exact five-step ramp validated with the dataviz skill's ordinal checkset", () => {
    // `validate_palette.js ... --ordinal --mode light --surface "#ffffff"` reported ALL CHECKS
    // PASS for this sequence. Changing any value invalidates that verification.
    expect(AGREEMENT_SCALE_RAMP).toEqual(["#ff66ab", "#ed008c", "#ac0064", "#8c0050", "#51002c"]);
  });

  it("is monotonically ordered, so the scale's direction is visible in the colour", () => {
    // The property that makes it ordinal rather than categorical: lightness decreases in one
    // direction across the whole scale. Asserted on the ramp's own luminance so a later edit
    // that keeps five valid hexes but scrambles their order fails here.
    const luminance = (hex: string): number => {
      const channel = (start: number): number => {
        const srgb = parseInt(hex.slice(start, start + 2), 16) / 255;
        return srgb <= 0.03928 ? srgb / 12.92 : Math.pow((srgb + 0.055) / 1.055, 2.4);
      };
      return 0.2126 * channel(1) + 0.7152 * channel(3) + 0.0722 * channel(5);
    };
    const values = AGREEMENT_SCALE_RAMP.map(luminance);
    for (let index = 1; index < values.length; index += 1) {
      expect(values[index]!).toBeLessThan(values[index - 1]!);
    }
  });
});

describe("categoricalColor", () => {
  it("assigns the validated palette in fixed order", () => {
    expect(categoricalColor(0)).toBe(CHART_PALETTE[0]);
    expect(categoricalColor(1)).toBe(CHART_PALETTE[1]);
    expect(categoricalColor(2)).toBe(CHART_PALETTE[2]);
  });

  it("wraps rather than throwing for an index past the validated three", () => {
    expect(categoricalColor(3)).toBe(CHART_PALETTE[0]);
    expect(categoricalColor(4)).toBe(CHART_PALETTE[1]);
  });

  it("is the exact three-hex triple this pass validated with the dataviz skill's script", () => {
    // Both `--mode light` and `--mode dark` reported ALL CHECKS PASS for this triple.
    // Changing any of these three values invalidates that verification.
    expect(CHART_PALETTE).toEqual(["#ed008c", "#8e4fc4", "#009aa8"]);
  });
});
