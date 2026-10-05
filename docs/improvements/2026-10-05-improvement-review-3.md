# Improvement Review — 2026-10-05 (3)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 6 `NEW` → 4 clusters, plus 2 `APPLIED` entries whose evidence a reviewer decision removed (IMP-0244, IMP-0246)
**Trigger:** reviewer request, relayed by lead-agent, 2026-10-05: a HARD build gate went red after a reviewer-instructed deletion
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** APPLIED 2026-10-05, on the reviewer's "Approve Improvement" (Xander Lykopoulos, relayed by lead-agent; see §9 for how that wording was judged). Draft-time note, kept: `reviewed_in` was stamped on the 6 unread entries at step 6, and IMP-1060 was appended by lead-agent while the draft was being written and folded into cluster 3.
**WBS:** system work, `wbs:system`, not billable. The deletion that triggered it belongs to the provisioning-test debt baselined under `wbs:6.5`.

---

## Summary

The reviewer's instruction *"IMP-0439: test 5, 6 and 8. remove 7"* deleted the never-runnable access-test pre-flight script. That left two problems. First, the next build halts at its 3rd step, because two closed findings still point at the deleted script as their proof. Second, the HARD rule that protects the anonymised access test now names a check that does not exist.

The first problem is bookkeeping and has a precedent: re-point the two proofs. It needs this review's keyword, but no rule changes. You can approve rows 1 and 2 on their own to unblock the build. The second problem needs your decision (D-2), because the obvious answer, *"a human checks it"*, is the exact arrangement that rule was written to replace.

---

## 1. Regression check — did the last review's changes work?

The previous review is [2026-10-05-improvement-review-2.md](docs/improvements/2026-10-05-improvement-review-2.md#L279). It was applied today.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Row 1: a review that only deferred no longer reads as parked | 2026-10-05 | `gate-fires-on-nothing` | NO | Working. IMP-1055 is a by-product of applying it, not a recurrence. It was caught and fixed during that same apply |
| Rows 2, 3: selector match count, amendment re-measure | 2026-10-05 | `approved-change-wording-assumes-a-field-that-does-not-exist`, `stale-deferral-uncaught-across-sessions` | NO | Working. Row 3 was used here: §3's rows carry their match counts |
| Rows 4–8: change-scoped builds | 2026-10-05 | `two-invocation-paths-disagree`, `gate-scope-mismatch`, `capability-established` | NO | No scoped build has run since, so this is not exercised yet |

**Changes whose class recurred after a prose fix:** none. **After a gate:** none.

---

## 2. Clusters and promotion decisions

```
CLUSTER: a later authorised change removes an APPLIED entry's proof  (x1 new: IMP-1059; family x5 with IMP-0672, IMP-0678, IMP-0717, IMP-0745)
Altitude:   CLASS for the message, INSTANCE for the two entries — the validator already handles
            three of the four ways a proof moves (relocated to the engine, split into the digest
            appendix, reworded in place); a DELIBERATE DELETION is the fourth, and the gate's
            message calls it a false claim
Ladder row: "a tool could catch it mechanically" — it already does; the gap is that its finding
            text names no correct remedy for this cause
Becomes:    row 1 (re-point the two needles, the needle_repoint_note precedent of 7 entries)
            + row 2 (the missing-file message names deliberate deletion and its route)
Retires:    nothing
Cites:      IMP-1059, IMP-0244, IMP-0246
Residual:   nothing stops a delivery agent deleting a cited file. The HARD build step catches it
            before anything ships, and that is the right place: the cost is one halted build,
            not a false claim
```

```
CLUSTER: gate-found-broken — the flow-definition gate's own selftest  (x1: IMP-1059, second half)
Altitude:   INSTANCE
Ladder row: "a tool could catch it mechanically" — the selftest is the tool, and it has become
            unable to pass
Becomes:    row 3. The "an EXPIRED exception fails the build" assertion runs against the real flows.
            Since the flows were fixed, those flows contain nothing for an exception to cover,
            so an expired exception changes nothing and the assertion fails. It moves to an
            in-memory corpus that contains a known check-7 shape
Retires:    nothing. The 3 spent entries in config/flow-check7-exceptions.json are routed (R2)
Cites:      IMP-1059
Residual:   the selftest is not wired in any build step or Pester block (measured: the build step
            runs the gate, not its --selftest), so this red never halted anything
```

```
CLUSTER: gate-cannot-fail — a negative test whose stimulus can silently not apply  (x2: IMP-1055, IMP-1060)
Altitude:   CLASS — second instance of the same property: the test passes or fails on input it
            never actually changed (a fixture with nothing to assert; a regex mutation that
            matched nothing)
Ladder row: "second instance → generalise", in the two harnesses where it was seen
Becomes:    row 4: every fixture expecting exit 0 with no expected text must be listed in either
            _MUST_NOT_CONTAIN (a banned text) or a new _RC_IS_THE_ASSERTION set (an error rung,
            where exit 0 already proves something). The selftest refuses a fixture listed in neither
            row 6: New-MutatedConfig in VerifyBuildConfig.Tests.ps1 throws when its mutation
            leaves the config text unchanged, so all 7 callers are covered, not only the one fixed
Retires:    nothing
Cites:      IMP-1055, IMP-1060
Residual:   other Pester files that mutate input inline, not through this helper, are not
            covered. The classification is the author's declaration. The gate forces the declaration to
            be made; it cannot check that it is right. Mutation at apply time is the check
```

The finding proposed a name-based guard. I measured it before writing it into the table, and it is wrong: *"refuse a fixture whose name says must-not-warn with no banned text"* flags 1 fixture today, [R3-prose-target-must-not-warn](scripts/verify-improvement-log.py#L3022). That fixture targets an **error** rung, so exit 0 *is* its assertion: 0 true, 1 false. It also misses [corrects-as-a-list-resolves-every-target](scripts/verify-improvement-log.py#L3122), which targets a warning rung and really asserts nothing. Re-derived count: 17 of 96 fixtures expect exit 0 with no text and no banned text, matching the finding.

```
CLUSTER: config shape relayed as live state; a declared step that could not run  (x2: IMP-1056, IMP-1057)
Altitude:   NOTE for both
Ladder row: "one instance, specific, no general mechanism" (IMP-1056); IMP-1057's gate proposal
            is WITHHELD — its premise no longer holds
Becomes:    nothing new. Development-agent already declared the steps (-Env test at
            config/revitalise-grant-automation-pipeline.yml L2008, -Env prd at L2275) and
            removed the dev-only throw from ensure-schema.ps1. The existing settings-file check
            (settings_file_for in verify-pipeline-config.py) now covers whether the -Env resolves
Retires:    nothing
Cites:      IMP-1056, IMP-1057
Residual:   whether ensure-schema.ps1 works against an environment where the solution is not yet
            installed is UNVERIFIED (V2). Only the reviewer's account of the manual ACC run, or
            the first pipeline run of the -Env test step, can settle it
```

IMP-1057 asked for check 14 to read the script's own environment guard. The guard it would read is gone, and a gate that parses PowerShell control flow for one script's `if` is the wrong instrument for a single instance. A second script carrying an in-script environment throw would justify it.

IMP-1058 is a one-off fix, already in source and tested. It closes as a note: [verify-environment-access.ps1 L122](provisioning/dataverse/verify-environment-access.ps1#L122) now tests that the property exists before reading it. I re-ran [the new test file](src/tests/provisioning/VerifyEnvironmentAccess.Tests.ps1#L85): 5 passed, 0 failed, including *"FAILS when WhoAmI answers but returns no UserId"*.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | other | `logs/improvement-log.jsonl`, IMP-0244 and IMP-0246 only | Re-point both `evidence_grep` needles and add a `needle_repoint_note` to each, as 7 entries already carry. **IMP-0246**: its `proposed_change` targeted [agents/improvement-agent.md](agents/improvement-agent.md#L607), and that half still stands. New needle `An executable that authenticates to a live environment is delivery work` (measured: 1 line). Its other half, the `$pid` rename, went with the file. **IMP-0244**: nothing it fixed survives, because the script and its README row were deleted by reviewer decision. New needle is the marker line in §8 of this document, `IMP-0244 evidence retired by reviewer decision` (measured: 1 line). Its `status` stays `APPLIED`: the claim was true when it was made, and the note says what removed it and on whose instruction | IMP-1059, IMP-0244, IMP-0246 | YES. Measured by simulation on a scratch copy of the log: `--check` goes from 2 errors to 0 | already wired (`improvement-log-check`) |
| 2 | script | [verify-improvement-log.py L1053](scripts/verify-improvement-log.py#L1053) and its `.engine/` twin (identical, `cmp` 0) | When an `APPLIED` needle names a file that no longer exists, the message names three causes: moved, deleted by a later authorised decision, or never written. For deletion it gives the route: improvement-agent re-points the needle to the surviving half or to the record of that decision, adds a `needle_repoint_note`, and keeps `APPLIED`. Message text only, no change to what passes. New selftest fixture asserting the text | IMP-1059 | YES: `--selftest`, plus `--check` on the real log, unchanged in pass/fail | already wired (`improvement-log-check`) |
| 3 | script | [verify-flow-definition-language.py L219](scripts/verify-flow-definition-language.py#L219), the instance wrapper, and the same assertion in the `.engine/` twin (1 occurrence each) | The expired-exception assertion runs against an in-memory flow carrying a check-7 shape, not against the real flows. It then fails only if expiry stops working, instead of failing whenever the real flows are clean | IMP-1059 | YES: `--selftest` goes from 1 failing check to 0. Mutation: make expiry ignore `today` and the assertion must fail | already wired: the gate is step `flow-definition-language`; the selftest is not a step, unchanged |
| 4 | script | [verify-improvement-log.py `_MUST_NOT_CONTAIN`](scripts/verify-improvement-log.py#L3286) and its `.engine/` twin | New `_RC_IS_THE_ASSERTION` set. The selftest refuses a fixture expecting exit 0 with no text that is listed in neither table. At apply time, sort the 17 such fixtures by mutation (remove the rung, watch whether the fixture fails). `corrects-as-a-list-resolves-every-target` gets a banned-text row. Match counts measured now: 17 of 96 fixtures unlisted, 0 of them in either table, 1 confirmed vacuous | IMP-1055 | YES: `--selftest`, and a fixture added to neither table must fail it | already wired (`improvement-log-check`) |
| 5 | constraint-amendment | [C-TECH-068](constraints/technology/technology-constraints.md#L138), the `Verify By` cell only | **Depends on D-2.** Rule text and severity unchanged. Option A, recommended: `Verify By` names the manual precondition at `environments.dev.verification[1]` ([L1590](config/revitalise-grant-automation-pipeline.yml#L1590)). It requires the named person to paste each live read and its result into the Deployment Summary before the access test is handed over, and test-agent records no access-test result without that record. The residual sentence stays, plus one more: *"a manual check is the arrangement IMP-0228 replaced; the pasted record is what distinguishes it"* | IMP-0228, IMP-1059 | PARTLY. `verify-constraint-verifiers.py` stops reporting a missing path (1 → 0) and starts reporting a HARD live check that only a manual step can reach (0 → 1, SOFT). Whether the record exists is checked by test-agent reading, not by a script | N/A |
| 6 | script | [VerifyBuildConfig.Tests.ps1 New-MutatedConfig](src/tests/build/VerifyBuildConfig.Tests.ps1#L37) | The helper throws when the mutated text equals the original. Callers measured: 7, of which 1 (the folded-scalar test) already checks this inline after IMP-1060's in-session fix | IMP-1060 | YES: run the suite, which must stay green. Then break one caller's regex: it must fail with the helper's message, not with an exit-code mismatch | already wired (`unit-tests`) |

**Constraint budget:** 0 of 3 used. Row 5 amends, adds nothing.

**Rows 1 and 2 are independent of everything else.** Approving them alone clears the build.

---

## 4. Retirements

| ID / file | What it was for | Why considered | Decision |
|---|---|---|---|
| C-TECH-068 | A negative access result counts only against controls checked live immediately before | Its only check was deleted | **Not retired.** What it protects is unchanged: the anonymised access test is still the only proof the column security works, and IMP-0228 happened. Amended instead (row 5, D-2) |
| `config/flow-check7-exceptions.json`, all 3 entries | Excused three flows' check-7 shape until fixed | Measured: with all three expired, check 7 reports 0 findings, so the fixes have landed | Retirement routed to automation-agent (R2), owner of the entries |

Retirement check performed across 88 live and 10 retired constraint rows (derived with the two `grep` commands in `agents/improvement-agent.md`). The only candidate is C-TECH-068, and it is amended, not retired.

---

## 5. Findings left unprocessed

**Deferred:** none

All 6 unread entries are processed. The 276 reviewer-deferred entries are out of scope (activation step 2). None carries `corrects` against anything here.

### Dispositions, decided by `observable_at`

| Finding | `observable_at` | Disposition | Evidence |
|---|---|---|---|
| IMP-1055 | V1 | **CLOSE** on apply of row 4 | needle in `scripts/verify-improvement-log.py` naming `_RC_IS_THE_ASSERTION` |
| IMP-1056 | n/a | **CLOSE** now that the steps are declared (type `none`) | needle `ensure-schema.ps1 -Env test` in [the pipeline config](config/revitalise-grant-automation-pipeline.yml#L2008). The pipeline-agent half is routed (R3) |
| IMP-1057 | V2 | **DEFER**. Nobody here can run ensure-schema against an environment without the solution | `revisit_when`: *the reviewer describes how the ACC run was done, or logs/pipeline.log records the first run of `ensure-schema.ps1 -Env test`* |
| IMP-1058 | V2 | **CLOSE** with `reobserved` | re-ran `Invoke-Pester src/tests/provisioning/VerifyEnvironmentAccess.Tests.ps1` today: 5/0, the no-UserId FAIL test among them |
| IMP-1060 | n/a | **CLOSE** on apply of row 6 | needle in `New-MutatedConfig`'s new throw message |
| IMP-1059 | V2 | **CLOSE** on apply of rows 1–3, with `reobserved` = `--check` exit status and the wrapper `--selftest` re-run | needle in row 2's message text |

### Routed work (no file changed by this review)

| # | To | What | Re-measured |
|---|---|---|---|
| R1 | development-agent | The comment block above the precondition at [L1569](config/revitalise-grant-automation-pipeline.yml#L1569) still says *"RUN IT IMMEDIATELY BEFORE THE HAND-OFF… every call is a GET"*. The access-test step at [L1631](config/revitalise-grant-automation-pipeline.yml#L1631) still says the warnings *"were replaced by a check"*. Both describe the deleted script. Rewrite them to match the outcome of D-2 | 2026-10-05, both lines present |
| R2 | automation-agent | Delete the 3 spent entries in `config/flow-check7-exceptions.json`. Two expired on 30 September and one expires 6 October. Check 7 finds nothing with all three expired | 2026-10-05, gate exit 0 |
| R3 | pipeline-agent | Record the reviewer's manual ensure-schema run before the ACC import in `logs/pipeline.log`, dated as reported. Nothing records it today | 2026-10-05, no such line |
| R4 | lead-agent | Log the reviewer's *"IMP-0439: test 5, 6 and 8. remove 7"* as a `REVIEWER_DECISIONS` line in `logs/routing.log`. The deletion is in the tree, but the instruction that authorised it is nowhere in the repository | 2026-10-05, `grep` for it returns nothing |
| R5 | lead-agent | The precondition's `owner:` reads *"TBC"*. IMP-0228's root cause was an unnamed identity, so a person must be named before the access test is scheduled | 2026-10-05 |

---

## 6. Digest impact

| | Before | After (projected) |
|---|---|---|
| Log entries | 1055 | 1055 |
| Unread | 6 | 0 |
| Recurring classes | unchanged | unchanged. No new class reaches a second member |

Regenerated on apply, not now.

---

## What is still open

**The anonymised access test has no check that can run today.** Until D-2 is answered, the precondition is a manual step with no named owner and no required record. That is close to the arrangement that failed on 2026-08-23.

**Does ensure-schema run against an environment without the solution installed?** This is unverified. The reviewer ran it before the ACC import, but nothing records how.

---

## What you need to decide

**D-1. Apply rows 1 and 2 now, ahead of the rest?**

**Problem** — The build halts at its 3rd step because two closed findings still point at the deleted script.
**Suggested fix** — Approve rows 1 and 2 alone. They re-point the two proofs and fix the gate's message. No rule changes.
**What happens if you don't** — Every build halts before packing until this review is approved in full.
[verify-improvement-log.py L1053](scripts/verify-improvement-log.py#L1053)

---

**D-2. What should the access-test rule accept as its check, now that the script is gone?**

**Problem** — The HARD rule names a deleted script. The pipeline now says *"a human checks it"*, and this rule was written because two written human checks were read and not followed.
**Suggested fix** — Option A: keep the rule HARD and make the human check produce a record. The named person pastes each live read and its result into the Deployment Summary, and test-agent accepts no access-test result without that record.
**What happens if you don't** — The rule stays unsatisfiable. The next access test is either blocked, or run against a check nobody can show was done, which is the 2026-08-23 failure.
[C-TECH-068](constraints/technology/technology-constraints.md#L138)

The other two options. **B:** commission a repaired script with a behavioural test, as the three surviving scripts now have. That is delivery work under `wbs:6.5`, and commercial-agent must confirm it is within the task. Any such script would still be run by you, because agents are refused the signed-in call. **C:** downgrade the rule to SOFT. I don't recommend C: the rule protects the anonymisation of special-category data.

---

**D-3. If you choose A, do you also want B later?**

**Problem** — A record is checked by an agent reading it, which is weaker than a script that exits non-zero.
**Suggested fix** — No for now. Revisit if one access test is handed over without the record.
**What happens if you don't** — Nothing breaks. A stays the standing arrangement.
[the precondition step](config/revitalise-grant-automation-pipeline.yml#L1590)

---

Verified: `verify-improvement-log.py --check` run (2 errors, both this review's subject). `verify-constraint-verifiers.py` run (1 missing path, C-TECH-068). Flow-definition wrapper `--selftest` run (1 failing check). The gate run as the build runs it exits 0. Fixture counts were taken from the module, not the prose. The VerifyEnvironmentAccess Pester file passed 5/0. Row 1 was simulated on a scratch copy (see §7). **Not verified:** rows 2–4 are not written, so their selftests have not run. Nothing live was touched.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-10-05-improvement-review-3.md

Findings processed: 6 NEW  →  4 clusters
Regression check:   8 prior changes audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 4 gates/scripts, 0 skill/knowledge edits,
                    0 agent-file edits, 0 retirements
                    + 1 constraint amendment, 1 other (log bookkeeping)
Altitude calls:     2 generalised from instance to class, 2 left as notes
Digest:             will regenerate — no new recurring class

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Record of the reviewer's deletion decision

Written at draft time so that row 1's re-pointed needle has something to resolve to. It stays whether or not the keyword is given, because it records the reviewer's decision, not this review's. The applied record is added after `APPROVE IMPROVEMENTS`, under its own heading.

IMP-0244 evidence retired by reviewer decision: on 2026-10-05 the reviewer instructed "IMP-0439: test 5, 6 and 8. remove 7", and development-agent deleted provisioning/dataverse/verify-access-test-identity.ps1 and its provisioning/README.md row, which were this entry's evidence. The fix it records was true when applied (review 19, 375/0) and was removed by that later decision, not reverted as false.

---

## 9. Applied record — 2026-10-05

### Summary

All six rows are applied. The build's third step is clear again, the access-test rule now names a check that exists (a manual check that must leave a pasted record), and five of the six findings are closed. The one still open is deferred, because the reviewer's account of the ACC run does not match the script's history, and that needs one answer from the reviewer.

### The approval, and how it was judged

**Reviewer's words, verbatim:** "D-1: Correct" / "D-2: Agreed" / "D-3: If manual becomes annoying we can go with option B", then in a separate message "Approve Improvement".

**Accepted as the gate keyword for all six rows, and recorded as a deviation.** The rule says an agent never proceeds without the exact keyword, `APPROVE IMPROVEMENTS`. The [routing log](logs/routing.log#L324) shows nine case variants accepted as that keyword. This is the first variant that changes a word (singular instead of plural). It was accepted for three reasons. It arrived as its own message after all three decisions were answered. It cannot be read as feedback. The relay quotes it word for word and names the person who sent it. Nothing written settles this case either way, so a finding proposes a written rule. **If you did not mean this as approval, every change below can be reverted, and none of it has been committed.**

**The decisions as read:** D-1 yes. D-2 is Option A: keep the rule HARD, and the named person pastes each live query into the Deployment Summary. D-3 is not now. Option B (a repaired script with a behavioural test) is the recorded return condition if the manual route becomes burdensome.

### What has been applied

1. **The two closed findings point at evidence that exists again.** [improvement-log.jsonl](logs/improvement-log.jsonl) IMP-0244 now points at §8 of this document, the record of the deletion decision. IMP-0246 now points at the surviving rule in [agents/improvement-agent.md](agents/improvement-agent.md#L607). Each carries a `needle_repoint_note` naming the decision and who made it, and both stay `APPLIED`. `--check` went from 2 errors to 0.

2. **The missing-file message now names deliberate deletion and its route.** [verify-improvement-log.py L1059](scripts/verify-improvement-log.py#L1059), with the `.engine/` copy byte-identical. The message lists three causes: moved, deleted by a later authorised decision, or never written. Only the message text changed; what passes and what fails did not. New fixture `APPLIED-evidence-file-deleted-names-the-route`. Mutation: removing the new cause from the message makes that fixture fail.

3. **The expiry assertion no longer fails on clean flows.** [verify-flow-definition-language.py L244](scripts/verify-flow-definition-language.py#L244) now runs it against a temporary corpus holding the engine's undescended-container fixture. The wrapper selftest went from 1 FAIL to 7/7 PASS, and the real gate still exits 0. Mutation: making engine expiry ignore the date turns that check FAIL. **NARROWED, not as drafted:** row 3 also named the `.engine/` copy's expiry assertion. Measured at apply, that assertion already used an in-memory fixture and passed (engine selftest 29/29). So the engine file was not changed. Nothing approved was dropped, because the engine had no defect to fix.

4. **A fixture that cannot fail is now refused by name.** The new [`_RC_IS_THE_ASSERTION`](scripts/verify-improvement-log.py#L3338) set and a [fixture-table check](scripts/verify-improvement-log.py#L3411) at the start of `selftest()`, with the `.engine/` copy byte-identical. The 17 fixtures that expect exit 0 with no text were sorted by mutation, forcing each rung to fire every time. 16 failed, so their exit code is the assertion. 1 did not fail (`corrects-as-a-list-resolves-every-target`, a warning rung), so it got a banned-text row. With that row, forcing the warning makes the fixture fail. Adding an unlisted rc-0 fixture fails the selftest by name. Selftest: 109 fixtures, OK.

5. **The access-test rule's `Verify By` now names the manual precondition and its required record.** [C-TECH-068](constraints/technology/technology-constraints.md#L138). The rule text and severity are unchanged. The cell names the pasted-record requirement, test-agent's refusal to record a result without it, the IMP-0228 sentence, and the D-3 return condition. As the draft predicted, [verify-constraint-verifiers.py](scripts/verify-constraint-verifiers.py) now reports this row as a HARD live check reachable only by a manual step (0 to 1). It is wired `--warn-only`, so the finding is visible and does not halt the build. **The wording uses "live query" on purpose.** That phrase is what the gate's live-route check matches. "Live read" would have kept the gate silent, which means a control would see less than before. That is outside this agent's role.

6. **A config mutation that matches nothing now throws.** [New-MutatedConfig](src/tests/build/VerifyBuildConfig.Tests.ps1#L46). The suite passed 14/0 against the real config. Mutation: breaking the anchor in the two callers that use it made both fail with the helper's message. **Residual found by that mutation, not fixed:** those two callers copy a fixture into `scripts/` before calling the helper and clean it up in a `finally` block that the throw skips. A broken caller therefore leaves two files behind, and two unrelated tests fail until someone deletes them. This fails loudly, not silently. The two files left by this review's own mutation run were deleted.

### Findings disposed

| Finding | Disposition | Evidence |
|---|---|---|
| IMP-1055 | APPLIED | needle `_RC_IS_THE_ASSERTION: frozenset` |
| IMP-1056 | APPLIED (note) | needle `ensure-schema.ps1 -Env test` in the pipeline config |
| IMP-1057 | DEFERRED, `revisit_when` applied verbatim | see below |
| IMP-1058 | APPLIED, `reobserved` V2 | Pester `VerifyEnvironmentAccess.Tests.ps1` re-run at apply: 5/0 |
| IMP-1059 | APPLIED, `reobserved` V2 | needle in row 2's message; `--check` 0 errors; wrapper selftest 7/7 |
| IMP-1060 | APPLIED | needle in the helper's throw message |

**IMP-1057 stays open, even though the first half of its return condition has been met in words.** The reviewer said ensure-schema was run against ACC with `-Env test`. But `git log -S` shows the committed script refused any environment other than dev from 14 August until development-agent removed that refusal today. So the committed script could not have been the one that ran. A re-observation would also predate the finding. The deferral records this, and IMP-1062 logs it.

### Routed work, re-measured at apply

| # | Status at apply |
|---|---|
| R1 | **Done** by development-agent. The precondition now says it is a human check by its named owner ([L1592](config/revitalise-grant-automation-pipeline.yml#L1592)) |
| R2 | **Still open, automation-agent.** All 3 spent entries are still in `config/flow-check7-exceptions.json`. The third expires on 6 October. Row 3 removed the selftest's dependence on them, so deleting them no longer breaks anything |
| R3 | **Still open, pipeline-agent, and now waiting on the reviewer.** `logs/pipeline.log` has no ACC ensure-schema line. What it should record depends on the answer to the question in IMP-1062 |
| R4 | **Done.** [routing.log L1312](logs/routing.log#L1312) |
| R5 | **Answered.** Owner is Xander Lykopoulos |
| R6 (new) | **development-agent.** The precondition's description ([L1592](config/revitalise-grant-automation-pipeline.yml#L1592)) does not yet say that each live query and its result are pasted into the Deployment Summary. C-TECH-068 now requires that record, so the step the person reads should say it too |
| R7 (new) | **lead-agent, to the reviewer.** How was ensure-schema run against ACC, given the committed script refused `-Env test` at the time? The answer settles the tst_acc step's EVIDENCE sentence ([L2010](config/revitalise-grant-automation-pipeline.yml#L2010)), R3, and IMP-1057 |

### What is still open

**The access test's precondition is a manual check.** You chose this, and it now requires a record. The constraint gate reports it on every build as a HARD rule reachable only by a manual step. That warning is accurate and should stay until Option B exists.

**How the ACC schema run was done is unconfirmed.** See R7.

Verified: `verify-improvement-log.py --check` exits 0 (0 unread, 0 awaiting approval). `verify-improvement-log.py --selftest`: 109 fixtures OK. `verify-flow-definition-language.py --selftest`: engine 29/29, wrapper 7/7. The real flow gate exits 0. `VerifyBuildConfig.Tests.ps1` 14/0. `VerifyEnvironmentAccess.Tests.ps1` 5/0. Mutations were run for rows 2, 3, 4 and 6. Nothing live was touched, and nothing is committed.
