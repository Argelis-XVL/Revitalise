# Power Automate — Design Conventions

> 📝 Replace `[PREFIX]` with your project's publisher prefix (from `stack-overview.md`).

## Flow Types in Use

| Type | When to Use | When NOT to Use |
|---|---|---|
| **Automated Cloud Flow** | Triggered by Dataverse row events (create/update/delete), HTTP webhooks, queue messages | Real-time UI interactions |
| **Instant Cloud Flow** | Triggered manually from MDA ribbon or button | Background/scheduled logic |
| **Scheduled Cloud Flow** | Batch jobs, nightly reconciliation, SLA checks | Event-driven logic |
| Desktop Flows | [✅ / ❌ — set per project] | — |
| Code App-triggered Flows | **Instant flow with the Power Apps trigger, registered with `pa app add flow`** — see the section below. **E1** (live-confirmed against DEV 2026-08-25, `IMP-0317`) | **Not** an HTTP-trigger URL and **not** a custom API with MSAL — see the warning below |
| Canvas-triggered Flows | [✅ / ❌ — depends on whether Canvas Apps are in scope] | — |

### Calling a flow from a Power Apps code app — and the row that used to be wrong here

> ⚠️ **This row previously said a code app calls a flow "via HTTP action … using a custom API or
> Power Automate HTTP trigger". Both are wrong for this stack, and the first would have violated a
> HARD constraint.** A Power Automate HTTP-trigger URL carries a SAS key in the query string, and
> embedding one in a client-side app is exactly the *"hand-rolled token acquisition or credential
> handling"* that `C-TECH-048` forbids. An architect reading the old row would reasonably conclude
> either that flow invocation was unavailable within the rules, or that it needed an app
> registration and MSAL. It was template text nobody had ever checked, and it contributed to a TAD
> designing a nightly batch, a table, an option set, a purge job and four provisioning items that
> were then deleted (`IMP-0303`, `IMP-0304`).

**The first-party route** — **E1, live-confirmed against this project's DEV environment on
2026-08-25** (`IMP-0317`; recorded as `IMP-0306`/E2 from Microsoft Learn before it was run):

```bash
pa app list-flows                      # find the flow
pa app add flow --flow-id <guid>       # generate the typed service + register it
```

**`pa` and `pac` are two different binaries, and only one of them has this verb.** `pa` is the
Power Apps CLI (`~/.npm-global/bin/pa`, v1.0.0 here); `pac` is the Microsoft PowerPlatform CLI
(`~/.dotnet/tools/pac`, v2.4.1 here) and **has no `app` command group at all**. A design document
that writes `pac app add flow` names a command that does not exist. Both `pa app list-flows` and
`pa app add flow -f <id>` returned real results against DEV — including under Auto Mode, which had
been assumed to refuse them (`IMP-0314`).

**A new cloud flow also needs its own `<RootComponent>` entry in `Other/Solution.xml`, one per
flow by GUID.** It is *not* covered by anything else the way an entity's `behavior="0"` attributes
are, so adding a flow is two changes. And when you check whether a component is declared, **grep
for the type number or the GUID, never the display name** — `RootComponent` entries for
GUID-keyed types (flows, roles) carry no name at all, so a name-grep returns nothing and reads
exactly like "this type does not need a declaration":

```bash
grep -c 'type="29"' src/solutions/*/Other/Solution.xml   # cloud flows, declared
```

`scripts/verify-solution-root-components.py` catches the omission on the next full test run with
the flow's GUID in the message, which is how this one was found.

`pa app add flow` downloads the flow's OpenAPI definition, generates a typed TypeScript service
exposing a **static `Run()`** returning `{ success, data, error }`, and adds the flow plus its
connection references to `power.config.json`. Because it is a CLI-generated managed data source, it
satisfies `C-TECH-048` — there is no token for anyone to hand-roll.

**Preconditions, all four of which bite:**

| Precondition | Consequence if unmet |
|---|---|
| The flow is **solution-aware** | Not addressable by `--flow-id` |
| Its trigger is the **Power Apps trigger** | Scheduled, automated and other instant triggers are **not supported** |
| `@microsoft/power-apps` **≥ 1.1.1** | The verb does not exist below that floor (this project is on 1.3.0) |
| The end user holds **Dataverse privileges to invoke the flow** | Runtime failure per user, not a build error |

**The flow runs on its own connection reference, which is what makes the read privileged** — that
is the whole reason this route can aggregate over a column the signed-in user cannot read.

### `List rows` does NOT support aggregate FetchXML

**E2**, Microsoft Learn's *"Use lists of rows in flows"*, recorded 2026-08-25 (`IMP-0306`):

> "Aggregation queries aren't currently supported when using the List rows action with FetchXML
> queries. However, the distinct operator is supported."

So `count`, `groupby` and `avg` are **unavailable inside a flow**. Tally with array expressions over
the returned rows instead, and mind the page limits while doing it. This is recorded as a stated
platform boundary because nothing anywhere in this repository held it, which left a previous design
treating server-side aggregation in a flow as an open possibility worth verifying later.

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
