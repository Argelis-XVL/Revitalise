# Improvement Review — 2026-08-21 (fourth review this date)

**Trigger:** one `blocker` appended by `test-agent` at 13:05 from the TST/ACC retry recorded in
[docs/tests/acc-walkthrough-data-test-report.md](../tests/acc-walkthrough-data-test-report.md).
Processed immediately under the do-not-batch rule, as its own cycle, after review 3 closed.

**Status:** AWAITING `APPROVE IMPROVEMENTS`. Nothing in section 3 has been applied.

---

## 1. Regression check — did review 3's changes work?

Applied minutes ago, so most have had nothing to bite on. One already has a result.

| Prior change | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|
| `evidence_grep` on APPLIED entries — [verify-improvement-log.py](../../scripts/verify-improvement-log.py) | `evidence-rule-satisfied-by-a-forward-reference` | No — and it **fired correctly on its first real run** | **Working, proven.** It rejected an `APPLIED` claim written by this agent during review 3: the entry asserted `verify-environment-access.ps1` contained a string that differed by one capital letter. Under the old rule — the file exists, so the claim stands — it would have passed. |
| Check 11, settings content — [verify-pipeline-config.py](../../scripts/verify-pipeline-config.py) | `gate-reassures-wrongly` | No | **Working.** Reports 18 unowned keys and 4 accepted ones; the suite asserts the failure is exactly that set. |
| Check 12 + [verify-environment-access.ps1](../../provisioning/dataverse/verify-environment-access.ps1) | `provisioning-identity-not-onboarded-to-target-environment` | No | **Working, and it changed the facts.** Run live it returns PASS against DEV *and* TST/ACC, establishing that the application user now exists — which is what makes today's finding a genuinely different defect rather than the same one. |
| `C-TECH-065` | as above | n/a | Too new. |

**The regression check has a bearing on this cycle's finding.** Review 3's probe proves the
identity now reaches TST/ACC. So the flow not firing is not an access problem, and the two
blockers are not the same blocker wearing different clothes.

---

## 2. Clusters and promotion decisions

### CLUSTER — the trigger metadata ladder (6 findings, each defeated by the next)

```
CLUSTER:    a Dataverse-triggered flow reports every correct state and does not fire
            (IMP-0148, prior instances IMP-0104, IMP-0106, IMP-0113, IMP-0114, IMP-0136)
Class:      exit-zero-does-not-mean-created (x13 overall)
Altitude:   CLASS, and an EVIDENCE-CLASS change rather than another assertion.
Ladder row: "second instance -> generalise. Instance patches are forbidden here."
Becomes:    a behavioural probe — provisioning/dataverse/verify-flow-trigger.ps1
Retires:    no constraint; it RETIRES A HABIT — the metadata checklist may no longer be
            recorded as evidence that a trigger works
Cites:      IMP-0148, IMP-0104, IMP-0106, IMP-0113, IMP-0114, IMP-0136
```

Read the ladder in order. Each rung is a real fix that added one more thing to read, and each
was defeated by the next incident:

| Finding | What was added to the checklist | How the next one defeated it |
|---|---|---|
| `IMP-0100` | `statecode` must be 1, not 0 | statecode 1 with no registration at all |
| `IMP-0104` | so also assert a `callbackregistration` row exists | a row existed but predated the import |
| `IMP-0114` | so also compare its `createdon` against the flow's `modifiedon` | a designer save silently changed the trigger's scope |
| `IMP-0106` | so also re-read `subscriptionRequest/scope` from `workflow.clientdata` | — |
| `IMP-0148` | **every one of the above passes, and the flow still does not fire** | — |

`IMP-0148` is the terminal proof that the checklist is the wrong *kind* of evidence. The
registration is not stale, the scope is 4, `runas` is 3, the message is Create, the entity is
`rev_application`, and 12 of 12 rows sat unscored for nine minutes with **no** `asyncoperation`
and **no** error-log row — the platform never attempted the call. Adding a seventh field to read
would be the instance patch the altitude rule forbids, and on this evidence it would not work.

**The property, independent of the instance:** *a trigger is proven by causing it to fire, not by
reading the state that is supposed to mean it will.* In `C-TECH-053`'s own vocabulary the whole
checklist is V3 — accepted by the target — being recorded as though it were V5.

**What this does and does not do.** It **detects**; it cannot **fix**. The remedy for a dead
registration is a human opening the flow in the Power Automate designer and saving it
(`IMP-0104`, `IMP-0114`), never a `statecode` PATCH (`IMP-0113`), and no identity this project
holds has maker access to TST/ACC. So the probe's value is that it converts a nine-minute silent
non-event into one FAIL line naming the person and the click. That is worth building; claiming
more would be dishonest.

**Residual.** The probe writes a real row to a real environment, so it is refused where writes
are refused (`IMP-0084`'s class) and must be safe to run against production — it therefore
creates one canary, waits a bounded time, and deletes it in a `finally`. A canary that is
created and not cleaned up is worse than no probe, and the delete path needs its own test. It
also cannot distinguish "the trigger is dead" from "the flow ran and failed before writing" —
so it reports the three observable outcomes separately (`rev_scoredon` set / an `asyncoperation`
exists / an error-log row exists) rather than one boolean.

---

## 3. Proposed changes

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | script (new) | `provisioning/dataverse/verify-flow-trigger.ps1` | The canary probe. Creates ONE minimal `rev_application` row, polls up to a bounded timeout for any of the three observable effects, deletes the canary in a `finally`, and reports `PASS`/`FAIL` per the provisioning script contract. The FAIL detail names the remedy exactly: open the flow in the Power Automate designer and save it; do not PATCH `statecode` | IMP-0148, IMP-0104, IMP-0114 | YES — Pester tests in `DataverseScripts.Tests.ps1`, mocked for both outcomes and for the cleanup path |
| 2 | config | [config/revitalise-grant-automation-pipeline.yml](../../config/revitalise-grant-automation-pipeline.yml) | Add the probe as the FIRST `smoke_tests` entry for `tst_acc` and `prd`, and to `dev`. A deploy that leaves a dead trigger currently reports success | IMP-0148 | YES — `python3 scripts/verify-pipeline-config.py` |
| 3 | script | [provisioning/dataverse/seed-test-data.ps1](../../provisioning/dataverse/seed-test-data.ps1) | The test-agent's own proposal: after the existing preconditions pass, seed ONE probe row and assert the effect before loading the remaining eleven. Twelve wasted rows and a nine-minute wait become one row and a bounded wait | IMP-0148 | YES — extends the existing precondition block, asserted in `DataverseScripts.Tests.ps1` |
| 4 | constraint | [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) — **amend, no new row** | Add to `Verify By`: for a Dataverse-triggered flow, a metadata assertion (`statecode`, `callbackregistration`, `subscriptionRequest`) may **not** be recorded as evidence that the trigger works. The evidence is an observed run. Amending rather than adding keeps the rule count flat — the property is already this row's subject | IMP-0148 + the five prior rungs | YES — the probe is the command |
| 5 | knowledge | `knowledge/technology/testing-tools.md` | The ladder table from section 2, so the next agent does not add a seventh field to read | IMP-0148 | N/A — instruction |

**No new constraint.** The cluster's home is an existing row whose subject is already "environment
state that solution source cannot express, verified live"; what was wrong is that its `Verify By`
enumerated only metadata queries, which is exactly what this finding defeats.

---

## 4. Retirements

**Candidate: `C-TECH-023`** —
[technology-constraints.md#L63](../../constraints/technology/technology-constraints.md#L63),
SOFT, *"New dependencies must be from sources approved in `stack-overview.md`"*, `Verify By`:
*"Architecture review; code review."*

It is the **fourth member of a family whose other three were retired on 2026-08-19** —
`C-TECH-020` (dependencies pinned), `C-TECH-021` (dependency scan), `C-TECH-022` (licence check)
— all for one reason: this repository has no `package.json`, no `requirements.txt` and no
`.csproj` package reference, so there is nothing to audit. `C-TECH-023` says the same thing about
the same absent manifest and was simply missed in that sweep. Its `Verify By` is also
non-mechanical, which `constraints/README.md` rule 5 forbids.

Coverage is not lost, for the same reason it was not lost for the other three: there are no
third-party dependencies. Reinstate it with a new id alongside `C-TECH-020`–`022` when the Phase 3
Code App introduces a real manifest.

---

## 5. Findings left unprocessed

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| `IMP-0085` | `no-assertion-on-shipped-content` | Table auditing has no representation in solution source; unchanged from three prior reviews | The next Dataverse table is built (Phase 3, tasks 6.4 / 8.1) |
| `IMP-0112` | `platform-contract-guessed-not-groundtruthed` | Gate applied and firing; the instance fix restructures a flow that has never run live | Before the WordPress integration is connected to DEV |

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 145 | 146 (one new finding: the `powershell_params` single-line edge case carried forward from review 3's residual) |
| `NEW` entries | 3 | 2, both deferred with a reason and a revisit condition |
| Recurring classes (x≥2) | 19 | 19 — `exit-zero-does-not-mean-created` moves x12 → x13 |
| Constraints, active | 46 | 45 after retiring `C-TECH-023`; no new row |

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-21-improvement-review-4.md

Findings processed: 3 NEW  →  1 cluster (1 processed, 2 restated as deferred)
Regression check:   4 prior changes audited, 0 classes recurred (1 proven working in anger)
Proposed:           0 constraints (cap 3) — 1 amended, 2 gates/scripts, 1 knowledge edit,
                    1 config edit, 1 retirement
Altitude calls:     1 generalised from instance to class, 0 left as notes
Digest:             will regenerate — 146 lessons, 19 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

### What needs your decision

**The probe writes to the environment it checks. Is that acceptable in production?**

It creates one `rev_application` row, waits, and deletes it in a `finally`. The alternative —
never proving production's triggers — is how this defect reached TST/ACC. My recommendation is
yes, with the canary clearly marked and the delete path covered by its own test; but a write to
production is your call, not mine.

**Who opens the TST/ACC flow in the designer?**

No fix in this review makes the flow fire. That needs a human with Power Automate maker access to
REV-GrantApplications-ACC to open `REV | Scoring | Calculate & Flag` and save it. Until then
Emily's walkthrough stays blocked, and the probe will report the block rather than removing it.

---

## 8. Applied

**`APPROVE IMPROVEMENTS` received 2026-08-21. PARTIALLY APPLIED, 2026-08-21** — 2 of this
review's 5 proposals plus its retirement are on disk; 3 are not, and are carried on the finding
itself rather than left implicit. Every row below was verified by reading the target file, not by
reading this document (`IMP-0140`).

This review reached its gate at 15:25 and nothing was applied for six hours. Reviews 5 and 6 then
carried all five proposals forward unchanged, so the applied state of this document is the applied
state of review 5 items 1–4 and 10.

| # | Change | State | Evidence |
|---|---|---|---|
| 1 | `provisioning/dataverse/verify-flow-trigger.ps1` — the canary probe | **NOT APPLIED** | The file does not exist. Carried on `IMP-0148`, whose `evidence_grep` now asserts its absence mechanically |
| 2 | Probe wired into `smoke_tests` for `tst_acc` / `prd` / `dev` | **NOT APPLIED** | Depends on item 1 |
| 3 | Probe row in [seed-test-data.ps1](../../provisioning/dataverse/seed-test-data.ps1) | **NOT APPLIED** | Depends on item 1 |
| 4 | [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) `Verify By` amended | **APPLIED** | Clauses (a) metadata-is-not-evidence, (b) Resubmit-is-a-replay and (c) column-security MEMBERSHIP are all in the row. `IMP-0151` closed on clause (b) |
| 5 | Ladder table in `knowledge/technology/testing-tools.md` | **NOT APPLIED** | Instruction-only; carried on `IMP-0148` |
| — | Retire [C-TECH-023](../../constraints/technology/technology-constraints.md#L63) | **APPLIED** | Struck through in place, with a `retired_reason`, plus a row in the Retired Constraints table |

**The human remedy this review asked for has happened.** Its open question — who opens
`REV | Scoring | Calculate & Flag` in the designer — was answered by the reviewer on 2026-08-21:
already done, and the trigger fires. Nothing in the repo recorded it, which is `IMP-0171`. The
probe at item 1 is still the only thing that would prove it again after the next import.
