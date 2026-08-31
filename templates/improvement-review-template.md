# Improvement Review — <YYYY-MM-DD>

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** <n> `NEW` → <n> clusters
**Trigger:** feature completion | reviewer request | ≥10 NEW entries | blocker escalation
**Gate:** `APPROVE IMPROVEMENTS`

---

## 1. Regression check — did the last review's changes work?

The first section, deliberately. A review that proposes new rules without auditing the last
set's effect is how a constraint file grows to 57 rows with zero retirements.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| <e.g. C-TECH-049 + verify-workflow-description-length.py> | <date> | `platform-field-length-limit-unenforced` | YES — IMP-0009 | **Wrong altitude.** Instance patch; class needs one gate |
| <change> | <date> | `<class>` | NO | Working — leave alone |

**Changes whose class recurred after a *prose* fix:** <list> → escalate to a mechanical gate.
**Changes whose class recurred after a *gate*:** <list> → the gate exists but did not fire.
Log each as a new `gate-cannot-fail` finding; a gate that cannot fire is a defect, not a gap.

---

## 2. Clusters and promotion decisions

One block per cluster, in the format `skills/how-to-promote-a-finding.md` §5 specifies.
`Residual` is mandatory — every promotion leaves something uncovered, and naming it is the
difference between a gate and a false sense of one.

```
CLUSTER: <class_instance_of>  (x<n>: IMP-nnnn, IMP-nnnn)
Altitude:   INSTANCE | CLASS | LAW — <why>
Ladder row: <which row of the ladder applies>
Becomes:    <the concrete change: file + what it does>
Retires:    <instance gates / constraints this replaces, or "nothing">
Cites:      IMP-nnnn, …
Residual:   <what this still does not cover, and why that is acceptable>
```

---

## 3. Proposed changes

**Copy this line into your own §3, verbatim, before the table.** It is what makes the gate block's
arithmetic checkable, and `verify-review-document.py`'s `PROPOSED-COUNT` check runs **only** on a
document that carries it:

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | `scripts/<name>.py` | <one line> | IMP-nnnn | YES — `<command>` | `HARD` at `config/<slug>-build.yml` L<n> |
| 2 | constraint | `constraints/technology/technology-constraints.md` | C-TECH-<nnn> | IMP-nnnn | YES — `<command>` | N/A |
| 3 | agent | `agents/<agent>.md` | <one line> | IMP-nnnn | N/A — instruction change | N/A |

### The `Wiring` column is REQUIRED on every row of type `script`

One of: **`HARD`** · **`SOFT (--warn-only)`** · **`SUITE_GATE_EXEMPT` + the reason** ·
**`already wired`** — and for the first two, name the config file and line the step sits at. Any
other type may write `N/A`.

**A `script` row with this column blank is an incomplete proposal, not a tidy one.**
`scripts/verify-build-config.py`'s suite-gate rung makes an unwired `verify-*.py` a **red
preflight**, so "write the gate now, wire it later" is not a smaller change than wiring it — it
is the same change plus a broken build in between. Deciding the wiring is also what forces the
question the register exists for: a gate that measures red over pre-existing debt the dispatch
does not own needs a `config/gate-baselines.json` entry in the same change, or it must not be
wired HARD at all (`IMP-0439`, `IMP-0491`).

### The `Type` column is a CLOSED vocabulary, and a per-type figure counts ROWS

Eight values, and no others: `constraint` · `constraint-amendment` · `script` · `skill` ·
`knowledge` · `agent` · `template` · `other`. A change that edits a script is `script` whether you
think of it as a gate, a build-gate or a verifier.

**§9's `Proposed:` figures count the numbered ROWS of this table, by their `Type`, never the number
of FILES touched.** Three rows editing two scripts is `3 gates/scripts`, not 2. The mapping is
fixed:

| `Type` | Counted in §9 as |
|---|---|
| `constraint` | `<n> constraints` |
| `constraint-amendment` | `<n> constraint amendment` |
| `script` | `<n> gates/scripts` |
| `skill` + `knowledge` | `<n> skill/knowledge edits` (one figure for both) |
| `agent` | `<n> agent-file edits` |
| `template` | `<n> template edits` |

Both rules exist because the arithmetic was undecidable without them, and the measurement is on
the record (`IMP-0397`). This check has been attempted four times. Review 30 built it, measured 18
findings / 0 true, and diagnosed a parsing defect. Scoped correctly it still failed — **17
findings across 24 documents, and 15 across 22, with roughly one true positive between them** —
because the `Type` column was an **open vocabulary of 65 distinct values**, 20 of them mapping to
no figure at all, and because the gate block counted files while the table counted rows. Neither
is a parsing problem. Review 31's §9 then claimed `1 skill/knowledge edits` over three such rows,
and the reviewer's approval message quoted that wrong figure back — so the miscount reached the
authorisation record before anyone noticed.

**Constraint budget:** <n> of 3 used.
Any constraint whose "Mechanically verifiable?" is NO must be justified here or downgraded to
a knowledge-file line — an unverifiable constraint is a comment.

---

## 4. Retirements

| ID / file | What it was for | Why retired | Replaced by | Coverage proven? |
|---|---|---|---|---|
| C-TECH-<nnn> | <summary> | superseded by the general gate | <the general gate> | YES — the retired gate's known-bad fixtures still fail under the replacement |

If nothing is being retired, say so explicitly and confirm the check was made:

> Retirement check performed: <n> constraints reviewed, none currently redundant because <reason>.

---

## 5. Findings left unprocessed

No silent caps. Anything deferred is named here with a reason.

**Deferred:** IMP-nnnn, IMP-nnnn

**That line is REQUIRED, and it is read by a gate.** `scripts/verify-improvement-log.py`
(`DEFERRED_DECLARATION`) takes it as this document's machine-readable disposition: the ids named
there are declared *not processed* for the **whole document**, so you may mention them anywhere
else — including a paragraph whose purpose is context rather than disposition — without the check
reading it as an unstamped processing claim.

Two things it is not:

- **Not the list of ids left OPEN.** An entry can be processed and not closed — a V5 defect whose
  fix is on disk but whose reproduction nobody in this session can run. That state is recorded on
  the entry itself with `reviewed_in` plus `deferred_reason`, never here. Conflating the two makes
  this field as loose as the prose it replaced.
- **Not an override of a processing claim.** An id on this line that also appears in a `Cites:`
  line or a change-table row still counts as processed — the stronger signal wins.

Write the line even when it is empty (`**Deferred:** none`). Before this field existed, a review
declared non-scope in prose and the check inferred intent by matching a phrase against a cue list,
which cost one review three rewordings of this section and fired on ids it had just gone on record
as not taking (`IMP-0471`, third instance). Prose still works as a fallback; this line always does.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-nnnn | `<class>` | single instance; needs a second to establish the class | a second instance appears |

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | <n> | <n> |
| Distinct lessons | <n> | <n> |
| Recurring classes (x≥2) | <n> | <n> |
| Digest lines | <n> | <n> |

Regenerated with `python3 scripts/generate-known-failure-modes.py`; confirmed current with
`--check`. The digest is the read path — a finding that never reaches it teaches nobody.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/<date>-improvement-review.md

Findings processed: <n> NEW  →  <n> clusters
Regression check:   <n> prior changes audited, <n> classes recurred
Proposed:           <n> constraints (cap 3), <n> gates/scripts, <n> skill/knowledge edits,
                    <n> agent-file edits, <n> retirements
Altitude calls:     <n> generalised from instance to class, <n> left as notes
Digest:             will regenerate — <n> lessons, <n> recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

Filled in **after** `APPROVE IMPROVEMENTS`, not before.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | <change> | <commit sha> | IMP-nnnn, … |

Entries rejected, with reasons:

| Finding | Rejected because |
|---|---|
| IMP-nnnn | <reason — this is a decision, and it is recorded, not silently dropped> |
