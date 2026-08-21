# REVScoringDailySummary-8F1C2A44-1003-4B7A-9E21-0A1B2C3D4E03.json - full action/trigger descriptions

Power Automate enforces a hard limit (256 characters) on the `description` field of every action, trigger, parameter and schema property - exceeding it blocks the flow from being saved in the designer at all. The condensed descriptions actually shipped in this file keep the essential fact and citation; the full reasoning that used to live there is preserved here, keyed by the same JSON path, so none of the domain detail this project treats as load-bearing documentation is lost.

## `/properties/definition/description`

REV | Scoring | Daily Summary. Serves FR-021: tell the process owner how many applications were scored, how many were auto-rejected and how many are Borderline awaiting review, so she has oversight without opening the system.

COUNTS ONLY, NO IDENTIFIERS - AND THAT IS ENFORCED BY THE QUERIES, NOT BY THE MESSAGE. Every list below selects rev_applicationid and nothing else, so the flow never holds a name, a reference, a score or a narrative to leak. A summary posted into a chat is the easiest place in the whole solution for personal data to escape, so the narrowing is deliberate (TAD section 5.3, NFR-012).

SAFE TO RUN TWICE: it reads and reports, it writes nothing to Dataverse. A duplicated schedule produces a duplicate message and no data effect.

DOCUMENTED DEVIATION from knowledge/technology/power-automate.md, which says scheduled flows should hold their schedule in a Dataverse configuration table. A Recurrence trigger is evaluated by the platform before any action runs, so it CANNOT read a Dataverse row - the schedule is necessarily a trigger property. Changing the time is a solution change, not a setting change. Recorded in Dev Summary section 4.

## `/properties/definition/triggers/Every_weekday_morning/description`

07:00 UTC, Monday to Friday. Weekdays only because the summary exists to prompt action and there is nobody to act at the weekend - a Saturday message trains the recipient to ignore the channel. Monday's message therefore covers the whole weekend, which is why the reporting window below is computed from the previous run rather than fixed at 24 hours.

## `/properties/definition/actions/Summarise/actions/Count_borderline_awaiting_review/description`

Deliberately NOT windowed. FR-021 asks how many are Borderline AWAITING REVIEW, which is a backlog question, not a yesterday question - a Borderline application ignored for a fortnight must keep appearing in this count until somebody looks at it. That is what makes NFR-018 (100% of Borderline outcomes receive human review) observable day after day.

## `/properties/definition/actions/Summarise/actions/Count_withheld_awaiting_review/description`

Status 5 Under Review - the FR-022 cases where a scored answer was missing so no automated outcome was issued. Not named in FR-021, but included as a DERIVED addition: NFR-018 requires 100% of these to reach a human too, and an application sitting unscored is the most easily forgotten state in the process. Also a backlog count, not a windowed one.

## `/properties/definition/actions/Summarise/actions/Post_the_summary/description`

Each "waiting for you now" line is now a link into the view it counts, added 2026-08-20. The URL
is assembled from two sources with different lifetimes, and keeping them apart is the point:

  * the **view id** comes from the solution's own `Entities/rev_application/SavedQueries/`, so it
    is identical in every environment and belongs in this definition;
  * the **host and appid** are assigned per environment and come from the `rev_GrantAdminAppUrl`
    environment variable (C-TECH-047).

`if(empty(parameters('rev_GrantAdminAppUrl')), ...)` guards every anchor. An unset variable would
otherwise render `href=""`, and the summary's whole job is to be acted on - a dead link is worse
than a plain count. When it is unset the counts still send and the message says how to enable the
links.

THIS ACTION IS THE FALLBACK, NOT THE MESSAGE - CORRECTED 2026-08-21. The paragraph that stood
here said "this is not an Adaptive Card ... converting to one is worth doing only if buttons are
actually wanted", and it was already false when it was written: `Post_the_summary_card` was added
the same day and has been posting a real card through `PostCardToConversation` ever since. This
HTML message runs only on that card's `Failed` / `TimedOut` / `Skipped`, carrying the same counts
with anchors instead of buttons. Both shapes work; the card is what the process owner sees.
Logged as `IMP-0131`, with the finding that nothing ties an action's documentation to the action's
own operationId.

## `/properties/definition/actions/Find_the_failed_action/description`

See the same note in the scoring flow. `result('Summarise')[0]` named the first child rather than
the failed one; this filters for the child whose status is Failed. `Summarise` has no nested
scope, so there is nothing to descend into and no second lookup is needed.

