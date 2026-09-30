import { expect, test } from "@playwright/test";
import type { Page } from "@playwright/test";

/**
 * WI-0005 — the Trustee Pack rows, MEASURED in Chromium (`C-TECH-078`).
 *
 * `app.module.css`'s `.packDefinitions` comment makes three geometry claims about the detail
 * screen now that its labels are the Pack's own questions. Each is measured here rather than
 * asserted in a comment:
 *
 *   1. the page never scrolls sideways (WCAG 1.4.10), at a 320px phone width or a desktop one;
 *   2. no label or value overflows its own grid cell — long labels WRAP inside their track;
 *   3. from 480px up the value sits to the RIGHT of its label on the same row, and at desktop
 *      width the value column is the wider of the two (the Pack's own two-column proportion);
 *      below 480px each value sits directly BELOW its label, left-aligned with it.
 *
 * The 320px case failed on its first run (the page scrolled sideways by 8px: a 66px value
 * track could not hold "accommodation"), which is what the stacking rule answers.
 *
 * The harness (`detail-harness.html` → `src/test/detail-harness-app.tsx`) mounts every
 * section of `APPLICATION_DETAIL_LAYOUT` twice, released and withheld, inside the app's own
 * `.page` container and stylesheets.
 */

interface Geometry {
  pageOverflow: number;
  rows: number;
  cellOverflows: string[];
  notBesideLabel: string[];
  notBelowLabel: string[];
  valueNarrowerThanLabel: string[];
}

async function measure(page: Page): Promise<Geometry> {
  return page.evaluate(() => {
    const notBelowLabel: string[] = [];
    const doc = document.documentElement;
    const terms = [...document.querySelectorAll<HTMLElement>("dt[data-field]")];
    const cellOverflows: string[] = [];
    const notBesideLabel: string[] = [];
    const valueNarrowerThanLabel: string[] = [];
    for (const dt of terms) {
      const dd = dt.nextElementSibling as HTMLElement | null;
      const id = dt.getAttribute("data-field") ?? "?";
      if (dd === null) {
        notBesideLabel.push(`${id}: no dd`);
        continue;
      }
      for (const [name, el] of [["dt", dt], ["dd", dd]] as const) {
        if (el.scrollWidth > el.clientWidth + 1) cellOverflows.push(`${id} ${name} ${el.scrollWidth}>${el.clientWidth}`);
      }
      const t = dt.getBoundingClientRect();
      const d = dd.getBoundingClientRect();
      if (d.left < t.right || Math.abs(d.top - t.top) > 1) notBesideLabel.push(`${id} dt[${t.left},${t.right}] dd[${d.left},${d.top - t.top}]`);
      if (d.top < t.bottom - 1 || Math.abs(d.left - t.left) > 1) notBelowLabel.push(`${id} dt[${t.left},${t.bottom}] dd[${d.left},${d.top}]`);
      if (d.width < t.width) valueNarrowerThanLabel.push(`${id} ${d.width}<${t.width}`);
    }
    return {
      pageOverflow: doc.scrollWidth - doc.clientWidth,
      rows: terms.length,
      cellOverflows,
      notBesideLabel,
      notBelowLabel,
      valueNarrowerThanLabel,
    };
  });
}

for (const width of [320, 390, 1280]) {
  test(`detail sections at ${width}px: no sideways scroll, no cell overflow, value placed against its label`, async ({
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
    expect(g.cellOverflows, "a label or value overflows its grid cell").toEqual([]);
    if (width < 480) {
      expect(g.notBelowLabel, "a value is not directly below its label").toEqual([]);
    } else {
      expect(g.notBesideLabel, "a value is not beside its label").toEqual([]);
    }
    if (width >= 1280) {
      expect(g.valueNarrowerThanLabel, "value column narrower than label column").toEqual([]);
    }
  });
}

/**
 * WI-0008 review (2026-09-30): "Make it three distinct sections with more white space in between
 * the sections. Now it show the section title "in the last two weeks" directly under the last
 * question." Measured in the Current Circumstances panel of both mounts: the three wellbeing
 * sub-headings are present, each sits BELOW the previous group's last answer, and the smallest
 * gap between two groups is at least TWICE the largest gap between two rows inside any group.
 *
 * Twice, not merely larger, because "larger" already held on phones before the fix: measured
 * without `.detailGroup + .detailGroup`, the group gap was 24px against a 16px row gap at 320px,
 * and 12px against 16px at 1280px, the desktop case the reviewer saw. With the rule it is 60px
 * and 48px. Removing the rule fails this at every width.
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
    const lastAnswerBottom = (g: HTMLElement) =>
      Math.max(...[...g.querySelectorAll("dt, dd")].map((el) => el.getBoundingClientRect().bottom));
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
      const gap = group.getBoundingClientRect().top - lastAnswerBottom(previous);
      minGroupGap = Math.min(minGroupGap, gap);
      const h3 = group.querySelector("h3");
      if (h3 && h3.getBoundingClientRect().top < lastAnswerBottom(previous)) {
        headingAbovePrevious.push(h3.textContent ?? "");
      }
    }
    let maxRowGap = 0;
    for (const g of groups) {
      for (const [previousTerm, term] of pairs([...g.querySelectorAll<HTMLElement>("dt")])) {
        const previousValue = previousTerm.nextElementSibling;
        const previousBottom = Math.max(
          previousTerm.getBoundingClientRect().bottom,
          previousValue === null ? 0 : previousValue.getBoundingClientRect().bottom,
        );
        maxRowGap = Math.max(maxRowGap, term.getBoundingClientRect().top - previousBottom);
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
  test(`Current Circumstances at ${width}px: three wellbeing sub-sections, spaced at least twice the row gap`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/detail-harness.html");
    await page.getByTestId("harness-ready").waitFor();
    for (const mount of ["released", "withheld"]) {
      const g = await measureSubsections(page, mount);
      expect(g.headings, mount).toEqual(["Life satisfaction", "In the last 2 weeks…", "In the last year…"]);
      expect(g.headingAbovePrevious, `${mount}: a sub-heading overlaps the previous answer`).toEqual([]);
      expect(g.maxRowGap, `${mount}: rows measured`).toBeGreaterThan(0);
      expect(
        g.minGroupGap,
        `${mount}: sub-section gap ${String(g.minGroupGap)}px must be at least twice the row gap ${String(g.maxRowGap)}px`,
      ).toBeGreaterThanOrEqual(2 * g.maxRowGap);
    }
  });
}
