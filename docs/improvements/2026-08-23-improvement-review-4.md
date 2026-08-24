# Improvement Review 16 — 2026-08-23

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 9 → 5 clusters (8 unread, 1 appended by this review)
**Trigger:** blocker escalation — `IMP-0224`, processed immediately rather than batched. `IMP-0221`, the second unread blocker, is in scope by the same activation step.
**Gate:** `APPROVE IMPROVEMENTS`
**WBS:** `system`. The findings guard delivery tasks 6.1–6.5. No contracted task is claimed here.

**Status:** ~~AWAITING `APPROVE IMPROVEMENTS`.~~ **APPROVED and APPLIED 2026-08-23** by the
reviewer (Xander Lykopoulos). See section 8 — including three findings deliberately **not** closed,
and two corrections made to this review's own proposals during application.

---

## The headline

**Three separate findings logged today all say the same thing: a written claim that a problem was
fixed was accepted as proof the problem was gone.** The trustee portal's connector error was
declared fixed and the reviewer hit it again live. A `pac` hang was declared fixed by killing a
process and it hung again immediately afterwards. Two test rows were recorded as deleted and are
still in the environment. Three different agents, three different subjects, one shape.

**The mechanism that let it happen is this system's own closure check, and it is circular.** When a
finding is closed, [verify-improvement-log.py](../../scripts/verify-improvement-log.py#L681)
requires an `evidence_grep` needle — a file and a string that must be present. The needle that
closed the connector defect pointed at
[code-apps.md](../../knowledge/technology/code-apps.md#L219) and searched for the words *"This is
the fix, and it is confirmed working"*. That sentence was written **by the review that was closing
the finding**. The check passed because the reviewer had typed the claim, not because anything
re-tested it.

**So the fix is not another knowledge note — the last three reviews already wrote those.** It is a
new required field on a finding saying at what level the defect was actually visible, and a rule
that a defect visible only to a live signed-in user cannot be closed by a document saying it was
fixed. That is a script change, and it binds forward only.

**Nothing here waits on the repair currently in flight.** A development-agent dispatch is fixing the
live connector defect now, by one of two possible routes. The knowledge correction proposed below
deliberately describes *the class of mistake* — the fix was verified against a data source the app
never calls — rather than naming today's remedy, so it stays true whichever route lands.

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Review 11 — [code-apps.md](../../knowledge/technology/code-apps.md#L204) org-url diagnostic rewritten from executed ground truth | 2026-08-22 | `code-app-connector-org-url-null` | **YES — twice** (`IMP-0208`, then `IMP-0224`) | **Wrong altitude.** Prose, twice over |
| Review 12 — [code-apps.md](../../knowledge/technology/code-apps.md#L219) step 2 declared the `-u` flag the confirmed fix | 2026-08-22 | same class | **YES — `IMP-0224`, live** | **Wrong altitude, and factually narrower than written** |
| Review 15 — [build-and-deploy.md](../../knowledge/technology/build-and-deploy.md) hang procedure, stray-`pac`-process cause | 2026-08-23 | `platform-contract-guessed-not-groundtruthed` | **YES — `IMP-0217`, same incident** | **Diagnosis was wrong.** Correlation accepted as cause |
| Review 14 — [verify-source-derived-test-counts.py](../../scripts/verify-source-derived-test-counts.py) + `C-TECH-067` | 2026-08-23 | `test-coupled-to-absolute-counts` | NO | Working — leave alone. Too recent to be conclusive |
| Review 13 — knowledge note on generated-service write semantics, no gate minted | 2026-08-23 | `platform-fact-groundtruthed` | NO | Working — the control was already a test |
| Review 8 — `evidence_grep` needle required on closure | 2026-08-21 | closure claims unverifiable | **YES — this review** | **Mis-scoped.** A needle proves an artefact changed, never that a symptom stopped |

**Changes whose class recurred after a prose fix:** review 11, review 12, review 15 — all three in
the same 24 hours. Escalated to a mechanical gate in cluster A below.

**The last row is the important one.** The needle requirement is not wrong; it is incomplete in a
way that produces false confidence, which is worse than a missing check. It is logged as a finding
in its own right — `IMP-0225`, appended by this review.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: remediation-claimed-not-reobserved  (x4: IMP-0224 blocker, IMP-0217 rework,
                                                    IMP-0218 rework, IMP-0225 rework)
Altitude:  CLASS. Four findings in one day, three agents, one shape: a remediation was
           recorded in a document and the document was then read as evidence the defect
           was gone. IMP-0224 is instance 9 of `v3-does-not-imply-v4` and instance 5 of
           `code-app-connector-org-url-null`; IMP-0217's own why_it_was_never_caught names
           this review process by file.
Ladder row: "a tool could catch it mechanically" + "second instance -> generalise"
Becomes:   scripts/verify-improvement-log.py gains `observable_at` (required on new
           blocker/rework entries) and `reobserved` (required to close one), forward-bound
           to this review the way NEEDLE_REQUIRED_FROM already is.
           Plus the four prose edits that hang off it (section 3).
Retires:   nothing. No instance gate existed for this class; the closure check that did
           exist is amended, not retired, because it is correct for the artefact half.
Cites:     IMP-0217, IMP-0218, IMP-0224, IMP-0225
Residual:  The gate cannot tell whether a `reobserved` record is TRUE. It asserts that
           someone recorded a named person, a timestamp later than the finding, and the
           exact step re-run — it cannot verify they ran it. That is the same residual
           C-TECH-053 carries for V4 generally, and it is the right one to keep: the
           failure being prevented is nobody re-running the step at all, not somebody
           lying about having done so.
```

```
CLUSTER B: a blocked_on note is a claim about a point in time  (x2: IMP-0220, IMP-0222)
Altitude:  CLASS. IMP-0222 is instance 5 of
           `agent-instructions-describe-a-topology-that-changed`; IMP-0220 is instance 6 of
           `harness-blocks-destructive-call` and revises what that class actually is. Both
           findings disprove a standing written claim that an operation cannot be performed.
Ladder row: "a tool could catch it mechanically" for the staleness half; "an agent had the
           information and still did the wrong thing" for the routing half.
Becomes:   scripts/verify-pipeline-config.py gains a staleness check on `blocked_on`;
           agents/pipeline-agent.md gains a "try the native pac verb first" step and loses
           a factual claim that is now known false.
Retires:   nothing at constraint level. The retired *claim* is in prose and is corrected
           in place, not deleted (IMP-0209's precedent).
Cites:     IMP-0220, IMP-0222
Residual:  SUPERSEDED AT APPLY TIME — see section 8. This said the check could only see a
           blocked_on naming a FILE path, and that the "the harness refused it in August"
           half was unmechanisable. The path-based check was built, produced 3 false
           positives on this config, would not have caught IMP-0222, and was withdrawn.
           What shipped is an EXPIRY (blocked_on_asserted + a 14-day limit), which covers
           both halves. The real residual is smaller: an expiry catches rot on a timer, so
           a note that goes stale on day 2 — as IMP-0222's did — is still only caught on
           day 15. Nothing detects that faster without re-running the step.
```

```
CLUSTER C: IMP-0221 (blocker) — the V4 positive control has no member
Altitude:  INSTANCE. One occurrence, specific to one environment's membership state.
Ladder row: "one instance, cause is general, a human needs to know it"
Becomes:   a precondition line in the V4 step of the pipeline config. The lesson is
           already in the digest.
Retires:   nothing
Cites:     IMP-0221
Residual:  No script can check this. verify-column-security-membership.py reads settings
           FILES and asserts the negative control (no trustee team is ever a member); the
           positive control is live per-environment state that no source file declares.
           Making it mechanical would mean a live query in a build gate, which this
           repository deliberately does not do.
```

```
CLUSTER D: IMP-0219 (friction) — a register row's closing precondition is not tracked
Altitude:  INSTANCE. First member of its class.
Ladder row: "one instance, cause is general" -> a template field
Becomes:   a column in templates/test-report-template.md section 7.1
Retires:   nothing
Cites:     IMP-0219
Residual:  scripts/verify-assumption-register.py could eventually assert the new column is
           populated. Not proposed now — one instance does not earn a gate, and a gate over
           an empty column is a gate that fires on nothing (IMP-0057's class).
```

```
CLUSTER E: IMP-0223 (friction, capability) — a pushed Code App IS a solution component
Altitude:  NOTHING BEYOND THE RECORD. A ground-truthed platform fact that closes an open
           architecture question. No defect, no rule.
Ladder row: "a capability was established and could be lost again"
Becomes:   TAD section 9.3's open deviation closed; the duplicate per-environment push
           step removed from the pipeline config's tst_acc/prd blocks.
Retires:   the TAD's open question, which is the point of it.
Cites:     IMP-0223
Residual:  Verified in DEV only. Whether the component survives the managed export into
           TST/ACC is a separate observation nobody has made yet, and section 3 says so
           rather than implying it follows.
```

---

## 3. Proposed changes

### A1 — the closure gate (the substance of this review)

**`scripts/verify-improvement-log.py`** — two new fields and three rules, bound forward exactly the
way [`NEEDLE_REQUIRED_FROM`](../../scripts/verify-improvement-log.py#L233) already binds the needle
requirement. Retroactive application would report on ~200 finished entries, which is how a gate
teaches people to skip it.

```python
# From this review onward, a finding declares the level at which its defect was VISIBLE, and a
# defect visible only at runtime cannot be closed by a document saying it was fixed.
#
# Review 8 required a needle on closure. A needle proves an artefact CONTAINS a string. IMP-0208
# closed on a needle pointing at knowledge/technology/code-apps.md for the words "This is the fix,
# and it is confirmed working" -- a sentence written by the review doing the closing. The check
# passed by construction. Three days later the reviewer hit the identical error live (IMP-0224),
# and on the same day two more findings recorded the same shape (IMP-0217, IMP-0218).
REOBSERVATION_REQUIRED_FROM = ("2026-08-23", 16)

VALID_OBSERVABLE_AT = {"V1", "V2", "V3", "V4", "V5", "n/a"}
```

Rule 1 — **declare it.** An entry with `ts` on or after the cutoff whose `severity` is `blocker` or
`rework` must carry `observable_at`. `n/a` is a valid answer and means the defect had no runtime
symptom (a wrong document, a missing citation, a process gap). The author knows this at the moment
they write the finding and never again.

Rule 2 — **close it at its own level.** An entry whose `observable_at` is `V2` or higher may not
move to `APPLIED` while its only closure evidence is an `evidence_grep` needle pointing into
`knowledge/`, `docs/`, `agents/`, `skills/`, `constraints/` or `contract/`. Those are prose. It must
also carry `reobserved`:

```json
"reobserved": {"level": "V4",
               "by": "XLykopoulos@revitalise.org.uk",
               "ts": "2026-08-23T14:00",
               "rerun": "signed in to REV Trustee Review Portal, opened the applications list",
               "result": "symptom absent — list loaded, no org-url error"}
```

Rule 3 — **the record must be later than the finding.** `reobserved.ts` must postdate the entry's
own `ts`, and `rerun` must be non-empty. A re-observation timestamped before the defect was recorded
is a copy of the original report.

The self-test at [`selftest()`](../../scripts/verify-improvement-log.py#L1121) gains one passing and
one failing fixture per rule, per [`C-TECH-057`](../../constraints/technology/technology-constraints.md#L127).

**Why this catches what prose did not.** `IMP-0208` was `severity: blocker`. Under rule 1 it declares
`observable_at: V4` — its own text describes a browser error seen by a signed-in user. Under rule 2
review 12 could not have closed it on a `code-apps.md` needle. The gate would have said so, in the
review, before the reviewer spent a day discovering it live.

### A2 — the three files that tell agents to use it

| File | Change |
|---|---|
| [how-to-log-an-improvement.md](../../skills/how-to-log-an-improvement.md#L35) | `observable_at` added to the schema block and to *Required fields, and the three that do the work* at [line 50](../../skills/how-to-log-an-improvement.md#L50), with the one-line rule: *the level at which YOU could see the defect, not the level at which you happened to notice it* |
| [how-to-promote-a-finding.md](../../skills/how-to-promote-a-finding.md#L103) | §4 *What is not evidence for promotion* gains a fourth bullet: **an argued mechanism is not a confirmed cause.** A fix may not be written into a knowledge file until the exact failing call has been re-run and observed to succeed. `IMP-0217` names this file by path as the thing that permitted its defect |
| [improvement-agent.md](../../agents/improvement-agent.md#L116) | Activation step 8 gains: before setting an entry to `APPLIED`, check its `observable_at` and record `reobserved` where the gate requires it — and where the re-observation cannot be made in this session, the entry stays `NEW` with a `revisit_when`, rather than being closed on the review's own prose. The Regression Check table at [line 122](../../agents/improvement-agent.md#L122) gains a fourth row: *did the closure evidence match the level the defect was visible at?* |

### A3 — the knowledge correction, written to survive either repair

**[code-apps.md](../../knowledge/technology/code-apps.md#L219) step 2 is corrected, not deleted.** The
`-u` flag genuinely works — for what it covers. The sentence *"This is the fix, and it is confirmed
working"* is what needs to go, because it was read as closing the defect for the app rather than for
one data source inside it.

Proposed replacement, deliberately scoped to the *class of mistake* rather than to today's remedy,
because the repair is in flight and may land as either a generic-connector fix or a migration of the
hand-rolled client onto the generated typed services:

> **2. Pass the org URL explicitly — and then check you fixed the data source the app actually
> calls.** `pa app add data-source --connector dataverse --table <t> -u <url>` succeeds and produces
> real per-table models and services. **It changes only the per-table dataset it names.** An app can
> hold two Dataverse data sources in one `dataSourcesInfo.ts`: the per-table entries the command
> generates, and a separate generic `commondataserviceforapps` block that a hand-rolled client calls
> directly. `-u` does not exist for the generic one, and fixing the first leaves the second exactly
> as broken.
>
> **Before believing this symptom is resolved, answer two questions.** Which key does
> `getClient(dataSourcesInfo)` resolve against — read the call site, not the schema. And which
> top-level key carries non-empty `apis` for the operations the app issues: in this project
> `ListRecords` / `GetItem` / `UpdateOnlyRecord` live only under the generic connector key, and every
> per-table key has `"apis": {}`.
>
> **Then re-open the app as a real signed-in user.** This defect has never been observable any other
> way. A clean `tsc`, a clean `eslint`, a zero exit from the CLI and a diff full of new generated
> files are all evidence about the files — none of them is evidence about the running app. Five
> findings in this class were closed on that evidence and the error was still there.

The live call site is [client.ts line 143](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts#L143);
the generic block is [dataSourcesInfo.ts line 8](../../src/code-apps/trustee-review-portal/.power/schemas/appschemas/dataSourcesInfo.ts#L8)
and the per-table keys with empty `apis` begin at
[line 1835](../../src/code-apps/trustee-review-portal/.power/schemas/appschemas/dataSourcesInfo.ts#L1835);
the app's own README states the choice at
[line 30](../../src/code-apps/trustee-review-portal/src/dataverse/README.md#L30).

### A4 — one constraint amendment, and no new constraints

**No new constraint row is proposed.**
[`C-TECH-053`](../../constraints/technology/technology-constraints.md#L108) already says a component
is reported only at the level actually executed. It was never wrong; it simply governs components in
a deploy and says nothing about a finding being closed. Adding a near-duplicate row would be the
bloat the anti-bloat limits exist to stop.

Proposed amendment, in place, to `C-TECH-053`'s rule text and Checked By column:

> …and **a finding is closed only by evidence at the level its defect was visible at**: a defect
> observable only to a signed-in user (V4) or in an end-to-end run (V5) is not closed by a document
> recording the fix. Checked By gains `improvement-agent`. Verify By gains
> `python3 scripts/verify-improvement-log.py --check`.

### B — the two pipeline changes

**[verify-pipeline-config.py](../../scripts/verify-pipeline-config.py#L462)** gains check 14, inside
`check_step`: when a step's `script` is `manual` and its `blocked_on` text names a path under
`provisioning/`, `config/` or `scripts/`, **fail if that path now exists**. The
[auditing step](../../config/revitalise-grant-automation-pipeline.yml#L667) sat marked *DEAD AS
DECLARED* for a full day after `dev-auditing-settings.json` was created, and ran clean on the first
attempt when finally re-tried.

**[pipeline-agent.md](../../agents/pipeline-agent.md#L73)** — two edits to *Reviewer-Executed
Operations*. A new step before the escalation ladder: *check for a native `pac` verb first* —
`pac admin assign-user` performed a live role-assignment write from the same background session
where the equivalent hand-rolled call was refused twice. And the standing sentence naming the
`organizations` / `EntityDefinitions` auditing PATCH as one of three recorded refusals is corrected:
it was not refused on 2026-08-23. The refusal boundary as now observed is *a shell command that
itself touches local keychain material*, not *a Dataverse write*.

**[pipeline.yml](../../config/revitalise-grant-automation-pipeline.yml#L667)** — the auditing
prerequisite's `script` changes from `manual   # DEAD AS DECLARED` to the executable form, with the
live result recorded.

### C, D, E — the three smaller changes

| Finding | File | Change |
|---|---|---|
| `IMP-0221` | [pipeline.yml V4 step](../../config/revitalise-grant-automation-pipeline.yml#L777) | The positive control's instruction gains an explicit precondition: confirm live that the comparison identity is a `REV_TrusteeRestricted` member before trusting a populated-or-null result. In DEV today it is zero on both axes, so the comparison read returns null for everyone and proves nothing |
| `IMP-0218` | [how-to-verify-a-platform-contract.md](../../skills/how-to-verify-a-platform-contract.md#L246) | Checklist gains: a recorded removal under [`C-TECH-056`](../../constraints/technology/technology-constraints.md#L111) is re-queried by id before a later report accepts it. Two rows recorded as deleted are still live in DEV |
| `IMP-0219` | [test-report-template.md](../../templates/test-report-template.md#L57) | Section 7.1 gains a *closing precondition, and does it exist yet* field, separate from OPEN/CLOSED |
| `IMP-0223` | [TAD section 9.3](../../docs/architecture/revitalise-grant-automation-architecture.md#L1094) | Open deviation closed: a pushed Code App registers as componenttype 300 in its solution, verified live in DEV. The pipeline config's tst_acc/prd blocks drop the second per-environment push. Stated as DEV-verified only — survival through the managed export is not yet observed |

---

## 4. Retirements

**Checked, and no constraint is a retirement candidate this round.**
[verify-constraint-verifiers.py](../../scripts/verify-constraint-verifiers.py) passes: *63
repository paths named by 74 active constraint rows all resolve*, so no row has drifted into naming
a verifier that no longer exists — the condition that produced the last seven retirements. The prose
retraction in A3 is the nearest equivalent and is handled as a correction in place.

**But the reverse obligation has come due, and nothing was watching for it.** Four constraints —
[C-TECH-020](../../constraints/technology/technology-constraints.md#L151),
[C-TECH-021](../../constraints/technology/technology-constraints.md#L152),
[C-TECH-022](../../constraints/technology/technology-constraints.md#L153) and
[C-TECH-023](../../constraints/technology/technology-constraints.md#L154) — were retired on the
stated grounds that this repository has no dependency manifest, each with the same written
condition: *"reinstate with a new id when the Phase 3 Code App introduces a real manifest."*

That condition is now met.
[package.json](../../src/code-apps/trustee-review-portal/package.json) and a tracked
`package-lock.json` carry 24 dependencies, and `npm audit` would run against them today.

**This is cluster B's class at constraint altitude** — a retirement reason is a claim about a point
in time, and four of them expired without anyone noticing. It is **not** proposed here: reinstating
four rows would breach the 3-per-review cap and each needs its own build step designed
(`npm audit`, a lockfile check, a licence scan). Recommended as the first item of the next review.

---

## 5. Findings left unprocessed

Per the no-silent-caps rule, the states excluded from this pass and why:

| Excluded | Count | Which | Why |
|---|---|---|---|
| `awaiting-approval` | 1 | `IMP-0198` | A review already processed it and is parked at its own gate. It needs the keyword sent against **that** document, not a second review (`IMP-0154`, `IMP-0183`) |
| `reviewer-deferred` | 4 | `IMP-0112`, `IMP-0152`, `IMP-0197`, `IMP-0205` | Each carries a `deferred_reason` a human accepted |
| `APPLIED` / `REJECTED` | 208 | — | The digest already carries their lessons |

All 8 `unread` entries were read in full, and all 8 — plus `IMP-0225`, appended here — are processed
above. Nothing in scope was deferred, and no cap was applied silently.

---

## 6. Digest impact

**Two bookkeeping actions are already on disk, deliberately, because neither is a rule change.**

`logs/improvement-log.jsonl` moved from 221 to 222 entries — `IMP-0225`, appended by this review,
recording that the needle check is satisfiable by a self-certifying sentence. A finding is an
observation and stays true whether or not this review is approved; leaving it unwritten is
`IMP-0033`'s failure. [known-failure-modes.md](../../logs/known-failure-modes.md) was regenerated in
the same breath (`IMP-0080`) and `--check` reports it current at 222 lessons and 25 recurring
classes.

All nine processed entries were stamped with `reviewed_in`. That is the remedy
[verify-improvement-log.py](../../scripts/verify-improvement-log.py) itself printed nine times, and
`IMP-0154`'s rule: an entry a review has processed must not read as one nobody has opened. The queue
now correctly reports **0 unread** and this document as the thing the two blockers are waiting on.

Two recurring classes advanced: `gate-reassures-wrongly` to x10 with `IMP-0225`
([line 34](../../logs/known-failure-modes.md#L34)), and `v3-does-not-imply-v4` stands at x9 with
`IMP-0224` ([line 37](../../logs/known-failure-modes.md#L37)).
`code-app-connector-org-url-null` reaches its fifth entry under that exact class name and its
seventh across the connector chain. `IMP-0224`'s lesson sits in *Before you declare a deploy or an
import successful* at [line 189](../../logs/known-failure-modes.md#L189).

On approval the digest regenerates again, with the nine entries moved to `APPLIED`.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-23-improvement-review-4.md

Findings processed: 9 NEW  →  5 clusters
Regression check:   6 prior changes audited, 4 classes recurred
Proposed:           0 constraints (cap 3) + 1 amendment, 2 gates/scripts,
                    6 skill/knowledge/template edits, 2 agent-file edits, 0 retirements
Altitude calls:     2 generalised from instance to class, 3 left as notes
Digest:             will regenerate — 222 lessons, 25 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

**APPROVED and APPLIED 2026-08-23.** Everything in sections 2–4 is on disk, with two departures
from what section 3 proposed. Both are recorded below rather than quietly absorbed.

### What changed

| # | Change | File | Cites |
|---|---|---|---|
| 1 | `observable_at` + `reobserved`, three rules, forward-bound by `REOBSERVATION_REQUIRED_FROM` | [verify-improvement-log.py](../../scripts/verify-improvement-log.py#L233) | IMP-0225 |
| 2 | 12 new self-test fixtures — one reproduces IMP-0208's closure exactly | [verify-improvement-log.py](../../scripts/verify-improvement-log.py#L1121) | IMP-0225, C-TECH-057 |
| 3 | `C-TECH-053` amended: a finding is closed only by evidence at the level its defect was visible at; `improvement-agent` added to Checked By | [technology-constraints.md](../../constraints/technology/technology-constraints.md#L108) | IMP-0217, IMP-0218, IMP-0224, IMP-0225 |
| 4 | Activation step 8 rewritten; a fourth row added to the Regression Check | [improvement-agent.md](../../agents/improvement-agent.md#L116) | IMP-0225 |
| 5 | Schema gains `observable_at`; both new fields documented | [how-to-log-an-improvement.md](../../skills/how-to-log-an-improvement.md#L36) | IMP-0225 |
| 6 | §4 gains *an argued mechanism is not a confirmed cause* | [how-to-promote-a-finding.md](../../skills/how-to-promote-a-finding.md#L110) | IMP-0217 |
| 7 | Step 2 corrected — `-u` scoped to per-table datasets, with the two questions and the V4 demand | [code-apps.md](../../knowledge/technology/code-apps.md#L219) | IMP-0224 |
| 8 | Hang procedure corrected; new step 2 for the macOS Keychain prompt | [build-and-deploy.md](../../knowledge/technology/build-and-deploy.md#L275) | IMP-0217 |
| 9 | §10 checklist: a removal recorded by someone else is re-queried, not believed | [how-to-verify-a-platform-contract.md](../../skills/how-to-verify-a-platform-contract.md#L264) | IMP-0218 |
| 10 | §7.1 gains *Closing precondition* / *Does it exist yet?* columns | [test-report-template.md](../../templates/test-report-template.md#L62) | IMP-0219 |
| 11 | Check 14: every `blocked_on` carries `blocked_on_asserted` and expires after 14 days | [verify-pipeline-config.py](../../scripts/verify-pipeline-config.py#L462) | IMP-0222 |
| 12 | Step 3a — look for a native `pac` verb first; refusal-boundary paragraph corrected | [pipeline-agent.md](../../agents/pipeline-agent.md#L73) | IMP-0220, IMP-0222 |
| 13 | DEV auditing step executable again; V4 positive-control precondition; code-app push answer; 11 `blocked_on` notes dated | [pipeline.yml](../../config/revitalise-grant-automation-pipeline.yml#L664) | IMP-0221, IMP-0222, IMP-0223 |
| 14 | TAD §9.3's open deviation closed, with the evidence and its scope | [architecture.md](../../docs/architecture/revitalise-grant-automation-architecture.md#L1094) | IMP-0223 |

### Two corrections to this review's own proposals

**The `blocked_on` check in section 3 was built, tested, and withdrawn.** Section 3 proposed
failing when a `blocked_on` names a path *as missing* that now exists. Run against this project's
own config it produced **three false positives** — notes that cite a path as *evidence for* the
blockage, such as a test asserting that a function throws — and it would **not** have caught
`IMP-0222`, whose note never named `dev-auditing-settings.json` at all. A gate with a 3:0
false-positive ratio is one people learn to route around, which is the failure this whole review is
about. It was replaced by an expiry: a `blocked_on` now carries `blocked_on_asserted` and goes red
after 14 days. That is unfoolable by prose and it covers the half no artefact test can reach —
*"the harness refused this in August"* names nothing a script can re-test, but it can still go
stale, and now it says when. All 11 remaining notes were stamped with their own asserted date and
the preflight passes at 81 steps.

**The new gate's cutoff was wrong on its first run, and it caught itself.** Rule 1 bound entries
with `ts` **on or after** 2026-08-23, and immediately reported four entries — `IMP-0210`,
`IMP-0212`, `IMP-0215`, `IMP-0216` — that were written and closed hours earlier the same day, before
the rule existed. That is `IMP-0181`'s lesson in miniature: a rule cannot bind entries written
before it existed. The comparison is now strict, with a fixture asserting that the cutoff date
itself is not bound.

### Three findings deliberately left OPEN

This is the new rule applied to its own review, and it is the part worth reading.

**The rule change shipped; the defect did not go away.** For `IMP-0218`, `IMP-0221` and `IMP-0224`
the proposed change is on disk — but each records a defect that is **still live**, and each is
`observable_at` V4 or V5. Closing them on the document edit is exactly what review 12 did to
`IMP-0208`, and exactly what this review exists to prevent. Each now carries a `deferred_reason`
and a `revisit_when` naming the live observation that closes it:

| Finding | Applied | Still open until |
|---|---|---|
| `IMP-0224` (blocker, V4) | code-apps.md step 2 corrected | a real trustee signs in after the repair lands and the three call sites return data |
| `IMP-0221` (blocker, V4) | pipeline.yml V4 precondition added | one identity is a member of `REV_TrusteeRestricted` and the positive control has actually been read |
| `IMP-0218` (rework, V5) | the re-query rule added to the skill | the two `rev_review` rows are deleted and a re-query by id returns nothing |

**Six closed, and two of them carry a real `reobserved` record.** `IMP-0217` closes on the reviewer's
and build-agent's own re-run of the failing `lint` step (35.5s, correlation id
`a6c0e6e2-7faa-41c3-b76d-062b81b2d364`, all severities 0). `IMP-0225` closes on the new fixture that
reproduces `IMP-0208`'s closure shape and now goes red. `IMP-0219`, `IMP-0220`, `IMP-0222` and
`IMP-0223` are `friction` and needed no re-observation.

### Verification

`verify-improvement-log --selftest`: 36 fixtures, all pass. `verify-improvement-log --check`: one
trigger, and it belongs to another session (below). `generate-known-failure-modes --check`: current
at 224 entries. `verify-pipeline-config`: PASS, 81 steps across 3 environments.
`verify-constraint-verifiers`: PASS.

**Not verified, and it cannot be from here:** that any of the three open findings' defects are gone.
That is the point of leaving them open.

### Findings NOT PROCESSED here, and carried forward

**The `C-TECH-020`–`023` reinstatement** stays for the next review, at the reviewer's explicit
instruction and this review's own recommendation.

**Two findings arrived from another session while this one was being applied** —
`IMP-0226` (friction) and `IMP-0227` (**blocker**, `observable_at: V4`), both from the
development-agent dispatch repairing `IMP-0224`. `IMP-0227` reports the read paths migrated to the
generated typed services. They are `unread`, they postdate this dispatch, and they are **not**
processed here: one unread blocker does not pull a review of everything around it (`IMP-0183`).
`IMP-0227` is a new blocker trigger and needs its own dispatch.

Worth recording: `IMP-0227` was written **after** this review's gate landed and already carries
`observable_at: V4`, set by a different agent. The field is in use within the hour.
