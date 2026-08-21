# Improvement Review — 2026-08-21 (second review this date)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 15 `NEW` → 6 clusters (12 applied, 3 deferred)
**Trigger:** two `blocker`-severity entries appended (IMP-0112 carried, IMP-0137 new) + reviewer's `APPROVE IMPROVEMENTS`
**Gate:** `APPROVE IMPROVEMENTS` — received before this document was drafted; applied, then written up, per the reviewer's explicit instruction in this session. Every change below was verified (build gates, Pester suite, a live comparison against DEV) before being marked `APPLIED` in the log.

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| `scripts/verify-flow-definition-language.py` (checks 1–3: select()/filter(), alt-key Row ID, nested item on UpdateRecord) | 2026-08-21, 11:22 review | `platform-contract-guessed-not-groundtruthed` | Class recurred (IMP-0128, IMP-0137) but **neither is the same property** the gate checks — a column Format/Length mismatch and an `InitializeVariable` nesting rule. The gate itself ran correctly against the still-unfixed IMP-0112 shape in every gate run this session. | **Working, not broken.** This is the umbrella class covering many distinct mechanical properties; the correct response — taken this session — is to add a numbered check to the SAME script (check 4), not to escalate a working gate or write a new script. |
| `verify-shipped-content.py` check 4 (card-payload drift, IMP-0131) | 2026-08-21, 11:22 review | `no-assertion-on-shipped-content` | Class recurred (IMP-0127, IMP-0139) | **Working — and the same script pattern held.** Two more checks (5, 7) added to the same script this session, consistent with its own "ONE GATE, NOT THREE" docstring rule. |
| `skills/how-to-write-a-test-plan.md` update (IMP-0111, `test-asserts-the-defect`) | Claimed applied, 2026-08-21 11:22 review | `test-asserts-the-defect` | **Recurred (IMP-0138) — and the claim was false.** The file exists at 102 lines; it never carried the rule the log said it did. | **Wrong altitude — worse than that, unevidenced.** See cluster 5 and `IMP-0140`: a status of `APPLIED` was reconciled against the file's existence, not its content. Fixed this session — the rule is now actually written, generalised to cover both instances. |
| `scripts/verify-improvement-log.py` C-TECH-061 (≥10 `NEW` / unprocessed blocker gate) | 2026-08-17 | `gate-cannot-fail` (learning loop's own trigger enforcement) | Did not recur as a gate defect — it correctly fired at the top of this session (12 `NEW`, 1 unprocessed blocker) and is the reason this review ran now rather than later | **Working.** |

**Changes whose class recurred after a *prose* fix:** IMP-0111's skill update — escalated properly this time; the content is now written and verified present by grep, not merely claimed (see `IMP-0140`).
**Changes whose class recurred after a *gate*:** none — both gate recurrences (above) are new properties within a broad class, not the same property slipping through, so no `gate-cannot-fail` finding was warranted for either.

---

## 2. Clusters and promotion decisions

```
CLUSTER: platform-contract-guessed-not-groundtruthed  (x2 NEW this session: IMP-0128, IMP-0137 — class now x18)
Altitude:   CLASS — two more distinct platform-contract properties within an 18-instance umbrella
Ladder row: "a tool could catch it mechanically" — extend the existing multi-check gate
Becomes:    scripts/verify-flow-definition-language.py check 4 (InitializeVariable top-level-only,
            all 4 flows, 2 new selftest cases) for IMP-0137; scripts/verify-shipped-content.py
            check 6 (long-text column Format=textarea, threshold derived from the real schema's
            own split at 250 chars) for IMP-0128, in preference to the knowledge-file note both
            findings originally proposed — the ladder prefers the more mechanical home available.
Retires:    nothing
Cites:      IMP-0128, IMP-0137
Residual:   the umbrella class will keep recurring by nature — each new instance is a genuinely
            different platform rule. The pattern that generalises (one script, numbered checks,
            per rule) is now established across two scripts; a THIRD occurrence of the SAME
            specific rule (not just the same umbrella class) is what would demand escalation.
```

```
CLUSTER: no-assertion-on-shipped-content  (x2 NEW this session: IMP-0127, IMP-0139 — class now x10)
Altitude:   CLASS
Ladder row: "a tool could catch it mechanically" — extend the existing multi-check gate
Becomes:    scripts/verify-shipped-content.py check 5 (multi-line cell auto="true") for IMP-0127;
            check 7 (shipped prose promising a re-run a create-only flow cannot perform, scoped to
            skip the action's own `description` field) for IMP-0139. The IMP-0139 instance itself
            — the card, its email twin and the rev_scorebreakdown text — was reworded to name only
            the FR-018 override path, per the reviewer's "Yes, re-word for now."
Retires:    nothing
Cites:      IMP-0127, IMP-0139
Residual:   check 7's verb list ("re-run", "resubmit") is a named set, not a general
            capability-resolution engine — a differently-worded promise of an unbuilt mechanism
            would not be caught. Documented in the check's own docstring rather than silently
            narrowed.
```

```
CLUSTER: test-asserts-the-defect  (x1 NEW this session: IMP-0138 — class now x2, with IMP-0111)
Altitude:   CLASS — second instance, and the first instance's fix turned out not to exist
Ladder row: "second instance of the same class.class_instance_of → generalise, instance patches
            forbidden" + the discovery that IMP-0111's APPLIED claim was unevidenced
Becomes:    src/tests/solutions/ScoringInvariants.Tests.ps1's ordering assertion corrected
            in-session (the edge now hangs off Score_each_wellbeing_answer, not a declaration);
            skills/how-to-write-a-test-plan.md gains a real section covering BOTH instances — the
            platform-contract rule IMP-0111 stated and the ordering-assertion rule IMP-0138 adds —
            with the shared failure mode named explicitly (asserting an assumption vs. a property)
Retires:    nothing
Cites:      IMP-0111, IMP-0138
Residual:   a written rule is a prose fix, per the ladder's own ranking below a mechanical gate —
            there is no proposed mechanical check for "does this assertion pin to an assumption",
            because that judgement is not yet mechanisable here. Flagged, not silently accepted.
```

```
CLUSTER: applied-status-unevidenced  (x1 NEW: IMP-0140 — new class, first instance)
Altitude:   INSTANCE — one occurrence; per the ladder, one instance with a general cause a human
            needs to know becomes a knowledge/log note, not yet a gate
Becomes:    IMP-0111's status corrected in this pass (it is no longer misleadingly APPLIED-and-hollow
            — the content now genuinely exists); the general rule recorded as this cluster's own
            lesson in the log so a future improvement-agent session checks a claimed fix's CONTENT,
            not its file's existence, before marking APPLIED
Retires:    nothing
Cites:      IMP-0140
Residual:   left NEW / deferred (see §5) — the proposed mechanical gate (an `evidence_grep` field
            on `verify-improvement-log.py`, a HARD C-TECH-061 script wired into CI) is real scope,
            not something to fold into an already-large session unreviewed
```

```
CLUSTER: platform-state-divergence  (x1 NEW: IMP-0136 — class now x2, with IMP-0084/related)
Altitude:   CLASS — the digest already carried a contradictory pair of prose claims ("every flow"
            vs "2 of 4") for this environment behaviour and nothing had reconciled them
Ladder row: "a tool could catch it mechanically" — a diff beats two unreconciled prose claims
Becomes:    provisioning/dataverse/reconcile-flow-statecodes.ps1 (new script, Capture/Diff modes),
            wired into config/revitalise-grant-automation-pipeline.yml's tst_acc and prd pre_deploy
            (Capture) and post_deploy (Diff, deliberately LAST among scripted steps so a
            deactivation-driven non-zero exit does not block role/security/setting provisioning
            that ran before it). 5 Pester tests reproduce the real 2026-08-21 2-of-4 shape.
Retires:    nothing
Cites:      IMP-0136
Residual:   not wired into DEV's stage in ci.yml, because DEV is imported by hand-scripted bash
            (`stage-dev`) that calls no pipeline-config step at all — documented in the script's
            own header rather than silently assumed covered. Available for a pipeline-agent or a
            human to run by hand around a manual DEV import, which is the actual DEV workflow
            today (IMP-0133's protocol).
```

```
CLUSTER: gate-reassures-wrongly + gate-cannot-fail + output-shape-defeats-the-reader + harness-blocks-destructive-call
         (x1 NEW each: IMP-0134, IMP-0141, IMP-0142, IMP-0133 — classes now x5, x19, x7, x4)
Altitude:   mixed — see below
Becomes:
  - IMP-0134 (gate-reassures-wrongly): src/tests/Invoke-Tests.ps1 — the coverage runner no longer
    prints "threshold met (C-TECH-014)" when it is not deciding (-CoverageThreshold retired to 0
    as the default). Found in the SAME edit: the FAILED branch had the identical `Write-Output
    (...) + string` precedence bug (splits the message, leaves a `{0}` unsubstituted) — fixed
    for both branches, and generalised as IMP-0142 below.
  - IMP-0141 (gate-cannot-fail): two known-bad fixtures for verify-shipped-content.py's checks 3
    and 4 existed with README instructions and NO wired Pester test — and the label fixture was
    itself incomplete (missing an AppModules/AppModule.xml, so even a manual run per its own
    README would have failed at an earlier, unrelated check). Both completed and wired; 5 more
    tests added for the 3 new checks this session.
  - IMP-0142 (output-shape-defeats-the-reader): the `-f`/`+` PowerShell precedence trap that
    caused IMP-0134's bug documented in knowledge/technology/coding-standards.md with the
    correct pattern, so the next multi-line formatted Write-Output does not repeat it.
  - IMP-0133 (harness-blocks-destructive-call): no change — first recurrence since the protocol
    was written, and it held (REVIEWER ACTION REQUIRED was emitted correctly). Carried forward
    as this review's regression-check evidence for that class.
Retires:    nothing
Cites:      IMP-0133, IMP-0134, IMP-0141, IMP-0142
Residual:   none of these four extend further — each is either a completed fix or a confirmed
            hold.
```

```
CLUSTER: test-coupled-to-absolute-counts  (x0 NEW this session; IMP-0005/IMP-0039 carried forward
         from the 2026-08-20 review, deferred four times, "decision now due")
Altitude:   CLASS — second instance already established (IMP-0039), decision explicitly deferred
            pending this write-up rather than another instance patch
Ladder row: "second instance → generalise" + "prefer the most mechanical home available" (here:
            an invariant, or a source-derived count, over a literal — but NOT a blanket
            retrofit, which IMP-0039 itself warned would be "wrong about 30 of [45 sites]")
Becomes:    knowledge/technology/coding-standards.md — the discrimination rule: a count describing
            the real solution source is fragile and must be derived or replaced with a
            count-free invariant; a count describing a test fixture's own data is stable and
            stays a literal. Cites the concrete tell (source path vs fixture path) and the two
            preferred replacements, in order (count-free Compare-Object invariant, then a
            source-derived count), with the existing EnsureSchema.Tests.ps1 secured-column
            cross-reference as the worked example.
Retires:    nothing
Cites:      IMP-0005, IMP-0039
Residual:   the ~45-site inventory itself is NOT retrofitted in this review — that is real
            implementation work for whoever next touches src/tests/, applied site-by-site as
            ordinary maintenance rather than a wholesale migration behind this gate. Named
            explicitly rather than silently left as if the decision closed the work too.
```

---

## 3. Proposed changes

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | build-gate | `scripts/verify-flow-definition-language.py` | check 4: no `InitializeVariable` below the top level; no Set/Increment/AppendToStringVariable naming an undeclared variable | IMP-0137 | YES — `python3 scripts/verify-flow-definition-language.py --selftest` (8/8), and clean against `src/solutions/RevitaliseGrantAutomation` |
| 2 | build-gate | `scripts/verify-shipped-content.py` | checks 5–7: multi-line cell `auto="true"`; long-text column `Format=textarea` (threshold 250, derived from source); shipped prose promising a re-run a create-only flow cannot perform | IMP-0127, IMP-0128, IMP-0139 | YES — 3 new known-bad fixtures + 7 new/fixed negative tests in `BuildGates.Tests.ps1`, all failing for the stated reason; clean against the real solution |
| 3 | script (new) | `provisioning/dataverse/reconcile-flow-statecodes.ps1` | Capture/Diff modes for cloud-flow statecodes around an import | IMP-0136 | YES — 5 Pester tests in `DataverseScripts.Tests.ps1`, reproducing the real 2-of-4 deactivation shape |
| 4 | config | `config/revitalise-grant-automation-pipeline.yml` | wire the script above into `tst_acc`/`prd` pre_deploy (Capture) and post_deploy (Diff, last) | IMP-0136 | YES — `python3 scripts/verify-pipeline-config.py` PASS |
| 5 | knowledge | `knowledge/technology/coding-standards.md` | discrimination rule for count-coupled Pester assertions | IMP-0005, IMP-0039 | N/A — a rule for future authoring judgement, not itself executable |
| 6 | knowledge | `knowledge/technology/coding-standards.md` | the `-f`/`+` PowerShell precedence trap, with the correct pattern | IMP-0142 | N/A — instruction |
| 7 | skill | `skills/how-to-write-a-test-plan.md` | real section covering both `test-asserts-the-defect` instances | IMP-0111, IMP-0138 | N/A — instruction |
| 8 | test | `src/tests/build/BuildGates.Tests.ps1` | wire the 2 orphaned checks + 5 new ones; complete the label fixture's missing `AppModule.xml` | IMP-0141 | YES — all pass, all proven able to fail |
| 9 | source fix | `src/tests/Invoke-Tests.ps1` | retire the coverage-threshold default to 0; correct the `-f`/`+` bug in both branches | IMP-0134, IMP-0142 | YES — both branches printed and verified by direct invocation |
| 10 | source fix | `REVScoringCalculateAndFlag-...json` (flow + notes.md) | lift both `InitializeVariable` actions to the top level; reword the withheld-outcome card/email/column text | IMP-0137, IMP-0139 | YES — matches the live DEV definition exactly (0 diff, 50/50 actions); all gates clean |
| 11 | test | `src/tests/solutions/ScoringInvariants.Tests.ps1` | correct the ordering assertion; add 2 assertions proven able to fail | IMP-0137, IMP-0138 | YES — 92/92 pass; proven to fail by re-nesting the action |

**Constraint budget:** 0 of 3 used. No new constraint ROW was needed — every mechanical fix this
review extended an existing gate SCRIPT (the preferred, more mechanical home per the ladder),
which is why the constraint count stays at zero.

---

## 4. Retirements

Retirement check performed: no constraint was reviewed as a retirement candidate this session
— every change extended a script or a knowledge file, not a constraint row, so there was nothing
in `constraints/` this review's changes made redundant.

---

## 5. Findings left unprocessed

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| `IMP-0085` | `no-assertion-on-shipped-content` | Table-level auditing has no representation in solution source and no dev-environment route exists yet to script it — carried from the 2026-08-20 review unchanged | The next Dataverse table is built (Phase 3, tasks 6.4/8.1) |
| `IMP-0112` | `platform-contract-guessed-not-groundtruthed` | The GATE is applied (check 2 of `verify-flow-definition-language.py` names all six occurrences on every build, confirmed still firing this session); the INSTANCE FIX — restructuring six chained `Get-a-row-by-id` actions into one `List rows` + `Filter array` per value — touches a flow that has never run live, and doing that untested inside this review would be worse than leaving it named and red | Before Alex's WordPress integration is connected to DEV — the first live submission is when this fails |
| `IMP-0140` | `applied-status-unevidenced` | The finding is real and the specific instance it names (`IMP-0111`) is corrected this session; the proposed GATE (an `evidence_grep` field on `verify-improvement-log.py`, a HARD C-TECH-061 script wired into CI) is real scope needing its own reviewed change | The next improvement review, or the next time an `APPLIED` claim is found unevidenced |

---

## 6. Digest impact

| | Before this review | After |
|---|---|---|
| Log entries | 136 | 139 |
| Distinct lessons | 136 | 139 |
| Recurring classes (x≥2) | 18 | 19 |
| `NEW` entries | 12 | 3 (all deferred with a recorded reason) |
| Digest lines | 381 | 385 |

Regenerated with `python3 scripts/generate-known-failure-modes.py`; confirmed current with
`--check`.

---

## 7. Verification

- Full Pester suite: **809 passed, 0 failed, 1 skipped** (`pwsh -NoProfile -File src/tests/Invoke-Tests.ps1`)
- `verify-build-config.py`, `verify-pipeline-config.py`: **PASS**
- `verify-flow-definition-language.py --selftest`: **8/8**, including 2 new cases proven to fail for the stated reason
- `verify-shipped-content.py` against the real solution: **OK**, all 7 checks clean
- `verify-improvement-log.py --check`: **OK** — 3 `NEW`, all deferred with a recorded reason; 0 unprocessed blockers
- `generate-known-failure-modes.py --check`: **current**
- Live comparison: `REVScoringCalculateAndFlag`'s corrected definition matches the DEV
  environment's live definition **exactly** — 50/50 actions, 0 structural differences —
  confirmed by direct `pac env fetch` query against `REV-GrantApplications-DEV`

**Not verified in this review:** `reconcile-flow-statecodes.ps1` was proven against a mocked
Dataverse Web API (5 Pester tests reproducing the real 2-of-4 shape), not against a live import
— this environment has no app-only certificate available to exercise it end to end. `IMP-0112`'s
instance fix remains unbuilt and untested, as recorded above.
