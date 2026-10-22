/**
 * CARD APP (Design 2.0 Revision 2, TAD trustee-portal-design-2 §13.5, WI-0097/WI-0098):
 * `GroupScreens.jsx` lines 53-66 — the group hero (`cards/GroupHero.tsx`), the eyebrow
 * "Applications in this group", then the same members table, unsorted, with the verdict dialog
 * in place. "Group summary" stays the hero's accessible heading.
 *
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
 *
 * ## SDD A-14, FR-116 — the members table shows the trustee's own verdict (ADR-086)
 *
 * The same `ApplicationsTable`, so the same marking as the applications list: one review read for
 * the members (`useReviewIndex`), each member's review chosen by `currentReviewFor`, the button
 * from `ownVerdictState`. The per-member verdict button STAYS (EF-43, reviewer 2026-10-22: "No,
 * leave it for now." — ADR-087 point 8's "kept" design).
 *
 * ## SDD A-14, FR-118/FR-119 — one verdict for the whole group (ADR-087)
 *
 * Above the members table, **Record a verdict for the whole group** opens `GroupVerdictDialog`
 * with the members and the review index. Disabled, with the existing identity explanation, when
 * the user cannot be identified; disabled while the review index loads; and when the index could
 * not be read the page says so instead of planning from nothing.
 */
import { useId, useMemo, useState } from "react";
import { currentReviewFor } from "../dataverse/currentReview";
import { ownVerdictState } from "../domain/ownVerdict";
import type { OwnVerdictState } from "../domain/ownVerdict";
import { useReviewIndex } from "../hooks/queries";
import type { GroupSummary } from "../domain/groups";
import { DEFAULT_SORT } from "../domain/listView";
import { ApplicationsTable } from "../components/ApplicationsTable";
import { VerdictDialog } from "../components/VerdictDialog";
import { useToast } from "../app/toast";
import type { ApplicationSummary, CurrentUser } from "../dataverse/types";
import { usePageTitle } from "../hooks/usePageTitle";
import { Eyebrow } from "../components/Panel";
import { GroupHero } from "../cards/GroupHero";
import { GroupVerdictDialog } from "../components/GroupVerdictDialog";
import { Button } from "../components/ds";
import styles from "../styles/app.module.css";

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
  const [groupVerdictOpen, setGroupVerdictOpen] = useState(false);
  const identityNoteId = useId();
  const userKnown = user.systemUserId !== null;
  const memberIds = useMemo(
    () => (userKnown ? group.members.map((member) => member.id) : []),
    [group.members, userKnown],
  );
  const reviewIndex = useReviewIndex(memberIds);
  const verdictStateFor = (row: ApplicationSummary): OwnVerdictState =>
    reviewIndex.data === undefined
      ? { kind: "none" }
      : ownVerdictState(currentReviewFor(row.id, reviewIndex.data), user);

  return (
    <>
      <h1>Group {group.code}</h1>

      {/* The group header — the plan's own fixed, small field list, and nothing else. No
          cost field: see `domain/groups.ts`'s header for why one is not invented here.
          `Panel` is this app's own `<section aria-labelledby>` + `<h2>` primitive
          (`components/Panel.tsx`), reused rather than hand-rolled so this page's one new
          heading follows the same landmark pattern every other panel in the app already
          uses. */}
      <GroupHero group={group} />
      {/* ADR-087 point 1: the group verdict entry point, above the members table. */}
      <div className={styles.actionRow} data-print="hide">
        <Button
          variant="primary"
          disabled={!userKnown || reviewIndex.data === undefined}
          aria-describedby={userKnown ? undefined : identityNoteId}
          onClick={() => {
            setGroupVerdictOpen(true);
          }}
        >
          Record a verdict for the whole group
        </Button>
        {userKnown ? null : (
          <p id={identityNoteId} className={styles.hint}>
            {user.unresolvedReason ?? "The portal could not confirm which trustee you are signed in as."}
          </p>
        )}
        {userKnown && reviewIndex.isError ? (
          <p role="alert" className={styles.hint}>
            Your verdict status for this group could not be loaded, so a group verdict cannot be planned.
          </p>
        ) : null}
      </div>
      {/* GroupScreens.jsx:61 — decorative, above the members table. */}
      <Eyebrow tone="purple">Applications in this group</Eyebrow>
      <ApplicationsTable
        rows={group.members}
        sort={DEFAULT_SORT}
        // No sort control is offered for a group's small, fixed member set (see header
        // comment): the rows keep DEFAULT_SORT's order, and the headers are plain text with no
        // arrow, as the kit's group table passes no sort (GroupScreens.jsx:62).
        sortable={false}
        onSort={() => undefined}
        caption={`${group.memberCount} application${group.memberCount === 1 ? "" : "s"} in group ${group.code}.`}
        onOpen={onOpenApplication}
        verdictStateFor={verdictStateFor}
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

      {groupVerdictOpen && reviewIndex.data !== undefined ? (
        <GroupVerdictDialog
          groupCode={group.code}
          members={group.members}
          reviewRows={reviewIndex.data}
          user={user}
          onClose={() => {
            setGroupVerdictOpen(false);
          }}
        />
      ) : null}

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
