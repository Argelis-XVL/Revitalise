# Improvement Review — 2026-09-23 (4)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 `NEW` → 2 clusters
**Trigger:** blocker escalation — one unread `blocker` entry, routed immediately per
[`agents/WORKFLOW.md`](agents/WORKFLOW.md) → *Processing triggers*
**Gate:** `APPROVE IMPROVEMENTS`

**Scope, stated up front.** This review processes **IMP-0843**, the single entry in state
`unread` with severity `blocker`, plus **IMP-0844**, which this review logged itself while grepping
IMP-0843's premises. The queue also holds 24 other `unread` entries and six parked
blockers belonging to other reviews; §5 names them (`IMP-0183`: one unread blocker summons a
review of itself, not of the queue around it).

**This is a mechanical application, and the review is short on purpose.** The obligation was
specified in the approved architecture document before the column was built, the exact row was
drafted by the building dispatch, and the only reason a review exists at all is that the file
lives under `constraints/` and a write-protection hook correctly refused a delivery agent's edit.

**One thing the reviewer needs before reading any further: this change alone does NOT turn the
build green.** The dispatch brief that summoned this review said IMP-0838 had been *"processed and
applied"* by [2026-09-23 improvement review 3](docs/improvements/2026-09-23-improvement-review-3.md).
It has been processed; it has **not** been applied — that review is parked at its own gate awaiting
your keyword, and its two rows are not in the register. Measured, not inferred, before drafting
anything:

```
$ grep -c "rev_derivedcity" constraints/domain/special-category-register.yml     → 0
$ grep -n  "rev_localauthority" constraints/domain/special-category-register.yml → (no match)
$ python3 scripts/verify-domain-invariants.py src/solutions/RevitaliseGrantAutomation
  ERROR: UNADJUDICATED-SECURED — rev_applicant.rev_derivedcity …
  ERROR: UNADJUDICATED-SECURED — rev_applicant.rev_localauthority …
  ERROR: UNADJUDICATED-SECURED — rev_applicant.rev_localauthoritystatus …
  DOMAIN INVARIANTS: FAILED — 3 violation(s) across 21 registered and 78 secured column(s)
```

Three errors, not one. This review can only clear the first. **Two keywords are needed to unblock
the `domain-invariants` step — this document and review 3** — and review 3's rows are not
re-derived or applied here, because applying an unapproved draft is the one thing the gate exists
to prevent. Logged as `IMP-0844`, whose lesson is one sentence:
**processed and applied are two different states, and `awaiting-approval` is the first one.**

---

## 1. Regression check — did the last review's changes work?

The last review to apply anything was
[2026-09-22 improvement review 2](docs/improvements/2026-09-22-improvement-review-2.md). Reviews
[2026-09-23 (1)](docs/improvements/2026-09-23-improvement-review.md),
[(2)](docs/improvements/2026-09-23-improvement-review-2.md) and
[(3)](docs/improvements/2026-09-23-improvement-review-3.md) are drafted and parked, so they have
applied nothing and there is nothing of theirs to audit.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [`agents/pipeline-agent.md`](agents/pipeline-agent.md) — *"Before you dispatch ANOTHER agent to fix what a finding describes"* | 2026-09-22 | `build-blocked-by-the-finding-it-remediates` | NO | Working — leave alone |
| [`agents/improvement-agent.md`](agents/improvement-agent.md) activation step 6 — the `observable_at` CLOSE/DEFER table | 2026-09-22 | `draft-states-a-disposition-the-closure-rules-forbid` | NO, and exercised again here | Working — leave alone |

Measured by classifying every entry carrying either `class_instance_of`: three members
(`IMP-0814`, `IMP-0815`, `IMP-0817`), all `APPLIED`, all timestamped before the changes landed. No
member of either class has been appended since.

**Changes whose class recurred after a *prose* fix:** none.
**Changes whose class recurred after a *gate*:** none.

**The durable success this review is an instance of.** The register's own *"HOW TO ADD A COLUMN"*
block was rewritten on 2026-09-06 to say plainly that the agent securing a column cannot write the
register and must propose the row instead. That is exactly what happened: the building dispatch
attempted the write, was refused by `.claude/hooks/protect-system-rules.py`, drafted the row in
[`docs/development/city-derivation-dev-summary.md`](docs/development/city-derivation-dev-summary.md)
§6, logged the blocker and stopped. Second consecutive time in two days. The control, the
documented route around it, and the capture all worked — the finding is the system running
correctly, not a defect.

---

## 2. Clusters and promotion decisions

```
CLUSTER: pending-adjudication-entry-needed  (x1 in scope: IMP-0843; x2 in the class)
Altitude:   INSTANCE, deliberately. Ladder row 1 — "one instance, specific to one feature,
            no general mechanism". The general mechanism already exists and already fired,
            by name, within one dispatch of the column being built.
Becomes:    one row in constraints/domain/special-category-register.yml pending_adjudication:,
            with the rationale as a dated comment block.
Retires:    nothing.
Cites:      IMP-0843 (IMP-0598 and IMP-0761 as the precedent this follows)
Residual:   This closes the ADJUDICATION DEBT, not the adjudication. The row records that the
            column is secured and that nobody with the authority to classify it has done so in
            writing. The Domain Owner / Compliance Lead still owns that call. And it clears
            ONE of the three errors the gate reports — see the note at the top.
```

```
CLUSTER: dispatch-brief-asserts-unverified-fact  (x1 in scope: IMP-0844; x7 in the class)
Altitude:   NOTHING — ladder row 1. The rule that would have to be added already exists and
            already worked: agents/improvement-agent.md step 6 mandates grepping the premises
            of every finding a review processes, and that grep is what caught this. A class
            with a working defence does not get a second rule for the same property.
Becomes:    the record itself, and the 3->2 wording in §3 that it forced.
Retires:    nothing.
Cites:      IMP-0844
Residual:   Nothing reads a dispatch brief, and nothing reasonably could. The receiving
            agent's own premise-grep stays the only defence for this class.
```

**Duplicate check (`skills/how-to-promote-a-finding.md` §3a), measured:** the class
`pending-adjudication-entry-needed` has exactly two members in the log, `IMP-0838` and `IMP-0843`,
and **neither is `APPLIED`**. No finished work is being re-proposed here.

### Why no rule change follows from the blocker

The second instance of a class normally forbids another instance patch and demands
generalisation (§2 of the promotion skill). It does not apply here, because **the general
mechanism is what produced both findings**. `C-DOM-033` is enforced by
`scripts/verify-domain-invariants.py`, it failed by column name with the exact remedy in its
message, and the handoff it required is written into the register's own header. A finding whose
entire content is *"the machinery worked, now do the human step it routes to"* produces no rule
change; adding one would be the speculative-constraint case §4 rules out.

### The one thing measured against the finding's own wording

The Dev Summary drafts the row inside a three-line comment block and the finding's
`proposed_change` writes a bare `{ entity, name }` pair. Measured rather than transcribed:
`verify-domain-invariants.py` reads only `entity` and `name` from each row and ignores anything
else, so both forms validate. The applied form follows the file's established convention — a bare
pair under a dated comment block — and preserves the Dev Summary's reason text verbatim in that
comment.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | constraint-amendment | [`constraints/domain/special-category-register.yml`](constraints/domain/special-category-register.yml) | Add `rev_applicant.rev_derivedcity` to `pending_adjudication:`, under a dated comment block recording why | IMP-0843 | YES — `python3 scripts/verify-domain-invariants.py src/solutions/RevitaliseGrantAutomation` drops from 3 violations to 2, and the `rev_derivedcity` ERROR disappears by name |

**Constraint budget:** 0 of 3 used. The change adds no constraint row; it amends a data file an
existing HARD constraint already reads.

**Note the verification wording.** It is *3 → 2*, not *3 → 0*. Claiming a green gate here would be
the `gate-reassures-wrongly` class this log carries 35 instances of.

### The exact text proposed

Appended to `pending_adjudication:`, after the block added on 2026-09-18. It does not disturb the
anchor review 3's change 1 appends against, so the two apply in either order:

```yaml
  # ── Added 2026-09-23 (IMP-0843), wbs:4.7 / CO-007 / EF-03, city-derivation ─
  # Built and secured in the city-derivation dispatch (TAD
  # docs/architecture/city-derivation-architecture.md §6, ADR-005). NOT an open Article 9
  # question: it is the third location attribute on rev_applicant, mirroring the
  # already-secured rev_towncity and rev_locationarea above — a geographic quasi-identifier,
  # secured because it narrows who a person is, not because of an Article 9 category.
  # Released to REV Admin and REV Service Automation by REV_TrusteeRestricted; trustees are
  # excluded by non-membership, unchanged (2026-09-17 EF-02: trustees see no location at all).
  # development-agent drafted this row in docs/development/city-derivation-dev-summary.md §6
  # and was correctly refused the write by .claude/hooks/protect-system-rules.py — the
  # register's own "HOW TO ADD A COLUMN" block working as written, not a defect.
  - { entity: rev_applicant, name: rev_derivedcity }
```

**Not proposed here, deliberately:** the header's *"these 51 columns"* sentence, which the gate now
contradicts at 58. It is review 3's change 2 and is left to that document rather than fixed twice.

---

## 4. Retirements

> Retirement check performed: 86 live constraint rows reviewed against this cluster, none
> currently redundant.

Derived, not typed: `grep -rh '^| C-' constraints/ --include='*.md' | wc -l` → 86 live;
`grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` → 10 retired.

`C-DOM-033` is the constraint in play and is the opposite of a retirement candidate. The nearest
thing to a retirement here is a discharge rather than a retirement: every row in
`pending_adjudication:` is a debt that leaves the list when its owner decides it, and this review
adds one rather than clearing any. That backlog is the Domain Owner's.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0798, IMP-0799, IMP-0800, IMP-0801, IMP-0802, IMP-0803, IMP-0811, IMP-0812,
IMP-0818, IMP-0819, IMP-0822, IMP-0823, IMP-0825, IMP-0826, IMP-0827, IMP-0828, IMP-0829,
IMP-0832, IMP-0833, IMP-0836, IMP-0837, IMP-0839, IMP-0841, IMP-0842

**States excluded from this review, and why:**

| State | Count | Why excluded |
|---|---|---|
| `unread`, non-blocker | 24 | Out of scope. A blocker trigger summons a review of the blocker, not of the queue (`IMP-0183`). These wait for a batch review. |
| `awaiting-approval`, blocker | 6 | Already processed by reviews parked at their own gates. The remedy is a keyword, not a session (`IMP-0154`). Named below. |
| `awaiting-approval`, non-blocker | 3 | Same — parked at documents this review does not touch (IMP-0830, IMP-0834, IMP-0840). |
| `reviewer-deferred` | 180 | Carry a `deferred_reason` a human accepted. Left alone. |

**The six parked blockers, and the document each waits on** — these need a keyword from you, and
none is re-derived here:

| Finding | Parked at |
|---|---|
| IMP-0820, IMP-0821 | [`docs/improvements/2026-09-22-improvement-review-3.md`](docs/improvements/2026-09-22-improvement-review-3.md) |
| IMP-0824 | [`docs/improvements/2026-09-22-improvement-review-4.md`](docs/improvements/2026-09-22-improvement-review-4.md) |
| IMP-0831 | [`docs/improvements/2026-09-23-improvement-review.md`](docs/improvements/2026-09-23-improvement-review.md) |
| IMP-0835 | [`docs/improvements/2026-09-23-improvement-review-2.md`](docs/improvements/2026-09-23-improvement-review-2.md) |
| **IMP-0838** | [`docs/improvements/2026-09-23-improvement-review-3.md`](docs/improvements/2026-09-23-improvement-review-3.md) — **the one that also blocks this feature's build** |

**One flag carried forward, still true:** `IMP-0800` sits in the deferred list and the validator
warns it is corrected by `IMP-0801` with no review having processed it, which will fail the next
build that reaches the `unit-tests` step. It is a batch-review item and cannot be cleared by
stamping a `deferred_reason` on it.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 839 | 840 — IMP-0844, logged by this review |
| Recurring classes (x≥2) | 62 | 62 — IMP-0844 joins `dispatch-brief-asserts-unverified-fact` (x6 → x7) |

Regenerate with `python3 scripts/generate-known-failure-modes.py` and confirm with `--check`.

**Disposition simulated before parking**, per activation step 8: on a scratch copy, IMP-0843 was
set `APPLIED` with its `evidence_grep` needle and the gate re-run. The unread-blocker trigger
clears. `observable_at` is `V1`, which is the CLOSE/DEFER table's first row — **CLOSE**,
`evidence_grep` is sufficient and no `reobserved` record is required or should be written. The
real log was restored and confirmed byte-identical with `diff`.

**The digest was regenerated at draft time, not held to approval** (`IMP-0702`): an entry was
appended, and a build dispatched before the keyword would otherwise inherit a stale digest.
`--check` is green at 840 entries.

### Gate results carried out of this session, none of them this review's to fix

| Gate | Result | Whose |
|---|---|---|
| `verify-derived-counts.py` | 4 drifted claims → **3**. The digest line-count claim in `scripts/generate-known-failure-modes.py` drifted 741 → 756 as a consequence of the regeneration this review is required to perform, so this review corrected it — **in both copies**, `scripts/` and `.engine/scripts/`, since the two are unsplit duplicates | this review's, and done |
| `verify-derived-counts.py` | the other 3: `docs/development/revitalise-grant-automation-dev-summary.md` says 75 secured columns at two places (source: 78), and `Roles/REV Trustee/REV Trustee.xml` says 59 (source: 62). SOFT, pre-existing, and both are delivery-owned prose about the same securing passes this register records | development-agent |
| `verify-review-document.py` | 5 errors across 108 documents, **all in reviews from 2026-08-21 to 2026-08-31**; none in this document | pre-existing debt, batch review |
| `verify-improvement-log.py` | red on the parked-review trigger only. The unread-blocker trigger this review was summoned by clears | your keyword ×2 |

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-23-improvement-review-4.md

Findings processed: 2 NEW  →  2 clusters
Regression check:   2 prior changes audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 1 constraint amendment, 0 gates/scripts,
                    0 skill/knowledge edits, 0 agent-file edits, 0 retirements
Altitude calls:     0 generalised from instance to class, 2 left at instance
Digest:             will regenerate — 840 lessons, 62 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

**Applied 2026-09-23** on `APPROVE IMPROVEMENTS`, as part of a batch applying six parked reviews.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | `constraints/domain/special-category-register.yml` — `rev_applicant.rev_derivedcity` added to `pending_adjudication:`, under the dated comment block verbatim from §3 | 2026-09-23 | IMP-0843 |
| 2 | no file change — IMP-0844 closes against this document | 2026-09-23 | IMP-0844 |

Entries rejected, with reasons:

| Finding | Rejected because |
|---|---|
| — | — |

**The 3 → 2 wording in §3 was correct when written, and the batch overtook it.** This review was
applied alongside [review 3](2026-09-23-improvement-review-3.md), which supplies the other two rows,
so the measured result is not 2 remaining violations but none:

```
DOMAIN INVARIANTS: PASS — 21 special-category column(s) verified.
  UNADJUDICATED-SECURED coverage: 78 secured = 17 registered + 61 pending adjudication, 0 undeclared
```

§3's refusal to claim a green gate was the right call on the evidence it had — this review genuinely
could not clear the other two, and claiming otherwise would have been the `gate-reassures-wrongly`
class. The gate is green because **both** keywords arrived, which is precisely what the note at the
top of this document said was needed.

**IMP-0844's premise was re-verified at apply time and held.** The dispatch brief for this review
asserted IMP-0838 had been *"processed and applied"*; it had been processed only. The batch brief
that applied all six made the opposite and correct claim — that review 3 was parked and unapplied —
and the register measured empty of both rows immediately before they were written. The finding's
lesson stands as recorded: **processed and applied are two different states, and
`awaiting-approval` is the first one.**

No rule change follows, as §2 decided: `agents/improvement-agent.md` step 6 already mandates the
premise-grep that caught this, and that grep is what caught it again here. A class with a working
defence does not get a second rule for the same property.
