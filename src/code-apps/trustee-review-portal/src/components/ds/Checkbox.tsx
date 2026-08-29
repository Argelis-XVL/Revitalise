/**
 * Checkbox — converted from
 * `Designsystem/Revitalise Design System/components/forms/Checkbox.jsx` and its prop contract
 * `forms/Checkbox.d.ts` (A-R42, ADR-034).
 *
 * The same shape as `Radio.tsx` and for the same reasons: the control sits inside its own
 * `<label>` (an implicit and correct label association, WCAG 1.3.1 / 3.3.2), `type` is
 * `Omit`ted so a checkbox cannot be configured into something else, `.choice` raises the click
 * target to 44x44 by giving the label the height (WCAG 2.5.5 — the design system sets no height
 * and its target is the 18px box), `data-print` lands on the outermost `<label>` so the caption
 * is hidden with the control, and `role` reaches the `<input>` because that is the semantic
 * element.
 *
 * No consumer exists in the app today. It is converted because it is one of the seven components
 * ADR-033 adopts and the design system's own forms use it; `Accordion`, `Badge`, `Navbar`,
 * `Footer`, `CookieBanner` and `NewsletterForm` are deliberately NOT converted for the opposite
 * reason (§2.1.2 — dead code still has to be maintained, audited and covered).
 */
import type { InputHTMLAttributes } from "react";
import styles from "../../styles/ds.module.css";
import { classNames } from "./classNames";

export interface CheckboxProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, "type"> {
  /** The visible, programmatically associated label. Required by the supplied contract. */
  label: string;
  /** §8.5 point 7 — see `Button.tsx` for the print vocabulary. */
  "data-print"?: string;
}

export function Checkbox({
  label,
  className,
  "data-print": dataPrint,
  ...rest
}: CheckboxProps) {
  return (
    <label className={classNames(styles.choice, className)} data-print={dataPrint}>
      <input type="checkbox" className={styles.choiceControl} {...rest} />
      {label}
    </label>
  );
}
