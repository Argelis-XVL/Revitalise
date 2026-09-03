/**
 * REAL-BROWSER mount for `RoundStatisticsCharts` — Playwright only, never shipped.
 *
 * `visual-harness.html` is a second Vite entry (not referenced by `index.html`, not part of
 * `power.config.json`'s `buildPath`, and excluded from the production bundle budget check —
 * see `playwright.config.ts`'s own header) that boots exactly this file in a real Chromium tab.
 *
 * Why this exists at all: `RoundStatisticsCharts.test.tsx` runs under jsdom, which computes NO
 * SVG font-metric layout (no `getBBox`, no real glyph ascent/descent) — a fact this file's own
 * header states three times over (IMP-0509, IMP-0577, IMP-0581/IMP-0584). Every arithmetic
 * "fix" to the axis-tick gap has therefore been self-consistent on paper and wrong on a real
 * screen, twice. This harness renders the two chart components that carry the wrapped
 * category axis (`CategoryBarChart`, `WellbeingComparisonChart`) with fixed, deterministic
 * fixture data, so a real browser can be asked "how many pixels are actually between the plot
 * area's bottom edge and the first line of tick text" — the one question no vitest assertion in
 * this app can answer.
 *
 * Deliberately minimal: no `FluentProvider`, no query client, no repository. Both components
 * take plain `series`/`data` props (see `RoundStatisticsCharts.tsx`) and read no context, so
 * none of that machinery is needed to reproduce the defect.
 */
import { createRoot } from "react-dom/client";
import { CategoryBarChart, WellbeingComparisonChart } from "../components/RoundStatisticsCharts";
import { buildWellbeingComparisonData } from "../domain/charts";
import { buildSeries } from "../domain/landing";
import { APPLICANT_GENDER_LABELS } from "../dataverse/schema";
import type { Series } from "../domain/landing";
import type { WellbeingLastYear } from "../dataverse/types";

const genderSeries: Series | null = buildSeries(
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

const wellbeing: WellbeingLastYear = {
  questions: [
    {
      column: "rev_wellbeinganswer8",
      population: 400,
      categories: [
        { value: 1, count: 40, percentage: 10 },
        { value: 2, count: 60, percentage: 15 },
        { value: 3, count: 80, percentage: 20 },
        { value: 4, count: 120, percentage: 30 },
        { value: 5, count: 80, percentage: 20 },
        { value: 6, count: 20, percentage: 5 },
      ],
    },
    {
      column: "rev_wellbeinganswer9",
      population: 400,
      categories: [
        { value: 1, count: 20, percentage: 5 },
        { value: 2, count: 40, percentage: 10 },
        { value: 3, count: 100, percentage: 25 },
        { value: 4, count: 140, percentage: 35 },
        { value: 5, count: 80, percentage: 20 },
        { value: 6, count: 20, percentage: 5 },
      ],
    },
  ],
};

const wellbeingData = buildWellbeingComparisonData(wellbeing);

if (genderSeries === null || wellbeingData === null) {
  throw new Error("visual harness fixtures must build a real series — check the fixture data above");
}

const root = document.getElementById("root");
if (root === null) throw new Error("visual harness: #root missing");

createRoot(root).render(
  <div style={{ padding: 24, fontFamily: "sans-serif" }}>
    <h2 id="gender-heading">Gender (CategoryBarChart)</h2>
    <div id="gender-chart">
      <CategoryBarChart series={genderSeries} />
    </div>
    <h2 id="wellbeing-heading">Wellbeing (WellbeingComparisonChart)</h2>
    <div id="wellbeing-chart">
      <WellbeingComparisonChart data={wellbeingData} />
    </div>
    {/* A marker Playwright waits on so it never measures a chart mid-mount. */}
    <div data-testid="harness-ready">ready</div>
  </div>,
);
