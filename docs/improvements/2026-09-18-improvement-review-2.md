# Improvement Review — 2026-09-18 (2)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 3 `NEW` → 2 clusters
**Trigger:** blocker escalation (unread `blocker`, not batched)
**Gate:** `APPROVE IMPROVEMENTS`

**Status: APPLIED IN FULL 2026-09-18.** The single row in §3 landed, all three findings are closed
`APPLIED`, and the digest is regenerated and current. 0 rows remain unapplied, 0 withheld. Two
*proposals inside* those findings were withheld as already-satisfied — that is recorded in §2 and
on each entry, and is not an unapplied row.

~~DRAFT — parked at its gate. `APPROVE IMPROVEMENTS` has not been given. Nothing in §3 has been
applied; §8 is empty by design.~~

---

## 0. The one thing to read first

**Both problems were caught by gates that already exist, and both findings ask for those gates to
be built.**

The dispatch brief asks whether each of these two repeat problems now needs a general
check — a preflight proving every `{{...}}` placeholder is declared, and a hard check failing any
re-test date older than 14 days. Both already exist, both are wired into the build, both are what
stopped the build this morning, and both are green again now.

Executed, not read — `python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml`,
true exit status **0** (taken from `$?` on a redirect, not through a pipe):

```
PIPELINE CONFIG PREFLIGHT: PASS — 116 steps across 3 environment(s).
```

| What the brief asks for | What already exists | Where |
|---|---|---|
| A check that every placeholder in a settings file is declared, checked structurally | Check 11. It walks every value position by dot-path, demands a matching declaration carrying owner, reason and expiry date, and fails on a missing, unowned **or expired** one | [verify-pipeline-config.py#L297](../../scripts/verify-pipeline-config.py#L297), wired at [build line 75](../../config/revitalise-grant-automation-build.yml#L75) |
| A hard check failing any re-test date older than 14 days | Check 14, plus a warning four days before expiry and a separate check that a resolved note has its block removed rather than re-dated | [verify-pipeline-config.py#L505](../../scripts/verify-pipeline-config.py#L505) and [#L655](../../scripts/verify-pipeline-config.py#L655) |

So the answer to both halves of the brief is the same: **nothing to build, and nothing to
retire.** The brief also asks whether the earlier five instances' own one-off gates should be
retired in favour of a general one. Measured: there are no one-off gates. Check 11 *is* the
generalisation, written in [review 3 of 2026-08-21](2026-08-21-improvement-review-3.md) from the
first instance, and it has defended this ever since.

**The real defect this review fixes is that the system told both agents otherwise.** The digest's
recurring-class table is derived purely from how many times a class has occurred, so it cannot say
"this one is already defended and the gate is green". Its heading reads *"where a general gate is
missing"* for all 56 rows. Both findings followed that instruction and proposed building a gate
into the very file whose checks had just caught them. That is a read-path defect, it is
mechanical, and it is the one change proposed here.

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| A check that spots a log entry a review left behind rather than parked | 2026-09-18 (review 1) | `stale-deferral-uncaught-across-sessions` | **YES — one of today's two findings** | **Correctly scoped; not a miss.** That check guards entries in the improvement log. Today's recurrence is a re-test date in the pipeline config — a different thing wearing the same class name (see §2) |
| A compliance register split into two independent axes | 2026-09-18 (review 1) | `approved-document-internally-inconsistent` | NO | Working — leave alone |
| Field-permission route wired for the two promoted environments | 2026-09-18 (review 1) | `gate-scope-mismatch` | NO | Working — leave alone |

**Did a gate exist and fail to fire?** No. Both gates fired, correctly, first time, and halted the
build — which is the designed behaviour, not a defect in them.

**Did the closure evidence match the level each defect was visible at?** Yes. Both of today's
defects were visible only when something ran, and both were re-confirmed by re-running the same
preflight to a clean exit, not by reading a file.

**One class recurred after a mechanical fix, and the audit of it is the finding of this review.**
The class name `stale-deferral-uncaught-across-sessions` covers two unrelated mechanisms — a
forgotten entry in the improvement log, and a re-test date in a deployment config. Yesterday's gate
closed the first. Today's finding is the second. Counting them as one class is what produced a
recurrence signal against a change that was never aimed at it.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: config-placeholder-known-but-not-fixed   (x6 as tagged: IMP-0145, IMP-0166,
                                                     IMP-0175, IMP-0243, IMP-0244, IMP-0763,
                                                     plus IMP-0765 recording the fix)
Altitude:   ALREADY AT CLASS — the generalisation exists and is green. No new altitude to reach.
Ladder row: none applies. The ladder's "second instance → generalise" rung was taken on the
            second instance, in review 3 of 2026-08-21, and the gate it produced caught this one.
Becomes:    NOTHING in the gate. The source fix landed in the concurrent delivery dispatch.
Retires:    nothing — there are no instance-level gates for this class; it has one general gate.
Cites:      IMP-0763, IMP-0765
Residual:   The class tag conflates two properties with different remedies (see below), so its
            count of 6 overstates the pressure on the defended one. Not fixed here; see §5.
```

**Re-derived, one member at a time, rather than taken from the tag** — the count that decides
whether more work is needed is exactly the count this skill requires be re-derived:

| Finding | What it actually was | Same property? |
|---|---|---|
| IMP-0145 | A placeholder left in a deployment settings file | **YES** — and the fix for it built check 11 |
| IMP-0175 | Placeholders in the same files; the remedy was wiring the check into the build | **YES** |
| IMP-0763 | A placeholder left in a deployment settings file | **YES** — caught by check 11 |
| IMP-0166 | A pending role id in **solution source XML**, resolvable only by a live write | no — different files, different brace style, different remedy |
| IMP-0243 | A pending profile id in solution source XML; its own finding proposed no mechanism | no — same as above |
| IMP-0244 | A provisioning script missing its exit call and result vocabulary | **not a placeholder finding at all** |

So the defended property has **three** instances across four weeks, and has been green for the last
two of them. The tag says six.

```
CLUSTER B: stale-deferral-uncaught-across-sessions   (x6 as tagged: IMP-0366, IMP-0585,
                                                      IMP-0602, IMP-0610, IMP-0762, IMP-0764)
Altitude:   ALREADY AT CLASS — the hard 14-day check exists, with a 4-day early warning.
Ladder row: none applies; the rung was taken on the second instance.
Becomes:    NOTHING. The four notes were re-tested and re-dated in the concurrent dispatch.
Retires:    nothing.
Cites:      IMP-0764, IMP-0765
Residual:   The automatic re-testing this finding proposes is measured as unimplementable as
            written (below) and is left open with a return condition in §5.
```

**The finding's proposal is withheld, and here is the measurement that forced it.** It asks for the
gate to run a note's own stated discharge check automatically. Those discharge conditions are real
and three of the four are one-line searches — but they are written as **comments** in the config
file, at lines
[675](../../config/revitalise-grant-automation-pipeline.yml#L675),
[697](../../config/revitalise-grant-automation-pipeline.yml#L697),
[717](../../config/revitalise-grant-automation-pipeline.yml#L717) and
[1159](../../config/revitalise-grant-automation-pipeline.yml#L1159).
The gate reads the file with a YAML parser, which discards comments before the gate sees anything.
Measured across the whole corpus of 5 blocked notes: **0 of 5 expose a discharge condition the gate
can read.** A gate built to the proposal as written would find nothing, every time.

I re-measured this twice. My own first pass dumped the notes through the parser, saw no discharge
text, and concluded the conditions did not exist — which was wrong, and a plain search of the file
found four of them. Recorded because the wrong conclusion and the right one look identical in a
report.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | [generate-known-failure-modes.py#L762](../../scripts/generate-known-failure-modes.py#L762), its twin under `.engine/scripts/`, and a new `logs/class-defences.json` | The recurring-class table gains a **Defended by** column, read from a small data file naming the class, the exact property defended, the gate that defends it and the command that proves it green. A row with an entry reads "a gate exists — confirm it is green before proposing another"; a row without one is unchanged | IMP-0763, IMP-0764 | YES — `python3 scripts/generate-known-failure-modes.py --check` | already wired, [build line 113](../../config/revitalise-grant-automation-build.yml#L113) |

**Constraint budget:** 0 of 3 used.

**Seeded with two entries, and deliberately no more.** The file starts with the two defences
measured in this review — check 11 for the settings-placeholder property, check 14 for the re-test
cadence — each scoped to the property actually defended rather than to the whole class name. The
other 54 rows get an empty cell.

**The empty cell means "no defence recorded", never "no defence exists".** That asymmetry is the
safe direction and it is chosen on purpose: under-claiming a defence costs one wasted grep, while
over-claiming one would suppress a gate that genuinely needs building.

---

## 4. Retirements

> Retirement check performed: 85 live constraint rows and 10 already-retired rows reviewed; none
> is currently redundant, because neither cluster produced a new rule that supersedes an existing
> one.

The retirement the brief proposed was checked specifically and **does not exist**: the five earlier
instances of the placeholder class never had one-off gates. The first instance produced the general
check directly, so there is nothing to collapse.

---

## 5. Findings left unprocessed

**Deferred:** none

All three findings in scope are processed. Two things are left open rather than deferred, and both
are recorded on the entries themselves:

**Automatic re-testing of a blocked note stays unbuilt.** The conditions exist but live in comments
the gate cannot read. The honest first step is to move them into a field on the step, which is a
change to a file owned by the delivery agents, not by me. Worth doing when a fifth or sixth note
appears, or the first time one of these causes is found to have quietly cleared.

**The two class names each cover two different mechanisms.** Splitting them would make the
recurrence signal true, but it means re-tagging settled entries, which changes records the system
has already learned from. The column proposed in §3 gets the reader to the right answer without
rewriting history, and is the cheaper half. Revisit if a third class is measured as conflated.

| Finding | Class | Why open | Revisit when |
|---|---|---|---|
| IMP-0764 | `stale-deferral-uncaught-across-sessions` | The automatic-discharge proposal is unimplementable against comments; the instance work is done | a blocked note's cause clears without anyone noticing, or the corpus passes 8 notes |

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 762 | 762 |
| Distinct lessons | 755 | 755 |
| Recurring classes (x≥2) | 56 | **56** — measured, not predicted |
| Rows carrying a recorded defence | 0 | **2** of 56 |
| Digest lines | 707 | **711** |

Regenerated with `python3 scripts/generate-known-failure-modes.py` and confirmed current with
`--check` (exit 0). All figures above are measured after the change, not predicted, because a
predicted digest delta has been wrong here before.

**The registered digest-size claim was corrected in the same change**, from 702 to 711 lines. That
claim drifts as a consequence of regenerating the digest — which every review is required to do —
so the review that causes the drift is the one that fixes it. Three other drifted claims remain and
are **not** mine: two secured-column figures in the development summary and one in the Trustee role
file, all delivery-owned. They are routed, not fixed here.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-18-improvement-review-2.md

Findings processed: 3 NEW  →  2 clusters
Regression check:   3 prior changes audited, 1 class recurred
Proposed:           0 constraints (cap 3), 1 gates/scripts, 0 skill/knowledge edits,
                    0 agent-file edits, 0 retirements
Altitude calls:     0 generalised from instance to class (both classes were already
                    generalised, and both gates fired), 2 proposals withheld as
                    already-satisfied, 1 read-path change
Digest:             will regenerate — 755 lessons, 56 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

Approved by the reviewer (Anna Southern) 2026-09-18 and applied as written.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | `logs/class-defences.json` created, seeded with the two measured defences, each scoped to the sub-property actually defended and each carrying a `not_covered` clause | working tree | IMP-0763, IMP-0764 |
| 1 | `scripts/generate-known-failure-modes.py` + its `.engine` twin: `load_class_defences()`, `defence_cell()`, `md_cell()`, a **Defended by** column, and a heading that no longer asserts a gate is missing for every row | working tree | IMP-0763, IMP-0764 |
| — | Registered digest-size claim corrected 702 → 711 lines in both twins (drift caused by this review's own required regeneration) | working tree | — |

**Measured against the real corpus, not only the fixtures.** 56 recurring-class rows; 2 carry a
defence; both were confirmed by *executing* the command each one names
(`python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml`,
true exit status 0), not by reading the gate's source. The other 54 cells are empty, which is
correct — none of those classes had a defence recorded, and an empty cell claims nothing.

**Both twins were edited and confirmed byte-identical**, because the build runs the `scripts/`
copy: an engine-only edit would not execute while both files still parsed and passed their own
checks.

Entries rejected, with reasons:

| Finding | Rejected because |
|---|---|
| — | None rejected. Two *proposals* were withheld as already-satisfied and the reasoning is recorded on each entry's own `applied_by`, but no finding was rejected — both described real defects that real gates caught |

### What was NOT done, and by whose decision

**The two gate proposals were not built.** Both asked for checks that already exist. Recorded on
the entries rather than silently dropped.

**The class names were not split.** Both cluster tags cover two mechanisms each, which is what
makes their counts overstate the pressure on the defended half. Splitting means re-tagging settled
entries; the `Defended by` column gets the reader to the right answer without rewriting records the
system has already learned from. Left open in §5 with a return condition.
