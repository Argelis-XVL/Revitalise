# REVOpsFailureAlert-8F1C2A44-1004-4B7A-9E21-0A1B2C3D4E04.json - full action/trigger descriptions

Power Automate enforces a hard limit (256 characters) on the `description` field of every action, trigger, parameter and schema property - exceeding it blocks the flow from being saved in the designer at all. The condensed descriptions actually shipped in this file keep the essential fact and citation; the full reasoning that used to live there is preserved here, keyed by the same JSON path, so none of the domain detail this project treats as load-bearing documentation is lost.

## `/properties/definition/description`

REV | Ops | Failure Alert. Child flow called from the run-after failed/timed-out path of every other flow in this solution. Writes exactly one rev_errorlog row and alerts the process owner, so no failure is silent (FR-010, NFR-016). HOLDS NO PERSONAL DATA: the caller passes a record REFERENCE, never a name, contact detail or narrative fragment (NFR-012, C-DOM-004). The structural control is the rev_errorlog schema itself, which has no column capable of holding personal data (TAD NFR-012 rationale); the truncation below is defence in depth, not the control. Compliance caveat recorded in TAD section 5.14: a reference that resolves to a living person is strictly pseudonymised personal data rather than anonymous, which is why this table carries a 90-day operational retention and no trustee access (risk A-R12, flagged for DPO confirmation).

