# Improvement Review — 2026-09-18

**Status: APPLIED IN FULL 2026-09-18.** All 6 rows in §3 landed, including all three decision
items the reviewer approved. 0 rows remain unapplied, 0 withheld.

~~DRAFT — parked at its gate. `APPROVE IMPROVEMENTS` has not been given. Nothing in §3 has been
applied; §8 is empty by design.~~

Processed: **6 findings → 4 clusters.** 3 were `unread` at dispatch (IMP-0759, IMP-0760,
IMP-0761); 2 were `awaiting-approval` and are reconciled here rather than re-derived (IMP-0723,
IMP-0747); the 6th (IMP-0762) was logged by this review after measuring the queue state the
dispatch brief asked to be checked.

---

## 0. The one thing to read first

**The `domain-invariants` build gate is red on seven violations right now, not one.** The
dispatch brief describes IMP-0760's alternation mismatch as the blocker. It is one of seven, and
the other six are a different defect that the same day's draft document was written to fix.

Executed, not read — `python3 scripts/verify-domain-invariants.py src/solutions/RevitaliseGrantAutomation`,
true exit status **1** (taken from `$?` on a redirect, not through a pipe):

| # | Violation | Fixed by |
|---|---|---|
| 1 | `REGISTER-ENTITY-MISMATCH` — the FR-016 gate does not bar `rev_receivesbenefits` | Cluster A part 1 (schema extension) |
| 2–7 | `UNADJUDICATED-SECURED` × 6 — `rev_applicant.rev_locationarea` plus five `rev_application` helper/safeguarding columns are secured but in neither register list | Cluster A part 2 (apply the register-update draft) |

So **applying IMP-0760's proposal alone leaves the build red.** The two halves have to land
together, and both live under `constraints/`, which makes them mine to apply and nobody else's.

The six columns in rows 2–7 are exactly the six the register-update draft enumerates — five on
`rev_application` and one on `rev_applicant`. That one is `rev_locationarea`, and it is the entity
error IMP-0761 caught.

---

## 1. Regression check — the 2026-09-17 review

Twenty-one rows, recorded as applied in full. Audited here:

| Question | Answer |
|---|---|
| Has any class from that review recurred? | **One.** `stale-deferral-uncaught-across-sessions` recurred as IMP-0762 — and the recurrence was *caused by* that review's own bookkeeping (§2 cluster D) |
| Prose fix or mechanical gate? | Neither. The rule this review broke was already prose in `agents/improvement-agent.md`, and it was followed for 2 of 4 eligible entries. Prose at the wrong altitude → escalate to a gate (cluster D) |
| Did a gate exist and not fire? | Yes — `verify-improvement-log.py` ran clean and reported both stale entries as *"send the keyword; do not re-derive."* It had the data to know better |
| Did closure evidence match `observable_at`? | Checked. The row that closed IMP-0723's change landed correctly (`--mapping-claims-only`, build line 299) and the entry was **correctly** left open at V5 — the live-form question it turns on cannot be settled here |

**The 2026-09-17 change for IMP-0723 did land.** Verified in the target, not in the review's own
APPLIED cell: `scripts/verify-design-doc-claims.py` carries `--mapping-claims-only` and the
`docs/development` root, wired SOFT at
[build line 299](../../config/revitalise-grant-automation-build.yml#L299).

---

## 2. Clusters

```
CLUSTER A: a compliance register conflates two independent axes   (x1: IMP-0760)
Altitude:  CLASS — 22nd instance of gate-scope-mismatch, 1st of this sub-shape
Ladder row: "a tool could catch it mechanically" — script, not prose
Becomes:   .engine/scripts/verify-domain-invariants.py gains an optional per-column
           exception field; constraints/domain/special-category-register.yml gains the
           schema and the row; C-DOM-030's wording is amended to match
Engine/instance: the MECHANISM (a governance register whose security axis and whose
           gate-bar axis are independent) is ENGINE. The LITERALS (FR-016,
           rev_receivesbenefits, the step name) stay in the instance register
Retires:   the register header's blanket sentence "Every row is barred from the automated
           score regardless of its `secured` value" — which is the conflation, in prose
Cites:     IMP-0760
Residual:  a column carrying the exception is no longer covered by the blanket gate. The
           only thing holding the narrowed boundary is the companion build step and a
           Pester test — which is why the field's `gate:` key is MANDATORY below
```

**One deliberate change from what the finding proposed.** IMP-0760 proposes
`fr016_scoring_exception: {reason, owner, scope}`. Three prose keys create a hole whose only
guard is prose. I propose a fourth key, **`gate:`, mandatory**, naming the build step that
enforces the narrowed boundary — and the checker verifies that step exists in the build config.
That turns the exception from a note into something with a mechanical guard, which is the
ladder's own preference. It is additive and it narrows nothing.

The field is named generically in the engine (the engine has no concept of "FR-016"); the
instance register supplies the literal.

```
CLUSTER B: a draft named the wrong entity for a column          (x1: IMP-0761)
Altitude:  INSTANCE — one occurrence, already fixed in the dispatch that found it
Ladder row: row 1 — "one instance, specific to one feature" → stays a log note
Becomes:   nothing. Close the entry
Cites:     IMP-0761
Residual:  none. The corrected draft cites Entity.xml line 288 per column
```

Verified against source rather than against the finding: `rev_locationarea` is declared at
`Entities/rev_applicant/Entity.xml` line 288, and the draft now names `rev_applicant`.

```
CLUSTER C: a change order priced before its FR text exists      (x3: IMP-0278, IMP-0288, IMP-0759)
Altitude:  LEFT AS A NOTE — and the third instance does not change that
Ladder row: none. §4 exclusion — "an argued mechanism in place of a defect"
Becomes:   nothing
Cites:     IMP-0759
Residual:  the re-price rule has never been observed to FIRE — see §4
```

The ladder's third-instance row points at a constraint. I am not proposing one, for two reasons
I can evidence. The rule already exists —
[`agents/commercial-agent.md` line 62](../../agents/commercial-agent.md#L62) says verbatim what
the finding says is missing, and I grepped it rather than taking the finding's word. And a
constraint reading *"was this estimate produced by analogy?"* has no mechanically executable
`Verify By`, which makes it a comment under the anti-bloat limits. The count is the deliverable;
the digest already carries it at ×3.

```
CLUSTER D: an entry left open with no deferred_reason reports as awaiting-approval
                                                     (x5 class: IMP-0723, IMP-0747, IMP-0762)
Altitude:  CLASS — 5th instance of stale-deferral-uncaught-across-sessions
Ladder row: "the system's own memory failed" → a read-path change, mechanised
Becomes:   scripts/verify-improvement-log.py + .engine twin — a new WARNING
Cites:     IMP-0723, IMP-0747, IMP-0762
Residual:  the check cannot tell a correctly-parked entry from a stale one where the
           review closed NO entries at all. That case stays invisible, and it is rare —
           0 instances in 758 entries today
```

**What went wrong.** `agents/improvement-agent.md` requires an entry left open to carry a
`revisit_when` **and** a `deferred_reason`. The 2026-09-17 review supplied both for two entries
and only the first for two others. A `deferred_reason` is one of the four discharges the queue
gate recognises; a bare `revisit_when` is none of them. So IMP-0723 and IMP-0747 have been
reporting as *"a review already processed it and is parked at its own gate — send the keyword"*
ever since, against a review that was applied in full the same day.

**The measured check.** An entry still `NEW`, with no `deferred_reason`, whose `reviewed_in`
names a document that has **already closed other entries**. If a review closed entries, its
keyword was given; anything still open under it was left behind, not awaiting approval. This is a
count of rows, not a reading of prose.

Measured over the whole corpus — **758 entries, 2 findings, 2 true positives, 0 false
positives**, and 140 entries correctly not flagged because they carry the `deferred_reason`
discharge. The two findings are IMP-0723 and IMP-0747.

---

## 3. Proposed changes

| # | Row | Repo | Severity | Cites |
|---|---|---|---|---|
| 1 | `.engine/scripts/verify-domain-invariants.py` — optional per-column gate-exception field with a mandatory `gate:` key, excluded from the alternation-parity comparison; every other invariant unchanged | **.engine** | — | IMP-0760 |
| 2 | `constraints/domain/special-category-register.yml` — the schema block, the `rev_receivesbenefits` exception row, and the header sentence amended | instance | — | IMP-0760 |
| 3 | `constraints/domain/domain-constraints.md` — C-DOM-030 amended: the two lists are equal *except* for rows carrying a gated exception | instance | HARD (amended, not new) | IMP-0760 |
| 4 | `constraints/domain/special-category-register.yml` — the six `pending_adjudication:` rows from the register-update draft, entity-verified per column | instance | — | IMP-0761 |
| 5 | `scripts/verify-improvement-log.py` + `.engine` twin — the left-behind-entry WARNING measured in cluster D | instance **+ .engine** | SOFT (warning) | IMP-0762 |
| 6 | `logs/improvement-log.jsonl` — `deferred_reason` + `revisit_when` on IMP-0723 and IMP-0747 | instance | — | IMP-0723, IMP-0747 |

**No new constraints.** Cap is 3; this review proposes 0 and amends 1.

**No new scripts.** Both mechanical changes extend gates that already exist and are already
wired, so `scripts/derived-counts-registry.json`'s verify-script count stays at **62** and needs
no update in this change.

**Retirement.** One retired: the register header's blanket sentence, which is the conflated axis
written down. No constraint row is retired — checked. C-DOM-030 is amended rather than retired
because it remains correct for every column that carries no exception. Derived at draft time:
**10 retired rows, 85 live rows.**

---

## 4. What this review is NOT doing

**The re-price rule has never been observed to fire.** Cluster C rests on
`agents/commercial-agent.md`'s rule that a by-analogy ROM is re-priced when its SDD lands. The
rule exists. I did not verify that it has ever actually executed against CO-001, whose SDD is the
only one old enough to have triggered it. That is a question for `commercial-agent`, it is
outside this dispatch's scope, and it is the honest residual on leaving cluster C as a note.

**Scope excluded by the dispatch brief**, and stated so the cap is not silent: today's Dev
Summary, the CO-003/004/005 approval bookkeeping, and the two delivery builds. None was read.

**163 `reviewer-deferred` entries were not read**, per activation step 2 — each carries a
`deferred_reason` a human accepted. One of them, IMP-0274, names no `revisit_when`, which the
gate reports as *"a decision to never do it."* Left as is; it is not this review's to reopen.

**Five `corrects` warnings are open** on IMP-0290, IMP-0298, IMP-0320, IMP-0430 and IMP-0437.
All five belong to reviews from August. None names anything this review proposes to act on, so
none is load-bearing here.

---

## 8. Applied record

**All 6 rows landed. 0 withheld.** Applied incrementally, each entry closed as its change landed;
the digest was regenerated once, last.

| # | Row | Repo | Entry closed |
|---|---|---|---|
| 1 | `verify-domain-invariants.py` — `gate_exception`, four keys, `gate:` mandatory | **.engine** | IMP-0760 |
| 2 | Register — the two-axis schema block, the `rev_receivesbenefits` exception row | instance | IMP-0760 |
| 3 | C-DOM-030 amended — the lists are equal *except* for gated exceptions | instance | IMP-0760 |
| 4 | Register — six `pending_adjudication:` rows, entity-verified per column | instance | IMP-0761 |
| 5 | `verify-improvement-log.py` + `.engine` twin — `check_left_behind()` | instance **+ .engine** | IMP-0762 |
| 6 | `deferred_reason` + `revisit_when` on the two left-behind entries | instance | IMP-0723, IMP-0747 |

**The headline result.** `domain-invariants` went from **exit 1 with 7 violations** to **exit 0**.

### One change made beyond what was proposed, and one bug it caught

`gate:` was made **mandatory** rather than one of three optional prose keys, and the checker
asserts the named step exists in the build config. The reviewer approved this explicitly.

The first version of the note-printing appended to the script's `notes` list — which is the
auditing-off enumeration, printed with its own hardcoded prefix and whose `len()` feeds the
sentence below it. The carve-out note rendered as *"NOTE: auditing is off — GATE-EXCEPTION…"* and
would have reported 5 audit-off attributes where there are 4. Caught by running the gate rather
than re-reading the edit; fixed with a separate list.

### Proven able to fail, three ways

Not merely selftested. Each ran against the real register and build config:

| Fixture | Result |
|---|---|
| `gate:` key removed | exit 1, `GATE-EXCEPTION-INCOMPLETE` |
| `gate:` names a step that does not exist | exit 1, `GATE-EXCEPTION-UNENFORCED` |
| exempt column left in the alternation too | exit 1, `GATE-EXCEPTION-CONTRADICTED` |
| control — unmodified | no `GATE-EXCEPTION-*` finding of any kind |

`check_left_behind()` fired on exactly the 2 entries measured at draft time — **2 findings, 2 true
positives, 0 false positives over 759 entries** — and 68 selftest fixtures stayed green.

### Verification run at apply time

`domain-invariants` exit 0 · improvement-log gate exit 0 (0 unread, 0 awaiting-approval) ·
`verify-improvement-log.py --selftest` 68 fixtures, both copies · `verify-build-config.py` exit 0 ·
`verify-engine-instance-split.py` exit 0 · `generate-known-failure-modes.py --check` current at
759 entries · `verify-review-document.py` exit 0.

**`verify-derived-counts.py` — 3 drifted claims remain, none of them this review's.** The one this
review caused (the digest's own line count, 700 → 702, which regenerating the digest mechanically
drifts) was corrected in the same change. The other three are pre-existing and belong to the pass
that secured six columns on 2026-09-17/18: two secured-column counts in the Dev Summary (69 vs 75)
and one in `REV Trustee.xml` (53 vs 59), each off by exactly the six. Verified as pre-existing
against `HEAD`, not assumed. They are SOFT, they do not block, and both files are outside this
review's scope — the Dev Summary explicitly so, and the role XML is shipped solution source.
**Routed to `development-agent`, not fixed here.**

### Not published to the engine remote

Rows 1 and 5 touch `.engine`. Committing and pushing was not requested, so the changes are in the
working tree only. Publishing them is a submodule push **first**, verified with
`git -C .engine branch -r --contains HEAD`, then the pointer bump here — in that order.
