/**
 * The layout rules' ACCESSIBILITY properties — CONTRACT, byte-identical in both apps
 * (TAD trustee-portal-design-2 §5.3 rule 1, Revision 3.2; reviewer answer "Rewrite in both apps").
 *
 * WHAT THIS FILE HOLDS, AND WHAT IT DELIBERATELY DOES NOT. Until Revision 3.1 this file pinned the
 * first app's layout VALUES (an 8px nav gutter, a button padding equal to the nav tabs', a 2:1
 * vertical rhythm, the 240px/340px grid floors). Those are presentation: the card app takes every
 * one of them from the design kit instead (ADR-061), so a values test cannot be identical in both
 * apps. §5.3 rule 1 is the way out — when a contract test asserts structure rather than content,
 * make it assert the load-bearing property, in both apps in one commit. The load-bearing properties
 * of a layout are its accessibility guarantees, and those hold in BOTH apps:
 *
 *   1. no button, nav tab, sort control, row link, select or input gives up the 44px target, and
 *      none sets a fixed `height` — 200% zoom grows a control instead of clipping it (WCAG 2.5.5,
 *      1.4.4);
 *   2. both form controls keep the strong boundary of ADR-037 correction 4 (WCAG 1.4.11), and
 *      ds/Input declares its own line-height rather than inheriting FluentProvider's 22px
 *      (IMP-0509; the first app's select is Fluent's own and carries Fluent's);
 *   3. every action row and the nav bar wrap, and nothing that names them turns wrapping off, so no
 *      row overflows a 320px viewport (WCAG 1.4.10);
 *   4. every auto-fit/auto-fill grid floor carries a container-relative term (C-TECH-076 check B,
 *      ADR-041), and data tables scroll inside their own container (WCAG 1.4.10);
 *   5. keyboard focus is drawn with the focus-ring token on buttons and inputs (WCAG 2.4.7);
 *   6. a hover lift, where a stylesheet has one, switches off under prefers-reduced-motion
 *      (WCAG 2.3.3).
 *
 * The VALUES each app chose are pinned elsewhere: the first app's by its reviewer-item comments
 * in its stylesheets, the card app's by the measured style inventory in its Dev Summary and by
 * `test/visual/app-screens.visual.spec.ts`.
 *
 * WHY TEXT AND NOT RENDERED GEOMETRY. vitest processes no CSS import, so `getComputedStyle` here
 * would pass over an empty stylesheet (IMP-0111). The stylesheets are read off disk and the
 * declarations asserted; rendered geometry is the visual specs' job.
 */
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

/** Comments out, so a rule and a warning about a rule cannot be confused. */
function withoutComments(css: string): string {
  return css.replace(/\/\*[\s\S]*?\*\//g, "");
}

const read = (name: string) => withoutComments(readFileSync(join(__dirname, name), "utf8"));
const APP_MODULE = read("app.module.css");
const DS_MODULE = read("ds.module.css");
/** Every CSS module this app ships — the card app has more of them than the first app. */
const MODULES = readdirSync(__dirname)
  .filter((name) => name.endsWith(".module.css"))
  .map((name) => [name, read(name)] as const);

/** Innermost rule blocks: `selector { body }`. Same helper shape as `ds-tokens.test.ts`. */
function rules(css: string): { selector: string; body: string }[] {
  return [...css.matchAll(/([^{}]+)\{([^{}]*)\}/g)].map((match) => ({
    selector: match[1]!.trim().replace(/\s+/g, " "),
    body: match[2]!.replace(/\s+/g, " ").trim(),
  }));
}

function ruleBody(css: string, selector: string): string {
  const found = rules(css).find((rule) => rule.selector === selector);
  if (found === undefined) throw new Error(`No rule for "${selector}"`);
  return found.body;
}

/** Rules whose selector list names `.className` as a whole class token. */
function rulesNaming(css: string, className: string): { selector: string; body: string }[] {
  const token = new RegExp(`\\.${className}(?![\\w-])`);
  return rules(css).filter((rule) => token.test(rule.selector));
}

const FIXED_HEIGHT = /(^|;)\s*height\s*:/;

describe("1. every interactive control keeps a 44px floor and no fixed height (WCAG 2.5.5, 1.4.4)", () => {
  const targets: [string, string, string][] = [
    ["ds.module.css", ".button", DS_MODULE],
    ["ds.module.css", ".buttonSm", DS_MODULE],
    ["ds.module.css", ".buttonMd", DS_MODULE],
    ["ds.module.css", ".buttonLg", DS_MODULE],
    ["ds.module.css", ".inputField", DS_MODULE],
    ["app.module.css", ".filterSelect", APP_MODULE],
    ["app.module.css", ".viewNavButton", APP_MODULE],
    ["app.module.css", ".table th .sortButton", APP_MODULE],
    ["app.module.css", ".rowLink", APP_MODULE],
    ["app.module.css", ".tallTarget", APP_MODULE],
  ];
  for (const [file, selector, css] of targets) {
    it(`${file} ${selector}: min-height 44px, no fixed height`, () => {
      const body = ruleBody(css, selector);
      expect(body).toMatch(/min-height: 44px/);
      expect(body).not.toMatch(FIXED_HEIGHT);
    });
  }
});

describe("2. both form controls keep the strong boundary; ds/Input declares its line-height", () => {
  for (const [file, selector, css] of [
    ["ds.module.css", ".inputField", DS_MODULE],
    ["app.module.css", ".filterSelect", APP_MODULE],
  ] as const) {
    it(`${file} ${selector}`, () => {
      const body = ruleBody(css, selector);
      if (selector === ".inputField") expect(body).toMatch(/line-height\s*:/);
      expect(body).toContain("var(--border-strong)");
      expect(body).not.toContain("var(--border-default)");
    });
  }
});

describe("3. action rows and the nav bar wrap (WCAG 1.4.10)", () => {
  for (const className of ["viewNav", "toolbar", "refreshBar", "rowActions", "verdictActions", "actionRow"]) {
    it(`.${className} wraps, and no rule naming it turns wrapping off`, () => {
      const named = rulesNaming(APP_MODULE, className);
      expect(named.length, `.${className} must have a rule`).toBeGreaterThan(0);
      expect(named.some((rule) => rule.body.includes("flex-wrap: wrap"))).toBe(true);
      for (const rule of named) expect(rule.body, rule.selector).not.toMatch(/flex-wrap:\s*nowrap/);
    });
  }
});

describe("4. grids cap against their container, tables scroll inside theirs (WCAG 1.4.10)", () => {
  for (const [name, css] of MODULES) {
    it(`${name}: every auto-fit/auto-fill floor carries a container-relative term`, () => {
      for (const match of css.matchAll(/repeat\(\s*auto-(?:fit|fill)\s*,\s*minmax\(([\s\S]*?)\)\s*\)/g)) {
        expect(match[1], match[0]).toMatch(/%/);
      }
    });
  }

  it("app.module.css .tableScroll scrolls horizontally inside itself", () => {
    expect(ruleBody(APP_MODULE, ".tableScroll")).toContain("overflow-x: auto");
  });
});

describe("5. keyboard focus is drawn with the focus-ring token (WCAG 2.4.7)", () => {
  for (const selector of [".button:focus-visible", ".inputField:focus-visible"]) {
    it(`ds.module.css ${selector}`, () => {
      expect(ruleBody(DS_MODULE, selector)).toMatch(/outline: \d+px solid var\(--focus-ring\)/);
    });
  }
});

describe("6. a hover lift switches off under prefers-reduced-motion (WCAG 2.3.3)", () => {
  for (const [name, css] of MODULES) {
    it(`${name}`, () => {
      const lifts = rules(css).some((rule) => /:hover/.test(rule.selector) && /translateY\(/.test(rule.body));
      if (!lifts) return;
      expect(css).toMatch(/@media \(prefers-reduced-motion: reduce\)[\s\S]*transform: none/);
    });
  }
});
