# Improvement Review 10 — 2026-09-01 (capability mode, Group 7: WS-B)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 0 pre-existing `NEW` → 3 clusters (capability mode: the authorising
artefact is a design document, not a set of `IMP-` ids). 3 findings were *logged* by this review
from its own measurements — [IMP-0543](logs/improvement-log.jsonl#L540),
[IMP-0544](logs/improvement-log.jsonl#L541), [IMP-0545](logs/improvement-log.jsonl#L542).
**Trigger:** reviewer request via lead-agent — capability mode, Group 7
**Authorising document:** [WS-B](docs/improvements/2026-08-31-capability-design-agent-system-optimisation.md#L60)
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** APPLIED 2026-09-01 — see section 8.

---

## 0. Headline — WS-B's premise and its recommended default both measure false

Two clauses of [WS-B](docs/improvements/2026-08-31-capability-design-agent-system-optimisation.md#L63)
were checked against the tree before anything was designed, and neither holds:

| WS-B says | Measured, 2026-09-01 |
|---|---|
| "572 lines / 110KB at 430 entries … **with no compaction**" | Size confirmed and now larger (612 lines / 119,475 bytes at 542 entries). **Compaction exists and binds**: [`MAX_PER_SECTION = 20`](scripts/generate-known-failure-modes.py#L83) hides **362 of 537** lessons (67%) in 6 of the 10 populated sections |
| "Recommend starting conservative (e.g. entries older than **60 days** AND already `APPLIED` AND not part of a recurring class)" | Selects **0 of 537** lessons. The entire log spans 2026-08-12 → 2026-08-31 — **20 days**. Nothing in it is older than 60 days, and nothing will be until 2026-10-11 |

**So the recommended default is not conservative, it is inert**, and I am not adopting it. Had it
been implemented as written it would have shipped as "implemented, measured no size reduction" and
read as evidence that compaction does not help. This is logged as
[IMP-0544](logs/improvement-log.jsonl#L541).

**The real defect the measurement found is not volume — it is selection.** The cap already does
the collapsing WS-B asks for. It collapses the wrong 362.

---

## 1. Regression check — did the last review's changes work?

The prior change in this file's own lineage is
[IMP-0383](docs/improvements/2026-08-27-improvement-review.md), applied as `_capped_index()`
([L605](scripts/generate-known-failure-modes.py#L605)) — the capped-lesson note regrouped from a
flat id run into an index by `class_instance_of`, plus the `--subject` flag.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| `_capped_index()` grouped by class + `--subject TERM` ([L605](scripts/generate-known-failure-modes.py#L605), [L710](scripts/generate-known-failure-modes.py#L710)) | 2026-08-27 | `digest-cap-hides-a-whole-subject-area` | **YES — [IMP-0543](logs/improvement-log.jsonl#L540)** | **Wrong altitude.** It made the hidden lessons *findable*; it never touched *which* lessons are hidden |
| `corrections_of()` ⚠ CORRECTED markers ([L385](scripts/generate-known-failure-modes.py#L385)) | 2026-08-26 | `two-recorded-lessons-contradict-each-other` | NO further instance in the generator | Working — leave alone |
| `contests_of()` ⚠ CONTESTED markers ([L442](scripts/generate-known-failure-modes.py#L442)) | 2026-08-28 | same | [IMP-0478](logs/improvement-log.jsonl) — the edge was set *wrongly* on first use, not absent | Working as a mechanism; the defect was authoring, not the gate |
| `structural_errors()` — refuse to generate over an invalid log ([L282](scripts/generate-known-failure-modes.py#L282)) | 2026-08-28 | `gate-cannot-fail` | NO | Working. Verified: `--check` exits 0 today |

**Recurred after a non-mechanical fix:** `digest-cap-hides-a-whole-subject-area`, second instance.
Per [the altitude rule](skills/how-to-promote-a-finding.md), the second instance may not get
another instance-level patch. Change 1 below is the generalisation: it fixes the *ranking
function*, not the *index of what the ranking function excluded*.

**A note on the previous review's gate-block arithmetic.**
[IMP-0529](logs/improvement-log.jsonl) and [IMP-0534](logs/improvement-log.jsonl) record two
consecutive reviews hand-typing this document's own "N lessons, N recurring classes" figures
wrongly. Section 7's figures below are derived by script, not typed.

---

## 2. Clusters and promotion decisions

```
CLUSTER: digest-cap-hides-a-whole-subject-area  (x2: IMP-0383, IMP-0543)
Altitude:   CLASS — second instance; the first fix indexed the symptom
Ladder row: "a second instance may not get another instance patch — generalise it"
Becomes:    Change 1 — sort_key's tail moves from ascending id to
            (NEW before APPLIED, then id DESCENDING)
Retires:    nothing. _capped_index() and --subject stay; they are the safety net that
            makes any cap tolerable, and Change 3 extends rather than replaces them
Cites:      IMP-0383, IMP-0543
Residual:   67% of lessons are still not rendered. This change decides WHICH 175 render,
            not HOW MANY. Rendering all 537 is not on the table — see section 3's
            rejected options.
```

```
CLUSTER: instrument-exists-never-used  (IMP-0545)
Altitude:   INSTANCE — one occurrence, and the remedy is one print statement
Ladder row: instance-level, made visible rather than gated
Becomes:    Change 4's merge-count line on stdout
Retires:    nothing — see section 4 for why the inert key is NOT retired
Cites:      IMP-0545
Residual:   nothing makes the key work; it makes its inertness visible at every run.
            A semantic dedup key is a design change, not a defect fix.
```

```
CLUSTER: finding-diagnosis-unverified  (IMP-0544)
Altitude:   INSTANCE — the corrective action is this review reporting the measurement
Ladder row: instance; the general form already exists as improvement-agent step 8
Becomes:    NOTE ONLY in this dispatch. The proposed_change targets
            agents/improvement-agent.md, which belongs to Group 6 (WS-H + WS-F) and is
            outside this Group 7 dispatch's file ownership
Cites:      IMP-0544
Residual:   deferred to Group 6 — see section 5
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | [`scripts/generate-known-failure-modes.py`](scripts/generate-known-failure-modes.py#L525) | `sort_key`'s tail changes from `fs[0]["id"]` ascending to `(0 if any NEW else 1, -id_number)` — recurring, then blocker, then not-yet-fixed, then newest | IMP-0543, IMP-0383 | YES — `--selftest` asserts the rendered set's median `ts` is not older than the capped set's | `already wired` (generator, not a `verify-*.py` gate) |
| 2 | script | [`scripts/generate-known-failure-modes.py`](scripts/generate-known-failure-modes.py#L574) | New `MAX_IDS_PER_ROW = 6`. Id lists in the Recurring-classes table ([L574](scripts/generate-known-failure-modes.py#L574)) and the capped index ([L643](scripts/generate-known-failure-modes.py#L643)) truncate to the 6 highest ids + `(+N earlier)`. Counts and class names are untouched | IMP-0543 | YES — `--selftest` asserts no row's id cell exceeds 6 ids | `already wired` |
| 3 | script | [`scripts/generate-known-failure-modes.py`](scripts/generate-known-failure-modes.py#L888) | Write a second generated file `logs/known-failure-modes-appendix.md` holding **all** capped lessons in full and **all** truncated id lists. Not read at activation; linked from every capped-index note and every truncated row. This is what makes Change 2 lossless | WS-B requirement | YES — `--check` covers both files; `--selftest` asserts every capped lesson appears in the appendix | `already wired` |
| 4 | script | [`scripts/generate-known-failure-modes.py`](scripts/generate-known-failure-modes.py#L810) | Add `--selftest`: proves the generator can fail, asserts the size envelope WS-B asks for at synthetic 700/1000/1500-entry logs, and prints the dedup merge count so an inert grouping key is visible | IMP-0545, WS-B verification | YES — `python3 scripts/generate-known-failure-modes.py --selftest` | `already wired` |
| 5 | other | [`scripts/derived-counts-registry.json`](scripts/derived-counts-registry.json#L119) | Register the digest's line count and byte size so `verify-derived-counts.py` reports drift instead of a future document restating a stale figure | IMP-0529, IMP-0534 | YES — `python3 scripts/verify-derived-counts.py` | `already wired` |

**Constraint budget: 0 of 3 used.** WS-B states "none — generator change", and the measurement
agrees: every change above is to one script's behaviour, and each has a mechanical check. No rule
needs writing down that a `--selftest` does not already enforce.

### The numeric choices I am asking you to approve

These are decisions, not measurements, and WS-B explicitly reserved them:

| Choice | Value proposed | Why this value |
|---|---|---|
| **The WS-B cutoff `N`** | **Rejected outright — no age cutoff** | Measured at 0 of 537 rows selected. Age is not the discriminator on a 20-day-old corpus; `status` and recurrence are, and Change 1 uses those directly |
| **`MAX_PER_SECTION`** | **Unchanged at 20** | Lowering it is the only lever that materially shrinks the file (15 → −25 lessons ≈ −13KB), and the cap's own comment at [L79](scripts/generate-known-failure-modes.py#L79) says the right answer at the cap is to *split the section*, not lower the number. 67% is already hidden |
| **`MAX_IDS_PER_ROW`** | **6** | The only genuinely new number. Six fits one line, keeps the most recent instances visible, and cuts 8,160 bytes of exhaustive id enumeration to ~4,000. Any value from 4 to 10 is defensible; say so if you prefer another |

### Measured effect — stated honestly, including where it falls short of WS-B

Prototyped against the real log and against synthetic logs resampled from it (model reproduces
the current file to within 0.8%):

- at **542** log entries (today) — current 119,475 B → proposed ~122,400 B
- at **700** log entries — current ~134,300 B → proposed ~135,000 B
- at **1000** log entries — current ~146,400 B → proposed ~139,600 B
- at **1500** log entries — current ~163,300 B → proposed ~152,000 B

**WS-B asks for the file to stay "roughly flat" and this does not deliver that.** It delivers a
~7% reduction in growth, and it is *larger today* than the current file, because Change 1 promotes
recent lessons and recent lessons are longer prose (mean lesson length rose from ~180 chars on
2026-08-14 to ~600 by 2026-08-22, now ~455). I am proposing it anyway because the correctness
defect it fixes is worth more than 3KB, and because the honest reason the file cannot be made flat
is stated below rather than hidden behind a change that appears to address it.

**Why flat is not achievable without a decision outside this workstream.** 175 rendered lessons ×
~513 bytes = 89,780 bytes, **75% of the file**, and that term is bounded in *count* by
`MAX_PER_SECTION × sections`. The residual growth after Changes 1–3 is driven by the **number of
distinct classes** (66 unrouted classes today), not the number of findings. The two levers that
would actually flatten it are (a) lowering `MAX_PER_SECTION`, and (b) truncating rendered lesson
text — truncating at 400 chars saves 27,183 bytes (23%) but damages 113 of 175 lessons. Both trade
the file's usefulness for its size, and neither is a decision to take inside a generator change.

**And the largest single section is `Unrouted` — 216 lessons, 40% of all lessons, 66 classes with
no row in [`SECTIONS`](scripts/generate-known-failure-modes.py#L115).** Six classes account for
128 of them: `gate-reassures-wrongly` (27), `approved-document-internally-inconsistent` (25),
`hand-maintained-count-drifts-from-source` (22), `declared-policy-not-mechanically-enforced` (21),
`finding-diagnosis-unverified` (19), `platform-state-divergence` (14). That section's own note says
it "reaches nobody". Routing those six classes is the highest-value change available to this file
and it is **not in WS-B's scope** — it is a decision about which agent reads what, at which moment.
Flagged in section 5.

---

## 4. Retirements

| ID / file | What it was for | Why retired | Replaced by | Coverage proven? |
|---|---|---|---|---|
| — | — | — | — | — |

> Retirement check performed: 82 live constraint rows and 10 already-retired rows reviewed
> (`grep -rh '^| C-' constraints/ --include='*.md' | wc -l` → 82;
> `grep -rh '^| ~~C-' … | wc -l` → 10). **None is redundant under this review**, because this
> review adds no constraint and changes no rule — it changes one generator's ranking function and
> its output shape. A constraint retirement requires a *replacement* that provably covers the
> retired row's known-bad fixtures, and nothing here covers any constraint's ground.

**One candidate was considered and deliberately NOT retired:** the lesson-text deduplication key
at [L506](scripts/generate-known-failure-modes.py#L506) and the `**x{n}**` marker at
[L659](scripts/generate-known-failure-modes.py#L659). Measured, it merges **0 of 537** findings
and the marker has never fired ([IMP-0545](logs/improvement-log.jsonl#L542)). It is dead code by
measurement. It stays because removing it would silently discard the correct behaviour if lesson
texts ever do repeat, and because deleting a mechanism is a worse answer than *reporting that it is
inert* — which is what Change 4 does. Revisit if it still merges 0 at 1,000 entries.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0539, IMP-0540, IMP-0541, IMP-0544

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| [IMP-0539](logs/improvement-log.jsonl), [IMP-0540](logs/improvement-log.jsonl), [IMP-0541](logs/improvement-log.jsonl) | various | **Out of this dispatch's scope.** All three were already processed by reviews 7 and 8 ([2026-08-31-improvement-review-7.md](docs/improvements/2026-08-31-improvement-review-7.md), [-8.md](docs/improvements/2026-08-31-improvement-review-8.md)). At this dispatch's activation (09:05) all three read `unread` — cited by two review documents and carrying no `reviewed_in`, the [IMP-0488](logs/improvement-log.jsonl) defect. **Re-measured at 09:46: all three now read `awaiting-approval`** — a concurrent dispatch stamped them while this review was drafting. They are those reviews' to close, not this one's | reviews 7 and 8 reach their own gates |
| [IMP-0544](logs/improvement-log.jsonl#L541) | `finding-diagnosis-unverified` | Its `proposed_change` targets `agents/improvement-agent.md`, which is Group 6's file (WS-H with WS-F folded in). Editing it from a Group 7 dispatch is exactly the concurrent-same-file write [IMP-0080](logs/improvement-log.jsonl) and [IMP-0538](logs/improvement-log.jsonl) both cost this project | Group 6 (WS-H + WS-F) is dispatched — fold the one-paragraph note into it |

**States excluded from this review's scope, per activation step 2:** 115 `reviewer-deferred`
(each carries an accepted `deferred_reason`), 419 `APPLIED`, 2 `REJECTED`. The 3 entries at
`unread` before this dispatch are the three deferred above. Nothing was silently capped.

**Observed during this dispatch, not logged as a finding, reported here instead.** At 09:41
`python3 scripts/verify-improvement-log.py --check` printed
`ERROR: IMP-0542: reviewed_in names '…-7.md, …-9.md', which does not exist` and `FAILED`. Re-run
at 09:44 against the same file: exit 0, zero errors. Nothing was fixed in between. The concurrent
Group 6 dispatch was mid-write on `logs/improvement-log.jsonl`, converting `IMP-0542`'s
`reviewed_in` from a scalar to a list, and the validator read the half-written state. **A HARD gate
read a shared append-only file that another live session was writing, and reported a false FAILED.**
That is [`concurrent-session-same-file-write`](logs/improvement-log.jsonl) again —
[IMP-0080](logs/improvement-log.jsonl), [IMP-0538](logs/improvement-log.jsonl),
[IMP-0541](logs/improvement-log.jsonl) — reaching the *gates* rather than the writers. It is not
logged as a fourth finding because `IMP-0541` already carries the class and is open; it belongs to
whichever workstream takes the lease/lock question
([WS-L](docs/improvements/2026-08-31-capability-design-agent-system-optimisation.md#L331)), which
currently scopes leases to `pipeline-agent` writes only and would not have covered this.

**Routing `Unrouted`'s six largest classes is deferred to a new workstream**, not to this one.
It is the highest-value change available to this file (216 lessons, 40% of the corpus, reaching
nobody), it needs a decision about which agent reads what at which moment, and WS-B's scope is
bounded to compaction. Recommend it be written up as WS-N in the capability design document.

---

## 6. Digest impact

| | At activation (09:05) | Now (09:46) | After Changes 1–5 |
|---|---|---|---|
| Log entries | 539 | 543 | 543 |
| Distinct lessons | 537 | 541 | 541 |
| Recurring classes (x≥2) | 40 | 42 | 42 |
| Digest lines | 608 | 612 | ~600 (est.) |
| Digest bytes | 118,568 | 119,475 | ~122,400 (est.) |

The "Now" column includes one entry (`IMP-0546`) appended by a concurrent Group 6 dispatch, not by
this review. This review appended three: `IMP-0543`, `IMP-0544`, `IMP-0545`.

The middle column is already on disk: this review's three findings were appended and the digest
regenerated, per `CLAUDE.md`'s Learning Rules (append → validate → regenerate), which is the
standing obligation on **every** agent that appends and is not part of this review's proposed
changes. `python3 scripts/verify-improvement-log.py --check` exits 0;
`python3 scripts/generate-known-failure-modes.py --check` exits 0.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-01-improvement-review.md

Findings processed: 0 pre-existing NEW (capability mode)  →  3 clusters
                    3 findings logged by this review from its own measurements
Regression check:   4 prior changes audited, 1 class recurred
Proposed:           0 constraints (cap 3), 4 gates/scripts, 0 skill/knowledge edits,
                    0 agent-file edits, 0 retirements, 1 other
Altitude calls:     1 generalised from instance to class, 2 left as notes
Digest:             will regenerate — 541 lessons, 42 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

**APPROVED 2026-09-01** with the recommended defaults on all three open numeric choices: reject the
age-cutoff mechanism entirely, keep `MAX_PER_SECTION` at 20, set `MAX_IDS_PER_ROW` to 6.

**Step-8 re-verification before applying.** The tree had moved from 539 to 545 entries between the
draft and the keyword. Re-run: `verify-improvement-log.py --check` exit 0, zero errors; no entry
appended in the interval carries `corrects` or `contests` against `IMP-0383`, `IMP-0543`,
`IMP-0544` or `IMP-0545`. All four premises re-executed against the 545-entry log rather than
re-read (`IMP-0426`): dedup merges **0 of 543**; the 60-day cutoff selects **0 of 543**; the cap
binds in **6 of 10** populated sections; rendered median ts **2026-08-20** against capped
**2026-08-26**. Nothing was disproved, so nothing was withheld.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | `sort_key` → recurring, blocker, **unfixed**, **newest** ([L610](scripts/generate-known-failure-modes.py#L610)) | working tree | IMP-0543 |
| 2 | `MAX_IDS_PER_ROW = 6` ([L148](scripts/generate-known-failure-modes.py#L148)) + `id_cell()` ([L159](scripts/generate-known-failure-modes.py#L159)), applied to the Recurring-classes table and the capped index | working tree | — |
| 3 | `logs/known-failure-modes-appendix.md` — all capped lessons in full, all truncated id lists; [`render_appendix()`](scripts/generate-known-failure-modes.py#L847), [`group_lessons()`](scripts/generate-known-failure-modes.py#L577), [`live_lessons()`](scripts/generate-known-failure-modes.py#L557) | working tree | IMP-0543 |
| 4 | [`--selftest`](scripts/generate-known-failure-modes.py#L1014) (can-it-fail + nothing-lost + size envelope) and the dedup merge-count line | working tree | IMP-0545 |
| 5 | `known-failure-modes-digest-line-count` in `scripts/derived-counts-registry.json` | working tree | — |

**Change 5 was NARROWED, and this is the deviation record.** The approved row said "register the
digest's line count and byte size so `verify-derived-counts.py` reports drift". A registry row must
anchor to a prose claim that exists, and the natural home — `agents/improvement-agent.md` — is
Group 6's file, which section 5 of this review had already deferred. Anchoring it there would have
been the concurrent-same-file write this review named as a hazard. **Narrowed to:** the claim is
stated in the generator's own docstring and the row points there; line count only, not byte size
(no prose states a byte size, so a byte-size row would have been a registry defect by
construction). Measured: with the row pointing at `agents/improvement-agent.md`,
`verify-derived-counts.py` reported **1 registry defect** — `claim_pattern matched 0 times`. After
the narrowing: **0 registry defects**. That is the named false positive the narrowing removes.

The same edit corrected the docstring sentence that WS-B's wrong premise came from — it asserted
the digest's "cost stays flat while the log behind it grows", written when the log held 26 entries.

### Measured effect

| | Before | After |
|---|---|---|
| Log entries | 545 | 545 |
| Distinct lessons | 543 | 543 |
| Recurring classes (x≥2) | 42 | 42 |
| Digest lines / bytes | 608 / 118,568 | **618 / 123,943** |
| Appendix lines / bytes | — | **818 / 228,549** |
| Rendered median timestamp | 2026-08-20 | **2026-08-23** |
| Rendered lessons already `APPLIED` | 150/176 (85%) | **128/176 (73%)** |
| Lessons logged since 2026-08-25 that render | 25 of 253 | **68 of 259 (2.7×)** |
| Blocker-severity lessons rendered | — | 107 of 125 |

**The digest is 4,468 bytes larger, as predicted.** Change 1 promotes recent lessons and recent
lessons are longer prose; the growth curves cross at roughly 1,000 entries. `--selftest` asserts
the envelope: 131,511 B at 700 entries, 143,219 B at 1,000, 153,515 B at 1,500 — against the
current design's ~134,300 / ~146,400 / ~163,300. **This is a growth-rate improvement and a
correctness fix, not the flat file WS-B asked for**, and the reason it cannot be flat is now
recorded in the generator's docstring rather than left to be re-inferred.

The recency gain is real but bounded by the blocker term, which correctly consumes 107 of 176
rendered slots. That is the intended priority, not a defect.

### Verification

| Command | Result |
|---|---|
| `python3 scripts/generate-known-failure-modes.py --selftest` | **exit 0** — 8/8 checks; "367 capped, 0 missing" from the appendix |
| `python3 scripts/generate-known-failure-modes.py --check` | **exit 0** — both files current |
| `python3 scripts/verify-improvement-log.py --check` | **exit 0** — 545 entries, **0 unread, 0 awaiting-approval** |
| `python3 scripts/verify-doc-line-links.py` | exit 0 |
| `python3 scripts/verify-derived-counts.py` | SOFT WARN — 5 drifted claims, **0 registry defects**. All 5 pre-date this review (dev-summary and trustee-role column counts) and belong to the delivery feature, not here |
| `python3 scripts/verify-review-document.py` | exit 1 — **identical on `HEAD` before these changes** (3 cluster-count, 1 cross-ref, 1 lost-deferral, on three 2026-08-22/25/31 documents). This document contributes zero findings |

**Level reached, per `C-TECH-053`: V1.** Every claim above is a script that ran and whose output
was read. No live environment is involved in this change.

Entries rejected, with reasons:

| Finding | Rejected because |
|---|---|
| — | none |

**Left open deliberately:** `IMP-0544` stays `NEW` with a `deferred_reason` and a `revisit_when`
naming Group 6. Its measurement is fully applied — the age cutoff was rejected, not implemented —
but its `proposed_change` edits `agents/improvement-agent.md`, which this dispatch does not own.
Recorded as a reviewer-accepted deferral rather than closed on a fix that did not happen here.
