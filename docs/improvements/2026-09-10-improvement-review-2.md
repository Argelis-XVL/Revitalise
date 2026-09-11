# Improvement Review — 2026-09-10 (2)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 21 `NEW` → 10 clusters
**Trigger:** the reviewer asked ("process improvements"), carrying a request to bring improvement-agent's own dispatch share down from an observed 30% to 10–15%
**Gate:** `APPROVE IMPROVEMENTS` — ~~not yet given; nothing in this document has been applied~~
**APPLIED 2026-09-11.** See §10.

---

## 0. The one thing to read first

**The dispatch-share problem is real and slightly worse than reported — but three of the four findings written about it blame the wrong causes, and the two biggest causes are named in none of them.**

The reviewer's figure was 90 of 299 dispatches (30%). Counted by exact dispatch target, it is **90 of 294 = 30.6%**, so the headline holds. What does not hold is the attribution. Every one of the four findings' cause figures was re-derived from [`logs/routing.log`](../../logs/routing.log) rather than taken from the findings' prose, and here is what the log actually says:

| Driver | The findings said | Measured | Note |
|---|---|---|---|
| Blocker trigger | 12 dispatches | **31 (34.4%)** | The largest driver. Understated nearly 3× |
| Relaying the approval keyword / applying a parked draft | not mentioned | **24 (26.7%)** | **Named by no finding.** Second-largest driver |
| Capability mode | not mentioned | 9 (10.0%) | |
| Batch trigger (the fixed ≥30 rule) | **28 — "the largest single driver"** | **8 (8.9%)** | Nearly the *smallest*. Overstated 3.5× |
| Revision / continuation of a live cycle | "roughly half" (≈45) | 7 (7.8%) | |
| Bookkeeping-only status moves | not mentioned | 7 (7.8%) | **Named by no finding** |
| Other | — | 4 (4.4%) | |

Two consequences follow, and they change what this review proposes.

**First, the change the reviewer's request most naturally points at cannot deliver the target.** Making the fixed ≥30 batch trigger adaptive addresses 8 of 90 dispatches — **2.7% of all dispatches**. Even eliminating that trigger entirely leaves the share above 28%. It is still worth doing, and it is proposed below, but proposing it *as the answer* to the 10–15% target would have been a measurement failure dressed as a fix.

**Second, the largest correctable driver is a dispatch that carries no analytical work at all.** 24 dispatches exist only to relay `APPROVE IMPROVEMENTS` to an agent whose draft is already parked, and 7 more only to move a status field so the build gate goes green. That is **31 of 90 improvement-agent dispatches — 34.4% of them, and 10.5% of every dispatch in the project** — spent on a full strategic-tier invocation that reads its own parked document back. Removing that class alone takes the share from **30.6% to 22.4%**, and the mechanism already exists in this repository's own rules: [`agents/WORKFLOW.md`](../../agents/WORKFLOW.md#L122) already establishes that resuming an agent you dispatched yourself is the default, and that the *only* mandatory reason for a fresh dispatch is a tier change — which for this agent can never arise, because it has no lower tier.

None of the four findings saw this, because each was written from a keyword count rather than a per-line classification. It is logged as `IMP-0720` and processed here.

**One further correction, and it is the cheapest change in this review.** The blocker trigger — the actual largest driver — reads differently in the two files that state it. [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L52) says *"Any **UNREAD** blocker-severity entry"*, and explains at length why the word matters. [`agents/WORKFLOW.md` line 405](../../agents/WORKFLOW.md#L405) — the file lead-agent actually reads when routing — says *"Any blocker-severity entry appended"*, with no such word. The narrowing was established after a measured incident and applied to only one of the two canonical copies.

---

## 1. Regression check — did the last review's changes work?

The previous review is [2026-09-10-improvement-review.md](2026-09-10-improvement-review.md), applied earlier the same day.

| Prior change | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|
| [`verify-improvement-log.py`](../../scripts/verify-improvement-log.py) three-way citation outcome | `engine-split-left-instance-gate-red` | NO | **Working.** No new instance in this batch |
| [`derive-wbs-state.py`](../../scripts/derive-wbs-state.py) comment stripping | `gate-cannot-fail` (evidence rules) | NO new instance of the comment shape | **Working** |
| [`verify-wbs-chain.py`](../../scripts/verify-wbs-chain.py) weak-rule warning | same | NO | Working — but see cluster F, which finds a *different* hole in the same script |
| [`architect-agent.md`](../../agents/architect-agent.md) author-new vs amend | `approved-document-internally-inconsistent` | **YES — x33** | **Recurred after a prose change.** Two new instances this batch (cluster B) |
| [`verify-derived-counts.py`](../../scripts/verify-derived-counts.py) wired SOFT | `hand-maintained-count-drifts-from-source` | **YES — x37** | **Fourth consecutive review recording this.** The gate is red right now |
| [`verify-engine-instance-split.py`](../../scripts/verify-engine-instance-split.py) (new, SOFT) | duplicate engine twins | NO | Working |

**Changes whose class recurred after a prose change:** `approved-document-internally-inconsistent`, at x33. The previous review added an author-new-versus-amend step to the architect agent file; this batch produced two more instances of the same class from a *different* direction — an ADR whose Decision and Consequences disagree with each other. The ladder says a recurrence after prose is evidence of wrong altitude. Cluster B takes that seriously and still declines to build a gate, for a reason it states.

**Changes whose class recurred after a gate:** `hand-maintained-count-drifts-from-source`. `verify-derived-counts.py` was **FAILED on one drifted claim** at draft time — the digest line-count prose said 676 where the source said 682. **Corrected at apply time**: two claims had drifted by then (the digest to 683, and the `verify-*.py` count to 60 because this review adds one), both fixed, and the gate now reports 10 of 10 matching. This is the drift the previous review predicted would recur as a *consequence of compliance*: regenerating the digest is mandatory for every review, and doing it dirties a registered claim. Correcting it is part of this review's own closing work, not a new proposal.

**Closure-evidence audit.** The previous review left five entries open rather than closing them on documents, and named a level and a reason for each. That is the behaviour `C-TECH-053` asks for, and none of the five has been closed since on weaker evidence.

---

## 2. Clusters and promotion decisions

Ten clusters account for all 21 findings.

```
CLUSTER: the learning loop's own processing-trigger budget
         (x5: IMP-0716, IMP-0717, IMP-0718, IMP-0719, IMP-0720)
Altitude:  CLASS, and ENGINE per skill §6 — "a review loop's trigger budget must be measured
           against delivery volume, not asserted" is true in any client's repo. Grepped the
           promoted text for this client's literals: none present
Ladder row: "the ORDER of steps was wrong" + "a tool could catch it mechanically"
Becomes:   agents/WORKFLOW.md (3 rows), a constraint AMENDMENT to C-TECH-061, the
           TRIGGER_BATCH constant, one new SOFT gate, one skill clause
Retires:   the hand-typed "thirty" in C-TECH-061's rule text — superseded by the script
           constant the row itself already declares authoritative
Cites:     IMP-0716, IMP-0717, IMP-0718, IMP-0719, IMP-0720
Residual:  The blocker trigger stays the largest driver (31 of 90) and MOST of it is
           legitimate. This review reduces the share; it does not claim to reach 10-15%,
           and §5 says what the remaining gap is made of.
```

**Every figure in this cluster was re-derived, and most of the findings' figures were wrong** — the table in §0 is the measurement. Four sub-decisions follow.

**(a) The blocker row loses a word it should never have lacked.** `WORKFLOW.md` will say *UNREAD*, matching the agent file that already does. This is the largest single lever available at zero risk: it does not weaken the trigger, it aligns it with the narrowing already argued and accepted elsewhere.

**(b) The scoped-fix exception is a documentation alignment, not a new rule.** The finding asked for a new named exception with three conditions. Measured: the exception **already exists**, in two places. [`verify-improvement-log.py` line 1245](../../scripts/verify-improvement-log.py#L1245) prints it as the gate's own remedy — *"or by recording an explicit `deferred_reason` on each entry"* — and `C-TECH-061`'s rule text names it as a discharge. What is missing is any mention of it in the trigger table lead-agent reads. So the change is narrowed from *invent an exception* to *state the existing one where the routing decision is taken*, and the three proposed conditions are replaced by the discharge the validator actually recognises.

The precedent claim is also narrowed: the finding cites two prior uses. **One is real** — `IMP-0698` carries a properly formed `deferred_reason` naming the reviewer, the date, the direct Pester verification and a `revisit_when`. **The other is not** — `IMP-0700` carries no `deferred_reason` at all, which is precisely why it is still in the unread queue and why the validator warns about it. One precedent, correctly formed, is enough to codify; two would have been better and only one exists.

**(c) The adaptive threshold is proposed, with its own effect stated honestly.** It touches three places, not one: the `WORKFLOW.md` row, `C-TECH-061`'s rule text, and `TRIGGER_BATCH` in the script — which the constraint row itself declares *"authoritative over this sentence"*. Changing only the prose would have produced two invocation paths disagreeing, a class at x13 here.

**(d) The pre-submission duplicate check is narrowed to a named exception to activation step 2.** The finding asked this agent to grep the log for already-applied findings before submitting. As written that instruction **contradicts** [activation step 2](../../agents/improvement-agent.md#L112), which forbids reading `APPLIED` entries — and that rule is exactly what produced the duplicate miss the finding cites, as the previous review's own §0 records. A general "grep everything" would be countermanded by the step above it. Narrowed to: a targeted read of `APPLIED` entries **sharing a cluster's own `class_instance_of`**, which is cheap, bounded, and the only subset that could contain a duplicate.

```
CLUSTER: an approved ADR that contradicts itself  (x2: IMP-0704, IMP-0710)
Altitude:  CLASS — both describe one ADR whose Decision names two controls and whose
           Consequences names one. x33 for the class overall
Ladder row: "an agent had the information and still did the wrong thing"
Becomes:   agents/architect-agent.md — an authoring discipline at the point of writing
Retires:   nothing
Cites:     IMP-0704, IMP-0710
Residual:  The instance is already FIXED (TAD rev 7 and rev 8). What is proposed guards the
           next ADR, and it is prose, knowingly, on a class that has recurred after prose.
           The reason a gate is refused is stated below and is a measurement, not a preference.
```

**The instance is closed and was closed before this review was dispatched.** Verified by grep: the totalising phrase *"the entire intervention"* appears nowhere in any architecture document; ADR-046 was corrected at rev 7, `ADR-046a` was added stating the convention for both payee types, and rev 8 records the reviewer confirming it.

**One of these two findings proposes the only constraint in the queue, and it is WITHHELD.** The proposal is a constraint requiring each intervention an ADR's Decision names to get its own row in the dev summary's component table. Its `Verify By` would have to count the interventions in a prose Decision paragraph — a phrase-reading instrument, which this repository has measured at 48–100% false **five** times and once shipped a gate that went red on the erratum written to satisfy it. Per the anti-bloat limits, a constraint whose `Verify By` is not mechanically executable is a comment. It is withheld and reported rather than written as a HARD row that cannot be checked.

What is applied instead is the other finding's cheaper and better-aimed proposal: number the Decision's interventions and trace them in the same order in Consequences, so a dropped one is visible as a gap in a sequence rather than as absent prose. That lands in the [`A default is specified by what the USER SEES`](../../agents/architect-agent.md#L137) section, which exists and is the right home.

```
CLUSTER: a task deriving complete without its human half
         (x3: IMP-0705, IMP-0708, IMP-0709)
Altitude:  CLASS for the mechanism; the instances are all already fixed
Ladder row: "a tool could catch it mechanically" — reached for one half, refused for the other
Becomes:   one stale-prose correction in contract/evidence-map.json. NO new gate
Retires:   nothing
Cites:     IMP-0705, IMP-0708, IMP-0709
Residual:  Nothing compares an evidence rule's REACHABLE verification level against the design
           document that constrains it. That gap is real and is left open deliberately, with a
           measurement saying why a gate for it would be a sixth phrase-reading instrument.
```

**All three instances are already fixed, two of them by work that landed hours before this review.** Verified by execution and by reading the state file, not by report:

- The `complete_states` split the third finding asked for a reviewer decision on **has been made and applied**. [`contract/delivery-parameters.json`](../../contract/delivery-parameters.json) now carries two lists — `complete_states_build_order` and `complete_states_money` — and six scripts read the correct one each: the queue and schedule scripts take build order, the invoice, hours and acceptance-pack scripts take money.
- Task 8.3 now derives **`partial`**, not `complete`. The `complete_pending_manual` state and the `manual` evidence-rule kind both already exist in [`derive-wbs-state.py`](../../scripts/derive-wbs-state.py#L129), so the first finding's premise that there is "no state between complete and partial" is stale.

**What is genuinely left is one line of wrong prose and one gap that stays open.** [`contract/evidence-map.json`](../../contract/evidence-map.json) still carries a note telling its reader that `complete_states` *"currently INCLUDES complete_pending_manual, so that state still clears successors and still counts as complete for invoicing"*. That was true when written and is false now, and it sits in the file a future PM dispatch reads first. Correcting it is the whole of this cluster's applied work.

**The gate is refused, and the finding that proposed it agrees.** The proposal is to widen the human-step check by grepping a feature's SDD and TAD for a sentence binding a task to a verification level, and the finding itself says *"measure the false-positive rate before wiring it HARD — this repository has rejected phrase-based instruments five times."* Measured. The repository's "recurring phrasing" occurs **once**, at one line in one architecture document, and two near-miss variants exist that the phrasing would not match. A gate whose corpus is a single sentence and whose near-misses already outnumber its hits is not a gate; it is a regex fitted to one example. Left open with a return condition in §5.

```
CLUSTER: an assumption id that does not denote its own claim
         (x2: IMP-0703 [blocker], IMP-0707 [blocker])
Altitude:  CLASS — x6. The instance is fixed; the gate hole is not
Ladder row: "a tool could catch it mechanically" + "second instance → generalise"
Becomes:   scripts/verify-assumption-markers.py — a second direction, NARROWED, reported as a
           WARNING, plus a widened register corpus
Retires:   nothing
Cites:     IMP-0703, IMP-0707
Residual:  A marker whose id resolves to a row about a DIFFERENT subject stays undetectable —
           no gate can tell one claim from another. Only the orphan half is mechanical.
```

**The instance is fixed** — a fresh id `A-FIN-08` was allocated in the register that actually governs the file, the row added, and the source comment re-cited. **The gate hole is confirmed by execution**: the script walks register→source for OPEN rows only, so a source marker citing a closed row is outside its search entirely. It reports PASS over this tree today.

**This is the review's one narrowing, and the measurement compelled it.** The proposal was: for every `A-nnn` appearing in `src/`, require a register row with that id **and require that row to be OPEN**; a marker resolving to a closed row is a FAIL. Measured against the real corpus — 47 distinct ids across 382 tracked files under `src/`:

| Outcome under the proposal as written | Ids | Adjudication |
|---|---|---|
| Resolves to an **OPEN** row — passes | 24 | correct |
| Resolves to a **CLOSED** row — **would FAIL** | 19 | **all 19 false positives** |
| Resolves to **no row found** — would FAIL | 4 | **1 true positive, 3 false** |

**23 of 47 ids — 49% of the corpus — would fail on day one, and the require-OPEN half is inverted.** A marker citing a closed row is not a defect; it is what every *successfully closed* assumption looks like, because this repository's convention retains the comment that recorded the guess. The proposal would have made correct closure the failure condition.

The three false positives among the no-row group are the useful part, because they say where registers actually live: one row is struck through (`A-FIN-01`), one is recorded as prose rather than a table row (`A-LAND-1`), and one lives in an **architecture** document (`A-RED-1`) while the script's `SCAN_GLOBS` reads `docs/development/*.md` only.

**One true positive, and it is a real defect: `A-REV-01`.** It is cited in a `rev_review` form XML and appears in **no register, in any document, anywhere** — zero hits across all of `docs/`. That is exactly the shape the finding was logged about, and it is invisible to every gate today.

So the narrowed form: add the source→register direction, reusing the script's existing closure and strikethrough handling, widen the register corpus to the architecture documents where registers demonstrably live, **drop the require-OPEN condition entirely**, and fail only on an id with no row in any register. **Predicted findings: 1, and it is the true positive.** The named false positives this narrowing removes are the 19 closed-row ids and the three off-corpus rows listed above. Reported as a WARNING first, because a fail-closed check over a 47-member corpus is the case where enumeration *is* the design.

`A-REV-01` itself is routed, not fixed here — it is a source and register edit owned by development-agent.

```
CLUSTER: a dispatch brief asserting an unverified fact  (x2: IMP-0706, IMP-0713)
Altitude:  CLASS at x4 for the brief half — already promoted, nothing new needed.
           INSTANCE-with-a-mechanism for the split-slug half
Ladder row: "a tool could catch it mechanically" for the slug; nothing for the brief
Becomes:   scripts/verify-system-consistency.py — one slug per feature, as a WARNING
Retires:   nothing
Cites:     IMP-0706, IMP-0713
Residual:  Nothing can verify a brief's arithmetic before an agent acts on it — a brief exists
           only inside a live session and no gate can read one. That half stays prose, and it
           is already prose in three agent files.
```

One of the two proposes nothing and says so, correctly: it is the fourth instance of an already-tracked class, logged for recurrence tracking.

The other's premise is confirmed and its proposal is the good kind — it asserts on **values**, not phrases. The slug is genuinely split: [`docs/plans/revitalise-payment-capture-plan.md`](../../docs/plans/revitalise-payment-capture-plan.md) and a matching dev summary exist under one slug, while the TAD, build config, artifact and pipeline config sit under another, and `config/revitalise-payment-capture*` **does not exist at all**. [`verify-system-consistency.py`](../../scripts/verify-system-consistency.py) exists and contains **zero** occurrences of "slug". A file-existence check is mechanical, has no polarity risk, and catches the case that sent a dispatch to a 5,000-line document silent about the feature it was asked to read.

```
CLUSTER: a detector whose result cannot reach a reader  (x2: IMP-0714, IMP-0715)
Altitude:  CLASS — "the gate computed the right answer and rendered it nowhere" is one property
Ladder row: "a tool could catch it mechanically"
Becomes:   scripts/import-baseline.py (discover the source by version, not by filename) and
           scripts/verify-wbs-chain.py (report an exception that matched nothing)
Retires:   nothing
Cites:     IMP-0714, IMP-0715
Residual:  An INERT exception still needs a human to decide whether its cause is fixed. The gate
           can only say "this waiver suppressed nothing this run", never "close it".
```

**The instance half of the first finding is fixed and the general half is not — established by running the script, not by reading it.** The pin was bumped to v0.6 and the unreachable ternary in the drift report was repaired. But `python3 scripts/import-baseline.py --check` **exits 0** today with `WBS_SRC` still a hardcoded filename at line 58, and the file carries a comment describing the glob-and-fail fix as *proposed*. So the defect the finding is actually about — a staleness gate that cannot detect the one event it exists for, a newer accepted source arriving — is live and will recur verbatim on v0.7. This is the half worth building, and it asserts on a version ordering, not on prose.

The second finding's premise is confirmed by grep: `verify-wbs-chain.py` contains **zero** occurrences of "inert". An exception whose `matches` string matched nothing is indistinguishable in the output from one holding a real violation down, and the wrong reading — a quiet gate means the waiver is working — is the natural one.

```
CLUSTER: a serialisation default that invalidates evidence needles  (x1: IMP-0699)
Altitude:  INSTANCE — the rule is already written; one code path lacks it
Ladder row: "a tool could catch it mechanically" — already reached, in the wrong file
Becomes:   one line in .engine/scripts/kb.py
Retires:   nothing
Cites:     IMP-0699
Residual:  Nothing prevents the next one-off script from omitting the argument. The rule is in
           the skill every agent loads at the moment of writing, which is the available altitude.
```

**Most of this finding's proposal is already done, and the tell was the one step 6 warns about** — a proposal phrased as *"add a rule that X"* where X is hygiene the target already carries. [`skills/how-to-log-an-improvement.md` line 354](../../skills/how-to-log-an-improvement.md#L354) already says, in the exact file the finding names: *"If you append or rewrite this file with a SCRIPT, pass `ensure_ascii=False`."*

**The cross-check half is true, and the finding named the wrong file.** There is no `json.dumps` anywhere in `scripts/kb.py`, which is a 2.3 kB wrapper. The engine copy's `add_failure_mode` serialises at `json.dumps(entry, sort_keys=True)` with no `ensure_ascii=False` — a genuine latent instance of the same bug, waiting for the first failure mode whose text contains an em-dash. One line, one file.

```
CLUSTER: an SDD open question nothing reads  (x1: IMP-0711)
Altitude:  CLASS by class count (x31) but INSTANCE by evidence — one occurrence, and the
           finding's own second half is what makes the first half real
Ladder row: "a tool could catch it mechanically"
Becomes:   agents/plan-agent.md (date against an EVENT) + scripts/verify-open-questions.py
           (new, SOFT) + one stale row corrected
Retires:   nothing
Cites:     IMP-0711
Residual:  Whether a due EVENT has occurred is derivable for a deploy or a privilege grant and
           NOT for "the business decided". The gate reports the first kind and cannot see the
           second.
```

Both premises confirmed. `scripts/verify-open-questions.py` does not exist, and the open question in question still reads **"Before build"** in its plan row today — while the TAD records its architectural half as resolved in full at rev 7 and reviewer-confirmed at rev 8. So the row is both undated against any real event *and* now stale about its own state.

**The finding is right that its two halves are not separable**, and says so in its own words: without the gate, dating questions against events is *"another declared policy nothing enforces, which is this finding's own class."* Both are proposed together, the gate SOFT, with its corpus measured before wiring.

```
CLUSTER: two parallel dispatches racing one gate's verdict  (x1: IMP-0712)
Altitude:  INSTANCE with a general cause — one occurrence, no mechanical home exists
Ladder row: "an agent had the information and still did the wrong thing"
Becomes:   agents/lead-agent.md — one clause in the dispatch-parameters rungs
Retires:   nothing
Cites:     IMP-0712
Residual:  NO GATE IS POSSIBLE and this is not a deferral. A dispatch prompt exists only inside
           a live session; nothing in this repository can read one. Stated so the next review
           does not propose one.
```

Confirmed: [`agents/lead-agent.md`](../../agents/lead-agent.md) contains exactly **one** occurrence of "parallel", in a history pointer, and no guidance on shared gate scope between concurrent dispatches. The cost here was zero because the dispatcher independently re-ran the gate — but the recorded `BLOCKED` verdict was already false when it was read, and asking the reviewer to act on it would have been the failure.

```
CLUSTER: no change needed — the system worked  (x2: IMP-0700, IMP-0702)
Altitude:  none reached. The ladder is for findings that still need a home
Becomes:   NOTHING. Both close
Retires:   nothing
Cites:     IMP-0700, IMP-0702
Residual:  IMP-0700 must close by being PROCESSED, not by a deferred_reason — the validator's
           own warning says so, and an agent writing its own deferral to clear its own build is
           the gate-cannot-fail class wearing a helpful face.
```

Both are `type: none` by their authors' own judgement, and both judgements hold. The untriaged-advisory finding was fixed by the next dispatch and carries a `corrects` link. The stale-digest finding records a gate catching exactly what it exists to catch, on the very next build, and asks for nothing.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | agent | `agents/WORKFLOW.md` | Blocker trigger row: add **UNREAD**, matching `agents/improvement-agent.md`'s row and the narrowing already argued there | IMP-0717, IMP-0720 | YES — `grep -c 'UNREAD' agents/WORKFLOW.md` | N/A |
| 2 | agent | `agents/WORKFLOW.md` | Blocker trigger row: state the **existing** `deferred_reason` discharge as the scoped-fix path, naming what a well-formed one carries. Not a new exception — the validator and `C-TECH-061` already have it | IMP-0717 | YES — the validator already enforces the discharge | N/A |
| 3 | constraint-amendment | `C-TECH-061`, **and in the same change** `TRIGGER_BATCH` in `scripts/verify-improvement-log.py` plus the `WORKFLOW.md` batch row | Replace the flat count with `max(floor, 20% of dispatches since the last improvement-agent dispatch)`; floor raised to 45. **All three places in one change** — the constraint row already declares the script authoritative, so amending the prose alone would leave two invocation paths disagreeing | IMP-0716 | YES — `python3 scripts/verify-improvement-log.py --check` | already wired — `improvement-log-check` |
| 4 | agent | `agents/WORKFLOW.md` + `agents/lead-agent.md` | **A keyword relay is a resume, not a dispatch.** `APPROVE IMPROVEMENTS` against a parked draft goes to the live agent via `SendMessage`; a fresh dispatch only where the transcript is gone. Addresses 31 of 90 dispatches | IMP-0718, IMP-0720 | NO — `SendMessage` leaves no repository trace, stated as a known limit | N/A |
| 5 | script | `scripts/report-dispatch-share.py` (new) | Report improvement-agent's rolling dispatch share **and its composition** from `logs/routing.log`, reusing `verify-routing-reconciliation.py`'s existing parser. Flag >15%. The composition is what made this diagnosable; the bare share would not have been | IMP-0719, IMP-0718 | YES — `--selftest` plus the real corpus | **SOFT (`--warn-only`)**, wired in the same change |
| 6 | skill | `skills/how-to-promote-a-finding.md` | Pre-submission duplicate check, **narrowed** to a named exception to activation step 2: read `APPLIED` entries sharing a cluster's own `class_instance_of`, not the log at large | IMP-0718 | N/A — instruction change | N/A |
| 7 | agent | `agents/architect-agent.md` | Number the Decision's interventions; trace them in the same order in Consequences. Any sentence fixing a COUNT of controls is reconciled against the Decision's list in the same dispatch | IMP-0710 | N/A — instruction change | N/A |
| 8 | other | `contract/evidence-map.json` | Correct the note claiming `complete_states` still includes `complete_pending_manual` — the split landed and six scripts read the two new lists | IMP-0708 | YES — `grep -c 'complete_states currently INCLUDES'` returns 0 | N/A |
| 9 | script | `scripts/verify-assumption-markers.py` + engine twin | Source→register direction, **narrowed**: fail only on an id with no row in any register; require-OPEN dropped; `SCAN_GLOBS` widened to the architecture documents. Reported as WARNING | IMP-0703, IMP-0707 | YES — `--selftest` plus the real corpus (1 predicted finding) | already wired — `assumption-markers` |
| 10 | script | `scripts/verify-system-consistency.py` + engine twin | One slug per feature: plan, architecture, dev summary, build config and pipeline config resolve to the same slug; report a split naming both. WARNING | IMP-0706 | YES — file existence, not prose | already wired |
| 11 | script | `scripts/import-baseline.py` | Discover the WBS source by glob over `docs/Import/*WBS*v?.?*.xlsx` and take the highest version; `--check` exits non-zero when the newest present version is not the pinned one | IMP-0714 | YES — run `--check` against a planted higher version | already wired — PM gates |
| 12 | script | `scripts/verify-wbs-chain.py` + engine twin | Report every exception in `contract/known-exceptions.json` whose `matches` string matched nothing this run as **INERT**, with id, owner and expiry | IMP-0715 | YES — run it; the corpus contains a known inert exception | already wired — PM gates |
| 13 | script | `.engine/scripts/kb.py` | `add_failure_mode`: `json.dumps(entry, sort_keys=True, ensure_ascii=False)` | IMP-0699 | YES — round-trip a non-ASCII entry and grep the raw bytes | already wired |
| 14 | agent | `agents/plan-agent.md` | Date every SDD open question against a named **EVENT** that makes its answer load-bearing — a deploy, a privilege grant, a first live run — never "before build" | IMP-0711 | N/A — instruction change | N/A |
| 15 | script | `scripts/verify-open-questions.py` (new) | Fail when an open question whose due **event** has occurred carries no answer and no dated re-scope. Corpus measured before wiring | IMP-0711 | YES — `--selftest` plus the real corpus | **SOFT** first, wired in the same change |
| 16 | other | `docs/plans/revitalise-payment-capture-plan.md` | Re-date OQ-151 against its real event and record that its architectural half is closed by `ADR-046a` | IMP-0711 | YES — `grep -c 'Before build'` on that row returns 0 | N/A |
| 17 | other | `scripts/generate-known-failure-modes.py` | Correct the registered digest-size claim that this review's own mandatory regeneration drifts | IMP-0716 *(housekeeping — the regression check's own finding)* | YES — `python3 scripts/verify-derived-counts.py` | already wired — SOFT |

**Constraint budget: 0 of 3 new constraints used.** Row 3 is an *amendment* to an existing row, not a new one, and the only constraint-type proposal in the queue is withheld — see §4. The constraint set stands at **85 live** rows and **10 retired**, derived at draft time.

**Row 4 is the change that moves the reviewer's number, and it is the one with no mechanical half.** That is stated plainly rather than dressed up: `SendMessage` calls leave no repository trace, so no gate can observe whether a relay was a resume or a dispatch. Row 5 is what makes the effect *visible* even though it cannot make it enforceable — the share and its composition will show whether row 4 is being followed.

---

## 4. Retirements and withholdings

> **Retirement check performed.** 85 live constraint rows reviewed at class level against these ten clusters. One candidate found and named below; the rest are not redundant, because every other proposed change extends a gate that already exists rather than replacing a rule.

**Retirement candidate — the hand-typed threshold in `C-TECH-061`.** The row's own text carries the word *"thirty"* while also declaring that `TRIGGER_BATCH` in the script *"is authoritative over this sentence"*. That is a hand-maintained number duplicating a source of truth, in the class this project has now recurred **37** times. Row 3 strikes the number from the rule text and cites the constant instead. The row itself is not retired — its rule is live and load-bearing; the duplicated figure inside it is.

**Withheld — the only new constraint proposed in this queue.** The requirement that each intervention named in an ADR's Decision get its own dev-summary component row cannot be given a mechanically executable `Verify By`: counting interventions in a prose paragraph is a phrase-reading instrument, measured 48–100% false five times here, once shipping a gate that reddened on the erratum written to satisfy it. Per the anti-bloat limits it would be a comment wearing a HARD constraint's clothes. Withheld and reported; the authoring discipline in row 7 is the altitude that is actually available.

**Withheld — the SDD/TAD verification-level grep.** Measured: the repository's supposed recurring phrasing occurs **once**, and two near-miss variants already exist that it would not match. Left open with a return condition in §5 rather than shipped as a sixth phrase-based instrument. The finding that proposed it asked for exactly this measurement first.

---

## 5. Findings left unprocessed, and what the remaining dispatch share is made of

**Deferred: none.** All 20 unread entries were processed, plus the one this review logged itself (`IMP-0720`).

**Two states were excluded from scope**, per activation step 2:

| State | Count | Why excluded | Where they are parked |
|---|---|---|---|
| `awaiting-approval` | 4 | A review already processed them and is parked at its own gate. The remedy is the keyword against **that** document, not a second review | IMP-0608 → [2026-09-05 review (2)](2026-09-05-improvement-review-2.md); IMP-0644, IMP-0645 → [2026-09-07 review (2)](2026-09-07-improvement-review-2.md); IMP-0652 → [2026-09-07 review (3)](2026-09-07-improvement-review-3.md) |
| `reviewer-deferred` | 149 | Each carries a reason a human accepted | On their own entries |

**Two blocker entries stay red until this review's keyword arrives.** `IMP-0703` and `IMP-0707` are processed here and now read `awaiting-approval`; the blocker rung fires on that state as well as on `unread`, by design. The log therefore stays FAILED until the keyword closes them — that is the parked-review state working as documented, not a new defect.

### The honest arithmetic on the 10–15% target

The reviewer asked for 10–15%. This review does not claim to deliver it, and here is the gap:

| | Dispatches | Share of 294 |
|---|---|---|
| Observed today | 90 | **30.6%** |
| Less the relay and bookkeeping class (row 4) | 59 | **22.4%** |
| Less the batch trigger entirely (row 3 reduces, not eliminates) | 51 | **19.5%** |
| Remaining: 31 blocker + 9 capability + 7 revision + 4 other | 51 | — |

**Reaching 10–15% requires a decision this review cannot take on its own: whether the blocker trigger should batch.** 31 of 90 dispatches are blocker-immediate, and that rule exists because a fifteen-attempt failure should not wait for a quorum. Rows 1 and 2 shave the illegitimate part of it — entries that were never unread, and entries a scoped fix already closed. What remains is the rule doing its job. Putting that to the reviewer is §6's question.

---

## 6. What you need to decide

**Should the blocker-immediate trigger be allowed to batch, and if so under what bound?**

**Problem** — 31 of 90 improvement-agent dispatches are blocker-immediate, and after rows 1–4 that is the entire remaining gap between 19.5% and the 10–15% target.
**Suggested fix** — leave it immediate for now; row 5 makes the share and its composition visible monthly, and revisit with three months of data rather than changing a safety trigger on one measurement.
**What happens if you don't** — the share settles near 19.5% rather than 15%. Nothing breaks; the target is simply not met, and the reason is a rule you may well want to keep.
[`agents/WORKFLOW.md` line 405](../../agents/WORKFLOW.md#L405)

---

**Should `A-REV-01` be routed to development-agent now, or wait for the next feature dispatch?**

**Problem** — a form XML cites an assumption id that exists in no register in any document; it is the one true positive the narrowed marker gate would report.
**Suggested fix** — route it with the next `rev_review` dispatch; it is a source comment and a register row, not a build defect.
**What happens if you don't** — the gate in row 9 opens with one finding against work no dispatch owns, which is the shape that teaches people to ignore a gate.
[`src/solutions/RevitaliseGrantAutomation/Entities/rev_review/FormXml/main/{d3000000-0000-4000-8000-00000000ad01}.xml`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_review/FormXml/main/{d3000000-0000-4000-8000-00000000ad01}.xml)

---

## 7. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 716 | 717 |
| Distinct lessons | 710 | 711 |
| Recurring classes (x≥2) | 53 | 54 |

To be regenerated with `python3 scripts/generate-known-failure-modes.py` at apply time and confirmed with `--check`. Regenerating drifts a registered size claim, so `python3 scripts/verify-derived-counts.py` runs in the same change — it is **already red** on that claim today, which row 17 corrects.

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-10-improvement-review-2.md

Findings processed: 21 NEW  →  10 clusters
Regression check:   6 prior changes audited, 2 classes recurred
Proposed:           0 constraints (cap 3), 7 gates/scripts, 1 skill/knowledge edits,
                    5 agent-file edits, 1 retirements
                    plus 1 constraint amendment and 3 'other' rows (a contract note, a plan
                    row, a registered count) — 17 change-table rows in total
Altitude calls:     4 generalised from instance to class, 3 left as notes, 2 gates refused
                    on measured false-positive grounds
Narrowed:           3 proposals — marker gate (49% false as written), scoped-fix exception
                    (already exists), duplicate check (contradicted activation step 2)
Withheld:           2 — the only new constraint, and the SDD/TAD phrase grep
Digest:             will regenerate — 711 lessons, 54 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

**Nothing above has been applied.** The only writes this review has made are the mandatory `reviewed_in` stamps on the 21 entries it processes — which is what makes them read as `awaiting-approval` rather than as unlooked-at while this document waits — plus the digest regeneration the capture contract requires for the entry this review logged itself. Verified: `git status` over `agents/`, `constraints/`, `skills/`, `scripts/` and `config/` shows **no rule file touched**.

---

## 9. Verification actually executed at draft time

| What | Result |
|---|---|
| Queue state | 717 entries; **0 unread**, 25 awaiting-approval, 149 reviewer-deferred |
| Digest | regenerated and `--check` **current** (717 entries, 711 lesson groups) |
| Review-document gate | **clean against this document** (0 findings); 5 findings stand against four August documents, pre-existing and untouched |
| Dispatch-share corpus | 294 dispatches classified one line at a time into 7 mutually exclusive categories |
| Marker-gate corpus | 47 distinct ids across 382 tracked files under `src/`; each of the 23 would-be failures adjudicated individually |
| Phrase-instrument corpus | 1 hit, 2 unmatched near-miss variants — the measurement that refused the gate |
| `import-baseline.py --check` | **executed**, exit 0 with a hardcoded source filename — the behavioural assertion, not a read |
| `verify-assumption-markers.py` | **executed**, PASS over this tree, confirming the hole |
| Disposition simulation | ran against a scratch copy; **both triggers clear** (0 unread, 0 blocker, 0 batch). Real file restored and confirmed **byte-identical** |
| `verify-derived-counts.py` | **FAILED — 1 drifted claim** (digest line count 676 vs 682). Row 17 |
| `verify-build-config.py` | **exit 1 — already red**, on `report-baseline-drift.py` as an unwired suite gate. Pre-existing, not caused by this review — see below |

**Not verified:** nothing was run against a live environment, and no V3/V4 observation was made — hence the three entries that will stay open. No proposed change has been executed, because none has been applied.

### Two things the reviewer should know before the next build

**The build-config preflight is red right now, independently of this review.** `python3 scripts/verify-build-config.py` exits **1** on `report-baseline-drift.py` being an unwired suite gate. This review did not cause it and does not fix it — it is in the class the preflight exists for, and the fix belongs to whoever owns the build config. It matters here only because it will halt the next build at step 1 whatever this review does.

**And it constrains rows 5 and 15.** Both add a new script under `scripts/`, and an unwired one is a red preflight by this agent's own rule — so each is wired SOFT in the same change, or added to `SUITE_GATE_EXEMPT` with a stated reason. Not afterwards.

### Known at draft time, to be honoured at apply time

1. **`IMP-0708`'s closure must account for BOTH paths its `proposed_change.target` names.** The simulation failed on exactly this: the target names `contract/delivery-parameters.json` and `scripts/compute-invoice.py`, and a closure naming only the evidence-map note is refused. Both landed already, so `applied_by` names both.
2. **Three entries stay open, not closed.** `IMP-0704`, `IMP-0710` and `IMP-0711` are `observable_at` V4 — a signed-in user must see the form. Each gets a `deferred_reason` and a `revisit_when`; a document saying the ADR was corrected is not that observation.
3. **`IMP-0703` and `IMP-0707` close together or not at all.** The second `corrects` the first, and the validator warns until both move.
4. **Row 9 is a narrowing, not the proposal as written.** The deviation is recorded on the entry, in §2, and in the gate output — three places, per the narrowing rule. The false positives it removes are the 19 closed-row ids and the three off-corpus register rows, all named in §2.
5. **The digest was already regenerated** for `IMP-0720`. Re-run it once more at apply time and correct the registered size claim in the same change (row 17), or `verify-derived-counts.py` stays red on this review's own compliance.

### One residual worth a line, not a row

`verify-review-document.py`'s CLUSTER-COUNT failure message tells the author to re-derive with `grep -c '^CLUSTER '` — a literal trailing space, which returns **0** on every correctly formatted review document in this repository, including the nine-cluster one approved earlier today. The gate's own regex is `^CLUSTER\b` and counts correctly; only its advice is wrong. That is the shape of a remediation sentence that cannot be followed, a class already recorded once. One character, and not worth a change-table row against this review's budget — recorded here so the next author does not trust the message over the gate.

---

## 10. Applied

Applied 2026-09-11 on `APPROVE IMPROVEMENTS`, with the reviewer's decision on §6: **leave the
blocker trigger immediate**, ship the visibility metric, revisit with real data.
**All 17 rows landed. 15 entries closed, 3 left open with a reason, 2 proposals withheld,
5 changes narrowed by measurement.**

| # | Change | Entries moved to APPLIED |
|---|---|---|
| 1 | `WORKFLOW.md` blocker row now says **UNREAD** | IMP-0717 |
| 2 | `WORKFLOW.md` scoped-fix exception, with its three conditions | IMP-0717 |
| 3 | Adaptive batch threshold — `batch_threshold()`, floor 30→45, `C-TECH-061` and the `WORKFLOW.md` row now cite the constant | IMP-0716 |
| 4 | `WORKFLOW.md` "a gate keyword is a RESUME" + `lead-agent.md` rung 7 + rung 5's parallel-gate clause | IMP-0718, IMP-0712 |
| 5 | `scripts/report-dispatch-share.py` (new) + SOFT wiring as `dispatch-share` | IMP-0719 |
| 6 | `how-to-promote-a-finding.md` §3a duplicate check, §3b classify-the-corpus rule | IMP-0718, IMP-0720 |
| 7 | `architect-agent.md` — consequence trace covers every named mechanism | *(IMP-0704, IMP-0710 left open — V4)* |
| 8 | `contract/evidence-map.json` stale `complete_states` note corrected | IMP-0708 |
| 9 | `verify-assumption-markers.py` + twin — source→register direction, narrowed | IMP-0703, IMP-0707 |
| 10 | `verify-system-consistency.py` (engine) — one slug per feature, narrowed | IMP-0706 |
| 11 | `import-baseline.py` — discover the source by version, fail on a newer one | IMP-0714 |
| 12 | `verify-wbs-chain.py` + twin — INERT exception reporting | IMP-0715 |
| 13 | `.engine/scripts/kb.py` — `ensure_ascii=False` | IMP-0699 |
| 14 | `plan-agent.md` — date an open question against an EVENT | *(IMP-0711 left open — V4)* |
| 15 | `scripts/verify-open-questions.py` (new) + SOFT wiring as `open-questions` | *(IMP-0711)* |
| 16 | `OQ-151` re-dated against the wbs:8.2 privilege grant | *(IMP-0711)* |
| 17 | Two registered derived counts corrected (digest 676→683, verify scripts 59→60) | — |
| — | Closed on work that landed before this review | IMP-0700, IMP-0702, IMP-0705, IMP-0709, IMP-0713 |

### Withheld, and why

**The only new constraint in the queue was not written.** `IMP-0704` proposed a constraint giving
each intervention an ADR's Decision names its own dev-summary row. Its `Verify By` would have to
count interventions in a prose paragraph — a phrase-reading instrument, measured 48–100% false five
times here, once reddening on the erratum written to satisfy it. A constraint whose `Verify By` is
not mechanically executable is a comment. The authoring discipline in row 7 is the altitude that
works. **Constraint budget: 0 of 3 used.**

**The SDD/TAD verification-level grep was not built** (`IMP-0709`). The finding asked for the
false-positive rate to be measured first; the repository's supposed recurring phrasing occurs
**once**, with two near-miss variants it would not match. A regex fitted to one sentence is not a
gate. Return condition: revisit if a second document independently adopts that phrasing.

### Narrowed, and the false positives each narrowing removes

Five changes were narrowed by measurement rather than applied as written.

1. **Row 9 — the marker gate's require-OPEN condition was dropped.** As written it failed **23 of
   47 ids (49%)**. **19 were correct closures**: a marker citing a closed row is what a
   *successfully ground-truthed* assumption looks like, because this repository retains the comment
   that recorded the guess. Three more were register rows the gate could not see — one struck
   through, one written as prose, one in an architecture document. Narrowed to orphans only, with
   register discovery widened: **1 finding, 1 true positive** (`A-REV-01`).

2. **Row 10 — the build and pipeline configs were removed from the per-feature artefact set.**
   Including them reported 3 of 4 features split, and **every config finding was false**: this
   solution has exactly one build config and one pipeline config, shared by all features, because a
   packer config describes the solution. Narrowed to the document triple: **2 findings, both
   adjudicated true** (payment-capture has no architecture under its own slug;
   form-field-corrections' dev-summary content sits under the parent slug, confirmed by grep).

3. **Row 15 — the gate asserts exact membership of a declared non-event set, not event
   specificity.** The nearest mechanical form of the proposal — does the due cell anchor to a task
   id, date, gate keyword or named artefact — measured **25 of 51 rows (49%)**, with legitimate
   events among the false positives: *"Before go-live"*, *"At environment setup"*, *"Before
   procurement"*, *"At TAD stage"*. Exact membership cannot false-positive: **5 findings, 5 true
   positives**, now 4 after row 16.

4. **Row 2 — the scoped-fix exception already existed.** The finding asked for a new one; it is
   already `verify-improvement-log.py`'s own printed remedy and `C-TECH-061`'s named discharge. The
   change states the existing discharge where the routing decision is taken. Its cited precedent
   also halved on measurement: `IMP-0698` carries a well-formed `deferred_reason`; `IMP-0700`
   carries none, which is why it was still queued.

5. **Row 6 — the duplicate check is a named exception to activation step 2, not a general grep.**
   The general form contradicts the step above it, and that step is what produced the miss it cites.
   Scoped to `APPLIED` entries sharing a cluster's own `class_instance_of`.

**And row 3's reporting was narrowed even though its substance was not:** the finding called the
batch trigger *"the largest single driver"* at 28 of 90 dispatches. It measures **8**. The change
ships, and moves the dispatch share by roughly 2.7 points — not the 15 the request implied.

### Routed, not fixed here

| Item | Owner | Why it is not this review's to fix |
|---|---|---|
| `A-REV-01` — a marker in `rev_review`'s form XML with no register row anywhere | development-agent | A source comment plus a register row in the governing dev summary. Row 9 reports it as a NOTE so the gate does not open red on work no dispatch owns |
| **All 6 live exceptions report INERT** | pm-agent | Six accepted waivers currently suppress nothing. Whether each cause is genuinely fixed — and not merely quiet, or fixed by something unrelated — is a PM judgement, and four expire within weeks |
| 2 features split across slugs | development-agent / architect-agent | Renaming a shipped document's slug is not a rules change |
| 4 open questions still dated *"Before build"* / *"Before build starts"* | plan-agent | Re-dating them needs the owner who knows which event each answer is load-bearing for |

**Re-measured at apply time, and the diagnosis changed.** The draft reported the build-config
preflight as *"already red, independently of this review"*. Re-run at apply time it exits **0** —
but only because a **concurrent session added `report-baseline-drift.py` to `SUITE_GATE_EXEMPT`
uncommitted.** Proven by execution: stashing that one file returns exit **1**. So the fix exists
only in this working tree, is red at `HEAD` and in CI, and the real cause — the suite-gate check's
`--check` detection is a naive whole-file substring match that hit prose *about another script's*
flag — was logged independently by a build-agent session as `IMP-0721` while this review was
parked. That entry is **outside this review's approved scope and left `unread`**; it now owns the
routed item and proposes the correct fix (scope the detection to the script's own argparse).

### Verification actually executed

| What | Result |
|---|---|
| `verify-improvement-log.py --check` | **exit 0** — 718 entries, 0 unread blockers, batch trigger clear |
| `verify-improvement-log.py --selftest` | **68 fixtures PASS**; `batch_threshold()` exercised at 0/10/100/225/226/400/1000 dispatches and with the log absent |
| `report-dispatch-share.py` | selftest **11 checks PASS** (both flag polarities); real corpus **91/300 = 30.3%**, independently reproducing the hand measurement |
| `verify-open-questions.py` | selftest **11 checks PASS**; corpus **5 → 4 findings**, all true positives |
| `verify-assumption-markers.py` | selftest **14 fixtures PASS**; corpus **1 orphan**, the predicted true positive; exit 0 |
| `verify-wbs-chain.py` | corpus **6 of 6 exceptions INERT** — verified a true reading by there being **0** `[EXCEPTION]` tags among 33 warnings; polarity fixture proves a *consulted* exception is not reported |
| `import-baseline.py --check` | **both polarities**: exit 0 clean → exit 1 against a planted v0.7 → exit 0 with the plant removed, tree left clean |
| `verify-system-consistency.py` | 2 findings, both adjudicated; binary gate still PASS |
| `.engine/scripts/kb.py` | round-tripped an em-dash and an arrow through `add_failure_mode`; **literal bytes stored, no `\uXXXX`**; selftest 16 checks PASS |
| `scripts/ci/verify-pm-gates.sh` | **exit 0** — all PM gates pass, every known-bad fixture rejected |
| `BuildGates.Tests.ps1` | **115 tests, 0 failed** — the suites that pattern-match gate stdout, re-run because rows 9 and 12 changed printed text (`IMP-0698`'s class) |
| `verify-build-config.py` | **exit 0** with both new gates wired |
| `verify-derived-counts.py` | **exit 0 — 10 of 10 claims match** |
| Digest | regenerated, `--check` **current** (718 entries, 712 lesson groups) |
| Engine twins | `verify-wbs-chain.py` and `verify-assumption-markers.py` confirmed **byte-identical** to their `.engine/` copies |
| Task states | **61 derived statuses unchanged** before and after the `contract/evidence-map.json` edit |

**Not verified:** nothing was run against a live environment and no V3/V4 observation was made —
hence the three entries left open. `verify-open-questions.py` and `report-dispatch-share.py` are
V1: they parse, self-test and run over the real corpus, and no build has yet executed them as
wired steps.
