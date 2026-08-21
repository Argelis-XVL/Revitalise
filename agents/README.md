# Agents — Quick Reference

Master orchestration rules: `WORKFLOW.md`
Model assignments: `config/models.yml`
Constraints: `constraints/domain/` and `constraints/technology/`

---

## Agent Index

| Agent | Tier | Domain Constraints | Tech Constraints | Output |
|---|---|---|---|---|
| Lead | Mechanical | — | — | Routes requests |
| Plan | Standard† | HARD only | — | `docs/plans/<slug>-plan.md` |
| Architect | Standard† | HARD + SOFT | HARD + SOFT | `docs/architecture/<slug>-architecture.md` |
| Development | Standard† | HARD only | HARD + SOFT | `docs/development/<slug>-dev-summary.md` + build/pipeline configs |
| Test | Standard† | HARD + SOFT (**final**) | HARD + SOFT (**final**) | `docs/tests/<slug>-test-report.md` |
| Build | Standard† | — | HARD only | `build/artifacts/<slug>-<date>-<n>/` |
| Pipeline | Standard† | — | HARD only | `docs/deployments/<slug>-deployment-summary.md` |

† = escalates to the **strategic** tier when the escalation conditions in
`config/models.yml` are met. Model IDs live only in `config/models.yml` — tiers resolve
there (mechanical/standard/strategic), never in agent files.

Build and Pipeline are **Standard**, not Mechanical — re-tiered 2026-08-17
(`config/models.yml` lines 138-162) after a week where both did real diagnostic reasoning
(decompiling a packer DLL, diagnosing a silent no-op gate, live-querying a failed import) on
the rationale that they were "reads a YAML file, no reasoning required." This table itself
carried the old, superseded tier for four days after the re-tier — the
`two-invocation-paths-disagree` class, x7 with this instance (`IMP-0144`). If you find this
table disagreeing with `config/models.yml` again, `config/models.yml` is the source of truth;
fix this table, not the other way round.

**Mechanical enforcement.** Each row is a generated Claude Code subagent —
`.claude/agents/<file-stem>.md`, produced from this table's Tier column (via
`config/models.yml`) by `scripts/generate-subagents.py`. Delegating to an agent means
dispatching that subagent with the Task tool, not continuing this conversation as that
agent. See `agents/WORKFLOW.md` → "Session Boundaries" for the full rule, including the
escalation-override step.

---

## Constraint Severity

| Severity | Agent Behaviour |
|---|---|
| **HARD** | Gate is **BLOCKED** — agent cannot accept `APPROVED`; violation must be resolved first |
| **SOFT** | Gate emits **WARN** — agent proceeds to approval prompt; human explicitly acknowledges risk |

Constraint check output is mandatory on every gate. Format defined in `skills/how-to-apply-constraints.md`.

---

## Flow (with constraint check points)

```
User → Lead(mechanical)
         │
         ▼
    Plan(standard†) ── [domain HARD check] ──[APPROVED]──►
         │
         ▼
    Architect(standard†) ── [domain HARD+SOFT + tech HARD+SOFT check] ──[APPROVED]──►
         │
         ▼
    Development(standard†) ── [domain HARD + tech HARD+SOFT check] ──[APPROVED]──►
         │
         ▼
    Build(standard†) ── [tech HARD check] ──►
         │
         ▼
    Test(standard†) ── [domain HARD+SOFT + tech HARD+SOFT FINAL check] ──[APPROVED]──►
         │
         ▼
    Pipeline(standard†) ── [tech HARD check]
    Tenant prereqs [APPROVE TENANT] (only if declared)
    Env prereqs (per environment, before its first deploy — C-TECH-050/051)
    Dev→Test  (auto)   → verify (a) query (b) re-run (c) human open+save
    Test→Prd  [APPROVE PRD]      ← ADR-006: Test and Acceptance are ONE environment
                                   on this project, so there is no Acc hop. The chain
                                   is whatever config/<slug>-pipeline.yml declares.
```

**Verification levels.** Build claims **V2 packaged**; pipeline claims **V3 accepted** and,
after the human open-and-save step, **V4 usable**; test claims **V5 executed**. No agent
reports a level it did not execute (`C-TECH-053`). See
`skills/how-to-verify-a-platform-contract.md`.

**Intake mode:** when requirements or a solution architecture arrive from outside the
system, Plan and Architect adopt the external document instead of authoring
(`skills/how-to-intake-external-documents.md`); their gates additionally present an
Adoption Report. Check points and everything downstream are unchanged.

---

## Gate Keywords

| Keyword | Effect |
|---|---|
| `APPROVED` | Proceed (only valid when constraint check is PASS or WARN) |
| `REQUEST RETEST` | Re-run tests at current scope |
| `APPROVE TENANT` | Execute tenant-level provisioning (app registrations, admin consent, groups, site collections, Teams catalog) |
| `APPROVE ACC` | Deploy to Acceptance — only where the pipeline config declares an `acc` environment. **This project has none** (ADR-006) |
| `APPROVE PRD` | Deploy to Production |
| `HOLD` | Pause any pipeline stage |

`APPROVED` is **invalid** when the constraint check status is `BLOCKED`.

---

## Handoff Format

```
HANDOFF | from:<agent> | to:<agent> | feature:<slug> | status:<STATUS> | doc:<path>
```

Append `| artifact:<path>` when a build artifact exists.

---

## Token Efficiency Rules

1. **Load-once:** Only lead-agent reads `WORKFLOW.md`; no agent re-reads a file already in this session's context
2. **Narrow knowledge:** Each agent loads only its declared `Knowledge to Load` files
3. **Templates on demand:** `templates/` loaded only when writing that document
4. **Skills inline:** Loaded at the step that needs them, not at activation
5. **Right-sized model:** `config/models.yml` resolves tiers (mechanical/standard/strategic) to model IDs; escalate only on the listed conditions
6. **Scoped constraints:** Each agent filters constraints by its own name in the `Scope` column
7. **Paths, not pastes:** Handoffs and sub-agent prompts reference documents by path — never inline their contents
8. **Cache-friendly ordering:** Stable context (knowledge, constraints, templates) first, per-feature content last — see `config/models.yml` → Prompt caching

---

## Sub-Agents (spawned by Development Agent)

| Sub-Agent | Tier | Responsibility |
|---|---|---|
| `data-agent` | standard | Schema, migrations |
| `backend-agent` | standard | APIs, services, business logic |
| `frontend-agent` | standard | UI components and views |
| `automation-agent` | standard | Workflows, event handlers, scheduled jobs |
| `identity-agent` | standard | App registrations, security roles, group teams, app sharing |
| `m365-agent` | standard | SharePoint sites, Teams provisioning, Teams app packages |
| `config-agent` | **mechanical** | Environment config, secrets, feature flags, deployment settings |

Sub-agents inherit the technology constraint check from the development-agent.

---

## Adding a New Agent

1. Create `agents/<n>-agent.md` — include a `**Tier:**` line (never a model ID) and a `Constraints to Check` section
2. Add an entry to `config/models.yml` under `agents:`
3. Add the agent name to the `Scope` column of any constraints it should enforce
4. Register in this file and in `agents/WORKFLOW.md` Agent Roster
5. Add a routing rule in `agents/lead-agent.md`
6. Add a one-line entry to `ROSTER_DESCRIPTIONS` (or `SUB_AGENT_DESCRIPTIONS_AND_SKILL` for a
   development-agent sub-agent) in `scripts/generate-subagents.py`, then run
   `python3 scripts/generate-subagents.py` — step 2 declares the tier, this step is what
   actually pins a model to it. `--check` fails CI if this step is skipped.
