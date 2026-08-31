/**
 * The layout rules Revision 8 changed — reviewer items 1, 2, 3 and 8, WBS 6.9, CO-001-A2.
 *
 * WHY THESE ARE ASSERTED AS TEXT AND NOT AS RENDERED GEOMETRY. `vitest.config.ts` sets no
 * `css` option, so **vitest processes no CSS import at all**: a `.css` import resolves to an
 * empty module and jsdom computes no layout from it. `getComputedStyle` in a test would
 * return the initial value for every property this file cares about, so a test written that
 * way would pass against a completely empty stylesheet — the `IMP-0111` trap ("a test written
 * from the same assumption as the code locks the assumption in") in its purest form.
 *
 * `ds-tokens.test.ts` and `print.test.ts` already establish the alternative this file follows:
 * read the stylesheet off disk AS TEXT and assert against the declarations actually in it.
 * That is genuinely weaker than a rendered check — it verifies the rule is DECLARED, not that
 * a browser resolves it to four columns — so every assertion below is written against the
 * specific declaration whose absence caused the reported defect, and the arithmetic that makes
 * it the right declaration is in the stylesheet's own comment beside the value.
 *
 * WHAT THIS FILE DOES NOT CLAIM. It does not prove the reviewer's screenshots are fixed. A
 * four-column grid is an interaction between a track floor, a gap and a container width, and
 * only a browser resolves that. What it does hold is the REGRESSION: each of these four rules
 * was authored to a stated figure, and a later edit that silently drops the cap, the basis or
 * the shared button metric fails here rather than in the next review round.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

/** Comments out, so a rule and a warning about a rule cannot be confused. */
function withoutComments(css: string): string {
  return css.replace(/\/\*[\s\S]*?\*\//g, "");
}

const APP_MODULE = withoutComments(readFileSync(join(__dirname, "app.module.css"), "utf8"));
const DS_MODULE = withoutComments(readFileSync(join(__dirname, "ds.module.css"), "utf8"));

/** Innermost rule blocks: `selector { body }`. Same helper shape as `ds-tokens.test.ts`. */
function rules(css: string): { selector: string; body: string }[] {
  return [...css.matchAll(/([^{}]+)\{([^{}]*)\}/g)].map((match) => ({
    selector: match[1]!.trim().replace(/\s+/g, " "),
    body: match[2]!,
  }));
}

function ruleBody(css: string, selector: string): string {
  const found = rules(css).find((rule) => rule.selector === selector);
  if (found === undefined) throw new Error(`No rule for "${selector}"`);
  return found.body.replace(/\s+/g, " ").trim();
}

describe("reviewer item 1 — the KPI tile grid tops out at four columns", () => {
  // The reviewer measured eight tiles laid out 6 + 2, on both the FR-063 financial panel and
  // "Round progress", and asked for 4 + 4.
  const body = ruleBody(APP_MODULE, ".statTiles");

  it("caps the track count with a container-relative floor, not a bigger absolute one", () => {
    // `auto-fit` fits as MANY tracks as the floor allows, so a purely absolute floor cannot
    // cap the count at any width — that is why ADR-041's 240px did not produce four columns.
    // A floor of at least a quarter of the row makes a fifth column impossible.
    expect(body).toContain("auto-fit");
    expect(body).toMatch(/max\(\s*240px\s*,\s*\(100% - 3 \* var\(--space-4\)\) \/ 4\s*\)/);
  });

  it("keeps the 240px absolute floor, so it still collapses on a narrow viewport", () => {
    // The WCAG 1.4.10 guarantee ADR-041 rests on: below ~1000px the absolute half of the
    // `max()` takes over and `auto-fit` collapses to 3, then 2, then 1. A cap that replaced
    // the floor rather than joining it would overflow a 320px viewport.
    expect(body).toContain("240px");
    expect(body).not.toMatch(/grid-template-columns:\s*repeat\(\s*4\s*,/);
  });
});

describe("reviewer item 2 — every filter field is the same width", () => {
  // The controls were sized by their own content above a `min-width` floor, so "Review round"
  // grew to fit its longest option string and "Status" did not.
  it("gives the field a fixed flex basis rather than only a minimum", () => {
    const body = ruleBody(APP_MODULE, ".filterField");
    expect(body).toMatch(/flex:\s*1 1 220px/);
    // A flex item's `auto` minimum would re-inflate the field to its content's width and
    // undo the basis. This is the declaration that actually holds the equality.
    expect(body).toMatch(/min-width:\s*0/);
  });

  it("makes the control fill the field, for both the Fluent Select and ds/Input", () => {
    // Equal-width FIELDS still render unequal CONTROLS without this: a `<select>` falls back
    // to its longest option and an `<input>` to its 20-character default size.
    expect(ruleBody(APP_MODULE, ".filterControl")).toMatch(/width:\s*100%/);
    expect(ruleBody(APP_MODULE, ".filterSelect")).toMatch(/width:\s*100%/);
  });

  it("keeps the two score fields equal to each other", () => {
    expect(ruleBody(APP_MODULE, ".scoreRange .filterField")).toMatch(/flex:\s*1 1 0/);
  });
});

describe("reviewer item 3 — one button size across every screen", () => {
  // The detail screen's buttons were "oversized vs. the nav-bar buttons": `.viewNavButton`
  // (this app's own, ADR-040) and `ds/Button`'s default `md` were two ladders authored in two
  // files, neither aware of the other.
  const navBar = ruleBody(APP_MODULE, ".viewNavButton");
  const buttonMd = ruleBody(DS_MODULE, ".buttonMd");

  it("gives ds/Button's `md` the nav bar's own padding and type size", () => {
    for (const declaration of ["padding: var(--space-2) var(--space-4)", "font-size: var(--text-sm)"]) {
      expect(navBar).toContain(declaration);
      expect(buttonMd).toContain(declaration);
    }
  });

  it("keeps the ladder monotone — `sm` is not wider than `md`", () => {
    // Leaving `sm` at its old `10px 20px` would have made "small" WIDER than "medium", which
    // is the kind of quiet incoherence that produces the next mismatch.
    expect(ruleBody(DS_MODULE, ".buttonSm")).toContain("padding: 6px var(--space-3)");
  });

  it("does not give up the 44px target on any size (WCAG 2.5.5)", () => {
    // The guarantee is the target size; only the appearance moved. `ds-tokens.test.ts`
    // asserts this too — restated here because THIS change is the one that could have
    // dropped it.
    for (const selector of [".buttonSm", ".buttonMd", ".buttonLg"]) {
      expect(ruleBody(DS_MODULE, selector)).toContain("min-height: 44px");
    }
    expect(navBar).toContain("min-height: 44px");
  });

  it("puts every action bar on the same vertical rhythm", () => {
    // The other half of "misaligned": the bars were never mis-aligned horizontally, they were
    // on two different vertical rhythms because `.verdictActions` declared no margin.
    const rhythm = /margin:\s*var\(--space-3\) 0/;
    for (const selector of [".verdictActions", ".landingNav", ".refreshBar"]) {
      expect(ruleBody(APP_MODULE, selector)).toMatch(rhythm);
    }
  });
});

describe("reviewer item 8 — the applicant distributions lay out two per row", () => {
  const body = ruleBody(APP_MODULE, ".applicantGrid");

  it("caps at two columns the same way the tile grid caps at four", () => {
    expect(body).toContain("auto-fit");
    expect(body).toMatch(/max\(\s*340px\s*,\s*\(100% - var\(--space-6\)\) \/ 2\s*\)/);
  });

  it("still collapses to one column on a narrow viewport (WCAG 1.4.10)", () => {
    expect(body).toContain("340px");
    expect(body).not.toMatch(/grid-template-columns:\s*repeat\(\s*2\s*,/);
  });

  it("stacks the share-only block rather than splitting an already-halved cell in two", () => {
    // `.chartLayout` pairs a table with a chart at >=900px. In `share-only` there is no second
    // chart to pair with, and the cell has already been halved by the grid above.
    const stacked = ruleBody(APP_MODULE, ".chartLayoutStacked");
    expect(stacked).toMatch(/grid-template-columns:\s*1fr/);
  });
});
