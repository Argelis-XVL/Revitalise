/**
 * A distribution's table and its chart — ADR-029, TAD §8.1.
 *
 * The assertion that carries the decision is the last one in the first block: every bar's
 * width is derived from the same row the table cell rendered, so the chart and the table
 * cannot disagree. Everything else here is the accessibility contract ADR-029 chose the
 * table-first shape in order to meet properly.
 */
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DistributionChart } from "./DistributionChart";
import { buildSeries } from "../domain/landing";
import type { Series } from "../domain/landing";
import { APPLICANT_GENDER_LABELS } from "../dataverse/schema";

function series(): Series {
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

describe("DistributionChart — the table is the content", () => {
  it("renders every category as a row header with its count and share", () => {
    render(<DistributionChart title="Gender" series={series()} />);
    const female = screen.getByRole("rowheader", { name: "Female" });
    const row = female.closest("tr");
    expect(row).not.toBeNull();
    expect(row?.textContent).toContain("260");
    expect(row?.textContent).toContain("59.9%");
  });

  it("puts the denominator on the page beside the percentages (TAD §3.3 point 1)", () => {
    render(<DistributionChart title="Gender" series={series()} />);
    expect(screen.getByText(/counted over 434 applications in this round/i)).toBeInTheDocument();
  });

  it("says so when the response carried no denominator, rather than showing bare percentages", () => {
    const built = buildSeries(
      { population: null, categories: [{ value: 1, count: 3, percentage: null }] },
      APPLICANT_GENDER_LABELS,
    );
    if (built === null) throw new Error("expected a series");
    render(<DistributionChart title="Gender" series={built} />);
    expect(screen.getByText(/was not reported/i)).toBeInTheDocument();
  });

  it("renders a missing percentage as words, never as 0%", () => {
    const built = buildSeries(
      { population: 10, categories: [{ value: 1, count: 3, percentage: null }] },
      APPLICANT_GENDER_LABELS,
    );
    if (built === null) throw new Error("expected a series");
    render(<DistributionChart title="Gender" series={built} />);
    // 3 of 10 is plainly 30%, and the response did not say so. A 0% here would be a
    // fabricated figure; "Not recorded" is the fact.
    expect(screen.getByText("Not recorded")).toBeInTheDocument();
  });

  it("draws one bar per row, scaled from the SAME array the table rendered", () => {
    const built = series();
    const { container } = render(<DistributionChart title="Gender" series={built} />);
    const bars = container.querySelectorAll("svg rect");
    expect(bars).toHaveLength(built.rows.length);
    // The chart and the table are two renderings of one array, so a bar's width is a pure
    // function of the count in the cell beside it. This is the property that makes a
    // chart/table disagreement structurally impossible rather than merely unlikely.
    built.rows.forEach((row, index) => {
      const expected = (row.count / built.maxCount) * 100;
      expect(Number(bars[index]?.getAttribute("width"))).toBeCloseTo(expected, 6);
    });
  });
});

describe("DistributionChart — accessibility", () => {
  it("marks the chart as an image with a summarising label, not a paraphrasing alt", () => {
    render(<DistributionChart title="Gender" series={series()} />);
    const chart = screen.getByRole("img");
    expect(chart.getAttribute("aria-label")).toContain("Bar chart: Gender");
    expect(chart.getAttribute("aria-label")).toContain("table beside this chart");
  });

  it("keeps the chart out of the tab order", () => {
    // An SVG is a tab stop in some engines, and a non-interactive graphic must not be one
    // (WCAG 2.4.3).
    render(<DistributionChart title="Gender" series={series()} />);
    expect(screen.getByRole("img").getAttribute("focusable")).toBe("false");
  });

  it("gives the section its own heading, beneath the panel's h2", () => {
    render(<DistributionChart title="Gender" series={series()} />);
    const heading = screen.getByRole("heading", { level: 3, name: "Gender" });
    // The section is a labelled region rather than a div, which is what makes the heading
    // structural (WCAG 1.3.1).
    expect(heading.closest("section")?.getAttribute("aria-labelledby")).toBe(heading.id);
  });

  it("carries every value as text, so colour is never the only carrier (WCAG 1.4.1)", () => {
    const { container } = render(<DistributionChart title="Gender" series={series()} />);
    for (const cell of ["260", "150", "24"]) {
      expect(container.textContent).toContain(cell);
    }
  });

  it("names what the count column counts, so a response count is not read as an application count", () => {
    render(
      <DistributionChart title="Wellbeing question 8" series={series()} countHeading="Responses" />,
    );
    expect(screen.getByRole("columnheader", { name: "Responses" })).toBeInTheDocument();
  });

  it("marks the chart and the block for the print stylesheet (FR-039)", () => {
    const { container } = render(<DistributionChart title="Gender" series={series()} />);
    expect(container.querySelector('[data-print="chart"]')).not.toBeNull();
    expect(container.querySelector('[data-print="block"]')).not.toBeNull();
  });
});
