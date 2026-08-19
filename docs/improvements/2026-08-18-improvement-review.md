# Improvement Review — 2026-08-18

**Agent:** improvement-agent (tier `strategic`, `config/models.yml` → `tiers.strategic`)
**Findings processed:** 32 `NEW` → 7 clusters
**Trigger:** blocker escalation (16 `blocker` entries with status `NEW`) **and** the ≥10 `NEW`
threshold — both tripped simultaneously, which is itself the finding in §1.
**Gate:** `APPROVE IMPROVEMENTS` — given by the reviewer before this document existed; see §7.

This is the **first** improvement review. The system it audits was built on 2026-08-17 and has
never been run.

---

## 1. Regression check — did the last review's changes work?

There is no prior `*-improvement-review.md`. The "previous review" is the manual loop the
reviewer ran by hand on 2026-08-14 and the design pass of 2026-08-17 (commit `6f84354`), so
that is what is audited here.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| `C-TECH-049` + `verify-workflow-description-length.py` | 2026-08-14 | `platform-field-length-limit-unenforced` | **YES — IMP-0009**, two days later, from a different direction | **Wrong altitude.** Instance patch. Generalised in this review (§2 C-2) and retired (§4) |
| `C-TECH-052` (record every guessed contract) | 2026-08-14 | `platform-contract-guessed-not-groundtruthed` | **YES — IMP-0014, IMP-0017** | **Prose, and it was wired to nothing.** Recording a guess never required closing one. Escalated to a mechanical gate as `C-TECH-058` on 08-17; that gate has not yet met a deploy |
| `skills/how-to-verify-a-platform-contract.md` | 2026-08-17 | `platform-contract-guessed-not-groundtruthed` | Not since | Too new to judge. Next hand-authored artefact is the test |
| `scripts/verify-build-config.py` + `BuildGates.Tests.ps1` | 2026-08-17 | `gate-cannot-fail` (x4 at the time) | **YES — IMP-0024, IMP-0025** — but *both were found BY the new gate suite as it was built* | **Working as designed.** A preflight that catches two defects in its own first hours is the intended behaviour, not a recurrence of the class |
| `scripts/resolve-artifact-dir.py` + `C-TECH-059` | 2026-08-17 | `learning-substrate-destroyed` | Not since | Working — leave alone |
| `agents/pipeline-agent.md` step 0 reads the digest | 2026-08-17 | `learning-substrate-destroyed` | Not since | **Unproven.** No deploy has run since. Do not claim this works |

**Changes whose class recurred after a prose fix:** `C-TECH-052` → already escalated to
`C-TECH-058`. **Changes whose class recurred after a gate:** none — `IMP-0024`/`IMP-0025` were
caught *by* the new gate, which is the opposite failure mode.

### The regression finding this check actually produced

**All 32 entries were still `NEW`, including 23 whose fix had already shipped in commit
`6f84354`.** Nothing moves an entry to `APPLIED` except this agent, and this agent had never
run. Consequences, both real:

1. `lead-agent`'s `≥10 NEW` trigger was tripped by *resolved* findings, so it cannot distinguish
   "the system has learned nothing" from "nobody has done the bookkeeping".
2. Four findings whose proposed change was a one-line knowledge edit (`IMP-0003`, `IMP-0010`,
   `IMP-0017`, `IMP-0021`) were **never applied at all** — proposed when they happened, and
   invisible in the noise of 32 undifferentiated `NEW` entries. All four are applied in this
   review. `IMP-0017` in particular is a `blocker`: an undocumented three-import procedure for
   changing a column's type, which the next type change would have rediscovered by failing.

That is the honest headline of this review: **the capture path worked and the reconciliation
path did not exist.**

---

## 2. Clusters and promotion decisions

```
CLUSTER: gate-cannot-fail  (x6: IMP-0002, IMP-0004, IMP-0007, IMP-0020, IMP-0024, IMP-0025)
Altitude:   CLASS — already generalised on 08-17, correctly
Ladder row: "a tool could catch it mechanically" + "second instance -> generalise"
Becomes:    nothing new. scripts/verify-build-config.py + src/tests/build/BuildGates.Tests.ps1
            + C-TECH-057 already exist and are the right altitude. Verified live this session:
            preflight PASS over 19 steps / 14 gates, 692 tests green through
            src/tests/Invoke-Tests.ps1 (the path CI uses, per IMP-0026).
Retires:    nothing
Cites:      IMP-0002, IMP-0004, IMP-0007, IMP-0020, IMP-0024, IMP-0025
Residual:   Four gates remain exempt from negative testing with stated reasons (lint,
            unit-tests, verify-tooling, preflight-build-config). `lint` is the one that matters:
            a Microsoft-hosted analyser whose behaviour cannot be fixtured. Its ORDER and INPUT
            TYPE are checked, which is the defect that actually occurred (IMP-0004), but a
            regression in what the analyser reports would pass unnoticed.
```

```
CLUSTER: platform-field-length-limit-unenforced  (x2: C-TECH-049's origin incident, IMP-0009)
Altitude:   CLASS — second instance, so the altitude rule FORBIDS a third instance patch
Ladder row: "second instance of the same class -> generalise; instance patches are forbidden"
Becomes:    scripts/verify-field-length-limits.py + C-TECH-060. Reads <MaxLength> from
            Entities/*/Entity.xml instead of transcribing it; carries platform-fixed limits no
            schema declares in one named table with citations; covers settingRows[].key
            (rev_name, 100) and .value (rev_value, 4000) as well as .description (500).
Retires:    C-TECH-049; scripts/verify-workflow-description-length.py;
            scripts/verify-setting-description-length.py; the two build steps that ran them.
Cites:      IMP-0009, and the standing consolidation candidate recorded in the 2026-08-17
            retirement check in constraints/technology/technology-constraints.md
Residual:   Three real gaps, named rather than implied.
            (a) The 256-char flow cap is a platform constant no schema declares, so it is still
                a literal — now in ONE table with a citation instead of buried in a script, but
                if Microsoft changes it, nothing tells us.
            (b) Coverage is the two surfaces that have actually failed (flow descriptions,
                settings rows). Other shipped text with a declared MaxLength — option-set
                labels, form labels, entity <Description> prose — is NOT checked. The third
                instance of this class may well arrive there.
            (c) SETTING_ROW_COLUMNS is a hand-written map from settings-JSON field to Dataverse
                column, transcribed from seed-settings.ps1 lines 205-209. If that script starts
                writing a fourth field, the gate will not know. It fails loudly on an unknown
                limit, but it cannot detect a field nobody told it about.
```

```
CLUSTER: exit-zero-does-not-mean-created  (x4: IMP-0013, IMP-0018, IMP-0019, IMP-0030)
Altitude:   CLASS — generalised on 08-17 for the import cases
Ladder row: "an agent had the information and still did the wrong thing" -> agent-file edit
Becomes:    nothing new for the import cases (pipeline-agent derives its query list from source).
Retires:    nothing
Cites:      IMP-0013, IMP-0018
Residual:   TWO members of this class are NOT covered and are deferred, not solved.
            IMP-0019 (option values orphaned by import) is blocked on IMP-0021 — the cleanup
            needs DeleteOptionValue, which this environment refuses — and no gate yet compares
            live option-set members against source, so a re-deploy will not reveal it either.
            IMP-0030 (a WBS Status column claiming Done for five absent tables) is the same
            class pointed at the project plan rather than at an import, and belongs to the
            deferred PM capability work (§5).
```

```
CLUSTER: learning-substrate-destroyed  (x3: IMP-0016, IMP-0022, IMP-0023)
Altitude:   CLASS — generalised on 08-17 (C-TECH-059 + resolve-artifact-dir.py + the digest)
Ladder row: "the system's own memory failed" -> a read-path change
Becomes:    one addition. scripts/generate-known-failure-modes.py gains two SECTIONS entries,
            because five lessons were rendering under "Unrouted — no section assigned", which
            reaches no agent at any moment. The digest is the read path; a lesson sitting in it
            unrouted is the same defect as a finding sitting in routing.log (IMP-0023).
Retires:    nothing
Cites:      IMP-0023, IMP-0027, IMP-0028, IMP-0029, IMP-0031, IMP-0032
Residual:   The read path is still unproven where it matters most. pipeline-agent reads the
            digest at step 0, but no deploy has happened since that instruction was written, so
            "the capability section prevents re-teaching" is a design claim, not a result.
```

```
CLUSTER: no-assertion-on-shipped-content  (x2: IMP-0008, IMP-0015)
Altitude:   CLASS — second instance, so an instance patch is forbidden
Ladder row: "second instance -> generalise"
Becomes:    NOTHING YET, deliberately. Both findings propose a "candidate gate" and neither
            decides what the source of truth is: for IMP-0008 it is "no shipped <Description>
            names a column absent from the solution" (mechanical, uncontroversial); for
            IMP-0015 it is "a form control's label matches the attribute's authored wording" —
            which requires deciding WHICH wording wins when they differ, and that is a
            reviewer's call about content, not a gate's.
Retires:    nothing
Cites:      IMP-0008, IMP-0015
Residual:   Everything. This class is undefended today, and it is the class that reached the
            reviewer twice as visible defects. It is the highest-priority item for the next
            review, and it is recorded in §5 rather than half-built here.
```

```
CLUSTER: no-route-for-system-capability-request  (x1: IMP-0027)
Altitude:   LAW — a structural hole in the routing table, not an instance of anything
Ladder row: "the ORDER of steps was wrong" -> a routing/activation fix
Becomes:    agents/lead-agent.md gains a routing row for capability requests; this agent gains
            a "capability mode" activation trigger authorised by a design document in
            docs/improvements/ rather than by IMP ids; agents/WORKFLOW.md gains the matching
            processing-trigger row.
Retires:    nothing
Cites:      IMP-0027
Residual:   The carve-out lets a capability review cite requirement ids instead of IMP ids,
            which weakens the "a constraint with no finding behind it is an opinion" rule by
            exactly the width of a design document. That is deliberate — the alternative is
            that the system can only ever change in response to its own failures — but it is
            the rule most likely to be abused, and the 3-constraint cap is what limits the
            damage.
```

```
CLUSTER: the commercial / contract classes  (x5: IMP-0028..IMP-0032, one reusing an old class)
            baseline-restated-not-cited, input-type-with-no-owning-agent,
            work-order-not-driven-by-contract, instrument-exists-never-used,
            exit-zero-does-not-mean-created (IMP-0030)
Altitude:   CLASS, all five — but the change they require is a CAPABILITY, not a rule edit
Ladder row: none of them. The ladder assumes the mechanism exists and asks where the rule
            should live; here the mechanism (a contractual baseline the repo can read) does not
            exist at all.
Becomes:    routing only, in this review: the five classes now reach an agent through the
            digest's two new sections. The substance — contract/, 14 scripts, three agents,
            V6, the worklog — is DEFERRED to a capability review (§5), and is authorised by
            docs/improvements/2026-08-18-project-management-system-redesign.md under the
            capability mode this review just created.
Retires:    nothing
Cites:      IMP-0028, IMP-0029, IMP-0030, IMP-0031, IMP-0032
Residual:   The two blockers in this cluster stay open. IMP-0029 (an APPROVED plan document
            understating the contracted baseline by 186 hours) and IMP-0030 (a Done claim over
            five absent tables) are both live and both unmitigated by anything in this review.
            Routing their lessons into the digest makes them visible; it does not fix them.
```

---

## 3. Changes applied

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | build-gate | `scripts/verify-field-length-limits.py` (new) | One schema-driven gate for the whole field-length class; reads `<MaxLength>` from source, fails on unreadable schema or empty scan | IMP-0009 | **YES** — `python3 scripts/verify-field-length-limits.py src/solutions/RevitaliseGrantAutomation provisioning/deploymentSettings` |
| 2 | constraint | `constraints/technology/technology-constraints.md` | **C-TECH-060** — no shipped text value exceeds the limit that governs it; limits are read, never transcribed | IMP-0009 | **YES** — the command above, plus `Invoke-Pester src/tests/build` |
| 3 | retirement | same file | `C-TECH-049` → `status: retired`, `retired_reason`, first row of the Retired Constraints table | IMP-0009 | **YES** — both retired fixtures still fail (§4) |
| 4 | fixture | `src/tests/fixtures/known-bad/field-length-limits/` (new) | A settings `key` at 109 chars against `rev_name`'s declared 100 — the surface neither retired gate checked | IMP-0009 | **YES** — registered negative test |
| 5 | config | `config/revitalise-grant-automation-build.yml` | Two steps replaced by one `field-length-limits` step | IMP-0009 | **YES** — preflight PASS, 19 steps / 14 gates |
| 6 | script | `scripts/verify-build-config.py` | `.*-limits$` added to `GATE_NAME_PATTERNS` so the new step is treated as a gate | IMP-0009 | **YES** — preflight reports 14 gates, all with negative-test coverage |
| 7 | knowledge | `knowledge/technology/build-and-deploy.md` | New section: credential material outside the repo; spaces in this repo's path; operations the harness refuses | IMP-0003, IMP-0010, IMP-0021 | N/A — reference material |
| 8 | knowledge | `knowledge/technology/dataverse.md` | New section: the three-import procedure for changing a shipped column's type | IMP-0017 | N/A — reference material |
| 9 | script | `scripts/generate-known-failure-modes.py` | Two new `SECTIONS` entries; the digest's *Unrouted* section is now empty | IMP-0027…IMP-0032 | **YES** — `--check` exits 0; no `## Unrouted` heading in the output |
| 10 | agent | `agents/lead-agent.md` | Routing row for capability requests + a *Capability mode* definition | IMP-0027 | N/A — instruction change |
| 11 | agent | `agents/improvement-agent.md` | Capability-mode activation trigger, its authorising artefact, and the anti-bloat substitution | IMP-0027 | N/A — instruction change |
| 12 | agent | `agents/WORKFLOW.md` | Matching processing-trigger row | IMP-0027 | N/A — instruction change |
| 13 | consistency | 8 files (`skills/how-to-promote-a-finding.md`, `constraints/README.md`, `agents/improvement-agent.md`, `knowledge/technology/coding-standards.md`, `knowledge/technology/power-automate.md`, `provisioning/deploymentSettings/settings-rows.notes.md`, `src/tests/provisioning/DeploymentSettings.Tests.ps1`) | Live instructions pointing at the two deleted scripts, repointed at the replacement | IMP-0009 | **YES** — `grep -rl` over live surfaces is clean |

**Constraint budget: 1 of 3 used.** One retirement, so the net constraint count is unchanged at
60 rows with one retired.

### Two live references deliberately NOT edited

`docs/development/revitalise-grant-automation-dev-summary.md` and
`revitalise-grant-automation-dev-deployment-handover.md` still name the retired scripts, and the
handover gives `python3 scripts/verify-workflow-description-length.py …` as a runnable command at
line 104. Both are **approved, dated delivery records owned by the delivery flow**, and this agent
does not rewrite them. Flagged here instead: the next agent to work that runbook will find one
command that no longer resolves. The dated design documents under `docs/improvements/` are
historical by definition and are left as written.

---

## 4. Retirements

| ID / file | What it was for | Why retired | Replaced by | Coverage proven? |
|---|---|---|---|---|
| `C-TECH-049` | No flow `description` over 256 chars | Instance of `platform-field-length-limit-unenforced`; a second instance got its own script instead of a generalisation | `C-TECH-060` / `scripts/verify-field-length-limits.py` | **YES** |
| `scripts/verify-workflow-description-length.py` | as above | superseded | as above | **YES** — the replacement exits 1 on this gate's own known-bad fixture |
| `scripts/verify-setting-description-length.py` | `rev_description` ≤ 500 | Second instance of the same class | as above | **YES** — the replacement exits 1 on this gate's own known-bad fixture |

**Coverage proof, executed this session** — not asserted:

| Case | Result |
|---|---|
| Real solution source + real deployment settings | **exit 0** — 129 flow descriptions, 126 settings-row values, 56 declared limits read |
| Retired `workflow-description-length` fixture | **exit 1** |
| Retired `setting-description-length` fixture | **exit 1** |
| New fixture: settings `key` over `rev_name`'s declared 100 | **exit 1** (new coverage) |
| Target directory that does not exist | **exit 1** (IMP-0007's failure mode) |
| Schema with no declared limits | **exit 1** — refuses to pass over nothing |
| `Invoke-Pester src/tests/build` | 39 passed, 0 failed |
| `src/tests/Invoke-Tests.ps1` (the CI path, IMP-0026) | **692 passed, 0 failed, 1 skipped** |

This is the file's **first retirement in 60 constraints**. One further candidate was considered
and rejected: `C-TECH-052` (record every guessed platform contract) looks redundant beside
`C-TECH-058` (an `OPEN` assumption blocks the deploy), but they act at different moments — 052
makes the guess visible at authoring time, 058 stops it shipping — and retiring 052 would leave
058 with nothing to read.

---

## 5. Findings left unprocessed

No silent caps. Nine of 32 entries keep `status: NEW`, each with a `deferred_reason` in the log.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0005 | `test-coupled-to-absolute-counts` | The finding itself defers it: deriving counts from source vs asserting invariants is a reviewed decision, not a silent edit | The next schema change that breaks a count assertion |
| **IMP-0008** | `no-assertion-on-shipped-content` | x2 class, so the altitude rule forbids an instance patch; the generalisation needs a scope decision (which text is the source of truth) | **Next review — highest priority.** Both instances reached the reviewer as visible defects |
| **IMP-0015** | `no-assertion-on-shipped-content` | Same class as IMP-0008; deferred together into one gate, not two | as above |
| IMP-0019 | `exit-zero-does-not-mean-created` | Blocked on IMP-0021: cleanup needs `DeleteOptionValue`, which this environment refuses. Needs reviewer action in the maker portal | The reviewer clears the orphaned values on `rev_breaktype` (4) and `rev_applicanttype` (1) |
| IMP-0028 | `input-type-with-no-owning-agent` | PM capability review | Capability review, build-order step 1 |
| **IMP-0029** | `baseline-restated-not-cited` | PM capability review; blocked on design decisions D-3, D-4, D-5 | D-5 answered: is WBS v0.5 Client-accepted? |
| **IMP-0030** | `exit-zero-does-not-mean-created` | PM capability review, build-order step 2 | Capability review |
| IMP-0031 | `work-order-not-driven-by-contract` | PM capability review, build-order steps 3–4 | Capability review |
| IMP-0032 | `instrument-exists-never-used` | PM capability review, build-order step 6; blocked on D-6, D-7 | Capability review |

**Two of the 16 blockers are therefore still open**: `IMP-0029` and `IMP-0030`. Both are
commercial, both are quantified in
`docs/improvements/2026-08-18-project-management-system-redesign.md`, and neither is mitigated by
anything in this review. Deferring them is a scope decision, not a judgement that they are minor:
`IMP-0029` is a 186-hour understatement sitting in an approved document, and `IMP-0030` is a
`Done` claim over five tables that do not exist.

### Why the PM work is deferred rather than built

It is 30 requirements, 14 scripts, three new agents, eight changed agents, a new `contract/`
folder and a sixth verification level. Its own build order says steps 1–3 are the urgent part.
Eight decisions (D-1…D-8) are the reviewer's, and **D-5 blocks D-1 and D-2**. Building ahead of
those answers would be guessing at a contract — which is the single most expensive habit this
log records (`IMP-0011`: fifteen import attempts, every one a plausible guess).

It now has a legitimate route, which it did not have this morning: **capability mode**, created
by item 10–12 above. That was the precondition, and it is the one thing here worth doing first.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 32 | 32 |
| Distinct lessons | 32 | 32 |
| Entries with status `NEW` | 32 | 9 |
| Entries with status `APPLIED` | 0 | 23 |
| Recurring classes (x≥2) | 5 | 5 |
| Sections in the digest | 5 + Unrouted | 7, **no Unrouted** |
| Lessons reaching no agent | 5 | **0** |
| Digest lines | 135 | 159 |

Regenerated with `python3 scripts/generate-known-failure-modes.py`; confirmed current with
`--check`. `APPLIED` entries keep teaching — the generator carries lessons for `NEW` and
`APPLIED` and drops only `REJECTED`, so reconciliation loses nothing from the read path.

Nothing was **rejected**. No finding in this log was judged wrong.

---

## 7. Gate

```
IMPROVEMENT REVIEW — docs/improvements/2026-08-18-improvement-review.md

Findings processed: 32 NEW  →  7 clusters  →  23 APPLIED, 9 deferred, 0 rejected
Regression check:   6 prior changes audited, 2 classes recurred (1 wrong altitude -> generalised,
                    1 prose -> already escalated 08-17)
Applied:            1 constraint (cap 3), 1 new gate + 1 fixture, 3 retirements,
                    2 knowledge sections, 3 agent-file edits, 1 generator edit,
                    8 consistency repairs
Altitude calls:     2 generalised from instance to class (field-length; capability route),
                    1 held at class level pending a scope decision (shipped-content, x2),
                    5 routed only (commercial classes -> capability review)
Digest:             regenerated — 32 lessons, 5 recurring classes, 0 unrouted (was 5)
Verification:       preflight PASS (19 steps / 14 gates); 692 tests passed, 0 failed via
                    src/tests/Invoke-Tests.ps1; digest --check exits 0
Still open:         IMP-0029 and IMP-0030 (both blocker, both commercial) -> capability review
```

The reviewer gave `APPROVE IMPROVEMENTS` **before** this document existed, in response to a
routing recommendation. The changes above are applied, every one of them local to this branch
and reversible with `git checkout -- <path>`. The scope was held deliberately narrow for that
reason: no commercial machinery, no invoicing, no new agents, nothing client-facing, and the
largest proposal on the table deferred to a review of its own.

```
HANDOFF | from:improvement-agent | to:lead-agent | feature:system | status:APPROVED | doc:docs/improvements/2026-08-18-improvement-review.md
```

---

## 8. Applied

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | `verify-field-length-limits.py` + `C-TECH-060` + fixture + config + preflight pattern | 2026-08-18, working tree (uncommitted) | IMP-0009 |
| 2 | `C-TECH-049` retired; two instance scripts deleted; 8 live references repointed | 2026-08-18 | IMP-0009 |
| 3 | Knowledge sections in `build-and-deploy.md` and `dataverse.md` | 2026-08-18 | IMP-0003, IMP-0010, IMP-0017, IMP-0021 |
| 4 | Digest routing table — two new sections | 2026-08-18 | (routing for IMP-0027…IMP-0032) |
| 5 | Capability mode — `lead-agent`, `improvement-agent`, `WORKFLOW.md` | 2026-08-18 | IMP-0027 |
| 6 | Status reconciliation for fixes already shipped in `6f84354` | 2026-08-18 | IMP-0001, 0002, 0004, 0006, 0007, 0011, 0012, 0013, 0014, 0016, 0018, 0020, 0022, 0023, 0024, 0025, 0026 |

Entries rejected: **none.**

| Finding | Rejected because |
|---|---|
| — | No finding in this log was judged wrong |
