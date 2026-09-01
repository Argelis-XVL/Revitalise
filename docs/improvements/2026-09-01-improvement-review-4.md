# Improvement Review — 2026-09-01 (4)

**Mode:** capability. Authorising artefact:
[`docs/improvements/2026-08-31-capability-design-agent-system-optimisation.md`](2026-08-31-capability-design-agent-system-optimisation.md),
workstreams [WS-C](2026-08-31-capability-design-agent-system-optimisation.md#L82) and
[WS-K](2026-08-31-capability-design-agent-system-optimisation.md#L304) — parallel-safe dispatch
Group 5. `wbs:system`, non-billable (`C-COM-002`).

**Status:** ~~DRAFT — nothing in this document is on disk. Awaiting `APPROVE IMPROVEMENTS`.~~
**CORRECTED 2026-09-01 — APPLIED.** Approved and applied the same day; see §8 for what landed and
for the one deviation from the draft's projection. The struck-through line is retained because it
is what the reviewer approved against.

**Queue scope.** `verify-improvement-log.py --check` at activation reported **0 unread, 0
awaiting-approval, 117 reviewer-deferred, 0 already-fixed**. No finding drove this dispatch and
none was processed; the design document is the authorising artefact, per
[`agents/improvement-agent.md` L64-L80](../../agents/improvement-agent.md#L64). The 117
reviewer-deferred entries were deliberately not re-derived
([`agents/improvement-agent.md` L99-L119](../../agents/improvement-agent.md#L99)). **Four** findings
were **appended** by this review — `IMP-0549`, `IMP-0550`, `IMP-0551` at draft time and `IMP-0552`
at application time — all carrying `appended_by` and no `reviewed_in`, per
[IMP-0456](../../logs/known-failure-modes.md#L277).

---

## 0. Conclusion first

**WS-C is sound and lands; WS-K is withheld on a disproved premise.** Both were measured against
the tree rather than read from the design document, and the design document's numbers had moved.

| Workstream | Outcome | The measurement that decided it |
|---|---|---|
| **WS-C** | **Proceed**, with the `<20%` threshold dropped | Full comment strip leaves 301 lines and `verify-build-config.py` still passes, 70 steps / 55 gates |
| **WS-K** percentage half | **WITHHELD** | Candidate gate: **0 findings on the pre-fix corpus and 0 on the post-fix corpus**. Naive variant: **6 findings, 0 true, 6 false** |
| **WS-K** Playwright half | **DEFERRED** — blocked | **0** tracked screenshots of this app exist; Playwright is in no `package.json`. WS-K's own verification cannot be run |

Two of the design document's own figures were re-measured and are wrong. That is not a criticism
of the document — it is the reason the re-measurement step exists.

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [`scripts/verify-css-arithmetic.py`](../../scripts/verify-css-arithmetic.py#L228) check B (broadened from `verify-css-line-height.py`) | 2026-08-31, review 4 | `unverified-arithmetic-claim-in-css-comment` | **NO** | **Working.** Gate runs on the real corpus and passes: 5 authored stylesheets, ambient body size 17px |
| [`scripts/allocate-review-number.py`](../../scripts/allocate-review-number.py) | 2026-08-31, review 9 change F1 | `concurrent-session-same-file-write` | see note | **Working — this dispatch is its first live use.** It claimed `2026-09-01-improvement-review-4.md` and wrote the stub |
| `.claude/settings.json` routing control (WS-E) | 2026-09-01 | `agent-instructions-describe-a-topology-that-changed` | NO | Working — outside this dispatch's files |

**Note on the second row.** [IMP-0547](../../logs/improvement-log.jsonl) is the third instance of
`concurrent-session-same-file-write` and its `revisit_when` reads *"improvement review 9's change
F1 is applied — then close this entry against it."* F1 **is** applied and I used it successfully.
I am **not** closing IMP-0547 here: one successful single-session allocation is not a
re-observation of a *concurrent* collision, and `observable_at` discipline
([`skills/how-to-promote-a-finding.md` L190-L195](../../skills/how-to-promote-a-finding.md#L190))
says an honest open entry beats a closed one nobody tested. Routed, not actioned.

**Audit of closure evidence.** No entry processed by this review is being closed, so the
`observable_at`-versus-closure-evidence column has no rows. Stated rather than omitted.

---

## 2. Clusters and promotion decisions

Capability mode: the units are workstreams, not `class_instance_of` clusters. Two, as dispatched.

```
CLUSTER: WS-C — narrative history crowding out executable config
Altitude:  CLASS — the cost is per-feature; a second feature slug generates its own verbose pair
Ladder row: "the ORDER/shape of the thing was wrong" → config + a read-path change
Becomes:   docs/development/revitalise-grant-automation-build-config-history.md (new)
           + 58 one-line pointers in the YAML
           + one new check inside the EXISTING scripts/verify-build-config.py
Retires:   nothing. Candidate considered and rejected — see §4
Cites:     design document WS-C (no IMP- ids drive it; IMP-0551 corroborates its threshold defect)
Residual:  the operative/provenance split is a JUDGEMENT per block, and no gate can make it.
           The pointer-resolution check protects against LOSS, not against misclassification.
```

```
CLUSTER: WS-K — no gate checks rendered/visual output
Altitude:  n/a — WITHHELD before altitude, on a disproved premise
Ladder row: none reached. skills/how-to-promote-a-finding.md L178-L180: "an argued mechanism,
           in place of a confirmed one" is not evidence for promotion
Becomes:   nothing. Two measurements below, and a deferral with a revisit_when
Retires:   nothing
Cites:     design document WS-K; IMP-0550 records the disproof
Residual:  the INTENT is real and remains uncovered — see §5
```

---

## 3. Proposed changes

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | template | `docs/development/revitalise-grant-automation-build-config-history.md` (new) | Receives the 58 historical comment blocks, one anchored section each | WS-C | YES — `python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml` | N/A |
| 2 | script | [`scripts/verify-build-config.py`](../../scripts/verify-build-config.py) | New check: every `# History:` pointer in the config resolves to an existing anchor in an existing file | WS-C, IMP-0551 | YES — `python3 scripts/verify-build-config.py --selftest` | already `HARD` at [`config/…-build.yml` L106](../../config/revitalise-grant-automation-build.yml#L106) — **no new step** |
| 3 | config | [`config/revitalise-grant-automation-build.yml`](../../config/revitalise-grant-automation-build.yml) | 58 narrative blocks replaced by one-line `# History:` pointers | WS-C | YES — as row 1 | N/A |

**No new constraint rows** (cap 3, used 0). No new build step, no new script file: change 2 goes
into the preflight that already runs, which is the most mechanical home available
([`skills/how-to-promote-a-finding.md` L28](../../skills/how-to-promote-a-finding.md#L28)).

### The classification rule that decides what moves

A comment line **stays** in the YAML if it changes what the next agent *does* when running or
editing that step — the gate's operative contract, an input-type requirement, an ordering
constraint, an exemption mechanism, an env-var declaration. It **moves** if it records *why the
step reached its current form* — dated incident narrative, `IMP-`/`ADR-` provenance, superseded
designs, "was X until Y", measurements from past reviews.

This split is not cosmetic. [IMP-0492](../../logs/known-failure-modes.md#L107) is this repository's
own record of a config comment eleven lines above a call site going on telling the next agent to
use a retired flag — config comments **are** read as instructions, and moving one wholesale is how
you lose an instruction. The rule above is what
[`skills/how-to-promote-a-finding.md` L88-L112](../../skills/how-to-promote-a-finding.md#L88)
already demands when retiring anything: classify every hit as implementation, call site,
**instruction**, or history, and leave history alone.

### Measured, not projected

| Quantity | Value |
|---|---|
| `…-build.yml` today | **1,640 lines, 1,339 comment lines (81.6%), 117,304 bytes** |
| Comment blocks | **67**, of which **58** carry a historical marker (**1,304 lines, 97%**) |
| Full strip (control experiment) | **301 lines**; `verify-build-config.py` **PASS — 70 steps, 55 gates** |
| Projected after the move, 1-line pointers | **394 lines, 93 comments (23.6%)** |

The full-strip control is the load-bearing one: it proves nothing in the preflight depends on
comment content, so the move cannot break the gate over the gates. It is a *control*, not the
proposal — the proposal keeps 35 operative comment lines plus 58 pointers.

### Why the `<20%` threshold is NOT adopted

WS-C asks for [comment share below a stated threshold, e.g. `<20%`](2026-08-31-capability-design-agent-system-optimisation.md#L102)
**and** for [each moved block to leave a one-line pointer](2026-08-31-capability-design-agent-system-optimisation.md#L92).
Measured, those two requirements conflict:

- move all 58 blocks, keep the mandated pointers → **23.6%. FAILS `<20%`.**
- drop the pointers → 10.4%, but abandons the traceability the same sentence demands.

The mechanism is that a relocation shrinks the **denominator** too. Separately,
`…-pipeline.yml` already sits at **375/1,860 = 20.2%** and fails the threshold while needing no
work at all — a threshold that fails a file nobody considers a problem is the wrong instrument.

I therefore propose **reporting the absolute reduction (1,640 → ~394 lines; 117KB → ~28KB) and not
gating on a ratio.** This is [IMP-0544](../../logs/improvement-log.jsonl)'s discipline — run a
recommended threshold against the corpus before adopting it — applied to a second workstream in
the same document; [IMP-0551](../../logs/improvement-log.jsonl) records it so Group 6 measures that
rule against two instances rather than one.

### Scope narrowed to `…-build.yml` only

`…-pipeline.yml` is **excluded** this review, for two measured reasons: it is 20.2% comments (not
80%), so the payoff is small; and
[`scripts/derived-counts-registry.json`](../../scripts/derived-counts-registry.json)'s
`pipeline-rev-setting-row-count` row sites a registered claim **inside that file's prose**, so
relocating it silently breaks a wired derived-count check. That is a real hazard with an owner and
a fix, and it belongs to whichever dispatch does pipeline.yml — named here rather than discovered
there.

**Relocation target is safe from the doc gates.** Measured:
[`doc-line-links`](../../config/revitalise-grant-automation-build.yml#L1166) and
[`design-doc-claims`](../../config/revitalise-grant-automation-build.yml#L1125) both scan
`docs/architecture docs/plans` only. `docs/development/` is outside both corpora, so the moved
prose does not turn either gate red. This was checked because a prose-reading gate going red on
relocated prose is exactly [IMP-0428](../../logs/known-failure-modes.md#L92)'s shape.

---

## 4. Retirements

| ID / file | What it was for | Why retired | Replaced by | Coverage proven? |
|---|---|---|---|---|
| — | — | — | — | — |

**Candidate considered and rejected.** `verify-css-arithmetic.py` check A is the only plausible
retirement candidate in scope — it is the narrower of the gate's two checks and the class it
defends (`no-assertion-on-shipped-content`) has 22 members, which invites generalising it away.
**Rejected:** check A and check B assert different arithmetic over the same corpus, neither
subsumes the other, and check A's own residual
([`scripts/verify-css-arithmetic.py` L54-L58](../../scripts/verify-css-arithmetic.py#L54)) is
already documented and measured at zero. Retiring it would lose coverage, which
[`skills/how-to-promote-a-finding.md` L86](../../skills/how-to-promote-a-finding.md#L86) calls a
regression rather than a promotion. Checked, and none found.

Retired-row count, derived not typed:

```bash
grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l
```

---

## 5. Findings left unprocessed, and WS-K's two halves

### 5a. WS-K percentage half — WITHHELD, with the measurement that forced it

WS-K asks to
[extend the CSS-arithmetic approach to percentage/proportion correctness](2026-08-31-capability-design-agent-system-optimisation.md#L314),
citing `IMP-0509`, `IMP-0525`, `IMP-0526`. Four measurements, in the order that settled it:

**(i) The gate's corpus cannot reach percentages.**
[`authored_stylesheets()`](../../scripts/verify-css-arithmetic.py#L182) scans
`src/code-apps/*/src/**/*.css`. `percentage` appears **once** in all authored CSS. Every displayed
percentage is computed in the **flow**, as
`mul(div(float(length(body('Filter_<dim>_<n>'))), float(max(length(outputs('List_applications_in_round'))…,1))), 100)`,
and passed straight through by
[`landing.ts` L395](../../src/code-apps/trustee-review-portal/src/domain/landing.ts#L395). A CSS
gate cannot see any of it. Extending *this* script is a category error; the intent, if it survived,
would belong in a flow-definition gate.

**(ii) The cited findings are not percentage defects.** `IMP-0525`'s class is
`revision-header-committed-ahead-of-implementation` — a narrative header claiming corrections
absent from the code. `IMP-0526`'s is the auto-fit column count, **already covered by check B and
shipped**. `IMP-0509` is line-height, **already covered by check A**.

**(iii) The commit WS-K reads as a percentage fix is a feature change.** `2afcb2b` changes
`RoundStatisticsCharts.tsx`'s `dataKey` from `count` to `percentage` — the displayed measure. Its
subject line ("Changed to percentages of total applications in that round") describes a feature,
and reads identically to a defect fix.

**(iv) The candidate gate fires on nothing, and its naive variant is 100% false.** Run against the
real corpus, both versions:

| Design | Post-fix (`2afcb2b`) | Pre-fix (`45dee74`) | Adjudication |
|---|---|---|---|
| Denominator-consistency per distribution | **0 findings** | **0 findings** | Would not have caught the defect it exists to prevent |
| Naive "all percentages share one denominator" | **6 findings** | 6 findings | **0 true, 6 false (100%)** — all six are legitimate cost-share measures, `requested_sum / cost_sum` |

The pre-fix flow carries the **same** denominators as the post-fix one (51 round-total + the same
6 cost-share, versus 57 + 6). The denominators never changed; the fix added dimensions.

Per [`agents/improvement-agent.md` L205-L208](../../agents/improvement-agent.md#L205) — *never
apply a gate whose premise you have just watched fail* — and
[L484-L570](../../agents/improvement-agent.md#L484) — *a design measured at high false-positive
rates is redesigned, not shipped* — **this half is withheld.** [IMP-0550](../../logs/improvement-log.jsonl)
records the disproof.

### 5b. WS-K Playwright half — DEFERRED, blocked

WS-K's own mechanical verification requires
[true/false-positive counts against "the real corpus of past screenshots/known-bad layouts from
this feature's own history"](2026-08-31-capability-design-agent-system-optimisation.md#L320) before
deciding SOFT vs HARD. Measured: **2 tracked non-`Designsystem/` images exist, both logos; zero are
screenshots of this app.** Playwright appears in no `package.json`. The corpus does not exist and
cannot be reconstructed — those defects were seen on a reviewer's screen and never captured.

Per [`agents/improvement-agent.md` L77-L79](../../agents/improvement-agent.md#L77), an open
decision blocks the parts that depend on it, and I say which I deferred. **Nothing is wired SOFT
or HARD.** Wiring it SOFT "just to start collecting" would install a step that cannot fail, which
is `gate-cannot-fail` — this repository's largest class at 41 instances.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| WS-K Playwright half | — (capability, no `IMP-` id) | no baseline corpus exists; Playwright is not a dependency; the required FP measurement cannot be taken | a reviewer decides to capture and commit baseline screenshots of the round-statistics landing screen, **and** approves adding Playwright as a dev dependency — both are reviewer decisions, not measurements |
| [IMP-0547](../../logs/improvement-log.jsonl) | `concurrent-session-same-file-write` | its `revisit_when` is satisfied, but closure needs a *concurrent* re-observation this dispatch cannot make | a second session races the allocator, or the owner accepts single-session evidence |
| [IMP-0549](../../logs/improvement-log.jsonl), [IMP-0550](../../logs/improvement-log.jsonl), [IMP-0551](../../logs/improvement-log.jsonl) | appended by this review | a review does not process its own findings ([IMP-0456](../../logs/known-failure-modes.md#L277)) | the next review batch |

**The intent behind WS-K remains uncovered, and that is the honest residual.** No gate in this
repository renders anything. What the two shipped checks cover is CSS *arithmetic*; what caught
every real defect was a human opening the app. Closing that needs a rendering harness, which needs
the two reviewer decisions above.

---

## 6. Digest impact

| | Before (this dispatch's activation) | After |
|---|---|---|
| Log entries | 545 | **549** |
| Distinct lessons | 543 | **547** |
| Digest lines | 619 | **618** |
| Recurring classes (x≥2) | not measured at activation | **42** (`grep -c '^| \*\*x' logs/known-failure-modes.md`) |

Regenerated once at the end, after the fourth append. `--check` reports current.

The digest got one line SHORTER while gaining four entries, which is the per-section cap absorbing
them — the four new lessons displace capped ones rather than extending the file. Stated because a
"+4 entries, −1 line" pair looks like an error and is not. The recurring-class row is given as
measured now rather than as a delta: the activation figure was read from prose, not derived, and
inventing a before-value to make a delta look tidy is the defect
[IMP-0551](../../logs/improvement-log.jsonl) is about.

**One entry was edited rather than appended**, and it is recorded here because an edit to an
`APPLIED` entry is not routine: `IMP-0430`'s `evidence_grep.file` was repointed from the build
config to the history document, because the phrase its needle names is one of the 55 blocks this
review moved. The substance is unchanged and the needle now matches; `IMP-0552` records the general
lesson. Nothing else in the log was touched — no `status` moved.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-01-improvement-review-4.md

Findings processed: 0 NEW  →  2 clusters (capability mode: 2 workstreams, WS-C and WS-K)
Regression check:   3 prior changes audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 1 gates/scripts, 0 skill/knowledge edits,
                    0 agent-file edits, 0 retirements
                    (+ 1 new changelog document, + 1 config edit)
Altitude calls:     0 generalised from instance to class, 2 left as notes
Withheld:           WS-K percentage gate — 0 findings on both corpora; naive variant 6/0 true/6 false
Deferred:           WS-K Playwright half — no baseline corpus, measurement impossible
Digest:             regenerated — 546 lessons, 43 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied — 2026-09-01, on `APPROVE IMPROVEMENTS`

~~**Status: DRAFT — nothing in this document is on disk.**~~ **CORRECTED 2026-09-01: applied.**
The header above and §0 were written before the keyword and are retained as the record of what was
proposed; this section is what actually landed.

| # | Change | State | Verification run |
|---|---|---|---|
| 1 | `docs/development/revitalise-grant-automation-build-config-history.md` created — 55 blocks, **verbatim** | **APPLIED** | 55 `## ` headings ↔ 55 pointers, 1:1 |
| 2 | [`scripts/verify-build-config.py`](../../scripts/verify-build-config.py) — new `check_history_pointers` | **APPLIED** | PASS on the real corpus; **proven able to fail twice** (renamed heading → exit 1; deleted file → 55 findings); Pester `VerifyBuildConfig.Tests.ps1` **14/14** |
| 3 | [`config/…-build.yml`](../../config/revitalise-grant-automation-build.yml) — 55 narrative blocks → operative line + pointer | **APPLIED** | preflight PASS, **70 steps / 55 gates** — identical to pre-change |

**Measured result: 1,640 → 742 lines, 117,304 → 52,109 bytes (a 55.6% reduction).**

**The comment share is 59.4%, not the 23.6% projected — and the deviation was deliberate.**
The projection assumed a bare one-line pointer per block. Applying the classification rule honestly,
55 blocks carried operative content that had to stay: the `CONVERGENCE:` declaration format, the
`GATE-INPUT-TRACKING:` escape, "DO NOT PUT A NUMBER BACK HERE", the `gate-baselines.json` mechanism
with its "`--allow` was RETIRED" warning ([IMP-0492](../../logs/known-failure-modes.md#L107) is
precisely this failure), the folded-scalar indentation rule, and three "IT IS RED — DO NOT DELETE
THE STEP" notices. **Keeping instruction was chosen over hitting a ratio**, which is the same
conclusion §3 reached about the `<20%` gate and the reason it was not adopted.

**Verified: zero executable lines changed.** The multiset of non-comment lines is identical to
`HEAD`'s apart from one blank line and review 8's own uncommitted reorder of
`design-doc-claims`/`doc-line-links`. Step count 76 → 76.

**Two gates remain red, both pre-existing and both documented in the config as such:**
`doc-line-links` (5 true positives, owner `plan-agent`) and `design-doc-claims` (3 true positives,
owner `architect-agent`). Their corpus is `docs/architecture` + `docs/plans`, which this review did
not touch — confirmed by an empty `git status` over both directories.

**No finding moved to `APPLIED`.** This review processed 0 findings; it appended 3, which carry
`appended_by` and no `reviewed_in` so a later review processes them
([IMP-0456](../../logs/known-failure-modes.md#L277)). The registered derived count
`improvement-agent-verify-script-count` is unchanged at **54** — change 2 extended an existing
script rather than adding one, which is why no new `verify-*.py` and no new build step were needed.

### Withheld — decided, and recorded rather than silently dropped

| Item | Withheld because |
|---|---|
| WS-K percentage gate | Premise disproved by measurement: 0 findings on pre- and post-fix corpora; the naive variant measured 6 findings, 0 true, 6 false. Recorded in [IMP-0550](../../logs/improvement-log.jsonl). |
| WS-C `<20%` comment-share threshold | Unreachable by WS-C's own mechanism — 23.6% with the mandated pointers. Recorded in [IMP-0551](../../logs/improvement-log.jsonl). |

### Re-verification required before applying

Per [`agents/improvement-agent.md` L143-L204](../../agents/improvement-agent.md#L143), before
applying: re-run `verify-improvement-log.py --check` and read its `corrects` warnings; re-measure
the four figures in §3 (they moved once already — the design document said 1,425 lines and the
file is 1,640); and re-check that `doc-line-links` and `design-doc-claims` still exclude
`docs/development/`. Delivery dispatches run in parallel with reviews.
