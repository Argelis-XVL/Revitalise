# Improvement Review — 2026-09-30 (2): post-deploy batch after builds 20260930-2 to 20260930-4

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 69 `NEW` → 38 clusters (62 unread — 6 at draft, 6 folded in by Amendment 1 after build 20260930-4, 30 folded in by Amendment 2 after the trustee-portal-design-2 DEV deploy, 8 folded in by Amendment 3 after the DEV deploy of build 20261002-1, 12 folded in by Amendment 4 after the DEV deploy of build 20261003-2 — plus 5 logged by this review, and 2 reviewer-deferred entries whose approved return condition has happened)
**Trigger:** post-deploy batch
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** APPLIED 2026-10-05 on `APPROVE IMPROVEMENTS` (Xander Lykopoulos, relayed by lead-agent 10:41), as revalidated the same day; decisions 1–6 answered *agreed with suggested*. See §8 *Record of what is done on approval*. Drafted 2026-09-30, amended four times, revalidated 2026-10-05. Previously recorded: DRAFT, parked at the gate, nothing applied; `reviewed_in` stamped on 67 of 69 entries.
**WBS:** system work, `wbs:system`. The flows and ledger items it touches belong to `wbs:4.2,4.3` and `wbs:6.8` (Amendment 1's findings come from WI-0052 and WI-0005, both `wbs:6.8`). Amendment 2's findings come from trustee-portal-design-2, `wbs:6.3`, which the reviewer has declared unbilled ([EX-008](contract/known-exceptions.json#L84)). Amendment 3's findings come from the intake rework, `wbs:4.2,4.3`; three of them record their cost as warranty-class rework on the delivered intake, with no hours estimated. Amendment 4's findings come from the Create Envelope rework, `wbs:3.2` (one also names `wbs:3.1,3.5`, and three are `wbs:system`). One of them refers a possible change order to commercial-agent; this review does not decide it. No change here is billable.

---

## Revalidation — 2026-10-05 (read this first)

Re-measured against the working tree (branch `deploy-first-learning-and-item-closure`, uncommitted changes present) and against DEV, read-only, at 2026-10-05 10:00–10:20. No commit has landed since this draft's last amendment (`7cd080c`, 2 October); what landed is 18 hotfix imports to DEV ([pipeline L299–L316](logs/pipeline.log#L299)) and uncommitted edits. Nothing below is applied; the keyword still applies the table in §3, read with these verdicts.

**Proposed changes (§3, 48 rows).** Each row's target was grepped for the text the row would add. **None of the 48 is on disk.** 42 rows are **VALID as drafted**: 1–5, 8, 9, 11–14, 16–42, 44–46, 48. Row 9's target moved ten lines ([lead-agent L433](agents/lead-agent.md#L433)); its text is unchanged. The other six:

| Row | Verdict | What changed |
|---|---|---|
| 6, 7 | **VALID, still HELD**, and the hold now has a second condition | The check-7 descent is still in no commit: on the committed tree the wrapper self-test reports *"the declared exceptions suppress the check-7 FAILURE today"* PASS; on the working tree it reports FAIL. Once committed, the plain gate will also fail on Create Envelope's `Find_the_failed_action` (routed R1 of [review 2026-10-05](docs/improvements/2026-10-05-improvement-review.md#L161)) until that is fixed. Apply rows 6–7 only after both |
| 10 | **VALID, overlaps** | The count is now **70**. [Review 2026-10-05 row 4](docs/improvements/2026-10-05-improvement-review.md#L149) proposes the same edit; apply it once |
| 15 | **CHANGED — strengthened** | A fourth dated reading: the card app became a solution component on **2 October 09:10 UTC** (`solutioncomponent.createdon`), a day after its push and with no deploy logged at that time. That is the manual *Add existing*. Add this reading to the row's list |
| 43 | **CHANGED — incomplete** | The hotfixes measured three more DocuSign facts the section should carry: prefill fills accept `textTabs` while recipient fills accept `Text` ([pipeline L308](logs/pipeline.log#L308)); a Company tab stores a value the signer sees empty ([L314](logs/pipeline.log#L314)); `routingOrder` is locked by the template and `UpdateEnvelopeRecipient` returns 200 with `RECIPIENT_UPDATE_FAILED` ([L311](logs/pipeline.log#L311)). Fold them in at apply, at E1 |
| 47 | **VALID, still HELD** | `WdlExpression.psm1` is still untracked |

**Routed work (§5).**

| Item | Verdict | Evidence |
|---|---|---|
| Add the card app to the solution (reviewer) | **ALREADY RESOLVED** | DEV: two componenttype-300 rows in `RevitaliseGrantAutomation`, one per appId (`70869c95…` since 22 Aug, `b0483396…` since 2 Oct 09:10 UTC); the solution export holds both `CodeAppPackages` folders |
| Commit the six WI-0005 files (lead-agent) | **ALREADY RESOLVED** | all six are tracked (`git ls-files`) |
| Commit `verify-live-flow-definitions.py` and the deployed flows (lead-agent) | **PARTLY RESOLVED** | the script is tracked since `4eb731e`; the flows, the check-7 descent and `WdlExpression.psm1` are not |
| Designer-save question (reviewer) | **WITHHELD** already (Amendment 3) | — |
| Dev Summary revision for the check-7 failure path (IMP-0968) | **VALID** | [Dev Summary L11244](docs/development/revitalise-grant-automation-dev-summary.md#L11244) still says the exception expires 30 September |
| `.definitions` grid at 320 px; first app `.tableScroll` position; per-app test port | **VALID** | [`.definitions`](src/code-apps/trustee-review-portal/src/styles/app.module.css#L563) keeps its fixed column; [`.tableScroll`](src/code-apps/trustee-review-portal/src/styles/app.module.css#L303) has no `position`; both `playwright.config.ts` use port 4173 |
| pm-agent re-read of the 21 feedback-sheet items | **VALID** | no re-read recorded; the 32 acceptance links since 30 September are Design 2.0 items plus WI-0013 and WI-0053 |
| Your verdict on WI-0005 | **VALID** | WI-0005 is still `deployed:dev` |
| Three pipeline-config notes; TAD §9.3; supplied-assets page | **VALID** | [pipeline L1124](config/revitalise-grant-automation-pipeline.yml#L1124) and [L1968](config/revitalise-grant-automation-pipeline.yml#L1968) still credit the push; [TAD L1708](docs/architecture/revitalise-grant-automation-architecture.md#L1708) still says a pushed app *is* a component; [supplied-assets L36](docs/reference/supplied-assets.md#L36) still says 131 files (285 tracked) |
| Relink WI-0055..0105 after row 16; retitle WI-0052 after row 23 | **VALID**, waits on those rows | — |
| `settings-rows.notes.md` RoundStatisticsHistory values (IMP-0995) | **VALID** | the notes still say 2026-02-16 and 0; DEV holds 2026-09-24 and 715 (modified 3 Oct) |
| Live re-read mode for "written after the last import" | **VALID** | no such mode in the script |
| Test-data instructions still describe the token route (IMP-1017) | **VALID** | [README L198](src/tests/data/README.md#L198), [payloads L13](src/tests/data/intake-payloads.json#L13) |
| Endpoint check accepts `dev` (IMP-1018) | **VALID** | [ValidateSet L75](provisioning/entra/verify-intake-endpoint-auth.ps1#L75) still lists `dev` |
| TAD §12.3: close A-INT-15 and A-INT-11 | **VALID** | [A-INT-15 row](docs/architecture/revitalise-grant-automation-architecture.md#L3788) unchanged |
| TAD every-tab rule (IMP-1031) | **VALID** | [ADR-043](docs/architecture/revitalise-grant-automation-architecture.md#L2446) still says the referee tabs are left for the referee |
| Re-issue route after a pre-send stop (IMP-1028) | **VALID** | no re-issue route anywhere in the TAD |
| Commit Create Envelope and `WdlExpression.psm1` | **VALID** | both still uncommitted |
| Commercial-agent: recipient-authentication change order | **VALID** | nothing recorded in `logs/commercial-events.jsonl` or `contract/change-orders/` |
| Your live checks R1–R6, M4, M6 | **UNVERIFIABLE from here, likely exercised** | Create Envelope ran 19 times since 3 October (last 7 Succeeded, newest 4 Oct 07:39 UTC), but what each envelope held is visible only in DocuSign. Your confirmation per step closes the six deferrals |

**Dispositions (§5 table) that change:**

| Entry | Was | Now | Why |
|---|---|---|---|
| IMP-1008 | DEFER | **CLOSE** at apply | Its `revisit_when` is met: re-run FetchXML on `solutioncomponent` (componenttype 300, linked to `solution`) on 2026-10-05 10:05 by improvement-agent shows two rows in `RevitaliseGrantAutomation`, one per appId. Re-run at apply and record it as `reobserved` V3 |
| IMP-1025 | DEFER | **DEFER**, condition half met | The `tabType` strings were measured live on 3 October ([L308](logs/pipeline.log#L308)); the TAD still says *"unmeasured"* ([L3391](docs/architecture/revitalise-grant-automation-architecture.md#L3391)). New routed item: architect-agent records the measurement against `A-DS-16` |
| IMP-0971, IMP-0879, IMP-0906 (decision 2) | DEFER | **DEFER**, unverifiable | The 2 and 3 October DEV stage lines are PARTIAL and the audit since 2 October gives 0 findings, but no line records that `--pending` ran before them. A pipeline line naming that run would settle it |

**Decisions.** 1, 2, 3, 4 and 6: **VALID, unanswered**. Decision 5: **CHANGED.** `Designsystem/Revitalise Design System (1)/` is no longer untracked: commit `7cd080c` (2 October) added it, 145 files beside the original drop's 131. The question still stands, because the two copies still share inner folders. Its last consequence (CI and a local run judge different trees) no longer applies.

**Logged by this revalidation:** IMP-1039 (the "still parked" warning about IMP-0298 is false; both reviews it names are applied), IMP-1040 (this draft's carried rows went stale while parked), IMP-1041 (DEV's intake flow lacks the `rev_costs` write). All three are unread and wait for the next batch.

---

## Summary

The DEV deploy of build 20260930-2 worked: the import, the Code App push and the new live flow re-read all ran. Every finding from it is small. The one that matters: **agents type log timestamps by hand, and today they typed times up to five and a half hours in the future** in three different logs. Yesterday's written reminder to use the clock did not reach a single one of the five agents involved. This review makes the tools stamp the time.

**Added since the draft (builds 20260930-3 and -4):** the Trustee Portal detail screen had to be rebuilt field by field from the Trustee Pack PDF, after you raised it a third time. Every earlier pass checked only the section order, and the written rule telling developers to open the document page by page was already in place for two of them. The amendment adds a method (write the PDF's rows into a test and compare the screen to it), a fix to how feedback-sheet rows become work items, and a small ledger fix.

**Added by Amendment 2 (the Design 2.0 card app's first DEV deploy):** the second Code App reached DEV but not the solution. Pushing it with the solution's name did not add it, which is what the first push found in August. A later note that called the opposite "settled" had mistaken a manual add for the push. Two things in the delivery records were also wrong in a way nothing caught. All 51 new items were recorded as deployed against the first app's push line, so they would have read as deployed even if the card app had never been pushed. And the item wording kept drifting from the approved design: eight clauses in five items had to be amended one at a time, after development had started. The amendment fixes both in the tools, adds an intake checklist for supplied design bundles (the export had arrived with four of its screens missing, and nobody checked), and says how to prove a screen "matches the design".

**Added by Amendment 3 (the intake rework's DEV deploy, build 20261002-1):** the deploy worked, and the live intake flow now matches source. The lesson behind it is larger than the flow. Someone saved the intake flow in the designer, and the save rewrote the whole flow from what the designer understood: it emptied two record-creating steps, removed the secure-inputs setting and changed the trigger's sign-in mode. **This system's own definition of "a human can use it" requires exactly that save**, in seven places, and says nothing about what to do afterwards. The amendment adds the missing step (re-read the live flow after any designer save, and re-import if it differs) everywhere that definition is taught. It also records that an integration decision was closed when credentials were handed over, before anyone checked that the website's plugin could send them. And it asks you whether open assumptions that only a DEV deploy can close should still need an override each time: the last three DEV deploys all did.

**Added by Amendment 4 (the Create Envelope rework, build 20261003-2 in DEV):** four of the twelve new lessons come from the same habit. A flow you saved in the designer was treated as proof of more than it shows: that a property it did not complain about was accepted, that actions placed one after another work on the same envelope, that two actions with the same body are the same call, and that a field called "phone number" is only a contact field (it turns on SMS delivery). The verify skill gains one paragraph saying what a designer-saved flow proves and what it does not. The workflow design skill gains three checks that the Create Envelope design missed: send last, after every step that can fail; say how a stopped run is restarted when the flow only fires on a new record; and list every signer control only DocuSign's template or account can set. The build's timeout script now stops calling a leftover `pac` process "the usual cause". On 2 and 3 October that wording cost two blocked builds while the real blocker was a Keychain prompt, the same mistake as August. And `testResults.xml` stops being tracked: test runs have rewritten it, and three commits picked up the rewrite.

**Waiting on you:** `APPROVE IMPROVEMENTS`, plus six decisions below (Amendment 4 adds none). Two of the changes (rows 6 and 7) wait on the same condition as this morning's secure-data review: the other session's flow changes must be committed first. Row 47 waits on a commit too: the new test helper it names is not in git yet. One live step is still yours from the deploy: add the card app to the solution in the maker portal.

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

*Items 11–20 were added by Amendment 2.*

11. **The Code App knowledge page records that pushing by solution name does not add an app to the solution, with the dated evidence for both readings** ([code-apps L536](knowledge/technology/code-apps.md#L536)). The first app is in the solution because the reviewer added it by hand on 22 August. A read the next day saw it there and credited the push, and that credit went into the TAD and three pipeline-config notes. Today's first push of the card app reproduced August's result: no solution component, and no app row at all. The page gains the check that tells the two apart: compare the component's creation time with the push time.

12. **One app's push can no longer count as another app's deployment** ([deploy-record L689](.engine/scripts/lib/work_items.py#L689), [labels L95](.engine/scripts/lib/deploy_markers.py#L95)). Executed, not read: all 51 card-app items resolve their DEV deploy record on the first app's push line ([L277](logs/pipeline.log#L277)), not the card app's ([L279](logs/pipeline.log#L279)). A push entry gains an `app:` folder, its label names the folder, and the deploy line must name it too. This is the same rule as "an import never counts as a push", taken one step further.

13. **A supplied design bundle gets an intake checklist of its own** (new section beside [Palette Check L139](skills/how-to-intake-external-documents.md#L139)). Today nothing exists for it. The Design 2.0 export loads nine local files, and three are present (renamed `.jsx.txt`), two belong to the design-system root, and four are missing. The design was scoped to one screen from its README title, and the reviewer found the gap. The checklist asks for the entry point's references to be resolved, duplicate copies to be compared, kit wording to be treated as presentation only, the handoff's own claims to be measured, and a 320 px render.

14. **The design-source gate checks every top-level supplied folder, not only folders named after an app** ([in-scope rule L117](scripts/verify-design-source-coverage.py#L117)). It passed with `Design-2.0/` present and uncited, because none of its folders is named after an app. Measured: the new rule finds 0 problems today and would have flagged both new drops before the TAD cited them. Its second half (two identical copies of the design system) waits on decision 5.

15. **"Matches the design" is proved by measuring both renders, never by reading the design's code** (new §12d beside [§12c L927](skills/how-to-verify-a-platform-contract.md#L927)). Three passes on the card app claimed matches that were not there. The first read inline styles and missed the kit's global stylesheet. The second marked 29 rows "match" from a grep. The third measured, but only at desktop width and only for elements it had chosen by eye. The rule: equal computed values on both renders, at every width captured, with the probe list generated from the design's own declarations.

16. **The architect lists the item clauses a TAD overrides, before development starts** ([architect L254](agents/architect-agent.md#L254)). The items for this feature were written from the design README while the TAD was being written, and the TAD then decided otherwise in places. Measured: 8 clauses in 5 items had to be amended, one pm-agent round trip at a time, after development had found them ([routing L1209–L1212](logs/routing.log#L1209)).

17. **Re-tracing a test's evidence stops counting as a rejection** ([fold L771](.engine/scripts/lib/work_items.py#L771)). Rewriting one test file left three items pointing at test names that no longer exist, and the only way to re-point them was a reopen. Two of them now show two reopens, which is the trigger for a stronger model. This replaces row 13's narrower fix: a reopen counts only when something was rejected.

18. **The assumption-register check reads the ids it used to skip** ([id grammar L127](scripts/verify-assumption-markers.py#L127)). Measured over the real registers: 11 rows the gate never saw (ids such as `A-ATYPE-1`, `A-RESULT-1`, `A-G03`), and with the wider grammar 0 failures and one true new note (an open row with no location).

19. **The build warns four days before a gate baseline expires** ([expiry L140](scripts/lib/gate_baseline.py#L140)). Eight baselines expired on 30 September with no warning and were renewed this morning "to unblock the build". Twelve now expire on 13–14 October.

20. **Four smaller lessons are written down where the next person will look.** Power Automate's ordering comparisons fail on an empty value, and `string()` of a true/false value gives `True`/`False` ([power-automate L340](knowledge/technology/power-automate.md#L340)). Two layout lessons from the card app go in the Code App styling notes ([code-apps L639](knowledge/technology/code-apps.md#L639)). Commercial-agent reads the recorded unbilled decisions before proposing hours ([commercial L126](agents/commercial-agent.md#L126)). And this agent never ties its closing evidence to wording that another rule forces to be rewritten ([improvement-agent L676](agents/improvement-agent.md#L676)).

*Items 21–27 were added by Amendment 3.*

21. **A designer save counts as a live write, and every place that asks for one says what to do next** ([C-TECH-053](constraints/technology/technology-constraints.md#L108), [V4 row L596](skills/how-to-verify-a-platform-contract.md#L596), [pipeline check (c) L476](agents/pipeline-agent.md#L476), [build-and-deploy L199](knowledge/technology/build-and-deploy.md#L199), [dev summary template L96](templates/dev-summary-template.md#L96), [test report template L82](templates/test-report-template.md#L82), [pipeline example L171](config/pipeline.yml.example#L171)). Today "a human can use it" means a person opens the flow in the designer *and saves it*. On 2 October one such save rewrote the live intake flow, and nothing noticed until an application arrived empty. The new sentence, in all seven places: after the save, run the live-flow re-read, and re-import from source if it reports a difference.

22. **The knowledge page stops calling the designer-save cause "not proven"** ([build-and-deploy L227](knowledge/technology/build-and-deploy.md#L227)). The 2 October loss carries the designer's fingerprints throughout, and inside the same save the step written in the flat form kept every column while the two nested ones lost theirs. That answers the designer-save question this review has listed as yours since 29 September.

23. **Three Power Automate facts are written down** ([hand-authoring L381](knowledge/technology/power-automate.md#L381), [Trigger L290](knowledge/technology/power-automate.md#L290), [fetch note L483](knowledge/technology/power-automate.md#L483)). Write each Dataverse create or update column as its own `item/<column>` key, and a lookup as `item/<navigation property>@odata.bind`. The trigger's sign-in mode is a property of the flow definition (`triggerAuthenticationType`, `All` for Anyone), so it can ship in source. And one `pac env fetch` with a `like` filter finds every live flow containing a given shape, even though reading the column itself that way truncates it.

24. **A decision that depends on what an outside party's tool can do stays open until that tool has done it** ([what counts L41](skills/how-to-verify-a-platform-contract.md#L41), [first-environment sweep L662](skills/how-to-verify-a-platform-contract.md#L662)). The intake sign-in decision was closed on "I have shared the url, clientid and secret". The open question it had recorded, whether the website's plugin could send a changing token, was answered no a week later. The sweep a first environment triggers also re-tests every "this cannot be written in source" claim, because that is the claim that was wrong here.

25. **A check that needs a person in the designer names that person** ([register L499](skills/how-to-verify-a-platform-contract.md#L499)). The TAD told a development dispatch to settle a key name by binding it in the designer, which no dispatch can do. It went to you as a reviewer action, you did it in a few minutes, and the conversion followed. The register's "cheapest verification" cell now names a human executor whenever the step needs the designer.

26. **When a decision is re-made, the architect lists every place the old decision is written, not only the build checks** ([architect L106](agents/architect-agent.md#L106)). The architect's instruction today says to list the gates from the build config. The re-decided sign-in route was written into about 14 files, most of them tests, fixtures, settings comments and shipped descriptions. Two were still missed: the test-data instructions, in a README and in the payload file, still describe the retired token route. The new instruction: grep the old decision's words across the whole repository and list every hit with what happens to it.

27. **Only on decision 6: an open assumption that only a DEV deploy can close stops needing an override for that DEV deploy** ([C-TECH-058](constraints/technology/technology-constraints.md#L128)). It still blocks everything after DEV until it is closed. The last three DEV deploys that carried open assumptions each needed your override for this reason ([routing L943](logs/routing.log#L943), [L1227](logs/routing.log#L1227), [L1249](logs/routing.log#L1249)).

*Items 28–33 were added by Amendment 4 (table rows 41–48).*

28. **The verify skill says what a designer-saved flow proves, and what it does not** (row 41, after [§2 L104](skills/how-to-verify-a-platform-contract.md#L104)). It proves the actions and the parameters it holds. It does not prove four things, and each one cost a design pass on Create Envelope. A property the designer did not complain about may simply have been dropped: the merge fields placed inside `SendEnvelope`'s signers never filled a tab. Actions in a row do not act on one envelope unless an id parameter links them: the third action of your test flow has no `envelopeId`, so it would have sent a second envelope ([TAD L3338](docs/architecture/revitalise-grant-automation-architecture.md#L3338)). Two actions with the same body may still be different calls. And a parameter's name does not show what it triggers: `phoneNumber` on a recipient turns on SMS delivery ([TAD L3443](docs/architecture/revitalise-grant-automation-architecture.md#L3443)). The skill already says the opposite case (a designer error about an unflagged property is a warning sign, [L103](skills/how-to-verify-a-platform-contract.md#L103)); this adds the case where it says nothing.

29. **The workflow design checklist gains three checks** (row 42, [design checklist L27](skills/how-to-design-a-workflow.md#L27)). Send last: in Create Envelope as built since 6 September, the reminders and the Dataverse write ran after the send, so a failure there left the applicant holding an envelope while the alert invited a re-run that would send a second one. It is fixed in source: reminders now run before the send, and only the record write follows it ([flow L1567](src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L1567)). Name the restart: the flow fires only when a grant is created, and the new pre-send stops told the process owner to "correct it and re-run", which nothing can do. Name what only the outside service can enforce: required fields, reassignment and recipient sign-in are DocuSign template or account settings that no connector action sets.

30. **A short DocuSign section on the Power Automate knowledge page** (row 43, before [Sensitive Data Flows L310](knowledge/technology/power-automate.md#L310)). Four facts, each with the level of its evidence, pointing at the measured table in TAD ADR-067 rather than copying it.

31. **A template's own field list decides which fields a flow fills** (row 44, extends [§2 L120](skills/how-to-verify-a-platform-contract.md#L120)). The TAD named eight tabs to fill, taken from an earlier design; you said every tab on the template is filled except signature, signer name and date. The skill row that already says a template's role names come from the template now says the same of its field set.

32. **The build's timeout script stops naming a leftover `pac` process as the cause** (row 45, [report_stray_pac L94](scripts/run-with-timeout.sh#L94); row 46, [build-and-deploy L451](knowledge/technology/build-and-deploy.md#L451)). On 2 and 3 October it printed "the usual cause" for a VS Code `pac` that was not blocking anything, and two build reports repeated it ([build L159–L160](logs/build.log#L159)). The Keychain hint printed only when no such process was found. The new message calls the process a candidate, prints the Keychain check in both cases, and gives the 45-second `pac org who` test that tells the two apart. This is the August mistake again: the knowledge page was corrected then, and the script was not.

33. **Two small housekeeping changes.** The Power Automate page names the new test helper that runs a flow's own guard expressions (row 47, held until the helper is committed). And `testResults.xml` is untracked and ignored (row 48). Pester's `-CI` switch rewrites it at the repository root. It was committed once on 26 August and swept into three later commits as a rewrite; nothing reads it.

### Elements added

| Element | What it is |
|---|---|
| `scripts/log-line.py` (and its engine copy) | Appends one line to a `logs/*.log` file, stamped from the clock under a lock. Refuses a line that already carries a stamp |
| A `BuildGates.Tests.ps1` test (row 7, held) | Runs the flow-definition gate's own self-test in the build's test step |
| A `work-items.py` self-test case (row 13) | Resuming a deferred item leaves its Reopens count unchanged |
| *(Amendment 2)* Supplied Design Bundle Checklist in the intake skill (row 18) | Five checks before a supplied design is scoped: entry-point references, duplicate copies, kit wording, the handoff's own claims, a 320 px render |
| *(Amendment 2)* §12d in the verify skill (row 21) | How a "matches the design" claim is measured |
| *(Amendment 2)* `reopen --retrace` (row 13, revised) | Re-points an item's evidence after a test rewrite without counting as a rejection |
| *(Amendment 2)* `link --title` (row 23) | Lets the ledger correct a title that a relinked acceptance has reversed |
| *(Amendment 2)* An `app:` key on a Code App push entry (row 16) | Names which app a push delivers, so each app's items are discharged only by its own push |
| *(Amendment 4)* A DocuSign section in the Power Automate knowledge page (row 43) | What a flow can set through the connector and what only the template or account can |
| *(Amendment 4)* A `run-with-timeout.sh` self-test case (row 45) | A timeout that finds a stray `pac` still prints the Keychain check and the confirming probe |

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
| *(Amendment 2)* [work_items.py fold L771](.engine/scripts/lib/work_items.py#L771) (row 13, revised) | Reopens counts rejections only: a resume from `deferred` and a `--retrace` add nothing |
| *(Amendment 2)* [code-apps.md L536](knowledge/technology/code-apps.md#L536) | The push-by-name warning keeps its conclusion and gains the dated evidence and the creation-time check |
| *(Amendment 2)* [deploy_markers.py L95](.engine/scripts/lib/deploy_markers.py#L95), [work_items.py L689](.engine/scripts/lib/work_items.py#L689), [verify-pipeline-config.py](scripts/verify-pipeline-config.py) (both copies), the pipeline config's three DEV push entries | Per-app push labels and the check that two push entries in one environment each name their app |
| *(Amendment 2)* [pipeline-agent.md L283](agents/pipeline-agent.md#L283) | A Code App push's `WRITE` lines name the folder pushed from |
| *(Amendment 2)* [verify-design-source-coverage.py L117](scripts/verify-design-source-coverage.py#L117) (both copies) | Every top-level supplied folder is in scope by its root path; colliding citations need the full path (decision 5) |
| *(Amendment 2)* [C-TECH-075](constraints/technology/technology-constraints.md#L145) | Amended to match the gate: a supplied drop's root is cited, not only folders named after an app |
| *(Amendment 2)* [architect-agent.md L254](agents/architect-agent.md#L254) | New "before you finish" step: the item clauses this TAD overrides |
| *(Amendment 2)* [verify-assumption-markers.py L127](scripts/verify-assumption-markers.py#L127) (both copies) | Wider id grammar, bold ids, `.css` targets |
| *(Amendment 2)* [gate_baseline.py L140](scripts/lib/gate_baseline.py#L140) (both copies) and [verify-build-config.py](scripts/verify-build-config.py) | A four-day expiry warning, printed once per build at the preflight |
| *(Amendment 2)* [power-automate.md L340](knowledge/technology/power-automate.md#L340), [code-apps.md L639](knowledge/technology/code-apps.md#L639) | Four lessons: null in ordering comparisons, `string()` of a boolean, group spacing, positioned scroll wrappers |
| *(Amendment 2)* [commercial-agent.md L126](agents/commercial-agent.md#L126), [improvement-agent.md L676](agents/improvement-agent.md#L676) | Read the recorded unbilled decisions; never anchor a needle to rewritable wording |
| *(Amendment 2)* IMP-0764's `evidence_grep`, IMP-0500's `deferred_reason` (log data) | The needle moves to a stable line; the deferral records that its condition is met |
| *(Amendment 3)* [C-TECH-053](constraints/technology/technology-constraints.md#L108) | Amended: a V4 designer save of a solution flow is followed by the live-flow re-read |
| *(Amendment 3)* [verify skill §5 L596](skills/how-to-verify-a-platform-contract.md#L596), [§1 L41](skills/how-to-verify-a-platform-contract.md#L41), [§4 L499](skills/how-to-verify-a-platform-contract.md#L499), [§6 L662](skills/how-to-verify-a-platform-contract.md#L662) | After-the-save step; an outside party's tool is a platform contract; a designer-only check names its human executor; the sweep re-tests "cannot be written in source" claims |
| *(Amendment 3)* [pipeline-agent.md check (c) L476](agents/pipeline-agent.md#L476), [architect-agent.md L106](agents/architect-agent.md#L106) | The after-the-save step; a re-decided ADR lists every hit of the old decision's words |
| *(Amendment 3)* [dev-summary template L96](templates/dev-summary-template.md#L96), [test-report template L82](templates/test-report-template.md#L82), [pipeline.yml.example L171](config/pipeline.yml.example#L171) | The V4 wording gains the live re-read after the save |
| *(Amendment 3)* [build-and-deploy.md L199, L227](knowledge/technology/build-and-deploy.md#L199), [power-automate.md L290, L381, L483](knowledge/technology/power-automate.md#L381) | The after-the-save step; the designer-save cause recorded as observed; flat item keys, the trigger-mode property, the `like` search |
| *(Amendment 3)* [C-TECH-058](constraints/technology/technology-constraints.md#L128) (only on decision 6) | An assumption whose own register row names the DEV deploy as its check does not block that DEV deploy |
| *(Amendment 4)* [verify skill §2 L104, L120](skills/how-to-verify-a-platform-contract.md#L104) | What a designer-saved flow does not prove; a template's field set comes from the template |
| *(Amendment 4)* [how-to-design-a-workflow.md L27](skills/how-to-design-a-workflow.md#L27) | Three checklist lines: irreversible step last, the restart route, what only the outside service enforces |
| *(Amendment 4)* [run-with-timeout.sh L88–L111](scripts/run-with-timeout.sh#L88), both copies | The stray-`pac` message: a candidate, not the cause; Keychain check and probe in both branches |
| *(Amendment 4)* [build-and-deploy.md L451](knowledge/technology/build-and-deploy.md#L451) | Step 1 ends with the 45 s `pac org who` probe before any retry |
| *(Amendment 4)* [power-automate.md L340](knowledge/technology/power-automate.md#L340) (held) | Names the guard-expression test helper; IMP-1029 gains `capability: true` |
| *(Amendment 4)* `.gitignore`, `testResults.xml` | The file is ignored and removed from the index (`git rm --cached`) |

## What is still open

**The flows now running in DEV exist in no commit.** The build manifest records 12 changed paths at pack time ([manifest](build/artifacts/revitalise-grant-automation-20260930-2/manifest.json)). The new live-flow check script is untracked, and it has already run in a deploy. Committing them is lead-agent's call. Two held changes here and six in this morning's review wait on it.

**The rebuilt Trustee Portal detail screen is in DEV too, and six of its files are in no commit either.** The layout module, its PDF transcription test, the phone-width browser test, its harness page and harness app, and the field map are all untracked. Build 20260930-4 recorded 33 changed paths at pack time ([manifest](build/artifacts/revitalise-grant-automation-20260930-4/manifest.json)). They belong in the same commit as the flows. Row 11 describes the transcription test in general terms, so it does not depend on that commit.

**Only you can say whether the rebuilt screen now matches the PDF.** WI-0005 is at deployed:dev after build 20260930-4. At 15:15 you called it "much better", and lead-agent asked you to confirm it is done. The finding stays open until the ledger records your confirmation or a reopen.

**The other label/value lists in the portal are not measured on a phone.** The shared list layout ([`.definitions` L563](src/code-apps/trustee-review-portal/src/styles/app.module.css#L563)) keeps the same fixed 140 px label column that pushed the new rows 8 px sideways at 320 px. It is used through [`Definitions` L135](src/code-apps/trustee-review-portal/src/components/Panel.tsx#L135) by five components and pages. That is delivery work, routed to development-agent below.

**The rewritten failure path in the intake, scoring and reminders flows is shipped but not described or tested.** The test report caught it before the deploy, and you approved the deploy knowing. The Dev Summary still says the check-7 exceptions are open ([L11244](docs/development/revitalise-grant-automation-dev-summary.md#L11244)). Only making a flow fail on purpose proves the new path works. That revision belongs to the session that wrote the change. It is routed below, and the finding stays open until the revision exists.

**The 29 September 21:51 "SUCCESS" should have read PARTIAL, and the log cannot be corrected.** That retry re-imported the solution and never pushed the Code App ([L241](logs/pipeline.log#L241)). Lead-agent never received that dispatch, so its check never ran. Today's push replaced the app, so nothing is wrong live now. The line stays in the log. Once row 5 lands, lead-agent's per-result check stops re-reporting it; the build's history audit still lists it, as a warning only.

**Your designer-save question from yesterday's review is still unanswered.** Nothing here depends on it. *(Amendment 3: answered by evidence, so it is no longer yours to answer. The 2 October loss is a designer save, shown by the designer's fingerprints and by the flat step surviving the same save. The routed row below is withheld at apply.)*

**RESOLVED 2026-10-05 (revalidation): the card app is in the solution** — a componenttype-300 row dated 2 October 09:10 UTC. Previously recorded: *the card app is in DEV but in no solution, and only you can add it.* Pipeline-agent read the solution four times after the push, including after a repeat push: still one Code App in it, and no record of the card app in any solution ([L281](logs/pipeline.log#L281)). Until it is added through the maker portal's *Add existing*, it cannot travel to Test/Acceptance with the solution. The finding stays open until a re-read shows two apps in the solution.

**Three pipeline-config notes and two TAD passages still say the push puts the app in the solution.** They are at [L1099](config/revitalise-grant-automation-pipeline.yml#L1099), [L1936](config/revitalise-grant-automation-pipeline.yml#L1936) and [L2220](config/revitalise-grant-automation-pipeline.yml#L2220) of the pipeline config, in the main TAD's §9.3 and in the Design 2.0 TAD's A-TR-15 row. Their conclusion for Test and Production still holds for the first app, because it is in the solution; only the reason is wrong. They belong to pipeline-agent and architect-agent, and are routed below.

**The 51 card-app items read as deployed on the strength of the wrong log line.** The card app really was pushed ([L279](logs/pipeline.log#L279)), so nothing is false today. Their records stay as they are; after row 16 lands, pm-agent relinks them to the card app's own label, so the next deploy is judged correctly.

**Whether the card app now matches the design is still yours to judge.** The second audit's 17 findings were fixed in Revision 3.2 and measured at 1280 px and below. No rule here can stand in for you comparing the two apps side by side.

**The first app has the same hidden-text overflow the card app had, and nobody has measured it.** Its table wrapper scrolls sideways but is not positioned ([L303](src/code-apps/trustee-review-portal/src/styles/app.module.css#L303)), which is what let the card app's hidden sort hints widen the page at 320 px. Routed to development-agent.

**(Amendment 3) A designer save between deploys is still seen only at the next deploy.** The live-flow re-read runs after an import, and it ran on 1 October with nothing wrong ([pipeline L283](logs/pipeline.log#L283)). The save came the next morning. Running it before a deploy or a test needs a small change first: run against today's source, it would report every change the deploy is about to make. Its "written after the last import" check is the part that matters there. Routed to development-agent.

**(Amendment 3) Only a real website submission proves the new sign-in route.** The import kept the trigger mode and the three rewritten record steps exactly as in source ([pipeline L289](logs/pipeline.log#L289)). Whether the website's form reaches the flow through the signed address is your step R1 from the test report. The callback-address check could not run, because it needs the provisioning certificate you hold.

**(Amendment 3) The test-data instructions still describe the retired token route** ([README L197](src/tests/data/README.md#L197), [payloads L12](src/tests/data/intake-payloads.json#L12)). Anyone following them asks for a token the flow no longer accepts. Routed to development-agent.

**(Amendment 3) The endpoint check accepts `dev` and then fails on it** ([ValidateSet L75](provisioning/entra/verify-intake-endpoint-auth.ps1#L75)). DEV has no intake settings block by design, so the script throws. Its sibling, the callback-address check, already says so in its own help ([L52](provisioning/entra/verify-intake-callback-url.ps1#L52)). Routed, as a one-line change for whoever owns the script.

**(Amendment 4) The Create Envelope flow in DEV is in no commit, and nor is the test helper that checks it.** The deploy's provenance check records the artifact as differing from the manifest commit, "uncommitted by instruction" ([pipeline L298](logs/pipeline.log#L298)). The contract tests import `WdlExpression.psm1`, which is untracked, so a fresh clone cannot run them. Committing is lead-agent's call; row 47 waits on it.

**(Amendment 4) The TAD still says the flow fills eight tabs and leaves the referee's address for the referee** ([§5.8 step 2 L1154](docs/architecture/revitalise-grant-automation-architecture.md#L1154), [ADR-043 L2446](docs/architecture/revitalise-grant-automation-architecture.md#L2446)). Your code-review rule (every tab except signature, signer name and date) is not in it yet. Routed to architect-agent.

**(Amendment 4) Nothing restarts Create Envelope after one of its pre-send stops.** The flow fires only when a grant is created, and neither the TAD's risk rows ([A-R74 L3659](docs/architecture/revitalise-grant-automation-architecture.md#L3659), [A-R79 L3664](docs/architecture/revitalise-grant-automation-architecture.md#L3664)) nor the flow name a route. The shipped alert no longer promises a re-run; the design question is routed to architect-agent.

**(Amendment 4) Most of the new lessons close only on your live checks.** R1, R2, R3, R5 and R6 in the test report ([L69–L72](docs/tests/revitalise-grant-automation-test-report-20261003-2.md#L69)) and M4 and M6 in the TAD ([L3844](docs/architecture/revitalise-grant-automation-architecture.md#L3844)) are what re-observe them. Which `tabType` string the fill action accepts is one of them, still open as `A-DS-16`.

**(Amendment 4) One finding refers a possible change order for recipient authentication to commercial-agent.** The TAD has since replaced phone authentication with an access code, recorded as free ([L3711](docs/architecture/revitalise-grant-automation-architecture.md#L3711)), so the referral may be moot. That is commercial-agent's to confirm, not this review's.

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

**4. Should a gate stop hours being billed against work you have declared unbilled?** *(Amendment 2)*

**Problem** — Your unbilled decision for the Design 2.0 work is recorded in two places ([EX-008](contract/known-exceptions.json#L84), [CE-0012](logs/commercial-events.jsonl#L12)), and no check reads either: the worklog check would accept a billable session against `wbs:6.3`.
**Suggested fix** — Yes, but as a commercial-agent design, not a rule written here: `wbs:6.3` also holds contracted, billable work, so the check has to key on items, and today a worklog session does not name items. Row 28 makes commercial-agent read the recorded decisions in the meantime.
**What happens if you don't** — The decision holds only as long as commercial-agent remembers to read it, and the first test of that is the next invoice.
[EX-008](contract/known-exceptions.json#L84)

---

**5. What is `Designsystem/Revitalise Design System (1)/`: the replacement for the tracked design system, or a stray copy?** *(Amendment 2)*

**Problem** — It is an untracked, newer full export: the tracked drop plus the Design 2.0 handoff, two new kit screens and three screenshots (17 differences, measured with `diff -rq`). The TAD reads screens from it, but the design-source gate cannot tell which copy a citation means, because both copies have the same inner folders.
**Suggested fix** — Treat it as the replacement: architect-agent tracks it in place of the old drop, re-measures the supplied-assets page, and the gate's collision check (row 19, second half) then has nothing to report.
**What happens if you don't** — Row 19's collision half stays held, and the gate keeps reporting one citation as covering both copies. Also, the CI run never sees untracked files, so it and a local run judge different design trees.
[supplied-assets L36](docs/reference/supplied-assets.md#L36)

---

**6. Should an open assumption that only a DEV deploy can close stop needing an override for that DEV deploy?** *(Amendment 3)*

**Problem** — The rule blocks a deploy into any environment where an open assumption could be closed, so an assumption that only the DEV deploy itself can close always needs your override; the last three DEV deploys that carried open assumptions all did, for that reason.
**Suggested fix** — Yes: where the assumption's own register row names the DEV deploy (the import, the first push, a designer check in DEV, a run in DEV) as its check, the DEV deploy goes ahead and records it, and the assumption blocks every environment after DEV until it is closed.
**What happens if you don't** — Nothing breaks: each DEV deploy of this kind keeps costing you one more message and a relay. But the override stops being a real decision when it is always given, and that makes a genuine one harder to notice.
[C-TECH-058](constraints/technology/technology-constraints.md#L128)

---

Measured, not assumed: the future timestamps come from `stat` modification times, not from any agent's statement. The deploy-list rule was measured over all 8 `built` transitions in the ledger. The post-deploy check was run in three forms. The npm audit was re-run (exit 0, one advisory, already triaged). The disposition was simulated on a copy of the log: `verify-improvement-log.py --check` exits 0, with 0 unread and none of this review's entries left awaiting approval, in both the held and the applied variant of rows 6–7. **Not verified:** none of the scripts in rows 1, 2, 6 and 8 is written yet. Whether a flow's rewritten failure path works was not observed, and cannot be without making the flow fail in DEV. **Amendment:** the decision-3 rule was measured over all 52 ledger items, and the feedback-sheet gap over its 38 rows that carry a status comment. The two new future stamps come from the log file's modification time. The disposition was simulated again for all 16 entries, in both variants of rows 6–7: exit 0, 0 unread, and only the other reviews' two entries left awaiting approval. **Not verified:** whether the rebuilt screen matches the PDF (that needs your eyes), and the portal's other label/value lists at 320 px. Rows 11–14 are not written yet. **Amendment 2:** executed, not read: the deploy-record matcher on today's log (51 of 51 card-app records resolve on the first app's line), the assumption-marker gate with the wider grammar over the real registers (97 → 108 rows, 0 failures), the design-source gate and the root-path rule over the three drops (0 findings today, 2 true before the Design 2.0 TAD), a missing-reference resolver over 40 HTML files (16 reported, 6–10 real, so not wired), the ordering-comparison search over all flow source (1 hit, safe by its data), IMP-0500's own check command (58 of 80 manifests) and a signature diff over them (37 of 261). The disposition was simulated in three variants, each exit 0 with 0 unread. **Not verified:** none of rows 13 and 15–30 is written. Nothing live was read by this amendment; the push and solution readings are pipeline-agent's. Whether the card app matches the design, and whether the wellbeing spacing is right, need your eyes. **Amendment 3:** executed, not read: the flow source walk (all four Dataverse writes in the two flows are flat; 0 nested writes across the 10 flows), the retired-route word search over `src/`, `provisioning/`, `config/` and `scripts/` (it does reach the test data, so the miss was in reading the hits, not in where the search looked), the V4 wording search inside the engine, with a positive control (7 places), the override count in the routing log (3 of 3 DEV overrides since 25 September give "closes only by the deploy" as the reason), log times against file times (3 more future-dated findings), and the disposition simulated a fourth time (exit 0, 0 unread). **Not verified:** none of rows 31–40 is written. Nothing live was read by this amendment; the live readings are pipeline-agent's and lead-agent's. Whether a designer save now leaves the three record steps intact has not been observed, because nobody has saved the flow since the deploy. **Amendment 4:** executed, not read: the timeout script's self-test (6 of 6, exit 0) and its two-branch message read at source (the Keychain line sits only in the no-stray branch); the Create Envelope action order walked from the flow source (reminders, then send, then the record write; no `phoneNumber` parameter, only a description saying why); the TAD searched for a re-issue route (none) and for the corrected one-call-per-signer row (present); `testResults.xml`'s history (added once, rewritten in three commits) and its readers (none: the test runner writes `pester-results.xml` elsewhere, and CI names neither); log stamps against file times (3 more instances, one of them a new shape: pipeline lines in UTC); the derived-count gate (the same 8 drifts as Amendment 3, none new); and the disposition simulated a fifth time, in two variants (exit 0, 0 unread). **Not verified:** none of rows 41–48 is written. Nothing live was read; R1–R6, M4 and M6 are yours.

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

**Amendment 2 scope (2026-10-01, after the trustee-portal-design-2 DEV deploy, [pipeline.log L275–L284](logs/pipeline.log#L275)).** The 30 entries unread at dispatch: IMP-0979 (left for this batch by Amendment 1) and IMP-0980 to IMP-1008. Plus IMP-1009, logged by this amendment from its own measurement, and IMP-0500: reviewer-deferred, but its approved return condition ("three build manifests carry a conforming `warnings_detail[]`") was executed and is met by 58 of 80 manifests, so it is due, as IMP-0954 was. This amendment extends the parked batch review rather than opening a second one.

**Amendment 2 exclusions.** Unchanged from above: IMP-0934 (governance blocker) and IMP-0855 wait on their own reviews; IMP-0963 and IMP-0966 on review 2026-09-30; IMP-0298's warning on a review parked since 2026-08-28; IMP-0879, IMP-0906 and IMP-0824 are reviewer-deferred with conditions not met. Not re-read: IMP-0385 and IMP-0510 (reviewer-deferred, read only for the duplicate check, §2).

**Amendment 2 departures from the findings' own proposals, each forced by a measurement:**
- **IMP-0983** proposed recording the two readings side by side as an open question. IMP-1008 settles it: the 23 August read saw the reviewer's manual add of 22 August, not the push. Row 15 records the settled answer with the evidence, and keeps the existing warning, which was right.
- **IMP-1008**'s config proposal is routed, not applied here. The three notes sit in a file owned by pipeline-agent and development-agent, and their correction cites a live measurement this session cannot repeat.
- **IMP-0991** proposed a missing-reference check. A mechanical version was measured first: over the 40 HTML files in `Designsystem/`, a naive resolver reports 16 missing references, of which 6 to 10 are real (three are present as `.jsx.txt` renames, and four "missing" in the newer copy exist elsewhere in the same drop). That is too low to wire, so it is a checklist step (row 18), with the renaming and root-relative cases named.
- **IMP-0984** proposed bringing into scope any drop whose README names an app. Row 19 is simpler and value-only: every top-level folder under `Designsystem/` must be cited by its root path. Measured: 3 drops, 0 findings today; against the TADs as they stood before the Design 2.0 TAD was written, 2 findings, both true.
- **IMP-0992**'s collision rule measures 1 finding today, and it is true: the tracked copy's `ui_kits/trustee-review-portal` is cited only by its two-component key, and the identical untracked copy makes that key ambiguous. Wiring it today would turn a HARD step red over a question only the reviewer can answer, so it is held on decision 5.
- **IMP-0980** suggested a static check for ordering comparisons on a raw column. Measured over all flow source: 1 such comparison exists (`maxAge` in the intake flow's age-band map), and its seeded data never holds an empty value (the top band is 200). 1 finding, 0 true today, so it stays a knowledge line.
- **IMP-0989** proposed a warning on every gate run that reads the baselines. Six gates load them (`load_baselines`, measured), so that would print each warning up to six times per build. Row 25 prints it once, from the build preflight.
- **IMP-0990** named two misses. The register corpus has more: 11 rows the gate never parsed, with ids `A-ATYPE-1`, `A-RESULT-1`, `A-G01` to `A-G04`, and bold ids. Row 24 widens the grammar to all of them, measured at 0 new failures.
- **IMP-0994** also proposed a warning when an acceptance is relinked and the title is not. 26 of the 51 Design 2.0 items were relinked, most correctly keeping their titles, so the warning is not proposed; row 23 adds only the `--title` option the fix needs.
- **IMP-0998** proposed splitting stylesheet tests into contract and presentation halves. The reviewer has since decided otherwise (answer R19: rewrite `layout.test.ts` in both apps and keep it a contract test), so it is REJECTED as superseded.
- **IMP-1000** proposed gitignoring `build/fidelity/`. Not adopted: fidelity screenshots belong in the session scratchpad, which is where the agent put them. The lesson (check a brief's "gitignored" with `git check-ignore`) stays in the record, and the class it belongs to is `dispatch-brief-asserts-unverified-fact`.
- **IMP-1004** proposed a new `retrace` event. Row 13 is revised to an option on the existing `reopen` instead, the same shape as the deferred-resume case it already handles: one schema, and both cases fixed by one rule ("Reopens counts rejections only").
- **IMP-1006** proposed building the warning-row check now. Its input exists (IMP-0500's condition is met), but the check as designed measures badly: only 37 of 261 recorded warning signatures appear word for word in their own feature's Dev Summary. It needs a design, not a script (C24).

**Amendment 3 scope (2026-10-02, after the DEV deploy of build 20261002-1, [pipeline.log L285–L290](logs/pipeline.log#L285)).** The 8 entries unread at dispatch: IMP-1010, IMP-1011, IMP-1014 to IMP-1019. Plus IMP-1020, logged by this amendment from its own measurement (the V4 wording, C27). IMP-1012 and IMP-1013 are not here: the capability review [2026-10-02](docs/improvements/2026-10-02-improvement-review.md) processed and applied them today. That review's applied note names IMP-1014 to IMP-1016 only to say they arrived after its draft; it did not process them, so they are this batch's.

**Amendment 3 exclusions.** Unchanged: IMP-0934 (governance blocker) and IMP-0855 wait on their own reviews; IMP-0963 and IMP-0966 on review 2026-09-30; IMP-0298's warning on a review parked since 2026-08-28; IMP-0879, IMP-0906 and IMP-0824 are reviewer-deferred with conditions not met. IMP-0959 is `APPLIED` and is not reopened; C27 records what IMP-1010 adds to it.

**Amendment 3 departures from the findings' own proposals, each forced by a measurement:**
- **IMP-1010** proposed four things, and two are already done in source by the dispatch that logged it. (1) All four Dataverse writes in the intake and failure-alert flows are flat today (walked: 16, 20, 81 and 8 flat keys, none nested), and the deploy re-read them live with 0 differences ([L289](logs/pipeline.log#L289)). (2) The "no nested `item`" check exists as a test inside the HARD unit-test step ([ScoringInvariants L1469](src/tests/solutions/ScoringInvariants.Tests.ps1#L1469)), so no new gate is proposed. (3) Running the live re-read before a deploy is routed, not applied: its DIFFERS check compares against current source, so before a deploy it would report every intended change. Only its MODIFIED check means "written after the last import", and the script has no mode that runs that alone. (4) is row 34.
- **IMP-1010's lesson ("never save a solution flow in the designer") contradicts this system's own V4 definition**, which requires the save in seven places (measured, C27). The lesson is not adopted as written, because V4 exists for a measured reason: three of the fifteen founding failures imported cleanly and could not be saved. Rows 31–35 keep the save and add what must follow it. Logged as IMP-1020.
- **IMP-1017**'s root cause, that the retired-route word search "did not cover test-data run instructions", is false. Executed: one of IMP-1015's own words, the double-slash scope, matches [intake-payloads.json L12](src/tests/data/intake-payloads.json#L12), and `src/tests/data/` is under `src/`, which that search covered. The miss was in reading the hits: the same word matches 7 other lines (8 in all), which are kept on purpose as history ("SUPERSEDED … retained so the change is visible") or are tests asserting the old value is gone, and the stale one looked like them. So row 39 asks for every hit to be listed with what happens to it, which makes an unhandled one visible to whoever reads the list.
- **IMP-1015** proposed a `skill` change targeting `agents/architect-agent.md`. It lands as an agent-file edit (row 39), in the section that gave the build config as the source of the list ([L106](agents/architect-agent.md#L106), from IMP-0472). That instruction caused this narrowing: the TAD's rev 14 list says it was taken "from `config/revitalise-grant-automation-build.yml` and the pipeline config".
- **IMP-1014**'s second suggestion, measuring whether the connector's dynamic-schema call returns flat key names, is not adopted. You settled the question in a few minutes in the designer ([routing L1241](logs/routing.log#L1241)), the skill already says a dynamic parameter has no route except a person in the designer ([L88](skills/how-to-verify-a-platform-contract.md#L88)), and nothing has needed it a second time.
- **IMP-1019** proposed amending C-TECH-058 directly. It removes a human approval step for one class of DEV deploy, so it is offered as decision 6, not drafted as a row the keyword alone would approve. The measurement backs it: 3 of 3 DEV overrides since 25 September give the reason "closes only by the deploy".
- **IMP-1018** proposed a provisioning-script change. Provisioning scripts are delivery work, not this agent's to write. Routed.

**Amendment 4 scope (2026-10-03, after the DEV deploy of build 20261003-2, [pipeline.log L291–L298](logs/pipeline.log#L291)).** The 12 entries unread at dispatch, IMP-1021 to IMP-1032, all from the Create Envelope rework (`wbs:3.2`) and its two blocked builds. Census at dispatch, re-measured: 12 unread, 0 fixed-in-flight, 0 deploy-lane blockers open. No entry was logged by this amendment: its one new measurement (pipeline lines stamped in UTC) is an instance of C1, recorded there.

**Amendment 4 exclusions.** Unchanged: IMP-0934 (governance blocker) and IMP-0855 wait on their own reviews; IMP-0963 and IMP-0966 on review 2026-09-30; IMP-0298's warning on a review parked since 2026-08-28; IMP-0879, IMP-0906 and IMP-0824 are reviewer-deferred with conditions not met. IMP-0217 is `APPLIED` and is not reopened; C36 records what IMP-1032 adds to it.

**Amendment 4 departures from the findings' own proposals, each forced by a measurement:**
- **IMP-1021, IMP-1023 and IMP-1026** proposed three separate skill edits, in two places. They share one class and one property (what a designer-saved flow proves), so row 41 is one paragraph in one place. IMP-1021's second half, "enumerate the connector's whole action list for a dedicated action", is already the skill's catalogue rule ([L258](skills/how-to-verify-a-platform-contract.md#L258), from IMP-0620) and is not repeated.
- **IMP-1025** proposed amending ADR-067 D6/E2. The architect already did: the row is corrected in place to "one call per signer" ([TAD L3366](docs/architecture/revitalise-grant-automation-architecture.md#L3366), [L3387](docs/architecture/revitalise-grant-automation-architecture.md#L3387)), and the `tabType` string is an open register row ([A-DS-16 L3855](docs/architecture/revitalise-grant-automation-architecture.md#L3855)). Nothing is routed. Its general lesson (an action's body shape is taken from the designer-saved definition, never from the reference) is row 41's.
- **IMP-1022** proposed a knowledge page of DocuSign facts. Adopted narrower: the measured facts already live in TAD ADR-067 with their evidence levels, so row 43 gives the boundary in four lines and points there instead of copying a table that will be revised. Its negative claims ("no connector action exposes `allowReassign`") are E2 in the TAD ([L3431](docs/architecture/revitalise-grant-automation-architecture.md#L3431)) and stay E2 here; this review could not re-scan the connector catalogue. The design lesson (list what only the service's template or account enforces) goes to the design skill (row 42), where an architect looks before designing, not after.
- **IMP-1028** proposed only a route to architect-agent. Routed, and row 42 adds the general check, because the gate that caught the shipped wording ([verify-shipped-content.py check 7 L716](scripts/verify-shipped-content.py#L716)) reads shipped text, never the TAD's risk table.
- **IMP-1031** proposed only a TAD route. Routed, and row 44 extends the skill row that IMP-0615 wrote: role names come from the template, and so does the field set. That row is the applied prior change this finding recurs against (§1).
- **IMP-1032** is filed under `gate-defect`. It is the second instance of IMP-0217's misdiagnosis, which is filed under `platform-contract-guessed-not-groundtruthed`, so the class count understates it. Treated as a recurrence after a prose fix: review 16 corrected the knowledge page and left the script's own message saying "the usual cause", and the script's message is what an agent reads at the moment of the hang. Its proposal is adopted as written (row 45), plus the knowledge step (row 46). No build-agent rule: both BLOCKED reports repeated the script's word.
- **IMP-1030** proposed waiting for a second instance before untracking `testResults.xml`. Measured: the file was added on 26 August and rewritten in three later commits (`git log --numstat`), and nothing reads it ([Invoke-Tests.ps1 L103](src/tests/Invoke-Tests.ps1#L103) writes `pester-results.xml` elsewhere; CI names neither). The second instance has already happened, so row 48 adopts it now.
- **IMP-1027** suggested a shared line-anchored replace helper on a second instance. One instance; not adopted.
- **IMP-1029** is a capability with no `capability: true` field, so the digest renders it as an ordinary lesson. Row 47 sets the field, which is what the ladder's capability row asks for, and names the helper in the knowledge page. Held: the helper is untracked.

**Amendment 1 (2026-09-30, after build 20260930-4).** *Folded in:* IMP-0973 to IMP-0978, with `reviewed_in` stamped on all six. That adds clusters C10–C13 and extends C1 with IMP-0974 and two new measured future stamps. It adds rows 11–13, and row 14 on the new decision 3. It adds one regression row (§12c), dispositions for all six, four routed items, and a re-measurement that narrows row 8's cutoff. The gate block, header, summary, simulation and digest table were reconciled first. *Still to do:* nothing in this document. Everything waits on the keyword and the three decisions. Rows 6–7 and the WI-0005 files still wait on lead-agent's commit. *Not folded in:* IMP-0979, appended during this dispatch. It goes to the next batch.

**Amendment 2 (2026-10-01, after the trustee-portal-design-2 DEV deploy).** *Folded in:* the 30 entries unread at dispatch (IMP-0979 to IMP-1008), each stamped with `reviewed_in`; IMP-1009, logged by this amendment; and IMP-0500, a reviewer-deferral that is due. That extends C1, C11 and C12, and adds clusters C14–C26. It revises row 13 (generalised on its second instance) and adds rows 15–30, decisions 4 and 5, six regression rows, 32 dispositions, seven routed items and a third simulation. The gate block, header, summary, digest table and derived-count note were reconciled first. *Still to do:* nothing in this document. Everything waits on the keyword and five decisions; rows 6–7 and the WI-0005 files still wait on lead-agent's commit, and row 19(b) on decision 5. *Not folded in:* nothing; the queue had 0 unread entries after the stamps (measured).

**Amendment 3 (2026-10-02, after the DEV deploy of build 20261002-1).** *Folded in:* the 8 entries unread at dispatch (IMP-1010, IMP-1011, IMP-1014 to IMP-1019), each stamped with `reviewed_in`, and IMP-1020, logged by this amendment. That extends C1 with three measured instances, and adds clusters C27–C32, rows 31–40, decision 6, six regression rows, nine dispositions, six routed items (one of them a withholding), and a fourth simulation. The gate block, header, summary, digest table and derived-count note were reconciled first; `verify-review-document.py` passes on this file. *Still to do:* nothing in this document. Everything waits on the keyword and six decisions; rows 6–7 and the WI-0005 files still wait on lead-agent's commit, row 19(b) on decision 5, row 40 on decision 6. *Not folded in:* nothing; the queue had 0 unread entries after the stamps (measured).

**Amendment 4 (2026-10-03, after the DEV deploy of build 20261003-2).** *Folded in:* the 12 entries unread at dispatch (IMP-1021 to IMP-1032), each stamped with `reviewed_in`; no entry logged by this amendment. That extends C1 with three measured instances (one in UTC), and adds clusters C33–C38, items 28–33, rows 41–48, six regression rows, twelve dispositions, five routed items and a fifth simulation. The gate block, header, summary, closing verification line and digest table were reconciled first. *Still to do:* nothing in this document. Everything waits on the keyword and the same six decisions; rows 6–7, row 47 and the WI-0005 files wait on lead-agent's commit, row 19(b) on decision 5, row 40 on decision 6. *Not folded in:* nothing; the queue had 0 unread entries after the stamps (measured).

---

## 1. Regression check — did the last review's changes work?

The last review applied is [2026-09-29](docs/improvements/2026-09-29-improvement-review.md), applied 06:35 today. [Review 2026-09-30](docs/improvements/2026-09-30-improvement-review.md) was approved later but applied only a digest line count; its six changes are held, so there is nothing of it to audit yet.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| 09-29 change 1: re-read a flow's live definition after an import | 2026-09-30 | `async-flow-postimport-plugin-fails-silently` | NO. Promoted by the reviewer to `verify-live-flow-definitions.py`, which ran in this deploy: 10 of 10 flows, 0 differences ([L247](logs/pipeline.log#L247)) | Working; now a script |
| 09-29 change 2: import takes 4–6 minutes, wrapper ≥ 600 s | 2026-09-30 | `client-timeout-misread-as-write-failure` | NO. 900 s wrapper, import 3 m 48 s, publish 36 s, no client-side timeout ([L244](logs/pipeline.log#L244)) | Working. IMP-0954 closes on it |
| 09-29 change 3: `pac` times are UTC; take log times from `date` | 2026-09-30 | `log-timestamp-not-taken-from-the-clock` | **YES, at least 10 times in 12 hours, by 5 agents across 3 logs** (§2, C1). **4 more since the draft**, across 2 logs (amendment). **And again by Amendment 2:** lead-agent's five routing lines stamped 00:20 to 01:05 when the clock read about 22:56, up to 2 h 9 min ahead ([L1183–L1188](logs/routing.log#L1183); its own correction at [L1189](logs/routing.log#L1189) names four of them), and an architect-agent line stamped 23:59 that precedes one stamped 22:46 ([L1182](logs/routing.log#L1182)); build-agent's two lines stamped 11:32 and 12:05 in a `build.log` last written at 11:06:34 ([L156–L157](logs/build.log#L156)); IMP-1007 stamped 12:00 and appended before IMP-1008, stamped 11:45 | **Wrong altitude.** A prose line nobody reads at the moment of writing. Escalated to the tools (rows 1–5) |
| 09-29 `fixes` field warning | 2026-09-29 | `two-recorded-lessons-contradict-each-other` | Exercised again: the gate warned "IMP-0961: fixed by IMP-0962, and no review has processed it" | Working. It put IMP-0961 here |
| 09-30 digest line-count correction | 2026-09-30 | `hand-maintained-count-drifts-from-source` | NO. Digest is still 606 lines after this review's three appends, and after the amendment | Working |
| *(amendment)* review 2026-09-22-4: verify skill §12c (open the supplied document, check it page by page) and a development-agent trigger row that loads it | 2026-09-23 | `no-assertion-on-shipped-content` | **YES.** The next pass on the same screen (Revision 14, committed 09-26) says it checked "against the PDF p.1 directly", and compared section order only. Raised again 09-30 (C10) | **Right idea, wrong instrument.** Opening the document was done; the check it produced was still section-level. Row 11 names the row-by-row test, and decision 3 offers the ledger check |
| *(Amendment 2)* review 2026-08-23-4: "a pushed Code App IS a solution component", into the main TAD §9.3 and three pipeline-config notes | 2026-08-23 | `platform-contract-guessed-not-groundtruthed` | **YES — the lesson itself was wrong.** The first push of a second app reproduced the August 22 negative (IMP-1008). The 23 August read saw a manual add made the day before | **Closed at the right level (V3), on the wrong cause.** Nobody compared the component's creation time with the push. Row 15 records the test that separates them; the config and TAD corrections are routed |
| *(Amendment 2)* review 2026-08-31: `C-TECH-075` and `verify-design-source-coverage.py` | 2026-08-31 | `input-type-with-no-owning-agent` | **YES, three times** (IMP-0984, IMP-0991, IMP-0992). The gate ran and passed: scoped to folders named after an app, it never saw `Design-2.0/` | **The gate ran and was mis-scoped** (a `gate-scope-mismatch` finding is already logged, IMP-0984). Rows 19–20 re-scope it; row 18 covers what no gate can |
| *(Amendment 2)* review 2026-08-28-3: accessibility checklist §1.4a (recompute a supplied palette) | 2026-08-28 | `supplied-design-asset-assumed-wcag-compliant` | **YES, twice** (IMP-0985, IMP-1001), **and caught both times** before anything shipped: the TAD recomputed the 4.49:1 pink, the build kept the 320 px reflow | **Working.** Row 18 adds the 320 px render the rule did not ask for |
| *(Amendment 2)* review 2026-09-18-2: IMP-0764 closed on a needle in a `blocked_on` note's wording | 2026-09-18 | `serialisation-default-invalidates-evidence-needle` | **YES** (IMP-1007): check 14 forced the note to be rewritten, and the needle broke the HARD log gate | **Wrong needle, not wrong rule.** Row 29 adds the rule to the needle list; 1 of the 4 needles in the pipeline config was exposed (measured) |
| *(Amendment 2)* review 2026-09-26-6: a deploy record must match the component's own command (IMP-0910) | 2026-09-26 | `wrong-artefact-cited-as-evidence` | **YES** (IMP-0986): two Code Apps share the command, so the first app's push discharged the card app's 51 items (executed) | **Right rule, one level too low.** Row 16 takes it from "an import is not a push" to "one app's push is not another's" |
| *(Amendment 2)* review 2026-08-30: IMP-0500 deferred until three manifests carry `warnings_detail[]` | 2026-08-30 | `untriaged-tool-warning` | Not a recurrence. The condition came true (58 of 80 manifests) and nothing said so (IMP-1009), while IMP-1006 re-proposed the same gate | **Due.** Annotated, not built: the check as designed measures 37 of 261 (C24) |
| *(Amendment 3)* review [2026-10-02](docs/improvements/2026-10-02-improvement-review.md), the last review applied (today): reviewer verdicts on the work board | 2026-10-02 | `evidence-recorded-but-not-surfaced` | NO. None of the 9 entries in this amendment is in that class or touches the ledger or the board | Working, too early to say more |
| *(Amendment 3)* 09-29 change 1, now `verify-live-flow-definitions.py` | 2026-09-30 | `async-flow-postimport-plugin-fails-silently` | **YES, in a new shape** (IMP-1010). The script ran and was right twice: 0 differences on 1 October ([L283](logs/pipeline.log#L283)) and on 2 October after the fix ([L289](logs/pipeline.log#L289)). The designer save came between them, and the script runs only after an import | **The gate ran, and its moment was too narrow.** Pre-deploy and pre-test use routed (C27) |
| *(Amendment 3)* 09-29 knowledge step 4: close a designer tab before an import; designer save "not proven" | 2026-09-30 | `finding-diagnosis-unverified` | **YES** (IMP-1010). A later, deliberate save did what an open tab was suspected of. The prose covered one shape | **Recurred after a prose fix → mechanical defence**, already in source: flat writes and the nested-`item` test (HARD unit tests). Row 34 corrects the prose; rows 31–35 cover the save the system itself asks for |
| *(Amendment 3)* review 2026-08-28: architect lists an ADR's gate interactions from the build config (IMP-0472) | 2026-08-28 | `platform-contract-guessed-not-groundtruthed` | **YES** (IMP-1015, IMP-1017). Followed exactly, and the rule's own source was the cause: a decision is written mostly into tests, fixtures and settings, which are not build steps | **Right idea, too narrow a source.** Row 39 widens it for a re-decided ADR |
| *(Amendment 3)* C-TECH-058, OPEN assumptions block a deploy (from IMP-0014) | August | `assumption-shipped-open` | **Not a defect recurrence**, but the rule meets one case every time: 3 of 3 DEV overrides since 25 September give "closes only by the deploy" as the reason | **Working as written; the wording costs a message per DEV deploy.** Decision 6 |
| *(Amendment 3)* C1, the log-time rows 1–5 (still unapplied) | — | `log-timestamp-not-taken-from-the-clock` | **YES, again**: IMP-1017, IMP-1018 and IMP-1019 are stamped 15:00 and sit in a log last written at 13:58:47, about an hour ahead, all through the allocator | **Each day the draft waits costs more instances.** No new row; rows 1–5 fix it on the keyword |
| *(Amendment 4)* C1 again | — | `log-timestamp-not-taken-from-the-clock` | **YES, three more, one in a new shape.** Pipeline-agent's eight DEV lines for build 20261003-2 are stamped 09:11–09:23, which is UTC: lead-agent routed the deploy at 11:10 local and received it at 11:23 ([routing L1295](logs/routing.log#L1295), [L1297](logs/routing.log#L1297)), and the file was last written at 11:23:04 ([pipeline L291–L298](logs/pipeline.log#L291)). Build-agent's success line is stamped 09:58 in a `build.log` last written at 09:46:48 ([L161](logs/build.log#L161)). IMP-1032 is stamped 09:50 in a log last written at 09:45:36 | **Same verdict.** Rows 1–2 take the local clock, which settles the UTC shape too |
| *(Amendment 4)* IMP-0614, IMP-0882 and IMP-0620: the verify skill's dynamic-parameter and connector-catalogue rules | 2026-09-08, 2026-09-25 | `platform-contract-guessed-not-groundtruthed` | **YES, four times on one flow** (IMP-1021, IMP-1023, IMP-1025, IMP-1026). The rules were followed: you ran the designer step and saved the flow. What was misread was the saved flow itself | **Right rule, one case short.** It says what a designer error means, not what its silence means. Row 41. No gate: nothing here can read a connector's dynamic schema ([L92](skills/how-to-verify-a-platform-contract.md#L92)) |
| *(Amendment 4)* IMP-0615: a template's role names come from the template, not a requirement document ([§2 L120](skills/how-to-verify-a-platform-contract.md#L120)) | 2026-09-08 | `platform-contract-guessed-not-groundtruthed` | **YES, next door** (IMP-1031): the role names were right this time; the tab set was taken from an earlier design | **Right rule, too narrow.** Row 44 widens it from names to the field set |
| *(Amendment 4)* Review 16: the knowledge page's correction that a stray `pac` was not the cause (IMP-0217) | 2026-08-23 | `platform-contract-guessed-not-groundtruthed` (IMP-1032 is filed as `gate-defect`) | **YES** (IMP-1032): two blocked builds, a kill that changed nothing, then the Keychain prompt. The page was right; the script's own message still said "the usual cause" | **Recurred after a prose fix → the tool.** Rows 45–46 |
| *(Amendment 4)* IMP-0139: shipped prose promises nothing the solution cannot do (check 7) | August | `shipped-prose-promises-unbuilt-capability` | Exercised: it failed "Correct it and re-run" on the first run (IMP-1028), and the wording was fixed in the same dispatch | **Working.** Its reach stops at shipped text; row 42 covers the design |
| *(Amendment 4)* Review 2026-09-28: guards and fallbacks are tested with the input that triggers them | 2026-09-29 | `no-assertion-on-shipped-content` | **NO.** IMP-1029 is that rule being made executable: a test helper that runs the flow's own guard expressions; a mutation back to the old access-code expression failed 8 tests | **Working.** Row 47 names the helper |

**Changes whose class recurred after a *prose* fix:** 09-29 change 3 → rows 1–5. *(Amendment)* 09-23 §12c → row 11, plus row 14 if decision 3 is yes. *(Amendment 2)* 09-29 change 3 again → still rows 1–5, with build-agent's and lead-agent's new instances; 08-23-4's knowledge lesson → row 15; 09-18-2's needle → row 29. Not the last review applied, but it is the prior change this amendment's main finding tests, so it is audited. *(Amendment 3)* 09-29 knowledge step 4 → rows 31–35 and the defence already in source; 08-28 IMP-0472 → row 39; 09-29 change 3 (log times) again → still rows 1–5. *(Amendment 4)* the dynamic-parameter rules → row 41 (prose again, because no instrument here can read a dynamic schema); IMP-0615's row → row 44; review 16's stray-`pac` correction → rows 45–46, moved from the page into the script's own message; 09-29 change 3 again → still rows 1–5.
**Changes whose class recurred after a *gate*:** *(Amendment 4)* none; the one gate this amendment's findings touched (shipped-content check 7) fired on its first run and the wording was fixed. *(Amendment 3)* one more: `verify-live-flow-definitions.py` ran and was right, but only after imports, and the designer save fell between two runs (routed, C27). *(Amendment 2)* two. `verify-design-source-coverage.py` ran and passed while mis-scoped (rows 19–20). The deploy-record command rule worked as written and was not specific enough (row 16). Before Amendment 2: none. Nearest case: IMP-0971 is a recurrence of a class after its gate was *built*. The gate is invoked by instruction, the dispatch that skipped it was never routed through lead-agent, and the build's history audit is warn-only by design. Recorded, not re-escalated (C7).
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

*Amendment 2 extends three clusters above and adds C14–C26.*

- **C1 gains IMP-0996** (class now x5 by `class_instance_of`). Its proposal, `$(date …)` typed inline in lead-agent's example, is the prose form that has now failed five times; rows 2–3 already give lead-agent's two format blocks the helper instead, so no row is added. New measured instances are in §1. Agents seen typing future times now include build-agent and architect-agent, both of whose format blocks row 3 already covers.
- **C11 gains IMP-0979** (`no-assertion-on-shipped-content`, V4). The pack sub-headings lost their top margin to a `:first-child` reset; fixed in source (`.detailGroup + .detailGroup`), WI-0008 is at deployed:dev waiting for you. The general lesson goes to the Code App styling notes (row 27). DEFER on your verdict.
- **C12 gains IMP-1004 and is generalised** (two instances now: a resume from `deferred` and a test-rewrite re-trace, both counted as rejections). The property: *Reopens counts rejections, and nothing else*. Row 13 is revised to cover both; its earlier narrow form is superseded, not kept beside it (the altitude rule forbids a second instance patch).

```
CLUSTER C14: platform-contract-guessed-not-groundtruthed — Code App push does not add the app to a solution
            (x2 in scope: IMP-1008, which corrects IMP-0223, and IMP-0983, class two-recorded-lessons-
            contradict-each-other)
Altitude:   INSTANCE, settled live. Three readings exist: 22 Aug push → absent (IMP-0185); 23 Aug read →
            present (IMP-0223, credited to the push); 01 Oct first push of a second app → absent in any
            solution, no canvasapp row, after a re-push too (pipeline.log L279, L281). The first app's
            solution component post-dates its canvasapp by four hours, matching the 22 Aug manual add
            (IMP-0193). The knowledge page's warning was right; the 23 Aug lesson and the notes built on it
            were wrong about the cause
Ladder row: "a capability was established and could be lost again" does not fit; "one instance, general
            cause, a human needs it" → knowledge, plus the corrections routed to their owners
Becomes:    row 15. Routed: three pipeline-config notes, the main TAD §9.3, the Design 2.0 TAD A-TR-15
            and R-D2-4, and your maker-portal add
Retires:    nothing. IMP-0223 stays APPLIED as history; the digest already flags it CORRECTED by IMP-1008
Cites:      IMP-1008, IMP-0983
Residual:   whether a solution-member Code App survives the managed export into Test/Acceptance has
            still never been observed (the notes say so, correctly)
```

```
CLUSTER C15: wrong-artefact-cited-as-evidence — one app's push discharges another app's items
            (x1: IMP-0986; class x10 with IMP-0910)
Altitude:   CLASS. Strip this client and it holds: "a deploy record resolves only on a marker naming the
            component it delivers". Executed: deploy_markers gives one literal, `pac code push`, for the
            label `operation:code-app-push` in DEV; three DEV entries carry that operation; the first
            matching line for all 51 card-app records is L277, the first app's push. ENGINE-level
Ladder row: "a tool could catch it mechanically", and a second shape of IMP-0910's class (generalise)
Becomes:    row 16 (labels, matcher and config check), row 17 (pipeline-agent's WRITE line names the
            folder). Dated from the apply date, as rows 8 and 14, because verify-work-items replays history
Retires:    nothing; IMP-0910's command rule stays and is extended
Cites:      IMP-0986
Residual:   the label is only as good as the folder the agent writes in the WRITE line; a line naming the
            wrong folder still discharges. The 51 existing records stay as recorded (true by L279)
```

```
CLUSTER C16: input-type-with-no-owning-agent — a supplied design bundle has no intake checklist
            (x6 in scope: IMP-0991, IMP-0993, IMP-0985, IMP-1001, IMP-0984, IMP-0992; classes
            input-type-with-no-owning-agent x6, supplied-design-asset-assumed-wcag-compliant x3,
            gate-scope-mismatch x29, supplied-design-content-predates-source x1)
Altitude:   CLASS — "a supplied design is intake'd against what it references, what it duplicates, what
            it claims, and how it renders, before anything is scoped from it". The intake skill has
            checklists for six source classes and none for a design bundle (grepped). ENGINE-level for the
            checklist; the gate scope is instance config (`SUPPLIED_ROOTS`)
Ladder row: third-plus instance of input-type-with-no-owning-agent → C-TECH-075 exists, so its
            amendment (row 20) rather than a new row; "a tool could catch it" for the scope half only
            (row 19); the rest is judgement → the checklist (row 18)
Becomes:    rows 18, 19 (second half on decision 5), 20
Retires:    nothing. C-TECH-075's name-match clause is widened, not removed
Cites:      IMP-0991, IMP-0993, IMP-0985, IMP-1001, IMP-0984, IMP-0992
Residual:   (1) the missing-reference check stays manual (measured too imprecise to wire, §0). (2) The
            CI checkout never sees an untracked drop, so CI and a local run judge different trees until
            decision 5 is answered. (3) A README's contrast claim is still only re-computed when the TAD
            restates it (verify-design-doc-claims reads docs/, not Designsystem/)
```

```
CLUSTER C17: design-values-read-from-source-not-rendering — "matches the design" claimed, not measured
            (x3: IMP-0997, IMP-1002, IMP-1005; IMP-1005 names IMP-1002's class as its own)
Altitude:   CLASS — "a fidelity claim is a comparison of computed values from both renders, at every
            captured width, over a probe list generated from the design's declarations". Three passes,
            each closing the previous pass's gap and leaving the next: global stylesheet unread (Rev 1),
            29 grep-made "match" rows (Rev 2), 1280-only hand-picked probes, 17 misses (Rev 3).
            ENGINE-level; the sibling of §12c, which covers a supplied DOCUMENT
Ladder row: third instance → a constraint would need a Verify By that renders the kit, which no build step
            can do here, so it would be a comment. The skill is the most mechanical honest home
Becomes:    row 21 (§12d)
Retires:    nothing
Cites:      IMP-0997, IMP-1002, IMP-1005
Residual:   the probe script lives in a session workflow, not in the repository, so the next feature
            rebuilds it; §12d says to keep it beside the screenshots. V4 stays yours
```

```
CLUSTER C18: item-acceptance-contradicts-approved-design (x3 in scope: IMP-0987, IMP-1003, and the
            adjacent IMP-0994 ledger-title-contradicts-relinked-acceptance; plus WI-0086 and WI-0087's
            clause misses, which no finding recorded)
Altitude:   CLASS — "when a TAD or a TAD revision decides a value an item clause pins, the clause is
            amended before development, in one batch". Measured: 8 clauses in 5 items (WI-0055 c0,
            WI-0085 c1, WI-0088 c2, WI-0086 c2–3, WI-0087 c0, c2–3), amended in 4 pm-agent round trips
            after development found them (routing L1209–L1212 and 09:46). A mechanical rule keyed on
            "linked before the TAD's approval" would flag all 51 items for 5 true: 10%, not wired
Ladder row: "an agent had the information and still did the wrong thing" — the architect wrote the
            overriding ADRs and is the one agent who knows which clauses they touch
Becomes:    row 22 (architect step); row 23 (`link --title`, so a reversed title can be corrected)
Retires:    nothing
Cites:      IMP-0987, IMP-1003, IMP-0994
Residual:   a fidelity brief that overrides a TAD (IMP-1003's shape) still depends on lead-agent routing
            the change through architect-agent first; development-agent's handling (implement, keep the
            item reopened, raise the TAD row) was correct and needs no rule
```

```
CLUSTER C19: gate-cannot-fail — assumption-register rows the gate cannot parse  (x1: IMP-0990; class x52)
Altitude:   INSTANCE, value-only. Measured over the 13 register documents: 11 rows invisible to the gate
            (digit or 5–6-letter prefixes, a prefix with no hyphen, bold ids); with the wider grammar 97 →
            108 rows read, 0 new failures, 1 new note, true (A-G03 is open and names no location)
Ladder row: "a tool could catch it mechanically" — the tool exists and is HARD; widen its grammar
Becomes:    row 24
Retires:    nothing
Cites:      IMP-0990
Residual:   a register row whose first cell is prose ("A-INT-10 marker comment") stays unread, correctly
```

```
CLUSTER C20: gate-baseline-expires-without-owner-action  (x1: IMP-0989)
Altitude:   INSTANCE, mechanical, and the precedent exists: check 14's four-day warning (IMP-0585). Eight
            baselines expired together on 30 September; renewed 1 October on your instruction; twelve now
            expire on 13–14 October
Ladder row: "a tool could catch it mechanically"
Becomes:    row 25 (warning once per build, at the preflight)
Retires:    nothing
Cites:      IMP-0989
Residual:   a warning is not a decision; renewals still happen in a batch on the day
```

```
CLUSTER C21: ledger-has-no-billing-status-field  (x1: IMP-0982)
Altitude:   NOTE plus one agent-file line. The decision is recorded twice (EX-008, CE-0012/13) and read by
            nothing: commercial-agent's file never names either (grepped), and verify-worklog reads no
            billing-decision event. `wbs:6.3` holds billable contracted work too, so a wbs-keyed check would
            be wrong, and worklog sessions name no items today
Ladder row: commercial design → decision 4
Becomes:    row 28 (commercial-agent reads the recorded decisions). The mechanical half waits on decision 4
Retires:    nothing
Cites:      IMP-0982
Residual:   until decision 4, the only defence is an instruction
```

```
CLUSTER C22: Power Automate expression behaviour  (x2: IMP-0980 null-operand-in-ordering-comparison-
            throws, V5; IMP-0981 solution-source-edited-outside-dispatch, V1)
Altitude:   NOTE + knowledge. Two platform facts a human needs: ordering comparisons throw on an empty
            value where `equals()` does not; `string(<boolean>)` gives `True`/`False`. IMP-0981's governance
            question (a lead-agent check comparing uncommitted solution edits with routing.log) is not
            adopted: a dispatch is a prompt, not a file, so there is nothing to compare reliably, and the
            source gates did catch the edit at the next run
Ladder row: one instance each, general cause → knowledge
Becomes:    row 26
Retires:    nothing
Cites:      IMP-0980, IMP-0981
Residual:   the only raw ordering comparison left in flow source is safe only because its seeded data
            has no empty value (measured)
```

```
CLUSTER C23: a second Code App exposes latent defects in the first  (x2: IMP-0999, IMP-0988)
Altitude:   NOTE, delivery work. The first app's `.tableScroll` has no `position` (measured,
            app.module.css L303), the card app's has; both apps start their harness on port 4173 with
            local reuse on. Both are fixes in source, not rules
Ladder row: one instance each → knowledge line for the CSS (row 27); both fixes routed
Becomes:    row 27 (with IMP-0979); routed to development-agent
Retires:    nothing
Cites:      IMP-0999, IMP-0988
Residual:   the first app's tables are unmeasured at 320 px with their sort hints present
```

```
CLUSTER C24: untriaged-tool-warning, and a deferral nobody re-checked  (x3: IMP-1006, IMP-1009, plus the
            due IMP-0500; untriaged-tool-warning x21, stale-deferral-uncaught-across-sessions x8)
Altitude:   NOTE. IMP-0500's condition is met (58 of 80 manifests carry warnings_detail[]), so the input
            exists. Measured before proposing: 37 of 261 recorded signatures appear word for word in their
            own Dev Summary, and 36 entries name no file at all. A text diff would be red by construction,
            and comparing `triaged_in` reads build-agent's own answer. C-TECH-055's reading by build-agent
            worked again (it withheld the build). IMP-0500 is due, said here so a reader can grep it:
            IMP-0500 is due in this batch
Ladder row: none taken; a design question, not a defect with a known fix
Becomes:    nothing built. IMP-0500's deferred_reason is annotated with this measurement; its approved
            revisit_when stays verbatim
Retires:    nothing
Cites:      IMP-1006, IMP-1009
Residual:   each new shared-config feature can again miss a warning row for steps it did not add; the
            build catches it, at the cost of one build
```

```
CLUSTER C25: serialisation-default-invalidates-evidence-needle — a needle on rewritable wording
            (x1: IMP-1007; class x4)
Altitude:   INSTANCE + rule. Of 4 needles pointing into the pipeline config, 1 sits in a blocked_on note's
            free text (IMP-0764); the others are self-citing markers that no rule rewrites (measured)
Ladder row: "an agent had the information" — this agent writes the needles
Becomes:    row 29 (one bullet in the needle list), row 30 (IMP-0764's needle moves to
            `BLOCKED_ON_MAX_AGE_DAYS = 14`, which its own applied_by names as the defence)
Retires:    nothing. The retained 2026-09-18 history line may then go; that is pipeline-agent's call
Cites:      IMP-1007
Residual:   no check finds a needle in rewritable text; it stays a rule
```

```
CLUSTER C26: notes with no system change  (x3: IMP-0995, IMP-0998, IMP-1000)
Altitude:   NOTE. IMP-0995: the settings notes give the 19 September seed while DEV holds a later one;
            the notes file is delivery-owned, routed. IMP-0998: superseded by your answer R19, REJECTED.
            IMP-1000: the brief's "gitignored" was wrong and the agent checked; proposal not adopted
Ladder row: one instance each, no general mechanism beyond what the digest carries
Becomes:    nothing; one routed item
Retires:    nothing
Cites:      IMP-0995, IMP-0998, IMP-1000
Residual:   none new
```

*Amendment 3 extends C1 and adds C27–C32.*

- **C1 gains three measured instances and no entry.** IMP-1017, IMP-1018 and IMP-1019 carry `ts` 15:00 in a log whose modification time is 13:58:47, all appended through the allocator that row 1 changes. The class count is unchanged (these are instances of the entries' own stamps, not new findings), and no row is added.

```
CLUSTER C27: live-definition-overwritten-outside-the-pipeline — a designer save rewrites a solution flow,
            and V4 asks for one  (x2: IMP-1010, IMP-1020; IMP-0959 and IMP-0956 APPLIED, read for §3a)
Altitude:   CLASS, ENGINE-level for the V4 half. The property, with this client stripped: "a designer
            save of a solution-sourced flow is a live write that rewrites the whole definition from what
            the designer understood". Measured inside one save on 2026-10-02: the two nested Dataverse
            writes lost every column, the flat one in the same flow kept all of its columns; secureData removed;
            every inputs.authentication stripped; parameters renamed to display names; trigger mode
            added. The V4 wording that asks for the save, found by a search with a positive control
            inside .engine: skill §5 L596, pipeline-agent L476, the two templates (L96, L82); plus
            C-TECH-053 L108, build-and-deploy L199 and pipeline.yml.example L171 in this repository
Ladder row: "an agent had the information and still did the wrong thing" does not fit — the rule
            itself mandates the step. "A tool could catch it mechanically": the tool exists
            (verify-live-flow-definitions.py) and only needs to be tied to the save. The defect half
            (nested bags) is already defended mechanically in source (flat writes + the nested-item
            test, HARD unit tests), so no new gate
Becomes:    row 31 (C-TECH-053 amendment), 32 (skill §5), 33 (pipeline-agent (c)), 34 (build-and-deploy:
            step 5(c), and step 4's "not proven" replaced by the observation), 35 (templates and the
            example config), 36 (power-automate: the flat-key rule). Routed: a "modified since the last
            import" run before a deploy and before a test
Retires:    nothing. The save stays in V4; three of the fifteen founding failures were found only by it
Cites:      IMP-1010, IMP-1020
Residual:   (1) a save that happens with nobody running the re-read is still found only at the next
            deploy, until the routed pre-deploy use exists. (2) A save also drops secureData and
            inputs.authentication, which no flat-key rule protects; only the re-read and a re-import
            restore them. (3) Whether a save now keeps the three flat writes intact has not been
            observed (IMP-1010 stays open on it)
```

```
CLUSTER C28: platform-contract-guessed-not-groundtruthed — a decision closed on what an outside party was
            given, not on what its tool can do; and a "cannot be written in source" claim never re-tested
            (x2: IMP-1011, IMP-1016; class x75)
Altitude:   CLASS, ENGINE-level. Two properties, one root: an untested claim about something outside the
            repository. (a) "A route that depends on what a third party's tool can send is closed only
            when that tool has made one call, or its owner has confirmed the mechanism." The TAD had
            already written the risk as an open inference (rev 9) and converted it to "answered" on a
            credential handover (rev 10). (b) "A claim that a setting has no definition property is a
            negative platform claim, and the first live definition is the whole set." The §12 claim
            was written before any environment existed; the first live read contradicts it
            (triggerAuthenticationType, IMP-1016). §2's negative-claim rule (L204) exists; nothing
            routes a TAD claim of this kind into the first-environment sweep (§6, grepped)
Ladder row: "an agent had the information and still did the wrong thing" — skill edit
Becomes:    row 37 (§1 table gains an "outside party's tool" row; §6 gains one step)
Retires:    nothing
Cites:      IMP-1011, IMP-1016
Residual:   a claim made in a TAD and never copied into a register row is still invisible to every
            gate; the sweep step is prose
```

```
CLUSTER C29: platform-contract-guessed-not-groundtruthed — a check only a person in the designer can make,
            assigned to an agent  (x1: IMP-1014; adjacent applied IMP-0614)
Altitude:   INSTANCE + one sentence. §2 already says a dynamic connector parameter has no route except a
            person in the designer (L88, from IMP-0614). What was missing is who: the register's
            "cheapest verification" cell (L499) has no executor, so the TAD gave the step to the
            development dispatch. Handled correctly anyway: the dispatch handed it to you, you made the
            binding in about 4 minutes (TEST_Binding created 11:15 UTC, modified 11:19), and the
            conversion followed in the next dispatch
Ladder row: "one instance, general cause, a human needs to know it" → one skill sentence
Becomes:    row 38
Retires:    nothing
Cites:      IMP-1014
Residual:   the throwaway flow TEST_Binding is still in DEV (routing L1241); removing it is yours
```

```
CLUSTER C30: re-decided-adr-encoded-beyond-its-named-checks  (x2: IMP-1015, IMP-1017 — IMP-1015 names it as
            its class and files itself under stale-claim-contradicting-rechecked-source, so the digest counts x1)
Altitude:   CLASS. The property: "when a decision is re-made, every place the old decision is written is
            found by searching for its words across the repository, and every hit is listed with its
            disposition". The second instance shows the listing half matters: the search reached the
            stale fixture, and it was missed while reading 8 hits that look alike (§0)
Ladder row: "second instance → generalise" + "an agent had the information" — the agent file whose
            IMP-0472 section produced the narrow list
Becomes:    row 39. Routed: the two stale test-data instructions
Retires:    nothing. IMP-0472's build-config enumeration stays, for an ADR that specifies mechanism
Cites:      IMP-1015, IMP-1017
Residual:   choosing the retired decision's distinctive words is judgement; a word list that misses one
            misses its hits. No gate: an ADR's hit list is prose, and this repository has measured
            prose gates at 48–100% false
```

```
CLUSTER C31: gate-cannot-fail — a script accepts an environment it cannot run for  (x1: IMP-1018; class x54)
Altitude:   NOTE. One script; its sibling already documents the same limit (callback-URL check L52).
            The DEV pipeline correctly does not wire the probe, so nothing false has been reported
Ladder row: one instance, no general mechanism worth a gate; §3a found no applied entry about ValidateSet
Becomes:    nothing here; routed as a one-line delivery change
Retires:    nothing
Cites:      IMP-1018
Residual:   other provisioning scripts may accept values they cannot run for; not measured
```

```
CLUSTER C32: platform-contract-guessed-not-groundtruthed — a rule that blocks its own closing step
            (x1 finding: IMP-1019; x3 measured in routing.log)
Altitude:   INSTANCE, constraint wording. C-TECH-058 blocks a deploy into any environment where an OPEN
            assumption could be closed; when the deploy IS the closing step, the rule always needs an
            override. Measured: every DEV override since 25 September gives that reason (L943 A-DS-12/13,
            "name the DEV designer as their own closing step"; L1227 nine A-TR/A-CRD rows, "closes only
            by the first DEV push"; L1249 A-INT-11..13, "closed by the DEV import"). Adjacent class
            hard-gate-has-no-scoped-override-path x7 is about gates with NO override; this one has one
Ladder row: "a platform law, or a third instance → constraint" — the constraint exists, so an
            amendment. It removes a human approval for one class of DEV deploy, so it is decision 6
Becomes:    row 40, only on decision 6
Retires:    nothing
Cites:      IMP-1019
Residual:   the rule then depends on the register row naming its check honestly; a row that names "the
            DEV import" for an assumption that a query could close would skip the override. Test-agent
            already re-evaluates C-TECH-058 each cycle (digest), which is where that is caught
```

*Amendment 4 extends C1 and adds C33–C38.*

- **C1 gains three measured instances and no entry** (§1): eight pipeline lines stamped in UTC, one build line 11 minutes ahead, one finding 5 minutes ahead. The UTC shape is new: the 09-29 lesson ("`pac` times are UTC; take log times from `date`") was written for exactly this and did not reach the writer. Rows 1–2 stamp the local clock, which covers it; no row is added.

```
CLUSTER C33: platform-contract-guessed-not-groundtruthed — what a designer-saved flow proves
            (x4: IMP-1021, IMP-1023, IMP-1025, IMP-1026; class x80)
Altitude:   CLASS, ENGINE-level. The property, with this client stripped: "a designer-saved definition
            is E1 for the actions and parameters it CONTAINS, and for nothing it omits or implies".
            Four readings beyond that, all on one DocuSign flow in two days: (1) silence about a
            nested property read as acceptance (signers' tabs inside SendEnvelope, never filled live);
            (2) a chain of actions read as one envelope's sequence, where the third has no envelopeId
            and creates a new one (TAD L3338); (3) two actions with one body schema read as one call,
            where their addressing parameters differ; (4) cardinality taken from the reference (E2) as
            a decision basis — "one tab per call" — where the saved action takes an array per signer
            (TAD L3387); plus a parameter named after a person's attribute (phoneNumber) that is a
            delivery channel (TAD L3443). The skill states the error case (L103) and the catalogue
            rule (L258); it has no sentence on any of these four
Ladder row: "an agent had the information and still did the wrong thing" + "second instance →
            generalise": one paragraph for the class, not four rows
Becomes:    row 41 (verify skill §2, after L104)
Retires:    nothing
Cites:      IMP-1021, IMP-1023, IMP-1025, IMP-1026
Residual:   no gate: the schema exists only inside the vendor's designer (L92). All four entries close
            only on live DEV runs (R1–R3, R5), which are the reviewer's
```

```
CLUSTER C34: a flow that drives an outside service — three design checks the checklist lacks
            (x3: IMP-1024 failure-path-leaves-inconsistent-state, IMP-1028
            shipped-prose-promises-unbuilt-capability, IMP-1022 platform-contract-guessed-not-
            groundtruthed; each x1 in its own class except IMP-1022)
Altitude:   CLASS, ENGINE-level for the checklist. One property, three faces: "a flow that hands work
            to an outside service states, at design time, what state each failure leaves, how a stopped
            run is restarted, and which behaviours only the service's own configuration enforces".
            Measured against the design skill: its checklist asks "what happens at each failure point"
            (L27) and "can the workflow run twice safely" (L26), and none of the three (grepped:
            irreversib*, re-issue, external configuration). All three hit Create Envelope's rev 15
            design. The ordering defect is fixed in source (reminders L1538, send L1567, record write
            L1593 — the only step after the send). The shipped "re-run" wording is gone (0 hits);
            the restart route is not designed (TAD searched: none)
Ladder row: "one instance, general cause, a human needs to know it" ×3, landing in one existing
            checklist an architect reads before designing
Becomes:    row 42 (design checklist, three lines); row 43 (the DocuSign boundary in four lines,
            pointing at TAD ADR-067). Routed: the restart route (architect-agent)
Retires:    nothing
Cites:      IMP-1024, IMP-1028, IMP-1022
Residual:   checklist lines bind only an architect who opens the skill; the restart route stays a design
            gap until the TAD names one; the template's Required and reassignment settings are checked
            by a person (M4, M6) and by nothing in this repository
```

```
CLUSTER C35: platform-contract-guessed-not-groundtruthed (adjacent) — a template's field set taken from
            a design summary  (x1: IMP-1031, human-correction-of-agent-output; recurs against IMP-0615)
Altitude:   CLASS by extension. IMP-0615's row says a template's ROLE NAMES come from the template; the
            same reasoning applied to its FIELD SET would have listed every tab. The TAD named eight
            (§5.8 step 2, L1154); the reviewer's rule is every tab except signature, signer name and date
Ladder row: "an agent had the information" — the row exists one word too narrow
Becomes:    row 44 (the L120 row's left cell gains "or the set of fields it carries"). Routed: the TAD
            amendment (architect-agent)
Retires:    nothing
Cites:      IMP-1031
Residual:   which recipient group holds which placeholders is still unsettled by the pasted tab list
            (the finding's own caveat); the flow matches per role at run time, and R2–R3 observe it
```

```
CLUSTER C36: the timeout script names a stray pac as "the usual cause"  (x1: IMP-1032; a recurrence of
            IMP-0217, class platform-contract-guessed-not-groundtruthed; filed as gate-defect x6)
Altitude:   INSTANCE, mechanical, in the tool's own message. Read at source and executed: report_stray_pac()
            (L88–L111) prints "the usual cause (IMP-0215/0216/0226)" when it finds a pac and the
            Keychain line only when it finds none. Both causes were present on 2–3 October; the build
            log repeats the script's word (L159–L160); the kill changed nothing and the Keychain answer
            fixed it (L161). The knowledge page has said since 2026-08-23 that the two causes are not
            exclusive (build-and-deploy L423); its step 1 still ends "kill it, retry" with no
            confirming probe (L451)
Ladder row: "recurrence after a prose fix → escalate": the tool prints its diagnosis at the moment of
            the hang, so the tool's message is the mechanical home
Becomes:    row 45 (both copies, byte-identical today: cmp exit 0), row 46 (knowledge step 1)
Retires:    the phrase "the usual cause" in the script, replaced in place
Cites:      IMP-1032
Residual:   no shell probe can see a Keychain prompt (the page's own words); the script can only tell the
            agent to ask the person at the screen
```

```
CLUSTER C37: capability — a flow's guard expressions executed in a test  (x1: IMP-1029)
Altitude:   NOTE + knowledge + capability flag. The evaluator is untracked
            (src/tests/solutions/_harness/WdlExpression.psm1: `??`), and the tracked contract tests
            already import it. It evaluates if() eagerly, which the knowledge page's open if() question
            (L237) makes the safe choice, and its own header says so
Ladder row: "a capability was established and could be lost again" → `capability: true`
Becomes:    row 47, HELD until the helper is committed
Retires:    nothing
Cites:      IMP-1029
Residual:   the evaluator covers a subset; a guard using a function outside it fails "unsupported", by
            design
```

```
CLUSTER C38: notes  (x2: IMP-1027 tooling-edit-landed-in-the-wrong-place, IMP-1030
            tool-side-effect-on-tracked-file)
Altitude:   IMP-1027: NOTE, one instance, repaired in the same dispatch; the register row sits where it
            should (TAD L3853). IMP-1030: INSTANCE, and already repeated: testResults.xml added
            2026-08-26 and rewritten in 3 later commits (git log --numstat); nothing reads it
            (Invoke-Tests.ps1 writes pester-results.xml under its own output path; ci.yml names
            neither); the engine-instance classification already calls it "should probably be
            gitignored"
Ladder row: IMP-1027 none; IMP-1030 "a tool could catch it" — the ignore file is the tool
Becomes:    row 48 (.gitignore entry and git rm --cached)
Retires:    the tracked testResults.xml
Cites:      IMP-1027, IMP-1030
Residual:   a Pester run with -CI still writes the file locally; it just stops reaching commits
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
- *(Amendment 2)* IMP-1008 and IMP-0983: the three "settled (IMP-0223)" notes exist ([L1099](config/revitalise-grant-automation-pipeline.yml#L1099), [L1936](config/revitalise-grant-automation-pipeline.yml#L1936), [L2220](config/revitalise-grant-automation-pipeline.yml#L2220)); the knowledge warning exists ([L536](knowledge/technology/code-apps.md#L536)); the digest already shows IMP-0223 as corrected by IMP-1008. The live readings are pipeline-agent's ([L279](logs/pipeline.log#L279), [L281](logs/pipeline.log#L281)) and were not repeated here.
- *(Amendment 2)* IMP-0986: executed. All 51 Design 2.0 items carry the single label `operation:code-app-push` and one deploy record with needle `trustee-portal-design-2-20261001-2`; the matcher's literal for that label is `pac code push`; the first matching line is L277.
- *(Amendment 2)* IMP-0984: executed. The gate reports "43 supplied subdirectories, 2 matching a deliverable", and `Design-2.0/` has one subfolder (`design_handoff_application_detail`), not three as the finding says: `tokens/` and `reference/` sit inside it.
- *(Amendment 2)* IMP-0991: the four missing screens are absent from `Design-2.0/` and present in the untracked `Revitalise Design System (1)/ui_kits/trustee-review-portal/`. `diff -rq` against the tracked drop: 17 differences, including two kit screens only the copy has. The `Design-2.0` handoff is byte-identical to the copy's (`diff -rq` exit 0).
- *(Amendment 2)* IMP-0985: `#e6027f` on `#ffffff` recomputed at 4.4874.
- *(Amendment 2)* IMP-0989: the eight baselines named were renewed to 2026-10-14 with a `renewed{}` record, on your instruction at 08:08 ([routing L1199](logs/routing.log#L1199)); `gate_baseline.py` warns on nothing before expiry (its only date test is `expires < today`, [L140](scripts/lib/gate_baseline.py#L140)).
- *(Amendment 2)* IMP-0990: executed against the corpus (C19).
- *(Amendment 2)* IMP-0982: `work-items.py link` has no billing option (`--help`); `verify-worklog.py` mentions no `billing-decision`; `commercial-agent.md` names neither `known-exceptions` nor `billing-decision` (grepped with Python; the shell `grep -i` returned nothing on files where Python found matches, so every negative here was re-run in Python).
- *(Amendment 2)* IMP-0999 and IMP-0988: the first app's `.tableScroll` has no `position`, the card app's has; both `playwright.config.ts` files start `vite --port 4173 --strictPort` with `reuseExistingServer: !process.env.CI`.
- *(Amendment 2)* IMP-0979: fixed in source (`.detailGroup + .detailGroup`, [app.module.css L656](src/code-apps/trustee-review-portal/src/styles/app.module.css#L656)); WI-0008 is at deployed:dev.
- *(Amendment 2)* IMP-0998: the reviewer's R19 answer keeps `layout.test.ts` a contract test, rewritten in both apps (Design 2.0 TAD, Revision 3.2 §5.3).
- *(Amendment 2)* IMP-1000: `.gitignore` covers `build/exports/` and `build/artifacts/**` only; `CLAUDE.md`'s layout says the same, so the brief, not the repository document, was wrong.
- *(Amendment 2)* IMP-1007: of 4 needles into the pipeline config, 1 is note wording (IMP-0764); `BLOCKED_ON_MAX_AGE_DAYS = 14` occurs once in `verify-pipeline-config.py`.
- *(Amendment 3)* IMP-1010: walked the two flows' JSON: `Refresh_existing_applicant` 16, `Create_new_applicant` 20, `Create_application` 81 and `Write_error_log_row` 8 flat `item/` keys, none nested; 0 nested writes across all 10 flows; `Create_application` binds `item/rev_applicantid@odata.bind`. The live re-read is wired only in DEV `post_deploy` ([pipeline config L1541](config/revitalise-grant-automation-pipeline.yml#L1541)); `--help` shows no MODIFIED-only mode. The knowledge page still says "not proven" ([L227](knowledge/technology/build-and-deploy.md#L227)) and still says "Open every flow in the designer and press Save" ([L199](knowledge/technology/build-and-deploy.md#L199)).
- *(Amendment 3)* IMP-1020: the V4 wording search, run inside `.engine` after a positive control (a plain `git grep -- agents skills` from the instance returned nothing for a phrase present in the skill: the submodule trap the promotion skill names). 4 engine hits plus 3 instance hits, listed in C27.
- *(Amendment 3)* IMP-1011: §1's category table has no row for an outside party's tool, and §6's sweep names register rows only (both read). IMP-1016: `triggerAuthenticationType` appears in no knowledge file (grepped); power-automate.md warns against reading `workflow.clientdata` through `pac env fetch` ([L483](knowledge/technology/power-automate.md#L483)) and says nothing about filtering on it.
- *(Amendment 3)* IMP-1014: the register's columns ([L491–L501](skills/how-to-verify-a-platform-contract.md#L491)) name no executor. IMP-1015: the TAD's rev 14 list says it came from the build and pipeline configs; the architect file's instruction names the build config as the source ([L110](agents/architect-agent.md#L110)).
- *(Amendment 3)* IMP-1017: still true today ([README L197](src/tests/data/README.md#L197), [payloads L12](src/tests/data/intake-payloads.json#L12)); its root cause is false (§0). IMP-1018: still true ([L75](provisioning/entra/verify-intake-endpoint-auth.ps1#L75)); no `dev-*.json` file carries an `intake` block (counted). IMP-1019: C-TECH-058's text ([L128](constraints/technology/technology-constraints.md#L128)) and the three overrides (C32).
- *(Amendment 4)* IMP-1032: `report_stray_pac()` read in both copies (byte-identical, `cmp` exit 0); the Keychain line is in the `else` branch only ([L105–L111](scripts/run-with-timeout.sh#L105)); self-test case 6 matches the prefix `STRAY pac PROCESS(ES) FOUND` ([L196](scripts/run-with-timeout.sh#L196)), so row 45 keeps that prefix; self-test executed, 6 of 6. The phrase "the usual cause" has no reader outside the two script copies (`git grep --recurse-submodules`, with the engine copy as positive control).
- *(Amendment 4)* IMP-1024: the flow source's order, walked from `runAfter`: `Set_reminder_cadence` → `Send_the_envelope` → `Write_the_envelope_id_and_issue_date` ([L1538](src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L1538), [L1567](src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L1567), [L1593](src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L1593)). The design skill has no ordering-by-reversibility line (grepped).
- *(Amendment 4)* IMP-1026: `phoneNumber` appears once in the flow source, in a description saying why it is not set ([L976](src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L976)).
- *(Amendment 4)* IMP-1025: the TAD's D6 row is corrected in place ([L3366](docs/architecture/revitalise-grant-automation-architecture.md#L3366)) and the `tabType` question is open ([L3391](docs/architecture/revitalise-grant-automation-architecture.md#L3391), [A-DS-16 L3855](docs/architecture/revitalise-grant-automation-architecture.md#L3855)).
- *(Amendment 4)* IMP-1028: the flow no longer says "re-run" (0 hits in the source); the TAD names no re-issue route (searched for re-issue, reissue, resubmit and re-run beside envelope: only the A-R74 risk row). The trigger is `rev_grant` create only (message 1).
- *(Amendment 4)* IMP-1031: the TAD still names the eight tabs ([§5.8 step 2 L1154](docs/architecture/revitalise-grant-automation-architecture.md#L1154)) and ADR-043 still says "left for the referee to complete" ([L2446](docs/architecture/revitalise-grant-automation-architecture.md#L2446)).
- *(Amendment 4)* IMP-1029: `WdlExpression.psm1` is untracked and imported by the tracked contract tests ([L22](src/tests/solutions/AcceptanceEnvelopeContract.Tests.ps1#L22)); it evaluates `if()` eagerly and says why, consistent with the open question ([power-automate L237](knowledge/technology/power-automate.md#L237)).
- *(Amendment 4)* IMP-1030: `testResults.xml` is tracked, not ignored (`.gitignore` has no entry), and its history is 1 add plus 3 rewrites. IMP-1022: no file under `knowledge/technology/` names any DocuSign connector action (grepped for four operation ids, `allowReassign` and `tabType`: 0 hits in `knowledge/` and `skills/`).

**Duplicate check (skill §3a).** The `APPLIED` entries sharing each cluster's class were read for C1 (IMP-0960: knowledge line only; its mechanical candidate was named and not applied, so there is no duplicate) and C6 (none). C2's closest applied entry, IMP-0962, is the fix this review closes against. *(Amendment)* C10: the class's applied entries since 09-15 are IMP-0845 and IMP-0846 (provisioning tests), which do not overlap. The prior change on this subject is §12c, audited in §1. Also read: IMP-0920 (applied by review 2026-09-28), the same checklist paragraph row 12 extends; row 12 does not repeat it. C12 and C13: no other entry in either class. *(Amendment 2)* C14: IMP-0185, IMP-0193 and IMP-0223 read; row 15 extends the page IMP-0185 and IMP-0193 wrote and does not repeat it. C15: IMP-0910 (review 2026-09-26-6) is the rule row 16 extends. C16: IMP-0510 and IMP-0385 read (both reviewer-deferred); C-TECH-075 and §1.4a are their applied homes, and row 18 adds only what neither covers. C24: IMP-0500 read, because IMP-1006 re-proposes it. C25: IMP-0664, IMP-0733 and IMP-0755 share the class, all about needle form; none covers rewritable text. C19: no `APPLIED` entry in `gate-cannot-fail` mentions the assumption-marker gate (searched). C17, C18 and C20–C23: no `APPLIED` entry shares any of their classes (counted). C26 proposes no change, so there is nothing to duplicate. *(Amendment 3)* C27: no `APPLIED` entry shares its class; IMP-0959 and IMP-0956 (the 09-29 subsection) were read, and row 34 corrects their step 4 rather than repeating it. C28, C29 and C32 share `platform-contract-guessed-not-groundtruthed` (41 `APPLIED`); searched for sender, handover, executor, designer save and override: IMP-0614 is the §2 dynamic-parameter rule that C29 extends, IMP-0618 (a reviewer's own description of a platform artefact outranks repository prose) is adjacent to C28 and does not cover a closure test, and none covers an outside party's tool, an executor, or C-TECH-058's wording. C30: no `APPLIED` entry in its class; IMP-0472's section is the one row 39 widens. C31: 0 of 43 `APPLIED` `gate-cannot-fail` entries mention `ValidateSet`. IMP-1016's class has 25 `APPLIED`; IMP-0409 (read a live flow through export and unpack) is the nearest, and does not cover the trigger-mode property or a `like` search. *(Amendment 4)* C33, C34 (IMP-1022) and C35 share `platform-contract-guessed-not-groundtruthed`; its `APPLIED` entries were searched for designer silence, `envelopeId`, `phoneNumber`, SMS, body schema and a template's field list. None covers them; the nearest are IMP-0614, IMP-0620 and IMP-0615, the rules rows 41 and 44 extend (§1). C34's other two classes have no other member. C36: the five `APPLIED` `gate-defect` entries (IMP-0619, IMP-0621, IMP-0693, IMP-0896, IMP-0916) are about gate wiring, a site-map pairing, a coverage substring and review stamps; none touches the timeout script. IMP-0217 is the prior change C36 recurs against. C37 and C38: no other member in any of their classes.

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
| 10 | agent | [improvement-agent.md L568](agents/improvement-agent.md#L568) | Verify-script count, re-derived at apply with `ls scripts/verify-*.py \| wc -l` (68 at the draft, after development-agent's `verify-live-flow-definitions.py`; *Amendment 2:* 69, with the untracked `verify-code-app-variant-parity.py`) | — (registered claim, `verify-derived-counts.py`) | YES — `python3 scripts/verify-derived-counts.py` | N/A |
| 11 | skill | [skills/how-to-verify-a-platform-contract.md §12c](skills/how-to-verify-a-platform-contract.md#L927) (engine) | New paragraph after the name-resemblance tell: "Opening the document is not the check. Where it specifies a screen, transcribe its rows (section, sub-heading, label, in order) into a test fixture, build the screen from a typed row specification, and assert the two are equal; a section-level reorder passes a heading test by construction (IMP-0975). Record every row you cannot render as a gap for the reviewer, never as a silent omission." No client names (grepped before commit, skill §6) | IMP-0975, IMP-0973 | N/A — instruction change | N/A |
| 12 | skill | [skills/how-to-intake-external-documents.md `acceptance` row](skills/how-to-intake-external-documents.md#L238) (engine) | Append to the row's Rule cell: "Where the requirement in force points at a document ('as the PDF', 'the pack', 'the form'), the clause names it by path (IMP-0973)." | IMP-0973 | N/A — reference text; row 14 is its mechanical half | N/A |
| 13 | script | [.engine/scripts/lib/work_items.py fold](.engine/scripts/lib/work_items.py#L771), [reopen check L523](.engine/scripts/lib/work_items.py#L523) and `.engine/scripts/work-items.py` | **Revised by Amendment 2 (IMP-1004, the second instance), superseding the narrower draft.** Reopens counts rejections only. (a) A `reopen` from `deferred` leaves `reopens` unchanged, comment "a reopen from deferred is a resume, not a rejection (IMP-0977)". (b) New `reopen --retrace`: legal from `built` or later; the reason must name the evidence file that changed; refused if a `link --acceptance` arrives before the next transition, and that transition must return to the state held before the retrace; `reopens` unchanged, comment "a retrace re-points evidence and is not a rejection (IMP-1004)". Self-test: defer → reopen → 0; built → reopen → 1; built → reopen --retrace → built → 0; retrace then acceptance relink → refused; retrace then a different target state → refused | IMP-0977, IMP-1004 | YES — `python3 scripts/work-items.py --selftest`; `python3 scripts/verify-work-items.py --check` (0 new findings; WI-0045 and WI-0008 drop by 1 in the export; the three 09:53 retrace reopens of WI-0092, WI-0102, WI-0103 stay counted, because history is not rewritten) | already wired — `work-items` step ([build L160](config/revitalise-grant-automation-build.yml#L160), `--warn-only`) |
| 14 | script | [.engine/scripts/lib/work_items.py `built` branch](.engine/scripts/lib/work_items.py#L549) — **only if decision 3 is yes** | For `pbi`/`bug`, a `built` dated **after** the apply date: each clause whose text names a `docs/Import/` path needs a `source-lines` for that clause whose `file` matches `*.test.*` or `*.spec.*` and whose `contains` holds the document's file name, else `EVIDENCE: <id>: clause <n> names <doc>; built needs a test line that names it too`. A module date constant, as row 8. Self-test: refused without; passes with; pre-cutoff event folds | IMP-0973, IMP-0975 | YES — `python3 scripts/work-items.py --selftest`; `verify-work-items.py --check` 0 new findings (measured corpus: 1 of 52 items, WI-0005, whose last `built` at 13:52 today would fail if the cutoff included today — its test evidence names the fixture, not the PDF) | already wired — `work-items` step, `--warn-only` |
| 15 | knowledge | [knowledge/technology/code-apps.md ALM L536–L543](knowledge/technology/code-apps.md#L536) | Keep the warning. Replace its evidence sentence with the three dated readings (22 Aug push: absent; 22 Aug manual *Add existing*: present; 23 Aug read: present, which was the manual add; 01 Oct first push of a second app: absent from every solution, with no canvasapp row) and one line: "membership came from the maker portal, not the push (IMP-1008)". Add the check: after a first push, read `solutioncomponent` by the app's id in any solution, and before crediting a push compare the component's `createdon` with the push time. Item 3 (*Promotion*) becomes conditional: the app travels in the managed solution once it has been added to it | IMP-1008, IMP-0983 | N/A — reference text | N/A |
| 16 | script | [.engine/scripts/lib/deploy_markers.py `checkable` L95](.engine/scripts/lib/deploy_markers.py#L95), [work_items.py deploy-record L689](.engine/scripts/lib/work_items.py#L689), `scripts/verify-pipeline-config.py` **and** its engine copy, and the three DEV `code-app-push` entries in [the pipeline config](config/revitalise-grant-automation-pipeline.yml#L1115) | A `post_deploy` entry may carry `app: src/code-apps/<folder>`. Its label becomes `operation:code-app-push@<folder>` and its literal `from src/code-apps/<folder>)`, so a marker discharges it only when its command half carries `(from src/code-apps/<folder>)` (the closing parenthesis stops `trustee-review-portal` matching `trustee-review-portal-cards`). New pipeline-config check: two or more entries with one `operation` in one environment must each carry an `app:` naming an existing folder. Item labels without `@` stay valid where an environment has one such entry. Dated: records after the apply date only. The config's three DEV push entries gain `app:` in the same change (the first app twice, the card app once) | IMP-0986 | YES — `python3 scripts/work-items.py --selftest` (new case: a card-app record is refused on a first-app marker); `python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml` exit 0; `verify-work-items.py --check` 0 new findings | already wired — `pipeline-config-preflight` ([build L78](config/revitalise-grant-automation-build.yml#L78)) and `work-items` |
| 17 | agent | [agents/pipeline-agent.md WRITE lines L283–L284](agents/pipeline-agent.md#L283) | Add: "For a Code App push, the command half names the folder: `pac code push --solutionName <S> -Env <env> (from src/code-apps/<folder>) (build <dir>)`. With two apps in one environment, a line without it discharges neither (IMP-0986)." | IMP-0986 | N/A — instruction change | N/A |
| 18 | skill | [skills/how-to-intake-external-documents.md](skills/how-to-intake-external-documents.md#L139) (engine), new section after *Palette Check* | **Supplied Design Bundle Checklist (architect-agent).** Before anything is scoped from a supplied design: (1) resolve every local reference its entry point loads (IMP-0991): every `src`/`href` in each `*.html`; count a `.jsx.txt` copy as present-renamed; resolve `../` references against the design system's root; list what is missing and put it to the reviewer before items are cut. (2) If another drop has the same inner folders, `diff -rq` the two and name the copy you read. (3) kit content is presentation, never a requirement (IMP-0993): labels, headings, sections and figures come from current source; record each kit-vs-source difference in a register; a kit's own provenance line is not evidence. (4) For each claim the handoff makes — a contrast ratio, "this test must change" — measure the ratio and grep which repository test actually asserts it (IMP-0985). (5) Render every supplied screen at 320 px; an overflow in the design is a recorded deviation and WCAG 1.4.10 wins (IMP-1001), with the palette itself checked under the accessibility checklist §1.4a. No client names (grepped before commit, skill §6) | IMP-0991, IMP-0993, IMP-0985, IMP-1001, IMP-0992 | N/A — instruction change; row 19 is its mechanical half | N/A |
| 19 | script | [scripts/verify-design-source-coverage.py `scan` L117](scripts/verify-design-source-coverage.py#L117) **and** its engine copy | (a) Every top-level folder under each `SUPPLIED_ROOTS` entry is in scope by its root path (`Designsystem/<drop>`, with a boundary so `Revitalise Design System` does not match `Revitalise Design System (1)`), and must appear in some architecture document; docstring line "every top-level drop is in scope by its root path (IMP-0984)". (b) **Only on decision 5:** where two in-scope folders share a `citation_key`, each must be cited by its full repo path; docstring line "a citation key two in-scope folders share needs the full path (IMP-0992)". Self-test: a drop named after a screen, uncited → FAIL; cited → PASS; (b) two drops with one inner layout → FAIL until each full path is cited | IMP-0984, IMP-0992 | YES — `--selftest`; real corpus: (a) 3 drops, 0 findings; (b) 1 finding, true | already wired — HARD `design-source-coverage` ([build L858](config/revitalise-grant-automation-build.yml#L858)) |
| 20 | constraint-amendment | [C-TECH-075](constraints/technology/technology-constraints.md#L145) | Rule gains one sentence: "Every top-level folder of a supplied design root is cited by its root path, whatever it is named (IMP-0984)." Rationale gains IMP-0984 and IMP-0992. Verify By unchanged (the same script) | IMP-0984, IMP-0992 | YES — row 19's command | already wired |
| 21 | skill | [skills/how-to-verify-a-platform-contract.md](skills/how-to-verify-a-platform-contract.md#L927) (engine), new §12d after §12c | **§12d. A supplied DESIGN is matched by measurement, never by reading it.** "Matches" means equal computed values from both renders: one probe per element, the same locator on both, at every width the screenshots cover. Generate the probe list from the design's declarations (every inline-style property per element type, plus its global stylesheet and any `<style>` block), not from a screenshot. Probe each token through a component that consumes it, and probe latent properties (wrapping, stretch, first/last-child borders) directly. Keep the probe script beside the screenshots. A grep of the built CSS proves a declaration exists, not that it renders (IMP-1002) | IMP-0997, IMP-1002, IMP-1005 | N/A — instruction change | N/A |
| 22 | agent | [agents/architect-agent.md](agents/architect-agent.md#L254), new subsection after *run the design-doc-claims check* | **Before you finish: list the item clauses this TAD overrides.** Where the feature already has items in the ledger (`python3 scripts/work-items.py export --format json --scope <ids>`), grep each clause for the concrete values your ADRs and "keep source" rows decide (a hex value, a file, a component, a mechanism) and list the clauses they contradict in the gate output as `item | clause | TAD row`, so pm-agent amends them in one batch before development; and list the item clauses this TAD overrides (IMP-0987) again at every TAD revision — a revision that changes a value an item clause pins (IMP-1003) is the same case | IMP-0987, IMP-1003 | N/A — instruction change | N/A |
| 23 | script | `.engine/scripts/work-items.py` link sub-command and [work_items.py fold](.engine/scripts/lib/work_items.py#L760) | `link --title "<text>"` replaces the title; help text "link --title (IMP-0994)". Self-test: a relinked title folds and exports | IMP-0994 | YES — `python3 scripts/work-items.py --selftest` | already wired — `work-items` |
| 24 | script | [scripts/verify-assumption-markers.py `ROW_ID` L127](scripts/verify-assumption-markers.py#L127), `MARKER_IN_SOURCE` L124, `PATHISH` L138, **and** the engine copy | Grammar `A-(?:[A-Z][A-Z0-9]{0,7}-\|[A-Z]{1,3}(?=\d))?\d{1,3}` in both patterns, optional `**` around a row id, and `css` in `PATHISH`; comment "a digit or up to eight characters in the prefix (IMP-0990)". Self-test: `A-D2-1`, `A-ATYPE-1`, `A-G03` and `**A-X-1**` rows are read; a `.css` code-span Where resolves | IMP-0990 | YES — `--selftest`; real corpus: 97 → 108 rows, 0 failures, 1 new note (true) | already wired — HARD `assumption-markers` ([build L274](config/revitalise-grant-automation-build.yml#L274)) |
| 25 | script | [scripts/lib/gate_baseline.py](scripts/lib/gate_baseline.py#L140) **and** its engine copy, and `scripts/verify-build-config.py` (both copies) | New `expiring(repo_root, within_days=4)` returns entries whose `expires` is within 4 days, docstring line "expires within 4 days (IMP-0989)". `verify-build-config.py` prints one NOTE per such entry, naming owner and finding, and never changes its exit code. Self-test: an entry 3 days out is reported, 5 days out is not | IMP-0989 | YES — `python3 scripts/lib/gate_baseline.py` (run directly, it runs its self-test; exit 0 today) and `pwsh -NoProfile -File src/tests/Invoke-Tests.ps1 -Path build` (verify-build-config.py has no `--selftest`; its tests are in `BuildGates.Tests.ps1`); today 0 NOTEs (nearest expiry 2026-10-13) | runs inside HARD `preflight-build-config` ([build L73](config/revitalise-grant-automation-build.yml#L73)), SOFT by construction |
| 26 | knowledge | [knowledge/technology/power-automate.md *Guards and fallbacks* L340](knowledge/technology/power-automate.md#L340) | Two bullets. "An ordering comparison on a nullable value: `greater`, `greaterOrEquals`, `less` and `lessOrEquals` throw `InvalidTemplate` on an empty operand, where `equals()` returns false. Wrap it in `coalesce()` with a value outside every band, and test with an unscored row (IMP-0980)." And: "`string(<boolean>)` renders `True`/`False` (IMP-0981), which is invalid JSON spliced unquoted; use `if(<cond>,'true','false')`." | IMP-0980, IMP-0981 | N/A — reference text | N/A |
| 27 | knowledge | [knowledge/technology/code-apps.md *Styling* L639](knowledge/technology/code-apps.md#L639) | Two lines. "A heading that is the first child of its own group wrapper loses its top margin to a `:first-child` reset; space the wrappers (`.group + .group`), and assert in Chromium that the gap between groups is clearly larger than the gap between rows (IMP-0979)." "A horizontally scrolling wrapper clips an absolutely positioned descendant, such as visually hidden `.srOnly` text, only if it is that descendant's containing block: give every `overflow-x: auto` wrapper `position: relative` (IMP-0999)." | IMP-0979, IMP-0999 | N/A — reference text | N/A |
| 28 | agent | [agents/commercial-agent.md](agents/commercial-agent.md#L126) | Add before hours are proposed: "read every `billing-decision` event (IMP-0982) in `logs/commercial-events.jsonl` and every `contract/known-exceptions.json` entry whose `gate` is `none`, and propose no billable hours for the items or feature they name" | IMP-0982 | N/A — instruction change; the mechanical half is decision 4 | N/A |
| 29 | agent | [agents/improvement-agent.md needle list L676](agents/improvement-agent.md#L676) | New bullet: "never anchor a needle to text a rule requires to be rewritten (IMP-1007): a `blocked_on` note is re-dated and reworded every 14 days by check 14. Anchor to a stable key — a script constant, a prerequisite id, or a marker that cites the entry's own id." | IMP-1007 | N/A — instruction change | N/A |
| 30 | other | `logs/improvement-log.jsonl` (data) | IMP-0764's `evidence_grep` → `{"file": "scripts/verify-pipeline-config.py", "contains": "BLOCKED_ON_MAX_AGE_DAYS = 14"}` (`grep -c` = 1, measured), the defence its own `applied_by` names. IMP-0500's `deferred_reason` gains the measurement in C24; its `revisit_when` stays verbatim | IMP-1007, IMP-1009 | YES — `python3 scripts/verify-improvement-log.py --check` | N/A |
| 31 | constraint-amendment | [C-TECH-053](constraints/technology/technology-constraints.md#L108) | Rule gains: "**AMENDED <apply date> — a V4 designer save of a solution-sourced flow is itself a live write (IMP-1020)**: it rewrites the whole definition from what the designer understood, so run `verify-live-flow-definitions.py --env <env>` after it, and re-import from source on any difference before the flow is tested further (IMP-1010)." Rationale gains IMP-1010 and IMP-1020. Verify By unchanged | IMP-1020, IMP-1010 | YES — the named script, exit 0 after a save | already wired — DEV `post_deploy` `flow-definition-reread` |
| 32 | skill | [skills/how-to-verify-a-platform-contract.md §5, after the levels table L596](skills/how-to-verify-a-platform-contract.md#L596) (engine) | New paragraph: "**A V4 save rewrites a solution flow from what the designer understood (IMP-1010).** It is a live write, not an observation: in one measured save it dropped nested write parameters, the secure-inputs setting and every action's authentication block, renamed parameters and added the trigger's sign-in mode. Save, then re-read the live definition against source and re-import on any difference; a V4 claim stands only on a re-read taken after the save." No client names (grepped before commit, skill §6) | IMP-1010, IMP-1020 | N/A — instruction change; row 31 is its constraint | N/A |
| 33 | agent | [agents/pipeline-agent.md check (c) L476](agents/pipeline-agent.md#L476) (engine) | The How cell gains: "then re-read the live definition (`verify-live-flow-definitions.py --env <env>`) and re-import on any difference (IMP-1020); a save is a write" | IMP-1020 | N/A — instruction change | N/A |
| 34 | knowledge | [knowledge/technology/build-and-deploy.md L199](knowledge/technology/build-and-deploy.md#L199) and [step 4 L222–L229](knowledge/technology/build-and-deploy.md#L227) | (a) Step 5(c) becomes "Open every flow in the designer and press Save, then re-read it live; a designer save rewrites the whole definition (IMP-1010)." (b) Step 4 keeps its instruction and replaces "This is the leading candidate … and it is **not proven** …" with: "Observed 2026-10-02 (IMP-1010): a designer save between deploys, with the designer's fingerprints throughout (display-name parameters, authentication blocks and secureData removed, trigger mode added), emptied the two nested writes while the flat write in the same flow kept every column. The 2026-09-29 loss has the same shape." | IMP-1010 | N/A — reference text | N/A |
| 35 | template | [templates/dev-summary-template.md L96](templates/dev-summary-template.md#L96), [templates/test-report-template.md L82](templates/test-report-template.md#L82) (engine) and [config/pipeline.yml.example L171](config/pipeline.yml.example#L171) | Each V4 wording gains "then re-read live (IMP-1020)" after "saved"; the example's (c) description gains the command | IMP-1020 | N/A — template text | N/A |
| 36 | knowledge | [knowledge/technology/power-automate.md](knowledge/technology/power-automate.md#L381): *Hand-Authoring* L381, *Trigger* L290, the fetch note L483 | Three bullets. (a) "Write each column as its own `item/<column>` key (IMP-1010) in a Dataverse create or update, never a nested `item` object: the designer binds only the flat form and a save keeps only what it bound. A lookup is `item/<navigation property>@odata.bind` with the value `/<entity set>(<guid>)`." (b) "The HTTP trigger's 'Who can trigger the flow?' is `triggers.<name>.inputs.triggerAuthenticationType` (IMP-1016); `All` is Anyone. It ships in source and the live re-read compares it." (c) After the L483 warning: "Filtering on the column works: a `like` condition on `clientdata` (category 5) finds every live flow containing a shape in one query; `pac` rejects `fetch/@top` (IMP-1016)." | IMP-1010, IMP-1016 | N/A — reference text | N/A |
| 37 | skill | [skills/how-to-verify-a-platform-contract.md §1 table L41](skills/how-to-verify-a-platform-contract.md#L41) and [§6 L662](skills/how-to-verify-a-platform-contract.md#L662) (engine) | (a) New category row: "**An outside party's tool** — what a third party's plugin, form or service can send or accept (fixed or per-request headers, token refresh, retries). A route that depends on it is closed only when that tool has made one successful call, or its owner has confirmed the mechanism in writing; a credential handover is not that evidence (IMP-1011)." (b) §6 new step 0: "List every 'cannot be expressed in source' or 'no property exists' claim in the TAD and test each against the first exported definition: it is a negative claim, and the export is the whole set (IMP-1016)." No client names | IMP-1011, IMP-1016 | N/A — instruction change | N/A |
| 38 | skill | [skills/how-to-verify-a-platform-contract.md §4 register, *Cheapest verification* L499](skills/how-to-verify-a-platform-contract.md#L499) (engine) | Meaning cell gains: "Where the step needs the maker designer (bind, save, read back), the cell names its human executor and the step goes out as `REVIEWER ACTION REQUIRED`; never assign it to an agent dispatch (IMP-1014)" | IMP-1014 | N/A — reference text | N/A |
| 39 | agent | [agents/architect-agent.md, the IMP-0472 section L106](agents/architect-agent.md#L106) (engine) | New paragraph at its end: "**When an ADR is RE-DECIDED, the build config is not the source.** Search for the retired decision's distinctive words across the whole repository (`git grep -n --recurse-submodules`, no extension filter, a positive control first) and list every hit of the retired decision's words (IMP-1015) in the ADR's gate-interactions paragraph, each marked *rewrite* or *history, kept*. A hit nobody marks is the one that is missed: the second instance was found by the search and lost among similar history lines (IMP-1017)." | IMP-1015, IMP-1017 | N/A — instruction change | N/A |
| 40 | constraint-amendment | [C-TECH-058](constraints/technology/technology-constraints.md#L128) — **only on decision 6** | Rule gains: "An OPEN assumption whose register row names the DEV deploy as its own check (IMP-1019) (the import, the first push, a designer check in DEV, a run in DEV) does not block that DEV deploy; pipeline-agent records it as measured by the deploy, and it blocks every environment after DEV until closed." Verify By unchanged | IMP-1019 | YES as far as today's Verify By goes — pipeline-agent's register output names each such row | N/A |
| 41 | skill | [skills/how-to-verify-a-platform-contract.md §2, after L104](skills/how-to-verify-a-platform-contract.md#L104) (engine) | New paragraph: "**A designer-saved definition proves what it CONTAINS, and nothing it leaves out.** It is E1 for the actions it holds and the parameters it bound. It is not evidence of: (1) a property it did not reject — a designer's silence about a property is not acceptance (IMP-1021); a dynamic block may drop what it did not bind, and only a live run shows it; (2) composition — actions in a row act on one resource only where an id parameter is bound to the earlier output (an envelope id, a record id); an action with none creates a new resource (IMP-1023); (3) sameness — two actions with one body schema are different calls when their path or id parameters differ (IMP-1026); (4) side effects — read a parameter's reference description, not its display name: a phone-number parameter can be a delivery channel (IMP-1026). And take an action's body shape and cardinality from the saved definition, never from the reference (IMP-1025)." No client names (grepped before commit, skill §6) | IMP-1021, IMP-1023, IMP-1025, IMP-1026 | N/A — instruction change; no instrument here reads a dynamic schema (L92) | N/A |
| 42 | skill | [skills/how-to-design-a-workflow.md Design Checklist L27](skills/how-to-design-a-workflow.md#L27) (engine) | Three lines after *Error handling*: "- [ ] **Irreversible step last:** every fallible step runs before the send, post or payment, so a failure leaves the unsent state the alert describes; only the local record of the action follows it (IMP-1024)". "- [ ] **Restart route:** a workflow that fires only when a record is created names how a stopped run is re-issued once its cause is fixed; shipped text never says 're-run' without one (IMP-1028)". "- [ ] **Outside configuration:** list each behaviour only the outside service's own template or account can enforce (required fields, reassignment, recipient sign-in), each with a per-environment configuration row and a live test (IMP-1022)". No client names | IMP-1024, IMP-1028, IMP-1022 | N/A — instruction change | N/A |
| 43 | knowledge | [knowledge/technology/power-automate.md, new section before *Sensitive Data Flows* L310](knowledge/technology/power-automate.md#L310) | "### DocuSign connector — what a flow can set, and what only the template or account can (IMP-1022)". Four bullets, each with its level: tab values are written by `tabId` through `UpdateRecipientTabsValues` (one recipient) or `UpdateEnvelopePrefillTabs` (one document), array bodies of `{tabType, tabId, value}` (E1, saved); neither sets *Required* or *Locked*, which stay on the template (E2); reassignment is a template or account setting no action exposes (E2); the referee's access code is `AddVerificationToRecipient` (E1), and `UpdateEnvelopeRecipient`'s `phoneNumber` makes SMS a delivery channel (E2). Closing line: "The measured table, with sources, is TAD ADR-067; correct it there first." | IMP-1022 | N/A — reference text | N/A |
| 44 | skill | [skills/how-to-verify-a-platform-contract.md §2 table, L120](skills/how-to-verify-a-platform-contract.md#L120) (engine) | The row's first cell gains: "— or the set of fields a template carries (IMP-1031)"; its second cell gains: "the template's own field list, every field minus those the platform fills (signature, signer name, date signed)". The paragraph under the table gains one sentence: "The same holds for a template's fields: a design summary lists the fields someone thought of; the template lists the ones that will show placeholder text if left unfilled." | IMP-1031 | N/A — instruction change | N/A |
| 45 | script | [scripts/run-with-timeout.sh `report_stray_pac` L88–L111](scripts/run-with-timeout.sh#L88) **and** `.engine/scripts/run-with-timeout.sh` | Stray-found branch: the first line becomes "STRAY pac PROCESS(ES) FOUND — a candidate, not yet the cause (IMP-1032)." (the prefix self-test case 6 matches is kept). Both branches then print: "Also check for a pending macOS Keychain prompt (IMP-0217): no shell probe can see it." and "To confirm a kill fixed it: run `scripts/run-with-timeout.sh 45 pac org who` before retrying. Still hangs → the stray was not the blocker; ask the person at the screen." Self-test case 7: with a fixture process list containing a `pac`, the output carries both the Keychain line and the probe line. The process list moves behind a small function so the self-test can supply one | IMP-1032 | YES — `bash scripts/run-with-timeout.sh --selftest` (7 of 7) | already invoked by the HARD `lint` step ([build L1057](config/revitalise-grant-automation-build.yml#L1057)); not a `verify-*` gate. `verify-engine-instance-split.py` at apply |
| 46 | knowledge | [knowledge/technology/build-and-deploy.md step 1 L451](knowledge/technology/build-and-deploy.md#L451) | Step 1's heading becomes "**Find a stray `pac`, kill it, then confirm before you retry.**" and gains: "Run `scripts/run-with-timeout.sh 45 pac org who`. If it returns, retry the build. If it still hangs, the stray was not the blocker: go to step 2 before any further attempt. A build report calls a stray `pac` 'found', never 'the cause', until this probe has returned (IMP-1032; on 2–3 October a kill changed nothing and two builds were lost)." | IMP-1032 | N/A — reference text | N/A |
| 47 | knowledge | [knowledge/technology/power-automate.md *Guards and fallbacks* L340](knowledge/technology/power-automate.md#L340) and `logs/improvement-log.jsonl` (data) | One bullet: "To execute a guard rather than read it, import `src/tests/solutions/_harness/WdlExpression.psm1` (IMP-1029) and evaluate the source's own expression with the input that selects each branch. It evaluates `if()` eagerly, which is safe under either answer to the open question above; extend it rather than skip a function it lacks." IMP-1029 gains `"capability": true`. **HELD**: applies when `WdlExpression.psm1` is committed | IMP-1029 | YES for the data half — `python3 scripts/verify-improvement-log.py --check` and `generate-known-failure-modes.py --check` (the lesson moves to *Capabilities*) | N/A |
| 48 | other | `.gitignore` and the tracked `testResults.xml` | `.gitignore` gains, under *OS / editor*: "# Pester -CI writes this at the repo root; never track it (IMP-1030)" and "testResults.xml" on its own line (a `#` inside a pattern line would be part of the pattern). Then `git rm --cached testResults.xml` in the same commit | IMP-1030 | YES — `git check-ignore -v testResults.xml` names the new line; `git ls-files testResults.xml` prints nothing | N/A |

**Amendment re-measurement of row 8.** Since WI-0052, all 4 `built` events recorded today had components declared before them ([L149](logs/work-items.jsonl#L149), [L155](logs/work-items.jsonl#L155), [L159](logs/work-items.jsonl#L159), [L160](logs/work-items.jsonl#L160)). The one that had none, WI-0052 at 09:37 ([L143](logs/work-items.jsonl#L143)), is dated today. So row 8's "on or after the apply date" would report it if applied today, and its "0 new findings" verification would fail. At apply, row 8 takes the same **after the apply date** cutoff as row 14. That narrowing removes one named historical event the rule would wrongly report, and does not change what the rule enforces.

**Constraint budget:** 0 of 3 used. *(Amendment 2)* One amendment to an existing constraint (row 20), which adds no row. *(Amendment 3)* Two more amendments (rows 31 and 40, the second only on decision 6); still no new row. *(Amendment 4)* None; still 0 of 3.

**Publishing.** Rows 1, 2, 3, 4, 8 and 10 change the `.engine` submodule, and so do rows 11–14 from the amendment. It already carries one uncommitted change from review 2026-09-30 (the digest line count in `generate-known-failure-modes.py`). The order is: commit there, `git -C .engine push origin HEAD:main`, verify with `git -C .engine branch -r --contains HEAD`, then bump the pointer here. Rows 1 and 2 are script pairs: both copies, same change. *(Amendment 2)* Engine changes added: rows 13, 16 (`deploy_markers.py`, `work_items.py`), 17, 18, 21, 22, 23, 28 and 29. Script pairs added: `verify-pipeline-config.py` (row 16), `verify-design-source-coverage.py` (row 19), `verify-assumption-markers.py` (row 24) and `lib/gate_baseline.py` (row 25) are byte-identical pairs today (`cmp`). `verify-build-config.py` (row 25) is not: the instance copy carries two exemption entries the engine copy lacks (`report-baseline-drift.py`, `verify-live-flow-definitions.py`), so row 25 edits each copy in place and must not copy one over the other. Rows 15, 20, 26, 27 and 30, and the pipeline config's `app:` keys, are instance-repository changes. *(Amendment 3)* Engine changes added: rows 32, 33, 35 (the two templates), 37, 38 and 39. Instance changes added: rows 31, 34, 35 (`config/pipeline.yml.example`), 36 and 40. No script pair is touched. *(Amendment 4)* Engine changes added: rows 41, 42 and 44. Script pair added: `run-with-timeout.sh` (row 45), byte-identical today (`cmp` exit 0), so one edit is copied to both. Instance changes added: rows 43, 46, 47 and 48.

---

## 4. Retirements

> Retirement check performed: 87 live constraint rows, 10 retired (`grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l`, re-run at apply). None is made redundant: this review adds no constraint. Retired as text: the three check-7 exceptions (row 7, held), and the testing-tools.md clause about `date`, struck through in place (row 5). No gate is retired. *(Amendment)* Checked again for rows 11–14: none replaces an existing rule. Row 12 sits beside the 09-28 status-column rule and does not supersede it, and §12c's existing text stays, because opening the document is still the first step. *(Amendment 2)* Re-derived: 87 live rows, 10 retired. Checked for rows 15–30: none retires a constraint. C-TECH-075 is amended, not replaced: its name-match clause still finds a folder named after an app inside a drop, which the root-path rule does not. The drafted narrow form of row 13 is superseded by its revision (a draft row, not a rule, so there is nothing to strike through). The three `IMP-0223` config notes are corrected by their owners, not retired. *(Amendment 3)* Checked for rows 31–40: none retires a constraint or a gate. The V4 save was considered for retirement and kept: three of the fifteen founding failures were found only by it. Row 34 replaces a "not proven" sentence with the observation, in place; that is a correction, not a retirement. Live and retired counts unchanged (87 and 10, re-derived). *(Amendment 4)* Checked for rows 41–48: none retires a constraint or a gate. Retired as text: the script phrase "the usual cause" (row 45), replaced in place, and the tracked `testResults.xml` (row 48). The knowledge page's 23 August CORRECTION block stays: it is the history row 46 builds on. Live and retired counts re-derived: 87 and 10.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0934, IMP-0855, IMP-0963, IMP-0966, IMP-0879, IMP-0906, IMP-0298, IMP-0824 *(Amendments 2, 3 and 4: the same list; nothing added)*

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
| *(Amendment 2)* IMP-0979 | V4 | **DEFER from the start.** Fixed in source; row 27 lands the lesson | `revisit_when`: *the ledger records WI-0008 at verified:dev on your confirmation of the wellbeing sub-heading spacing, or records a reopen* |
| IMP-0980 | V5 | **DEFER from the start.** Row 26 lands; only a live run with an unscored application re-observes it, and the deploy's post-import run was not made ([L273](logs/pipeline.log#L273)) | `revisit_when`: *a Round Statistics run in DEV, with an unscored application in the open round, ends with the result row Complete and no new error row* |
| IMP-0981 | V1 | **CLOSE** → `APPLIED`, row 26 | `evidence_grep` on "`string(<boolean>)` renders `True`/`False` (IMP-0981)" |
| IMP-0982 | n/a | **DEFER on decision 4.** Row 28 lands either way. If you answer "no gate", CLOSE on row 28's needle "read every `billing-decision` event (IMP-0982)" | `revisit_when`: *decision 4 is answered: a commercial-agent design for a per-item billing check exists under docs/improvements/, or the reviewer decides the recorded decision plus row 28 is enough* |
| IMP-0983 | n/a | **CLOSE** → `APPLIED`, row 15 | `evidence_grep` on "membership came from the maker portal, not the push (IMP-1008)" |
| IMP-0984 | n/a | **CLOSE** → `APPLIED`, rows 19(a) and 20 | `evidence_grep` on "every top-level drop is in scope by its root path (IMP-0984)" |
| IMP-0985 | n/a | **CLOSE** → `APPLIED`, row 18 | `evidence_grep` on "grep which repository test actually asserts it (IMP-0985)" |
| IMP-0986 | V3 | **DEFER from the start.** Rows 16–17 land; only a deploy re-observes them | `revisit_when`: *the first DEV deploy after rows 16–17 records each app's items against its own push line, and verify-work-items.py --check reports 0 findings* |
| IMP-0987 | n/a | **CLOSE** → `APPLIED`, row 22 | `evidence_grep` on "list the item clauses this TAD overrides (IMP-0987)" |
| IMP-0988 | V2 | **DEFER from the start**, routed | `revisit_when`: *each app's playwright.config.ts derives its harness port from its own folder (or an env var), in one change that keeps the file under parity* |
| IMP-0989 | V1 | **CLOSE** → `APPLIED`, row 25 | `evidence_grep` on "expires within 4 days (IMP-0989)" |
| IMP-0990 | V1 | **CLOSE** → `APPLIED`, row 24 | `evidence_grep` on "a digit or up to eight characters in the prefix (IMP-0990)" |
| IMP-0991 | V1 | **CLOSE** → `APPLIED`, row 18 | `evidence_grep` on "every local reference its entry point loads (IMP-0991)" |
| IMP-0992 | n/a | **CLOSE** if decision 5 is answered and row 19(b) applies, on "a citation key two in-scope folders share needs the full path (IMP-0992)". **Otherwise DEFER** | `revisit_when`: *decision 5 is answered and row 19(b) applies, or the duplicate drop is removed* |
| IMP-0993 | n/a | **CLOSE** → `APPLIED`, row 18 | `evidence_grep` on "kit content is presentation, never a requirement (IMP-0993)" |
| IMP-0994 | n/a | **CLOSE** → `APPLIED`, row 23 | `evidence_grep` on "link --title (IMP-0994)" in `.engine/scripts/work-items.py` |
| IMP-0995 | n/a | **DEFER from the start**, routed | `revisit_when`: *settings-rows.notes.md states DEV's current RoundStatisticsHistory* values with who set them, or states that it gives initial values only* |
| IMP-0996 | V1 | **CLOSE** → `APPLIED`, rows 2–3 | `evidence_grep` on row 2's docstring line, as IMP-0970 |
| IMP-0997 | V2 | **DEFER from the start.** Row 21 lands; only a fidelity measurement re-observes it | `revisit_when`: *a fidelity audit of the card app, with probes generated from the kit's declarations at 320, 390 and 1280 px, reports no deviation the Dev Summary does not record, or you confirm the side-by-side comparison* |
| IMP-0998 | V1 | **REJECT** — superseded by your R19 answer | `rejected_reason`: *the reviewer decided R19 (rewrite layout.test.ts in both apps, keep it contract); the proposed split is not the decision in force* |
| IMP-0999 | V2 | **DEFER from the start.** Fixed in the card app; the first app still has the shape (routed); row 27 lands the lesson | `revisit_when`: *the first app's table scroll wrapper declares position and its Chromium spec measures 0 px page overflow at 320 px with the sort hints present* |
| IMP-1000 | n/a | **REJECT** — proposal not adopted | `rejected_reason`: *fidelity screenshots belong in the session scratchpad, where they were put; nothing needs a tracked build/fidelity/ path* |
| IMP-1001 | V2 | **DEFER from the start.** The defect is the supplied kit's; row 18 lands the rule | `revisit_when`: *you accept the 320 px deviation recorded in the Design 2.0 TAD, or a re-export of the kit reflows at 320 px* |
| IMP-1002 | V2 | **DEFER from the start**, as IMP-0997 | `revisit_when`: as IMP-0997 |
| IMP-1003 | V1 | **CLOSE** → `APPLIED`, row 22 | `evidence_grep` on "a revision that changes a value an item clause pins (IMP-1003)" |
| IMP-1004 | V1 | **CLOSE** → `APPLIED`, row 13 (revised) | `evidence_grep` on "a retrace re-points evidence and is not a rejection (IMP-1004)" |
| IMP-1005 | V2 | **DEFER from the start**, as IMP-0997 | `revisit_when`: as IMP-0997 |
| IMP-1006 | V1 | **DEFER from the start**, joined to IMP-0500 | `revisit_when`: *a capability design under docs/improvements/ specifies a C-TECH-055 warning-row check and measures it over the conforming manifests* |
| IMP-1007 | V1 | **CLOSE** → `APPLIED`, rows 29–30 | `evidence_grep` on "never anchor a needle to text a rule requires to be rewritten (IMP-1007)" |
| IMP-1008 | V3 | **CLOSE** (revalidation 2026-10-05: the return condition below is met live; re-run the FetchXML at apply and record it as `reobserved` V3). Was: DEFER from the start. Row 15 lands; the live correction is yours | `revisit_when`: *the card app is added through the maker portal's Add existing, and a solutioncomponent re-read for the solution shows two componenttype-300 rows, one per appId* |
| IMP-1009 | n/a | **CLOSE** → `APPLIED`, row 30 and C24 | `evidence_grep` on "IMP-0500 is due in this batch" in this review document |
| *(Amendment 3)* IMP-1010 | V3 | **DEFER from the start.** The fix is in source and live: the deploy re-read all four writes flat with 0 differences ([L289](logs/pipeline.log#L289)). But the defect was a designer save emptying them, and nobody has saved the flow since. Rows 31–36 land | `revisit_when`: *the intake flow is saved in the designer in DEV, and verify-live-flow-definitions.py --env dev run straight afterwards shows Create_application, Create_new_applicant and Write_error_log_row with every column (any other difference it reports is the expected save rewrite, and is re-imported)* |
| IMP-1011 | V5 | **DEFER from the start.** Row 37 lands; only a real call from the website's form proves the decided route | `revisit_when`: *a submission from the website's form through the signed callback address creates a populated rev_application in DEV (test report step R1)* |
| IMP-1014 | n/a | **CLOSE** → `APPLIED`, row 38 | `evidence_grep` on "names its human executor and the step goes out as `REVIEWER ACTION REQUIRED`" — one line of §4, `grep -c` = 1 before it is written into the entry |
| IMP-1015 | n/a | **CLOSE** → `APPLIED`, row 39 | `evidence_grep` on "list every hit of the retired decision's words (IMP-1015)" |
| IMP-1016 | n/a | **CLOSE** → `APPLIED`, row 36 | `evidence_grep` on "`triggers.<name>.inputs.triggerAuthenticationType` (IMP-1016)" |
| IMP-1017 | n/a | **DEFER from the start.** Row 39 lands the rule; the two stale instructions are routed | `revisit_when`: *src/tests/data/README.md and intake-payloads.json _howToRun describe the signed callback address plus x-rev-client-id, and name no bearer token*. It then closes on an `evidence_grep` there |
| IMP-1018 | n/a | **DEFER from the start**, routed | `revisit_when`: *verify-intake-endpoint-auth.ps1's -Env accepts only values it can run for (test, acc, prd), or DEV gains an intake settings block and a DEV post_deploy probe* |
| IMP-1019 | n/a | **CLOSE** if decision 6 is yes and row 40 applies, on "names the DEV deploy as its own check (IMP-1019)". **Otherwise DEFER** | `revisit_when`: *decision 6 is answered* |
| IMP-1020 | n/a | **CLOSE** → `APPLIED`, rows 31–35 | `evidence_grep` on "a V4 designer save of a solution-sourced flow is itself a live write (IMP-1020)" in the technology constraints |
| *(Amendment 4)* IMP-1021 | V4 | **DEFER from the start.** Fixed by redesign in source (draft, bind, fill, read back, send), deployed to DEV; no run has filled a tab yet. Row 41 lands | `revisit_when`: *R2 and R3 of test report 20261003-2 pass in DEV: a Create Envelope run fills every in-scope tab on the draft and its read-back check passes* |
| IMP-1022 | V5 | **DEFER from the start.** Rows 42–43 land; the template and account settings are set and checked by a person | `revisit_when`: *M4 and M6 are done: the template's Required boxes and reassignment option are confirmed, and a forwarded test envelope asks for the access code and cannot be reassigned* |
| IMP-1023 | V5 | **DEFER from the start.** The chain was never built (TAD L3344); row 41 lands | `revisit_when`: *R1 of test report 20261003-2: one DEV run creates exactly one envelope for the grant, and it holds both roles* |
| IMP-1024 | V5 | **DEFER from the start.** Fixed in source (reminders before the send, L1538–L1567); row 42 lands | `revisit_when`: *R6 of test report 20261003-2: reminders are attached on the draft and the signing email arrives only after them* |
| IMP-1025 | V4 | **DEFER from the start.** The TAD is corrected; the `tabType` string is open | `revisit_when`: *A-DS-16 is closed: R2 and R3 show which tabType string the fill accepts, and the TAD records it* |
| IMP-1026 | V5 | **DEFER from the start.** Fixed in source (`phoneNumber` not set, L976); row 41 lands | `revisit_when`: *R5 or M6: the referee receives the signing link by email only, with no SMS, and the link asks for the access code* |
| IMP-1027 | n/a | **CLOSE** → `APPLIED`, no system change; repaired in the same dispatch | `evidence_grep`: "`CompositeTemplates` with `status: Created` produces a draft carrying both template roles" in the TAD, the start of the `A-DS-14` register row ([L3853](docs/architecture/revitalise-grant-automation-architecture.md#L3853)), `grep -c` = 1 (measured): the register row is where it belongs |
| IMP-1028 | V5 | **DEFER from the start.** Row 42 lands; the route is routed | `revisit_when`: *the TAD names how Create Envelope is re-issued for an existing Awarded grant after a pre-send stop (A-R74, A-R79), and one DEV run proves that route* |
| IMP-1029 | V1 | **CLOSE** if row 47 applies, on "WdlExpression.psm1` (IMP-1029)" in power-automate.md. **Otherwise DEFER** | `revisit_when`: *src/tests/solutions/_harness/WdlExpression.psm1 is committed; then apply row 47 and close* |
| IMP-1030 | n/a | **CLOSE** → `APPLIED`, row 48 | `evidence_grep` on "never track it (IMP-1030)" in `.gitignore` |
| IMP-1031 | V1 | **DEFER from the start.** Row 44 lands; the TAD amendment is routed, and the defect lives there | `revisit_when`: *TAD §5.8 step 2, ADR-067 design requirement 4 and ADR-043 state the reviewer's every-tab rule*. It then closes on an `evidence_grep` there |
| IMP-1032 | V1 | **CLOSE** → `APPLIED`, rows 45–46 | `evidence_grep` on "a candidate, not yet the cause (IMP-1032)" in `scripts/run-with-timeout.sh` |
| IMP-0500 (reviewer-deferred, due) | n/a | **Stays deferred**, annotated (row 30) | `deferred_reason` gains: *condition met 2026-10-01, 58 of 80 manifests; the diff as designed measures 37 of 261, so a design is needed (C24)*. `revisit_when` unchanged, verbatim |

**Simulated before parking.** The simulation ran in a scratch root: every top-level path is linked to this repository, except `logs/`, `scripts/` and `agents/`, which are copies. The copies had the dispositions above applied, and stub lines carrying each proposed needle. `verify-improvement-log.py --check` exits **0** in both variants of IMP-0967 (deferred, and closed with rows 6–7). Both show 0 unread and 0 fixed-in-flight. The IMP-0961 warning is cleared. The only entries left awaiting approval belong to other reviews (IMP-0855, and the governance blocker IMP-0934). The only warning left is IMP-0298's. The real log's only changes are this draft's ten `reviewed_in` stamps and its three appended findings.

*(Amendment)* **Simulated again, all 16 entries.** Same method: a scratch root with `logs/`, `scripts/` and `.engine/` copied, and stub lines carrying the needles for rows 1, 2, 6, 9, 11 and 13. Both variants of IMP-0967 exit **0**, with 0 unread and 0 fixed-in-flight. (The simulation ran before IMP-0979 was appended; that entry is the next batch's, and it is unread on the real log.) The only entries left awaiting approval are the other reviews' IMP-0855 and IMP-0934, and the only warning is still IMP-0298's. The real log's only change from the amendment is six `reviewed_in` stamps (`diff`: 6 lines).

*(Amendment 2)* **Simulated a third time: all 48 entries (the 46 stamped with this review, plus IMP-0954 and IMP-0500).** Same method: a scratch root with `logs/`, `scripts/`, `.engine/`, `knowledge/` and `config/` copied, every draft disposition applied, and a stub line carrying each needle in the copied target file. Three variants: decisions 4 and 5 unanswered; decision 5 answered (IMP-0992 closed on row 19(b)); decision 4 answered "no gate" (IMP-0982 closed on row 28). All three exit **0**, with 0 unread and 0 fixed-in-flight. The only entries left awaiting approval are the other reviews' IMP-0855 and IMP-0934. The warning that IMP-0979 was cited but unstamped is gone; the only warning left is IMP-0298's. The real log's only changes from Amendment 2 are 30 `reviewed_in` stamps and the appended IMP-1009 (`diff`: 30 changed lines and 1 added).

*(Amendment 3)* **Simulated a fourth time, for this amendment's nine entries.** A scratch root with `logs/`, `constraints/` and `knowledge/` copied, and the verify skill and the architect file copied out of their symlinked folders; a stub line carrying each needle; every other path linked. The nine dispositions above applied on a copy of today's log, the earlier 48 left as they are (they were simulated by Amendment 2). Two variants, decision 6 unanswered and yes: both exit **0**, with 0 unread and 0 fixed-in-flight. Each variant prints one warning per earlier entry of this review saying the keyword was given and the entry left behind; that is what a partial simulation produces by construction, and the full apply closes those entries in the same step. The real log's only changes from Amendment 3 are 8 `reviewed_in` stamps and the appended IMP-1020 (`diff` against the pre-simulation copy: identical).

*(Amendment 4)* **Simulated a fifth time, for this amendment's twelve entries.** A scratch root with `logs/`, `knowledge/technology/`, `scripts/run-with-timeout.sh` and `.gitignore` copied, a stub line carrying each needle in its copied target, and every other path linked (hidden ones included: a first run without `.claude/` reported a missing needle file for an unrelated applied entry). The twelve dispositions above applied, the earlier 57 left as they are. Two variants, row 47 held (IMP-1029 deferred) and applied (IMP-1029 closed, `capability: true`): both exit **0**, with 0 unread and 0 fixed-in-flight. The only warnings are the 55 "keyword given, entry left behind" lines a partial simulation produces by construction, and IMP-0298's. The real log's only change from Amendment 4 is 12 `reviewed_in` stamps (`diff` against the pre-stamp copy: 12 changed lines; against the pre-simulation copy: identical).

**Routed work, to be re-measured at apply before it is handed on:**

| To | Item | From |
|---|---|---|
| the session that authored the check-7 descent (automation-agent, via lead-agent) | Dev Summary revision for the failure-path change in flows 1001, 1002 and 1007 (Describe_the_failure If → Switch, descent queries, the new If in 1007); correct the "exception expires 2026-09-30" notes at [L11244](docs/development/revitalise-grant-automation-dev-summary.md#L11244) | IMP-0968 |
| lead-agent | Commit the deployed working-tree changes, including the untracked `scripts/verify-live-flow-definitions.py`; rows 6–7 here and 1–6 of review 2026-09-30 wait on it | IMP-0967, IMP-0964 |
| reviewer | The designer-save question from review 2026-09-29, still unanswered | IMP-0959 |
| lead-agent | **RESOLVED 2026-10-05 — WITHHOLD at apply** (all six tracked). *(Amendment)* Add the six untracked WI-0005 files to the same commit: `domain/applicationDetailLayout.ts` and `.test.ts`, `test/detail-harness-app.tsx`, `test/visual/application-detail-layout.visual.spec.ts`, `detail-harness.html`, and `docs/development/trustee-portal-pack-field-map.md` | IMP-0975, IMP-0976 |
| development-agent (frontend) | *(Amendment)* Measure the shared `.definitions` grid at 320 px in the Chromium suite for every `Definitions` consumer, or give it the same narrow-width stacking the pack rows now have. Delivery work under `wbs:6.8`, not a rule change | IMP-0976 |
| pm-agent | *(Amendment)* Re-read the 21 items from `FeedbackDeployment_20-09-2026.xlsx` whose status comment never became acceptance, and add a clause wherever the comment states a requirement (checklist L247). Not classified here: how many of the 21 comments state one | IMP-0973 |
| reviewer | *(Amendment)* Your verdict on the rebuilt WI-0005 screen in DEV | IMP-0973, IMP-0824 |
| reviewer | **RESOLVED 2026-10-05 — WITHHOLD at apply** (two componenttype-300 rows measured in DEV). *(Amendment 2)* Add the card app to the solution through the maker portal's *Add existing* (owed since the deploy, [L284](logs/pipeline.log#L284)); then pipeline-agent re-reads the solution's componenttype-300 rows | IMP-1008 |
| pipeline-agent (owner of the DEV post_deploy notes) or development-agent | *(Amendment 2)* Correct the three notes that credit membership to the push ([L1099](config/revitalise-grant-automation-pipeline.yml#L1099), [L1936](config/revitalise-grant-automation-pipeline.yml#L1936), [L2220](config/revitalise-grant-automation-pipeline.yml#L2220)): membership came from the 22 August manual add (IMP-1008). The Test/Production conclusion stands for an app already in the solution | IMP-1008, IMP-0983 |
| architect-agent | *(Amendment 2)* Main TAD §9.3 ([L1575](docs/architecture/revitalise-grant-automation-architecture.md#L1575)) and Design 2.0 TAD A-TR-15 and R-D2-4: record the refutation and its cause; re-measure the supplied-assets page, which still says the `Designsystem/` working tree is clean ([L36](docs/reference/supplied-assets.md#L36)) while two drops are untracked | IMP-1008, IMP-0992 |
| pm-agent | *(Amendment 2)* After row 16 lands, relink WI-0055..WI-0105's components to `operation:code-app-push@trustee-review-portal-cards`; after row 23, retitle WI-0052 to its relinked order | IMP-0986, IMP-0994 |
| development-agent (frontend) | *(Amendment 2)* First app: give `.tableScroll` `position: relative` and measure its tables at 320 px with sort hints present; both apps: derive the visual-test port per app in one parity-preserving change. Delivery work under `wbs:6.3` (unbilled) or `wbs:6.8` | IMP-0999, IMP-0988 |
| development-agent | *(Amendment 2)* `provisioning/deploymentSettings/settings-rows.notes.md` ([L94](provisioning/deploymentSettings/settings-rows.notes.md#L94)): record DEV's current RoundStatisticsHistory* values and who set them, or say the notes give initial values only | IMP-0995 |
| reviewer | *(Amendment 2)* Decisions 4 and 5 | IMP-0982, IMP-0992 |
| — | *(Amendment 3)* **WITHHELD at apply:** the row above that sends you "the designer-save question from review 2026-09-29". It is answered by evidence (C27), so it is no longer yours to answer | IMP-0959, IMP-1010 |
| development-agent (owner of the pipeline config) | *(Amendment 3)* Give `verify-live-flow-definitions.py` a mode that reports only flows written after the last import, and run it in DEV `pre_deploy` and before test-agent's live runs. Its DIFFERS check compares against current source, so before a deploy it would report every intended change | IMP-1010 |
| development-agent | *(Amendment 3)* Rewrite the run instructions in [src/tests/data/README.md L197](src/tests/data/README.md#L197) and [intake-payloads.json L12](src/tests/data/intake-payloads.json#L12) for the signed callback address plus `x-rev-client-id`, with no bearer token | IMP-1017 |
| identity-agent or development-agent | *(Amendment 3)* [verify-intake-endpoint-auth.ps1 L75](provisioning/entra/verify-intake-endpoint-auth.ps1#L75): narrow `-Env` to `test`, `acc`, `prd`, and say why in its help, as its sibling does ([L52](provisioning/entra/verify-intake-callback-url.ps1#L52)) | IMP-1018 |
| architect-agent | *(Amendment 3)* TAD §12.3: `A-INT-15` closed on your designer-written `TEST_Binding` (the Dev Summary has the evidence; test report D-04), and `A-INT-11` closed at V3 by the 2 October import | IMP-1014 |
| reviewer | *(Amendment 3)* Test report step R1, a real submission from the website through the signed address; the callback-address capture and compare, which need your provisioning certificate; removing the throwaway `TEST_Binding` flow from DEV; and decision 6 | IMP-1011, IMP-1014, IMP-1019 |
| architect-agent | *(Amendment 4)* Amend TAD §5.8 step 2 ([L1154](docs/architecture/revitalise-grant-automation-architecture.md#L1154)), ADR-067 design requirement 4 and ADR-043 ([L2446](docs/architecture/revitalise-grant-automation-architecture.md#L2446)) to your code-review rule: every tab except signature, signer name and date signed; placeholders matched per role at run time; the applicant's agreement checkbox sent unticked and marked Required on the template; the unmapped-tab stop; "left for the referee" becomes "cleared to empty by the flow" | IMP-1031 |
| architect-agent | *(Amendment 4)* Name how Create Envelope is re-issued for an existing Awarded grant after a pre-send stop ([A-R74](docs/architecture/revitalise-grant-automation-architecture.md#L3659), [A-R79](docs/architecture/revitalise-grant-automation-architecture.md#L3664)): an update trigger on a re-issue field, a manual route, or run-history Resubmit confirmed by one DEV measurement | IMP-1028 |
| lead-agent | *(Amendment 4)* Commit the deployed Create Envelope flow, its notes and tests, and the untracked `src/tests/solutions/_harness/WdlExpression.psm1` that the tracked contract tests import; row 47 waits on it | IMP-1029 |
| commercial-agent | *(Amendment 4)* Confirm whether the possible change order for recipient authentication still stands: the TAD now records an access code, free per the reviewer ([L3711](docs/architecture/revitalise-grant-automation-architecture.md#L3711)) | IMP-1022 |
| reviewer | *(Amendment 4)* R1, R2, R3, R5 and R6 from test report 20261003-2, and M4 and M6 from the TAD; six of this amendment's deferrals close on them | IMP-1021, IMP-1022, IMP-1023, IMP-1024, IMP-1025, IMP-1026 |

---

## 6. Digest impact

| | Before this review | Draft (regenerated) | Amendment 1 (regenerated) | Amendment 2 (regenerated) | Amendment 3 (regenerated) | Amendment 4 (regenerated) | After apply |
|---|---|---|---|---|---|---|---|
| Log entries | 965 | 968 (IMP-0970, IMP-0971, IMP-0972 appended) | 975 (IMP-0973 to IMP-0978 in scope; IMP-0979 appended by a live development-agent during this dispatch, not processed here) | 1005 (IMP-0979 to IMP-1008 in scope; IMP-1009 appended by this amendment) | 1016 (IMP-1010, IMP-1011, IMP-1014 to IMP-1019 in scope; IMP-1012 and IMP-1013 applied by review 2026-10-02; IMP-1020 appended by this amendment) | 1028 (IMP-1021 to IMP-1032 in scope; none appended) | 1028 or more |
| Distinct lessons | 949 | 952 | 959 | 989 | 1000 | 1012 | 1012 or more |
| Recurring classes (x≥2) | 73 | 73 (`log-timestamp-not-taken-from-the-clock` x2 → x3, `pipeline-dispatch-stops-before-declared-post-deploy` x2 → x3) | 73 (`log-timestamp-…` x3 → x4, `no-assertion-on-shipped-content` x32 → x36 with IMP-0979; the two new classes are x1) | 76 (measured: `log-timestamp-…` x5, `supplied-design-asset-assumed-wcag-compliant` x3, `design-values-read-from-source-not-rendering` x2, `item-acceptance-contradicts-approved-design` x2, `stale-deferral-uncaught-across-sessions` x8) | 78 (measured: rows in the recurring-classes table; `live-definition-overwritten-outside-the-pipeline` x2 is among the new ones) | 78 (measured; none of the twelve opens a recurring class, and `platform-contract-guessed-not-groundtruthed` is x80 by `class_instance_of`) | 78 |
| Digest lines | 606 | 606 | 606 | 611 | 613 | 613 | 613 (re-measured at apply) |

Regenerated after the three appends, and again after the amendment's six stamps (`--check` exits 0 both times). `generate-known-failure-modes.py --check` exits 0. `verify-derived-counts.py` reports 6 drifted claims. Five predate this review and belong to other files' owners: the `rev_setting` count twice in the pipeline config, two secured-column counts in the Dev Summary, and the REV Trustee role header. The sixth is row 10.

*(Amendment 2)* Regenerated after the 30 new `reviewed_in` stamps and IMP-1009 (`--check` exits 0). `verify-derived-counts.py` now reports 7 drifted claims. Five are the same as above. The sixth is row 10 (now 69). The seventh is new and is caused by this regeneration: the digest is 611 lines, and [generate-known-failure-modes.py L46](scripts/generate-known-failure-modes.py#L46) says 606. Apply corrects it in both copies, re-measured after the final regeneration.

*(Amendment 3)* Regenerated after the 8 new stamps and IMP-1020 (`--check` exits 0). `verify-derived-counts.py` reports 8 drifted claims. The digest line count is now 613 against the 612 the generator says ([L46](scripts/generate-known-failure-modes.py#L46)), still corrected at apply. Row 10's verify-script count is 69. A new one, the `Designsystem/` tracked-file count (131 stated, 285 measured, [supplied-assets L36](docs/reference/supplied-assets.md#L36)), belongs to the supplied-assets re-measure already routed to architect-agent. The rest are other files' owners', as before.

*(Amendment 4)* Regenerated after the 12 stamps (`--check` exits 0; 1028 entries, 1012 lessons, 613 lines, 78 recurring classes). `verify-derived-counts.py` reports the same 8 drifted claims as Amendment 3 and no new one; row 10's count is still 69.

**Apply-time obligations:** regenerate the digest, then run `--check`, `verify-derived-counts.py`, `verify-engine-instance-split.py`, `verify-build-config.py config/revitalise-grant-automation-build.yml`, every added or edited script's `--selftest`, and `verify-work-items.py --check`. *(Amendment)* Also: `grep` the new §12c and ingestion-checklist text for this client's names before the engine commit (skill §6), and `grep -c` each new needle = 1.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-30-improvement-review-2.md

Findings processed: 69 NEW  →  38 clusters
Regression check:   24 prior changes audited, 13 classes recurred
Proposed:           0 constraints (cap 3) + 3 constraint amendments (row 40 only on
                    decision 6), 12 gates/scripts (row 14 only on decision 3; row 19's
                    second half only on decision 5), 20 skill/knowledge edits (row 47
                    held behind a commit), 9 agent-file edits, 1 template edits,
                    3 other, 0 retirements
Altitude calls:     12 generalised from instance to class, 11 left as notes
Digest:             regenerated at draft (amended four times) — 1012 lessons,
                    78 recurring classes; will regenerate at apply

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Record of what is done on approval

**Applied 2026-10-05, 10:55–11:30**, on the reviewer's verbatim turn *"Agreed with all suggested improvements for the questions 1 - 6 and D1 - 3 / Approve Improvements for all reviews, process them one by one."* (Xander Lykopoulos), relayed by lead-agent at 10:41 ([routing.log](logs/routing.log)). Third of four sequential dispatches. Reviews 2026-09-23-7 and 2026-09-27 were applied before it, and 2026-10-05 is applied after it. Nothing is committed (the dispatch said not to).

### Decisions, recorded verbatim as "agreed with suggested"

| # | Answer | What it made happen |
|---|---|---|
| 1 | agreed with suggested — refuse `built` without declared components | Row 8 applied |
| 2 | agreed with suggested — keep the "post-deploy step skipped" findings open | IMP-0971 deferred beside IMP-0879 and IMP-0906, which are unchanged |
| 3 | agreed with suggested — yes | Row 14 applied |
| 4 | agreed with suggested — yes, as a commercial-agent design | Row 28 applied (narrowed, below); the design is routed to commercial-agent |
| 5 | agreed with suggested, as amended by the revalidation — the `(1)` copy is the replacement | Row 19(a) applied. Row 19(b) is **held** until the old drop is removed (below) |
| 6 | agreed with suggested — yes | Row 40 applied ([C-TECH-058](constraints/technology/technology-constraints.md#L128)) |

### What landed

44 rows: the revalidation's 42 valid rows, and rows 15 and 43 with the facts the revalidation added. Each row's entries were closed as the row landed.

- **Log time comes from the clock** — [allocator](scripts/allocate-improvement-id.py#L46), new [log-line.py](scripts/log-line.py#L11), the eight format blocks ([WORKFLOW](agents/WORKFLOW.md#L661) and the other seven), the [logging skill](skills/how-to-log-an-improvement.md#L63), [testing-tools](knowledge/technology/testing-tools.md#L165) (rows 1–5). Self-tests 14/14 and 8/8.
- **Lead-agent's per-result check gets `--since`** ([lead L436](agents/lead-agent.md#L436), row 9).
- **The ledger's dated rules** ([work_items.py L155](.engine/scripts/lib/work_items.py#L155), rows 8, 13, 14, 23). Built needs declared components. A clause naming a supplied document needs a test line that names it. Reopens count rejections only, with `reopen --retrace`. `link --title`. All bind events dated **after 2026-10-05**; earlier events fold as before.
- **One push label per app** ([deploy_markers L75](.engine/scripts/lib/deploy_markers.py#L75), [check 15](scripts/verify-pipeline-config.py#L577), [the three DEV `app:` keys](config/revitalise-grant-automation-pipeline.yml#L1238), [pipeline-agent WRITE line](agents/pipeline-agent.md#L295), rows 16–17).
- **Verify skill** — §12c's transcription test ([L969](skills/how-to-verify-a-platform-contract.md#L969)), §12d ([L972](skills/how-to-verify-a-platform-contract.md#L972)), what a designer-saved flow proves ([L107](skills/how-to-verify-a-platform-contract.md#L107)), a template's field set, the outside-party row ([L49](skills/how-to-verify-a-platform-contract.md#L49)), §6 step 0, the designer executor, the V4 save paragraph ([L612](skills/how-to-verify-a-platform-contract.md#L612)) (rows 11, 21, 32, 37, 38, 41, 44).
- **Intake skill** — the path rule ([L257](skills/how-to-intake-external-documents.md#L257)) and the [Supplied Design Bundle Checklist](skills/how-to-intake-external-documents.md#L164) (rows 12, 18).
- **Design-source gate** — every top-level drop in scope by its root path ([L98](scripts/verify-design-source-coverage.py#L98)), with [C-TECH-075](constraints/technology/technology-constraints.md#L145) amended (rows 19(a), 20).
- **Constraint amendments** — [C-TECH-053](constraints/technology/technology-constraints.md#L108) and [C-TECH-058](constraints/technology/technology-constraints.md#L128) (rows 31, 40). No new constraint: 0 of 3 used. Live rows 88 and retired rows 10, re-derived (88 includes C-TECH-080 from review 2026-09-27).
- **Agent files** — architect: [clauses a TAD overrides](agents/architect-agent.md#L276) and the [re-decided ADR search](agents/architect-agent.md#L138); [commercial](agents/commercial-agent.md#L27); [improvement-agent needle rule](agents/improvement-agent.md#L692); [pipeline check (c)](agents/pipeline-agent.md#L480) (rows 22, 28, 29, 33, 39).
- **Templates and example config** — the live re-read after a V4 save ([dev summary](templates/dev-summary-template.md#L96), test report, pipeline.yml.example) (row 35). **Workflow checklist** — three lines ([L28](skills/how-to-design-a-workflow.md#L28), row 42).
- **Knowledge** — [Code App membership readings](knowledge/technology/code-apps.md#L548) and [styling lines](knowledge/technology/code-apps.md#L657) (rows 15, 27); [the DocuSign section](knowledge/technology/power-automate.md#L311) and the Power Automate bullets (rows 26, 36, 43); [build-and-deploy](knowledge/technology/build-and-deploy.md#L226) (rows 34, 46).
- **Scripts** — [assumption-marker grammar](scripts/verify-assumption-markers.py#L124), [baseline expiry warning](scripts/lib/gate_baseline.py#L152) and [its NOTE](scripts/verify-build-config.py#L1322), [timeout message](scripts/run-with-timeout.sh#L104) (rows 24, 25, 45). Every script pair was edited in both copies (`cmp` identical). The exception is `verify-build-config.py`, whose two copies differ by design, so each was edited in place.
- **Housekeeping** — `testResults.xml` is ignored ([.gitignore L22](.gitignore#L22)) and removed from the index with `git rm --cached`. That change is **staged, not committed**. IMP-0764's needle moved and IMP-0500's deferral was annotated (rows 48, 30).

Row 15 carries the fourth reading. Row 43 carries the three measured hotfix facts: the two `tabType` spellings, a Company tab the signer sees empty, and `RECIPIENT_UPDATE_FAILED` behind a 200.

**Row 10** was re-derived at 71 `verify-*.py`, the figure review 2026-09-27 already wrote. No edit, and review 2026-10-05 row 4 needs none either.

### Narrowed, held, withheld at apply

- **Row 28 NARROWED.** The drafted selector, "a known-exceptions entry whose `gate` is `none`", matches **0** entries literally and **2** by prefix. One of the two is EX-005, a DPIA risk acceptance over billable work: a named false positive. The applied selector is `matches` beginning `UNBILLED`, which matches EX-008 only.
- **Row 19(b) HELD**, a new hold at apply. Measured on the real tree it finds **1 true finding**: the old drop's `ui_kits/trustee-review-portal` is cited by no full path. Wiring it today would turn the HARD `design-source-coverage` step red until architect-agent replaces the old drop, which is what decision 5 asks for. Apply it in the same change as that removal.
- **Row 8's cutoff** is "after 2026-10-05", as the draft's Amendment re-measurement already required.
- **Rows 6–7 HELD.** The check-7 descent is still in no commit, and Create Envelope's `Find_the_failed_action` fails the plain gate ([review 2026-10-05 L132](docs/improvements/2026-10-05-improvement-review.md#L132)).
- **Row 47 HELD.** `WdlExpression.psm1` is still untracked, re-measured at 0 `git ls-files` hits.
- **Withheld from the routed table, already resolved:** the card-app *Add existing* (re-measured at V3, below) and the WI-0005 commit (all six files tracked). The designer-save question was already withheld (Amendment 3). Partly resolved: the commit item now covers only the flows, the check-7 descent and `WdlExpression.psm1`, because `verify-live-flow-definitions.py` is tracked.
- **IMP-1039 to IMP-1041 are not folded in.** Their proposed changes were never in front of the reviewer, so applying them on this keyword would apply unapproved rules. They carry `excluded_by` naming this review and stay unread for the next batch, as the revalidation said. IMP-1040 is cited in IMP-1008's closure as the record of the stale carried row.

### Entries

69 entries: **34 APPLIED**, **32 DEFER** with a reviewer-accepted `deferred_reason` and their approved `revisit_when` verbatim, **2 REJECTED** (IMP-0998, IMP-1000), and IMP-0500 annotated and still deferred. Three closures carry a `reobserved` record:

- IMP-1008 at V3: `pac env fetch` on `solutioncomponent` in DEV at 2026-10-05 09:14:13Z shows two componenttype-300 rows in `RevitaliseGrantAutomation`, one per appId (`b0483396…` created 2 Oct 09:10 UTC, `70869c95…` created 22 Aug).
- IMP-0961 at V2: `npm audit --audit-level=high` re-run at 09:20:36Z exits 0 with the one triaged advisory.
- IMP-0954 at V3: pipeline-agent's import of 30 September.

### Routed at apply

The rows in §5 still stand, except the three withheld above. These are added:

| To | Item | From |
|---|---|---|
| architect-agent | Decision 5: replace `Designsystem/Revitalise Design System/` with the `(1)` copy, cite the replacement's paths, and re-measure [supplied-assets L36](docs/reference/supplied-assets.md#L36) (it still says 131 files). Then improvement-agent applies row 19(b) in the same change | IMP-0992 |
| commercial-agent | Decision 4: a design under `docs/improvements/` for a per-item billing check (a worklog session names no items today) | IMP-0982 |
| architect-agent | Record the measured `tabType` strings (prefill `textTabs`, recipient `Text`, [pipeline L308](logs/pipeline.log#L308)) against `A-DS-16`; the TAD still says "unmeasured" | IMP-1025 |
| pm-agent | Row 16 is live: **62 items** carry the plain `operation:code-app-push` label (55 verified, 6 deployed, 1 reopened). Their next DEV deploy is refused until they are relinked. Card-app items WI-0055..0105 go to `@trustee-review-portal-cards`, the rest to `@trustee-review-portal`. Retitle WI-0052 with `link --title` | IMP-0986, IMP-0994 |

### Verification

- **Gates:** `verify-improvement-log.py --check` exits 0 (275 NEW, 744 APPLIED, 18 REJECTED), with 0 entries of this review awaiting approval and 0 blockers. `verify-build-config.py` PASS (102 steps, 75 gates). `verify-pipeline-config.py` exits 0; before the `app:` keys, check 15 found 3 findings, all 3 true. `verify-design-source-coverage.py` PASS: 3 drops, 0 findings. `verify-assumption-markers.py` PASS: 106 → 117 rows, 0 new failures, 1 new note, true. `verify-class-defences.py` OK. `verify-engine-instance-split.py` exits 0.
- **Self-tests:** allocator 14, log-line 8, work-items (incl. 17 new cases), post-deploy-completeness 15, design-source 6, assumption-markers 16, gate_baseline, run-with-timeout 7. All pass.
- **Real ledger:** `verify-work-items.py --check` adds **0** findings. Its 1 failure, WI-0009, is pre-existing and identical on the pre-change library. WI-0045 moved 1 → 0 reopens and WI-0008 2 → 1, as predicted.
- **Pester:** the build suite is 141 passed, 3 failed. The 3 are `domain-invariants`, the special-category register and `shipped-content`, run over working-tree solution source this review did not edit. They are the hotfix session's red source gates recorded by review 2026-10-05.
- **Not verified:** no new rule has met a real event yet. The dated ledger rules bind from 6 October, and per-app labels are proven by fixtures and by check 15 on the real config, never by a deploy. Rows 41–44 and the knowledge lines are prose. Nothing here is above V1 except the three re-observations.
