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
3. Record the result as `PASS`, `VIOLATION` (HARD), or `WARNING` (SOFT)

Evaluation order: check all HARD constraints first, then SOFT.

---

## Step 4: Produce the Constraint Check Block

Append this block to your gate output, **before** the approval prompt.
Never omit this block. If no constraints apply to your agent, output the block with all zeros.

```
CONSTRAINT CHECK
Domain   HARD: <n passed> / <n total in scope>  |  violations: C-DOM-002, C-DOM-007  (or NONE)
Domain   SOFT: <n total in scope>               |  warnings:   C-DOM-011             (or NONE)
Tech     HARD: <n passed> / <n total in scope>  |  violations: C-TECH-003            (or NONE)
Tech     SOFT: <n total in scope>               |  warnings:   C-TECH-009            (or NONE)
Overall: PASS | BLOCKED | WARN
```

**Overall status rules:**
- `BLOCKED` — one or more HARD violations exist (domain or tech)
- `WARN` — zero HARD violations, one or more SOFT warnings exist
- `PASS` — zero violations and zero warnings

---

## Step 5: Act on the Result

### If BLOCKED
- Do not emit the approval prompt
- Do not accept `APPROVED` from the human — it is not valid while `BLOCKED`
- Output instead:

```
GATE BLOCKED
Reason: HARD constraint violation(s) — see CONSTRAINT CHECK above.
Resolve the violations listed and re-run this agent to re-check.
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
