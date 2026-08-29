/**
 * `ds/Card` — the converted design-system card (ADR-034).
 *
 * See `Button.test.tsx`'s header for what a class assertion here does and does not prove.
 */
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Card } from "./Card";

describe("ds/Card — the forwarded attributes", () => {
  it("forwards data-print (§8.5 point 7)", () => {
    const { container } = render(<Card data-print="block">Body.</Card>);
    expect(container.firstElementChild).toHaveAttribute("data-print", "block");
  });

  it("forwards role (§8.5 point 6)", () => {
    render(<Card role="note">Body.</Card>);
    expect(screen.getByRole("note")).toHaveTextContent("Body.");
  });

  it("forwards className and aria-labelledby alongside its own class", () => {
    const { container } = render(
      <Card className="appOwnedClass" aria-labelledby="heading-id">
        Body.
      </Card>,
    );
    expect(container.firstElementChild).toHaveClass("appOwnedClass");
    expect(container.firstElementChild).toHaveAttribute("aria-labelledby", "heading-id");
    expect(container.firstElementChild?.className).toContain("card");
  });
});

describe("ds/Card — the heading", () => {
  it("renders the title as an <h3>, the level the supplied component uses", () => {
    // A fixed level, so a card must sit under an <h2> for the hierarchy to stay logical
    // (WCAG 1.3.1, 2.4.6). In this app that is automatic: Panel IS the <section> + <h2>
    // landmark (Panel.tsx:22-25).
    render(<Card title="Round overview">Body.</Card>);
    expect(screen.getByRole("heading", { level: 3, name: "Round overview" })).toBeInTheDocument();
  });

  it("renders the title as text and NOT as a DOM title attribute", () => {
    const { container } = render(<Card title="Round overview">Body.</Card>);
    expect(container.firstElementChild).not.toHaveAttribute("title");
  });

  it("renders no heading when no title is given, or when it is empty", () => {
    const { unmount } = render(<Card>Body.</Card>);
    expect(screen.queryByRole("heading")).toBeNull();
    unmount();
    render(<Card title="">Body.</Card>);
    expect(screen.queryByRole("heading")).toBeNull();
  });
});

describe("ds/Card — the image is decorative by contract", () => {
  it("renders the image with an EMPTY alt, so a screen reader skips it", () => {
    // Exactly as `Card.jsx:6` has it. Correct for a decorative band and wrong for an image
    // carrying information — which this component has no way to express, deliberately (see the
    // component header: no `imageAlt` prop was invented ahead of a consumer).
    const { container } = render(<Card image="/band.png">Body.</Card>);
    const image = container.querySelector("img");
    expect(image).toHaveAttribute("src", "/band.png");
    expect(image).toHaveAttribute("alt", "");
    // An empty alt means it is not exposed as an image at all.
    expect(screen.queryByRole("img")).toBeNull();
  });

  it("renders no img element when no image is given, or when the url is empty", () => {
    const { container, unmount } = render(<Card>Body.</Card>);
    expect(container.querySelector("img")).toBeNull();
    unmount();
    const { container: empty } = render(<Card image="">Body.</Card>);
    expect(empty.querySelector("img")).toBeNull();
  });
});

describe("ds/Card — body and footer", () => {
  it("renders children in the body", () => {
    render(<Card>The round is open.</Card>);
    expect(screen.getByText("The round is open.")).toBeInTheDocument();
  });

  it("renders a footer when one is given", () => {
    render(<Card footer={<span>Figures as at 20 August 2026</span>}>Body.</Card>);
    expect(screen.getByText("Figures as at 20 August 2026")).toBeInTheDocument();
  });

  it("renders no footer element when none is given, or when it is null", () => {
    // The card body holds, in order: the optional heading, the text container, the optional
    // footer. With no title and no footer that is exactly one child — counted on the body
    // itself rather than with a `div > div` selector, which would also match the card root.
    const cardBody = (element: HTMLElement): Element | null =>
      element.firstElementChild?.lastElementChild ?? null;

    const { container, unmount } = render(<Card>Body.</Card>);
    expect(cardBody(container)?.children).toHaveLength(1);
    unmount();

    const { container: nulled, unmount: unmountNulled } = render(
      <Card footer={null}>Body.</Card>,
    );
    expect(cardBody(nulled)?.children).toHaveLength(1);
    unmountNulled();

    // And the positive case, so the count above is known to be sensitive to a footer at all.
    const { container: withFooter } = render(<Card footer={<i>f</i>}>Body.</Card>);
    expect(cardBody(withFooter)?.children).toHaveLength(2);
  });

  it("carries no inline style attribute", () => {
    const { container } = render(<Card title="A" image="/b.png" footer={<i>f</i>}>Body.</Card>);
    expect(container.firstElementChild?.hasAttribute("style")).toBe(false);
    expect(container.querySelector("img")?.hasAttribute("style")).toBe(false);
  });
});
