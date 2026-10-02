# Test Report — Trustee Portal Design 2.0: the card-layout Code App

**Feature Slug:** trustee-portal-design-2
**Artifact:** build/artifacts/trustee-portal-design-2-20261001-2/
**Date:** 2026-10-01
**Status:** PARTIAL
**WBS:** `6.3`, UNBILLED (reviewer decision). Items WI-0055 to WI-0105 (51 items).
**Pipeline-config gates:** PROVISIONAL, because a sibling pipeline-agent dispatch may edit one note in `config/revitalise-grant-automation-pipeline.yml` while this ran. The edit was already present when I read the file (the `blocked_on` note); my run passed with it.

---

## Summary

**The card app is sound as source and as a package, and the first app has not regressed, but nothing has been tested in Power Apps itself, so the result is PARTIAL and not PASS.** Every gate I ran exited 0, I re-measured the design fidelity and got the same 411 equal and 31 classified values, and I found no leak of a withheld answer or a restricted field in either app. Nine assumptions are still open because they can only close on the first push to DEV, and that needs a decision from you (below).

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit (card app, vitest, 49 files) | 888 | 888 | 0 | 0 |
| Regression: first app (vitest, 45 files) | 790 | 790 | 0 | 0 |
| Integration / geometry: card app Chromium visual specs | 23 | 23 | 0 | 0 |
| Regression: first app Chromium visual specs | 8 | 8 | 0 | 0 |
| Security: independent redaction and restricted-field probe, both apps | 5 per app | 5 per app | 0 | 0 |
| Accessibility: independent probe, 6 screens at 320 and 1280 | 12 | 12 | 0 | 0 |
| Fidelity: computed-style re-measure, kit against app | 442 values | 411 equal, 31 classified | 0 unclassified | 0 |
| Gates (parity, budget, build config, source gates, others, section 5) | see section 5 | all exit 0 | 0 | 0 |
| Provisioning | 0 | 0 | 0 | 1 (justified: section 6) |
| Performance | 0 | 0 | 0 | 1 (justified: bundle budget only, no NFR threshold changed) |

Test data: the whole-app harness `app-harness.html` mounts the app on the design kit's own mock data. Nothing used production data. The canary probe used synthetic strings.

Evidence files are in the scratchpad: `cov-trustee-review-portal-cards.txt`, `cov-trustee-review-portal.txt`, `vis-*.txt`, `build-*.txt`, `indep.json`, and `measure-test/measured.json`.

## 2. Requirement Coverage

No functional requirement changed (TAD section 0.3). Coverage is by item group, each traced to the contracted task `6.3`. Every item reached `packaged` (the level `C-TECH-079` requires at this gate) and none was reopened.

| Items | What they cover | Test evidence | Result |
|---|---|---|---|
| WI-0055, WI-0056 | Display hint and per-group row order | `ApplicationDetailPage.test.tsx` order contract (ADR-057 cases a to c), `applicationDetailDisplay.test.ts` | PASS |
| WI-0057 to WI-0062 | Hero, status pill, chips, fact tiles, conditions, cost receipt | `CasePanels.test.tsx`, `ApplicationDetailPage.test.tsx`, fidelity rows | PASS |
| WI-0063, WI-0067, WI-0075 | Answer cards (three redaction states), restricted rows F1 to F3, contracts preserved | unit tests, plus my independent canary probe (section 4) | PASS |
| WI-0064 to WI-0066 | Score bar, 0 to 10 scale, answer list | `CasePanels.test.tsx`, `charts.test.ts` | PASS |
| WI-0068 to WI-0074, WI-0076 | Panels, tokens, print, accessibility, responsive coverage | `print.test.ts`, `ds-tokens.test.ts`, visual specs at 320, 390, 1280, my accessibility probe | PASS |
| WI-0077 to WI-0079 | Scaffold, shell, sharing and packaging | build, parity gate check P3, pipeline entries. **WI-0079's live push, share and V4 are not tested: they are pipeline-agent's** | PASS to V2 |
| WI-0080 to WI-0090 | Round overview (hero, charts, cards, money) | `LandingPage*.test.tsx`, `RoundStatisticsCharts.test.tsx`, `CategoryBars.test.tsx`, visual spec | PASS |
| WI-0091 to WI-0098 | Applications list, filters, group screens | `ApplicationsListPage`, `GroupsListPage`, `GroupDetailPage`, `ApplicationFilters` tests | PASS |
| WI-0099 to WI-0105 | Header, nav, layout, buttons, tables, dialog, tiles | `App.test.tsx`, `VerdictForm.test.tsx`, visual spec, fidelity re-measure | PASS |

## 3. Failed Tests

None.

## 4. Defects Raised

No P1 or P2 defect. Three observations, none blocking:

| Id | Severity | Description | Linked test |
|---|---|---|---|
| O-1 | P3, carried from the first app, not caused by this feature | The round-statistics fetcher treats an unseeded freshness setting as "never fresh". [isCurrent](../../src/code-apps/trustee-review-portal/src/dataverse/roundStatistics.ts#L527) compares against `NaN`, so in an environment where the setting is not seeded, no computed result is ever shown. DEV is seeded (300 seconds). Test and Acceptance and Production are not seeded. The card app copies this file under the parity gate. [Test case 4](../../src/code-apps/trustee-review-portal-cards/src/dataverse/roundStatistics.test.ts#L830) asserts the `pending` outcome under that default, and [case 6](../../src/code-apps/trustee-review-portal-cards/src/dataverse/roundStatistics.test.ts#L882) reaches success only with the setting seeded to 120. No test reaches success under the unseeded default. This is the already-logged class in the [digest](../../logs/known-failure-modes.md#L135); I did not add a duplicate entry. It does not apply to this feature while the card app is DEV-only (TAD section 9.3), and it must be cleared before either app is promoted. | `roundStatistics.test.ts` cases 4 and 6 |
| O-2 | Advisory | The whole card app (184 files), `config/code-app-variant-parity.json`, the parity script, the TAD and the Dev Summary are untracked in git, as is `Designsystem/`. CI on a clean checkout has none of them. This is a commit decision for lead, not a test failure. | `git add -n` listing |
| O-3 | Advisory | The first app's `layout.test.ts` shrank from 32 to 25 tests, and the card app's grew from 23 to 29, under your decision R19 (rewrite in both apps to assert accessibility only). The first app's geometry values are now held only by its 8 Chromium visual tests, which pass. | `vis-trustee-review-portal.txt` |

## 5. Constraint & Compliance Verification

Scope is rows where the Scope column names test-agent: 6 domain HARD, 29 technology HARD, 1 technology SOFT. A row marked NOT TRIGGERED has a trigger this dispatch cannot reach (a live environment write, a live identity probe, or a provisioning script change). I counted it as not evaluable at this gate and list it separately, because I will not mark a live check PASS without running it.

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-DOM-004](../../constraints/domain/domain-constraints.md#L37) | No personal data in logs | PASS | no logging added; source gate `domain-invariants` exit 0 |
| [C-DOM-010](../../constraints/domain/domain-constraints.md#L47) | Audit of sensitive-entity writes | PASS | no entity, flow or write path changed; `git diff --stat src/solutions provisioning` empty |
| [C-DOM-011](../../constraints/domain/domain-constraints.md#L48) | Audit record content | PASS | same as above |
| [C-DOM-030](../../constraints/domain/domain-constraints.md#L92) | No special-category column in scoring | PASS | `no-special-category-data-in-scoring` exit 0 |
| [C-DOM-031](../../constraints/domain/domain-constraints.md#L93) | Register columns secured | PASS | `field-security-coverage` exit 0 |
| [C-DOM-032](../../constraints/domain/domain-constraints.md#L94) | Register columns audited | PASS | `domain-invariants` exit 0 |
| [C-TECH-001](../../constraints/technology/technology-constraints.md#L34) | No hardcoded secrets | PASS | `gitleaks detect --no-git` over the card app and `config/`: no leaks |
| [C-TECH-004](../../constraints/technology/technology-constraints.md#L37) | Input validation | PASS | `VerdictForm.test.tsx` passes unchanged (contract file) |
| [C-TECH-006](../../constraints/technology/technology-constraints.md#L39) | Authentication enforced | PASS | no route added; the app runs only inside Power Apps sign-in |
| [C-TECH-014](../../constraints/technology/technology-constraints.md#L52) | Coverage threshold | PASS | `npm run coverage` exit 0 in both apps |
| [C-TECH-040](../../constraints/technology/technology-constraints.md#L82) | Roles only via group teams | NOT TRIGGERED | no role change; the share is a later manual step to the group team (TAD section 6.1) |
| [C-TECH-042](../../constraints/technology/technology-constraints.md#L84) | Idempotent provisioning | NOT TRIGGERED | no provisioning script changed |
| [C-TECH-045](../../constraints/technology/technology-constraints.md#L87) | Connectors comply with DLP | PASS | the same single Dataverse connection as the first app; `code-app-data-sources` exit 0 for both apps. Reuse of the connection key is assumption A-CRD-1 (open) |
| [C-TECH-046](../../constraints/technology/technology-constraints.md#L88) | No edit to out-of-box roles | PASS | no solution change |
| [C-TECH-048](../../constraints/technology/technology-constraints.md#L90) | Code Apps use generated data sources | PASS | `verify-code-app-data-sources.py` exit 0 on both folders |
| [C-TECH-051](../../constraints/technology/technology-constraints.md#L93) | No fabricated platform id | PASS | `appId` is `null` on purpose; parity check P3 passes with the note that it is the placeholder |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Assumption register | PASS | nine rows recorded; `verify-assumption-markers.py`: 0 source markers without a row |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Verification level honest | PASS | the Dev Summary claims V1 and V2 only; I confirmed both (section 7.2) |
| [C-TECH-054](../../constraints/technology/technology-constraints.md#L109) | Scripts run on the CI OS | PASS (static only) | the parity script uses no OS-specific API; it was run on macOS only, not on the CI runner |
| [C-TECH-056](../../constraints/technology/technology-constraints.md#L111) | Diagnostic components removed | PASS | Dev Summary section 11 records none; no environment was touched |
| [C-TECH-057](../../constraints/technology/technology-constraints.md#L127) | Every gate can fail | PASS | `verify-build-config.py` exit 0; parity gate `--selftest`: 9 of 9 cases behaved |
| [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) | Open assumptions block deploy | **DECISION NEEDED** | nine OPEN rows, each closeable only by the first DEV push. See "What you need to decide" |
| [C-TECH-059](../../constraints/technology/technology-constraints.md#L129) | Learning substrate kept | PASS | `generate-known-failure-modes.py --check` exit 0; the artifact directory is its own `-2` |
| [C-TECH-060](../../constraints/technology/technology-constraints.md#L130) | Text length limits | PASS | `verify-field-length-limits.py` exit 0 |
| [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) | Live environment state verified | NOT TRIGGERED | no deploy yet |
| [C-TECH-065](../../constraints/technology/technology-constraints.md#L135) | Identity probe before scripts | NOT TRIGGERED | no environment script run |
| [C-TECH-066](../../constraints/technology/technology-constraints.md#L136) | TAD tables checked | PASS | `verify-tad-coverage.py` exit 0 (188 column specs) |
| [C-TECH-068](../../constraints/technology/technology-constraints.md#L138) | Negative access result confirmed live | NOT TRIGGERED | no live access test in this dispatch |
| [C-TECH-069](../../constraints/technology/technology-constraints.md#L140) | Readers survive a second instance | PASS | `verify-source-reader-plurality.py` exit 0 |
| [C-TECH-070](../../constraints/technology/technology-constraints.md#L141) | Secured-column shapes | PASS | `field-security-coverage` exit 0 (it also reports the known money-twin gap on `rev_grant`, not this feature) |
| [C-TECH-071](../../constraints/technology/technology-constraints.md#L142) | Declared property reaches creation | PASS | no entity change; the gate lists only a known gap on relationships, unrelated |
| [C-TECH-073](../../constraints/technology/technology-constraints.md#L143) | Metadata writes are PUT | PASS | `verify-metadata-write-verbs.py` exit 0 |
| [C-TECH-076](../../constraints/technology/technology-constraints.md#L146) | CSS arithmetic | PASS | `verify-css-arithmetic.py` exit 0 (12 stylesheets) |
| [C-TECH-078](../../constraints/technology/technology-constraints.md#L148) | Geometry measured in a browser | PASS | 23 card-app and 8 first-app Chromium tests exit 0; fidelity re-measured (section 7.2) |
| [C-TECH-079](../../constraints/technology/technology-constraints.md#L149) | Items move on evidence | PASS | `verify-work-items.py --check --scope WI-0055..WI-0105 --at-least packaged` exit 0 |
| [C-TECH-067](../../constraints/technology/technology-constraints.md#L137) | Derived test counts (SOFT) | WARN | `verify-source-derived-test-counts.py` reports 8 fragile literals across 16 test files (tier 1, never blocking). I did not attribute them to this feature |

Gates also run: the parity gate (129 byte-identical files, 124 contract, 60 presentation, exit 0), both bundle budgets (exit 0), 17 of 17 source gates, `verify-pipeline-config.py` (exit 0, PROVISIONAL), `verify-improvement-log.py` (OK, 1003 entries), `verify-doc-line-links.py` (OK), `verify-design-source-coverage.py` (PASS).

```
CONSTRAINT CHECK
Domain   HARD: 6 / 6 of 6      |  violations: NONE
                               |  unevaluable: NONE
Domain   SOFT: 0               |  warnings:   NONE
Tech     HARD: 23 / 24 of 29   |  violations: C-TECH-058 (conditional: nine OPEN assumptions, closeable only by the first DEV push; needs the reviewer's decision)
                               |  unevaluable: C-TECH-040, C-TECH-042, C-TECH-064, C-TECH-065, C-TECH-068 (not triggered: no live environment write in this dispatch)
Tech     SOFT: 1               |  warnings:   C-TECH-067 (8 fragile literals, tier 1, not attributed to this feature)
Overall: BLOCKED (formal reading of the skill: one conditional violation and five not-triggered live checks; no row failed a test)
```

Compliance: this feature adds no data, no log and no flow, so `knowledge/domain/compliance-requirements.md` has nothing new to check beyond the redaction and restricted-field probe in section 8.

## 6. Provisioning Verification

Skipped, with justification: TAD section 12 lists four items (the new Code App record, the solution-membership fallback, the CanView share, and the `dev-settings.json` entry). All four happen after the first push, which is pipeline-agent's and the reviewer's. None exists to verify. The pipeline entries that will perform them are present: [the two `-cards` entries](../../config/revitalise-grant-automation-pipeline.yml#L1189), DEV only, with no Test, Acceptance or Production entry (TAD section 9.2 and 9.3).

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

Closing precondition for every row below is a live DEV state that does not exist yet (the first push, or a human opening the app in Power Apps). I checked that the precondition is still absent: `appId` is `null` in [power.config.json](../../src/code-apps/trustee-review-portal-cards/power.config.json), and no `-cards` deploy record exists in the ledger.

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| A-TR-14 | The platform assigns the new app's `appId` on first push | OPEN | first push from the `-cards` folder | No | Static half: parity check P3 accepts `null`, rejects a copied id (selftest 9 of 9) | OPEN (cannot close pre-push) |
| A-TR-15 | `pac code push --solutionName` adds the second app and keeps the first | OPEN | first push, then read `solutioncomponents` | No | not verifiable | OPEN |
| A-TR-16 | CanView share to the trustee group team grants view only | OPEN | the share, then admin-centre check | No | not verifiable | OPEN |
| A-TR-17 | Removing a Code App deletes it downstream | OPEN, avoidable | only if the second app is promoted | No, and TAD section 9.3 avoids it | not applicable | OPEN (avoidable) |
| A-CRD-1 | Reusing the first app's connection reference does not rebind the first app | OPEN | after first push, open both apps | No | not verifiable | OPEN |
| A-CRD-2 | Fluent's textarea slot classes are the rendered ones | OPEN | open the detail page in the Power Apps host | No | rendered in Chromium (fidelity re-measure, notes box rows equal); host not reached | OPEN |
| A-CRD-3 | Dialog slot classes and generated-content alt text work in the host | OPEN | open "Record verdict" in the host | No | Chromium only | OPEN |
| A-CRD-4 | The host browser supports `:has()` | OPEN | open the app in the host | No | Chromium only | OPEN |
| A-CRD-5 | The host paints `content: url()`, `accent-color` and `lh` | OPEN | open the app in the host | No | Chromium only | OPEN |

Orphans (hand-authored contracts with no register row): none found by `verify-assumption-markers.py`.

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary section 11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Card app source | V1 and V2 | V1 and V2 | typecheck, lint, coverage (888 tests) and build all exit 0, run by me | PASS |
| Card app packaged output | V2 | V2 | `diff -rq` of the artifact's `code-app-cards` against a fresh `dist` build: no difference | PASS |
| First app | unchanged except `layout.test.ts` | confirmed | 790 tests, typecheck, lint, build, 8 visual tests, parity P1 all exit 0 | PASS |
| Design fidelity | V2, measured | V2, re-measured | I re-ran the measuring script on a fresh render: 107 probes, 442 values, 411 equal, 31 different, identical to the recorded measurement element by element | PASS |
| Parity gate | V1, both directions | V1, both directions | real tree PASS; `--selftest` 9 of 9 | PASS |
| Build and pipeline config | V1 | V1 | build-config exit 0; pipeline-config exit 0 (PROVISIONAL) | PASS |
| Push, share, the host browser | not reached | not reached | no environment write | not reached |

- Idempotency (deploy re-run against a deployed target): N/A, nothing deployed.
- V4 designer or editor open and save, performed by `<nobody>` on `<not yet>`: not performed. It belongs to the reviewer after the push (WI-0079).
- Cross-OS (C-TECH-054): static check only. Not run on the CI runner OS.
- Warnings triaged (C-TECH-055) and diagnostic components removed (C-TECH-056): PASS. All eight warnings have a row in Dev Summary section 11, and none was created.

## 8. Independent checks (did not rely on the Dev Summary)

**Protected values never render.** I rendered the whole detail page in both apps with a distinctive marker string in every redacted free-text field, and in four fields the app must never bind (the three restricted answers and the care-costs field). Results, identical in both apps:
- Withheld (`redactionReleased` false): the marker appears nowhere in the page HTML, text or attributes. The page shows "Withheld until released" and "Restricted".
- Released: the redacted text shows. The restricted fields still never appear.
- Released but blank: shows "Nothing recorded", not the withheld note.
- Released set to `undefined`, `null`, `"true"` or `1`: fails closed, nothing shown.
- A sanity case proves the probe's repository override is the one the page calls. My first draft overrode the wrong method and would have passed vacuously, so the sanity case was added before I relied on the result.

The probe file was deleted after the run; nothing of it remains in the repository. The contract files [visibility.ts](../../src/code-apps/trustee-review-portal-cards/src/domain/visibility.ts#L84), [AnswerCards.tsx](../../src/code-apps/trustee-review-portal-cards/src/components/detail/AnswerCards.tsx#L54) and [RestrictedList.tsx](../../src/code-apps/trustee-review-portal-cards/src/components/detail/RestrictedList.tsx#L18) agree with this. The only first-app change to `visibility.ts` is additive: the first sentence became its own constant and the long text is composed from it, character for character the same string.

**The first app's contract held.** The parity gate passes. The first app's own suite passes. The source needles for WI-0013 (wellbeing headings), WI-0053 (Exceptional circumstance cited block) and WI-0052 (nav order: Round overview, Group applications, Individual applications) still resolve, and the card app's `applicationDetailLayout.ts` is byte-identical to the first app's. The three items remain `deployed:dev`; I did not move them.

**Accessibility, independently measured.** On six screens at 320 and 1280 pixels, including the verdict dialog: no text under its WCAG 2.1 AA contrast threshold (gradients checked at every stop), exactly one h1, no skipped heading level, every form control labelled, every button and link named, the dialog named, the page language set, a visible focus ring (2 to 3 pixels, black), and no sideways scroll. I confirmed the contrast probe can fail by injecting a light-grey line, which it flagged.

## 9. Recommendations

1. Treat O-1 as a gate on promotion of either app, not on this DEV push.
2. Commit the card app and its supporting files before CI is expected to cover it (O-2).
3. After the push, re-run section 7.1 first, because every row's precondition will then exist.
4. `logs/state/wbs-state.json` is stale (`verify-wbs-chain.py` says so). pm-agent should re-derive it; it does not affect this result.

## What you need to decide

**Allow the first DEV push with nine assumptions still open?**

**Problem** — [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) blocks a deploy into an environment where an open assumption could be closed, and A-TR-14 to A-TR-16 and A-CRD-1 can only be closed by that very push.
**Suggested fix** — Reply `OVERRIDE` for the nine rows with the reason "closes only by the first DEV push", so pipeline-agent can push, and re-run section 7.1 straight after.
**What happens if you don't** — Pipeline-agent stops at its assumption gate and the card app stays unpushed; nothing is lost, it just waits.
[Dev Summary section 10](../development/trustee-portal-design-2-dev-summary.md#L197)

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | | | O-1 is the already-logged IMP-0511 class; no new entry |

Digest regenerated: NO, because nothing was appended. `generate-known-failure-modes.py --check` exits 0.
