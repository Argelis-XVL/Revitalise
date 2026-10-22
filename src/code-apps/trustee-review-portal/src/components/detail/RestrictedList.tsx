/**
 * The restricted rows — WI-0067, FR-078, ADR-032.
 *
 * F1-F3 are secured columns the trustee cannot read and this app never requests; the cell carries
 * no value at all, only its catalogue key. Each row shows the question and a "Restricted" pill;
 * the full `RESTRICTED_VALUE_TEXT` is shown ONCE below the list. Every `<dd>` still contains that
 * full text, visually hidden, so a screen reader reads each restricted row exactly as the first
 * app's `<dl>` does — the pill is `aria-hidden` and the note below is `aria-hidden` too, so the
 * sentence is announced once per row and not once more at the end.
 */
import type { ResolvedRow } from "../../domain/applicationDetailDisplay";
import { RESTRICTED_VALUE_TEXT } from "../../domain/fieldCatalogue";
import styles from "../../styles/detail.module.css";

/** Design copy for the pill (README line 112). The words a screen reader hears are the constant. */
export const RESTRICTED_PILL_TEXT = "Restricted";

export function RestrictedList({ rows }: { rows: readonly ResolvedRow[] }) {
  return (
    <>
      <dl className={styles.restrictedList} data-print="restricted">
        {rows.map(({ row }) => (
          <div key={row.id} className={styles.restrictedRow} data-print="tile">
            <dt data-field={row.id}>{row.label}</dt>
            <dd>
              <span className={`${styles.pill} ${styles.restrictedPill}`} aria-hidden="true">
                {RESTRICTED_PILL_TEXT}
              </span>
              <span className={styles.srOnly}>{RESTRICTED_VALUE_TEXT}</span>
            </dd>
          </div>
        ))}
      </dl>
      <p className={styles.restrictedNote} aria-hidden="true">
        {RESTRICTED_VALUE_TEXT}
      </p>
    </>
  );
}
