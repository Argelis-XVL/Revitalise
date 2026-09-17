# Improvement Review — 2026-09-17

**Status: APPLIED 2026-09-17.** ~~DRAFT — parked at its gate. `APPROVE IMPROVEMENTS` has not been
given. Nothing in §3 has been applied; §8 is empty by design.~~ Superseded on the keyword: 11 of
the 21 rows in §3 landed, 3 were withheld on measurements taken at apply time, and 7 were not
applied. §9 is the record, and it names the 7 rather than dropping them.

Processed: **29 findings → 13 clusters.** 28 were `unread` at dispatch; the 29th
([IMP-0752](../../logs/improvement-log.jsonl)) was logged by this review after measuring a
premise the dispatch brief asked to be checked.

---

## 0. The one thing to read first

**Four of the twenty-one proposed changes land in a different git repository from the other
seventeen, and this review is the first one written since that became true.**

`agents/`, `skills/` and `templates/` are symlinks into `.engine`, a submodule pinned at
`ee9c101` on `Argelis-XVL/Agent-Delivery-System`. A change to a skill, an agent file or a
template commits **there** and needs a pointer bump here. `constraints/`, `scripts/`, `config/`,
`knowledge/`, `contract/`, `docs/` and `logs/` are ordinary instance files.

And a script change is **two** edits, not one: `scripts/verify-engine-instance-split.py` reports
**57 of 87 scripts as unsplit duplicates**, so the instance copy and its `.engine` twin must move
together or the split gate reports the divergence. Every `script` row in §3 carries both paths.

[`agents/improvement-agent.md`](../../agents/improvement-agent.md#L381)'s own Outputs table does
not say any of this — `grep -n '\.engine' agents/improvement-agent.md` returns **0 hits**, and the
only file under `agents/` or `skills/` that mentions the submodule at all is
[`skills/how-to-promote-a-finding.md` §6](../../skills/how-to-promote-a-finding.md#L290), which
answers a *different* question (is a learning engine-level or client-specific, not where the file
commits). Row 14 fixes it.

**Applied 2026-09-17, so the two measurements above are now historical.** `grep -n '\.engine'
agents/improvement-agent.md` returns hits, not 0 — row 14 landed. And the split figure re-measured
after this review's own additions is **60 of 88**, not 57 of 87, because every new gate here ships
as an instance copy and an engine twin. Both figures are left in place as written rather than
edited, because they are what the draft measured and what its reasoning rests on.

---

## 1. Regression check — did the last review's changes work?

Previous review: [2026-09-10-improvement-review-2.md](2026-09-10-improvement-review-2.md), 17 rows
applied 2026-09-11.

| Prior change | Class it targeted | Recurred? | Verdict |
|---|---|---|---|
| [`verify-improvement-log.py`](../../scripts/verify-improvement-log.py#L764) appendix read | `gate-couples-two-files-by-size` | n/a — this batch's [IMP-0745](../../logs/improvement-log.jsonl) **is** that change, applied inline | **Landed.** Verified by execution, not by reading — see below |
| [`report-dispatch-share.py`](../../scripts/report-dispatch-share.py) (new, SOFT) | improvement-agent dispatch share | — | **Working, and it reports bad news.** 30.4% (93 of 306) |
| [`how-to-promote-a-finding.md`](../../skills/how-to-promote-a-finding.md#L132) §3a duplicate check | review proposes finished work | NO | **Working.** Used on all 13 clusters here; it caught [IMP-0745](../../logs/improvement-log.jsonl) as already-applied |
| [`verify-wbs-chain.py`](../../scripts/verify-wbs-chain.py) INERT exceptions | `gate-fires-on-nothing` | NO new instance | Working — but cluster F finds a *different* hole in the same script, exactly as last review did |
| [`.engine/scripts/kb.py`](../../.engine/scripts/kb.py) `ensure_ascii=False` | `serialisation-default-invalidates-evidence-needle` | **YES — [IMP-0733](../../logs/improvement-log.jsonl)** | **Recurred after a prose change.** Cluster G escalates it to a gate |
| [`architect-agent.md`](../../agents/architect-agent.md) consequence trace | `approved-document-internally-inconsistent` | **YES — now x34** | **Third consecutive review recording this recurrence.** Cluster C finally has a mechanical half |
| [`verify-derived-counts.py`](../../scripts/verify-derived-counts.py) wired SOFT | `hand-maintained-count-drifts-from-source` | No *new finding*, but **the gate is RED right now** | Row 21. Fifth consecutive review paying this |

**The one that matters: a class recurred after a prose fix.** The previous review put
`ensure_ascii=False` into `kb.py` (a real mechanical fix, in one script) and stated the rule as
prose in two agent-specific documents. Two days later lead-agent — editing the same file through a
fallback path, having loaded neither document — rewrote it with the default and reddened an
unrelated entry's needle. The ladder is explicit that a recurrence after prose is evidence of wrong
altitude. Row 4 moves it to the file's own gate, where it reaches whoever opens the file next
regardless of which agent they are.

**Execution, not reading, on the one behavioural assertion.**
[IMP-0745](../../logs/improvement-log.jsonl) asserts `verify-improvement-log.py` did not read the
appendix. Re-run at draft time: the appendix read is at
[line 764](../../scripts/verify-improvement-log.py#L764) and the IMP-0555 error is gone — the gate
exits 1 solely on the blocker trigger this review exists to clear. The fix was applied inline by the
session that found it; the entry is closed here, not re-proposed.

**Closure-evidence audit.** Of the 29 findings, 6 carry `observable_at` at V1 or above and so cannot
be closed on a document. Four of those six are closable here with a re-run I can perform; two
([IMP-0734](../../logs/improvement-log.jsonl) at V3, [IMP-0737](../../logs/improvement-log.jsonl) at
V4) need a credentialled session and stay open with a `deferred_reason` and a named owner. See §5.

---

## 2. Clusters and promotion decisions

Thirteen clusters. The two consolidations — A and B — are where most of the value is: **ten
findings become two skill sections**, because ten authors each hit the same property from a
different artefact.

---

```
CLUSTER A: an artefact answers only the question its CONSTRUCTION can answer
           (x5: IMP-0736, IMP-0740, IMP-0744, IMP-0748, IMP-0751)
Altitude:  CLASS — five instances, five different artefact types, one property
Ladder row: "an agent had the information and still did the wrong thing" → skill edit
Becomes:   skills/how-to-verify-a-platform-contract.md, one new section (row 8)
Retires:   nothing — the existing "absence of rows" section stays; the new one generalises
           and cites it
Cites:     IMP-0736, IMP-0740, IMP-0744, IMP-0748, IMP-0751
Residual:  no gate is possible. Which question an artefact was used to answer exists only in
           the reasoning, never in the repository. Stated, not papered over.
```

A static capture of an unanswered form evidences **markup, never behaviour** (0736). A client's
rendered pack evidences **what its readers see, never what the system stores** (0740). A flow's
trigger schema evidences **what the contract accepts, never what the sender sends** (0744). A
documentation page evidences **what a source contains, never how it is reached** (0751). And two
observers of the **same surface** are one observation, not two (0748).

That skill's [*absence of rows*](../../skills/how-to-verify-a-platform-contract.md#L636) section
already carries the special case — *"the absence of rows is not evidence of the absence of events"*.
These five are the general case, and that section becomes an example of it rather than the whole
rule.

---

```
CLUSTER B: the artefact's own AUTHORED statement was not read before its meaning was inferred
           (x5: IMP-0735, IMP-0731, IMP-0743, IMP-0742, IMP-0730)
Altitude:  CLASS — five instances; one of them (0730) is itself an instance of the class,
           which is why 0731 exists
Ladder row: skill edit, PLUS "a tool could catch it mechanically" for the cheap half
Becomes:   skill rule (row 9) + dump-entity-attributes.py emits descriptions (row 6)
Retires:   nothing
Cites:     IMP-0735, IMP-0731, IMP-0743, IMP-0742
Residual:  IMP-0730's own proposal is WITHHELD — see §4. Its premise measured false.
```

A column was re-purposed from its **name** without opening its description (0735). A finding
asserted the repository "failed to flag" a defect the cited file flags in its own `<Description>`
(0731). A domain concept was invented from **two data samples** while the domain model already
separated them (0742). A column's description was incomplete and a reader reasonably inferred a
counterpart that does not exist (0743).

Row 6 is the part that matters more than the prose: `dump-entity-attributes.py` does **not** emit
descriptions today (`grep -n 'description' scripts/dump-entity-attributes.py` → 0 hits), so a triage
pass working from a field list never has them to hand. Making the right thing cheap beats telling
people to do the expensive thing.

---

```
CLUSTER C: a design document's claim about the shipped schema is not checked against the schema
           (x2: IMP-0723, IMP-0725)
Altitude:  CLASS — and it is the mechanical half C-DOM-001 has been missing
Ladder row: "a tool could catch it mechanically"
Becomes:   two new checks in scripts/verify-design-doc-claims.py + engine twin (rows 1, 2)
Retires:   nothing — this EXTENDS C-DOM-001's existing Verify By, it does not replace a rule
Cites:     IMP-0723, IMP-0725
Residual:  the mapping check only catches a rev_* name no Entity.xml declares. A document that
           maps a field to the WRONG existing column still passes. Named, not hidden.
```

Both premises grepped and both hold.
[`docs/development/…form-validation-spec.md:293`](../../docs/development/revitalise-grant-automation-form-validation-spec.md#L293)
still maps form field 63 to `rev_application.rev_currentlyworking`; that column survives in
`Entity.xml` **only inside a rename comment** (`RENAMED rev_currentlyworking -> rev_employmentstatus,
2026-08-17`). And all four columns [IMP-0725](../../logs/improvement-log.jsonl) names —
`rev_locationarea`, `rev_helperorganisation`, `rev_helperrelationship`, `rev_agerange` — appear in
`Other/FieldSecurityProfiles.xml` **only in comments**, never as a `FieldPermission` under
`REV_TrusteeRestricted`, so all four are trustee-readable today.

**My own first count was a false positive and this is worth recording**: `grep -c rev_locationarea`
returned 2, which reads as "it is in the profile". Both hits were prose comments. That is precisely
the step-6 premise-grep rule catching the review's own draft.

[`C-DOM-001`](../../constraints/domain/domain-constraints.md#L34) already names
`verify-design-doc-claims.py` as its `Verify By`, and `docs/development` is outside the roots the
build passes it ([build config line 541](../../config/revitalise-grant-automation-build.yml#L541)).
**No new constraint is needed** — the rule exists and was unenforced in two directions.

---

```
CLUSTER D: a kind of INPUT arrives with no checklist, only an owner
           (x2 here, x5 lifetime: IMP-0726, IMP-0739; APPLIED siblings IMP-0028, IMP-0384, IMP-0510)
Altitude:  CLASS — FIFTH instance. The altitude rule forbids a fourth instance patch here.
Ladder row: "second instance → generalise"
Becomes:   a declared class→checklist map in the skill + a gate that asserts it (rows 7, 11)
Retires:   nothing
Cites:     IMP-0726, IMP-0739
Residual:  the gate proves a checklist EXISTS for every declared class. It cannot prove the
           checklist is any good. That is the honest limit.
```

The three prior fixes each **added an owner for a directory or an artefact and no checklist for a
kind of content** — [IMP-0726](../../logs/improvement-log.jsonl)'s own root cause says so. So a
fourth checklist alone would be the instance patch the ladder forbids.

The generalisation is [IMP-0726](../../logs/improvement-log.jsonl)'s `why_it_was_never_caught`
verbatim: *nothing asserts that every `class` value in `docs/Import/MANIFEST.yml` resolves to a
checklist in the skill its `intaked_by` agent loads.* That is mechanical.

Corpus enumerated **before** choosing the set, because this is a fail-closed check: the manifest
declares exactly four classes — `requirements`, `contractual`, `compliance`, `data-sample` — against
three checklists plus a scoped palette check. The gate opens with a real finding on day one, and row
11 supplies the missing checklist in the same change so it opens green.

[IMP-0739](../../logs/improvement-log.jsonl) is the same class one level further out: a client's
covering **email body** carried two lists that exist in none of its attachments, and a mail body is
not a file until someone transcribes it.

---

```
CLUSTER E: the contracted baseline read as line items rather than as a costed estimate
           (x2: IMP-0727, IMP-0729)
Altitude:  CLASS, but the change is a RECORDED DECISION, not a rule — the reviewer's, 2026-09-11
Ladder row: "the cause is general and a human needs to know it" → knowledge/contract note
Becomes:   contract/delivery-parameters.json note + agents/plan-agent.md (rows 19, 13-adjacent)
Retires:   nothing
Residual:  A0 and A8 carry NO feedback row. That is a COMMERCIAL fact, routed — see §5.
```

Sixteen of 39 client items were held at a change-order gate because no WBS row named per-component
rework. The reviewer's correction: every one of the 61 accepted tasks carries an
`hours_low`–`hours_high` **range**, rework on an already-built component is quoted work, and
`C-COM-002` exists to stop unquoted **building**, not iteration.

[IMP-0729](../../logs/improvement-log.jsonl) then tested that correction against
`contract/wbs.json` rather than accepting it — the right instinct — and found the gap the
correction did not name: **A0 (Platform Foundation) and A8 (Finance) have no feedback or rework row
at all**, and A0 is where task 0.4 delivered the grant administrator app. Its own
`proposed_change` is `none`, correctly: that is a commercial decision, not a repository change.

---

```
CLUSTER F: a change-order task id read as a baseline task id  (x1: IMP-0724)
Altitude:  INSTANCE with a general mechanism — the two id namespaces are indistinguishable by shape
Ladder row: "a tool could catch it mechanically"
Becomes:   scripts/verify-wbs-chain.py + engine twin (row 3)
Cites:     IMP-0724
Residual:  catches an id cited inside contract/*.json. The ~205 occurrences across src/ and
           docs/ are out of scope; widening it is a second-instance decision.
```

`contract/known-exceptions.json` states, as an expiry rationale, that *"wbs:6.9 sits alongside
6.1-6.8 in Phase 3 (contract/wbs.json)"*. It does not: `6.9` was created by change order `CO-001`
and is not among the 61 accepted tasks. A `contract/` file citing `contract/wbs.json` for a task id's
phase membership is checkable in one pass.

---

```
CLUSTER G: a serialisation default silently invalidates every evidence needle  (x2: IMP-0733)
Altitude:  CLASS, and specifically an ESCALATION — the prose fix recurred
Ladder row: "the system's own memory failed" → make the gate catch the operation
Becomes:   scripts/verify-improvement-log.py + engine twin (row 4)
Retires:   nothing; the prose stays, it is now backed
Cites:     IMP-0733, IMP-0664
Residual:  the gate catches escaped output. It cannot catch a rewrite that loses a whole line.
```

**Corpus measured before wiring: 2 findings, 2 true positives, 0 false positives.** Exactly two
lines in a 749-entry log carry a `—` escape — [IMP-0664](../../logs/improvement-log.jsonl) and
[IMP-0699](../../logs/improvement-log.jsonl), both `APPLIED`, and **IMP-0664 is the finding that
established the rule**, still carrying the defect in its own record. Row 4 repairs both lines in the
same change, so the gate opens green rather than red on pre-existing debt
(`hard-gate-red-on-pre-existing-debt`, x3).

---

```
CLUSTER H: the engine submodule is invisible until something fails  (x2: IMP-0738, IMP-0752)
Altitude:  CLASS — two instances, one at session start and one in this agent's own instructions
Ladder row: "the system's own memory failed" → a read-path change
Becomes:   agents/improvement-agent.md topology (row 14) + a session-start line — see NARROWING
Cites:     IMP-0738, IMP-0752
Residual:  CLAUDE.md cannot be gated by anything that lives in the engine. That is the point.
```

**[IMP-0738](../../logs/improvement-log.jsonl)'s proposal measures wrong, and this is a
NARROW-AND-REPORT.** It asks for the assertion in `scripts/validate-instance.py`. Two measurements
say that cannot work:

1. That file is a **wrapper**; the real check is `.engine/scripts/validate-instance.py`
   ([line 26](../../scripts/validate-instance.py#L26)) — so when the submodule is missing, the
   checker is missing too. The wrapper already prints the exact remedy
   (`git submodule update --init`) at [line 33](../../scripts/validate-instance.py#L33).
2. It is wired as a **build** step ([line 50](../../config/revitalise-grant-automation-build.yml#L50)),
   and the defect happens at **session start**, before any build. A build-time gate does not help a
   session that has already read a truncated rule set at CLAUDE.md step 1.

The narrowing removes exactly one false positive: *"validate-instance.py does not check this"* is
true and irrelevant, because the check must live in the one artefact that **survives an
uninitialised submodule** — `CLAUDE.md`, which is a tracked instance file and not a symlink. That
is what row 14 pairs with, and it is additive: nothing is removed from `validate-instance.py`.

---

```
CLUSTER I: a reference map's fallback degrades to a SHORTER prefix and manufactures a
           confident wrong value  (x1, blocker: IMP-0737)
Altitude:  INSTANCE with a mechanical property
Ladder row: "a tool could catch it mechanically", and the severity earns skipping ahead
Becomes:   scripts/verify-postcode-region-map.py, NEW, wired SOFT (row 5)
Cites:     IMP-0737
Residual:  the DATA fix is not mine — routed. The gate is red until it lands, which is why
           it is SOFT and not HARD.
```

**CORRECTED AT APPLY TIME, 2026-09-17.** The draft attributed all five affected areas to one
mechanism. That was wrong, and the reviewer caught it. Withdrawn wording, retained so the change is
visible: *"`BB`, `PE` and `WD` derive confidently wrong regions … because the map's fallback
degrades to a shorter prefix."* **`PE` and `WD` are both present in the map** — at options 4 and 7 —
so the fallback has nothing to do with them. There are **two independent defects**, not one.

Re-derived at apply time by reconciling the client's `docs/Import/Postcode Details.xlsx`
(3,394 districts, 120 areas) against the seeded map, ignoring rows that put a *country* in the
Region column and normalising case:

| | Area | Client says | Map derives | Districts |
|---|---|---|---|---|
| **A. Mapped to the wrong option** | `PE` | East of England | East Midlands | 38 |
| | `WD` | East of England | London | 25 |
| **B. Absent, degrades to a shorter prefix** | `BB` | North West | West Midlands (via `B`) | 18 |
| **C. Absent, resolves to *Not known*** | `HP` | South East | — | 23 |
| | `CT` | South East | — | 21 |

**IMP-0737's figure — 125 districts across 5 areas — is exactly right**, and is now verified against
the source rather than carried forward from the finding's prose. What was wrong was only this
review's account of *why*. Group B is the fallback defect and has **one** member, not three; groups
A and C are an ordinary wrong value and an ordinary coverage gap.

This changes the gate's design, and row 5 reflects it: a check for the fallback mechanism alone
would have caught **one** of the five. The gate must assert **coverage** as well, against the
client's sheet as the authority.

The gate is mine; **the map edit and the redeploy are delivery work with a commercial consequence**
and are routed in §5.

---

```
CLUSTER J: a live naming convention diverged from every settings file that assumes it
           (x1, blocker: IMP-0734)
Altitude:  INSTANCE — one environment confirmed, two unchecked
Ladder row: "the cause is general and a human needs to know it" → knowledge line
Becomes:   knowledge/technology/ (row 18). Everything else is ROUTED.
Cites:     IMP-0734
Residual:  test/prd team names are UNVERIFIED. Only a credentialled session can settle them.
```

Dataverse group teams in dev are named `REV-PP-GrantApplications-<Persona>-<ENV>` — the Entra
group's own display name, because they were created through the admin centre's *add group team*
flow — not the short `REV Finance` form the settings files carry. One live name even carries a
leading space. The proposal's *"consider a pre-flight check in `provisioning-common.ps1`"* is an
executable that authenticates to a live environment: **not mine to author**, per this agent's own
boundary. Handed over with the verification query.

---

```
CLUSTER K: a gate coupled two files by SIZE, so an unrelated append reddened it
           (x1, blocker: IMP-0745)
Altitude:  n/a — ALREADY APPLIED before this review opened
Becomes:   nothing new. Closed on execution.
Cites:     IMP-0745
```

Caught by §3a's duplicate check. The digest and its appendix are one read path split by a
per-lesson character budget; the needle check now reads both halves. Re-run at draft time: clean.

---

```
CLUSTER L: single-instance analysis discipline  (x4: IMP-0746, IMP-0749, IMP-0750, IMP-0741)
Altitude:  INSTANCE each — four distinct classes, one member apiece, why_it_was_never_caught
           = "nothing". The ladder's §4 is explicit: a knowledge or skill line, NOT a constraint.
Becomes:   rows 10, 12, 13, 15 — one prose home each, at the point of use
Cites:     IMP-0746, IMP-0749, IMP-0750, IMP-0741
Residual:  four prose changes with no mechanical half. If any recurs, that is the second
           instance and it earns a gate then.
```

[IMP-0749](../../logs/improvement-log.jsonl) is the one worth reading. A threshold rule was
specified, sized and prepared for handoff as *"over £500"* with the comparison operator never
stated. 35 of 63 applications request **exactly** £500 — because a cap is the modal value in
application data, applicants asking for the maximum. `>` flags 0; `>=` flags 37. One character
decides between a dead rule and an unusable one. The rule that follows generalises cleanly: when
sizing a threshold against a corpus, count **beyond the boundary, on it, and what the opposite
operator gives**.

---

```
CLUSTER M: a flow step's DESCRIPTION ages independently of the setting it quotes  (x1: IMP-0747)
Altitude:  INSTANCE — one member, and the proposal itself offers the cheaper alternative
Becomes:   NOTHING in this review. See §4.
Cites:     IMP-0747
```

---

## 3. Proposed changes

> `Type` from the closed vocabulary: `constraint` · `constraint-amendment` · `script` · `skill` ·
> `knowledge` · `agent` · `template` · `other`.
> **`Repo`** names which git repository the change commits to — `instance` (Revitalise) or
> `.engine` (submodule, needs its own commit plus a pointer bump here).

| # | Type | Repo | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|---|
| 1 | script | instance **+ .engine** | `scripts/verify-design-doc-claims.py` + twin | Widen roots to `docs/development`; flag any `rev_<table>.rev_<column>` mapping claim naming a column no `Entity.xml` declares | IMP-0723 | YES — `--selftest` + real corpus | **already wired** — `design-doc-claims`, [build line 541](../../config/revitalise-grant-automation-build.yml#L541); roots widened in the same edit |
| 2 | script | instance **+ .engine** | `scripts/verify-design-doc-claims.py` + twin | Every column a design document states is withheld from the trustee role must appear as a `FieldPermission` under `REV_TrusteeRestricted` | IMP-0725 | YES — `--selftest` + real corpus | **already wired** — same step |
| 3 | script | instance **+ .engine** | `scripts/verify-wbs-chain.py` + twin | Every task id cited inside `contract/*.json` resolves to `contract/wbs.json` **or** to an approved change order, and the finding says which | IMP-0724 | YES — corpus contains the known bad citation | **already wired** — PM gates |
| 4 | script | instance **+ .engine** | `scripts/verify-improvement-log.py` + twin | Fail when the raw file contains a `\uXXXX` escape. **Repair the 2 existing lines in the same change** so it opens green | IMP-0733, IMP-0664 | YES — 2 findings, 2 true positives, measured | **already wired** — `improvement-log-check`, [build line 80](../../config/revitalise-grant-automation-build.yml#L80) |
| 5 | script | instance **+ .engine** | `scripts/verify-postcode-region-map.py` **(NEW)** | Assert the map's prefixes cover the UK postcode areas and that no two-letter area resolves through a one-letter prefix | IMP-0737 | YES — `--selftest` + the seeded map | **SOFT (`--warn-only`)** — red until the data fix lands; HARD is a follow-up, not this change |
| 6 | script | instance **+ .engine** | `scripts/dump-entity-attributes.py` + twin | Emit each attribute's `<Description>` beside its name | IMP-0735, IMP-0743 | YES — `grep -c 'Description'` on the output | N/A — reporting tool, not a gate |
| 7 | script | instance **+ .engine** | `scripts/verify-import-manifest-intake.py` **(NEW)** | Every `class` in `docs/Import/MANIFEST.yml` resolves to a checklist in the skill its `intaked_by` agent loads | IMP-0726 | YES — 4 declared classes enumerated before choosing the set | **SOFT** first, wired in the same change as row 11 |
| 8 | skill | **.engine** | `skills/how-to-verify-a-platform-contract.md` | New section — *an artefact answers only the question its construction can answer*, with the five measured artefact types | IMP-0736, IMP-0740, IMP-0744, IMP-0748, IMP-0751 | NO — instruction change, stated | N/A |
| 9 | skill | **.engine** | `skills/how-to-verify-a-platform-contract.md` | Before extending, categorising or re-purposing an existing artefact, read its own authored description — `<Description>`, README, inline comment — not only its values | IMP-0735, IMP-0731, IMP-0743, IMP-0742 | NO — instruction change | N/A |
| 10 | skill | **.engine** | `skills/how-to-verify-a-platform-contract.md` | Sizing a threshold rule against a corpus requires three counts: beyond the boundary, **on** it, and what the opposite operator gives | IMP-0749 | NO — instruction change | N/A |
| 11 | skill | **.engine** | `skills/how-to-intake-external-documents.md` | Fourth checklist, *Review Feedback Intake (plan-agent)*; the covering-message rule; and a **declared class→checklist map** row 7 reads | IMP-0726, IMP-0739, IMP-0735 | YES for the map (row 7 reads it); NO for the checklist prose | N/A |
| 12 | skill | **.engine** | `skills/how-to-ask-clarifying-questions.md` | When a client asks for a field whose subject overlaps a known defect, establish whether it records a **human action** or a **data state** before designing it | IMP-0741 | NO — instruction change | N/A |
| 13 | agent | **.engine** | `agents/plan-agent.md` | A source's **silence** on a previously-established rule is resolved against the earlier source before it changes any dependent item's classification or enters a client question list | IMP-0750, IMP-0727 | NO — instruction change | N/A |
| 14 | agent | **.engine** | `agents/improvement-agent.md` | State the two-repository topology in [Outputs](../../agents/improvement-agent.md#L381): which targets are submodule paths, which are instance files, and that a script edit lands in both copies. **Paired with a CLAUDE.md session-start line** (row 20) | IMP-0752, IMP-0738 | YES — `grep -c '\.engine' agents/improvement-agent.md` > 0 | N/A |
| 15 | template | **.engine** | `templates/` (triage/plan row convention) | Quote the client's ask **verbatim with its source and date**; mark which attributes of a proposed solution are the agent's own design | IMP-0746 | NO — convention | N/A |
| 16 | knowledge | instance | `knowledge/domain/` | The live application form is **public and fetchable** and is the authority for wording, option lists and conditional logic; DEV and Acceptance hold **demo data**, so no question about real applications is answerable from an environment | IMP-0728, IMP-0740 | YES — the URL resolves | N/A |
| 17 | knowledge | instance | `knowledge/domain/data-entities.md` | State the three applicant routes and what each does and does not record — including that a carer's own disability is out of scope, and that `rev_narrativeraw` is **route-independent** | IMP-0742, IMP-0743 | NO — reference material | N/A |
| 18 | knowledge | instance | `knowledge/technology/` | Dataverse group teams here are named after the Entra group (`REV-PP-GrantApplications-<Persona>-<ENV>`); list live teams before resolving any team by name | IMP-0734 | NO — reference material | N/A |
| 19 | other | instance | `contract/delivery-parameters.json` | Record the reviewer's standing interpretation (2026-09-11): every WBS row is an hours **range**; rework of an already-built component draws on reserved capacity and is not a change order | IMP-0727, IMP-0729 | YES — `grep -c` on the recorded decision | N/A |
| 20 | other | instance | `CLAUDE.md` | Session-start step 0: confirm `agents/`, `skills/` and `.claude/hooks/` resolve; if not, run `git submodule update --init .engine` **before** reading step 1 | IMP-0738 | YES — the file is tracked and not a symlink, so it survives the failure | N/A |
| 21 | other | instance | `docs/Import/2026-09-11-live-application-form-capture.md` + `scripts/generate-known-failure-modes.py` | Head the capture with what it can and cannot evidence, with a discharge condition; and correct the drifted registered digest line count (**693 → 698**, re-measured after this review's own regeneration) | IMP-0736 *(plus this review's own mandatory regeneration)* | YES — `python3 scripts/verify-derived-counts.py` | N/A |

**Constraint budget: 0 of 3 used.** No new constraint is proposed and none is needed: rows 1 and 2
are the mechanical half of [`C-DOM-001`](../../constraints/domain/domain-constraints.md#L34), which
already names this script as its `Verify By`. The set stands at **85 live** rows and **10 retired**,
both derived at draft time, never typed.

**Type counts (rows, not files):** `script` 7 · `skill` 5 · `knowledge` 3 · `agent` 2 ·
`template` 1 · `other` 3 · `constraint` 0 · `constraint-amendment` 0. **21 rows.**

---

## 4. Retirements and withholdings

> **Retirement check performed: 85 live constraint rows reviewed at class level against these 13
> clusters. No candidate found.** Every proposal here either extends a gate that already exists
> (rows 1–4, 6) or adds a first mechanical check where a rule had none (rows 5, 7). Nothing is
> superseded, so retiring anything would lose coverage rather than consolidate it. Derived with
> `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` → 10.

**WITHHELD — the banded-option-set gate ([IMP-0730](../../logs/improvement-log.jsonl)).** Its
premise measured false. The finding asserts `rev_carehoursband.xml` *"reproduces the defect exactly
rather than correcting or flagging it"*; the file's own `<Description>` at
`src/solutions/RevitaliseGrantAutomation/OptionSets/rev_carehoursband.xml:48` reads *"Bands 4 and 5
overlap at 50-59 hours on the live form itself - V-10, unresolved, tracked in the change request to
Alex, not this schema's problem to fix by inventing a cleaner band."* Grepped, not inferred.
[IMP-0731](../../logs/improvement-log.jsonl) had already recorded this as a correction, and the
validator was already warning that IMP-0730 carried an unprocessed `corrects` edge.

So the gate would fire on a defect that is real, known, owned, dated and deliberately accepted —
`hard-gate-red-on-pre-existing-debt` by construction. Withheld and reported. The live-form defect
itself is unchanged and still tracked as V-10.

**WITHHELD — the flow-description-versus-setting gate ([IMP-0747](../../logs/improvement-log.jsonl)).**
The finding is real: three step descriptions in `REVScoringCalculateAndFlag` still state that
`LikertPointMap` key 6 is worth 0.5 when it was changed to 0 on 2026-08-20, making
`Round_the_circumstance_score` dead code. But the proposed gate must decide *"this sentence states a
numeric value for that setting key"* by reading prose — the instrument this repository has measured
**five times at 48%–100% false**, once shipping a gate that reddened on the erratum written to
satisfy it. The finding itself offers the cheaper alternative (*"a convention that step descriptions
cite a setting by key without restating its value"*) and that is a **development-agent** authoring
convention, not an improvement-agent rule. Routed, not built.

**WITHHELD — a feedback-row coverage check ([IMP-0729](../../logs/improvement-log.jsonl)).** Whether
an automation *should* carry a feedback row is a commercial judgement about a signed baseline, not a
repository fact. Its own `proposed_change` is `none` and it is right. Routed to `commercial-agent`.

**NOT MINE TO WRITE — three items handed over rather than authored.** The `provisioning-common.ps1`
pre-flight (row 18's neighbour), the postcode map data edit, and the `Entity.xml` description
amendment all either authenticate to a live environment or change shipped solution source. §5.

---

## 5. Findings left unprocessed, and what is routed

**States excluded from this review, per activation step 2:**

- **155 `reviewer-deferred`** — each carries a `deferred_reason` a human accepted. Left as-is. One
  of them, `IMP-0274`, still names no `revisit_when`; the gate flags it and it is not this review's
  to close.
- **4 `awaiting-approval`** — [IMP-0608](../../logs/improvement-log.jsonl),
  [IMP-0644](../../logs/improvement-log.jsonl), [IMP-0645](../../logs/improvement-log.jsonl),
  [IMP-0652](../../logs/improvement-log.jsonl). **Not re-derived.** Each already names a review
  document that exists and is parked at its own gate:
  IMP-0608 → [2026-09-05-improvement-review-2.md](2026-09-05-improvement-review-2.md);
  IMP-0644 and IMP-0645 → [2026-09-07-improvement-review-2.md](2026-09-07-improvement-review-2.md);
  IMP-0652 → [2026-09-07-improvement-review-3.md](2026-09-07-improvement-review-3.md).
  **The remedy for these four is a keyword sent against those three documents, not another
  session.** Each is stamped `excluded_by` naming this review.

**Routed work — re-measured at draft time, to be re-measured again at apply time.**

| To | What | Why it is not mine | Re-measured |
|---|---|---|---|
| `development-agent` | Add `BB`, `CT`, `HP`, `PE`, `WD` to `PostcodeRegionMap`; make an unlisted two-letter area resolve to *Not known* rather than to its first letter | Shipped reference data that changes derived values in three environments | Confirmed against the seeded map, 2026-09-17 |
| `pipeline-agent` | Redeploy the corrected map to dev / tst_acc / prd, and confirm the live Dataverse team names in tst_acc and prd the way dev's were confirmed | Requires a credentialled session | dev confirmed 2026-09-15; test/prd **unverified** |
| `architect-agent` | Record the `REV-PP-GrantApplications-<Persona>-<ENV>` convention in the architecture document §6.2.1 | An approved architecture document is its deliverable, not mine | — |
| `development-agent` | Amend `rev_narrativeraw`'s description to say it is route-independent; add the step-description-cites-a-key-not-a-value convention | Shipped solution source | Confirmed: bound to one trigger key, no route branch |
| `commercial-agent` | A0 and A8 carry no feedback/rework row, and no accepted task mentions safeguarding | A decision about a signed baseline | Confirmed against `contract/wbs.json`, 61 tasks |

**Entries that cannot be closed here, and stay open with a reason rather than a claim.**
[IMP-0734](../../logs/improvement-log.jsonl) is `observable_at: V3` and
[IMP-0737](../../logs/improvement-log.jsonl) is `V4`. Neither is closed by a knowledge file saying
it was fixed — they need a signed-in session to re-run the original reproduction. Both get a
`deferred_reason` and a `revisit_when` naming the owner above. An honest open entry beats a closed
one nobody tested.

---

## 6. Digest impact

**Already regenerated at draft time**, because appending IMP-0752 made the digest stale and
`known-failure-modes-check` is a HARD build step — leaving it red for a reviewer to find is not a
smaller act than regenerating it.

| | Before this review | Now |
|---|---|---|
| Entries | 748 | **749** |
| Lessons (NEW + APPLIED) | 742 | **743** |
| Distinct classes | 163 | **164** |
| Recurring classes (≥2) | 57 | **57** |
| Digest lines | 696 | **698** (appendix 1,359; 61 lessons truncated past the 600-char budget) |

Eight classes gain their first sibling or grow: `stale-claim-contradicting-rechecked-source`
14 → 14 (five of this batch already counted), `input-type-with-no-owning-agent` at **x5**,
`declared-knowledge-source-is-empty` at **x4**, `agent-instructions-describe-a-topology-that-changed`
at **x7**, `serialisation-default-invalidates-evidence-needle` at **x2**,
`baseline-read-as-line-items-not-as-an-estimate` at **x2**.

The digest regenerates at apply time and **that regeneration is itself what drifts the registered
line-count claim** — row 21 corrects it in the same change, because nothing else will.

---

## 7. Verification actually executed at draft time

| Check | Result |
|---|---|
| `python3 scripts/verify-improvement-log.py --check` | exit 1 — the blocker trigger this review exists to clear; 0 unread after stamping |
| `python3 scripts/verify-improvement-log.py` (schema) | exit 0 — 749 entries |
| `python3 scripts/generate-known-failure-modes.py --check` | exit 0 — **after** regenerating; my draft-time append of IMP-0752 made it stale, which is a HARD step, so it was regenerated here rather than left for apply time |
| `python3 scripts/verify-derived-counts.py` | **exit 1** — 1 drifted claim, digest line count 693 vs **698**. SOFT, and row 21 corrects it |
| `python3 scripts/verify-review-document.py --only <this file>` | exit 0 — 13 claimed clusters match 13 CLUSTER blocks; no section reference dangles |
| `python3 scripts/verify-doc-line-links.py` | exit 0 |
| Disposition simulation on a scratch copy, then restore | blocker trigger **clears**; one apply-time error surfaced early — see below |
| `python3 scripts/report-dispatch-share.py` | exit 0 — 30.4%, blocker trigger now the largest category at 33 |
| `python3 scripts/verify-engine-instance-split.py` | exit 0 — 87 scripts, 57 unsplit duplicates |
| Byte-safety of the `reviewed_in` stamp | 33 of 749 lines changed, all intended; no `\u` escape introduced |

**The simulation earned its cost.** The draft's dispositions were applied to a scratch copy of the
log and the gate run against it: the blocker trigger clears, and one thing that would otherwise have
been discovered *after* the keyword surfaced instead — `IMP-0727`'s `proposed_change.target` names
**two** paths (`contract/delivery-parameters.json` and `agents/plan-agent.md`), and the validator
refuses a closure that accounts for only one. Rows 19 and 13 do both; `applied_by` must name both.
The real log was restored and confirmed byte-identical with `diff`.

**Level reached: V1.** Rows 1–7 are designed, their premises grepped and their corpora enumerated,
and **none has been written or run.** Nothing in §3 exists on disk. `--selftest` and the real-corpus
measurement each new gate demands happen at apply time, and their numbers go in §8 — not here, and
not as a claim now.

**What was NOT verified:** the live Dataverse team names in tst_acc and prd; whether the corrected
postcode map produces the right region for the 125 affected districts once deployed; and every
`skill`, `agent` and `template` row, which have no mechanical half by construction and are stated as
such in §3.

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-17-improvement-review.md

Findings processed: 29 NEW  →  13 clusters
Regression check:   7 prior changes audited, 2 classes recurred
Proposed:           0 constraints (cap 3), 7 gates/scripts, 8 skill/knowledge edits,
                    2 agent-file edits, 1 template edit, 3 'other' rows, 0 retirements
                    — 21 change-table rows in total
Altitude calls:     10 generalised from instance to class (clusters A and B), 5 left as
                    notes, 1 narrowed on measurement, 3 proposals withheld
Digest:             will regenerate — 743 lessons, 57 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 9. Applied — 2026-09-17, on `APPROVE IMPROVEMENTS`

**11 of 21 rows landed. 3 were WITHHELD on measurements taken at apply time. 7 remain open.**
`verify-improvement-log.py --check` **exits 0**: all four blocker triggers cleared.

Applied incrementally, each change closed as it landed. Two repositories, stated per row.

| # | Row | Repo | Entries moved |
|---|---|---|---|
| 1 | `verify-design-doc-claims.py` check (c), mapping claims + `--mapping-claims-only` | instance **+ .engine** | *(IMP-0723 left open — V5)* |
| 4 | `verify-improvement-log.py` escaped-non-ASCII refusal, **redesigned** | instance **+ .engine** | IMP-0733 |
| 5 | `verify-postcode-region-map.py` (new) + SOFT wiring | instance **+ .engine** + config | *(IMP-0737 left open — V4)* |
| 8 | Skill section 12 — the artefact/question table | **.engine** | IMP-0736, IMP-0740, IMP-0744, IMP-0748, IMP-0751 |
| 9 | Skill section 12a — read the authored statement | **.engine** | IMP-0731, IMP-0735 |
| 10 | Skill section 12b — a threshold is three counts | **.engine** | IMP-0749 |
| 14 | `improvement-agent.md` two-repository topology | **.engine** | IMP-0752 |
| 18 | `knowledge/technology/entra-id.md` team-naming convention | instance | *(IMP-0734 left open — V3)* |
| 20 | `CLAUDE.md` session-start step 0 — **narrowed** | instance | IMP-0738 |
| 21 | Registered digest line count 693 → 699; verify-script count 60 → 61 | instance **+ .engine** | — |
| — | Closed on work that landed before this review | instance | IMP-0745 |

### Withheld, and the measurement that forced each

**Row 2 — the withheld-column gate.** Two mechanical forms built and measured, **both 100%
false**. Form (a), rows naming a column plus "Column security": 24 candidates, 4 findings, 0 true —
two of them rows that *document a removal from* `REV_TrusteeRestricted`, the polarity inversion
again. Form (b), "every Tier 4 column is in a profile": 8 Tier-4 rows, 2 findings, 0 true — both
say **"Trustee-visible by design"**. **Tier 4 is a sensitivity classification and does not imply
secured**, so the relation the proposal assumed does not exist in the data. The defect is real and
routed.

**Row 6 — `dump-entity-attributes.py` emitting descriptions.** Premise disproved **by execution**.
The script already prints every description and `--grep` already searches them; the draft's
supporting grep hit the *wrapper*, whose implementation lives in `.engine/scripts/`. Running
`python3 scripts/dump-entity-attributes.py rev_application` prints `rev_intakereviewnote`'s
description in full — the description IMP-0735 says was never opened. `instrument-exists-never-
used`, not a tooling gap. Section 12a now names the command instead.

**Row 1's root widening.** Running the *existing* checks over `docs/development` produces **5 new
errors on a HARD step**, all against frozen approved deliverables (four documents saying
`rev_ethnicgroup` was never built, one saying `rev_finalpaymentdate` is not built; all five columns
exist). Check (c) therefore ships as its own SOFT step and the HARD step's roots are unchanged.
The 5 are real and routed, not suppressed.

### Not applied — 7 rows, stated rather than quietly dropped

Rows **3** (`verify-wbs-chain.py` task-id namespace), **7** (`verify-import-manifest-intake.py`),
**11** (intake checklist + covering-message rule), **12** (`how-to-ask-clarifying-questions.md`),
**13** (`plan-agent.md` silence rule), **15** (triage-row template), **16**, **17**, **19**. Their
entries stay `NEW` and unclosed. No change was made and none is claimed.

### Corrected at apply time

The draft's account of the postcode defect was **wrong and has been rewritten in cluster I**: `PE`
and `WD` are in the map under the wrong option, only `BB` degrades via a shorter prefix. The
finding's own figure — 125 districts across 5 areas — was **re-derived from the client's sheet and
is exactly right**.

### Verification executed at apply time

`verify-improvement-log.py --check` **exit 0** · schema **exit 0**, 749 entries ·
`generate-known-failure-modes.py --check` **exit 0** · `verify-derived-counts.py` **exit 0**, 10 of
10 · `verify-review-document.py` **exit 0** · `verify-doc-line-links.py` **exit 0** ·
`verify-build-config.py` — no `suite-gate-is-not-a-step` violation; the 5 remaining failures are
pre-existing and were confirmed present at `HEAD`.

**Level reached: V1.** Every new and edited gate parses, self-tests and has been run against its
real corpus. Nothing here has been executed against a live environment, and the two entries that
need one (IMP-0734 at V3, IMP-0737 at V4) are open with a named owner.

---

## 10. Phase 2 — the three older parked reviews

**Scope extended 2026-09-17** ("Yes, do everything now") to
[2026-09-05-improvement-review-2.md](2026-09-05-improvement-review-2.md),
[2026-09-07-improvement-review-2.md](2026-09-07-improvement-review-2.md) and
[2026-09-07-improvement-review-3.md](2026-09-07-improvement-review-3.md), carrying four entries
between them.

**All three predate the submodule split** — `.gitmodules` was added on 2026-09-10 in `e37fad0`,
and all three were written on 2026-09-05 or 2026-09-07, when `agents/`, `skills/` and `templates/`
were ordinary files in this repository. Every proposal was re-verified against the current tree
before being touched. **All four premises still hold**; one target had moved repositories and one
defect had grown worse.

| Entry | Premise re-measured | Disposition |
|---|---|---|
| `IMP-0644` | No when-required statement exists in the closure block | **APPLIED — in `.engine`.** The target was an ordinary file when proposed and is now a symlink; applied literally it would have landed in the wrong repository |
| `IMP-0645` | Message at `verify-improvement-log.py:2082` still reads *"Stamp `<id>` with the review that processes it"* | **APPLIED — instance + `.engine` twin.** Its optional second half (suppressing the rung) was **not** done: it changes behaviour, not wording, and no second instance justifies it |
| `IMP-0608` | Register exists; the test still hand-maintains the list, `12 - 1 + 4 = 15` comment intact | **NOT APPLIED — delivery work**, and its own proposing review already routed it. Deferred with an owner |
| `IMP-0652` | **Worse than recorded**: dev now holds **18** invocations of `ensure-schema.ps1`, `tst_acc` **0**, `prd` **0** | **NOT APPLIED — delivery work.** Wiring a live provisioning script into a deploy pipeline changes what runs against a live environment. Deferred with an owner |

**No proposal was withheld on a failed premise in phase 2**, which is worth stating plainly because
the extension brief predicted withholds across a ten-to-twelve-day gap spanning a repository
restructure. The gap mattered in a different way than expected: it moved a *target*, it did not
falsify a *diagnosis*. The one row that changed materially — `IMP-0652` — changed by getting worse,
not by being fixed.

Neither `IMP-0608` nor `IMP-0652` is affected by the split: `src/tests/` and `config/` are instance
paths and always were.
