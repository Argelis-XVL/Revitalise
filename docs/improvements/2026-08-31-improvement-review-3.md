# Improvement Review — 2026-08-31 (review 48)

**Agent:** improvement-agent
**Trigger:** unread `blocker` — [`IMP-0521`](../../logs/improvement-log.jsonl), appended 2026-08-31T12:25
**WBS:** 6.9 (the halted build), plus system work that carries no task id
**Status:** **APPLIED 2026-08-31.** `APPROVE IMPROVEMENTS` received; all three changes are on
disk, all three findings are closed or deferred, and the digest is regenerated. §7 is the applied
record. Two figures in the draft were corrected at application time after re-measurement — the
script count in §3 and the whole of §3.2 — and the §5 routed table changed to withhold both rows.

---

## Summary

**The gate for this class already exists, already scopes to the exact line that halted the build,
and printed it 44 steps before the halt — as a warning nobody had to act on.** The finding says
[`verify-source-derived-test-counts.py`](../../scripts/verify-source-derived-test-counts.py)
*"does not scope to Pester It-block literals compared against settings-file key counts."* I ran it.
It does, and it names `DeploymentSettings.Tests.ps1:158` with the correct diagnosis, at build step
25 of 71 ([`build.yml` L504](../../config/revitalise-grant-automation-build.yml#L504)), while
`unit-tests` is step 69 ([L1452](../../config/revitalise-grant-automation-build.yml#L1452)).

So this is not a scope defect. It is the regression-check row that says **a gate that exists and
did not fire is mis-scoped or mis-severitied** ([`improvement-agent.md`
L356](../../agents/improvement-agent.md#L356)) — and the severity is the answer. The gate is SOFT
because it cannot tell a fragile literal from a correct one, which is true of 10 of its 11 current
findings and **false of the one shape where the true value is sitting in a JSON file it can read.**
The change is to make that subset compare values and exit non-zero, per
[`improvement-agent.md` L500](../../agents/improvement-agent.md#L500) — assert on values, not on
phrases, wherever a value exists.

Two script changes, one agent-file line, **zero new constraints**.

---

## 0. Scope, and what I excluded

[`scripts/verify-improvement-log.py`](../../scripts/verify-improvement-log.py) `--check` reports
**107 NEW: 3 unread, 0 awaiting-approval, 104 reviewer-deferred, 0 already-fixed**.

My scope is the **three unread** entries: [`IMP-0521`](../../logs/improvement-log.jsonl) (the
blocker that summoned this dispatch), [`IMP-0519`](../../logs/improvement-log.jsonl) and
[`IMP-0520`](../../logs/improvement-log.jsonl). The dispatch named only `IMP-0521`; the other two
are `unread` and therefore in scope by activation step 2
([`improvement-agent.md` L100](../../agents/improvement-agent.md#L100)). Leaving them would be a
silent cap.

**Excluded: the 104 `reviewer-deferred` entries.** Each carries a `deferred_reason` a human
accepted; none is re-derived here. **No entry is `awaiting-approval`**, so no parked document is
waiting on a keyword.

Five pre-existing `corrects` WARNINGs stand (`IMP-0290`, `IMP-0298`, `IMP-0320`, `IMP-0430`,
`IMP-0437`). None names anything this review touches; all five are left alone.

---

## 1. Regression check — did the last review's changes work?

Audited against [`2026-08-31-improvement-review-2.md`](2026-08-31-improvement-review-2.md)
(review 47), and against **review 19**, which is the review that owns the count-drift class.

| Prior change | Class recurred? | Verdict |
|---|---|---|
| Review 47 change 1 — the dangling `#L448` in the plan document | No | **Worked.** `doc-line-links` is green; this build's halt was at `unit-tests`, not at that gate |
| Review 47 changes 2/3 — step-8 routed-work re-verification prose | Not yet testable | This review is the first to exercise it; §5 records the result |
| Review 19 — [`verify-source-derived-test-counts.py`](../../scripts/verify-source-derived-test-counts.py), the class's general gate | **Yes — 6th and 7th instance** | **Mis-severitied, not mis-scoped.** See below. This is the row that decides the whole review |
| Review 8 (`C-TECH-060`) — [`verify-field-length-limits.py`](../../scripts/verify-field-length-limits.py) | **Yes, from a new direction** | The gate is correct; its **known-bad fixture** silently stopped being bad when the limit it violates was widened |

### The row that matters: the gate ran, and it was ignored

Run just now against the live tree:

```
WARNING: src/tests/provisioning/DeploymentSettings.Tests.ps1:158: asserts a literal count of 15
on `$testKeys.Count`, in an It block that reads solution source (a deployment-settings
'settingRows' array). ...
SOURCE-DERIVED TEST COUNTS: 11 fragile literal(s) of 14 source-coupled assertion(s), out of 107
literal count(s) across 11 test file(s) — SOFT: reported as WARN, never blocking.
```

Exit **0**. The build continued for 44 more steps and then halted at
[`unit-tests`](../../config/revitalise-grant-automation-build.yml#L1452) on that same line.

The gate's own docstring is honest about why it is SOFT
([L59](../../scripts/verify-source-derived-test-counts.py#L59)): it cannot read intent, and
blocking on a literal it cannot adjudicate reproduces `IMP-0212`'s harm. **That reasoning holds for
10 of its 11 findings and collapses for the eleventh**, because
[`provisioning/deploymentSettings/test-settings.json`](../../provisioning/deploymentSettings/test-settings.json)
is a JSON file this gate can open and count: `settingRows` is 16 in `test-settings.json`,
`prd-settings.json` and `dev-scoring-settings.json` alike. `15` matches none of them. That is not
an intent judgement; it is a value comparison.

The finding's own `why_it_was_never_caught` is therefore **wrong**, and I am recording that rather
than inheriting it — this is [`improvement-agent.md` L150](../../agents/improvement-agent.md#L150)'s
execute-it-do-not-read-it rule applied to a finding written by another agent.

---

## 2. Clusters and promotion decisions

```
CLUSTER: hand-maintained-count-drifts-from-source  (x1 new: IMP-0521; class at x7)
Altitude:  CLASS — 7th instance (IMP-0005, IMP-0039, IMP-0120, IMP-0155, IMP-0212, IMP-0518,
           IMP-0521). The class already HAS its general gate, wired at build step 25.
Ladder row: "a tool could catch it mechanically" — but the tool exists, so the promotion is
           SEVERITY, not scope: the subset whose true value is machine-readable becomes HARD.
Becomes:   change 1 (verify-source-derived-test-counts.py, derive-and-compare tier)
         + change 2 (verify-field-length-limits.py, known-bad fixture staleness)
Retires:   nothing — see §4
Cites:     IMP-0521, IMP-0212, IMP-0514
Residual:  The 10 findings the gate cannot compute stay SOFT and stay noisy. Nothing here fixes
           the Get-Rev* reader shapes, which need PowerShell to evaluate. And change 2 covers
           fixtures whose badness is a LENGTH; a known-bad fixture that stops being bad for any
           other reason is still only caught at unit-tests.
```

```
CLUSTER: dispatched-agent-stalls-silently  (x1 new: IMP-0520; class at x7)
Altitude:  CLASS, and the prose fix already failed — WORKFLOW.md's fifth case
           (L151) was cited in this session's own dispatch briefs and the failure recurred
           twice more, at ~500k tokens.
Ladder row: "the ORDER of steps was wrong" — the existing text tells the dispatcher how to
           RECOGNISE the death; it never tells them to PREVENT it when composing the prompt.
Becomes:   change 3 — one paragraph in the fifth case, written as a dispatcher obligation.
Retires:   nothing
Cites:     IMP-0520, IMP-0357, IMP-0299
Residual:  This stays PROSE and I want that on the record, because the ladder says a
           recurrence after prose is evidence of wrong altitude. There is no mechanical home:
           no gate can read a dispatch prompt that exists only inside a live session. What
           change 3 does is move the instruction from the diagnosis section to the composition
           step. If it recurs an eighth time, the honest next rung is a dispatch-prompt
           checklist in agents/lead-agent.md's activation sequence, not another paragraph.
```

```
CLUSTER: gate-blocks-on-unrelated-precondition  (x1 new: IMP-0519)
Altitude:  INSTANCE — one occurrence, cost ~5 minutes, no delivery impact, and the entry
           already names its own return condition.
Ladder row: "one instance, specific, no general mechanism" -> stays a log note.
Becomes:   a deferred_reason. No file changes. See §3.1.
Retires:   nothing
Cites:     IMP-0519
Residual:  If a second closure is blocked by clock skew, the tolerance question becomes real
           and needs its own corpus measurement before the check is loosened.
```

---

## 3. Proposed changes

### Change 1 — `scripts/verify-source-derived-test-counts.py`: a derive-and-compare tier, HARD

Add a third tier above the existing WARN. Where a flagged literal's source mention is one of the
`SETTINGS_ARRAYS` shapes ([L88](../../scripts/verify-source-derived-test-counts.py#L88)), the gate
reads every `provisioning/deploymentSettings/*.json` that declares that array, collects the set of
observed lengths, and:

- literal ∈ observed set → **silent** (it is a correct transcription; still not derived, so the
  existing WARN is retained at its current wording),
- literal ∉ observed set → **ERROR**, exit 1, naming the array, the literal, the observed
  value(s) and the files they came from.

Everything the gate cannot compute — the `Get-Rev*` readers, the mock-call counts — is untouched
and stays SOFT. The step at
[`build.yml` L504](../../config/revitalise-grant-automation-build.yml#L504) already passes no
`--warn-only`, so nothing in the config changes: the script's own exit code carries the severity.

Update the docstring's `**SOFT.**` paragraph
([L59](../../scripts/verify-source-derived-test-counts.py#L59)) to describe the two tiers, and
`scripts/derived-counts-registry.json`'s `improvement-agent-verify-script-count` is unaffected —
this adds no new script (`ls scripts/verify-*.py | wc -l` = **54**, unchanged).

> **Corrected at application time.** The draft of this line said **55**. Measured, it is **54**,
> and `verify-derived-counts.py` reports no drift on that registry row — which is the point of
> registering it. A hand-typed derived count inside the section of a review that forbids hand-typed
> derived counts; caught only because step 8 re-runs the measurement.

### Change 2 — `scripts/verify-field-length-limits.py`: known-bad fixtures must still be bad

Add `--check-fixtures`, wired onto the existing step at
[`build.yml` L699](../../config/revitalise-grant-automation-build.yml#L699). For every fixture
directory under `src/tests/fixtures/known-bad/` whose name ends `-length`, assert that at least one
value in it still exceeds the **currently declared** limit the gate reads from source. If none
does, fail naming the fixture, its longest value, and the current `MaxLength`.

This is the same failure the `BuildGates` negative test at
[`BuildGates.Tests.ps1` L207](../../src/tests/build/BuildGates.Tests.ps1#L207) catches — but at
step 36 instead of step 69, with a message that says *regenerate the padding* rather than
*expected non-zero, got 0*.

### Change 3 — `agents/WORKFLOW.md`, the fifth case: the dispatcher's half

Append to the fifth case ([L151](../../agents/WORKFLOW.md#L151)) a paragraph stating that the
dispatcher **preempts** this, in the dispatch prompt itself: every dispatch whose task contains a
long-running step (`npm ci`, a full Pester or vitest run, a live solution-checker call) must state
that long steps run **synchronously and blocking within the turn** — never backgrounded, never
deferred to a notification — because a dispatched agent's background child process does not
survive its own turn ending and the dispatcher cannot wake it either way.

### 3.1 What I measured and then declined to propose

- **Widening the gate's scope**, as `IMP-0521` proposes. Declined: measured, the scope is already
  correct and the finding's premise is false (§1).
- **Promoting the whole gate to HARD**, as its own docstring
  ([L62](../../scripts/verify-source-derived-test-counts.py#L62)) anticipates. Declined: 11 live
  findings, 10 of them uncomputable. That is a flag day that halts every build until ten
  assertions are rewritten, and it is how a gate teaches people to route around it.
- **Deriving the fixture padding at test time** rather than checking it. Declined: it makes the
  fixture non-deterministic and the check is cheaper.
- **A constraint row for either change.** Declined: both are enforcement added to gates that
  already exist under `C-TECH-060`
  ([technology-constraints.md L130](../../constraints/technology/technology-constraints.md#L130))
  and `C-TECH-014` ([L52](../../constraints/technology/technology-constraints.md#L52)). A row
  restating a script that already runs is the bloat the limits exist to prevent. **0 of cap 3.**

### 3.2 Measurement against the real corpus

**Change 1.** In-scope assertions across the 11 test files: **1** (settings-array-coupled literal
counts; the other 10 fragile literals trace to `Get-Rev*` readers or mock counts and are out of
tier). Findings: **1. True positives: 1. False positives: 0.**

| Subject | Literal | Observed in source | Verdict |
|---|---|---|---|
| `DeploymentSettings.Tests.ps1:157` `$testKeys.Count`, `settingRows` (pre-fix, from `git archive HEAD`) | 14 | 16 in `test-settings.json`, `prd-settings.json`, `dev-scoring-settings.json` | **true positive** |

**Re-measured at application time, and the subject moved.** The draft measured the live tree at
literal **15** and called it "the halt". By the time the keyword arrived the parallel delivery
dispatch had landed the fix, so the live tree now reads **16 at line 161** and the gate's tier 2
reports **0 findings, exit 0, 1 literal compared**. The true positive above is therefore measured
against the pre-fix file recovered with `git archive HEAD` (literal **14** — HEAD predates the
15 the draft saw), which the gate reports as **1 finding, 1 true positive, 0 false positives,
exit 1**, naming the line and the three files it read.

**Polarity check, both directions, run rather than reasoned:** defective input → exit 1 with the
correct diagnosis; corrected input → exit 0. The design also passes `groupTeams`, where the files
legitimately disagree (2 in `dev-settings.example.json`, 3 in `test`/`prd`) — a literal of either
is accepted, which is why the rule is *matches no observed value* rather than *matches one
specific file*. Both cases are now selftest fixtures.

**N=1 is a thin corpus and I am not dressing it up.** The measurement's value here is the negative
half: the design fires on the one true drift and on nothing else, including the array where
per-environment disagreement is correct. `--selftest` is green at **17** fixtures (was 11; the six
added are all tier 2, including the two that must NOT fire).

**One residual, recorded rather than resolved:** the `count-coupled` annotation suppresses tier 2
as well as tier 1. That follows the approved wording ("where a *flagged* literal…") and is now a
named fixture, but it does mean the documented escape hatch can silence a *measurable* drift, not
just an unmeasurable one. Left as approved; worth revisiting if anyone ever annotates a settings
array.

**Change 2.** Fixtures in scope: **2**. Against the current tree — **0 findings**
(`workflow-description-length` exit 1, `setting-description-length` exit 1; both still violate).
Against `git show HEAD:` for the setting fixture, whose padding was **1478** characters against a
`MaxLength` of **2000** ([`Entity.xml`
L69](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_setting/Entity.xml#L69)) —
**1 finding, 1 true positive.** Correct polarity: it reports the stale fixture and clears on the
regenerated one (now 2017 characters, landed by the parallel delivery dispatch).

### 3.3 Simulation — does the blocker trigger actually clear?

Run on a scratch copy, dispositions applied, then restored and confirmed byte-identical with
`diff`:

```
verify-improvement-log: NOTE — 105 NEW: 0 unread, 0 awaiting-approval, 105 reviewer-deferred,
                        0 already-fixed, 0 approved-not-applied.
```

The blocker rung **clears**. The residual failures in the simulation are the `evidence_grep`
needles, which cannot match a tree the changes have not been applied to yet; real needles go on at
application.

**One thing the reviewer should expect and not act on:** between now and the keyword,
`IMP-0521` classifies `awaiting-approval`, and the blocker rung fires on `unread` **or**
`awaiting-approval` alike (`IMP-0516`). The gate will stay red while this document waits. **The
remedy is the keyword against this document, not another dispatch.**

---

## 4. Retirement

**Checked, and none found.** The candidate I considered is `C-TECH-060`
([L130](../../constraints/technology/technology-constraints.md#L130)): change 2 strengthens its
gate rather than replacing it, and the constraint's own `Verify By` is still the command that
proves it. Retiring it would lose the schema-read rule that change 2 depends on.

Derived, not typed: **10** retired rows and **82** live rows
(`grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l`; `grep -rh '^| C-' …`).

**One stale transcription noted in passing, not proposed as a change:**
[`verify-field-length-limits.py` L15](../../scripts/verify-field-length-limits.py#L15) says
`rev_setting.rev_description` is `MaxLength="500"`. It is 2000. The gate reads the schema at run
time so nothing is broken — but a comment transcribing the number the script exists to avoid
transcribing is this class in miniature, and change 2 should fix that line while it is in the file.

---

## 5. Work this review ROUTES rather than performs

Re-measured immediately before writing this table, per
[`improvement-agent.md` L184](../../agents/improvement-agent.md#L184).

| Routed to | What | State when re-measured at application time | Action |
|---|---|---|---|
| development-agent (in flight) | `DeploymentSettings.Tests.ps1` literal 15 → 16 | **Already landed.** The file now reads `Should -Be 16` at line **161**, matching `settingRows` = 16 in all three settings files. Tier 2 exits 0 against it | **WITHHELD — not dispatched** |
| development-agent (in flight) | `setting-description-length` fixture padding | **Already landed.** 2017 characters against `MaxLength` 2000 | **WITHHELD — not dispatched** |

**Nothing is routed out of this review.** Row 1 changed state between the draft and the keyword:
the draft recorded it as *"Still open — the delivery fix is still required"*, and re-measuring
before handing it on showed the fix had shipped. Dispatching it would have sent an agent to fix a
line that already reads correctly. This is exactly the interval
[`improvement-agent.md` L184](../../agents/improvement-agent.md#L184) describes, and the re-measure
is the only thing that caught it.

Both rows were the same dispatch's work and neither was mine: `src/tests/` is a delivery
deliverable. **I edited no test file.** That is the distinction change 1 turns on — the gate change
is mine, the assertion is theirs. `src/tests/build/BuildGates.Tests.ps1`, the third path
`IMP-0521` names, needed no change either: it is the negative test that correctly went red, and its
suite is green again now the fixture it exercises is bad again (**113 passed, 0 failed**).

---

## 6. Improvement log

`IMPROVEMENT LOG:` 3 findings processed (`IMP-0519`, `IMP-0520`, `IMP-0521`); 0 new findings
appended at draft time.

All three are stamped `reviewed_in: docs/improvements/2026-08-31-improvement-review-3.md` **now**,
at draft time, per [`improvement-agent.md` L126](../../agents/improvement-agent.md#L126). `status`
stays `NEW`; `applied_by` does not exist until something is applied.

Dispositions on approval:

| Finding | Disposition | Closure evidence |
|---|---|---|
| `IMP-0521` | `APPLIED` — changes 1 and 2 | `observable_at: V1`. Re-run both gates; change 1 must exit 1 naming line 158 while the literal is 15 |
| `IMP-0520` | `APPLIED` — change 3 | `observable_at: n/a`. The text on disk is the whole change |
| `IMP-0519` | **stays `NEW`, with a `deferred_reason`** | One instance, ~5 minutes, no delivery impact; loosening a monotonicity check that currently catches copy-paste closures needs its own corpus measurement first. `revisit_when` is applied **verbatim** from the entry |

---

## 7. What lands on approval

All three changes are on disk. Nothing was withheld; two draft figures were corrected and the
routed table was emptied, all three recorded above at the point they apply.

| # | File | What landed | Verified by |
|---|---|---|---|
| 1 | [`scripts/verify-source-derived-test-counts.py`](../../scripts/verify-source-derived-test-counts.py) | Tier-2 derive-and-compare: `observed_array_lengths()` reads `provisioning/deploymentSettings/*.json` at any nesting depth; a `SETTINGS_ARRAYS` literal matching no observed length is an `ERROR` with **exit 1**. Tier 1 unchanged and still SOFT | `--selftest` PASS, **17** fixtures; live tree exit 0; pre-fix HEAD exit 1 with 1 true positive |
| 2 | [`scripts/verify-field-length-limits.py`](../../scripts/verify-field-length-limits.py) | `--check-fixtures`: every `*-length` known-bad fixture must still exceed the **currently declared** limit. Failure names the fixture and its longest value. The summary line now separates the two failure shapes instead of reporting both as "values exceed the limit" | Live exit 0, 2 fixtures still violating; with the 1478-char fixture restored, exit 1 naming it |
| 2b | [`config/…-build.yml` L699](../../config/revitalise-grant-automation-build.yml#L699) | `--check-fixtures` wired onto the existing `field-length-limits` step, with the reason in a comment beside it | `verify-build-config.py` exit 0 |
| 3 | [`agents/WORKFLOW.md`](../../agents/WORKFLOW.md) | The fifth case gains "The dispatcher's half", carrying the verbatim sentence a dispatch prompt must include, and stating on the record that this is a second prose fix in a class at x7 with the next rung named | Text on disk is the whole change |

**Stale comment fixed in passing**, as §4 anticipated: `verify-field-length-limits.py`'s docstring
said `rev_setting.rev_description` "is `MaxLength=500`" when it is **2000** — a comment
transcribing the number the script exists to avoid transcribing. Now states the historical value as
historical, and says so.

**Nothing new was appended to the log.** [`IMP-0522`](../../logs/improvement-log.jsonl) (friction,
`unread`) was left for its own cycle by explicit reviewer instruction and is **not** processed
here; it is the one remaining `unread` entry and it is a NOTE, not a trigger.

Closing state: [`verify-improvement-log.py`](../../scripts/verify-improvement-log.py) `--check`
**exits 0**. The blocker rung is clear.

---

## 8. Gate

```
IMPROVEMENT REVIEW APPLIED — docs/improvements/2026-08-31-improvement-review-3.md

Findings processed: 3 unread  →  3 clusters
Regression check:   4 prior changes audited, 2 classes recurred
Applied:            0 constraints (cap 3), 2 gates/scripts, 0 skill/knowledge edits,
                    1 agent-file edit, 1 build-config wiring, 0 retirements
Withheld:           0 changes; 2 routed items (both re-measured as already landed)
Altitude calls:     2 generalised from instance to class, 1 left as notes
Digest:             regenerated — 519 entries, 517 distinct lessons, 596 lines

APPROVED and applied 2026-08-31. Log validator exits 0.
```
