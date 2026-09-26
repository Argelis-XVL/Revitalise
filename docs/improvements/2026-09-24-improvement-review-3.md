# Improvement Review — 2026-09-24 (3)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 4 `NEW` → 1 cluster (1 further `NEW` entry excluded, named in §5)
**Trigger:** blocker escalation — one unread critical finding
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** ~~DRAFT — parked at the gate, nothing applied~~ **APPLIED 2026-09-24** — approved as
drafted; both changes landed, four entries closed. See §8.

---

## Summary

A build was halted by a test that still demanded a value the platform had already rejected. The
test has since been corrected by a parallel dispatch, so **the thing this review was called to fix
is already fixed** — and the useful question is the one left behind: why the correction that
withdrew that value did not reach the test suite in the first place.

The answer is measured and small. This repository's documented reference-sweep command **cannot see
PowerShell files at all**, and the PowerShell test suite is the one referrer that *breaks* rather
than quietly rots. This review proposes two prose edits and, deliberately, **no new gate** — the
obvious gate measures at 25% precision and its false positives are structural.

---

## 1. Regression check — did the last review's changes work?

The last review applied was [review 2 of 2026-09-24](2026-09-24-improvement-review-2.md), which
corrected the invented FormXml `type` value in source, taught the general component-shape gate to
check attribute values, retired a duplicate instance gate, and recorded the defence.

| Prior change | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|
| `entity form` shape block + `attribute_values` in [verify-component-shape.py](../../scripts/verify-component-shape.py) | `platform-contract-guessed-not-groundtruthed` | **No** | Working. Gate green over 56 files, 3 shapes |
| Retirement of the duplicate `formxml-type-values` gate | `declared-policy-not-mechanically-enforced` | **No** | Working — one gate, not two |
| The defence recorded in [class-defences.json](../../logs/class-defences.json) | same | **No** | Working |

**One class recurred, and it recurred in a surface none of those changes covered.** The general
shape gate reads `Entities/*/FormXml/*/*.xml` — solution source. The defect that halted the build
was in `src/tests/`. The gate did not fail to fire; it was never pointed at the test tree, and
pointing it there is the proposal this review declines (§3).

| Question | Answer |
|---|---|
| Was the recurrence after a *prose* change or a *gate*? | After a **prose** change — the sweep rule. Per the ladder, that is evidence of wrong altitude, and §2 addresses the altitude rather than repeating the prose |
| Did any gate exist and not fire? | No. No gate has ever covered the test tree for this property, so this is not a `gate-cannot-fail` |
| Did closure evidence match the level the defect was visible at? | Yes. Both prior entries were correctly held **open** at V3, not closed on file evidence — that judgement stands and is unaffected by this review |

---

## 2. Clusters and promotion decisions

### The altitude call, stated plainly

The finding that halted the build is labelled the **third** instance of *"a test asserts the thing
that was wrong"*. The brief asks whether a third instance needs a generalised change. **The honest
answer is that the label is shared and the mechanism is not**, and promoting on the label would add
a rule against a failure that did not happen.

The first two instances were **test-authoring** defects: a test written from an unverified belief
about the platform, at the moment the test was written. That has a defence — a rule in
[how-to-write-a-test-plan.md](../../skills/how-to-write-a-test-plan.md) — and it has held since
2026-08-21; nothing in this incident shows it failing.

This instance is a **fix-time sweep** defect. The test was written honestly from the convention the
whole repository then believed. It became wrong the instant source was corrected, and the only
moment it could have been caught is the sweep that followed the correction. That is a different
mechanism with a different remedy, and it has **two** measured instances on the same day, from the
same dispatch.

```
CLUSTER: the reference sweep after a correction does not reach the test tree   (x2)
Altitude:   CLASS — second instance, both 2026-09-24, both from the dispatch that fixed
            the FormXml type value. One missed a retired script's Pester block; one missed
            a withdrawn literal asserted in a Pester test.
Ladder row: "second instance of the same mechanism → generalise" + "an agent had the
            information and still did the wrong thing → skill edit"
Becomes:    (1) the sweep command in how-to-promote-a-finding.md §2.4 — its file filter
                cannot match *.ps1, measured at 0 hits vs 7
            (2) the closure rule in how-to-verify-a-platform-contract.md §4 — sweeps an
                assumption ID across four documents; adds the withdrawn VALUE across the
                whole tree, and the test suite as a fifth location
Retires:    the extension allow-list as an instrument in that command — not a constraint
Cites:      the two findings named in §3
Residual:   Both changes are prose, and prose is what the regression check above just
            found insufficient. This is accepted deliberately and the reason is in §3:
            the mechanical form was built and measured at 25% precision, and its false
            positives cannot be removed without handing every author an opt-out.
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | skill | [how-to-promote-a-finding.md](../../skills/how-to-promote-a-finding.md#L88) | Replace the retirement sweep's extension allow-list with an unfiltered whole-tree sweep; name the test suite as the referrer that breaks rather than rots; record the two command traps measured below | IMP-0869 | NO — instruction change | N/A |
| 2 | skill | [how-to-verify-a-platform-contract.md](../../skills/how-to-verify-a-platform-contract.md#L498) | Extend the closure rule: when a closure **withdraws a value**, sweep the withdrawn literal across the whole tree, not only the assumption id across four documents; add the test suite as a fifth location | IMP-0871 | NO — instruction change | N/A |

**Constraint budget:** 0 of 3 used.

### Why change 1 is the one that matters

The sweep command this repository documents is, verbatim:

```bash
grep -rn -- '<the-retired-flag-or-mode-or-convention>' . \
  --include='*.py' --include='*.md' --include='*.yml' --include='*.json' \
  --exclude-dir=.git --exclude-dir=node_modules
```

Measured against the withdrawn literal under `src/tests/`:

| Command | Hits |
|---|---|
| That filter set, applied with correct semantics | **0** |
| The same with `--include='*.ps1'` added | **7** |
| Unfiltered | 11 |

**The entire PowerShell test suite is invisible to it**, and that suite is precisely the referrer
that turns a tidy-up into a red build. An extension allow-list encodes the author's guess about
where references live; the reference that costs is by definition the one the author did not think
of. The remedy is to stop filtering, not to add `*.ps1` to the list.

### Two command traps, both measured here, both going into the skill

These are not incidental — the finding being processed proposed one of these commands as its own
remedy.

**`git grep` cannot see this system's own rules.** `agents/`, `skills/` and `templates/` are
symlinks into the `.engine` submodule (git mode `120000`). A plain `git grep` for a string that
appears three times in `agents/improvement-agent.md` **exits 1 with no match**;
`git grep --recurse-submodules` finds it. Any sweep prescribed as `git grep` must carry that flag
or it silently skips every agent file and every skill.

**On this machine `grep` is ugrep, and flags placed after the path are parsed as filenames.**
Written exactly as the skill writes it — filters trailing the `.` — the filters are ignored with a
warning, so the command does not do what it documents. Both measurements are recorded here because
this review's own first pass at them was wrong and had to be re-run.

### The gate this review is NOT proposing, and the number that decided it

The mechanical form is real and was designed: for every attribute vocabulary declared in
[component-shapes.yml](../../constraints/technology/component-shapes.yml#L82), fail any file under
`src/tests/` asserting a value outside it. It asserts on **values, not phrases**, which is the form
this repository's evidence favours.

It was measured before being proposed, and the measurement killed it:

| Corpus | Findings | True positives | False |
|---|---|---|---|
| The tree as it stands today | 3 | **0** | 3 |
| The pre-fix tree (`git show HEAD:`) | 4 | **1** | 3 |

**25% precision, and the false positives are structural.** All three are in
[BuildGates.Tests.ps1](../../src/tests/build/BuildGates.Tests.ps1#L843) — they are the negative
tests that prove the component-shape gate *rejects* the bad value. A gate's own known-bad assertion
must name the bad value; that is what makes it a negative test. Removing them needs an opt-out
marker, which hands every author an escape hatch on a real finding, and this repository has
measured phrase-based instruments five times at 48–100% false.

So: **withheld, with the number**, per the rule that a design measured at high false-positive rates
is redesigned rather than shipped with an exemption.

---

## 4. Retirements

> Retirement check performed: 86 live constraint rows and 10 already retired were reviewed; none is
> currently redundant, because this review adds no constraint and supersedes no rule's subject
> matter.

One **instrument** is retired inside change 1: the extension allow-list in the retirement sweep
command. That is a correction to a command, not a constraint retirement, and it is recorded here so
the check is not reported as vacuous.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0862

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0862 | `gate-scope-mismatch` | Not the blocker this review was summoned by, and already declared out of scope by [review 1 of 2026-09-24](2026-09-24-improvement-review.md). It proposes widening one gate's document scope — a sound change, unrelated to this cluster | the next batch review, or a second TAD-scope miss |

The queue also holds 206 entries carrying a reviewer-accepted `deferred_reason` and 1 non-blocker
parked at its own gate ([IMP-0855](../../logs/improvement-log.jsonl)); none were re-derived here.
One unread blocker does not pull a review of everything around it.

### One routed item, re-measured and WITHHELD

The blocker finding proposed routing a one-line test correction to development-agent. **That is
already done.** The assertion now reads `type="quick"` and the test's own name has been corrected
with it; the pre-fix text survives only in `git show HEAD:`. Nothing is dispatched for it, and the
change is credited to the parallel dispatch rather than to this review.

That dispatch logged its own entry while this draft was being written. It carries `corrects`
against the blocker, reports the corrected assertion and a standalone Pester run of the file at
**69 of 69 passing, 0 failed**, and proposes no change of its own. It was folded into this review
rather than left unread, and it does not disturb the altitude call: its own lesson says the same
thing this review's change 2 does, and explicitly calls itself *the closing half of that finding,
not a new pattern*. So the class still has one live mechanism here, not two.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 867 | 867 (no entries appended) |
| Digest lines | 770 | regenerated at apply time |
| Recurring classes (x≥2) | unchanged | unchanged — no new class introduced |

The digest is currently **stale** against the log, because the blocker entry was appended after the
last regeneration. Regenerating is part of applying this review.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-24-improvement-review-3.md

Findings processed: 4 NEW  →  1 cluster
Regression check:   3 prior changes audited, 1 class recurred
Proposed:           0 constraints (cap 3), 0 gates/scripts, 2 skill/knowledge edits,
                    0 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 1 left as a note
Digest:             will regenerate — stale by 1 entry, 0 new recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

Approved as drafted and applied 2026-09-24. Both changes landed; four entries closed.

### What landed

| Change | Where | Evidence |
|---|---|---|
| (1) The sweep command — unfiltered whole-tree `git grep -n --recurse-submodules`, the extension allow-list removed, the test suite named as the referrer that breaks rather than rots, and both measured command traps recorded | [how-to-promote-a-finding.md §2.4](../../skills/how-to-promote-a-finding.md#L88) | Positive control run: the new command returns the control string from `agents/improvement-agent.md`, which the old form missed |
| (2) The closure rule — a fifth location (`src/tests/`) and a withdrawn-**value** sweep beside the existing assumption-**id** sweep | [how-to-verify-a-platform-contract.md §4](../../skills/how-to-verify-a-platform-contract.md#L498) | Rule text carries the command and the incident that produced it |
| (3) The registered digest line count, 770 → 771, in **both** copies | [generate-known-failure-modes.py](../../scripts/generate-known-failure-modes.py#L45) and its `.engine` twin | `verify-derived-counts.py`: OK, 10 of 10; twins confirmed byte-identical |

### The log

| Finding | Disposition |
|---|---|
| The blocker (test asserting the withdrawn value) | **APPLIED** — its own proposed fix withheld from routing (already landed elsewhere); the general lesson is change 2 |
| The incomplete retirement sweep | **APPLIED** via change 1, with a target correction recorded below |
| The test correction (`corrects` the blocker) | **APPLIED** — supplies the re-observation the blocker's closure rests on |
| The sweep-instrument measurement | **APPLIED** via change 1 |

`verify-improvement-log.py --check` went from **FAILED** to **OK (schema + triggers)** — the blocker
trigger this review exists to clear is clear. 9 warnings remain, all pre-existing `corrects` chains
on entries this review does not touch.

### Two deviations, both recorded rather than silent

**The target correction.** The sweep finding named `agents/improvement-agent.md`. The command it
asks to fix lives in the promotion skill; the agent file delegates the retirement procedure to it.
Editing the named file would have written a second, competing copy of the rule, so the edit landed
where the command is. Intent preserved exactly; this is recorded in the entry's `applied_by` and in
the gate output as well as here.

**The needle drifted from the approved wording and the text was corrected, not the needle.** Change
1 was first written as *"because it BREAKS rather than rots"*, which does not contain the phrase
this document committed to as the closure's evidence anchor. Rewording the needle to match the prose
would have been the silent half of the substitution this agent's own rules forbid, so the prose was
reworded to carry the approved phrase instead.

### What was NOT done, and why

No new gate, per §3 — the design measured at 25% precision with structural false positives. No
constraint. No retirement of any constraint row. The `src/tests/` sweep remains **prose**, which §2's
`Residual` line already names as this cluster's accepted weakness.

### Planned dispositions

| Finding | `observable_at` | Disposition | Evidence |
|---|---|---|---|
| The blocker (test asserting the withdrawn value) | V1 | **CLOSE** | `evidence_grep` on the corrected test name in [IntakeContract.Tests.ps1](../../src/tests/solutions/IntakeContract.Tests.ps1#L722), verified present exactly once |
| The incomplete retirement sweep | V1 | **CLOSE** | `evidence_grep` on change 1 in the promotion skill |
| The test correction (`corrects` the blocker) | V1 | **CLOSE** | `evidence_grep` on the same corrected test name; the entry proposes no change and records its own Pester run |
| The sweep-instrument measurement, logged by this review | V1 | **CLOSE** | `evidence_grep` on `--recurse-submodules` in the promotion skill, which change 1 introduces |

All four are V1, so `evidence_grep` alone is sufficient and no `reobserved` record is required.

### The dispositions were simulated before this draft was parked

Run against a scratch copy of the log with the three closures applied, never against the real file:

| Result | |
|---|---|
| **The blocker trigger clears** | This is the question the simulation exists to answer, and the answer is yes |
| Needles on the corrected test file | Both resolve — matched on one line, as required |
| One residual error | Change 1's own needle is not in the skill yet, because change 1 has not been applied. It resolves when it lands |

**So change 1 must contain the phrase `the referrer that breaks rather than rots` verbatim.** That
is the needle the closure is evidenced by; rewording it at apply time without re-pointing the needle
is what turns a real change into an unevidenced claim.

**One safer-method note.** The simulation was first attempted by writing the dispositions into the
real log and restoring it afterwards. The harness refused that, correctly, and the refusal was not
worked around — the run above uses the gate's own `--log` flag against a scratch copy, which is
strictly safer and should be the documented form of this step.

**One target correction to report at apply time.** The sweep finding named
`agents/improvement-agent.md` as its target. The sweep command it asks to fix lives in
[how-to-promote-a-finding.md §2.4](../../skills/how-to-promote-a-finding.md#L88); the agent file
delegates the retirement procedure rather than carrying the command. Landing the edit where the
command actually is preserves the finding's intent exactly; landing it where the finding pointed
would have written a second, competing copy of the rule.
