# Constraints

Constraints are **enforceable rules** with explicit severity and clear pass/fail semantics.

They are distinct from knowledge files (`knowledge/`), which are reference material agents
read to be informed. Constraints are rules agents must actively check and report on at
defined points in the workflow. Violations are never silently ignored.

---

## Constraints vs Knowledge

| | `knowledge/` | `constraints/` |
|---|---|---|
| Purpose | Inform agent decisions | Enforce project boundaries |
| Format | Reference documentation | Structured rule tables |
| Agent action | Read and apply | Check, report, and block or warn |
| Owned by | Project team generally | Domain owner / Tech lead specifically |
| Violation consequence | n/a | HARD: gate blocked; SOFT: warning logged |

---

## Severity Levels

### HARD
The agent **cannot** emit `APPROVED` at its gate if a HARD constraint is violated.
The gate output must list every violated HARD constraint explicitly.
The agent emits `BLOCKED` status and stops until the violation is resolved.

### SOFT
The agent **may** proceed past its gate but **must** document the violation in its
gate output as a warning. The human reviewer decides whether to accept the risk.

---

## Directory Structure

```
constraints/
├── README.md                          ← this file
├── domain/
│   └── domain-constraints.md          ← business, regulatory, compliance rules
│       (add additional files per sub-domain as needed)
└── technology/
    └── technology-constraints.md      ← platform, language, security, tooling rules
        (add additional files per concern area as needed)
```

---

## Constraint ID Format

```
C-DOM-<nnn>   Domain constraint
C-TECH-<nnn>  Technology constraint
```

IDs are stable — never renumber or reuse a retired ID.
To retire a constraint, mark it `status: retired` and add a `retired_reason`.

---

## Which Agents Check Which Constraints

| Agent | Domain Constraints | Technology Constraints |
|---|---|---|
| plan-agent | ✅ All HARD at SDD completion | — |
| architect-agent | ✅ All HARD + SOFT | ✅ All HARD + SOFT |
| development-agent | ✅ HARD only (via TAD) | ✅ All HARD + SOFT |
| test-agent | ✅ All HARD + SOFT (final verifier) | ✅ All HARD + SOFT (final verifier) |
| build-agent | — | ✅ Build-scoped HARD only |
| pipeline-agent | — | ✅ Deploy-scoped HARD only |

---

## Constraint Check Output Format

Every agent must append a constraint check block to its gate output.
The block format, status rules (`PASS` / `BLOCKED` / `WARN`), and step-by-step
procedure are defined in **one place**: `skills/how-to-apply-constraints.md`.
Do not restate the format here or elsewhere — agents load that skill at check time.

---

## Updating Constraints

Constraints are living documents. Update them when:
- Regulations change
- A new technology is adopted or deprecated
- A post-incident review reveals a gap
- A project decision changes an approved pattern

Every constraint change should be reviewed by its owner (domain owner or tech lead)
and committed as a pull request — not edited directly on the main branch.

---

## Adding a New Constraint

Only **improvement-agent**, behind `APPROVE IMPROVEMENTS`, adds or retires constraints. No
delivery agent edits this directory mid-task.

1. Add a row to the relevant constraint file
2. Assign the next available ID in that file's sequence
3. Set severity (`HARD` / `SOFT`), scope, and verification method
4. **Cite the `IMP-` finding ids that justify it**, in the Rationale column. A constraint with
   no finding behind it is an opinion, and this file is not for opinions.
5. **`Verify By` must name a mechanically executable check** — a command, a script, a query.
   A constraint that can only be verified by someone remembering to look is a comment. The
   project's own evidence: `C-TECH-049` became effective when
   `scripts/verify-workflow-description-length.py` was written, not when the row was added.
6. If the constraint affects which agents must check it, update the table above
7. Commit with a message: `constraints: add C-DOM-<nnn> — <short description> (IMP-nnnn)`

### The 3-per-review cap

No more than **three** new constraints per improvement review. If clustering suggests more,
the correct output is a consolidation proposal — see `skills/how-to-promote-a-finding.md` §2.
A rule set that only grows is one nobody can hold in mind.

### Retirement is not optional

Every improvement review must consider retirement and either name a candidate or state that it
checked and found none. Constraints superseded by a general gate are retired, not left as
duplicate coverage:

1. Mark `status: retired` with a `retired_reason` — never renumber or reuse the ID
2. Name the general gate that replaces it
3. **Prove coverage is not lost**: the retired constraint's own known-bad fixtures must still
   fail under the replacement
