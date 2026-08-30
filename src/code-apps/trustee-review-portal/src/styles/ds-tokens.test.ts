/**
 * The design-system token layer — ADR-033, ADR-035, ADR-036, ADR-037, and A-R38's mitigation.
 *
 * WHY THIS FILE IS A REQUIRED DELIVERABLE AND NOT A NICE-TO-HAVE. `vitest.config.ts` sets no
 * `css` option, so **vitest processes no CSS imports at all** — a `.css` import from a
 * test-reachable module resolves to an empty module and defines not one custom property in
 * jsdom. The `import "../styles/ds-tokens.css"` in `src/test/harness.tsx` therefore keeps the
 * harness's module graph identical to `main.tsx`'s and does NOTHING else; it is fidelity, not
 * evidence. Which means a broken token, a reverted correction or a drifted hex would be
 * invisible to all 496 of this app's other tests.
 *
 * This file is what actually catches it, and it is the same technique `theme.test.ts:266-329`
 * and `print.test.ts:17` already use: read the stylesheet off disk as TEXT, and then
 * COMPUTE-AND-PIN rather than snapshot. A snapshot would record whatever the file says; these
 * assertions recompute every WCAG ratio from the values actually declared and fail when one
 * stops clearing its floor.
 *
 * COMMENTS ARE STRIPPED BEFORE ANYTHING IS ASSERTED. `ds-tokens.css` discusses the failing
 * design-system values by name in prose — `--text-muted`'s six failing ratios, the removed
 * `outline: none`, the unshipped `--warning` — and a rule must never be confused with a
 * WARNING ABOUT a rule. `theme.test.ts:266-273` does exactly this and says exactly why.
 *
 * NO HEX IS RETYPED AS A FACT HERE. The three button fills, the heading colour and both font
 * stacks are imported from `theme.ts`, which is the single source of truth for every supplied
 * brand value (ADR-035). That is the point: two files naming the same colour is the drift risk,
 * so the stylesheet is asserted to AGREE WITH the module rather than to match a literal a future
 * editor would have to remember to change in two places.
 */
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import {
  REV_FONT_COLOUR,
  REV_FONT_FAMILY_BODY,
  REV_FONT_FAMILY_HEADING,
  brandRamp,
} from "../theme";

/**
 * WCAG 2.1 relative luminance. Copied verbatim from `theme.test.ts:35-40` rather than shared:
 * this app adds no dependency for eight lines of arithmetic, and a hand-checkable formula that
 * lives beside the assertions it serves is the point (`theme.test.ts:12-15`).
 */
function luminance(hex: string): number {
  const value = hex.replace("#", "");
  const channels = [0, 2, 4].map(
    (offset) => Number.parseInt(value.slice(offset, offset + 2), 16) / 255,
  );
  const linear = channels.map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4));
  return 0.2126 * linear[0]! + 0.7152 * linear[1]! + 0.0722 * linear[2]!;
}

/** WCAG 2.1 contrast ratio, rounded to two places the way the comments quote it. */
function contrast(a: string, b: string): number {
  const [high, low] = [luminance(a), luminance(b)].sort((x, y) => y - x) as [number, number];
  return Math.round(((high + 0.05) / (low + 0.05)) * 100) / 100;
}

/** WCAG 2.1 AA floors. */
const NORMAL_TEXT = 4.5;
const LARGE_TEXT_AND_UI_GRAPHICS = 3;

const WHITE = "#ffffff";

/** Comments out, so a rule and a warning about a rule cannot be confused. */
function withoutComments(css: string): string {
  return css.replace(/\/\*[\s\S]*?\*\//g, "");
}

const DS_TOKENS = withoutComments(readFileSync(join(__dirname, "ds-tokens.css"), "utf8"));
const DS_MODULE = withoutComments(readFileSync(join(__dirname, "ds.module.css"), "utf8"));

/**
 * Every custom-property declaration in `ds-tokens.css`, last-one-wins the way the cascade
 * resolves them.
 */
function declarations(css: string): Map<string, string> {
  const found = new Map<string, string>();
  for (const match of css.matchAll(/(--[a-z0-9-]+)\s*:\s*([^;}]+);/g)) {
    found.set(match[1]!, match[2]!.trim().replace(/\s+/g, " "));
  }
  return found;
}

const TOKENS = declarations(DS_TOKENS);

/**
 * Resolve a token to a 6-digit hex, following `var()` aliases. `--text-body: var(--ink-600)`
 * and `--ink-600: #5a5a5a` is two hops, and resolving rather than reading the literal is what
 * makes the alias CHAIN part of what is guarded: repointing `--text-body` at a failing neutral
 * would otherwise be invisible here.
 *
 * Throws rather than returning a default, so a renamed or deleted token is a loud failure.
 */
function resolve(name: string, seen: string[] = []): string {
  if (seen.includes(name)) throw new Error(`Circular token reference: ${[...seen, name].join(" -> ")}`);
  const raw = TOKENS.get(name);
  if (raw === undefined) throw new Error(`ds-tokens.css declares no ${name}`);
  const alias = /^var\(\s*(--[a-z0-9-]+)\s*\)$/.exec(raw);
  if (alias !== null) return resolve(alias[1]!, [...seen, name]);
  if (!/^#[0-9a-f]{6}$/i.test(raw)) {
    throw new Error(`${name} resolves to "${raw}", which is not a 6-digit hex colour`);
  }
  return raw.toLowerCase();
}

/** Innermost rule blocks: `selector { body }`. */
function rules(css: string): { selector: string; body: string }[] {
  return [...css.matchAll(/([^{}]+)\{([^{}]*)\}/g)].map((match) => ({
    selector: match[1]!.trim().replace(/\s+/g, " "),
    body: match[2]!,
  }));
}

/**
 * The six surfaces the design system defines and that every foreground below is checked
 * against. Checking each PAIR rather than trusting a general rule is what found the two
 * corrections recorded in `theme.ts`'s header, and it is what found ADR-037's five.
 */
const SURFACES = [
  "--surface-page",
  "--surface-muted",
  "--grey-100",
  "--surface-band",
  "--brand-tint",
  "--pink-50",
] as const;

describe("the contrast function itself", () => {
  // Identical fixed points to theme.test.ts:57-62. A contrast check whose arithmetic is wrong
  // would pass everything below for the wrong reason, and this file's whole value is its
  // arithmetic — so the arithmetic is pinned against three figures nobody has to trust it for.
  it("computes the two known extremes and one published Fluent figure", () => {
    expect(contrast("#000000", WHITE)).toBe(21);
    expect(contrast(WHITE, WHITE)).toBe(1);
    // Fluent light's own body text: colorNeutralForeground1 #242424 on white.
    expect(contrast("#242424", WHITE)).toBe(15.52);
  });

  it("resolves a var() alias chain to the hex at the end of it", () => {
    // The resolver is as load-bearing as the arithmetic: if it silently returned the wrong
    // value, every ratio below would be computed against the wrong colour.
    expect(resolve("--white")).toBe("#ffffff");
    expect(resolve("--text-body")).toBe("#5a5a5a"); // via --ink-600
    expect(resolve("--surface-muted")).toBe("#f8f7f7"); // via --grey-50
    expect(() => resolve("--no-such-token")).toThrow(/declares no/);
  });
});

describe("ADR-037 correction 1 — the button ladder comes from the supplied ramp", () => {
  it("declares the three fills as brandRamp[70] / [60] / [30], imported from theme.ts", () => {
    // Assertion 1. No hex is retyped: these compare the stylesheet against the module, so the
    // two files cannot drift. brandRamp[70] is #cc0078, [60] #ac0064, [30] #51002c.
    expect(resolve("--brand-primary")).toBe(brandRamp[70]);
    expect(resolve("--brand-primary-hover")).toBe(brandRamp[60]);
    expect(resolve("--brand-primary-active")).toBe(brandRamp[30]);
  });

  it("does NOT use the design system's own reconstructed pink for the primary", () => {
    // White on --pink-600 (#e6027f) is 4.49:1 and fails by 0.01. The token is kept as a palette
    // entry (§8.4.4 adopts the --pink-* ramp verbatim) and must not back --brand-primary.
    expect(contrast(WHITE, resolve("--pink-600"))).toBeLessThan(NORMAL_TEXT);
    expect(resolve("--brand-primary")).not.toBe(resolve("--pink-600"));
  });

  it("passes normal-text contrast with white on all three button states", () => {
    // Assertion 2. Expected 5.47 rest / 7.15 hover / 15.15 active.
    for (const token of [
      "--brand-primary",
      "--brand-primary-hover",
      "--brand-primary-active",
    ] as const) {
      expect(contrast(WHITE, resolve(token)), token).toBeGreaterThanOrEqual(NORMAL_TEXT);
    }
    expect(contrast(WHITE, resolve("--brand-primary"))).toBe(5.47);
  });

  it("passes normal-text contrast with --brand-primary AS TEXT on every surface", () => {
    // The other direction, and it is not hypothetical: this token is the secondary button's
    // LABEL colour (.buttonSecondary) and the link colour (--link-default). Thinnest margin is
    // 4.54 on --surface-band.
    for (const surface of SURFACES) {
      expect(
        contrast(resolve("--brand-primary"), resolve(surface)),
        `--brand-primary on ${surface}`,
      ).toBeGreaterThanOrEqual(NORMAL_TEXT);
    }
  });

  it("keeps every state a distinct colour, with a rest-to-hover step that is felt", () => {
    // The regression correction 1 could have introduced: a ladder whose states are compliant
    // but indistinguishable, so a button stops responding visibly to a pointer. Fluent's own
    // default step is 1.30 (brand[80] -> brand[70]) and theme.ts:126-131 pins the same property
    // for the Fluent theme.
    const states = [
      resolve("--brand-primary"),
      resolve("--brand-primary-hover"),
      resolve("--brand-primary-active"),
    ];
    expect(new Set(states).size).toBe(states.length);
    expect(
      contrast(resolve("--brand-primary"), resolve("--brand-primary-hover")),
    ).toBeGreaterThanOrEqual(contrast(brandRamp[80], brandRamp[70]));
  });

  it("carries the link colours through the same corrected values", () => {
    expect(resolve("--link-default")).toBe(brandRamp[70]);
    expect(resolve("--link-hover")).toBe(brandRamp[60]);
  });
});

describe("text colours on every surface the design system defines", () => {
  it("sets --text-heading to the SUPPLIED font colour and passes on all six (OQ-040)", () => {
    // Assertion 3. OQ-040 resolved to the supplied value on reviewer silence, 2026-08-27:
    // #002060 is what Revitalise supplied, and the design system's near-black is a
    // reconstruction from three screenshots. Compared against theme.ts, not a literal.
    // Expected 15.27 · 14.28 · 13.21 · 12.66 · 12.73 · 13.90.
    expect(resolve("--text-heading")).toBe(REV_FONT_COLOUR);
    for (const surface of SURFACES) {
      expect(
        contrast(resolve("--text-heading"), resolve(surface)),
        `--text-heading on ${surface}`,
      ).toBeGreaterThanOrEqual(NORMAL_TEXT);
    }
  });

  it("passes --text-body on all six surfaces", () => {
    // Expected 6.90 · 6.45 · 5.97 · 5.72 · 5.75 · 6.28. This is the token every text use of
    // --text-muted was remapped to, so its compliance is what makes correction 2 possible.
    for (const surface of SURFACES) {
      expect(
        contrast(resolve("--text-body"), resolve(surface)),
        `--text-body on ${surface}`,
      ).toBeGreaterThanOrEqual(NORMAL_TEXT);
    }
  });

  it("records that --text-muted FAILS as text everywhere, which is why correction 2 exists", () => {
    // Both halves pinned, the way theme.test.ts:207-225 pins its own two corrections: that the
    // token is unusable as text, and that the shipped alternative works. 3.45 is its best
    // showing, on white, and it is still below 4.5. On three surfaces it is below even 3.0.
    for (const surface of SURFACES) {
      expect(
        contrast(resolve("--text-muted"), resolve(surface)),
        `--text-muted on ${surface}`,
      ).toBeLessThan(NORMAL_TEXT);
    }
  });
});

describe("ADR-037 correction 3 — the focus ring is the app's black", () => {
  it("declares #000000 and clears the 3:1 UI-graphic floor on all six surfaces", () => {
    // Assertion 4. Expected 21.00 · 19.64 · 18.17 · 17.41 · 17.51 · 19.11. The design system's
    // own --focus-ring (#ec4ea3) measured 2.82-3.40 and failed three of its own six surfaces.
    expect(resolve("--focus-ring")).toBe("#000000");
    for (const surface of SURFACES) {
      expect(
        contrast(resolve("--focus-ring"), resolve(surface)),
        `--focus-ring on ${surface}`,
      ).toBeGreaterThanOrEqual(LARGE_TEXT_AND_UI_GRAPHICS);
    }
  });

  it("does not carry the design system's failing pink ring", () => {
    expect(resolve("--focus-ring")).not.toBe(resolve("--pink-500"));
    expect(contrast(resolve("--pink-500"), resolve("--surface-band"))).toBeLessThan(
      LARGE_TEXT_AND_UI_GRAPHICS,
    );
  });
});

describe("ADR-037 correction 4 — a control boundary is --border-strong", () => {
  it("clears the 3:1 control-boundary floor with --border-strong against white", () => {
    // Assertion 5. Expected 3.45.
    expect(contrast(resolve("--border-strong"), WHITE)).toBeGreaterThanOrEqual(
      LARGE_TEXT_AND_UI_GRAPHICS,
    );
  });

  it("records that --border-default does NOT clear it, so it stays decorative only", () => {
    // 1.34:1. Fine as a card boundary, where the content carries the meaning; not fine as the
    // only way to perceive a form control (WCAG 1.4.11).
    expect(contrast(resolve("--border-default"), WHITE)).toBeLessThan(
      LARGE_TEXT_AND_UI_GRAPHICS,
    );
  });

  it("uses the strong border on every input/textarea/select rule in ds.module.css", () => {
    // Assertion 8, correction 4 made mechanical. Scoped to rules whose SELECTOR names a form
    // control, so the card and tile borders — which are legitimately --border-default — are not
    // caught. Written over every matching rule rather than the one that exists today, so a
    // textarea or select class added later inherits the guard.
    const controlRules = rules(DS_MODULE).filter(
      (rule) => /input|textarea|select/i.test(rule.selector) && /border\s*:/.test(rule.body),
    );
    expect(controlRules.length).toBeGreaterThan(0);
    for (const rule of controlRules) {
      expect(rule.body, rule.selector).toContain("--border-strong");
      expect(rule.body, rule.selector).not.toContain("--border-default");
    }
  });
});

describe("ADR-037 corrections 2 and 3, made mechanical over ds.module.css", () => {
  it("never sets a text colour to --text-muted", () => {
    // Assertion 6. The token is retained for non-text use; this is the guard that keeps it
    // there. StatTile's label is the case this exists for (§8.5 point 3).
    expect(DS_MODULE).not.toMatch(/color\s*:\s*var\(\s*--text-muted\s*\)/);
  });

  it("never removes a focus outline", () => {
    // Assertion 7. `components/forms/Input.jsx:17` sets `outline: none`; the conversion drops
    // it. WCAG 2.4.7 outright, not a contrast miss.
    expect(DS_MODULE).not.toMatch(/outline\s*:\s*none/);
    expect(DS_MODULE).not.toMatch(/outline\s*:\s*0\b/);
  });

  it("gives every focusable converted control a visible ring from --focus-ring", () => {
    const focusRules = rules(DS_MODULE).filter((rule) => rule.selector.includes(":focus-visible"));
    expect(focusRules.length).toBeGreaterThan(0);
    for (const rule of focusRules) {
      expect(rule.body, rule.selector).toContain("var(--focus-ring)");
    }
  });
});

describe("the 44px minimum target, on every button size (§2.2.2, WCAG 2.5.5)", () => {
  it("declares min-height: 44px on sm, md AND lg", () => {
    // Assertion 9. `sm` is the one that matters: the mockup uses it for the per-row Record
    // verdict control and four others, and at --text-sm with the supplied '10px 20px' padding
    // the computed height lands below the 44x44 this app already guarantees via
    // styles.tallTarget (app.module.css:171).
    const sizeRules = rules(DS_MODULE).filter((rule) =>
      /^\.button(Sm|Md|Lg)$/.test(rule.selector),
    );
    expect(sizeRules.map((rule) => rule.selector).sort()).toEqual([
      ".buttonLg",
      ".buttonMd",
      ".buttonSm",
    ]);
    for (const rule of sizeRules) {
      expect(rule.body, rule.selector).toMatch(/min-height\s*:\s*44px/);
    }
  });

  it("protects an icon-only button's width on the shared base class", () => {
    const base = rules(DS_MODULE).find((rule) => rule.selector === ".button");
    expect(base).toBeDefined();
    expect(base!.body).toMatch(/min-width\s*:\s*44px/);
    expect(base!.body).toMatch(/min-height\s*:\s*44px/);
  });
});

describe("statTileValue wraps a long figure instead of overflowing its tile (IMP-0486)", () => {
  it("declares overflow-wrap: break-word, never a truncating rule", () => {
    // The design system's own spec (`StatTile.prompt.md`) shows only a 5-character example
    // ("1,000") and states no overflow behaviour — this app's own figures are not all that
    // short (`RoundFinancePanel.tsx`'s currency values), so wrapping is this app's own
    // addition, not a conversion of anything supplied. A currency figure must WRAP, never be
    // hidden behind an ellipsis: `text-overflow: ellipsis` would silently misstate an amount.
    const rule = rules(DS_MODULE).find((candidate) => candidate.selector === ".statTileValue");
    expect(rule, ".statTileValue rule must exist in ds.module.css").toBeDefined();
    expect(rule!.body).toMatch(/overflow-wrap\s*:\s*break-word/);
    expect(rule!.body).not.toMatch(/text-overflow\s*:\s*ellipsis/);
    expect(rule!.body).not.toMatch(/white-space\s*:\s*nowrap/);
  });

  it("declares its own line-height, wide enough for its own font-size (IMP-0509)", () => {
    // GROUND TRUTH, live in a Chromium render of `RoundFinancePanel` at 1280px (`wbs:6.9`):
    // `.statTileValue` set no `line-height` of its own, so it inherited whatever ancestor set
    // one last — `FluentProvider`'s root, at 22px for the 16px body face
    // (`lineHeightBase300`). 22px is fine leading for 16px text and is COMPRESSED leading for
    // this class's own 32px (`--text-2xl`) display type: a wrapped value's two line boxes
    // painted on top of each other instead of stacking, and the second line spilled past the
    // tile's visible bottom border into whatever sat below it. The box model itself was never
    // wrong — `getBoundingClientRect` on the wrapped `<dd>` always fit inside its tile — only
    // the glyphs painted outside their too-short line box.
    //
    // This is deliberately not a snapshot of the current numeric line-height: it recomputes
    // the ratio from the tokens actually declared, so a future change to `--text-2xl` or the
    // leading scale that reintroduces the defect is caught rather than silently accepted.
    const rule = rules(DS_MODULE).find((candidate) => candidate.selector === ".statTileValue");
    expect(rule, ".statTileValue rule must exist in ds.module.css").toBeDefined();
    const lineHeightMatch = /line-height\s*:\s*([^;]+);/.exec(rule!.body);
    expect(lineHeightMatch, ".statTileValue must declare its own line-height").not.toBeNull();

    const leadingToken = lineHeightMatch![1]!.trim();
    const varMatch = /^var\(\s*(--[a-z0-9-]+)\s*\)$/.exec(leadingToken);
    expect(varMatch, "line-height should read from the design system's leading scale").not.toBeNull();
    const leadingValue = Number.parseFloat(TOKENS.get(varMatch![1]!) ?? "");
    expect(Number.isNaN(leadingValue)).toBe(false);

    const fontSizeMatch = /font-size\s*:\s*var\((--[a-z0-9-]+)\)\s*;/.exec(rule!.body);
    expect(fontSizeMatch).not.toBeNull();
    const fontSizePx = Number.parseFloat(TOKENS.get(fontSizeMatch![1]!) ?? "");
    expect(Number.isNaN(fontSizePx)).toBe(false);

    // The Fluent root's inherited line-height for 16px body text (`lineHeightBase300`) —
    // the exact value this class silently inherited before this fix. Any leading that
    // resolves to less than this for a 32px face would reproduce the same overlap.
    const INHERITED_FLUENT_LINE_HEIGHT_PX = 22;
    const resolvedLineHeightPx = leadingValue * fontSizePx;
    expect(resolvedLineHeightPx).toBeGreaterThan(INHERITED_FLUENT_LINE_HEIGHT_PX);
    // And it must actually exceed the font's own size, or lines still collide regardless of
    // what Fluent happens to inherit.
    expect(resolvedLineHeightPx).toBeGreaterThan(fontSizePx);
  });
});

describe("ADR-037 correction 5 — the failing tones are not introduced", () => {
  it("declares neither --success nor --warning", () => {
    // Assertion 10. --warning #c47a00 on #fdf5e6 is 3.16:1 and fails; --success #3a8a52 on
    // white is 4.25:1 and fails. This app has no warning state and no success state, so
    // adopting either would be importing a defect for no delivered requirement. Declaring the
    // token is what would let the tone come back.
    expect(TOKENS.has("--warning")).toBe(false);
    expect(TOKENS.has("--success")).toBe(false);
  });

  it("ships no warning tone class in ds.module.css either", () => {
    expect(DS_MODULE).not.toMatch(/\.noticeWarning\b/);
  });
});

describe("ADR-036 — the fonts, made mechanical", () => {
  it("declares no remote stylesheet import, no font face and no font file", () => {
    // Assertion 11, the same shape as theme.test.ts:317-323 and extended to the second
    // stylesheet. A hotlinked webfont sends every trustee's IP to a third party from a screen
    // rendering Art. 9 counterparts, and Microsoft 365's Aptos licence does not cover
    // self-hosting one. `tokens/fonts.css:2` is what this refuses.
    expect(DS_TOKENS).not.toContain("@import");
    expect(DS_TOKENS).not.toContain("@font-face");
    expect(DS_TOKENS).not.toContain("googleapis");
    expect(DS_TOKENS).not.toMatch(/\.woff2?|\.ttf|\.otf|\.eot/);
    expect(DS_MODULE).not.toContain("@font-face");
  });

  it("carries the SUPPLIED Aptos stacks behind the design system's token names", () => {
    // Assertion 13. Compared family by family rather than as one string, the way
    // theme.test.ts:289-300 does it, because the stylesheet wraps across lines and uses double
    // quotes where theme.ts uses single ones. The design system's own values here are Playfair
    // Display and Nunito Sans, which it flags as substitutions for fonts it could not identify
    // — while Revitalise supplied Aptos and Aptos Display by name (ADR-035, ADR-036).
    const normalise = (stack: string): string[] =>
      stack
        .split(",")
        .map((part) => part.trim().replace(/\s+/g, " ").replace(/["']/g, ""))
        .filter((part) => part.length > 0);

    const body = TOKENS.get("--font-body");
    const display = TOKENS.get("--font-display");
    expect(body).toBeDefined();
    expect(display).toBeDefined();

    expect(normalise(body!)).toEqual(normalise(REV_FONT_FAMILY_BODY));
    expect(normalise(display!)).toEqual(normalise(REV_FONT_FAMILY_HEADING));
    expect(normalise(body!)[0]).toBe("Aptos");
    expect(normalise(display!)[0]).toBe("Aptos Display");
    // The reason naming rather than embedding is safe: the stack has to land somewhere.
    expect(normalise(body!).at(-1)).toBe("sans-serif");
    expect(normalise(display!).at(-1)).toBe("sans-serif");
    // The refused half of ADR-036, pinned: no serif display face is introduced.
    expect(normalise(display!)).not.toContain("Playfair Display");
    expect(normalise(body!)).not.toContain("Nunito Sans");
  });
});

describe("the literal primary is not reachable by hand from this stylesheet", () => {
  it("exposes no --rev-color-primary and never names the failing pairing's value", () => {
    // Assertion 12, extending theme.test.ts:325-328's guard to the second stylesheet. White on
    // the supplied #ED008C is 4.22:1 — it clears the 3:1 large-text/UI-graphic floor and FAILS
    // the 4.5:1 normal-text floor. The guarantee is structural: the primary reaches the UI only
    // through the Fluent ramp in theme.ts, and no hand-written rule in either stylesheet can
    // recreate the white-on-primary pairing if the value is not spellable here.
    expect(DS_TOKENS).not.toContain("--rev-color-primary");
    expect(DS_TOKENS.toLowerCase()).not.toContain("#ed008c");
    expect(DS_MODULE.toLowerCase()).not.toContain("#ed008c");
    // And the arithmetic that makes it a rule rather than a preference.
    expect(contrast(WHITE, brandRamp[80])).toBeGreaterThanOrEqual(LARGE_TEXT_AND_UI_GRAPHICS);
    expect(contrast(WHITE, brandRamp[80])).toBeLessThan(NORMAL_TEXT);
  });

  it("uses a token for every colour in ds.module.css — no raw hex at all", () => {
    // The design system's own `_adherence.oxlintrc.json` forbids raw hex colours, and its own
    // Button.jsx, Input.jsx, Radio.jsx and Checkbox.jsx all violate it. The conversion does not.
    expect(DS_MODULE).not.toMatch(/#[0-9a-f]{3,8}\b/i);
  });
});

describe("what was deliberately NOT copied out of the design system", () => {
  it("copies the :root blocks and none of effects.css's element rules", () => {
    // `tokens/effects.css` carries `body{…}`, `h1,h2,h3,h4{…}`, `a{…}`, `a:hover{…}` and
    // `*{box-sizing:border-box}` after its :root block. Copying them would fight brand.css's own
    // h1..h6 rule (which applies the supplied heading font and the 44px title), restyle every
    // Fluent link, and change box-sizing app-wide. §2.1.2 asks for the custom properties.
    for (const rule of rules(DS_TOKENS)) {
      expect(rule.selector, `unexpected selector in ds-tokens.css: ${rule.selector}`).toBe(
        ":root",
      );
    }
  });

  it("adopts the spacing, radius and type scales verbatim — the part that conflicts with nothing", () => {
    // §8.4.4: these are the design system's real contribution. Spot-checked at both ends of
    // each scale so a truncated copy is caught.
    for (const [token, expected] of [
      ["--space-1", "4px"],
      ["--space-24", "96px"],
      ["--radius-sm", "4px"],
      ["--radius-pill", "999px"],
      ["--text-xs", "13px"],
      ["--text-4xl", "56px"],
      ["--leading-normal", "1.6"],
      ["--weight-bold", "700"],
      ["--container-max", "1200px"],
      ["--border-width", "1px"],
    ] as const) {
      expect(TOKENS.get(token), token).toBe(expected);
    }
  });
});

/**
 * A-R38's OTHER HALF — the one every assertion above is blind to.
 *
 * Everything before this block reads `ds-tokens.css` OFF DISK. That is deliberate and it is what
 * makes the token values guardable at all, because `vitest.config.ts` sets no `css` option, so
 * vitest never processes a CSS import and jsdom resolves no `var()`. But it has a consequence
 * worth stating plainly: **delete the `import "./styles/ds-tokens.css"` line from `main.tsx` and
 * all 29 assertions above still pass**, while the running app renders every `var(--space-6)`,
 * `var(--radius-pill)` and `var(--text-heading)` in seven converted components as nothing at all.
 *
 * That is precisely the failure A-R38 predicted — "460 passing tests asserting markup the app
 * never produces" — and the arithmetic half of its mitigation cannot see it. `gate-cannot-fail` is
 * this project's second-largest recurring class (x33), so the import itself is asserted here
 * rather than trusted to survive review.
 *
 * The harness half matters for a different reason: `src/test/harness.tsx` must compose the same
 * stylesheet set as the composition root, or the two module graphs diverge and a future decision
 * to enable `css: true` would silently apply to only one of them.
 */
describe("the stylesheet is actually loaded by both roots (A-R38)", () => {
  const MAIN = readFileSync(join(__dirname, "..", "main.tsx"), "utf8");
  const HARNESS = readFileSync(join(__dirname, "..", "test", "harness.tsx"), "utf8");

  it("is side-effect imported by the composition root, beside the app's other two globals", () => {
    expect(MAIN).toMatch(/^import\s+"\.\/styles\/ds-tokens\.css";$/m);
    // The other two are asserted alongside it so this reads as one invariant — the app's global
    // stylesheet set — rather than three unrelated lines that happen to be adjacent today.
    expect(MAIN).toMatch(/^import\s+"\.\/styles\/brand\.css";$/m);
    expect(MAIN).toMatch(/^import\s+"\.\/styles\/print\.css";$/m);
  });

  it("is imported by the test harness too, so the two module graphs agree", () => {
    expect(HARNESS).toMatch(/^import\s+"\.\.\/styles\/ds-tokens\.css";$/m);
  });

  it("tokens land before the print reset, which is what lets print.css win the cascade", () => {
    // `print.css`'s `[data-print="state"] { background: none }` and a `ds.module.css` tone class
    // are both (0,1,0), so source order decides. Verified in the built bundle at
    // dist/assets/index-*.css, where @media print emits after every notice rule — this asserts
    // the import order that produces it, which is the half a source change can break.
    const order = ["ds-tokens.css", "brand.css", "print.css"].map((file) =>
      MAIN.indexOf(`import "./styles/${file}"`),
    );
    expect(order.every((position) => position >= 0)).toBe(true);
    expect([...order].sort((a, b) => a - b)).toEqual(order);
  });
});

/**
 * ADR-034's locational boundary, made mechanical (A-R42).
 *
 * "Nothing is generated, vendored or imported from the `Designsystem/` directory at build time —
 * that directory is a design reference that stays outside the app's `src/`." Nothing enforced it,
 * and the failure mode is not hypothetical: the supplied kit is `.jsx` with no types, unlintable
 * under `eslint.config.js`'s `projectService`, and invisible to `npm run typecheck` because
 * `tsconfig.json` sets neither `allowJs` nor `checkJs` — so an import of it would ship
 * un-typechecked source through two green gates (§2.1.1 reasons 1 and 2).
 */
describe("ADR-034 — the design system stays outside src/", () => {
  it("no module under src/ imports from the Designsystem directory", () => {
    // Matched on the IMPORT FORMS specifically, not on any mention of the word: every converted
    // file names its source path in a header comment on purpose (A-R42), this file names the
    // directory in its own assertion, and a rule that fired on the name would forbid the
    // provenance trail the same ADR asks for. What is actually forbidden is a resolvable
    // reference — an ES import, a require, a CSS @import, or a url().
    const FORBIDDEN = [
      /\bfrom\s+["'][^"']*Designsystem/i,
      /\bimport\s+["'][^"']*Designsystem/i,
      /\bimport\s*\(\s*["'][^"']*Designsystem/i,
      /\brequire\s*\(\s*["'][^"']*Designsystem/i,
      /@import\s+(url\()?\s*["'][^"']*Designsystem/i,
      /\burl\(\s*["']?[^"')]*Designsystem/i,
    ];
    const offenders: string[] = [];
    const walk = (directory: string): void => {
      for (const entry of readdirSync(directory, { withFileTypes: true })) {
        const path = join(directory, entry.name);
        if (entry.isDirectory()) {
          walk(path);
          continue;
        }
        if (!/\.(ts|tsx|css)$/.test(entry.name)) continue;
        const body = withoutComments(readFileSync(path, "utf8")).replace(/\/\/.*$/gm, "");
        if (FORBIDDEN.some((pattern) => pattern.test(body))) offenders.push(path);
      }
    };
    walk(join(__dirname, ".."));
    expect(offenders, "these files resolve a reference into Designsystem/").toEqual([]);
  });
});
