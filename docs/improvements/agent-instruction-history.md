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

---

# From `agents/lead-agent.md`

Relocated by the generalisation initiative, Phase 1, 2026-09-08. `lead-agent.md` keeps every rule;
these are the incidents behind them. This file is on the hot path of no dispatch, and
`lead-agent.md` is on the hot path of every one.

## Delegation — why a hop is a dispatch and not a persona switch

`IMP-0143`, 2026-08-21. "Act as plan-agent, then architect-agent, then development-agent" inside one
continuously growing conversation runs all three on whatever model that conversation happens to be
on. That is how this project ran two full days of Haiku/Sonnet-tier work on Opus, at Opus's price,
because nothing ever actually dispatched a separate, pinned session. The Tier column in the roster
means nothing until the agent runs on its own invocation.

## WBS resolution — why build order is not conversational

`IMP-0031`. Build order was set by conversation until 2026-08-19, and the result was Phase 1 —
contractually due 25 September — sitting at 0 of 13 tasks while Phase 2, due three weeks later, was
two-thirds built. The queue is not advice; it is what the Client bought, in the order they bought
it.

## The `ROUTED_TO` reason line — why the tier and the terminal line are both mandatory

`IMP-0290`: a dispatched agent cannot see its own dispatch parameters — its generated frontmatter
and `config/models.yml` both show only its **default** tier. The `ROUTED_TO` line is the one
artefact that can tell it otherwise, and its absence produced a `blocker` finding logged against a
dispatch that had in fact been escalated correctly.

`IMP-0291`: on 2026-08-25 three dispatches were recorded as routed and never reconciled, and the
only trace any of them left was an unclosed `ROUTED_TO`.

## Dispatch parameters — the withdrawn "nothing sits between an agent and the Task tool" claim

**Erratum 2026-09-01 (improvement review, WS-E).** The rung list in `lead-agent.md` was introduced
by a paragraph reading *"Nothing sits between an agent and the Task tool, so these are prose and
will stay prose."* **That is false, and it was never tested** — it was the stated reason every rung
went unenforced. `permissions.deny` in `.claude/settings.json` accepts an `Agent(<name>)` matcher
and **refuses the dispatch at the tool call**; measured live on Claude Code 2.1.100 in three runs
with a control (denied → refused naming the rule; empty deny → same dispatch succeeded; project
agents and ordinary work unaffected). Rung 6 uses it.

The withdrawn sentence conflated two different things, and the distinction is what to carry
forward: **which agent a dispatch names is mechanically constrainable; what its brief claims is
not.** Rungs 1–5 each turn on a *parameter or premise* — `model:`, `isolation:`, the truth of a
cited fact, whether another dispatch is mid-edit — and `permissions.deny` matches on the agent
**name** only, so those five stay prose on their merits rather than on a false generalisation. The
narrower claim — that no gate in `scripts/` reaches them — does survive, because the control rung 6
uses is a harness permission and not a script.

The list carries no count in its heading (`IMP-0532`): the heading read *"Three things"* against
four rules for three days, which is `hand-maintained-count-drifts-from-source` in prose.

## Rung 1 — the tier correction that silently no-opped

`IMP-0399`. `SendMessage`'s schema has no `model` field, so passing one **returns success,
silently, as a no-op**. `logs/routing.log` was written asserting *"Escalated to strategic tier
(opus)"* and the target session's pin was unchanged; the next turn revealed it. **A resume call
accepting an extra parameter without erroring is not evidence the parameter took effect.**

## Rung 2 — the worktree that could not see the file it was sent to amend

`IMP-0400`. A worktree is created from the current *commit graph*, so by definition it excludes
everything not yet committed, and this project runs largely on uncommitted working-tree state
between dispatches: concurrent sessions routinely edit the same synced path without committing. An
architect-agent dispatch sent to amend a TAD got a worktree whose newest reachable commit held a
**1318-line** version of a file whose real working-tree form is **2298 lines**. It could read none
of the state its brief named and could not write its output back to the real file.

## Rung 3 — why a citation makes a paraphrase look verified

`IMP-0381`, the founding instance: a brief stated *"revision 0.5, at a CODE REVIEW REQUIRED gate"*;
on disk the file was revision 0.6, status DRAFT, and the phrase `CODE REVIEW REQUIRED` appeared once
as prose describing revision 0.2. A peer session had advanced it in between. The TAD drafted from
that brief had to be corrected.

**The rule was widened on 2026-08-28 because ONE dispatch brief produced two more instances,
neither of them about a document's status** (`IMP-0460`, `IMP-0464`):

- It asserted a **platform semantic** — *"`if()` evaluates only the branch it takes in this
  runtime, proven on this project by TD-07/TD-08 (`IMP-0124`), so the guard is real"*. The attached
  id's lesson carries that as a trailing *"Related:"* clause, and two later findings record the
  question as **open**. An expression was built on it and rewritten before it shipped.
- It asserted a **disclosure control** — *"aggregate-only content (no cell smaller than a safe
  threshold, consistent with S6.3.4's existing reasoning)"*. Three approved documents said the
  opposite: the SDD's minimum-cell-size requirement was **struck through and withdrawn** by a dated
  reviewer risk-acceptance, and the very section cited argues *"suppression would not help"*.
  Applied, it would have changed what every trustee sees.

**No gate is possible here, and that is structural rather than a gap worth closing.** A dispatch
brief is a Task-tool prompt: it is never written to a file, and `logs/routing.log` records the
routing decision and the WBS id, not the brief's text. There is no artefact for a script to read.
Both 2026-08-28 instances were caught the only way they can be — the receiving agent read the cited
source before building on it.

## Rung 4 — the credential wall four dispatches walked into

`PROVISION_APP_ID` and `PROVISION_CERT_THUMBPRINT` are **reviewer-held by design** — not persisted
anywhere a dispatched agent session can read them (`agents/development-agent.md`, the "holds no
live credential at all" row). So any brief whose steps include a live run of
`provisioning/dataverse/ensure-schema.ps1`, `ensure-auditing.ps1` or any sibling that writes to
Dataverse **will** stop at `REVIEWER ACTION REQUIRED` — the throw is
`provisioning/common/provisioning-common.ps1:170` — every time.

**The protocol is not wrong and does not change** — it routes this correctly once it happens. What
is wasted is the round-trip. Four instances, none of them pre-checked by the dispatching agent:
`IMP-0048`, `IMP-0061`, `IMP-0105`, `IMP-0528`. Deliberately a briefing rule and not a gate, for the
same reason rung 3 cannot be one.

## Rung 5 — the build dispatched over source another dispatch was editing

**A dispatch scope is not a filesystem boundary.** The packer and every source-level gate read the
TREE, not the brief. `IMP-0531`/`IMP-0532`: the wbs:6.9 build was dispatched at 18:19 scoped to
*"7 of 8 reviewer items; item 5 tracked separately under the concurrent development-agent dispatch,
not part of this dev-summary's scope"*, and blocked at 18:28 on step 34 of 70 — `C-TECH-060`, a
380-char flow description that the concurrent dispatch had appended to and had not yet reached its
own constraint check over. It fixed it at 18:29. **Nothing was skipped and no agent got anything
wrong**; the sequencing did. The first finding blamed the editing agent, and promoting that root
cause would have written a rule against a step nobody missed.

The tell that this is a *briefing* failure and not an unavoidable one: **the same lead-agent turn,
in the same minute, got it right for the other dispatch** — the 18:19 architect-agent line names the
concurrent state explicitly (*"instructed to amend on top of that working-tree state, not a clean
checkout"*), and the build dispatch one line above it does not.

Prose, like rungs 3 and 4. The one file that does record dispatches is `logs/routing.log`, and a
gate pairing its `ROUTED_TO` lines to terminal lines is exactly the FIFO design `IMP-0319` measured
*reporting zero unreconciled dispatches while hiding the one real stall*. This stays prose
deliberately, not by omission.

## Rung 6 — why all four generic agents are denied

`claude`, `general-purpose`, `Explore` and `Plan` are reachable through the same Task-tool mechanism
as this project's 18 agents and share none of its machinery: no tier pin, no constraint check, no
gate keyword, no improvement-log capture. A dispatch to one produces work that **looks delivered and
was never gated** — and raises no error, which is what makes it the highest-likelihood silent
mis-route rather than merely another way to be wrong.

**Reviewer decision, 2026-09-01, recorded because it overrode the applying review's
recommendation.** That review proposed denying only `claude` and `general-purpose`, on the ground
that `Explore` and `Plan` have no Edit/Write/NotebookEdit grant and so cannot produce an ungated
artefact, and are useful as read-only search. **The reviewer chose all four.** The rule is therefore
the simple one — *no generic agent, for anything* — and it costs read-only fan-out search, which is
a real capability this repository has given up deliberately. If that cost is later judged too high,
the narrowing is a two-string edit to the same array and the reasoning is in the review document; do
not re-derive it.

**Caveat, unresolved:** `claude` is this harness's default agent when no name is typed, and is
described as FleetView's default. Ordinary work was verified unaffected in Claude Code, but
**FleetView was not tested.** If this repository is ever driven from FleetView, `Agent(claude)` may
need to come back out of the deny list.

**No instance has occurred** — 209 `ROUTED_TO` lines in `logs/routing.log` name only project agents.
This rung is preventive, and it is worth the words precisely because the failure mode is silence: a
mis-route to a generic agent leaves no distinguishing trace to find afterwards.

## Reading the improvement queue — why it is the gate and not two greps

**This used to be two greps, and they were wrong in the expensive direction.** `NEW` has not meant
"unread" since improvement reviews 5 and 6 gave the gate a four-state model; a `reviewer-deferred`
entry is still `NEW` in the file and carries a reason a human accepted. Run on 2026-08-24 the greps
returned **27 pending and 12 blockers** against the gate's **6 unread and 3 unread blockers** — the
difference is 21 findings already decided. A routing trigger that is permanently and visibly
over-tripped is one that gets ignored, and ignoring it is how this class keeps recurring
(`IMP-0265`, and `IMP-0183` is the same shape in `improvement-agent.md`).

`IMP-0265` is also why the check runs *before* dispatching build or pipeline work: both check
`C-TECH-061` at their own activation, so a live blocker or batch-trigger halts them *after* the
dispatch has already been made — which is how `build-agent` came to be the thing that keeps
discovering a red queue for reasons unrelated to the code it was sent to build, twice in two days.

## The exit code — the blocker that halted a build at step 3 of 70

`IMP-0527` (**blocker**): a routing note recorded that a parked blocker was *"already routed
separately (improvement-review-4, awaiting APPROVE IMPROVEMENTS, not itself a build gate)"* and
dispatched `build-agent` anyway. `verify-improvement-log.py --check` **had been run** — its counts
were read, its exit code was not — and the claim was false in the most checkable way available:
`improvement-log-check` is the literal, HARD, **third** step of the very build config being
dispatched. The build halted there, at step 3 of 70, before any packaging work.

A blocker at `awaiting-approval` **fails by design** — the gate says so in its own output, *"a
stalled review must not go quiet"*. This is `improvement-agent.md`'s *"execute it, do not read it"*
rule (`IMP-0426`) applied to routing, and `gate-reassures-wrongly` is at ×27.

---

# From `agents/build-agent.md`

Relocated by the generalisation initiative, Phase 1, 2026-09-08. `build-agent.md` keeps every rule.

## Why build-agent is not a mechanical-tier agent

**This agent was tier `mechanical` until 2026-08-17, on the rationale that it "reads a YAML file and
executes commands — no reasoning required."** That description did not survive contact with the
work. In one week this agent decompiled `SolutionPackagerLib.dll` with `ilspycmd` to recover an
undocumented packer contract, worked out that `pac solution check` requires a packed `.zip` and that
the step order was therefore wrong, and found a HARD compliance gate that had been a silent no-op
since the day it was written. That is the hardest diagnostic reasoning in this system. See
`docs/improvements/2026-08-17-failure-analysis-and-self-learning-design.md` §2.1.

Its config is an input to be verified, not an instruction set to be trusted: three of this project's
own gates were found broken while reporting PASS.

## Artifact directories — why one is resolved per build

`IMP-0016`. Six builds once shared one artifact directory, and the manifests for three of them no
longer exist. `IMP-0016` and `IMP-0022` are also why activation step 0 exists at all: build-agent and
pipeline-agent were the only agents in the roster that loaded no prior experience, and so re-entered
the same minefield every run.

## The two slugs — why `<build-config-slug>` and `<feature-slug>` are read off the dispatch

This file used to spell both of them `<slug>`. They are equal only when a feature owns its own build
config; **whenever a build config is shared across features they differ** (`IMP-0479`, `IMP-0494`,
and `IMP-0470` is the same conflation costing a build).

## Re-hashing the build config — the step inserted mid-build

**Not hypothetical.** On 2026-08-23 a concurrent improvement-agent session applied a fix that
inserted a new step between `secret-scan` and `source-validate` while a build was executing. That
build's preflight had already passed against the 37-step version. It recovered by hand — re-ran
preflight (38 steps, PASS), ran the inserted step, and re-ran the full Pester suite, which
incidentally showed one of its two failures had been fixed concurrently too. That manual recovery
was correct and is now a step rather than an improvisation (`IMP-0213`).

Two sessions can be live in this repository at once (`IMP-0080` recorded the same hazard in the
improvement log), and this one is on a synced SharePoint path.

## Re-checking the improvement queue at manifest time

`improvement-log-check` is step 3 of the config because it is cheap — which means it proves the queue
was clear **at that instant**, and nothing else. A build takes twenty minutes; another session
appends findings during it.

`IMP-0343` is the instance: `improvement-log-check` passed at build start (335 entries, 7 unread) and
a concurrent session appended `IMP-0339`–`IMP-0342` during the ~20-minute window. Re-checked at
manifest time — after all 57 steps and packaging — the same gate reported 339 entries and 11 unread,
over the batch trigger. No rework was needed, and that is exactly why this is a record rather than a
failure.

`--warn-only` (added by improvement review 30 change 9) is what makes that distinction expressible:
the re-check reports without reddening a build that did nothing wrong. Packaging past an unread
blocker is how `IMP-0285` cost a full nine-minute build. **Never write `... || true` here** — that is
the `gate-cannot-fail` pattern this repository has recorded 33 times, and it would silence the
blocker case along with the harmless one.

This is deliberately not a step in the build config: every step there runs *before* build-agent
writes the manifest, so a config step cannot observe manifest-time state at all.

## Warnings — the pack warning carried through weeks of green builds

A pack warning that root components were "not defined in customizations" was carried silently
through every green build on this project for weeks. It was a precise, correct report of a defect
that later failed the import. Tools rarely warn about nothing.

## A repeating warning is matched on its figures, not its wording

`IMP-0573` is the seventh instance of `untriaged-tool-warning` and the first of this shape. Vite
prints *"Some chunks are larger than 500 kB after minification"* **identically** at 558 kB and at
1,204 kB. The triage row existed, cited ~558 kB, and said *"pre-existing and not worsened"*; the live
build measured 1,204.72 kB, because `recharts@3.10.1` landed in a commit later than the prose and was
named in no Dev Summary. Three successive reads matched the wording and re-asserted "not worsened"
without re-reading the magnitude.

## Deferred steps — the broken lint step behind four green builds

Builds #1–#4 all reported `SUCCESS` while `auth` and `lint` were deferred, each time annotated "not a
defect". Defensible once; collectively it hid a broken `lint` step for four consecutive green builds
(`IMP-0004`). A step that did not execute is a **coverage gap that the next build inherits**, not a
footnote that resets.

`auth` is the first step to declare an execution context (`when: ci`): it needs GitHub's OIDC token
variables and cannot run anywhere else.

## `warnings_detail` — why the shape is declared before the gate exists

Added 2026-08-30 by improvement review 44 (`IMP-0499`, `IMP-0500`). It is the input a gate needs, and
it did not exist: `IMP-0500` measured all 22 tracked manifests and found the `warnings` block in
**five different shapes across nine key names**, with a near-miss `warnings_detail[]` improvised in 3
of them. Nothing diffs a build's warnings against the Dev Summary today, and `untriaged-tool-warning`
is at ×6 because of it.

Nothing is wired against this field yet **by design** — the diff gate is deferred until three
manifests carry the declared shape, so it can be measured against a real corpus rather than fixtures
(review 44 §6). Write it correctly now and the gate becomes a value comparison later; keep
improvising key names and it stays a prose-matching problem this project has already measured at
48–100% false (`IMP-0422`, `IMP-0428`).

`steps_not_executed`'s mandatory-and-may-be-empty rule has the same origin: an absent field reads as
"everything ran", which is exactly the ambiguity that hid the broken `lint` step.

## `wbs` and `soft_gates` — the two conventions that regressed

Both were added on 2026-08-28 by improvement review 33; both were previously conventions held in the
authoring agent's head, and both regressed in exactly the way an unenforced convention does.

`IMP-0350`: build `20260826-1` carried `"wbs": ["6.1","6.3","6.9"]`. The very next build of the same
feature carried no `wbs` at all. Both reported SUCCESS with every gate green, and the previous cycle's
test report had cited the field by line number, which made it look established. The task id is the
join key between a commit, a contract line and an invoice.

`IMP-0395`: `warnings.total` is an aggregate. Builds recorded `warnings: {total: 83, untriaged: 0}`
while the `derived-counts` step printed four drifts on every run, and a fifth would have been
arithmetically invisible inside 83. A per-step number makes 4 → 5 visible. Note this covers steps
that are SOFT *via `--warn-only`*; a step that is SOFT by its own internal design
(`source-derived-test-counts` exits 0 with findings by choice) is not derivable and not covered.

## `source_commit_note` — why it records a count and never contents

`IMP-0078`: build #7's manifest recorded a commit from the previous day that contained no `rev_grant`
source at all, while the zip it described packaged `rev_grant` with a form, three views and fifteen
attributes — the sha was read from `HEAD` over a dirty tree, which is the normal case for a build that
packs work before committing it. A dirty build was indistinguishable from a clean one in the record.

`IMP-0324`: build `20260825-1`'s note stated the packaged tree "includes the
trustee-portal-visual-refresh changes (rev_roundfinance table, LandingPage/charts UI, A-FIN-05/07/A-002
marker fixes)". No `LandingPage*`, chart or `RoundStatistics*` file existed anywhere under the code
app, and the built bundle in the same artifact contained none — the Dev Summary correctly reported them
as NOT STARTED. The dirty-path count in the same note was right. `C-COM-005`'s rule that a `Status`
column is a claim and not a result applies to a manifest's own prose exactly as it applies to a WBS
row.

`scripts/verify-build-manifest-note.py` enforces the shape, and it is a SHAPE check on purpose: it
forbids a class of claim rather than adjudicating one. Resolving prose tokens to files would be fuzzy,
and fuzzy prose-matching is how one review produced five false-positive classes in a single sitting.

## `--build-config` — why the flag is passed when the slugs differ

Without the flag the script derives its SOFT-step list from `config/<feature>-build.yml`, using the
manifest's **own `feature` field** — so a feature that shares a parent's build config points it at a
file that does not exist and it stops with `NO BUILD CONFIG`. **Verified by running it, not by reading
it:** `--selftest` carries the fixture *"a manifest naming a feature with no build config fails rather
than reporting OK → exit 1"*. So the failure is loud and the manifest is never judged against an empty
step list — the cost is a red gate you then have to diagnose at the one moment the artifact is already
packed (`IMP-0479`).

It is deliberately NOT a step in the build config. Every step there runs before the manifest is
written, so a step naming `$ARTIFACT_DIR/manifest.json` would reference a path nothing in the config
produces — a gate that cannot run, which is the exact class `verify-build-config.py` exists to catch.

## Why the `IMPROVEMENT LOG` line is mandatory even when empty

Its absence is what let a week of findings go uncaptured. It is positioned where the reviewer is
already reading, so an omission is visible at the moment of review.

---

# From `agents/pipeline-agent.md`

Relocated by the generalisation initiative, Phase 1, 2026-09-08. `pipeline-agent.md` keeps every rule.

## Why pipeline-agent is not a mechanical-tier agent

**This agent was tier `mechanical` until 2026-08-17**, described as "reads a YAML file and executes
deploy commands in sequence — no reasoning required." In one week it diagnosed a form-dependency block
on an attribute delete and devised a transitional-import sequence to clear it, ruled out data, binding,
security and XML-structure causes by live query before concluding a control classid was wrong, and
caught a *successful* import that had silently created nothing. See
`docs/improvements/2026-08-17-failure-analysis-and-self-learning-design.md` §2.1.

## Activation step 0 — the capability that had to be re-taught

The digest's *"Capabilities established in earlier sessions"* section exists because a working
certificate-from-keychain procedure established on 2026-08-16 was gone by 08-17 and the reviewer had to
re-teach it (`IMP-0022`). Do not ask the reviewer to re-supply something that file records.

## Artifact provenance — the directory that looked deployable

**The artifact to deploy is the one on build-agent's `HANDOFF … artifact:` line, not the newest
directory under `build/artifacts/`.** A directory listing cannot tell a finished build from a
build-agent session that died after packing the zips: `IMP-0582` was
`trustee-portal-visual-refresh-20260902-3/`, which held both zips, a code-app `dist/` and
`test-results/` and had no `manifest.json`, no `logs/build.log` line and no test report. It looked, from
a listing, exactly like the two deployable builds either side of it. The provenance gate is what makes
the difference readable, and it runs first because everything after it costs a live environment.

## The assumption register — A-001 and the three empty dropdowns

A-001 was recorded exactly as the process asks: a guessed multi-select control classid, severity E2,
`OPEN`, "pending V4". It then shipped, and the reviewer found three fields rendering as dropdowns with
no options. The register predicted the defect precisely and was wired to nothing — `C-TECH-052`
requires *recording* a guess, and nothing required *closing* it (`IMP-0014`).

## Refusals — why the count is derived and not typed

A table typed into the agent file needs retyping on every recurrence and did not get it: the version
that stood there until 2026-08-24 described *seven* instances while the log held eight (`IMP-0252`).
`python3 scripts/refusal-history.py` reads every instance, its `harness_mode`, its `dispatch` site and
which layer refused, from the log itself.

## What actually separates a refused call from an accepted one

**The boundary is not write-versus-read, and the auditing PATCH is no longer an example of it.** This
section used to name the `organizations` / `EntityDefinitions` PATCH that switches auditing on — refused
on 2026-08-19 under an explicit `APPROVE TENANT` — as the third instance. It ran clean on the first
attempt from a dispatched pipeline-agent session on 2026-08-23 (`IMP-0222`), so *"reliably refused"* was
never true of it. And a **pure read** was refused the same day: a `pwsh` script that only resolved the
auth context and printed eight characters of the app id, making no Dataverse call at all (`IMP-0220`).

What actually separates the two, as observed: **a shell command that itself touches local certificate or
keychain material** gets refused; **a command going through an already-authenticated tool's own
credential path** does not, even for a live write. A hand-rolled script that dot-sources
`provisioning/common/provisioning-common.ps1` is the first kind. `pac` is the second.

## The `pac` verb search — and the class that has no verb

Confirmed on 2026-08-23 (`IMP-0220`): `pac admin assign-user --environment <url> --user <upn> --role
"<role name>"` performed a live `systemuserroles` association **from the same background session** where
the equivalent `POST systemusers({id})/systemuserroles_association/$ref` was refused twice — once inside
a full write script, once isolated down to nothing but token acquisition. `pac org fetch --xmlFile
<file>` is the working read path. Three blocked attempts preceded finding this on the fourth, which is
three more than the next run needs to spend.

**One operation class has no target, and looking for one is wasted effort.** `ensure-schema.ps1`-class
*metadata creation* — entities, attributes, global option sets, security roles, field security profiles
(`C-TECH-050`) — has **no native `pac` verb at all** in pac 2.4.1. All 22 top-level groups were
enumerated on 2026-08-23 and none reaches entity, attribute, role or field-security-profile metadata,
which is the reason `ensure-schema.ps1` exists in the first place. Role *assignment* has one (`pac admin
assign-user`); role *creation* does not (`IMP-0245`).

## Why the reviewer's block is zsh

Never emit `$env:VAR = '…'` there: in zsh, `:P` is the realpath expansion modifier, so the line
mis-parses into a `no such file or directory` error naming a garbled path, and the reviewer goes looking
for a missing file rather than a wrong shell (`IMP-0253`).

And the verification query is not optional: the reviewer enabling organisation auditing by hand on
2026-08-19 was real and correct, and a query still showed retention unset and all five tables still off —
the portal confirms the click, not the outcome (`C-TECH-064`).

## Write markers — why they are written per operation and in real time

A dispatch that dies between `WRITE BEGUN:` and `WRITE ATTEMPTED:` — spend limit, credit exhaustion, a
silent stall — leaves a **dangling `WRITE BEGUN:`**, which is partial evidence that something reached the
environment, instead of the blank page that is indistinguishable from never having started (`IMP-0484`,
and the same property already forced on `improvement-agent` by `IMP-0301` and `IMP-0333`).

**A dangling marker has a SECOND reading, and you cannot tell the two apart from the log: a dispatch that
is still alive right now.** `logs/pipeline.log` has no lease, no lock and no append-time identity, so two
live dispatches reconciling the same build write into it interleaved, and neither can see the other.

On 2026-08-31 this produced a **factually wrong line**: a `WRITE ATTEMPTED` for a solution import naming
the PUBLISH step's GUID as the import id, written by a session that was not the one running the import
(`IMP-0538`). No damage followed only because both writers' operations were idempotent, which is luck, not
a control. `IMP-0538`'s `pac solution import` was still running normally at the moment its dispatch was
declared dead, and completed correctly.

**There is no lock, and the rule in the agent file is not one.** It is the reader-side half only. A lease
keyed on "an unclosed `WRITE BEGUN:`" was proposed and **not built**: this log carries 12 `WRITE BEGUN`
against 15 `WRITE ATTEMPTED`, so the markers do not pair and such a detector would misclassify existing
history on its first run. Whether `logs/pipeline.log` gains a real lease is an open decision recorded in
improvement review 7 §6.

`verify-provisioning-report.py --check` parses the markers, never the surrounding prose — an entry that
*mentions* a script to say it was never run is not a write attempt, and on 2026-08-22 one entry did
exactly that (`IMP-0252`). This does not close the window, it shrinks it: a dispatch can still die before
its first `WRITE BEGUN:` append. Nothing can make a log line and a live write atomic across a process
death.

## A refusal is a control — where step 4 came from

Until 2026-08-24 this section instructed a retry in lead-agent's foreground session, on one success whose
harness mode was never recorded (`IMP-0173`). `IMP-0252` was then refused in exactly that position under
Auto Mode, and the route that has actually completed this operation class is step 4 as it now stands — the
reviewer's own shell, on 2026-08-24, which produced three real platform findings the refusals never would
have.

Improvement review 21 proposed moving the operation into a broader-permissioned session to get a different
answer from the classifier, and had to be rejected (`IMP-0264`). **If a proposal's advantage disappears
once the operation is described honestly, that is the tell.**

## The `pac`-credential-path exemption is observed, not guaranteed

Added 2026-09-08 (`IMP-0636`). The measurement: `pac solution import` against the same DEV org, for the
same feature, from what is described as the same class of dispatched session, **succeeded twice on
2026-09-05 and was refused with "Blocked by classifier" on 2026-09-07** — with `pac auth list` showing an
active profile and `pac org who` succeeding live moments before the refusal. No isolated variable
distinguishes the two runs from the log alone, so the refusal boundary is **not** the
cert-versus-credential-path distinction described above, or not only that.

**This narrows what the document claims. It does not narrow what the classifier sees.**

## Verification list (a) — why it is derived from source

**Do not write a list of component types by hand.** This class of failure has occurred three times
(`IMP-0013`, `IMP-0018`, `IMP-0019`), and the first instance is instructive: the hand-written
verification list for the first DEV deploy queried `environmentvariabledefinitions`, `appmodules`,
`sitemaps` and `workflows` — and omitted `savedquery` and `systemform`, which were precisely the two
component types that had silently not been created. The list was correct about everything it named. It
simply did not name the failure.

A hand-written list encodes what you already suspected. A derived list cannot.

**(c) is not optional and cannot be automated away.** Three of the fifteen failures on this project were
invisible to (a) and (b): the deploy succeeded, the component existed and was queryable, and no maker
could open or save it. And import *relabels* matching option-set values but never *deletes* omitted ones
(`IMP-0019`).

## Stage 2 — the Acc hop that does not exist

**CORRECTED 2026-08-19.** That section instructed the agent to *"execute the `environments.acc` block"*
and to wait for `APPROVE ACC`. On this project neither exists. TAD **ADR-006** (`Adopted`) combined Test
and Acceptance into ONE environment; `config/<slug>-pipeline.yml` declares `dev`, `tst_acc` and `prd`, and
`.github/workflows/ci.yml` has had exactly two deploy targets since 2026-08-12. An agent following the
file literally would have blocked waiting for a keyword nobody was going to send, on a config block that
is not there.

## Stage 0.5 — why it runs once per environment

DEV having been prepared says nothing about TST/ACC or PRD. Skipping it is the single most likely source
of avoidable first-import failures — on the feature that produced this stage, it was the missing
prerequisite that turned "just import it" into a fifteen-attempt investigation.

## Why a DEV deploy is an accounting trigger and not a billing event

`logs/pipeline.log` records five DEV deploys, four of them for one feature in five hours. Accounting runs
per deploy so the evidence is fresh; invoices are issued monthly. The ledger's one-invoice-per-session
rule (`C-COM-003`) is what makes the repeated trigger safe.

---

# From `agents/development-agent.md`

Relocated by the generalisation initiative, Phase 1, 2026-09-08. `development-agent.md` keeps every rule.

## `run-source-gates.py` — what a green run does not cover

Until 2026-09-08 the instruction read *"every HARD gate over the source you just wrote"*, which was false
by 3 gates — and the 3 it missed included `no-hardcoded-environment-values`. `IMP-0658` is the halted
build: the authoring dispatch ran the command, read 13 of 13 PASS as full coverage, and handed off source
that a 0.03-second grep rejected at build step 46 of 73.

`verify-assumption-register.py` is named explicitly because `run-source-gates.py` **cannot select it**:
that tool requires a command naming `src/solutions/<Name>`, and this gate takes no path at all. So the two
register gates are not one gate. `IMP-0654` is the halted build that proved it: the authoring dispatch ran
the derived set, 13 of 13 PASS, and the gate that stopped the build was never in it. A documentation-only
change reaches this gate and no other.

**`run-source-gates.py` exists because the static three were not enough, and the reason generalises.** The
instruction previously named two scripts, a third component type arrived, and the list was silently
incomplete — hence deriving the set from the build config instead. Measured on the reference config: 16
gates, under 10 seconds, no authentication, no writes.

**The gap it closes is TIME, not coverage.** Every gate it runs is already HARD and already wired, so a
defect it catches would have been caught — at build time, one or more dispatches after the gate output was
presented and approved. `IMP-0619` is one such defect (a flow and two environment variables missing from
`Solution.xml`'s `RootComponents`); `IMP-0621` is what running the whole set found the same day: **five
further HARD gates red on the working tree and green at `HEAD`**, all five introduced by a batch of three
flows that had already been presented as clean and was waiting only on a build slot. `IMP-0286` and
`IMP-0307` are the same mechanism two dispatches apart at a different gate.

## Assumption markers — the orphan rows

`C-TECH-052` is HARD: every OPEN §10 row carries an `A-nnn` comment at the point of the guess in source.
The script that checks it is already wired as the HARD build step `assumption-markers` — so an orphan row
does not go unnoticed, it goes unnoticed *until the build*, one dispatch after the gate was presented and
approved. That has happened twice from the same cause: `IMP-0286` (A-FIN-07) and `IMP-0307` (A-TRM-2), each
a sibling row added in the same pass as a row that *did* get its marker, each costing a second
single-purpose dispatch to add one comment line. `IMP-0299` is why the count matters: run mechanically, the
first sweep found **four** orphans across three documents where the prose finding had reported one.

Self-assessing `C-TECH-052` by re-reading your own register table is what failed both times. The register
is the claim; the grep is the evidence.

## Step 9 — why the gates run twice

The Dev Summary's own `VERIFICATION SUMMARY` block reports those commands and is therefore written after
them. The last edit to the document is, by construction, an edit no local gate has yet seen. `IMP-0661` is
that edit costing a build: step 8's four gates ran and passed, the revision block was written afterwards,
and `assumption-register` halted the build at step 23 of 73 on the block itself.

## The `constraints/` refusal to expect

If a change secures a new column, `C-DOM-033` requires a row in
`constraints/domain/special-category-register.yml` — and the protection hook will refuse that write,
because `constraints/` is improvement-agent's. Propose the row in the Dev Summary and gate output and let
it be applied there; that file's own header says the same (`IMP-0622`).

## Sub-agent fan-out — why an omission is stated rather than made silently

Added 2026-08-30 (`IMP-0498`): a dispatch whose own opening instruction read *"fan out to
automation-agent per your own sub-agent table"* wrote the flow JSON, the gate-script edit and a new Pester
test inline instead, with no dispatch at any point. The work was correct and the reason was sound; it was
recorded nowhere, and the omission surfaced only because the agent volunteered it afterwards.

Tightly-coupled research-then-implement work is a real category: ground-truthing a platform contract and
writing the construction it justifies sometimes cannot be split without re-deriving the same context
twice. That is a judgement the agent is allowed to make. What it may not do is make it silently, because
nothing else can see it — a Task-tool dispatch is a prompt, never a file, so no gate can assert one
occurred (`IMP-0470`). This makes the omission **visible**, not impossible — that is the whole of what is
available here (`IMP-0143` is the session-boundary rule it sits under).

## Quoting a command for a sub-agent

`IMP-0470`: the `wbs:6.9` dispatch told a sub-agent to run
`python3 scripts/verify-code-app-column-bindings.py src/code-apps/trustee-review-portal`. That gate takes
**two** positional arguments — the app root *and* the `FieldSecurityProfiles.xml` path — and its own
docstring says so two lines from the end. The one-argument form exits 2, which reads like a finding rather
than a typo. A shortened form is not a shorter version of the command, it is a different command.

**No gate can catch this**, and the reason is structural: a dispatch instruction is a Task-tool prompt,
never a file, so there is nothing for a script to read (established in improvement review 39 for the same
class of defect).

## Reviewer-executed operations — the five instances and the three refusal points

Five instances of this class have been recorded, the fifth (`IMP-0170`) because the fix from the first
(`IMP-0084`) landed only on `pipeline-agent.md`: an explicit reviewer directive to create a named security
role, citing the role file's own documented closure procedure, was refused by the classifier and the WBS
task stayed open with nothing actionable written down.

**The foreground-retry step** (`IMP-0173`, 2026-08-22): same command, same environment, different execution
context — and that alone resolved A-TR-2 in one attempt after `identity-agent`'s background dispatch was
refused for exactly the call `IMP-0170` describes. Treat it as *try this first*, never as a guarantee: it is
one observation of the classifier's behaviour.

**The dispatch-level refusal** (`IMP-0313`, 2026-08-25): the Agent-tool DISPATCH itself can be refused
before the sub-agent ever runs. The classifier keys on the dispatch *prompt text* describing a live write,
not on any call the sub-agent later makes — measured in one turn on 2026-08-25, where a dispatch describing
a live cloud-flow write was refused and a second dispatch in the same message describing only local file
edits was not. Re-dispatching the identical prompt is the one response that is certainly useless. A primary
agent's own foreground `pwsh` write against DEV has succeeded, unrefused, under Auto Mode (`IMP-0314`,
verified afterwards by read queries against the same environment) — a nested dispatch's refusal is not
evidence about your own session.

**The absent credential** (`IMP-0512`, 2026-08-31): a session that holds no live credential in the first
place. Nothing declined anything, so a foreground retry is missing exactly the same variable and can only
fail in the same way — it costs a turn and teaches nothing.

**And the line none of this crosses.** Rewriting a dispatch prompt to omit or soften a live write in order
to get it past the classifier is forbidden, and so is any rewording whose only benefit is that the harness
stops recognising what is about to happen. Improvement review 21 proposed exactly that bypass and had to be
rejected (`IMP-0264`) — nothing mechanical caught it.

## Regression tests for hand-authored artefacts

*"Add a regression test for every P1 or P2 defect fixed, to prevent recurrence"* has been written down for a
long time, in a skill the Steps-and-Inline-Skills table never loaded at the step where it applies.
`IMP-0346`: defect D-02, a P2 in a hand-authored flow definition, was fixed with **no regression test at
all** — nothing under `src/tests/` referenced `Respond_error`, `Alert_on_failure`, `Compute_statistics` or
`Find_the_failed_action`. And the P1 the fix *introduced* then passed an 876-test suite, a clean packer and
a clean Solution Checker.

The packer, the hosted Solution Checker and `verify-flow-definition-language.py` all pass over a
semantically broken failure path — the gate says so in its own output — so until a source-level test exists
the fix is guarded by nothing.

## Closing a finding your fix answers

`IMP-0285` is the founding instance and `IMP-0640` the second: both times the fix was correct, verified, and
on disk, and both times a build died at the `improvement-log-check` step because the finding describing the
fixed defect had never been closed. Verifying only the gate the fix targeted is what makes this invisible:
the gate goes green, the queue stays red, and the cost is paid hours later by whoever dispatches the build.

## Gate baselines — grep for the sibling encodings

This repository routinely encodes one invariant more than once — a `scripts/verify-*.py` build gate and a
Pester assertion under `src/tests/` reading the same source files — and the encodings do not know about each
other.

`IMP-0638` → `IMP-0639` wired `scripts/verify-field-security-coverage.py` and stopped there.
`src/tests/provisioning/EnsureSchema.Tests.ps1` asserted *"every `IsSecured` column has exactly one
`FieldPermission`"* three more times over the same `Entity.xml`/`FieldSecurityProfiles.xml` pair, went red at
build step 68 of 73, and cost a second dispatch (`IMP-0641` → `IMP-0642`). One grep at `IMP-0639` time would
have found it — the sibling names the baselined column literally.

**No gate enforces this, and the reason is measured rather than assumed.** Keying a gate on each baseline
entry's `matches` token and grepping for other files that name it returns 2 findings across the 8 current
entries: 1 false positive (`verify-environment-access.ps1`, named by `verify-provisioning-report.py` and
`verify-pipeline-config.py` for unrelated reasons) and 1 true positive that is already fixed. Three of the
eight entries have a `matches` value that is not a source identifier at all (`status:error`,
`status-unproduced:threshold-unset`, `environments.prd.environment_prerequisites[0]`), so the grep cannot be
attempted for them. Whether two checks encode the same invariant is a semantic judgement — hence a checklist
step, not a script. Do not re-propose the token gate without re-measuring it (`IMP-0643`).

## Hours proposals — why they are made while the work is fresh

`IMP-0032`: six weeks into a time-and-materials engagement the WBS's `Actual Hours` column was empty on all
61 rows, because filling it depended on someone remembering at month end what happened weeks earlier.

## Hand-authoring — where the two-failed-guesses rule came from

Ground truth costs minutes; the alternative cost fifteen import attempts on the feature that produced that
section (`docs/development/revitalise-grant-automation-dev-deployment-handover.md`).

---

# More from `agents/improvement-agent.md`

Relocated by the generalisation initiative, Phase 1, 2026-09-08, extending the sections at the top of this
file (relocated by improvement review 7).

## The protection hook — what it binds and what it does not

**Since 2026-09-01 improvement-agent's exclusive write access is enforced, not merely declared.**
`.claude/hooks/protect-system-rules.py` is a `PreToolUse` hook that refuses `Edit`, `Write`, `MultiEdit` and
`NotebookEdit` against `agents/`, `constraints/`, `skills/` and `knowledge/` from any **dispatched** subagent
whose `agent_type` is not `improvement-agent`.

Two limits are deliberate, and a reader who does not know both will over-trust the control: it does **not**
bind the root session or the human — `agent_id` is absent for both, so `lead-agent` and the reviewer keep
write access to all four directories — and it does **not** cover `Bash`, so it is a refused route, not an
impossible write. Proven by live fixture, not read from documentation: a real `build-agent` dispatch was
refused on `agents/` and `constraints/` and a real `improvement-agent` dispatch was not
(`docs/improvements/2026-09-01-improvement-review-6.md` §4, `IMP-0556`).

## Why the safety-control prohibition is at the top of the file

Review 21 proposed a bypass and the only thing that stopped it was the reviewer reading the draft
(`IMP-0264`). This agent edits the rules every other agent obeys, which makes it the least supervised output
in the system.

## Capability mode — why it exists, and what it must re-measure

Every trigger except the capability one is defect-driven: findings in, rules out. A request to *add*
something the system has never had produces no finding, so until 2026-08-18 it had no trigger and no routing
row, and the only agent permitted to create `agents/`, `constraints/` and `skills/` files could not
legitimately act on it (`IMP-0027`).

**Why the brief's premises are re-measured, especially the negative ones.** "There is no pruning mechanism",
"no lint catches this", "no document covers this" are established by a search, not by a read, and a brief
declaring them verified is not a substitute for running one query each. Three of five such premises failed
re-measurement on 2026-09-01 (`IMP-0559`). The same finding is why a design document is grepped for first: a
parked or partly-applied design is invisible to the queue gate, so a brief saying none exists is not
evidence.

## The blocker trigger — unread, not the whole blocker population

A blocker already sitting in `awaiting-approval` has a document; it needs the keyword sent against that
document. One unread blocker must not pull a review of everything around it — that is how a one-finding
dispatch became a pass over twenty-three settled entries (`IMP-0183`).

## Step 2 — why exclusions are declared with `excluded_by`

The field exists so that obeying the no-silent-caps rule does not trip a citation-stamp warning per excluded
id (`IMP-0557`).

## Step 6 — why the premises of every finding are grepped at draft time

Step 8's grep clause is scoped to the review's OWN rationale, and the same failure arrives one position
upstream — inside the `proposed_change` and the stated instance counts of the findings being read. Those are
written mid-incident, by an agent with no obligation to grep the file it proposes to change, and nothing
between the finding and the applied change reads them: `verify-improvement-log.py` checks a
`proposed_change`'s TYPE and never its content (`IMP-0423`).

Three measured instances. `IMP-0632`: two of four findings in one batch carried a premise that failed
re-measurement — one proposed behaviour `run-with-timeout.sh` had had since it was written, one asserted a
fourth instance of a class that had three. `IMP-0660`: an approved change's wording filtered build steps by a
severity field the config does not carry, and had to be narrowed at apply time. Review 2 of 2026-09-08 then
found **three** more in one sitting — a skill needing rules it already stated, a proposed gate measuring 28
false positives in a 69-directory corpus, and a routed item already fixed.

**This belongs at step 6 and not at step 8 because every instance was caught at APPLY time, which is late** —
by then the wording is approved, and the only remaining moves are NARROW-AND-REPORT or withholding something
the reviewer has already said yes to.

## Step 8 — why a tracked file's current state is grepped

Same rule as the behavioural-assertion clause, cheaper instrument, and it is now the more common failure of
the two. Three instances, all inside three days, all in this agent's own output: a `proposed_change` naming a
`--warn-only` flag the target script's parser does not accept, written by analogy with its four neighbours
(`IMP-0570`); a review's rationale asserting the neighbouring build steps carry no `# History:` pointer when
55 of 76 steps do (`IMP-0571`); and `CLAUDE.md`'s supplied-assets table asserting `Designsystem/` has **0
tracked files** against a measured **131** (`IMP-0549`).

Note what makes this class persistent rather than careless. **In all three the false premise supported a
decision that was independently correct**, so nothing downstream broke and nothing would ever have surfaced
it — `IMP-0571`'s omitted pointer was fine for a different reason, and `IMP-0570` was caught only because
someone tried to run the command. A premise that is never exercised is never disproved. No gate reads a
finding's `proposed_change` or a review's rationale prose, and none reasonably could, so this clause is the
only thing standing between the two.

## Step 8 — why the disposition is simulated before parking

`classify()` recognises exactly four discharges, and a bare `revisit_when` is none of them: an entry with
`reviewed_in` and no `deferred_reason` classifies as `awaiting-approval`, and the blocker rung fires on
`unread` OR `awaiting-approval` alike (`IMP-0516`). Reading `classify()`'s source is exactly what produces
the confident wrong answer, because the precedence between `deferred_reason` and `awaiting-approval` is the
whole mechanism and it is four lines apart in one function. The question the simulation answers is the one no
amount of reading answers: **do the triggers this review exists to clear actually clear?**

## Retirement counts — why they are derived, never typed

Anchor on the struck-through id, not on the phrase: a naive `grep -c "status: retired"` returns one more than
the truth, because `domain-constraints.md`'s header sentence explains the convention without being a retired
row. The claim is registered in `scripts/derived-counts-registry.json`, which is how this instruction was
itself found wrong on 2026-08-24, having asserted zero retirements against ten (`IMP-0262`).

## Executables — the wiring obligation, and the gate that could not run

`scripts/verify-build-config.py`'s `suite-gate-is-not-a-step` check treats any unwired `verify-*.py` in
`scripts/` as a violation, and it is the *build* that discovers it — so the cost of forgetting is a halted
delivery dispatch hours later, paid by another agent. `IMP-0568` and `IMP-0569` are one gate that failed this
in both directions: authored, selftested, corpus-measured, derived-count-updated, and unrunnable.

The verify-script count drifted twice before anyone read the report, because the step is SOFT and its findings
were being counted into an aggregate (`IMP-0395`).

## The pipeline-config boundary — per operation, not per file

`IMP-0586`: eight expired `blocked_on` notes, four of them repository facts. This agent re-measured all four,
confirmed the causes still held, **wrote the measurement into the draft's own table** — and routed all eight
to the reviewer as `REVIEWER ACTION REQUIRED` anyway. The evidence and the conclusion were in the same
document and the conclusion was never drawn from the evidence. The reviewer's approval had to expand the
scope to say "re-date the four you already re-tested."

The tell is a section of your own draft that reports a measurement and then asks someone else to take it.

## `verify-derived-counts.py` — the drift that compliance itself creates

Regenerating the digest — the one step every review is REQUIRED to perform — mechanically drifts a registered
claim. The digest's line count is a function of the log's contents, and every review changes the log's
contents by moving entries to `APPLIED`. So the `CURRENT SIZE` sentence in
`scripts/generate-known-failure-modes.py` goes stale as a *consequence of compliance*, not as an authoring
mistake, and the review that created the drift is the one that must correct it.

Nothing else will. The step is **SOFT and wired `--warn-only`**, so it never blocks a build, and its findings
land in an aggregate `IMP-0395` already records people not reading — which is how three unrelated drifts
accumulated undetected in delivery documents while this gate reported them on every run. `IMP-0657` and
`IMP-0665` are the same mechanism logged twice, five days apart, by two different sessions.

**This is deliberately NOT proposed as a new gate.** The gate exists, is wired, and detects this correctly;
the gap was only ever that this agent's closing checklist never invoked it.

## Two field shapes that cost a validator round-trip each

`excluded_by` is a PATH field: the validator resolves it to a file on disk, so a path with an explanatory
clause appended fails as *"names '…', which does not exist"* (`IMP-0657`).

`reobserved` and `evidence_grep` were both first written as plain strings and the validator returned four
errors before the shape was recovered by reading its source (`IMP-0572`). The prose describing `reobserved`'s
*purpose* has three nouns that happen to map onto three of the five required keys, which is worse than saying
nothing: it reads complete. This is **not** proposed as a gate — the validator already enforces both correctly
and its messages are precise; the gap was discoverability at write time, and a defect that is self-correcting
within a session is exactly the one that never gets fixed, because every agent that meets it repairs its own
copy and leaves the instruction alone.

Any programmatic rewrite of `logs/improvement-log.jsonl` uses `json.dumps(..., ensure_ascii=False)`:
`evidence_grep` needles are matched as **raw bytes**, and the default escaping rewrites every non-ASCII
character as a six-character backslash-`u` escape — so an em-dash in the file stops matching an em-dash in the
needle, silently invalidating every needle that contains one (4 of 351 on 2026-09-08) and making the gate
report a false claim against a correctly applied entry (`IMP-0664`).

## Fail-closed gates — why corpus enumeration IS the design

Where a check rejects anything outside a declared set, every value you did not think of becomes a false
positive on day one — so enumerate the real corpus before choosing the set, not after (`IMP-0560`).
