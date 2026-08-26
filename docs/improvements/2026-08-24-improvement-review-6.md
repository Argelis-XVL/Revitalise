# Improvement Review 26 — 2026-08-24

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 5 `NEW` (`unread`) → 5 clusters
**Trigger:** blocker escalation — one unread blocker, [IMP-0285](../../logs/improvement-log.jsonl#L282), routed immediately per [WORKFLOW.md → Processing triggers](../../agents/WORKFLOW.md#L214)
**Status:** ~~REVISION 1, 2026-08-25. AWAITING `APPROVE IMPROVEMENTS`. Nothing in this document is on disk.~~
**APPLIED 2026-08-25** on `Approve Improvements` from the reviewer. Seven of eight changes are on disk; **change 5 was WITHHELD at application because its premise failed re-verification** — see §10. Measured outcomes, the three findings this application produced, and the corrections to this document's own §6 verification table are all in §10.
**Why it was revised:** the reviewer held this document back rather than approving it, because [review 27](./2026-08-25-improvement-review.md) found that one of its dispositions was contradicted by a finding logged after it was drafted. Review 27 has since been **applied in full**, which moved most of the files this document cites. Everything changed in this revision is marked **REVISED** and listed in §0.
**Scope note:** the sixth review dated 2026-08-24, after [21](./2026-08-24-improvement-review.md), [22](./2026-08-24-improvement-review-2.md), [23](./2026-08-24-improvement-review-3.md), [24](./2026-08-24-improvement-review-4.md) and [25](./2026-08-24-improvement-review-5.md). Read after [review 27](./2026-08-25-improvement-review.md), which is already on disk.
**WBS:** the build defect behind cluster A was met while packaging [task 0.4](../../contract/wbs.json); everything proposed here is system work, not billable ([C-COM-002](../../constraints/commercial/commercial-constraints.md#L35))

---

## Summary

**Two of this repository's HARD rules have never been enforced automatically, and finding that is worth more than the nine minutes the blocker cost.** The check that failed the build lives only inside the Pester suite at step 41 of 46, and the same is true of the workflow validator. Both rules name CI as their enforcement, and CI has never fired on this project.

> **ANNOTATION, 2026-08-25 (at application).** The last clause of that paragraph — *"CI has never fired on this project"* — **did not survive re-verification and is left standing only because it is what was approved.** `ci.yml` triggers on `main` and `project-management` as well as `feature/**`, and both exist with pushed commits. The claim is unproven, `gh` is unauthenticated so it cannot be settled here, and **change 5 was withheld for it**. The first two sentences are unaffected and are what changes 1 and 2 were applied on. See §10 and [IMP-0308](../../logs/improvement-log.jsonl#L305).

**The fix is structural rather than a rule about remembering:** two cheap steps early in the build, plus a check that makes it impossible for a gate to hide inside the test suite again. Both are measured against the real tree, not only fixtures.

**On the question this dispatch asked:** the `corrects` mechanism added yesterday does **not** cover this case, and could not have. It only speaks about a finding a review has already processed.

**What needs you:** three gate/script changes, four skill edits, two constraint amendments, no new constraints, and two decisions — the retirement obligation, and whether the `corrects` rung should stop reading an optional field.

**REVISED — one conclusion in the original draft was wrong.** It said [IMP-0278](../../logs/improvement-log.jsonl#L275) needed no change because a first change order now exists to pattern-match. [IMP-0288](../../logs/improvement-log.jsonl#L285) was logged hours later and records that that change order's own estimate was wrong and had to be resized. The class recurred before this document reached its gate; the change it declined is now on disk, applied by review 27.

---

## 0. What changed in revision 1

| Section | What changed |
|---|---|
| §1 | Two rows added to the regression table: [IMP-0288](../../logs/improvement-log.jsonl#L285)'s recurrence, and the fact that this document's own change 3 would have been **blind** to it |
| §2 | The "one cluster produced no change at all" paragraph is withdrawn and replaced. Cluster B's residual is no longer hypothetical — it has an instance |
| §3 | Changes 4, 7 and 8 re-anchored: review 27 edited all three target files, so the original line references are stale. Change 6's regeneration now follows review 27's |
| §4, §6 | Re-measured against today's tree. Constraint rows **80 / 10**, not 79 / 10; the log is at **298** entries, not 282 |
| §5 | The change-order decision is answered differently, and a second decision is added on the `corrects` rung's altitude |
| §8, §9 | Digest prediction and gate figures rebased |

**Nothing in the eight proposed changes was withdrawn, and no new change was added.** Every premise was re-checked against the current tree and all eight still hold — the rung is still unwritten, the two gates are still reachable only inside `unit-tests`, and both HARD rows still name a dead CI path.

---

## 1. Regression check — did review 25's changes work?

[Review 25](./2026-08-24-improvement-review-5.md) was applied yesterday evening. Its seven applied changes are audited below.

| Prior change | Class it targeted | Recurred? | Verdict |
|---|---|---|---|
| [C-TECH-073](../../constraints/technology/technology-constraints.md#L143) (HARD) | a metadata write guessed, not ground-truthed | no | **Worked.** No finding in that class since |
| [verify-metadata-write-verbs.py](../../scripts/verify-metadata-write-verbs.py), wired HARD as [`metadata-write-verbs`](../../config/revitalise-grant-automation-build.yml#L555) | same | no | **Worked, and it ran.** Executed standalone and in the full 46/46 sequence |
| [`constraint-verifiers`](../../config/revitalise-grant-automation-build.yml#L578) wired SOFT | a gate reachable only by hand | no | **Worked** — it now runs on every build |
| [check_corrections()](../../scripts/verify-improvement-log.py#L1295) | a correction landing after a review's draft | **YES — within hours** | **Right rule, wrong scope.** See below |
| [improvement-agent.md activation step 8](../../agents/improvement-agent.md#L127) | same | **YES** | Same gap; it is the prose half of the same rung |
| [testing-tools.md](../../knowledge/technology/testing-tools.md#L244) generalised | guessing a metadata write contract | no | Worked |
| [C-TECH-042](../../constraints/technology/technology-constraints.md#L84) amendment | an all-`EXISTS` run read as proof | no | Worked |
| **REVISED —** this document's own disposition of [IMP-0278](../../logs/improvement-log.jsonl#L275) | change-order sizing with no precedent | **YES** | **Contradicted by [IMP-0288](../../logs/improvement-log.jsonl#L285)**, logged after this draft. See below |

**REVISED — the disposition that has to change.** This draft concluded that [IMP-0278](../../logs/improvement-log.jsonl#L275) needed nothing, because [CO-001.md](../../contract/change-orders/CO-001.md) now exists as a pattern and a template built from one instance is speculative. [IMP-0288](../../logs/improvement-log.jsonl#L285) records that CO-001's own estimate — sized by analogy to two comparable contracted tasks before any requirement text existed — undercounted the work badly enough to need a formal resize, and that a manual follow-up dispatch, not any gate, is what caught it. The class is `x2`, so the altitude rule forbade leaving it as a note.

**That change is already on disk.** Review 27 applied it as its change 9: [agents/commercial-agent.md L49](../../agents/commercial-agent.md#L49) now requires commercial-agent to re-open a change order whose estimate was deferred to a later design document the moment that document lands. **Approving this document as originally drafted would have closed a finding whose class had already recurred** — which is why the reviewer held it.

**REVISED — and this document's own new rung would not have caught it.** Change 3 below extends [check_corrections()](../../scripts/verify-improvement-log.py#L1295) to fire when an entry's `corrects` field names a target still unread. [IMP-0288](../../logs/improvement-log.jsonl#L285) carries **no `corrects` field**, so the rung would have stayed silent about the one finding that disproves this review. That is the same optional-field hole this document already names as cluster B's residual — stated there as a possibility, and now with an instance. It does **not** invalidate change 3, which fixes a real and different gap; it does mean the rung is patched twice and still reads a field nobody is obliged to set. §5 puts that to you rather than proposing a third patch, because instance 33 of the largest gate class in this project is exactly where the altitude rule says stop.

**The `corrects` rung exists, it ran, and it was structurally unable to see the pair it was built from.** [check_corrections()](../../scripts/verify-improvement-log.py#L1295) reports a correction only when the corrected finding **has already been processed by a review document** — the line `if not docs: continue`. At the moment the build failed, no review had processed [IMP-0276](../../logs/improvement-log.jsonl#L273), so the rung was silent about the exact pair on which it had been modelled the previous evening.

That is the third row of this agent's own regression table: a gate that exists and did not fire is mis-scoped, and that is a `gate-cannot-fail` finding in its own right. It is instance 33 of the largest gate class in the project.

**It is a scope gap, not a defect.** The rung answers *"has something been disproved since I drafted this?"* — the re-verification question review 25 was convened by. The case here is different and earlier: *"the code fix landed and nobody moved the finding's own queue entry."* Change 3 adds it; nothing in the existing rung is withdrawn.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: learning-substrate-destroyed  (x1 BLOCKER: IMP-0285, x20 overall)
Altitude:  CLASS, and the class is NOT the one the finding names. The proposed
           change is a single step in a single config -- an instance patch. The
           property behind it is that a HARD assertion needing no toolchain was
           reachable only INSIDE an expensive, nested step, and that has happened
           before: IMP-0132 recorded `unit-tests` carrying both the test-count gate
           and the coverage gate, and was fixed by splitting `coverage-threshold`
           out. Two instances of "a gate hides inside unit-tests", both in the same
           step, forbid a third instance patch under the altitude rule.
Ladder row: "the ORDER of steps was wrong" + "a tool could catch it mechanically"
Becomes:   two new early steps in the build config (the instance fix, free), PLUS
           check_suite_gates_are_steps() in verify-build-config.py -- the exact
           INVERSE of check_negative_tests(), which already asserts that every gate
           step has a test in the suite. This asserts that every gate script in the
           suite has a step in the config.
Retires:   nothing -- no instance gate existed for this property.
Cites:     IMP-0285, IMP-0132, IMP-0165, IMP-0175
Residual:  It reads `Invoke-Python 'verify-*.py'` out of the suite. A gate the suite
           exercises through some other call shape, or one that lives in no suite at
           all, is invisible to it. It also says nothing about WHERE in the config a
           step sits -- only that it exists.
```

```
CLUSTER B: gate-cannot-fail  (x1: the regression finding above; x32 overall)
Altitude:  SCRIPT. The rung shipped yesterday and its scope was set by the incident
           that produced it. This is the adjacent case, one day later.
Ladder row: "a tool could catch it mechanically"
Becomes:   a second case in check_corrections() + the `corrects` field documented in
           the schema skill, where it has never appeared.
Cites:     IMP-0285, IMP-0275, IMP-0169
Residual:  REVISED -- THIS RESIDUAL NOW HAS AN INSTANCE, AND IT IS THIS REVIEW'S OWN.
           It reads the `corrects` FIELD. An agent who fixes the code and logs a
           fresh entry WITHOUT setting `corrects` is invisible to it, exactly as
           IMP-0169's earlier fix was invisible here because `evidence_grep` is
           optional and IMP-0276 carries none. IMP-0288 is that agent: it carries no
           `corrects`, it contradicts this document's disposition of IMP-0278, and
           change 3 would have said nothing. The shape that WOULD have caught it is
           `class_instance_of`, which is mandatory -- an entry sharing a class with a
           finding a pending review concluded "no change needed" about. That is a
           different rung, not a third patch to this one, and it is a section 5
           decision rather than a change I am proposing here.
```

```
CLUSTER C: escalation-trigger-conflates-request-and-document-state  (x1: IMP-0280)
Altitude:  KNOWLEDGE LINE, and the intent it needs is already written down elsewhere.
           skills/how-to-intake-external-documents.md L53 already says MISSING items
           at THIS intake count toward the trigger. models.yml and the model-selection
           skill say only "more than 3 open questions", which a long-lived SDD's
           backlog satisfies permanently.
Ladder row: "one instance, cause is general, a human needs to know it"
Becomes:   one clause in config/models.yml and one in skills/how-to-select-a-model.md.
Cites:     IMP-0280
Residual:  Prose. No gate can count "questions this request raises".
```

```
CLUSTER D: open-question-answerable-from-repo  (x1: IMP-0284)
Altitude:  KNOWLEDGE LINE, one step in an existing procedure.
Ladder row: "one instance, cause is general, a human needs to know it"
Becomes:   a clause in the intake skill's step 2, before a section is classed MISSING.
Cites:     IMP-0284
Residual:  A grep finds a concept named the same way. A concept the architecture
           document calls something else stays invisible.
```

```
CLUSTER E: spec-field-list-not-verified-against-implementation  (x1: IMP-0279)
Altitude:  KNOWLEDGE LINE. First instance, observable only at V4, and the mechanical
           home does not exist: a category-level FR carries no field list for a gate
           to diff against.
Ladder row: "one instance, cause is general, a human needs to know it"
Becomes:   one trap in skills/how-to-write-requirements.md.
Cites:     IMP-0279
Residual:  THE DELIVERY HALF IS NOT MINE AND IS NOT FIXED. Section 5 names it.
```

**REVISED — the cluster that produced no change now has one, and it is already applied.** The original text read: *"[IMP-0278](../../logs/improvement-log.jsonl#L275) asked for a change-order template because no prior change order existed to pattern-match. One does now — [CO-001.md](../../contract/change-orders/CO-001.md) — so the gap the finding records has been closed by the work that recorded it."*

**That was true about the template and wrong about the gap.** A pattern to copy is not what was missing; what was missing was anything that forces a deferred estimate to be revisited when the design it was deferred to arrives. CO-001 proved that by getting its own estimate wrong ([IMP-0288](../../logs/improvement-log.jsonl#L285)), and by needing a human to notice. Review 27 applied the rule at [agents/commercial-agent.md L49](../../agents/commercial-agent.md#L49).

**So [IMP-0278](../../logs/improvement-log.jsonl#L275) closes on that change rather than on nothing** — `applied_by` naming review 27's change 9, since one rule now covers both instances. The template question is separate and still open; §5 answers it.

---

## 3. Proposed changes

| # | Type | Target | What it does | Can it fail? |
|---|---|---|---|---|
| 1 | **build config** | two steps after [pipeline-config-preflight](../../config/revitalise-grant-automation-build.yml#L121) | `improvement-log-check` (`verify-improvement-log.py --check`) and `workflow-syntax` (`verify-workflow-syntax.py --root .github`). Both are dependency-free and run in about a second | **YES** — `improvement-log-check` exits 1 on this tree right now, on the blocker that convened this review |
| 2 | **script rung** | `check_suite_gates_are_steps()` in [verify-build-config.py](../../scripts/verify-build-config.py#L560) | Every `verify-*.py` that [BuildGates.Tests.ps1](../../src/tests/build/BuildGates.Tests.ps1#L772) exercises must be invoked by a step in the config. Exemptions live in a dict with a stated reason, mirroring [GATE_EXEMPT](../../scripts/verify-build-config.py#L117) | **YES, measured** — 2 violations against today's real config; 0 after change 1 |
| 3 | **script rung** | [check_corrections()](../../scripts/verify-improvement-log.py#L1295) | Adds the missing case: an entry carrying `corrects` naming a target still `unread`. Warns; does not close it, and says explicitly that the correcting agent must not stamp a `deferred_reason` — that is a reviewer's decision under [C-TECH-061](../../constraints/technology/technology-constraints.md#L131) | **YES, measured** — silent on today's log, fires on the reconstructed pre-review-25 log naming the real pair |
| 4 | **skill** | **REVISED anchor** — [how-to-log-an-improvement.md](../../skills/how-to-log-an-improvement.md#L110), immediately after the `refusal_context` block review 27 added | Documents `corrects`. It is read by two gates and by [activation step 8](../../agents/improvement-agent.md#L127), and appears nowhere in the file every agent loads to write a finding | Prose; change 3 is the mechanical half |
| 5 | **constraint amendment** | [C-TECH-061](../../constraints/technology/technology-constraints.md#L131) and [C-TECH-063](../../constraints/technology/technology-constraints.md#L133) | Both `Verify By` clauses name CI as the automatic enforcement. CI has never fired on this project. Amend both to name the build step that will actually run | Prose inside two existing HARD rows; change 1 is the enforcement |
| 6 | **config + skill** | [models.yml L86](../../config/models.yml#L86) + [how-to-select-a-model.md L47](../../skills/how-to-select-a-model.md#L47) | The open-questions escalation trigger counts only questions **this request** raises, not a target document's pre-existing backlog. Requires regenerating `.claude/agents/` — **REVISED:** review 27 already regenerated all 18 files for its own change, so this regeneration lands on top of that, not instead of it |
| 7 | **skill** | **REVISED anchor** — [how-to-intake-external-documents.md step 2](../../skills/how-to-intake-external-documents.md#L30) | Before classing a section MISSING or recording an open question, grep `docs/architecture/` and `src/` for the concept by name and cite what is found. **The Procedure was renumbered by review 27** (a new step 4 resolves named data items; old steps 4–8 are now 5–9), so this must be applied against the current file | Prose |
| 8 | **skill** | **REVISED anchor** — [how-to-write-requirements.md → Common Traps](../../skills/how-to-write-requirements.md#L88) | New trap: an FR naming a content **category** is not satisfied by a component whose name matches. Get one real example of what the business produces by hand and diff it field by field. **L59 is now review 27's *Data Provenance* section**, which this trap complements rather than duplicates: that one asks whether the data exists, this one asks whether the category was enumerated | Prose |

**Zero new constraints against a cap of three.** Two rows are amended instead. Nothing here is a new platform law; it is a wiring gap and four things agents need to know.

**Why change 5 is not a new row.** [C-TECH-061](../../constraints/technology/technology-constraints.md#L131) and [C-TECH-063](../../constraints/technology/technology-constraints.md#L133) are both correct and both HARD. What is false is their `Verify By`: C-TECH-063's says "wired as the FIRST step of `.github/workflows/ci.yml` → `validate`", and [IMP-0165](../../logs/improvement-log.jsonl#L162) records that workflow firing only on `push` to `feature/**`, a branch pattern that has never existed here. The rules were sound; their enforcement path was dead, and the only thing that actually ran either check was the Pester suite five steps from the end of a build.

---

## 4. Retirements — none, for the third review running

**No constraint row retires, and I checked mechanically rather than by eye.** Every live row's `Verify By` names a script that exists; the only two dangling script names are inside [C-TECH-049](../../constraints/technology/technology-constraints.md#L91)'s `retired_reason`, where they are correct history. No row is enforced twice, and no row this review touches loses its purpose.

**Derived, not typed — REVISED: 80 live constraint rows and 10 retired**, via `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l`. The 80th is [C-TECH-074](../../constraints/technology/technology-constraints.md#L144), added by review 27 to reinstate the enforceable half of four rows whose retirement premise had expired. That is worth noting under this heading: the first thing the retirement audit ever produced was a **reinstatement**, which is the opposite of the failure the obligation was written to catch.

**Review 25 predicted this and named the test.** It wrote that if review 26 also found nothing, *"the honest conclusion is that this rule set has no retirement pressure and the obligation is producing a paragraph rather than a decision."* Three reviews have now produced three paragraphs. Section 5 asks you what to do about it; I have not changed the obligation myself, because weakening a self-discipline rule is the last thing an agent that edits its own rules should do unasked.

---

## 5. What you need to decide

**Nothing blocks this review, and four things want an answer.**

**REVISED — should the `corrects` rung stop reading an optional field?** This is the new question, and it is the one I would answer first.

[check_corrections()](../../scripts/verify-improvement-log.py#L1295) has now been scoped twice — once by review 25, once by change 3 below — and it still only sees an entry whose author chose to set `corrects`. [IMP-0288](../../logs/improvement-log.jsonl#L285) did not, and it is the finding that contradicts this very document.

The version that would have caught it keys on `class_instance_of`, which is mandatory: warn when a new entry shares a class with a finding that a review document on disk concluded needed **no change**. That is a new rung, not a third patch, and it would have fired here.

I am not proposing it, for one reason: this is instance 33 of the largest gate class in the project, and the altitude rule exists precisely to stop a review from patching the same script a third time in three days. Say the word and it is the next review's change, measured before it is proposed.

**Should the retirement obligation change?** Today every review must name a retirement candidate or state that it checked. Three consecutive reviews have found none, which is evidence the rule set is lean rather than evidence the reviews are lazy. The cheaper version is to require the audit only when a review **adds** a constraint, or every fifth review.

**REVISED:** review 27 is the data point that changes my recommendation here. Its audit ran the obligation *backwards* and found four retired rows whose reinstatement condition had fired four days earlier and been missed by five reviews. So the audit does earn its keep — but not the half that looks for rows to remove. **My recommendation is now to keep the obligation and re-point it:** every review checks whether any *retired* row's reinstatement trigger has fired, and names a removal candidate only when it is adding a row. Left alone, it stays exactly as it is.

**REVISED — do you want a change-order template, or a pointer?** My original recommendation was a pointer, and I still recommend a pointer — but for a different reason, and with something added.

[CO-001.md](../../contract/change-orders/CO-001.md) is a pattern for the *shape* of a change order. What [IMP-0288](../../logs/improvement-log.jsonl#L285) shows is that it is not a pattern for the *estimate*: its own figure was wrong. So the one line in [contract/README.md](../../contract/README.md#L17) should name it as the precedent **and** name the trap — an estimate made by analogy before requirement text exists is provisional, and [agents/commercial-agent.md L49](../../agents/commercial-agent.md#L49) now says when to revisit it. A template that quietly reproduced CO-001's estimating method would have been worse than nothing.

**One finding names delivery work that is not mine and is not fixed.** [IMP-0279](../../logs/improvement-log.jsonl#L276) records that the trustee detail screen never renders the break type, the itemised holiday costs, or the exceptional-circumstance fields, against an approved requirement that says it shows holiday details in full. That is WBS 6.3 rework or change-order scope depending on your read, and it needs `pm-agent` or `commercial-agent`, not this review. All I am proposing here is the rule that would have caught it.

---

## 6. Verification executed for this review

**Level reached: V1, measured.** Nothing in this document has been written into the repository, and no live environment was touched.

| Check | Result |
|---|---|
| `verify-build-config.py` against a scratch copy carrying change 1 | **PASS — 48 steps, 37 gates**, both new steps recognised as gates, negative-test coverage OK. **REVISED — this figure is stale by construction:** today's real config already measures **48 steps / 36 gates** without change 1, because review 27 added two steps. Change 1 would take it to 50 / 38, and I re-measure at application rather than restate this |
| Change 2's rung against **today's real config** | **2 violations** — `verify-improvement-log.py` and `verify-workflow-syntax.py`, both reachable only inside `unit-tests`. **REVISED — re-confirmed on the current tree:** neither is a step yet, and [BuildGates.Tests.ps1](../../src/tests/build/BuildGates.Tests.ps1#L772) still exercises both, so both violations stand |
| Change 2's rung against the **patched config** | **0 violations**, 15 suite gate scripts inspected. **REVISED:** the suite now names **18** distinct gate scripts, so this count is re-measured at application |
| Change 3's rung against **today's log** | **0 warnings** — self-clearing, as the existing rung is. **REVISED and still true:** today's only `corrects` pair is [IMP-0298](../../logs/improvement-log.jsonl#L295) → [IMP-0290](../../logs/improvement-log.jsonl#L287), and its target is already processed, so the *existing* rung covers it. Change 3's new case has no instance on today's log |
| Change 3's rung against the **reconstructed pre-review-25 log** | **1 warning**, naming the real pair correctly |
| **REVISED — change 3 against [IMP-0288](../../logs/improvement-log.jsonl#L285)** | **Silent.** The entry carries no `corrects` field. This is the measurement that drove §1's revision, and it is the honest limit of change 3 |
| `verify-workflow-syntax.py --root .github --repo-root .` | exit 0 — 3 workflow/action files |
| `verify-improvement-log.py --check` | **exit 1. REVISED — the reason changed:** the blocker that convened this review ([IMP-0285](../../logs/improvement-log.jsonl#L282)) is still unread, and the batch trigger now fires at exactly 10 unread. Approving this document is what clears both |
| `generate-known-failure-modes.py --check` | exit 0. **REVISED — current at 299 entries, not 282**: review 27 closed 8, rejected 1, and appended 5 (one of them found while revising *this* document — [IMP-0302](../../logs/improvement-log.jsonl#L299)), and plan-agent logged 2 more |
| `generate-subagents.py --check` | exit 0, 18 files current — re-confirmed after review 27's regeneration |
| Branches vs `ci.yml`'s trigger | `main`, `project-management`, `self-learning` — **no `feature/**` branch exists**, confirming CI has never run |
| Live / retired constraint rows | **REVISED — 80 / 10**, derived |
| Constraint rows naming a non-existent script | none live |

**Not verified, and it is the honest limit.** The two rungs above are prototypes measured in a scratch directory **against a tree that has since changed**; they are not the final code and will be re-measured at application. No Pester suite has been run for this review, because nothing it proposes touches PowerShell. No live environment was touched.

---

## 7. Findings left unprocessed, and one that is not this feature's

**States excluded, stated so the cap is not silent:** 26 `reviewer-deferred` (each carrying a reason a human accepted), 0 `awaiting-approval`, 0 `already-fixed`, and every `APPLIED`/`REJECTED` entry. All five `unread` entries were read in full and all five are dispositioned above.

**One deferred entry carries no trigger to come back.** [IMP-0274](../../logs/improvement-log.jsonl#L271) has a `deferred_reason` and no `revisit_when`, which the log gate reports as a standing NOTE. Review 25 left it because it was out of approved scope; I am leaving it for the same reason and naming it so it does not go quiet.

**[IMP-0284](../../logs/improvement-log.jsonl#L281) belongs to a different thread and was processed anyway.** It comes from a concurrent `plan-agent` session on the change-order work, not from the WBS 0.4 build. It shares the queue, not the subject. Its remedy is one clause in a skill and it costs nothing to close now.

**Four entries close on approval and one does not.** [IMP-0278](../../logs/improvement-log.jsonl#L275), [IMP-0279](../../logs/improvement-log.jsonl#L276), [IMP-0280](../../logs/improvement-log.jsonl#L277), [IMP-0284](../../logs/improvement-log.jsonl#L281) and [IMP-0285](../../logs/improvement-log.jsonl#L282) all declare `observable_at` of `n/a` or `V1`, so each is closable by the change itself — except [IMP-0279](../../logs/improvement-log.jsonl#L276), which is `V4` and whose delivery half is untouched. **It stays open**, with a `revisit_when` naming the trustee-detail screen and the reference document, per section 5.

**REVISED — [IMP-0278](../../logs/improvement-log.jsonl#L275)'s closure changed.** It was going to close on nothing at all; it now closes with `applied_by` naming **review 27's change 9** at [agents/commercial-agent.md L49](../../agents/commercial-agent.md#L49), which is already on disk. One rule covers both instances of the class, so this document proposes no change of its own for it.

**REVISED — all five entries currently read as `unread` and the queue cannot tell them from findings nobody has opened.** The log gate reports exactly that, five times over, plus a blocker trigger on [IMP-0285](../../logs/improvement-log.jsonl#L282) and a batch trigger at 10. **All five are cited by this document, so the correct response to those triggers is the keyword against this file, not another dispatch** — that distinction is [IMP-0183](../../logs/improvement-log.jsonl#L180), and the gate cannot make it until `reviewed_in` is stamped, which happens at approval.

---

## 8. Digest impact

**Not zero, and this time the prediction counts this review's own findings.** Review 25 predicted zero, gave a good reason, and was wrong for exactly that omission.

I expect to append **three** findings at application — the mis-scoped `corrects` rung, the two HARD rules whose enforcement path has never executed, and **REVISED:** the rung's blindness to [IMP-0288](../../logs/improvement-log.jsonl#L285), which is the optional-field hole with an instance attached rather than a prediction.

**REVISED — the base is 299, not 282**, so the prediction is **299 → 302**, and `gate-cannot-fail` goes from **x32 to x35**. Both growing classes are already over the 20-lesson display cap, so I expect the new lessons in the not-shown lists and the line count roughly unchanged — the digest is currently 484 lines.

**A note on that prediction, because review 27's was wrong in both directions.** It predicted 292 → 296 against a base that had already moved to 294, and one of the four findings it named turned out to be another finding's substance rather than its own entry. So treat the number above as an intention, not a measurement: I regenerate and report the measured before-and-after on approval, and I state where it differs from this prediction rather than letting the prediction stand as the record.

---

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-24-improvement-review-6.md
                              REVISION 1 — re-presented 2026-08-25, nothing applied

Findings processed: 5 unread  →  5 clusters
Regression check:   8 prior changes audited, 2 classes recurred
                    (+1 row: this review's own IMP-0278 disposition, contradicted by IMP-0288)
Proposed:           0 constraints (cap 3), 3 gates/scripts, 4 skill/knowledge edits,
                    0 agent-file edits, 2 constraint amendments, 0 retirements
                    — unchanged from revision 0; 3 anchors re-pointed after review 27
Altitude calls:     1 generalised from instance to class, 4 left as knowledge lines,
                    1 declined as a third patch to one script (put to you in §5)
Digest:             will regenerate — predicted 298 → 301, will report measured

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 10. Applied — 2026-08-25

**Seven of eight changes are on disk. Change 5 is withheld: its premise failed re-verification, and applying it would have written a false claim into two HARD rows.** Everything below is measured against the tree, not restated from §3 or §6.

### What landed

| # | Type | Where it is now | Measured |
|---|---|---|---|
| 1 | build config | [`improvement-log-check`](../../config/revitalise-grant-automation-build.yml#L141) and [`workflow-syntax`](../../config/revitalise-grant-automation-build.yml#L144), beside the two existing preflights | preflight **PASS — 50 steps, 38 gates**; both selftests exit 0, so both register under `check_negative_tests`'s `--selftest` path |
| 2 | script rung | [`check_suite_gates_are_steps()`](../../scripts/verify-build-config.py#L638), wired at [L879](../../scripts/verify-build-config.py#L879) | **2 violations without change 1, 0 with it** — exactly as approved. Proven able to fail by stripping the two steps from a scratch copy |
| 3 | script rung | [`check_corrections()` second case](../../scripts/verify-improvement-log.py#L1381) | selftest **53 fixtures, all green**, including the new warning firing and staying quiet on a reviewer-deferred target |
| 4 | skill | [`corrects` documented](../../skills/how-to-log-an-improvement.md#L128) | it had **0 occurrences** in that file before today, despite two gates and an activation step reading it |
| 5 | constraint amendment | **WITHHELD — see below** | — |
| 6 | config + skill | [models.yml](../../config/models.yml#L91) and [how-to-select-a-model.md](../../skills/how-to-select-a-model.md#L48) | 18 subagent files regenerated, generator `--check` clean, clarification verified present at `.claude/agents/plan-agent.md` line 27 |
| 7 | skill | [intake step 2](../../skills/how-to-intake-external-documents.md#L38) | anchored against the current file — review 27's renumbering confirmed before editing |
| 8 | skill | [a content CATEGORY read as a field list](../../skills/how-to-write-requirements.md#L94) | sits under *Common Traps*, complementing review 27's *Data Provenance* section rather than repeating it |

### Change 5 is withheld, and this is why

**Its premise is that CI has never fired on this project. That is not established, and the evidence §6 offered for it does not support it.** [ci.yml](../../.github/workflows/ci.yml#L259) triggers on pushes to **three** patterns — `main`, `project-management` and `feature/**` — and the first two are real branches carrying pushed commits. The trigger gained `main` and `project-management` in `388291b` on 2026-08-21, the same day [IMP-0165](../../logs/improvement-log.jsonl#L162) recorded the `feature/**`-only observation this premise descends from, and `a072849` was pushed to `project-management` on 2026-08-23 — after `ci.yml` was made valid on 2026-08-19 (`6158243`). The `validate` job does run both scripts, at [L316](../../.github/workflows/ci.yml#L316) and [L422](../../.github/workflows/ci.yml#L422).

§6's row concluded *"no `feature/**` branch exists, confirming CI has never run"*. An absence proven against one of three patterns proves nothing.

**Whether CI actually fired is unobservable from this session** — `gh` is unauthenticated — and that is the decisive fact rather than a caveat. [Activation step 8](../../agents/improvement-agent.md#L127) forbids applying a HARD constraint whose premise has just failed, and forbids quietly substituting different rule text for approved rule text. Both rows keep their current `Verify By`. Logged as [IMP-0308](../../logs/improvement-log.jsonl#L305), which proposes the **additive** form for a future review: name *both* enforcement paths, the CI job **and** the new build steps, rather than replacing one whose deadness is unproven. One authenticated `gh run list` settles it.

### Two corrections to this document's own §6

- **`generate-subagents.py --check` did not exit 0, and the 18 files were not current.** §6 claimed both, "re-confirmed after review 27's regeneration". Reconstructing HEAD's generated files against the working-tree generator exits **1 with all 18 STALE**; `git show HEAD:.claude/agents/data-agent.md` contains no `IMP-0290`. Review 27's regeneration never happened — it is one of the six-of-twelve changes the spend limit cut short ([IMP-0301](../../logs/improvement-log.jsonl#L298)) — and [IMP-0298](../../logs/improvement-log.jsonl#L295)'s own `applied_by` asserts it too. Change 6 required a regeneration, so the 18 files are now current and review 27's undelivered change landed with it. Logged as [IMP-0309](../../logs/improvement-log.jsonl#L306).
- **Change 2's rung measures 4 candidate violations, not 2, and two of them must never be reported.** `verify-workflow-description-length.py` and `verify-setting-description-length.py` are named in the suite **only by an It block asserting they are gone** — they are this project's founding altitude-rule retirement, replaced by `verify-field-length-limits.py` under `C-TECH-060`. A rung keyed on the name alone would report that retirement as a violation and pressure a future agent into resurrecting exactly the two scripts the altitude rule deleted. Membership is therefore filtered by existence on disk, which yields the approved figure of 2.

### Closures

**Four closed, one deliberately left open.** [IMP-0278](../../logs/improvement-log.jsonl#L275) closes on review 27's change 9 at [commercial-agent.md L49](../../agents/commercial-agent.md#L49), not on a change of this review's own. [IMP-0280](../../logs/improvement-log.jsonl#L277), [IMP-0284](../../logs/improvement-log.jsonl#L281) and [IMP-0285](../../logs/improvement-log.jsonl#L282) close on changes 6, 7 and 1+2+3+4 respectively, each carrying an `evidence_grep` needle.

**[IMP-0279](../../logs/improvement-log.jsonl#L276) stays open, and that is the honest answer.** Change 8 shipped the rule that would have caught it; the trustee detail screen still does not render the break type, the itemised costs or the exceptional-circumstance fields. Its `observable_at` is `V4` — only ever visible when the screen runs — so closing it on a skill edit would be the exact level-skip that closed `IMP-0208` on a sentence its own review had just written and left the defect live for a real signed-in user three days later. It carries a `revisit_when` naming the reproduction and the reference document, and the delivery half is WBS 6.3 rework or change-order scope for `pm-agent` or `commercial-agent`.

### Digest and the queue, measured

**307 entries, 307 distinct lessons, 484 lines** — `generate-known-failure-modes.py --check` clean.

**The §8 prediction was wrong in its base and in its classes, so here is the measurement instead.** §8 predicted `299 → 302` and the gate block said `298 → 301`; the real base at application was **304**, and three findings were appended to reach **307**. `gate-cannot-fail` did **not** move to x35 — it is still **x32**, because the three findings this application produced belong to `finding-diagnosis-unverified`, `learning-substrate-destroyed` and a new class, `rule-written-where-the-generator-drops-it`. Line count is unchanged at 484, which §8 did predict, and for the reason it gave.

**The blocker trigger is cleared. The batch trigger is not, and will not be by this document.** `verify-improvement-log.py --check` now exits 1 on one problem instead of two: 14 unread findings against a batch trigger of 10. Eleven were never in this review's scope, and three are its own output. **So [`improvement-log-check`](../../config/revitalise-grant-automation-build.yml#L141) — the step change 1 just added — is red, and the next build fails on it in about one second.** That is not a regression introduced by change 1: `C-TECH-061` was already HARD and already asserted inside `BuildGates.Tests.ps1`, so the same build already failed on the same condition at step 41 of 46 after roughly nine minutes of npm and Pester work. Failing in one second at step 3 is the entire content of [IMP-0285](../../logs/improvement-log.jsonl#L282). Clearing it needs the next review, drafted as [review 28](./2026-08-25-improvement-review-2.md).
