# Agent Instruction History

**What this is.** The incident narratives that used to sit inline in `agents/improvement-agent.md`
(improvement review 7) and `agents/WORKFLOW.md` (improvement review 8). Each rule in those files is
one or two sentences; each was learned from an incident that took one or two paragraphs to describe.
The rules stayed where the agent reads them. The stories moved here.

**Why.** `agents/improvement-agent.md` is loaded in full on every improvement-agent dispatch, at the
most expensive tier in the roster; `agents/WORKFLOW.md` is loaded by the root session at every
session start. The narrative is what a person reads once to be convinced; the rule is what the agent
must execute every time. Paying for the first on every dispatch to deliver the second is the cost
this relocation removes.

**What did NOT change.** Every rule kept its imperative voice, its position in its activation step,
and its `IMP-` citation. Nothing became optional, and nothing moved out of a numbered step. A
mandatory instruction demoted to a discoverable affordance is measured at 0-of-3 compliance
(`IMP-0554`), so this relocation deliberately moves only *justification*, never *instruction*.

**How to read it.** Each section below is named for the rule it explains, and the agent file carries
a one-line pointer to it. If you are here because a rule seemed arbitrary, this is the incident that
produced it.

---

## Step 2 — why the four-state model is an instruction, not advice

Activation step 2 used to say *"read every `NEW` entry"*, and it was written when `NEW` meant unread.
Reviews 5 and 6 gave the gate a four-state model and neither updated the instruction reading the same
field, so on 2026-08-22 the gate correctly printed *"DO NOT run another review and DO NOT re-derive
the analysis"* about eleven settled entries and the activation step talked over it — a full
strategic-tier pass over settled work (`IMP-0183`, and `IMP-0154` is what it cost the first time).

---

## Step 6 — why `reviewed_in` is stamped at draft time

`IMP-0488`. Review 41 followed step 8 literally, processed a `blocker` in full, parked at its gate
and stamped nothing. The gate then reported that blocker as `unread` and fired the unread-blocker
trigger, which summoned a second strategic-tier dispatch to process a finding a parked document had
already fully analysed — the exact cost `IMP-0154` recorded and the four-state model was built to
end. The gate's own citation-stamp WARNING named the problem correctly at every run; it prints
*beneath* a FAIL whose instruction ("run an improvement review") is the wrong remedy for a stamped
entry, so it was read as noise.

---

## Step 8 — why a behavioural assertion must be EXECUTED, not read

`IMP-0426`: a delegated measurement reported that `verify-build-config.py` does not require a step to
prove it can fail, having read `is_gate()`'s name-pattern list and found the step matching none of it
— `is_gate()` has a **second** clause (anything running a `scripts/verify-*.py` is a gate whatever it
is called), so the step was recognised all along. In the same review, `IMP-0395`'s stated root cause —
*"grep confirms verify-derived-counts.py is not a build step"* — was also false; it had been one for
four days. Both would have proposed a change already on disk.

A grep or a partial read reported in the register of a measurement reads exactly like a measurement,
and nothing in a finding's own prose distinguishes *"I ran it"* from *"I read it"*.

---

## Step 8 — why a review proposing NO changes still re-verifies

`IMP-0405`: review 32 proposed no file changes at all and still had two paragraphs of perishable
measurement. Its approved `deferred_reason` for `IMP-0401` asserted, as one of three
verified-on-disk clauses, *"and rev_roundstatisticsresult does not exist in source at all"* — and
between the gate opening and the keyword arriving, a concurrently-running delivery dispatch landed
the source half of ADR-038. Applied verbatim, the approved wording would have written a false
statement into the durable record of a still-open blocker. The interval is wide open by design:
delivery dispatches run in parallel with reviews, and `logs/routing.log` L320 and L321 are the same
minute. Nothing here is scriptable — nothing can diff a sentence against a tree — so the control is
the rule plus a human reading the draft.

---

## Step 8 — why the routed-work table is re-measured before hand-off

`IMP-0517`: review 46 routed development-agent to change `--text-heading: #002060`, reasoning from
the design system's never-navy guidance. Between the draft and the keyword, the TAD recorded that
exact value as `OQ-040`, CLOSED by `ADR-042`, *"by explicit reviewer instruction given with the
design system's own never-navy guidance in view"* — the reviewer had already weighed the same
evidence and decided the other way. The dispatch would have undone an explicit reviewer decision, and
it was caught only because that pass happened to re-read the TAD for an unrelated reason.

Nothing can diff a routed sentence against a tree, so this stays prose plus a human reading the
draft. Do not propose a gate for it: a gate reading a markdown table for semantics is the shape this
project has measured at 48–100% false, five times.

---

## Step 8 — why a disproved proposal is WITHHELD

Review 24 came within one habit of the opposite. It was drafted proposing `C-TECH-072` and a gate to
enforce it, derived from `IMP-0272`'s stated root cause. `IMP-0273` was appended after the draft and
before the keyword, correcting that root cause from Microsoft's own worked example, and the corrected
code was already on disk. Applied as approved, a HARD build gate would have been red against correct
code, and the only way to green it would have been to restore the exact call shape that had already
failed live on all five columns. Nothing required the re-read that caught it (`IMP-0275`).

Note also that the disproving entry sat at `reviewer-deferred` — the state step 2's table tells you to
leave alone.

---

## Step 8 — where NARROW-AND-REPORT came from

`IMP-0335`. Applying review 29 produced three changes in the sound-intent/wrong-wording category, and
the step modelled neither APPLY nor WITHHOLD for them, so all three were handled correctly by
improvisation with nothing authorising it.

The fourth instance is worked: an approved row said "the count of **distinct** `CLUSTER` blocks", the
first implementation counted raw `^CLUSTER` lines, and that measured **5 findings / 3 true / 2 false**
across 35 documents. Two narrowings — dedupe by label, exclude blocks declaring `(x0` — removed both
false positives *by name* (a re-quoted block in an Addendum; a class carried forward with no finding
from the batch) and left both true positives standing. Re-measured: 3 findings, 3 true, 0 false.

---

## Step 8 — why an amendment note is written LAST

`IMP-0333`: the dispatch amending review 29 hit the account's spend limit five minutes in, leaving an
amended header, Summary and body, a §9 gate block still carrying the pre-amendment counts, and a
header note asserting *"the gate block below carries the revised counts"*. The only durable record of
how far it reached was that note, and it was false in exactly the direction that hides unfinished
work. A later session had to reconstruct the true state by reading the document against the log.

---

## Step 8 — why bookkeeping is incremental

The step used to batch every status, the digest and the review document after the final file edit,
which meant any interruption landed in the worst available state: **the durable changes on disk and
nothing recording them.** On 2026-08-25 the dispatch applying review 27 hit the account's spend limit
after change 6 of 12. Six changes were correctly wired and measured, all ten processed findings still
read `NEW`, the digest was unregenerated, and the document still said *"Nothing in this document is on
disk."* The only record of which six had landed was a `STALLED` line a human reconstructed by
inspecting the tree. `verify-improvement-log.py` run at that moment reported **seventeen unread
entries and fired both triggers**, pointing at a review whose changes were already half applied
(`IMP-0301`).

`IMP-0033`'s lesson, one level up: an unreconciled log cannot tell *"nothing was learned"* from
*"nobody did the bookkeeping"*.

---

## Step 8 — why an unclosable entry stays open

`IMP-0208` was closed on a needle matching a sentence the closing review had just written, and the
defect was still live for a real signed-in user three days later (`IMP-0224`, `IMP-0225`). An honest
open entry beats a closed one nobody tested.

And on the `revisit_when` half (`IMP-0516`): review 45 reasoned correctly that a V5 entry must not be
*closed* on evidence nobody had gathered, and then chose the one remaining state that keeps the gate
red forever — halting an unrelated build at step 3 of 68. `classify()` recognises exactly four
discharges and a bare `revisit_when` is none of them.

---

## Review filenames — why the number is claimed, not computed

"List the directory, take the highest number, add one" is a race, and this project has run it twice in
one day. Two dispatches that list `docs/improvements/` before either writes compute the same `-N`. On
2026-08-31 Groups 1 and 2 both chose `-7` (`IMP-0539`); nothing was lost only because the losing
dispatch had not yet written anything (`IMP-0540` corrects `IMP-0539` on exactly that point), and
`IMP-0541` states the residual race without the false clobber claim.

This is `IMP-0080`'s race at a second resource. The id space next door was mechanised after prose
failed **six** times.

---

## Executables — why yours go in `scripts/`, and live ones do not

Both halves were established on 2026-08-23 by one script. Review 18 wrote
`provisioning/dataverse/verify-access-test-identity.ps1` — a live Dataverse verifier, four access
routes, 285 lines — into a folder governed by a contract it did not follow, and closed on a digest
check. Three hours later an unrelated build surfaced three convention failures and recorded them
against the wrong owner, because the file was untracked and read as another session's work. That was
the cheap half. **The expensive half is that the script could never run at all:** it assigned `$pid`,
which is a read-only PowerShell automatic variable, so it died before querying either of the two
membership routes the control exists to check — and the contract suite passed over it throughout,
because that suite parses the AST and never executes anything.

---

## Corpus measurement — why fixtures cannot answer the second question

Review 28 wired four gates, each with passing fixtures. Against the actual tree they produced **five
distinct false-positive classes and one masked true positive**: a requirement reported as withdrawn
because a neighbouring row cited *another* requirement's withdrawal, `asks` matched inside `tasks`,
and — the dangerous one — a plausible FIFO pairing of dispatches to terminal log lines reported
**zero** unreconciled dispatches while hiding the one real stall and flagging a healthy dispatch
instead (`IMP-0319`). Nothing would have caught any of it: `verify-build-config.py` runs a new gate's
`--selftest` and accepts exit 0, which is a can-it-fail proof and nothing more.

Review 29's cluster C measured its obvious design at 31 findings across 3 documents, **15 of them
false** — 48% wrong on first contact — and the measurement is what replaced an inferred rule with a
declared one.

---

## Shell measurement — the `&&` chain that deleted a measurement

`IMP-0542`, 2026-08-31: review 7 measured whether `lead-agent` is ever a dispatch target with
`grep -c 'ROUTED_TO:lead-agent' logs/routing.log`, chained after an earlier `grep -ci` that matched
nothing. The chain aborted, the lead-agent count never ran, and its absence was written into the
review document as *"0 ROUTED_TO:lead-agent lines, against 208"*. The true value was 2. It was caught
only by re-running it unchained at step 8.

This is `IMP-0007`'s pattern — *"the `! grep … && echo` gate pattern turns EVERY grep failure,
including exit 1 no-match, into a PASS"* — committed by an agent that had read that exact line in
`logs/known-failure-modes.md` at activation. Knowing the pattern does not prevent it when the shell is
being used as a notepad rather than as a gate.

---

## Prose gates — why polarity inverts on a corrected file

A correction in this repository's documentation style *retains* the withdrawn wording so a reader can
see what changed — an erratum quotes the sentence it is withdrawing — so the corrected text contains
strictly MORE instances of the offending phrase than the defective text did.

The shape has been measured **five** times across three reviews, at 48% to 100% false (`IMP-0422`,
and `IMP-0428` is it happening to a gate already wired — `verify-design-doc-claims.py` went red on the
erratum written to satisfy it).

---

## Why this agent exists at all

The learning loop this agent automates already ran once, manually. On 2026-08-14 the reviewer asked
for it twice, explicitly:

> "Make a handover document to update all the docs and scripts so the next time we don't run into so
> many problems deploying to development."
> "Based on the created handover document … Adjust the multi agent development system files so i
> don't run into these problems again."

It produced real work: `C-TECH-049`–`056`, `skills/how-to-verify-a-platform-contract.md`, three verify
scripts, edits across seven agent files. And then 08-16 and 08-17 produced ten new incidents in the
*same classes*.

The loop failed for three reasons, and this agent's design is a direct response to each:

| Why the manual loop failed | What this agent does about it |
|---|---|
| It ran when a human remembered | Fixed triggers, one of them automatic |
| It learned at **instance** altitude — one gate per incident, forever one behind | The promotion ladder's altitude rule: a second instance may not get another instance patch |
| It wrote to files nobody read back | Regenerating `logs/known-failure-modes.md` is a required output, not an optional extra |

Full analysis: `docs/improvements/2026-08-17-failure-analysis-and-self-learning-design.md`.

---

# From `agents/WORKFLOW.md`

Relocated by improvement review 8, 2026-09-01. `WORKFLOW.md` keeps every rule; these are the
incidents behind the dispatch-death section.

## The fourth case — a dispatch that stalls without erroring

**Three instances in one day, all on 2026-08-25, against a class the log scored `x1`:**

- the 09:23 `architect-agent` dispatch, reported stuck by the reviewer, producing nothing
  (`IMP-0291`);
- the 23:25 `development-agent` dispatch to add the `A-FIN-07` marker — still absent from
  `ensure-auditing.ps1` the next day;
- the 23:25 `improvement-agent` resume to fold two findings into review 26 — review 26 mentions
  neither id.

### And the reconciliation that checked four things and was wrong about all of them

**`IMP-0484`, 2026-08-29.** The 09:00 reconciliation of the 2026-08-28 23:58 `pipeline-agent`
dispatch checked four things — log content, Deployment Summary mtime, marker absence, `ListAgents` —
and concluded *"died before Stage 0 produced any output — no live write was attempted, nothing to
reconcile."* Every one of the four is a fact about a file or a session.

Live queries then showed the table, all four attributes, the alternate key, both role privilege
grants, the audit switch and the seed row **already present in DEV**, and two stale privileges
already revoked. The dispatch had done nearly all of it and died before writing the line that would
have said so. Nothing was damaged only because the writes happened to be complete and convergent.

### The resume measurement behind the two-conditions rule

`logs/routing.log` records 13 resume attempts: one incident of three failures (`No transcript found
for agent ID`, `logs/routing.log` line 334, all 2026-08-28) against at least six whose applied output
is on disk today. The `SendMessage`-has-no-`model`-parameter case was caught on 2026-08-28 only
because the agent re-derived its own tier from its model identity and refused to author under it
(`logs/routing.log` line 317, `IMP-0399`).

The 13 lines exist only because lead-agent narrated them: `SendMessage` calls leave no repository
trace, so no gate can observe a resume attempt.

### The routing-reconciliation cutoff, and the paragraph it replaced

The cutoff was set by reviewer decision on 2026-09-01 — *"the reconciliation date can be yesterday …
everything before that is history"* — recorded in
`docs/improvements/2026-09-01-improvement-review-2.md` (`IMP-0547`). Its reading at that date was
**17 unreconciled, 4 in flight, 5 closed** of 26 in-scope dispatches. Re-scoping took it from 33
unreconciled to 17, not to zero, which is why the gate stayed `--warn-only`.

**This replaced a paragraph that said the opposite** — *"the mechanical half is deliberately not
proposed here"* — written when the log carried 99 `ROUTED_TO` against 9 `GATE_RECEIVED`, where a gate
over that history would have emitted ninety false positives. The gate was built anyway, with the
cutoff that paragraph predicted it would need. The counts were 208 and 105 when it was retired
(2026-08-31, `IMP-0537`): a superseded statement that keeps instructing the next reader is the costly
kind of stale reference.

## The fifth case — the exact message that arrives wearing success

The final message that triggered `IMP-0357`, 2026-08-28:

> *"I already have a Monitor watching for the idempotent re-run's completion (task bhkamkuhd).
> I'll resume automatically once that notification arrives — no further action needed from me
> right now."*

In the real instance no `logs/pipeline.log` entry existed for the dispatch at all, and the reviewer
was reporting the app failing to start (*"Encountered internal server error"*) at the same moment.
The remaining reconciliation took two clean `pac code push` calls.

The dispatcher's-half rule (`IMP-0520`, 2026-08-31) was added after the diagnosis paragraphs had
been cited in dispatch briefs and the failure recurred anyway, twice more, both times at roughly
500k tokens. It then recurred again hours after that paragraph was applied (`IMP-0537`), which is why
`WORKFLOW.md` now names the next rung as a `lead-agent` activation-sequence checklist rather than
another paragraph.
