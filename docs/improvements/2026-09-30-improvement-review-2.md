# Improvement Review — 2026-09-30 (2): post-deploy batch after builds 20260930-2 to 20260930-4

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 16 `NEW` → 13 clusters (12 unread — 6 at draft, 6 folded in by the amendment after build 20260930-4 — plus 3 logged by this review, and 1 reviewer-deferred entry whose approved return condition happened in this deploy)
**Trigger:** post-deploy batch
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** DRAFT, amended once (see *Amendment 1* at the end of §0). Parked at the gate, nothing applied. `reviewed_in` is stamped on all 16 entries.
**WBS:** system work, `wbs:system`. The flows and ledger items it touches belong to `wbs:4.2,4.3` and `wbs:6.8` (the amendment's findings come from WI-0052 and WI-0005, both `wbs:6.8`). No change here is billable.

---

## Summary

The DEV deploy of build 20260930-2 worked: the import, the Code App push and the new live flow re-read all ran. Every finding from it is small. The one that matters: **agents type log timestamps by hand, and today they typed times up to five and a half hours in the future** in three different logs. Yesterday's written reminder to use the clock did not reach a single one of the five agents involved. This review makes the tools stamp the time.

**Added since the draft (builds 20260930-3 and -4):** the Trustee Portal detail screen had to be rebuilt field by field from the Trustee Pack PDF, after you raised it a third time. Every earlier pass checked only the section order, and the written rule telling developers to open the document page by page was already in place for two of them. The amendment adds a method (write the PDF's rows into a test and compare the screen to it), a fix to how feedback-sheet rows become work items, and a small ledger fix.

**Waiting on you:** `APPROVE IMPROVEMENTS`, plus three decisions below. Two of the changes (rows 6 and 7) wait on the same condition as this morning's secure-data review: the other session's flow changes must be committed first.

## What this review proposes

1. **The finding log's id tool stamps each finding's time from the clock** ([append L111](scripts/allocate-improvement-id.py#L111)). Every future-dated finding today went through this tool, which writes whatever time it is given. It kept happening after the draft. Two findings stamped 14:40 and 14:41 sit in a file last written at 13:55, and a third stamped 16:10 arrived at 15:23. Lead-agent also logged its own future-dated line in the routing log. The work-item ledger's tool already stamps its own time ([L857](.engine/scripts/lib/work_items.py#L857)), and none of its lines is skewed.

2. **A small helper writes every plain log line, and it takes the time itself** (new `scripts/log-line.py`). Measured against file modification times: `build.log` holds three lines written before the times they carry ([L149–L151](logs/build.log#L149)), and `pipeline.log` two ([L248–L249](logs/pipeline.log#L248)). The helper reads the line from a quoted heredoc, so a backtick or `$` in a summary is never run as a command.

3. **The eight places that teach the log-line format name the helper** ([WORKFLOW L657](agents/WORKFLOW.md#L657), [lead L113](agents/lead-agent.md#L113), [build L423](agents/build-agent.md#L423), [pipeline L625](agents/pipeline-agent.md#L625), [pm L205](agents/pm-agent.md#L205), [commercial L167](agents/commercial-agent.md#L167), [acceptance L131](agents/acceptance-agent.md#L131), plus lead's inline form at [L430](agents/lead-agent.md#L430)). Today each shows only a `[YYYY-MM-DD HH:MM]` placeholder, which is what agents fill in by guessing. A mechanised rule is not finished until every file that teaches the old way names the command.

4. **Two reference lines stop claiming the time comes from the clock** ([logging skill L57](skills/how-to-log-an-improvement.md#L57), [testing-tools L164](knowledge/technology/testing-tools.md#L164)). The second says log lines are "taken from `date` when the line is written". That was measured false today, and it becomes true only with rows 1–3.

5. **Lead-agent's post-deploy check looks at the result it just received, not at all of history** ([lead L423](agents/lead-agent.md#L423)). Today it re-judges every stage line since 26 September against today's config. So it flags the 29 September 21:51 line for a step declared only this morning, and it will flag that line for ever. Adding the stage line's date as `--since` fixes both (measured: 0 findings on today's line).

6. **Finishing a work item requires naming what must be deployed for it** ([built check L549](.engine/scripts/lib/work_items.py#L549)). Today the ledger asks for this only at the deploy step. So WI-0052's deploy ran in full, and only then was its status change refused. Development-agent's own instructions already say to declare it before finishing ([step 4 L276](agents/development-agent.md#L276)); none of the 8 items finished so far did. Decision 1.

7. **Held behind the flow commit: the flow-check self-test stops depending on a defect that has now been fixed** ([wrapper self-test L61](scripts/verify-flow-definition-language.py#L61)). All three check-7 exceptions are cleared in source, so the self-test now fails for the wrong reason. Nothing runs it, so nobody saw. The fix empties the exceptions file, makes the self-test report a stale exception by name, and runs the self-test in the build for the first time.

8. **A screen built from a supplied document is tested against a written-out copy of that document, row by row** ([verify skill §12c L927](skills/how-to-verify-a-platform-contract.md#L927)). §12c already says "open the document and check it page by page". It was in place from 23 September. The next pass (committed 26 September) did open the PDF, and still compared only section order. The new sentence names the method that worked today: the PDF's rows typed into a test, and the screen compared to them.

9. **A work-item clause that points at a document names the document's path** ([ingestion checklist L238](skills/how-to-intake-external-documents.md#L238)). WI-0005 took the sheet's original ask word for word ("Mirror the current Trustee Pack's setup and wording") and named no file. That is what leaves nothing for a check to key on (decision 3). The checklist already says a later status column on the same row is the requirement in force ([L247](skills/how-to-intake-external-documents.md#L247)). That line arrived with review 2026-09-28, after the sheet's items were ingested on 27 September, and nobody has re-read them since. Measured: 21 of the 38 rows with a status comment still carry only the original ask. That re-read is routed to pm-agent.

10. **Resuming a parked work item stops counting as a reopen** ([fold L771](.engine/scripts/lib/work_items.py#L771)). Today the only way out of `deferred` is `reopen`, which adds one to the Reopens count. That count triggers the "reopened two or more times" escalation ([models L138](config/models.yml#L138)). Two items have already been resumed this way. At 15:15 the escalation was applied to WI-0008 on "Reopens 2", and one of the two was its resume ([routing L1132](logs/routing.log#L1132)).

### Elements added

| Element | What it is |
|---|---|
| `scripts/log-line.py` (and its engine copy) | Appends one line to a `logs/*.log` file, stamped from the clock under a lock. Refuses a line that already carries a stamp |
| A `BuildGates.Tests.ps1` test (row 7, held) | Runs the flow-definition gate's own self-test in the build's test step |
| A `work-items.py` self-test case (row 13) | Resuming a deferred item leaves its Reopens count unchanged |

### Elements changed

| Element | Change |
|---|---|
| [allocate-improvement-id.py](scripts/allocate-improvement-id.py#L111), both copies | `ts` is set from the clock inside the lock; a value given by the agent is replaced |
| 7 agent files and [WORKFLOW.md L657](agents/WORKFLOW.md#L657) | The log format block names the helper |
| [work_items.py L549](.engine/scripts/lib/work_items.py#L549) | `built` needs declared components, for events from the apply date on |
| [lead-agent.md L423](agents/lead-agent.md#L423) | The post-deploy check gets `--since <date of the stage line>` |
| [flow-check7-exceptions.json](config/flow-check7-exceptions.json#L1) (held) | Emptied; all three clearing actions are done in source |
| [improvement-agent.md L568](agents/improvement-agent.md#L568) | The verify-script count, 67 → 68, re-derived at apply |
| [verify skill §12c L927](skills/how-to-verify-a-platform-contract.md#L927) | One paragraph: the row-by-row transcription test for a screen specified by a supplied document |
| [ingestion checklist L238](skills/how-to-intake-external-documents.md#L238) | The `acceptance` row: a clause that points at a document names it by path |
| [work_items.py fold L771](.engine/scripts/lib/work_items.py#L771) | A `reopen` from `deferred` does not add to `reopens` |
| [work_items.py `built` branch L549](.engine/scripts/lib/work_items.py#L549) (only on decision 3) | A clause naming a `docs/Import/` document needs `source-lines` evidence in a test file that names that document |

## What is still open

**The flows now running in DEV exist in no commit.** The build manifest records 12 changed paths at pack time ([manifest](build/artifacts/revitalise-grant-automation-20260930-2/manifest.json)). The new live-flow check script is untracked, and it has already run in a deploy. Committing them is lead-agent's call. Two held changes here and six in this morning's review wait on it.

**The rebuilt Trustee Portal detail screen is in DEV too, and six of its files are in no commit either.** The layout module, its PDF transcription test, the phone-width browser test, its harness page and harness app, and the field map are all untracked. Build 20260930-4 recorded 33 changed paths at pack time ([manifest](build/artifacts/revitalise-grant-automation-20260930-4/manifest.json)). They belong in the same commit as the flows. Row 11 describes the transcription test in general terms, so it does not depend on that commit.

**Only you can say whether the rebuilt screen now matches the PDF.** WI-0005 is at deployed:dev after build 20260930-4. At 15:15 you called it "much better", and lead-agent asked you to confirm it is done. The finding stays open until the ledger records your confirmation or a reopen.

**The other label/value lists in the portal are not measured on a phone.** The shared list layout ([`.definitions` L563](src/code-apps/trustee-review-portal/src/styles/app.module.css#L563)) keeps the same fixed 140 px label column that pushed the new rows 8 px sideways at 320 px. It is used through [`Definitions` L135](src/code-apps/trustee-review-portal/src/components/Panel.tsx#L135) by five components and pages. That is delivery work, routed to development-agent below.

**The rewritten failure path in the intake, scoring and reminders flows is shipped but not described or tested.** The test report caught it before the deploy, and you approved the deploy knowing. The Dev Summary still says the check-7 exceptions are open ([L11244](docs/development/revitalise-grant-automation-dev-summary.md#L11244)). Only making a flow fail on purpose proves the new path works. That revision belongs to the session that wrote the change. It is routed below, and the finding stays open until the revision exists.

**The 29 September 21:51 "SUCCESS" should have read PARTIAL, and the log cannot be corrected.** That retry re-imported the solution and never pushed the Code App ([L241](logs/pipeline.log#L241)). Lead-agent never received that dispatch, so its check never ran. Today's push replaced the app, so nothing is wrong live now. The line stays in the log. Once row 5 lands, lead-agent's per-result check stops re-reporting it; the build's history audit still lists it, as a warning only.

**Your designer-save question from yesterday's review is still unanswered.** Nothing here depends on it.

**Parked elsewhere, not re-derived:** the governance-lane blocker in [review 2026-09-27](docs/improvements/2026-09-27-improvement-review.md), one entry in [review 2026-09-23-7](docs/improvements/2026-09-23-improvement-review-7.md), and the two secure-data entries held by [review 2026-09-30](docs/improvements/2026-09-30-improvement-review.md).

## What you need to decide

**1. Require the deploy list when a work item is finished, rather than when it is packaged?**

**Problem** — WI-0052 reached the deploy with nothing declared, so its status change was refused only after the live writes had run. Development-agent's instruction to declare first was skipped on all 8 items finished so far.
**Suggested fix** — Refuse `built` without declared components, from the apply date, so the refusal reaches development-agent in the same dispatch. The finding proposed refusing at `packaged`: that catches exactly this 1 case of 8, but it lands on build-agent, which does not own the declaration and would have to hand back.
**What happens if you don't** — The next Code App item can again deploy in full, then be refused, and cost one extra dispatch to link and re-record.
[built check L549](.engine/scripts/lib/work_items.py#L549)

---

**2. Keep the two earlier "post-deploy step skipped" findings open?**

**Problem** — They wait for a DEV dispatch that runs the post-deploy check before its stage line and whose status word matches. Today's dispatch did exactly that ([L249](logs/pipeline.log#L249)). The 21:51 retry the night before did neither.
**Suggested fix** — Keep both open, and close them on the next dispatch that passes the check. This review's new finding records the 21:51 miss and waits on the same condition.
**What happens if you don't** — If you close them on today's evidence, the record says the class is fixed. One of the two dispatches since the check was built skipped it.
[L241](logs/pipeline.log#L241)

---

**3. Should the ledger refuse `built` for an item whose acceptance names a supplied document, until a test file names that document too?**

**Problem** — The written rule to check a supplied document failed twice on WI-0005, and nothing mechanical checks that a screen was compared with its document.
**Suggested fix** — Yes: row 14 requires, from the apply day, `source-lines` evidence for that clause in a `*.test.*` or `*.spec.*` file whose line names the document; row 12 makes sure the path is in the clause.
**What happens if you don't** — The next screen built from a supplied document again depends on someone remembering the method, which is how WI-0005 reached three raises. The check is narrow either way: it applies to 1 of 52 items today, and it proves a test cites the document, not that the test's copy of it is right.
[ingestion checklist L238](skills/how-to-intake-external-documents.md#L238)

---

Measured, not assumed: the future timestamps come from `stat` modification times, not from any agent's statement. The deploy-list rule was measured over all 8 `built` transitions in the ledger. The post-deploy check was run in three forms. The npm audit was re-run (exit 0, one advisory, already triaged). The disposition was simulated on a copy of the log: `verify-improvement-log.py --check` exits 0, with 0 unread and none of this review's entries left awaiting approval, in both the held and the applied variant of rows 6–7. **Not verified:** none of the scripts in rows 1, 2, 6 and 8 is written yet. Whether a flow's rewritten failure path works was not observed, and cannot be without making the flow fail in DEV. **Amendment:** the decision-3 rule was measured over all 52 ledger items, and the feedback-sheet gap over its 38 rows that carry a status comment. The two new future stamps come from the log file's modification time. The disposition was simulated again for all 16 entries, in both variants of rows 6–7: exit 0, 0 unread, and only the other reviews' two entries left awaiting approval. **Not verified:** whether the rebuilt screen matches the PDF (that needs your eyes), and the portal's other label/value lists at 320 px. Rows 11–14 are not written yet.

---

## 0. Scope, and where this review departs from its findings

**In scope.** The six `unread` entries (IMP-0961, IMP-0964, IMP-0965, IMP-0967, IMP-0968, IMP-0969), plus three this review logged from its own measurements (IMP-0970, IMP-0971, IMP-0972). Also IMP-0954: it is reviewer-deferred, but its approved `revisit_when` names the next import running under a 600 s or longer wrapper, and [pipeline.log L244](logs/pipeline.log#L244) is that import (900 s wrapper, no client-side 124). A deferral whose return condition has happened is due, so it is closed here and not left for someone to notice. **Amendment 1 adds** the six entries that became unread after the draft (IMP-0973 to IMP-0978), from builds 20260930-3 (WI-0052) and 20260930-4 (WI-0005, WI-0008).

**Excluded, and why.** IMP-0934 (governance blocker) and IMP-0855 are awaiting approval in their own reviews. IMP-0963 and IMP-0966 are held by [review 2026-09-30](docs/improvements/2026-09-30-improvement-review.md), which the brief says not to reopen. IMP-0879 and IMP-0906 are reviewer-deferred; their return condition is now ambiguous rather than met (decision 2). IMP-0298's warning belongs to a review parked since 2026-08-28. *(Amendment)* IMP-0824 is reviewer-deferred: it is the same screen's 09-22 instance, and its approved return condition is a human comparing the screen with the PDF *and confirming the order matches*. Today's comparison found it did not, so the condition is not met and the entry is left as it is. It is due on the same verdict as IMP-0973. IMP-0979 was appended by a live development-agent (WI-0008) while this amendment was being written. It is outside this dispatch's six and is left unread for the next post-deploy batch.

**Overlap with review 2026-09-30, and how it is resolved.** None of its six held changes is re-proposed or contradicted here. Two rows here touch the same uncommitted files, so they take the same sequencing condition ([its §3 L181](docs/improvements/2026-09-30-improvement-review.md#L181)):
- Row 6 edits the same function its row 2 extends (`_extended_selftest`). The two edits do not compete: its row adds a check-11 proof, this one replaces the check-7 proof. Whichever lands second keeps both.
- Row 7 empties the check-7 exceptions. That is only safe once the flow files carrying the descent are committed. Those are the same uncommitted flow files it is waiting on.
IMP-0965 is the escalation that review logged from its own regression check and deferred to this batch. Rows 1–5 are that escalation.

**Departures from the findings' own proposals, each forced by a measurement:**
- **IMP-0969** proposed refusing `packaged`. Row 8 refuses `built` instead (decision 1). And it applies only from the apply date, because [verify-work-items.py](.engine/scripts/verify-work-items.py) replays the whole ledger through the same function: an undated rule would turn all 8 historical `built` events red.
- **IMP-0968** proposed a build-agent handoff change. Not adopted, for two reasons. Build-agent did not write the understatement: it came from the description of the other session's work that the reviewer was asked to include. And the defence that exists worked: test-agent diffed the artefact and surfaced the change before the deploy. The build manifest already records the dirty-path count.
- **IMP-0967** states that the wrapper self-test "is not a build step". Executed, not read: `verify-build-config.py` runs a step's `--selftest` only for a gate *not* registered in `BuildGates.Tests.ps1` ([L630–L642](scripts/verify-build-config.py#L630)), and `flow-definition-language` is registered by name. `verify-build-config.py` exits 0 while the wrapper self-test exits 1. The premise holds, and row 7's test block is what closes it.
- **IMP-0964**'s root cause says the script was written "in a separate session". [routing.log](logs/routing.log) shows it was written by this session's development-agent (06:48–06:52), and the build that halted was the *other* session's. It picked up the half-finished script from the shared working tree. The conclusion (the preflight caught it at step 1) is unchanged.
- **IMP-0973** says WI-0005's acceptance was "a one-line paraphrase". Re-measured against [the sheet](docs/Import/FeedbackDeployment_20-09-2026.xlsx): it is the "What Emily asked for" column of row 6, word for word. What was left out is the "Status after deployment" column of the same row, which already said the order must follow the PDF exactly. The checklist has required that column since review 2026-09-28, which came after this item was ingested, so row 12 adds only the missing half: name the document's path. It also says the item "moved to deployed:dev with no evidence". It carried source lines, a legacy manifest and a deploy record from the 25 September build ([L109](logs/work-items.jsonl#L109)), so every ledger rule was met. No rule consulted the reviewer's "Not done yet" in column 1. Of the 7 rows marked not done, WI-0005 is the only one the backfill moved past `ready`.
- **IMP-0973 and IMP-0975** propose two homes for one method (a new intake-skill step, and §12c). Adopted once, in §12c (row 11), plus the narrower ingestion fix the measurement supports (row 12). IMP-0975's proposal to cite the portal's own test as the worked example is not adopted. §12c is an engine file, which carries no client names (promotion skill §6), and the test is untracked.
- **IMP-0976**'s proposal, to extend the browser test to the portal's other lists, is delivery work. It is routed, not made a rule.
- **IMP-0977**'s "no deferred item had been resumed through the tool before" is false. WI-0045 was resumed the same way on 27 September ([L134](logs/work-items.jsonl#L134)), so this is the second instance. Of its two options, row 13 takes the narrower one: do not count a reopen from `deferred`. A new event type would change the ledger schema and every reader of it, for the same effect.

**Amendment 1 (2026-09-30, after build 20260930-4).** *Folded in:* IMP-0973 to IMP-0978, with `reviewed_in` stamped on all six. That adds clusters C10–C13 and extends C1 with IMP-0974 and two new measured future stamps. It adds rows 11–13, and row 14 on the new decision 3. It adds one regression row (§12c), dispositions for all six, four routed items, and a re-measurement that narrows row 8's cutoff. The gate block, header, summary, simulation and digest table were reconciled first. *Still to do:* nothing in this document. Everything waits on the keyword and the three decisions. Rows 6–7 and the WI-0005 files still wait on lead-agent's commit. *Not folded in:* IMP-0979, appended during this dispatch. It goes to the next batch.

---

## 1. Regression check — did the last review's changes work?

The last review applied is [2026-09-29](docs/improvements/2026-09-29-improvement-review.md), applied 06:35 today. [Review 2026-09-30](docs/improvements/2026-09-30-improvement-review.md) was approved later but applied only a digest line count; its six changes are held, so there is nothing of it to audit yet.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| 09-29 change 1: re-read a flow's live definition after an import | 2026-09-30 | `async-flow-postimport-plugin-fails-silently` | NO. Promoted by the reviewer to `verify-live-flow-definitions.py`, which ran in this deploy: 10 of 10 flows, 0 differences ([L247](logs/pipeline.log#L247)) | Working; now a script |
| 09-29 change 2: import takes 4–6 minutes, wrapper ≥ 600 s | 2026-09-30 | `client-timeout-misread-as-write-failure` | NO. 900 s wrapper, import 3 m 48 s, publish 36 s, no client-side timeout ([L244](logs/pipeline.log#L244)) | Working. IMP-0954 closes on it |
| 09-29 change 3: `pac` times are UTC; take log times from `date` | 2026-09-30 | `log-timestamp-not-taken-from-the-clock` | **YES, at least 10 times in 12 hours, by 5 agents across 3 logs** (§2, C1). **4 more since the draft**, across 2 logs (amendment) | **Wrong altitude.** A prose line nobody reads at the moment of writing. Escalated to the tools (rows 1–5) |
| 09-29 `fixes` field warning | 2026-09-29 | `two-recorded-lessons-contradict-each-other` | Exercised again: the gate warned "IMP-0961: fixed by IMP-0962, and no review has processed it" | Working. It put IMP-0961 here |
| 09-30 digest line-count correction | 2026-09-30 | `hand-maintained-count-drifts-from-source` | NO. Digest is still 606 lines after this review's three appends, and after the amendment | Working |
| *(amendment)* review 2026-09-22-4: verify skill §12c (open the supplied document, check it page by page) and a development-agent trigger row that loads it | 2026-09-23 | `no-assertion-on-shipped-content` | **YES.** The next pass on the same screen (Revision 14, committed 09-26) says it checked "against the PDF p.1 directly", and compared section order only. Raised again 09-30 (C10) | **Right idea, wrong instrument.** Opening the document was done; the check it produced was still section-level. Row 11 names the row-by-row test, and decision 3 offers the ledger check |

**Changes whose class recurred after a *prose* fix:** 09-29 change 3 → rows 1–5. *(Amendment)* 09-23 §12c → row 11, plus row 14 if decision 3 is yes. Not the last review applied, but it is the prior change this amendment's main finding tests, so it is audited.
**Changes whose class recurred after a *gate*:** none. Nearest case: IMP-0971 is a recurrence of a class after its gate was *built*. The gate is invoked by instruction, the dispatch that skipped it was never routed through lead-agent, and the build's history audit is warn-only by design. Recorded, not re-escalated (C7).
**Closure evidence against level:** no entry closed by the last review has recurred. IMP-0955 was closed at V2 on a re-run audit, and its successor IMP-0961 was a *new* advisory set, not a recurrence of the triaged one.

---

## 2. Clusters and promotion decisions

Instance counts are re-derived from `class_instance_of` and from the files, not from the findings' prose.

```
CLUSTER C1: log-timestamp-not-taken-from-the-clock  (x3 in scope: IMP-0965, IMP-0970, IMP-0974; class x4 with IMP-0960)
Altitude:   CLASS — the instance is "the improvement log's ts"; the property is "every timestamp in
            an append-only log is taken from the clock by the tool that appends it". Measured today
            in three logs: improvement log 5 entries (IMP-0962 07:10 and IMP-0963 12:00 and IMP-0964
            12:30, all appended before 06:55; IMP-0966 07:02 against 06:59; IMP-0969 10:25 against a
            file mtime of 10:17:54), build.log 3 lines (L149 12:35 and L150 13:10 and L151 09:40,
            file mtime 09:35:39), pipeline.log 2 lines (L248 10:27 and L249 10:40, mtime 10:19:42).
            Amendment, measured the same way: improvement log 2 more (IMP-0977 14:40 and IMP-0978
            14:41, both in a file whose mtime is 13:55:14, both through the allocator); routing.log
            1 (IMP-0974, lead-agent's own count: L1103 stamped 11:01 when `date` read 10:59).
            And once more during the amendment: IMP-0979 (not in scope) carries 16:10 in a file
            last written at 15:23:42.
            Strip this client's names and the statement still holds: ENGINE-level.
Ladder row: "a tool could catch it mechanically" + "recurrence after a prose fix → escalate"
Becomes:    row 1 (allocator stamps ts), row 2 (scripts/log-line.py), row 3 (eight format blocks name
            it), rows 4–5 (the two instructing lines swept, IMP-0492's rule)
Retires:    the clause "taken from `date` when the line is written" in testing-tools.md, struck
            through in place (row 5) — it is false today and is replaced by the tool
Cites:      IMP-0965, IMP-0970, IMP-0974 (routing.log is row 3's lead-agent blocks, L113 and L430)
Residual:   (1) a line appended by hand, bypassing both tools, is still unstamped. None of today's
            improvement-log instances did that (all five are in the allocator's id-first form), so no
            validator check is proposed. (2) A stamp later than the clock is not detected after the
            fact; an ordering check misses a consistent skew, as the 09-29 review noted. (3) The
            plain-log helper is an instruction target, not a forced path: an agent using its own
            editor to append still types the time. (4) Minute resolution, local time, as today.
```

```
CLUSTER C2: untriaged-tool-warning  (x1: IMP-0961, fixed by IMP-0962; class x20)
Altitude:   NOTE — no change. The HARD code-app-audit step and the Dev Summary rule worked: an
            in-range lockfile bump cleared both high advisories and the build passed.
Ladder row: none taken. Second npm-advisory instance in two days (IMP-0955), both handled correctly
            by the existing rule. An advisory-id gate would buy determinism, not lower cost (09-29 C4)
Becomes:    nothing. CLOSE on a V2 re-run of the audit (§5)
Retires:    nothing
Cites:      IMP-0961
Residual:   advisories are published daily; the next build can halt on one nobody has triaged. That
            is the rule working, and it costs one development-agent dispatch each time.
```

```
CLUSTER C3: suite-gate-is-not-a-step  (x1: IMP-0964)
Altitude:   NOTE — the preflight caught an unwired verify-*.py at step 1, the cheapest point.
            development-agent already has the instruction to run verify-build-config.py before it
            presents (development-agent.md step 8); the SUITE_GATE_EXEMPT entry now exists
            (verify-build-config.py L723). The build that halted belonged to another live session
            that packaged the shared working tree while the script was half-done — the concurrent-
            session class, x3 already, and not something a wiring rule can prevent
Ladder row: one instance; the gate is the defence and it fired
Becomes:    nothing. CLOSE (V1)
Retires:    nothing
Cites:      IMP-0964
Residual:   two live sessions sharing one working tree will keep seeing each other's unfinished work
```

```
CLUSTER C4: selftest-depends-on-live-defect  (x1: IMP-0967)
Altitude:   INSTANCE, mechanical. The wrapper's two real-corpus check-7 assertions can only pass
            while a check-7 defect exists; all three are cleared, so the self-test fails. The engine's
            synthetic fixtures already prove the exception mechanism (both PASS). What the wrapper
            uniquely proves is that each DECLARED exception still covers something, so a stale one is
            reported by name, and nothing is asserted when none is declared
Ladder row: "a tool could catch it mechanically" — and the self-test ran nowhere, so it rotted unseen
Becomes:    row 6 (wrapper self-test reshaped), row 7 (exceptions file emptied; a BuildGates test runs
            the wrapper self-test). HELD behind the flow commit (§0)
Retires:    the three check-7 exceptions, all cleared in source ("No check-7 exception was applied")
Cites:      IMP-0967
Residual:   check 7 itself proves a failure branch exists, never that it works (its own NOTE)
```

```
CLUSTER C5: handoff-understates-artifact-content  (x1: IMP-0968)
Altitude:   NOTE — the proposal is not adopted (§0). test-agent's diff review caught it before the
            deploy, the reviewer approved with it on the page, and the manifest records dirty paths
Ladder row: one instance; the existing defence worked
Becomes:    routed: a Dev Summary revision for the check-7 failure-path change in flows 1001, 1002 and
            1007, by the session that authored it. DEFER until it exists
Retires:    nothing
Cites:      IMP-0968
Residual:   the rewritten failure paths are untested at runtime (V4/V5)
```

```
CLUSTER C6: item-components-undeclared-at-deploy  (x1: IMP-0969)
Altitude:   INSTANCE, mechanical; lands at the transition owned by the agent whose instruction was
            skipped. Corpus: 8 built transitions, 8 without components at that moment (all true
            violations of development-agent step 4's order; 7 linked later in one batch on
            2026-09-27, WI-0052 only after its deploy); 8 packaged, 1 without (WI-0052)
Ladder row: "a tool could catch it mechanically" + "an agent had the information and still did the
            wrong thing" — the mechanical home wins
Becomes:    row 8. Dated from the apply day, because verify-work-items.py replays history through the
            same function
Retires:    nothing
Cites:      IMP-0969
Residual:   an item with genuinely nothing to deploy has no component label to declare; none exists
            in the ledger today (all 52 items are pbi, bug or epic, and every built one owes a push)
```

```
CLUSTER C7: pipeline-dispatch-stops-before-declared-post-deploy  (x1 in scope: IMP-0971; class x3)
Altitude:   NOTE — the gate exists (verify-post-deploy-completeness.py) and today's dispatch ran it.
            The miss was a narrow reviewer-directed retry, never routed through lead-agent
Ladder row: third instance, but after a gate; "did the gate run?" — no, and the dispatch that
            should have run it is visible only in pipeline.log. Not escalated to a constraint:
            the one mechanical backstop left, lead-agent's per-result check, is repaired by row 9
Becomes:    nothing new. DEFER, joined to IMP-0879 and IMP-0906 (decision 2)
Retires:    nothing
Cites:      IMP-0971
Residual:   a pipeline dispatch that lead-agent never receives escapes both checks
```

```
CLUSTER C8: gate-scope-mismatch  (x1 in scope: IMP-0972; class x26)
Altitude:   INSTANCE, one argument. Executed three forms: plain --audit → L241 with 2 operations, 1
            false; --as-of-git → 1, true; --since 2026-09-30 → 0 over today's 1 SUCCESS line. The
            --since form judges the new line against the config that dispatch actually ran under,
            which --as-of-git would not (today's flow-reread declaration is uncommitted)
Ladder row: "an agent had the information..." does not apply: the instruction itself carried the
            wrong window. Agent-file edit
Becomes:    row 9
Retires:    nothing
Cites:      IMP-0972
Residual:   --since is date-granular (measured), so two dispatches on one day are judged together
```

```
CLUSTER C9: client-timeout-misread-as-write-failure  (x1: IMP-0954)
Altitude:   NOTE — closure. The approved return condition happened (L244)
Becomes:    nothing. CLOSE with reobserved V3 from pipeline-agent's import
Cites:      IMP-0954
Residual:   the wrapper budget is still set by the agent, not by a config step
```

*Clusters C10–C13 were added by Amendment 1.*

```
CLUSTER C10: no-assertion-on-shipped-content — screen specified by a supplied document
            (x2 in scope: IMP-0973, IMP-0975 — one incident, WI-0005, logged by lead-agent and by
            development-agent; the same screen's 09-22 instance is IMP-0824, reviewer-deferred and
            not re-derived; class x35)
Altitude:   CLASS — the property is "a screen whose specification is a supplied document is
            verified against a row-by-row transcription of that document, never against its section
            headings". Strip the portal and the Trustee Pack and it still holds: ENGINE-level for
            the method (row 11); the ingestion half (row 12) is engine-level too, because the
            intake skill's feedback-sheet checklist is. Measured: 3 raises (09-07, 09-25, 09-30), 3
            passes (Revisions 13, 14, 15). The third transcribed the PDF's rows into a test fixture
            (PACK_PAGES_1_2) and a field map: 45 PDF rows, 26 of them missing from the screen and
            added, 8 gaps put to you as decisions (routing.log, 13:00)
Ladder row: "recurrence after a prose fix → escalate" — §12c (09-23) is that prose. The mechanical
            candidate was measured before it was proposed: keyed on an acceptance clause naming a
            docs/Import/ path, it applies to 1 of 52 ledger items and would have fired on 0 of the 3
            raises as the ledger stood, because the clause named no path until today's re-link. So
            it only works together with row 12, and it is offered as decision 3, not drafted as a
            row the keyword alone would approve
Becomes:    row 11 (§12c method), row 12 (ingestion checklist), row 14 (only on decision 3)
Retires:    nothing
Cites:      IMP-0973, IMP-0975
Residual:   (1) a transcription can itself be wrong or incomplete; only the reviewer comparing the
            screen with the PDF is V4, which is why IMP-0973 stays open. (2) Row 12 is prose and binds
            pm-agent at ingestion. The status-column rule it sits beside (L247, review 2026-09-28,
            IMP-0919) already covers WI-0005's omission but postdates its ingestion; the 21 items
            ingested before it and never re-read are routed, not fixed here. (3) Row 14 proves a test cites the document, not what it asserts
```

```
CLUSTER C11: no-assertion-on-shipped-content — layout measured only in a real browser  (x1: IMP-0976)
Altitude:   NOTE — the new Chromium spec caught an 8 px sideways scroll at 320 px before review, and
            the build ran it (code-app-visual-tests is HARD under C-TECH-078, and build 20260930-4 lists
            no step as not executed except `auth`). The defence worked. The config itself calls this
            V2 geometry evidence, never a substitute for a named human at V4
Ladder row: one instance; the gate is the defence and it fired. Its proposal (measure the remaining
            .definitions consumers at 320 px) is delivery test work, not a rule
Becomes:    routed to development-agent. DEFER until those consumers are measured
Retires:    nothing
Cites:      IMP-0976
Residual:   the shared .definitions grid (minmax(140px, max-content) 1fr) is unmeasured at 320 px in
            the five components and pages that use Definitions
```

```
CLUSTER C12: work-item-state-model-gap  (x1: IMP-0977; 2 instances in the ledger, WI-0045 and WI-0008)
Altitude:   INSTANCE, mechanical. The fold adds 1 to `reopens` on every reopen (L771), including the
            only legal exit from `deferred`; models.yml escalates on "reopened two or more times"
            (L138). 14 items are deferred today, so each resume would count as a rejection.
            Observed during the amendment: at 15:15 lead-agent applied that escalation to WI-0008
            on "Reopens 2", one of which was the 13:51 resume (routing L1132; no cost this time,
            the dispatch was already at the strategic tier)
Ladder row: "a tool could catch it mechanically" — one-line change in the fold, plus a self-test case
Becomes:    row 13
Retires:    nothing
Cites:      IMP-0977
Residual:   the Reopens column still mixes post-deploy rejections with pre-deploy code-review
            revisions (WI-0005's 13:38 reopen is one); separating those is a design question nobody
            has raised, and this review does not
```

```
CLUSTER C13: quoted-decision-names-secured-column  (x1: IMP-0978)
Altitude:   NOTE — the app's own secured-column scan failed on three comments that quoted the reviewer
            by the secured column's name, on the first run, and the quotes were redacted in the same
            dispatch (types.ts L200 carries the placeholder). The gate is right not to tell a quote
            from a use
Ladder row: one instance; the gate is the defence and it fired
Becomes:    nothing. CLOSE (V1)
Retires:    nothing
Cites:      IMP-0978
Residual:   none new; the lesson sits in the digest for the next quote
```

**Premises grepped at draft time.**
- IMP-0965: `allocate-improvement-id.py` has no clock stamp (the only `ts` in it is a fixture). `verify-improvement-log.py` compares `ts` only against other fields, never against the clock. Both confirmed. The two scripts are byte-identical engine/instance pairs (`cmp`).
- IMP-0969: the `packaged` branch checks only for a manifest ([L560](.engine/scripts/lib/work_items.py#L560)). Confirmed.
- IMP-0967: the self-test runs nowhere. Confirmed by execution (§0).
- IMP-0964: the exemption now exists ([L723](scripts/verify-build-config.py#L723)). `verify-build-config.py` exits 0.
- IMP-0961: the re-run audit exits 0.
- *(Amendment)* IMP-0975: §12c has no transcription method today; it says to open the document and check it page by page ([L927](skills/how-to-verify-a-platform-contract.md#L927)). Its proposed worked example, `applicationDetailLayout.test.ts`, exists and is untracked (`git status`: `??`).
- *(Amendment)* IMP-0973: the checklist's status-column rule already exists ([L247](skills/how-to-intake-external-documents.md#L247)); nothing in it asks a clause to name a document's path. All 51 items from that sheet carry exactly one acceptance clause.
- *(Amendment)* IMP-0976: the shared `.definitions` grid still has the 140 px label floor ([L563](src/code-apps/trustee-review-portal/src/styles/app.module.css#L563)), and the Chromium suite has two specs, neither covering it.
- *(Amendment)* IMP-0977: `reopen` is the only exit from `deferred`, the fold always adds 1 ([L771](.engine/scripts/lib/work_items.py#L771)), and the models trigger reads that count ([L138](config/models.yml#L138)). 2 items were resumed this way (WI-0045, WI-0008); 14 are deferred today.
- *(Amendment)* IMP-0978: the placeholder is in source ([types.ts L200](src/code-apps/trustee-review-portal/src/dataverse/types.ts#L200)).

**Duplicate check (skill §3a).** The `APPLIED` entries sharing each cluster's class were read for C1 (IMP-0960: knowledge line only; its mechanical candidate was named and not applied, so there is no duplicate) and C6 (none). C2's closest applied entry, IMP-0962, is the fix this review closes against. *(Amendment)* C10: the class's applied entries since 09-15 are IMP-0845 and IMP-0846 (provisioning tests), which do not overlap. The prior change on this subject is §12c, audited in §1. Also read: IMP-0920 (applied by review 2026-09-28), the same checklist paragraph row 12 extends; row 12 does not repeat it. C12 and C13: no other entry in either class.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | `scripts/allocate-improvement-id.py` **and** `.engine/scripts/allocate-improvement-id.py` | In `append()`, inside the lock, set `ts` to the local clock (`%Y-%m-%dT%H:%M`, the log's existing form), replacing any supplied value. If the supplied value differed by more than 5 minutes, print a NOTE naming both. Docstring line: "`ts` is stamped here, from the clock, inside the lock (IMP-0965)". Self-test: a supplied `2099-01-01T00:00` is replaced; a missing `ts` is filled | IMP-0965, IMP-0970 | YES — `python3 scripts/allocate-improvement-id.py --selftest` | Not a gate (not `verify-*`); no step needed. `verify-engine-instance-split.py` at apply |
| 2 | script | new `scripts/log-line.py` **and** `.engine/scripts/log-line.py` | `python3 scripts/log-line.py logs/<name>.log <<'EOF'` … `EOF`. Reads one line from stdin, joins line breaks, refuses a target outside `logs/` or not `*.log`, refuses text already starting with a `[YYYY-MM-DD` stamp (exit 2), prepends `[YYYY-MM-DD HH:MM] ` from the clock, appends under an exclusive lock, prints what it wrote. Docstring line: "stamps the line from the clock (IMP-0970)". Self-test: stamps; refuses a pre-stamped line; refuses a non-log path; keeps backticks and `$` literal | IMP-0970 | YES — `python3 scripts/log-line.py --selftest` | Not a gate; no step needed. Engine text grepped for client literals before commit |
| 3 | agent | the 8 format blocks: [WORKFLOW L657](agents/WORKFLOW.md#L657), [lead L113](agents/lead-agent.md#L113) and [L430](agents/lead-agent.md#L430), [build L423](agents/build-agent.md#L423), [pipeline L625](agents/pipeline-agent.md#L625), [pm L205](agents/pm-agent.md#L205), [commercial L167](agents/commercial-agent.md#L167), [acceptance L131](agents/acceptance-agent.md#L131) | Keep each format line (without the stamp) and show the command that writes it (row 2's heredoc form), plus one sentence: "The time is the tool's; never type it (IMP-0970)." | IMP-0970 | N/A — instruction change | N/A |
| 4 | skill | [how-to-log-an-improvement.md L57](skills/how-to-log-an-improvement.md#L57) | After the allocator command: "It stamps `ts` from the clock too; any value you write is replaced (IMP-0965)." | IMP-0965 | N/A — reference text | N/A |
| 5 | knowledge | [testing-tools.md L164](knowledge/technology/testing-tools.md#L164) | Strike through "taken from `date` when the line is written" and add: "stamped by the tool that appends them (`scripts/log-line.py`; the id allocator for the improvement log). Typed stamps were measured up to five and a half hours in the future on 2026-09-30 (IMP-0970)." | IMP-0970 | N/A — reference text | N/A |
| 6 | script | [scripts/verify-flow-definition-language.py `_extended_selftest`](scripts/verify-flow-definition-language.py#L61) (instance wrapper only) | No exception declared → print "no check-7 exception declared; the engine's synthetic fixtures prove the mechanism" and assert nothing real-corpus for check 7. Otherwise one assertion per declared exception that it still suppresses a real finding, failing as "exception <flow>/<scope> suppresses nothing — the defect it covered is cleared; remove the entry (IMP-0967)", plus the existing 2099 expiry assertion. **HELD** with row 7 (§0) | IMP-0967 | YES — `python3 scripts/verify-flow-definition-language.py --selftest` | already wired — HARD `flow-definition-language` ([build L648](config/revitalise-grant-automation-build.yml#L648)); its self-test newly run by row 7 |
| 7 | other | [config/flow-check7-exceptions.json](config/flow-check7-exceptions.json#L1) and `src/tests/build/BuildGates.Tests.ps1` | Exceptions file → `[]`. New `Describe`/`It` running `Invoke-Python 'verify-flow-definition-language.py' @('--selftest') \| Should -Be 0`, modelled on [L1355](src/tests/build/BuildGates.Tests.ps1#L1355). **HELD**: applies when the flow files carrying the check-7 descent are committed, and the plain gate then passes on the committed tree | IMP-0967 | YES — `pwsh -NoProfile -File src/tests/Invoke-Tests.ps1 -Path build` | runs in HARD `unit-tests` |
| 8 | script | [.engine/scripts/lib/work_items.py `built` branch](.engine/scripts/lib/work_items.py#L549) and `.engine/scripts/work-items.py` self-test | For `pbi`/`bug`, a `built` event dated on or after the apply date with no declared components is refused: `EVIDENCE: <id>: declare components before built — python3 scripts/work-items.py link <id> --components <label,…>`. The date is a module constant, as `REQUIRED_FROM` is elsewhere. Self-test: fixtures link before `built`; new case "built with no components refused"; an event dated before the cutoff still folds | IMP-0969 | YES — `python3 scripts/work-items.py --selftest` and `python3 scripts/verify-work-items.py --check` (0 new findings on the real ledger) | already wired — `work-items` step ([build L157](config/revitalise-grant-automation-build.yml#L157), `--warn-only`) |
| 9 | agent | [lead-agent.md L423](agents/lead-agent.md#L423) | Command becomes `… --audit --since <YYYY-MM-DD of the stage line> ; echo "exit=$?"`, plus one sentence: the step judges the result just received; history is the build's warn-only `post-deploy-completeness` step | IMP-0972, IMP-0971 | YES — the command as written exits 0 on today's line (measured) | N/A |
| 10 | agent | [improvement-agent.md L568](agents/improvement-agent.md#L568) | Verify-script count, re-derived at apply with `ls scripts/verify-*.py \| wc -l` (68 today, after development-agent's `verify-live-flow-definitions.py`) | — (registered claim, `verify-derived-counts.py`) | YES — `python3 scripts/verify-derived-counts.py` | N/A |
| 11 | skill | [skills/how-to-verify-a-platform-contract.md §12c](skills/how-to-verify-a-platform-contract.md#L927) (engine) | New paragraph after the name-resemblance tell: "Opening the document is not the check. Where it specifies a screen, transcribe its rows (section, sub-heading, label, in order) into a test fixture, build the screen from a typed row specification, and assert the two are equal; a section-level reorder passes a heading test by construction (IMP-0975). Record every row you cannot render as a gap for the reviewer, never as a silent omission." No client names (grepped before commit, skill §6) | IMP-0975, IMP-0973 | N/A — instruction change | N/A |
| 12 | skill | [skills/how-to-intake-external-documents.md `acceptance` row](skills/how-to-intake-external-documents.md#L238) (engine) | Append to the row's Rule cell: "Where the requirement in force points at a document ('as the PDF', 'the pack', 'the form'), the clause names it by path (IMP-0973)." | IMP-0973 | N/A — reference text; row 14 is its mechanical half | N/A |
| 13 | script | [.engine/scripts/lib/work_items.py fold](.engine/scripts/lib/work_items.py#L771) and `.engine/scripts/work-items.py` self-test | `reopen` leaves `reopens` unchanged when the item's state before it was `deferred`, with the comment "a reopen from deferred is a resume, not a rejection (IMP-0977)". Self-test: defer → reopen → Reopens 0; built → reopen → Reopens 1 | IMP-0977 | YES — `python3 scripts/work-items.py --selftest` and `python3 scripts/verify-work-items.py --check` (0 new findings; WI-0045 and WI-0008 each drop by 1 in the export) | already wired — `work-items` step ([build L157](config/revitalise-grant-automation-build.yml#L157), `--warn-only`) |
| 14 | script | [.engine/scripts/lib/work_items.py `built` branch](.engine/scripts/lib/work_items.py#L549) — **only if decision 3 is yes** | For `pbi`/`bug`, a `built` dated **after** the apply date: each clause whose text names a `docs/Import/` path needs a `source-lines` for that clause whose `file` matches `*.test.*` or `*.spec.*` and whose `contains` holds the document's file name, else `EVIDENCE: <id>: clause <n> names <doc>; built needs a test line that names it too`. A module date constant, as row 8. Self-test: refused without; passes with; pre-cutoff event folds | IMP-0973, IMP-0975 | YES — `python3 scripts/work-items.py --selftest`; `verify-work-items.py --check` 0 new findings (measured corpus: 1 of 52 items, WI-0005, whose last `built` at 13:52 today would fail if the cutoff included today — its test evidence names the fixture, not the PDF) | already wired — `work-items` step, `--warn-only` |

**Amendment re-measurement of row 8.** Since WI-0052, all 4 `built` events recorded today had components declared before them ([L149](logs/work-items.jsonl#L149), [L155](logs/work-items.jsonl#L155), [L159](logs/work-items.jsonl#L159), [L160](logs/work-items.jsonl#L160)). The one that had none, WI-0052 at 09:37 ([L143](logs/work-items.jsonl#L143)), is dated today. So row 8's "on or after the apply date" would report it if applied today, and its "0 new findings" verification would fail. At apply, row 8 takes the same **after the apply date** cutoff as row 14. That narrowing removes one named historical event the rule would wrongly report, and does not change what the rule enforces.

**Constraint budget:** 0 of 3 used.

**Publishing.** Rows 1, 2, 3, 4, 8 and 10 change the `.engine` submodule, and so do rows 11–14 from the amendment. It already carries one uncommitted change from review 2026-09-30 (the digest line count in `generate-known-failure-modes.py`). The order is: commit there, `git -C .engine push origin HEAD:main`, verify with `git -C .engine branch -r --contains HEAD`, then bump the pointer here. Rows 1 and 2 are script pairs: both copies, same change.

---

## 4. Retirements

> Retirement check performed: 87 live constraint rows, 10 retired (`grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l`, re-run at apply). None is made redundant: this review adds no constraint. Retired as text: the three check-7 exceptions (row 7, held), and the testing-tools.md clause about `date`, struck through in place (row 5). No gate is retired. *(Amendment)* Checked again for rows 11–14: none replaces an existing rule. Row 12 sits beside the 09-28 status-column rule and does not supersede it, and §12c's existing text stays, because opening the document is still the first step.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0934, IMP-0855, IMP-0963, IMP-0966, IMP-0879, IMP-0906, IMP-0298, IMP-0824

These are parked in other reviews or reviewer-deferred (§0), and are cited only as context. None of the `unread` entries at draft time is unprocessed.

**Dispositions, decided from each entry's `observable_at` (step 6's table):**

| Finding | Level | Disposition | Closure evidence |
|---|---|---|---|
| IMP-0961 | V2 | **CLOSE** → `APPLIED`, no system change; fixed by IMP-0962 | `reobserved` V2: improvement-agent re-ran `npm --prefix src/code-apps/trustee-review-portal audit --audit-level=high` at 2026-09-30 10:30. Exit 0, one advisory (GHSA-82fw-gwwq-j7x9), cited 4 times in the Dev Summary. Re-run at apply. `evidence_grep`: the Dev Summary revision heading ([L11725](docs/development/revitalise-grant-automation-dev-summary.md#L11725)) |
| IMP-0964 | V1 | **CLOSE** → `APPLIED`, no system change | `evidence_grep` on the exemption key ([L723](scripts/verify-build-config.py#L723)) |
| IMP-0965 | V1 | **CLOSE** → `APPLIED`, row 1 | `evidence_grep` on row 1's docstring line |
| IMP-0970 | V1 | **CLOSE** → `APPLIED`, rows 2–5 | `evidence_grep` on row 2's docstring line |
| IMP-0972 | V1 | **CLOSE** → `APPLIED`, row 9 | `evidence_grep` on `--audit --since <YYYY-MM-DD of the stage line>` |
| IMP-0954 | V3 | **CLOSE** → `APPLIED`, by 09-29 change 2 | `reobserved` V3: pipeline-agent, 2026-09-30 10:15, `pac solution import -Env dev` under a 900 s wrapper, no client-side 124 ([L244](logs/pipeline.log#L244)). `evidence_grep`: "wrapper budget of at least 600 seconds" ([build-and-deploy L185](knowledge/technology/build-and-deploy.md#L185)) |
| IMP-0967 | V3 | **CLOSE** if rows 6–7 apply, with `reobserved` from re-running `python3 scripts/verify-flow-definition-language.py --selftest` (exit 0). **Otherwise DEFER**, `revisit_when`: *the flow files carrying the check-7 descent are committed; then apply rows 6–7 and close* | — |
| IMP-0968 | V2 | **DEFER from the start.** The proposed build-agent change is not adopted; the gap it names is routed | `revisit_when`: *the Dev Summary carries a revision describing the check-7 failure-path change in flows 1001, 1002 and 1007* |
| IMP-0969 | V3 | **DEFER from the start.** Row 8 lands, but only a deploy re-observes it | `revisit_when`: *the next pbi or bug item reaches deployed:<env> after row 8 lands with no components refusal* |
| IMP-0971 | V3 | **DEFER from the start**, joined to IMP-0879 and IMP-0906 (decision 2) | `revisit_when`: *the next DEV dispatch that imports runs --pending before its stage line and its status word matches* |
| IMP-0974 | n/a | **CLOSE** → `APPLIED`, rows 2–3 | `evidence_grep` on row 2's docstring line, as IMP-0970 |
| IMP-0975 | V1 | **CLOSE** → `APPLIED`, row 11 | `evidence_grep` on "a section-level reorder passes a heading test by construction (IMP-0975)" — kept on one line of §12c, `grep -c` = 1 before it is written into the entry |
| IMP-0977 | n/a | **CLOSE** → `APPLIED`, row 13 | `evidence_grep` on "a reopen from deferred is a resume, not a rejection (IMP-0977)" in `.engine/scripts/lib/work_items.py` |
| IMP-0978 | V1 | **CLOSE** → `APPLIED`, no system change; the gate fired and the quotes were redacted | `evidence_grep`: "its name is never written in this app" ([types.ts L200](src/code-apps/trustee-review-portal/src/dataverse/types.ts#L200)) |
| IMP-0973 | V4 | **DEFER from the start.** Rows 11, 12 (and 14) land, but only the reviewer comparing the screen with the PDF re-observes it | `revisit_when`: *the ledger records WI-0005 at verified:dev from build 20260930-4 or later on the reviewer's confirmation (closes this entry and IMP-0824 together), or records a reopen (both stay open)*. At 15:15 the reviewer said "much better" and lead-agent left WI-0005 at deployed:dev, asking for confirmation ([routing L1131](logs/routing.log#L1131)). That is not yet either outcome |
| IMP-0976 | V4 | **DEFER from the start.** The pack rows' overflow is fixed and the build's Chromium step ran green, but that is V2 geometry evidence and the proposal is routed | `revisit_when`: *the Chromium visual suite measures every `Definitions` consumer at 320 px, or the shared `.definitions` grid stacks below a stated width with a test proving it* |

**Simulated before parking.** The simulation ran in a scratch root: every top-level path is linked to this repository, except `logs/`, `scripts/` and `agents/`, which are copies. The copies had the dispositions above applied, and stub lines carrying each proposed needle. `verify-improvement-log.py --check` exits **0** in both variants of IMP-0967 (deferred, and closed with rows 6–7). Both show 0 unread and 0 fixed-in-flight. The IMP-0961 warning is cleared. The only entries left awaiting approval belong to other reviews (IMP-0855, and the governance blocker IMP-0934). The only warning left is IMP-0298's. The real log's only changes are this draft's ten `reviewed_in` stamps and its three appended findings.

*(Amendment)* **Simulated again, all 16 entries.** Same method: a scratch root with `logs/`, `scripts/` and `.engine/` copied, and stub lines carrying the needles for rows 1, 2, 6, 9, 11 and 13. Both variants of IMP-0967 exit **0**, with 0 unread and 0 fixed-in-flight. (The simulation ran before IMP-0979 was appended; that entry is the next batch's, and it is unread on the real log.) The only entries left awaiting approval are the other reviews' IMP-0855 and IMP-0934, and the only warning is still IMP-0298's. The real log's only change from the amendment is six `reviewed_in` stamps (`diff`: 6 lines).

**Routed work, to be re-measured at apply before it is handed on:**

| To | Item | From |
|---|---|---|
| the session that authored the check-7 descent (automation-agent, via lead-agent) | Dev Summary revision for the failure-path change in flows 1001, 1002 and 1007 (Describe_the_failure If → Switch, descent queries, the new If in 1007); correct the "exception expires 2026-09-30" notes at [L11244](docs/development/revitalise-grant-automation-dev-summary.md#L11244) | IMP-0968 |
| lead-agent | Commit the deployed working-tree changes, including the untracked `scripts/verify-live-flow-definitions.py`; rows 6–7 here and 1–6 of review 2026-09-30 wait on it | IMP-0967, IMP-0964 |
| reviewer | The designer-save question from review 2026-09-29, still unanswered | IMP-0959 |
| lead-agent | *(Amendment)* Add the six untracked WI-0005 files to the same commit: `domain/applicationDetailLayout.ts` and `.test.ts`, `test/detail-harness-app.tsx`, `test/visual/application-detail-layout.visual.spec.ts`, `detail-harness.html`, and `docs/development/trustee-portal-pack-field-map.md` | IMP-0975, IMP-0976 |
| development-agent (frontend) | *(Amendment)* Measure the shared `.definitions` grid at 320 px in the Chromium suite for every `Definitions` consumer, or give it the same narrow-width stacking the pack rows now have. Delivery work under `wbs:6.8`, not a rule change | IMP-0976 |
| pm-agent | *(Amendment)* Re-read the 21 items from `FeedbackDeployment_20-09-2026.xlsx` whose status comment never became acceptance, and add a clause wherever the comment states a requirement (checklist L247). Not classified here: how many of the 21 comments state one | IMP-0973 |
| reviewer | *(Amendment)* Your verdict on the rebuilt WI-0005 screen in DEV | IMP-0973, IMP-0824 |

---

## 6. Digest impact

| | Before this review | Draft (regenerated) | Amendment 1 (regenerated) | After apply |
|---|---|---|---|---|
| Log entries | 965 | 968 (IMP-0970, IMP-0971, IMP-0972 appended) | 975 (IMP-0973 to IMP-0978 in scope; IMP-0979 appended by a live development-agent during this dispatch, not processed here) | 975 or more |
| Distinct lessons | 949 | 952 | 959 | 959 or more |
| Recurring classes (x≥2) | 73 | 73 (`log-timestamp-not-taken-from-the-clock` x2 → x3, `pipeline-dispatch-stops-before-declared-post-deploy` x2 → x3) | 73 (`log-timestamp-…` x3 → x4, `no-assertion-on-shipped-content` x32 → x36 with IMP-0979; the two new classes are x1) | 73 |
| Digest lines | 606 | 606 | 606 | 606 (re-measured at apply) |

Regenerated after the three appends, and again after the amendment's six stamps (`--check` exits 0 both times). `generate-known-failure-modes.py --check` exits 0. `verify-derived-counts.py` reports 6 drifted claims. Five predate this review and belong to other files' owners: the `rev_setting` count twice in the pipeline config, two secured-column counts in the Dev Summary, and the REV Trustee role header. The sixth is row 10.

**Apply-time obligations:** regenerate the digest, then run `--check`, `verify-derived-counts.py`, `verify-engine-instance-split.py`, `verify-build-config.py config/revitalise-grant-automation-build.yml`, every added or edited script's `--selftest`, and `verify-work-items.py --check`. *(Amendment)* Also: `grep` the new §12c and ingestion-checklist text for this client's names before the engine commit (skill §6), and `grep -c` each new needle = 1.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-30-improvement-review-2.md

Findings processed: 16 NEW  →  13 clusters
Regression check:   6 prior changes audited, 2 classes recurred
Proposed:           0 constraints (cap 3), 6 gates/scripts (row 14 only on decision 3),
                    4 skill/knowledge edits, 3 agent-file edits, 1 other, 0 retirements
Altitude calls:     2 generalised from instance to class, 7 left as notes
Digest:             regenerated at draft (amended) — 959 lessons, 73 recurring classes;
                    will regenerate at apply

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Record of what is done on approval

Written only after `APPROVE IMPROVEMENTS`. Nothing has been done yet.
