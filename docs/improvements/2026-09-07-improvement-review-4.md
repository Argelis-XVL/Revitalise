# Improvement Review — 2026-09-07 (4)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 `NEW` → 2 clusters
**Trigger:** blocker escalation — [IMP-0650](../../logs/improvement-log.jsonl#L647) and [IMP-0651](../../logs/improvement-log.jsonl#L648), both `blocker`/`unread`, both halting [`improvement-log-check`](../../config/revitalise-grant-automation-build.yml#L62)
**WBS:** 3.2, 3.4
**Gate:** `APPROVE IMPROVEMENTS`

---

## 0. The one thing to read first

**The DocuSign connector id was fixed, and the identical unfixed guess is still sitting eleven lines below it in the same file, scheduled to be hit by the same maker action that exposed the first one.**

[A-DS-10](../../src/solutions/RevitaliseGrantAutomation/Other/Customizations.xml#L109) declares `shared_sharepointonline` and says so in its own words: *"connectorid is E3 evidence, the same class as rev_SharedDocuSign above … not yet ground-truthed against this tenant's own connector catalogue. Cheapest verification: pac connection list."* That is a verbatim description of [IMP-0650](../../logs/improvement-log.jsonl#L647)'s root cause, written before it happened, still open after it happened. And [pipeline.log#L162](../../logs/pipeline.log#L162)'s outstanding DEV checklist already schedules *"bind rev_SharedSharePoint"* — the same empty-picker action that cost the reviewer a maker-portal session on `rev_SharedDocuSign`.

**So [IMP-0650](../../logs/improvement-log.jsonl#L647)'s own `proposed_change` of `type: none` — "the corrective mechanism already exists" — is the one claim in it that does not survive.** The mechanism exists and did not run. It is prose, it is now at 58 instances, and its next failure is already identifiable by name.

**Neither finding gets a new gate, and §2 is the measurement that forced that** — the obvious candidate scores a false negative on `A-DS-10`, the very row it would exist to catch.

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [agents/development-agent.md#L387](../../agents/development-agent.md#L387) — *"run `verify-improvement-log.py --check` standalone, the queue, NOT the gate you fixed"* | 2026-08-24 (review 26), re-stated review 2 | `learning-substrate-destroyed` | **YES — [IMP-0651](../../logs/improvement-log.jsonl#L648)** | **See below: the recurrence is not a failure of this rule** |
| [`improvement-log-check`](../../config/revitalise-grant-automation-build.yml#L62) build step | 2026-08-25 | `learning-substrate-destroyed` | n/a — this IS the gate | **Working, and cheaply** — halted at step 3 of 73 in under two seconds ([build.log#L100](../../logs/build.log#L100)) |
| [C-TECH-050](../../constraints/technology/technology-constraints.md#L92) widening, [verify-pipeline-config.py](../../scripts/verify-pipeline-config.py#L631) check | **not applied** — review 3 is parked at its gate | `platform-import-ordering-defect` | n/a | Cannot be audited yet; §6 explains why that matters to this review |

**The recurrence needs stating carefully, because the obvious reading of it is wrong.** [agents/development-agent.md#L387](../../agents/development-agent.md#L387) tells a delivery agent to close a **prior** finding its fix answers. [IMP-0650](../../logs/improvement-log.jsonl#L647) is not a prior finding — development-agent appended it in the same session, correctly, under the mandatory blocker trigger. **It could not have closed it: only improvement-agent closes a blocker, behind this keyword.** So development-agent followed the rule and the build halted anyway.

**That makes [IMP-0651](../../logs/improvement-log.jsonl#L648) a report of the system working, not of a defect** — which is exactly what its own `why_it_was_never_caught` says: *"it WAS caught."* §4 proposes no rule for it, and §3 explains why proposing one would cost more than the thing it prevents.

**Classes recurring after a prose fix:** one, and analysed above as a non-failure. **Classes recurring after a gate:** none. No `gate-cannot-fail` finding is logged; logging one would be false.

**Closure-level audit.** [IMP-0650](../../logs/improvement-log.jsonl#L647) is `observable_at: V4` and [IMP-0651](../../logs/improvement-log.jsonl#L648) is `V1`. §7 states which this session can close and neither is proposed for closure on source state alone.

---

## 2. What was measured

### The mechanical candidate — measured and DROPPED

The tempting gate is: *an OPEN assumption row whose own stated verification is a command someone could run right now is overdue once an environment exists.* I ran it against the real corpus of OPEN rows in the [Unvalidated Assumptions Register](../../docs/development/revitalise-grant-automation-dev-summary.md#L6617).

| Measurement | Result |
|---|---|
| OPEN rows in the register | **28** |
| Of those, rows whose register line names a runnable `pac` command | **5** — `A-002`, `A-DS-1` (×2), `A-DS-2`, `A-DS-8` |
| Does `A-DS-10`'s register line name one? | **NO** |

**The candidate scores a FALSE NEGATIVE on `A-DS-10` — the single row this review exists to catch.** The reason is structural, not tunable: the runnable command lives in the [XML source comment](../../src/solutions/RevitaliseGrantAutomation/Other/Customizations.xml#L113), not in the register row the gate would read. A gate that misses the instance that motivated it is not narrowable into usefulness; it is the wrong instrument.

**This is this repository's five-times-measured prose-gate shape arriving from a sixth direction**, and the rule that follows the measurement — *assert on VALUES, not on PHRASES* — is what the routed item in §6 is built on instead: a dated connector catalogue is a set of values, and *"is this connectorid in it"* is an assertion. Producing that catalogue needs one credentialled `pac connection list`, which is why it is handed over rather than authored here.

### The behavioural assertion, executed rather than read

[IMP-0650](../../logs/improvement-log.jsonl#L647) claims [`verify-assumption-markers.py`](../../scripts/verify-assumption-markers.py) *"only checks that an OPEN row carries its A-nnn comment in source."* Per this agent's own step-8 rule I ran it rather than reading it:

```
ASSUMPTION MARKERS: PASS — 23 OPEN row(s) checked, every one carrying its marker in source;
58 row(s) total, 23 closed, 12 naming no target (a NOTE, not a failure), 0 unreadable, 0 exempt
```

**Confirmed, and sharper than the finding put it.** The gate is green **while naming `A-DS-10` as OPEN in its own output**, and `A-DS-10` falls in the weakest bucket — one of the 12 rows *"naming no target, so its source marker cannot be checked."* The gate verifies that a marker is **present**; nothing verifies that what the marker says is **true**. That distinction is the whole of this cluster.

### The class-name split

| Claim | Measured | Result |
|---|---|---|
| [IMP-0650](../../logs/improvement-log.jsonl#L647) is instance 58 of `platform-contract-guessed-not-groundtruthed` | 58 entries carry that `class_instance_of` | **Confirmed** — matches [the digest](../../logs/known-failure-modes.md#L32) |
| [IMP-0651](../../logs/improvement-log.jsonl#L648)'s class is an established one | `unread-blocker-halts-packaging` has **exactly 1 member** — itself | **DISPROVED — it is a brand-new singleton** |

**The dispatch brief told me this was "a recurrence of that same queue-processing-gap class" and directed me to find the established name. It is not a recurrence under any established name, because build-agent minted a new one.** The established class for this exact property is [`learning-substrate-destroyed`](../../logs/known-failure-modes.md#L38) at **x29**, and it already contains both `IMP-0285` and `IMP-0640` — the two prior findings that record *"fixing what a finding describes does not close it."* [IMP-0651](../../logs/improvement-log.jsonl#L648)'s own `root_cause` names `IMP-0285` as *"the same mechanism"* in prose while its `class_instance_of` says otherwise.

**Why this is worth a change rather than a shrug:** [the digest itself warns about precisely this](../../logs/known-failure-modes.md#L84) — *"a property recorded under two names produces a weaker signal than its true instance count ever should."* The altitude rule fires on instance counts. A 30th instance recorded as a 1st is an instance count that lies to the next reviewer.

---

## 3. The clusters, and the altitude calls

```
CLUSTER A: platform-contract-guessed-not-groundtruthed  (x58: IMP-0650, +57 earlier)
Altitude:   CLASS, already established — no new altitude is available at instance 58.
            The ladder's mechanical rung is BLOCKED, not skipped: validating a
            connectorid requires this tenant's own catalogue, and no repository
            fact substitutes for it (§2's measurement).
Ladder row: "A tool could catch it mechanically" — REACHABLE, but only once the
            catalogue exists. That input is a live-credentialled operation, so it
            is delivery work and is routed in §6, not authored here.
Becomes:    NOTHING in this review's own files. One routed item with a named,
            concrete next instance (A-DS-10) rather than a general exhortation.
Retires:    nothing — no instance gate exists for this class.
Cites:      IMP-0650
Residual:   A-DS-10 stays wrong until someone runs `pac connection list`. This
            review cannot close it and does not claim to. What it changes is that
            the next instance is now NAMED and DATED instead of latent — the
            difference between a known open row and a surprise in a maker portal.
```

```
CLUSTER B: learning-substrate-destroyed  (x30 once corrected: IMP-0651, +29 earlier)
Altitude:   NONE — deliberately. The gate that caught this is the mechanism, and
            it cost under two seconds at step 3 of 73. A routing rule to prevent
            a two-second failure costs more to carry than the failure costs to hit.
Ladder row: "One instance, specific to one feature, no general mechanism" ->
            "Nothing. It stays a log note." The one exception is bookkeeping:
            the entry is filed under a name that hides it from the count.
Becomes:    Change 1 only — the class_instance_of correction.
Retires:    the singleton class name `unread-blocker-halts-packaging`.
Cites:      IMP-0651
Residual:   Nothing prevents a future delivery agent minting another synonym for
            an established class. A gate over class names would be a fail-closed
            check against a 77-member singleton vocabulary, which per IMP-0560 is
            the shape that opens red on everything nobody thought of. Not proposed.
```

### Why no new constraint, and why no new gate

**Constraint budget: 0 of 3 used.** Cluster A's rule already exists as [`skills/how-to-verify-a-platform-contract.md`](../../skills/how-to-verify-a-platform-contract.md) §6's sweep; writing it again in a constraint row would be the same prose at a different address. Cluster B's rule already exists as [C-TECH-061](../../constraints/technology/technology-constraints.md#L131) and **fired correctly**.

---

## 4. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | other | [logs/improvement-log.jsonl#L648](../../logs/improvement-log.jsonl#L648) | Correct [IMP-0651](../../logs/improvement-log.jsonl#L648)'s `class_instance_of` from the singleton `unread-blocker-halts-packaging` to the established [`learning-substrate-destroyed`](../../logs/known-failure-modes.md#L38), taking that class from x29 to **x30**. Its `lesson` is retained verbatim — it is accurate; only its filing is wrong | IMP-0651 | YES — `python3 scripts/generate-known-failure-modes.py --check` after regeneration | N/A — log bookkeeping |

**One change. No constraints, no gates, no agent-file edits, no skill edits.**

That is the honest output of two findings that each proposed `type: none`, one of which was right and one of which was not — and the one that was wrong ([IMP-0650](../../logs/improvement-log.jsonl#L647)) is wrong in a way that produces a **routed item**, not a rule. Adding a rule at instance 58 of a class whose corrective mechanism is already written down, already read, and already unrun would be writing the same sentence a 59th time.

---

## 5. Retirements

> Retirement check performed: **85 live constraint rows and 10 retired** reviewed for redundancy against both clusters; **none currently redundant.** [C-TECH-061](../../constraints/technology/technology-constraints.md#L131) is the row governing cluster B and it fired exactly as written — a rule that just worked is the worst possible retirement candidate.

Counts derived, not typed: `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` → **10**; `grep -rh '^| C-' constraints/ --include='*.md' | wc -l` → **85**; `ls scripts/verify-*.py | wc -l` → **57**, unchanged because this review adds no gate, so [scripts/derived-counts-registry.json](../../scripts/derived-counts-registry.json) needs no edit and `verify-build-config.py`'s suite-gate rung has nothing new to find.

**The retirement here is a class name, not a rule** — `unread-blocker-halts-packaging`, retired by change 1 after one instance, before it can accumulate members that belong to a count of 30.

---

## 6. What is routed, and to whom

**One item, and I am reporting it rather than dispatching it.**

**Ground-truth `A-DS-10`'s connectorid, and produce a dated connector catalogue while the credential is open.** Owner: **development-agent** (source + register) with **pipeline-agent** or the reviewer to run the live command.

| What | Detail |
|---|---|
| The command | `pac connection list` against `REV-GrantApplications-DEV` — the same one that disproved `A-DS-1` |
| The row | [`A-DS-10`](../../src/solutions/RevitaliseGrantAutomation/Other/Customizations.xml#L109), `shared_sharepointonline`, at [Customizations.xml#L119](../../src/solutions/RevitaliseGrantAutomation/Other/Customizations.xml#L119) |
| Why now | [pipeline.log#L162](../../logs/pipeline.log#L162) already schedules *"bind rev_SharedSharePoint"* as an outstanding DEV checklist item. The next maker to attempt it meets `A-DS-1`'s empty picker if the guess is wrong |
| The durable half | Commit the catalogue as a dated artefact. Then *"every `<connectorid>` in solution source appears in the catalogue"* becomes an assertion on **values**, which §2 shows is the only form of this check that can work |
| Blocked on | A live credential. Per this agent's boundary rule, live-authenticating work is handed over, never authored here |

**This is the boundary table's live-environment row, not its repository-fact row.** The repository-fact half — *does another unclosed row of this class exist, and which* — is mine, and §0 and §2 are me having measured it rather than asking someone else to.

**Nothing else is routed.** [verify-derived-counts.py](../../scripts/verify-derived-counts.py) is SOFT and reports the same drifted claims review 3 measured and routed; they are live in-flight work, none caused by this review, and a finding restating a live gate's output is duplicate bookkeeping.

---

## 7. Findings left unprocessed

**Deferred:** IMP-0611, IMP-0612, IMP-0613, IMP-0614, IMP-0615, IMP-0617, IMP-0618, IMP-0620, IMP-0625, IMP-0626, IMP-0631, IMP-0632, IMP-0635, IMP-0636, IMP-0646, IMP-0648

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| `IMP-0611`, `IMP-0612`, `IMP-0613`, `IMP-0614`, `IMP-0615`, `IMP-0617`, `IMP-0618`, `IMP-0620`, `IMP-0625`, `IMP-0626`, `IMP-0631`, `IMP-0632` | various | **Already analysed** by [2026-09-06-improvement-review-3.md](2026-09-06-improvement-review-3.md), which never stamped `reviewed_in`. They need that document's keyword, **not a third analysis** | That document's gate is answered |
| `IMP-0635`, `IMP-0636`, `IMP-0646`, `IMP-0648` | `activation-rule-overridden-by-draft-reasoning`, `harness-blocks-destructive-call`, `figure-restated-not-cited`, `source-comment-overstates-log-evidence` | Genuinely unread, none `blocker`, neither cluster. **An unread blocker must not pull a review of everything around it** (`IMP-0183`) | The next batch review, or the batch trigger at 30 |

`IMP-0637`, `IMP-0647`, `IMP-0649` are **not** deferred by this review and are **not** re-derived: they are `awaiting-approval` at [2026-09-07-improvement-review-3.md](2026-09-07-improvement-review-3.md), whose scope this review does not touch. §9 explains why they nonetheless matter to the reviewer's sequencing.

Each deferred entry is stamped `excluded_by` naming this document, so this disclosure does not raise a citation warning per id.

### Closure levels — what this session can and cannot prove

**This session holds no credential for the DEV environment and no maker-portal access.**

| Entry | Proposed disposition | Why |
|---|---|---|
| [IMP-0650](../../logs/improvement-log.jsonl#L647) | **`deferred_reason` + `revisit_when`** — stays `NEW`, not closed | `observable_at: V4`. The corrected connectorid is **in source but undeployed** — [pipeline.log](../../logs/pipeline.log#L162) has no entry after 06:10, because the build that would have packaged it halted ([build.log#L100](../../logs/build.log#L100)). Closing it would claim a maker saw a populated picker. **Nobody has.** |
| [IMP-0651](../../logs/improvement-log.jsonl#L648) | **`deferred_reason` + `revisit_when`** — stays `NEW`, not closed | `observable_at: V1`, and its symptom **is** [IMP-0650](../../logs/improvement-log.jsonl#L647)'s queue state. It cannot be reobserved gone until this same keyword discharges IMP-0650. Change 1 lands regardless |

**Why a `deferred_reason` and not a bare `revisit_when`.** A bare `revisit_when` discharges nothing, and for a blocker it is a permanent red light — the rung fires on `unread` **and** `awaiting-approval` alike. A `deferred_reason` is the gate's own named second discharge. §9 is me confirming that by running it rather than reasoning about it.

---

## 8. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 648 | 648 — this review appends none |
| `learning-substrate-destroyed` | x29 | **x30** |
| `unread-blocker-halts-packaging` | x1 | **retired — 0** |
| `platform-contract-guessed-not-groundtruthed` | x58 | x58, unchanged |
| Distinct classes | 77 singletons | 76 |

Regenerated on approval with `python3 scripts/generate-known-failure-modes.py`, confirmed with `--check`. **The digest's value here is a count that stops lying:** the altitude rule fires on instance counts, and a 30th instance filed as a 1st is exactly the signal this system uses to decide when prose must become a gate.

---

## 9. Simulation of the disposition — run, not reasoned

Per `agents/improvement-agent.md`, I ran the queue gate against **scratch copies** of the log using the validator's own `--log` flag, so the real file was never written.

| Simulated state | Gate exit | Blockers remaining | What it showed |
|---|---|---|---|
| **A** — this draft parked, `reviewed_in` stamped, `status` still `NEW` | **1** | 3 `awaiting-approval` | Correct and expected: the rung fires on `awaiting-approval` too, and now names *this* document instead of reporting the entries unlooked-at |
| **B** — post-keyword, `deferred_reason` + `revisit_when` applied to both | **1** | **1** — `IMP-0649` only | **My two blockers clear.** `reviewer-deferred` goes 136 → **138**; `unread` goes 18 → **16** |

### What the simulation caught, and it changes what the reviewer should do

**Approving this review alone does not turn the build green.** Simulation B's residual failure is not mine:

```
TRIGGER: 1 NEW entry of severity 'blocker' in state 'awaiting-approval'
      IMP-0649 -> docs/improvements/2026-09-07-improvement-review-3.md
```

**[IMP-0649](../../logs/improvement-log.jsonl#L646) is parked at [review 3](2026-09-07-improvement-review-3.md)'s gate, and [`improvement-log-check`](../../config/revitalise-grant-automation-build.yml#L62) stays red until *both* keywords land.** I would have predicted otherwise from reading the classifier; running it is what showed me the two documents' gates are independent and jointly required. **The wbs:3.2 packaging dispatch that [IMP-0651](../../logs/improvement-log.jsonl#L648) records will halt at step 3 again if only one review is approved** — that is the single most actionable line in this document, and it is the reason §7 names review 3's entries rather than ignoring them as out of scope.

**The simulations wrote nothing.** Both ran via `--log` against scratch copies; the real log was never the target, and no scratch file was copied over it. The log's 648 entries and its JSON validity were re-confirmed after the step-6 stamps landed.

### One side effect of the stamps, measured rather than assumed

The `excluded_by` stamps did what [`IMP-0557`](../../logs/improvement-log.jsonl) added them for — **this document appears as a citer of none of the sixteen deferred entries**, so obeying the no-silent-caps rule raised no citation warning per id.

But comparing the validator against a pre-stamp backup shows the stamps also **changed the warning text on twelve entries**, from *"cited by 1 review document"* to *"cited by 2"*, newly naming [2026-09-07-improvement-review-2.md](2026-09-07-improvement-review-2.md) alongside [2026-09-06-improvement-review-3.md](2026-09-06-improvement-review-3.md). Same reviews directory both runs; only the log differed. **The second citer was always there** — review 2 does cite `IMP-0611` — so the warning got *more* accurate, not less.

**I am reporting this rather than passing over it because I did not predict it and cannot fully explain the scanner's precedence from one measurement.** It changes no exit code, touches neither blocker, and concerns only entries this review defers to other documents. It is a `WARNING`-severity display change on findings owned by two other parked reviews, and it is theirs to clear with their keywords.

**Real-log diff at draft time:** review 3's pre-existing stamps, the two uncommitted appends by development-agent and build-agent, and this review's own eighteen step-6 stamps — nothing else.

---

## 10. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-07-improvement-review-4.md

Findings processed: 2 NEW  →  2 clusters
Regression check:   3 prior changes audited, 1 class recurred (analysed as a
                    non-failure — the agent followed the rule; only improvement-agent
                    can close a blocker)
Proposed:           0 constraints (cap 3), 0 gates/scripts, 0 skill/knowledge edits,
                    0 agent-file edits, 1 log-bookkeeping correction, 1 class-name retirement
Altitude calls:     2 left as notes, 1 mechanical candidate measured and DROPPED
                    (false negative on the very row it would exist to catch),
                    1 class re-filed from a singleton to an x29 class
Digest:             will regenerate — learning-substrate-destroyed x29 -> x30

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 11. What the keyword changed

**Status: APPLIED — `APPROVE IMPROVEMENTS` received 2026-09-07 from the reviewer directly. Everything in §4 is on disk.**

| # | Change | Applied | Result |
|---|---|---|---|
| 1 | IMP-0651 `class_instance_of` → `learning-substrate-destroyed` | YES | `learning-substrate-destroyed` **x29 → x30**, re-measured on the applied log; `unread-blocker-halts-packaging` **retired to 0 members** |
| 2 | `deferred_reason` + `revisit_when` on IMP-0650 and IMP-0651 | YES | Both stay `status: NEW`, both now classify `reviewer-deferred`. `reviewer-deferred` 137 → **139**; `awaiting-approval` 6 → **4** |
| 3 | Digest regenerated | YES | `generate-known-failure-modes.py`, confirmed with `--check` |
| 4 | §6's routed item | **WITHHELD** | See below — superseded by reviewer ground truth, not dispatched |

**No entries are rejected.** Both findings are accurate records; [IMP-0650](../../logs/improvement-log.jsonl#L647)'s *self-assessment* that no change is needed is what §0 disagreed with, and the disagreement produced a routed item rather than a rejection.

### §6's routed item is WITHHELD, and §0's second premise is superseded

**Re-verifying the routed-work table at application time — the step-8 rule that a routed item is where staleness is most likely — disproved the premise it rested on.** §0 and §6 argued that [A-DS-10](../../src/solutions/RevitaliseGrantAutomation/Other/Customizations.xml#L109) (`rev_SharedSharePoint`, `shared_sharepointonline`) was *"the identical unfixed guess … eleven lines below"* the fixed DocuSign row, scheduled to fail the same way. **The reviewer has since confirmed that connection reference is correctly wired and working in DEV**, and a separate `development-agent` dispatch is closing `A-DS-10` in the assumption register on that evidence.

So `A-DS-10` is **ground-truthed CORRECT — not a recurrence of `platform-contract-guessed-not-groundtruthed`**. Per `IMP-0517`, a routed item that has become a closed reviewer decision is withheld and reported, never dispatched. The guess happened to be right; §2's measurement that the mechanical candidate scores a false negative on this very row stands unchanged, because that finding was about the *instrument*, not about whether this particular value was correct.

**What this does NOT change: either finding's disposition.** §7 proposed `deferred_reason` + `revisit_when` for both, and neither depended on `A-DS-10`. [IMP-0650](../../logs/improvement-log.jsonl#L647) stays open because its own V4 observation — a maker seeing a populated picker for `rev_SharedDocuSign` — has still not been made and the corrected value is still undeployed.

### One correction to §9's simulation, measured at application time

**§9 said approving this review alone would leave the build red on [IMP-0649](../../logs/improvement-log.jsonl#L646), parked at [review 3](2026-09-07-improvement-review-3.md)'s gate. That is no longer true: review 3 was approved and applied in the interval**, and `IMP-0649` now carries a `deferred_reason` and classifies `reviewer-deferred`. The log also grew 648 → **649** entries ([IMP-0652](../../logs/improvement-log.jsonl#L649), `rework`, appended by review 3's own application and parked at that document).

§9's reasoning was correct and its conclusion is simply spent. The applied result is the stronger one: `verify-improvement-log.py --check` now exits **0** with **zero** `TRIGGER` lines.
