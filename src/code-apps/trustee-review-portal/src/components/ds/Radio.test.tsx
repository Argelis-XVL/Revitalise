/**
 * `ds/Radio` — the converted design-system radio (ADR-034).
 *
 * SCOPE NOTE. This replaces Fluent's `Radio` and NOT its `RadioGroup` (§2.1.4): a group carries
 * roving tabindex and arrow-key behaviour, and the supplied `Radio.jsx:6` is a bare
 * `<input type="radio">` with an `accentColor` — the mockup wires three of them with no group
 * semantics at all. So `RadioGroup`, `Field` and `Label` stay around this component.
 *
 * See `Button.test.tsx`'s header for what a class assertion here does and does not prove.
 */
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Radio } from "./Radio";

describe("ds/Radio", () => {
  it("renders a radio input with its label programmatically associated", () => {
    // The control sits inside its own <label>, which is an implicit and correct association
    // (WCAG 1.3.1, 3.3.2).
    render(<Radio label="Support" name="verdict" />);
    const control = screen.getByRole("radio", { name: "Support" });
    expect(control).toHaveAttribute("type", "radio");
    expect(screen.getByLabelText("Support")).toBe(control);
  });

  it("cannot be configured into a different control type", () => {
    // `type` is Omitted from the props: a Radio that renders a checkbox is a bug, not a
    // configuration, and a compile error is cheaper than a code review. This records the
    // runtime half — the element is always a radio.
    render(<Radio label="Decline" name="verdict" />);
    expect(screen.getByRole("radio", { name: "Decline" })).toHaveAttribute("type", "radio");
    expect(screen.queryByRole("checkbox")).toBeNull();
  });

  it("puts data-print on the label, so the caption is hidden with the control", () => {
    const { container } = render(<Radio label="Support" data-print="hide" />);
    expect(container.firstElementChild?.tagName).toBe("LABEL");
    expect(container.firstElementChild).toHaveAttribute("data-print", "hide");
  });

  it("forwards role (§8.5 point 6) to the input, which is the semantic control", () => {
    render(<Radio label="Support" role="menuitemradio" />);
    expect(screen.getByRole("menuitemradio", { name: "Support" })).toBeInTheDocument();
  });

  it("forwards name, checked, onChange and disabled", async () => {
    const onChange = vi.fn();
    const { unmount } = render(
      <Radio label="Support" name="verdict" value="1" onChange={onChange} />,
    );
    const control = screen.getByRole("radio", { name: "Support" });
    expect(control).toHaveAttribute("name", "verdict");
    await userEvent.click(control);
    expect(onChange).toHaveBeenCalledTimes(1);
    unmount();

    render(<Radio label="Support" disabled />);
    expect(screen.getByRole("radio", { name: "Support" })).toBeDisabled();
  });

  it("reflects the checked state it is given", () => {
    render(<Radio label="Support" checked readOnly />);
    expect(screen.getByRole("radio", { name: "Support" })).toBeChecked();
  });

  it("forwards className alongside its own choice class", () => {
    const { container } = render(<Radio label="Support" className="appOwnedClass" />);
    expect(container.firstElementChild).toHaveClass("appOwnedClass");
    expect(container.firstElementChild?.className).toContain("choice");
  });

  it("carries no inline style attribute", () => {
    const { container } = render(<Radio label="Support" />);
    expect(container.firstElementChild?.hasAttribute("style")).toBe(false);
    expect(screen.getByRole("radio").hasAttribute("style")).toBe(false);
  });
});
