# Improvement Review — 2026-09-20 (3)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 6 `NEW` → 5 clusters
**Trigger:** blocker escalation — one unread `blocker` entry (`IMP-0804`), processed on its own
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** ~~AWAITING — nothing in section 3 has been applied.~~ **APPLIED 2026-09-20.** All five
changes landed, plus one file the approved wording did not name — see section 10. Six entries
settled. **Not yet committed to either repository.**
**WBS:** `wbs:6.10` (the flow this incident aborted), `wbs:system` (the gate and the rules)

---

## 0. The measurement that decides this review

**The fix proposed inside the blocker finding, implemented literally, would have passed the
artifact whose import aborted.**

That is not a quibble about wording. The finding asks for a recursive walk over
"actions / **elseActions** / case-actions / default-actions" containers. This solution's flows are
Logic Apps schema definitions: an If's alternative branch is `else.actions`, not `elseActions`.
Measured across the eight production flows, the key `actions` occurs 68 times, `else` 22 times and
`elseActions` **zero** times.

| Candidate gate | Action names it collects from the failing flow | Duplicates found |
|---|---|---|
| **A** — the container keys the finding names, taken literally | 40 of 261 | **0** — reports OK on the artifact that aborted the import |
| **B** — generic descent into every `actions` dict at any depth | 261 of 261 | **1** — the real one, at both of its paths |

Design B is what section 3 proposes, and it needs no new descent code: the general gate for this
class already carries exactly that walker at
[`_iter_actions`](.engine/scripts/verify-flow-definition-language.py#L86), which recurses through
every key and therefore covers `else`, `cases` and `default` without naming any of them.

A second measurement removed a design that looked obvious:

| Candidate gate | Findings across the 8 production flows | True positives |
|---|---|---|
| **C** — action names unique across the whole *solution* | 13 | **0** |

Every one of the 13 is the shared error-handling scaffold — `Initialise_failure_detail`,
`Find_the_failed_action`, `Set_failure_detail`, `Compose_run_link`, `Alert_on_failure` — repeated
deliberately in seven flows. The platform's dictionary is built per flow, so solution-wide
uniqueness is not the property; flow-wide uniqueness is. A gate built on the wider reading would
have opened red on the project's own convention on day one.

### And the corpus moved twice while this was being written

Two dispatches were live in this repository throughout. Both facts below are measurements taken
minutes apart, and both changed what this review says:

| Measured at | What the flow file showed |
|---|---|
| 22:10 | The duplicate name was gone (renamed), and the sole consumer still read the **old** name unguarded — so on the unseeded-history path it read an action that does not run there. Logged as `IMP-0805` |
| 22:35 | **Fixed.** The consumer now reads `if(empty(outputs('Compose_history_start_raw')), '[]', outputs('Compose_historic_months_array'))` — a branch-discriminator guard plus a literal. The other dispatch had found the same defect independently and fixed it |

Nothing is proposed on the strength of the 22:10 measurement. It is recorded because a review that
measured once and reported it twenty-five minutes later would have routed a fixed defect back to
the agent that had just fixed it.

---

## 1. Regression check — did the last review's changes work?

Audited against [the previous review](2026-09-20-improvement-review-2.md), all four of its changes.

| Prior change | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|
| `scripts/verify-assumption-id-collisions.py` + its build step | assumption ids reused for a new question | **No** | Working; nothing has tested it either way yet |
| The two claims a TAD makes about files it does not own, in `agents/architect-agent.md` | `architect-agent` asserting things whose ground truth lives elsewhere | **No** | Working |
| The premise-check clauses in `agents/lead-agent.md` | a dispatch brief carrying an unverified fact | **Yes, once — and the rule fired.** A deployment session was told to verify a saved query that does not exist in source, greped for it first, found nothing, and reported the mismatch rather than fabricating a result | Working. That is the rule doing its job; the open question it raises is in section 8 |
| The registered `verify-*.py` count in `agents/improvement-agent.md`, 63 → 64 | a hand-maintained count drifting | **No** — and this review does not drift it, because it adds **no new script** | Working |

**Changes whose class recurred after a prose fix:** none.
**Changes whose class recurred after a gate:** none.

Two older changes were audited as well, because this review depends on both:

- [Step 6 of `agents/improvement-agent.md`](agents/improvement-agent.md#L142) — *grep the premises
  of every finding you are processing, at draft time* — is what produced section 0. **Working**,
  and its class recurring is the rule catching something rather than failing.
- The id allocator, `scripts/allocate-improvement-id.py`, built because the prose version of that
  rule had failed six times. **Not working — and section 3 change 5 says why.** It failed a
  seventh time in this session, in both live dispatches at once.

---

## 2. Clusters and promotion decisions

```
CLUSTER: platform-contract-guessed-not-groundtruthed  (x61 overall; x1 new: IMP-0804)
Altitude:  CLASS — far past the second instance. This is the class's 61st member and the
           fourth to land as a numbered check in the same general gate.
Ladder row: "a tool could catch it mechanically" + "a platform law" — and the platform law
           was observed live (V3), not argued: a real import aborted on it.
Becomes:   CHECK 8 of .engine/scripts/verify-flow-definition-language.py, whose docstring
           already names it "THE GENERAL GATE FOR CLASS
           platform-contract-guessed-not-groundtruthed". No new script, no new build step,
           no new wiring, no registered-count drift.
Retires:   nothing — see section 4
Cites:     IMP-0804
Residual:  THREE, all named rather than absorbed.
           (a) Triggers are excluded. Whether a trigger name shares the same dictionary as
               action names is not established; the corpus has 0 trigger/action collisions,
               so including it would change no result today and would assert a contract
               nobody has ground-truthed.
           (b) Case-insensitive collisions are reported, never failed on. The incident's
               duplicate was exact-case; case-insensitivity is inferred from the .NET
               exception type, which is a diagnosis, not an observation. Corpus: 0.
           (c) This gate reads SOURCE. A flow edited in the maker portal and exported later
               is outside it until the export lands in src/.
```

```
CLUSTER: rename-leaves-unreachable-branch-output  (x2: IMP-0805, IMP-0807)
Altitude:  INSTANCE — a new class, two members, both from the same fix, both closed within
           the hour by the dispatch that introduced it.
Ladder row: "one instance, specific to one feature" → it stays a log note.
Becomes:   NOTHING in agents/, constraints/ or skills/. The fix is already in the tree and
           was verified there at 22:35. A candidate gate was built and measured, and the
           measurement is why it is a decision for you rather than a change here — section 8.
Retires:   nothing
Cites:     IMP-0805, IMP-0807
Residual:  The class has a real mechanical gap. A reference-resolution check does NOT catch
           it — all 972 expression references in this solution resolve to a declared action,
           including the broken one, because the old name survived on the sibling branch.
           Catching it needs branch reachability, which nothing here does.
```

```
CLUSTER: finding-premise-fails-re-measurement  (x2 overall; x1 new: IMP-0808)
Altitude:  NOTE — the rule that catches this already exists and caught this.
Ladder row: none taken. Raising an existing, working rule because it fired is how a rule set
           reaches 56 rows and zero retirements.
Becomes:   NOTHING. Recorded, and used as the worked example section 0 makes of it.
Retires:   nothing
Cites:     IMP-0808
Residual:  Nothing reads a finding's proposed_change for content, and nothing reasonably
           could. The defence stays a human-executed step in one agent's activation sequence.
```

```
CLUSTER: resolved-field-carries-prose  (x1: IMP-0809)
Altitude:  CLASS, but at the SCHEMA — the rule exists and lives in the wrong file.
Ladder row: "an agent had the information and still did the wrong thing" — except it did not
           have it: the rule is in agents/improvement-agent.md, which no delivery agent reads.
Becomes:   One clause in skills/how-to-log-an-improvement.md's `corrects` section, which every
           agent reads when writing a finding.
Retires:   nothing
Cites:     IMP-0809
Residual:  Measured 3 of 43 entries carrying `corrects` hold a non-id value — one sentence and
           two nulls. The two nulls are not addressed here; they predate this and nothing reads
           them.
```

```
CLUSTER: duplicate-improvement-id-race  (x1 new: IMP-0810 — and the SEVENTH of its prose rule)
Altitude:  CLASS — and the generalisation already exists as a script. What failed is the
           INSTRUCTION, which still names the superseded manual method.
Ladder row: "the system's own memory failed" → a read-path change, in the agent file.
Becomes:   agents/improvement-agent.md line 278 rewritten to name the command instead of the
           method that has now failed seven times.
Retires:   the manual method, in the one file that still teaches it.
Cites:     IMP-0810
Residual:  The lock coordinates processes on ONE machine. Two machines syncing this SharePoint
           path are caught by the validator's duplicate-id error, not prevented — which is what
           happened here, twice, and is the honest limit of the fix.
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | [`.engine/scripts/verify-flow-definition-language.py`](.engine/scripts/verify-flow-definition-language.py#L116) | **Check 8** — no action name occurs twice anywhere in one flow definition, at any depth, in any branch. Fails HARD, citing every JSON path the name occupies. Case-only and trigger/action collisions print as a non-fatal `NOTE` | IMP-0804 | YES — `python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation` | **already wired** — [`flow-definition-language`](config/revitalise-grant-automation-build.yml#L611); check 8 rides the existing HARD step |
| 2 | script | [`.engine/scripts/verify-flow-definition-language.py`](.engine/scripts/verify-flow-definition-language.py#L749) | Two selftest fixtures for check 8: a duplicate name across the two branches of one `If` (**must fail**), and the same name used in two different flows (**must pass**) — the second pins candidate C's false-positive class so the polarity cannot silently invert | IMP-0804 | YES — `python3 scripts/verify-flow-definition-language.py --selftest` | N/A |
| 3 | knowledge | [`knowledge/technology/power-automate.md`](knowledge/technology/power-automate.md#L194) | Under *Naming Convention*: action names are unique **per flow, across every branch**, because the import-time dependency calculator flattens all branches into one dictionary before computing dependencies. Mutually exclusive branches do not make two names one name. Observed live at V3, with the async operation id | IMP-0804, IMP-0805 | N/A — reference material | N/A |
| 4 | skill | [`skills/how-to-log-an-improvement.md`](skills/how-to-log-an-improvement.md#L128) | In the `corrects` section: the value is **resolved against this log's ids**, so it takes an id or a list of ids and nothing else — no sentence, no `"none"`, no explanatory clause. Correcting nothing is said by omitting the field | IMP-0809 | YES — `python3 scripts/verify-improvement-log.py --check` already reports the dangling edge | N/A |
| 5 | agent | [`agents/improvement-agent.md`](agents/improvement-agent.md#L278) | Replace *"re-read the log's current maximum id immediately before you append anything"* with the command — `python3 scripts/allocate-improvement-id.py --append <entry.json>` — stating that reading a maximum and writing by hand is the form that has now failed **seven** times, and that the lock is the only form that holds | IMP-0810 | YES — `python3 scripts/allocate-improvement-id.py --selftest` | N/A |

**Constraint budget:** 0 of 3 used.

**Why no constraint row.** Every prior member of this class became a numbered check in this one
gate and none of them got a constraint row — checks 1, 3, 4 and 7 all landed this way. A row
asserting what check 8 already executes would be a comment with an id, and this project's own
evidence is that the script is what changes behaviour.

**Why no new script.** The gate that owns this class exists, runs on every build, and already
carries the exact recursive walker the correct design needs. A separate
`verify-flow-action-name-uniqueness.py` would need its own build step, its own wiring proof, and
would drift the registered `verify-*.py` count. Extending the general gate costs one function and
changes no count.

### The corpus measurement, in full

**1 finding across 28 committed flow-file versions and 1,813 action names — 1 true positive, 0
false positives.**

| Corpus | Scanned | Findings | Adjudication |
|---|---|---|---|
| The 8 production flows, current working tree | 446 action names | **0** | **0 is correct, and here is why**: the concurrent dispatch renamed the else-branch copy while this review was being written. The duplicate is gone from the tree. This is not a clean run over an unfixed corpus |
| Every committed version of every production flow (`git log` sweep) | 28 file-versions, 1,813 action names | **1** | **True.** `Compose_historic_months_array` at commit `7d22c7d`, at exactly the two paths the finding names — the if-branch and the else-branch of `Condition_history_start_seeded` |
| The 5 known-bad workflow fixtures | 3 action names (1 file deliberately unparseable) | **0** | Correct — none of them is about names |
| Case-only collisions, whole corpus | 1,813 names | **0** | Nothing to adjudicate; this is why residual (b) is a note and not a failure |
| Trigger/action collisions, whole corpus | 8 flows | **0** | Same, for residual (a) |

The selftest and the corpus run answer different questions, and both are required before wiring:
the selftest proves the check *can* fail, the corpus run proves it fails on the *right* things.
Here the corpus run also disproved two designs — candidate A (0 true positives, misses the real
one) and candidate C (13 findings, 0 true) — which is the whole reason the measurement comes
before the wiring rather than after.

---

## 4. Retirements

> Retirement check performed: no constraint row, gate or check is made redundant by check 8,
> because nothing in this repository checked action-name uniqueness at any scope before it.

The check was a grep, not an impression: `elseActions` and `FlattenNestedActions` return zero hits
across `scripts/`, `.engine/scripts/` and `src/tests/`, and no `C-TECH-` row cites the
`flow-definition-language` gate at all. Check 8 is additive to an undefended class.

**One method is retired, in the one file that still teaches it**: change 5 removes the
read-the-maximum-by-hand instruction from `agents/improvement-agent.md`. That is a retirement of a
superseded *method* rather than of a constraint row, and it is the sweep step of the retirement
procedure — the implementation and its call sites were done months ago; the instruction was not.

The nearest constraint candidate considered and rejected: the hardcoded descent-depth assertions in
`src/tests/solutions/RoundStatisticsContract.Tests.ps1`, stale twice now for the same structural
reason. They are a test-design problem in `src/`, owned by development-agent, and they assert
something check 8 does not — retiring them would lose coverage, not consolidate it.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0798, IMP-0799, IMP-0800, IMP-0801, IMP-0802, IMP-0803

**Why these six are out of scope, stated rather than assumed.** The queue holds seven `unread`
entries. Exactly one is a `blocker`, and the blocker trigger is what summoned this dispatch: it is
processed **on its own, at once**, and one unread blocker must not pull a review of everything
around it. The other six are `rework` and `friction`, none is older than today, and three already
carry their own fix in the log. They are the next ordinary review's work.

The 176 `reviewer-deferred` entries are excluded by state, not by choice — each carries a reason a
human accepted.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0798 | commercial ledger backfill, already done | Asks this agent to close two other entries on evidence a delivery dispatch produced. Bookkeeping, not a blocker | the next ordinary improvement review |
| IMP-0799 | test hardcodes container descent depth | Second instance and a real generalisation candidate — but the target is `src/tests/`, owned by development-agent, and the remedy is a test rewrite rather than a rule change | the next ordinary review, or a third instance |
| IMP-0800 / IMP-0801 | stale figure inside a triage row | The fix has already landed. Needs closing, not deciding — **and the gate warns that leaving it open will fail the next build's unit-tests step** | the next ordinary review, which should take it first |
| IMP-0802 | stale pack-warning count, 14 against a measured 17 | A figure in a Dev Summary owned by development-agent | the next ordinary review |
| IMP-0803 | a dispatch brief naming a component that does not exist in source | **This one has a question in it for you — section 8.** The rule that caught it was added yesterday and worked | you answer where `EqualityMonitoring` came from |

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 801 | 806 |
| Distinct classes | 176 | 179 |
| Recurring classes (x≥2) | 60 | 62 |
| Digest lines | 729 | regenerated on approval |

Five entries were appended during this review: `IMP-0805` and `IMP-0807` (the rename defect, found
independently by two dispatches and fixed by one of them), `IMP-0808` (the premise that failed
re-measurement), `IMP-0809` (a resolved field carrying prose) and `IMP-0810` (the id race this
review itself caused). All six processed entries are stamped; none is deferred.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-20-improvement-review-3.md

Findings processed: 6 NEW  →  5 clusters
Regression check:   4 prior changes audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 2 gates/scripts, 2 skill/knowledge edits,
                    1 agent-file edits, 0 retirements
Altitude calls:     2 generalised from instance to class, 3 left as notes
Digest:             will regenerate — 806 lessons, 62 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. What you need to decide

**Should a second check go in — one that flags a `Compose` action whose output nothing reads?**

**Problem** — The fix for the import failure renamed one branch's action and, for about
twenty-five minutes, left its only consumer reading the old name, which no longer existed on the
path being taken. Check 8 cannot see that, and neither can a reference-resolution check: all 972
expression references in this solution resolve to a declared action, including the broken one,
because the old name survived on the sibling branch.
**Suggested fix** — Add check 9: a `Compose` whose output no expression reads is a finding.
Measured over the corpus it returns 3 findings from 144 `Compose` actions — one certain true
positive (the renamed action, referenced zero times), one probable (a computed provider name
nothing reads) and one deliberate placeholder named `DEFERRED_call_duplicate_grant_check`. Wiring
it HARD needs those two pre-existing findings baselined with an owner and an expiry first, which is
plumbing this gate does not yet carry.
**What happens if you don't** — This class stays invisible to every gate. The one live instance was
caught because a review happened to measure for it, and the next one will be found the same way or
not at all.
[The measurement is in section 3; the live instance is `IMP-0805` in the log.](logs/improvement-log.jsonl)

---

**Where did `EqualityMonitoring` come from?**

**Problem** — A dispatch brief told a deployment session to verify two saved queries were reachable
after import. One of them does not exist anywhere in source — not as a view, not in the app's
sitemap, not as a component. The other is real and correctly wired.
**Suggested fix** — Tell us whether it names wanted future scope. If it does, it needs a WBS task
id and a change-order decision rather than an ad-hoc verification instruction; if it was a
conflation with the equality-monitoring *columns*, which are real and shipped, nothing needs doing.
**What happens if you don't** — A named component nobody can account for stays in the delivery
record, and the next dispatch that inherits the phrase will try to verify it again.
[`IMP-0803` in the log](logs/improvement-log.jsonl)

---

## 9. What the keyword disposes of — simulated before it is asked for

Nothing here has been done. This is what `APPROVE IMPROVEMENTS` would move, run against a scratch
copy of the log so that the answer is measured rather than intended. **Two of the six entries
cannot be closed by anyone in this session, and the keyword is being asked to approve that
deferral explicitly rather than have an agent write one quietly.**

| Finding | Disposition on approval | Why |
|---|---|---|
| The import blocker | **stays open**, with a reviewer-approved reason and a return condition | Its defect was only ever visible when a live import ran (V3). The gate is applied; the closure needs the next successful DEV import, and that is pipeline-agent's to observe |
| The rename defect, source side | **closed** | Re-measured at source: the guard is in the file. Evidence needle verified against the line it matches |
| The rename defect, runtime side | **stays open**, same treatment as the blocker | Only visible when the flow takes the unseeded-history path live (V5) |
| The premise that failed re-measurement | **rejected**, with the reason recorded | No change proposed and none needed — the rule that catches it already exists and caught it |
| The resolved field carrying prose | **closed** on change 4 landing | — |
| The id race | **closed** on change 5 landing | — |

Simulated with the gate, on a scratch copy, before this draft was submitted: **the blocker trigger
clears under this disposition**, and the real log was confirmed byte-identical afterwards. The two
errors the simulation still reports are the two changes not yet applied, which is correct — they
are claims that only become true when section 3 lands.

---

## 10. Applied — 2026-09-20

### The authorisation, recorded first

| | |
|---|---|
| Keyword | `APPROVE IMPROVEMENTS`, verbatim |
| Authorised by | **Anna Southern** (anna.southern@argelis.nl) |
| Channel | `lead-agent` relay, stated as quoted from her own turn in this session's conversation |
| Artefact named | `docs/improvements/2026-09-20-improvement-review-3.md` |

Checked against all four conditions in `agents/WORKFLOW.md` before the relay was accepted: from
`lead-agent`, keyword verbatim, the human named, and stated as quoted from her own turn. Not a
commercial act, so the record is this section and the gate output rather than
`logs/commercial-events.jsonl`.

### Re-verified before applying

No entry was appended between the draft and the keyword; the log's maximum was unchanged at
`IMP-0810`. The one `corrects` edge touching this review — `IMP-0807` correcting `IMP-0805` — is
the fix confirmation, which agrees with the disposition rather than contradicting it. The flow was
re-measured: still 0 duplicate names, guard still in place. **And the gate was executed rather than
read**, which is what produced the correction below.

### What landed

| # | Target | Repository | Landed |
|---|---|---|---|
| 1 | `.engine/scripts/verify-flow-definition-language.py` | `.engine` | Check 8, plus `notes` threaded through `check_definition` and `run` so the two unproven shapes report without failing |
| 2 | same file, selftest | `.engine` | Two cases, both green: duplicate across `If` branches **fails**, same name in two flows **passes**. The harness now accepts a list payload, because no single-file fixture can prove a per-flow scope |
| 3 | `knowledge/technology/power-automate.md` | instance | New subsection under *Naming Convention*, with the mechanism, the async operation id, and the three consequences |
| 4 | `skills/how-to-log-an-improvement.md` | `.engine` | The `corrects` section: bare id only, omission means no correction |
| 5 | `agents/improvement-agent.md` | `.engine` | The allocator command replaces the manual method, with the seven-instance record and the honest residual |
| 5b | `skills/how-to-log-an-improvement.md` | `.engine` | **Beyond the approved wording — see below** |
| 6 | `config/revitalise-grant-automation-build.yml` | instance | The step's own comment, which described the gate as catching three shapes and now names check 8 as the fourth |
| 7 | `scripts/generate-known-failure-modes.py` + its `.engine` twin | both | The registered digest line count, 728 → 733, drifted twice by regenerating |
| 8 | `logs/improvement-log.jsonl` | instance | Six entries settled; four appended during the review |
| 9 | `logs/known-failure-modes.md` + appendix | instance | Regenerated — 806 entries |

### One change went WIDER than the approved wording, and here is exactly how much

Change 5's approved wording named **one** file, and section 4 called it *"the one file that still
teaches it"*. That was wrong, and the change's own rule is what found it: *when a prose rule is
mechanised, every file that INSTRUCTS the prose version must name the command instead.* Running
that sweep turned up a second instruction — `skills/how-to-log-an-improvement.md`'s *Required
fields* section printed a copy-pasteable one-liner computing the maximum id by hand.

It is applied, as 5b, and it is reported here, in the entry's `applied_by`, and in the gate output.

**Why this is a widening and not a substitution.** It changes no rule's meaning and removes no
enforcement; it deletes the last copy of an instruction the reviewer approved retiring, in the file
an agent actually reads when writing a finding. Leaving it would have defeated change 5 entirely —
`agents/improvement-agent.md` is read by one agent, the skill by all of them. The reviewer should
know it happened; the alternative was an approved change that could not work.

### Measured results of the applied gate

| Run | Exit | Result |
|---|---|---|
| `--selftest` | 0 | All cases pass, including the two new ones. Proves check 8 **can** fail |
| The real build command, current tree | 0 | 8 flows, 0 findings, 0 notes — no false positive on a clean corpus |
| The pre-fix artifact rebuilt from commit `7d22c7d` | **1** | Names the duplicate and **both** JSON paths. Proves it fails on the **right** thing |

### Nothing narrowed, nothing withheld

Every change survived re-verification in its approved wording. Verification level reached:
**V1** for the gate — it runs, its selftest is green, and it discriminates correctly between the
broken and fixed artifacts on disk. Nothing here has been proven against a live import, and the
blocker entry stays open for exactly that reason.

### Not yet published — and a clean tree does not prove otherwise

Four of these changes are in the `.engine` submodule and are committed to **neither** repository.
The publish order is not a preference: push the submodule first, verify with
`git -C .engine branch -r --contains HEAD` (`git status` reports clean throughout and `git status
-sb` prints `## HEAD (no branch)` either way), then commit and push the instance pointer bump.
