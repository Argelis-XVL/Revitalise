# Improvement Review — 2026-09-22 (2)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 3 `NEW` → 3 clusters
**Trigger:** blocker escalation — one unread `blocker`-severity entry (IMP-0816)
**Gate:** `APPROVE IMPROVEMENTS`

**Scope.** This review processes the unread blocker (IMP-0816), one deferred entry whose return
condition fired on this review's own activation (IMP-0815), and one finding this review logged
itself (IMP-0817). The eight other unread entries (IMP-0798 … IMP-0803, IMP-0811, IMP-0812) were
already declared out of scope by
[review 1 of today](2026-09-22-improvement-review.md#L155) and carry its `excluded_by` stamp; they
stay out of scope here for the same reason — one unread blocker must not pull a review of
everything around it (`IMP-0183`). §5 names each of them.

---

## 0. What the reviewer needs to know first

**Stamping the blocker as "reviewed" does not unblock the build, and it has already been stamped.**
The blocker rung of the queue gate fires on `awaiting-approval` exactly as it fires on `unread`
([verify-improvement-log.py#L1373](../../scripts/verify-improvement-log.py#L1373)), and
`improvement-log-check` is a HARD step with no `--warn-only` at
[config/revitalise-grant-automation-build.yml#L80](../../config/revitalise-grant-automation-build.yml#L80).
Executed after stamping: exit **1**, with the message changed from *"run a review"* to *"read the
document and respond `APPROVE IMPROVEMENTS`"*. The gate goes green when IMP-0816 moves to a
reviewer-authored deferral — simulated in §6, not inferred.

**The fix for the defect is already in source.** `Set_trailing_filled_count` no longer references
the variable it sets; a `Compose` computes the increment first and the assignment reads that
Compose's output
([REVPortalRoundStatistics…json#L3028](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L3028)).
What is missing is not the fix; it is a gate that would have caught the shape before a human opened
the designer.

---

## 1. Regression check — did the last review's changes work?

Audited: [`docs/improvements/2026-09-22-improvement-review.md`](2026-09-22-improvement-review.md)
(applied roughly four hours before this one).

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| `knowledge/technology/build-and-deploy.md` — the `git log -S` diagnostic for a designer error naming an action absent from source | 2026-09-22 | `live-definition-drifts-from-source` | NO — 0 new instances | Working — leave alone |
| [`agents/pipeline-agent.md#L112`](../../agents/pipeline-agent.md#L112) — run the queue gate and read its exit code before dispatching another agent to fix what a finding describes | 2026-09-22 | `build-blocked-by-the-finding-it-remediates` | **YES — once, four hours later.** And see below: the cost fell to zero | Working — and the recurrence is the evidence, not the counter-evidence |
| `logs/improvement-log.jsonl` — `class_instance_of` corrected on IMP-0813 and IMP-0814 | 2026-09-22 | bookkeeping | N/A | Held — IMP-0817 clusters correctly because of it |

**Changes whose class recurred after a prose fix:** one — and the regression table's own question is
the wrong one to ask of it.

**The second row is this review's main finding, and it is measured, not argued.** Two occurrences of
the same class, four hours apart, on the same day:

| | Occurrence 2 — 09:21 | Occurrence 3 — 13:41 |
|---|---|---|
| Blocker | IMP-0813 | IMP-0816 |
| Where it halted | **at step 5 of the build** | **before any step ran** |
| What that cost | one build dispatch, packaging never reached | one preflight command |
| Evidence | [logs/build.log#L123](../../logs/build.log#L123) | [logs/build.log#L125](../../logs/build.log#L125) |

The instruction applied this morning is what moved the halt from inside the build to in front of it.
The class recurred; the defect it causes did not. **When a class is one the system cannot eliminate,
the regression question has to be asked of the cost, not only of the recurrence count** — that is
IMP-0817's lesson and it is why this review proposes no further rule for it.

---

## 2. Clusters and promotion decisions

```
CLUSTER: platform-contract-guessed-not-groundtruthed  (x1 new: IMP-0816; x16 historically)
Altitude:   CLASS — but by the named exception, not by instance count. skills/how-to-promote-a-
            finding.md#L224 permits skipping ahead on ONE instance where the severity is
            `blocker` and the mechanism is a platform law. Both hold: Power Automate refuses the
            designer save, and no authoring choice makes a self-referencing SetVariable legal.
Ladder row: "a tool could catch it mechanically" → a script plus a build gate.
Becomes:    check 9 of .engine/scripts/verify-flow-definition-language.py — the gate that already
            exists for this class. Not a new script: a new check inside the general gate, which
            is what the altitude rule asks for.
Retires:    nothing
Cites:      IMP-0816
Residual:   The check reads the LITERAL variable name in inputs.name against variables('…') calls
            in inputs.value. A name assembled at runtime — concat() into a variable name — is
            outside it. No such shape exists in this solution's 22 SetVariable actions, and the
            platform does not accept a dynamic variable name in inputs.name in any case.
```

```
CLUSTER: draft-states-a-disposition-the-closure-rules-forbid  (x1: IMP-0815)
Altitude:   INSTANCE, and the entry's own return condition is what convened it: "the next
            improvement review reaches activation step 6" — this review, at step 6.
Ladder row: "an agent had the information and still did the wrong thing" → an agent-file edit.
Becomes:    one clause in agents/improvement-agent.md activation step 6, beside the premise-
            grepping clause: read observable_at on every entry the review will dispose of, and
            draft the disposition as CLOSE or DEFER accordingly.
Retires:    nothing — the step 8 clause at agents/improvement-agent.md#L303 stays exactly as it
            is. This adds a read upstream of the approval; it removes no check.
Cites:      IMP-0815
Residual:   Nothing mechanically compares a draft's stated disposition against the entry's
            fields. This stays prose, and this review is its first test: IMP-0816 is drafted as
            a DEFERRAL from the start, because its observable_at is V4 (see §3 note).
```

```
CLUSTER: build-blocked-by-the-finding-it-remediates  (x2: IMP-0814, IMP-0817)
Altitude:   NO PROMOTION. The remedy a third instance would normally justify already exists, in
            two places, and one of them was measured working on this very instance.
Ladder row: none taken. Recorded as a capability lesson in the digest.
Becomes:    nothing beyond IMP-0817's own record.
Retires:    nothing
Cites:      IMP-0814, IMP-0817
Residual:   The cost that remains — one improvement-review dispatch and one reviewer keyword
            between a fix and its build — is not removable by any agent-side change. It is what
            C-TECH-061 charges. Whether that price should stay is a reviewer decision, put in §5.
```

**Why no lead-agent preflight, stated plainly, because the brief asked for it.**
[`agents/lead-agent.md#L320`](../../agents/lead-agent.md#L320) already says *"Run it BEFORE
dispatching `build-agent` or `pipeline-agent`, not after"*;
[`#L325`](../../agents/lead-agent.md#L325) already says *"READ ITS EXIT CODE, NOT ITS NARRATIVE.
Anything other than 0 blocks the dispatch"*; and
[`#L306`](../../agents/lead-agent.md#L306) already routes any blocker to this agent immediately.
Adding "grep the target finding's id against the queue" would be a fourth statement of a rule the
file states three times. Review 1 today measured this and declined it for the same reason
([§2](2026-09-22-improvement-review.md#L96)); this review re-measured it independently and agrees.

**And the obvious alternative is refused, explicitly.** The cheapest way to stop a self-remediating
blocker from halting its own build is to stop logging it at `blocker` severity once the fix is in
source. That is a proposal whose entire benefit is that a control observes less than before, and
`skills/how-to-promote-a-finding.md` §4 forbids it. Severity records what the defect did, not how
convenient the queue is afterwards. It is named here so it is not rediscovered as a good idea.

**One thing was considered and rejected on its own merits.** Recording this class in
[`logs/class-defences.json`](../../logs/class-defences.json) looks right and is not: that file's
own rule is that a row names *the sub-property a GATE actually defends*
([#L16](../../logs/class-defences.json#L16)). This class is defended by an instruction to a
dispatching agent, not by a gate, and a row claiming otherwise would tell the digest a gate exists
where none does.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | `.engine/scripts/verify-flow-definition-language.py` | Check 9: for every `SetVariable` action, flag any `variables('X')` reference in `inputs.value` where `inputs.name` is also `X` — the shape the Power Automate designer refuses to save with *"Self reference is not supported"* | IMP-0816 | YES — `python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation` | **already wired** — `HARD` at [config/revitalise-grant-automation-build.yml#L615](../../config/revitalise-grant-automation-build.yml#L615) |
| 2 | agent | `agents/improvement-agent.md` | Activation step 6 gains one clause beside the premise-grepping rule: read `observable_at` on every entry the review will dispose of, and write each disposition in the draft as CLOSE or DEFER accordingly | IMP-0815 | N/A — instruction change | N/A |

**Constraint budget:** 0 of 3 used.

**Row 1 corrects its own finding's premise, and the correction matters.** IMP-0816 proposes *"add a
fourth check"*. The script has **eight**; check 8 was added by
[review 3 on 2026-09-20](2026-09-20-improvement-review-3.md) for the duplicate-action-name defect on
this same flow. It is check **9**. The finding also names `scripts/verify-flow-definition-language.py`
as the target — that file is a 115-line instance wrapper, and every check's mechanism lives in
`.engine/scripts/verify-flow-definition-language.py`. A self-reference is a pure platform fact with
no client literal in it, so it belongs in the engine copy and the wrapper needs no change.

**Corpus measurement, executed at draft time against a prototype of the check** (the rule that a
`--selftest` is not evidence a gate is correct):

| Corpus | Findings | True positives | False positives |
|---|---|---|---|
| Current tree — 8 flow definitions, 22 `SetVariable` actions | **0** | — | 0 |
| The same flow at `HEAD`, before the fix | **1** | 1 | 0 |

**Zero on the current tree is the correct answer and is reported as such rather than as a clean
run:** the fix shipped before this review convened, so the only instance the corpus ever held is the
one the second row reproduces. The prototype names the full container path to the offending action,
nine levels deep, which is the output a delivery agent needs.

---

## 4. Retirements

> Retirement check performed: 86 live constraint rows reviewed (10 already retired, derived with
> `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l`), none currently redundant. This
> review adds no constraint, and the one check it adds extends an existing gate rather than
> standing beside it — so it supersedes no instance gate. The nearest candidate,
> [`C-TECH-061`](../../constraints/technology/technology-constraints.md#L131), is the rule that
> halted the build correctly twice today and is doing exactly what it was written for.

---

## 5. Findings left unprocessed

**Out of scope, already stamped by review 1 of today:** IMP-0798, IMP-0799, IMP-0800, IMP-0801,
IMP-0802, IMP-0803, IMP-0811, IMP-0812. Each carries
`excluded_by: docs/improvements/2026-09-22-improvement-review.md`, and the reasons are tabulated at
[review 1 §5](2026-09-22-improvement-review.md#L155). None is a blocker; none is re-derived here.

**IMP-0800 still carries a standing gate WARNING** — it is corrected by IMP-0801 and no review has
processed it. It is a WARNING, not a counted problem, so it does not block a build today. Named
again rather than left silent; it is the strongest candidate for the next scheduled review.

**One open decision for the reviewer, and it is a policy question, not a defect:**

**Should a blocker whose fix is already committed to source still hold its own build until you
answer?**

**Problem** — Three times now, an agent has fixed a defect, logged the blocker the capture contract
requires, and thereby blocked the build that ships the fix. Each time the remedy was one
improvement-review dispatch and one keyword from you.
**Suggested fix** — Leave `C-TECH-061` exactly as it is. The price is roughly an hour of your
attention per occurrence, and the alternative — any rule that lets an agent's own judgement release
a blocker — removes the only human checkpoint on the class.
**What happens if you don't decide** — Nothing breaks; the fourth occurrence simply gets
re-litigated from scratch, as this one nearly was. Recording your answer is what stops that.
[constraints/technology/technology-constraints.md#L131](../../constraints/technology/technology-constraints.md#L131)

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 812 | 813 (IMP-0817, logged by this review) |
| Digest lines | 736 | **737** — regenerated at draft time, because the capture contract requires the digest to be current once a finding is appended, and IMP-0817 was appended by this review. The registered `CURRENT SIZE` claim that this regeneration mechanically drifts was corrected in the same change, in both the instance and `.engine` copies |
| Recurring classes (x≥2) | `build-blocked-by-the-finding-it-remediates` 1 | same class 2 — the count becomes true |

**Disposition simulated, not inferred.** Two runs were executed against a scratch copy of the log,
and the real file restored and confirmed byte-identical with `diff`.

- **With `reviewed_in` stamped only** (this draft's state, already on disk): exit **1**, blocker
  trigger naming IMP-0816 in state `awaiting-approval`.
- **With IMP-0816 deferred** (post-approval state): the blocker trigger **clears**.

**And one thing the simulation disproved, which is why it was run.** The tempting shortcut was to
give IMP-0816 an `evidence_grep` needle pointing at the fix already in source, so the queue would
report it as `already-fixed`. Executed: that makes the gate **worse**, not better —
`already-fixed` outranks every other state, and the gate then fails with *"status NEW, but … ALREADY
contains …"*. A deferral is the only disposition that clears the rung.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-22-improvement-review-2.md

Findings processed: 3 NEW  →  3 clusters
Regression check:   3 prior changes audited, 1 class recurred (at reduced cost — see §1)
Proposed:           0 constraints (cap 3), 1 gates/scripts, 0 skill/knowledge edits,
                    1 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 1 left as notes
Digest:             regenerated at draft time — 737 lines, 1 recurring class corrected

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

*Nothing is applied yet. This section is written when the keyword arrives.*

**Intended dispositions, stated now because `observable_at` was read at draft time (change 2's own
rule, applied to this review):**

| Finding | `observable_at` | Intended disposition | Why |
|---|---|---|---|
| IMP-0815 | V1 | **APPLIED** | Readable at source; closed by the agent-file edit itself |
| IMP-0816 | **V4** | **DEFERRED**, reviewer-authored | The defect was only ever visible when a human opened the Power Automate designer. Nobody in this session can re-observe it fixed — that needs a fresh import into DEV and a designer save. Closing it would be a claim, not a result. Owner: the reviewer, after the next DEV import. Same disposition IMP-0813 and IMP-0804 received |
| IMP-0817 | V1 | **APPLIED** | Readable in `logs/build.log`; closed by this document's own record |
