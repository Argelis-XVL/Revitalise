# Improvement Review — 2026-09-22 (4)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 1 `NEW` → 1 cluster
**Trigger:** blocker escalation — one unread `blocker` entry, routed immediately and not batched
**Gate:** `APPROVE IMPROVEMENTS`

**Scope.** This review processes the single unread blocker (`IMP-0824`) and nothing else, per
`agents/improvement-agent.md` activation step 2 and the one-unread-blocker rule (`IMP-0183`). The
twelve other `unread` entries and the two blockers already parked against
[`docs/improvements/2026-09-22-improvement-review-3.md`](2026-09-22-improvement-review-3.md) are
named in §5 and were not read or re-derived.

---

## 1. Regression check — did the last review's changes work?

The class here is `stale-claim-contradicting-rechecked-source`, now at **x17**. The audit below
covers every prior change applied against that class, which is the set that matters.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| `skills/how-to-verify-a-platform-contract.md` §12 — the artefact/question table, three rows (static capture, rendered pack, trigger schema) | 2026-09-17 | `stale-claim-contradicting-rechecked-source` | **YES — the entry this review processes** | **Wrong altitude — but not in the way the template assumes.** See below |
| `templates/deployment-summary-template.md` — live version column | 2026-09-08 | same class, deploy-reporting half | NO | Working — leave alone |
| `agents/pm-agent.md` — the no-v0.6 rule | 2026-09-10 | same class, plan-of-record half | NO | Working — leave alone |
| `knowledge/technology/dataverse.md` — profile membership is per-environment config | 2026-09-10 | same class, environment half | NO | Working — leave alone |
| `scripts/verify-wbs-chain.py` — every task id cited in `contract/*.json` resolves | 2026-09-11 | same class, contract half | NO | Working — the one mechanised member of this class |

**Changes whose class recurred after a *prose* fix:** the artefact/question table in
`how-to-verify-a-platform-contract.md` → the template says escalate to a mechanical gate. **A gate candidate was designed and measured, and it is rejected on the number,
not on taste** — see §2's `Residual`. The escalation instead takes the other route the ladder
offers: the rule moves from a reference section nobody was triggered to open into an **activation
step**, which is the read-path row of `skills/how-to-promote-a-finding.md` §1.

**Changes whose class recurred after a *gate*:** none.

---

## 2. Clusters and promotion decisions

```
CLUSTER: stale-claim-contradicting-rechecked-source  (x17; this review processes IMP-0824)
Altitude:   CLASS — 17 instances of "a claim was checked against something one level removed
            from the artefact that governs it". The three most recent (IMP-0736, IMP-0740,
            IMP-0744) were fixed by prose in exactly the section this instance walked past.
Ladder row: TWO rows, and the second is the escalation:
              "An agent had the information and still did the wrong thing" -> skill edit
              "The system's own memory failed"                             -> a read-path change
Becomes:    1. skills/how-to-verify-a-platform-contract.md — section 12 gains a row for the
               document the dispatch is IMPLEMENTING FROM, plus a new subsection 12c naming the
               name-resemblance tell.
            2. agents/development-agent.md — the "Steps and Inline Skills" trigger table gains a
               row that FIRES for this kind of work. Measured: not one of its seven existing
               rows fires on "implement a UI item whose acceptance is a supplied document", so
               change 1 on its own lands in a file this dispatch had no trigger to open.
Retires:    nothing — see section 4
Cites:      IMP-0824 (and the prose precedent it recurred against: IMP-0736, IMP-0740, IMP-0744)
Residual:   THREE things this does not cover, and one rejected design.
            (a) The rejected gate. The obvious mechanical form is "a plan line that specifies
                behaviour from a supplied source document must cite that document". Measured
                over the corpus: 49 lines across 5 plan documents cite a docs/Import/ path, and
                9 distinct binary sources are cited. The defective row ALREADY CITED THE PDF, by
                full path, in its own last column — so that gate scores 0 true positives on the
                one known instance of the defect. Rejected on that number.
            (b) No gate can compare a rendered screen's section order against a PDF's section
                order. That is a semantic content match, and it would require the pack's content
                to be carried in source.
            (c) The instance is now guarded by a source-level order assertion added by the
                fixing dispatch (ApplicationDetailPage.test.tsx asserts the literal heading list).
                Nothing ties that expected list back to the PDF, so a future paraphrase-sourced
                edit could rewrite the list and its explaining comment together — which is
                IMP-0446's shape. That residual is real and is not closed by this review.
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | skill | [`skills/how-to-verify-a-platform-contract.md`](../../skills/how-to-verify-a-platform-contract.md#L720) | §12's table gains a row for a plan/spec/brief's paraphrase of a source document, and a new §12c states the rule and the name-resemblance tell | IMP-0824 | NO — instruction change | N/A |
| 2 | agent | [`agents/development-agent.md`](../../agents/development-agent.md#L222) | The "Steps and Inline Skills" table gains a trigger row: implementing to an item whose acceptance is "it matches a supplied source document" loads §12c | IMP-0824 | NO — instruction change | N/A |

**Constraint budget:** 0 of 3 used.

### The exact text proposed

**Change 1a — new row at the end of `how-to-verify-a-platform-contract.md` §12's artefact/question table:**

| A **plan, spec or brief's paraphrase** of a source document it cites | that a requirement exists, and which document governs it | what that document LITERALLY says — a summary line is built to decide priority, not to reproduce content | a screen's section order reported delivered against a one-line summary; a live check reopened it |

**Change 1b — new subsection, placed after §12b:**

> ### 12c. The document you are implementing FROM is one of these artefacts too
>
> The rows above are all evidence somebody went and gathered. The same rule governs the document
> the dispatch is working **from** — the plan, the spec, the feedback log, the brief. **A plan is
> built to decide what to do and in what order. It is not built to reproduce the content of the
> source documents it cites**, so a line summarising a supplied pack, form or report settles which
> document governs the claim and nothing at all about what that document says.
>
> So where an item's acceptance is *"it matches the supplied `<document>`"*, open that document and
> check the claim against it page by page **before** reporting the item delivered. The plan's
> summary line is the pointer, not the answer — and citing the source is not the same act as
> reading it.
>
> **The tell is a name that resembles a name you already have.** Where a source document's own
> section or field label closely resembles an existing component, panel or column name in the
> codebase, a name-resemblance match will silently substitute for a content match, and it will feel
> like a confirmation rather than a guess. Two labels reading alike is the condition under which
> the source must be opened, not the condition under which it may be skipped.

**Change 2 — new row in the "Steps and Inline Skills" table, inserted *before* the
"Fixing a defect a Test Report raised" row** so that the paragraph beginning *"On that last row"*
still refers to the row it explains:

| **Implementing an item whose acceptance is "it matches a supplied source document"** | **`skills/how-to-verify-a-platform-contract.md` §12c** — open the cited document, never the plan's summary of it |

---

## 4. Retirements

> Retirement check performed: 86 live constraint rows and 10 already-retired rows reviewed
> (derived with `grep -rh '^| C-' constraints/ --include='*.md' | wc -l` and
> `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l`), plus the two sections of
> `how-to-verify-a-platform-contract.md` this review edits. None currently redundant: this review
> adds no constraint, and the new §12c states a property that neither the artefact/question table
> nor §12a's authored-statement rule already covers — §12a governs an artefact's own authored text,
> §12c governs a second-hand summary of a different artefact.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0798, IMP-0799, IMP-0800, IMP-0801, IMP-0802, IMP-0803, IMP-0811, IMP-0812,
IMP-0818, IMP-0819, IMP-0822, IMP-0823, IMP-0825

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| The twelve ids above, plus IMP-0825 | various | Out of scope. One unread blocker summons a review of **that blocker**, not of the queue around it (`IMP-0183`). None is `blocker` severity, so none carries its own immediate trigger | the batch trigger (30 `unread`/`awaiting-approval`) fires, or a feature completes |
| IMP-0820, IMP-0821 | `platform-contract-guessed-not-groundtruthed` | **Not deferred by this review and not this review's to touch.** Already `awaiting-approval` against `docs/improvements/2026-09-22-improvement-review-3.md`. The remedy is the keyword on that document, not another session | — |

**IMP-0824 itself is processed but NOT closed.** Its `observable_at` is `V4`: the reproduction is a
human opening the deployed screen and comparing it page by page against the source PDF. Nobody in
this session can run that, and reading source plus the new order assertion reaches V1/V2 only. So
per `agents/improvement-agent.md` step 6's disposition table, it is drafted as a deferral from the
start rather than as a closure: the rule change lands, the entry stays `NEW` with a
`deferred_reason` and a `revisit_when` naming the observation that would close it. That is the
gate's own second discharge, and it clears the blocker rung exactly as a closure would.

---

## 6. Digest impact

| | Before | After (expected) |
|---|---|---|
| Log entries | 820 | **821** — one entry appended: IMP-0825, this session's own capture of a gate false positive hit while drafting this document |
| Distinct lessons | 812 | **813** |
| Recurring classes (x≥2) | 60 | 60 — unchanged |

No status moves to `APPLIED`. The digest has already been regenerated (the capture contract
requires it after any append) and `--check` reports it current at 821 entries. The figures above
are measured, not predicted.

One registered derived count drifted as a consequence: the `CURRENT SIZE` sentence in
`scripts/generate-known-failure-modes.py` said 739 lines against an actual 741. Corrected in both
the instance copy and its `.engine` twin, and `verify-derived-counts.py` is green.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-22-improvement-review-4.md

Findings processed: 1 NEW  →  1 cluster
Regression check:   5 prior changes audited, 1 class recurred
Proposed:           0 constraints (cap 3), 0 gates/scripts, 1 skill/knowledge edits,
                    1 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 0 left as notes
Digest:             regenerated — 813 lessons, 60 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

**Applied 2026-09-23** on `APPROVE IMPROVEMENTS`, as part of a batch applying six parked reviews.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | `skills/how-to-verify-a-platform-contract.md` — §12's artefact table gains the paraphrase row; new §12c added after §12b, verbatim from §3 | 2026-09-23 | none — see below |
| 2 | `agents/development-agent.md` — the "Steps and Inline Skills" table gains the §12c trigger row, inserted **before** the "Fixing a defect a Test Report raised" row so the *"On that last row"* paragraph still refers to the row it explains | 2026-09-23 | none — see below |

Entries rejected, with reasons:

| Finding | Rejected because |
|---|---|
| — | none |

**IMP-0824 is processed and APPLIED as a rule change, but the entry is DEFERRED, not closed** —
exactly as §5 drafted it. `observable_at` is `V4`: the reproduction is a human opening the deployed
screen and comparing it page by page against the source PDF. Nobody in this session can produce that
observation, so the entry keeps `status: NEW` and gains a `deferred_reason` recording that both
changes landed, plus a `revisit_when` naming the observation that would close it. That is the gate's
own second discharge and it clears the blocker rung exactly as a closure would.

This review's two targets are both **symlinks into the `.engine` submodule**, so publishing them is
a commit and push in `.engine` first, then the instance pointer bump — not one ordinary commit.
