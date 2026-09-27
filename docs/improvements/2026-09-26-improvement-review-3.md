# Improvement Review — 2026-09-26 (3): WS-X, every declared post-deploy operation actually ran

**Agent:** improvement-agent (tier `strategic`)
**Mode:** capability mode. Authorising artefact: [capability design WS-X](2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L372). The reviewer's settled decisions S-1 to S-5 in that document are not re-asked.
**Scope:** WS-X only, the first slice of Group 3, released early because it does not depend on Group 1.
**Findings processed:** 3 `NEW` → 2 clusters (the finding WS-X adopts, plus two logged by this review from what the measurement showed)
**Trigger:** reviewer request (capability), relayed by lead-agent
**WBS:** `wbs:n/a` — system work on the rules, non-billable, no contracted task ([`C-COM-002`](../../constraints/commercial/commercial-constraints.md))
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** ~~DRAFT — parked at the gate, nothing applied~~ ~~PARTIALLY APPLIED 2026-09-26~~ **APPLIED 2026-09-26, in the working tree, not yet committed.** `APPROVE IMPROVEMENTS` was given by Xander Lykopoulos and relayed by lead-agent. All three changes and all three entries have landed. Committing is deferred to the single final commit the reviewer asked for. See §8.

---

## Summary

The deploy log shows five past DEV deploys that wrote `SUCCESS` without pushing the trustee Code App, although the pipeline config declares that push as a post-deploy step. A new check, run by pipeline-agent just before it writes the stage line, catches all five. It flags nothing that is not a real case: 5 findings across 49 success lines, 5 correct.

Two things came out of the measurement that the design did not expect. **First**, one of the three deploys the design names cannot be flagged: its import failed, so no post-deploy step was owed. **Second**, the prose rule added yesterday for this same problem made the push visible but did not make it run. The very next deploy named the push as refused by the harness and still wrote `SUCCESS`. That is why this is now a gate, not more prose.

**What is waiting on you:** one decision (accept the restated acceptance test), then `APPROVE IMPROVEMENTS`.

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [Review 2026-09-25 (1)](2026-09-25-improvement-review.md#L282), change 1: pipeline-agent step 4 binds every declared post-deploy step; the stage line names each one | 2026-09-25 13:44 | `pipeline-dispatch-stops-before-declared-post-deploy` | **YES, in a weaker form.** [pipeline.log L219](../../logs/pipeline.log#L219) (15:05) named the push as the rule asks, recorded it as refused by the harness at [L218](../../logs/pipeline.log#L218), and wrote `SUCCESS (V3)`. [L227](../../logs/pipeline.log#L227) (20:06) ran the push | **Right idea, wrong altitude.** Naming went from 0 of 3 deploys to 2 of 2. But the status word is still unchecked, so escalate to a gate: this review |
| [Review 2026-09-25 (2)](2026-09-25-improvement-review-2.md#L103), change 1: a correction triggers a sweep of the changed segment (skill paragraph) | 2026-09-25 | `test-asserts-the-defect` | NO. No entry of that class since 2026-09-25 14:40 | Too early to call working, since the window is one day. Leave it alone |
| Review 2026-09-25 (2), change 2: a finding's class re-tagged | 2026-09-25 | data only | n/a | Nothing to audit |

**Changes whose class recurred after a *prose* fix:** review 2026-09-25 (1) change 1. It is escalated to a mechanical gate below, which is the escalation that review named as its own next step if the class came back.
**Changes whose class recurred after a *gate*:** none.

---

## 2. Clusters and promotion decisions

### Cluster A — a deploy stage says SUCCESS while a declared post-deploy step did not run

```
CLUSTER: pipeline-dispatch-stops-before-declared-post-deploy  (x2: IMP-0879, IMP-0906; 5 deploys in the log)
Altitude:   CLASS, ENGINE — the property is "a stage may not claim SUCCESS while a post_deploy
            operation its own config declares has no SUCCEEDED write marker in the same
            dispatch". It holds for any client. The one stack literal (code-app-push → `pac code
            push`) is Power Platform-level, not client-level. A grep of the draft for this
            client's literals (Revitalise, rev_, REV-) returns 0.
Ladder row: "second instance → generalise" + "a tool could catch it mechanically"; the class
            recurred after a prose fix, which the regression table says escalates to a gate
Becomes:    scripts/verify-post-deploy-completeness.py (+ byte-identical .engine copy).
            pipeline-agent runs it with --pending immediately before appending the stage line;
            exit 1 means the word is PARTIAL (change 2). The build runs it SOFT with --audit as a
            backstop for a dispatch that skipped it (change 1 wiring).
Retires:    nothing. The naming rule stays, because it is the only thing covering the 18 manual
            DEV entries the gate cannot identify (see Residual 1)
Cites:      IMP-0879, IMP-0906, IMP-0907
Residual:   (1) A manual entry with no `operation:` key cannot be recognised in a log. That is
            18 of 20 in DEV and 2 of 11 each in TST/ACC and PRD. The gate counts and prints
            them on every run and never skips them silently. Most are one-off designer steps
            owned by the reviewer.
            (2) A dispatch that imports but writes no `WRITE ATTEMPTED` marker for the import is
            not judged. The marker rule (C-TECH-065, pipeline-agent's report-back block) covers
            that, not this gate. Measured once: the 2026-09-07 lead-agent sequence at
            pipeline.log L156-L162 recorded its import as SUCCESS lines, not as markers.
            (3) The gate reads a marker's outcome word, not the live environment. A push marked
            SUCCEEDED that changed nothing still passes. Verification (a)/(c) owns that.
            (4) pipeline.log has no dispatch id, so two dispatches writing into it at the same
            time share one window (the known concurrent-dispatch class).
            (5) The rule is unconditional: a push the diff did not need is still owed, and its
            absence is PARTIAL. That is by design. The reviewer approved "whether or not the
            dispatch brief names it" on 2026-09-25, and per-dispatch judgement of "not needed"
            is IMP-0879's root cause.
```

**Why a new script and not a check inside [`verify-pipeline-config.py`](../../scripts/verify-pipeline-config.py#L219).** The design allowed either. That script is a static preflight over the config. It is wired HARD at build step [`pipeline-config-preflight`](../../config/revitalise-grant-automation-build.yml#L74) and has no `--selftest`. A log reader inside it would make every build red on the five historical findings, unless a baseline were added in the same change. A sibling script can run HARD where the claim is made (pipeline-agent) and SOFT at build time. It reuses check 13's rule that a manual step is known by its `operation:` key and never by its description ([L227](../../scripts/verify-pipeline-config.py#L227)).

**Why this does not repeat the concern the 2026-09-25 review raised against a log reader.** That review turned down *"a check that reads `pipeline.log` and infers which solution imports should have triggered a push"* because it reads a log for meaning ([review L109](2026-09-25-improvement-review.md#L109)). This gate reads no meaning. It reads the per-operation `WRITE ATTEMPTED: <command> — SUCCEEDED | FAILED | REFUSED` markers that pipeline-agent must write for every live write ([report-back block](../../agents/pipeline-agent.md#L250)). The "did it run" question is answered by the outcome token, and the "was it owed" question by a SUCCEEDED marker for the import. The measurement below shows the one place prose was allowed in, and why it came back out.

#### Real-corpus measurement (the acceptance test the design asks for)

Run against the whole of [`logs/pipeline.log`](../../logs/pipeline.log) (227 lines, 49 success stage lines), each config judged as it was committed at the time of the line (`--as-of-git`), so a step declared later is not demanded of an earlier deploy. The code-app push was first declared on 2026-08-23. **Each finding below was read one at a time and adjudicated.**

| Design variant | Findings | True | False | Precision | Real case missed |
|---|---|---|---|---|---|
| First draft: a stage line's prose may *add* the obligation, markers discharge it | 11 | 6 | 5 | 55% | — |
| The design's literal wording: the operation is *named* anywhere in the dispatch | 4 | 4 | 0 | 100% | [L219](../../logs/pipeline.log#L219), which names the push as REFUSED |
| **Proposed: a SUCCEEDED marker for the import creates the obligation, and only a SUCCEEDED marker for the operation discharges it** | **5** | **5** | **0** | **100%** | [L162](../../logs/pipeline.log#L162), an import recorded without markers (Residual 2) |

The first draft's five false positives, by name: [L20](../../logs/pipeline.log#L20) and [L22](../../logs/pipeline.log#L22) pushed, but recorded it only in prose, before markers were in use. [L62](../../logs/pipeline.log#L62) is a reconciliation line that *mentions* an import. [L157](../../logs/pipeline.log#L157) and [L158](../../logs/pipeline.log#L158) are per-step lines written as stage lines, so one deploy was counted three times. The measurement changed the design: prose no longer creates an obligation.

**The five findings of the proposed design:**

| Line | Deploy | Verdict | Why | Did it matter live? |
|---|---|---|---|---|
| [L148](../../logs/pipeline.log#L148) | 2026-09-05, a form-cell fix | TRUE | import SUCCEEDED ([L145](../../logs/pipeline.log#L145)), no push marker, `SUCCESS (V3)` | Not known. The only Code App commit since the last push lands 40 minutes after it |
| [L167](../../logs/pipeline.log#L167) | 2026-09-08, docs/settings-only build | TRUE | import SUCCEEDED ([L164](../../logs/pipeline.log#L164)), no push marker | No. The line itself records no source change |
| [L197](../../logs/pipeline.log#L197) | 2026-09-22 | TRUE | one of the three the design names | Likely. The live app stayed on the 2026-09-20 build until 2026-09-25 |
| [L207](../../logs/pipeline.log#L207) | 2026-09-24 18:13 | TRUE | one of the three the design names | **Yes.** A Code App commit from 2026-09-23 was not live until the 2026-09-25 push |
| [L219](../../logs/pipeline.log#L219) | 2026-09-25 15:05 | TRUE | push REFUSED by the harness ([L218](../../logs/pipeline.log#L218)), `SUCCESS (V3)` written | No. The dispatch confirmed the live app was already current |

**The design's acceptance test, measured:** it asked that *"the real run must flag the three historical dispatches"* the source finding names. Two of them are flagged ([L197](../../logs/pipeline.log#L197), [L207](../../logs/pipeline.log#L207)). The third, [L202](../../logs/pipeline.log#L202) on 2026-09-24 at 11:47, is **correctly not flagged**. Its import failed on an unsupported form type ([L201](../../logs/pipeline.log#L201)), the stage line says `FAILED`, and a failed deploy owes no post-deploy step. The source finding's description says all three reached import success. For one of them that is wrong, and this review logs that as its own finding.

**Correct negatives:** 16 success lines hold a SUCCEEDED import marker. The other 11 are clean because each also holds a SUCCEEDED push marker. Spot-checked: [L227](../../logs/pipeline.log#L227) against [L226](../../logs/pipeline.log#L226), [L172](../../logs/pipeline.log#L172) against [L171](../../logs/pipeline.log#L171), and [L51](../../logs/pipeline.log#L51) against L48 and L50. A push-only dispatch ([L212](../../logs/pipeline.log#L212)) owes nothing and is not flagged.

**At the cutover date the gate reports 0 findings, and 0 is correct:** no stage line has been written on or after 2026-09-26 yet. The build-time form (`--audit --as-of-git --warn-only`) and `--pending` both exit 0 on today's log.

**Selftest:** 13 fixtures, PASS. They cover declared-and-run clean; declared-not-run; run-but-REFUSED; prose naming the push does not discharge it; push-only owes nothing; prose naming an import creates no obligation; FAILED and PARTIAL are not judged; the underscore marker spelling; the previous dispatch's push does not carry over; a TST/ACC executable step matched by script name; pending with and without the push; and an operation with no evidence literal is a config error.

**Verification level reached:** V1. The script parses and its selftest and corpus runs are green. No pipeline-agent dispatch has yet run it before writing a stage line. That is the V3 observation that closes the two V3 findings below, and nobody in this session can make it.

### Cluster B — a finding's instance list that its own log contradicts

```
CLUSTER: finding-premise-fails-re-measurement  (x1 this review: IMP-0907; the class is live in the digest)
Altitude:   INSTANCE — a counting error in one finding, inherited by one acceptance criterion
Ladder row: "one instance, specific, no general mechanism" → a note, plus an erratum where the
            wrong claim is written
Becomes:    a one-paragraph erratum under WS-X's "Mechanical verification" in the capability
            design, restating the acceptance test as measured above (change 3)
Retires:    nothing
Cites:      IMP-0907
Residual:   nothing checks a finding's claims against the log lines it cites, and nothing
            reasonably could; this is the draft-time premise grep's job
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | `scripts/verify-post-deploy-completeness.py` + `.engine/scripts/verify-post-deploy-completeness.py` (byte-identical) | New gate, text in the appendix. `--pending` for pipeline-agent before the stage line; `--audit` over the log; `REQUIRED_FROM` set to the apply date | IMP-0879, IMP-0906 | YES — `python3 scripts/verify-post-deploy-completeness.py --selftest`; corpus: `… config/revitalise-grant-automation-pipeline.yml --audit --since 2000-01-01 --as-of-git` must print the 5 findings above | `SOFT (--warn-only)` at `config/revitalise-grant-automation-build.yml`, a new step after `routing-reconciliation` ([L134](../../config/revitalise-grant-automation-build.yml#L134)) |
| 2 | agent | `agents/pipeline-agent.md` → section **`## Logging`** only ([L539-L556](../../agents/pipeline-agent.md#L539)) | Adds `PARTIAL` to the stage-line format, and requires the `--pending` check before the stage line; exit 1 means `PARTIAL`, naming each missing operation and its owner | IMP-0879, IMP-0906 | N/A — instruction change | N/A |
| 3 | other | [capability design, WS-X](2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L384) | Erratum paragraph restating the acceptance test as measured (2 of the 3 flagged; the third correctly silent) | IMP-0907 | YES — needle grep | N/A |

**Constraint budget:** 0 of 3 used. No row is needed. The rule's enforcement point is the gate plus pipeline-agent's instruction, and a constraint row would restate change 2.

### Why SOFT at build time and not `SUITE_GATE_EXEMPT`

The build is the one thing that runs whether or not an agent remembers the check. The exemption list's own test is *"does the input exist when a build runs"*, and here it does: `logs/pipeline.log` is always present. It is SOFT because a build cannot fix a past deploy's wrong status word, and halting delivery on a record fact is what the capability design's Group 1 is removing. The HARD enforcement point is pipeline-agent's `--pending` run, where the word is being chosen. [`verify-provisioning-report.py`](../../scripts/verify-build-config.py#L701) is exempt for a different reason: its subject is one dispatch's report. This gate's `--audit` subject is the whole log.

### Exact wording

**Change 1 — build step.** Insert after the `routing-reconciliation` step:

```yaml
  # SOFT backstop. pipeline-agent runs this gate with --pending BEFORE it writes a stage line
  # (agents/pipeline-agent.md → Logging); this run catches a dispatch that skipped that. It reads
  # WRITE ATTEMPTED markers only, never stage-line prose. Measured over the whole log before
  # wiring: 5 findings / 5 true, 49 success lines (improvement review 2026-09-26-3).
  - name: post-deploy-completeness
    command: python3 scripts/verify-post-deploy-completeness.py config/revitalise-grant-automation-pipeline.yml --audit --as-of-git --warn-only
```

**Change 2 — [`agents/pipeline-agent.md` → `## Logging`](../../agents/pipeline-agent.md#L539).** The format line at [L543](../../agents/pipeline-agent.md#L543) becomes:

```
[YYYY-MM-DD HH:MM] [PIPELINE] [<slug>] [<ENV>] <SUCCESS|PARTIAL|FAILED|HELD> — <summary>
```

The paragraph at [L546](../../agents/pipeline-agent.md#L546) is kept verbatim, and this is inserted directly after it:

> **Naming an entry is not running it, so run the check before you choose the word.** Immediately
> before you append the stage line:
>
> ```bash
> python3 scripts/verify-post-deploy-completeness.py config/<slug>-pipeline.yml --env <env> --pending ; echo "exit=$?"
> ```
>
> Exit 1 means a declared `post_deploy` operation has no `WRITE ATTEMPTED: … — SUCCEEDED` marker in
> this dispatch. **The word is then `PARTIAL`, never `SUCCESS`.** Name each missing operation, why it
> did not run, and who owns running it. A refusal, a skip judged harmless, and a step "not needed
> for this diff" are all `PARTIAL`: the check reads markers, and no prose discharges it. The same
> word governs this stage's gate output. `PARTIAL` halts, retries and rolls back nothing. It is the
> honest status of a deploy with a declared step still outstanding (`IMP-0906`: the first
> dispatch after the naming rule above named its push as REFUSED and still wrote `SUCCESS`).

Nothing else in `agents/pipeline-agent.md` changes. **Group 1 of the capability design also edits this file**, in *"Before you dispatch ANOTHER agent to fix what a finding describes"* ([L112-L131](../../agents/pipeline-agent.md#L112)). The two edits do not overlap. If both are approved, **Group 1 applies first**, and this change is then re-anchored on the `## Logging` heading and the paragraph text above, never on line numbers.

**Change 3 — erratum**, appended to WS-X's *Mechanical verification* paragraph in the capability design:

> **Erratum (improvement review 2026-09-26-3):** of the three dispatches the source finding names, the
> 2026-09-24 11:47 one failed at import and owes no post-deploy step. The check flags the other two
> and must not flag that one. Measured over the whole log: 5 findings, 5 true.

### Bookkeeping on approval

| Entry | `observable_at` | Disposition | Why |
|---|---|---|---|
| IMP-0879 | V3 | **DEFER** (already reviewer-deferred; `deferred_reason` gains this review's measurement; `revisit_when` replaced) | A V3 defect closes only on a re-run of a real DEV dispatch, and nobody in this session can run one |
| IMP-0906 | V3 | **DEFER from the start** | same |
| IMP-0907 | n/a | **CLOSE**, with `evidence_grep` on change 3's erratum | a document defect; the needle is enough |

Proposed `revisit_when` for both V3 entries, replacing IMP-0879's current one, which has literally been satisfied ([L219](../../logs/pipeline.log#L219) named every entry): *"the first pipeline-agent DEV dispatch after verify-post-deploy-completeness.py lands runs it with --pending before its stage line, and the stage line's status word matches the gate's verdict"*.

**Simulated before parking.** The three dispositions above, plus change 3's erratum, were applied to a scratch copy of the log and of `docs/improvements/`. `verify-improvement-log.py --check` was then run against that copy: exit 0, no trigger, and no error on any of the three entries. IMP-0906 reads as reviewer-deferred and IMP-0907 as applied, with its needle resolving. The real log was never touched by the simulation.

**Drift this draft caused, left for the owner.** Appending this review's two findings and regenerating the digest, as the capture contract requires, moved the registered digest line count in `scripts/generate-known-failure-modes.py`: `verify-derived-counts.py` reports 779 written against 787 measured. That step is SOFT. That script is being edited by the parallel Group 4 draft, so this review does not touch it. Whichever of the two applies last re-derives the figure.

At apply time the registered count of `verify-*.py` scripts in `agents/improvement-agent.md` is **re-derived with `ls scripts/verify-*.py | wc -l`, never typed**. The WS-W1 draft running in parallel also adds scripts, so whichever review applies second derives the number after the first.

---

## 4. Retirements

> Retirement check performed: 86 live constraint rows, 10 retired (derived with the commands in
> `agents/improvement-agent.md`). The rows touching post-deploy work are C-TECH-040, C-TECH-042,
> C-TECH-064 and C-TECH-065. None of them states "every declared post-deploy step ran", so none is
> made redundant by this gate. The stage-line naming rule in pipeline-agent.md is also kept: it
> is the only coverage for manual entries that carry no `operation:` key.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0862, IMP-0887, IMP-0891, IMP-0892, IMP-0893, IMP-0894, IMP-0895, IMP-0896, IMP-0897, IMP-0898, IMP-0899, IMP-0900

These are the 12 entries in state `unread` when this dispatch started. They are outside a WS-X capability dispatch, and they belong to the next batched run. One is related: the harness refusal of the push at [L218](../../logs/pipeline.log#L218) is recorded as a refusal finding. It proposes no change to this gate and is left for that batch.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Lessons added by this review | — | +2 (IMP-0906, IMP-0907) |
| `pipeline-dispatch-stops-before-declared-post-deploy` | x1 | x2 |

Regenerated at apply with `python3 scripts/generate-known-failure-modes.py` and confirmed with `--check`. Parallel dispatches are appending to the same log, so the absolute counts are derived at apply time rather than stated here.

---

## What you need to decide

**Accept the restated acceptance test for WS-X?**

**Problem** — The design asks the check to flag three past deploys, but one of them failed at import, so flagging it would be a false alarm.
**Suggested fix** — Accept "flags L197 and L207, correctly not L202", plus the three further real cases the measurement found, as WS-X's acceptance. Change 3 writes this into the design.
**What happens if you don't** — The design's acceptance test can only be met by a gate that also flags failed deploys, which would put the false-alarm class this project has measured five times back into a new gate.
[capability design, WS-X](2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L384)

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-26-improvement-review-3.md

Findings processed: 3 NEW  →  2 clusters
Regression check:   3 prior changes audited, 1 classes recurred
Proposed:           0 constraints (cap 3), 1 gates/scripts, 0 skill/knowledge edits,
                    1 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 1 left as notes
Digest:             will regenerate — +2 lessons, 1 class moves to x2

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

Verification: the selftest passed (13 of 13). The corpus run over 49 success lines gave 5 findings, all 5 true. The cutover-date run and `--pending` both exited 0. The queue gate exits 0 with this review's three entries stamped. **Not verified:** no pipeline-agent dispatch has run the check yet (V3). The script exists only as the appendix below until it is applied.

---

## 8. Applied

**Authorisation, recorded before any edit (2026-09-26 20:34).**

| Field | Value |
|---|---|
| `authorised_by` | Xander Lykopoulos (the reviewer) |
| `relayed_by` | lead-agent, quoting the reviewer's own conversation turn in the commissioning session (`logs/routing.log`, 2026-09-26 20:33 `RESUMED:improvement-agent`) |
| Keyword, verbatim | "APPROVE IMPROVEMENTS for WS-X" |
| Decision, verbatim | "Restated test is approved." (the one decision in this review; change 3 applies it) |
| Artefacts this act produces | changes 1–3 of §3 and the bookkeeping table, as drafted |

All four conditions of the relay rule in `agents/WORKFLOW.md` (*What channel a keyword must arrive through*) hold. The relay comes from lead-agent, carries the keyword verbatim, names the human, and says it is quoted from that session's own turn.

**Re-verified before applying (step 8).** No entry appended since the draft carries `corrects` naming IMP-0879, IMP-0906 or IMP-0907. `logs/pipeline.log` is unchanged at 227 lines. The design anchor, the build-config insertion point and the `## Logging` heading were all re-read. The script count was 66 (WS-W1 had landed). **Nothing was withheld and nothing was narrowed** in the parts applied so far.

| # | Change | Landed at | Verified by |
|---|---|---|---|
| 1 | The gate, extracted byte-for-byte from this document's appendix | `scripts/verify-post-deploy-completeness.py` and `.engine/scripts/verify-post-deploy-completeness.py` (byte-identical, `cmp`) | `--selftest` 13/13 PASS. The full-log run `--audit --since 2000-01-01 --as-of-git` exits 1 with exactly L148, L167, L197, L207, L219. The build form exits 0 with 0 findings, and `--pending --env dev` exits 0 |
| 1 | SOFT step `post-deploy-completeness` after `routing-reconciliation` | `config/revitalise-grant-automation-build.yml` | `verify-build-config.py` exit 0 |
| 3 | Erratum under WS-X's *Mechanical verification* | capability design | needle grep: 1 match |
| 2 | `## Logging` edit in `agents/pipeline-agent.md` | `agents/pipeline-agent.md` (engine), placed by heading and text after Group 1's edits were final in the working tree | needle grep "Naming an entry is not running it": 1 match; format line carries `PARTIAL`: 1 match |
| — | Registered count 66 → 67 (`improvement-agent-verify-script-count`) | `agents/improvement-agent.md` L551 (engine) | `ls scripts/verify-*.py \| wc -l` = 67; `verify-derived-counts.py`: 11 of 11 claims match |

**Entries.**

| Entry | Outcome |
|---|---|
| IMP-0907 | **APPLIED**, with `evidence_grep` on the erratum (observable at n/a) |
| IMP-0879, IMP-0906 | **Deferred with reason**, as drafted. `revisit_when` is the approved text, verbatim |

**Completed after Group 1 was final.** Lead-agent relayed that Group 1's edits to `agents/pipeline-agent.md` and `agents/improvement-agent.md` were final in the working tree. It also relayed the reviewer's instruction, verbatim: *"Wait until group 1 has landed. And all items of the plan are processed. Then we do 1 big commit."* So the ordering condition became "final in the working tree" instead of "on origin". Both files were re-read immediately before editing, and change 2 and the count line then landed.

**Not published, by the reviewer's instruction.** Nothing from this review is committed or pushed. Earlier, the harness permission classifier refused an engine commit and push from this dispatch ("Out-of-Place Publication"). It was not retried, and the reviewer has since said the commit comes later as one commit. The paths to commit are:

- **Engine (`.engine`):** `scripts/verify-post-deploy-completeness.py`, `agents/pipeline-agent.md` (the `## Logging` hunk), `agents/improvement-agent.md` (L551, the count).
- **Instance:** `scripts/verify-post-deploy-completeness.py`, `config/revitalise-grant-automation-build.yml` (the `post-deploy-completeness` step), `docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md` (the erratum), `docs/improvements/2026-09-26-improvement-review-3.md`, and this review's lines in `logs/improvement-log.jsonl` (IMP-0906 and IMP-0907 appended; IMP-0879, IMP-0906 and IMP-0907 updated), plus the regenerated `logs/known-failure-modes.md` and `logs/known-failure-modes-appendix.md`. The instance commit must also bump the `.engine` pointer after the engine push.

**Pre-commit correction: the engine gate carried this client's environment chain (2026-09-27).** Lead-agent's client-literal sweep of the engine diff found two defects under the same authorisation and design decision S-5 (engine files carry no client facts):
- `env_of()` matched untagged stage lines against a hard-coded `dev|tst_acc|prd`. This was functional: at an instance with other environment names it would silently read nothing.
- Two fixtures used `tst_acc` / `TST_ACC`.

My draft's client-literal grep searched for the client's name, table prefix and environment host prefix. It did not search for the environment-chain names, so it missed this.

The corrections, in `.engine/scripts/verify-post-deploy-completeness.py` only (5 hunks, 44 lines changed):
- `env_of()` now builds its alternation from the pipeline config's own `environments` keys, the one source the script already reads, escaped and case-insensitive, and returns the declared key.
- A bracketed tag is still taken as written: an undeclared tag owes nothing, because `checkable()` finds no block for it.
- The fixtures use a generic `dev/test/prod` chain.
- Two fixtures were added. A non-default declared name (`staging`) is recognised, and an undeclared one (`uat`) is not.

The regexes stay in this script rather than moving to `lib/deploy_markers.py`: stage-line environment parsing has no other reader, and neither `lib/work_items.py` nor the ledger scripts parse stage lines. The instance wrapper is unchanged.

| Check after the correction | Result |
|---|---|
| `--selftest` (wrapper and engine direct) | PASS, 15 fixtures |
| Mutation: the old hard-coded `env_of` against the new selftest | FAILS on "a non-default environment name the config declares must be recognised", so the fixture can fail |
| Real-log audit `--audit --since 2000-01-01 --as-of-git` | exit 1, **byte-identical** to before the correction (`cmp`), with L148, L167, L197, L207, L219 |
| Build form `--audit --as-of-git --warn-only` | exit 0, byte-identical to before |
| `--pending --env dev` | exit 0 |
| `verify-work-items.py --selftest`, `work-items.py --selftest` | both OK |
| `verify-engine-instance-split.py` | exit 0 (96 scripts) |
| `grep -ciE 'tst_acc\|tst/acc'` on the engine gate | 0 (`lib/deploy_markers.py` was not touched and is also 0) |

The miss is logged as IMP-0917 (friction, observable at n/a) and closed **APPLIED** on the correction, with `evidence_grep` on the engine gate.

**Gates run after applying (working tree):**

| Gate | Result |
|---|---|
| `verify-post-deploy-completeness.py --selftest` | exit 0, 13 fixtures |
| `verify-build-config.py config/revitalise-grant-automation-build.yml` | exit 0 |
| `verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml` | exit 0 |
| `generate-known-failure-modes.py --check` | current |
| `verify-class-defences.py` | exit 0 |
| `verify-engine-instance-split.py` | exit 0 (95 scripts) |
| `verify-doc-line-links.py` | exit 0 |
| `verify-derived-counts.py` | exit 0, 11 of 11 claims match (re-run after the count edit) |
| `verify-improvement-log.py --check` | exit 0, re-run after Group 1 was final. At the first pass it exited 1 on IMP-0717's needle while Group 1 was mid-edit on `agents/WORKFLOW.md`. This review's three entries raise no error or warning |
| full-log run, after all edits | exit 1, with exactly L148, L167, L197, L207, L219; `--pending --env dev` exits 0 |

---

## Appendix — the gate, exactly as measured

This is the text that produced every figure above. Change 1 lands it verbatim. The only edit is `REQUIRED_FROM`, which is set to the apply date.

```python
#!/usr/bin/env python3
"""A deploy stage may not claim SUCCESS while a declared post_deploy operation did not run.

WHY THIS EXISTS. IMP-0879: `config/<slug>-pipeline.yml`'s dev block declares a post_deploy entry
carrying `operation: code-app-push`, and consecutive DEV dispatches imported the solution, wrote
`SUCCESS (V3)` to `logs/pipeline.log`, and never pushed the Code App. The live app ran five days
behind the solution. A prose rule then required every stage line to NAME each declared entry, and
the next dispatch did name it -- as REFUSED -- and still wrote SUCCESS. Naming is not running.

WHAT IT CHECKS. For every stage line that claims SUCCESS (or DEPLOYED) for an environment, over
the lines of that one dispatch:

  1. TRIGGER -- did this dispatch deploy? Yes when the window holds a `WRITE ATTEMPTED` marker
     for the environment's deploy command with outcome SUCCEEDED. Markers only: a first draft
     also let the stage line's prose add the obligation, and measured 11 findings / 6 true over
     this project's log -- a reconciliation line that MENTIONS an import, and per-step lines
     written as stage lines, are not deploys. Markers only: 5 findings / 5 true.
  2. EVIDENCE -- for each CHECKABLE post_deploy entry of that environment, the window must hold a
     `WRITE ATTEMPTED` marker naming it with outcome SUCCEEDED. A stage line's prose never counts
     as evidence: "pac code push -- REFUSED" and "pac code push not needed" both contain the words.
  3. An entry is CHECKABLE when it carries an `operation:` key (a manual step, known by that key
     and never by its description -- the same rule as verify-pipeline-config.py check 13) or an
     executable `script:` (known by the script's file name). A manual entry with no `operation:`
     key cannot be identified in a log and is COUNTED and printed, never silently skipped.

Markers are read in all three spellings the log carries today (`WRITE ATTEMPTED:`, the
ISO-stamped form, and `WRITE_ATTEMPTED —`). Accepting a spelling can only discharge an obligation
with a real SUCCEEDED marker, so widening the grammar here removes false reports and adds none.

MODES.
  --pending   the lines after the last stage line: the dispatch that is running NOW, before it
              writes its stage line. pipeline-agent runs this; exit 1 means the line must read
              PARTIAL and name each missing operation.
  --audit     every success stage line on or after --since (default REQUIRED_FROM).
              --as-of-git judges each line against the config committed at that moment, so an
              operation declared later is not demanded of an earlier dispatch.

Exit 0 clean, 1 on any finding (0 with --warn-only), 2 on a usage or config error.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("verify-post-deploy-completeness: PyYAML is required", file=sys.stderr)
    sys.exit(2)

# Stage lines on or after this date are judged by default. Set to the date the gate lands, so
# finished work written before the rule existed is reported only when asked for (--since).
REQUIRED_FROM = "2026-09-26"

# The evidence literal for each `operation:` value. Fail-closed: an operation not listed here and
# carrying no step-level `evidence:` is a config error, so a new operation cannot go unchecked.
OPERATION_EVIDENCE = {"code-app-push": "pac code push"}

# Deploy commands, when the environment block names none of its own. `pac pipeline deploy` is the
# Power Platform Pipelines promotion verb (TST/ACC, PRD).
DEFAULT_DEPLOY_EVIDENCE = ("pac solution import", "pac pipeline deploy")

STAGE = re.compile(r"^\[(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2})\] \[PIPELINE\] "
                   r"\[(?P<slug>[^\]]+)\](?: \[(?P<env>[^\]]+)\])? ?(?P<body>.*)$")
# Tokens that are PART of a dispatch, not the end of one.
IN_DISPATCH = ("WRITE", "PREFLIGHT", "CORRECTION", "NOTE")
SUCCESS = ("SUCCESS", "DEPLOYED")
ATTEMPTED = re.compile(r"WRITE[ _]ATTEMPTED\s*[:—–-]\s*(?P<body>.+)$")
OUTCOME = re.compile(r"\b(SUCCEEDED|FAILED|REFUSED|DENIED)\b")
MANUAL = re.compile(r"^\s*(manual|n/a)\b", re.IGNORECASE)


def norm(text: str) -> str:
    return " ".join(text.split()).casefold()


def env_of(tag: str | None, body: str) -> str | None:
    if tag:
        return tag.strip().lower().replace("/", "_")
    m = re.match(r"\s*\S+\s+(dev|tst_acc|prd)\b", body, re.IGNORECASE)   # "DEPLOYED_V3 dev"
    if m:
        return m.group(1).lower()
    m = re.search(r"\b(DEV|TST_ACC|PRD)\b", body[:40])                      # "PARTIAL — DEV import"
    return m.group(1).lower() if m else None


def status_of(body: str) -> str:
    return body.lstrip().split(" ", 1)[0].upper() if body.strip() else ""


def succeeded_markers(lines: list[str]) -> list[str]:
    """The command half of every WRITE ATTEMPTED marker whose FIRST outcome token is SUCCEEDED."""
    out = []
    for line in lines:
        m = ATTEMPTED.search(line)
        if not m:
            continue
        o = OUTCOME.search(m.group("body"))
        if o and o.group(1) == "SUCCEEDED":
            out.append(norm(m.group("body")[:o.start()]))
    return out


class ConfigError(Exception):
    pass


def checkable(config: dict, env: str) -> tuple[list[tuple[str, str]], int, list[str]]:
    """(label, evidence) per checkable post_deploy entry; count of unkeyed manual entries; deploy literals."""
    block = (config.get("environments") or {}).get(env)
    if block is None:
        return [], 0, []
    seen: dict[str, str] = {}
    unkeyed = 0
    for i, step in enumerate(block.get("post_deploy") or []):
        if not isinstance(step, dict):
            continue
        op = str(step.get("operation") or "").strip()
        script = str(step.get("script") or step.get("command") or "").strip()
        if op:
            ev = str(step.get("evidence") or OPERATION_EVIDENCE.get(op) or "").strip()
            if not ev:
                raise ConfigError(f"environments.{env}.post_deploy[{i}]: operation '{op}' has no "
                                  f"evidence literal. Add it to OPERATION_EVIDENCE or declare "
                                  f"`evidence:` on the step, or it can never be checked.")
            seen.setdefault(f"operation:{op}", norm(ev))
        elif script and not MANUAL.match(script):
            name = Path(script.split()[0]).name
            seen.setdefault(f"script:{name}", norm(name))
        else:
            unkeyed += 1
    deploy = block.get("deploy_command") or (config.get("alm") or {}).get(f"stage_{env}_command")
    literals = [norm(" ".join(str(deploy).split()[:3]))] if deploy else \
        [norm(d) for d in DEFAULT_DEPLOY_EVIDENCE]
    return list(seen.items()), unkeyed, literals


def judge(lines: list[str], window: range, config: dict, env: str) -> list[str]:
    """Missing operation labels for one dispatch window, or [] when nothing was owed or all ran."""
    entries, _, deploy = checkable(config, env)
    if not entries:
        return []
    ran = succeeded_markers([lines[i] for i in window])
    deployed = any(d in m for m in ran for d in deploy)
    if not deployed:
        return []
    return [label for label, ev in entries if not any(ev in m for m in ran)]


def stage_lines(lines: list[str]):
    for i, line in enumerate(lines):
        m = STAGE.match(line)
        if m and not status_of(m.group("body")).startswith(IN_DISPATCH):
            yield i, m


def config_as_of(path: Path, date: str, time: str, repo: Path, cache: dict) -> dict | None:
    sha = subprocess.run(["git", "-C", str(repo), "log", "-1", f"--before={date} {time}",
                          "--format=%H", "--", str(path)], capture_output=True, text=True).stdout.strip()
    if not sha:
        return None
    if sha not in cache:
        blob = subprocess.run(["git", "-C", str(repo), "show", f"{sha}:{path}"],
                              capture_output=True, text=True).stdout
        cache[sha] = yaml.safe_load(blob) or {}
    return cache[sha]


def audit(lines, config, config_path, since, as_of_git, repo) -> tuple[list[str], dict]:
    findings, stats, cache = [], {"success": 0, "as_of_fallback": 0}, {}
    prev = -1
    for i, m in stage_lines(lines):
        body, env = m.group("body"), env_of(m.group("env"), m.group("body"))
        window, prev = range(prev + 1, i + 1), i
        if not status_of(body).startswith(SUCCESS) or m.group("date") < since or not env:
            continue
        stats["success"] += 1
        cfg = config_as_of(config_path, m.group("date"), m.group("time"), repo, cache) \
            if as_of_git else config
        if cfg is None:            # no commit that old (a shallow clone): judge against the
            cfg = config           # current config and SAY so, never skip the line silently
            stats["as_of_fallback"] += 1
        missing = judge(lines, window, cfg, env)
        if missing:
            findings.append(
                f"L{i + 1} [{m.group('date')} {m.group('time')}] {m.group('slug')} {env} "
                f"{status_of(body)}: declared post_deploy {', '.join(missing)} has no SUCCEEDED "
                f"WRITE ATTEMPTED marker in this dispatch (L{window.start + 1}-L{i + 1}). The "
                f"stage line must read PARTIAL and name each one, with its owner.")
    return findings, stats


def pending(lines, config, env) -> list[str]:
    last = max((i for i, _ in stage_lines(lines)), default=-1)
    window = range(last + 1, len(lines))
    missing = judge(lines, window, config, env)
    return [f"pending dispatch (L{window.start + 1}-L{len(lines)}) {env}: declared post_deploy "
            f"{', '.join(missing)} has no SUCCEEDED WRITE ATTEMPTED marker. Do not write SUCCESS: "
            f"write PARTIAL and name each one, with its owner."] if missing else []


# ── selftest ──────────────────────────────────────────────────────────────────────────────
CFG = {"alm": {"stage_dev_command": "pac solution import --path x"},
       "environments": {
           "dev": {"post_deploy": [{"operation": "code-app-push", "script": "manual"},
                                   {"script": "manual", "description": "designer save"}]},
           "tst_acc": {"post_deploy": [{"script": "provisioning/dataverse/seed-settings.ps1 -Env test"}]}}}
H = "[2026-09-30 10:0{}] [PIPELINE] [f] [DEV] "
IMPORT_OK = "2026-09-30T10:01:00Z WRITE ATTEMPTED: pac solution import -Env dev — SUCCEEDED"
PUSH_OK = H.format(2) + "WRITE ATTEMPTED: pac code push -Env dev — SUCCEEDED (app x)"


def _run(lines, env="dev", cfg=CFG):
    return audit(lines, cfg, Path("x"), "2026-01-01", False, Path("."))[0] if env != "pending" \
        else pending(lines, cfg, "dev")


def selftest() -> int:
    cases = [
        ("declared and run -> clean", [IMPORT_OK, PUSH_OK, H.format(3) + "SUCCESS (V3)"], 0),
        ("declared, not run -> finding", [IMPORT_OK, H.format(3) + "SUCCESS (V3)"], 1),
        ("run but REFUSED -> finding",
         [IMPORT_OK, H.format(2) + "WRITE ATTEMPTED: pac code push — REFUSED (classifier)",
          H.format(3) + "SUCCESS (V3)"], 1),
        ("prose naming the push never discharges it",
         [IMPORT_OK, H.format(3) + "SUCCESS (V3) — pac code push not needed, no app diff"], 1),
        ("no deploy in dispatch (push-only) -> nothing owed",
         [PUSH_OK, H.format(3) + "SUCCESS — code push only"], 0),
        ("prose naming an import is not a deploy (no marker) -> nothing owed",
         [H.format(3) + "SUCCESS (V3) — reconciles the earlier pac solution import"], 0),
        ("FAILED and PARTIAL stage lines are not success claims",
         [IMPORT_OK, H.format(3) + "FAILED — x", IMPORT_OK, H.format(4) + "PARTIAL — push owed"], 0),
        ("underscore spelling accepted",
         [IMPORT_OK, H.format(2) + "WRITE_ATTEMPTED — pac code push, build 1 — SUCCEEDED",
          H.format(3) + "SUCCESS (V3)"], 0),
        ("previous dispatch's push does not carry over",
         [IMPORT_OK, PUSH_OK, H.format(3) + "SUCCESS (V3)", IMPORT_OK, H.format(4) + "SUCCESS (V3)"], 1),
        ("executable step matched by script name (tst_acc)",
         ["[2026-09-30 10:01] [PIPELINE] [f] [TST_ACC] WRITE ATTEMPTED: pac pipeline deploy — SUCCEEDED",
          "[2026-09-30 10:02] [PIPELINE] [f] [TST_ACC] SUCCESS"], 1),
    ]
    failures = []
    for name, lines, expected in cases:
        got = len(_run(lines))
        if got != expected:
            failures.append(f"{name}: expected {expected} finding(s), got {got}")
    if len(_run([IMPORT_OK], env="pending")) != 1:
        failures.append("pending: an import with no push, before the stage line, must report")
    if _run([IMPORT_OK, PUSH_OK], env="pending"):
        failures.append("pending: an import plus a SUCCEEDED push must be clean")
    try:
        checkable({"environments": {"dev": {"post_deploy": [{"operation": "new-op"}]}}}, "dev")
        failures.append("an operation with no evidence literal must be a config error")
    except ConfigError:
        pass
    if failures:
        print("verify-post-deploy-completeness --selftest: FAILED")
        for f in failures:
            print("  " + f)
        return 1
    print(f"verify-post-deploy-completeness --selftest: PASS — {len(cases) + 3} fixtures")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config", nargs="?", type=Path)
    ap.add_argument("--log", type=Path, default=Path("logs/pipeline.log"))
    ap.add_argument("--env")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--pending", action="store_true")
    mode.add_argument("--audit", action="store_true")
    mode.add_argument("--selftest", action="store_true")
    ap.add_argument("--since", default=REQUIRED_FROM)
    ap.add_argument("--as-of-git", action="store_true")
    ap.add_argument("--warn-only", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.config or not args.config.is_file() or not args.log.is_file():
        print("verify-post-deploy-completeness: config and --log must both exist", file=sys.stderr)
        return 2
    config = yaml.safe_load(args.config.read_text()) or {}
    lines = args.log.read_text().splitlines()
    try:
        if args.pending:
            if not args.env:
                print("--pending needs --env", file=sys.stderr)
                return 2
            findings, summary = pending(lines, config, args.env), f"pending window, env {args.env}"
        else:
            findings, stats = audit(lines, config, args.config, args.since, args.as_of_git, Path("."))
            summary = f"{stats['success']} success stage line(s) since {args.since}"
            if stats["as_of_fallback"]:
                summary += (f"; {stats['as_of_fallback']} judged against the CURRENT config "
                            f"(no commit of it that old in this clone)")
        for env in (config.get("environments") or {}):
            entries, unkeyed, _ = checkable(config, env)
            if unkeyed:
                print(f"NOTE: environments.{env}: {len(entries)} checkable post_deploy entr(y/ies); "
                      f"{unkeyed} manual entr(y/ies) carry no `operation:` key and cannot be checked "
                      f"from the log.")
    except ConfigError as exc:
        print(f"verify-post-deploy-completeness: CONFIG ERROR — {exc}", file=sys.stderr)
        return 2
    for f in findings:
        print(("WARNING: " if args.warn_only else "FINDING: ") + f)
    print(f"verify-post-deploy-completeness: {len(findings)} finding(s) — {summary}")
    return 0 if (args.warn_only or not findings) else 1


if __name__ == "__main__":
    sys.exit(main())
```
