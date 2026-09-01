# Capability Design — Operating-Cost Reduction (2026-09-01)

**Status:** DRAFT — not authorised. Requires `APPROVE IMPROVEMENTS` per workstream.
**Scope:** `system` only. Non-billable, outside the contracted WBS ([`C-COM-002`](constraints/commercial/commercial-constraints.md)).
**Authorising basis:** capability mode, per [`agents/lead-agent.md` L33](agents/lead-agent.md#L33) routing row and [`agents/improvement-agent.md` L73-L91](agents/improvement-agent.md#L73).
**Relationship to the earlier design:** this document is a **successor to five workstreams** of
[`2026-08-31-capability-design-agent-system-optimisation.md`](docs/improvements/2026-08-31-capability-design-agent-system-optimisation.md),
not a replacement for it. WS-A, WS-C, WS-G and WS-K of that document are already applied or
withheld by reviews 4, 5 and 6. WS-N below **supersedes its WS-B**; everything else here is new.

---

## 0. Conclusion first

**The dispatching brief named five problems. Three of them measured differently than stated, and
the measurements changed what should be built.** Two are worth building as described, one is worth
building in a corrected form, one is a cheap regression guard with no current instance, and one
should not be built at all because its premise does not hold.

Nothing here proposes a new constraint row. Four of the five workstreams are script or file
changes; the fifth is a withholding.

**This document does not reopen the improvement-agent tier question.** [`config/models.yml` L216-L243](config/models.yml#L216)
measured and rejected splitting this agent's apply phase to a cheaper tier on 2026-09-01, with
hard numbers. "Reduce improvement-agent's share of system usage" is answered here by shrinking
**what reaches this agent** — its own prompt, the digest it reads, and the false gate findings its
reviews have to explain away — never by moving it down a tier. A future reader finding this
document should read it as complementary to that decision, not as an attempt to revisit it.

---

## 1. Premises re-measured before drafting

Every figure below was re-derived on 2026-09-01 against this tree. The command is recorded beside
each number, because a bare integer in a design document cannot be falsified by a later reader —
that is the defect this project has now recorded three times against the previous design document.

| Brief's claim | Measured | Verdict |
|---|---|---|
| The digest is "unboundedly growing, no pruning/rotation mechanism" | [`MAX_PER_SECTION = 20`](scripts/generate-known-failure-modes.py#L107) already caps every section, and the appendix already exists and is `--check`ed | **Partly false.** The count is bounded; the *lesson text* is not — mean lesson length rose from 256 to 583 characters (first six days vs. last six days of the log, n=46 and n=201). That is the real driver, and it is a different fix. |
| `agents/WORKFLOW.md` and `agents/improvement-agent.md` carry long inline incident narrative | 42 lines carrying an `IMP-` id in [improvement-agent.md](agents/improvement-agent.md) (43.4 KB), 19 in [WORKFLOW.md](agents/WORKFLOW.md) (32.4 KB) | **True.** Build it. |
| Two gate defects self-diagnosed and unfixed | Both confirmed live and both `reviewer-deferred` with a `revisit_when` this dispatch satisfies | **True, with a correction** — see WS-P. |
| No lint catches a load-bearing comment beside a `tier:` key in `config/models.yml` | **0** comments currently sit immediately above `tier:` / `escalate_to_strategic_when:` / `de_escalate_to_mechanical_when:` | **True that no lint exists; false that anything trips it today.** A regression guard, not a fix. |
| Three rules are each restated in `CLAUDE.md`, `WORKFLOW.md` **and** `lead-agent.md` | The never-paste rule appears in CLAUDE.md and WORKFLOW.md only (twice in each, never in lead-agent.md); the report-format rule appears in CLAUDE.md, lead-agent.md and improvement-agent.md, never in WORKFLOW.md; the WBS rule appears once each in CLAUDE.md and lead-agent.md, and in WORKFLOW.md only as two diagram labels | **False as stated.** No rule is stated in the three files named. See WS-R. |

---

## WS-N — Bound the digest by lesson LENGTH, and track the appendix

**Supersedes WS-B of the 2026-08-31 design.** WS-B proposed an age-and-status cutoff moving old
single-instance findings to an appendix. Both halves of that proposal are already done: the
appendix exists and the per-section cap is 20. A prior measurement found WS-B's recommended 60-day
cutoff selected **0 of 543** lessons.

**Problem, restated from measurement.** The digest is 621 lines / 124.6 KB, read at activation by
[build-agent](agents/build-agent.md#L32), pipeline-agent, pm-agent, acceptance-agent, commercial-agent
and test-agent. Its 20-lesson-per-section cap bounds *how many* lessons render; nothing bounds *how
long each one is*, and lesson length has more than doubled over the life of the log (256 → 583 mean
characters). Total lesson text in the log is 300,571 characters. A future 800-entry log at today's
mean writes a materially larger digest than an 800-entry log at the original mean, with the same cap.

**Second, cheaper problem.** [`logs/known-failure-modes-appendix.md`](logs/known-failure-modes-appendix.md)
is **0 tracked files** (`git ls-files` returns nothing) and is not gitignored — it has simply never
been added. The digest points readers at it **6 times**. Anyone cloning this repository, and CI,
gets six dangling pointers to a 234 KB file that is not there.

**Requirement.**
1. `git add` the appendix, so the digest's six pointers resolve for every reader. This is one
   command and is independent of everything else in this document.
2. Add a **rendered-length budget per lesson** in the digest (not in the log): a lesson longer than
   a declared character budget renders truncated at a sentence boundary with a pointer to its full
   text in the appendix, which already carries every capped lesson in full. The log keeps the whole
   lesson — nothing is lost, only relocated, exactly as the appendix already works for capped ones.
3. The generator prints the digest's total byte size on every run, so growth is visible rather than
   inferred.

**Mechanical verification.** `python3 scripts/generate-known-failure-modes.py --check` exits 0;
`--selftest` gains a case proving a lesson over budget is truncated **and** that its full text is
present in the appendix; digest byte size before and after is reported in the review document as a
measured pair, not an estimate.

**Files.** `scripts/generate-known-failure-modes.py`, `logs/known-failure-modes.md` (regenerated),
`logs/known-failure-modes-appendix.md` (regenerated **and** tracked).

**Decision this document cannot make:** the character budget. It must be chosen by running the
generator at several candidate values and reading what gets truncated — a budget that truncates the
long platform-contract lessons mid-mechanism is worse than no budget, because those lessons are the
ones whose detail is load-bearing. Recommend measuring at 400, 600 and 800 characters and reporting
the three digest sizes plus a sample of what each truncates, rather than picking a number here.

---

## WS-O — Move incident narrative out of the two most-read agent files

**This is the most direct lever in this document on improvement-agent's own per-dispatch cost**,
and it does not touch the tier.

**Problem.** [`agents/improvement-agent.md`](agents/improvement-agent.md) is 43.4 KB / 685 lines and
is loaded in full on **every** improvement-agent dispatch, at the most expensive tier in the roster.
42 of its lines carry an `IMP-` id, and most sit inside multi-paragraph incident narratives —
`IMP-0333`'s spend-limit account, `IMP-0301`'s six-of-twelve interruption, `IMP-0517`'s routed-work
reversal, `IMP-0426`'s two false root causes. Each is a *rule* of one or two sentences wrapped in a
*story* of one or two paragraphs. [`agents/WORKFLOW.md`](agents/WORKFLOW.md) is 32.4 KB / 529 lines
with the same shape at 19 marker lines, read by lead-agent at every session start.

**Requirement.** Apply the technique already proven by WS-C of the earlier design, which moved 55
narrative comment blocks out of the build config into a history document: each narrative block is
replaced in the agent file by **the rule in imperative form plus a one-line pointer** into a new
`docs/improvements/agent-instruction-history.md`, which carries the moved prose verbatim under a
heading naming the finding id. The rule stays where the agent reads it; the story moves.

**The line that must not be crossed.** A rule may lose its narrative and must never lose its
*imperative*. This project has already measured what happens when a mandatory step is softened into
something discoverable: an agent given a task squarely inside a skill's trigger loaded it **0 of 3**
times, against **2 of 2** when told to. So the acceptance test for this workstream is not "the file
is shorter" — it is **"every instruction that was mandatory before is mandatory after, in the same
step, in the same imperative voice."**

**Mechanical verification.** Before and after, `grep -c 'IMP-[0-9]'` on each file and the byte size,
both reported. Then a **live fixture**, because that is the only thing that answers the question
above: dispatch a real improvement-agent against a small scoped task under the rewritten file and
confirm it performs the activation steps whose narrative was removed — specifically the step-6
`reviewed_in` stamp and the step-8 re-verification, the two most narrative-heavy and most
consequential. If the fixture shows a dropped step, the rewrite is wrong and is reverted, not tuned.

**Files.** `agents/improvement-agent.md`, `agents/WORKFLOW.md`, new
`docs/improvements/agent-instruction-history.md`.

**Prerequisite check, learned the expensive way.** Before moving any block, grep
`logs/improvement-log.jsonl` for `evidence_grep` needles pointing into the text being moved. A
needle is a claim about *where* a substance lives, and a relocation silently falsifies it until the
next run of a HARD build gate. Exactly this broke a build during the WS-C relocation, on one needle
out of 426 applied entries.

**Decision this document cannot make:** whether `agents/WORKFLOW.md` is in scope for the same
dispatch as `agents/improvement-agent.md`. They are different readers (lead-agent vs.
improvement-agent) and different risk profiles — WORKFLOW.md governs the handoff contract every
agent depends on. Recommend improvement-agent.md first, measured, before WORKFLOW.md is touched.

---

## WS-P — Fix the two self-diagnosed gate defects

Both findings are `reviewer-deferred` with an owner and a `revisit_when` that **this dispatch
satisfies** — each names "the next improvement review that processes" the relevant entries or file.
Neither is being reopened against a reviewer's wishes; both were deferred *to* a pass like this one.

### P1 — a declared `excluded_by` field

**Problem.** Activation step 2 requires a review to name the findings it deliberately excluded from
scope. Doing so currently trips one spurious warning per excluded id — 4 of the 9 warnings on the
current queue read are this shape, against a review that did exactly the right thing.

**Correction to the finding's own diagnosis.** It names `check_missing_stamps()`. No such function
exists; the code is [`check_citation_stamps()` at L1464](scripts/verify-improvement-log.py#L1464).
The substance is right and the identifier is wrong — recorded here because a later reader following
the finding to a function name will not find it.

**Why a declared field rather than a fifth prose exemption.** The selftest already carries three
named exemptions for innocent citation positions (`deferral-table-citation-must-not-warn`,
`prose-non-scope-declaration-must-not-warn`, `reviewer-deferred-citation-must-not-warn`). "Cited in
order to declare it out of scope" would be the fourth. A predicate that subtracts known-innocent
positions grows one exemption per shape forever and is wrong by construction on the shapes nobody
has met yet — which is the reasoning that produced the `appended_by` field
([L503](scripts/verify-improvement-log.py#L503)). This is the same altitude, for the same reason.

**Requirement.** An `excluded_by` field taking one path or a list, validated exactly as
`appended_by` is (naming a document that does not exist is a HARD error), and an entry carrying it
is treated as innocently cited.

### P2 — a fail-closed status-token allowlist

**Problem.** [`AWAITING_RE` at L197](scripts/verify-review-document.py#L197) matches the literal word
`AWAITING` and nothing else, so a `DRAFT` status header above a populated Applied section passes
clean — which is precisely the contradiction the check was built to catch.

**Two corrections the corpus measurement forces, and this is why the corpus rule exists.** Measured
across all **65** review documents:

- The proposed token set (`AWAITING, DRAFT, PARKED, APPLIED, SUPERSEDED, WITHDRAWN`) **omits
  `REVISION`**, which is in live use. A fail-closed allowlist as proposed would report that document
  as carrying an unknown token — a false positive on day one.
- The proposal does not account for [`STRUCK_RE` at L199](scripts/verify-review-document.py#L199).
  20 of 65 documents use a struck-through `~~AWAITING` header, and striking through is this
  project's convention for "this status is superseded". The allowlist must compose with that rule,
  not replace it, or it fires on 20 correct documents.

**Requirement.** Replace the single-synonym match with an allowlist that fails closed on an
unrecognised token, includes `REVISION`, and preserves the existing struck-through semantics.

**Mechanical verification, for both halves.** `--selftest` proving each can fail, then a run against
the real corpus — all 555 log entries for P1, all 65 review documents for P2 — with every finding
adjudicated true or false positive one at a time and the precision stated as "N findings, K true
positives" in the review document. A green selftest is a can-it-fail proof and nothing more.

**Pre-existing debt, declared.** `verify-review-document.py` currently exits 1 with 5 findings
across 65 documents (3 cluster-count, 1 cross-ref, 1 lost-deferral), all in documents from 08-21 to
08-31. None is introduced by this work and none is this dispatch's to fix. The P2 change must be
measured against that baseline, not credited with clearing it.

**Files.** `scripts/verify-improvement-log.py`, `scripts/verify-review-document.py`,
`skills/how-to-log-an-improvement.md` (the `excluded_by` field must be documented where authors
read the schema, or the field exists and nobody uses it).

---

## WS-Q — Lint for a load-bearing comment beside a propagating key

**Problem.** [`config/models.yml` L5-L22](config/models.yml#L5) documents, in its own header, a real
failure this project has already paid for: `scripts/generate-subagents.py` keeps values and discards
comments, so a rule written in a comment beside `tier:` never reaches the agent that must obey it.
The header says `--check` stays green either way, and it is right — no gate can distinguish a
dropped comment from one never meant to propagate.

**Measured, and stated plainly: 0 instances exist today.** The historical instance was fixed. This
is a **regression guard**, not a repair, and it must be described that way in its own finding
message or the first person to see it fire will assume it is noise.

**Requirement.** A check reporting any comment line immediately above `tier:`,
`escalate_to_strategic_when:` or `de_escalate_to_mechanical_when:` as a **SOFT** reminder to move
load-bearing text into the string value. SOFT is deliberate: a comment beside those keys is
sometimes legitimately just a note to a human, so this can never be a HARD block without generating
exactly the false positives that teach people to route around a gate.

**Mechanical verification.** `--selftest` with a fixture proving it fires; a run against the real
`config/models.yml` reporting **0**, stated as 0 and not as a clean run — a gate reporting zero
against a corpus is only trustworthy when you know the corpus is genuinely empty, and here it is,
by the measurement above.

**Decision this document cannot make:** whether this earns a place as a build step at all. It
guards a file that changes rarely, and the wired-step budget is not free. Recommend shipping it as
a standalone script first and deciding on wiring after it has run a few times.

---

## WS-R — WITHHELD: consolidating the "triple-stated" rules

**Not proposed for building.** The premise does not survive measurement, and a consolidation built
on a wrong map of where a rule lives would move the wrong text.

The brief describes three rules each stated in `CLAUDE.md`, `agents/WORKFLOW.md` and
`agents/lead-agent.md`. Measured, **no rule is stated in those three files**:

| Rule | Where it actually is |
|---|---|
| Never paste document contents | [CLAUDE.md L63](CLAUDE.md#L63) and [L122](CLAUDE.md#L122); [WORKFLOW.md L46](agents/WORKFLOW.md#L46) and [L489](agents/WORKFLOW.md#L489). Not in lead-agent.md at all |
| Reviewer report format | [CLAUDE.md L72](CLAUDE.md#L72); [lead-agent.md L362](agents/lead-agent.md#L362) and [L385](agents/lead-agent.md#L385); [improvement-agent.md L654](agents/improvement-agent.md#L654) and [L685](agents/improvement-agent.md#L685). Not in WORKFLOW.md |
| WBS-first routing | [CLAUDE.md L94](CLAUDE.md#L94); [lead-agent.md L47](agents/lead-agent.md#L47). In WORKFLOW.md only as two diagram labels, which are not a restatement |

**There is a real finding inside the wrong one**, and it is smaller and cheaper than the workstream
proposed: two of the three rules are duplicated **within a single file** — the never-paste rule
twice inside CLAUDE.md, the report-format rule twice inside both lead-agent.md and
improvement-agent.md. An intra-file duplicate is unambiguous to remove and costs nothing to verify.
That is folded into WS-O, where those files are already open, rather than given a workstream of its
own.

**And the reason not to consolidate the genuine cross-file repeats.** Each is a *deliberate*
activation-step restatement. The report-format rule sits in two agent files precisely because a rule
named only in `CLAUDE.md` and absent from any activation sequence is a rule that depends on
remembering — which this project has already paid for once, when an agent that knew the reporting
rule wrote a long report without loading the file. Replacing an activation step with a citation to
another file is the same substitution measured at 0-of-3 compliance under WS-G. The duplication is
the mechanism, not the waste.

---

## 2. Anti-bloat accounting

| Limit | This document |
|---|---|
| New constraints (cap 3) | **0**. Nothing here is a constraint row; four workstreams are script or file changes and one is a withholding |
| Every new constraint cites its justification | n/a — none proposed |
| Retirement considered | **Yes.** Candidate named: **WS-B of the 2026-08-31 design document**, superseded by WS-N's measurement that its two mechanisms already exist and its recommended cutoff selects 0 of 543 lessons. No **constraint** retirement candidate found — checked against 82 live and 10 retired rows (`grep -rh '^| C-' constraints/ --include='*.md' | wc -l`), and nothing in this document's subject area touches a constraint row |
| Mechanically executable verification | Every workstream states a command; WS-O additionally requires a live fixture because its risk is behavioural and no command can measure it |
| No silent caps | Section 3 names what this document deliberately leaves alone |

---

## 3. What this document deliberately does not touch

- **The improvement-agent tier split.** Closed by [`config/models.yml` L216-L243](config/models.yml#L216) on 2026-09-01. Not reopened, and section 0 says so for future readers.
- **The 4 unread findings on the queue** (`IMP-0549`–`IMP-0552`). They are a queue matter, not a capability matter, and this dispatch is capability mode. Naming them here is the no-silent-caps rule, not a claim to have processed them — and it is worth noting that naming them is itself what trips the 4 spurious warnings WS-P/P1 exists to fix.
- **The 120 `reviewer-deferred` findings.** Each carries a reason a human accepted. Two of them (the WS-P pair) are acted on here only because their own `revisit_when` names this exact circumstance.
- **The 5 pre-existing `verify-review-document.py` findings.** Declared in WS-P, owned by nobody in this dispatch.

---

## 4. What you need to decide

**Approve WS-N (digest length budget + track the appendix)?**

**Problem** — The digest's per-section cap bounds lesson *count* but not lesson *length*, and mean lesson length has more than doubled; separately its 234 KB appendix is untracked while the digest points at it six times.
**Suggested fix** — Track the appendix now, add a per-lesson rendered-length budget with the full text kept in the appendix, and print the digest's byte size on every generator run.
**What happens if you don't** — Six pointers stay dangling for every reader who is not on this machine, and the largest static read in the system keeps growing on an axis nothing measures.
[`scripts/generate-known-failure-modes.py` L107](scripts/generate-known-failure-modes.py#L107)

---

**Approve WS-O (move incident narrative out of improvement-agent.md, and WORKFLOW.md separately)?**

**Problem** — The most expensive agent in the roster loads 43.4 KB of its own instructions on every dispatch, much of it incident narrative wrapping one-sentence rules.
**Suggested fix** — Move the stories to a history document and keep the rules, in imperative voice, in the agent file; verify with a live fixture that no mandatory step became optional.
**What happens if you don't** — The single most direct lever on this agent's cost that does not touch its tier stays unused, and the file keeps growing with every review that adds a worked example.
[`agents/improvement-agent.md`](agents/improvement-agent.md)

---

**Approve WS-P (the two gate fixes)?**

**Problem** — Naming deliberately-excluded findings trips four spurious warnings, and a review document whose header says DRAFT above a populated Applied section passes the check built to catch exactly that.
**Suggested fix** — A declared `excluded_by` field, and a fail-closed status-token allowlist that includes `REVISION` and composes with the struck-through convention.
**What happens if you don't** — Every future review pays to explain away warnings it earned by following the rules, and the stale-header check keeps returning a clean line on the defect it exists to find.
[`scripts/verify-review-document.py` L197](scripts/verify-review-document.py#L197)

---

**Approve WS-Q, knowing it currently finds nothing?**

**Problem** — A rule written in a comment beside a `tier:` key silently never reaches the agent, and nothing catches it.
**Suggested fix** — A SOFT standalone check flagging comments adjacent to the three propagating keys, shipped unwired.
**What happens if you don't** — The failure recurs silently the next time someone annotates that file, exactly as it did once already; the cost of not building it is low but the cost of building it is lower.
[`config/models.yml` L5-L22](config/models.yml#L5)

---

**Choose the character budget for WS-N.**

**Problem** — The budget cannot be chosen from a desk; too tight truncates the long platform lessons whose detail is the whole value.
**Suggested fix** — Run the generator at 400, 600 and 800 characters and pick from the three measured digest sizes and samples of what each truncates.
**What happens if you don't** — WS-N either ships an unmeasured number or does not ship; this is the one open decision that blocks a workstream rather than accompanying it.
[`logs/known-failure-modes.md`](logs/known-failure-modes.md)

---

## 5. Verification reached

Everything in this document is **V1** — measurement against the tree and the log. Nothing has been
applied; no file outside this document has been edited.

Executed: `verify-improvement-log.py --check` (exit 0, 555 entries, 9 warnings),
`generate-known-failure-modes.py --check` (exit 0), `verify-review-document.py` (exit 1, 5
pre-existing findings across 65 documents), plus the counts recorded inline in section 1.

**Not verified:** every workstream's own precision measurement, which by this project's rule must be
run against the real corpus at application time and not before — a draft's numbers can move under
it between the gate opening and the keyword arriving.
