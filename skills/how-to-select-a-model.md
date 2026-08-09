# Skill: How to Select a Model

Used by: any agent or orchestrator that needs to override the default assignment in `config/models.yml`

---

## The Core Question

> **What is the cost of a wrong answer here, and can it be cheaply corrected?**

That single question drives almost every model selection decision.

| Wrong answer cost | Correctability | Use |
|---|---|---|
| Cheap — one message to fix | Easy | Mechanical (Haiku) |
| Moderate — revision cycle | Manageable | Standard (Sonnet) |
| Expensive — downstream rework, data migration, security exposure | Hard | Strategic (Opus) |

---

## Decision Tree

```
Is the task purely mechanical?
  (routing, command execution, status reporting, log writing)
    YES → Haiku

Does the task require novel reasoning?
  (design decisions, trade-off analysis, security architecture)
    YES → Opus

Does the task involve structured production within known patterns?
  (document writing from templates, code gen within a defined TAD, test derivation)
    YES → Sonnet
    NO  → Opus (when in doubt, escalate)
```

---

## Signals That Justify Escalation to Opus

Escalate from Sonnet → Opus when **any** of the following are true:

**Scope signals**
- Estimated effort is L or XL
- The feature has no existing pattern in the codebase to follow
- More than 3 open questions remain unresolved at task start

**Risk signals**
- Task involves cryptography, auth flows, or custom security controls
- Task touches regulated data (PII, financial, medical, legal)
- A wrong decision requires a database migration to undo
- A wrong decision breaks a public API contract

**Quality signals**
- Previous Sonnet output failed the gate on this feature
- The TAD contains open ADRs (Architecture Decision Records) still marked "Proposed"
- The domain compliance checklist has mandatory controls that are novel to the codebase

---

## Signals That Justify Staying on Haiku

Stay on Haiku (don't over-spend) when **all** of the following are true:

- The task has a small, finite set of valid outputs (routing, yes/no, status)
- The inputs are fully structured (reading a YAML file, following a numbered list)
- A wrong output is immediately visible and trivially corrected
- No domain knowledge or creative synthesis is required

---

## Applying a Model Override

Model IDs live **only** in `config/models.yml` (`tiers.<tier>.model`). Resolve the
tier there — never type a model ID from memory.

### Claude Code
```bash
# Override for a single agent invocation (ID resolved from config/models.yml)
ANTHROPIC_MODEL=$(yq '.tiers.strategic.model' config/models.yml) claude

# Or via flag
claude --model "$(yq '.tiers.strategic.model' config/models.yml)"
```

### API / custom orchestrator
```python
# Resolve tier from config/models.yml
tier = models["agents"]["architect-agent"]["tier"]
model = models["tiers"][tier]["model"]

# Apply escalation rule if condition is met
if feature.effort_size in ["L", "XL"]:
    model = models["tiers"]["strategic"]["model"]

response = client.messages.create(model=model, ...)
```

### In agent files
Each agent file declares its assigned tier and model at the top. The orchestrator reads
`config/models.yml` to resolve the actual model ID. Agents do not hardcode model strings —
they reference their tier only.

---

## Anti-Patterns

| Anti-pattern | Problem |
|---|---|
| Always use Opus "to be safe" | 10–20× cost inflation with no quality gain on mechanical tasks |
| Always use Haiku "to save money" | TAD and security decisions degrade; downstream rework costs more than the saving |
| Hard-code model IDs in agent files | Can't update all agents when a new model releases — use `config/models.yml` |
| Never escalate | Forces Sonnet into tasks it handles poorly; creates silent quality degradation |
| Escalate on every feature | Defeats the cost model; reserve Opus for decisions with lasting consequences |

---

## Reviewing Model Assignments

Review `config/models.yml` when:
- A new Claude model is released (check if tier assignments still hold)
- A model that was strategic becomes standard-tier capable
- Cost targets for the project change
- An agent is consistently failing its gate (may signal under-powered model)

Update the model IDs in `config/models.yml` — all agents pick up the change automatically.
