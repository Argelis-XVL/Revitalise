/**
 * The group verdict planner and executor — portal TAD trustee-portal-design-2 ADR-087 (SDD A-14,
 * FR-118, FR-119; US-012 AC-12; WI-0148). Test contract: TAD §14.4 row AC-12.
 */
import { describe, expect, it, vi } from "vitest";
import {
  NOT_CONFIRMED_REASON,
  confirmLabel,
  executeGroupVerdict,
  groupNotesProblem,
  notesToSend,
  planGroupVerdict,
  previewSentence,
  replanForConfirm,
  resultSentence,
} from "./groupVerdict";
import { VERDICT_NOTES_MAX_LENGTH, VERDICT_VALUES } from "../dataverse/schema";
import type { SaveVerdictInput } from "../dataverse/types";
import { TRUSTEE_1_ID, TRUSTEE_2_ID, makeReview, makeSummary, makeUser } from "../test/harness";

const OTHER = "99999999-9999-4999-8999-999999999999";
const id = (n: number) => `aaaaaaaa-0000-4000-8000-00000000000${String(n)}`;
const rid = (n: number) => `bbbbbbbb-0000-4000-8000-00000000000${String(n)}`;

const M = [1, 2, 3, 4].map((n) => makeSummary({ id: id(n), reference: `REV-A-0000${String(n)}`, groupLinkage: "GP1" }));
/** An application OUTSIDE the group, with a writable review — must never be written. */
const OUTSIDE = makeSummary({ id: id(9), reference: "REV-A-00009", groupLinkage: "GP2" });

const user = makeUser({ systemUserId: TRUSTEE_1_ID });

function rows() {
  return [
    // 1: trustee 1 slot (writable)
    makeReview({ id: rid(1), applicationId: id(1), trustee1Id: TRUSTEE_1_ID, trustee2Id: TRUSTEE_2_ID }),
    // 2: the same trustee is trustee 2 here (writable, slot 2)
    makeReview({ id: rid(2), applicationId: id(2), trustee1Id: TRUSTEE_2_ID, trustee2Id: TRUSTEE_1_ID }),
    // 3: not one of the two trustees
    makeReview({ id: rid(3), applicationId: id(3), trustee1Id: OTHER, trustee2Id: TRUSTEE_2_ID }),
    // 4: no review row at all
    makeReview({ id: rid(9), applicationId: id(9) }),
  ];
}

describe("planGroupVerdict — the preview", () => {
  it("targets each writable member in ITS OWN slot, and skips with the three reasons", () => {
    const finalisedRows = [
      ...rows(),
      makeReview({ id: rid(5), applicationId: id(5), finalisedOn: "2026-10-20T00:00:00Z" }),
    ];
    const members = [...M, makeSummary({ id: id(5), reference: "REV-A-00005" })];
    const plan = planGroupVerdict(members, finalisedRows, user);
    expect(plan.targets.map((t) => [t.application.reference, t.reviewId, t.slot])).toEqual([
      ["REV-A-00001", rid(1), "trustee1"],
      ["REV-A-00002", rid(2), "trustee2"],
    ]);
    expect(plan.skipped.map((s) => s.reason)).toEqual([
      "you are not one of the two trustees on REV-A-00003",
      "there is no review record for REV-A-00004 yet",
      "the round for REV-A-00005 has been finalised",
    ]);
  });

  it("states what will happen before anything is written", () => {
    const plan = planGroupVerdict(M, rows(), user);
    expect(previewSentence(plan, VERDICT_VALUES.approve)).toBe(
      "Approve will be recorded on 2 of 4 applications. 2 skipped: you are not one of the two trustees on REV-A-00003; there is no review record for REV-A-00004 yet.",
    );
    expect(confirmLabel(plan, VERDICT_VALUES.approve)).toBe("Record Approve on 2 applications");
    expect(confirmLabel(planGroupVerdict(M.slice(0, 1), rows(), user), VERDICT_VALUES.reject)).toBe(
      "Record Reject on 1 application",
    );
  });
});

describe("replanForConfirm — the fresh read at confirm (ADR-087 point 4)", () => {
  it("drops a member finalised since the preview, with its new reason", () => {
    const preview = planGroupVerdict(M, rows(), user);
    const fresh = rows().map((row) => (row.id === rid(2) ? { ...row, finalisedOn: "2026-10-22T10:00:00Z" } : row));
    const plan = replanForConfirm(preview, M, fresh, user);
    expect(plan.targets.map((t) => t.application.reference)).toEqual(["REV-A-00001"]);
    expect(plan.skipped.find((s) => s.application.id === id(2))?.reason).toBe(
      "the round for REV-A-00002 has been finalised",
    );
  });

  it("does NOT add a member that became writable after the preview, and says why", () => {
    const preview = planGroupVerdict(M, rows(), user);
    const fresh = [...rows(), makeReview({ id: rid(4), applicationId: id(4) })];
    const plan = replanForConfirm(preview, M, fresh, user);
    expect(plan.targets.map((t) => t.application.reference)).toEqual(["REV-A-00001", "REV-A-00002"]);
    expect(plan.skipped.find((s) => s.application.id === id(4))?.reason).toBe(NOT_CONFIRMED_REASON);
  });
});

describe("executeGroupVerdict — one ordinary save per member, one at a time (ADR-087 point 5)", () => {
  it("writes each member's own slot, never a member outside the group, and the other trustee's column never", async () => {
    const saved: SaveVerdictInput[] = [];
    const plan = planGroupVerdict(M, rows(), user);
    await executeGroupVerdict(M, plan, VERDICT_VALUES.approve, undefined, (input) => {
      saved.push(input);
      return Promise.resolve();
    });
    expect(saved).toEqual([
      { reviewId: rid(1), slot: "trustee1", verdict: VERDICT_VALUES.approve },
      { reviewId: rid(2), slot: "trustee2", verdict: VERDICT_VALUES.approve },
    ]);
    expect(saved.some((input) => input.reviewId === rid(9))).toBe(false);
    expect(OUTSIDE.groupLinkage).not.toBe("GP1");
  });

  it("with one failing write: 2 recorded, 1 failed, 1 skipped — and the failed one is not reported recorded", async () => {
    const members = [...M.slice(0, 2), makeSummary({ id: id(6), reference: "REV-A-00006" }), M[2]!];
    const rowsWithSix = [...rows(), makeReview({ id: rid(6), applicationId: id(6) })];
    const plan = planGroupVerdict(members, rowsWithSix, user);
    expect(plan.targets).toHaveLength(3);
    const save = vi.fn((input: SaveVerdictInput) =>
      input.reviewId === rid(2) ? Promise.reject(new Error("Network down")) : Promise.resolve(),
    );
    const outcomes = await executeGroupVerdict(members, plan, VERDICT_VALUES.reject, "Not enough evidence.", save);
    expect(save).toHaveBeenCalledTimes(3);
    expect(outcomes.map((o) => [o.application.reference, o.kind])).toEqual([
      ["REV-A-00001", "recorded"],
      ["REV-A-00002", "failed"],
      ["REV-A-00006", "recorded"],
      ["REV-A-00003", "skipped"],
    ]);
    expect(resultSentence(outcomes)).toBe(
      "2 recorded, 1 skipped: you are not one of the two trustees on REV-A-00003, 1 failed: REV-A-00002",
    );
    // The same notes go to every member's own notes column (reviewer, 2026-10-22).
    for (const call of save.mock.calls) expect(call[0].notes).toBe("Not enough evidence.");
  });

  it("writes strictly one after another", async () => {
    const order: string[] = [];
    let inFlight = 0;
    const plan = planGroupVerdict(M, rows(), user);
    await executeGroupVerdict(M, plan, VERDICT_VALUES.approve, undefined, async (input) => {
      inFlight += 1;
      expect(inFlight).toBe(1);
      await Promise.resolve();
      order.push(input.reviewId);
      inFlight -= 1;
    });
    expect(order).toEqual([rid(1), rid(2)]);
  });

  it("reports progress as 'n of total'", async () => {
    const progress: string[] = [];
    const plan = planGroupVerdict(M, rows(), user);
    await executeGroupVerdict(M, plan, 1, undefined, () => Promise.resolve(), (done, total) => {
      progress.push(`${String(done)}/${String(total)}`);
    });
    expect(progress).toEqual(["1/2", "2/2"]);
  });
});

describe("notes — EF-05 on a group verdict (reviewer, 2026-10-22)", () => {
  it("requires notes for Defer and Reject, not for Approve, and caps the length", () => {
    expect(groupNotesProblem(VERDICT_VALUES.defer, "  ")).toBe("required");
    expect(groupNotesProblem(VERDICT_VALUES.reject, "")).toBe("required");
    expect(groupNotesProblem(VERDICT_VALUES.approve, "")).toBeNull();
    expect(groupNotesProblem(VERDICT_VALUES.defer, "Reason.")).toBeNull();
    expect(groupNotesProblem(VERDICT_VALUES.approve, "x".repeat(VERDICT_NOTES_MAX_LENGTH + 1))).toBe("too-long");
  });

  it("sends no notes column for an Approve with no note, so each member's stored note is kept", () => {
    expect(notesToSend("   ")).toBeUndefined();
    expect(notesToSend("  Support.  ")).toBe("Support.");
  });
});
