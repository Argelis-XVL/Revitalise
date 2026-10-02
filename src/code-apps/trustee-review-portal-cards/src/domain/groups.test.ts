/**
 * Group derivation (EF-43) — grouping, member counting, summing and the shared-dates
 * fallback. See `groups.ts`'s header for the plan citation and what is deliberately absent
 * (validation of the code, and a group total cost).
 */
import { describe, expect, it } from "vitest";
import { deriveGroups } from "./groups";
import { makeSummary } from "../test/harness";

describe("deriveGroups", () => {
  it("returns no groups when nothing carries a group code", () => {
    const rows = [makeSummary({ id: "a", groupLinkage: null }), makeSummary({ id: "b", groupLinkage: "" })];
    expect(deriveGroups(rows)).toEqual([]);
  });

  it("groups by an EXACT string match, typos and all — no normalising", () => {
    const rows = [
      makeSummary({ id: "a", groupLinkage: "RA" }),
      makeSummary({ id: "b", groupLinkage: "RA" }),
      // A typo'd/mistyped code is its own separate one-member group, not silently merged.
      makeSummary({ id: "c", groupLinkage: "ra" }),
    ];
    const groups = deriveGroups(rows);
    // Two distinct groups — the point of the test — in whichever order `localeCompare`
    // puts them (case is not the property under test here).
    expect(groups).toHaveLength(2);
    expect(groups.map((g) => g.memberCount).sort()).toEqual([1, 2]);
    expect(new Set(groups.map((g) => g.code))).toEqual(new Set(["RA", "ra"]));
  });

  it("orders groups by code, locale-aware", () => {
    const rows = [
      makeSummary({ id: "a", groupLinkage: "300" }),
      makeSummary({ id: "b", groupLinkage: "43" }),
      makeSummary({ id: "c", groupLinkage: "RA" }),
    ];
    expect(deriveGroups(rows).map((g) => g.code)).toEqual(["300", "43", "RA"]);
  });

  it("leaves ungrouped rows out entirely — the flat list still shows them", () => {
    const rows = [
      makeSummary({ id: "a", groupLinkage: "RA" }),
      makeSummary({ id: "b", groupLinkage: null }),
    ];
    const groups = deriveGroups(rows);
    expect(groups).toHaveLength(1);
    expect(groups[0]?.members.map((m) => m.id)).toEqual(["a"]);
  });

  describe("totalRequested — summed, never derived from cost", () => {
    it("sums the members' own amountRequested fields", () => {
      const rows = [
        makeSummary({ id: "a", groupLinkage: "RA", amountRequested: 350 }),
        makeSummary({ id: "b", groupLinkage: "RA", amountRequested: 350 }),
        makeSummary({ id: "c", groupLinkage: "RA", amountRequested: 350 }),
        makeSummary({ id: "d", groupLinkage: "RA", amountRequested: 350 }),
      ];
      expect(deriveGroups(rows)[0]?.totalRequested).toBe(1400);
    });

    it("treats an absent amount as zero when at least one member has one", () => {
      const rows = [
        makeSummary({ id: "a", groupLinkage: "101", amountRequested: 500 }),
        makeSummary({ id: "b", groupLinkage: "101", amountRequested: null }),
      ];
      expect(deriveGroups(rows)[0]?.totalRequested).toBe(500);
    });

    it("is null, not zero, when no member has a recorded amount", () => {
      const rows = [
        makeSummary({ id: "a", groupLinkage: "101", amountRequested: null }),
        makeSummary({ id: "b", groupLinkage: "101", amountRequested: null }),
      ];
      expect(deriveGroups(rows)[0]?.totalRequested).toBeNull();
    });

    it("has no group-cost field at all — the plan's own decision not to sum rev_costs", () => {
      const rows = [makeSummary({ id: "a", groupLinkage: "RA" })];
      expect(deriveGroups(rows)[0]).not.toHaveProperty("totalCost");
      expect(deriveGroups(rows)[0]).not.toHaveProperty("cost");
    });
  });

  describe("shared dates — earliest start, latest end, when members do not literally agree", () => {
    it("returns the single date when every member genuinely shares it", () => {
      const rows = [
        makeSummary({
          id: "a",
          groupLinkage: "RA",
          preferredStart: "2026-10-05T00:00:00Z",
          preferredEnd: "2026-10-12T00:00:00Z",
        }),
        makeSummary({
          id: "b",
          groupLinkage: "RA",
          preferredStart: "2026-10-05T00:00:00Z",
          preferredEnd: "2026-10-12T00:00:00Z",
        }),
      ];
      const group = deriveGroups(rows)[0];
      expect(group?.sharedStart).toBe("2026-10-05T00:00:00Z");
      expect(group?.sharedEnd).toBe("2026-10-12T00:00:00Z");
    });

    it("spans earliest-start/latest-end when members disagree", () => {
      const rows = [
        makeSummary({
          id: "a",
          groupLinkage: "RA",
          preferredStart: "2026-10-05T00:00:00Z",
          preferredEnd: "2026-10-10T00:00:00Z",
        }),
        makeSummary({
          id: "b",
          groupLinkage: "RA",
          preferredStart: "2026-10-01T00:00:00Z",
          preferredEnd: "2026-10-12T00:00:00Z",
        }),
      ];
      const group = deriveGroups(rows)[0];
      expect(group?.sharedStart).toBe("2026-10-01T00:00:00Z");
      expect(group?.sharedEnd).toBe("2026-10-12T00:00:00Z");
    });

    it("ignores members with no recorded date rather than treating an absence as earliest/latest", () => {
      const rows = [
        makeSummary({ id: "a", groupLinkage: "RA", preferredStart: null, preferredEnd: null }),
        makeSummary({
          id: "b",
          groupLinkage: "RA",
          preferredStart: "2026-10-05T00:00:00Z",
          preferredEnd: "2026-10-12T00:00:00Z",
        }),
      ];
      const group = deriveGroups(rows)[0];
      expect(group?.sharedStart).toBe("2026-10-05T00:00:00Z");
      expect(group?.sharedEnd).toBe("2026-10-12T00:00:00Z");
    });

    it("is null when no member has any recorded date", () => {
      const rows = [
        makeSummary({ id: "a", groupLinkage: "RA", preferredStart: null, preferredEnd: null }),
      ];
      const group = deriveGroups(rows)[0];
      expect(group?.sharedStart).toBeNull();
      expect(group?.sharedEnd).toBeNull();
    });
  });
});
