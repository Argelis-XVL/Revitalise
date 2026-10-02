/**
 * The cost receipt — WI-0062. D5, D6, D7, then D8 Total Estimated Cost with the heavier rule,
 * then D9 and D10: Pack order, because the rows arrive in Pack order and D8 is simply the line
 * marked `costTotal` (ADR-057 decision 3). Every amount is the layout cell's own text, which the
 * layout builds with `formatAmount()`; nothing is re-formatted here.
 */
import type { ResolvedRow } from "../../domain/applicationDetailDisplay";
import { isAbsentText } from "../../domain/applicationDetailDisplay";
import styles from "../../styles/detail.module.css";
import { plainText } from "./cellText";

export function CostReceipt({ rows }: { rows: readonly ResolvedRow[] }) {
  return (
    <dl className={styles.receipt} data-print="receipt">
      {rows.map(({ row, cell, display }) => {
        const text = plainText(cell);
        const total = display === "costTotal";
        return (
          <div
            key={row.id}
            className={total ? `${styles.receiptLine} ${styles.receiptTotal}` : styles.receiptLine}
            data-total={total ? "true" : undefined}
          >
            <dt data-field={row.id}>{row.label}</dt>
            <dd data-absent={isAbsentText(text) ? "true" : undefined}>{text}</dd>
          </div>
        );
      })}
    </dl>
  );
}
