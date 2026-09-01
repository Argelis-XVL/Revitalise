# WORKFLOW.md — Orchestration Rules

Read by the **Lead Agent only** on session start.
All other agents receive these rules via the handoff contract.

---

## Agent Roster

| Agent | File | Primary Output |
|---|---|---|
| Lead | `agents/lead-agent.md` | Routes requests |
| Plan | `agents/plan-agent.md` | `docs/plans/<slug>-plan.md` |
| Architect | `agents/architect-agent.md` | `docs/architecture/<slug>-architecture.md` |
| Development | `agents/development-agent.md` | `docs/development/<slug>-dev-summary.md` + `config/build.yml` |
| Test | `agents/test-agent.md` | `docs/tests/<slug>-test-report.md` |
| Build | `agents/build-agent.md` | `build/artifacts/<slug>-<date>-<n>/` |
| Pipeline | `agents/pipeline-agent.md` | `docs/deployments/<slug>-deployment-summary.md` |
| Improvement | `agents/improvement-agent.md` | `docs/improvements/<date>-improvement-review.md` + regenerated `logs/known-failure-modes.md` |
| PM | `agents/pm-agent.md` | `logs/state/wbs-state.md` + the status block + `contract/*.json` |
| Commercial | `agents/commercial-agent.md` | `logs/worklog.jsonl` + `contract/invoices/INV-<YYYY-MM>.md` |
| Acceptance | `agents/acceptance-agent.md` | `contract/acceptance/PA-<phase>.md` + `contract/handover/` |

---

## Session Boundaries (mechanical enforcement)

**Added 2026-08-21, IMP-0143.** Every row above is a Claude Code subagent —
`.claude/agents/<file-stem>.md`, generated from `config/models.yml` by
`scripts/generate-subagents.py`. A hop in the Flow below is one **Task-tool dispatch** to that
subagent, never a persona switch inside the conversation you are reading this in.

This is not optional structure; it is what makes the Tier column mean anything. A resolved
model ID only takes effect if the agent actually runs on a separate invocation pinned to it.
"Act as plan-agent, then architect-agent, then development-agent" inside one continuously
growing conversation runs all three on whatever model that conversation happens to be on —
which is how this project ran two full days on Opus for work designed to run mostly on Haiku
and Sonnet, at Opus's price, before this section existed.

**Before every hop, the dispatcher:**
1. Checks the target agent's `escalate_to_strategic_when` / `de_escalate_to_mechanical_when`
   list in `config/models.yml`. If a condition is met, passes an explicit `model:` override
   (`opus` or `haiku`) on the Task invocation — the generated subagent file is pinned to the
   agent's *default* tier only and cannot escalate itself mid-invocation.
2. Dispatches via the Task tool, `subagent_type: <agent-name>`, carrying the handoff line and
   doc path only — never pasted content (Handoff Contract, below).
3. Reads back only the subagent's gate output. If it stopped short of a gate, that is a
   finding, not an invitation to finish its work in this conversation — re-dispatch it with
   the doc path carried forward.

**Stop condition, every agent, no exception:** produce the required output, emit the
`HANDOFF` (or `BLOCKED` / `DEPLOYMENT FAILED`) line, and end the turn there. A gate block is
not a pause for more discussion on the same invocation — a further instruction to that agent
is a new dispatch. "Handover" in this system means a written doc plus a stopped subagent,
never a conversation kept open in case there is more to do.

Development-agent's own sub-agents (`data-agent`, `backend-agent`, … — see
`agents/development-agent.md` → Sub-Agents) follow the same rule one level down: each is its
own Task dispatch, not a section of development-agent's own turn.

### When a dispatch dies instead of finishing

A dispatched agent can be terminated by a limit outside this system — an account spend ceiling, a
context or timeout limit — enforced by the API layer, which no gate in this repository can see. It
is neither a `BLOCKED`, nor a failed constraint check, nor a harness permission refusal. It produces
**no gate output at all**, so the dispatcher learns nothing unless it goes looking (`IMP-0172`).

Three rules, and the first is the one that was got wrong:

1. **A parent's terminal error does not stop its children.** Sub-dispatches already launched keep
   running independently and report as separate, later notifications. Before treating the batch as
   failed, enumerate every child (`ListAgents` / the pending notifications) and record each
   outcome **individually** — not one pass/fail for the tree.
2. **Verify each touched file directly, not from the parent's last words.** Compile it, parse it,
   run its selftest, run it against real data. A child that died mid-verification may have already
   written a complete and correct edit; a child that reported success may still have left a claim
   the file does not support (`C-TECH-061`'s `evidence_grep` is the mechanical form of this).
3. **Do not re-dispatch the same scale of work.** It will fail the same way. Surface the limit to
   the reviewer — the error names its own remedy — and if anything must proceed first, dispatch
   the smallest remaining reconciliation, never another wide fan-out.

An agent that fans out internally states its child count and their completion state in its own
gate output, so "this batch is *n* of *m* complete, here is what is left" is written down
somewhere before it can be lost. The backstop, when nothing is written down, is
`python3 scripts/verify-improvement-log.py --check`: a batch that never reconciled leaves its
findings unread and the gate goes red. That is how `IMP-0172` was found.

#### The fourth case: a dispatch that stalls without erroring, in a session you cannot reach

The rules above assume a *terminal error* the API layer produced. A dispatch can instead simply stop
— no error, no gate output, no notification — and if it was launched by a **different top-level
session**, it is invisible to everything this session can query. `ListAgents` lists this session's
own children and named peer sessions; it does not list another session's internal Task-tool
dispatch. **Its silence is not evidence that nothing was dispatched, and not evidence that nothing
was written** (`IMP-0291`, three instances in one day against a class the log scored `x1` —
`docs/improvements/agent-instruction-history.md` → *The fourth case*).

So, when told a dispatch is stuck:

1. **Verify the target artefact directly, and let the MEDIUM THE DISPATCH WRITES TO decide what
   counts as evidence.** For a dispatch whose artefact is a file, that is its mtime and its
   content, checked for a partial write before assuming nothing happened — a stalled agent may
   have written a complete edit. For a dispatch whose artefact is a **live environment** — every
   `pipeline-agent` dispatch, and any dispatch running a provisioning script — an unchanged
   mtime, an empty `logs/pipeline.log` and absent `PREFLIGHT:` / `WRITE BEGUN:` / `WRITE
   ATTEMPTED:` markers are evidence about *this repository* and say nothing whatever about the
   environment. **Verify live state directly**, exactly as the fifth case below already requires.

   A reconciliation that checked four things — log content, Deployment Summary mtime, marker
   absence, `ListAgents` — concluded no live write was attempted, and was wrong on every component:
   the table, its attributes, the alternate key, both privilege grants, the audit switch and the
   seed row were already in DEV. Every one of the four checks is a fact about a file or a session
   (`IMP-0484`; the full account is in
   `docs/improvements/agent-instruction-history.md` → *The fourth case*).

   The live check is cheap and needs no new tooling: this project's provisioning scripts are
   idempotent and report per component, so `pwsh provisioning/dataverse/ensure-schema.ps1 -Env
   <env>` answers *"was this written?"* with `EXISTS`/`CREATED` per item and creates nothing that
   is already there. Run the probe first (`C-TECH-065`), and report both in the reconciling
   entry.
2. **Re-dispatch fresh from the current session.** Do not wait on, or try to resume, a dispatch
   in a session this one cannot see.

   **But a resume of a session this one CAN see is cheap and usually works — measured, not
   assumed.** `logs/routing.log` records 13 resume attempts: one incident of three failures against
   at least six whose applied output is on disk today. Resume is the default for a parked agent you
   dispatched yourself in this session; it keeps that agent's loaded context and skips a full
   re-read of its knowledge, constraint and template files.

   **Two conditions, and only these two, make a fresh dispatch mandatory:**

   1. **You need a different tier.** `SendMessage` has **no `model` parameter**, so an override
      passed to a resume silently no-ops and the agent keeps running on the tier it was spawned
      with. A tier change is always a fresh Agent-tool dispatch with `model:` set at spawn
      (`IMP-0399`).
   2. **The transcript is gone** — another top-level session, a reboot, or a resume that returns
      `No transcript found for agent ID`. Do not retry the resume; dispatch fresh, carrying the
      doc path.

   A failed resume costs one round trip and names its own remedy, so it is not a thing to
   pre-emptively avoid — it is a thing to stop retrying once it has answered. **This is prose and
   cannot be otherwise:** `SendMessage` calls leave no repository trace, so no gate can observe a
   resume attempt.
3. **Close the `ROUTED_TO` line.** Every `ROUTED_TO` line is closed by a terminal line for the
   same dispatch — `GATE_RECEIVED`, `BLOCKED`, or an explicit `STALLED`/`RE-DISPATCHED` note
   naming what was verified. An unclosed `ROUTED_TO` is the only trace this class leaves.
4. **Record the resolved tier when a dispatch is escalated.** Write it on the `ROUTED_TO` line —
   *"Escalated to strategic tier (opus)"*. It is the only artefact a dispatched agent can read to
   learn which tier it is actually running on: neither `config/models.yml` nor its own generated
   frontmatter can ever show an override (`IMP-0290`).

**The mechanical half EXISTS — read it before you reconcile by hand.**
`scripts/verify-routing-reconciliation.py` closes every `ROUTED_TO` against a later
`GATE_RECEIVED` / `STALLED` / `BLOCKED` / `HANDOFF_RECEIVED` naming the same agent and feature,
working forward from a cutoff per the `IMP-0181` precedent. It is wired as the
`routing-reconciliation` step of `config/<slug>-build.yml` and runs on every build.

**It is `--warn-only`, so it exits 0 and blocks nothing.** Run it yourself when told a dispatch
is stuck — it names the unclosed line for you, which is faster than reading the log:

```bash
python3 scripts/verify-routing-reconciliation.py
```

**The cutoff is 2026-08-31 by reviewer decision, and it is inclusive of its own day:** 2026-08-31
dispatches are in scope, everything before is out of scope by design and reported as such rather
than silently dropped (`IMP-0547`).

**A non-zero reading is a queue of dispatches whose artefacts nobody verified — not noise, and not a
build problem.** Read the current figures from the script, never from this page. Going HARD is still
open and is gated on reconciling the outstanding queue first, not on choosing a later cutoff: a
cutoff picked to produce a green reads zero over an empty corpus and is evidence of nothing.

#### The fifth case: a dispatch that reports `completed` while deferring work to a monitor it created itself

This one arrives wearing success. The dispatch's task status is `completed`, no error is reported,
and its final message says the work is in hand — typically *"I already have a Monitor watching for
completion; I'll resume automatically once that notification arrives."*

**That resumption cannot happen.** A background `Agent`-tool dispatch has no way to be woken by a
Monitor or background-task notification: those route to the **dispatching** session, never to the
dispatched agent's own — by then ended — context. The agent had modelled its own execution the
way the parent session works rather than recognising that *its turn ending IS the terminal state*
from the dispatcher's point of view (`IMP-0357`).

So it is identical in effect to the three spend-limit deaths above, and must be reconciled the
same way — with one extra trap: **`completed` describes only that the agent's turn ended with no
live children. It is not a claim that the agent's stated goal was reached.**

The tell, and it is cheap to spot: **a final message whose remaining work is phrased as *"I'll
resume when X completes"*.** Treat it as a death. Verify live state directly, then do the
smallest remaining reconciliation yourself rather than waiting for a resumption that is not
coming.

##### The dispatcher's half: preempt it in the prompt, do not just recognise it afterwards

Everything above tells the dispatcher how to *recognise* this death after it has happened. That is
diagnosis, and diagnosis has failed repeatedly: the paragraphs above were cited in dispatch briefs
and the failure recurred anyway. A dispatched agent does not re-derive the harness's execution model
mid-turn; it reaches for the tool that looks right, and `run_in_background` looks right for a long
step (`IMP-0520`).

So the obligation moves to where it can act — **composing the prompt, not reading the result.**
Every dispatch whose task contains a long-running step (`npm ci`, a full Pester or vitest run, a
live solution-checker call, a `pac` push) must **state in the dispatch prompt** that long steps run
**synchronously and blocking within the turn** — never backgrounded, never deferred to a
notification. One sentence, and the reason belongs with it, because an unexplained prohibition is
the kind an agent optimises around:

> Run every long step in the foreground and wait for it. Do not use `run_in_background`, and do not
> create a Monitor to wait on your own work: a dispatched agent's background child does not survive
> its own turn ending, and the notification routes to the dispatching session, not back to you.

**This stays PROSE, and that is on the record as a known weakness.** The ladder says a recurrence
after a prose change is evidence of wrong altitude, and this is the second prose change in the same
class. There is no mechanical home available: no gate can read a dispatch prompt that exists only
inside a live session. Moving the instruction from the *diagnosis* section to the *composition* step
is the only altitude change still available, and **it recurred again afterwards (`IMP-0537`), so the
next rung is due: a dispatch-prompt checklist in `agents/lead-agent.md`'s activation sequence — not
another paragraph here.**

**Do not hand-type this class's instance count.** Three documents carried one and all three had
drifted. `logs/known-failure-modes.md` generates it from the log and is the read path for it — cite
the class name and let the digest carry the number (`IMP-0537`).
---

## Flow

```
User → Lead → Plan ──[APPROVED]──► Architect ──[APPROVED]──► Development
                                                                   │
                                                              [APPROVED]
                                                                   ▼
                                                    Build (auto) ──► Test
                                                                      │
                                                               [APPROVED]
                                                                      ▼
                                                               Pipeline
                                                               Tenant prereqs   [APPROVE TENANT]*
                                                               Env prereqs      (per env, auto)†
                                                               Dev→Test  (auto)
                                                               Test→Prd  [APPROVE PRD]
```

‡ **The environment chain is whatever `config/<slug>-pipeline.yml` declares — not what this
diagram draws.** On this project TAD ADR-006 combined Test and Acceptance into one
environment (`tst_acc`), so there is no Acc hop and no `APPROVE ACC` gate. This diagram, and
`agents/README.md`, and `agents/pipeline-agent.md` all still described the three-hop chain on
2026-08-19, nine days after the topology changed and seven days after `ci.yml` was rewritten
around two deploy targets. Where a project *does* declare a separate `acc` environment, its
gate keyword is its own `gate:` key and `APPROVE ACC` is the convention.

\* Stage 0 — only when `config/<slug>-pipeline.yml` declares a `tenant_prerequisites`
block (app registrations, admin consent, Entra security groups, SPO site collections,
Teams org-catalog publishing). Skipped otherwise.

† Stage 0.5 — everything the deploy mechanism cannot *create*, only update (TAD §12.1,
`C-TECH-050`), plus reconciliation of platform-assigned ids (`C-TECH-051`). Runs **before
the first deploy into each environment**, and runs again for every new environment: DEV
being prepared says nothing about TST/ACC or PRD.

### Verification levels — what each stage is entitled to claim

No stage may report a level it did not execute (`C-TECH-053`,
`skills/how-to-verify-a-platform-contract.md` §5):

| Stage | Claims | Does **not** prove |
|---|---|---|
| Build | **V2 packaged** — layout accepted by the packer | Anything about content |
| Pipeline deploy | **V3 accepted** — components exist and re-deploy cleanly | That a human can use them |
| Pipeline V4 step | **V4 usable** — a named person opened and saved each one | That it produces correct results |
| Test | **V5 executed** — end-to-end with real inputs and observed outputs | Any other environment or OS |
| **Acceptance** | **V6 client accepted** — a dated record signed by the Client's authorised contact | That it will keep working; warranty covers that, and only for what we built |

**V6 may be set by nobody.** It is recorded only from an explicit `CLIENT ACCEPTED <phase> <date>`
input naming the person who accepted. Warranty (60 days, Build Terms B4), hypercare (10 business
days) and the per-phase liability cap (B11) all hang off that date, so no quantity of passing tests
substitutes for it (`C-COM-006`).

A green build on source the target rejects is the normal case, not an anomaly: it happened
fifteen times in a row on this repo's first live deployment
(`docs/development/revitalise-grant-automation-dev-deployment-handover.md`).

### Intake variant

When requirements and/or a solution architecture are authored **outside** the system,
plan-agent and architect-agent run in **intake mode**: they adopt the external document
(map → normalise → verify) instead of authoring it, per
`skills/how-to-intake-external-documents.md`. Each gate additionally receives an
**Adoption Report** (sections PRESENT / DERIVED / MISSING, interpretations,
out-of-palette components). Gate keywords, constraint checks, revision cap, and
everything from Development onward are identical to the authoring flow.

```
External docs → Lead → Plan (intake) ──[APPROVED]──► Architect (intake) ──[APPROVED]──► Development → …
```

If both documents are provided, requirements intake runs first; the adopted SDD then
feeds architecture intake. If only an architecture is provided, plan-agent must first
produce or adopt an SDD.

---

## The Learning Loop

Runs alongside the delivery flow, not inside it. Every agent **writes** findings; one agent
**reads** them back and changes the system.

```
any agent, on friction ──► logs/improvement-log.jsonl        (append-only, per-finding)
                                      │
                        improvement-agent  [APPROVE IMPROVEMENTS]
                                      │
              ┌───────────────────────┴────────────────────────┐
              ▼                                                ▼
   constraints/ skills/ knowledge/            logs/known-failure-modes.md
   agents/ scripts/ config/                   (generated digest — the READ path)
                                                               │
                                          build-agent & pipeline-agent
                                          read it at activation step 0
```

**Why the read path is drawn explicitly.** This system never had a capture problem — build-agent
and pipeline-agent already wrote forensic post-mortems into their logs and manifests. Nothing
read any of it back, and those two were the only agents in the roster loading no prior
experience at all. The digest closes that loop; without it, capture is just archiving.
See `docs/improvements/2026-08-17-failure-analysis-and-self-learning-design.md`.

### Capture contract (all agents)

| | |
|---|---|
| **Where** | `logs/improvement-log.jsonl`, append-only, one JSON object per line |
| **How** | `skills/how-to-log-an-improvement.md` — loaded at the moment of writing, not upfront |
| **When** | 2nd attempt at an operation · reality contradicted a repo document · any `BLOCKED`/`FAILED`/`HOLD` · **any human correction of agent output** · a gate fired or was found broken · a capability was established |
| **Then** | `python3 scripts/generate-known-failure-modes.py` — a finding that never reaches the digest teaches nobody |
| **Report** | One line in the gate output, **even when the answer is none**: `IMPROVEMENT LOG: <n> entries appended — <ids or "none">  \|  digest regenerated: YES` |

Findings never go into `routing.log`, `build.log` or `pipeline.log` — those stay one line per
action. Eight findings were once improvised into `routing.log`, where nothing could process
them (`IMP-0023`).

### Processing triggers (lead-agent routes to improvement-agent)

| Trigger | Timing |
|---|---|
| A feature or phase completes | after the Deployment Summary |
| The reviewer asks | on request |
| `logs/improvement-log.jsonl` reaches ≥30 `NEW` entries **that are `unread` or `awaiting-approval`** | at the next routing decision |
| **Any `blocker`-severity entry appended** | **immediately — do not batch** |
| **The reviewer requests a new system capability** (new agent, gate, ledger, or rule) | on request — **capability mode**, authorised by a design document in `docs/improvements/` (`IMP-0027`) |

---

## The Commercial Loop

Runs alongside the delivery flow, like the learning loop — never inside it. **A commercial or
reporting failure never halts, retries or rolls back a build or a deploy** (PM-R30).

```
docs/Import/  WBS v0.5 (client-accepted) + Service Agreement v1.3 (signed)
      │  [APPROVE BASELINE]
      ▼
contract/wbs.json · service-agreement.json · source-lock.json      (generated, hours only — D-3)
      │
      ├──► pm-agent: derive state from EVIDENCE ──► logs/state/wbs-state.md
      │         │                                   (claimed_status compared, never trusted)
      │         ▼
      │    ready set over the dependency graph ──► lead-agent routes by WBS task id
      │                                                        │
      │                                          plan → arch → dev → build → test → pipeline
      │                                                        │
      │      ┌─────────────────────────────────────────────────┘  (DEV deploy success)
      │      ▼                                    ▼
      │  pm-agent: re-derive state        commercial-agent: propose sessions from evidence
      │                                          │  [APPROVE TIMESHEET]
      │                                          ▼
      │                                   logs/worklog.jsonl
      │                                          │  month end · [ISSUE INVOICE <id>]
      │                                          ▼
      │                                   contract/invoices/
      ▼
phase complete ──► acceptance-agent: pack (V5 → V6)  [CLIENT ACCEPTED <phase> <date>]
                          │
                          ▼
                   contract/acceptance/  ──► warranty clock starts  ──► [APPROVE HANDOVER]
                                                                          contract/handover/
```

Every arrow is a machine-checkable link, joined by the **WBS task id**. `scripts/verify-wbs-chain.py`
walks it in both directions: a task claiming completion with no artefact is an *unevidenced claim*, an
artefact no task accounts for is *unquoted work*, and neither is inferred away.

---

## Human Gate Keywords

| Gate | Proceed | Pause / Revise |
|---|---|---|
| Plan, Architecture, Dev, Test | `APPROVED` | any other text |
| Request test re-run | `REQUEST RETEST` | — |
| Tenant-level provisioning | `APPROVE TENANT` | `HOLD` |
| Deploy to Acc — **only where the pipeline config declares an `acc` environment**; this project has none (ADR-006) | `APPROVE ACC` | `HOLD` |
| Deploy to Prd | `APPROVE PRD` | `HOLD` |
| **System self-improvement** | **`APPROVE IMPROVEMENTS`** | any other text |
| **Deploy with an OPEN assumption** | **`OVERRIDE <A-nnn>` + reason** | `HOLD` |
| **Lock a new contractual baseline version** | **`APPROVE BASELINE`** | `HOLD` |
| **Confirm hours into the ledger** | **`APPROVE TIMESHEET`** | `HOLD` |
| **Accept unquoted scope as chargeable** | **`APPROVE CHANGE ORDER <id>`** | `HOLD` |
| **Issue a monthly invoice** | **`ISSUE INVOICE <id>`** | `HOLD` |
| **Record client acceptance of a phase** | **`CLIENT ACCEPTED <phase> <YYYY-MM-DD>`** | — |
| **Release a handover pack** | **`APPROVE HANDOVER`** | `HOLD` |

Two of those are not approvals but **facts the system cannot derive**. `APPROVE BASELINE` fixes which
document version is contractual; `CLIENT ACCEPTED` records an act by the Client's authorised contact
and starts a 60-day warranty window. An agent that infers either has invented a contract term.

`APPROVE IMPROVEMENTS` is the only keyword that authorises edits to `agents/`, `constraints/`,
`skills/` and `knowledge/`. No other agent may change the rules it operates under.

`OVERRIDE <A-nnn>` exists because an Unvalidated Assumptions Register row marked `OPEN` is a
prediction of a live defect, not paperwork: A-001 was recorded correctly, shipped anyway, and
the reviewer found it as three dropdowns with no options (`IMP-0014`).

Tenant-level operations (create/modify app registrations, grant admin consent, create
security groups, create SPO site collections, publish to the Teams org catalog) are
hard to reverse and privileged — they run **only** behind `APPROVE TENANT`, and every
executed operation is recorded in the Deployment Summary.

An agent **never** proceeds past its gate without the exact keyword.
After **3 failed revision cycles** the agent emits `BLOCKED` and stops.

---

## Handoff Contract

Every handoff **must** contain these five fields — nothing more, nothing less:

```
HANDOFF | from:<agent> | to:<agent> | feature:<slug> | status:<STATUS> | doc:<path>
```

Valid STATUS values: `READY` `APPROVED` `REVISION` `BLOCKED`

Handoffs reference documents **by path only** — never paste document contents into a
handoff or into a receiving agent's prompt; the receiving agent reads the file itself.

Append `| artifact:<path>` only when a build artifact is present:

```
HANDOFF | from:build-agent | to:test-agent | feature:my-feature | status:READY | doc:docs/development/my-feature-dev-summary.md | artifact:build/artifacts/my-feature-20250414-3/
```

---

## Logging

One line per completed action. Identical format across all logs:

```
[YYYY-MM-DD HH:MM] [AGENT] [FEATURE] [STATUS] — <one-line summary>
```

| Log | Owner | Format |
|---|---|---|
| `logs/routing.log` | lead-agent | one line per action |
| `logs/build.log` | build-agent | one line per action |
| `logs/pipeline.log` | pipeline-agent | one line per action |
| `logs/improvement-log.jsonl` | **all agents** (append-only); status fields owned by improvement-agent | one JSON object per line |
| `logs/known-failure-modes.md` | **generated** — `scripts/generate-known-failure-modes.py` | never hand-edited |
| `logs/pm.log` | pm-agent, commercial-agent, acceptance-agent | one line per action |
| `logs/worklog.jsonl` | **commercial-agent only**, behind `APPROVE TIMESHEET` | one JSON object per session, append-only |
| `logs/commercial-events.jsonl` | the three PM agents | one JSON object per authorised commercial act, append-only |
| `logs/state/*` | **generated** — `scripts/derive-wbs-state.py`, `scripts/report-baseline-drift.py` | never hand-edited |

---

## Revision Cap

Maximum 3 revision cycles per gate. On the 3rd failure, emit and stop:

```
BLOCKED | agent:<n> | feature:<slug> | gate:<n> | doc:<latest-path>
Reason: <one sentence>
```
