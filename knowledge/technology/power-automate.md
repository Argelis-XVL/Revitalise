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

### And there is no `sum()` over an array in the expression language either

**E3**, Microsoft Learn's *Reference guide to functions in expressions for workflows in Azure Logic
Apps and Power Automate* → **Math functions**, read 2026-08-28 (`IMP-0463`). The complete set is:

> `add` · `div` · `max` · `min` · `mod` · `mul` · `pow` · `rand` · `range` · `sub`

**No `sum`. No `average`.** And `add(<summand1>, <summand2>)` takes **exactly two** operands. Two
consequences, and the first is why this is not merely inconvenient:

- A total over a **fixed, known** operand count is expressible by nesting `add()` *n−1* deep. This is
  how FR-060's five-break-type total-row **count** ships.
- A total over a **variable-length array is not expressible at all.** So *no mean, no total and no
  ratio-of-totals over a filtered subset* can be computed with the math functions, however the
  requirement is worded.

**`max` and `min` are the only two that accept a collection** — documented as *"the highest value
from a set of numbers **or an array**"*, with `min(createArray(1, 2, 3))` as Microsoft's own example.
That is both a real capability and the reason `max(<divisor>, 1)` is available as the safe-divisor
pattern below.

**The trap that makes this worth writing down.** Bot Framework's *Adaptive expressions* reference
has `sum`, `average`, `floor`, `ceiling` and `round`, and its page sits one search result away from
the one that governs here. Finding `sum` on that page and concluding it exists is the failure this
section prevents — check which product the reference is for before believing a function exists.

### Totalling a variable-length array anyway: `xpath(xml(...), 'sum(...)')`

**This IS a first-party documented pattern, not a trick** (`IMP-0466`, correcting an earlier
characterisation in this project's own design documents). It is **Example 7** in the same reference's
**X** section:

```
xpath(xml(parameters('items')), 'sum(/produce/item/count)')     → 30
```

And the same page fixes the semantics: *"In Consumption and Standard logic apps, all function
expressions use the **.NET XPath library**… and support only the expression that the underlying .NET
library supports."* So **XPath 1.0 rules govern**, and XPath 1.0 has two silent-wrong-answer modes
(`IMP-0467`):

| Input | XPath 1.0 `sum()` returns | Why it is dangerous |
|---|---|---|
| An **empty** node-set | `0` | Indistinguishable from a real total of zero |
| A node-set with **any** non-numeric leaf — a blank element from a null column, or a formatted `1,200.50` | **`NaN` for the whole sum** | `NaN` is not valid JSON, so one blank cell makes the entire response document unparseable and takes **every** metric off the screen, not just the affected one |

**On this project that is certain, not hypothetical:** all three money columns on `rev_application`
are `RequiredLevel None`, so blanks occur in real data.

#### There is a THIRD emptiness, and it is the one that nearly shipped a defect

Added 2026-08-28 (`IMP-0473`), after the shape above was built and measured. **A blank VALUE inside
a non-empty collection and an entirely EMPTY collection are different failures, and a presence
filter only fixes the first.**

`join()` over an empty array returns `''`. Wrap that in the element literals and you get
`<r><v></v></r>` — a node-set containing one empty element, which is exactly the `NaN` case. So the
literal expression *"filter the nulls out, then sum"* **converts an empty subset into `NaN`**, and
"the presence filter removes the `NaN` case" is true only of blank values inside a collection that
has something in it.

Measured against a conformant XPath 1.0 engine (libxml2 — the semantics are specification-level, so
they carry to the .NET library the runtime actually uses):

| XML | `sum(/r/v)` |
|---|---|
| `<r></r>` | `0` |
| `<r><v></v></r>` | **`NaN`** |
| `<r><v>10</v><v></v></r>` | **`NaN`** |
| `<r><v>10</v><v>5</v></r>` | `15` |

**So build the XML so an empty collection produces NO element at all** — do not guard the sum,
guard the *projection*:

```
concat('<r>', if(empty(body('S')), '', concat('<v>', join(body('S'), '</v><v>'), '</v>')), '</r>')
```

**And check where a `NaN` can escape to.** A nested `add()` over per-group sums carries one group's
`NaN` into the total, so a single break type with no costed application takes **every** metric in
the document off the screen rather than one. That is the difference between a `rework` finding and a
`blocker`: it was caught pre-ship.

**So: exclude, never coerce.** Filter the nulls **out** before projecting to XML — and that filter's
own `length()` is the measure's honest denominator, because coercing a null to `0` while still
counting the row biases the mean.

**Level reached: V1.** The pattern is documented, its semantics are attributable, and the four
results above are measured against an XPath 1.0 engine; **no run on this tenant has produced a
figure from it.**

**This IS partly gate-enforced now** — corrected 2026-08-28, `IMP-0473`. The sentence here used to
read *"nothing in `verify-flow-definition-language.py`'s seven checks reads inside an `xpath()`
expression, so an unguarded `sum()` over a nullable column packs, imports, activates and runs
green."* That remains true of *that* script, and it is no longer the whole picture:
`scripts/verify-flow-trigger-body-isolation.py` check B1 exempts this reduction only as an
**anchored template** (`_SCALAR_REDUCTION`) that includes the `if(empty(body('S')), '', …)` guard
above, with the *same* source in both positions. The unguarded form therefore fails a HARD build
gate rather than only failing a test, and a known-bad fixture plus a `BuildGates.Tests.ps1` block
hold the line. What is still unchecked: any *other* `xpath()` expression, and any `sum()` outside
that one pinned shape.

**The two alternatives, with their costs, so a design need not re-derive them.** An `Apply to each`
accumulation is proven and turns a declarative tally into roughly 900 sequential action executions,
which breaks a *"figures read as seconds old"* claim; a Dataverse Custom API reopens ADR-030's
rejection. **Choosing between the three is an architecture decision** (carried as TAD A-FLOW-08) —
this file records what each costs and picks none.

## Naming Convention

```
[PREFIX] <Domain> - <Action> - <Trigger>

Examples:
  [PREFIX] Cases - Escalate Record - On Status Change
  [PREFIX] Onboarding - Send Welcome Notification - Scheduled Daily
  [PREFIX] Approvals - Lock Record on Submit - On Row Updated
```

## Design Rules

### `if()` and short-circuiting — THIS REPOSITORY RECORDS BOTH ANSWERS, AND THE QUESTION IS OPEN

Added 2026-08-28 by improvement review 33, and **deliberately narrower than the finding that
prompted it** (`IMP-0378`, narrowed by `IMP-0412`).

Two lessons in this repository state opposite things about whether the workflow definition
language's `if(<condition>, <valueIfTrue>, <valueIfFalse>)` evaluates both branches:

| Recorded in | Claims | Evidence |
|---|---|---|
| `IMP-0124`'s tail | `if()` evaluates **only the branch it takes** | TD-07 failing and TD-08 passing on the same action |
| `IMP-0378` | `if()` evaluates **all three arguments** | Microsoft's function reference: *"Parameters are evaluated from left to right"* |

**Both are recorded in this repository as established. Only one can be right, and neither has been
re-tested.** `IMP-0412`'s own analysis is that `IMP-0124`'s differential observation cannot
distinguish the two cases — but it labels that a *prediction*, not a finding. So neither is written
here as settled: a documentation-derived claim written down as established is
`skills/how-to-promote-a-finding.md` §4's named exclusion and `IMP-0217`'s defect.

**Write arithmetic that is correct under EITHER semantics. It costs nothing.**

```
A DIVISION BY A POSSIBLY-ZERO POPULATION
NOT:  if(equals(population, 0), 0, mul(div(float(count), float(population)), 100))
USE:  mul(div(float(count), float(max(population, 1))), 100)

A DATE FUNCTION OVER A POSSIBLY-NULL DATE  —  ticks() and formatDateTime() THROW on null
NOT:  if(empty(coalesce(openedOn, '')), 'null', concat(... ticks(openedOn) ...))
USE:  ticks(coalesce(openedOn, <a real timestamp, e.g. computedOn>))
```

`max(<divisor>, 1)` gives the same correct answer whenever the true divisor is 0, because the
numerator is then necessarily 0 too. `coalesce(<maybe-null date>, <a real timestamp>)` makes both
branches total before either date function is reached. This is the shipped pattern for every
percentage-over-a-possibly-zero-population computation in this project's flows. Never use a
conditional to guard a division, an array index, a date function, or anything else that throws on
the *untaken* branch's own inputs.

**The second example is not hypothetical — it is `IMP-0460`.** A dispatch brief quoted `IMP-0124`'s
tail as settled ground truth and specified the `NOT:` form for FR-058's `applicationsPerDay`. Under
eager evaluation an absent `rev_roundopenedon` makes `ticks(null)` throw, which fails the `Compose`,
fails `Compute_statistics`, and takes **every figure on the trustee landing screen** down over one
untyped date. It was rewritten to the `USE:` form before it shipped, which returns the identical
document under either semantics.

**Settling it needs one deliberate live run:** an `if()` whose untaken branch divides by zero,
observed once. Whichever lesson loses then gets a `corrects` entry naming the other.

**Until then the digest marks it.** `logs/known-failure-modes.md` renders **⚠ CONTESTED by
`IMP-0412`** beneath `IMP-0124`'s lesson, so the trailing clause can no longer be read as settled by
anyone meeting it there. That marker records a dispute and does **not** decide it — the `corrects`
edge above is still reserved for whichever claim eventually loses.

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

**`subscriptionRequest/message` is NOT `{1 Create, 2 Update, 3 Delete}`.** Read live from
`stringmap` in `REV-GrantApplications-DEV` on 2026-08-28, the `callbackregistration.message`
option set is:

| Value | Meaning | | Value | Meaning |
|---|---|---|---|---|
| 1 | Added | | 5 | Added or Deleted |
| **2** | **Deleted** | | 6 | Modified or Deleted |
| **3** | **Modified** | | 7 | Added or Modified or Deleted |
| 4 | Added or Modified | | | |

**For "fires when a row is updated" the value is 3.** `2` is *Deleted*, and it looks exactly like
the natural choice for the second of {Create, Update, Delete}, which is how an APPROVED ADR came
to specify it (`IMP-0406`, a **blocker**). This is the same defect shape as `runas: 4` above: the
wrong value packs, imports and reports `Activated` while registering a webhook for an event that
never happens — so the flow never fires, a polling app times out, and every user is told "still
working" forever with every source-side gate green.

The parameter passes straight through to `callbackregistration.message`, corroborated in both
directions on this tenant, so **the cheapest confirmation for any row-triggered flow is to read
that column's formatted value back after turning the flow on.** Note the narrow limit: that is
the ONE thing a `callbackregistration` row can tell you, because its existence, `createdon`,
`scope` and `runas` are all inadmissible as evidence that a trigger fires (`C-TECH-064` clause
(a)).

**Reading a live flow definition, and a picklist's real enumeration, from this Mac.** Both are
read-only, unrefused under Auto Mode, and touch no cert or keychain (`IMP-0409`):

```bash
# A live flow definition, in the same file shape as src/solutions/ — so a live-vs-source
# comparison is a plain file diff. This is the route that WORKS; see IMP-0083's cert-based
# Web API path for the one that gets refused under Auto Mode (IMP-0287).
pac solution export --path <dir> --name RevitaliseGrantAutomation --overwrite
pac solution unpack --zipfile <dir>/RevitaliseGrantAutomation.zip --folder <dir> \
    --packagetype Unmanaged

# Any picklist's real value-to-label mapping, including platform tables like callbackregistration.
pac env fetch --xml "<fetch><entity name='stringmap'>\
<attribute name='attributevalue'/><attribute name='value'/>\
<filter><condition attribute='attributename' operator='eq' value='<column>'/></filter>\
</entity></fetch>"
```

**Do NOT reach for `pac env fetch` to read `workflow.clientdata`**: it renders results as a
fixed-width TABLE, so the column is truncated to a column width and cannot be recovered, and
`pac` 2.4.1 has no `--dataFile` option (only `--environment`, `--xml`, `--xmlFile`). That trap is
named here because it is the obvious first thing to try.

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

### `result()` is documented for `Scope`, `For_each` and `Until` — and for nothing else

**Microsoft documents `result()` against exactly three container types. A `Switch` or an `If`
passed by its own name is neither confirmed nor denied anywhere in first-party documentation**
(`IMP-0496`, ground-truthed 2026-08-30 across four Microsoft Learn pages: `result()`'s own
expression-function reference, the *"Get context and results for failures"* exception-handling
walkthrough, the Switch and Condition how-to guides, and the control-workflow-action schema
reference). Every worked example and every prose description names `Scope`, `For_each`, `Until`.

**Do not read the nesting caveat as an answer.** The documented sentence — *"this function
returns information only from the first-level actions in the scoped action and not from deeper
nested actions such as switch or condition actions"* — describes a switch or condition **nested
inside** the named scope. It says nothing about passing a switch or condition **as** the name.
These are different questions, and the caveat's vocabulary makes it very easy to answer the
second by reading the first.

This matters because the failure-diagnosis chain this project uses — descend `result()` into the
container that failed, so an alert names the true leaf action rather than a generic wrapper — was
generalised from `Scope` (live-observed) to `Switch` and `If` (never separately confirmed) by
convention, not by evidence. The assumption is **OPEN as `A-FLOW-13`** in
`docs/development/trustee-portal-visual-refresh-dev-summary.md` §10. It closes on a designer save
without a validation error (V2) plus one live run failing inside the container (V5) — not on a
document, and not on this note. Where you need the behaviour before then, gate each call behind a
name check confirming the platform already reported that action as the one that ran and failed, so
a wrong answer degrades to the generic message instead of becoming a new failure mode.
