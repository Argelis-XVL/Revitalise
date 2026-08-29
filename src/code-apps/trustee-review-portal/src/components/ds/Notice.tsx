/**
 * Notice — converted from
 * `Designsystem/Revitalise Design System/components/feedback/Notice.jsx` and its prop contract
 * `feedback/Notice.d.ts` (A-R42, ADR-034).
 *
 * THIS COMPONENT SETS NO `role`, AND THAT IS THE MOST IMPORTANT LINE IN THE FILE
 * (§8.5 point 6). The supplied `Notice.jsx:11-15` is a plain `<div>` with no role at all. This
 * app needs THREE different answers from the same visual treatment:
 *
 *   - the applications list's error state passes `role="alert"` — an error a screen reader is
 *     never told about is a worse outcome than an unstyled one;
 *   - the two distinct empty states pass `role="note"`;
 *   - the withheld / released-empty redaction states pass `role="note"` too, because
 *     `Panel.tsx:35-37` records that `role="alert"` there would interrupt a screen-reader
 *     trustee on EVERY navigation to tell them something entirely expected.
 *
 * So the role is supplied by the call site and forwarded here. Hardcoding either value would be
 * wrong in the other place.
 *
 * TONES. `muted` and `info` are the design system's, minus its `warning`:
 *
 *   - `warning` IS NOT IMPLEMENTED (ADR-037 correction 5). Its title `#c47a00` on the `#fdf5e6`
 *     the design system pairs it with measures 3.16:1 and fails the 4.5:1 normal-text floor,
 *     and this app has no warning state to put it in — the designed states are neutral notes
 *     and exactly one error. `ds-tokens.css` declares neither `--warning` nor `--success`, so
 *     the tone cannot be reintroduced by adding a class alone.
 *   - `quiet` IS NEW, and it is not decoration (§8.5 point 1). The three-state redaction
 *     rendering needs two VISUALLY DISTINCT treatments for two states that are not the same
 *     fact: `withheld` (not permitted to see it) takes `muted`, and `released-empty` (nothing
 *     was recorded) takes `quiet`. Collapsing them into one grey box asserts something false
 *     about Art. 9 data — which is why `CasePanels.test.tsx:166` pins the exact
 *     `released-empty` sentence and `:178-181` asserts it does not contain the word "withheld".
 *
 * `title` IS HEADING TEXT, NOT THE DOM `title` ATTRIBUTE. The supplied contract uses that name
 * for the notice's visible heading, and `React.HTMLAttributes` uses it for the tooltip
 * attribute. The DOM one is deliberately `Omit`ted so the collision is a stated decision rather
 * than a silent shadowing — a tooltip is not an accessible name and nothing here should imply
 * it is.
 */
import type { HTMLAttributes } from "react";
import styles from "../../styles/ds.module.css";
import { classNames } from "./classNames";

export type NoticeTone = "muted" | "info" | "quiet";

/** `string | undefined` for the reason given in `Button.tsx`'s own variant map. */
const TONE_CLASS: Record<NoticeTone, string | undefined> = {
  muted: styles.noticeMuted,
  info: styles.noticeInfo,
  quiet: styles.noticeQuiet,
};

export interface NoticeProps extends Omit<HTMLAttributes<HTMLDivElement>, "title"> {
  tone?: NoticeTone;
  /** The notice's visible heading. Rendered as text, never as a `title` attribute. */
  title?: string;
  /** §8.5 point 7 — see `Button.tsx` for the print vocabulary. */
  "data-print"?: string;
}

export function Notice({
  tone = "muted",
  title,
  className,
  children,
  ...rest
}: NoticeProps) {
  return (
    // `role` arrives through `rest` and lands here, on the outermost element — which is what
    // makes `role="alert"` announce the whole notice rather than only its body.
    <div className={classNames(styles.notice, TONE_CLASS[tone], className)} {...rest}>
      {title === undefined || title === "" ? null : (
        <p className={styles.noticeTitle}>{title}</p>
      )}
      <div className={styles.noticeBody}>{children}</div>
    </div>
  );
}
