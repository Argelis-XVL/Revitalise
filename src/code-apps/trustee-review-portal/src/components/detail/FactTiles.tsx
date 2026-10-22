/**
 * Fact tiles — WI-0060 (the default display) and WI-0061 (A3's conditions as chips).
 *
 * One `<dl>` grid; each tile is a `<div>` wrapping one `<dt>` + `<dd>` pair, which is valid HTML
 * and keeps the term/definition association a screen reader relies on. `data-field` stays on the
 * `<dt>`. A value that is one of the app's absence words ("Not recorded", "Not set", …) renders in
 * the tile's absent state; the words themselves are unchanged.
 *
 * A3 is UK GDPR Art. 9 data. Its chips read exactly the two condition-profile columns its layout
 * row already reads, and nothing is logged, exported or requested beyond that (WI-0061 clause 2).
 */
import type { ApplicationDetail } from "../../dataverse/types";
import type { ResolvedRow } from "../../domain/applicationDetailDisplay";
import { chipRowsOf, isAbsentText } from "../../domain/applicationDetailDisplay";
import styles from "../../styles/detail.module.css";
import { MultilineText } from "../Panel";
import { plainText } from "./cellText";

function ConditionChips({ rowId, detail }: { rowId: string; detail: ApplicationDetail }) {
  const rows = chipRowsOf(rowId, detail);
  return (
    <div className={styles.conditionGroups}>
      {rows.map((chipRow) => (
        <div key={chipRow.owner ?? "only"}>
          {chipRow.owner === null ? null : (
            <span className={styles.conditionOwner}>{chipRow.owner}:</span>
          )}
          <ul className={styles.conditionChips}>
            {chipRow.labels.map((label, index) => (
              <li key={`${label}-${String(index)}`} className={styles.conditionChip}>
                {label}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

export function FactTiles({
  rows,
  detail,
}: {
  rows: readonly ResolvedRow[];
  detail: ApplicationDetail;
}) {
  return (
    <dl className={styles.tiles} data-print="tiles">
      {rows.map(({ row, cell, display }) => {
        const hasChips = display === "chips" && chipRowsOf(row.id, detail).length > 0;
        const text = plainText(cell);
        const absent = !hasChips && isAbsentText(text);
        return (
          <div
            key={row.id}
            className={styles.tile}
            data-absent={absent ? "true" : undefined}
            data-print="tile"
          >
            <dt data-field={row.id}>{row.label}</dt>
            <dd>
              {hasChips ? (
                <ConditionChips rowId={row.id} detail={detail} />
              ) : cell.kind === "long-text" ? (
                <MultilineText text={text} />
              ) : (
                text
              )}
            </dd>
          </div>
        );
      })}
    </dl>
  );
}
