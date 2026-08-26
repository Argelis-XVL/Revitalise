# Improvement Review 30 — 2026-08-26

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 13 `NEW` (`unread`) → 9 clusters
**Trigger:** batch — 12 unread against a batch trigger of 10, no unread blocker. One further
finding (`IMP-0344`) was appended by this session's own gate measurement and is processed here.
**The queue grew to 16 unread while this was drafted** — three findings from the concurrent
`test-agent` dispatch. They are **deferred, not folded in**, and §5 gives the reason.
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** ~~DRAFT — nothing in this document is on disk~~ — **APPLIED 2026-08-26.** The reviewer
sent `Approve improvements`; all thirteen changes of §3 are on disk, all thirteen findings are
dispositioned, and §10 records what landed, what was narrowed on measurement, and what was
deliberately left open. Two of the thirteen were **narrowed** at application because their measured
precision was worse than the draft's probe reported — recorded per activation step 8's third
branch, which this review itself added.
**Scope note:** drafted alongside a `test-agent` dispatch on `trustee-portal-visual-refresh`.
Neither gate blocks the other. This review touched nothing under `docs/tests/`,
`docs/development/` or `docs/architecture/` — and §5 records the one live defect that fencing
left unfixed.
**WBS:** all system work, not billable
([C-COM-002](../../constraints/commercial/commercial-constraints.md#L35)). One finding carries a
commercial consequence belonging to another agent, named in §5.

---

## Summary

**The last review's largest escalation was built on a misdiagnosis, and the gate it built is what
proved it.** Review 29 escalated "a requirement names data this solution cannot supply" to a
mechanical gate because the class had recurred three times through two rounds of written
guidance. That gate then fired on six items, and every one of them names a column that already
existed in the schema — including the one item review 29 called "the real undeliverable
requirement" and priced as a probable change order. The coverage gate is green today with no
schema change and no change order. The class was never about data the solution could not supply;
it was about nobody enumerating the columns.

**Three of the four checks the queue asked me to build are dropped, because I measured them.** One
scored eighteen false positives and no true ones, and is conceptually wrong besides — it compares
a count of retirements against rows of a table that never held them. One scored zero true positives
in six hits and would not have caught the defect it was proposed for. The third scored 1 of 1 until
I ran it against this document, where it fired on the sentence describing the very error it had
correctly found. The one that survived measured 3 of 3 across all thirty-three documents.

**A review document still on disk contradicts itself in the way it recorded that reviews
contradict themselves.** The last review's summary says it asks you seven questions; its
decisions section asks eight. That specific error was written down as a finding, and then not
fixed.

**A gate measurement found a live defect on the feature your test thread is looking at, and I left
it alone.** A dev summary cites its architecture document as approved at revision 2; that document
says draft at revision 2. One of the two is wrong, both files are the delivery thread's, and this
dispatch was fenced off from them.

**What needs you:** **no new constraints** against a cap of three, one gate widening and one new
gate, one gate promoted from warning to blocking, four agent-file edits, three skill edits, one new
helper script and two one-line script fixes, no retirements, and five decisions — none of which
blocks this review. Thirteen changes, and the per-type figures above are derived from the thirteen
rows of §3 rather than counted by hand, because this review's own subject is what happens when they
are not.

---

## 1. Regression check — did review 29's changes work?

Review 29 applied seventeen changes on 2026-08-26. Its own applied record is
[§10](2026-08-25-improvement-review-3.md#L786). Grouped by the class each targeted:

| Prior change | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|
| 1 — [`verify-tad-coverage.py`](../../scripts/verify-tad-coverage.py) widening | `requirement-names-data-the-solution-cannot-supply` | **YES, twice** — but as *documentation* defects, not scope defects | **The gate worked and the finding behind it was wrong.** See below |
| 4 — [`verify-requirement-id-uniqueness.py`](../../scripts/verify-requirement-id-uniqueness.py) | `identifier-namespace-collision-across-documents` | **YES, twice** — the gate firing as designed | **Working.** It surfaced a 19-identifier collision, which is now resolved |
| 5 — corpus-precision obligation, [`improvement-agent.md`](../../agents/improvement-agent.md#L291) | `declared-policy-not-mechanically-enforced` | **YES, once** — as a direct consequence | **Working, and it exposed a gap it created.** See cluster D |
| 8 — correction markers in the digest | `finding-diagnosis-unverified` | NO | Working — one new correction will render |
| 9 — citation check scoping + `appended_by` | `gate-fires-on-nothing` | NO | **Working, proven live.** It refused this session's own first append |
| 16 — [`tad-template.md`](../../templates/tad-template.md) prose | `approved-document-internally-inconsistent` | **YES, twice** | **Wrong altitude.** Prose fix, recurred the next day → cluster A escalates it |
| 17 — class aliasing in the digest read path | `hand-maintained-count-drifts-from-source` | NO | Working — the merged row reads x16 |
| 2, 3, 6, 7, 10–15 | various | NO | Working — leave alone |

**Changes whose class recurred after a *prose* fix:** review 29's change 16 → escalated to a
mechanical gate in cluster A. This is the regression rule firing exactly as written. Every "change
N" in this section refers to **review 29's** numbering; this review's own changes are numbered in §3.

**Changes whose class recurred after a *gate*:** changes 1 and 4, and in both cases the gate fired
correctly. Neither is a `gate-cannot-fail`. Change 4's gate found a real collision; change 1's gate
found six real rule violations. What was wrong in change 1's case was the *finding*, not the gate.

**Change 1 deserves its own paragraph, because it inverts the conclusion review 29 reached.**
Review 29 predicted one genuine undeliverable requirement and four items "one backtick from
compliant". Measured now, all six items name columns that exist:
`rev_breaklocation` at
[Entity.xml L1252](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_application/Entity.xml#L1252),
and `rev_breakstart`/`rev_breakend` at
[L1268](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_application/Entity.xml#L1268)
and [L1284](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_application/Entity.xml#L1284),
the last two committed on 2026-08-14 — eleven days before the finding that said no such column
existed anywhere in the solution. `verify-tad-coverage.py` reports **0 violations** today.

The lesson is not that the gate was wrong. It is that **a class name asserting a negative was
adopted three times without anyone enumerating the attribute set**, and the gate is what forced
the enumeration. Cluster C makes that enumeration cheap.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: approved-document-internally-inconsistent  (class is x7; this cluster processes 6:
           IMP-0332, IMP-0340, IMP-0344 + IMP-0158, IMP-0302, IMP-0331. IMP-0347 is the
           seventh and is DEFERRED — see §5)
Altitude:   CLASS — sixth instance. Review 29 answered instance three with a template edit
            (prose) and explicitly declined to gate; two recurrences landed the next day. The
            regression rule says a recurrence after a prose fix escalates to a gate.
Ladder row: "a tool could catch it mechanically" + "second instance -> generalise"
Becomes:    change 1 widens scripts/verify-review-document.py with ONE counting check;
            change 2 is a new gate comparing a citation's asserted status against the cited
            file's own Status line.
Retires:    nothing. THREE of the four checks IMP-0332 proposed are DROPPED on measurement rather
            than shipped -- see §3 -- which is a retirement of proposed scope, not of a live rule.
Cites:      IMP-0332, IMP-0340, IMP-0344, IMP-0302, IMP-0331, IMP-0158
Residual:   THREE, and the third is the honest limit.
            (a) Only ONE of the four proposed checks survived measurement. Two figures this class
                keeps getting wrong -- a review's decision count, and a "change N" prose
                reference -- are now covered by nothing, because neither has a structural home
                to scope a check to. §7 asks whether to build one.
            (b) Change 2 cannot tell WHICH side of a disagreement is stale. It reports the
                contradiction; a human decides. IMP-0344 is open for exactly that reason.
            (c) The property behind these six instances is "one fact stated in two fixed-format
                places, with nothing comparing them". Changes 1-2 cover two such pairs. Any
                fact stated in PROSE in both places stays uncovered, and review 29's cluster I
                was right to decline that half -- it is prose resolution, not counting.
                IMP-0347, the seventh instance, is exactly that uncovered half: a one-sided
                assumption-register claim. It confirms the residual rather than changing the
                design, which is part of why deferring it costs nothing.
```

```
CLUSTER B: identifier-namespace-collision-across-documents  (x3: IMP-0336, IMP-0339 + IMP-0327)
Altitude:   CLASS — third instance, and the first two were instance-level fixes. IMP-0339 says
            so itself: the collision is a property of the numbering CONVENTION, not of either
            document, which is why two local fixes did not prevent it.
Ladder row: "the order of steps was wrong" (nothing checks at AUTHORING time) + "a platform law,
            or a third instance"
Becomes:    change 3 promotes the existing gate from --warn-only to HARD, now that the corpus is
            clean; change 4 adds the authoring-time step to agents/plan-agent.md.
Retires:    nothing. The gate exists; this raises its severity and adds the missing upstream step.
Cites:      IMP-0339, IMP-0336, IMP-0327
Residual:   The gate compares DECLARED ranges. A document that declares a range and then uses
            identifiers outside it is not detected, and a document with no declaration is only
            caught because all three current plans declare one. Change 3's HARD promotion is
            what makes a missing declaration block rather than warn -- that is the point of it.
```

```
CLUSTER C: tad-narrative-omits-an-already-existing-column  (x2: IMP-0337, IMP-0338)
Altitude:   CLASS — second instance, and both landed on the SAME TAD sentence, which is stronger
            evidence than two unrelated instances. IMP-0338 also carries `corrects` against
            IMP-0326, the finding that drove review 29's largest escalation.
Ladder row: "an agent had the information and still did the wrong thing" -> skill edit; plus
            "prefer the most mechanical home available" -> make the required enumeration one
            command instead of a manual scan.
Becomes:    change 5 adds the negative-claim rule to skills/how-to-verify-a-platform-contract.md;
            change 6 adds scripts/dump-entity-attributes.py so the rule is executable.
Retires:    nothing.
Cites:      IMP-0337, IMP-0338, and IMP-0326 as the finding both correct
Residual:   NO GATE, deliberately. A gate would have to read a negative claim out of prose and
            refute it against schema -- prose resolution, and the class of design review 29
            measured at 48% false positives before rejecting it. The mechanical half here is a
            TOOL that makes the correct method cheap, not a check that adjudicates prose. That
            leaves the rule dependent on an agent choosing to run it, and I am naming that
            rather than claiming coverage.
```

```
CLUSTER D: declared-policy-not-mechanically-enforced  (x1 here: IMP-0335; x14 overall)
Altitude:   INSTANCE, promoted to an agent-file rule — and it is codifying a practice already
            observed working, not inventing one.
Ladder row: "an agent had the information and still did the wrong thing" — inverted: the agent
            did the RIGHT thing with no rule authorising it, three times in one review.
Becomes:    change 7 adds a third branch to activation step 8: NARROW-AND-REPORT.
Retires:    nothing. It does NOT loosen the existing prohibition on substituting rule text; it
            is a named, evidenced exception with a stated tell.
Cites:      IMP-0335
Residual:   The tell separating a narrowing from a substitution ("a narrowing removes findings
            that would have been wrong and can NAME them") is a judgement, and no gate can read
            it. This stays prose and will stay prose. Its enforcement is that the deviation must
            appear in three places, one of which the reviewer reads.
```

```
CLUSTER E: learning-substrate-destroyed  (x1 here: IMP-0333; x23 overall)
Altitude:   INSTANCE, promoted to an agent-file rule in the same section as cluster D.
Ladder row: "the order of steps was wrong" — the amendment note was written BEFORE the work it
            claimed, so an interruption left a false completion claim instead of a to-do list.
Becomes:    change 8, folded into the same step-8 edit as change 7.
Retires:    nothing.
Cites:      IMP-0333
Residual:   Covered mechanically ONLY where the interrupted amendment leaves a gate block
            disagreeing with its body -- which is precisely cluster A's change 1. An amendment
            interrupted before it touches any counted figure leaves no mechanical trace, and the
            prose rule is the only control. Clusters A and E interlock here by design.
```

```
CLUSTER F: gate-reassures-wrongly  (x1 here: IMP-0343; x14 overall)
Altitude:   INSTANCE — one instance, but the mechanism is general and already has a precedent in
            the same agent file (step 7a re-hashes the build config for exactly this reason).
Ladder row: "the order of steps was wrong" + a read-path change
Becomes:    change 9 adds --warn-only to verify-improvement-log.py, matching 8 existing gates;
            change 10 extends build-agent.md step 7a to re-run the log check at manifest time
            and record the drift.
Retires:    nothing.
Cites:      IMP-0343
Residual:   I am NOT proposing a HARD re-check step at the end of the build config, and the
            reason is a correctness point rather than caution -- see §3, change 10. The residual
            is that the drift is RECORDED rather than blocking, so a batch trigger crossed
            mid-build is reported to lead-agent instead of stopping the package.
```

```
CLUSTER G: wrong-artefact-cited-as-evidence  (x2: IMP-0341 + IMP-0305)
Altitude:   CLASS — second instance, though IMP-0341's own author believed it was the first and
            proposed waiting for a third. The digest already records IMP-0305 in this class.
Ladder row: "second instance -> generalise", and the generalisation extends a rule that ALREADY
            EXISTS in the file IMP-0305 put it in.
Becomes:    change 11 extends the existing "evidence must come from the artefact that GOVERNS
            the claim" rule with liveness: a PROPOSED schema does not evidence a claim about a
            live artefact.
Retires:    nothing — it widens an existing rule rather than adding a row beside it.
Cites:      IMP-0341, IMP-0305
Residual:   NO GATE, and the measurement is why: the false claim lived in a DISPATCH BRIEF, an
            ephemeral prompt that no gate over tracked files can ever read. I measured 11
            candidate prose references to a key inside a contract/*.json file across the repo;
            adjudicated, roughly 3 are genuine key assertions and the rest are line-links to
            values. A gate would be a prose regex over a corpus of three. The marker convention
            IMP-0341 suggests stays deferred to a third instance, and §5 records the cheap
            retrofit size (6 fenced blocks in 3 documents) so that decision is informed.
```

```
CLUSTER H: bulk-identifier-remap-misses-compound-forms  (x1: IMP-0342)
Altitude:   INSTANCE — new class, one member, why_it_was_never_caught is "nothing". The ladder is
            explicit that this is a knowledge line, not a constraint, and that the second
            instance is what earns a gate.
Ladder row: "one instance, but the cause is general and a human needs to know it"
Becomes:    change 12, a renumbering procedure in skills/how-to-write-requirements.md.
Retires:    nothing.
Cites:      IMP-0342
Residual:   Entirely dependent on the procedure being read before a bulk remap. It pairs with
            cluster B because cluster B's resolution is what produced this defect -- the same
            renumbering. If a second bulk remap half-changes a compound form, the answer is a
            script that takes a mapping table, not another paragraph.
```

```
CLUSTER I: output-shape-defeats-the-reader  (x1 here: IMP-0334; x8 overall)
Altitude:   INSTANCE — a labelling defect in one script, with an exact fix.
Ladder row: "a tool could catch it mechanically" — here the tool IS the defect, so the fix is in
            the tool rather than a gate over it.
Becomes:    change 13, one line in generate-known-failure-modes.py.
Retires:    nothing.
Cites:      IMP-0334
Residual:   None worth naming. Zero false positives are structurally possible: the change makes
            two counts read from one set and labels what the difference is. Note that IMP-0334's
            own line references (552, 337, template 186) are stale -- the real lines are 643,
            400 and 213 -- which is itself a small instance of the class this review keeps
            meeting.
```

---

## 3. Proposed changes

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | gate widening | [`verify-review-document.py`](../../scripts/verify-review-document.py#L28) | Check `CLUSTER-COUNT`: every "→ N clusters" claim **in the header line or the fenced gate block** matches the count of distinct `CLUSTER` blocks | IMP-0332 | **YES, measured — 3 findings, 3 true, 0 false** across 33 documents |
| 2 | new gate | `scripts/verify-document-status-consistency.py` + SOFT build step | A citation line asserting a status opens the cited file and compares its own `Status:` line | IMP-0340, IMP-0344 | **YES, measured — 17 citations, 1 true positive, 0 false**; proven able to fail on the real corpus |
| 3 | gate promotion | [`build.yml` L216](../../config/revitalise-grant-automation-build.yml#L216) | `requirement-id-uniqueness` drops `--warn-only` and becomes HARD | IMP-0339, IMP-0336 | **YES** — corpus is clean today: 3 documents, 168 identifiers, 0 duplicated |
| 4 | agent file | [`plan-agent.md`](../../agents/plan-agent.md#L24) | Before writing an id-allocation declaration: run the gate, grep sibling declarations, take a block no sibling owns. A delta SDD declares `none` or takes a disjoint block — never continues its parent's sequence | IMP-0339 | N/A — instruction change, enforced downstream by change 3 |
| 5 | skill | [`how-to-verify-a-platform-contract.md` §2](../../skills/how-to-verify-a-platform-contract.md#L68) | A negative claim ("no column supplies X") must be backed by a full attribute enumeration of the target `Entity.xml`, never a remembered category list | IMP-0337, IMP-0338 | N/A — made executable by change 6 |
| 6 | script | `scripts/dump-entity-attributes.py` | Prints every `PhysicalName`, type, `MaxLength` and `IsSecured` for a named entity, so change 5's rule is one command | IMP-0337, IMP-0338 | **YES** — `--selftest`, and it is the command change 5 names |
| 7 | agent file | [`improvement-agent.md` step 8 L134](../../agents/improvement-agent.md#L134) | Third branch beside APPLY and WITHHOLD: **NARROW-AND-REPORT**, for a change whose intent survives and whose literal wording measures as wrong. Requires the forcing measurement, the deviation in `applied_by` **and** the document **and** the gate output, and states the tell | IMP-0335 | N/A — instruction change |
| 8 | agent file | [`improvement-agent.md` step 8 L154](../../agents/improvement-agent.md#L154) | The incremental-bookkeeping rule extends to the amend-a-draft path: reconcile the gate block **first**, write the amendment note **last**, as what has been folded in plus what remains | IMP-0333 | Partially — change 1 detects the trace an interrupted amendment leaves |
| 9 | script flag | [`verify-improvement-log.py`](../../scripts/verify-improvement-log.py) | Add `--warn-only` (print findings, exit 0), matching the 8 gates that already offer it | IMP-0343 | **YES** — `--selftest` plus a run under both modes |
| 10 | agent file | [`build-agent.md` step 7a L55](../../agents/build-agent.md#L55) | Beside the config re-hash: re-run the log check before writing the manifest, record start-vs-manifest counts in the manifest. An unread **blocker** appearing mid-build stops packaging; a batch-trigger crossing is recorded and reported | IMP-0343 | Partially — the manifest record is assertable; the trigger judgement is not |
| 11 | skill | [`how-to-verify-a-platform-contract.md` §2](../../skills/how-to-verify-a-platform-contract.md#L68) | Extend the governing-artefact rule with liveness: a proposed schema in `docs/improvements/` is not evidence about a live artefact in `contract/` | IMP-0341, IMP-0305 | N/A — no tracked-file corpus exists; see cluster G |
| 12 | skill | [`how-to-write-requirements.md`](../../skills/how-to-write-requirements.md#L140) | A "renumbering an allocated block" procedure: enumerate compound and range forms first, remap from an explicit mapping table, then re-grep for the old tokens **and** the compound shapes | IMP-0342 | N/A — procedure |
| 13 | script | [`generate-known-failure-modes.py` L643](../../scripts/generate-known-failure-modes.py#L643) | Derive the stdout lesson count from the same `live` set the header uses at [L400](../../scripts/generate-known-failure-modes.py#L400), and label it "N distinct teaching lessons (K rejected, excluded)" | IMP-0334 | **YES** — the two figures agree or they do not |

**Constraint budget: 0 of 3 used.** One gate widening, one new gate, one gate promoted from SOFT to
HARD, four agent-file edits, three skill edits, two script edits and one new helper script. No new
constraint rows. Thirteen changes, matching the thirteen rows above.

### Three of the four checks the queue asked for are dropped, and the measurement is why

IMP-0332 proposed four checks. **Only one is in the table above**, and the third drop was caught by
running the proposed check against this very document.

**Dropped — "the gate block's per-type Proposed counts sum to the numbered rows of the change
table". Measured: 18 findings, 18 false, 0 true.** My first implementation swept the neighbouring
`Digest:` line into the sum, producing arithmetic like `[0, 1, 3, 2, 0, 0, 1, 253, 26]`. That was
my bug. Fixing it does not save the check, because the premise is wrong: a review's `Proposed:`
line counts **retirements**, and retirements are not rows of the change table. Review 29's own
figures — 0 constraints, 5 gates, 5 knowledge/skill, 3 agent-file, 1 template, 2 retirements —
sum to 16 against 17 rows, and both numbers are correct. A check that fires on a correct document
teaches everyone to ignore it.

**Dropped — "every 'change N' prose reference resolves to a row of the change table". Measured:
6 findings, 0 true, 6 false.** Five are references to *another review's* change ("review 27's
change 9"); the sixth is my regex reading "2 violations without change 1, 0 with it" as a
reference to change 0. But the decisive objection is different, and it is that **the check would
not have caught the defect it was proposed for.** IMP-0332's item 4 is a note citing "change 15"
where the content described is change 17. Review 29 has seventeen rows, so 15 resolves. The check
is blind to the only instance in evidence.

**Dropped — "the Summary's decision count matches the bold numbered questions in the decisions
section". Measured: 1 true, 1 false — and the false one is this document.** On the 33 documents
that existed when I drafted it, this check scored 1 of 1: it found the still-live error in review
29's summary. Then I ran it against this review, and it fired on the sentence in my own Summary
that *describes* that error — "the last review's summary says it asks you seven questions; its
decisions section asks eight."

That is not a fixable bug, and the distinction matters. Check 1 had the same problem — it fired on
a paragraph narrating old wrong figures while explaining the correction — and check 1 was
**saveable** because a cluster count has two structural homes, a header field and a fenced gate
block, so scoping to those excluded prose entirely. **A decision count has no structural home; it
lives in prose, and reviews on this project discuss each other's figures constantly.** Any narrowing
would be a prose heuristic, and this gate's own docstring records the maintainers losing that fight
twice already, with `asks` matching inside `tasks` and `declined` firing on a retrospective.

So one check survives, on the one figure that has somewhere structural to live. §7 asks whether you
want the structural home built for the other one.

Both dropped counting checks are the shape review 29's own change 5 exists to catch, and this is
that obligation's second use — the first time it has rejected three designs out of four.

### Change 2 was proven able to fail against the real tree, not a fixture

The current tree measures **17 resolvable citations, 16 agreeing, 1 disagreement.** A clean run on
a corpus whose one known instance was already fixed is the "0 findings is the tell" case the agent
file warns about, so I reconstructed the original defect on a scratch copy of `docs/` — reverting
one `Status:` line to `DRAFT`, as it read for nine days — and the gate reported **3 disagreements**,
including both citations named in IMP-0340. It fails on the right things.

Two measurement bugs were found on the way, and both were mine: paths in this repo are
repo-relative rather than relative to the citing file, and `**Status:** **APPROVED 2026-08-16**`
puts the value in bold, so a regex demanding a letter where a `*` stands reports "no status line"
on a document that has one. Uncorrected, the first made the gate see 0 citations and the second
made it see 2 statusless files. Either would have shipped as a clean run.

### Change 10 is deliberately not a build-config step

The obvious form of IMP-0343's fix is a second `improvement-log-check` at the end of
[build.yml](../../config/revitalise-grant-automation-build.yml#L141). I am not proposing it, for
two reasons.

Every step in that config runs *before* build-agent writes the manifest, so a step cannot observe
manifest-time state — the same correctness point that moved review 29's change 14 out of the
config. And making it HARD at the end would fail a build that packaged correctly because another
session appended findings during it, which is precisely the event IMP-0343 recorded as friction
with no rework needed. The tempting workaround — `... || true` — is the
`gate-cannot-fail` pattern this repository has recorded **33 times**, and I will not propose it.

So the blocking semantics stay at step 3 where they are cheap and correct, and the addition is an
honest record of when the queue was actually clean. `--warn-only` (change 9) is what lets the
re-check run without a red build, and it is the flag 8 other gates already carry.

---

## 4. Retirements

**No retirements, and the audit was run.** All ten retired rows were checked for a fired
reinstatement condition; none has one. Derived rather than typed — **10 retired, 80 live** — via
`grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l`, and
`verify-derived-counts.py` reports all **8 registered claims** matching.

**The two standing candidates are named for the third review running, so they do not go quiet.**
[C-TECH-011](../../constraints/technology/technology-constraints.md#L155) still has no
verification — its `Verify By` names a CI grep that has never been a step in any build config —
and [C-TECH-012](../../constraints/technology/technology-constraints.md#L156) still has neither a
threshold nor a tool to read one. Both are already marked retired; what is outstanding is the
decision in §5 about whether either should be reinstated with a real check or left retired
permanently.

**Nothing this review adds makes a live row redundant.** Change 2's new gate was checked against
[`verify-review-document.py`](../../scripts/verify-review-document.py#L28)'s existing
`STALE-HEADER` check for overlap: that one compares a *review document's* own AWAITING claim
against its own Applied section, while change 3 compares a *delivery document's* citation against
a different file's header. Different corpora, different facts. Keeping both is not duplicate
coverage.

---

## 5. Findings left unprocessed, and what this dispatch could not fix

**All 13 findings in the batch that triggered this review are processed. Three that arrived
during the drafting are deferred, and this is why.**

`IMP-0345`, `IMP-0346` and `IMP-0347` were appended at 12:38 by the `test-agent` dispatch running
alongside this one, after every measurement in §3 was complete. **That dispatch is still live, and
its findings are about a flow it is actively fixing.** Folding in a running dispatch's findings is
how a review processes finding N while finding N+1 from the same source contradicts it — the
hazard `IMP-0338` demonstrated one day ago by correcting `IMP-0326`, which is the very finding that
drove review 29's largest escalation. Their remedies target `scripts/`, `agents/` and `templates/`,
none of which this dispatch is fenced off from, so this is a sequencing judgement rather than a
scope limit.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| `IMP-0345` | `platform-contract-guessed-not-groundtruthed` (x41) | **Guards a live P1** — an error-branch `Response` that also fires on every successful run. Its proposed check 6 is an exact shape check over flow definitions and needs measuring against all five flows, which is the delivery thread's corpus, not this review's | the test dispatch reports its gate |
| `IMP-0346` | `no-assertion-on-shipped-content` (x13) | Its remedy is a skill-table edit in `development-agent.md` for the step that fixes a test-report defect — the same step `IMP-0345` is about | with `IMP-0345` |
| `IMP-0347` | `approved-document-internally-inconsistent` (x7) | Cluster A's class, but its instance is a one-sided assumption claim — prose semantics, not a counting property. It confirms cluster A's residual (c) rather than altering changes 1–2 | with `IMP-0345` |

**I recommend routing `IMP-0345` promptly and not waiting for a batch.** It is a P1 that every
static gate in the build passes over: the packer, the hosted Solution Checker and the
flow-definition gate all report clean, because that gate proves a failure path *exists* and never
that it is correctly bounded. It is not a blocker by severity, so it will not summon a review on
its own.

**After this review applies, the queue sits at 3 unread — below the batch trigger of 10.** No
re-trigger, and no second pass over settled work.

What follows is scope this review deliberately did not take.

| Item | Why not done here | Who closes it |
|---|---|---|
| `IMP-0344` — the live status contradiction | Both files are `trustee-portal-visual-refresh`'s, and this dispatch was fenced off from `docs/architecture/` and `docs/development/` for that feature | architect-agent |
| `IMP-0337`'s document half | Already done by the delivery thread — `verify-tad-coverage.py` is green | closed |
| The 38 `reviewer-deferred` entries | Each carries a reason a human accepted. Re-deriving them is the defect `IMP-0183` records | — |
| `IMP-0274` — a deferral with no `revisit_when` | Flagged by the gate every run; it is a decision to never do it, which needs a human | reviewer |
| A **live `lost-deferral` failure** in review 28 at [line 39](2026-08-25-improvement-review.md#L39) | `verify-review-document.py` is RED on the corpus today: review 28 defers a decision to its section 5 and section 5 does not carry it — the exact `IMP-0302` shape the gate was built for. It is a settled, approved document, so editing it is a decision rather than a fix, and no finding in this batch names it | reviewer |

**States excluded from this review's scope, per activation step 2:** 38 `reviewer-deferred`, 0
`awaiting-approval`, 0 `already-fixed`, 0 `approved-not-applied`. No entry is parked at another
review's gate, so nothing here is waiting on a keyword other than this document's.

**The commercial residual, which is not mine to resolve.** `IMP-0341` establishes that
`contract/wbs.json` records no mapping from a feature slug to WBS task ids — the key it was
briefed to read does not exist, and the note quoted to it lives inside a *proposed* schema in a
design document. The consequence is that the form-field corrections work is **genuinely
unrecorded** commercially rather than recorded-as-unquoted, which is a
[C-COM-002](../../constraints/commercial/commercial-constraints.md#L35) question for
`commercial-agent`. I am not restating any hours figure and I am not deciding it.

---

## 6. Verification executed for this review

**Level reached: V1 for everything proposed, and nothing has been applied.** No live environment
was touched; no PowerShell was written, so no provisioning contract suite applies.

| Check | Result |
|---|---|
| `verify-improvement-log.py --check` | 12 unread at the trigger → **16 now** (`IMP-0344` mine, 3 from the test dispatch); `IMP-0338`'s `corrects` warning is cleared by this review's stamp |
| `verify-improvement-log.py` (schema) | **OK — 344 entries** (54 NEW, 289 APPLIED, 1 REJECTED) |
| `verify-review-document.py --only` on this document | **OK** — every section reference resolves, every deferral finds its question, no status header contradicts an applied section |
| `verify-improvement-log.py` (append validation) | **Correctly refused** `IMP-0344`'s first append — `appended_by` named this document before it existed |
| `verify-requirement-id-uniqueness.py` | **OK** — 3 documents, 168 identifiers, 0 allocated twice |
| `verify-tad-coverage.py` | **OK** — 148 column specs, 6 deliverable-now items all naming a real column, 0 violations |
| `verify-derived-counts.py` | **OK** — 8 registered claims all match |
| `generate-known-failure-modes.py --check` | **current** — 340 entries (pre-append) |
| Change 1 (`CLUSTER-COUNT`), real corpus | **3 findings / 3 true / 0 false** across 33 review documents, this one included |
| Dropped check — Summary decision count | **2 findings / 1 true / 1 false** — the false one is this document narrating the true one → dropped |
| Dropped check — per-type `Proposed:` sums | **18 findings / 0 true / 18 false** → dropped |
| Dropped check — `change N` resolution | **6 findings / 0 true / 6 false**, and blind to its own instance → dropped |
| Change 2, real corpus | **17 citations, 1 true positive, 0 false** |
| Change 2, negative test on a scratch tree | **3 findings** — reproduces IMP-0340's original defect |
| `verify-review-document.py` over the whole corpus | **FAILED — 1 lost-deferral** in `2026-08-25-improvement-review.md:39`. Pre-existing, not caused by this review, and not fixed here; see §5 |
| Cluster G candidate gate, real corpus | **11 candidates, ~3 genuine** → gate declined, skill rule instead |
| `IMP-0338`'s schema claim | **Confirmed** — `rev_breakstart` L1268, `rev_breakend` L1284, `rev_breaklocation` L1252 |
| `IMP-0334`'s diagnosis | **Confirmed exactly** — `IMP-0290` is the log's only `REJECTED` entry |

~~**Not verified, and it is the honest limit.** None of the thirteen proposed changes exists on
disk, so no `--selftest` has been run against a real implementation — the measurements above were
made with throwaway probes in a scratch directory, which is what proves a *design* rather than a
shipped gate.~~ **Superseded 2026-08-26 by §10.** Changes 1, 2, 6, 9 and 13 were re-measured
against the corpus at application time, as this paragraph required — and **two of the five did not
reproduce the figures above.** The re-measurement is in §10; the numbers there supersede every
figure in this section. The rest of the paragraph stands: nothing here was executed against a live
environment, and `IMP-0344` names a defect only its document's owner can settle.

---

## 7. What you need to decide

**Nothing blocks this review. Five things want an answer.**

**1. Should the requirement-id gate become HARD now, or stay a warning?**

I recommend HARD, and change 3 proposes it. The corpus is clean for the first time — 168
identifiers, none allocated twice — so promoting it costs nothing today and blocks the next
collision instead of warning about it. The gate has been SOFT through all three instances of this
class and never blocked anything.

The trade-off: a new plan document with no id-allocation declaration will fail the build rather
than warn. That is the intent, but it means `plan-agent` must always declare, and change 4 is what
makes that a step rather than a habit.

**2. Two retired constraints have been named as candidates in three consecutive reviews. Reinstate
or close them permanently?**

[C-TECH-011](../../constraints/technology/technology-constraints.md#L155) (no `TODO`/`FIXME` above
Test) needs one grep step in a build config to become real.
[C-TECH-012](../../constraints/technology/technology-constraints.md#L156) (complexity threshold)
needs a number chosen and a linter rule, and no static-analysis tool is installed.

Naming them a fourth time is not useful. Either is a small piece of work; the question is whether
either rule is one you actually want enforced, because if not, the honest outcome is to record
them as permanently retired and stop listing them.

**3. Who settles the trustee-portal architecture document's status?**

A dev summary cites it as approved at revision 2; the document says draft at revision 2. One is
wrong. I found it by measurement and left both files alone, because they belong to the delivery
thread this review was fenced off from — and because the gate can report the contradiction but
cannot know which side is stale.

This matters slightly more than a header usually would: a test gate on that feature is live, and a
test report citing an approved TAD that says draft is the shape that produced the last instance of
this class.

**4. Should the "proposed schema" marker convention be built now or wait for a third instance?**

I recommend waiting, and cluster G explains why: the failure happened in a dispatch brief, which
no gate over tracked files can read. But the retrofit is genuinely cheap if you want it now — **6
fenced yaml/json blocks across 3 documents** in `docs/improvements/` would need a
`# PROPOSED — not live` header line, and after that a gate requiring it is exact rather than a
prose regex.

**5. Two figures this class keeps getting wrong now have no check at all. Give them a structural
home?**

A review's decision count and its "change N" references are both hand-typed, both were wrong in the
last review, and both proposed checks failed measurement — not because the checks were badly built
but because the figures live in free prose, where narration and claim are indistinguishable.

The fix, if you want one, is to stop putting them in prose: add a `Decisions:` line to the gate
block in [`improvement-review-template.md`](../../templates/improvement-review-template.md), the way
`Findings processed:` already works, and the same counting check that succeeded for clusters becomes
available for decisions.

I have not proposed it, because it changes the shape of every future gate block and that is your
call rather than mine. The cost of leaving it: this class is at seven instances and two of its
recurring shapes stay uncovered.

---

## 8. Digest impact

**Measured on the log as it stands now, not predicted from the batch.** Four entries arrived while
this was drafted — `IMP-0344` from this session, three from the test dispatch — so the "before"
column is the state at the trigger and the "now" column is what a regeneration would write today.

| | At the trigger | Now |
|---|---|---|
| Log entries | 340 | **344** |
| Distinct teaching lessons | 339 | **343** |
| Recurring classes (x≥2) | 34 | **35** |
| Digest lines | 495 | ~500 |
| Correction markers rendered | 3 | **4** — `IMP-0338` corrects `IMP-0326` |

Classes this review's own findings advance: `approved-document-internally-inconsistent`
**x5 → x7**, `tad-narrative-omits-an-already-existing-column` **x2** (new row, at the
generalisation threshold), `wrong-artefact-cited-as-evidence` **x2**, and
`bulk-identifier-remap-misses-compound-forms` **x1** (below it, which is why cluster H is a
knowledge line). The one new recurring row is `tad-narrative-omits-an-already-existing-column`
reaching two.

**Hold me to the measurement, not to this table.** Review 29 predicted a digest delta of 0–2 lines
and measured 6, because correction markers it had not foreseen rendered. Section 9's figures are
the ones re-derived at application.

---

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-26-improvement-review.md

Findings processed: 13 unread  →  9 clusters   (3 later arrivals deferred, named in §5)
Regression check:   17 prior changes audited, 3 classes recurred
Proposed:           0 constraints (cap 3), 1 gate widening + 1 new gate + 1 promoted SOFT→HARD,
                    4 agent-file edits, 3 skill edits, 1 new script + 2 script edits,
                    0 retirements   — 13 changes, matching the 13 rows of §3
Altitude calls:     4 generalised from instance to class, 5 left at instance with a named reason
                    3 of 4 proposed checks DROPPED on measurement (0/18, 0/6, and 1/2 true)
Decisions:          5, none blocking
Digest:             will regenerate — 343 teaching lessons, 35 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 10. Applied

**`Approve improvements` received 2026-08-26. All 13 changes are on disk; all 13 findings are
dispositioned — 12 `APPLIED`, 1 (`IMP-0344`) deliberately left open with a recorded reason.**

**Re-verification ran first, per activation step 8, and nothing was disproved.** The only `corrects`
edge in the log is `IMP-0338` → `IMP-0326`, which is cluster C's own basis rather than a
contradiction of it; its schema claim was re-read on disk (`rev_breakstart` L1268, `rev_breakend`
L1284, `rev_breaklocation` L1252, all `IsSecured=0`). None of the three later arrivals named in §5
carries `corrects` against anything processed here. **Nothing was withheld.**

### What landed

| # | Change | Landed as | Measured at application |
|---|---|---|---|
| 1 | `CLUSTER-COUNT` check | [`verify-review-document.py`](../../scripts/verify-review-document.py#L38) | **NARROWED** — see below. 3 findings / 3 true / 0 false across 35 documents |
| 2 | new status-consistency gate | [`verify-document-status-consistency.py`](../../scripts/verify-document-status-consistency.py#L1) + SOFT step at [build.yml L201](../../config/revitalise-grant-automation-build.yml#L201) | **CORRECTED** — see below. 16 resolved citations / 1 true / 0 false; negative test on a scratch tree reproduces `IMP-0340` at 3 findings |
| 3 | `requirement-id-uniqueness` → HARD | [build.yml L239](../../config/revitalise-grant-automation-build.yml#L239) | Corpus clean, re-verified immediately before promoting: 3 documents, 168 identifiers, 0 allocated twice, exit 0 |
| 4 | id-allocation authoring step | [`plan-agent.md` step 4a](../../agents/plan-agent.md#L31) | N/A — instruction; enforced downstream by change 3 |
| 5 | negative-claim rule | [`how-to-verify-a-platform-contract.md`](../../skills/how-to-verify-a-platform-contract.md#L105) | N/A — made executable by change 6 |
| 6 | attribute enumerator | [`dump-entity-attributes.py`](../../scripts/dump-entity-attributes.py#L1) | `--selftest` OK; `--all --grep prefer` surfaces all three columns three findings said did not exist |
| 7 | `NARROW-AND-REPORT` branch | [`improvement-agent.md` step 8](../../agents/improvement-agent.md#L150) | N/A — and **used twice in this very application** |
| 8 | amend-a-draft ordering | [`improvement-agent.md` step 8](../../agents/improvement-agent.md#L176) | N/A — mechanical half is change 1 |
| 9 | `--warn-only` | [`verify-improvement-log.py`](../../scripts/verify-improvement-log.py#L1993) | Same log exits 1 without the flag and 0 with it, asserted as a fixture — 60 fixtures OK |
| 10 | manifest-time re-check | [`build-agent.md` step 7b](../../agents/build-agent.md#L78) | Partially — the manifest record is assertable; the trigger judgement is not |
| 11 | liveness half | [`how-to-verify-a-platform-contract.md`](../../skills/how-to-verify-a-platform-contract.md#L88) | Re-verified: `contract/wbs.json` has no `deliverable_map` and 0 occurrences of the slug |
| 12 | renumbering procedure | [`how-to-write-requirements.md`](../../skills/how-to-write-requirements.md#L140) | Both greps verified working — 93 and 80 hits; 0 surviving half-remaps |
| 13 | one lesson count | [`generate-known-failure-modes.py`](../../scripts/generate-known-failure-modes.py#L640) | stdout **343** and the header it writes **343** — agreeing for the first time |

**One unplanned edit, and a gate found it.** `verify-derived-counts.py` went red the moment change
2 landed: [`improvement-agent.md`](../../agents/improvement-agent.md#L314) said `scripts/` holds 43
`verify-*.py` checks and it now holds 44. Corrected, and the registry is green at 8/8. That is a
registered derived count doing exactly its job on the same day it was cited.

### The two deviations, per activation step 8's third branch

Both are **narrowings, not substitutions** — each names the specific false positives it removes,
which is the tell change 7 states.

**Change 1 was NARROWED.** The draft measured "3 findings / 3 true / 0 false across 33 documents".
The shipped implementation of the same wording measured **5 findings / 3 true / 2 false across 35**.
The two false positives, both correct documents:

- `2026-08-19-improvement-review-3.md` states 5 clusters and carries 6 `CLUSTER` lines, because its
  Addendum **re-quotes** one block verbatim after the reviewer answered an open decision.
- `2026-08-21-improvement-review-2.md` states 6 and carries 7, the seventh being a class **carried
  forward with `(x0` new members** — not one of the clusters the batch produced.

Two narrowings — dedupe by label, exclude `(x0` — removed both **by name** and left both true
positives standing. Re-measured: **3 / 3 / 0**. Note that "the count of **distinct** `CLUSTER`
blocks" is the approved §3 wording; the raw count was the deviation, and the narrowing restored it.

**Change 2 was CORRECTED before wiring, and the "0 findings is the tell" rule is what caught it.**
Its first implementation resolved **5** citations and reported a **clean run** — over `IMP-0344`'s
own live instance. This repository writes every path in a code span
(`` `docs/…-architecture.md` `` (APPROVED, Revision 2)) and the regex did not allow a closing
backtick, so the gate was blind to almost every citation it exists to read. With the backtick
allowed: **16 resolved, 1 finding, 1 true positive.** The draft's §6 recorded two measurement bugs
it had already fixed in its probe and this was a third, present only in the shipped artefact.

**The lesson both share is logged as `IMP-0348`:** a draft's corpus figures are a property of the
throwaway probe, not of the gate that ships, and re-measuring the shipped artefact is the only
thing that closes the gap. Half the value of the corpus obligation is in *where* it is run.

### Findings dispositioned

| Finding | Status | By |
|---|---|---|
| `IMP-0332` | `APPLIED` | change 1 (narrowed) |
| `IMP-0333` | `APPLIED` | change 8 |
| `IMP-0334` | `APPLIED` | change 13 |
| `IMP-0335` | `APPLIED` | change 7 |
| `IMP-0336` | `APPLIED` | change 3 — its `revisit_when` condition has occurred |
| `IMP-0337` | `APPLIED` | changes 5 + 6; document half already closed, `verify-tad-coverage.py` green |
| `IMP-0338` | `APPLIED` | changes 5 + 6 |
| `IMP-0339` | `APPLIED` | changes 3 + 4 |
| `IMP-0340` | `APPLIED` | change 2 (corrected) |
| `IMP-0341` | `APPLIED` | change 11 |
| `IMP-0342` | `APPLIED` | change 12 |
| `IMP-0343` | `APPLIED` | changes 9 + 10 |
| `IMP-0344` | **`NEW`, deferred with a reason** | change 2 wired the gate; the live contradiction is `architect-agent`'s |

**`IMP-0344` was NOT closed, on its own instruction:** *"It stays open after that gate is wired,
because wiring the gate does not decide WHICH side is wrong."* The gate now reports it as its one
true positive. Closing it on a needle pointing at a sentence this review wrote is `IMP-0208`'s
defect exactly, over a live contradiction on a feature whose test gate is running.

**`IMP-0345`, `IMP-0346` and `IMP-0347` were not processed in this review** and remain `unread`,
per §5 and the reviewer's explicit instruction — they are out of scope here and belong to the next
review. `IMP-0347` still raises a citation-stamp warning, because §2's cluster A discusses it by
name while cluster A's residual (c) explains why it changes nothing; stamping it would claim this
review processed it, so the warning is left standing as the honest state. It is a warning, not an
error — the log gate exits 0.

### Queue state after this application

| | Before | After |
|---|---|---|
| `verify-improvement-log.py --check` | **FAILED** — 1 problem (batch trigger, 16 pending) | **OK, exit 0** |
| unread | 16 | **3** — the three later arrivals §5 defers, and nothing else |
| `APPLIED` | 289 | **301** |
| Digest | 340 entries, 339 lessons, 495 lines | **345 entries, 344 teaching lessons, 495 lines** |
| Retired / live constraints | 10 / 80 | **10 / 80** — no retirements, as proposed |

**`C-TECH-061` is clear and the batch trigger no longer fires**, which is what the held
`trustee-portal-visual-refresh` build was waiting on.
