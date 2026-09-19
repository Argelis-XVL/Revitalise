# Improvement Review — 2026-09-19 (1)

**Status:** ~~AWAITING — nothing in section 3 has been applied. Those changes land only on
`APPROVE IMPROVEMENTS`. Section 0 records one thing that has already been measured and one finding
that has already been appended, because both are capture obligations rather than changes.~~
**APPLIED IN FULL 2026-09-19**, approved by Anna Southern as written. See section 9 — including the
one thing the keyword did not settle, `IMP-0777`, which remains open by design.

**Agent:** improvement-agent (tier `strategic`)
**Trigger:** two unread `rework`/`friction` entries (`IMP-0775`, `IMP-0776`), routed now rather than
batched because `verify-improvement-log.py --check` warns that leaving `IMP-0775` unprocessed fails
the next build's `unit-tests` step.
**Scope:** the two `unread` entries. 167 `reviewer-deferred` and 0 `awaiting-approval` entries were
excluded by activation step 2 and are accounted for in section 6.
**Gate:** `APPROVE IMPROVEMENTS` — section 9 is empty and stays empty until the keyword arrives.

---

## 0. The suite is not green today, and it has nothing to do with either finding

`IMP-0776` records the fix for `IMP-0775` as *"Full suite now passes: 1034/1034 (1 skipped),
confirmed by re-running, not read."* That claim was true when it was written, at 21:15 on
2026-09-18. It re-ran here, in full, and it is no longer true:

```
$ pwsh -NoProfile -File src/tests/Invoke-Tests.ps1
Tests completed in 169.62s
Tests Passed: 1033, Failed: 1, Skipped: 1, Inconclusive: 0, NotRun: 0
```

**The failing test is not one of the eleven `IMP-0775` reported.** All ten fixture-cascade tests and
the `ProvisioningCommon` absent-file test pass. The single failure is:

```
[-] 'verify-pipeline-config' passes against the real config, with every exception still reported
    at $errors.Count | Should -Be 0, src/tests/build/BuildGates.Tests.ps1:993
    Expected 0, but got 16.
```

Running the gate itself explains it in one line, sixteen times over:

```
$ python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml
ERROR: provisioning/deploymentSettings/test-settings.json: _unresolved entry for
  'entra.appRegistrations[2]…resourceAccess[0].id' EXPIRED on 2026-09-18
  (owner: Xander Lykopoulos). Re-date it with a reason or resolve the key.
… (14 entries across test-settings.json and prd-settings.json, plus 2 rolled-up
    "undeclared placeholder" errors that are the same keys counted a second time)
PIPELINE CONFIG PREFLIGHT: FAILED — 16 problem(s) across 116 step(s)
```

Fourteen `_unresolved` declarations in
[`test-settings.json`](../../provisioning/deploymentSettings/test-settings.json#L54) and
[`prd-settings.json`](../../provisioning/deploymentSettings/prd-settings.json#L53) carry
`"expires": "2026-09-18"`. They were green yesterday and are red today, purely because a day
passed. Every other `_unresolved` entry in those two files is dated 2026-11-27 or 2026-12-11 and is
unaffected.

**The gate is not defective — this is the control working.** Each expired entry names its owner, the
exact read-only Graph call that resolves it, and why the value was deliberately not written from
memory. What the expiry did is convert a decision that was owned into a build failure, at the
moment it was supposed to.

**What follows for the dispatch that sent me here:** processing `IMP-0775` does not make the next
build green. The next build fails at `unit-tests` (HARD) on this instead, and only the owner can
clear it — by resolving the seven lookups per environment, or by re-dating the declarations with a
reason. Logged as **`IMP-0777`**, severity `blocker`, owner Xander Lykopoulos. It is reported here
and **not** discharged: I cannot re-date another owner's deferral, and an agent writing a
`deferred_reason` to clear its own build is the failure `verify-improvement-log.py`'s own warning
text names.

**Appending it adds no halt that does not already exist.** `unit-tests` is red on the config state
regardless of what the log says.

### One option considered and rejected, so the next review need not re-derive it

A pre-expiry warning band in `verify-pipeline-config.py` — *"this declaration expires in 3 days"* —
would turn the cliff into a ramp. **Rejected.** It would have to be SOFT to avoid failing a build on
a date that has not arrived, and this project has already measured what happens to SOFT findings:
they land in an aggregate nobody reads (`IMP-0657`, `IMP-0665`, recorded in
`agents/improvement-agent.md`'s closing checklist). A warning nobody reads is not a remedy, and it
would cost a gate edit to install one.

---

## 1. Regression check — did the last reviews' changes work?

| Prior change | Review | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| The closing checklist gains the data-file validator (`agents/improvement-agent.md`) | [5](2026-09-18-improvement-review-5.md) | `closing-checklist-omits-the-data-file-validator` | **No instance.** This review is its first consumer: it edits `logs/improvement-log.jsonl` and runs `verify-improvement-log.py` rather than the generator | Working; exercised, see section 6 |
| `narrowed_by` validated + shape defect named (`scripts/verify-class-defences.py`) | [5](2026-09-18-improvement-review-5.md) | `prose-appended-to-a-field-a-validator-parses-as-a-literal` | **No instance.** This review writes no `class-defences.json` row | Untested here |
| The field-shape section states the rule, not a list (`agents/improvement-agent.md`) | [5](2026-09-18-improvement-review-5.md) | same | **No instance** — but it was consulted: the two `evidence_grep` needles in section 3 were `grep -c`'d to 1 before being written | Working |
| **Reusing a recurring-class name inherits its defence claim** (`skills/how-to-log-an-improvement.md`) | [4](2026-09-18-improvement-review-4.md) | `scope-tag-does-not-imply-content-clean` / class mis-reuse | **RECURRED ONCE — see below** | Wrong shape for the common case; change 2 |

### The one recurrence, dated precisely, because the dates decide the verdict

Both findings in this review carry `class_instance_of: gate-reassures-wrongly`, and section 2
establishes that neither belongs there. The clause that should have prevented it landed in the
engine at **2026-09-18 20:26:47** (`e606351`, *"improvement-agent: reusing a recurring-class name
inherits its defence claim"*).

| Entry | Logged | Clause existed? | Verdict |
|---|---|---|---|
| `IMP-0775` | 2026-09-18 **18:58** | **No** — 88 minutes before the clause | Not a recurrence. Nothing was in force to follow |
| `IMP-0776` | 2026-09-18 **21:15** | **Yes** — 48 minutes after the clause | **A recurrence, of a prose fix, within an hour** |

The ladder says a recurrence after a prose fix is evidence of wrong altitude and should escalate to
a gate. **It does not, here, and the reason is a measurement rather than a preference:** a gate
would have to decide whether a finding's mechanism matches a class name's meaning, and a gate
reading prose for semantics is the shape this repository has measured at 48–100% false, five times
across three reviews (`IMP-0422`, `IMP-0428`).

**But the clause is also not innocent, and this is the part worth fixing.** Its instruction is
*"read the cell before reusing the name"* — the `Defended by` cell in
`logs/known-failure-modes.md`. Measured:

```
$ python3 -c "…distinct class_instance_of values in logs/improvement-log.jsonl…"
distinct class_instance_of names: 170
$ python3 -c "…len(json.load(open('logs/class-defences.json'))['defences'])…"
defence rows: 4
```

**4 of 170 class names have a cell to read — 2.4%.** `gate-reassures-wrongly` is one of the 166
that do not. An author following the clause literally finds `—`, nothing to compare their mechanism
against, and no instruction covering what to do next. The clause is written for the rare case and
silent on the common one. That is change 2: one sentence, same clause, no new mechanism.

### Closure-evidence audit

Both entries closed by this review are `observable_at` V2 and are closed on a full execution of
`src/tests/Invoke-Tests.ps1` — the exact command whose failure produced `IMP-0775`. That is
re-observation at the level the defect was visible at. The `reobserved.result` strings record the
1033/1/1 run honestly, including the unrelated failure, rather than the 1034/0/1 the finding claims.

---

## 2. Clusters and promotion decisions — the class audit

The dispatch asked whether `IMP-0775`'s `gate-defect` / `gate-reassures-wrongly` tags are a genuine
instance. They are not, and neither are `IMP-0776`'s. Both were read against the property the class
is named for.

### 2.1 What `gate-reassures-wrongly` actually means

Its 35 members were listed and their `why_it_was_never_caught` fields read. The property every
genuine member shares: **a check, a runner or a report emitted a signal that reassured — `PASS`,
`OK`, a green run, a count — while the thing it appeared to assure was untrue.** Representative:

| Member | The false reassurance |
|---|---|
| `IMP-0147` | A preflight asserted the file existed; nothing read its contents |
| `IMP-0369` | The digest generator accepted entries the validator rejects, so running it reassured |
| `IMP-0452` | The gate is its own check, and it reported `OK` |
| `IMP-0770` | A class-defence row claimed a property the gate does not actually defend |

**And the class already has a recorded exclusion, decided the same way.** `IMP-0599` is the one
`REJECTED` member of these 35, and its `why_it_was_never_caught` reads *"not applicable — the gate
caught this correctly and is working as designed"*. That is the precedent this audit follows.

### 2.2 `IMP-0775` — the gate fired, correctly, and halted the build

`unit-tests` (HARD, `C-TECH-014`) **failed**, at step 78 of 83, on the first run that executed the
fixture-swap test and the nine tests downstream of it together. Nothing was reassured; a build was
stopped. Under the property above, this is not an instance, and under `IMP-0599`'s precedent it is
the same non-instance for the same reason.

The mechanism `IMP-0775` actually describes: **a state mutation on shared fixture state was placed
outside the `try` whose `finally` restores it, so one predictable throw skipped the restore and nine
later, unrelated tests failed with a message naming the missing fixture rather than the true cause.**
The cost of the mis-tag was not a false defence claim — `gate-reassures-wrongly` has no `Defended
by` cell — but count inflation of an `x33` class, which is one of the inputs the digest's
recurring-class table uses to decide what gets generalised.

```
CLUSTER: skipped-cleanup-misattributes-later-failures  (x1: IMP-0775)
Altitude:   INSTANCE — one occurrence, one file, and the general property already has a home
Ladder row: "one instance, but the cause is general and a human needs to know it"
Becomes:    a retag (change 3) and the lesson it already carries in the digest. NOT a gate
Retires:    nothing
Cites:      IMP-0775
Residual:   the fixed code still mutates state outside its own try — section 5, routed
```

**Why no gate, stated rather than assumed.** An AST check over `src/tests/` could assert that a
fixture-creating call paired with a restoring `finally` sits inside the `try`. The corpus is ~30
`New-SettingsFixture` call sites in four files, of which **one** is a swap-and-restore. A gate
built on a one-member corpus is a gate whose precision cannot be measured, which is exactly what
`agents/improvement-agent.md`'s corpus rule forbids shipping. The altitude rule also does not apply:
this is a first instance, not a second.

### 2.3 `IMP-0776` — an existing class already names it, exactly

`IMP-0776`'s own `root_cause` reads: *"IMP-0775 was logged from a build-agent's static read of the
two files, without running them against the real repo state."* That is
**`finding-diagnosis-unverified`** verbatim — an existing class at `x32`, with no defence cell and
none possible.

```
CLUSTER: finding-diagnosis-unverified  (x33 after this retag: IMP-0776 joins 32)
Altitude:   CLASS — but the class's remedy already exists, in two places, and one of them worked
Ladder row: "an agent had the information and still did the wrong thing" → skill edit
Becomes:    change 1 (one clause, sharpening the existing rule) + change 3 (the retag)
Retires:    nothing
Cites:      IMP-0776, IMP-0775, IMP-0426, IMP-0255
Residual:   no gate can read a proposed_change's prose, and none reasonably could. Accepted
```

**The dispatch asked whether this lesson needs anything durable. Mostly it already has one, and it
worked.** `skills/how-to-log-an-improvement.md` lines 301–325 already say:

> **`root_cause` and `proposed_change` are a HYPOTHESIS, not a specification.** … **If you are the
> agent acting on a finding, re-verify both against source before building either.**

That is exactly what `development-agent` did. It ran the proposed reorder, watched the dev-only test
still fail, found the real constraint, fixed it properly, and filed a `corrects` entry. **Cost: 0.**
This is the loop working as designed, and it is worth saying so plainly rather than treating a
correction as a defect.

**One gap is real, and it is narrow.** The clause tells the acting agent to re-verify, and both
commands it offers are `grep`:

```bash
grep -rn "<the thing the finding says source never declares>" src/    # is the claim true?
grep -rln "<the check the finding proposes>" scripts/                 # does the gate exist?
```

Its worked example (`IMP-0255`) is a grep case too. **Here, both greps would have passed.**
`New-SettingsFixture -Env dev` exists, the `try/finally` exists, the statement order is visibly
wrong — the finding's reading was correct as far as reading goes. What could only be learned by
executing is that the call throws *unconditionally*, so the reorder fixes the cascade and not the
test. The rule that covers this — *where the assertion is about behaviour, execute it; re-reading
the source is what produces the confident wrong answer* (`IMP-0426`) — is written in
`agents/improvement-agent.md` step 8, and binds **improvement-agent only**. The agent this clause
addresses is a delivery agent, who never reads that file. That is change 1.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` · `script` ·
> `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | skill | `skills/how-to-log-an-improvement.md` **(`.engine` submodule)** | a behavioural claim is re-verified by RUNNING it, not by the two greps above | IMP-0776, IMP-0775, IMP-0426 | NO — instruction | N/A |
| 2 | skill | `skills/how-to-log-an-improvement.md` **(`.engine` submodule)** | class reuse asserts a property match even where there is no `Defended by` cell — the 97.6% case | IMP-0776, IMP-0769 | NO — instruction | N/A |
| 3 | other | `logs/improvement-log.jsonl` | retag IMP-0775 and IMP-0776 out of `gate-reassures-wrongly` | IMP-0775, IMP-0776 | YES — `verify-improvement-log.py --check` | N/A |
| 4 | other | `logs/improvement-log.jsonl` | close IMP-0775 and IMP-0776 `APPLIED`, with `evidence_grep` and `reobserved` | — | YES — same | N/A |

**0 new constraints** (cap 3). **0 gates/scripts.** **2 skill edits.** 0 agent-file edits. 0
retirements. `IMP-0777` stays open and is routed, not proposed as a change.

### Change 1 — the re-verification of a behavioural claim is an execution

Appended to the `root_cause`/`proposed_change` hypothesis clause, after the two `grep` commands:

> **Where the claim is about BEHAVIOUR, the re-verification is running it.** *"This call throws"*,
> *"this check does not fire"*, *"moving this line fixes it"* — a grep confirms the code is shaped
> the way the finding says, which is a different question and is usually true. Run the failing
> command, apply the proposed fix, and run it again.
>
> `IMP-0775` proposed moving a fixture-creating call inside its own `try`. Both greps above pass on
> that finding: the call is there, the `try/finally` is there, the order is visibly wrong. Executing
> it is what showed the call throws **unconditionally** against a file this repository permanently
> tracks — so the reorder prevents the cascade and leaves the test itself still failing
> (`IMP-0776`). Reading produces the confident wrong answer; only the run separates *"mis-ordered"*
> from *"never going to work"*.

Zero client literals: the paragraph names no table, environment, cmdlet or file of this client's.
Engine-level under `skills/how-to-promote-a-finding.md` §6 — strip the instance and a true statement
remains.

### Change 2 — the class-reuse clause covers the case it is silent on

Appended to the clause added by review 4:

> **And where the cell is `—`, the assertion is the same one.** 4 of 170 class names carry a
> recorded defence (measured 2026-09-19), so the ordinary case is a class with nothing to read.
> That is not permission — reuse still asserts that your mechanism is the one the class is named
> for. Read two or three of the class's existing members and compare their mechanism to yours, not
> their surface. A gate firing correctly and a gate reassuring wrongly are both *"something went
> wrong at a gate"* and have nothing else in common (`IMP-0775`, filed under
> `gate-reassures-wrongly` for a build the gate correctly stopped).

### Change 3 — the retags

| Entry | Field | From | To |
|---|---|---|---|
| IMP-0775 | `class` | `gate-defect` | `test-defect` (existing value, x6) |
| IMP-0775 | `class_instance_of` | `gate-reassures-wrongly` | `skipped-cleanup-misattributes-later-failures` (new, x1) |
| IMP-0776 | `class_instance_of` | `gate-reassures-wrongly` | `finding-diagnosis-unverified` (existing, x32 → x33) |

`IMP-0776`'s `class` stays `gate-defect`: it is the coarse field, and the entry records a defect in
two test files. A new class name is being coined once, for `IMP-0775`, because no existing name
carries the property; `skills/how-to-log-an-improvement.md` warns against near-duplicate names, and
the 170 existing names were scanned for a fit before coining it.

### Change 4 — closure

| Entry | `evidence_grep` | `reobserved` |
|---|---|---|
| IMP-0775 | `src/tests/provisioning/DataverseScripts.Tests.ps1` contains `regardless of which branch throws (IMP-0775)` — `grep -c` = 1 | V2, full `Invoke-Tests.ps1` run, 2026-09-19 |
| IMP-0776 | `src/tests/provisioning/ProvisioningCommon.Tests.ps1` contains `Get-ProvisioningSettings -Env acc` — `grep -c` = 1 | V2, same run |

Both needles were `grep -c`'d to exactly 1 before being written into the entries, per the one-line
needle rule.

### The disposition was simulated before this draft was parked, and it caught two things

The proposed statuses and fields were applied to a scratch copy of the log and the gate run against
it, per `agents/improvement-agent.md` step 8. The real file was restored and confirmed
byte-identical with `diff`. Two results, neither of which reading would have produced:

**1. The first draft of `IMP-0776`'s closure was rejected.**

```
ERROR: IMP-0776: proposed_change.target names 2 paths and the closure accounts for only 1.
       Unaccounted: src/tests/provisioning/DataverseScripts.Tests.ps1.
```

`IMP-0776`'s `proposed_change.target` names both test files; a needle can only point at one.
`applied_by` now names both explicitly, and the re-run simulation exits 0.

**2. Closing both entries does not make the log gate green, and the reason is `IMP-0777`.**

| Disposition | `verify-improvement-log.py --check` | The build |
|---|---|---|
| Close IMP-0775 + IMP-0776, leave `IMP-0777` open | **exit 1** — blocker trigger, plus a warning that `IMP-0777` was "left behind" by a review whose keyword was given | red at `improvement-log-check` **and** at `unit-tests` |
| The same, plus a reviewer-accepted `deferred_reason` + `revisit_when` on `IMP-0777` | **exit 0** (measured) | still red at `unit-tests` — the settings files are unchanged |
| The owner resolves or re-dates the 14 declarations, then `IMP-0777` closes on evidence | exit 0 | green |

**Only the third row actually unblocks anything**, which is why section 0 routes `IMP-0777` to its
owner rather than proposing a deferral. A deferral here would remove a second report of a failure
that is still happening — the shape `verify-improvement-log.py`'s own warning text warns about.
**This is a decision for the reviewer, and it is the one open question in this review.**

---

## 4. Retirements

**Checked, none found.** 85 live constraint rows and 10 retired, derived rather than typed:

```bash
grep -rh '^| C-'   constraints/ --include='*.md' | wc -l   # 85
grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l   # 10
```

This review adds no constraint, so there is no instance-level rule for a general one to supersede.

One candidate was considered and rejected: **the two `grep` commands in the hypothesis clause**,
which change 1 could have replaced with *"run it"* rather than added to. Rejected — the greps are
right for the case they were written for (`IMP-0255`, a claim about what source declares), and
change 1 splits the clause by what settles the claim rather than replacing one instrument with
another.

---

## 5. Routed work — for another agent, not for this review

| # | Item | Owner | Why not here |
|---|---|---|---|
| R1 | **`IMP-0777` — 14 expired `_unresolved` declarations in `test-settings.json` and `prd-settings.json`.** The next build fails at `unit-tests` on this. Remedy: resolve the seven lookups per environment with the read-only Graph calls each declaration names, or re-date with a reason | Xander Lykopoulos (named as `owner` in every one of the 14) | Live-environment state. The pipeline-config boundary in `agents/improvement-agent.md` puts this on the "hand it over, never widen this row" side |
| R2 | `src/tests/provisioning/DataverseScripts.Tests.ps1` lines 606–609: the applied fix still mutates shared state **outside** its own `try`. `Remove-SettingsFixture` (606) deletes the `acc` fixture and `Move-Item` (608) moves the real file, both before `try` at 610. A throw from the `Move-Item` reproduces `IMP-0775`'s exact cascade, narrowed from certainty to one statement. The `finally` is idempotent — `Remove-SettingsFixture` swallows a missing file and the restore is `Test-Path`-guarded — so both lines move inside the `try` with no other change | development-agent, next time that file is open | Delivery work in `src/tests/`, not an improvement-agent edit. Deliberately **not** logged as a finding: it is a residual I measured, not a defect that has occurred, and speculative entries are what `skills/how-to-promote-a-finding.md` §4 excludes |

Both rows were measured during this review, not carried in from an earlier one.

---

## 6. Findings left unprocessed

State counts are as `verify-improvement-log.py --check` reported them **at activation**, before this
review stamped anything:

- **0 `awaiting-approval`** at activation. There are 3 now — `IMP-0775`, `IMP-0776` and `IMP-0777`,
  all stamped `reviewed_in` by this document at draft time, per step 6.
- **167 `reviewer-deferred`**, left untouched per activation step 2, each carrying a
  reviewer-accepted `deferred_reason`. One (`IMP-0274`) names no `revisit_when` and has been
  reported as such for some time — unchanged here.
- **0 `already-fixed`. 0 `approved-not-applied`.**
- **`IMP-0777`** — appended by this review, left `NEW`, severity `blocker`, owner named. Reported in
  section 0 and routed in section 5. Not discharged, because only its owner can discharge it.
- Seven pre-existing `corrects` warnings (`IMP-0290`, `IMP-0298`, `IMP-0320`, `IMP-0430`,
  `IMP-0437`, `IMP-0703`, `IMP-0763`). Checked individually: none names an entry this review acts
  on. The eighth, `IMP-0775`-corrected-by-`IMP-0776`, is the one this review clears.

---

## 7. Digest impact

**Already measured**, because appending `IMP-0777` is a capture obligation and the capture contract
regenerates the digest at the moment of the append:

- The digest went from **716 to 717 lines** on that regeneration. The registered `CURRENT SIZE`
  claim in `generate-known-failure-modes.py` drifted as a direct consequence, exactly as the
  closing checklist predicts, and has been corrected in **both** copies —
  `scripts/generate-known-failure-modes.py` and its byte-identical `.engine/scripts/` twin.
  `verify-derived-counts.py` now reports `OK — 10 registered claim(s)`, having reported
  `1 drifted claim(s)` before the correction.

Predicted for the retags, on approval:

- `gate-reassures-wrongly` drops from **x35 to x33** in the log and loses `IMP-0775` from the
  recurring-class table's example ids.
- `finding-diagnosis-unverified` rises to **x33**.
- `skipped-cleanup-misattributes-later-failures` reaches **x1** and therefore renders no
  recurring-class row; its lesson still reaches the per-finding digest lines.

### The data-file rule, exercised

This review's only data edits are to `logs/improvement-log.jsonl`. The gate that validates it is
`verify-improvement-log.py`, not the generator that renders it — review 5's change 1, applied here
for the first time. Run in that order, validator first, after every append and stamp.

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-19-improvement-review.md

Findings processed: 2 unread  →  2 clusters
Regression check:   4 prior changes audited, 1 class recurred (prose fix, 48 min; held at prose —
                    reason measured, section 1)
Proposed:           0 constraints (cap 3), 0 gates/scripts, 2 skill/knowledge edits,
                    0 agent-file edits, 0 retirements
Altitude calls:     0 generalised from instance to class, 2 retagged out of a class they never
                    belonged to, 1 left as an instance note
Digest:             regenerated at capture time — 716 → 717 lines; 2 lessons retagged on approval,
                    2 recurring classes affected

IMPROVEMENT LOG: 1 entry appended — IMP-0777  |  digest regenerated: YES

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

**One decision is requested with the keyword**, and it is section 3's simulation table: `IMP-0777`
is a `blocker` this review cannot discharge. Either its owner resolves or re-dates the fourteen
declarations — the only path that makes a build green — or the keyword carries an instruction to
record a `deferred_reason`, which silences the log gate and changes nothing else.

---

## 9. Applied — 2026-09-19

Approved by Anna Southern: *"apply as written (retag IMP-0775/IMP-0776, both skill edits)."*
**No deviation from section 3.** All four changes landed as drafted; nothing was narrowed and
nothing was withheld.

| # | Target | Landed |
|---|---|---|
| 1 | `skills/how-to-log-an-improvement.md` (`.engine`) | the hypothesis clause gains *"where the claim is about BEHAVIOUR, the re-verification is running it, not either grep above"*, with `IMP-0775`/`IMP-0776` as the worked example |
| 2 | `skills/how-to-log-an-improvement.md` (`.engine`) | the class-reuse clause gains the `—` case: 4 of 170 names carry a defence cell, and finding nothing is not permission |
| 3 | `logs/improvement-log.jsonl` | `IMP-0775` → `class: test-defect`, `class_instance_of: skipped-cleanup-misattributes-later-failures`; `IMP-0776` → `class_instance_of: finding-diagnosis-unverified` |
| 4 | `logs/improvement-log.jsonl` | both closed `APPLIED` with `evidence_grep` and `reobserved` |

### Two things withheld inside change 3, named rather than left implicit

`IMP-0775`'s `applied_by` records that **neither of its own proposed fixes was applied**:

- *"move the two lines inside the try"* — **disproved** by `IMP-0776`, which ran it and watched the
  dev-only test fail anyway.
- *"add a harness-level safeguard so `New-SettingsFixture` never accepts `-Env dev`"` — **withheld**,
  because the shipped fix legitimately uses `-Env dev` around a backup and restore. Installing that
  safeguard now would fail the corrected code.

The entry is `APPLIED` on the fix that was actually made, not on the fix it proposed, and says so.

### Measured after regeneration — two predictions, one of which was wrong

| Prediction (section 7) | Measured | |
|---|---|---|
| `gate-reassures-wrongly` drops to x33 | **raw log count 33, digest renders x32** | The digest's recurring-class table excludes the `REJECTED` member (`IMP-0599`); the raw `class_instance_of` count does not. The prediction was counting the wrong population |
| `finding-diagnosis-unverified` rises to x33 | **x33, raw and rendered** | Correct |
| `skipped-cleanup-misattributes-later-failures` at x1, no recurring-class row | **x1, no row; lesson present in the digest and the appendix** | Correct |

Digest 717 → **718 lines**; the registered `CURRENT SIZE` claim drifted a second time on this
regeneration and was corrected again in both copies. `verify-derived-counts.py` OK across 10 claims.

**The wrong prediction was itself logged, as `IMP-0778`** (`friction`,
`two-invocation-paths-disagree`, no change proposed). Two counts of one class over one file disagree
by one wherever that class has ever had a finding rejected, and neither the digest nor the
re-derivation says which population it is counting. Recorded so the next review to notice the
difference does not read it as drift and go hunting for a defect.

### Verification run

```
python3 scripts/verify-improvement-log.py              → exit 0  (774 entries, 168 NEW, 599 APPLIED, 7 REJECTED)
python3 scripts/verify-improvement-log.py --check      → exit 1  (IMP-0777 blocker only — see below)
python3 scripts/generate-known-failure-modes.py --check → exit 0
python3 scripts/verify-derived-counts.py               → exit 0
python3 scripts/verify-review-document.py --only …     → exit 0
python3 scripts/verify-doc-line-links.py …             → exit 0
```

### `IMP-0777` is still open, and the keyword did not change that

The approval said *"apply as written"*, and as written this review routes `IMP-0777` to its owner
rather than deferring it. So the log gate remains at **exit 1**, with the warning that `IMP-0777`
was left behind by a review whose keyword was given. That is accurate and it is the honest state:
the fourteen declarations are still expired, `verify-pipeline-config.py` still exits 1 with 14
`EXPIRED` errors (re-measured at apply time), and `unit-tests` is red on that regardless of what the
log says. The disposition table in section 3 is unchanged and still describes the three ways out.

### Not committed

The working tree carries these changes and **nothing has been committed or pushed**, in either
repository. Changes 1 and 2 are in the `.engine` submodule and publishing them is the three-step
order in `agents/improvement-agent.md` — push the submodule first, verify with
`git -C .engine branch -r --contains HEAD`, then commit the pointer bump here. A clean
`git status` would prove nothing about whether that happened.
