# Improvement Review — 2026-09-20 (2)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 10 `NEW` → 5 clusters
**Trigger:** blocker escalation (`IMP-0794`, unread) + the re-observation that closes `IMP-0787`
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** ~~AWAITING — nothing in section 3 has been applied.~~ **APPLIED 2026-09-20.** All four
changes landed; nine entries settled. See section 10. **Not yet committed to either repository.**

---

## 0. The measurement that decides this review

Two of the three things the dispatch brief asked for had **already been done by delivery
dispatches** between the brief being written and this review running. Both were measured, not
assumed, and in both cases the measurement changed the disposition from *propose a fix* to
*close the entry*.

| Brief said | Measured | Command |
|---|---|---|
| "a development-agent dispatch is currently fixing it" (the hand-typed count) | **Already fixed.** No literal count remains; the gate names the file zero times | `grep -n 'Should -Be 18' …Tests.ps1` → no match; `verify-source-derived-test-counts.py` → 0 hits on that file |
| The commercial ledger fails its gate 9-against-6 | **The gate now exits 0.** The gap is 10-against-7 — still exactly 3 short, reported non-fatally | `python3 scripts/verify-commercial-events.py` → `exit=0` |

A third premise moved **under the draft while it was being written**. On the first run of the
queue gate, `IMP-0666` reported as a hard `ERROR` — its evidence needle `acceptedDevOnly` not
found in the test file it names. On a re-run twenty minutes later the error was gone, because the
development-agent dispatch fixing `IMP-0794` had landed the refactor that restored the token. The
file now carries it five times.

**Nothing was proposed on the strength of that error**, and this is the section that records why:
an `APPLIED` entry whose needle has stopped matching is a real defect class, and it would have
been entirely reasonable to open one here. The tree was simply mid-change.

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| The keyword-channel rule in `agents/WORKFLOW.md` + the relay section in `agents/commercial-agent.md` | 2026-09-20 | `hard-gate-has-no-scoped-override-path` (x7) | **No — and it is confirmed working end to end.** A commercial gate cleared on a relay the next day | Working. This is what closes `IMP-0787` |
| [`C-COM-011`](constraints/commercial/commercial-constraints.md#L54) + check 3 of `scripts/verify-commercial-events.py` | 2026-09-20 | authorisation provenance | **No.** The new ledger entry carries both fields; the gate reports `0 unnamed/unrecorded` | Working |
| The pre-dispatch sibling check at [`agents/lead-agent.md#L122`](agents/lead-agent.md#L122) | 2026-09-20 | `duplicate-dispatch-unobserved` | **No** | Working — and section 3 extends this same subsection rather than opening a second one |
| The registered `CURRENT SIZE` correction in `scripts/generate-known-failure-modes.py` | 2026-09-20 | `hand-maintained-count-drifts-from-source` | **Yes — twice, elsewhere.** Two prose counts in the pipeline config still say 18 rev_setting rows against a measured 21 | See change 4 |

**Changes whose class recurred after a prose fix:** none.
**Changes whose class recurred after a gate:** none — in both recurrences below, the gate *fired
correctly*. `verify-source-derived-test-counts.py` halted the build on the drifted literal, and
`verify-derived-counts.py` is reporting the two stale prose counts right now. Neither is a
`gate-cannot-fail`; both are gates doing their job and a dispatch not finishing the change.

**I verified the last review's claims landed rather than trusting its own status header.** The
first grep for the lead-agent change came back empty and looked like an unevidenced `APPLIED`
claim; a second grep with the right terms found it at line 122. Recording that because a
regression check that greps once and concludes "never landed" is its own failure mode.

---

## 2. Clusters and promotion decisions

```
CLUSTER: hand-maintained-count-drifts-from-source  (x33 overall; here IMP-0794, IMP-0796)
Altitude:   CLASS — but the generalisation ALREADY LANDED, in the delivery dispatch
Ladder row: "second instance → generalise" (this was the sixth in this one file)
Becomes:    NOTHING NEW. The expected count is now derived from dev-scoring-settings.json in
            BeforeAll and compared via $script:acceptedDevOnly, never a literal. Verified:
            no `Should -Be 18` remains, and the gate names the file 0 times.
Retires:    nothing
Cites:      IMP-0794, IMP-0796
Residual:   The gate still reports 8 fragile literals in OTHER test files (DataverseScripts,
            EnsureSchema). Those are pre-existing and not this blocker's scope — they are
            tier-1 SOFT and named here so the number is not mistaken for zero.
```

```
CLUSTER: hard-gate-has-no-scoped-override-path  (x7 overall; here IMP-0787, IMP-0795)
Altitude:   CLASS — already fixed last review; this cluster exists to CLOSE, not to change
Ladder row: n/a — the re-observation rung
Becomes:    NOTHING NEW. IMP-0787 was parked at V4 waiting for exactly one event: a commercial
            gate clearing on a lead-agent relay. IMP-0795 is that event, recorded by the
            dispatch that performed it.
Retires:    nothing
Cites:      IMP-0787, IMP-0795
Residual:   One observation, at one desk. acceptance-agent and pm-agent also guard Human Gate
            Keywords and neither has been exercised by a relay since the rule landed. The rule
            is in WORKFLOW.md, which they all read, so this is monitoring rather than a gap.
```

```
CLUSTER: unflagged-platform-contract  (x2 — the altitude rule's own trigger; IMP-0790, IMP-0792)
Altitude:   CLASS — second instance, so an instance patch is forbidden here
Ladder row: "a tool could catch it mechanically" for one half; "an agent had the information
            and still did the wrong thing" for the other
Becomes:    The shared property is that architect-agent asserts things whose ground truth lives
            in a file it does not own — solution source, and the Dev Summary's §10 register.
            Split by instrument: the ID COLLISION is a comparison of VALUES, so it becomes a
            gate (change 1). The "no unverified platform contract" claim is a comparison against
            PROSE, so it stays an authoring step (change 2).
Retires:    nothing
Cites:      IMP-0790, IMP-0792
Residual:   The gate catches a collision only once BOTH documents are written. It cannot stop
            architect-agent picking a taken id at authoring time — that is what change 2's
            grep step is for, and a grep step is a checklist, not an enforcement.
```

```
CLUSTER: a HANDOFF premise accepted without reading the document that answers it
         (IMP-0785, IMP-0786 = unquoted-artefact x3; IMP-0789 = missing-architecture-decision
          -before-build-dispatch x1)
Altitude:   CLASS — and I am declaring the mixed class counts rather than hiding them
Ladder row: "the ORDER of steps was wrong" — in all three the information existed, in a tracked
            file, before the dispatch started
Becomes:    Two clauses added to the pre-dispatch subsection that already exists at
            agents/lead-agent.md#L122 (change 3). NOT a second subsection.
Retires:    nothing
Cites:      IMP-0786, IMP-0789
Residual:   IMP-0789's class has ONE member. I am folding it in because it shares the mechanism
            and the target file, not because the class count justifies it — a reader should
            treat that clause as a single-instance note that happened to have a home, and the
            honest test is whether a second instance appears. IMP-0785 needs no rule at all:
            C-COM-002 already required the resolution step, and CO-006 recorded the outcome.
```

```
CLUSTER: gate-reassures-wrongly  (IMP-0797, first instance of this specific behaviour)
Altitude:   INSTANCE — deferred, see section 5
Ladder row: "one instance, no general mechanism" → stays a log note
Becomes:    NOTHING. Recorded, stamped, and left open for a second instance.
Retires:    nothing
Cites:      IMP-0797
Residual:   The behaviour is arguably correct; only its description in the agent file is
            incomplete. Fixing a correct behaviour on one instance is how rule sets bloat.
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | `scripts/verify-assumption-id-collisions.py` **and its `.engine` twin** | For each feature, compare the `A-nnn` ids cited in the TAD against those in the Dev Summary §10 register; fail where one id names two different questions | IMP-0792 | YES — `python3 scripts/verify-assumption-id-collisions.py` | `HARD`, at `config/revitalise-grant-automation-build.yml` immediately after the `assumption-markers` step (L254) |
| 2 | agent | `agents/architect-agent.md` | One subsection under the ADR guidance: before asserting a mechanism introduces no unverified platform contract, grep source for **every** function it newly introduces, not only the one being contrasted against a prior ADR; and allocate a new `A-nnn` id from the next value free across **both** the TAD and the Dev Summary register | IMP-0790, IMP-0792 | N/A — instruction change | N/A |
| 3 | agent | `agents/lead-agent.md` | Two clauses appended to the existing pre-dispatch subsection at L122: (a) cross-check a HANDOFF's `wbs:` tag against `contract/evidence-map.json` before dispatching against a live-environment defect report; (b) where the only spec is a change order, grep it for a "no FR text yet" disclaimer and route to plan/architect first if present | IMP-0786, IMP-0789 | N/A — instruction change | N/A |
| 4 | other | `config/revitalise-grant-automation-pipeline.yml` L573, L1838 | Correct two prose counts, "the 18 rev_setting rows" → 21, the loose end the `IMP-0794` change left behind | IMP-0794 | YES — `python3 scripts/verify-derived-counts.py` | N/A |

**Constraint budget:** 0 of 3 used.

No constraint is proposed. Three of the four changes are instruction or prose; the one
enforcement this review adds is a gate, which the ladder prefers over a constraint row anyway.

**Change 4 is inside a file another agent owns, and I am claiming it deliberately.** The
pipeline-config boundary in my own agent file splits those notes by what settles them: a
**repository fact** settled by a grep I was going to run anyway is mine to re-measure and
re-date; **live environment state** is not. Two stale integers against a JSON file on disk are
squarely the first row.

**Change 1 is not finished when it is written.** Before it is wired I will run it against the
real corpus — every TAD and Dev Summary pair in `docs/` — read each finding one at a time, and
publish the measured precision as "N findings, K true positives" in section 8. A green
`--selftest` proves it *can* fail, not that it fails on the right things. If it measures badly it
gets redesigned, not exempted.

---

## 4. Retirements

> Retirement check performed: 86 live constraint rows reviewed (10 already retired), none
> currently redundant.

The nearest candidate was the settings-parity rule behind `IMP-0666`, which looked superseded
once the count became derived. It is not: the derivation and the parity assertion answer
different questions — *how many keys should TST have* versus *are DEV's keys mirrored at all* —
and the `IMP-0794` refactor kept both. Retiring it would have lost coverage, which is a
regression rather than a promotion.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0793

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0793 | `gate-reassures-wrongly` | **Not mine to settle.** It is parked `awaiting-approval` against the previous review, and its disposition — backfill three August ledger entries, or record a `deferred_reason` accepting the gap — is a reviewer decision about the commercial record. I re-measured it and did not re-derive it | the reviewer chooses; see the decision in section 9 |
| IMP-0797 | `gate-reassures-wrongly` | Processed and stamped, but **not** fixed: first instance, and the behaviour it describes is arguably correct | a second review stamps `excluded_by` and the citation warning persists |

The five entries the previous review excluded — `IMP-0785`, `IMP-0786`, `IMP-0789`, `IMP-0790`,
`IMP-0792` — are **processed here**, not deferred again. Each gets a `reviewed_in` stamp so the
queue stops reporting them as unopened.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 793 | 794 |
| Distinct classes | 175 | 175 |
| Recurring classes (x≥2) | 60 | 60 |
| Digest lines | 728 | regenerate to confirm |

The digest is **already stale** before this review touches anything — three delivery dispatches
appended findings without regenerating it. Regenerating is a required step, and it mechanically
drifts the registered `CURRENT SIZE` claim in the generator, so that correction lands in the same
change.

---

## 7. What the queue looks like, and what still blocks a build

| State | Count | Disposition |
|---|---|---|
| `unread` | 9 | **All 9 processed** — 8 named in the brief plus `IMP-0797`, logged during this review |
| `awaiting-approval` | 1 | `IMP-0793`, parked on `docs/improvements/2026-09-20-improvement-review.md` — reported, not re-derived |
| `reviewer-deferred` | 175 | Each carries a reason a human accepted; left alone. `IMP-0787` is closed out of this set |
| `already-fixed` | 0 | — |

**The build stays blocked until the keyword arrives, and I simulated that rather than assuming
it.** Stamping `reviewed_in` moves `IMP-0794` from `unread` to `awaiting-approval` — and the
blocker trigger fires on **both** states alike. So the draft alone does not clear it.

| Simulated disposition | Gate result |
|---|---|
| Draft only — `reviewed_in` stamps, no closures | `FAILED`, 1 problem: the blocker trigger, now reading `awaiting-approval` |
| Post-approval — 5 entries closed, 4 stamped | **`OK`, exit 0**, 0 errors, 0 triggers |

The simulation earned its place twice. It also caught a defect in this draft: closing `IMP-0787`
failed because its `proposed_change.target` names two files and my `applied_by` named neither.
That is a validator round-trip I would otherwise have paid at apply time, with the durable
changes already on disk.

The log was restored to byte-identity after each run (`diff` confirms).

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-20-improvement-review-2.md

Findings processed: 10 NEW  →  5 clusters
Regression check:   4 prior changes audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 1 gates/scripts, 0 skill/knowledge edits,
                    2 agent-file edits, 0 retirements
Altitude calls:     2 generalised from instance to class, 3 left as notes
Digest:             will regenerate — 794 lessons, 60 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 10. Applied — 2026-09-20

### The authorisation, recorded first

| | |
|---|---|
| Keyword | `APPROVE IMPROVEMENTS`, verbatim |
| Authorised by | **Anna Southern** (anna.southern@argelis.nl) |
| Channel | `lead-agent` relay, stated as quoted from her own turn in this session's conversation |
| Artefact named | `docs/improvements/2026-09-20-improvement-review-2.md` |

Checked against all four conditions of `agents/WORKFLOW.md` → *What channel a keyword must arrive
through* before the relay was accepted: from `lead-agent`, keyword verbatim, the human named, and
stated as quoted from her own turn. This is not a commercial act, so the record is this gate output
and the log line rather than `logs/commercial-events.jsonl`.

### Re-verified before applying

No `corrects` finding had been appended against anything closed here; the log's maximum id was
unchanged at `IMP-0797`, so no concurrent session had allocated one. Both premises the changes rest
on were re-measured and still held: the two pipeline prose counts still read 18, and the target
subsection in `agents/lead-agent.md` was still at line 122. The routed item was re-measured too and
is unchanged — still a reviewer decision, still exactly three ledger entries short.

### What landed

| # | Target | Repository | Landed |
|---|---|---|---|
| 1 | `scripts/verify-assumption-id-collisions.py` **and its `.engine` twin** | both | New HARD gate; byte-identical in both copies |
| 1b | `config/revitalise-grant-automation-build.yml` | instance | Wired as the `assumption-id-collisions` step, immediately after `assumption-markers` |
| 1c | `config/gate-baselines.json` | instance | One dated, owned baseline for the pre-existing `A-FLOW-13` collision |
| 2 | `agents/architect-agent.md` | `.engine` | New subsection *Two claims a TAD makes about files it does not own* |
| 3 | `agents/lead-agent.md` | `.engine` | New subsection *And check the two premises the HANDOFF itself carries*, appended to the existing pre-dispatch block |
| 4 | `config/revitalise-grant-automation-pipeline.yml` | instance | Two prose counts, 18 → 21 (L573, L1838) |
| 5 | `agents/improvement-agent.md` | `.engine` | The registered `verify-*.py` count, 63 → 64 — drifted by adding the gate |
| 6 | `logs/improvement-log.jsonl` | instance | Nine entries settled; `IMP-0797` appended during the review |
| 7 | `logs/known-failure-modes.md` + appendix | instance | Regenerated — 794 entries |

### The gate was measured against the real corpus, and the measurement changed the design

**1 finding across 3 document pairs, 1 true positive.**

The alternative design was built and measured first, and it is the reason the shipped one looks the
way it does:

| Candidate | Findings | True positives |
|---|---|---|
| **A** — an id with a definition row in **both** documents | 1 (`A-FLOW-08`) | **0** |
| **B** — an id marked **NEW** in the TAD that already has a register row | 1 (`A-FLOW-13`) | **1** — shipped |

Design A's only finding is a TAD row reading *"RESOLVED. Replaced by A-FLOW-11"* — a resolution
cross-reference, which is the register working correctly. A TAD legitimately carries rows about ids
the register owns; what it must not do is hand a **new** question an id already taken. That
false positive is now a selftest case, so the polarity cannot silently invert later.

The one true positive is **pre-existing debt in an approved document that only `architect-agent`
may revise**, so it is baselined rather than left to halt the next build: owner `architect-agent`,
expires 2026-10-31, clearing action named. The baseline suppresses the failure and still prints the
finding on every run.

### Nothing narrowed, nothing withheld

Every change survived re-verification in its approved wording.

### One late correction, caused by this review's own closure

Closing the relay finding made the **previous** review read as one that had closed entries — which
re-classified `IMP-0793`. The gate then reported it correctly: its state said `awaiting-approval`,
whose instruction is *send the keyword*, but that review's keyword had already been given, so
sending another could never dispose of it.

Its `deferred_reason` and `revisit_when` now record the honest state: **routed to the reviewer,
pending, with the return condition named**. The substantive choice — backfill the three ledger
entries, or accept the gap — is untouched and remains the reviewer's. Warnings fell from 9 to 8.

Recording this because it is the shape section 0 warned about: a routed item sits open across
exactly the interval in which something else moves it.

### Not yet published — and a clean tree does not prove otherwise

Four of the changes are in the `.engine` submodule and are **committed to neither repository**. The
publish order is not a preference: push the submodule first, verify with
`git -C .engine branch -r --contains HEAD`, then commit and push the instance pointer bump. A
pushed pointer to an unpushed object breaks `git submodule update --init` in every fresh clone.

### Verification run

| Check | Result |
|---|---|
| `verify-improvement-log.py --check` | **OK** — 794 entries, blocker trigger cleared |
| `verify-assumption-id-collisions.py --selftest` | **OK** — 6 checks; the gate can fail |
| `verify-assumption-id-collisions.py` (real corpus) | **OK** — 3 pairs, 1 baselined |
| `verify-build-config.py` | **OK** — the new gate owns its wiring |
| `verify-derived-counts.py` | **OK** — 10 claims, 0 drifted |
| `verify-class-defences.py` | **OK** — 4 defences, 25 references |
| `verify-engine-instance-split.py` | **OK** — the twin is an unsplit duplicate, as 63 of 91 scripts are |
| `generate-known-failure-modes.py --check` | **current** — 794 entries |
| `verify-doc-line-links.py` | **OK** |

**Not verified:** no build was run end to end, so the new step is proven at V1 — it parses, its
selftest passes, and it runs correctly standalone. Nothing here executed it inside a real build.
