# Mechanical Model Dispatch and Session Boundaries — 2026-08-21

**Mode:** Capability (`agents/lead-agent.md` → "Capability mode"; `IMP-0027`) — this changes the
system, not the product.
**Cites:** `IMP-0143`, `IMP-0144`.
**Gate:** `APPROVE IMPROVEMENTS` — given directly by the reviewer in this session ("Make the
suggested changes... make sure the agents switch to designated models mechanically... implement
the stop and handover fix as well"), in response to a cost/architecture review the reviewer
requested. Applied, then written up, per that instruction — the same pattern
`docs/improvements/2026-08-21-improvement-review-2.md` §Gate used for the same reason.

---

## 1. Problem

The reviewer measured **$98 of AI subscription usage on 2026-08-20 and 2026-08-21** and reported
"sessions are very long." Asked to audit as an AI system architect, the finding was: this
project runs its entire Lead → Plan → Architect → Development → Build → Test → Pipeline →
Improvement flow in **one continuous Claude Code conversation**, with the reviewer expecting the
tier declared in each `agents/*.md` file to switch the running model automatically. It does not,
and cannot — a model cannot redispatch itself to a different model mid-conversation from a
markdown instruction. The entire flow ran on Opus for two days.

Every cost control this system already declares — tiered pricing (`config/models.yml`), small
per-agent context, prompt-cache reuse — only pays off if an agent hop is a real, separately
priced invocation. None of `agents/*.md` defined a session-length or handover-restart rule
either, so nothing bounded how long an agent stayed "open" once dispatched.

## 2. What changed

| # | Change | Files |
|---|---|---|
| 1 | New generator: reads `config/models.yml` tiers, emits one Claude Code subagent definition per roster agent and per development-agent sub-agent, with the model pinned in frontmatter | `scripts/generate-subagents.py` (new) → `.claude/agents/*.md` (18 generated files) |
| 2 | Authoritative rule: a hop is a Task-tool dispatch to that subagent, never a persona switch; the dispatcher checks escalation conditions before dispatching and overrides the model explicitly when one fires; every agent stops at its gate output | `agents/WORKFLOW.md` → new "Session Boundaries" section |
| 3 | Delegation instructions rewritten to describe dispatch, not manual model application | `CLAUDE.md` §"When Delegating to Another Agent"; `agents/lead-agent.md` → new "How Delegation Happens"; `skills/how-to-select-a-model.md` §"Applying a Model Override" |
| 4 | `config/models.yml` header now states the mechanical path as primary, manual `ANTHROPIC_MODEL`/`--model` as fallback | `config/models.yml` (comment block only — no tier or model values changed) |
| 5 | Session-boundary / stop-condition pointer added to each delivery agent's own activation steps, so the rule is not only central (`IMP-0070`'s lesson: a rule absent from an activation sequence gets ignored) | `agents/plan-agent.md`, `agents/architect-agent.md`, `agents/development-agent.md`, `agents/test-agent.md`, `agents/build-agent.md`, `agents/pipeline-agent.md` |
| 6 | development-agent's own sub-agent fan-out made an explicit Task dispatch, not inline exploration | `agents/development-agent.md` → "Sub-Agents" |
| 7 | Fixed a stale drift found while cross-referencing tiers for (1): Build and Pipeline were re-tiered `standard` on 2026-08-17 but this index still said `Mechanical` — caught before the generator could have propagated it into a wrong model pin | `agents/README.md` (Agent Index table, Flow diagram) |
| 8 | Regenerated the learning digest | `logs/known-failure-modes.md` (via `scripts/generate-known-failure-modes.py`) |

Deliberately **not** done in this pass (reviewer scoped it out): a database for logs/knowledge
(recommendation #5 of the review — held off), and the two CI/provisioning automation gaps found
in the same review (provisioning cert secret on GitHub Environments; `promote_mode: cli`) — both
require the reviewer to handle a credential directly and one changes deploy behaviour against an
explicitly `not_verified` platform assumption (`config/revitalise-grant-automation-pipeline.yml:339`),
so they are named here as follow-ups, not silently dropped.

## 3. Why subagent dispatch, not a re-invoked CLI process

`skills/how-to-select-a-model.md` already documented a fallback path (`claude --model <id>` per
agent hop), which assumes the operator manually exits and restarts the CLI at every handoff. That
is exactly the manual-remembering failure this finding is about — asking the reviewer to
type a different flag ten times a day is the same class of problem as asking them to remember a
model switch that never happens. Claude Code's subagent feature (`.claude/agents/<name>.md`,
dispatched by the Task tool) pins a model in the subagent's own definition, so invoking it *is*
the model switch — mechanical, not remembered. The manual path stays documented as a fallback for
contexts with no Task tool.

## 4. Escalation, given a pinned model

A generated subagent file pins one model. `config/models.yml`'s `escalate_to_strategic_when` /
`de_escalate_to_mechanical_when` lists cannot be evaluated *by* a pinned subagent mid-run — it
would have to reason its way to "I should be a different model," which is the same
impossibility this whole finding is about. So escalation stays the **dispatcher's**
responsibility: check the condition list (rendered into each generated file for convenience)
before dispatching, and pass an explicit `model:` override on that one Task call when a condition
fires. No parallel "-strategic" subagent variants were generated; the override does the job with
one file per agent instead of two.

## 5. Verification

```
$ python3 scripts/generate-subagents.py
generate-subagents: wrote 18 files to .claude/agents.

$ python3 scripts/generate-subagents.py --check
generate-subagents: .claude/agents is current (18 files).

$ python3 scripts/verify-improvement-log.py
verify-improvement-log: OK (schema) — 141 entries (3 NEW, 138 APPLIED, 0 REJECTED) in logs/improvement-log.jsonl.

$ python3 scripts/generate-known-failure-modes.py --check
generate-known-failure-modes: logs/known-failure-modes.md is current (141 entries).
```

**Not verified in this pass:** an actual Claude Code session dispatching one of the 18 generated
subagents end-to-end — this repo change makes the mechanism available; the reviewer's next
feature run is the real test, per their own "I can re-test with other features and monitor
usage."

## 6. What the reviewer should watch for on the next feature

- Delegation should show up as separate Task-tool calls in the transcript, not as the top-level
  conversation narrating "now I am architect-agent."
- Per-hop cost should track the dispatched model, not the model the top-level conversation
  happens to be running on. The top-level/orchestrator thread is itself `lead-agent`, tier
  `mechanical` — if it is still launched on Opus by default, that thread's own routing overhead
  stays at Opus price even though everything it delegates should not. Switching the default
  launch model for that thread (`claude --model claude-haiku-4-5`, or a project
  `.claude/settings.json` default) is a further, separate lever the reviewer did not ask for in
  this pass and was not applied here — it changes day-to-day chat quality for ad-hoc questions,
  which is the reviewer's call, not a mechanical default.
- Each delivery agent should stop at its gate output rather than continuing to explore — if one
  keeps going, that is a finding against this change, not a one-off.

## 7. Retirements

None. No constraint row existed for this gap, so none is retired; the change added a script,
a generated directory, and doc updates.
