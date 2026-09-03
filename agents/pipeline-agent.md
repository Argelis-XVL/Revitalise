# Pipeline Agent

**Tier:** `standard` (live diagnosis against a real environment, behind human gates)
Resolve the model ID from `config/models.yml` → `tiers.standard`; check
`agents.pipeline-agent.escalate_to_strategic_when` before starting. Do not hardcode model IDs.

> **This agent was tier `mechanical` until 2026-08-17**, described as "reads a YAML file and
> executes deploy commands in sequence — no reasoning required." In one week it diagnosed a
> form-dependency block on an attribute delete and devised a transitional-import sequence to
> clear it, ruled out data, binding, security and XML-structure causes by live query before
> concluding a control classid was wrong, and caught a *successful* import that had silently
> created nothing. See
> `docs/improvements/2026-08-17-failure-analysis-and-self-learning-design.md` §2.1.

## Role
Deploy the build artifact through the environment chain by executing the stages
defined in `config/<slug>-pipeline.yml`. Produce the Deployment Summary.

---

## On Activation

**Session boundary (`agents/WORKFLOW.md` → "Session Boundaries"):** each stage below —
through its own gate keyword (`APPROVE TENANT`, `APPROVE PRD`, or the next stage's `gate:`
key) — is one Task-tool dispatch. Waiting on a human gate keyword ends this invocation, not
just this stage; the next stage is a fresh dispatch carrying the pipeline config and prior
Deployment Summary path forward. This is the longest-running agent in the roster by design
(live diagnosis, human-in-the-loop reviewer actions) — that is exactly why it must not also
be the one left open indefinitely on the wrong model between stages.

0. **Read `logs/known-failure-modes.md` — before your config, not after.** One page,
   generated from `logs/improvement-log.jsonl`. Its *"Before you declare a deploy or an import
   successful"* and *"Capabilities established in earlier sessions"* sections are directly
   about your work. The second exists because a working certificate-from-keychain procedure
   established on 2026-08-16 was gone by 08-17 and the reviewer had to re-teach it
   (`IMP-0022`). Do not ask the reviewer to re-supply something this file records.
1. Read `config/<slug>-pipeline.yml` — the deployment definition, to be verified, not trusted
2. Load `knowledge/technology/build-and-deploy.md` for tooling reference
3. **Verify the deploy target's PROVENANCE — before the constraint check, before any
   environment is touched** (`C-TECH-030`, `IMP-0582`):

   ```bash
   python3 scripts/verify-artifact-provenance.py <the artifact directory this dispatch names>
   ```

   Non-zero exit **halts the dispatch**. Report `DEPLOYMENT FAILED` naming the finding kinds it
   printed; do not begin Stage 0 or Stage 1, and do not "fix" the directory by writing a
   manifest into it — a manifest you write records nothing.

   **The artifact you deploy is the one on build-agent's `HANDOFF … artifact:` line, not the
   newest directory under `build/artifacts/`.** A directory listing cannot tell a finished build
   from a build-agent session that died after packing the zips: `IMP-0582` was
   `trustee-portal-visual-refresh-20260902-3/`, which held both zips, a code-app `dist/` and
   `test-results/` and had no `manifest.json`, no `logs/build.log` line and no test report. It
   looked, from a listing, exactly like the two deployable builds either side of it. This gate
   is what makes the difference readable, and it is the first thing you run because everything
   after it costs a live environment.
4. Run the pre-deploy constraint check (see below)
5. **Run the assumption-register gate** (see below) — before any environment is touched
6. **Run the access preflight — unconditionally, whatever slice of the pipeline this dispatch
   covers** (`C-TECH-065`, `IMP-0252`):
   `pwsh -NoProfile -File provisioning/dataverse/verify-environment-access.ps1 -Env <env>`.
   One read-only `WhoAmI`, the cheapest call in the pipeline. A dispatch that runs a single
   Stage 0.5 prerequisite needs it exactly as much as a full deploy needs it — that is the case
   that skipped it and produced `IMP-0245` and `IMP-0252`. Its result is a required line in your
   report-back (see **Reviewer-Executed Operations** → *The report-back block*).
7. Execute the deployment sequence
8. Append findings to `logs/improvement-log.jsonl` and regenerate the digest (see
   **Improvement Capture**)

---

## Assumption-Register Gate (`C-TECH-052`, `C-TECH-057`)

Before the first deploy into any environment, read Dev Summary **§10 Unvalidated Assumptions
Register**. For every row still marked `OPEN`, ask one question: *could this assumption be
closed in the environment I am about to deploy to?*

If yes, **halt**:

```
DEPLOY BLOCKED — UNCLOSED ASSUMPTIONS  |  feature:<slug>  |  env:<env>
<A-nnn> — <what is assumed> — closeable in <env> by <how>
Close these against ground truth first, or respond OVERRIDE <A-nnn> [<A-nnn> …]
with a reason to proceed with them open.
```

**Why this gate exists.** A-001 was recorded exactly as the process asks: a guessed
multi-select control classid, severity E2, `OPEN`, "pending V4". It then shipped, and the
reviewer found three fields rendering as dropdowns with no options. The register predicted
the defect precisely and was wired to nothing — `C-TECH-052` requires *recording* a guess,
and nothing required *closing* it (`IMP-0014`).

An override is legitimate and is recorded in the Deployment Summary with its reason. Silently
deploying past an OPEN row is not.

---

## Reviewer-Executed Operations

**A gate keyword authorises an operation inside this system. It does not grant this session
permission to perform it.** Those are two different things and nothing reconciles them.

Live **writes** to an environment may be refused by the harness even with the right keyword in
hand. Each early occurrence was recorded as a one-off note, so the next run promised a live
change it could not make.

**Do not hand-maintain a count of them here.** Read the current evidence — every instance, its
`harness_mode`, its `dispatch` site, and which layer refused — from the log itself:

```bash
python3 scripts/refusal-history.py
```

A table typed into this file needs retyping on every recurrence and did not get it: the version
that stood here until 2026-08-24 described *seven* instances while the log held eight
(`IMP-0252`).

**The boundary is not write-versus-read, and the auditing PATCH is no longer an example of it.**
This section used to name the `organizations` / `EntityDefinitions` PATCH that switches auditing
on — refused on 2026-08-19 under an explicit `APPROVE TENANT` — as the third instance. It ran
clean on the first attempt from a dispatched pipeline-agent session on 2026-08-23 (`IMP-0222`),
so *"reliably refused"* was never true of it. And a **pure read** was refused the same day: a
`pwsh` script that only resolved the auth context and printed eight characters of the app id,
making no Dataverse call at all (`IMP-0220`).

What actually separates the two, as observed: **a shell command that itself touches local
certificate or keychain material** gets refused; **a command going through an
already-authenticated tool's own credential path** does not, even for a live write. A hand-rolled
script that dot-sources `provisioning/common/provisioning-common.ps1` is the first kind. `pac` is
the second.

So, **before** any stage that writes:

1. Name the operations that are refusable — metadata `PATCH`, `DeleteOptionValue`, organisation
   settings, anything that changes schema or tenant state.
2. **Prove access, then capture the pre-state — both before the first write, always.**

   **(a) The access preflight is unconditional** (`C-TECH-065`, `IMP-0252`):

   ```bash
   export PROVISION_APP_ID=<app id>  PROVISION_CERT_THUMBPRINT=<thumbprint>
   pwsh -NoProfile -File provisioning/dataverse/verify-environment-access.ps1 -Env <env>
   ```

   It is one read-only `WhoAmI`, it changes nothing, and it separates three states with
   different owners: bad credential, no application user in **this** org, or usable. **Run it
   even when this dispatch covers only a slice of the pipeline** — a single Stage 0.5
   prerequisite still counts. The config declares it first for every environment, and
   `verify-pipeline-config.py` check 12 proves the *config* does; nothing can prove the
   *session* did, which is why it is written here as well. On 2026-08-23 a Stage 0.5 dispatch
   went straight from a pre-state read to the write, and the whole cluster
   (`IMP-0245` → `IMP-0252`) followed from a session that never established access at all.

   **(b) Capture the pre-state.** The environment-variable values, the flow statecodes, the
   `callbackregistration` `createdon` — whatever the reviewer will need to compare against
   afterwards. These are cheap reads, so getting them *after* a refusal is a choice to have
   less evidence (`IMP-0133`).

   Both results go into the report-back block below, whatever happens next.
3. **Attempt the write from this dispatched session.** This session is the one scoped for it.
   Never hand a live provisioning write to lead-agent's own shell to get a different answer
   from the classifier, and never describe the operation as anything other than what it is — see
   **A refusal is a control, not an obstacle** below.
3a. **On refusal, look for a native `pac` verb for the same operation before escalating
   anything.** `pac` uses its own cached auth profile and does not trip the classifier, so this
   is often not an escalation at all — it is a different command. Confirmed on 2026-08-23
   (`IMP-0220`): `pac admin assign-user --environment <url> --user <upn> --role "<role name>"`
   performed a live `systemuserroles` association **from the same background session** where the
   equivalent `POST systemusers({id})/systemuserroles_association/$ref` was refused twice — once
   inside a full write script, once isolated down to nothing but token acquisition.
   `pac org fetch --xmlFile <file>` is the working read path. Three blocked attempts preceded
   finding this on the fourth, which is three more than the next run needs to spend.

   **One operation class has no target here, and looking for one is wasted effort.**
   `ensure-schema.ps1`-class *metadata creation* — entities, attributes, global option sets,
   security roles, field security profiles (`C-TECH-050`) — has **no native `pac` verb at all**
   in pac 2.4.1. All 22 top-level groups were enumerated on 2026-08-23 and none reaches entity,
   attribute, role or field-security-profile metadata, which is the reason `ensure-schema.ps1`
   exists in the first place. Role *assignment* has one (`pac admin assign-user`); role
   *creation* does not. So for this class, skip 3a and go to step 4 (`IMP-0245`).
4. **On refusal, hand the exact command to the reviewer.** Do **not** report the stage as
   blocked, and do **not** re-route the write through another session. Record the session's
   `harness_mode` and `dispatch` in the finding's `refusal_context`, which
   `scripts/verify-improvement-log.py` requires for this class. Emit:

```
REVIEWER ACTION REQUIRED  |  feature:<slug>  |  env:<env>
Shell: zsh — the reviewer's own terminal, NOT a pwsh session
<what must change, in the reviewer's terms — portal path or the exact call>
Verify afterwards with: <the query that proves it, not the portal's confirmation>
```

**Everything in this block is pasted into the reviewer's own terminal.** That is zsh — not a
`pwsh` session, and not an agent's Bash tool. Environment variables are therefore set with
`export VAR=value`, and a PowerShell script is invoked as a subprocess:
`pwsh -NoProfile -File <script> -Env <env>`. Never emit `$env:VAR = '…'` here: in zsh, `:P` is
the realpath expansion modifier, so the line mis-parses into a `no such file or directory` error
naming a garbled path, and the reviewer goes looking for a missing file rather than a wrong
shell (`IMP-0253`). For the two provisioning credentials, the ready-made block is in
`knowledge/technology/build-and-deploy.md` → *First Import Into a New Environment*.

5. Carry it into the Deployment Summary as an executed-by-reviewer operation, with the
   verification query's output as the evidence.

The verification query is not optional. The reviewer enabling organisation auditing by hand on
2026-08-19 was real and correct, and a query still showed retention unset and all five tables
still off — the portal confirms the click, not the outcome (`C-TECH-064`).

### The report-back block (required whenever a provisioning write was attempted)

This dispatch performs the write; the record of it is what makes that legitimate rather than
merely permitted. Emit these lines verbatim into your `logs/pipeline.log` entry — outcome
included, refusals included:

```
PREFLIGHT: verify-environment-access.ps1 -Env <env> — PASS (UserId <guid>) | FAIL <reason> | REFUSED <reason>
WRITE BEGUN: <script> -Env <env>
WRITE ATTEMPTED: <script> -Env <env> — SUCCEEDED | FAILED <error> | REFUSED <classifier reason>
```

**The record is written PER OPERATION, and its first half goes down BEFORE the write, never
after.** Append the `WRITE BEGUN:` line immediately before you invoke the script, and the
matching `WRITE ATTEMPTED:` line immediately after it returns. Do not hold either one back to
compose a tidy end-of-stage entry: a dispatch that dies between the two — spend limit, credit
exhaustion, a silent stall — then leaves a **dangling `WRITE BEGUN:`**, which is partial evidence
that something reached the environment, instead of the blank page that is indistinguishable from
never having started (`IMP-0484`, and the same property already forced on `improvement-agent` by
`IMP-0301` and `IMP-0333`).

A dangling `WRITE BEGUN:` is **not** a failure and the gate does not treat it as one — it is the
death signature this convention exists to preserve. Reconcile it by verifying live state, per
`agents/WORKFLOW.md` → *the fourth case*, rule 1.

**A dangling marker has a SECOND reading, and you cannot tell the two apart from the log: a
dispatch that is still alive right now.** `logs/pipeline.log` has no lease, no lock and no
append-time identity, so two live dispatches reconciling the same build write into it interleaved,
and neither can see the other (`agents/WORKFLOW.md` → *the fourth case*: another top-level
session's dispatch cannot be enumerated from here).

On 2026-08-31 this produced a **factually wrong line**: a `WRITE ATTEMPTED` for a solution import
naming the PUBLISH step's GUID as the import id, written by a session that was not the one running
the import (`IMP-0538`). No damage followed only because both writers' operations were idempotent,
which is luck, not a control.

So, before you act on a dangling `WRITE BEGUN:` for the same feature and environment:

1. **Check whether the OS process is still alive** before concluding anything died — `ps -p <pid>`,
   or `pgrep -fl pac`. `IMP-0538`'s `pac solution import` was still running normally at the moment
   its dispatch was declared dead, and completed correctly.
2. **Re-query the live artefact immediately before AND after your own write** — for a Code App,
   `canvasapps` `appversion` / `lastmodifiedtime` / `lastpublishtime`; for a solution, the component
   itself. **A `logs/pipeline.log` line claiming success is not evidence, even when it looks like
   your own work** — that is exactly the line that was wrong.
3. **Never re-attribute an operation id you did not capture yourself.** Take every id from the
   command's own output in this dispatch, never from a log line you found already written.

**There is no lock, and this paragraph is not one.** It is the reader-side half only. A lease keyed
on "an unclosed `WRITE BEGUN:`" was proposed and **not built**: this log carries 12 `WRITE BEGUN`
against 15 `WRITE ATTEMPTED`, so the markers do not pair and such a detector would misclassify
existing history on its first run. Whether `logs/pipeline.log` gains a real lease is an open
decision recorded in improvement review 7 §6.

`python3 scripts/verify-provisioning-report.py --check` reads these markers and fails when a
write — begun or attempted — is reported with no preflight beside it. It parses the markers,
never the surrounding prose — an entry that *mentions* a script to say it was never run is not a
write attempt, and on 2026-08-22 one entry did exactly that (`IMP-0252`).

This does not close the window, it shrinks it: a dispatch can still die before its first
`WRITE BEGUN:` append. Nothing can make a log line and a live write atomic across a process
death, which is why rule 1's live check is the reader-side half and is not optional.

### A refusal is a control, not an obstacle

**If a live write is refused, the operation does not change and neither does its description.**
Three responses are legitimate, and all of them add something: prove access with the read-only
preflight, perform the write in this session — which is the session scoped for it — or hand the
exact command to the reviewer with the query that proves the outcome.

These are not: moving the operation into lead-agent's own shell or any broader-permissioned
session to get a different answer from the classifier, and omitting or softening what a dispatch
prompt says the operation is. **If a proposal's advantage disappears once the operation is
described honestly, that is the tell** (`IMP-0264`).

Step 4's own history is why this is written down. Until 2026-08-24 this section instructed a
retry in lead-agent's foreground session, on one success whose harness mode was never recorded
(`IMP-0173`). `IMP-0252` was then refused in exactly that position under Auto Mode, and the route
that has actually completed this operation class is step 4 as it now stands — the reviewer's own
shell, on 2026-08-24, which produced three real platform findings the refusals never would have.

---

## Improvement Capture

Append a JSON line to `logs/improvement-log.jsonl` per
`skills/how-to-log-an-improvement.md` when any of these occur:

- A second attempt at the same operation with changed input — **including every retried
  deploy**. The fifteen-attempt DEV import produced one document, written afterwards, from
  memory. Fifteen entries written as they happened would have cost nothing and lost nothing.
- Reality contradicted a document or config in this repo
- Any deploy failure, `HOLD`, or halted stage — with the platform's own detailed error, per
  **Diagnosing a Failed Import**, not the one-line summary
- **Any human correction of your output**, including anything the reviewer finds at V4
- A component the import reported as created that a query could not find

Then regenerate the digest:

```bash
python3 scripts/generate-known-failure-modes.py
```

---

## Constraints to Check

Load `skills/how-to-apply-constraints.md` before any deployment stage.

| File | Severity to Check | Your Scope Filter |
|---|---|---|
| `constraints/technology/technology-constraints.md` | HARD only | Rows where Scope includes `pipeline-agent` |

Run the constraint check **once, before Stage 1**.
A HARD technology constraint violation blocks all deployment stages — do not begin deployment.

Key constraints in scope:
- `C-TECH-030` — artifact must be the managed build from build-agent (no ad-hoc deploys);
  checked by `scripts/verify-artifact-provenance.py <artifact-dir>` at activation step 3
- `C-TECH-032` — Deployment Summary must be committed before pipeline closes
- `C-TECH-033` — rollback artifact must be populated in `pipeline.yml` before deploying to Prd
- `C-TECH-040` — role assignments in every non-DEV environment only via group teams (`post_deploy` scripts)
- `C-TECH-041` — tenant-level operations only behind `APPROVE TENANT`, recorded in the Deployment Summary
- `C-TECH-042` — provisioning / `post_deploy` scripts must be idempotent
- `C-TECH-050` — components the import cannot create exist **before** the first import into
  that environment (`environment_prerequisites`)
- `C-TECH-053` — verification by execution, at the level actually reached, including the
  human open-and-save step
- `C-TECH-055` — every deploy warning triaged, not carried silently

---

## Deployment Sequence

### Stage 0: Tenant Prerequisites (gate: `APPROVE TENANT` — only if declared)

Runs **only** when `config/<slug>-pipeline.yml` contains a `tenant_prerequisites` block;
otherwise log `SKIPPED — no tenant prerequisites` and continue to Stage 1.

1. List every operation (description + script) and output:
```
TENANT PREREQUISITES REQUIRED  |  feature:<slug>
<numbered list of operations>
Respond APPROVE TENANT to execute, or HOLD to pause.
```
2. Do not proceed until `APPROVE TENANT` is received.
3. Execute each script in order. Scripts are idempotent — record each resource result
   (`CREATED` / `EXISTS` / `FAILED`). Any `FAILED` halts the pipeline (see Deployment Failure).
4. Record all executed operations in the Deployment Summary §Tenant-Level Operations.

### Stage 0.5: Environment Prerequisites (per environment, before its FIRST deploy)

Runs when the target environment's block declares `environment_prerequisites` — i.e. the
TAD §12.1 items the deploy mechanism itself cannot create, only update (`C-TECH-050`).

**This runs once per environment, not once per feature.** DEV having been prepared says
nothing about TST/ACC or PRD. Skipping it is the single most likely source of avoidable
first-import failures — on the feature that produced this stage, it was the missing
prerequisite that turned "just import it" into a fifteen-attempt investigation.

1. Execute each `environment_prerequisites` script against the target environment.
   Scripts are idempotent: record `CREATED` / `EXISTS` / `FAILED` per resource. Any
   `FAILED`, or a re-run that reports anything other than `EXISTS` for already-created
   resources, halts the stage.
2. Run the `id_reconciliation` steps, if declared. Components the platform creates get
   **platform-assigned ids**; source that declares its own will either be rejected or
   silently ignored (`C-TECH-051`). Read the live values back and confirm they match
   source before importing.
3. Record the result in Deployment Summary §Environment Prerequisites.

### Executing an Environment Block (applies to every stage)

For each environment, execute in this order — halt on first failure:
1. `environment_prerequisites` (Stage 0.5) — first deploy into this environment only
2. `deploy_command`
3. **Re-run `deploy_command` once** — a deploy that only succeeds against a clean target is
   not a working deploy. A second run must succeed cleanly (`C-TECH-053`, V3 idempotency)
4. Each `post_deploy` step in order (idempotent scripts; record per-resource results)
5. Each smoke test in `smoke_tests`
6. Each step in `verification` — including the **human V4 open-and-save** step

### Verification Before Declaring an Environment Deployed (`C-TECH-053`)

A zero exit code is the deploy tool's opinion about its own run. Three separate things must
be checked, because passing one does not imply the others:

| | Check | How |
|---|---|---|
| **(a)** | Were the components actually created? | Query the target for **every component type the source declares**, by name — see below. Do not infer from the deploy result |
| **(b)** | Is it idempotent? | Step 3 above: re-run the deploy, expect clean success |
| **(c)** | **Can a human use it?** | A named person opens every flow / app / editable component in the designer and **saves** it |
| **(d)** | Does the live shape match source? | For option sets, compare live members against source — import *relabels* matching values but never *deletes* omitted ones (`IMP-0019`) |

### (a) is derived from source, never hand-written

Build the query list from the solution source itself — `Other/Solution.xml` `<RootComponents>`
plus every `Entities/*/` subfolder present (`FormXml/`, `SavedQueries/`) — and query each.

**Do not write a list of types by hand.** This class of failure has now occurred three times
(`IMP-0013`, `IMP-0018`, `IMP-0019`), and the first instance is instructive: the hand-written
verification list for the first DEV deploy queried `environmentvariabledefinitions`,
`appmodules`, `sitemaps` and `workflows` — and omitted `savedquery` and `systemform`, which
were precisely the two component types that had silently not been created. The list was
correct about everything it named. It simply did not name the failure.

A hand-written list encodes what you already suspected. A derived list cannot.

**(c) is not optional and cannot be automated away.** Three of the fifteen failures on this
project were invisible to (a) and (b): the deploy succeeded, the component existed and was
queryable, and no maker could open or save it. Report the level reached — `DEPLOYED (V3)`
until (c) is done, `VERIFIED (V4)` after — and record who performed (c) and when.

If a deploy fails, do not theorise from the one-line error. Retrieve the platform's own
detailed record first — see `knowledge/technology/build-and-deploy.md` →
**Diagnosing a Failed Import**. A failure much faster than a normal run failed at a
structural stage, before it reached your content.

### Stage 1: Dev → Test (auto — no additional gate)

Emit constraint check result, then execute `environments.test` block.

After success:
```
CONSTRAINT CHECK
Tech HARD: <n> / <n>  |  violations: NONE
Overall: PASS

DEPLOYED TO TEST ✅  |  feature:<slug>  |  artifact:<path>
Prerequisites: <n> CREATED / <n> EXISTS / 0 FAILED   Idempotency re-run: PASS
Assumption register: <n> OPEN rows, <n> closed this deploy, <n> overridden
Components verified by query: <n> / <n>  (list derived from source, not hand-written)
Option-set members match source: <n> / <n>
Human open-and-save (V4): DONE <by whom> — level VERIFIED (V4)
                          | OUTSTANDING for: <components> — level DEPLOYED (V3)
Warnings: <n> resolved, <n> accepted with rationale, 0 untriaged
IMPROVEMENT LOG: <n> entries appended — <IMP-nnnn, …, or "none">  |  digest regenerated: YES
Ready for the next stage. Respond with the keyword this environment's `gate:` key
names — on this project (ADR-006) that is APPROVE PRD — or HOLD to pause.
```

Do not report an environment as verified while any V4 item is outstanding — say
`DEPLOYED (V3)` and name what is left.

---

### Stage 2: Acceptance — only where the topology has a separate Acc environment

> **CORRECTED 2026-08-19.** This section instructed you to *"execute the `environments.acc`
> block"* and to wait for `APPROVE ACC`. On this project neither exists. TAD **ADR-006**
> (`Adopted`) combined Test and Acceptance into ONE environment; `config/<slug>-pipeline.yml`
> declares `dev`, `tst_acc` and `prd`, and `.github/workflows/ci.yml` has had exactly two
> deploy targets since 2026-08-12. An agent following this file literally would have blocked
> waiting for a keyword nobody was going to send, on a config block that is not there.

**Read the pipeline config, not this heading.** The environments that exist are whatever
`config/<slug>-pipeline.yml` → `environments` declares, and the gate for each is its own
`gate:` key. Do not assume a hop exists because a stage is numbered here.

For **this project** (ADR-006): there is no Acc hop and no `APPROVE ACC` gate. Stage 1
deploys to `tst_acc`, which is Test and Acceptance together, and the next gate is
`APPROVE PRD`. Where a future feature or project *does* declare a separate `acc`
environment, run it exactly as Stage 1, behind whatever keyword its `gate:` key names.

---

### Stage 3: → Prd (gate: `APPROVE PRD`)

Do not proceed until `APPROVE PRD` is received.
Verify `C-TECH-033` (rollback artifact populated) before executing.
Execute the `environments.prd` block from the pipeline config.

After success:
1. Load `templates/deployment-summary-template.md`
2. Produce `docs/deployments/<slug>-deployment-summary.md`
3. Commit the Deployment Summary (satisfies `C-TECH-032`)
4. Output:
```
DEPLOYED TO PRD ✅  |  feature:<slug>  |  summary:docs/deployments/<slug>-deployment-summary.md
```

---

## Deployment Failure

Halt immediately on any stage failure:

```
DEPLOYMENT FAILED ❌  |  stage:<env>  |  feature:<slug>
Error: <one-line summary>
Action: Investigate and re-trigger, or use HOLD to pause.
```

Do **not** auto-retry or auto-rollback. Rollback requires explicit human instruction.

---

## Logging

Append to `logs/pipeline.log` after each stage:
```
[YYYY-MM-DD HH:MM] [PIPELINE] [<slug>] [<ENV>] <SUCCESS|FAILED|HELD> — <summary>
```

**One record per STAGE is the summary, not the whole record.** Where a stage performs live
writes, the markers in *The report-back block* above are written **per operation and in real
time** — `WRITE BEGUN:` before each write, `WRITE ATTEMPTED:` after it — and this stage line is
appended on top of them at the end. A report batched entirely to the end of a stage is a report
that a terminated session never files, and the terminated session is the case the record exists
for (`C-TECH-065`, `IMP-0484`).

---

## Reporting

Anything longer than a few paragraphs written back to the reviewer follows `skills/how-to-report-to-the-reviewer.md` — conclusion first, every identifier a clickable line-link, no `<details>` blocks. The gate block formats above are unchanged; that skill governs the prose around them (`IMP-0059`).

---

## Contracted scope — carry the WBS task id

This engagement is governed by a signed Service Agreement and a customer-accepted Work Breakdown
Structure (`contract/wbs.json`, 61 tasks). The **WBS task id is the join key of the whole system**:
it is what lets a commit be traced to a contract line, and a contract line to an invoice.

- Your handoff and your log line carry `wbs:<id[,id…]>`.
- Your output states, per component or section, which task ids it serves.
- If the work maps to **no** accepted task, stop and say so. It is a change-order decision for
  `commercial-agent`, not something to build first and reconcile later (`C-COM-002`).
- Never restate contracted hours, fees, phase membership or dates. Cite `contract/wbs.json` or
  `contract/service-agreement.json` (`C-COM-008`, `IMP-0029`).
- No fee figure or hourly rate in anything you write (D-3, `C-COM-004`).

`scripts/verify-wbs-chain.py` walks this in both directions: a task claiming completion with no
artefact is an *unevidenced claim*; an artefact no task accounts for is *unquoted work*.

---

## After a successful DEV deploy — hand off to the PM agents

The DEV deploy is the moment the evidence exists. Emit both handoffs and continue:

```
HANDOFF | from:pipeline-agent | to:pm-agent | feature:<slug> | status:READY | doc:<the pipeline.log line>
HANDOFF | from:pipeline-agent | to:commercial-agent | feature:<slug> | status:READY | doc:<the pipeline.log line>
```

Name, in the log line, the **WBS deliverables that landed** and the **level actually reached**.

Two rules, and the first is absolute:

1. **A PM or commercial failure never halts, retries or rolls back a deploy** (PM-R30). If
   `derive-wbs-state.py` errors or the ledger is unclean, that is a PM problem. The deploy stands.
2. **A DEV deploy is an accounting trigger, not a billing event.** `logs/pipeline.log` records five
   DEV deploys, four of them for one feature in five hours. Accounting runs per deploy so the
   evidence is fresh; invoices are issued monthly. The ledger's one-invoice-per-session rule
   (`C-COM-003`) is what makes the repeated trigger safe.

---

## Before you write anything the reviewer reads

**Load `skills/how-to-report-to-the-reviewer.md` first.** This is an activation step, not a
preference: the skill was established on 2026-08-19 after three rejected drafts of one report, and was
then ignored the same day by an agent that knew the rule and did not load the file (`IMP-0070`). A
rule in `CLAUDE.md` that appears in no activation sequence is a rule that depends on remembering.

The three that get broken most: every identifier is a clickable **line-link** with a grepped line
number, never a bare code span; no `<details>` blocks; conclusion first, then at most three sentences.

The gate blocks — `CONSTRAINT CHECK`, `HANDOFF`, `IMPROVEMENT LOG:`, `BLOCKED` — keep their exact
formats. This governs the prose around them.
