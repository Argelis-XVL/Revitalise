/**
 * The group detail page (EF-43).
 *
 * The one assertion this file exists to make load-bearing: the circumstance-score /
 * "Current Circumstances" section an individual application's own detail page shows
 * (`CasePanels.tsx`'s `ScorePanel`, heading "Summary" as of Revision 14) is ABSENT here — the
 * plan's own settled decision (`docs/plans/emily-review-feedback-2026-09-plan.md` §4.3,
 * the 12-of-12 worked example). See `GroupDetailPage.tsx`'s header for why this is proved
 * by assertion rather than by "the component is never imported".
 */
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { GroupDetailPage } from "./GroupDetailPage";
import type { GroupSummary } from "../domain/groups";
import { makeRepository, makeReview, makeSummary, makeUser, renderWithProviders } from "../test/harness";

function group(overrides: Partial<GroupSummary> = {}): GroupSummary {
  return {
    code: "RA",
    memberCount: 2,
    totalRequested: 700,
    sharedStart: "2026-10-05T00:00:00Z",
    sharedEnd: "2026-10-12T00:00:00Z",
    members: [
      makeSummary({ id: "a", reference: "REV-2026-010", groupLinkage: "RA" }),
      makeSummary({ id: "b", reference: "REV-2026-011", groupLinkage: "RA" }),
    ],
    ...overrides,
  };
}

function renderPage(theGroup = group(), onOpenApplication = vi.fn()) {
  const repository = makeRepository();
  const result = renderWithProviders(
    <GroupDetailPage group={theGroup} user={makeUser()} onOpenApplication={onOpenApplication} />,
    repository,
  );
  return { onOpenApplication, ...result };
}

describe("GroupDetailPage", () => {
  it("titles the page with the group code", () => {
    renderPage();
    expect(screen.getByRole("heading", { level: 1, name: /group ra/i })).toBeInTheDocument();
  });

  it("renders the group's own fixed summary fields, and no cost field", () => {
    renderPage(group({ code: "RA", memberCount: 2, totalRequested: 700 }));
    expect(screen.getByText("Group code")).toBeInTheDocument();
    expect(screen.getByText("RA")).toBeInTheDocument();
    expect(screen.getByText("Members")).toBeInTheDocument();
    expect(screen.getByText("Group total requested")).toBeInTheDocument();
    expect(screen.getByText("£700.00")).toBeInTheDocument();
    expect(screen.getByText("Shared dates")).toBeInTheDocument();
    // Deliberately absent — see `domain/groups.ts`'s header on why no group cost figure
    // is invented.
    expect(screen.queryByText(/group total.*cost/i)).toBeNull();
  });

  it("lists the member applications with their normal summary fields", () => {
    renderPage();
    const table = screen.getByRole("table");
    expect(within(table).getByText("REV-2026-010")).toBeInTheDocument();
    expect(within(table).getByText("REV-2026-011")).toBeInTheDocument();
  });

  it("does NOT render the circumstance score / score breakdown section (settled: 12-of-12 worked example)", () => {
    renderPage();
    // `CasePanels.tsx`'s `ScorePanel` — heading "Summary" as of Revision 14 — must not
    // appear. Exact name match, so this does not collide with this page's OWN "Group summary"
    // panel heading below.
    expect(screen.queryByRole("heading", { name: "Summary" })).toBeNull();
    expect(screen.queryByText(/no score breakdown recorded/i)).toBeNull();
    expect(screen.queryByText(/current circumstances/i)).toBeNull();
  });

  it("opens a member's individual application detail page from the member table", async () => {
    const onOpenApplication = vi.fn();
    renderPage(group(), onOpenApplication);
    await userEvent.click(
      screen.getByRole("button", { name: /REV-2026-010, open the full case/i }),
    );
    expect(onOpenApplication).toHaveBeenCalledTimes(1);
    expect(onOpenApplication.mock.calls[0]?.[0]).toMatchObject({ reference: "REV-2026-010" });
  });

  it("still offers Record verdict on a member row, same as the flat list", async () => {
    renderPage();
    await userEvent.click(
      screen.getByRole("button", { name: /record verdict for REV-2026-010/i }),
    );
    const dialog = await screen.findByRole("dialog");
    expect(dialog).toHaveTextContent(/record a verdict for REV-2026-010/i);
  });

  it("sets the document title to the group", async () => {
    renderPage();
    await waitFor(() => {
      expect(document.title).toBe("Group RA — Trustee Review Portal");
    });
  });
});

describe("GroupDetailPage — the members table shows the trustee's own verdict (SDD A-14, FR-116; ADR-086)", () => {
  const M1 = "aaaaaaaa-0000-4000-8000-000000000001";
  const M2 = "aaaaaaaa-0000-4000-8000-000000000002";

  it("marks a member with the trustee's own verdict and leaves the awaiting one as Record verdict; the per-member button stays (EF-43)", async () => {
    const theGroup = group({
      members: [
        makeSummary({ id: M1, reference: "REV-2026-010", groupLinkage: "RA" }),
        makeSummary({ id: M2, reference: "REV-2026-011", groupLinkage: "RA" }),
      ],
    });
    const repository = makeRepository({
      listReviewsForApplications: () =>
        Promise.resolve([
          makeReview({ id: "11111111-0000-4000-8000-000000000001", applicationId: M1, verdict1: 2 }),
          makeReview({ id: "11111111-0000-4000-8000-000000000002", applicationId: M2, verdict2: 1 }),
        ]),
    });
    renderWithProviders(<GroupDetailPage group={theGroup} user={makeUser()} onOpenApplication={vi.fn()} />, repository);
    expect(await screen.findByRole("button", { name: /^Deferred — your verdict on REV-2026-010/ })).toHaveTextContent("Deferred");
    // M2: only the other trustee (slot 2) decided — still awaiting this trustee.
    expect(screen.getByRole("button", { name: "Record verdict for REV-2026-011" })).toBeInTheDocument();
  });
});

describe("GroupDetailPage — one verdict for the whole group (SDD A-14, FR-118, FR-119; ADR-087; WI-0148)", () => {
  const G1 = "cccccccc-0000-4000-8000-000000000001";
  const G2 = "cccccccc-0000-4000-8000-000000000002";
  const G3 = "cccccccc-0000-4000-8000-000000000003";
  const OUT = "cccccccc-0000-4000-8000-000000000009";

  /** A stateful fake: saves change what later reads return, so the result is visible on screen. */
  function setup() {
    const reviews = new Map([
      [G1, makeReview({ id: "dddddddd-0000-4000-8000-000000000001", applicationId: G1 })],
      [G2, makeReview({ id: "dddddddd-0000-4000-8000-000000000002", applicationId: G2 })],
      [G3, makeReview({ id: "dddddddd-0000-4000-8000-000000000003", applicationId: G3 })],
      [OUT, makeReview({ id: "dddddddd-0000-4000-8000-000000000009", applicationId: OUT })],
    ]);
    const byReviewId = (reviewId: string) => [...reviews.values()].find((r) => r.id === reviewId);
    const saved: { reviewId: string; slot: string; verdict: number; notes?: string }[] = [];
    let failFor: string | null = null;
    const repository = makeRepository({
      listReviewsForApplications: (ids) =>
        Promise.resolve(ids.map((applicationId) => reviews.get(applicationId)).filter((r) => r !== undefined)),
      getReviewForApplication: (applicationId) => Promise.resolve(reviews.get(applicationId) ?? null),
      saveVerdict: (input) => {
        if (input.reviewId === failFor) return Promise.reject(new Error("The service is unavailable."));
        saved.push({ ...input });
        const review = byReviewId(input.reviewId);
        if (review !== undefined) {
          const updated = input.slot === "trustee1" ? { ...review, verdict1: input.verdict } : { ...review, verdict2: input.verdict };
          if (input.notes !== undefined) {
            if (input.slot === "trustee1") updated.notes1 = input.notes;
            else updated.notes2 = input.notes;
          }
          reviews.set(review.applicationId as string, updated);
        }
        return Promise.resolve();
      },
    });
    const theGroup = group({
      code: "GP1",
      memberCount: 3,
      members: [
        makeSummary({ id: G1, reference: "REV-G-001", groupLinkage: "GP1" }),
        makeSummary({ id: G2, reference: "REV-G-002", groupLinkage: "GP1" }),
        makeSummary({ id: G3, reference: "REV-G-003", groupLinkage: "GP1" }),
      ],
    });
    renderWithProviders(<GroupDetailPage group={theGroup} user={makeUser()} onOpenApplication={vi.fn()} />, repository);
    return {
      saved,
      reviews,
      failOn: (reviewId: string) => {
        failFor = reviewId;
      },
    };
  }

  async function openGroupDialog() {
    const entry = await screen.findByRole("button", { name: "Record a verdict for the whole group" });
    await waitFor(() => {
      expect(entry).toBeEnabled();
    });
    await userEvent.click(entry);
    return screen.findByRole("dialog");
  }

  it("previews how many applications the verdict applies to, and Cancel writes nothing", async () => {
    const { saved } = setup();
    const dialog = await openGroupDialog();
    await userEvent.click(within(dialog).getByRole("radio", { name: "Approve" }));
    expect(within(dialog).getByText("Approve will be recorded on 3 of 3 applications.")).toBeInTheDocument();
    expect(within(dialog).getByRole("button", { name: "Record Approve on 3 applications" })).toBeEnabled();
    await userEvent.click(within(dialog).getByRole("button", { name: "Cancel" }));
    await waitFor(() => {
      expect(screen.queryByRole("dialog")).toBeNull();
    });
    expect(saved).toEqual([]);
  });

  it("blocks Defer without a note before ANY write (EF-05)", async () => {
    const { saved } = setup();
    const dialog = await openGroupDialog();
    await userEvent.click(within(dialog).getByRole("radio", { name: "Defer" }));
    await userEvent.click(within(dialog).getByRole("button", { name: "Record Defer on 3 applications" }));
    expect(await within(dialog).findByText("Notes are required when the verdict is Defer or Reject.")).toBeInTheDocument();
    expect(saved).toEqual([]);
  });

  it("records on every member of the group and no application outside it, with the same notes on each, and reports the result", async () => {
    const { saved } = setup();
    const dialog = await openGroupDialog();
    await userEvent.click(within(dialog).getByRole("radio", { name: "Reject" }));
    await userEvent.type(within(dialog).getByRole("textbox"), "Outside the criteria.");
    await userEvent.click(within(dialog).getByRole("button", { name: "Record Reject on 3 applications" }));
    expect(await within(dialog).findByText("3 recorded")).toBeInTheDocument();
    expect(saved.map((s) => s.reviewId).sort()).toEqual([
      "dddddddd-0000-4000-8000-000000000001",
      "dddddddd-0000-4000-8000-000000000002",
      "dddddddd-0000-4000-8000-000000000003",
    ]);
    expect(saved.every((s) => s.slot === "trustee1" && s.verdict === 3 && s.notes === "Outside the criteria.")).toBe(true);
    expect(within(dialog).getByText("REV-G-002: recorded")).toBeInTheDocument();
  });

  it("with one failing write shows which succeeded and which did not, and reports none recorded that was not", async () => {
    const { failOn } = setup();
    failOn("dddddddd-0000-4000-8000-000000000002");
    const dialog = await openGroupDialog();
    await userEvent.click(within(dialog).getByRole("radio", { name: "Approve" }));
    await userEvent.click(within(dialog).getByRole("button", { name: "Record Approve on 3 applications" }));
    expect(await within(dialog).findByText("2 recorded, 1 failed: REV-G-002")).toBeInTheDocument();
    expect(within(dialog).getByText("REV-G-002: failed — The service is unavailable.")).toBeInTheDocument();
    expect(within(dialog).queryByText("REV-G-002: recorded")).toBeNull();
  });

  it("shows the batched verdict on each member afterwards, and one member's own dialog still opens and can change it", async () => {
    setup();
    const dialog = await openGroupDialog();
    await userEvent.click(within(dialog).getByRole("radio", { name: "Approve" }));
    await userEvent.click(within(dialog).getByRole("button", { name: "Record Approve on 3 applications" }));
    await within(dialog).findByText("3 recorded");
    await userEvent.click(within(dialog).getByRole("button", { name: "Close" }));
    const member = await screen.findByRole("button", { name: /^Approved — your verdict on REV-G-001. Open to view or change it/ });
    await userEvent.click(member);
    const single = await screen.findByRole("dialog");
    await waitFor(() => {
      expect(within(single).getByRole("radio", { name: "Approve" })).toBeChecked();
    });
  });

  it("disables the group verdict, with the identity explanation, when the user cannot be identified", () => {
    renderWithProviders(
      <GroupDetailPage
        group={group()}
        user={makeUser({ systemUserId: null, unresolvedReason: "Your user record could not be matched." })}
        onOpenApplication={vi.fn()}
      />,
      makeRepository(),
    );
    const entry = screen.getByRole("button", { name: "Record a verdict for the whole group" });
    expect(entry).toBeDisabled();
    expect(entry).toHaveAccessibleDescription("Your user record could not be matched.");
  });
});
