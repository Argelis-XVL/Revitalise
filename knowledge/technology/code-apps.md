# Power Apps Code Apps — Design Conventions

> Power Apps Code Apps are code-first apps (React + Vite + TypeScript) that run on the
> Power Apps host: the platform provides authentication, connector access, and governance;
> you provide the code. They are the **preferred UI choice** over Canvas Apps when custom
> or complex UX is required.
>
> ⚠️ Code Apps are **not** PCF controls and **not** web resources — do not use
> `pac pcfpush` or copy build output into `WebResources/`. Two CLIs exist: the **Power Apps
> CLI** (`pa`) is the current one, and the `pac code` verbs this project is built on still
> work and are announced-for-deprecation, not deprecated. See Toolchain below.

## When to Use a Code App vs. MDA vs. Canvas App

| Scenario | Preferred Choice |
|---|---|
| Process-driven internal workflow (cases, tasks, approvals) | Model-Driven App |
| Custom UX, complex layouts, or code-heavy interactions | **Power Apps Code App** ✅ |
| Simple data entry form for external or field users | Power Apps Code App (first preference) or Canvas App |
| Quick prototype / no TypeScript experience on team | Canvas App (fallback only) |

> Licensing note: Code Apps require Power Apps Premium licences for end users —
> confirm licensing before choosing this path in the TAD.

## Toolchain

Code Apps have **two** CLIs. The npm-based one is the current tool. The `pac code` verbs still
work, are on an announced deprecation clock, and are what this project's live app is built on.

| | Current | Superseded |
|---|---|---|
| Tool | **Power Apps CLI** — `npm install --global @microsoft/power-apps-cli`, commands prefixed `pa` | PAC CLI, `pac code` verbs |
| Status | Microsoft's documented prerequisite for Code Apps. Version 1.0.0 — a **new** package | Ships with Power Apps SDK v1.0.4+; the new CLI *"will replace these commands, which will be deprecated in a future release"* |
| Prerequisites | IDE, Node.js LTS, npm, Git | Node LTS **plus** the .NET-based `pac` CLI |

**Read the status wording exactly, and do not overstate it.** `pac code` is *announced for
deprecation, not deprecated*. Nothing built on it stops working today, and "superseded" above is
a statement about Microsoft's direction, not about anything breaking. Two facts keep this
honest: Microsoft's own `AGENTS.md` and the `power-apps-vite` README both still instruct
`pac code`, and every script in this repository — including the portal's own
`npm run dev` and `npm run push` — is on `pac code` right now. Treat `pa` as the emerging,
**less-validated-in-the-wild** option rather than a completed migration.

### Evidence level for everything below

**The command surface is EXECUTED ground truth** — every command, group and flag in the table was
read from `pa <group> --help` on this machine on 2026-08-22, against `pa` 1.0.0. **Runtime
behaviour is E2 (first-party documentation, status ASSUMED)**: no `pa` command has been run
against a live environment from this project.

Note the two scales and do not mix them (`skills/how-to-verify-a-platform-contract.md`):
documentation is **E2** on the evidence scale and has **no V-level at all** — `V2` means *"does
it package"*. An earlier draft of this file said *"Verification level: documentation only (V2)"*,
which mislabelled one scale as the other.

**`pa` IS installed on this machine — it is a PATH gap, not a missing install.**
`@microsoft/power-apps-cli@1.0.0` is installed globally and the binary is at
`$(npm config get prefix)/bin/pa` (here: `/Users/xvl/.npm-global/bin/pa`), which is not on
`PATH`. So a bare `which pa` reports nothing and looks exactly like an absent install — that
misreading is why this file once claimed the tool was unavailable while it sat one directory
away. Run it by full path, or prepend that directory. **Before reporting any npm-distributed
tool as absent, check `npm ls -g --depth=0` and `npm config get prefix` as well as `which`.**

| Command | Purpose |
|---|---|
| `pa auth login` · `pa auth status` · `pa auth switch` · `pa auth logout` | Sign in through the system browser; show, change and clear cached accounts. **No certificate, no `Cert:\` PSDrive.** `switch` changes the active account without logging out |
| `pa app init -n "<App Name>" -e <env-id>` | Initialise the app in the current directory; writes `power.config.json`. Also takes `-t/--app-type` (`CodeApp`\|`MobileApp`), `-b/--build-path` (default `./dist`), `-f/--file-entry-point`, `-a/--app-url`, `-l/--logo-path` — the last three matter for a hand-authored Vite project like this one |
| `pa app add data-source --connector dataverse --table <logical-name>` | Add a Dataverse table — generates a **per-table** `<Table>Model.ts` and `<Table>Service.ts` |
| `pa app add data-source … -u/--org-url <url>` | **Pass the org URL explicitly.** The flag exists precisely for the value that appears as `null` in the *"Invalid organization URL 'null' provided"* failure, so it is the first thing to try on that symptom — see Data Access & Auth below |
| `pa app add data-source --connector <id> -c/--connection-id <id> [-d/--dataset <db>] [--table <t>] [--procedure <p>]` | Add a non-tabular or SQL data source |
| `pa app add data-source --connector <id> --connection-ref <logical-name> -s/--solution-id <guid>` | Bind through a solution **connection reference** rather than a per-user connection — the environment-portable form, and the preferred one here |
| `pa app add dataverse-api --api-name <operation>` · `pa app find-dataverse-api` | Add a Dataverse action or function; search for one by name |
| `pa app refresh data-source [--name <name>]` | Regenerate a data source's files after a schema change. **Omit `--name` to refresh all** |
| `pa app remove data-source --connector <id> --name <name> [-f/--force]` | Remove a data source. `--name` defaults to the connector name when omitted |
| `pa app run` | Start the Power Apps local host; open the URL labelled **Local Play**, in the same browser profile as the tenant |
| `pa app list` | List the code apps in the environment |
| `npm run build` then `pa app push [-s/--solution-id <guid>]` | Build, then publish. `--solution-id` takes a **GUID, never a name** |
| `pa app share -p/--principal <emails-or-object-ids> [--access play\|edit]` | Share a published app. The tool's own help scopes this to *"email addresses or Entra object IDs … for the **users or service principals**"* — **groups are not named at flag level.** See the ALM section |
| `pa solution list [-s/--search <text>] [--json]` | **Lists solutions including their solution ID.** This is how you get a `--solution-id` value; `pac solution list` never shows it, and the `pac env fetch` FetchXML workaround is no longer the only route |
| `pa connector list` · `pa connection list` · `pa connection create` | Find connectors, list connections, create a connection without the maker portal |
| `pa connection list-references [-s/--solution-id <guid>]` | List connection references, optionally filtered to one solution |
| `pa connection list-datasets` · `pa connection list-tables` · `pa connection list-procedures` | Inspect a connection's datasets, tables and stored procedures. A **different command path** from `pac code list-tables`/`list-datasets`, which returned an empty `{}` against this project's connection. **Neither takes an org-url flag** |
| `pa app list-environment-variables` · `pa app list-flows` · `pa app add flow` | Environment variables and solution-aware flows available to the app. **`pa app add flow --flow-id <guid>` is how a code app calls a cloud flow**: it generates a typed service with a static `Run()` and registers the flow in `power.config.json`, which makes it a managed data source and therefore `C-TECH-048`-clean. Preconditions and limits: `power-automate.md` → *Calling a flow from a Power Apps code app*. This row listed the verb without saying what it enables, and that gap contributed to a deleted TAD design (`IMP-0303`) |
| `pa telemetry` | Manage telemetry settings |

Every command also accepts `--non-interactive`, `--json`, `--no-color`, `-e/--environment-id` and
`--cloud <public\|usgov\|usgovhigh\|usgovdod\|china>`.

Generated files land in `src/generated/models/` and `src/generated/services/`. Tabular services
expose `create` / `get` / `getall` / `update` / `delete`.

### The SDK is a separate package from the CLI

`@microsoft/power-apps` is the runtime SDK; `@microsoft/power-apps-cli` is the tool. This project
is on SDK **1.3.0**.

Its `./app` export surface is **exactly `setConfig`, `getContext`, and the `IConfig`/`IContext`
types** — read from the installed `dist/app/index.d.ts`, not from documentation. There is no
`initialize` and nothing else initialiser-shaped, so `setConfig` called once before the tree
renders is the whole contract. If you are carrying an `initialize` import or an `isInitialized`
gate from an older sample, delete it.

**An installed package's own `.d.ts` files are executed-grade ground truth and they are already
on disk.** That is a cheaper and stronger source than any documentation page, and checking it
closed assumption **A-TR-12** — open since `PowerProvider.tsx` was authored — in about a minute.

### Vite dev loop

Microsoft publishes **`@microsoft/power-apps-vite`** (1.0.2), a Vite plugin that runs the Power
Apps local host inside the normal `vite` dev server. Prefer it for new apps: this project's
portal instead runs two processes under `concurrently` (`pac code run` alongside `vite`), which
predates the plugin and is a migration candidate for whoever next touches that app's build
config.

### One tooling dead end, recorded so nobody re-spends the research

Microsoft's `PowerAppsCodeApps` repository advertises a **Claude Code plugin** in
`.claude-plugin/marketplace.json`, sourced from `./plugin/power-apps-plugin` with its homepage at
`github.com/microsoft/powerpapps-claude-plugin`. **Neither resolves** (checked 2026-08-22): that
repository 404s, the correctly-spelled variant 404s, and the `PowerAppsCodeApps` repo has no
`plugin/` directory. Most likely a manifest that shipped ahead of the plugin. Do not try to wire
it up.

## Project Structure

Each Code App lives in `src/code-apps/<app-slug>/`:

```
src/code-apps/<app-slug>/
├── src/
│   ├── components/        ← React components
│   ├── hooks/             ← custom hooks wrapping generated services
│   ├── pages/             ← route-level components
│   ├── generated/         ← models/services from `pa app add data-source` (committed)
│   ├── types/             ← additional TypeScript types
│   ├── PowerProvider.tsx  ← Power Apps SDK initialisation (generated)
│   ├── App.tsx
│   └── main.tsx
├── power.config.json      ← created by `pa app init` (committed)
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Data Access & Auth

- All data access goes through **connector data sources** added with
  `pa app add data-source` — the generated services are typed against the live schema,
  per table for tabular sources.
- Authentication is the **signed-in user's identity**, brokered by the Power Apps host
  and the user's connections. No MSAL code, no tokens, no credentials in the app for
  standard connectors (`C-TECH-048`).
- Because calls run as the user, **Dataverse security roles and column security apply
  automatically** — never build client-side authorisation logic to compensate for a
  missing role design (see `security-model.md`).
- Calling a custom external API is the only case that needs an app registration +
  MSAL — see `knowledge/technology/entra-id.md`, and isolate that code in one module.

### Aggregation — a Code App cannot compute round-level statistics client-side

**Established 2026-08-25 by reading the generator's own output on disk, which makes it E1 rather
than documentation** (`IMP-0295`). Read this before designing any dashboard, statistics screen,
distribution chart or count — the obvious design is to fetch the rows and total them in the
browser, and all three obstacles below are invisible until someone checks.

1. **No `$apply` reaches the typed services.** The generated `IGetAllOptions` in
   `src/code-apps/trustee-review-portal/src/generated/models/CommonModels.ts` accepts
   `maxPageSize`, `select`, `filter`, `orderBy`, `top`, `skip`, `count` and `skipToken` — and has
   **no `apply` member at all**, so OData `$apply` / `groupby` / `aggregate` is not expressible
   through the generated per-table services. Its `count` member carries a generated comment
   recording that Dataverse caps the value at **5000**.
2. **Column security nulls the columns a tally needs.** The app runs as the signed-in user, so
   every read is filtered by that user's profile: `rev_applicant.rev_gender` is `IsSecured=1`
   inside `REV_TrusteeRestricted`, so a trustee-side tally over it returns nothing. **Dataverse has
   no release-in-aggregate-only mode** — there is no setting that hides a column row-by-row and
   still reveals its distribution.
3. **The client caps reads below the population.** `src/dataverse/client.ts` sets `MAX_ROWS = 500`
   and raises `TruncatedListError` past it, against a round of 434 applications in the figures the
   charity actually has. Client-side totalling therefore fails at the *next* round, not at this
   one, which is the worst way for it to fail.

**The pattern.** Any aggregate over a secured column, or over a population wider than the persona's
own row filter, is computed by a **privileged identity** — a flow running as the service account,
reading on its own connection reference.

Do not widen a trustee's column security to make a chart work. That trades a real control
(`CR-01`) for a display convenience.

#### WHO computes it and WHEN it is computed are two questions. The obstacles above answer only the first

**This paragraph used to name one delivery mechanism — "written to a non-personal aggregate table
that the app then reads as ordinary rows" — and a design read the prescribed implementation as the
rule** (`IMP-0303`). Having correctly proved that a trustee's own session cannot do the counting,
ADR-025 chose a nightly batch and an intermediate table with no stated reason connecting the two,
importing staleness and a stored copy of aggregate data that no obstacle required. A table, a global
option set, a scheduled flow, a purge job, a retention rule and four provisioning items were
designed and then deleted.

Nothing in the three obstacles says anything about *when*. Both mechanisms are available:

| Mechanism | What it gives you | What it costs |
|---|---|---|
| **Synchronous, no-input instant flow** the app calls via `pa app add flow` | Live figures, nothing stored, no purge job, no retention question | One flow round-trip per view; tallying must be done in flow expressions (`List rows` has no aggregate FetchXML) |
| **Persisted aggregate table** written by a scheduled flow | Cheap repeat reads, survives flow throttling | Staleness, a table, a seed/purge story, and a stored copy of aggregate data derived from special-category columns |

**Choosing the table is a freshness decision and needs its own written justification.** It does not
follow from the privilege requirement, and an ADR that treats it as a consequence has skipped a
step. Where the figures must be current — a landing screen showing "the actual numbers" — the
synchronous route reads as the natural default, and it is first-party: see
`knowledge/technology/power-automate.md` → *Calling a flow from a Power Apps code app*, cross-linked
from the `pa app add flow` row in the CLI table above.

> **⚠ CORRECTED 2026-08-28 — the synchronous route is NOT the default here, because it does not
> work in this environment.** Binding `shared_logicflows` to this app crashed its boot, twice, and
> the row below is the mechanism that shipped instead. Read the next subsection before choosing.

#### Adding a NEW CONNECTOR to a Code App is a boot-risk change, not an additive one

**Two confirmed live reproductions, both verified in a private/incognito session, 2026-08-26 and
2026-08-27** (`IMP-0358`, `IMP-0365`, `IMP-0392`). This is the most expensive thing on this page:
it produced two live outage windows for every trustee.

Adding a new **table** to an already-connected connector is additive. Adding a new **connector
type** to `power.config.json` is not:

- `shared_logicflows` (the connector `pa app add flow` binds for a PowerApps-triggered flow) made
  the Power Apps Code App host fail at the **shell** level — *"The app didn't start correctly.
  Check that you are online, and try refreshing your browser."* The app never rendered.
- This is **a different and more severe symptom** than the `Invalid organization URL 'null'`
  family below (`IMP-0187`/`IMP-0191`/`IMP-0192`), which is an in-app data error *after* the app
  renders. A boot failure and a data failure have different causes and different fixes.
- **Eliminated as causes:** missing `prvReadWorkflow` (granted before the second attempt), the
  `workflowDetails` field (`IMP-0355`, stripped both times), and a stale or dangling push (two
  clean idempotent pushes each time). The remaining variables are the flow's PowerApps **V1**
  trigger — never tested against V2 — and a host defect in resolving any `shared_logicflows`
  reference at boot.

**Do not re-attempt this binding without a genuinely new variable** (a flow rebuilt on a
PowerAppsV2 trigger) **or a Microsoft support ticket.** A third identical attempt is the
"same scale of work, expect the same failure" pattern `IMP-0172` warns against.

**The mechanism that works: write-then-poll over a Dataverse row trigger.** No new connector, so
no boot risk. TAD §3.3's response contract was byte-for-byte unchanged — only the transport moved:

1. A single-row request table (`rev_roundstatisticsrequest`, seeded by provisioning) that the app
   **writes** (`rev_triggeredon`) through the generic-connector update path already proven for
   Save Verdict, and **reads** (`rev_status`/`rev_resultjson`/`rev_computedon`) through the typed
   per-table path every other screen uses.
2. The flow's trigger becomes *When a row is added or modified*; its final action becomes
   *Update a row* instead of *Respond to a PowerApp*. **Both are designer-only changes — no `pac`
   verb exists for either**, so they are a named human step in any environment promotion.
3. The app polls the row on a bounded schedule after writing, so the screen still feels
   synchronous, and a genuine timeout returns an explicit pending state rather than blank figures.

**The trap inside step 3, and it is a correctness bug rather than a platform one.** Deciding "a
fresh result is ready" from `computedOn !== null` is wrong the moment a poll times out while an
**older** non-null `computedOn` sits on the row from a previous cycle — that reads as fresh and
shows a stale result as current. Thread an explicit freshness flag out of the poll loop, set true
only when the row's `computedOn` is newer than the timestamp **this** write produced, and branch
every downstream decision on that flag. Any write-then-poll design against a nullable completion
timestamp has this trap: **null-checking a completion timestamp is not the same claim as
freshness-checking it against the request that most recently asked.**

**And verify every Code App push in a PRIVATE/incognito window.** The tester's regular signed-in
session served a stale JS bundle through two full push-and-verify cycles, and reported *both* a
false "still broken, same error as before" **and** a false "boots fine" in the same investigation.
A verbatim, hard-coded string match between a "live" report and old source is itself the tell that
the report is cache, not reality (`IMP-0365`).

### The generated services cannot send custom headers on a write

**Executed ground truth, `@microsoft/power-apps` 1.3.0, read from the installed package's own
shipped source, 2026-08-23.** This is the one thing to check before swapping any hand-rolled
write for a generated one.

A generated per-table service's `create()` / `update()` wrap the SDK's high-level
`createRecordAsync` / `updateRecordAsync`. **`updateRecordAsync` has a fixed three-argument
signature — `(tableName, recordId, changes)` — with no headers parameter at any layer** of the
call chain: `data/Data.types.d.ts`, `internal/data/core/types`, `internal/data/core/api/updateRecord.js`,
the operation orchestrator, and `dataverseDataOperationExecutor`. It issues a plain `PATCH`.

**Why that matters more than it sounds: Dataverse's default `PATCH` is an UPSERT.** A `PATCH`
against an id that does not exist **silently creates the row** and returns 204 — proven live
against this very app, as the negative control that closed `A-TR-10`. So "update" through the
generated service is really "update or create", and any invariant of the form *"this table's rows
are only ever created by X"* is unenforceable through it.

**The only surface that can attach connector-operation headers is the low-level
`executeAsync(connectorOperation)`** — the same `getClient(dataSourcesInfo)` object the generated
services themselves use underneath. That is how this project's Trustee Portal guarantees a
`rev_review` row is never accidentally created:

```ts
client().executeAsync({ operationName: "UpdateOnlyRecord",
                        parameters: { If_Match: "*", /* … */ } })
```

`If-Match: *` turns the upsert back into a true update-only write: a real id returns 204, a
nonexistent id returns 404 rather than creating anything.

**The rule.** Adopting the generated services for **reads** is fine and mechanically
straightforward. A **write** that depends on `If-Match`, `If-None-Match`, an ETag, or any other
connector-operation header must stay on `executeAsync` — even in an app that otherwise migrates
wholesale. Do not treat the two surfaces as symmetrical; read the installed package's own
`.d.ts` and executor source for the pinned version before assuming a high-level wrapper can
express what a low-level call does.

**This control is already defended by a test, and that is deliberate.**
`src/dataverse/client.test.ts` asserts the operation name is `UpdateOnlyRecord` and that
`parameters.If_Match === "*"` — under the heading *"so it can never create a row"* — and
`repository.test.ts` asserts the same shape in source. A migration that quietly swapped this
write path would fail both. If you are here because those tests went red, the tests are right.

### "Invalid organization URL 'null' provided" — diagnose it in this order

This one error cost a full day on the Trustee Portal, and almost every hypothesis tried was the
wrong one. It is **identical across unrelated tables**, which rules out a security-role cause
outright — a role problem returns 403 per-entity on that entity's own privileges, not the same
message verbatim.

1. **Confirm which identity the browser is actually signed in as.** Open
   `https://myaccount.microsoft.com` in a plain tab — never by following an app link first. A
   device enrolled in Microsoft's Company Portal / Enterprise SSO extension can silently
   authenticate every Microsoft sign-in, **including incognito windows**, as whatever account the
   extension last cached, with no prompt and no browser-level fix. On this Mac that cached
   identity is `svc_grantapplications`, this project's own provisioning service account. Check
   with `pluginkit -m | grep -i microsoft` and `profiles status -type enrollment`. Until this is
   settled, no app, connection or role symptom observed on this machine can be trusted as real.
2. **Pass the org URL explicitly — then check you fixed the data source the app actually calls.**

   ```
   pa app add data-source --connector dataverse --table <logical-name> \
     -u https://<org>.crm<n>.dynamics.com -c <connection-id> --non-interactive
   ```

   Verified live against DEV on 2026-08-22: it succeeded and produced real per-table models and
   services. **The tool does not resolve the organisation URL from `--connection-id` or
   `--environment-id` in this environment/connector combination — it passes `null` through
   unless you supply `-u`.** That single missing value is the defect, one layer under every
   symptom in this list.

   Two consequences worth keeping straight. `pa connection list-datasets` / `list-tables` have
   **no** org-url flag at all, so they still fail and cannot be fixed this way — do not read
   their failure as evidence the connection is broken. And the old `pac code add-data-source`
   has no such flag either, which is why re-running *it* was a confirmed no-op and why that
   no-op was mistaken for proof of a platform defect.

   > **⚠ CORRECTION, 2026-08-23 — this command changes ONLY the per-table dataset it names.**
   > This step used to end *"This is the fix, and it is confirmed working."* It was read as
   > closing the defect for the app, and it does not. The reviewer signed in as a real trustee
   > after the fix shipped and hit the identical error on all three call sites (`IMP-0224`).
   >
   > **There are TWO KINDS of Dataverse data source in one `dataSourcesInfo.ts`, they resolve
   > the organisation URL by completely different mechanisms, and only one of them is broken.**
   >
   > | | `dataSourceType: "Dataverse"` (per-table) | `dataSourceType: "Connector"` (generic) |
   > |---|---|---|
   > | Key | `rev_applications`, `systemusers`, … | `commondataserviceforapps` |
   > | Created by | `pa app add data-source --table <t> -u <url>` | the non-table `--connector dataverse` call |
   > | Called via | the generated services in `src/generated/services/` | `getClient(dataSourcesInfo).executeAsync({connectorOperation})` |
   > | Resolves the org URL from | **the app's own launch-time runtime metadata** (`metadataClient.getAppDataSourceConfigsAsync()`) | **the shared "Microsoft Dataverse" OAuth connection's org-url header** |
   > | Observed `null` for a real signed-in user? | no | **yes, every time since `IMP-0187`** |
   >
   > The right-hand column is the defect. Read from the installed
   > `@microsoft/power-apps@1.3.0` package's own `dataverseDataOperationExecutor.js`, so this is
   > a structural difference rather than an incidental one.
   >
   > **NO CLI FLAG FIXES THE GENERIC ONE. Checked directly, both tools** (`IMP-0226`):
   >
   > - `pa app add data-source --connector dataverse -u <url>` **without** `--table` exits 2 with
   >   *"Missing required option --table"*. The new CLI's `-u` has no path that ever reaches a
   >   non-table-scoped source.
   > - `pac code add-data-source -a shared_commondataserviceforapps -c <id> -env <url>` — the old
   >   CLI's equivalent flag, previously undocumented here — **does** run and reports *"Data
   >   source added successfully"*, growing the connector's `apis` block from 1858 to 3574 lines.
   >   It changes which connector **schema version** is fetched. The org URL string appears
   >   **nowhere** in the regenerated file, and `tableId` / `version` / `primaryKey` stay empty
   >   strings — because a `"Connector"` entry has **no field that could hold one**.
   >
   > **A `-c <connection-id>` written down in this repository is a LEAD, never a value to
   > reuse.** Before passing one to any command, confirm it still exists:
   >
   > ```bash
   > pa connection list -e <env-id> --json
   > ```
   >
   > A maker's OAuth connection is deleted and recreated without notice — re-authenticating, a
   > revoked consent or a rebuilt app all mint a fresh GUID — and **no document here self-updates**.
   > Two connection ids this repository records across four documents are both gone (`IMP-0489`).
   > A stale id does not fail cleanly at the point you pass it; it surfaces later as an
   > authorisation or org-URL error that reads exactly like the structural defect above, which is
   > how one gets diagnosed as the other. Confirm first, then reuse.
   >
   > **So the fix is a different data source TYPE, not a different flag.** If an app's call sites
   > use the generic connector, move them to the per-table services. That is what the trustee
   > portal did (`IMP-0227`): `client.ts`'s reads now dispatch through a `READ_SERVICES` map onto
   > `Rev_applicationsService`, `Rev_reviewsService`, `Rev_applicantsService` and
   > `SystemusersService`, while the **write deliberately stays on `executeAsync`**, because
   > `UpdateOnlyRecord` + `If-Match: '*'` cannot be expressed through the generated `update()`
   > (`IMP-0210`). A migrated app therefore ends up using **both** types on purpose — reads on
   > one, the guarded write on the other.
   >
   > **And none of that is evidence the symptom is gone.** Re-open the app as a real signed-in
   > user and re-run the calls that failed. A clean `tsc`, a clean `eslint`, a passing unit suite
   > against a mocked SDK and a zero exit from the CLI are evidence about the *files*; none is
   > evidence about the *running app*. Every prior closure in this class was made on exactly that
   > evidence while the error was still live (`IMP-0208`, `IMP-0224`).

   > **⚠ ADDING A TABLE IS THREE STEPS IN A FIXED ORDER, AND THE MIDDLE ONE IS LIVE.**
   > `IMP-0417`. `READ_SERVICES` must register the entity set for the app to compile and be
   > tested, and `pa app add data-source` **cannot** declare it in the generated
   > `dataSourcesInfo.ts` until the table EXISTS LIVE, because the verb reads the table's metadata
   > from the environment. So the order is: (1) author the entity set in source, (2) create the
   > table live, (3) run the CLI verb to bind the app. No build can perform step 2.
   >
   > The consequence is that the HARD `code-app-data-sources` gate is **correctly red for the
   > whole interval** between steps 1 and 3. The sanctioned way to say so is that step's own
   > documented mechanism, `--allow ENTITY=REASON`, with an owner and a clearing action in the
   > reason string — verified working: exit 0 with a printed *"exempt by --allow"* line naming the
   > entity and the reason. **Delete the `--allow` line in the same change that runs `pa app add
   > data-source`**, and note that doing so closes the entity-set-name assumption everywhere it was
   > guessed, at once.
   >
   > **Both tempting shortcuts are forbidden, and both look like the obvious fix.** Hand-authoring
   > an entry in `dataSourcesInfo.ts` fabricates platform-assigned connector metadata
   > (`C-TECH-051`) in the one file whose entire value is that the platform wrote it. Deleting or
   > skipping the step removes a gate whose defect is observable only at **V4** — typecheck, lint,
   > unit tests and build all pass with it present, because a mock never resolves a data source.
3. **Check the per-user connection, not the maker's.** A Code App resolves its Dataverse
   connection **per signed-in user at runtime**: `power.config.json`'s `connectionReferences`
   entry is a local manifest key with no `connectionId` and no corresponding Dataverse
   `connectionreference` row (confirmed by querying every such row in the org and finding none).
   So a maker deleting and recreating *their own* connection never touches a different user's
   binding. Ask whether **that** user has ever created a Microsoft Dataverse connection at
   `make.powerapps.com/connections`.
4. **Verify the role grant including team-inherited roles.** `systemuserroles` alone will not
   show a role inherited via a team — join `teamroles`.
5. **Escalating to Microsoft support is no longer the recommended answer for this symptom, and
   that is a correction.** A standing recommendation in this project said to raise a support
   ticket for *"Invalid organization URL 'null' provided"*, on the reasoning that identity, role
   grant and per-user connection had all been verified and every local avenue was exhausted.
   They had not been: **step 2 fixes it locally**, and none of the six findings in that
   diagnosis had tried passing the org URL explicitly.

   Keep the support route for a symptom that survives steps 1–4 *with `-u` supplied* — quote the
   original error's `OperationId` and `ClientRequestId` for correlation. But do not open a ticket
   for this error without trying step 2 first.

   **The transferable lesson is the one worth remembering.** "Every local cause is exhausted" was
   wrong because the diagnosis never checked whether the tool exposed an override for the exact
   value the error named as `null`. When an error message names a specific missing value, search
   the CLI's own `--help` for a flag that supplies it before concluding the platform is at fault.

> ### ⚠ CORRECTED 2026-08-28 — and this narrows the advice above as well as `IMP-0191`'s
>
> **`IMP-0360`.** Two things in this section were understated, and Microsoft's own maintained
> sample settles both.
>
> 1. **The escalate-to-support conclusion is withdrawn outright**, not merely deprioritised. It
>    was `IMP-0191`'s recommendation and it was wrong.
> 2. **"The only fix is a different data-source TYPE" is too strong.** A GENERIC connector
>    operation is fixable **at the call site**: resolve the org URL once from
>    `getContext().app.dataverseOrgUrl`, then call the ***WithOrganization*** variant of every
>    operation with it. Every generic Dataverse operation has such a variant. This app's
>    `src/dataverse/client.ts` now does exactly that.
>
> **The cheap step this whole diagnosis skipped, and the reason it is now step 0:** when a Code
> Apps connector symptom looks unfixable after checking identity, role and connection, **read
> Microsoft's own public sample for the same connector before escalating.**
> `github.com/microsoft/PowerAppsCodeApps/samples/Dataverse` and `…/samples/DataverseConnector`
> are real, maintained, directly comparable app structures — not documentation, and not a forum
> post. `samples/DataverseConnector/src/dataverse/client.ts` is the reference implementation for
> the pattern above. Six findings' worth of diagnosis preceded a fix that was readable in a
> sample the whole time.

Useful throughout: `pac env fetch -xf <file>` runs an arbitrary **read-only** FetchXML query
against Dataverse under the currently selected `pac auth` profile — no `PROVISION_APP_ID` or
certificate needed. It is how you read a solution's real `solutionid` when the cert identity is
not loaded in the shell, and how to join `teamroles` for step 4.

## Naming Conventions

| Element | Convention | Example |
|---|---|---|
| App folder name | `<app-slug>` (kebab-case) | `case-portal`, `onboarding-app` |
| App display name | `[PREFIX] <App Name>` | `PROJ Case Portal` |
| React component files | PascalCase `.tsx` | `CaseDetailPanel.tsx` |
| Hook files | camelCase `.ts`, `use` prefix | `useCases.ts` |
| Type files | camelCase `.ts` | `caseTypes.ts` |
| Route paths | kebab-case | `/case-detail/:id` |

## Vite Configuration

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "./",
  server: {
    host: "::",
    port: 3000,          // the Power Apps local host expects port 3000
  },
  build: {
    outDir: "dist",
    sourcemap: false,    // never ship sourcemaps to a shared environment
  },
});
```

## ALM — How a Code App Moves Through Environments

**Prerequisite, once per environment, by a human.** *Power Apps code apps* is a per-environment
product feature and it is **off by default**: Power Platform admin centre → Environments →
`<env>` → Settings → Product → Features → **Enable code apps**. There is no CLI verb and no
organization attribute for it, so no script in this repository can set it or read it back, and a
push into an environment where it is off fails. A System Administrator or Environment
Administrator does this once, before the first push. This stopped a DEV deploy on 2026-08-22.

1. **Dev.** `npm run build`, then `pa app push`. On the **first** push the CLI places the app in
   a solution by itself: the environment's *preferred* solution, else the all-components Default
   solution, else no solution at all if Dataverse is absent. Set a preferred solution for the
   environment, or pass `--solution-id <guid>` and be explicit.
   **Only a GUID is accepted — a solution name is not.** Read the GUID with
   **`pa solution list`**, which prints solution IDs (add `--search` to filter, `--json` to
   parse); `pac solution list` does not show them, and the `pac env fetch -xf` FetchXML query or
   the maker-portal URL are the fallbacks when only `pac` is available.

   ⚠️ **This is a live migration trap.** The pipeline's push step passes a solution *name*
   (`pac code push --solutionName RevitaliseGrantAutomation`). The replacement command takes only
   a GUID, so that step fails on migration until someone reads the real id.

   ⚠️ **And `pac code push --solutionName` does not do what it says on this tenant.** Verified
   live: 49 `solutioncomponents` on the target solution and the pushed app's `appId` absent from
   all of them. The confirmed route to get a Code App into a named solution here is the maker
   portal's **Add existing component**. So treat every environment as needing its own push plus
   that manual step, not a managed-import ride-along.
2. **Later pushes** do not change solution membership unless `--solution-id` is passed again.
3. **Promotion.** The code app is a solution component and travels in the managed solution
   through Test/Acc/Prd like every other component. Code apps do **not** support Power Platform
   Git integration or source-code integration — the solution is the only transport.
4. **Environment-independent data sources.** Prefer a connection reference (`--connection-ref`
   with `--solution-id`) over a per-user connection, and `@envvar:<schema-name>` for dataset and
   table arguments, so one app resolves correctly per environment. Note what this changes: a
   `connectionReferences` key written by `pac code` is a **local manifest key only**, with no
   corresponding Dataverse row; `--connection-ref` binds to a real solution component.
5. **CI/CD push, when the solution route is not used.** Set `PA_CLI_USE_SP_AUTH=true`,
   `SP_CLIENT_ID`, `SP_CLIENT_SECRET`, `SP_TENANT_ID`, then `pa app push --non-interactive`.
   **A maker must first share the app with the service principal at `edit` access — a service
   principal cannot grant itself access, and environment-level permissions are not enough.** Use
   the **Enterprise application** object ID, never the App registration object ID. This is a
   one-time human step, not a pipeline step.
6. **Sharing.** Share with the persona's **Entra security group**, never with individual users in
   Test/Acc/Prd (see `security-model.md` → App Access).
   ⚠️ **Group sharing is the one real gap in this migration.** `pa app share --principal` is
   scoped **by the tool's own `--help`** to *"email addresses or Entra object IDs … for the users
   or service principals"* — groups are not named at flag level. That is stronger evidence than
   documentation silence, though still not a test: a group object ID *is* an Entra object ID, so
   it may work. `share-apps.ps1`'s code-app branch does take a group explicitly
   (`-PrincipalType Group`) but **cannot run on this Mac** — it fails both on an assembly
   conflict with the model-driven branch's MSAL token acquisition and on the absence of the
   Windows-only `Cert:\` PSDrive (`X509Store` is the portable route, per `C-TECH-054`). **Until
   `pa app share` is tested with a group object ID, treat group sharing as a maker-portal
   step**, and do not record `pa app share` as a replacement for that script. For individual
   users and service principals, `pa app share` does replace it — and it runs here.

### Why the generated Dataverse service did not compile

Executed ground truth, `pac` 2.4.1, 2026-08-21, re-inspected 2026-08-22. Kept as a historical
record: it explains the hand-written client in this repository, and it is the evidence behind an
upstream bug report.

> **CORRECTION, 2026-08-22 — the per-table typed route is NOT closed.** Everything below is
> accurate about `pac code`, and the conclusion drawn from it at the time — *"the typed route is
> unreachable in this environment"* — was **wrong**. It was the same missing org URL as every
> other symptom on this page. Supplying `-u` reopens it:
>
> ```
> pa app add data-source --connector dataverse --table <logical-name> \
>   -u https://<org>.crm<n>.dynamics.com -c <connection-id> --non-interactive
> ```
>
> Run for `rev_application`, `rev_review`, `rev_applicant` and `systemuser` against DEV: all four
> succeeded and produced real per-table models and services. **None of them carries the
> `MSCRM.IncludeMipSensitivityLabel` parse defect** described below — confirmed by grep and by a
> clean `tsc --noEmit` and `eslint .` across the whole app. So per-table generation does not
> merely avoid the defect by luck; it never surfaces that parameter.
>
> The route was never structurally closed — only blocked by the identical org-url-null failure,
> through a CLI that had no flag to fix it. **Before recording a platform route as unreachable,
> establish that the blocker is the route and not a missing parameter you can supply.**
>
> This project's Trustee Review Portal still uses its hand-rolled generic-connector client
> (`src/dataverse/client.ts`) **by choice**, recorded in that app's own
> `src/dataverse/README.md` — not because the typed route is unavailable.

- `pac code init` created only `power.config.json` — it did not scaffold React, so the Vite
  project here is hand-authored.
- `pac code add-data-source` generated the **generic** Dataverse connector typing with no
  per-table models, and `pac code list-tables` / `list-datasets` returned an empty `{}` on all
  three dataset forms against this connection — which was read at the time as the typed route
  being unreachable, and was really the missing org URL (see the correction above).
- The generated `MicrosoftDataverseService.ts` **does not compile**: a parameter named
  `MSCRM.IncludeMipSensitivityLabel` becomes a TypeScript identifier, and `.` is not legal in
  one. The workaround is `getClient(dataSourcesInfo)` from `@microsoft/power-apps/data` — never
  editing generated output.

**That last one is a `pac code` generator defect, not a connector-schema problem.** The same
parameter object in the connector schema already carries
`"x-ms-name-for-model": "mscrm_include_mip_sensitivity_label"` — a valid, dot-free identifier
whose whole purpose is to name generated code. This repo's copy of the schema carries **185** of
these hints. The generator uses the raw wire name and never falls back to one. The failure is
absent from the Code Apps overview's five documented Limitations, so it is an unreported tool
defect: raise it at <https://github.com/microsoft/PowerAppsCodeApps/issues>, which that overview
names for feedback and guidance. For a fix commitment on a bug, the same page directs you to the
standard Microsoft support channel instead.

Two consequences. The `pa` CLI uses a **different** generator, so the defect may simply not exist
there — untested. And per-table generation may never surface that parameter at all, in which case
the defect is obsoleted rather than fixed, and its upstream priority is correspondingly low.

## Design Rules

### State Management
- Use **React Query** (`@tanstack/react-query`) around the generated connector
  services for caching, retries, and invalidation
- Avoid global state libraries (Redux, Zustand) unless the app complexity requires them
- Keep component state local; lift to context only when shared across multiple subtrees

### TypeScript
- Strict mode enabled (`"strict": true` in `tsconfig.json`)
- No `any` types — use `unknown` with type guards instead
- Do not hand-edit files in `src/generated/` — re-run `pa app refresh data-source --name <name>`
  on schema change

### Styling
- Use **CSS Modules** or **Tailwind CSS** — one approach per project, set in `stack-overview.md`
- No inline styles except for dynamic/computed values
- Fluent UI v9 (`@fluentui/react-components`) for components that must match Power Platform visual language

### Before you add a shared primitive, find the component that already renders those blocks

**A design document names blocks by their business meaning and hides the single implementation
seam.** So a requirement stated per-block reads as three or four decisions and is very often one
property on one class. Grep for the components that already render the content the requirement
describes, *before* writing a new class, hook or wrapper:

```bash
grep -rn "<the CSS class or component the existing blocks share>" src/code-apps/<app>/src/
```

Measured on this app (`IMP-0311`): a TAD asked for a narrow measure on the redacted-narrative
panel, the score breakdown and a not-yet-built care-support panel as if each needed deciding
separately. All of them — plus the staff recommendation panel the TAD never mentioned — render
through one component, `components/Panel.tsx`'s `MultilineText`, which applies exactly one class,
`.preserveLines`. One property on that class satisfied every existing block and will satisfy the
fourth for free once it renders through the same component. No component file was touched.

### Re-derive from source; never trust a transcription

**Any value in app source that was copied out of solution source is asserted against its origin
at test time, not spot-checked.** Option-set label maps, entity-set names, column lists: the copy
is the thing that drifts, and a drift with nothing rendering through it has no symptom at all.

`IMP-0330` is the shape. `BREAK_TYPE_LABELS` was stubbed as `{}` with a comment recording the
*stub's* reason as a *fact about the option set* — "a placeholder set" — while that option set had
carried five real authored labels in solution source for as long as the file existed. Nothing
rendered through the map, so nothing disagreed. `schema.test.ts` now re-derives **all six** label
maps from `OptionSets/*.xml` rather than trusting any transcription, which also means a solution
import that silently relabels an option value (`IMP-0019`) fails a test instead of rendering
plausible wrong text.

Two habits follow. A comment about a stub says it is about the stub. And a transcription gets a
test that reads its source, in the same commit as the transcription.

### Accessibility
- All Code Apps must meet WCAG 2.1 Level AA
- Use semantic HTML elements; ARIA attributes only when native semantics are insufficient
- Keyboard navigation must work end-to-end before code review

#### Fluent v9's default theme is NOT accessible for an arbitrary brand ramp

**Computed pair by pair against the real ramp, 2026-08-26** (`IMP-0352`). Caught before any push;
it would have shipped a WCAG 2.1 AA failure on **every** primary button in the app.

`createLightTheme` does not guarantee AA, and the claim that "Fluent's own default theme is already
accessible by design" is true of **Fluent's own blue ramp** (`brand[80]` = `#0f6cbd`, 5.38:1 against
white) and does not generalise. Fluent's alias layer pins `colorBrandBackground` and
`colorBrandBackgroundStatic` to `brand[80]`, while `colorNeutralForegroundOnBrand` is a **hard-coded
white**. So:

> **AA compliance of the primary button is a property of the RAMP, not of Fluent.** Any brand whose
> shade 80 falls between 3:1 and 4.5:1 against white ships a failing button.

This charity's `#ED008C` gives `brand[80]` at **4.22:1** — under the 4.5:1 floor for normal-size
text, which is what a button label is.

**Before adopting any ramp:** compute white-on-`brand[80]`. If it is under 4.5:1, move **both** rest
tokens to `brand[70]` *and* shift Hover/Pressed/Selected one step with them — otherwise rest and
hover resolve to the same colour and the button loses all hover feedback.

**Never accept a general statement that a palette "is accessible", including from a human.** The
supplied brand guidance here said "use white when text sits over one of the other colours"; white on
the supplied accent `#14ADBB` is **2.72:1**, which fails normal text *and* fails the 3:1 large-text
and UI-graphic floor, so no size of white text is usable on it. Both defects were found only by
computing every pair individually.

The working implementation is `src/code-apps/trustee-review-portal/src/theme.test.ts` — 26
assertions, wired into the build through the `code-app-coverage` step. **Copy that file into the
next Code App**; nothing currently requires it to exist, which is this lesson's open residual.

### Error Handling
- All connector calls wrapped in try/catch; errors surfaced to the user via a
  toast/notification, not a blank screen
- Log errors to `[prefix]_flowexceptionlog` (via a Power Automate cloud flow) for
  server-side traceability

## Testing

See `knowledge/technology/testing-tools.md` for the full test stack.

Summary:
- **Unit**: Vitest + React Testing Library — test components in isolation with mocked
  generated services
- **Integration**: Vitest against a real Test environment
- **E2E**: Playwright — automate the full app flow in a browser against the Test environment

---

## Eleven lessons from the trustee portal, 2026-08-26 → 08-28

Added by improvement review 33. Each is one instance whose **cause is general**, which is why
these are knowledge lines rather than gates: no two share a mechanical surface. Grouped by the
moment they bite.

### Wiring a Code App to a Power Automate flow — three traps, in the order you meet them

**1. Check the flow's TRIGGER KIND before you run `pa app add flow` at all** (`IMP-0359`). Read
`properties.definition.triggers.<name>.kind` in the flow's own workflow JSON. `PowerApp` (V1) is
the legacy **Canvas-App-only** trigger, and on this project's evidence its connection cannot be
established or shared through **any** UI reachable for a Code App: no connector appears in the
Connections gallery, and the *"Run only users"* tab does not apply. Recreate the trigger as
`PowerAppV2` first.

Be honest about the level here: **converting the trigger is the identified variable, not a proven
fix.** It is the one thing this project has not tried. Re-adding `shared_logicflows` without
resolving the trigger version would very likely reproduce the same boot failure.

**2. After `pa app add flow`, strip `workflowDetails` from `power.config.json` before
`pac code push`** (`IMP-0355`). `pa` writes a `workflowDetails` member into the new
`connectionReferences` entry; `pac` 2.4.1's code-push `PUT` **rejects it outright** with
`HTTP 400 InvalidRequestContent`, naming `AppConnectionReference` as a type with no such member.
Keep `id` / `displayName` / `dataSources` and delete the rest.

**This is a repeat-every-time step, not a one-off fix.** Any later `pa app add flow` or
`pa app refresh data-source` writes the field back in.

**3. Do not trust the generated service's RESPONSE TYPE as proof of what the flow returns**
(`IMP-0356`). A `void`-typed `Run()` does not mean an empty response: observed `void`/202 typing
against a flow carrying **five** `200`-with-body Response actions. Read the flow's own Response
actions (`type: Response`, `kind: PowerApp`) for a real `statusCode`/`body` before designing
against the type. Reading the actual runtime value rather than the static type is the robust
shape — `src/dataverse/roundStatistics.ts`'s `extractResponseText` already does this. Confirming
which is true needs a **live, signed-in invocation**; nothing local can tell you.

### Two generator and host defects, so nobody re-diagnoses them

**The generated `MicrosoftDataverseService.ts` does not parse** (`IMP-0361`). Line 496 uses
`MSCRM.IncludeMipSensitivityLabel` as a **bare JavaScript identifier**, which is a syntax error.
Before assuming a generated file's escape-hatch workaround is a style choice, check whether the
generated class actually parses. This blocks all 30+ typed methods on that class, not only the one
an app needs — a genuine upstream-issue candidate against
`github.com/microsoft/PowerAppsCodeApps`. `src/dataverse/README.md` documents it at file level;
this records the identifier and the line.

**A Vite-imported binary asset referenced via `import.meta.url` does not resolve in the Code App
host** (`IMP-0362`). `index.html`'s own build-time-baked relative paths do resolve. So **use the
`?inline` import suffix** for any binary asset a Code App bundles *from application code*, rather
than leaving it as a hashed, separately-emitted file with a runtime `import.meta.url` reference.
Applies to every binary asset any code app in this solution bundles.

### Self-hosting a named typeface — check `@fontsource` BEFORE calling it an unmet dependency

**Added 2026-08-31, `IMP-0513` — a capability, not a defect.** When a supplied design system names
a typeface, **check whether that face is a published Google Font available as
`@fontsource/<slug>` on npm before recording it as an external dependency waiting on the
reviewer.** For an open-source face that package *is* the supply: it ships the real font files
under the **SIL Open Font License 1.1**, which explicitly permits embedding and redistribution,
and it includes the licence text in the package itself.

```bash
npm view @fontsource/<slug> version license   # e.g. playfair-display -> 5.3.0, OFL-1.1
```

**The caveat is the load-bearing half of this entry, not a footnote.** It applies **only** to
open-source faces. A proprietary or commercially licensed face — **Aptos**, this project's
`--font-body` — is not on `@fontsource` under any slug, and reviewer-supplied files plus a
licence remain the only route there. Do not read this as "fonts are always obtainable".

**Bundle the result as a base64 `data:` URI inside the `@font-face` rule — never a relative
`url()`** to a separately emitted asset. This is the `A-BRAND-1` precedent and the same host
defect as `IMP-0362` above: the Power Apps Code App host does not reliably resolve a second
fetched file at runtime. Copy only the weights and subsets your call sites actually render, and
put the OFL licence text next to the files.

Worked example on this project: ADR-036/ADR-042 carried *"real font files, or a licence permitting
redistribution"* as an unmet external dependency (`A-R53`) across multiple TAD revisions, blocking
`--font-display`. Two static weights of Playfair Display (400 and 700, latin, normal) from
`@fontsource/playfair-display@5.3.0` closed it — the dependency was one `npm view` away for as
long as it was recorded as blocked.

### Testing — four ways to read a green result as more than it is

**Run ONE vitest file with `npm --prefix <app> run test -- <path>`. Never
`npm --prefix <app> exec -- vitest run <path>`** (`IMP-0394`). The `exec` form **does not
discover the app's `vitest.config.ts`**, so its `server.deps.inline` entries vanish and
Fluent/tabster fails to load as ESM. A green or red result from an invocation path the build never
uses is evidence about neither the code nor the build — `IMP-0026`'s rule, applied to a
single-file run.

**A stale `node_modules/.vite` cache reproduces a fixed defect verbatim** (`IMP-0370`). Before
treating `Cannot find module .../dist/data/multiSelectPicklistUtils` — or any
`@microsoft/power-apps/dist` internal-import failure — as real, run `rm -rf node_modules/.vite`
and re-run. `vitest.config.ts`'s `server.deps.inline` already documents and fixes this class, and
the cache can show the pre-fix symptom **while the fix is correctly in place**. Never hand-patch
`node_modules` around it: untracked, does not reach CI, and the real fix is one directory
deletion.

**A component test proves which class KEY was asked for, and NOTHING about the stylesheet**
(`IMP-0386`). Vitest processes no CSS, and its CSS-Modules stub is a **Proxy that fabricates a
class name for any key** — so a class-name assertion is a tautology that any claim satisfies.
Split the two halves deliberately: assert the key name as a substring in the component test, and
assert the rule's existence and content by **reading the stylesheet off disk** (the technique at
`theme.test.ts:266-329`). Never read a green class assertion as evidence that a style ships.

**A test asserting a NON-SUCCESS outcome under the shipping default is a specification claim, not
a regression guard** (`IMP-0511`, blocker). When a test's own title or comment names the
configuration it runs under as the shipped one, and its assertion is `pending`, `null`, `withheld`
or any other not-ready state, it is **not** guarding behaviour — it is transcribing a design
sentence into an assertion, and it will stay green for exactly as long as the defect lives.

**Make it quote the design sentence it implements**, by reference, in the test itself. Then the
check is available to any reader: does that sentence describe the same user-visible outcome the
test asserts? Where it does not, the test is **pinning the defect rather than catching it**, and
the green run is evidence of nothing at all.

`roundStatistics.test.ts` is the worked example. It ran the full write-then-poll cycle, titled
itself *"case 4 — S null: always recompute, even over a document one second old"*, commented that
this was *"the SHIPPING configuration"*, and asserted `status === "pending"`. The design sentence
it was written from said the unseeded state means *always recompute*; what the code did with a
null bound was *never return a computed result at all*. The test could not have failed, the
feature was invisible from the day it shipped, and the test suite reported that as correct.

### TypeScript — a CSS-Modules class is `string | undefined`

`IMP-0387`. `vite/client.d.ts` types a CSS-Modules import as an **index signature**, so under
`noUncheckedIndexedAccess` every class lookup is `string | undefined`. A map of class names is
`Record<K, string | undefined>`, and a **filtering join** is what keeps the literal string
`"undefined"` out of a `class` attribute.

The process half matters as much: when a TAD prescribes a type annotation verbatim, check it
against the declaration file of the thing being annotated **before** writing it — and when it does
not compile, **ship the working form and report the deviation. Never weaken the `tsconfig`.**

### Fluent UI — a compound widget may pass state through private React context

`IMP-0388`. Before replacing a compound widget's CHILD while keeping its Fluent PARENT, check
whether the parent passes state through **React context** rather than through the DOM: grep the
library for a `*Context` module and see which component consumes it.

Fluent v9's `RadioGroup` publishes `name` and `checked` through `RadioGroupContext`, and **only
Fluent's own `Radio` reads it.** A look-alike child therefore renders `name=null` on every input —
and single-selection, arrow-key traversal and the roving tabindex all derive from that shared
`name`. Losing them is a WCAG 1.3.1 / 2.1.1 / 4.1.2 regression **that still looks correct on the
first click**, which is why inspection misses it.

So verify a child swap by rendering **both** children inside the parent and comparing the DOM
attributes the browser depends on — `name`, `checked`, `aria-*` — never by reading the child's own
props. The same question applies to every Fluent group/child pair: `Field`, `Accordion`,
`Tablist`, `MenuList`.

### And the correction that belongs with these

`IMP-0360` withdrew this file's escalate-to-support recommendation for *"Invalid organization URL
'null' provided"* and narrowed the standing data-source-type advice. It is marked in place in the
**Data Access & Auth** section above rather than repeated here, because a correction appended
somewhere else is a second claim rather than a fix.
