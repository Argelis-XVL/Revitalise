/**
 * The applications summary list — WBS 6.2, FR-034, SDD US-012 AC-1, US-013 AC-1/AC-2.
 *
 * A native `<table>` with `<th scope="col">` and `aria-sort`, not a div grid. TAD §8
 * requires "full keyboard operability of the sortable/filterable list (FR-034)
 * including sort controls as real buttons", and a native table gives a screen-reader
 * user row/column announcement for free — ARIA only where native semantics fall short
 * (`code-apps.md` → Accessibility). Fluent supplies the buttons, inputs and tokens; the
 * table itself is HTML.
 *
 * Every sortable header is a real `<button>` inside the `<th>`. The `<th>` carries
 * `aria-sort`; the button carries the accessible name and the direction it will apply
 * next, so a keyboard user is told the outcome before committing to it.
 *
 * ## Revision 4 — the RULE AND THE TYPE change; the MARKUP does not (TAD §2.2.1, §2.2.2)
 *
 * Only two things in this file are different: the per-row **Record verdict** control is now
 * `ds/Button variant="primary"` (§2.2.2 item 2), and the table's rule, header type and row
 * padding take the design system's treatment — which is entirely in `app.module.css`, so
 * not a line of the markup below moved for it (§2.2.2 item 3).
 *
 * THREE THINGS THE SUPPLIED MOCKUP WOULD HAVE COST, HAD IT BEEN FOLLOWED. Its header row is
 * a plain `<th>` with no `scope`, no button and no sort at all
 * (`ui_kits/trustee-review-portal/ApplicationsList.jsx:44-48`) — it restyles a table that
 * does not sort. Its row navigation is `<a href="#" onClick={e => e.preventDefault()}>`
 * (`:26`, `:53`), and a fragment anchor that is really a button is a semantics regression as
 * well as a navigation risk in a Power Apps host. And it sets the per-row control to
 * `size="sm"` (`:58`), which at its own padding and type size computes below the 44x44
 * target this app guarantees — the converted `ds/Button` carries `min-height: 44px` on every
 * size for exactly that reason, so `styles.tallTarget` is no longer needed beside it and is
 * not re-applied.
 */
import { Button } from "./ds";
import { APPLICATION_STATUS_LABELS, optionLabel } from "../dataverse/schema";
import type { ApplicationSummary } from "../dataverse/types";
import { formatDateRange, formatRegion, formatScore, NOT_AVAILABLE } from "../domain/format";
import { ariaSortFor } from "../domain/listView";
import type { SortKey, SortState } from "../domain/listView";
import styles from "../styles/app.module.css";

interface Column {
  key: SortKey;
  label: string;
  numeric?: boolean;
}

const COLUMNS: Column[] = [
  { key: "reference", label: "Application" },
  { key: "score", label: "Circumstance score", numeric: true },
  { key: "region", label: "Region" },
  { key: "dates", label: "Preferred dates" },
  { key: "status", label: "Status" },
];

function SortHeader({
  column,
  sort,
  onSort,
}: {
  column: Column;
  sort: SortState;
  onSort: (key: SortKey) => void;
}) {
  const current = ariaSortFor(sort, column.key);
  const nextDirection =
    current === "ascending" ? "descending" : current === "descending" ? "ascending" : "ascending";
  const indicator = current === "ascending" ? "▲" : current === "descending" ? "▼" : "";
  return (
    <th scope="col" aria-sort={current} className={column.numeric === true ? styles.numeric : undefined}>
      <button
        type="button"
        className={styles.sortButton}
        onClick={() => {
          onSort(column.key);
        }}
      >
        <span>{column.label}</span>
        {/* The arrow is decorative: the sorted state is carried by aria-sort and by the
            button's own accessible name, never by the glyph alone (WCAG 1.4.1). */}
        <span className={styles.sortIndicator} aria-hidden="true">
          {indicator}
        </span>
        <span className={styles.srOnly}>
          {current === "none"
            ? `, not sorted. Activate to sort ${nextDirection}.`
            : `, sorted ${current}. Activate to sort ${nextDirection}.`}
        </span>
      </button>
    </th>
  );
}

export function ApplicationsTable({
  rows,
  sort,
  onSort,
  onOpen,
  onRecordVerdict,
  caption,
}: {
  rows: readonly ApplicationSummary[];
  sort: SortState;
  onSort: (key: SortKey) => void;
  onOpen: (application: ApplicationSummary) => void;
  onRecordVerdict: (application: ApplicationSummary) => void;
  caption: string;
}) {
  return (
    <div className={styles.tableScroll}>
      <table className={styles.table}>
        <caption>{caption}</caption>
        <thead>
          <tr>
            {COLUMNS.map((column) => (
              <SortHeader key={column.key} column={column} sort={sort} onSort={onSort} />
            ))}
            <th scope="col">
              <span className={styles.plainHeader}>Decision</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              <th scope="row">
                {/* The accessible name is set with aria-label rather than a visually
                    hidden span: the name-computation algorithm concatenates adjacent
                    text nodes WITHOUT inserting a space, so "Record verdict" plus a
                    hidden " for REV-…" announced as "Record verdictfor REV-…". It still
                    contains the visible label, which WCAG 2.5.3 requires. */}
                <button
                  type="button"
                  className={styles.rowLink}
                  aria-label={`${row.reference}, open the full case`}
                  onClick={() => {
                    onOpen(row);
                  }}
                >
                  {row.reference}
                </button>
              </th>
              <td className={styles.numeric}>{formatScore(row.circumstanceScore)}</td>
              <td>
                {/* Region comes from rev_applicant.rev_locationarea. When the applicant
                    row cannot be read it says "Not available" — as text, never a blank
                    cell — and is never back-filled from rev_breaklocation, which is the
                    BREAK's location and a different fact. */}
                {formatRegion(row.region) === NOT_AVAILABLE ? (
                  <span className={styles.notAvailable}>{NOT_AVAILABLE}</span>
                ) : (
                  formatRegion(row.region)
                )}
              </td>
              <td>{formatDateRange(row.preferredStart, row.preferredEnd)}</td>
              <td>{optionLabel(APPLICATION_STATUS_LABELS, row.status)}</td>
              <td>
                <div className={styles.rowActions} data-print="hide">
                  {/* US-013 AC-3: a trustee who works only from this screen must be able
                      to record a verdict without opening the case. */}
                  <Button
                    variant="primary"
                    aria-label={`Record verdict for ${row.reference}`}
                    onClick={() => {
                      onRecordVerdict(row);
                    }}
                  >
                    Record verdict
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
