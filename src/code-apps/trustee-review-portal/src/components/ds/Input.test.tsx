/**
 * `ds/Input` — the converted design-system input (ADR-034).
 *
 * THE NO-WRAPPER-WITHOUT-LABEL BEHAVIOUR IS THE REASON THIS FILE MATTERS. The supplied
 * `Input.jsx:4-20` ALWAYS wraps its input in its own `<label>`. This app's filter controls pair
 * an external Fluent `<Label htmlFor>` with the input's `id`, and Fluent's `Label` and `Select`
 * both stay (§2.1.4). A second, nested `<label>` around an input an outer label already points
 * at breaks the label association (WCAG 1.3.1, 3.3.2): the browser resolves the innermost, so
 * the authored visible label silently stops being the accessible name. Nothing about that
 * failure is visible on screen, which is why it is asserted here.
 *
 * See `Button.test.tsx`'s header for what a class assertion here does and does not prove.
 */
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Input } from "./Input";

describe("ds/Input — with NO label prop, it renders a bare input", () => {
  it("renders no wrapping <label> element at all", () => {
    const { container } = render(<Input id="filter-reference" />);
    expect(container.querySelector("label")).toBeNull();
    expect(container.firstElementChild?.tagName).toBe("INPUT");
  });

  it("lets an EXTERNAL label own the association, which is the whole point", () => {
    // The shape ApplicationFilters.tsx uses: a Fluent <Label htmlFor> beside the control.
    render(
      <>
        {/* An external label pointing at the input by id — the case under test. */}
        <label htmlFor="filter-reference">Reference</label>
        <Input id="filter-reference" />
      </>,
    );
    // If ds/Input had wrapped itself in its own label, this accessible name would be wrong.
    expect(screen.getByLabelText("Reference")).toBe(screen.getByRole("textbox"));
  });

  it("treats an empty label string as no label", () => {
    const { container } = render(<Input label="" />);
    expect(container.querySelector("label")).toBeNull();
  });

  it("puts data-print on the input, because the input IS the outermost element", () => {
    render(<Input data-print="hide" />);
    expect(screen.getByRole("textbox")).toHaveAttribute("data-print", "hide");
  });
});

describe("ds/Input — with a label prop, the supplied wrapping behaviour is kept", () => {
  it("wraps the input in its own label and associates the two implicitly", () => {
    const { container } = render(<Input label="Search applications" />);
    expect(container.firstElementChild?.tagName).toBe("LABEL");
    expect(screen.getByLabelText("Search applications")).toBe(screen.getByRole("textbox"));
  });

  it("puts data-print on the LABEL, so the caption is hidden with the field", () => {
    // print.css hides by attribute. On the inner input it would hide the field and leave its
    // caption on the paper (§8.5 point 7).
    const { container } = render(<Input label="Search" data-print="hide" />);
    expect(container.firstElementChild).toHaveAttribute("data-print", "hide");
    expect(screen.getByRole("textbox")).not.toHaveAttribute("data-print");
  });

  it("marks a required field with a glyph, not with colour alone", () => {
    // WCAG 3.3.2. The programmatic signal a screen reader announces is the `required` attribute
    // on the input itself, which arrives through the spread.
    render(<Input label="Your email" required />);
    expect(screen.getByRole("textbox")).toBeRequired();
    expect(screen.getByText(/\*/)).toBeInTheDocument();
  });

  it("renders no marker when the field is not required", () => {
    render(<Input label="Your email" />);
    expect(screen.queryByText(/\*/)).toBeNull();
  });
});

describe("ds/Input — the forwarded attributes and the dropped outline", () => {
  it("defaults to type='text' and lets the caller override it", () => {
    const { unmount } = render(<Input />);
    expect(screen.getByRole("textbox")).toHaveAttribute("type", "text");
    unmount();
    render(<Input type="email" />);
    expect(screen.getByRole("textbox")).toHaveAttribute("type", "email");
  });

  it("forwards role (§8.5 point 6) to the input, which is the semantic control", () => {
    render(<Input role="searchbox" />);
    expect(screen.getByRole("searchbox")).toBeInTheDocument();
  });

  it("forwards aria-*, placeholder, value and onChange", async () => {
    const onChange = vi.fn();
    render(<Input aria-label="Reference" placeholder="REV-2026-" onChange={onChange} />);
    const field = screen.getByRole("textbox", { name: "Reference" });
    expect(field).toHaveAttribute("placeholder", "REV-2026-");
    await userEvent.type(field, "001");
    expect(onChange).toHaveBeenCalled();
  });

  it("forwards className alongside its own field class", () => {
    render(<Input className="appOwnedClass" />);
    const field = screen.getByRole("textbox");
    expect(field).toHaveClass("appOwnedClass");
    expect(field.className).toContain("inputField");
  });

  it("carries no inline style attribute — so nothing can outrank print.css", () => {
    const { container } = render(<Input label="Search" />);
    expect(container.firstElementChild?.hasAttribute("style")).toBe(false);
    expect(screen.getByRole("textbox").hasAttribute("style")).toBe(false);
  });
});
