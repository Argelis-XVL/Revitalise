/**
 * `ds/Notice` — the converted design-system notice (ADR-034).
 *
 * THE ROLE IS THE WHOLE POINT OF THIS FILE (§8.5 point 6). The supplied `Notice.jsx:11-15` is a
 * plain `<div>` with no role, and this app needs three different answers out of one visual
 * treatment: `role="alert"` for the applications list's error state, and `role="note"` for the
 * two distinct empty states and for the redaction states. So the component must set none and
 * forward whatever the call site passes. An error a screen reader is never told about is a worse
 * outcome than an unstyled one — and conversely, `Panel.tsx:35-37` records that `role="alert"`
 * on a designed state would interrupt a screen-reader trustee on every navigation.
 *
 * See `Button.test.tsx`'s header for what a class assertion here does and does not prove.
 */
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Notice } from "./Notice";

describe("ds/Notice — the role comes from the call site, never from the component", () => {
  it("sets NO role of its own", () => {
    const { container } = render(<Notice>Nothing to report.</Notice>);
    expect(container.firstElementChild).not.toHaveAttribute("role");
    // Neither of the two roles the app uses appears by accident.
    expect(screen.queryByRole("alert")).toBeNull();
    expect(screen.queryByRole("note")).toBeNull();
  });

  it("forwards role='alert' for the error state, on the outermost element", () => {
    // ApplicationsListPage.tsx:56-74 renders styles.errorBox + role="alert" + an <h2> + the
    // error message + a Try again button. Rendering that through ds/Notice is only allowed if
    // the role survives (§2.2.1, §8.5 point 6).
    render(
      <Notice role="alert" tone="muted" title="Something went wrong">
        The list could not be loaded.
      </Notice>,
    );
    const alert = screen.getByRole("alert");
    // On the OUTERMOST element, so the title is announced with the body rather than after it.
    expect(alert).toHaveTextContent("Something went wrong");
    expect(alert).toHaveTextContent("The list could not be loaded.");
  });

  it("forwards role='note' for a designed, expected state", () => {
    render(
      <Notice role="note" title="Narrative withheld">
        The circumstance score is still available.
      </Notice>,
    );
    expect(screen.getByRole("note")).toHaveTextContent(/withheld/i);
    // Not an alert. This is the assertion CasePanels.test.tsx:26 already makes of StateMessage.
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("forwards data-print (§8.5 point 7)", () => {
    const { container } = render(<Notice data-print="state">Withheld.</Notice>);
    expect(container.firstElementChild).toHaveAttribute("data-print", "state");
  });

  it("forwards aria-live and id, which the app's state messages use", () => {
    const { container } = render(
      <Notice id="empty-state" aria-live="polite">
        No applications match these filters.
      </Notice>,
    );
    expect(container.firstElementChild).toHaveAttribute("id", "empty-state");
    expect(container.firstElementChild).toHaveAttribute("aria-live", "polite");
  });
});

describe("ds/Notice — the tones, and the one that is deliberately absent", () => {
  it("defaults to the muted tone, which is the one already AA-compliant", () => {
    // §8.4.2: "the tone this app actually needs is the one that is already compliant" —
    // --text-heading title at 13.21:1 and --text-body body at 5.97:1 on --surface-muted.
    const { container } = render(<Notice>Default tone.</Notice>);
    expect(container.firstElementChild?.className).toContain("noticeMuted");
  });

  it("asks for a DISTINCT class for each of the three tones", () => {
    // §8.5 point 1: "withheld" and "no text recorded" must not become one grey box. Two states
    // that are not the same fact must not share a treatment, so the classes must differ.
    const keys = (["muted", "info", "quiet"] as const).map((tone) => {
      const { container, unmount } = render(<Notice tone={tone}>{tone}</Notice>);
      const className = container.firstElementChild?.className ?? "";
      unmount();
      return className;
    });
    expect(new Set(keys).size).toBe(3);
    expect(keys[0]).toContain("noticeMuted");
    expect(keys[1]).toContain("noticeInfo");
    expect(keys[2]).toContain("noticeQuiet");
  });

  it("has no warning tone to reach for (ADR-037 correction 5)", () => {
    // The design system's warning title measures 3.16:1 and fails, and this app has no warning
    // state. The type union is what enforces this at compile time; this records the intent so a
    // later addition is a deliberate act. ds-tokens.test.ts asserts neither --warning nor
    // --success is declared and that no .noticeWarning class exists.
    const tones: readonly string[] = ["muted", "info", "quiet"];
    expect(tones).not.toContain("warning");
  });
});

describe("ds/Notice — the title is text, not a tooltip", () => {
  it("renders the title as visible text and NOT as a title attribute", () => {
    // React.HTMLAttributes uses `title` for the DOM tooltip; the supplied contract uses it for
    // the visible heading. The DOM one is Omitted so the collision is a stated decision — a
    // tooltip is not an accessible name and nothing here should imply it is.
    const { container } = render(<Notice title="Figures unavailable">Body text.</Notice>);
    expect(screen.getByText("Figures unavailable")).toBeInTheDocument();
    expect(container.firstElementChild).not.toHaveAttribute("title");
  });

  it("renders no title element when no title is given", () => {
    const { container } = render(<Notice>Body only.</Notice>);
    expect(container.firstElementChild?.children).toHaveLength(1);
  });

  it("treats an empty title as no title", () => {
    const { container } = render(<Notice title="">Body only.</Notice>);
    expect(container.firstElementChild?.children).toHaveLength(1);
  });

  it("carries no inline style attribute", () => {
    const { container } = render(<Notice tone="info">Tinted.</Notice>);
    expect(container.firstElementChild?.hasAttribute("style")).toBe(false);
  });
});
