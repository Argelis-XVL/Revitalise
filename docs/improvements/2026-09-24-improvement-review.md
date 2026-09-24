# Improvement Review — 2026-09-24

**Status:** APPLIED 2026-09-24. All five changes in section 6 are on disk, verbatim as approved.
Two of the draft's *predictions about what the changes would measure* were wrong and are corrected
in section 12; no approved wording was altered.

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 36 `NEW` → 8 clusters
**Trigger:** the batch rung — 32 unread entries, over the threshold of 30. No unread blocker.
**Gate:** `APPROVE IMPROVEMENTS`

**Scope.** This is the first batch review since 2026-09-20. Every review in between was a blocker
escalation processing one to three entries, so the friction and rework queue grew unread from eight
to thirty-two while the critical ones were handled promptly. All thirty-two are processed here,
plus three this review logged itself while measuring. One entry appended by a live session
mid-draft is named in section 7 and left alone.

---

## Summary

Thirty-six findings resolve into eight groups. Five changes are proposed, none of them a new
constraint, and every one was measured against the real corpus before being written down rather
than after.

Two of those measurements changed the proposal they were testing. A gate that checks whether a
live deployment recorded its access probe turns out to be reading about one marker in five, not
one in five-ninths as the finding said — and the obvious wider fix, measured, opens ninety-three
complaints about finished work, so the narrow fix ships and the rest becomes a decision for you.
A gate over the commercial ledger has two false matches, not the one its finding named, and
correcting them still does not make it green, because the two sides of its comparison count
different things.

The rest of the queue divides into eight items routed to delivery agents, nine deferred with a
stated return condition, and eighteen closed.

---

## 1. Regression check — did the last review's changes work?

The previous review is [2026-09-23 improvement review 6](2026-09-23-improvement-review-6.md),
applied the same day. Six further reviews were applied in a batch on 2026-09-23.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [`agents/development-agent.md`](agents/development-agent.md#L395) — the companion-checks block before reporting a new provisioning script done | 2026-09-23 | `new-provisioning-script-companion-artifact-missed-serially` | **No.** Two builds have run since (`20260924-2`, `20260924-4`) and neither logged that class | Working, but one day old — weak evidence, not strong |
| [`skills/how-to-model-a-data-schema.md`](skills/how-to-model-a-data-schema.md#L28) — declare a new table for auditing in all three settings files | 2026-09-23 | audit-declaration drift | **No** | Same — too recent to be evidence |
| [`skills/how-to-verify-a-platform-contract.md`](skills/how-to-verify-a-platform-contract.md#L343) — re-check your own tier after ground-truthing | 2026-09-23 | `dispatched-below-required-tier` | **No, and it fired correctly once** — IMP-0841's own cost line records one tier escalation on exactly this trigger | Working |
| `skills/how-to-verify-a-platform-contract.md` §2 — two governing-artefact rows for what an external data service returns | 2026-09-23 | `platform-contract-guessed-not-groundtruthed` | **Yes** — see below | **Recurred after a prose change. Escalating within the same file** |
| `skills/how-to-verify-a-platform-contract.md` §12c — a plan or brief's paraphrase of a source document is itself an artefact | 2026-09-23 | `approved-document-internally-inconsistent` | **Ambiguous** — IMP-0832 is the same property, timestamped the morning of the day the change landed. Cannot tell which came first | Counted as neither; re-audit next review |

### The one that recurred, and why it is not a failure of the change

The §2 rows added on 2026-09-23 say that what an external data service returns is cited from a live
metadata call. That rule was followed. The architect ran a live call, the endpoint returned HTTP
400, and the 400 was recorded as a verified fact about what the service cannot do.

It was not a fact. The identical query succeeded eight times out of eight when the requests were
paced two seconds apart. The service answers overload with a 400 rather than a 429, so a capability
probe and a throttle response are the same observation.

So the change did what it said and the gap it left is one level down: **the skill governs where
evidence comes from and says nothing about how many times a refusal must be seen before it counts.**
That is change 5.

---

## 2. Cluster 1 — a gate that reads one marker in five

**Findings:** IMP-0819, and IMP-0863 which this review logged while measuring it.
**Class:** `gate-cannot-fail`, now at 51 instances.

[`scripts/verify-provisioning-report.py`](scripts/verify-provisioning-report.py#L81) enforces
`C-TECH-065`: a dispatch that writes to a live environment must have recorded a read-only access
probe first, and the entry in `logs/pipeline.log` is what proves it. The finding reported that the
gate's regexes are anchored to the start of a line, so a marker written behind an ISO-8601
timestamp — which dispatches have been doing since 2026-09-19 — is invisible.

That is true. It is also about a fifth of the problem.

### What the corpus actually contains

Counted over `logs/pipeline.log`, one command per shape:

| Shape of the marker | Occurrences | Seen by the gate |
|---|---|---|
| `WRITE BEGUN:` bare at the start of a line — the documented convention | 7 | **yes** |
| `2026-09-19T12:09:51Z WRITE BEGUN:` — behind an ISO timestamp | 9 | no |
| `[2026-09-19 12:33] [PIPELINE] … WRITE BEGUN:` — inline after the entry header | 19 | no |
| `WRITE_BEGUN — …` — underscore spelling, em-dash separator | 84 | no |

Counting whole log entries rather than markers: the gate observes **3 write-bearing entries out of
25**, or 12%. It has been reporting on an eighth of its own subject matter since the convention was
introduced on 2026-08-24.

### Why the wide fix is not the fix

Two wider designs were built in scratch and run against the real log. Both were rejected on the
number, not on taste.

**Widening the entry-boundary rule as well** — so an ISO-stamped line starts its own entry — yields
**22 findings**, one of which is matched out of the prose of a log note that happens to quote the
marker names, and several of which are artefacts of one operation being split across two synthetic
entries. That is the prose-matching instrument this repository has measured five times at 48–100%
false.

**Widening the marker vocabulary to all three spellings** yields **93 findings**, almost all of them
historical entries written under the underscore convention that never recorded a probe. Whether
that is real `C-TECH-065` debt or a convention that was simply never subject to the pairing rule is
not a question a regex settles, and shipping 93 complaints about finished work is precisely how a
gate teaches people to route around it (`IMP-0181`).

### The narrow fix, measured

Tolerating an optional leading ISO-8601 timestamp on the colon-form markers, with the entry
boundary left alone:

| | Markers seen | Write-bearing entries | Findings |
|---|---|---|---|
| Today | 7 | 3 | 1 |
| With the change | 16 | 6 | 4 |

**All four findings are true positives** — each names a real live write with no access probe
recorded in its entry. One of the three new ones is the 2026-09-22 DEV import the finding itself was
written about. They are adjudicated individually in section 6.

One defect of the fix as drafted, found by the measurement and corrected in the proposed text: a
marker on an unbracketed line is attributed to the preceding bracketed entry, so one finding would
have been reported against 2026-09-13 for a write that happened on 2026-09-19. The change carries
the date on the marker line itself where there is one.

The gate is `SUITE_GATE_EXEMPT` — its input is a post-deploy report, not a build artefact — so no
build is halted by the increase from one finding to four. It is already exit 1 today.

**Residual.** Two of the four marker spellings stay invisible after this change, and 84 occurrences
of the underscore form stay invisible. That is section 9's first decision.

---

## 3. Cluster 2 — a ledger gate counting mentions as acts

**Findings:** IMP-0829, IMP-0798, and IMP-0864 which this review logged while measuring.
**Class:** `gate-regex-matches-mention-not-act`, and `finding-premise-false-at-draft-time` for the
re-measurement.

[`scripts/verify-commercial-events.py`](scripts/verify-commercial-events.py#L83) counts the
authorising commercial acts recorded in `logs/pm.log` and compares that count against the ledger of
authorisations. Its two patterns are asymmetric: the change-order pattern requires the literal word
`APPROVED` after the order id, and the baseline pattern is a bare keyword match.

The finding reported one false match. Enumerating every line the pattern touches — four of them —
finds **two**:

| Line | Text | Verdict |
|---|---|---|
| 3 | `APPROVE BASELINE — estimating_rule amended to …` | **a real act** (the source of ledger entry CE-0008) |
| 21 | `… No import performed — awaiting APPROVE BASELINE.` | **a mention** — the finding's own example |
| 22 | `[BASELINE] — APPROVE BASELINE (Xander Lykopoulos): imported WBS v0.6 …` | **a real act** (CE-0003) |
| 32 | `… CE-0008 (2026-08-20 03:10 APPROVE BASELINE amendment, pm.log:3) …` | **a mention** — a timesheet line quoting the act it backfilled |

Two of four, 50% precision. Requiring the keyword to be followed by `(` or an em dash keeps both
real acts and rejects both mentions, which is the same anchor discipline the change-order pattern
already uses. The act count goes from 12 to 10.

### And it still does not reconcile, which is the more useful finding

With the fix, the gate reports 10 acts against 11 ledger entries. Mapping each act to its ledger row
by hand accounts for all ten. The eleventh row is `CE-0002`, whose action is `CLOSED` — a value the
script's own `AUTHORISING_ACTIONS` set does not contain.

So the two sides of the comparison count different populations: one side counts authorising acts,
the other counts all rows. **The change proposed here fixes the act side only, and the gate stays
red.** Adjusting the entry side to reconcile would be making a gate green rather than making it
true, and it is a commercial-agent question about what belongs in that ledger, not a regex question.
It is section 9's second decision.

---

## 4. Cluster 3 — a warning triaged in one document and silent in the next

**Findings:** IMP-0811, IMP-0861, IMP-0800, IMP-0802.
**Class:** `untriaged-tool-warning` and `triaged-warning-cites-no-local-row`.

`C-TECH-055` requires every tool warning to be triaged in **the current feature's own** Dev Summary.
Several features share one build configuration, so the same standing warnings — a chunk-size notice,
an `npm` deprecation, a disposal warning, an advisory on a test dependency — surface on every build
of every feature, and their reasoning was written once, in whichever feature first met them.

[`agents/build-agent.md`](agents/build-agent.md#L295) already states the remedy exactly: where the
rationale lives in another feature's document, this feature's Dev Summary carries a row citing it.

**The obligation is stated in the agent that reads the manifest and absent from the agent that
writes the document.** Grepped: `agents/development-agent.md` contains no occurrence of `triaged_in`,
`citing row`, or the sentence above. So the rule is correct, written down, and lands on nobody.

IMP-0861 measured the consequence: the convention was followed once and skipped in at least three
other feature Dev Summaries sharing the same configuration. Change 3 puts the obligation in the
authoring agent.

---

## 5. Cluster 4 — instructions describing a topology the project abandoned

**Finding:** IMP-0836. **Class:** `agent-instructions-describe-a-topology-that-changed`, at 9.

`agents/development-agent.md` step 7 requires a build and pipeline configuration per feature, and
the CI workflow's slug mechanism genuinely requires a file at that path. But no feature other than
the original has ever had one, across five change orders and several WBS tasks that all deploy into
the same Dataverse solution — because `verify-build-config.py` requires every gate in `scripts/` to
be wired as a step in any configuration that exists, so a new slug's file cannot be small.

Every dispatch so far has resolved this silently, by not creating the file. Change 4 makes the
choice explicit rather than leaving each dispatch to re-derive it and say nothing.

---

## 6. The changes awaiting the keyword

Five changes. No new constraints. Each `.engine` path is the same file reached through a directory
symlink, so it is one write, not two; `scripts/` genuinely holds two copies and is named as such.

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | script | `scripts/verify-provisioning-report.py` **and** `.engine/scripts/verify-provisioning-report.py` | The three marker patterns accept an optional leading ISO-8601 timestamp; a marker on an unbracketed line reports its own date rather than the preceding entry's; one `--selftest` fixture proves a timestamp-prefixed marker is detected **and** one proves it can still fail | IMP-0819, IMP-0863 | **Yes** — `python3 scripts/verify-provisioning-report.py` goes from 1 finding to 4, all adjudicated below |
| 2 | script | `scripts/verify-commercial-events.py` **and** `.engine/scripts/verify-commercial-events.py` | The `APPROVE BASELINE` pattern requires the keyword to be followed by `(` or an em dash, matching the change-order pattern's anchor discipline; a `--selftest` fixture for each of the two measured mentions | IMP-0829, IMP-0798, IMP-0864 | **Yes** — authorising acts go from 12 to 10, both mentions rejected, both real acts kept |
| 3 | agent | `agents/development-agent.md`, Dev Summary authoring | Where a build runs against a configuration shared with other features, the Dev Summary's warnings table carries a one-line row citing the document that triaged each shared warning, by path and line — even when the gate's own verdict is PASS and unchanged | IMP-0811, IMP-0861, IMP-0800, IMP-0802 | **No** — an authoring obligation; see the residual |
| 4 | agent | `agents/development-agent.md`, before *Build & Pipeline Config Output* | A decision step: if the feature deploys into a solution that already has a build configuration, state whether this feature amends that configuration or needs its own, and if its own, budget for replicating every wired gate. Do not resolve it silently either way | IMP-0836 | **No** — a decision step |
| 5 | skill | `skills/how-to-verify-a-platform-contract.md` §2, after the negative-claim subsection | A negative capability result — the endpoint refused — is re-issued at least three times, at least two seconds apart, before it may be recorded as a verified contract fact. The ONS FeatureServer 400-under-burst measurement is the worked example | IMP-0841, IMP-0842 | **No** — but the rule states a number, so a report can be checked against it |

### The exact text proposed

**Change 1** — in `scripts/verify-provisioning-report.py`, the three patterns become:

```python
# A marker may carry a leading ISO-8601 stamp. Dispatches have written them that way since
# 2026-09-19 and the anchored patterns silently stopped checking those writes (IMP-0819).
# Measured 2026-09-24 over logs/pipeline.log: 7 markers seen before, 16 after, 4 findings, all
# true. The two OTHER spellings in that file -- inline after the entry header (19), and the
# WRITE_BEGUN underscore form (84) -- are deliberately NOT matched here: widening to them yields
# 93 findings against finished work and needs a convention decision first (IMP-0863).
MARKER_STAMP = r"(?P<stamp>\d{4}-\d{2}-\d{2})T[\d:]{5,8}Z?\s+"
PREFLIGHT = re.compile(rf"^\s*(?:{MARKER_STAMP})?PREFLIGHT:\s*(?P<body>.+)$", re.MULTILINE)
WRITE_ATTEMPTED = re.compile(rf"^\s*(?:{MARKER_STAMP})?WRITE ATTEMPTED:\s*(?P<body>.+)$", re.MULTILINE)
WRITE_BEGUN = re.compile(rf"^\s*(?:{MARKER_STAMP})?WRITE BEGUN:\s*(?P<body>.+)$", re.MULTILINE)
```

The name is `MARKER_STAMP` and not `_STAMP` because the file already defines `ENTRY_STAMP`, which
contains `_STAMP` as a substring — the simulation below caught that as a needle that matched before
the change was written, which is the one kind of evidence needle that is worse than none.

and the failure message uses the marker's own `stamp` group where it has one, so a write recorded on
2026-09-19 is not reported against the 2026-09-13 entry it was appended under.

**The four findings this produces, adjudicated one at a time:**

| Reported against | The write | True or false |
|---|---|---|
| 2026-08-30 | `pac solution import … --force-overwrite` | **True** — already reported today; unchanged |
| 2026-09-19 (was 2026-09-13 before the date fix) | `pac solution import -Env dev — FAILED` | **True** — a real DEV import, no probe in its entry |
| 2026-09-19 | `pac solution import -Env dev — SUCCEEDED` | **True** — the retry of the same import |
| 2026-09-22 | `pac solution import -Env dev — SUCCEEDED` | **True** — the write IMP-0819 was written about |

**Change 2** — in `scripts/verify-commercial-events.py`:

```python
# The keyword must introduce the act, not merely appear on the line. Measured 2026-09-24 over
# logs/pm.log: the bare pattern matched 4 lines, 2 of them real acts (line 3, line 22) and 2 of
# them mentions -- line 21 "awaiting APPROVE BASELINE", and line 32 quoting the act it backfilled
# (IMP-0829, IMP-0864). This mirrors the CHANGE-ORDER pattern's own anchor on APPROVED.
AUTHORISING = (
    re.compile(r"\bAPPROVE\s+BASELINE\b\s*(?:\(|—)"),
    re.compile(r"\[CHANGE-ORDER\][^\n]*?\b[A-Z]{2}-\d+[A-Za-z0-9-]*\s+APPROVED\b"),
)
```

**Change 3** — a new bullet in `agents/development-agent.md`'s Dev Summary section:

> **A shared build configuration means shared warnings, and each feature's Dev Summary carries its
> own row for every one of them.** Where this feature builds against a `config/<slug>-build.yml`
> that other features also use, its warning-triage table needs a one-line citing row for each
> standing warning those shared steps emit — naming the document that actually triaged it, by
> `path#Lnnn` — even where the gate's verdict is PASS and nothing changed. A PASS is not a
> citation, and `triaged_in` in the build manifest has nowhere correct to point without the row.
> `agents/build-agent.md` states the requirement from the reading side; this is the authoring side
> of the same rule, and the convention has been followed in one feature Dev Summary and skipped in
> at least three (`IMP-0861`, `IMP-0811`).

**Change 4** — a new step before *Build & Pipeline Config Output*:

> **First, decide whether this feature needs its own configuration at all, and say which you chose.**
> The step below is written as though every feature were an independently built unit. It is not: the
> build and pipeline configuration is scoped to a Dataverse **solution**, and
> `verify-build-config.py` requires every gate under `scripts/` to be wired as a step in any
> configuration that exists — so a new slug's file cannot be feature-sized, it has to replicate the
> whole thing. No feature other than the original has ever had its own, across five change orders.
> So: if this feature deploys into a solution that already has a `config/<slug>-build.yml`, state in
> the Dev Summary whether this feature **amends that configuration** (same CI slug — the usual
> answer) or **needs its own** (and then budget for replicating every wired gate, not only the new
> ones). Resolving it silently in either direction is what this step exists to stop (`IMP-0836`).

**Change 5** — a new subsection in `skills/how-to-verify-a-platform-contract.md` §2, after
*A NEGATIVE claim needs the whole set*:

> #### A refusal is re-issued before it is recorded. Once is not a measurement
>
> A negative capability result — *the endpoint rejected this* — is **re-issued at least three times,
> at least two seconds apart**, before it may be written down as a contract fact. One refusal is one
> refusal.
>
> The ONS ArcGIS FeatureServer answers **overload with HTTP 400 `Invalid query parameters`**, not
> with 429. So a query that is genuinely unsupported and a query that arrived too fast return the
> identical response, and nothing in a single observation separates them. An identical query that
> 400'd back-to-back succeeded **8 times out of 8** when paced two seconds apart — after a design
> revision had already been written on the strength of the first one (`IMP-0841`).
>
> The corollary binds the happy path too: **any bulk harvest against such an endpoint retries a 400
> with backoff**, and only a persistent 400 is a failure.
>
> This is `§9`'s *one instance proves one instance* applied to a refusal rather than to a success,
> and it is the rung below the §2 rows above: those say where the evidence comes from, this says how
> many times you need it.

### Residual — what these changes do not cover

1. **Changes 3, 4 and 5 are prose, and prose has failed in this exact area before.** `IMP-0853`
   measured a case where the rule already existed in the right file and was ignored anyway. Change 3
   is nevertheless prose rather than a gate, because the mechanical form — "does this Dev Summary
   contain a row citing another Dev Summary for each shared warning" — has to read a markdown table
   for semantics, which this repository has measured at 48–100% false on five occasions. A second
   instance after change 3 ships is evidence for a different instrument, not for the same one.
2. **Change 1 leaves 103 markers invisible** across two spellings. Named, measured, and section 9's
   first decision.
3. **Change 2 does not make its gate green.** Named, and section 9's second decision.
4. **Change 5 states a number that nothing enforces.** A report can be checked against it by a
   reader; no gate reads how many times a request was issued.

---

## 7. What this review did NOT process, and why

**Eighteen entries close.** Six close against changes 1–5. The other twelve close with no file
change, because the work they describe already shipped and only the bookkeeping was outstanding:

| Finding | Why it closes with no change of its own |
|---|---|
| IMP-0798 | The commercial ledger backfill it records was carried out and verified against the source change orders |
| IMP-0800, IMP-0801 | The advisory row and the stale "0 vulnerabilities" clause were both fixed in the Dev Summary; the needle is the advisory id |
| IMP-0823 | A change order's open naming question, answered from the plan section that change order itself cites. A per-instance application of a rule both `plan-agent.md` and the clarifying-questions skill already state |
| IMP-0833 | A handoff named the wrong tool as the proven route; the receiving agent re-derived the right one live rather than trusting it. One instance, and the system behaving as designed |
| IMP-0839 | The exemption is already in `scripts/verify-shipped-content.py` — applied by the dispatch that found it |
| IMP-0842 | A research correction that landed before any build. No rule change; logged so the next session does not re-derive the wrong conclusion |
| IMP-0853, IMP-0854 | Both record this agent's own premise-grepping step firing correctly, at draft time rather than at apply time. Counted, not acted on |
| IMP-0858, IMP-0859 | The recursive-loop finding was triaged and the underlying race genuinely fixed with a trigger-scope filter. Closed with the live re-run as its re-observation; the *wording* of its disposition is routed above as IMP-0860 |
| IMP-0864 | This review's own re-measurement of IMP-0829, which is change 2 |

**Nine are deferred** with a return condition. Three more beyond the table below:
**IMP-0822** (grep a plan for a feedback note's decision language before pricing it) is one
instance with one near-neighbour, and the underlying question — which feedback item a reviewer's
"we settled on this" actually refers to — is commercial-agent's to resolve with you, not a rule;
**IMP-0825** (a review-document gate reporting a dangling self-reference against a citation of
*another* file's numbered section) asks in its own text for a precision measurement over the whole
review corpus before the suppression window is widened, and widening it wrongly would suppress the
real defect the check exists to catch; **IMP-0865**, logged by this review, records that nine of ten
review documents state their applied status only in their final section and not in their header,
which is how this review's own first reading of the queue went wrong.

| Finding | Why deferred | Revisit when |
|---|---|---|
| IMP-0826, IMP-0827 | Both are `observable_at: V4` — visible only when a human opened a form. Nobody in this session can re-run the observation, so they are drafted as deferrals from the start rather than as closures that would be claims | a human re-opens the Application form in DEV and confirms the control bindings and the read-only state |
| IMP-0812 | **Premise measured largely false.** `knowledge/technology/build-and-deploy.md` already carries the probe table showing `pac auth list` instant and `pac org who` hung, and already names the macOS Keychain prompt as a cause with no shell-visible trace. What is genuinely absent is one sentence — an active profile is not evidence a live call completes — and it is not worth a change of its own | the next review that touches that file, or a second instance |
| IMP-0828 | **Target measured wrong.** The finding proposes a fourth row in a table it places in `agents/development-agent.md`; the table is in `agents/pipeline-agent.md`, which `development-agent.md` points at rather than restating. The change is right and the address is not | re-drafted against the correct file |
| IMP-0818, IMP-0853, IMP-0854 | Three observations about this agent's own draft-time measurements. `IMP-0818`'s own text says one instance and a second would justify the edit; `IMP-0854`'s says the same. Six reviews have edited `agents/improvement-agent.md` in the last three days and a seventh small edit has a poor ratio of value to churn | a third instance, or the next review that edits that file for another reason |
| IMP-0803 | Needs the origin of a component name in a dispatch brief traced, which only the dispatcher can do | section 9, decision 3 |
| IMP-0837 | The gate is easy; the two orphaned skills it would fail need a wire-or-retire decision that is yours | section 9, decision 4 |

**Eight are routed to delivery agents.** Re-measured at draft time; each is a document or
configuration this agent does not own:

| Finding | Owner | The work |
|---|---|---|
| IMP-0799 | development-agent | A Pester test hardcodes a flow's container nesting depth and has now gone stale twice. Second instance — the altitude rule says derive the depth from the flow, not add a third hand-written level |
| IMP-0802 | development-agent | A warning count of 14 in one Dev Summary; the tool now prints 17 |
| IMP-0856 | development-agent | Two lines of prose in the pipeline configuration still say 21 settings rows; there are 22 |
| IMP-0857 | development-agent | An `npm ci` on this OneDrive-synced path exited 0 with the next step's binary not yet readable, costing a whole build. A retry or a post-install assertion belongs in the build configuration |
| IMP-0858, IMP-0860 | development-agent | The analyser still reports the recursive-loop finding after the fix, because its rule is structural and cannot see a trigger-scope change. The disposition in the Dev Summary says *Fixed* and should say *accepted* |
| IMP-0861 | development-agent | The citing rows change 3 makes obligatory, applied to the feature summaries that are missing them |
| IMP-0832 | plan-agent | A closed-dependency row reads as though one data source superseded three attributes; the analysis it cites covers one |

**One entry is excluded.** IMP-0862 was appended by a live test-agent session while this draft was
being written. It is `friction`, it does not keep any gate red, and folding a fresh finding into a
draft at gate time is how an amendment note becomes a false completion claim (`IMP-0333`). It is
stamped `excluded_by` naming this document and is the first entry the next review reads.

**One entry belongs to another review.** IMP-0855 is parked against
[2026-09-23 improvement review 7](2026-09-23-improvement-review-7.md). The remedy there is a
keyword, not a session, and this review did not re-derive it.

---

## 8. Retirement

**Candidate: `skills/how-to-write-a-deployment-runbook.md`.** Re-measured at draft time with one
command over every skill: it is named by no agent file, and by nothing else in the repository —
not even the layout diagram in `CLAUDE.md`. A second skill,
`skills/how-to-select-a-model.md`, is named only by that diagram, which loads nothing. Every other
skill in the directory is named by at least one agent.

Neither is retired in this review, because retiring a skill and building the gate that would have
caught it are one change, and the gate needs a decision first — decision 4 below.

**Constraints retired in this review: none. Constraints added: none.** Live and retired counts are
derived, not typed:

```bash
grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l
grep -rh '^| C-'   constraints/ --include='*.md' | wc -l
```

---

## 9. What you need to decide

**Settle one spelling for the deployment write markers, and decide what to do about the 84 written the other way**

**Problem** — The gate that proves a live deployment ran its access probe first is reading about one marker in five. Three different spellings of the same convention coexist in the deployment log, and the gate matches one of them.
**Suggested fix** — Approve the narrow change now, then have pipeline-agent pick one canonical spelling; either correct the historical entries or record the pre-2026-09-24 ones as accepted debt with an owner and an expiry date.
**What happens if you don't** — The gate keeps passing over roughly seven-eighths of the live writes it exists to check, and nothing in its output says so. This is the control that proves nobody wrote to a live environment without checking their access first.
[the measurement](docs/improvements/2026-09-24-improvement-review.md#L88)

---

**Decide what belongs in the commercial authorisation ledger**

**Problem** — The gate comparing authorised commercial acts against the ledger counts all eleven ledger rows on one side and only authorising acts on the other. One row records a change order being *closed*, which is not an authorisation. Fixing the act side, as this review proposes, leaves it at 10 against 11 and still red.
**Suggested fix** — Ask commercial-agent whether a `CLOSED` row belongs in that ledger at all, and make both sides of the comparison count the same thing.
**What happens if you don't** — A red gate that everyone knows is red for a benign reason is a gate people learn to skip, and the next genuinely missing authorisation looks exactly the same.
[the mapping](docs/improvements/2026-09-24-improvement-review.md#L166)

---

**Where did "EqualityMonitoring" come from?**

**Problem** — A dispatch instructed a deployment session to verify that two saved views were reachable after import. One is real. The other does not exist anywhere in the solution source, the Dev Summary or the test report.
**Suggested fix** — Trace it. If it names wanted future scope it needs a WBS task and a change-order decision; if it was a slip, nothing further is needed.
**What happens if you don't** — Either a piece of wanted scope is invisible to the plan, or dispatches keep being sent to verify components that were never built.
[the finding](logs/improvement-log.jsonl)

---

**Two written frameworks are read by nobody. Wire them or retire them?**

**Problem** — `skills/how-to-write-a-deployment-runbook.md` is referenced by nothing at all, and `skills/how-to-select-a-model.md` only by a diagram that loads nothing. A rule in a file no agent opens depends on someone remembering it.
**Suggested fix** — Retire the runbook skill, which is for a deliverable this project has not produced; fold the model-selection framework into `agents/lead-agent.md`, which makes that decision. Then a small gate — every skill is named by at least one agent — keeps it from happening again.
**What happens if you don't** — The next rule that belongs in either file lands there and is never read, which is the failure mode that produced both orphans.
[`skills/how-to-select-a-model.md`](skills/how-to-select-a-model.md)

---

## 10. The disposition was simulated before this draft was parked

Every status, needle, re-observation and deferral reason in sections 6 and 7 was applied to a
scratch copy of the log and the queue gate run against that copy, then the real file restored and
confirmed unchanged. The question a simulation answers is the one no amount of reading answers:
**do the triggers this review exists to clear actually clear?**

They do. Against the simulated disposition the queue reports **one** unread entry — the one
appended mid-draft and deliberately excluded — and **one** awaiting-approval entry, which belongs
to another review. The batch trigger that summoned this review is cleared.

The simulation also returned exactly six errors, and all six are the correct answer for a draft:
each says the file does not yet contain the substance its needle names, because nothing in section 6
has been written. They will clear as each change lands.

It caught one real defect. The needle for change 1 was originally the variable name `_STAMP`, which
**already matched** — `scripts/verify-provisioning-report.py` defines `ENTRY_STAMP`, and needles are
matched as raw substrings. A needle that matches before the change is made would have reported a
green closure against an unapplied change, which is the failure `evidence_grep` exists to prevent,
arriving through the needle itself. Renamed to `MARKER_STAMP`, re-grepped at zero.

---

## 12. Applied record — 2026-09-24

All five changes were applied **verbatim as approved**. Nothing was narrowed, substituted or
withheld. What follows is the re-verification required before applying, and the two places where the
draft's *prediction* of a measurement turned out to be wrong.

### The two measurement corrections

**Change 1 produces six findings on the real corpus, not four.** The draft predicted four, and all
four are present and adjudicated exactly as the draft's table states. The other two are:

- the **2026-09-06 PREFLIGHT-states-no-outcome** finding, which was already being reported before
  this change and belongs to a different check. The draft's "1 finding today → 4" figures counted
  only the missing-probe check; the gate's total was 2 before and is 6 now.
- a **new 2026-09-24 finding**, from a live DEV import logged into `logs/pipeline.log` at 11:47
  *after* this draft was parked. Adjudicated individually: **true positive.** That entry records a
  real `pac solution import` against DEV with `WRITE BEGUN` and `WRITE ATTEMPTED` markers and no
  `PREFLIGHT:` line — the session did ground-truth its access, but recorded it in prose rather than
  against the marker the constraint names. Five true positives out of five new findings.

Marker counts also moved with the corpus: the draft measured 7 markers seen before and 16 after;
the measurement at apply time is **7 before and 18 after**, across **7** write-bearing entries
rather than 6. The two extra markers are in the same post-draft entry.

**Change 2 turns its gate GREEN, where the draft said it would stay red.** This is the correction
that matters, because it inverts what the reviewer is deciding.

The draft reasoned that 10 acts against 11 ledger entries would still fail. It does not:
`verify-commercial-events.py` only fails when an **act has no ledger entry**, so reducing the act
count from 12 to 10 removes the last finding and the gate now exits 0. Measured both ways —
`git show HEAD:scripts/verify-commercial-events.py` exits 1 with "12 authorising act(s) … 11
ledger entry(ies)"; the applied version exits 0 with "10 … 11".

So the eleventh ledger row — `CE-0002`, action `CLOSED` — is still unaccounted for, and it is now
**invisible instead of red**. That does not weaken decision 2 in section 9; it sharpens it. The
gate no longer nags anyone about the mismatch, so if the two sides of that comparison are never
reconciled, nothing will raise it again.

### Re-verification performed before applying

| Assertion the draft rests on | How it was settled | Result |
|---|---|---|
| The three marker patterns are line-anchored and `MARKER_STAMP` does not exist | grep over the file | true; `ENTRY_STAMP` exists, `MARKER_STAMP` did not |
| `logs/pm.log` lines 3, 21, 22 and 32 are the four the bare pattern matches | grep with line numbers | true, all four at the stated lines and in the stated forms |
| `scripts/` and `.engine/scripts/` hold two separate copies of both scripts | `diff -q` plus `ls -l` | true — two regular files, byte-identical, now re-synced |
| The commercial gate was red before the change | executed the pre-change file from `git show HEAD:` | true, exit 1 |
| Each of the five evidence needles fits one line and does not match before its change | `grep -c` per needle | all five at 0 before, 1+ after |

The draft's own simulation had already caught the one needle defect worth catching: `_STAMP` matched
`ENTRY_STAMP` before the change was written. The applied name is `MARKER_STAMP`, re-grepped at zero
beforehand.

### Closures with no file change of their own

Eight entries close against artefacts other agents had already written, and four close against this
record. The markers below are what their `evidence_grep` needles point at.

```
APPLIED 2026-09-24 | IMP-0823 | a change order's open naming question, answered from the plan
  section that change order itself cites. A per-instance application of a rule both
  agents/plan-agent.md and skills/how-to-ask-clarifying-questions.md already state.
APPLIED 2026-09-24 | IMP-0833 | a handoff named the wrong tool as the proven route; the receiving
  agent re-derived the right one live rather than trusting it. One instance, and the system
  behaving as designed.
APPLIED 2026-09-24 | IMP-0853 | this agent's own draft-time premise-grep firing correctly, at
  draft time rather than at apply time. Counted, not acted on.
APPLIED 2026-09-24 | IMP-0854 | the second record of the same draft-time premise-grep working.
  Counted; the agent-file edit it proposes is deferred as IMP-0818.
```

### What moved in the queue

**18 closed, 10 deferred with a stated return condition, 7 routed to a delivery agent, 1 excluded.**

The draft's prose said "nine are deferred" and then named ten. The per-entry dispositions were
unambiguous and were applied as written; **ten** is the measured count, and the draft's summary
sentence was the thing that was off by one. IMP-0853 and IMP-0854 appear in both the closed table
and the deferred row about IMP-0818 — they close, and the *edit they jointly propose* is what
IMP-0818 defers.

Every routed and deferred entry carries a `deferred_reason` as well as a `revisit_when`, because a
bare `revisit_when` discharges nothing and would leave the batch trigger live.

### One navigational correction, disclosed

Six places in the body pointed the reader at "section 8" for the decisions; the decisions are
section 9, and section 8 is Retirement. `verify-review-document.py`'s `CROSS-REF` check does not
catch this, because section 8 *exists* — it is simply the wrong one. The six pointers were
re-numbered. No proposal, rule text or disposition was touched by that edit.

---

## 11. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-24-improvement-review.md

Findings processed: 36 NEW  →  8 clusters
Regression check:   5 prior changes audited, 1 class recurred (prose change, escalated in place)
Proposed:           0 constraints (cap 3), 2 gates/scripts, 1 skill edit,
                    2 agent-file edits, 0 retirements
Altitude calls:     2 generalised from instance to class, 3 left as notes
Digest:             will regenerate — 861 entries, 8 new lessons

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```
