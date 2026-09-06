# Improvement Review — 2026-09-04 (2)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 31 unread → 7 clusters
**Trigger:** batch — the queue stood at 31 unread against a threshold of 30, so
`improvement-log-check` was halting the build for the WBS 0.4 applicant-ethnicgroup form fix at
step 3 of 70. Reviewer authorised a dedicated batch review to clear it.
**Gate:** `APPROVE IMPROVEMENTS` — **sent in the dispatch, ahead of this draft.** See §0.
**WBS:** 0.4 (the trigger), 6.8 (the findings' own tasks). The rule changes themselves are system
work, not a contracted deliverable.

**The queue is cleared, and nothing was closed to make the number go down.** All 31 unread entries
are dispositioned: **23 applied**, **8 left open with a recorded reason and a return condition**.
Every one of the eight is open because the evidence that would close it does not exist yet — six
need a human to look at a live screen or an authenticated session, two are routed to the agent that
owns the file. Simulated against a scratch copy before anything moved: `0 unread, 0
awaiting-approval`, so the batch trigger clears.

**One proposal was WITHHELD on evidence, and it is the most important decision in this review.**
[`IMP-0584`](../../logs/improvement-log.jsonl) proposed extending
[`C-TECH-076`](../../constraints/technology/technology-constraints.md#L146) with a symbolic check
over the chart geometry constants. [`IMP-0590`](../../logs/improvement-log.jsonl) — logged
afterwards — disproves it. A real-browser step was wired instead. §4.

---

## 0. The keyword arrived before the draft existed

`agents/improvement-agent.md` step 7 says present the gate and wait; step 8 says apply on the
keyword. Here the keyword was in the dispatch, so there was no draft for it to approve. It was read
as authorisation to apply, because the brief names the outcome it wants
(*"until `verify-improvement-log.py --check` exits 0"*), which is unreachable without applying.

**What that costs you, stated plainly so you can reverse it:** you are reading the changes after
they landed rather than before. The three you would most plausibly want back are the new HARD build
step (§3), the new constraint row (§4), and the correction to `CLAUDE.md`'s own supplied-assets
table (§8). Each is one commit and none is load-bearing for the 0.4 fix.

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [Review 2026-09-04](2026-09-04-improvement-review.md) — [`C-TECH-077`](../../constraints/technology/technology-constraints.md#L147) plus the form-surface check in [`verify-forms-and-views-reachable.py`](../../scripts/verify-forms-and-views-reachable.py) | 2026-09-04 | `no-assertion-on-shipped-content`, schema↔form half | **NO** — no entry since carries the schema↔form shape | **Working.** The gate fired on the pre-fix tree and is green on the corrected one |
| [Review 2026-09-03](2026-09-03-improvement-review.md) — the `blocked_on` freshness window in [`verify-pipeline-config.py`](../../scripts/verify-pipeline-config.py) | 2026-09-03 | `stale-deferral-uncaught-across-sessions` | **NO** | **Working.** Re-run today: exit 0. Its residual is discharged |
| Review 10 — [`verify-code-app-bundle-budget.py`](../../scripts/verify-code-app-bundle-budget.py) | 2026-09-01 | `untriaged-tool-warning` | **YES** — [`IMP-0592`](../../logs/improvement-log.jsonl) | **Gate fired correctly; the finding is elsewhere.** The warning is real and untriaged in *this* feature's Dev Summary, which is a delivery document. Routed, §7 |
| Reviews 1–37 cumulative — the `no-assertion-on-shipped-content` family, **rendered-geometry half** | various, all per-instance | `no-assertion-on-shipped-content` | **YES ×6** | **This is cluster A, and it is a prose-and-per-instance failure of six rounds.** §3 |
| [`IMP-0410`](../../logs/improvement-log.jsonl)'s `tracked_glob()` fix | 2026-08-27 | `gate-scope-mismatch` | **YES** — [`IMP-0591`](../../logs/improvement-log.jsonl) | **Mis-scoped, exactly as the regression row predicts.** Fixed in the one script it was raised against; the next script in the class was undefended. §6 |

**Classes that recurred after a gate, where the gate failed to fire:** one —
[`IMP-0410`](../../logs/improvement-log.jsonl)'s. It did not fail; it was never wired to the second
script. That is the altitude rule's own textbook case and it is fixed at the class this time.

**Classes that recurred after a PROSE change:** the rendered-geometry family, six times. Every one
of the six was found by the reviewer looking at live DEV, never by the suite. The answer is not
more prose, and §3 is a browser.

**Closure evidence audited against `observable_at`:** four entries this review closes are `V4`.
None is closed on a document, a clean build or a zero exit — three carry the reviewer's own
2026-09-03 live confirmation, and the fourth is `V2` closed on a command this review ran. Seven
`V2`+ entries that could **not** be re-observed here are left open rather than closed, §7.

---

## 2. Clusters and promotion decisions

Seven clusters over 31 entries. Three produced durable mechanism, three produced prose at the
altitude the evidence supports, one produced bookkeeping only.

```
CLUSTER A: no-assertion-on-shipped-content, RENDERED GEOMETRY
           (x6: IMP-0566, IMP-0577, IMP-0579, IMP-0581, IMP-0584, IMP-0590)
Altitude:  CLASS — six instances, one property: "a number in source that is supposed to come
           out as a distance on screen". jsdom computes no layout, so the suite is SILENT here
           rather than wrong, and all six were found by a human on live DEV.
Ladder row: "a tool could catch it mechanically" + "second instance -> generalise"
Becomes:   build step `code-app-visual-tests` (real Chromium, the harness already existed and
           ran nowhere) + C-TECH-078 + a five-bullet section in skills/how-to-review-code.md
Retires:   nothing. C-TECH-076 is NOT subsumed — it reads every authored stylesheet statically;
           this step measures two gaps in one component. Neither covers the other.
Withheld:  IMP-0584's proposed symbolic "check C" for C-TECH-076. IMP-0590 disproves it. §4.
Cites:     IMP-0566, IMP-0577, IMP-0579, IMP-0581, IMP-0584, IMP-0590, and IMP-0509 which
           stays open
Measured:  the wired suite exits 0, 2 passed in 3.5s, and verify-build-config.py exits 0 with
           the step in place. CAN-IT-FAIL is second-hand: IMP-0590's own stash-and-rerun
           (-4px, two sessions). This review's attempt to reproduce it was REFUSED by the
           harness and not routed around. §4.
Residual:  two gaps on ONE component. Every other rendered geometry in the app is undefended,
           and a green step must not be read as "the layout is correct". V2 evidence only —
           it never discharges the named-human V4 step, which is why IMP-0509 is still open.
```

```
CLUSTER B: finding-diagnosis-unverified / stale claim about a tracked file
           (x6: IMP-0549, IMP-0550, IMP-0551, IMP-0562, IMP-0570, IMP-0571)
Altitude:  CLASS at the THIRD instance, which is the threshold IMP-0571 itself named
Ladder row: "an agent had the information and still did the wrong thing" -> agent-file edit
Becomes:   a paragraph in agents/improvement-agent.md step 8 extending "assertions about
           BEHAVIOUR must be executed" to "assertions about the CURRENT STATE OF A TRACKED
           FILE must be grepped"
Retires:   nothing
Cites:     IMP-0549, IMP-0570, IMP-0571 (IMP-0550, IMP-0551, IMP-0562 are the same discipline
           working — each was caught by step 8 as written)
Residual:  no gate can read a finding's proposed_change or a review's rationale prose, and
           none reasonably could. This clause is the only control. It is prose by necessity,
           not by preference.
Note:      the new clause paid for itself inside this review. §8.
```

```
CLUSTER C: declared-policy-not-mechanically-enforced (x2: IMP-0567, IMP-0572)
Altitude:  INSTANCE each — two unrelated subjects that happen to share a class name
Ladder row: "an agent had the information and still did the wrong thing"
Becomes:   skills/accessibility-checklist.md gains a conflict route (IMP-0567);
           agents/improvement-agent.md gains the two closure field shapes inline (IMP-0572)
Retires:   nothing
Residual:  neither is gateable. No gate reads a reviewer instruction — a dispatch instruction
           is a Task-tool prompt, never a file (IMP-0470) — and the log validator already
           enforces the field shapes correctly. Both gaps were DISCOVERABILITY, not
           enforcement.
```

```
CLUSTER D: stale-claim-contradicting-rechecked-source (x3: IMP-0575, IMP-0594, IMP-0596)
Altitude:  one template edit, one routed, one bookkeeping
Ladder row: "the ORDER of steps was wrong" -> templates/deployment-summary-template.md
Becomes:   the Environment Results table now asks for a live `pac solution list` per
           environment the feature could have reached, and distinguishes "not queried" from
           "not attempted" (IMP-0596). IMP-0594 is executed as bookkeeping, §5. IMP-0575 is
           three prose surfaces in delivery files — routed, §7.
Retires:   nothing
Residual:  the template prompts; nothing enforces it. A gate would need to query three live
           environments at document-write time.
```

```
CLUSTER E: identifier-namespace-collision-across-documents (x1: IMP-0576)
Altitude:  CLASS on one instance, and the reason for skipping ahead is COMMERCIAL — the WBS
           task id is the join key between a dispatch, a commit and an invoice
Ladder row: "a tool could catch it mechanically"
Becomes:   check 2 in scripts/verify-routing-reconciliation.py — an already-wired SOFT build
           step that already reads logs/routing.log and already has a reviewer-set cutoff
Retires:   nothing
Cites:     IMP-0576
Measured:  1 finding across 71 in-scope tags / 2 distinct ids — 1 true positive, 0 false.
           Selftest extended from 5 to 8 fixtures, exits 0. Under --warn-only, as the build
           invokes it, exit 0.
Residual:  8 COMMIT MESSAGES carry the same bad tag and git history is not editable, so
           commits are deliberately out of scope — a gate over them would open red on work no
           dispatch can close. The cutoff keeps the log half honest: pre-cutoff lines are
           history, and 52 of the 95 bad lines are.
```

```
CLUSTER F: gate-scope-mismatch (x2: IMP-0591, IMP-0595)
Altitude:  IMP-0591 -> the class fix IMP-0410 should have had. IMP-0595 -> deferred, §7.
Ladder row: "second instance of the same class -> generalise"
Becomes:   scripts/verify-source-derived-test-counts.py resolves its
           provisioning/deploymentSettings/*.json glob through tracked_glob()
Retires:   nothing
Cites:     IMP-0591, IMP-0410
Measured:  --selftest exit 0 (17 fixtures), real run exit 0, and
           verify-gate-input-tracking.py now lists the script as declaring its own handling.
Residual:  the gitleaks half is NOT fixed. `secret-scan` runs `gitleaks detect --source .
           --no-git`, which cannot be routed through tracked_glob() because the scope is
           gitleaks' own. An interrupted Pester run leaving provisioning/certs/*.pem behind
           still halts a build. A file-level Pester AfterAll cleanup is the remedy and it is
           delivery work in src/tests/build/ — named, not written here.
```

```
CLUSTER G: notes and one-offs, no rule change
           (x11: IMP-0552, IMP-0563, IMP-0578, IMP-0580, IMP-0583, IMP-0586, IMP-0587,
            IMP-0589, IMP-0592, IMP-0593, IMP-0600)
Altitude:  INSTANCE. Two produced knowledge lines (a platform law each), one a skill line,
           one an agent-file clause, one a registry re-anchor, and the rest are recorded.
Ladder row: "one instance, but the cause is general and a human needs to know it"
Becomes:   knowledge/technology/coding-standards.md (IMP-0589, PowerShell output streams);
           knowledge/technology/build-and-deploy.md (IMP-0593, pac org fetch omitting a live
           row); skills/how-to-write-a-test-plan.md (IMP-0580, an untested optional prop);
           agents/improvement-agent.md (IMP-0586, credential boundary per operation);
           scripts/derived-counts-registry.json (IMP-0600, re-anchored)
Retires:   nothing in constraints/. §9.
Residual:  IMP-0587's proposed gate is deliberately unbuilt — it is the phrase-based
           instrument this project has measured at 48-100% false five times. §7.
```

---

## 3. Cluster A — the mechanism existed and ran nowhere

**Six rounds of one symptom on one file, and the fix for round four wrote the test that would have
caught rounds one to three.** The `IMP-0590` dispatch authored
[`playwright.config.ts`](../../src/code-apps/trustee-review-portal/playwright.config.ts#L19) and
[`round-statistics-charts.visual.spec.ts`](../../src/code-apps/trustee-review-portal/src/test/visual/round-statistics-charts.visual.spec.ts#L42),
proved them against real Chromium — and wired them into nothing. The config's own docstring says
so: *"CI wiring: add the same script as a step after `npm test`."* So does the Deployment Summary:
*"The Playwright visual-regression spec also remains un-wired … known gap, not this dispatch's to
close."*

That is `gate-cannot-fail` in its milder form — a check that exists and is invoked by no config —
and it is the one thing in this batch where a durable mechanism was already paid for and simply
not connected.

Wired as [build step `code-app-visual-tests`](../../config/revitalise-grant-automation-build.yml#L631),
immediately after `code-app-unit-tests`, HARD. The browser install is in the step command on
purpose: leaving it to the workflow is how a step acquires an undeclared dependency that passes
locally and fails on a fresh runner. The step's first token is `npm`, already in
`required_tools`, so nothing else changes.

**Executed, not read:** `test:visual:install` exit 0, `test:visual` exit 0, **2 passed in 3.5 s**,
`verify-build-config.py` exit 0 with the step in place.

---

## 4. The withheld proposal — and why the tell matters

[`IMP-0584`](../../logs/improvement-log.jsonl) asked for a **symbolic** check: read
`AXIS_LABEL_GAP`, `TICK_ASCENT_PX` and `FIRST_TICK_LINE_DY` and assert the derived gap. It is a
reasonable proposal, it fits `C-TECH-076`'s existing shape, and it would have been cheap.

[`IMP-0590`](../../logs/improvement-log.jsonl) proves it would have **passed on the defective
tree**. `FIRST_TICK_LINE_DY`'s value was correct. The defect was that the value sat on a `<text>`
element whose child `<tspan>` declared its own `dy`, and SVG's composition rule silently discards
the parent's — an intended `+27 px` gap rendered as `-4 px`. No check that reads values rather than
rendering them can tell those two trees apart.

So it is **withheld**, not deferred: the premise failed, and applying a check whose premise you
have just watched fail is what [`IMP-0275`](../../logs/improvement-log.jsonl) forbids. It is
recorded as withheld in `IMP-0584`'s own `applied_by`, in
[`C-TECH-078`](../../constraints/technology/technology-constraints.md#L148)'s Rationale, and here.

**And this review's own can-it-fail evidence is second-hand, which is stated rather than
smoothed over.** The negative control is `IMP-0590`'s: the fix hunk stashed, the spec re-run, both
assertions failing at exactly `-4 px`, independently reproduced by two sessions. This review tried
to re-run it and the **harness refused the source mutation**. That refusal was not routed around —
`skills/how-to-promote-a-finding.md` §4 forbids it, and the operation was out of this review's
scope besides. The level actually reached is therefore *green-on-the-corrected-tree, verified here*
plus *red-on-the-defective-tree, recorded by another agent*, and `C-TECH-078` says so in its own
Verify By cell.

---

## 5. Cluster D bookkeeping — what the reviewer's confirmation does and does not close

[`IMP-0594`](../../logs/improvement-log.jsonl) is a finding whose entire content is *"do not
over-close on this evidence"*, and it was right.

The dispatch that logged it was asked to close four ids on the reviewer's 2026-09-03 live
confirmation (*"its good now"*). Three describe the same symptom — chart x-axis category-label
geometry — and one, [`IMP-0509`](../../logs/improvement-log.jsonl), describes a **different** one:
a stat-tile currency-value overlap in a different component, carried into the same "x-axis overlap"
narrative by three successive pipeline log entries and a deployment summary.

Closed on that confirmation: `IMP-0577`, `IMP-0581`, `IMP-0590` at `V4`, plus `IMP-0584` at `V2`
on this review's own green run of the spec it asked for. **`IMP-0509` is left open**, unchanged,
with its original `revisit_when` intact. Its symptom has still never been re-checked.

---

## 6. Elements added and changed

| Added | What |
|---|---|
| [`C-TECH-078`](../../constraints/technology/technology-constraints.md#L148) | HARD. Rendered geometry is proven in a real browser — not by a comment, a jsdom test, or a symbolic relation between declared constants |
| [build step `code-app-visual-tests`](../../config/revitalise-grant-automation-build.yml#L631) | Runs the real-Chromium harness that previously ran nowhere |
| [check 2 in `verify-routing-reconciliation.py`](../../scripts/verify-routing-reconciliation.py#L90) | Every `wbs:` tag on or after the cutoff resolves to a task in `contract/wbs.json` |
| [`designsystem-tracked-file-count`](../../scripts/derived-counts-registry.json#L110) | Registry row so `CLAUDE.md`'s tracked-file figure cannot drift silently again |

| Changed | What |
|---|---|
| [`agents/improvement-agent.md`](../../agents/improvement-agent.md) | Three clauses: grep assertions about tracked-file state; the two closure field shapes inline; the credential boundary is per **operation**, not per file |
| [`skills/how-to-review-code.md`](../../skills/how-to-review-code.md#L52) | Rendered geometry is a platform contract — five checks, each naming its instance |
| [`skills/accessibility-checklist.md`](../../skills/accessibility-checklist.md#L160) | A route for a customer instruction that conflicts with a success criterion |
| [`skills/how-to-write-a-test-plan.md`](../../skills/how-to-write-a-test-plan.md#L82) | An optional prop or slot that no test supplies is an untested branch |
| [`knowledge/technology/coding-standards.md`](../../knowledge/technology/coding-standards.md#L124) | A PowerShell helper that prints must never be captured by an assignment |
| [`knowledge/technology/build-and-deploy.md`](../../knowledge/technology/build-and-deploy.md#L214) | An unfiltered `importjob` query can omit a live row with no error |
| [`scripts/verify-source-derived-test-counts.py`](../../scripts/verify-source-derived-test-counts.py#L96) | Its settings glob resolves through `tracked_glob()` |
| [`scripts/generate-known-failure-modes.py`](../../scripts/generate-known-failure-modes.py#L45) | The registered line count is now a separate, undated, rewritable sentence |
| [`templates/deployment-summary-template.md`](../../templates/deployment-summary-template.md#L9) | Query the environments you are **not** deploying to |
| [`CLAUDE.md`](../../CLAUDE.md#L262) | Two of four rows in the supplied-assets table were false. §8 |

---

## 7. What is still open, and why each one is honestly open

Eight entries stay `NEW` with a `deferred_reason` and a `revisit_when`. None is a closure in
disguise; six are blocked on an observation nobody here can make, two are routed.

**Three shipped fixes with no confirmation of their own symptom.** `IMP-0566` (two filter controls
rendering ~4 px apart), `IMP-0579` (a pie chart overflowing the page) and `IMP-0580` (a duplicate
chart under a toggle) are all `V3`/`V4` and all fixed in code. The 2026-09-03 confirmation was
scoped to the chart x-axis, and stretching it across differently-named symptoms is precisely what
`IMP-0594` exists to prevent. Each returns when a reviewer looks at that specific screen.

**Two need a session this one does not have.** `IMP-0593`'s knowledge line is applied, but
re-observing an unfiltered `pac org fetch` omitting a live row needs an authenticated session
against DEV. `IMP-0575`'s three prose surfaces sit in `docs/architecture/` and `src/`, owned by
architect-agent and development-agent.

**Two gates deliberately unbuilt.** `IMP-0587`'s environment-name check is the phrase-based
instrument this project has measured at 48–100 % false five times, and the file it would read
legitimately retains withdrawn wording in comments — it needs a corpus measurement first, which is
outside a batch review. `IMP-0595`'s cross-environment `post_deploy` check would open a HARD build
preflight red on a gap that was routed to development-agent yesterday and has not had time to be
closed.

**One routed delivery row.** `IMP-0592` needs a `§11` row in this feature's own Dev Summary.

### Routed work — re-measured before handing on

| To | What | Re-measured today |
|---|---|---|
| development-agent | `seed-round-statistics-request.ps1` / `-result.ps1` as `tst_acc`/`prd` `post_deploy` steps | **Still open.** Already handed over in [`logs/pipeline.log`](../../logs/pipeline.log) at 2026-09-04 08:10, so this is a confirmation, not a second dispatch |
| development-agent | The `field-security-coverage` standing 2-item warning needs a row in `trustee-portal-visual-refresh-dev-summary.md` §11 | **Still open** |
| development-agent | Two `roundStatistics` comments still call `null` *"the shipping default"* | **Still open** |
| architect-agent | `OQ-042`'s three rows still record the unseeded value as the approved default | **Still open** |
| development-agent | A file-level Pester `AfterAll` so an interrupted run cannot leave `provisioning/certs/*.pem` behind | **Still open.** The stray fixtures are gone from the tree today, so this is latent, not live |
| the WBS 0.4 dispatch | 5 of the 6 SOFT derived-count drifts are that fix's own sources | **Re-measured, §8** |

**Withheld from routing:** nothing. Every row above was re-checked against the tree today and none
had become a shipped fix, a closed decision or a superseded diagnosis.

---

## 8. Two measurements this review made that its findings had not

**`IMP-0600`'s adjudication, done one drift at a time as it asked.** The SOFT
`derived-counts` step has been reporting an aggregate for two reviews running, and an aggregate
that is never zero is one nobody reads. Read individually: **one** row was a category error — it
anchored on a *dated* sentence, so it could never go green without making that sentence false — and
it is re-anchored. The other **five** are real drifts in three files, all consequences of work in
flight: the secured-column count moving 67 → 68 and the role header 51 → 52 (the WBS 0.4
ethnic-group fix's own sources, explicitly out of this review's scope) and the `rev_setting` row
count 15 → 16 (yesterday's TST/ACC seeding). Each belongs to the dispatch that moved its source.
The step now reports **5**, and every one has a named owner.

**Cluster B's new clause paid for itself immediately, on the very finding that justified it.**
`IMP-0549` reported one row of `CLAUDE.md`'s supplied-assets table false — *"Tracked? No. 0 tracked
files"* against a measured 131. Re-measuring **all four** rows, as the clause now requires,
found a **second** false one: *"Read by any build step? No. No `config/*.yml` step, workflow or
script references it"* — when the wired HARD step `design-source-coverage` runs
[`verify-design-source-coverage.py`](../../scripts/verify-design-source-coverage.py), which reads
that directory. Both rows are corrected.

And the paragraph immediately below that table was itself a correction of `IMP-0384`, asserting the
directory *"is not tracked"* — so the erratum had gone stale as well. That is now the block's
stated lesson: a supplied artefact's status is a measurement with a date on it, and two of these
four answers changed within seven days of being verified.

---

## 9. Retirement — checked, and none warranted

Derived at application time, never retyped:

```
grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l   →  10 retired
grep -rh '^| C-'   constraints/ --include='*.md' | wc -l   →  85 live (84 before C-TECH-078)
ls scripts/verify-*.py | wc -l                             →  57 unchanged — no new script
```

**The candidate considered was [`C-TECH-076`](../../constraints/technology/technology-constraints.md#L146),
and it stays.** `C-TECH-078` does not subsume it: `C-TECH-076` reads every authored stylesheet in
the app statically, without a browser, and catches a bad declaration at the commit that writes it.
`C-TECH-078` measures two gaps in one rendered component. Retiring the static gate because a
narrower dynamic one now exists would lose coverage, which is a regression and not a promotion.

The retirement made instead is a **registry row's anchor**, not a constraint: no rule was removed,
so the live count moves by exactly the one row added.

---

## 10. Applied record

| Entry | Status | Where it landed |
|---|---|---|
| `IMP-0549` | APPLIED | `CLAUDE.md` two rows corrected + `designsystem-tracked-file-count` registered |
| `IMP-0550`, `IMP-0551`, `IMP-0562` | APPLIED | No rule change needed — each was step 8 working. Recorded as cluster B corroboration |
| `IMP-0552`, `IMP-0563`, `IMP-0578`, `IMP-0583` | APPLIED | No rule change. Recorded as class markers; §2 cluster G |
| `IMP-0566`, `IMP-0579`, `IMP-0580` | **open** | Fixes shipped; no confirmation of their own symptom. §7 |
| `IMP-0567` | APPLIED | `skills/accessibility-checklist.md` conflict route |
| `IMP-0570`, `IMP-0571` | APPLIED | `agents/improvement-agent.md` step-8 grep clause |
| `IMP-0572` | APPLIED | `agents/improvement-agent.md` inline field shapes |
| `IMP-0575`, `IMP-0592` | **open** | Routed to architect-agent / development-agent. §7 |
| `IMP-0576` | APPLIED | `verify-routing-reconciliation.py` check 2 |
| `IMP-0577`, `IMP-0581`, `IMP-0590` | APPLIED | Build step + `C-TECH-078` + review-code clause; closed at `V4` on the reviewer's confirmation |
| `IMP-0584` | APPLIED | Same, and **its own symbolic proposal withheld**. §4 |
| `IMP-0586` | APPLIED | `agents/improvement-agent.md` credential-boundary clause |
| `IMP-0587`, `IMP-0595` | **open** | Gates deliberately unbuilt. §7 |
| `IMP-0589` | APPLIED | `knowledge/technology/coding-standards.md`; closed at `V2` on a Pester run |
| `IMP-0591` | APPLIED | `verify-source-derived-test-counts.py` via `tracked_glob()`; closed at `V2` |
| `IMP-0593` | **open** | Knowledge line applied; `V3` re-observation needs a live session. §7 |
| `IMP-0594` | APPLIED | Executed as bookkeeping. §5 |
| `IMP-0596` | APPLIED | `templates/deployment-summary-template.md`; closed at `V3` on pipeline-agent's live query |
| `IMP-0600` | APPLIED | Registry row re-anchored; the other five drifts adjudicated. §8 |

**No narrowing at application time**, other than the one withholding in §4 and cluster E's home
(`verify-routing-reconciliation.py` rather than the `verify-wbs-chain.py` the finding named — a
better home, stated in the code's own comment, and it needed no new script or build step).

---

## 11. Findings logged by this review

Recorded during application, not processed here — a review does not adjudicate its own findings in
the same pass.

**One: [`IMP-0601`](../../logs/improvement-log.jsonl), `friction`.** `C-TECH-078`'s `Verify By`
cell, as first authored, named the new harness as `playwright.config.ts` and `src/test/visual/` —
paths relative to the Code App subproject, not to the repository root, where a constraint row is
actually read from.
[`verify-constraint-verifiers.py`](../../scripts/verify-constraint-verifiers.py) went red
immediately, naming the row, the path and the reason, and both were corrected to their full
repo-relative form. Proposal is *no change*: first instance, and the gate detects it exactly.

The near-miss is the part worth keeping. The same change wired the build step with the **correct**
full path, so the mechanism worked and only its documentation was wrong — which would have read as
verified to anyone who checked the step instead of the row.

Two things were **not** logged, and here is why. `CLAUDE.md`'s second false row is `IMP-0549`'s own
class measured properly rather than a new defect, and the five remaining derived-count drifts are
`IMP-0600`'s own request carried out. The harness refusal at §4 is a control working as designed.

**Also worth your attention: the log validator caught two defects in `IMP-0601` itself** — three
missing required fields, and then a `reviewed_in` stamp naming this document, which would have made
a finding this review *wrote* read as one it had *processed* and left it unreachable by any keyword.
Both were fixed before the digest was regenerated. That is the validator-first rule working, and it
is the second time in this review that running a check beat reading one.
