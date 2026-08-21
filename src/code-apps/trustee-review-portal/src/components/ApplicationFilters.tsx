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
 */
import { Button, Input, Label, Select } from "@fluentui/react-components";
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

      <Button
        className={styles.tallTarget}
        onClick={() => {
          onChange(EMPTY_FILTERS);
        }}
      >
        Clear filters
      </Button>
    </div>
  );
}
