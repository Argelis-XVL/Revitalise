# Improvement Review — 2026-09-06 (3)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 `NEW` → 1 cluster
**Trigger:** blocker escalation — `IMP-0633`, `unread`, severity `blocker`, `observable_at` V2
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** ~~DRAFT — nothing applied. `reviewed_in` stamped at step 6; `status` stays `NEW`.~~
**APPLIED 2026-09-07** on `APPROVE IMPROVEMENTS` from the reviewer (Xander Lykopoulos). Both
entries closed; no rule, constraint, gate or agent-file change was made. See §8 for the applied
record and the two places the applied form deviates from the approved draft.
**WBS:** `wbs:3.2,3.3,3.4`

**Conclusion first.** The defect is fixed, I re-ran the original reproduction myself and it
passes, and **this review proposes no rule, constraint, gate or agent-file change at all**. The
only thing the keyword releases is the bookkeeping: closing two log entries with a `reobserved`
stamp. Nothing else is waiting on it.

---

## 1. The evidence, re-measured this session

Nothing below is quoted from the dispatching brief or from `IMP-0634`'s own prose. Every row was
run or read here.

| Claim | Instrument | Result |
|---|---|---|
| The manifest's status word is now `SUCCESS` | `grep -n '"status"'` on the file | [`manifest.json` L51](../../build/artifacts/revitalise-grant-automation-20260906-3/manifest.json#L51) reads `"status": "SUCCESS"` |
| The gate that halted the deploy now passes | **executed** `python3 scripts/verify-artifact-provenance.py build/artifacts/revitalise-grant-automation-20260906-3/` | `PASS`, **exit 0**, 1 unrelated warning (see §4) |
| The allowlist was not widened to accommodate the outlier | read [`verify-artifact-provenance.py` L84](../../scripts/verify-artifact-provenance.py#L84) | still `OK_STATUS_PREFIXES = ("SUCCESS", "DEPLOYED")` — unchanged, which is the right outcome |
| `SUCCESS` is build-agent's own documented word | read [`build-agent.md` L139](../../agents/build-agent.md#L139) and [L289](../../agents/build-agent.md#L289) | L139 defines what `SUCCESS` means; L289's manifest template prints `"status": "SUCCESS"` |
| No other build has ever written `PASSED` | **enumerated all 49** `build/artifacts/*/manifest.json` and printed each top-level status | `SUCCESS` ×23, `BLOCKED` ×11, `FAILED` ×7, `DEPLOYED …` ×4, absent ×1. **`PASSED`: zero.** `IMP-0634`'s claim is independently confirmed |
| The 73/73 step result was not disturbed | the provenance gate re-reads the manifest as a whole and accepts it | unchanged; only the one field moved |

**Level reached: V2.** The artifact is packaged and the packaged artifact is accepted by the gate
that reads it. Nothing was imported into an environment by this review, so this is not V3 — see §4.

---

## 2. The cluster, and why it produces no rule change

```
CLUSTER: manifest-field-vocabulary-mismatch  (x2 entries: IMP-0633, IMP-0634)
Altitude:  INSTANCE — and the x2 is two REPORTS of ONE incident, not two incidents.
           Both name the same build, the same manifest and the same field. The altitude
           rule's "second instance -> generalise" does not fire on a single occurrence
           described from two sides.
Ladder row: skills/how-to-promote-a-finding.md section 4 - "a finding whose class has one
           member is a candidate for a knowledge line, not a constraint. Wait for the
           second instance - unless the severity is blocker AND the mechanism is a
           platform law." Severity is blocker; the mechanism is a naming convention,
           not a platform law. So the exemption does not apply either.
Becomes:   nothing durable. The lesson already reaches the read path: the class renders in
           logs/known-failure-modes.md at L77.
Retires:   nothing - see section 3.
Cites:     IMP-0633, IMP-0634
Residual:  verify-artifact-provenance.py is NOT wired into any build config or workflow
           (grep over config/*.yml and .github/workflows/ returns zero hits), so the
           vocabulary is still only checked downstream, at deploy time. That gap is real
           and is deliberately left open - see section 4.
```

The tempting change here is a build-time check that a new manifest status word is in the
allowlist. I am not proposing it, for the reason the ladder gives: one occurrence, and the
existing downstream gate already caught it correctly and cheaply — the deploy halted **before any
environment was touched**, which is the gate working, not failing.

---

## 3. Regression check and retirement

**Prior review audited:** [2026-09-06-improvement-review-2.md](2026-09-06-improvement-review-2.md),
which processed `IMP-0627`–`IMP-0630` and is still parked at its own gate. Its classes are
`harness-blocks-destructive-call`, `stale-deferral-uncaught-across-sessions` and
`manifest-narrates-its-own-disposition`. **None recurred here** — this cluster's class is new to
the log as of this build session, so there is nothing to escalate from prose to a gate.

**Closure-level audit.** Both entries are `observable_at` V2, and both are closed on a V2
re-observation: the packaged artifact re-read by the gate that rejected it. That is the matching
level, not a document asserting the fix.

**Retirement candidate: none.** Derived, not typed — 10 retired rows and 85 live rows across
`constraints/`. No rule in this cluster's area is now redundant; `C-TECH-030` is doing exactly the
job it was written for.

---

## 4. What is deliberately left open

**The build log line is missing, and the gate says so.** The provenance run emits one warning: no
`SUCCESS — build/artifacts/revitalise-grant-automation-20260906-3` line in `logs/build.log`. That
log is appended by hand at the end of a build dispatch, so this is evidence a log write was
skipped. It is not this review's to fix — it is build-agent's line to append — and it does not
affect the closure, because the manifest is the load-bearing signal and the gate says so itself.

**No build-time vocabulary check is proposed.** Stated in §2 as the cluster's `Residual` so it is
on the record rather than silently dropped. A second, genuinely separate occurrence is what would
justify building one.

**This review did not reach V3.** The deploy has not been re-attempted. `IMP-0634` recommended
waiting for that re-attempt and calling it the closing observation. I am not waiting, and the
reason is that `observable_at` is **V2**, not V3: the defect was a malformed packaged artifact, and
re-running the gate that reads that packaged artifact is the original reproduction step. Requiring
V3 would be claiming a level above what the finding asks for, which
[`C-TECH-053`](../../constraints/technology/technology-constraints.md) forbids in the other
direction too.

---

## 5. Why this is at a gate at all

The dispatching brief asked whether pure reobservation of an already-fixed artifact defect could be
applied directly, without the keyword. It cannot, and I checked rather than assumed:

- [`agents/improvement-agent.md` L135–L136](../../agents/improvement-agent.md#L135) puts every
  `status` move at step 8, **on approval**. `reviewed_in` is the only field that moves at draft
  time, and it is stamped.
- **Simulated, not read** ([`improvement-agent.md` L292–L305](../../agents/improvement-agent.md#L292)
  requires this): on a scratch copy of the log, stamping `reviewed_in` alone leaves the gate
  **FAILED**, with the trigger merely re-worded from `unread` to `awaiting-approval`. Applying the
  full closure — `status: APPLIED`, `applied_by`, `reobserved`, `evidence_grep` on both entries —
  gives `verify-improvement-log: OK (schema + triggers)`, **exit 0**, 7 pre-existing warnings.

So the honest answer to *"does the check exit 0 now?"* is **no, and it cannot until the keyword
arrives** — but the exact disposition that makes it exit 0 has been measured and is written out
below, ready to apply.

## 6. What the keyword will move

Both entries: `status: APPLIED`, `reviewed_in` (already stamped), `applied_by` naming this review,
and:

```json
"reobserved": {"level": "V2", "by": "improvement-agent, review 3 (2026-09-06)",
               "ts": "2026-09-06T23:59",
               "rerun": "python3 scripts/verify-artifact-provenance.py build/artifacts/revitalise-grant-automation-20260906-3/",
               "result": "PASS, exit 0 - manifest.json status reads SUCCESS and C-TECH-030's provenance check accepts the artifact; 1 unrelated warning about a missing logs/build.log line"}
"evidence_grep": {"file": "build/artifacts/revitalise-grant-automation-20260906-3/manifest.json",
                  "contains": "\"status\": \"SUCCESS\""}
```

Then regenerate `logs/known-failure-modes.md`. No file under `agents/`, `constraints/`, `skills/`,
`knowledge/`, `scripts/` or `config/` is touched by this review.

---

## 7. Scope excluded, stated rather than capped silently

This dispatch was summoned by **one unread blocker**. Per
[`agents/improvement-agent.md` L84–L87](../../agents/improvement-agent.md#L84), one unread blocker
must not pull a review of everything around it. Excluded and untouched:

- **12 other `unread` entries** — `IMP-0611`, `IMP-0612`, `IMP-0613`, `IMP-0614`, `IMP-0615`,
  `IMP-0617`, `IMP-0618`, `IMP-0620`, `IMP-0625`, `IMP-0626`, `IMP-0631`, `IMP-0632`. None is
  severity `blocker`; none shares this cluster's class. **All 12 are stamped `excluded_by` naming
  this review** (applied 2026-09-07). ~~They are not stamped `excluded_by`, because naming them
  here in a non-citation position is the declaration the rule asks for and stamping would be a
  write to entries this review has not read.~~ That draft reasoning was **measured wrong at apply
  time**: enumerating the ids here is a citation, so the gate raised one
  `state unread, cited by 1 review document … carries NO 'reviewed_in'` warning per excluded id —
  19 warnings where 7 were pre-existing. `excluded_by` is the field activation step 2 provides for
  exactly this (`IMP-0557`), and stamping it returned the count to the 7 pre-existing warnings.
- **1 `awaiting-approval` entry** — `IMP-0608`, parked at its own document. The remedy is a
  keyword against that document, not a session.
- **136 `reviewer-deferred` entries** — left as deferred, per activation step 2.

---

## 8. Applied record — 2026-09-07, on `APPROVE IMPROVEMENTS`

**Re-verified before applying**, per activation step 8. The keyword approves a draft, not the tree
the draft was written against:

| Premise re-checked | Instrument | Result |
|---|---|---|
| The gate still passes | **re-executed** `verify-artifact-provenance.py` | PASS, exit 0 — unchanged |
| The manifest still reads `SUCCESS` | grep on the file | L51 `"status": "SUCCESS"` — unchanged |
| No entry appended since the draft | max id in the log | still `IMP-0634`, 631 entries |
| No `corrects`/`contests` naming either entry | scanned every entry's edges | **NONE** |

### Closed

| Entry | Severity | `observable_at` | Closed as | Closure evidence |
|---|---|---|---|---|
| `IMP-0633` | blocker | V2 | `APPLIED` | V2 `reobserved` — the provenance gate re-run against the packaged artifact |
| `IMP-0634` | friction | V2 | `APPLIED` | same re-run, plus an independent re-enumeration of all 49 manifests |

### Changed nothing

No file under `agents/`, `constraints/`, `skills/`, `knowledge/`, `scripts/` or `config/` was
touched. 0 constraints, 0 gates, 0 retirements — as approved.

### Two deviations from the approved draft, both recorded rather than silent

1. **`reobserved.ts` is `2026-09-07T00:05`, not the draft's `2026-09-06T23:59`.** The re-run
   happened at apply time, after midnight. The timestamp records when the observation was actually
   made; back-dating it to the draft's figure would have made it a copy of the draft rather than a
   record of the re-test, which is the precise thing the field's validator exists to catch.
2. **The 12 excluded `unread` entries are stamped `excluded_by`, which §7 originally said they
   would not be.** The intent — declare the scope cap rather than apply it silently — is unchanged
   and is what survived; the literal wording measured as wrong. Compelled, not chosen: the
   enumeration produced **12 citation-stamp warnings** (19 total against 7 pre-existing), each
   telling the next queue reader that an entry looked unopened. Stamping removed exactly those 12
   and added none. §7 carries the withdrawn wording struck through.

### Verification at close

`verify-improvement-log.py` (schema) exit 0 · `verify-improvement-log.py --check` **exit 0**, no
triggers, no errors, 7 pre-existing warnings · `generate-known-failure-modes.py` regenerated, then
`--check` exit 0 (current at 631 entries) · `verify-review-document.py` exit 0 ·
`verify-doc-line-links.py` exit 0.

**Not verified: anything at V3 or above.** No environment was touched. The deploy of
`revitalise-grant-automation-20260906-3` has not been re-attempted, and this review makes no claim
that it will succeed — only that the artifact now clears the provenance gate that halted it.

### One finding appended by this review

`IMP-0635` (friction, class `activation-rule-overridden-by-draft-reasoning`), carrying
`appended_by` naming this document. It records deviation 2 above as its own finding: activation
step 2 states the `excluded_by` rule correctly and completely, and this draft reasoned around it
anyway. Left `NEW`/unread deliberately — a review does not process a finding it wrote in the same
sitting, and the altitude question it raises needs a second instance before it is worth answering.

### SOFT gate fired, and none of it is this review's

`verify-derived-counts.py` exits 1 with 4 drifted claims and 1 registry defect. **Attributed, not
waved through:** three concern secured-column counts in the dev summary and the REV Trustee role
XML, and one is the `rev_setting` row count disagreeing across three deploymentSettings files —
all other dispatches' in-flight work. The fourth, `known-failure-modes-digest-line-count`, was
measured at **644 lines before this session wrote anything** and is still 644 after the
regeneration, so the 632→644 drift accumulated earlier and this review neither caused nor widened
it. Reported as WARN per the gate's own severity, not fixed here.
