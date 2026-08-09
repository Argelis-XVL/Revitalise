# Multi-Agent Development System

A structured, technology-agnostic multi-agent system for building software with
human-in-the-loop approval gates, YAML-driven builds and deployments, and full documentation trails.

Built for **Claude Code** (`claude` CLI).

---

## Quick Start

### 1. Configure the project
Edit the `⚙️ Project Configuration` block in `CLAUDE.md`.

### 2. Populate knowledge
| Directory | What to add |
|---|---|
| `knowledge/domain/` | Domain rules, regulations, glossary — see `knowledge/domain/README.md` |
| `knowledge/technology/` | Stack reference, coding standards — see `knowledge/technology/README.md` |

### 3. Start Claude Code
```bash
npm install -g @anthropic-ai/claude-code
cd multi-agent-dev-system
claude
```

Claude reads `CLAUDE.md` on startup and responds: **"Lead Agent ready."**

### 4. Run a feature end-to-end
Respond to each gate keyword as the agents prompt you:

```
APPROVED          → proceed past Plan / Architecture / Dev / Test gate
REQUEST RETEST    → re-run tests
APPROVE ACC       → deploy to Acceptance
APPROVE PRD       → deploy to Production
HOLD              → pause the pipeline
```

---

## How It Works

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
                                                               Dev→Test  (auto)
                                                               Test→Acc  [APPROVE ACC]
                                                               Acc→Prd   [APPROVE PRD]
```

Every agent produces a structured document. Every transition past a gate requires
an explicit keyword from you — nothing deploys automatically to Acc or Prd.

**Externally authored documents:** if your requirements or solution architecture are
written outside this system, the plan- and architect-agents run in **intake mode** —
they adopt your document (map it onto the SDD/TAD template, normalise formats, report
every gap and out-of-scope component) instead of authoring one. See
`skills/how-to-intake-external-documents.md` for the procedure and the checklist of
sections your documents must arrive with.

---

## YAML-Driven Build and Deployment

The development-agent generates two YAML config files per feature:

### `config/<slug>-build.yml`
Defines every build step — clean, install, lint, compile, test, package.
The build-agent executes these steps in order and halts on any failure.
No build logic lives in the agent prose.

### `config/<slug>-pipeline.yml`
Defines per-environment deploy commands, gates, smoke tests, rollback commands,
notifications, and escalation contacts.
The pipeline-agent reads this file and executes it — no deployment logic in agent prose.

This means you can review and version-control the exact commands that will
run against each environment before any deployment happens.

---

## Token Efficiency

Four rules keep context window usage low as the project grows:

| Rule | What it means |
|---|---|
| **Load-once** | Only lead-agent reads `WORKFLOW.md`; no file is re-read once it's in the session context |
| **Narrow knowledge** | Each agent declares exactly which files it needs — not "load all domain" |
| **Templates on demand** | `templates/` files are loaded only when the agent is about to write that document |
| **Skills inline** | Each agent loads a skill at the step that needs it, not at activation |
| **Paths, not pastes** | Handoffs reference documents by path; contents are never inlined |
| **Tiered models** | `config/models.yml` maps each agent to the cheapest capable model tier, with explicit escalation conditions |
| **Cache-friendly ordering** | Stable context (knowledge, constraints) first, per-feature content last — maximises Anthropic prompt-cache hits |

---

## Repository Structure

```
multi-agent-dev-system/
├── CLAUDE.md                        ← entry point + project config (edit first)
├── README.md
├── .gitignore
├── agents/
│   ├── README.md                    ← agent index and design notes
│   ├── WORKFLOW.md                  ← gates, handoff contract, logging
│   ├── lead-agent.md
│   ├── plan-agent.md
│   ├── architect-agent.md
│   ├── development-agent.md
│   ├── test-agent.md
│   ├── build-agent.md
│   └── pipeline-agent.md
├── templates/
│   ├── sdd-template.md
│   ├── tad-template.md
│   ├── dev-summary-template.md
│   ├── test-report-template.md
│   └── deployment-summary-template.md
├── config/
│   ├── build.yml.example            ← copy → <slug>-build.yml
│   └── pipeline.yml.example         ← copy → <slug>-pipeline.yml
├── skills/
│   ├── how-to-write-requirements.md
│   ├── how-to-intake-external-documents.md
│   ├── how-to-ask-clarifying-questions.md
│   ├── how-to-estimate-effort.md
│   ├── how-to-document-architecture.md
│   ├── how-to-model-a-data-schema.md
│   ├── how-to-design-a-workflow.md
│   ├── how-to-review-code.md
│   ├── how-to-write-a-test-plan.md
│   ├── how-to-write-a-deployment-runbook.md
│   ├── accessibility-checklist.md
│   ├── compliance-checklist.md
│   └── data-classification.md
├── knowledge/
│   ├── domain/README.md
│   └── technology/README.md
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
│   ├── routing.log
│   ├── build.log
│   └── pipeline.log
└── .github/workflows/ci.yml
```

---

## Connecting CI/CD to Config YAML

The GitHub Actions workflow in `.github/workflows/ci.yml`:

1. Derives the feature slug from the branch name (`feature/<slug>`)
2. Verifies `config/<slug>-build.yml` and `config/<slug>-pipeline.yml` exist
3. Executes build steps from the build config
4. Deploys using deploy commands from the pipeline config
5. Uses GitHub Environment protection rules to enforce the Acc and Prd gates

To wire up a real step, replace each `TODO` comment with a command that reads
the relevant field from the YAML config — for example using `yq`:

```bash
COMMAND=$(yq '.steps[] | select(.name == "build") | .command' config/my-feature-build.yml)
eval "$COMMAND"
```

---

## Adapting to Your Stack

Everything platform-specific lives in `knowledge/technology/`.
See `knowledge/technology/README.md` for the suggested file list and template.

## Adapting to Your Domain

Everything domain-specific lives in `knowledge/domain/`.
See `knowledge/domain/README.md` for the suggested file list and template.

## Extending the System

To add a new agent, follow the pattern in `agents/README.md`.
To add a new skill, create `skills/how-to-<name>.md` and reference it inline
in the relevant agent's `Steps and Inline Skills` table.
