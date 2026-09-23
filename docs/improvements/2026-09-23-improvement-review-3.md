# Improvement Review — 2026-09-23 (3)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 `NEW` → 2 clusters
**Trigger:** blocker escalation — one unread `blocker` entry, routed immediately per
[`agents/WORKFLOW.md`](agents/WORKFLOW.md) → *Processing triggers*
**Gate:** `APPROVE IMPROVEMENTS`

**Scope, stated up front.** This review processes **IMP-0838 only**, plus **IMP-0840**, which this
review logged itself while editing the file IMP-0838 names. IMP-0838 is the single entry in state
`unread` with severity `blocker`. The queue also holds 21 other `unread` entries and five parked
blockers belonging to other reviews; §5 names them and why they are not in scope
(`IMP-0183`: one unread blocker summons a review of itself, not of the queue around it).

**This is a mechanical application, and the review is short on purpose.** The obligation was
specified in the approved architecture document before the column was built, the exact rows were
drafted by the building dispatch, and the only reason a review exists at all is that the file lives
under `constraints/` and a write-protection hook correctly refused a delivery agent's edit. There
is no judgement call in it, and manufacturing one would be the wrong output.

---

## 1. Regression check — did the last review's changes work?

The last review to apply anything was
[2026-09-22 improvement review 2](docs/improvements/2026-09-22-improvement-review-2.md). Review
[2026-09-23 (2)](docs/improvements/2026-09-23-improvement-review-2.md) is drafted and still parked
at its gate, so it has applied nothing and there is nothing of its to audit yet.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [`agents/pipeline-agent.md`](agents/pipeline-agent.md) — *"Before you dispatch ANOTHER agent to fix what a finding describes"* | 2026-09-22 | `build-blocked-by-the-finding-it-remediates` | NO | Working — leave alone |
| [`agents/improvement-agent.md`](agents/improvement-agent.md) activation step 6 — the `observable_at` CLOSE/DEFER table | 2026-09-22 | `draft-states-a-disposition-the-closure-rules-forbid` | NO, and exercised again here | Working — leave alone |

Measured by classifying every entry carrying either `class_instance_of`: three members
(`IMP-0814`, `IMP-0815`, `IMP-0817`), all `APPLIED`, all timestamped before the changes landed. No
member of either class has been appended since.

The second row was exercised: both entries this review disposes of carry `observable_at: "V1"`,
which is the CLOSE/DEFER table's first row — **CLOSE**, `evidence_grep` is sufficient, and no
`reobserved` record is required or should be written.

**Changes whose class recurred after a *prose* fix:** none.
**Changes whose class recurred after a *gate*:** none.

**One durable success worth recording, because it is this review's whole subject.** The register's
own *"HOW TO ADD A COLUMN"* block was rewritten on 2026-09-06 to say plainly that the agent
securing a column cannot write the register and must propose the row instead. That is exactly what
happened here: the building dispatch attempted the write, was refused, drafted the rows in its Dev
Summary, logged the blocker and stopped. The control, the documented route around it, and the
capture all worked — the finding is the system running correctly, not a defect.

---

## 2. Clusters and promotion decisions

```
CLUSTER: pending-adjudication-entry-needed  (x1: IMP-0838)
Altitude:   INSTANCE, deliberately. Ladder row 1 — "one instance, specific to one feature,
            no general mechanism". The general mechanism already exists and already fired.
Becomes:    two rows in constraints/domain/special-category-register.yml
            pending_adjudication:, with the rationale as a dated comment block.
Retires:    nothing.
Cites:      IMP-0838 (IMP-0598 and IMP-0761 as the precedent this follows)
Residual:   This closes the ADJUDICATION DEBT, not the adjudication. Both rows record that
            the two columns are secured and that nobody with the authority to classify them
            has done so in writing. The Domain Owner / Compliance Lead still owns that call.
```

```
CLUSTER: hand-maintained-count-drifts-from-source  (x1 in scope: IMP-0840; x41 in the class)
Altitude:   INSTANCE. The class is heavily defended already and this is a number in a YAML
            comment that nothing reads; the fix is to stop stating a count, not to register
            and check one.
Becomes:    a wording change in the same file, in the same edit.
Retires:    nothing.
Cites:      IMP-0840
Residual:   Only this one sentence. No sweep of other prose counts is attempted here.
```

### Why no rule change follows from the blocker

`IMP-0838`'s own `proposed_change` asks for the two register rows and nothing else, and that is the
correct scope. Three things had to be true for this to be an instance application rather than a
generalisation, and all three measure true:

1. **The obligation was specified before the code was written.** The approved architecture document
   named the register entry as a deliverable of this task, and the source comment on each column
   points at the Dev Summary that drafts it.
2. **The gate caught it by name, at the right moment, in the right place.** `domain-invariants`
   failed with the two column names and the exact remedy. Run today against the tree as it stands:
   *"FAILED — 2 violation(s) across 21 registered column(s) and 77 secured column(s)"*.
3. **The handoff it required is already written down.** The register's own procedure says the
   securing agent proposes and improvement-agent applies. Nothing was missing; the only thing
   between the finding and the fix was the keyword this document asks for.

A finding whose entire content is *"the machinery worked, now do the human step it routes to"*
produces no rule change. Adding one would be the speculative-constraint case
[`skills/how-to-promote-a-finding.md` §4](skills/how-to-promote-a-finding.md) rules out.

### The one thing measured against the finding's own wording

The Dev Summary's draft block writes each row with a third key, `reason:`. The finding's own
`proposed_change` and `lesson` write them as bare `{ entity, name }` pairs. These are not the same
text, so the premise was measured rather than transcribed:
`verify-domain-invariants.py` reads only `entity` and `name` from each row and ignores anything
else, so **both forms validate**. The applied form follows the finding's own wording and the file's
established convention — bare pairs, with the rationale in a dated comment block directly above
them, exactly as the six rows added on 2026-09-18 are written. Nothing is lost: the reason text is
preserved verbatim in the comment.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | constraint-amendment | [`constraints/domain/special-category-register.yml`](constraints/domain/special-category-register.yml) | Add `rev_applicant.rev_localauthority` and `rev_applicant.rev_localauthoritystatus` to `pending_adjudication:`, under a dated comment block recording why | IMP-0838 | YES — `python3 scripts/verify-domain-invariants.py src/solutions/RevitaliseGrantAutomation --register constraints/domain/special-category-register.yml` goes from 2 violations to 0 |
| 2 | constraint-amendment | same file | Replace the header sentence *"these 51 columns"* with a phrasing that points at the count the gate prints on every run | IMP-0840 | YES — same command prints the true figure; no number is left in the prose to drift |

**Constraint budget:** 0 of 3 used. Neither change adds a constraint row; both amend a data file an
existing HARD constraint already reads.

### The exact text proposed — change 1

Appended to `pending_adjudication:`, after the block added on 2026-09-18:

```yaml
  # ── Added 2026-09-23 (IMP-0838), wbs:0.11 / CO-003, grant-admin-app ────────
  # Two columns built and secured in the grant-admin-app dispatch (TAD
  # docs/architecture/grant-admin-app-architecture.md §3/§6). NOT an open Article 9 question:
  # OQ-252 in docs/plans/grant-admin-app-plan.md resolves local authority as a geographic
  # administrative fact derived from postcode. Secured for the same reason, and released to the
  # same audience, as its sibling rev_applicant.rev_locationarea above — REV_TrusteeRestricted
  # releases both to the Grant Administrator role and REV Service Automation, trustees excluded
  # by non-membership (FR-256). Adjudicated together, as both columns' Entity.xml comments say.
  # development-agent drafted these rows in docs/development/grant-admin-app-dev-summary.md §6
  # and was correctly refused the write by .claude/hooks/protect-system-rules.py — the register's
  # own "HOW TO ADD A COLUMN" block working as written, not a defect.
  - { entity: rev_applicant, name: rev_localauthority }
  - { entity: rev_applicant, name: rev_localauthoritystatus }
```

### The exact text proposed — change 2

Replacing one line in the `pending_adjudication:` header block:

```
# WHAT IT IS NOT: a finding that these 51 columns are not Article 9 data. Nobody with the authority
```

becomes

```
# WHAT IT IS NOT: a finding that the columns listed below are not Article 9 data. Their number is
# printed by verify-domain-invariants.py on every run, green ones included — read it from there,
# never from a figure typed into this comment, which is the drift this register exists to end
# (IMP-0840: the sentence said 51 while the block held 58). Nobody with the authority
```

---

## 4. Retirements

> Retirement check performed: 86 live constraint rows reviewed against these clusters, none
> currently redundant.

Derived, not typed: `grep -rh '^| C-' constraints/ --include='*.md' | wc -l` → 86 live;
`grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` → 10 retired.

`C-DOM-033` is the constraint in play and is the opposite of a retirement candidate — it is the
rule that produced this review, by name, within one dispatch of the column being built. The nearest
thing to a retirement here is a discharge rather than a retirement: every row in
`pending_adjudication:` is a debt that leaves the list when its owner decides it, and this review
adds two rather than clearing any. That backlog is the Domain Owner's, and §5 records it.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0798, IMP-0799, IMP-0800, IMP-0801, IMP-0802, IMP-0803, IMP-0811, IMP-0812,
IMP-0818, IMP-0819, IMP-0822, IMP-0823, IMP-0825, IMP-0826, IMP-0827, IMP-0828, IMP-0829, IMP-0832,
IMP-0833, IMP-0836, IMP-0837, IMP-0839

**States excluded from this review, and why:**

| State | Count | Why excluded |
|---|---|---|
| `unread`, non-blocker | 21 | Out of scope. A blocker trigger summons a review of the blocker, not of the queue (`IMP-0183`). These wait for a batch review. |
| `awaiting-approval`, blocker | 5 | Already processed by reviews parked at their own gates. The remedy is a keyword, not a session (`IMP-0154`). Named below. |
| `awaiting-approval`, non-blocker | 4 | Same — parked at documents this review does not touch. |
| `reviewer-deferred` | 180 | Carry a `deferred_reason` a human accepted. Left alone. |

**The five parked blockers, and the document each waits on** — these need a keyword from you, and
none is re-derived here:

| Finding | Parked at |
|---|---|
| IMP-0820, IMP-0821 | [`docs/improvements/2026-09-22-improvement-review-3.md`](docs/improvements/2026-09-22-improvement-review-3.md) |
| IMP-0824 | [`docs/improvements/2026-09-22-improvement-review-4.md`](docs/improvements/2026-09-22-improvement-review-4.md) |
| IMP-0831 | [`docs/improvements/2026-09-23-improvement-review.md`](docs/improvements/2026-09-23-improvement-review.md) |
| IMP-0835 | [`docs/improvements/2026-09-23-improvement-review-2.md`](docs/improvements/2026-09-23-improvement-review-2.md) |

**Two items from the same delivery dispatch, noted and not actioned here:**

| Finding | Why deferred | Revisit when |
|---|---|---|
| IMP-0836 | The same dispatch found that no feature since the first has ever been given its own build/pipeline config, because the gate-wiring rule makes a feature-scoped one impossible — it would have to replicate the whole existing config. That is a reviewer/architect decision about the CI model, not a rules edit, and it is not what this blocker summoned a review for. | the next batch review of the unread queue, or an architect decision on one CI slug per solution |
| IMP-0839 | Logged by the same dispatch, `gate-scope-mismatch`. Untouched here for the same reason. | the next batch review |

**One thing the brief raised that produced no finding, and should.** The architecture document's
§8 describes the sibling control `rev_locationarea` as being in a state the actual source does not
match. The building dispatch noticed, built to the real source rather than to the document, and
said so — which is the right call — but the document is still wrong and nothing tracks it. This
review does not log it, because it has not read that document and a second-hand description is not
a measurement; the correct owner is the dispatch that saw it, or the next architect pass over that
TAD. Raised here so it is not lost. It is a documentation correction, not a build blocker.

**One flag carried forward from the previous review, still true:** `IMP-0800` sits in the deferred
list and the validator warns it is corrected by `IMP-0801` with no review having processed it,
which will fail the next build that reaches the `unit-tests` step. It is a batch-review item and
cannot be cleared by stamping a `deferred_reason` on it.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 835 | 836 |
| Distinct classes | 196 | 196 — IMP-0840 joins an existing class |
| Recurring classes (x≥2) | 63 | 63 |
| Digest lines | 752 | regenerate to confirm |

Regenerate with `python3 scripts/generate-known-failure-modes.py` and confirm with `--check`.

**Disposition simulated before parking**, per activation step 8: on a scratch copy, both entries
were set `APPLIED` with their `evidence_grep` needles and the gate re-run. The unread-blocker
trigger clears, and the only remaining errors are the two needle checks against text change 1 and
change 2 have not written yet — which is the gate confirming that an `APPLIED` claim without the
substance on disk is refused. The real log was restored and confirmed byte-identical with `diff`.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-23-improvement-review-3.md

Findings processed: 2 NEW  →  2 clusters
Regression check:   2 prior changes audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 2 constraint amendments, 0 gates/scripts,
                    0 skill/knowledge edits, 0 agent-file edits, 0 retirements
Altitude calls:     0 generalised from instance to class, 2 left at instance
Digest:             will regenerate — 836 lessons, 63 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

**Applied 2026-09-23** on `APPROVE IMPROVEMENTS`, as part of a batch applying six parked reviews.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | `constraints/domain/special-category-register.yml` — `rev_applicant.rev_localauthority` and `rev_applicant.rev_localauthoritystatus` added to `pending_adjudication:`, under the dated comment block verbatim from §3 | 2026-09-23 | IMP-0838 |
| 2 | Same file — the header's *"these 51 columns"* sentence replaced with the phrasing that points at the count the gate prints on every run | 2026-09-23 | IMP-0840 |

Entries rejected, with reasons:

| Finding | Rejected because |
|---|---|
| — | — |

**The gate result, measured after both this review and review 4 landed.** §3 predicted change 1
takes `domain-invariants` from 2 violations to 0 *for the columns this review names*. Review 4 of
the same day was applied in the same batch and cleared the third. The combined result:

```
DOMAIN INVARIANTS: PASS — 21 special-category column(s) verified.
  UNADJUDICATED-SECURED coverage: 78 secured = 17 registered + 61 pending adjudication, 0 undeclared
```

Exit code 0, no `UNADJUDICATED-SECURED` error remaining. **This review alone would not have produced
that line** — review 4's `rev_derivedcity` row was needed too, which is exactly what `IMP-0844`
recorded when a dispatch brief claimed this review had already been applied.

The two reviews append to the same block and were applied **in sequence**, this one first, rather
than assumed independent. Review 4's own §3 had measured that its row does not disturb this review's
anchor, and that held — but the sequencing was done on the measurement, not on the claim.
