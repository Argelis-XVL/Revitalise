/**
 * The Recharts visuals in isolation — Fix 3, WBS 6.9.
 *
 * `DistributionChart.test.tsx` already covers the accessible content (the table, the
 * `role="img"` SVG, the print attributes); these tests cover what is NEW here: the
 * decorative figures are actually hidden from assistive technology and out of the tab
 * order, the fixed categorical palette is assigned in order, and a legend appears
 * exactly when the dataviz skill says one must (>= 2 series, none for one).
 */
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import {
  CategoryBarChart,
  CompositionPieChart,
  WellbeingComparisonChart,
  wrapTickLabel,
} from "./RoundStatisticsCharts";
import {
  agreementResponseColor,
  AGREEMENT_OFFSCALE_COLOR,
  buildWellbeingComparisonData,
  CHART_PALETTE,
} from "../domain/charts";
import { buildSeries } from "../domain/landing";
import type { Series } from "../domain/landing";
import { APPLICANT_GENDER_LABELS, APPLICANT_TYPE_LABELS } from "../dataverse/schema";
import type { WellbeingLastYear } from "../dataverse/types";

function genderSeries(): Series {
  const built = buildSeries(
    {
      population: 434,
      categories: [
        { value: 1, count: 260, percentage: 59.9 },
        { value: 2, count: 150, percentage: 34.6 },
        { value: 3, count: 24, percentage: 5.5 },
      ],
    },
    APPLICANT_GENDER_LABELS,
  );
  if (built === null) throw new Error("expected a series");
  return built;
}

function applicantTypeSeries(): Series {
  const built = buildSeries(
    {
      population: 434,
      categories: [
        { value: 1, count: 210, percentage: 48.4 },
        { value: 2, count: 180, percentage: 41.5 },
        { value: 3, count: 44, percentage: 10.1 },
      ],
    },
    APPLICANT_TYPE_LABELS,
  );
  if (built === null) throw new Error("expected a series");
  return built;
}

/**
 * Every axis tick's label, reassembled from its `<tspan>` lines.
 *
 * `WrappedCategoryTick` breaks a long label across `<tspan>`s at word boundaries, and the
 * space it wraps ON is consumed by the break — so the tick's raw `textContent` reads
 * "Wellbeing question8, last year" and a naive substring assertion fails on a chart that is
 * in fact correct. Joining the lines with a single space reverses the wrap exactly, because
 * `wrapTickLabel` only ever splits on whitespace it has already collapsed.
 */
function axisTickLabels(container: HTMLElement): string[] {
  return Array.from(container.querySelectorAll("svg text")).map((text) => {
    const spans = Array.from(text.querySelectorAll("tspan"));
    const parts = spans.length === 0 ? [text.textContent ?? ""] : spans.map((s) => s.textContent ?? "");
    return parts.join(" ").trim();
  });
}

/**
 * A series with a null percentage in it — the absence case, which must draw no bar rather
 * than a zero-height one (TAD §3.3 point 3).
 */
function seriesWithAbsentShare(): Series {
  const built = buildSeries(
    {
      population: 434,
      categories: [
        { value: 1, count: 260, percentage: 59.9 },
        { value: 2, count: 150, percentage: null },
      ],
    },
    APPLICANT_GENDER_LABELS,
  );
  if (built === null) throw new Error("expected a series");
  return built;
}

describe("CategoryBarChart", () => {
  it("draws one bar for every category in the series", () => {
    const series = genderSeries();
    const { container } = render(<CategoryBarChart series={series} />);
    const bars = container.querySelectorAll(".recharts-rectangle");
    expect(bars).toHaveLength(series.rows.length);
  });

  it("draws bars from PERCENTAGE, not count (FR-061/FR-062, reviewer items 4 and 6)", () => {
    // The regression guard for the reviewer's "percentage of round applications, not raw
    // counts" finding.
    //
    // THE FIXTURE DELIBERATELY INVERTS THE TWO FIELDS: the first category has the larger
    // COUNT and the smaller PERCENTAGE. That is legal input — `SeriesRow.percentage` is "as
    // the response computed it, never derived here from count/population" (domain/landing.ts)
    // — and it is the only fixture shape that can tell the two apart. A realistic one cannot:
    // with `percentage` proportional to `count`, both readings give bars in the SAME ratio,
    // so a chart that regressed to `count` would still pass.
    const inverted = buildSeries(
      {
        population: 434,
        categories: [
          { value: 1, count: 260, percentage: 20 },
          { value: 2, count: 150, percentage: 60 },
        ],
      },
      APPLICANT_GENDER_LABELS,
    );
    if (inverted === null) throw new Error("expected a series");
    const { container } = render(<CategoryBarChart series={inverted} />);
    const heights = Array.from(container.querySelectorAll(".recharts-rectangle")).map((bar) =>
      Number(bar.getAttribute("height")),
    );
    // Plotted by percentage, the SECOND bar is the taller one. Plotted by count it would be
    // the first. Ratios rather than pixels, so this does not depend on chart geometry.
    expect(heights[1]! / heights[0]!).toBeCloseTo(60 / 20, 1);
    expect(heights[0]!).toBeLessThan(heights[1]!);
  });

  it("draws NO bar for a null percentage — never a zero-height one", () => {
    // "A zero is a finding; a null is an absence" (TAD §3.3 point 3). A 0%-height bar would
    // assert a measurement of 0%, which the response did not report.
    const { container } = render(<CategoryBarChart series={seriesWithAbsentShare()} />);
    expect(container.querySelectorAll(".recharts-rectangle")).toHaveLength(1);
  });

  it("grows bars upward, with the categories on the x-axis (reviewer item 4)", () => {
    // The Recharts `layout="vertical"` inversion this chart used to hit: that prop names the
    // CATEGORY AXIS's direction, so it drew horizontal bars. In the default layout the
    // category axis is the x-axis, which is where the option labels must be.
    //
    // Asserted against the whole figure's text rather than `.recharts-xAxis`'s own: Recharts
    // v3 draws the axis LINE and its TICKS into two different z-index layers, so the element
    // carrying that class is empty and a `.recharts-xAxis` query silently passes nothing.
    const series = genderSeries();
    const { container } = render(<CategoryBarChart series={series} />);
    const labels = axisTickLabels(container);
    for (const row of series.rows) {
      expect(labels).toContain(row.label);
    }
    // The value axis is a percentage scale, not a count of applications.
    expect(labels.join(" ")).toMatch(/\d+%/);
    // A vertical bar is taller than it is wide only incidentally; what makes it vertical is
    // that it is anchored to the BOTTOM of the plot area. Every bar's lower edge is the same
    // y, which is false for the horizontal layout this replaced.
    const bottoms = Array.from(container.querySelectorAll(".recharts-rectangle")).map(
      (bar) => Number(bar.getAttribute("y")) + Number(bar.getAttribute("height")),
    );
    for (const bottom of bottoms) {
      expect(bottom).toBeCloseTo(bottoms[0]!, 1);
    }
  });

  it("fills every bar with the palette's first slot — one series, one hue", () => {
    const { container } = render(<CategoryBarChart series={genderSeries()} />);
    const bars = container.querySelectorAll(".recharts-rectangle");
    bars.forEach((bar) => {
      expect(bar.getAttribute("fill")).toBe(CHART_PALETTE[0]);
    });
  });

  it("shows no legend for a single series (dataviz skill: the title names it)", () => {
    const { container } = render(<CategoryBarChart series={genderSeries()} />);
    expect(container.querySelector("ul")).toBeNull();
  });

  it("is hidden from assistive technology and out of the tab order", () => {
    // The adjacent DistributionChart table is the accessible content for this same
    // data — see this file's header comment for why a second image landmark would be
    // a duplicate announcement rather than new information.
    const { container } = render(<CategoryBarChart series={genderSeries()} />);
    const wrapper = container.firstElementChild;
    expect(wrapper?.getAttribute("aria-hidden")).toBe("true");
    expect(container.querySelectorAll('[tabindex="0"]')).toHaveLength(0);
  });

  it("marks the figure for the print stylesheet", () => {
    const { container } = render(<CategoryBarChart series={genderSeries()} />);
    expect(container.querySelector('[data-print="chart"]')).not.toBeNull();
  });
});

describe("CompositionPieChart", () => {
  it("draws one slice per category, coloured in the fixed palette order", () => {
    const series = applicantTypeSeries();
    const { container } = render(<CompositionPieChart series={series} />);
    const slices = container.querySelectorAll(".recharts-sector");
    expect(slices).toHaveLength(series.rows.length);
    slices.forEach((slice, index) => {
      expect(slice.getAttribute("fill")).toBe(CHART_PALETTE[index]);
    });
  });

  it("shows a legend naming every category — three slices need identity, not colour alone", () => {
    const series = applicantTypeSeries();
    const { container } = render(<CompositionPieChart series={series} />);
    const legendText = container.querySelector("ul")?.textContent ?? "";
    for (const row of series.rows) {
      expect(legendText).toContain(row.label);
    }
  });

  it("is hidden from assistive technology and out of the tab order", () => {
    const { container } = render(<CompositionPieChart series={applicantTypeSeries()} />);
    const wrapper = container.firstElementChild;
    expect(wrapper?.getAttribute("aria-hidden")).toBe("true");
    expect(container.querySelectorAll('[tabindex="0"]')).toHaveLength(0);
  });
});

describe("WellbeingComparisonChart — one group per question (reviewer item 7)", () => {
  // Every one of the six agreement-response categories carries a non-null percentage for
  // BOTH questions, so the "one bar per series per row" assertion below is unambiguous.
  // `domain/charts.test.ts` already covers the sparser, more realistic case — a category one
  // question did not report — as a pure data assertion; a null value renders no shape at all,
  // which would only muddy this DOM test's bar count.
  const wellbeing: WellbeingLastYear = {
    questions: [
      {
        column: "rev_wellbeinganswer8",
        population: 400,
        categories: [1, 2, 3, 4, 5, 6].map((value) => ({
          value,
          count: 10 + value,
          percentage: 10 + value,
        })),
      },
      {
        column: "rev_wellbeinganswer9",
        population: 380,
        categories: [1, 2, 3, 4, 5, 6].map((value) => ({
          value,
          count: 20 + value,
          percentage: 5 + value,
        })),
      },
      {
        column: "rev_wellbeinganswer10",
        population: 390,
        categories: [1, 2, 3, 4, 5, 6].map((value) => ({
          value,
          count: 30 + value,
          percentage: 8 + value,
        })),
      },
    ],
  };

  it("draws one bar GROUP per question and one bar per response category within it", () => {
    // The transposed shape the reviewer asked for: three vertical-bar groups, one per
    // question, each showing its answer-label percentages. One <g class="recharts-bar"> layer
    // per SERIES (response category) now, each contributing one bar to every question group.
    const data = buildWellbeingComparisonData(wellbeing);
    if (data === null) throw new Error("expected comparison data");
    expect(data.rows).toHaveLength(3);
    expect(data.series).toHaveLength(6);
    const { container } = render(<WellbeingComparisonChart data={data} />);
    expect(container.querySelectorAll(".recharts-bar")).toHaveLength(data.series.length);
    expect(container.querySelectorAll(".recharts-rectangle")).toHaveLength(
      data.series.length * data.rows.length,
    );
  });

  it("puts the three QUESTIONS on the category axis, not the response labels", () => {
    // The axis that proves the pivot actually turned over. Before Revision 8 this axis
    // carried "Strongly Disagree"… and the questions were the series.
    const data = buildWellbeingComparisonData(wellbeing);
    if (data === null) throw new Error("expected comparison data");
    const { container } = render(<WellbeingComparisonChart data={data} />);
    const labels = axisTickLabels(container);
    expect(labels).toContain("Wellbeing question 8, last year");
    expect(labels).toContain("Wellbeing question 9, last year");
    expect(labels).toContain("Wellbeing question 10, last year");
    // The response categories moved OFF this axis and onto the legend, which is what the
    // transpose means. The legend is a `<ul>`, not an SVG `<text>`, so it is not in this set.
    expect(labels).not.toContain("Strongly Disagree");
    expect(container.querySelector("ul")?.textContent).toContain("Strongly Disagree");
  });

  it("colours each response category by its POSITION on the scale, not the categorical palette", () => {
    // The ordinal ramp, not `CHART_PALETTE`. Painting a Likert scale with three wrapped
    // categorical hues would give "Strongly Disagree" and "Agree" the same magenta.
    const data = buildWellbeingComparisonData(wellbeing);
    if (data === null) throw new Error("expected comparison data");
    const { container } = render(<WellbeingComparisonChart data={data} />);
    const layers = container.querySelectorAll(".recharts-bar");
    layers.forEach((layer, index) => {
      const series = data.series[index]!;
      const bar = layer.querySelector(".recharts-rectangle");
      expect(bar?.getAttribute("fill")).toBe(agreementResponseColor(series.value));
    });
    // Explicitly NOT the categorical palette — the assertion this replaced.
    const firstBar = layers[0]?.querySelector(".recharts-rectangle");
    expect(firstBar?.getAttribute("fill")).not.toBe(CHART_PALETTE[0]);
  });

  it("renders 'Not sure' as a real sixth bar, in the off-scale neutral", () => {
    // Ground truth chart5 carries real counts for this option, so it must be drawn — and it
    // must not be drawn as a sixth step past "Strongly Agree".
    const data = buildWellbeingComparisonData(wellbeing);
    if (data === null) throw new Error("expected comparison data");
    const { container } = render(<WellbeingComparisonChart data={data} />);
    const notSureIndex = data.series.findIndex((series) => series.heading === "Not sure");
    expect(notSureIndex).toBe(5);
    const layer = container.querySelectorAll(".recharts-bar")[notSureIndex];
    const bars = layer?.querySelectorAll(".recharts-rectangle") ?? [];
    expect(bars).toHaveLength(data.rows.length);
    bars.forEach((bar) => {
      expect(bar.getAttribute("fill")).toBe(AGREEMENT_OFFSCALE_COLOR);
    });
  });

  it("shows a legend naming every response category — colour is never the only carrier", () => {
    // WCAG 1.4.1. The off-scale status of "Not sure" is carried by the legend's own words,
    // not by its grey alone.
    const data = buildWellbeingComparisonData(wellbeing);
    if (data === null) throw new Error("expected comparison data");
    const { container } = render(<WellbeingComparisonChart data={data} />);
    const legendText = container.querySelector("ul")?.textContent ?? "";
    for (const series of data.series) {
      expect(legendText).toContain(series.heading);
    }
    expect(legendText).toContain("Not sure");
  });

  it("is hidden from assistive technology and out of the tab order", () => {
    const data = buildWellbeingComparisonData(wellbeing);
    if (data === null) throw new Error("expected comparison data");
    const { container } = render(<WellbeingComparisonChart data={data} />);
    const wrapper = container.firstElementChild;
    expect(wrapper?.getAttribute("aria-hidden")).toBe("true");
    expect(container.querySelectorAll('[tabindex="0"]')).toHaveLength(0);
  });
});

describe("wrapTickLabel — the only place a category label can lose a character", () => {
  it("keeps a short label on one line", () => {
    expect(wrapTickLabel("Female")).toEqual(["Female"]);
  });

  it("wraps a long option label across lines without losing a word", () => {
    // APPLICANT_TYPE_LABELS' longest, verbatim from the option set.
    const label = "A carer applying on behalf of a disabled person";
    const lines = wrapTickLabel(label);
    expect(lines.length).toBeGreaterThan(1);
    expect(lines.join(" ")).toBe(label);
  });

  it("never breaks a word mid-way, even one longer than the budget", () => {
    // Hyphenating a category name would invent a word that is not the category's name.
    const lines = wrapTickLabel("Supercalifragilisticexpialidocious", 10, 3);
    expect(lines).toEqual(["Supercalifragilisticexpialidocious"]);
  });

  it("ellipsises rather than silently truncating, past the line budget", () => {
    const lines = wrapTickLabel("one two three four five six seven eight nine ten", 8, 2);
    expect(lines).toHaveLength(2);
    expect(lines[1]).toMatch(/…$/);
  });

  it("returns no lines for an empty label, rather than one empty tspan", () => {
    expect(wrapTickLabel("")).toEqual([]);
    expect(wrapTickLabel("   ")).toEqual([]);
  });
});
