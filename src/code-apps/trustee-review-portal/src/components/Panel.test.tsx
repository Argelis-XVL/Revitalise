/**
 * The five semantic primitives, and the three properties Revision 4 could have silently
 * dropped while every other gate stayed green.
 *
 * WHY THIS FILE EXISTS NOW AND NOT BEFORE. Until Revision 4 these five components were
 * plain markup with a CSS class each, and they were exercised — thoroughly — through the
 * screens that render them. Revision 4 routes two of them through converted design-system
 * components (`StateMessage` through `ds/Notice`, `StatTileRow` through `ds/StatTile`), and
 * that introduces a class of regression the screen-level tests cannot see: a restyle that
 * keeps every word on the page and every role in the DOM while collapsing two visually
 * distinct states into one box, or typesetting an absence as a measurement. TAD §8.5 calls
 * that out as the risk of this whole pass — "a restyle that quietly removes one would leave
 * every gate green" — so the new properties get assertions of their own here.
 *
 * HOW THE TONE ASSERTIONS ARE WRITTEN, AND WHY NOT BY CLASS NAME. Vitest processes no CSS
 * (`vitest.config.ts` sets no `css` option), so a CSS-Module class arrives as an opaque
 * hashed string. These tests therefore assert RELATIONS between class attributes — that two
 * states differ, that a third equals one of them — rather than matching a literal like
 * `noticeMuted`. That is deliberate on two counts: it is the property §8.5 point 1 actually
 * states (the two states must not become one box), and it survives a rename inside
 * `components/ds`, which is a conversion of an external artefact and will be re-diffed
 * against it. A test that pinned the design system's internal class names would fail on a
 * re-supply that changed nothing about this app's behaviour — which is `IMP-0111` in the
 * other direction: a test that has to be rewritten when nothing broke is as much a defect as
 * one rewritten to make a break go green.
 */
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Definitions, MultilineText, Panel, StateMessage, StatTileRow } from "./Panel";
import { NOT_AVAILABLE, NOT_RECORDED } from "../domain/format";

/** The `class` attribute of the single `role="note"` currently rendered. */
function noteClass(): string {
  return screen.getByRole("note").getAttribute("class") ?? "";
}

describe("Panel — the landmark, unchanged by the restyle", () => {
  it("is a section labelled by its own h2, not a div with a bold line in it", () => {
    const { container } = render(
      <Panel heading="Financial eligibility">
        <p>Body</p>
      </Panel>,
    );
    const heading = screen.getByRole("heading", { level: 2, name: "Financial eligibility" });
    const section = container.querySelector("section");
    expect(section).not.toBeNull();
    // `aria-labelledby` pointing at the h2's own id is what makes this a landmark rather
    // than a div (WCAG 1.3.1). Asserted as the pairing, not as the presence of either half.
    expect(section?.getAttribute("aria-labelledby")).toBe(heading.id);
    expect(heading.id).not.toBe("");
  });

  it("keeps data-print='block', which is the only thing print.css can see", () => {
    // `print.css` targets `data-print` attributes and NEVER a class name, because CSS Module
    // class names are hashed at build time. That is exactly why the restyle is safe — and it
    // is only safe while the attribute is still there (§8.5 point 7).
    const { container } = render(
      <Panel heading="Holiday details">
        <p>Body</p>
      </Panel>,
    );
    expect(container.querySelector("section")).toHaveAttribute("data-print", "block");
  });
});

describe("StateMessage — role and print marker (§8.5 point 1, point 6)", () => {
  it("is a note by default, never an alert", () => {
    // An alert would interrupt a screen-reader trustee on EVERY navigation to tell them
    // something entirely expected. `Panel.tsx:35-37`'s reasoning, restated as a test.
    render(<StateMessage heading="Narrative withheld" explanation="Not released yet." />);
    expect(screen.getByRole("note")).toHaveTextContent("Narrative withheld");
    expect(screen.getByRole("note")).toHaveTextContent("Not released yet.");
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("lets the call site pass role='alert' for the one state that is a real failure", () => {
    // §8.5 point 6. `ds/Notice` sets no role at all, so the role has to be the call site's:
    // hardcoding `note` here would make the applications list's load failure a state no
    // screen reader is ever told about.
    render(<StateMessage heading="Could not load" explanation="Connector down." role="alert" />);
    expect(screen.getByRole("alert")).toHaveTextContent("Could not load");
    expect(screen.queryByRole("note")).toBeNull();
  });

  it("carries data-print='state' in both tones, so a withheld state prints as prominently as it displays", () => {
    // `print.css:58-63` gives this attribute a 1pt box and a 3pt left rule on paper. A
    // trustee working from the printed pack has to be able to see that a narrative was
    // WITHHELD rather than absent by accident.
    for (const tone of ["muted", "quiet"] as const) {
      const { unmount } = render(<StateMessage heading="H" explanation="E" tone={tone} />);
      expect(screen.getByRole("note")).toHaveAttribute("data-print", "state");
      unmount();
    }
  });
});

describe("StateMessage — the two tones stay visually distinct (§8.5 point 1)", () => {
  it("renders muted and quiet with different classes, and neither with none", () => {
    // THE PROPERTY THIS WHOLE FILE EXISTS FOR. "You may not see this" and "this has not been
    // scrubbed yet" are different facts about different causes, and rendering either as an
    // undifferentiated box tells a trustee something false about Art. 9 data.
    const { unmount } = render(<StateMessage heading="H" explanation="E" tone="muted" />);
    const muted = noteClass();
    unmount();

    render(<StateMessage heading="H" explanation="E" tone="quiet" />);
    const quiet = noteClass();

    expect(muted).not.toBe("");
    expect(quiet).not.toBe("");
    expect(muted).not.toBe(quiet);
  });

  it("defaults to the muted tone, so an unwired call site is the withheld treatment", () => {
    // The safer of the two to default to: `muted` is the filled panel the app has always
    // used for a withheld state, so a call site that forgets to pass a tone looks exactly
    // as it did before this pass rather than silently becoming the lighter treatment.
    const { unmount } = render(<StateMessage heading="H" explanation="E" tone="muted" />);
    const muted = noteClass();
    unmount();

    render(<StateMessage heading="H" explanation="E" />);
    expect(noteClass()).toBe(muted);
  });
});

describe("Definitions — the markup FR-078 depends on (§8.5 point 2)", () => {
  it("renders a real dl with one dt/dd pair per item, each dd its dt's next sibling", () => {
    const { container } = render(
      <Definitions
        items={[
          { label: "Income flag", value: "Within income ceiling" },
          { label: "Benefit status", value: "Protected by column-level security" },
        ]}
      />,
    );
    const list = container.querySelector("dl");
    expect(list).not.toBeNull();
    const terms = container.querySelectorAll("dt");
    const values = container.querySelectorAll("dd");
    expect(terms).toHaveLength(2);
    expect(values).toHaveLength(2);
    // The programmatic association is the ADJACENCY, not merely the presence of both
    // elements — `<dt>` followed by its own `<dd>` is what a screen reader announces as one
    // term/definition pair (WCAG 1.3.1).
    expect(terms[0]?.nextElementSibling).toBe(values[0]);
    expect(terms[1]?.nextElementSibling).toBe(values[1]);
  });

  it("REFUSES the supplied mockup's strong/span shape", () => {
    // `ui_kits/trustee-review-portal/ApplicationDetail.jsx:11-18` renders each field as
    // `<div><strong>label</strong><span>value</span></div>`, which is not a programmatic
    // label-value association at all — and it is exactly the property FR-078 rests on,
    // because a restricted catalogue row and a real value must read the same way to a screen
    // reader. The mockup's two-column measure and label weight are taken in CSS; its markup
    // is not, and this is the assertion that keeps it that way.
    const { container } = render(
      <Definitions items={[{ label: "Helper email", value: "Protected by column-level security" }]} />,
    );
    expect(container.querySelector("strong")).toBeNull();
    expect(container.querySelector("dl > div > dt")).not.toBeNull();
  });
});

describe("StatTileRow — an absence is not a measurement (§8.5 point 3)", () => {
  it("puts every tile inside one dl, as dt/dd pairs", () => {
    // `ds/StatTile` renders `<div><dt/><dd/></div>` and is only valid inside a `<dl>`. This
    // is the assertion that the `<dl>` survived the re-implementation: without it the pairs
    // are two orphaned elements and the term/definition association is gone.
    const { container } = render(
      <StatTileRow
        items={[
          { label: "People supported", value: "128" },
          { label: "Monthly disbursement", value: "£20,000.00" },
        ]}
      />,
    );
    expect(container.querySelectorAll("dl")).toHaveLength(1);
    expect(container.querySelectorAll("dl dt")).toHaveLength(2);
    expect(container.querySelectorAll("dl dd")).toHaveLength(2);
    expect(screen.getByText("People supported").closest("dt")).not.toBeNull();
    expect(screen.getByText("128").closest("dd")).not.toBeNull();
  });

  it("typesets 'Not recorded' differently from a real figure, with the words unchanged", () => {
    // The design system sets a tile's value in the display face at 32px, which would render
    // the literal "Not recorded" as a 32px display figure — READING AS A VALUE where an
    // absence is meant. `formatAmount`/`formatCount` return these words rather than a zero
    // because "on this screen a zero is a finding and an absence is an absence"
    // (`domain/format.ts`). The words are what a trustee reads and they do not change; only
    // the typography's claim to being a measurement is withdrawn.
    render(
      <StatTileRow
        items={[
          { label: "Committed or spent to date", value: "£41,000.00" },
          { label: "Remaining legacy fund (charity-wide)", value: NOT_RECORDED },
        ]}
      />,
    );
    const figure = screen.getByText("£41,000.00");
    const absence = screen.getByText(NOT_RECORDED);
    expect(figure.tagName).toBe("DD");
    expect(absence.tagName).toBe("DD");
    expect(figure.getAttribute("class")).not.toBe("");
    expect(absence.getAttribute("class")).not.toBe("");
    expect(absence.getAttribute("class")).not.toBe(figure.getAttribute("class"));
  });

  it("treats 'Not available' as an absence too — the other half of format.ts's vocabulary", () => {
    // `NOT_RECORDED` and `NOT_AVAILABLE` are not interchangeable to a reader (one is "nobody
    // entered it", the other is "the portal could not read it") and `format.ts` is explicit
    // about that. They ARE the same fact typographically: neither is a figure.
    const { unmount } = render(<StatTileRow items={[{ label: "A", value: NOT_RECORDED }]} />);
    const recorded = screen.getByText(NOT_RECORDED).getAttribute("class");
    unmount();

    render(<StatTileRow items={[{ label: "A", value: NOT_AVAILABLE }]} />);
    expect(screen.getByText(NOT_AVAILABLE).getAttribute("class")).toBe(recorded);
  });

  it("does not mistake a real figure for an absence", () => {
    // The guard on the other side: the absence test is a comparison against `format.ts`'s
    // own two constants, so nothing a formatter actually produces for a real number can trip
    // it. A zero especially must not — on this screen a zero is a finding.
    const { unmount } = render(<StatTileRow items={[{ label: "A", value: NOT_RECORDED }]} />);
    const absent = screen.getByText(NOT_RECORDED).getAttribute("class");
    unmount();

    render(
      <StatTileRow
        items={[
          { label: "A", value: "0" },
          { label: "B", value: "£0.00" },
          { label: "C", value: "Not scored" },
        ]}
      />,
    );
    for (const value of ["0", "£0.00", "Not scored"]) {
      expect(screen.getByText(value).getAttribute("class"), value).not.toBe(absent);
    }
  });
});

describe("MultilineText", () => {
  it("keeps authored line breaks rather than collapsing them", () => {
    const { container } = render(<MultilineText text={"Wellbeing 20\nCare hours 12"} />);
    const paragraph = container.querySelector("p");
    expect(paragraph).not.toBeNull();
    // The line break is preserved in the TEXT, and `.preserveLines`' `white-space: pre-wrap`
    // is what renders it. jsdom computes no CSS, so this asserts the half that is this
    // component's: the string reaches the DOM intact.
    expect(paragraph?.textContent).toBe("Wellbeing 20\nCare hours 12");
  });
});
