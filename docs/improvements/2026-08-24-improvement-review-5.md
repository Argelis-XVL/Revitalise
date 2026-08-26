# Improvement Review 25 — 2026-08-24

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 `NEW` (`unread`) → 2 clusters
**Trigger:** blocker escalation — one unread blocker, [IMP-0276](../../logs/improvement-log.jsonl#L273), routed immediately per [WORKFLOW.md → Processing triggers](../../agents/WORKFLOW.md#L207)
**Status:** ~~AWAITING `APPROVE IMPROVEMENTS`. Nothing in this document is on disk.~~ **APPLIED 2026-08-24** on the reviewer's `APPROVE IMPROVEMENTS`. Everything below §10 is the applied record; §§1–9 are the draft as approved and are deliberately left unedited. Change 6 landed **narrower** than drafted and one finding arrived between the keyword and the application — both are in §10.
**Scope note:** the fifth review dated 2026-08-24, after [21](./2026-08-24-improvement-review.md), [22](./2026-08-24-improvement-review-2.md), [23](./2026-08-24-improvement-review-3.md) and [24](./2026-08-24-improvement-review-4.md).
**WBS:** the defect behind cluster A serves [task 0.4](../../contract/wbs.json); cluster B is system work, not billable ([C-COM-002](../../constraints/commercial/commercial-constraints.md))

---

## Summary

**The platform contract is now confirmed, and it is narrower and harder than either of the two reviews that guessed at it: a Dataverse metadata write is `PUT` with the complete object, and `PATCH` is never valid — not on `Attributes`, not on `EntityDefinitions`, not anywhere.** I fetched both Microsoft pages myself rather than inherit the diagnosis, and the wording is categorical: *"You can't use the `PATCH` method to update data model entities… You can't update individual properties."*

That earns the constraint row [review 24 deliberately withheld](./2026-08-24-improvement-review-4.md#L277) — but for the **verb** rule, which was observed live twice, not the **cast** rule, which was wrong. I have written and measured the gate rather than proposing it unbuilt: it flags both real historical defects against the committed tree and passes the corrected one.

**Two things happened during this review that you should know about.** The `development-agent` fix landed mid-session, so the tree moved under me exactly as [IMP-0275](../../logs/improvement-log.jsonl#L272) describes; and review 24's own headline gate turns out to be wired into nothing, so it has never run.

**What needs you:** one new constraint, three gate/script changes, one knowledge edit, one agent-file edit, and one correction to a finding whose recorded reason is now false.

---

## 1. Regression check — did review 24's changes work?

[Review 24](./2026-08-24-improvement-review-4.md) was applied yesterday evening. Its seven applied changes are audited below.

| Prior change | Class it targeted | Recurred? | Verdict |
|---|---|---|---|
| Rung 5 in [verify-constraint-verifiers.py](../../scripts/verify-constraint-verifiers.py) | a HARD rule verified only by a `manual` step | no | **Correct, and unreachable.** It exits 1 on [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) as designed — but the gate is in no build config, so nothing runs it. See below |
| [how-to-verify-a-platform-contract.md §9](../../skills/how-to-verify-a-platform-contract.md#L244) — one live run does not close two defects | inferring a sibling fix succeeded | no | **Worked.** [IMP-0276](../../logs/improvement-log.jsonl#L273) re-queried the auditing defect separately instead of assuming the schema fix covered it — which is how it was found |
| Scope selector in [verify-derived-counts.py](../../scripts/verify-derived-counts.py) + registry | a file-wide count answering a scoped claim | no | Worked |
| [derived-counts](../../config/revitalise-grant-automation-build.yml#L275) wired SOFT into the build | a gate reachable only by hand | no | Worked — and it is the precedent for change 3 below |
| [lead-agent.md](../../agents/lead-agent.md#L137) greps replaced by the gate | a permanently over-tripped trigger | no | Worked |
| [testing-tools.md L244](../../knowledge/technology/testing-tools.md#L244) — the write-side PUT rule | guessing a metadata write contract | **YES — same day** | **Right rule, too narrow.** It is scoped to *column* metadata; the next live failure was *table* metadata. See cluster A |
| Withholding `C-TECH-072` and its cast gate | enforcing a disproved premise | no | **The most valuable thing review 24 did.** Had it shipped, it would be red against the correct code now on disk |

**Two rows matter.**

**Review 24's own headline gate has never run.** `verify-constraint-verifiers.py` appears in no build config and no CI workflow — I grepped `config/`, `.github/` and `constraints/`, and the only hit is [C-TECH-064's own prose](../../constraints/technology/technology-constraints.md#L134) mentioning it. Review 24 [said so itself](./2026-08-24-improvement-review-4.md#L273) and called the fix out of scope; it is instance 31 of `gate-cannot-fail`, and change 3 closes it.

**The knowledge edit recurred within hours, and the shape of the recurrence is the lesson.** Review 24 wrote the PUT rule for *columns* because a column write was what had failed. Table metadata failed next, with a different error code (`0x80060888` rather than a verb rejection), and the same rule would have covered it had it been written at the endpoint-family altitude instead of the instance. That is the altitude rule biting a knowledge file rather than a gate.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: platform-contract-guessed-not-groundtruthed  (x1 BLOCKER: IMP-0276,
           closing out IMP-0272 + IMP-0273)
Altitude:  CONSTRAINT, and this time the premise is confirmed rather than argued.
           how-to-promote-a-finding.md §4 permits skipping ahead when the severity is
           blocker and the mechanism is a platform law. It is instance 36 of the
           project's largest class. Crucially it is also the SECOND live instance of
           the same endpoint-family rule (Attributes on 08-24 20:10, EntityDefinitions
           on 08-24 22:03), which under §2 forbids a third instance-level patch --
           and a knowledge line scoped to columns was exactly that patch.
Ladder row: "a platform law" + "prefer the most mechanical home available"
Becomes:   C-TECH-073 (HARD) + scripts/verify-metadata-write-verbs.py, wired HARD into
           the build, + generalising review 24's knowledge section from columns to all
           metadata endpoints.
Retires:   nothing. C-TECH-072 was never written to disk, so there is nothing to retire;
           see section 4 for why I skip that NUMBER rather than reuse it.
Cites:     IMP-0276, IMP-0272, IMP-0273
Residual:  The gate reads the VERB and the ENDPOINT. It cannot see whether a PUT body is
           the COMPLETE object, which is the other half of the platform rule and is not
           statically decidable here -- the body is assembled by mutating a fetched
           object across several statements. A URI built from a lookup table or spliced
           across variables is also invisible to it.
```

```
CLUSTER B: declared-policy-not-mechanically-enforced  (x1: IMP-0275)
Altitude:  SCRIPT, not prose. Instance 7 of the class. The finding was caught by a
           habit, not by a rule -- and a habit that catches a two-hour window will not
           catch a two-day one. Prose has already been tried on this class and this is
           precisely the case §2 says may not receive another prose statement.
Ladder row: "the system's own memory failed" + "a tool could catch it mechanically"
Becomes:   a `corrects` rung in verify-improvement-log.py + an activation-step-8
           amendment in agents/improvement-agent.md.
Cites:     IMP-0275, IMP-0273, IMP-0154
Residual:  The rung catches a finding that names `corrects` explicitly. A later entry
           that quietly contradicts an earlier one WITHOUT setting the field is still
           invisible, and no gate can read a contradiction out of prose.
```

**A working model already exists for cluster B's rung.** [verify-worklog.py L145](../../scripts/verify-worklog.py#L145) already implements exactly this check — a correction naming a superseded row — for the worklog ledger. The improvement log has the same field, used by [IMP-0273](../../logs/improvement-log.jsonl#L270), and [no script reads it](../../scripts/verify-improvement-log.py). This is a port, not a design.

---

## 3. Proposed changes

| # | Type | Target | What it does | Can it fail? |
|---|---|---|---|---|
| 1 | **constraint** | `C-TECH-073` (HARD), new | **A Dataverse Web API metadata write is `PUT` with the complete current object. `PATCH` is never valid against `EntityDefinitions`, `Attributes`, `GlobalOptionSetDefinitions`, `RelationshipDefinitions` or `EntityKeyDefinitions` — and the derived-type cast belongs on the preparatory `GET` only, never on the write URI.** `Verify By` is change 2 | Change 2 is its `Verify By` |
| 2 | **script + build gate** | `scripts/verify-metadata-write-verbs.py` (new), wired HARD beside [provisioning-step-convergence](../../config/revitalise-grant-automation-build.yml#L523) | Fails any `PATCH` under `provisioning/` whose URI resolves to a metadata entity set; warns on a metadata `PUT` with no `MSCRM.MergeLabels` header | **YES, measured** — see section 6 |
| 3 | **build gate** | [build.yml](../../config/revitalise-grant-automation-build.yml#L275) + a `--warn-only` flag on [verify-constraint-verifiers.py](../../scripts/verify-constraint-verifiers.py) | Wires review 24's gate in as **SOFT**, the same mechanism [derived-counts](../../config/revitalise-grant-automation-build.yml#L275) uses. It exits 1 on C-TECH-064 today, so HARD would block every build — that is a delivery decision, not a rules one | YES — it exits 1 on the real tree now |
| 4 | **script** | [verify-improvement-log.py](../../scripts/verify-improvement-log.py) — new rung | For any finding a review document processed, report when a later entry carries `corrects` naming it. Ports [verify-worklog.py L145](../../scripts/verify-worklog.py#L145) | YES — IMP-0272/IMP-0273 are a live fixture |
| 5 | **agent** | [improvement-agent.md L127](../../agents/improvement-agent.md#L127) — activation step 8 | Before applying an approved review, re-run the log gate and check whether anything appended since the draft corrects a finding the review acted on. Withhold, and say so | Partly — prose, but change 4 is the mechanical half |
| 6 | **knowledge** | [testing-tools.md L244](../../knowledge/technology/testing-tools.md#L244) | Generalises review 24's column-scoped section to every metadata endpoint, and adds the `MSCRM.MergeLabels` destructive default — **a fact no finding has recorded** | Facts are documentation; change 2 is the enforcement |
| 7 | **constraint amendment** | [C-TECH-042 L84](../../constraints/technology/technology-constraints.md#L84) | Extends the present-but-wrong clause: a run in which every resource reported `EXISTS` is evidence about convergence **only**, never that the write path works | Prose inside an existing HARD row |

**One new constraint against a cap of three.** Cluster B needs none — it is a missing check and a stale instruction, not a missing rule.

**Change 7 is an amendment, not a row.** [C-TECH-042](../../constraints/technology/technology-constraints.md#L84) already says the state that matters is present-but-wrong. [IMP-0276](../../logs/improvement-log.jsonl#L273) is that sentence from the evidence side: six tables reported `EXISTS`, the idempotency guard skipped the write for all six, and **not one of those six successes ever executed the write path**. The rule was right; what was missing is that a green run is not evidence for it.

---

## 4. Retirements, and one number I am deliberately not reusing

**No constraint row retires, and I checked rather than assuming.** The nearest candidate was [C-TECH-071](../../constraints/technology/technology-constraints.md#L142) (a declared property must reach the creation path), which overlaps `C-TECH-073` in subject but not in mechanism — 071 is source-vs-code-path, 073 is call-shape-vs-platform. Retiring either would lose real coverage.

**Two reviews running have now found nothing to retire, and that is worth watching rather than repeating.** If review 26 also finds none, the honest conclusion is that this rule set has no retirement pressure and the obligation is producing a paragraph rather than a decision.

**`C-TECH-072` is skipped, not reused.** Review 24 [reserved that number](./2026-08-24-improvement-review-4.md#L225) for the cast rule and withheld it when [IMP-0273](../../logs/improvement-log.jsonl#L270) disproved it. The number never reached a constraint file, so there is nothing to retire — but binding it now to a *different* rule would mean anyone grepping `C-TECH-072` finds review 24 describing the cast rule and the constraint file describing the verb rule. I take the free number instead.

**Derived, not typed:** 78 live constraint rows and 10 retired, via `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l`.

---

## 5. What you need to decide

**Nothing is blocked on you, and two things need naming.**

**The live gap is closed by hand, and the script that should have closed it has still never run.** You enabled auditing on the four finance tables in the admin portal, so [IMP-0271](../../logs/improvement-log.jsonl#L268)'s live defect is gone. The corrected [ensure-auditing.ps1](../../provisioning/dataverse/ensure-auditing.ps1#L202) has not been executed by anyone — and because auditing is now already `true` on all ten tables, **a re-run will report `EXISTS` throughout and prove nothing**, which is change 7's whole point. The next real exercise of that write path is TST/ACC, PRD, or the next new table.

**IMP-0271's recorded reason is now false and I propose correcting it.** Its [`revisit_when`](../../logs/improvement-log.jsonl#L268) calls `ensure-auditing.ps1` *"proven working, no code change needed"*. It was not working, it needed a code change, and that sentence is the kind of claim [C-COM-005](../../constraints/commercial/commercial-constraints.md) exists to distrust. I would rewrite the reason to state what is actually true and leave the entry open.

**Do you still want the C-TECH-064 live verifier built?** Review 24 [handed it over](./2026-08-24-improvement-review-4.md#L267) and it was not written. Change 3 makes its absence visible on every build instead of only when somebody runs a gate by hand. That is the honest half-measure; the verifier itself is still delivery work and still unwritten.

---

## 6. Verification executed for this review

**Level reached: V1, measured — and unlike review 24, the gate exists and has been run.** Nothing here has been written into the repository.

| Check | Result |
|---|---|
| Both Microsoft Learn pages fetched directly | **Confirmed** — `PUT` only, full object, *"You can't update individual properties"*; write URI **uncast**, cast on the `GET` only |
| `verify-metadata-write-verbs.py --selftest` (drafted) | **11 / 11 OK** |
| Same, against the **pre-fix committed tree** (`HEAD`) | **exit 1** — names both real defects: [ensure-auditing.ps1:170](../../provisioning/dataverse/ensure-auditing.ps1) and `ensure-schema.ps1:632` |
| Same, against the **current working tree** | **exit 0**, 33 provisioning scripts |
| [verify-constraint-verifiers.py](../../scripts/verify-constraint-verifiers.py) against the real tree | **exit 1** — C-TECH-064 only |
| Its wiring, grepped across `config/`, `.github/`, `constraints/` | **wired into nothing** |
| [verify-provisioning-step-convergence.py](../../scripts/verify-provisioning-step-convergence.py) | **exit 0** — IMP-0274's PUT fix holds |
| `verify-improvement-log.py --check` | 273 entries, **2 unread**, 24 reviewer-deferred |
| `corrects` grepped across `scripts/` | read by [verify-worklog.py](../../scripts/verify-worklog.py#L145), **not** by the improvement-log gate |
| Live/retired constraint counts | **78 / 10**, derived |

**A defect I found in my own gate, stated because it is the class this review is about.** The first draft passed the real tree — not because the tree was clean, but because its regex stopped at PowerShell's backtick line-continuation, so `-Path` on a second line was invisible. It would have shipped green over the very defect it exists to catch. It was found by testing against the pre-fix tree rather than trusting the selftest, and the fix is the `logical_lines` function.

**Not verified, and it is the honest limit.** No live Dataverse call was made by anything in this review. The corrected `PUT` in both scripts is **V1/V2 only** — it matches the documented shape and has never been executed against an environment, so [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) forbids reporting it as fixed.

---

## 7. Findings left unprocessed, and the tree that moved under me

**States excluded, stated so the cap is not silent:** 24 `reviewer-deferred` (each carrying a reason a human accepted), 0 `awaiting-approval`, 0 `already-fixed`, and every `APPLIED`/`REJECTED` entry. Both `unread` entries were read in full and both are dispositioned above.

**I read four deferred entries anyway, and change 4 is the reason.** [IMP-0271](../../logs/improvement-log.jsonl#L268), [IMP-0272](../../logs/improvement-log.jsonl#L269), [IMP-0273](../../logs/improvement-log.jsonl#L270) and [IMP-0274](../../logs/improvement-log.jsonl#L271) are all `reviewer-deferred`, the state [activation step 2](../../agents/improvement-agent.md#L102) says to leave alone. IMP-0273 carries `corrects` against IMP-0272 and is load-bearing for this review's central rule, which is exactly IMP-0275's point: the four-state model is right for scope and wrong for corrections.

**The tree moved under me during this review, which is IMP-0275 happening again in the same day.** When I started, [ensure-auditing.ps1](../../provisioning/dataverse/ensure-auditing.ps1#L202) still carried the broken `PATCH`; the `development-agent` fix landed mid-session and I re-read it before finalising. Its shape is correct against the documentation I fetched: uncast `PUT`, no `$select` on the `GET`, OData annotations stripped, `MSCRM.MergeLabels: true` present. Had I drafted the gate against the tree I first read and applied it without re-reading, change 2 would have been red against correct code — the exact failure review 24 escaped by luck.

**One finding closes, one does not.** [IMP-0275](../../logs/improvement-log.jsonl#L272) declares `observable_at: n/a` and is closed by changes 4 and 5. [IMP-0276](../../logs/improvement-log.jsonl#L273) is `observable_at: V3` and **stays open** with a corrected `revisit_when` — the fix is on disk and unexecuted, and the manual admin-portal workaround means a DEV re-run can no longer exercise it.

---

## 8. Digest impact

**Zero, and this time that is a prediction with a reason rather than a refusal to predict.** Review 24 [measured the delta at zero](./2026-08-24-improvement-review-4.md#L242) and established why: the generator already renders `NEW` entries, so moving a finding to `APPLIED` changes its status, not its lesson or its class. This review closes one entry and corrects the prose of two others, so the only possible change is the corrected `deferred_reason` text.

I regenerate and report the measured before-and-after on approval.

---

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-24-improvement-review-5.md

Findings processed: 2 unread  →  2 clusters
Regression check:   7 prior changes audited, 2 classes recurred
Proposed:           1 constraint (cap 3), 3 gates/scripts, 1 knowledge edit,
                    1 agent-file edit, 1 constraint amendment, 0 retirements
                    (+ 1 finding's recorded reason corrected)
Altitude calls:     1 skipped ahead to a constraint (blocker + platform law, confirmed
                    live twice), 1 generalised from prose to a script rung
Digest:             will regenerate — predicted delta zero, will report measured

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 10. Applied — 2026-08-24

**All seven changes are on disk, and the first thing the new activation step did was fire on its own author.** Between this document reaching its gate and the keyword arriving, four findings were appended — [IMP-0277](../../logs/improvement-log.jsonl#L274) among them, carrying `corrects` against [IMP-0276](../../logs/improvement-log.jsonl#L273), the blocker this whole review is built on. That is change 5's scenario exactly, on its first outing, before change 5 existed to catch it. It was read in full before anything was applied.

**It confirms rather than disproves, so cluster A stands.** [IMP-0277](../../logs/improvement-log.jsonl#L274) is the `development-agent` fix responding to IMP-0276, re-verified against the same Microsoft worked example rather than assumed to carry over: full-object `PUT` to the **uncast** `EntityDefinitions` URI, no cast segment anywhere (`EntityMetadata` is not polymorphic the way `Attributes` is), `MSCRM.MergeLabels: true`. Had it disproved the premise, [C-TECH-073](../../constraints/technology/technology-constraints.md#L143) and its gate would have been withheld under the rule this review was writing.

### What landed

| # | Type | Where it is now | Verified |
|---|---|---|---|
| 1 | constraint | [C-TECH-073](../../constraints/technology/technology-constraints.md#L143), HARD | its `Verify By` is change 2, which is wired and green |
| 2 | script + HARD build gate | [scripts/verify-metadata-write-verbs.py](../../scripts/verify-metadata-write-verbs.py), step [`metadata-write-verbs`](../../config/revitalise-grant-automation-build.yml#L555) | **13/13 selftest; exits 1 over the real pre-fix tree naming both historical defects; exits 0 over the corrected tree** |
| 3 | SOFT build gate | step [`constraint-verifiers`](../../config/revitalise-grant-automation-build.yml#L578) + [`--warn-only`](../../scripts/verify-constraint-verifiers.py#L55) | 16/16 selftest; prints the real C-TECH-064 finding and exits 0 |
| 4 | script rung | [check_corrections()](../../scripts/verify-improvement-log.py#L1295) | 52/52 selftest; **fires live on both real pairs in this log** |
| 5 | agent file | [activation step 8](../../agents/improvement-agent.md#L127) | prose; change 4 is its mechanical half |
| 6 | knowledge | [testing-tools.md §Writing ANY metadata](../../knowledge/technology/testing-tools.md#L244) | narrower than drafted — see below |
| 7 | constraint amendment | [C-TECH-042](../../constraints/technology/technology-constraints.md#L84) | prose inside an existing HARD row |

**Change 2 is proven able to fail against real code, not only fixtures.** Reconstructing `HEAD`'s `provisioning/` into a scratch tree and running the gate over it exits 1 naming `ensure-auditing.ps1:170` and `ensure-schema.ps1:632` — both genuine defects, at the lines §6 predicted — while the corrected working tree passes with 66 Dataverse calls across 33 scripts inspected.

**Change 6 landed narrower than drafted, because the tree moved again.** [IMP-0277](../../logs/improvement-log.jsonl#L274) had already generalised this section from `Attributes` to `EntityDefinitions` and recorded that the old PATCH precedent never exercised the write path. What was still missing, and is what actually got written: the heading and framing generalised from *column* metadata to the whole **endpoint family**; the data-record-versus-metadata trap stated plainly (the same script PATCHes `organizations` correctly two dozen lines above where it must never PATCH `EntityDefinitions`); and [the `MSCRM.MergeLabels` destructive default](../../knowledge/technology/testing-tools.md#L278) — omitting it makes Dataverse *replace* rather than merge the localised label collections, so a full-object `PUT` built from a one-language `GET` silently deletes every other language's labels on a call whose intent was to flip one boolean. No finding records that; it comes from the platform documentation.

**One change nobody asked for, and the reason it was necessary.** [scripts/verify-build-config.py](../../scripts/verify-build-config.py#L109) gained `.*-verbs$` and `.*-verifiers$` gate-name patterns. Without them the preflight reads both new steps as ordinary steps and never requires them to prove they can fail — wiring a gate in while leaving it unrecognised *as* a gate is `gate-cannot-fail` one level up, which is precisely what this review was convened to stop. The preflight now reports **46 steps, 35 gates**, both new ones included.

### Findings

**Three logged, as flagged at the gate — and the digest delta is therefore NOT zero.** §8 predicted zero and gave a good reason; the reason was right and the prediction was wrong, because it did not count this review's own findings. Measured: 277 → 280 entries, 277 → 280 distinct lessons, `gate-cannot-fail` **x30 → x32**, `gate-reassures-wrongly` **x12 → x13**. Line count is unchanged at 477 — both classes were already over the 20-lesson display cap, so the new lessons land in the not-shown lists rather than adding rows.

| Finding | What it records | State |
|---|---|---|
| [IMP-0281](../../logs/improvement-log.jsonl#L278) | review 24's headline gate was wired into nothing and had never run — instance 31 of `gate-cannot-fail` | APPLIED by change 3 |
| [IMP-0282](../../logs/improvement-log.jsonl#L279) | this review's own gate would have shipped green over both defects it exists to catch: its regex stopped at PowerShell's backtick continuation, and its selftest was 11/11 at that moment | APPLIED — fixed before shipping |
| [IMP-0283](../../logs/improvement-log.jsonl#L280) | [IMP-0271](../../logs/improvement-log.jsonl#L268)'s recorded reason claimed `ensure-auditing.ps1` was "proven working, no code change needed" — it was not, it needed one, and the reviewer's run produced four FAILED lines | APPLIED by change 7 + the correction |

**[IMP-0282](../../logs/improvement-log.jsonl#L279) is the one worth reading.** A gate's selftest proves it against fixtures its own author wrote — the same person's model of the defect, twice. This one was caught only by rebuilding the pre-fix tree from `HEAD` and running the draft over it. For a gate reading source in another language, the parser *is* the gate.

### Entries closed, corrected, and left open

**[IMP-0275](../../logs/improvement-log.jsonl#L272) → APPLIED**, `observable_at: n/a`, so no live re-observation applies. Its `reobserved` field records the mechanical proof instead: the new rung fires on both real pairs in this log, including IMP-0276/IMP-0277 — the case that had to be caught by hand at the start of this session.

**[IMP-0276](../../logs/improvement-log.jsonl#L273) stays OPEN**, and the corrected code being on disk is not a reason to close it. It is `observable_at: V3`; [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) admits only a live re-run, and no agent session here holds Dataverse credentials. Its `revisit_when` now names the trap this review is about: auditing is already true on all ten tables after the reviewer's manual workaround, so a DEV re-run reports `EXISTS` throughout and **proves nothing** — a genuine V3 observation needs TST/ACC, PRD, or the next new table.

**[IMP-0271](../../logs/improvement-log.jsonl#L268)'s reason is rewritten and the entry stays open.** It now records what is true: the live DEV gap is closed, by hand in the admin portal, not by the script; the script was broken, needed a code change, and got one; and that fix is unexecuted.

**[IMP-0272](../../logs/improvement-log.jsonl#L269), [IMP-0273](../../logs/improvement-log.jsonl#L270), [IMP-0274](../../logs/improvement-log.jsonl#L271) and [IMP-0277](../../logs/improvement-log.jsonl#L274) were restamped** to name this review, which clears every citation-stamp and correction warning the log gate had standing.

**Three findings arrived after the draft and are NOT processed here**, stated so the cap is not silent: [IMP-0278](../../logs/improvement-log.jsonl#L275) (change-order sizing with no precedent), [IMP-0279](../../logs/improvement-log.jsonl#L276) (an FR's category-level field list never diffed against the implementation) and [IMP-0280](../../logs/improvement-log.jsonl#L277) (the open-questions escalation trigger counting a document's whole backlog). None shares a class with either cluster; all three are `unread` and are the next review's scope.

### Verification executed at application

**Level reached: V1.** Nothing in this review has been executed against a live environment, and the corrected `PUT` in both provisioning scripts remains V1/V2 — matching the documented shape, never run.

| Check | Result |
|---|---|
| `verify-metadata-write-verbs.py --selftest` | **13/13**, exit 0 |
| Same, over `HEAD`'s `provisioning/` (pre-fix) | **exit 1** — `ensure-auditing.ps1:170`, `ensure-schema.ps1:632` |
| Same, over the working tree | **exit 0** — 66 calls, 33 scripts |
| `verify-constraint-verifiers.py --selftest` | **16/16**, exit 0 |
| `--warn-only` against the real tree | prints the C-TECH-064 finding, **exit 0** |
| `verify-improvement-log.py --selftest` | **52/52**, exit 0 |
| `verify-improvement-log.py --check` | **exit 0**, 280 entries, 0 warnings |
| `generate-known-failure-modes.py --check` | **exit 0**, current at 280 |
| `verify-build-config.py` on the real config | **exit 0** — 46 steps, 35 gates |
| `verify-derived-counts.py` | exit 0 — 7 registered claims all match |
| `verify-pipeline-config.py`, `verify-workflow-syntax.py` | exit 0 |
| `Invoke-Tests.ps1 -Path build` | **117 passed, 0 failed** |
| Live constraint rows / retired | **79 / 10**, derived |

**Not verified, and it is the honest limit.** No live Dataverse call was made. [C-TECH-073](../../constraints/technology/technology-constraints.md#L143) is enforced statically and says nothing about whether a `PUT` body is the complete object — that half is not statically decidable and is named as the residual in both the row and the gate. `verify-build-config.py` has no `--selftest` of its own by design; it is exempt in `GATE_EXEMPT` and covered by `src/tests/build/VerifyBuildConfig.Tests.ps1`, which is green.

**One pre-existing note left standing:** [IMP-0274](../../logs/improvement-log.jsonl#L271) carries a `deferred_reason` and no `revisit_when`, which the log gate reports as a NOTE. Changing it was not in this review's approved scope.
