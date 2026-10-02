/**
 * The restricted-field catalogue's app-facing surface (ADR-032, FR-078, TAD §3.2.3).
 *
 * The catalogue itself (`src/generated/trusteeRestrictedFieldCatalogue.ts`) is generated —
 * see that file's header and `scripts/generate-trustee-field-catalogue.py`. This module is
 * hand-authored and does the one thing the generated data cannot do for itself: turn a group
 * name into the definition-list rows a panel renders, with the one sentence FR-078 requires
 * attached to every one of them.
 *
 * `RESTRICTED_VALUE_TEXT` is the "value" half of each row (`Definitions` renders label/value
 * pairs). It is deliberately not "Withheld" alone or a blank dash: FR-078 says a restricted
 * field must be told apart from a question the applicant did not answer, so the text names
 * the mechanism rather than just the outcome.
 */
import { TRUSTEE_RESTRICTED_FIELD_CATALOGUE } from "../generated/trusteeRestrictedFieldCatalogue";

export const RESTRICTED_VALUE_TEXT =
  "Restricted — this field is protected by column-level security and is not requested by this app.";

/**
 * The two board-pack groups SDD §7.1b actually populates. A third, "Condition and
 * circumstance", is named in §7.1b too but carries zero Group-B (secured, non-free-text)
 * columns — every one of its secured columns is free text with a redacted counterpart
 * instead (ADR-031) — so it is deliberately absent here rather than declared with an empty
 * list nothing ever checks.
 */
export const FIELD_CATALOGUE_GROUPS = {
  financialEligibility: "Financial eligibility",
  helperRefereeEmergencyContact: "Helper, referee and emergency contact",
} as const;

/**
 * Every catalogue entry in one group, as `Definitions` items. Order is the generated
 * file's own order (SDD §7.1b group order, then the manifest's within-group order) — never
 * re-sorted here, so "Helper Name" stays beside "Helper Email" rather than falling out
 * alphabetically among the referee and emergency-contact rows.
 */
export function restrictedFieldsForGroup(group: string): { label: string; value: string }[] {
  return TRUSTEE_RESTRICTED_FIELD_CATALOGUE.filter((entry) => entry.group === group).map(
    (entry) => ({ label: entry.label, value: RESTRICTED_VALUE_TEXT }),
  );
}
