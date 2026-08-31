# Improvement Review 5 — 2026-08-28

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 1 `unread` → 1 clusters
**Trigger:** blocker escalation — one unread `blocker`, [IMP-0423](../../logs/improvement-log.jsonl)
**Gate:** `APPROVE IMPROVEMENTS` — ~~nothing in this document is on disk yet~~ **APPROVED 2026-08-28 by Xander Lykopoulos and APPLIED in full; section 8 carries the record.**

---

## Summary

**The crash that made [IMP-0423](../../logs/improvement-log.jsonl) a blocker is already fixed, verified on disk this dispatch, and the entry can close — but the fix shipped with no test behind it, and the entry's own prescription for the rest is wrong.** The authoritative log validator runs to completion over every entry and prints its full state breakdown; the `isinstance` guard that fixes it sits at [scripts/verify-improvement-log.py#L1049](../../scripts/verify-improvement-log.py#L1049), applied by review 33 as [IMP-0424](../../logs/improvement-log.jsonl). What is missing is the fixture: all 60 selftest fixtures build `proposed_change` as an object, so deleting that guard leaves the suite green — the same "a mitigation that cannot fail" shape the finding itself is filed under.

This review closes the blocker, adds the two mechanical changes that make the guard defensible, and **withholds** the one change [IMP-0423](../../logs/improvement-log.jsonl) asked for whose premise measures false.

---

## 1. Regression check — did the last review's changes work?

**Scoped deliberately to the one prior change that targets this cluster's class.** A single unread blocker summons a review of itself, not of the twenty-three settled entries around it (`agents/improvement-agent.md` activation step 2, after `IMP-0183`).

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| The `isinstance` type guard at [verify-improvement-log.py#L1049](../../scripts/verify-improvement-log.py#L1049), review 33 ([IMP-0424](../../logs/improvement-log.jsonl)) | 2026-08-28 | `gate-cannot-fail` | NO — no new instance of the crash | **Working, and under-tested.** The symptom is gone and re-observed; the change has no fixture, so it can be removed without any suite noticing |

The four audit questions, answered:

- **Has any finding in that class appeared since?** No new instance of the crash. [IMP-0423](../../logs/improvement-log.jsonl) is the *same* instance seen from a concurrent session, not a recurrence — both entries describe one AttributeError at one line over the same two entries.
- **Was the change prose or a mechanical gate?** Mechanical, in the gate itself. No escalation needed.
- **Did the gate run?** Yes. Measured this dispatch: `python3 scripts/verify-improvement-log.py --check` reaches a verdict over every entry in the log with no traceback (424 when this review opened, 427 now), and `--selftest` reports 60 fixtures green.
- **Did the closure evidence match the level the defect was visible at?** Yes, and better than the entry claims. `observable_at` is V1; the fix was re-observed by re-running the original command, **and** the pre-fix crash was reproduced on a copy of the script with the guard reverted, which is what proved the fixture below is load-bearing.

---

## 2. Clusters and promotion decisions

```
CLUSTER: gate-cannot-fail  (x1: IMP-0423)
Altitude:   INSTANCE — one defect, already fixed by IMP-0424; what is missing is the coverage
            that keeps the fix in place. The class is at x36 and has a general gate already
            (verify-build-config.py + the negative-test suite); this rung is a fixture inside
            an existing verifier, not a new rule.
Ladder row: "a tool could catch it mechanically" — the tool exists, the fixture does not.
Becomes:    scripts/verify-improvement-log.py — (1) the string-form fixture
            APPLIED-with-a-string-proposed_change-is-reported-not-raised, the twin of
            APPLIED-after-the-cutoff-without-a-needle-fails; (2) the selftest reports a fixture
            that RAISES by name instead of aborting the suite with a traceback naming none.
Retires:    nothing — see section 4.
Cites:      IMP-0423, IMP-0424
Residual:   Two, both stated rather than papered over. (a) The fixture pins ONE consumer of
            proposed_change; a future consumer that reads the field unguarded will crash the
            same way, and nothing enumerates consumers. (b) A check that RAISES rather than
            returning is still not a reported finding anywhere except the selftest — the
            general form of that (every gate in scripts/) is IMP-0424's open half and is NOT
            in this review, because it touches 48 scripts and no measurement supports it yet.
```

### The withheld half, and why

**[IMP-0423](../../logs/improvement-log.jsonl) asked for a schema assertion that `proposed_change` must be an object. It is WITHHELD: the premise measures false in both halves.**

The schema already type-checks the field — [verify-improvement-log.py#L805](../../scripts/verify-improvement-log.py#L805) requires `type` on an object and reports, by id, anything that is neither an object, a string, nor absent. And the bare-string form is legal **by design**: 2 of 424 entries carry one, and they are named — [IMP-0390](../../logs/improvement-log.jsonl) and [IMP-0391](../../logs/improvement-log.jsonl), both legitimate, both closed by review 33. So the proposed rule would report two correct entries as errors, and the only way to green it would be to rewrite them.

This matters beyond the entry, because the wrong instruction is already in the read path: the lesson renders in full at [logs/known-failure-modes.md#L113](../../logs/known-failure-modes.md#L113) under *Before you execute a build config*, telling the next agent to require a dict. Change 4 appends the correction so the digest marks it.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | script | `scripts/verify-improvement-log.py` | Add fixture `APPLIED-with-a-string-proposed_change-is-reported-not-raised` at [#L1627](../../scripts/verify-improvement-log.py#L1627): an `APPLIED` entry whose `proposed_change` is a bare string must be REPORTED (exit 1, "with no 'evidence_grep'"), never raised | IMP-0423, IMP-0424 | YES — `python3 scripts/verify-improvement-log.py --selftest`: 61 fixtures green with the guard; revert the guard and this fixture raises |
| 2 | script | `scripts/verify-improvement-log.py` | Wrap the fixture runner at [#L1985](../../scripts/verify-improvement-log.py#L1985) so a fixture that raises prints `RAISED <name>` and fails the suite, instead of ending the run with a traceback that names no fixture | IMP-0423 | YES — with the guard reverted: exit 1, the fixture named, 0 tracebacks |
| 3 | other | `logs/improvement-log.jsonl` | Close [IMP-0423](../../logs/improvement-log.jsonl) `APPLIED` — `applied_by` naming IMP-0424's guard as the actual crash fix plus changes 1–2, `reobserved` recording the re-run, `evidence_grep` on change 1's fixture name, and the withheld half stated in the entry | IMP-0423 | YES — `python3 scripts/verify-improvement-log.py --check` exits 0 |
| 4 | other | `logs/improvement-log.jsonl` | Append one finding carrying `corrects: IMP-0423`, recording that the schema half's premise is false and that the crash exits **1**, not 0 (the 0 came from measuring through a pipe) | IMP-0423, IMP-0424 | YES — the digest renders a `CORRECTED by` marker under IMP-0423's lesson |

**Constraint budget:** 0 of 3 used.

**One correction marker, not two, and this is a judgement rather than an oversight.** `corrects` is single-valued at [verify-improvement-log.py#L1474](../../scripts/verify-improvement-log.py#L1474), and the entry it names is the one whose lesson renders in full and misdirects. [IMP-0424](../../logs/improvement-log.jsonl)'s wrong clause is its exit-code arithmetic; its actionable half — guard with `isinstance`, the string form is legal — is correct, and a CORRECTED marker on it would tell readers to distrust a lesson that is right. The correction text names it instead.

---

## 4. Retirements

> Retirement check performed: 80 live constraint rows reviewed (10 already retired, both figures derived with the commands in `skills/how-to-promote-a-finding.md` §3), none currently redundant.

The reason is structural: this review adds no rule. It adds fixture coverage inside the verifier that [C-TECH-061](../../constraints/technology/technology-constraints.md#L131) already names as its enforcement, and that row is the only mechanical statement of this log's shape — retiring it would remove the check this review is strengthening.

---

## 5. Findings left unprocessed

No silent caps. Eight `unread` entries were in the queue and **none of them is opened by this dispatch**: a blocker is processed on its own, at once, and one unread blocker must not pull a review of everything around it (`IMP-0183`). None is a `blocker`, so none is a live trigger.

**After application the queue stands at 9 `unread` against a batch trigger of 10** — the eight below plus `IMP-0432`, which this review's own application produced (section 6). **One more arrival summons a full review before the next build.**

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0420 | `declared-policy-not-mechanically-enforced` | not a blocker; unrelated to this cluster | the next scheduled review, or at 10 unread |
| IMP-0421 | `learning-substrate-destroyed` | as above | as above |
| IMP-0422 | `gate-reassures-wrongly` | as above | as above |
| IMP-0425 | `gate-scope-mismatch` | as above | as above |
| IMP-0426 | `finding-diagnosis-unverified` | as above — and it shares a class with change 4's entry, so the two are worth clustering together next time | the next review, clustered with change 4's entry |
| IMP-0428 | `gate-fires-on-nothing` | arrived from a concurrent architect dispatch while this review was drafting | as above |
| IMP-0429 | `wrong-artefact-cited-as-evidence` | as above; `rework`, and its own proposal notes it is the third instance of its class, so it is due generalisation in a review that can cluster it | the next review — it asks for a skill change, which needs the cluster |
| IMP-0430 | `gate-scope-mismatch` | as above; clusters with IMP-0425 | the next review, clustered with IMP-0425 |

**The log moved under this review, and that is why change 4 names no id.** It stood at 424 entries when this dispatch opened and at 427 twenty minutes later; the id this review had drafted for its correction, `IMP-0428`, was taken at 14:05 by a concurrent architect dispatch. The id is therefore allocated with `python3 scripts/allocate-improvement-id.py` at the moment of appending, re-read against the then-current maximum (`IMP-0080`, `IMP-0312`), and the figures below were re-measured against the 427-entry log rather than the snapshot this review started from. None of the three arrivals carries `corrects` against anything here, and none touches this cluster.

The 72 `reviewer-deferred` entries are untouched by design, and the 109 pre-cutoff `APPLIED` entries with no needle stay un-backfilled (`IMP-0181`).

Two SOFT `verify-derived-counts.py` drifts are live and are **not** this review's: both are secured-column figures in `docs/development/revitalise-grant-automation-dev-summary.md` and `src/solutions/RevitaliseGrantAutomation/Roles/REV Trustee/REV Trustee.xml` (prose 67/51 against source 68/52). Delivery-owned; reported, not fixed. The one figure this agent owns, `improvement-agent-verify-script-count`, is current at 48 and this review adds no script.

---

## 6. Digest impact

Measured against a drafted copy of the log in a scratch tree, not predicted (`IMP-0198`).

| | Before | After (drafted) | After (**actual**) |
|---|---|---|---|
| Log entries | 427 | 428 | **429** |
| Distinct lessons | 426 | 427 | **428** |
| Recurring classes (x≥2) | 37 | 37 | 37 |
| Digest lines | 571 | 572 | 572 |

**The actual is one entry above the drafted figure, and the extra entry is named.** Applying change 3 was refused by `check_reobservation()` — correctly — because a truthful re-observation stamp read *earlier* than the finding it re-tested: IMP-0423 is stamped 17:58, the concurrent architect entries 14:05–14:09, and this machine's `date` returned 13:36. That is a second defect, not a detail of this one, so it was captured as `IMP-0432` (`gate-scope-mismatch`, `friction`, left `NEW` with a `revisit_when`) rather than absorbed into the closure. The re-observation is stamped on the entry's own clock with the skew stated in `reobserved.result`; no other session's `ts` was rewritten.

The visible change in the read path is the `⚠ CORRECTED by` marker rendered under [IMP-0423](../../logs/improvement-log.jsonl)'s lesson at [logs/known-failure-modes.md#L113](../../logs/known-failure-modes.md#L113), which is the point of change 4.

**What was executed, and what was not.** All four changes were assembled in a scratch overlay — the edited script and the edited log, every other path symlinked to this repository — and run there against the current 427-entry log: `verify-improvement-log.py --check` exits **0** over 428 entries, with the blocker trigger cleared and 8 `unread` entries left; `--selftest` reports **61 fixtures** green; with the `isinstance` guard reverted the new fixture reports `RAISED … AttributeError` by name and the suite exits 1 with **0** tracebacks; the digest regenerates to 572 lines carrying the correction marker. Nothing has been written to `scripts/`, `logs/` or the digest in this repository — the level reached is V1 for the changes and a measured simulation for the end state, and the tracked tree still fails `--check` on this one blocker until the keyword lands.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-28-improvement-review-5.md

Findings processed: 1 NEW  →  1 clusters
Regression check:   1 prior changes audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 2 gates/scripts, 0 skill/knowledge edits,
                    0 agent-file edits, 0 retirements
Altitude calls:     0 generalised from instance to class, 1 left as notes
Digest:             will regenerate — 427 lessons, 37 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

Approved 2026-08-28 by Xander Lykopoulos and applied in full, in the order below. Each entry was closed as its change landed, not batched at the end (`IMP-0301`); the digest was regenerated once, last.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | Fixture `APPLIED-with-a-string-proposed_change-is-reported-not-raised` in `scripts/verify-improvement-log.py` | working tree, uncommitted | — |
| 2 | The selftest runner names a fixture that raises (`RAISED <name>`) instead of aborting with an anonymous traceback | working tree, uncommitted | — |
| 3 | `IMP-0423` closed with `reviewed_in`, `applied_by`, `reobserved` and `evidence_grep`; the schema half **withheld** and stated in the entry | working tree, uncommitted | IMP-0423 |
| 4 | `IMP-0431` appended, `corrects: IMP-0423` — the withheld half and the corrected exit-code claim | working tree, uncommitted | IMP-0431 |
| — | `IMP-0432` appended `NEW` — the cross-session clock skew that refused change 3 on the first attempt (see section 6) | working tree, uncommitted | — |
| — | `logs/known-failure-modes.md` regenerated — 429 entries, 428 lessons, 572 lines, correction marker at line 115 | working tree, uncommitted | — |

**Deviation from the approved draft, stated so it cannot be silent:** one entry more than the draft named (`IMP-0432`), for the reason in section 6. Nothing else differs — the two script changes, the closure and the correction are exactly as approved, and no change was substituted or reworded.

**Verification after application:** `python3 scripts/verify-improvement-log.py --check` exits **0** — 429 entries, 81 NEW (9 `unread`, none a blocker), 347 APPLIED, 1 REJECTED, 3 pre-existing `corrects` warnings that belong to other entries. `--selftest` reports **61 fixtures** green, and the new fixture is load-bearing: on a copy with the `isinstance` guard reverted it reports `RAISED … AttributeError` by name, the suite exits 1, and 0 tracebacks are printed. `python3 scripts/generate-known-failure-modes.py --check` reports the digest current. Not verified: nothing was committed, and no build has been run against the changed gate.

Entries rejected, with reasons:

| Finding | Rejected because |
|---|---|
| — | none — IMP-0423 closed `APPLIED`; one half of its `proposed_change` is withheld, and that is recorded in the entry, in section 2 and in IMP-0431 rather than as a rejection |
