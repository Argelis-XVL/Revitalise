/**
 * The shell — landmarks, the signed-in line, and navigation between the two screens.
 */
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { App } from "./App";
import { makeRepository, makeUser, renderWithProviders } from "./test/harness";

describe("App", () => {
  it("provides a skip link and a main landmark for it to target", async () => {
    renderWithProviders(<App />, makeRepository());
    const skip = screen.getByRole("link", { name: /skip to the applications/i });
    expect(skip).toHaveAttribute("href", "#main");
    expect(document.querySelector("main")?.id).toBe("main");
    await waitFor(() => {
      expect(screen.getByRole("table")).toBeInTheDocument();
    });
  });

  it("shows one h1 on the list view", async () => {
    renderWithProviders(<App />, makeRepository());
    await waitFor(() => {
      expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    });
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
      "Applications under review",
    );
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

  it("opens a case and comes back to the list", async () => {
    renderWithProviders(<App />, makeRepository());
    await waitFor(() => {
      expect(screen.getByRole("table")).toBeInTheDocument();
    });
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
  });

  it("sets a distinct document title per view", async () => {
    renderWithProviders(<App />, makeRepository());
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
