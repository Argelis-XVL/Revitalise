# Improvement Review — 2026-09-20 (1)

**Status:** ~~AWAITING — nothing in section 3 has been applied.~~ **APPLIED 2026-09-20.** All six
changes landed, none narrowed, none withheld. The applied record is section 10, and it opens with
the authorisation — because this review's own subject is how an authorisation is recorded.

**Agent:** improvement-agent (tier `strategic`)
**Trigger:** two unread `blocker` entries — `IMP-0787` and `IMP-0791` — routed immediately
rather than batched, per [`agents/WORKFLOW.md`](../../agents/WORKFLOW.md) → Processing triggers.
**Scope:** those two entries only. Five other `unread` entries and 173 `reviewer-deferred`
entries were excluded by activation step 2 and are accounted for in section 6.
**Gate:** `APPROVE IMPROVEMENTS`.
**WBS:** this review proposes no delivery work. It touches the **commercial loop's authorisation
record**, which is the join between a contract line and an invoice, so its consequence is
commercial rather than contractual. No hour is billed or unbilled by it.

---

## 0. The measurement that decides this review

**Every commercial gate this project has ever cleared was cleared by a lead-agent relay — six of
six — and the ledger already records that fact as data.**

| Ledger entry | Act | Who authorised | Channel recorded |
|---|---|---|---|
| CE-0001 | change order CO-001-A2 approved | Xander Lykopoulos | `relayed_by: lead-agent` |
| CE-0002 | change order closed | Xander Lykopoulos | `relayed_by: direct` |
| CE-0003 | baseline imported | Xander Lykopoulos | `relayed_by: lead-agent` |
| CE-0004 | change order CO-003 approved | Anna Southern | `relayed_by: lead-agent` |
| CE-0005 | change order CO-004 approved | Anna Southern | `relayed_by: lead-agent` |
| CE-0006 | change order CO-005 approved | Anna Southern | `relayed_by: lead-agent` |

Read from [`logs/commercial-events.jsonl`](../../logs/commercial-events.jsonl). The matching
[`logs/pm.log`](../../logs/pm.log#L28) lines say the same thing in prose — *"exact gate keyword
`APPROVE CHANGE ORDER CO-003`, relayed by lead-agent"* — for CO-003, CO-004 and CO-005 on
2026-09-18, and for CO-001-A1 and CO-001-A2 in August.

So the refusal recorded as a critical finding on 2026-09-19 was not an agent applying a rule. It
was an agent improvising one, two days after the same role had accepted the same channel three
times in ten minutes and written the channel into the ledger each time. **Three greps confirm
nothing was being applied:** the commercial agent's own instruction file contains no rule about
what channel a keyword may arrive through (zero matches for *relay*, *verbatim*, *consent*, *gate
keyword* in [`agents/commercial-agent.md`](../../agents/commercial-agent.md)), the workflow file
contains none either (zero matches for *consent* outside the unrelated tenant-consent rows), and
the keyword table at [`agents/WORKFLOW.md#L507`](../../agents/WORKFLOW.md#L507) carves out no
commercial exception.

**An unwritten policy on a question every gate-guarding agent must answer produces a coin flip.**
That is the defect, and it is the whole defect.

### And it is not hypothetical that prose in a review document does not reach the next agent

The previous review recorded, in its own applied section, that it had itself been approved through
a relay and called that *"the weaker channel"*. One hour earlier, the same question had blocked a
change order. **The same question arrived twice in one evening and was answered two different
ways, in two documents, by two agents.** That is the argument for landing the answer where every
agent reads it rather than in a third review document.

---

## 1. The decision this review had to make, stated honestly

The finding proposes a rule telling the receiving agent to accept a lead-agent relay as approval.
**That proposal, in the form it was written, is the one change this system's promotion ladder never
makes** — [`skills/how-to-promote-a-finding.md`](../../skills/how-to-promote-a-finding.md) §4
forbids any promotion whose mechanism is that a safety control observes less than it did before,
and the previous review declined it on exactly that ground.

So the question is whether a narrower form exists that is not that. Three things persuade me it
does, and I am stating them so the reasoning can be attacked rather than trusted.

**1. The blanket refusal has no stopping point.** The reviewer's only channel to a dispatched agent
is through lead-agent. If a relay is never consent, then no keyword in the thirteen-row table at
[`agents/WORKFLOW.md#L507`](../../agents/WORKFLOW.md#L507) can ever clear, and the system has no
gates — it has thirteen permanent stops. A reading that makes every gate unreachable is not a
strict reading of the guard; it is a different rule that happens to look like it.

**2. The guard is about a different thing, and the platform's own words say so.** The warning
attached to an inbound agent message is that *an agent's own claim* of approval carries no user
authority. An agent announcing "I have decided this is approved" is the case it catches. A
transport carrying a human's exact words, naming the human, into a record the human will read, is
not that case — and treating them as identical is what produced the inconsistency in section 0.

**3. What makes a relay safe is not trust, it is the record.** Nothing inside a single turn can
authenticate a human. What *can* be done is make an unauthorised relay visible and cheap to
repudiate: the exact keyword, the named human, the channel, and the artefact the act produces, all
written down before the act, in a file the reviewer reads. That already happens six times out of
six — by convention, checked by nothing.

**So the change proposed below is a tightening, not a loosening.** Measured against today's state —
an unwritten policy under which six relays were accepted with no required record and a seventh was
refused — it adds four requirements a relay must meet, makes the record mandatory and
machine-checked, and leaves the case the guard exists for refused exactly as before.

---

## 2. Clusters

```
CLUSTER: hard-gate-has-no-scoped-override-path  (x6, this instance: IMP-0787)
Altitude:  CLASS — but a different class from the five earlier members. Those five (IMP-0638,
           0639, 0641, 0642, 0643) are all "a HARD check encodes a rule reality violates, with
           no scoped way to record the exception". This one is "a gate has no documented
           channel, so the channel is decided by whoever is asked first".
Ladder row: "An agent had the information and still did the wrong thing" → agent-file/skill edit,
           PLUS "a tool could catch it mechanically" for the record half.
Becomes:   agents/WORKFLOW.md (the channel rule, where every agent reads it)
           + agents/commercial-agent.md (a pointer, because this is where it was hit)
           + scripts/verify-commercial-events.py (the record becomes checkable)
           + C-COM-011 (the constraint row that gives the script its authority)
Retires:   nothing
Cites:     IMP-0787
Residual:  NOTHING AUTHENTICATES A HUMAN. This change makes an unauthorised relay recorded,
           reportable and repudiable; it does not make one impossible, and no rule in a
           single-channel harness can. Stated here rather than implied.

CLUSTER: concurrent-session-same-file-write  (x4, this instance: IMP-0791)
Altitude:  SPLIT — the class holds two mechanisms under one name. IMP-0539/0541/0547 are a race
           for a NAMED RESOURCE (a review filename), already mechanised by
           scripts/allocate-review-number.py. IMP-0791 is a duplicate DISPATCH against the same
           scope, which that script cannot see.
Ladder row: "An agent had the information and still did the wrong thing" — lead-agent has the
           tool that would have shown the sibling dispatch and no instruction to use it.
Becomes:   agents/lead-agent.md (one pre-dispatch check) + a retag so the class count is honest
Retires:   nothing
Cites:     IMP-0791
Residual:  The session-identity half — the same tool describing this process two different ways
           in one conversation — has an UNCONFIRMED cause and gets no rule. It is a platform
           observation for the reviewer, not a repository defect.
```

---

## 3. Proposed changes

### Change 1 — the channel rule, in `agents/WORKFLOW.md`

A new subsection under **Human Gate Keywords**, immediately after the table at
[`agents/WORKFLOW.md#L507`](../../agents/WORKFLOW.md#L507):

> ### What channel a keyword must arrive through
>
> **The reviewer's only channel to a dispatched agent is lead-agent.** A relay is therefore the
> system's normal resume path, not an anomaly, and an agent that refuses all relays has not
> applied a strict rule — it has made its own gate permanently unreachable. Six of six commercial
> acts on this project cleared this way (`logs/commercial-events.jsonl`), and a seventh was
> refused on the same evening the previous one was accepted (`IMP-0787`).
>
> **A relay is accepted only in this exact form.** Anything looser is refused:
>
> 1. it comes **from lead-agent**, not from any other agent;
> 2. it carries the **keyword verbatim, including its id** — `APPROVE CHANGE ORDER CO-006`, never
>    *"the reviewer approved the change order"*;
> 3. it **names the human** who sent it;
> 4. it states it is quoted from that session's own conversation turn.
>
> **Before the act, the receiving agent writes the record.** `authorised_by` (the named human),
> `relayed_by` (`lead-agent` or `direct`), the verbatim keyword, and the artefact the act
> produces. In the commercial loop that is `logs/commercial-events.jsonl` and `logs/pm.log`;
> elsewhere it is the agent's own gate output and log line. **The record is what makes a relay
> safe — not the relay's wording.** Nothing in a single-channel harness authenticates a human;
> what a record does is make an unauthorised relay visible in the next thing the reviewer reads,
> while the act is still revertible.
>
> **Four acts leave this repository, and each reports its record back before it completes** —
> `APPROVE TENANT`, `APPROVE PRD`, `ISSUE INVOICE <id>`, `CLIENT ACCEPTED <phase> <date>`. A
> tenant write, a production environment, a document reaching the Client's finance address, and a
> date that starts a warranty window and fixes a liability cap are not revertible by a commit. For
> these four the agent writes the record, states in one line what it is about to create and what
> that commits the practice to, and only then acts.
>
> **What stays refused, unchanged:** an agent asserting approval on its own authority, a
> paraphrase, a relay naming no human, a relay from any agent other than lead-agent. That is what
> the platform's permission warning exists for, and nothing here touches it.

### Change 2 — a pointer in `agents/commercial-agent.md`

A short section before **Gate output** ([`agents/commercial-agent.md#L115`](../../agents/commercial-agent.md#L115))
pointing at change 1, and recording that this agent's own gates have cleared by relay six times
with the channel written into the ledger each time — so a relay meeting the four conditions is
handled, and only a relay failing them is refused.

**Why both files.** The rule belongs in the workflow file because it binds every agent guarding a
keyword, and a pointer belongs in the commercial file because that is where an agent stands when
the question arrives. A rule in a file nobody reads at the moment of decision is a rule that
depends on remembering.

### Change 3 — make the record checkable: `scripts/verify-commercial-events.py`

Today `authorised_by` and `relayed_by` exist on every ledger row by convention and **nothing reads
them** — grepped across the whole repository, the token `relayed_by` appears in the ledger file
and nowhere else. The gate that already reads that file gains one check: every entry whose
`action` is an authorising one must carry a non-empty `authorised_by` and a `relayed_by` of
`lead-agent` or `direct`.

Edited in **both copies** (`scripts/` and `.engine/scripts/`), already wired as the
`commercial-events` step at
[`config/revitalise-grant-automation-build.yml#L140`](../../config/revitalise-grant-automation-build.yml#L140),
so no new wiring is needed. **Measured against the real corpus before wiring**, per the corpus rule
— the six existing rows and the selftest fixtures — with the finding count and true-positive count
recorded in the applied section.

### Change 4 — one constraint: `C-COM-011`

| Id | Rule | Severity | Scope | Verify By |
|---|---|---|---|---|
| C-COM-011 | Every authorising commercial act records the human who authorised it and the channel it arrived through, before the act. An entry with no named `authorised_by`, or no `relayed_by` of `lead-agent` or `direct`, is not an authorisation | HARD | commercial-agent, pm-agent, acceptance-agent | `scripts/verify-commercial-events.py` |

Cites `IMP-0787`. One of the cap of three.

### Change 5 — one pre-dispatch check, in `agents/lead-agent.md`

> Before dispatching an agent, check whether one of the same type is already live on the same
> feature and scope, and resume it rather than dispatch a second. Two independent dispatches
> wrote the same architecture document within one minute of each other on 2026-09-19; the
> surviving file was coherent, which is not evidence there was one writer (`IMP-0791`).

That file contains no such instruction today — grepped, zero matches for the tool that would show
it. The rule holds whatever caused the duplicate, which is why it is proposed while the cause is
unconfirmed.

### Change 6 — one retag

`IMP-0791`'s class moves from `concurrent-session-same-file-write` to
`duplicate-dispatch-unobserved`. The old class reads x4 and its digest row implies a general gate
is missing; three of its four members are a filename race that `allocate-review-number.py` already
defends. Merging a second mechanism under that name weakens the signal for both.

---

## 4. Regression check — did the last review's changes work?

Four changes were applied yesterday by improvement review 2026-09-19 (2).

| Change | Class | Recurred since? |
|---|---|---|
| Pipeline credential declaration at activation step 6 | `credential-not-on-the-machine-that-needs-it` (x5) | **No.** No entry in that class after `IMP-0781` |
| Dataverse securability section | `platform-contract-guessed-not-groundtruthed` (x59) | **No** in that class — but see below |
| `IMP-0784` retagged | `wrong-artefact-cited-as-evidence` (x9) | **No** |
| Derived-count correction after regeneration | `hand-maintained-count-drifts-from-source` (x39) | **No** |

**One adjacent recurrence, and it is worth naming.** Two entries appended after that review
(`unflagged-platform-contract`, now x2) are the neighbouring failure: a design document declaring
that a mechanism touches no unverified platform contract, when part of it does. Different class,
same evening, same document. Both are outside this review's scope and stay `unread`.

**And one recurrence that is this review's own subject.** The previous review's applied section
recorded its own approval as arriving through the weaker channel and left the question open for a
later review. It has now arrived twice. A prose note in a review document reached nobody, which is
the evidence that change 1 belongs in the workflow file rather than in a third review.

---

## 5. What is routed elsewhere, not fixed here

**The commercial ledger is three entries short, and its gate is red today.**
`python3 scripts/verify-commercial-events.py` fails right now: nine authorising acts in
`logs/pm.log` against six entries in the ledger. The three unrecorded ones are the August
`APPROVE BASELINE` and the CO-001 and CO-001-A1 approvals. `IMP-0312` recorded exactly this and is
marked `APPLIED`, while the defect it names is live — the backfill was correctly left as the
reviewer's decision, but the closure claims more than happened. **Routed to the reviewer as a
decision, and logged.** The step is wired `--warn-only`, so nothing is blocked by it.

**The session-identity anomaly has no repository remedy.** The tool that reports which agents are
live described this process two different ways within one conversation, and one agent reported
acting on a message lead-agent has no record of sending. Nothing in this repository can observe
harness topology. If it recurs, it is a Claude Code product report, not a finding.

---

## 6. Queue — what was excluded, and why

| State | Count | Disposition |
|---|---|---|
| `unread` | 7 | **2 processed** (`IMP-0787`, `IMP-0791`). **5 excluded**: `IMP-0785`, `IMP-0786`, `IMP-0789`, `IMP-0790`, `IMP-0792` — none is a blocker, and a single unread blocker must not pull a review of everything around it |
| `awaiting-approval` | 0 | — |
| `reviewer-deferred` | 173 | Each carries a reason a human accepted; left alone |
| `already-fixed` | 0 | — |

On approval the five excluded entries gain an `excluded_by` naming this review, so obeying the
no-silent-caps rule does not trip a citation warning on each of them. That field takes a bare
path and nothing else — the reason goes in a prose field beside it.

---

## 7. Retirement

**Checked, and none found.** The candidate search was the ten commercial rows in
[`constraints/commercial/commercial-constraints.md`](../../constraints/commercial/commercial-constraints.md#L34),
for a rule this review's change 1 or change 4 makes redundant. None is: C-COM-011 covers the
*record of who authorised an act*, which no existing row addresses — C-COM-001 covers the evidence
behind an hour, C-COM-005 covers a status claim, C-COM-010 covers an accepted gate violation.
Ten constraints are retired across the constraint set today and 85 are live, both derived rather
than typed.

---

## 8. Disposition of the two findings

**Neither entry can be closed by this review, and both stay open honestly.**

- **`IMP-0787`** was visible only when something ran, at V4. Its re-observation is a commercial
  agent accepting a relayed keyword under the new rule — which is the CO-006 dispatch that is
  waiting on this review. So the changes land, and the entry is parked with a `deferred_reason`
  recording that, and a `revisit_when` naming the next relayed commercial gate as the dispatch
  that supplies the observation and closes it.
- **`IMP-0791`** was visible at V2 and its root cause is unconfirmed. Changes 5 and 6 land; the
  entry is parked with a `deferred_reason` recording that the duplicate-dispatch half has a rule
  and the topology half has no repository remedy, and a `revisit_when` naming a recurrence.

A parked entry with a reason a human accepted is one of the four discharges the queue gate
recognises, so both triggers clear. **That will be simulated against a scratch copy of the log
before anything is parked**, per the simulate-before-you-park rule.

---

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-20-improvement-review.md

Findings processed: 2 unread (2 blocker)  →  2 clusters
Regression check:   4 prior changes audited, 0 classes recurred (1 adjacent class recurred;
                    1 recurrence is this review's own subject — section 4)
Proposed:           1 constraint (cap 3), 1 gate/script extension, 0 skill/knowledge edits,
                    3 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 1 class SPLIT (retag), 0 left as notes
Digest:             will regenerate — 2 lessons, 2 recurring classes affected

IMPROVEMENT LOG: 1 entry to append — id allocated at apply time  |  digest regenerated: on approval

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

**Level reached: V1.** Nothing here has been executed against a live environment. The corpus
measurement for change 3 runs at apply time and its numbers go in the applied section.

---

## 10. Applied — 2026-09-20

### The authorisation, recorded first

```
keyword:       APPROVE IMPROVEMENTS
authorised_by: Anna Southern (anna.southern@argelis.nl)
relayed_by:    lead-agent
form:          verbatim, quoted from her own turn in this session's conversation
```

**This review's changes were applied on the channel they describe, and the first relay of this
keyword was refused.** That relay carried the keyword verbatim from lead-agent and **named no
human**, which is condition 3 of the rule in change 1 — the load-bearing one, because a record
with no name in it is a record nobody can repudiate. It was refused, the missing element was
named, and the second relay supplied it. The refusal cost one round trip.

**That is not a footnote; it is the only live test this rule has had.** The rule was applied by an
agent that had just been asked to install it, on the authority of a relay under it, which is the
worst possible provenance — so the rule was run against itself first. It refused once and accepted
once, for the stated reason each time. What it did **not** do is refuse everything, which is the
failure mode the previous review's answer would have produced.

### What landed

| # | Target | Repository | Landed |
|---|---|---|---|
| 1 | `agents/WORKFLOW.md` | `.engine` | new subsection *What channel a keyword must arrive through*: the four conditions, the record obligation, the four acts that report back before completing, and what stays refused |
| 2 | `agents/commercial-agent.md` | `.engine` | a relay section before **Gate output**, pointing at change 1 and stating what it means at that desk |
| 3 | `agents/lead-agent.md` | `.engine` | one pre-dispatch check for a live sibling of the same type and scope |
| 4 | `scripts/verify-commercial-events.py` **and its `.engine` twin** | both | check 3: an authorising entry names its human and its channel. Byte-identical in both copies |
| 5 | `constraints/commercial/commercial-constraints.md` | instance | `C-COM-011`, HARD, cites `IMP-0787`, `Verify By` names check 3 and its two negative fixtures |
| 6 | `logs/improvement-log.jsonl` | instance | `IMP-0791` retagged to `duplicate-dispatch-unobserved`; both entries parked; five exclusions stamped; `IMP-0793` appended |
| 7 | `scripts/generate-known-failure-modes.py` **and its `.engine` twin** | both | the registered `CURRENT SIZE` claim corrected 725 → 728 after regeneration |

Change 7 is not in section 3. It is the drift that regenerating the digest mechanically creates —
the claim goes stale **as a consequence of compliance**, and the review that caused it is the one
that corrects it.

### Check 3 measured against the real corpus — 0 findings, and here is why 0 is correct

**The six real ledger rows all pass.** Reporting that as a clean run would be misleading, so the
number is explained instead: all six already carried `authorised_by` and `relayed_by`, because the
convention was followed six times out of six — **and read by nothing.** Grepped 2026-09-20, the
token `relayed_by` appeared in the ledger file and in no script anywhere in the repository.

**Proven by mutation, not by reading**, because "this gate checks nothing" is a behavioural
assertion and re-reading the source is what produces the confident wrong answer:

| Run | UNNAMED AUTHORISER | UNRECORDED CHANNEL |
|---|---|---|
| Both fields stripped from all six rows, **before** check 3 existed | 0 — the gate's output did not change at all | 0 |
| Both fields stripped from all six rows, **after** | **5** | **5** |
| The six rows as they actually are | 0 | 0 |

Five and not six is the designed under-firing edge: the sixth row's action is `CLOSED`, which
authorises nothing and is deliberately outside the checked set. The ledger was restored
byte-identically after each mutation, confirmed by comparison.

**So this is a regression guard on a convention, not a fix for a live defect.** Stated plainly
because a gate that finds nothing on the day it ships is the one most likely to be mistaken for
evidence that something was fixed.

Selftest: **12 fixtures, all green**, including two negative fixtures for check 3, one control
asserting a `CLOSED` entry produces no finding, and one asserting a malformed line is reported
once rather than twice.

### Nothing narrowed, nothing withheld

Every change in section 3 was applied in the form the reviewer was shown. **The re-verification
that could have forced a narrowing was run and changed nothing:** no entry was appended between
the draft and the keyword (the log held 789 entries at both moments, maximum id `IMP-0792`), and
nothing carries `corrects` against either processed finding.

### Both findings stay open, on purpose

- **`IMP-0787`** — parked with a `deferred_reason` recording that the fix landed and a
  `revisit_when` naming the next relayed commercial gate. It was visible only at V4, and its
  re-observation is a commercial agent accepting a relayed keyword under the new rule. **The
  CO-006 dispatch waiting on this review is that observation** — it closes the entry, this review
  cannot.
- **`IMP-0791`** — parked the same way. The duplicate-dispatch half has a rule; the
  session-topology half has an unconfirmed cause and no repository remedy. Re-verified before
  writing the deferral: the architecture document carries 0 conflict markers and
  `verify-design-doc-claims.py` reports OK, so nothing was corrupted in outcome.

**Simulated before parking**, on a scratch copy, because "do the triggers actually clear" is a
question no amount of reading answers: the gate returns `OK (schema + triggers)` with both blocker
triggers discharged. The scratch run also caught that the first version of the disposition script
reserialised all 789 rows rather than only the 7 it changed — corrected before it touched the real
file, which then differed by exactly the 15 lines expected.

### Verification run

```
python3 scripts/verify-commercial-events.py --selftest   → OK, 12 fixtures, all three checks
python3 scripts/verify-improvement-log.py --check        → OK, 790 entries, 0 blocker triggers
python3 scripts/generate-known-failure-modes.py --check  → current (790 entries)
python3 scripts/verify-class-defences.py                 → OK, 4 defences, 25 references
python3 scripts/verify-derived-counts.py                 → 2 drifted claims, NEITHER mine (below)
python3 scripts/verify-engine-instance-split.py          → OK, both twins byte-identical
python3 scripts/verify-build-config.py <build.yml>       → OK, the gate was already wired
python3 scripts/verify-review-document.py --only <this>  → OK
```

**Level reached: V1.** No script here authenticates to anything and nothing ran against a live
environment. The two instruction changes cannot be executed at all, and the rule they carry is
unproven until a commercial agent accepts a relay under it — which is precisely why `IMP-0787`
is parked rather than closed.

### Left alone, and named rather than fixed

`verify-derived-counts.py` reports one further drifted claim, at two lines of
`config/revitalise-grant-automation-pipeline.yml`: prose says *"the 18 rev_setting rows"* where
source says 21. **It predates this review and is not mine.** The file belongs to
`development-agent` and `pipeline-agent`, and correcting a count without knowing what the original
18 enumerated is the quiet substitution this agent is told not to make. Reported, not touched. The
step is SOFT and blocks nothing.

### Not committed

The working tree carries all of it and **nothing has been committed or pushed**, in either
repository. Changes 1, 2 and 3 and the `.engine` halves of 4 and 7 are in the submodule.
Publishing is the three-step order: `git -C .engine push origin HEAD:main`, verify with
`git -C .engine branch -r --contains HEAD` (a clean `git status` proves nothing here, and
`status -sb` prints `## HEAD (no branch)` whether or not the push succeeded), then commit and push
the pointer bump in the instance repository.
