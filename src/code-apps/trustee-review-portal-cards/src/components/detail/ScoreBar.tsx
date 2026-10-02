/**
 * The C1 score bar — WI-0064. "{n} / 60" in the display face, or the cell's own "Not recorded"
 * wording, and a 10px track filled to score/60. The track is decorative (`aria-hidden`): the
 * value is already text in the `<dd>`. Its width is the one inline style here, and it is computed
 * at runtime, which is the only kind this app permits (`knowledge/technology/code-apps.md`).
 */
import type { ApplicationDetail } from "../../dataverse/types";
import type { ResolvedRow } from "../../domain/applicationDetailDisplay";
import { SCORE_MAX, numberOf, scoreFraction } from "../../domain/applicationDetailDisplay";
import { NOT_RECORDED } from "../../domain/format";
import styles from "../../styles/detail.module.css";

export function ScoreBar({ rows, detail }: { rows: readonly ResolvedRow[]; detail: ApplicationDetail }) {
  return (
    <dl className={styles.block} data-print="scorebar">
      {rows.map(({ row }) => {
        const score = numberOf(row.id, detail);
        return (
          // One `<dl>` group: a `<dl>` group may hold only its `<dt>` and `<dd>`, so the track
          // lives inside the `<dd>` and is positioned against the group's own box.
          <div
            key={row.id}
            className={`${styles.scoreBar} ${styles.scoreBarLine}`}
            data-print="tile"
          >
            <dt data-field={row.id}>{row.label}</dt>
            <dd
              className={styles.scoreBarValue}
              data-absent={score === null ? "true" : undefined}
            >
              {score === null ? NOT_RECORDED : `${String(score)} / ${String(SCORE_MAX)}`}
              <span className={styles.track} aria-hidden="true" data-print="hide">
                <span
                  className={styles.trackFill}
                  style={{ width: `${String(scoreFraction(score) * 100)}%` }}
                />
              </span>
            </dd>
          </div>
        );
      })}
    </dl>
  );
}
