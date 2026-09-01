# Capability Design — Agent System Optimisation (2026-08-31)

**Author:** external audit, this conversation (Xander Lykopoulos, reviewer)
**Status:** DRAFT — not authorised. Requires `APPROVE IMPROVEMENTS` per workstream, same as any
other improvement-agent gate.
**Scope:** `system` only. No product/WBS work in this document. Non-billable throughout
(`C-COM-002`).
**Authorising basis:** capability mode per `agents/lead-agent.md` L33-L40 and
`agents/improvement-agent.md` L64-L80 — this document is the required design artifact; there are
no `IMP-` ids driving most of these (a handful are named where they exist as corroborating
evidence, not as the trigger).

---

## How to use this document

This is **not** an improvement review — it is the design document that authorises capability-mode
work, per the project's own rule that a request to add something the system has never had needs a
design document, not a set of findings. Each workstream below is written so it can be handed to
`improvement-agent` as its own dispatch:

```
ROUTED_TO:improvement-agent — capability mode, wbs:system, non-billable.
doc:docs/improvements/2026-08-31-capability-design-agent-system-optimisation.md#WS-<letter>
```

**Read "Parallel-safe dispatch groups" (bottom of this document) before dispatching more than one
workstream at once.** Several workstreams edit the same file (`agents/lead-agent.md`,
`agents/pipeline-agent.md`, `config/*-build.yml`) and this project has already paid twice for two
live sessions writing the same file concurrently (`IMP-0080`, `IMP-0538`) — do not repeat that
here. Workstreams sharing a file must be one dispatch, not two parallel ones.

Every workstream still runs behind its own `APPROVE IMPROVEMENTS` keyword and still obeys the
3-new-constraints-per-review cap and the retirement-consideration obligation
(`agents/improvement-agent.md` L282-L305) — this document does not waive either.

---

## WS-A — Scope `.claude/agents/*.md` tool grants to what each role needs

**Priority:** Medium
**Problem:** All 18 generated subagent definitions carry unrestricted tool access. `improvement-
agent`'s stated exclusivity over editing `agents/`, `constraints/`, `skills/`, `knowledge/`
(`CLAUDE.md` — "the only agent that edits this system's own rules") is enforced only by each
agent's own instructions choosing to comply, not by the harness.
**Requirement:** Every non-`improvement-agent` generated subagent definition is scoped so it
cannot call Edit/Write against `agents/`, `constraints/`, `skills/`, `knowledge/`. `improvement-
agent`'s own definition keeps full access to those paths.
**Mechanical verification:** `scripts/generate-subagents.py --check` still exits 0 after the
change, and a fixture dispatch attempting an out-of-scope edit from e.g. `build-agent` is refused
by the harness, not merely discouraged by prose.
**Files:** `scripts/generate-subagents.py`, `.claude/agents/*.md` (regenerated, not hand-edited).
**Constraint cap:** none required — this is a generator change, not a new constraint row.
**Decision this document cannot make:** whether tool scoping is expressed as a Claude Code
subagent-definition field or as a settings-level allowlist — depends on what the harness actually
supports for per-subagent tool restriction; confirm the mechanism before implementing.

---

## WS-B — Bound the growth of `logs/known-failure-modes.md`

**Priority:** High
**Problem:** 572 lines / 110KB at 430 entries, read in full by `build-agent`/`pipeline-agent` at
step 0 of every single activation (`agents/build-agent.md` L26-30, `agents/pipeline-agent.md`
L21-24), with no compaction. It is already the single largest static read in the system and grows
with every finding, forever.
**Requirement:** `scripts/generate-known-failure-modes.py` keeps the "Recurring classes" table
(the highest-value section) in full, and for single-instance, non-recurring, already-`APPLIED`
findings older than N reviews, collapses them to a one-line pointer into an appendix loaded only
on demand (not part of the file `build-agent`/`pipeline-agent` read by default).
**Mechanical verification:** `python3 scripts/generate-known-failure-modes.py --check` still
exits 0; the default-loaded file's byte size stays roughly flat as the log grows past 500, 600,
700 entries, measured by a simple size-over-time assertion in the script's own selftest.
**Files:** `scripts/generate-known-failure-modes.py`.
**Constraint cap:** none — generator change.
**Decision this document cannot make:** the cutoff N (reviews or days) for what moves to the
appendix. Recommend starting conservative (e.g. entries older than 60 days AND already `APPLIED`
AND not part of a recurring class) and measuring the size reduction before tightening further.

---

## WS-C — Separate narrative history out of `config/*-build.yml` / `*-pipeline.yml`

**Priority:** High
**Problem:** `config/revitalise-grant-automation-build.yml` is 1,425 lines, 1,143 of them (80%)
prose comments recording historical ADR resolutions and past incidents, not executable config.
`config/revitalise-grant-automation-pipeline.yml` carries the same pattern at smaller share
(133KB total). Both are read in full by `build-agent`/`pipeline-agent` on every dispatch, and the
cost is per-feature — a second feature slug generates its own equally verbose pair.
**Requirement:** The narrative/historical comment blocks move to a linked changelog document
(e.g. `docs/development/<slug>-build-config-history.md`), leaving the YAML itself close to purely
executable. Each moved block is replaced in the YAML by a one-line pointer citing the changelog
section, so nothing is lost, only relocated.
**Explicitly rejected alternative, and why:** moving the *read* itself to `lead-agent` (rather
than shrinking the file) does not reduce total tokens read — `build-agent` still needs the actual
executable content to run its steps, `lead-agent`'s context is the persistent root conversation
(not a bounded dispatch that discards context on completion, see WS-D), and pasting the config
content into a dispatch prompt violates the standing rule against pasting document content into a
handoff (`agents/WORKFLOW.md` L375-377, `CLAUDE.md` Token Rules). Shrinking the file itself is the
only change that actually reduces the read cost, regardless of who reads it.
**Mechanical verification:** `scripts/verify-build-config.py` and `scripts/verify-pipeline-
config.py` (or equivalent) still pass; comment-line share of the YAML measured below a stated
threshold (e.g. <20%).
**Files:** `config/revitalise-grant-automation-build.yml`, `config/revitalise-grant-automation-
pipeline.yml`, new `docs/development/*-build-config-history.md`.
**Constraint cap:** none.
**Note:** this touches the same file as WS-M and WS-K (both add steps to `config/*-build.yml`) —
see Parallel-safe groups.

---

## WS-D — Mechanical check that a dispatch was actually a fresh, bounded session

**Priority:** Critical
**Problem, part 1 (lead-agent tier):** `lead-agent` is loaded as the root conversation via
`CLAUDE.md`, never as a Task-tool dispatch — so it never actually runs on the `mechanical`/Haiku
tier `config/models.yml` L91-95 assigns it. `agents/lead-agent.md` L78-82 states this as a known
gap with no enforcement.
**Problem, part 2 (silent stalls):** the `dispatched-agent-stalls-silently` class has recurred
**8 times**, most recently `IMP-0537` on 2026-08-31 — hours *after* a prose-only fix (`IMP-0520`,
"preempt it in the prompt") was applied the same day. The finding itself states the correct next
step: *"a second recurrence after a prose fix is the ladder's signal to escalate altitude to a
mechanical dispatch-composition checklist."* This document adopts that conclusion rather than
re-arguing it.
**Requirement:**
1. Extend `scripts/verify-routing-reconciliation.py` (or add a sibling script) to flag a
   `ROUTED_TO` line whose target agent's default tier does not match its `GATE_RECEIVED` model
   identity, where that identity is knowable — surfacing tier-mismatch dispatches instead of
   relying on the dispatcher remembering to check.
2. Add a pre-dispatch check for any background-write dispatch (`pipeline-agent` in particular)
   that scans the dispatched agent's own final message for the stall signature — phrasing like
   "I'll wait for," "resume when," "once the notification arrives" — and refuses to accept that
   dispatch as terminal. This is a **mechanical gate**, not another instruction added to
   `agents/pipeline-agent.md` prose, per the altitude rule that a second recurrence after a prose
   fix must not get a third prose patch.
**Mechanical verification:** run both checks against the real corpus of past `ROUTED_TO`/
`GATE_RECEIVED` pairs and past dispatch final-messages before wiring either as HARD, per `agents/
improvement-agent.md` L367-400's own measurement discipline — report true/false positive counts
in the applying review, same as any other new gate.
**Files:** `scripts/verify-routing-reconciliation.py` (or a new sibling script),
`agents/WORKFLOW.md`, `agents/pipeline-agent.md`.
**Constraint cap:** likely needs 1 new HARD or SOFT constraint row (technology) — counts against
the 3-per-review cap for whichever review applies it.
**Decision this document cannot make:** whether the tier-mismatch check for `lead-agent`
specifically is enforceable at all given `lead-agent` is the root conversation, not a Task
dispatch — this may be a structural limit of the harness rather than something a script can close.
If so, say so explicitly in the applying review rather than shipping a gate that can never fire.

---

## WS-E — Exclude generic built-in agents from routing

**Priority:** Medium
**Problem:** `claude`, `general-purpose`, `Explore`, `Plan` are reachable via the same Task-tool
mechanism as the 18 project-specific agents. A dispatch to any of them silently skips every
constraint check, tier pin, gate keyword, and improvement-log capture this system depends on —
with no error, which makes it the highest-likelihood silent mis-route.
**Requirement:** `agents/lead-agent.md`'s routing table gains an explicit line: delivery/PM work
never routes to a generic built-in agent, and if the harness supports it, the four are excluded
from the roster available for this repository's Task dispatches.
**Mechanical verification:** none purely mechanical is available if the harness has no per-repo
subagent allowlist — in that case this is prose-only, which is an acceptable exception given no
script can constrain which subagent name a dispatch names. State that explicitly rather than
overclaiming enforcement.
**Files:** `agents/lead-agent.md`, `.claude/settings.json` (if a subagent allowlist field exists
— confirm before assuming).
**Constraint cap:** none, or 1 if expressed as a constraint row rather than routing-table prose.
**Note:** shares `agents/lead-agent.md` with WS-I — see Parallel-safe groups.

---

## WS-F — Deduplicate concurrent improvement-agent review batches before gating

**Priority:** Medium
**Problem:** on 2026-08-28, reviews 3 and 4 ran the same day, both touched the same underlying
defect, and produced a real collision (`IMP-0423` vs `IMP-0424`) requiring a dedicated
reconciliation dispatch to close.
**Requirement:** before two improvement-agent reviews are dispatched to run concurrently, a
cheap pre-check compares the finding-id sets each is scoped to process and flags any overlap
back to the dispatcher, rather than discovering the collision after both apply.
**Mechanical verification:** a script that takes two review-doc scopes (or two sets of unread
finding ids) and reports intersection, run before both dispatches are issued.
**Files:** `agents/improvement-agent.md` (activation step, dispatcher-facing note),
new `scripts/verify-review-scope-overlap.py` or similar.
**Constraint cap:** none, or 1 if made HARD at dispatch time.

---

## WS-G — Register the highest-traffic skills as native Claude Code Skills

**Priority:** Low
**Problem:** `.claude/skills/` is empty. All 23 `skills/*.md` files are loaded by hand-written
"Load X" prose duplicated inside every agent file that references them, rather than through the
Skill tool's own trigger/description mechanism already used elsewhere in this environment.
**Requirement:** the highest-traffic skills — `how-to-verify-a-platform-contract.md` (referenced
from 10 files), `how-to-report-to-the-reviewer.md`, `how-to-apply-constraints.md` — get a
`.claude/skills/<name>/SKILL.md` wrapper with an accurate trigger description, and the
corresponding "Load X" prose is removed from the agent files that referenced it by hand.
**Mechanical verification:** each agent file's own activation step still resolves to the same
content by a different path; no agent's behaviour changes, only how the file is discovered.
**Files:** new `.claude/skills/*/SKILL.md` tree, edits to every `agents/*.md` file that previously
hand-referenced the migrated skill.
**Constraint cap:** none.
**Decision this document cannot make:** whether native Skill-tool discovery composes correctly
with this project's own dispatch model (Task-tool subagents, not the interactive skill-invocation
flow) — test on one skill before migrating all three.

---

## WS-H — Split improvement-agent's discovery and apply steps by tier; broaden de-escalation generally

**Priority:** Medium
**Problem:** `improvement-agent` runs strategic/opus for its *entire* activation, including the
mechanical half of "apply an already-approved, already-narrowed diff and run the stated
verification commands." On 2026-08-28 alone this was ~7 strategic-tier dispatches in one day. Only
`pm-agent` currently has a `de_escalate_to_mechanical_when` clause (`config/models.yml` L226-229)
— every other agent's tier floor is fixed regardless of how mechanical a given instance turns out
to be.
**Requirement:** split `improvement-agent`'s activation into two phases with two tiers:
- **Discovery** (strategic, unchanged): clustering, altitude judgment, drafting the review
  document with literal proposed diffs, the regression check, the re-verify-before-apply step.
  This is exactly where `config/models.yml` L203-217's rationale ("wrong or over-broad constraint
  is sticky, expensive to reverse") applies, and stays strategic without exception.
- **Apply** (standard/sonnet, new): once a review is `APPROVE IMPROVEMENTS`'d and its diffs are
  literal, mechanically apply each one, run the review's own stated verification commands
  (`grep` needles, selftest, corpus measurement), do the incremental bookkeeping (status
  transitions, digest regeneration), and stop. **The WITHHOLD and NARROW-AND-REPORT branches
  (`agents/improvement-agent.md` L152-199) always escalate back to strategic tier or the human —
  never resolved silently by the apply step.** This preserves the exact safety property the
  strategic tier exists for (a wrong or premature change is expensive to reverse) while moving the
  genuinely mechanical majority of apply work off the most expensive tier.
**Mechanical verification:** `scripts/generate-subagents.py --check` after adding the new tier
split; measure apply-step token cost before/after on the next 5 reviews.
**Files:** `config/models.yml`, `agents/improvement-agent.md`, `scripts/generate-subagents.py`.
**Constraint cap:** none — tier/process change, not a new rule.
**Decision this document cannot make:** whether a WITHHOLD/NARROW-AND-REPORT case detected by the
apply-tier agent should re-dispatch strategic-tier itself, or simply halt and report back to the
human directly. Recommend the latter (halt and report) as the more conservative default until this
split has run cleanly a few times.
**Note:** shares `agents/improvement-agent.md` with WS-F — see Parallel-safe groups.

---

## WS-I — Split C-TECH-061 into a HARD blocker half and a SOFT batch-count half

**Priority:** Critical — highest priority in this document
**Problem:** `C-TECH-061` (`constraints/technology/technology-constraints.md` L131) is HARD and
fires on *either* an unresolved blocker *or* fewer-than-ten `NEW` entries in total — both
conditions gate `build-agent`'s dispatch identically. In practice a single healthy delivery
dispatch now routinely produces more than 10 findings by itself (`IMP-0406..IMP-0417`, 12 findings
from one development-agent gate output on 2026-08-28), so the batch half of this rule now trips on
ordinary, well-processed days, not only on the neglect scenarios (`IMP-0033`, days-old stale
queues) it was written for. This was the direct cause of an entire day (2026-08-28) and 3 of 11
build failures this week (2026-08-31 05:20, 17:52, 21:05) being consumed by improvement-review
cycles before a build could even start. `build-agent`'s own internal step-7b logic already treats
the two cases differently — only a blocker halts packaging; a crossed batch trigger is recorded
and reported, not fatal (`agents/build-agent.md`, "Warnings Are Findings" / step 7b table) — so
this brings the pre-dispatch check lead-agent runs into line with the discipline build-agent
already applies to itself mid-run, rather than inventing a new distinction.
**Requirement:**
1. `C-TECH-061`'s blocker half stays HARD and immediate, unchanged.
2. The batch-count half (`fewer than ten entries at NEW`) becomes SOFT ahead of a build dispatch:
   `lead-agent` may dispatch `build-agent` with an unresolved batch-trigger present, recording it,
   and `improvement-agent` processes the batch in parallel rather than as a precondition.
3. Separately, recalibrate the numeric threshold: 10 was set against multi-day neglect scenarios,
   not against single-dispatch output that now routinely exceeds it. Recommend measuring the
   typical finding count of a normal (non-neglected) development-agent/architect-agent dispatch
   over the last 20 gate outputs and setting the threshold above that median, not at a round
   number chosen in advance.
**Mechanical verification:** `python3 scripts/verify-improvement-log.py --check` distinguishes
blocker-only failure (exit non-zero, HARD) from batch-only trigger (exit 0 with a WARN line);
`agents/build-agent.md` step 7b's existing table becomes the shared behaviour, not a build-only
exception.
**Files:** `constraints/technology/technology-constraints.md` (C-TECH-061 row), `scripts/verify-
improvement-log.py`, `agents/lead-agent.md` (pre-dispatch check), `agents/build-agent.md`.
**Constraint cap:** this is an edit to an *existing* row, not a new one — does not count against
the 3-per-review cap, but confirm that reading with `constraints/README.md`'s own retirement/edit
procedure before applying.
**Note:** shares `agents/lead-agent.md` with WS-E, and `agents/build-agent.md` with WS-M — see
Parallel-safe groups.

---

## WS-J — Stop attempting `SendMessage` resume on improvement-agent; redispatch fresh

**Priority:** High
**Problem:** every `SendMessage` resume attempt on a parked improvement-agent or architect-agent
session recorded in this project's history has failed ("No transcript found for agent ID" —
`logs/routing.log` L334, three failures in one incident on 2026-08-28). `agents/WORKFLOW.md`
L89-153 documents this as a recurring, not occasional, class.
**Requirement:** `agents/WORKFLOW.md`'s dispatch-recovery guidance changes from "attempt resume,
fall back to fresh dispatch on failure" to "go straight to a fresh dispatch" for this specific
agent-role pattern, removing the now-consistently-wasted resume attempt and its round trip.
**Mechanical verification:** none available — this is a documented behavioural pattern, not
something a script can enforce. State plainly in the applying review that this is a prose-only
change, per the same honesty this document asks of WS-E.
**Files:** `agents/WORKFLOW.md`.
**Constraint cap:** none.
**Note:** shares `agents/WORKFLOW.md` with WS-D — see Parallel-safe groups. Small enough to fold
directly into WS-D's dispatch rather than running separately.

---

## WS-K — Add an automated visual/layout regression check

**Priority:** High
**Problem:** every real defect in the trustee-portal-visual-refresh feature's history — StatTile
wrapped-value line overlap (`IMP-0509`), wrong percentages, wrong chart shapes, layout defects
(`IMP-0525`, `IMP-0526`) — was caught by a human opening the live app after deploy, never by any
of the 65 `verify-*.py` gates. None of them check rendered/visual output. The project has already
started moving this direction tonight (`scripts/verify-css-line-height.py` replaced by `scripts/
verify-css-arithmetic.py`, per current `git status`) — this workstream is asking to broaden that,
not to start it from nothing.
**Requirement:** extend the CSS-arithmetic checking approach to cover percentage/proportion
correctness specifically (the class actually named in the most recent fix commit), not only line-
height. Where feasible, add a Playwright screenshot-diff step for the round-statistics landing
screen against a known-good baseline, gated SOFT initially (report, don't block) until its false-
positive rate is measured, per the same discipline `agents/improvement-agent.md` L367-400 already
requires of every new gate.
**Mechanical verification:** run the new check's `--selftest`, then against the real corpus of
past screenshots/known-bad layouts from this feature's own history, and report true/false positive
counts before deciding SOFT vs HARD.
**Files:** `scripts/verify-css-arithmetic.py` (extend), possibly a new `scripts/verify-visual-
regression.py`, `config/revitalise-grant-automation-build.yml` (new step).
**Constraint cap:** 1 new constraint likely (technology) once the gate is proven — counts against
the cap for whichever review adds it.
**Note:** shares `config/*-build.yml` with WS-C and WS-M — see Parallel-safe groups.

---

## WS-L — Lease/lock for concurrent pipeline-agent dispatches against the same feature+environment

**Priority:** High
**Problem:** on 2026-08-31, two live pipeline-agent dispatches reconciled the same build
concurrently with no lease or lock on `logs/pipeline.log`, producing a wrong operation-id
attribution (`IMP-0538`, new class). No data damage resulted only because both writes happened to
be idempotent — that is luck, not a control. This is the "two sessions can be live in this repo
at once" hazard (previously only observed against `logs/improvement-log.jsonl` id allocation,
`IMP-0080`) recurring in a more dangerous place: live writes against a real DEV environment.
**Requirement:** before `pipeline-agent` performs a live write (`pac solution import`, `pac code
push`, or any `provisioning/**/*.ps1` write) for a given feature+environment, it checks for and
writes a lease file (session id, timestamp, feature, environment) and refuses or waits if another
live lease already exists for the same feature+environment. The lease clears on that dispatch's
own terminal line.
**Mechanical verification:** a fixture test simulating two concurrent dispatches against the same
feature+environment — the second must wait or refuse, not proceed.
**Files:** `agents/pipeline-agent.md`, new `scripts/pipeline-lease.py` or similar, a new
gitignored lease-file location (e.g. `logs/state/pipeline-leases/`).
**Constraint cap:** 1 new constraint likely (technology, HARD).
**Note:** shares `agents/pipeline-agent.md` with WS-D — see Parallel-safe groups.

---

## WS-M — Batch independent static/source-level HARD gates into one collect-and-report pass

**Priority:** Medium
**Problem:** build-agent halts at the first HARD violation, one per attempt. On 2026-08-31,
11:30 → 12:20 → 13:05 → 13:15 was three separate ~20-minute build attempts (doc-line-links twice,
then unit-tests) before one finally succeeded — each surfacing exactly one problem before halting.
Several of the gates involved (doc-line-links, field-length-limits, design-doc-claims) are static,
source-level checks that do not depend on each other's outcome or on packaging having happened.
**Requirement:** identify the subset of `build-agent`'s HARD gates that are genuinely independent
static/source-level checks (not dependent on packaging or prior steps' output), run that subset to
completion regardless of individual failures, and report every violation found together — before
proceeding to the expensive dynamic steps (tests, packaging). Steps with a genuine dependency order
(e.g. anything requiring a packed artifact) stay sequential and fail-fast as today.
**Mechanical verification:** a build run against a fixture tree with 2+ independent static
violations reports both in one pass, not one-then-the-next-attempt.
**Files:** `agents/build-agent.md`, `config/revitalise-grant-automation-build.yml` (step grouping).
**Constraint cap:** none — process change to how existing gates are sequenced, not a new rule.
**Note:** shares `agents/build-agent.md` with WS-I, and `config/*-build.yml` with WS-C and WS-K —
see Parallel-safe groups.

---

## Parallel-safe dispatch groups

Group workstreams that touch the same file into **one** dispatch. Groups below can run in
parallel with each other; do not split a group across two concurrent dispatches.

| Group | Workstreams | Shared file(s) |
|---|---|---|
| 1 | WS-D, WS-J, WS-L | `agents/WORKFLOW.md`, `agents/pipeline-agent.md` |
| 2 | WS-I, WS-M | `agents/build-agent.md`, plus WS-I touches `agents/lead-agent.md` |
| 3 | WS-E | `agents/lead-agent.md` — **sequence after Group 2**, not concurrent with it, since both edit `agents/lead-agent.md` |
| 4 | WS-A, WS-H | `config/models.yml`, `scripts/generate-subagents.py` |
| 5 | WS-C, WS-K | `config/*-build.yml` — **sequence C before K** (shrink the file first, then add K's new step to the smaller version) |
| 6 | WS-F, WS-H | both touch `agents/improvement-agent.md` — **fold F into the same dispatch as WS-H**, not a separate one |
| 7 | WS-B | `scripts/generate-known-failure-modes.py` — standalone, fully parallel-safe |
| 8 | WS-G | `.claude/skills/`, various `agents/*.md` reference edits — standalone, fully parallel-safe |

Recommended first wave, given priority: **Group 2 (WS-I, WS-M) and Group 1 (WS-D, WS-J, WS-L)
first** — both contain the Critical/High items causing the most active cost this week. Groups
4-8 are lower-urgency and safe to run whenever capacity allows.

---

## Gate

Each group above requires its own `APPROVE IMPROVEMENTS` when improvement-agent drafts it as a
review against this design document. This document itself authorises the work existing; it does
not apply anything.
