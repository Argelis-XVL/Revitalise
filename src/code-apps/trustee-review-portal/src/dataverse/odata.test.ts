/**
 * The wire-format helpers. Two of these carry security-relevant behaviour:
 * `asAffirmativeBoolean` decides visibility, `asGuid`/`sameRecord` decide slot ownership.
 */
import { describe, expect, it } from "vitest";
import {
  andFilters,
  asAffirmativeBoolean,
  asGuid,
  asNumber,
  asString,
  odataGuid,
  odataString,
  sameRecord,
} from "./odata";

describe("asAffirmativeBoolean — the fail-closed primitive", () => {
  it("accepts the three affirmative shapes a bit column takes on the wire", () => {
    expect(asAffirmativeBoolean(true)).toBe(true);
    expect(asAffirmativeBoolean(1)).toBe(true);
    expect(asAffirmativeBoolean("true")).toBe(true);
    expect(asAffirmativeBoolean("TRUE")).toBe(true);
    expect(asAffirmativeBoolean(" true ")).toBe(true);
  });

  it("rejects everything else, including the shapes that look truthy", () => {
    for (const value of [
      false,
      null,
      undefined,
      0,
      2,
      "",
      "yes",
      "1",
      "false",
      {},
      [],
      [1],
      "on",
    ]) {
      expect(asAffirmativeBoolean(value)).toBe(false);
    }
  });
});

describe("asGuid and sameRecord", () => {
  const guid = "11111111-1111-4111-8111-111111111111";

  it("canonicalises case and braces", () => {
    expect(asGuid(`{${guid.toUpperCase()}}`)).toBe(guid);
    expect(asGuid(` ${guid} `)).toBe(guid);
  });

  it("rejects anything that is not a guid", () => {
    for (const value of [null, undefined, "", "not-a-guid", 42, {}, `${guid}extra`]) {
      expect(asGuid(value)).toBeNull();
    }
  });

  it("matches two representations of the same record", () => {
    expect(sameRecord(`{${guid.toUpperCase()}}`, guid)).toBe(true);
  });

  it("never matches when either side is absent", () => {
    // The important half. If two nulls compared equal, an unidentified user would own
    // every unassigned verdict slot.
    expect(sameRecord(null, null)).toBe(false);
    expect(sameRecord(null, guid)).toBe(false);
    expect(sameRecord(guid, undefined)).toBe(false);
    expect(sameRecord("", "")).toBe(false);
  });
});

describe("asString", () => {
  it("trims, and treats whitespace-only as absent", () => {
    expect(asString("  hello  ")).toBe("hello");
    expect(asString("   ")).toBeNull();
    expect(asString("")).toBeNull();
  });
  it("accepts a number, rejects other types", () => {
    expect(asString(7)).toBe("7");
    expect(asString(null)).toBeNull();
    expect(asString({})).toBeNull();
    expect(asString(Number.NaN)).toBeNull();
  });
});

describe("asNumber", () => {
  it("accepts numbers and numeric strings, including zero", () => {
    expect(asNumber(0)).toBe(0);
    expect(asNumber("0")).toBe(0);
    expect(asNumber("42")).toBe(42);
    expect(asNumber(-3.5)).toBe(-3.5);
  });
  it("rejects empty, non-numeric and non-finite values", () => {
    for (const value of ["", "  ", "abc", null, undefined, {}, Number.NaN, Infinity]) {
      expect(asNumber(value)).toBeNull();
    }
  });
});

describe("OData literals", () => {
  it("doubles single quotes in a string literal", () => {
    expect(odataString("O'Brien")).toBe("'O''Brien'");
  });

  it("emits a bare guid, unquoted", () => {
    const guid = "11111111-1111-4111-8111-111111111111";
    expect(odataGuid(`{${guid.toUpperCase()}}`)).toBe(guid);
  });

  it("throws rather than emitting an unvalidated fragment into a filter", () => {
    expect(() => odataGuid("' or 1 eq 1 --")).toThrow(/Not a GUID/);
  });

  it("joins fragments with and, parenthesised, and drops empties", () => {
    expect(andFilters("a eq 1", undefined, "", "b eq 2")).toBe("(a eq 1) and (b eq 2)");
    expect(andFilters(undefined, null, "")).toBeUndefined();
  });
});
