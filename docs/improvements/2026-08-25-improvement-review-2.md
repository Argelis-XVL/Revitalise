# Improvement Review 28 — 2026-08-25

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 14 `NEW` (`unread`) → 8 clusters
**Trigger:** batch — 14 unread against a batch trigger of 10, no unread blocker
**Status:** ~~DRAFT. AWAITING `APPROVE IMPROVEMENTS`. Nothing in this document is on disk.~~ —
**corrected 2026-08-25: `Approve Improvements` received and APPLIED IN FULL. All 12 changes are on
disk. See [section 10](#10-applied--2026-08-25) for what landed, what was measured, and the two
things that changed under this review while it was being applied.**
**Scope note:** drafted immediately after [review 26](./2026-08-24-improvement-review-6.md) was applied, in the same session. Eleven of the fourteen findings were never in review 26's scope; **three are review 26's own application output**, and two of those record a change of review 26's acquiring a defect within the hour.
**WBS:** cluster B carries a live commercial consequence on [CO-001-A1](../../contract/change-orders/CO-001-A1.md) (`wbs:6.9`); everything else is system work, not billable ([C-COM-002](../../constraints/commercial/commercial-constraints.md#L35))

---

## Summary

**A live change order is pricing scope the reviewer withdrew, and that is the one finding here with hours attached.** [CO-001-A1](../../contract/change-orders/CO-001-A1.md#L49) still itemises `NFR-027 — suppression/grouping helper` at 1–1.5h and [FR-061's benchmark charts](../../contract/change-orders/CO-001-A1.md#L46) at 2–3.5h. The SDD marks [NFR-027 withdrawn](../../docs/plans/revitalise-grant-automation-plan.md#L403) and [the benchmark clause withdrawn](../../docs/plans/revitalise-grant-automation-plan.md#L441). Nothing compares the two, so a change order keeps a withdrawn line item and its hours indefinitely.

**Two of the fourteen findings are already fixed in delivery and close on a re-measurement, not on a document.** `verify-assumption-markers.py` now **passes** — all four orphan markers [IMP-0299](../../logs/improvement-log.jsonl#L296) reported are in source.

**The most uncomfortable result is the regression check: two of review 26's own seven changes acquired a finding within the hour of being applied**, one of them the residual its own docstring predicted. Neither is a reason to withdraw them; both are named in §1.

**What needs you:** four new gates, six knowledge/skill edits, two agent-file edits, one constraint amendment, **no new constraints**, and **two retirement candidates — the first the obligation has produced in four reviews.**

---

## 1. Regression check — did review 26's changes work?

[Review 26](./2026-08-24-improvement-review-6.md) was applied roughly an hour before this draft, so most rows below are *measured but young*. Where a change is prose with no evidence yet, this table says so rather than claiming success.

| Prior change | Class it targeted | Recurred? | Verdict |
|---|---|---|---|
| [`improvement-log-check`](../../config/revitalise-grant-automation-build.yml#L141) + [`workflow-syntax`](../../config/revitalise-grant-automation-build.yml#L144) steps | a HARD gate reachable only inside `unit-tests` | no | **Worked, and one is red on purpose.** `improvement-log-check` fails in ~1s on the batch trigger this document exists to clear; `workflow-syntax` exits 0 |
| [`check_suite_gates_are_steps()`](../../scripts/verify-build-config.py#L638) | same, at class altitude | **YES — its own stated residual, within the hour** | **Right rule, incomplete source.** See below |
| [`check_corrections()` second case](../../scripts/verify-improvement-log.py#L1381) | a fix landing without its queue entry moving | no | **Worked.** Correctly silent on [IMP-0309](../../logs/improvement-log.jsonl#L306)'s `corrects` — its target is `APPLIED`, so the queue entry did move |
| [`corrects` documented](../../skills/how-to-log-an-improvement.md#L128) | a field two gates read and no author was told to write | no | Prose. [IMP-0309](../../logs/improvement-log.jsonl#L306) is the first entry written after it and does set `corrects` |
| change 5 — **withheld** | two HARD rows naming a dead CI path | n/a | Premise failed re-verification. [IMP-0308](../../logs/improvement-log.jsonl#L305), and §3 change 12 re-proposes it in additive form |
| [models.yml trigger](../../config/models.yml#L91) + [skill](../../skills/how-to-select-a-model.md#L48) | an escalation trigger counting a document's backlog | **YES — its first form could not reach the reader** | **Worked on the second attempt.** See below |
| [intake step 2](../../skills/how-to-intake-external-documents.md#L38), [category-as-field-list trap](../../skills/how-to-write-requirements.md#L94) | open questions the repo answers; category-level FRs | no | Prose, one hour old. No evidence either way yet |

**The rung that acquired its own residual.** `check_suite_gates_are_steps()` asserts that every gate script `BuildGates.Tests.ps1` exercises has its own step in the build config. Its docstring names the residual at design time: *"A gate the suite exercises through some other call shape, or one that lives in no suite at all, is invisible here."* Within the hour, [IMP-0309](../../logs/improvement-log.jsonl#L306) supplied the instance — `generate-subagents.py --check` had been failing with all 18 `.claude/agents/` files stale for about 26 hours, and it is not in the suite, so the new rung cannot see it. **A residual that acquires an instance in under an hour was not a residual, it was a scope decision.** §3 change 10 widens the source from the suite to `scripts/` itself.

**The change whose first form could not reach its reader.** Review 26 change 6 was first applied as a YAML **comment** above the trigger in `models.yml`. `generate-subagents.py` keeps values and discards comments, so the clarification sat in the file a human edits and was absent from `.claude/agents/plan-agent.md`, which is the copy a dispatched `plan-agent` actually reads. Caught by regenerating and grepping the generated file rather than re-reading the source edit; re-applied inside the string. Logged as [IMP-0310](../../logs/improvement-log.jsonl#L307). **`--check` stayed green throughout** — the generated files were current and merely silent, which is why no gate could have caught it.

**Fourth row of the agent's own regression table — did closure evidence match the level?** Two entries here are `V1` and closed on a gate run, which is the right level. [IMP-0279](../../logs/improvement-log.jsonl#L276) was `V4` and was deliberately **left open** by review 26 rather than closed on a skill edit. That is the row that was failed by `IMP-0208` and honoured here.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: declared-policy-not-mechanically-enforced  (x2 here: IMP-0299, IMP-0307; x11 overall)
Altitude:  AGENT FILE, and the mechanical half ALREADY SHIPPED and already worked.
           verify-assumption-markers.py exists, is wired HARD as `assumption-markers`,
           and today it PASSES -- 6 OPEN rows checked, all carrying markers, 24 rows
           total. All four orphans IMP-0299 reported are fixed in source. What is
           still missing is one line in the AUTHORING agent's gate sequence:
           agents/development-agent.md never names the script, so an orphan marker is
           found by the build one dispatch AFTER the Dev Summary gate was approved.
Ladder row: "an agent had the information and still did the wrong thing"
Becomes:   one command in development-agent's gate steps. NOT a new constraint --
           C-TECH-052 already binds this and is already enforced.
Retires:   nothing.
Cites:     IMP-0299, IMP-0307, IMP-0286
Residual:  The script reads a register table's 'Where' column. Seven OPEN rows name no
           'Where' target at all and are reported as unresolvable, not failed -- an
           assumption whose location is unstated is still outside the gate.
```

```
CLUSTER B: incorporated-document-version-mismatch  (x2: IMP-0297, IMP-0071)
Altitude:  SCRIPT. Second instance of the class, so the altitude rule forbids fixing
           CO-001-A1 by hand and moving on. MEASURED LIVE: the change order still
           prices NFR-027 (withdrawn) and FR-061's benchmark half (withdrawn).
Ladder row: "a tool could catch it mechanically" + "second instance -> generalise"
Becomes:   scripts/verify-change-order-requirements.py -- every FR/NFR id itemised in
           contract/change-orders/*.md must exist in the SDD and not be WITHDRAWN or
           struck through. Wired SOFT: a commercial gate never halts a build
           (CLAUDE.md, Commercial Rules), it reports.
Retires:   nothing.
Cites:     IMP-0297, IMP-0071
Residual:  It matches ids. A change order that prices withdrawn scope in PROSE without
           naming the id, or sizes a clause that was reworded rather than withdrawn, is
           invisible. It also cannot judge whether a still-valid id's HOURS moved.
```

```
CLUSTER C: requirement-names-data-the-solution-cannot-supply  (x2: IMP-0296, IMP-0293)
Altitude:  SKILL LINE, extending a section that already exists rather than adding one.
           Review 27 built the Data Provenance section for IMP-0293's flavour -- no
           COLUMN supplies the item -- and MEASURED TODAY it covers only that: its two
           questions are "does the column exist?" and "does field security release it?",
           both internal. IMP-0296 is the other flavour: no ORGANISATION holds the data.
           An external reference dataset appears in no Entity.xml, so it is absent from
           both sides of every source-against-source comparison this repo makes.
Ladder row: "second instance -> generalise" (one section, both flavours)
Becomes:   a third row in the Data Provenance table for external sources, plus the
           definition IMP-0296's root cause turns on: 'non-blocking' fences off the
           BUILD and is never authority to commit the clause it qualifies.
Retires:   nothing.
Cites:     IMP-0296, IMP-0293
Residual:  Prose, unavoidably. No gate can read whether a named owner really owns a
           dataset, and C-TECH-066 binds the TAD rather than the SDD.
```

```
CLUSTER D: dispatched-agent-stalls-silently  (x3: IMP-0300, IMP-0291, + the resumed
           improvement-agent dispatch IMP-0300 itself records)
Altitude:  SCRIPT. Third instance, so a fourth prose patch is forbidden outright.
Ladder row: "a tool could catch it mechanically" + third instance
Becomes:   scripts/verify-routing-reconciliation.py, FORWARD-ONLY from a cutoff date,
           on the IMP-0181 precedent. MEASURED: logs/routing.log holds 107 ROUTED_TO
           lines against 15 GATE_RECEIVED and 19 STALLED/BLOCKED, so a gate over
           history would emit roughly 70 false positives and teach people to ignore it.
Retires:   nothing.
Cites:     IMP-0300, IMP-0291, IMP-0181
Residual:  A dispatch that produces a gate line and no work is still invisible -- the
           check reads the log's shape, never the artefact. IMP-0300's own remedy
           ("before trusting a routing.log claim, grep the artefact") stays prose.
```

```
CLUSTER E: the apply step's own bookkeeping, and generated artefacts that cannot
           say they are stale  (x3: IMP-0301, IMP-0309, IMP-0310)
Altitude:  MIXED, and deliberately not one change. IMP-0301 is an AGENT FILE fix
           (improvement-agent's apply step batches all bookkeeping last, so any
           interruption lands in the worst state: durable changes on disk, nothing
           recording them). IMP-0309 is a GATE (wire the generator's own --check into
           the build, and widen the rung from cluster A of review 26). IMP-0310 is a
           KNOWLEDGE LINE (a rule written as a YAML comment never reaches the generated
           file). They share a property -- a claim about a generated or half-applied
           artefact was inherited instead of measured -- but they have three different
           cheapest homes, and collapsing them would be tidiness, not altitude.
Ladder row: "the system's own memory failed" + "a tool could catch it mechanically"
Becomes:   three changes: activation step 8 closes each entry as its change lands;
           generate-subagents --check becomes a build step and the suite-gate rung reads
           scripts/ instead of the suite; one line in models.yml saying which keys
           propagate.
Retires:   nothing.
Cites:     IMP-0301, IMP-0309, IMP-0310, IMP-0298, IMP-0172
Residual:  A sixth log state ('partly-applied') would make an interrupted review
           machine-readable. NOT proposed here -- it changes the gate every agent's
           build depends on, and this review already proposes four gates. Section 5.
```

```
CLUSTER F: approved-document-internally-inconsistent  (x2: IMP-0302, IMP-0204)
Altitude:  SCRIPT. Second instance, and the section structure is fixed by
           templates/improvement-review-template.md, which makes it tractable.
           Note this review is itself under the rule: review 27 said section 5 would
           ask a question and section 5 never did, so the reviewer approved a document
           without the altitude call it promised.
Ladder row: "a tool could catch it mechanically" + "second instance -> generalise"
Becomes:   scripts/verify-review-document.py -- (a) every 'section N' cross-reference
           resolves to a heading that exists, (b) every deferral naming a section is
           matched by a question in that section, (c) the status header agrees with
           whether the changes are on disk, which is IMP-0204's half.
Retires:   nothing, but it SUBSUMES check_review_status_headers() in
           verify-improvement-log.py -- see the honest note in section 3.
Cites:     IMP-0302, IMP-0204
Residual:  (b) is a heuristic over prose. A deferral phrased without naming a section,
           or a question a human would not recognise as one, slips past.
```

```
CLUSTER G: the code-app-to-flow platform contract, and evidence levels in knowledge
           files  (x4: IMP-0303, IMP-0304, IMP-0306, IMP-0305)
Altitude:  KNOWLEDGE for three of them, SKILL for the fourth, plus ONE ALTITUDE
           QUESTION I am not answering myself. MEASURED: knowledge/technology/
           power-automate.md line 13 still tells an architect to call a flow from a
           code app "via HTTP action ... using a custom API or Power Automate HTTP
           trigger". Both are wrong for this stack, and the first would violate HARD
           C-TECH-048 -- an HTTP-trigger URL carries a SAS key, and embedding one in a
           client-side app is exactly the hand-rolled credential handling that row
           forbids. The first-party route is 'pa app add flow'. That single wrong row
           contributed to ADR-025 designing a nightly batch, a table, an option set, a
           purge job and four provisioning items that were then deleted.
Ladder row: "one instance, cause is general, a human needs to know it" x3, plus
           "second instance of the same class in one dispatch -> generalise" for the
           evidence-column proposal IMP-0304 makes.
Becomes:   corrected + expanded rows in power-automate.md and code-apps.md (including
           the negative fact: List rows does NOT support aggregate FetchXML, only
           'distinct'), the privileged-vs-scheduled separation IMP-0303 asks for, and
           one rule in how-to-verify-a-platform-contract.md section 2: evidence must come
           from the artefact that GOVERNS the claim.
Retires:   nothing.
Cites:     IMP-0303, IMP-0304, IMP-0305, IMP-0306
Residual:  Both new platform facts are E2 (vendor documentation), NOT observed live on
           this project. Recorded as E2 and not as verified. The repo-wide evidence
           column IMP-0304 proposes is a section 5 decision, not a change here.
```

```
CLUSTER H: finding-diagnosis-unverified  (x1 here: IMP-0308; x4 overall)
Altitude:  CONSTRAINT AMENDMENT, in the ADDITIVE form -- which is the whole point.
           Review 26 change 5 was approved and WITHHELD because its premise ("CI has
           never fired") was inherited from IMP-0165 rather than measured, and the
           ci.yml trigger had been broadened the same day IMP-0165 was written.
Ladder row: "the order of steps was wrong" -- a premise was written into a rule before
           it was measured
Becomes:   C-TECH-061 and C-TECH-063's Verify By name BOTH enforcement paths, the CI
           validate job AND the new build steps, rather than replacing a path whose
           deadness is unproven.
Retires:   nothing.
Cites:     IMP-0308, IMP-0165
Residual:  THE UNDERLYING QUESTION IS STILL UNANSWERED AND CANNOT BE ANSWERED HERE.
           Whether CI has ever fired needs one authenticated `gh run list`; gh is not
           authenticated in any agent session. Section 5 assigns it.
```

---

## 3. Proposed changes

| # | Type | Target | What it does | Can it fail? |
|---|---|---|---|---|
| 1 | **agent file** | [development-agent.md gate steps](../../agents/development-agent.md#L186) | Names `python3 scripts/verify-assumption-markers.py` as a command the authoring session runs before presenting `CODE REVIEW REQUIRED` | Prose; the script is the mechanical half and already runs HARD |
| 2 | **new gate** | `scripts/verify-change-order-requirements.py` + SOFT build step | Every FR/NFR id itemised in `contract/change-orders/*.md` exists in the SDD and is not `WITHDRAWN`/struck through | **YES, measured** — fires now on [NFR-027](../../contract/change-orders/CO-001-A1.md#L49) and [FR-061](../../contract/change-orders/CO-001-A1.md#L46) |
| 3 | **skill** | [Data Provenance](../../skills/how-to-write-requirements.md#L59) | Third row for external sources (must resolve to a source that exists **and** a named owner), plus: `non-blocking` fences off the build, never the clause | Prose |
| 4 | **new gate** | `scripts/verify-routing-reconciliation.py` + build step | Every `ROUTED_TO` after a cutoff carries a terminal line naming the same agent and feature | **YES** — must be measured at the chosen cutoff before wiring |
| 5 | **agent file** | [improvement-agent.md activation step 8](../../agents/improvement-agent.md#L127) | Close each entry as its change lands; regenerate the digest last. This session followed the discipline manually — it is why the log stayed truthful through a 12-change apply | Prose |
| 6 | **new gate** | `scripts/verify-review-document.py` | Cross-references resolve; every deferral naming a section is matched by a question there; status header agrees with disk | **YES** — must fire on review 27's missing §5 question, the fixture |
| 7 | **knowledge** | [power-automate.md L13](../../knowledge/technology/power-automate.md#L13) | Correct the wrong row to `pa app add flow` with its preconditions; record that `List rows` does **not** support aggregate FetchXML (only `distinct`) | Prose; both facts marked **E2**, not verified live |
| 8 | **knowledge** | `knowledge/technology/code-apps.md` | Privileged compute and *scheduled* compute are two questions; name both delivery mechanisms and require staleness to be justified on its own merits | Prose |
| 9 | **skill** | [how-to-verify-a-platform-contract.md §2](../../skills/how-to-verify-a-platform-contract.md#L54) | Evidence must come from the artefact that **governs** the claim: a privilege claim cites the role definition, a behaviour claim cites application code | Prose |
| 10 | **gate widening** | [`check_suite_gates_are_steps()`](../../scripts/verify-build-config.py#L638) + a build step for `generate-subagents.py --check` | Read `scripts/` instead of only the suite, with the exemption dict carrying a reason per script legitimately having no step | **YES** — must be re-measured; it will name more scripts than the 2 it was built on |
| 11 | **knowledge** | [config/models.yml](../../config/models.yml#L91) | One line stating which keys propagate into `.claude/agents/` as values, and that comments do not | Prose |
| 12 | **constraint amendment** | [C-TECH-061](../../constraints/technology/technology-constraints.md#L131), [C-TECH-063](../../constraints/technology/technology-constraints.md#L133) | `Verify By` names **both** the CI `validate` job and the new build steps — additive, replacing nothing | Prose inside two HARD rows |

**Zero new constraints against a cap of three.** One amendment, four gates, five knowledge/skill edits, two agent-file edits.

**An honest overlap in change 6.** `verify-review-document.py` would subsume `check_review_status_headers()`, which already lives in `verify-improvement-log.py` and enforces `IMP-0204`'s half. Two gates asserting one rule is the duplication the anti-bloat limits exist to prevent, so if change 6 is approved the existing function is **retired into it**, not left running alongside — named here so the retirement is a decision rather than an accident.

---

## 4. Retirements — two candidates, and the obligation finally earned its keep

**For the first time in four reviews the retirement audit produced named candidates, and it did so because review 26 §5 re-pointed it.** The re-pointed question is *"has any retired row's reinstatement condition fired?"* rather than *"is any live row redundant?"*.

**Candidate 1 — [C-TECH-012](../../constraints/technology/technology-constraints.md#L50), half its retirement premise has expired.** Its `retired_reason` gives two grounds: *"no static analysis tool is installed, and `knowledge/technology/coding-standards.md` defines no complexity limit for it to read. Two undefined halves make an unevaluable rule."* The first half is now **false**: `eslint` 10.9.0 and `typescript-eslint` 8.67.0 are installed, and [`code-app-lint`](../../config/revitalise-grant-automation-build.yml#L890) runs `eslint .` as a build step. The second half is **still true** — [eslint.config.js](../../src/code-apps/trustee-review-portal/eslint.config.js#L10) sets no `complexity` rule and coding-standards defines no threshold. So the row is one config line and one threshold decision away from enforceable. This is the same shape as the reinstatement review 27 found four days late.

**Candidate 2 — [C-TECH-011](../../constraints/technology/technology-constraints.md#L49), whose `retired_reason` states its own reinstatement price.** It says the rule is *"one `grep -rn 'TODO\|FIXME\|HACK'` build step away from being real — add the step and reinstate the row with a new id."* That step still does not exist. Whether a TODO marker in shipped source matters here is a judgement I should not make unasked.

**Derived, not typed: 80 live constraint rows and 10 retired**, via `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l`. Unchanged by this review, which proposes no new rows.

**Neither candidate is proposed as a change.** Both are reinstatements of rules a previous review deliberately retired, and reinstating a rule the system chose to drop is a reviewer's call, not an agent's. §5 asks.

---

## 5. What you need to decide

**Nothing blocks this review. Six things want an answer, and the first is the only one with hours attached.**

> **A note on how question 6 got here.** It was missing from the first draft of this section while §2's cluster G promised it — the precise defect [IMP-0302](../../logs/improvement-log.jsonl#L299) records and change 6 proposes a gate for. It was caught by grepping this document's own body for section-5 promises and diffing them against the questions actually present, which is the check change 6 would automate. Recorded because a review that commits this defect while proposing its fix should say so.

**1. CO-001-A1 prices withdrawn scope — who fixes it, and is it a resize or a correction?** [NFR-027](../../contract/change-orders/CO-001-A1.md#L49) at 1–1.5h and [FR-061's benchmark half](../../contract/change-orders/CO-001-A1.md#L46) at 2–3.5h are both withdrawn in the SDD. Change 2 stops it recurring; it does not fix the document. That is `commercial-agent`'s, and [IMP-0288](../../logs/improvement-log.jsonl#L285) already established that this change order's estimates need re-opening when the design lands.

**2. Should the `corrects` rung's `class_instance_of` sibling be built?** This is the question [review 27 promised in its §5 and never asked](../../logs/improvement-log.jsonl#L299), which is why it is asked here explicitly. Warn when a new entry shares a `class_instance_of` with a finding a pending review concluded needed **no change** — the shape that would have caught [IMP-0288](../../logs/improvement-log.jsonl#L285), which carried no `corrects`. It keys on a **mandatory** field, unlike `corrects`. Review 26 declined it as a third patch to one script in three days; with review 26 now applied, it would be a fourth. **My recommendation is to build it and retire the two `corrects` cases into it**, as one rung over "a review's conclusion has been contradicted", rather than three cases in one function.

**3. Should the log gain a sixth state, `partly-applied`?** [IMP-0301](../../logs/improvement-log.jsonl#L298) proposes it: a review document exists, the keyword was sent, and some of its findings are `APPLIED` while others are still `NEW`. That is the state review 27 sat in for four hours while the gate reported seventeen unread findings and demanded a review of work already half done. **I recommend deferring it.** Change 5 addresses the same defect at prose altitude for a fraction of the cost, and this review already proposes four gates.

**4. Do the two retired rows come back?** [C-TECH-012](../../constraints/technology/technology-constraints.md#L50) needs a complexity threshold chosen and one eslint rule; [C-TECH-011](../../constraints/technology/technology-constraints.md#L49) needs a `TODO`/`FIXME` grep step and a decision that markers in shipped source matter. Both are cheap. Neither is mine to reinstate.

**5. Who runs `gh run list`?** Whether CI has ever fired on this project is **unresolved**, cannot be resolved from any agent session (`gh` is unauthenticated everywhere), and is load-bearing for two HARD rows' `Verify By` and for the stale claim now sitting in [three](../../config/revitalise-grant-automation-build.yml#L112) places in the repository. Change 12 is written to be correct either way, deliberately. One authenticated command settles it.

**6. Should `knowledge/technology/*.md` capability tables gain an evidence column?** [IMP-0304](../../logs/improvement-log.jsonl#L301) proposes it as the altitude fix for its own class: an `E1`/`E2`/`E3`/`UNVERIFIED` column, so an unverified vendor claim is visibly unverified **at the point of use** — the same discipline `C-TECH-052` already imposes on hand-authored source. The case for it is [power-automate.md L13](../../knowledge/technology/power-automate.md#L13), a row that was template text nobody ever checked, that names a mechanism which would violate a HARD constraint, and that cost a TAD revision cycle. The case against is scope: it touches every knowledge file, and most rows would be back-filled as `UNVERIFIED` by an agent guessing at their provenance, which is a large edit that adds one honest word per row. **My recommendation is to add the column to the two files changes 7 and 8 already touch, and let it spread as rows are edited** — rather than a repo-wide back-fill nobody can evidence.

**One finding names delivery work that is not mine.** [IMP-0296](../../logs/improvement-log.jsonl#L293) records that the TAD's benchmark design — a Dataverse column, a `rev_setting` seed step and its own §5.3 — was built for a dataset that never existed and is now dead work to unwind. That is `architect-agent` and `pm-agent`, not this review.

---

## 6. Verification executed for this review

**Level reached: V1, measured.** Nothing in this document is on disk. No live environment was touched. Every figure below was produced during this session, after review 26 was applied.

| Check | Result |
|---|---|
| `verify-improvement-log.py --check` | **exit 1** — one problem: 14 unread against a batch trigger of 10. Blocker trigger clear |
| `verify-improvement-log.py --selftest` | exit 0 — **53 fixtures** |
| `verify-build-config.py` on the real config | **PASS — 50 steps, 38 gates**, including the new `suite gates have their own step` row |
| `verify-assumption-markers.py` | **PASS — 6 OPEN rows, every one carrying its marker; 24 rows total, 11 closed, 7 unresolvable.** All four of [IMP-0299](../../logs/improvement-log.jsonl#L296)'s orphans confirmed present in source |
| Cluster B, measured against both documents | CO-001-A1 still prices NFR-027 and FR-061's benchmark half; SDD marks both withdrawn at [L403](../../docs/plans/revitalise-grant-automation-plan.md#L403) and [L441](../../docs/plans/revitalise-grant-automation-plan.md#L441) |
| Cluster D, `logs/routing.log` | **107 `ROUTED_TO`, 15 `GATE_RECEIVED`, 19 `STALLED`/`BLOCKED`** — a history-wide gate would emit ~70 false positives, so forward-only from a cutoff is the only workable shape |
| Cluster C, review 27's Data Provenance section | Covers the internal flavour only — both its questions are `(table, column)` questions. [IMP-0296](../../logs/improvement-log.jsonl#L293)'s external-dataset flavour is genuinely uncovered |
| Cluster G, `power-automate.md` L13 | Wrong row still present verbatim, and its first named mechanism would violate HARD `C-TECH-048` |
| Retirement audit, all 10 retired rows | 2 candidates found — the first the obligation has produced in four reviews |
| `generate-subagents.py --check` | exit 0, 18 files current — **now** true, having been false for ~26 hours ([IMP-0309](../../logs/improvement-log.jsonl#L306)) |
| `generate-known-failure-modes.py --check` | exit 0 — **307 entries, 484 lines** |
| `verify-derived-counts.py` | OK — 7 registered claims all match |
| `verify-workflow-syntax.py` | OK — and it independently reports that *every branch filter selects at least one of the 3 refs that exist*, which is part of why change 5 was withheld |
| Live / retired constraint rows | **80 / 10**, derived |

**Not verified, and it is the honest limit.** The four proposed gates are **not written** — changes 2, 4, 6 and 10 are specifications with a measured target, not code, and each must be proven able to fail before it is wired. `verify-constraint-verifiers.py` currently reports one pre-existing error against `C-TECH-064` (a HARD row reachable only by a manual pipeline step); it is unrelated to this review and wired `--warn-only`. No Pester suite was run, because nothing proposed here touches PowerShell.

---

## 7. Findings left unprocessed

**States excluded, stated so the cap is not silent:** **29 `reviewer-deferred`** (each carrying a reason a human accepted), 0 `awaiting-approval`, 0 `already-fixed`, 0 `approved-not-applied`, and every `APPLIED`/`REJECTED` entry. **All 14 `unread` entries were read in full and all 14 are dispositioned above.**

**One deferred entry still carries no trigger to come back.** [IMP-0274](../../logs/improvement-log.jsonl#L271) has a `deferred_reason` and no `revisit_when`, which the log gate reports as a standing NOTE. Reviews 25 and 26 both left it as out of approved scope; I am leaving it for the same reason and naming it for the third time so it does not go quiet.

**Two entries close on a re-measurement rather than on a change.** [IMP-0299](../../logs/improvement-log.jsonl#L296) and [IMP-0307](../../logs/improvement-log.jsonl#L304) both describe orphan assumption markers that are now **fixed in source** — `verify-assumption-markers.py` passes. Both are `V1`, so the gate run is evidence at the defect's own level. They close on approval with `reobserved` naming this session's run; change 1 is the durable half that stops the next one being found by the build.

**[IMP-0306](../../logs/improvement-log.jsonl#L303) is a capability record, not a defect.** It closes as `APPLIED` on change 7 with `capability: true`, and its two facts are recorded as **E2** — vendor documentation, not observed live here.

---

## 8. Digest impact

**This prediction is deliberately narrow, because the last two were wrong in both directions.** Review 26 predicted `299 → 302` against a base that was actually 304, and named `gate-cannot-fail` classes that none of its findings turned out to belong to. Review 27 was wrong the same way.

Base measured **307**. I expect to append **two** findings at application: the `check_review_status_headers` duplication if change 6 is approved, and whatever change 10's re-measurement turns up when the suite-gate rung is widened to `scripts/` — it will name more than the two scripts it was built on, and some of those will be legitimate exemptions rather than defects. So **307 → 309**, with `declared-policy-not-mechanically-enforced` moving to x11 and `learning-substrate-destroyed` to x23 from the closures rather than from new entries.

**Treat that as an intention, not a measurement.** Both growing classes are already over the 20-lesson display cap, so I expect the line count to stay near 484. I regenerate and report the measured before-and-after on approval, and state where it differs from this prediction rather than letting the prediction stand as the record.

---

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-25-improvement-review-2.md
                              DRAFT — nothing applied

Findings processed: 14 unread  →  8 clusters
Regression check:   7 prior changes audited, 2 classes recurred
                    (both are review 26's own: check_suite_gates_are_steps' stated
                     residual acquired an instance within the hour, and change 6's
                     first form could not reach the file its reader loads)
Proposed:           0 constraints (cap 3), 4 gates/scripts, 5 skill/knowledge edits,
                    2 agent-file edits, 1 constraint amendment, 0 retirements applied
                    (2 reinstatement CANDIDATES named for decision — the first the
                     obligation has produced in four reviews)
Altitude calls:     3 generalised from instance to class (clusters B, D, F),
                    4 left as knowledge/skill lines, 1 declined and put to you (§5.2),
                    1 deferred with a reason (§5.3), 1 scoped rather than repo-wide (§5.6)
Digest:             will regenerate — predicted 307 → 309, will report measured

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 10. Applied — 2026-08-25

`Approve Improvements` received. **All 12 changes are on disk. Nothing was withheld.** Four gates
were written, measured against the real tree, and wired; one function was retired into one of them.

**Two premises were re-verified before applying, per [activation step 8](../../agents/improvement-agent.md#L127), and both held.** The
`corrects` warning the log gate raised — [IMP-0309](../../logs/improvement-log.jsonl) correcting
[IMP-0298](../../logs/improvement-log.jsonl) — turned out to be the *basis* for change 10 rather
than a disproof of anything, and `CO-001-A1` still priced withdrawn scope at application time.

### What landed

| # | Change | Where | Entries closed |
|---|---|---|---|
| 1 | `verify-assumption-markers.py` is now a command the **authoring** session runs at step 8, not a check the build springs one dispatch later | [development-agent.md](../../agents/development-agent.md#L35) | IMP-0299, IMP-0307 |
| 2 | **New gate** — every FR/NFR id a change order prices must exist in the SDD and not be withdrawn. SOFT, `--warn-only` | [verify-change-order-requirements.py](../../scripts/verify-change-order-requirements.py), [build step](../../config/revitalise-grant-automation-build.yml) | IMP-0297 |
| 3 | Data Provenance gained a **third row** for items no table in this solution holds, plus the definition of `non-blocking` | [how-to-write-requirements.md](../../skills/how-to-write-requirements.md#L62) | IMP-0296 |
| 4 | **New gate** — every `ROUTED_TO` after a cutoff is closed by a terminal line. Forward-only, LIFO, SOFT | [verify-routing-reconciliation.py](../../scripts/verify-routing-reconciliation.py) | IMP-0300 |
| 5 | Apply-step bookkeeping is now **incremental**, plus the re-read-the-max-id rule | [improvement-agent.md](../../agents/improvement-agent.md#L152) | IMP-0301 |
| 6 | **New gate** — review-document self-consistency, and `check_review_status_headers()` **retired into it** | [verify-review-document.py](../../scripts/verify-review-document.py) | IMP-0302 |
| 7 | The wrong `power-automate.md` row corrected to `pa app add flow`; the aggregate-FetchXML limit recorded. Both **E2** | [power-automate.md](../../knowledge/technology/power-automate.md#L13) | IMP-0304, IMP-0306 |
| 8 | Privileged compute and **scheduled** compute separated into two questions | [code-apps.md](../../knowledge/technology/code-apps.md#L183) | IMP-0303 |
| 9 | Evidence must come from the artefact that **governs** the claim | [how-to-verify-a-platform-contract.md](../../skills/how-to-verify-a-platform-contract.md#L54) | IMP-0305 |
| 10 | Suite-gate rung **widened** from the Pester suite to `scripts/`; `subagents-current` and `digest-current` wired | [verify-build-config.py](../../scripts/verify-build-config.py#L638) | IMP-0309 |
| 11 | `models.yml` header now states which keys propagate as **values**, and that comments do not | [models.yml](../../config/models.yml#L5) | IMP-0310 |
| 12 | `C-TECH-061` / `C-TECH-063` `Verify By` name **both** enforcement paths — additive, replacing nothing | [technology-constraints.md](../../constraints/technology/technology-constraints.md#L131) | IMP-0308 |

### The four gates were wrong on first contact with real data, and that is the main lesson

**Three of the four passed their own selftests and were still wrong against the repository.** Six
defects, all found by running them, none by the fixtures — logged as
[IMP-0319](../../logs/improvement-log.jsonl):

- `verify-change-order-requirements.py` reported **FR-059** as withdrawn, because FR-059's SDD row
  *cites* NFR-027's withdrawal in prose. A row's own disposition is a **bold** marker; a mention of
  someone else's is not. It also needed a supersession rule, or every superseded change order would
  be reported forever — this project never edits an approved commercial document in place.
- `verify-review-document.py` matched `asks` inside **`tasks`**, read `declined` and `carries` in
  sentences looking *back* at a section, and read `TAD section 9.3` as a dangling self-reference.
  It also, in its first form, **did not fire on the very document `IMP-0302` was logged against**:
  review 27's §5 held four bold questions, just not the promised one, so "does the section ask
  anything?" passed it. Keying on the deferral's **topic** is what makes the check real.
- Worst, `verify-routing-reconciliation.py`'s first FIFO matching reported **0 unreconciled** while
  *masking* the one genuine stall in the log — [IMP-0291](../../logs/improvement-log.jsonl)'s 09:23
  architect-agent dispatch — and flagging a healthy dispatch as in-flight instead. **A false
  negative produced by a plausible rule.** LIFO reports the real stall from the log alone.

**Measured precision, stated so it is on the record rather than an impression:**

| Gate | Result on the real tree |
|---|---|
| `verify-change-order-requirements.py` | 2 findings / 10 priced ids / 2 change orders — NFR-027 `WITHDRAWN`, FR-061 `REWORDED`. 0 false positives |
| `verify-routing-reconciliation.py` | 1 unreconciled (the known stall), 3 in-flight (three genuinely live sessions), 13 closed of 17 in scope; 91 pre-cutoff dispatches out of scope by design |
| `verify-review-document.py` | 1 finding / 33 documents, 0 false positives — after five false-positive classes were eliminated |
| Widened suite-gate rung | 5 scripts named, all 5 resolved: 3 new gates wired, 2 generators wired |

### The retirement, and its coverage proof

`check_review_status_headers()` and its three regexes are **removed** from
`verify-improvement-log.py` (49 lines) and live on as check (c) of `verify-review-document.py`.
`IMP-0204`'s own fixture is preserved in that script's selftest and **still fails** there, which is
the proof [the altitude rule](../../skills/how-to-promote-a-finding.md#L79) demands of a
generalisation. Severity is unchanged — a warning before, a warning now. `IMP-0204`'s
`evidence_grep` needle was **repointed** to the new home, which the log gate caught when it went
stale: the retirement broke a closed entry's evidence, and the gate said so.

### What the widening found beyond its own finding

Change 10 was justified by `generate-subagents.py`. The widened rung also named
**`generate-known-failure-modes.py --check`** — `C-TECH-059` is HARD, names build-agent, and its
only runner was the CI validate job. Now build step `digest-current`. Logged as
[IMP-0318](../../logs/improvement-log.jsonl) and closed on the preflight run, because the general
lesson is worth more than the fix: **when a gate's source of truth is a hand-maintained list, its
coverage is that list's coverage — widening the source beats sharpening the check.**

### Measured before and after, against section 8's prediction

Section 8 predicted `307 → 309`. **Measured: 307 → 316**, and the difference is almost entirely
other sessions, not this review.

| | Predicted | Measured |
|---|---|---|
| Log entries | 309 | **316** — this review appended 2 (IMP-0318, IMP-0319); **7 arrived from four concurrent sessions** while it was being applied |
| Digest lines | ~484 | **486**, 316 distinct lessons |
| Live / retired constraint rows | 80 / 10 | **80 / 10** — unchanged, as predicted; no new rows |
| Build steps / gates | — | **55 / 41**, up from 50 / 38 |

**The prediction was wrong in the direction it is always wrong** — the queue moves underneath the
review. The log grew from 309 to 312 to 316 *during* application, and my own id allocation shifted
from IMP-0316/0317 to IMP-0318/0319 between reading the maximum and appending. That is precisely
why change 5 wrote the re-read rule into activation step 8, and it earned its keep within the hour.

### Findings not processed, and one that is now overtaken

**8 unread entries remain, none of them this review's**: IMP-0311 through IMP-0317 (appended by
frontend-agent, commercial-agent and development-agent sessions running concurrently) and IMP-0319
(this review's own). **29 `reviewer-deferred`** are untouched, and
[IMP-0274](../../logs/improvement-log.jsonl) still carries no `revisit_when` — named for the
**fourth** time so it does not go quiet.

**[IMP-0312](../../logs/improvement-log.jsonl) is a tenth instance of
`declared-policy-not-mechanically-enforced`** — `logs/commercial-events.jsonl` was declared in
`WORKFLOW.md`'s roster and never written by any script, sitting at 0 bytes through three authorised
commercial acts. It arrived after this review's scope was fixed and is left for the next one, but it
is the same class as cluster A and it is now the largest class in the digest.

**Section 5's six questions are all still open.** None was answered by the keyword, and none was
decided here — including the two retirement candidates ([C-TECH-011](../../constraints/technology/technology-constraints.md#L49),
[C-TECH-012](../../constraints/technology/technology-constraints.md#L50)), the `partly-applied`
sixth log state, and the `gh run list` that would settle whether CI has ever fired.

### Verification executed at application

**Level reached: V1.** No live environment was touched; nothing here required one.

| Check | Result |
|---|---|
| `verify-improvement-log.py --check` | **exit 0** — 316 entries, 8 unread, batch trigger clear |
| `verify-improvement-log.py --selftest` | exit 0 — 53 fixtures, after removing 49 lines from it |
| `verify-build-config.py` | **PASS — 55 steps, 41 gates**, widened rung green |
| `verify-review-document.py --selftest` | exit 0 — 8 fixtures |
| `verify-change-order-requirements.py --selftest` | exit 0 — 6 fixtures |
| `verify-routing-reconciliation.py --selftest` | exit 0 — 5 fixtures |
| `generate-subagents.py --check` | exit 0 — 18 files current |
| `generate-known-failure-modes.py --check` | exit 0 — 316 entries, 486 lines |
| `verify-assumption-markers.py` | PASS — 6 OPEN rows, all marked |
| `verify-derived-counts.py` | OK — 7 registered claims match |
| `verify-workflow-syntax.py` (+ `--selftest`) | exit 0 / exit 0 — 9 known-bad fixtures rejected |
| `verify-constraint-verifiers.py --warn-only` | exit 0 — one pre-existing `C-TECH-064` warning, unrelated |
| Pester | **Not run — nothing in this review touches PowerShell.** Stated rather than implied |

**One transient failure worth recording.** The build-config preflight went red once, mid-battery,
and passed on three consecutive re-runs. Cause: a concurrent development-agent session was writing
`verify-flow-definition-language.py` and its build step at the same moment. Both now exist and the
widened rung accepts them — **and had that session added the script without a step, the rung applied
by this review would have caught it.** The gate working on a real, concurrent event within minutes
of being wired.
