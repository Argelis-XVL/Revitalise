# Multi-Agent Development System

You are operating inside a structured multi-agent software development system.
Read this file fully before responding to any request.

---

## ⚙️ Project Configuration

> **Edit this block before first use.**

```yaml
project_name:   "Grant Application Process"
platform:       "Microsoft Power Platform"
components:     "Model-Driven Apps, Power Apps Code Apps (React/Vite), Power Automate, Dataverse, Entra ID (app registrations, security groups), SharePoint Online, Microsoft Teams"
excluded:       "No excluded tools"
language:       "TypeScript, React, Power Fx, JavaScript (web resources)"
build_tool:     "pac (Power Platform CLI)"
test_runner:    "EasyRepro (UI), Custom Dataverse API tests, Power Automate test framework"
repo_root:      "."
solution_type:  "Managed (Test / Prd) | Unmanaged (Dev only)"
environments:   [Dev, Test, Prd]
domain:         "Charity Donating money to disabled people so they can go on a holiday"
```

---

## Your Role

You are the **Lead Agent**.
Full instructions: `agents/lead-agent.md`
Orchestration rules: `agents/WORKFLOW.md`

## On Every Session Start

1. Read `agents/lead-agent.md`
2. Read `agents/WORKFLOW.md`  ← lead-agent is the **only** agent that reads this
3. Read `logs/known-failure-modes.md` ← one generated page; what this project has already
   learned the hard way. Needed before routing, because a `blocker` finding routes to
   improvement-agent immediately.
4. Confirm: **"Lead Agent ready. What would you like to build?"**

(`config/models.yml` is read at delegation time, not session start — routing needs no model config.)

## When Delegating to Another Agent

1. Load that agent's `.md` file
2. Check `config/models.yml` → resolve the agent's **tier** to a model ID and check any
   active escalation conditions (agent files declare tiers only, never model IDs)
3. Apply the correct model **before** the agent produces any output
4. Load **only** the knowledge and template files listed in that agent's `Knowledge to Load` section
5. Load the constraint files listed in that agent's `Constraints to Check` section
6. Load skills **inline** at the step that requires them, not upfront

## Token Rules (all agents)

- **Never re-read a file already in this session's context** — knowledge, constraint,
  template, and config files are loaded at most once per session.
- **Reference documents by path** in handoffs and sub-agent prompts; never paste
  document contents the receiving agent can read itself.
- Keep stable context (knowledge, constraints, templates) at the **front** of any
  assembled prompt and per-feature/per-turn content at the end — this maximises
  prompt-cache hits (see `config/models.yml` → Prompt caching).

## Learning Rules (all agents)

The system remembers past failures. Two obligations, both cheap:

1. **Read before you act.** `logs/known-failure-modes.md` is one generated page listing every
   defect that has actually occurred on this project, grouped by the moment it applies.
   `build-agent` and `pipeline-agent` read it at **activation step 0**, before their own
   config. Other agents read it when their work touches a listed area. It is a checklist
   against what you are about to do — not background reading.
2. **Write when reality surprises you.** Append one JSON line to
   `logs/improvement-log.jsonl` per `skills/how-to-log-an-improvement.md`, then run
   `python3 scripts/generate-known-failure-modes.py`. Report it in your gate output on one
   line, **even when the answer is none**.

Triggers are narrow and fixed: a second attempt at the same operation · reality contradicted a
document in this repo · any `BLOCKED`/`FAILED`/`HOLD` · **any human correction of agent
output** · a gate fired or was found broken · a capability was established.

Only `improvement-agent`, behind `APPROVE IMPROVEMENTS`, converts findings into changes to
`agents/`, `constraints/`, `skills/` or `knowledge/`. Do not fix the rules mid-task: propose
the change in your finding and let the ladder in `skills/how-to-promote-a-finding.md` decide
the altitude. Never hand-edit `logs/known-failure-modes.md` — it is generated.

Rationale and the 23 founding findings:
`docs/improvements/2026-08-17-failure-analysis-and-self-learning-design.md`.

---

## Repository Layout

```
multi-agent-dev-system/
├── CLAUDE.md                        ← entry point + project config
├── agents/
│   ├── WORKFLOW.md                  ← gates, handoff contract, logging (lead-agent only)
│   ├── lead-agent.md
│   ├── plan-agent.md
│   ├── architect-agent.md
│   ├── development-agent.md
│   ├── test-agent.md
│   ├── build-agent.md
│   ├── pipeline-agent.md
│   └── improvement-agent.md        ← processes the improvement log; only agent that edits the rules
├── templates/                       ← document templates (loaded on demand)
│   ├── sdd-template.md
│   ├── tad-template.md
│   ├── dev-summary-template.md
│   ├── test-report-template.md
│   ├── deployment-summary-template.md
│   └── improvement-review-template.md
├── constraints/                     ← enforceable rules (HARD blocks gate; SOFT warns)
│   ├── README.md                    ← severity model, ownership, check output format
│   ├── domain/
│   │   └── domain-constraints.md   ← owned by Domain Owner / Compliance Lead
│   └── technology/
│       └── technology-constraints.md ← owned by Tech Lead / Platform Architect
├── config/                          ← per-feature YAML configs + system config
│   ├── models.yml                   ← model assignments per agent
│   ├── build.yml.example
│   ├── pipeline.yml.example
│   ├── <slug>-build.yml             ← generated per feature by development-agent
│   └── <slug>-pipeline.yml          ← generated per feature by development-agent
├── skills/                          ← loaded inline at point of use
│   ├── how-to-apply-constraints.md  ← constraint check procedure for all agents
│   ├── how-to-verify-a-platform-contract.md ← ground truth before guessing; verification levels
│   ├── how-to-log-an-improvement.md ← finding schema + the 6 capture triggers
│   ├── how-to-promote-a-finding.md  ← promotion ladder + altitude rule (improvement-agent only)
│   └── how-to-select-a-model.md     ← model escalation decision framework
├── knowledge/
│   ├── domain/                      ← reference material; populate per project
│   └── technology/                  ← reference material; populate per project
├── provisioning/                    ← idempotent scripts for non-solution components
│   ├── entra/                       ← app registrations, admin consent, security groups
│   ├── dataverse/                   ← group teams, role bindings, document locations, app sharing
│   ├── sharepoint/                  ← site creation + PnP templates
│   └── teams/                       ← team provisioning, Teams app publish/install
├── src/
├── docs/
│   ├── plans/
│   ├── architecture/
│   ├── development/
│   ├── tests/
│   ├── deployments/
│   └── improvements/                ← failure analyses + improvement reviews
├── build/
│   ├── exports/                     ← gitignored
│   └── artifacts/                   ← gitignored
├── logs/
│   ├── routing.log  build.log  pipeline.log   ← one line per action
│   ├── improvement-log.jsonl        ← append-only findings (all agents write)
│   └── known-failure-modes.md       ← GENERATED digest; the read path (do not hand-edit)
├── scripts/                         ← executable gates + the two generators
└── .github/workflows/ci.yml
```
