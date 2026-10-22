/**
 * ADR-063's POSITIVE properties of the design's bars (card app only; presentation). The negative
 * half — no SVG rect or `.chartBar` drawn by `DistributionChart` — stays in the two contract WI-0053
 * tests, unchanged in both apps (TAD §13.6).
 */
import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CategoryBars } from "./CategoryBars";
import { DistributionChart } from "./DistributionChart";
import type { Series } from "../domain/landing";

const SERIES: Series = {
  population: 48,
  maxCount: 5,
  rows: [
    { value: 1, label: "Palliative care", count: 5, percentage: 10.4 },
    { value: 2, label: "Carer breakdown or urgent need", count: 4, percentage: 8.3 },
    { value: 3, label: "Severe financial hardship", count: 0, percentage: 0 },
  ],
};

function bars(container: HTMLElement) {
  return Array.from(container.querySelectorAll("li"));
}

describe("CategoryBars — ADR-063", () => {
  it("draws exactly one bar per series category, in series order", () => {
    const { container } = render(<CategoryBars series={SERIES} />);
    expect(bars(container).map((li) => li.getAttribute("data-category"))).toEqual(SERIES.rows.map((r) => r.label));
  });

  it("labels every bar with its category and '{count} · {share}' as visible text", () => {
    const { container } = render(<CategoryBars series={SERIES} />);
    const [first, , zero] = bars(container);
    expect(first).toHaveTextContent("Palliative care");
    expect(first).toHaveTextContent("5 · 10.4%");
    expect(zero).toHaveTextContent("Severe financial hardship");
    expect(zero).toHaveTextContent("0 · 0.0%");
  });

  it("sizes each fill as count over the largest count: the largest is 100%, a zero is 0%", () => {
    const { container } = render(<CategoryBars series={SERIES} />);
    const widths = bars(container).map((li) => (li.querySelector("[data-chart-mark]") as HTMLElement).style.width);
    expect(widths).toEqual(["100%", "80%", "0%"]);
  });

  it("puts no fill on screen without its label beside it", () => {
    const { container } = render(<CategoryBars series={SERIES} />);
    for (const li of bars(container)) {
      expect(li.querySelector("[data-chart-mark]")).not.toBeNull();
      expect(li.textContent?.trim().length).toBeGreaterThan(0);
    }
  });

  it("shows share only in share-only mode", () => {
    const { container } = render(<CategoryBars series={SERIES} figures="share-only" />);
    expect(bars(container)[0]).toHaveTextContent("10.4%");
    expect(bars(container)[0]).not.toHaveTextContent("5 ·");
  });

  it("is HTML, aria-hidden, and never SVG — the WI-0053 mechanism stays impossible", () => {
    const { container } = render(
      <DistributionChart title="Exceptional circumstance cited" series={SERIES} alwaysShowTable visual={<CategoryBars series={SERIES} />} />,
    );
    const block = screen.getByRole("heading", { level: 3 }).closest("section") as HTMLElement;
    expect(block.querySelector("svg, rect, .chartBar")).toBeNull();
    expect(container.querySelector("ul")).toHaveAttribute("aria-hidden", "true");
    // The table is still there, always visible, and is the accessible content.
    expect(within(block).getByRole("table")).toBeInTheDocument();
  });
});
