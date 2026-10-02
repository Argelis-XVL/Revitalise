/**
 * `ds/Checkbox` — the converted design-system checkbox (ADR-034).
 *
 * No consumer exists in the app today; it is converted because it is one of the seven components
 * ADR-033 adopts. See `Button.test.tsx`'s header for what a class assertion here does and does
 * not prove.
 */
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Checkbox } from "./Checkbox";

describe("ds/Checkbox", () => {
  it("renders a checkbox with its label programmatically associated", () => {
    // The control sits inside its own <label> — an implicit and correct association
    // (WCAG 1.3.1, 3.3.2).
    render(<Checkbox label="Eligible for this round" />);
    const control = screen.getByRole("checkbox", { name: "Eligible for this round" });
    expect(control).toHaveAttribute("type", "checkbox");
    expect(screen.getByLabelText("Eligible for this round")).toBe(control);
  });

  it("cannot be configured into a different control type", () => {
    // `type` is Omitted from the props — see Radio.test.tsx for the same decision.
    render(<Checkbox label="Eligible" />);
    expect(screen.getByRole("checkbox", { name: "Eligible" })).toHaveAttribute(
      "type",
      "checkbox",
    );
    expect(screen.queryByRole("radio")).toBeNull();
  });

  it("puts data-print on the label, so the caption is hidden with the control", () => {
    const { container } = render(<Checkbox label="Eligible" data-print="hide" />);
    expect(container.firstElementChild?.tagName).toBe("LABEL");
    expect(container.firstElementChild).toHaveAttribute("data-print", "hide");
  });

  it("forwards role (§8.5 point 6) to the input, which is the semantic control", () => {
    render(<Checkbox label="Eligible" role="menuitemcheckbox" />);
    expect(screen.getByRole("menuitemcheckbox", { name: "Eligible" })).toBeInTheDocument();
  });

  it("toggles through onChange and reflects the checked state it is given", async () => {
    const onChange = vi.fn();
    const { unmount } = render(<Checkbox label="Eligible" onChange={onChange} />);
    const control = screen.getByRole("checkbox", { name: "Eligible" });
    expect(control).not.toBeChecked();
    await userEvent.click(control);
    expect(onChange).toHaveBeenCalledTimes(1);
    unmount();

    render(<Checkbox label="Eligible" checked readOnly />);
    expect(screen.getByRole("checkbox", { name: "Eligible" })).toBeChecked();
  });

  it("forwards disabled and className", () => {
    const { container } = render(
      <Checkbox label="Eligible" disabled className="appOwnedClass" />,
    );
    expect(screen.getByRole("checkbox", { name: "Eligible" })).toBeDisabled();
    expect(container.firstElementChild).toHaveClass("appOwnedClass");
    expect(container.firstElementChild?.className).toContain("choice");
  });

  it("carries no inline style attribute", () => {
    const { container } = render(<Checkbox label="Eligible" />);
    expect(container.firstElementChild?.hasAttribute("style")).toBe(false);
    expect(screen.getByRole("checkbox").hasAttribute("style")).toBe(false);
  });
});
