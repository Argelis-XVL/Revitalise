# Power Automate — Design Conventions

> 📝 Replace `[PREFIX]` with your project's publisher prefix (from `stack-overview.md`).

## Flow Types in Use

| Type | When to Use | When NOT to Use |
|---|---|---|
| **Automated Cloud Flow** | Triggered by Dataverse row events (create/update/delete), HTTP webhooks, queue messages | Real-time UI interactions |
| **Instant Cloud Flow** | Triggered manually from MDA ribbon or button | Background/scheduled logic |
| **Scheduled Cloud Flow** | Batch jobs, nightly reconciliation, SLA checks | Event-driven logic |
| Desktop Flows | [✅ / ❌ — set per project] | — |
| Code App-triggered Flows | Called via HTTP action from a Power Apps Code App using a custom API or Power Automate HTTP trigger | — |
| Canvas-triggered Flows | [✅ / ❌ — depends on whether Canvas Apps are in scope] | — |

## Naming Convention

```
[PREFIX] <Domain> - <Action> - <Trigger>

Examples:
  [PREFIX] Cases - Escalate Record - On Status Change
  [PREFIX] Onboarding - Send Welcome Notification - Scheduled Daily
  [PREFIX] Approvals - Lock Record on Submit - On Row Updated
```

## Design Rules

### Trigger
- Dataverse triggers: always filter to the **specific columns** that should trigger the flow — never trigger on "any column change"
- Scheduled flows: store schedule configuration in a Dataverse configuration table, not hardcoded in the flow

### Error Handling
- Every flow must have a top-level **Scope** action with a parallel **Run After (failed/timed out/skipped)** error branch
- Error branch must: log to `[prefix]_flowexceptionlog` table, send alert to ops channel
- Never let a flow fail silently

### Connections
- All connections use **Service Principal** authentication where the connector supports it — no personal user connections in any non-Dev environment
- The SharePoint, Teams, and Office 365 connectors do **not** support service principals — use a dedicated **service account** connection for these, documented in TAD §4
- Connection references defined in solution; environment-specific values set via deployment parameters

### Microsoft 365 Connectors (SharePoint / Teams / Outlook)
- Site URLs, library names, and team/channel IDs come from **environment variables** — never literals (`C-TECH-047`)
- Teams notifications use Adaptive Cards with a deep link into the app; no Tier 3/4 data in cards or emails (see `knowledge/technology/teams.md`)
- All connectors must comply with the environment's DLP policies (`C-TECH-045`) — list every connector in TAD §4
- Calling Microsoft Graph via the HTTP connector requires an app registration — see `knowledge/technology/entra-id.md`

### Sensitive Data Flows
> 📝 If your domain has flows that handle highly sensitive data (Tier 3/4), define specific rules in
> `knowledge/domain/compliance-requirements.md`. Example controls to consider:
> - Never send sensitive content via email or to external endpoints without authorisation
> - Never log Tier 4 data to any system outside the platform boundary
> - Verify access controls before exposing sensitive data in notifications

### Performance
- Flows processing > 100 rows must use **pagination** (OData `$top` + `@odata.nextLink`)
- Flows calling external APIs must set a timeout and handle 429 / 503 with exponential back-off
- Avoid nested Apply-to-each loops — flatten with batch operations or child flows

## Testing Flows

- Unit test via **Power Automate Test Studio** (where available) or manual trigger with test data
- Integration test: trigger from a test Dataverse record; verify outcome in data and audit log
- All flows must have a test case in the test report covering: happy path and error branch

## Solution Packaging

Flows are stored inside the solution.
Connection references are environment-variable backed.
After `pac solution unpack`, flow JSON is committed to `src/solutions/<SolutionName>/Workflows/`.

## Hand-Authoring Flow JSON Before a Real `pac solution unpack` Exists

Everything in this section was learned the hard way: building flow JSON by hand ahead of a
live environment, then discovering the gap once a real import and a real designer session
exist. If a real `pac solution unpack` of a working flow is available, trust it over this
section - these are the traps that bite when it is not yet available.

- **Every `description` field has a hard 256-character limit — actions, triggers, trigger
  parameters, and trigger-schema properties, all of it.** This is a genuine platform limit,
  not a style guideline: exceeding it does not fail `pac solution pack` or `pac solution
  import` (both succeed silently), it fails only when a maker opens the flow in the designer
  and tries to save it - `Flow save failed`, with no indication of which field is over. A
  documentation style that writes long paragraph explanations (fine as an XML comment
  elsewhere in a solution) is exactly what overflows this. **Keep the description to the
  essential fact and citation (FR/NFR/ADR number); put the full reasoning in a companion
  `<FlowName>.notes.md` file next to the flow's `.json`, keyed by JSON path, so nothing is
  lost.** Gate this at build time (`scripts/verify-field-length-limits.py`, C-TECH-060 /
  `C-TECH-049`) — the failure mode is exactly the kind that hides for months until someone
  edits an unrelated part of the flow and can no longer save it.
- **A `Response` action requires `"operationOptions": "asynchronous"` whenever the trigger
  has concurrency control configured** (`runtimeConfiguration.concurrency.runs` set to
  anything). Without it: `Flow save failed with code 'InvalidConcurrencyConfiguration'`. This
  does not change the status code or body the caller receives - it only changes how the
  platform is allowed to deliver the response when concurrency limiting could delay
  processing. Any Request-triggered flow that both throttles concurrency (e.g. to protect a
  read-then-write step) and responds inline needs this on every `Response` action.
- **Do not add `runtimeConfiguration.staticResult` to an action unless you are actually
  configuring Static Results (a designer testing/mocking feature) with a real `name`.** A
  stray `{"staticResult": {"staticResultOptions": "Disabled"}}` block with no `name` looks
  inert but fails to save: `Flow save failed with code 'InvalidStaticResultName' ... cannot
  be null or empty`. If Static Results are not in use, omit the key entirely rather than
  writing a "disabled" placeholder.
- **When guessing a flow's JSON shape is unavoidable, get ground truth instead of guessing
  twice.** The entities Power Automate flows actually depend on (connection references,
  environment variable *values* at runtime) are ordinary Dataverse records — build one
  through the maker portal, or the smallest one via the Web API, then `pac solution export` +
  `pac solution unpack` it to see exactly how the platform serialises it, rather than
  iterating against live-import error messages one guess at a time.

## A Dataverse-Triggered Flow Is Not Live Until a `callbackregistration` Row Exists

Four findings on 2026-08-20 and 08-21 were the same mistake read four ways, and the cost was
several rounds of chasing Dataverse when the answer was never in Dataverse. The rule:

**`statecode=1` on a cloud flow does not mean its trigger is registered.** Query
`callbackregistrations?$filter=entityname eq '<table>'`. Zero rows means Dataverse will never
call the flow — no run is attempted, and run history shows nothing because there is nothing to
show. `statecode=0` is Draft, and a solution import never turns a flow on (`IMP-0100`).

**Existence of a row is not enough either.** Compare its `createdon` against the flow's
`modifiedon`. A registration that predates the import pins `logicappsversion` to a definition
version that no longer exists, and events are delivered into nothing — no run, no error, empty
history (`IMP-0114`). Deploying a Dataverse-triggered flow therefore has a mandatory post-deploy
step no import performs and no query substitutes for: turn the flow **off**, confirm the row
disappears, turn it on **from the designer**, confirm a row with a new `createdon` appears.

**`subscriptionRequest/runas` must be 3** (flow owner) on a row trigger. With 4 it packs,
imports and reports Activated while creating no subscription at all (`IMP-0108`).

**An unmanaged import with `--force-overwrite` deactivates every cloud flow in the solution**
while reporting success. Capture the statecodes before, re-assert them after, and re-activate in
the designer — never by PATCHing `workflow.statecode`, which can leave the flow reporting
Activated with no registration (`IMP-0113`). A designer save can also silently change the
trigger's scope, so re-read `subscriptionRequest/scope` out of `workflow.clientdata` afterwards
and compare it against solution source.

**When none of this explains it, stop querying Dataverse.** Two rows — one owned by the flow
owner, one not — rules out `scope=User` in two minutes. If neither fires and the registration
count is 0, every remaining cause is outside Dataverse: connection health, a DLP policy, or a
subscription error shown only in the maker UI (`IMP-0106`).

**A row-created trigger never replays.** Rows inserted before the registration existed must be
deleted and re-created, which is why the test-data loader deliberately does not upsert on the
`rev_sourcesubmissionid` alternate key (`IMP-0103`, `IMP-0104`).

### Environment variable VALUES do not travel, and an import can blank them

A definition ships in the solution; its value does not, and nothing in this repository writes
one. On 2026-08-20 DEV held four definitions and zero values, so every Teams action and the
failure-alert fallback email would have failed (`IMP-0101`). Worse: the DEV import **blanked all
five** `rev_*` variables that had been set by hand (`IMP-0121`).

Set the **current value**, never the definition's default — a default lives inside
`environmentvariabledefinition`, which is solution content, so the next import overwrites it
with whatever source declares, which is nothing. Check with:

```
environmentvariabledefinitions?$select=schemaname,defaultvalue
  &$expand=environmentvariabledefinition_environmentvariablevalue($select=value)
```

`isrequired=1` with no `defaultvalue` and no value row is the shape to look for: a required
setting nobody is scripted to supply.
