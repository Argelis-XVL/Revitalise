# Skill: How to Apply Constraints

Used by: all agents that have a `Constraints to Check` section

---

## What This Skill Covers

How to load constraint files, run a constraint check, produce the required gate output,
and respond correctly to HARD and SOFT violations.

---

## Step 1: Load the Right Constraint Files

Each agent's `Constraints to Check` section lists exactly which constraint files to load
and which severity levels to evaluate. Load only those files — do not load constraint files
not listed for your agent.

Constraint files live in:
- `constraints/domain/domain-constraints.md`  (and any additional domain files)
- `constraints/technology/technology-constraints.md`  (and any additional tech files)

---

## Step 2: Filter to Your Scope

Each constraint row has a `Scope` column listing which agents must check it.
**Only evaluate constraints that include your agent name in the Scope column.**

This keeps the check set small and precise. Do not evaluate constraints outside your scope —
that is another agent's responsibility.

---

## Step 3: Evaluate Each In-Scope Constraint

For each constraint in your scope:

1. Read the `Verify By` column — this is your pass criterion
2. Check whether the current document, code, or config satisfies that criterion
3. Record the result as `PASS`, `VIOLATION` (HARD), `WARNING` (SOFT), or **`UNEVALUABLE`**

Evaluation order: check all HARD constraints first, then SOFT.

**When `Verify By` is a command, capture its exit code bare** (added 2026-08-21, `IMP-0163`):

```bash
out=$(python3 scripts/verify-something.py 2>&1); rc=$?
```

Never read the status through a pipe — `cmd | tail` reports the exit code of `tail` — and never
via `PIPESTATUS`, which is bash-only and silently empty in this environment's zsh. A gate that
appears to contradict its own output is almost always this measurement artefact and not a gate
defect: **re-run it bare before reporting it as broken.** One review spent a cluster on a "gate
that exits 0 while printing FAILED" that did nothing of the kind.

### `UNEVALUABLE` — the outcome this skill was missing until 2026-08-19

A constraint is `UNEVALUABLE` when you **cannot decide** whether it passes, because the rule
or its verification is not usable as written:

| Situation | Example |
|---|---|
| The rule text is a placeholder | `C-DOM-030: [PLACEHOLDER] Replace with your first domain-specific constraint` |
| `Verify By` names no usable procedure | `[Verification method]` |
| `Verify By` names a tool or artefact this project does not have | "Dependency scan step in `build.yml`" when the build declares none |
| The rule presupposes a technology not in this stack | "SQL queries must use parameterised queries" in a project with no SQL layer |

**Never record such a constraint as `PASS`.** That is what this project did, silently, for
every gate of every feature it has shipped. `C-DOM-030` is HARD and in architect-agent's
scope; its rule text is the scaffolding's own placeholder, so it can never be violated, so it
always passed and inflated every `<n passed> / <n total>` count that any agent has ever
reported (`IMP-0035`, `blocker`).

A HARD constraint that cannot be evaluated is the constraint-file equivalent of a gate that
cannot fail: it manufactures the confidence that stops anyone looking. So:

- **HARD + `UNEVALUABLE` → the gate is `BLOCKED`**, exactly as a violation would be. The
  resolution is not to force a judgement — it is to fix the constraint (write the rule, or
  retire the row) via `improvement-agent` behind `APPROVE IMPROVEMENTS`, then re-check.
- **SOFT + `UNEVALUABLE` → `WARN`**, listed by ID with the reason.

Log an improvement-log finding the first time you meet one (`skills/how-to-log-an-improvement.md`
trigger 2 — reality contradicted a document in this repo). One line, and the next agent
inherits the knowledge instead of rediscovering it.

---

## Step 4: Produce the Constraint Check Block

Append this block to your gate output, **before** the approval prompt.
Never omit this block. If no constraints apply to your agent, output the block with all zeros.

```
CONSTRAINT CHECK
Domain   HARD: <n passed> / <n evaluable> of <n in scope>  |  violations: C-DOM-002  (or NONE)
                                                           |  unevaluable: C-DOM-030 (or NONE)
Domain   SOFT: <n in scope>                                |  warnings:   C-DOM-011  (or NONE)
Tech     HARD: <n passed> / <n evaluable> of <n in scope>  |  violations: C-TECH-003 (or NONE)
                                                           |  unevaluable: NONE
Tech     SOFT: <n in scope>                                |  warnings:   C-TECH-009 (or NONE)
Overall: PASS | BLOCKED | WARN
```

The denominator is **evaluable** constraints, not all in-scope constraints. A row you could
not assess is reported on its own line, never folded into the pass count — the whole point of
the count is that it means something.

**Overall status rules:**
- `BLOCKED` — one or more HARD violations **or** one or more HARD `UNEVALUABLE` rows
- `WARN` — zero of the above, and one or more SOFT warnings or SOFT `UNEVALUABLE` rows
- `PASS` — zero violations, zero warnings, zero unevaluable rows

---

## Step 5: Act on the Result

### If BLOCKED
- Do not emit the approval prompt
- Do not accept `APPROVED` from the human — it is not valid while `BLOCKED`
- Output instead:

```
GATE BLOCKED
Reason: HARD constraint violation(s) and/or unevaluable HARD constraint(s)
        — see CONSTRAINT CHECK above.
Resolve the violations listed and re-run this agent to re-check.
Unevaluable rows are fixed by improvement-agent (APPROVE IMPROVEMENTS), not by you.
```

- Stop and wait. Revision cycle applies (max 3 attempts per WORKFLOW.md).

### If WARN
- Emit the normal approval prompt
- Add below the prompt:

```
⚠️ SOFT constraint warning(s) present — see CONSTRAINT CHECK above.
Human reviewer must explicitly acknowledge: respond APPROVED to accept the risk,
or give feedback to resolve the warnings before approving.
```

### If PASS
- Emit the normal approval prompt with no additional constraint messaging

---

## Violation Description Format

When listing a violation, provide one line of context per violated constraint ID:

```
CONSTRAINT CHECK
Tech  HARD: 2 / 3  |  violations: C-TECH-001, C-TECH-005
  C-TECH-001: Hardcoded API key found in src/services/payment.ts line 42
  C-TECH-005: String concatenation in SQL query — src/repos/order-repo.ts line 88
Tech  SOFT: NONE
Domain: not in scope for this agent
Overall: BLOCKED
```

The violation description must be specific enough for the developer to locate and fix the issue
without needing to ask a follow-up question.

---

## Re-Running After a Fix

After a BLOCKED gate is resolved:
1. The agent re-runs its constraint check from Step 2
2. If the previously violated constraints now pass, the agent proceeds to its normal gate output
3. The revision counter in WORKFLOW.md increments — the fix counts as one revision cycle

---

## Common Mistakes

| Mistake | Correct behaviour |
|---|---|
| Skipping the constraint check because output "looks compliant" | Always run the full check — do not rely on intuition |
| Checking constraints outside your scope | Only check constraints that list your agent in `Scope` |
| Accepting `APPROVED` while status is `BLOCKED` | `BLOCKED` gates cannot be approved — require resolution first |
| Marking SOFT violations as HARD | Use the severity defined in the constraint file, not your own judgement |
| Omitting the violation description line | Always provide a specific location — not just the constraint ID |
| **Recording a placeholder or inapplicable constraint as `PASS`** | **Record it `UNEVALUABLE`. A HARD row you cannot assess blocks the gate — see Step 3 (`IMP-0035`)** |
| Fixing a broken constraint row yourself to clear your own gate | Only `improvement-agent`, behind `APPROVE IMPROVEMENTS`, edits `constraints/`. Report it and log a finding |
