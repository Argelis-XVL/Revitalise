# Improvement Review — 2026-09-01 (10)

**Status:** **APPLIED 2026-09-01** — `APPROVE IMPROVEMENTS` received; all five changes are on disk and the blocker is closed. See §8. ~~AWAITING `APPROVE IMPROVEMENTS`. Nothing in this review has been applied.~~
**Trigger:** unread `blocker` — [`IMP-0573`](../../logs/improvement-log.jsonl#L570), processed alone, not batched
**Findings processed:** 1 unread → 1 cluster
**wbs:** 6.9 (the halted build). The defect is system-level and maps to no accepted WBS task; nothing here is delivery work, so no change-order question arises (`C-COM-002`).

---

## 0. Conclusion first

**The class has crossed the threshold, and the gate this project has been waiting for would not have caught this instance.** Seven instances of `untriaged-tool-warning` have all been closed the same way — by adding a prose row to a Dev Summary's triage table — and [`C-TECH-055`](../../constraints/technology/technology-constraints.md#L110) records the mechanical gate as deliberately deferred behind [`IMP-0500`](../../logs/improvement-log.jsonl#L497) until three build manifests carry a conforming `warnings_detail[]`. That deferral's trigger **is now satisfied — 5 conforming manifests, measured, against a threshold of 3** — but the gate it unlocks diffs warning *signatures*, and [`IMP-0573`](../../logs/improvement-log.jsonl#L570)'s signature never changed. A signature diff would have matched the existing triage row and passed.

So the promotion is a **value** assertion, not a signature one: a committed byte budget for the built bundle, compared against the bytes on disk. Measured against the real bundle it exits 1 on the figure the triage table implied (558 kB) and 0 on the figure vite actually printed (1,204,716 bytes) — the correct polarity, on real values, not fixtures.

**No new constraints.** `C-TECH-055` is amended, not supplemented.

---

## 1. Regression check — did the last review's changes work?

Review 9 wired [`verify-models-yml-comments.py`](../../scripts/verify-models-yml-comments.py) into the build config and added the *"a gate you write is not finished until a build config invokes it"* paragraph to [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L381).

| Question | Answer |
|---|---|
| Has any finding in that class appeared since? | **No.** `python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml` — **exit 0**, 71 steps, `suite-gate-is-not-a-step` clean. `models-yml-comments` present, 2 occurrences. Both changes hold. |
| Prose or mechanical gate? | Mechanical (a wired step) plus one prose line. The mechanical half is self-checking: an unwired gate is a red preflight. |
| Did the gate run? | Yes — it is in the preflight's own step enumeration, and the preflight passes. |
| Did closure evidence match `observable_at`? | Yes. `IMP-0568`/`IMP-0569` were V1/V2 (preflight exit code) and were closed on a re-run preflight, which is the level they were visible at. |

**Executed, not read**, per step 8's behavioural-assertion clause. [`IMP-0570`](../../logs/improvement-log.jsonl#L567), [`IMP-0571`](../../logs/improvement-log.jsonl#L568) and [`IMP-0572`](../../logs/improvement-log.jsonl#L569) carry `appended_by` naming review 9 — they are findings that review *logged*, not recurrences of the class it fixed.

---

## 2. Clusters and promotion decisions

```
CLUSTER: untriaged-tool-warning  (x7: IMP-0177, IMP-0214, IMP-0323, IMP-0393, IMP-0411,
                                     IMP-0499, IMP-0573)
Altitude:  CLASS, and specifically a SUB-PROPERTY the pending class gate does not cover.
           Instances 1-6 are all "a warning present in the build has no row in the current
           feature's Dev Summary" — an ABSENCE of a row. Instance 7 is the first where the
           row was PRESENT and its cited MAGNITUDE was false. Those are different defects
           behind one warning string.
Ladder row: "a tool could catch it mechanically" -> a script plus a build gate.
           Also "second instance -> generalise": six prose patches to six documents is
           exactly the instance-patching the altitude rule forbids, and this is the seventh.
Becomes:   scripts/verify-code-app-bundle-budget.py (HARD, wired after code-app-build)
           + src/code-apps/trustee-review-portal/bundle-budget.json (the declared values)
           + C-TECH-055's Verify By amended to record which half is now mechanical
           + agents/build-agent.md: signature-stable != magnitude-stable
Retires:   nothing. No instance gate ever existed for this class; all seven prior remedies
           were document edits, which are not gates and cannot be retired.
Cites:     IMP-0573 (the blocker), IMP-0499 (instance 6, the C-TECH-055 amendment),
           IMP-0500 (the deferred signature-diff gate this does NOT replace)
Residual:  THREE, all named rather than smoothed over.
           (1) The budget carries ~3% headroom over the measured figure, deliberately. A
               budget pinned to the exact byte would fail on routine churn (a changed hash,
               a one-line edit); 3% blocks a recharts-scale addition (+117%) and tolerates
               noise. The cost is that a real growth under 3% passes silently.
           (2) It covers the ONE Code App in this repository. A second Code App with no
               bundle-budget.json is not caught by this gate's absence — it is caught only
               when someone wires the step for it. The gate fails loudly on a missing budget
               file for a path it IS given, which is the half that can be mechanised.
           (3) gzip figures are ADVISORY only. Python's gzip -9 and rollup's reporter
               disagree by ~0.06% on this bundle (471,087 bytes vs vite's printed 471.37 kB),
               so a HARD assertion on a gzip number would assert on an implementation
               detail. Raw bytes are exact and reproducible; only they block.
```

### Why the pending `warnings_detail[]` gate is not the answer here

[`IMP-0500`](../../logs/improvement-log.jsonl#L497)'s `revisit_when` asks for three manifests carrying a conforming `warnings_detail[]`. Measured against every manifest on disk, against the declared shape `{step, signature, status, triaged_in}`:

| Result | Count | Manifests |
|---|---|---|
| **Conforming** | **5** | `revitalise-grant-automation-20260831-1`, `trustee-portal-visual-refresh-20260830-2`, `-20260831-5`, `-20260831-6`, `-20260831-8` |
| Diverging key sets | 4 | three at `{note, recorded_at, source, status, warning}`, one at `{count, note, status, step}` |
| Present but empty `[]` | 3 | `trustee-portal-visual-refresh-20260831-1`, `-4`, `-7` |

**The trigger is satisfied.** It is nonetheless not discharged here, and that is deliberate: `IMP-0500` is `reviewer-deferred`, step 2 says leave such entries alone, and the approved `revisit_when` is applied verbatim rather than rewritten. It is carried as routed work in §5 instead — because the gate it unlocks compares `step` + `signature` against the triage table, and `IMP-0573`'s signature was byte-identical across both revisions. **A signature diff would have reported this warning as triaged and passed the build.**

One measured caveat for whoever builds it: `build/artifacts/**` is gitignored at [`.gitignore:10`](../../.gitignore#L10) and yet 34 manifests are tracked in the index. A gate reading manifests therefore reads files whose presence depends on local state, which is the [`IMP-0410`](../../logs/improvement-log.jsonl#L407) shape. Recorded as an appended finding in §5, not fixed here.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | `scripts/verify-code-app-bundle-budget.py` | New HARD gate: measures `dist/assets/*` byte sizes against a declared budget; fails on budget exceeded, on a budget entry matching no file, and on a missing/malformed budget file | IMP-0573, IMP-0499 | YES — `python3 scripts/verify-code-app-bundle-budget.py src/code-apps/trustee-review-portal` | **`HARD`**, new step `code-app-bundle-budget` between [`code-app-build`](../../config/revitalise-grant-automation-build.yml#L631) and [`package-code-app`](../../config/revitalise-grant-automation-build.yml#L637) |
| 2 | other | `src/code-apps/trustee-review-portal/bundle-budget.json` | New tracked data file: the declared budget, one entry per asset family, each carrying `reason` and `triaged_in` | IMP-0573 | YES — read by change 1 | N/A |
| 3 | constraint-amendment | [`constraints/technology/technology-constraints.md` L110](../../constraints/technology/technology-constraints.md#L110) | `C-TECH-055`'s *"Not yet mechanical, and deliberately so"* clause is corrected: the **magnitude** half is now mechanical via change 1; the **signature** half remains deferred, with its trigger recorded as satisfied | IMP-0573, IMP-0499, IMP-0500 | YES — the clause names a runnable command | N/A |
| 4 | agent | [`agents/build-agent.md` L150](../../agents/build-agent.md#L150) | *Warnings Are Findings* step 2 gains: a repeating warning signature is matched on its **figures**, not its wording; an unchanged warning text is not evidence that nothing changed | IMP-0573 | N/A — instruction change | N/A |
| 5 | agent | [`agents/improvement-agent.md` L370](../../agents/improvement-agent.md#L370) | The derived `verify-*.py` count moves 55 → 56 in the same change that adds the gate, as that section itself requires | IMP-0573, IMP-0395 | YES — `python3 scripts/verify-derived-counts.py` | N/A |

**Constraint budget:** 0 of 3 used. Change 3 is an amendment to an existing row, not a new one — the rule `C-TECH-055` states is already correct; only its claim about its own enforceability is out of date.

### Change 1, measured before it is wired

`--selftest` — **8/8 checks pass**, and it proves the gate *can* fail in each direction: one byte over budget fails, exactly at budget passes, a loose budget is SOFT not HARD, a glob matching no file fails, an entry missing `reason` fails, an absent budget file fails, and a gzip overage is SOFT only.

**A green selftest is not evidence a gate is correct**, so it was also run against the real corpus — the actual built bundle the halted build produced:

| Budget declared | Actual measured | Gate verdict | Correct? |
|---|---|---|---|
| 558,000 bytes — the figure the triage table implied before the correction | `index-CHj1JD9T.js` at 1,204,716 bytes (1204.72 kB) | **exit 1**, names the 646,716-byte overage | **TRUE POSITIVE** — this is `IMP-0573` itself |
| 1,204,716 bytes — the figure vite actually printed | same | **exit 0** | **TRUE NEGATIVE** |
| 1,210,000 JS + 78,000 CSS — both families at measured truth + headroom | 1,204,716 JS, 77,221 CSS | **exit 0** | **TRUE NEGATIVE** |

**2 findings across 3 runs over the real corpus, 1 true positive, 0 false positives.** The corpus is one Code App and its one built bundle — that is the whole population, and it is small; §2's Residual (2) says so plainly rather than dressing three runs up as a survey.

**The polarity is the point.** Per `agents/improvement-agent.md`'s prose-gate rule, a candidate that scores the *corrected* artefact worse than the defective one has inverted polarity and a wrong design. This gate reads no prose at all — it compares an integer to an integer — which is why it is immune to the 48–100%-false shape this project has measured five times. The corrected Dev Summary row now cites **1,204.72 kB**, and the bundle measures **1,204,716 bytes = 1204.72 kB decimal**: the document and the bytes agree exactly, and the gate passes on that agreement.

### One correction to the finding's own `proposed_change`

[`IMP-0573`](../../logs/improvement-log.jsonl#L570) proposes an `agents/build-agent.md` edit and nothing else. That edit is worth making and is change 4 — but **as the whole remedy it would be the seventh prose patch to a class that has taken six.** The finding's own `why_it_was_never_caught` says it: *"no gate compares vite's own printed chunk-size figures against the specific kB numbers cited in the Dev Summary."* Prose is kept as the part that generalises to warnings carrying no number; the number gets a gate.

---

## 4. Retirements

> Retirement check performed: 82 live constraint rows reviewed (10 already retired, both figures derived with `grep -rh '^| C-' constraints/ --include='*.md' | wc -l` and `'^| ~~C-'`), none currently redundant.

`C-TECH-055` is the row this review touches and it is **not** a retirement candidate: it becomes *more* enforceable, not less. The honest candidate was its *"Not yet mechanical, and deliberately so"* clause, which is amended by change 3 rather than retired, because half of it is still true — the signature diff remains unbuilt.

No instance gates exist to retire. All seven prior remedies for this class were edits to Dev Summary documents, and a document row is not a gate.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0549, IMP-0550, IMP-0551, IMP-0552, IMP-0562, IMP-0563, IMP-0566, IMP-0567, IMP-0570, IMP-0571, IMP-0572

These 11 are `unread` and **out of scope by rule, not by choice.** `agents/improvement-agent.md`'s activation step 2 is explicit that an unread blocker must not pull a review of everything around it (`IMP-0183`), and the dispatch routed this one immediately under the blocker trigger. Each is stamped `excluded_by` naming this document, per `IMP-0557`, so that obeying the rule does not trip a citation-stamp warning per id.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0549 | `hand-maintained-count-drifts-from-source` | not the routed blocker | next batch review or the ≥30-entry trigger |
| IMP-0550, IMP-0551, IMP-0562, IMP-0570, IMP-0571 | `finding-diagnosis-unverified` | not the routed blocker; a 5-strong cluster deserving its own pass, not a footnote to this one | next batch review |
| IMP-0552 | `wrong-artefact-cited-as-evidence` | not the routed blocker | next batch review |
| IMP-0563, IMP-0566 | `no-assertion-on-shipped-content` | not the routed blocker | next batch review |
| IMP-0567, IMP-0572 | `declared-policy-not-mechanically-enforced` | not the routed blocker | next batch review |

**One of these needs naming rather than listing.** [`IMP-0563`](../../logs/improvement-log.jsonl#L560) is `unread` yet is cited by [review 8](2026-09-01-improvement-review-8.md) and carries no `reviewed_in` — the gate reports it as a WARNING. That is review 8's step-6 stamp missing, not something this review can fix without processing the entry; flagged so it is not lost.

### Routed work — re-measure before dispatching

| Item | Owner | State measured 2026-09-01 |
|---|---|---|
| The `warnings_detail[]` **signature-diff** gate behind `IMP-0500` | improvement-agent, a future review | **Trigger satisfied** (5 conforming manifests ≥ 3). Not dispatched here: it is a different property from this blocker, and `IMP-0500` is `reviewer-deferred`. Whoever takes it must first settle the `.gitignore`-vs-tracked contradiction below, because the gate's input is a gitignored directory. |
| The Dev Summary content fix (the stale triage row) | development-agent, separate dispatch | **Already on disk.** [L2493](../../docs/development/trustee-portal-visual-refresh-dev-summary.md#L2493) now cites 1,204.72 kB / 471.37 kB gzip, names `recharts@3.10.1` and commit `2d34e9a`, and withdraws the *"not worsened"* / *"zero new warnings"* claims. Verified, not assumed — this review does not touch that document. |

### To be appended on approval

One finding, stamped `appended_by` and **not** `reviewed_in` (`IMP-0456`), so it does not read as processed: `build/artifacts/**` is gitignored at `.gitignore:10` while 34 manifests are tracked in the index, so any future gate reading manifests has an input whose presence depends on local filesystem state (`IMP-0410`'s class). Class `declared-policy-not-mechanically-enforced`, severity `friction`. Id from `python3 scripts/allocate-improvement-id.py`, read immediately before appending.

---

## 6. Digest impact

| | Before (measured) | After (predicted) |
|---|---|---|
| Log entries | 570 | 571 |
| Distinct lessons | 567 | 568 |
| Recurring classes (x≥2) | 44 | 44 |
| Digest lines | 621 | 621–624 |

**These After figures are predictions and are labelled as such.** `IMP-0198` is the review that predicted a digest delta of 31→26 and measured 31→30; the actual figures go in §8 from a real `--check` run, not from this table. `untriaged-tool-warning` is already listed at x7 and `declared-policy-not-mechanically-enforced` at x25, so no new class row is expected — only a count increment.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-01-improvement-review-10.md

Findings processed: 1 NEW  →  1 cluster
Regression check:   2 prior changes audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 1 constraint amendment, 1 gates/scripts,
                    2 agent-file edits, 1 other (the budget file), 0 retirements
Altitude calls:     1 generalised from instance to class, 0 left as notes
Digest:             will regenerate — 568 lessons predicted, 44 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied record — 2026-09-01

**All five changes landed. Nothing was withheld and nothing was narrowed.** Re-verification ran before anything was written, and every premise of the draft held.

| Re-verified at apply time | Result |
|---|---|
| Any `corrects` naming `IMP-0573`, or a later same-class entry? | **None.** It was the log's maximum id; nothing contradicted the draft. |
| Bundle bytes unchanged since the draft? | **Yes** — 1,204,716 JS / 77,221 CSS, byte-identical. |
| Routed row 1: `IMP-0500`'s trigger | **Still satisfied**, re-counted at 5 conforming manifests. Withheld from dispatch as drafted, not actioned. |
| Routed row 2: the Dev Summary content fix | **Still on disk**, re-checked at [L2493](../../docs/development/trustee-portal-visual-refresh-dev-summary.md#L2493). Not touched by this review. |
| `verify-build-config.py` (before) | exit 0 — review 9's changes still holding |

### What was applied

**Change 1** — [`scripts/verify-code-app-bundle-budget.py`](../../scripts/verify-code-app-bundle-budget.py#L1), `--selftest` 8/8. Wired as the `code-app-bundle-budget` step at [`config/revitalise-grant-automation-build.yml` L634](../../config/revitalise-grant-automation-build.yml#L634), between `code-app-build` and `package-code-app`.

**Change 2** — [`src/code-apps/trustee-review-portal/bundle-budget.json`](../../src/code-apps/trustee-review-portal/bundle-budget.json#L1): JS 1,241,000 against 1,204,716 measured; CSS 79,500 against 77,221. Both ~3% headroom, as approved.

**Change 3** — [`C-TECH-055`](../../constraints/technology/technology-constraints.md#L110) amended into an explicit (a) magnitude / (b) signature split, with the withdrawn wording retained inline.

**Change 4** — [`agents/build-agent.md` L154](../../agents/build-agent.md#L154), new subsection *"A repeating warning is matched on its FIGURES, not its wording"*.

**Change 5** — [`agents/improvement-agent.md` L370](../../agents/improvement-agent.md#L370), derived `verify-*.py` count 55 → 56.

### Verification executed after applying

| Command | Result |
|---|---|
| `python3 scripts/verify-code-app-bundle-budget.py --selftest` | exit 0, **8/8** |
| `python3 scripts/verify-code-app-bundle-budget.py src/code-apps/trustee-review-portal` | **exit 0** against the real budget |
| Same, negative control at the stale 558,000 figure | **exit 1**, naming the 646,716-byte overage — correct polarity on real bytes |
| `python3 scripts/verify-build-config.py config/…-build.yml` | **exit 0**, 11 rungs green including `suite gates have their own step` and `wired scripts own their wiring` |
| `python3 scripts/verify-improvement-log.py --check` | **exit 0** — blocker trigger cleared, 0 `awaiting-approval` |
| `python3 scripts/generate-known-failure-modes.py --check` | current at **571 entries** |
| `python3 scripts/verify-derived-counts.py` | SOFT, 5 drifted claims — **all pre-existing in other files**; this review's own registered claim agrees at 56 |

**§6's predictions were exact, measured rather than asserted:** 571 entries, 568 distinct lessons, 44 recurring classes, 621 digest lines. `untriaged-tool-warning` remains x7; no new class row appeared.

**The pre-parking simulation earned its keep.** It caught two schema errors that reading `classify()` would not have: `evidence_grep` must be an object `{file, contains}`, and `reobserved` requires all five of `level, by, ts, rerun, result`. Both were wrong in the first draft disposition and right in the applied one.

**One finding appended**, id from `scripts/allocate-improvement-id.py` read immediately before the write: `IMP-0574`, stamped `appended_by` and **not** `reviewed_in` (`IMP-0456`), carrying a `deferred_reason` — `build/artifacts/**` is gitignored while 34 manifests are tracked, which whoever builds the signature-diff gate must settle first.

**`IMP-0573` closed `APPLIED`** with `evidence_grep` pointing at the wired step and a `reobserved` recording the re-run gate, its negative control and the byte measurement. Its own `proposed_change` named only the agent-file edit; that edit is change 4, and the reason the review did not stop there is recorded in `applied_by` — as the whole remedy it would have been the seventh prose patch to a class that has taken six.

**Disposition simulated before parking**, per step 8, on a scratch copy of the log — and it caught two real schema errors that a reading would not have: `evidence_grep` must be an object `{file, contains}` and not a string, and `reobserved` requires all five of `level, by, ts, rerun, result`. Corrected in the planned disposition.

| Simulated state | Gate verdict |
|---|---|
| `IMP-0573` stamped `reviewed_in`, 11 entries stamped `excluded_by` (draft-time, keyword not sent) | `TRIGGER: 1 blocker in state 'awaiting-approval' — a review has already processed these and is parked at its own gate`. **Expected and correct**: the blocker rung fires on `unread` OR `awaiting-approval` alike, and the remedy is the keyword, not another session. |
| Plus `IMP-0573` → `APPLIED` with `evidence_grep` and `reobserved` | 1 error remaining: the `code-app-bundle-budget` needle is not yet in the build config. **This is the change itself, unapplied** — it resolves the moment change 1 is wired. |

The real `logs/improvement-log.jsonl` was not touched: it contains 0 references to `2026-09-01-improvement-review-10`.

**Re-verification obligations at apply time**, stated now so they are not skipped: re-run `verify-improvement-log.py --check` and read its `corrects` warnings; re-measure the routed-work table above (both rows are exactly the kind that go stale — one is another dispatch's in-flight fix); re-run the preflight after wiring change 1, which is the only step that cannot be proven before the script is in `scripts/`; and re-read the Dev Summary row before relying on §5's claim that it is fixed.
