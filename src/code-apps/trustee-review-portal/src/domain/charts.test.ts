/**
 * `buildWellbeingComparisonData` and the categorical chart palette — Fix 3, WBS 6.9.
 *
 * The pivot is the part worth testing exhaustively without rendering anything: it is
 * the one place this pass invents a NEW multi-series shape, and it must line up every
 * question on the same category axis even when one question's response omits a
 * category another one carries.
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

  it("puts every one of AGREEMENT_RESPONSE_LABELS' six categories on the axis, in order", () => {
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

  it("reads a category a question did not report as 0 for that question, not as a missing row", () => {
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
    expect(disagreeRow?.rev_wellbeinganswer8).toBe(0);
    const stronglyDisagreeRow = result?.rows.find((row) => row.value === 1);
    expect(stronglyDisagreeRow?.rev_wellbeinganswer8).toBe(100);
  });

  it("carries one series per question, each named through WELLBEING_QUESTION_HEADINGS", () => {
    const wellbeing: WellbeingLastYear = {
      questions: [
        { column: "rev_wellbeinganswer8", population: 400, categories: [] },
        { column: "rev_wellbeinganswer9", population: 400, categories: [] },
      ],
    };
    const result = buildWellbeingComparisonData(wellbeing);
    expect(result?.series).toEqual([
      { key: "rev_wellbeinganswer8", heading: "Wellbeing question 8, last year" },
      { key: "rev_wellbeinganswer9", heading: "Wellbeing question 9, last year" },
    ]);
  });

  it("names a question this build does not recognise by its raw column, never dropping it", () => {
    // Same rule RoundStatistics.tsx already applies per question: dropping a question
    // the flow chose to send would be a silent omission, not a safe default.
    const wellbeing: WellbeingLastYear = {
      questions: [{ column: "rev_wellbeinganswer99", population: 400, categories: [] }],
    };
    const result = buildWellbeingComparisonData(wellbeing);
    expect(result?.series).toEqual([{ key: "rev_wellbeinganswer99", heading: "rev_wellbeinganswer99" }]);
  });

  it("gives every question its own count in the same row, so bars for one category compare directly", () => {
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
    expect(agreeRow?.rev_wellbeinganswer8).toBe(300);
    expect(agreeRow?.rev_wellbeinganswer9).toBe(200);
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
