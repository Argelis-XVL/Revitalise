/**
 * Answer cards for the redacted free-text rows — WI-0063, FR-035, FR-079.
 *
 * A new LOOK for the three states `redactedTextState()` (`domain/visibility.ts`, under parity)
 * returns, and nothing else: this component never reads a column, it reads the state the layout
 * cell already carries. `released` shows the text through `MultilineText` (75ch). The two other
 * states are `role="note"`, never alerts, and keep `data-print="state"` so paper shows a withheld
 * answer as prominently as the screen does.
 *
 * Withheld shows only the FIRST SENTENCE of the explanation (reviewer R4, "First sentence per
 * card"), through `WITHHELD_EXPLANATION_FIRST_SENTENCE`, from which `WITHHELD_EXPLANATION` is
 * composed (ADR-059). Released-empty keeps its full explanation.
 */
import type { ResolvedRow } from "../../domain/applicationDetailDisplay";
import { WITHHELD_EXPLANATION_FIRST_SENTENCE } from "../../domain/visibility";
import styles from "../../styles/detail.module.css";
import { MultilineText } from "../Panel";
import { plainText } from "./cellText";

function AnswerBody({ resolved }: { resolved: ResolvedRow }) {
  const { cell } = resolved;
  if (cell.kind !== "redacted") {
    // Unreachable: `displayOf()` sends only redacted cells here. Rendered as plain text rather
    // than dropped, so a routing mistake is visible.
    return <MultilineText text={plainText(cell)} />;
  }
  const state = cell.state;
  if (state.kind === "released") {
    return (
      <div className={styles.answerText}>
        <MultilineText text={state.text} />
      </div>
    );
  }
  const withheld = state.kind === "withheld";
  return (
    <div
      role="note"
      className={styles.answerNote}
      data-tone={withheld ? "withheld" : "quiet"}
      data-print="state"
    >
      <span className={`${styles.pill} ${styles.answerPill}`}>
        <span className={styles.pillDot} aria-hidden="true" />
        {state.heading}
      </span>
      <p className={styles.answerExplanation}>
        {withheld ? WITHHELD_EXPLANATION_FIRST_SENTENCE : state.explanation}
      </p>
    </div>
  );
}

export function AnswerCards({ rows }: { rows: readonly ResolvedRow[] }) {
  return (
    <dl className={styles.answers} data-print="answers">
      {rows.map((resolved) => {
        const { row, cell } = resolved;
        const state = cell.kind === "redacted" ? cell.state.kind : "released";
        return (
          <div key={row.id} className={styles.answerCard} data-state={state} data-print="answer">
            <dt data-field={row.id} className={styles.answerQuestion}>
              {row.label}
            </dt>
            <dd>
              <AnswerBody resolved={resolved} />
            </dd>
          </div>
        );
      })}
    </dl>
  );
}
