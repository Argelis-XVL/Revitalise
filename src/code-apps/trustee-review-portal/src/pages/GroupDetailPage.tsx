/**
 * The group detail page (EF-43) — opened by clicking a row of `GroupsTable`.
 *
 * `docs/plans/emily-review-feedback-2026-09-plan.md` §4.3 settles this page's content in
 * full, from the delivered 12-page worked example: the group header repeats the group's own
 * summary fields (code, member count, group total requested, shared dates — no cost field,
 * see `domain/groups.ts`), and the member list below shows each application's NORMAL SUMMARY
 * FIELDS, the same ones `ApplicationsTable` already renders on the flat list. Reusing that
 * component rather than inventing a second table pattern is deliberate: `code-apps.md`'s
 * "derive in domain/, keep components thin" applies to REUSING an existing thin component
 * exactly as much as it applies to writing a new one, and every member row still opens the
 * SAME application detail page and offers the SAME "Record verdict" control the flat list
 * does — a trustee working from a group should lose no capability the flat list gives them.
 *
 * ## Why the score breakdown / circumstance score panel is absent, and how that is proved
 *
 * The plan's own worked example omits *Current Circumstances* in all 12 of the groups it
 * covers, "so the group detail page does not need the score breakdown" — this removed what
 * the plan itself calls "the biggest unknown" in EF-43's design. `CasePanels.tsx`'s
 * `ScorePanel` (heading "Summary" as of Revision 14 — "Circumstance score" before it) is what
 * an individual application's OWN detail page renders for that; this page never imports
 * `CasePanels` at all, so there is no code path here that could render it.
 * `GroupDetailPage.test.tsx` asserts the heading's absence directly rather than relying on "it
 * was never imported" as proof, because an import can be
 * added back later without this file's own tests noticing.
 *
 * No sort state is kept here, unlike `ApplicationsListPage` — a group is capped at however
 * many applications share one manual code (five and twelve in the plan's own worked
 * examples), which does not need FR-034's sortable/filterable machinery. `ApplicationsTable`
 * still requires a `SortState`/`onSort` pair to render its header buttons, so a fixed,
 * unchanging sort is passed through rather than adding a second, parallel "no-op sort"
 * concept to this codebase.
 *
 * ## EF-43 Δ5 — `onOpenApplication`'s SIGNATURE is unchanged; what `App.tsx` does with it is not
 *
 * The reviewer's live check found no route back from a member's own detail page to this one
 * (`docs/Import/FeedbackDeployment_20-09-2026.xlsx` row 50). This page's own `onOpenApplication`
 * prop is still exactly `(application: ApplicationSummary) => void` — this file needs no code
 * change for that fix, because it never held a `group` field to forget. `App.tsx`'s own call
 * site (its "EF-43 Δ5" header) is what changed: it now closes over `view.group` and carries it
 * into the `detail` view's new `fromGroup` field, which `ApplicationDetailPage` reads to offer
 * the "Back to group …" button. Recorded here so a reader of THIS file's `onOpenApplication`
 * prop is not left wondering why a fix that sounds like it belongs here left no diff.
 */
import { useState } from "react";
import { formatAmount, formatDateRange } from "../domain/format";
import type { GroupSummary } from "../domain/groups";
import { DEFAULT_SORT } from "../domain/listView";
import { ApplicationsTable } from "../components/ApplicationsTable";
import { VerdictDialog } from "../components/VerdictDialog";
import { useToast } from "../app/toast";
import type { ApplicationSummary, CurrentUser } from "../dataverse/types";
import { usePageTitle } from "../hooks/usePageTitle";
import { Definitions, Panel } from "../components/Panel";

export function GroupDetailPage({
  group,
  user,
  onOpenApplication,
}: {
  group: GroupSummary;
  user: CurrentUser;
  onOpenApplication: (application: ApplicationSummary) => void;
}) {
  usePageTitle(`Group ${group.code}`);
  const toast = useToast();
  const [verdictFor, setVerdictFor] = useState<ApplicationSummary | null>(null);

  return (
    <>
      <h1>Group {group.code}</h1>

      {/* The group header — the plan's own fixed, small field list, and nothing else. No
          cost field: see `domain/groups.ts`'s header for why one is not invented here.
          `Panel` is this app's own `<section aria-labelledby>` + `<h2>` primitive
          (`components/Panel.tsx`), reused rather than hand-rolled so this page's one new
          heading follows the same landmark pattern every other panel in the app already
          uses. */}
      <Panel heading="Group summary">
        <Definitions
          items={[
            { label: "Group code", value: group.code },
            { label: "Members", value: String(group.memberCount) },
            { label: "Group total requested", value: formatAmount(group.totalRequested) },
            { label: "Shared dates", value: formatDateRange(group.sharedStart, group.sharedEnd) },
          ]}
        />
      </Panel>

      {/* The member list — `ApplicationsTable` reused whole, so a member row opens the same
          application detail page and offers the same "Record verdict" control the flat
          applications list gives. Deliberately no circumstance-score BREAKDOWN panel here —
          see this file's header. */}
      <ApplicationsTable
        rows={group.members}
        sort={DEFAULT_SORT}
        // No sort control is offered for a group's small, fixed member set (see header
        // comment) — clicking a header re-applies the same fixed order rather than doing
        // nothing silently.
        onSort={() => undefined}
        caption={`${group.memberCount} application${group.memberCount === 1 ? "" : "s"} in group ${group.code}.`}
        onOpen={onOpenApplication}
        onRecordVerdict={(application) => {
          if (user.systemUserId === null) {
            toast.showError(
              "Cannot record a verdict yet",
              user.unresolvedReason ??
                "The portal could not confirm which trustee you are signed in as.",
            );
          }
          setVerdictFor(application);
        }}
      />

      {verdictFor === null ? null : (
        <VerdictDialog
          application={verdictFor}
          user={user}
          onClose={() => {
            setVerdictFor(null);
          }}
        />
      )}
    </>
  );
}
