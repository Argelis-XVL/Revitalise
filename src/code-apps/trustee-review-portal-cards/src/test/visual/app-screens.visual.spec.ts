import { expect, test } from "@playwright/test";
import type { Page } from "@playwright/test";

/**
 * Every screen of the card-layout app, MEASURED in Chromium (C-TECH-078) — Design 2.0 Revision 2,
 * TAD trustee-portal-design-2 §13 (WI-0099..WI-0103). Card app only (`src/test/visual/**` is
 * presentation). The harness `app-harness.html` → `src/test/app-harness-app.tsx` mounts the whole
 * app on the design kit's own mock data.
 *
 * Measured per screen at 320, 390 and 1280px:
 *   1. the page never scrolls sideways (WCAG 1.4.10) — the table cards scroll inside themselves;
 *   2. every button and nav tab is at least 44px tall (WCAG 2.5.5, TAD §8.1);
 *   3. the kit's shell values as the browser resolves them: the grey-50 page, the sticky white
 *      header, the 1200px main column, the white pill nav bar, Playfair bold headings in ink-900,
 *      16px card radii, and the corrected selected-tab fill (TAD §8.3).
 */

type Screen = [string, (page: Page) => Promise<void>];

const SCREENS: Screen[] = [
  ["Round overview", async () => {}],
  ["Group applications", async (p) => { await p.getByRole("button", { name: "Group applications" }).click(); }],
  ["Group detail", async (p) => {
    await p.getByRole("button", { name: "Group applications" }).click();
    await p.getByRole("button", { name: /^Group GRP-014/ }).click();
  }],
  ["Individual applications", async (p) => { await p.getByRole("button", { name: "Individual applications" }).click(); }],
  ["Application detail", async (p) => {
    await p.getByRole("button", { name: "Individual applications" }).click();
    await p.getByRole("button", { name: /REV-2026-1057, open/ }).click();
  }],
];

interface Shell {
  pageOverflow: number;
  shortTargets: string[];
  bodyBackground: string;
  headerPosition: string;
  mainMaxWidth: string;
  navBackground: string;
  navRadius: string;
  selectedTab: string;
  h1: { family: string; weight: string; color: string };
  cardRadii: string[];
}

async function measure(page: Page): Promise<Shell> {
  return page.evaluate(() => {
    const doc = document.documentElement;
    const style = (el: Element | null) => (el === null ? null : getComputedStyle(el));
    const shortTargets: string[] = [];
    for (const el of document.querySelectorAll<HTMLElement>("main button, nav button")) {
      const r = el.getBoundingClientRect();
      if (r.width === 0 || el.closest('[aria-hidden="true"]') !== null) continue;
      if (r.height < 43.5) shortTargets.push(`${el.textContent?.trim() ?? "?"} ${r.height}`);
    }
    const nav = document.querySelector('nav[aria-label="Screen navigation"]');
    const h1 = style(document.querySelector("h1"));
    return {
      pageOverflow: doc.scrollWidth - doc.clientWidth,
      shortTargets,
      bodyBackground: style(document.querySelector("main")?.parentElement ?? null)?.backgroundColor ?? "",
      headerPosition: style(document.querySelector("header"))?.position ?? "",
      mainMaxWidth: style(document.querySelector("main"))?.maxWidth ?? "",
      navBackground: style(nav)?.backgroundColor ?? "",
      navRadius: style(nav)?.borderTopLeftRadius ?? "",
      selectedTab: style(nav?.querySelector('[aria-current="page"]') ?? null)?.backgroundColor ?? "",
      h1: { family: h1?.fontFamily ?? "", weight: h1?.fontWeight ?? "", color: h1?.color ?? "" },
      // Top-level cards only: a chart block is a <section> inside a card, not a card, and the
      // verdict's shared panel sits inside the detail screen's frame.
      cardRadii: [...document.querySelectorAll('main section[aria-labelledby]')]
        .filter((s) => s.parentElement?.closest("section") === null && s.parentElement?.closest('[data-detail-frame]') === null)
        .map((s) => getComputedStyle(s).borderTopLeftRadius),
    };
  });
}

for (const width of [320, 390, 1280]) {
  for (const [name, go] of SCREENS) {
    test(`${name} at ${width}px: no sideways scroll, 44px targets, the kit's shell`, async ({ page }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.goto("/app-harness.html");
      await page.getByRole("button", { name: "Round overview" }).waitFor();
      await go(page);
      await page.getByRole("heading", { level: 1 }).waitFor();
      await page.waitForTimeout(300);
      const g = await measure(page);
      expect(g.pageOverflow, "page scrolls sideways").toBeLessThanOrEqual(0);
      expect(g.shortTargets, "a control under 44px").toEqual([]);
      expect(g.bodyBackground).toBe("rgb(248, 247, 247)");
      expect(g.headerPosition).toBe("sticky");
      expect(g.mainMaxWidth).toBe("1200px");
      expect(g.navBackground).toBe("rgb(255, 255, 255)");
      expect(g.navRadius).toBe("999px");
      expect(g.selectedTab, "selected tab at --pink-700").toBe("rgb(196, 0, 108)");
      expect(g.h1.family).toMatch(/Playfair Display/);
      expect(g.h1.weight).toBe("700");
      expect(g.h1.color).toBe("rgb(43, 43, 43)");
      for (const radius of g.cardRadii) expect(["16px", "20px"], "card radius").toContain(radius);
    });
  }
}
