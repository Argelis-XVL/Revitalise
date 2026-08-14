# Skill: How to Design a Workflow / Automation

Used by: `architect-agent`, `development-agent` (automation-agent)

---

## Trigger Taxonomy

Every automated workflow is initiated by one of:

| Trigger Type | Examples | Key Design Question |
|---|---|---|
| **Event-driven** | Record created/updated, message on a queue, webhook | Is the event source reliable? Can events be missed? |
| **Scheduled** | Cron job, daily batch | What happens if the schedule slips or runs twice? |
| **User-initiated** | Button press, API call, form submit | Is synchronous response required, or can it be async? |
| **Threshold / condition** | Alert when value crosses a limit | How is the threshold checked — polling or reactive? |

---

## Design Checklist

For every workflow:

- [ ] Trigger type identified and documented
- [ ] Input validated before processing begins
- [ ] Idempotency: can the workflow run twice safely? If not, document the guard
- [ ] Error handling: what happens at each failure point?
- [ ] Retry strategy: exponential back-off with a max retry cap
- [ ] Dead-letter: where do unprocessable messages go?
- [ ] Timeout: every external call has a defined timeout
- [ ] Logging: entry, exit, and error states are logged
- [ ] Alerts: on-failure notification to ops/on-call
- [ ] Data sensitivity: are credentials / PII handled safely (not logged, encrypted in transit)?

---

---

## Platform Limits and Where the Reasoning Goes

A workflow definition is a **platform artefact**, not a document. Its fields have limits the
packer does not check and the deploy does not check — they fail when a human opens the flow,
naming no field. Load `skills/how-to-verify-a-platform-contract.md` before hand-authoring one.

- **Know the limits before writing.** On Power Automate, every `description` — flow, trigger,
  action, parameter, schema property — is capped at **256 characters** (`C-TECH-049`). 62
  fields across four flows exceeded it here, one at 6,696 characters, and every one of them
  packed and imported successfully before making the flows unopenable.
- **The explanation and the field are different places.** Put the essential fact plus its
  FR/NFR/ADR citation in the field; put the full reasoning in a companion
  `<FlowName>.notes.md` next to the definition, keyed by JSON path. Verbose documentation is
  correct in a notes file and fatal in a flow field.
- **Configuration blocks interact.** Setting one property can silently invalidate another —
  capping trigger concurrency, for example, makes every inline `Response` action require
  `"operationOptions": "asynchronous"`. Check the stack's knowledge file
  (`knowledge/technology/power-automate.md`) for the known pairs before designing around one.
- **Never write an inert-looking placeholder block.** A "disabled" configuration stanza with
  a missing required child is not inert; it fails validation. Omit the key entirely.
- **Gate each limit at build time**, in `config/<slug>-build.yml`. A limit enforced only by a
  human opening the artefact months later is not enforced.

---

## Diagramming

Document every non-trivial workflow as a flowchart:

```mermaid
flowchart TD
  A([Trigger]) --> B{Input valid?}
  B -- No --> C[Return error / reject]
  B -- Yes --> D[Process step 1]
  D --> E{External call OK?}
  E -- No --> F[Retry / dead-letter]
  E -- Yes --> G[Process step 2]
  G --> H([Complete])
```

Include the diagram in the TAD (Section 5).

---

## Long-Running Processes

If a workflow runs longer than ~30 seconds:
- Make it **asynchronous** — return an accepted/queued response immediately
- Track status with a job/task record in the database
- Expose a status-check endpoint or mechanism
- Send a notification on completion or failure

---

## Compensation / Rollback

For workflows that modify multiple systems:
- Define the rollback action for each step
- Consider the Saga pattern for distributed transactions
- Prefer eventual consistency over distributed locks where possible

---

## Testing Workflows

| Test Scenario | How |
|---|---|
| Happy path | Provide valid input; assert expected outcome |
| Invalid input | Provide each bad input variant; assert rejection |
| External service failure | Mock the service returning 5xx / timeout |
| Duplicate trigger | Run the workflow twice; assert idempotent outcome |
| Timeout | Mock slow external call; assert timeout handling |
| Retry exhaustion | Exhaust retries; assert dead-letter behaviour |
