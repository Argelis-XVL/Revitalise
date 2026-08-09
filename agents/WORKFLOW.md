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
                                                               Tenant prereqs [APPROVE TENANT]*
                                                               Dev→Test  (auto)
                                                               Test→Acc  [APPROVE ACC]
                                                               Acc→Prd   [APPROVE PRD]
```

\* Stage 0 — only when `config/<slug>-pipeline.yml` declares a `tenant_prerequisites`
block (app registrations, admin consent, Entra security groups, SPO site collections,
Teams org-catalog publishing). Skipped otherwise.

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

## Human Gate Keywords

| Gate | Proceed | Pause / Revise |
|---|---|---|
| Plan, Architecture, Dev, Test | `APPROVED` | any other text |
| Request test re-run | `REQUEST RETEST` | — |
| Tenant-level provisioning | `APPROVE TENANT` | `HOLD` |
| Deploy to Acc | `APPROVE ACC` | `HOLD` |
| Deploy to Prd | `APPROVE PRD` | `HOLD` |

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

| Log | Owner |
|---|---|
| `logs/routing.log` | lead-agent |
| `logs/build.log` | build-agent |
| `logs/pipeline.log` | pipeline-agent |

---

## Revision Cap

Maximum 3 revision cycles per gate. On the 3rd failure, emit and stop:

```
BLOCKED | agent:<n> | feature:<slug> | gate:<n> | doc:<latest-path>
Reason: <one sentence>
```
