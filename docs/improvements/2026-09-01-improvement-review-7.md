# Improvement Review 7 — Operating-Cost Reduction (2026-09-01)

**Status: APPLIED — 2026-09-01, on `APPROVE IMPROVEMENTS`.** Three of four approved workstreams are
on disk in full. WS-O is applied for `agents/improvement-agent.md` and **deliberately not applied to
`agents/WORKFLOW.md`** — see section 6, which names the owner and the return condition.

**Authorising design document:**
[`2026-09-01-capability-design-operating-cost-reduction.md`](docs/improvements/2026-09-01-capability-design-operating-cost-reduction.md)
**Scope:** `system`, non-billable, outside the contracted WBS (`C-COM-002`).

---

## 0. Conclusion first

**The digest that six agents read at activation is 16,643 bytes smaller, the most expensive agent's
own prompt is 3,865 bytes smaller, two gate defects are fixed, and one regression guard is in place.**
Nothing was lost: every truncated lesson is in the appendix, and the appendix is now tracked.

Three things the application itself surfaced are logged rather than silently fixed — one of them a
gate that exits 0 having checked nothing.

---

## 1. Regression check — did the last reviews' changes work?

| Prior change | Held? |
|---|---|
| Review 6 — `.claude/hooks/protect-system-rules.py` + settings wiring + agent-file note | **Yes.** Hook on disk, executable, 10,770 bytes. No `live-verification-capability` recurrence |
| Review 5 — `skills/how-to-promote-a-finding.md` §4, mandatory-vs-elective bullet | **Yes.** Needle `becomes an ELECTIVE one` resolves |
| Review 4 — appended `IMP-0549`–`IMP-0552` | Consistent: those were appended, not applied, and remain open |

**One class recurred: `gate-fires-on-nothing` (x11)**, as `IMP-0557` and `IMP-0558`. Both were
appended *by* review 6 and both were prose-free from the start — they proposed mechanical remedies.
This review implements both, which is the correct altitude: the recurrence is not evidence a prose
fix failed, it is two instances arriving together and being answered mechanically at once.

---

## 2. Changes applied

### A1 — [`scripts/verify-models-yml-comments.py`](scripts/verify-models-yml-comments.py) (new) · WS-Q

SOFT lint reporting a comment directly above `tier:`, `escalate_to_strategic_when:` or
`de_escalate_to_mechanical_when:` in [`config/models.yml`](config/models.yml#L5), where the YAML
loader discards it and the dispatched agent never sees it.

**Measured: 8 selftest checks green (proving it fires, and that it stays silent on a non-propagating
key, a multi-line block reported once, and no comment at all); 0 findings against the real
`config/models.yml`.** Zero is the honest and correct result — the historical instance (`IMP-0310`)
was fixed before this script existed. This is a regression guard, and the script's docstring says so
in those words so the first person to see it fire does not read a human note as an error.

SOFT and unwired, deliberately: a comment beside those keys is sometimes legitimately a note to a
human, and a HARD block would manufacture exactly the false positives that teach people to route
around a gate.

### A2 — [`scripts/verify-improvement-log.py`](scripts/verify-improvement-log.py) · WS-P/P1

New declared `excluded_by` field — `excluded_by_paths()`, `resolved_excluders()`, validated exactly
as `appended_by` (naming a document that does not exist is a HARD error) and honoured in
`check_citation_stamps()`.

**Corpus measurement, all 557 entries: citation-stamp warnings 4 → 0, total warnings 9 → 5.** The
four removed are `IMP-0549`–`IMP-0552`, which improvement review 6 named *in order to declare them
out of scope* — all four true positives for removal. The five remaining are the `corrects` shape, a
different check, correctly retained. **68 selftest fixtures green**, including the over-suppression
control proving a *second* citing review still warns, and a `_MUST_NOT_CONTAIN` row — without which
the suppression case would pass on a no-op change, since exit code stays 0 either way.

**Why a declared field and not a fourth prose exemption:** the predicate already carries three
heuristics for innocent citation positions. A check that subtracts known-innocent positions grows one
exemption per shape forever and is wrong by construction on shapes nobody has met — the reasoning
that produced `appended_by`, applied a third time.

### A3 — [`scripts/verify-review-document.py`](scripts/verify-review-document.py) · WS-P/P2

`AWAITING_RE` replaced by a fail-closed allowlist: `PRE_APPROVAL_TOKENS`, `SETTLED_TOKENS` and
`status_verdict()`, composed with the existing struck-through convention.

**The corpus measurement changed the design twice, and this is why the rule exists:**

- `REVISION` is in live use ([`2026-08-24-improvement-review-6.md`](docs/improvements/2026-08-24-improvement-review-6.md)) and was **absent from the token set the finding proposed**. Shipped as proposed, a fail-closed allowlist would have reported a correct document on day one.
- 20 of 65 documents carry a struck-through `~~AWAITING` header. `STRUCK_RE` had to be **composed with**, not replaced, or the change fires on all 20.

**Adjudicated 5 of 5 on purpose-built fixtures:** the `DRAFT`-above-Applied header that escaped now
FIRES; an unknown token FIRES (fail-closed); struck-through, `REVISION` and plain `APPLIED` stay
silent. **Against the real corpus: 0 new findings across 66 documents**, with the 5 pre-existing
findings (3 cluster-count, 1 cross-ref, 1 lost-deferral, all in documents dated 08-21 to 08-31)
unchanged. Those are pre-existing debt, not this review's to fix.

### A4 — [`scripts/generate-known-failure-modes.py`](scripts/generate-known-failure-modes.py) · WS-N

Three changes: a per-lesson rendered-length budget, a third appendix part carrying every truncated
lesson in full, and digest byte-size reporting on every run. Also `import re`, which the file had
never had.

**The budget value was the reviewer's delegated decision, and the measurement decided it:**

| Budget | Digest | vs unbudgeted | Lessons truncated |
|---|---|---|---|
| off | 124,736 B | — | 0 |
| 400 | 95,421 B | −23.5% | 109 |
| **600 (chosen)** | **108,090 B** | **−13.3%** | **65** |
| 800 | 118,455 B | −5.0% | 27 |

**400 was rejected because it removes the remedy, not the story.** Inspected against the
platform-contract lessons flagged as load-bearing: at 400, `IMP-0276` loses the entire
GET→mutate→PUT-whole-object instruction; `IMP-0108` loses *"assert a callbackregistration row
exists"*, the whole verification step; `IMP-0467` loses *"Filter the nulls OUT"*, the whole fix. Those
lessons become a problem statement with no answer, which is worse than not rendering them. **800
truncates 27 lessons for 5%** — not worth a truncation mechanism. **At 600, five of those six
load-bearing lessons render whole**, and the sixth (`IMP-0116`) loses only a closing sentence that
restates what precedes it.

Truncation lands on a sentence boundary; a lesson with no boundary inside the budget renders whole,
because cutting *"never use PUT with a partial body"* mid-clause inverts the instruction.

**Appendix now tracked** — it was 0 tracked files while the digest pointed at it 71 times.

**16 selftest checks green**, including *"every TRUNCATED lesson appears in the appendix in full"* —
**65 truncated, 0 missing.**

### A5 — [`agents/improvement-agent.md`](agents/improvement-agent.md) · WS-O (partial)

Incident narrative moved to [`agent-instruction-history.md`](docs/improvements/agent-instruction-history.md);
every rule kept its imperative voice, its numbered step and its `IMP-` citation. **38,577 → 34,712
bytes (−10.0%), 608 → 575 lines**, paid back on every dispatch of the most expensive agent in the
roster.

**The prerequisite that broke a build last time was run first:** 18 registered `evidence_grep`
needles point into the two WS-O target files, 13 into this one. **All 13 verified present after the
rewrite; 0 broken.**

**The acceptance test was a live fixture, because no command can measure it.** WS-O's risk is not
that the file gets shorter — it is that a mandatory step quietly becomes optional, the substitution
measured at 0-of-3 compliance in review 5. A fresh `improvement-agent` was dispatched read-only and
asked to state its own obligations. It correctly and specifically stated the step-6 `reviewed_in`
stamp (naming that `status` stays `NEW` and `applied_by` does not yet exist), every step-8
re-verification including the scratch-copy simulation and the max-id re-read, the execute-don't-read
rule with its reasoning, and the new fail-closed corpus-enumeration rule — closing with *"All four are
covered by my instructions; none required filling from general knowledge."*

Also folded in here, from `IMP-0559`: two new capability-mode bullets — grep `docs/improvements/` for
an existing design document before authoring one, and re-measure a brief's premises, especially
negative ones.

### A6 — derived counts

`verify-derived-counts.py` caught two figures this review's own changes drifted: the `verify-*.py`
count (54 → 55) and the digest line count (618 → 622). Both corrected. **7 → 5 drifted claims**; the
remaining 5 are pre-existing and not this review's.

---

## 3. Findings closed

| Finding | Disposition |
|---|---|
| `IMP-0557` | APPLIED — the `excluded_by` field (A2) |
| `IMP-0558` | APPLIED — the status-token allowlist (A3) |
| `IMP-0559` | APPLIED — the two capability-mode bullets (A5) |
| `IMP-0560` | APPLIED — folded into A3; `REVISION` included, `STRUCK_RE` composed with |

Both `IMP-0557` and `IMP-0558` were `reviewer-deferred`. Neither was reopened against the reviewer's
wishes: each carried a `revisit_when` naming exactly this circumstance.

## 4. Findings appended

| Finding | Why |
|---|---|
| `IMP-0561` | `verify-review-document.py --only` with a bare filename prints a usage error and **exits 0** — a gate that checked nothing reporting clean. **Not fixed here:** WS-P's approved scope was the allowlist, and changing a gate's exit code deserves its own keyword |
| `IMP-0562` | The budget sweep initially returned four identical rows because `budget=LESSON_BUDGET` bound the constant as a default argument at def time. Caught only because all four rows matched |
| `IMP-0563` | The truncation notice promised text the appendix did not hold, because the appendix served one relocation mechanism and a second was added on the digest side. Caught by an assertion written in the same change |

---

## 5. Anti-bloat accounting

| Limit | This review |
|---|---|
| New constraints (cap 3) | **0** |
| Retirement considered | **Yes** — WS-B of the 2026-08-31 design document is superseded by WS-N and named as retired in the design document. No constraint retirement candidate: 82 live / 10 retired rows checked, none in this subject area |
| Verify scripts | 54 → **55**, registry updated in the same change |
| Mechanical verification | Every change ran `--selftest` **and** a real-corpus measurement with per-finding adjudication |

---

## 6. Deliberately not done, with owners

**`agents/WORKFLOW.md` — the second half of WS-O.** Applied to `improvement-agent.md` only. The design
document named this as a decision it could not make and recommended *"improvement-agent.md first,
measured, before WORKFLOW.md is touched"*; that measurement now exists (−10.0%, fixture green), and
the remaining work is a separate dispatch. Three reasons to separate it: `WORKFLOW.md` governs the
handoff contract **every** agent depends on; its reader is `lead-agent`, the root session rather than
a bounded dispatch, so it needs its own fixture rather than inheriting this one's; and 5 registered
needles point into it. **Owner: improvement-agent, next dispatch. Return condition: a
`WORKFLOW.md`-scoped WS-O dispatch with its own lead-agent fixture.**

**`IMP-0561`'s exit-code fix** — logged, not applied. Reason in section 4.

**The 5 pre-existing `verify-review-document.py` findings** and the **5 remaining derived-count
drifts** — pre-existing debt, owned by nobody in this dispatch (`C-COM-002`).

**The 4 unread findings `IMP-0549`–`IMP-0552`** — out of scope, and now declared as such with
`excluded_by`, which is the field this review built.

---

## 7. Verification executed

| Check | Result |
|---|---|
| `verify-improvement-log.py` (bare, authoritative) | **OK** — 560 entries, 125 NEW, 433 APPLIED, 2 REJECTED |
| `verify-improvement-log.py --selftest` | **OK** — 68 fixtures |
| `verify-improvement-log.py --check` | 5 warnings (all `corrects` shape; was 9) |
| `verify-review-document.py --selftest` | **OK** — 23 assertions |
| `verify-review-document.py` (66 documents) | 5 pre-existing findings, 0 new |
| `generate-known-failure-modes.py --selftest` | **OK** — 16 checks |
| `generate-known-failure-modes.py --check` | **exit 0** |
| `verify-models-yml-comments.py --selftest` | **OK** — 8 checks |
| `verify-models-yml-comments.py` | 0 findings (correct: regression guard) |
| `evidence_grep` needles into `improvement-agent.md` | **13 of 13 intact** |
| WS-O live fixture | **PASS** — all four mandatory steps stated unprompted |

**Level reached: V1** for every script change (executed against the real corpus), and **V4-equivalent
for WS-O** — a real dispatched agent read the rewritten file and behaved correctly.

**Not verified:** whether the digest reduction changes any agent's behaviour in practice. The bytes
are measured; the effect on a downstream dispatch is not, and no cheap measurement of it exists.
