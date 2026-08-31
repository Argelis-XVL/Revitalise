# Improvement Review — 2026-08-31 (6)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 1 `NEW` (unread blocker) → 1 cluster
**Trigger:** blocker escalation — `IMP-0535`, per `agents/improvement-agent.md#L61` ("Any UNREAD
blocker-severity entry is appended — immediately — do not batch")
**Gate:** `APPROVE IMPROVEMENTS`

**Scope note (no silent cap):** this dispatch processes only the one unread blocker, `IMP-0535`,
per `agents/improvement-agent.md#L85` — an unread blocker must not pull a review of everything
around it. `python3 scripts/verify-improvement-log.py --check` reports 112 further `NEW` entries,
all `reviewer-deferred` with a recorded reason (state table at
`agents/improvement-agent.md#L100-L105`); none of those are re-derived here.

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Review 36 change 1 — `scripts/verify-design-doc-claims.py` check (a)/(b) FAILED-message text carries the retraction-safe authoring form (`SOURCE-FIRST` wording, no old figure in a table row) | 2026-08-28 | `gate-fires-on-nothing` (retraction blind spot, `IMP-0428`) | **YES — `IMP-0535`**, same document, same mechanism, three days later | **Wrong altitude, but not the altitude IMP-0535 itself proposes.** See §2. |

The gate itself did not misfire in the sense of being broken: `scripts/verify-design-doc-claims.py
--selftest` still passes 22/22 (verified this session, see §2 residual), and its measured
precision on the design-doc corpus (docstring, `scripts/verify-design-doc-claims.py:60-84`) is
unchanged at 3 true / 0 false. What recurred is the **false positive on a retraction sentence**
IMP-0428 already named and explicitly declined to fix mechanically. Per
`agents/improvement-agent.md#L354-L356` (the Regression Check table): *"A recurrence after a prose
fix is evidence the fix was at the wrong altitude — escalate it to a gate."* That instruction is
followed in §2, but not by adding a second phrase heuristic to the same script — the reasoning for
why is the substance of this review.

---

## 2. Cluster and promotion decision

```
CLUSTER: gate-fires-on-nothing  (x2 on this exact mechanism: IMP-0428, IMP-0535 — both instances
         of verify-design-doc-claims.py check (a) firing on a retraction rather than an assertion,
         both in docs/architecture/trustee-portal-visual-refresh-architecture.md)
Altitude:   CLASS, but the class is narrower than "gate-fires-on-nothing" as a whole (x9 in
            logs/known-failure-modes.md#L49, most of them unrelated mechanisms). The property,
            independent of instance: "prose guidance embedded only in a gate's own FAILED message
            reaches nobody before the sentence that trips it is written."
Ladder row: skills/how-to-promote-a-finding.md#L44 ("second instance of the same
            class_instance_of — generalise, instance patches forbidden"), resolved via
            skills/how-to-promote-a-finding.md#L28 ("prefer the most mechanical home available")
            AND agents/improvement-agent.md#L500-L504 ("assert on VALUES, not on PHRASES,
            wherever a value exists" — which is why the mechanical home here is NOT a second
            regex).
Becomes:    agents/architect-agent.md — a new "Before you finish" step (same pattern as the
            IMP-0366 precedent immediately above it at agents/architect-agent.md#L132-L152):
            after any edit to docs/architecture/*.md or docs/plans/*.md, run
            `python3 scripts/verify-design-doc-claims.py docs/architecture docs/plans` against
            the edited document BEFORE presenting the gate output, and apply the check's own
            SOURCE-FIRST authoring fix immediately if it fails — rather than letting build-agent
            discover it 35+ minutes into an unrelated packaging run (IMP-0535's own `cost` field).
Retires:    nothing. See "why not a script change" below.
Cites:      IMP-0428, IMP-0535
Residual:   an architect-agent dispatch that forgets to run the step still recurs — this fix
            moves the check from "never seen before it fails" to "seen at authoring time," it does
            not make running it involuntary. The HARD gate at
            config/revitalise-grant-automation-build.yml:1223 stays wired unchanged as the
            backstop; this is a second, earlier checkpoint, not a replacement for it.
```

### Why not a script change (the choice IMP-0535 itself frames as contested)

`IMP-0535` `contests` `IMP-0428`'s decision to withhold a mechanical retraction-narrowing, on the
grounds that the message-only fix has now failed a second time in the same document. That
observation is correct and drove the escalation above — but the escalation is **not** to the
narrowing IMP-0428 rejected. `scripts/verify-design-doc-claims.py`'s own docstring
(`scripts/verify-design-doc-claims.py:33-45`) records that the *opposite* direction of this exact
check was tried first and measured **7 findings, 0 true, 7 false**, all of them "the OLD WORDING
SURVIVING INSIDE ITS OWN RETRACTION" — and `IMP-0422` has now measured phrase-proximity gates false
48-100% five separate times. A retraction-marker regex (`erratum`, `retract`, `wrongly stated`, …)
is the same instrument again: it would suppress exactly the sentence shape that is sometimes a real
False positive and sometimes IMP-0379's live defect restated, and `agents/improvement-agent.md:500`
names the tell directly — *"a retraction marker is a phrase, and adding one as a narrowing … hands
every author an escape hatch on a real finding."* `IMP-0428`'s WITHHELD decision is reaffirmed on
this third look at the evidence, not overridden.

What IMP-0428 left unaddressed is timing, not precision: its own `why_it_was_never_caught`
equivalent for IMP-0535 is stated plainly in the finding — *"the guidance lives in the gate's own
FAILED message, read only by whoever is looking at the gate output at the moment it fails …
nothing checks NEW prose against it before the prose is written."* That is a step-order defect
(`skills/how-to-promote-a-finding.md`'s ladder row *"the order of steps was wrong"*), and its fix is
mechanical in the sense the anti-bloat rule requires (`agents/improvement-agent.md#L393-L396`,
*"Verify By" must be mechanically executable*): `Verify By` = re-run the same, already-measured
script, against the same file, one step earlier in the pipeline. Nothing in the script changes, so
none of its measured precision is at risk.

### Which half is IMP-0535: script defect, or document-authoring defect?

Both, and they are not weighted equally. The **document-authoring half** is real and is being fixed
separately, in parallel, by development-agent per this dispatch's own framing — Erratum 8.1's
sentence at `docs/architecture/trustee-portal-visual-refresh-architecture.md:755` is not required
reading for anyone; it could have used the SOURCE-FIRST form the gate's own message already
recommends and did not. But the **script/process half is the one this review can durably fix**: a
correctly-worded erratum, written by an author who never saw the gate's guidance because nothing
put it in front of them before they wrote the sentence, is what recurred twice. Fixing only the one
sentence (as development-agent is doing) closes this instance and not the class; the
architect-agent step closes the class without touching the script's measured behaviour.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | agent | `agents/architect-agent.md` (new "Before you finish" subsection, following the `IMP-0366` precedent at `agents/architect-agent.md#L132-L152`) | Before presenting the gate output, run `python3 scripts/verify-design-doc-claims.py docs/architecture docs/plans` against any `docs/architecture/*.md` or `docs/plans/*.md` file this dispatch edited, and apply the FAILED message's SOURCE-FIRST fix immediately on a red result | IMP-0428, IMP-0535 | YES — `python3 scripts/verify-design-doc-claims.py docs/architecture docs/plans` exits 0/1 | N/A (agent-instruction change; the underlying gate stays `HARD` at `config/revitalise-grant-automation-build.yml:1223`, unchanged) |

**Constraint budget:** 0 of 3 used. No constraint proposed — `Verify By` for this change is "run
the agent's own next-activation step," which is process, not a platform rule; a constraint row
whose enforcement is "an agent read its own file" would be a comment, per
`skills/how-to-promote-a-finding.md#L37-L38`.

No change to `scripts/verify-design-doc-claims.py` is proposed. See §2 "Why not a script change."

---

## 4. Retirements

Retirement check performed: 0 constraints touched by this cluster (no constraint is added, amended
or targeted). A repository-wide retirement audit is out of scope for this single-blocker dispatch
per `agents/improvement-agent.md#L85` (narrow-scope rule) and is not attempted here.

---

## 5. Findings left unprocessed

**Deferred:** none newly deferred by this review. The 112 `reviewer-deferred` entries reported by
`verify-improvement-log.py --check` were deferred by earlier reviews and are not re-opened here —
this dispatch's scope is `IMP-0535` alone.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 532 | 532 (no new entry appended — `IMP-0535` is stamped `reviewed_in`, not duplicated) |
| Distinct lessons under `gate-fires-on-nothing` | 9 (`logs/known-failure-modes.md:49`) | 9 (unchanged — no new finding logged; `IMP-0535`'s existing lesson line stands) |
| Recurring classes (x≥2) | unchanged | unchanged |
| Digest lines | unchanged pending regeneration | regenerated after approval to reflect `IMP-0535`'s `awaiting-approval` state |

Regeneration deferred to post-approval per §7/§8 below (`IMP-0535`'s `status` and `reviewed_in`
move on the keyword, not before).

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-31-improvement-review-6.md

Findings processed: 1 NEW  →  1 cluster
Regression check:   1 prior change audited, 1 class recurred (prose fix, escalated — see §2)
Proposed:           0 constraints (cap 3), 0 gates/scripts, 0 skill/knowledge edits,
                    1 agent-file edit, 0 retirements
Altitude calls:     1 generalised from instance to class (agent-file step-order fix), 0 left as notes
Digest:             will regenerate — IMP-0535 moves unread → awaiting-approval, 9 lessons under
                    gate-fires-on-nothing, unchanged in count

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```
