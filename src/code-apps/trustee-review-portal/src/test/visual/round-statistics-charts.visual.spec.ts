import { expect, test } from "@playwright/test";
import type { Page } from "@playwright/test";

/**
 * REAL-BROWSER assertion on the category-axis gap — the permanent test IMP-0584 asked for.
 *
 * `RoundStatisticsCharts.test.tsx` (vitest/jsdom) asserts the ARITHMETIC around
 * `CATEGORY_AXIS_HEIGHT`/`FIRST_TICK_LINE_DY`, and that arithmetic has been self-consistent
 * through three live-DEV rounds (IMP-0509, IMP-0577, IMP-0581) while the rendered gap was
 * wrong every time — because jsdom computes no SVG font-metric layout, so no jsdom assertion
 * can see what a real browser actually draws. This file is the missing half: it renders
 * `visual-harness.html` in real Chromium and reads `getBoundingClientRect()` off the actual
 * DOM, the same technique that found Revision 13's root cause (a Chromium behaviour where the
 * outer `<text>` element's `dy` is not honoured once its first child `<tspan>` declares its
 * own `dy`, even `0` — see `RoundStatisticsCharts.tsx`'s `WrappedCategoryTick` comment).
 *
 * Tolerance: the measured gap is glyph-bounding-box top to plot-bottom, which is generally
 * a few pixels MORE than `AXIS_LABEL_GAP` alone (a real font's internal leading sits above its
 * own ascent) — so this asserts "at least `AXIS_LABEL_GAP`, allowing headroom for internal
 * leading" rather than pinning an exact figure a font-metrics change would make brittle. What
 * it MUST catch: the pre-fix defect, where the measured gap was **-4px** (the label overlapped
 * the gridline) — so the floor below is set well above zero and nowhere near that regression.
 *
 * Run via `npm run test:visual` (`package.json`). Needs `npx playwright install chromium` once
 * per machine/CI runner (not run automatically by `npm install`).
 */

/** Reads the real pixel gap between a chart's plot-bottom and its first tick line's top. */
async function measureAxisGap(page: Page, chartId: string) {
  return page.evaluate((id) => {
    const chart = document.getElementById(id);
    if (!chart) throw new Error(`#${id} not found in the harness`);
    const plotLines = [...chart.querySelectorAll(".recharts-cartesian-grid-horizontal line")];
    const plotBottom = Math.max(...plotLines.map((line) => line.getBoundingClientRect().bottom));
    const firstTspans = [...chart.querySelectorAll("g[transform] > text tspan:first-child")];
    if (firstTspans.length === 0) throw new Error(`no wrapped category ticks found in #${id}`);
    const tops = firstTspans.map((tspan) => tspan.getBoundingClientRect().top);
    return { plotBottom, minGap: Math.min(...tops.map((top) => top - plotBottom)) };
  }, chartId);
}

test.describe("category axis tick gap — real Chromium measurement", () => {
  test("CategoryBarChart (gender) renders a real, positive gap above its first tick line", async ({
    page,
  }) => {
    await page.goto("/visual-harness.html");
    await page.waitForSelector('[data-testid="harness-ready"]');

    const { minGap } = await measureAxisGap(page, "gender-chart");

    // The defect this guards: -4px (measured against Revision 12's code, live in DEV a third
    // time). 12px is comfortably above that regression and a real margin below the ~23px this
    // fix currently renders at, so a future edit that reintroduces the "dy on the outer <text>
    // is silently dropped" shape fails this long before it reaches a rendered screen again.
    expect(minGap).toBeGreaterThanOrEqual(12);
  });

  test("WellbeingComparisonChart renders the same real, positive gap", async ({ page }) => {
    await page.goto("/visual-harness.html");
    await page.waitForSelector('[data-testid="harness-ready"]');

    const { minGap } = await measureAxisGap(page, "wellbeing-chart");

    expect(minGap).toBeGreaterThanOrEqual(12);
  });
});
