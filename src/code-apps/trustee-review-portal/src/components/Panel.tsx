/**
 * This app's own five semantic primitives — RESTYLED IN REVISION 4, NOT REPLACED.
 *
 * TAD §2.1.4's last paragraph is the decision this file implements: `Panel`, `StateMessage`,
 * `Definitions`, `StatTileRow` and `MultilineText` "are not replaced, they are restyled",
 * because each of the five carries a property §8.5 holds and the supplied design system has
 * no equivalent for any of them. The design-system components under `components/ds` supply
 * the LOOK; these five keep the MEANING:
 *
 *   - `Panel` is the `<section aria-labelledby>` + `<h2>` landmark;
 *   - `StateMessage` is the `role="note"` withheld state (§8.5 point 1);
 *   - `Definitions` is the `<dl>`/`<dt>`/`<dd>` that makes a restricted row read as a value
 *     (§8.5 point 2);
 *   - `StatTileRow` is the `<dl>` around the design system's tiles, and the place a null
 *     figure stops looking like a measurement (§8.5 point 3).
 *
 * WHERE THE VISUAL RULES NOW LIVE. `styles/ds.module.css` holds the converted component
 * variants and `styles/app.module.css` holds this app's own layout — the split TAD §2.1.2
 * asks for, because the first is a conversion of an external artefact that will be re-diffed
 * against it and the second is ours. Nothing here carries an inline `style` attribute whose
 * value is not computed at runtime (`knowledge/technology/code-apps.md:527`): the one that
 * survives is `Definitions`' `display: "contents"`, which is a grid mechanism rather than a
 * colour, and it is the reason the `<dl>` can be a two-column grid without a wrapper element
 * breaking the term/definition association.
 */
import { useId } from "react";
import type { ReactNode } from "react";
import { NOT_AVAILABLE, NOT_RECORDED } from "../domain/format";
import { Notice, StatTile } from "./ds";
import styles from "../styles/app.module.css";

/**
 * A titled region of a case.
 *
 * Every panel is a real `<section>` with a real `<h2>`, so the detail screen has one
 * `<h1>` and a flat list of `<h2>`s beneath it — a hierarchy that survives the print
 * stylesheet and reads correctly to a screen reader (WCAG 1.3.1, 2.4.6). The
 * `aria-labelledby` pairing is what makes the section a landmark rather than a div.
 *
 * `data-print="block"` is unchanged and is what `print.css` keys on to print the panel as a
 * rule rather than a box (§8.5 point 7 — the print path never reads a class name, which is
 * precisely why restyling it is safe).
 */
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

/** The two designed tones of a state message. See `tone` below. */
export type StateMessageTone = "muted" | "quiet";

/**
 * A first-class informational state: withheld narrative, no review row, not assigned.
 *
 * Not an error and not an empty box. `role="note"` rather than `role="alert"` on
 * purpose: these are the designed state of the screen, and an alert would interrupt a
 * screen-reader user on every navigation to tell them something entirely expected. That
 * reasoning is unchanged by Revision 4 and is why `ds/Notice` is adopted as this
 * component's VISUAL TREATMENT and never as a replacement for it — the supplied `Notice`
 * is a plain `<div>` with no role at all, so the role is this component's to supply
 * (§8.5 point 1, point 6).
 *
 * ## `tone` — two states that are not the same fact, and must not become one grey box
 *
 * `domain/visibility.ts` returns three states and two of them reach this component:
 * **`withheld`** ("you are not permitted to see this") takes `muted`, a filled grey panel;
 * **`released-empty`** ("nothing has been scrubbed into this field yet") takes `quiet`, an
 * unfilled panel with a hairline. Rendering either as an undifferentiated box tells a
 * trustee something false about UK GDPR Art. 9 data — `visibility.ts:98-106` records why
 * `released-empty` is not the same fact as "nothing recorded", and
 * `CasePanels.test.tsx:166` pins the exact `released-empty` sentence while `:178-181`
 * asserts it does not contain the word "withheld".
 *
 * ## `role` — overridable, for exactly one call site
 *
 * The default is `note` and every caller in this app but one takes it. §8.5 point 6 needs
 * `role="alert"` for the applications list's error box, which is a genuine failure rather
 * than a designed state; an error a screen reader is never told about is a worse outcome
 * than an unstyled one. Hardcoding either value would be wrong in the other place.
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
    // NO app-layout class is passed. The box is entirely `ds/Notice`'s — fill, hairline,
    // radius, padding, and the two tones — and `app.module.css` no longer carries a
    // `.stateMessage` rule at all. That is deliberate rather than an omission: a class in
    // this app's module and a class in the design system's module sit at equal specificity
    // (0,1,0) in two separate CSS Modules, so any property both declared would be resolved
    // by whichever stylesheet the bundler emitted first. Declaring nothing here is the only
    // way to make the outcome independent of build order. `data-print="state"` is what
    // `print.css` keys on, and it is unchanged.
    <Notice tone={tone} title={heading} role={role} data-print="state">
      {explanation}
    </Notice>
  );
}

/**
 * A definition list of label/value pairs. Values are always non-empty strings.
 *
 * THE MARKUP IS THE REQUIREMENT AND THE SUPPLIED MOCKUP IS REFUSED HERE (§8.5 point 2).
 * `ui_kits/trustee-review-portal/ApplicationDetail.jsx:11-18` renders each field as
 * `<div><strong>label</strong><span>value</span></div>`, which is not a programmatic
 * label-value association at all (WCAG 1.3.1) — and it is exactly the property FR-078
 * depends on, because a restricted row from the field catalogue and a real value have to
 * read the same way to a screen reader (`CasePanels.tsx:159-163`). The mockup's VISUAL
 * treatment — the two-column measure and the label weight — is taken; its markup is not.
 *
 * `display: "contents"` is a computed grid mechanism, not a style choice: it lets the
 * wrapper `<div>` that `key`s each pair disappear from the grid so `<dt>` and `<dd>` land
 * in the two columns themselves. It is one of the app's two permitted inline styles.
 */
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

/**
 * `domain/format.ts`'s absence vocabulary, imported rather than retyped.
 *
 * These are the only two strings this app puts in a value position to mean "there is no
 * figure here": `formatAmount`, `formatCount`, `formatRate` and `formatPercentage` all
 * return `NOT_RECORDED` for a null, and `formatRegion` returns `NOT_AVAILABLE` when a row
 * could not be read. Importing the constants rather than matching a literal is what keeps
 * this in step with `format.ts` — rename either there and this follows, with no second
 * place to remember.
 */
const ABSENCE_WORDS: readonly string[] = [NOT_RECORDED, NOT_AVAILABLE];

/**
 * A KPI row — the Round 4 deck's headline-figure dashboard, re-implemented over
 * `ds/StatTile` in Revision 4 (TAD §2.1.4, §8.5 point 3).
 *
 * THREE THINGS ARE KEPT AND ONE IS NEW.
 *
 * Kept: the `{ label, value }[]` contract, so no call site changes; the `<dl>` element,
 * because a `<dl>` of `<dt>`/`<dd>` pairs is a PROGRAMMATIC term/definition association and
 * `ds/StatTile` renders exactly that pair inside a `<div>` (valid HTML5 — a `<dl>` permits
 * each group wrapped in a `<div>`); and the SAME accessible content as `Definitions`, so a
 * screen reader announces the same pairs either component renders. There is nothing to
 * "fall back" to alongside a stat tile the way there is for a chart (ADR-029): the number
 * IS the content, not a picture of it.
 *
 * New: **an absence stops being typeset as a measurement.** `ds/StatTile` sets its value in
 * the display face at 32px, which would render the literal "Not recorded" as a 32px display
 * figure — reading as a value where an absence is meant. The `absent` state renders the same
 * words in body type and body colour instead. This matters here and only here because the
 * two screens have deliberately OPPOSITE null behaviours: `RoundFinancePanel` renders all
 * eight rows even when a figure is null, because a person has left a real field empty and
 * a trustee needs to see that; the statistics blocks render nothing at all, because a null
 * metric was never computed and a heading over "Not recorded" would invent a gap
 * (`RoundStatistics.tsx:10-13`, `RoundFinancePanel.tsx:8-22`). The words are unchanged in
 * both cases; only their typographic claim to being a measurement is withdrawn.
 */
export function StatTileRow({ items }: { items: { label: string; value: string }[] }) {
  return (
    <dl className={styles.statTiles}>
      {items.map((item) => (
        <StatTile
          key={item.label}
          label={item.label}
          value={item.value}
          absent={ABSENCE_WORDS.includes(item.value)}
        />
      ))}
    </dl>
  );
}

/**
 * Authored multi-line text, line breaks preserved.
 *
 * `.preserveLines` keeps its 75ch measure: the page shell is fluid (NFR-026) but prose does
 * not follow it, because WCAG 1.4.8 asks for a line length of no more than about 80
 * characters. That is unchanged by the restyle.
 */
export function MultilineText({ text }: { text: string }) {
  return <p className={styles.preserveLines}>{text}</p>;
}
