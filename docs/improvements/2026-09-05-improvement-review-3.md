# Improvement Review — 2026-09-05 (3)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 `NEW` → 2 clusters
**Trigger:** blocker escalation — `IMP-0609`, unread, severity `blocker`
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** ~~DRAFT — nothing applied. `reviewed_in` stamped at step 6; `status` stays `NEW`.~~
**APPLIED 2026-09-05** on `APPROVE IMPROVEMENTS`. Superseded wording retained above so the change
is visible. See §9.
**WBS:** `wbs:0.4`

This review exists to unblock one build. `IMP-0609` halts
[`config/revitalise-grant-automation-build.yml`](../../config/revitalise-grant-automation-build.yml#L62)'s
`improvement-log-check` step (HARD, step 3 of 73), so the
`applicant-ethnicgroup-form-defect` feature cannot be built until it carries a disposition —
which is exactly what `IMP-0610` reports.

---

## 1. Regression check — did the last review's changes work?

The prior review is
[`docs/improvements/2026-09-05-improvement-review.md`](2026-09-05-improvement-review.md), which
processed `IMP-0602` and `IMP-0605`.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [`scripts/verify-pipeline-config.py`](../../scripts/verify-pipeline-config.py) gains `check_resolved_note_cleared` | 2026-09-05 | `stale-deferral-uncaught-across-sessions` | Nominally YES — `IMP-0610` carries that `class_instance_of` | **Not a gate failure — a class-name collision.** See below |
| `IMP-0605`: no gate; recorded as process discipline | 2026-09-05 | `routed-work-not-reverified-at-apply-time` | YES — `IMP-0610` is the same mechanism | **Recurred after a no-change disposition, at reduced cost.** See below |
| `IMP-0602`'s own proposed standing tracker — WITHHELD | 2026-09-05 | (same) | n/a | Withholding still correct; this review reaches the same conclusion independently |

**Did the gate run?** Yes, and it is green. `python3 scripts/verify-pipeline-config.py
config/revitalise-grant-automation-pipeline.yml` exits **0** as of this review, and
`check_resolved_note_cleared` appears **2×** in that script. So the change landed and fires.

**Why `IMP-0610` is not that gate's recurrence.** `check_resolved_note_cleared` is scoped to
`blocked_on` notes in `config/revitalise-grant-automation-pipeline.yml`. `IMP-0610`'s subject is
an **improvement-log entry**, not a pipeline note. The gate could not have fired on it and was
never meant to. The entry's `class_instance_of` of `stale-deferral-uncaught-across-sessions` is,
in this reviewer's reading, **mis-assigned**: its mechanism — *the underlying condition was fixed
and the finding that reported it was left unread, so the next build halts* — is `IMP-0605`'s
`routed-work-not-reverified-at-apply-time` verbatim. Recorded here rather than rewritten on the
entry, because a finding's own classification is the logging agent's, and the digest's `x4`
against `x2` is the signal a future review should read alongside this note.

**Changes whose class recurred after a *prose* fix:** `IMP-0605`'s discipline note. The template
says escalate to a mechanical gate. **This review does not**, and the reason is measured rather
than argued: the gate already exists, already fires, and already prints the exact remedy —
`verify-improvement-log.py` named `IMP-0609` by id and offered both discharges (a review, or a
`deferred_reason`) in this review's own activation run. **The cost also fell**: `IMP-0605` cost a
halted 73-step build; `IMP-0610` cost *"one verification cycle… no build re-run attempted once the
blocking finding was identified live"*. A second forecasting mechanism over a gate that fires
correctly is the wrong altitude — the same conclusion the prior review reached when it withheld
`IMP-0602`'s standing tracker.

**Changes whose class recurred after a *gate*:** none.

---

## 2. Clusters and promotion decisions

```
CLUSTER: untriaged-tool-warning  (x9 overall; this instance: IMP-0609)
Altitude:   INSTANCE — the constraint fired correctly and prescribed the exact fix that was made.
            The class is already at LAW altitude (C-TECH-055, HARD), amended once (IMP-0499) and
            half-mechanised once (IMP-0573). Nothing here argues for a tenth rung.
Ladder row: "One instance, specific to one feature, no general mechanism" → stays a log note,
            CLOSED. The document fix is development-agent's, and it has landed.
Becomes:    Nothing enforceable. IMP-0609 closes APPLIED against a fix already on disk.
            One clarifying constraint-amendment (§3 row 1), which is scope, not a new rule.
Retires:    nothing
Cites:      IMP-0609, IMP-0499, IMP-0573
Residual:   The signature-diff half of C-TECH-055 remains unbuilt behind IMP-0500 — so nothing
            mechanically compares a build's live warning stream against §11, and this class's
            tenth instance will again be caught only by build-agent reading the stream by hand.
            That is unchanged by this review and deliberately so: IMP-0500 already owns the work
            and already names its precondition (build/artifacts/** is gitignored while 34
            manifests are tracked — IMP-0410's class).
```

```
CLUSTER: routed-work-not-reverified-at-apply-time  (x3: IMP-0517, IMP-0605, IMP-0610)
            — logged by build-agent as stale-deferral-uncaught-across-sessions; see §1.
Altitude:   NOTE — the system behaved as designed. A blocker halts every gate that reads the log
            until a review dispositions it; that is the control, not a defect in it.
Ladder row: None applies. Per skills/how-to-promote-a-finding.md §4, "it would be cleaner" is not
            a finding, and the mechanism here is a control doing its job.
Becomes:    Nothing. IMP-0610 closes APPLIED with no rule change, matching IMP-0605's disposition.
Retires:    nothing
Cites:      IMP-0610, IMP-0605, IMP-0517
Residual:   IMP-0605's applied_by said "a third makes it a constraint row". This IS arguably the
            third, and this review declines to write that row — on the measured grounds that the
            cost fell rather than rose and the existing gate names the remedy precisely. If a
            FOURTH instance appears whose cost is a halted build rather than a verification cycle,
            that judgement is disproved and the row should be written. Stated here so the next
            review can hold this one to it.
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | constraint-amendment | [`constraints/technology/technology-constraints.md`](../../constraints/technology/technology-constraints.md#L110) | `C-TECH-055`: state WHICH warnings §11 must carry — third-party tool output, not this repository's own SOFT gate findings | IMP-0609 | NO — prose; justified below | N/A |

**Constraint budget: 0 of 3 used.** Row 1 amends an existing row and adds none.

### Why row 1, and the measurement behind it

Build `applicant-ethnicgroup-form-defect-20260905-4`'s manifest carries **8** `warnings_detail[]`
entries. `IMP-0609` named **2** of them. The other six are not an oversight, and I measured why:

| Warning | Origin | Where it is triaged |
|---|---|---|
| `npm warn deprecated glob@10.5.0` | third-party (`npm ci`) | §11 row — [dev summary L146](../development/applicant-ethnicgroup-form-defect-dev-summary.md#L146) |
| `pac solution pack` "not defined in customizations" | third-party (`pac`) | §11 row — [dev summary L147](../development/applicant-ethnicgroup-form-defect-dev-summary.md#L147) |
| `vite`: chunks larger than 500 kB | third-party (`vite`) | [`bundle-budget.json`](../../src/code-apps/trustee-review-portal/bundle-budget.json) — C-TECH-055's own half (a), wired at [build config L675](../../config/revitalise-grant-automation-build.yml#L675) |
| `change-order-requirements`, `routing-reconciliation`, `review-document`, `commercial-events`, `derived-counts` | **this repo's own SOFT gates** (`scripts/verify-*.py`) | the gate's own step output |

Measured, not assumed: `grep -rln` for `routing-reconciliation`, `commercial-events`,
`review-document` and `change-order-requirements` across **every** `docs/development/*dev-summary*.md`
returns **zero files**. No Dev Summary in this project has ever recorded a repo SOFT-gate finding
as a Dev Summary §11 row, including in builds declared SUCCESS.

So `C-TECH-055`'s `Verify By` clause — *"build log warning count reconciles to resolved-or-recorded
entries in the current feature's Dev Summary §11"* — reads **8-vs-2 and red** taken literally, and
**2-vs-2 and green** under the reading every agent has actually applied. The row says *"emitted by
a build, pack, or deploy **tool**"*, which is the right rule; it has simply never said that its own
gate steps are not tools. The amendment writes down the boundary build-agent drew correctly here,
so the next one does not draw it differently — in either direction. Pasting five meaningless rows
into a Dev Summary §11 to satisfy a literal count is the failure mode this prevents.

**Justification for `Mechanically verifiable? NO`:** the mechanical form of this boundary is a
classifier over `warnings_detail[]` by originating step, which is precisely the deferred
signature-diff work `C-TECH-055` already tracks behind `IMP-0500`. This amendment **sharpens
`IMP-0500`'s specification and does not compete with it** — it tells whoever builds that gate
which subset to diff. Writing a second gate here would be the wrong altitude and a second
authority over the same rule.

---

## 4. Retirements

> Retirement check performed: **10 retired** and **85 live** constraint rows reviewed (derived, not
> typed: `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` → 10;
> `grep -rh '^| C-' constraints/ --include='*.md' | wc -l` → 85). None currently redundant. The one
> row this review touches, `C-TECH-055`, is load-bearing and firing — it is what caught `IMP-0609`
> — and its half-mechanised state (`IMP-0573`) means retirement would remove enforcement no other
> row provides.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0608

**States excluded from this review's scope, per `agents/improvement-agent.md` activation step 2**
(measured by `python3 scripts/verify-improvement-log.py --check`, which reported
133 `NEW`: 2 `unread`, 1 `awaiting-approval`, 130 `reviewer-deferred`, 0 `already-fixed`):

| State | Count | Disposition |
|---|---|---|
| `unread` | 2 | **This review's scope** — IMP-0609, IMP-0610 |
| `awaiting-approval` | 1 | IMP-0608 — parked on [`2026-09-05-improvement-review-2.md`](2026-09-05-improvement-review-2.md). **The remedy is the keyword against THAT document, not a session here.** Not re-derived |
| `reviewer-deferred` | 130 | Left as deferred; each carries a reviewer-accepted `deferred_reason`. Not enumerated, and no `excluded_by` stamp needed — this document names none of them by id |

One housekeeping note the gate raises and this review does **not** take: `IMP-0274` is the single
deferred entry carrying no `revisit_when`. It is out of scope here and named without disposition.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0608 | (see review-2) | Already processed by another review parked at its own gate; re-deriving it is the `IMP-0183` defect | `APPROVE IMPROVEMENTS` is sent against `2026-09-05-improvement-review-2.md` |

---

## 6. Digest impact

**Measured on a simulated log, not predicted** (`IMP-0198`: a review that predicted a digest delta
from the class names measured 31→30).

| | Before | After |
|---|---|---|
| Log entries | 607 | 607 |
| Distinct lessons | 603 | 603 |
| Recurring classes (x≥2) | 47 | 47 |
| Digest lines | 630 | 630 |

`diff` between the current digest and one generated from the simulated log is **one relocation**:
`IMP-0609`'s lesson moves from line 507 to line 524 within its section as its status changes. No
lesson is added, removed or reworded. The digest is currently `--check` clean (607 entries) and
will be regenerated at apply time regardless.

---

## 7. Verification performed for this draft

Every premise below was **executed or grepped**, per `agents/improvement-agent.md` step 8. None is
read from a document.

| Claim | Instrument | Result |
|---|---|---|
| `IMP-0609`'s fix is on disk | `grep -n` on the dev summary | Rows present at **L146** and **L147**; the old *"None emitted by any command run in this session"* string is **gone** (0 matches) |
| Both citations resolve to real rationale | `sed -n` on both targets | `revitalise-grant-automation-dev-summary.md#L4893` is the *"Tool warnings triaged… 3, all accepted"* paragraph, item 2 = `glob@10.5.0`. `trustee-portal-visual-refresh-dev-summary.md#L2631` is the `pac solution pack` "not defined in customizations" row. **Both line anchors are exact** |
| The `pac` warning is unchanged in **magnitude** | `pac solution pack … --errorlevel Info`, run live to a scratch zip | exit 0; block is **14 lines = 9 `EntityRelationship` + 5 `EnvironmentVariableDefinition`**, matching the cited rationale. Figures, not wording — `C-TECH-055`'s own lesson |
| The `npm` warning still fires, and nothing else does | `npm --prefix src/code-apps/trustee-review-portal ci` — the exact build-step command at [L517](../../config/revitalise-grant-automation-build.yml#L517) | exit 0; **exactly one** `npm warn deprecated` line (`glob@10.5.0`) and **zero** other `npm warn` lines. §11's two rows therefore cover 100% of the stream from these two steps |
| The disposition actually clears the trigger | simulated log + `verify-improvement-log.py --check --log <sim>` | `0 unread` — the blocker TRIGGER **clears**. Sole remaining error is that this document did not yet contain the string `IMP-0610`, which the written body now satisfies |
| The probes changed nothing tracked | `git status --porcelain` | Unchanged before and after; `pac` wrote to scratch, `npm ci` to `node_modules/` |

**Level reached: V2.** Two real tools ran and their warning streams were read. V3+ (solution
import, live behaviour) is not claimed and was not run.

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-05-improvement-review-3.md

Findings processed: 2 NEW  →  2 clusters
Regression check:   3 prior changes audited, 1 class recurred (after a no-change disposition;
                    escalation declined on measured grounds — §1)
Proposed:           0 constraints (cap 3), 1 constraint amendment, 0 gates/scripts,
                    0 skill/knowledge edits, 0 agent-file edits, 0 retirements
Altitude calls:     0 generalised from instance to class, 2 left as notes
Digest:             will regenerate — 603 lessons, 47 recurring classes (measured: no delta)

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 9. Applied

`APPROVE IMPROVEMENTS` received 2026-09-05. Re-verified before applying, per
`agents/improvement-agent.md` step 8, and **every premise still held**: the log was unchanged at
607 entries with `IMP-0610` still the maximum id (no concurrent session appended), **no** entry
carries `corrects` naming either finding, both Dev Summary rows were still present, `C-TECH-055`
was still at L110, and the "no Dev Summary records a repo SOFT-gate finding" grep still returned
zero files. Nothing was withheld and nothing was narrowed.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | [`C-TECH-055`](../../constraints/technology/technology-constraints.md#L110) amended — the reconciliation counts third-party tool output, not this repository's own SOFT gate findings | working tree, 2026-09-05 | — |
| 2 | Closure of the citation-gap blocker against the fix at [dev summary L146–147](../development/applicant-ethnicgroup-form-defect-dev-summary.md#L146), with a V2 `reobserved` from re-running both build steps | `logs/improvement-log.jsonl` | IMP-0609 |
| 3 | Closure with no rule change, and the declined escalation recorded on the entry | `logs/improvement-log.jsonl` | IMP-0610 |

**Table integrity after the amendment:** `C-TECH-055` remains a single row of 8 fields, matching
its sibling `C-TECH-054`; live rows **85** and retired rows **10**, both unchanged — the amendment
added no row, as the draft promised.

**Gates after applying:** `verify-improvement-log.py --check` exits **0** — *0 unread, 1
awaiting-approval* (that one is `IMP-0608`, parked on review-2 and out of scope here). The blocker
trigger that halted step 3 of the build is **cleared**.

Entries rejected, with reasons:

| Finding | Rejected because |
|---|---|
| — | none. Both entries closed `APPLIED`; neither proposal was disproved on re-verification |
