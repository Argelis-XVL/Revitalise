/**
 * Radio — converted from `Designsystem/Revitalise Design System/components/forms/Radio.jsx` and
 * its prop contract `forms/Radio.d.ts` (A-R42, ADR-034).
 *
 * WHAT THIS COMPONENT IS AND IS NOT. It is a single styled radio input with an implicit label,
 * and nothing more. It is NOT a radio group: §2.1.4 keeps Fluent's `RadioGroup` precisely
 * because a group carries roving tabindex and arrow-key behaviour, and the supplied
 * `Radio.jsx:6` is a bare `<input type="radio">` with an `accentColor` — the mockup wires three
 * of them with no group semantics at all (`ui_kits/…/ApplicationDetail.jsx:64-66`). So this
 * replaces Fluent's `Radio`, and Fluent's `RadioGroup`, `Field` and `Label` stay around it.
 *
 * `type` IS `Omit`TED FROM THE PROPS. A `Radio` that renders a checkbox is a bug, not a
 * configuration, and making it a compile error is cheaper than making it a code review.
 *
 * TARGET SIZE. The design system sets no height, so its target is the 18px control (WCAG 2.5.5
 * asks 44x44). `.choice` gives the whole `<label>` a 44px minimum height, and because the label
 * IS the click target that raises the target rather than only the box.
 *
 * `data-print` lands on the `<label>` — the outermost element — so hiding the control on paper
 * hides its caption with it. `role` goes to the `<input>`, the semantic control.
 */
import type { InputHTMLAttributes } from "react";
import styles from "../../styles/ds.module.css";
import { classNames } from "./classNames";

export interface RadioProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, "type"> {
  /** The visible, programmatically associated label. Required by the supplied contract. */
  label: string;
  /** §8.5 point 7 — see `Button.tsx` for the print vocabulary. */
  "data-print"?: string;
}

export function Radio({
  label,
  className,
  "data-print": dataPrint,
  ...rest
}: RadioProps) {
  return (
    <label className={classNames(styles.choice, className)} data-print={dataPrint}>
      <input type="radio" className={styles.choiceControl} {...rest} />
      {label}
    </label>
  );
}
