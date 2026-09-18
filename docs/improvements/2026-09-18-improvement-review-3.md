# Improvement Review — 2026-09-18 (3)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 `NEW` → 2 clusters
**Trigger:** blocker escalation — `IMP-0767`, unread, appended by a build dispatch
**Gate:** `APPROVE IMPROVEMENTS` — §8 is empty and stays empty until the keyword arrives.

---

## 0. The question this review was dispatched to answer

The build dispatch logged `IMP-0767` under `identifier-namespace-collision-across-documents`,
already tracked at x6, making it the 7th. The dispatch asked whether that 7th instance really
shares the property the first six share, or whether a different failure is wearing the same class
tag — because this log's class tags have been measured as polluted before.

**Answer: the tag is polluted, the count of 7 is three unrelated mechanisms, and the blocker itself
is not an instance of the property the class is named for.** The audit that established this also
turned up three *live* collisions of the genuine property, in a namespace no gate reads. That is
the substantive finding of this review, and it is the reason the review proposes anything at all.

---

## 1. Regression check — did the last review's changes work?

The previous review is
[2026-09-18-improvement-review-2.md](2026-09-18-improvement-review-2.md), earlier the same day. It
made one durable change: it created
[`logs/class-defences.json`](../../logs/class-defences.json#L32) and wired it into the digest's
recurring-class table, so a class whose gate already exists says so instead of reading as
undefended.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| `logs/class-defences.json` + the `Defended by` column in [`generate-known-failure-modes.py`](../../scripts/generate-known-failure-modes.py#L171) | 2026-09-18 | `gate-reassures-wrongly` / findings proposing an existing gate | **NO new instance of the original defect** — no finding since has proposed building a gate that already exists | Working, and this review is the first consumer: the class audit below produced exactly the row the mechanism was built to hold |

**Changes whose class recurred after a *prose* fix:** none.
**Changes whose class recurred after a *gate*:** none.

**But the change introduced a gap of its own, and it was logged the same day.** `IMP-0766`
(improvement-agent, unread until this review) records that *nothing validates the record*: the
digest generator is deliberately forgiving, so a row naming a since-renamed check parses perfectly
and goes on telling every agent at activation that the class is defended. That is not a recurrence
— it is the new mechanism's own residual, caught immediately — and it is change 1 below.

Two things follow that are worth stating plainly, because they are the point of doing this section
first:

1. **This review makes the gap worse before it makes it better.** Change 2 adds a third row to
   that record. Adding a row to an unvalidated reassurance file and deferring the validation would
   be the exact shape `IMP-0766` describes, so the two changes ship together or not at all.
2. **The mechanism worked as designed on its first real use.** The class audit below ends in a
   `not_covered` clause naming a namespace with no gate. Before this file existed there was
   nowhere to write that down except prose nobody re-reads.

---

## 2. Clusters and promotion decisions

### 2.1 The class audit — what `x7` actually contains

Every entry carrying `class_instance_of: identifier-namespace-collision-across-documents` was read
and adjudicated against the property the class is named for: **one identifier meaning two different
things.**

| Finding | What actually happened | Same property? |
|---|---|---|
| `IMP-0327` | `FR-056`–`FR-064` etc. allocated independently by two plan documents; the same ids meant different requirements | **YES** — the founding instance |
| `IMP-0339` | The same block again, resolved by retiring one document | **YES** |
| `IMP-0336` | Three plan documents carried no `id-allocation` declaration. **No collision existed** | **NO** — missing declaration |
| `IMP-0576` | Seven commits tagged `wbs:6.9`, a task that is not in the contracted WBS | **NO** — a dangling reference to an id that was never allocated |
| `IMP-0703` | An assumption marker in source cited `A-FIN-03`, which resolves to a different, closed register row | **YES**, but in the `A-nnn` namespace, not the plan namespace |
| `IMP-0707` | The fix record for `IMP-0703` | **NO** — a fix record, not an independent instance |
| `IMP-0767` | Three plan documents carried no `id-allocation` declaration. **No collision existed** | **NO** — missing declaration |

So `x7` is **three mechanisms checked by three different tools**: a genuine plan-id collision (2),
a missing declaration (2), a dangling cross-reference (2 + 1 fix record). The count is real as a
count of entries and misleading as a signal of recurrence, which is precisely what the altitude
rule keys on.

**`IMP-0767` is a missing declaration.** The gate's own output settles it —
`0 identifier(s) allocated more than once` across every document in scope — and each of the three
documents only cites ids allocated elsewhere. **It is not a recurrence of the defended property,
and it needs no new mechanism.**

```
CLUSTER: identifier-namespace-collision-across-documents  (x7 → 3 sub-shapes: IMP-0767 + 6 prior)
Altitude:   INSTANCE, deliberately — and the instance is already fixed
Ladder row: "the gate exists, is wired, and caught it" — no rung applies
Becomes:    logs/class-defences.json gains a row stating the sub-property this gate
            ACTUALLY defends, and a not_covered clause naming the namespace it does not
Retires:    nothing
Cites:      IMP-0327, IMP-0336, IMP-0339, IMP-0767
Residual:   the A-nnn namespace, with three live collisions — logged as IMP-0768, NOT gated
            here, because the naive design measures 60% precise
```

**Why the missing-declaration half needs no new gate either, although it has now happened twice.**
The altitude rule would ordinarily forbid a second instance patch. It does not apply, because there
is no patch: the gate already fails an undeclared document in its own right, and its finding message
already names the exact comment to add including the `none` form. The whole cost of the second
instance was that it was caught at build time rather than at authoring time. That is a latency
problem, not a detection gap, and the cheapest carrier for the instruction is the failure message
the author is already reading — which is where it already is.

### 2.2 What the audit turned up — three live collisions with no gate

Auditing `IMP-0703` meant looking at the `A-nnn` Unvalidated Assumptions Register namespace, and
the genuine property is alive there right now.

Measured across `docs/development/*-dev-summary.md`: **56 distinct `A-nnn` ids carry register rows;
5 appear in more than one document.** Each adjudicated individually:

| Id | Document A | Document B | Verdict |
|---|---|---|---|
| `A-DS-1` | DocuSign connector `apiId` | [the `muted`/`quiet` state treatments](../development/trustee-portal-visual-refresh-dev-summary.md#L2354) | **TRUE collision** — unrelated claims |
| `A-FIN-03` | `REV_FinanceOnly` field-security profile id (closed, verified) | [the `rev_roundfinance` Decimal control id](../development/trustee-portal-visual-refresh-dev-summary.md#L2351) (open) | **TRUE collision** |
| `A-FLOW-13` | [`result()` on a Switch/If](../development/trustee-portal-visual-refresh-dev-summary.md#L2478) (open) | [unscored applications excluded from a score band](../development/emily-review-2026-09-18-dev-summary.md#L254) (open) | **TRUE collision**, authored 2026-09-18 |
| `A-TRM-1` | generated services send a bare PATCH | same claim, successor document | FALSE — legitimate carry-forward |
| `A-TRM-2` | migrating reads loses compile-time enforcement | same claim, successor document | FALSE — legitimate carry-forward |

**5 candidates, 3 true positives, 2 false positives — 60%.**

Two details make this worth acting on rather than noting:

- **`A-FLOW-13`'s two meanings are marked in the same source file.** Both register rows point their
  marker at `REVPortalRoundStatistics-…4E05.json`. An agent resolving that marker by id alone —
  which is what the marker is for — cannot tell which assumption it has found.
- **`IMP-0703`'s fix did not hold, and its closure says it did.** `IMP-0707` allocated a fresh
  `A-FIN-08` for the *source marker* and left the duplicate register **row** in place, so the
  collision survived the entry that closed it. This is the audit question "did the closure evidence
  match the level the defect was visible at?" answering *no*, one review late.

The convention exists and is being followed unevenly: one dispatch
[deliberately allocated `A-PAY-1` rather than reuse `A-FIN-03`](../development/revitalise-payment-capture-dev-summary.md#L132),
citing this very class by name. Three others collided without noticing. **A convention that half
the dispatches follow is the definition of something that should be mechanical.**

```
CLUSTER: identifier-namespace-collision-across-documents, A-nnn half  (IMP-0768, new)
Altitude:   CLASS — same property as the FR-/NFR- half, different namespace, no gate
Ladder row: third-instance generalisation
Becomes:    NOTHING IN THIS REVIEW. Logged with the measurement; the gate is not built
Retires:    nothing
Cites:      IMP-0703, IMP-0707, IMP-0768
Residual:   three live collisions stay live until a delivery dispatch fixes the documents
```

**Why the gate is not built here, when the case for it is this strong.** At 60% precision the
gate would be wrong two times in five on day one, and this project has measured prose-shaped gates
at 48–100% false on five prior occasions. The false positives are not noise to tune away — they
are a *legitimate* authoring pattern (a successor document restating a carried-forward assumption)
that no parser can distinguish from a collision, because the distinction lives in the prose. The
design that reaches 100% requires the carry-forward case to be **declared** — the restating row
naming the document the id came from — which is a value, not a phrase, and is the same instrument
that makes the plan-id gate precise. That convention has to land before the gate, so wiring it now
would teach every agent that this gate cries wolf. The measurement and the design are recorded in
`IMP-0768`.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

**Nothing below has been applied.** Both changes were built and measured in full, then reverted;
the working tree is clean of them and the staged diff sits in this session's scratch directory.
That is stated explicitly because this review's own measurements — the corpus run, the mutation
test, the wiring check — could only be made with the files present, and a reader is entitled to
know how a result was obtained for a file that is not on disk.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | `scripts/verify-class-defences.py` (new) | Every recorded class defence still resolves: the scripts it names exist, the symbols it quotes are still in them, its `wired_at` step is still in that config, its `imp_ids` are real findings, its documents exist, and no class is recorded twice | IMP-0766 | YES — `python3 scripts/verify-class-defences.py` | **`HARD`** at [`config/revitalise-grant-automation-build.yml`](../../config/revitalise-grant-automation-build.yml#L112), new step `class-defences` immediately after `digest-current` |
| 2 | other | `logs/class-defences.json` | A third row, for `identifier-namespace-collision-across-documents`: the sub-property the gate actually defends (both halves), and a `not_covered` clause carrying the `A-nnn` measurement | IMP-0327, IMP-0336, IMP-0339, IMP-0767 | YES — validated by change 1 | N/A |

**Constraint budget: 0 of 3 used.** No new constraint is proposed. Both changes are mechanical,
and a rule saying "do not reuse an identifier" already exists in the only form that has ever
worked here — a gate that fails.

### Change 1 — what was measured

`--selftest`: **11 fixtures, all green.** Two of them exist specifically because a file-existence
check alone would pass them — a renamed function inside a surviving gate, and a step removed from a
surviving config.

**Real corpus: 2 recorded defences, 14 references resolved, 0 findings.** Zero is the correct
answer here and it is also the answer a gate that checks nothing would give, so it was tested
rather than asserted. On a scratch copy of the live record:

| Mutation (the named file/config still exists) | Result |
|---|---|
| `check_settings_content` → a non-existent symbol | `DEFENCE NAMES A MISSING SYMBOL` — exit 1 |
| a real build step name → a removed one | `STEP NOT IN CONFIG` — exit 1 |
| unmutated control | exit 0 |

The live file was confirmed byte-identical afterwards. With change 2's row added the run reports
3 defences and 19 references resolved, exit 0.

Wiring proven: `python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml`
exits 0 with the new step in place and its history section written.

**What it deliberately does not do**, recorded because an over-read of this gate is the same
failure it exists to prevent: it does **not** run `proves_green` (a full build gate over the real
corpus; a red one is a finding about *that* gate, not about this record), it does **not** judge
whether a row's stated property is *adequate* — existence, never adequacy — and it does **not**
require every recurring class to have a row, because the record is opt-in and under-claims by
design.

---

## 4. Retirements

> Retirement check performed: 85 live constraint rows and 62 wired gates reviewed against both
> clusters; none currently redundant.

The honest candidate was the prose convention that a dev-summary must not reuse another document's
assumption id — retiring prose in favour of a gate is exactly the trade this system prefers. **It
is not retired, because the gate that would replace it is not being built** (§2.2). Retiring a
convention while deferring its replacement would leave the `A-nnn` namespace with neither, and
three live collisions already sit in it.

---

## 5. Findings left unprocessed

**Deferred:** none

Both `unread` entries are processed: `IMP-0766` (change 1) and `IMP-0767` (the class judgment).
`IMP-0768` was created by this review and is processed by it.

**States excluded from scope, per activation step 2:** 165 entries in `reviewer-deferred` — each
carries a reason a human accepted — and all `APPLIED` / `REJECTED` entries, whose lessons the
digest already carries. No entry was in `awaiting-approval` or `already-fixed` when this review
opened. One unread blocker does not pull a review of the queue around it.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0768 | `identifier-namespace-collision-across-documents` | Measured at 60% precision without a carry-forward declaration; wiring at that rate teaches agents the gate cries wolf | The carry-forward declaration convention lands in `agents/development-agent.md`, **or** a fourth true collision appears — whichever is first |

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 764 | 765 |
| Distinct lessons | 757 | 758 |
| Recurring classes (x≥2) | 56 | 56 |
| Digest lines | 710 | ~712 |

The one visible change is the `Defended by` cell on the
`identifier-namespace-collision-across-documents` row, [today an em dash](../../logs/known-failure-modes.md#L58)
reading as *no defence recorded*. After change 2 it names the gate, the sub-property it defends,
and the command that proves it green — and, in `not_covered`, the namespace it does not reach.

Regenerated with `python3 scripts/generate-known-failure-modes.py` and confirmed with `--check` at
apply time, followed by `python3 scripts/verify-derived-counts.py`, which the regeneration itself
drifts.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-18-improvement-review-3.md

Findings processed: 2 NEW  →  2 clusters
Regression check:   1 prior change audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 1 gates/scripts, 0 skill/knowledge edits,
                    0 agent-file edits, 0 retirements
Altitude calls:     0 generalised from instance to class, 1 left as notes
Digest:             will regenerate — 758 lessons, 56 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

**Approved by Anna Southern, 2026-09-18: `APPROVE IMPROVEMENTS` — apply as written.**
Applied in full, as written. No narrowing, no withheld change.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | `scripts/verify-class-defences.py` (new, + `.engine` mirror) and the `class-defences` HARD step at [`config/revitalise-grant-automation-build.yml`](../../config/revitalise-grant-automation-build.yml#L112), with its history section | working tree | IMP-0766 |
| 2 | The third row in [`logs/class-defences.json`](../../logs/class-defences.json#L56) | working tree | IMP-0767 |

**Re-verification before applying (activation step 8).** No finding appended after the draft
carried `corrects` against either entry; no new log entry at all. The blocker's fix was still on
disk — all three declarations present, gate exit 0. The routed item was re-measured and is still
live, so it was handed on rather than withheld.

**Disposition simulated before it was written**, on a scratch copy: the gate returned exit 0 with
`0 unread, 0 awaiting-approval`, confirming the blocker trigger this review exists to clear
actually clears. The real file was then changed in exactly the three rows the simulation changed,
verified row by row.

**Both `evidence_grep` needles were grepped before being written** — each matches on one line of
its target.

### Consequential changes made in the same sitting

| Change | Why it belongs to this review |
|---|---|
| [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L504): `62` → `63` `verify-*.py` | A registered derived count that adding a gate mechanically drifts |
| [`scripts/generate-known-failure-modes.py`](../../scripts/generate-known-failure-modes.py#L46): digest `711` → `710` lines | Registered claim that regenerating the digest drifts *as a consequence of compliance* — the review that creates the drift is the one that corrects it |
| `.engine/scripts/` mirrors of both scripts | `scripts/` and `.engine/scripts/` are unsplit duplicates and the build runs the `scripts/` copy; an engine-only edit does not execute |

### Not fixed here, and deliberately so

Three `verify-derived-counts.py` drifts remain, all pre-existing and all in delivery artefacts
owned by another agent: two secured-column counts in the grant-automation Dev Summary (prose 69,
source 75) and one in `REV Trustee.xml` (prose 53, source 59). SOFT, reported, not this review's
to edit.

Entries rejected, with reasons:

| Finding | Rejected because |
|---|---|
| — | none |

### Entry left open

`IMP-0768` stays `NEW`, carrying a `deferred_reason` recording the 60% measurement and a
`revisit_when` naming who can discharge it. An honest open entry beats a closed one nobody tested
— and the three live collisions it names are real, unfixed, and routed to development-agent.
