/**
 * The layout rules Revisions 8, 9 and 11 changed — WBS 6.9 and 6.8, CO-001-A2.
 *
 * THREE ROUNDS OF REVIEWER ITEMS LIVE IN THIS FILE AND THEY ARE NUMBERED SEPARATELY. The
 * `describe` blocks reading "reviewer item N" with no revision are Revision 8's eight items
 * (2026-08-31); the ones marked "Revision 9" are the six items of 2026-09-01. The two sets of
 * numbers do not correspond — Revision 9 item 1 is the data tables, Revision 8 item 1 was the
 * KPI tile grid — so every block below names its revision where the number alone would be
 * ambiguous.
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
    //
    // REVISION 9 MOVED THE FIGURE, NOT THE PROPERTY. Reviewer item 6 re-based every
    // group-level separation on `--space-8`; what this assertion has always held is that these
    // bars share ONE rhythm, so it is restated at the new step rather than deleted. `.actionRow`
    // (item 4) joins the list because it is now one of those bars.
    //
    // REVISION 11 NARROWS THE LIST BY TWO, AND THAT IS REVIEWER ITEM 2 — see the block at the
    // bottom of this file, which asserts the exception explicitly rather than letting these two
    // simply fall out of a shared assertion. What this test has always held is that the bars
    // which sit DIRECTLY UNDER THE NAV BAR share one rhythm; `.landingNav` and `.refreshBar` no
    // longer do, by the reviewer's own instruction, and their new step is pinned below.
    const rhythm = /margin:\s*var\(--space-8\) 0/;
    for (const selector of [".verdictActions", ".actionRow"]) {
      expect(ruleBody(APP_MODULE, selector)).toMatch(rhythm);
    }
  });
});

describe("reviewer item 8 — the applicant distributions lay out two per row", () => {
  const body = ruleBody(APP_MODULE, ".applicantGrid");

  it("caps at two columns the same way the tile grid caps at four", () => {
    expect(body).toContain("auto-fit");
    // The subtracted term IS the grid's own gap — Revision 9's item 6 moved both from
    // `--space-6` to `--space-8` in one edit, and this assertion is what makes moving only one
    // of them fail: a cap computed against a gap the grid does not use is off by the difference.
    expect(body).toMatch(/max\(\s*340px\s*,\s*\(100% - var\(--space-8\)\) \/ 2\s*\)/);
    expect(body).toMatch(/gap:\s*var\(--space-8\)/);
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

/* ========================================================================================= *
 * Revision 9 (2026-09-01, wbs:6.9) — the six reviewer items of the second post-deploy round.
 *
 * Items 1 and 5 are BEHAVIOURAL and are asserted where behaviour can be observed:
 * `components/DistributionChart.test.tsx` and `src/App.test.tsx` respectively. What is here is
 * the same class of assertion the blocks above make — a declaration whose absence caused, or
 * whose presence fixes, a defect a browser rendered and jsdom cannot.
 * ========================================================================================= */

describe("Revision 9 item 3 — the six filter controls resolve to one height", () => {
  const inputField = ruleBody(DS_MODULE, ".inputField");
  const filterSelect = ruleBody(APP_MODULE, ".filterSelect");

  it("gives ds/Input's field the border-box the Fluent Select already had", () => {
    // THE DIAGNOSIS, as an assertion. `*{box-sizing:border-box}` is one of the element rules
    // `ds-tokens.css` deliberately did not copy, so a bare `<input>` in this app is
    // content-box and its padding and border land OUTSIDE its height — while Fluent's own
    // select slot declares `box-sizing: border-box`. That difference is 26px of padding and
    // border counted twice over, and it is why two rules that both read `min-height: 44px`
    // rendered ~48px and 44px.
    expect(inputField).toContain("box-sizing: border-box");
    expect(filterSelect).toContain("box-sizing: border-box");
  });

  it("declares its own line-height rather than inheriting FluentProvider's 22px", () => {
    // The height of a content-sized input is its line box. Inheriting one tuned for a
    // different base size is the same mechanism as IMP-0509, one level up: there it made
    // glyphs overlap, here it made the BOX a size nobody authored.
    expect(inputField).toMatch(/line-height:\s*var\(--leading-snug\)/);
  });

  it("puts both controls' content inside the 44px floor rather than past it", () => {
    // 17px x 1.3 = 22.1px line box + 2 x 8px padding + 2 x 1px border = ~40px, under the
    // floor — so `min-height` is what renders, on both controls, and they agree by
    // construction. At `--space-3` the same sum is ~48px and the floor never applies.
    for (const body of [inputField, filterSelect]) {
      expect(body).toContain("min-height: 44px");
    }
    expect(inputField).toMatch(/padding:\s*var\(--space-2\) 14px/);
    expect(filterSelect).toMatch(/padding-top:\s*var\(--space-2\)/);
    expect(filterSelect).toMatch(/padding-bottom:\s*var\(--space-2\)/);
  });

  it("keeps the floor a floor, so 200% zoom grows the control instead of clipping it", () => {
    // WCAG 1.4.4. A fixed `height: 44px` would have equalised the two controls just as well
    // and clipped the text at zoom, which is why neither rule declares one.
    for (const body of [inputField, filterSelect]) {
      expect(body).not.toMatch(/(^|;)\s*height:/);
    }
  });
});

describe("Revision 9 item 4 — the page action row is the nav bar's own row", () => {
  const viewNav = ruleBody(APP_MODULE, ".viewNav");
  const actionRow = ruleBody(APP_MODULE, ".actionRow");

  it("takes the nav bar's gutter, which is the value that was 4px out", () => {
    // `.verdictActions`' 12px gap against `.viewNav`'s 8px is what put the second button in
    // the lower row 4px right of the second button above it.
    expect(viewNav).toContain("gap: var(--space-2)");
    expect(actionRow).toContain("gap: var(--space-2)");
  });

  it("does not re-introduce the centring that broke the shared baseline", () => {
    // `.verdictActions` sets `align-items: center` against the nav bar's default `stretch`.
    // That one is still correct INSIDE the verdict form; it is wrong for a row published
    // directly under the bar.
    expect(actionRow).not.toContain("align-items");
    expect(viewNav).not.toContain("align-items");
  });

  it("still wraps, so the row cannot overflow a 320px viewport (WCAG 1.4.10)", () => {
    expect(actionRow).toContain("flex-wrap: wrap");
  });
});

describe("Revision 9 item 5 — the nav bar's disabled-tab styling is gone, not orphaned", () => {
  it("declares neither of the two classes the removed state needed", () => {
    // ADR-040's "disabled, not hidden" is reversed at the reviewer's direction (App.tsx's
    // Revision 9 header). A class with no reachable call site reads as a live decision, so
    // both were deleted rather than left behind — and this is what fails if one comes back
    // without the markup that would use it.
    const selectors = rules(APP_MODULE).map((rule) => rule.selector);
    expect(selectors).not.toContain(".viewNavButtonDisabled");
    expect(selectors).not.toContain(".viewNavCaption");
  });

  it("keeps the two classes the two remaining states still use", () => {
    const selectors = rules(APP_MODULE).map((rule) => rule.selector);
    expect(selectors).toContain(".viewNavButton");
    expect(selectors).toContain(".viewNavButtonSelected");
  });
});

describe("Revision 9 item 6 — one rhythm, two tokens, every screen", () => {
  // The reviewer's ask was "more whitespace", and the failure mode of that ask is drift: each
  // screen nudged by a different amount. These assert the two chosen steps are the ones
  // actually declared, at every group boundary the three screens share.

  it("separates GROUPS with --space-8, on all three screens", () => {
    for (const selector of [
      ".header", // header band -> content (all screens)
      ".viewNav", // nav bar -> what follows it (all screens)
      ".toolbar", // the filter row (list screen)
      ".actionRow", // print / back-and-print (list and detail screens)
      ".panel", // every panel (landing and detail screens)
      ".chartBlock", // one distribution against the next (landing screen)
    ]) {
      expect(ruleBody(APP_MODULE, selector)).toMatch(/var\(--space-8\)/);
    }
  });

  it("separates ATTRIBUTES WITHIN a group with --space-4", () => {
    expect(ruleBody(APP_MODULE, ".definitions")).toMatch(/gap:\s*var\(--space-4\)/);
    expect(ruleBody(APP_MODULE, ".table caption")).toMatch(
      /padding-bottom:\s*var\(--space-4\)/,
    );
    expect(ruleBody(APP_MODULE, ".toolbar")).toMatch(/gap:\s*var\(--space-4\)/);
    expect(ruleBody(APP_MODULE, ".dataTableToggle")).toMatch(/margin:\s*var\(--space-4\) 0/);
  });

  it("introduces no pixel literal for any of it", () => {
    // The app's own convention: a raw px value is authored only where no token fits, and every
    // such place says so in a comment beside it. Item 6 needed no such place.
    for (const selector of [
      ".header",
      ".viewNav",
      ".toolbar",
      ".actionRow",
      ".panel",
      ".chartBlock",
      ".definitions",
      ".dataTableToggle",
    ]) {
      expect(ruleBody(APP_MODULE, selector)).not.toMatch(/margin[^;]*\d+px|gap:[^;]*\d+px/);
    }
  });
});

describe("Revision 9 item 2 — the chart legend keeps pace with the axis labels", () => {
  const legend = ruleBody(APP_MODULE, ".chartLegend");

  it("is set at the same --text-sm step the ticks moved to", () => {
    expect(legend).toMatch(/font-size:\s*var\(--text-sm\)/);
  });

  it("declares its own line-height, because this list wraps (IMP-0509's shape)", () => {
    expect(legend).toMatch(/line-height:\s*var\(--leading-normal\)/);
  });
});

/* ========================================================================================= *
 * Revision 11 (2026-09-02, wbs:6.8) — the third post-deploy review round's CSS-side items.
 *
 * Same limit as every block above: these assert the DECLARATION, because vitest processes no
 * CSS and jsdom resolves no layout. What they hold is the regression — each rule below was
 * authored to a stated figure for a stated reason, and an edit that silently reverts one fails
 * here rather than in the next review round.
 * ========================================================================================= */

describe("Revision 11 item 2 — the round overview's two control bars sit closer to the figures", () => {
  // "Too much white space between the round's summary/KPI figures and the 'Applications list'
  // button below them." The reading taken, and why, is in `app.module.css` beside `.landingNav`:
  // these two bars are the only thing between the round-overview screen's figures and its own
  // "Open the applications list" control, and each declared 32px on both sides.
  it("halves the step on `.landingNav` and `.refreshBar`, and on nothing else", () => {
    for (const selector of [".landingNav", ".refreshBar"]) {
      expect(ruleBody(APP_MODULE, selector)).toMatch(/margin:\s*var\(--space-4\) 0/);
    }
  });

  it("leaves Revision 9's group rhythm governing every OTHER boundary", () => {
    // The exception is two rules on one screen. If a later edit generalises it into "less
    // whitespace everywhere", these fail — which is the point: item 2 asked about one gap.
    for (const selector of [".viewNav", ".actionRow", ".verdictActions", ".panel", ".chartBlock"]) {
      expect(ruleBody(APP_MODULE, selector)).toMatch(/var\(--space-8\)/);
    }
  });

  it("stays on the two-token scale — no pixel literal is introduced for it", () => {
    for (const selector of [".landingNav", ".refreshBar"]) {
      expect(ruleBody(APP_MODULE, selector)).not.toMatch(/margin[^;]*\d+px/);
    }
  });
});

describe("Revision 11 item 4 — the chart legend gives every label the block's full width", () => {
  const legend = ruleBody(APP_MODULE, ".chartLegend");
  const item = ruleBody(APP_MODULE, ".chartLegendItem");

  it("lays the entries out as a column, not as a wrapping row", () => {
    // As a wrapping row each entry was sized by the row's leftover space, so
    // APPLICANT_TYPE_LABELS' 46-character option broke mid-phrase in a half-width grid cell —
    // the "wrapped badly" the reviewer reported.
    expect(legend).toContain("flex-direction: column");
    expect(legend).not.toContain("flex-wrap: wrap");
  });

  it("keeps the swatch on the first line of a label that still wraps", () => {
    // `align-items: center` would centre a 12px swatch against a two-line label.
    expect(item).toContain("align-items: flex-start");
    expect(ruleBody(APP_MODULE, ".chartLegendSwatch")).toMatch(/margin-top:\s*5px/);
  });

  it("does not give up Revision 9 item 2's legend type size", () => {
    // The legend must never read SMALLER than the axis labels it explains — that was half of
    // Revision 9's "too small", and item 4 is about width, not about size.
    expect(legend).toMatch(/font-size:\s*var\(--text-sm\)/);
  });
});
