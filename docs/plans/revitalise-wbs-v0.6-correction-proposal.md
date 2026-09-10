# WBS v0.6 Correction Proposal — DRAFT, NOT YET CLIENT-ACCEPTED

**Status:** DRAFT — for reviewer sign-off, then external client acceptance. **Nothing in
`contract/` treats v0.6 as accepted, and nothing in this document may be read as though it
already is.**
**Raised by:** pm-agent, `feature:system` (WBS-wide correction, not scoped to one automation)
**Reverses:** the 2026-08-19 "no v0.6" decision recorded in `scripts/import-baseline.py`
(`WBS_IS_FINAL = True`, `KNOWN_GAP.resolution`) and `contract/README.md`. That reversal is
**itself** a reviewer decision this document assumes was already made (per the dispatch that
requested this draft) — it is not re-argued here.

---

## 1. The correction that drives this proposal

**WBS task 8.3 ("Build payment capture form") must contractually depend on task 8.2 ("Build
finance security role"), not only on 8.1.**

| | Current (v0.5) | Proposed (v0.6) |
|---|---|---|
| Task 8.3, "Depends On" column | `8.1` | `8.1, 8.2` |

**Why.** 8.3 is the payment capture form for the finance role. The Bank Account and Payment
columns it binds are secured under `REV_FinanceOnly`, whose only intended member is the REV
Finance role's group team — built by 8.2, not 8.1. On the v0.5 graph as written, 8.3 could be
built and even reach completion before the role meant to be the only thing able to see it
exists, producing a form nobody can read. This is not a hypothetical: `wbs-ready-set.py` and its
build-order union already encode this edge non-contractually, and 8.3 is derived `partial` today
regardless of this dependency — but the graph itself still under-states its own precondition.

**Where this already lives, non-contractually, today:**
`contract/delivery-parameters.json` → `build_order_constraints.edges[0]`
(`contract/delivery-parameters.json#L88`), authorised 2026-09-09, finding `IMP-0676`. That block
exists **because** `contract/wbs.json` is generated verbatim from the accepted workbook's own
`Depends On` column and a hand-edit to it would be silently erased by the next
`import-baseline.py` run — the edge could only be added where it would not require touching an
accepted source. If v0.6 is really happening, this is the one item that stops being a
workaround and becomes a proper correction to the workbook itself: **the v0.6 workbook's row for
task 8.3 should read `8.1, 8.2` in Depends On**, and once that revision is accepted the
non-contractual edge in `delivery-parameters.json` should be retired (it will have become
redundant, not wrong — see §3).

---

## 2. Other corrections already on record — checked, not bundled

`contract/README.md` (`contract/README.md#L51`) names exactly two items that used to be
routed toward "wait for v0.6" before that route was closed on 2026-08-19. Both were re-checked
against current state before writing this section, per this project's own rule never to restate
a status without re-deriving it.

**2a. The 20-hour DocuSign selection/trial gap (`IMP-0064`) — do NOT fold into v0.6.**

This is not simply "an item that was waiting for a v0.6 that wasn't coming." It was
**independently withdrawn from ever needing one**, by the reviewer, on 2026-08-20 —
`docs/Import/baseline-lock.yml` → `a2_docusign_and_rework_hours`
(`docs/Import/baseline-lock.yml#L237`), finding `IMP-0098`. The reviewer's own words: *"The work
for Docusign was not scoped in the WBS and falls completely out of it… no v0.6 task should carry
it."* The 20 hours cover platform selection **and** documentation rework after a solution design
change — neither is WBS-shaped work, and the reviewer explicitly said the earlier plan to carry
it as a v0.6 task was wrong on its own terms, not merely blocked by "no v0.6 coming." Reversing
the no-v0.6 policy does not reopen a question the reviewer already answered a different way.
**Recommendation: leave it exactly where it is** — `KNOWN_GAP` in `scripts/import-baseline.py`
(`scripts/import-baseline.py#L71`), permanently understating v0.5's total by 20 hours, already
invoiced (`WL-0002`). If v0.6 is issued, `KNOWN_GAP.resolution` should be reworded from
`NO_V06_WILL_BE_ISSUED` to record that v0.6 exists but does not carry this item, by design —
a wording fix, not a scope change.

**2b. Task 0.4's status claim (`IMP-0030`, exception `EX-001`) — do NOT bundle as-is; optional
administrative line only.**

`EX-001` (`contract/known-exceptions.json`) is **open** — 0.4 still claims `Done` against five of
its eight named tables (Review, Provider, Bank Account, Payment, the Anonymised Statistic
snapshot) being absent from the solution — but its own `clears_when` is explicit: *"There is no
v0.6 to restate 0.4's status, so this cannot be cleared by correcting the document — only by
building what the claim asserts."* That mechanism doesn't change if v0.6 exists: a v0.6 row
correcting 0.4's Status column to "Partially done" does not build the Review, Provider, Bank
Account or Payment tables, and `verify-wbs-chain.py` derives completion from evidence
(`logs/state/wbs-state.json`) regardless of what the Status cell says. **Recommendation:** if the
reviewer wants v0.6 to be comprehensive, a corrected Status cell for 0.4 costs nothing and closes
a long-standing paper inaccuracy in the accepted specification — but it is optional, does not
clear `EX-001`, and should not be presented to the client as resolving anything.

**A third item surfaced during this check, not previously named as a "v0.6 candidate":**
exception `EX-002` — the Grant Administration model-driven app (`rev_grantadministration`) is
shipped and implied by tasks 0.4 and 2.2 but named by neither. Unlike 0.4's status, this is a
genuine content gap in the specification (a deliverable that exists and is used but was never
written down), the same shape as the 8.3 dependency edge. **Recommendation: if v0.6 is being
issued anyway, add `rev_grantadministration` as a named deliverable under 0.4 or 2.2** — it is
the cheapest of the three to fold in and the only one of the three that a workbook edit actually
resolves outright (it clears `EX-002`; `contract/known-exceptions.json#L20` shows its current
`clears_when` already names exactly this as the alternative to a v0.6 that wasn't coming).

**Summary table:**

| Item | Finding | Fold into v0.6? | Why |
|---|---|---|---|
| 8.3 depends_on 8.2 | `IMP-0676` | **Yes** — the driver of this proposal | corrects the graph itself; nothing else clears it |
| DocuSign 20h (`KNOWN_GAP`) | `IMP-0064`/`IMP-0098` | **No** | reviewer already ruled it out of WBS scope on its own terms, independent of the no-v0.6 policy |
| Task 0.4 status wording | `IMP-0030`/`EX-001` | **Optional, cosmetic only** | does not clear the exception; the exception clears by building tables |
| `rev_grantadministration` unnamed | `IMP-0066`/`EX-002` | **Recommend yes** | a real content gap a workbook edit actually fixes |

---

## 3. What actually has to happen, procedurally

1. **This document** is the draft correction proposal — reviewer-facing, not yet client-facing.
   It stays in `docs/plans/` until the reviewer approves its content, because `docs/Import/` is
   reserved for the actual contractual source files (`contract/README.md#L30`,
   `contract/source-lock.json`) — a draft proposal is not one, and putting it there ahead of
   acceptance would put an unaccepted document inside the directory the source-lock hash treats
   as ground truth. **`docs/Import/` is where the new *workbook file* lands — the actual
   `Revitalise-WBS-Grant-Automation-v0.6.xlsx`, once the client has actually accepted it — not
   where this proposal lands while it is still a proposal.**

2. **The reviewer takes this proposal (or their edited version of it) to the client** and gets
   the client to actually revise and re-approve the WBS workbook — specifically, the client (or
   whoever holds the authoritative copy) edits task 8.3's `Depends On` cell from `8.1` to
   `8.1, 8.2`, and, if the reviewer chooses, the two optional items in §2. This step happens
   **outside this repository** — nothing here can fabricate that acceptance.

3. **Once the client-accepted `Revitalise-WBS-Grant-Automation-v0.6.xlsx` exists**, it is placed
   in `docs/Import/` alongside (not overwriting) v0.5 — the historical source is never deleted,
   consistent with `docs/Import/baseline-lock.yml`'s own practice of retaining superseded text
   rather than erasing it.

4. **pm-agent then runs BASELINE INTAKE** exactly as `agents/pm-agent.md`'s "On new source"
   procedure specifies: `scripts/import-baseline.py` (regenerate), `scripts/report-baseline-drift.py`
   (diff in hours and task count), present that diff plus every stale downstream figure, and
   **wait for `APPROVE BASELINE`** before committing the regenerated `contract/*.json` and
   appending the `logs/commercial-events.jsonl` line naming the version, hash and approver. This
   is the same gate every prior baseline change in this project has gone through — nothing about
   reversing "no v0.6" changes the gate itself.

5. **Retire the non-contractual workaround, after and only after step 4 lands.** Once
   `contract/wbs.json`'s own `depends_on` for 8.3 includes `8.2`, the
   `build_order_constraints.edges` entry in `contract/delivery-parameters.json`
   (`contract/delivery-parameters.json#L82`) becomes redundant — `wbs-ready-set.py` already
   unions both — and should be removed or marked historical so a future reader does not wonder
   why a contractual dependency is also recorded as a non-contractual one. **Do this only after
   the v0.6 edge is confirmed live in `contract/wbs.json`**, not in anticipation of it.

6. **Two things this document explicitly does NOT do**, per the dispatch's own instruction and
   `C-COM-009`/`C-COM-006`: it does not edit `contract/wbs.json` or `contract/source-lock.json`,
   and it does not write or imply a `CLIENT ACCEPTED` record anywhere. `WBS_IS_FINAL` in
   `scripts/import-baseline.py` stays `True` until the reviewer says otherwise and a real v0.6
   file exists to import.

---

## 4. Open questions for the reviewer

**Confirm the reversal itself before this goes further.** This draft assumes the "no v0.6"
decision has been reversed, because that is what the dispatch instructing this document stated.
Nothing in `contract/` or `docs/Import/baseline-lock.yml` currently reflects that reversal —
`scripts/import-baseline.py#L95` still reads `WBS_IS_FINAL = True`. If the reviewer has not yet
said this in their own words in a form this system can cite, that citation should exist before
the client conversation happens, for the same reason `docs/Import/baseline-lock.yml` exists at
all: so this decision doesn't have to be re-derived or misremembered next session.

**Decide the two optional bundle items (§2b, the 0.4 status wording and `rev_grantadministration`)
one way or the other**, so the proposal put to the client is final rather than growing across
multiple client conversations.

---

## References

- `contract/delivery-parameters.json#L82` — the non-contractual 8.3→8.2 edge this proposal would make contractual
- `contract/README.md#L34` — the "no v0.6" decision this proposal reverses
- `docs/Import/baseline-lock.yml#L237` — `a2_docusign_and_rework_hours`, why the DocuSign gap is not a v0.6 candidate
- `contract/known-exceptions.json` — `EX-001`, `EX-002`
- `scripts/import-baseline.py#L71` — `KNOWN_GAP`, `WBS_IS_FINAL`
- `agents/pm-agent.md` — BASELINE INTAKE procedure and `APPROVE BASELINE` gate
