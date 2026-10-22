/**
 * The status pill and the score chip — card app only (TAD trustee-portal-design-2 §13.3, WI-0094).
 * Design: `Shared.jsx` `StatusPill` (lines 70-73) and `ScoreChip` (lines 74-82).
 *
 * Both carry their value as TEXT: the pill's label is the status in words (`optionLabel`), and the
 * chip's number is the score, so colour is never the only carrier (WCAG 1.4.1). The chip's 56x6px
 * bar is `aria-hidden` decoration; a null score reads "Not scored" (`formatScore`), the first app's
 * wording.
 */
import { APPLICATION_STATUS_LABELS, optionLabel } from "../dataverse/schema";
import { formatScore } from "../domain/format";
import { statusToneOf } from "./statusTone";
import styles from "../styles/cards.module.css";

export function StatusPill({ status }: { status: number | null }) {
  return (
    <span className={styles.statusPill} data-tone={statusToneOf(status)}>
      {optionLabel(APPLICATION_STATUS_LABELS, status)}
    </span>
  );
}

const SCORE_MAX = 60;

export function ScoreChip({ score }: { score: number | null }) {
  if (score === null) return <span className={styles.scoreAbsent}>{formatScore(score)}</span>;
  const fraction = Math.min(Math.max(score / SCORE_MAX, 0), 1);
  return (
    <span className={styles.scoreChip}>
      <span className={styles.scoreTrack} aria-hidden="true">
        <span className={styles.scoreFill} style={{ width: `${String(fraction * 100)}%` }} />
      </span>
      <span className={styles.scoreValue}>{formatScore(score)}</span>
    </span>
  );
}
