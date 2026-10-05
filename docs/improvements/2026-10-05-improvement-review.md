# Improvement Review — 2026-10-05

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 6 `NEW` → 4 clusters (the 3 unread entries in the queue, plus 3 logged by this review while checking them)
**Trigger:** reviewer request (relayed by lead-agent, 2026-10-05; the dispatch named this file)
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** **APPLIED 2026-10-05** on `APPROVE IMPROVEMENTS` (Xander Lykopoulos, relayed by lead-agent 10:41), revalidated set: rows 1, 2, 3, 5, 6 landed; row 4 dropped as a duplicate (no edit); decisions D-1, D-2, D-3 answered *agreed with suggested*. See *Applied record* at the end. Previously: DRAFT, parked at the gate; revalidated 2026-10-05 against DEV.
**WBS:** system work, `wbs:system`, not billable. The findings come from the intake fix (`wbs:4.2,4.3`), the income-band option set (`wbs:6.8`) and the Create Envelope rework (`wbs:3.2,3.5`).

**Why this is a new review and not a fifth amendment to the open batch review.** The batch review [2026-09-30-improvement-review-2.md](docs/improvements/2026-09-30-improvement-review-2.md#L1) is still parked with 69 entries and six decisions. This dispatch was a reviewer request, not a post-deploy batch, and it named this file. Nothing here overlaps that review's change rows, so the two can be approved separately. The one shared class is noted in cluster C4.

---

## Revalidation — 2026-10-05 10:00–10:20 (read this first)

Nothing in the tree changed after this draft was written (09:44; no file is newer except `logs/routing.log`). What the revalidation adds is **live DEV evidence**, read-only: a solution export, FetchXML reads and `verify-live-flow-definitions.py --env dev`.

| Item | Verdict | Evidence |
|---|---|---|
| Rows 1, 2 | **VALID** | the provisioning name search is still at [L35](scripts/verify-plain-column-not-claimed-calculated.py#L35); no Rule C; `--selftest` 5 of 5 |
| Row 3 | **VALID** | the entry is still tagged `platform-contract` |
| Row 4 | **VALID, overlaps** | the same edit as [review 2026-09-30-2 row 10](docs/improvements/2026-09-30-improvement-review-2.md#L1140); apply once. Count is 70 |
| Row 5 | **VALID** | the digest is now 616 lines (this revalidation regenerated it after logging three findings) |
| Row 6 | **VALID** | `domain-invariants` still reports 8 violations; DEV holds all 8 referee columns as secured, each with two field-permission rows |
| R1, R3, R4, R5, R7 | **VALID** | `run-source-gates.py` still 3 of 18 red, the same three; the conversion warning and header unchanged; the same 8 count drifts; no finding logged since 09:39 |
| R2 / D-2 | **VALID, confirmed live** | `verify-live-flow-definitions.py` reports Create Envelope live equal to source, so DEV runs the unsecured version: **0 of its 18 DocuSign actions carry `secureData`**. It has run 19 times since 3 October |
| R6 | **CHANGED** | The defect is gone live: `rev_incomeband` holds only 1–4 in DEV (solution export and `stringmap`, 10:05–10:17). No log line records who removed 5 and 6 (logged as IMP-1040). R6 is now only the verifier's first live run, which `C-TECH-064` still needs |
| D-1 | **VALID** | unanswered |
| D-3 | **CHANGED — wider** | In DEV, 9 of 21 applicants have no full name and 10 of 22 applications no total cost, all of them created by the intake. **And the live intake flow does not write the total cost**: the re-read reports `item/rev_costs` missing live, and no live flow contains it. The 3 October hotfix excluded it on purpose ([pipeline L305](logs/pipeline.log#L305)), so new rows lack it too until the intake flow is deployed from source (IMP-1041). The full-name write is live |

**Dispositions that change (§5):**

| Entry | Was | Now |
|---|---|---|
| Income-band orphans | DEFER until R6 | **CLOSE permitted**: the original observation (live members against source) was re-run at V3 and shows none. Record that as `reobserved` at apply, re-running it first. R6 stays as routed work for the gate |
| Total-cost column not written | DEFER | **DEFER**; its `revisit_when` must now start with *the intake flow is deployed from source and the live re-read reports no difference* |
| Full-name column not written | DEFER | **DEFER**, unchanged. The write is live, but no intake row has arrived since 2 October |

---

## Summary

The queue held only **3 unread findings**. The other 304 open entries were looked at already: 69 wait on the parked reviews, and 235 are deferrals you accepted. Two of the three are the same mistake made twice on 3 October. A column (the applicant's full name, then the application's total cost) shipped as an ordinary column while everything around it assumed Dataverse would calculate it, so nothing filled it in. The third: an income-band option set kept two old values live for 16 days, because the check that reads the live environment only proved the set existed.

**Checking those three turned up a larger problem.** Between 3 October 18:51 and 4 October 07:25, eighteen hotfix imports went into DEV with every gate skipped. None of them produced a finding. **The current source now fails 3 of the 18 source gates**, so the next normal build will stop. Most important: the DocuSign envelope flow has lost its secure-data setting on the actions that carry applicant and referee names. Those lines call the removal a *temporary diagnostic*, and no later line puts it back.

**Applied 2026-10-05** — see the record at the end. *(Draft text:)* **Waiting on you:** `APPROVE IMPROVEMENTS` for six small changes (three edits to scripts, two bookkeeping edits, one register entry), plus three decisions below. No new constraints.

---

## 1. Regression check — did the last review's changes work?

The last reviews applied were [2026-10-02](docs/improvements/2026-10-02-improvement-review.md#L9) (verdicts on the work board) and [2026-09-29](docs/improvements/2026-09-29-improvement-review.md#L7) (three knowledge edits). Two older rules are audited too, because this batch's findings name them.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Verdicts given on the work board (W8) | 2026-10-02 | `evidence-recorded-but-not-surfaced` | NO | **Not yet used.** No verdicts file has gone through the ledger yet, so "working" is not established |
| *A live read is a snapshot* ([build-and-deploy.md](knowledge/technology/build-and-deploy.md#L205)) | 2026-09-30 | `async-flow-postimport-plugin-fails-silently` | YES, and caught. An open designer tab overwrote a hotfix import one minute later ([pipeline.log L300](logs/pipeline.log#L300)); the re-read this change teaches found it | **Working** |
| Import wait of at least 600 s | 2026-09-30 | `client-timeout-misread-as-write-failure` | NO. 18 imports since, none misread | **Working** |
| UTC and the clock ([testing-tools.md](knowledge/technology/testing-tools.md#L163)) | 2026-09-30 | `log-timestamp-not-taken-from-the-clock` | **YES.** [routing.log L1285–L1286](logs/routing.log#L1285) are dated 3 October 22:18 and 22:43 for events of 2 October; they sit before a line dated 3 October 08:35 | **Wrong altitude — prose recurred.** The parked [2026-09-30-2 review](docs/improvements/2026-09-30-improvement-review-2.md#L81) already proposes that the tools stamp the time. Approving it is the remedy, so this instance is reported here and not logged again |
| [C-TECH-064](constraints/technology/technology-constraints.md#L134) — live option-set members compared with source | 2026-08-19 | `exit-zero-does-not-mean-created` | **YES** (cluster C3) | **A rule that could not fire.** The HARD rule requires a live member comparison. The only live check counted existence, and its pipeline step still reads [NOT YET PERFORMED](config/revitalise-grant-automation-pipeline.yml#L1723). The comparison now exists in source (V1). It still has to run live |
| [C-TECH-060](constraints/technology/technology-constraints.md#L130) field-length gate | 2026-08-18 | `platform-field-length-limit-unenforced` | YES, live: action descriptions over 256 characters stopped the envelope flow being switched on ([pipeline.log L305](logs/pipeline.log#L305)) | **Gate correct, path skipped.** It passes the committed tree and counts action descriptions (674 today); the hotfixes never ran the build (cluster C4) |

**Changes whose class recurred after a *prose* fix:** the clock paragraph. It is escalated by the parked review; nothing more here.
**Changes whose class recurred after a *gate*:** C-TECH-064. Its member comparison did not exist, so it could not fire. That is recorded on the cluster C3 entry rather than as a separate `gate-cannot-fail` finding, because that entry's in-flight fix is the remedy.

---

## 2. Clusters and promotion decisions

```
CLUSTER C1: document-contradicted-by-shipped-artefact  (x3: IMP-1033, IMP-1035, IMP-1037)
Altitude:   CLASS — three instances of one property: a column shipped plain while its writers and
            readers kept assuming it was calculated. Two reached DEV data (V5), one is a latent
            instruction in provisioning/ (V1)
Ladder row: "third instance -> constraint row" OVERRIDDEN by "prefer the most mechanical home": the
            gate already exists and is wired HARD, so a constraint row would restate it as prose
Becomes:    rows 1 and 2 (the gate's Rule B narrowed; a Rule C added) + routed item R4
Retires:    nothing
Cites:      IMP-1033, IMP-1035, IMP-1037
Residual:   the gate reads a declaration, a Description and the presence of a write. It never
            checks that the written value is right, and a column with no marker and no
            Description claim is not examined at all
```

The gate [verify-plain-column-not-claimed-calculated.py](scripts/verify-plain-column-not-claimed-calculated.py#L31) was written during the fix and is wired HARD at [build.yml L531](config/revitalise-grant-automation-build.yml#L531). No build has run it yet: the last `build.log` line is build 20261003-2, which came before it. **Executed here:** `--selftest` gives 5 of 5 fixtures. The working tree gives 0 findings over 273 plain columns, and 0 is right because both columns are now written. **The committed tree** (`git archive HEAD`, before the fixes) gives 3 findings, all true. All three come from Rule A, the Description claim, and that is where the next cluster starts.

Two proposals in the findings are **not adopted**. One would check columns the flow notes call "set by the flow"; the other is the second rule IMP-1035 asks about. Both would read prose in `notes.md`, and this project has measured prose-reading gates five times at 48–100% false. The value-based form already exists: the `NOT CALCULATED YET` marker on the column itself, which Rule B reads.

```
CLUSTER C2: gate-cannot-fail  (x1 new member of a 54-member class: IMP-1036)
Altitude:   INSTANCE fix to a gate written two days ago — not a new gate
Ladder row: "a tool could catch it mechanically" (the tool exists; its writer test is wrong)
Becomes:    row 1
Retires:    nothing
Cites:      IMP-1036
Residual:   a flow writing the column inside an expression that is not a payload key would read
            as "not written" (a false FAIL, the safe direction)
```

Rule B is meant to fail when a column marked `NOT CALCULATED YET` has no writer. It [counts any mention of the column name under provisioning/](scripts/verify-plain-column-not-claimed-calculated.py#L35) as a writer. Both real columns are named in [ensure-schema.ps1's header](provisioning/dataverse/ensure-schema.ps1#L192) and in [a formula map](provisioning/dataverse/ensure-schema-helpers.psm1#L569) that creates schema, not data. **So Rule B could not fail on either case it was written for.** Measured on a candidate that counts only flow write payloads: the committed tree gives **5 findings, all 5 true**; the working tree gives 0, which is correct; the selftest stays green.

```
CLUSTER C3: exit-zero-does-not-mean-created  (x1 here; IMP-1034, the second trim of an option set after IMP-0019)
Altitude:   CLASS — already promoted (C-TECH-064). The defect was that the rule's live step did not
            compare members
Ladder row: "a tool could catch it mechanically" — built in flight
Becomes:    row 3 (re-tag the entry into its real class) + routed item R6 (the first live run)
Retires:    nothing
Cites:      IMP-1034
Residual:   until someone with the provisioning credential runs the verifier, nothing checks this
            live, exactly as for the last 47 days
```

The fix is [Test-OptionSetMembers](provisioning/dataverse/verify-solution-components.ps1#L193). It compares both directions (extra values, missing values, English labels) and runs inside the existing DEV verification step. **Executed here:** its Pester file passes 4 of 4. That is V1: it has never run against DEV. The entry was tagged `platform-contract`, a class of one. Its real class is the one its own first instance carries, so row 3 moves it there and the digest counts the recurrence. **Not adopted:** the suggestion that every option-set trim also be listed in the Dev Summary. A written list would duplicate a check that now exists in code.

```
CLUSTER C4: solution-source-edited-outside-dispatch  (x2: IMP-0981, parked in review 2026-09-30-2; IMP-1038)
Altitude:   CLASS, second instance — so an instance patch is forbidden, and none is proposed. The
            general home is an existing draft design, not a new rule in this review
Ladder row: "second instance -> generalise" — deferred to decision D-1, because the bypass was a
            reviewer's explicit choice and only the reviewer can say what must accompany it
Becomes:    routed items R1-R3, R5, R7 + row 6 (the register entry the next build needs) + decision D-1
Retires:    nothing
Cites:      IMP-1038
Residual:   until D-1 is decided, a hotfix session is bound only by the general logging rule, which
            this session did not follow
```

The parked review declined a check for the first instance because *"the source gates did catch the edit at the next run"*. That is still true: [run-source-gates.py](scripts/run-source-gates.py#L1) now reports **3 of 18 red** on the working tree. **But here DEV received 18 imports before any next run.** Measured today:

- **flow-definition-language** fails on [Find_the_failed_action](src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L2085). The failure lookup does not look inside three new containers, so an alert would name the wrong step. The committed tree passes.
- **domain-invariants** fails on 8 referee columns the hotfixes added as secured and never entered in the [special-category register](constraints/domain/special-category-register.yml#L335). On the committed tree it reports none of these.
- **shipped-content** fails because the escalation alert card on file no longer matches the one the flow sends. Not compared against the committed tree.
- **Secure data:** 22 of 24 connector actions in the envelope flow have no `secureData`, including every action that reads or fills the signer tabs. The [20:40 line](logs/pipeline.log#L306) calls the removal a *temporary diagnostic*. The only risk acceptance for this flow ([EX-004](contract/known-exceptions.json#L29)) covers two other actions and expires on 16 October. No gate flags this: flow-definition-language checks secure outputs on Dataverse reads, not on DocuSign actions.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | [scripts/verify-plain-column-not-claimed-calculated.py](scripts/verify-plain-column-not-claimed-calculated.py#L31) | Rule B counts only flow write payloads (`item/<col>`, `body/<col>` in `Workflows/*.json`); remove the provisioning name search and the unused `pat`; add fixture `mentioned-only-in-provisioning-must-fail`; docstring states why provisioning is not a writer | IMP-1036, IMP-1035 | YES — `--selftest` (6 fixtures); committed tree must give 5 findings, working tree 0 | already wired — `HARD` at [build.yml L531](config/revitalise-grant-automation-build.yml#L531) |
| 2 | script | same file | Rule C: a column that declares `SourceType`/`FormulaDefinition` (calculated) must not be written by any flow payload. This is the coupling the [column's own comment](src/solutions/RevitaliseGrantAutomation/Entities/rev_applicant/Entity.xml#L119) says "MUST" be honoured if the planned conversion happens; add fixture `calculated-and-written-must-fail` | IMP-1033, IMP-1037 | YES — `--selftest` (7 fixtures); corpus: 0 findings, correct because no column in source is calculated today | already wired — `HARD` at [build.yml L531](config/revitalise-grant-automation-build.yml#L531) |
| 3 | other | [logs/improvement-log.jsonl L1030](logs/improvement-log.jsonl#L1030) | `class_instance_of` of the option-set entry: `platform-contract` → `exit-zero-does-not-mean-created` | IMP-1034 | YES — `python3 scripts/verify-improvement-log.py --check` | N/A |
| 4 | agent | [agents/improvement-agent.md L568](agents/improvement-agent.md#L568) | The registered `verify-*.py` count: re-derive with `ls scripts/verify-*.py \| wc -l` at apply (70 today, 67 written) | IMP-1036 | YES — `python3 scripts/verify-derived-counts.py` | N/A |
| 5 | script | [scripts/generate-known-failure-modes.py L46](scripts/generate-known-failure-modes.py#L46) **and** its byte-identical `.engine/scripts/` copy | `CURRENT SIZE` line: re-derive the digest line count after the final regeneration (615 today, 612 written) | IMP-1036 | YES — `python3 scripts/verify-derived-counts.py` | already wired (`derived-counts`, SOFT) |
| 6 | other | [constraints/domain/special-category-register.yml L335](constraints/domain/special-category-register.yml#L335) `pending_adjudication`, `rev_application` group | Add the 8 new secured referee columns beside the 3 referee columns already listed there. Basis: your 30 September ruling that referee columns are personal data | IMP-1038 | YES — `python3 scripts/verify-domain-invariants.py src/solutions/RevitaliseGrantAutomation` exits 0 | already wired (`domain-invariants`, HARD) |

**Constraint budget:** 0 of 3 used.

**Engine or client:** rows 1–2 stay in this repository's `scripts/` (no engine copy exists; the `NOT CALCULATED YET` marker is this project's convention). Row 4 is engine text, a number only, with no client literal. Row 5 touches both copies, because they are byte-identical duplicates.

### Routed work — none of this is improvement-agent's to change

| # | To | What | Settles it |
|---|---|---|---|
| R1 | development-agent (`wbs:3.2`) | Make the envelope flow's failure lookup descend into the three new containers | `python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation` exits 0 |
| R2 | development-agent (`wbs:3.2`) | **Decided (D-2, agreed):** restore `secureData` on `Read_the_tabs` and every `Fill_*_tabs` action in the envelope flow as part of the `wbs:3.2` rework, then deploy through a gated build. Re-measured at apply: 2 of 24 connector actions carry it; DEV runs the same unsecured version | every DocuSign action carrying applicant or referee details shows `secureData`; `verify-live-flow-definitions.py --env dev` reports the flow equal to source after the deploy |
| R3 | development-agent | Bring the escalation alert card on file back in line with the flow | `scripts/verify-shipped-content.py` exits 0 |
| R4 | development-agent (`wbs:4.2,4.3`) | Correct [the conversion warning](provisioning/dataverse/ensure-schema-helpers.psm1#L579) and the ensure-schema header: both must say the intake flow's two writes come out before any conversion to calculated | grep of both files |
| R5 | development-agent / architect-agent | Four registered counts drifted in their files: settings rows 22→36, secured columns 78→88 (twice), Trustee role header 62→72, supplied-asset files 131→285 | `python3 scripts/verify-derived-counts.py` |
| R6 | reviewer (holds the provisioning credential) | **Narrowed by the revalidation:** the defect itself is gone live (re-observed at apply, 1–4 only). What remains is the verifier's **first live run**: `pwsh provisioning/dataverse/verify-solution-components.ps1 -Env dev`, keeping the option-set lines | the first live execution of `Test-OptionSetMembers`, which C-TECH-064's option-set clause needs and has never had |
| R7 | lead-agent, to the session that ran the hotfixes | Log the hotfixes' lessons while that context exists: DocuSign tab-type spellings, `routingOrder` locked by the template, Company tab stored but shown empty, designer tab overwriting an import, the field-security import failure | `verify-improvement-log.py` shows the new entries |

---

## 4. Retirements

> Retirement check performed: 87 live constraint rows, 10 retired (derived with the grep in `agents/improvement-agent.md`). None is currently redundant. The one rule this batch touches, C-TECH-064, is the rule whose missing member comparison caused cluster C3, so it is needed more than before, not less.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0019, IMP-0934, IMP-0981

None of the three is processed here. IMP-0019 is closed and is cited only as the first instance of cluster C3's class. IMP-0981 is processed by the parked [2026-09-30-2 review](docs/improvements/2026-09-30-improvement-review-2.md#L779). IMP-0934, the one open governance-lane critical finding, is parked in [review 2026-09-27](docs/improvements/2026-09-27-improvement-review.md#L7). It needs the keyword sent against that document, not a new review.

**Excluded from scope, not re-derived:** 69 entries waiting on parked reviews (67 in 2026-09-30-2, 1 in 2026-09-23-7, and the 2026-09-27 critical one above) and 235 reviewer-accepted deferrals.

**Dispositions this review will write on approval** (decided now from each entry's `observable_at`):

| Entry | Level | Disposition | Why |
|---|---|---|---|
| Full-name column not written | V5 | **DEFER** | fix is in source; closing needs a real intake row read back in DEV, which no session here can produce |
| Total-cost column not written | V5 | **DEFER** | same |
| Income-band orphans | V3 | **DEFER** | member check is V1; closing needs R6 |
| Rule B could not fail | V1 | **CLOSE** → `APPLIED` with row 1 | `evidence_grep` on the new fixture name |
| Provisioning conversion instruction | V1 | **DEFER** | routed (R4); not fixed yet |
| Hotfix session | V1 | **DEFER** | routed (R1–R3, R7) and decision D-1 |

**Simulated before parking:** on a scratch copy of the log with the five deferrals and the re-tag applied, `verify-improvement-log.py --check` exits 0 with 0 unread, 0 deploy-lane critical findings, and the warning *"fixed by IMP-1035, and no review has processed it"* cleared. The real log was confirmed byte-identical afterwards. In the draft state that warning is still shown; it clears on approval.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 1031 | 1034 |
| Distinct lessons | 1015 | 1018 |
| Recurring classes (x≥2) | 79 | 80 |
| Digest lines | 614 | 615 |

Regenerated once already, at draft time, because this review appended three entries (capture contract). It is regenerated again after apply. `--check` reports it current.

---

## What you need to decide

**D-1. Should a reviewer-directed hotfix carry two obligations, written into the existing runtime-incident design rather than a new rule?**

**Problem** — eighteen hotfix imports reached DEV with every gate skipped and no lesson logged, and nothing in the rules names this route.
**Suggested fix** — extend the [runtime-incident design's decisions](docs/improvements/2026-09-29-capability-design-runtime-incident-autofix.md#L393) so a hotfix (a) runs `run-source-gates.py` first and records which gates were red in its pipeline line, and (b) logs each surprise before the session ends. The override stays yours.
**What happens if you don't** — the next hotfix session skips the same gates again (one of them would have caught the description-length stop). Its lessons are lost when its context closes, as these were.
[pipeline.log L299](logs/pipeline.log#L299)

---

**D-2. Restore secure data on the envelope flow's signer-tab actions now?**

**Problem** — the actions that read and fill applicant and referee details were unsecured as a temporary diagnostic, and no later line restores them.
**Suggested fix** — restore them as part of the `wbs:3.2` rework (R2), now that the diagnostic has served its purpose.
**What happens if you don't** — each envelope run writes names and addresses into DEV run history, outside column security, and no risk acceptance covers it. Your 30 September ruling treats referee details as personal data.
[pipeline.log L306](logs/pipeline.log#L306)

---

**D-3. Fill in the full name and total cost on DEV intake rows created before the fix?**

**Problem** — every intake row since 14 August has both columns empty, and round statistics leave out every row with no total cost.
**Suggested fix** — a one-off script you run, routed to development-agent, that writes both values from the source columns.
**What happens if you don't** — only new submissions get the values. Round statistics in DEV stay incomplete until old rows age out.
[IMP-1035 in the log](logs/improvement-log.jsonl#L1031)

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-10-05-improvement-review.md

Findings processed: 6 NEW  →  4 clusters
Regression check:   6 prior changes audited, 4 classes recurred
Proposed:           0 constraints (cap 3), 3 gates/scripts, 0 skill/knowledge edits,
                    1 agent-file edits, 0 retirements
Altitude calls:     2 generalised from instance to class, 2 left as notes
Digest:             will regenerate — 1018 lessons, 80 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

Rows 3 and 6 are type `other` and are not counted in the `Proposed:` line.

**Verified here:** the gate's selftest (5/5) and three corpus runs (committed tree 3, working tree 0, Rule B candidate 5 and 0); the option-set Pester file (4/4); `run-source-gates.py` (15 of 18 green); flow-definition-language on the committed tree (clean) and domain-invariants on it (no referee-column errors; its one error was an artefact of the scratch copy, which lacked the build config); `verify-improvement-log.py --check` (exit 0) on the real log and on the simulated one; digest `--check` current. **Not verified:** anything live in DEV, because no session here holds the provisioning credential. shipped-content was not compared against the committed tree.

---

## Applied record — 2026-10-05

**Authority.** `APPROVE IMPROVEMENTS` plus decisions D-1, D-2, D-3, from Xander Lykopoulos verbatim: *"Agreed with all suggested improvements for the questions 1 - 6 and D1 - 3 / Approve Improvements for all reviews, process them one by one."* Relayed by lead-agent, [routing.log](logs/routing.log) 2026-10-05 10:41. This was dispatch 4 of 4; the three reviews before it were applied first.

**Re-verified before applying** (step 8). `verify-improvement-log.py --check`: no `corrects` against any entry here. IMP-1039..1042 were logged after the draft and are not in any approved row, so they were not folded; IMP-1040 and IMP-1041 now carry this review in `excluded_by`, and stay unread for the next batch.

| Row | Result | Measured |
|---|---|---|
| 1 | **LANDED** — Rule B counts only flow write payloads; the provisioning search and unused `pat` are gone; fixture `mentioned-only-in-provisioning-must-fail`; the docstring says why provisioning is not a writer | `--selftest` 7 of 7. Committed tree (`git archive HEAD`): **5 findings, 5 true** (3 Rule A, 2 Rule B on `rev_fullname` and `rev_costs`). Working tree: 0 findings over 273 plain columns, correct because both columns are now written |
| 2 | **LANDED** — Rule C: a calculated column written by a flow payload fails; fixture `calculated-and-written-must-fail` | corpus 0 findings over 0 calculated columns. 0 is correct: no column in source is calculated today. The fixture proves it can fail |
| 3 | **LANDED** — the option-set entry is re-tagged `exit-zero-does-not-mean-created` | log check exit 0 |
| 4 | **DROPPED** — duplicate of [review 2026-09-30-2 row 10](docs/improvements/2026-09-30-improvement-review-2.md#L1140), already applied | re-derived `ls scripts/verify-*.py \| wc -l` = **71**; the agent file already says 71. No edit |
| 5 | **LANDED, no edit needed** — the `CURRENT SIZE` line already reads 617 in both byte-identical copies | digest regenerated last: **617 lines**; `verify-derived-counts.py` reports no drift on the digest or the gate count |
| 6 | **LANDED** — the 8 referee columns are added to `pending_adjudication`, `rev_application` group, with a dated comment citing your 30 September ruling | `verify-domain-invariants.py` exit 0 (was 8 violations) |

**Decisions.**

- **D-1 — agreed with suggested.** Recorded in the runtime-incident design, §7 *Settled by the reviewer, 2026-10-05*: a hotfix runs `run-source-gates.py` first and records which gates were red in its pipeline line, and logs each surprise before the session ends. The override stays yours. It is a recorded decision inside a draft design, so nothing enforces it yet.
- **D-2 — agreed with suggested.** Restore secure data on the envelope flow's tab actions in the `wbs:3.2` rework. Routed to development-agent (R2, rewritten above). Not edited here: it is solution source.
- **D-3 — agreed with suggested, as widened.** A one-off backfill script for the full name and total cost, routed to development-agent. Because the live intake flow does not write the total cost, new rows are affected too. So pipeline-agent must first deploy the intake flow from source through a gated build, and the backfill runs after that.

**Dispositions written.**

| Entry | Disposition |
|---|---|
| Rule B could not fail | **CLOSED** (`APPLIED`, needle on the new fixture name) |
| Income-band orphans | **CLOSED** (`APPLIED`), re-observed at V3 at 09:33 UTC: `pac env fetch` of the live string map shows values 1–4 only, equal to source in both directions. R6 stays open for the verifier's first live run |
| Full-name column not written | **DEFER** (V5): the fix is live, but no intake row has arrived since it shipped |
| Total-cost column not written | **DEFER** (V5). The return condition now starts with *the intake flow is deployed from source and the live re-read reports no difference* |
| Provisioning conversion instruction | **DEFER**, routed R4. Re-measured: both texts still wrong |
| Hotfix session | **DEFER**, routed R1–R3 and R7, with D-1 recorded |

**Routed work, re-measured at apply.** R1 is still valid (flow-definition-language red on `Find_the_failed_action`). R2 is still valid (2 of 24 actions secured). R3 is still valid (shipped-content red). R4 is still valid. R5 is still valid: the same 6 drifted lines across 4 claims. R6 is narrowed as above. R7 is still valid: no hotfix lesson has been logged. Source gates are now **2 of 19 red**, down from 3 of 18: row 6 cleared domain-invariants, and attribute-type-stability was added by dispatch 2.

