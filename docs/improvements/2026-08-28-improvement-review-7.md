# Improvement Review 37 — 2026-08-28

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 6 `unread` → 5 clusters
**Trigger:** two unread `blocker` entries — [`IMP-0434`](../../logs/improvement-log.jsonl) and
[`IMP-0435`](../../logs/improvement-log.jsonl)
([`agents/WORKFLOW.md` L280](../../agents/WORKFLOW.md#L280), *"immediately — do not batch"*).
**Gate:** `APPROVE IMPROVEMENTS` — ~~nothing in this document is on disk~~ **APPROVED 2026-08-28 by
Xander Lykopoulos and APPLIED in full; §9 carries the record and the one deviation. All gates green;
the build is clear.**
**Scope:** the 4 dispatched entries `IMP-0434`–`IMP-0437`, plus 2 this review appended itself:
[`IMP-0438`](../../logs/improvement-log.jsonl) (found by measuring change 1 before wiring it) and
[`IMP-0439`](../../logs/improvement-log.jsonl) (found by auditing review 36 in §1). The
`reviewer-deferred` entries are untouched per activation step 2
([`improvement-agent.md` L103](../../agents/improvement-agent.md#L103)), and so are the **5** now
at `awaiting-approval` — `IMP-0440`–`IMP-0444`, every one stamped
`reviewed_in: docs/improvements/2026-08-28-improvement-review-6.md`. They need a keyword sent
against that document, not a second review here.
**Concurrency — it moved the ground under three of this document's sections, twice.**
[Review 36](2026-08-28-improvement-review-6.md) was parked at its gate when this dispatch opened
and **was approved and applied while this review was being written**: both its new gates are on
disk, the `verify-*.py` count moved 48 → 50, its 10 entries closed, and it appended the 5 findings
above. Its own header still reads *"nothing in this document is on disk"*, which is stale but not
this review's to edit. Everything below is measured against the tree **after** that landing, and
activation step 8 re-measures again before anything here is applied
([`IMP-0405`](../../logs/improvement-log.jsonl), [`IMP-0080`](../../logs/improvement-log.jsonl)).
Checked at the last re-measurement: none of the 5 carries `corrects` naming anything this review
acts on.
**Numbering:** 36 → 37, following review 36's own note that review 35 mis-titles itself as *"5"*.
**WBS:** the four dispatched findings carry `wbs:6.9`; `IMP-0439` carries none and none is
invented. The review itself is `system` work, never billable
([`C-COM-002`](../../constraints/commercial/commercial-constraints.md#L35)). No contracted figure
is restated (D-3).

---

## Summary

**Seven changes, no new rules — the constraint budget is untouched at 0 of 3.** Every cluster
resolved to a script, a helper, or a knowledge line, because in four of the five cases a mechanism
already existed and stopped one step short of the defect.

**The most urgent item is not one of the four findings dispatched: the next build will halt at step
4 of 72.** Review 36's new `provisioning-test-presence` gate is correct, its three findings are
all true, and it is wired at
[`build.yml` L183](../../config/revitalise-grant-automation-build.yml#L183) where a non-zero exit
stops the build — measured this dispatch, it exits **1**. That is
[`IMP-0439`](../../logs/improvement-log.jsonl), and change 7 is the unblock.

**Measuring the new gate before wiring it found a second live instance of the defect it was
written for.** A shipped `<Description>` says `rev_status` is *"written by nothing and read by
nothing"*;
[`seed-round-statistics-request.ps1` L105](../../provisioning/dataverse/seed-round-statistics-request.ps1#L105)
writes it. Which artefact is wrong is WBS 6.9 delivery work, so it is logged as
[`IMP-0438`](../../logs/improvement-log.jsonl) and put to the reviewer in §7, not patched here.

**Three proposals measured wrong and were narrowed or discarded before reaching this page.** One
would have blinded this review's own new gate; one would have shipped a 67%-false-positive regex;
one was a duplicate of a gate that landed mid-draft. §6 carries every measurement.

---

## 1. Regression check — did the last applied reviews' changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [`scripts/lib/tracked_paths.py`](../../scripts/lib/tracked_paths.py#L96) + the lock [`verify-gate-input-tracking.py`](../../scripts/verify-gate-input-tracking.py) — review [34](2026-08-28-improvement-review-4.md), for `IMP-0410` | 2026-08-28 | `gate-scope-mismatch` | **YES** — `IMP-0437`, same day | **Working for the direction it covers, structurally blind to this one.** See below |
| The string-form `proposed_change` fixture in [`verify-improvement-log.py`](../../scripts/verify-improvement-log.py) — review [35](2026-08-28-improvement-review-5.md), for `IMP-0423` | 2026-08-28 | `gate-cannot-fail` | **NO** | **Working.** `--check` reaches a verdict over all 441 entries with no traceback |
| [`scripts/verify-provisioning-test-presence.py`](../../scripts/verify-provisioning-test-presence.py) + the step at [`build.yml` L183](../../config/revitalise-grant-automation-build.yml#L183) — review [36](2026-08-28-improvement-review-6.md), for `IMP-0433` | 2026-08-28, mid-draft | `declared-policy-not-mechanically-enforced` | **NO in that class — YES in a new one** | **Working, and it stops the build.** Exit 1 over three pre-existing scripts. That is `IMP-0439`, change 7 |

The four audit questions, answered for the `gate-scope-mismatch` recurrence:

- **Was the change prose or a mechanical gate?** A gate, and a shared helper behind it. No higher
  altitude is available — this is already the most mechanical home.
- **Did the gate run?** **Yes, and it passed.** `python3 scripts/verify-gate-input-tracking.py`
  exits 0: *"24 resolvable gate input(s) examined, none ignored by the repository."* It did not
  fire on
  [`verify-forms-and-views-reachable.py`](../../scripts/verify-forms-and-views-reachable.py#L55)
  for two reasons, and it reports the second itself — it asks only whether an input is
  **ignored**, never whether it is **untracked**, and *"84 glob call(s) whose pattern or base this
  gate cannot resolve statically"* sit outside its reach. The forms gate composes its pattern at
  runtime, so it is one of the 84.
- **So is this `gate-cannot-fail`?** No, and the distinction is worth keeping. That class is a
  gate reporting a clean bill it cannot support; this one prints *"This is a coverage gap, not a
  clean bill"* on every run. It is mis-scoped and says so, which is why change 3 widens the
  helper rather than replacing the lock.
- **Did the closure evidence match the level the defect was visible at?** Yes. `IMP-0410` is V1
  and was closed on source evidence plus a materialised reproduction.

**And the one thing this audit establishes about the system, not about a gate:** review 36's own
change table recorded change 6 as proven — *"`--selftest` (4 checks) then the corpus run: 3
findings, all true"* — and every word of that is accurate. It is still the change that stops the
next build, because *"the gate is correct"* and *"the build is green"* are two questions and
nothing asked the second. `IMP-0439` is that finding.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: a shipped <Description>'s claim about WRITERS is prose nothing checks
           (x2: IMP-0434, IMP-0438 — class no-assertion-on-shipped-content, now x18)
Altitude:  CLASS. Two instances, three days apart, in one feature — and the second was found by
           measuring the gate the first proposed, before it was wired. The ladder would normally
           send a one-member "why_it_was_never_caught: nothing" finding to a knowledge line and
           make it wait; it did not have to wait.
Ladder row: "a tool could catch it mechanically" → a script plus a build gate
Becomes:   (1) scripts/verify-superseded-column-writers.py. Proposed SOFT; the reviewer decided
           HARD (§7, §9) and it is wired HARD. Turns the sentence
           "Written by nothing" into a checkable claim about provisioning/**/*.ps1 and
           Workflows/*.json.
Retires:   nothing — this class had no gate at all; it was undefended
Cites:     IMP-0434, IMP-0438, and IMP-0008 for the older half of the same property
Residual:  co-occurrence within one FILE, not one statement. A script that legitimately
           references the old entity set and, separately, a superseded column in live code would
           be a false positive. None exists today (§6a); statement-level attribution needs a
           PowerShell parser, which is not a one-second gate. The READ half of the same claim
           ("read by nothing") has no gate and one instance — deliberately not proposed.
```

```
CLUSTER B: the Web API OMITS a null column, and StrictMode turns that into a throw
           (IMP-0435 — class platform-contract-guessed-not-groundtruthed, x49)
Altitude:  INSTANCE, deliberately, and the x49 does not change it. This class's general mechanism
           exists and works — skills/how-to-verify-a-platform-contract.md is what the digest
           routes 41 of its 49 members through. Each member is a NEW platform fact; the general
           fix is the habit of ground-truthing, not another gate.
Ladder row: "one instance, but the cause is general and a human needs to know it" → knowledge/
Becomes:   (2) knowledge/technology/dataverse.md — a new section stating the omission, the
           StrictMode interaction, the required guard idiom, and the rule that a test fake must
           OMIT the property rather than set it to $null.
Retires:   nothing
Cites:     IMP-0435
Residual:  a gate for this was designed and DISCARDED on measurement — 6 candidate sites, 2 true,
           4 false (§6b). Separating "this variable holds an API response" from "this variable is
           a locally built request body" needs dataflow analysis. The knowledge line is the honest
           altitude; the mocked test in DataverseScripts.Tests.ps1 is the real guard.
```

```
CLUSTER C: a per-file test-presence gate — LANDED mid-draft, and needs one narrowing
           (IMP-0436 — class declared-policy-not-mechanically-enforced, x20)
Altitude:  NEITHER a new gate nor a deferral. The mechanism this finding asks for is review 36's
           change 6, which was parked when this dispatch opened and is now on disk. Building a
           second gate for one property is the duplication the anti-bloat limits exist to
           prevent, so this review does not.
Becomes:   (6) one narrowing to the landed gate: a mention inside the CONVENTION suite does not
           count as coverage evidence. Measured (§6c): that admits exactly the substitution
           IMP-0433 recorded as invalid, and excluding it adds a fourth true positive with no
           false positive.
Retires:   nothing
Cites:     IMP-0436, IMP-0433, IMP-0443
Residual:  "named by a test" is still not "exercised by a test". The aggregate coverage threshold
           remains the only instrument that measures lines, which is why §4 declines to retire it.
Note:      review 36 reached the duplication finding independently and recorded it as IMP-0443 —
           two dispatches designed one gate within the hour because a parked review is invisible
           to the log. That entry is review 36's and is not re-derived here; it is cited because
           it is the durable record of why this cluster builds nothing.
```

```
CLUSTER D: a gate's verdict depends on UNTRACKED working-tree files  (IMP-0437 — class
           gate-scope-mismatch, x9; second in the git-input sub-family after IMP-0410)
Altitude:  CLASS for the helper, INSTANCE for the adoption — and the finding's own literal
           proposal is WITHHELD. It asks that every glob-driven gate resolve its inputs through
           `git ls-files`. Measured, that would drop 5 files from this repository's gate inputs,
           2 of them whole entity directories, and would leave the CLUSTER A gate with ZERO
           inputs, because the only three "UNUSED FROM REVISION" markers live in an untracked
           Entity.xml (§6d).
Ladder row: "second instance of the same class → generalise", applied to the PROPERTY rather than
           to the finding's wording: a gate reads either the working tree or the commit, and which
           one it reads must be declared and REPORTED, not implicit.
Becomes:   (3) scripts/lib/tracked_paths.py gains untracked_paths()/describe_untracked() and
           states the two-universes rule where the next gate author reads it; (4)
           verify-forms-and-views-reachable.py NAMES its untracked inputs and gains
           --committed-only to reproduce CI without an rsync copy.
Retires:   nothing. verify-gate-input-tracking.py is NOT retired — it locks the ignored direction
           and is this review's own regression evidence (§1).
Cites:     IMP-0437, IMP-0410
Residual:  opt-in, exactly as the ignored direction is. Nothing forces a new gate to report its
           untracked inputs, and the meta-lock cannot reach 84 of 108 glob calls because their
           patterns are composed at runtime. Note the corroboration: the dispatch applying review
           36 folded this same lesson into its own gate's summary line unprompted, in the
           report-do-not-narrow direction this cluster chose.
```

```
CLUSTER E: a HARD gate switched on in the same change that first measured it red
           (IMP-0439 — new class, x1)
Altitude:  INSTANCE plus a read-path fix, and NOT a constraint. The ladder forbids a constraint
           row on one instance whose why_it_was_never_caught is "nothing" unless the mechanism is
           a platform law, and this is a process omission, not a platform law.
Ladder row: "a tool could catch it mechanically" for the unblock; "an agent had the information
           and still did the wrong thing" for the prevention
Becomes:   (7) the landed gate gains a declared baseline with known-exceptions.json's semantics —
           owner, clearing action, dated expiry; suppresses the FAIL, never the report; fails on
           an unowned or expired entry — and the three pre-existing scripts are baselined. Plus
           (5)'s docstring half: verify-build-config.py already tells a gate author to measure
           precision before wiring; it does not tell them to read the EXIT CODE against the
           current tree.
Retires:   nothing
Cites:     IMP-0439, and IMP-0320 as the recorded CORRECT handling of the same shape
Residual:  a baseline is a waiver with a date on it. The control is the expiry, and it is only as
           good as someone reading the report — which is why the entries print on every run.
```

---

## 3. Changes proposed

| # | Type | Target | What | Cites | Provable? |
|---|---|---|---|---|---|
| 1 | script + build step | `scripts/verify-superseded-column-writers.py` (**new**) + a **HARD** `superseded-column-writers` step (proposed SOFT, **reviewer decided HARD** — §9) in [build.yml](../../config/revitalise-grant-automation-build.yml#L183), beside `provisioning-test-presence` | Every `<attribute>` whose `<Description>` carries `UNUSED FROM REVISION n` is read from `Entities/*/Entity.xml` with its entity set name; any `provisioning/**/*.ps1` or `Workflows/*.json` referencing both **outside comments** is a finding | IMP-0434, IMP-0438, IMP-0008 | YES — `--selftest`, then the corpus run: **1 finding, 1 true, 0 false** after one narrowing (§6a) |
| 2 | knowledge | [`knowledge/technology/dataverse.md`](../../knowledge/technology/dataverse.md#L269) — a new section after *"Reading Metadata Through the Web API"* | A null-valued column is OMITTED from a response body, not returned as null; under `Set-StrictMode -Version Latest` a bare read of it is a **terminating** error. The `PSObject.Properties.Name -contains` guard is the required idiom, and a test fake must OMIT the property | IMP-0435 | Partly — the guard is on disk at [`seed-round-statistics-test-data.ps1` L231](../../provisioning/dataverse/seed-round-statistics-test-data.ps1#L231); the live re-observation is unavailable (§5) |
| 3 | script | [`scripts/lib/tracked_paths.py`](../../scripts/lib/tracked_paths.py#L96) | `untracked_paths()` and `describe_untracked()` beside the existing ignored-path pair, plus the two-universes rule in the module docstring: an authoring-time gate reads the working tree and MUST NOT adopt a tracked-only rule; a gate whose count is transcribed as a claim about delivered source reports the split | IMP-0437, IMP-0410 | YES — `python3 scripts/lib/tracked_paths.py` selftest, 6 cases → 8 |
| 4 | script | [`scripts/verify-forms-and-views-reachable.py`](../../scripts/verify-forms-and-views-reachable.py#L55) | The summary line names every untracked input, so a warning COUNT cannot be transcribed without seeing it is working-tree-specific; `--committed-only` reproduces CI's verdict | IMP-0437 | YES — bare run reports 12 warnings **and** 5 untracked inputs; `--committed-only` reports 14 |
| 5 | script docstring | [`scripts/verify-build-config.py`](../../scripts/verify-build-config.py) | One paragraph beside the existing measure-precision-first obligation: before wiring a gate as a blocking step, run it against the current tree and read the **exit code**. A correct gate that is red is still a halted build, and pre-existing debt is not the introducing dispatch's to fix | IMP-0439, IMP-0320 | Prose. No gate — see §6e for why |
| 6 | script | [`scripts/verify-provisioning-test-presence.py`](../../scripts/verify-provisioning-test-presence.py#L75) | A mention inside a **convention suite** does not count as coverage evidence. Excludes `ScriptContract.Tests.ps1`, which discovers scripts by [`Get-ChildItem -Recurse`](../../src/tests/provisioning/ScriptContract.Tests.ps1#L24) and asserts shape, never behaviour | IMP-0436, IMP-0433 | YES — corpus run: 3 findings → **4 findings, 4 true, 0 false** (§6c) |
| 7 | script + config | [`scripts/verify-provisioning-test-presence.py`](../../scripts/verify-provisioning-test-presence.py) + a baseline block | A declared baseline with [`known-exceptions.json`](../../contract/known-exceptions.json)'s semantics: owner, clearing action, dated expiry; suppresses the FAIL for a named script while still printing the finding; fails on an unowned or expired entry. The three pre-existing scripts are baselined so the gate stops blocking the build | IMP-0439 | YES — the gate exits **0** with the baseline and **1** with any entry removed, which is the can-it-still-fail proof |

**Rows 6 and 7 both edit a script another dispatch landed minutes ago and may still be finishing.**
Both are applied at *this* review's application time, after the keyword, for that reason — not
now.

**The derived `verify-*.py` count is 50 today and becomes 51 with row 1.** It is **not** typed into
[`agents/improvement-agent.md` L332](../../agents/improvement-agent.md#L332) from this page: review
36 moved it 48 → 50 mid-draft, which is exactly why the figure is re-derived at application and
reported by
[`verify-derived-counts.py`](../../scripts/verify-derived-counts.py) if it is skipped.

---

## 4. Retirement — considered, none found

Checked, and both candidates were rejected for cause:

- **[`C-TECH-014`](../../constraints/technology/technology-constraints.md#L52)** (the aggregate
  coverage threshold). Review 36's per-file gate is a leading indicator for the same policy, so
  retiring the aggregate in its favour is the obvious move. Rejected: a file *named* by a test is
  not a file *exercised* by one, and the aggregate figure is the only thing that notices the
  difference. Complementary coverage, not duplicate.
- **[`verify-gate-input-tracking.py`](../../scripts/verify-gate-input-tracking.py)**, on the
  argument that change 3 widens the helper it locks. Rejected: it is the regression lock for
  `IMP-0410` and this review's own regression evidence (§1). Retiring the lock in the same review
  that records a recurrence in its class would invert the rule.

Derived, not typed: `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` → **10** retired
rows against **80** live ones.

---

## 5. Deferrals — what this review does NOT close, and why

Both blockers dispatched here stay open, and that is the honest outcome rather than a gap.

- **[`IMP-0434`](../../logs/improvement-log.jsonl) stays open, with a reason.** Its
  `observable_at` is **V4** and
  [`C-TECH-053`](../../constraints/technology/technology-constraints.md#L108) is explicit that a
  V4 defect is not closed by a document, a clean build or a zero exit. The delivery half is fixed
  on disk — the seeder now writes `rev_roundstatisticsresults` — and the re-observation cannot be
  made by anyone here: the parent Dev Summary records that the table is **absent from DEV**, so
  there is no environment in which to re-run the reproduction and watch the charts populate.
  `revisit_when`: the round-statistics tables exist in DEV and the seeder is re-run against it.
- **[`IMP-0435`](../../logs/improvement-log.jsonl) stays open, same reason at V5.** The guard is
  on disk and a mocked test reproduces the absence, which is V1/V2 evidence. End-to-end execution
  against a live environment is what `observable_at: V5` demands, and it is not available.
  `revisit_when`: as above.
- **[`IMP-0438`](../../logs/improvement-log.jsonl)** is delivery work and not this review's to
  fix. `revisit_when`: the reviewer answers §7's first question.
- **[`IMP-0436`](../../logs/improvement-log.jsonl), [`IMP-0437`](../../logs/improvement-log.jsonl)
  and [`IMP-0439`](../../logs/improvement-log.jsonl) close** on `APPLIED`. All three are
  `observable_at: n/a` or V1, changes 3–7 are their fixes, and `IMP-0437`'s literal proposal is
  recorded as withheld with the measurement that forced it.

---

## 6. Measurements

Every gate here was run against the real corpus, not only its fixtures, and every finding was
adjudicated one at a time.

### 6a — the CLUSTER A gate: 1 finding, 1 true, 0 false

The first implementation stripped only line comments (`#` to end of line). Measured **3 findings,
1 true, 2 false** across 38 candidate files — 67% wrong on first contact.

One narrowing, and it removes both false positives **by name**: also strip PowerShell **block**
comments (`<# … #>`). Both false positives were the strings `rev_resultjson` and `rev_computedon`
at line 24 of
[`seed-round-statistics-request.ps1`](../../provisioning/dataverse/seed-round-statistics-request.ps1#L24),
inside the `<# .SYNOPSIS #>` header that explains why those two columns are *not* written. Every
`.ps1` in this repository opens with such a header naming the very entity sets and columns the
gate looks for, so this was not a corner case.

Re-measured: **1 finding, 1 true, 0 false.** The survivor is real —
[L105](../../provisioning/dataverse/seed-round-statistics-request.ps1#L105) PATCHes
`rev_status = 2` into `rev_roundstatisticsrequests`, against a shipped `<Description>` at
[`Entity.xml` L92](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_roundstatisticsrequest/Entity.xml#L92)
saying the column is written by nothing.

**And the script's own header is wrong in the other direction**, which is why §7 asks rather than
answers. Its lines 19–24 justify the write as feeding *"the landing screen's first-ever read"*;
the app's own test asserts the opposite —
[`schema.test.ts` L351](../../src/code-apps/trustee-review-portal/src/dataverse/schema.test.ts#L351)
pins `ROUND_STATISTICS_REQUEST_COLUMNS` to exactly `["rev_roundstatisticsrequestid"]` and
[L352](../../src/code-apps/trustee-review-portal/src/dataverse/schema.test.ts#L352) asserts it
contains none of the three superseded columns. So the column is written by something and read by
nothing, and two shipped artefacts each state one half wrongly.

### 6b — the CLUSTER B gate, designed and DISCARDED: 6 candidates, 2 true, 4 false

A regex for a bare property read on a Dataverse response was measured before being proposed: 6
candidate sites across `provisioning/`, of which 2 are the real ones (both already fixed) and 4
are false — 2 are a locally constructed request body in `seed-settings.ps1`, which is not an API
response at all, and 2 read `rev_name`, a primary name column that cannot be null. 67% wrong, and
the remedy needs to know what a variable holds. Discarded in favour of the knowledge line; 12
guarded reads already use the correct idiom.

### 6c — the narrowing the landed gate needs

[`verify-provisioning-test-presence.py`](../../scripts/verify-provisioning-test-presence.py#L75)
accepts *"named by some `*.Tests.ps1`"* as coverage evidence. Its own summary line states the
limitation — *"Being NAMED is not behavioural coverage: a script can be named inside a convention
loop that executes none of it"* — and then counts such a mention anyway.

| Evidence rule | Findings | True | False | Misses, by name |
|---|---|---|---|---|
| any file under `src/tests/` names it | 2 | 2 | 0 | `create-self-signed-cert.ps1`, `verify-environment-access.ps1` |
| any `*.Tests.ps1` names it (**as landed**) | 3 | 3 | 0 | `create-self-signed-cert.ps1` |
| any `*.Tests.ps1` **other than the convention suite** names it | 4 | 4 | 0 | — |

The loosest rule misses two files named only by a README and by two fixture `.yml` files. The
landed rule misses one: `create-self-signed-cert.ps1`, named only by
[`ScriptContract.Tests.ps1`](../../src/tests/provisioning/ScriptContract.Tests.ps1#L24), which
discovers every script by `Get-ChildItem -Recurse` and asserts shape. All four findings of the
strictest rule are true positives, and the escape hatch for a script that should not have a test
already exists.

### 6d — why `IMP-0437`'s literal proposal is withheld

`git ls-files -o --exclude-standard` over the forms gate's input tree returns **5 untracked files,
0 ignored**:

| Untracked input | Effect of a blanket `git ls-files` input rule |
|---|---|
| `rev_roundfinance/FormXml/main/{…}.xml`, `SavedQueries/ActiveRoundFinances.xml`, `SavedQueries/AllRoundFinances.xml` | **This is the defect.** Their presence silences 2 warnings on `rev_roundfinance`: 12 warnings here, 14 in CI |
| `rev_roundstatisticsrequest/Entity.xml`, `rev_roundstatisticsresult/Entity.xml` | **This is why the rule cannot be blanket.** Two whole tables vanish, taking 4 of the 12 current warnings — and taking the only three `UNUSED FROM REVISION` markers in the repository, which are the sole input to change 1. The CLUSTER A gate would have zero inputs |

The same rule applied to the landed `provisioning-test-presence` gate would drop all three
`seed-round-statistics-*.ps1` files, because they are untracked too — the exact scripts
`IMP-0433`, `IMP-0434` and `IMP-0436` are about. The generalisation is real; the wording is not.
Report the split, do not narrow the inputs.

### 6e — why change 5 is prose and gets no gate

The check would be *"every blocking step in `build.yml` exits 0 against the current tree"*, which
is the build itself. Running the whole sequence to preflight the sequence is not a one-second
gate, and a partial version — run only steps added in this commit — needs a commit boundary a
working tree does not have. Stated rather than papered over: change 5 raises the floor by putting
the question where a gate author reads it, and closes nothing.

---

## 7. What you need to decide

**Is the `rev_status` write the defect, or is the shipped `<Description>` the defect?**

Ground truth is settled and it contradicts both artefacts. The column *is* written, by
[`seed-round-statistics-request.ps1` L105](../../provisioning/dataverse/seed-round-statistics-request.ps1#L105),
so *"written by nothing"* is false. The column is *not* read, so the same script's header
rationale about the landing screen is false.

Two routes, and neither is mine: drop `rev_status` from that PATCH body and leave the retained
column genuinely dead, or correct the `<Description>` to *"written once at seed time, read by
nothing"* and fix the header. The first is tidier and touches a one-row DEV/TST seeder; the second
is cheaper and keeps a deliberate default in place. Either way it is WBS 6.9 delivery work under
[`C-COM-002`](../../constraints/commercial/commercial-constraints.md#L35), logged as
[`IMP-0438`](../../logs/improvement-log.jsonl) and routed to `development-agent`. Which route?

**Do you want the build unblocked by a dated baseline, or by three exclusions?**

The next build halts at step 4 over `ensure-document-locations.ps1`,
`verify-access-test-identity.ps1` and `verify-environment-access.ps1`. Change 7 proposes a
baseline carrying an owner, a clearing action and a dated expiry per script — the semantics
[`known-exceptions.json`](../../contract/known-exceptions.json) already uses, where an exception
suppresses the FAIL and never the report.

The alternative is three [`coverage-exclusions.json`](../../config/coverage-exclusions.json)
entries, which is the wrong instrument: that file carves out the line-coverage threshold and
demands a `proven_able_to_fail` per entry, which a script with no tests cannot supply. It also has
`_max_entries: 6` with 4 used, so three more would breach it.

I have assumed you are the owner of all three baseline entries, as you are for every entry in
`known-exceptions.json`, with an expiry of **2026-09-30** — the date `EX-002` uses for work in our
own hands. Confirm the owner and that date, or name others?

**Should the new gate in change 1 be SOFT now and HARD later, or HARD immediately?**

Proposed SOFT, and `IMP-0439` is the argument for it: HARD would halt the same build over §7's
first question, which this review cannot answer. A SOFT step still reports on every run and its
warning is itself gated by
[`C-TECH-055`](../../constraints/technology/technology-constraints.md#L110), so it cannot be
carried silently. Do you want it SOFT with promotion to HARD tied to `IMP-0438` closing?

**DECIDED: HARD, immediately.** Applied as decided. Vindicated within four minutes — the gate is
red on a live regression the delivery fix introduced, which a SOFT step would have reported into a
warning nobody was blocked by. See §9.

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-28-improvement-review-7.md

Findings processed: 6 unread  →  5 clusters
Regression check:   3 prior changes audited, 1 class recurred (+1 new class produced)
Proposed:           0 constraints (cap 3), 6 gates/scripts, 1 skill/knowledge edits,
                    0 agent-file edits, 0 retirements
Altitude calls:     2 generalised from instance to class, 1 left as notes, 1 folded into
                    another review's landed gate
Digest:             REGENERATED for the 2 findings appended here — 441 entries, 440 lessons,
                    39 recurring classes. Will regenerate again at application

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 9. Applied — the record

**Approved 2026-08-28 by Xander Lykopoulos, with the three §7 decisions resolved as:** (1) the
script is the wrong artefact and gets fixed, not the `<Description>`; (2) change 7's baseline,
expiring 2026-09-30, owned by **`lead-agent`** rather than the reviewer personally, on the ground
that an untested provisioning script is a system item and not a delivery one; (3) the new gate
stays **HARD**.

All seven changes are on disk. Re-verified before applying, per activation step 8: no entry
appended after the draft carries `corrects` naming anything this review acts on, and the
`verify-*.py` count was re-derived rather than taken from the draft (48 → 50 by review 36 → **51**
with change 1).

| # | Landed | Proof executed |
|---|---|---|
| 1 | [`scripts/verify-superseded-column-writers.py`](../../scripts/verify-superseded-column-writers.py) + the HARD `superseded-column-writers` step at [`build.yml` L186](../../config/revitalise-grant-automation-build.yml#L186) | `--selftest` **10/10**, including the real defect shape and both measured false-positive shapes. `verify-build-config.py` accepts the step and ran its selftest as part of preflight |
| 2 | [`knowledge/technology/dataverse.md` L294](../../knowledge/technology/dataverse.md#L294), *"Reading DATA Through the Web API — a Null Column Is OMITTED"* | Prose. The guard idiom it prescribes is on disk at [`seed-round-statistics-test-data.ps1` L231](../../provisioning/dataverse/seed-round-statistics-test-data.ps1#L231) |
| 3 | [`scripts/lib/tracked_paths.py`](../../scripts/lib/tracked_paths.py) — `untracked_paths()`, `describe_untracked()`, and the *"TWO INPUT UNIVERSES"* rule | Selftest **6 cases → 11**, all green, including that an ignored file and an untracked file are different answers |
| 4 | [`scripts/verify-forms-and-views-reachable.py`](../../scripts/verify-forms-and-views-reachable.py) — every verdict now carries a scope line and names its untracked inputs; `--committed-only` added | Bare run: 12 warnings, **5 untracked inputs named**. `--committed-only`: **10** warnings across 11 entities |
| 5 | [`scripts/verify-build-config.py`](../../scripts/verify-build-config.py) — *"AND READ THE EXIT CODE BEFORE YOU MAKE THE STEP BLOCKING"* | Prose, deliberately (§6e) |
| 6 | [`scripts/verify-provisioning-test-presence.py`](../../scripts/verify-provisioning-test-presence.py) — `CONVENTION_SUITES` excluded from counting as coverage evidence | Selftest **4 → 7** checks. Corpus: 3 findings → **4, all true, 0 false** |
| 7 | [`scripts/lib/gate_baseline.py`](../../scripts/lib/gate_baseline.py) + [`config/gate-baselines.json`](../../config/gate-baselines.json) | Selftest **11/11**. `verify-provisioning-test-presence.py` now exits **0** with 4 baselined and still printed |

Closed incrementally as each change landed: `IMP-0436`, `IMP-0437` and `IMP-0439` are `APPLIED`.
`IMP-0434` (V4) and `IMP-0435` (V5) are deferred with a reason and a trigger — neither can be
re-observed while the round-statistics tables are absent from DEV, and
[`C-TECH-053`](../../constraints/technology/technology-constraints.md#L108) forbids closing them on
a clean exit. Digest regenerated last and once: **443 entries, 442 lessons**.

### The one deviation, stated because it must not be silent

**The approval named THREE scripts for the baseline and the file carries FOUR.** Change 6 — approved
by the same keyword — stops a convention-suite mention counting as coverage, which moves the gate's
true-positive set from 3 to 4. That measurement is §6c's table and was in front of the reviewer at
approval. The fourth is `create-self-signed-cert.ps1`; without its entry, applying change 6 would
have left the build red, which is the outcome change 7 exists to prevent. Same owner, same expiry,
same class. Recorded here, in `IMP-0439`'s `applied_by`, in the gate output, and in
`config/gate-baselines.json`'s own `_four_not_three` key.

### The gate found a live regression four minutes after it existed — RESOLVED 15:35

This is the most important thing on this page, and it is not one of the four dispatched findings.

The `development-agent` dispatch acting on decision 1 removed `rev_status` from
`seed-round-statistics-request.ps1`'s PATCH body and, in the same edit, **added three more
columns**: `rev_resultjson`, `rev_computedon` and `rev_triggeredon`. Two are the other ADR-038
superseded columns carrying the same *"Written by nothing"* `<Description>`; the third is the flow's
Dataverse **trigger** column, which that file's own header says would *"start a computation during
provisioning"*. Meanwhile the header, the inline comment at line 122 and the `Write-ResourceStatus`
detail were all rewritten to say the body is *"rev_name only"*. **The prose half of the fix landed
and the code half did not.**

Logged as [`IMP-0446`](../../logs/improvement-log.jsonl), a blocker, and **not fixed here** —
delivery source under `wbs:6.9` is not `improvement-agent`'s to edit
([`C-COM-002`](../../constraints/commercial/commercial-constraints.md#L35)).

`superseded-column-writers` went **red** on it, which is the gate working rather than a defect in
it: these were live regressions, not pre-existing debt, so they were deliberately **not** baselined.
`IMP-0439`'s own rule is what says so — a baseline is for debt the introducing dispatch does not own.

**Resolved at 15:35, by the same dispatch, within two minutes of the finding being logged.** The
PATCH body is now `@{ rev_name = $requestKey }` and nothing else, matching what that file's header,
inline comment and status string had been claiming all along. Re-observed at V1 on both axes and
recorded on both entries: the gate exits **0** (3 marked columns across 38 writer candidates, 0
findings), and line 126 was read directly to confirm the `rev_triggeredon` write is gone —
**separately**, because the gate cannot see that one. `IMP-0438` and `IMP-0446` are both `APPLIED`
with a `reobserved` record. **The build is clear.**

**Note what the gate does not cover, because it is why line 126 was read by hand.** The
`rev_triggeredon` write is invisible to it: that column carries no superseded marker. Nothing in
this repository asserts that a flow's trigger column must not be seeded during provisioning, and
that has exactly one instance, so no gate is proposed for it here — it is a knowledge-level fact
recorded in `IMP-0446`'s lesson and it needs a human to check, which is what happened.

**What this sequence is evidence of, and it is the most useful thing on this page.** The gate was
built, measured, and inside forty minutes it caught two distinct instances of its own class in a
file it was written from — one pre-existing (`IMP-0438`) and one introduced by the fix for the
first (`IMP-0446`). Neither would have been seen by `pac solution pack`, Solution Checker, or any
source-vs-source gate here, because every table and every column genuinely exists. That is the
argument for the altitude call in CLUSTER A, made by the corpus rather than by me.
