/**
 * The brand theme — NFR-026, ADR-026, A-R26.
 *
 * WHAT THIS FILE IS FOR. ADR-026 and TAD §8.2 both require every brand colour pair to be
 * contrast-verified. Until this pass that verification lived only in `theme.ts`'s header
 * comment, i.e. in prose that nothing re-checks. One of those pairs turned out to be a real
 * WCAG failure in Fluent's own defaults (white normal-size text on `brand[80]`, 4.22:1), so
 * the arithmetic is executed here instead: the ratios are computed from the values the app
 * actually ships, and a later ramp or token change that breaks AA fails a test rather than
 * shipping.
 *
 * The contrast function is WCAG 2.1's own definition (relative luminance, then
 * (L1 + 0.05) / (L2 + 0.05)) written out in full rather than pulled from a dependency —
 * this app adds no dependency for eight lines of arithmetic, and a hand-checkable formula is
 * the point.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import {
  REV_ACCENT,
  REV_BODY_FONT_SIZE,
  REV_FONT_COLOUR,
  REV_FONT_FAMILY_BODY,
  REV_FONT_FAMILY_HEADING,
  REV_ON_ACCENT,
  REV_ON_SECONDARY,
  REV_SECONDARY,
  REV_SECONDARY_FADED,
  brandRamp,
  brandTheme,
} from "./theme";

/** WCAG 2.1 relative luminance. */
function luminance(hex: string): number {
  const value = hex.replace("#", "");
  const channels = [0, 2, 4].map((offset) => Number.parseInt(value.slice(offset, offset + 2), 16) / 255);
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

describe("the contrast function itself", () => {
  // A contrast check whose arithmetic is wrong would pass everything below for the wrong
  // reason. These three are fixed points nobody has to trust this file for.
  it("computes the two known extremes and one published Fluent figure", () => {
    expect(contrast("#000000", WHITE)).toBe(21);
    expect(contrast(WHITE, WHITE)).toBe(1);
    // Fluent light's own body text: colorNeutralForeground1 #242424 on white.
    expect(contrast("#242424", WHITE)).toBe(15.52);
  });
});

describe("the brand ramp", () => {
  it("puts Revitalise's supplied primary at exactly shade 80", () => {
    // Not cosmetic. brand[80] is the shade Fluent's own alias layer treats as "the" brand
    // colour — it backs colorBrandBackground, colorCompoundBrandBackground,
    // colorBrandForeground1, colorCompoundBrandForeground1, colorBrandStroke1 and
    // colorBrandBackgroundStatic. If the supplied colour sits anywhere else on the ramp,
    // "the primary colour" is not the primary colour.
    expect(brandRamp[80]).toBe("#ed008c");
  });

  it("has all sixteen shades, darkest to lightest", () => {
    const shades = Object.keys(brandRamp).map(Number);
    expect(shades).toHaveLength(16);
    const luminances = shades.map((shade) => luminance(brandRamp[shade as keyof typeof brandRamp]));
    const ascending = [...luminances].sort((a, b) => a - b);
    expect(luminances).toEqual(ascending);
  });
});

describe("WCAG 2.1 AA — text on a brand fill", () => {
  const onBrand = brandTheme.colorNeutralForegroundOnBrand;

  it("uses a fixed white as the foreground on every brand fill", () => {
    // The premise of every assertion in this block. Fluent hard-codes it rather than taking
    // it from the ramp, so a ramp change cannot move it and the fill has to do the work.
    expect(onBrand).toBe(WHITE);
  });

  it("passes normal-text contrast in the REST state (the bug this fix exists for)", () => {
    // Fluent's default colorBrandBackground is brand[80], which is 4.22:1 against white and
    // FAILS. Three buttons in this app render `appearance="primary"` — VerdictForm,
    // ApplicationsTable, LandingPage — and Fluent draws that label as normal-size text.
    expect(contrast(onBrand, brandTheme.colorBrandBackground)).toBeGreaterThanOrEqual(NORMAL_TEXT);
    expect(contrast(onBrand, brandTheme.colorBrandBackground)).toBe(5.47);
    expect(brandTheme.colorBrandBackground).toBe(brandRamp[70]);
  });

  it("passes normal-text contrast in every other brand-fill state too", () => {
    for (const token of [
      "colorBrandBackgroundStatic",
      "colorBrandBackgroundHover",
      "colorBrandBackgroundPressed",
      "colorBrandBackgroundSelected",
    ] as const) {
      expect(contrast(onBrand, brandTheme[token]), token).toBeGreaterThanOrEqual(NORMAL_TEXT);
    }
  });

  it("keeps every interactive state a visibly different colour from the others", () => {
    // The regression the rest-state fix could have introduced: move REST down to brand[70]
    // and it becomes Fluent's own default HOVER value, so a primary button would stop
    // responding visibly to a pointer. Every state must be a distinct value.
    const states = [
      brandTheme.colorBrandBackground,
      brandTheme.colorBrandBackgroundHover,
      brandTheme.colorBrandBackgroundPressed,
      brandTheme.colorBrandBackgroundSelected,
    ];
    expect(new Set(states).size).toBe(states.length);
  });

  it("keeps the rest-to-hover step at least as strong as Fluent's own default step", () => {
    // Distinct is not the same as noticeable. Fluent's default step is brand[80] -> brand[70]
    // (1.3:1); this theme's is brand[70] -> brand[60], and must not be a weaker signal.
    const fluentDefaultStep = contrast(brandRamp[80], brandRamp[70]);
    const shippedStep = contrast(brandTheme.colorBrandBackground, brandTheme.colorBrandBackgroundHover);
    expect(shippedStep).toBeGreaterThanOrEqual(fluentDefaultStep);
  });
});

describe("WCAG 2.1 AA — brand text and graphics on the page background", () => {
  it("puts body text at the supplied font colour, on white and on every light surface", () => {
    expect(brandTheme.colorNeutralForeground1).toBe(REV_FONT_COLOUR);
    for (const background of [
      "colorNeutralBackground1",
      "colorNeutralBackground2",
      "colorNeutralBackground3",
      "colorNeutralBackground1Hover",
      "colorNeutralBackground1Pressed",
    ] as const) {
      expect(
        contrast(brandTheme.colorNeutralForeground1, brandTheme[background]),
        background,
      ).toBeGreaterThanOrEqual(NORMAL_TEXT);
    }
  });

  it("never lets neutral text flip back to Fluent's grey on hover or press", () => {
    // Fluent sets the Hover/Pressed/Selected siblings to the same grey[14] as the base, so
    // overriding only the base would make text change colour under the pointer.
    for (const token of [
      "colorNeutralForeground1Hover",
      "colorNeutralForeground1Pressed",
      "colorNeutralForeground1Selected",
      "colorNeutralForeground1Static",
      "colorNeutralForeground2Hover",
      "colorNeutralForeground2Pressed",
      "colorNeutralForeground2Selected",
    ] as const) {
      expect(brandTheme[token], token).toBe(REV_FONT_COLOUR);
    }
  });

  it("passes normal-text contrast on the row link and the de-emphasised text classes", () => {
    // .rowLink reads colorBrandForegroundLink; .notAvailable and .hint read
    // colorNeutralForeground3 and 2 (styles/app.module.css).
    for (const token of [
      "colorBrandForegroundLink",
      "colorNeutralForeground2",
      "colorNeutralForeground3",
    ] as const) {
      expect(
        contrast(brandTheme[token], brandTheme.colorNeutralBackground1),
        token,
      ).toBeGreaterThanOrEqual(NORMAL_TEXT);
    }
  });

  it("clears the UI-graphic floor for the chart bar, the focus ring and the error border", () => {
    // .chartBar fills with colorCompoundBrandBackground, which theme.ts deliberately leaves
    // at brand[80]: no text is drawn on it, so WCAG 1.4.11's 3:1 is the floor that applies.
    for (const token of [
      "colorCompoundBrandBackground",
      "colorCompoundBrandStroke",
      "colorStrokeFocus2",
      "colorPaletteRedBorder2",
    ] as const) {
      expect(
        contrast(brandTheme[token], brandTheme.colorNeutralBackground1),
        token,
      ).toBeGreaterThanOrEqual(LARGE_TEXT_AND_UI_GRAPHICS);
    }
    expect(brandTheme.colorCompoundBrandBackground).toBe(brandRamp[80]);
  });

  it("keeps the Spinner's arc visible against its own track", () => {
    expect(
      contrast(brandTheme.colorBrandStroke1, brandTheme.colorBrandStroke2Contrast),
    ).toBeGreaterThanOrEqual(LARGE_TEXT_AND_UI_GRAPHICS);
  });
});

describe("the two corrections to the supplied 'white over the brand colours' rule", () => {
  it("uses the font colour on the accent, NOT white — white fails at every text size", () => {
    // Correction 1, and it reverses the supplied rule for this one colour. Both halves are
    // pinned: that white is unusable, and that the shipped foreground is the one that works.
    expect(contrast(WHITE, REV_ACCENT)).toBeLessThan(LARGE_TEXT_AND_UI_GRAPHICS);
    expect(REV_ON_ACCENT).not.toBe(WHITE);
    expect(contrast(REV_ON_ACCENT, REV_ACCENT)).toBeGreaterThanOrEqual(NORMAL_TEXT);
  });

  it("records that white on the literal primary is large-text-only, and never ships it", () => {
    // Correction 2. 4.22:1 clears the 3:1 large-text/UI-graphic floor and fails the 4.5:1
    // normal-text floor, so the literal primary must not sit behind body-size text. The
    // guarantee is structural: brand[80] reaches the UI only through Fluent's own tokens,
    // and the one that puts text on a brand fill was moved off it.
    expect(contrast(WHITE, brandRamp[80])).toBeGreaterThanOrEqual(LARGE_TEXT_AND_UI_GRAPHICS);
    expect(contrast(WHITE, brandRamp[80])).toBeLessThan(NORMAL_TEXT);
    expect(brandTheme.colorBrandBackground).not.toBe(brandRamp[80]);
    expect(brandTheme.colorBrandBackgroundStatic).not.toBe(brandRamp[80]);
  });

  it("does follow the supplied rule on the secondary and the faded secondary", () => {
    expect(REV_ON_SECONDARY).toBe(WHITE);
    expect(contrast(REV_ON_SECONDARY, REV_SECONDARY)).toBeGreaterThanOrEqual(NORMAL_TEXT);
    expect(contrast(REV_ON_SECONDARY, REV_SECONDARY_FADED)).toBeGreaterThanOrEqual(NORMAL_TEXT);
  });
});

describe("typography", () => {
  it("sets the supplied body size on the token FluentProvider and every control read", () => {
    // FluentProvider's own root sets font-size: var(--fontSizeBase300), so this one token
    // moves the app's inherited body text and every Fluent control label together.
    expect(brandTheme.fontSizeBase300).toBe(REV_BODY_FONT_SIZE);
    expect(brandTheme.fontSizeBase300).toBe("16px");
  });

  it("pairs the body size with Fluent's own line height for that size, not the 14px one", () => {
    // Fluent's default lineHeightBase300 is 20px, which pairs with its default 14px. 22px is
    // Fluent's own lineHeightBase400, the height it pairs with its own 16px fontSizeBase400.
    expect(brandTheme.lineHeightBase300).toBe("22px");
    expect(brandTheme.lineHeightBase300).toBe(brandTheme.lineHeightBase400);
  });

  it("names Aptos in the body stack and bundles no font file", () => {
    expect(brandTheme.fontFamilyBase).toBe(REV_FONT_FAMILY_BODY);
    expect(brandTheme.fontFamilyBase).toContain("'Aptos'");
  });

  it("gives both stacks a real fallback chain, because Aptos is often absent", () => {
    // The whole point of naming rather than embedding: on a device without Aptos the stack
    // has to land somewhere sensible, and must end at a generic family.
    for (const stack of [REV_FONT_FAMILY_BODY, REV_FONT_FAMILY_HEADING]) {
      const families = stack.split(",").map((part) => part.trim());
      expect(families.length).toBeGreaterThan(4);
      expect(families.at(-1)).toBe("sans-serif");
      expect(families).toContain("'Segoe UI'");
    }
  });
});

describe("styles/brand.css — the values Fluent's theme has no token for", () => {
  // Comments stripped before anything is asserted, the same way print.test.ts does it. That
  // stylesheet's header discusses `@font-face` and the failing `#ED008C` pairing by name in
  // prose; a rule and a warning about a rule must not be confused for each other.
  const BRAND_CSS = readFileSync(join(__dirname, "styles", "brand.css"), "utf8").replace(
    /\/\*[\s\S]*?\*\//g,
    "",
  );

  it("declares the same colour values theme.ts exports, with no drift", () => {
    // Two files naming the same colour is the drift risk. theme.ts is the source of truth;
    // this asserts the stylesheet agrees, the same way print.test.ts guards print.css.
    for (const [property, expected] of [
      ["--rev-color-secondary", REV_SECONDARY],
      ["--rev-color-secondary-faded", REV_SECONDARY_FADED],
      ["--rev-color-accent", REV_ACCENT],
      ["--rev-color-on-secondary", REV_ON_SECONDARY],
      ["--rev-color-on-accent", REV_ON_ACCENT],
    ] as const) {
      expect(BRAND_CSS, property).toMatch(new RegExp(`${property}:\\s*${expected};`));
    }
  });

  it("carries the heading font stack theme.ts exports", () => {
    // Same stack, CSS quoting. Compared family by family rather than as one string, because
    // the stylesheet wraps across lines and uses double quotes.
    const declared = /--rev-font-family-heading:([^;]+);/.exec(BRAND_CSS)?.[1] ?? "";
    const normalise = (stack: string): string[] =>
      stack
        .split(",")
        .map((part) => part.trim().replace(/\s+/g, " ").replace(/["']/g, ""))
        .filter((part) => part.length > 0);
    expect(normalise(declared)).toEqual(normalise(REV_FONT_FAMILY_HEADING));
    expect(normalise(declared)[0]).toBe("Aptos Display");
  });

  it("honours the supplied 44px title size and still reflows at 320px (WCAG 1.4.10)", () => {
    // A fixed 44px would make "Applications" wider than the 288px of content a 320px
    // viewport has, forcing the page body to scroll sideways. clamp() honours 44px wherever
    // it fits and falls back below that.
    expect(BRAND_CSS).toMatch(/--rev-font-size-title:\s*clamp\(\s*\d+px\s*,[^,]+,\s*44px\s*\)/);
    expect(BRAND_CSS).toMatch(/h1\s*\{[^}]*font-size:\s*var\(--rev-font-size-title\)/);
  });

  it("gives the 44px title its own line height rather than inheriting the body's", () => {
    // An <h1> inherits line-height from FluentProvider's root, which is 22px. At 44px that
    // overlaps its own second line.
    expect(BRAND_CSS).toMatch(/--rev-line-height-title:\s*1\.2/);
    expect(BRAND_CSS).toMatch(/h1\s*\{[^}]*line-height:\s*var\(--rev-line-height-title\)/);
  });

  it("bundles no font file and declares no @font-face anywhere", () => {
    // The licence finding, made structural: Microsoft 365's Aptos licence does not cover
    // self-hosting a webfont, so Aptos is named and never served. A future @font-face rule
    // pointing at a bundled Aptos file is the thing this must catch.
    expect(BRAND_CSS).not.toContain("@font-face");
    expect(BRAND_CSS).not.toMatch(/\.woff2?|\.ttf|\.otf|\.eot/);
  });

  it("exposes no primary custom property, so no stylesheet can recreate the failing pair", () => {
    expect(BRAND_CSS).not.toContain("--rev-color-primary");
    expect(BRAND_CSS.toLowerCase()).not.toContain("#ed008c");
  });
});
