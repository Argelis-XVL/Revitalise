/**
 * Filters for the applications list — WBS 6.2, FR-034 ("sortable and filterable"),
 * FR-038 (round scoping).
 *
 * Every control has a visible `<label>` bound by `htmlFor`, not placeholder text
 * (WCAG 3.3.2). Choices are DERIVED from the rows the trustee can already see, so the
 * filter never offers a round or a status that would return nothing.
 *
 * The region filter is offered only for regions actually present on the rows the trustee
 * can see, so it never offers a choice that would return nothing — and it disappears
 * entirely when no region is readable at all, rather than shipping a control that cannot
 * work.
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
 */
import { Label, Select } from "@fluentui/react-components";
import { Button, Input } from "./ds";
import { useId } from "react";
import type { Filters } from "../domain/listView";
import { EMPTY_FILTERS } from "../domain/listView";
import styles from "../styles/app.module.css";

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
  regions,
  onChange,
}: {
  filters: Filters;
  rounds: readonly string[];
  statuses: readonly { value: number; label: string }[];
  regions: readonly { value: number; label: string }[];
  onChange: (next: Filters) => void;
}) {
  const roundId = useId();
  const statusId = useId();
  const regionId = useId();
  const minId = useId();
  const maxId = useId();
  const textId = useId();

  return (
    <div className={styles.toolbar} data-print="hide">
      <div className={styles.filterField}>
        <Label htmlFor={roundId}>Review round</Label>
        <Select
          id={roundId}
          select={{ className: styles.filterSelect }}
          value={filters.round ?? ""}
          onChange={(_event, data) => {
            onChange({ ...filters, round: data.value === "" ? null : data.value });
          }}
        >
          <option value="">All rounds available to you</option>
          {rounds.map((round) => (
            <option key={round} value={round}>
              {round}
            </option>
          ))}
        </Select>
      </div>

      <div className={styles.filterField}>
        <Label htmlFor={statusId}>Status</Label>
        <Select
          id={statusId}
          select={{ className: styles.filterSelect }}
          value={filters.status === null ? "" : String(filters.status)}
          onChange={(_event, data) => {
            onChange({ ...filters, status: data.value === "" ? null : Number(data.value) });
          }}
        >
          <option value="">All statuses</option>
          {statuses.map((status) => (
            <option key={status.value} value={String(status.value)}>
              {status.label}
            </option>
          ))}
        </Select>
      </div>

      {regions.length === 0 ? null : (
        <div className={styles.filterField}>
          <Label htmlFor={regionId}>Region</Label>
          <Select
            id={regionId}
            select={{ className: styles.filterSelect }}
            value={filters.region === null ? "" : String(filters.region)}
            onChange={(_event, data) => {
              onChange({ ...filters, region: data.value === "" ? null : Number(data.value) });
            }}
          >
            <option value="">All regions</option>
            {regions.map((region) => (
              <option key={region.value} value={String(region.value)}>
                {region.label}
              </option>
            ))}
          </Select>
        </div>
      )}

      <div className={styles.scoreRange}>
        <div className={styles.filterField}>
          <Label htmlFor={minId}>Score from</Label>
          <Input
            id={minId}
            type="number"
            inputMode="numeric"
            value={filters.scoreMin === null ? "" : String(filters.scoreMin)}
            onChange={(event) => {
              onChange({ ...filters, scoreMin: toNumberOrNull(event.target.value) });
            }}
          />
        </div>
        <div className={styles.filterField}>
          <Label htmlFor={maxId}>Score to</Label>
          <Input
            id={maxId}
            type="number"
            inputMode="numeric"
            value={filters.scoreMax === null ? "" : String(filters.scoreMax)}
            onChange={(event) => {
              onChange({ ...filters, scoreMax: toNumberOrNull(event.target.value) });
            }}
          />
        </div>
      </div>

      <div className={styles.filterField}>
        <Label htmlFor={textId}>Application reference contains</Label>
        <Input
          id={textId}
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
  );
}
