/**
 * The shell — landmarks, the signed-in line, and navigation across the three screens.
 *
 * FR-056 changed the entry state: the app opens on the LANDING screen, not on the case
 * list. Every test below that used to start on the list now navigates there first, which
 * is the assertion FR-056 actually needs — "trustees have a clear starting point instead of
 * landing directly inside case data" is only true if the first paint is not the case data.
 */
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { App } from "./App";
import { makeRepository, makeUser, renderWithProviders } from "./test/harness";

/** FR-056's first hop: landing -> list. */
async function openTheList(): Promise<void> {
  await userEvent.click(
    await screen.findByRole("button", { name: /open the applications list/i }),
  );
  await waitFor(() => {
    expect(screen.getByRole("table")).toBeInTheDocument();
  });
}

describe("App", () => {
  it("opens on the landing screen, not inside case data (FR-056)", async () => {
    renderWithProviders(<App />, makeRepository());
    expect(
      await screen.findByRole("heading", { level: 1, name: /round overview/i }),
    ).toBeInTheDocument();
    // The point of FR-056: no case list on the first paint.
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("provides a skip link and a main landmark for it to target", async () => {
    renderWithProviders(<App />, makeRepository());
    const skip = screen.getByRole("link", { name: /skip to the applications/i });
    expect(skip).toHaveAttribute("href", "#main");
    expect(document.querySelector("main")?.id).toBe("main");
    await openTheList();
  });

  it("shows one h1 on the landing screen and one on the list", async () => {
    renderWithProviders(<App />, makeRepository());
    await waitFor(() => {
      expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    });
    await openTheList();
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
      "Applications under review",
    );
  });

  it("brands every view with the charity's logo, named rather than decorative", async () => {
    // NFR-026. The logo lives in the shell header, so one placement covers all three views;
    // `alt` is the organisation's name because this identifies the charity whose money the
    // round distributes, which is content, not decoration (WCAG 1.1.1). An `alt=""` here
    // would leave a screen-reader user with no idea whose portal they are in.
    renderWithProviders(<App />, makeRepository());
    const logo = screen.getByRole("img", { name: /revitalise/i });
    expect(logo).toBeInTheDocument();
    await openTheList();
    expect(screen.getByRole("img", { name: /revitalise/i })).toBeInTheDocument();
  });

  it("names the signed-in trustee", async () => {
    renderWithProviders(<App />, makeRepository());
    expect(await screen.findByText(/signed in as kevin trustee/i)).toBeInTheDocument();
  });

  it("says so when the host did not give a name", async () => {
    renderWithProviders(
      <App />,
      makeRepository({ getCurrentUser: () => Promise.resolve(makeUser({ fullName: null })) }),
    );
    expect(await screen.findByText(/your name was not available/i)).toBeInTheDocument();
  });

  it("explains that cases are still readable when the trustee record is unconfirmed", async () => {
    renderWithProviders(
      <App />,
      makeRepository({
        getCurrentUser: () =>
          Promise.resolve(
            makeUser({ systemUserId: null, unresolvedReason: "No user record matches you." }),
          ),
      }),
    );
    // waitFor, not findByRole: the note is present from the first paint carrying an
    // interim "still working out who you are" reason, so finding a note proves nothing.
    // The assertion is on the RESOLVED reason.
    await waitFor(() => {
      expect(screen.getByRole("note")).toHaveTextContent("No user record matches you.");
    });
    const note = screen.getByRole("note");
    expect(note).toHaveTextContent(/read cases, but not record a verdict/i);
    // The point of the message: it must not read as a lockout.
    expect(note).toHaveTextContent(/still readable/i);
  });

  it("reports a failed identity query as a reason rather than as a blank line", async () => {
    renderWithProviders(
      <App />,
      makeRepository({ getCurrentUser: () => Promise.reject(new Error("Identity query broke.")) }),
    );
    await waitFor(() => {
      expect(screen.getByRole("note")).toHaveTextContent("Identity query broke.");
    });
  });

  it("walks the whole FR-056 chain: landing to list to case and back again", async () => {
    renderWithProviders(<App />, makeRepository());
    await openTheList();

    await userEvent.click(
      screen.getByRole("button", { name: /REV-2026-001, open the full case/i }),
    );
    await waitFor(() => {
      expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
        "Application REV-2026-001",
      );
    });
    // The list's h1 is replaced, not duplicated — one h1 per view (WCAG 2.4.6).
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);

    await userEvent.click(screen.getByRole("button", { name: /back to the list/i }));
    await waitFor(() => {
      expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
        "Applications under review",
      );
    });

    // And back up to the landing screen — without this the list is a dead end and the
    // round's figures are unreachable without reloading the app.
    await userEvent.click(screen.getByRole("button", { name: /back to the round overview/i }));
    await waitFor(() => {
      expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Round overview");
    });
  });

  it("sets a distinct document title per view", async () => {
    renderWithProviders(<App />, makeRepository());
    // The landing title names the round, so two rounds are distinguishable in a browser
    // history or a printed header (WCAG 2.4.2).
    await waitFor(() => {
      expect(document.title).toBe("Round overview — 2026-Q4 — Trustee Review Portal");
    });
    await openTheList();
    await waitFor(() => {
      expect(document.title).toBe("Applications under review — Trustee Review Portal");
    });
    await userEvent.click(
      await screen.findByRole("button", { name: /REV-2026-001, open the full case/i }),
    );
    await waitFor(() => {
      expect(document.title).toBe("Application REV-2026-001 — Trustee Review Portal");
    });
  });
});
