/**
 * Brand theme — NFR-026, ADR-026. A-R26 is CLOSED by this file.
 *
 * NFR-026 asks for full-width, brand-consistent rendering. Fluent UI v9's theme is a
 * token contract, and this app's stylesheet already reads those tokens
 * (`var(--colorNeutralBackground1)` and siblings in `styles/app.module.css`), so brand
 * adoption is a substitution, not a rewrite: build a theme from a brand colour ramp and
 * hand it to the existing `FluentProvider` in `main.tsx`. No component file changes for
 * the colour and type work — the one component change in this pass is the logo, which is
 * an element rather than a token (see `App.tsx`).
 *
 * REAL BRAND VALUES ARE NOW IN PLACE (A-R26 closed, 2026-08-26). Revitalise supplied the
 * primary, secondary, secondary-faded and accent colours, the font colour, the two font
 * names, the title and body sizes, and the logo file. Nothing in this file is a
 * placeholder any more. Four things live here, and one deliberately does not:
 *
 *   1. `brandRamp` — the sixteen-shade `BrandVariants` ramp, generated from the supplied
 *      primary `#ED008C` by Microsoft's own Fluent 2 Theme Designer algorithm
 *      (`microsoft/fluentui`, `packages/react-components/theme-designer/src/colors/*`),
 *      with the sampling anchored so the supplied colour lands EXACTLY at shade 80.
 *      Shade 80 is the anchor because `@fluentui/tokens/lib/alias/lightColor.js` is what
 *      makes `brand[80]` "the" primary colour — it backs `colorBrandBackground`,
 *      `colorCompoundBrandBackground`, `colorBrandForeground1`,
 *      `colorCompoundBrandForeground1`, `colorBrandStroke1` and
 *      `colorBrandBackgroundStatic`. Left unanchored, Microsoft's per-hue heuristic puts
 *      `#ED008C` elsewhere on the ramp and computes shade 80 as `#940055`, a dark maroon,
 *      so "the primary colour" would not have been the primary colour.
 *   2. The brand-background overrides — a real WCAG failure in Fluent's own defaults for
 *      this ramp. See "THE REST-STATE FIX" below.
 *   3. The neutral text overrides — Revitalise's font colour `#002060`, applied to every
 *      token Fluent light resolves to `grey[14]` (`#242424`). All fourteen are foreground
 *      tokens; none is a fill or a stroke, so this changes text colour and nothing else.
 *   4. `fontFamilyBase`, `fontSizeBase300` and `lineHeightBase300` — the body font stack
 *      and the supplied 16px body size. `FluentProvider` itself sets
 *      `font-family: var(--fontFamilyBase)`, `font-size: var(--fontSizeBase300)` and
 *      `line-height: var(--lineHeightBase300)` on its own root element (confirmed in
 *      `@fluentui/react-provider/lib/components/FluentProvider/useFluentProviderStyles.styles.js`),
 *      and every Fluent control reads the same three tokens — so one override moves the
 *      app's inherited body text and every control label together. `22px` is not invented:
 *      it is Fluent's own `lineHeightBase400`, the line height Fluent itself pairs with its
 *      own 16px `fontSizeBase400`.
 *
 * WHAT DELIBERATELY IS NOT HERE. Fluent's theme has exactly one font-family token family
 * (`fontFamilyBase`, `fontFamilyMonospace`, `fontFamilyNumeric` — confirmed in
 * `@fluentui/tokens/lib/global/fonts.js`); there is no heading-font token to override, and
 * no token equals the supplied 44px title size either (Fluent's ramp jumps 40px → 68px). So
 * the heading font stack and the 44px title live in `styles/brand.css` as element rules,
 * which also reaches the `<h1>` on all three views without editing the two page components
 * that render two of them. The three non-ramp brand colours are exported below as literals
 * and declared as custom properties in that same file, because `createLightTheme` accepts
 * one ramp and has nowhere to put a secondary or an accent.
 *
 * ---------------------------------------------------------------------------------------
 * THE FONT LICENCE FINDING — WHY THE BODY FACE SHIPS NO FONT FILE, AND WHY THE HEADING FACE
 * NOW DOES (ADR-042, Revision 7, 2026-08-30 — closes OQ-040)
 *
 * `REV_FONT_FAMILY_BODY` (Aptos) is named and NOT bundled — unchanged by Revision 7.
 * Microsoft 365's inclusion of Aptos licenses install and use on a licensed device, and
 * embedding inside documents; it is not a webfont-embedding licence, and a separate
 * commercial webfont licence (Monotype/MyFonts) exists but is not procured for this
 * engagement. This portal is opened by trustees from their own devices, so self-hosting the
 * file would be exactly the use that licence does not cover. Naming a font in a stack costs
 * nothing and needs no licence — the browser uses Aptos only where the viewer's own device
 * already has it installed (common on current Microsoft 365 Windows machines) and silently
 * falls through otherwise. This is recorded rather than silently substituted.
 *
 * `REV_FONT_FAMILY_HEADING` is DIFFERENT as of Revision 7: it is no longer "Aptos Display"
 * named-only. `readme.md:75` (the supplied design system) instructs headings to use the
 * Playfair Display serif, and the reviewer directed adopting it (ADR-042). The route ADR-036
 * already named for this — "obtain the real files or a licence, self-host under
 * `src/assets/fonts/`" — is the one actually taken: the real Playfair Display files, under the
 * SIL Open Font License 1.1 (which explicitly permits embedding, unlike Aptos's Microsoft 365
 * licence), are bundled and declared via `@font-face` in `styles/ds-tokens.css`, not here —
 * `--font-display` is the token this stack backs, and its self-hosting is documented at that
 * file's own "Font stacks" section. This constant stays the single source of truth for the
 * FAMILY NAME string (`ds-tokens.css` and `brand.css` are both asserted to match it
 * byte-for-byte), even though the file that actually ships the font bytes is not this one.
 *
 * ---------------------------------------------------------------------------------------
 * THE REST-STATE FIX — A REAL AA FAILURE IN FLUENT'S DEFAULTS FOR THIS RAMP
 *
 * `Button appearance="primary"` renders `colorNeutralForegroundOnBrand` (a fixed white,
 * `lightColor.js:50`) on `colorBrandBackground` (`brand[80]`, `lightColor.js:119`) as
 * normal-size label text. With this ramp that pair is 4.22:1 — below the 4.5:1 floor for
 * normal text. Three buttons in this app use that appearance (`VerdictForm.tsx`,
 * `ApplicationsTable.tsx`, `LandingPage.tsx`), so it would have shipped non-compliant.
 *
 * Fluent's own interactive states were already compliant (`brand[70]`/`[40]`/`[60]`); only
 * the two rest-state tokens were not. Moving rest to `brand[70]` alone would have made rest
 * and hover the same colour and removed all hover feedback, so the whole ladder shifts one
 * step. The step SIZE is preserved, not just the compliance:
 *
 *   rest -> hover  Fluent default brand[80] vs brand[70] = 1.297:1
 *                  this theme     brand[70] vs brand[60] = 1.306:1   (marginally stronger)
 *   hover -> press Fluent default brand[70] vs brand[40] = 2.216:1
 *                  this theme     brand[60] vs brand[30] = 2.120:1
 *
 * `colorCompoundBrandBackground` is deliberately LEFT at `brand[80]`. Its only consumer in
 * this app is `.chartBar`'s SVG fill (`styles/app.module.css`) — a UI graphic, which WCAG
 * 1.4.11 holds to 3:1, and 4.22:1 clears it. Grepped: nothing else reads that token, and no
 * text is drawn on it.
 *
 * ---------------------------------------------------------------------------------------
 * CONTRAST CHECK — WCAG 2.1 AA, computed against the values this file actually ships
 * (4.5:1 normal text / 3:1 large text and UI graphics)
 *
 * Text:
 *   - colorNeutralForeground1 (#002060, the brand font colour) on white:      15.27:1 PASS
 *     ... on colorNeutralBackground2 (#fafafa) 14.63:1, Background3 (#f5f5f5) 14.00:1,
 *         colorNeutralBackground1Pressed (#e0e0e0) 11.57:1                          PASS
 *   - colorNeutralForeground2 (#424242) on white:                             10.05:1 PASS
 *   - colorNeutralForeground3 (#616161) on white — `.notAvailable`:            6.19:1 PASS
 *   - colorBrandForegroundLink, brand[70] (#cc0078) on white — `.rowLink`:     5.47:1 PASS
 *   - colorNeutralForegroundOnBrand (#ffffff) on colorBrandBackground,
 *     now brand[70] (#cc0078) — every primary button's rest label:             5.47:1 PASS
 *     ... hover brand[60] 7.15:1, pressed brand[30] 15.15:1, selected brand[50] 9.41:1 PASS
 *
 * UI graphics (>= 3:1):
 *   - colorCompoundBrandBackground, brand[80] (#ed008c) vs white — `.chartBar`: 4.22:1 PASS
 *   - colorBrandStroke1, brand[80], vs colorBrandStroke2Contrast, brand[140]
 *     (#ffdce8) — the Spinner's arc against its own track:                      3.34:1 PASS
 *   - colorCompoundBrandStroke, brand[80], vs white — the Radio indicator:      4.22:1 PASS
 *   - colorStrokeFocus2 (#000000) vs white — the focus ring:                   21.00:1 PASS
 *   - colorPaletteRedBorder2 (#d13438) vs white — `.errorBox`:                  4.93:1 PASS
 *   - `--rev-color-secondary` (#49345B) vs white — the header rule:            10.91:1 PASS
 *
 * TWO CORRECTIONS TO THE SUPPLIED "use white text over the other brand colours" RULE.
 * Both were found by checking each pair rather than trusting the general rule, and both
 * are followed by what ships:
 *
 *   1. ACCENT IS THE EXCEPTION, AND IT IS THE OPPOSITE OF THE RULE. White on
 *      `#14ADBB` is 2.72:1 — it fails normal text AND fails the 3:1 large-text/UI-graphic
 *      floor as well, so there is no size at which it is usable. `#002060` on `#14ADBB` is
 *      5.62:1 and passes. `REV_ON_ACCENT` below is therefore `#002060`, not white, and
 *      `theme.test.ts` pins both halves of that so a later change cannot quietly undo it.
 *   2. WHITE ON THE LITERAL PRIMARY `#ED008C` IS LARGE-TEXT-ONLY. 4.22:1 clears the 3:1
 *      large-text floor (>=24px, or >=18.7px bold) and the UI-graphic floor, and fails the
 *      4.5:1 normal-text floor. Nothing in this app pairs them: the primary is reachable
 *      only through the Fluent ramp (no `--rev-color-primary` custom property exists, on
 *      purpose, so no stylesheet can create that pairing by hand), and the one token that
 *      still resolves to `#ED008C` behind text — `colorBrandBackground` — was moved to
 *      `brand[70]` by the rest-state fix above.
 *
 * White on the secondary (10.91:1) and on the secondary-faded (6.50:1) do follow the
 * supplied rule, and `REV_ON_SECONDARY` is white accordingly.
 */
import { createLightTheme } from "@fluentui/react-components";
import type { BrandVariants, Theme } from "@fluentui/react-components";

/**
 * Revitalise's primary, as a Fluent brand ramp. 10 = darkest .. 160 = lightest, and
 * shade 80 is the supplied `#ED008C` exactly, by construction — see this file's header.
 */
export const brandRamp: BrandVariants = {
  10: "#0c0004",
  20: "#36001c",
  30: "#51002c",
  40: "#6e003e",
  50: "#8c0050",
  60: "#ac0064",
  70: "#cc0078",
  80: "#ed008c",
  90: "#fe379c",
  100: "#ff66ab",
  110: "#ff89b9",
  120: "#ffa7c9",
  130: "#ffc2d8",
  140: "#ffdce8",
  150: "#fff5f9",
  160: "#ffffff",
};

/**
 * The three supplied brand colours Fluent's theme has nowhere to put, plus the verified
 * foreground for each. `createLightTheme` takes one ramp; a secondary and an accent are
 * not part of that system, so they are declared as CSS custom properties in
 * `styles/brand.css` and exported here as the single source of truth for those values.
 * `theme.test.ts` reads that stylesheet off disk and asserts the two agree, which is the
 * same drift guard `styles/print.test.ts` already applies to the print stylesheet.
 *
 * There is deliberately no `REV_PRIMARY`. The primary reaches the UI through `brandRamp`
 * and Fluent's own tokens; exposing it as a hand-usable value is how the 4.22:1
 * white-on-primary pairing would get recreated in a stylesheet later.
 */
export const REV_SECONDARY = "#49345b";
export const REV_SECONDARY_FADED = "#6a5774";
export const REV_ACCENT = "#14adbb";

/** White, 10.91:1 on the secondary and 6.50:1 on the faded secondary. */
export const REV_ON_SECONDARY = "#ffffff";

/**
 * `#002060` at 5.62:1, NOT white at 2.72:1. Correction 1 in this file's header: the accent
 * is the one supplied colour where white fails every WCAG threshold, large text included.
 */
export const REV_ON_ACCENT = "#002060";

/** The supplied font colour. 15.27:1 on white. */
export const REV_FONT_COLOUR = "#002060";

/**
 * Aptos by name only — no font file is bundled and no `@font-face` rule exists anywhere in
 * this app for the BODY face. See "THE FONT LICENCE FINDING" in this file's header for why.
 */
export const REV_FONT_FAMILY_BODY =
  "'Aptos', 'Segoe UI Variable', 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif";

/**
 * Playfair Display, self-hosted (ADR-042, Revision 7, 2026-08-30 — closes OQ-040). Unlike
 * `REV_FONT_FAMILY_BODY` above, this face's real files ARE bundled — as `@font-face` rules
 * with `data:` URIs in `styles/ds-tokens.css`, under the SIL Open Font License 1.1. This
 * constant is still the single source of truth for the family-name STRING; the font bytes
 * themselves live in `styles/ds-tokens.css` and `src/assets/fonts/playfair-display/`.
 */
export const REV_FONT_FAMILY_HEADING =
  "'Playfair Display', Georgia, Cambria, 'Times New Roman', Times, serif";

/** The supplied body size. Fluent's own default for this token is 14px. */
export const REV_BODY_FONT_SIZE = "16px";

/**
 * Fluent's own `lineHeightBase400` — the line height it pairs with its own 16px
 * `fontSizeBase400`. Fluent's default `lineHeightBase300` is 20px, which pairs with 14px.
 */
export const REV_BODY_LINE_HEIGHT = "22px";

/**
 * The rest-state fix. `brand[80]` behind white normal-size text is 4.22:1 and fails AA;
 * the whole state ladder therefore shifts one step down the ramp so that rest passes and
 * hover stays visibly distinct from it. Numbers and reasoning: this file's header.
 */
const brandBackgroundOverrides = {
  colorBrandBackground: brandRamp[70],
  colorBrandBackgroundStatic: brandRamp[70],
  colorBrandBackgroundHover: brandRamp[60],
  colorBrandBackgroundPressed: brandRamp[30],
  colorBrandBackgroundSelected: brandRamp[50],
} satisfies Partial<Theme>;

/**
 * Every token Fluent light resolves to `grey[14]` (`#242424`), set to the supplied font
 * colour. The list is exhaustive — `grep ': grey\[14\],' @fluentui/tokens/lib/alias/lightColor.js`
 * returns exactly these fourteen — and every one of them is a foreground token, so this
 * moves text colour only and cannot change a fill or a stroke.
 *
 * The Hover/Pressed/Selected siblings matter as much as the base: Fluent sets them to the
 * same `grey[14]`, so overriding only `colorNeutralForeground1` would make text flip from
 * navy back to `#242424` on hover. `colorNeutralForeground2`/`3` themselves stay Fluent's
 * greys (`#424242` at 10.05:1, `#616161` at 6.19:1) — de-emphasised text is meant to be
 * de-emphasised, and inventing brand-tinted greys would be inventing brand values nobody
 * supplied.
 */
const neutralTextOverrides = {
  colorNeutralForeground1: REV_FONT_COLOUR,
  colorNeutralForeground1Hover: REV_FONT_COLOUR,
  colorNeutralForeground1Pressed: REV_FONT_COLOUR,
  colorNeutralForeground1Selected: REV_FONT_COLOUR,
  colorNeutralForeground1Static: REV_FONT_COLOUR,
  colorNeutralForeground2Hover: REV_FONT_COLOUR,
  colorNeutralForeground2Pressed: REV_FONT_COLOUR,
  colorNeutralForeground2Selected: REV_FONT_COLOUR,
  colorNeutralForeground2LinkHover: REV_FONT_COLOUR,
  colorNeutralForeground2LinkPressed: REV_FONT_COLOUR,
  colorNeutralForeground2LinkSelected: REV_FONT_COLOUR,
  colorNeutralForeground5Hover: REV_FONT_COLOUR,
  colorNeutralForeground5Pressed: REV_FONT_COLOUR,
  colorNeutralForeground5Selected: REV_FONT_COLOUR,
} satisfies Partial<Theme>;

/**
 * The theme handed to `FluentProvider` in `main.tsx`. `createLightTheme` returns a flat
 * record of 459 string values, so a spread-override is the whole mechanism — there is no
 * nested structure to merge.
 */
export const brandTheme: Theme = {
  ...createLightTheme(brandRamp),
  ...brandBackgroundOverrides,
  ...neutralTextOverrides,
  fontFamilyBase: REV_FONT_FAMILY_BODY,
  fontSizeBase300: REV_BODY_FONT_SIZE,
  lineHeightBase300: REV_BODY_LINE_HEIGHT,
};
