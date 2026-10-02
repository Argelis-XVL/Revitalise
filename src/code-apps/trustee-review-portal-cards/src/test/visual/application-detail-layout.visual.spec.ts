import { expect, test } from "@playwright/test";
import type { Page } from "@playwright/test";

/**
 * The card-layout detail screen, MEASURED in Chromium (`C-TECH-078`) — Design 2.0, card app only
 * (TAD trustee-portal-design-2, WI-0076). This file is on the parity gate's allow-list: the first
 * app's version measures a two-column `<dl>` whose value sits beside its label, a geometry this
 * layout deliberately does not have (tiles put the value BELOW the label at every width).
 *
 * The harness (`detail-harness.html` → `src/test/detail-harness-app.tsx`, byte-identical to the
 * first app's) mounts every section of `APPLICATION_DETAIL_LAYOUT` twice, released and withheld,
 * with long real-shaped values, through this app's `DetailSectionPanel` — so the hero, tiles,
 * receipt, answer cards, score bar, scale, answer list and restricted list are all on the page.
 *
 * Claims measured, at 320, 390 and 1280px:
 *   1. the page never scrolls sideways (WCAG 1.4.10), and no row's label or value overflows;
 *   2. every block stays inside its card, and every card inside the page;
 *   3. the grids reflow: one tile / one answer card per row at 320px, several at 1280px, and
 *      never more than their declared cap (4 tiles, 3 answer cards);
 *   4. the hero stacks below 480px (badge above the text) and sits side by side above it;
 *   5. the receipt's amounts sit right-aligned on their label's line;
 *   6. the 0-10 scale shows eleven 34px points; the score bar's fill is score/60 of its track;
 *   7. Current Circumstances keeps three spaced sub-sections (WI-0008), 32px apart.
 */

interface Geometry {
  pageOverflow: number;
  rows: number;
  cellOverflows: string[];
  outsideCard: string[];
  tileColumns: number[];
  answerColumns: number[];
  heroStacked: boolean[];
  heroSideBySide: boolean[];
  receiptMisaligned: string[];
  scalePoints: number[];
  scalePointSizes: string[];
  fillRatios: number[];
}

async function measure(page: Page): Promise<Geometry> {
  return page.evaluate(() => {
    const doc = document.documentElement;
    const rect = (el: Element) => el.getBoundingClientRect();
    const terms = [...document.querySelectorAll<HTMLElement>("dt[data-field]")];
    const cellOverflows: string[] = [];
    for (const dt of terms) {
      const id = dt.getAttribute("data-field") ?? "?";
      const dd = dt.nextElementSibling as HTMLElement | null;
      for (const [name, el] of [["dt", dt], ["dd", dd]] as const) {
        if (el === null) {
          cellOverflows.push(`${id}: no ${name}`);
          continue;
        }
        // A visually hidden label (the status pill's "Status") is a deliberate 1px clip box, read
        // by assistive technology only; it has no visible box to overflow.
        if (el.clientWidth <= 1) continue;
        if (el.scrollWidth > el.clientWidth + 1) cellOverflows.push(`${id} ${name} ${el.scrollWidth}>${el.clientWidth}`);
      }
    }
    const outsideCard: string[] = [];
    for (const card of document.querySelectorAll("section")) {
      const c = rect(card);
      if (c.right > doc.clientWidth + 1 || c.left < -1) outsideCard.push(`card ${c.left}..${c.right}`);
      for (const block of card.querySelectorAll("dl, [data-display-group]")) {
        const b = rect(block);
        if (b.left < c.left - 1 || b.right > c.right + 1) {
          outsideCard.push(`${block.getAttribute("data-display-group") ?? block.tagName} ${b.left}..${b.right} in ${c.left}..${c.right}`);
        }
      }
    }
    /**
     * How many distinct column positions a grid's children occupy — for grids with at least two
     * children only, since a one-card grid (Financial Eligibility's F5) has one column by definition.
     */
    const columns = (selector: string) =>
      [...document.querySelectorAll(selector)]
        .filter((grid) => grid.children.length >= 2)
        .map((grid) => new Set([...grid.children].map((child) => Math.round(rect(child).left))).size);
    const heroStacked: boolean[] = [];
    const heroSideBySide: boolean[] = [];
    for (const hero of document.querySelectorAll('section[data-section="summary"]')) {
      const badge = hero.querySelector("dl");
      const text = hero.querySelector("h2")?.parentElement?.parentElement;
      if (!badge || !text) continue;
      heroStacked.push(rect(badge).bottom <= rect(text).top + 1);
      heroSideBySide.push(rect(badge).right <= rect(text).left + 1);
    }
    const receiptMisaligned: string[] = [];
    for (const line of document.querySelectorAll('[data-print="receipt"] > div')) {
      const dt = line.querySelector("dt");
      const dd = line.querySelector("dd");
      if (!dt || !dd) continue;
      const l = rect(line);
      const style = getComputedStyle(line);
      const contentRight = l.right - parseFloat(style.paddingRight);
      if (Math.abs(rect(dd).right - contentRight) > 1) receiptMisaligned.push(`${dt.getAttribute("data-field") ?? "?"} not right-aligned`);
      if (rect(dd).top > rect(dt).bottom) receiptMisaligned.push(`${dt.getAttribute("data-field") ?? "?"} amount below its label`);
    }
    const scales = [...document.querySelectorAll('[role="img"]')];
    const scalePointSizes: string[] = [];
    for (const scale of scales) {
      for (const point of scale.children) {
        const p = rect(point);
        if (Math.round(p.width) !== 34 || Math.round(p.height) !== 34) scalePointSizes.push(`${p.width}x${p.height}`);
      }
    }
    const fillRatios = [...document.querySelectorAll('dt[data-field="C1"]')].map((dt) => {
      const track = dt.nextElementSibling?.querySelector('[aria-hidden="true"]');
      const fill = track?.firstElementChild;
      return track && fill ? rect(fill).width / rect(track).width : -1;
    });
    return {
      pageOverflow: doc.scrollWidth - doc.clientWidth,
      rows: terms.length,
      cellOverflows,
      outsideCard,
      tileColumns: columns('[data-print="tiles"]'),
      answerColumns: columns('[data-print="answers"]'),
      heroStacked,
      heroSideBySide,
      receiptMisaligned,
      scalePoints: scales.map((scale) => scale.children.length),
      scalePointSizes,
      fillRatios,
    };
  });
}

for (const width of [320, 390, 1280]) {
  test(`card layout at ${width}px: no sideways scroll, nothing overflows its card, grids and hero reflow`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/detail-harness.html");
    await page.getByTestId("harness-ready").waitFor();
    const g = await measure(page);
    // Proves the harness mounted: at least the Pack's 45 rows, in both mounts (released +
    // withheld). Count-coupled BY DESIGN (C-TECH-067) to the PDF's row count, not to the spec.
    expect(g.rows).toBeGreaterThanOrEqual(2 * 45);
    expect(g.pageOverflow, "page scrolls sideways").toBeLessThanOrEqual(0);
    expect(g.cellOverflows, "a label or value overflows its own box").toEqual([]);
    expect(g.outsideCard, "a block leaves its card, or a card leaves the page").toEqual([]);
    expect(g.receiptMisaligned, "a receipt amount is not right-aligned on its label's line").toEqual([]);
    expect(g.heroStacked.length, "both heroes measured").toBe(2);
    if (width < 480) {
      expect(g.heroStacked, "hero badge above the text below 480px").toEqual([true, true]);
      for (const n of [...g.tileColumns, ...g.answerColumns]) expect(n, "one column at phone width").toBe(1);
    } else {
      expect(g.heroSideBySide, "hero badge beside the text from 480px").toEqual([true, true]);
    }
    if (width >= 1280) {
      for (const n of g.tileColumns) {
        expect(n, "tiles reflow into several columns").toBeGreaterThan(1);
        expect(n, "never more than 4 tile columns").toBeLessThanOrEqual(4);
      }
      for (const n of g.answerColumns) {
        expect(n, "answer cards reflow into several columns").toBeGreaterThan(1);
        expect(n, "never more than 3 answer-card columns").toBeLessThanOrEqual(3);
      }
    }
    expect(g.scalePoints, "every scale shows eleven points").toEqual([11, 11]);
    expect(g.scalePointSizes, "every scale point is 34x34").toEqual([]);
    // Fixture score 59 → 59/60 of the track.
    for (const ratio of g.fillRatios) expect(ratio).toBeCloseTo(59 / 60, 2);
  });
}

/**
 * WI-0008 review (2026-09-30): "Make it three distinct sections with more white space in between
 * the sections." Kept in the card layout (README "Current Circumstances": blocks 32px apart).
 * Measured in the Current Circumstances panel of both mounts: the three wellbeing sub-headings are
 * present, each sits BELOW the previous group, and every gap between two groups is at least the
 * design's 32px and larger than any gap between two rows inside a group.
 */
interface SubsectionGeometry {
  headings: string[];
  minGroupGap: number;
  maxRowGap: number;
  headingAbovePrevious: string[];
}

async function measureSubsections(page: Page, mountId: string): Promise<SubsectionGeometry> {
  return page.evaluate((id) => {
    const mount = document.getElementById(id);
    if (!mount) throw new Error(`#${id} missing`);
    const panel = [...mount.querySelectorAll("section")].find(
      (s) => s.querySelector("h2")?.textContent === "Current Circumstances",
    );
    if (!panel) throw new Error("Current Circumstances panel missing");
    const groups = [...panel.querySelectorAll<HTMLElement>("[data-group]")];
    /** Each element paired with the one before it. Defined in here: `evaluate` serialises this callback. */
    function pairs<T>(items: readonly T[]): [T, T][] {
      const out: [T, T][] = [];
      let previous: T | undefined;
      for (const item of items) {
        if (previous !== undefined) out.push([previous, item]);
        previous = item;
      }
      return out;
    }
    let minGroupGap = Number.POSITIVE_INFINITY;
    const headingAbovePrevious: string[] = [];
    for (const [previous, group] of pairs(groups)) {
      const previousBottom = previous.getBoundingClientRect().bottom;
      minGroupGap = Math.min(minGroupGap, group.getBoundingClientRect().top - previousBottom);
      const h3 = group.querySelector("h3");
      if (h3 && h3.getBoundingClientRect().top < previousBottom) headingAbovePrevious.push(h3.textContent ?? "");
    }
    let maxRowGap = 0;
    for (const g of groups) {
      const rows = [...g.querySelectorAll<HTMLElement>("dl > div")];
      for (const [previous, row] of pairs(rows)) {
        maxRowGap = Math.max(maxRowGap, row.getBoundingClientRect().top - previous.getBoundingClientRect().bottom);
      }
    }
    return {
      headings: [...panel.querySelectorAll("h3")].map((h) => h.textContent ?? ""),
      minGroupGap,
      maxRowGap,
      headingAbovePrevious,
    };
  }, mountId);
}

for (const width of [320, 390, 1280]) {
  test(`Current Circumstances at ${width}px: three wellbeing sub-sections, 32px apart`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/detail-harness.html");
    await page.getByTestId("harness-ready").waitFor();
    for (const mount of ["released", "withheld"]) {
      const g = await measureSubsections(page, mount);
      expect(g.headings, mount).toEqual(["Life satisfaction", "In the last 2 weeks…", "In the last year…"]);
      expect(g.headingAbovePrevious, `${mount}: a sub-heading overlaps the previous group`).toEqual([]);
      expect(g.minGroupGap, `${mount}: sub-section gap`).toBeGreaterThanOrEqual(31.5);
      expect(g.minGroupGap, `${mount}: sub-sections must be further apart than rows`).toBeGreaterThan(g.maxRowGap);
    }
  });
}
