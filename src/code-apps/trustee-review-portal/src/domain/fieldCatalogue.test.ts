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
  it("carries exactly eleven entries — Amendment A-05 Finding 1's Group B", () => {
    expect(TRUSTEE_RESTRICTED_FIELD_CATALOGUE).toHaveLength(11);
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

  it("uses no group other than the two SDD §7.1b actually populates", () => {
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
  it("returns three entries for Financial eligibility", () => {
    const items = restrictedFieldsForGroup(FIELD_CATALOGUE_GROUPS.financialEligibility);
    expect(items).toHaveLength(3);
  });

  it("returns eight entries for Helper, referee and emergency contact", () => {
    const items = restrictedFieldsForGroup(
      FIELD_CATALOGUE_GROUPS.helperRefereeEmergencyContact,
    );
    expect(items).toHaveLength(8);
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
    const items = restrictedFieldsForGroup(FIELD_CATALOGUE_GROUPS.financialEligibility);
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
