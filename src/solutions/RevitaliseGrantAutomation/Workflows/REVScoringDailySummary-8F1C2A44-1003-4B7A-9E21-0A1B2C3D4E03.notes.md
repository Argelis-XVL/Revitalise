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

