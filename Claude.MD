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
3. Confirm: **"Lead Agent ready. What would you like to build?"**

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
│   └── pipeline-agent.md
├── templates/                       ← document templates (loaded on demand)
│   ├── sdd-template.md
│   ├── tad-template.md
│   ├── dev-summary-template.md
│   ├── test-report-template.md
│   └── deployment-summary-template.md
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
│   └── deployments/
├── build/
│   ├── exports/                     ← gitignored
│   └── artifacts/                   ← gitignored
├── logs/
└── .github/workflows/ci.yml
```
