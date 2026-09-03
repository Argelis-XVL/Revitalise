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
  categoryAxisPlan,
  CategoryBarChart,
  CompositionPieChart,
  WellbeingComparisonChart,
  wrapTickLabel,
} from "./RoundStatisticsCharts";
import { buildWellbeingComparisonData, CHART_PALETTE } from "../domain/charts";
import { buildSeries } from "../domain/landing";
import type { Series } from "../domain/landing";
import {
  AGE_RANGE_LABELS,
  APPLICANT_GENDER_LABELS,
  APPLICANT_TYPE_LABELS,
  ETHNIC_GROUP_LABELS,
  LIFE_SATISFACTION_LABELS,
} from "../dataverse/schema";
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

describe("WellbeingComparisonChart — one group per response category (reviewer item 3, Revision 10)", () => {
  // Every one of the six agreement-response categories carries a non-null percentage for
  // every question, so the "one bar per series per row" assertion below is unambiguous.
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

  it("draws one bar GROUP per response category and EXACTLY THREE bars — one per question — within it (reviewer item 3)", () => {
    // The shape the reviewer asked for this round: six category groups, three bars each. One
    // <g class="recharts-bar"> layer per SERIES (question) now, each contributing one bar to
    // every category group.
    const data = buildWellbeingComparisonData(wellbeing);
    if (data === null) throw new Error("expected comparison data");
    expect(data.rows).toHaveLength(6);
    expect(data.series).toHaveLength(3);
    const { container } = render(<WellbeingComparisonChart data={data} />);
    expect(container.querySelectorAll(".recharts-bar")).toHaveLength(data.series.length);
    expect(container.querySelectorAll(".recharts-rectangle")).toHaveLength(
      data.series.length * data.rows.length,
    );
  });

  it("puts the six RESPONSE OPTIONS on the category axis, as their literal wording (reviewer item 3)", () => {
    // The axis that proves the pivot turned back over. Under Revision 8 this axis carried the
    // three question headings and the response options were the series/legend.
    const data = buildWellbeingComparisonData(wellbeing);
    if (data === null) throw new Error("expected comparison data");
    const { container } = render(<WellbeingComparisonChart data={data} />);
    const labels = axisTickLabels(container);
    expect(labels).toContain("Strongly Disagree");
    expect(labels).toContain("Disagree");
    expect(labels).toContain("Neutral");
    expect(labels).toContain("Agree");
    expect(labels).toContain("Strongly Agree");
    expect(labels).toContain("Not sure");
    // The questions moved OFF this axis and onto the legend. The legend is a `<ul>`, not an
    // SVG `<text>`, so it is not in this set.
    expect(labels).not.toContain("Wellbeing question 8, last year");
    expect(container.querySelector("ul")?.textContent).toContain("Wellbeing question 8, last year");
  });

  it("colours each question by the fixed categorical palette, in series order", () => {
    // A question is a plain identity here — not a point on an ordered scale, which is why
    // `CHART_PALETTE` (not an ordinal ramp) is correct for this axis assignment.
    const data = buildWellbeingComparisonData(wellbeing);
    if (data === null) throw new Error("expected comparison data");
    const { container } = render(<WellbeingComparisonChart data={data} />);
    const layers = container.querySelectorAll(".recharts-bar");
    layers.forEach((layer, index) => {
      const bar = layer.querySelector(".recharts-rectangle");
      expect(bar?.getAttribute("fill")).toBe(CHART_PALETTE[index]);
    });
  });

  it("renders 'Not sure' as a real sixth GROUP, never dropped", () => {
    // Ground truth chart5 carries real counts for this option, so it must be drawn.
    const data = buildWellbeingComparisonData(wellbeing);
    if (data === null) throw new Error("expected comparison data");
    const { container } = render(<WellbeingComparisonChart data={data} />);
    const notSureRowIndex = data.rows.findIndex((row) => row.label === "Not sure");
    expect(notSureRowIndex).toBe(5);
    const bars = container.querySelectorAll(".recharts-rectangle");
    // One bar per series lands in every group, "Not sure" included — the group count alone
    // (asserted above) already proves it is not silently dropped.
    expect(bars).toHaveLength(data.series.length * data.rows.length);
  });

  it("shows a legend naming every question — colour is never the only carrier", () => {
    // WCAG 1.4.1.
    const data = buildWellbeingComparisonData(wellbeing);
    if (data === null) throw new Error("expected comparison data");
    const { container } = render(<WellbeingComparisonChart data={data} />);
    const legendText = container.querySelector("ul")?.textContent ?? "";
    for (const series of data.series) {
      expect(legendText).toContain(series.heading);
    }
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

/**
 * Revision 9 (2026-09-01, wbs:6.9) — reviewer item 2, "chart label font size too small".
 *
 * WHAT THESE CAN AND CANNOT SEE. jsdom paints nothing, so no test in this repository can
 * observe the overlap `IMP-0509` describes; what CAN be asserted is the coupling that prevents
 * it — that the rendered glyph size and the line box the wrapped `<tspan>`s are spaced by moved
 * together, and that the axis reserved room for the result. That is the same assertion shape
 * `C-TECH-076` check A makes mechanically for CSS, applied to the SVG constants the gate cannot
 * reach because they are TypeScript numbers, not declarations.
 */
describe("Revision 9 item 2 — the tick type size, and everything coupled to it", () => {
  function categoryTicks(container: HTMLElement): SVGTextElement[] {
    // `WrappedCategoryTick` is the only <text> this file emits with an explicit fontSize.
    return [...container.querySelectorAll("g > text")] as unknown as SVGTextElement[];
  }

  it("renders category labels at the constant the whole file derives from (13px since Revision 11)", () => {
    const { container } = render(<CategoryBarChart series={genderSeries()} />);
    const ticks = categoryTicks(container);
    expect(ticks.length).toBeGreaterThan(0);
    for (const tick of ticks) {
      expect(tick.getAttribute("font-size")).toBe("13");
    }
  });

  it("spaces the wrapped lines by MORE than the glyph size (IMP-0509's actual defect)", () => {
    // The defect is not "the font is big"; it is "the line box is smaller than the glyphs".
    // A ratio below 1 overlaps; this asserts the ratio, so the test still holds if a later
    // revision changes the size again.
    const built = buildSeries(
      {
        population: 100,
        // Option 2 is "A carer applying on behalf of a disabled person" — 46 characters, the
        // longest label any option set in this app declares, and the one the wrap budget was
        // sized around. It occupies three <tspan> lines at 18 characters per line.
        categories: [{ value: 2, count: 100, percentage: 100 }],
      },
      APPLICANT_TYPE_LABELS,
    );
    if (built === null) throw new Error("expected a series");
    const { container } = render(<CategoryBarChart series={built} />);
    const tick = categoryTicks(container)[0];
    expect(tick).toBeDefined();
    const fontSize = Number(tick?.getAttribute("font-size"));
    const spans = [...(tick?.querySelectorAll("tspan") ?? [])];
    expect(spans.length).toBeGreaterThan(1);
    // Every line after the first is offset by the line box.
    for (const span of spans.slice(1)) {
      expect(Number(span.getAttribute("dy"))).toBeGreaterThan(fontSize);
    }
  });

  it("sets the value axis to the same size, so one axis is not left behind", () => {
    // Two hardcoded 12s in one file is how one of them gets missed; the Y axis takes its size
    // from the same constant now.
    const { container } = render(<CategoryBarChart series={genderSeries()} />);
    const percentTicks = [...container.querySelectorAll("text")].filter((node) =>
      /%$/.test(node.textContent ?? ""),
    );
    expect(percentTicks.length).toBeGreaterThan(0);
    for (const tick of percentTicks) {
      expect(tick.getAttribute("font-size")).toBe("13");
    }
  });

  it("keeps the 54-character wrap budget, so no label becomes newly ellipsised", () => {
    // The alternative fix — narrowing the character budget to hold the same pixel width —
    // would have pushed APPLICANT_TYPE_LABELS' 46-character option into the one lossy path
    // this file has. The chart was widened instead.
    expect(wrapTickLabel("a".repeat(17) + " " + "b".repeat(17) + " " + "c".repeat(17))).toHaveLength(3);
    const longest = Object.values(APPLICANT_TYPE_LABELS).reduce((a, b) =>
      a.length > b.length ? a : b,
    );
    expect(wrapTickLabel(longest).join(" ")).not.toContain("…");
  });
});

/**
 * Revision 10 (2026-09-02, wbs:6.8) — reviewer item 4, the root cause of overlapping x-axis
 * labels: a per-category column narrower than the wrap budget's own rendered width.
 *
 * jsdom computes no layout, so no test here can see two labels actually overlap on screen —
 * the same residual `IMP-0509`'s own tests state. What CAN be asserted is the ratio that
 * caused it: the chart's per-category column (its own computed `width` divided by category
 * count) must be at least as wide as one full wrapped line, at ANY reasonable estimate of a
 * glyph's pixel width — this fails at the OLD 85px figure for any label long enough to wrap,
 * and holds at the fixed derivation this revision introduces.
 */
describe("Revision 10 item 4 — the category column is wide enough to hold its own wrapped tick line", () => {
  it("CategoryBarChart's column stays wider than a conservative estimate of one wrapped line", () => {
    // APPLICANT_GENDER_LABELS' longest option, "Describes themselves another way" (33
    // characters), wraps across two lines at the 18-character budget — the exact shape that
    // overlapped its neighbour at the old 85px column width.
    const built = buildSeries(
      {
        population: 300,
        categories: [
          { value: 1, count: 100, percentage: 33.3 },
          { value: 2, count: 100, percentage: 33.3 },
          { value: 4, count: 100, percentage: 33.4 },
        ],
      },
      APPLICANT_GENDER_LABELS,
    );
    if (built === null) throw new Error("expected a series");
    const { container } = render(<CategoryBarChart series={built} />);
    const surface = container.querySelector(".recharts-surface");
    const chartWidth = Number(surface?.getAttribute("width"));
    const longestLine = wrapTickLabel("Describes themselves another way").reduce((a, b) =>
      a.length > b.length ? a : b,
    );
    // A DELIBERATELY LOW lower bound on glyph width (6px, below every realistic sans-serif
    // figure at 15px) — this only fails if the column shrinks back toward the old, too-narrow
    // 85px figure, not on any reasonable tightening of the real estimate.
    const conservativeLineWidthPx = longestLine.length * 6;
    expect(chartWidth / built.rows.length).toBeGreaterThan(conservativeLineWidthPx);
  });
});

/**
 * Revision 11 (2026-09-02, wbs:6.8) — reviewer items 1, 4 and 5.
 *
 * THE ONE THING THESE CAN SEE THAT THE REVISION 10 BLOCK ABOVE COULD NOT. Recharts computes its
 * own coordinates in JavaScript and writes them into the DOM as attributes, so a tick's baseline
 * and the plot area's lower edge are both readable in jsdom even though nothing is painted.
 * Item 5 is therefore asserted as real geometry — "the last wrapped line sits below the plot and
 * inside the SVG" — rather than as an arithmetic proxy. Items 1 and 4 stay arithmetic: a chart's
 * fit inside its GRID CELL depends on a container width only a browser resolves.
 */
describe("Revision 11 item 1 — every chart is fitted to a stated width budget", () => {
  /** The budget `RoundStatisticsCharts.tsx` states, restated here so a change to it fails. */
  const CHART_WIDTH_BUDGET = 620;

  function widthOf(ui: React.ReactElement): number {
    const { container } = render(ui);
    return Number(container.querySelector(".recharts-surface")?.getAttribute("width"));
  }

  function seriesFor(labels: Readonly<Record<number, string>>): Series {
    const built = buildSeries(
      {
        population: 100,
        categories: Object.keys(labels).map((key) => ({
          value: Number(key),
          count: 1,
          percentage: 1,
        })),
      },
      labels,
    );
    if (built === null) throw new Error("expected a series");
    return built;
  }

  it("keeps every option set this app declares inside the budget", () => {
    // The reviewer's finding was charts overflowing their box and scrolling sideways. These are
    // the four single-series distributions the round-overview screen draws, at their real
    // option-set sizes — nine age bands, six ethnic groups and eleven life-satisfaction scores
    // are the three that overflowed.
    for (const labels of [
      APPLICANT_GENDER_LABELS,
      AGE_RANGE_LABELS,
      ETHNIC_GROUP_LABELS,
      LIFE_SATISFACTION_LABELS,
    ]) {
      expect(widthOf(<CategoryBarChart series={seriesFor(labels)} />)).toBeLessThanOrEqual(
        CHART_WIDTH_BUDGET,
      );
    }
  });

  it("stops sizing a two-character axis for the app's longest label", () => {
    // THE ROOT CAUSE, as an assertion. Every chart used to take a column of
    // `TICK_CHARS_PER_LINE * TICK_GLYPH_WIDTH_PX` — a full 18-character line, 162px — including
    // LIFE_SATISFACTION_LABELS, whose labels are "0" to "10". Eleven such columns is 1782px.
    const width = widthOf(<CategoryBarChart series={seriesFor(LIFE_SATISFACTION_LABELS)} />);
    expect(width).toBeLessThan(11 * 162);
  });

  it("wraps a tick to the SAME budget the width was computed from", () => {
    // `IMP-0577`'s rule, in its current form: a column sized to one budget and a label wrapped
    // to another is the overlap defect with extra steps. `categoryAxisPlan` returns one figure
    // and both consumers take it, so the tightest wrap this app reaches is observable here.
    const plan = categoryAxisPlan(Object.values(ETHNIC_GROUP_LABELS), 44, 460);
    const { container } = render(<CategoryBarChart series={seriesFor(ETHNIC_GROUP_LABELS)} />);
    const lines = [...container.querySelectorAll("g[transform] > text tspan")].map(
      (span) => (span.textContent ?? "").length,
    );
    expect(lines.length).toBeGreaterThan(0);
    for (const length of lines) {
      expect(length).toBeLessThanOrEqual(plan.charsPerLine);
    }
  });

  it("loses no character of any label to the ellipsis branch at the tighter wrap", () => {
    // The cost of a tighter wrap is more lines, and TICK_MAX_LINES went 3 -> 4 to pay it. This
    // is what fails if a later edit takes that back: ETHNIC_GROUP_LABELS' longest option needs
    // four lines at the budget its own six-category chart resolves to.
    const plan = categoryAxisPlan(Object.values(ETHNIC_GROUP_LABELS), 44, 460);
    for (const label of Object.values(ETHNIC_GROUP_LABELS)) {
      expect(wrapTickLabel(label, plan.charsPerLine, 4).join(" ")).toBe(label);
    }
  });

  it("never returns a column narrower than the line it has to hold, budget or no budget", () => {
    // The budget is a budget, not a clamp: a label set long enough to blow it still gets a
    // column wide enough for its own text, and scrolls inside `.tableScroll`. Overflowing beats
    // overlapping — the failure direction IMP-0577 was raised about.
    const absurd = Array.from({ length: 40 }, (_, index) => `Category number ${String(index)}`);
    const plan = categoryAxisPlan(absurd, 44, 460);
    expect(plan.width).toBeGreaterThan(CHART_WIDTH_BUDGET);
    expect(plan.width / absurd.length).toBeGreaterThanOrEqual(44);
  });
});

describe("Revision 11 item 5 — the x-axis labels render below the plot area, inside the SVG", () => {
  it("puts every wrapped line under the plot's lower edge and above the SVG's own", () => {
    // THE DEFECT, AS GEOMETRY. `CATEGORY_AXIS_HEIGHT` was `lines * lineHeight + 20` and the
    // tick's own first-line `dy` already spent that 20, so the band reserved nothing for the
    // LAST line — which is what ran into the chart. Recharts writes both edges into the DOM as
    // attributes, so this is a real measurement rather than a proxy for one.
    const built = buildSeries(
      {
        population: 300,
        categories: [1, 2, 4].map((value) => ({ value, count: 100, percentage: 33.3 })),
      },
      APPLICANT_GENDER_LABELS,
    );
    if (built === null) throw new Error("expected a series");
    const { container } = render(<CategoryBarChart series={built} />);

    const surface = container.querySelector(".recharts-surface");
    const svgHeight = Number(surface?.getAttribute("height"));
    // The lowest horizontal grid line IS the plot area's lower edge.
    const plotBottom = Math.max(
      ...[...container.querySelectorAll(".recharts-cartesian-grid-horizontal line")].map((line) =>
        Number(line.getAttribute("y1")),
      ),
    );
    expect(plotBottom).toBeGreaterThan(0);

    // `g[transform] > text` is `WrappedCategoryTick`'s own shape — Recharts positions its own
    // axis ticks with `y` on the `<text>` and no group transform at all, so this selects the
    // category ticks and nothing else.
    const ticks = [...container.querySelectorAll("g[transform] > text")];
    expect(ticks).toHaveLength(built.rows.length);
    for (const tick of ticks) {
      const group = tick.parentElement;
      const translateY = Number(
        /translate\([^,]+,([^)]+)\)/.exec(group?.getAttribute("transform") ?? "")?.[1],
      );
      expect(translateY).not.toBeNaN();
      const first = Number(tick.getAttribute("dy"));
      const spans = [...tick.querySelectorAll("tspan")];
      const lastBaseline =
        translateY + first + spans.reduce((sum, span) => sum + Number(span.getAttribute("dy")), 0);
      // Below the plot: no label is drawn over the chart it labels.
      expect(translateY + first).toBeGreaterThanOrEqual(plotBottom);
      // And inside the box: the axis band reserved room for the descenders of the last line.
      expect(lastBaseline).toBeLessThan(svgHeight);
    }
  });
});

describe("Revision 11 item 4 — the pie's box is wide enough for its own data labels", () => {
  it("is wider than it is tall, because the labels are drawn outside the circle", () => {
    // On a square box the size of the circle's diameter, a label on the horizontal flank starts
    // outside `outerRadius` and runs off the edge — which is the clipping the reviewer saw.
    const { container } = render(<CompositionPieChart series={applicantTypeSeries()} />);
    const surface = container.querySelector(".recharts-surface");
    const width = Number(surface?.getAttribute("width"));
    const height = Number(surface?.getAttribute("height"));
    expect(width).toBeGreaterThan(height);
    // Room for the leader line plus a percentage label either side of a 100px radius.
    expect(width).toBeGreaterThanOrEqual(2 * (100 + 25 + 45));
  });

  it("scrolls that width inside its own box, never the page (WCAG 1.4.10)", () => {
    // A CORRECTION found while widening it: this file's header has always claimed every chart
    // "sits inside `styles.tableScroll`", and this one did not — so a fixed-width pie in a
    // narrower grid cell overflowed all the way out to the page body. Asserted for all three
    // chart components together, because the claim is about all three.
    const data = buildWellbeingComparisonData({
      questions: [
        {
          column: "rev_wellbeinganswer8",
          population: 100,
          categories: [1, 2, 3, 4, 5, 6].map((value) => ({ value, count: value, percentage: value })),
        },
      ],
    });
    if (data === null) throw new Error("expected comparison data");
    for (const ui of [
      <CategoryBarChart key="bar" series={genderSeries()} />,
      <CompositionPieChart key="pie" series={applicantTypeSeries()} />,
      <WellbeingComparisonChart key="cmp" data={data} />,
    ]) {
      const { container, unmount } = render(ui);
      expect(container.firstElementChild?.className).toContain("tableScroll");
      unmount();
    }
  });
});
