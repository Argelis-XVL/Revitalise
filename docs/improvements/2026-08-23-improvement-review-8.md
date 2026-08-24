# Improvement Review 20 — 2026-08-23

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 unread → 3 clusters (2 unread blockers, plus 1 cluster raised by the regression check)
**Trigger:** two unread blocker-severity entries, reported by [verify-improvement-log.py](../../scripts/verify-improvement-log.py#L179) → `--check`.
**Gate:** `APPROVE IMPROVEMENTS`
**WBS:** `0.4` (the four finance tables and the second column-security profile).

**Status:** ~~AWAITING `APPROVE IMPROVEMENTS`.~~ **APPROVED and APPLIED 2026-08-23** by the reviewer (Xander Lykopoulos). All five changes are in the tree, plus one item folded in after approval on the reviewer's instruction. The open question was answered KEEP. See section 8.

**Sections 1–7 are the record as written before approval and are deliberately left in the present tense.** Where they say a thing "is" true, read it as true at the time of the finding; section 8 states what is true now.

---

## Summary

**Both blockers are real, and the more serious one is still live: a build gate reported PASS this afternoon over source that Dataverse then rejected outright, and the same gate reports PASS today over a second security control that does not actually work.** One column in the grant table is marked confidential in a way the platform cannot honour, and nothing has ever told anyone.

**The other blocker is largely already resolved by events, and the log has not caught up.** You ran the blocked command yourself and it worked; the profile exists, its real id is in source, and one entry still deferred in the log is waiting for something that has already happened.

**I need one decision from you, and it is small.** The rest is a gate extension, one constraint, and two corrections to instructions that currently state an untested guess as advice.

---

## What has been built

Nothing has been built. This review proposes; section 3 is the diff and it is unapplied.

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| The new plurality gate and [C-TECH-069](../../constraints/technology/technology-constraints.md#L140), review 19 change 1–2 | 2026-08-23 | a check keyed on a column name alone, in a solution that reuses names | NO | **Working.** No finding in that class since |
| Code-app gate rescoped to the tables the app names, deny-list retired, review 19 change 3 | 2026-08-23 | a hand-maintained exclusion list | NO | **Working** |
| Count gate's test-double carve-out narrowed, review 19 change 4 | 2026-08-23 | a test asserting a hand-typed total | NO | **Working** |
| The closing-verification step, review 19 [change 5](./2026-08-23-improvement-review-7.md#L222) | **declared NOT APPLIED** | a review's own script escaping the rules of the folder it lands in | n/a | **The declaration is wrong.** Its substance is in the working tree at [agents/improvement-agent.md L208](../../agents/improvement-agent.md#L208), uncommitted. See below |
| A review declaring findings out of scope no longer trips the citation warning, review 19 change 7 | 2026-08-23 | a gate firing on nothing | NO | **Working** — today's run produced no false citation warnings |
| Closure evidence must match the level the defect was visible at, reviews 16–19 | 2026-08-23 | closing a finding on prose | NO | **Working, and it decided a disposition today.** It is why one of today's two blockers stays open rather than closing on a source fix |

**The fourth row is the one that needs you, and it is the same defect one level up from the one review 19 itself recorded.** That review told you change 5 was not applied and parked it as your open decision. The text it describes — *"for every executable this review created or edited, run the test suite governing its folder"* — is in the file now, inside the block that landed as part of a different, approved change. So you are being asked to decide something that is already in force.

**I have not touched it either way.** Deciding it by applying it, or by removing it, would both be me answering a question you reserved. It is in "What you need to decide" as a one-line confirmation, not as a fresh proposal.

**A second closure defect surfaced while I was ground-truthing, and it is the reason cluster A exists at all.** A finding from 2026-08-19 proposed three things: a knowledge note, a warning in the coverage gate, and a test. It was marked done on the strength of the knowledge note alone, and [its own record](../../logs/improvement-log.jsonl#L47) names only that one file. The gate warning was never written, and the column it was meant to warn about is still secured in source today.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: source marks a column confidential in a way the platform will not honour
           (x2: IMP-0249, IMP-0047)
Altitude:  CLASS — two instances, one loud and one silent, same underlying property
Ladder row: "second instance → generalise" + "a tool could catch it mechanically"
           + "a platform law → a constraint row"
Becomes:   scripts/verify-field-security-coverage.py gains an unsecurable-shape check
           and a --selftest, + C-TECH-070 (HARD)
Retires:   nothing — this class was undefended; see section 4
Cites:     IMP-0249, IMP-0047
Residual:  the gate reads SOURCE. A column shape Dataverse refuses to secure that is
           not declarable in source at all stays invisible to it — the Money _base twin
           is exactly that, which is why the Money half is a warning naming the twin
           rather than an assertion about it.
```

```
CLUSTER B: the harness refuses a live write, and after seven occurrences nobody has
           recorded the conditions well enough to know why   (x7: IMP-0245)
Altitude:  CLASS — the protocol's step 4 is a PROSE fix from review 8 and the class has
           recurred twice since, so per the regression rule it escalates to a gate
Ladder row: "a recurrence after a prose change → escalate to a gate"
Becomes:   pipeline-agent.md steps 3a and 4 corrected, + a required refusal_context
           field on this class in verify-improvement-log.py
Retires:   nothing
Cites:     IMP-0245, and the six earlier instances step 4 already names
Residual:  the gate makes the NEXT refusal diagnostic. It cannot make this one
           diagnostic retroactively, and it cannot settle the question on its own —
           settling it needs one deliberate retry from a non-auto session.
```

```
CLUSTER C: the log's own record of what was done contradicts the tree
           (x2: raised by this review's regression check)
Altitude:  CLASS — third generation of one substrate defect, two of them today
Ladder row: "the system's own memory failed" → a read-path change, mechanical where possible
Becomes:   verify-improvement-log.py — a closed entry whose proposed change named
           several targets must account for every one of them
Retires:   nothing
Residual:  the inverse case is NOT mechanically checkable. A review's prose claim that
           something was NOT applied cannot be checked against a tree that carries it,
           because nothing states in machine-readable form what "it" was. Reported to
           you instead, which is the only remedy available.
```

---

## 3. Proposed changes

| # | Type | Target | What it does | Can it fail? |
|---|---|---|---|---|
| 1 | script | [verify-field-security-coverage.py](../../scripts/verify-field-security-coverage.py#L55) | Two new checks. **FAIL** if a table's primary name column is marked secured — Dataverse refuses to create the table at all. **WARN** if a currency column is marked secured, naming the automatic twin that carries the same number unsecured and the table privilege that is the real control. The primary name is read from each table's own declaration, never hard-typed | YES — a `--selftest` with three fixtures: a secured primary name must fail, a secured currency column must warn, the real tree must pass |
| 2 | constraint | `C-TECH-070` (HARD) | States the rule change 1 enforces: marking a column confidential is a control only where the platform can actually secure that column shape, and the two shapes it cannot are named with what proved each | Change 1 is its `Verify By` |
| 3 | agent file | [pipeline-agent.md step 3a](../../agents/pipeline-agent.md#L106) and [step 4](../../agents/pipeline-agent.md#L115) | Step 3a records that no command-line verb exists for creating tables, columns, roles or column-security profiles, so this operation class has no fallback there — checked across all 22 command groups. Step 4 stops presenting its guess as advice: it says which variable was actually tested, which was not, and what today's one datapoint does and does not show | Partly — the facts are checkable, the remembering is prose |
| 4 | gate | [verify-improvement-log.py](../../scripts/verify-improvement-log.py#L179) | A finding recording a refused live operation must carry a `refusal_context` naming whether the session was automatic or interactive and whether it was a background dispatch, the lead session, or your own shell. Binds from a dated cutoff forward only | YES — selftest fixtures both ways |
| 5 | gate | [verify-improvement-log.py](../../scripts/verify-improvement-log.py#L179) | A finding closed as done, whose proposed change named more than one file, must account for each one. Closing on a subset is what left a live security defect unreported for four days | YES — the 2026-08-19 entry is the fixture |

**One new constraint against a cap of three.** Clusters B and C needed none: cluster B is a correction to an existing instruction plus a gate, and cluster C is bookkeeping enforcement.

**Changes 4 and 5 are two rules in one file.** I am listing them separately because they answer different clusters, not because they are separate work.

---

## 4. Retirements

**I checked and found nothing superseded by this review.** The one mechanism I seriously considered retiring is the hand-written exemption list at the top of [the coverage gate](../../scripts/verify-field-security-coverage.py#L39) — it is the same shape as the deny-list review 19 retired yesterday. I am leaving it, and the reason is that it points the other way: it records a column deliberately left *un*secured with a stated reason, so the failure mode when someone forgets to update it is a build failure, not a silent gap. The deny-list's failure mode when someone forgot was silence.

**Worth flagging as a trend rather than an action.** Seventy constraints, one retired row. Nothing here qualifies, but a rule set that only grows is the thing [the retirement rule](../../constraints/README.md#L139) exists to catch, and this is the fourth consecutive review to report none.

---

## 5. Findings left unprocessed, and one deferral that has gone stale

**States excluded, stated so the cap is not silent:** 1 `awaiting-approval`, 12 `reviewer-deferred`, and every entry already closed. Two `unread` entries were read in full and both are dispositioned above.

**One entry is parked at another review's gate and must not be re-derived.** It has been waiting since 2026-08-22 for a keyword sent against [the review that processed it](./2026-08-22-improvement-review-2.md), not for a new session. The remedy is a keyword, not a review.

**One of the twelve deferrals is now waiting for something that already happened, and I am reporting it rather than closing it.** It was deferred because a placeholder id could not be replaced until a live write created the profile. [Your own manual run did that](../../logs/routing.log#L158) — the profile exists, and its real id is already in [FieldSecurityProfiles.xml L622](../../src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L622) and [Solution.xml L249](../../src/solutions/RevitaliseGrantAutomation/Other/Solution.xml#L249). No placeholder remains anywhere in the solution. It is a reviewer-deferred entry, so closing it is not mine to do, but leaving it looking blocked would mislead the next agent that reads the queue.

---

## 6. Digest impact

**I am not predicting a number.** A previous review's predicted delta was wrong because the generator routes a lesson by two mechanisms and one silently wins; the lesson was to measure after regenerating. On approval I will run the generator and report the measured before-and-after.

What I can state without measuring: one of the two blockers changes status, one stays open by design, and two new findings are appended for the closure defects in section 1.

---

## What is still open

**The two finance tables have not been created.** The source fix is real — I checked every table in the solution and no primary name column is marked secured anywhere. But the only thing that proves the fix is the create call succeeding, and nothing has re-run it since the fix landed. That is why this finding stays open rather than closing on a clean file, and it needs one command run against DEV, not another review.

**Nobody knows why the harness refuses these writes.** Seven occurrences, and the instruction file currently offers a remedy based on a single observation that was never isolated. Today's evidence narrows it slightly and unhelpfully: the command succeeded from your own shell, which is the last step in the ladder, so the step before it — retrying from the lead session — is still untested after all seven.

**The currency column in the grant table is still marked confidential and still is not.** Change 1 makes the build say so on every run. It does not change the column, because you accepted that risk on 2026-08-19 on the basis that the table privilege is the real control, and that decision stands.

---

## What you need to decide

**Was change 5 from yesterday's review meant to be in the tree?**

You approved review 19 without answering its closing question, and it recorded change 5 as not applied. Its substance is in [agents/improvement-agent.md L208](../../agents/improvement-agent.md#L208) now, uncommitted, having arrived inside a neighbouring change.

So this is a confirmation, not a fresh proposal: **keep it, or take it out?** I recommend keeping it — the evidence for it got stronger yesterday, and it costs a few seconds per review. But I will not treat silence as a yes, because that is how it got in.

**Everything else in this review is a straight approve or reject.** No part of it depends on this answer.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-23-improvement-review-8.md

Findings processed: 2 unread  →  3 clusters
Regression check:   6 prior changes audited, 0 classes recurred, 2 closure defects found
Proposed:           1 constraint (cap 3), 3 gates/scripts, 1 agent-file edit, 0 retirements
Altitude calls:     2 generalised from instance to class, 1 escalated from prose to gate
Digest:             will regenerate — measured after applying, not predicted

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

**Verification actually executed.** Every table in the solution checked for a secured primary name — 10 of 10 clean. Every currency and decimal column enumerated — 1 of 10 secured, in the grant table. The coverage gate re-run against the real tree: PASS, 67 secured columns, which is the point. The command-line verb absence re-confirmed against the recorded group list. The profile's live id confirmed present in both source files, with no placeholder remaining anywhere under `src/solutions/`.

**Not verified.** Nothing here ran against a live environment, and the two finance tables have still never been created. The proposed gate has not been written yet, so it has never run; I will state its selftest count when it exists, not before.

---

## 8. Applied — 2026-08-23

**Approved and applied in full. Change 5 confirmed as a deliberate KEEP, and one orphaned finding folded in on your instruction — it turned out to be unactionable by any keyword, which is why six previous reviews could not shift it.**

### The orphan, because it is the most useful thing in this section

**A finding had been sitting in `awaiting-approval` since 2026-08-22 waiting for a keyword that could never have worked.** It was appended to [the 2026-08-22 review](./2026-08-22-improvement-review-2.md) *after* that document's gate had already been approved and applied, so it was parked against a gate with nothing left in it. Six later reviews each independently wrote "send the keyword against that document"; none noticed. Folded into this review and applied instead of opening a seventh review repeating the same note.

**Its content was worth having.** The digest generator routes a lesson to a section by two mechanisms — the class table and a `capability: true` flag — and the flag wins silently, so a review that reads the class table can predict a digest change that cannot happen. [routing_of](../../scripts/generate-known-failure-modes.py#L264) and [print_routing](../../scripts/generate-known-failure-modes.py#L433) now make all of it visible: the recurring-classes table gains a `Renders in` column, and `--routing` answers "if I add this class, what moves?" directly.

**Fixing it exposed a third mechanism nobody had recorded.** A class named in two section tuples renders only in the last one, because the lookup is built by overwriting. [The digest now says so on its own front page](../../logs/known-failure-modes.md#L59) — `repo-path-contains-spaces` is in both `before-build` and `operating`, and has only ever rendered in `operating`.

### Elements changed

| # | Change | Where | Verified by |
|---|---|---|---|
| 1 | Coverage gate now fails on a secured primary name and warns on a secured currency column. Both read from the table's own declarations, never transcribed | [verify-field-security-coverage.py L211](../../scripts/verify-field-security-coverage.py#L211), [L221](../../scripts/verify-field-security-coverage.py#L221) | 3/3 selftests, **plus the real pre-fix tree**: re-introducing the defect into a copy of the live source makes it exit 1 naming both tables |
| 2 | [C-TECH-070](../../constraints/technology/technology-constraints.md#L141) — HARD, the rule change 1 enforces | technology-constraints.md | change 1 is its `Verify By`; `verify-constraint-verifiers.py` green |
| 3 | Refusal protocol: no command-line verb exists for this operation class, and step 4 stops stating its guess as advice | [pipeline-agent.md L118](../../agents/pipeline-agent.md#L118), [L129](../../agents/pipeline-agent.md#L129) | prose; the facts in it are each cited to what proved them |
| 4 | A finding about a refused live operation must record the session conditions | [check_refusal_context](../../scripts/verify-improvement-log.py#L587) | 5 selftest fixtures both ways |
| 5 | A closed finding must account for every path its proposed change named | [check_multi_target_closure](../../scripts/verify-improvement-log.py#L621) | 5 selftest fixtures; the 2026-08-19 entry is the live case |
| 6 | **Folded in after approval:** the digest's three routing mechanisms made visible | [generate-known-failure-modes.py](../../scripts/generate-known-failure-modes.py#L264) | `--routing` runs; the digest regenerates and `--check` is current |

### The four-day-silent defect now speaks

The build says this on every run, and said nothing for four days:

> `MONEY IS NOT SECURABLE IN FULL - rev_grant.rev_amountawarded is IsSecured=1, but Dataverse maintains rev_amountawarded_base alongside it with CanBeSecuredForRead=False.`

It is a warning, not a failure, because you accepted that risk on 2026-08-19 on the basis that the table privilege is the real control. Nothing about the column changed.

### Findings: what closed, what did not

**Six entries moved, and two stayed open on purpose.** The harness finding closed on its documented half, carrying the first `refusal_context` record in the log and a `reobserved` naming your own shell run. The 2026-08-19 currency finding is now closed against **both** the targets it named, with its third part explicitly recorded as deliberately not done and why. Two new findings were appended for the closure defects in section 1.

**The primary-name blocker stays open, and so does the placeholder finding, for the same reason.** Both are `observable_at` V4 or V3, and neither has had its reproduction re-run. The source is fixed and both gates that were red are green — but a clean file is not a create call, and closing on one would be exactly the closure this system refuses.

**One stale deferral was narrowed and one was given a trigger it never had.** The placeholder entry's clearing action is verifiably complete — the profile exists, its real id is in both source files, [guid-syntax](../../scripts/verify-guid-syntax.py) is green over 414 elements — so its reason now says only the deploy remains. The other had no `revisit_when` at all, which the log gate had flagged on every run since review 18; it has one now.

### Digest impact — measured, not predicted

**246 → 248 entries**, 248 distinct lessons, **466 → 472 lines**, and the recurring-class count held at **26** — no new class, which is the point. `learning-substrate-destroyed` **x17 → x19**; `harness-blocks-destructive-call` steady at **x7**, because the finding that triggered this review was already counted in it.

**The digest also gained a column.** Every row of the recurring-classes table now names where that class's lessons actually render, so the mistake that produced the orphaned finding cannot be made by reading the table.

### Verification actually executed

Eight repository gates, all exit 0: both new selftests (3 fixtures and **48**, up from 38), the log gate, the digest freshness check, the constraint-verifier check, the guid gate, the plurality gate, and the coverage gate against the real tree. **112 of 112 Pester tests** across `src/tests/build`, 0 failures — run because change 5's closing step is now in force and this review wrote executables into `scripts/`.

**Not verified, unchanged:** nothing ran against a live environment. The two finance tables have still never been created, no solution import has carried the new profile id into DEV, and the question of what actually makes the harness refuse these writes is instrumented but unanswered — it needs one deliberate retry from a non-auto session.
