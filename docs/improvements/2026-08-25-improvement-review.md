# Improvement Review 27 — 2026-08-25

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 10 `NEW` (`unread`) → 7 clusters
**Trigger:** blocker escalation — two unread blockers, [IMP-0287](../../logs/improvement-log.jsonl#L284) and [IMP-0290](../../logs/improvement-log.jsonl#L287), routed immediately per [WORKFLOW.md → Processing triggers](../../agents/WORKFLOW.md#L207)
**Status:** **APPLIED IN FULL 2026-08-25.** All 12 changes are on disk; all 10 findings are
dispositioned. See §10 for what was measured at application and where it differs from the
predictions in §7 and §8. Applied across two dispatches — the first hit the account's spend limit
after change 6, which is itself now logged as [IMP-0301](../../logs/improvement-log.jsonl#L298).
**Scope:** the 10 `unread` entries **not** already clustered by [review 26](./2026-08-24-improvement-review-6.md) — [IMP-0286](../../logs/improvement-log.jsonl#L283) to [IMP-0295](../../logs/improvement-log.jsonl#L292). Review 26 is still parked at its own gate and is not re-derived here.
**WBS:** [0.4](../../contract/wbs.json) (three findings) and [6.1, 6.3, 6.5, 6.9](../../contract/wbs.json) (five findings); everything proposed here is system work, not billable ([C-COM-002](../../constraints/commercial/commercial-constraints.md#L35))

---

## Summary

**One of the two blockers is not a blocker, and its stated cause is disproved by the record of the dispatch that logged it.** [IMP-0290](../../logs/improvement-log.jsonl#L287) says architect-agent was dispatched at default Sonnet tier without the required escalation. [routing.log L211](../../logs/routing.log#L211) records the opposite in the dispatcher's own words — *"Escalated to strategic tier (opus) — feature touches special-category data"*. The agent inferred its tier from [models.yml's default](../../config/models.yml#L89) instead of observing it, so the proposed gate would enforce a rule that was already followed.

**The other blocker is real and its fix is additive.** [IMP-0287](../../logs/improvement-log.jsonl#L284) reconciles two findings nobody had ever compared: the cert-based live-read control documented at [build-and-deploy.md L344](../../knowledge/technology/build-and-deploy.md#L344) is Auto-Mode-dependent, and that file never mentions Auto Mode.

**Two findings that arrived as prose became one measured gate, and it found more than the finding reported.** [IMP-0286](../../logs/improvement-log.jsonl#L283) reported one register row missing its source marker. The mechanical form finds **two** — [A-FIN-07](../../docs/development/revitalise-grant-automation-dev-summary.md#L6021) and [A-FIN-05](../../docs/development/revitalise-grant-automation-dev-summary.md#L5785).

**Four retired constraints have had their reinstatement condition met for four days and nobody noticed.** [IMP-0294](../../logs/improvement-log.jsonl#L291) is the highest-value finding in this batch and its severity says `friction`.

**What needs you:** one new constraint against a cap of three, two measured build gates, seven prose edits, one rejection, and two entries I am **not** closing.

---

## 1. Regression check

[Review 26](./2026-08-24-improvement-review-6.md) audited review 25's seven changes fifteen hours ago and nothing from review 26 is on disk — [technology-constraints.md](../../constraints/technology/technology-constraints.md) is unchanged at 22:50, before review 26's 23:18 draft. I do not re-derive that audit. What follows is the delta since it was written.

| Prior change | Class it targeted | Recurred? | Verdict |
|---|---|---|---|
| [C-TECH-073](../../constraints/technology/technology-constraints.md#L143) + [verify-metadata-write-verbs.py](../../scripts/verify-metadata-write-verbs.py), wired at [build step L555](../../config/revitalise-grant-automation-build.yml#L555) | a metadata write guessed, not ground-truthed | no | **Worked, and it is on disk and wired** |
| [check_corrections()](../../scripts/verify-improvement-log.py#L1295) | a correction landing after a review's draft | **YES — again** | **Same scope hole, one day later.** See below |
| Review 26's disposition of [IMP-0278](../../logs/improvement-log.jsonl#L275) — *no change, the gap closed itself* | change-order sizing with no precedent | **YES** | **Contradicted by [IMP-0288](../../logs/improvement-log.jsonl#L285)**, logged after review 26 was drafted |

**Review 26's own new rung is blind to the entry that contradicts review 26.** Its change 3 extends [check_corrections()](../../scripts/verify-improvement-log.py#L1295) to catch an entry whose `corrects` field names a still-`unread` target. [IMP-0288](../../logs/improvement-log.jsonl#L285) carries no `corrects` field, so the rung stays silent — the same optional-field hole that made [IMP-0169](../../logs/improvement-log.jsonl#L166)'s earlier fix invisible. This is instance 33 of `gate-cannot-fail` and I am **not** proposing a third patch to that rung; §5 puts it to you.

**The substantive point for you:** review 26 concluded that [IMP-0278](../../logs/improvement-log.jsonl#L275) needed nothing because [CO-001.md](../../contract/change-orders/CO-001.md) now exists as a pattern. [IMP-0288](../../logs/improvement-log.jsonl#L285) records that CO-001's own ROM was wrong and needed CO-001-A1 to resize it. The class is now `x2`, which under the altitude rule forbids leaving it as a note. Change 9 below is the change review 26 declined, and **approving review 26 unchanged would close a finding whose class recurred before the keyword was sent.**

**A third stall, not counted anywhere.** [routing.log](../../logs/routing.log) at 23:25 records two dispatches — development-agent to add the A-FIN-07 marker, and improvement-agent resumed to fold [IMP-0286](../../logs/improvement-log.jsonl#L283)/[IMP-0287](../../logs/improvement-log.jsonl#L284) into review 26. **Neither left any trace.** The marker is absent from [ensure-auditing.ps1](../../provisioning/dataverse/ensure-auditing.ps1) and review 26 contains no mention of either id. Together with [IMP-0291](../../logs/improvement-log.jsonl#L288)'s stalled architect dispatch, that is three dispatches in one day recorded as routed and never reconciled, against a class the log scores `x1`.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: declared-policy-not-mechanically-enforced  (x1: IMP-0286; x8 overall)
Altitude:  SCRIPT, and there is no argument left to have. Instance 8 of a class whose
           own constraint names a HUMAN as its verifier: C-TECH-052's Verify By says
           "test-agent cross-checks the register against the hand-authored artefacts".
           A HARD rule enforced by whether a session remembers to grep is the exact
           shape of IMP-0165 and IMP-0174, both blockers, both in this class.
Ladder row: "a tool could catch it mechanically"
Becomes:   scripts/verify-assumption-register.py + a build step, wired HARD, plus an
           amendment to C-TECH-052's Verify By naming it instead of the human.
Retires:   nothing. It NARROWS C-TECH-052's manual clause rather than retiring the row.
Cites:     IMP-0286, IMP-0165, IMP-0174
Residual:  It resolves the "Where" column's markdown link and greps for the row's own
           id anywhere in that file, NOT at the cited line. A marker in the wrong
           function still passes. It also depends on an uncontrolled status vocabulary
           -- CLOSED, VERIFIED, OPEN and "Already CLOSED" all appear today; the
           prototype treats CLOSED and VERIFIED as closed and a new word would be
           read as OPEN, which fails safe but noisily.
```

```
CLUSTER B: harness-blocks-destructive-call  (x1 BLOCKER: IMP-0287; x9 overall)
Altitude:  READ PATH. The capability claim lives in knowledge/technology/build-and-deploy.md
           L344 and in the digest's Capabilities section; NEITHER mentions Auto Mode.
           agents/pipeline-agent.md L221 already carries the correct, honest pattern,
           established 2026-08-24. This is not a new rule -- it is that pattern reaching
           the two files test-agent actually reads.
Ladder row: "the system's own memory failed" -> a read-path change
Becomes:   one qualifier at build-and-deploy.md L344 and one in how-to-verify-a-platform-
           contract.md section 3, plus documenting `refusal_context` in the schema skill.
Retires:   nothing. It CORRECTS a standing capability claim from IMP-0084 -- that reads
           always run freely -- which is true only of a non-Auto-Mode session.
Cites:     IMP-0287, IMP-0084, IMP-0245, IMP-0252
Residual:  An agent cannot always determine its own harness mode. The instruction is to
           STATE the mode and treat unknown as unavailable, which is prose and will stay
           prose. Nothing here changes what the classifier observes -- checked against
           how-to-promote-a-finding.md section 4 before drafting.
```

```
CLUSTER C: dispatched-below-required-tier  (x1 BLOCKER: IMP-0290)
Altitude:  NONE as proposed -- the premise is disproved and the mechanism is impossible.
           (a) routing.log L211 records the opus override in the dispatcher's own words,
           so the manual step the finding says was skipped was performed. (b) The proposal
           is "a script that refuses a Task-tool dispatch"; NOTHING in scripts/ sits
           between an agent and the Task tool, so its Verify By cannot be executed --
           anti-bloat limit 4, and the exact shape that got C-TECH-023 retired.
Ladder row: none. Rejected as proposed.
Becomes:   the real, much smaller gap: the agent inferred its tier from models.yml's
           default and its own generated frontmatter, both of which ALWAYS show the
           default and never the override. One clause in the generator's self-check block.
Retires:   nothing.
Cites:     IMP-0290
Residual:  An agent still cannot see its dispatch parameters. It can read the ROUTED_TO
           line and its own model identity; if neither is conclusive it must ask, not
           assume. Prose.
```

```
CLUSTER D: dispatched-agent-stalls-silently  (x1 logged: IMP-0291; x3 VERIFIED today)
Altitude:  ABOVE the proposed instance patch. IMP-0291 proposes one more case in
           WORKFLOW.md's "When a dispatch dies instead of finishing" (L61) -- a section
           that already exists for the spend-limit case and already names its backstop
           at L86. That backstop cannot see this class: it detects a dispatch that
           LOGGED findings and left them unread, not one that produced nothing at all.
           Three instances in one day forbid a third instance patch.
Ladder row: "second instance -> generalise" + "the ORDER of steps was wrong"
Becomes:   the CONVENTION half now (every ROUTED_TO line is closed by a terminal line),
           and the script half put to you as a decision -- see section 5.
Retires:   nothing.
Cites:     IMP-0291, IMP-0286, IMP-0172
Residual:  THE SCRIPT IS NOT PROPOSED AS MEASURED AND I SAY SO. routing.log carries 99
           ROUTED_TO lines against 9 GATE_RECEIVED; only plan-, commercial- and
           architect-agent use the terminal marker at all, so a reconciliation gate over
           history would emit ~90 false positives. It can only work forward from a
           cutoff, which is the IMP-0181 precedent, and that is a decision, not my call.
```

```
CLUSTER E: requirement-names-data-the-solution-cannot-supply  (x2: IMP-0292, IMP-0293)
Altitude:  KNOWLEDGE LINE, and deliberately NOT a constraint. The two findings are one
           property: a data fact was asserted without resolving it to a (table, column)
           pair against solution source, then against the field security profile for the
           persona named. IMP-0293 proposes a HARD domain row; both are first-instance,
           both `rework` not blocker, and the mechanism is a project convention rather
           than a platform law -- how-to-promote-a-finding.md section 4 says wait.
Ladder row: "one instance, cause is general, a human needs to know it"
Becomes:   one step in how-to-write-requirements.md and one in how-to-intake-external-
           documents.md.
Retires:   nothing.
Cites:     IMP-0292, IMP-0293
Residual:  THE DELIVERY HALF IS NOT MINE AND IS NOT FIXED, and both entries are V4.
           Section 6 says why neither closes. Extracting data-item names from FR prose
           is a natural-language problem; a gate over it would have unknown recall, which
           is why I propose prose and not the script IMP-0293 sketches.
```

```
CLUSTER F: retired-constraint-premise-expired  (x1: IMP-0294)
Altitude:  CONSTRAINT, skipping the wait-for-a-second-instance rule, and here is why:
           this is not a defect prediction, it is an EXPIRED PREMISE. Four rows
           (C-TECH-020 to C-TECH-023, L60-L63) were retired for want of a dependency
           manifest and each names the same reinstatement trigger. That trigger fired on
           2026-08-21 18:45. Reviews 21 through 26 all ran after it. 24 dependencies and
           a committed lockfile are audited by nothing.
Ladder row: "a platform law" + "a tool could catch it mechanically"
Becomes:   ONE new row consolidating four reinstatements -- anti-bloat limit 2 forbids
           four -- plus one build step. Measured.
Retires:   nothing new, and one thing STAYS retired ON PURPOSE: the licence half of
           C-TECH-022. No licence checker is installed, and a Verify By naming an absent
           tool is what got that row retired in the first place.
Cites:     IMP-0294
Residual:  `npm audit` reports what the registry knows today; a clean run is not proof of
           a clean tree tomorrow, and it says nothing about licences or provenance. The
           reinstated row covers the code app only -- no other manifest exists.
```

```
CLUSTER G: platform-fact-groundtruthed + proposed-control-overridden + commercial
           (x3: IMP-0295, IMP-0289, IMP-0288)
Altitude:  KNOWLEDGE LINE for the first two, AGENT FILE for the third.
           IMP-0295 is a capability fact established from the generator's own output --
           E1, not documentation -- and belongs where the next agent will look.
           IMP-0289 is a risk-class confusion the compliance file cannot currently
           express: CR-01 covers hiding a raw column, not what a combination of visible
           aggregates discloses.
           IMP-0288 is instance 2 of the class review 26 left as a note. See section 1.
Ladder row: "a capability was established and could be lost again" / "one instance, cause
           is general" / "second instance -> generalise"
Becomes:   an Aggregation subsection in code-apps.md, a CR-11 row, and one step in
           commercial-agent.md.
Retires:   nothing.
Cites:     IMP-0295, IMP-0289, IMP-0288, IMP-0278
Residual:  CR-11 has no gate and I am not pretending otherwise -- small-cell disclosure is
           a judgement about a query result, not a property of source. It is a checklist
           line, which is what CR-04 and CR-06 already are.
```

---

## 3. Proposed changes

| # | Type | Target | What it does | Can it fail? |
|---|---|---|---|---|
| 1 | **script + build step** | `scripts/verify-assumption-register.py`, wired HARD after [metadata-write-verbs](../../config/revitalise-grant-automation-build.yml#L555) | For every OPEN row of the Dev Summary assumption register, resolve the `Where` link and require the row's own `A-nnn` id to appear in that file | **YES, measured — exit 1 on today's tree**, naming [A-FIN-05](../../docs/development/revitalise-grant-automation-dev-summary.md#L5785) and [A-FIN-07](../../docs/development/revitalise-grant-automation-dev-summary.md#L6021) |
| 2 | **constraint amendment** | [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Its `Verify By` names test-agent's manual grep as the enforcement of the source-marker half. Replace that clause with change 1's step; the rule text is untouched | Prose inside a HARD row; change 1 is the enforcement |
| 3 | **1 new constraint** | [constraints/technology/technology-constraints.md](../../constraints/technology/technology-constraints.md) | One row reinstating the enforceable half of [C-TECH-020](../../constraints/technology/technology-constraints.md#L60)–[023](../../constraints/technology/technology-constraints.md#L63): a code-app manifest ships a committed lockfile, is installed with `npm ci`, and reports no HIGH/CRITICAL advisory. Cites `IMP-0294` | **YES** — it is enforced by change 4 |
| 4 | **build step** | `code-app-audit`, after [code-app-install](../../config/revitalise-grant-automation-build.yml#L752) | `npm audit --audit-level=high`. The lockfile-drift half needs **no new step**: [code-app-install](../../config/revitalise-grant-automation-build.yml#L752) already runs `npm ci`, which fails by design when the lockfile and manifest disagree | **Measured — exit 0, 0 vulnerabilities today.** It is a real check against a real manifest, not a check over nothing |
| 5 | **generator** | the self-check block at [generate-subagents.py L201](../../scripts/generate-subagents.py#L201) | One clause: the `model:` frontmatter and [models.yml](../../config/models.yml#L89) always show your agent's **default** tier, never the override actually applied — confirm against the `ROUTED_TO` line and your own model identity before concluding you were under-dispatched. Requires regenerating `.claude/agents/` | Prose. It is the honest residue of a rejected proposal |
| 6 | **agent files** | [lead-agent.md](../../agents/lead-agent.md) + [WORKFLOW.md L61](../../agents/WORKFLOW.md#L61) | Every `ROUTED_TO` line records the resolved tier when a dispatch is escalated (already de-facto practice, [5 instances](../../logs/routing.log#L211)) and is closed by a terminal line. Adds the stalled-in-an-unreachable-session case | Prose; §5 holds the mechanical half |
| 7 | **knowledge + skill** | [build-and-deploy.md L344](../../knowledge/technology/build-and-deploy.md#L344) + [how-to-verify-a-platform-contract.md §3](../../skills/how-to-verify-a-platform-contract.md#L112) | The cert-based live-read control is Auto-Mode-dependent. State the harness mode before relying on it; treat unknown as unavailable and route to a `REVIEWER ACTION REQUIRED` block with the exact command | Prose. No control observes less — this makes a refusal *expected* rather than surprising |
| 8 | **skill** | [how-to-log-an-improvement.md §2](../../skills/how-to-log-an-improvement.md#L33) | Documents `refusal_context`, which [verify-improvement-log.py L595](../../scripts/verify-improvement-log.py#L595) has **required** on this class since review 24 and which appears nowhere in the file agents load to write a finding | Prose. Same defect review 26's change 4 fixes for `corrects` — see the collision note in §5 |
| 9 | **agent file** | [commercial-agent.md](../../agents/commercial-agent.md) | When a change order's firm figure was deferred to a later SDD, re-price it when that SDD lands instead of waiting for a human to notice. The change review 26 declined, now at instance 2 | Prose |
| 10 | **knowledge** | [code-apps.md](../../knowledge/technology/code-apps.md) | New Aggregation subsection: [IGetAllOptions L10](../../src/code-apps/trustee-review-portal/src/generated/models/CommonModels.ts#L10) has no `apply` member and caps `count` at 5000; [client.ts L73](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts#L73) caps reads at 500; a Code App runs as the signed-in user so column security nulls any secured column a tally needs. Aggregate in a flow as the service identity into a non-personal table | Prose recording an E1 fact |
| 11 | **knowledge** | [compliance-requirements.md](../../knowledge/domain/compliance-requirements.md#L17) | New `CR-11`: small-cell / statistical disclosure on an aggregate view is a **distinct** risk class from [CR-01](../../knowledge/domain/compliance-requirements.md#L17)'s field-level security, and CR-01's evidence may not be reused for it | Prose, marked ⚠️ no gate, as [CR-04](../../knowledge/domain/compliance-requirements.md#L20) and [CR-06](../../knowledge/domain/compliance-requirements.md#L22) already are |
| 12 | **skills** | [how-to-write-requirements.md](../../skills/how-to-write-requirements.md#L59) + [how-to-intake-external-documents.md](../../skills/how-to-intake-external-documents.md#L36) | Before writing a requirement that names data a specific persona will see, resolve each item to a `(table, column)` pair against `Entities/*/Entity.xml`, then against `Other/FieldSecurityProfiles.xml` for that persona. A generated per-table model, a code-app type file and a form are projections, not the schema | Prose; the residual in cluster E is why not a gate |

**One new constraint against a cap of three**, and it consolidates four reinstatements into one row rather than restoring four.

---

## 4. Retirement

**Nothing retires, and this is the fourth review running to say so.** Review 26 verified mechanically fifteen hours ago that every live row's `Verify By` names a script that exists; no constraint file has changed since, so re-deriving it would produce the same answer at strategic-tier cost.

**Derived, not typed:** 79 live rows and 10 retired, via `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l`.

**Two things worth naming instead.** [C-TECH-052](../../constraints/technology/technology-constraints.md#L107)'s manual clause is *narrowed* by change 1, not retired — the row stays, its human verifier is replaced by a script. And the licence-compatibility half of [C-TECH-022](../../constraints/technology/technology-constraints.md#L62) **stays retired deliberately**: no licence checker is installed, and reinstating a row whose `Verify By` names an absent tool is precisely what earned that row its retirement.

**This review runs the obligation backwards.** It found four rows whose retirement premise expired, which is the opposite failure from the one the obligation was written to catch — a rule set that only grows. Review 26 already put the obligation's future to you; I am not duplicating that question, only adding the data point that the audit finally produced something, and it was a reinstatement.

---

## 5. What you need to decide

**Nothing blocks this review. Four things want an answer, and the first one affects a document already at your gate.**

**Review 26 should not be approved unchanged.** Its disposition of [IMP-0278](../../logs/improvement-log.jsonl#L275) — no change needed, the gap closed itself — is contradicted by [IMP-0288](../../logs/improvement-log.jsonl#L285), logged after that draft was written. Change 9 is the change it declined. Either approve review 26 with that one cluster reopened, or approve this review first and let change 9 stand for both.

**Two pending reviews edit the same two skill files.** Review 26's changes 7 and 8 touch [how-to-intake-external-documents.md](../../skills/how-to-intake-external-documents.md#L36) and [how-to-write-requirements.md](../../skills/how-to-write-requirements.md#L59); so does my change 12. They do not conflict in substance, but whichever applies second must re-read both files rather than applying a diff written against the earlier tree — [activation step 8](../../agents/improvement-agent.md#L127) already requires that, and this is a live instance of it.

**Do you want the dispatch-reconciliation script?** Cluster D's convention half is in change 6 and costs nothing. The script — every `ROUTED_TO` line closed by a terminal line, unreconciled dispatches reported — can only work forward from a cutoff date, because [routing.log](../../logs/routing.log) carries 99 `ROUTED_TO` lines against 9 `GATE_RECEIVED` and three agents use the marker at all. That is the [IMP-0181](../../logs/improvement-log.jsonl#L178) precedent applied to a second log, and it is a decision about convention, not a defect fix. Say the word and it is the next review's change.

**Two markers are delivery work and gate the next build.** Change 1 goes red on [A-FIN-05](../../docs/development/revitalise-grant-automation-dev-summary.md#L5785) and [A-FIN-07](../../docs/development/revitalise-grant-automation-dev-summary.md#L6021). Adding two comment lines belongs to development-agent, not to this review; [routing.log](../../logs/routing.log) shows A-FIN-07's fix was already dispatched at 23:25 and never landed.

---

## 6. Closure states — six close, two do not, one is rejected

**Before closing anything I read each entry's `observable_at`.** Two entries are `V4` and neither is closable here.

| Finding | Disposition |
|---|---|
| [IMP-0286](../../logs/improvement-log.jsonl#L283) | `APPLIED` on change 1 for the **systemic** half. The two missing markers are delivery work and are named in §5 |
| [IMP-0287](../../logs/improvement-log.jsonl#L284) | `APPLIED` on changes 7 and 8. `observable_at` is `n/a` |
| [IMP-0288](../../logs/improvement-log.jsonl#L285) | `APPLIED` on change 9 |
| [IMP-0289](../../logs/improvement-log.jsonl#L286) | `APPLIED` on change 11 |
| [IMP-0290](../../logs/improvement-log.jsonl#L287) | **`REJECTED` as proposed**, with a `rejected_reason` recording that [routing.log L211](../../logs/routing.log#L211) disproves the stated cause and that the proposed script cannot be executed. Change 5 is applied against the real gap. **Its `blocker` severity is not supported** — its own `cost` field says *"zero rework"*, and the dispatch it complains about ran on the correct tier |
| [IMP-0291](../../logs/improvement-log.jsonl#L288) | `APPLIED` on change 6, convention half only. The script is a §5 decision, stated so the cap is not silent |
| [IMP-0292](../../logs/improvement-log.jsonl#L289) | **STAYS OPEN.** `V4`. [Amendment A-02's](../../docs/plans/revitalise-grant-automation-plan.md) Finding 1 is still wrong on disk — [rev_applicanttype](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_applicant/Entity.xml#L304) exists and the amendment says no column does. `revisit_when`: plan-agent corrects FR-035 |
| [IMP-0293](../../logs/improvement-log.jsonl#L290) | **STAYS OPEN.** `V4`. Two approved FR clauses remain partly undeliverable; FR-035 needs Automation #5 and FR-061 needs a DPO decision on ethnicity capture. `revisit_when`: those two land |
| [IMP-0294](../../logs/improvement-log.jsonl#L291) | `APPLIED` on changes 3 and 4 |
| [IMP-0295](../../logs/improvement-log.jsonl#L292) | `APPLIED` on change 10, with its cited path **corrected** — the file is at [src/code-apps/trustee-review-portal/src/generated/models/CommonModels.ts](../../src/code-apps/trustee-review-portal/src/generated/models/CommonModels.ts#L10), not the `src/generated/models/` the finding names |

**States excluded, stated so the cap is not silent:** 26 `reviewer-deferred` (each with a reason a human accepted), 5 `unread` belonging to [review 26](./2026-08-24-improvement-review-6.md) and not re-derived, 0 `already-fixed`, and every `APPLIED`/`REJECTED` entry. All 10 in-scope `unread` entries were read in full and all 10 are dispositioned above.

**Five entries read as `unread` that are not.** [IMP-0278](../../logs/improvement-log.jsonl#L275), [IMP-0279](../../logs/improvement-log.jsonl#L276), [IMP-0280](../../logs/improvement-log.jsonl#L277), [IMP-0284](../../logs/improvement-log.jsonl#L281) and [IMP-0285](../../logs/improvement-log.jsonl#L282) are all clustered by review 26 and none carries a `reviewed_in` stamp, which the gate reports as five WARNINGs. Stamping them is review 26's job at its own approval, not mine — but until it happens the queue cannot distinguish them from findings nobody has opened, which is [IMP-0154](../../logs/improvement-log.jsonl#L151)'s exact lesson.

**Do not route a third review off this queue.** Measured after this draft was written: [verify-improvement-log.py](../../scripts/verify-improvement-log.py) still reports **15 unread** and still fires **both** the blocker and the batch trigger, because `reviewed_in` is only stamped at approval. All 15 are now cited by a review document — 5 by review 26, 10 by this one — so the correct response to those triggers is a **keyword against a named document**, not another dispatch. That distinction is [IMP-0183](../../logs/improvement-log.jsonl#L180), and the gate cannot make it for you until one of the two reviews is approved.

---

## 7. Verification executed for this review

**Level reached: V1, measured.** Nothing in this document is on disk and no live environment was touched.

| Check | Result |
|---|---|
| Change 1's prototype against **today's real tree** | **exit 1 — 4 OPEN rows checked, 2 orphan guesses**, `A-FIN-05` and `A-FIN-07` |
| Change 1's prototype, first draft | 3 orphans — one was `A-FIN-03`, a **false positive** from an uncontrolled status vocabulary (`VERIFIED`, not `CLOSED`). Fixed and re-measured before proposing |
| `npm audit --audit-level=high` in the code app | **exit 0, 0 vulnerabilities** — the gate is green today and can fail tomorrow |
| Manifest pinning | 24 dependencies (5 runtime, 19 dev); **one range spec**, `@types/node ^24.13.3`. The finding says 21 dev — derived, not restated |
| `npm ci` already wired | [build step L752](../../config/revitalise-grant-automation-build.yml#L752). Lockfile-drift needs no new step; asserted from `npm ci`'s documented behaviour, **not** executed |
| [IMP-0290](../../logs/improvement-log.jsonl#L287)'s premise | **Disproved** — [routing.log L211](../../logs/routing.log#L211) records the opus override; [models.yml L89](../../config/models.yml#L89) and the generated frontmatter both show only the default |
| [IMP-0292](../../logs/improvement-log.jsonl#L289)'s premise | **Confirmed** — `rev_applicanttype` exists at [Entity.xml L304](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_applicant/Entity.xml#L304) |
| [IMP-0293](../../logs/improvement-log.jsonl#L290)'s premise | **Confirmed** — `rev_ethnicgroup` matches nothing under `src/` |
| [IMP-0295](../../logs/improvement-log.jsonl#L292)'s premise | **Confirmed on substance, wrong on path.** No `apply` member; `count` capped at 5000; `MAX_ROWS = 500` |
| [IMP-0294](../../logs/improvement-log.jsonl#L291)'s premise | **Confirmed** — manifest committed 2026-08-21 18:45, four retired rows name that exact trigger |
| Review 26's fold-in claim at [routing.log](../../logs/routing.log) 23:25 | **False.** No `IMP-0286`/`IMP-0287` anywhere in review 26 |
| A-FIN-07 marker fix, dispatched 23:25 | **Never landed.** No `A-FIN` string in [ensure-auditing.ps1](../../provisioning/dataverse/ensure-auditing.ps1) |
| `generate-known-failure-modes.py --check` | exit 0, current at 292 entries |
| Live / retired constraint rows | **79 / 10**, derived |

**Not verified, and it is the honest limit.** Change 1 is a scratch prototype, not final code, and will be re-measured at application. The dispatch-reconciliation script of §5 is **not written and not measured** — that is why it is a decision and not a change. No Pester suite ran, because nothing here touches PowerShell. No live Dataverse read was attempted; per cluster B that is exactly the claim an agent should stop making without stating its harness mode.

---

## 8. Digest impact

I expect to append **four** findings at application, taking the log from 292 to 296:

- `IMP-0290`'s root cause disproved by the dispatch record (`corrects: IMP-0290`) — the first entry in this project to carry `corrects` against a finding **being processed in the same review**, which is the case review 26's change 3 is built for
- two further orphan guesses found mechanically that the prose finding never saw (`declared-policy-not-mechanically-enforced` → `x9`)
- the 23:25 double-stall, taking `dispatched-agent-stalls-silently` from `x1` to `x3`
- `refusal_context` required by a gate and documented nowhere

`gate-cannot-fail` stays at `x32` — I am proposing no third patch to the `corrects` rung. Both growing classes are already over the 20-lesson display cap, so I expect the new lessons in the not-shown lists and the line count roughly unchanged. I regenerate and report measured before-and-after on approval.

---

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-25-improvement-review.md

Findings processed: 10 unread  →  7 clusters
Regression check:   3 prior changes audited, 2 classes recurred
Proposed:           1 constraint (cap 3), 2 gates/scripts, 6 skill/knowledge edits,
                    3 agent-file edits, 1 constraint amendment, 0 retirements
Altitude calls:     2 generalised from instance to class, 4 left as knowledge lines,
                    1 rejected as proposed (premise disproved, mechanism impossible)
Digest:             will regenerate — predicted 292 → 296, will report measured

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 10. Applied — measured, 2026-08-25

**All 12 changes are on disk and all 10 findings are dispositioned.** Two of this document's own
predictions were wrong, and both are corrected here rather than left to be inherited.

| # | Landed at | Measured |
|---|---|---|
| 1 | [scripts/verify-assumption-markers.py](../../scripts/verify-assumption-markers.py), build step [assumption-markers](../../config/revitalise-grant-automation-build.yml#L263) | **exit 1, and it found 4 orphans not 2** — see below. `--selftest` exit 0 |
| 2 | [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) `Verify By` | Names the step; the human grep clause is gone |
| 3 | [C-TECH-074](../../constraints/technology/technology-constraints.md#L144) | One row; [C-TECH-020](../../constraints/technology/technology-constraints.md#L60)–023 annotated in place |
| 4 | build step [code-app-audit](../../config/revitalise-grant-automation-build.yml#L811) | `npm audit --audit-level=high`, exit 0, 0 vulnerabilities |
| 5 | [generate-subagents.py](../../scripts/generate-subagents.py#L207) self-check | 18 `.claude/agents/` files regenerated, generator `--check` clean |
| 6 | [WORKFLOW.md L89](../../agents/WORKFLOW.md#L89) + [lead-agent.md L95](../../agents/lead-agent.md#L95) | Convention only. The script is **still not built** — now [IMP-0300](../../logs/improvement-log.jsonl#L297) |
| 7 | [build-and-deploy.md](../../knowledge/technology/build-and-deploy.md#L288) + [how-to-verify-a-platform-contract.md](../../skills/how-to-verify-a-platform-contract.md#L130) | Prose. `agents/test-agent.md` deliberately not touched — the read path was the fix |
| 8 | [how-to-log-an-improvement.md](../../skills/how-to-log-an-improvement.md#L110) | `refusal_context` now documented where findings are written |
| 9 | [commercial-agent.md](../../agents/commercial-agent.md#L49) | Prose. Scoped to the approved text; see the note below on [IMP-0297](../../logs/improvement-log.jsonl#L294) |
| 10 | [code-apps.md](../../knowledge/technology/code-apps.md#L160) | Aggregation subsection, all three obstacles |
| 11 | [CR-11](../../knowledge/domain/compliance-requirements.md#L27) | Plus the accepted-residual-risk note the override needed |
| 12 | [how-to-write-requirements.md](../../skills/how-to-write-requirements.md#L59) + [how-to-intake-external-documents.md](../../skills/how-to-intake-external-documents.md#L43) | Intake steps 4–9 renumbered |

**§7 undercounted the orphans by half.** The shipped gate reports **4 orphan rows of 6 OPEN
checked, across 3 documents** — `A-002`, `A-FIN-05`, `A-FIN-07` and `A-TRM-2` — where §7 recorded
2 from a scratch prototype that read only the Dev Summary. The prose finding
[IMP-0286](../../logs/improvement-log.jsonl#L283) had reported 1. Logged as
[IMP-0299](../../logs/improvement-log.jsonl#L296); four comment markers are delivery work for
development-agent and **the build gate is red until they land**.

**§8 predicted 292 → 296. The measured log is 299 entries, 484 digest lines.** The base was 294,
not 292: [IMP-0296](../../logs/improvement-log.jsonl#L293) and
[IMP-0297](../../logs/improvement-log.jsonl#L294) were appended by plan-agent at 12:32, after the
keyword. Four entries were appended at application, but the fourth is not the one §8 named —
*"`refusal_context` required by a gate and documented nowhere"* was not logged as its own finding
because it is [IMP-0287](../../logs/improvement-log.jsonl#L284)'s own substance and change 8 is its
fix; a separate entry would have been born `already-fixed`. In its place:
[IMP-0301](../../logs/improvement-log.jsonl#L298), the partial application of this review. A
**fifth** was then logged while revising review 26 —
[IMP-0302](../../logs/improvement-log.jsonl#L299): §1 above says *"§5 puts it to you"* about the
twice-patched `corrects` rung, and **§5 never asks that question**, so the reviewer approved this
document without it. Review 26's revision now carries the question.

**Two entries arrived after the keyword and neither disproves anything applied here.**
[IMP-0296](../../logs/improvement-log.jsonl#L293) is a **second instance** of cluster E's class and
names the same file as change 12, from the other direction — a data item no *organisation* holds,
where [IMP-0293](../../logs/improvement-log.jsonl#L290) is one no *column* supplies. Change 12 was
applied **exactly as approved** and does not cover the external-provenance flavour: widening
approved rule text on an entry the reviewer has not seen is the substitution
[activation step 8](../../agents/improvement-agent.md#L127) forbids. That widening is the next
review's first item. [IMP-0297](../../logs/improvement-log.jsonl#L294) corroborates change 9 and
extends it — a sizing made against `PROPOSED` text that later changed — and was likewise left out
of the applied text for the same reason.

**Still not verified.** No live environment was touched and no Pester suite ran, because nothing
here is PowerShell. The dispatch-reconciliation script of §5 is not built. Constraint rows now
stand at **80 live / 10 retired**, derived.
