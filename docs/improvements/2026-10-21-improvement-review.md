# Improvement Review — 2026-10-21

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 71 `NEW` → 18 clusters (54 hollow-stamped entries IMP-1139..IMP-1193, 10 unread IMP-1194..IMP-1203, 2 logged by this review, and 5 reviewer-deferred entries whose return condition this window met)
**Trigger:** post-deploy batch — pipeline-agent's DEV PARTIAL of build `revitalise-grant-automation-20261021-3` ([pipeline.log L442](logs/pipeline.log#L442)) and the targeted DEV push of flow 1011, corrected to PARTIAL ([L447](logs/pipeline.log#L447)); reviewer request *"Start post deploy improvement review after the changes of the last 3 days."*
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** APPLIED 2026-10-22, all 17 rows, on your "Approve improvements" (2026-10-22 09:53, relayed by lead-agent). 53 entries closed, 1 rejected, 17 deferred; see the [applied record](#applied-record--2026-10-22). Draft revised 2026-10-22 with your answers to D-1, D-2 and D-3.
**WBS:** system work, `wbs:system`, not billable. The findings belong to wbs:2.4, 2.7, 3.2, 5.3–5.7, 6.6 and 8.6, as each entry records.

---

## Summary

All seventeen changes are applied (2026-10-22): six tool fixes, four knowledge updates, four agent-instruction edits, two skill edits and one comment in the special-category register. No new constraints and no retirements. The two that matter most: the review queue will stop counting a finding as "parked" when the review it names never mentions it (54 findings were hidden that way for a day), and a new listing shows every dated exception about to expire before a build is approved, which you agreed on 5 October and nobody drafted.

Your three answers of 22 October are folded in: AI Builder's own copy of the narrative gets a 30-day delete job in production only, set up with the other retention jobs (D-1, routed as R4); the redacted narrative stays off the special-category register and the register's comment is corrected (D-2, row 17); and your clean re-run of application 1086 closes four findings (D-3). Only the keyword is needed now.

**This review was meant to extend the 17 October review, and could not.** While it was being drafted, another session applied that review on your *"Approve Improvements for all open improvement reviews"* ([its applied record](docs/improvements/2026-10-17-improvement-review.md#L250)). An applied review cannot be extended, so this is a new one. That approval does not cover this draft.

## What has been built

All of it, on 2026-10-22; the [applied record](#applied-record--2026-10-22) names each landing line and the one narrowing.

1. **The queue stops trusting a review stamp the review does not back up** — [verify-improvement-log.py classify()](scripts/verify-improvement-log.py#L1580). Two batch drafts were paused after stamping 54 findings with the 17 October review's name and before writing them into it. The queue then reported them as "waiting for a keyword" and three critical, already-fixed findings as "reviewed and deferred". Measured today: 54 hollow stamps, 54 true, 0 false. The same row adds a note naming the open post-deploy review (two dispatches looked for it by date and missed it), and corrects a warning that predicts a build failure which does not happen.

2. **Expiring exceptions are listed before a build is approved** — new `scripts/report-expiring-registers.py`, plus one line for lead-agent. You approved this on 5 October ([D-3](docs/improvements/2026-10-05-improvement-review-2.md#L251)). It was recorded in a way the queue reads as settled, so four reviews passed it by, and a deferral expired and halted a full build on 20 October. Run against today's tree it lists 10 entries: 3 DEV placeholders that expired on 16 October, 3 flow-check exceptions that expired in September and now cover nothing, and 4 pipeline notes due on 30 October.

3. **Three deploy-time tools stop needing workarounds** — [verify-live-flow-definitions.py](scripts/verify-live-flow-definitions.py#L75) crashes on the one classic workflow in the solution, and four deploys copied the flows to a scratch folder to get past it. [log-line.py](scripts/log-line.py#L22) joins two log entries into one line, which broke the start/finish pairing of deploy writes; 22 such lines exist, all of them two entries joined. The flow checker gains a test that every "run after" name points at an action in the same block, which is what stopped Finalise Decisions from turning on.

4. **A targeted one-flow push comes from a build, not from source** — [pipeline-agent.md L92](agents/pipeline-agent.md#L92). Today's flow 1011 hotfix was packed from the working tree, beside an artifact that had passed the provenance check, so that check never saw the bytes imported. The bullet the 17 October review just added says "never by hand"; this settles the conflict its applied record flagged: build first (a change-scoped build is fine), then cut the one flow from that build.

5. **Four knowledge updates record what DEV taught this week** — the Flow-menu trigger's shape and its traps, AI Builder's billing per started 1,000 characters, the fact that AI Builder keeps every input in its own table whatever the flow hides, `sort()` needing one number type, and `pac power-fx run` writing table rows.

6. **Instruction edits for four agents and two skills** — each closes a mistake made this week by an agent that had the information. They cover re-checking the escalation tier on every hop, logging every dispatch so another session can see it, re-reading a review's status before writing to it, stating the order of rules, and lettering options in page order.

7. **The special-category register states the real reason the redacted narrative is not on it** — [special-category-register.yml L475](constraints/domain/special-category-register.yml#L475). Its comment still says nothing writes the column and a confidence threshold catches what the model misses. Both stopped being true: the flow writes it, and since 19 October the process owner reviews every scrubbed record. Your D-2 answer keeps the column off the register because trustees read it in the quarterly rounds; the comment now says that and records the one surname fragment found in DEV.

## Elements added

| Element | Where |
|---|---|
| Expiry listing with self-test | `scripts/report-expiring-registers.py` (new, this repository only) |
| Check 19: every runAfter key names a sibling | [verify-flow-definition-language.py](.engine/scripts/verify-flow-definition-language.py) (engine) |
| Flow-menu trigger subsection | [power-automate.md, after the Trigger section](knowledge/technology/power-automate.md#L290) |
| `pac power-fx run` subsection | [dataverse.md, before L450](knowledge/technology/dataverse.md#L450) |

## Elements changed

| Element | Change |
|---|---|
| [verify-improvement-log.py](scripts/verify-improvement-log.py#L1580) (both copies) | hollow stamp reads as unread; open-batch note; conditional warning text |
| [verify-live-flow-definitions.py](scripts/verify-live-flow-definitions.py#L75) | skips a workflow file with no flow JSON; accepts a `Z` time |
| [log-line.py](scripts/log-line.py#L22) (both copies) | refuses two entries in one call |
| [work_items.py](.engine/scripts/lib/work_items.py#L157) (engine) | Pester and pytest test names count; component labels checked |
| [power-automate.md AI Builder](knowledge/technology/power-automate.md#L403), [(l)](knowledge/technology/power-automate.md#L546), [Compose row](knowledge/technology/power-automate.md#L350) | three bullets; (m) added; one evaluator rule; one authoring rule |
| [architect-agent.md](agents/architect-agent.md#L198), [lead-agent.md](agents/lead-agent.md#L205), [pipeline-agent.md](agents/pipeline-agent.md#L92), [improvement-agent.md](agents/improvement-agent.md#L155) | one to four sentences each |
| [how-to-write-requirements.md](skills/how-to-write-requirements.md#L111), [how-to-report-to-the-reviewer.md](skills/how-to-report-to-the-reviewer.md#L195) | two traps; one rule-5 sentence |
| [special-category-register.yml L475–L490](constraints/domain/special-category-register.yml#L475) | two comment paragraphs replaced (no register row changes) |

---

## 0. Why this is a new review and not an amendment

The brief said to extend [the 17 October review](docs/improvements/2026-10-17-improvement-review.md), parked at its gate, and that the keyword had not been given. Both were true at dispatch (routing.log 20:59). Between 21:04 and 21:12 another session applied it, committed it (`e873736`) and pushed the engine half (`9c64a1f`). That apply wrote no routing line, so it showed up only as `scripts/scoped-repack.py` appearing between two reads of the tree. This review waited until the tree was quiet, claimed this filename with `allocate-review-number.py`, and wrote nothing before then. Logged as [IMP-1205, log L1201](logs/improvement-log.jsonl#L1201).

**The 54 stamps.** IMP-1139..IMP-1193 (except IMP-1143) carry `reviewed_in` naming the 17 October review, which never mentions them: two batch drafts, paused on 20 October 20:56 and 21 October 14:59, stamped them at draft time and wrote nothing ([IMP-1195, log L1191](logs/improvement-log.jsonl#L1191); [IMP-1203, log L1199](logs/improvement-log.jsonl#L1199)). This review processes all 54 and replaces each hollow stamp with this document, which names every one. The approval of 17 October did not dispose of them, as its own applied record says.

---

## 1. Regression check — did the last reviews' changes work?

The last three applied reviews: [2026-10-17](docs/improvements/2026-10-17-improvement-review.md#L250) (applied 21:10 today), [2026-10-20](docs/improvements/2026-10-20-improvement-review.md) (IMP-1143 only), and [2026-10-16-2](docs/improvements/2026-10-16-improvement-review-2.md#L384) (applied 17 October).

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| 10-17 rows 1–4: scoped-repack tool, partial-push bullet, fact (h), deploy-keyed deferral re-check | 2026-10-21 21:10 | `scoped-pack-hand-built`, `import-changes-flow-statecode`, `stale-deferral-uncaught-across-sessions` | Too soon to tell. Row 4 was used by this review (§2 cluster 18: 17 entries re-measured, 3 closed). Fact (h) gained two more "stayed Activated" readings today ([L434](logs/pipeline.log#L434), [L445](logs/pipeline.log#L445)) | No window; row 4 working |
| 10-20 rows 1–2: income rule and three rejection rules in the domain knowledge | 2026-10-20 | `stale-claim-contradicting-rechecked-source` | NO. IMP-1150 and IMP-1158 share the class and were logged before the apply | Working |
| 10-16-2 rows 1–3: C-TECH-030 wording, status-aware provenance check, lead runs it first | 2026-10-17 | `gate-scope-mismatch` | **YES, by a new route.** Lead ran provenance before both full deploys (routing 11:36, 14:27). The 15:13 hotfix imported a zip packed from source beside the checked artifact, so the gate passed for bytes that were not imported ([IMP-1204, log L1200](logs/improvement-log.jsonl#L1200)) | **The gate ran and was mis-scoped**: it checks the directory a dispatch names. Row 13 here closes the route; no gate change, because a scoped pack now records the artifact it was cut from |
| 10-16-2 row 5: superseding ADR lists reviewer decisions | 2026-10-17 | `approved-document-internally-inconsistent` | YES, different mechanism: IMP-1161 (one TAD paragraph too thin to build from), IMP-1163 (a reversed decision left in a diagram) | Not evidence against row 5; the class is 45 instances with no defence, and none is proposed (§2 cluster 12) |
| 10-16-2 row 7: census splits reviewed fixed-in-flight entries | 2026-10-17 | `gate-reassures-wrongly` | **YES, after a gate.** The split trusted the stamp, so three hollow-stamped critical findings read "already reviewed and reviewer-deferred" | **The gate ran and was mis-scoped**: it is row 1 here |
| 10-16-2 rows 4, 6, 8–12 | 2026-10-17 | various | NO | Working or no opportunity |

**Recurred after a prose fix:** none. **Recurred after a gate:** two (rows 1–3 and row 7 of 10-16-2), both mis-scoped rather than silent, both addressed here and logged (IMP-1204, IMP-1195). **Closure levels:** the 10-17 apply closed IMP-1102 (V3) with a V3 re-run; no closure in these reviews was made below its finding's `observable_at`.

---

## 2. Clusters and promotion decisions

```
CLUSTER: hollow-review-stamp  (x2: IMP-1195, IMP-1203; class gate-reassures-wrongly)
Altitude:   CLASS. One mechanism, seen from two sides: the stamp alone decides awaiting-approval,
            so an interrupted draft hides its entries from the unread list AND the batch trigger.
Ladder row: "A tool could catch it mechanically".
Becomes:    row 1(a): classify() treats a reviewed_in document that does not contain the entry's
            id as no stamp at all (state unread), and --check prints one WARNING per hollow stamp.
            Row 14: improvement-agent writes ids into the document before stamping them.
Retires:    nothing. check_self_stamps() (same-document appended_by + reviewed_in) stays; it is
            the HARD subset of this warning and costs nothing.
Cites:      IMP-1195, IMP-1203
Residual:   A document that mentions an id only in prose ("IMP-0033 is what an unprocessed queue
            looks like") satisfies the test. Measured today: 0 such cases among 1,128 stamps.
            The 25 closed and 7 deferred entries stamped to documents that do not name them stay
            silent by design (their status or deferred_reason discharges them).
```

```
CLUSTER: dispatch-brief-asserts-unverified-fact  (x3: IMP-1183, IMP-1196, IMP-1186)
Altitude:   INSTANCE x2 plus one rung slip. Two dispatches looked for the open post-deploy review
            by today's date and missed one three days old; one routing line said tier:standard for
            an agent with no lower tier; one resume kept a tier the reopen count had outgrown.
Ladder row: "A tool could catch it" (the first two) and "an agent had the information" (the third).
Becomes:    row 1(b): --check prints "open post-deploy batch review: <path>; extend it" for every
            review whose header says post-deploy and whose Status is not APPLIED. Row 12: lead's
            post-deploy step 5 names that note and says the tier comes from config/models.yml;
            rung 1 says to re-check escalation on every hop.
Retires:    nothing.
Cites:      IMP-1183, IMP-1196, IMP-1186
Residual:   A tier label typed by hand is still unchecked; verify-routing-reconciliation.py could
            compare it with config/models.yml, not proposed on two instances.
```

```
CLUSTER: gate-message-overstates-consequence  (x1: IMP-1150)
Altitude:   INSTANCE. The "corrected by, unprocessed" warning says the next build fails; it fails
            only when a C-TECH-061 rung fires. The sibling "fixed by" warning already says it
            correctly (verify-improvement-log.py, the fixes branch).
Becomes:    row 1(c): the corrects-branch text says "counts toward C-TECH-061's blocker and batch
            triggers" and names when a build fails, as the fixes branch does.
Cites:      IMP-1150
Residual:   none.
```

```
CLUSTER: concurrent-dispatches-one-document  (x2: IMP-1164, IMP-1205; plus IMP-1168, IMP-1169)
Altitude:   CLASS on the second instance. The property: two top-level sessions act on one shared
            file and neither can see the other, because a dispatch is visible only through
            routing.log and one session did not write there. IMP-1168 (another session's
            half-written flow failing a build) is the same property in the working tree; IMP-1169
            later found that flow committed and in scope, which narrows 1168's diagnosis but not
            its lesson.
Ladder row: "An agent had the information" - rung 5 already says to wait for a live dispatch.
Becomes:    row 12: rung 5 says "live" means an open ROUTED_TO from any session, and every
            dispatch, an improvement apply included, is logged before it is sent. Row 14:
            improvement-agent re-reads the target's Status and mtimes before its first write,
            and an apply writes "Status: APPLYING" first.
Retires:    nothing.
Cites:      IMP-1164, IMP-1168, IMP-1169, IMP-1205
Residual:   No lock. Two sessions that both follow the rule still race inside the same minute;
            the allocators cover ids and review names, nothing covers a shared prose document.
```

```
CLUSTER: live-definition-check-scope  (x4: IMP-1178, IMP-1181, IMP-1194, IMP-1155; gate-scope-mismatch)
Altitude:   INSTANCE, fourth occurrence of one defect. source_flows() reads JsonFileName from
            every *.data.xml; the business rule Rev-Payment-Issued has none, so Path('') is the
            folder and the read fails. Workarounds at pipeline.log L430 and L441 (11:46, 14:39).
Ladder row: "A tool could catch it" - the tool itself is the defect.
Becomes:    row 2: skip a data file with no JsonFileName (print "skipped: <name>, not a cloud
            flow"), and parse --imported-at as UTC-aware so a trailing Z works.
Retires:    nothing.
Cites:      IMP-1178, IMP-1181, IMP-1194, IMP-1155
Residual:   IMP-1155's main proposal, an --artifact mode comparing live with the deployed zip
            rather than with src/, is NOT drafted: one instance, and today's deploys matched 13/13.
            Deferred with a return condition. Boundary: the edit touches only source_flows() and
            argument parsing; the authenticated fetch is unchanged (agents/improvement-agent.md,
            per-operation boundary).
```

```
CLUSTER: log-marker-lost-to-tool-behaviour  (x1 finding, 22 measured lines: IMP-1165, part of IMP-1181)
Altitude:   CLASS by measurement. log-line.py joins stdin lines by design ("one action is one
            line"), so two entries in one heredoc become one line. Measured: 7 lines in
            pipeline.log and 15 in routing.log carry a second "[TAG] [feature]" header. All 22 are
            two or more entries joined (adjudicated one at a time). The pipeline ones break the
            WRITE BEGUN / WRITE ATTEMPTED pairing; L445-L446 today are two more.
Ladder row: "A tool could catch it mechanically".
Becomes:    row 3: refuse (exit 2, nothing written) stdin in which a line after the first begins
            with "[<TAG>] [" - a second entry. A wrapped single entry still joins.
Retires:    nothing.
Cites:      IMP-1165
Residual:   An entry deliberately typed on one line with two headers still passes; 0 found that
            were not accidental.
```

```
CLUSTER: dated-register-expiry-unseen  (x4: IMP-1046, IMP-1157, IMP-1154, IMP-1197; stale-deferral-uncaught-across-sessions)
Altitude:   APPROVED CHANGE, undrafted. D-3 (2026-10-05) said yes; IMP-1046 was then recorded with
            a deferred_reason, which the queue reads as settled, so reviews 10-07, 10-16, 10-16-2
            and 10-17 passed it (IMP-1157). TD-007 then expired and halted the 2026-10-20 build at
            its last step (IMP-1154). IMP-1197: three DEV placeholders expired on 16 October in a
            file no gate reads.
Ladder row: "A tool could catch it mechanically" + "an agent had the information" for the record.
Becomes:    row 4: scripts/report-expiring-registers.py lists every dated entry expiring within
            --days (default 14) or already past, with owner and clearing action, across
            config/flow-check7-exceptions.json, config/gate-baselines.json,
            contract/known-exceptions.json, contract/tad-deferrals.json, the three
            deploymentSettings *-settings.json _unresolved blocks (examples excluded), and the
            pipeline config's blocked_on_asserted + 14 days. Report only, exit 0. Row 12: lead
            runs it before relaying any "Approved for build". Row 14: an approved change left for
            a later review is recorded with approved_in + evidence_grep, never deferred_reason.
Retires:    nothing. verify-tad-coverage.py and verify-pipeline-config.py keep their HARD expiry
            checks; this is the advance warning D-3 asked for, not a second gate.
Cites:      IMP-1046, IMP-1157, IMP-1154, IMP-1197
Residual:   Measured today: 10 lines, all true (3 expired DEV placeholders, 3 check-7 exceptions
            expired 2026-09-30/10-06 whose flows were fixed and which now cover nothing, 4
            blocked_on notes due 2026-10-30); the 2026-08-19 PRD note is printed as accepted by its
            gate-baselines entry. A register added later is unseen until the file list is updated;
            the docstring says so. Not a build step: it is not a verify-* gate and its use is at
            approval time.
```

```
CLUSTER: push-from-what-artifact  (x3: IMP-1201, IMP-1204, IMP-1159)
Altitude:   CLASS. The property: what is imported must be an artifact build-agent produced, and
            newer than every approved fix for that solution. IMP-1159 deployed an artifact packed
            before an approved fix; IMP-1204 imported a pack built from source beside a checked
            artifact; IMP-1201 records the carrier route and that its stage word was wrong.
Ladder row: "An agent had the information" (C-TECH-030 exists).
Becomes:    row 13: the component-scoped bullet gains: a single-flow fix newer than the last
            artifact gets a change-scoped build first, then scoped-repack from it; never pack from
            source; PARTIAL when declared post_deploy steps are skipped. Row 12: before a deploy,
            lead compares the artifact's pack time with DEFECT-fix and CODE REVIEW APPROVED lines
            logged after it.
Retires:    nothing. This settles the conflict the 10-17 applied record flagged: the documented
            route is "cut from an artifact"; the carrier solution is not documented.
Cites:      IMP-1201, IMP-1204, IMP-1159
Residual:   verify-artifact-provenance still reads the directory, not the imported zip. With the
            pack cut by scoped-repack, its sidecar carries the artifact zip's hash, which is the
            link; a gate comparing them is not proposed until a scoped push has used the tool once.
```

```
CLUSTER: flow-menu-trigger-contract  (x5: IMP-1166, IMP-1167, IMP-1182, IMP-1184, IMP-1185)
Altitude:   KNOWLEDGE. Five findings on one trigger, in one evening: its names, how to read its
            definition, a wrong diagnosis from a header, the empty-schema trap, and the
            read-the-row-first pattern. IMP-1184 fixes IMP-1182; IMP-1185 fixes IMP-1184.
Ladder row: "One instance, general cause, a human needs to know it", five times over.
Becomes:    row 7: one subsection in power-automate.md (text in §3).
Cites:      IMP-1166, IMP-1167, IMP-1182, IMP-1184, IMP-1185
Residual:   The trigger's OUTPUT shape beyond the declared columns is unobserved; flow #7 reads
            the row with Get a row by ID, so nothing depends on it.
```

```
CLUSTER: ai-builder-behaviour  (x6: IMP-1139, IMP-1170, IMP-1189, IMP-1190, IMP-1191, IMP-1192)
Altitude:   KNOWLEDGE for four, ROUTED for two. Extractor spans stop inside a hyphenated surname
            (IMP-1139, critical, fixed in source) and the extractor answers one text differently
            between runs (IMP-1170). Extraction is billed per started 1,000 characters per call
            (IMP-1189). AI Builder stores every input in msdyn_aievent whatever secureData says
            (IMP-1190). Purchase routes (IMP-1191) and the real volume, about 1,000 a year against
            the TAD's 200 (IMP-1192), are design inputs for the TAD, not platform facts.
Becomes:    row 8: three AI Builder bullets. R3 to architect-agent: NFR-021 and A-R16 at ~1,000
            a year, the purchase routes, and msdyn_aievent as a store of special-category text.
            D-1 answered 2026-10-22: a 30-day recurring bulk delete of msdyn_aievent in PRD
            only, provisioned with the retention jobs; routed as R4.
Cites:      IMP-1139, IMP-1170, IMP-1189, IMP-1190, IMP-1191, IMP-1192
Residual:   D-3 answered: your DEV re-run of 1086 processed all five columns cleanly, so the span
            fix and the practice labelling held on the live model once. One clean run does not
            show the extractor is now stable (IMP-1170); row 8 says nothing may rest on it alone.
            Pricing facts are point-in-time and stay out of knowledge/.
```

```
CLUSTER: test-evaluator-weaker-than-platform  (x7: IMP-1153, IMP-1198, IMP-1199, IMP-1156, IMP-1176, IMP-1187, IMP-1179)
Altitude:   CLASS for the evaluator rule: three times a test evaluator accepted what the platform
            refuses and the tests passed over the defect (IMP-1136 deferred, IMP-1153 substring
            on '', IMP-1199 sort over mixed types). The rest are platform facts and one gate.
Ladder row: "Second instance -> generalise" for the evaluator; "a tool could catch it" for
            IMP-1179's runAfter rule.
Becomes:    row 9: (m) sort needs one type; (l) gains the empty-safe way to drop a separator; the
            Compose secureData row gains the save error and check 18; the designer-save section
            gains "every throw recorded here lands in both evaluators in the same change"; the
            hand-authoring section gains "one chain at the top level". Row 6: check 19, every
            runAfter key names a sibling in the same actions collection.
Retires:    nothing. FinaliseDecisions.Tests.ps1's per-flow runAfter test stays; check 19 is its
            solution-wide form.
Cites:      IMP-1153, IMP-1198, IMP-1199, IMP-1156, IMP-1176, IMP-1187, IMP-1179
Residual:   IMP-1176 is REJECTED: its premise ("no source gate looks for an argument-less
            createArray()") was executed and is false - the flow checker rejects it, and
            power-automate.md L394 already says so. Check 19 measured: 0 findings on the 13 current
            flows (correct: flow #7 was fixed), 2 findings, 2 true, on the 13 flows of build
            20261020-6, the one that would not turn on. The top-level shape rule (IMP-1187) is
            knowledge, not a gate: 8 of 13 flows have one or two top-level joins today.
```

```
CLUSTER: tad-instructions  (x6: IMP-1142, IMP-1144, IMP-1172, IMP-1161, IMP-1162, IMP-1163)
Altitude:   AGENT for three, NOTES for three. An off-by-default mode guarded across four
            revisions before anyone asked if it was wanted (IMP-1142); a per-environment DocuSign
            check for a service with one instance (IMP-1144); a gate list taken from build steps
            that missed a test-suite check (IMP-1172). IMP-1161 and IMP-1162 were settled by TAD
            rev 27 and flow #7's rebuild (verified in DEV, routing.log 11:53); IMP-1163's rule
            already exists (architect-agent.md, "When an ADR is RE-DECIDED", a whole-repository
            search, which covers the TAD's own diagrams) and was not run.
Becomes:    row 10: three sentences in architect-agent.md (text in §3).
Cites:      IMP-1142, IMP-1144, IMP-1172, IMP-1161, IMP-1162, IMP-1163
Residual:   approved-document-internally-inconsistent stays undefended at 45 instances. A gate
            would read prose for meaning, the shape measured at 48-100% false five times.
```

```
CLUSTER: rules-without-order  (x4: IMP-1140, IMP-1146, IMP-1171, IMP-1145)
Altitude:   CLASS. Three findings share one property: a list of rules read by a model or a
            person, with no stated order and with phrasings given as a closed list (the name-rule
            seed row twice, FR-095 once). IMP-1145 is the plan-side twin: an exposure requirement
            reasoned from a column flag, not from what the persona can open.
Ladder row: "An agent had the information" -> skill.
Becomes:    row 15: two traps in how-to-write-requirements.md (text in §3).
Cites:      IMP-1140, IMP-1146, IMP-1171, IMP-1145
Residual:   Whether the live model now follows the reordered rows is a DEV run, not a document.
```

```
CLUSTER: decision-relay-loses-its-referent  (x1: IMP-1174)
Altitude:   INSTANCE, cheap rule. Options written recommended-first under the later letter; the
            relay mapped "option B" to the wrong mechanism.
Becomes:    row 16: one sentence in rule 5 of the reporting skill; row 12: lead quotes the
            option's own sentence when relaying a letter.
Cites:      IMP-1174
Residual:   none.
```

```
CLUSTER: work-item-ledger-gaps  (x3: IMP-1152, IMP-1160, IMP-1175)
Altitude:   SCRIPT for two, DEFERRED for one. TEST_FILE_RE ("\.(test|spec)\.") matches no
            Pester or pytest file, so a flow's tests can never satisfy the import-document rule
            (IMP-1152). Component labels are free text at creation: 171 labels in the ledger, 1
            outside deploy / operation:<x> / script:<x>, and it is the instance IMP-1160 found.
            A supersede transition (IMP-1175) is a state-machine change that needs a design.
Ladder row: "A tool could catch it mechanically".
Becomes:    row 5: TEST_FILE_RE also accepts *.Tests.ps1 and test_*.py; add and link refuse a
            component outside the three forms.
Cites:      IMP-1152, IMP-1160, IMP-1175
Residual:   Both are engine changes, generic (no client literal). The pipeline-config half of
            IMP-1160 (the named operation exists) is not drafted: it needs the config path at
            creation time. IMP-1175 deferred.
```

```
CLUSTER: delivery-one-offs  (x11: IMP-1147, IMP-1148, IMP-1149, IMP-1151, IMP-1158, IMP-1173, IMP-1177, IMP-1180, IMP-1188, IMP-1193, IMP-1200)
Altitude:   NOTES, one knowledge line, three routed. Re-measured today:
            IMP-1147 both gates caught it (data point). IMP-1148 the four scoring rows now carry
            createOnly: true in all three files (V5, deferred). IMP-1149 -> row 10 knowledge line.
            IMP-1151 positional _unresolved paths; the lesson renders, no change. IMP-1158 the
            register comment is stale against ADR-078; D-2 answered, row 17. IMP-1173 re-grepped: the other
            type-29 readers either label the type or compare like with like; no second counter is
            wrong. IMP-1177 CO-010 now reads "| New task id | **8.6** |", so the gate passes; its
            fixture gap is a note. IMP-1180 the pipeline config no longer names "-Admins-DEV".
            IMP-1188 the audit gate working. IMP-1193 lead applied the lesson at 14:10 today.
            IMP-1200 evidence-map.json still names REVAcceptanceComplete, REVAnonymise and
            REVFinaliseDecisions (R2).
Becomes:    row 10 knowledge line (IMP-1149); row 17 register comment (IMP-1158).
Cites:      IMP-1147, IMP-1148, IMP-1149, IMP-1151, IMP-1158, IMP-1173, IMP-1177, IMP-1180, IMP-1188, IMP-1193, IMP-1200
Residual:   IMP-1197's three expired placeholders and the leading space in
            " REV-PP-GrantApplications-Finance-DEV" are R1.
```

```
CLUSTER: rewrite-keeps-punctuation  (x2: IMP-1141, IMP-1202)
Altitude:   DEFERRED. You added the keep-punctuation sentence in DEV and confirmed it on
            application 1086; the prompt document and its test now carry it. The shipped source
            (Other/Customizations.xml) still holds the older template until you re-export.
Cites:      IMP-1141, IMP-1202
Residual:   An ACC build before the re-export ships the old wording.
```

```
CLUSTER: deploy-keyed-deferrals-re-measured  (x4 closed of 17 re-measured: IMP-0670, IMP-0804, IMP-0969, IMP-0274)
Altitude:   BOOKKEEPING under the bullet the 10-17 review added today. 17 reviewer-deferred
            entries wait on an import or deploy; each was re-measured against today's lines:
            IMP-0670 met (test-agent re-evaluated C-TECH-058 after an import, 12:07, FAIL on 12
            OPEN rows - the evaluation is what the entry waited for). IMP-0804 met (both imports
            of builds containing Round Statistics completed, L423, L434). IMP-0969 met (WI-0129, a
            pbi, reached deployed:dev with declared components, work-items.jsonl 2026-10-20T20:34).
            IMP-0274 has no revisit_when and its own deferred_reason says the fix landed (V1):
            PATCH_CALLS reads -Method\s+(?:PATCH|PUT), selftest exit 0 today.
Cites:      IMP-0670, IMP-0804, IMP-0969, IMP-0274
Residual:   13 not met, one line each in §5. IMP-0971's condition met a counter-observation
            today: the 15:16 push skipped --pending and said SUCCESS (lead corrected it).
```

**Duplicate check (skill §3a):** the APPLIED entries of each cluster's class were read where the class has them. IMP-1137 (applied today) is the scoped-repack tool row 13 builds on, not a duplicate. No proposal redoes landed work.

**Premises grepped or executed at draft time (step 6):**
- IMP-1176 "no gate catches createArray()": **executed, false** (the checker failed a fixture with `@createArray()`).
- IMP-1195 "44 hollow stamps": re-measured 54 (10 more from the 21 October dispatch), 54 true.
- IMP-1183 "nothing prints the open batch": `grep "post-deploy batch" verify-improvement-log.py` → 0.
- IMP-1150 the warning text: present at [L2588](scripts/verify-improvement-log.py#L2588).
- IMP-1178 the crash: `source_flows()` at [L75](scripts/verify-live-flow-definitions.py#L75) reads `JsonFileName or ""`.
- IMP-1152: `TEST_FILE_RE = re.compile(r"\.(test|spec)\.")` at [L157](.engine/scripts/lib/work_items.py#L157).
- IMP-1160 selector: `components` field, 171 labels, 1 outside the vocabulary.
- IMP-1148, IMP-1177, IMP-1180: fixes found on disk (above). IMP-1200: defect still present.
- IMP-1197: three `_unresolved` entries with `expires: 2026-10-16`; Finance team name has a leading space.
- Check 19: 2 of 2 on the defective build, 0 on today's.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | [verify-improvement-log.py](scripts/verify-improvement-log.py#L1580), both copies | (a) `classify()`: a `reviewed_in` document that does not contain the entry's id counts as no stamp; the same test in the fixed-in-flight "already reviewed" note; one WARNING per hollow stamp naming the document. (b) NOTE: "open post-deploy batch review: `<path>` — extend it; do not open a second", for every review whose header carries `**Trigger:** post-deploy` and whose `**Status:**` does not start with APPLIED. (c) The corrects-branch warning ([L2588](scripts/verify-improvement-log.py#L2588)) says the entry "counts toward C-TECH-061's blocker and batch triggers" and that a build fails only when one fires. Selftest fixtures for (a) and (b) | IMP-1195, IMP-1203, IMP-1183, IMP-1196, IMP-1150 | YES — `--selftest`; corpus: (a) 54 hollow, 54 true before this draft's stamps, 0 after; (b) prints this review only | already wired (`improvement-log-check`) |
| 2 | script | [verify-live-flow-definitions.py](scripts/verify-live-flow-definitions.py#L75) | `source_flows()` skips a `*.data.xml` with no `JsonFileName` and prints `skipped: <Name> (no flow JSON; not a cloud flow)`; `--imported-at` parsed with `fromisoformat` after replacing a trailing `Z`, converted to naive UTC. Selftest fixture: a `.xaml.data.xml` beside two flows | IMP-1178, IMP-1181, IMP-1194, IMP-1155 | YES — `--selftest`; source half on the real `Workflows/`: 13 flows read, 1 skipped (no live call) | SUITE_GATE_EXEMPT already (deploy-time read; not changed) |
| 3 | script | [log-line.py](scripts/log-line.py#L22), both copies | Refuse (exit 2, nothing written) when a stdin line after the first starts with `[<TAG>] [`; the message says "one call per entry". Docstring cites IMP-1165 | IMP-1165 | YES — `--selftest` gains the two-entry heredoc case; corpus: 22 joined lines in logs/, 22 true | N/A, a tool, not a gate |
| 4 | script | `scripts/report-expiring-registers.py` (new, instance-only) | Lists every dated entry expiring within `--days` (default 14) or past, with file, id, owner, clearing action, across the seven files and the pipeline `blocked_on_asserted` notes named in cluster 7; skips entries carrying `closed`; prints a `blocked_on` note accepted by a `config/gate-baselines.json` entry as accepted. Exit 0 always | IMP-1046, IMP-1157, IMP-1154, IMP-1197 | YES — `--selftest`; corpus today: 10 lines, 10 true | N/A: not `verify-*`, no `--check`; used at approval time |
| 5 | script | [work_items.py](.engine/scripts/lib/work_items.py#L157), engine | `TEST_FILE_RE = re.compile(r"\.(test|spec)\.|\.Tests\.ps1$|^test_[^/]*\.py$")`; `add` and `link` refuse a component that is not `deploy`, `operation:<x>` or `script:<x>` | IMP-1152, IMP-1160 | YES — engine selftest gains both; corpus: 171 labels, the 1 refused is IMP-1160's | already wired (`work-items` step) |
| 6 | script | [verify-flow-definition-language.py](.engine/scripts/verify-flow-definition-language.py), engine | Check 19: in every actions collection (top level, scope, If/else, Switch case and default, loops), each `runAfter` key names a sibling in that collection | IMP-1179 | YES — `--selftest` with IMP-1179's shape; corpus: 0 of 13 today, 2 of 2 true on build 20261020-6 | already wired (`flow-definition-language`, HARD, [build config L710](config/revitalise-grant-automation-build.yml#L710)) |
| 7 | knowledge | [power-automate.md, after the Trigger section](knowledge/technology/power-automate.md#L290) | Text A below | IMP-1166, IMP-1167, IMP-1182, IMP-1184, IMP-1185 | YES — needle `### Dataverse "When a row is selected"` | N/A |
| 8 | knowledge | [power-automate.md AI Builder](knowledge/technology/power-automate.md#L403) | Text B below | IMP-1139, IMP-1170, IMP-1189, IMP-1190 | YES — needle `msdyn_datainfo` | N/A |
| 9 | knowledge | [power-automate.md (l), (m), Compose row, hand-authoring](knowledge/technology/power-automate.md#L546) | Text C below | IMP-1153, IMP-1198, IMP-1199, IMP-1156, IMP-1187 | YES — needle `(m) \`sort()\`` | N/A |
| 10 | knowledge | [dataverse.md, before L450](knowledge/technology/dataverse.md#L450) | Text D below | IMP-1149 | YES — needle `pac power-fx run --environment` | N/A |
| 11 | agent | [architect-agent.md L126, L198](agents/architect-agent.md#L198) | Text E below | IMP-1142, IMP-1144, IMP-1172 | N/A — instruction change | N/A |
| 12 | agent | [lead-agent.md rungs 1, 5, 7 and post-deploy step 5](agents/lead-agent.md#L205) | Text F below | IMP-1186, IMP-1164, IMP-1168, IMP-1159, IMP-1183, IMP-1196, IMP-1174, IMP-1046 | N/A — instruction change | N/A |
| 13 | agent | [pipeline-agent.md L92, L315](agents/pipeline-agent.md#L92) | Text G below | IMP-1201, IMP-1204, IMP-1181, IMP-1165 | N/A — instruction change | N/A |
| 14 | agent | [improvement-agent.md L155, L303, L400](agents/improvement-agent.md#L155) | Text H below | IMP-1195, IMP-1205, IMP-1157 | N/A — instruction change | N/A |
| 15 | skill | [how-to-write-requirements.md Common Traps](skills/how-to-write-requirements.md#L111) | Text I below | IMP-1140, IMP-1146, IMP-1171, IMP-1145 | N/A — instruction change | N/A |
| 16 | skill | [how-to-report-to-the-reviewer.md rule 5](skills/how-to-report-to-the-reviewer.md#L195) | Text J below | IMP-1174 | N/A — instruction change | N/A |
| 17 | other | [special-category-register.yml L475–L490](constraints/domain/special-category-register.yml#L475) | Text K below: the *WHAT WOULD REVERSE THIS* and *FLAGGED FOR REVIEWER CONFIRMATION* comment paragraphs replaced. No register row added or changed | IMP-1158 | YES — needle `CONFIRMED by the reviewer, 2026-10-22 (D-2` | N/A, a comment |

**Constraint budget:** 0 of 3 used.

**Where rows land:** rows 1 and 3 change both copies (instance `scripts/` and `.engine/scripts/`, byte-identical today); rows 5, 6, 11–16 are engine; rows 2, 4, 7–10 and 17 are this repository. Engine first: commit, push to the branch holding `HEAD~1`, check with `git -C .engine branch -r --contains HEAD`, then the pointer bump here.

**Client literals in engine text (skill §6):** rows 11–16 name no table, flow or environment of this client. Row 12's D-3 line names `scripts/report-expiring-registers.py`, an instance tool; the same residual the 10-17 review accepted for scoped-repack.

### The text of rows 7–17

**A (row 7).** New subsection `### Dataverse "When a row is selected" (Flow menu) trigger`, *added by improvement review 2026-10-21 (IMP-1166, IMP-1167, IMP-1182, IMP-1184, IMP-1185), DEV 2026-10-20/21*:
- The designer lists it as *Microsoft Dataverse — Manual*; its `operationId` is `RecordSelected` (type `Request`, kind `ApiConnection`, `parameters.entityName`, `splitOn @triggerBody()['rows']`). Microsoft Learn documents neither name.
- **Declare every column the flow reads under `rows.items.entity.properties`**, at least the table's id column, stored as the designer stores it (title, type string, format guid). An empty schema delivers an empty row from the Flow menu: the raw body was `{"entity":{"entity":{}}}`.
- **Make Get a row by ID the first action**, keyed on `triggerBody()?['entity']?['<id column>']`, and work from its output. A failed read is then the single missing-id and not-found failure.
- **An exported scratch flow stores only the columns its actions reference.** Make an action use every column you will need before exporting, or the export shows an empty schema and copying it copies the defect.
- A flow's stored definition can be read without the provisioning credential: `pac env fetch --xmlFile <file>` selecting `clientdata` from `workflow` by `workflowid` (no `top` attribute).
- **A run's `Origin` header is `make.powerautomate.com` even when it was started from a model-driven app's Flow menu**, so it says nothing about where a run started.

**B (row 8).** Three bullets at the end of *AI Builder*:
- **An extractor span is not a word boundary.** The prebuilt extractor returned *Holloway* for *Holloway-Reed*. A check that searches only the extractor's values cannot see the remainder: widen a name span over a directly joined hyphen or apostrophe fragment before labelling, and hold a label still joined to letters (IMP-1139). The extractor also answered the same text differently on two days (IMP-1170), so nothing that must always happen may rest on it alone.
- **Prebuilt entity extraction is billed per started 1,000 characters, per call** (20 credits, Microsoft Learn rate table). Measured in DEV: 460 of 626 credits on 2026-10-19/20 went to extraction, against 3–7 per prompt call. Read real per-call cost from `msdyn_aievent` (`msdyn_creditconsumed`, `msdyn_aimodelid`, `createdon`) before estimating, and batch short texts into one call (IMP-1189).
- **`secureData` does not stop AI Builder keeping the input.** Every prediction writes an `msdyn_aievent` row whose `msdyn_datainfo` holds the full input text, whatever the calling action secures. For personal data, establish that table's retention and its readers, and record it as a store (IMP-1190).

**C (row 9).**
- After (l): **(m) `sort()` over an object array needs one type in the sortBy property in every object.** An integer `2` beside a Float score fails at run time: InvalidTemplate, "sort expects the sortBy parameter … the same type for each object" (IMP-1198, DEV 2026-10-21). Write a literal that meets a Float as `float(2)`.
- Appended to (l): to drop a leading separator from a value that can be empty, use `join(skip(split(x, sep), 1), sep)`, never `substring()` (IMP-1153).
- Under the *Designer save and activation* heading: **Every throw recorded here lands in both test evaluators in the same change** — `src/tests/narrative/wdl_sim.py` and `src/tests/solutions/_harness/WdlExpression.psm1`. Three times an evaluator accepted what the platform refuses and the tests passed over the defect (IMP-1136, IMP-1153, IMP-1199).
- The Compose row of the secureData table gains: securing `outputs` imports, then the designer refuses to save with 0x80060467; check 18 fails the build on it (IMP-1156).
- In *Hand-Authoring Flow JSON*: **Give the top level one chain.** One action with an empty `runAfter`, every other action with exactly one `runAfter` key; read earlier outputs through the chain, never by adding a second predecessor. A success/failure fork is fine; a join draws crossing lines in the designer, and flow #7's layout was rejected for it although it ran (IMP-1187). 8 of 13 flows still have one or two top-level joins (2026-10-21): a rule for new authoring, not a gate.

**D (row 10).** New subsection `### pac power-fx run can write and read table rows`: `pac power-fx run --environment <url>` can `Patch` a Dataverse row by logical name and read it back (DEV `rev_setting`, 2026-10-19). On a locale with comma decimals, separate arguments with `;`. Use it for a one-row maker edit no script covers, then verify with `pac env fetch` (IMP-1149).

**E (row 11).**
- After the `grep` block at L126: **The source is the config's `steps:` and the test suites those steps run.** A loop check can live in a unit-test file that no `steps:` entry names, so grep `src/tests/` for checks over the artefact as well (`IMP-1172`).
- New item 4 under *An ADR states what it protects and what it costs*: **An ADR that introduces a mode that ships OFF and waits for a later decision asks, in the same gate, whether the mode is wanted at all.** Do not design guards around it until the answer is yes; one such mode was guarded across four revisions and removed on the reviewer's first look (`IMP-1142`).
- New item 5: **Before writing a per-environment check for an external service, state how many instances of it serve the Power Platform environments.** And an option the reviewer has not approved lives in one place, the ADR's open list, never in the test contract, gate table or risk register (`IMP-1144`).

**F (row 12).**
- Rung 1, appended: **Re-check `escalate_to_strategic_when` on every hop, a resume included.** A work item's reopen count can cross the threshold mid-chain, and only a fresh dispatch can raise the tier (`IMP-1186`).
- Rung 5, appended: **"Still live" means an open `ROUTED_TO` in `logs/routing.log` from any session**, so log every dispatch, an improvement apply included, before you send it: two top-level sessions work in this tree, and an unlogged dispatch is invisible to the other (`IMP-1164`, `IMP-1168`, `IMP-1205`). **Before a deploy, compare the artifact's pack time with every `DEFECT fix` or `CODE REVIEW APPROVED` line for the same solution logged after it**; a newer approved fix means rebuild first, or tell the reviewer the deploy re-ships the defect (`IMP-1159`). **Before relaying any "Approved for build", run `python3 scripts/report-expiring-registers.py` and put every line it prints in front of the reviewer** (reviewer decision D-3, 2026-10-05; `IMP-1046`).
- Rung 7, appended: **A one-letter answer is relayed with the option's own sentence quoted beside it** (`IMP-1174`).
- Post-deploy step 5, appended: find the parked review from the census NOTE that names it, never by today's date, and write the tier from `config/models.yml` (`IMP-1183`, `IMP-1196`).

**G (row 13).**
- Appended to the component-scoped bullet at L92: **A reviewer-requested single-flow fix that is newer than the last artifact gets a change-scoped build first** (`run-build.py --changed-since last-green`), and the pack is cut from that artifact. Never pack a carrier from source: the provenance check reads the artifact directory, not the zip you import (`IMP-1204`). The stage word is `PARTIAL` whenever a declared `post_deploy` step is skipped (`IMP-1201`).
- After the Code App marker form at L315: nothing may sit between the folder and the closing parenthesis; put an app id after the dash (`IMP-1181`). **One `log-line.py` call per marker**: two entries in one heredoc became one line seven times in `pipeline.log` (`IMP-1165`).

**H (row 14).**
- Step 6, after the stamp paragraph (L155): **Write each id into the document (a `Cites:` line or a change-table row) before you stamp it.** A stamp whose document does not yet name the entry is hollow, and an interruption leaves it hollow (`IMP-1195`: 54 entries for a day).
- *Amending a draft* (L303), new first paragraph: **Immediately before your first write, re-read the target review's `Status` line and the mtimes of the log and the review.** An apply can start in another session after you were dispatched; if it has, wait for it to finish and claim the next review. An apply writes `**Status:** APPLYING <time>` before its first change (`IMP-1205`).
- Step 8, after "Where you cannot make that observation" (L400): **An approved change left for a later review is recorded with `approved_in` and an `evidence_grep` naming text the change will put in its target, never as a `deferred_reason`.** The first reads as approved-not-applied and fails until the work lands; the second reads as settled forever (`IMP-1157`).

**I (row 15).** Two bullets in *Common Traps to Avoid*:
- **Rules without an order.** When a requirement or a prompt row carries more than one rule, state the order they apply in, and give phrasings as examples ("this includes …"), never as a closed list. After adding an exception to a requirement, re-read its other sentences for the case the exception now contradicts (IMP-1140, IMP-1146, IMP-1171).
- **An exposure requirement grounded in a flag.** Before writing "never shown to persona X", list what X can open — shared apps, portal screens and their queries — and cite them. An unsecured column that no one in that role can reach is not an exposure (IMP-1145).

**J (row 16).** Appended to rule 5: **Options inside one decision are lettered in the order they appear**, with the recommendation named in words ("recommended: (a)"), never by placing the recommended option first under a later letter. A relayed one-letter answer was mapped to the wrong mechanism because the page order and the letters disagreed (`IMP-1174`).

**K (row 17).** Replaces the two paragraphs from `# WHAT WOULD REVERSE THIS:` to the end of `# FLAGGED FOR REVIEWER CONFIRMATION …` (L475–L490). *THE DECISION* paragraph above them stays.

```yaml
  # CONFIRMED by the reviewer, 2026-10-22 (D-2 of improvement review 2026-10-21, IMP-1158):
  # rev_narrativeredacted stays off this register. The redacted text is what trustees read
  # to review applications in the quarterly rounds, so `secured: required` would defeat it.
  # The control behind that is ADR-078: the process owner reviews every scrubbed record
  # before release, and nothing is released automatically (RedactionAutoRelease retired
  # 2026-10-19). REV | Narrative | Scrub Free-Text writes the column; it is no longer empty.
  #
  # The reversal condition has been exercised once. In DEV a fragment of a hyphenated
  # surname reached this column (IMP-1139); the span fix is in source and the process-owner
  # review is the control that would have held it back.
  #
  # WHAT WOULD REVERSE THIS NOW: a scrubbed record released without the process owner's
  # review, or an identifying fragment found in a released record. Then add the column here
  # as `secured: required` until a stronger control exists, and tell the reviewer.
```

---

## 4. Retirements

> Retirement check performed: 88 live constraint rows, 10 retired (derived with the anchored grep). Read against this batch: [C-TECH-030](constraints/technology/technology-constraints.md#L71) (rows 12–13 lean on it; it is the only build-to-deploy rule) and [C-TECH-061](constraints/technology/technology-constraints.md#L131) (row 1 changes what its census counts, not the rule). Neither is redundant. The three expired check-7 exceptions are data, not constraints; removing them is R1. None retired.

---

## 5. Findings left unprocessed

**Deferred:** IMP-1095, IMP-1098, IMP-0243, IMP-0597, IMP-0649, IMP-0866, IMP-0867, IMP-0879, IMP-0906, IMP-0922, IMP-0933, IMP-0943, IMP-0971, IMP-0986

| Finding | Why not processed | Re-measured against today's deploys |
|---|---|---|
| IMP-1095, IMP-1098 | reviewer-deferred; wait on your designer save of flow 1011 | not met: no save recorded after the 14:33 or 15:15 imports ([L447](logs/pipeline.log#L447): "V4 open-and-save outstanding") |
| IMP-0243, IMP-0649 | wait on a live security-profile query | not met: no query in today's lines |
| IMP-0597 | waits on you entering an applicant with an ethnic group | not met |
| IMP-0866, IMP-0867 | wait on an import carrying three applicant Quick View Forms | cannot be met by today's imports: build 20261021-3's zip holds no applicant quick-view form |
| IMP-0879, IMP-0906, IMP-0971 | wait on a deploy that runs `--pending` before its stage word | not met; the 15:16 push is a counter-observation (no `--pending`, SUCCESS corrected to PARTIAL) |
| IMP-0922, IMP-0933 | wait on a read-back of a RequiredLevel change | not met: no read-back recorded |
| IMP-0943 | waits on a designer read-back of trigger authentication | not met |
| IMP-0986 | waits on a deploy recording each app's items against its own push | not exercised: no app item carried today |

Excluded by state, per activation step 2: 279 other reviewer-deferred entries, none waiting on a deploy.

---

## 6. Digest impact

| | Before (dispatch) | After this draft | After apply (predicted) |
|---|---|---|---|
| Log entries | 1198 | 1201 (IMP-1203 by the 10-17 apply; IMP-1204, IMP-1205 here) | 1201 |
| Recurring classes (x≥2) | — | `concurrent-dispatches-one-document` x1 → x2 | unchanged |
| Lesson groups | — | 1179 (regenerated at draft time, 1201 entries) | about 1179 |
| Digest lines | 637 | 638 | about 640 |

`generate-known-failure-modes.py --check`: current. `verify-derived-counts.py`: 1 drift (the size sentence says 637, the digest is 638), SOFT; corrected in both copies at apply, when the digest is regenerated again.

---

## What is still open

**The rows take effect only on approval.** Rows 2, 3 and 6 meet their first real use at the next DEV deploy; rows 7–10 are read at the next authoring of a flow.

**Your D-3 answer closed four live-only findings, IMP-1139 among them.** The rest of §8's DEFER rows still wait on one run, one designer save or one re-export by you, or on routed work (IMP-1190 waits on R4).

**Routed work, re-measured today:**

| # | To | Work | Cites |
|---|---|---|---|
| R1 | development-agent | Resolve or re-date the three expired `_unresolved` entries in [dev-settings.json](provisioning/deploymentSettings/dev-settings.json) (the Graph lookup is yours); check the leading space in `" REV-PP-GrantApplications-Finance-DEV"` against live; remove the three expired check-7 exceptions whose flows were fixed; qualify line 10 of `docs/development/quick-view-form-formxml-reference.md` (form metadata, not row data) | IMP-1197, IMP-1149 |
| R2 | pm-agent | Rename the four [evidence-map.json](contract/evidence-map.json#L252) rules to the built flow names (REVAcceptanceCompletion, REVNarrativeScrubFreeText, REVPortalFinaliseDecisions) | IMP-1200 |
| R3 | architect-agent | NFR-021 and A-R16 at about 1,000 applications a year (your figure, 21 October); Copilot Credit purchase routes into A-R16 and the Azure-subscription inconsistency in §6.3 | IMP-1192, IMP-1191 |
| R4 | architect-agent, then development-agent | Your D-1 answer: design [A-R105](docs/architecture/revitalise-grant-automation-architecture.md#L6459) and settle [A-NS-45](docs/architecture/revitalise-grant-automation-architecture.md#L6743) as a 30-day recurring Dataverse bulk delete of `msdyn_aievent` (`OlderThanXDays`), **PRD only, none in DEV**, set up before go-live; name the table as a store in the DPIA and RoPA. Provision it as a `dataverse.bulkDeleteJobs` entry plus a jobKey branch in [ensure-bulk-delete-jobs.ps1](provisioning/dataverse/ensure-bulk-delete-jobs.ps1#L1), bundled with the retention jobs ([regulations.md L81](knowledge/domain/regulations.md#L81): 6 years paid, 12 months rejected, 6 months withdrawn or incomplete). Measured today: `prd-settings.json` holds four jobs (rejected, withdrawn/incomplete, orphaned applicants, error log); **the 6-year paid-grant job is not there**, although `rev_grant` is now in source; the TAD already flags it as outside `wbs:8.6` ([ADR-081 item 10](docs/architecture/revitalise-grant-automation-architecture.md#L6157)). Source for the route: Microsoft Learn, *AI Builder activity monitoring*; whether deleting the rows affects credit reporting is not stated by Microsoft and is unverified | IMP-1190 |

## What you need to decide

Nothing. The keyword was given and the review is applied. Your three answers of 22 October are recorded below, each with what it changed in this draft.

---

**D-1 — Should AI Builder's own copy of raw narrative text be deleted on a schedule before production?** *Answered 2026-10-22.*

**Problem** — AI Builder keeps the full input of every call, including the unscrubbed narrative sent to extraction, in its own Dataverse table, whatever the flow hides from run history.
**Your answer** — *"for DEV this is not necessary. It is test data anyway."* Then, on the proposal of a 30-day scheduled bulk delete in PRD set up before go-live: *"Yes, you can note that down. Bundle it with the other bulk delete jobs that have to be setup for the 6 year timeline for given applications and the i believe 1 year timeline for rejected ones?"* The schedule in [regulations.md L81](knowledge/domain/regulations.md#L81) confirms 6 years paid and 12 months rejected, plus 6 months withdrawn or incomplete.
**What it changed** — R4 routes the design and provisioning to architect-agent; IMP-1190 is deferred until that job exists in PRD (§8).
[IMP-1190, log L1186](logs/improvement-log.jsonl#L1186)

---

**D-2 — Should the redacted narrative column be listed in the special-category register?** *Answered 2026-10-22.*

**Problem** — The register leaves it out because, it says, nothing writes it and a confidence threshold catches what the model misses; today the flow writes it, every record goes to the process owner, and a surname fragment did reach it once in DEV.
**Your answer** — *"keep the columns of the register.. these redacted versions are for the trustees to review applications on the quarterly rounds."* Confirmed with you as: keep it off the register and correct the comment.
**What it changed** — row 17 (text K); IMP-1158 closes on it (§8).
[IMP-1158, log L1154](logs/improvement-log.jsonl#L1154)

---

**D-3 — Did your re-run of application 1086 after the 15:15 import process all five columns cleanly?** *Answered 2026-10-22.*

**Problem** — The 14:39 build failed one column at the sort step; the hotfix went in at 15:15, and the log did not say whether all five columns then ran.
**Your answer** — *"Yes, all 5 columns have been processed cleanly."*
**What it changed** — IMP-1139, IMP-1170, IMP-1198 and IMP-1199 move from DEFER to CLOSE with your re-run as the `reobserved` record (§8). "Cleanly" is read as covering the two specifics the return condition named (no "-Reed" fragment, GP practice labelled); say so if it does not.
[IMP-1198, log L1194](logs/improvement-log.jsonl#L1194)

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-10-21-improvement-review.md

Findings processed: 71 NEW  →  18 clusters
Regression check:   18 prior changes audited, 3 classes recurred
Proposed:           0 constraints (cap 3), 6 gates/scripts, 6 skill/knowledge edits,
                    4 agent-file edits, 1 other, 0 retirements
Altitude calls:     6 generalised from instance to class, 1 left as notes
Digest:             will regenerate — see §8 for the measured counts

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Planned dispositions

**Draft-time stamping is complete.** All 71 entries carry this document's name in `reviewed_in`. 8 were stamped by this review on 21 October; the other 63, refused then by the auto-mode classifier, were applied by lead-agent on 22 October on your *"Allow edits to improvement log."*, one edit per line, each matching once. `verify-improvement-log.py --check` re-run for this revision: 0 unread, 63 awaiting-approval, OK. The other 8 report in their own states: IMP-1139, IMP-1156 and IMP-1179 as fixed-in-flight blockers (3 of the gate's 5), and IMP-0274, IMP-0670, IMP-0804, IMP-0969 and IMP-1046 as reviewer-deferred. Every one of the 71 appears in the table below exactly once.

The applied record is written here **after** `APPROVE IMPROVEMENTS`, not before. Each disposition follows the entry's `observable_at`. "Note" closures use the needle `APPLIED 2026-10-2x | IMP-nnnn` in this document's applied record, as earlier reviews did.

| Disposition | Entries | Closure |
|---|---|---|
| CLOSE (V1 / n/a), on its row's needle | IMP-1158 (row 17, on D-2); IMP-1195, IMP-1203, IMP-1183, IMP-1196, IMP-1150 (row 1); IMP-1046, IMP-1154, IMP-1157, IMP-1197 (rows 4, 12, 14); IMP-1152, IMP-1160 (row 5); IMP-1185 (row 7); IMP-1149 (row 10); IMP-1142, IMP-1144, IMP-1172 (row 11); IMP-1186, IMP-1164, IMP-1168 (row 12); IMP-1201, IMP-1204 (row 13); IMP-1205 (row 14); IMP-1145, IMP-1146 (row 15); IMP-1174 (row 16); IMP-1166 (row 7) | `evidence_grep` on the text each row puts in its target |
| CLOSE as a note | IMP-1147, IMP-1151, IMP-1161, IMP-1162, IMP-1163, IMP-1169, IMP-1173, IMP-1177, IMP-1180, IMP-1188, IMP-1191, IMP-1192, IMP-1193 | applied-record needle; IMP-1191/1192 carry R3 |
| CLOSE (V1), fix already on disk | IMP-0274 | `scripts/verify-provisioning-step-convergence.py` · `(?:PATCH|PUT)|Invoke-RevPatch`; `deferred_reason` removed |
| CLOSE with `reobserved` | IMP-1179 (V3 → V5: you turned flow #7 on and it created a grant, routing.log 2026-10-21 11:53); IMP-1184, IMP-1182 (V3 → V5, the same Flow-menu run delivered the row); IMP-1187 (V4: "the right structure in designer", same line); IMP-1167 (V3: pipeline-agent read `workflow.clientdata` for 13 flows by `pac env fetch`, [L441](logs/pipeline.log#L441)); IMP-0670 (V3: test-agent, 2026-10-21 12:07); IMP-0804 (V3: imports at [L423](logs/pipeline.log#L423), [L434](logs/pipeline.log#L434); the log records no asyncoperation id, which its return condition asked to name — narrowed, the build and line are named instead); IMP-0969 (V3: WI-0129 deployed:dev, 2026-10-20T20:34); **IMP-1139, IMP-1170, IMP-1198, IMP-1199 (V5, on D-3: you re-ran application 1086 in DEV on flow 1011 as imported 2026-10-21 15:15, and answered 2026-10-22 09:52 "Yes, all 5 columns have been processed cleanly"; needles: row 8 for IMP-1139 and IMP-1170, row 9 for IMP-1198 and IMP-1199)** | five-key `reobserved` plus the row or applied-record needle |
| REJECT | IMP-1176 | premise executed and false: the flow checker already rejects `createArray()`, and power-automate.md L394 says so |
| DEFER, reviewer-authored, on D-1 | IMP-1190 | `deferred_reason`: D-1 answered 2026-10-22, a 30-day recurring bulk delete of `msdyn_aievent` in PRD only, routed as R4; the knowledge half lands with row 8. `revisit_when`: the job exists in PRD (read back by `ensure-bulk-delete-jobs.ps1 -Env prd`) and the DPIA/RoPA names `msdyn_aievent` as a store. `observable_at` is V5, so it cannot close on row 8's needle alone |
| DEFER, on your designer save | IMP-1156, IMP-1159 | IMP-1095's `revisit_when`, verbatim |
| DEFER, on the next DEV deploy | IMP-1178, IMP-1194 (default `Workflows/` read without a workaround); IMP-1165, IMP-1181 (no line carrying two entries, and code-app markers resolve) | `revisit_when` as written |
| DEFER, other | IMP-1140, IMP-1171 (your next DEV run of 1086 and 1088 keeps the writer's own name and "our daughter" as the rules say; re-measured 2026-10-22: your D-3 answer covers 1086's five columns, but no 1088 run is recorded and the answer does not speak to these two rules, so not met); IMP-1141, IMP-1202 (you re-export the rewrite prompt and `Other/Customizations.xml` carries "keep every punctuation mark exactly where it is"); IMP-1148 (a process-owner edit in ACC survives a deploy); IMP-1153 (a DEV run of the scoring flow with no rejection rule completes); IMP-1155 (a second false DIFFERS from source drift past a build); IMP-1175 (a design for a work-item supersede transition exists); IMP-1189 (the wbs:5.7 scoring run reads per-call credits after ADR-082); IMP-1200 (R2 lands) | `deferred_reason` + `revisit_when` |

Verification at draft time: see the closing lines of the gate output; the figures are re-measured after this document and the stamps were written.

---

## Amendment 2026-10-22 — your answers to D-1, D-2 and D-3

Folded in: D-1 (R4 added; R3 no longer carries `msdyn_aievent`; IMP-1190 deferred on R4), D-2 (row 17 and text K; IMP-1158 closes on it; the gate block gains "1 other"), D-3 (IMP-1139, IMP-1170, IMP-1198, IMP-1199 moved from DEFER to CLOSE with `reobserved`). Also corrected: two references to IMP-1149's change named row 11; it is row 10.

Re-measured for this revision: the log gate (0 unread, 63 awaiting-approval); `prd-settings.json`'s bulk-delete jobs (four, no paid-grant job); the register's line range (L475–L490); IMP-1140 and IMP-1171 against your D-3 answer (not met); R1 still open on disk (three `_unresolved` entries expiring 2026-10-16 in `dev-settings.json`, and the leading-space team name on 2 lines); R2 still open (4 evidence-map lines name the old flow names). Not re-measured: R1's live half (the Graph lookup and the real team name) and every other DEFER row's live condition, which need a credentialled session or you.

Remained at the time: the keyword. It arrived 2026-10-22 09:53, and the applied record below supersedes this line.

---

## Applied record — 2026-10-22

**Applied on your "Approve improvements" (Xander Lykopoulos, 2026-10-22 09:53, relayed by lead-agent after the D-1/D-2/D-3 revision parked).** Before the first write: `verify-improvement-log.py --check` re-run (0 unread, 63 awaiting-approval, no `corrects` warning against any entry here), the Status line and both mtimes re-read (no other session writing), and the Status set to APPLYING.

### What landed, row by row

| # | Landed at | Measured at apply |
|---|---|---|
| 1 | [backed_reviews()](scripts/verify-improvement-log.py#L873), [check_hollow_stamps()](scripts/verify-improvement-log.py#L886), [open_batch_reviews()](scripts/verify-improvement-log.py#L907), [corrects warning](scripts/verify-improvement-log.py#L2667); both copies byte-identical | selftest 112 fixtures OK (3 new). Hollow stamps: 0 on today's log; 48 on the committed log at `e873736`, all 48 naming the 10-17 review, 48 true (the draft's 54 was read from the working log mid-stamping). **Narrowed, see below** |
| 2 | [parse_imported_at()](scripts/verify-live-flow-definitions.py#L71), [source_flows()](scripts/verify-live-flow-definitions.py#L86) | selftest passes (2 new cases); real `Workflows/`: 13 flows read, 1 skipped (`Rev-Payment-Issued`). No live call made |
| 3 | [SECOND_ENTRY](scripts/log-line.py#L56); both copies byte-identical | selftest 9 fixtures OK; 22 joined lines in logs/ (7 pipeline, 15 routing), the shape the refusal now stops |
| 4 | [report-expiring-registers.py](scripts/report-expiring-registers.py#L1) (new, this repository only) | selftest passes; real run: 10 lines, 10 true (3 expired check-7 exceptions, 3 expired DEV placeholders, 4 pipeline notes due 2026-10-30) plus the PRD note printed as accepted |
| 5 | [TEST_FILE_RE, COMPONENT_LABEL_RE](.engine/scripts/lib/work_items.py#L160), refusal in `work-items.py` `cmd_write` | selftest OK (3 new checks); 171 labels in the ledger, 1 outside the forms (WI-0129's, the instance the finding named) |
| 6 | [_check_runafter_siblings()](.engine/scripts/verify-flow-definition-language.py#L284) | selftest 31 checks OK; source: 0 findings on 13 flows; build 20261020-6: 2 findings, 2 true (both in the Finalise Decisions failure Switch) |
| 7 | [power-automate.md L295](knowledge/technology/power-automate.md#L295) | text A verbatim |
| 8 | [power-automate.md L457](knowledge/technology/power-automate.md#L457) | text B verbatim |
| 9 | [(m) L600](knowledge/technology/power-automate.md#L600), [(l) appended](knowledge/technology/power-automate.md#L595), [evaluators L546](knowledge/technology/power-automate.md#L546), [one chain L526](knowledge/technology/power-automate.md#L526), Compose row of the secureData table | text C; the one-chain bullet gains one sentence pointing at check 19 |
| 10 | [dataverse.md L450](knowledge/technology/dataverse.md#L450) | text D verbatim |
| 11 | [architect-agent.md L132](agents/architect-agent.md#L132), [items 4–5 L220](agents/architect-agent.md#L220) | text E verbatim |
| 12 | [rung 1 L212](agents/lead-agent.md#L212), [rung 5 L290](agents/lead-agent.md#L290), [rung 7 L335](agents/lead-agent.md#L335), [post-deploy step 5 L499](agents/lead-agent.md#L499) | text F; the "Approved for build" line is its own paragraph |
| 13 | [pipeline-agent.md L97](agents/pipeline-agent.md#L97), [L322](agents/pipeline-agent.md#L322) | text G; `--changed-since` confirmed in `run-build.py --help` |
| 14 | [improvement-agent.md L164](agents/improvement-agent.md#L164), [L310](agents/improvement-agent.md#L310), [L414](agents/improvement-agent.md#L414) | text H; this apply followed the L310 rule before its first write |
| 15 | [how-to-write-requirements.md L147](skills/how-to-write-requirements.md#L147) | text I verbatim |
| 16 | [how-to-report-to-the-reviewer.md L225](skills/how-to-report-to-the-reviewer.md#L225) | text J verbatim |
| 17 | [special-category-register.yml L475](constraints/domain/special-category-register.yml#L475) | text K verbatim; YAML parses; `domain-invariants` gate exit 0 |

### Deviations, each named

- **Row 1(b) narrowed.** The literal test (Status does not start with APPLIED) named three open reviews on the real corpus; two were false: [2026-10-16](docs/improvements/2026-10-16-improvement-review.md) and [2026-10-16-2](docs/improvements/2026-10-16-improvement-review-2.md), whose Status keeps the struck-through `~~DRAFT~~` ahead of `**APPLIED**`. The test now drops struck-through text and emphasis first. 3 named, 1 true before; 1 named, 1 true after. A fixture with the struck-through form fails the old test.
- **IMP-1139 keeps its own fixed-in-flight needle** (the span-widening action in the flow source) instead of row 8's. Its `fixed_in_flight` stamp is validated against that needle, and replacing it would invalidate the stamp.
- **Engine comment for check 19 names no flow.** The draft's measurement note named the client's flow; the engine text says "one build".
- **Unrelated, not caused here:** `verify-work-items.py` fails on WI-0009, a source-lines needle no longer found in `CasePanels.tsx`. Row 5 does not touch source-lines resolution. Left for its owner.

### Closures with an applied-record needle

APPLIED 2026-10-22 | IMP-1147 — both gates caught it; a data point.
APPLIED 2026-10-22 | IMP-1151 — positional `_unresolved` paths; the lesson renders, no change.
APPLIED 2026-10-22 | IMP-1161 — settled by TAD rev 27 and flow #7's rebuild, verified in DEV (routing.log 2026-10-21 11:53).
APPLIED 2026-10-22 | IMP-1162 — same settlement as IMP-1161.
APPLIED 2026-10-22 | IMP-1163 — the rule exists in architect-agent.md ("When an ADR is RE-DECIDED") and was not run; no new text.
APPLIED 2026-10-22 | IMP-1169 — narrows IMP-1168's diagnosis; its lesson landed in row 12.
APPLIED 2026-10-22 | IMP-1173 — re-grepped: no second wrong counter of type 29.
APPLIED 2026-10-22 | IMP-1177 — CO-010 now names task 8.6 and the gate passes; the fixture gap is a note.
APPLIED 2026-10-22 | IMP-1180 — the pipeline config no longer names "-Admins-DEV".
APPLIED 2026-10-22 | IMP-1188 — the audit gate working as designed.
APPLIED 2026-10-22 | IMP-1191 — design input, carried by R3.
APPLIED 2026-10-22 | IMP-1192 — design input, carried by R3.
APPLIED 2026-10-22 | IMP-1193 — lead applied the lesson at 14:10 on 2026-10-21.
APPLIED 2026-10-22 | IMP-0670 — test-agent re-evaluated C-TECH-058 after an import (routing.log 2026-10-21 12:07); `reobserved` V3.
APPLIED 2026-10-22 | IMP-0804 — both imports of builds holding Round Statistics completed ([L423](logs/pipeline.log#L423), [L434](logs/pipeline.log#L434)). The entry already carried a V3 `reobserved` from 2026-09-20 naming the asyncoperation id, so that record stands and the draft's narrowing is not needed.
APPLIED 2026-10-22 | IMP-0969 — WI-0129 (a pbi) reached deployed:dev with declared components, 2026-10-20T20:34; `reobserved` V3.

### Logged by this apply

- [IMP-1206](logs/improvement-log.jsonl#L1202): row 1(b)'s draft-time measurement was stated, not executed, and the IMP-0804 plan was written without reading the entry's existing `reobserved`. Both were caught at apply and are named above.
- [IMP-1207](logs/improvement-log.jsonl#L1203): this apply ran `git stash` in the engine tree by mistake inside a diagnostic command, and restored it within a minute; nothing was lost.

Both are unread for the next review.

**Verification at apply.** Selftests: verify-improvement-log 112/112, verify-live-flow-definitions passed, log-line 9/9, report-expiring-registers 9/9, work-items OK, verify-flow-definition-language 31/31. Gates: `verify-improvement-log.py --check` OK (0 unread before the two new entries, 0 awaiting-approval, 0 warnings); `verify-review-document.py` OK for this document (the corpus run still fails on five errors in five older reviews, none touched here); `verify-derived-counts.py` OK after the size sentence went 637 → 638 in both copies; `generate-known-failure-modes.py --check` current; `generate-subagents.py --check` current; `verify-engine-instance-split.py` OK, the two duplicated scripts byte-identical; `verify-build-config.py` OK; `domain-invariants` OK. **Not verified:** rows 2, 3 and 6 against a live deploy (the next DEV deploy is their first real use), and nothing here re-ran a flow in DEV.
