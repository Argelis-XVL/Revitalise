# Test Report (v2) — Trustee Portal Visual Refresh and Round-Statistics Landing Screen

**Feature:** `trustee-portal-visual-refresh`
**Cycle:** re-test after the FAIL recorded in [trustee-portal-visual-refresh-test-report.md](trustee-portal-visual-refresh-test-report.md#L11)
**Artifact:** `build/artifacts/revitalise-grant-automation-20260826-1/`
**Dev Summary:** [trustee-portal-visual-refresh-dev-summary.md](../development/trustee-portal-visual-refresh-dev-summary.md)
**TAD:** [trustee-portal-visual-refresh-architecture.md](../architecture/trustee-portal-visual-refresh-architecture.md)
**SDD:** [revitalise-grant-automation-plan.md](../plans/revitalise-grant-automation-plan.md) — Amendments A-02/A-03 (FR-057–FR-063)
**WBS:** `6.1`, `6.3`, `6.9` per [manifest.json](../../build/artifacts/revitalise-grant-automation-20260826-1/manifest.json#L3) — see defect D-13, the Dev Summary still adds `6.5`
**Date:** 2026-08-26 · **Tier:** strategic (special-category data central to the scope under test)

**Status:** **FAIL**

Written as v2 rather than over the first cycle's report on purpose: that document is the record of
D-01/D-02's original diagnosis and the evidence the fixes were measured against.

---

## 1. Test Summary

**Both P2 defects from the previous cycle are genuinely fixed — and the fix for one of them
introduced a P1 defect that breaks the feature's success path.**

The re-test was scoped by first establishing what actually changed. The unmanaged solution zip in
this artifact differs from the previously-tested build (`revitalise-grant-automation-20260825-1`) in
**exactly one file** — the Round Statistics flow definition. Everything else in the solution is
byte-identical, so the previous cycle's live DEV verification of the schema half (13 attributes,
alternate key `Active`, the three redacted columns, role privileges, table auditing) still describes
the packaged bytes, and re-running fourteen live queries would have produced no new information. The
Code App changed separately: the landing-screen UI now exists, and `rev_roundfinance` is registered
as a data source.

What was executed this cycle:

| Layer | Executed | Result |
|---|---|---|
| Unit / Regression (Code App) | `npx vitest run` — 372 tests, 21 files | **PASS**, 372/372, matches the manifest exactly |
| Unit / Regression (PowerShell) | `pwsh src/tests/Invoke-Tests.ps1` | **875 passed / 1 failed / 1 skipped** — the one failure is out of scope, §3 |
| Security | 6 gates re-run with the build's own invocations | **PASS** — §5 |
| Accessibility | Chart table-first rule, newly testable | **PASS** — §2 |
| Platform Contract | Flow failure path traced by hand against platform `runAfter` semantics | **FAIL — D-10** |
| Verification Level | Live DEV query for the flow, with positive control | **PASS on the claim** — §7.2 |
| Provisioning | Data-source registration verified in source and by gate | **PASS** — §6 |
| Integration / End-to-End | **not possible** — the flow is absent from DEV and the app has no generated flow service | **not executed**, §7.2 |

**The headline finding.** `Respond_error`'s `runAfter` lists `Skipped`
([flow JSON line 309](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L309)).
On a successful run its predecessor `Alert_on_failure` **is** skipped, so `Respond_error` executes
after `Respond_ok` has already responded. Every successful trustee dashboard load attempts a second
`Response`. This is determinate from the definition, not a guess — and it is the direct consequence
of the D-02 fix, so it did not exist before this revision.

---

## 2. Requirement Coverage

`PARTIAL` means some named element of the requirement is delivered and some is not. The UI built
this revision moves several rows off "flow source only", but nothing moves to `PASS` end-to-end,
because no metric can travel from Dataverse to the screen yet (§7.2).

| Requirement | Description | Test IDs | Result |
|---|---|---|---|
| FR-035 | Detail view: redacted narrative, score breakdown, break type + "other" specifier, preferred dates, location, total funding requested, applicant-type and care-support context | TC-035a…f | **PARTIAL** — preferred dates and location now wired (below); three columns still unwired, D-03 |
| FR-039 | Print/offline export reusing FR-035's field list | TC-039 | **PARTIAL** — inherits FR-035; chart blocks now carry `data-print` markers, asserted by test |
| FR-057 | Landing screen shell, full viewport width | TC-057 | **PASS (V2)** — `LandingPage.tsx` exists, 372/372 including its own tests |
| FR-058 | Total applications received, date round opened, average per day | TC-058a/b | **PARTIAL** — `applicationsReceived` authored and rendered; `applicationsPerDay` an explicit `null` in the flow |
| FR-059–FR-062 | Distributions: break type, gender, age range, applicant type, ethnic group, wellbeing, life satisfaction, and the three headline proportions | TC-059…062 | **PARTIAL (UI only)** — `DistributionChart` renders any distribution correctly and is tested; the flow emits `null` for every one of them |
| FR-063 | Round financial position + charity capacity figures | TC-063 | **PARTIAL** — all 13 columns live and audited in DEV; `RoundFinancePanel` now reads them through a registered data source; no row exists in DEV |
| NFR-024 | Accessibility (WCAG 2.1 AA per ADR-020) | TC-N24a…d | **PASS for what exists** — and ADR-029's table-first rule is now genuinely tested, see below |
| NFR-026 | Full-viewport-width, brand-consistent rendering | TC-N26a/b | **PARTIAL** — full-width delivered; **brand half still explicitly unmet** by design ([theme.ts](../../src/code-apps/trustee-review-portal/src/theme.ts#L15) ships Fluent's own default ramp, A-R26, because no approved brand ramp exists) |
| NFR-001, NFR-003 | No secured column released; no identifying attribute in a trustee view | TC-SEC-01…04 | **PASS** — §5 |
| NFR-013 | Data minimisation | TC-SEC-05 | **PASS** — the flow selects only `rev_applicationid`; the app binds only unsecured columns |

**Preferred dates and break location are now delivered, closing the previous cycle's D-04.**
`rev_breakstart`, `rev_breakend` and `rev_breaklocation` are named in the TAD
([§3.1 lines 267–268](../architecture/trustee-portal-visual-refresh-architecture.md#L267)) and are
wired through the app's `schema.ts`, `repository.ts` and `types.ts` — not merely present in
generator output. D-04 was a scope gap; it is closed as a documentation-and-wiring gap, correctly.

**ADR-029's table-first rule is implemented faithfully, and this is the first cycle in which it
could be tested at all.** [ADR-029](../architecture/trustee-portal-visual-refresh-architecture.md#L949)
requires a real data table as the content with the SVG as a labelled companion.
[`DistributionChart.tsx`](../../src/code-apps/trustee-review-portal/src/components/DistributionChart.tsx#L64)
renders a `<table>` with `<th scope="col">` and `<th scope="row">` cells, a screen-reader caption,
the denominator as text before the figures it divides, and an SVG marked `role="img"` with a
summarising label and kept out of the tab order. Thirteen tests assert exactly these properties. The
previous report recorded this rule as untestable because no chart existed; it now passes.

---

## 3. Failed Tests

| Test ID | Layer | Description | Expected | Actual | Severity |
|---|---|---|---|---|---|
| TC-SEC-06b | Platform Contract | The new flow's failure path responds on failure **and only on failure** | `Respond_error` runs when `Compute_statistics` fails, and not otherwise | `Respond_error`'s `runAfter` accepts `Skipped`, which is `Alert_on_failure`'s status on every successful run — so it runs on success too, after `Respond_ok` already responded | **P1** |
| TC-REG-01 | Regression | A regression test guards the D-02 fix | A test asserts the failure path's shape | No test in `src/tests/` references `Respond_error`, `Alert_on_failure`, `Compute_statistics` or `Find_the_failed_action` | **P3** |
| TC-PC-03 | Platform Contract | Dev Summary §9's suite figures match a measured run | Figures match | [§9 line 343](../development/trustee-portal-visual-refresh-dev-summary.md#L343) states 874/1/1; measured 875/1/1; the build measured 876/0/1 | **P4** |

**The one PowerShell test failure is out of my scope and is not a regression in this feature.** It is
`'verify-improvement-log --check' passes against the real log`, failing because twelve findings now
sit unread and the batch trigger is ten. That gate is
[C-TECH-061](../../constraints/technology/technology-constraints.md#L131), whose Scope column names
`lead-agent, improvement-agent, build-agent, pipeline-agent` and **not** `test-agent`. The build
manifest disclosed this drift itself as a post-pack event
([manifest line 20](../../build/artifacts/revitalise-grant-automation-20260826-1/manifest.json#L20)):
it passed at 7 unread when the build ran, and a concurrent session appended more findings during the
build window. The manifest's 876/0/1 was accurate when measured and is stale now, knowably and for a
recorded reason. It does matter downstream — C-TECH-061 **is** in `pipeline-agent`'s scope, so it
must be green before this artifact deploys.

---

## 4. Defects Raised

| Defect ID | Severity | Description | Linked Test |
|---|---|---|---|
| **D-10** | **P1** | **The D-02 fix responds twice on the success path.** [`Respond_error`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L301) runs after `Alert_on_failure` with `runAfter: ["Succeeded","Failed","TimedOut","Skipped"]`. On a successful run the chain `Find_the_failed_action` → `Describe_the_failure` → `Compose_run_link` → `Alert_on_failure` is **all skipped**, because `Find_the_failed_action` only runs on `Compute_statistics` being `Failed`/`TimedOut`. `Skipped` is an accepted status on `Respond_error`, so it executes — after `Respond_ok` (or `Respond_no_open_round` / `Respond_truncated` / `Respond_ambiguous_round`) has already sent a body. Class: `platform-contract-guessed-not-groundtruthed` | TC-SEC-06b |
| D-11 | P3 | **No regression test guards the failure path.** [`skills/how-to-write-a-test-plan.md` line 80](../../skills/how-to-write-a-test-plan.md#L80) requires a regression test for every P1 or P2 defect fixed. D-02 was fixed with none, and nothing in `src/tests/` asserts any part of the new failure path — which is why D-10 shipped through a green suite, a clean packer and a clean Solution Checker. Class: `no-assertion-on-shipped-content` | TC-REG-01 |
| D-12 | P3 | **D-03 is unchanged and still under-declared.** `rev_otherbreaktype`, `rev_additionalamountrequested` and `rev_exceptionalfundingrequested` appear **only** in the platform-generated `Rev_applicationsModel.ts`, which is generator output, not app code. They are absent from `schema.ts`, `repository.ts` and `types.ts`, so FR-035's structured half is still unwired — and Dev Summary §7 still names only the other three columns as known limitations | §2 |
| D-13 | P3 | **The WBS scope disagreement is narrowed but not closed.** The manifest now says `6.1`, `6.3`, `6.9` (the stray `0.4` is gone), but [Dev Summary line 8](../development/trustee-portal-visual-refresh-dev-summary.md#L8) still claims `6.5`, whose contracted deliverable is *"Shared app + access test"*. No access test has been performed in either cycle. Per my own instructions a task whose deliverable names a test and has no test result is carried as an open item, not accepted — owner `pm-agent`/`commercial-agent`, not a retest item. Separately, `6.9` is still absent from `contract/wbs.json` | §7.2 |
| D-14 | P4 | Dev Summary §9's suite figures are stale for the second consecutive cycle (the previous cycle raised this as D-07). Reported figure 874/1/1; measured 875/1/1 | TC-PC-03 |

**Carried forward, unchanged, from the previous cycle:** D-05 (P3) — `rev_roundfinance.rev_name`
still reaches an OData `$filter` and a hand-built JSON document unescaped, at
[flow lines 146](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L146)
and [185](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L185).
Blast radius is still narrow (admin-only input on a table the service identity already reads in
full), but it is the one privileged read path this feature adds and it was not addressed.

**Closed this cycle:** **D-01** and **D-02** (both verified below), **D-04** (preferred dates and
break location, closed by architect-agent), **D-06** (both prose placeholders resolved — no `A-nnn`
literal remains), **D-09** (requirement-id collision, closed by plan-agent).

### D-01 — verified closed, on both halves

The previous defect was that the manifest asserted packaged content that did not exist. Both halves
now check out, and I verified the content rather than the fix description:

1. **The claim is gone, and structurally cannot recur in this shape.**
   `verify-build-manifest-note.py` exits 0 against this manifest. It forbids a *class* of claim —
   no `rev_*` identifier and no filename-shaped token in any note field — rather than adjudicating
   one, so it has no false-positive surface. I confirmed it is deliberately **not** a build-config
   step, for a sound reason recorded at
   [build-agent.md line 257](../../agents/build-agent.md#L257): every config step runs before the
   manifest is written, so a step naming it would be a gate that cannot run. It is invoked by
   build-agent immediately after writing the manifest, and `logs/build.log` records it ran OK for
   this build.
2. **The content it previously overclaimed now genuinely exists.** The prior artifact's bundle
   contained **zero** occurrences of `Applications received`, `applicationsReceived`, `no-open-round`
   or `computedOn`. This artifact's bundle contains all of them, plus `rev_roundfinance`,
   `ambiguous-round` and `truncated`. `LandingPage.tsx`, `RoundStatistics.tsx`,
   `DistributionChart.tsx`, `RoundFinancePanel.tsx` and `domain/landing.ts` all exist in source.

### D-02 — the required behaviour exists; the wiring is wrong on the success path

Three of the four things the TAD asks for are present, and I checked each against the artefact
rather than the description:

- **`rev_errorlog` row — PRESENT, transitively, which is this project's actual pattern.**
  `Alert_on_failure` invokes workflow `8f1c2a44-1004-…`, and that flow's `Write_error_log_row`
  action is a `CreateRecord` on `rev_errorlogs`. It is the only flow in the solution that writes
  that table; the other four reach it by invoking this child. A direct write here would have been
  the wrong fix.
- **`REV | Ops | Failure Alert` call — PRESENT**, severity `Warning`, with a run deep link built in
  the caller (correct: `workflow()` in the child would return the child's identity).
- **Non-`ok` status in the response — PRESENT**, `status: "error"`, and the app handles it: only
  `"ok"` shows a figure, and any unrecognised status degrades to the generic "figures unavailable"
  wording ([landing.ts line 248](../../src/code-apps/trustee-review-portal/src/domain/landing.ts#L248)).
- **`result()` trap avoided — CORRECTLY.** `Find_the_failed_action` is a `Query` filtering
  `@result('Compute_statistics')` for `status eq 'Failed'`, not `result(scope)[0]`, which would
  return the first child regardless of which failed. The known trap was avoided deliberately.

**What is wrong is the one action the pattern being copied did not contain.** The notes cite
`REVScoringDailySummary` as the source of the shape, and that flow's error chain **ends at
`Alert_on_failure`** — it is scheduled, so it has no caller to respond to and no `Respond_error` at
all. For the `Respond_error` the notes instead cite `REVOpsFailureAlert`'s
`Respond_to_calling_flow`, describing it as *"the same shape of always-respond-regardless-of-status
wiring"*. That flow has **exactly one** `Response` action, so always-responding is correct and safe
there. This flow has **four**.

The correct in-repo precedent is the intake flow — the only other multi-`Response` flow, with the
identical `Alert_on_failure` predecessor. Its `Respond_500_intake_failed`
([line 1382](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L1382))
uses `["Succeeded","Failed","TimedOut"]` and **omits `Skipped`**, which is precisely what stops it
firing on the success path.

| Flow | `Response` actions | `Skipped` accepted on the error response? | Correct? |
|---|---|---|---|
| `REVOpsFailureAlert` | 1 | yes | yes — nothing else responds |
| `REVIntakeWordPressToDataverse` | 5 | **no** | yes — this is the precedent |
| `REVPortalRoundStatistics` | 4 | **yes** | **no — D-10** |

**The fix is to delete one token:** remove `"Skipped"` from `Respond_error`'s `runAfter`
([line 309](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L309)).
Worth checking in the same change: `Find_the_failed_action` catches only `Failed` and `TimedOut`, so
if `Compute_statistics` were ever itself skipped no response would be reached at all — the narrow
residue of the original D-02.

**What I can and cannot claim about the consequence.** That `Respond_error` *executes* on a
successful run is determinate from the definition — a `runAfter` listing `Skipped` runs when its
predecessor is skipped, which is the entire purpose of that status being allowed there. What I have
**not** observed is what the platform then does with a second `Response`: whether the run is marked
`Failed` after the caller was already served, or the caller receives the error instead. I could not
distinguish these, because the flow is absent from DEV (§7.2) and there is nothing to run. Both
outcomes are bad and the one-token fix removes the question, so I have rated this on the worse
branch — "feature broken" is P1 under
[the severity scale](../../skills/how-to-write-a-test-plan.md#L64). A reviewer who reads the
platform behaviour as the milder branch should read it as P2; the gate outcome is FAIL either way.

**The assumption register frames this risk in only one direction, which is why it was missed.**
[A-FLOW-05](../development/trustee-portal-visual-refresh-dev-summary.md#L386) asks whether
`Respond_error` *"will actually execute and return a body"* — that it might execute when it should
not is not asked. A live test that exercises only the failure path would close A-FLOW-05 as
CONFIRMED and leave D-10 in place. The row needs its second direction before it is closed.

---

## 5. Constraint & Compliance Verification

As final verifier my scope is all HARD and SOFT rows in both files
([constraints/README.md line 77](../../constraints/README.md#L77)). Rows the previous cycle verified
live and that this build does not touch are carried forward on the byte-identity evidence in §1 and
marked accordingly, rather than restated as fresh live results.

### Executed this cycle

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-DOM-004](../../constraints/domain/domain-constraints.md#L37) | No personal data in application logs | PASS, with a stated limit | `domain-invariants` exit 0. `Secure Outputs` is set on the one row-reading action and correctly absent from the `Respond` actions. **Evidence level V1, source inspection** — no gate can observe `secureData`, and whether it takes effect for a hand-authored flow is A-FLOW-03, still OPEN |
| [C-DOM-010](../../constraints/domain/domain-constraints.md#L47) | CUD on sensitive entities audit-logged | PASS (carried) | Verified live in the previous cycle; the packaged schema is byte-identical. Cited with C-TECH-064's live half as C-DOM-032 requires |
| [C-DOM-011](../../constraints/domain/domain-constraints.md#L48) | Audit records carry timestamp, actor, action, entity id, before/after | PASS (platform-provided) | Dataverse's own audit store; retention 2192 days confirmed live last cycle. No custom audit writer added |
| [C-DOM-030](../../constraints/domain/domain-constraints.md#L92) | No special-category column influences an automated outcome | **PASS** | `domain-invariants` exit 0, 20 register columns, register and FR-016 bar in sync. The new flow emits counts and feeds no eligibility or scoring outcome — re-confirmed against the changed flow definition |
| [C-DOM-031](../../constraints/domain/domain-constraints.md#L93) | Register columns carry `IsSecured=1` | **PASS** | 16 secured, 4 documented exceptions, all four printed by the gate with reason and owner. The three `…redacted` columns are correctly not register entries — they are redactions of registered columns whose sources remain secured |
| [C-DOM-032](../../constraints/domain/domain-constraints.md#L94) | Register columns carry `IsAuditEnabled=1` | **PASS** | 20/20. Two non-register attributes with auditing off are reported, not failed |
| [C-TECH-004](../../constraints/technology/technology-constraints.md#L37) | Inputs validated and sanitised | PASS (with residual) | The flow accepts no input parameters at all, so it has no caller-steerable surface. Residual is D-05's unescaped internal concatenation, unchanged |
| [C-TECH-014](../../constraints/technology/technology-constraints.md#L52) | Unit-test coverage meets the threshold | PASS, both numbers stated | Code App **372/372 at 96.27%** statement/line — re-measured by me. PowerShell **875/1/1**; the 81.81% line-coverage figure is build-agent's measurement, **which I did not independently re-measure**. Per the two-gates rule, the coverage figure is the one that matters and it is cited, not claimed as mine |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Assumption register + `A-nnn` markers in source | PASS | `verify-assumption-markers.py` PASS; no orphan. D-06's two prose placeholders are resolved. Note A-FLOW-05's one-directional wording, §4 |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Report only the level actually executed | **PASS** | §7.2. Every Dev Summary §11 claim was re-checked and **none overclaims** — the failure path is honestly reported as V2 with A-FLOW-05 named as the untested half. D-10 is a design defect inside a correctly-claimed level, not a level overclaim. Applying this row rigorously is what surfaced it: "packaged and Solution-Checker-clean" is not "works" |
| [C-TECH-055](../../constraints/technology/technology-constraints.md#L110) | Warnings triaged | PASS | 47 warnings, 0 untriaged per the manifest; `rev_roundfinance`'s two `forms-and-views-reachable` warnings carry a recorded rationale |
| [C-TECH-057](../../constraints/technology/technology-constraints.md#L127) | Every gate proven able to fail | PASS | `verify-build-config.py` all checks OK, exemptions named not silent |
| [C-TECH-060](../../constraints/technology/technology-constraints.md#L130) | No shipped text exceeds its governing limit | PASS | `verify-field-length-limits.py` exit 0. The flow's long reasoning correctly lives in `.notes.md`, and every new action `description` is within 256 characters |
| [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) | Environment state source cannot express, verified LIVE | PASS (carried) + live this cycle | Previous cycle's 14 live queries stand on byte-identity. This cycle I ran one new live query: the flow's absence from DEV, with a positive control |
| [C-TECH-066](../../constraints/technology/technology-constraints.md#L136) | TAD schema/access tables are a checked specification | **PASS** | `verify-tad-coverage.py` OK — 148 column specs across 11 table blocks, 18 trustee-visible columns on readable tables, and **6 deliverable-now items all naming a column that exists**. This was red at 1 violation before architect-agent closed preferred dates |
| [C-TECH-069](../../constraints/technology/technology-constraints.md#L140) | Readers survive a second instance; identity is (table, column) | PASS | `verify-source-reader-plurality.py` OK, 36 readers |
| [C-TECH-070](../../constraints/technology/technology-constraints.md#L141) | `IsSecured` protects a stored value, never a projection | PASS | `verify-field-security-coverage.py` — 67 secured columns, every one released by a profile, with the two standing platform warnings (5 secured-lookup name companions, 1 Money `_base`). This feature correctly used `Decimal`, not `Money`, for all seven measures |
| [C-TECH-071](../../constraints/technology/technology-constraints.md#L142) | A declared property is only delivered if the builder emits it | PASS | `declared-property-reaches-creation-path` green; confirmed live last cycle on all 13 attributes |
| — | No secured column reaches the Code App | **PASS** | `verify-code-app-column-bindings.py` OK — **68 authored files** reference none of 62 forbidden columns across 7 tables, and **all 3 fail-closed visibility columns are present**. The scope grew with the new UI files and the redaction wiring held |
| — | No trustee in a column security profile | **PASS** | `verify-column-security-membership.py` OK — 4 membership lists, no team holding a trustee-facing role is a member of any profile |
| — | Code App data sources resolve | **PASS** | `verify-code-app-data-sources.py` OK, **5 registrations / 5 declared** (was 5/4). §6 |

### Not in my scope, but red and blocking downstream

[C-TECH-061](../../constraints/technology/technology-constraints.md#L131) (learning-loop triggers)
is **RED**: 12 unread findings against a batch trigger of 10, exit 1. Its Scope column does not
name `test-agent`, so it is not a violation of my gate — but it **is** in `pipeline-agent`'s scope
and will block the deploy. Already routed to `improvement-agent` in parallel by lead-agent.

### Unevaluable

**None.** `C-DOM-030` and `C-DOM-031`, the two rows recorded historically as placeholder text that
could never fail, now carry real rule text backed by a 20-column register and a gate that exits
non-zero. Both were evaluated on their merits above.

### The count, and the filter it was taken through

I applied the filter my own instructions specify — rows whose `Scope` column names `test-agent` —
which is 6 domain HARD rows and 26 technology HARD + 1 technology SOFT. Note the tension worth
recording: [constraints/README.md line 77](../../constraints/README.md#L77) describes test-agent as
checking *all* HARD and SOFT rows in both files as final verifier, while the per-row `Scope` column
excludes it from 6 domain and 15 technology HARD rows. The two readings disagree, and C-TECH-061 —
red right now — sits exactly in the gap. I report on the narrower, per-row basis because that is
what `agents/test-agent.md`'s own Constraints-to-Check table instructs, and I have surfaced
C-TECH-061 explicitly rather than letting the filter hide it.

```
CONSTRAINT CHECK
Domain   HARD: 6 / 6 of 6                 |  violations: NONE
                                          |  unevaluable: NONE
Domain   SOFT: 0 in scope                 |  warnings:   NONE
Tech     HARD: 26 / 26 of 26              |  violations: NONE
                                          |  unevaluable: NONE
Tech     SOFT: 1 in scope                 |  warnings:   C-TECH-067
  C-TECH-067: source-derived-test-counts reports 10 fragile absolute-count literals in the
              test tree (SOFT, --warn-only, reviewer-pre-accepted per the build handoff)
Overall: WARN
```

**The constraint check is WARN; the test run is FAIL.** These are different questions. No HARD row
in my scope is violated — D-10 is a functional defect in a hand-authored flow definition, and no
constraint in either file encodes the property it breaks. That absence is what finding IMP-0345
proposes to close.

---

## 6. Provisioning Verification

| Item | Expected | How verified | Result |
|---|---|---|---|
| `rev_roundfinance` registered as a Code App data source | Present in the generated config | `power.config.json` [line 46](../../src/code-apps/trustee-review-portal/power.config.json#L46) — `roundfinances` → `entitySetName: rev_roundfinances`, `logicalName: rev_roundfinance` | **PASS** |
| Registration count | 5 registrations, 5 declared | `verify-code-app-data-sources.py` exit 0 | **PASS** — closes the gap that gate was built to catch |
| `REV \| Portal \| Round Statistics` in DEV | Present if deployed | Live `pac env fetch` on `workflow`, `category eq 5` | **ABSENT** — 7 flows returned, the other four `REV` flows among them as positive control |
| Schema half (table, 13 attributes, key, redacted columns, roles, auditing) | As previous cycle | Byte-identity of the packaged solution against the previously-verified build | **PASS (carried)** — §1 |

**The data-source fix is real and correctly scoped.** It closed A-LAND-1 by direct comparison
against the generated service rather than by inference, and the registration is in the file the SDK
actually reads. What it does **not** establish is a real signed-in trustee's read — the Dev Summary
claims V3 for this and explicitly not V4, which is the honest level.

**Live-access note.** Live Dataverse reads worked from this session (`pac auth list`, `pac env
fetch` against DEV as `svc_grantapplications`), so the flow's absence is a measured fact with a
positive control, not an inability to look.

---

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

Each row's closing precondition is answered fresh, separately from its status.

| ID | Claim | Status per Dev Summary | Closing precondition | Exists yet? | Result |
|---|---|---|---|---|---|
| A-FLOW-01 | Hand-authored `kind: "PowerApp"` trigger and `Response` shapes are well-formed and the designer will save them | OPEN | Flow imported, then a human opens and saves it in the designer | Environment yes, flow no | **OPEN** |
| A-FLOW-02 | `prvReadWorkflow` at Global is sufficient and not excessive | OPEN | Grant it and nothing else, invoke as a real trustee | Grant is live; flow is not | **OPEN** |
| A-FLOW-03 | `Secure Outputs` hides row data from run history for a hand-authored flow | OPEN | One real run, then read its history as owner | No run has occurred | **OPEN** |
| A-FLOW-04 | `rev_SharedDataverse` binds to a Power-Apps-triggered flow | OPEN | Same designer-save step as A-FLOW-01 | No import | **OPEN** |
| A-FLOW-05 | `Respond_error`, reached via a failure branch, will execute and return a body | OPEN | Force a failure, confirm a `status:"error"` body | No import | **OPEN — and the row is one-directional.** It asks only whether the action will fire when it should. D-10 is the opposite failure, and closing this row as written would not detect it |
| ~~A-LAND-1~~ | Stand-in matches the generated `rev_roundfinance` service | CLOSED | — | — | **Closure confirmed** — the registration is in `power.config.json` and the gate is 5/5 |
| A-LAND-2 | The eventual generated flow service is a static no-argument `Run()` | OPEN | `pa app add flow`, then swap the default | **`pa app add flow` has never been run** — `fetchRoundStatistics` still defaults to `missingFlowService`, which rejects | **OPEN, and it is why nothing is end-to-end** |
| A-LAND-3 | FR-062's three proportions are `{population, count, percentage}` | OPEN | The flow emits one populated | Flow emits `null` | **OPEN** |
| A-LAND-4 | FR-060's total row mirrors a data row minus the category | OPEN | The flow emits a real `breakTypeProfile` | Flow emits `null` | **OPEN** |

**Orphan check (C-TECH-052).** No orphans — `verify-assumption-markers.py` resolves every OPEN row's
`Where` target to a real file containing the row's own id, exit 0.

**Eight OPEN rows, and every one of them is closable only by deploying.** My own fail conditions
treat an OPEN assumption as a FAIL where an environment exists in which it could be closed. DEV
exists — but the flow must be imported first, and import is `pipeline-agent`'s stage, after this
gate. So these rows are reported OPEN and are **not** independent FAIL drivers for this cycle, on
the same reading the previous cycle applied. They are, however,
[C-TECH-058](../../constraints/technology/technology-constraints.md#L128) blockers on the deploy
itself, which needs the reviewer's explicit `OVERRIDE`.

### 7.2 Verification levels achieved

| Component | Level claimed (§11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| `rev_roundfinance` + 13 attributes + alternate key | V4 | **V4 — carried** | Live-verified last cycle; packaged bytes identical | PASS |
| 3 redacted columns on `rev_application` | V4 | **V4 — carried** | As above | PASS |
| Role privilege grants (3 roles) | V4 | **V4 — carried** | As above | PASS |
| Table auditing on `rev_roundfinance` | V4 | **V4 — carried** | As above | PASS |
| `REV \| Portal \| Round Statistics` flow | V2 | **V2 — confirmed, and confirmed it is not V3** | Solution Checker 0/0/0/0/0; flow in the packed zip; **absent from DEV** by live query with positive control | PASS on the claim |
| **The flow's failure path** | **V2** | **V2 on packaging — but the design is defective at V1** | `pac solution pack` and Solution Checker accept it, and `verify-flow-definition-language.py` passes. None of the three can see D-10: the gate's own output says check 5 *"proves a failure path EXISTS, never that it works"* | **FAIL — D-10** |
| `LandingPage.tsx` + `RoundStatistics`/`RoundFinancePanel`/`DistributionChart` | V2 | **V2 — confirmed** | 372/372 across 21 files at 96.27%, re-run by me; column-binding gate OK over 68 files | PASS |
| `rev_roundfinance` Code App data source | V3 (binding), not V4 | **V3 — confirmed as claimed** | Registration present in `power.config.json`; gate 5/5. No real signed-in read | PASS on the claim |
| ADR-026 brand theme | V2 | **V2 — confirmed** | Typecheck/lint/test clean. Brand ramp still Fluent's default by design (A-R26) | PASS on the claim |
| `pa app list-flows` / `pa app add flow` mechanism | V3 (connectivity) | **Accepted as claimed; not re-executed** | Correctly scoped by the Dev Summary itself | PASS on the claim |

- **V4 designer open + save: NOT PERFORMED.** The flow has never been imported anywhere. This is the
  single step that would close A-FLOW-01, A-FLOW-03, A-FLOW-04 and half of A-FLOW-05.
- **Idempotency (V3 re-run):** PASS as convergence evidence only — an all-`EXISTS` run proves the
  read and the comparison, not the write path. The write path is evidenced by the previous cycle's
  live reads.
- **Cross-OS (C-TECH-054):** source review only. No new script this revision; CI has still never run
  on this project, so no gate here has executed on the runner's OS.
- **Diagnostic components (C-TECH-056):** none created; `rev_roundfinance` holds 0 rows.

**The level this feature has actually reached, stated plainly:**

> **The schema half is V4 in DEV. The flow is V2 — packaged and Solution-Checker-clean, never
> imported, and carrying a P1 design defect that no packaging-time check can see. The Code App is
> V2 — compiled, linted, 372 tests green, never pushed — except the `rev_roundfinance` data-source
> binding, which is V3. Nothing in this feature has reached V5. No FR-058–FR-063 figure can travel
> from Dataverse to the screen today, because the flow is not deployed and the app has no generated
> flow service: `fetchRoundStatistics` still defaults to a stand-in that rejects.**

**And the stand-in fails honestly**, which is worth recording as a design strength rather than a
gap: it rejects with a diagnostic naming the missing provisioning verb, and the screen renders
"round figures are unavailable". No figure is invented and no zero is displayed as if it were data.

---

## 8. Recommendations

**1. Fix D-10 before anything is imported — it is one token.** Remove `"Skipped"` from
`Respond_error`'s `runAfter` and copy the intake flow's `["Succeeded","Failed","TimedOut"]` exactly.
While there, decide whether `Find_the_failed_action` should also catch `Skipped` on
`Compute_statistics`, which is the last narrow path to a bare platform failure.

**2. Add the regression test D-11 names, in the same change.** A source-level test over the flow
definition would have caught D-10 in milliseconds: assert that no `Response` action outside the
failure chain can be reached on a run where the scope succeeded, or more simply that only one
`Response` is reachable per outcome. This is the project's signature failure class — a green suite
beside a defect the suite structurally cannot see — and it is cheap to close here.

**3. Widen A-FLOW-05 to both directions before treating it as closeable.** As written, a live test
that only forces a failure will close it while D-10 survives. The row should assert that
`Respond_error` fires on failure **and does not fire otherwise**.

**4. Consider promoting the `verify-flow-definition-language.py` check.** Its check 5 correctly
declares its own limit — presence, not correctness. A cheap extension that would have caught D-10:
flag any `Response` action whose `runAfter` accepts `Skipped` in a flow containing more than one
`Response`. That is a shape check with no fuzzy matching, in the spirit of the manifest-note gate.

**5. Three items are not retest items.** D-12 (FR-035's unwired columns) is a scope question for
the reviewer; D-13 (the `6.5` claim and `6.9`'s absence from the baseline) belongs to `pm-agent` and
`commercial-agent` under the rule that work enters by WBS task id; D-05 (unescaped concatenation)
was carried forward unaddressed and needs an explicit decision to fix or accept.

**6. Before the deploy, two gates must clear that are not mine.** C-TECH-061 is red (12 unread
findings) and is in `pipeline-agent`'s scope. C-TECH-058 requires the reviewer's `OVERRIDE` for the
eight OPEN assumptions, which the import is the means of closing.

---

## Approval

**TEST REVIEW REQUIRED** — this run is **FAIL** on one P1 defect. Per
[my own fail conditions](../../agents/test-agent.md#L99), a FAIL cannot be approved into the
pipeline; the route is back to `development-agent` for D-10.

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0345 | `platform-contract-guessed-not-groundtruthed` | rework | A `runAfter` listing `Skipped` fires when its predecessor is skipped, so an always-respond error branch copied from a one-`Response` flow into a multi-`Response` flow responds on the success path too — check the `Response` count before copying that wiring |
| IMP-0346 | `no-assertion-on-shipped-content` | rework | A P2 fix shipped with no regression test, and the defect it introduced was invisible to a green 876-test suite, a clean packer and a clean Solution Checker — the flow-shape gate says in its own output that it proves presence, not correctness |
| IMP-0347 | `approved-document-internally-inconsistent` | friction | An assumption-register row worded in one direction ("will it fire when it should") cannot detect the opposite defect ("does it fire when it should not"), and closing it from a one-sided live test would certify the bug |

**Not mine, but blocking downstream:** `IMP-0344` (a concurrent session's entry) names an
`appended_by` document that does not exist, which is the single problem
`verify-improvement-log.py` now reports. It is the reason C-TECH-061 stays red, and C-TECH-061 is
in `pipeline-agent`'s scope.
