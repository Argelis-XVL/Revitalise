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

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | build-gate | `scripts/<name>.py` | <one line> | IMP-nnnn | YES — `<command>` |
| 2 | constraint | `constraints/technology/technology-constraints.md` | C-TECH-<nnn> | IMP-nnnn | YES — `<command>` |
| 3 | agent | `agents/<agent>.md` | <one line> | IMP-nnnn | N/A — instruction change |

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
