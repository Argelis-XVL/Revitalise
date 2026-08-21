/**
 * Wire-format helpers: reading values out of an untyped connector row, and writing
 * literals into an OData filter.
 *
 * These are deliberately boring and deliberately strict. Two of them carry the
 * security-relevant behaviour of the whole app:
 *
 *   - `asAffirmativeBoolean` decides whether a case is visible at all (TAD §5.5).
 *   - `asGuid` decides whether the signed-in trustee owns a verdict slot (WBS 6.4).
 *
 * A sloppy version of either fails silently in the direction that matters.
 */

/** A string value, or `null` for absent, empty or non-textual. */
export function asString(value: unknown): string | null {
  if (typeof value === "string") {
    const trimmed = value.trim();
    return trimmed.length > 0 ? trimmed : null;
  }
  if (typeof value === "number" && Number.isFinite(value)) return String(value);
  return null;
}

/** A finite number, or `null`. A numeric string is accepted; `""` and `NaN` are not. */
export function asNumber(value: unknown): number | null {
  if (typeof value === "number") return Number.isFinite(value) ? value : null;
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (trimmed.length === 0) return null;
    const parsed = Number(trimmed);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

/**
 * `true` only for an AFFIRMATIVE true. Everything else — `false`, `null`, `undefined`,
 * a missing key, `0`, `""`, an object, a column hidden by column security — is `false`.
 *
 * This is the fail-closed half of TAD §5.5. A Dataverse `bit` column arrives as a JSON
 * boolean, but the connector layer may hand back its string or numeric form, so those
 * three affirmative shapes are recognised and NOTHING else is. Widening this function
 * widens who can see a case.
 */
export function asAffirmativeBoolean(value: unknown): boolean {
  if (value === true) return true;
  if (value === 1) return true;
  if (typeof value === "string") return value.trim().toLowerCase() === "true";
  return false;
}

const GUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;

/**
 * A canonical lower-case, brace-free GUID, or `null`.
 *
 * Canonicalising matters: `_rev_trustee1_value` and `systemuserid` are compared to
 * decide whether a trustee may write a verdict. If one side arrived `{ABC…}` and the
 * other `abc…`, a real trustee would be shown a read-only screen with no explanation,
 * and nothing would log an error. Compare canonical forms, never raw strings.
 */
export function asGuid(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const bare = value.trim().replace(/^\{/, "").replace(/\}$/, "").toLowerCase();
  return GUID_PATTERN.test(bare) ? bare : null;
}

/** True when two lookup/id values refer to the same record. Never `true` for nulls. */
export function sameRecord(left: unknown, right: unknown): boolean {
  const a = asGuid(left);
  const b = asGuid(right);
  return a !== null && b !== null && a === b;
}

/** Escapes a value for use inside an OData string literal. */
export function odataString(value: string): string {
  return `'${value.replace(/'/g, "''")}'`;
}

/**
 * A GUID literal for an OData `eq`. Dataverse takes a bare GUID, unquoted.
 * Throws rather than emitting an unvalidated fragment into a filter.
 */
export function odataGuid(value: string): string {
  const guid = asGuid(value);
  if (guid === null) throw new Error(`Not a GUID: ${value}`);
  return guid;
}

/** Joins filter fragments with `and`, dropping empties. */
export function andFilters(...fragments: (string | undefined | null)[]): string | undefined {
  const kept = fragments.filter((f): f is string => typeof f === "string" && f.length > 0);
  if (kept.length === 0) return undefined;
  return kept.map((f) => `(${f})`).join(" and ");
}
