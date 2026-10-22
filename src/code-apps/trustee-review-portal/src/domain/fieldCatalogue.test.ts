/**
 * The restricted-field catalogue (ADR-032, FR-078, TAD §3.2.3).
 *
 * Deliberately asserts STRUCTURAL properties only — count, groups, the shared value text,
 * uniqueness — and never a specific Dataverse column name. The generated catalogue itself
 * carries none (see `src/generated/trusteeRestrictedFieldCatalogue.ts`'s own header), and a
 * test here must not reintroduce one: this file lives under `src/code-apps/trustee-review-
 * portal`, which `no-secured-columns-in-code-app` scans, unlike the generated file it is
 * excluded from scanning.
 */
import { describe, expect, it } from "vitest";
import {
  FIELD_CATALOGUE_GROUPS,
  RESTRICTED_VALUE_TEXT,
  restrictedFieldsForGroup,
} from "./fieldCatalogue";
import { TRUSTEE_RESTRICTED_FIELD_CATALOGUE } from "../generated/trusteeRestrictedFieldCatalogue";

describe("TRUSTEE_RESTRICTED_FIELD_CATALOGUE — the generated data", () => {
  it("carries exactly eighteen entries — the helper, referee and emergency-contact columns (SDD A-14 removed the three financial ones)", () => {
    // EF-10 (2026-09-17) reclassified two previously IsSecured=0 helper columns as IsSecured=1
    // and added them to REV_TrusteeRestricted — catalogue grows from 11 to 13; the eight referee-* columns (CO-008) take it to 21.
    // SDD A-14 (2026-10-22, ADR-085): benefit status, benefit provider and employment status are
    // released to trustees read only and left the catalogue — 21 to 18.
    expect(TRUSTEE_RESTRICTED_FIELD_CATALOGUE).toHaveLength(18);
  });

  it("keeps the other eighteen keys unchanged, and drops exactly the three released ones (WI-0146 positive control)", () => {
    expect(TRUSTEE_RESTRICTED_FIELD_CATALOGUE.map((entry) => entry.key)).toEqual([
      "helper-organisation", "helper-relationship", "helper-name", "helper-email", "helper-phone",
      "referee-name", "referee-email", "referee-phone", "referee-first-name", "referee-last-name",
      "referee-title", "referee-job-title", "referee-company", "referee-address",
      "referee-town-city", "referee-postcode", "emergency-contact-name", "emergency-contact-phone",
    ]);
    const keys = new Set(TRUSTEE_RESTRICTED_FIELD_CATALOGUE.map((entry) => entry.key));
    for (const released of ["benefit-status", "benefit-provider", "employment-status"]) {
      expect(keys.has(released)).toBe(false);
    }
  });

  it("marks every entry restricted, always", () => {
    for (const entry of TRUSTEE_RESTRICTED_FIELD_CATALOGUE) {
      expect(entry.restricted).toBe(true);
    }
  });

  it("has a non-empty label and key for every entry", () => {
    for (const entry of TRUSTEE_RESTRICTED_FIELD_CATALOGUE) {
      expect(entry.key.length).toBeGreaterThan(0);
      expect(entry.label.length).toBeGreaterThan(0);
    }
  });

  it("uses no group other than the one SDD §7.1b still populates", () => {
    const groups: Set<string> = new Set(Object.values(FIELD_CATALOGUE_GROUPS));
    for (const entry of TRUSTEE_RESTRICTED_FIELD_CATALOGUE) {
      expect(groups.has(entry.group)).toBe(true);
    }
  });

  it("has no duplicate keys and no duplicate labels", () => {
    const keys = TRUSTEE_RESTRICTED_FIELD_CATALOGUE.map((entry) => entry.key);
    const labels = TRUSTEE_RESTRICTED_FIELD_CATALOGUE.map((entry) => entry.label);
    expect(new Set(keys).size).toBe(keys.length);
    expect(new Set(labels).size).toBe(labels.length);
  });
});

describe("restrictedFieldsForGroup", () => {
  it("returns nothing for Financial eligibility since SDD A-14 released its three answers", () => {
    expect(restrictedFieldsForGroup("Financial eligibility")).toEqual([]);
  });

  it("returns eighteen entries for Helper, referee and emergency contact — EF-10 added two, CO-008 eight", () => {
    // EF-10 (2026-09-17) added helper-organisation and helper-relationship to this group.
    const items = restrictedFieldsForGroup(
      FIELD_CATALOGUE_GROUPS.helperRefereeEmergencyContact,
    );
    expect(items).toHaveLength(18);
  });

  it("returns nothing for a group the catalogue has no entries for", () => {
    // "Condition and circumstance" is named in SDD §7.1b but carries zero Group-B
    // columns — every secured column in that group is free text with a redacted
    // counterpart instead (ADR-031). An unknown group returns [], not an error, so a
    // typo in a group name fails a count assertion loudly rather than throwing deep
    // inside a render.
    expect(restrictedFieldsForGroup("Condition and circumstance")).toEqual([]);
    expect(restrictedFieldsForGroup("Not a real group")).toEqual([]);
  });

  it("gives every row the same value text — FR-078's named restricted state", () => {
    const items = restrictedFieldsForGroup(FIELD_CATALOGUE_GROUPS.helperRefereeEmergencyContact);
    expect(items.length).toBeGreaterThan(0);
    for (const item of items) {
      expect(item.value).toBe(RESTRICTED_VALUE_TEXT);
      expect(item.label.length).toBeGreaterThan(0);
    }
  });

  it("preserves the catalogue's own order rather than re-sorting", () => {
    const wholeGroupInOrder = TRUSTEE_RESTRICTED_FIELD_CATALOGUE.filter(
      (entry) => entry.group === FIELD_CATALOGUE_GROUPS.helperRefereeEmergencyContact,
    ).map((entry) => entry.label);
    const items = restrictedFieldsForGroup(FIELD_CATALOGUE_GROUPS.helperRefereeEmergencyContact);
    expect(items.map((item) => item.label)).toEqual(wholeGroupInOrder);
  });
});
