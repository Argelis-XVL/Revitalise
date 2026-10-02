/**
 * The card app's chart-mark and decoration palettes — Design 2.0 Revision 3 (fidelity audit,
 * 2026-10-01). Card app only (`src/cards/**` is presentation); the first app keeps
 * `categoricalColor` from `domain/charts.ts` (contract), which this module does not change.
 *
 * MARKS (bars, columns, donut slices, grouped series). The kit's own five-step palette,
 * `RoundOverview.jsx` line 3: brand pink, purple #49345b, teal #14adbb, pink-300, purple-faded
 * #6a5774. A chart mark is a graphic that carries meaning, so it needs 3:1 against the white card
 * (WCAG 1.4.11). Measured against #ffffff:
 *
 *   #e6027f 4.49:1  kept (graphics only; as TEXT it fails 4.5:1 and is --pink-700 elsewhere)
 *   #49345b 10.91:1 kept
 *   #14adbb 2.72:1  NOT kept — TAD §8.3 row "Chart mark in teal"; replaced by #009aa8 (3.39:1), the
 *                   teal `categoricalColor` already validated (domain/charts.ts)
 *   #f28cc6 2.25:1  NOT kept — TAD §8.3 row "Chart mark in --pink-300"; replaced by --pink-500
 *                   #ec4ea3 (3.40:1), the nearest kit pink that clears 3:1. TAD §8.3 names
 *                   `--pink-500` as the replacement (R17).
 *   #6a5774 6.50:1  kept
 *
 * DECORATIONS (the groups table's member dots, `GroupScreens.jsx` line 37). Those are
 * `aria-hidden` and carry no information (the member count is text beside them), so WCAG 1.4.11
 * does not apply and the kit's four colours are used exactly, teal and pink-300 included.
 *
 * ADOPTED BY THE TAD (R17, TAD Revision 3.2, 2026-10-01): §8.3's palette rows, §13.2, ADR-063
 * decision 3 and Appendix B #27 now name this palette, replacing Revision 2's "marks keep
 * `categoricalColor`" (the conflict IMP-1003 recorded). The pink-500 substitute is §8.3's.
 */
export const CARD_MARK_PALETTE = ["#e6027f", "#49345b", "#009aa8", "#ec4ea3", "#6a5774"] as const;

/** The kit's member-dot cycle, exactly: brand pink, purple, teal, pink-300. */
export const MEMBER_DOT_PALETTE = ["#e6027f", "#49345b", "#14adbb", "#f28cc6"] as const;

/** The kit's `PALETTE[i % PALETTE.length]` — fixed order, cycling after five. */
export function markColor(index: number): string {
  return CARD_MARK_PALETTE[index % CARD_MARK_PALETTE.length] ?? CARD_MARK_PALETTE[0];
}

export function memberDotColor(index: number): string {
  return MEMBER_DOT_PALETTE[index % MEMBER_DOT_PALETTE.length] ?? MEMBER_DOT_PALETTE[0];
}
