# REVOpsFailureAlert-8F1C2A44-1004-4B7A-9E21-0A1B2C3D4E04.json - full action/trigger descriptions

Power Automate enforces a hard limit (256 characters) on the `description` field of every action, trigger, parameter and schema property - exceeding it blocks the flow from being saved in the designer at all. The condensed descriptions actually shipped in this file keep the essential fact and citation; the full reasoning that used to live there is preserved here, keyed by the same JSON path, so none of the domain detail this project treats as load-bearing documentation is lost.

## `/properties/definition/description`

REV | Ops | Failure Alert. Child flow called from the run-after failed/timed-out path of every other flow in this solution. Writes exactly one rev_errorlog row and alerts the process owner, so no failure is silent (FR-010, NFR-016). HOLDS NO PERSONAL DATA: the caller passes a record REFERENCE, never a name, contact detail or narrative fragment (NFR-012, C-DOM-004). The structural control is the rev_errorlog schema itself, which has no column capable of holding personal data (TAD NFR-012 rationale); the truncation below is defence in depth, not the control. Compliance caveat recorded in TAD section 5.14: a reference that resolves to a living person is strictly pseudonymised personal data rather than anonymous, which is why this table carries a 90-day operational retention and no trustee access (risk A-R12, flagged for DPO confirmation).

## `/properties/definition/triggers/manual/inputs/schema/properties/text_5/description`

The deep link to the CALLING flow's run, added 2026-08-20 after the first live failures produced
alerts nobody could act on. The caller builds it, because only the caller knows its own identity:

    concat('https://make.powerautomate.com/environments/', workflow()?['tags']?['environmentName'],
           '/flows/', workflow()?['name'], '/runs/', workflow()?['run']?['name'])

Both parts are runtime values, so nothing is hardcoded and no environment variable is needed -
`workflow()` resolves the environment id and the flow id of whichever flow is calling.

DELIBERATELY NOT IN THE `required` ARRAY. The three existing callers were updated in the same
change, but a required input would break any caller that had not been, and the failure alert is
the last thing that should fail. Absent, the Teams message says so and points at the run id
instead.

## `/properties/definition/actions/Compose_error_message_for_the_log/description`

The run link is appended to the logged error text rather than stored in its own column, because
`rev_errorlog` has no URL column and adding one is a schema change for a value that is only ever
read by a human clicking it. `rev_errormessage` is 4000 characters and the truncation above caps
the platform text at 2000, so there is room for the link and it survives truncation - it is
appended AFTER the cut, not before it.

## `/properties/definition/actions/Alert_process_owner_in_Teams/description`

Renders the run link as an anchor. The `if()` around it is load-bearing: an empty `text_5` would
otherwise produce `<a href="">`, a link that looks clickable and goes nowhere, which is worse
than no link. When it is absent the message says so in words.

## `/properties/definition/actions/Write_error_log_row/description`

`rev_runurl` was added to `rev_errorlog` on 2026-08-20 and is on the Error Log main form, so a
row is actionable on its own: the reader clicks through to the failing run without going via the
Teams alert. It replaces an earlier attempt that appended the link to `rev_errormessage`, which
worked but put a URL inside a column whose job is to hold the platform's error text.

FORMAT IS `text`, NOT `url`, AND THAT IS DELIBERATE. `A-G02` established on 2026-08-18 that
`Format=url` is not what this platform holds - the column the Web API created reported `text`,
and a DEV export wrote `text`, so source was corrected to match. The consequence is that the
value displays on the form but is not guaranteed to render as a clickable hyperlink. Making it
clickable is a change to make in the maker portal and then read back into source, exactly as
`A-G02` was resolved - not a second guess in this file.

The item object stays NESTED here. `CreateRecord` accepts `"item": { ... }` and is verified
working - this action wrote eleven rows that way. Only `UpdateRecord` needs the flattened
`item/<column>` form.
