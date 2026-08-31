# Improvement Review — 2026-08-31 (review 46)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 13 `unread` + 1 appended by this review (`IMP-0516`) → 9 clusters
**Trigger:** batch (≥10 `NEW`) **and** unread `blocker` [`IMP-0515`](../../logs/improvement-log.jsonl)
**Gate:** `APPROVE IMPROVEMENTS`
**WBS:** 6.9 (11 of 14 entries); 3 carry no task — system-level (`C-COM-002`: no change-order question, all warranty rework inside 6.9)

---

## Summary

**Approving this review alone does not unblock the build, and approving
[review 45](2026-08-30-improvement-review-2.md) alone does not either — both are needed, plus one
piece of bookkeeping review 45 omits.** I proved this by simulation rather than by reading the
gate's source, and the result is the most consequential thing in this document: applied exactly as
written, review 45 leaves [`C-TECH-061`](../../constraints/technology/technology-constraints.md#L131)
**permanently red**, because `IMP-0511` would still classify as `awaiting-approval`, which is the
same blocker rung as `unread`. That is logged as [`IMP-0516`](../../logs/improvement-log.jsonl) and
fixed in §3 change 8.

**Review 45 is correct and I have not re-derived it.** Its analysis of `IMP-0511` stands unchanged;
this review neither extends nor supersedes it. The only thing I add is the one field its §8
disposition does not set.

Two of the 13 findings had already been half-fixed on disk while they sat unread, and re-measuring
changed what I propose for both — see §2.4 and §2.5.

**Proposed: 2 constraints (cap 3), 2 gates, 4 skill/knowledge edits, 1 agent edit, 0 retirements.**
Both gates were measured against the real corpus before being proposed, and both came back
**100% precision on small corpora** — the numbers are in §3.2 and §3.3.

---

## 1. Regression check — did review 44's changes work?

Review 45 is **parked, not applied**, so it is not auditable here; its three changes are correctly
absent from disk. Review 44 is the last applied review.

| Prior change | Class it targeted | Recurred? | Verdict |
|---|---|---|---|
| [`build-agent.md` L251](../../agents/build-agent.md#L251) — `warnings_detail[]` | `gate-reassures-wrongly` | NO | **Working.** Present |
| [`C-TECH-055`](../../constraints/technology/technology-constraints.md#L110) — names the current Dev Summary | `declared-policy-not-mechanically-enforced` | NO (see note) | **Working.** [`verify-constraint-verifiers.py`](../../scripts/verify-constraint-verifiers.py) re-run: PASS |
| [`power-automate.md`](../../knowledge/technology/power-automate.md) — `result()`'s scope | `platform-contract-guessed-not-groundtruthed` | **YES ×2** | **Prose change, class recurred within 5 hours.** See below |
| [`development-agent.md` L104](../../agents/development-agent.md#L104) — fan-out gate line | `declared-policy-not-mechanically-enforced` | NO | **Working.** Present |

**The one recurrence, stated honestly.** `platform-contract-guessed-not-groundtruthed` is the
largest class in this repository (**×52**) and it recurred **twice** within five hours of review 44
landing a prose change into it — [`IMP-0507`](../../logs/improvement-log.jsonl) at 17:45 and
[`IMP-0508`](../../logs/improvement-log.jsonl) at 19:20. The regression table in
[`improvement-agent.md` L307](../../agents/improvement-agent.md#L307) says a recurrence after a
prose change is evidence of wrong altitude and should escalate to a gate.

**I am not escalating it, and here is why that is not evasion.** Neither recurrence is about
`result()` — change 3's actual subject. One is *"the source deck's own worked numbers contradicted
the convention we chose"*; the other is *"a timestamp proxy was read as proof where a definitive
live test was available."* Change 3 did not fail; a class far larger than change 3 produced two new
members from mechanisms change 3 never addressed. The honest characterisation is a **standing gap
in the repository's largest class**, not a regression of review 44. What both new members *do*
share is gateable in neither case — a deck's arithmetic and a live write-then-observe are not
things a script in `scripts/` can check — so §2.6 puts them in the skill that is loaded at the
exact moment of use, and names the trigger that would justify a gate.

**`declared-policy-not-mechanically-enforced` also gained a member** ([`IMP-0515`](../../logs/improvement-log.jsonl))
but that entry is the gate **working**, not the policy failing — its own `why_it_was_never_caught`
says *"nothing to catch."* Not a recurrence.

**No gate that exists failed to fire.** No `gate-cannot-fail` finding is owed against review 44.

**Closure-evidence audit.** Review 44 left `IMP-0496` open with a named `revisit_when` rather than
closing it on a needle matching its own new sentence — the discipline
[`IMP-0225`](../../logs/improvement-log.jsonl) asked for, and it held. This review applies the same
test and it costs me five closures: see §5.

---

## 2. Clusters and promotion decisions

### 2.1 Cluster A — V4 evidence demanded before the deploy that alone could produce it

```
CLUSTER: gate-scope-mismatch  (x3 this review: IMP-0503, IMP-0505 carry the class outright;
         IMP-0502 is logged v3-does-not-imply-v4 but shares the property below.
         gate-scope-mismatch is x15 lifetime, counting IMP-0516 appended by this review.)
Altitude:  CLASS — three instances, three DIFFERENT agents (test-agent, lead-agent, test-agent
           again), one property: "an agent demanded or requested V4/V5 evidence about a
           component before the pipeline run that alone could produce that evidence had
           happened." The altitude rule FORBIDS three instance patches here, and the three
           findings propose exactly that (agents/test-agent.md, agents/lead-agent.md,
           agents/pm-agent.md) — one per agent that happened to hit it.
Ladder row: "An agent had the information and still did the wrong thing" -> skill edit.
           NOT a constraint row: see the Verify By argument below.
Becomes:   skills/how-to-apply-constraints.md — ONE decision step at the shared moment of use
Retires:   nothing
Cites:     IMP-0502, IMP-0503, IMP-0505
Residual:  Prose, and not mechanical. A gate would need to read intent. The trigger to build
           one is a fourth instance arising AFTER this edit ships.
```

**Why one skill edit and not three agent edits.** The three findings were written by agents who
each saw their own half. `IMP-0503` is test-agent asserting a V4 constraint at Test;
`IMP-0505` is lead-agent *asking the reviewer* for V4 actions; `IMP-0502` is a test cycle
re-discovering, for the third consecutive report, that a V4 step has not moved. All three happen at
**the moment an agent applies a constraint or judges an assumption's closure**, and
[`skills/how-to-apply-constraints.md`](../../skills/how-to-apply-constraints.md) is the one file
every agent loads at exactly that moment. Three agent-file edits would leave the fourth agent
uncovered; one skill edit does not.

**Why not a constraint row.** Anti-bloat limit 4: a constraint whose `Verify By` is not mechanically
executable is a comment. *"Could this evidence exist yet?"* is a judgement about ordering that no
script in this repository can settle — [`agents/WORKFLOW.md`](../../agents/WORKFLOW.md)'s own
Verification levels table already assigns V4 to the Pipeline step, and being written down is
precisely what failed here three times.

### 2.2 Cluster B — a supplied design drop was read one folder deep

```
CLUSTER: input-type-with-no-owning-agent  (x1 this review: IMP-0510; x3 LIFETIME)
Altitude:  CLASS — and the trigger is CLAUDE.md's own. Its supplied-assets rule ends
           "A third instance is what would justify building one [a gate]." IMP-0028 was the
           first, IMP-0384 the second, IMP-0510 is the THIRD. The condition the repository
           set for itself is met; I am not inventing the threshold.
Ladder row: "A tool could catch it mechanically" + "a platform law, or a third instance"
Becomes:   scripts/verify-design-source-coverage.py + C-TECH-075, wired into build config
Retires:   nothing
Cites:     IMP-0028, IMP-0384, IMP-0510
Residual:  The gate checks that a feature-matching supplied folder is CITED, not that it was
           obeyed. A TAD could cite ui_kits/ and still convert the wrong thing.
```

**Verified at V1, not taken on the finding's word.** The TAD contains 12 occurrences of
`Designsystem` and cites exactly three paths — `readme.md`, `tokens/colors.css`,
`tokens/fonts.css`. `Designsystem/Revitalise Design System/ui_kits/trustee-review-portal/` exists
with **7 files** (`AppFrame.jsx`, `RoundOverview.jsx`, `ApplicationsList.jsx`,
`ApplicationDetail.jsx`, `TrusteePortalApp.jsx`, `index.html`, `README.md`) and is cited **nowhere**.
Its `README.md` L4 reads: *"Headings switched from bold navy sans to Playfair Display in ink-900
(brand has no navy in its palette)."* The finding's quotation is accurate.

**This is the value-based instrument the repository has been asking for.** The five prior prose
gates measured at 48%–100% false ([`IMP-0422`](../../logs/improvement-log.jsonl)) all matched
*phrases*. This one compares a **directory listing** against **cited paths** — both values. That is
the *"assert on values, not on phrases"* rule being satisfiable for once.

### 2.3 Cluster C — a font-size larger than the ambient body size with no line-height

```
CLUSTER: no-assertion-on-shipped-content  (x1 this review: IMP-0509; x22 lifetime)
Altitude:  CLASS — the class is at x22 and this is the first member of it that is reducible
           to ARITHMETIC rather than to a rendered judgement. That is what makes it gateable
           where the other 21 were not.
Ladder row: "A tool could catch it mechanically"
Becomes:   scripts/verify-css-line-height.py + C-TECH-076, wired into build config
Retires:   nothing
Cites:     IMP-0486, IMP-0509
Residual:  The gate cannot see INHERITED line-height, only its absence in the same rule. A
           rule inheriting a CORRECT line-height from a parent is a false positive by
           construction — measured at zero in this corpus, but the shape exists.
```

**The mechanism, confirmed in source.** The token scale in
[`ds-tokens.css` L253](../../src/code-apps/trustee-review-portal/src/styles/ds-tokens.css#L253) runs
`--text-base: 17px` up to `--text-3xl: 42px`. FluentProvider's root sets `line-height: 22px`. Any
rule setting a font-size above 17px without its own line-height inherits 22px — and at
`--text-xl: 24px` the line box is **smaller than the glyphs**, which is an overlap by arithmetic,
not by opinion.

### 2.4 Re-verification (not a cluster) — IMP-0510 and IMP-0509 are BOTH half-fixed already

**This is the re-verification step earning its place, and it changed two outcomes.**

**`IMP-0509` names a defect that is fixed on disk.** `.statTileValue` now carries
`line-height: var(--leading-tight)` at
[`ds.module.css` L378](../../src/code-apps/trustee-review-portal/src/styles/ds.module.css#L378),
alongside the `overflow-wrap: break-word` from `IMP-0486` and a
`clamp(var(--text-lg), 6cqi, var(--text-2xl))` font-size. The specific fix landed. **It still does
not close** — `observable_at: V4`, and the only proof is a rendered screenshot no session here can
produce. It stays open with a `revisit_when`. The *class* fix (§2.3) proceeds regardless, and note
that the now-fixed rule is exactly why the gate reports 2 findings rather than 3.

**`IMP-0510` has diverged into one stale half and one live half**, and closing or acting on it
whole would be wrong in both directions:

| Half of IMP-0510 | Claim | Measured now | Disposition |
|---|---|---|---|
| `--font-display` is a Fluent/Aptos **sans** stack at `ds-tokens.css:334` | typeface wrong | **STALE — already fixed.** [L378](../../src/code-apps/trustee-review-portal/src/styles/ds-tokens.css#L378) now reads `"Playfair Display", Georgia, Cambria, "Times New Roman", Times, serif`, self-hosted per ADR-042 (this is `IMP-0513`'s own work, landed while `IMP-0510` sat unread) | no action |
| `--text-heading: #002060` (navy) at `ds-tokens.css:176` | colour wrong | **LIVE.** [L176](../../src/code-apps/trustee-review-portal/src/styles/ds-tokens.css#L176) still reads `--text-heading: #002060`, against a supplied README that names navy as absent from the brand | routed to delivery, §3.4 |

Had I taken the finding at its word I would have proposed a typeface fix that shipped yesterday and
missed the colour that is still wrong today.

### 2.5 Cluster D — a source-declared MaxLength that never reached the live column

```
CLUSTER: platform-state-divergence  (x1 this review: IMP-0514; x14 lifetime)
Altitude:  CLASS, but NOT MINE TO BUILD.
Ladder row: "A tool could catch it mechanically" — and the tool must AUTHENTICATE.
Becomes:   a routed requirement, not a script in this review. See §3.4.
Retires:   nothing
Cites:     IMP-0122, IMP-0259, IMP-0514
Residual:  Until the live-reconciliation step exists, verify-field-length-limits.py keeps
           reporting PASS on writes that live will reject. That is a KNOWN, OPEN hole and it
           is stated here rather than papered over.
```

[`improvement-agent.md` L383](../../agents/improvement-agent.md#L383) is explicit: *"An executable
that authenticates to a live environment is delivery work, and it is not yours to author."* The fix
`IMP-0514` asks for reads live Dataverse metadata. I hand over the requirement and the verification
query; I do not write the script because I happened to identify the need. Review 18's 285-line live
verifier that could never run is the precedent.

### 2.6 Cluster E — a cheaper definitive check existed and an inference was used instead

```
CLUSTER: platform-contract-guessed-not-groundtruthed  (x2: IMP-0507, IMP-0508; x52 lifetime)
Altitude:  CLASS for the shared property — "a definitive check was available and cheap, and an
           inference was recorded as though it were the check."
Ladder row: "An agent had the information and still did the wrong thing" -> skill edit
Becomes:   skills/how-to-verify-a-platform-contract.md
Retires:   nothing
Cites:     IMP-0507, IMP-0508
Residual:  Prose into the largest class in the repository, five hours after the last prose
           change into it did not stop these two. I am not claiming this will. It is the only
           available home — neither a deck's arithmetic nor a live write-then-observe is
           scriptable from here — and §1 records the recurrence rather than hiding it.
```

`IMP-0507`: the two source decks showed *"Average 6 per day"* against cumulative totals of 434 and
717 — arithmetic that was itself the answer to the convention question, available before anyone
asked the reviewer. `IMP-0508`: `callbackregistration.createdon` looking stale was treated as proof
a trigger was broken; the definitive test (write `rev_triggeredon`, observe `rev_computedon`) was
available throughout and, when finally run, showed an **exact 19:15 match** — the flow was working.
Same property, opposite directions: one inferred from a document, one from a timestamp.

### 2.7 Clusters F, G, H — three single-instance findings, three different rungs

```
CLUSTER: session-lacks-live-credentials  (x1: IMP-0512)
Altitude:  INSTANCE — first member of the class, and the mechanism is specific to how this
           system dispatches agents rather than general to the platform.
Ladder row: "An agent had the information and still did the wrong thing" -> agent-file edit
Becomes:   agents/development-agent.md — a branch its Reviewer-Executed Operations section
           lacks: "the credential is ABSENT by design", distinct from "the classifier refused"
Retires:   nothing
Cites:     IMP-0512
Residual:  Prose in one agent file. Every other non-pipeline agent has the same property and
           the same missing branch; I am not editing eight files on one instance. A second
           instance in a DIFFERENT agent is the trigger to move this to a shared surface.
```

```
CLUSTER: reusable-font-self-hosting-technique  (x1: IMP-0513)
Altitude:  CAPABILITY, not defect — the rung this system rarely uses and should.
Ladder row: "A capability was established and could be lost again"
Becomes:   knowledge/technology/code-apps.md
Retires:   nothing
Cites:     IMP-0513
Residual:  The distinction is the fragile part, not the technique. It applies ONLY to
           open-source faces; Aptos is proprietary and reviewer-supplied files remain the
           only route there. A knowledge line that lost that caveat would be worse than none.
```

```
CLUSTER: output-shape-defeats-the-reader  (x1 this review: IMP-0506; x10 lifetime)
Altitude:  CLASS — x10, and the finding hands over a COMPLETE ready template, so there is no
           design work to do and no reason to defer it to a second instance.
Ladder row: "An agent had the information and still did the wrong thing" -> skill edit
Becomes:   skills/how-to-report-to-the-reviewer.md — a per-item template for exactly one
           section whose shape was underspecified relative to every other section in the file
Retires:   nothing — this TIGHTENS an existing rule in place rather than adding a row
Cites:     IMP-0506
Residual:  Unmeasurable. "Could the reviewer decide without opening another document" is the
           thing being fixed and no gate can ask it. IMP-0059 founded this class and it is
           still prose seven instances later.
```

`IMP-0513` is not a defect — it is a *capability*: a named open-source typeface is obtainable from
`@fontsource/<slug>` under SIL OFL 1.1, which closes an "external dependency, waiting on the
reviewer" that ADR-036/ADR-042 carried across multiple TAD revisions.

### 2.8 Cluster I — IMP-0504 and IMP-0515, processed with no change proposed

```
CLUSTER: no-change-owed  (x2: IMP-0504 finding-diagnosis-unverified; IMP-0515 gate-fired-correctly)
Altitude:  NONE, deliberately, and for two DIFFERENT reasons — grouped only because both
           produce no rule change, not because they share a mechanism.
Ladder row: "One instance, specific to one feature, no general mechanism" -> stays a log note
Becomes:   nothing. IMP-0504 is deferred verbatim on its own revisit_when; IMP-0515 is
           REJECTED as a report of the gate SUCCEEDING.
Retires:   nothing
Cites:     IMP-0504, IMP-0515
Residual:  IMP-0504's two sub-mechanisms (a reviewer decision in routing.log never carried
           into the register; seed data indistinguishable from flow-produced data) are BOTH
           gateable and BOTH real. They are left undone on its own author's judgement that
           one instance does not justify the gate, and its revisit_when is the trigger.
```


**[`IMP-0504`](../../logs/improvement-log.jsonl)** (`finding-diagnosis-unverified`, ×17) already
carries its own `revisit_when` and its own entry says *"Not applied here - one instance."* I agree
and I am not overriding a correctly-scoped self-deferral. Deferred verbatim.

**[`IMP-0515`](../../logs/improvement-log.jsonl)** is the `blocker` that summoned this dispatch, and
it is **the gate working exactly as designed** — halted at step 3 of 68, before nine minutes of
build work would have been discarded. Its own `proposed_change` is `type: none` and its
`why_it_was_never_caught` is *"nothing to catch."* **REJECTED, with the reason recording that no
rule change is owed and that this review is the remedy it names.** Rejecting a finding that reports
a success is the correct bookkeeping, not a dismissal.

---

## 3. Proposed changes

> `Type` values from the closed vocabulary: `constraint` · `constraint-amendment` · `script` ·
> `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanical? |
|---|---|---|---|---|---|
| 1 | skill | [`skills/how-to-apply-constraints.md`](../../skills/how-to-apply-constraints.md) | New step: **before recording a FAIL on, or requesting a human action for, a V4/V5-observable requirement, establish that the evidence could exist yet.** If the only run that could produce it is the pipeline step that follows this gate, record `deferred-to-pipeline` naming the constraint and the step — not FAIL, and not an ask to the reviewer | IMP-0502, IMP-0503, IMP-0505 | NO |
| 2 | script | `scripts/verify-design-source-coverage.py` **(new)** | For each supplied design drop, enumerate the full tree; where a subdirectory's name matches the feature slug or a screen name the TAD declares, require the TAD to cite that path. Measured in §3.2 | IMP-0028, IMP-0384, IMP-0510 | **YES** |
| 3 | constraint | `C-TECH-075` **(new)** | **A supplied design artefact is intake'd by full directory enumeration, not by the first folder found.** Any subdirectory of a supplied drop whose name matches the feature under design is cited by the TAD or explicitly declared out of scope with a reason | IMP-0028, IMP-0384, IMP-0510 | **YES** — change 2 |
| 4 | script | `scripts/verify-css-line-height.py` **(new)** | Flag any authored CSS rule setting `font-size` above the ambient body size without a `line-height` in the same rule. Measured in §3.3 | IMP-0486, IMP-0509 | **YES** |
| 5 | constraint | `C-TECH-076` **(new)** | **A CSS rule setting a font-size larger than the ambient body size declares its own line-height.** Inheriting a host framework's line-height tuned for its base size produces overlapping wrapped lines, invisible to jsdom | IMP-0486, IMP-0509 | **YES** — change 4 |
| 6 | skill | [`skills/how-to-verify-a-platform-contract.md`](../../skills/how-to-verify-a-platform-contract.md) | New subsection: **an inference is not the check when the check is cheap.** Two named shapes — a source document showing a *worked example* is checked against the implementation's arithmetic; a proxy signal (a timestamp, a registration date) is a reason to run the definitive test, never a substitute for it | IMP-0507, IMP-0508 | NO |
| 7 | agent | [`agents/development-agent.md`](../../agents/development-agent.md) | New branch in Reviewer-Executed Operations distinguishing *"the harness classifier refused a recognised live write"* (existing) from *"this session holds no live credential at all, by design"* (new). For the latter, **skip the foreground retry** — the variable is absent, not blocked — and go straight to handing over the command plus its verification query | IMP-0512 | NO |
| 8 | other | [`logs/improvement-log.jsonl`](../../logs/improvement-log.jsonl) | Record `deferred_reason` on `IMP-0511`, the field review 45's §8 disposition omits. **Without it the build gate stays red forever** — proven by simulation in §3.1 | IMP-0516 | **YES** — the gate itself |
| 9 | knowledge | [`knowledge/technology/code-apps.md`](../../knowledge/technology/code-apps.md) | Font self-hosting procedure: for a typeface named by a supplied design system, check `@fontsource/<slug>` (SIL OFL 1.1) **before** recording it as an unmet external dependency — open-source faces only, proprietary faces (Aptos) still need the reviewer. Embed as a base64 `data:` URI inside the `@font-face` rule, never a relative `url()`, per the A-BRAND-1 precedent | IMP-0513 | NO |
| 10 | skill | [`skills/how-to-report-to-the-reviewer.md`](../../skills/how-to-report-to-the-reviewer.md) | Replace the *"What you need to decide"* shape with a fixed per-item template: **Problem** (≤1 sentence) · **Suggested fix** (≤1 sentence) · **What happens if you don't** (≤2 sentences) · a line-link to the source · items separated by a horizontal rule | IMP-0506 | NO |

**Constraint budget: 2 of 3 used.** **Script count moves 52 → 54**, and
[`scripts/derived-counts-registry.json`](../../scripts/derived-counts-registry.json)'s
`improvement-agent-verify-script-count` is updated in the same change, per
[`improvement-agent.md` L377](../../agents/improvement-agent.md#L377).

### 3.1 The simulation that produced change 8 — and why reading the source would have missed it

**I ran the gate rather than reading it**, per
[`improvement-agent.md` L150](../../agents/improvement-agent.md#L150), against two copies of the log
in a scratch directory, restoring the real file after each and confirming byte-identity with `diff`.

**SIM A — review 45 applied exactly as its §8 says** (`IMP-0511` stays `NEW`, gains `revisit_when`,
no `deferred_reason`):

```
TRIGGER: 1 blocker in state 'unread': IMP-0515.
TRIGGER: 1 blocker in state 'awaiting-approval': IMP-0511 -> 2026-08-30-improvement-review-2.md
TRIGGER: 14 NEW entries awaiting closure (batch trigger is 10)
verify-improvement-log: FAILED — 3 problem(s)
```

**All three triggers survive. The build stays halted at step 3 of 68 indefinitely.**

**Why.** [`classify()`](../../scripts/verify-improvement-log.py#L992) puts `deferred_reason` **ahead
of** `awaiting-approval` in precedence. `revisit_when` alone does nothing to the state. And the
blocker rung fires on `unread` **or** `awaiting-approval` alike — so a blocker parked at a correct,
approved, fully-analysed review is red on exactly the same rung as one nobody has read. Review 45
reasoned, correctly, that `IMP-0511` must not be *closed* on evidence nobody gathered. It then chose
the one remaining state that keeps the gate red.

**SIM B — this review's disposition** (6 closed, 8 deferred with reasons, `IMP-0511` among them):

```
NOTE — 104 NEW: 0 unread, 0 awaiting-approval, 104 reviewer-deferred, 0 already-fixed
verify-improvement-log: FAILED — 1 problem(s)   [the simulation's OWN artefact: I set no
                                                 evidence_grep on the 5 closures]
```

**All three triggers clear.** The residual failure is mine, not the design's — and it is a
requirement I have carried into the apply step: **every entry moved to `APPLIED` carries an
`evidence_grep`.** Five entries would have failed the gate at apply time had the simulation not
surfaced it.

`deferred_reason` is not a loophole here — it is the discharge the gate's own message names:
*"or by recording an explicit 'deferred_reason' on each entry."* A reviewer-accepted decision with a
named owner and a return condition is what the four-state model calls a decision. What it must never
be is a rubber stamp, which is why §5 gives each of the eight a real trigger.

### 3.2 Gate measurement — `verify-design-source-coverage.py`

**Corpus:** the one supplied design drop (`Designsystem/Revitalise Design System/`, 19 directories)
against the TAD for the feature under design.

| | Result |
|---|---|
| Findings | **1** |
| True positives | **1** — `ui_kits/trustee-review-portal/` (7 files, name matches the feature slug) cited nowhere in a TAD that cites 3 other paths under the same drop |
| False positives | **0** |
| Negative control | `ui_kits/marketing-site/` correctly **not** reported — a sibling of identical shape whose name matches no screen this TAD declares. This is the check that distinguishes the gate from *"flag every uncited folder"*, which would have reported 16 |

**This is a small corpus and I am saying so.** Review 45 rejected its own gate at a corpus of one
row, and the distinction I am drawing is real: that gate was a **phrase matcher over prose**; this
one compares a **directory listing to cited paths**. Its failure mode is a renamed folder, not a
rephrased sentence. The negative control is what makes the 1/1 meaningful rather than tautological.

### 3.3 Gate measurement — `verify-css-line-height.py`

Measured in three passes, because the first two were wrong and the corpus said so.

| Pass | Rule | Findings | Verdict |
|---|---|---|---|
| 1 | any `font-size` without `line-height`, all `.css` under `src/` | **77** across 17 files | **Unusable.** Dominated by `node_modules/` and `dist/` — the built bundle re-reports every authored rule |
| 2 | same, authored sources only (5 files) | **23** | **Still wrong.** Most sit at 13–17px, where inheriting 22px is harmless or generous. Flagging them teaches the gate to cry wolf |
| 3 | **font-size resolving above `--text-base` (17px)**, authored only; `clamp()` judged on its maximum | **2** | **Shipped design** |

**Pass 3 adjudicated one finding at a time:**

| Finding | Size | Inherited line box | True or false |
|---|---|---|---|
| [`app.module.css:413`](../../src/code-apps/trustee-review-portal/src/styles/app.module.css#L413) `.panelHeading` | 20px | 22px (ratio 1.1) | **TRUE** — below the ~1.2 minimum for descenders; a wrapped heading crowds |
| [`ds.module.css:423`](../../src/code-apps/trustee-review-portal/src/styles/ds.module.css#L423) `.cardTitle` | 24px | 22px (ratio 0.92) | **TRUE** — the line box is *smaller than the glyphs*. Overlap on wrap is arithmetic |

**2 findings, 2 true positives, 0 false positives.** The narrowing from 77 → 2 removed, by name,
every `node_modules`/`dist` duplicate and every at-or-below-base rule (`--text-xs`, `--text-sm`,
`--text-base`, `11px`, `11pt`) — none of which can produce `IMP-0509`'s mechanism. I can name what
the narrowing removed, which is the tell that separates a narrowing from a substitution.

**The corpus confirms the gate would have caught the original defect.** `.statTileValue` does *not*
appear in pass 3 — because its `line-height` was added yesterday. Running pass 3 against
`git show HEAD~1` would report it as a third finding. **A gate reporting 0 against a corpus known to
contain an instance is the tell** ([`improvement-agent.md` L433](../../agents/improvement-agent.md#L433));
this one reports the instance until the fix lands and then stops. That is the polarity being right.

### 3.4 Work this review ROUTES rather than performs

| To | What | WBS |
|---|---|---|
| [`development-agent`](../../agents/development-agent.md) | `--text-heading: #002060` at [`ds-tokens.css:176`](../../src/code-apps/trustee-review-portal/src/styles/ds-tokens.css#L176) — the live half of `IMP-0510`. The supplied `ui_kits/trustee-review-portal/README.md` L4 specifies ink-900, and names navy as absent from the brand | 6.9 |
| [`architect-agent`](../../agents/architect-agent.md) | A TAD erratum recording that `ui_kits/trustee-review-portal/` was supplied and unread, and what ADR-033/034 would have said had it been read | 6.9 |
| [`pipeline-agent`](../../agents/pipeline-agent.md) or the reviewer's own shell | The live-vs-source `MaxLength` reconciliation `IMP-0514` needs: `EntityDefinitions(...)/Attributes(...)?$select=MaxLength` against every attribute [`verify-field-length-limits.py`](../../scripts/verify-field-length-limits.py) checks. **Not authored here** — it authenticates (§2.5) | 6.9 |
| [`plan-agent`](../../agents/plan-agent.md) / [`architect-agent`](../../agents/architect-agent.md) | FR-058's definitional correction from `IMP-0507`: cumulative-since-16-Feb-2026, not per-round. SDD amendment + ADR + flow rework | 6.9 |

All four are warranty rework inside task 6.9. **No change-order question arises**
([`C-COM-002`](../../constraints/commercial/commercial-constraints.md)).

---

## 4. Retirements

> **Retirement check performed: 80 active constraint rows reviewed against these nine clusters;
> 10 already retired. None currently redundant.**
>
> The candidate I examined and rejected is
> [`C-TECH-060`](../../constraints/technology/technology-constraints.md) (field-length limits).
> `IMP-0514` shows its gate reporting PASS on a write live then rejected, which looks like grounds to
> retire or replace it. **It is not.** The row is correct about what it claims — the *source* value
> fits the *declared* MaxLength — and the gap is a second, live check that does not exist yet
> (§3.4). Retiring a working source-side gate because a live-side gate is missing would delete
> coverage and add none. Revisit once the live reconciliation ships, at which point the two may
> merge into one row.

Derived, not typed: `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` → **10**;
`grep -rh '^| C-' constraints/ --include='*.md' | wc -l` → **80** (→ 82 on approval).

---

## 5. Disposition of all 14 entries

**Closed on approval (5 APPLIED + 1 REJECTED).** Each `APPLIED` entry carries an `evidence_grep`,
per §3.1's measured requirement.

| Finding | To | Why closeable |
|---|---|---|
| IMP-0503 | APPLIED | `observable_at: n/a`; change 1 is its whole remedy |
| IMP-0505 | APPLIED | `observable_at: n/a`; change 1 |
| IMP-0506 | APPLIED | `observable_at: n/a`; change 10 is the finding's own template verbatim |
| IMP-0512 | APPLIED | `observable_at: n/a`; change 7 |
| IMP-0513 | APPLIED | `observable_at: n/a`; change 9. A capability, already exercised — Playfair ships |
| IMP-0515 | **REJECTED** | The gate working as designed. `rejected_reason` records that no rule change is owed |

**Left open with a `deferred_reason` and a real trigger (8).** Five of these could have been closed
on a needle matching a sentence this review just wrote. That is precisely how `IMP-0208` was closed
while still live ([`IMP-0224`](../../logs/improvement-log.jsonl),
[`IMP-0225`](../../logs/improvement-log.jsonl)), and I am not repeating it.

| Finding | `observable_at` | Why it stays open | `revisit_when` |
|---|---|---|---|
| IMP-0502 | V4 | The V4 step it reports is still unmoved; change 1 changes how it is *reported*, not whether it happened | the next test cycle after this build reaches DEV |
| IMP-0504 | V1 | Carries its own correctly-scoped self-deferral (§2.8) | **verbatim from its own field** |
| IMP-0507 | V1 | The flow arithmetic is still wrong; routed, not fixed | the FR-058 SDD amendment lands |
| IMP-0508 | V5 | Needs the write-then-observe re-run recorded, not a prose edit | a pipeline run records a definitive trigger test |
| IMP-0509 | V4 | **Fix is on disk** but proof is a rendered screenshot no session here can produce | a human opens the portal and reports whether a wrapped tile value overlaps |
| IMP-0510 | V4 | One half stale, one half **live** at `ds-tokens.css:176` (§2.4) | the navy heading colour is corrected and rendered |
| IMP-0511 | V5 | **Review 45 owns this analysis and I have not touched it.** Change 8 adds only the `deferred_reason` its §8 omits | **verbatim from review 45 §8**: seed `RoundStatisticsStaleAfterSeconds` in DEV, open the landing screen, record whether a computed figure appears |
| IMP-0514 | V3 | The live-reconciliation gate is delivery work (§2.5); the hole is open until it ships | the live `MaxLength` check exists and runs |

**Not read, and stated rather than implied:** 96 entries at `reviewer-deferred`, 0 at
`already-fixed`, 0 at `approved-not-applied`. `APPLIED` and `REJECTED` entries were not read — the
digest carries their lessons.

**Four standing `corrects` warnings are untouched by this review** (`IMP-0290`, `IMP-0298`,
`IMP-0320`, `IMP-0437`). I checked each against the 14 entries here: **none of the 14 carries
`corrects` naming anything this review proposes**, and none shares a class with a contradicting
conclusion. Those four belong to earlier reviews and clearing them is those reviews' bookkeeping,
not mine.

---

## 6. Digest impact

| | Before | After | State |
|---|---|---|---|
| Log entries | 512 | **513** (`IMP-0516`) | **done** — regenerated at draft time |
| Distinct teaching lessons | 511 | **512** (1 rejected, excluded) | **done** |
| Digest lines | 592 | **594** | **done** |
| Recurring classes (×≥2) | 41 | **41** | unchanged — `gate-scope-mismatch` was already recurring |
| Constraint rows (active) | 80 | 82 | on approval |
| `scripts/verify-*.py` | 52 | 54 | on approval |

**The digest is already regenerated and current, and that is a deliberate exception to
"regenerate last."** Appending `IMP-0516` made
[`logs/known-failure-modes.md`](../../logs/known-failure-modes.md) stale immediately, and a stale
digest is itself a gate failure that would block anyone else's build while this review waits.
`python3 scripts/generate-known-failure-modes.py --check` → *"current (513 entries)."* It will be
regenerated once more on approval, when the six status changes land.

**Note the corrected baseline:** review 45 §6 recorded 39 recurring classes against a log of 508.
The true figure at that time is not re-derivable here, but it is **41** now and was **41** before
`IMP-0516`, so the movement is in the four entries appended after review 45 was drafted, not in this
review.

---

## 7. Verification reached, per C-TECH-053

**V1** for every source claim: the TAD's cited paths, the `ui_kits/` tree, the token scale, both CSS
rules, `ds-tokens.css` L176 and L378, and `classify()`'s precedence.

**Executed, not read** — the distinction
[`improvement-agent.md` L150](../../agents/improvement-agent.md#L150) demands:
`verify-improvement-log.py --check` run four times (baseline, SIM A, SIM B, restore-verify), and the
line-height gate candidate run in three successive designs over the real corpus. §3.1 and §3.3 are
measurements, not readings.

**Not verified, and named:** whether the two `C-TECH-076` findings actually overlap when rendered
(V4 — needs a browser); whether seeding `RoundStatisticsStaleAfterSeconds` restores the screen (V5 —
review 45's, and still nobody's); whether the navy heading is the only remaining `ui_kits/`
divergence (I compared the README's 5 listed changes against shipped tokens, not against a render).

---

## 8. Applied

**APPROVED and APPLIED 2026-08-31**, after
[review 45](2026-08-30-improvement-review-2.md) and in that order, in one dispatch.
[`verify-improvement-log.py --check`](../../scripts/verify-improvement-log.py) exits **0** —
`C-TECH-061` green, both triggers cleared, 0 unread and 0 `awaiting-approval`.

| # | Change | Applied at | Entries moved |
|---|---|---|---|
| 1 | [`skills/how-to-apply-constraints.md`](../../skills/how-to-apply-constraints.md) — new step before Step 4: *"Before a FAIL on a V4/V5 requirement: could the evidence exist YET?"*, with the `deferred-to-pipeline` record | 2026-08-31 | `IMP-0503`, `IMP-0505` → APPLIED |
| 2 | [`scripts/verify-design-source-coverage.py`](../../scripts/verify-design-source-coverage.py) **(new)** | 2026-08-31 | — |
| 3 | `C-TECH-075` **(new, HARD)** in [`technology-constraints.md`](../../constraints/technology/technology-constraints.md), wired as build step `design-source-coverage` | 2026-08-31 | — |
| 4 | [`scripts/verify-css-line-height.py`](../../scripts/verify-css-line-height.py) **(new)** | 2026-08-31 | — |
| 5 | `C-TECH-076` **(new, HARD)**, wired as build step `css-line-height` | 2026-08-31 | — |
| 6 | [`skills/how-to-verify-a-platform-contract.md`](../../skills/how-to-verify-a-platform-contract.md) — *"An INFERENCE is not the check when the check is cheap"*, both named shapes | 2026-08-31 | — (`IMP-0507`, `IMP-0508` deferred) |
| 7 | [`agents/development-agent.md`](../../agents/development-agent.md) — third branch: the credential is **absent by design**, foreground retry skipped | 2026-08-31 | `IMP-0512` → APPLIED |
| 8 | [`logs/improvement-log.jsonl`](../../logs/improvement-log.jsonl) — `deferred_reason` on `IMP-0511` **and** the step-8 half in [`agents/improvement-agent.md`](../../agents/improvement-agent.md) | 2026-08-31 | `IMP-0516` → APPLIED |
| 9 | [`knowledge/technology/code-apps.md`](../../knowledge/technology/code-apps.md) — *"Self-hosting a named typeface"*, `@fontsource` check + base64 `data:` URI rule + the open-source-only caveat | 2026-08-31 | `IMP-0513` → APPLIED |
| 10 | [`skills/how-to-report-to-the-reviewer.md`](../../skills/how-to-report-to-the-reviewer.md) — rule 5 gains the finding's four-part template verbatim | 2026-08-31 | `IMP-0506` → APPLIED |

**Disposition: 7 APPLIED, 1 REJECTED (`IMP-0515`), 7 deferred with a reason and a trigger.**
Derived at apply time, not projected: **82** active constraint rows (`grep -rh '^| C-'`), **10**
retired, **54** `scripts/verify-*.py`, **70** build steps / **55** gates, digest **594** lines over
513 entries.

### Three deviations, each compelled by re-verification rather than chosen

**1. `IMP-0510`'s navy heading is DISPROVED as a defect, and §3.4's routing of it is WITHHELD.**
§2.4 measured `--text-heading: #002060` as the live half and routed a fix to
[`development-agent`](../../agents/development-agent.md). Re-read at apply time, the TAD now records
that value as **OQ-040, CLOSED 2026-08-30 by ADR-042**, *"by explicit reviewer instruction given
with the design system's own 'never navy' guidance in view."* A reviewer decision taken with the
conflicting guidance in front of them is a decision, not an oversight. **Applied as approved, this
review would have routed a delivery agent to undo a reviewer's explicit instruction.** The class fix
(changes 2/3) is unaffected and proceeded.

**2. Change 2's corpus measurement no longer reproduces, and the polarity proof replaces it.** §3.2
measured 1 finding / 1 true positive against the then-current TAD. TAD **Revision 7** has since read
`ui_kits/trustee-review-portal/` in full and cites it, so the gate now exits **0** over the working
tree. Both polarities were therefore run: against `HEAD`'s `docs/architecture/` it exits **1**,
naming that directory (7 files) — the real `IMP-0510` defect, 1 finding, 1 true positive, 0 false —
and the negative control `ui_kits/marketing-site/` is correctly silent in both. **The gate reports
the instance until the fix lands and then stops**, which is
[the polarity test](../../agents/improvement-agent.md) being passed rather than a clean run being
assumed.

**3. Change 8 was applied in BOTH halves its finding names, not the one the §3 table listed.**
[`IMP-0516`](../../logs/improvement-log.jsonl)'s `proposed_change.target` is
`logs/improvement-log.jsonl + agents/improvement-agent.md`; the table listed only the log.
`verify-improvement-log.py`'s subset-closure check **refused the partial closure** — correctly, per
`IMP-0047` — so `improvement-agent.md` step 8 also gained the rule that `revisit_when` alone
discharges nothing, that for a blocker it is a permanent red light, and the simulate-before-you-park
procedure. That is the durable half.

### Gate measurements at wiring time, both re-run against the real corpus

`verify-design-source-coverage.py`: `--selftest` **3 fixtures, 0 failures** (one of them the
negative control). Corpus: 18 supplied subdirectories, 1 in scope, PASS on the working tree, **1
finding / 1 true positive / 0 false** on `HEAD`.

`verify-css-line-height.py`: `--selftest` **2 fixtures, 0 failures**. Corpus: **2 findings, 2 true
positives, 0 false** — [`app.module.css:415`](../../src/code-apps/trustee-review-portal/src/styles/app.module.css#L415)
`.panelHeading` (20px, inherited ratio 1.10) and
[`ds.module.css:426`](../../src/code-apps/trustee-review-portal/src/styles/ds.module.css#L426)
`.cardTitle` (24px, ratio **0.92** — the line box is smaller than the glyphs). Against `HEAD~1` it
reports **3**, the third being `.statTileValue` at 32px, which is `IMP-0509`'s original defect; it
stopped being reported the moment that fix landed. **One defect in the gate itself was found by
running it over the real corpus and not by its fixtures**: the selector capture swallowed the
25-line explanatory comment above each rule, making the finding message unreadable. Fixed with a
comment-stripper that preserves newlines so line numbers stay true.

### ⚠ `css-line-height` is wired HARD and is RED today, on two true positives

This is stated plainly because it is a **new** blocking condition, and it was not what the reviewer
was told approving these reviews would produce. `C-TECH-061` is green and the improvement-log
blocker is gone — but the next build now stops at `css-line-height` until the two rules above
declare a `line-height`. Both are genuine defects of exactly the shape `IMP-0509` cost a human
eye to find, so the gate is not crying wolf; the fix is two one-line CSS declarations and it is
**delivery work under WBS 6.9**, not this agent's to author. Routed to
[`development-agent`](../../agents/development-agent.md) alongside §3.4's other items. Softening
the row to SOFT to keep the build green was available and was **not** taken — that would be
substituting different enforcement for approved enforcement.

### Not done, and named

The `verify-derived-counts.py` SOFT step reports **5 pre-existing drifted claims** in delivery
documents (the `rev_setting` row count at two pipeline-config lines, the secured-column count at two
Dev Summary lines, and the `REV Trustee.xml` header). None is this review's; all predate it, and
`improvement-agent-verify-script-count` — the one claim this review owns — was updated 52 → 54 in
the same change and is clean.
