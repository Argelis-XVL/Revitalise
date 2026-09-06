# Improvement Review — 2026-09-05

**Status:** APPLIED 2026-09-05 under `APPROVE IMPROVEMENTS`. See §11 for the applied record and
for the one premise that changed between approval and application.
**Trigger:** blocker escalation — [`IMP-0602`](../../logs/improvement-log.jsonl#L599), unread, appended by build-agent.
**Filename claimed** at step 6 via `scripts/allocate-review-number.py`.

---

## 1. Conclusion

`IMP-0602` is genuinely resolved in substance and should be closed — the two `blocked_on` notes it
named were re-tested live and re-dated, and
[`verify-pipeline-config.py`](../../scripts/verify-pipeline-config.py) now passes at 104 steps with
0 expiring. **But closing it does not clear the halt on its own, and the review draft does not
either.** Only the keyword does. Three findings beyond the brief were measured, and one of them is a
live defect that will halt a build again on **2026-09-20** if nothing is applied.

---

## 2. Scope, and what was excluded

`python3 scripts/verify-improvement-log.py --check` reports **133 NEW: 5 unread, 0
awaiting-approval, 128 reviewer-deferred, 0 already-fixed**.

Scope is the **5 unread** entries: [`IMP-0601`](../../logs/improvement-log.jsonl#L598),
[`IMP-0602`](../../logs/improvement-log.jsonl#L599),
[`IMP-0603`](../../logs/improvement-log.jsonl#L600),
[`IMP-0604`](../../logs/improvement-log.jsonl#L601),
[`IMP-0605`](../../logs/improvement-log.jsonl#L602).

**Excluded: the 128 `reviewer-deferred` entries**, each carrying a `deferred_reason` a human
accepted. Not re-derived, per activation step 2. The brief named only `IMP-0602`; the other four
unread entries are in scope because step 2 defines scope by state, not by brief.

The gate also emits 5 standing `corrects` warnings (`IMP-0290`, `IMP-0298`, `IMP-0320`, `IMP-0430`,
`IMP-0437`). None names an entry this review acts on. Left untouched.

---

## 3. Live re-verification of the brief's premise

The brief asked me to confirm that `IMP-0603`/`IMP-0604` actually resolved what `IMP-0602`
described, rather than taking the prior handoff's word. **Confirmed, and it holds.** Measured, not
read:

| What `IMP-0602` named | State now | How settled |
|---|---|---|
| `environments.dev.post_deploy[1]` — trustee Code App team share | `blocked_on_asserted: 2026-09-05`, `satisfied_on: 2026-09-05` | Reviewer's own V4 UI inspection ([line 1131](../../config/revitalise-grant-automation-pipeline.yml#L1131)) |
| `environments.tst_acc.environment_prerequisites[0]` — Dataverse application user | `blocked_on_asserted: 2026-09-05`, `satisfied_on: 2026-09-05` | `pac org fetch` FetchXML against `systemuser` ([line 1627](../../config/revitalise-grant-automation-pipeline.yml#L1627)) |

`python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml` run
live this session: **PASS — 104 steps, 7/8 blocked_on notes fresh, 0 expiring, 1 accepted by
baseline**, exit 0. Both notes IMP-0602 named are among the fresh.

---

## 4. The finding the brief did not contain — a resolved note still on the expiry treadmill

`check_blocked_on_staleness` in
[`verify-pipeline-config.py:525`](../../scripts/verify-pipeline-config.py#L525) reads `blocked_on`
and `blocked_on_asserted`. **It never reads `satisfied_on`.** So a note that is RESOLVED, carrying
a `satisfied_on` and a full `satisfied_by`, stays on the 14-day cadence and HARD-fails a build 15
days after its last re-date — forever, unless a human removes the `blocked_on`.

The correct pattern already exists in the same file at
[line 472](../../config/revitalise-grant-automation-pipeline.yml#L472): *"blocked_on REMOVED
2026-09-03 (IMP-0587), not re-dated"*. On 2026-09-05 three resolved notes were **re-dated instead**.

**Corpus measurement — 86 steps scanned, 3 findings, 3 true positives, 0 false positives:**

| Step | `satisfied_on` | `blocked_on_asserted` | Adjudication |
|---|---|---|---|
| `dev.post_deploy[0]` | 2026-09-05 | 2026-09-05 | TRUE — resolved by a working `pac` route |
| `dev.post_deploy[1]` | 2026-09-05 | 2026-09-05 | TRUE — resolved by reviewer V4 |
| `tst_acc.environment_prerequisites[0]` | 2026-09-05 | 2026-09-05 | TRUE — resolved by live FetchXML |

**Polarity check passed.** The one correctly-handled step ([line 472](../../config/revitalise-grant-automation-pipeline.yml#L472),
`blocked_on` removed) produces **no** finding. The corrected form scores better than the defective
form, which is the test `IMP-0422`/`IMP-0428` require of any candidate.

**Residual, stated plainly:** the corpus is a **single** pipeline config. 3/3 is a real measurement
but a small one, and a second config could contain a shape I have not seen.

### A smaller doc defect in the same block

[Line 1131](../../config/revitalise-grant-automation-pipeline.yml#L1131) reads
`blocked_on_asserted: 2026-09-05   # re-tested 2026-09-05 (IMP-0602): cause STILL HOLDS` — while
the same step carries `satisfied_on: 2026-09-05` and a `script:` comment three lines above reading
`RESOLVED 2026-09-05 by human V4`. *"Cause still holds"* and *"resolved"* sit in one block. No gate
reads that comment, and cluster A's check would not catch it either — it asserts on fields, not
prose. Reported, not gated: a prose gate here is the instrument this project has measured at
48–100% false five times.

---

## 5. Regression check

| Prior change | Class it targeted | Recurred? | Verdict |
|---|---|---|---|
| `BLOCKED_ON_WARN_DAYS = 4` early warning, [line 520](../../scripts/verify-pipeline-config.py#L520) (2026-09-03, `IMP-0585`) | `stale-deferral-uncaught-across-sessions` | **Yes — `IMP-0602`** | See below. Not a gate gap |
| Credential-boundary clause in [`agents/improvement-agent.md`](../../agents/improvement-agent.md) (2026-09-04, `IMP-0586`) | repository-fact vs live-state split | No | **Worked.** `IMP-0603`/`IMP-0604` are that clause executing correctly |

**The recurrence is not what `IMP-0602` says it is, and this changes the altitude call.**
`IMP-0602`'s `why_it_was_never_caught` says the 2026-09-03 review *"did not re-test these two"*.
True — but it omits that the review **named both notes and forecast their exact expiry dates two
days in advance**: [2026-09-03 review, line 97](2026-09-03-improvement-review.md#L97) reads *"expire
on **2026-09-05 and 2026-09-06**. A reviewer who re-tests only the eight named…"*.

So the class name `stale-deferral-uncaught-across-sessions` is wrong for this instance. It was
caught, forecast, and written down. Nobody acted, because both notes needed live or human action
that session could not take. **A forecast with no owner is not a control** — and adding a second
forecasting mechanism, which is what `IMP-0602`'s own `proposed_change` asks for, would be a rule at
the wrong altitude aimed at a mechanism that already fired.

---

## 6. Clusters

```
CLUSTER A: resolved-note-retains-live-expiry  (x3 steps, from IMP-0602/IMP-0604)
Altitude:  CLASS — a mechanically-checkable property of the config, not an instance
Ladder row: "a tool could catch it mechanically"
Becomes:   one check in scripts/verify-pipeline-config.py — a step carrying BOTH satisfied_on
           and a live blocked_on_asserted is an ERROR: remove the blocked_on (the IMP-0587
           pattern at line 472), do not re-date it
Retires:   nothing
Cites:     IMP-0602, IMP-0604, IMP-0587
Residual:  single-config corpus (§4). And the check cannot tell a genuinely-resolved note from
           a prematurely-closed one — it asserts shape, never truth
```

```
CLUSTER B: forecast-without-an-owner  (IMP-0602)
Altitude:  NOTE, not a rule — the existing mechanism fired and was correct (§5)
Ladder row: "one instance, cause is general" → nothing beyond the record
Becomes:   nothing. IMP-0602's proposed standing tracker is WITHHELD: the existing baseline
           route (config/gate-baselines.json, IMP-0588) already is that tracker, and
           prd.environment_prerequisites[0] uses it correctly today
Retires:   nothing
Cites:     IMP-0602, IMP-0585, IMP-0588
Residual:  a chronically-manual note still depends on a human choosing to act on a warning
```

```
CLUSTER C: platform-fact-groundtruthed  (x2: IMP-0603, IMP-0604)
Altitude:  KNOWLEDGE — the cause is general and a human needs to know it
Ladder row: "one instance, cause is general, a human needs to know it"
Becomes:   knowledge/technology/build-and-deploy.md — BAP-layer role assignment has no working
           live-query route on this project's tooling, distinct from Dataverse-table-backed
           prerequisites which do
Retires:   nothing
Cites:     IMP-0603, IMP-0604, IMP-0186
Residual:  IMP-0603 cannot be CLOSED on the evidence it carries — see §7
```

```
CLUSTER D: notes, no rule change  (IMP-0601, IMP-0605)
Altitude:  NOTE — both are a gate working exactly as designed
Becomes:   nothing. IMP-0601 was caught by verify-constraint-verifiers.py in its own session;
           IMP-0605 is verify-improvement-log.py firing correctly
Retires:   nothing
Cites:     IMP-0601, IMP-0605, IMP-0285
Residual:  IMP-0605 is the second instance of routed-work-not-reverified-at-apply-time
           (with IMP-0517). A third makes it a constraint row
```

---

## 7. The disposition simulation — and what it caught

Run per activation step 8 on a scratch copy, never the real log (`--log` takes a path; the real
file was not written).

**Scenario 1 — this draft as it stands** (`reviewed_in` stamped, `status` still `NEW`):

```
NOTE — 133 NEW: 0 unread, 5 awaiting-approval, 128 reviewer-deferred
TRIGGER: 2 NEW entry(ies) of severity 'blocker' in state 'awaiting-approval'
FAILED — 1 problem(s)
```

**The build stays halted.** The blocker rung fires on `unread` OR `awaiting-approval` alike
(`IMP-0516`). Stamping `reviewed_in` is required bookkeeping and is **not** a discharge.

**Scenario 2 — after the keyword** (`status: APPLIED`): the blocker TRIGGER is **gone** — `0
unread, 0 awaiting-approval`. Remaining errors are the simulation's own artefacts (files not yet
written), **except one real catch**:

```
ERROR: IMP-0603: reobserved.ts 2026-09-04T00:00 predates the finding's own ts 2026-09-05T00:00.
```

`IMP-0603` is `observable_at: V3`, and the only re-observation available — pipeline-agent's
cert-drive reproduction — happened on **2026-09-04**, *before* the finding was logged. So it cannot
close on that evidence. `Microsoft.PowerApps.Administration.PowerShell` is not installed on this
machine, so a fresh V3 reproduction is not available to me either.

**Proposed: `IMP-0603` stays `NEW` with a `deferred_reason` and a `revisit_when`**, not closed. An
honest open entry beats a closed one nobody tested (`IMP-0208`, `IMP-0224`, `IMP-0225`). Its
knowledge edit still applies.

---

## 8. Anti-bloat

- **New constraints: 0** (cap 3). Live rows **85**, retired **10** — both derived, not typed.
- **Retirement considered:** checked, **none warranted**. No rule in this area has been superseded;
  cluster A adds a check to an existing gate rather than a competing one.
- **`verify-*.py` count unchanged at 57** — cluster A edits an existing, already-build-wired script,
  so no new file and no `suite-gate-is-not-a-step` exposure.
- Digest is current (`generate-known-failure-modes.py --check`, exit 0).

---

## 9. Proposed disposition on the keyword

| Entry | Proposed | Note |
|---|---|---|
| `IMP-0601` | APPLIED — no rule change | Class marker; gate worked |
| `IMP-0602` | APPLIED | Substance resolved (§3); cluster A gate is its durable change |
| `IMP-0603` | **stays NEW** + `deferred_reason` + `revisit_when` | Cannot close: §7. Knowledge edit still applies |
| `IMP-0604` | APPLIED | Closes at V4 on the reviewer's 2026-09-05 inspection |
| `IMP-0605` | APPLIED — no new gate | Process-discipline note |

## 10. Reviewer decision required

Cluster A's check is a **repository fact** and within my boundary to write. But **removing the three
`blocked_on` blocks** from the config is an edit to a file owned by development-agent /
pipeline-agent. Per the credential-boundary table in
[`agents/improvement-agent.md`](../../agents/improvement-agent.md), the discharge is a repository
fact settled by a grep, so re-dating is mine — but a **deletion** changes delivery semantics.

**Recommend:** I add the check, and hand the three `blocked_on` removals to pipeline-agent, since
wiring the check before the config is corrected would halt the next build on all three.

---

## 11. Applied record — and the premise that moved

**The routed work in §10 was completed by another session while this review sat at its gate, and
that changed the application.** Re-measured at apply time per activation step 8, which is the only
reason it was noticed:

| Measurement | At draft (§4) | At apply |
|---|---|---|
| Steps with `satisfied_on` + live `blocked_on` | **3 of 86** | **0 of 86** |
| `blocked_on` notes checked by the staleness gate | 8 | 5 |

[`config/revitalise-grant-automation-pipeline.yml`](../../config/revitalise-grant-automation-pipeline.yml)
now carries `blocked_on REMOVED 2026-09-05 (IMP-0603/IMP-0604), not re-dated` on all three steps —
exactly the `IMP-0587` pattern §4 named as correct. The internal inconsistency §4 flagged at line
1131 (*"cause STILL HOLDS"* beside a resolved note) is gone with it.

**So the §10 hand-off is WITHHELD, not dispatched** (`IMP-0517`). Dispatching it would have
re-routed work already shipped — which is precisely `IMP-0605`'s own class,
`routed-work-not-reverified-at-apply-time`, reproduced inside the review that processes it.

**No `config/gate-baselines.json` entries were added.** The draft anticipated needing them to keep
the build green over three pre-existing findings (`IMP-0439`'s shape). With the debt cleared, they
would have baselined nothing — an unclaimable entry that `load_baselines` fails on the day it
expires.

**The check ships as an ERROR, as drafted. No narrowing was required.**

### Gate evidence

- **Known-bad fixture — exit 1**, naming `environments.dev.post_deploy[1]`. Proves it *can* fail.
- **Real corpus — exit 0, `PIPELINE CONFIG PREFLIGHT: PASS`, 104 steps. 0 findings, and 0 is
  correct**: this is now a regression guard for a defect fixed hours earlier, not a clean run over
  a corpus that still contains instances.
- `verify-build-config.py` exit 0 — the gate is already build-wired, so no new
  `suite-gate-is-not-a-step` exposure. `verify-*.py` count **unchanged at 57** (an existing script
  was edited, not a new one added).

### Entries

| Entry | Status | Change |
|---|---|---|
| [`IMP-0601`](../../logs/improvement-log.jsonl#L598) | APPLIED | No rule change; class marker |
| [`IMP-0602`](../../logs/improvement-log.jsonl#L599) | APPLIED | `check_resolved_note_cleared`; its own standing-tracker proposal **withheld** (§5) |
| [`IMP-0603`](../../logs/improvement-log.jsonl#L600) | **stays NEW** | `deferred_reason` + `revisit_when`. Knowledge edit applied; only the closure is deferred (§7) |
| [`IMP-0604`](../../logs/improvement-log.jsonl#L601) | APPLIED | Same gate change; closed at **V4** on the reviewer's 2026-09-05 inspection |
| [`IMP-0605`](../../logs/improvement-log.jsonl#L602) | APPLIED | No new gate; process-discipline note |

`verify-improvement-log.py --check`: **exit 0**, `0 unread, 0 awaiting-approval`. Both blocker
triggers cleared — [`IMP-0605`](../../logs/improvement-log.jsonl#L602)'s halt at build step 3 is
released.
