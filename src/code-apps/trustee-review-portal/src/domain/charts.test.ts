/**
 * `buildWellbeingComparisonData` and the categorical chart palette — Fix 3, Revision 8 and
 * Revision 10 (wbs:6.8/6.9).
 *
 * The pivot is the part worth testing exhaustively without rendering anything: it is the one
 * place this pass invents a multi-series shape, and it must break every question down on the
 * SAME six-way scale even when one question's response omits a category another one carries.
 *
 * ## Revision 10 (2026-09-02, wbs:6.8) — pivoted BACK, and these tests are rewritten to match
 *
 * Revision 8 transposed this to one row per QUESTION, one property per response category. The
 * reviewer this round asked for the opposite axis assignment again — one row per RESPONSE
 * CATEGORY (the x-axis, in literal answer-option words), one property per question. Every
 * assertion below is rewritten to those axes; each one still asserts the same PROPERTY it
 * asserted before Revision 8 turned it over — completeness of the six-way scale, stable
 * order, a question named by its heading, an unrecognised question kept rather than dropped,
 * and two questions' figures readable against each other.
 */
import { describe, expect, it } from "vitest";
import { buildWellbeingComparisonData, categoricalColor, CHART_PALETTE } from "./charts";
import type { WellbeingLastYear } from "../dataverse/types";

describe("buildWellbeingComparisonData", () => {
  it("returns null when there is no wellbeing data at all (TAD §3.3 point 3)", () => {
    expect(buildWellbeingComparisonData(null)).toBeNull();
  });

  it("returns null when the flow reported zero questions", () => {
    expect(buildWellbeingComparisonData({ questions: [] })).toBeNull();
  });

  it("puts one row per AGREEMENT_RESPONSE_LABELS category, in scale order (reviewer item 3)", () => {
    const wellbeing: WellbeingLastYear = {
      questions: [{ column: "rev_wellbeinganswer8", population: 400, categories: [] }],
    };
    const result = buildWellbeingComparisonData(wellbeing);
    expect(result?.rows.map((row) => row.value)).toEqual([1, 2, 3, 4, 5, 6]);
    expect(result?.rows.map((row) => row.label)).toEqual([
      "Strongly Disagree",
      "Disagree",
      "Neutral",
      "Agree",
      "Strongly Agree",
      "Not sure",
    ]);
  });

  it("puts one series per question, in the order the flow sent them, named by its heading", () => {
    const wellbeing: WellbeingLastYear = {
      questions: [
        { column: "rev_wellbeinganswer8", population: 400, categories: [] },
        { column: "rev_wellbeinganswer9", population: 380, categories: [] },
        { column: "rev_wellbeinganswer10", population: 390, categories: [] },
      ],
    };
    const result = buildWellbeingComparisonData(wellbeing);
    expect(result?.series.map((series) => series.key)).toEqual([
      "rev_wellbeinganswer8",
      "rev_wellbeinganswer9",
      "rev_wellbeinganswer10",
    ]);
    expect(result?.series.map((series) => series.heading)).toEqual([
      "Wellbeing question 8, last year",
      "Wellbeing question 9, last year",
      "Wellbeing question 10, last year",
    ]);
  });

  it("keeps 'Not sure' as a real sixth row, never dropped from the scale", () => {
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
    const notSure = result?.rows.find((row) => row.label === "Not sure");
    expect(notSure?.value).toBe(6);
    expect(notSure?.rev_wellbeinganswer8).toBe(10);
  });

  it("reads a category a question did not report as null, not as 0", () => {
    // "A zero is a finding; a null is an absence" (TAD §3.3 point 3). A null property is
    // present and aligns identically across every question's row without asserting a
    // measurement.
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
    const disagreeRow = result?.rows.find((row) => row.value === 2);
    const stronglyDisagreeRow = result?.rows.find((row) => row.value === 1);
    expect(disagreeRow?.rev_wellbeinganswer8).toBeNull();
    expect(stronglyDisagreeRow?.rev_wellbeinganswer8).toBe(25);
  });

  it("carries the response's own PERCENTAGE, never its count", () => {
    // Three questions with three different populations cannot be compared on a count axis at
    // all, which is what makes the percentage the correct measure. `count` and `percentage`
    // are deliberately different numbers in this fixture so a regression to `count` cannot pass.
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
    const agreeRow = result?.rows.find((row) => row.value === 4);
    expect(agreeRow?.rev_wellbeinganswer8).toBe(75);
    expect(agreeRow?.rev_wellbeinganswer9).toBe(52.6);
  });

  it("names a question this build does not recognise by its raw column, never dropping it", () => {
    // Same rule RoundStatistics.tsx already applies per question: dropping a question the flow
    // chose to send would be a silent omission, not a safe default.
    const wellbeing: WellbeingLastYear = {
      questions: [{ column: "rev_wellbeinganswer99", population: 400, categories: [] }],
    };
    const result = buildWellbeingComparisonData(wellbeing);
    expect(result?.series).toHaveLength(1);
    expect(result?.series[0]?.key).toBe("rev_wellbeinganswer99");
    expect(result?.series[0]?.heading).toBe("rev_wellbeinganswer99");
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
