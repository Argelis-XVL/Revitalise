# Improvement Review — 2026-08-31 (review 50)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 `NEW` → 2 clusters (plus 2 appended at application, §8)
**Trigger:** unread `blocker` — [`IMP-0531`](../../logs/improvement-log.jsonl#L528), appended 2026-08-31T18:40
**WBS:** 6.9
**Gate:** `APPROVE IMPROVEMENTS` — **received 2026-08-31**
**Status:** ✅ **APPLIED. Change 1 is on disk; both entries are closed. See §8.**

---

## Summary

**The gate did its job and the finding blamed the wrong agent.**
[C-TECH-060](../../constraints/technology/technology-constraints.md#L130) caught a 380-char flow
description at step 34 of 70 — before any expensive step — which is exactly the behaviour it was
generalised for, so the field-length half of [`IMP-0531`](../../logs/improvement-log.jsonl#L528)
promotes to **nothing**, as its own `proposed_change` says. The durable gap is one level up and in a
different place: [`logs/routing.log:430`](../../logs/routing.log#L430) dispatched build-agent to
package a working tree that a live delivery dispatch was still editing, and
[`agents/lead-agent.md`](../../agents/lead-agent.md#L125) has no rule about that.

**Zero new constraints, zero scripts, one agent-file edit.**

---

## 0. Scope, and what I excluded

[`verify-improvement-log.py`](../../scripts/verify-improvement-log.py) `--check`, run before
reading any finding, reported **112 NEW: 1 unread, 0 awaiting-approval, 111 reviewer-deferred, 0
already-fixed**. The one `unread` entry is [`IMP-0531`](../../logs/improvement-log.jsonl#L528) and
it is this review's whole inbound scope. The 111 `reviewer-deferred` entries are **not re-derived**
— each carries a `deferred_reason` a human accepted, and re-opening them is the exact cost
`IMP-0183` and `IMP-0154` record.

[`IMP-0532`](../../logs/improvement-log.jsonl#L529) was appended **by this review**, correcting
`IMP-0531`'s stated root cause (§2, cluster 2). Both entries carry `reviewed_in` naming this
document, stamped at draft time per
[`agents/improvement-agent.md`](../../agents/improvement-agent.md#L125) step 6. That is the only
change this draft has made to the tree.

---

## 1. Regression check — did the last review's changes work?

Review 49 ([`2026-08-31-improvement-review-4.md`](2026-08-31-improvement-review-4.md#L332)) landed
five changes plus one config rename. Three findings have been appended since (`IMP-0529`,
`IMP-0530`, `IMP-0531`).

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [`scripts/verify-css-arithmetic.py`](../../scripts/verify-css-arithmetic.py) broadened to two checks | 2026-08-31 | `unverified-arithmetic-claim-in-css-comment` | NO | Working — leave alone |
| [C-TECH-076](../../constraints/technology/technology-constraints.md#L146) broadened to the class | 2026-08-31 | same | NO | Working — leave alone |
| [`knowledge/technology/code-apps.md`](../../knowledge/technology/code-apps.md#L667) CSS law | 2026-08-31 | same | NO | Working — leave alone |
| [`agents/lead-agent.md`](../../agents/lead-agent.md#L256) — read the gate's exit code | 2026-08-31 | `gate-reassures-wrongly` | NO | Working — leave alone |
| [`agents/lead-agent.md`](../../agents/lead-agent.md#L171) — briefing rule 4, credentials | 2026-08-31 | `credential-not-on-the-machine-that-needs-it` | NO | Working — leave alone |

**Changes whose class recurred after a *prose* fix:** none.
**Changes whose class recurred after a *gate*:** none.

**But one pattern is worth naming, because it is the third consecutive one.** `IMP-0530`
(`dispatch-brief-asserts-unverified-fact`), `IMP-0528` (credentials) and now
[`IMP-0532`](../../logs/improvement-log.jsonl#L529) are all defects in a **lead-agent dispatch
brief**, and all three fixes are prose. Normally a third prose instance is the signal to escalate to
a mechanical gate. It cannot be escalated here, and rule 4 already says why in its own last
paragraph: *"a dispatch brief is a Task-tool prompt, never written to a file, so there is no
artefact for a script to read"*
([`agents/lead-agent.md`](../../agents/lead-agent.md#L186)). The one file that does record dispatches
is [`logs/routing.log`](../../logs/routing.log), and a gate pairing its `ROUTED_TO` lines to
terminal lines is precisely the design `IMP-0319` measured — it *"reported **zero** unreconciled
dispatches while hiding the one real stall and flagging a healthy dispatch instead"*. So this stays
prose deliberately, not by omission.

**Closure evidence check.** `IMP-0531` is `observable_at: V2`. I re-ran the original reproduction
step rather than reading about it:
`python3 scripts/verify-field-length-limits.py src/solutions/RevitaliseGrantAutomation provisioning/deploymentSettings`
now exits **0** — *374 flow descriptions within 256 chars, 144 settings-row values within their
declared MaxLength, 95 declared limits read from schema*. That is the `reobserved` evidence, and it
is why this entry can be closed at application rather than deferred.

---

## 2. Clusters and promotion decisions

```
CLUSTER: platform-field-length-limit-exceeded  (x1: IMP-0531)
Altitude:   INSTANCE — and it promotes to NOTHING. The class already has its general gate.
Ladder row: row 1, "one instance, no general mechanism" — the mechanism exists and fired.
Becomes:    no change. C-TECH-060 + verify-field-length-limits.py caught a real 380-char
            description on the first build to run over the edited file, at step 34 of 70.
            MEASURED, not assumed: steps 1-33 of config/revitalise-grant-automation-build.yml
            are all cheap static checks, and every expensive step (code-app-build L1424,
            pack-managed L1510, unit-tests L1482) sits AFTER step 34 — so there is no
            reordering win to propose, and the "1 build cycle" cost is the floor for this
            defect, not evidence of a badly placed gate.
Retires:    nothing
Cites:      IMP-0531
Residual:   the gate still cannot fire before a build runs. A dispatch that edits a flow
            description and hands off without running it will still be found downstream.
            That residual is cluster 2's subject, and it is NOT specific to field lengths.
```

```
CLUSTER: finding-diagnosis-unverified  (x1 in this review: IMP-0532; x18 in the log)
Altitude:   CLASS — a packaging dispatch started over another dispatch's live source.
Ladder row: "the ORDER of steps was wrong" + "an agent had the information and still did the
            wrong thing" — at 18:03 lead-agent applied exactly this sequencing reasoning for a
            different gate ("not in parallel, to avoid re-tripping the same gate this build
            already hit once"), then at 18:19 did not apply it to a dispatch still editing the
            source about to be packaged.
Becomes:    agents/lead-agent.md — briefing rule 5 under "How Delegation Happens".
Retires:    nothing
Cites:      IMP-0532, IMP-0531
Residual:   unenforceable mechanically, for the reason rule 4 already records — a dispatch
            brief is a Task-tool prompt and no script can read it. The routing.log alternative
            is the FIFO-pairing design IMP-0319 measured as reporting zero while hiding a real
            stall. This rule is prose and will stay prose.
```

**Why `IMP-0531`'s own root cause is not the one being fixed.** It reads: the concurrent dispatch
edited the description *"without re-running field-length-limits or checking the existing
description's length headroom"*. [`logs/routing.log:437`](../../logs/routing.log#L437) shows that
dispatch (`a848f221d57e31f5b`) was still in flight when the build blocked at 18:28, and fixed the
description at 18:29 — it had not yet reached
[`agents/development-agent.md`](../../agents/development-agent.md#L35) step 8, where its constraint
check runs. **Nothing was skipped; the dispatch was simply not finished.** Had the stated root cause
been promoted, the change would have been a fourth hand-listed script in development-agent step 8 —
a rule against a step no agent got wrong.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | agent | [`agents/lead-agent.md`](../../agents/lead-agent.md#L171) | Briefing rule 5: do not start a packaging or deploy dispatch over source another dispatch is still editing; if you do it anyway, name the expected dirty state and its owner in the brief | IMP-0531, IMP-0532 | NO — instruction change; see the residual in §2 cluster 2 and rule 4's own reasoning at L186 | N/A |

**Constraint budget:** 0 of 3 used.

---

## 4. Retirements

> Retirement check performed: 82 live constraint rows reviewed (10 already retired, both figures
> derived with `grep -rh '^| C-' constraints/ --include='*.md' | wc -l` and the `~~C-` variant, not
> typed). None currently redundant — this review adds no rule that supersedes an existing one, and
> the only constraint it touches conceptually, [C-TECH-060](../../constraints/technology/technology-constraints.md#L130),
> is the one that just worked.

---

## 5. Findings left unprocessed

**Deferred:** none

Both entries in scope are processed. The 111 `reviewer-deferred` entries are outside this review's
scope by state, not by cap — see §0.

---

## 6. Digest impact

| | Before | At application (final) |
|---|---|---|
| Log entries | 528 | **531** |
| Distinct lessons | 526 | **529** |
| Recurring classes (x≥2) | **39** | **39** |
| Digest lines | 604 | 604 |

**Two figures in this table were wrong in the draft and are corrected above — see
[`IMP-0534`](../../logs/improvement-log.jsonl#L531).** The draft stated `40 → 40` recurring
classes; measured at application against both the pre-application digest (`git show HEAD:`) and the
regenerated one, `awk '/^## Recurring classes/,/^## Before you execute/' logs/known-failure-modes.md
| grep -c '^| \*\*x'` returns **39** in each case. The *delta* the draft asserted (unchanged) was
right; the absolute figure was wrong by one, in both cells.

That is the **second instance of [`IMP-0529`](../../logs/improvement-log.jsonl#L526) in the very
next review**, and it is the recurrence that settles its open design question: the fix belongs in
the Gate template and a `DIGEST-COUNT` check, not in a prose lesson, because the next review's
author reads the template and not the log entry. It was **not built here** — see §8.

`finding-diagnosis-unverified` is already recurring at 17 members, so `IMP-0532` moves no class
across the x≥2 boundary.

**Already regenerated, at draft time rather than at application.** Appending `IMP-0532` made the
digest stale, and `digest-current` is a build step
([`config/revitalise-grant-automation-build.yml`](../../config/revitalise-grant-automation-build.yml#L219))
— leaving it stale would have blocked the queued wbs:6.9 build on a *second* gate.
`generate-known-failure-modes.py --check` now reports **current (529 entries)**. Nothing else in
this document is on disk.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-31-improvement-review-5.md

Findings processed: 2 NEW  →  2 clusters
Regression check:   5 prior changes audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 0 gates/scripts, 0 skill/knowledge edits,
                    1 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 1 left as notes
Digest:             will regenerate — 527 lessons, 40 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

### The C-TECH-061 build gate does NOT clear until this keyword lands

Reported here because a build-agent re-dispatch for wbs:6.9 is waiting on it. Simulated on a scratch
copy of the log per [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L334), then
the real file restored:

| Log state | `verify-improvement-log.py --check` |
|---|---|
| `reviewed_in` stamped only (**the current state**) | **FAILED** — blocker rung fires on `awaiting-approval` too |
| `reviewed_in` + `deferred_reason` | OK |
| `status: APPLIED` + `reobserved` (what this keyword produces) | OK |

This is `IMP-0516` exactly: a fully-analysed blocker parked at a correct review is red on the same
rung as one nobody has read. The honest discharges are the keyword or an explicit reviewer-accepted
deferral — **not** a `revisit_when`. The `reobserved` evidence §1 already gathered is what makes the
first option available.

---

## 8. Applied

`APPROVE IMPROVEMENTS` received 2026-08-31. Re-verification per
[`agents/improvement-agent.md`](../../agents/improvement-agent.md#L148) step 8 was run **before**
anything was applied, and is recorded below the table.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | [`agents/lead-agent.md`](../../agents/lead-agent.md#L192) — briefing rule 5, "Do not start a packaging or deploy dispatch over source another dispatch is still editing" | 2026-08-31 | `IMP-0531`, `IMP-0532` |
| 1a | [`agents/lead-agent.md`](../../agents/lead-agent.md#L108) — the section heading's hand-typed cardinal removed, not incremented | 2026-08-31 | `IMP-0533` (appended, closed) |

Entries rejected, with reasons:

| Finding | Rejected because |
|---|---|
| — | none |

### Re-verification before applying

- **The V2 reproduction step was re-executed, not re-read.**
  `python3 scripts/verify-field-length-limits.py src/solutions/RevitaliseGrantAutomation provisioning/deploymentSettings`
  exits **0** — *374 flow descriptions within 256 chars, 144 settings-row values within their
  declared MaxLength, 95 declared limits read from schema*. That is `IMP-0531`'s `reobserved`.
- **The routed-work table was re-measured:** this review routes nothing, so nothing was withheld
  on that rung.
- **No `corrects` entry was appended against either finding** in the interval between the draft and
  the keyword. `IMP-0532` itself carries `corrects: IMP-0531`, and it is this review's own
  correction, already folded into cluster 2.
- **The cited routing evidence was re-read at
  [`logs/routing.log`](../../logs/routing.log#L430)** and still reads as §2 states — including the
  detail the rule now turns on: the 18:19 architect-agent dispatch names its concurrent dirty
  state explicitly, and the build dispatch one line above it does not.

### Change 1a — an in-scope adjunct, recorded rather than folded in silently

Adding rule 5 to a section headed *"**Three** things a dispatch gets wrong that nothing can see"*
would have left the heading wrong by two. It was **already** wrong by one — review 49 added rule 4
on 2026-08-28 and did not touch it. The durable fix is not to increment the number but to remove it,
so the next addition to a list designed to grow cannot drift it again; the lead sentence
(*"One property, three rungs"*) was changed the same way. Logged as
[`IMP-0533`](../../logs/improvement-log.jsonl#L530) and closed, rather than absorbed into change 1
without a record.

### One thing this application did NOT do, and why

[`IMP-0529`](../../logs/improvement-log.jsonl#L526)'s `revisit_when` reads *"the next improvement
review of any kind"* — which is this one — and §6 above found its second instance. **Its gate was
still not built.** Review 50's approved draft proposed **zero** scripts and zero gates, and the
keyword approved that draft; wiring a new gate under it would be applying an unapproved change,
which is the one thing
[`agents/improvement-agent.md`](../../agents/improvement-agent.md#L536) forbids most strongly for
this agent. The measurement is on the record as
[`IMP-0534`](../../logs/improvement-log.jsonl#L531) with a `deferred_reason` and a `revisit_when`
naming the next review, so it arrives there as a settled design with two instances rather than an
open question.

### Post-application state

| Check | Result |
|---|---|
| `verify-improvement-log.py --check` | **OK** — 531 entries, 0 unread, 0 awaiting-approval, 5 pre-existing warnings |
| Blocker trigger (`IMP-0531`) | **cleared** — the C-TECH-061 build gate no longer blocks the queued wbs:6.9 build |
| `generate-known-failure-modes.py --check` | **current** (531 entries, 529 lessons, 604 lines) |
| Constraints | 82 live, 10 retired — unchanged, 0 of 3 budget used |
| `ls scripts/verify-*.py \| wc -l` | 54 — unchanged, this review added no script |
