/**
 * The computedOn stamp's card-app wording — ADR-066 decision 2 (reviewer R11, "Design wording"):
 * "Computed on {date} at {time}", the date then the time with its "UTC" suffix, both taken from
 * `formatDateTime`'s own output so the two apps can never disagree about WHEN. A null `computedOn`
 * reads "Computed on Not recorded", as the first app's line would.
 */
import { formatDateTime } from "../domain/format";

export function computedOnStamp(computedOn: string | null): string {
  const formatted = formatDateTime(computedOn);
  const comma = formatted.lastIndexOf(", ");
  if (comma < 0) return `Computed on ${formatted}`;
  return `Computed on ${formatted.slice(0, comma)} at ${formatted.slice(comma + 2)}`;
}
