# Improvement Review — 2026-09-04

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 3 unread → 3 clusters
**Trigger:** blocker escalation — [`IMP-0597`](../../logs/improvement-log.jsonl), [`IMP-0598`](../../logs/improvement-log.jsonl) and [`IMP-0599`](../../logs/improvement-log.jsonl), all unread, appended 2026-09-04 00:00–00:20
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** ~~DRAFT — parked at its gate. `reviewed_in` stamped per activation step 6; no `status` moved.~~
**APPLIED 2026-09-04** — see §10. All seven proposed changes landed as drafted; no narrowing at
application time beyond the one §3 already recorded. One new finding was logged during application
(`IMP-0600`) and is named in §11.
**WBS:** 0.4 (carried from the findings; the rule changes themselves are system work, not a contracted deliverable)

**The dispatch brief named two blockers. There are three.** The gate reports
`IMP-0597`, `IMP-0598` **and** `IMP-0599` unread at `blocker`. `IMP-0599` is `build-agent`'s own
record of the halt, and it is in scope for the same reason the other two are.

**And processing all three does not turn the build green.** Simulated against a scratch copy of the
log: the blocker trigger clears, the **batch trigger does not** — 33 unread minus 3 leaves exactly
30, and the threshold is 30. `verify-improvement-log.py --check` still exits 1, so
`improvement-log-check` still halts the build at step 3. That is §6.

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [`2026-09-03` review](2026-09-03-improvement-review.md) — [`BLOCKED_ON_WARN_DAYS = 4`](../../scripts/verify-pipeline-config.py#L520) plus the PASS-path freshness line | 2026-09-03 | `stale-deferral-uncaught-across-sessions` | **NO** — no entry after [`IMP-0586`](../../logs/improvement-log.jsonl) carries this class | **Working, and its residual is discharged.** That review closed with `verify-pipeline-config.py` exiting **1** on four unre-tested notes. Re-run today: **exit 0** |
| Review 10 — [`scripts/verify-code-app-bundle-budget.py`](../../scripts/verify-code-app-bundle-budget.py) | 2026-09-01 | `untriaged-tool-warning` | **YES** — [`IMP-0592`](../../logs/improvement-log.jsonl), `friction` | **Out of this dispatch's scope** (unread, not a blocker — §7). Flagged for the batch review, not diagnosed here |
| Reviews 1–36 cumulative — the `no-assertion-on-shipped-content` family | various | `no-assertion-on-shipped-content` | **YES ×2** — [`IMP-0590`](../../logs/improvement-log.jsonl), [`IMP-0597`](../../logs/improvement-log.jsonl) | **This is cluster A.** The class is at **×29** and every prior fix has been per-instance. Generalised here for the schema↔form-surface half |

**Classes that recurred after a prose fix:** one, and it is the sharpest signal in this review.
[`agents/lead-agent.md` L345–349](../../agents/lead-agent.md#L345) already states, in terms written
*for this exact failure* after [`IMP-0527`](../../logs/improvement-log.jsonl), that a dispatch note
says one of exactly two things about `verify-improvement-log.py --check`. `IMP-0599`'s root cause is
a dispatch note that said a third thing. See cluster C — the answer is **not** more prose.

**Classes that recurred after a gate:** none where the gate failed to fire. The
`improvement-log-check` HARD step fired correctly and stopped the build at step 3 of 70.

---

## 2. Clusters and promotion decisions

```
CLUSTER: no-assertion-on-shipped-content  (x1 unread: IMP-0597; x29 in class)
Altitude:  CLASS — a secured, capture-intended column and its form control are two XML
           files, and nothing asserted they move together
Ladder row: "a tool could catch it mechanically" + "second instance -> generalise"
Becomes:   a new check in scripts/verify-forms-and-views-reachable.py (already a wired
           build step, so no new script and no new build step) + constraint C-TECH-077
Retires:   nothing - this property was undefended; no instance gate existed to replace
Cites:     IMP-0597
Measured:  1 finding / 1 true positive against the pre-fix tree; 0 findings against the
           corrected tree. 52 secured columns on 7 main-form entities. Both polarities run.
Residual:  the predicate is IsSecured=1, a PROXY for "intended to be captured". A future
           secured column that is system-computed would be a false positive. Handled by an
           enumerated FORM_SURFACE_EXEMPT dict, empty today by measurement. The check says
           nothing about columns that are NOT secured - rev_agerange would not be covered.
```

```
CLUSTER: declared-policy-not-mechanically-enforced  (x1 unread: IMP-0598; x27 in class)
Altitude:  CLASS - a hand-kept list with no independent cross-check against source, the
           same property as IMP-0038 / IMP-0155 / IMP-0212 in this codebase
Ladder row: "a tool could catch it mechanically", NARROWED - see below
Becomes:   the register row itself, the FR-016 alternation entry, a pending_adjudication
           block in the register, and a fail-closed completeness check in
           scripts/verify-domain-invariants.py (already a wired build step) + C-DOM-033
Retires:   nothing
Cites:     IMP-0598
Measured:  the finding's OWN proposal was disproved - see the table in section 3
Residual:  C-DOM-033 asserts that every secured column has been LOOKED AT, never that it
           was classified correctly. Article 9 membership is a legal judgement about what
           data means, and no property of the XML decides it. The 51 pending rows are a
           visible debt owned by the Domain Owner, not a clean bill of health.
```

```
CLUSTER: unread-blocker-halts-build  (x1 unread: IMP-0599; x1 under this name, x28 as
           gate-reassures-wrongly - and it stays x28, see section 4)
Altitude:  NOTHING - no change. The control performed exactly as designed
Ladder row: none applies. Per skills/how-to-promote-a-finding.md section 4, a gate that
           fired is not a defect to route around
Becomes:   one bookkeeping correction: class_instance_of re-pointed to
           gate-reassures-wrongly, the class IMP-0527 already carries
Retires:   nothing
Cites:     IMP-0599
Residual:  the recurrence-after-prose signal is recorded and deliberately NOT acted on.
           Section 4 says why.
```

---

## 3. Cluster B — the finding's own proposal, disproved by measurement

[`IMP-0598`](../../logs/improvement-log.jsonl) proposed scanning `Entity.xml` descriptions for
Article-9 self-declaring language, with a fallback of printing every `IsSecured=1` column absent
from the register as a NOTE. **Both forms measure as noise.** Every candidate signal, run against
the whole corpus of 226 attributes:

| Candidate signal | Findings | True positives | Precision | Recall over the 20 registered rows |
|---|---|---|---|---|
| `IsSecured=1` and not in the register (the finding's own fallback) | 52 | 1 | **2%** | n/a |
| `article 9` / `special-category` in a Description, case-insensitive | 9 | 1 | **11%** | 4/20 = 20% |
| `ARTICLE 9` upper-case only | 1 | 1 | 100% | 4/20 = 20%, and the precision rests on one author's capitalisation |
| `REV_TrusteeRestricted` field-permission membership | 36 | 1 | **3%** | 16/20 |
| `REV_FinanceOnly` field-permission membership | 16 | 0 | **0%** | 0/20 |

**The polarity is inverted, exactly as [`IMP-0422`/`IMP-0428`](../../logs/improvement-log.jsonl)
predicted for a prose gate.** All eight false positives in the case-insensitive row are sentences
whose author took the trouble to explain *non*-membership —
[`rev_gender`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_applicant/Entity.xml)
(*"not special-category data — gender is not a UK GDPR Article 9 category"*), `rev_hearaboutus`,
`rev_review.rev_notes1`, and the five `*redacted` counterpart columns that name their Article 9
*source*. Better documentation produces more findings. This is the sixth measured instance of the
shape and the design is rejected rather than exempted.

Membership of `REV_TrusteeRestricted` fails for a stated reason, not an accidental one: the
profile's own `description` in
[`FieldSecurityProfiles.xml`](../../src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml)
says it releases *"the Tier 4 identifying **and** special-category columns"*. It was never built to
separate the two.

### NARROW-AND-REPORT — the narrower change that replaces it

**The intent survives: a register omission must become visible on the next build. The literal
wording does not.** So C-DOM-033 asserts on **values** rather than phrases, and fail-closed:

> Every attribute carrying `<IsSecured>1</IsSecured>` appears **either** in the register's
> `columns:` list **or** in a new `pending_adjudication:` list. A secured column in neither is a
> HARD failure naming the column.

The corpus was enumerated **before** the set was chosen, per
[`IMP-0560`](../../logs/improvement-log.jsonl): 68 secured attributes, 17 of them registered once
`rev_ethnicgroup` is added, **51** into `pending_adjudication` — 12 on `rev_applicant`, 11 on
`rev_application`, 7 on `rev_bankaccount`, 12 on `rev_grant`, 9 on `rev_payment`. Day-one findings:
**0, and 0 is correct**, because the set is the measured corpus. The first new secured column
thereafter produces exactly one true finding.

**The false positives this narrowing removes, named:** `rev_gender`, `rev_hearaboutus`,
`rev_review.rev_notes1`, `rev_unabletofundexplanationredacted`,
`rev_exceptionalfundingdetailredacted`, `rev_otherexceptionalcircumstanceredacted`,
`rev_otherconditionredacted`, `rev_supportrecipientotherconditionredacted` — the eight the prose
scan would have raised, plus the 51 the `IsSecured` scan would have raised as NOTEs.

**`pending_adjudication` is not an adjudication, and it does not claim to be.** Naming 51 columns
as *not* Article 9 is a compliance judgement belonging to the Domain Owner / Compliance Lead, who
[`constraints/README.md`](../../constraints/README.md) makes the owner of this file — the same
principle by which this agent does not author scripts that authenticate to live environments
([`IMP-0250`](../../logs/improvement-log.jsonl)). The block is marked with the register's own ⚠️
convention for a position its owner has not confirmed, and it makes an existing **silence** into an
enumerated, printed debt.

---

## 4. Cluster C — why a fourth statement of a working rule is not the answer

[`IMP-0599`](../../logs/improvement-log.jsonl) proposes no change, and that is correct. Three facts
settle it:

1. **The rule already exists, in maximal form.** [`agents/lead-agent.md` L345–349](../../agents/lead-agent.md#L345)
   was written after [`IMP-0527`](../../logs/improvement-log.jsonl) and enumerates the two
   permissible dispatch-note statements *"and never a third"*.
2. **The mechanical enforcement already exists and fired.** `improvement-log-check` is the HARD
   third step of the build config; the build stopped there, before any packaging work. Cost: one
   dispatch, three steps in.
3. Adding prose to a prose rule that is already both explicit and mechanically backed is what
   [`agents/improvement-agent.md` L292](../../agents/improvement-agent.md#L292) calls strangling
   the system in accumulated rules.

**One bookkeeping change does land.** `IMP-0599` declares
`class_instance_of: unread-blocker-halts-build`, a class of one. It is the same property
`IMP-0527` recorded as `gate-reassures-wrongly` (×28). Per the digest's own note on
[`IMP-0330`](../../logs/improvement-log.jsonl), a property recorded under two names produces a
weaker signal than its true instance count, and the altitude rule fires on instance counts. The
class is re-pointed and the original name preserved in `rejected_reason`.

**But the re-point changes no count, and this draft first claimed otherwise.** Measured by
regenerating the digest against a scratch copy carrying all three final dispositions:
`gate-reassures-wrongly` stays at **×28**, not ×29, because a `REJECTED` entry is not counted into
its class tally at all. `unread-blocker-halts-build` never had a row to lose — it was ×1. So the
re-point is bookkeeping hygiene that stops a future instance from landing under a name of one; it
is **not** a signal change, and saying so would have been [`IMP-0198`](../../logs/improvement-log.jsonl)'s
error of predicting a digest delta instead of running the generator.

---

## 5. Proposed changes

| # | Change | File | Justified by |
|---|---|---|---|
| 1 | New check: every `IsSecured=1` attribute on an entity with a main form has a `<control datafieldname="…">` on it. `FORM_SURFACE_EXEMPT` dict, empty, documented | [`scripts/verify-forms-and-views-reachable.py`](../../scripts/verify-forms-and-views-reachable.py) | `IMP-0597` |
| 2 | New constraint row **C-TECH-077** (HARD), `Verify By` = the step above | [`constraints/technology/technology-constraints.md`](../../constraints/technology/technology-constraints.md) | `IMP-0597` |
| 3 | Register row for `rev_applicant.rev_ethnicgroup`, `secured: required`, basis *"Art. 9 — racial or ethnic origin (Tier 4); OQ-027, reviewer direction 2026-08-27"* | [`constraints/domain/special-category-register.yml`](../../constraints/domain/special-category-register.yml#L60) | `IMP-0598` |
| 4 | `rev_ethnicgroup` added to the FR-016 grep alternation — forced by C-DOM-030's exact-equality assertion | [`config/revitalise-grant-automation-build.yml` L416](../../config/revitalise-grant-automation-build.yml#L416) | `IMP-0598` |
| 5 | `pending_adjudication:` block, 51 enumerated secured columns, ⚠️-marked, plus a `HOW TO ADD A COLUMN` step pointing at it | [`constraints/domain/special-category-register.yml`](../../constraints/domain/special-category-register.yml#L28) | `IMP-0598` |
| 6 | New check: every secured attribute is in `columns:` or `pending_adjudication:`; PASS summary prints the pending count | [`scripts/verify-domain-invariants.py`](../../scripts/verify-domain-invariants.py#L257) | `IMP-0598` |
| 7 | New constraint row **C-DOM-033** (HARD), `Verify By` = the step above | [`constraints/domain/domain-constraints.md`](../../constraints/domain/domain-constraints.md) | `IMP-0598` |

**Change 4 was verified not to break the gate it touches.** `grep -cE 'body/rev_ethnicgroup'`
against
[`REVScoringCalculateAndFlag`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVScoringCalculateAndFlag-8F1C2A44-1002-4B7A-9E21-0A1B2C3D4E02.json)
returns **0** — the scoring flow does not read the column, so the HARD FR-016 gate stays green with
the name added. Measured, not assumed.

**No new script and no new build step**, so `ls scripts/verify-*.py | wc -l` stays at **57** and
[`scripts/derived-counts-registry.json`](../../scripts/derived-counts-registry.json#L114) needs no
edit. Both changed scripts are already wired steps
([`forms-and-views-reachable`](../../config/revitalise-grant-automation-build.yml#L288),
[`domain-invariants`](../../config/revitalise-grant-automation-build.yml#L399)), which also avoids
`verify-build-config.py`'s `suite-gate-is-not-a-step` trap entirely
([`IMP-0568`, `IMP-0569`](../../logs/improvement-log.jsonl)).

**Two new constraint rows, cap is 3.** Live rows go 82 → 84; retired stays 10.

### Retirement candidate — considered, none found

Checked and none. The two rules nearest to retirement are
[`C-DOM-030`](../../constraints/domain/domain-constraints.md) and
[`C-DOM-032`](../../constraints/domain/domain-constraints.md), and neither qualifies: C-DOM-033 is
*additive* to C-DOM-030 rather than a generalisation of it — C-DOM-030 asserts register↔gate
equality, C-DOM-033 asserts register↔source completeness, and dropping either loses the other's
coverage. Derived, not typed: `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` = **10**;
`grep -rh '^| C-' constraints/ --include='*.md' | wc -l` = **82**.

---

## 6. Dispositions, and the simulation that checked them

Simulated on a scratch copy per [`agents/improvement-agent.md` L258](../../agents/improvement-agent.md#L256),
then the real log restored and proved byte-identical with `diff`.

| Finding | `observable_at` | Disposition | Why |
|---|---|---|---|
| [`IMP-0597`](../../logs/improvement-log.jsonl) | **V4** | stays `NEW` + `deferred_reason` + `revisit_when` | The gate lands, but the original reproduction — enter a test applicant with an ethnic group and see it save — needs the **deployed** form and a signed-in reviewer. The control is in the working tree, **uncommitted and undeployed**. An honest open entry beats a closed one nobody tested (`IMP-0208`, `IMP-0224`) |
| [`IMP-0598`](../../logs/improvement-log.jsonl) | V1 | `APPLIED`, with `evidence_grep` `{file: constraints/domain/special-category-register.yml, contains: rev_ethnicgroup}` | V1 needs no `reobserved`; the register row is readable from source the moment it lands |
| [`IMP-0599`](../../logs/improvement-log.jsonl) | n/a | `REJECTED`, `rejected_reason` naming the working control and the re-pointed class | No change warranted (§4) |

**Simulated result: the blocker trigger clears; the build stays red.**

```
TRIGGER: 30 NEW entries awaiting closure — 30 unread, 0 awaiting-approval (batch trigger is 30)
verify-improvement-log: FAILED
```

33 unread − 3 = **30**, and the threshold is 30. `improvement-log-check` is HARD with no
`--warn-only`, so `build-agent` still halts at step 3. **Approving this review does not enable the
build.** What does: a separately-scoped batch review of the 30 remaining unread findings.

### Digest delta — measured, not predicted

The generator was run against the scratch copy carrying all three final dispositions, then the real
log and both digests restored and proved byte-identical:

| | Before | After |
|---|---|---|
| Entries | 596 | 596 — no entry is appended by this review |
| Distinct lessons | 593 | **592** — `IMP-0599`'s lesson stops rendering once it is `REJECTED` |
| Recurring-class rows | 46 | **46** — unchanged, for the reason in §4 |

A review that *reduces* the digest by one lesson is the right outcome here: the lesson `IMP-0599`
carried was a restatement of a rule the digest already teaches through `IMP-0527`.

**Deliberately not done: closing one arbitrary extra finding to get under the threshold.** That
would be picking a number to satisfy a gate rather than a finding to resolve, and the
blocker-dispatch scope rule ([`IMP-0183`](../../logs/improvement-log.jsonl)) exists to stop a
one-finding dispatch from becoming a pass over its neighbours. The reviewer decides.

---

## 7. Scope — what was excluded, and on what

Per activation step 2, this is a **blocker** dispatch, so its scope is the three unread blockers.

| State | Count | Excluded because |
|---|---|---|
| `unread`, `blocker` | 3 | **in scope** — `IMP-0597`, `IMP-0598`, `IMP-0599` |
| `unread`, not `blocker` | 30 | Blocker dispatches are not batched with their neighbours (`IMP-0183`). To be stamped `excluded_by` naming this review on approval, so the exclusion does not read as an unlooked-at finding and does not trip a citation-stamp warning per id (`IMP-0557`) |
| `reviewer-deferred` | 119 | Carry a `deferred_reason` a human accepted. One, [`IMP-0274`](../../logs/improvement-log.jsonl), carries **no `revisit_when`** — a deferral with no way back. Reported, not changed here |
| `awaiting-approval` | 0 | none — no parked review is waiting on a keyword |
| `already-fixed` | 0 | none |

**Nine of the 30 excluded ids carry pre-existing citation-stamp warnings** from the 2026-09-01 and
2026-09-02 reviews: `IMP-0549`, `IMP-0550`, `IMP-0551`, `IMP-0552`, `IMP-0562`, `IMP-0563`,
`IMP-0566`, `IMP-0567`, `IMP-0583`. They are cited by review documents and carry no `reviewed_in`.
Not created here and not this review's to clear — they belong to the batch review.

**Also carried forward, not diagnosed here:** [`IMP-0592`](../../logs/improvement-log.jsonl) is a
recurrence of `untriaged-tool-warning` after review 10's gate (§1).

### Nothing was routed to another agent

There is **no routed-work table in this review**, so activation step 8's re-measurement obligation
for routed rows has no rows to re-measure. The one item that would have been routed —
re-observing `IMP-0597` at V4 — is recorded as that finding's `revisit_when` instead, which is
where a re-observation that needs a signed-in human belongs.

---

## 8. Bookkeeping state at gate time

~~Nothing applied. `APPROVE IMPROVEMENTS` not received at time of writing.~~ Superseded by §10 on
2026-09-04. `reviewed_in` was stamped on all three findings at step 6, **before** the keyword,
which is what made them read as `awaiting-approval` rather than unlooked-at while this document
waited.

---

## 9. Re-verification before applying

`APPROVE IMPROVEMENTS` received. Activation step 8 run before anything was written:

| Re-checked | Result |
|---|---|
| Log unchanged since the draft? | **Yes** — 596 entries, `IMP-0599` still the maximum id |
| Any entry carrying `corrects` against `IMP-0597`/`0598`/`0599`? | **None** |
| **Behavioural:** does the scoring flow read `rev_ethnicgroup`? (change 4's premise) | **No** — `grep -cE "body/rev_ethnicgroup"` returns 0, exit 1. **Executed, not re-read** |
| `IMP-0597`'s `deferred_reason` premises — still uncommitted and undeployed? | **Yes** — `git status` still shows the FormXml file modified; no commit, no `pipeline.log` entry |
| Register still lacks `rev_ethnicgroup`? (is the defect still real) | **Yes** — 0 matches |
| Derived counts unchanged? | **Yes** — 57 `verify-*.py`, 82 live rows, 10 retired |

No routed-work table existed, so §7's re-measurement obligation had no rows to re-measure.

---

## 10. Applied record — 2026-09-04

| # | Change | File | Verified by |
|---|---|---|---|
| 1 | `check_form_surface_coverage()` + `FORM_SURFACE_EXEMPT` (empty, documented) | [`scripts/verify-forms-and-views-reachable.py`](../../scripts/verify-forms-and-views-reachable.py) | **Both polarities executed.** Corrected tree: exit 0, `52 secured column(s) with a main-form control`. Pre-fix fixture (`git show HEAD` of the applicant form): **exit 1, 1 finding, 1 true positive**, naming `rev_applicant.rev_ethnicgroup` |
| 2 | **C-TECH-077** (HARD) | [`constraints/technology/technology-constraints.md`](../../constraints/technology/technology-constraints.md) | `verify-constraint-verifiers.py` exits 0 — 110 paths across 84 rows all resolve |
| 3 | Register row `rev_applicant.rev_ethnicgroup`, `secured: required` | [`constraints/domain/special-category-register.yml`](../../constraints/domain/special-category-register.yml) | Gate reports `21 special-category column(s) verified`; `C-DOM-031 17 secured, 4 documented exception(s)` |
| 4 | `rev_ethnicgroup` added to the FR-016 alternation | [`config/revitalise-grant-automation-build.yml`](../../config/revitalise-grant-automation-build.yml#L416) | The HARD FR-016 grep **re-run with the new alternation**: still PASS. `C-DOM-030 register ↔ FR-016 gate: in sync (21 names)` |
| 5 | `pending_adjudication:` — **51 rows, generated from source**, ⚠️-marked, plus a new `HOW TO ADD A COLUMN` clause | [`constraints/domain/special-category-register.yml`](../../constraints/domain/special-category-register.yml) | YAML parses; `columns: 21, pending_adjudication: 51` read back |
| 6 | C-DOM-033 completeness check, pending count printed on the PASS path too | [`scripts/verify-domain-invariants.py`](../../scripts/verify-domain-invariants.py) | `68 secured = 17 registered + 51 pending adjudication, 0 undeclared`, exit 0 |
| 7 | **C-DOM-033** (HARD) | [`constraints/domain/domain-constraints.md`](../../constraints/domain/domain-constraints.md) | `verify-constraint-verifiers.py` exits 0 |

**C-DOM-033 was proven able to fail, four ways.** A `--selftest` proves a gate *can* fail; these
prove it fails on the *right* things:

| Negative test | Result |
|---|---|
| `rev_ethnicgroup` removed from both lists — **`IMP-0598` itself, reproduced** | exit 1, names the column |
| A column in **both** lists | exit 1 — *"two lists that overlap are one list nobody maintains"* |
| A `pending_adjudication` row for a non-existent column | exit 1 |
| A **new** secured column declared nowhere (`rev_religiousbelief` fixture) | exit 1, names the column |

The first attempts at tests 2 and 3 patched the *comment* containing `pending_adjudication:`
rather than the YAML key, and so exited 1 for the wrong reason. They were rebuilt against the real
key and re-run; the rows above are the corrected runs. A fixture that fails for the wrong reason is
indistinguishable from one that works.

**No new script, no new build step.** `ls scripts/verify-*.py | wc -l` = **57**, unchanged, so
[`scripts/derived-counts-registry.json`](../../scripts/derived-counts-registry.json) needed no edit.
Constraint rows **82 → 84** live, **10** retired — both derived with the greps, never typed.
`verify-build-config.py` exits 0.

### Bookkeeping

| Finding | Landed as |
|---|---|
| [`IMP-0597`](../../logs/improvement-log.jsonl) | stays `NEW` + `deferred_reason` + `revisit_when` naming the reviewer and the exact V4 reproduction |
| [`IMP-0598`](../../logs/improvement-log.jsonl) | `APPLIED`, `evidence_grep` = `{special-category-register.yml, rev_ethnicgroup}`, `applied_by` recording the §3 deviation |
| [`IMP-0599`](../../logs/improvement-log.jsonl) | `REJECTED`, `class_instance_of` re-pointed to `gate-reassures-wrongly`, original name preserved in `rejected_reason` |
| The 30 out-of-scope unread entries | `excluded_by` = this document, reason in a new `excluded_reason` field |

**`excluded_by` had to be corrected mid-application, and it is worth recording why.** The first
pass wrote the *reason* into `excluded_by`; the gate parses that field as a **path** and raised 28
errors. The prose moved to `excluded_reason` beside it and `excluded_by` became the bare path. Two
entries (`IMP-0549`, `IMP-0596`) were also missed by that pass's id parse and stamped separately.
Final coverage is **30 of 30**, verified by re-deriving the unread set from the gate rather than
from the list I had already got wrong once.

Digest regenerated **once, last**: **597 entries, 592 distinct lessons**, 46 recurring classes.
`generate-known-failure-modes.py --check` exits 0.

### RESIDUAL — the build is still red, exactly as §6 predicted

`python3 scripts/verify-improvement-log.py --check` **exits 1** on a single trigger: **31 unread**
(the 30 carried forward, plus `IMP-0600` logged below) against a batch threshold of 30. All three
blockers are discharged and **0 errors** remain. `improvement-log-check` is HARD with no
`--warn-only`, so `build-agent` still halts at step 3 of 70. **The next dispatch is a batch review,
not a build.**

Also unchanged, and not this review's: `verify-derived-counts.py` reports **6 SOFT drifts**, all
pre-existing. Five are in files this review never touched — the pipeline config's `rev_setting` row
count (×2), two dev-summary secured-column figures, and the REV Trustee role header. The sixth is
`IMP-0600`.

---

## 11. Improvement log

**IMPROVEMENT LOG: 1 finding — [`IMP-0600`](../../logs/improvement-log.jsonl)** (`friction`,
`gate-reassures-wrongly`). Id from `scripts/allocate-improvement-id.py`; validator run **before**
the generator.

Trigger: *reality contradicted a document in this repository*. While checking whether any of the 6
SOFT derived-count drifts were caused by my own changes, I found that
`known-failure-modes-digest-line-count` **can never be green**. Its `claim_pattern` anchors on the
only line-count sentence in the generator's docstring, and that sentence is an explicitly **dated
measurement** — *"Measured 2026-09-01 at 562 log entries: the digest is 621 lines."* Correcting
`621` to `629` would not fix a stale figure; it would forge a dated record. The registry row is the
category error, not the prose.

Its intent is sound and well-evidenced — `IMP-0529`, `IMP-0534` and `IMP-0543` are three real
instances of the digest's size being restated from memory — so the proposal is to re-anchor it on a
new *undated* sentence or retire the row. Deliberately **not** fixed here: a `scripts/` edit inside
an approved review that the reviewer never saw is the quiet substitution §3 warns against.

**Neither `HEAD`'s digest nor mine is 621 lines — both are 629**, so this drift predates this
review and my regeneration moved the count by zero. Measured with
`git show HEAD:logs/known-failure-modes.md | wc -l` before any of the above was written.

The three measurement tables that disproved `IMP-0598`'s own proposal are recorded in §3 and in
that entry's `applied_by`, not as findings — a review's own re-measurement belongs in the review.
