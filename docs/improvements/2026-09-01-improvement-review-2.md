# Improvement Review — 2026-09-01 (2)

**Agent:** improvement-agent (tier `strategic`)
**Mode:** capability / reviewer-directed, per [`agents/improvement-agent.md#L62`](../../agents/improvement-agent.md#L62)
**Authorising artefact:** a direct reviewer decision, answering the cutoff half of open decision 1 in [`docs/improvements/2026-08-31-improvement-review-7.md#L488`](2026-08-31-improvement-review-7.md#L488) — *"Should `routing-reconciliation` ever go HARD, and from what cutoff?"*
**Findings processed:** 0 pre-existing. One finding (`IMP-0548`) is **logged by** this review, recording the capability established
**Gate:** `APPROVE IMPROVEMENTS`
**wbs:** system (non-billable, `C-COM-002`)
**Status:** **APPLIED 2026-09-01** — approved by the reviewer exactly as drafted. Three files changed; see §7.

**Numbered 2, not 1.** This review was drafted concurrently with two others. All three
independently computed `2026-09-01-improvement-review.md`; only one draft survived on disk, and
this one was re-persisted here. That is the same filename-collision shape review 8 recorded at
[`2026-08-31-improvement-review-8.md#L11`](2026-08-31-improvement-review-8.md#L11), now its second
instance — noted in §6 as a class, not patched here.

---

## 1. The decision, in one line

The `routing-reconciliation` cutoff moves from **2026-08-25** to **2026-08-31**, and the gate
**stays SOFT**. At the new cutoff the log still reports **17 unreconciled** dispatches, so removing
`--warn-only` would red every build.

---

## 2. Regression check — did the last change to this gate work?

| Question | Answer |
|---|---|
| Has any finding in the class appeared since? | **Yes.** `dispatched-agent-stalls-silently` recurred as recently as `IMP-0537` (2026-08-31). |
| Was the change prose, or a mechanical gate? | **A gate** — review 27 change 6 built [`scripts/verify-routing-reconciliation.py`](../../scripts/verify-routing-reconciliation.py). |
| Did the gate run, and did it fire? | **It ran and it fired.** It reports the stalled dispatches correctly. This is not a `gate-cannot-fail` finding. |
| So what is wrong with it? | **Its scope, not its logic.** Review 7 already diagnosed it as *"mis-scoped, not broken"* ([`2026-08-31-improvement-review-7.md#L83`](2026-08-31-improvement-review-7.md#L83)). This review re-scopes it. |
| Did the closure evidence match the level the defect was visible at? | Yes — every claim in this review is a V1 script execution, re-run at apply time (§5). |

---

## 3. The mechanism was extended, not invented

The dispatch asked for a cutoff mechanism. **One already exists**, and reinventing it would have
been the instance-patch error the altitude rule forbids:

- the constant at [`scripts/verify-routing-reconciliation.py#L77`](../../scripts/verify-routing-reconciliation.py#L77),
- the `--cutoff` argument at [`#L314`](../../scripts/verify-routing-reconciliation.py#L314),
- the comparison `if d.when < cutoff` at [`#L187`](../../scripts/verify-routing-reconciliation.py#L187),
- and the OUT-OF-SCOPE counter reported in the summary at [`#L353`](../../scripts/verify-routing-reconciliation.py#L353).

So the only code change is the value of one constant plus the prose that justifies it. No new
argument, no new branch, no new mechanism.

### The cutoff is INCLUSIVE, and that is forced rather than chosen

Routing-log timestamps are `[YYYY-MM-DD HH:MM]` (the regex at
[`#L66`](../../scripts/verify-routing-reconciliation.py#L66)). A date-only `--cutoff` parses to
midnight at [`#L333`](../../scripts/verify-routing-reconciliation.py#L333), and the comparison is a
**strict** `<`. So `--cutoff 2026-08-31` means *dispatches before 2026-08-31 00:00 are history, and
2026-08-31 itself is in scope*.

That is the reviewer's sentence — *"the reconciliation date can be yesterday… everything before
that is history"* — mapped onto the existing comparison with no code change to it. The alternative
reading (exclude 08-31 too) would have required either a different constant or a changed operator,
and §4 shows it would also have produced a meaningless green.

---

## 4. Measurement — why SOFT, stated plainly

Run against the live [`logs/routing.log`](../../logs/routing.log), without `--warn-only`:

| Cutoff | In scope | Closed | Unreconciled | Verdict |
|---|---|---|---|---|
| 2026-08-25 (previous default) | 113 | 76 | **33** | too wide — 91 pre-convention dispatches already excluded, and still a third of the corpus is open |
| **2026-08-31 (applied)** | 26 | 5 | **17** | correct scope; **too many open to go HARD** |
| 2026-09-01 | 4 | 0 | **0** | a green that proves nothing — see below |

**The 2026-09-01 row is the trap, and it is why the decision was made on the measurement rather
than on the framing.** It reads zero unreconciled over a scope of four dispatches, *all four
in-flight, none closed*. A gate flipped HARD on that basis would be passing over an empty corpus —
precisely the tell recorded at [`agents/improvement-agent.md#L481`](../../agents/improvement-agent.md#L481):
*where a gate reports 0 findings against a corpus you know contains an instance, that is the tell;
do not record it as a clean run.*

### The 17, named — not silently dropped

Per the no-silent-caps rule, these are the dispatches that remain unreconciled at the applied
cutoff. Each is a `ROUTED_TO` line in `logs/routing.log` with no later `GATE_RECEIVED` / `BLOCKED`
/ `STALLED` naming the same agent and feature:

| routing.log line | When | Agent | Feature |
|---|---|---|---|
| 411 | 2026-08-31 11:23 | build-agent | trustee-portal-visual-refresh |
| 417 | 2026-08-31 17:30 | improvement-agent | system |
| 426 | 2026-08-31 18:03 | development-agent | trustee-portal-visual-refresh |
| 440 | 2026-08-31 18:05 | build-agent | trustee-portal-visual-refresh |
| 442 | 2026-08-31 18:14 | improvement-agent | trustee-portal-visual-refresh |
| 443 | 2026-08-31 18:14 | development-agent | trustee-portal-visual-refresh |
| 445 | 2026-08-31 18:15 | build-agent | trustee-portal-visual-refresh |
| 431 | 2026-08-31 18:19 | architect-agent | system |
| 448 | 2026-08-31 18:58 | improvement-agent | trustee-portal-visual-refresh |
| 450 | 2026-08-31 19:00 | build-agent | trustee-portal-visual-refresh |
| 438 | 2026-08-31 19:04 | improvement-agent | system |
| 452 | 2026-08-31 19:04 | improvement-agent | trustee-portal-visual-refresh |
| 454 | 2026-08-31 19:09 | build-agent | trustee-portal-visual-refresh |
| 456 | 2026-08-31 19:20 | test-agent | trustee-portal-visual-refresh |
| 459 | 2026-08-31 19:32 | pipeline-agent | trustee-portal-visual-refresh |
| 464 | 2026-08-31 22:19 | improvement-agent | system |
| 465 | 2026-08-31 22:19 | improvement-agent | system |

These are real log-hygiene debt, not false positives: they cluster in one evening's session series
where lead-agent dispatched and never wrote the closing line. **Reconcile these seventeen, then
`--warn-only` comes off in a one-line follow-up.** That follow-up is the remaining half of review 7's
open decision 1 and is explicitly not taken here.

---

## 5. What was re-verified at apply time

Per [`agents/improvement-agent.md#L143`](../../agents/improvement-agent.md#L143), the draft was
re-measured against the tree before anything was written, because the interval between the gate
opening and the keyword arriving is time in which other dispatches land ground truth (`IMP-0405`):

| Claim | Re-verified how | Result |
|---|---|---|
| 17 unreconciled at cutoff 2026-08-31 | re-ran the gate, not re-read it | **unchanged, 17** |
| `DEFAULT_CUTOFF` is still `2026-08-25` | read L77 | unchanged |
| The build step still carries `--warn-only` | read [`config/revitalise-grant-automation-build.yml#L247`](../../config/revitalise-grant-automation-build.yml#L247) | unchanged |
| WORKFLOW.md L182-186 still carries the old counts | read the lines | unchanged |
| No `corrects` entry contradicts this change | `verify-improvement-log.py --check` | none |
| The improvement-log id is still free | `allocate-improvement-id.py`, re-read immediately before appending | **it was NOT** — see below |

**Two ids were burned to concurrent allocation.** The draft named `IMP-0543`; by apply time another
concurrent dispatch had claimed it along with 0544–0546, so the id became `IMP-0547`. Re-reading the
maximum id again immediately before the append — the rule at
[`agents/improvement-agent.md#L303`](../../agents/improvement-agent.md#L303) (`IMP-0312`, originally
`IMP-0080`) — showed 0547 had *also* gone in the interim. This review's finding is therefore
**`IMP-0548`**. Nothing was corrupted; the rule fired twice and did its job both times.

---

## 6. Retirement, constraints, and what was deliberately not done

**New constraints: 0** (cap is 3). A default value is not a rule. The convention it encodes —
*every `ROUTED_TO` is closed by a terminal line* — already exists and is already enforced by the
gate; only its start date moved. A constraint row here would be a comment, which
[`agents/improvement-agent.md#L393`](../../agents/improvement-agent.md#L393) forbids.

**Retirement candidate: none, and this was checked.** The obvious candidate — the *"the mechanical
half is deliberately not proposed here"* paragraph — **was already retired on 2026-08-31** by
review 7 (`IMP-0537`). This review updates its replacement rather than retiring anything.

**Not done, and reported rather than dropped:**

1. **`config/revitalise-grant-automation-build.yml` is untouched.** `--warn-only` stays (§4). Its
   explanatory comment at [`#L232`](../../config/revitalise-grant-automation-build.yml#L232)
   justifies the SOFT setting by citing *"the 2026-08-25 09:23 architect-agent dispatch"* — which
   this change puts **out of scope**, making that justification stale. It is left for whoever owns
   that file next rather than risking a collision with the concurrent WS-C/WS-K dispatch editing
   the same file. Flagged, not silently accepted.
2. **The HARD flip itself**, pending reconciliation of the 17 (§4).
3. **The review-filename collision**, now at two instances. Not patched here: a third instance is
   what would justify a mechanical fix, and this review has no mandate to widen its own scope.

---

## 7. Applied record

| # | Change | File | Justification |
|---|---|---|---|
| 1 | `DEFAULT_CUTOFF` `2026-08-25` → `2026-08-31`, and the docstring paragraph rewritten to record the convention decision, its date and its attribution | [`scripts/verify-routing-reconciliation.py`](../../scripts/verify-routing-reconciliation.py) | reviewer decision; review 7 §6 decision 1 |
| 2 | The stale reading **31 unreconciled / 2 in flight / 76 closed of 109** refreshed to the measured **17 / 4 / 5 of 26**, and the cutoff convention recorded as 2026-08-31, dated and attributed | [`agents/WORKFLOW.md#L182`](../../agents/WORKFLOW.md#L182) | a superseded figure that keeps instructing the next reader is the costly kind of stale reference |
| 3 | `IMP-0548` appended and closed `APPLIED`; digest regenerated | [`logs/improvement-log.jsonl`](../../logs/improvement-log.jsonl) | learning rule — a capability was established |

**Verification level: V1** per `C-TECH-053` — the gate was executed against the real corpus at both
cutoffs, and `--selftest` re-run after the edit. The selftest passes an explicit cutoff, so it is
unaffected by the constant and does not evidence it; the corpus runs in §4 are what evidence it.

---

## 8. Deviations from the approved wording

**None.** The change applied is the change presented: cutoff 2026-08-31, gate stays SOFT, no HARD
flip, three files. The only substitution is the finding id (`IMP-0543` → `IMP-0547` → `IMP-0548`), forced twice by
concurrent allocation and recorded in §5.
