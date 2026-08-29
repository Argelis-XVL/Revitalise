/*
 * GENERATED — do not hand-edit. Regenerate with
 * `python3 scripts/generate-trustee-field-catalogue.py` (see that script's docstring)
 * after any change to Other/FieldSecurityProfiles.xml or Entities/rev_application/Entity.xml.
 * CI and the `trustee-field-catalogue` build step verify it is current with `--check`.
 *
 * ADR-032, FR-078, TAD §3.2.3 — the eleven `REV_TrusteeRestricted` columns Amendment A-05
 * puts on the trustee detail screen's board pack, rendered as a restricted state WITHOUT
 * ever being queried. This file is NOT `pac`/`pa` CLI output (unlike its siblings under
 * src/generated/) — it lives here because that directory is the one place this app's own
 * build gate (`no-secured-columns-in-code-app`) already treats as generator output.
 *
 * Deliberately carries NO Dataverse logical column name — see the generation script's
 * docstring for why. `restricted` is always `true`; it is a literal here, not a query result.
 */

export interface TrusteeRestrictedFieldCatalogueEntry {
  readonly key: string;
  readonly label: string;
  readonly group: string;
  readonly restricted: true;
}

export const TRUSTEE_RESTRICTED_FIELD_CATALOGUE: readonly TrusteeRestrictedFieldCatalogueEntry[] = [
  { key: "benefit-status", label: "Receives Means-Tested Benefits", group: "Financial eligibility", restricted: true },
  { key: "benefit-provider", label: "Benefit Provider", group: "Financial eligibility", restricted: true },
  { key: "employment-status", label: "Employment Status", group: "Financial eligibility", restricted: true },
  { key: "helper-name", label: "Helper Name", group: "Helper, referee and emergency contact", restricted: true },
  { key: "helper-email", label: "Helper Email", group: "Helper, referee and emergency contact", restricted: true },
  { key: "helper-phone", label: "Helper Phone", group: "Helper, referee and emergency contact", restricted: true },
  { key: "referee-name", label: "Referee Name", group: "Helper, referee and emergency contact", restricted: true },
  { key: "referee-email", label: "Referee Email", group: "Helper, referee and emergency contact", restricted: true },
  { key: "referee-phone", label: "Referee Phone", group: "Helper, referee and emergency contact", restricted: true },
  { key: "emergency-contact-name", label: "Emergency Contact Name", group: "Helper, referee and emergency contact", restricted: true },
  { key: "emergency-contact-phone", label: "Emergency Contact Phone", group: "Helper, referee and emergency contact", restricted: true },
] as const;
