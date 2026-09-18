# Dev Summary — Emily Review 2026-09-18 Sign-off Items (3 pieces of work)

**Feature Slug:** n/a (three items against the existing `revitalise-grant-automation` feature and
the Trustee Review Portal — no new solution component set, no new `config/<slug>-build.yml`)
**TAD Reference:** `docs/architecture/revitalise-grant-automation-architecture.md` (item 1);
no TAD exists for items 2/3 — see §7
**Date:** 2026-09-18
**Status:** DRAFT — awaiting reviewer `APPROVED`

**Build config used:** `config/revitalise-grant-automation-build.yml` (edited in this dispatch,
item 1 only — see §5). No new build/pipeline config is produced: items 2 and 3 extend components
(the scoring/round-statistics flows, the Trustee Review Portal) already governed by this file.

---

## 0. Scope and authorisation

Three unrelated pieces of work, authorised together by the reviewer (Anna Southern) on
2026-09-18, closing out `docs/plans/emily-review-status-2026-09-18.md` §1a and acting on her two
direct waivers:

| # | Item | Authorisation | Tag |
|---|---|---|---|
| 1 | Compliance register proposal (FR-016 carve-out + pending-adjudication additions) | Reviewer sign-off 2026-09-18: *"Yes, you can use receivebenefits column in calculation flow. Also agreed on the pending adjudication list [as-is]."* | `wbs:1.2,1.4` (EF-28b/M-04), `wbs:6.8` (EF-02/EF-10/EF-27 family) |
| 2 | EF-43 — grouped applications table, Trustee Portal | Reviewer waiver 2026-09-18: *"send the grouped applications in trustee portal... to development-agent already. Skipping commercial-agent."* | `change-order-candidate`, reviewer-waived `C-COM-002`, no WBS id — cite the waiver, not a task id |
| 3 | EF-12 second half — circumstance-score distribution chart | Same waiver as item 2 (`docs/plans/emily-review-feedback-2026-09-plan.md` line 1264: *"bundle with EF-43, same waiver"*) | `change-order-candidate`, reviewer-waived `C-COM-002`, no WBS id |

**Sub-agent fan-out performed** (not withheld): item 2 was dispatched to `frontend-agent` in full;
item 3 was dispatched to `automation-agent` (it required a hand-authored Power Automate flow
change coordinated with the portal contract, so automation-agent owned both halves of that one
contract rather than splitting it across two dispatches — the two ends of one JSON response field
cannot be designed independently). Item 1's build-config edit and the register's proposed YAML
were done directly by development-agent, per the explicit constraint that `constraints/` is
refused to every agent but `improvement-agent` (`IMP-0622`).

---

## 1. Implementation Summary

### Item 1 — FR-016 scoped carve-out + register proposal

The scoring flow (`REVScoringCalculateAndFlag-...4E02.json`) already reads `rev_receivesbenefits`
inside `Derive_income_flag` only (built in the prior session, EF-28b/M-04) — this dispatch makes
the two compliance gates that were deliberately red agree with that reviewer-approved design:

- `config/revitalise-grant-automation-build.yml`'s `no-special-category-data-in-scoring` step no
  longer bars `rev_receivesbenefits` (a blanket grep alternation cannot express "except in one
  named action").
- A new companion HARD gate, `receivesbenefits-scoped-to-income-flag`, greps a ±2-line window
  around every `rev_receivesbenefits` reference and fails if `Score_calculation`,
  `rev_scorebreakdown` or `rev_scoringaudit` appears in that window — the part the blanket grep
  gave up. Proven able to fail against a known-bad fixture (`C-TECH-057`) — see §5.
- `src/tests/solutions/ScoringInvariants.Tests.ps1:605-661` (already in the tree from the prior
  session) asserts the same boundary at the source level, independently.
- The register update this unblocks is **proposed, not applied** — see §9. Development-agent
  cannot write `constraints/`.

**A schema gap was found and is not silently worked around: `IMP-0760`.** The register's
`secured: required/exception` field only answers "is this column column-secured" — it has no way
to record "required-secured, AND scoped-exempt from the FR-016 scoring bar in one place", which is
exactly this carve-out's shape. Applying §9's proposed block as written will keep
`domain-invariants`'s `REGISTER-ENTITY-MISMATCH` check red even after application, until
improvement-agent either extends the checker (IMP-0760's proposal) or the reviewer accepts a
`contract/known-exceptions.json` row instead. This is stated plainly rather than papered over with
a register edit engineered to look green.

### Item 2 — EF-43 grouped applications table (Trustee Portal)

Delivered in full by `frontend-agent`. A second entity-level table (`GroupsTable`) renders above
the existing flat applications list on `ApplicationsListPage`, one row per distinct
`rev_grouplinkage` value (exact-match grouping, no normalising — EF-42's accepted deferred scope):
group code, member count, group total *requested* (summed — reviewer-confirmed safe), shared
start/end dates (earliest-start/latest-end fallback — see judgement call below). **No group-cost
column** — the plan's own worked example shows summing individual `rev_costs` double-counts in 4
of 5 groups (Group RA: £8,300 summed vs. a real £2,075), and no formula recovers the true figure,
so it is omitted rather than estimated. Clicking a group row opens `GroupDetailPage`, which lists
member applications via the existing `ApplicationsTable` and **explicitly omits the score
breakdown / "Current Circumstances" panel** — settled by the plan's own delivered example (absent
in 12 of 12 groups) and asserted by a dedicated test that the panel is not rendered.

### Item 3 — EF-12 second half (circumstance-score distribution chart)

Delivered in full by `automation-agent`, across both ends of the contract:

- **Flow side** (`REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json`): ten new `Filter`/`Compose` actions,
  copied byte-for-byte from the existing `lifeSatisfactionDistribution` actions (the ground-truth
  route available with no live environment reachable this session), banding `rev_circumstancescore`
  (declared range 0-60) into ten equal-width deciles (band 9 is 7-wide, absorbing the 61st value).
  Deliberately **not** anchored to `KnockoutThreshold`/`BorderlineBand*`, because both settings
  files mark those `PROVISIONAL VALUE` pending an undecided board threshold (SDD OQ-001/OQ-002) —
  coupling a chart's bucket boundaries to an undecided policy figure would force a redeploy on a
  board decision unrelated to what the chart shows. Full rationale in the flow's own
  `.notes.md`, "FOURTH VERSION" section.
- **Portal side**: `circumstanceScoreDistribution` added to `RoundStatisticsMetrics`/parsing, a
  new `CIRCUMSTANCE_SCORE_BAND_LABELS` map, and a new chart rendered via the existing
  `DistributionChart`/`CategoryBarChart` pair inside the current "Level of need" section, right
  after life satisfaction — same pattern as CO-001-A1/A2, no new component invented.
- **One open assumption, `A-FLOW-14` (OPEN):** an unscored application is silently excluded from
  every band's numerator but still counted in the population denominator — identical, pre-existing
  behaviour to `lifeSatisfactionDistribution`, not a new defect, but flagged because a trustee-facing
  chart may want an explicit "not yet scored" category. Cheapest close: ask whether any DEV/TST
  round currently holds unscored applications. Register row in §10.

---

## 2. Components Changed / Created

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| `config/revitalise-grant-automation-build.yml` | Build config | FR-016 alternation carve-out + new `receivesbenefits-scoped-to-income-flag` gate | FR-016, item 1 |
| `src/tests/build/BuildGates.Tests.ps1` | Test | Registers + proves the new gate can fail (`C-TECH-057`) | item 1 |
| `src/tests/fixtures/known-bad/receivesbenefits-scoped-to-income-flag/` | Fixture | Known-bad fixture for the new gate | item 1 |
| `docs/plans/special-category-register-update-draft-2026-09-18.md` | Doc | Corrected pre-existing draft (wrong entity for `rev_locationarea`; added the alternation-removal already built; flagged IMP-0760) | item 1 |
| `src/code-apps/trustee-review-portal/src/domain/groups.{ts,test.ts}` | Frontend/domain | Group derivation: count, sum-requested, shared-date fallback | EF-43 |
| `src/code-apps/trustee-review-portal/src/components/GroupsTable.{tsx,test.tsx}` | Frontend | Group-level table | EF-43 |
| `src/code-apps/trustee-review-portal/src/pages/GroupDetailPage.{tsx,test.tsx}` | Frontend | Group detail route, score panel explicitly absent | EF-43 |
| `.../dataverse/{types,schema,repository}.ts` | Frontend/data | `groupLinkage`, `amountRequested` surfaced at list time | EF-43 |
| `.../pages/ApplicationsListPage.tsx`, `App.tsx` | Frontend | Wired `GroupsTable`/`GroupDetailPage` into navigation | EF-43 |
| `src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json(+.notes.md)` | Flow | `circumstanceScoreDistribution` computation, `A-FLOW-14` | EF-12 |
| `.../dataverse/{types,roundStatistics,schema}.ts`, `components/RoundStatistics.tsx` | Frontend | New distribution chart, `CIRCUMSTANCE_SCORE_BAND_LABELS` | EF-12 |
| `src/tests/solutions/RoundStatisticsContract.Tests.ps1` | Test | 7 new + 2 extended Pester assertions on the new flow actions | EF-12 |
| `logs/improvement-log.jsonl` | Log | `IMP-0760` (register schema gap) | item 1 |

---

## 3. Data Model Changes

No new Dataverse columns. `rev_receivesbenefits`, `rev_circumstancescore`, `rev_grouplinkage` and
`rev_costs`/`rev_amountrequested` all already exist; this dispatch changes only how they are read
and gated, never their schema.

## 4. Automation / Workflow Changes

`REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json`: 10 new `Filter_circumstancescore_N` actions + 1 new
`Compose_circumstancescore_categories` action, wired into the response body after
`lifeSatisfactionDistribution`; `List_applications_in_round`'s `$select` widened to include
`rev_circumstancescore` (`IsSecured=0`, no disclosure-control impact — verified by the Pester
"selects nothing beyond columns an expression reads" test).

## 5. Configuration & Provisioning Changes

| Key | Environment | Notes |
|---|---|---|
| `config/revitalise-grant-automation-build.yml` steps `no-special-category-data-in-scoring`, `receivesbenefits-scoped-to-income-flag` | all | See §1 |

No provisioning script changes.

## 6. Security Controls Implemented

- FR-016 boundary for `rev_receivesbenefits` now held by **two independent build gates plus one
  Pester test** (belt-and-braces, per C-DOM-030's own design intent) rather than one blanket grep.
- `rev_circumstancescore` confirmed `IsSecured=0` before widening the flow's `$select` — no new
  disclosure surface.
- No change to `REV_TrusteeRestricted` membership, role privileges, or any Entra/security-group
  provisioning.

## 7. Known Limitations / Deferred Items

- Items 2 and 3 have no approved TAD/SDD of their own — they are reviewer-waived
  `change-order-candidate` build direct to development, per `docs/plans/emily-review-status-2026-09-18.md`
  §1d and the plan's own §5b. No `CASCADE: SPEC_GAP` is raised because the plan text (lines 432-473,
  1062-1064, 1103-1104, 1263-1264) is settled enough to build against directly, and both sub-agents
  confirmed no genuine spec gap was hit.
- `IMP-0760` (register schema gap) remains open — see §1 and §9.
- `A-FLOW-14` (OPEN) — see §1 item 3 and §10.
- EF-12's flow change reached verification level **"copied byte-for-byte from an already-deployed
  action" (upgraded ground truth, not E1)** for the action shape, and **V1 only** (well-formed
  JSON) for the whole artefact — no live environment was reachable this session to pack, import or
  designer-save it. **V2/V3/V4/V5 are NOT proven.** This must be run before the next promotion to
  DEV/TST (`C-TECH-053`).

---

## 8. Judgement calls (all sub-agents, for the record)

1. **Shared group dates** are not literally guaranteed identical across members in the data model;
   rendered as earliest-start/latest-end across members with a recorded date.
2. **No group-cost column** — omitted rather than estimated (see §1).
3. **Group detail page reuses `ApplicationsTable` verbatim** for the member list, including its
   "Record verdict" control — interpreted as "the same fields a member already shows on its own",
   consistent with the plan's emphasis on not duplicating per-application presentation.
4. **Decile banding, not threshold-aligned banding**, for the circumstance-score chart — see §1,
   full rationale in the flow's own `.notes.md`.
5. **`CIRCUMSTANCE_SCORE_BAND_LABELS` placed in `dataverse/schema.ts`**, beside
   `LIFE_SATISFACTION_LABELS` (its closest structural precedent — a non-option-set numeric-scale
   label map), not in `domain/landing.ts`.

---

## 9. Proposed register changes — NOT APPLIED, for improvement-agent / reviewer only

`constraints/domain/special-category-register.yml` is refused to development-agent
(`.claude/hooks/protect-system-rules.py`, `IMP-0622`). The exact proposed blocks are also recorded,
corrected, in `docs/plans/special-category-register-update-draft-2026-09-18.md` (a pre-existing
draft from an earlier session, corrected in this dispatch — its original §2 named the wrong entity
for `rev_locationarea`). Reproduced here verbatim, ready to paste:

### 9.1 `columns:` — add a `read_exception` note to the existing `rev_receivesbenefits` row (line ~132)

```yaml
  - name: rev_receivesbenefits
    entity: rev_application
    basis: "SDD §7.1 — benefit status, classified at the highest restriction tier"
    secured: required
    # DPO-notified exception, confirmed by reviewer 2026-09-18 (Anna Southern), against
    # emily-review-status-2026-09-18.md §1a: "Yes, you can use receivebenefits column in
    # calculation flow." This column MAY be read by REVScoringCalculateAndFlag's
    # Derive_income_flag action ONLY, to set the income flag (rev_incomeflag). It must
    # never reach the numeric circumstance score, rev_scorebreakdown or rev_scoringaudit.
    # ALREADY BUILT: config/revitalise-grant-automation-build.yml's
    # no-special-category-data-in-scoring alternation no longer bars this column (it cannot
    # express "except in one named action"); a companion gate,
    # receivesbenefits-scoped-to-income-flag, asserts the column never reaches score
    # calculation or either scoring output. A source-level Pester test
    # (src/tests/solutions/ScoringInvariants.Tests.ps1:605-661) asserts the same boundary.
    read_exception:
      permits: "income-flag derivation only (Derive_income_flag -> rev_incomeflag)"
      forbids: "the circumstance score, rev_scorebreakdown, rev_scoringaudit, or any other derived value"
      flow: "REVScoringCalculateAndFlag-8F1C2A44-1002-4B7A-9E21-0A1B2C3D4E02.json"
      confirmed_by: "Anna Southern, 2026-09-18"
      dpo_notified: true
    # KNOWN GAP (IMP-0760): applying this row as-is will keep domain-invariants'
    # REGISTER-ENTITY-MISMATCH check HARD-red, because the checker requires every columns:
    # entry to appear in the FR-016 alternation regardless of secured: mode. Resolve via
    # IMP-0760 (extend the checker) or a dated, owned contract/known-exceptions.json row —
    # improvement-agent's or the reviewer's call, not development-agent's.
```

### 9.2 `pending_adjudication:` — six new rows (append, do not reorder existing rows)

```yaml
  # rev_applicant — secured 2026-09-17 (EF-02), region hidden from trustees, admin-visible
  - { entity: rev_applicant, name: rev_locationarea }

  # rev_application — secured 2026-09-17, EF-10 (helper org/relationship reclassified sensitive)
  # and EF-27 (safeguarding action-completed record, same basis as rev_safeguardingflag)
  - { entity: rev_application, name: rev_helperorganisation }
  - { entity: rev_application, name: rev_helperrelationship }
  - { entity: rev_application, name: rev_safeguardingactioncompleted }
  - { entity: rev_application, name: rev_safeguardingactioncompletedon }
  - { entity: rev_application, name: rev_safeguardingactioncompletedby }
```

**Ground truth for the entity names** (verified against live `Entity.xml`, not assumed):
`rev_locationarea` → `Entities/rev_applicant/Entity.xml` line 288. The other five →
`Entities/rev_application/Entity.xml` lines 1070, 1095, 2330, 2344, 2360.

---

## 10. Unvalidated Assumptions Register (§10)

| Id | Status | What was guessed | Where (source marker) | Cheapest verification |
|---|---|---|---|---|
| A-FLOW-14 | OPEN | An unscored application is excluded from every circumstance-score band's numerator but stays in the population denominator (same behaviour as the existing life-satisfaction distribution) | `REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json`, `Filter_circumstancescore_9`'s description; detailed in `.notes.md` §2 | Ask whether any DEV/TST round holds unscored applications; if none exist yet, this is unobservable until one does |

No other new OPEN assumption rows. Both sub-agents reported ground truth reached by copying
already-deployed action shapes (item 3) or by following an already-tested domain-logic pattern
(item 2); no cold guesses were made in either.

## 11a. Hours proposal (for `commercial-agent`, behind `APPROVE TIMESHEET`)

Per `agents/development-agent.md` "Propose actual hours while you still know them" — a proposal
only, never a booking; `logs/worklog.jsonl` is `commercial-agent`'s to write.

| WBS / reference | Work | Proposed actual | Note |
|---|---|---|---|
| `wbs:1.2,1.4` | Item 1 — FR-016 gate carve-out, companion gate + fixture, register proposal | 2.0h | Below any WBS estimate for this task family (D-6) |
| `wbs:6.8` | Item 1 — six-column `pending_adjudication` additions | 0.5h | Bookkeeping-only, per the reviewer's own framing |
| `system` | `logs/improvement-log.jsonl` findings (IMP-0760, IMP-0761) and correcting the pre-existing draft doc | 0.5h | Tooling/process work, not client-billable (`agents/development-agent.md`) |
| n/a — `change-order-candidate`, reviewer-waived `C-COM-002`, cite the waiver not a WBS id | Item 2 — EF-43 grouped applications table (frontend-agent dispatch + this dispatch's own compilation) | 6.0h | No WBS estimate exists to compare against; sized against the plan's own **L** shirt-size for this item |
| n/a — same waiver | Item 3 — EF-12 circumstance-score chart (automation-agent dispatch, flow + portal, + this dispatch's own compilation) | 4.5h | No WBS estimate exists; plan's own shirt-size is **S**, but this item carried a hand-authored flow change (`C-TECH-052` verification) which the shirt-size does not price |

## 11. Verification Evidence

| Item | Level reached | Evidence |
|---|---|---|
| Item 1, new build gate | Proven able to fail (`C-TECH-057`) | `src/tests/build/BuildGates.Tests.ps1` "Build gate: receivesbenefits-scoped-to-income-flag" — 3/3 passing (negative + missing-target + positive) |
| Item 1, register proposal | Not applied — proposal only | §9, `docs/plans/special-category-register-update-draft-2026-09-18.md` |
| Item 2, EF-43 | Full unit/component test coverage, real repo test runner | 783/783 vitest, typecheck clean, eslint clean (frontend-agent's run, reproduced by development-agent — see below) |
| Item 3, EF-12 flow | Ground truth: copied byte-for-byte from an already-deployed, already-working action pair. V1 (well-formed) proven. **V2/V3/V4/V5 NOT proven — no environment reachable** | `verify-field-length-limits.py` PASS, `verify-flow-definition-language.py` OK, 61/61 Pester (`RoundStatisticsContract.Tests.ps1`) |
| Item 3, EF-12 portal | Full unit test coverage | Included in the same 783/783 vitest run |

---

## VERIFICATION SUMMARY (reproduced by development-agent, after both sub-agents' work landed)

```
python3 scripts/verify-assumption-markers.py     → PASS (26 OPEN rows checked, all carry markers; 1 pre-existing NOTE unrelated to this dispatch — A-REV-01)
python3 scripts/verify-assumption-register.py    → PASS (86 rows, 45 open, none self-contradicted)
python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml → OK (all checks green, including inverted-grep safety after the fixture was added)
python3 scripts/run-source-gates.py config/revitalise-grant-automation-build.yml    → 16 gates run, 15 PASS, 1 FAIL (domain-invariants — expected, see §1/§9; unchanged in kind from before this dispatch, now also naming exactly the 6 §9.2 columns plus the pre-existing rev_ethnicgroup posture)
pwsh Invoke-Pester src/tests/build/BuildGates.Tests.ps1                             → 117 passed, 4 failed (2 pre-existing/unrelated: verify-pipeline-config, no-trustee-in-column-security-profile — confirmed via git stash to predate this dispatch; 2 expected: domain-invariants-dependent register-parity tests, see §1/§9)
pwsh Invoke-Pester src/tests/solutions/ScoringInvariants.Tests.ps1, RoundStatisticsContract.Tests.ps1 → 154/154 passed
npx vitest run (trustee-review-portal)                                              → 783/783 passed, 42/42 files
npx tsc --noEmit -p . (trustee-review-portal)                                       → clean
python3 scripts/verify-improvement-log.py --check                                  → OK, 757 entries, 5 pre-existing warnings (unrelated to this dispatch)
```

---

## CONSTRAINT CHECK

Per `skills/how-to-apply-constraints.md`, scoped to development-agent, HARD (+SOFT for technology):

| Constraint | Result | Note |
|---|---|---|
| C-DOM-030 | **VIOLATION (HARD)** | `domain-invariants` exits 1. Pre-existing since the prior session (register not yet updated for EF-28b/M-04); this dispatch's build.yml edit is a precondition for clearing it, not a cause. Clears once §9 is applied. |
| C-DOM-031 | PASS | All registered `secured: exception` rows carry reason + owner. |
| C-DOM-032 | PASS | `IsAuditEnabled=1` on all registered columns; 4 unrelated exclusions already reported and accepted (pre-existing). |
| C-DOM-033 | **VIOLATION (HARD)** | Same `domain-invariants` run: 6 columns from EF-02/EF-10/EF-27 are column-secured but adjudicated in neither list yet. §9.2 is the fix, pending application. |
| C-DOM-003, C-DOM-004, C-DOM-010, C-DOM-011, C-DOM-020 | PASS | No new entity, no new log surface, no new role/privilege change in this dispatch. |
| C-TECH-042, C-TECH-046, C-TECH-047 | PASS | No provisioning, no OOB role edit, no hardcoded environment value (all three unchanged from the pre-existing gate run). |
| C-TECH-052 | PASS | `A-FLOW-14` declared at point of guess; ground-truth route documented (§1/§9 above, §11 table). |
| C-TECH-053 | PASS | Verification level reported honestly per item — V1-only for the flow, stated plainly, not overstated. |
| C-TECH-054 | PASS | No new script; existing `.ps1`/`.py` gates run unchanged. |
| C-TECH-055 | PASS | No untriaged tool warnings; `verify-field-length-limits.py` PASS after one description shortened twice by automation-agent (reported, not silent). |
| C-TECH-057 | PASS | New gate proven able to fail — §5, §11. |
| C-TECH-060 | PASS | `verify-field-length-limits.py` PASS. |
| Accessibility (`skills/accessibility-checklist.md`, cited by C-TECH scope for UI work) | PASS | Native table semantics, real `<button>` navigation, descriptive `aria-label`s, `<dl>`/`<dt>`/`<dd>` reuse, one `<h1>` per view — frontend-agent's report, §8 above. |

**Two HARD violations stand (C-DOM-030, C-DOM-033), both pre-existing in kind, both a precondition
of the fix rather than caused by it, and both explicitly out of development-agent's authority to
clear** (`constraints/` is refused; `IMP-0622`). This is the expected shape per
`docs/plans/emily-review-status-2026-09-18.md` §1a and per development-agent.md's own "One refusal
to expect, and it is not a defect" note. A build dispatched now halts at `domain-invariants`,
exactly as it did before this dispatch — this dispatch does not make the compliance posture worse,
and closes everything within its own authority (the two build gates, the register proposal, and
both frontend/flow deliverables) fully green.
