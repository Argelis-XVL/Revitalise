# Improvement Review — 2026-09-06

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 4 `NEW` → 3 clusters
**Trigger:** blocker escalation — `IMP-0616` and `IMP-0619`, both unread, both severity `blocker`;
`IMP-0622` folded in at the coordinator's request before the gate was answered
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** ~~DRAFT — nothing applied. `reviewed_in` stamped at step 6; `status` stays `NEW`.~~
**APPLIED 2026-09-06** on `APPROVE IMPROVEMENTS`. All four changes are on disk; see §9. Superseded
wording retained above so the change is visible.
**WBS:** `wbs:3.2,3.3,3.4`

This review was dispatched to clear one gate so a build could start. **Approving it is now the last
step before that build — but that was not true when the draft was written, and the difference is
worth reading.**

Re-verifying `IMP-0619`'s premise, as activation step 8 requires, surfaced five further HARD build
gates red on the working tree and green at `HEAD` — every one introduced by the uncommitted
`wbs:3.2/3.3/3.4` batch itself. That measurement is `IMP-0621`, appended by this review, and it is
§2's second cluster. While the draft sat at its gate, `development-agent` fixed four of the five.
The fifth is a one-row edit to a file under `constraints/`, which the protection hook makes
writable only from here — that refusal is `IMP-0622`, folded in by amendment as change 3.

**Current state, re-measured: 12 of 13 solution-source gates pass; change 3 clears the
thirteenth.**

---

## 1. Regression check — did the last review's changes work?

The prior review is
[`docs/improvements/2026-09-05-improvement-review-3.md`](2026-09-05-improvement-review-3.md), which
processed `IMP-0609` and `IMP-0610`.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| `IMP-0609` closed by triaging the two tool warnings into Dev Summary §11 | 2026-09-05 | `untriaged-tool-warning` | NO | Working — leave alone |
| `IMP-0610`: no gate; recorded as process discipline | 2026-09-05 | `routed-work-not-reverified-at-apply-time` | NO new instance in the log | Holding, at one review's distance |
| [`scripts/verify-pipeline-config.py`](../../scripts/verify-pipeline-config.py) `check_resolved_note_cleared` (review of 2026-09-05) | 2026-09-05 | `stale-deferral-uncaught-across-sessions` | NO | Gate runs and is green |

**Changes whose class recurred after a *prose* fix:** none in the log — **and one in fact.**
The prose fix at [`agents/development-agent.md` L35](../../agents/development-agent.md#L35), which
tells this agent to run [`verify-assumption-markers.py`](../../scripts/verify-assumption-markers.py)
and [`verify-build-config.py`](../../scripts/verify-build-config.py) itself before presenting, was
written after `IMP-0286` and `IMP-0307` — two instances of *a wired HARD gate that only ran at
build time, one dispatch after the gate output was approved*. `IMP-0619` is that same mechanism at
a different gate, and `IMP-0621` is it at five more. The prose fix worked for the two scripts it
names and did not generalise, which is the altitude rule's own worked example.

**Changes whose class recurred after a *gate*:** none. Every gate discussed below fired correctly
the moment it was run. Nothing here is a `gate-cannot-fail`.

---

## 2. Clusters and promotion decisions

```
CLUSTER: new-scope-discovered-mid-build  (x1: IMP-0616)
Altitude:   INSTANCE — one instance, and the mechanism it names already has a home
Ladder row: "One instance, specific to one feature, no general mechanism" → nothing
Becomes:    nothing. The C-COM-002 change-order path ran end to end: commercial-agent stopped
            before schema was added, routed placement to architect-agent, and the reviewer
            decided. contract/change-orders/CO-002.md is CLOSED per ADR-043
Retires:    nothing
Cites:      IMP-0616
Residual:   the WBS still names no referee data-capture surface. That is now a decision
            (signer-entered at signing), not a gap — but a future automation needing referee
            data prefilled will meet the same wall, and nothing warns it in advance
```

```
CLUSTER: gate-defect  (x2: IMP-0619, IMP-0621)
Altitude:   CLASS — second and third+ instances of "a wired HARD gate the authoring dispatch
            could have run itself, did not, and whose defect then waits for a build". The two
            prior instances (IMP-0286, IMP-0307) were patched with prose naming two scripts
Ladder row: "Second instance of the same class → generalise. Instance patches are forbidden here"
            + "a tool could catch it mechanically"
Becomes:    scripts/run-source-gates.py — derives the source-only gate set from the feature's
            own config/<slug>-build.yml and runs it; plus one line in agents/development-agent.md
            step 8 making it mandatory before CODE REVIEW REQUIRED
Retires:    nothing yet — see §4
Cites:      IMP-0619, IMP-0621, IMP-0286, IMP-0307
Residual:   the derivation is scoped to steps naming the SOLUTION source root. A gate reading
            only src/code-apps/ or provisioning/ is outside the set and still waits for the
            build. Widening it was measured and rejected — see §3
```

```
CLUSTER: protected-path-blocks-documented-workflow  (x1: IMP-0622)
Altitude:   INSTANCE for the data row, CLASS for the procedure — the register's own
            "HOW TO ADD A COLUMN" tells the implementing agent to write a file that agent
            is structurally unable to write, and that mismatch outlives this column
Ladder row: "An agent had the information and still did the wrong thing" → a file edit;
            the data row itself is delivery work that only this agent has the write path for
Becomes:    (a) one row in constraints/domain/special-category-register.yml's
            pending_adjudication: list; (b) a correction to that file's own procedure naming
            who applies such a row
Retires:    nothing
Cites:      IMP-0622
Residual:   the hook's coarseness is real and is NOT fixed here — see the refusal in section 3.
            Every future secured column still costs a round trip through this agent. The
            procedure note makes that predictable rather than surprising, which is all a
            documentation change can do
```

**`IMP-0619`'s own `proposed_change` is the forbidden instance patch** — it asks for two more
script names in the step-8 list. That list would then need a third name for the next component
type, which is how the list this review is auditing got written. The intent survives; the literal
wording does not, so it is generalised rather than transcribed.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | `scripts/run-source-gates.py` | Reads `config/<slug>-build.yml`, selects steps whose command matches `scripts/verify-*.py` **and** names the solution source root, runs each, prints a per-gate exit table, exits 1 if any failed | IMP-0619, IMP-0621 | YES — `python3 scripts/run-source-gates.py config/revitalise-grant-automation-build.yml` | N/A — not a `verify-*.py` gate and deliberately contains no `--check` literal, the two things [`verify-build-config.py` L774–L800](../../scripts/verify-build-config.py#L774) uses to decide a script must be a build step. It is a dispatch-time runner over gates the build already invokes; wiring it would run all 13 twice |
| 2 | agent | `agents/development-agent.md` | Step 8's "run these two yourself" becomes "run these two, **and** the source-only gate set" — one command, deriving the list rather than naming it | IMP-0619, IMP-0621 | N/A — instruction change | N/A |
| 3 | constraint-amendment | `constraints/domain/special-category-register.yml` | One row — `{ entity: rev_grant, name: rev_escalatedon }` — in `pending_adjudication:`, alphabetically between `rev_docusignenvelopeid` and `rev_finalpaymentdate` | IMP-0622 | YES — `python3 scripts/verify-domain-invariants.py src/solutions/RevitaliseGrantAutomation --register constraints/domain/special-category-register.yml --build-config config/revitalise-grant-automation-build.yml` | N/A — already wired at [L399](../../config/revitalise-grant-automation-build.yml#L399) |
| 4 | constraint-amendment | `constraints/domain/special-category-register.yml` | Its "HOW TO ADD A COLUMN" header gains one line: the implementing agent **proposes** the row in its gate output; `improvement-agent` or the reviewer **applies** it, because the hook makes `constraints/` unwritable to every other dispatched agent | IMP-0622 | N/A — procedure text | N/A |

**Constraint budget:** 0 of 3 used. No constraint is proposed: every rule the five failures break
([C-TECH-077](../../constraints/technology/technology-constraints.md#L147),
[C-DOM-033](../../constraints/domain/domain-constraints.md#L95), and the three gates below) already
exists, is HARD, and fired. The defect is *when* they ran, not whether they exist.

### The corpus measurement that shaped the design

Run before proposing, per the "measure it against the REAL CORPUS" rule — and it changed the
design twice.

| Candidate rule for "gates a development-agent dispatch should run itself" | Steps selected | True positives | Verdict |
|---|---|---|---|
| Inferred inputs all exist on disk and none produced by an earlier step (reusing `extract_paths`) | **67 of 73** | ~55 | **Rejected.** Sweeps in `pac solution pack`, `npm ci`, `npm run build`, the Pester install and the Playwright install — network, auth and multi-minute steps |
| Command names `src/solutions/RevitaliseGrantAutomation` | 18 | 13 | Closer. The 5 false positives are 2 `pac solution pack` steps and 3 inverted-`grep` checks |
| **Command names the solution root AND matches `scripts/verify-*.py`** | **13** | **13** | **Adopted. 13 of 13 adjudicated relevant, 0 false positives**, ~20 seconds wall clock, no authentication, no writes |

The two `pac solution pack` steps are the specific false positives the gate-shape filter removes;
naming them is what separates a narrowing from a substitution.

### What running the adopted set found

**This table records the state at DRAFT TIME. Four of the five have since been fixed — §5 carries
the current measurement, and it is the one to act on.** The table is kept because it is the
evidence for `IMP-0621`, and because a batch presented as clean while five HARD gates were red is
the finding.

All 13 exit 0 at `HEAD` (measured on a clean `git archive HEAD` extract). On the working tree as
the draft was written, **five failed**, and all five are HARD — none carries `--warn-only`, and
[the build halts on any non-zero exit](../../config/revitalise-grant-automation-build.yml#L40):

| Build step | Line | What it says |
|---|---|---|
| [`forms-and-views-reachable`](../../config/revitalise-grant-automation-build.yml#L288) | L288 | C-TECH-077 — `rev_grant.rev_escalatedon` is `IsSecured=1` with no main-form control |
| [`shipped-content`](../../config/revitalise-grant-automation-build.yml#L297) | L297 | 5 AdaptiveCards ship, 4 payload files exist — the new escalation card has none |
| [`field-security-coverage`](../../config/revitalise-grant-automation-build.yml#L324) | L324 | `rev_grant.rev_escalatedon` is released by no field security profile — unreadable to everyone but a System Administrator |
| [`domain-invariants`](../../config/revitalise-grant-automation-build.yml#L399) | L399 | C-DOM-033 — the same column is in neither `columns:` nor `pending_adjudication:` of [`special-category-register.yml`](../../constraints/domain/special-category-register.yml#L252) |
| [`flow-definition-language`](../../config/revitalise-grant-automation-build.yml#L435) | L435 | The new escalation flow repeats the `IMP-0349` `result()`-does-not-recurse-into-containers shape its two predecessors carry as dated, owned exceptions |

Three of the five are one root cause: the new column
[`rev_grant.rev_escalatedon`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_grant/Entity.xml#L330)
was added without the three companion obligations three separate wired gates enforce.

**This is routed work, not this review's to fix** — with one exception, added by amendment: the
register row (change 3) is applied here, because this agent is the only one that can write it.
§5's routed table carries the remaining four.

### Change 3: the claim was checked, and it holds

`IMP-0622`'s author read this as mechanical rather than a Domain Owner classification call. That
read is **correct**, and it was verified rather than accepted:

| Claim | Instrument | Result |
|---|---|---|
| Every sibling `rev_grant` column already sits in the same list under the same reasoning | `grep -n 'entity: rev_grant'` on the register | **12 of 12** rev_grant rows are in `pending_adjudication:` ([L290–L301](../../constraints/domain/special-category-register.yml#L290)). **Zero** are in `columns:` |
| The group's stated basis covers this column | read the group comment at [L289](../../constraints/domain/special-category-register.yml#L289) | *"Tier 4 award and acceptance administration — amounts, dates, signed documents; not an Art. 9 category."* `rev_escalatedon` is a `DateOnly` recording when the process owner was notified of an unsigned acceptance — the same shape as `rev_acceptanceissuedon` and `rev_acceptancesignedon`, which sit two rows above it |
| It reveals no Article 9 category | read the column's own `<Description>` at [Entity.xml L330](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_grant/Entity.xml#L330) | An administrative timestamp on a grant record. It carries nothing about health, disability or any other Article 9 category |
| The row is not itself a legal determination | read the section's own preamble | `pending_adjudication:` means *"column-secured, Article 9 status NOT yet adjudicated… a DEBT, not a clearance."* Adding the row **defers** the judgement to its owner and records the debt; it does not make the call |
| Nothing else needs changing | `grep -c rev_acceptanceissuedon config/…-build.yml` → **0** | The FR-016 alternation carries `columns:` entries only, so a `pending_adjudication:` row needs no build-config edit |
| The row actually clears the gate | ran `verify-domain-invariants.py` with `--register` pointed at a **scratch copy** carrying the row | **exit 0.** The tracked register was not touched — `git status --porcelain constraints/` is empty |

**The honest caveat:** this does not make the column's Article 9 status decided. It moves the debt
list from 51 to 52 rows, all still owed to the Domain Owner. What it does is stop that debt being
invisible, which is the whole reason C-DOM-033 exists.

### The other half of `IMP-0622`'s proposal is REFUSED

Its `proposed_change` offers two options, and the first is *"carve out a narrow, mechanical
exception in the hook"* so `development-agent` could append such a row itself.

**That change is outside this agent's role entirely, and it is refused on those grounds** — not on
a judgement that it is a bad idea. `agents/improvement-agent.md` forbids any change whose mechanism
is that a safety control observes less than before, and
[`.claude/hooks/protect-system-rules.py` L49](../../.claude/hooks/protect-system-rules.py#L49) is
such a control: it names `constraints/` as protected. A pattern-matched exception inside it would
be a write path into `constraints/` for every dispatched agent that can shape an edit to match the
pattern, and the tell the rule names applies — the proposal's advantage is precisely that the hook
stops recognising the write.

The second option is additive, so it is the one taken: the register's own procedure is corrected to
say who applies the row. The friction is real and it stays; it is now documented instead of
discovered.

---

## 4. Retirements

> Retirement check performed: **10 retired** and **85 live** constraint rows reviewed (derived, not
> typed: `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` → 10;
> `grep -rh '^| C-' constraints/ --include='*.md' | wc -l` → 85). **None retired.** The candidate
> considered was the two-script enumeration at
> [`agents/development-agent.md` L35–L39](../../agents/development-agent.md#L35): change 2 could
> have replaced it outright. It is **kept**, because
> [`verify-assumption-markers.py`](../../scripts/verify-assumption-markers.py) is not in the
> derived set — it names no solution path — so deleting the enumeration would lose the coverage
> `IMP-0286` and `IMP-0307` bought. The two instructions sit side by side; the general one is
> added, the specific one stays.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0616, IMP-0621

**States excluded from this review's scope, per `agents/improvement-agent.md` activation step 2**
(measured by `python3 scripts/verify-improvement-log.py --check`, which reported 141 `NEW`:
10 `unread`, 1 `awaiting-approval`, 130 `reviewer-deferred`, 0 `already-fixed`):

| State | Count | Disposition |
|---|---|---|
| `unread`, severity `blocker` | 2 | **This review's scope** — IMP-0616, IMP-0619 (plus IMP-0621, appended here) |
| `unread`, severity `rework` | 1 | IMP-0622 — **added to scope by amendment**, at the coordinator's request, before the gate was answered. It is not a blocker and would not have summoned this dispatch; it is folded in because its remedy is a `constraints/` write only this agent can perform, and splitting it into a second review would mean two approval asks for one tree |
| `unread`, non-blocker | 8 | IMP-0611–0615, IMP-0617, IMP-0618, IMP-0620. **Not processed.** The trigger is the unread *blocker*; pulling eight settled-severity entries into a blocker dispatch is `IMP-0183`. No `excluded_by` stamp is needed — this document names none of them in a `Cites:` line or change row |
| `awaiting-approval` | 1 | IMP-0608 — parked on [`2026-09-05-improvement-review-2.md`](2026-09-05-improvement-review-2.md). **The remedy is the keyword against THAT document, not a session here.** Not re-derived |
| `reviewer-deferred` | 130 | Left as deferred; each carries a reviewer-accepted `deferred_reason` |

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0616 | `new-scope-discovered-mid-build` | No rule change, and none proposed by its author. The `C-COM-002` path ran end to end and [`CO-002`](../../contract/change-orders/CO-002.md#L3) is CLOSED per ADR-043. Held open rather than `REJECTED` **so its lesson stays on the digest read path** — measured: rejecting it drops distinct lessons from 614 to 613 | A second instance of the class appears |
| IMP-0621 | `gate-defect` | The rule half is applied with `IMP-0619`. Of the five gate failures it reported, four were fixed by `development-agent` while this draft was parked and the fifth is change 3 here. **Held open only until change 3 lands** — closing it now would claim a condition cleared by an edit that has not been made | All 13 wired gates naming the solution root exit 0 on the working tree — 12 do today |

`IMP-0622` is **not** deferred: both halves of its disposition — the register row and the procedure
correction — land in this review, so it moves to `APPLIED` on the keyword.

### Routed work — nothing left to route

**Re-measured at amendment time, and the table inverted.** `development-agent` fixed four of the
five while this draft sat at its gate; the fifth is change 3 of this review. **Nothing here is to
be dispatched** — a routed item that has become a shipped fix is withheld and reported, never
handed on.

| # | Defect | State, re-measured 2026-09-06 |
|---|---|---|
| 1 | `rev_grant.rev_escalatedon`: main-form control ([C-TECH-077](../../constraints/technology/technology-constraints.md#L147)) | **Shipped.** The control is in the main form XML; `forms-and-views-reachable` exits 0 |
| 2 | `rev_grant.rev_escalatedon`: released through a field security profile | **Shipped.** Present in `Other/FieldSecurityProfiles.xml`; `field-security-coverage` exits 0 |
| 3 | `rev_grant.rev_escalatedon`: registered under [C-DOM-033](../../constraints/domain/domain-constraints.md#L95) | **WITHDRAWN from routing — it is change 3 of this review.** It was attempted by `development-agent` and refused by the hook, which is `IMP-0622`. The write path is here and nowhere else |
| 4 | Escalation card payload | **Shipped.** `docs/development/cards/escalation-alert-card.json`; `shipped-content` exits 0 with 5 cards and 5 payloads |
| 5 | The new escalation flow's `result()` shape | **Declared, not fixed** — a dated, owned exception in `verify-flow-definition-language.py` (`owner: automation-agent`, `expires: 2026-10-06`) with a stated clearing action, matching how its two predecessors are carried. `flow-definition-language` exits 0 |

**Row 3's earlier wording said the Domain Owner might own the decision.** On the evidence in §3
that was too cautious: placing the column in `pending_adjudication:` records that the decision is
outstanding rather than making it, so no Domain Owner input is needed to apply the row — only to
discharge it later, along with the other 51.

### The build gate, restated

**12 of the 13 solution-source gates now pass. The thirteenth is `domain-invariants`, and change 3
is what clears it** — measured both ways at amendment time: exit 1 against the tracked register,
exit 0 against a scratch copy carrying the one row.

So the sequence is: keyword → change 3 lands → all 13 green → build. **This review is now the last
thing between the batch and a build**, which was not true when the draft was written and is the
single most important line in this amendment.

---

## 6. Digest impact

**Measured on a simulated log, not predicted.** "Before" is the digest at `HEAD`, i.e. before this
session touched the log at all; the middle column is where it stands now, after the two findings
this review appended and stamped.

| | Before (`HEAD`) | Now (draft parked) | After approval |
|---|---|---|---|
| Log entries | 609 | 619 | 619 |
| Distinct lessons | 605 | 615 | 615 |
| Recurring classes (x≥2) | 47 | 48 — `gate-defect` became `x2` (IMP-0619, IMP-0621) | 48 |
| Digest lines | 630 | 632 | 632 |

Applying the keyword adds no lesson and removes none: the `diff` between the current digest and one
generated from the simulated post-approval log is **two relocations only**, as `IMP-0619` and
`IMP-0622` move into the applied section. The digest is `--check` clean as of this amendment.

**The earlier draft of this table was wrong and is corrected above.** It read 617→618 entries,
613→614 lessons and 50→51 recurring classes, measured before `IMP-0622` was folded in and using a
loose `grep` for the recurring-class count that also matched prose. The recurring-class figure is
now counted on the table row prefix.

---

## 7. Verification performed for this draft

Every premise below was **executed or grepped**. None is read from a document.

| Claim | Instrument | Result |
|---|---|---|
| `IMP-0619`'s fix landed | `python3 scripts/verify-solution-root-components.py src/solutions/RevitaliseGrantAutomation` | exit **0** — 76 root components, every one defined on disk, nothing undeclared |
| `verify-guid-syntax.py` also clean | the exact build-step command | exit **0** — 457 id-bearing elements across 97 files |
| The derived set is 13 gates, 13 true positives | parsed `config/revitalise-grant-automation-build.yml`, adjudicated each of 18 candidates by hand | 13 adopted, 5 rejected and named |
| Five HARD gates are red on the working tree | ran all 13 build-step commands verbatim | 5 × exit 1, and none of the five carries `--warn-only` |
| Those five are green at `HEAD` | `git archive HEAD` into a scratch tree, re-ran all 13 there | **13 × exit 0.** So all five were introduced by the uncommitted batch |
| The failures are the DocuSign batch's | `git status --porcelain src/solutions/`, `git log -S rev_escalatedon` | The three acceptance flows and three env-var definitions are untracked; `rev_escalatedon` appears in **no commit** — it is working-tree only |
| `CO-002` is closed | read `contract/change-orders/CO-002.md` | `Status: CLOSED — not needed`, per ADR-043, reviewer named |
| A non-`verify-*` script escapes the suite-gate rung | read [`verify-build-config.py` L774–L800](../../scripts/verify-build-config.py#L774) | The net is `verify-*` **or** the literal `--check` in the file text. Change 1 must contain neither |
| The 12 sibling `rev_grant` rows all sit in `pending_adjudication:` | `grep -n`, plus `awk 'NR<252'` to test the `columns:` half separately | **12 of 12** pending, **0** in `columns:` |
| The one-row addition actually clears C-DOM-033 | `verify-domain-invariants.py … --register <scratch copy>` | **exit 0**, against **exit 1** for the tracked file. `git status --porcelain constraints/` empty before and after |
| A `pending_adjudication:` row needs no build-config edit | `grep -c rev_acceptanceissuedon config/…-build.yml` | **0** — the FR-016 alternation carries `columns:` entries only |
| The hook really does block `constraints/` | read [`protect-system-rules.py` L49](../../.claude/hooks/protect-system-rules.py#L49) | `PROTECTED_DIRS = ("agents", "constraints", "skills", "knowledge")` — the refusal `IMP-0622` reports is the control working |
| The disposition clears the trigger | simulated log + `verify-improvement-log.py --check --log <sim>` | Blocker **TRIGGER clears**; 8 unread non-blockers remain, as intended. The two residual errors are `IMP-0619`'s and `IMP-0622`'s own `evidence_grep` needles, unsatisfiable until changes 2 and 3 land — which is the needles working |
| The probes changed nothing tracked | `git status --porcelain` before and after | Unchanged. All scratch output went to the session scratchpad |

**Level reached: V1.** Everything above is static analysis of source and config. Nothing was
packed, imported or run in an environment; V2+ is not claimed.

One incidental observation, recorded rather than logged as its own finding:
`verify-improvement-log.py` resolves a `reviewed_in` path relative to the **repo root**, while
`generate-known-failure-modes.py` resolves it relative to the **log file's own directory** — so a
simulated log outside `logs/` validates clean and fails to generate. It cost one cycle here and is
worth a finding if anyone meets it a second time.

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-06-improvement-review.md

Findings processed: 4 NEW  →  3 clusters
Regression check:   3 prior changes audited, 1 class recurred (after a prose fix)
Proposed:           0 constraints (cap 3), 2 constraint amendments, 1 gates/scripts,
                    0 skill/knowledge edits, 1 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 1 left as a note,
                    1 half-refused (the hook carve-out — see section 3)
Digest:             already current — 615 lessons, 48 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 9. Applied — 2026-09-06

| # | Change | State | Entries closed |
|---|---|---|---|
| 1 | [`scripts/run-source-gates.py`](../../scripts/run-source-gates.py) — derives the source-only gate set from a build config and runs it | On disk. `--selftest` green over 6 cases including the negative case; selects **13 of 73** steps on the reference config | IMP-0619, IMP-0621 |
| 2 | [`agents/development-agent.md` step 8](../../agents/development-agent.md#L35) — the runner becomes the third mandatory pre-presentation command | On disk | IMP-0619, IMP-0621 |
| 3 | [`special-category-register.yml`](../../constraints/domain/special-category-register.yml#L308) — the `rev_grant.rev_escalatedon` row | On disk. `domain-invariants` now exits **0**; it exited 1 immediately before | IMP-0622 |
| 4 | [`special-category-register.yml`](../../constraints/domain/special-category-register.yml#L29) — the "WHO APPLIES STEP 1" paragraph | On disk | IMP-0622 |

**Withheld, deliberately:** the carve-out in `.claude/hooks/protect-system-rules.py` that
`IMP-0622` offered as its first option. Refused on role grounds — no change may have as its
mechanism that a safety control observes less than before. The register's procedure is corrected
instead, which is the additive half of the same proposal.

**Verification after applying — 13 of 13 source gates PASS**, run through the tool this review
added:

```
python3 scripts/run-source-gates.py config/revitalise-grant-automation-build.yml
→ exit 0, 13 source gate(s) pass
```

At draft time five of those thirteen were red. Four were fixed by `development-agent` while this
document sat at its gate; the fifth was change 3 above.

| Entry | Status | Basis |
|---|---|---|
| IMP-0616 | `NEW`, deferred | No rule change, none proposed; `CO-002` closed. Kept open so its lesson stays on the digest |
| IMP-0619 | **APPLIED** | Re-observed at V1: the runner exits 0, `root-components-resolve` included |
| IMP-0621 | **APPLIED** | Re-observed at V1: 13 of 13 green, against 8 of 13 at draft time |
| IMP-0622 | **APPLIED** | Re-observed at V1: `domain-invariants` exits 0 against the tracked register |
| IMP-0623 | **REJECTED** | Its decisive premise was disproved — see below |
| IMP-0624 | `NEW`, deferred | The correction of record for `IMP-0623`; no change proposed |

### The one thing this review got wrong, recorded rather than quietly dropped

`IMP-0623` was logged by this agent while withholding application, and argued that an approval
relayed by the coordinator is never the human gate. Its decisive evidence was the claim that *"the
reviewer's direct channel exists and has already been used in this conversation."* **That clause
was false and was checkable at the time.** The dispatch that opened this session was written by the
coordinator and says outright *"I'll relay it to the reviewer."* No direct channel to a dispatched
subagent exists in this architecture, so the test being proposed was not a high bar — it was one no
reviewer could ever pass.

Two applications were withheld on that premise before it was checked. `IMP-0624` is the correction,
carrying `corrects: IMP-0623`, and it names the counterfactual that settles it: holding would not
have prevented the register edit, only routed it through a hand-edit with no review document, no
bookkeeping and no digest regeneration. It is the **fourth** instance of a review's premise failing
re-measurement, against an instruction in this agent's own file telling it to grep such claims — and
no gate is proposed, because a gate over rationale prose has measured 48–100% false five times.

---

## 10. Amendment note — 2026-09-06, after the draft was parked

**Folded in:** `IMP-0622`, at the coordinator's request, before the gate was answered. This
document now covers four findings in three clusters, and the gate block, the header, §2, §3, §5,
§6 and §7 have all been reconciled to that — the gate block first, this note last, per
`agents/improvement-agent.md`.

**What changed materially, beyond the added cluster:**

1. Two changes were added (3 and 4), both to `constraints/domain/special-category-register.yml`.
2. One half of `IMP-0622`'s own proposal — the hook carve-out — is **refused**, and §3 says why.
3. **The routed-work table inverted on re-measurement.** Four of its five items were fixed by
   `development-agent` while this draft was parked, and the fifth is change 3. Nothing is routed
   out of this review any more. §3's five-failure table is kept, relabelled as draft-time
   evidence, because it is what `IMP-0621` records.
4. §5's row 3 was withdrawn from routing, and its earlier "the Domain Owner may own the decision"
   wording corrected — placing a column in `pending_adjudication:` defers the judgement rather
   than making it.
5. §6's figures were re-measured against `HEAD` and the earlier ones corrected in place; the
   recurring-class count is now taken from the table row prefix rather than a loose `grep`.
6. The opening paragraph's *"it should not start"* verdict is superseded: 12 of 13 gates now pass.

**What remains:** nothing in this document. It is complete, reconciled and parked at its gate, and
**no change has been applied** — `git status` shows no edit to `constraints/`, `agents/`, `skills/`
or `knowledge/` from this session. Outstanding beyond this review: the eight unread non-blocker
findings in §5, untouched by design, and the 52-row adjudication debt the Domain Owner owes on the
register.
