# Improvement Review — 2026-09-28 (1): the batch after the intake rework

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 50 `NEW` → 19 clusters (46 unread, plus 4 logged by this review: three from what its measurements showed, one recording the harness refusal)
**Trigger:** batch threshold (`batch_threshold()`), routed after a DEV deploy result (see §0: the routing line should have carried `trigger:post-deploy`)
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** ~~DRAFT — parked at the gate, nothing applied~~ **APPLIED 2026-09-29, in the working tree, not committed.** `APPROVE IMPROVEMENTS` from Xander Lykopoulos, relayed by lead-agent. All 23 changes landed, and all 50 entries are closed or deferred with a reason (§8). **One act is still owed by the reviewer:** the harness refused the re-point of EX-004 that the reviewer decided during the apply, so it is handed over as a script (§8). The engine files are uncommitted in `.engine` (§8, *Publishing*).
**WBS:** system work, `wbs:system`. The findings come from `wbs:4.2,4.3` (intake rework) and `wbs:6.8` (trustee portal); no change here is billable.
**Filename:** claimed on 2026-09-28 by the batch dispatch that stalled at 09:47 ([routing.log L1065](logs/routing.log#L1065)); this dispatch replaces it and adopted the orphaned stub rather than leave it behind. Drafted 2026-09-29.

---

## Summary

The intake rework produced most of this batch: defects in the intake flow that only a real submission showed, places where the approved architecture document contradicts itself or the source, and platform facts learned by running into them. This review proposes 23 changes, all at existing gates or in reference files: four new checks inside gates that already run, three repairs to the learning system's own bookkeeping, five agent-file lines, and ten skill and knowledge edits. No new constraint.

**Waiting on you:** two commands the harness would not let this agent run (below), then `APPROVE IMPROVEMENTS` or feedback. One decision, about a data-protection exception, is independent of the keyword.

## What this review proposes

1. **Four static checks, each at a gate that already runs HARD** ([flow-definition-language](config/revitalise-grant-automation-build.yml#L648), [field-length-limits](config/revitalise-grant-automation-build.yml#L478), [tad-coverage](config/revitalise-grant-automation-build.yml#L408)). A `createArray()` call with no argument fails the flow gate: it throws at runtime, and it reached DEV in the intake flow. Any flow expression over 8,192 characters fails the length gate, since the packer does not check that platform limit. The architecture-coverage gate gains two value checks: every table in the solution has a schema block in the architecture document, and a security value the document states for a column matches the column's source. Three of the four were measured against the real files. The length check's expected result comes from the finding and is confirmed before wiring. §3 gives the counts.

2. **Three repairs to the learning system's own bookkeeping** ([verify-improvement-log.py](scripts/verify-improvement-log.py#L2507), [verify-routing-reconciliation.py](scripts/verify-routing-reconciliation.py#L352), [generate-known-failure-modes.py](scripts/generate-known-failure-modes.py#L830)). The queue gate stops raising "read this correction before applying the review" about reviews that were applied weeks ago: 8 of its 10 current warnings are that. A finding that records a fix gets its own field, so it is no longer marked on the digest as having disproved a correct lesson. Every routing line to this agent names its trigger from a fixed list: the two routing lines since the lane split both stated their trigger from memory, and both were wrong. And the digest's capability section stops hiding the certificate lesson two agents are told to read it for.

3. **Five agent-file lines, each where the agent looks at the moment it decides.** lead-agent tags the trigger. WORKFLOW and development-agent say `fixes`, not `corrects`, for a fix. build-agent gains the exception its warning rule was missing ([L181](agents/build-agent.md#L181)). pipeline-agent gets the copyable pre-state read ([L213](agents/pipeline-agent.md#L213)).

4. **Ten skill and knowledge edits,** mostly lessons from the intake rework: run history is a log and how to hide it, guards and fallbacks tested with the input that triggers them, the test runner's strict mode, the column-retype sequence, reading live data under Auto Mode, and two domain facts the rework proved wrong in the knowledge files.

### Elements added

| Element | What it is |
|---|---|
| Check 10 in `.engine/scripts/verify-flow-definition-language.py` | No zero-argument `createArray()` |
| `flow-expression` in `.engine/scripts/verify-field-length-limits.py` `PLATFORM_LIMITS` | 8,192 characters per expression |
| Assertions (c) and (d) in `verify-tad-coverage.py` | Every table has a §3.1 block; a stated `IsSecured` matches source |
| Check 4 in `verify-routing-reconciliation.py` | Improvement-agent routing lines carry a trigger from a closed list |
| `fixes` field in the improvement-log schema | "This entry fixes that one", distinct from "this entry disproves that one" |

### Elements changed

| Element | Change |
|---|---|
| `verify-tad-coverage.py` assertion (b) | A negated mention ("not trustee-visible") no longer counts as a marking |
| `verify-improvement-log.py` corrects rung | Silent once the review it warns about has been applied |
| `generate-known-failure-modes.py` | Capabilities ranked without the "unfixed first" term; selftest for cited capabilities |
| `config/gate-baselines.json` | Four dated entries for the four known `tad-coverage` findings, owned by architect-agent |
| `config/revitalise-grant-automation-pipeline.yml` | Three DEV notes whose stated cause is false, corrected |

## What is still open

**The harness refused this draft's bookkeeping, twice.** Stamping the 46 processed entries with this document's name was refused (*"[Modify Shared Resources]"*), and so was regenerating the digest after this review appended three findings. Per this project's rule, neither was retried by another route. Until you run them, the queue gate reports all 46 as never opened, which keeps the batch trigger red. The next build's [`known-failure-modes` step](config/revitalise-grant-automation-build.yml#L113) will also fail, because the digest is four entries behind the log (this review appended four findings; the fourth records the refusal itself). Both commands are in *What you need to decide*, item 1.

**The 2026-09-27 review, still parked, overlaps this one in one file.** Its change 3 extends the retype section of [dataverse.md](knowledge/technology/dataverse.md#L327), and this review's row 19 adds three facts to the same section, so row 19 lands after it. If that review is approved first, nothing changes. If it is rejected, row 19 lands as a self-contained addition. One fact from this batch also bears on that review's own entry: development-agent's step 5 confirmed live that all ten field-permission rows came back and all eleven columns exist. That is most of the observation its deferral is waiting for. It is that review's to use, not this one's.

**The secure-data gate the data-protection exception is waiting for is still not built, and this review does not build it.** A check that flags every flow action on a personal-data table was measured at 5 clear true positives in 12 flags. That is below the bar for a gate, so it is withheld (§2, cluster K). A precise check needs a list of which columns are personal, which is the decision below.

**Most of the intake defects are fixed in source and cannot be closed here.** Each was only visible when a real website submission ran, and none has run since the fixes. Nine findings stay open with a named observation that would close them (§5).

## What you need to decide

**1. Run the two refused commands, then send the keyword.**

**Problem** — The harness refused both writes to `logs/`, so the queue reads this batch as unopened and the digest is behind the log.
**Suggested fix** — Run `python3 "<scratchpad>/stamp-reviewed-in.py"` then `python3 scripts/verify-improvement-log.py && python3 scripts/generate-known-failure-modes.py` from the repository root (the stamp script's full path is in the gate hand-off).
**What happens if you don't** — The next build fails at the digest check, and the batch trigger keeps firing on 46 entries this review has already read. A second strategic dispatch would then re-read them.
[improvement-agent.md, step 6](agents/improvement-agent.md#L150)

---

**2. Re-scope the data-protection exception for flow run history, or raise the change order it points to.**

**Problem** — [EX-004](contract/known-exceptions.json#L29) accepts six named flow actions that no longer expose personal data, while five reads in the two DocuSign acceptance flows that do return names, emails and referee phone numbers are covered by nothing.
**Suggested fix** — Re-point EX-004 at `REV | Acceptance | Create Envelope` and `REV | Acceptance | Reminders & Escalation`, keeping its expiry, and decide whether to authorise a list of personal columns so a precise secure-data gate can be built.
**What happens if you don't** — EX-004 expires on 2026-10-16 describing an exposure that is gone, while the real one has no owner, no expiry and no check.
[known-exceptions.json EX-004](contract/known-exceptions.json#L29)

---

Closing line: every count in §2 and §3 was measured by command at draft time, and the commands are named where the count appears. Nothing is applied, so no gate has run over a changed file. The three new checks have no selftest yet, and each must reproduce its §3 count before it is wired. The two refused writes are unverified by definition.

---

## 0. Where this review departs from its findings and its brief, and why

**Two proposals are disproved by measurement, and both are narrowed.** Defaulting `verify-tad-coverage.py` to every architecture document (IMP-0862) fails on 6 of 7. Only the primary document has the §3.1 table-block shape the parser reads, and a run against the postcode TAD exits 1 with 4 violations (0 specs parsed, floors unmet). What IMP-0862 actually needs is narrower and measurable: the two tables that only a delta TAD describes (`rev_localauthorityregister`, `rev_citysettlementregister`) have no §3.1 block in the primary document, while the precedent (`rev_roundfinance` and the two statistics tables, all from a delta TAD) folded them in. Counting a review as approved only when an entry's `applied_by` names it (IMP-0916) would drop 542 of 628 closure records: 86 name the review. Logged as IMP-0952.

**The table-level secure-data gate is withheld on its measured precision.** 23 connector actions touch a Tier 3/4 table. 18 can carry personal columns (a read that selects only the id and primary name cannot), and 12 of those set no `secureData`. Of the 12, five clearly return personal data. The other seven write a grant's status or dates, or a score, and whether those are personal is a judgement the check cannot make. 5 of 12 is below the bar. Logged as IMP-0951, with the exception drift it found.

**The routing line for this batch named the wrong trigger and the wrong count.** It followed a PARTIAL DEV stage line ([pipeline.log L231](logs/pipeline.log#L231)), so it was the post-deploy batch and owed `trigger:post-deploy`. Its reason, *"261 NEW entries, exceeds batch threshold"* ([routing.log L1064](logs/routing.log#L1064)), is the rule from before reviewer decision D-U1: the trigger counts unread and fixed-in-flight entries, which were 46. [verify-routing-reconciliation.py](scripts/verify-routing-reconciliation.py#L352) check 3 reports the episode. The dispatch was right in outcome, so nothing broke; it is the second routing line in two days composed from a remembered rule. Logged as IMP-0950.

**IMP-0899's proposed home would put this client's literals in the engine.** It asks for a line in `agents/architect-agent.md` naming SDD §7.1a, NFR-031 and ADR-027. That file is an engine symlink shared by every client (`skills/how-to-promote-a-finding.md` §6). The rule goes to `knowledge/domain/data-entities.md` instead, which architect-agent already loads.

**Parked entries in other reviews are named, not re-derived.** IMP-0934 is in [2026-09-27-improvement-review.md](docs/improvements/2026-09-27-improvement-review.md#L219) and IMP-0855 in `2026-09-23-improvement-review-7.md`; both need their own keyword. Two reviewer-deferred entries, IMP-0320 and IMP-0322, are cited as context in cluster K and are not re-processed.

---

## 1. Regression check — did the last reviews' changes work?

The reviews applied most recently are 2026-09-26-3, -4, -6 and -7 (applied 2026-09-26 and 2026-09-27). The 2026-09-27 review audited review 6 at 20:18 on 2026-09-27; this audit covers everything logged since, and the other three reviews in full. One DEV deploy has run since they landed.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Post-deploy batch trigger: WORKFLOW, lead-agent and this agent's rows (review 7, changes 4–6) | 2026-09-26 | `learning-substrate-destroyed` (WS-U) | **YES, the prose half** — the one deploy since was followed by a batch, but the routing line carried no tag and a pre-D-U1 count (IMP-0950) | **Prose recurred.** The report half worked: check 3 caught it. Escalated to a checked tag vocabulary (rows 6 and 8) |
| Lane split for blockers: WORKFLOW and lead-agent rows (review 4, changes 6–7) | 2026-09-26 | `declared-policy-not-mechanically-enforced` | **YES, the prose half** — a governance-lane blocker was routed immediately under the pre-lane wording (IMP-0936), while the queue gate printed the correct lane note | **Prose recurred.** The gate worked; the router did not read it. Same escalation |
| Routing check 3, `trigger:post-deploy` (review 7, change 2) | 2026-09-26 | the above | Fired on the one episode it could see | Working — it is what surfaced IMP-0950 |
| Post-deploy completeness and the `PARTIAL` stage word (review 3) | 2026-09-26 | `pipeline-dispatch-stops-before-declared-post-deploy` | NO — the 2026-09-28 stage line used `PARTIAL` with the reviewer action named; `--audit` reports 0 findings | Working |
| Production guard (review 7, changes 1, 3, 7, 10) | 2026-09-26 | governance blockers before production | Not exercised — no production deploy | Too early to judge |
| `fixed_in_flight` (review 4, change 2) | 2026-09-26 | `build-blocked-by-the-finding-it-remediates` | Not exercised — no deploy-lane blocker since | Too early to judge |
| `items:` on every handoff (review 6, changes 8–14) | 2026-09-27 | capability (WS-W3) | 13 delivery dispatches since carried none. None of them was work-item work: one ledger item names `4.2`, and the intake rework came from a payload sample, not from the feedback sheet | Too early to judge — no evidence either way |
| Lock-held id allocator, its wording swept (IMP-0810, WS-W1) | 2026-09-26 | `duplicate-improvement-id-race` | NO — three appends this session, no collision; the clause IMP-0901 asked to remove is already gone | Working |

**Changes whose class recurred after a *prose* fix:** the two routing rules above → escalated to a mechanical check (rows 6 and 8).
**Changes whose class recurred after a *gate*:** none. The one gate involved fired correctly.
**Closure evidence against level:** no entry closed by these reviews has recurred, so no closure is shown to have been a claim.

---

## 2. Clusters and promotion decisions

`Residual` is mandatory. Instance counts are re-derived from `class_instance_of` and the tree, not from the findings' prose.

```
CLUSTER: intake guards and fallbacks never executed on the input that triggers them  (x5: IMP-0926, IMP-0927, IMP-0930, IMP-0945, IMP-0949)
Altitude:   CLASS — five defects in one flow, one property: an If guarding a rejection, a
            Derive_ fallback, an equality against an empty setting, a preserve-on-omission
            column and a coalesce fallback, each asserted by shape and never evaluated with
            the adverse input. Tags differ (test-asserts-the-defect, approved-document-
            internally-inconsistent x2, stale-claim, no-assertion-on-shipped-content)
Ladder row: "a tool could catch it mechanically" for the one static case; knowledge line for
            the rest, which need an executor with the right input
Becomes:    row 1 (createArray() arity, a static and unconditional platform fact) and row 17
            (the test-the-adverse-input rule, with the five worked cases)
Retires:    nothing
Cites:      IMP-0926, IMP-0927, IMP-0930, IMP-0945, IMP-0949
Residual:   no gate can decide which branch of an If holds the rejection, or which input
            triggers a fallback, without evaluating the flow. IntakeContract.Tests.ps1 now
            does that for this flow (D-01, D-02); no other flow has an executor. All five stay
            open until a real website submission runs (§5)
```

```
CLUSTER: platform-field-length-limit-unenforced  (x1 NEW: IMP-0931; class x2 with IMP-0009)
Altitude:   CLASS — second instance. The general gate exists (verify-field-length-limits.py,
            PLATFORM_LIMITS); this adds the limit, not a second gate
Ladder row: "second instance → generalise"
Becomes:    row 2
Retires:    the instance Pester block "Power Automate platform limit — characters per
            expression" (IntakeContract.Tests.ps1 L1416), routed to development-agent once
            row 2 is green. Its known-bad case must fail under row 2 first
Cites:      IMP-0931
Residual:   IMP-0931's second proposal, a check that every externally supplied text value is
            cut to its column's MaxLength before a write, is NOT built: it needs a map from
            trigger input to written column that no parser here builds. Knowledge line only
```

```
CLUSTER: verify-tad-coverage reads less than the document says  (x3: IMP-0862, IMP-0896, IMP-0944)
Altitude:   CLASS — three findings on one gate: tables it never sees, a value it never
            compares, a phrase it misreads. The fix asserts on values wherever one exists
Ladder row: "a tool could catch it mechanically"
Becomes:    row 3 — (c) every Entities/ folder has a §3.1 block; (d) a §3.1 row stating
            IsSecured=0|1 matches Entity.xml; (e) a negated "trustee-visible" is not a marking
Retires:    nothing
Cites:      IMP-0862, IMP-0896, IMP-0944
Measured:   (c) 15 entity folders, 13 blocks → 2 findings, 2 true (rev_localauthorityregister,
            rev_citysettlementregister). (d) 20 column claims in §3.1 → 2 findings, 2 true
            (TAD L593: rev_helperorganisation, rev_helperrelationship say 0, source says 1).
            (e) 0 negated mentions today, because rev 10's rows were reworded; 0 is correct,
            and the pre-rewording text is the fixture
Residual:   (d) sees only the 20 claims written as IsSecured=<digit>; a row stating security
            in prose is not compared. (c) cannot check the delta TADs themselves, because 6 of
            7 have no §3.1 shape; it forces their tables into the primary document instead,
            which is the existing precedent. (e) is still a phrase test, now narrowed; the safe
            wording goes in its finding message. The four findings are red today, so they are
            baselined in config/gate-baselines.json against architect-agent's next revision
```

```
CLUSTER: the improvement log's link fields say more than the author meant  (x3: IMP-0916, IMP-0932, IMP-0937)
Altitude:   CLASS — one field (corrects) carries two meanings, and one warning's remedy trips a
            second check. IMP-0937 is the measured instance: it records a FIX of IMP-0934 and
            its corrects field marks IMP-0934's correct lesson as superseded on the digest.
            Class two-recorded-lessons-contradict-each-other is x2 (IMP-0460)
Ladder row: "an agent had the information and still did the wrong thing" + a schema change
Becomes:    rows 4, 5, 9, 10, 13
Retires:    nothing
Cites:      IMP-0916, IMP-0932, IMP-0937
Measured:   the corrects rung prints 10 "appended later" warnings today; 8 name a review that
            has since closed at least one entry, so its keyword was given (IMP-0272, 0290, 0320,
            0430, 0437, 0703, 0763, 0879). Silencing those leaves 2: IMP-0934 (a genuinely
            parked review) and IMP-0298 (its newest review closed nothing)
Residual:   the 43 older entries carrying corrects are not re-classified as fix or disproof;
            only IMP-0937 moves, because it is the one measured. The left-behind check still
            infers approval from reviewed_in on a closed entry; row 4 removes the reason to
            write such a stamp, it does not change that inference
```

```
CLUSTER: dispatch-brief-asserts-unverified-fact  (x4 NEW: IMP-0887, IMP-0929, IMP-0936, IMP-0950; class x12)
Altitude:   CLASS — the class has 12 instances and no defence. The two routing instances
            (IMP-0936, IMP-0950) share a property a value can check: the trigger a router
            names. IMP-0936's own proposal said to build the check on a second instance; this
            is it
Ladder row: "second instance → generalise"; "a tool could catch it mechanically"
Becomes:    rows 6 and 8 — a closed trigger vocabulary; a deploy-blocker tag must name an id
            whose lane derives to deploy
Retires:    nothing
Cites:      IMP-0887, IMP-0929, IMP-0936, IMP-0950
Measured:   improvement-agent routing lines since the lane cutover (2026-09-26): 2, both
            untagged, both true (routing.log L1041, L1064)
Residual:   the check cannot verify a batch-threshold count after the fact: reviewed_in stamps
            carry no timestamp, so the queue at a past moment is not reconstructable. IMP-0929
            (a brief's pointers to a register and a digest view) is a different mechanism with
            nothing to check — REJECTED, no change
```

```
CLUSTER: digest-cap-hides-a-whole-subject-area  (x1 NEW: IMP-0902; class x3)
Altitude:   INSTANCE of a class already defended for defects; the capability ranking is the gap
Ladder row: "the system's own memory failed" → read-path change
Becomes:    row 7
Retires:    nothing
Cites:      IMP-0902
Measured:   IMP-0022 is cited at build-agent.md L68 and pipeline-agent.md L60 and is rendered
            in neither agent's --for view; it appears only in the capped index
Residual:   the selftest covers ids cited in the three agents' activation steps only; a
            capability named elsewhere can still be capped out
```

```
CLUSTER: agent-file-restates-constraint-incompletely  (x2: IMP-0941, IMP-0942)
Altitude:   INSTANCE — IMP-0942 disproves IMP-0941's diagnosis and names the real gap
Ladder row: "an agent had the information and still did the wrong thing"
Becomes:    row 11
Retires:    nothing
Cites:      IMP-0941, IMP-0942
Residual:   other agent files may summarise constraints without their amendments; no check
            compares the two, and a prose check here is the instrument measured at 48–100% false
```

```
CLUSTER: live reads under Auto Mode and the pre-state they enable  (x2: IMP-0900, IMP-0928)
Altitude:   CLASS — IMP-0928 establishes the route; IMP-0900 is a skipped pre-state read that
            route makes cheap
Ladder row: "a capability was established and could be lost again" + agent line
Becomes:    rows 12, 14, 20
Retires:    nothing
Cites:      IMP-0900, IMP-0928
Residual:   the route is observed, not guaranteed; the classifier can refuse it tomorrow, and
            it cannot read EntityDefinitions metadata
```

```
CLUSTER: an intake row read by its first column  (x3: IMP-0918, IMP-0919, IMP-0920)
Altitude:   CLASS — three misreadings of one checklist: an unresolvable reference, a superseded
            ask, a negatively phrased ask
Ladder row: "an agent had the information and still did the wrong thing" → skill
Becomes:    row 15
Retires:    nothing
Cites:      IMP-0918, IMP-0919, IMP-0920
Residual:   no gate reads acceptance wording, deliberately (prose). The reference half is
            already mechanical at ledger intake (work-items.py) and in routing check 1; the
            skill moves it earlier
```

```
CLUSTER: domain knowledge the real payload proved wrong  (x4: IMP-0895, IMP-0897, IMP-0898, IMP-0899)
Altitude:   INSTANCE x4 — each a fact about this client's form or data model
Ladder row: "one instance, general cause, a human needs to know it" → knowledge; IMP-0897 is
            the second instance of sdd-mechanism-claim-not-ground-truthed (IMP-0830), so its
            general half goes to the requirements skill
Becomes:    rows 16, 21, 22
Retires:    nothing
Cites:      IMP-0895, IMP-0897, IMP-0898, IMP-0899
Residual:   nothing compares knowledge/domain/ claims with the payload sample; the next form
            change can stale them again
```

```
CLUSTER: run history is a log  (x3: IMP-0894, IMP-0921, IMP-0951; with deferred IMP-0320, IMP-0322)
Altitude:   CLASS — the fourth and fifth findings on one control since 2026-08-25, still with no
            gate
Ladder row: "a tool could catch it mechanically" — WITHHELD on measured precision (5 of 12)
Becomes:    row 17 (the per-type secureData table and the non-propagation through Compose);
            the gate and the C-DOM-004 Verify By widening wait for the column list (decision 2)
Retires:    nothing
Cites:      IMP-0894, IMP-0921, IMP-0951
Residual:   the whole control. Until a column-level check exists, EX-004's expiry is the only
            thing that looks at this, and EX-004 names the wrong actions today
```

```
CLUSTER: two-invocation-paths-disagree — the suite runner's strict mode  (x2: IMP-0924, IMP-0939)
Altitude:   CLASS — one runner setting, two mechanisms (a title token, an XML child read)
Ladder row: "second instance → generalise" — but the build already runs the strict path
            (build config L913), so neither can ship; the cost is a re-run. A knowledge rule
            stated for the class, not per mechanism, is proportionate
Becomes:    row 18
Retires:    nothing
Cites:      IMP-0924, IMP-0939
Residual:   a third mechanism will surface the same way, and cost one more re-run
```

```
CLUSTER: the column-retype sequence, completed  (x3: IMP-0933, IMP-0938, IMP-0940)
Altitude:   CLASS — three gaps in one procedure, found while running it
Ladder row: knowledge; the mechanical half is the parked 2026-09-27 review's check
Becomes:    row 19, landing after that review's change 3
Retires:    nothing
Cites:      IMP-0933, IMP-0938, IMP-0940
Residual:   the row-size budget (IMP-0933) is documented by Microsoft and was not reproduced
            here, so it is recorded as documented, not as measured
```

```
CLUSTER: the DEV intake-auth notes in the pipeline config  (x2: IMP-0943, IMP-0947)
Altitude:   INSTANCE — one stale cause, one missing step
Ladder row: the pipeline-config boundary table: the stated cause is a repository fact, so this
            review corrects it; the missing step is delivery work
Becomes:    row 23; the DEV step and settings block are routed to development-agent
Retires:    nothing
Cites:      IMP-0943, IMP-0947
Residual:   whether an import resets "Who can trigger the flow?" is readable only in the
            designer (IMP-0947), so a human closes it
```

```
CLUSTER: approved documents that disagree with what they describe — routed, no system change  (x4: IMP-0892, IMP-0893, IMP-0922, IMP-0923)
Altitude:   NOTES — each is fixed in source or owed by architect-agent; the class
            (approved-document-internally-inconsistent, x44 in the digest) has no general
            gate, and row 3 (d) is the only value-level part of it this batch exposes
Becomes:    nothing here; routed (§3.2)
Cites:      IMP-0892, IMP-0893, IMP-0922, IMP-0923
Residual:   the class stays undefended in general
```

```
CLUSTER: finding-premise-fails-re-measurement  (x3: IMP-0901, IMP-0935, IMP-0952; class x7)
Altitude:   CLASS — seven instances, every one caught by this agent's step 6. The defence works
            downstream; the fix is upstream, at the logging skill. IMP-0935's own proposal said
            to add it on a recurrence; IMP-0952 is the recurrence
Becomes:    row 13 (the search-before-asserting paragraph). IMP-0901 needs nothing: its change
            already landed with WS-W1 (WORKFLOW.md L372)
Cites:      IMP-0901, IMP-0935, IMP-0952
Residual:   an author can still skip the search; step 6 stays the backstop
```

```
CLUSTER: harness-blocks-destructive-call  (x3: IMP-0891, IMP-0946, IMP-0953)
Altitude:   NOTES — the refusal protocol was followed all three times and worked. IMP-0953 is
            this review's own: the step-6 stamp and the digest regeneration were refused, the
            allocator's appends were not, and both refused commands are handed to the reviewer
Becomes:    nothing — REJECTED as "no rule change follows"
Cites:      IMP-0891, IMP-0946, IMP-0953
Residual:   the refusal boundary is still not isolated; two new reason strings ("[Blind Apply]",
            "[Modify Shared Resources]") are recorded in the entries' own text
```

```
CLUSTER: hand-maintained-count-drifts-from-source  (x1 NEW: IMP-0925)
Altitude:   NOTE — the rule already exists (coding-standards.md's first remedy); the test fix
            is delivery work
Becomes:    nothing here; routed
Cites:      IMP-0925
Residual:   the literal will need a fourth bump if the test is not changed
```

```
CLUSTER: fix-claimed-not-reverified-against-live-tool  (x1: IMP-0948)
Altitude:   NOTE — one instance; the proposed gate fetches a report from a signed URL, which is
            live work and belongs to a delivery agent
Becomes:    nothing here; routed
Cites:      IMP-0948
Residual:   the lint step still asserts only that the checker's log is not empty
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | `.engine/scripts/verify-flow-definition-language.py` ([L79](.engine/scripts/verify-flow-definition-language.py#L79)) | Check 10: reject the literal zero-argument `createArray()` in any expression string. Measured: 0 at HEAD; 10 literal occurrences in the intake flow at `HEAD~1`. The finding counts 19, so the apply step reconciles the spelling variants before writing the regex | IMP-0949 | YES — `python3 scripts/verify-flow-definition-language.py --selftest`; then the real corpus (0), then the `HEAD~1` definition (≥ 10) | already wired — HARD `flow-definition-language` ([L648](config/revitalise-grant-automation-build.yml#L648)) |
| 2 | script | `.engine/scripts/verify-field-length-limits.py` ([L62](.engine/scripts/verify-field-length-limits.py#L62)) | `PLATFORM_LIMITS["flow-expression"] = 8192`, cited to Microsoft's limits page, checked over every `@`-expression string in `Workflows/*.json` | IMP-0931 | YES — `--selftest` with a 8,193-character fixture; real corpus expected 0 (longest reported 6,955) | already wired — HARD `field-length-limits` ([L478](config/revitalise-grant-automation-build.yml#L478)) |
| 3 | script | `scripts/verify-tad-coverage.py` + byte-identical `.engine/` copy ([L124](scripts/verify-tad-coverage.py#L124)) | Assertions (c), (d), (e) of cluster C; four `config/gate-baselines.json` entries (owner architect-agent, clears when the TAD adds the two blocks and corrects L593, expiry 2026-10-13) | IMP-0862, IMP-0896, IMP-0944 | YES — `python3 scripts/verify-tad-coverage.py --selftest`; real run reports 4 baselined findings | already wired — HARD `tad-coverage` ([L408](config/revitalise-grant-automation-build.yml#L408)), with the baseline |
| 4 | script | `scripts/verify-improvement-log.py` + `.engine/` copy ([L2507](scripts/verify-improvement-log.py#L2507)) | Corrects rung: silent when the newest review that processed the target has closed ≥ 1 entry; when the correcting entry is itself closed, the remedy says do not stamp it | IMP-0916 | YES — `--selftest` gains both fixtures; real run: 10 → 2 warnings, the 8 removed named in cluster D | already wired — HARD `improvement-log-check` ([L80](config/revitalise-grant-automation-build.yml#L80)) |
| 5 | script | `scripts/verify-improvement-log.py` + `.engine/` copy | Optional `fixes` field (id or list), validated like `corrects`, feeding the "fix landed, target unprocessed" rung and nothing else; `generate-known-failure-modes.py` does not render it as CORRECTED. IMP-0937 moves from `corrects` to `fixes` at apply | IMP-0932, IMP-0937 | YES — `--selftest` fixtures: a `fixes` entry raises the unprocessed-target warning and no CORRECTED marker | already wired — same step |
| 6 | script | `scripts/verify-routing-reconciliation.py` + `.engine/` copy ([L352](scripts/verify-routing-reconciliation.py#L352)) | Check 4, report only: improvement-agent `ROUTED_TO`/`RE-DISPATCHED` lines since 2026-09-26 carry one of `trigger:post-deploy`, `batch-threshold`, `deploy-blocker`, `reviewer`, `capability`; a `deploy-blocker` line names an id whose `derive_lane()` is `deploy` | IMP-0950, IMP-0936, IMP-0887 | YES — `--selftest`; real run 2 findings, 2 true | already wired — SOFT `routing-reconciliation` ([L134](config/revitalise-grant-automation-build.yml#L134)) |
| 7 | script | `scripts/generate-known-failure-modes.py` + `.engine/` copy ([L830](scripts/generate-known-failure-modes.py#L830)) | Capabilities section sorted without the NEW-before-APPLIED term; selftest: every IMP id cited in the activation steps of the three `--for` agents renders in that agent's view. The 20 rendered before and after are listed at apply | IMP-0902 | YES — `--selftest`, and `--for build-agent` shows IMP-0022 | already wired — HARD `known-failure-modes` ([L113](config/revitalise-grant-automation-build.yml#L113)) |
| 8 | agent | `agents/lead-agent.md` → *After every pipeline result* ([L401](agents/lead-agent.md#L401)) and the improvement-agent rows of the routing table | Every improvement-agent routing line carries one tag from row 6's list, taken from what `verify-improvement-log.py --check` printed on this run | IMP-0950, IMP-0936 | N/A — instruction change; row 6 reports a miss | N/A |
| 9 | agent | `agents/WORKFLOW.md` ([L389](agents/WORKFLOW.md#L389)) | "stamp `corrects`" on a fix → "stamp `fixes`"; `corrects` only when the earlier finding is wrong. Withdrawn wording retained | IMP-0932 | N/A — instruction change | N/A |
| 10 | agent | `agents/development-agent.md` ([L435](agents/development-agent.md#L435)) | Same change in *Fixing what a finding describes* | IMP-0932 | N/A — instruction change | N/A |
| 11 | agent | `agents/build-agent.md` → *Warnings Are Findings* ([L181](agents/build-agent.md#L181)) | One line: a repository-owned `scripts/verify-*.py` gate's WARNING, printed at its own step while exiting 0, is reconciled there and is not a Dev Summary §11 row (C-TECH-055, amended 2026-09-05) | IMP-0942 | N/A — instruction change | N/A |
| 12 | agent | `agents/pipeline-agent.md` → rule 2(b) ([L213](agents/pipeline-agent.md#L213)) | Name the flow-statecode pre-state read: `bash scripts/run-with-timeout.sh 90 pac env fetch --xmlFile <workflow statecode query>`, which needs no provisioning credential | IMP-0900 | N/A — instruction change | N/A |
| 13 | skill | `skills/how-to-log-an-improvement.md` (schema, [L188](skills/how-to-log-an-improvement.md#L188)) | The `fixes` field beside `corrects`, and one paragraph: a claim that something is absent is established by a search, and a proposal that re-scopes a gate carries the measured count and its command | IMP-0932, IMP-0935, IMP-0952 | N/A — skill text | N/A |
| 14 | skill | `skills/how-to-verify-a-platform-contract.md` ([L450](skills/how-to-verify-a-platform-contract.md#L450)) | Qualify "under Auto Mode there is no live route": the `pac env fetch` route was measured working on 2026-09-27, with what it proves and what it cannot read | IMP-0928 | N/A — skill text | N/A |
| 15 | skill | `skills/how-to-intake-external-documents.md` → *Work-Item Ingestion Checklist* ([L221](skills/how-to-intake-external-documents.md#L221)) and *Review Feedback Intake Checklist* | `acceptance` is built from the whole row: a later status column on the same row supersedes the ask, and a negatively phrased ask is settled by the row's resolution column. Every `wbs:`/`CO-` reference resolves against `contract/wbs.json` and `contract/change-orders/` before the plan is presented | IMP-0918, IMP-0919, IMP-0920 | N/A — skill text | N/A |
| 16 | skill | `skills/how-to-write-requirements.md` ([L117](skills/how-to-write-requirements.md#L117)) | Extend the content-category trap: every row of a reference artefact resolves to a form question, a payload key and a column; a row that resolves to no column is a missing source | IMP-0897 | N/A — skill text | N/A |
| 17 | knowledge | `knowledge/technology/power-automate.md` → *Sensitive Data Flows* ([L310](knowledge/technology/power-automate.md#L310)) | Two subsections. *Run history is a log*: per-type `secureData` support, Compose inputs-only, no propagation through a Compose, with the Microsoft citation. *Guards and fallbacks are tested with the input that triggers them*: the five cluster-A cases | IMP-0894, IMP-0921, IMP-0926, IMP-0927, IMP-0930, IMP-0945, IMP-0949 | N/A — reference text | N/A |
| 18 | knowledge | `knowledge/technology/coding-standards.md` (Pester, beside [L95](knowledge/technology/coding-standards.md#L95)) | The suite runner sets StrictMode: no `<word>` in a test title, optional XML children via `SelectSingleNode`, and a changed test file runs through `src/tests/Invoke-Tests.ps1` | IMP-0924, IMP-0939 | N/A — reference text | N/A |
| 19 | knowledge | `knowledge/technology/dataverse.md` → retype section ([L327](knowledge/technology/dataverse.md#L327)) | Publish between the transitional import and the delete; a multiline cell needs `auto="true"`; the transitional package cannot pass `C-TECH-077`, so it is packed and imported directly; the 8,060-byte row budget for String widening, and Memo for open text. After the 2026-09-27 review's change 3 | IMP-0933, IMP-0938, IMP-0940 | N/A — reference text | N/A |
| 20 | knowledge | `knowledge/technology/testing-tools.md` → *Verifying live Dataverse state* ([L148](knowledge/technology/testing-tools.md#L148)) | The FetchXML recipes: aggregate `countcolumn` proves a column exists, `fieldpermission` rows prove securing, `workflow.clientdata` gives the live definition; EntityDefinitions is out of reach | IMP-0928 | N/A — reference text | N/A |
| 21 | knowledge | `knowledge/domain/business-rules.md` BR-A04 ([L18](knowledge/domain/business-rules.md#L18)) | The age band is the applicant's own answer ("Prefer not to say" kept); no date of birth is collected or derived; location from postcode at write time | IMP-0898 | N/A — reference text | N/A |
| 22 | knowledge | `knowledge/domain/data-entities.md` (after [L111](knowledge/domain/data-entities.md#L111)) | The reviewer's 2026-09-25 intake transfer rule, verbatim; and the securing rule for a new Art. 9 column: categorical answers under a `secured: exception`, free text secured with a redacted counterpart (SDD §7.1a) | IMP-0895, IMP-0899 | N/A — reference text | N/A |
| 23 | other | `config/revitalise-grant-automation-pipeline.yml` ([L721](config/revitalise-grant-automation-pipeline.yml#L721), [L740](config/revitalise-grant-automation-pipeline.yml#L740), [L1183](config/revitalise-grant-automation-pipeline.yml#L1183)) | Correct the stated cause of three DEV notes: `dev-settings.json` has existed since `5bdfbd7`; the blocker is its missing `intake` block and the missing `INTAKE_ENDPOINT_URL_DEV`. Re-dated, with discharge condition `grep -c '"intake"' provisioning/deploymentSettings/dev-settings.json` ≥ 1 | IMP-0947 | YES — `python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml` | N/A |

**Constraint budget:** 0 of 3 used. No constraint amendment either: widening `C-DOM-004`'s Verify By to name run history would name a check that does not exist, so it waits for decision 2.

### 3.1 Engine or client (skill §6)

Rows 1 and 2 are pure platform facts and go to the engine copy only; both instance scripts are wrappers. Rows 3–7 are unsplit duplicates, so each edits both copies in the same change and `verify-engine-instance-split.py` runs before closing. Rows 8–16 are engine files. Their text was checked for this client's literals, and none is needed: row 11 cites a constraint id, as those files already do. Rows 17–20 are instance knowledge. Rows 21–22 are client-specific and stay in `knowledge/domain/`.

### 3.2 Routed work — handed to other agents once this review lands

Re-measured at draft time; re-measured again at apply before anything is handed on.

| To | Item | From |
|---|---|---|
| architect-agent (next TAD revision) | Correct §3 L593 to `IsSecured=1` for the two helper columns; add §3.1 blocks for the two register tables; §12.4's mechanism column (DEV via `ensure-schema.ps1`, other environments by promotion, the RequiredLevel change by import) and its publish step; ADR-052's gate-interaction line ("the four Art. 9 columns"); ADR-051 item 7's value for the Compose; decide ADR-054's refresh path for the four guarded straight-through columns | IMP-0944, IMP-0862, IMP-0922, IMP-0940, IMP-0923, IMP-0921, IMP-0945 |
| development-agent | Replace the count literal in `ScoringInvariants.Tests.ps1` L636 with a comparison; add the `intake` block to `dev-settings.json`, the DEV trigger-auth step and smoke test, and `INTAKE_ENDPOINT_URL_DEV`; retire the IntakeContract 8,192 block once row 2 is green; re-verify the Solution Checker fix claim (Dev Summary L10323) against a fresh run | IMP-0925, IMP-0943, IMP-0947, IMP-0931, IMP-0948 |
| reviewer | Decision 2 above | IMP-0951 |

---

## 4. Retirements

> Retirement check performed: 87 live constraint rows (10 retired, derived by `grep -rh '^| ~~C-' constraints/`). None is made redundant by this review. It adds no constraint, and each script row adds a property to an existing gate rather than duplicating one. The one retirement candidate is not a constraint: the instance Pester block for the 8,192-character limit (`IntakeContract.Tests.ps1` L1416) becomes redundant once row 2 is green. It is routed to development-agent (§3.2), on condition that its known-bad case fails under row 2 first.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0934, IMP-0855, IMP-0320, IMP-0322

None of this batch's 50 is unprocessed. The four ids above are parked in, or deferred by, other documents and are cited here only as context (§0, cluster K).

**Processed but left open** — each gets `deferred_reason` and `revisit_when` at apply, because its defect was only visible at V3 or above and nobody in this session can re-run that observation (step 6's table):

| Finding | Level | Fix state | Revisit when |
|---|---|---|---|
| IMP-0926, IMP-0927, IMP-0930, IMP-0945, IMP-0892 | V5 | fixed in source (IMP-0945 awaits architect-agent) | the first authenticated submission from the website reaches DEV, and its run shows the caller admitted, blank answers left empty and no `InvalidTemplate` |
| IMP-0949 | V4 | fixed in source, build 20260928-1 | a DEV submission with an optional checkbox left unticked completes |
| IMP-0931 | V5 | fixed in source; row 2 adds the gate | an over-long answer submitted in DEV is stored cut, with its note |
| IMP-0893 | V4 | `RequiredLevel` None in source | staff save an intake-created applicant in DEV without entering a date of birth |
| IMP-0894, IMP-0921 | V5 / V4 | intake secured in source; knowledge in row 17 | a DEV intake run's history shows `Normalise_payload` and its consumers obscured, and decision 2 is made |
| IMP-0922, IMP-0933 | V3 | owed by architect-agent (IMP-0922); documented, not measured (IMP-0933) | the next DEV import carries the RequiredLevel change and it reads back |
| IMP-0943 | V4 | owed by development-agent | the trigger-auth setting is read back in the DEV designer after an import |
| IMP-0948 | V3 | the Dev Summary claim is unverified | a fresh Solution Checker run is parsed against the claim |
| IMP-0923, IMP-0925 | n/a | owed by architect-agent / development-agent | the routed change lands |
| IMP-0951 | V1 | reviewer decision | decision 2 is made |

**Closed on apply:** IMP-0862, IMP-0887, IMP-0895, IMP-0896, IMP-0897, IMP-0898, IMP-0899, IMP-0900, IMP-0901, IMP-0902, IMP-0916, IMP-0918, IMP-0919, IMP-0920, IMP-0924, IMP-0928, IMP-0932, IMP-0935, IMP-0936, IMP-0938, IMP-0939, IMP-0942, IMP-0944, IMP-0947, IMP-0950, IMP-0952 (`APPLIED`, each with an `evidence_grep` needle in the file its row changes). Also IMP-0940 (`APPLIED` with `reobserved` at V3: the reviewer ran the publish and then the deletes, which succeeded, 2026-09-27 22:30, [routing.log L1053](logs/routing.log#L1053)).

**Rejected on apply:** IMP-0891, IMP-0946, IMP-0953 (the refusal protocol worked, so no rule change follows); IMP-0929 (its pointers resolved at activation, and test-agent reading the whole digest is by design); IMP-0937 (a record that a design gap was closed, so no rule change follows; its `corrects` becomes `fixes` under row 5); IMP-0941 (disproved by IMP-0942).

---

## 6. Digest impact

| | Before this review | After apply |
|---|---|---|
| Log entries | 945 | 949 (this review appended IMP-0950..0953; applying adds none) |
| Distinct lessons | 936 | 940 |
| Recurring classes (x≥2) | 72 | 72 (the four new entries join existing classes) |
| Digest lines | 609 | not measured — regeneration was refused (decision 1) |

**Apply-time obligation:** `verify-derived-counts.py` runs after the regeneration, and the size sentence in both copies of the generator is corrected if it drifted.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-28-improvement-review.md

Findings processed: 50 NEW  →  19 clusters
Regression check:   8 prior changes audited, 2 classes recurred
Proposed:           0 constraints (cap 3), 7 gates/scripts, 10 skill/knowledge edits,
                    5 agent-file edits, 0 retirements
Altitude calls:     9 generalised from instance to class, 4 left as notes
Digest:             will regenerate — 940 lessons, 72 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Record of what is done on approval

**Authorisation record, written before any change:** keyword `APPROVE IMPROVEMENTS`, verbatim; `authorised_by: Xander Lykopoulos`; `relayed_by: lead-agent`, quoted from the user's own turns in the lead session; received 2026-09-29. The artefact it authorises is the 23 changes in §3 and the dispositions in §5.

**Pre-apply state, measured read-only:** `verify-improvement-log.py --check` exit 0, 0 unread, 52 awaiting-approval (the 50 this review processed, plus IMP-0855 and IMP-0934, which are parked elsewhere). `generate-known-failure-modes.py --check` exit 0 (949 entries). The reviewer ran the stamp and the regeneration the harness had refused this agent. No entry has been appended since the draft, so no new `corrects` names a finding processed here.

Progress is recorded below, change by change, as each one lands.

| # | Change | Landed | Verified by | Entries moved |
|---|---|---|---|---|
| 4 | corrects rung narrowed; closed-correction remedy | 2026-09-29, both copies byte-identical | `--selftest` 107 fixtures OK; real log 9 corrects warnings → 1 (IMP-0298) | IMP-0916 APPLIED (NARROWED — see its `applied_by`) |
| 5 | `fixes` field (schema + second case) | 2026-09-29, same file | `--selftest` fixtures `fixes-*` OK | IMP-0937 REJECTED, its `corrects` moved to `fixes` |
| 9, 10, 13 | `fixes` instructed in WORKFLOW, development-agent, the logging skill; the search-and-count paragraph | 2026-09-29 | needles grepped, 1 each | IMP-0932, IMP-0935, IMP-0952 APPLIED |
| 6 | Routing check 5 (the draft said "check 4"; that number was already taken by the work-item check) | 2026-09-29, both copies byte-identical | `--selftest` OK. Default run 0 findings, because it is forward-only from 2026-09-29 like checks 3 and 4. With `--improvement-trigger-since 2026-09-26`: **9 untagged, not 2 as drafted** — 7 capability dispatches on 2026-09-26 evening, before any tag existed, plus the 2 cited. The draft's count only covered lines after the lane split | IMP-0887, IMP-0936, IMP-0950 APPLIED (IMP-0950 records the forward-only narrowing) |
| 8 | lead-agent trigger-tag rule | 2026-09-29 | needle grepped | (with row 6) |
| — | cluster E, the brief-pointer instance | — | — | IMP-0929 REJECTED |
| 11 | build-agent carve-out line | 2026-09-29 | needle grepped | IMP-0942 APPLIED; IMP-0941 REJECTED (disproved) |
| 12 | pipeline-agent pre-state command | 2026-09-29 | needle grepped | IMP-0900 APPLIED |
| 14, 20 | Auto Mode qualification; FetchXML recipes | 2026-09-29 | needles grepped | IMP-0928 APPLIED |
| 15 | intake checklists | 2026-09-29 | needles grepped | IMP-0918, IMP-0919, IMP-0920 APPLIED |
| 16 | requirements-skill reverse diff | 2026-09-29 | needle grepped | IMP-0897 APPLIED |
| — | already on disk | — | WORKFLOW.md "Which id" row grepped | IMP-0901 APPLIED |
| — | cluster Q | — | — | IMP-0891, IMP-0946, IMP-0953 REJECTED |
| 17 | power-automate.md: run history; guards and fallbacks | 2026-09-29 | needles grepped | lessons for the cluster A and K entries, which stay open (§5) |
| 18 | coding-standards.md: StrictMode | 2026-09-29 | needles grepped | IMP-0924, IMP-0939 APPLIED |
| 19 | dataverse.md: four retype additions, as a **separate block** after the section, not merged into it, so the parked 2026-09-27 review's rewrite of that section does not collide with it | 2026-09-29 | needles grepped | IMP-0938 APPLIED; IMP-0940 APPLIED with `reobserved` V3 (development-agent's step 5 read-back at 22:40, after the reviewer's publish-then-delete at 22:30; the finding's own timestamp is 22:38, so the 22:30 re-run could not be the record) |
| 21 | BR-A04 | 2026-09-29 | needle grepped | IMP-0898 APPLIED |
| 22 | data-entities.md: transfer rule verbatim from SDD A-08; §7.1a securing rule | 2026-09-29 | needles grepped; both quotations checked against the plan | IMP-0895 APPLIED; IMP-0899 APPLIED (NARROWED in placement: domain knowledge, not the engine agent file) |
| 1 | Flow gate check 10, zero-argument `createArray()` (engine copy; the instance script is a wrapper) | 2026-09-29 | `--selftest` OK (a bad and a good fixture). Real corpus: 0 findings. **Replayed on the intake flow shipped in build `revitalise-grant-automation-20260927-2`: 19 findings, 19 true** — the finding's own count. The draft's "10 at `HEAD~1`" was the committed file; that build was packed from a dirty tree | IMP-0949 DEFERRED (V4) |
| 2 | `PLATFORM_LIMITS["flow-expression"] = 8192` (engine copy) | 2026-09-29 | `--selftest` 6/6 (8,193 characters fails, 8,192 passes, prose and `@@` are skipped). Real corpus: 0 findings; the longest whole expression is 6,582 characters (the finding said 6,955, measured differently). An `@{…}` interpolation inside a longer string is not measured on its own, which is a residual | IMP-0931 DEFERRED (V5). The instance Pester block's retirement is routed |
| 3 | tad-coverage. The draft's letters **(c)(d)(e) became (g)(h) plus a narrowing of (b)**, because (c) through (f) were already taken. Four `config/gate-baselines.json` entries (owner architect-agent, expire 2026-10-13) | 2026-09-29, both copies byte-identical | `--selftest` 37 cases, 4 of them new. Real run before the baselines: **exactly the 4 predicted findings, 4 true**. After: exit 0, the 4 printed as suppressed. Trustee-visible count unchanged at 41 | IMP-0862 (NARROWED, see its `applied_by`), IMP-0896, IMP-0944 APPLIED |
| 7 | Capabilities ranking and pin; selftest E | 2026-09-29, both copies byte-identical | `--selftest` PASSED; 15 ids are cited across the two activation sections, 2 of them capabilities (IMP-0022, IMP-0213), and both now render. 9 of the 20 rendered capabilities changed | IMP-0902 APPLIED |
| 23 | Three DEV `blocked_on` notes corrected and re-dated, with a precise grep discharge | 2026-09-29 | The premise was executed, not read: the loader throws only on a missing file, `dev-settings.json` is tracked, and its three `entraGroupObjectId` values are `{{…}}` placeholders. `verify-pipeline-config.py` exit 0; YAML parses. **A fourth note (~L702, the SharePoint prerequisite) carries the same false clause; it was not in the approved rows, so it is routed, not edited** | IMP-0947 APPLIED |
| — | the deferrals in §5 | 2026-09-29 | each `deferred_reason` re-grepped before it was written | IMP-0892, 0893, 0894, 0921, 0922, 0923, 0925, 0926, 0927, 0930, 0931, 0933, 0943, 0945, 0948, 0949, 0951 deferred, each with a reviewer-accepted `deferred_reason` and a `revisit_when` |

**Decision received during the apply, and the one refused act.** Xander Lykopoulos, relayed by lead-agent, verbatim: *"Agreed with suggested approach for EX-004"*. That decides decision 2's first half: re-point EX-004 at `REV | Acceptance | Create Envelope` and `REV | Acceptance | Reminders & Escalation`, keeping its owner and its 2026-10-16 expiry. The second half, a personal-column list for a precise gate, is **still undecided**: the gate stays withheld and no change order is raised. **Writing the re-point into `contract/known-exceptions.json` was refused by the harness (*"[Modify Shared Resources]"*) and was not retried.** It is handed to the reviewer as a script that changes EX-004 only, records the decision inside the entry (`authorised_by`, `relayed_by`, verbatim, date), and keeps the withdrawn scope and reason as history. Simulated on a scratch copy: EX-004 re-pointed, owner and expiry kept, 17 changed lines. IMP-0951 records the half-decision and stays deferred until the other half is decided.

**Closing checks, all executed.** The queue gate exits 0 with 0 unread, 2 awaiting approval (IMP-0855 and IMP-0934, both parked elsewhere) and 1 warning (IMP-0298, whose newest review closed nothing). The digest was regenerated last and `--check` confirms it current: 949 entries and 934 distinct lessons, not the 940 §6 predicted, because the header counts NEW and APPLIED only and 6 of this batch were REJECTED. 72 recurring classes, 605 lines, and IMP-0022 now renders. The other checks:
- The size sentence was corrected in both generator copies (603 → 605). `verify-derived-counts.py` still reports 5 drifts, all in files owned by delivery agents, and all present before this review (§3.2 routed).
- `verify-engine-instance-split.py` exit 0 and `verify-build-config.py` exit 0.
- Every edited script's `--selftest` passes.
- The four Pester suites that invoke these scripts ran 242 passed, 0 failed, 1 skipped.
- `verify-wbs-chain.py` exits 2 on a stale `logs/state/wbs-state.json` (55 newer files, from other sessions' work). That file is pm-agent's to rebuild, so the chain was not re-run.

**Routed work, re-measured at apply:** every row in §3.2 still holds, re-grepped today. Two additions: the fourth stale pipeline note above, and a warning that `tad-coverage`'s two existing baselines (`status:error` and `status-unproduced:threshold-unset`) expire on **2026-09-30**. After that date the gate fails, so lead-agent should route both to their owner now. The 2026-09-27 review's applier must keep row 19's separate block in `dataverse.md` when it rewrites that section.

**Publishing.** Nothing is committed. `agents/`, `skills/` and the `.engine/scripts/` copies are edits inside the `.engine` submodule. Push that first, verify with `git -C .engine branch -r --contains HEAD`, then bump the pointer in the instance commit (`agents/improvement-agent.md` → *Committed is not published*).
