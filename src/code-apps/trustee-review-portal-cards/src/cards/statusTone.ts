/**
 * The status tones — card app only, shared by the detail hero, the applications list and the
 * group detail members table (TAD trustee-portal-design-2 §13.3: "the detail screen's tone map,
 * moved to a shared card-only module"). Design: `ui_kits/trustee-review-portal/Shared.jsx`
 * `STATUS_TONES` (lines 64-69).
 *
 * Keyed by the option VALUE of `rev_applicationstatus`, never by a label string, so the mapping
 * reads the existing enumeration (`APPLICATION_STATUS_LABELS`) rather than inventing one; the test
 * pins each key's label against it.
 */
import { APPLICATION_STATUS_LABELS } from "../dataverse/schema";

export type StatusTone = "eligible" | "review" | "borderline" | "other";

export const STATUS_TONE_BY_VALUE: Readonly<Record<number, StatusTone>> = {
  6: "eligible", // "Eligible for Panel"
  5: "review", // "Under Review"
  3: "borderline", // "Borderline"
};

export function statusToneOf(status: number | null): StatusTone {
  if (status === null) return "other";
  return STATUS_TONE_BY_VALUE[status] ?? "other";
}

/** Re-exported so the tone test can check every key against the enumeration it claims to read. */
export const STATUS_LABELS = APPLICATION_STATUS_LABELS;
