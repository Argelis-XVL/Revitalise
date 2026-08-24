# Improvement Review 18 — 2026-08-23

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 6 unread → 4 clusters (4 `blocker`, 2 `rework`)
**Trigger:** blocker escalation — [IMP-0228](../../logs/improvement-log.jsonl#L225), appended by pipeline-agent during today's trustee-portal deploy to DEV. Five further unread findings landed from other sessions while this review was being written and are included; see section 6.
**Gate:** `APPROVE IMPROVEMENTS`
**WBS:** `6.1–6.5` (trustee portal), plus evidence rules touching `0.5`, `0.7`, `0.10` and `2.8`.

**Status:** ~~AWAITING `APPROVE IMPROVEMENTS`.~~ **APPROVED and APPLIED 2026-08-23** by the
reviewer (Xander Lykopoulos). All 11 changes are in the tree. See section 8 — including two
findings deliberately **not** closed, seven that arrived mid-application and are out of scope,
one correction to this review's own text, and one pre-existing gate this review had to re-scope
to keep the suite green.

**Sections 1–7 are the record as written before approval and are deliberately left in the present
tense.** Where they say a thing "is" true, read it as true at the time of the finding; section 8
states what is true now.

---

## The headline

**Three separate mechanisms are currently telling you the trustee access test is fine. It has not been run, and as staged it cannot produce a truthful answer.** The account you are about to sign in as has been granted read access to the very columns the test exists to prove are hidden. The project status snapshot reports the test as not outstanding. The contract's own task tracker reports the task complete. None of the three is lying deliberately; each defaults to reassurance when it has no evidence.

**Yes, a mechanical gate is warranted, and the evidence is unusually direct: the prose reminder did not merely fail, it caused this.** Five hours ago a written precondition was added to the test step telling whoever staged it to "confirm membership live and add one identity if there is none." It never said *which* identity. Someone read it, added one, and picked the trustee's own test account — the single account that must never be added.

**But no gate I can write unblocks this afternoon, and I would rather say so than let a proposal look like a remedy.** What makes the account safe again is removing that access — a one-minute action in the maker portal that only you can perform. A check confirms the removal; it cannot perform it.

**One thing nobody has checked, and it decides whether the removal is even sufficient.** The profile's other member is a *team*. If the trustee test account also belongs to that team, removing the direct grant changes nothing — the access simply arrives by the other route. That query is the most urgent item in this document and it is first in section 5.

**A second, unrelated group of findings arrived while this was being written, and it lands on the one script whose numbers nobody is permitted to question.** Every project-status answer must be rendered from a single snapshot script, with [no figure that the snapshot does not contain](../../agents/pm-agent.md#L34) — and [once that script exits cleanly a cheaper model is authorised](../../agents/pm-agent.md#L4) to repeat its output. Run today it reports 84 invoiced hours where all three commercial gates report 64, and reports the trustee access test as not outstanding. **Not one number it prints is checked by anything**, and the 84 is the same 20-hour over-count a blocker closed three days ago in three other scripts.

---

## 1. Regression check — did the last reviews' changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Written precondition on the sign-in test step, [pipeline.yml L821](../../config/revitalise-grant-automation-pipeline.yml#L821) | 2026-08-23 (review 16) | live security-state divergence | **YES — within ~5 hours, and today's blocker *is* the recurrence** | **Wrong altitude.** It asked for "one identity" and named no exclusion. Escalate to a gate |
| Source-side membership gate, [verify-column-security-membership.py](../../scripts/verify-column-security-membership.py#L8) | 2026-08-21 (review 5) | the same profile's membership direction | **YES — and the gate could not fire** | **Mis-scoped, not broken.** It reads solution source; this grant exists only in the live environment and in no file |
| Tightening task 6.5's evidence rule from a forward reference to a file check | 2026-08-19 | evidence rule satisfied by something that is not the deliverable | **YES — same task, second time** | **Half-fixed.** It closed the "script only declares intent" hole and left the "human step never happened" hole open |
| Closure evidence rules — a defect stays open until re-observed where it was visible | 2026-08-23 (reviews 16, 17) | closing findings on prose | NO | **Working.** Four findings are held open under it rather than declared fixed |
| One shared ledger reader, plus a cross-check that the readers agree — [the policy](../../scripts/lib/worklog.py#L17) and [the gate](../../scripts/ci/verify-pm-gates.sh#L112) | 2026-08-20 | two readers of one file compute different totals | **YES — the identical 84-vs-64 over-count, in a fourth script** | **The gate ran and could not fire.** It names its three readers by hand. The fourth is [started by the same suite](../../scripts/ci/verify-pm-gates.sh#L43), but only to see whether it crashes |
| [C-COM-005](../../constraints/commercial/commercial-constraints.md#L43)'s verifier — a claimed status is compared against evidence, never taken as fact | 2026-08-18 | a status claim believed without checking | **YES — for one of the three claim values** | **Two-thirds wired.** "Done" and blank are compared; "Partially done" is never compared against anything |

**The second row is not a failure of that gate, and the distinction shapes the fix.** [The script says so itself](../../scripts/verify-column-security-membership.py#L24): "no gate over solution source can see this." It correctly compares what the packaged solution declares. The grant added this morning was typed into a web portal by a human after the deploy, and no file anywhere expresses it. That is a right tool aimed at the wrong half, and the answer is a second check on the live half — not a repair of this one.

**Why today counts as the sixth time, not the first.** The underlying class — the environment quietly holding a state no file describes — has now produced six findings. The specific version, *someone becomes a member of the profile whose entire control is that nobody is a member*, has now produced two: [the first](../../logs/improvement-log.jsonl#L150) was an agent about to write the instruction, caught before it shipped; this one is a real account in the real environment, caught by chance.

**Caught by chance is the phrase that matters.** Nothing scheduled this discovery — the deploying agent happened to re-read the membership while confirming something else. Had it not, the test would have run this afternoon, the trustee would have seen the hidden columns filled in, and the only two available readings would have been "the privacy control is broken" or "the control works and the test is lying," with no way to tell them apart from inside the test.

**The fifth row is the most instructive regression result I have had to write, because the fix was a good one.** Three days ago the same 20-hour over-count appeared in two scripts out of three, was traced correctly, and was closed properly: the rule moved into [one shared module](../../scripts/lib/worklog.py#L33), the two duplicate implementations were deleted, a [cross-check](../../scripts/ci/verify-pm-gates.sh#L112) was added so the readers can never again disagree silently, and [a fixture](../../scripts/ci/verify-pm-gates.sh#L137) proves the check discriminates. It runs [on every CI run](../../.github/workflows/ci.yml#L441). It passed today, while the number was wrong.

**It could not have caught this, because the fix enumerated its readers by hand and the repository grew a fourth.** The module's own docstring states the policy — [no script may compute the superseded set itself](../../scripts/lib/worklog.py#L17) — and a policy stated in a docstring is enforced by whoever reads the docstring. Nine files mention the ledger; four call the module; [the status renderer parses it itself](../../scripts/collect-project-status.py#L79) and reproduces exactly the arithmetic that was deleted from the other three.

**The altitude lesson is specific: the fix generalised the *rule* and hand-wrote the *list*.** That is the same shape as [the promotion skill's own worked example](../../skills/how-to-promote-a-finding.md#L73) — derive the list from source, never hand-write it. A gate that names three scripts is an instance gate wearing a class gate's clothes.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: platform-state-divergence  (x6; this instance IMP-0228, direct
           precedent IMP-0153, adjacent IMP-0110 / IMP-0221)
Altitude:   CLASS — second instance of "a principal became a member of the profile
            whose control is non-membership", sixth of the live-divergence class.
            The altitude rule forbids a third prose reminder, and two already sit in
            the same step of the same file.
Ladder row: "a tool could catch it mechanically" + "second instance -> generalise"
Becomes:    provisioning/dataverse/verify-access-test-identity.ps1 — read-only live
            pre-flight asserting a declared test identity holds NONE of the access
            the test asserts is absent, across all four grant routes, with the
            profile list enumerated live rather than named; declared as the
            precondition of the sign-in step; plus one constraint row.
Retires:    the two prose warning blocks in the sign-in step (L790-792, L808-835) —
            REPLACED by the check, not supplemented by a third.
Cites:      IMP-0228, IMP-0153, IMP-0221, IMP-0110
Residual:   The check is a moment in time. Nothing stops a grant being added between
            the check passing and the person signing in — which is why it must run
            immediately before the hand-off, not at deploy time. It also cannot see
            grants made outside Dataverse's own tables; a tenant-level admin role
            appears on none of the four routes.

CLUSTER B: a derived status defaults to the reassuring value  (IMP-0229, IMP-0230,
           IMP-0233; lineage gate-reassures-wrongly x11, gate-cannot-fail x28)
Altitude:   CLASS — three scripts, one shape: on the path where no comparison
            happens, the field is written with the value that means "fine".
            No manual rule -> complete. A phrasing the regex misses -> V4 closed.
            A claim of "Partially done" -> compared against nothing, reads "agrees".
            Also the second recorded instance for task 6.5 specifically, which the
            promotion skill treats as stronger evidence than two unrelated ones.
Ladder row: "second instance -> generalise" + "a tool could catch it mechanically"
Becomes:    (i) the three tasks whose contracted deliverable names a human step and
            whose evidence rules carry no `manual` entry get one; (ii) a check that
            fails when any task's deliverable names a human step and its rules carry
            no `manual` entry — both sides derived from source, so a new task is
            covered without anyone editing the check; (iii) the V4 status field is
            inverted to require an affirmative "performed" match rather than
            recognising two spellings of "outstanding"; (iv) the verdict chain gains
            the missing "partial" branches, in both directions.
Retires:    nothing — no gate existed for any of the three halves.
Cites:      IMP-0229, IMP-0230, IMP-0233
Residual:   A `manual` rule records that a human step is REQUIRED, not that it
            happened. The task reads complete_pending_manual until someone records
            the result; nothing yet forces that record to be dated or attributed.
            Named here deliberately as the next rung, not built in this review.
            And (iv) closes the one claim value in use — the chain is still a list of
            branches, so a claim spelling nobody has typed yet falls through it the
            same way. A test that asserts every claim value has a branch would close
            the class; it needs the claim vocabulary declared in one place first.

CLUSTER C: declared-policy-not-mechanically-enforced  (x5; IMP-0231)
Altitude:   INSTANCE-plus — fifth in the class, but the first about the commercial
            ledger, and the mechanism is a two-line staleness comparison.
Ladder row: "a tool could catch it mechanically"
Becomes:    a staleness check in verify-worklog.py comparing the newest DEV deploy
            success against the newest worklog entry.
Retires:    nothing
Cites:      IMP-0231
Residual:   The check flags that a commercial pass is overdue; it cannot make the
            pass happen, and the threshold is a judgement I am asking you to set.

CLUSTER D: two invocation paths disagree  (x9; IMP-0232, direct precedent IMP-0093)
Altitude:   CLASS, and the least ambiguous call in this document — the SAME 84-vs-64
            over-count as its precedent, in a fourth script, three days after a fix
            that migrated the three scripts it named and wrote the policy in a
            docstring. An instance patch here is forbidden outright.
Ladder row: "second instance -> generalise. Instance patches are forbidden here."
Becomes:    section 7 of verify-pm-gates.sh stops naming its readers and DERIVES
            them: every file that parses the ledger and produces an hours figure
            must obtain it from scripts/lib/worklog.py, and all of them must agree.
            Plus the one-line migration that makes the renderer pass it.
Retires:    the hand-written three-reader list in section 7 — replaced, not extended.
Cites:      IMP-0232, IMP-0093
Residual:   Two files parse the ledger for something that is NOT hours —
            reconstruct-worklog.py reads which evidence has already been claimed,
            and the library is the library. They must be declared exempt with a
            stated reason inside the gate, or the check degrades into a grep for a
            filename. Two more mention the path only in prose and must not be
            flagged, which is why the check keys on parsing rather than mentioning.
```

### The property behind cluster A, stated independently of this incident

> A test that proves someone **cannot** see something is only evidence if that person's lack of access has been confirmed live, by every route that could grant it, immediately before they are told to run it — and the identity used as the comparison case must be a different person from the one under test.

That covers both prose warnings currently in the file, and it would cover the next access test against any profile, role or table without being rewritten.

### What I found while checking cluster B, which is better news than the finding

**The mechanism the finding asks for already exists.** [`derive-wbs-state.py`](../../scripts/derive-wbs-state.py#L165) already downgrades any task carrying a `manual` evidence rule to `complete_pending_manual` instead of `complete`, and 22 tasks already use it. The proposal to build a new evidence kind is unnecessary.

**The actual defect is smaller and worse: task 6.5's rule list simply omits it.** It carries two file-existence rules and no `manual` rule, so the machinery built precisely to prevent this reads it as complete.

**And it is not alone — I checked all 61 tasks rather than assuming.** Three tasks name a human verification in their own contracted deliverable and carry no `manual` rule:

| Task | Contracted deliverable | Currently derives as |
|---|---|---|
| `0.5` | Security roles + field-security profile + **DPO sign-off** | complete, from files alone |
| `2.8` | Test results / **sign-off** | complete, from files alone |
| `6.5` | Shared app + **access test** | complete, from files alone |

**Task 0.5 is the one I would not have predicted.** It is the sign-off on the security roles and the field-security profile — the very profile at the centre of today's blocker. The task whose human review exists to catch a misconfigured profile is itself satisfiable without the review.

### The fourth item in cluster B is worse than reported, and in your favour

**The finding named one task; there are two, and both understate what has been delivered.** [The verdict chain](../../scripts/derive-wbs-state.py#L176) compares a claim of "Done" against the evidence, and compares a blank status against the evidence, and never compares "Partially done" against anything at all. I ran the full distribution rather than trusting the example: three tasks carry a partial claim, and **two of them — `0.7` and `0.10` — have every one of their evidence rules resolving present.** Both read `agrees`.

**So the count of disagreements you have been shown is short by two, in the direction nobody checks for.** Ten disagreements are reported today; twelve exist. Underclaims matter less than overclaims for delivery risk, but they are the half of [C-COM-005](../../constraints/commercial/commercial-constraints.md#L43) that protects the invoice rather than the client, and that rule names this exact script as its verifier.

### The property behind cluster D, stated independently of this incident

> Where two pieces of code answer the same question about the same file, the list of them is derived from the file, never written down — because the list is what goes stale, not the rule.

**The three-reader list in section 7 was correct on the day it was written.** It is wrong now for the ordinary reason: a fourth reader was added, by someone who had no way to know a hand-written list elsewhere needed editing too. Deriving the list means the fifth reader is covered without anyone remembering this document exists.

---

## 3. Proposed changes

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | script | `provisioning/dataverse/verify-access-test-identity.ps1` (new, read-only) | Asserts the declared test identity holds only its declared role and belongs to no column-security profile by **either** membership route, and is not the comparison identity | IMP-0228, IMP-0153, IMP-0221 | YES — exits non-zero, one `PASS`/`FAIL` line per route |
| 2 | settings | `provisioning/deploymentSettings/dev-access-test-settings.json` (new) | Declares the DEV test identity, its permitted role and the comparison identity — identifiers only, no secrets | IMP-0228 | YES — the script fails fast if absent or unresolved |
| 3 | config | [pipeline.yml sign-in step](../../config/revitalise-grant-automation-pipeline.yml#L787) | The two prose warnings are replaced by change 1 as a declared precondition | IMP-0228, IMP-0221 | YES — `verify-pipeline-config.py` already reads declared script paths |
| 4 | constraint | `constraints/technology/technology-constraints.md` — new row `C-TECH-068`, HARD | Carries the cluster-A property: a negative result is evidence only against a live-verified control pair | IMP-0228, IMP-0153, IMP-0221, IMP-0110 | YES — `Verify By` names change 1 |
| 5 | contract | [evidence-map.json](../../contract/evidence-map.json#L378) | Add the missing `manual` rule to tasks `0.5`, `2.8` and `6.5` | IMP-0230 | YES — `derive-wbs-state.py` already honours the kind |
| 6 | script | `scripts/verify-wbs-chain.py` | New check: a task whose contracted deliverable names a human step must carry a `manual` rule. Both sides read from source | IMP-0230 | YES — fails on the three tasks above before change 5 |
| 7 | script | [collect-project-status.py L93](../../scripts/collect-project-status.py#L93) | Invert the V4 field: require an affirmative "performed/confirmed" match, default to outstanding | IMP-0229 | YES — a fixture per phrasing found in the log |
| 8 | script | [verify-worklog.py](../../scripts/verify-worklog.py#L82) | Staleness check: newest DEV deploy success against newest worklog entry | IMP-0231 | YES — threshold-driven, testable both sides |
| 9 | script | [collect-project-status.py L70-81](../../scripts/collect-project-status.py#L79) | Replace the hand-rolled ledger loop with the shared module's [`load()`](../../scripts/lib/worklog.py#L33) and [`invoiced_to_date()`](../../scripts/lib/worklog.py#L71) | IMP-0232, IMP-0093 | YES — its figure must equal the other three readers' |
| 10 | script | [verify-pm-gates.sh section 7](../../scripts/ci/verify-pm-gates.sh#L112) | Derive the reader list from source instead of naming three; every hours-producing reader must use the module and all must agree; non-hours readers declared exempt with a reason | IMP-0232, IMP-0093 | YES — fails on change 9's script *before* change 9 lands |
| 11 | script | [derive-wbs-state.py L176-182](../../scripts/derive-wbs-state.py#L176) | Add the missing `partial` branches: against complete → UNDERCLAIM, against not_started → OVERCLAIM, against manual_only/unknown → unverifiable | IMP-0233 | YES — two tasks change verdict today; one fixture per branch |

**One new constraint against a cap of three**, per [the anti-bloat limit](../../constraints/README.md#L130). Eleven changes, one rule.

**Changes 9 and 10 land in that order**, for the same reason as 5 and 6: change 10 is designed to fail on exactly the defect change 9 fixes, so introducing the gate first turns CI red on a commit that fixes nothing.

**I considered a second constraint row for cluster D and decided against it.** The class has nine instances and would justify one on the ladder. But the enforcement is a source-derived check that extends itself, and a constraint row restating "readers must agree" would add a sentence, not a check — its [`Verify By`](../../constraints/README.md#L122) would name change 10 and nothing else. Where the mechanical home is sufficient, the row is the bloat the cap exists to prevent.

**Changes 1 and 4 must land together or not at all.** [`verify-constraint-verifiers.py`](../../scripts/verify-constraint-verifiers.py) reads every repository path a constraint's `Verify By` names and fails if it is absent. A constraint row naming a script written five minutes later turns the build red in between — the failure that made [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) unsatisfiable for a day, and avoidable purely by ordering.

**Changes 5 and 6 must land in that order**, or change 6 fails the build on the three tasks change 5 fixes. That is the correct behaviour of the gate, but not on the commit that introduces it.

### Why a new constraint row rather than amending an existing one

The finding suggested amending [C-TECH-064](../../constraints/technology/technology-constraints.md#L134), and I looked hard at that first. That rule governs *the environment matching what was deployed*, checked *after a deploy*. This property governs *a test's controls*, checked *before a human is asked to run it* — a different subject at a different moment. C-TECH-064 is also already the longest row in the file and has been narrowed once for becoming unsatisfiable through exactly this kind of accumulation.

**And there is a real gap where it belongs.** I grepped every constraint file for "positive control" and "negative control" and found nothing. The idea that an empty result proves nothing until you have watched the same query return something has now produced three findings and lives only in a prose paragraph inside a pipeline config.

---

## 4. Retirements

**Checked; no constraint is a retirement candidate this review.** The retirement here is prose: the two warning paragraphs in the sign-in step are replaced by change 3, not left standing beside it. Leaving them would be the accumulation the altitude rule exists to stop — a third warning in a step where two were already read and not followed.

**[verify-column-security-membership.py](../../scripts/verify-column-security-membership.py#L8) is explicitly *not* retired, and the distinction matters.** It catches a bad membership *in the solution before it ships*; the new check catches one *in the environment after it ships*. Neither subsumes the other, and retiring the source-side gate because a live gate now exists would lose the earlier and cheaper catch.

**One mechanical retirement, added by cluster D: the hand-written three-reader list in [section 7](../../scripts/ci/verify-pm-gates.sh#L112).** Change 10 replaces it rather than appending a fourth name, which is the altitude rule applied to a gate instead of a constraint — a list that has now gone stale once will go stale again, and adding the missing entry is the instance patch.

**The replacement must be proved not to lose coverage, and the proof already exists in the repository.** [The superseded-seed fixture](../../scripts/ci/verify-pm-gates.sh#L137) asserts that a corrected 10-hour seed reports as 0 h and as 10 h once the correction line is removed — it discriminates, which is what makes it a real check rather than an assertion that the code ran. **That fixture must still fail under change 10, and the three original readers must still be compared**; a generalisation that widens the reader list while weakening the arithmetic assertion would be a regression dressed as a promotion.

---

## 5. What you need to decide

**First — before anything else here — one query, then one removal.**

The finding records the trustee test account as a direct member of the restricted profile. The deployment summary records the profile's *intended* single member as a team. Nobody has checked whether the trustee account is **also in that team** — and if it is, removing the direct grant leaves the access fully intact by the other route and the test still produces a false pass.

So: read both membership routes, remove whatever puts the trustee account on either, re-read to confirm. The removal is a write, which this session cannot perform — live writes from here are refused by the harness, across six recorded findings. It is a maker-portal action and it is yours.

**Second — approve the gate, knowing it does not unblock this afternoon.**

To answer the question directly: the check can be written and run today. It is read-only, it queries what pipeline-agent already queried by hand this morning, and it could exist within the hour.

But it confirms the staging rather than repairing it. If you want the test to run this afternoon, the removal above is the entire critical path and the gate can follow it. If you would rather the test not run until it cannot silently lie, the gate lands first. **My recommendation is to do the removal now and let the gate follow**, because the gate's value is in the second, third and tenth staging of this test, not this one — this one already has your attention, which is the condition that will not repeat.

**Third — a constraint on how the script must be built, which I would otherwise have got wrong.**

A new script under `provisioning/dataverse/` taking `-Env dev` **cannot run in DEV**. [`Get-ProvisioningSettings`](../../provisioning/common/provisioning-common.ps1#L47) [throws by design](../../provisioning/common/provisioning-common.ps1#L53) for `dev` — a DEV settings file must not exist, and a test asserts the throw. Six pipeline steps are already marked `manual` for this reason, [with the cause spelled out](../../config/revitalise-grant-automation-pipeline.yml#L643).

The way through is the pattern the repository already uses three times: a dedicated DEV settings file read directly, plus a `-SettingsPath` override, exactly as [ensure-auditing.ps1 does](../../provisioning/dataverse/ensure-auditing.ps1#L82). That is why change 2 is its own line item. **Written the ordinary way, this gate would have joined the list of steps that have never once executed** — a gate that cannot fail, added in a review about a gate that could not fire.

**Fourth — should the comparison identity be pinned by name?**

The instruction that caused this said "add one identity." The obvious hardening is to name the intended comparison account in the settings file so the instruction can no longer be satisfied by the wrong person. Change 2 assumes yes.

The trade-off is that it fixes the comparison account for DEV until someone edits the file. I think that is right — it is a test fixture, not a person's standing access — but it is your call. The alternative is a script that only checks the two are *different* without caring which.

**Fifth — how stale is too stale for the commercial ledger?**

Change 8 needs a threshold and I will not invent one. The evidence is that six DEV deploy successes have landed since the ledger's last entry, and the finding's own argument is that a same-day pass produces one clean cluster while a five-day gap produces eleven mixed ones.

Two days would enforce the finding's intent. Five would only catch the pathological case. **Is this a warning or a hard failure?** I would make it a warning — a stale ledger should not block a deploy — but that is a commercial judgement rather than a technical one.

**Sixth — may a script ever read the ledger without the shared module?**

Change 10 has to answer this to be writable. Two scripts parse the ledger for something other than hours: one reads which evidence has already been claimed so it does not propose the same work twice, and the module itself obviously parses it. Neither can produce the over-count, because neither computes a total.

The strict answer — everything goes through the module — is tidier and would mean rewriting a script that has no defect. **My recommendation is to exempt by name, with the reason written in the gate**, so the exemption is visible to the next person rather than being an absence. The weaker option is a check that only looks at scripts printing an hours figure, which is harder to keep honest.

**Seventh — two tasks are about to start reporting as underclaimed, and that is a claim you may want to correct instead.**

Change 11 makes tasks `0.7` and `0.10` report as UNDERCLAIM: both are marked "Partially done" in the WBS while every piece of evidence they name is present. The disagreement count goes from ten to twelve.

That is the gate working — but the honest resolution may be that the claims are simply out of date, in which case the fix is to update the two Status values and the disagreement disappears. **Do you want me to leave the disagreements standing as the record, or is updating those two claims a pm-agent task to dispatch after this?** I have not touched them: a claim is the client-facing baseline and editing one is not mine to do inside a rules review.

---

## 6. Scope, and a note on how it changed underneath me

**At activation the queue held one unread finding. By the time I checked the digest it held four. It now holds six.** Two more arrived from pm-agent after this document was already parked at its gate, and a second dispatch was sent to process one of them. I re-ran the queue gate again rather than trusting either earlier read, and both are included above.

That is worth recording as its own lesson, now twice over: **a strategic review long enough to be worth doing is long enough for its own scope to go stale**, and this repository runs on a synced shared path where two sessions are routinely live at once. I will append that as a finding on approval rather than leaving it as a paragraph nobody reads.

**Why the two late findings extended this document instead of opening a second one.** The dispatch that brought them asked for exactly that decision, and the deciding fact is overlap, not tidiness: they change the same two scripts this review already changes — [the status renderer](../../scripts/collect-project-status.py#L79) that change 7 edits at another line, and [the state deriver](../../scripts/derive-wbs-state.py#L176) whose behaviour cluster B depends on. Two review documents proposing edits to the same two files, each behind its own keyword, is how a repository ends up half-applied.

**The second reason is an altitude one, and it would have been invisible from inside a separate document.** Split across two reviews, one would have seen two instances of "the status defaults to reassuring" and the other one instance. Together they are three, in three different scripts, which is what moves the cluster from a pair of local fixes to a stated property. The promotion ladder only works if the clustering step sees the whole queue.

**Findings excluded, and why.** Nine entries sit in a non-final state and are out of scope by activation step 2. Eight carry an accepted deferral reason and are waiting on live observations, not on a keyword: IMP-0112, IMP-0152, IMP-0197, IMP-0205, IMP-0218, IMP-0221, IMP-0224, IMP-0227. One (IMP-0198) is parked at its own approval gate in [review 10](../../docs/improvements/2026-08-22-improvement-review-2.md) and needs the keyword sent against that document, not a second review here. I read none of them as fresh scope.

**One correction to my own earlier read, since it affected a stamp — and I had the wrong finding.** An earlier draft of this paragraph named IMP-0231. The entry the queue gate actually flags is **IMP-0221**, the deferred finding cluster A cites: its `reviewed_in` still named [review 16](../../docs/improvements/2026-08-23-improvement-review-4.md) while this review was the one that last worked on it. Its stamp moved here on approval; its deferral stands, because what it waits on is a live read. Recorded rather than quietly fixed: a wrong id in a review document is the kind of thing the next reader inherits as fact.

**Log disposition.** [IMP-0228](../../logs/improvement-log.jsonl#L225) and IMP-0230 are `observable_at: V4` — visible only in the live environment. Neither is closed by this review or by approving it. On approval each gains a `reviewed_in` stamp pointing here and a `revisit_when` naming the live re-read: for IMP-0228, the trustee account absent from both membership routes with the comparison member still in place. They close when someone reads that, not when the scripts are written. IMP-0229 and IMP-0231 are not level-restricted and close on their fixes landing with tests.

**The two late findings close on evidence available here, and that is worth stating precisely, because the last review to get this wrong closed a defect on a sentence it had just written.** [IMP-0232](../../logs/improvement-log.jsonl#L229) is `observable_at: n/a` and its symptom is a number this session reproduced by running the script — it closes when that same command prints 64 and the cross-check compares four readers instead of three. [IMP-0233](../../logs/improvement-log.jsonl#L230) is `observable_at: V1` and closes when the two tasks appear in the disagreement list. Both re-observations are commands anyone can run in this repository with no credentials, so neither needs a `revisit_when`.

**One open risk while this sits at the gate.** IMP-0228 carries no `reviewed_in` stamp yet, because stamping is an edit and edits wait for the keyword. Until then the queue cannot distinguish it from a finding nobody has opened, and another blocker dispatch could re-derive this analysis from scratch — which has cost this project a duplicated strategic-tier pass before. If the keyword is going to be delayed, stamping that one field early is worth more than the consistency it breaks.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-23-improvement-review-6.md

Findings processed: 6 NEW (unread: 4 blocker, 2 rework)  →  4 clusters
                    9 excluded: 8 reviewer-deferred, 1 awaiting-approval elsewhere
Regression check:   6 prior changes audited, 5 classes recurred
                    — 1 after a PROSE fix (escalating to a gate, this review)
                    — 1 after a GATE that is source-side and structurally could not fire
                    — 1 after a GATE that RAN, passed, and names its 3 readers by hand
                    — 1 after a HALF-fix to the same task's evidence rule
                    — 1 wired for 2 of its 3 claim values since 2026-08-18
Proposed:           1 constraint (cap 3), 2 new scripts/settings + 7 script/config edits,
                    1 contract evidence-map edit,
                    0 skill/knowledge edits, 0 agent-file edits,
                    0 constraint retirements (2 prose warnings + 1 hand-written
                    reader list replaced, not extended)
Altitude calls:     3 generalised from instance to class, 1 left at instance-plus,
                    1 second constraint row considered and declined for a gate
Digest:             will regenerate — 230 lessons, 25 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

**Verification actually performed for this review:** the queue gate run three times, at activation, before writing, and again for the late findings (1 → 4 → 6 unread, explained in section 6); all 61 contracted tasks surveyed for human-verification language against their evidence rules, returning exactly three gaps; the existing `manual` evidence kind and its `complete_pending_manual` handling confirmed present and in use by 22 tasks; the DEV settings resolution traced through to its deliberate throw; the two prose warnings and review 16's precondition read in place at their cited lines; the source-side gate's own statement of scope read at its cited line; the absence of positive/negative-control language across every constraint file confirmed by grep.

**For the two late findings, both symptoms were reproduced rather than accepted.** The status renderer was run and prints 84.0 invoiced hours and `v4_outstanding: false`; the three commercial gates were run against the same file in the same working tree and print 64. The nine files mentioning the ledger were enumerated and classified by whether they actually parse it — four use the shared module, two parse it raw, two mention it only in prose, one is the module. The claim/evidence distribution was computed across all 61 tasks rather than checking the one task the finding named, which is how the second hidden underclaim (`0.10`) was found; the verdict chain's three branches were read directly. The cross-check gate was confirmed present, confirmed wired into CI, and confirmed to name its readers by hand.

**Not verified, and it is the load-bearing gap:** I did not read the live environment. This session holds no provisioning credentials, so the membership state described here is as pipeline-agent recorded it this morning and may already have changed. The team-membership question in section 5 is unanswered for the same reason. **Nothing in this document should be treated as a current statement of who can see those columns.**

**Also not verified:** none of the eleven proposed changes has been written or run — this document is a proposal at a gate, and the "mechanically verifiable" column states what each change would make checkable, not something already checked.

> ~~Superseded by section 8.~~ All eleven were written and run on approval, and each was also shown to fail on the defect it targets. Section 8 carries the numbers. This paragraph is left in place as the pre-approval record.

---

## 8. Applied — 2026-08-23

**All 11 changes landed and every gate in the suite passes.** The two live symptoms are gone: the status renderer printed 84 invoiced hours before and prints 64 now, and the trustee access test no longer reads as closed. **Three things are still open and one of them is the blocker itself** — the gate can now tell you the staging is wrong, and it still is.

### What landed

| # | Change | Where |
|---|---|---|
| 1 | Read-only live pre-flight, 4 access routes, profiles enumerated live | [verify-access-test-identity.ps1](../../provisioning/dataverse/verify-access-test-identity.ps1) (285 lines) |
| 2 | The two identities and the permitted role set, declared separately | [dev-access-test-settings.json](../../provisioning/deploymentSettings/dev-access-test-settings.json) |
| 3 | The check declared as the V4 step's precondition; both prose warnings gone | [pipeline.yml L840](../../config/revitalise-grant-automation-pipeline.yml#L840) |
| 4 | New HARD constraint carrying the cluster-A property | [C-TECH-068](../../constraints/technology/technology-constraints.md#L138) |
| 5 | `manual` rule added to tasks `0.5`, `2.8`, `6.5` | [evidence-map.json](../../contract/evidence-map.json) |
| 6 | A deliverable promising a human step must carry a `manual` rule | [verify-wbs-chain.py L127](../../scripts/verify-wbs-chain.py#L127) |
| 7 | V4 status inverted — silence now means outstanding | [collect-project-status.py L70](../../scripts/collect-project-status.py#L70) |
| 8 | Ledger-currency warning against the newest DEV deploy | [verify-worklog.py L285](../../scripts/verify-worklog.py#L285) |
| 9 | The renderer reads the ledger through the shared module | [collect-project-status.py L47](../../scripts/collect-project-status.py#L47) |
| 10 | Reader list derived from source; the hand-written list retired | [verify-ledger-readers.py](../../scripts/verify-ledger-readers.py) (233 lines), wired at [section 7](../../scripts/ci/verify-pm-gates.sh#L134) |
| 11 | The missing `partial` branches, plus unrecognised claim spellings | [derive-wbs-state.py L196](../../scripts/derive-wbs-state.py#L196) |

### What was actually verified, with numbers

**Every change was proved to discriminate, not merely to run.** A gate that passes on a clean tree has shown nothing; each of these was also shown to fail on the defect it targets.

1. **The status renderer now agrees with the other three readers.** It printed `84.0` before and `64.0` after, against `verify-worklog.py`, `verify-wbs-chain.py` and `compute-invoice.py` at 64. Section 7 now compares **four** readers, not three.

2. **The new reader gate catches the original defect.** Run against the pre-fix renderer it flags it as a raw parser; its `--selftest` rejects a synthetic raw parser, so it has been shown to go red. It also classifies all ten files that mention the ledger — 5 through the module, 2 exempt with stated reasons, 2 prose-only, 1 the module — and fails on any reader nobody has classified.

3. **The human-step gate flags exactly the three tasks and no others.** Run against the pre-change evidence-map it fails on `0.5`, `2.8` and `6.5`; on the fixed one it passes. The vocabulary matches 11 of the 61 contracted tasks, all 11 genuinely name a human act, and it produced no false positives on the other 50.

4. **Task 6.5 no longer reads complete.** It derives `complete_pending_manual`, as do `0.5` and `2.8`.

5. **19 V4 phrasing fixtures pass** — one per phrasing found in the pipeline log, plus the affirmatives that must clear the flag. Every one of the 16 real phrasings in the log now reads outstanding, correctly, because V4 has never been performed on this project.

6. **The claim gate found more than the finding reported.** Tasks `0.7` **and** `0.10` now surface as underclaims; the finding named only `0.7`. Disagreements went 11 → 13.

7. **The ledger-currency warning fires today**: 4 days behind, newest deploy 2026-08-23 against newest ledger entry 2026-08-19, and the run still passes — a warning, as recommended.

8. **`scripts/ci/verify-pm-gates.sh`: all PM gates pass and every known-bad fixture is rejected.** The digest regenerated to 239 entries and is current.

### One thing broke on the way, and it was not the new logic

**Editing the evidence map turned two passing fixture assertions red, including the one that proves a corrected ledger entry is excluded.** The cause was a pre-existing freshness guard comparing *any* `--state` file against everything under `contract/` — so the first edit to a contract file made all 52 of them "newer than" the committed fixtures, and the gate refused to run. It looked exactly like this review having broken the suite.

**Scoped to the generated cache it was written for, and proved still armed.** It now runs only for the default state path; `touch contract/evidence-map.json` still makes the real gate refuse and exit 2. Logged as its own finding rather than fixed quietly, because a freshness guard aimed at the wrong artefact will be written again otherwise.

### Findings: what closed, what did not

**Four closed, two deferred, and the two deferred are the ones that matter most.**

`IMP-0229`, `IMP-0231`, `IMP-0232`, `IMP-0233` are closed, each with the re-observation recorded in the entry. `IMP-0242` (the guard above) is closed on a re-observation in both directions.

**`IMP-0228` and `IMP-0230` are deferred to you, not closed.** Everything a repository can carry has landed; the defect in `IMP-0228` is live state and no file changed it. The trustee account is still recorded as a direct member of the restricted profile, removing it is a write this session cannot perform, and **the team-membership route still has not been queried by anyone**. `IMP-0230` waits on the access test actually happening, which waits on that removal.

They are marked deferred with a reason rather than parked at a gate, deliberately: labelling them "awaiting approval" would tell the next agent to send a keyword that has already been sent.

### Two decisions left with you, exactly as flagged

**Tasks `0.7` and `0.10` now report as underclaimed, and I did not touch the claims.** The honest resolution may be that the two Status values are simply out of date, in which case the disagreements disappear when they are corrected — a pm-agent task. A claim is the client-facing baseline and editing one is not mine to do inside a rules review.

**Whether a non-hours reader may read the ledger raw.** I implemented this review's own recommendation — exempt by name, with the reason written inside the gate, where the next reader will see it. Two files are exempt on that basis. Flipping it to "everything goes through the module" is a one-list change if you prefer the stricter rule.

### Scope: what I did NOT apply, and why

**Seven findings arrived from the parallel Phase 0 schema build while this was being applied, two of them blockers, and none of them is in this review.** `IMP-0234` through `IMP-0240` are a coherent cluster of their own — helpers and tests that assumed a single field-security profile, surfaced by a second profile being added — and four are already marked fixed in that session. They were not in front of you when the keyword was given, so applying them under it would be the silent scope creep this system's own rules forbid. **They are a live trigger: two unread blockers.**

**One finding this review raised is also deliberately unapplied.** The lesson behind cluster D — that a fix which centralises a rule while hand-writing its call-site list is still an instance fix — proposes editing the promotion ladder and the regression check themselves. That is a different altitude and belongs in front of you as its own decision, not folded in under this keyword.

**Not verified, and unchanged from section 7:** I did not read the live environment. No provisioning credentials in this session, so the new pre-flight script has never been executed against DEV — it parses clean and its settings file resolves, and that is all. **Nothing here is a current statement of who can see those columns.**
