/**
 * Brand theme — NFR-026, ADR-026.
 *
 * NFR-026 asks for full-width, brand-consistent rendering. Fluent UI v9's theme is a
 * token contract, and this app's stylesheet already reads those tokens
 * (`var(--colorNeutralBackground1)` and siblings in `styles/app.module.css`), so brand
 * adoption is a substitution, not a rewrite: build a theme from a brand colour ramp and
 * hand it to the existing `FluentProvider` in `main.tsx`. No component file changes.
 *
 * THE ONE THING THAT NEEDS REPLACING WHEN REAL BRAND VALUES ARRIVE (A-R26): `brandRamp`
 * below, and nothing else in this file. As of 2026-08-25 the public Revitalise site
 * returned no colour, font or logo value in its served markup — see
 * docs/architecture/trustee-portal-visual-refresh-architecture.md §10 ADR-026 and §11
 * A-R26 — so there is no real brand ramp to build from, and inventing one would ship a
 * brand identity nobody at Revitalise has approved. `brandRamp` is therefore Fluent's own
 * default web ramp (`brandWeb` from `@fluentui/tokens` — the same sixteen shades that
 * already produce `webLightTheme`), reproduced here as a literal so the one constant that
 * must change on brand handover is visible in this file alone. Until replaced, this theme
 * renders byte-for-byte the same as `webLightTheme` — visibly still Fluent-default, not a
 * brand choice nobody signed off. Swap only this object for Revitalise's own sixteen-shade
 * ramp (10 = darkest .. 160 = lightest) once supplied, then re-run the contrast check
 * this file's own comments describe below against the new values.
 *
 * No brand font stack for the same reason: `createLightTheme` leaves `fontFamilyBase` at
 * Fluent's default, and this file does not override it. A brand font is as much an input
 * this document does not have as the colour ramp is (A-R26).
 *
 * Contrast check performed against this placeholder ramp (WCAG 2.1 AA — see the dev
 * summary for the full working):
 *   - colorNeutralForeground1 (#242424) on colorNeutralBackground1 (#ffffff): 15.52:1
 *   - colorNeutralForeground2 (#424242) on white: 10.05:1
 *   - colorNeutralForeground3 (#616161) on white: 6.19:1 — `.notAvailable`, `.hint`
 *   - colorBrandForegroundLink, brand[70] (#115ea3) on white: 6.66:1 — `.rowLink`
 *   - colorCompoundBrandForeground1, brand[80] (#0f6cbd) on white: 5.38:1
 *   - colorStrokeFocus2 (#000000) vs white: 21:1 — focus ring, UI graphic (>=3:1 needed)
 *   - colorPaletteRedBorder2 (#d13438) vs white: 4.93:1 — `.errorBox` border (>=3:1 needed)
 * All exceed the 4.5:1 (normal text) / 3:1 (UI graphics, large text) AA floor. Because
 * `brandRamp` reproduces `brandWeb` exactly, this is arithmetic confirmation of what
 * Fluent already ships as `webLightTheme`, not a new claim — see ADR-026's own point that
 * "Fluent's own default theme is already accessible by design", confirmed rather than
 * assumed here.
 */
import { createLightTheme } from "@fluentui/react-components";
import type { BrandVariants, Theme } from "@fluentui/react-components";

// PLACEHOLDER — Fluent's default ramp until Revitalise supplies real brand colours (A-R26).
export const brandRamp: BrandVariants = {
  10: "#061724",
  20: "#082338",
  30: "#0a2e4a",
  40: "#0c3b5e",
  50: "#0e4775",
  60: "#0f548c",
  70: "#115ea3",
  80: "#0f6cbd",
  90: "#2886de",
  100: "#479ef5",
  110: "#62abf5",
  120: "#77b7f7",
  130: "#96c6fa",
  140: "#b4d6fa",
  150: "#cfe4fa",
  160: "#ebf3fc",
};

export const brandTheme: Theme = createLightTheme(brandRamp);
