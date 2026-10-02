/**
 * The design-system barrel — the import path every consumer uses.
 *
 * WHY THIS IS WORTH A TEST RATHER THAN JUST COVERAGE. The design system's own adherence lint
 * requires consumers to import from the barrel and not from component internals
 * (`_adherence.oxlintrc.json` → "Import design-system components from 'index.js', not component
 * internals"), and nothing in this app's eslint config enforces that. So the barrel is a real
 * contract with a real failure mode: add a component file, forget the barrel line, and the
 * component is unreachable through the documented path while every other gate stays green.
 *
 * It also pins the SHAPE of the surface Package B will consume: exactly seven components, and
 * `classNames` deliberately absent because the barrel is the component surface rather than a
 * grab-bag of internals.
 */
import { describe, expect, it } from "vitest";
import * as ds from "./index";

/** The seven components ADR-033 adopts. */
const ADOPTED = ["Button", "Card", "Checkbox", "Input", "Notice", "Radio", "StatTile"] as const;

/**
 * The six the TAD deliberately does NOT convert (§2.1.2): no screen in this app renders an
 * accordion, a social icon, a marketing navbar, a site footer, a cookie banner or a newsletter
 * form, and converting a component nothing renders is dead code that still has to be
 * maintained, audited and counted in the coverage denominator (A-R41).
 */
const NOT_CONVERTED = [
  "Accordion",
  "Badge",
  "Navbar",
  "Footer",
  "CookieBanner",
  "NewsletterForm",
] as const;

describe("components/ds barrel", () => {
  it("re-exports all seven adopted components as callable functions", () => {
    for (const name of ADOPTED) {
      expect(typeof ds[name], name).toBe("function");
    }
  });

  it("exports exactly those seven and nothing else at runtime", () => {
    // Type-only exports compile away, so this is the runtime surface. A new component reaching
    // the directory without a barrel line — or an internal leaking out of it — fails here.
    expect(Object.keys(ds).sort()).toEqual([...ADOPTED].sort());
  });

  it("does not export the classNames helper", () => {
    // Stated in the barrel's own header: it is an internal detail of the conversion.
    expect("classNames" in ds).toBe(false);
  });

  it("does not export the six components the TAD declines to convert", () => {
    for (const name of NOT_CONVERTED) {
      expect(name in ds, name).toBe(false);
    }
  });
});
