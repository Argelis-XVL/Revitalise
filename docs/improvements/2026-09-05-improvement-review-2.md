# Improvement Review — 2026-09-05 (2)

**Status:** APPLIED 2026-09-05 under `APPROVE IMPROVEMENTS`. See §11 for the applied record and for
the premise that failed re-verification at apply time.
**Trigger:** blocker escalation — [`IMP-0606`](../../logs/improvement-log.jsonl#L603), unread, appended by build-agent.
**Filename claimed** at step 6 via `scripts/allocate-review-number.py`.
**WBS:** 0.4 (`applicant-ethnicgroup-form-defect`).

---

## 1. Conclusion

**Yes — generalise. The derive-from-source fix is the right altitude and it is small enough for this
dispatch: roughly fifteen lines inside one test file, no new gate script.**

The decisive measurement is that the hand-copied corpus is **exactly two patterns**, both in
[`BuildGates.Tests.ps1`](../../src/tests/build/BuildGates.Tests.ps1#L236) — and the second one
([`ThresholdPattern`](../../src/tests/build/BuildGates.Tests.ps1#L280)) has **no sync check at all**,
so it is strictly more exposed than the pattern that just halted the build. Deriving both removes
the drift structurally rather than guarding against it.

Two things the brief did not anticipate, both measured below: the fix development-agent already
landed **holds** but leaves the sync check pointing the wrong way, and the generalised gate this
class already produced (`verify-source-derived-test-counts.py`) **ran, exited 0, and cannot see
this defect by design**.

---

## 2. Scope, and what was excluded

`python3 scripts/verify-improvement-log.py --check` reports **130 NEW: 1 unread, 0
awaiting-approval, 129 reviewer-deferred, 0 already-fixed**.

Scope is the **1 unread** entry: [`IMP-0606`](../../logs/improvement-log.jsonl#L603).

**Excluded: the 129 `reviewer-deferred` entries**, each carrying a `deferred_reason` a human
accepted. Not re-derived, per activation step 2. The gate also emits 5 standing `corrects` warnings
(`IMP-0290`, `IMP-0298`, `IMP-0320`, `IMP-0430`, `IMP-0437`); none names an entry this review acts
on, and none is left in a state this review changes.

No review document in `docs/improvements/` mentions `IMP-0606` — checked by grep, not assumed, so
this is not a re-derivation of parked work.

---

## 3. Live re-verification of the brief's premise

The brief states development-agent fixed
[`BuildGates.Tests.ps1:236/256`](../../src/tests/build/BuildGates.Tests.ps1#L236) and re-ran the
suite. **Re-run here rather than trusted — 112 passed, 1 failed, and the failure is the expected
circular one.**

```
pwsh -NoProfile -Command "Invoke-Pester -Path src/tests/build/BuildGates.Tests.ps1 -Output Detailed"
Tests Passed: 112, Failed: 1
```

The single failure is `'verify-improvement-log --check' passes against the real log`
([line 923](../../src/tests/build/BuildGates.Tests.ps1#L923)), which fails **because `IMP-0606`
itself is unread**. All four FR-016 tests pass, including
[the sync check](../../src/tests/build/BuildGates.Tests.ps1#L254). The fix holds.

### But the sync check only ever pointed one way, and that is the actual defect

This is the part the finding does not state and it is why the instance patch is not enough. The
loop at [line 258](../../src/tests/build/BuildGates.Tests.ps1#L258) already derives the column list
**from the test's own pattern** and asserts each column appears in the config. That direction
catches *"the test names a column the config lacks"*. It cannot catch *"the config names a column
the test lacks"* — which is exactly what happened.

The only thing covering that direction was the hand-typed closing anchor at
[line 256](../../src/tests/build/BuildGates.Tests.ps1#L256), which moved from
`'rev_intakereviewnote)'` to `'rev_ethnicgroup)'`. **That anchor is a hand-maintained copy guarding
against hand-maintained copies**, and it will break identically on the next column added to
[build.yml:416](../../config/revitalise-grant-automation-build.yml#L416).

---

## 4. Regression check

| Question | Answer |
|---|---|
| Has any finding in the previous review's classes appeared since? | **No.** `resolved-note-retains-live-expiry`, `forecast-without-an-owner`, `platform-fact-groundtruthed`, `routed-work-not-reverified-at-apply-time` — none recurred. `IMP-0606` is the only entry appended since, and it is a different class. |
| This class was fixed by a **gate** (review 48, `IMP-0521`). Did it recur? | **Yes — this is the recurrence.** |
| Did that gate run? | **Yes. Exit 0, 11 warnings, and none of them is `BuildGates.Tests.ps1`.** |
| Was the closure evidence at the right level? | Yes. `IMP-0606` is `observable_at: V2` and the re-run above is V2. |

**So the gate is mis-scoped, not broken — and the mis-scope is declared in its own docstring.**
[`verify-source-derived-test-counts.py`](../../scripts/verify-source-derived-test-counts.py#L109)
matches `<subject>.Count | Should -Be <n>`. `IMP-0606` is a hand-copied **string pattern**, not a
count, and it is assembled in a `BeforeAll` — which that file's own *"WHAT IT CANNOT DO"* paragraph
names as its honest limit.

This is a `gate-scope-mismatch` in its own right and is logged as one below, per the regression-check
row in [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L318).

---

## 5. The finding's cited precedent does not exist

`IMP-0606`'s `proposed_change` justifies itself by analogy: *"the same fix already applied to
verify-flow-definition-language's threshold list"*. **Measured, and it is false.**

```
LABEL 3: grep -rn "KnockoutThreshold" scripts/
scripts/verify-tad-coverage.py:246:   continue  # `REV_FinanceOnly`, `GR-2026-00001`, `KnockoutThreshold`
```

`verify-flow-definition-language.py` derives no threshold list; the only mention of the token
anywhere in `scripts/` is an identifier-exclusion in an unrelated gate. This is the
`IMP-0570`/`IMP-0571` shape — a proposal written by analogy with a neighbour, where the analogy was
never run.

**The intent survives; the citation does not.** Deriving from source is still correct here, for the
reasons in §1 and §3, and the proposal is adopted on that evidence rather than on its own stated
precedent. The false premise is recorded so it is not inherited.

---

## 6. Clusters

```
CLUSTER A: hand-maintained-count-drifts-from-source  (IMP-0606, 32nd instance)
Altitude:  CLASS — but the generalisation is a SOURCE change, not a new gate
Ladder row: "second instance of the same class → generalise. Instance patches are forbidden here"
Becomes:   src/tests/build/BuildGates.Tests.ps1 — one Get-BuildGatePattern helper that reads the
           named step's `grep -rnE` pattern out of config/revitalise-grant-automation-build.yml at
           test-run time. Both $script:Fr016Pattern (L236) and $script:ThresholdPattern (L280) are
           derived from it. The literal-substring sync check at L254-261 is DELETED — a derived
           pattern cannot drift from the thing it is read from, so the check becomes tautological.
Retires:   the L256 hand-typed closing anchor, and the L258 one-directional column loop
Cites:     IMP-0606, and the class record IMP-0005/IMP-0039/IMP-0120/IMP-0155/IMP-0212/IMP-0521
Residual:  If a future build step's pattern is not a single-line `grep -rnE '...'`, the helper
           cannot parse it and must fail loudly rather than return empty. Corpus is 2 today; the
           helper asserts a non-empty result for exactly that reason.
```

```
CLUSTER B: gate-scope-mismatch  (new finding, from this review's regression check)
Altitude:  NOTE + a new log entry. NOT a gate extension.
Ladder row: "one instance, cause is general" — and the anti-bloat limit against speculative gates
Becomes:   a new IMP- entry recording that verify-source-derived-test-counts.py's scope is
           `.Count` literals only, so a hand-copied build.yml PATTERN is outside it.
Why not extend the gate: after Cluster A lands, the corpus of hand-copied build.yml patterns is
           ZERO. A gate would guard nothing on day one, and a phrase-based matcher over prose
           comments ("Verbatim from config") is the instrument this repo has measured five times
           at 48-100% false (IMP-0422). Structural removal beats a gate here.
Residual:  A THIRD hand-copied pattern added later is undefended. The discharge condition is
           written into the helper's own comment, where the next author will be.
```

---

## 7. The disposition simulation

Run on a scratch copy per activation step 8, because the question *"does the halt actually clear"*
is not answerable by reading `classify()`.

| Simulated disposition | Result |
|---|---|
| **`reviewed_in` only** — what this draft does | `0 unread, 1 awaiting-approval`. **`TRIGGER` still fires.** The blocker rung fires on `unread` **or** `awaiting-approval` alike. |
| **Full `APPLIED` closure** — what the keyword does | `0 unread, 0 awaiting-approval`. Blocker trigger **cleared.** One remaining `ERROR`, and it is the correct one: the `evidence_grep` needle `Get-BuildGatePattern` is not in the file *because nothing is applied yet*. It resolves when the change lands. |

**So stamping this draft does not release the build.** The `applicant-ethnicgroup-form-defect` build
stays halted at step 68/73 until `APPROVE IMPROVEMENTS` is sent and the change is applied. That is
the design, not a defect — but it is worth stating plainly, because a draft parked overnight looks
from the outside like progress on the halt.

Real log confirmed byte-identical after the simulation; all writes went to the scratchpad.

---

## 8. Anti-bloat

- **New constraints: 0** (cap 3). This is a source change plus a log entry; neither needs a rule row.
- **New gates/scripts: 0.** `verify-*.py` count stays at **57** (derived:
  `ls scripts/verify-*.py | wc -l`). No `suite-gate-is-not-a-step` exposure.
- **Retirement considered.** Live constraint rows: **85**; retired: **10** (both derived, per
  `constraints/README.md`). **No constraint retirement is proposed** — the retirement in Cluster A is
  of two *test assertions*, not of a constraint row, and no live row is made redundant by it.

---

## 9. Proposed disposition on the keyword

| Entry | Proposed status | Change |
|---|---|---|
| [`IMP-0606`](../../logs/improvement-log.jsonl#L603) | **APPLIED** | `Get-BuildGatePattern` helper; both patterns derived; sync check deleted. Closed at **V2** by re-running the Pester suite — the same level the defect was observed at. |

Plus **one new entry appended** for Cluster B (`gate-scope-mismatch`), with the id taken from
`scripts/allocate-improvement-id.py` read immediately before the append, never from `tail -1`.

---

## 10. Reviewer decision required

One decision. It is in the gate output.

---

## 11. Applied record — and the premise that failed re-verification

**The draft's "the corpus is exactly two patterns" premise was WRONG, and re-measuring at apply
time per activation step 8 is the only reason it was caught.** There is a third hand-maintained copy
of the same property, and it is stale right now.

| Measurement | At draft (§1, §3) | At apply |
|---|---|---|
| Hand-copied FR-016 column lists in the repo | **2**, both in `BuildGates.Tests.ps1` | **3** — plus [`ScoringInvariants.Tests.ps1`](../../src/tests/solutions/ScoringInvariants.Tests.ps1#L554) |
| Columns in the build gate's alternation | 21 | 21 |
| Columns in the third copy | not measured | **15 — short by six**, including `rev_ethnicgroup` |

The draft grepped `src/tests/build/` and the build config. It did not grep `src/tests/` whole. The
conclusion it supported — *derive rather than hand-copy* — is unchanged and is strengthened by the
correction, which is exactly the `IMP-0571` shape: **a false premise supporting an independently
correct decision**, invisible because nothing downstream exercises it.

### The second false premise, in the code being edited

The comment above `Invoke-GrepGate` claimed *"VerifyBuildConfig.Tests.ps1 additionally asserts these
patterns stay in sync."* **It does not and never did** — that file's `It` blocks cover the
negative-test registry, step order, input types and shell parsing, and never mention these patterns.
Rewritten in the same change, per the retirement rule in
[`how-to-promote-a-finding.md`](../../skills/how-to-promote-a-finding.md#L88): a retired guarantee
that still has a documented user is worse than one never retired.

### What was applied

[`BuildGates.Tests.ps1`](../../src/tests/build/BuildGates.Tests.ps1) gains `Get-BuildGatePattern`,
which reads the `grep -rnE` pattern out of a named build step at run time. Both patterns are derived;
the hand-maintained sync check is gone.

**One addition beyond the literal draft, recorded so it is not silent.** The draft said the sync
check would be *deleted* as tautological. It was deleted and **replaced by two negative tests** that
assert the helper throws — on an unknown step, and on a step declaring no grep pattern. This is
additive and sits squarely inside the draft's own Residual (*"the helper asserts a non-empty result
for exactly that reason"*): a silently-empty pattern would make every `-Not -Match` assertion pass
vacuously, which is the `gate-cannot-fail` shape.

### Gate evidence

- **Suite re-run: 114 passed, 1 failed** (was 112/1; three tests added, one removed). All six FR-016
  tests and both threshold tests pass **with the derived patterns**, which is the proof the
  derivation is real rather than vacuous — the known-bad fixture still fails, and the missing-target
  case still returns 2.
- The one failure is `'verify-improvement-log --check' passes against the real log`, the circular
  self-reference of `IMP-0606`. It clears with this closure.
- `verify-improvement-log.py --check`: **exit 0**, `0 unread, 0 blocker`. **The build halt is
  released.**
- Digest regenerated; `--check` exit 0. `verify-*.py` count **unchanged at 57** — no script added, so
  no `suite-gate-is-not-a-step` exposure.

### Entries

| Entry | Status | Change |
|---|---|---|
| [`IMP-0606`](../../logs/improvement-log.jsonl#L603) | **APPLIED** | `Get-BuildGatePattern`; both patterns derived. Closed at **V2** by re-running the suite |
| [`IMP-0607`](../../logs/improvement-log.jsonl#L604) | NEW, deferred | Cluster B class marker: the derived-counts gate sees counts, not strings. Gate deliberately **not** extended |
| [`IMP-0608`](../../logs/improvement-log.jsonl#L605) | **NEW, routed** | The third copy. **Not fixed here** — see below |

### What remains, and why it was not done here

`IMP-0608` is **routed to the reviewer, not fixed.** Two reasons, and neither is effort: the approved
scope named `BuildGates.Tests.ps1`, and changing which columns an FR-016 compliance assertion covers
is delivery work against `C-DOM-030`'s register rather than a rules change this agent should make
unreviewed. It is logged at `rework`, not `blocker`, so it records the defect without re-halting the
build — an honest open entry rather than a closed one nobody tested.

**The lesson it carries is the transferable one.** Every assertion over that list is *negative*
(`Should -Not -Match` per column), so a dropped column removes an assertion instead of breaking one:
**the suite goes greener as coverage falls.** That is the opposite of the count-shaped instances of
this class, which fail loudly — and it is why this one sat undetected while the noisy one halted a
build within hours.
