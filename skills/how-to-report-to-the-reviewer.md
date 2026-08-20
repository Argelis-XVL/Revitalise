# Skill: How to Report to the Reviewer

Load this whenever you are about to write more than a few paragraphs back to the human — a gate
output, a completion report, an analysis, a summary of a multi-step change. Not for a one-line
answer.

**Used by:** every agent. The reviewer reads these to **decide**, not to audit.

---

## Why this exists

Established 2026-08-19 (`IMP-0059`), after three rejected drafts of the same report. The
content was right every time; the shape made it unusable. In the reviewer's own words:

> *"The answers are always very elaborate and with lots of references. This makes it difficult
> to understand what exactly has been going on and what I need to decide on in plain language
> without having to re-open other files it is referring to."*

> *"The whole point is to digest the result much quicker."*

What failed, in order — each is a rule below:

| Draft | What was wrong |
|---|---|
| 1 | Wall of prose. Identifiers like `C-TECH-062` written as bare code spans, so nothing was clickable and every one meant opening a file and searching |
| 2 | Used `<details>` / `<summary>` for collapsibles. **They do not render as expandable in this client** — the reviewer saw the raw tags as noise, and the sections were as long as before |
| 3 | Moved every link into a numbered references list at the bottom. The reviewer could not tell which reference belonged to which claim, and said the earlier inline style had been clearer |

The third failure is the instructive one: it was a reasonable-looking idea that made things
worse, because it separated a claim from its evidence. **Evidence goes where the claim is.**

---

## The shape

Fixed section order. Omit a section only when it is genuinely empty.

```
## Summary
2–3 sentences. What is done, then what is waiting on the reader.

## What has been built
Numbered items. Each: one bold plain-language claim + links on that same line,
then 2–3 sentences of rationale.

## Elements added        (small table)
## Elements changed      (small table)

## What is still open
One bold lead-in per item, then the reason in plain prose.

## What you need to decide
Grouped by category. One bold question per block, short spaced paragraphs.

Closing line: verification results, and what was NOT verified.
```

---

## The rules

### 1. Every identifier is a clickable line-link

A constraint id, script name, config key or agent file mentioned in prose is a link **to the
exact line it lives at**. Grep the line number first — do not guess it.

```
[C-TECH-062](constraints/technology/technology-constraints.md#L132)      ← correct
`C-TECH-062`                                                              ← the reviewer cannot click this
C-TECH-062 [5]  ... 5. technology-constraints.md                          ← the reviewer cannot tell which is which
```

```bash
grep -n "^| C-TECH-062" constraints/technology/technology-constraints.md
```

**Never collect links into a references section.** The reader is reading the claim; the
evidence belongs at the claim.

### 2. No HTML collapsibles

`<details>` and `<summary>` do not render as expandable here. They add visible tag noise and
hide nothing. If a block is too long to read inline, it is too long — shorten it and point a
line-link at the document that carries the detail.

### 3. Conclusion first, rationale second, and short

Lead every item with what is true. Then at most **three sentences** of why. If it needs more
than three, the rest belongs in a document — link to it.

### 4. Plain language

Write for someone who has not read the codebase this week.

| Not this | This |
|---|---|
| "`gate-cannot-fail` recurred at x13" | "the same class of problem has now happened 13 times" |
| "the OIDC subject claim is environment-scoped" | "each environment authenticates as its own identity" |
| "IMP-0042 recorded a blocker" | "a critical finding recorded that…" |

Keep `IMP-nnnn` ids **out of the body**. They are the join key for the log, not information for
the reader. Put them in the linked record.

### 5. Decisions are spaced, not dense

One bold question per block. Short paragraphs with blank lines between them. State the
recommendation or the trade-off, then the actual question. A table only when the items are
genuinely enumerable (a list of seven contract questions is a table; a judgement call with a
trade-off is prose).

Say plainly when one decision blocks another.

### 6. Answer what you can rather than asking

Before adding a question, check whether it is answerable from evidence. One of eight open
decisions in the 2026-08-19 review was *"are these files real applicant data?"* — a five-minute
inspection answered it (they are field definitions, not data). Do not hand the reviewer a
question you could have closed yourself.

### 7. Verification is a number, and so is its absence

Close with what was actually executed — "13 of 13 checks, 728 tests, 0 failures" — and then
state what was **not** verified and why. `C-TECH-053` applies to reports as much as to
components: never claim a level you did not reach.

---

### 8. The headline number in a gate block is the number being approved

A gate block asks for a decision about **one** quantity. Lead with that quantity, then show the
others as a ladder that reconciles to it. Never reuse the same word for two different numbers in
the same block.

What failed (`IMP-0095`): a timesheet gate opened with *"evidence span 14.20h → proposed 18.50h"*
and four lines later said *"Non-billable proposed: 5 sessions, 13.75h"*. Both said "proposed", so
both read as proposals, and the reviewer held the gate to ask which one was the bill. The number
actually being approved — 4.75 h — appeared nowhere.

```
Candidates: 6 sessions  evidence span 14.20h → proposed 18.50h    ← two "proposed" figures,
Non-billable proposed: 5 sessions, 13.75h                            neither is the decision

BILLABLE FOR APPROVAL: 4.75 h                                     ← the decision, first
  14.20h evidence span + 4.30h lead-in = 18.50h total session time
  − 13.75h system work (never billable, C-COM-002)
  = 4.75h                                                         ← and it reconciles
```

The reader must never have to subtract two numbers to find the one they are approving. If the
figures do not add up on the page, the block is wrong even when every figure in it is right.

## What this does not change

The **gate output blocks** — `CONSTRAINT CHECK`, `HANDOFF`, `IMPROVEMENT LOG:`, `BLOCKED` —
keep their exact formats from `agents/WORKFLOW.md` and `skills/how-to-apply-constraints.md`.
They are parsed by convention and by the reviewer's eye in a fixed position.

This skill governs the **prose around them**: the summary, the explanation, the open items and
the decisions. When both appear, the gate block comes last, immediately before the approval
prompt.
