# Improvement Review — 2026-08-19 (second)

**Agent:** improvement-agent · **Tier:** strategic
**Trigger:** two `blocker` entries appended (`IMP-0071`, `IMP-0072`) — `agents/WORKFLOW.md` →
Processing triggers requires immediate processing, not batching. `scripts/verify-improvement-log.py
--check` failed on exactly this and named the rule.
**Queue:** 20 `NEW` entries in 15 clusters.
**Status:** **APPLIED** 2026-08-19 on `APPROVE IMPROVEMENTS`. 16 of 20 entries closed; 4 deferred
with reasons and return triggers.

This is the second review dated 2026-08-19. The first ran before the project-management capability
was built; five of its deferrals were explicitly conditional on that work landing, and it has now
landed on branch `project-management`. That is why a second review the same day is not churn.

---

## 1. Regression check — did the previous review's changes work?

| Class it addressed | What it applied | Recurrence since | Verdict |
|---|---|---|---|
| `platform-field-length-limit-unenforced` | `C-TECH-060` + one schema-driven gate, two instance gates retired | none | **Worked.** Third instance never arrived |
| `gate-cannot-fail` (x13) | `verify-pipeline-config.py`, `verify-improvement-log.py`, the `UNEVALUABLE` outcome | `IMP-0041` — one new instance | **Partially worked.** See below |
| `no-assertion-on-shipped-content` | `verify-shipped-content.py`, checks 1 and 2 | none | **Worked**, and it closes two of this queue's entries |
| `output-shape-defeats-the-reader` | `skills/how-to-report-to-the-reviewer.md` | **`IMP-0070` — recurred the same day** | **Failed.** See below |

### The failure worth stating in full

`IMP-0059` established `skills/how-to-report-to-the-reviewer.md` on 2026-08-19 after three rejected
drafts of one report. Later the same day a long report was written back to the reviewer without
loading it, in the wrong section order, with no clickable line-links. The reviewer asked why.

The previous review's fix was **prose**: a rule written into `CLAUDE.md` and a skill file. Per
`agents/improvement-agent.md` → The Regression Check, *"a recurrence after a prose change is evidence
the fix was at the wrong altitude"*. It is. The skill is named in `CLAUDE.md` under Reporting Rules
and appears in **no agent's activation sequence**, and no gate checks a report's shape. It depended on
an agent remembering a rule at the end of a long session — structurally identical to the WBS
`Actual Hours` column depending on someone remembering at month end (`IMP-0032`).

This review therefore escalates it from prose to **step order**, which is the ladder row that fits:
*"the order of steps was wrong."*

### `gate-cannot-fail` at x13, and why no new gate is proposed for it

`IMP-0041` is a thirteenth instance: the `auth` build step cannot run outside GitHub Actions, so
locally it is skipped, and a skipped step is indistinguishable from a passing one. Closing it needs a
`when: ci` / `when: always` condition in the build-config schema plus preflight support — a change to
the config contract, not another gate. Deferred with that reason, unchanged from the last review. The
class count is the argument for doing it, not for doing something cheaper.

---

## 2. Clusters and promotion decisions

### CLUSTER: the five deferrals conditional on the PM capability
```
Entries:    IMP-0028, IMP-0029, IMP-0030, IMP-0031, IMP-0032
Altitude:   already decided — each was deferred with "deferred to the PM capability review"
Ladder row: "a tool could catch it mechanically" — all five now have one
Becomes:    APPLIED. The capability shipped on branch project-management:
              IMP-0028 → skills/how-to-intake-external-documents.md gains a Commercial Baseline
                         checklist; pm-agent owns BASELINE INTAKE
              IMP-0029 → scripts/import-baseline.py generates the baseline; C-COM-008 forbids
                         restating it; report-baseline-drift.py §3 finds stale figures and found
                         three in the approved SDD
              IMP-0030 → scripts/derive-wbs-state.py + verify-wbs-chain.py; C-COM-005
              IMP-0031 → scripts/wbs-ready-set.py + schedule-risk.py; lead-agent resolves a request
                         to WBS ids before routing; C-COM-002
              IMP-0032 → logs/worklog.jsonl + verify-worklog.py; development-agent proposes actuals
                         while it still knows them
Retires:    nothing — none of these had an instance gate to replace
Residual:   IMP-0031's root cause is CORRECTED by IMP-0069, not merely closed. The build order was
            not set by conversation alone: all of Phase 1 is blocked on the Client. The fix stands,
            but a queue does not unblock a phase waiting on a DocuSign licence.
```

### CLUSTER: `output-shape-defeats-the-reader` — x2, second instance
```
Entries:    IMP-0059 (applied), IMP-0070 (new)
Altitude:   CLASS. Second instance, and the first fix was prose that was then ignored
Ladder row: "the order of steps was wrong" → an activation-order fix
Becomes:    Every agent that writes a gate output gains an explicit numbered activation step:
              "Load skills/how-to-report-to-the-reviewer.md before writing any output the reviewer
               reads."
            Not a new rule — the same rule, moved from something to remember into something to
            execute. Nine agent files: lead, plan, architect, development, test, build, pipeline,
            improvement, and the three PM agents.
Retires:    nothing. The CLAUDE.md rule stays; it is now backed by a step
Residual:   Still not mechanically checked. A verify-report-shape.py could grep a draft for bare
            code-span identifiers and a missing Summary heading, but a report is not a file in the
            repo — it is a chat message, and nothing can gate that. This is the honest limit: the
            step makes the skill loaded, it cannot make it followed. If a third instance occurs, the
            answer is a checklist emitted INTO the gate block, where the reviewer can see it was run.
```

### CLUSTER: `acceptance-happens-without-anyone-recording-it` — x1, blocker
```
Entries:    IMP-0072
Altitude:   CONSTRAINT AMENDMENT, skipping ahead. §4 of the promotion skill permits skipping the
            "wait for a second instance" rule when severity is blocker AND the mechanism is a law.
            Build Terms B5 is a contract law, and the existing constraint is WRONG as written
Ladder row: "an agent had the information and still did the wrong thing" — except it did not have
            the information: the clause text was not in the repository until today
Becomes:    C-COM-006 is AMENDED, not supplemented. Its current text says V6 "is recorded only from
            an explicit dated CLIENT ACCEPTED input naming the person who accepted". B5 says a phase
            is also accepted after ten business days of silence following submission, and by putting
            a deliverable into live operational use. Both start a 60-day warranty window with nobody
            recording anything.
              scripts/warranty-clock.py  — already reads three routes and reports the EARLIEST as
                                           operative (done in this session)
              templates/phase-acceptance-template.md — gains "Submitted for acceptance:" and
                                           "In live use since:"
              agents/acceptance-agent.md — the V6 section is rewritten
Retires:    nothing
Residual:   The system cannot detect live operational use. It can record a date a human supplies.
            Which deliverables Revitalise is actually using today is unknown and is a question for
            the reviewer, not a gap a script can close.
```

### CLUSTER: `incorporated-document-version-mismatch` — x1, blocker
```
Entries:    IMP-0071
Altitude:   SCRIPT — already mechanical, and cheaper than a constraint
Ladder row: "a tool could catch it mechanically"
Becomes:    scripts/import-baseline.py → warranty_block() computes the version match and surfaces
            open_issue in contract/service-agreement.json. Done in this session.
Retires:    nothing
Residual:   The wrong revision cannot be corrected from this repository. General Terms v1.3 (August
            2026) has to be supplied. Until then nothing may compute against a General Terms clause
            — payment terms, IP, confidentiality, termination. The Build Terms, which carry every
            warranty and liability clause this system uses, match exactly.
```

### CLUSTER: `no-assertion-on-shipped-content` — x5, two closable
```
Entries:    IMP-0008, IMP-0015, IMP-0052 (all NEW), plus two APPLIED
Altitude:   already generalised by the previous review
Becomes:    IMP-0008 → APPLIED, covered by verify-shipped-content.py check 2 (dangling column
                       references in shipped prose)
            IMP-0052 → APPLIED, covered by check 1 (navigability: an entity shipping forms or views
                       must appear as a SubArea)
            IMP-0015 → STAYS OPEN. The script declares it NOT_YET_IMPLEMENTED with a real reason: it
                       needs a rule for which text wins when a form label and the column's own
                       displayname legitimately differ, and that is a decision, not a lookup
Retires:    nothing
Residual:   IMP-0015 is the only member of a x5 class still uncovered, and it is blocked on one
            decision. It is in §6 as a question rather than deferred silently.
```

### CLUSTER: fixed at the point of discovery
```
Entries:    IMP-0066 (unquoted artefact), IMP-0067 (evidence rule passed on a forward reference),
            IMP-0069 (schedule double-counted capacity)
Altitude:   NOTHING — one instance each, cause is general, and the lesson is already in the digest
Ladder row: "one instance, but the cause is general and a human needs to know it"
Becomes:    APPLIED with no further change. All three were found and fixed in the same session:
            IMP-0066 recorded as EX-002 with an owner and an expiry; IMP-0067 fixed by tightening
            three evidence rules; IMP-0069 fixed by making headroom cumulative.
Retires:    nothing
Residual:   IMP-0067 is the interesting one — it is gate-cannot-fail inside the evidence map, caught
            on the map's first run against real data. If a second instance appears, the pairing rule
            ("every grep needs an existence check beside it") earns a constraint row. Not yet.
```

### CLUSTER: `platform-contract-guessed-not-groundtruthed` — a capability, not a defect
```
Entries:    IMP-0068
Altitude:   CAPABILITY line in the digest
Becomes:    APPLIED. It also removes IMP-0063's premise: that finding recorded the contracted total
            as unverifiable because "this machine has no PDF text extractor", and recommended
            installing poppler. The format was always readable — a PDF carries a /ToUnicode CMap per
            font. scripts/lib/pmsources.py reads it, and the agreement's 292 hours are verified two
            independent ways.
            IMP-0063 → APPLIED, closed by IMP-0068.
Retires:    nothing
Residual:   none. The same module reads .xlsx and .docx, so no contractual source in this project
            needs a third-party package.
```

### Deferred again, with reasons

| Entry | Class | Why it stays open |
|---|---|---|
| `IMP-0005`, `IMP-0039` | `test-coupled-to-absolute-counts` (x2) | The altitude rule binds: the second instance may not get another instance patch, so the fix is to derive counts from source across the whole Pester suite. That is a substantial change to roughly a dozen assertions and it is not PM work. Sized, not started |
| `IMP-0015` | `no-assertion-on-shipped-content` | Blocked on one decision — see §6 |
| `IMP-0019` | `exit-zero-does-not-mean-created` | Blocked on `IMP-0021`: the cleanup needs `DeleteOptionValue`, which this session's safety classifier refuses. Needs the reviewer in the maker portal |
| `IMP-0041` | `gate-cannot-fail` (x13) | Needs a `when: ci` condition in the build-config schema plus preflight support |

---

## 3. Proposed changes (as drafted — see §6 for what was applied)

| # | Change | Files | Cites |
|---|---|---|---|
| 1 | Load the reporting skill as an activation **step**, not a remembered rule | 12 agent files | `IMP-0059`, `IMP-0070` |
| 2 | Amend `C-COM-006`: V6 is the **earliest of three acceptance routes**, not only an explicit act | `constraints/commercial/commercial-constraints.md` | `IMP-0072` |
| 3 | Acceptance template gains `Submitted for acceptance:` and `In live use since:` | `templates/phase-acceptance-template.md` | `IMP-0072` |
| 4 | Rewrite `acceptance-agent`'s V6 section against the clause text | `agents/acceptance-agent.md` | `IMP-0072` |
| 5 | Move 12 entries to `APPLIED`, 4 stay deferred with reasons, 4 blocked on decisions | `logs/improvement-log.jsonl` | — |

**Zero new constraints.** One amendment to an existing row. The cap is three per review; this review
proposes an amendment because `C-COM-006` is not incomplete, it is **wrong**, and adding a second row
beside a wrong one is how a rule set becomes unreadable.

---

## 4. Retirement

`skills/how-to-promote-a-finding.md` §3.3 requires naming a candidate or stating that none was found.

**Candidate: `C-COM-010`.** It requires an accepted gate exception to carry an owner, a clearing
action and a dated expiry. Both live exceptions had a clearing action of *"WBS v0.6 restates it"* —
and the reviewer confirmed today that no v0.6 will be issued, so both actions were unachievable from
the moment they were written. `C-COM-010` caught nothing, because it checks that the fields are
**present**, not that the action is **possible**.

**Recommendation: do not retire it — strengthen it in a later review.** It is one day old and its
first real test found a genuine gap in itself, which is evidence it is in the right place. The
strengthening is to require that a clearing action name something within the writer's own control.
Recorded here so the next review does not have to rediscover it.

---

## 5. Digest impact

| | Before | After |
|---|---|---|
| Entries | 72 | 72 |
| `NEW` | 20 | **4** |
| `APPLIED` | 52 | **68** |
| Recurring classes | 8 | 8 |
| Unrouted classes | 0 | 0 |

Three classes are new to the routing table and already declared: `unquoted-artefact`,
`evidence-rule-satisfied-by-a-forward-reference`, `gate-reassures-wrongly`. Two more need adding with
this review: `incorporated-document-version-mismatch` and
`acceptance-happens-without-anyone-recording-it`, both under *"Before you bill an hour, accept a
phase, or report status"*.

---

## 6. Applied — and what the reviewer answered while it was open

All four questions §7 raised were answered before the review was applied, so three of them changed
what got built rather than staying open.

| Question | Answer | Effect |
|---|---|---|
| Which text wins on a form label? | *"The column name should be leading, but can be altered if necessary."* | Check 3 implemented: a difference is permitted and must be **declared**. `IMP-0015` closed after three reviews |
| Do the 20 DocuSign hours sit inside the 64? | *"The DocuSign hours sit in those hours."* | `WL-0002` double-counted. Superseded by `WL-0003`, a correction entry — the ledger is append-only, so the over-count stays visible and is excluded from every total. Invoiced to date is **64**, not 84 |
| Which deliverables are in live operational use? | *"Revitalise is not using anything yet. It's in development."* | B5 route 3 has not fired. No warranty window has started for anything |
| General Terms version | v1.3 uploaded, v1.2 removed | `IMP-0071` closed clean rather than as a contract defect |

### The distinction this review nearly missed

The reviewer also said: *"I want them to start testing at the end of the week with what's been created
so far for Phase 2."*

Under B5, **submitting a phase for acceptance** starts a ten-business-day clock after which silence
accepts it. Handing work over to be tested is *not* a submission — but nothing in the system
distinguished the two, and recording this week's Phase 2 test as a submission would have accepted
Phase 2 by default in mid-September, with no-one deciding to.

`contract/acceptance/README.md` records the distinction, and
`contract/delivery-parameters.json` → `testing_and_acceptance` carries the position: this week is a
**V4 review**, `Submitted for acceptance:` stays unset, and acceptance follows testing in the
acceptance environment. That environment is `tst_acc` (TAD ADR-006), and nothing has been promoted
beyond DEV — promotion is a manual Pipelines step (ADR-007). So acceptance is gated on a promotion
that has not happened.

### Changes applied

| # | Change | Files |
|---|---|---|
| 1 | The reporting skill became an activation **step** | 11 agent files |
| 2 | `C-COM-006` **amended** — V6 is the earliest of B5's three routes | `constraints/commercial/commercial-constraints.md` |
| 3 | Acceptance template gains `Submitted for acceptance:` and `In live use since:` | `templates/phase-acceptance-template.md` |
| 4 | `acceptance-agent`'s V6 section rewritten against the clause text | `agents/acceptance-agent.md` |
| 5 | `verify-shipped-content.py` check 3 — form labels vs the column's own name, with a known-bad fixture | `scripts/verify-shipped-content.py`, `src/tests/fixtures/known-bad/shipped-content-label/` |
| 6 | Corrections honoured: a superseded session is excluded from every total | `scripts/verify-worklog.py`, `scripts/compute-invoice.py` |
| 7 | Ten preconditions answered; `not_yet_required` added as a non-blocking state | `contract/external-dependencies.json`, `scripts/wbs-ready-set.py` |
| 8 | 16 entries to `APPLIED` | `logs/improvement-log.jsonl` |

**Zero new constraints.** One amendment, because `C-COM-006` was wrong rather than incomplete.

## 7. What this review cannot decide

All four questions this section originally raised were answered — see §6. What remains:

**The board cutoff decision is unclear to the reviewer too.** It is the one precondition that has
been asked and came back undetermined, so it will not resolve by waiting. It gates automation #2.

**Four findings stay open**, each with a return trigger: two on deriving test counts from source
rather than asserting literals (`test-coupled-to-absolute-counts`, x2 — the altitude rule forbids
another instance patch, and the generalisation touches roughly a dozen assertions), one blocked on a
destructive metadata call this environment refuses, and one needing a `when: ci` condition in the
build-config schema.

**`C-COM-010` should be strengthened, not retired.** It requires an exception to carry a clearing
action; it does not require that action to be *possible*. Both live exceptions were written with a
clearing action — "WBS v0.6 restates it" — that the reviewer then confirmed could never happen. The
rule caught nothing. It is one day old and its first real test found a gap in itself, which is why the
recommendation is to strengthen rather than retire.
