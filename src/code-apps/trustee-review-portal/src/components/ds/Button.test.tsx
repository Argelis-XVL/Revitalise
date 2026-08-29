/**
 * `ds/Button` — the converted design-system button (ADR-034).
 *
 * WHAT A CLASS ASSERTION IN THIS FILE DOES AND DOES NOT PROVE. Vitest does not process CSS
 * (`vitest.config.ts` sets no `css` option); the CSS-Module import resolves to a Proxy that
 * invents `_<key>_<hash>` for ANY key, including one the stylesheet does not declare. So
 * asserting a class here proves the component asked for the RIGHT KEY, and nothing about
 * whether `ds.module.css` declares it or what it declares. That half is
 * `src/styles/ds-tokens.test.ts`, which reads the stylesheet off disk — and it is why the
 * assertions below match on the key NAME as a substring rather than on `styles.x`, so the two
 * tests meet on the same string.
 *
 * The properties pinned here are the ones §8.5 depends on and a verbatim port would have
 * dropped: the default `type`, the forwarded `data-print`, and the forwarded `role`.
 */
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Button } from "./Button";

describe("ds/Button — the default type (§2.1.3)", () => {
  it("defaults to type='button', because the supplied component defaults to submit", () => {
    // `Button.jsx:26` sets no `type`, and a <button> with no type submits. VerdictForm.tsx
    // renders a real form, so the supplied default would have submitted it on every click.
    render(<Button>Record verdict</Button>);
    expect(screen.getByRole("button", { name: "Record verdict" })).toHaveAttribute(
      "type",
      "button",
    );
  });

  it("still lets a caller ask for a real submit button", () => {
    // The default must be overridable or a genuine submit control becomes inexpressible.
    render(<Button type="submit">Save</Button>);
    expect(screen.getByRole("button", { name: "Save" })).toHaveAttribute("type", "submit");
  });
});

describe("ds/Button — the attributes the app needs and the supplied contract omits", () => {
  it("forwards data-print, which is how the print path survives the conversion (§8.5 point 7)", () => {
    // print.css targets [data-print] and NEVER a class name, because CSS Module class names are
    // hashed at build time (print.css:15-16). The verdict action bars are hidden on paper by
    // data-print="hide".
    render(<Button data-print="hide">Print this list</Button>);
    expect(screen.getByRole("button", { name: "Print this list" })).toHaveAttribute(
      "data-print",
      "hide",
    );
  });

  it("forwards role, so a call site can change the element's semantics (§8.5 point 6)", () => {
    render(<Button role="menuitem">Sort</Button>);
    expect(screen.getByRole("menuitem", { name: "Sort" })).toBeInTheDocument();
  });

  it("forwards aria-* and className, both of which shipped code passes today", () => {
    // aria-*: the sort control's accessible name and the Refresh figures button's stable one.
    // className: the app's own styles.tallTarget and styles.sortButton.
    render(
      <Button aria-label="Sort by score, ascending" className="appOwnedClass">
        Score
      </Button>,
    );
    const button = screen.getByRole("button", { name: "Sort by score, ascending" });
    expect(button).toHaveClass("appOwnedClass");
    // The component's own base class is still there beside the caller's.
    expect(button.className).toContain("button");
  });

  it("passes the disabled attribute through and does not fire onClick", async () => {
    const onClick = vi.fn();
    render(
      <Button disabled onClick={onClick}>
        Blocked
      </Button>,
    );
    const button = screen.getByRole("button", { name: "Blocked" });
    expect(button).toBeDisabled();
    await userEvent.click(button);
    expect(onClick).not.toHaveBeenCalled();
  });

  it("fires onClick when it is not disabled", async () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Refresh figures</Button>);
    await userEvent.click(screen.getByRole("button", { name: "Refresh figures" }));
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});

describe("ds/Button — variants and sizes map to the keys ds.module.css declares", () => {
  it("asks for the size class matching each size, sm included (§2.2.2)", () => {
    // The 44px minimum target on ALL THREE sizes is asserted over the stylesheet itself in
    // ds-tokens.test.ts. This asserts the component reaches the class that carries it — the
    // per-row Record verdict control is size="sm" in the mockup, and that is the one that would
    // otherwise have landed under 44px.
    for (const [size, key] of [
      ["sm", "buttonSm"],
      ["md", "buttonMd"],
      ["lg", "buttonLg"],
    ] as const) {
      const { unmount } = render(<Button size={size}>{size}</Button>);
      expect(screen.getByRole("button", { name: size }).className, size).toContain(key);
      unmount();
    }
  });

  it("defaults to the md size and the primary variant", () => {
    render(<Button>Default</Button>);
    const className = screen.getByRole("button", { name: "Default" }).className;
    expect(className).toContain("buttonMd");
    expect(className).toContain("buttonPrimary");
  });

  it("asks for the variant class matching each variant", () => {
    for (const [variant, key] of [
      ["primary", "buttonPrimary"],
      ["secondary", "buttonSecondary"],
      ["ghost", "buttonGhost"],
    ] as const) {
      const { unmount } = render(<Button variant={variant}>{variant}</Button>);
      expect(screen.getByRole("button", { name: variant }).className, variant).toContain(key);
      unmount();
    }
  });
});

describe("ds/Button — the icon slot", () => {
  it("renders an icon before the label when one is given", () => {
    render(
      <Button icon={<span data-testid="glyph">*</span>}>Download</Button>,
    );
    const button = screen.getByRole("button", { name: /Download/ });
    expect(screen.getByTestId("glyph")).toBeInTheDocument();
    // Order matters: the icon is a leading adornment, not a trailing one.
    expect(button.firstElementChild).toHaveAttribute("data-testid", "glyph");
  });

  it("renders no extra element when no icon is given", () => {
    render(<Button>Plain</Button>);
    expect(screen.getByRole("button", { name: "Plain" }).children).toHaveLength(0);
  });

  it("carries no inline style attribute at all", () => {
    // The whole reason the conversion exists (§2.1.1 point 4, ADR-034): an inline style
    // attribute outranks every plain rule in print.css, of which only print.css:22 is
    // !important, so a component carrying its own background PRINTS it — and print.test.ts
    // reads the stylesheet as text and cannot see that.
    render(<Button variant="secondary">No inline style</Button>);
    expect(
      screen.getByRole("button", { name: "No inline style" }).hasAttribute("style"),
    ).toBe(false);
  });
});
