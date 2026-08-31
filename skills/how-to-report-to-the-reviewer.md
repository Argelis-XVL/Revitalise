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
Grouped by category. One block per item, in the fixed four-part template of rule 5,
separated by horizontal rules.

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

#### This rule is for REPORTS. In a SOURCE COMMENT it inverts.

Added 2026-08-28 (`IMP-0389`). The rule above was generalised in practice into source comments,
where **the cost profile is the opposite**: a report is read once, a comment is read for the life
of the file.

| | Cite by | Because |
|---|---|---|
| A report the reviewer reads | `path#Lnnn`, grepped fresh | it is read once, and the reviewer needs to click straight to the line |
| A comment in tracked source | the **name of the thing** — `app.module.css`'s `.tallTarget` | a grep finds the symbol forever; a line number is stale the next time either file is edited by anyone |
| A **long-lived design document** (plan, TAD, SDD) cited **from another document** | the **section identifier alone** — `[TAD §3.5]`, no `#Lnnn` | it is revised across months, and neither editor is prompted to update the other file |

**The third row was added 2026-08-31 (`IMP-0518`), and it is the row people get wrong**, because a
design document is prose the reviewer reads — so it gets authored under row 1 — while having row
2's cost profile. An author following rule 1 *correctly* writes the rot in, and `doc-line-links` is
a HARD build step, so the bill arrives as a halted build in another feature entirely.

Three measured instances, all in `revitalise-grant-automation-plan.md`, all pointing at the same
architecture document: `IMP-0389` (`#L363`), `IMP-0430` (`#L924`), `IMP-0518` (`#L448`, which
halted the wbs:6.9 build at step 55 of 70). Each was fixed by re-pointing the line number, and each
re-pointed number rotted again on the next revision of the target.

**Do not re-point a dangling design-doc link at its new line — drop the number.** That is the
remedy `scripts/verify-doc-line-links.py`'s own failure message asks for, and re-pointing is the
patch that has now failed three times.

**What went wrong.** Three files cited this app's layout stylesheet by line number —
`ds.module.css`, `Button.tsx` and `ds-tokens.test.ts` all saying
*"`styles.tallTarget` (app.module.css:171)"* and *"`styles.sortButton` (:355-356)"*. **Two were
already transposed when written** (171 was `.sortButton`'s `min-height`; 355-356 was
`.tallTarget`'s), and a later restyle of that stylesheet moved both declarations again, so all
three now point at unrelated lines. Nothing asserts any of it — they are comments.

**And note the structural trap, because it is not carelessness.** When a package split gives two
dispatches one file each, **a line citation across the boundary cannot be maintained by either of
them**: the pass that writes the pointer never edits the target, and the pass that edits the
target is told not to edit the pointer. Neither is ever in a position to see it break. Name the
symbol and the problem disappears.

**No gate, and the reason is worth stating.** Building one needs a registry of citations, and the
three that exist sit in frozen deliverables nobody is authorised to edit — so a gate would open
red on work no dispatch owns. This is a convention line; a second instance in an editable file
would justify extending `scripts/verify-derived-counts.py` to a second claim kind.

### 2. No HTML collapsibles

`<details>` and `<summary>` do not render as expandable here. They add visible tag noise and
hide nothing. If a block is too long to read inline, it is too long — shorten it and point a
line-link at the document that carries the detail.

### 3. Conclusion first, rationale second, and short

Lead every item with what is true. Then at most **three sentences** of why. If it needs more
than three, the rest belongs in a document — link to it.

#### And it binds TABLE CELLS, not only sections

**Inside a matrix cell, the current verdict is rewritten IN PLACE and the history moves after
it.** A reader scans the leading words of each cell and stops there; that is what a table is for.
So a cell whose first words are a verdict that has since been superseded has misinformed every
reader who scanned the column, however complete the correction further down the same cell.

This is the one place the *retain-the-superseded-wording* convention does **not** apply. That
convention is for **narrative** — an erratum quotes the sentence it withdraws so a reader can see
what changed, and gates that read prose depend on it. A traceability matrix is not narrative.

| Not this | This |
|---|---|
| **PARTIAL, and the split is exact.** … *(1,400 characters later)* … **UPDATE 2026-08-28 — DELIVERED IN FULL** | **DELIVERED IN FULL** (2026-08-28). Previously recorded PARTIAL — <what changed> |

`IMP-0482`: two Appendix A rows opened *"**PARTIAL**"* and stated a measure was *"**NOT
delivered**"*, then reversed themselves roughly 1,400 characters later in the same cell. Both
rows were correct documents and unreadable tables.

**Deliberately not a gate, and it will stay that way.** The measurable form of *"a cell's opening
verdict contradicts its closing verdict"* is phrase-based, and this repository has measured that
instrument five times at 48%–100% false (`IMP-0422`) — including a wired gate going red on the
erratum written to satisfy it (`IMP-0428`). A corrected cell contains strictly **more** of the
superseded wording than an uncorrected one, so the polarity inverts.

### 4. Plain language

Write for someone who has not read the codebase this week.

| Not this | This |
|---|---|
| "`gate-cannot-fail` recurred at x13" | "the same class of problem has now happened 13 times" |
| "the OIDC subject claim is environment-scoped" | "each environment authenticates as its own identity" |
| "IMP-0042 recorded a blocker" | "a critical finding recorded that…" |

Keep `IMP-nnnn` ids **out of the body**. They are the join key for the log, not information for
the reader. Put them in the linked record.

### 5. Decisions are spaced, not dense — and each one has a FIXED four-part shape

One bold question per block. Short paragraphs with blank lines between them. A table only when
the items are genuinely enumerable (a list of seven contract questions is a table; a judgement
call with a trade-off is prose).

**Every item in "What you need to decide" uses this template** (added 2026-08-31, `IMP-0506`):

```
**<The decision, as a bold question or imperative>**

**Problem** — <one sentence>
**Suggested fix** — <one sentence>
**What happens if you don't** — <at most two sentences>
<line-link to the source>

---
```

Four parts, the stated lengths, a line-link, and a horizontal rule between items. **The
consequence line is the one that gets dropped and it is the one that decides priority**: a
reviewer triaging eight decisions is choosing what to do first, and without "what happens if you
don't" every item reads equally urgent.

Every other section in this file had a specified shape; this one said only *"short spaced
paragraphs"*, and it was the section the reviewer actually had to act on. `IMP-0506` is the
finding that supplied this template, and it supplied it complete.

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
