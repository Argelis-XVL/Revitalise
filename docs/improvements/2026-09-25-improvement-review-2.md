# Improvement Review — 2026-09-25 (2)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 3 `NEW` → 2 clusters
**Trigger:** blocker escalation (two unread blockers from one build failure)
**Gate:** `APPROVE IMPROVEMENTS` — **APPLIED 2026-09-25** (see §8)
**WBS:** `wbs:n/a` — system work on the rules, no contracted task (`C-COM-002`); the incident touched 3.2/3.4 and 6.8/6.10 builds

---

## Summary

The shared build stopped at its last step. The address of the government postcode service had been corrected in the script that loads the council register, but a test's fake copy of that address still used the old one. The test was fixed in a parallel dispatch at 14:08, and I re-ran that test file: 9 of 9 now pass.

Following the existing sweep rule for this review turned up a second leftover copy that nobody had reported. The postcode-watch flow still calls the old address, and a live check today shows that address returns *400 Invalid URL*. I have logged it and am handing it to development-agent. It is not a rule change.

The rule meant to prevent this kind of leftover was written yesterday, and it has now failed once. Turning it into an automatic check measured at **0 correct out of 136 alerts**, so I am not proposing one. I propose one wording change to the rule instead. Your decision is whether to approve that and the two log-record changes.

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [review 2026-09-25 (1)](2026-09-25-improvement-review.md) change 1: pipeline-agent binds every declared post-deploy step | 2026-09-25 | pipeline stage reported done with a step unrun | NO | Working — leave alone |
| same review, change 2: resolve a connector operation's whole parameters block | 2026-09-25 | `platform-contract-guessed-not-groundtruthed` (DocuSign) | NO | Working — leave alone |
| same review, change 3: `npm ci` operating fact | 2026-09-25 | untrusted installed packages | NO | Working — leave alone |
| same review, change 4: bundle figure registered in `derived-counts-registry.json` | 2026-09-25 | `hand-maintained-count-drifts-from-source` | NO | Working — gate-backed |
| [review 2026-09-24 (3)](2026-09-24-improvement-review-3.md) change 2: sweep the WITHDRAWN LITERAL across the whole tree, `src/tests/` first ([skill §4](../../skills/how-to-verify-a-platform-contract.md#L529)) | 2026-09-24 | `test-asserts-the-defect` (fix-time sweep) | **YES — IMP-0888, IMP-0890, ~16 hours later** | **Prose recurred.** Escalation to a gate measured and rejected (Cluster A); reach widened instead |

**Changes whose class recurred after a *prose* fix:** the §4 withdrawn-literal rule. The regression table says escalate to a gate. I measured two candidate gates and neither holds up. The numbers are under Cluster A.
**Changes whose class recurred after a *gate*:** none. The one gate over this class, `unit-tests` ([C-TECH-014](../../constraints/technology/technology-constraints.md#L52)), fired correctly on its first run against the corrected script.

---

## 2. Clusters and promotion decisions

### Cluster A — a corrected address left behind in two other places

```
CLUSTER: test-asserts-the-defect — fix-time sweep mechanism  (x2 this review: IMP-0888, IMP-0890;
         prior instances of the same mechanism: IMP-0871, IMP-0872)
Altitude:   CLASS — third sitting in which a source correction withdrew a value and a second
            referrer kept demanding it
Ladder row: "second instance -> generalise" was already applied (skill §4, 2026-09-24); this is
            "an agent had the information and still did the wrong thing" -> skill edit
Becomes:    skills/how-to-verify-a-platform-contract.md §4 — (1) the rule binds ANY correction of
            a hard-coded value after live evidence, not only a formal register closure;
            (2) sweep the DISTINCTIVE SEGMENT that changed, never only the whole old value;
            (3) the measured no-gate verdict, so the next review does not re-attempt it
Retires:    nothing — no instance gate exists for this class
Cites:      IMP-0888, IMP-0890
Residual:   the rule is still prose, and this incident's author ran no sweep at all. Nothing
            mechanical covers a flow's hard-coded URI: no test asserts it, so IMP-0890's copy
            rots until a live run. The durable fix is one source for the URL, which is an
            architecture call, routed rather than ruled
```

**What happened, measured.** At the last commit (`c62d309`), the ONS address was typed out by hand in three places. [The script default](../../provisioning/dataverse/seed-local-authority-register.ps1#L169), [the watch flow's first action](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVLocalAuthorityRegisterWatch-8F1C2A44-1010-4B7A-9E21-0A1B2C3D4E10.json#L93) and [the Pester fake route](../../src/tests/provisioning/LocalAuthorityRegister.Tests.ps1#L59) all used the same wrong service name, and the tests were written from that wrong name. An uncommitted edit corrected the script and added a settings override. It left the other two copies alone. It also left the [A-LAR-06 register row](../development/postcode-lookup-dev-summary.md#L214) alone, which still says the address is *not re-confirmed live*. No line in `routing.log`, `pipeline.log` or the improvement log records who made the edit.

**Ground truth for the flow copy, measured today with a read-only `curl`.** The old name `ONSPD_Online_Latest_Centroids` returns `{"error":{"code":400,"message":"Invalid URL"}}`. The corrected name returns the `ONSPD_LATEST_UK` layer. So the watch flow's first action fails on every run.

**Why sweeping the whole old value is not enough, measured.** The Pester fake held only a regex *fragment* (`ONSPD_Online_Latest_Centroids/FeatureServer/0\?f=json`), not the full URL. Grepping the full old URL across `src/tests/` at `HEAD` returns **0** hits. Grepping the service name that actually changed returns the test (positive control run). The first search would have found the flow and missed the test that halted the build. That result is change 1's point (2).

**Why no gate — two designs, both measured:**

| Candidate | Measurement | Verdict |
|---|---|---|
| Diff-driven: an identifier removed from code lines and not re-added, still used in code elsewhere | Replayed over all 181 commits: **136 findings, 10 distinct identifiers, 0 true positives**. All ten were refactors: an import moved, an env-var name taken out of one settings file, a YAML key re-dated. Removing a name from one file looks the same as withdrawing a wrong value. It would also have missed the earlier `quickview` instance, because that value has no distinctive token. On today's working tree it finds the flow (1 true positive). | **Rejected on the number** |
| Declared: the author records the withdrawn value in the register row, and a gate sweeps for it | This incident's author edited no register row, so the gate had nothing to read | **Rejected** — it cannot fire on the incident that motivates it |

**The premise in IMP-0888's proposal is partly wrong.** It says eight route registrations needed updating. It was one variable (`$script:LayerRootPattern`), used by all eight tests. The fix intent was right, and it shipped as a one-line diff (file modified 14:08). The routed fix is therefore **WITHHELD as shipped**, not re-dispatched.

**Class label.** IMP-0888 was logged under a new singleton class, `test-fixture-lags-groundtruthed-source-correction`. Its mechanism is the one IMP-0871/IMP-0872 record under `test-asserts-the-defect`. One property split across two names weakens the recurrence signal (`IMP-0330`), so change 2 relabels `class_instance_of` and keeps the agent's own `class` text. The row goes from x4 to x6 (IMP-0890 is already filed under that label).

### Cluster B — the same build failure, logged from the other feature

```
CLUSTER: hard-gate-red-on-pre-existing-debt  (x1 this review: IMP-0889; class x4 in the digest)
Altitude:   INSTANCE — left as a note
Ladder row: none applies; the proposal's premise fails re-measurement
Becomes:    nothing. Proposed change REJECTED with the measurement below
Retires:    nothing
Cites:      IMP-0889
Residual:   one feature's build can still go red on another feature's uncommitted work in this
            shared checkout. That is handled by lead-agent sequencing (routing.log 2026-09-24
            09:15), not by a build-time annotation
```

The trustee-portal build hit the same failing test and logged it from that feature's side. It proposes teaching `run-build.py` to label a HARD failure as *"attributable to uncommitted, out-of-scope work"* when the failing paths lie outside the dispatching feature's scope.

**Measured against this incident, the heuristic gets the wrong answer.** The failing file, `LocalAuthorityRegister.Tests.ps1`, was **clean** at failure time; `git status` listed only the script it tests. The script's edit was not *mid-edit* either. It was a complete, live-confirmed correction, and the unswept test was the only thing missing. Matching failing paths to dirty paths would have pointed at the wrong file and given the wrong reason. The four members of this class also share a name and nothing else: a new gate wired red, a flow exception growing, an unowned plan document, and this one. That is not grounds for a class gate.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | skill | `skills/how-to-verify-a-platform-contract.md` §4 (engine submodule) | One paragraph after the "Do not filter the sweep by extension" paragraph: any correction triggers the sweep; sweep the changed segment; recorded no-gate measurement | IMP-0888, IMP-0890 | N/A — instruction change | N/A |
| 2 | other | `logs/improvement-log.jsonl` | IMP-0888 `class_instance_of` → `test-asserts-the-defect` | IMP-0888 | YES — `python3 scripts/generate-known-failure-modes.py --check`; the class row reads x6 | N/A |

**Constraint budget:** 0 of 3 used.

### Exact wording

**Change 1**, inserted after [skill §4 L547–550](../../skills/how-to-verify-a-platform-contract.md#L547):

> **Sweep the segment that changed, not the whole old value — and any correction triggers it.**
> Added 2026-09-25 (`IMP-0888`, `IMP-0890`). Correcting a hard-coded value after live evidence is a
> closure whether or not anyone opens the register, and this rule binds it. A referrer often holds
> only a *fragment* of the withdrawn value: a test double matching a regex, or a flow building a URL
> from parts. Swept on the full old URL, the ONS base-URL correction finds the flow and misses the
> Pester double that halted the build; swept on the service name that actually changed, it finds
> both. So grep the part that differs between old and new, and treat a clean result on the whole
> value as unproven.
>
> **No gate, and the number is why.** A diff-driven check for a removed identifier still used
> elsewhere was replayed over all 181 commits on 2026-09-25: 136 findings, 0 true positives,
> because a refactor that moves a name out of one file looks the same as a correction that
> withdraws it. A variant that reads author-declared withdrawn values would not have fired on this
> incident, whose author updated no register. Do not re-attempt either without a new discriminator.

The paragraph names no client table, environment or tenant. The ONS example is a public service, and the section already carries a client example (`IntakeContract.Tests.ps1`), so it stays at the engine altitude under skill §6. It commits in `.engine` first: push, then `branch -r --contains HEAD`, then the pointer bump.

**Change 2:** only the `class_instance_of` field of IMP-0888 changes. Every other line of the log stays byte-identical, and the edit is written with `ensure_ascii=False`.

---

## 4. Retirements

> Retirement check performed: 86 live constraint rows, 10 retired (derived with the struck-through-id grep). None is currently redundant because of this review: no constraint targets the fix-time sweep, and the one gate that fired, `C-TECH-014`, is the defence that worked.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0862, IMP-0887

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0862 | `gate-scope-mismatch` | unread non-blocker; one unread blocker must not pull a review of everything around it (`IMP-0183`). Batch threshold not reached (5 unread + awaiting in the queue). `excluded_by` stamped | next batch or reviewer request |
| IMP-0887 | `dispatch-brief-asserts-unverified-fact` | same reason; its own proposal is `none` | same |

**Also not processed:** IMP-0855 is `awaiting-approval` against its own parked document and needs a keyword, not a review. 213 entries are `reviewer-deferred`.

### Dispositions this review proposes (decided by `observable_at`)

| Entry | `observable_at` | Disposition |
|---|---|---|
| IMP-0888 | V1 | **CLOSE → APPLIED.** `applied_by` names change 1 and the shipped one-line test fix; `evidence_grep` is a one-line fragment of change 1. Re-observation (not required at V1): standalone Pester run of `LocalAuthorityRegister.Tests.ps1`, 9 passed / 0 failed, 2026-09-25 |
| IMP-0889 | V1 | **CLOSE → REJECTED**, with `rejected_reason` = the Cluster B measurement. The defect it hit is resolved by the IMP-0888 fix |
| IMP-0890 | V1 | **DEFER** with `deferred_reason` + `revisit_when`: the flow fix is routed below, and the entry closes when the flow's URI stops matching the withdrawn name |

### Routed work

| To | Item | Re-measured at draft |
|---|---|---|
| development-agent (`postcode-lookup`) | Correct `Get_ONSPD_edition_marker`'s `uri` to the corrected ONSPD service name. Update the A-LAR-06 register row with today's live result. Decide, or put to architect-agent, whether the base URL should come from one setting so the three copies cannot drift again | flow L93 still carries the old name; old name 400s live (curl, 2026-09-25) |
| — | IMP-0888's own test fix | **WITHHELD — already shipped** (test L59, 14:08; 9/9 green) |

### Disposition simulation (run before parking)

The three dispositions above were applied to a scratch copy of the log, and the queue gate was run against it with `--log`. It exited **0** with triggers clear: 217 NEW, 660 APPLIED, 9 REJECTED. The real log was confirmed byte-identical afterwards with `diff -q`.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 886 | 886 |
| `test-asserts-the-defect` row | x5 | x6 |
| Singleton class `test-fixture-lags-groundtruthed-source-correction` | 1 | 0 |
| Unread blockers | 2 | 0 |

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-25-improvement-review-2.md

Findings processed: 3 NEW  →  2 clusters
Regression check:   5 prior changes audited, 1 classes recurred
Proposed:           0 constraints (cap 3), 0 gates/scripts, 1 skill/knowledge edits,
                    0 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 1 left as notes
Digest:             will regenerate — 878 lessons, recurring classes unchanged in number
                    (test-asserts-the-defect x5 → x6)

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

Filled in **after** `APPROVE IMPROVEMENTS`, not before.

**Authorised:** `APPROVE IMPROVEMENTS`, from Anna Southern, quoted verbatim ("Approve improvements and approved for build."), relayed by lead-agent on 2026-09-25. The record was written to `logs/routing.log` before any change was made.

**Re-verified before applying (step 8):** no entry appended since the draft; no `corrects` naming IMP-0888/0889/0890; the test fix is still on disk (1 match); the flow still carries the withdrawn name (1 match), so the routed item stands; the skill anchor paragraph is unchanged at L547.

| # | Change | Applied at | Entries moved |
|---|---|---|---|
| 1 | Paragraph "Sweep the segment that changed, not the whole old value" added to skill §4 | `skills/how-to-verify-a-platform-contract.md` (engine submodule, **uncommitted**) — needle grep: 1 match | IMP-0888 → APPLIED |
| 2 | IMP-0888 `class_instance_of` → `test-asserts-the-defect` | `logs/improvement-log.jsonl` — digest row now x6 | (same) |

Entries rejected, with reasons:

| Finding | Rejected because |
|---|---|
| IMP-0889 | The proposal's premise failed re-measurement: the failing test file was clean, and the dirty script held a complete correction. See Cluster B |

**Deferred with reason:** IMP-0890. The flow fix is routed to development-agent (`postcode-lookup`), and `revisit_when` names the grep that closes it.

**Deviation from the gate block:** the digest reports **877** lessons, not the 878 the gate predicted, because the rejected IMP-0889 no longer renders a lesson. No change to what was approved.

**Checks:**
- `verify-improvement-log.py --check`: exit 0, triggers clear.
- `generate-known-failure-modes.py --check`: current.
- `verify-derived-counts.py`: 0.
- `verify-class-defences.py`: 0.
- `verify-engine-instance-split.py`: 0.
- `verify-doc-line-links.py`: 0.

**Not published:** the engine commit, push and pointer bump have not been done. `.engine` already carries uncommitted edits from earlier reviews to the same skill file and four others, so publishing is one decision covering all of them.
