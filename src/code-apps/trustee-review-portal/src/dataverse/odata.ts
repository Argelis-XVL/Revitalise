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

/**
 * A tri-state boolean: `true`, `false`, or `null` for absent/unreadable/unrecognised.
 *
 * Deliberately NOT `asAffirmativeBoolean` above, and not a replacement for it —
 * `asAffirmativeBoolean` exists ONLY for the two visibility-gate columns (TAD §5.5),
 * where "anything that is not an affirmative true" must collapse to one closed state.
 * A plain informational yes/no answer (Amendment A-05's financial-eligibility and
 * helper-declaration columns) is a different shape: several of those columns' own
 * `Entity.xml` descriptions say explicitly that an absent value is a NORMAL, expected
 * state ("collected only when a helper is involved") and must stay distinguishable from
 * an explicit "No" — collapsing null into false here would be exactly the "not answered"
 * vs "answered no" conflation those columns' own comments warn against.
 */
export function asNullableBoolean(value: unknown): boolean | null {
  if (value === true || value === 1) return true;
  if (value === false || value === 0) return false;
  if (typeof value === "string") {
    const trimmed = value.trim().toLowerCase();
    if (trimmed === "true") return true;
    if (trimmed === "false") return false;
  }
  return null;
}

/**
 * A multi-select picklist's selected values, or `null` for absent/empty/unreadable.
 *
 * A-TR-13 (GUESS, E3) — Dataverse's Web API convention returns a `multiselectpicklist`
 * column as a comma-separated string of option values (e.g. `"1,3,7"`) over OData. This
 * has not been observed live through THIS app's connector — same unverified-connector-shape
 * class as A-TR-7 (`schema.ts`). Written defensively rather than assumed one way: an array
 * of numbers is accepted too, so whichever shape the connector actually hands back is read
 * correctly. Cheapest verification: read `rev_careprovidedtype` for one populated
 * application row through the app and log the raw value's `typeof`.
 */
export function asNumberArray(value: unknown): number[] | null {
  if (Array.isArray(value)) {
    const numbers = value.map((entry) => asNumber(entry)).filter((n): n is number => n !== null);
    return numbers.length > 0 ? numbers : null;
  }
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (trimmed.length === 0) return null;
    const numbers = trimmed
      .split(",")
      .map((part) => asNumber(part))
      .filter((n): n is number => n !== null);
    return numbers.length > 0 ? numbers : null;
  }
  return null;
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
