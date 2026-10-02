/**
 * The card-layout panel — WI-0068 / WI-0069, TAD trustee-portal-design-2 ADR-055..058.
 *
 * Same MEANING as `components/Panel.tsx`'s `Panel`, which this app shares byte-for-byte with the
 * first one: a `<section aria-labelledby>` landmark with exactly one `<h2>`, and
 * `data-print="block"` so `print.css` prints it as a rule rather than a box. What differs is the
 * look (a white card, 16px radius, the panel shadow, 20px internal gap) and one decorative line
 * above the heading, the eyebrow. `Panel` itself cannot take either without changing a file the
 * parity gate holds equal, so the card is its own component here, on the gate's allow-list.
 *
 * The eyebrow is `aria-hidden` and print-hidden: it is design copy (reviewer R2, "Approve all"),
 * not a heading, and a screen reader hears only the Pack's own `<h2>`.
 */
import { useId } from "react";
import type { ReactNode } from "react";
import type { Eyebrow } from "../../domain/applicationDetailDisplay";
import styles from "../../styles/detail.module.css";

export function EyebrowLine({ eyebrow }: { eyebrow: Eyebrow }) {
  return (
    <p className={styles.eyebrow} data-tone={eyebrow.tone} aria-hidden="true" data-print="hide">
      <span className={styles.eyebrowDot} />
      {eyebrow.text}
    </p>
  );
}

export function DetailPanel({
  heading,
  eyebrow,
  spacious = false,
  children,
}: {
  heading: string;
  eyebrow?: Eyebrow;
  /** Current Circumstances: blocks 32px apart instead of 20px (WI-0064 clause 0, WI-0008). */
  spacious?: boolean;
  children: ReactNode;
}) {
  const headingId = useId();
  return (
    <section className={styles.card} aria-labelledby={headingId} data-print="block">
      <div className={styles.cardHeader}>
        {eyebrow === undefined ? null : <EyebrowLine eyebrow={eyebrow} />}
        <h2 id={headingId} className={styles.cardHeading}>
          {heading}
        </h2>
      </div>
      <div className={spacious ? `${styles.cardBody} ${styles.spacious}` : styles.cardBody}>
        {children}
      </div>
    </section>
  );
}

/**
 * A card around a panel that a SHARED component renders itself — the Verdict
 * (`VerdictSection` → `Panel`), which is under parity and cannot take a class or an eyebrow. The
 * frame supplies the card and the eyebrow; the shared `<section>`, its `<h2>` ("Your verdict")
 * and its behaviour are untouched (WI-0070 clause 0: "content and behaviour unchanged").
 */
export function PanelFrame({ eyebrow, children }: { eyebrow: Eyebrow; children: ReactNode }) {
  return (
    <div className={styles.frame} data-detail-frame="true" data-print="frame">
      <EyebrowLine eyebrow={eyebrow} />
      {children}
    </div>
  );
}
