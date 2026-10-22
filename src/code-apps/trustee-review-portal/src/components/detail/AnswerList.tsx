/**
 * The C3-C12 answer list — WI-0066. The question, then the answer in a pill, from the layout
 * cell's own text — which the layout builds through `wellbeing()` and the existing Likert and
 * agreement label maps. An unanswered question shows the same "Not recorded" in the same pill,
 * in italics. The group headings ("In the last 2 weeks…", "In the last year…") are the spec's
 * own, rendered by `DetailSectionPanel`, not by this list.
 */
import type { ResolvedRow } from "../../domain/applicationDetailDisplay";
import { isAbsentText } from "../../domain/applicationDetailDisplay";
import styles from "../../styles/detail.module.css";
import { plainText } from "./cellText";

export function AnswerList({ rows }: { rows: readonly ResolvedRow[] }) {
  return (
    <dl className={styles.answerList} data-print="answer-list">
      {rows.map(({ row, cell }) => {
        const text = plainText(cell);
        return (
          <div key={row.id} className={styles.answerRow}>
            <dt data-field={row.id}>{row.label}</dt>
            <dd>
              <span
                className={`${styles.pill} ${styles.likertPill}`}
                data-absent={isAbsentText(text) ? "true" : undefined}
              >
                {text}
              </span>
            </dd>
          </div>
        );
      })}
    </dl>
  );
}
