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
0. **Read `logs/known-failure-modes.md` — before your config, not after.** One page,
   generated from `logs/improvement-log.jsonl`. Its *"Before you declare a deploy or an import
   successful"* and *"Capabilities established in earlier sessions"* sections are directly
   about your work. The second exists because a working certificate-from-keychain procedure
   established on 2026-08-16 was gone by 08-17 and the reviewer had to re-teach it
   (`IMP-0022`). Do not ask the reviewer to re-supply something this file records.
1. Read `config/<slug>-pipeline.yml` — the deployment definition, to be verified, not trusted
2. Load `knowledge/technology/build-and-deploy.md` for tooling reference
3. Run the pre-deploy constraint check (see below)
4. **Run the assumption-register gate** (see below) — before any environment is touched
5. Execute the deployment sequence
6. Append findings to `logs/improvement-log.jsonl` and regenerate the digest (see
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
- `C-TECH-030` — artifact must be the managed build from build-agent (no ad-hoc deploys)
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
