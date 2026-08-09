# Skill: How to Ask Clarifying Questions

Used by: `lead-agent`, `plan-agent`

---

## Principle

Ask the minimum number of questions needed to produce useful output.
Prefer one well-chosen question over three narrow ones.
Never ask for information that can be reasonably inferred from context.

---

## When to Ask

Ask before starting if the request is ambiguous on **any of these dimensions**:

| Dimension | Example ambiguity |
|---|---|
| Scope | "Is this a new feature or a change to an existing one?" |
| Audience | "Who are the primary users — internal staff or external customers?" |
| Priority | "Is this needed for the next release or can it wait?" |
| Constraints | "Are there regulatory or compliance requirements I should know about?" |
| Integration | "Does this need to connect to any external systems?" |

---

## Question Quality Checklist

Before asking, verify:
- [ ] The answer cannot be inferred from the request or existing documentation
- [ ] The answer will materially change what I produce
- [ ] The question is phrased neutrally — not leading toward a particular answer
- [ ] I am asking at most **one question** (two if critically necessary; never more)

---

## Question Formats

**Closed (binary) — use when you need a routing decision:**
> "Is this a brand-new feature, or a modification to an existing one?"

**Open — use when you need to understand intent:**
> "What problem is this feature solving for the user?"

**Offering options — use when the user may not know the vocabulary:**
> "Should this run automatically in the background (a scheduled job), or should a user trigger it manually (a button/action)?"

---

## What NOT to Ask

- Do not ask about implementation details at the planning stage
- Do not ask questions whose answers are already in the SDD or TAD
- Do not ask for confirmation of things that are standard practice
- Do not ask "Is there anything else?" at the end of a document review
