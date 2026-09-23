# Improvement Review — 2026-09-23 (2)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 1 `NEW` → 1 cluster
**Trigger:** blocker escalation — one unread `blocker` entry, routed immediately per
`agents/WORKFLOW.md` → *Processing triggers*
**Gate:** `APPROVE IMPROVEMENTS`

**Scope, stated up front.** This review processes **IMP-0835 only**. It is the single entry in
state `unread` with severity `blocker`. The queue also holds 19 other `unread` entries and four
`awaiting-approval` blockers; §5 names them and why they are not in scope. This is
`agents/improvement-agent.md` activation step 2 and the `IMP-0183` rule it carries: one unread
blocker summons a review of **itself**, not of the queue around it.

---

## 1. Regression check — did the last review's changes work?

The last reviews to apply anything were 2026-09-22 improvement review and review 2.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| `agents/pipeline-agent.md`, new subsection *"Before you dispatch ANOTHER agent to fix what a finding describes"* | 2026-09-22 | `build-blocked-by-the-finding-it-remediates` | NO | Working — leave alone |
| `agents/improvement-agent.md` activation step 6, the `observable_at` CLOSE/DEFER table | 2026-09-22 | `draft-states-a-disposition-the-closure-rules-forbid` | NO | Working — leave alone |

Measured by classifying every entry carrying either `class_instance_of`: three members total
(`IMP-0814`, `IMP-0815`, `IMP-0817`), all `APPLIED`, all timestamped **before** the changes landed.
No member of either class has been appended since.

**Changes whose class recurred after a *prose* fix:** none.
**Changes whose class recurred after a *gate*:** none.

One note on the second row, because this review is the first to exercise it: step 6's CLOSE/DEFER
table was applied here. `IMP-0835` carries `observable_at: "n/a"`, which is the table's first row —
**CLOSE**, `evidence_grep` is sufficient, and no `reobserved` record is required or should be
written. That is the table doing its job at draft time rather than at apply time, which is the
correction `IMP-0815` asked for.

---

## 2. Clusters and promotion decisions

```
CLUSTER: dispatched-below-required-tier  (x1 in scope: IMP-0835; x3 in the class overall)
Altitude:   CLASS — but NOT the class the tag implies. See the split below.
Ladder row: "The system's own memory failed" → a read-path change, at the point of use.
            NOT "an agent had the information and still did the wrong thing" — the agent did
            the right thing, and had no instruction telling it to.
Becomes:    skills/how-to-verify-a-platform-contract.md §3, one new subsection placed
            immediately after the ground-truth procedure: re-evaluate your own
            escalate_to_strategic_when list against what ground-truthing just measured,
            BEFORE authoring the design it implies; stop and request re-dispatch if a
            trigger now fires that did not fire at dispatch.
Retires:    nothing — no instance gate or constraint exists for this class.
Cites:      IMP-0835 (and IMP-0398, IMP-0290 as the class history that sets the altitude)
Residual:   Stated in full below. Three parts, and the third is the one that matters.
```

### The class tag hides a split, and the split decides the altitude

Three entries carry `class_instance_of: dispatched-below-required-tier`. They are **not three
instances of one mechanism**, and treating them as such would produce the wrong change.

| Entry | Status | Mechanism | Was the trigger knowable at dispatch? |
|---|---|---|---|
| `IMP-0290` | `REJECTED` | Claimed a dispatch was not escalated. `logs/routing.log` recorded that it **was**. Premise disproved. | n/a — no defect occurred |
| `IMP-0398` | `NEW`, reviewer-deferred | Dispatcher lapse. The feature's data profile met the trigger, and four sibling dispatches on the same document had been escalated for the same reason. | **YES** — from the brief alone |
| `IMP-0835` | `NEW`, in scope here | The trigger became true **during** the work, when ground-truthing showed the fix was a different size than the brief described. | **NO** — the information did not exist |

So the defended surface is not "dispatchers forget to escalate". That is `IMP-0398`'s mechanism,
it has one verified instance, and its own deferral already records why a further
`agents/lead-agent.md` edit is being held.

`IMP-0835`'s mechanism is different and previously undefended: **the tier decision is evaluated
once, from the brief, and the single step most likely to invalidate it happens afterwards.** The
escalation check in `agents/architect-agent.md` runs *"before producing any output"*, while the
TAD's contract-verification section is ground-truthed inside step 4, after it. Nothing re-opens the
question.

### Why the change lands in the skill and not in the agent file

`IMP-0835`'s own `proposed_change` names `agents/architect-agent.md` — a new step for one agent.
Three measurements moved it:

1. **The altitude rule forbids an instance patch here.** This is the third entry in the class.
   `skills/how-to-promote-a-finding.md` §2: on the second instance you generalise.

2. **Four agents ground-truth, not one.** `skills/how-to-verify-a-platform-contract.md` is loaded
   by `architect-agent`, `development-agent`, `test-agent` and `build-agent` — measured by grep —
   and all four carry an `escalate_to_strategic_when` list in `config/models.yml`. An
   architect-only step would not have covered `development-agent`, which ground-truthed **this same
   ONS endpoint one dispatch earlier** (`IMP-0831`). The next instance of this class is as likely to
   arrive through that door.

3. **The skill is loaded at the exact moment the trigger fires.** A rule about what to do when
   ground truth surprises you belongs next to the procedure that produces the surprise, not in an
   activation preamble read an hour earlier. `agents/architect-agent.md`'s step table already loads
   this skill at the TAD's environment-prerequisites and contract-verification sections, so the read
   path exists and needs no second edit to open it.

### The obvious home is disqualified by measurement

`skills/how-to-select-a-model.md` — 148 lines, titled *"model escalation decision framework"* — is
where a reader would expect this rule to go. It is the wrong home, and not as a matter of taste:

```
grep -rn "how-to-select-a-model" agents/ skills/ CLAUDE.md config/ scripts/
→ CLAUDE.md:203    (the repository-layout diagram)
```

**One hit, and it is a picture of the directory tree.** No agent loads this file at any point in
any activation sequence. A rule written into it would be a rule that depends on remembering, which
is `IMP-0554` and `IMP-0070`'s measured shape. Sweeping every skill the same way found a second
orphan — `skills/how-to-write-a-deployment-runbook.md`, referenced by nothing at all. That
measurement is logged as **IMP-0837** with a proposed gate; it is **not** actioned here, because
wiring or retiring two skills is a separate change from the one this blocker asks for, and §5
records it as deferred rather than folding it in silently.

### Residual — what this change does not cover

1. **It is prose, and prose is the weakest rung of the ladder.** No gate can read a dispatch's
   effort estimate or compare it to a tier. The ladder's mechanical rungs are genuinely unavailable
   here: `IMP-0290`'s rejection already established that nothing in `scripts/` sits between an agent
   and the Task tool, so a pre-dispatch refusal is not buildable, and a mid-task re-check is a
   judgement an agent makes about its own work. This is one of the cases where prose is the correct
   altitude rather than a concession.

2. **It defends only the ground-truthing door.** A standard-tier dispatch can discover it is
   under-tiered by other routes — reading a knowledge file, tracing a dependency, finding a
   contradiction in an approved document. Those are undefended. One instance, one door: the
   generalisation goes as far as the evidence does and no further.

3. **The control that has actually worked twice is the agent's own self-check, and it is not
   this change.** Both `IMP-0398` and `IMP-0835` were caught by the dispatched agent noticing and
   stopping — `IMP-0398` by review 27's self-check clause in `scripts/generate-subagents.py`, and
   `IMP-0835` by an agent that stopped correctly **with no instruction telling it to**. This change
   converts that good judgement into an instruction so it does not depend on the agent being the
   sort that stops. It raises the floor; it does not add a new detector, and it should not be
   reported as one.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | skill | `skills/how-to-verify-a-platform-contract.md` | New subsection in §3: re-check your own tier after ground-truthing, before authoring; stop and request re-dispatch if a trigger now fires | IMP-0835 | NO — instruction change; see §2 Residual 1 for why no gate is buildable | N/A |

**Constraint budget:** 0 of 3 used.

### The exact text proposed

To be inserted after the *"Two failed guesses is the signal to stop guessing"* paragraph that
closes the ground-truth procedure, and before the *"Reconciling a hand-edited live artefact"*
subsection.

---

### When ground truth changes the SHAPE of the fix, re-check your own tier BEFORE authoring

Your tier-escalation check — `config/models.yml` → your agent's `escalate_to_strategic_when` — ran
**once**, at activation, against **what the dispatch brief described**. The procedure above is the
step most likely to invalidate it. A brief says *"the field names are wrong, correct them"*;
ground-truthing says the field does not exist, cannot exist, and the mechanism that would replace
it is absent from this stack. Those are different sizes of work, and the second may meet a trigger
the first did not.

So, before you write any of the design the ground truth implies:

1. **Re-read your own `escalate_to_strategic_when` list**, and evaluate it against what you just
   measured — not against what the brief said.
2. **Where a trigger now fires that did not fire at dispatch, STOP.** Emit `BLOCKED`, state the
   ground truth you established and which trigger it turned on, and ask for a re-dispatch carrying
   the explicit `model:` override. Do not author the design at the original tier.
3. **Record the ground truth in the register (§4) before you stop.** The next dispatch inherits it.
   A re-dispatch that has to re-measure the endpoint pays for this twice, and the stop is only cheap
   if the measurement survives it.

The two triggers ground-truthing most often turns on are **"estimated effort is L or XL"** and
**"new integration topology or external system not in `knowledge/technology/`"**, because both are
properties of the *solution*, and the solution is not known until the contract is. **A dispatcher
cannot evaluate either one.** `IMP-0835`'s brief — *revise the TAD's field names against the live
ONS endpoint* — could not have known that the replacement needs server-side aggregation the live
layer rejects on every expression form tried, in-flow aggregation this stack does not have anywhere
(`knowledge/technology/power-automate.md` → *`List rows` does NOT support aggregate FetchXML*, and
*no `sum()` over an array in the expression language either*), and a second external ONS service
nobody had listed. That is not a dispatcher lapse; it is information that did not exist at dispatch
time — which is why this re-check belongs here, beside the measurement, rather than in the
dispatching agent's file.

**Stopping is the cheap outcome.** The dispatch that logged `IMP-0835` stopped itself, and cost one
dispatch's ground-truthing which the next one reuses. The alternative is a design authored below the
tier its own complexity calls for, discovered — if at all — after it has been approved and built
against.

---

## 4. Retirements

> Retirement check performed: 86 live constraint rows reviewed against this cluster, none
> currently redundant.

Derived, not typed: `grep -rh '^| C-' constraints/ --include='*.md' | wc -l` → 86 live;
`grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` → 10 retired.

No constraint governs tier selection — the rules live in `config/models.yml` and the agent files —
so this cluster has nothing to retire and adds nothing retirable. The nearest candidate the sweep
surfaced is not a constraint at all: **`skills/how-to-select-a-model.md` and
`skills/how-to-write-a-deployment-runbook.md`, neither loaded by any agent.** Retiring or wiring
them is proposed under **IMP-0837** and deliberately left to the review that processes it; a
blocker-triggered review is not the place to remove two files on a measurement taken in passing.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0798, IMP-0799, IMP-0800, IMP-0801, IMP-0802, IMP-0803, IMP-0811, IMP-0812,
IMP-0818, IMP-0819, IMP-0822, IMP-0823, IMP-0825, IMP-0826, IMP-0827, IMP-0828, IMP-0829, IMP-0832,
IMP-0833, IMP-0837

**States excluded from this review, and why:**

| State | Count | Why excluded |
|---|---|---|
| `unread`, non-blocker | 19 | Out of scope. A blocker trigger summons a review of the blocker, not of the queue (`IMP-0183`). These wait for a batch review. |
| `awaiting-approval`, blocker | 4 | Already processed by a review parked at its own gate. The remedy is a keyword, not a session (`IMP-0154`). Named below. |
| `awaiting-approval`, non-blocker | 2 | Same — `IMP-0830` and `IMP-0834`, both parked. |
| `reviewer-deferred` | 180 | Carry a `deferred_reason` a human accepted. Left alone. |

**The four parked blockers, and the document each waits on** — these need a keyword from you, and
none of them is re-derived here:

| Finding | Parked at |
|---|---|
| IMP-0820, IMP-0821 | `docs/improvements/2026-09-22-improvement-review-3.md` |
| IMP-0824 | `docs/improvements/2026-09-22-improvement-review-4.md` |
| IMP-0831 | `docs/improvements/2026-09-23-improvement-review.md` |

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0837 | `rule-lives-in-a-file-no-agent-loads` | Logged by this review as a measurement taken while choosing a home for change 1. Its remedy is a new gate plus wiring-or-retiring two files — a separate change from the blocker this review was summoned for. | the next batch review of the unread queue |
| IMP-0398 | `dispatched-below-required-tier` | Same class as change 1, different mechanism (dispatcher lapse, knowable at dispatch). Already reviewer-deferred with its own `revisit_when`; this review does not disturb it and change 1 does not address it. | as recorded on the entry — consolidated with IMP-0399/IMP-0400 |

One flag worth surfacing, not actioned here: `IMP-0800` is in the deferred list above, and the
validator warns that it is corrected by `IMP-0801` with no review having processed it — which will
fail the next build that reaches the `unit-tests` step. That is a batch-review item, and it cannot
be cleared by stamping a `deferred_reason` on it.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 832 | 833 |
| Distinct classes | 194 | 195 |
| Recurring classes (x≥2) | 63 | 63 |
| Digest lines | 751 | regenerate to confirm |

Regenerated with `python3 scripts/generate-known-failure-modes.py`; confirmed current with
`--check`. The digest is the read path — a finding that never reaches it teaches nobody.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-23-improvement-review-2.md

Findings processed: 1 NEW  →  1 cluster
Regression check:   2 prior changes audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 0 gates/scripts, 1 skill/knowledge edits,
                    0 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 0 left as notes
Digest:             will regenerate — 833 lessons, 63 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

**Applied 2026-09-23** on `APPROVE IMPROVEMENTS`, as part of a batch applying six parked reviews.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | `skills/how-to-verify-a-platform-contract.md` §3 — new subsection *"When ground truth changes the SHAPE of the fix, re-check your own tier BEFORE authoring"*, inserted verbatim from §3's proposed text, after the *"Two failed guesses"* paragraph and before *"Reconciling a hand-edited live artefact"* | 2026-09-23 | IMP-0835 |

Entries rejected, with reasons:

| Finding | Rejected because |
|---|---|
| — | — |

**IMP-0835 was disposed of by TWO reviews, and is closed once.** This document and
[2026-09-23 improvement review 1](2026-09-23-improvement-review.md) were both drafted against the
same blocker by separate sessions, neither aware the other was live. Review 1 folded it in as its
change 5 (the escalation preamble in `scripts/generate-subagents.py`); this review was summoned by
it and lands the skill subsection. **Neither change was withheld** — they are complementary rather
than competing, and the reconciliation is recorded on the entry itself: `reviewed_in` lists both
documents and `applied_by` names both changes.

That the two independently chose different homes is worth keeping. Review 1 put the rule where
every dispatched agent reads it at activation; this review put it where the four ground-truthing
agents read it at the moment the trigger fires. §2's three measurements argued for the second, and
the first does not contradict them — the preamble is read once and early, the skill is read late and
in context. Applying both is strictly better than either.

**The re-homing noted in §8 stands and was applied as written.** `IMP-0835`'s own `proposed_change`
named `agents/architect-agent.md`; change 1 landed in the skill instead, for the three measured
reasons in §2. Recorded here, in the entry's `applied_by`, and in the gate output — not a silent
substitution. The rule's substance is unchanged.

**Note for the apply step.** `IMP-0835`'s own `proposed_change` names
`agents/architect-agent.md`; change 1 lands in `skills/how-to-verify-a-platform-contract.md`
instead, for the three measured reasons in §2. This is a deliberate re-homing of an approved
intent, recorded here, in the entry's `applied_by`, and in the gate output — not a silent
substitution. The rule's substance is unchanged: re-check the tier after ground-truthing and stop
if a trigger fires.
