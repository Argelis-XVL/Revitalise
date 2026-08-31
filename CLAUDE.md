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
environments:   [dev, tst_acc, prd]   # ADR-006: Test and Acceptance are ONE
                                     # environment. These are the exact keys used by
                                     # config/<slug>-pipeline.yml, .github/workflows/ci.yml
                                     # and the GitHub Environments — one spelling, everywhere.
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

**Delegation is a Task-tool dispatch, never a persona switch inside this conversation.**
(Added 2026-08-21, IMP-0143, after this project ran two full days of Haiku/Sonnet-tier work
on Opus because nothing ever actually dispatched a separate, pinned session — see
`agents/WORKFLOW.md` → "Session Boundaries" for the full rule.)

1. Dispatch the Task tool with `subagent_type: <agent-name>`. This loads
   `.claude/agents/<agent-name>.md` — generated from `config/models.yml` by
   `scripts/generate-subagents.py` — whose frontmatter pins the correct model automatically.
   You do not resolve or apply a model yourself; the dispatch does it.
2. Before dispatching, check `config/models.yml` → the target agent's
   `escalate_to_strategic_when` / `de_escalate_to_mechanical_when` conditions. If one is met,
   pass an explicit `model:` override on the Task call — the generated file only pins the
   *default* tier, and a subagent cannot escalate itself mid-invocation.
3. Pass the handoff line and doc path only — never pasted document contents; the dispatched
   agent reads its own knowledge, constraint, and template files by path (its `.md` file
   names exactly which ones).
4. Read back only the subagent's gate output. It stops there by design — a further
   instruction to it is a new dispatch, not a continued conversation.

## Reporting Rules (all agents)

Anything longer than a few paragraphs written back to the reviewer — a gate output's prose, a
completion report, an analysis — follows `skills/how-to-report-to-the-reviewer.md`. Load it
before writing, not after.

The three rules that get broken most:

- **Every identifier in prose is a clickable line-link** to where it lives
  (`[C-TECH-062](constraints/technology/technology-constraints.md#L132)`). Grep the line number;
  do not guess it. Never collect links into a references section at the bottom — the reviewer
  cannot tell which one belongs to which claim.
- **No `<details>` / `<summary>`.** They do not render as expandable in this client; they only
  add visible tag noise.
- **Conclusion first, then at most three sentences of rationale.** If it needs more, it belongs
  in a document the line-link points at.

Established by `IMP-0059` after three rejected drafts of one report. The content was right each
time; the shape made it unusable.

## Commercial Rules (all agents)

This engagement is governed by a **signed Service Agreement** and a **customer-accepted Work
Breakdown Structure**. Five rules follow, and they bind every agent, not just the PM ones:

1. **Work enters by WBS task id.** `contract/wbs.json` holds the 61 accepted tasks. Before any
   delivery work starts, the request resolves to task ids — or it goes to `commercial-agent` as a
   change-order decision first (`C-COM-002`). Build order comes from the contracted dependency graph
   (`scripts/wbs-ready-set.py`), not from whatever was asked for last.
2. **Hours only. No money in this repository.** No fee figure, hourly rate, currency amount or bank
   detail in any tracked file (D-3, `C-COM-004`). The rate lives outside the repo. This repository
   sits in a SharePoint library named after the client, and a rate in git history cannot be
   withdrawn.
3. **Never restate a baseline figure — cite the generated baseline.** `IMP-0029`: the approved SDD
   §10 stated 106–160 hours over 7 automations against a signed 292 over 9, and every downstream
   document inherited it (`C-COM-008`).
4. **A `Status` column is a claim, not a result.** Task state is derived from evidence and the claim
   is compared against it (`C-COM-005`). `IMP-0030`: task 0.4 read `Done` with five of the eight
   tables it names absent.
5. **Never claim a level above the evidence, and V6 is never inferred.** Client acceptance is
   recorded only from a dated `CLIENT ACCEPTED <phase> <date>` naming the person who accepted
   (`C-COM-006`). It starts a 60-day warranty window and fixes a liability cap.

A commercial gate **never** halts, retries or rolls back a build or a deploy. Delivery continues; the
finding is reported.

The reviewer's answers to the eight open commercial decisions are in
`docs/Import/baseline-lock.yml`. Read it before asking a question it already answers.

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
   `logs/improvement-log.jsonl` per `skills/how-to-log-an-improvement.md` — taking the id from
   `python3 scripts/allocate-improvement-id.py`, never from `tail -1` — then run **both**
   commands, **validator first**:
   `python3 scripts/verify-improvement-log.py` (authoritative), then
   `python3 scripts/generate-known-failure-modes.py`. Report it in your gate output on one
   line, **even when the answer is none**.

   **Regenerating the digest is not validation.** This rule named only the generator until
   2026-08-28, and the generator validated nothing: three agents appended eleven malformed
   entries and two duplicate ids on 2026-08-27, each saw exit 0, and the halted build was the
   first anyone noticed (`IMP-0369`).

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
│   ├── pm-agent.md                  ← plan of record: baseline, task state, queue, schedule, status
│   ├── commercial-agent.md          ← hours, change orders, invoices
│   ├── acceptance-agent.md          ← phase acceptance, warranty clock, handover
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
│   ├── commercial/
│   │   └── commercial-constraints.md ← C-COM-nnn: hours, invoicing, acceptance, the baseline
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
│   ├── how-to-select-a-model.md     ← model escalation decision framework
│   └── how-to-report-to-the-reviewer.md ← output shape for anything the reviewer reads
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
├── contract/                        ← the commercial spine (generated or gated; hours only)
│   ├── README.md                    ← what is here, and the two rules that govern it
│   ├── wbs.json                     ← GENERATED: the 61 accepted tasks + dependency graph
│   ├── service-agreement.json       ← GENERATED: phase hours + milestone dates, read from the PDF
│   ├── source-lock.json             ← GENERATED: sha256 of every contractual source
│   ├── evidence-map.json            ← WBS task → the evidence that proves its deliverable
│   ├── external-dependencies.json   ← each precondition's state, owner and age
│   ├── delivery-parameters.json     ← capacity + the estimating rule (NOT contractual)
│   ├── known-exceptions.json        ← accepted gate violations, each owned and dated
│   ├── acceptance/                  ← phase acceptance records (Agreed Specification, B1)
│   ├── invoices/  change-orders/  handover/
├── logs/
│   ├── routing.log  build.log  pipeline.log  pm.log   ← one line per action
│   ├── improvement-log.jsonl        ← append-only findings (all agents write)
│   ├── worklog.jsonl                ← append-only work sessions (commercial-agent only)
│   ├── commercial-events.jsonl      ← append-only record of authorised commercial acts
│   ├── state/                       ← GENERATED: wbs-state, baseline-drift (do not hand-edit)
│   └── known-failure-modes.md       ← GENERATED digest; the read path (do not hand-edit)
├── scripts/                         ← executable gates + the two generators
├── Designsystem/                    ← SUPPLIED ASSETS. Untracked, ships nothing, read by no gate.
│                                      Owner: architect-agent. See the rule below.
└── .github/workflows/ci.yml
```

### Supplied assets: every input surface names its owning agent

**Added 2026-08-28 (`IMP-0028`, `IMP-0384` — second instance of `input-type-with-no-owning-agent`,
so this is a RULE for any supplied artefact, not a row for one directory).**

A brand, design or reference artefact supplied by the client **can arrive anywhere in the tree,
not only in `docs/Import/`**. When one does, four things are established **before** anything is
designed against it, and stated where the next agent will look:

| Question | For `Designsystem/`, verified 2026-08-28 |
|---|---|
| **Tracked?** | **No.** 0 tracked files; `git status` shows `?? Designsystem/`. Not gitignored either — simply never added |
| **Does it ship?** | **No.** Nothing under it reaches a solution, an artifact or a bundle |
| **Read by any build step?** | **No.** No `config/*.yml` step, workflow or script references it |
| **Which agent owns intake?** | **`architect-agent`**, and its placement outside `src/` is `ADR-034` — an architecture decision, not an existing rule |

**The failure mode this prevents is silence, not error.** `docs/Import/` accepts any document, but
`skills/how-to-intake-external-documents.md` carries exactly two checklists — SDD-shaped and
TAD-shaped — and is declared *"used by plan-agent and architect-agent"*. So a commercial or
operational source dropped there **maps to no checklist and is silently unread**: `IMP-0028` was
the WBS quoting workbook that a plan document cited as the basis of its own estimate. `IMP-0384`
was the same defect from the other direction — a design system arriving in a directory named
nowhere at all, so nothing said whether it was tracked, deployable, ignored, or read.

**Note the correction.** `IMP-0384` describes `Designsystem/` as *"a tracked repository
directory"*. It is not tracked; that was checked when this rule was written, and the row above is
the measured answer. A supplied artefact's status is established by running the check, never by
inferring it from the fact that the files are visible.

**No gate enumerates top-level directories against this layout, and that is deliberate.** The
corpus is 14 directories, one of them untracked, and a gate reading a prose layout block would be
asserting against a markdown code fence. A third instance is what would justify building one.
