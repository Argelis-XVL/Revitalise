/**
 * A titled region of a case.
 *
 * Every panel is a real `<section>` with a real `<h2>`, so the detail screen has one
 * `<h1>` and a flat list of `<h2>`s beneath it — a hierarchy that survives the print
 * stylesheet and reads correctly to a screen reader (WCAG 1.3.1, 2.4.6). The
 * `aria-labelledby` pairing is what makes the section a landmark rather than a div.
 */
import { useId } from "react";
import type { ReactNode } from "react";
import styles from "../styles/app.module.css";

export function Panel({
  heading,
  children,
}: {
  heading: string;
  children: ReactNode;
}) {
  const headingId = useId();
  return (
    <section className={styles.panel} aria-labelledby={headingId} data-print="block">
      <h2 id={headingId} className={styles.panelHeading}>
        {heading}
      </h2>
      <div className={styles.panelBody}>{children}</div>
    </section>
  );
}

/**
 * A first-class informational state: withheld narrative, no review row, not assigned.
 *
 * Not an error and not an empty box. `role="note"` rather than `role="alert"` on
 * purpose: these are the designed state of the screen, and an alert would interrupt a
 * screen-reader user on every navigation to tell them something entirely expected.
 */
export function StateMessage({
  heading,
  explanation,
}: {
  heading: string;
  explanation: string;
}) {
  return (
    <div className={styles.stateMessage} role="note" data-print="state">
      <p className={styles.stateHeading}>{heading}</p>
      <p className={styles.stateExplanation}>{explanation}</p>
    </div>
  );
}

/** A definition list of label/value pairs. Values are always non-empty strings. */
export function Definitions({ items }: { items: { label: string; value: string }[] }) {
  return (
    <dl className={styles.definitions}>
      {items.map((item) => (
        <div key={item.label} style={{ display: "contents" }}>
          <dt>{item.label}</dt>
          <dd>{item.value}</dd>
        </div>
      ))}
    </dl>
  );
}

/** Authored multi-line text, line breaks preserved. */
export function MultilineText({ text }: { text: string }) {
  return <p className={styles.preserveLines}>{text}</p>;
}
