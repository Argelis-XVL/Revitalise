/**
 * Button — converted from `Designsystem/Revitalise Design System/components/core/Button.jsx`
 * and its prop contract `core/Button.d.ts` (A-R42, ADR-034).
 *
 * THREE THINGS THE CONVERSION CHANGES, EACH FOR A STATED REASON:
 *
 *   1. `type="button"` IS THE DEFAULT. The supplied `Button.jsx:26` sets no `type`, and a
 *      `<button>` with no type defaults to `submit`. `src/components/VerdictForm.tsx` renders a
 *      real form, so a supplied-as-is button inside it would submit the form on every click.
 *      The caller can still override it — `type` is spread AFTER this default, deliberately, so
 *      a genuine submit button remains expressible.
 *   2. THE INLINE `style` OBJECT IS GONE. `Button.jsx:6-24` builds one; the rules now live in
 *      `styles/ds.module.css`. An inline `style` attribute outranks every plain rule in
 *      `print.css` (only `print.css:22` is `!important`), so a component carrying its own
 *      background prints it — and `print.test.ts` reads the stylesheet as text and cannot see
 *      that. §2.1.1 point 4.
 *   3. EVERY SIZE CARRIES A 44px MINIMUM TARGET, `sm` INCLUDED (§2.2.2, WCAG 2.5.5). At
 *      `--text-sm` 15px with the supplied '10px 20px' padding the computed height lands below
 *      the 44x44 this app already guarantees via `styles.tallTarget` (`app.module.css:171`).
 *      The design system's visual intent for a small button — its padding and its type size —
 *      is preserved; its accidental target size is not inherited.
 *
 * PROPS ARE THE SUPPLIED SHAPE INTERSECTED WITH THE DOM CONTRACT (§2.1.3). `Button.d.ts`
 * declares six props and the app needs more than that in shipped code today: `type`,
 * `className` (the 44px target and the sort control), `aria-*` (the sort control's accessible
 * name and the Refresh figures button's stable one), and `data-print` (the verdict action bars
 * are hidden on paper).
 */
import type { ButtonHTMLAttributes, ReactNode } from "react";
import styles from "../../styles/ds.module.css";
import { classNames } from "./classNames";

export type ButtonVariant = "primary" | "secondary" | "ghost";
export type ButtonSize = "sm" | "md" | "lg";

/**
 * `string | undefined`, not `string`, and NOT the `Record<Variant, string>` §2.1.3 names. Vite
 * types a CSS Module as an index signature and `tsconfig.json` sets `noUncheckedIndexedAccess`,
 * so every `styles.x` here is `string | undefined` and the stricter annotation does not compile.
 * The map is still exhaustive over the union, which is the property that mattered: the supplied
 * `Button.jsx:26`'s `styles[variant]` lookup is what does not typecheck as written.
 */
const VARIANT_CLASS: Record<ButtonVariant, string | undefined> = {
  primary: styles.buttonPrimary,
  secondary: styles.buttonSecondary,
  ghost: styles.buttonGhost,
};

const SIZE_CLASS: Record<ButtonSize, string | undefined> = {
  sm: styles.buttonSm,
  md: styles.buttonMd,
  lg: styles.buttonLg,
};

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual style. Supplied contract: `core/Button.d.ts`. */
  variant?: ButtonVariant;
  size?: ButtonSize;
  /** Leading glyph or icon element. Never the only carrier of meaning (WCAG 1.4.1). */
  icon?: ReactNode;
  /**
   * The print vocabulary — `hide | page | block | state | brand | stamp | chart` (§8.5 point 7).
   * `print.css` targets this attribute and NEVER a class name, because CSS Module class names
   * are hashed at build time (`print.css:15-16`). Declared explicitly so the contract is
   * visible in the type rather than relying on TypeScript's blanket permission for hyphenated
   * JSX attributes.
   */
  "data-print"?: string;
}

export function Button({
  variant = "primary",
  size = "md",
  icon,
  className,
  children,
  ...rest
}: ButtonProps) {
  return (
    <button
      // Before the spread on purpose: this is a DEFAULT, and `rest.type` overrides it.
      type="button"
      className={classNames(
        styles.button,
        VARIANT_CLASS[variant],
        SIZE_CLASS[size],
        className,
      )}
      {...rest}
    >
      {icon}
      {children}
    </button>
  );
}
