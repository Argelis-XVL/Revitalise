/**
 * Decision capture end to end through the component tree — WBS 6.4, FR-037.
 *
 * The repository is a fake, so what is proven here is that the right slot's columns are
 * requested for the right user, and that every non-writable case offers no write path.
 */
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { VerdictSection } from "./VerdictSection";
import { VERDICT_NOTES_MAX_LENGTH, VERDICT_VALUES } from "../dataverse/schema";
import {
  makeRepository,
  makeReview,
  makeSummary,
  makeUser,
  OTHER_USER_ID,
  renderWithProviders,
  REVIEW_ID,
  TRUSTEE_2_ID,
} from "../test/harness";

const application = makeSummary();

describe("VerdictSection — writable", () => {
  it("saves the trustee-1 verdict and notes into the trustee-1 slot", async () => {
    const repository = makeRepository();
    renderWithProviders(
      <VerdictSection application={application} review={makeReview()} user={makeUser()} loading={false} />,
      repository,
    );

    expect(screen.getByText(/Trustee 1/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("radio", { name: "Approve" }));
    await userEvent.type(screen.getByLabelText(/notes/i), "Clear case.");
    await userEvent.click(screen.getByRole("button", { name: /save verdict/i }));

    await waitFor(() => {
      expect(repository.saved).toEqual([
        {
          reviewId: REVIEW_ID,
          slot: "trustee1",
          verdict: VERDICT_VALUES.approve,
          notes: "Clear case.",
        },
      ]);
    });
  });

  it("saves into the trustee-2 slot when the signed-in user is trustee 2", async () => {
    const repository = makeRepository();
    renderWithProviders(
      <VerdictSection
        application={application}
        review={makeReview()}
        user={makeUser({ systemUserId: TRUSTEE_2_ID })}
        loading={false}
      />,
      repository,
    );
    expect(screen.getByText(/Trustee 2/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("radio", { name: "Reject" }));
    await userEvent.click(screen.getByRole("button", { name: /save verdict/i }));
    await waitFor(() => {
      expect(repository.saved[0]?.slot).toBe("trustee2");
    });
  });

  it("pre-fills the verdict already recorded against the trustee's own slot", () => {
    renderWithProviders(
      <VerdictSection
        application={application}
        review={makeReview({ verdict1: VERDICT_VALUES.defer, notes1: "Wait for costs." })}
        user={makeUser()}
        loading={false}
      />,
      makeRepository(),
    );
    expect(screen.getByRole("radio", { name: "Defer" })).toBeChecked();
    expect(screen.getByLabelText(/notes/i)).toHaveValue("Wait for costs.");
  });

  it("does not pre-fill from the OTHER trustee's slot", () => {
    renderWithProviders(
      <VerdictSection
        application={application}
        review={makeReview({ verdict2: VERDICT_VALUES.reject, notes2: "Other trustee." })}
        user={makeUser()}
        loading={false}
      />,
      makeRepository(),
    );
    expect(screen.getByRole("radio", { name: "Reject" })).not.toBeChecked();
    expect(screen.getByLabelText(/notes/i)).toHaveValue("");
  });

  it("refuses to save with no verdict chosen, and says why in text", async () => {
    const repository = makeRepository();
    renderWithProviders(
      <VerdictSection application={application} review={makeReview()} user={makeUser()} loading={false} />,
      repository,
    );
    await userEvent.click(screen.getByRole("button", { name: /save verdict/i }));
    expect(repository.saved).toEqual([]);
    // Identified in text, not by colour (WCAG 3.3.1, 1.4.1).
    expect(screen.getAllByText(/choose approve, defer or reject/i).length).toBeGreaterThan(0);
  });

  it("states the notes limit and counts down as it is approached", async () => {
    renderWithProviders(
      <VerdictSection application={application} review={makeReview()} user={makeUser()} loading={false} />,
      makeRepository(),
    );
    expect(
      screen.getByText(new RegExp(`${String(VERDICT_NOTES_MAX_LENGTH)} characters remaining`)),
    ).toBeInTheDocument();
    await userEvent.type(screen.getByLabelText(/notes/i), "abc");
    expect(
      screen.getByText(new RegExp(`${String(VERDICT_NOTES_MAX_LENGTH - 3)} of`)),
    ).toBeInTheDocument();
  });

  it("keeps what was typed and reports the failure when the save fails", async () => {
    const repository = makeRepository({
      saveVerdict: () => Promise.reject(new Error("Dataverse said no.")),
    });
    renderWithProviders(
      <VerdictSection application={application} review={makeReview()} user={makeUser()} loading={false} />,
      repository,
    );
    await userEvent.click(screen.getByRole("radio", { name: "Approve" }));
    await userEvent.type(screen.getByLabelText(/notes/i), "Typed text.");
    await userEvent.click(screen.getByRole("button", { name: /save verdict/i }));

    await waitFor(() => {
      expect(screen.getByText(/could not save your verdict/i)).toBeInTheDocument();
    });
    expect(screen.getByText("Dataverse said no.")).toBeInTheDocument();
    // A failed save must not silently discard the trustee's work.
    expect(screen.getByLabelText(/notes/i)).toHaveValue("Typed text.");
  });
});

describe("VerdictSection — the four states with no write path", () => {
  it("offers nothing to click when no review row exists", () => {
    renderWithProviders(
      <VerdictSection application={application} review={null} user={makeUser()} loading={false} />,
      makeRepository(),
    );
    const note = screen.getByRole("note");
    expect(note).toHaveTextContent(/no review record/i);
    expect(screen.queryByRole("radio")).toBeNull();
    expect(screen.queryByRole("button", { name: /save verdict/i })).toBeNull();
  });

  it("is read-only for a user who is neither trustee", () => {
    renderWithProviders(
      <VerdictSection
        application={application}
        review={makeReview()}
        user={makeUser({ systemUserId: OTHER_USER_ID })}
        loading={false}
      />,
      makeRepository(),
    );
    expect(screen.getByRole("note")).toHaveTextContent(/not one of the two trustees/i);
    expect(screen.queryByRole("radio")).toBeNull();
  });

  it("is read-only and carries the reason when the identity could not be resolved", () => {
    renderWithProviders(
      <VerdictSection
        application={application}
        review={makeReview()}
        user={makeUser({ systemUserId: null, unresolvedReason: "No user record matches you." })}
        loading={false}
      />,
      makeRepository(),
    );
    const note = screen.getByRole("note");
    expect(note).toHaveTextContent("No user record matches you.");
    expect(screen.queryByRole("radio")).toBeNull();
  });

  it("shows a finalised round as read-only with the recorded verdict in words", () => {
    renderWithProviders(
      <VerdictSection
        application={application}
        review={makeReview({
          verdict1: VERDICT_VALUES.approve,
          notes1: "Agreed.",
          finalisedOn: "2026-10-02T09:00:00Z",
        })}
        user={makeUser()}
        loading={false}
      />,
      makeRepository(),
    );
    expect(screen.getByRole("note")).toHaveTextContent(/finalised/i);
    expect(screen.getByText("Approve")).toBeInTheDocument();
    expect(screen.getByText("Agreed.")).toBeInTheDocument();
    expect(screen.queryByRole("radio")).toBeNull();
  });

  it("shows a loading state rather than a premature read-only message", () => {
    renderWithProviders(
      <VerdictSection application={application} review={null} user={makeUser()} loading />,
      makeRepository(),
    );
    // Critical ordering: while the review row is still loading, `review === null` must
    // NOT be reported as "no review record exists".
    expect(screen.queryByRole("note")).toBeNull();
    expect(screen.getByText(/loading the review record/i)).toBeInTheDocument();
  });
});
