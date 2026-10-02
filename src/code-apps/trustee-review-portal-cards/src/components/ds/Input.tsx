/**
 * Input — converted from `Designsystem/Revitalise Design System/components/forms/Input.jsx` and
 * its prop contract `forms/Input.d.ts` (A-R42, ADR-034).
 *
 * THREE CORRECTIONS, AND THE FIRST IS THE ONE A VERBATIM PORT WOULD HAVE BROKEN ON DAY ONE:
 *
 *   1. WITH NO `label` PROP IT RENDERS A BARE `<input>` AND NO WRAPPER. The supplied
 *      `Input.jsx:4-20` ALWAYS wraps its `<input>` in its own `<label>`. This app's filter
 *      controls pair an EXTERNAL Fluent `<Label htmlFor>` with the input's `id`
 *      (`ApplicationFilters.tsx`), and Fluent's `Label` and `Select` both stay (§2.1.4). A
 *      second, nested `<label>` around an input that an outer label already points at is a
 *      broken label association (WCAG 1.3.1, 3.3.2) — the browser resolves the innermost, so
 *      the authored visible label stops being the accessible name. The wrapping behaviour is
 *      kept and made CONDITIONAL rather than removed, because the supplied form layouts do use
 *      it.
 *   2. `outline: none` IS DROPPED, NOT CARRIED (ADR-037 correction 3). `Input.jsx:17` sets it
 *      with no replacement, which is the removal of the visible focus indicator — WCAG 2.4.7
 *      outright, not a contrast miss. `ds.module.css`'s `.inputField:focus-visible` supplies a
 *      `var(--focus-ring)` ring instead (#000000, 17.41-21.00:1 on every surface), matching
 *      `app.module.css:45` and `:193-197`. `ds-tokens.test.ts` asserts no `outline: none`
 *      survives anywhere in that stylesheet.
 *   3. THE BOUNDARY IS `--border-strong`, NOT `--border-default` (ADR-037 correction 4).
 *      `Input.jsx:15` uses the 1.34:1 border. On a form control the boundary is the only way to
 *      perceive the control, so WCAG 1.4.11's 3:1 applies to it: `--border-strong` is 3.45:1.
 *      A trustee who cannot see where the notes box starts cannot use the notes box.
 *
 * `data-print` LANDS ON THE OUTERMOST ELEMENT RENDERED — the `<label>` when there is one, the
 * `<input>` when there is not. `print.css` hides by attribute (`[data-print="hide"]`), so
 * putting it on the inner input while a label wrapper existed would hide the field and leave
 * its caption on the paper (§8.5 point 7).
 *
 * `role` goes to the `<input>`, because the input is the semantic control; the wrapper is
 * presentation.
 */
import type { InputHTMLAttributes } from "react";
import styles from "../../styles/ds.module.css";
import { classNames } from "./classNames";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  /**
   * When given, the input is wrapped in its own `<label>` and this is its visible text. When
   * OMITTED, a bare `<input>` is rendered so an external `<Label htmlFor>` can own the
   * association — see this file's header.
   */
  label?: string;
  /** §8.5 point 7 — see `Button.tsx` for the print vocabulary. */
  "data-print"?: string;
}

export function Input({
  label,
  className,
  "data-print": dataPrint,
  ...rest
}: InputProps) {
  const labelled = label !== undefined && label !== "";

  const field = (
    <input
      // Before the spread: a DEFAULT the caller can override, as the supplied contract intends.
      type="text"
      className={classNames(styles.inputField, className)}
      // Only when this input IS the outermost element. See the header.
      data-print={labelled ? undefined : dataPrint}
      {...rest}
    />
  );

  if (!labelled) return field;

  return (
    <label className={styles.inputLabel} data-print={dataPrint}>
      <span>
        {label}
        {/*
          The supplied component's required marker (`Input.jsx:7`). It is a glyph rather than a
          colour, so it does not fall foul of "required fields are indicated, not by colour
          alone" — and the programmatic signal a screen reader actually announces is the
          `required` attribute on the input itself, which arrives through the spread above.
        */}
        {rest.required === true ? "*" : null}
      </span>
      {field}
    </label>
  );
}
