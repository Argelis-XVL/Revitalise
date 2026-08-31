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

/**
 * `figures="share-only"` — Revision 8 (wbs:6.9), the reviewer's "drop the raw-count tables
 * under 'Who applied in this round'".
 *
 * The point of these tests is the BOUNDARY of that instruction. What is removed is one column
 * of numbers and one redundant picture; what is NOT removed is the table's accessible
 * structure, the denominator, or the rule that a null renders as words.
 */
describe("DistributionChart — figures=\"share-only\"", () => {
  it("drops the count column, keeping category and share", () => {
    render(<DistributionChart title="Gender" series={series()} figures="share-only" />);
    expect(screen.queryByRole("columnheader", { name: "Applications" })).not.toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Category" })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Share of round" })).toBeInTheDocument();
  });

  it("drops its own count-scaled bars, which the removed column can no longer be checked against", () => {
    // ADR-029's rule runs both ways: "every value it depicts is text in the table beside it".
    // A count-scaled bar beside a table with no count column depicts a quantity the reader
    // cannot check. The `visual` slot's Recharts chart is the percentage-scaled replacement.
    const { container } = render(
      <DistributionChart title="Gender" series={series()} figures="share-only" />,
    );
    expect(container.querySelector('[role="img"]')).toBeNull();
    expect(container.querySelector("svg")).toBeNull();
  });

  it("KEEPS the table as real, structured accessible content", () => {
    // The table is still what satisfies WCAG 1.1.1 and 1.3.1 for this data — this mode
    // removes a column, not the text alternative.
    render(<DistributionChart title="Gender" series={series()} figures="share-only" />);
    expect(screen.getByRole("rowheader", { name: "Female" })).toBeInTheDocument();
    expect(screen.getByRole("rowheader", { name: "Male" })).toBeInTheDocument();
    expect(screen.getByRole("table")).toBeInTheDocument();
  });

  it("KEEPS the denominator on the page (TAD §3.3 point 1)", () => {
    // "A percentage whose denominator is not on the page is not auditable" — which is the
    // whole reason a share-only table is allowed to exist.
    const { container } = render(
      <DistributionChart title="Gender" series={series()} figures="share-only" />,
    );
    expect(container.textContent).toContain("Counted over 434 applications in this round");
  });

  it("KEEPS a null share as words, never as 0%", () => {
    const withNull = buildSeries(
      {
        population: 434,
        categories: [
          { value: 1, count: 260, percentage: 59.9 },
          { value: 2, count: 150, percentage: null },
        ],
      },
      APPLICANT_GENDER_LABELS,
    );
    if (withNull === null) throw new Error("expected a series");
    const { container } = render(
      <DistributionChart title="Gender" series={withNull} figures="share-only" />,
    );
    expect(container.textContent).toContain("Not recorded");
    expect(container.textContent).not.toContain("0%");
  });

  it("still describes itself in its caption, without naming a column it no longer has", () => {
    const { container } = render(
      <DistributionChart title="Gender" series={series()} figures="share-only" />,
    );
    const caption = container.querySelector("caption")?.textContent ?? "";
    expect(caption).toContain("Share of the round, by category");
    expect(caption).not.toContain("Applications and");
  });

  it("leaves the default mode completely unchanged", () => {
    // The mode is additive. Every other call site on the screen still gets three columns and
    // the `role="img"` chart, byte-for-byte as before.
    const { container } = render(<DistributionChart title="Gender" series={series()} />);
    expect(container.querySelectorAll("thead th")).toHaveLength(3);
    expect(container.querySelector('[role="img"]')).not.toBeNull();
  });
});
