/**
 * Regression coverage for `IMP-0486`'s Select-sizing defect: the reviewer saw "Review
 * round"/"Status"/"Region" render at Fluent's native size while "Score from"/"Score to" (the
 * `ds/Input`-backed pair right beside them) carried the design system's box. Two halves, per
 * `IMP-0386`'s rule that a component test proves which class KEY was requested and nothing
 * about the stylesheet, and a stylesheet claim is asserted by reading the file off disk:
 *
 *   1. The three `<select>` elements ask for `styles.filterSelect` — not `ApplicationFilters`
 *      inventing a new design-system component (this file's own header explains why not: the
 *      design system has no `Select` at all), and not a top-level `className` on `<Select>`,
 *      which `@fluentui/react-select`'s `getPartitionedNativeProps` routes to the outer
 *      wrapper `<span>` rather than the `<select>` element itself.
 *   2. `app.module.css`'s `.filterSelect` rule actually carries the box `ds/Input` uses
 *      (`min-height`, `--border-strong`), read as text, never through the CSS-Modules Proxy
 *      vitest substitutes (`vitest.config.ts` sets no `css` option, so no class body is ever
 *      real inside a test).
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApplicationFilters } from "./ApplicationFilters";
import { EMPTY_FILTERS } from "../domain/listView";

describe("ApplicationFilters — the three Selects ask for styles.filterSelect (IMP-0486)", () => {
  it("puts filterSelect on Review round, Status and Region", () => {
    render(
      <ApplicationFilters
        filters={EMPTY_FILTERS}
        rounds={["Spring 2026"]}
        statuses={[{ value: 1, label: "Submitted" }]}
        regions={[{ value: 1, label: "North West" }]}
        onChange={vi.fn()}
      />,
    );

    for (const name of ["Review round", "Status", "Region"]) {
      const select = screen.getByLabelText(name);
      expect(select.className, name).toContain("filterSelect");
    }
  });

  it("does not render a Region control at all when no region is readable — filterSelect has nothing to miss", () => {
    render(
      <ApplicationFilters
        filters={EMPTY_FILTERS}
        rounds={[]}
        statuses={[]}
        regions={[]}
        onChange={vi.fn()}
      />,
    );
    expect(screen.queryByLabelText("Region")).toBeNull();
  });
});

describe("app.module.css's .filterSelect rule (IMP-0486)", () => {
  const APP_MODULE = readFileSync(join(__dirname, "..", "styles", "app.module.css"), "utf8");

  /** Innermost rule blocks: `selector { body }` — same technique as `ds-tokens.test.ts`. */
  function rules(css: string): { selector: string; body: string }[] {
    return [...css.replace(/\/\*[\s\S]*?\*\//g, "").matchAll(/([^{}]+)\{([^{}]*)\}/g)].map(
      (match) => ({
        selector: match[1]!.trim().replace(/\s+/g, " "),
        body: match[2]!,
      }),
    );
  }

  it("matches ds/Input's box: 44px min-height and the --border-strong boundary", () => {
    const rule = rules(APP_MODULE).find((candidate) => candidate.selector === ".filterSelect");
    expect(rule, ".filterSelect rule must exist in app.module.css").toBeDefined();
    expect(rule!.body).toMatch(/min-height\s*:\s*44px/);
    expect(rule!.body).toContain("--border-strong");
    // ADR-037 correction 4's own rule, restated here rather than assumed: the WEAK boundary
    // token must never be the one a control's own perceivability depends on.
    expect(rule!.body).not.toContain("--border-default");
  });

  it("leaves horizontal padding to Fluent — only vertical padding is overridden", () => {
    const rule = rules(APP_MODULE).find((candidate) => candidate.selector === ".filterSelect");
    // `padding-top:`/`padding-bottom:` do NOT match `\bpadding\s*:` (the character after
    // "padding" is "-", not whitespace or ":"), so this only refuses the SHORTHAND, which
    // would reintroduce Fluent's own icon-spacing right padding — see this class's own comment.
    expect(rule!.body).not.toMatch(/\bpadding\s*:/);
    expect(rule!.body).not.toMatch(/padding-(?:left|right)\s*:/);
  });
});
