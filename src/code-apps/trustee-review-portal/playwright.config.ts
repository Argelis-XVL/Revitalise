import { defineConfig } from "@playwright/test";

/**
 * Real-Chromium config for `visual-harness.html` only.
 *
 * WHY THIS EXISTS: `RoundStatisticsCharts.test.tsx` runs under jsdom (`vitest.config.ts`),
 * which computes no SVG font-metric layout — no real glyph ascent, no `getBBox`. Three
 * findings against this exact file (IMP-0509, IMP-0577, IMP-0581, IMP-0584) were each a
 * symbolic "fix" that was self-consistent on paper and wrong on a rendered screen, because
 * nothing before this file could ask a real browser to measure anything. This config boots
 * a second, throwaway Vite entry (`visual-harness.html`, not `index.html` — never built by
 * `npm run build`, never referenced by `power.config.json`'s `buildPath`, so nothing here
 * ships) on a dedicated port and drives it with real Chromium.
 *
 * Run with `npm run test:visual` (see `package.json`). CI wiring: add the same script as a
 * step after `npm test` in this app's pipeline stage — it needs `npx playwright install
 * chromium` once per runner image, which `test:visual:install` below does.
 */
export default defineConfig({
  testDir: "./src/test/visual",
  timeout: 30_000,
  fullyParallel: false,
  reporter: [["list"]],
  use: {
    baseURL: "http://localhost:4173",
    screenshot: "only-on-failure",
  },
  webServer: {
    // `vite preview` on the PRODUCTION-shaped bundle would need `visual-harness.html` added
    // as a rollup input, which is more moving parts than a throwaway harness earns; `vite`
    // (dev server) serves any `.html` file under root with no extra config and is what this
    // harness actually needs — real Chromium, real layout, no jsdom.
    command: "npx vite --port 4173 --strictPort",
    url: "http://localhost:4173/visual-harness.html",
    reuseExistingServer: !process.env.CI,
    timeout: 30_000,
  },
  projects: [{ name: "chromium", use: { browserName: "chromium" } }],
});
