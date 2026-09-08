# Improvement Review — 2026-09-07 (2)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 3 `NEW` → 1 cluster
**Trigger:** blocker escalation — [IMP-0641](../../logs/improvement-log.jsonl#L638), `blocker`/`unread`, blocking the `revitalise-grant-automation` build at its [`improvement-log-check`](../../config/revitalise-grant-automation-build.yml#L62) step
**WBS:** 3.2, 3.3, 3.4 (phase-1 two-import workaround)
**Gate:** `APPROVE IMPROVEMENTS`

---

## 0. The one thing to read first

**The delivery fix is real, it is on disk, and I re-verified it by execution rather than by reading it. One rule change is proposed, and it is NOT the one the finding asked for.**

[IMP-0643](../../logs/improvement-log.jsonl#L640) proposes its new step on [`agents/build-agent.md`](../../agents/build-agent.md#L18). That is the wrong file: build-agent's role is *"No code changes"*, and on a red gate it *"emit[s] `BLOCKED` and hand[s] back to development-agent"* ([L152](../../agents/build-agent.md#L152)). The step describes an action — wiring a gate to a baseline — that build-agent structurally never performs, so the rule would sit in the one agent file where it can never fire. I am proposing it on [`agents/development-agent.md`](../../agents/development-agent.md#L372) instead, as a sibling of the subsection the previous review added there. **The intent is applied in full; only the target moved**, and the reasoning is in §3.

**On the reviewer's request to confirm `--check` exits 0: it exits 1 now, by design, and exits 0 the moment the keyword lands.** The blocker rung passes only on *"zero `NEW` entries of severity `blocker` in state `unread` **or** `awaiting-approval`"* ([verify-improvement-log.py#L124](../../scripts/verify-improvement-log.py#L124)), and a stamped-but-unapproved entry is `awaiting-approval`. I simulated both dispositions rather than reasoning about it — §6. I have not claimed a green queue anywhere in this document.

---

## 1. Verification of the delivery fix — executed, not read

[IMP-0642](../../logs/improvement-log.jsonl#L639) claims it made three Pester assertions baseline-aware. I re-ran both commands myself:

| Command | Result |
|---|---|
| `pwsh -NoProfile -Command "Invoke-Pester -Path src/tests/provisioning/EnsureSchema.Tests.ps1"` | **45 passed, 0 failed** (30.2s) |
| `python3 scripts/run-source-gates.py config/revitalise-grant-automation-build.yml` | **13 of 13 PASS**, including `field-security-coverage` |

Both figures match the claim exactly. The fix is at [EnsureSchema.Tests.ps1#L146-L161](../../src/tests/provisioning/EnsureSchema.Tests.ps1#L146), reading [config/gate-baselines.json](../../config/gate-baselines.json#L84) at test time and subtracting every current, non-expired `field-security-coverage` entry from the `Entity.xml`-derived declared count. The three consuming assertions are at [L479](../../src/tests/provisioning/EnsureSchema.Tests.ps1#L479), [L901](../../src/tests/provisioning/EnsureSchema.Tests.ps1#L901) and [L1105](../../src/tests/provisioning/EnsureSchema.Tests.ps1#L1105).

**Three things I checked beyond the claim, because a passing suite does not distinguish a generalised fix from a hardcoded 68.**

1. **It is genuinely generalised.** The count is `declared − count(current baseline entries)` ([L161](../../src/tests/provisioning/EnsureSchema.Tests.ps1#L161)), keyed on no column name. Any future entry for this gate is handled with no further edit, and an empty baseline set collapses the released count back to the declared count by construction.
2. **The declared-count assertion was retained, not replaced.** [L477](../../src/tests/provisioning/EnsureSchema.Tests.ps1#L477) still asserts the `Entity.xml` count of 69; only the *released* count is baseline-adjusted. So the fix did not weaken the invariant — it split one assertion into two that are each true, which is more than [IMP-0641](../../logs/improvement-log.jsonl#L638)'s own `proposed_change` asked for.
3. **It expires.** The filter requires `expires >= today` ([L156](../../src/tests/provisioning/EnsureSchema.Tests.ps1#L156)), so after the entry's 2026-09-14 date the released count returns to 69 and these assertions go red again rather than suppressing quietly. That matches `gate_baseline.py`'s own fail-on-expired semantics.

---

## 2. Regression check — did the last review's change work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [agents/development-agent.md#L372](../../agents/development-agent.md#L372) — *"Fixing what a finding describes does NOT close that finding"* ([IMP-0640](../../logs/improvement-log.jsonl#L637)) | 2026-09-07 (review 1) | `learning-substrate-destroyed` | **NO** | **Partially proven — see below** |
| [`improvement-log-check`](../../config/revitalise-grant-automation-build.yml#L62) build step ([IMP-0285](../../logs/improvement-log.jsonl#L282)'s class fix) | 2026-08-24 (review 26) | `learning-substrate-destroyed` | NO new instance | The gate fired correctly again |

**The prose change from review 1 worked in part, and the part that worked is the part that matters here.** Its step 1 asks a fixing dispatch to stamp `corrects` on its own entry: [IMP-0642](../../logs/improvement-log.jsonl#L639) carries `corrects: IMP-0641`, where [IMP-0639](../../logs/improvement-log.jsonl#L636) — the same situation one dispatch earlier — carried nothing, and that omission is what produced [IMP-0640](../../logs/improvement-log.jsonl#L637). Its step 3 asks the dispatch to route the unclosed entry to improvement-agent rather than deferring it itself: that routing is why this review exists.

**Be careful about how much credit that deserves.** [IMP-0642](../../logs/improvement-log.jsonl#L639) is timestamped `03:00` and review 1 was applied around midday, so the `corrects` stamp cannot have been *caused* by the rule — the timestamps rule out causation. What I can say is the weaker, honest thing: **the class did not recur, and the behaviour the rule requires was present this time.** One clean instance is not proof a prose change works; it is the absence of a counter-example.

**Classes recurring after a prose fix:** none. **Classes recurring after a gate:** none — and the `improvement-log-check` gate fired again at step 3, in about a second, exactly as designed. No `gate-cannot-fail` finding is logged; logging one would be false.

**Closure-level audit.** [IMP-0641](../../logs/improvement-log.jsonl#L638) is `observable_at` **V1** and so needs no `reobserved` under [REOBSERVATION_LEVELS](../../scripts/verify-improvement-log.py#L380). I am recording one anyway, at **V2**, because I actually ran the reproduction (the Pester file that was red) rather than inspecting source — a stronger closure than the schema demands. [IMP-0643](../../logs/improvement-log.jsonl#L640) is `observable_at: n/a` (a process finding) and closes on source state.

---

## 3. The cluster, and the altitude call

```
CLUSTER: hard-gate-has-no-scoped-override-path  (x3 on this feature: IMP-0638/0639, IMP-0641/0642, IMP-0643)
Altitude:  CLASS — third instance of one shape: a scoped exception recorded in ONE encoding
           of an invariant, while a sibling encoding of the same invariant knows nothing of it
Ladder row: "An agent had the information and still did the wrong thing" → an agent-file edit
Becomes:   agents/development-agent.md — a new subsection requiring a sibling-encoding grep
           in the same dispatch that wires a gate to scripts/lib/gate_baseline.py
Retires:   nothing — see §5
Cites:     IMP-0638, IMP-0639, IMP-0641, IMP-0642, IMP-0643
Residual:  Whether two checks encode the SAME invariant is a semantic judgement. The grep finds
           candidates; a human or agent still adjudicates each. Named in the rule text itself.
```

### Why this is not a gate — measured, not assumed

Before proposing prose I measured the mechanical candidate, because the ladder says a script beats a paragraph. The candidate: for each `matches` token in [config/gate-baselines.json](../../config/gate-baselines.json), grep `scripts/` and `src/tests/` for other files naming that token, and flag any that are not baseline-aware.

Run against the real corpus of **8 baseline entries**, it returns **2 findings, of which 1 is a false positive**:

| Baseline entry | Files naming the token | Adjudication |
|---|---|---|
| `provisioning/dataverse/verify-environment-access.ps1` | `scripts/verify-provisioning-report.py`, `scripts/verify-pipeline-config.py` | **FALSE POSITIVE** — both name the script for unrelated reasons (a pipeline step, a report), neither encodes its invariant |
| `rev_grant.rev_escalatedon` | `src/tests/provisioning/EnsureSchema.Tests.ps1` | TRUE — and already fixed by [IMP-0642](../../logs/improvement-log.jsonl#L639) |
| the other 6 entries | none | 0 findings |

**And 3 of the 8 entries cannot be checked this way at all:** `status:error`, `status-unproduced:threshold-unset` and `environments.prd.environment_prerequisites[0]` are not source identifiers, so there is no token to grep for. So the gate would ship at **50% false on the entries it can read, blind to 38% of the corpus, and with its only true positive already closed** — which is this repository's five-times-measured prose-gate shape ([IMP-0422](../../logs/improvement-log.jsonl), [IMP-0428](../../logs/improvement-log.jsonl)) arriving from a new direction. A design measured like that is redesigned or dropped, not shipped with an exemption. **Dropped**, and the measurement goes in the rule text so the next agent does not re-propose it.

### Why development-agent.md and not build-agent.md

[IMP-0643](../../logs/improvement-log.jsonl#L640) argues for build-agent on the ground that build-agent *"has now discovered this gap three times by hitting the red sibling at build time."* That is an argument about **detection**, and detection was never the gap — build-agent detected it correctly all three times and reported it. The gap is in the dispatch that **wires** the gate, and that is development-agent in both instances ([IMP-0639](../../logs/improvement-log.jsonl#L636) and [IMP-0642](../../logs/improvement-log.jsonl#L639) are both development-agent entries). Placing a "when you wire a gate, also grep" instruction on an agent whose role forbids code changes would create a rule that cannot fire — the `gate-cannot-fail` class in prose form, which is the single most recurrent class in this repository at 44 instances.

---

## 4. The change, as a concrete diff

**One change. Nothing is applied yet.**

**Target:** [`agents/development-agent.md`](../../agents/development-agent.md#L372), inserted after the existing subsection that ends at [L400](../../agents/development-agent.md#L400) and before `## Contracted scope`.

````markdown
### Wiring ONE gate to a baseline does not cover the invariant — grep for the siblings

When you wire a gate to `scripts/lib/gate_baseline.py`, or add an entry to
`config/gate-baselines.json`, the exception you just recorded is scoped to **one encoding** of
the invariant. This repository routinely encodes one invariant more than once — a
`scripts/verify-*.py` build gate and a Pester assertion under `src/tests/` reading the same
source files — and the encodings do not know about each other.

So, in the same dispatch, before you report the baseline as handled:

```bash
# every OTHER check that reads the same source files as the gate you just wired
grep -rln '<the source file the gate reads>' scripts/ src/tests/
```

Read each hit and decide whether it asserts the same invariant. Then either give it the same
baseline-awareness in this dispatch, or **name it in your gate output as checked and not
applicable**. Silence is what costs: nothing compares two encodings of one rule.

`IMP-0638` → `IMP-0639` wired `scripts/verify-field-security-coverage.py` and stopped there.
`src/tests/provisioning/EnsureSchema.Tests.ps1` asserted *"every `IsSecured` column has exactly
one `FieldPermission`"* three more times over the same
`Entity.xml`/`FieldSecurityProfiles.xml` pair, went red at build step 68 of 73, and cost a
second dispatch (`IMP-0641` → `IMP-0642`). One grep at `IMP-0639` time would have found it —
the sibling names the baselined column literally.

**No gate enforces this, and the reason is measured rather than assumed.** Keying a gate on each
baseline entry's `matches` token and grepping for other files that name it returns 2 findings
across the 8 current entries: 1 false positive (`verify-environment-access.ps1`, named by
`verify-provisioning-report.py` and `verify-pipeline-config.py` for unrelated reasons) and 1 true
positive that is already fixed. Three of the eight entries have a `matches` value that is not a
source identifier at all (`status:error`, `status-unproduced:threshold-unset`,
`environments.prd.environment_prerequisites[0]`), so the grep cannot be attempted for them.
Whether two checks encode the same invariant is a semantic judgement — hence a checklist step,
not a script. Do not re-propose the token gate without re-measuring it (`IMP-0643`).
````

**No change to [`agents/build-agent.md`](../../agents/build-agent.md#L18)**, deliberately, per §3.

---

## 5. Anti-bloat

| Limit | This review |
|---|---|
| Max 3 new constraints | **0 proposed** — the cluster's altitude is an agent file, not a constraint row |
| Every new constraint cites `IMP-` ids | n/a — none added |
| Retirement considered | **Checked, none found.** Nothing here is superseded: `C-TECH-061` is the rule that caught the unclosed blocker and is working; the six-entry baseline mechanism gained a seventh gate rather than replacing anything. Derived counts unchanged: 85 live constraint rows, 10 retired (`grep -rh '^\| ~~C-' constraints/`), 57 `scripts/verify-*.py` |
| New scripts | **0** — so no `--selftest`, no corpus run, and no `verify-build-config.py` wiring is owed. The one mechanical candidate was measured and dropped (§3) |

---

## 6. Simulation of the disposition — run, not reasoned

Per `agents/improvement-agent.md`, I applied this review's proposed dispositions to a **scratch copy** of the log and ran the gate against it, then confirmed the real file byte-identical.

| Simulated disposition | Gate exit |
|---|---|
| This draft parked — `reviewed_in` stamped, `status` still `NEW` | **1** — trigger reads *"1 NEW entry of severity `blocker` in state `awaiting-approval`"* and names this document |
| Full closure, first attempt — `APPLIED` + `applied_by` + `reobserved`, `evidence_grep` on one entry only | **1** — see the correction below |
| Full closure, corrected — `evidence_grep` on **both** entries, with the §4 change applied | **0**, clean: no errors, no triggers, no warnings |

The last row is the answer to *"confirm it exits 0"*: the disposition this review proposes does clear the gate, and the keyword is what moves it. The real log was byte-identical before and after every run (`sha256 6770d3e7…`), confirmed by checksum rather than by intention.

**The simulation caught a defect in this review's own plan, which is the reason the step exists.** I had written that `evidence_grep` is opt-in and could therefore be omitted for [IMP-0643](../../logs/improvement-log.jsonl#L640) until the change landed. **That is wrong**, and the withdrawn wording is retained here deliberately: the field is opt-in only for entries that predate improvement review 8, and any entry moved to `APPLIED` after 2026-08-21 without one fires `TRIGGER: 1 entry(ies) moved to APPLIED … with no 'evidence_grep'`. Reading the validator's source is what produced the wrong answer; running it produced the right one.

**Consequence for the apply order, and it is now load-bearing:** the §4 edit must land **before** [IMP-0643](../../logs/improvement-log.jsonl#L640) is closed, because its `evidence_grep` needle is the new subsection heading and an `APPLIED` entry whose needle is absent is an error. Applied in the other order, the closure fails. The third row above was produced against a scratch repository root with the §4 change applied, so it is a test of the real post-apply state and not of a hoped-for one.

---

## 7. Scope — what this review did NOT process, and why

The queue holds **15 other `unread` entries**. None is `blocker` severity, so none triggers the immediate rung, and an unread blocker must not pull a review of everything around it (`IMP-0183` — a one-finding dispatch that became a pass over twenty-three settled entries). Each is stamped `excluded_by` naming this document, so this disclosure does not generate a citation warning per id (`IMP-0557`).

| Excluded | Severity | Status |
|---|---|---|
| `IMP-0611`, `IMP-0612`, `IMP-0613`, `IMP-0614`, `IMP-0615`, `IMP-0617`, `IMP-0618`, `IMP-0620`, `IMP-0625`, `IMP-0626`, `IMP-0631`, `IMP-0632` | friction / rework | **Already analysed** by [2026-09-06-improvement-review-3.md](2026-09-06-improvement-review-3.md), which never stamped `reviewed_in`. They need that document's keyword, **not a second analysis** |
| `IMP-0635`, `IMP-0636`, `IMP-0637` | friction / rework | Genuinely unread and uncited. Left for the next batch review |

**One item routed, and I am reporting it rather than dispatching it:** [2026-09-06-improvement-review-3.md](2026-09-06-improvement-review-3.md) is parked at its gate with 12 entries analysed and unstamped. Sending `APPROVE IMPROVEMENTS` against *that* document is what clears them; nothing in this review touches them.

### Four SOFT count drifts, measured here and routed — not fixed

[`verify-derived-counts.py`](../../scripts/verify-derived-counts.py) is **SOFT** and currently reports 4 drifted claims and 1 registry defect. I re-measured all five rather than passing on the gate's word, and **none is caused by this review**. Two are squarely in this cluster's subject area, which is why they are named here instead of left in a log nobody reads:

| Drifted claim | Measured | Owner |
|---|---|---|
| `dev-summary-secured-column-count` ×2 — *"67, not 68 or more"* and *"source is **67** today"* | prose 67, source **68** | development-agent — and the file has 836 uncommitted insertions, so this is **in-flight work**, not stale debt |
| `rev-trustee-role-header-secured-column-count` — *"51 secured columns"* | prose 51, source **52** | delivery; committed and genuinely stale |
| `known-failure-modes-digest-line-count` — *"the digest is 651 lines"* | 651 vs **652** | this loop's own generator; drifted when the digest regenerated |
| `pipeline-rev-setting-row-count` (registry defect) | three settings files disagree with each other (18/16/16) | development-agent |

**Not fixed, and the reason is scope rather than effort.** The two dev-summary figures sit in an artefact a concurrent dispatch is actively rewriting, and the secured-column count is the very number that dispatch is changing — correcting it from here would collide with work in flight (`C-COM-002`). The other three are one-line corrections in files this review does not own. **No new finding is logged for them:** the gate already reports all five by name on every run, and a finding restating a live gate's output is duplicate bookkeeping, not learning.

---

## 8. Applied record

**Status: ~~DRAFT — awaiting `APPROVE IMPROVEMENTS`. Nothing in §4 is on disk.~~ → APPLIED 2026-09-07**, on `APPROVE IMPROVEMENTS` sent by Xander Lykopoulos in his own message against this document. The superseded header is struck through rather than deleted, per the correction convention.

**What is on disk now:**

| Change | Landed | Verified by |
|---|---|---|
| §4 subsection → [`agents/development-agent.md`](../../agents/development-agent.md#L402) | L402, ahead of `## Contracted scope` at [L437](../../agents/development-agent.md#L437); file 481 → 509 lines | needle present exactly once; anchor still unique |
| [IMP-0641](../../logs/improvement-log.jsonl#L638) → `APPLIED` | `applied_by`, `reobserved` (V2), `evidence_grep` | validator exit 0 |
| [IMP-0643](../../logs/improvement-log.jsonl#L640) → `APPLIED` | `applied_by` recording the re-targeting, `evidence_grep` | validator exit 0 |
| Digest regenerated | 640 entries, 635 lessons; appendix 1,137 lines | `--check` exit 0 |

**`python3 scripts/verify-improvement-log.py --check` exits 0.** Census: 152 `NEW` — 15 `unread`, 1 `awaiting-approval`, 136 `reviewer-deferred`, 0 `already-fixed`, 0 `approved-not-applied`. No blocker trigger, no batch trigger, no errors.

**Re-verification performed after the keyword and before applying** (step 8): the log was still at 640 entries with max id `IMP-0643`, nothing new carried `corrects` against either entry, no new finding shared the cluster's class, the Pester suite re-ran at 45/45 and the source gates at 13/13, and the corpus measurement in §3 re-measured identically (8 entries, 2 with hits, 1 false positive, 3 non-source matches). Nothing in the draft was disproved, so nothing was withheld.

### Two findings this review logged against itself

Both are `friction`, both `awaiting-approval`, and neither is a defect in anything this review shipped — they are two places where **this loop's own instructions gave a shape without giving an obligation**, and both were caught by running something rather than reading it.

**[IMP-0644](../../logs/improvement-log.jsonl#L641) — the closure-field requirement is invisible until the validator runs.** This document's own draft asserted `evidence_grep` was optional; the pre-park simulation returned exit 1 and disproved it. [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L267) supplies both closure fields' JSON shapes but never states that `evidence_grep` is mandatory on anything closed after 2026-08-21, and the validator's own docstring calls the mechanism *"deliberately OPT-IN in both directions"* — true of the ~130 pre-cutoff entries, false of every entry closed today. **This is the second instance of [IMP-0572](../../logs/improvement-log.jsonl)'s shape on the same two fields**, which is why it proposes the same file rather than a gate: the validator already enforces it correctly and its message is precise, so the gap is write-time discoverability, and that now has two recorded instances.

**[IMP-0645](../../logs/improvement-log.jsonl#L642) — citing a closed finding re-opens a warning on its corrector.** §3 cites `IMP-0638`, closed days ago. That citation made this document the newest review to process it, which re-fired the `corrects` rung against `IMP-0639` even though nothing about the settled pair had changed. The discharge is a **list-valued** `reviewed_in`, which is supported and documented nowhere; the warning's own text says *"stamp IMP-nnnn"*, which reads as a scalar overwrite. I made exactly that mistake first — added a second `reviewed_in` key to the same JSON line, which parses to the last occurrence and **silently discarded the edit**. It was caught only by counting the key, not by any gate, and the proposed change is to the warning's wording rather than to its logic.

**Digest after regeneration:** 642 entries, 637 lessons. `declared-policy-not-mechanically-enforced` is now x28 and `gate-fires-on-nothing` x12.

### The original plan, kept for the record

Stamped at draft time (step 6 bookkeeping only — `status` unmoved, no `applied_by`):

| Entry | Field stamped |
|---|---|
| [IMP-0641](../../logs/improvement-log.jsonl#L638) | `reviewed_in` → this document |
| [IMP-0642](../../logs/improvement-log.jsonl#L639) | `reviewed_in` → this document (needed for the `corrects` warning on `IMP-0641` to self-clear) |
| [IMP-0643](../../logs/improvement-log.jsonl#L640) | `reviewed_in` → this document |
| [IMP-0639](../../logs/improvement-log.jsonl#L636) | `reviewed_in` → **list**, adding this document beside review 1 |
| 15 entries in §7 | `excluded_by` → this document |

**Why `IMP-0639` needed a stamp it did not obviously need**, since it was already closed by review 1: this review's §3 cluster block cites `IMP-0638` as processed, which made this document the *newest* review to process it, and the `corrects` rung then re-fired on `IMP-0639` because its own stamp named only the older review. Adding this document to the list cleared it. Total footprint: **19 entries touched, 0 statuses moved** — verified by querying the log for this document's own filename rather than by counting my edits.

On approval, **in this order** — step 1 before step 3, per §6:

1. Apply §4 to [`agents/development-agent.md`](../../agents/development-agent.md#L372).
2. Close [IMP-0641](../../logs/improvement-log.jsonl#L638) → `APPLIED`, `applied_by` naming the delivery fix and this rule change, `reobserved` at V2, `evidence_grep` on `ExpectedReleasedSecuredColumnCount`.
3. Close [IMP-0643](../../logs/improvement-log.jsonl#L640) → `APPLIED`, `applied_by` recording the **re-targeting from build-agent.md to development-agent.md** and the corpus measurement that dropped the gate, `evidence_grep` on the new subsection heading (**required, not optional** — §6).
4. Regenerate the digest, then re-run `verify-improvement-log.py --check` and report the exit code.

Bookkeeping moves incrementally: each entry closes as its change lands, and the digest regenerates once, last.

**Verification reached: V1 for the rule change (a markdown edit executes nothing) and V2 for the delivery fix it describes** (45 of 45 Pester assertions, 13 of 13 source gates, both executed here). **Not verified:** that the phase-2 dispatch will actually delete the baseline entry by its 2026-09-14 expiry — that is a live delivery step owned by development-agent, and after that date these assertions go red by design rather than silently passing.
