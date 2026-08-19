# Improvement Review — 2026-08-19

**Agent:** improvement-agent (strategic tier)
**Trigger:** the reviewer asked for a system-wide analysis, then authorised every proposal in it
**Gate:** `APPROVE IMPROVEMENTS` — given by the reviewer as *"Go-ahead with all the suggestions for improvements."*
**Findings processed:** 23 `NEW` → 12 `APPLIED`, 11 deferred with recorded reasons
**Findings added:** 10 (`IMP-0048`–`IMP-0057`), 9 of them applied in this same review

This review is unusual in one respect and it should be said plainly: it began as an **audit**,
not as a finding. The reviewer asked what was wrong with the system, and the answer was found
by reading the repository rather than by a defect stopping work. Ten of the fifty-seven entries
in the log now exist because somebody looked, not because something broke. Two of those ten
were `blocker`-severity latent defects that would have failed the first deployment above DEV.

---

## 1. Regression check — did the last review's changes work?

`docs/improvements/2026-08-18-improvement-review.md` applied 23 findings across seven clusters.

| Cluster | Change made 08-18 | Recurred since? | Verdict |
|---|---|---|---|
| `platform-field-length-limit-unenforced` | `C-TECH-060` + `verify-field-length-limits.py`, two instance gates retired | No new instance | **Worked.** The generalisation held; no third instance |
| `gate-cannot-fail` | `verify-build-config.py` preflight, negative-test requirement | **Yes — 3 more** (`IMP-0050`, and `IMP-0035`/`IMP-0042` were open) | **Partially worked.** See below |
| `learning-substrate-destroyed` | artifact-dir resolver, digest regeneration | **Yes — 2 more** (`IMP-0049`, `IMP-0055`) | **Partially worked.** See below |
| `exit-zero-does-not-mean-created` | source-derived component queries | No new instance | Worked |
| `no-assertion-on-shipped-content` | deferred, deliberately | **Yes — 1 more** (`IMP-0052`) | Now x4. Deferred again — see §5 |
| `test-coupled-to-absolute-counts` | deferred, deliberately | No new instance | Still deferred |
| PM / commercial capability | deferred to a design document | n/a | Still deferred, and now blocked on the reviewer — see §7 |

### The two regressions worth stating in full

**`gate-cannot-fail` recurred three times after a gate was built to prevent it.** The
improvement-agent's own regression rule says: *"A gate that exists and did not fire is either
mis-scoped or not wired into the config. That is a `gate-cannot-fail` finding in its own
right."* All three are exactly that, and the shape is consistent — **the preflight only
governs the surface it was pointed at**:

- `IMP-0042` — it preflights `build.yml` and **nothing preflights `pipeline.yml`**, so a step
  could name a parameter that does not exist. Two open blockers were that one defect written
  twice.
- `IMP-0035` — it preflights *build gates* and says nothing about *constraint rows*, so two
  HARD constraints whose rule text was `[PLACEHOLDER]` passed every gate ever run.
- `IMP-0050` — it identifies gates **by name pattern**, so the two gates added in this very
  review were silently exempt from the negative-test requirement it enforces. Found by
  noticing the step count rise while the gate count did not.

That is not a failure of the idea; it is the idea being under-applied. The fix in this review
is to apply it to all three surfaces (§3).

**`learning-substrate-destroyed` recurred twice, and once was this system's own fix leaking.**
`IMP-0016` made the *build* config resolve its artifact directory per run. `IMP-0049` is the
*pipeline* config still naming the literal directory that fix made obsolete — so
`stage-dev` could not have succeeded on any date after 2026-08-10. **A constraint applied to
one of two files that must agree is a constraint half-applied**, and nothing noticed for nine
days because no CI run had ever reached that job.

---

## 2. Clusters and promotion decisions

23 `NEW` entries → 11 classes. Altitude calls, per `skills/how-to-promote-a-finding.md` §2:

| Class | n | Altitude | Decision |
|---|---|---|---|
| `gate-cannot-fail` | 6 | **class** | Three surfaces gated: pipeline config (`C-TECH-062`), constraint evaluability (`UNEVALUABLE`), the learning loop itself (`C-TECH-061`) |
| `platform-contract-guessed-not-groundtruthed` | 3 | **class** | `IMP-0037` + `IMP-0045` are one defect — an authored element set differing from the platform's. **One** shape gate reading one reference table, not two instance gates |
| `no-assertion-on-shipped-content` | 3 (now 4) | class | **Deferred again.** Needs a scope decision, not a fourth patch — see §5 |
| `test-coupled-to-absolute-counts` | 2 | class | **Deferred.** Needs a reviewed refactor of ~12 assertions |
| `learning-substrate-destroyed` | 2 | instance ×2 | Both had already shipped their code fix; the missing half was a *test*, added |
| `exit-zero-does-not-mean-created` | 2 | — | One blocked on the harness, one on PM capability. Both deferred |
| 5 singleton classes (commercial / capability) | 5 | — | All deferred to the PM capability work |

### The one place the altitude rule was actively binding

`IMP-0045` is a `blocker` — four failed imports with `0x80040216` naming no component — and the
obvious response is a one-line check that an `environmentvariabledefinition.xml` starts with
its root element. That is an instance patch, and `IMP-0037` (an option set missing its
optionset-level elements) is the second instance of the same class. So instead:
`scripts/verify-component-shape.py` reads `constraints/technology/component-shapes.yml`, and a
future component type is **a block in that file, not another script**.

This is also why no fourth constraint was written for it. It could have been `C-TECH-063`;
instead the existing `C-TECH-052` — which already governs hand-authored platform contracts —
gained the mechanical half of its `Verify By`. **Strengthening a row beats adding one.**

---

## 3. Changes applied

### Executable gates — four new, all with known-bad fixtures and negative tests

| Gate | Wired into | Closes | Fixtures |
|---|---|---|---|
| `scripts/verify-pipeline-config.py` | `ci.yml` → `validate` | `IMP-0042`, `IMP-0046`, `IMP-0049` | 3 known-bad configs, 7 tests |
| `scripts/verify-improvement-log.py` | `ci.yml` → `validate` | `IMP-0033` | 3 known-bad logs, 6 tests |
| `scripts/verify-domain-invariants.py` | `build.yml` → `domain-invariants` | `IMP-0035` | 3 registers + 2 entities, 9 tests |
| `scripts/verify-component-shape.py` | `build.yml` → `component-shape` | `IMP-0045`, `IMP-0037` | 2 malformed components, 6 tests |

Each **fails on a missing target and on an empty scan surface**, so none can report PASS over
nothing (`IMP-0007`'s rule, applied at construction rather than discovered later).

### Constraints — three added, at the cap; seven retired

`C-TECH-061` (the learning loop's triggers are enforced by a script) · `C-TECH-062` (the
pipeline config is preflighted) · `C-DOM-032` (special-category columns are audited).
`C-DOM-030` and `C-DOM-031` are **replacements** for the two `[PLACEHOLDER]` rows, not
additions. Retirements are in §4.

### The `UNEVALUABLE` outcome

`skills/how-to-apply-constraints.md` offered `PASS`, `VIOLATION` and `WARNING` — and nothing
for a rule that **cannot be assessed at all**. So a HARD constraint reading
`[PLACEHOLDER] Replace with your first domain-specific constraint` was scored `PASS`, by every
agent, at every gate, for the life of the project.

`UNEVALUABLE` now exists, **a HARD unevaluable row blocks the gate**, and the constraint-check
block's denominator is *evaluable* constraints rather than in-scope ones — because the point of
a count is that it means something.

This single change is what made §4's retirements not merely tidy but necessary: seven rows
would from now on have **blocked every gate they are scoped to**.

### The domain side of the house

The technology constraints had grown to 40 rows and nine executable gates. The domain
constraints were still the vendor template, including two literal placeholders. That asymmetry
is structural, not careless: **32 of 47 findings came from `build-agent` and `pipeline-agent`,
so the learning loop only ever fed the technology side.** A loop that learns only where it
already has instruments will keep getting better at the thing it can already see.

`constraints/domain/special-category-register.yml` is now the single source of the Article 9
column list — read at check time by both the new gate and the FR-016 build step, which are
asserted to name **exactly the same 20 columns**. That list previously lived only as a regex
alternation inside a shell one-liner, hand-edited four times in eight days, under a comment
warning that it "must grow with every future special-category column, or the gate silently
narrows."

Four columns are recorded as documented security exceptions. **They are printed on every
build**, and all four are marked ⚠️ unconfirmed — the shipped schema says they are
trustee-visible and no approval record names all four. That is a question for the Domain
Owner, surfaced rather than resolved.

### Two latent CI defects, neither of which any gate could have found

| | |
|---|---|
| `IMP-0048` | The promote jobs exported `PROVISION_CERT_THUMBPRINT` but **nothing installed the certificate**. A thumbprint is a lookup key into a store that is empty on a fresh runner. All 14 provisioning steps across TST/ACC and PRD would have thrown at connect time |
| `IMP-0049` | The pipeline config's artifact path was frozen at `…-20260810-1`, so `stage-dev` could only fail. Compounded by `upload-artifact`'s least-common-ancestor rooting, which stripped the dated directory from the archive anyway |

Both share a cause worth naming: **a path that has never been executed reports nothing.**
Not a false PASS — no signal at all. That is `gate-cannot-fail`'s quieter sibling, and the
only defence is to notice that a branch has never run. `IMP-0025` and `IMP-0041` are the
same shape.

### A gate that was failing on nothing

`IMP-0057`, found while running the full verification at the end of this review — which is the
only reason it was found at all.

`gitleaks detect --source . --no-git` scans the whole working tree, **including
`build/artifacts/` — the build's own output**. On any machine that has run a build, the
`C-TECH-001` HARD gate therefore scans the previous run's deploy logs. It reported three
`generic-api-key` findings against the literal text `ParameterKey=""` — an **empty** attribute
value in a Dataverse import-job record, in a gitignored directory, from a run the day before.

This is the mirror image of `gate-cannot-fail`, and this project's first recorded instance of
it: **a gate that fires on nothing teaches people to ignore it**, exactly as a gate that cannot
fire teaches them to trust it wrongly. It is invisible to CI by construction, because on a
runner `build/artifacts/` is empty when the scan runs.

`.gitleaks.toml` now scopes the scan to what the build **reads**. Narrowing a security gate
needs its own proof, so three tests were added — including one that plants a PEM under
`provisioning/certs/` and asserts the scan still fails, because that is the one case this gate
has ever actually caught (`IMP-0003`, build #5).

### Documentation that had drifted from the system it describes

- **`IMP-0056` (blocker).** `pipeline-agent.md` instructed the agent to *"execute the
  `environments.acc` block"* behind `APPROVE ACC`. ADR-006 removed that environment on
  2026-08-12. An agent following it would block waiting for a keyword nobody would send — and
  would report that as *waiting*, not as *broken*. `WORKFLOW.md`, `agents/README.md` and
  `CLAUDE.md` carried the same stale topology in three different spellings.
- **`IMP-0053`.** `models.yml` — the declared single source of truth for model assignment —
  named a superseded model, while `routing.log` cited a third value. It also restated per-MTok
  pricing and an expired intro-pricing date: the same defect as `IMP-0029` on the commercial
  side, in a different file. Prices are now gone; the cost table carries token volumes only.
- **`IMP-0054`.** `CLAUDE.md` was tracked as `Claude.MD` and resolved only because macOS is
  case-insensitive. On a Linux runner every agent would start with **no project instructions
  at all**.
- **`IMP-0051`.** `Invoke-Tests.ps1` defaulted to 70% coverage while its own docstring claimed
  that 70 was the figure in `coding-standards.md`, which has said 80 since it was written. The
  build always passed 80 explicitly — **so CI was correct and the branch nothing exercised was
  wrong.**
- **`IMP-0055`.** `routing.log` opened with 12 lines of scaffolding demo data for a different
  project, and a foreign build manifest was committed. Archived under a header rather than
  deleted; the log is now 72 real lines.

### Knowledge files that were still scaffolding

`stack-overview.md` — the file `architect-agent` loads first — still read
`Publisher Prefix: [prefix]` under a banner saying *"agents derive schema names from the
prefix"*, after ~200 `rev_`-prefixed components had shipped. `platform.md`'s entire site map
was `[Area 1 — e.g. Work Items]`. Both are now read back from the shipped solution.

Populating `platform.md` from source surfaced `IMP-0052`: **`rev_grant` has no `SubArea` at
all.** It shipped with a form and three views that nobody can navigate to. `forms-and-views-reachable`
proves the *packer* keeps a form; whether a *human* can reach it is a different question, and
nothing asks it.

### Three one-line knowledge findings, applied

`IMP-0040`, `IMP-0044` and `IMP-0047` each proposed a paragraph in a knowledge file and each
had been sitting unapplied. `IMP-0033`'s lesson is precisely this: *"four one-line knowledge
proposals sat unapplied for four days because 23 already-fixed entries were still marked NEW
alongside them."* Cheap changes drown in an unreconciled queue.

---

## 4. Retirements

**Seven**, the first retirement pass driven by *coverage* rather than consolidation:
`C-TECH-005` · `C-TECH-011` · `C-TECH-012` · `C-TECH-013` · `C-TECH-020` · `C-TECH-021` ·
`C-TECH-022`.

Every active row's `Verify By` was classified. Of 55 active constraints, **12 named anything a
machine could run, and 8 corresponded to a check that actually exists.** The seven retired rows
each name a tool, manifest or technology this project does not have: there is no SQL layer, no
package manifest, no dependency scanner, no licence scanner, no static-analysis tool.

`C-TECH-021` deserves singling out. It is **HARD**, scoped to `build-agent` and
`pipeline-agent`, and reads *"No dependency with a known HIGH or CRITICAL CVE may be deployed
to Acc or Prd"*, verified by *"Dependency scan step in `build.yml`"*. **There is no such step
and there never was.** It has recorded PASS since the day it was written — `IMP-0007`'s exact
shape, in the constraint file rather than in a build gate.

**Coverage is not lost, because there was none.** No fixture, script or test asserted any of
the seven. That is the finding, not a caveat. Each retirement names what would have to exist
to reinstate it — for four of them, the Phase 3 Code App and its `package.json`.

Net: the technology file is **eight rows shorter and four executable gates richer**.

The domain file retired nothing, and the reason is recorded rather than left as a clean-looking
empty table: **none of its 13 inherited rows has a mechanically executable `Verify By` either.**
Converting them is the standing candidate, and it is a bigger job — several need a live
environment to assert against.

---

## 5. Findings left unprocessed

No silent caps. Twelve entries keep `status: NEW`, **each with a `deferred_reason` and a
`revisit_when` in the log**, which is what distinguishes a decision from a backlog.

| Finding(s) | Class | Why deferred | Revisit when |
|---|---|---|---|
| `IMP-0008`, `IMP-0015`, `IMP-0052` | `no-assertion-on-shipped-content` | Now **x4** and the largest unaddressed cluster. Needs one gate and a scope decision about what "shipped content" means — description prose, form label text, site-map reachability are three different surfaces | **First agenda item of the next review** |
| `IMP-0005`, `IMP-0039` | `test-coupled-to-absolute-counts` | x2, so the altitude rule forbids another patch. The fix is ~12 assertions replaced by source-derived counts — a reviewed refactor | Next review, or the next schema addition that breaks them |
| `IMP-0019` | `exit-zero-does-not-mean-created` | Blocked on `IMP-0021`: the cleanup needs `DeleteOptionValue`, which the session's safety classifier refuses | Reviewer clears them in the maker portal |
| `IMP-0041` | `gate-cannot-fail` | Needs a `when: ci` condition in the build-config schema; which steps are CI-only is the reviewer's call | Next build-config revision |
| `IMP-0028`–`IMP-0032` | commercial / PM | **Blocked on the reviewer.** See §7 | Part 11 decisions answered |

The pattern in the top two rows is worth stating: **both are classes where the correct fix is a
refactor rather than an addition, and both have now been deferred twice.** A promotion ladder
that forbids instance patches must eventually pay for the generalisation, or it becomes a
mechanism for never fixing anything. Neither should survive another review undone.

---

## 6. Digest impact

`logs/known-failure-modes.md` — 57 entries, 57 distinct lessons, 220 lines.

**The cap was silently filtering the most-read page in the system.** `MAX_PER_SECTION = 8` was
set when the log held 26 entries. By 2026-08-19 the *"Before you execute a build config"*
section held 17 lessons and **showed eight** — in the one section `build-agent` reads first, on
the one page it reads before its own config. Raised to 20, with the dropped-lesson note kept so
hitting it stays visible. The real fix beyond 20 is to **split the section**, not raise the
number again.

**The `Unrouted` section is now empty.** Four classes had no home — including `IMP-0034`, whose
lesson ("check that a file named in your Knowledge to Load actually contains knowledge") had
been sitting in `Unrouted` since 08-18, reaching nobody, while the exact defect it describes
was live in two files this review had to fix. A new section — *"Before you run something on a
machine it has never run on"* — collects the three classes that ask one question: **does this
work on the machine that will run it, as opposed to the one it was written on?**

Recurring-class table after this review: `gate-cannot-fail` **x13**, `learning-substrate-destroyed`
**x7**, `platform-contract-guessed-not-groundtruthed` **x7**, `no-assertion-on-shipped-content`
**x4**, `exit-zero-does-not-mean-created` **x4**.

---

## 7. Gate

```
IMPROVEMENT REVIEW — docs/improvements/2026-08-19-improvement-review.md

Findings processed: 23 NEW  →  11 clusters  →  12 APPLIED, 11 deferred, 0 rejected
Findings added:     10 (IMP-0048..IMP-0057), 9 applied in this review
Regression check:   7 prior clusters audited, 2 classes recurred (both under-applied, not wrong)
Proposed:           3 constraints (cap 3), 4 gates/scripts, 6 knowledge/skill edits,
                    4 agent-file edits, 7 retirements
Altitude calls:     2 generalised from instance to class (component shapes; the column register),
                    1 folded into an existing constraint rather than adding a fourth
Digest:             regenerated — 57 lessons, 5 recurring classes, 0 unrouted
Verification:       728/729 full suite (1 skipped), 62/62 build-gate tests; all six gates PASS;
                    secret-scan PASS
```

### What this review could not decide

`IMP-0028`–`IMP-0032` — five findings including two `blocker`s, covering contracted hours,
phase membership, WBS-driven work ordering and actual-hours capture — are blocked on **Part 11
of `docs/improvements/2026-08-18-project-management-system-redesign.md`**, which lists decisions
the design explicitly cannot make for itself. That design is ~1,700 lines across two documents
and specifies a `pm-agent` that does not exist in `agents/`.

Those decisions are the reviewer's. They are not deferred because they are unimportant —
`IMP-0032` records 61 WBS rows with empty Actual Hours columns six weeks into a
billed-in-arrears engagement.

**One of the eight was answerable from evidence, and is now answered.** D-8 asked whether the
two application-data exports in `docs/Import/` are real applicant data, noting that if so they
are special-category health data in a git-tracked folder and the matter *"outranks everything
above"*. **They are not.** Both are the WordPress form's **field schema**: 163 column
definitions and a single descriptive row holding option lists rather than a person's values,
with zero email addresses, zero UK-postcode-shaped values and zero NHS-number-shaped values
across the `.csv` and the `.xlsx`. Recorded as `IMP-0058` so it is not re-raised.

That leaves **D-1 to D-7**, all of which are commercial or contractual: a 39-hour Phase 3
variance, an unquoted Finance workstream, what the committed baseline may carry, two
incorporated-by-reference terms documents absent from the repo, whether WBS v0.5 was accepted
by the Client, weekly capacity, and hours already worked or invoiced. None is a question the
system can answer for itself, and D-5 blocks D-1 and D-2.

---

## 8. Applied

All changes in this document were applied after the reviewer's `APPROVE IMPROVEMENTS`
equivalent (*"Go-ahead with all the suggestions for improvements"*), in one session, on
2026-08-19. Entry statuses in `logs/improvement-log.jsonl` were moved to `APPLIED` with
`applied_by` naming the specific artefact, and the digest was regenerated.

**Verification actually executed** (not claimed):

| Check | Result |
|---|---|
| `python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml` | PASS — 22 steps, 17 gates, negative-test coverage OK |
| `python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml` | PASS — 62 steps, 31 paths, 31 `.ps1` parameters |
| `python3 scripts/verify-domain-invariants.py …` | PASS — 20 columns, register ↔ FR-016 gate in sync |
| `python3 scripts/verify-component-shape.py …` | PASS — 25 component files, 2 shapes |
| `python3 scripts/verify-improvement-log.py --check` | PASS — 56 entries, 12 deferred with reasons |
| `python3 scripts/generate-known-failure-modes.py --check` | PASS — digest current |
| `gitleaks detect --source . --no-git --config .gitleaks.toml` | PASS — no leaks |
| `Invoke-Pester src/tests/build/BuildGates.Tests.ps1` | 62/62 |
| `Invoke-Pester src/tests` (full suite) | **728 passed, 0 failed, 1 skipped** |

**Not executed, and therefore not claimed:** nothing in this review has run against a live
Dataverse environment. The certificate-install action (`IMP-0048`) is verified by inspection
and by its own fail-fast assertions — it has never run on a GitHub runner, because no
environment above DEV has been deployed to. That is precisely the condition that hid the
defect, and it is not resolved by this review. **`C-TECH-053` applies to this document too:
these changes are verified at the level actually executed, which is V1/V2 — static and
unit-tested — not V3.**
