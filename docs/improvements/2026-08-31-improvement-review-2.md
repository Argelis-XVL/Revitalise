# Improvement Review — 2026-08-31 (review 47)

**Agent:** improvement-agent
**Trigger:** unread `blocker` — [`IMP-0518`](../../logs/improvement-log.jsonl), appended 2026-08-31T12:20
**WBS:** 6.9 (the halted build), plus system work that carries no task id
**Status:** **APPLIED 2026-08-31.** All three changes are on disk. `APPROVE IMPROVEMENTS` received,
with change 1's ownership deviation approved explicitly (see §5). `IMP-0517` and `IMP-0518` are
both `APPLIED`; one new finding, `IMP-0519`, was appended during application. See §8.

---

## Summary

**The one-line citation fix is right, and it is not the whole answer — but the rest is one table
row, not a project.** [`IMP-0518`](../../logs/improvement-log.jsonl) is a dangling `#L448` in the
plan document, and dropping the line number greens the gate. Measured, on a scratch copy:
`doc-line-links` goes from `FAILED — 1 dangling` to `OK`. That unblocks wbs:6.9 today.

But this is the **third** instance of the same mechanism, and the ladder
([`how-to-promote-a-finding.md` L22](../../skills/how-to-promote-a-finding.md#L22)) forbids
answering a third instance with a third instance patch. The generalisation is cheap and specific:
the system's own reporting rule **mandates** `#Lnnn` line-links, its exception table has exactly
two rows — reports and source comments — and a **long-lived design document is neither**. An
author following the rule correctly writes the rot into the plan, and a HARD gate then halts an
unrelated build on it. One new row closes that.

**I am not proposing a new constraint, a new script, or a widened gate.** The gate already exists,
already works, and fired correctly. Three findings are what I measured before declining each.

---

## 0. Scope, and what I excluded

[`scripts/verify-improvement-log.py`](../../scripts/verify-improvement-log.py) `--check` reports
**106 NEW: 2 unread, 0 awaiting-approval, 104 reviewer-deferred, 0 already-fixed**.

My scope is the **two unread** entries — [`IMP-0518`](../../logs/improvement-log.jsonl) (the
blocker that summoned this dispatch) and [`IMP-0517`](../../logs/improvement-log.jsonl). The
dispatch named only `IMP-0518`; `IMP-0517` is `unread` and therefore in scope by activation step 2
([`improvement-agent.md` L100](../../agents/improvement-agent.md#L100)), so processing it is not
scope creep — leaving it would have been a silent cap.

**Excluded: the 104 `reviewer-deferred` entries.** Each carries a `deferred_reason` a human
accepted. None is re-derived here. No entry is in `awaiting-approval`, so no parked document is
waiting on a keyword.

Four pre-existing `corrects` WARNINGs stand (`IMP-0290`, `IMP-0298`, `IMP-0320`, `IMP-0437`). None
names anything this review touches; all four are left alone.

---

## 1. Regression check — did the last review's changes work?

Audited against [`2026-08-31-improvement-review.md`](2026-08-31-improvement-review.md) (review 46),
and against **review 30**, which is the review that owns this class.

| Prior change | Class recurred? | Verdict |
|---|---|---|
| Review 46 change 4/5 — `verify-css-line-height.py` + `C-TECH-076` | No | **Worked.** The dispatch reports the css-line-height fixes (`IMP-0509`, `IMP-0514`) passed clean in this same build |
| Review 46 change 8 — `deferred_reason` on `IMP-0511` | No | **Worked.** `IMP-0511` now classifies `reviewer-deferred`; the blocker rung it was holding red is clear, re-observed in [`IMP-0516`](../../logs/improvement-log.jsonl)'s own closure |
| **Review 30 — [`verify-doc-line-links.py`](../../scripts/verify-doc-line-links.py) as a HARD build step** | **YES — `IMP-0518`** | **The gate worked. The authoring rule did not.** See below |

**The third row is the finding of this review, and the distinction matters.** A recurrence after a
*gate* normally means the gate is mis-scoped or unwired
([`improvement-agent.md` L335](../../agents/improvement-agent.md#L335)). Neither applies here: the
step is wired at
[`revitalise-grant-automation-build.yml` L1257](../../config/revitalise-grant-automation-build.yml#L1257),
it ran, and it caught the defect at V1 before the artifact was packaged. **What recurred is the
input.** The gate is a detector at the end of a pipeline whose authoring rule keeps producing the
thing being detected — so the correct escalation is not a better gate, it is the rule upstream.

---

## 2. Clusters and promotion decisions

### 2.1 Cluster A — a cross-document line number that no editor of either file is prompted to update

```
CLUSTER: hand-maintained-count-drifts-from-source  (x1 this review: IMP-0518; x3 for this
         SUB-mechanism — IMP-0389, IMP-0430, IMP-0518; x16 lifetime for the parent class)
Altitude:  CLASS — third instance, and the ladder forbids a third instance patch. But the
           class-level MECHANICAL home already exists and works (verify-doc-line-links.py,
           review 30), so the generalisation is NOT another script. It is the authoring rule
           that keeps generating the gate's input.
Ladder row: "An agent had the information and still did the wrong thing" -> a skill edit.
           The agent following skills/how-to-report-to-the-reviewer.md rule 1 CORRECTLY was
           doing the thing that rots.
Becomes:   change 1 (the instance, to unblock wbs:6.9) + change 2 (a third row in the
           reporting skill's cite-by table)
Retires:   nothing — see §4
Cites:     IMP-0389, IMP-0430, IMP-0518
Residual:  The remedy REDUCES gate coverage by one link, by design: a bare `[TAD §3.5]` with no
           `#Lnnn` is no longer checked by the gate at all, because there is no longer a
           pointer to check. That is the trade the gate's own message asks for. It is stated
           here rather than buried, and §3.2 measures it: 3 line-links read becomes 2.
```

**The tension, stated plainly.**
[`how-to-report-to-the-reviewer.md` L64-67](../../skills/how-to-report-to-the-reviewer.md#L64)
says every identifier is a clickable line-link and *"Grep the line number first."* Its exception
table at [L88-91](../../skills/how-to-report-to-the-reviewer.md#L88) has exactly two rows:

| | Cite by | Because |
|---|---|---|
| A report the reviewer reads | `path#Lnnn` | read once |
| A comment in tracked source | the name of the thing | read for the life of the file |

A **plan or architecture document is neither.** It is revised across months, cited across
documents, and sits under a HARD gate. It has the cost profile of row 2 and, being prose the
reviewer reads, gets authored under row 1. That gap is the whole mechanism, and it produced
`IMP-0389` (`#L363`), `IMP-0430` (`#L924`), and now `IMP-0518` (`#L448`) — **three different
citations, same plan document, same target document, same rot.**

### 2.2 Cluster B — a review's routed work is the one output step 8 never re-verifies

```
CLUSTER: routed-work-not-reverified-at-apply-time  (x1: IMP-0517)
Altitude:  INSTANCE, and deliberately so — first member of its class. But the ladder row that
           fits is "an agent had the information and still did the wrong thing", and the agent
           is THIS one: the defect is in agents/improvement-agent.md's own step 8.
Ladder row: "An agent had the information and still did the wrong thing" -> agent-file edit
Becomes:   change 3
Retires:   nothing
Cites:     IMP-0517
Residual:  Nothing can diff a routed sentence against a tree; this stays prose and a human
           reading the draft. IMP-0517's own why_it_was_never_caught says so, and I agree
           rather than proposing a gate that would read a markdown table for semantics —
           the exact shape measured at 48-100% false five times (improvement-agent.md L475).
```

`IMP-0517` is self-detected by this agent, at V1, and its cost was a near-miss: a delivery
dispatch would have been sent to undo `ADR-042`, an explicit reviewer decision, because review
46's routed table named a defect that had been closed in the drafting-to-keyword interval. Step 8
re-verifies *proposed changes* and *`deferred_reason` prose*; the routed table is neither, and it
is the only review output that becomes an instruction to another agent.

---

## 3. Proposed changes

> `Type` values from the closed vocabulary: `constraint` · `constraint-amendment` · `script` ·
> `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanical? |
|---|---|---|---|---|---|
| 1 | knowledge | [`docs/plans/revitalise-grant-automation-plan.md`](../../docs/plans/revitalise-grant-automation-plan.md) L902 | Drop the stale anchor: `[TAD §3.5](...architecture.md#L448)` becomes `[TAD §3.5](...architecture.md)`. **Not** re-pointed at `#L1518` — that is the patch that has now failed three times | IMP-0518 | **YES** — the gate itself |
| 2 | skill | [`skills/how-to-report-to-the-reviewer.md`](../../skills/how-to-report-to-the-reviewer.md) L88-91 | Add a **third row** to the cite-by table: *a long-lived design document (plan, TAD, SDD) cited from another document* → cite the **section identifier alone**, no `#Lnnn`, because it is revised across months and neither editor is prompted to update the other file. Names the three instances inline | IMP-0389, IMP-0430, IMP-0518 | **YES** — change 1's gate is its enforcement |
| 3 | agent | [`agents/improvement-agent.md`](../../agents/improvement-agent.md) step 8 | Extend the re-verification obligation to the **"work this review routes rather than performs"** table: every routed item is re-measured before apply, and one that has become a **closed reviewer decision or a shipped fix** is WITHHELD and reported, not dispatched | IMP-0517 | NO |

**Constraint budget: 0 of 3 used. Script count unchanged at 54** — so
[`scripts/derived-counts-registry.json`](../../scripts/derived-counts-registry.json)'s
`improvement-agent-verify-script-count` needs no edit this review.

### 3.1 Three things I measured and then declined to propose

Each of these looked like a reasonable extension. Each is recorded here with the number that
killed it, because an unmeasured proposal is the [`IMP-0442`](../../logs/improvement-log.jsonl)
defect — *proposed-mechanism-cannot-reach-the-instances-the-finding-names*.

**(a) Widening the gate to non-`.md` targets. DECLINED — 21 links, 0 reachable.** The gate's
`LINK` regex requires `.md` before `#L`, so of 24 raw `#Lnnn` links in its scope it reads 3. The
other 21 point at `.ts`, `.tsx`, `.xml` and `.yml`. I extended the regex and re-ran: **21 non-`.md`
links, of which identifier-labelled = 0.** Every one is labelled by symbol or filename
(`[BREAK_TYPE_LABELS]`, `[types.ts]`, `[L389]`), and narrowing 1 excludes all of them by design.
Widening the extension list would change nothing and would read as coverage.

**(b) A constraint row for the doc-line-links gate. DECLINED — and a correction.**
`IMP-0518`'s `expected` field cites *"per C-TECH-069/verify-doc-line-links.py"*. **That
attribution is wrong.** [`C-TECH-069`](../../constraints/technology/technology-constraints.md#L140)
is source-reader plurality — cardinality and `(table, column)` identity. Grepping `constraints/`
for `verify-doc-line-links`, `line-link`, `dangling` and `#Lnnn` returns **no row at all**: the
step is a HARD build gate with no constraint backing it. I am not adding one. A row that only
describes a working mechanical gate is documentation, and the anti-bloat rule
([`how-to-promote-a-finding.md` L118](../../skills/how-to-promote-a-finding.md#L118)) is against
exactly that. The misattribution is corrected here so the next reader does not chase C-TECH-069.

**(c) Re-pointing the citation at `#L1518` instead of dropping it. DECLINED — this is the failed
patch.** It is what the previous two instances did, and `#L1518` is stale the next time anyone
inserts a paragraph above it. The gate's own failure message asks for the opposite
([`verify-doc-line-links.py` L178](../../scripts/verify-doc-line-links.py#L178)): *"prefer citing
the SECTION IDENTIFIER without '#Lnnn'."*

### 3.2 Measurement — change 1 against the real corpus

Applied to a scratch copy of `docs/`, gate run over `docs/architecture docs/plans`:

```
BEFORE: DANGLING: docs/plans/revitalise-grant-automation-plan.md:902: [TAD §3.5] -> ...#L448
        doc-line-links: FAILED — 1 dangling of 2 identifier-labelled link(s) (3 read)
AFTER:  doc-line-links: OK — 2 line-link(s), 1 identifier-labelled, all resolving
```

**1 finding, 1 true positive, 0 false positives.** The `3 → 2` and `2 → 1` drop is the residual
named in §2.1: the fixed link is no longer checkable, because it no longer carries a pointer.

### 3.3 Simulation — does the blocker trigger actually clear?

Required by [`improvement-agent.md` L311](../../agents/improvement-agent.md#L311). Run on a scratch
copy, real log restored and confirmed byte-identical with `diff` afterwards.

**It caught two real defects in my own draft bookkeeping**, which is the point of the step:

1. First attempt wrote `evidence_grep` and `reobserved` as **strings**. The gate: *"must be an
   object `{"file": ..., "contains": ...}`, got str."* Corrected to objects.
2. `reviewed_in` naming this document **errors while the document does not exist** — so the stamp
   is only valid once the file is written, which it now is.

With both corrected, the simulated post-apply state reports **0 unread, 0 awaiting-approval**, and
the `blocker` TRIGGER line is **gone**. The build-halting rung clears on approval.

Note the interim state, honestly: between this draft and the keyword, `IMP-0518` classifies
`awaiting-approval`, and per [`IMP-0516`](../../logs/improvement-log.jsonl) the blocker rung fires
on `unread` **or** `awaiting-approval` alike. **So the gate stays red until this review is
applied** — that is expected, not a defect, and it is why this is parked rather than deferred. A
bare `revisit_when` here would keep it red permanently.

---

## 4. Retirement

**Checked; no candidate.** Required by
[`how-to-promote-a-finding.md` L121](../../skills/how-to-promote-a-finding.md#L121).

Derived, not typed: **10 retired**, **82 live** constraint rows
(`grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` and its `^| C-` counterpart).

The nearest candidate was the gate this review's cluster A is about, and it fails the test in the
opposite direction: `verify-doc-line-links.py` is not superseded, it is the thing that **worked**.
This review adds no rule that replaces an existing one — change 2 tightens a table in place rather
than adding a row elsewhere, so there is nothing rendered redundant.

---

## 5. Work this review ROUTES rather than performs — and one ownership call

**Changes 2 and 3 are mine outright** (`skills/`, `agents/`). **Change 1 is not**, and this needs
stating rather than glossing.

[`docs/plans/revitalise-grant-automation-plan.md`](../../docs/plans/revitalise-grant-automation-plan.md)
is a **plan-agent deliverable**. This agent's remit is `agents/`, `constraints/`, `skills/` and
`knowledge/`. [`IMP-0518`](../../logs/improvement-log.jsonl)'s own `proposed_change` routes the fix
to plan-agent for exactly that reason.

**I propose to perform it here anyway, and the reviewer should approve that explicitly or send it
back.** The argument for performing it:

- It deletes a stale pointer and changes **no prose, no claim, and no meaning** — `[TAD §3.5]`
  still reads `[TAD §3.5]` and still links to the same document.
- It is the remedy the gate itself prescribes
  ([L178](../../scripts/verify-doc-line-links.py#L178)), not a judgement I am making about the
  plan's content.
- Routing it leaves a HARD gate red and wbs:6.9 blocked across another dispatch boundary, for a
  one-token edit.

The argument against, which is real: it is an approved deliverable, and an agent editing another
agent's document without its gate is how change control erodes. **If the reviewer prefers,
withhold change 1 and route it to plan-agent** — changes 2 and 3 stand on their own and the
class-level fix lands either way.

**RESOLVED 2026-08-31: the reviewer approved change 1 explicitly**, naming it in the approval as
*"the plan-agent-owned one-line citation fix … it only deletes a stale pointer and changes no
prose."* Performed by this agent under that approval, not under its standing remit. The remit
itself is unchanged: `docs/plans/` remains a plan-agent deliverable, and the next such edit needs
its own explicit approval or a route to plan-agent.

Recorded in this table rather than buried in §3 because
[`IMP-0517`](../../logs/improvement-log.jsonl) — processed in this same review — is precisely about
routed work being the least-scrutinised thing a review emits.

---

## 6. Improvement log

`IMPROVEMENT LOG:` 2 findings processed (`IMP-0517`, `IMP-0518`); **1 new finding appended during
application** — [`IMP-0519`](../../logs/improvement-log.jsonl), clock skew blocking an honest
closure. See §8. (This paragraph read *"0 new findings"* at draft time; the finding arose from
applying the review, not from drafting it.)

Both are stamped `reviewed_in: docs/improvements/2026-08-31-improvement-review-2.md` **now**, at
draft time, per [`improvement-agent.md` L126](../../agents/improvement-agent.md#L126). `status`
stays `NEW`; `applied_by` does not exist until something is applied.

Both are `observable_at: V1`, so both can be honestly closed in this session on approval —
`IMP-0518` by re-running the gate, `IMP-0517` by the step-8 text being on disk.

---

## 7. Applied record — 2026-08-31

**All three changes applied as approved. Nothing withheld, nothing narrowed.** The re-verification
required by [`improvement-agent.md` L146](../../agents/improvement-agent.md#L146) was run first and
confirmed every premise still held.

| # | Target | Landed as | Verified by |
|---|---|---|---|
| 1 | [`docs/plans/revitalise-grant-automation-plan.md`](../../docs/plans/revitalise-grant-automation-plan.md) L902 | `#L448` dropped; `[TAD §3.5]` now cites the document with no line anchor | `verify-doc-line-links.py` **exit 0** — see below |
| 2 | [`skills/how-to-report-to-the-reviewer.md`](../../skills/how-to-report-to-the-reviewer.md#L91) | Third row in the cite-by table + the three measured instances and the do-not-re-point rule | Row present at L91 |
| 3 | [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L184) | *"RE-VERIFY THE ROUTED-WORK TABLE TOO"* in step 8, ahead of the WITHHELD paragraph | Clause present at L184 |

**Change 1 re-measured after applying**, exactly as §3.2 predicted:

```
BEFORE: doc-line-links: FAILED — 1 dangling of 2 identifier-labelled link(s) (3 read)
AFTER:  doc-line-links: OK — 2 line-link(s), 1 identifier-labelled, all resolving   [exit 0]
```

**1 finding, 1 true positive, 0 false positives.** The HARD build step that halted wbs:6.9 at step
55 of 70 is green, and the `blocker` trigger is gone from
[`verify-improvement-log.py`](../../scripts/verify-improvement-log.py) `--check`, which now reports
**0 unread, 0 awaiting-approval** and exits OK.

**One `corrects` WARNING appeared that §0 did not anticipate**, and step 8 required reading it
before applying: `IMP-0442` carries `corrects` against `IMP-0430`, which change 2 cites. Read in
full. It disproves `IMP-0430`'s *proposed mechanism* — extending `verify-design-doc-claims.py` to
source comments, measured at 0 of 3 instances reachable — and **not** `IMP-0430`'s status as an
instance of line-link rot, which is the only thing change 2 uses it for. `IMP-0442` is already
`APPLIED`. Change 2 stands unaltered.

## 8. What application itself surfaced — `IMP-0519`

**§6 said 0 new findings. That is now 1**, and the correction belongs here rather than in a silent
edit to §6.

Closing `IMP-0518` required a `reobserved` block, and
[`verify-improvement-log.py`](../../scripts/verify-improvement-log.py) rejects one whose `ts`
predates the finding's own. `IMP-0518` is stamped `12:20` by build-agent; `date` on this host
returned **`12:08`**. The re-observation genuinely happened after the defect was reported, and the
honest current time still failed the check — the two stamps come from clocks disagreeing by about
thirteen minutes.

Recorded as `12:21` with the skew stated inline in `reobserved.result`, rather than back-dating the
finding or routing around the check. **The ordering being asserted is true**; only the arithmetic
proving it was unavailable. Logged as [`IMP-0519`](../../logs/improvement-log.jsonl) (`friction`,
`gate-blocks-on-unrelated-precondition`), with a `revisit_when` of a second skew-blocked closure.

**No change proposed for it in this review, deliberately.** It is a single instance, the workaround
is one line, and loosening a check that currently catches copy-paste closures needs its own
corpus measurement first — proposing it here would be the unmeasured extension §3.1 exists to
refuse.

The schema also rejected two earlier drafts of these blocks (`reobserved` requires `level`, `by`,
`ts`, `rerun`, `result` — not the free-form object §3.3's simulation used). Both corrected. This is
the simulation step working one layer later than intended.

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-31-improvement-review-2.md

Findings processed: 2 NEW  →  2 clusters
Regression check:   3 prior changes audited, 1 class recurred (gate worked; authoring rule did not)
Proposed:           0 constraints (cap 3), 0 gates/scripts, 2 skill/knowledge edits,
                    1 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 1 left as notes
Digest:             will regenerate — 2 lessons, 1 recurring class

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```
