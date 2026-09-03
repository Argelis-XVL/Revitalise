# Improvement Review — 2026-09-02

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 1 `NEW` → 1 cluster
**Trigger:** blocker escalation — [`IMP-0582`](../../logs/improvement-log.jsonl#L579), unread, appended by pipeline-agent at 15:05
**Gate:** `APPROVE IMPROVEMENTS` — supplied in the dispatch brief
**Status:** APPLIED
**WBS:** 6.8 (carried from the finding; system-rule changes, not a contracted deliverable)

`C-TECH-030` said every deploy target must be build-agent's managed artifact, and its `Verify By`
column said *"Pipeline log references artifact manifest; no manual deploy steps"* — a description
of the desired state with no command behind it. So nothing ran, and a dispatch was told to deploy
[`build/artifacts/trustee-portal-visual-refresh-20260902-3/`](../../build/artifacts/trustee-portal-visual-refresh-20260902-3),
a directory holding both solution zips, a code-app `dist/` and `test-results/` and no
`manifest.json`. That directory is now refused by a command, at
[activation step 3](../../agents/pipeline-agent.md#L37), before any environment is touched.

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Review 9, change 2 — [the wiring obligation in `agents/improvement-agent.md`](../../agents/improvement-agent.md#L381): a gate is not finished until a build config invokes it or `SUITE_GATE_EXEMPT` states why it cannot | 2026-09-01 | `gate-cannot-fail` | **NO** — no entry after [`IMP-0569`](../../logs/improvement-log.jsonl#L566) carries this class | **Working, and positively tested by this review.** This review authored a gate and wired it in the same change; [`verify-build-config.py`](../../scripts/verify-build-config.py#L718) exits 0 |
| Review 10, changes 1–3 — [`scripts/verify-code-app-bundle-budget.py`](../../scripts/verify-code-app-bundle-budget.py) plus its build step | 2026-09-01 | `untriaged-tool-warning` | **NO** | Working, **but not yet exercised.** The only build since (2026-09-02 16:00) blocked at the improvement-log preflight, step 3 of 68, and never reached the bundle step. No recurrence is therefore weak evidence here — say so rather than claim a clean run |

**Classes that recurred after a prose fix:** none.
**Classes that recurred after a gate:** none. No `gate-cannot-fail` finding is raised by this review.

The review-9 row is the stronger of the two, because it was tested in the only way that counts:
the obligation applied to this review's own output, and this review met it without being told.

---

## 2. Clusters and promotion decisions

```
CLUSTER: artifact-cited-for-deploy-has-no-build-record  (x1: IMP-0582)
Altitude:   CLASS — one instance, but the ladder's "a tool could catch it mechanically" row
            fits before the count matters, and severity is blocker. The property is general:
            an artifact DIRECTORY does not distinguish a finished build from a build-agent
            session that died after packing. Nothing about it is specific to this feature.
Ladder row: "A tool could catch it mechanically" → a script plus a gate.
            NOT "a constraint row": C-TECH-030 already exists and already says the right
            thing. It was unenforced, not missing.
Becomes:    scripts/verify-artifact-provenance.py — a HARD preflight over the NAMED artifact
            directory: manifest.json present, parsing, naming ITSELF, status beginning
            SUCCESS or DEPLOYED, and some docs/tests/ report naming the build.
            Wired as pipeline-agent activation step 3; C-TECH-030's Verify By replaced with
            the command; SUITE_GATE_EXEMPT with a stated reason.
Retires:    nothing — no instance gate existed for this class; it was undefended.
Cites:      IMP-0582
Residual:   THREE, and all are real.
            (a) The gate proves the artifact has a build RECORD, not that the zips inside it
                are what that record describes. A manifest and its zips can still disagree;
                verify-build-manifest-note.py owns the manifest's claims, and nothing checks
                zip contents against them.
            (b) The docs/tests/ check is satisfied by a report NAMING the build, not by a
                report APPROVING it. A test report recording a failure against this exact
                artifact passes this rung. Making it read a verdict would be prose-matching,
                which this project has measured at 48–100% false five times (IMP-0422).
            (c) OK_STATUS_PREFIXES is fail-closed on two words enumerated from the 38
                manifests on disk. A legitimate third outcome word introduced later halts a
                deploy until someone adds it. The finding message says so and names the
                constant; that is the mitigation, and it is not a complete one.
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | [`scripts/verify-artifact-provenance.py`](../../scripts/verify-artifact-provenance.py) | New HARD preflight: the artifact directory a deploy dispatch names has a `manifest.json` that names itself, a `SUCCESS`/`DEPLOYED` status, and a `docs/tests/` report naming the build. Missing `logs/build.log` line is a WARNING, not a failure | IMP-0582 | YES — `python3 scripts/verify-artifact-provenance.py <artifact-dir>` | `SUITE_GATE_EXEMPT` — its inputs (the manifest, the test report) do not exist while the build that produces the artifact is running, so a build step would name a path nothing in the config produces. Reason recorded at [`verify-build-config.py:718`](../../scripts/verify-build-config.py#L718) |
| 2 | agent | [`agents/pipeline-agent.md`](../../agents/pipeline-agent.md#L37) | New activation step 3 invoking the gate before the constraint check and before any environment is touched; plus the rule that the deploy target is the artifact on build-agent's `HANDOFF … artifact:` line, never the newest directory in a listing. Steps 4–8 renumbered | IMP-0582 | N/A — instruction change, but the step it mandates is the command in row 1 | N/A |
| 3 | constraint-amendment | [`constraints/technology/technology-constraints.md:71`](../../constraints/technology/technology-constraints.md#L71) | `C-TECH-030`'s `Verify By` replaced with the command from row 1. The withdrawn wording is retained inline, per this repository's correction style | IMP-0582 | YES — the column now names an executable check | N/A |
| 4 | script | [`scripts/verify-build-config.py`](../../scripts/verify-build-config.py#L718) | `SUITE_GATE_EXEMPT` entry for the new gate, with the reason and the file that invokes it | IMP-0582 | YES — `python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml`, exit 0 | already wired |
| 5 | agent | [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L370) | The registered `verify-*.py` count moves 56 → 57 in the same change that adds the gate, per that section's own rule | IMP-0582 | YES — `python3 scripts/verify-derived-counts.py`, claim `improvement-agent-verify-script-count` clean | N/A |

**Constraint budget: 0 of 3 used.** Row 3 is a `constraint-amendment`, not a new row — the
constraint was already correct and already HARD. What it lacked was a command. Adding
`C-TECH-0nn — "and this time we mean it"` would have been the bloat this budget exists to prevent.

### No `agents/build-agent.md` edit, and the measurement is why

The dispatch brief invited one. It is not warranted. `logs/build.log`'s 16:00 entry records
build-agent handling this correctly and unprompted: it blocked at its own improvement-log
preflight, resolved a fresh
[`-20260902-4/`](../../build/artifacts/trustee-portal-visual-refresh-20260902-4) via
`resolve-artifact-dir.py`, wrote a `BLOCKED` manifest there, and **left `-3/` untouched as
evidence** — which is why this review could re-observe the defect at all. Nothing build-agent did
caused `IMP-0582`, and an instruction added to a file whose agent already behaved correctly is a
rule that teaches nothing and costs every future read.

### Corpus measurement — 9 real deploy targets, 0 false positives

Per the "run it against the real corpus before you wire it" obligation. The corpus this gate will
actually run over is not `build/artifacts/` — it is the directories a deploy dispatch names, and
[`logs/pipeline.log`](../../logs/pipeline.log) records exactly 9 of those.

| Corpus | Result | Adjudication |
|---|---|---|
| **9 directories `logs/pipeline.log` records as deployed** | **9 pass, 0 fail. 1 warning.** | **0 false positives.** The one warning — `revitalise-grant-automation-20260823-2` has no `SUCCESS` line in `logs/build.log` — is a TRUE observation: the line really is absent |
| `trustee-portal-visual-refresh-20260902-3`, the finding's own directory | FAIL: `no-manifest`, `no-test-report-names-this-build` | True positive. This is `IMP-0582`, reproduced by command |
| All 51 directories under `build/artifacts/` | 16 pass, 35 fail | Not this gate's corpus. 12 are failed or blocked builds, 11 are pre-convention directories with no manifest, 1 is `test-results/` which is not an artifact directory at all, and none is a deploy candidate |

**The one adjudication worth stating plainly**, because it is the closest thing to a false
positive in the set: 5 directories (`revitalise-alert-links-20260820-1` and four siblings) fail on
`no-test-report-names-this-build` alone, and their manifests record a real DEV deploy. Those are
**true positives** against `C-TECH-030`'s build → test → deploy chain — they were deployed in
August with no test report naming them — but a re-deploy of one today would halt until a report
names it. That is the constraint working, and the finding message says how to clear it.

**Why the `logs/build.log` rung is a WARNING and not a failure.** Hard-failing on it would have
produced 1 false halt in 9. That log is appended by hand at the end of a dispatch, so a missing
line is evidence a log write was skipped, not evidence a build never ran; `manifest.json` is
written by build-agent as part of the build itself and is the load-bearing signal. A gate that
halts a legitimate deploy on the weaker of two signals is how a gate teaches people to route
around it (`IMP-0181`).

**Fail-closed set enumerated from the corpus, not invented** (`IMP-0560`). The 38 manifests on
disk carry first status words `SUCCESS`, `DEPLOYED`, `FAILED`, `BLOCKED` and one null.
[`OK_STATUS_PREFIXES`](../../scripts/verify-artifact-provenance.py#L84) is `("SUCCESS",
"DEPLOYED")`; `DEPLOYED` is in the set because four artifacts record their deploy in `status`
rather than the word SUCCESS, and re-deploying one of those is legitimate.

**Selftest: 9 fixtures, PASS.** Including the two that matter most — the missing-`build.log`-line
case asserts the gate does **not** fail, and the `DEPLOYED TO DEV, NOT RUNNABLE — …` status with a
slashless `artifact_path` asserts both real-world irregularities pass.

---

## 4. Retirements

> Retirement check performed: `C-TECH-030` and its neighbours reviewed; none currently redundant.
> `C-TECH-030` itself was the candidate — an unverifiable constraint is a comment, and the
> anti-bloat rule says so — but the correct disposal was to make it executable rather than to
> retire it, because the rule it states is right and is now enforced. 10 retired rows and 82 live
> rows across `constraints/`, both derived at application time, unchanged by this review.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0549, IMP-0550, IMP-0551, IMP-0552, IMP-0562, IMP-0563, IMP-0566, IMP-0567, IMP-0570, IMP-0571, IMP-0572, IMP-0574, IMP-0575, IMP-0576, IMP-0577, IMP-0578, IMP-0579, IMP-0580, IMP-0581

**Scope, stated so it is not a silent cap.** The queue holds 138 `NEW` entries: 19 `unread`, 119
`reviewer-deferred`. This dispatch was summoned by **one unread blocker**, and an unread blocker
does not pull a review of everything around it (`IMP-0183`). The 18 other unread entries are all
`friction` or `rework`; each is stamped `excluded_by` naming this review, so the queue records
that they were seen and not taken rather than reporting them as unlooked-at. The 119
`reviewer-deferred` entries carry human-accepted reasons and were left alone.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0574 | `declared-policy-not-mechanically-enforced` | Already `reviewer-deferred` with a recorded reason; not this review's to reopen. Noted here because **change 3 is an instance of its class** — `C-TECH-030`'s `Verify By` was exactly a declared policy with no mechanism — so this review is evidence for it, not a substitute | its own recorded `revisit_when` |
| IMP-0577, IMP-0581 | `no-assertion-on-shipped-content` | Two instances of one class, both `rework`, neither a blocker. This is a genuine second instance and the altitude rule will apply to it — which is precisely why it deserves its own review rather than a rider on a blocker dispatch | the next scheduled improvement review, or a third instance |
| The other 15 unread | various | `friction`/`rework`, no blocker, outside this dispatch's trigger | next queue-depth or feature-completion trigger |

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 579 | 580 |
| Distinct lessons | 576 | 577 |
| Recurring classes (x≥2) | 47 | 47 |
| Digest lines | 625 | 626 |

The one new entry is this review's own: `IMP-0583`, `friction`, class
`flag-semantics-not-what-its-name-implies` — [`scripts/verify-review-document.py`](../../scripts/verify-review-document.py)
takes no positional argument and its `--only` flag needs a full repo-relative path, not the
basename its name implies, so closing this review cost three invocations of one check. Logged, not
acted on: one instance of friction is a log note, not a change (`skills/how-to-promote-a-finding.md`
§1, first row).

`--check` reported the digest stale, and **this review cannot attribute that to a prior dispatch**:
the check was run *after* this review had already stamped `reviewed_in` and `excluded_by` on 8
entries, which is itself enough to make it stale. The pre-session state of
`logs/improvement-log.jsonl` is not in git — it was already modified in the working tree — so the
question is not answerable, and a claim either way would be a guess in the register of a
measurement. Regenerated with `python3 scripts/generate-known-failure-modes.py`; `--check` now
exits 0 at 579 entries. The
figures do not move because `IMP-0582`'s lesson was already in the log and therefore already in
the digest; what changed is that the lesson now also has a command behind it.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-02-improvement-review.md

Findings processed: 1 NEW  →  1 cluster
Regression check:   2 prior changes audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 1 constraint amendment, 2 gates/scripts,
                    0 skill/knowledge edits, 2 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 0 left as notes
Digest:             regenerated — 576 lessons, 47 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | `scripts/verify-artifact-provenance.py` — new HARD preflight, 9/9 selftest, 0 false positives over the 9-directory deploy corpus | working tree, 2026-09-02 | IMP-0582 |
| 2 | `agents/pipeline-agent.md` — activation step 3 + the HANDOFF-line rule; steps 4–8 renumbered; `C-TECH-030` bullet names the command | working tree, 2026-09-02 | IMP-0582 |
| 3 | `constraints/technology/technology-constraints.md:71` — `C-TECH-030` `Verify By` now executable | working tree, 2026-09-02 | IMP-0582 |
| 4 | `scripts/verify-build-config.py` — `SUITE_GATE_EXEMPT` entry with reason | working tree, 2026-09-02 | IMP-0582 |
| 5 | `agents/improvement-agent.md` — registered script count 56 → 57 | working tree, 2026-09-02 | IMP-0582 |

**Deviation from the finding's own `proposed_change`, recorded because it must never be silent.**
[`IMP-0582`](../../logs/improvement-log.jsonl#L579) proposed a change to `agents/pipeline-agent.md`
only. That is applied, as change 2 — but as the *whole* remedy it would have been prose against a
defect a command settles, and the ladder's "prefer the most mechanical home available" row is not
optional. The intent survived; the scope widened. This is recorded in the entry's `applied_by`, in
this table, and in the gate output.

**Re-observation** (`observable_at: V2`, so a document is not closure):
`python3 scripts/verify-artifact-provenance.py build/artifacts/trustee-portal-visual-refresh-20260902-3/`
— the exact directory this dispatch was told to deploy, still untouched on disk — **exits 1**,
naming `no-manifest` and `no-test-report-names-this-build` under
*"C-TECH-030 (HARD): do not begin Stage 1"*. The negative control,
`build/artifacts/trustee-portal-visual-refresh-20260902-2/` (the last artifact really deployed),
**exits 0**. The directory that halted a dispatch by inspection now halts it by command, and the
deployable sibling next to it is not caught with it.

**Verification level reached: V2.** The gate has been executed against real artifact directories
and real logs. It has **not** yet run inside a live pipeline-agent dispatch; the next deploy
dispatch is what takes it to V3, and pipeline-agent is who can do that.

Entries rejected, with reasons: **none.**

### Gates re-run after applying

| Command | Result |
|---|---|
| `python3 scripts/verify-artifact-provenance.py --selftest` | PASS — 9 fixtures |
| `python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml` | exit 0 |
| `python3 scripts/verify-improvement-log.py --check` | **exit 0** — the blocker trigger that halted the 16:00 build is cleared |
| `python3 scripts/generate-known-failure-modes.py --check` | exit 0, 579 entries |
| `python3 scripts/verify-derived-counts.py` | exit 1 (SOFT) — 6 drifted claims, **all pre-existing and none touched by this review**; `improvement-agent-verify-script-count` is clean at 57 |
