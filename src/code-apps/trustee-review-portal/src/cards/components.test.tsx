/**
 * The card app's round hero, group hero, pills and chart shapes (presentation). What they must
 * keep is asserted here; what the contract tests already hold (headings by name, the calendar
 * text, the "Members" fact once, the table as the accessible content) is not repeated.
 */
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RoundHero } from "./RoundHero";
import { GroupHero } from "./GroupHero";
import { ScoreChip, StatusPill } from "./pills";
import { ColumnChart, DonutChart, GroupedColumnChart } from "./charts";
import { makeRoundFinance, makeSummary } from "../test/harness";
import type { Series } from "../domain/landing";

const SERIES: Series = {
  population: 48,
  maxCount: 10,
  rows: [
    { value: 1, label: "Under 18", count: 1, percentage: 2.1 },
    { value: 2, label: "18 to 24", count: 10, percentage: 20.8 },
    { value: 3, label: "Not known", count: 0, percentage: 0 },
  ],
};

describe("RoundHero (WI-0081)", () => {
  it("keeps 'This round' as the accessible heading while the sentence is visible", () => {
    render(<RoundHero round={makeRoundFinance({ roundClosedOn: "2026-08-31T00:00:00Z" })} received={48} history={{ priorApplicationCount: 715, understatedTotal: false }} />);
    const heading = screen.getByRole("heading", { level: 2 });
    expect(heading).toHaveAccessibleName("This round");
    expect(heading.querySelector('[aria-hidden="true"]')?.textContent).toMatch(/^Open from 1 Aug/);
  });

  it("shows the plain heading when there is no open date", () => {
    render(<RoundHero round={makeRoundFinance({ roundOpenedOn: null })} received={null} history={null} />);
    expect(screen.getByRole("heading", { level: 2 }).textContent).toBe("This round");
  });

  it("draws the share bar at n / (n + p), aria-hidden, with the figures as text", () => {
    const { container } = render(<RoundHero round={makeRoundFinance()} received={48} history={{ priorApplicationCount: 715, understatedTotal: false }} />);
    const fill = container.querySelector("[data-share]") as HTMLElement;
    expect(Number(fill.getAttribute("data-share"))).toBeCloseTo(48 / 763, 6);
    expect(fill.parentElement).toHaveAttribute("aria-hidden", "true");
    expect(screen.getByText("All applications: 763, including 715 from before the portal")).toBeInTheDocument();
  });

  it("shows the round key in the badge as the Round fact", () => {
    render(<RoundHero round={makeRoundFinance()} received={null} history={null} />);
    expect(screen.getByText("Round").nextElementSibling).toHaveTextContent("2026-Q4");
  });
});

describe("GroupHero (WI-0097)", () => {
  const group = {
    code: "GRP-014",
    memberCount: 3,
    totalRequested: 2750,
    sharedStart: null,
    sharedEnd: null,
    members: [makeSummary()],
  };

  it("keeps 'Group summary' as the accessible heading and shows the total sentence", () => {
    render(<GroupHero group={group} />);
    const heading = screen.getByRole("heading", { level: 2 });
    expect(heading).toHaveAccessibleName("Group summary");
    expect(heading).toHaveTextContent("£2,750.00 requested together");
  });

  it("shows the plain heading when the total is null", () => {
    render(<GroupHero group={{ ...group, totalRequested: null }} />);
    expect(screen.getByRole("heading", { level: 2 }).textContent).toBe("Group summary");
  });

  it("states each of the four facts exactly once, the badge being the Members fact", () => {
    render(<GroupHero group={group} />);
    for (const label of ["Group code", "Members", "Group total requested", "Shared dates"]) {
      expect(screen.getAllByText(label)).toHaveLength(1);
      expect(screen.getByText(label).tagName).toBe("DT");
    }
  });
});

describe("pills (WI-0094)", () => {
  it("names the status in words and tones it by value", () => {
    render(<StatusPill status={3} />);
    const pill = screen.getByText("Borderline");
    expect(pill).toHaveAttribute("data-tone", "borderline");
  });

  it("shows the score as text beside an aria-hidden bar, and 'Not scored' for none", () => {
    const { container, unmount } = render(<ScoreChip score={42} />);
    expect(screen.getByText("42")).toBeInTheDocument();
    expect((container.querySelector('[aria-hidden="true"] span') as HTMLElement).style.width).toBe("70%");
    unmount();
    render(<ScoreChip score={null} />);
    expect(screen.getByText("Not scored")).toBeInTheDocument();
  });
});

describe("chart shapes (WI-0086..WI-0088)", () => {
  it("columns: one mark per category, heights over the largest value, aria-hidden, no SVG", () => {
    const { container } = render(<ColumnChart series={SERIES} />);
    const marks = Array.from(container.querySelectorAll<HTMLElement>("[data-chart-mark]"));
    expect(marks).toHaveLength(3);
    expect(marks[1]?.style.height).toBe("100%");
    expect(marks[2]?.getAttribute("data-empty")).toBe("true");
    expect(container.firstElementChild).toHaveAttribute("aria-hidden", "true");
    expect(container.querySelector("svg")).toBeNull();
  });

  it("grouped columns: one mark per category and series, legend in the series' own wording", () => {
    const data = {
      series: [
        { key: "rev_wellbeinganswer8", heading: "Go out and do something you enjoy" },
        { key: "rev_wellbeinganswer9", heading: "Enjoy other people’s company" },
      ],
      rows: [
        { value: 1, label: "Disagree", rev_wellbeinganswer8: 25, rev_wellbeinganswer9: 50 },
        { value: 2, label: "Agree", rev_wellbeinganswer8: 75, rev_wellbeinganswer9: null },
      ],
    };
    const { container } = render(<GroupedColumnChart data={data} />);
    expect(container.querySelectorAll("[data-chart-mark]")).toHaveLength(4);
    expect(screen.getByText("Go out and do something you enjoy")).toBeInTheDocument();
    expect(container.textContent).not.toMatch(/Question \d/);
  });

  it("donut: the population in the centre and share-only legend rows", () => {
    render(<DonutChart series={SERIES} />);
    expect(screen.getByText("48")).toBeInTheDocument();
    expect(screen.getByText("20.8%")).toBeInTheDocument();
    expect(screen.queryByText("10")).toBeNull();
  });
});
