/**
 * Card — converted from `Designsystem/Revitalise Design System/components/content/Card.jsx` and
 * its prop contract `content/Card.d.ts` (A-R42, ADR-034).
 *
 * TWO PROPERTIES A CONSUMER HAS TO KNOW ABOUT, BOTH INHERITED FROM THE SUPPLIED COMPONENT
 * RATHER THAN INVENTED HERE:
 *
 *   1. THE TITLE IS AN `<h3>`, AT A FIXED LEVEL. `Card.jsx:9` uses `<h3>` and the conversion
 *      keeps it, which means a card must sit under an `<h2>` for the document's heading
 *      hierarchy to stay logical (WCAG 1.3.1, 2.4.6). In this app that is automatic: `Panel`
 *      IS the `<section aria-labelledby>` + `<h2>` landmark (`Panel.tsx:22-25`), so a card
 *      inside a panel is correctly nested. A card placed anywhere else must be checked.
 *   2. THE IMAGE IS DECORATIVE BY CONTRACT — `alt=""`, exactly as `Card.jsx:6` has it, so a
 *      screen reader skips it. That is correct for a decorative band and WRONG for an image
 *      carrying information, and this component has no way to express the second case. No
 *      `imageAlt` prop was added: widening the supplied shape to make a meaningful image
 *      possible is a design decision about a component nothing renders yet, and inventing API
 *      ahead of a consumer is how a conversion drifts from its source (A-R42). If a later pass
 *      needs a content image, that is the moment to decide it.
 *
 * `border-default` at 1.34:1 is the card's boundary and that is deliberate — ADR-037
 * correction 4 restricts the weak border from FORM CONTROLS, where the boundary is the only way
 * to perceive the control. Here it is decorative and the content carries the meaning.
 *
 * `title` is heading text rather than the DOM `title` attribute, for the reason stated in
 * `Notice.tsx`.
 */
import type { HTMLAttributes, ReactNode } from "react";
import styles from "../../styles/ds.module.css";
import { classNames } from "./classNames";

export interface CardProps extends Omit<HTMLAttributes<HTMLDivElement>, "title"> {
  /** Decorative image URL. Rendered with an empty `alt` — see this file's header. */
  image?: string;
  /** The card's visible heading, rendered as an `<h3>`. Never a `title` attribute. */
  title?: string;
  /** Actions or metadata below the body. */
  footer?: ReactNode;
  /** §8.5 point 7 — see `Button.tsx` for the print vocabulary. */
  "data-print"?: string;
}

export function Card({
  image,
  title,
  footer,
  className,
  children,
  ...rest
}: CardProps) {
  return (
    <div className={classNames(styles.card, className)} {...rest}>
      {image === undefined || image === "" ? null : (
        <img src={image} alt="" className={styles.cardImage} />
      )}
      <div className={styles.cardBody}>
        {title === undefined || title === "" ? null : (
          <h3 className={styles.cardTitle}>{title}</h3>
        )}
        <div className={styles.cardText}>{children}</div>
        {footer === undefined || footer === null ? null : (
          <div className={styles.cardFooter}>{footer}</div>
        )}
      </div>
    </div>
  );
}
