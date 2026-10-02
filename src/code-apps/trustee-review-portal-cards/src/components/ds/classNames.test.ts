/**
 * The class-name joiner. Small, but it is the one place a missing CSS-Module class turns into
 * either a clean omission or the literal word "undefined" in a `class` attribute.
 *
 * WHY THE `undefined` INPUTS ARE NOT HYPOTHETICAL. Vite types a CSS Module as an index signature
 * (`vite/client.d.ts:4`) and `tsconfig.json` sets `noUncheckedIndexedAccess`, so every
 * `styles.x` in `components/ds/` is `string | undefined` at compile time — and in a REAL Vite
 * build a renamed-away class genuinely resolves to `undefined` at runtime. (Under vitest it does
 * not: the CSS stub is a Proxy that invents a class name for any key, which is exactly why this
 * behaviour is unit-tested here rather than inferred from a component render.)
 */
import { describe, expect, it } from "vitest";
import { classNames } from "./classNames";

describe("classNames", () => {
  it("joins the parts that are present, in order", () => {
    expect(classNames("a", "b", "c")).toBe("a b c");
  });

  it("drops an absent class rather than writing 'undefined' into the attribute", () => {
    // The defect this exists to prevent: `class="_button_abc undefined"`.
    expect(classNames("a", undefined, "b")).toBe("a b");
    expect(classNames(undefined, undefined)).toBeUndefined();
  });

  it("drops null, false and the empty string too", () => {
    expect(classNames("a", null, false, "", "b")).toBe("a b");
  });

  it("returns undefined rather than an empty string when nothing survives", () => {
    // So a component never emits a bare `class=""`.
    expect(classNames()).toBeUndefined();
    expect(classNames("", null)).toBeUndefined();
  });
});
