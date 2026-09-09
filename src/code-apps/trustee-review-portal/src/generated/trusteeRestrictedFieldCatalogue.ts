/*
 * GENERATED — do not hand-edit. Regenerate with the manifest and generation command named in
 * this repository's build config after any change to the securing field security profile or
 * the source entity's Entity.xml. A build step verifies it is current with --check.
 *
 * Renders a restricted state WITHOUT ever being queried. Deliberately carries NO Dataverse
 * logical column name — see the generation script's docstring for why. `restricted` is always
 * `true`; it is a literal here, not a query result.
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
