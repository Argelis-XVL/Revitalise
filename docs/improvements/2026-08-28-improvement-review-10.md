# Improvement Review 40 — 2026-08-28

**Status:** ~~AWAITING `APPROVE IMPROVEMENTS` — nothing in this document is on disk.~~
**APPLIED 2026-08-28**, approved by Xander Lykopoulos. All 13 changes are on disk; the record,
the four deviations and the verification results are in §9.
**Findings processed:** 11 `NEW` → 10 clusters
**Scope:** the 11 entries the gate reports as `unread`. The 84 `reviewer-deferred` entries are
left alone and reported in §5, per [`improvement-agent.md` L103](../../agents/improvement-agent.md#L103).
**WBS:** `wbs:6.9` for the ten delivery-sourced findings; the eleventh
([`IMP-0471`](../../logs/improvement-log.jsonl)) is `feature:system` and serves no WBS task —
it is this system's own gate, not contracted work, so no change-order question arises
([`C-COM-002`](../../constraints/commercial/commercial-constraints.md#L35), which puts work tagged
`system` outside contractual scope explicitly).

---

## Summary

Eleven unread findings, ten clusters, **13 proposed changes, no new constraints and no new
scripts** — every mechanical change extends a gate that already runs. Three designs were measured
against the real corpus and **two of them were cut by the measurement**: the docstring check in §6a
had its polarity inverted in its obvious form (it scored the *corrected* file worse than the
defective one), and the PowerShell-assertion gate in §6c measures at **0 true positives across 221
candidate lines**, so it is declined in favour of a knowledge line.

The one thing that needs your judgement rather than my disposal is in §7: a brand-new mechanism
from the last review — the `contests` edge — was used by another agent within hours and produced a
**false warning on a correct, applied lesson**. I can fix the data and require a field; whether
that is enough, or whether the edge needs a sibling, is a call about how much schema this log
should carry.

---

## 1. Regression check — did review 39's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| **The `contests` edge kind** — [`generate-known-failure-modes.py` L385](../../scripts/generate-known-failure-modes.py#L385) · [`verify-improvement-log.py` L388](../../scripts/verify-improvement-log.py#L388) — change 1 | 2026-08-28 | `two-recorded-lessons-contradict-each-other` | **YES — and by MISUSE, within hours** | **Working mechanically, wrong in the field.** See below |
| [`verify-tad-coverage.py` L851](../../scripts/verify-tad-coverage.py#L851) assertion (d) buckets — change 2 | 2026-08-28 | `gate-cannot-fail` | **NO** | **No evidence either way.** Nothing in this batch touches it |
| [`power-automate.md` L112](../../knowledge/technology/power-automate.md#L112) — the `xpath`/`sum` block — change 3 | 2026-08-28 | `platform-fact-groundtruthed` | **YES — [`IMP-0473`](../../logs/improvement-log.jsonl), `rework`** | **Working and incomplete in a way only a build could reveal.** See below |
| [`power-automate.md` L121](../../knowledge/technology/power-automate.md#L121) — the `coalesce` worked example — change 4 | 2026-08-28 | `two-recorded-lessons-contradict-each-other` | **NO** | **Working.** The shipped flow carries the pattern |
| [`lead-agent.md` L135](../../agents/lead-agent.md#L135) rule 3 widened — change 5 | 2026-08-28 | *a cited authority does not say what it was cited for* | **NO, and one adjacent near-miss** | **Prose. See below** |
| [`tad-deferrals.json` L44](../../contract/tad-deferrals.json#L44) rewritten — change 6 | 2026-08-28 | `finding-diagnosis-unverified` | **NO** | **Working.** The gate reads the key and acquits three |

The four audit questions, for the two recurrences:

- **The `contests` edge — was the change prose or a gate?** Both: a generator change plus one line
  in [`how-to-log-an-improvement.md` L128](../../skills/how-to-log-an-improvement.md#L128).
  **Did it run?** Yes, and it rendered correctly — the marker is on disk at
  [`known-failure-modes.md` L404](../../logs/known-failure-modes.md#L404). **So what recurred?**
  Not the class the edge was built for. The *edge itself was set wrongly by the next agent to use
  it.* [`IMP-0476`](../../logs/improvement-log.jsonl) set `contests: IMP-0142`, and the digest now
  tells every future reader that
  [`IMP-0142`](../../knowledge/technology/coding-standards.md#L64)'s lesson is *"disputed … and
  NEITHER has been re-tested"*. Both clauses are false: `IMP-0476` does not dispute `IMP-0142`, it
  says the property is **broader than the cmdlet `IMP-0142` named**; and `IMP-0476` was found by a
  tool, so it was tested. **This is the sharpest kind of regression:** a mechanism that works
  exactly as designed and is *understood* wrongly on first contact, which no fixture can catch.
  Cluster H.
- **The knowledge edit on `xpath`/`sum` — was it prose?** Yes, and `IMP-0473` is a recurrence of
  the class against a **third emptiness the edit did not model**. Review 39 recorded two dangerous
  inputs (an empty node-set → `0`; any non-numeric leaf → `NaN`). The build then met a third: an
  empty **array**, where `join()` yields `''` and the surrounding element literals turn it into the
  `NaN` case. **Altitude:** the mechanical half is already on disk and is not mine — the dispatch
  pinned the guard into
  [`verify-flow-trigger-body-isolation.py` L132](../../scripts/verify-flow-trigger-body-isolation.py#L132)
  as part of check B1's exempt template, which I verified by reading `_SCALAR_REDUCTION` and by
  running the gate. So this review adds only the knowledge the next flow author needs. Cluster F.
- **The `lead-agent.md` near-miss.** [`IMP-0470`](../../logs/improvement-log.jsonl) is the same
  family — a dispatch brief stating something the receiving agent had to correct — but the object
  was a **command line**, not a cited fact, so rule 3 as widened does not reach it. Cluster C
  extends the *quoting* obligation rather than rule 3, because the two failures have different
  remedies: a citation is checked by reading, a command line is checked by running.
- **Did the closure evidence match the level each defect was visible at?** Yes for review 39.
  Checked against this batch: **`IMP-0473` and `IMP-0477` are both `observable_at: V5` and this
  review reaches neither**, so §5 leaves both open with triggers rather than closing them on a
  document. That is [`IMP-0225`](../../logs/known-failure-modes.md#L37)'s rule applied to my own
  output.

**And the one thing this audit establishes.** Review 39 measured its `contests` edge at *"1 finding
/ 1 true / 0 false"*, and that measurement was correct. It measured whether the edge **renders**;
nothing measured whether an agent would **set it correctly**, and that is where it failed inside a
day. A new schema field is a new instruction to every future agent, and its first outside use is
the only test that counts.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: a wired gate's own docstring denies that it is wired  (x1 unread: IMP-0465)
           — class `approved-document-internally-inconsistent` x21; same property as IMP-0322
Altitude:  CLASS, and the general form was CUT DOWN by its own measurement.
Ladder row: "a tool could catch it mechanically" + "second instance -> generalise"
Becomes:   the instance docstring corrected, plus one preflight assertion in
           scripts/verify-build-config.py — the gate that already enumerates every step's
           command and already owns is_gate()
Retires:   nothing
Cites:     IMP-0465, IMP-0322
Residual:  A status claim written AFTER the docstring's first blank line is not seen. That is
           the narrowing the measurement compelled, not a preference: the unnarrowed form
           scores the CORRECTED file worse than the defective one (§6a). And nothing checks the
           OTHER half of IMP-0322 — a docstring that undercounts its own checks — because a
           check count has no single derivable home in these scripts.
```

```
CLUSTER B: an inherited risk acceptance annexed a data shape nobody reasoned about
           (x2 unread: IMP-0468, IMP-0469)
Altitude:  KNOWLEDGE + SKILL. The substantive contradiction is already CLOSED by the reviewer's
           own k=5 answer to OQ-043, so what is left is the durable lesson, not the decision.
Ladder row: "one instance, but the cause is general and a human needs to know it"
Becomes:   skills/data-classification.md — a step for inheriting an acceptance (name its stated
           basis; check the basis holds for the new shape); knowledge/technology/security-model.md
           — rev_setting carries two kinds of key, and which kind k=5 is
Retires:   nothing
Cites:     IMP-0468, IMP-0469
Residual:  THE MECHANICAL FORM IS DECLINED AND ROUTED, NOT TAKEN. A build check that every
           rev_setting key is classified tunable-or-control needs a `classification` field on
           every settingRows entry across three deploymentSettings files — a change to the seed
           payload shape, which is delivery work under provisioning/ and not this agent's to
           author. Put to you in §7.
```

```
CLUSTER C: a quoted command line does not match the script's argv contract  (x1 unread: IMP-0470)
Altitude:  INSTANCE for the prompt half (no gate is possible — review 39 §6d settled that a
           Task prompt is not a file), CLASS for the legibility half.
Ladder row: "an agent had the information and still did the wrong thing" -> an agent-file edit;
           plus "a tool could catch it mechanically" for the failure's SHAPE
Becomes:   agents/development-agent.md — quote a verification command with every required
           argument, copied from the script's own usage line; and the 7 scripts that answer a
           usage error by printing their WHOLE docstring print a usage line instead
Retires:   nothing
Cites:     IMP-0470
Residual:  The prompt half stays uncheckable, exactly as review 39 recorded. The script half
           makes the failure legible; it does not stop a brief being written wrong.
```

```
CLUSTER D: the citation-stamp check decides INTENT by matching a phrase  (x1 unread: IMP-0471)
           — class `gate-fires-on-nothing` x7, and THIRD instance of this specific over-firing
Altitude:  CLASS. The altitude rule forbids the instance patch, which is what makes this the
           most valuable change in the batch: the two prior fixes each WIDENED the recogniser
           (IMP-0196 added the heading rule, review 19 added the paragraph rule), so the next
           unmatched phrasing was guaranteed.
Ladder row: "the system's own memory failed" -> a read-path change
Becomes:   scripts/verify-improvement-log.py — an explicit, machine-readable `Deferred:` line
           declares disposition for the WHOLE document; the phrase cues stay as a fallback so
           no existing document regresses. Plus the line in the review template.
Retires:   considered SCOPE_DISCLAIMER's phrase list and RETAINED it — see §4
Cites:     IMP-0471, IMP-0196
Residual:  AN EXPLICIT DECLARATION IS AN EXPLICIT ESCAPE HATCH. An author can write
           `Deferred:` over every id and silence the check. That is already true of the prose
           cue; the difference is that the new form is greppable
           (`grep -n '^Deferred:' docs/improvements/*.md`), so abuse is visible where a buried
           sentence was not. The control on abuse stays the no-silent-caps rule and a human
           reading the draft — the same control that catches everything else this agent writes.
```

```
CLUSTER E: an ADR reasoned about ONE of the gates over its artefact  (x1 unread: IMP-0472)
           — class `gate-scope-mismatch` x12
Altitude:  INSTANCE at the agent-file level, deliberately. No gate can read an ADR's list of
           gate interactions and compare it against the build config: the list is prose.
Ladder row: "an agent had the information and still did the wrong thing"
Becomes:   agents/architect-agent.md — when an ADR specifies expression-level mechanism for an
           artefact that already has build gates, enumerate those gates FROM
           config/<slug>-build.yml and state, per gate, whether the mechanism trips it
Retires:   nothing
Cites:     IMP-0472
Residual:  The obligation is discharged by an agent choosing to do it. What makes it more than
           a wish is that the enumeration has a mechanical SOURCE — the build config's own
           steps block — so a reviewer can check the ADR against a list rather than against
           the author's memory.
```

```
CLUSTER F: XPath sum() has a THIRD emptiness  (x1 unread: IMP-0473) — class
           `platform-contract-guessed-not-groundtruthed` x50
Altitude:  KNOWLEDGE only. The gate half is ALREADY ON DISK and is not this review's to claim.
Ladder row: "one instance, but the cause is general and a human needs to know it"
Becomes:   knowledge/technology/power-automate.md — the empty-ARRAY case distinguished from the
           blank-VALUE case, the safe concat shape that is now gate-enforced, the nested-add()
           escape path, and a correction to the sentence that says no gate reads inside an
           xpath() expression (one now does)
Retires:   nothing
Cites:     IMP-0473, IMP-0467, IMP-0466
Residual:  IMP-0473 is `observable_at: V5` and NOT CLOSED by this review (§5). Also: its four
           measured results are against **libxml2**, and Logic Apps evaluates xpath() with the
           **.NET** XPath library. Both are XPath 1.0 conformant and the results follow from
           the specification, so the knowledge text states the measurement's engine rather
           than implying a run on this tenant.
```

```
CLUSTER G: a PowerShell assertion that silently asserts something else
           (x2 unread: IMP-0475, IMP-0476) — classes `gate-cannot-fail` x38 and
           `two-invocation-paths-disagree` x12, ONE property
Altitude:  KNOWLEDGE, and the gate is DECLINED ON MEASUREMENT rather than on judgement.
Ladder row: "one instance, but the cause is general and a human needs to know it"
Becomes:   knowledge/technology/coding-standards.md — both rules in the section that already
           carries IMP-0142's precedence trap, with the vacuous-pass direction named
Retires:   nothing
Cites:     IMP-0475, IMP-0476, IMP-0142
Residual:  Measured at ZERO true positives on today's tree — 54 -BeLike assertions of which 18
           negative, none with a bracketed literal needle; 167 `+`-terminated lines in .ps1,
           none adjudicated true (§6c). A gate here would be inert, and the ladder excludes
           "it might happen". The real home for a THIRD instance is named: the PowerShell AST,
           which src/tests/provisioning/ScriptContract.Tests.ps1 already parses. And the
           interpolated case — a needle whose bracket arrives through a variable — is
           undetectable statically in any design.
```

```
CLUSTER H: the `contests` edge was misread on its first use outside the review that built it
           (x1: IMP-0476's edge) — a regression against review 39 change 1
Altitude:  CLASS, and it is a DEFINITION problem rather than a rendering one.
Ladder row: "the system's own memory failed" -> a read-path change; the schema half is
           mechanical
Becomes:   the false edge removed from the log; `contests` required to carry a
           `contests_clause` naming the clause it disputes, validated for PRESENCE only; and
           the one-line test in how-to-log-an-improvement.md — a contest says the earlier
           lesson is WRONG, and "true but too narrow" is not a contest
Retires:   nothing
Cites:     IMP-0476, IMP-0142, IMP-0460, IMP-0412
Residual:  A REQUIRED FIELD CANNOT CHECK THAT THE CLAUSE IS REALLY DISPUTED — that is prose
           semantics and no gate will ever read it. What the field does is force the author to
           quote the clause, which is the step at which "there isn't one" becomes visible. This
           is the weakest mechanical link in the batch and §7 puts the alternative to you.
```

```
CLUSTER I: a declared exception's blast radius is not measured  (x1 unread: IMP-0477)
           — class `hard-gate-red-on-pre-existing-debt` x2, but a DIFFERENT property from
           IMP-0439's, so this is a first instance and an instance fix is allowed
Altitude:  INSTANCE, mechanical, and it asserts on a VALUE (a count of descendant actions).
Ladder row: "a tool could catch it mechanically"
Becomes:   scripts/verify-flow-definition-language.py check 7 prints, per suppressed
           exception, how many descendant actions it hides
Retires:   nothing
Cites:     IMP-0477, IMP-0349, IMP-0439
Residual:  Printing a number does not fail a build, and it should not — the exception is owned,
           dated and expires 2026-09-30. What it changes is that growth from 20 hidden actions
           to 104 is visible on the run that grew it. IMP-0477 stays OPEN at V5 (§5): the
           clearing action is a future dispatch's, and it needs the source-level regression
           test IMP-0346 demands in the same change.
```

```
CLUSTER J: an ADR's cost estimate was carried as though derived  (x1 unread: IMP-0474)
           — class `hand-maintained-count-drifts-from-source` x24
Altitude:  NOTHING. The reporting dispatch proposed no rule change and I agree with it.
Ladder row: row 1 — "one instance, specific to one feature, no general mechanism"
Becomes:   no file change. The lesson is in the digest already; the corrected figure is in the
           flow's notes.md and the Dev Summary
Retires:   nothing
Cites:     IMP-0474
Residual:  THE MECHANICAL FORM WAS CONSIDERED AND DECLINED WITH A REASON. Registering ADR-039's
           action count in scripts/derived-counts-registry.json would make it self-checking —
           and the ADR is a FROZEN approved document whose estimate is deliberately left as
           written, so the registered claim would open a SOFT gate permanently red against a
           document nobody is authorised to edit. That is IMP-0439's shape, and declining it
           is the same call review 39 made about the ADR's own superseded reasoning.
```

---

## 3. Changes proposed

| # | Type | Target | What | Cites | Provable? |
|---|---|---|---|---|---|
| 1 | script | [`verify-doc-line-links.py` L2](../../scripts/verify-doc-line-links.py#L2) | Docstring opens by stating it **is** wired as the HARD `doc-line-links` step; the measured-candidate history moves below the first blank line, marked as history | IMP-0465 | **YES** — the assertion is the build config's own [L1230](../../config/revitalise-grant-automation-build.yml#L1230) |
| 2 | gate extension | [`verify-build-config.py` L396](../../scripts/verify-build-config.py#L396), inside the already-HARD [`preflight-build-config` step](../../config/revitalise-grant-automation-build.yml#L107) | A script invoked by a step's `command` may not deny its own wiring in its docstring's **opening clause**. Reuses `is_gate()`'s own enumeration | IMP-0465, IMP-0322 | **YES** — **1 finding / 1 true / 0 false** over 44 wired scripts; the unnarrowed form is **2 / 1 / 1** and has inverted polarity (§6a) |
| 3 | skill | [`data-classification.md` L25](../../skills/data-classification.md#L25) | Inheriting an existing risk acceptance: name its **stated basis**, check that basis is present for the new data shape, record the check. A conditional mean, a cross-tabulation and a filtered subgroup each need their own consideration even where a marginal over the same column is accepted | IMP-0468 | Prose. The instance is settled by the reviewer's k=5 answer; this is the durable half |
| 4 | knowledge | [`security-model.md` L119](../../knowledge/technology/security-model.md#L119) | `rev_setting` carries **two kinds of key** — free tunables under NFR-019, and values encoding a reviewer risk decision, which name their deciding open question in their own description. Records that `RoundStatisticsMoneyMeasureMinimumPopulation` is k=5 by decision, and that an absent row withholds the four measures (fail-safe, but not the approved behaviour, and a DEV/TST divergence renders the same round differently per environment) | IMP-0469 | Prose + a live fact. The mechanical form is routed in §7 |
| 5 | agent file | [`development-agent.md` L104](../../agents/development-agent.md#L104) | When a dispatch prompt quotes a verification command for a sub-agent to run verbatim, quote it with **every required argument**, copied from the script's own usage line — never a shortened form | IMP-0470 | Prose, necessarily (a Task prompt is not a file) |
| 6 | script × 7 | [`verify-code-app-column-bindings.py` L232](../../scripts/verify-code-app-column-bindings.py#L232) and the 6 siblings listed in §6b | A usage error prints the docstring's **first line plus a usage line naming the missing argument**, not all 98 lines. `--help` keeps the full docstring | IMP-0470 | **YES** — measured before and after by execution on all 7 (§6b) |
| 7 | gate extension | [`verify-improvement-log.py` L1281](../../scripts/verify-improvement-log.py#L1281) | A line matching `^Deferred:` (or `^Not processed:`) followed by ids declares those ids not-processed for the **whole document**, read before any prose scan. `SCOPE_DISCLAIMER` stays as a fallback | IMP-0471, IMP-0196 | **YES** — byte-identical warning set across all 50 documents (inert without data), plus a fixture proving it recognises the line (§6d) |
| 8 | template | [`improvement-review-template.md` L106](../../templates/improvement-review-template.md#L106) | Section 5 carries the `Deferred:` line as a required field, so the declaration has one home rather than being re-derived per review | IMP-0471 | **YES** — this document carries the line |
| 9 | agent file | [`architect-agent.md` L59](../../agents/architect-agent.md#L59) | When an ADR specifies expression-level mechanism for an artefact that already has build gates, **enumerate the gates over that artefact from `config/<slug>-build.yml`** and state per gate whether the mechanism trips it — rather than naming whichever gate came to mind. Two gates guarded this flow and the ADR reasoned about one | IMP-0472 | Prose, with a mechanical source for the enumeration |
| 10 | knowledge | [`power-automate.md` L127](../../knowledge/technology/power-automate.md#L127) | The **third emptiness**: `join()` over an empty array is `''`, which the surrounding `<v>` literals turn into the `NaN` case — so "the presence filter removes the `NaN` case" is true only of blank values *inside* a non-empty collection. Adds the safe shape `concat('<r>', if(empty(body('S')), '', concat('<v>', join(body('S'),'</v><v>'), '</v>')), '</r>')`, the nested-`add()` escape path, and **corrects [L145](../../knowledge/technology/power-automate.md#L145)**, which says no gate reads inside an `xpath()` expression | IMP-0473, IMP-0467 | **YES** for the enforcement half — `_SCALAR_REDUCTION` read and the gate run. The four sum() results are cited to their engine, not to this tenant |
| 11 | knowledge | [`coding-standards.md` L64](../../knowledge/technology/coding-standards.md#L64) | Two rules in the section that already owns `IMP-0142`'s trap: (a) `-BeLike` is **wildcard** matching, so a needle containing `[` `]` — which every `item()?['column']` expression does — must use `-Match ([regex]::Escape(...))`, and **`-Not -BeLike` passes vacuously** where `-BeLike` fails loudly; (b) `IMP-0142`'s rule generalised from `Write-Output`/`-f` to the **parse property** — a string concatenation continued across a line break inside *any* cmdlet parameter argument re-parses the statement | IMP-0475, IMP-0476, IMP-0142 | Prose, and the gate is declined on measurement (§6c) |
| 12 | data + gate + skill | [`improvement-log.jsonl`](../../logs/improvement-log.jsonl) · [`verify-improvement-log.py` L388](../../scripts/verify-improvement-log.py#L388) · [`how-to-log-an-improvement.md` L128](../../skills/how-to-log-an-improvement.md#L128) | Drop the false `contests: IMP-0142` from `IMP-0476`; require a `contests` edge to carry a **`contests_clause`** quoting the clause it disputes (presence validated, semantics not); state the test — *a contest says the earlier lesson is **wrong**; true-but-too-narrow is not a contest, it is a widening* | IMP-0476, IMP-0142, IMP-0460 | **YES** for the data and the field. The definition half is prose — §7 |
| 13 | gate extension | [`verify-flow-definition-language.py` L574](../../scripts/verify-flow-definition-language.py#L574) | Check 7 prints, per suppressed exception, the **count of descendant actions it hides**, so an exception growing from 20 to 104 is visible on the run that grew it rather than at its expiry | IMP-0477, IMP-0349 | **YES** — the gate runs today and reports 3 suppressed exceptions, none with a count (§6e) |

**No new script, so the derived `verify-*.py` count stays at 51** and
[`improvement-agent.md` L356](../../agents/improvement-agent.md#L356) needs no edit. Derived at
draft time, to be re-derived at application: `ls scripts/verify-*.py | wc -l` → **51**.
**No new constraint**, against a cap of 3. Live constraint rows: **80**; retired: **10** — both
derived with the commands at
[`how-to-promote-a-finding.md` L101](../../skills/how-to-promote-a-finding.md#L101), not retyped.

Every mechanical change extends a gate that already asserts the neighbouring rule: change 2 lives
in the preflight that already enumerates step commands, change 7 and change 12 live in the
validator that already owns the four-state model and the `corrects` edge, and change 13 lives in
the check whose exception it measures.

---

## 4. Retirement — considered, one candidate, retained for cause

- **`SCOPE_DISCLAIMER`'s phrase list at
  [`verify-improvement-log.py` L225](../../scripts/verify-improvement-log.py#L225)** — the genuine
  candidate, and the one change 7 would let me delete. **Retained**, and the reason is a
  measurement rather than caution: all **50** documents in `docs/improvements/` declare their
  non-scope in prose, because the explicit line does not exist yet. Deleting the phrase list in the
  same change that introduces its replacement would fire warnings across the whole corpus for
  documents nobody is going to rewrite — [`IMP-0439`](../../logs/known-failure-modes.md#L65)'s
  shape exactly. It is demoted to a **fallback** and documented as one, and its retirement becomes
  correct once reviews carry the explicit line. Recorded here so the next review can act on it
  rather than rediscover it.

No other candidate. I checked the three gates this review touches for rules that change 7 or
change 2 subsume, and found none: change 2 asserts a property nothing asserted before, and change
13 adds output to a check whose verdict is unchanged.

---

## 5. Findings left unprocessed, and what this review does NOT close

**Deferred:** IMP-0467, IMP-0274, IMP-0290, IMP-0298, IMP-0320, IMP-0437

That line is change 8's new field and it means one thing precisely: **ids this document NAMES and
does not PROCESS.** All six are `reviewer-deferred` and appear below only as context. It is
deliberately *not* the list of ids left open — `IMP-0473` and `IMP-0477` are processed by this
review and merely not closed, which is a different state recorded a different way, and conflating
the two is what would make the new field as loose as the phrase cue it replaces.

**`IMP-0473` and `IMP-0477` are processed and NOT CLOSED.** Both are **`observable_at: V5`** and
this review reaches V1, so the reason is
[`IMP-0224`](../../logs/known-failure-modes.md#L220)/`IMP-0225`'s: an entry closed on a document
that says it was fixed is a claim, not a result. Their durable changes land, they get `reviewed_in`
and a `deferred_reason`, and they stay `NEW` with triggers:

- **`IMP-0473`** — the guard is on disk and HARD-enforced, and the knowledge lands as change 10.
  `revisit_when`: a round with an empty break type is computed live and the thirteen metrics are
  observed present. Needs a real round; nobody in this session can make that observation.
- **`IMP-0477`** — change 13 makes the widening visible; it does not clear the exception.
  `revisit_when`: the next dispatch on `REVPortalRoundStatistics` descends `result()` into
  `Switch_on_open_round_count` and then into `Condition_page_cap`, **with the source-level
  regression test in the same change**, before the declared expiry of 2026-09-30.

**The 84 `reviewer-deferred` entries are out of scope by activation step 2** and none of them is
processed in this review. Three things about them the gate reports and you should see:

- **[`IMP-0467`](../../logs/improvement-log.jsonl)'s trigger has FIRED, and I am disposing of it
  rather than re-deriving it.** It asked *"the next improvement review designs check 8 ONCE,
  covering both this entry's xpath-sum guard and `IMP-0460`'s throwing-call rule, after A-FLOW-08
  has settled which mechanism the money measures use."* A-FLOW-08 has settled — the shipped
  mechanism **is** `xpath` — and the xpath-sum half **no longer needs check 8**, because the
  delivery dispatch pinned the guard into check B1's exempt template
  ([`_SCALAR_REDUCTION`](../../scripts/verify-flow-trigger-body-isolation.py#L132), verified by
  reading and by running). Building check 8 for it would be two gates asserting one rule, which is
  [`IMP-0443`](../../logs/known-failure-modes.md#L35)'s defect. What remains of check 8 is
  `IMP-0460`'s rule alone, and that is still blocked on a live designer run to settle `if()`
  semantics. So check 8 is **not designed in this review**, and the reason has changed from *"the
  mechanism is unsettled"* to *"half is enforced elsewhere, half needs V5"*. Change 12 does not
  touch this; only the record needs updating, and I propose doing so on application.
- **[`IMP-0274`](../../logs/improvement-log.jsonl) still names no `revisit_when`** — a deferral
  with no trigger to come back is a decision never to do it. Not processed in this review; flagged
  because the gate flags it on every run and nothing has cleared it.
- **Four entries carry `corrects` warnings that only a stamp will clear** — `IMP-0290`,
  `IMP-0298`, `IMP-0320`, `IMP-0437`. Each is already processed by a named review document; the
  remedy is stamping the correcting entry, not a session. Not processed in this review.

**One live gate finding this review routes rather than fixes.**
[`verify-derived-counts.py`](../../scripts/verify-derived-counts.py) exits 1 **right now** with
three drifted claims, and because the step is SOFT nothing has reported them: two places in the
Dev Summary say **67** secured columns where source says **68**
([L4611](../../docs/development/revitalise-grant-automation-dev-summary.md#L4611) and
[L4768](../../docs/development/revitalise-grant-automation-dev-summary.md#L4768)), and the REV
Trustee role header says **51** where source says **52**
([`REV Trustee.xml` L73](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Trustee/REV%20Trustee.xml#L73)).
The cause is the concurrent `wbs:6.9` work adding secured columns. All three targets are delivery
artefacts under `docs/development/` and `src/solutions/`, so they are **not this agent's to edit** —
this is the routing, and it belongs to whoever next owns those files.

---

## 6. Measurements

### 6a. The docstring check — its obvious form has inverted polarity

Two candidates, both run over the **44 `verify-*.py` scripts named by a `command:` in the build or
pipeline config**, and then over the corrected text of the one true positive.

| Candidate | Defective tree | Corrected file | Verdict |
|---|---|---|---|
| **Unnarrowed** — the negative-wiring pattern anywhere in the docstring | **2 findings / 1 true / 1 false** | **FINDING** | **WRONG.** Polarity inverted |
| **Narrowed** — the docstring's **opening clause** only (text before the first blank line) | **1 finding / 1 true / 0 false** | **clean** | **Correct** |

The false positive the narrowing removes, by name:
[`verify-build-config.py` L90](../../scripts/verify-build-config.py#L90) — *"leave the step
unwired, with the reason recorded where the next agent will read it"* — which is advice to the
reader about **other** steps, not a claim about its own wiring.

**And the corrected-file column is the whole point.** This repository's correction convention
*retains* withdrawn wording as history, so the corrected docstring still contains
*"CANDIDATE (scratchpad, not wired)"* — below the first blank line, marked as history. The
unnarrowed candidate therefore scores the **corrected** file as a finding and the **defective** one
as a finding too: fixing the defect would not clear the gate. That is the inverted polarity
[`improvement-agent.md` L417](../../agents/improvement-agent.md#L417) describes, measured here for
the sixth recorded time. The opening-clause scope is the one position where a correction
necessarily *removes* the phrase rather than retaining it, which is why it is the narrowing and not
a stylistic choice.

### 6b. The usage-error shape — 7 scripts, measured by execution

The one-argument invocation quoted in the `wbs:6.9` dispatch brief was run: **exit 2, 98 lines of
output**, the entire module docstring. The two-argument form exits 0 with a single OK line. Both
executed this session, not read.

Seven scripts answer a usage error the same way (`print(__doc__)`), and this is the full list, so
change 6 is bounded rather than sampled:
[`verify-code-app-column-bindings.py` L232](../../scripts/verify-code-app-column-bindings.py#L232),
[`verify-column-security-membership.py` L91](../../scripts/verify-column-security-membership.py#L91),
[`verify-field-security-coverage.py` L234](../../scripts/verify-field-security-coverage.py#L234),
[`verify-declared-property-reaches-creation-path.py` L216](../../scripts/verify-declared-property-reaches-creation-path.py#L216),
[`verify-role-privilege-ownership.py` L360](../../scripts/verify-role-privilege-ownership.py#L360),
[`verify-guid-syntax.py` L254](../../scripts/verify-guid-syntax.py#L254),
[`verify-solution-root-components.py` L135](../../scripts/verify-solution-root-components.py#L135).

Each edit is one line and touches only the usage-error branch. Five of the seven are HARD build
steps, so the proof obligation at application is to execute all seven **with correct arguments**
and confirm the success path and exit code are unchanged, then with wrong arguments and confirm
exit 2 with a short message.

### 6c. The PowerShell-assertion gate — declined at zero true positives

| Candidate | Corpus | Findings | True | Verdict |
|---|---|---|---|---|
| `-BeLike` with a bracketed literal needle | `src/tests/**/*.ps1` — 54 `-BeLike` assertions, **18** of them `-Not -BeLike` | **1** | **0** | The single hit is the **comment** at [`RoundStatisticsContract.Tests.ps1` L203](../../src/tests/solutions/RoundStatisticsContract.Tests.ps1#L203) warning against the pattern. The three real assertions were fixed in the dispatch that found them |
| A `+` continued across a line break | `src/tests/` and `provisioning/` `*.ps1` — **167** `+`-terminated lines | **167** | **0** | Adjudicated: the safe forms dominate — concatenation already inside parens, and `++` increments. The unsafe shape needs "inside a named parameter argument, not inside parens", which a grep cannot decide |

**221 candidate lines, 0 true positives.** A gate here would be inert today and noisy tomorrow, and
[`how-to-promote-a-finding.md` L145](../../skills/how-to-promote-a-finding.md#L145) excludes *"it
might happen"*. The knowledge line is the ladder's answer for a one-instance-with-a-general-cause
finding, and the mechanical home for a third instance is named rather than left to be rediscovered:
the PowerShell AST, which
[`ScriptContract.Tests.ps1`](../../src/tests/provisioning/ScriptContract.Tests.ps1) already parses.

**The dangerous direction, stated because no failure will reveal it:** `-BeLike` with a bracketed
needle fails *loudly*, which is how `IMP-0475` was found. `-Not -BeLike` with the same needle
**passes vacuously** — an absence assertion whose needle can never match is a test that cannot
fail. Eighteen negative assertions exist today and none is in that state; a needle whose bracket
arrives through an interpolated variable would be undetectable by any static design.

### 6d. The `Deferred:` line — inert without data, exact with it

The obligation at application is the same two-part proof review 39 used for the `contests` edge:

1. **Inert:** run the patched validator over the current tree and confirm the warning set is
   **byte-identical** to the unpatched one. No document in `docs/improvements/` contains a
   `^Deferred:` line today except this one, so across the other **49** the new path must not change
   a single verdict.
2. **Exact, by fixture rather than by this document.** The six ids on §5's `Deferred:` line are all
   `reviewer-deferred`, and `check_citation_stamps()` only warns on `unread` — so **this document
   cannot demonstrate the change**, and saying otherwise would be the false measurement
   [`IMP-0426`](../../logs/known-failure-modes.md#L41) records. The proof is a selftest fixture: an
   `unread` id named once, in a paragraph carrying **no** phrase cue, under a `Deferred:` line —
   which warns today and must not warn after. Both negative cases must still fire: an id cited as
   processed stays a processing claim even when the `Deferred:` line also names it (the stronger
   signal wins, as it already does for headings), and an id in neither position still warns.

Note what this does **not** do: it does not remove the phrase-cue path, so a review that declares
non-scope only in prose behaves exactly as it does today. That is what makes the change safe to
apply against a 50-document corpus in one step.

### 6e. Check 7's suppressed exceptions — three today, none carrying a size

Executed against `src/solutions/RevitaliseGrantAutomation`: the gate exits **OK** and prints three
`EXCEPTION (reported, not failed)` blocks, each naming its owner, declaration date, expiry and
clearing action, and the OK line explicitly excludes them from what it certifies. What no line
carries is **how much each one hides** — which is precisely `IMP-0477`: the
`REVPortalRoundStatistics` exception now sits between the failure alert and 84 more actions than
when it was declared, and no verdict changed. The three exceptions are on
`REVIntakeWordPressToDataverse`, `REVPortalRoundStatistics` and `REVScoringCalculateAndFlag`, all
owned by `automation-agent`, all declared 2026-08-28, all expiring 2026-09-30.

Change 13 adds one number per block. It cannot fail a build and is not meant to.

---

## 7. What you need to decide

**Is a required field enough to stop the `contests` edge being misread, or does it need a sibling?**

The edge shipped one review ago and was set wrongly on its first use outside that review, which
now has the digest telling readers that a correct, applied lesson is disputed and untested. Change
12 removes the false edge and forces the author to quote the clause they dispute — which is the
moment they would notice there isn't one.

What it cannot do is check that the quoted clause really *is* disputed. The alternative is a second
edge kind — `widens`, for "the earlier lesson is true and too narrow" — which is what `IMP-0476`
actually meant. That is honest about the two cases and grows the schema by a third edge.

My recommendation is change 12 alone: one more edge kind is one more thing for an agent to choose
between, and the misuse here was a *missing distinction in the definition*, not a missing field.
Say the word and I will add `widens` instead.

**Should a `rev_setting` key be required to declare whether it is a tunable or a disclosure
control?**

Change 4 records the distinction in knowledge, where a human reads it. The mechanical form would
put a `classification` field on every `settingRows` entry across the three `deploymentSettings`
files and check it in the build.

I have not proposed it, for a reason rather than caution: it changes the seed payload shape, which
is delivery work under `provisioning/` and outside this agent's remit
([`improvement-agent.md` L359](../../agents/improvement-agent.md#L359)). It is also the only thing
standing between someone editing k=5 as though it were a cache duration.

If you want it, the routing is a `wbs:6.9` follow-up to `development-agent` with the requirement
and its verification, not an improvement change.

**Change 2's severity: HARD, as proposed, or SOFT?**

I have put it in the HARD preflight because after change 1 the tree is green, and the only remedy a
finding ever needs is a one-line docstring edit — so it cannot sit red over debt nobody owns, which
is the usual argument for SOFT.

The counter-argument is that it fails a build over a comment. If you prefer SOFT, the same code
moves to [`verify-derived-counts.py`](../../scripts/verify-derived-counts.py), which is this
repository's declared home for prose-versus-source claims and is already SOFT — at the cost of a
new non-numeric verdict shape in a gate built around counts.

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-28-improvement-review-10.md

Findings processed: 11 NEW  →  10 clusters
Regression check:   6 prior changes audited, 2 classes recurred
Proposed:           0 constraints (cap 3), 6 gates/scripts, 6 skill/knowledge/template edits,
                    2 agent-file edits, 0 retirements, 1 data correction
Altitude calls:     4 generalised from instance to class, 6 left as notes or instances
Digest:             will regenerate — 474 entries, 473 lessons, one CONTESTED marker REMOVED

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

Two gates run, validator first, per
[`CLAUDE.md`](../../CLAUDE.md)'s learning rules:
`python3 scripts/verify-improvement-log.py --check` → **1 problem, and it is the batch trigger
itself** (0 schema errors across 474 entries; the trigger is what this review exists to clear).
`python3 scripts/generate-known-failure-modes.py --check` → **current (474 entries)**.

**IMPROVEMENT LOG: one finding to append on application** — the `contests` edge produced a false
`CONTESTED` marker on `IMP-0142`, an applied and correct lesson, on its first use outside the
review that built it. Named here rather than appended now so this document's counts stay stable;
recorded in this section so an interrupted application leaves a to-do rather than nothing
([`IMP-0333`](../../logs/known-failure-modes.md#L35)'s rule). Its id comes from
`python3 scripts/allocate-improvement-id.py` at application time, never from `tail -1`.

---

## 9. Applied — the record

**APPLIED 2026-08-28**, approved by Xander Lykopoulos as drafted. All 13 changes are on disk.
Entries were closed **incrementally**, each as its change landed, rather than batched after the
final edit ([`IMP-0301`](../../logs/known-failure-modes.md#L35)).

### Verification executed at application time

| Gate | Result |
|---|---|
| `verify-improvement-log.py --check` | **exit 0** — 475 entries, 87 NEW / 387 APPLIED / 1 REJECTED. **Batch trigger cleared:** 1 unread (`IMP-0478`, appended by this application), 0 awaiting-approval, 86 reviewer-deferred. 4 warnings, all pre-existing `corrects` stamps |
| `verify-improvement-log.py --selftest` | **exit 0** — 64 fixtures, every pre-existing check still fires |
| `generate-known-failure-modes.py --check` | **current** — 475 entries, 474 distinct lessons |
| `verify-build-config.py` (real config) | **exit 0** — 67 steps, 52 gates, `wired scripts own their wiring: OK` |
| `Invoke-Pester src/tests/build/VerifyBuildConfig.Tests.ps1` | **14 passed, 0 failed**, including 3 new |
| `verify-flow-definition-language.py` + `--selftest` | **exit 0** / **exit 0** |
| `verify-flow-trigger-body-isolation.py` (as wired) | **exit 0** — A1, A2, A3, B1 clean |
| All 7 usage-patched scripts, correct arguments | **exit 0** each; two `--selftest` paths **exit 0** |
| `ls scripts/verify-*.py \| wc -l` | **51** — unchanged, no new script, so [`improvement-agent.md` L356](../../agents/improvement-agent.md#L356) needs no edit |

### Four deviations from the draft, none silent

1. **Change 2 was placed HARD**, per your answer leaving §7 question 3 to my judgement. The
   deciding evidence was measured, not argued: after change 1 the real config exits **0**
   ([`IMP-0439`](../../logs/known-failure-modes.md#L65)'s rule — run it and read the exit code), the
   only remedy a finding can ever need is a one-line docstring edit so it cannot sit red over debt
   nobody owns, and the verdict is a regex over a derived value rather than a judgement, which is
   `constraints/README.md`'s own test for HARD.

2. **Change 12 landed one entry wider than drafted, and the widening was compelled.** The new
   `contests_clause` requirement fired on **2 entries, 2 true positives, 0 false**: `IMP-0476`'s
   false edge (removed, as drafted) and **`IMP-0412`'s pre-existing legitimate edge**, which the
   draft did not mention. That edge is a real contest, so the fix was to backfill its clause —
   quoted verbatim from `IMP-0124`'s lesson, *"Related: if() evaluates ONLY the branch it takes
   here, proven by TD-07 failing and TD-08 passing on the same action."* One pre-existing edge is
   not the 138-errors-about-finished-work situation that would have justified a cutoff.

3. **Change 13 needed a helper the draft did not itemise.** `_descendant_action_count()` was added
   beside `_immediate_children()`, reusing `_iter_actions` rather than re-walking the Switch/If
   case-and-default nesting by hand — that nesting is exactly the shape a hand-rolled recursion
   gets wrong.

4. **The digest figures in §8's gate block are one entry stale**, because this application appended
   `IMP-0478`. Predicted 474 entries / 473 lessons; actual **475 / 474**, with one `CONTESTED`
   marker removed as stated. The marker count went **2 → 1**; the survivor is the legitimate
   `IMP-0412` → `IMP-0124` edge.

**One discrepancy in the approval message, recorded rather than absorbed:** it authorised *"all 10
clusters, 15 changes"*. This document proposed **13**, and 13 is what landed. Nothing was dropped —
the count in the approval simply does not match §3's table, and inventing two more changes to reach
15 would be the wrong way to reconcile it.

### One measurement that came out worse than the finding predicted

Change 13 made the check-7 exceptions state their blast radius, and the
`REVPortalRoundStatistics` exception **hides 167 descendant actions** — against 6 and 12 for the
other two. [`IMP-0477`](../../logs/improvement-log.jsonl) estimated 84 added / roughly 104. The
exception is owned, dated and unexpired, so nothing fails and nothing should; but the fail-loud
claim resting on that alert naming the failing action is materially weaker than the declaration
assumed, and the number is now printed on every run.

### Routed, not fixed

- **[`verify-derived-counts.py`](../../scripts/verify-derived-counts.py) exits 1 with three drifted
  claims** — 67 vs 68 secured columns in two Dev Summary places, 51 vs 52 in the REV Trustee role
  header. SOFT, so nothing blocks and nothing has reported them. All three targets are delivery
  artefacts under `docs/development/` and `src/solutions/`; not this agent's to edit.
- **[`scripts/verify-doc-line-links.py`](../../scripts/verify-doc-line-links.py) is UNTRACKED**
  (`git ls-files` → *"Did you forget to 'git add'?"*) while being the HARD `doc-line-links` build
  step. Found during re-verification, and it is a sharper defect than the docstring this review
  corrected: a HARD step whose script is not committed cannot run in CI. Needs `git add`, which
  belongs to whoever commits this work.
- **`IMP-0478`** is left `unread` by design — this application wrote it, and a review does not
  process a finding it created in the same pass
  ([`IMP-0443`](../../logs/known-failure-modes.md#L35)).

### Findings left open, deliberately

`IMP-0473` and `IMP-0477` carry `reviewed_in`, a `deferred_reason` recording exactly what landed and
what did not, and a `revisit_when`. Both are `observable_at: V5`; this review reached V1. An entry
closed on a document saying it was fixed is a claim, not a result
([`IMP-0224`](../../logs/known-failure-modes.md#L220)).
