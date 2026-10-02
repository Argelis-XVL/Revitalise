/**
 * This app's semantic primitives, in the Design 2.0 card look — CARD APP ONLY (TAD
 * trustee-portal-design-2 Revision 2, §13.1; ADR-060 classes this file `presentation`).
 *
 * Design source: `Designsystem/Revitalise Design System (1)/ui_kits/trustee-review-portal/Shared.jsx`
 * (`Eyebrow`, `Panel`, `Definitions`, `StateMessage`, `StatTileRow`) and `RoundOverview.jsx`
 * (`Card`, `ProgressTiles`, `MoneyTiles`). Every visual value is in `styles/app.module.css`, which
 * carries the design file and line beside each one; nothing here carries a style that is not
 * computed at runtime.
 *
 * WHAT DOES NOT CHANGE, AND IS HELD BY THE FIRST APP'S `Panel.test.tsx` (contract, identical):
 *
 *   - `Panel` is a `<section aria-labelledby>` with ONE `<h2>` and `data-print="block"`;
 *   - `StateMessage` is `role="note"` by default (overridable to `alert` for a real failure),
 *     carries `data-print="state"`, and its two tones stay visually distinct (§8.5 point 1);
 *   - `Definitions` and every tile row are one `<dl>` of `<dt>`/`<dd>` pairs, each `<dd>` its
 *     `<dt>`'s next sibling, never the mockup's `<strong>`/`<span>`;
 *   - an absence ("Not recorded", "Not available") is typeset differently from a figure, with the
 *     words unchanged.
 *
 * WHAT IS NEW. `Panel` takes an optional EYEBROW (ADR-062 A, design copy, `aria-hidden`) and an
 * optional computed SENTENCE (ADR-062 B, §13.7). While a sentence is shown it is the visible
 * heading and is `aria-hidden`; the `<h2>` keeps the existing plain heading as its accessible
 * name, visually hidden. So a screen reader hears exactly today's heading, and a contract test
 * that finds the heading by name (`name: "Round progress"`) still finds it.
 */
import { useId } from "react";
import type { ReactNode } from "react";
import { NOT_AVAILABLE, NOT_RECORDED } from "../domain/format";
import { StatTile } from "./ds";
import styles from "../styles/app.module.css";

/** An eyebrow's colour: `brand` pink (at the ADR-037 corrected shade), the purple, or ink. */
export type EyebrowTone = "brand" | "purple" | "ink";

/**
 * The small uppercase label above a heading — `Shared.jsx` `Eyebrow` (lines 14-16). Decorative:
 * `aria-hidden`, and hidden on paper.
 */
export function Eyebrow({ children, tone = "brand" }: { children: ReactNode; tone?: EyebrowTone }) {
  return (
    <p className={styles.eyebrow} data-tone={tone} aria-hidden="true" data-print="hide">
      <span className={styles.eyebrowDot} />
      {children}
    </p>
  );
}

/**
 * The visible heading text of a card: the computed sentence when there is one, otherwise the
 * plain heading. The accessible name is ALWAYS the plain heading (ADR-062 decision 2).
 */
export function HeadingText({ heading, sentence }: { heading: string; sentence?: string | null }) {
  if (sentence === undefined || sentence === null) return <>{heading}</>;
  return (
    <>
      <span className={styles.srOnly}>{heading}</span>
      <span aria-hidden="true">{sentence}</span>
    </>
  );
}

/**
 * A titled region of a case or of the round overview — `Shared.jsx` `Panel` / `RoundOverview.jsx`
 * `Card`: a white card with the panel shadow, 16px radius, 32px padding, 20px between its
 * blocks, and the hover lift of `.rv-card.rv-lift`.
 */
export function Panel({
  heading,
  eyebrow,
  eyebrowTone,
  sentence,
  children,
}: {
  heading: string;
  eyebrow?: string;
  eyebrowTone?: EyebrowTone;
  sentence?: string | null;
  children: ReactNode;
}) {
  const headingId = useId();
  return (
    <section className={styles.panel} aria-labelledby={headingId} data-print="block">
      <div className={styles.panelHeader}>
        {eyebrow === undefined ? null : <Eyebrow tone={eyebrowTone}>{eyebrow}</Eyebrow>}
        <h2 id={headingId} className={styles.panelHeading}>
          <HeadingText heading={heading} sentence={sentence} />
        </h2>
      </div>
      <div className={styles.panelBody}>{children}</div>
    </section>
  );
}

/** The two designed tones of a state message. See `tone` below. */
export type StateMessageTone = "muted" | "quiet";

/**
 * A first-class informational state: withheld narrative, no review row, not assigned —
 * `Shared.jsx` `StateMessage` (lines 98-105): a dashed lavender card with a soft gradient wash.
 *
 * `role="note"` by default, never an alert: these are the designed state of the screen. The
 * one call site that is a genuine failure passes `role="alert"`.
 *
 * `tone` keeps §8.5 point 1: `withheld` (`muted`) takes the design's dashed lavender card;
 * `released-empty` (`quiet`) takes a solid, unwashed card, so the two states never read as one
 * grey box. The design draws only the first; the second is this app's existing distinction.
 */
export function StateMessage({
  heading,
  explanation,
  tone = "muted",
  role = "note",
}: {
  heading: string;
  explanation: string;
  tone?: StateMessageTone;
  role?: string;
}) {
  return (
    <div
      role={role}
      className={tone === "muted" ? styles.stateMessage : styles.stateMessageQuiet}
      data-print="state"
    >
      <p className={styles.stateHeading}>{heading}</p>
      <p className={styles.stateExplanation}>{explanation}</p>
    </div>
  );
}

/**
 * `domain/format.ts`'s absence vocabulary, imported rather than retyped: the only two strings
 * this app puts in a value position to mean "there is no figure here".
 */
const ABSENCE_WORDS: readonly string[] = [NOT_RECORDED, NOT_AVAILABLE];

function isAbsent(value: string): boolean {
  return ABSENCE_WORDS.includes(value);
}

/**
 * A definition list of label/value pairs as FACT TILES — `Shared.jsx` `Definitions` (lines
 * 83-97): a grid of rounded grey tiles, each a `<div>` wrapping one `<dt>` + `<dd>` (valid HTML,
 * and the programmatic label/value association FR-078 depends on). An absent value takes the
 * dashed, transparent tile with italic body text.
 */
export function Definitions({ items }: { items: { label: string; value: string }[] }) {
  return (
    <dl className={styles.definitions}>
      {items.map((item) => (
        <div key={item.label} className={styles.definitionTile} data-absent={isAbsent(item.value) ? "true" : undefined} data-print="tile">
          <dt>{item.label}</dt>
          <dd className={isAbsent(item.value) ? styles.definitionValueAbsent : styles.definitionValue}>
            {item.value}
          </dd>
        </div>
      ))}
    </dl>
  );
}

/**
 * A KPI row over `ds/StatTile` — kept for any caller that still wants the design system's plain
 * stat tile. The round overview uses `ProgressTiles` and `MoneyTiles` below, which are the
 * design's own shapes for those two cards.
 */
export function StatTileRow({ items }: { items: { label: string; value: string }[] }) {
  return (
    <dl className={styles.statTiles}>
      {items.map((item) => (
        <StatTile key={item.label} label={item.label} value={item.value} absent={isAbsent(item.value)} />
      ))}
    </dl>
  );
}

/**
 * The round overview's progress tiles — `RoundOverview.jsx` `ProgressTiles` (lines 51-63): a
 * tinted tile per figure (pink-50, lavender-100, the teal tint, in turn), a 28x6px bar in the
 * matching colour, the value in Playfair 40px and the label beneath it. Still one `<dl>`: the
 * `<dt>` (label) precedes its `<dd>` (value) in the DOM, and the stylesheet draws the value first,
 * as the design does, so a screen reader reads "label, value" like every other pair.
 */
export function ProgressTiles({ items }: { items: { label: string; value: string }[] }) {
  return (
    <dl className={styles.progressTiles}>
      {items.map((item, index) => (
        <div
          key={item.label}
          className={styles.progressTile}
          data-tone={String(index % 3)}
          data-absent={isAbsent(item.value) ? "true" : undefined}
          data-print="tile"
        >
          <dt className={styles.progressTileLabel}>{item.label}</dt>
          <dd className={isAbsent(item.value) ? styles.progressTileValueAbsent : styles.progressTileValue}>
            {item.value}
          </dd>
        </div>
      ))}
    </dl>
  );
}

/**
 * The financial position's money tiles — `RoundOverview.jsx` `MoneyTiles` (lines 186-200): grey
 * tiles, the value in Playfair 26px, an absent value as a dashed transparent tile in italic body
 * text.
 */
export function MoneyTiles({ items }: { items: { label: string; value: string }[] }) {
  return (
    <dl className={styles.moneyTiles}>
      {items.map((item) => (
        <div
          key={item.label}
          className={styles.moneyTile}
          data-absent={isAbsent(item.value) ? "true" : undefined}
          data-print="tile"
        >
          <dt className={styles.moneyTileLabel}>{item.label}</dt>
          <dd className={isAbsent(item.value) ? styles.moneyTileValueAbsent : styles.moneyTileValue}>
            {item.value}
          </dd>
        </div>
      ))}
    </dl>
  );
}

/**
 * Authored multi-line text, line breaks preserved. `.preserveLines` keeps its 75ch measure
 * (WCAG 1.4.8).
 */
export function MultilineText({ text }: { text: string }) {
  return <p className={styles.preserveLines}>{text}</p>;
}
