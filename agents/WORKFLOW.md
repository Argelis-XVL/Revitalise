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
                                                               Test→Acc  [APPROVE ACC]
                                                               Acc→Prd   [APPROVE PRD]
```

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
| `logs/improvement-log.jsonl` reaches ≥10 `NEW` entries | at the next routing decision |
| **Any `blocker`-severity entry appended** | **immediately — do not batch** |
| **The reviewer requests a new system capability** (new agent, gate, ledger, or rule) | on request — **capability mode**, authorised by a design document in `docs/improvements/` (`IMP-0027`) |

---

## Human Gate Keywords

| Gate | Proceed | Pause / Revise |
|---|---|---|
| Plan, Architecture, Dev, Test | `APPROVED` | any other text |
| Request test re-run | `REQUEST RETEST` | — |
| Tenant-level provisioning | `APPROVE TENANT` | `HOLD` |
| Deploy to Acc | `APPROVE ACC` | `HOLD` |
| Deploy to Prd | `APPROVE PRD` | `HOLD` |
| **System self-improvement** | **`APPROVE IMPROVEMENTS`** | any other text |
| **Deploy with an OPEN assumption** | **`OVERRIDE <A-nnn>` + reason** | `HOLD` |

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

---

## Revision Cap

Maximum 3 revision cycles per gate. On the 3rd failure, emit and stop:

```
BLOCKED | agent:<n> | feature:<slug> | gate:<n> | doc:<latest-path>
Reason: <one sentence>
```
