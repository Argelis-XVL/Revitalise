/**
 * `currentReviewFor` — the ONE chooser of an application's review (portal TAD
 * trustee-portal-design-2 ADR-086 point 2; SDD A-14, FR-116).
 */
import { describe, expect, it } from "vitest";
import { currentReviewFor } from "./currentReview";
import { makeReview } from "../test/harness";

const APP_A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa";
const APP_B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb";

describe("currentReviewFor", () => {
  it("returns null when no row belongs to the application", () => {
    expect(currentReviewFor(APP_A, [])).toBeNull();
    expect(currentReviewFor(APP_A, [makeReview({ applicationId: APP_B })])).toBeNull();
  });

  it("picks the newest panel date, ignoring rows of other applications", () => {
    const older = makeReview({ id: "11111111-0000-4000-8000-000000000001", applicationId: APP_A, panelDate: "2026-09-01T00:00:00Z" });
    const newer = makeReview({ id: "11111111-0000-4000-8000-000000000002", applicationId: APP_A, panelDate: "2026-10-01T00:00:00Z" });
    const otherApp = makeReview({ id: "11111111-0000-4000-8000-000000000003", applicationId: APP_B, panelDate: "2027-01-01T00:00:00Z" });
    expect(currentReviewFor(APP_A, [older, otherApp, newer])?.id).toBe(newer.id);
  });

  it("ranks a null panel date oldest", () => {
    const undated = makeReview({ id: "11111111-0000-4000-8000-000000000001", applicationId: APP_A, panelDate: null });
    const dated = makeReview({ id: "11111111-0000-4000-8000-000000000009", applicationId: APP_A, panelDate: "2020-01-01T00:00:00Z" });
    expect(currentReviewFor(APP_A, [undated, dated])?.id).toBe(dated.id);
    expect(currentReviewFor(APP_A, [dated, undated])?.id).toBe(dated.id);
  });

  it("breaks a tie on the review id, so every read gives the same answer whatever the input order", () => {
    const first = makeReview({ id: "11111111-0000-4000-8000-00000000000a", applicationId: APP_A, panelDate: null });
    const second = makeReview({ id: "11111111-0000-4000-8000-00000000000b", applicationId: APP_A, panelDate: null });
    expect(currentReviewFor(APP_A, [second, first])?.id).toBe(first.id);
    expect(currentReviewFor(APP_A, [first, second])?.id).toBe(first.id);
  });

  it("matches the application id case-insensitively, as the connector's GUIDs may vary in case", () => {
    const row = makeReview({ applicationId: APP_A.toUpperCase() });
    expect(currentReviewFor(APP_A, [row])).not.toBeNull();
  });
});
