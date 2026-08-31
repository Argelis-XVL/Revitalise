# Improvement Review 39 — 2026-08-28

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 5 `unread` → 4 clusters
**Trigger:** the **unread `blocker`** trigger — `python3 scripts/verify-improvement-log.py --check`
reported `TRIGGER: 1 NEW entry(ies) of severity 'blocker' in state 'unread'` naming `IMP-0461`.
Processed on its own batch, immediately, per
[`improvement-agent.md` L82](../../agents/improvement-agent.md#L82).
**Gate:** `APPROVE IMPROVEMENTS` — ~~nothing in this document is on disk~~ **APPROVED 2026-08-28 by
Xander Lykopoulos and APPLIED IN FULL. §9 carries the record and the three deviations: change 3 was
amended after approval because two findings appended between the gate opening and the keyword
disproved two of its factual clauses; change 2's residual (a) was withheld on measurement; and
`IMP-0460` was deliberately left open because its `observable_at` is V5 and nothing here reached V5.
`verify-improvement-log.py` is OK, both triggers are cleared, and the digest is current — but
`verify-tad-coverage.py` is RED on a delivery-owned dead promise this review does not own (§9).**
**Scope:** the 5 `unread` entries (`IMP-0460`–`IMP-0464`). **No `APPLIED` or `REJECTED` entry was
read**, and the **81 `reviewer-deferred` entries are untouched** per activation step 2
([`improvement-agent.md` L103](../../agents/improvement-agent.md#L103)) — the dispatch's
"process everything you can dispose of yourself" does not widen this scope, and §5 names every
state excluded and what each parked group is waiting on.

**One `reviewer-deferred` entry IS read, deliberately, and it is the exception the rules name.**
`IMP-0412` carries the contradiction that `IMP-0460` is a second instance of, and change 1 writes a
field onto it. Activation step 8's clause applies in reverse here: *"a finding carrying `corrects`
against something you are about to act on is load-bearing regardless of its state"*
([`improvement-agent.md` L180](../../agents/improvement-agent.md#L180)). Its `deferred_reason` and
its `revisit_when` are **not edited** — only an edge is added, and §3 change 1 says why that is not
a re-derivation of a parked decision.

**Numbering:** 38 → 39. **WBS:** the five entries carry `wbs:6.9` where they carry one; the review
itself is `system` work and never billable
([`C-COM-002`](../../constraints/commercial/commercial-constraints.md#L35)). No contracted figure is
restated (D-3).

**Concurrency, and it bears on two of six changes.** A separate `architect-agent` dispatch is live
on **A-FLOW-08**, the money-average mechanism for the very four fields `IMP-0461` and `IMP-0462` are
about. `git status` shows [`contract/tad-deferrals.json`](../../contract/tad-deferrals.json), the
[TAD](../architecture/trustee-portal-visual-refresh-architecture.md) and four
`Workflows/REVPortalRoundStatistics*` files all `M`. Change 6 touches that register — one
documentation key in it, not an entry — and change 2's deferred half is explicitly gated on that
dispatch landing. Activation step 8 re-measures both before anything is applied
([`IMP-0405`](../../logs/improvement-log.jsonl)).

---

## Summary

**Six changes, zero new constraints, zero new scripts, and one proposal withheld because
measurement disproved it.** The constraint budget is untouched at **0 of 3**; both script edits go
inside gates that already exist, so the derived `verify-*.py` count stays at **51** and
[`improvement-agent.md` L356](../../agents/improvement-agent.md#L356) needs no edit.

**The blocker is real, its substance is already fixed, and what it handed me was two residual
weaknesses to weigh.** The gate blind spot — a status-free helper `Compose` classified as a non-ok
document and silently dropped — was fixed inside the dispatch that found it, and I re-ran the gate
to confirm: it now sees **7** OK-document nulls where it saw 4. Of the two residuals, **one is
withheld on measurement and one is applied in a narrowed form**, and both narrowings are recorded in
three places per [`improvement-agent.md` L184](../../agents/improvement-agent.md#L184).

**The withheld one is the interesting result.** The finding asked that a null response key which
neither the register nor any traceability row names should **FAIL** the build. Measured against the
real corpus that is **3 findings, 0 true positives** — all three are declared *collectively*, by one
traceability row reading *"the three proportions await OQ-039"*
([TAD L3462](../architecture/trustee-portal-visual-refresh-architecture.md#L3462)) and again in the
TAD's own response block. Detecting a collective declaration means matching a phrase, and that is
the instrument this repository has now measured at 48%–100% false five times over. So the intent is
kept and the enforcement is not: the gate now **names its unchecked set on every verdict** instead of
printing nothing about it.

**Two of the five findings are the same defect, and it already has a home.** A dispatch brief
asserted a platform semantic and a disclosure control, each with a citation attached, and neither
cited source said what it was cited for. [`lead-agent.md` L135](../../agents/lead-agent.md#L135)
already carries this rule for *"another document's revision, status or gate"*; change 5 widens its
object rather than adding a rule, which is what the second and third instance of one class are
supposed to produce.

**The digest gets a second, weaker edge kind, and this is the cheapest change here.** One lesson on
the one page every agent reads first carries two claims of very different standing —
`select()`/`filter()` ground-truthed and gate-enforced, then a trailing clause about `if()` that two
later findings dispute. `corrects` is the wrong field (it asserts the earlier entry is *wrong*), so
change 1 adds `contests` and sets one edge. Measured: the patched generator with no data change
reproduces the live digest **byte-for-byte**, and with the edge it adds **exactly one line, in the
right place — 1 finding, 1 true positive, 0 false**.

---

## 1. Regression check — did review 38's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [`verify-tad-coverage.py`](../../scripts/verify-tad-coverage.py#L632) assertions **(d)/(e)/(f)** — review 38 change 1 | 2026-08-28 | `gate-cannot-fail`, `no-assertion-on-shipped-content` | **YES — `IMP-0461`, `blocker`, hours later, on assertion (d) itself** | **Working, and mis-scoped in a third direction nobody could have measured.** See below |
| Same change, assertion **(f)** | 2026-08-28 | same | **YES, adjacently — `IMP-0462`** | **Working. (f) fired correctly; the new failure was a reader over-reading its verdict** |
| [`verify-superseded-column-writers.py`](../../scripts/verify-superseded-column-writers.py#L239) scope line — change 2 | 2026-08-28 | `gate-scope-mismatch` | **NO** | **Working.** Exits 0 and names its universe |
| [`how-to-log-an-improvement.md` L184](../../skills/how-to-log-an-improvement.md#L184) re-read-the-file rule — change 3 | 2026-08-28 | `finding-diagnosis-unverified` | **YES — `IMP-0462`** | **Prose, and the recurrence is a DIFFERENT half of the class.** See below |
| [`verify-assumption-markers.py`](../../scripts/verify-assumption-markers.py#L163) unquote + FAIL — change 4 | 2026-08-28 | `gate-fires-on-nothing` | **NO** | **No evidence either way.** Nothing in this batch touches it |
| [`verify-role-privilege-ownership.py`](../../scripts/verify-role-privilege-ownership.py#L417) de-dupe — change 5 | 2026-08-28 | `hand-maintained-count-drifts-from-source` | **NO** | **No evidence either way** |
| [`verify-provisioning-step-convergence.py`](../../scripts/verify-provisioning-step-convergence.py#L179) marker bytes — change 6 | 2026-08-28 | `output-shape-defeats-the-reader` | **NO** | **No evidence either way** |
| [`knowledge/technology/dataverse.md` L294](../../knowledge/technology/dataverse.md#L294) sweep-the-table-artefacts — change 7 | 2026-08-28 | `platform-contract-guessed-not-groundtruthed` | **NO** | **No evidence either way.** Prose |
| [`logs/improvement-log.jsonl`](../../logs/improvement-log.jsonl) false-`reviewed_in` correction — change 8 | 2026-08-28 | `learning-substrate-destroyed` | **NO** | **Working.** The gate reports 0 `awaiting-approval` and the five entries are disposable again |

The four audit questions, for the three recurrences:

- **Assertion (d) — was the change prose or a gate?** A gate, HARD, wired at
  [`build.yml` L617](../../config/revitalise-grant-automation-build.yml#L617). **Did the gate run?**
  Yes — and it **ran green while blind**, which is the worse outcome. **So is this
  `gate-cannot-fail`?** No, and the distinction matters: it fired correctly on everything in its
  model. Its classifier was a **two-way test over a three-way world** (ok document / non-ok document
  / status-free fragment) and the third branch defaulted to silence. **Why nothing could have caught
  it:** review 38 falsified (d) against a flow where all ten nulls sat in one action, and the
  fragment case *did not exist in that corpus* — the `wbs:6.9` build created it the same day by
  splitting a long `concat` into helper `Compose` actions, which is ordinary refactoring that nothing
  flags as gate-relevant. **This is the sharpest available example of the rule my own file states:**
  a gate's fixtures encode the author's model, and a corpus can grow a case the model never had.
- **The skill edit — was it prose?** Yes, and `IMP-0462` is a recurrence *of the class* and **not of
  the half that edit covers.** Review 38's rule was *"re-read a working-tree file before describing
  it"*. `IMP-0459` re-read the right file and read the **wrong depth**: it checked the top-level
  response key and concluded the metric shipped, while four sub-fields one action away were still
  null. **Altitude:** the second instance forbids another instance patch, and the general property
  here — *a metric is not a field* — is already written into `IMP-0462`'s own lesson and is enforced
  mechanically by the gate change 2 improves. No prose is added for it. **A third instance justifies
  a rule.**
- **Did the closure evidence match the level each defect was visible at?** Yes for review 38.
  Checked against this batch: **`IMP-0460`'s `observable_at` is V5 and this review does not claim to
  have reached V5** — §3 change 1 closes the *record* defect and §5 leaves the platform question
  open under `IMP-0412`'s own trigger, because settling it needs a live designer run nobody in this
  session can make ([`C-TECH-053`](../../constraints/technology/technology-constraints.md#L108)).

**And the one thing this audit establishes.** Review 38 closed by reporting assertion (d) at
*"4 findings / 4 true / 0 false"* against the state the defect shipped in. That measurement was
correct and the gate was blind within hours — not because the measurement was wrong, but because
**the artefact changed shape underneath it.** A gate measured against a corpus is proven against
*that* corpus. The durable lesson is `IMP-0461`'s own: *the tell is a null count that DROPS while
the artefact gains nulls* — and change 2 makes that count, and its buckets, printed on every run.

---

## 2. Clusters and promotion decisions

```
CLUSTER: gate-reassures-wrongly  (x1 unread: IMP-0461) — class total x23
Altitude:  INSTANCE, deliberately, and the general form is declined with a measurement.
           The blind spot itself is already fixed on disk by the dispatch that found it.
Ladder row: "a tool could catch it mechanically" — the gate exists; this is its disclosure
Becomes:   scripts/verify-tad-coverage.py — assertion (d) names its two silent buckets
Retires:   nothing
Cites:     IMP-0461, IMP-0458, IMP-0455
Residual:  Residual (a) is WITHHELD — 3 findings / 0 true / 3 false (§6a). Residual (b)'s
           ENFORCEMENT half is deferred: binding an acquittal to one action needs the
           register's `response_fields` syntax changed, and a concurrent dispatch holds
           that file. Detection ships now; enforcement is §5.
```

```
CLUSTER: two-recorded-lessons-contradict-each-other  (x1 unread: IMP-0460) — class x2 with IMP-0412
Altitude:  CLASS. Second instance of one recorded contradiction reaching live work, so the
           ladder forbids another note about if(). The property is general: THE DIGEST HAS NO
           WAY TO RENDER A DISPUTED CLAIM, only a disproved one.
Ladder row: "the system's own memory failed" → a read-path change
Becomes:   a `contests` edge kind in generate-known-failure-modes.py + verify-improvement-log.py,
           one edge set on IMP-0412, one line in how-to-log-an-improvement.md, and the date
           worked example in knowledge/technology/power-automate.md
Retires:   nothing
Cites:     IMP-0460, IMP-0412, IMP-0378, IMP-0124, IMP-0420
Residual:  A LESSON IS ONE STRING, so the marker cannot say WHICH clause is contested — and
           IMP-0124's contested clause is the tail of a sentence whose head is ground-truthed
           and gate-enforced. A reader who distrusts the whole lesson loses nothing
           operationally (check 1 of verify-flow-definition-language.py enforces the head),
           but the imprecision is real and no field can fix it.
```

```
CLUSTER: a cited authority does not say what it was cited for  (x2: IMP-0460, IMP-0464)
           — two class names, ONE property, both from the same dispatch brief
Altitude:  CLASS — and the rule already exists, scoped too narrowly. Widen, do not add.
Ladder row: "an agent had the information and still did the wrong thing" → an agent-file edit
Becomes:   agents/lead-agent.md rule 3, object widened from "another document's revision,
           status or gate" to any fact a brief asserts with a citation attached
Retires:   nothing
Cites:     IMP-0464, IMP-0460, IMP-0381
Residual:  NO GATE IS POSSIBLE, and this is not a judgement call. A dispatch brief is a Task-tool
           prompt: it is never a file, logs/routing.log records the decision and not the text, so
           there is nothing for a script to read. Both instances were caught by the RECEIVING
           agent ground-truthing before building, which is the only control that exists here and
           it worked twice.
```

```
CLUSTER: requirement-names-data-the-solution-cannot-supply (x1 unread: IMP-0463) — class x5
         + finding-diagnosis-unverified (x1 unread: IMP-0462) — class x14
Altitude:  KNOWLEDGE for IMP-0463, DATA CORRECTION for IMP-0462. Both are one-instance-with-a-
           general-cause, which the ladder puts in knowledge/ and not in a constraint row.
Becomes:   knowledge/technology/power-automate.md — the negative platform fact, ground-truthed
           this session from Microsoft's own reference, beside the aggregate-FetchXML boundary
           it belongs with; and contract/tad-deferrals.json — one documentation key that is now
           the exact opposite of true and is the most emphatic sentence in the file
Retires:   nothing
Cites:     IMP-0463, IMP-0462, IMP-0306, IMP-0455
Residual:  The knowledge note records THREE candidate mechanisms and their costs and CHOOSES
           NONE. Choosing is A-FLOW-08, and a concurrent architect-agent dispatch owns it. A
           review that picked one would be deciding an approved design's trade-off from here.
```

---

## 3. Changes proposed

| # | Type | Target | What | Cites | Provable? |
|---|---|---|---|---|---|
| 1 | script + data + skill | [`generate-known-failure-modes.py` L385](../../scripts/generate-known-failure-modes.py#L385) · [`verify-improvement-log.py` L388](../../scripts/verify-improvement-log.py#L388) · [`logs/improvement-log.jsonl`](../../logs/improvement-log.jsonl) · [`how-to-log-an-improvement.md` L178](../../skills/how-to-log-an-improvement.md#L178) | A **`contests`** edge kind: same shapes as `corrects` (string or list), rendered as **⚠ CONTESTED** and suppressed when a `corrects` marker already stands. Validated for type and target resolution, and **deliberately given no review-interval warning** (§6b). One edge set: `IMP-0412` contests `IMP-0124` | IMP-0460, IMP-0412, IMP-0378, IMP-0420 | **YES** — inert without data (digest byte-identical); **1 finding / 1 true / 0 false** with the edge; both negative cases fire; validator selftest 64 fixtures OK. §6b |
| 2 | gate extension | [`verify-tad-coverage.py` L851](../../scripts/verify-tad-coverage.py#L851) and [L1496](../../scripts/verify-tad-coverage.py#L1496), inside the already-HARD [`tad-coverage` step](../../config/revitalise-grant-automation-build.yml#L617) | Assertion (d) **names its two silent buckets on every verdict**: the keys no register entry and no traceability row NAMES (so it does not fail on them, and says so), and the keys composed as null in **more than one action**, so one acquittal covering three is visible. `flow_null_response_keys` returns every composing action, not the first | IMP-0461, IMP-0458 | **YES** — verdict unchanged (exit 0), selftest **32 cases / 19 known-bad rejected** identical to pre-patch, and the run now names `averageAmountRequested ×3 actions` and the 3 unchecked keys. §6a |
| 3 | knowledge | [`power-automate.md` L85](../../knowledge/technology/power-automate.md#L74), directly after the aggregate-FetchXML boundary | **There is no sum over an array.** The math set, quoted from Microsoft; `add` is binary; `max`/`min` are the only two that take an array; so a total over a FIXED operand count nests `add()` and a total over a filtered subset is inexpressible. Names the three candidate mechanisms with their costs and chooses none. Names the **`sum`/`average` trap**: Bot Framework *Adaptive expressions* has both, and its reference page is one search result away | IMP-0463, IMP-0306 | **YES** — ground-truthed this session against Microsoft Learn's *Reference guide to functions in expressions for workflows in Azure Logic Apps and Power Automate*, §Math functions. §6c |
| 4 | knowledge | [`power-automate.md` L121](../../knowledge/technology/power-automate.md#L121) | A second worked example in the existing `if()` block: `coalesce(<maybe-null date>, <a real timestamp>)` **before** `ticks()`/`formatDateTime()`, which throw on null — the guard shape that actually cost work. Plus one line recording that the digest now marks the contested lesson | IMP-0460 | Prose. The pattern is on disk in the shipped flow; the semantics question stays open (§5) |
| 5 | agent file | [`lead-agent.md` L135](../../agents/lead-agent.md#L135) | Widen rule 3's object: a brief asserting **any** fact with a citation attached — a platform semantic, a security or disclosure control, a requirement's status — quotes the line, or marks it unverified. Adds the two instances and the reason no gate is possible | IMP-0464, IMP-0460, IMP-0381 | Prose, necessarily. A Task prompt is not a file (§6d) |
| 6 | data | [`tad-deferrals.json` L44](../../contract/tad-deferrals.json#L44) | Rewrite `_undelivered_requirements_is_read_by_no_gate`: the gate **does** read the key, `response_fields` must be **leaf key names** and a dotted path fails as a dead promise, and a satisfied entry may need **narrowing** rather than deletion. Prior text retained and marked superseded, per this file's own convention | IMP-0462, IMP-0455, IMP-0459 | **YES** — the gate reports *"2 undelivered-requirement entry(ies)"* and acquits three keys from `UR-003`, against a key asserting in capitals that no gate reads it |

**No new script, so the derived `verify-*.py` count stays at 51** and
[`improvement-agent.md` L356](../../agents/improvement-agent.md#L356) needs no edit. Derived at draft
time, to be re-derived at application: `ls scripts/verify-*.py | wc -l` → **51**. Both script changes
extend gates that already carry the exact assertion being improved, which is the anti-bloat-correct
choice: change 2 lives inside [`C-TECH-066`](../../constraints/technology/technology-constraints.md#L136)'s
own gate, and change 1 lives inside the two scripts that already own the `corrects` edge.

---

## 4. Retirement — considered, one candidate, rejected for cause

- **The `if not hosts: continue` branch at
  [`verify-tad-coverage.py` L851](../../scripts/verify-tad-coverage.py#L851)** — the exact line
  `IMP-0461` asks to be removed, and the only genuine retirement candidate in this batch.
  **Rejected on measurement:** removing it produces 3 findings and 0 true positives (§6a). It is not
  dead code and it is not a waiver; it is a correctly-derived exclusion whose only fault was
  printing nothing. Change 2 keeps the branch and makes it speak.
- **`corrects`, on the argument that `contests` subsumes it.** Rejected immediately: they assert
  different things, and change 1's suppression rule depends on both existing —
  *wrong* subsumes *disputed*, so a lesson carrying both renders only the stronger marker.

Derived, not typed: `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` → **10** retired rows
against **80** live ones. No constraint row is added, retired or amended by this review.

---

## 5. Deferrals and routing — what this review does NOT close, and why

**Queue states excluded from scope, named per the no-silent-caps rule.** The gate reports 86 `NEW`:
**5 `unread`** (this review's whole scope), **0 `awaiting-approval`**, **81 `reviewer-deferred`**,
**0 `already-fixed`**, **0 `approved-not-applied`**. The 81 deferred entries each carry a
`deferred_reason` a human accepted and are left alone; **1 of them (`IMP-0274`) still names no
`revisit_when`**, which the gate reports as *"a decision to never do it"* and which this review does
not resolve — it is a reviewer decision, not a finding.

**Four `corrects` warnings stand and none of them touches this review's changes.** The gate warns on
`IMP-0290`, `IMP-0298`, `IMP-0320` and `IMP-0437`, each asking that a later correcting entry be
stamped by the review that processes it. Checked one at a time against this review's six changes:
none names a file, gate or premise any change here depends on. They are stale bookkeeping on earlier
reviews and stay open.

**Residual (b)'s enforcement half — deferred, with a trigger.** Change 2 makes the multiplicity
visible; it does not yet make an acquittal *bind* to one action. Doing that requires
`response_fields` to accept a qualified form, which means editing the register's syntax — and both
`UR-002` and `UR-003` cover exactly the four fields the concurrent **A-FLOW-08** dispatch is choosing
a mechanism for. Whatever it decides, those two entries change or disappear. **Revisit when
A-FLOW-08 lands and the register's entries are settled**; if a leaf key is then still shared between
two requirements, qualify it. Building it now would edit another dispatch's open file to enforce a
rule against entries that are about to be rewritten.

**The platform semantics of `if()` — still open, and this review does not close it.** `IMP-0460` is
`observable_at` V5 and change 1 fixes the *record*, not the platform question. `IMP-0412`'s
`revisit_when` is applied verbatim and unedited: one deliberate live run of an `if()` whose untaken
branch divides by zero. Nobody in this session can make that observation.

**A SOFT gate is red on three claims this review does not touch.**
`python3 scripts/verify-derived-counts.py` reports 3 drifted claims — two secured-column figures in
the [Dev Summary](../development/revitalise-grant-automation-dev-summary.md) and one in the
[REV Trustee role header](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Trustee/REV%20Trustee.xml)
— all saying 67/51 where source says 68/52. **Already covered by two open findings** (`IMP-0263`
and `IMP-0444`, both `reviewer-deferred`, both about exactly this count moving), so no new finding is
appended. It is delivery-owned prose about secured columns and belongs to whoever secures the next
column, not to this review.

**Not routed anywhere, and stated so it is not mistaken for an omission:** `IMP-0464` proposed no
rule change at all, and I agree with that half of its own disposition — the SDD's struck-through
NFR-027, FR-059's inline clause and the TAD's §6.3.3 tripwire are all correctly placed and all three
worked. Its contribution to this review is as the **second instance** that made change 5 a widening
rather than a note.

---

## 6. Measurements

### 6a. Assertion (d)'s two residuals — one withheld, one narrowed

**Residual (a), the FAIL that `IMP-0461` asked for: 3 findings, 0 true positives, 3 false
positives. WITHHELD.**

Enumerated against the real corpus, the OK-document nulls that no register entry and no traceability
row **names**:

| Key | Named anywhere by name? | Declared? | Verdict |
|---|---|---|---|
| `highHoursCareProportion` | No | **Yes — collectively**, [TAD L3462](../architecture/trustee-portal-visual-refresh-architecture.md#L3462) *"the three proportions await OQ-039"*, and [TAD L1234](../architecture/trustee-portal-visual-refresh-architecture.md#L1234) *"null until its `rev_setting` threshold is seeded"* | **FALSE POSITIVE** |
| `lowLifeSatisfactionProportion` | No | Same row, same block | **FALSE POSITIVE** |
| `unableToTakeBreakProportion` | No | Same row, same block | **FALSE POSITIVE** |

All three named, per [`improvement-agent.md` L198](../../agents/improvement-agent.md#L198): *a
narrowing removes findings that would have been wrong and can name them.* The finding's premise — *"a
null nobody has written down anywhere"* — is false for every member of the set it would fire on.
Making it FAIL would have turned the HARD `tad-coverage` step red against a correctly documented
design, and the only way to green it would have been to add three individual markers to satisfy a
matcher, which is documentation written for a gate rather than for a reader.

**Why no phrase-based variant was attempted.** A collective declaration is prose. Matching it is the
instrument [`improvement-agent.md` L426](../../agents/improvement-agent.md#L426) records as measured
at 48%–100% false across five instances in three reviews, and this corpus offers no *value* to assert
on instead. The available assertion is the one already there.

**Residual (b), the leaf-versus-path collapse: real, and measured exactly.**
`averageAmountRequested` is composed as a literal null in **three** actions —
`Compose_breaktype_rows` (×5, one per break type), `Compose_breaktype_total`, and
`Compose_exceptional_funding_summary` — and those belong to **two different requirements** carried by
**two different register entries** (`UR-002` for FR-059's, `UR-003` for FR-060's). The pre-change gate
reported **one** key, attributed to **one** entry:

```
ACQUITTED: averageAmountRequested ← register UR-003        ← UR-002 also names it; overwritten
```

The concrete hole: delete `UR-002` and the FR-059 occurrence stays acquitted by `UR-003`, which does
not cover it, and assertion (f) cannot see the dead promise because the leaf name is still null
elsewhere. **Detection ships (below); enforcement is deferred with a trigger (§5).**

**The patched gate against the real corpus — verdict unchanged, disclosure added:**

```
verify-tad-coverage: OK — … 7 null response key(s) …
  ACQUITTED, never suppressed silently: averageAmountRequested ← register UR-003;
    averageCost ← register UR-003; ethnicGroupDistribution ← Appendix A marker;
    percentageOfCost ← register UR-003.
  COMPOSED AS NULL IN MORE THAN ONE ACTION, so one acquittal covers all of them:
    averageAmountRequested ×3 actions; averageCost ×2 actions; percentageOfCost ×2 actions.
  NOT CHECKED — no register entry and no Appendix A row NAMES these, so assertion (d) has
    nothing to compare and does not fail on them; a collective declaration in prose is not
    machine-readable: highHoursCareProportion (…→ Compose_response_body);
    lowLifeSatisfactionProportion (…); unableToTakeBreakProportion (…).
```

**Selftest, pre- and post-patch, identical:** `32 case(s): 19 known-bad fixtures rejected, 13 valid
fixtures accepted`. **0 new findings, 0 false positives, exit 0 both before and after** — this change
adds no verdict and removes no coverage.

**And the re-observation `IMP-0461` needs to be closable.** Its `observable_at` is V1 and its claim
is about a script's behaviour, which
[`improvement-agent.md` L136](../../agents/improvement-agent.md#L136) says is settled by **executing**
it. Executed: the gate reports **7** OK-document nulls, including `averageCost ← Compose_breaktype_rows`
and `averageAmountRequested ← Compose_exceptional_funding_summary`, both of which are helper
`Compose` actions that the pre-fix classifier filed as non-ok. Before the fix it saw **4**. The
fragment-attribution fix is on disk and working.

### 6b. The `contests` edge — inert without data, exact with it

**Step 1, the polarity control: patched generator + UNPATCHED log reproduces the live digest
byte-for-byte.** No collateral churn, so any delta below is attributable to the one edge and nothing
else.

**Step 2, with `IMP-0412 contests IMP-0124` — the whole delta, all of it:**

```
154a155
>   <br><sub>**⚠ CONTESTED by `IMP-0412`** — a later finding disputes a claim in this lesson
>   and NEITHER has been re-tested. Read that entry before relying on this one; it carries the
>   form that is safe under either answer.</sub>
```

**1 finding, 1 true positive, 0 false positives**, rendered directly beneath `IMP-0124`'s lesson at
[`known-failure-modes.md` L153](../../logs/known-failure-modes.md#L153) — the line whose trailing
clause a `wbs:6.9` dispatch brief quoted as settled ground truth.

**Step 3, the suppression rule, which the corpus cannot test.** No lesson carries both edges today,
so this was measured on a synthetic case: `IMP-0378 corrects IMP-0124` **and** `IMP-0412 contests
IMP-0124` renders **one** line — the CORRECTED one — and `grep -c CONTESTED` returns **0**. *Wrong*
subsumes *disputed*; two markers on one lesson are noise.

**Step 4, it can fail.** Validator selftest: **64 fixtures, all pass** — nothing pre-existing broke.
Both negative cases fire:

```
WARNING: IMP-0412: contests 'IMP-9999', which is not an entry in this log — check the reference…
ERROR:   IMP-0463: contests must be a finding id as a string, or a list of them, got int
```

**What change 1 deliberately does NOT add, and why.** `corrects` carries two review-interval
warnings; `contests` gets neither. The first asks *"did a review draft a change on a diagnosis since
DISPROVED?"* — a contest disproves nothing by construction, so a review acting on the target is not
acting on a falsified premise. The second asks *"did the fix land while the corrected entry stayed
unread?"* — there is no fix; an open contest is settled by a live run, not a commit. Emitting either
would put a permanent warning on `IMP-0124` that is noise every time, which is how a gate teaches
people to route around it (`IMP-0181`).

**Why not simply set `corrects`, which needed no code at all.** Because it would be false in the
register the field is read in. [`how-to-log-an-improvement.md` L128](../../skills/how-to-log-an-improvement.md#L128)
defines `corrects` as *"the earlier entry's `root_cause`, `lesson` or `proposed_change` is **wrong**,
not merely incomplete"*; `IMP-0412`'s own `revisit_when` reserves it for whichever claim eventually
**loses**; and [`power-automate.md` L132](../../knowledge/technology/power-automate.md#L132) says the
same in the knowledge file. `IMP-0460` withheld the edge for exactly this reason and said so. Three
records agree, and overloading the field would have quietly contradicted all three to save nine
lines.

### 6c. The negative platform fact — ground-truthed, not recalled

`IMP-0463`'s root cause is a claim about what the expression language **lacks**, which is the shape
[`how-to-promote-a-finding.md` §4](../../skills/how-to-promote-a-finding.md#L149) warns is argued
rather than confirmed. Fetched this session from Microsoft Learn, *Reference guide to functions in
expressions for workflows in Azure Logic Apps and Power Automate* → **Math functions**:

> add · div · max · min · mod · mul · pow · rand · range · sub

No `sum`. No `average`. `add(<summand1>, <summand2>)` takes exactly two operands. The finding's
statement is confirmed verbatim.

**Two things the finding did not have, both worth recording.** First, `max` and `min` are documented
as *"Return the highest value from a set of numbers **or an array**"*, with
`min(createArray(1, 2, 3))` as Microsoft's own example — so they are the **only** two math functions
that take a variable-length collection, which is both a real capability and the reason
`max(divisor, 1)` is available as the safe divisor pattern. Second, the **trap**: Bot Framework's
*Adaptive expressions* reference has `sum`, `average`, `floor`, `ceiling` and `round`, and its page
sits one search result away from the one that governs here. A note recording only the absence would
leave the next author to find `sum` on the wrong page.

**Level reached: V1 for the mechanism candidates, and the note says so.** The `xpath(xml(...),
'sum(...)')` route is **unverified on this tenant** and is recorded as unverified, with the reason it
is dangerous rather than merely unproven: a silent `0` on malformed input puts a wrong money figure
on a board pack. No mechanism is chosen (§5).

### 6d. Why change 5 is prose, stated as a measurement and not a preference

A dispatch brief is a Task-tool prompt. It is never written to a file;
[`logs/routing.log`](../../logs/routing.log) records the routing decision and the WBS id, not the
brief's text. **There is no artefact for a gate to read**, so no script can compare a brief's claim
against its cited source — and this is not an argument that a gate would be hard, it is that its
input does not exist. Both instances in this batch were caught the only way they can be: the
receiving agent read the cited source before building on it. `IMP-0464` found the withdrawn NFR-027
by reading FR-059's requirement text; `IMP-0460` found the contradiction by checking the finding id
the brief quoted. The rule's job is to make that the expected step rather than a diligent one.

---

## 7. What you need to decide

**Nothing blocks approval.** All six changes are drafted, measured and independent of each other; the
two decisions below are about what happens *after* the keyword, and neither changes what is applied.

**Should the deferred enforcement half of assertion (d) be scheduled, or left to the trigger?**

Change 2 makes it visible that one register entry is acquitting three actions across two
requirements. Making the acquittal *bind* to a specific action needs the register's `response_fields`
to accept a qualified form — and the two entries involved cover precisely the four fields the
concurrent A-FLOW-08 dispatch is choosing a mechanism for, so they are likely to be rewritten or
deleted within days.

My recommendation is to leave it on the trigger in §5 rather than schedule it: building it now means
editing an open file to enforce a rule against entries that are about to change. If you would rather
it were closed regardless of A-FLOW-08, say so and it becomes a change in the next review.

**Do you want the three collectively-declared nulls named individually, so the gate can check
them?**

Right now `highHoursCareProportion`, `lowLifeSatisfactionProportion` and
`unableToTakeBreakProportion` are declared as a group by one traceability row, which a machine cannot
match. That is why change 2 reports them instead of failing on them.

Adding each key by name to a register entry would make all three genuinely checked, with an owner and
an expiry date, and it would cost one edit. I have not proposed it, because the register is
architect-agent's and this would be a real change to a phased-delivery record rather than a
correction — but it is the one edit that would convert three reported-but-unchecked nulls into
checked ones, and it is cheap. Say the word and it routes to `architect-agent`.

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-28-improvement-review-9.md

Findings processed: 5 NEW (unread)  →  4 clusters
Regression check:   9 prior changes audited, 3 classes recurred
Proposed:           0 constraints (cap 3), 2 gate/script edits, 3 skill/knowledge edits,
                    1 agent-file edit, 1 data correction, 0 retirements
Altitude calls:     2 generalised from instance to class, 1 left as an instance with a
                    measurement, 1 withheld on measurement (3 findings / 0 true positives)
Digest:             will regenerate — 460 lessons, 37 recurring classes, +1 CONTESTED marker

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

**Verification actually executed at draft time:** `verify-tad-coverage.py --selftest` 32/32 (19
known-bad rejected, identical pre- and post-patch); `verify-tad-coverage.py` against the real corpus,
exit 0 before and after; `verify-improvement-log.py --selftest` 64/64; `verify-improvement-log.py
--check` against the patched log, 1 problem (the pre-existing blocker trigger, unchanged);
`generate-known-failure-modes.py --stdout` twice, delta of exactly 1 line; `verify-derived-counts.py`
3 pre-existing SOFT drifts, none of them this review's claims. Microsoft Learn fetched once for the
math-function set.

**Not verified, and named:** the `if()` semantics question (needs a live designer run — §5); the
`xpath(xml(...), 'sum(...)')` mechanism recorded in change 3 (**unverified on this tenant**, recorded
as unverified); and change 6's target file, which is `M` in `git status` under a concurrent dispatch
and will be re-read before the edit per activation step 8.

---

## 9. Applied — the record

**APPROVED 2026-08-28 by Xander Lykopoulos and APPLIED IN FULL — six changes, with one amended after
approval and one entry deliberately left open.** `verify-improvement-log.py` reports **OK (schema +
triggers)** over 466 entries; the **blocker trigger and the batch trigger are both cleared**; the
digest is current at 465 distinct lessons.

| # | Change | Landed | Entry closed |
|---|---|---|---|
| 1 | `contests` edge kind — [generator](../../scripts/generate-known-failure-modes.py) + [validator](../../scripts/verify-improvement-log.py) + `IMP-0412 contests IMP-0124` + [skill](../../skills/how-to-log-an-improvement.md) | ✅ | `IMP-0460` **left open** (below) |
| 2 | [`verify-tad-coverage.py`](../../scripts/verify-tad-coverage.py) assertion (d) names its silent buckets | ✅ **narrowed** | `IMP-0461` → APPLIED |
| 3 | [`power-automate.md`](../../knowledge/technology/power-automate.md) — no `sum()` over an array, and the xpath route | ✅ **amended** | `IMP-0463` → APPLIED |
| 4 | Same file — the date worked example in the `if()` block | ✅ | (change 1's entry) |
| 5 | [`lead-agent.md`](../../agents/lead-agent.md) rule 3 widened | ✅ | `IMP-0464` → APPLIED |
| 6 | [`tad-deferrals.json`](../../contract/tad-deferrals.json) — the false documentation key | ✅ | `IMP-0462` → APPLIED |

### Three deviations from the approved draft, none silent

**1. Change 3 was AMENDED because two findings appended after the gate opened disproved its
wording.** `IMP-0466` and `IMP-0467` landed at 20:12 and 20:14, between the gate opening and the
keyword. The approved text described `xpath(xml(...), 'sum(...)')` as *"unverified on this tenant"*
with *"a silent 0 on malformed input"*. Both clauses are false:

- It is **first-party documented** — Example 7 of Microsoft's Logic Apps expression-functions
  reference, `sum(/produce/item/count)` → `30` — and the same page names the **.NET XPath library**,
  fixing the semantics as XPath 1.0. Verified independently this session, not taken from the finding.
- The real failure modes are **different and worse**: an empty node-set returns `0`; **any**
  non-numeric leaf returns **`NaN` for the whole sum**, `NaN` is not valid JSON, so one blank money
  cell destroys the **entire** response document rather than one figure. All three money columns on
  `rev_application` are `RequiredLevel None`, so blanks are certain.

Applied verbatim, the approved wording would have written two false statements into a knowledge file
— [`improvement-agent.md` L156](../../agents/improvement-agent.md#L156) is the clause that catches
this, and this is its second recorded instance. The change's **intent is unchanged**: record the
negative fact, name the mechanisms with costs, choose none.

**2. Change 2's residual (a) was WITHHELD, re-measured against the corpus as it stands now.** Still
**3 findings, 0 true positives** — `highHoursCareProportion`, `lowLifeSatisfactionProportion`,
`unableToTakeBreakProportion`, all three declared collectively and none individually. The narrowing
names the false positives it removes, which is the test that separates it from a substitution.

**3. `IMP-0460` was NOT closed, and this is the honest outcome rather than an omission.** Its
`observable_at` is **V5**; `verify-improvement-log.py` refuses a closure whose `reobserved.level`
sits below that, and correctly. Everything it asked for is on disk — the digest marker, the date
worked example, the widened brief rule, the documented field — but whether `if()` short-circuits is
still one live designer run from settled. Relabelling the entry V1 to permit closure would be
precisely the false closure `IMP-0208`/`IMP-0224` record. It is now `reviewer-deferred` with a
`deferred_reason` naming what shipped and `IMP-0412`'s trigger applied **verbatim**.

### What the corpus did underneath this review, and what it cost

**The concurrent dispatch shipped all four money measures between the gate opening and the keyword.**
Re-measured at application time:

| | At draft (19:xx) | At application (21:0x) |
|---|---|---|
| OK-document nulls | 7 | **4** |
| Keys null in >1 action | 3 (`×3`, `×2`, `×2`) | **0** |
| Unaccounted-bucket keys | 3 | **3** (unchanged) |
| Gate exit code | 0 | **1** — four assertion-(f) dead promises |

So **change 2's multiplicity disclosure now reports nothing on this corpus**, because the nulls it
was measured against shipped. The code is unchanged and correct — it fires whenever multiplicity
returns — but the measurement in §6a is evidence about the corpus of 19:xx, and saying otherwise
would be claiming a measurement I can no longer make. **Change 2 added no violation**: the same four
assertion-(f) errors were present before it was applied.

### Routed, not fixed — and one of them is a live red gate

**`verify-tad-coverage.py` exits 1 right now.** `UR-002` and `UR-003` are genuine dead promises: the
four money measures they defer have shipped. This is a **HARD** build step, so the next build halts
on it. **Clearing it is delivery's action, not this review's** — deleting the two entries without
correcting the TAD Appendix A rows in the same change produces the mirror-image overclaim (a
traceability row reading UNDELIVERED for a field that now has a producer, `IMP-0451`'s class with
the sign reversed), and `improvement-agent` does not own this register's entries. Recorded inside the
key itself; owner is the dispatch that shipped the measures.

**Three findings are out of scope here and have NOT been processed in this review**, deliberately:
`IMP-0465` (a wired gate's docstring says it is not wired), `IMP-0468` (two approved documents give
contradictory disclosure instructions for the four money measures) and `IMP-0469` (a `rev_setting`
key that encodes a reviewer risk decision is indistinguishable from a convenience tunable beside
it). None is touched, and each needs its own dispatch.

**Two more — `IMP-0466` and `IMP-0467` — were PARTLY acted on, so they are recorded as deferred
rather than left reading as unopened.** Their platform facts corrected change 3 (see the first
deviation above), which means a later reader must not find them looking like findings nobody had
opened — that is `IMP-0154`'s defect. Each now carries a `deferred_reason` naming what landed and a
`revisit_when` for what did not: their proposed **check 8** for
`verify-flow-definition-language.py`, which is a genuine altitude decision needing corpus
measurement and which collides with `IMP-0460`'s request for the same slot.

**`IMP-0467` and `IMP-0460` both want the same `check 8` slot.** Designing that check twice is
`IMP-0443`'s defect, so neither was built here and `IMP-0460`'s `deferred_reason` says so. They
belong in one pass.

**The suppression question reopened after `IMP-0464` was written — and neither of the two findings
that reopened it is in this review's scope.** `IMP-0464`'s lesson says *"do not add a threshold
without a NEW dated reviewer decision"* — and one arrived: OQ-043 answered **k=5** (`IMP-0469`),
with `IMP-0468` recording that the SDD withdrawal and the TAD tripwire actually conflict for these
four measures. Both are named here only for context and are **not processed in this review**. The
lesson's rule was satisfied, not violated; `IMP-0464`'s `applied_by` carries that so the digest
cannot teach a stale conclusion.

### One finding appended by this application: `IMP-0471`

**Applying this review tripped one of its own gates, three times, and the gate was wrong each time.**
`check_citation_stamps()` warned that the five late findings were *"cited by a review document and
carry NO `reviewed_in`"* — when §9 named them precisely to say it had **not** processed them, which
is the exact defect [`IMP-0196`](../../logs/improvement-log.jsonl) established and this check's own
docstring disclaims. `SCOPE_DISCLAIMER` has the cue *"left unprocessed"* and not *"left unread"*, and
a disclaimer governs **one paragraph**, so two ids cleared only after the same clause was repeated in
a later paragraph whose purpose was context rather than disposition.

**This is the third instance of one shape, and the altitude rule therefore forbids the obvious fix.**
`IMP-0196` added the heading rule; review 19 change 7 added the paragraph rule; both widened the same
phrase-matching design, which guarantees the next unmatched phrasing. Adding *"left unread"* to the
cue list would be a fourth instance patch. **Deliberately not fixed here** — it is this review's own
gate, and widening the rule while applying it is fixing the rule under test. `IMP-0471` carries the
general proposal: have a review declare its dispositions in one machine-readable position and read
**that**, rather than inferring intent from the prose around an id.

### Verification executed at application time

`verify-improvement-log.py --selftest` **64/64**; `verify-improvement-log.py --check` **OK (schema +
triggers)**, **468 entries, 0 triggers, 5 unread, 4 warnings — all four pre-existing `corrects`
stamps** (§5, untouched);
`verify-tad-coverage.py --selftest` **32 cases / 19 known-bad rejected**, identical pre- and
post-change; `verify-tad-coverage.py` real corpus, four assertion-(f) errors both before and after;
`generate-known-failure-modes.py` written and `--check` current, **CONTESTED marker present at
[L155](../../logs/known-failure-modes.md#L155)**; `verify-review-document.py --only` this document
**OK**; JSON re-parsed after change 6 with `deferrals` and `undelivered_requirements`
**byte-identical**. Derived, not typed: **51** `verify-*.py` scripts, **10** retired against **80**
live constraint rows, **37** recurring classes — all unchanged, so
[`improvement-agent.md` L356](../../agents/improvement-agent.md#L356) needs no edit.

**`verify-derived-counts.py` is SOFT-red on four claims and this review introduced none of them.**
Three are the pre-existing secured-column figures already carried by `IMP-0263` and `IMP-0444`. The
fourth appeared during application: [`pipeline.yml` L531](../../config/revitalise-grant-automation-pipeline.yml#L531)
says *"the fourteen `rev_setting` rows"* and source now holds **15** — the concurrent dispatch added
the `k=5` disclosure key that `IMP-0469` records, and that finding is **not processed in this
review**. Delivery-owned, and routed rather than fixed.

*(That sentence needed its own non-scope clause to stop `check_citation_stamps()` warning about a
finding this section had already declared out of scope two paragraphs earlier — the fourth occurrence
of `IMP-0471`'s defect, met while writing the paragraph that reports it.)*

**Not verified, and named:** the `if()` semantics (needs a live designer run); the `xpath` sum route
(documented and attributable, **no run on this tenant has produced a figure from it** — recorded as
V1 in the knowledge file itself); and `IMP-0467`'s XPath 1.0 failure modes, which that finding
measured and I confirmed only as to the engine attribution.
