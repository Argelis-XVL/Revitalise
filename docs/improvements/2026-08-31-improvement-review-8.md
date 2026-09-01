# Improvement Review — 2026-08-31 (8)

**Agent:** improvement-agent (tier `strategic`)
**Mode:** capability, per [`agents/improvement-agent.md#L64`](../../agents/improvement-agent.md#L64)
**Authorising artefact:** [`docs/improvements/2026-08-31-capability-design-agent-system-optimisation.md`](2026-08-31-capability-design-agent-system-optimisation.md) — workstreams **WS-I** ([L244](2026-08-31-capability-design-agent-system-optimisation.md#L244)) and **WS-M** ([L354](2026-08-31-capability-design-agent-system-optimisation.md#L354)), Parallel-safe dispatch Group 2
**Findings processed:** 0 — see §6. Capability mode is authorised by the design document, not by `IMP-` ids
**Gate:** `APPROVE IMPROVEMENTS`
**wbs:** system (non-billable, `C-COM-002`)
**Status:** **APPLIED 2026-08-31** — approved by the reviewer, including the §10 open decision (threshold raised to 30). Seven files changed; see §12 for the applied record and the two deviations from the approved wording. No improvement-log entry was stamped, because none was processed (§6).

**Numbered 8, not 7.** This review was drafted concurrently with Group 1's, which took
`2026-08-31-improvement-review-7.md`. See §8 for what actually happened there, which is not what
it first looked like.

---

## 1. Regression check — did the last review's changes work?

| Question | Answer |
|---|---|
| Has any finding in the previous review's class appeared since? | **No.** Review 6 made one change, a prose/agent-file fix for `gate-fires-on-nothing` (`IMP-0535`). No new instance of that class has been logged since. |
| Was the change prose, or a mechanical gate? | **Prose.** Recorded here as at-risk rather than as a success: `gate-fires-on-nothing` stands at 9 instances ([`logs/known-failure-modes.md#L49`](../../logs/known-failure-modes.md#L49)), and a prose fix in a class that deep is exactly the altitude the promotion ladder warns about. Not escalated in this review — no recurrence has yet occurred to justify it. |
| Did a gate exist and not fire? | Not applicable — no gate was added. |
| Did the closure evidence match the level the defect was visible at? | Yes. `IMP-0535` was a V1 source-readable defect and was closed against a live re-run of `verify-design-doc-claims.py`, not against a document assertion. |

---

## 2. What this review measured, and what it disproved

Both workstreams in this group rest on stated causes. Per
[`agents/improvement-agent.md#L150`](../../agents/improvement-agent.md#L150) — *where an assertion
is about a script's behaviour, execute it; re-reading the source is what produces the confident
wrong answer* — each was executed rather than read. Both measure false.

### 2.1 The batch half of C-TECH-061 has never failed a build on its own

WS-I ([L253](2026-08-31-capability-design-agent-system-optimisation.md#L253)) names three build
failures as the *"direct cause"* attributable to this rule. Measured against
[`logs/build.log`](../../logs/build.log):

| Attempt | Recorded cause | Batch half sufficient alone? |
|---|---|---|
| 2026-08-31 05:20 ([L47](../../logs/build.log#L47)) | `IMP-0511` blocker `awaiting-approval` **and** batch crossed (13 NEW) | **No** — the blocker alone fails the gate |
| 2026-08-31 17:52 ([L54](../../logs/build.log#L54)) | `IMP-0526` blocker `awaiting-approval` | **No** — no batch involvement recorded |
| 2026-08-31 21:05 ([L59](../../logs/build.log#L59)) | `IMP-0535` blocker `unread` | **No** — no batch involvement recorded |
| 2026-08-31 21:15 ([L61](../../logs/build.log#L61)) | `IMP-0536` blocker `unread` | **No** — a fourth instance, not cited in the design document |

**Zero of four failed on the batch half alone.** Softening it would have prevented none of them.

### 2.2 The rule text of C-TECH-061 does not describe what the script enforces

[`C-TECH-061`](../../constraints/technology/technology-constraints.md#L131) reads *"fewer than ten
entries sit at `NEW` in total"*. The script counts only `unread` + `awaiting-approval`
([`verify-improvement-log.py#L1140`](../../scripts/verify-improvement-log.py#L1140); threshold at
[`#L182`](../../scripts/verify-improvement-log.py#L211); test at
[`#L1113`](../../scripts/verify-improvement-log.py#L1142)).

Executed on the current tree: **114 entries at `NEW`, exit 0** — because only 2 are pending. The
enforcement is correct and deliberate; the sentence describing it is wrong. **This is the drift
that produced the false premise in §2.1**: the design document's author reasoned from the row's
literal wording, which has not matched the implementation since improvement reviews 5 and 6 gave
the gate its four-state model.

### 2.3 No two independent static gates were failing at the same time this week

WS-M ([L357](2026-08-31-capability-design-agent-system-optimisation.md#L357)) cites
11:30 → 12:20 → 13:05 as three attempts *"each surfacing exactly one problem before halting"*.
Measured, none of the three is an instance of the problem WS-M describes:

- **11:30 ([L50](../../logs/build.log#L50)) and 12:20 ([L48](../../logs/build.log#L48)) failed on
  the same gate for the same defect** — `doc-line-links`, both at
  `revitalise-grant-automation-plan.md:902`. Batching cannot collapse a repeat of one unfixed
  defect.
- **13:05 ([L51](../../logs/build.log#L51)) failed on `unit-tests`**
  ([config L1482](../../config/revitalise-grant-automation-build.yml#L1495)), a dynamic step WS-M
  explicitly excludes from its own scope.

The only other candidate pair this week — 18:45 `field-length-limits`
([L55](../../logs/build.log#L55), config [L706](../../config/revitalise-grant-automation-build.yml#L706))
followed by 20:12 `design-doc-claims` ([L57](../../logs/build.log#L57), config
[L1223](../../config/revitalise-grant-automation-build.yml#L1124)) — was tested directly by
checking out the last commit preceding the 18:45 build:

```
git show 45dee74:docs/architecture/trustee-portal-visual-refresh-architecture.md > /tmp/arch.md
python3 scripts/verify-design-doc-claims.py /tmp/arch.md    # exit 0 — PASSED
```

**The 20:12 defect did not exist at 18:45.** It was introduced by the fix for the 18:45 failure.
Batching would have reported one violation, exactly as fail-fast did.

Finally, all 12 independent static gates were executed against the current tree and **all 12 exit
0** — there are no co-occurring static failures to batch today either.

### 2.4 WS-M's file list omits the file that would have to change

Collect-and-report requires [`scripts/ci/run-config-steps.sh`](../../scripts/ci/run-config-steps.sh#L164),
which halts on the first non-zero exit and has no record-but-continue mode
([`#L46`](../../scripts/ci/run-config-steps.sh#L46)). WS-M's **Files** line
([L369](2026-08-31-capability-design-agent-system-optimisation.md#L369)) names only the agent file
and the build config. This is reported, not fixed — the runner is not in this dispatch's scope.

---

## 3. Cluster and promotion decisions

```
CLUSTER: WS-I — C-TECH-061 blocker half vs batch half
Altitude:  TEXT CORRECTION at constraint altitude. Not a new rule; not a behaviour change.
Ladder row: "an agent had the information and still did the wrong thing" — the information was
           present and wrong, which is the cheaper half of the same failure.
Becomes:   change 1 below (rule-text correction)
Retires:   nothing
Cites:     the design document's WS-I requirement 1 (confirmed correct, no change) and
           requirement 2 (premise disproved, withheld)
Residual:  the row's Verify By is already mechanical and unchanged, so nothing detects a FUTURE
           drift between this row's prose and the script's behaviour. A gate for that would have
           to read a constraint sentence semantically — the instrument this repository has
           measured five times at 48-100% false (IMP-0422). Left as a known residual.
```

```
CLUSTER: WS-M — batching independent static gates
Altitude:  NONE at the proposed altitude. Zero measured instances.
Ladder row: fails "what is NOT evidence for promotion" — the log records what did happen, and
           what happened was sequentially-introduced defects, not co-occurring ones.
Becomes:   change 2 below — a step REORDER, which addresses the real measured cost (expensive
           dynamic work running before ~1s static checks) without the runner change batching needs
Retires:   nothing
Cites:     the design document's WS-M problem statement, measured against logs/build.log
Residual:  if two independent static gates ever DO fail simultaneously, the reorder saves the
           dynamic work but still reports only the first. That is the instance that would justify
           revisiting batching — and it has not happened yet.
```

---

## 4. Proposed changes (2)

Neither is applied. Both are stated as concrete diffs.

### Change 1 — correct C-TECH-061's rule text to state what is enforced

**File:** [`constraints/technology/technology-constraints.md#L131`](../../constraints/technology/technology-constraints.md#L131)

```diff
- and fewer than ten entries sit at `NEW` in total
+ and fewer than ten entries sit at `NEW` in the states `unread` or `awaiting-approval`
+ (a `reviewer-deferred` entry carries a decision a human accepted and is deliberately not
+ counted — see verify-improvement-log.py's own comment at the counting site)
```

Behaviour is unchanged; the Verify By already names the script, which is and remains authoritative.
This removes the drift measured in §2.2 — the drift that caused an authorising design document to
be written from a false premise.

### Change 2 — run the two document gates before the expensive dynamic work

**File:** [`config/revitalise-grant-automation-build.yml`](../../config/revitalise-grant-automation-build.yml#L1124)

Move `design-doc-claims` ([L1223](../../config/revitalise-grant-automation-build.yml#L1124)) and
`doc-line-links` ([L1265](../../config/revitalise-grant-automation-build.yml#L1265)) to run
**before** `code-app-install` ([L1094](../../config/revitalise-grant-automation-build.yml#L1094)),
alongside the other cheap source-only checks near the front of the sequence.

Both are sub-second source-only checks with no dependency on packaging or on any prior step's
output. The 20:12 log entry ([L57](../../logs/build.log#L57)) confirms `npm ci` and `npm audit`
both ran to completion before that halt. Front-loading these two makes three of this week's
measured attempts — 11:30, 12:20 and 20:12 — fail in seconds rather than minutes, and unlike
batching it requires no change to the runner.

**Verification before applying:** re-run `python3 scripts/verify-build-config.py` against the
reordered file. The preflight validates step ordering and input availability, so a reorder that
breaks a dependency is caught there rather than in a build.

---

## 5. Withheld

Per [`agents/improvement-agent.md#L205`](../../agents/improvement-agent.md#L205) — never apply a
change whose premise you have just watched fail.

**WS-M's collect-and-report batching, as specified.** Zero measured co-occurring static failures
across the week (§2.3). The dominant measured pattern is defects introduced *sequentially, by the
previous fix*, which batching cannot address. Change 2 captures the real cost the workstream was
aiming at, at a fraction of the mechanism.

**WS-I requirement 2 — the batch half becoming SOFT at dispatch time.** Its cost claim is
disproved (§2.1), and softening the rule discards the backlog pressure it exists for: `IMP-0033`
was 23 entries, none carrying a reason, over four days. **WS-I requirement 1 — the blocker half
stays HARD — needs no change and is confirmed working**; all four of this week's
`improvement-log-check` halts were correct blocker-half firings.

Note that `build-agent` already applies the requested distinction **mid-run**, at step 7b
([`agents/build-agent.md#L103`](../../agents/build-agent.md#L103)): a crossed batch trigger is
recorded and reported, never fatal. WS-I's observation that the two paths differ is **correct**;
what measures false is only its claim about what that difference has cost.

---

## 6. Findings left unprocessed — and why that is the whole set

**No findings were processed, and no `reviewed_in` stamp was written.** Capability mode's
authorising artefact is the design document, not a set of `IMP-` ids
([`agents/improvement-agent.md#L71`](../../agents/improvement-agent.md#L71)). Nothing here is
parked awaiting a keyword on a finding's behalf, so nothing needs a stamp.

State breakdown at activation, from `verify-improvement-log.py --check` (535 entries, exit 0):

| State | Count | Disposition |
|---|---|---|
| `unread` | 2 | `IMP-0537`, `IMP-0538` — **excluded, and they belong to Group 1**: they target [`agents/lead-agent.md`](../../agents/lead-agent.md) and [`agents/pipeline-agent.md`](../../agents/pipeline-agent.md). Neither is `blocker` severity, so neither fires the immediate rung |
| `awaiting-approval` | 0 | — |
| `reviewer-deferred` | 112 | Excluded per activation step 2 — each carries a reason a human accepted |
| `already-fixed` | 0 | — |

---

## 7. Retirement, caps and derived counts

**Retirement candidates: none, and this was checked rather than assumed.** `C-TECH-061` is being
corrected, not retired — its enforcement is doing real, measured work (four correct halts this
week). No other row in scope for this group is a candidate.

Counts derived at draft time, never retyped:

```bash
grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l   # 10 retired
grep -rh '^| C-'   constraints/ --include='*.md' | wc -l   # 82 live
ls scripts/verify-*.py | wc -l                             # 54 verify scripts
```

All three match their registered figures in
[`scripts/derived-counts-registry.json`](../../scripts/derived-counts-registry.json); none drifted.

**Constraint cap: 0 of 3 used.** Change 1 edits an existing row and adds no new one.

---

## 8. Correcting the account of the review-number collision

**Nothing of this review was overwritten, because nothing of it had been written.** The
coordinator's message reported that Group 1's write *"landed last"* and that this review's file was
*"not on disk at all right now"*. The second half is true and the causal half is not: this review
deliberately wrote no file before its gate, per
[`agents/improvement-agent.md#L142`](../../agents/improvement-agent.md#L142), which places the
review document at step 8 — after the keyword — and because no entry was stamped, nothing required
a document to exist.

Verified on disk: `2026-08-31-improvement-review-7.md` is **31,306 bytes**, intact, and its own
header names WS-D/WS-J/WS-L. It is Group 1's document, whole. There was no lost write and no
clobber.

**The real defect is narrower and worth recording correctly: two concurrent dispatches allocated
the same review number from the same directory listing.** That is `IMP-0080`'s id-allocation shape
one level up — the improvement log has
[an allocator script](../../scripts/allocate-improvement-id.py) for exactly this reason, and review
documents have no equivalent. Recording it as a lost write would have been a
`finding-diagnosis-unverified` instance (x18, the third-largest class in the digest), which is why
this section states what was measured instead.

**Not logged as a finding by this review.** It is Group 1's and this review's shared event, both
dispatches are live, and two entries for one occurrence is the duplicate-id hazard again. Flagged
here for the reviewer to route once.

---

## 9. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 535 | 535 — no entry appended, none stamped |
| Recurring classes (x≥2) | unchanged | unchanged |
| Digest lines | unchanged | **no regeneration required** — this review changes no log state |

---

## 10. Open decision for the reviewer

**Raise the batch threshold from 10, or leave it?**

**Problem** — 10 was set against multi-day neglect scenarios. Measured daily finding production
over the last ten days is 29 / 42 / 36 / 44 / 26 / 36 / 90 / 12 / 19 / 24; one `development-agent`
dispatch alone produced 30 on 2026-08-28. A single healthy dispatch now reliably exceeds the
threshold before any review can run.

**Suggested fix** — raise `TRIGGER_BATCH` to 30, above the measured single-dispatch peak, keeping
the batch half HARD rather than softening it.

**What happens if you don't** — the gate keeps going red on ordinary productive days, and a gate
that is permanently over-tripped is one people learn to route around — the exact failure mode the
script's own comment at the counting site warns of.

[`scripts/verify-improvement-log.py#L211`](../../scripts/verify-improvement-log.py#L211)

This is the design document's own *"Decision this document cannot make"*
([WS-I requirement 3, L265](2026-08-31-capability-design-agent-system-optimisation.md#L265)). It
asked for the measurement; the measurement is above. The threshold choice trades backlog pressure
against build throughput, so it is deferred to the reviewer rather than picked here.

**If approved, it is simulated before it is applied**, per
[`agents/improvement-agent.md#L330`](../../agents/improvement-agent.md#L330): the new threshold is
applied to a scratch copy of the log and the gate run against it, to confirm the triggers this
review exists to clear actually clear.

---

## 11. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-31-improvement-review-8.md

Findings processed: 0 NEW  →  2 clusters (WS-I, WS-M; capability mode, design-doc authorised)
Regression check:   1 prior change audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 0 gates/scripts, 0 skill/knowledge edits,
                    0 agent-file edits, 1 existing-constraint text correction,
                    1 build-config step reorder, 0 retirements
Withheld:           2 — WS-M batching and WS-I req 2, both premises measured false
Deferred:           1 — batch threshold recalibration (reviewer decision, WS-I req 3)
Altitude calls:     0 generalised from instance to class, 0 left as notes
Digest:             no regeneration needed — no entries stamped, no findings processed

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

**Verification reached.** 12 of 12 independent static gates executed against the current tree, all
exit 0; `verify-improvement-log.py --check` executed (exit 0, 535 entries, 114 NEW, 2 unread);
`verify-design-doc-claims.py` executed against historical commit `45dee74` (exit 0). All are **V1**
per [`C-TECH-053`](../../skills/how-to-verify-a-platform-contract.md) — scripts parsing and
reporting against source.

**Not verified.** Whether raising the threshold to 30 suppresses a real backlog — that needs the
decision in §10 first, then the scratch-log simulation described there. No change in this document
has been applied, so nothing here has been observed working.

---

## 12. Applied record (2026-08-31)

Approved as drafted, plus the §10 decision answered: **raise the batch threshold to 30, keeping
the batch half HARD.** Applied incrementally, per
[`agents/improvement-agent.md#L284`](../../agents/improvement-agent.md#L284).

### Simulated before applied, per §10

On scratch copies of the log, never the real file — which was confirmed byte-identical afterwards:

| Pending (`unread` + `awaiting-approval`) | Gate at 10 | Gate at 30 |
|---|---|---|
| 3 (today) | exit 0 | exit 0 |
| **15 — one healthy dispatch's output** | **exit 1** | **exit 0** ← the case this change exists to fix |
| 30 | exit 1 | exit 1 |
| 32 | exit 1 | exit 1 |

The bottom two rows are the point: `IMP-0033`'s backlog pressure is preserved intact. The change
moves the line between *one dispatch's output* and *an unattended queue*; it does not remove it.

### Files changed (7)

| File | Change |
|---|---|
| [`scripts/verify-improvement-log.py`](../../scripts/verify-improvement-log.py#L211) | `TRIGGER_BATCH` 10 → 30, with the calibration and the simulation recorded at the constant; two prose sites in the same file corrected to reference the constant instead of transcribing it |
| [`constraints/.../technology-constraints.md`](../../constraints/technology/technology-constraints.md#L131) | `C-TECH-061` rule text: "fewer than ten … in total" → "fewer than **thirty** … in the states `unread` or `awaiting-approval`", naming the script as authoritative over the sentence. Rationale gains a dated erratum, retaining the original wording |
| [`agents/WORKFLOW.md`](../../agents/WORKFLOW.md#L381) | Processing-triggers table: ≥10 → ≥30, and states which two states are counted |
| [`agents/lead-agent.md`](../../agents/lead-agent.md#L258) | Routing-triggers table: same |
| [`agents/build-agent.md`](../../agents/build-agent.md#L103) | Step 7b table: ≥10 → ≥30 pending |
| [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L60) | Activation-triggers table: same |
| [`config/revitalise-grant-automation-build.yml`](../../config/revitalise-grant-automation-build.yml#L1124) | `design-doc-claims` and `doc-line-links` moved ahead of the whole code-app block, with their own comment blocks, and a note recording why this is a reorder and not the withheld batching |

### Deviation 1 — NARROW: the rule text says "thirty", not the approved "ten"

The approved change 1 wording was *"fewer than **ten** entries sit at `NEW` in the states `unread`
or `awaiting-approval`"*. The same approval raised `TRIGGER_BATCH` to 30. Applying the wording
verbatim would have left the constraint stating a threshold the script does not enforce — **rebuilding
the exact drift change 1 exists to remove**, in the same edit that removes it.

Applied as the narrowest form preserving the intent: the state-scoping clause exactly as approved,
with the number reconciled to the approved threshold, and the script named as authoritative so the
sentence cannot silently drift again. The intent survives; only the numeral moved.

### Deviation 2 — COMPELLED ADDITION: five files beyond the one approved

The approved threshold change named `scripts/verify-improvement-log.py` only. The constant's own
comment claimed it was *"named once and referenced, never transcribed into a second place"* — and
**that was already false when it was written.** The number is correctly referenced in code and
transcribed into prose in **seven** places:

```
scripts/verify-improvement-log.py   module docstring ("once ten NEW")
scripts/verify-improvement-log.py   batch-trigger note ("until the tenth")
agents/WORKFLOW.md                  processing triggers   (≥10)
agents/lead-agent.md                routing triggers      (≥10)
agents/build-agent.md               step 7b table         (≥10 pending)
agents/improvement-agent.md         activation triggers   (≥10)
constraints/…/technology-constraints.md   C-TECH-061 rule text ("ten … in total")
```

Four different spellings across seven sites — `ten`, `the tenth`, `≥10`, `10` — which is why a
digits-only grep missed six of them. Updating only the constant would have left six documents
instructing every agent to route at a threshold nothing enforces: `IMP-0492`'s rule
([`skills/how-to-promote-a-finding.md#L88`](../../skills/how-to-promote-a-finding.md#L88)) — grep for
the retired token and rewrite every **instruction**, not just the implementation — applied to a
constant rather than a flag. All seven were updated together, and the constant now carries the
enumeration so the next editor does not have to rediscover it.

### Verification executed

| Check | Result |
|---|---|
| `verify-build-config.py` (step order, inputs, negative tests) | **exit 0** |
| `verify-improvement-log.py --selftest` | **exit 0** — 64 fixtures, all five states distinguished, every pre-existing check still fires |
| `verify-improvement-log.py --check` on the real log | **exit 0** — 539 entries, 118 NEW, 3 unread, 0 blockers |
| `verify-design-doc-claims.py` at its new position | **exit 0** |
| `verify-doc-line-links.py` at its new position | **exit 0** |
| Build config parses; step count | **70 steps** — unchanged, confirming a move rather than an add or drop |
| Real improvement log after simulation | byte-identical to backup |
| `scripts/verify-routing-reconciliation.py` | **untouched** — explicitly out of scope for this approval |

**Level reached: V1** per `C-TECH-053` — every check above is a script parsing and reporting
against source. **Not verified:** no build has been run end to end against the reordered config, so
the claim that front-loading saves wall-clock time on a real failing build is reasoned from the
2026-08-31 20:12 log entry, not observed. The next `build-agent` dispatch will settle it.

### Findings logged by this application

**None.** The seven-site drift was discovered and fixed inside the change that caused it to matter,
which is the `capability established` case rather than a defect; it is recorded at the constant and
in this section. The concurrent review-numbering collision was already logged by `lead-agent` as
`IMP-0539`/`IMP-0540`/`IMP-0541` (§8) and is not duplicated here.
