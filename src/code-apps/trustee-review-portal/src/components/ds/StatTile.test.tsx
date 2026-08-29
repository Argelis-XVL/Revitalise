/**
 * `ds/StatTile` — the converted design-system stat tile (ADR-034).
 *
 * TWO PROPERTIES THIS FILE EXISTS TO PIN (§8.5 point 3):
 *
 *   1. THE `<dt>`/`<dd>` PAIR. `StatTileRow` is re-implemented over this component and keeps its
 *      `<dl>`, because a `<dl>` of `<dt>`/`<dd>` pairs is a programmatic term/definition
 *      association and the supplied mockup's `<div><strong>label</strong><span>value</span></div>`
 *      is not one at all (WCAG 1.3.1). If this component rendered a bare `<div>` pair, the
 *      property would be gone and every existing test would stay green.
 *   2. THE `absent` STATE. `RoundStatistics.tsx:10-13`: "a `null` metric renders as nothing at
 *      all. Not a zero, not an error, and not a heading with an empty body", and
 *      `format.ts:99-113` renders a null as WORDS because "on this screen a zero is a finding
 *      and an absence is an absence". The supplied component sets the value at 32px in the
 *      display face, which would make "Not recorded" read as a measurement.
 *
 * See `Button.test.tsx`'s header for what a class assertion here does and does not prove.
 */
import { render, screen } from "@testing-library/react";
import type { ReactElement } from "react";
import { describe, expect, it } from "vitest";
import { StatTile } from "./StatTile";

/** The element the component is designed to sit inside, as `StatTileRow` will render it. */
function renderInList(tile: ReactElement) {
  return render(<dl>{tile}</dl>);
}

describe("ds/StatTile — the definition-list markup that FR-078 and §8.5 depend on", () => {
  it("renders the label as a <dt> and the value as a <dd>", () => {
    const { container } = renderInList(<StatTile label="Amount committed" value="41,000" />);
    const term = container.querySelector("dt");
    const definition = container.querySelector("dd");
    expect(term).toHaveTextContent("Amount committed");
    expect(definition).toHaveTextContent("41,000");
  });

  it("wraps the pair in a div, so it is a valid group inside a <dl>", () => {
    // Panel.tsx:74 already records that a <dl> permits each group wrapped in a <div>.
    const { container } = renderInList(<StatTile label="People supported" value="128" />);
    const group = container.querySelector("dl > div");
    expect(group).not.toBeNull();
    expect(group?.querySelector("dt")).not.toBeNull();
    expect(group?.querySelector("dd")).not.toBeNull();
  });
});

describe("ds/StatTile — the absent state (§8.5 point 3)", () => {
  it("renders the same words, but not as a 32px display figure", () => {
    // The words are unchanged; only their typographic claim to being a measurement is
    // withdrawn. Both halves asserted, because "renders differently" alone would be satisfied
    // by dropping the text.
    const { container: normal, unmount } = renderInList(
      <StatTile label="Applications per day" value="14.47" />,
    );
    const asFigure = normal.querySelector("dd")?.className ?? "";
    unmount();

    const { container: absent } = renderInList(
      <StatTile label="Applications per day" value="Not recorded" absent />,
    );
    const asAbsence = absent.querySelector("dd");

    expect(asAbsence).toHaveTextContent("Not recorded");
    expect(asAbsence?.className).not.toBe(asFigure);
    expect(asFigure).toContain("statTileValue");
    expect(asAbsence?.className).toContain("statTileValueAbsent");
  });

  it("defaults to the figure treatment when absent is not passed", () => {
    const { container } = renderInList(<StatTile label="Grant capacity" value="250,000" />);
    expect(container.querySelector("dd")?.className).toContain("statTileValue");
    expect(container.querySelector("dd")?.className).not.toContain("statTileValueAbsent");
  });

  it("keeps the label in the same treatment either way — the name is not the absent part", () => {
    // A metric's name is not decoration (§8.5 point 3), and it does not become less identifiable
    // because its value is missing.
    const { container: a, unmount } = renderInList(<StatTile label="Same" value="1" />);
    const labelled = a.querySelector("dt")?.className;
    unmount();
    const { container: b } = renderInList(<StatTile label="Same" value="Not recorded" absent />);
    expect(b.querySelector("dt")?.className).toBe(labelled);
  });
});

describe("ds/StatTile — the forwarded attributes", () => {
  it("forwards data-print (§8.5 point 7)", () => {
    const { container } = renderInList(
      <StatTile label="Monthly disbursement" value="20,000" data-print="block" />,
    );
    expect(container.querySelector("dl > div")).toHaveAttribute("data-print", "block");
  });

  it("forwards role (§8.5 point 6)", () => {
    renderInList(<StatTile label="Remaining legacy fund" value="175,000" role="note" />);
    expect(screen.getByRole("note")).toHaveTextContent("175,000");
  });

  it("forwards className alongside its own tile class", () => {
    const { container } = renderInList(
      <StatTile label="A" value="1" className="appOwnedClass" />,
    );
    const group = container.querySelector("dl > div");
    expect(group).toHaveClass("appOwnedClass");
    expect(group?.className).toContain("statTile");
  });
});

describe("ds/StatTile — the sublabel", () => {
  it("renders a sublabel inside the term when one is given", () => {
    const { container } = renderInList(
      <StatTile label="Figures as at" value="20 August 2026" sublabel="hand-maintained" />,
    );
    expect(container.querySelector("dt")).toHaveTextContent("hand-maintained");
  });

  it("renders no sublabel element when it is absent or empty", () => {
    const { container, unmount } = renderInList(<StatTile label="A" value="1" />);
    expect(container.querySelector("dt")?.children).toHaveLength(0);
    unmount();
    const { container: empty } = renderInList(<StatTile label="A" value="1" sublabel="" />);
    expect(empty.querySelector("dt")?.children).toHaveLength(0);
  });

  it("carries no inline style attribute", () => {
    const { container } = renderInList(<StatTile label="A" value="1" />);
    expect(container.querySelector("dl > div")?.hasAttribute("style")).toBe(false);
  });
});
