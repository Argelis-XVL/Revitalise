/**
 * Decides what the trustee is shown for a review row, and wires the save.
 *
 * All five outcomes of `resolveSlot` are rendered, and four of them offer no write
 * path at all. That is the point: the `REV Trustee` role holds no
 * `prvCreaterev_review` (deliberately — see Roles/REV Trustee/REV Trustee.xml), so
 * when there is no review row the screen must say so plainly rather than present a
 * control that will fail.
 *
 * The recorded verdict is always shown as TEXT, including in the read-only states, so a
 * trustee can confirm what was captured for them without relying on the control's
 * appearance (WCAG 1.4.1).
 */
import { Spinner } from "@fluentui/react-components";
import { useToast } from "../app/toast";
import { VERDICT_LABELS, optionLabel } from "../dataverse/schema";
import type { ApplicationSummary, CurrentUser, ReviewRow } from "../dataverse/types";
import { resolveSlot } from "../domain/slots";
import { useSaveVerdict } from "../hooks/queries";
import { Definitions, Panel, StateMessage } from "./Panel";
import { VerdictForm } from "./VerdictForm";

const SLOT_LABELS = { trustee1: "Trustee 1", trustee2: "Trustee 2" } as const;

export function VerdictSection({
  application,
  review,
  user,
  loading,
}: {
  application: Pick<ApplicationSummary, "id" | "reference">;
  review: ReviewRow | null;
  user: CurrentUser;
  loading: boolean;
}) {
  const toast = useToast();
  const save = useSaveVerdict(application.id);

  if (loading) {
    return (
      <Panel heading="Your verdict">
        <Spinner size="tiny" label="Loading the review record…" labelPosition="after" />
      </Panel>
    );
  }

  const resolution = resolveSlot(review, user);

  if (
    resolution.kind === "no-review-row" ||
    resolution.kind === "unknown-user" ||
    resolution.kind === "not-assigned"
  ) {
    return (
      <Panel heading="Your verdict">
        <StateMessage heading={resolution.heading} explanation={resolution.explanation} />
      </Panel>
    );
  }

  if (resolution.kind === "finalised") {
    return (
      <Panel heading="Your verdict">
        <StateMessage heading={resolution.heading} explanation={resolution.explanation} />
        <Definitions
          items={[
            {
              label: "Recorded verdict",
              value: optionLabel(VERDICT_LABELS, resolution.verdict),
            },
            { label: "Recorded notes", value: resolution.notes ?? "None recorded" },
          ]}
        />
      </Panel>
    );
  }

  return (
    <Panel heading="Your verdict">
      <VerdictForm
        applicationReference={application.reference}
        slotLabel={SLOT_LABELS[resolution.slot]}
        initialVerdict={resolution.verdict}
        initialNotes={resolution.notes}
        saving={save.isPending}
        onSave={(verdict, notes) => {
          save.mutate(
            { reviewId: review !== null ? review.id : "", slot: resolution.slot, verdict, notes },
            {
              onSuccess: () => {
                toast.showSuccess(
                  "Verdict saved",
                  `${optionLabel(VERDICT_LABELS, verdict)} recorded for ${application.reference}.`,
                );
              },
              onError: (error: Error) => {
                // A failed save must never look like a successful one. The message stays
                // on screen until dismissed, and the form keeps what was typed.
                toast.showError("Could not save your verdict", error.message);
              },
            },
          );
        }}
      />
    </Panel>
  );
}
