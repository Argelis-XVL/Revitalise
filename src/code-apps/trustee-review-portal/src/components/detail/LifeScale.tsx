/**
 * The C2 life-satisfaction scale — WI-0065, WI-0074 clause 2.
 *
 * Eleven points, 0 to 10, the answered one filled. The value is carried in TEXT as well as
 * colour (WCAG 1.4.1): the points are one `role="img"` whose `aria-label` reads
 * "Answer: N out of 10", with N the layout cell's own `optionLabel(LIFE_SATISFACTION_LABELS, …)`
 * text; and a print-only copy of the same sentence prints on paper, where colour may not survive
 * (WI-0073). A null answer shows the cell's "Not recorded" instead of the points. An answer
 * outside 0-10 (the label map renders it "Unknown (n)") shows that text, never a wrong point.
 *
 * `<div>`s inside the `<dd>` rather than a second `<dl>` group: a `<dl>` group holds only
 * `<dt>`/`<dd>`, so the question is the `<dt>` and everything else is inside its `<dd>`.
 */
import type { ApplicationDetail } from "../../dataverse/types";
import type { ResolvedRow } from "../../domain/applicationDetailDisplay";
import { SCALE_POINTS, numberOf, scaleAnswerText } from "../../domain/applicationDetailDisplay";
import styles from "../../styles/detail.module.css";
import { plainText } from "./cellText";

export function LifeScale({ rows, detail }: { rows: readonly ResolvedRow[]; detail: ApplicationDetail }) {
  return (
    <dl className={styles.block} data-print="scale">
      {rows.map(({ row, cell }) => {
        const value = numberOf(row.id, detail);
        const label = plainText(cell);
        const onScale = value !== null && SCALE_POINTS.includes(value);
        return (
          <div key={row.id} className={styles.scale}>
            <dt data-field={row.id} className={styles.scaleQuestion}>
              {row.label}
            </dt>
            <dd>
              {onScale ? (
                <>
                  <div
                    role="img"
                    aria-label={scaleAnswerText(label)}
                    className={styles.scaleDots}
                    data-print="scale-points"
                  >
                    {SCALE_POINTS.map((point) => (
                      <span
                        key={point}
                        className={styles.scalePoint}
                        data-selected={point === value ? "true" : undefined}
                      >
                        {point}
                      </span>
                    ))}
                  </div>
                  <span className={styles.srOnly} aria-hidden="true" data-print="scale-value">
                    {scaleAnswerText(label)}
                  </span>
                </>
              ) : (
                <span className={styles.absentText}>{label}</span>
              )}
            </dd>
          </div>
        );
      })}
    </dl>
  );
}
