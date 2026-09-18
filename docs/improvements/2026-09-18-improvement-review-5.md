# Improvement Review — 2026-09-18 (5)

**Status:** ~~AWAITING — nothing in section 3 has been applied; those changes land only on
`APPROVE IMPROVEMENTS`. The **section 0 data fix is already on disk**, authorised in the dispatch as
a correction of this agent's own output against a schema the reviewer had already approved, and it
is what unblocks the halted build.~~ **APPLIED IN FULL 2026-09-18**, approved by Anna Southern as
written. See section 8.

**Trigger:** one unread `blocker` (IMP-0772), routed immediately per `agents/WORKFLOW.md`.

**Scope:** the one `unread` entry. 167 `reviewer-deferred` entries and 0 `awaiting-approval`
entries were excluded by activation step 2 and are named in section 5.

---

## 0. The fix that has already landed, and the command that proves it

`logs/class-defences.json` carried two fields whose values were prose where the checker parses a
literal. Both are corrected, and the correction is confirmed by running the gate — not by re-reading
the file:

```
$ python3 scripts/verify-class-defences.py
class-defences: OK
  4 recorded defence(s), 24 reference(s) resolved (scripts, symbols, build steps, review documents)
EXIT=0
```

| Field | Was | Now |
|---|---|---|
| `config-placeholder-known-but-not-fixed`.`recorded_by` | `docs/…-review-2.md, narrowed by docs/…-review-4.md` | `docs/improvements/2026-09-18-improvement-review-2.md` |
| same row, new key `narrowed_by` | — | `docs/improvements/2026-09-18-improvement-review-4.md` |
| `settings-file-narrowed-below-its-consumers`.`wired_at` | `…-build.yml (no-trustee-in-column-security-profile, the last of 52 steps)` | `…-build.yml (no-trustee-in-column-security-profile)` |

**The audit trail was not dropped to satisfy the parser.** The narrowing citation moved to a new
`narrowed_by` key rather than being deleted, because `recorded_by` answers *"which review recorded
this defence"* and review 2 is the honest answer to that. Section 3 change 3 makes `narrowed_by` a
validated field so that it cannot rot the way an unvalidated key would.

### A third defect, found while fixing the second, that the finding did not notice

The parenthetical this fix removed was **also factually wrong**. `no-trustee-in-column-security-profile`
was recorded as *"the last of 52 steps"*; the build config carries **89** named steps
([`config/revitalise-grant-automation-build.yml`](config/revitalise-grant-automation-build.yml#L518)).
So a hand-typed derived count sat inside a data file that no derived-counts registry watches. It is
gone rather than relocated — a count nothing verifies is worth less than no count. Logged as
IMP-0774.

---

## 1. Regression check — did the last review's changes work?

### Review 3 (`docs/improvements/2026-09-18-improvement-review-3.md`) — `scripts/verify-class-defences.py`

**The gate worked, exactly as designed, and that is the finding.** Review 3 shipped this checker on
the morning of 2026-09-18 to stop `logs/class-defences.json` making claims nobody could check.
Review 4, the same day, edited that file three times and wrote two non-conforming values into it.
The gate caught both, with precise messages, at the next build.

So this is **not** a `gate-cannot-fail` case and needs no escalation. The gate fired on the right
thing, the first time it had anything to fire on.

**What it cost is the point.** It fired at build step 11 of 83, in another agent's dispatch, hours
later — rather than in the dispatch that introduced the defect, where the fix was thirty seconds of
work. The gap is not in the gate; it is in this agent's closing checklist, which has no clause for
*a data file this review edited*. Measured:

```
$ grep -rn 'verify-class-defences' agents/ skills/ constraints/
(no output — 0 matches)
```

Review 4's own section 6 records the verification it ran: `generate-known-failure-modes.py --check`.
That is the **generator**, and the generator is deliberately forgiving — its own docstring says a
malformed record yields `{}` rather than failing, so an optional annotation can never block a
regeneration. **The one command a review naturally runs after editing that file is the one command
that structurally cannot see this defect.** That is change 1.

### Review 4 (`docs/improvements/2026-09-18-improvement-review-4.md`) — the `_README` authoring rule and the logging-skill clause

**Held.** Review 4's property-authoring rule (state the property from the gate's measured input
selection) was not violated by anything in this incident — both malformed fields were *citation*
fields, not `property`. The rule it added is about a different failure and remains untested.

### Closure-evidence audit

IMP-0769, closed by review 4, is `observable_at` V2 and was closed on a re-run of
`verify-column-security-membership.py`. That is an execution at the level the defect was visible at.
Sound.

---

## 2. Clusters and promotion decisions

```
CLUSTER: prose-appended-to-a-field-a-validator-parses-as-a-literal  (x2 measured: IMP-0657, IMP-0772)
Altitude:   CLASS — the instance is class-defences.json; the class is every validated field this
            agent writes, across at least three different files
Ladder row: a second instance in a different file, after a prose fix for the first, at the same
            altitude → generalise the rule, keep it prose, and add the mechanical half where the
            validator can carry it
Becomes:    changes 1–4 below
Retires:    nothing
Cites:      IMP-0772, IMP-0657, IMP-0755, IMP-0572, IMP-0644
Residual:   nothing detects the shape in a field no validator reads at all. Accepted: such a field
            is prose by definition, and the rule is scoped to fields something resolves.
```

### 2.1 Why this is one class and not a `class-defences.json` quirk

`agents/improvement-agent.md` already carries a section titled *"Two field shapes that cost a
validator round-trip each"*. It names `evidence_grep` (a needle must fit one line), `excluded_by`
(**"is a PATH field… a path with an explanatory clause appended fails as *'names …, which does not
exist'*"**) and the `ensure_ascii` rule. That third bullet is this exact defect, in a different
file, written down before today — including the misleading failure message it produces.

The section did not prevent today's incident, and the reason is structural rather than careless:
**it is an enumeration of fields, and an enumeration is only as good as its completeness at the
moment someone needs it.** `excluded_by` was on the list. `recorded_by` and `wired_at` were not:

```
$ grep -c 'recorded_by\|wired_at' agents/improvement-agent.md
0
```

An author checking the list correctly concludes their field is not one of the tricky ones. The fix
is to state the **rule** — *a field something resolves carries the bare literal* — and demote the
bullets to instances of it, so the question becomes *"what parses this field?"* rather than *"is it
on the list?"*.

### 2.2 The half the validator can carry

Two of today's three error messages were **accurate and misleading at the same time**:

> `'config-placeholder-known-but-not-fixed'.recorded_by names docs/…-review-2.md, narrowed by
> docs/…-review-4.md, which does not exist.`

Both documents exist. The value does not. A reader — including the build-agent that reported this —
spends its first minutes looking for a missing document, because the message names the failure
correctly in a register that describes a different problem. The checker already holds everything it
needs to say so: if the value fails `.exists()` **and** contains a second `docs/` path or a comma,
the defect is the field's shape, and the message should say which literal to write. Same for a
`wired_at` step name whose text before the first comma *is* in the config.

This is a shape check on data the gate already parses — not a prose gate — so it is outside the
48%–100%-false instrument this repository has measured five times.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | agent | `agents/improvement-agent.md` | closing checklist gains the data-file validator clause | IMP-0772, IMP-0773 | NO — instruction | N/A |
| 2 | agent | `agents/improvement-agent.md` | the field-shape section becomes a rule, not a list | IMP-0772, IMP-0657 | NO — instruction | N/A |
| 3 | script | `scripts/verify-class-defences.py` **and its `.engine/` twin** | validate `narrowed_by`; name the shape defect instead of reporting a missing file | IMP-0772 | YES — `python3 scripts/verify-class-defences.py --selftest` | **already wired** — `HARD` at [`config/revitalise-grant-automation-build.yml`](config/revitalise-grant-automation-build.yml#L121), step `class-defences` |
| 4 | other | `logs/class-defences.json` `_README` | the field-shape rule, where the next row is authored | IMP-0772 | NO — authoring guidance | N/A |
| 5 | other | `logs/improvement-log.jsonl` | close IMP-0772 and IMP-0774, park IMP-0773 | — | YES — `verify-improvement-log.py --check` | N/A |

**0 new constraints** (cap 3). **1 gate/script edit.** 0 skill/knowledge edits. 2 agent-file edits.
0 retirements.

### Change 1 — the closing checklist gains the data file

Added to *"Where your executable output goes — and what you must run before closing"*:

> **And run the gate that VALIDATES any DATA file this review edited.** The block above is written
> for executables, and an increasing share of this agent's output is data —
> `logs/class-defences.json`, `logs/improvement-log.jsonl`, `config/gate-baselines.json`,
> `contract/known-exceptions.json`. A data file with a validator behind it is an executable's input,
> and editing it without running that validator is the same omission as shipping a script without
> its selftest.
>
> **And the forgiving READER is not the validator.** Where a data file has both — a generator that
> renders it and a gate that checks it — the generator is usually written to swallow a malformed
> record rather than block a regeneration, so it is the one command that structurally cannot fail on
> your edit. `generate-known-failure-modes.py --check` reported the digest current across both of
> `IMP-0772`'s malformed rows.
>
> ```bash
> git diff --name-only -- logs/ config/ contract/     # every data file this review touched
> python3 scripts/verify-class-defences.py            # …then the gate that validates each one
> python3 scripts/verify-improvement-log.py --check
> ```

### Change 2 — the field-shape section states the rule and keeps the list as examples

The section heading and opening become:

> ### Fields a validator RESOLVES carry the bare literal, and nothing else
>
> **This is the rule. The bullets are instances of it, and the list has never been complete at the
> moment it was needed.** If anything downstream calls `.exists()`, `re.match()` or `in` on a value,
> then a comma, a second path or an explanatory clause appended to it is not extra information — it
> is a different value, and it fails as *"names '…', which does not exist"* while every document it
> names sits on disk. The narration goes in a prose field beside it. **Ask what parses the field,
> not whether it appears below**: `excluded_by` was on this list and `recorded_by` and `wired_at`
> were not, which is exactly how one review wrote two of them and halted the next build
> (`IMP-0772`).

and gains two bullets:

> - **`logs/class-defences.json`: `recorded_by`, `since` and `narrowed_by` are PATH fields, and
>   `wired_at`'s parenthesised part is a build-step name matched verbatim against the config.**
>   A citation chain needs a second field, never a compound string.

### Change 3 — the checker names the shape defect

Three edits to `scripts/verify-class-defences.py`, mirrored byte-identically into
`.engine/scripts/verify-class-defences.py` (the two are an unsplit duplicate today, and the build
runs the `scripts/` copy):

1. `narrowed_by` joins `since` and `recorded_by` in the document-existence loop, so the key added in
   section 0 is validated rather than inert.
2. Where such a field fails `.exists()` **and** contains a second `docs/` path or a comma, the
   message becomes `FIELD IS NOT A BARE PATH`, quoting the first path it found as the value to
   write.
3. Where a `wired_at` step is absent from the config **but its text before the first comma is
   present**, the message becomes `STEP NAME CARRIES TRAILING PROSE`, quoting the bare step name.

Two selftest fixtures are added — a compound `recorded_by` and a prose-padded `wired_at` — which are
precisely the two cases the eleven existing fixtures do not cover, because they were written from
the same mental model as the regex.

**The corpus measurement is 4 rows and will be reported at apply time**, per the corpus rule. Note
that the amendment cannot produce a new *finding*: it only re-words messages the gate already
emits, so its precision is that of the existing checks.

### Change 4 — the rule in the file's own `_README`

> **EVERY CITATION FIELD IS A BARE LITERAL.** `recorded_by`, `since` and `narrowed_by` hold one
> path and nothing else; `wired_at` holds `<config path> (<step name>)` with the step name exactly
> as the config spells it. `verify-class-defences.py` resolves all four, so an appended clause —
> *"…, narrowed by X"*, *"…, the last of 52 steps"* — is a different value, not a richer one. Put
> the narration in `property` or `not_covered`, and **run the gate before committing**: it is under
> a second and it is the only thing that reads this file strictly.

### Change 5 — log bookkeeping

Close IMP-0772 (the data fix, already applied and re-observed) and IMP-0774 (the wrong step count,
removed in the same edit). Park IMP-0773 — the closing-checklist gap — at this review's gate.

---

## 4. Retirements

**Checked, none found.** 85 live constraint rows and 10 retired
(`grep -rh '^| C-' constraints/ --include='*.md' | wc -l`). This review adds no constraint, so
there is no instance-level rule for a general one to supersede.

One candidate was considered and rejected: **deleting the `not_covered` prose from the two
class-defences rows** on the grounds that it is unvalidated text that can rot. Rejected — it is the
half that stops a class name being read as fully defended, which is the whole reason the file
exists.

---

## 5. Findings left unprocessed

**Deferred:** none

- **0 `awaiting-approval`.**
- **167 `reviewer-deferred`**, left untouched per activation step 2. Each carries a
  reviewer-accepted `deferred_reason`. One (IMP-0274) names no `revisit_when` and has been reported
  as such for some time — unchanged here.
- **0 `already-fixed`.**
- Seven pre-existing `corrects` warnings (IMP-0290, IMP-0298, IMP-0320, IMP-0430, IMP-0437,
  IMP-0703, IMP-0763). Checked individually: none names an entry this review acts on. IMP-0763 is
  the closest — it concerns the same data file — but IMP-0765 corrects its *property* claim, which
  this review does not touch.

---

## 6. Digest impact

Predictions, to be measured after regeneration rather than asserted now:

- `class-defence-record-malformed-reference` reaches **x1** and therefore renders **no** recurring-class
  row (`generate-known-failure-modes.py` builds that table from classes with two or more members).
  The lesson still reaches the per-finding digest lines.
- The `Defended by` cells for the two edited rows are unchanged in substance: the generator renders
  `property`, `defended_by` and `not_covered`, none of which this review's data fix altered.
- Digest currently 714 lines. The `CURRENT SIZE` claim registered in
  `generate-known-failure-modes.py`'s docstring will drift on regeneration and is corrected in the
  same change, in **both** copies, per the closing checklist.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-18-improvement-review-5.md

Findings processed: 1 unread  →  1 cluster
Regression check:   2 prior changes audited, 0 classes recurred (the new gate fired correctly)
Proposed:           0 constraints (cap 3), 1 gates/scripts, 0 skill/knowledge edits,
                    2 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 0 left as notes
Digest:             will regenerate — 3 findings appended, 0 recurring classes added

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied — 2026-09-18

Approved by Anna Southern as written. **Re-verified before applying**, per activation step 8: the
validator's `corrects` warnings re-read (seven exist; none names an entry this review acts on), and
both of section 2's premises re-measured rather than re-read —
`grep -rn 'verify-class-defences' agents/ skills/ constraints/` still returns nothing, and
`grep -c 'recorded_by\|wired_at' agents/improvement-agent.md` still returns 0. Nothing was
withheld and nothing was narrowed.

| # | Change | Where | Entries |
|---|---|---|---|
| 1 | closing checklist gains the data-file validator clause | `agents/improvement-agent.md` (`.engine`) | IMP-0773 |
| 2 | field-shape section becomes a rule, with the two missing fields named | `agents/improvement-agent.md` (`.engine`) | IMP-0773 |
| 3 | `narrowed_by` validated; two shape-aware messages; 3 selftest fixtures | `scripts/verify-class-defences.py` + `.engine/` twin | IMP-0772 |
| 4 | `EVERY CITATION FIELD IS A BARE LITERAL` authoring rule | `logs/class-defences.json` `_README` | IMP-0772, IMP-0774 |
| 5 | IMP-0772, IMP-0773, IMP-0774 closed | `logs/improvement-log.jsonl` | all three |

### The corpus measurement, and the one that actually proves the polarity

**Current corpus: 4 rows, 25 references resolved, 0 findings — correct, because the data is fixed.**
A clean run over corrected data proves only that the amendment is not noisy. So the gate was also
replayed against **the exact data that caused the incident**, recovered with
`git show HEAD:logs/class-defences.json`:

```
FIELD IS NOT A BARE PATH - 'config-placeholder-known-but-not-fixed'.recorded_by holds
  '…-review-2.md, narrowed by …-review-4.md'. … and 2 of the 2 document(s) it names DO exist.
  The defect is the field's shape, not a missing file. Write the bare path (…-review-2.md) …

STEP NAME CARRIES TRAILING PROSE - 'settings-file-narrowed-below-its-consumers'.wired_at claims
  step 'no-trustee-in-column-security-profile, the last of 52 steps', which is not in
  config/…-build.yml — but 'no-trustee-in-column-security-profile' IS. The gate is wired; the
  field is not. … Write '…-build.yml (no-trustee-in-column-security-profile)'.
```

**2 findings, 2 true positives.** Both previously read *"which does not exist"* about documents
that do exist; both now name the defect and quote the literal to write. The file was restored from
the scratch copy afterwards and confirmed byte-identical with `cmp`.

The amendment **cannot** raise a finding the gate did not already raise — it only re-words two
existing branches and validates one new optional field — which is why the 0-finding clean run is
the right result rather than a suspicious one.

### Selftest: 14 fixtures, up from 11

The three added are `compound-path-is-named-as-a-shape-defect`,
`prose-padded-step-name-is-named-as-a-shape-defect` and
`narrowed-by-is-validated-like-the-other-citations`. They exist because **all eleven original
fixtures supply a well-shaped field and vary only what it points at** — written in one sitting from
the same mental model as the regexes, so none of them could see a field whose *shape* is wrong.
That is the fixtures-encode-the-author's-assumptions failure, measured on this gate's own selftest.

### One deviation from the draft, stated rather than silent

IMP-0773 was logged at `observable_at` **V2** and is closed at **V1**. The defect is a missing
clause in a tracked instruction file, which a grep settles; V2 described its *consequence* — a red
build — not its visibility. The level was corrected at closure rather than a hollow `reobserved`
being written to satisfy the higher one, and the correction is recorded in the entry's `applied_by`.

### Verification run

`verify-class-defences.py` exit 0 (4 defences, 25 references) and selftest 14/14, in **both** the
`scripts/` copy and its `.engine/` twin, confirmed byte-identical with `cmp`;
`verify-improvement-log.py --check` OK — 771 entries, **0 unread, 0 awaiting-approval**;
`verify-derived-counts.py` OK, 10 of 10; `verify-build-config.py` OK;
`verify-engine-instance-split.py` exit 0; `verify-review-document.py` OK;
`generate-known-failure-modes.py` regenerated — 771 entries, 764 lessons, 716 lines.

**Not verified:** the full 83-step build. Step 11 was the red one and is now green in isolation;
build-agent re-dispatches to prove the rest.
