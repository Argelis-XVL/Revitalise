/**
 * A distribution's table and its chart — ADR-029, TAD §8.1.
 *
 * The assertion that carries the decision is the last one in the first block: every bar's
 * width is derived from the same row the table cell rendered, so the chart and the table
 * cannot disagree. Everything else here is the accessibility contract ADR-029 chose the
 * table-first shape in order to meet properly.
 */
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
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

/**
 * Revision 9 (2026-09-01, wbs:6.9) — reviewer item 1, "only the chart itself should be shown,
 * not the underlying data in tabular form".
 *
 * THE POINT OF THESE TESTS IS WHAT THE INSTRUCTION DID *NOT* AUTHORISE. Taken literally it
 * deletes the text alternative (WCAG 1.1.1) and the structured relationships (1.3.1) this
 * component exists to provide — see this component's Revision 9 header. What ships instead
 * moves the table off screen with `.srOnly` and offers a disclosure, so the accessibility tree
 * is UNCHANGED and only the pixels differ. Every assertion below is written to fail if a later
 * edit "simplifies" that into an actual removal, or into a `<details>` (which would take the
 * table out of the accessibility tree while collapsed).
 */
describe("DistributionChart — reviewer item 1, the data table is hidden, never removed", () => {
  it("still renders the whole table, in both modes, before anything is clicked", () => {
    for (const figures of ["count-and-share", "share-only"] as const) {
      const view = render(
        <DistributionChart title="Gender" series={series()} figures={figures} />,
      );
      // Queried by ROLE, which is the accessibility tree — the table is exposed to a screen
      // reader with no interaction at all, exactly as it was before this revision.
      expect(view.getByRole("table")).toBeInTheDocument();
      expect(view.getByRole("rowheader", { name: "Female" })).toBeInTheDocument();
      expect(view.getByRole("columnheader", { name: "Share of round" })).toBeInTheDocument();
      view.unmount();
    }
  });

  it("offers a disclosure whose state is announced, not inferred from its label", () => {
    render(<DistributionChart title="Gender" series={series()} />);
    const toggle = screen.getByRole("button", { name: /show the data table/i });
    // WCAG 4.1.2 — a control that changes what is on screen states its own state.
    expect(toggle).toHaveAttribute("aria-expanded", "false");
    const controlled = toggle.getAttribute("aria-controls");
    expect(controlled).not.toBeNull();
    expect(document.getElementById(controlled ?? "")).not.toBeNull();
  });

  it("brings the table on screen and back off again", async () => {
    render(<DistributionChart title="Gender" series={series()} />);
    const toggle = screen.getByRole("button", { name: /show the data table/i });
    const region = document.getElementById(toggle.getAttribute("aria-controls") ?? "");
    // The visually-hidden class is applied to the wrapper, not to the table: the DOM is the
    // same either way, which is the property that makes this a purely visual toggle.
    expect(region?.className).toContain("srOnly");

    await userEvent.click(toggle);
    expect(screen.getByRole("button", { name: /hide the data table/i })).toHaveAttribute(
      "aria-expanded",
      "true",
    );
    expect(region?.className).not.toContain("srOnly");
    expect(screen.getByRole("table")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /hide the data table/i }));
    expect(region?.className).toContain("srOnly");
    expect(screen.getByRole("table")).toBeInTheDocument();
  });

  it("marks the table for the print stylesheet, so a board pack is never pictures alone", () => {
    // print.css un-hides `[data-print="datatable"]` with `!important` whatever the toggle
    // says — the printed pack is the durable record of what a board saw (TAD §6.4).
    const { container } = render(<DistributionChart title="Gender" series={series()} />);
    const printed = container.querySelector('[data-print="datatable"]');
    expect(printed).not.toBeNull();
    expect(printed?.querySelector("table")).not.toBeNull();
    // And the control itself does not print.
    expect(
      screen.getByRole("button", { name: /show the data table/i }).getAttribute("data-print"),
    ).toBe("hide");
  });

  it("does not leave an empty grid column where the hidden table used to sit", () => {
    // `.srOnly` is `position: absolute`, so a two-column table-beside-chart grid would
    // reserve a track for an out-of-flow item and push the chart into the second column.
    // The collapsed state uses the single-column layout instead.
    const { container } = render(<DistributionChart title="Gender" series={series()} />);
    const layout = container.querySelector('[data-print="datatable"]')?.parentElement;
    expect(layout?.className).toContain("chartLayoutStacked");
  });
});

/**
 * Revision 11 (2026-09-02, wbs:6.8) — reviewer item 3, "a stray pink bar renders under the
 * 'Show the data table' link beneath the Life Satisfaction chart".
 *
 * THE FIRST TEST IN THIS BLOCK IS THE ONE THAT REPRODUCES IT. Before the fix, a call site
 * passing BOTH a `visual` and the default `figures="count-and-share"` — which is exactly what
 * `RoundStatistics.tsx`'s Life Satisfaction block does — rendered the supplied picture AND this
 * component's own count-scaled `.chartBar` SVG of the same array. With the table clipped to
 * `.srOnly` since Revision 9, that second picture stood alone under the toggle and read as a
 * loose magenta bar. No test in this file passed a `visual` before now, which is why nothing
 * caught it: the slot's own doc comment said so in as many words.
 *
 * The boundary these hold is the same one `share-only`'s block holds: what is withdrawn is a
 * redundant PICTURE, never the text alternative.
 */
describe("DistributionChart — reviewer item 3, a supplied visual is the only picture", () => {
  const visual = <div data-testid="supplied-visual" />;

  it("draws no bars of its own when a visual is supplied, in the DEFAULT count mode", () => {
    const { container } = render(
      <DistributionChart title="Life satisfaction, 0 to 10" series={series()} visual={visual} />,
    );
    expect(screen.getByTestId("supplied-visual")).toBeInTheDocument();
    // The stray bar itself, and the `role="img"` that summarised it — one dataset, one picture.
    expect(container.querySelector(".chartBar, svg")).toBeNull();
    expect(container.querySelector('[role="img"]')).toBeNull();
  });

  it("keeps drawing its own bars when NO visual is supplied", () => {
    // The withdrawal is keyed on the `visual`, not on the mode — so every call site that does
    // not supply one is untouched, which is most of them.
    const { container } = render(<DistributionChart title="Gender" series={series()} />);
    expect(container.querySelectorAll("svg rect")).toHaveLength(series().rows.length);
    expect(container.querySelector('[role="img"]')).not.toBeNull();
  });

  it("keeps the table, the counts and the denominator — only the duplicate picture goes", () => {
    // ADR-029: the table is the content. This mode removes a second rendering of it, not the
    // text alternative, so the accessibility tree is what it was.
    render(
      <DistributionChart
        title="Life satisfaction, 0 to 10"
        series={series()}
        countHeading="Responses"
        visual={visual}
      />,
    );
    expect(screen.getByRole("table")).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Responses" })).toBeInTheDocument();
    expect(screen.getByRole("rowheader", { name: "Female" })).toBeInTheDocument();
    expect(screen.getByText(/counted over 434 applications in this round/i)).toBeInTheDocument();
  });

  it("stacks rather than reserving an empty column for the chart it no longer draws", () => {
    const { container } = render(
      <DistributionChart title="Gender" series={series()} visual={visual} />,
    );
    const layout = container.querySelector('[data-print="datatable"]')?.parentElement;
    expect(layout?.className).toContain("chartLayoutStacked");
  });

  it("changes nothing about `share-only`, which already drew no bars", () => {
    const { container } = render(
      <DistributionChart
        title="Gender"
        series={series()}
        figures="share-only"
        visual={visual}
      />,
    );
    expect(screen.getByTestId("supplied-visual")).toBeInTheDocument();
    expect(container.querySelector('[role="img"]')).toBeNull();
    expect(screen.getByRole("table")).toBeInTheDocument();
    expect(screen.queryByRole("columnheader", { name: "Applications" })).not.toBeInTheDocument();
  });
});
