/**
 * StatTile — converted from
 * `Designsystem/Revitalise Design System/components/content/StatTile.jsx` and its prop contract
 * `content/StatTile.d.ts` (A-R42, ADR-034).
 *
 * IT RENDERS A `<dt>`/`<dd>` PAIR INSIDE A `<div>`, AND IT MUST BE PLACED INSIDE A `<dl>`.
 * That is not incidental (§8.5 point 3). `Panel.tsx`'s `StatTileRow` is re-implemented over this
 * component and keeps its `<dl>` element, because a `<dl>` of `<dt>`/`<dd>` pairs is a
 * PROGRAMMATIC term/definition association and a `<div><strong>label</strong><span>value</span></div>`
 * — which is what the supplied mockup does — is not one at all (WCAG 1.3.1). The wrapping
 * `<div>` is valid HTML5: a `<dl>` permits each group wrapped in a `<div>`, which
 * `Panel.tsx:74` already records. Rendering a bare `<div>` pair here would have quietly
 * destroyed the property, so the elements are fixed rather than configurable.
 *
 * TWO CORRECTIONS TO THE SUPPLIED COMPONENT:
 *
 *   1. THE LABEL IS NOT `--text-muted` (ADR-037 correction 2). `StatTile.jsx:6` sets the label
 *      in `--text-muted` at `--text-xs` 13px — 3.45:1 on white, and below even the 3:1 floor on
 *      three of the design system's own surfaces. The label is the half that says WHAT THE
 *      NUMBER MEANS: a metric whose name a partially-sighted trustee cannot read is a metric
 *      they cannot identify. It is `--text-body` instead (5.97-6.90:1).
 *   2. `absent` IS NEW (§8.5 point 3). `RoundStatistics.tsx:10-13` states the governing rule —
 *      "a `null` metric renders as nothing at all. Not a zero, not an error, and not a heading
 *      with an empty body" — and `formatPercentage` renders a null as WORDS rather than `0%`
 *      because "on this screen a zero is a finding and an absence is an absence"
 *      (`domain/format.ts:99-113`). The supplied component sets the value in `--font-display` at
 *      `--text-2xl` 32px (`StatTile.jsx:7`), which would set the literal "Not recorded" as a
 *      32px display figure — READING AS A VALUE where an absence is meant. `absent` renders the
 *      same words in body type and body colour instead. The words are unchanged; only their
 *      typographic claim to being a measurement is withdrawn.
 *
 * `children` is `Omit`ted from the DOM contract: this component's content is its label and its
 * value, and accepting children that JSX would then silently discard is worse than not
 * accepting them.
 */
import type { HTMLAttributes } from "react";
import styles from "../../styles/ds.module.css";
import { classNames } from "./classNames";

export interface StatTileProps extends Omit<HTMLAttributes<HTMLDivElement>, "children"> {
  /** What the figure means. Never set in `--text-muted` — see this file's header. */
  label: string;
  /** The figure, already formatted. Always a non-empty string, never a zero for an absence. */
  value: string;
  /** Optional second line under the label, at regular weight. */
  sublabel?: string;
  /**
   * Render `value` as an ABSENCE rather than as a figure: body type and body size instead of
   * the 32px display face. For "Not recorded" and its siblings.
   */
  absent?: boolean;
  /** §8.5 point 7 — see `Button.tsx` for the print vocabulary. */
  "data-print"?: string;
}

export function StatTile({
  label,
  value,
  sublabel,
  absent = false,
  className,
  ...rest
}: StatTileProps) {
  return (
    <div className={classNames(styles.statTile, className)} {...rest}>
      <dt className={styles.statTileLabel}>
        {label}
        {sublabel === undefined || sublabel === "" ? null : (
          <span className={styles.statTileSublabel}>{sublabel}</span>
        )}
      </dt>
      <dd className={absent ? styles.statTileValueAbsent : styles.statTileValue}>{value}</dd>
    </div>
  );
}
