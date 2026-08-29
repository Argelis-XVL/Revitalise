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
} from "./RoundStatisticsCharts";
import { buildWellbeingComparisonData, CHART_PALETTE } from "../domain/charts";
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

describe("CategoryBarChart", () => {
  it("draws one bar for every category in the series", () => {
    const series = genderSeries();
    const { container } = render(<CategoryBarChart series={series} />);
    const bars = container.querySelectorAll(".recharts-rectangle");
    expect(bars).toHaveLength(series.rows.length);
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

describe("WellbeingComparisonChart", () => {
  // Every one of the six agreement-response categories carries a non-zero count for
  // BOTH questions, so the "one bar per category per series" assertion below is
  // unambiguous. `domain/charts.test.ts` already covers the sparser, more realistic
  // case — a category one question did not report — as a pure data assertion; a
  // zero-valued bar renders no shape at all, which would only muddy this DOM test's
  // bar count without adding coverage the pure test does not already have.
  const wellbeing: WellbeingLastYear = {
    questions: [
      {
        column: "rev_wellbeinganswer8",
        population: 400,
        categories: [1, 2, 3, 4, 5, 6].map((value) => ({ value, count: 10 + value, percentage: null })),
      },
      {
        column: "rev_wellbeinganswer9",
        population: 380,
        categories: [1, 2, 3, 4, 5, 6].map((value) => ({ value, count: 20 + value, percentage: null })),
      },
    ],
  };

  it("draws one bar series per question, on the shared agreement-response axis", () => {
    const data = buildWellbeingComparisonData(wellbeing);
    if (data === null) throw new Error("expected comparison data");
    const { container } = render(<WellbeingComparisonChart data={data} />);
    // One <g class="recharts-bar"> layer per series (question), each containing one
    // bar per category on the shared axis.
    const seriesLayers = container.querySelectorAll(".recharts-bar");
    expect(seriesLayers).toHaveLength(data.series.length);
    const bars = container.querySelectorAll(".recharts-rectangle");
    expect(bars).toHaveLength(data.series.length * data.rows.length);
  });

  it("colours each question's series in the fixed palette order", () => {
    const data = buildWellbeingComparisonData(wellbeing);
    if (data === null) throw new Error("expected comparison data");
    const { container } = render(<WellbeingComparisonChart data={data} />);
    const seriesLayers = container.querySelectorAll(".recharts-bar");
    seriesLayers.forEach((layer, index) => {
      const bar = layer.querySelector(".recharts-rectangle");
      expect(bar?.getAttribute("fill")).toBe(CHART_PALETTE[index]);
    });
  });

  it("shows a legend naming every question — two or more series is never colour-alone", () => {
    const data = buildWellbeingComparisonData(wellbeing);
    if (data === null) throw new Error("expected comparison data");
    const { container } = render(<WellbeingComparisonChart data={data} />);
    const legendText = container.querySelector("ul")?.textContent ?? "";
    for (const series of data.series) {
      expect(legendText).toContain(series.heading);
    }
  });

  it("shows no legend for a single question, same rule as any other single series", () => {
    const oneQuestion: WellbeingLastYear = {
      questions: [wellbeing.questions[0]!],
    };
    const data = buildWellbeingComparisonData(oneQuestion);
    if (data === null) throw new Error("expected comparison data");
    const { container } = render(<WellbeingComparisonChart data={data} />);
    expect(container.querySelector("ul")).toBeNull();
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
