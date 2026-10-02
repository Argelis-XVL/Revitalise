/**
 * CARD APP (Design 2.0 Revision 2, TAD trustee-portal-design-2 §13.3, WI-0092):
 * `ApplicationsList.jsx` lines 11-37 — the fields in a white card under the eyebrow "Filter the
 * round" (ADR-062 A), in one wrapping row, controls 44px with a 12px radius and a grey-50 fill.
 * The labels, their `htmlFor` binding, the options, "Clear filters", the filter logic and the
 * strong control border (TAD §8.3) are unchanged.
 *
 * Filters for the applications list — WBS 6.2, FR-034 ("sortable and filterable"),
 * FR-038 (round scoping).
 *
 * Every control has a visible `<label>` bound by `htmlFor`, not placeholder text
 * (WCAG 3.3.2). Choices are DERIVED from the rows the trustee can already see, so the
 * filter never offers a round or a status that would return nothing.
 *
 * There is no region filter. EF-02 (`docs/plans/emily-review-feedback-2026-09-plan.md`)
 * removed it along with the region column: the location column is secured behind
 * `REV_TrusteeRestricted`, so trustees see no location at all and a filter over it would
 * have nothing to offer. This paragraph previously described a conditional region filter
 * that no longer exists below — corrected rather than left stale
 * (`stale-comment-contradicts-source`, `IMP-0330`'s class). (Deliberately not naming the
 * secured column here — `no-secured-columns-in-code-app` scans every authored file in this
 * app for the forbidden set, comments included, and does not distinguish a reference from a
 * mention.)
 *
 * ## Revision 4 — what changed here, and the one thing that deliberately did not
 *
 * TAD §2.1.4 and §2.2.2 item 1: `Button` and `Input` become the design system's
 * (`components/ds`); Fluent's **`Label` and `Select` STAY**. The design system has no
 * `Select` at all, and the supplied mockup's substitute
 * (`ui_kits/trustee-review-portal/ApplicationsList.jsx:11-20`) is a bare `<select>` with one
 * hardcoded option and no state — it is not a control, it is a picture of one.
 *
 * NO `label` PROP IS PASSED TO `ds/Input`, AND THAT IS LOAD-BEARING. Every control here
 * pairs an EXTERNAL `<Label htmlFor={id}>` with the input's own `id`, which is what makes
 * the visible label the accessible name (WCAG 1.3.1, 3.3.2). `ds/Input` wraps its input in
 * its own `<label>` when — and only when — a `label` prop is given (`ds/Input.tsx:56`), so
 * omitting it renders a bare `<input>` and the existing pairing keeps working. Passing both
 * would nest a second `<label>` inside the first, the browser would resolve the innermost,
 * and the authored visible label would silently stop being the accessible name.
 *
 * ## `styles.filterSelect` on the three `Select`s (IMP-0486)
 *
 * The reviewer saw these three render at Fluent's native size while `Score from`/`Score to`
 * carried `ds/Input`'s styling beside them. Fixed at the STYLE level only — Select stays
 * Fluent's, per this file's own decision above — by passing `select={{ className:
 * styles.filterSelect }}`, never a top-level `className`: `@fluentui/react-select`'s
 * `getPartitionedNativeProps` (read from the installed package) routes a top-level `className`
 * to the outer wrapper `<span>`, not the `<select>` element the border/height/background
 * actually need to land on. See `app.module.css`'s `.filterSelect` for the reasoning on what
 * is and is not overridden.
 *
 * ## Revision 8 (2026-08-31, wbs:6.9) — the same defect on the other axis
 *
 * IMP-0486 above equalised these controls' HEIGHT and box treatment. The reviewer then found
 * two of them still rendering at visibly different WIDTHS, which is a separate cause: a
 * flex item sized by its own content, so "Review round" grew to fit its longest option string
 * and "Status" did not. `app.module.css`'s `.filterField` now fixes the field's width, and
 * `styles.filterControl` — passed to every `ds/Input` here, and mirrored by `.filterSelect`'s
 * own `width: 100%` for the Fluent `Select`s — makes the control fill it.
 *
 * `className` on `ds/Input` lands on the `<input>` element itself (`ds/Input.tsx:60`), so
 * this needs no slot indirection the way `Select` does. Nothing about the label association
 * changes: still an external `<Label htmlFor>` and still no `label` prop, for the reason the
 * paragraph above gives.
 *
 * ## Card app, Design 2.0 Revision 3 — the two selects are NATIVE here
 *
 * The history above is the first app's. In this app the two selects are the kit's native
 * `<select>` (ApplicationsList.jsx:12, :25, :28 — the browser's own chevron, `0 14px` inline
 * padding): the card TAD's §13.1 keeps Fluent only for the Dialog, and the fidelity audit
 * (`individual-applications-select-control`) found Fluent's chevron and inset unrecorded. The
 * class still lands on the `<select>` itself (`className={styles.filterSelect}`), which is
 * what the contract test `ApplicationFilters.test.tsx` asserts, and the external `Label
 * htmlFor` pairing is unchanged. Each field is now its own wrap item (no `scoreRange`
 * wrapper), so at 320px "Score from" and "Score to" stack as the kit's do
 * (ApplicationsList.jsx:30-31).
 */
import { Label } from "@fluentui/react-components";
import { Button, Input } from "./ds";
import { useId } from "react";
import type { Filters } from "../domain/listView";
import { EMPTY_FILTERS } from "../domain/listView";
import styles from "../styles/app.module.css";
import { Eyebrow } from "./Panel";

function toNumberOrNull(value: string): number | null {
  const trimmed = value.trim();
  if (trimmed.length === 0) return null;
  const parsed = Number(trimmed);
  return Number.isFinite(parsed) ? parsed : null;
}

export function ApplicationFilters({
  filters,
  rounds,
  statuses,
  onChange,
}: {
  filters: Filters;
  rounds: readonly string[];
  statuses: readonly { value: number; label: string }[];
  onChange: (next: Filters) => void;
}) {
  const roundId = useId();
  const statusId = useId();
  const minId = useId();
  const maxId = useId();
  const textId = useId();

  return (
    <div className={styles.filterCard} data-print="hide">
      <Eyebrow tone="purple">Filter the round</Eyebrow>
      <div className={styles.toolbar}>
      <div className={styles.filterField}>
        <Label htmlFor={roundId}>Review round</Label>
        <select
          id={roundId}
          className={styles.filterSelect}
          value={filters.round ?? ""}
          onChange={(event) => {
            const value = event.target.value;
            onChange({ ...filters, round: value === "" ? null : value });
          }}
        >
          <option value="">All rounds available to you</option>
          {rounds.map((round) => (
            <option key={round} value={round}>
              {round}
            </option>
          ))}
        </select>
      </div>

      <div className={styles.filterField}>
        <Label htmlFor={statusId}>Status</Label>
        <select
          id={statusId}
          className={styles.filterSelect}
          value={filters.status === null ? "" : String(filters.status)}
          onChange={(event) => {
            const value = event.target.value;
            onChange({ ...filters, status: value === "" ? null : Number(value) });
          }}
        >
          <option value="">All statuses</option>
          {statuses.map((status) => (
            <option key={status.value} value={String(status.value)}>
              {status.label}
            </option>
          ))}
        </select>
      </div>

      <div className={`${styles.filterField} ${styles.filterFieldScore}`}>
        <Label htmlFor={minId}>Score from</Label>
        <Input
          id={minId}
          type="number"
          inputMode="numeric"
          className={styles.filterControl}
          value={filters.scoreMin === null ? "" : String(filters.scoreMin)}
          onChange={(event) => {
            onChange({ ...filters, scoreMin: toNumberOrNull(event.target.value) });
          }}
        />
      </div>
      <div className={`${styles.filterField} ${styles.filterFieldScore}`}>
        <Label htmlFor={maxId}>Score to</Label>
        <Input
          id={maxId}
          type="number"
          inputMode="numeric"
          className={styles.filterControl}
          value={filters.scoreMax === null ? "" : String(filters.scoreMax)}
          onChange={(event) => {
            onChange({ ...filters, scoreMax: toNumberOrNull(event.target.value) });
          }}
        />
      </div>

      <div className={`${styles.filterField} ${styles.filterFieldWide}`}>
        <Label htmlFor={textId}>Application reference contains</Label>
        <Input
          id={textId}
          className={styles.filterControl}
          value={filters.text}
          onChange={(event) => {
            onChange({ ...filters, text: event.target.value });
          }}
        />
      </div>

      {/*
        §2.2.2 item 2 names this control `secondary` explicitly. No `styles.tallTarget`: every
        `ds/Button` size carries `min-height: 44px` on its own base class (WCAG 2.5.5,
        asserted mechanically by `styles/ds-tokens.test.ts`), so the app class that used to
        supply it would now be restating a guarantee the component already makes.
      */}
      <Button
        variant="secondary"
        onClick={() => {
          onChange(EMPTY_FILTERS);
        }}
      >
        Clear filters
      </Button>
      </div>
    </div>
  );
}
