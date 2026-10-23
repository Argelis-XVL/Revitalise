# Improvement Review — 2026-10-23 (2)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 16 `NEW` → 8 clusters (9 unread; IMP-1251, logged by this review; and 6 reviewer-deferred entries whose return condition was met: 2 by this deploy, 4 by the reviewer's designer check)
**Trigger:** post-deploy batch. DEV deploy of build `revitalise-grant-automation-20261023-2`, PARTIAL at V3 ([pipeline.log L473](logs/pipeline.log#L473)), `wbs:2.2`, items WI-0150 to WI-0153. It also carries the three clean-ups the reviewer left for this run ([routing.log L1794](logs/routing.log#L1794)).
**Status:** APPLIED 2026-10-23 15:45 — `APPROVE IMPROVEMENTS` (reviewer Xander Lykopoulos, verbatim "Approve improvements", relayed by lead-agent). Rows 1–6 applied as drafted; 13 entries closed, 3 deferred; routed work R1a, R1b, R1d and R2 handed to lead-agent. Not committed. Applied record: §8.
**Amendment (2026-10-23, before the draft was presented):** *Folded in:* the reviewer's statement relayed at 15:28 that the scrub-flow designer check is done. IMP-1095, IMP-1098, IMP-1156 and IMP-1159 now close in cluster C8, with V4 `reobserved` in his words, and the time of his check is recorded as not stated. The gate block, header, summary, dispositions, §5 and digest table were reconciled, and the simulation was re-run: 0 unread, 0 awaiting approval, 0 fixed-in-flight blockers. *Still to do:* nothing in this document. Everything waits on the keyword.
**Serves:** `wbs:system`; the findings come from `wbs:2.2` work, and IMP-1242 from `wbs:6.3` (unbilled)
**Gate:** `APPROVE IMPROVEMENTS`

---

## Summary

Nine new findings came out of the settings-category work, and all of them are small. I propose one gate fix, one knowledge note, three instruction edits and one template comment. Thirteen entries close on the keyword, nine of them on today's DEV evidence or your word, and three wait on routed work. That includes the three scrub-flow blockers, on your statement that the designer check is done. Your three clean-ups are in, but none of them is a file I may edit. Two go to development-agent and one to commercial-agent, and the work-item clause cannot be corrected by the ledger tool at all. You have the keyword and one optional decision.

## What has been built

Nothing is applied yet. The draft proposes the following.

1. **The design-document coverage check stops reading a table's own name as one of its columns, and its error message says how to write a choice-set name** — [verify-tad-coverage.py L258](scripts/verify-tad-coverage.py#L258), [L1109](scripts/verify-tad-coverage.py#L1109).
   This morning the check failed twice on a revision paragraph that named its own table and the new choice set in code formatting. I rebuilt that paragraph in a scratch copy of the design document. Today's check gives 2 failures, and the fix gives 1. The one left is the choice-set name, and the message now tells the author to write it without code formatting. On the real document both versions give 0.

2. **A script handed to you to run has been run once by whoever hands it over, and again by whoever patches it** — [pipeline-agent.md L287](agents/pipeline-agent.md#L287), [dataverse.md L492](knowledge/technology/dataverse.md#L492).
   Two read-only probe scripts reached you without ever being run, and both failed. One was patched and failed again on a different line. The cause was the same both times: a syntax check passed what the script's strict mode rejects at run time. The knowledge note adds the two specific traps to the strict-mode section that already exists.

3. **Closing an item that rewrites text in a data file means searching the tests for that text and running the full test suite** — [development-agent.md L272](agents/development-agent.md#L272).
   The first build failed after 15 minutes because a Python test still expected the old wording of four settings descriptions. The item had been closed on the provisioning tests alone.

4. **Standing build warnings are carried into every new Dev Summary, not only a new feature's** — [development-agent.md L343](agents/development-agent.md#L343), [dev-summary-template.md L107](templates/dev-summary-template.md#L107).
   The rule already existed, but its wording covered only "a new feature". The settings work was a new Dev Summary under an existing feature, so the rule did not seem to apply. The template comment puts the same instruction where the table is written.

## Elements changed

| File | Repository | Change |
|---|---|---|
| [verify-tad-coverage.py](scripts/verify-tad-coverage.py#L258) + its `.engine` twin | both (byte-identical pair) | §A |
| [pipeline-agent.md](agents/pipeline-agent.md#L287) | engine | §B.1 |
| [dataverse.md](knowledge/technology/dataverse.md#L492) | instance | §B.2 |
| [development-agent.md](agents/development-agent.md#L272) | engine | §C, §D.1 |
| [dev-summary-template.md](templates/dev-summary-template.md#L107) | engine | §D.2 |

## What is still open

**Your three clean-ups are routed, not applied.** The settings description is in a provisioning script, the stale length checks are in the test suite, and the work-item clause is in the ledger. None of these is a file this agent edits. The routed-work table in §3 gives the exact change for each one. After approval, one development-agent dispatch covers the first two plus the stale bundle figure. The description fix reaches DEV only when you next run the city-register script, which writes descriptions on every run.

**The work-item clause cannot be corrected by the ledger tool.** WI-0150 is deployed, and the tool refuses any change to its wording past `ready`. Clause 3's evidence already points at the right script, so only the sentence is wrong. The fix I recommend is a one-line note in the change order the clause cites. This is the second time a design change has run into this limit, so I logged it.

**A mechanical check for missing warning rows is still not viable.** The standing-warnings rule has now failed twice, and that normally calls for a check in a script. I built two forms of it and ran both against all 56 consecutive build pairs. Both mostly flagged rows that were in fact present but named differently. Results are in §2 (C1), and the warning-row design stays deferred.

## What you need to decide

**Approve these 6 changes?**

**Problem** — Today's findings cost a failed build, a held package and two failed scripts on your machine; each row targets one of those causes.
**Suggested fix** — Reply `APPROVE IMPROVEMENTS`. I apply §A to §D, close 13 entries (the three scrub-flow blockers and IMP-1159 among them), and defer 3 until their routed work lands.
**What happens if you don't** — The next new Dev Summary or reviewer probe script is likely to repeat this morning's round trips.
[§3, proposed changes](docs/improvements/2026-10-23-improvement-review-2.md#L233)

---

**Optional: commission a design for correcting a delivered item's acceptance wording?**

**Problem** — The ledger cannot correct an item's wording after `ready` without logging a rejection nobody made. This is now the second time.
**Suggested fix** — Not now. Record corrections in the cited source (as for WI-0150), and commission the design when a third case appears or when a client-visible item needs it.
**What happens if you don't** — Nothing breaks. Corrected wording lives in the change order or plan line, and the ledger keeps the original sentence.
[§2, cluster C7](docs/improvements/2026-10-23-improvement-review-2.md#L202)

---

Verification: scratch copy of the coverage check — selftest 38 of 38, and the new fixture fails against today's code. Real design document: 0 failures before and after. Rebuilt defective paragraph: 2 failures before, 1 after. Two candidate warning-row checks measured over 56 build pairs (C1). Field-length gate with fixtures: exit 0, including the known-bad settings fixture. Post-deploy completeness check, `--pending` for DEV: 0 findings. Work-items check: exit 0. The dispositions were simulated on a scratch copy of the log: 0 unread, 0 awaiting approval, and the only 5 errors are needles the apply will write. **Not verified:** none of §A to §D is written yet, beyond the scratch copy of §A. Nothing live was read by this review. The DEV evidence for the closures is the reviewer's and pipeline-agent's, quoted in §2 with links.

---

## 1. Regression check — did the last review's changes work?

The last review applied was 2026-10-23 (1), at 06:50. Since then, nine findings. None is in a class that review targeted. One class that review 2026-10-22 (3) targeted, with prose, has recurred, so it is included.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Row 1: last green build keyed on the recorded build config | 2026-10-23 06:50 | `shared-build-config-feature-name-misderived` | NO | **Working.** Both of today's builds found their base under the sibling portal's folder (`trustee-portal-design-2-20261022-4`, commit `ca3797b`), and ran in full only because the engine changed, which is correct |
| Row 2: manifest check reads the recorded config | 2026-10-23 06:50 | same | NO | **Working.** Re-run now on the `20261023-2` manifest without `--build-config`: exit 0 |
| Row 3: drift on a deferred item is a note | 2026-10-23 06:50 | `work-item-evidence-orphaned-by-folder-rename` | NO | Not exercised: no defer since. Unscoped check today: 0 failures, 48 notes |
| Row 4: build-agent wording | 2026-10-23 06:50 | same | NO | No finding names it |
| Review 2026-10-22 (3) row 12(b): carry the last green manifest's warnings into a new feature's Dev Summary ([development-agent.md L343](agents/development-agent.md#L343)) | 2026-10-22 | `untriaged-tool-warning` | **YES — IMP-1250** | **Prose did not hold.** The rule said "a new feature", and the settings Dev Summary is a new document under an existing feature. Escalation to a script was measured and fails (C1), so this review narrows the wording and adds the instruction where the table is written |

**Changes whose class recurred after a *prose* fix:** `untriaged-tool-warning` (IMP-1250 after IMP-1237's rule). Escalation is required, and C1 shows the measurement that rules out a script today.
**Changes whose class recurred after a *gate*:** none.

---

## 2. Clusters and promotion decisions

```
CLUSTER: untriaged-tool-warning  (x2 here: IMP-1250, IMP-1242; class x29 in the log)
Altitude:   CLASS, at the authoring point. IMP-1250 is the recurrence after IMP-1237's prose; the
            rule existed and its scope word ("a new feature") excluded the case that happened.
Ladder row: recurrence after prose -> gate, MEASURED and not viable; falls back to "agent had the
            information" -> agent + template edit
Becomes:    row 5, development-agent.md: the carry rule applies to every new Dev Summary document,
            and names the steps a source-gates-only run never sees (§D.1).
            row 6, dev-summary-template.md §11 comment: carry every warnings_detail entry of the
            last green manifest of the same config, naming the step (§D.2).
            IMP-1242: routed to development-agent (R1d)
Retires:    nothing
Cites:      IMP-1250, IMP-1242
Residual:   No mechanical check. build-agent's C-TECH-055 read at packaging still catches the
            omission, and today it cost 2 minutes, because the artifact was packaged without a
            re-run (routing.log L1799-L1803).
```

**The two scratch checks, measured over every pair of consecutive green manifests that carry `warnings_detail` (56 pairs).**

| Candidate | Property checked | Result | Why it fails |
|---|---|---|---|
| Step name in the Source step column | every step in the previous green manifest appears in the current Dev Summary's warning table | 187 of 283 steps "missing" | Every one of these builds passed C-TECH-055 at packaging, so these are rows present under another name ("Vite build", "npm ci", "pack-managed / pack-unmanaged") |
| Citing link to the previous triage document | a cross-document pair's current table links the document the previous manifest named | 9 misses in 27 cross-document pairs | The parent Dev Summary triages these warnings itself and cites no one. One miss is a manifest whose `triaged_in` is prose, not a path |

The first false-alarm rate is too high to wire, and so is the second. This matches the September result (37 of 261 signatures). The reviewer-deferred warning-row design (IMP-1006) is the right home, and its return condition is unchanged.

**IMP-1242's premise, re-measured now:** `verify-derived-counts.py` still reports [dev summary L4893](docs/development/revitalise-grant-automation-dev-summary.md#L4893) at 1205 kB against 858 in the budget file. It also reports a second drift, the digest line count (640 in prose, 642 now), which comes from regenerating the digest. The apply corrects that one (§3, apply step 5).

```
CLUSTER: untested-hand-handed-script  (x2: IMP-1246, IMP-1247)
Altitude:   CLASS. The property is "a script the reviewer is asked to run has been executed by the
            agent handing it over". Two agents (development-agent, then lead-agent patching it),
            one cause: a parse check accepts what StrictMode throws on.
Ladder row: agent had the information and still did the wrong thing -> agent edit; plus one
            knowledge line for the two concrete traps
Becomes:    row 2, pipeline-agent.md, Reviewer-Executed Operations: one paragraph after the zsh
            paragraph (§B.1). This is the section development-agent.md L183 points every agent to.
            row 3, dataverse.md, StrictMode section: @odata.nextLink and the $select escape (§B.2)
Retires:    nothing
Cites:      IMP-1246, IMP-1247
Residual:   No gate: one-off reviewer scripts are not build inputs. The rule depends on the
            handing agent, and the knowledge note on the author.
```

**Premises re-measured.** The StrictMode absent-property rule already exists ([dataverse.md L469](knowledge/technology/dataverse.md#L469)), so the probe authors had it, and the new line is a cross-reference, not a new rule. `@odata.nextLink` appears nowhere in `knowledge/` beyond a flow-pagination note. Nothing in `agents/` or `skills/` asks for a reviewer script to be executed before hand-over (searched for "probe", "reviewer-run", "hand the reviewer"). The finding's proposed home, `how-to-verify-a-platform-contract.md`, is about evidence levels. The `REVIEWER ACTION REQUIRED` block is defined in pipeline-agent.md, so the rule goes there instead.

```
CLUSTER: close-out-ran-a-subset-of-the-build-test-suite  (x2, one incident: IMP-1248, IMP-1249)
Altitude:   CLASS, re-clustered. IMP-1249 is filed as untested-hand-handed-script, but its mechanism
            is IMP-1248's: an item closed on one test folder while the build's unit-tests step
            runs every suite, including a Python test asserting the replaced wording.
Ladder row: agent had the information -> agent edit (close-out step 3)
Becomes:    row 4, development-agent.md close-out step 3: for an item that rewrites text in a data
            file, grep src/tests for the replaced text first, and record the build config's
            unit-tests command as a test-run (§C)
Retires:    nothing
Cites:      IMP-1248, IMP-1249
Residual:   The full suite takes about 6 minutes (unit-tests step: 365 s in build 20261023-2). The
            rule asks for it only on data-file text rewrites, not on every item.
```

**Premise re-measured:** the unit-tests step runs `src/tests/Invoke-Tests.ps1` ([build config L967](config/revitalise-grant-automation-build.yml#L967)), and `run-source-gates.py` runs no test suite. The test is already fixed: it now asserts the process owner's warning phrase and no longer the old literal ([test_scrub_flow_definition.py L1117](src/tests/narrative/test_scrub_flow_definition.py#L1117)).

```
CLUSTER: platform-field-length-limit-unenforced  (x1 here: IMP-1243; your clean-up (c))
Altitude:   INSTANCE retirement under an existing CLASS gate. field-length-limits (C-TECH-060)
            already reads rev_description's MaxLength (2000) from Entity.xml; the Pester checks
            restate an old literal (1000).
Ladder row: when retiring an instance gate (skill §2): prove coverage, then retire
Becomes:    routed R1b to development-agent (src/tests is not this agent's to edit)
Retires:    3 instance assertions, routed: DeploymentSettings.Tests.ps1 L363-L374 (two It blocks),
            IntakeContract.Tests.ps1 L940-L947 (one It block, both its literals)
Cites:      IMP-1243
Residual:   The two city-register rows are written by a .ps1 the gate does not scan, so
            CitySettlementRegister.Tests.ps1 L242 (literal 2000, correct today) is their only
            length check. It is kept, and R1b makes it read MaxLength from Entity.xml.
```

**Premises re-measured.** The finding names two assertions. There are three, in two files (`grep -rn 'BeLessOrEqual 1000' src/tests`: DeploymentSettings L366 and L373, IntakeContract L945). The gate covers them: `verify-field-length-limits.py --check-fixtures …` exits 0, with 576 settings-row values checked and the known-bad settings fixture still failing. The longest description in the three files is 984 characters, so removing the checks changes no result today. The lines are at L363-L374, not L331-L341 as briefed, because today's uncommitted test additions moved them.

```
CLUSTER: gate-misparses-prose-as-schema  (x1: IMP-1244)
Altitude:   CLASS, narrowly. The property is "a §3.1 block never names its own table as a column".
            That is a value test (token == the block's table), not a phrase test. The choice-set
            half stays an authoring rule: a Choice column often shares its choice set's name, so
            skipping option-set names would hide a genuinely missing column.
Ladder row: a tool could catch it mechanically
Becomes:    row 1, verify-tad-coverage.py (both copies): own-table skip anywhere in a prose block;
            the absent-column remedy text names the safe authoring form; one VALID fixture (§A)
Retires:    nothing
Cites:      IMP-1244
Residual:   A backticked choice-set name in a prose block still fails, now with a message that
            says how to write it.
```

**Measured:** on a scratch copy of the design document with the paragraph rebuilt as it was (the finding quotes it), today's check gives 2 violations (`rev_setting.rev_setting`, `rev_setting.rev_settingcategory`), and the fix gives 1. The real document gives 206 specs and 0 failures under both, because architect-agent has already reworded the paragraph ([architecture L1231](docs/architecture/revitalise-grant-automation-architecture.md#L1231)). Selftest 38 of 38 on the scratch copy. The new fixture fails under today's parser (`DID NOT BEHAVE … rev_fixturedelta.rev_fixturedelta`).

```
CLUSTER: unverified-guess-about-live-state  (x1: IMP-1245)
Altitude:   NOTE. One instance, the assumption was marked unverified as designed, and the TAD was
            corrected the same morning. The lesson reaches the digest; no change proposed.
Becomes:    CLOSE (V2) with reobserved V3: pipeline-agent's live fetch, 2026-10-23 13:48
Cites:      IMP-1245
Residual:   none
```

```
CLUSTER: ledger-cannot-record-a-design-change-honestly  (x2: IMP-1175 deferred, IMP-1251 new)
Altitude:   NOTE. Second instance, logged by this review from your clean-up (a). The general fix is
            IMP-1175's supersede transition, which is a state-machine design and stays deferred.
Becomes:    routed R2 to commercial-agent: a one-line outcome note in CO-012.md Amendment 1
Retires:    nothing
Cites:      IMP-1251
Residual:   WI-0150 clause 3 keeps its original sentence in the ledger.
```

**Measured:** WI-0150 is `deployed:dev`. `AMENDABLE_STATES` is `new, ready, reopened` ([lib/work_items.py L142](.engine/scripts/lib/work_items.py#L142)), so `link --acceptance` is refused with `[AMEND]`. Clause 3's evidence already traces to `seed-city-settlement-register.ps1` line 238 (`rev_category = $categoryValue`), so the ledger's evidence is true and only its sentence is stale. The clause's `source_ref` is [CO-012.md L18-L23](contract/change-orders/CO-012.md#L16), which still describes the rows as unverified. A note there corrects the text the clause points to.

```
CLUSTER: deferred-entries-whose-condition-was-met  (x6: IMP-1077, IMP-1238; IMP-1095, IMP-1098, IMP-1156, IMP-1159)
Altitude:   NOTE. Closures, not changes
Becomes:    CLOSE on apply: IMP-1077 and IMP-1238 with reobserved V3; the four scrub-flow
            entries with reobserved V4 on the reviewer's statement
Cites:      IMP-1077, IMP-1238, IMP-1095, IMP-1098, IMP-1156, IMP-1159
Residual:   none
```

- **IMP-1077** (V3). Return condition: *"seed-settings distinguishes create-only rows, and a DEV re-run leaves an edited row unchanged"*. You ran `seed-settings.ps1 -Env dev` twice. The second run reported 16 rows "left unchanged (createOnly)", 32 "value upserted" and no FAILED ([routing.log L1789](logs/routing.log#L1789)). You then confirmed that `AmountLimitOther`, edited from 500 to 50, was still 50 ([L1794](logs/routing.log#L1794)).
- **IMP-1238** (V3). Return condition: *"after the engine commit, a deployed:<env> transition of an item linked after the fix succeeds with no relink…"*. The fix is in engine commit `48fd2b0`. WI-0150 to WI-0153 were linked between 07:01 and 09:38 today, and all four `deployed:dev` transitions at 14:10 were accepted with no relink.

- **IMP-1095, IMP-1098, IMP-1156** (blockers, fixed in flight, V4) **and IMP-1159** (rework, V4). Shared return condition: *"the reviewer opens REV | Narrative | Scrub Free-Text in the DEV designer after its next import and it saves"*. Your statement, relayed by lead-agent at 15:28 ([routing.log L1813](logs/routing.log#L1813)): *"Scrub flow check is already done. Can be closed."* Recorded as reviewer-observed, in your words. **You did not say when the check was done relative to today's 14:03 import.** If it was before, it was a save of the flow imported on 2026-10-21. Today's re-read found the imported flow equal to source (13 of 13), so the definition you saved is the one now live. Lead-agent's relay names three entries. IMP-1159 has the same return condition word for word, so it is included. Drop it from the closures if you meant only the three.

**Other reviewer-deferred entries checked against this deploy.** 139 deferred return conditions mention a deploy, an import, DEV, settings or a pipeline step, and I read each against today's log lines. Two are met (above), and the four scrub-flow entries are met by your statement. These are close but not met:
- IMP-1194 needs the flow re-read run on the default folder. Today's stage line records 13/13 matching but not which folder, so it is not confirmed.
- IMP-0879, IMP-0906 and IMP-0971 need pipeline-agent to run the completeness check with `--pending` before its stage line. Today's dispatch did not record that. Run now by this review, it gives 0 findings, but the condition names the dispatch.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | [scripts/verify-tad-coverage.py L258](scripts/verify-tad-coverage.py#L258) + `.engine/scripts/` twin | Own-table skip anywhere in a prose block; remedy text; `VALID-prose-delta-paragraph-naming-its-own-table` fixture (§A) | IMP-1244 | YES — `python3 scripts/verify-tad-coverage.py --selftest`. Scratch: 38/38; today's parser fails the new fixture. Corpus: real TAD 0 → 0; rebuilt paragraph 2 → 1 | already wired (HARD, `tad-coverage`, [build config L445](config/revitalise-grant-automation-build.yml#L445)) |
| 2 | agent | [agents/pipeline-agent.md L287](agents/pipeline-agent.md#L287) | One paragraph: a script the block names has been executed by whoever hands it over or patches it, and has a repository path (§B.1) | IMP-1246, IMP-1247 | N/A — instruction change | N/A |
| 3 | knowledge | [knowledge/technology/dataverse.md L492](knowledge/technology/dataverse.md#L492) | `@odata.nextLink` is absent on the last page; build OData paths in single quotes (§B.2) | IMP-1246, IMP-1247 | N/A — knowledge line | N/A |
| 4 | agent | [agents/development-agent.md L272](agents/development-agent.md#L272) | Close-out step 3: a data-file text rewrite greps `src/tests` and records the build's `unit-tests` command (§C) | IMP-1248, IMP-1249 | N/A — instruction change | N/A |
| 5 | agent | [agents/development-agent.md L343](agents/development-agent.md#L343) | The carry rule covers every new Dev Summary document; heading kept (IMP-1237's needle) (§D.1) | IMP-1250 | N/A — instruction change | N/A |
| 6 | template | [templates/dev-summary-template.md L107](templates/dev-summary-template.md#L107) | §11 comment: carry the last green manifest's `warnings_detail`, naming the step (§D.2) | IMP-1250 | N/A — template comment | N/A |

**Constraint budget:** 0 of 3 used.

**Engine altitude (skill §6).** Rows 2, 4, 5 and 6 land in `.engine` and name no client table, person or environment: the proposed text below was searched for `rev_`, `Revitalise` and `Emily`, with 0 hits. Row 1's script already hard-codes this client's `rev_` prefix throughout. It is an unsplit duplicate pair, and the edit adds no new literal beyond the fixture name `rev_fixturedelta`. Row 3 is instance knowledge.

**Dispositions, decided now from `observable_at`:**

| Entry | `observable_at` | Disposition |
|---|---|---|
| IMP-1244 | V1 | **CLOSE** on apply; `evidence_grep` `scripts/verify-tad-coverage.py` ⊃ `in a later rev-delta paragraph (IMP-1244)` |
| IMP-1246 | V1 | **CLOSE** on apply; `evidence_grep` `agents/pipeline-agent.md` ⊃ `has been executed once by whoever hands it over` |
| IMP-1247 | V1 | **CLOSE** on apply; `evidence_grep` `knowledge/technology/dataverse.md` ⊃ `` `@odata.nextLink` is the same case. `` |
| IMP-1248 | V1 | **CLOSE** on apply; `evidence_grep` `src/tests/narrative/test_scrub_flow_definition.py` ⊃ `The old fixed phrase was a test literal.` (the fix, already on disk, count 1) |
| IMP-1249 | V1 | **CLOSE** on apply; `evidence_grep` `agents/development-agent.md` ⊃ `grep src/tests for the text you replace` |
| IMP-1250 | V2 | **CLOSE** on apply with `reobserved` V2: build-agent, 2026-10-23T13:47, C-TECH-055 re-check of build 20261023-2 against the amended Dev Summary, 0 untriaged ([routing.log L1803](logs/routing.log#L1803)); `evidence_grep` `agents/development-agent.md` ⊃ `under an existing feature slug` |
| IMP-1245 | V2 | **CLOSE** with `reobserved` V3: pipeline-agent, 2026-10-23T13:48, live fetch of DEV `rev_setting`, 50 of 50 rows with a category, including CitySourceFile and CitySourceCapturedOn ([pipeline.log L464](logs/pipeline.log#L464)); `evidence_grep` the TAD ⊃ ``| `A-SETCAT-5` | **CLOSED, DISPROVED 2026-10-23.**`` |
| IMP-1077 | V3 | **CLOSE** with `reobserved` V3: Xander Lykopoulos, 2026-10-23T13:12, `seed-settings.ps1 -Env dev` twice after editing AmountLimitOther; `evidence_grep` `provisioning/dataverse/seed-settings.ps1` ⊃ `CREATE-ONLY ROWS (TAD rev 23, ADR-076 item 6` |
| IMP-1238 | V3 | **CLOSE** with `reobserved` V3: pipeline-agent, 2026-10-23T14:10, `work-items.py transition WI-0150..WI-0153 deployed:dev`, all four accepted with no relink; `evidence_grep` `.engine/scripts/work-items.py` ⊃ `undeclared component label refused at link (IMP-1238)` |
| IMP-1095, IMP-1098, IMP-1156 | V4 (blockers, fixed in flight) | **CLOSE** with `reobserved` V4: Xander Lykopoulos, 2026-10-23T15:28 (time of the statement; the check's own time not stated), rerun *opened REV \| Narrative \| Scrub Free-Text in the DEV designer and saved it*, result his words verbatim. `evidence_grep`: each entry's existing needle, re-measured now in the flow source (counts 14, 1, 1) |
| IMP-1159 | V4 (rework) | **CLOSE**, same `reobserved`; `evidence_grep` `agents/lead-agent.md` ⊃ ``the deploy re-ships the defect (`IMP-1159`)`` (count 1) |
| IMP-1242 | V1 | **DEFER** — routed R1d. `revisit_when`: *`verify-derived-counts.py` reports no drift on `dev-summary-code-app-bundle-kb`* |
| IMP-1243 | V1 | **DEFER** — routed R1b. `revisit_when`: *`grep -rn 'BeLessOrEqual 1000' src/tests` returns nothing and the unit-tests step is green* |
| IMP-1251 | n/a | **DEFER**, joined to IMP-1175. `revisit_when`: *a design for a work-item supersede transition exists* (IMP-1175's, verbatim) |

**Simulated** on a scratch copy of the log: the sixteen dispositions applied, then `verify-improvement-log.py --check --log <copy>` was run. Result: 0 unread and 0 awaiting approval. The only 5 errors are the needles of rows 1 to 6 (IMP-1244, IMP-1246, IMP-1247, IMP-1249, IMP-1250), which cannot exist until the apply. All eight `reobserved` records validated, and the three fixed-in-flight blockers leave the blocker count at 0. The real log was not touched by the simulation (sha1 checked).

### Routed work

These change no file in this review. Each is re-measured before hand-over (step 8).

| # | To | Change | Why not here |
|---|---|---|---|
| R1a | development-agent | [seed-city-settlement-register.ps1 L206](provisioning/dataverse/seed-city-settlement-register.ps1#L206), CitySourceFile description → *"The name of the postcode file the city lookup was loaded from. Used for information only, so you can tell which list the cities come from; no process reads this row. It is set by the deployment and is not meant to be edited. Text; if it is missing, nothing else changes."* Same shape as the CitySourceCapturedOn sentence beside it. No test asserts the old wording (searched). Then you re-run the city script in DEV, which writes descriptions every run | `provisioning/` is delivery work (your clean-up (b)) |
| R1b | development-agent | Delete the two 1000-character `It` blocks in [DeploymentSettings.Tests.ps1 L363-L374](src/tests/provisioning/DeploymentSettings.Tests.ps1#L363) and the map-row length block in [IntakeContract.Tests.ps1 L940-L947](src/tests/solutions/IntakeContract.Tests.ps1#L940), and the D-021 comment above the first ([L319](src/tests/provisioning/DeploymentSettings.Tests.ps1#L319)), citing the `field-length-limits` step as their replacement. In [CitySettlementRegister.Tests.ps1 L242](src/tests/provisioning/CitySettlementRegister.Tests.ps1#L242), read `rev_description`'s MaxLength from `Entities/rev_setting/Entity.xml` in place of the literal 2000. Run `src/tests/Invoke-Tests.ps1` | `src/tests` is delivery work (your clean-up (c), IMP-1243) |
| R1d | development-agent | [revitalise-grant-automation-dev-summary.md L4893](docs/development/revitalise-grant-automation-dev-summary.md#L4893): 1205 kB → 858 kB, as `bundle-budget.json` gives it | A development-agent document (IMP-1242) |
| R2 | commercial-agent | [CO-012.md](contract/change-orders/CO-012.md#L16) Amendment 1: one outcome line — the two rows are CitySourceFile and CitySourceCapturedOn, delivered by `seed-city-settlement-register.ps1` with category 6 (TAD ADR-090 as corrected 2026-10-23), not by the three settings files; the "unverified" text above stays as the record | `contract/` is commercial-agent's; the ledger refuses the clause edit (your clean-up (a), IMP-1251) |

R1a, R1b and R1d fit one development-agent dispatch under `wbs:2.2`. R1d's sentence is about the `wbs:6.3` portal, which is unbilled. No hours figure is stated here.

---

## 4. Retirements

> Retirement check performed: 10 retired and 88 live constraint rows (`grep -rh '^| ~~C-'` and
> `'^| C-'` over `constraints/`). The rows these clusters touch are C-TECH-055 (warnings) and
> C-TECH-060 (field lengths). Neither is made redundant: no script took over C-TECH-055 (C1 measured
> why), and C-TECH-060 is the general gate the routed R1b retires three instance assertions in
> favour of. Those three assertions are tests, not constraint rows. Their retirement is routed,
> and coverage is proven: the gate's known-bad settings fixture still fails. No constraint is retired.

---

## 5. Findings left unprocessed

**Deferred:** IMP-1175, IMP-1006, IMP-1194, IMP-0879, IMP-0906, IMP-0971

| Finding | Class | Why not processed | Revisit when |
|---|---|---|---|
| IMP-1175 | `ledger-cannot-record-a-design-change-honestly` | IMP-1251 joins it; its design is still the fix | its own |
| IMP-1006 | `untriaged-tool-warning` | C1's two measurements belong to its design, which this review does not write | its own |
| IMP-1194 | `gate-scope-mismatch` | Today's stage line does not say which folder the re-read used | its own |
| IMP-0879, IMP-0906, IMP-0971 | `pipeline-dispatch-stops-before-declared-post-deploy` | Today's dispatch did not record a `--pending` run | their own |

The other reviewer-deferred entries are unchanged.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 1246 | 1247 (IMP-1251, appended at draft and digest regenerated then) |
| Distinct lessons | 1222 | 1223 |
| Recurring classes (x≥2) | 97 | 98 (`ledger-cannot-record-a-design-change-honestly` reaches x2) |
| Entries closed | — | 13 on apply; 3 deferred |
| Digest lines | 641 | 642 now; measured again on apply |

Regenerated on apply with `python3 scripts/generate-known-failure-modes.py`, confirmed with `--check`.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-10-23-improvement-review-2.md

Findings processed: 16 NEW  →  8 clusters
Regression check:   5 prior changes audited, 1 classes recurred
Proposed:           0 constraints (cap 3), 1 gates/scripts, 1 skill/knowledge edits,
                    3 agent-file edits, 1 template edits, 0 retirements
Altitude calls:     4 generalised from instance to class, 4 left as notes
Digest:             will regenerate — 1223 lessons, 98 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. On approval

### Applied 2026-10-23 15:31–15:45 (`APPROVE IMPROVEMENTS`, reviewer Xander Lykopoulos, relayed by lead-agent)

**The keyword.** The reviewer wrote "Approve improvements", in lower case. It names the two words of the gate and nothing else, and he wrote it in his own turn. Earlier approvals were accepted in mixed case ("Approve Improvements", 2026-10-05 and 2026-10-22), so it was accepted here. The optional decision on IMP-1175 was not answered, so no design was commissioned.

All six rows were applied as drafted, with nothing withheld. The six target files still had the sha1s measured at draft, so no merge was needed.

| Row | Landed at | Verified by |
|---|---|---|
| 1 | [verify-tad-coverage.py L259](scripts/verify-tad-coverage.py#L259), engine twin byte-identical (`cmp`) | `--selftest` 38 of 38 (21 known-bad, 17 valid). Real check: exit 0, 206 specs |
| 2 | [pipeline-agent.md L296](agents/pipeline-agent.md#L296) | Text as in §B.1; needle count 1 |
| 3 | [dataverse.md L494](knowledge/technology/dataverse.md#L494) | Text as in §B.2; needle count 1 |
| 4 | [development-agent.md L277](agents/development-agent.md#L277) | Text as in §C; needle count 1 |
| 5 | [development-agent.md L350](agents/development-agent.md#L350) | Text as in §D.1. The heading is unchanged, so IMP-1237's needle still matches (count 1) |
| 6 | [dev-summary-template.md L110](templates/dev-summary-template.md#L110) | Text as in §D.2 |

The `first = True` line was also removed, as §A said.

**Dispositions, as drafted.** APPLIED with needles: IMP-1244, 1246, 1247, 1248, 1249 and 1250, with IMP-1250 also carrying V2 `reobserved`. APPLIED with `reobserved` V3: IMP-1245, 1077 and 1238. APPLIED with `reobserved` V4 on the reviewer's statement, whose time is recorded as not stated: IMP-1095, 1098, 1156 and 1159. For the last six, `reviewed_in` now lists the earlier review and this one. Deferred with the approved `revisit_when`, verbatim: IMP-1242, 1243 and 1251. IMP-1250's `applied_by` records that the change was narrowed from the finding's proposal: the template got a comment, not pre-seeded rows, because those warnings and their figures are client-specific and change with each build.

`verify-improvement-log.py --check` after the dispositions: exit 0, with 0 unread, 0 awaiting approval and 0 fixed-in-flight blockers.

**Closing checks.**
- The digest was regenerated: 642 lines, 1247 entries, 1223 lessons, 98 recurring classes. `--check` is current and the selftest passes.
- The `CURRENT SIZE` sentence in both copies of `generate-known-failure-modes.py` was corrected from 640 to 642.
- `verify-derived-counts.py` exits 1 (SOFT) on one claim only: the bundle figure, which is IMP-1242 and routed (R1d).
- `verify-engine-instance-split.py`, `verify-build-config.py` and `verify-class-defences.py` all exit 0.

**Provisional because of the concurrent WI-0154 dispatch.** IMP-1248's needle sits in `src/tests/narrative/test_scrub_flow_definition.py`, which that dispatch may edit. If its wording moves, `verify-improvement-log.py` will name the entry. Nothing this review wrote touches that dispatch's files.

**One whole-file write to the log.** A `sed -i` fixed a placeholder in two `deferred_reason` texts that this review had just written. The entry count was 1247 before and after, and the last line is still IMP-1251, so no concurrent append was lost.

**Routed work, re-measured at apply and handed to lead-agent:**
- **R1a, R1b and R1d** for development-agent, `wbs:2.2`, one dispatch. All are still open: the old CitySourceFile sentence is present, the 3 assertions are present, and the 1205 drift is present.
- **R2** for commercial-agent. `CO-012.md` has no outcome note yet.

**Post-apply bookkeeping.** When R1d landed, it broke the evidence check of IMP-0877, an already-applied finding whose check text was the old 1205 kB sentence. So `verify-improvement-log.py --check` failed. The old wording was edited in place, so I pointed IMP-0877's check at a stable phrase in the same sentence that carries no number: ``derived from `bundle-budget.json`'s `measured_bytes` ``. No keyword was needed, because the substance of IMP-0877 is unchanged. Afterwards the log check exits 0 and `verify-derived-counts.py` reports 0 drifts. This review's premise search missed it: it looked through `src/tests` for the old wording, but not through the log's evidence-check needles. IMP-1252 records that, and it waits for the next batch, because its fix is a skill change and needs the keyword.

**Publishing.** Rows 2, 4, 5 and 6 and the engine copies of rows 1 and 5 change `.engine`. Row 1, the generator's size line, row 3, the log and the digest change the instance repository. Nothing is committed. The engine needs its own commit, then a push to the branch that already contains its parent, then a pointer bump here.

---


Apply order (followed as written): (1) set the status to `APPLYING`. (2) Confirm the targets still have the sha1s measured at draft: `scripts/verify-tad-coverage.py` and its engine twin `f8e5f107928f…`, `agents/pipeline-agent.md` `00e244680d9c…`, `agents/development-agent.md` `ee7836f74e77…`, `templates/dev-summary-template.md` `3d60efddf252…`, `knowledge/technology/dataverse.md` `c46d5cc56c4a…`. Merge if they differ. (3) Apply rows 1 to 6 one at a time, and close each entry as its row lands. (4) Run `verify-tad-coverage.py --selftest` and the real check, `cmp` the two copies, `verify-engine-instance-split.py`, and `verify-build-config.py`. (5) Regenerate the digest, then correct the `CURRENT SIZE` sentence in both copies of `generate-known-failure-modes.py` to the measured line count. (6) Run `verify-improvement-log.py --check`, `verify-derived-counts.py`, `verify-class-defences.py` and `verify-review-document.py`. (7) Re-measure R1a, R1b, R1d and R2 against the tree before handing them to lead-agent.

---

## §A — `scripts/verify-tad-coverage.py`, both copies (proposed)

Measured on a scratch copy with `lib/` beside it: selftest OK, 38 cases (21 known-bad, 17 valid).

```diff
@@ parse_section_31, prose branch
-            first = True
             for number, line in prose:
                 visible = _is_trustee_visible(line)
                 for token in _CODE_SPAN.findall(line):
-                    if first and token == table:
-                        first = False
-                        continue  # the block header names its own table
+                    if token == table:
+                        continue  # a block names its own table, on its header and in a later rev-delta paragraph (IMP-1244)
@@ absent-column violation remedy
             f"{spec.table}/Entity.xml, or declare an owned, dated deferral in "
-            f"{deferrals_path}"))
+            f"{deferrals_path}. If the token names a choice set or a table rather than a column, "
+            f"write it without backticks: every backticked rev_* token in a §3.1 block is read "
+            f"as a column of that block's table (IMP-1244)"))
@@ _fixture_tad signature
-                 negated_on_unread_table: bool = False) -> str:
+                 negated_on_unread_table: bool = False,
+                 prose_block_with_delta: str | None = None) -> str:
@@ _fixture_tad, before section 3.2
+        if prose_block_with_delta is not None:
+            # IMP-1244: a prose block whose later rev-delta paragraph names the block's own table
+            t = prose_block_with_delta
+            out += [f"**`{t}` — Tier 2:** `{t}_c00`, `{t}_c01`.", "",
+                    f"Rev 2 (`ADR-1`): **`{t}`** gains `{t}_c02`.", ""]
@@ selftest, before deferral-with-no-owner
+        case("VALID-prose-delta-paragraph-naming-its-own-table (IMP-1244)",
+             tad=_fixture_tad(prose_block_with_delta="rev_fixturedelta"), read_tables=every,
+             deferral=None, expect_fail=False, extra_table="rev_fixturedelta")
```

The `first = True` line is removed because nothing reads it after the change. The scratch run kept it, and that has no effect on the result.

## §B — reviewer-run scripts (proposed text)

**B.1, `agents/pipeline-agent.md`, a new paragraph after L294** (after *"…First Import Into a New Environment*."*):

> **A script the block names has been executed once by whoever hands it over — and again by whoever patches it.** A parse check passes what StrictMode throws on at run time: an absent optional response property, or a `$select` interpolated inside a double-quoted path. Run it against the provisioning test harness's fakes, or read-only against the environment if you hold a credential, and name it by a repository path the reviewer can open, never a scratch path (`IMP-1246`, `IMP-1247`).

**B.2, `knowledge/technology/dataverse.md`, a new paragraph after L492** (end of *"Guard every optional-column read…"*):

> **`@odata.nextLink` is the same case.** It is absent on the last page of a result, so `$r.'@odata.nextLink'` throws there under StrictMode; read it through `$r.PSObject.Properties['@odata.nextLink']`. And build an OData path in a single-quoted string: in a double-quoted one, a backtick placed anywhere but directly before `$` leaves `$select` to be read as an unset variable, which StrictMode also throws on (`IMP-1246`, `IMP-1247`).

## §C — `agents/development-agent.md`, close-out step 3 (proposed text)

Append to step 3 (after *"…record the green one."*, L275):

> **Where the item rewrites text in a data file — a settings file, a seed list, a fixture — grep src/tests for the text you replace before you replace it, and record the build config's `unit-tests` command as one of the test-runs.** A test in another language may assert that wording, and `run-source-gates.py` runs no test suite (`IMP-1248`, `IMP-1249`).

## §D — standing warnings (proposed text)

**D.1, `agents/development-agent.md` L345–L348.** The heading stays as it is, because IMP-1237's needle is the heading. Replace the paragraph with:

> At handoff, read the last SUCCESS manifest of the same build config — for a new feature, and equally for a new Dev Summary written under an existing feature slug. For each `warnings_detail` entry whose `triaged_in` names another document, add a citing row to this document's tool-warnings table (`C-TECH-055`), naming the step in the Source step column. Steps that need a network, a credential or a full build — `lint`, the pack steps, the code-app build — are the ones a source-gates-only run never sees, so their warnings exist only there (`IMP-1237`, `IMP-1250`).

**D.2, `templates/dev-summary-template.md` L108–L109.** Extend the comment:

```diff
 <!-- Every warning from build, pack, or deploy: resolved, or accepted with a stated reason.
-     None may be carried silently. "No warnings emitted" is a valid entry. -->
+     None may be carried silently. "No warnings emitted" is a valid entry.
+     Before handoff, add a citing row for every `warnings_detail` entry of the last SUCCESS
+     manifest of the same build config, including steps you did not run (pack, lint, the
+     code-app build). Name the step in the Source step column. -->
```
