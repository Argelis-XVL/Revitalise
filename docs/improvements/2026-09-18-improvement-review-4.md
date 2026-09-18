# Improvement Review — 2026-09-18 (4)

**Status:** ~~AWAITING — nothing has been applied. Draft written at step 6; the changes below land
only on `APPROVE IMPROVEMENTS`.~~ **APPLIED IN FULL 2026-09-18**, approved by Anna Southern. Two
claims in section 6 were measured false while applying and are corrected in place there.

**Trigger:** one unread `blocker` (IMP-0769), routed immediately per `agents/WORKFLOW.md`.

**Scope:** the one `unread` entry. 166 `reviewer-deferred` entries and 0 `awaiting-approval`
entries were excluded by activation step 2 and are named in section 5.

---

## 0. The question this review was dispatched to answer

The dispatching brief asked one thing: does IMP-0769 share the defended property with IMP-0763, or
is it a distinct failure mode wearing the same class label?

**It is distinct, and the distinction is exact.** IMP-0763 was an unresolved `{{TOKEN}}` sitting in
a value position with no matching `_unresolved` declaration. IMP-0769's file contained **no
placeholder at all** — measured, `grep -c "{{" provisioning/deploymentSettings/dev-settings.json`
returned 0 at the time the build failed. A whole key was absent, which is a different mechanism,
caught by a different gate, with a different remedy.

Answering that question properly meant running the recorded defence rather than reading it, and
that is where this review's substantive finding came from — see section 1.

---

## 1. Regression check — did the last review's changes work?

Two prior sittings on this same day are in scope.

### Review 2 (`docs/improvements/2026-09-18-improvement-review-2.md`) — `logs/class-defences.json` plus a `Defended by` column in the digest

**Has the class recurred?** Yes, once, as a *tag* — IMP-0769 carries
`config-placeholder-known-but-not-fixed`. It is not a recurrence of the defended property; it is a
mis-assignment of the label. Section 2 adjudicates it.

**Did the change work?** Partly, and the half that failed is the more important half.

It worked in its stated purpose: build-agent, reading a digest whose `Defended by` cell was filled,
proposed a **knowledge** change (populate the settings file) rather than proposing a gate that
already exists. Before the column existed, the two findings of 2026-09-18 both proposed building a
check into the very script that had caught them. That did not happen this time.

It failed in a way the record explicitly said was impossible. `logs/class-defences.json`'s own
`_README` states that the file *"under-claims by construction"* and that under-claiming *"is the
safe direction."* **That protection depends on every filled row's `property` being accurate, and
one of them is not.**

Measured, by running the gate rather than reading it:

| | |
|---|---|
| The row's recorded property | an unresolved `{{TOKEN}}` in a value position of `provisioning/deploymentSettings/*.json` with no matching `_unresolved` entry |
| What check 11 actually reaches | only the settings files the **pipeline config references** — `test-settings.json` and `prd-settings.json`. `settings files opened and read: 7`, of which 2 are in this directory |
| Live consequence, today | `provisioning/deploymentSettings/dev-settings.json` carries **3 undeclared `{{...}}` tokens** (`dataverse.groupTeams[0..2].entraGroupObjectId`) and the preflight exits **0** |

So a filled cell is telling the next agent that a property is defended across a directory, while a
live instance of that exact property sits undetected in that directory. The record over-claims —
the one direction its `_README` says it never does.

**This is the second instance of `gate-reassures-wrongly`, and it arrived within hours of the
first.** IMP-0766 (logged in review 2, same day) predicted that a recorded defence could go stale
and that nothing validates the record. This instance shows the failure does not need staleness: the
row was **over-stated at authoring time**, so a future check asserting "the named script still
exists and still exits 0" would have passed on it every day. Section 3, change 2, is the
generalisation that follows.

### Review 3 (`docs/improvements/2026-09-18-improvement-review-3.md`) — the identifier-namespace row and the id-allocation declarations

**Has the class recurred?** No. `python3 scripts/verify-requirement-id-uniqueness.py` exits 0 —
10 documents declaring 180 identifiers, 0 allocated more than once. The residual that review
recorded (the `A-nnn` assumption-register namespace, measured 3 true of 5 and therefore not wired)
is tracked as IMP-0768 and is unchanged.

### Closure-evidence audit

Both entries closed in review 2 against a V2 `observable_at` carry a `reobserved` naming the exact
command re-run and its result. IMP-0767, closed in review 3 at V1, likewise. No closure in either
review rested on a document asserting a fix.

---

## 2. Clusters and promotion decisions

One unread entry, one cluster.

```
CLUSTER: config-placeholder-known-but-not-fixed  (x1 new: IMP-0769)  → RETAGGED
Altitude:  CLASS BOUNDARY — the tag is wrong, and correcting it is the change.
           No new instance gate; no new general gate.
Ladder row: "reuse an existing class name verbatim when one fits" — it does not fit.
Becomes:   a corrected class_instance_of, a new logs/class-defences.json row for the
           property that actually caught it, and one clause in
           skills/how-to-log-an-improvement.md.
Retires:   nothing.
Cites:     IMP-0769, IMP-0763, IMP-0766.
Residual:  in dev, the membership assertion is VACUOUS — see 2.3.
```

### 2.1 The two mechanisms, side by side

| | IMP-0763 | IMP-0769 |
|---|---|---|
| What was in the file | a `{{TOKEN}}` present, undeclared | a key **absent**; zero tokens in the file |
| What the file said about it | nothing — silently missing a declaration | its own `_readme` named the omission and warned against exactly this |
| Which gate caught it | `verify-pipeline-config.py` check 11 | `verify-column-security-membership.py`, fail-closed case 2 |
| The remedy | add an `_unresolved` declaration | populate the absent key |
| Can a gate prevent a recurrence | yes, and it exists | yes, and it exists |

The reviewer's own framing in the dispatch — *"a file that KNOWS it's incomplete and says so, versus
one that's silently missing a declaration"* — is the distinguishing property, and it holds under
measurement. They are not the same class.

### 2.2 Is this the class working as intended?

For the gate, yes, entirely. `scripts/verify-column-security-membership.py` documents three
fail-closed cases and this was the second of them, firing correctly the first time a build reached
step 52 against the narrowed file. The file's own header predicted the failure in as many words.
**Nothing about that gate should be relaxed**, and the temptation to make it skip narrow files must
be refused: this is the gate standing between a special-category-data disclosure and a live
environment, and its non-membership invariant is the control.

For the class taxonomy, no. The label pulled an improvement dispatch to adjudicate a mechanism it
does not describe, and — because the label now carries a `Defended by` cell — it also attached a
defence claim to a finding that defence does not cover.

### 2.3 What running the gate turned up that reading it would not have

Development-agent's concurrent dispatch landed while this draft was being written, so both
measurements below are of the current tree:

- `no-trustee-in-column-security-profile` now exits **0** — 6 profile membership lists across 3
  settings files. The blocker is cleared.
- **In dev the assertion is vacuous.** Resolving trustee-facing teams per file: `test-settings.json`
  1, `prd-settings.json` 1, `dev-settings.json` **0**. Dev declares three teams and no trustee-facing
  one, so the gate passes there by having nothing to test, and reports `OK` in exactly the same
  words as the two files where it did real work.

Development-agent recorded a reasoned, explicit decision not to invent a dev trustee team, which is
correct — no live DEV team name for that persona has ever been resolved, and inventing one is the
`IMP-0011` shape. So this is a coverage residual, not a defect, and it belongs in the record rather
than in a gate.

---

## 3. Proposed changes

| # | Type | Target | Wiring | Cites |
|---|---|---|---|---|
| 1 | data | `logs/class-defences.json` — narrow the over-stated `property` | read by `generate-known-failure-modes.py` | IMP-0770, IMP-0766 |
| 2 | data | `logs/class-defences.json` `_README` — the property-authoring rule | same | IMP-0770, IMP-0766 |
| 3 | data | `logs/class-defences.json` — new row for the absent-key property | same | IMP-0769 |
| 4 | skill | `skills/how-to-log-an-improvement.md` — `class_instance_of` | activation read path for every logging agent | IMP-0769, IMP-0763, IMP-0767 |
| 5 | data | `logs/improvement-log.jsonl` — retag IMP-0769, append IMP-0770/0771 | validator | — |

**0 new constraints** (cap 3). **0 new gates or scripts.** 1 skill edit. 0 agent-file edits.

### Change 1 — narrow the recorded property to what the gate's input selection reaches

The `config-placeholder-known-but-not-fixed` row's `property` currently claims the whole directory.
It is rewritten to name the files check 11 opens, and `not_covered` gains both the live gap and the
measurement that decides what to do about it.

### Change 2 — the authoring rule, in the file's own `_README`

> A row's `property` states what the gate's own **input selection** reaches, established by running
> the gate and reading which inputs it opened — never by the directory or glob its command line
> names. A gate invoked on a directory may resolve its inputs from somewhere else entirely.

This is where the generalisation belongs. `_README` is read by whoever adds the next row, which is
the only moment the error can be made.

### Change 3 — record the property that actually caught IMP-0769

A new row, under a new class name, recording that `verify-column-security-membership.py`'s
fail-closed case 2 defends *"a settings file declaring `columnSecurityProfiles` with no `groupTeams`
to resolve membership against"*, wired at build step `no-trustee-in-column-security-profile`, with
the vacuous-dev-pass residual of 2.3 stated in `not_covered`.

### Change 4 — one clause in the logging skill

The skill currently says, in full: *"Reuse an existing class name verbatim when one fits; check
`logs/known-failure-modes.md` first… Inventing a near-duplicate class name defeats the mechanism."*
Every word of that pushes toward reuse and nothing states reuse's cost. That was the right balance
until the `Defended by` column shipped this morning; it is not any more, because a class label now
carries a defence claim, and a finding filed under a label inherits it.

The clause to add, after the existing sentence:

> **Reuse has a cost now, and it is new.** Since 2026-09-18 a class name carries a `Defended by`
> cell in `logs/known-failure-modes.md`, so filing a finding under a class asserts that the gate
> named in that cell covers your finding's mechanism too. Read the cell before reusing the name. If
> the property it describes is not the mechanism you just hit, the class does not fit however
> similar the surface looks — a missing declaration and an absent key are both "config incomplete"
> and have nothing else in common. Say so in the entry and propose the class name you think it
> needs; improvement-agent adjudicates the boundary.

### Change 5 — log bookkeeping

Retag IMP-0769 to `settings-file-narrowed-below-its-consumers`, close it, and append the two
findings this review produced.

---

## 4. Retirements

**Checked, none found.** 85 live constraint rows and 10 retired. Nothing in this review's cluster
replaces an existing rule: the two gates involved both remain necessary and neither subsumes the
other, and no constraint row was added, so there is no instance-level rule to supersede. The one
candidate considered and rejected was narrowing
`verify-column-security-membership.py`'s fail-closed case 2 — rejected for the reason in 2.2.

---

## 5. Findings left unprocessed

- **0 `awaiting-approval`.**
- **166 `reviewer-deferred`**, left untouched per activation step 2. Each carries a
  reviewer-accepted `deferred_reason`; the validator lists them in full on every run. One of them
  (IMP-0274) names no `revisit_when` and has been reported as such for some time — unchanged here.
- **0 `already-fixed`.**
- Six pre-existing `corrects` warnings (IMP-0290, IMP-0298, IMP-0320, IMP-0430, IMP-0437, IMP-0703)
  concern reviews from August and 2026-09-10. None names an entry this review acts on; checked
  individually.

---

## 6. Digest impact

**Two of the three predictions below were wrong, and both were measured wrong after the digest was
actually regenerated.** The withdrawn wording is retained so the correction is visible.

- ~~`config-placeholder-known-but-not-fixed` drops from **x8** to **x7** and loses IMP-0769 from its
  findings list.~~ **It stays at x8.** IMP-0769 did leave the row, but IMP-0771 — appended by this
  review, and genuinely an undeclared-placeholder finding — took the vacated slot. The count was
  arithmetic nobody had done; the substantive half of the claim (IMP-0769 no longer appears there)
  is true and was verified.
- Its `Defended by` cell's `Covers:` line narrows, and its `NOT covered:` line gains the
  directory-glob gap and the 3-of-55 measurement. **Confirmed on the regenerated file** — both the
  narrowed `Covers:` text and the `DO NOT PROPOSE EXTENDING CHECK 11` warning render in full.
- ~~A new row appears for `settings-file-narrowed-below-its-consumers` (x1), with its defence
  recorded from day one.~~ **No row appears.** `generate-known-failure-modes.py` builds that table
  from classes with **two or more** members (`len(fs) >= 2`), and this class has one. The recorded
  defence is therefore **inert until a second instance is logged** — at which point it renders
  automatically, which is exactly the moment an agent would otherwise propose building the gate
  that already exists. The record is correct and its read path is deferred, not broken. Left as is
  rather than changing the generator's threshold: the reviewer approved a specific change set, a
  recurring-class table is meant to list recurring classes, and one-member rows would dilute the
  promotion-ladder signal the table exists to carry. **Stated here rather than claimed as
  delivered**, per `C-TECH-053`.

Regenerated with `python3 scripts/generate-known-failure-modes.py`, verified current with
`--check`. The regeneration drifted the registered `CURRENT SIZE` claim in the generator's own
docstring from 710 to 713 lines — corrected in the same change, in **both** the `scripts/` copy and
its `.engine/` twin, which were byte-identical before this edit.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-18-improvement-review-4.md

Findings processed: 1 unread  →  1 cluster
Regression check:   2 prior changes audited, 1 class recurred (as a tag, not as the property)
Proposed:           0 constraints (cap 3), 0 gates/scripts, 1 skill/knowledge edits,
                    0 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 0 left as notes
Digest:             will regenerate — 1 class retagged, 1 defence row added, 1 narrowed

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied — 2026-09-18

Approved by Anna Southern as drafted. Re-verified before applying: the column-security gate
re-run (exit 0), the pipeline preflight's input selection re-measured (2 files in that directory),
the routed item re-measured and still live, and the validator's `corrects` warnings re-read — none
names an entry this review touches.

| # | Landed | Where |
|---|---|---|
| 1 | The over-stated property narrowed to the two files the check opens; `not_covered` gained the live gap and the 3-of-55 measurement | `logs/class-defences.json` |
| 2 | The authoring rule — a property comes from a gate's measured input selection, never its command line | `logs/class-defences.json` `_README` |
| 3 | New defence row for `settings-file-narrowed-below-its-consumers`, with the vacuous-dev-pass residual | `logs/class-defences.json` |
| 4 | The reuse-has-a-cost clause | `skills/how-to-log-an-improvement.md` |
| 5 | IMP-0769 retagged and closed; IMP-0770 closed; IMP-0771 left open with a routed `deferred_reason` | `logs/improvement-log.jsonl` |
| 6 | `CURRENT SIZE` claim 710 → 713, in both copies | `scripts/generate-known-failure-modes.py` and its `.engine/` twin |

**Nothing was withheld and nothing was narrowed at apply time.** Every approved change landed as
worded. The only deviations are in this document's own section 6, where two predictions about the
regenerated digest measured false and are corrected in place there.

**Change 4 lands in the `.engine` submodule**, since `skills/` is a symlink into it. It is written
to the working tree and **not committed or pushed** — no instruction to commit was given, and
publishing it requires the submodule push before the pointer bump, in that order.

### Entry left open

**IMP-0771** — three undeclared placeholders in `provisioning/deploymentSettings/dev-settings.json`.
Delivery work in a directory this agent does not edit. Re-measured at apply time: still no
`_unresolved` key, still three tokens. Carries a `deferred_reason` and a `revisit_when` naming the
command that settles it, so it reports as a reviewer-accepted deferral rather than as an entry
nobody looked at.

### Not fixed here, and deliberately so

Three other registered count claims have drifted and belong to `development-agent`: the dev
summary's secured-column count in two places (says 69, source has 75) and the Trustee role file's
header (says 53, source has 59). The check is SOFT and does not block a build. Not this review's
to correct — a review corrects the drift it causes.
