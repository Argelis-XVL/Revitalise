# Improvement Review 42 — 2026-08-29

**Agent:** improvement-agent (tier `strategic`)
**Status:** APPLIED 2026-08-29 under `APPROVE IMPROVEMENTS`. Five of six changes landed as
approved; change 2 was already half-live and its remaining half is recorded as a **no-op**, per
this document's own §6 instruction. §9 has the record.
**Findings processed:** 4 `NEW` → 3 clusters
**Trigger:** the **unread `blocker`** trigger — `python3 scripts/verify-improvement-log.py --check`
reported `TRIGGER: 3 NEW entry(ies) of severity 'blocker' in state 'unread'` naming
[`IMP-0484`](../../logs/improvement-log.jsonl), `IMP-0485` and `IMP-0486`. Processed immediately,
not batched, per [`improvement-agent.md` L82](../../agents/improvement-agent.md#L82).
**Scope:** `IMP-0485` and `IMP-0486` (the two new blockers), plus `IMP-0487` and `IMP-0488`, both
appended by this review. **`IMP-0484` is NOT processed here** — improvement review 41 already
analysed it in full and is parked at its own gate; this review only supplies the `reviewed_in`
stamp it was missing. See §5.
**WBS:** `wbs:6.9` for `IMP-0485`/`IMP-0486`/`IMP-0487`; `IMP-0488` is `feature:system` and serves
no WBS task, so no change-order question arises
([`C-COM-002`](../../constraints/commercial/commercial-constraints.md#L35)).

---

## Summary

**The gate everyone assumed was missing has existed since 2026-08-26, is wired HARD, and caught
this defect — then an inline `--allow` on its own command line waved it through to the reviewer.**
[`IMP-0485`](../../logs/improvement-log.jsonl) proposes adding
[`scripts/verify-code-app-data-sources.py`](../../scripts/verify-code-app-data-sources.py). Running
it, per [`improvement-agent.md` L134](../../agents/improvement-agent.md#L134), settles the question
in one second: it exists, it has nine fixtures, and
[`logs/build.log` L39](../../logs/build.log#L39) and [L40](../../logs/build.log#L40) both record
`code-app-data-sources OK 6/7 (1 declared allowance, ADR-038)`. The finding's root cause is wrong
and `IMP-0487` records the correction.

**The real defect is that this repository has two exemption channels and only one of them is
governed.** [`config/gate-baselines.json`](../../config/gate-baselines.json) requires
`gate, matches, reason, owner, clears_when, expires`
([`gate_baseline.py` L65](../../scripts/lib/gate_baseline.py#L65)) and **fails on an expired entry**
([L140](../../scripts/lib/gate_baseline.py#L140)); four gates read it and it holds six aged
entries. `verify-code-app-data-sources.py` instead has a private `--allow` flag that requires only
a reason string, carries no expiry, is never aged, and is invisible to every reader of the
register. The one exemption that went through the ungoverned channel is the one that reached a
reviewer.

**And it is still there, now masking the very regression it was written about.** Measured in §6,
not argued: with the live `--allow` string from
[`build.yml` L1306](../../config/revitalise-grant-automation-build.yml#L1306) the gate returns
**OK** over an app whose `rev_roundstatisticsresults` registration has been removed; without it,
**FAILED**. The allowance's own clearing action says *"DELETE THIS --allow LINE in the same change
as step 9"*, step 9 landed at 15:26–15:33 today, and the line survived.

---

## 1. Regression check — did review 40's changes work?

Review 41 is **parked, not applied**, so the last applied review is **review 40** (2026-08-28,
13 changes). Review 41 §1 already audited all thirteen and found three recurrences
(`IMP-0478`, `IMP-0479`, `IMP-0483`). **I am not re-deriving that audit** — it is correct and it is
in [review 41 §1](2026-08-29-improvement-review.md). What follows is the audit specific to *this*
review's two classes, which review 41 had no reason to perform.

| Prior change | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|
| `verify-code-app-data-sources.py` + the HARD `code-app-data-sources` step (built 2026-08-26 for [`IMP-0329`](../../logs/improvement-log.jsonl)) | `v3-does-not-imply-v4` | **YES — [`IMP-0485`](../../logs/improvement-log.jsonl)** | **The gate WORKED and the exemption defeated it.** Not a wrong-altitude call — a governance gap |
| Four knowledge edits to [`code-apps.md`](../../knowledge/technology/code-apps.md) for `IMP-0187`, `IMP-0191`, `IMP-0192`, `IMP-0224` | `v3-does-not-imply-v4` | **YES — this is the fifth** | **Wrong altitude, confirmed by count.** Four prose fixes, four recurrences; the mechanical fix (the gate) is the one that finally caught it |
| [`gate-baselines.json`](../../config/gate-baselines.json) + `gate_baseline.py` (review 36, `IMP-0439`) | `hard-gate-red-on-pre-existing-debt` | **NO** | **Working** — six entries, all owned and dated. This review extends its reach rather than adding a rival |

The four audit questions, for the recurrence that matters:

- **Was it prose or a gate?** Both, in sequence, and the difference is the whole lesson. Four
  **prose** fixes into `knowledge/technology/code-apps.md` produced four recurrences of
  `v3-does-not-imply-v4` on this one app. The **gate** built for `IMP-0329` caught the fifth on
  its first encounter.
- **Did the gate run?** Yes — twice, on 2026-08-28 at 16:16 and 23:07, both recorded in
  `logs/build.log`. It is not mis-scoped and it is not unwired.
- **So why did the defect ship?** Because a HARD gate's finding was suppressed by an argument made
  in a code comment and a command-line flag, and nothing aged that argument or carried it to the
  deploy decision. That is a **new** property, not a recurrence of the old one.
- **Did closure evidence match the level the defect was visible at?**
  [`IMP-0224`](../../logs/improvement-log.jsonl) is the honest counter-example and it is why this
  is the fifth instance rather than the first: it is `observable_at: V4`, it was deliberately left
  open with a `revisit_when` naming *"a real trustee signs in … and the app loads"*, and that
  re-observation has now happened and **failed** — differently, but on the same screen. It stays
  open; §5.

---

## 2. Clusters and promotion decisions

```
CLUSTER: v3-does-not-imply-v4  (x11 — this instance: IMP-0485, corrected by IMP-0487)

Altitude:   CLASS, and the class is NOT the one the finding named. IMP-0485's stated class
            has 11 members and its stated remedy (build the gate) is already on disk. The
            PROPERTY that actually failed is "an exemption from a HARD gate was taken
            through a channel that has no expiry and nobody ages", and it has two channels
            to compare: config/gate-baselines.json (6 entries, all owned and dated, read by
            4 gates, fails when expired) and verify-code-app-data-sources.py's private
            --allow (1 entry, no expiry, aged by nobody). The ungoverned one shipped a V4
            defect to a reviewer.

Ladder row: "Prefer the most mechanical home available" + "second instance -> generalise".
            The mechanical home ALREADY EXISTS. This is not a new register; it is one gate
            being moved onto the register the other four already use.

Becomes:    1. verify-code-app-data-sources.py reads scripts/lib/gate_baseline.py instead of
               its own --allow. An exemption then REQUIRES gate/matches/reason/owner/
               clears_when/expires and FAILS once expired.
            2. The live rev_roundstatisticsresults exemption migrates into the register with
               a date, and the stale inline flag is deleted -- it is currently masking a real
               regression, measured in §6.
            3. C-TECH-053 gains the deploy-side half: an exemption for a defect whose
               observable_at is V4 or higher is not discharged by a green build. The
               Deployment Summary names it as a known-broken surface, or the deploy does not
               go to a reviewer.

Retires:    verify-code-app-data-sources.py's `--allow` flag and its parse_allow() helper
            (L113). A real retirement, not a nominal one: the capability survives on the
            shared register with strictly MORE governance (an expiry the flag never had).

Cites:      IMP-0485 (the finding), IMP-0487 (its correction), IMP-0329 (the gate's origin),
            IMP-0224 + IMP-0187 + IMP-0191 + IMP-0192 (the four prose fixes this recurrence
            audits), IMP-0439 (the register this adopts)

Residual:   THREE, and the first is the one to read.

            (a) NONE of this repairs the reviewer's screen. The source-side fix landed
                DURING this review (15:26 and 15:33, by a concurrent dispatch, not by me);
                the app has not been rebuilt or re-pushed since, so the live DEV app still
                throws. IMP-0485 is observable_at V4 and stays OPEN -- §5.

            (b) The register governs the EXEMPTION, never the DEPLOY. Change 3 is prose in a
                constraint, because deciding "is this surface safe to show a reviewer" needs
                a judgement no gate can make. What the gate CAN do -- age the exemption -- is
                change 1, and change 3 does not pretend to more.

            (c) An exemption can still be renewed indefinitely by moving its date. Nothing
                closes that, and the register's own _not_a_waiver note already says so: the
                control is the date plus a human reading it.
```

```
CLUSTER: no-assertion-on-shipped-content  (x21 — this instance: IMP-0486)

Altitude:   CLASS. C-TECH-053 (HARD) already says a component is reported only at the level
            actually executed, and already binds development-agent. Its Verify By names the
            build manifest, Test Report §7, pipeline.yml's V4 step, the Deployment Summary
            and verify-improvement-log.py -- and NOT the Dev Summary, which is the document
            a reviewer actually reads to decide what to expect on screen. So this is an
            enforcement gap in an existing HARD rule, not a missing rule.

Ladder row: "A tool could catch it mechanically" -- but only for the half that has a VALUE.

Becomes:    4. A new SOFT gate asserting on git's answer, not on wording: every source path a
               dev summary CITES must be tracked. Measured 9 findings / 9 true / 0 false.
            5. The prose half in how-to-verify-a-platform-contract.md's V-level section:
               "shipped"/"implemented in full"/"live" for a code artefact needs a commit sha
               or a pipeline.log entry, else the claim is "authored, not yet deployed".

Retires:    nothing -- no existing gate reads dev summaries for this property.

Cites:      IMP-0486, IMP-0225 (the V-level closure rule C-TECH-053 already carries)

Residual:   TWO.

            (a) The gate is SOFT, deliberately. During normal development a dev summary
                legitimately cites uncommitted work; a HARD gate would be red for the whole
                of every in-flight feature and would be routed around within a day. That is
                the measured lesson of IMP-0439 and IMP-0477 (hard-gate-red-on-pre-existing-
                debt, x2), and it is why this is a report rather than a halt.

            (b) It cannot read the SENTENCE. A dev summary that cites only committed files
                and still overclaims in prose passes. The phrase-based design that would
                catch that was measured at ~83% false and REJECTED -- §6.
```

```
CLUSTER: learning-substrate-destroyed  (x27 — this instance: IMP-0488)

Altitude:   CLASS. Two documents in this repository disagree about WHEN a review stamps
            reviewed_in, and the disagreement is what summoned this dispatch.
            improvement-agent.md step 8 puts all bookkeeping at apply time;
            verify-improvement-log.py L26 defines `awaiting-approval` as a stamp that exists
            BEFORE approval. Review 41 followed the agent file, so a fully-analysed blocker
            reported as `unread` -- "nothing records that anyone has looked at this" -- which
            is exactly the IMP-0154 cost the four-state model was built to end.

Ladder row: "The system's own memory failed" -> a read-path change; and "the ORDER of steps
            was wrong" -> the stamp belongs at draft time, not approval time.

Becomes:    6. improvement-agent.md's step 6 requires the stamp when the draft is written,
               and step 8 records that only status/applied_by move on approval. Each names
               the other document so they cannot drift apart again.

Retires:    nothing.

Cites:      IMP-0488, IMP-0154 (the original instance of this cost)
            NOT cited: the entry this happened to is named in prose in §5 and is review
            41's to process, so citing it here would read as a processing claim.

Residual:   The gate already emits the exact WARNING for this ("cited by 1 review document
            and carries NO 'reviewed_in'"). It fired correctly on IMP-0484 and was not acted
            on, because it prints BENEATH a FAIL whose own instruction -- "run an improvement
            review" -- is the wrong remedy for a stamped entry. Change 6 fixes the
            instruction that causes the miss; it does not make the warning louder.
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | script | [`verify-code-app-data-sources.py` L113](../../scripts/verify-code-app-data-sources.py#L113) | **Retire the private `--allow` flag**; read exemptions from [`gate_baseline.py`](../../scripts/lib/gate_baseline.py) instead, so every exemption requires `owner`, `clears_when` and a dated `expires`, and an expired one **fails**. The flag becomes a usage error naming the register | IMP-0485, IMP-0487, IMP-0439 | YES — `--selftest` plus a corpus run, §6 |
| 2 | other | [`gate-baselines.json`](../../config/gate-baselines.json) + [`build.yml` L1306](../../config/revitalise-grant-automation-build.yml#L1306) | Migrate the `rev_roundstatisticsresults` exemption into the register with an expiry, and **delete the inline `--allow`**. It is now stale — step 9 landed today and the line survived its own clearing action — and §6 measures it masking a real regression | IMP-0485, IMP-0487 | YES — the gate goes red on the fixture in §6 once the flag is gone |
| 3 | constraint-amendment | [`C-TECH-053`](../../constraints/technology/technology-constraints.md#L108) | Deploy-side rung: **an exemption for a defect whose `observable_at` is V4 or higher is not discharged by a green build.** Before an environment is handed to a reviewer, the Deployment Summary names every open exemption over a V4-observable surface, or the handover does not happen. [`pipeline.log` L35](../../logs/pipeline.log#L35) recorded *"STEP 9 … deliberately NOT performed"* and *"Level reached: DEV DEPLOYED (V3)"* correctly — and the reviewer was pointed at the app anyway | IMP-0485, IMP-0486, IMP-0225 | Partly — the naming is prose; the exemption's existence is machine-readable once change 1 lands |
| 4 | script | `scripts/verify-dev-summary-artefacts-committed.py` (new, **SOFT**) | Every source path a dev summary cites must be tracked by git; report each that is not. Asserts on git's answer, never on wording. **Measured: 9 findings across 7 documents and 30 cited paths, 9 true positives, 0 false** | IMP-0486 | YES — `--selftest` plus the corpus run in §6 |
| 5 | skill | [`how-to-verify-a-platform-contract.md` L361](../../skills/how-to-verify-a-platform-contract.md#L361) | In the V-level section: *"shipped" / "implemented in full" / "live"* for a code or UI artefact cites a commit sha or a `logs/pipeline.log` entry naming it. Absent either, the claim is **"authored, not yet deployed"** — V1/V2, not V4 | IMP-0486 | N/A — instruction change; change 4 is its mechanical half |
| 6 | agent | [`improvement-agent.md` L102](../../agents/improvement-agent.md#L102) and its step 8 | Stamp `reviewed_in` on every processed entry **at draft time**, not on approval; step 8 records that only `status`/`applied_by` move on the keyword. Each half cites [`verify-improvement-log.py` L26](../../scripts/verify-improvement-log.py#L26) so the two documents name each other | IMP-0488, IMP-0154 | YES — `verify-improvement-log.py --check` stops warning |

**Constraint budget: 0 of 3 used.** Change 3 amends an existing row. `C-TECH-053` is the correct
home for both delivery clusters — it already binds `development-agent`, `build-agent`,
`test-agent`, `pipeline-agent` and `improvement-agent`, and both findings are failures of *its*
rule, not of a rule nobody wrote.

Changes 3 and 5 are the only ones not fully mechanical, and both are deliberately prose: one asks
for a judgement about reviewer-readiness, the other governs a sentence. Their mechanical halves are
changes 1 and 4.

---

## 4. Retirements

| ID / file | What it was for | Why retired | Replaced by | Coverage proven? |
|---|---|---|---|---|
| `--allow` flag + `parse_allow()`, [`verify-code-app-data-sources.py` L113](../../scripts/verify-code-app-data-sources.py#L113) | A per-gate exemption channel taking `ENTITY=REASON` on the command line | Requires only a reason string. **No expiry, no ageing, no visibility to the four gates that read the register** — and its one live use is currently stale and masking a regression (§6) | [`config/gate-baselines.json`](../../config/gate-baselines.json) + [`gate_baseline.py`](../../scripts/lib/gate_baseline.py), which require `owner`, `clears_when` and `expires` and **fail** once expired | YES — change 1 keeps the script's own `an-owned-exemption-passes-and-is-named` and `a-bare-exemption-with-no-reason-is-refused` fixtures, re-pointed at the register. Both must still pass, and a third is added for **expired** |

Derived, not typed: **10** retired constraint rows
(`grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l`), unchanged by this review — no
constraint is retired here, only a script flag. Matches the figure registered in
[`derived-counts-registry.json`](../../scripts/derived-counts-registry.json).

**Verify-script count moves 51 → 52** (`ls scripts/verify-*.py | wc -l`, currently **51**) when
change 4 lands. That figure is registered as `improvement-agent-verify-script-count` and change 4
updates it in the same change, per
[`improvement-agent.md` L354](../../agents/improvement-agent.md#L354).

---

## 5. Findings left unprocessed

**Deferred:** IMP-0478, IMP-0479, IMP-0480, IMP-0481, IMP-0482, IMP-0483

Six of the nine `unread` entries, unchanged from review 41 §5 — all `rework` or `friction`, none
fires a trigger on its own, and a blocker dispatch must not pull a review of everything around it
([`improvement-agent.md` L87](../../agents/improvement-agent.md#L87)). The **86**
`reviewer-deferred` entries are untouched and unread by this review.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| [`IMP-0478`](../../logs/improvement-log.jsonl) | `gate-reassures-wrongly` | Review 40 §7 put this to the reviewer as an open schema question | the reviewer answers review 40 §7 |
| [`IMP-0479`](../../logs/improvement-log.jsonl) | `gate-invocation-omits-required-arg` | Second instance; needs generalising, not another named-file patch | the next batch review, or a third instance |
| [`IMP-0480`](../../logs/improvement-log.jsonl) | `declared-policy-not-mechanically-enforced` | Delivery finding on ADR-039's k=5 threshold; needs the TAD | the next batch review |
| [`IMP-0481`](../../logs/improvement-log.jsonl) | `approved-document-internally-inconsistent` | One cluster with `IMP-0482`; process together | the next batch review |
| [`IMP-0482`](../../logs/improvement-log.jsonl) | `approved-document-internally-inconsistent` | See above | the next batch review |
| [`IMP-0483`](../../logs/improvement-log.jsonl) | `gate-reassures-wrongly` | A wording call on review 40's change 13 | the next batch review |

### Three entries this review processes but does NOT close

- **[`IMP-0485`](../../logs/improvement-log.jsonl)** — `observable_at: V4`. Its source-side cause
  was repaired **during this review** by a concurrent dispatch (15:26 `dataSourcesInfo.ts` +
  `power.config.json`; 15:33 `client.ts` rewired from the stand-in to
  `Rev_roundstatisticsresultsService`), and **not by me**. The app has not been rebuilt or
  re-pushed since, so the reviewer's screen is still broken. On approval it takes `reviewed_in`, a
  `deferred_reason` recording what landed, and `revisit_when`: **the reviewer reloads the trustee
  portal's Round overview after a `pac code push` and the screen renders.** An honest open entry
  beats a closed one nobody tested ([`IMP-0224`](../../logs/improvement-log.jsonl), `IMP-0225`).
- **[`IMP-0486`](../../logs/improvement-log.jsonl)** — `observable_at: V4`. Changes 4 and 5 address
  the *claim*; the design-system conversion itself is still uncommitted against `HEAD 5b8b985` and
  has still never rendered in a browser. Same treatment, `revisit_when`: **the conversion is
  committed and the reviewer sees the refreshed UI in DEV.**
- **[`IMP-0484`](../../logs/improvement-log.jsonl)** — **not processed here at all.** Review 41
  analysed it fully and is parked at its own gate. This review supplies only the missing
  `reviewed_in` stamp naming *that* document, which moves it from `unread` to `awaiting-approval`
  so the queue stops reporting it as unlooked-at. Its four changes remain review 41's to apply.

### Reported, not fixed — two live delivery defects

`IMP-0486` names two UI defects that are **delivery work under `wbs:6.9`, not rules**, so they are
routed rather than fixed here ([`C-COM-002`](../../constraints/commercial/commercial-constraints.md#L35)).
Both confirmed by reading the working tree:

- [`ds.module.css` L319](../../src/code-apps/trustee-review-portal/src/styles/ds.module.css#L319) —
  `.statTileValue` sets `font-size: var(--text-2xl)` with **no** `overflow-wrap`, `word-break` or
  `white-space` rule, and the file contains **zero** such rules anywhere. A value like
  `£550,000.00` overflows its tile. This is the reviewer's *"text doesn't fit the squares."*
- [`ApplicationFilters.tsx` L30](../../src/code-apps/trustee-review-portal/src/components/ApplicationFilters.tsx#L30) —
  the three `<Select>` controls carry **no `className`** and render at Fluent's unstyled native
  size, while the score fields use the styled `ds/Input`. This is *"dropdown boxes not the same
  size as the first two filters."*

Both need a `development-agent` dispatch. Neither is an improvement-agent change.

---

## 6. Measurement

**Every number below was produced by running the thing, not by reading it**
([`improvement-agent.md` L134](../../agents/improvement-agent.md#L134),
[L383](../../agents/improvement-agent.md#L383)).

### Change 1 — the stale allowance masks a real regression

Fixture: the app exactly as it stands, with the `rev_roundstatisticsresults` block removed from
`dataSourcesInfo.ts` — i.e. the defect the reviewer met, reproduced.

| Run | Result |
|---|---|
| `verify-code-app-data-sources.py <fixture>` | **FAILED** — *"UNRESOLVABLE DATA SOURCE … throws for a real signed-in user and at no earlier level"*; `7 registration(s), 6 Dataverse source(s)` |
| Same, **with the live `--allow` string from `build.yml` L1306** | **OK**, exit 0 — *"exempt by --allow: rev_roundstatisticsresults"* |

The exemption's own text says *"Clear by deleting this line in the same change as step 9."* Step 9
landed at 15:26 and 15:33 today; the line is still at
[L1306](../../config/revitalise-grant-automation-build.yml#L1306). **A clearing action written as
prose in a comment did not clear.** A dated `expires` in the register would have.

### Change 1 — the two channels, counted

| Channel | Governed by | Entries | Owner required | Expiry required | Aged |
|---|---|---|---|---|---|
| [`gate-baselines.json`](../../config/gate-baselines.json) | [`gate_baseline.py` L65](../../scripts/lib/gate_baseline.py#L65) | **6** | yes | **yes** — expired **fails** ([L140](../../scripts/lib/gate_baseline.py#L140)) | yes |
| `--allow` on `verify-code-app-data-sources.py` | itself, [L113](../../scripts/verify-code-app-data-sources.py#L113) | **1** | by convention only | **no** | **no** |

Four gates read the register (`verify-build-config.py`,
`verify-provisioning-test-presence.py`, `verify-superseded-column-writers.py`,
`verify-tad-coverage.py`). The fifth exemptable gate is the one that shipped the defect.

### Change 4 — the value-based design, and the phrase-based one it replaced

**Candidate A, phrase-based** — the shape `IMP-0486` itself proposes (require a sha near any
*"shipped" / "implemented in full" / "live"* sentence):

- **99 hits across 7 documents.** Adjudicating the first 12 in
  `trustee-portal-visual-refresh-dev-summary.md`: **2 true, 10 false** — *"the shipped bundle"*
  (build output), *"'already shipped' and trustee-visible"* (quoting another document), *"would
  have shipped a…"* (a counterfactual), *"rather than shipped state"* (discussing a finding),
  *"What shipped carries no `<v>`"* (describing XML). **≈83% false.**
- That is squarely in the 48–100% band this repository has now measured **five** times
  ([`IMP-0422`](../../logs/known-failure-modes.md#L36), `IMP-0428`), and
  [`improvement-agent.md` L430](../../agents/improvement-agent.md#L430) is explicit: **assert on
  VALUES, not on PHRASES, wherever a value exists.** A commit is a value. **Candidate A is
  rejected on measurement, not on taste.**

**Candidate B, value-based** — every source path a dev summary cites must be tracked by git:

- **9 findings across 7 documents and 30 distinct cited paths. 9 true positives, 0 false.** All
  nine are in `trustee-portal-visual-refresh-dev-summary.md`, all nine exist on disk and are
  untracked, and they include `ds.module.css`, both round-statistics seed scripts and three
  solution `Entity.xml` files.
- **Polarity is not invertible here**, which is the point: git's answer is a fact about a commit,
  so a corrected document cannot score worse than the defective one the way a retained erratum
  phrase does.

### Change 1's polarity, and the corpus before any change

| Run | Result |
|---|---|
| `verify-code-app-data-sources.py` against the app **as it now stands** | **OK** — `7 registration(s), 7 Dataverse source(s)` (correct: step 9 landed mid-review) |
| `--selftest` | **OK — 9 fixtures**, unchanged |
| Same gate against `git show HEAD:` versions of both files | **OK, 0 findings** — 5 entity sets, 5 registered. No false positives on history |

### The two claims of `IMP-0485`, executed rather than read

- *"no gate compares a Code App's own runtime call sites against `dataSourcesInfo.ts`"* —
  **FALSE.** The gate exists, is tracked since 2026-08-26, and is wired HARD at
  [`build.yml` L1302](../../config/revitalise-grant-automation-build.yml#L1302). Recorded as
  `IMP-0487` with a `corrects` edge.
- *"`dataSourcesInfo.ts` and `power.config.json` … have no `rev_roundstatisticsresults` entry"* —
  **true when logged at 15:20, false by 15:26.** Both now carry it.

### A note on the interval, because it happened twice in one session

[`improvement-agent.md` L156](../../agents/improvement-agent.md#L156) warns that the window between
a gate opening and the keyword arriving is time in which delivery dispatches land live ground truth
([`IMP-0405`](../../logs/improvement-log.jsonl)). **This review watched its own subject change
twice while it was being written** — `dataSourcesInfo.ts` at 15:26, `client.ts` at 15:33. Every
factual clause above was re-run after the second change. Anything approving this document should
assume the same can happen again before the keyword arrives, and change 2 in particular must be
re-measured at apply time: if a later dispatch deletes the `--allow` line first, change 2 becomes a
no-op and should be recorded as such rather than applied.

---

## 7. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 483 | **485** |
| Distinct lessons | 482 | 484 |
| Recurring classes (x≥2) | 39 | 39 |
| Digest lines | 585 | **585** — measured after regenerating, never predicted |

`IMP-0485` and `IMP-0486` already render (the generator reads lessons regardless of status), so the
delta is the two entries this review appended. No new class appears: `finding-diagnosis-unverified`
is already x14 and `learning-substrate-destroyed` x27. **The line count is deliberately
unpredicted** — a review that predicted 31→26 and measured 31→30 is
[`IMP-0198`](../../logs/known-failure-modes.md#L28).

Regenerated with `python3 scripts/generate-known-failure-modes.py`, confirmed current with
`--check`, and validated **first** with `python3 scripts/verify-improvement-log.py` — validator
before generator, per `CLAUDE.md`'s learning rules (`IMP-0369`: regenerating is not validating).

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-29-improvement-review-2.md

Findings processed: 4 NEW  →  3 clusters
Regression check:   13 prior changes audited (review 41 §1) + 3 audited here, 2 classes recurred
Proposed:           0 constraints (cap 3), 1 constraint amendment, 2 gates/scripts,
                    1 skill/knowledge edits, 1 agent-file edits, 1 other, 1 retirement
Altitude calls:     3 generalised from instance to class, 0 left as notes
Digest:             will regenerate — 484 lessons, 39 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 9. Applied — 2026-08-29

**Five changes landed as approved. One — change 2 — was found already half-done by a concurrent
dispatch, and its remaining half is a no-op recorded as such rather than performed.** §6 of this
document anticipated exactly that and gave the instruction; this section follows it.

| # | Change | State | Measured at apply time |
|---|---|---|---|
| 1 | [`verify-code-app-data-sources.py`](../../scripts/verify-code-app-data-sources.py#L113) reads the shared register | **APPLIED** as approved | `--selftest` **PASS, 12 fixtures** (up from 9). New: an owned register entry passes **and is still reported**; an unowned one is refused; an **expired** one is refused; an entry for another gate exempts nothing here; the retired flag is a usage error naming the register |
| 2 | [`build.yml`](../../config/revitalise-grant-automation-build.yml#L1293) + [`gate-baselines.json`](../../config/gate-baselines.json) | **HALF ALREADY LIVE, HALF A NO-OP** — see below | The step's command carries no `--allow`; the gate is green unaided at **7 registrations / 7 Dataverse sources** |
| 3 | [`C-TECH-053`](../../constraints/technology/technology-constraints.md#L108) deploy-side rung | **APPLIED** as approved | Partly mechanical by design; the exemption's existence is now machine-readable via change 1 |
| 4 | [`verify-dev-summary-artefacts-committed.py`](../../scripts/verify-dev-summary-artefacts-committed.py#L1) (new, SOFT) | **APPLIED**, and **wired** — see below | `--selftest` **PASS, 7 fixtures**. Corpus: **12 findings across 7 documents and 219 distinct cited paths, 12 TRUE positives, 0 false** |
| 5 | [`how-to-verify-a-platform-contract.md`](../../skills/how-to-verify-a-platform-contract.md#L392) V-level section | **APPLIED** as approved | N/A — instruction change |
| 6 | [`improvement-agent.md`](../../agents/improvement-agent.md#L125) step 6 + step 8 | **APPLIED** as approved | `verify-improvement-log.py --check` no longer reports `IMP-0484` as `unread` |

### Change 2 — what was already done, and what was not done on purpose

**The `--allow` deletion was already live and was verified, not re-applied.** A concurrent
`development-agent` dispatch removed it in commit `2d34e9a` and the step now reads
`python3 scripts/verify-code-app-data-sources.py src/code-apps/trustee-review-portal` with no
flag. Confirmed by reading the config, and by running the gate: it returns OK unaided.

**The register migration was NOT performed, and that is the correct outcome.** There is no longer
an exemption to migrate — the underlying defect is fixed in source, so the gate is green on its
own. Adding a `gate-baselines.json` entry for a finding that no longer exists would create the
very debt the register exists to age; `gate_baseline.py`'s own `unused` property calls this out as
*"debt that has been paid and not recorded"*.

**One thing change 2 did NOT foresee and this apply pass fixed.** The step's comment block still
instructed readers *"To accept it temporarily, add `--allow rev_roundfinances=<reason and owner>`
HERE"* — a live instruction to use a flag that change 1 had just turned into a usage error. It now
names the register instead. Correcting it in the same change is `C-TECH-053`'s own rule about a
correction landing in every place that states the fact.

### Change 4 — the measurement, and one thing that was compelled rather than chosen

**12 findings, 12 true positives, 0 false.** Each was adjudicated individually and each is a real
deliverable the summary makes claims about: two solution `Entity.xml` files, an OptionSet, three
`seed-round-statistics-*.ps1` scripts, three `verify-*.py` scripts, a Pester suite, a known-bad
fixture, and the improvement-id allocator. All twelve were confirmed untracked **and not
gitignored** (`git check-ignore` on each — an ignored path is a fixture, not delivered source,
which is `IMP-0410`'s lesson).

**Polarity checked, because a gate that scores a corrected document worse is a wrong design.** Run
against the tracked set before the correcting commit and after it, holding the document constant:
**15 findings before, 12 after.** Committing artefacts strictly reduces the count. This design
cannot invert the way the phrase-based candidate would, because git's answer is a fact about a
commit and a retained erratum phrase is not.

**Wiring it was compelled, and is reported rather than slipped in.** The change table did not
mention wiring, but `verify-build-config.py`'s `suite-gate-is-not-a-step` check fails any
`verify-*.py` in `scripts/` that no step invokes — so leaving it unwired would have turned a HARD
preflight red on the build queued behind this review. It is wired **SOFT** via `--warn-only`,
which exits 0 and cannot halt a build, exactly the mechanism `derived-counts` uses. Build config
re-validated: **PASS, 68 steps, 53 gates.** The registered `improvement-agent-verify-script-count`
claim moved 51 → 52 in the same change and `verify-derived-counts.py` confirms it current.

### The three entries this review processed, and their state

- **[`IMP-0487`](../../logs/improvement-log.jsonl) and
  [`IMP-0488`](../../logs/improvement-log.jsonl) — APPLIED and closed.** Both `observable_at` V1,
  both carrying an `evidence_grep` needle pointing at the substance of the change that closed them.
- **[`IMP-0485`](../../logs/improvement-log.jsonl) — OPEN.** V4, and the reviewer's screen is
  unrepaired: `logs/pipeline.log` records **no `pac code push` after 14:43**, so DEV still serves
  the pre-fix bundle even though the source fix is committed. Approved `revisit_when` recorded
  verbatim.
- **[`IMP-0486`](../../logs/improvement-log.jsonl) — OPEN, with its trigger now half-satisfied.**
  Commit `2d34e9a` committed the design-system conversion and `ds.module.css` is tracked, so the
  first clause of *"the conversion is committed and the reviewer sees the refreshed UI in DEV"* is
  true and the second is not. The trigger is recorded **verbatim as approved** and the current
  state is annotated in `deferred_reason` — the wording is what the reviewer approved, and
  rewriting an approved trigger to match what has since become true is not this agent's to do.

**Queue effect.** `python3 scripts/verify-improvement-log.py --check` now exits **0**: no blocker
trigger, and the batch trigger is below threshold. Digest regenerated and confirmed current —
487 entries, 486 distinct lessons, 585 lines, measured after the fact and never predicted.
