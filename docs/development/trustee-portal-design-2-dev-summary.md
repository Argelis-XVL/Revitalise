# Dev Summary Document — Trustee Portal Design 2.0: the card-layout Code App on every screen

**Feature Slug:** trustee-portal-design-2
**TAD Reference:** docs/architecture/trustee-portal-design-2-architecture.md (APPROVED, **Revision 3.2**: the reviewer's answers R17-R20; ADR-055..066, all Adopted)
**SDD Reference:** docs/plans/revitalise-grant-automation-plan.md (Amendments A-02, A-05; no functional change — TAD §0.3)
**WBS:** `6.3`, **UNBILLED** by reviewer decision (`contract/known-exceptions.json` → the trustee-portal-design-2 entry; `logs/commercial-events.jsonl` CE-0012)
**Date:** 2026-10-01
**Status:** DRAFT — **Revision 3.2.1**, awaiting code review. Revision 3.2.1 (docs only, after build-agent's C-TECH-055 block) adds the three missing tool-warning rows to §11 — the first app's `glob` and chunk-size warnings and the pack's 17 root-component entries, naming the 3 beyond the parent's 14. Revision 3.2: Revision 3.2 closes the second independent fidelity audit (2026-10-01; `fidelity-audit-result-2.json`): its 17 unexcused or unrecorded deviations, down from 49, are fixed (10) or recorded (4 rows, plus the §13.9 c1 citation checked) — the *Revision 3.2* section below. Revision 3.1 (same day) built the reviewer's four answers recorded in TAD Revision 3.2 and the `layout.test.ts` rewrite in both apps; Revision 3 answered the first audit and replaced the inventory with one **measured** on both renders.
**Model tier:** strategic (opus), escalated at the Revision 1 dispatch and kept. Re-checked after ground truth: Revision 3.1 takes WI-0092 and WI-0102 to **two reopens** each (the escalation trigger); this dispatch already runs at the strategic tier, so no re-dispatch is needed — recorded for the next one.
**Design source:** `Designsystem/Revitalise Design System (1)/ui_kits/trustee-review-portal/` (untracked, read-only), its `tokens/`, and `design_handoff_application_detail/README.md` for the non-negotiables.

---

## Summary

The card app matches the kit's **computed** styles: a Playwright script read `getComputedStyle` from 107 elements on the kit and on the app, the same locator on both, across the six screens and at 1280/390/320 — 442 values compared, **411 equal**, 31 different, every difference now resting on a TAD row (§8.3, §13.9, Appendix B) or on your font decision. Your four answers (TAD Revision 3.2, R17-R20) are built: the kit's palette stays, the three contract limits are accepted, the three colour substitutions are recorded in §8.3, and `layout.test.ts` is rewritten identically in both apps so it asserts only accessibility properties — the one first-app change. Source and configuration only: nothing pushed, imported or shared, and the new app's `appId` is still `null`.

What waits on you: code review of this document. All 51 work items are built.

## Revision 3.2 — the second fidelity audit

The second audit found 17 deviations that were unexcused or unrecorded. Ten are now fixed, four are recorded, and the §13.9 c1 citation is confirmed. All in presentation files; **no contract file and nothing in the first app changed**. Each row below is in the measured inventory (§11).

| # | Audit finding | What changed | Measured now |
|---|---|---|---|
| 1 | Dialog flush with the viewport at 390/320 | the kit's 16px overlay gutter on the portal surface, overriding Fluent's `max-width: 100vw` ([cards.module.css](src/code-apps/trustee-review-portal-cards/src/styles/cards.module.css#L688)) | 16px each side at 390, 20px radius on all corners — equal |
| 2 | `--text-heading` navy #002060 | overridden to `--ink-900` at the card app's root and on the dialog portal; the token lives in the contract `ds-tokens.css` ([app.module.css](src/code-apps/trustee-review-portal-cards/src/styles/app.module.css#L54)) | rgb(43, 43, 43) on both — equal |
| 3 | Axis labels break inside words | no `min-width: 0` and no `overflow-wrap` at 370px and wider, so words break at spaces as in the kit. **Below 370px the kit's own labels push the page sideways** (48px at 320, 28px at 340, 8px at 360, 0 from 370 — measured), so there the old rule stays as deviation (c), WCAG 1.4.10 ([cards.module.css](src/code-apps/trustee-review-portal-cards/src/styles/cards.module.css#L181)) | at 390: equal; page overflow 0 at every width |
| 4 | Opened/Closed as a flex gap | an inline term followed by a normal space ([cards.module.css](src/code-apps/trustee-review-portal-cards/src/styles/cards.module.css#L488)) | inline, bold — equal |
| 5 | Group avatar never shrinks | `flex: none` removed | flex-shrink 1 at 390 — equal |
| 6 | Members table two-line headers | the kit's inert-button box: inline-flex, centred lines, 6px gap before an empty glyph slot ([ApplicationsTable.tsx](src/code-apps/trustee-review-portal-cards/src/components/ApplicationsTable.tsx#L107)) | display, alignment, gap equal; a 3px residual inset is the column width, which the table's data sets — (b), measured with the app's font in the kit |
| 7 | Cost receipt has no first rule | the first line keeps its top rule, pulled up 1px as the kit's wrapper does ([detail.module.css](src/code-apps/trustee-review-portal-cards/src/styles/detail.module.css#L507)) | rule width, style and colour equal; the -1px sits on the line, not a wrapper — (c), `<dl>` content model |
| 8 | Hero chip rows centred | `.chipRow` stretches as FactChips does; the pill-and-chips row keeps the kit's centring in its own class | align-items: normal — equal |
| 9 | Status pill may wrap | `white-space: nowrap` | equal |
| 10 | Font smoothing | `-webkit-font-smoothing: antialiased` on the page and the dialog portal | equal |

**Recorded, not changed:**

| Finding | Category | Basis |
|---|---|---|
| 44px on "Show the data table" and on the members-table row links | (c) | the design's non-negotiable 8 (`design_handoff_application_detail/README.md:22`) states 44px for buttons; the toggle and the row links are buttons in the markup and extend it under the same rule, as the Group and Individual row links already do |
| Filter selects and inputs: 1px #8a8a8a, not 1.5px grey-200 | (a) | TAD §8.3 "Form-control borders", ADR-037 correction 4: the 3:1 non-text boundary `ds-tokens.test.ts` (contract) asserts. Chromium computes the kit's 1.5px to 1px at 1x, so the width reads equal and the colour row records the difference |
| "Dates differ between members" against the date span | (b) | content from source: the app derives the shared span with `formatDateRange` (TAD §13.4) |
| Signed-in name not bold | (c) | TAD §13.9 c1 (R18) — the inventory row cites it |

## What has been built

1. **A measured style inventory, and a script anyone can re-run** — [§11 inventory](#style-inventory-measured), probe list and runner in the scratchpad (`measure/probes.cjs`, `measure/measure.mjs`).
   A row reads "match" only when the computed value is identical on both renders. Revision 2's inventory was built by grepping the CSS, which is how 29 wrong "match" rows got in (IMP-1002).

2. **The kit's unset line-heights, everywhere** — [page reset](src/code-apps/trustee-review-portal-cards/src/styles/app.module.css#L74).
   The kit's body sets no line-height, so its text renders at `normal`. Fluent's root had forced 22px, and 41 rules forced 1.3 or 1.1. All now read `normal`, except where the kit sets a number (1, 1.05, 1.15, 1.2, 1.25).

3. **The eyebrow at the size the kit renders, 13px** — [eyebrow](src/code-apps/trustee-review-portal-cards/src/styles/app.module.css#L350).
   The kit loads `RoundOverview.jsx` after `Shared.jsx`, and its 13px `Eyebrow` replaces the 12px one globally. Measured: 13px on all six kit screens. The dot now keeps the kit's #e6027f, because a graphic only needs 3:1.

4. **Chart marks and member dots in the kit's own colours** — [palette](src/code-apps/trustee-review-portal-cards/src/cards/palette.ts#L28).
   The marks use the kit's five-step order (#e6027f, #49345b, teal, pink, #6a5774). Only the two marks below 3:1 are swapped: teal for #009aa8 and pink-300 for pink-500. The member dots are decorative, so they use the kit's four colours exactly. This is the palette TAD Revision 3.2 adopts (R17, §8.3).

5. **The screens' structural fixes** — [native selects](src/code-apps/trustee-review-portal-cards/src/components/ApplicationFilters.tsx#L116), [Group detail headers](src/code-apps/trustee-review-portal-cards/src/components/ApplicationsTable.tsx#L107), [four group chips](src/code-apps/trustee-review-portal-cards/src/cards/GroupHero.tsx#L57), [detail hero row](src/code-apps/trustee-review-portal-cards/src/components/detail/SummaryHero.tsx#L162), [logo](src/code-apps/trustee-review-portal-cards/src/styles/app.module.css#L159).
   - The filters use native selects with the browser's chevron, and each field wraps on its own. At 320px "Score from" and "Score to" now stack, as the kit's do.
   - Group detail headers show no sort arrow, with `aria-sort="none"` as the kit has.
   - The group hero shows four chips. The badge repeats the count but is `aria-hidden`, so the contract test still finds "Members" exactly once.
   - On the detail screen, the status pill and the first chips wrap as two separate units.
   - The logo is the kit's file without the strapline, inlined at build time.
   - The group total renders in Playfair.
   - Type of break uses the kit's stats-table style.
   - Numeric headers are right-aligned, and tabular figures are gone.

6. **The verdict dialog, as far as CSS can reach the contract components** — [radios](src/code-apps/trustee-review-portal-cards/src/styles/app.module.css#L1196), [dialog layout](src/code-apps/trustee-review-portal-cards/src/styles/cards.module.css#L759), [the portal fix](src/code-apps/trustee-review-portal-cards/src/styles/app.module.css#L36).
   - The radios are native 18px controls, coloured with `accent-color` in each choice's tone.
   - The second "Your verdict" heading is hidden visually but kept for screen readers.
   - The 16px gap between blocks holds throughout.
   - The actions row is left-aligned.
   - The notes box is three rows high and full width.

   Fluent renders the dialog outside `.page`, so the kit's variables and `box-sizing` never reached it. That is why the choice cards had lost their 14px radius. Both are now set on the dialog surface too.

## Elements added

| Element | What it is |
|---|---|
| `src/code-apps/trustee-review-portal-cards/src/cards/palette.ts` | The kit's mark and member-dot palettes, with the two contrast substitutions |
| `src/code-apps/trustee-review-portal-cards/src/cards/assets/revitalise-logo.png` | Byte-identical copy of the kit's logo without the strapline (sha1 `b4e6e47a…`, the tracked `Designsystem/Revitalise Design System/assets/logo/` file) |

## Elements changed

| Element | Change |
|---|---|
| Card app `styles/app.module.css`, `cards.module.css`, `ds.module.css`, `detail.module.css` | line-heights, eyebrow, tables, filters, buttons, dialog, logo (presentation) |
| Card app `components/ApplicationFilters.tsx`, `ApplicationsTable.tsx`, `GroupsTable.tsx`, `CategoryBars.tsx`, `DistributionChart.tsx`, `RoundStatistics.tsx`, `detail/SummaryHero.tsx`, `cards/charts.tsx`, `cards/GroupHero.tsx`, `pages/GroupDetailPage.tsx` | as above (presentation) |
| Card app `components/CasePanels.test.tsx`, `styles/layout.test.ts` (presentation) | the hero-row grouping and the `normal` heading line-height they pin |
| `src/styles/layout.test.ts` in **both apps** (contract) | rewritten byte-identically under TAD §5.3 rule 1 (R19): 44px floors and no fixed heights on controls, the strong control boundary, wrapping rows, container-relative grid floors and scrolling tables, focus rings, reduced-motion. The values it used to pin are presentation (first app: 32 tests → 25; card app: 23 → 29) |
| `config/code-app-variant-parity.json` | `layout.test.ts` removed from the `presentation` list and the contract glob's `except`; the contract reason names it |
| Card app `bundle-budget.json` | CSS re-measured at 148,639 bytes (+37,769 over Revision 2: the inlined kit logo); JS 845,809 (Fluent `Select` gone) |

**One contract file changed in Revision 3.1, in both apps identically: `layout.test.ts` (R19).** Nothing else in the first app changed. The parity gate passes with 124 contract files and 60 presentation files.

## What is still open

**Work items: none open.** WI-0086 and WI-0087 were re-closed after pm-agent's amendments (§12); the scope check exits 0.

**WI-0079's live half.** Unchanged: first push from the `-cards` folder, read back and commit the `appId`, share CanView, then V4.

**The four gate baselines that expired 2026-09-30 now read 2026-10-14.** `config/gate-baselines.json` entries for IMP-0454, IMP-0481 (tad-coverage) and IMP-0649 on tst_acc and prd were re-dated outside this dispatch; this dispatch did not touch them. They are not this feature's.

**`Designsystem/` stays uncommitted** (ADR-064's 131 → 140/285 count applies when it is).

## What you need to decide

Nothing new. Your four answers to Revision 3's decisions are recorded in TAD Revision 3.2 (§0.6) and built:

| # | Question | Your answer (verbatim) | Where recorded | What the build does |
|---|---|---|---|---|
| R17 | Chart palette | "Design's palette (Recommended)" | TAD §8.3 palette rows, §13.2, ADR-063 decision 3, Appendix B #27 | keeps the kit's five-step palette, teal → #009aa8 and pink-300 → pink-500 ([palette.ts](src/code-apps/trustee-review-portal-cards/src/cards/palette.ts#L28)); WI-0085 and WI-0088 re-closed against their amended clauses |
| R18 | Three contract-markup limits | "Accept as-is (Recommended)" | TAD §13.9 c1-c3 | unchanged; the inventory rows cite §13.9 |
| R19 | `layout.test.ts` | "Rewrite in both apps (Recommended)" | TAD §5.3 | rewritten byte-identically in both apps, asserting only accessibility properties, and back on the `contract` list ([the test](src/code-apps/trustee-review-portal-cards/src/styles/layout.test.ts#L74)) |
| R20 | Three colour substitutions | "Record them (Recommended)" | TAD §8.3 (R20 rows) | unchanged; the inventory rows cite §8.3 |

---

Verification:
- **Passed:** 888 card-app and 790 first-app unit tests (the `layout.test.ts` rewrite changes both counts); the first app's 8 visual tests; 23 Chromium visual tests at 320/390/1280; the parity gate; css-arithmetic; build-config; pipeline-config; the source gates; the bundle budget. All exit 0.
- **Measured:** 442 computed values on both renders, 411 equal, 31 classified, 0 unclassified.
- **Not verified:** anything in Power Apps itself — the host browser's `:has()`, generated-content alt text, `content: url()` on an image, `accent-color` and the `lh` unit (A-CRD-3, A-CRD-4, A-CRD-5); the first push, solution membership and sharing.

---

## 1. Implementation Summary

See the sections above. **Build configuration decision (`IMP-0836`):** unchanged — this feature amends `config/revitalise-grant-automation-build.yml` and `config/revitalise-grant-automation-pipeline.yml` (same CI slug); Revision 3 adds no step.

**Sub-agent fan-out:** not performed (0 dispatched): one stylesheet set, one probe script.

**How fidelity was checked (Revision 3).**
1. The kit's `index.html` was served locally and rendered with Playwright. Beside it ran the card app's whole-app harness on the kit's own mock data, with the same navigation on both.
2. A helper injected into both pages finds each element by the same locator, mostly visible text and the kit's radii. It reads `getComputedStyle` (or a measured box or offset for layout properties) for 92 elements and 410 properties.
3. A value counts as a match only if the strings are identical.
4. Two layout probes run at 320px and 390px.
5. The kit's verdict choice is preselected, so the built Approve card was also measured after a click.

The 18 screenshot pairs were regenerated after the last fix.

## 2. Components Changed / Created

| Component | Type | Change (Revision 3) | Items |
|---|---|---|---|
| Every card stylesheet | CSS | `line-height: normal` where the kit sets none; page reset | WI-0101, WI-0105 |
| Eyebrow (shell, cards, detail, dialog) | CSS | 13px; brand dot #e6027f | WI-0069, WI-0105 |
| Charts, CategoryBars, member dots | Component | kit palette (`cards/palette.ts`) | WI-0085, WI-0086, WI-0088, WI-0096 |
| `ApplicationFilters` | Component + CSS | native selects, fixed-width wrap items | WI-0092 |
| `ApplicationsTable`, `GroupDetailPage` | Component | `sortable={false}`: no glyph, `aria-sort="none"` | WI-0098 |
| `GroupHero` | Component + CSS | four chips; decorative badge with a generated "Members" label | WI-0097 |
| `SummaryHero` | Component + CSS | pill and first chips as two wrap units | WI-0059 |
| Tables, Type of break, DistributionChart | Component + CSS | right-aligned numeric headers; no tabular-nums; stats-table style; Playfair group total | WI-0084, WI-0089, WI-0093, WI-0096 |
| `ds/Button` (markup contract) | CSS | transitions exactly the kit's; no `:active`; ghost border none; `0 14px` input padding | WI-0102 |
| Verdict dialog (contract markup) | CSS | native tinted radios, one visible heading, 16px rhythm, left actions, 3-row notes, variables and box-sizing on the portal | WI-0104 |
| Header logo (`App.tsx` contract) | CSS | the kit's logo via `content: url()` | WI-0099 |

## 3. Data Model Changes

None.

## 4. Automation / Workflow Changes

None.

## 5. Configuration & Provisioning Changes

| Key | Environment | Notes |
|---|---|---|
| `src/styles/layout.test.ts` in **both apps** (contract) | rewritten byte-identically under TAD §5.3 rule 1 (R19): 44px floors and no fixed heights on controls, the strong control boundary, wrapping rows, container-relative grid floors and scrolling tables, focus rings, reduced-motion. The values it used to pin are presentation (first app: 32 tests → 25; card app: 23 → 29) |
| `config/code-app-variant-parity.json` | `layout.test.ts` removed from the `presentation` list and the contract glob's `except`; the contract reason names it |
| Card app `bundle-budget.json` | build | CSS max 152,800 (measured 148,639); JS max 871,100 (measured 845,809) |
| Card app `power.config.json` → `appId` | DEV | still `null` (A-TR-14) |

No pipeline entry or provisioning script changed.

## 6. Security Controls Implemented

Unchanged and held by contract files (no contract file changed in Revision 3). The verdict radios are still the contract `RadioGroup`'s own inputs: shown instead of hidden, same `name`, same keyboard model, so EF-05 and "no preselected verdict" hold, and `VerdictForm.test.tsx` passes unchanged.

## 7. Known Limitations / Deferred Items

See *What is still open*. The verdict dialog's eyebrow and the group badge's "Members" are generated content with empty alternative text.

## 8. Build Instructions

No new step. Run `config/revitalise-grant-automation-build.yml` as before.

## 9. Test Guidance

- **Re-measure, don't eyeball.** Copy `measure/measure.mjs` into the card app folder and run `node .measure.mjs <scratchpad>/measure "<DS root>"`; it rewrites `measured.json`. `measure/inventory.py` turns that into the §11 tables.
- **At 320px**, the score fields stack, and the page never scrolls sideways. The kit itself does scroll sideways (IMP-1001).
- **The dialog**: tab into the choices. The native radio shows the focus ring, and arrow keys move between choices as before.

## 10. Unvalidated Assumptions Register (C-TECH-052)

| ID | Claim (one sentence — BOTH directions if it is a conditional) | Where in source | Evidence | Why not verified | Cheapest verification (BOTH directions) | Status |
|---|---|---|---|---|---|---|
| A-TR-14 | A new Code App's `appId` is assigned by the platform on its first push, so a `null` appId is a valid pre-push state, and the push does not reuse any other app's id | `scripts/verify-code-app-variant-parity.py`, `config/revitalise-grant-automation-pipeline.yml` | E3 | No live write in this dispatch | First push: `pac code list` shows two apps with different ids, and the first app's id and `lastmodifiedtime` are unchanged | OPEN |
| A-TR-15 | `pac code push --solutionName` adds the second app to `RevitaliseGrantAutomation`, and does not remove or replace the first app's component | `config/revitalise-grant-automation-pipeline.yml` | E4 | Never observed | `solutioncomponents` for the solution, type 300: two rows, one per appId | OPEN |
| A-TR-16 | A CanView share of the second app to the trustee group team works as it did for the first app, and grants nothing beyond view | `config/revitalise-grant-automation-pipeline.yml` | E3 | Needs the admin centre | Human check of the role assignment in the admin centre | OPEN |
| A-TR-17 | Removing a Code App from the solution deletes it downstream on managed upgrade — not needed while the business chooses before the first promotion | `config/revitalise-grant-automation-pipeline.yml` | E2 | Avoidable by ordering (TAD §9.3) | Only if a second app is ever promoted: observe on TST/ACC | OPEN |
| A-CRD-1 | The second app may reuse the first app's `connectionReferences` block, key included, in the same environment, and the push does not rebind the first app's connection | `config/code-app-variant-parity.json` | E4 | No live push | After the first push, both apps open signed in and read data | OPEN |
| A-CRD-2 | Fluent's rendered slot classes `.fui-Textarea` (the box) and `.fui-Textarea__textarea` (the element) are the ones the notes styles target, and styling them does not change the field's behaviour | [detail.module.css](src/code-apps/trustee-review-portal-cards/src/styles/detail.module.css) | E2 + Chromium render of the harness | Not rendered in the Power Apps host | Open the detail page in DEV: 12px radius and grey fill on the notes box, and typing updates the character count | OPEN |
| A-CRD-3 | The dialog, radio and textarea slot classes the card styles target are the rendered ones, and the Power Apps player honours generated-content alt text (`content: "…" / ""`) so the dialog eyebrow is drawn and NOT announced | [cards.module.css](src/code-apps/trustee-review-portal-cards/src/styles/cards.module.css) | E2 + Chromium render | Not rendered in the Power Apps host | Open "Record verdict" in DEV: the eyebrow shows; a screen reader reads the title "Record a verdict for …" without "Record verdict" before it | OPEN |
| A-CRD-4 | The Power Apps player's browser supports `:has()`, so the grey-50 page reaches the body while the app is mounted, and does not paint it when the app is not | [app.module.css](src/code-apps/trustee-review-portal-cards/src/styles/app.module.css) | Chromium only | Not rendered in the host | Open the app in DEV: grey page edge to edge; the body stays white in the maker portal outside the app | OPEN |
| A-CRD-5 | The Power Apps player's browser paints `content: url()` on an `<img>` (so the kit's logo shows, not the strapline logo), honours `accent-color` on the verdict radios and the `lh` unit on the notes box; where it does not, the strapline logo, Fluent-default radio tint and a 96px notes box show instead | [app.module.css](src/code-apps/trustee-review-portal-cards/src/styles/app.module.css) | Chromium only | Not rendered in the host | Open the app in DEV: logo without strapline; open "Record verdict": radios tinted pink/purple/grey, notes box three lines high | OPEN |

## 11. Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

### Verification level reached

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| Card app source | V1 + V2 (local build) | macOS, local | `npm run typecheck` 0, `npm run lint` 0, `npm run coverage` 0 (49 files, 888 tests), `npm run build` 0 |
| Card app geometry | V2 in headless Chromium | macOS, local | `npm run test:visual` 0 — 23 tests |
| Design fidelity | V2, measured | macOS, headless Chromium | 107 probes, 442 computed values on both renders, 411 equal, 31 classified |
| First app | changed only by the identical `layout.test.ts` (R19) | macOS, local | parity P1: 124 contract files byte-identical; `npm run coverage` 0 (45 files, 790 tests), typecheck 0, lint 0 |
| Parity gate | V1, both directions | macOS, local | real tree PASS (124 contract, 60 presentation) |
| Build and pipeline config | V1 | macOS, local | `verify-build-config.py` 0, `verify-pipeline-config.py` 0, `run-source-gates.py` 0 |
| Push, share, the host browser | **not reached** | — | no environment write in this dispatch |

### Side-by-side screenshots

18 pairs, regenerated after the last Revision 3 fix, named `{screen}-{width}-{design|built}.png`, in `/private/tmp/claude-501/-Users-xvl-Library-CloudStorage-OneDrive-SharedLibraries-ArgelisConsultancy-Revitalise-Respite-Holidays---Optimisation-Grant-Application-Process-Repository-Revitalise/2d33a38e-46cc-461e-b212-a0ddf04d7d87/scratchpad/fidelity/`: `round-overview`, `group-applications`, `group-detail`, `individual-applications`, `application-detail`, `verdict-dialog`, each at 1280, 390 and 320. They are not in the repository (`build/fidelity/` is not gitignored, IMP-1000).

<a id="style-inventory-measured"></a>

### Style inventory (measured)

**How to read it.** One row per element:
- the middle column lists the properties whose computed value is identical on both renders;
- the last column lists every property that differs, design value → built value, and why.

The kit's declared values are not repeated here. They are what the kit renders, which is what was measured.

**Totals:**

| Elements | Properties compared | Equal | Different |
|---|---|---|---|
| 107 | 442 | **411** | 31 |

The 31 differences:

| Category | Count | What they are |
|---|---|---|
| (a) contrast | 14 | contrast substitutions, and the strong form-control border (§8.3) |
| (b) kept content | 3 | the unpreselected verdict, the derived shared-dates span, a column width set by the source's data |
| (c) cannot express | 11 | 44px targets (row links and the data-table toggle), contract markup (§13.9), the contract font token, the `<dl>` receipt's -1px |
| Reviewer font decision | 3 | the font, and two heights proven to follow from it |
| Unclassified | **0** | — |

The Revision 2 grep-based inventory (86 rows) is withdrawn.

**Categories.**
- **(a)** TAD §8.2/§8.3 contrast substitutions, including the three R20 rows and the R17 palette rows.
- **(b)** Content kept from source (ADR-061, Appendix B).
- **(c)** TAD §13.9 c1-c3 (R18), the contract font token's fallback list, or the design's own non-negotiable 8 (44px targets, `design_handoff_application_detail/README.md:22`).

**Reviewer decision.** Body font, verbatim: "Keep the font that is currently used in the app."

#### Shell and Round overview (1280px)

| Element | Equal computed values | Different computed values (design → built) and why |
|---|---|---|
| Header bar | position `sticky`; padding-top `16px`; padding-left `48px`; background-color `rgb(255, 255, 255)`; box-shadow `rgba(43, 43, 43, 0.05) 0px 1px 0px 0px, rgba(43, 43, 43, 0.06) 0px 4px 16px 0px`; row-gap `16px` | **match** |
| Logo image | height `44px`; width `142px`; image `(see logo file probe)` | **match** |
| 'Signed in as' sentence | font-size `15px`; line-height `normal` | **color**: `rgb(138, 138, 138)` → `rgb(90, 90, 90)` — deviation (a): the kit's `--text-muted` #8a8a8a is 3.45:1 — TAD §8.3, ADR-037 correction 2 |
| Signed-in user name | — | **font-weight**: `700` → `400` — deviation (c): TAD §13.9 c1 (R18, accepted as-is): `App.tsx` (contract) renders the name inside one template string<br>**color**: `rgb(43, 43, 43)` → `rgb(90, 90, 90)` — deviation (c): TAD §13.9 c1, as the row above |
| Nav bar container | padding-top `6px`; padding-left `6px`; column-gap `4px`; border-top-left-radius `999px`; background-color `rgb(255, 255, 255)`; box-shadow `rgba(43, 43, 43, 0.04) 0px 1px 2px 0px, rgba(43, 43, 43, 0.07) 0px 6px 20px 0px` | **match** |
| Nav tab, selected | color `rgb(255, 255, 255)`; font-size `15px`; font-weight `700`; line-height `normal`; padding-left `18px`; height `44px`; border-top-left-radius `999px`; box-shadow `rgba(230, 2, 127, 0.18) 0px 2px 6px 0px` | **background-color**: `rgb(230, 2, 127)` → `rgb(196, 0, 108)` — deviation (a): white 15px bold on #e6027f is 4.49:1 — TAD §8.3 (nav bar selected tab) |
| Nav tab, not selected | background-color `rgba(0, 0, 0, 0)`; color `rgb(43, 43, 43)`; font-size `15px`; font-weight `700`; padding-left `18px`; height `44px` | **match** |
| Main column | padding-top `32px`; padding-left `48px`; max-width `1200px`; row-gap `24px` | **match** |
| Page title h1 | font-size `44px`; line-height `52.8px`; font-weight `700`; color `rgb(43, 43, 43)` | **match** |
| Body text font | — | **font-family**: `"Nunito Sans", "Segoe UI", Arial, sans-serif` → `Aptos, "Segoe UI Variable", "Segoe UI", -apple-system, "system-ui", Roboto, Helvetica, Arial, sans-serif` — reviewer decision: reviewer decision, verbatim: "Keep the font that is currently used in the app." |
| Eyebrow 'This round' (hero) | font-size `13px`; font-weight `700`; line-height `normal`; color `rgb(73, 52, 91)`; letter-spacing `1.04px`; text-transform `uppercase`; column-gap `8px` | **match** |
| Eyebrow 'Round progress' (pink, on a card) | font-size `13px`; font-weight `700`; line-height `normal`; letter-spacing `1.04px`; text-transform `uppercase` | **color**: `rgb(230, 2, 127)` → `rgb(196, 0, 108)` — deviation (a): #e6027f text is 4.49:1 on white — TAD §8.3 (eyebrow rows) |
| Eyebrow dot (pink) | background-color `rgb(230, 2, 127)`; width `8px`; height `8px` | **match** |
| Round hero band | padding-top `32px`; padding-right `32px`; padding-bottom `32px`; padding-left `32px`; border-top-left-radius `20px`; background-color `rgba(0, 0, 0, 0)`; background-image `linear-gradient(135deg, rgb(237, 232, 241) 0%, rgb(253, 241, 248) 100%)`; box-shadow `rgba(43, 43, 43, 0.04) 0px 1px 2px 0px, rgba(43, 43, 43, 0.07) 0px 6px 20px 0px`; row-gap `32px` | **match** |
| Hero heading h2 | font-size `32px`; line-height `normal`; font-weight `700`; color `rgb(43, 43, 43)` | **match** |
| Hero badge circle | width `120px`; height `120px`; background-color `rgb(255, 255, 255)`; box-shadow `rgba(73, 52, 91, 0.14) 0px 6px 20px 0px` | **match** |
| Hero badge value | font-size `52px`; line-height `52px`; color `rgb(230, 2, 127)` | **match** |
| Card (Round progress) | padding-top `32px`; padding-right `32px`; padding-bottom `32px`; padding-left `32px`; border-top-left-radius `16px`; background-color `rgb(255, 255, 255)`; background-image `none`; box-shadow `rgba(43, 43, 43, 0.04) 0px 1px 2px 0px, rgba(43, 43, 43, 0.07) 0px 6px 20px 0px`; row-gap `20px` | **match** |
| Card heading h2 | font-size `24px`; line-height `normal`; font-weight `700`; color `rgb(43, 43, 43)`; margin-bottom `0px` | **match** |
| Progress tile value (40px) | font-size `40px`; line-height `42px`; color `rgb(43, 43, 43)` | **match** |
| Progress tile | padding-top `20px`; padding-left `20px`; border-top-left-radius `14px`; background-color `rgb(253, 241, 248)`; row-gap `8px` | **match** |
| Chart heading h3 ('Gender') | font-size `20px`; line-height `normal`; font-weight `700`; color `rgb(43, 43, 43)` | **match** |
| 'Counted over' line | font-size `15px`; line-height `normal`; color `rgb(90, 90, 90)` | **match** |
| 'Show the data table' toggle | font-weight `700`; font-size `16px`; text-decoration-line `underline`; border-top-width `0px`; padding-left `0px` | **color**: `rgb(230, 2, 127)` → `rgb(204, 0, 120)` — deviation (a): #e6027f link text is 4.49:1; the app's `--link-default` #cc0078 is 5.47:1 — TAD §8.3 (R20 rows, link text)<br>**min-height**: `0px` → `44px` — deviation (c): 44px minimum target, as the Group and Individual row links: the design's non-negotiable 8 states 44px for buttons (`design_handoff_application_detail/README.md:22`); this toggle and the row links are buttons in the markup and extend it under the same rule |
| Category bar fills (Ethnic group), in order | — | **colours**: `rgb(230, 2, 127) \| rgb(73, 52, 91) \| rgb(20, 173, 187) \| rgb(242, 140, 198) \| rgb(106, 87, 116) \| rgb(230, 2, 127)` → `rgb(230, 2, 127) \| rgb(73, 52, 91) \| rgb(0, 154, 168) \| rgb(236, 78, 163) \| rgb(106, 87, 116) \| rgb(230, 2, 127)` — deviation (a): marks 1, 2, 5 and the wrap are the kit's own; mark 3 teal #14adbb → #009aa8 (2.72:1, TAD §8.3, Appendix B #27); mark 4 pink-300 #f28cc6 → pink-500 #ec4ea3 (pink-300 is 2.25:1, TAD §8.3). The palette is the kit's by R17 (TAD §8.3 palette rows, Appendix B #27) |
| Age range column fill | background-color `rgb(73, 52, 91)` | **match** |
| Donut ring gradient | — | **background-image**: `conic-gradient(rgb(230, 2, 127) 0%, rgb(230, 2, 127) 60.4167%, rgb(73, 52, 91) 60.4167%, rgb(73, 52, 91) 85.4167%, rgb(20, 173, 187) 85.4167%, rgb(20, 173, 187) 100%)` → `conic-gradient(rgb(230, 2, 127) 0%, rgb(230, 2, 127) 60.4%, rgb(73, 52, 91) 60.4%, rgb(73, 52, 91) 85.4%, rgb(0, 154, 168) 85.4%, rgb(0, 154, 168) 100%)` — deviation (a): slice 3 teal → #009aa8 (TAD §8.3); the stop positions differ by rounding only — the app plots the source's one-decimal share (60.4%) where the kit divides its mock counts (60.4167%), ADR-061 (b) |
| Category bar value text | white-space `normal`; color `rgb(75, 75, 75)`; font-size `15px` | **match** |
| Stats table numeric header | text-align `right`; padding-left `8px`; font-size `15px`; color `rgb(43, 43, 43)`; font-weight `700`; background-color `rgba(0, 0, 0, 0)`; text-transform `none` | **match** |
| Stats table numeric cell | text-align `right`; padding-left `8px`; font-size `15px`; font-variant-numeric `normal` | **match** |
| Type of break header cell, against the kit's stats-table header (no Type of break in the kit) | text-align `right`; padding-left `8px`; padding-top `6px`; font-size `15px`; color `rgb(43, 43, 43)`; font-weight `700`; background-color `rgba(0, 0, 0, 0)`; text-transform `none`; letter-spacing `normal` | **match** |
| Type of break body cell, against the kit's stats-table cell | text-align `right`; padding-left `8px`; padding-top `6px`; font-size `15px` | **match** |
| Type of break caption, against the kit's 'Counted over' line | font-size `15px`; color `rgb(90, 90, 90)`; padding-left `0px`; padding-top `0px`; background-color `rgba(0, 0, 0, 0)`; text-align `start` | **match** |
| Money tile value (26px) | font-size `26px`; line-height `29.9px`; color `rgb(43, 43, 43)` | **match** |

#### Group applications (1280px)

| Element | Equal computed values | Different computed values (design → built) and why |
|---|---|---|
| Table card | border-top-left-radius `16px`; box-shadow `rgba(43, 43, 43, 0.04) 0px 1px 2px 0px, rgba(43, 43, 43, 0.07) 0px 6px 20px 0px`; background-color `rgb(255, 255, 255)`; overflow-x `auto` | **match** |
| Table caption | font-size `15px`; color `rgb(75, 75, 75)`; padding-top `24px`; padding-left `24px`; text-align `left` | **match** |
| Header cell | background-color `rgb(248, 247, 247)`; font-size `12px`; font-weight `700`; letter-spacing `0.72px`; text-transform `uppercase`; color `rgb(75, 75, 75)`; line-height `normal` | **match** |
| Header label inset from the cell edge | left inset `16px`; top inset `16px` | **match** |

#### Individual applications (1280px)

| Element | Equal computed values | Different computed values (design → built) and why |
|---|---|---|
| Sortable header button | font-size `12px`; text-transform `none`; letter-spacing `normal`; column-gap `6px` | **match** |

#### Group applications (1280px)

| Element | Equal computed values | Different computed values (design → built) and why |
|---|---|---|
| Body cell | padding-top `16px`; padding-left `16px`; font-size `17px`; vertical-align `middle`; line-height `normal`; color `rgb(90, 90, 90)` | **match** |
| Row link | font-weight `700`; text-decoration-line `underline`; padding-left `0px`; border-top-width `0px` | **color**: `rgb(230, 2, 127)` → `rgb(204, 0, 120)` — deviation (a): #e6027f link text is 4.49:1; the app's `--link-default` #cc0078 is 5.47:1 — TAD §8.3 (R20 rows, link text)<br>**min-height**: `auto` → `44px` — deviation (c): 44px minimum targets — the design's own non-negotiable 8 (`design_handoff_application_detail/README.md:22`) |
| Group avatar | width `36px`; height `36px`; border-top-left-radius `12px`; background-color `rgba(0, 0, 0, 0)`; background-image `linear-gradient(135deg, rgb(237, 232, 241), rgb(253, 241, 248))`; color `rgb(230, 2, 127)`; font-size `15px`; font-weight `700` | **match** |
| Member dot colours (first row) | colours `rgb(230, 2, 127) \| rgb(73, 52, 91) \| rgb(20, 173, 187)`; size `22x22 22x22 22x22`; border `2px rgb(255, 255, 255) \| 2px rgb(255, 255, 255) \| 2px rgb(255, 255, 255)` | **match** |
| Group total cell | font-size `20px`; color `rgb(43, 43, 43)`; font-variant-numeric `normal`; text-align `right` | **font-family**: `"Playfair Display", Georgia, "Times New Roman", serif` → `"Playfair Display", Georgia, Cambria, "Times New Roman", Times, serif` — deviation (c): same first family, Playfair Display; the fallback list is the CONTRACT token `--font-display` (`ds-tokens.css`), identical in both apps (ADR-060) |
| Members numeric cell | text-align `right`; font-variant-numeric `normal` | **match** |

#### Group detail (1280px)

| Element | Equal computed values | Different computed values (design → built) and why |
|---|---|---|
| Circumstance score header glyph | glyph `none`; aria-sort `none` | **match** |
| Hero fact chips | chips `Group code, Members, Group total requested, Shared dates` | **match** |
| Fact chip | padding-top `8px`; padding-left `14px`; border-top-left-radius `12px`; background-color `rgba(255, 255, 255, 0.85)`; box-shadow `rgba(73, 52, 91, 0.08) 0px 1px 3px 0px`; row-gap `2px` | **match** |
| Fact chip label | font-size `12px`; color `rgb(90, 90, 90)`; line-height `normal` | **match** |
| Fact chip value | font-size `15px`; font-weight `700`; color `rgb(43, 43, 43)`; line-height `normal` | **match** |
| Hero heading h2 | font-size `32px`; line-height `normal`; color `rgb(43, 43, 43)` | **match** |
| Eyebrow 'Applications in this group' | font-size `13px`; font-weight `700`; line-height `normal`; color `rgb(73, 52, 91)`; letter-spacing `1.04px`; text-transform `uppercase` | **match** |

#### Individual applications (1280px)

| Element | Equal computed values | Different computed values (design → built) and why |
|---|---|---|
| Sortable header label inset from the cell edge | top inset `16px`; glyph right inset `16px` | **match** |
| Filter card | padding-top `24px`; padding-right `32px`; padding-bottom `24px`; padding-left `32px`; border-top-left-radius `16px`; background-color `rgb(255, 255, 255)`; background-image `none`; box-shadow `rgba(43, 43, 43, 0.04) 0px 1px 2px 0px, rgba(43, 43, 43, 0.07) 0px 6px 20px 0px`; row-gap `16px` | **match** |
| Filter label 'Review round' | font-size `15px`; color `rgb(43, 43, 43)`; line-height `normal`; font-weight `400` | **match** |
| Review round select | font-size `17px`; padding-left `14px`; padding-top `0px`; border-top-width `1px`; border-top-left-radius `12px`; background-color `rgb(248, 247, 247)`; height `44px`; appearance `auto`; color `rgb(43, 43, 43)` | **border-top-color**: `rgb(224, 222, 222)` → `rgb(138, 138, 138)` — deviation (a): the strong control border — ADR-037 correction 4, TAD §8.3 (the 1px width matches) |
| Score from input | padding-left `14px`; border-top-width `1px`; border-top-left-radius `12px`; background-color `rgb(248, 247, 247)`; height `44px`; width `120px` | **border-top-color**: `rgb(224, 222, 222)` → `rgb(138, 138, 138)` — deviation (a): the strong control border, 1px #8a8a8a in place of the kit's 1.5px grey-200 — TAD §8.3 'Form-control borders', ADR-037 correction 4; the 3:1 non-text contrast `ds-tokens.test.ts` (contract) asserts. (The 1.5px kit width computes to 1px at 1x in Chromium, so the width row reads equal; the declared widths differ.) |
| Filter field widths (round, score, reference) | round `200px`; score `120px`; reference `260px` | **match** |
| Secondary button 'Clear filters' | border-top-color `rgb(230, 2, 127)`; border-top-width `2px`; background-color `rgb(255, 255, 255)`; padding-left `28px`; padding-top `13px`; font-size `17px`; font-weight `700`; line-height `normal`; border-top-left-radius `999px`; box-shadow `rgba(43, 43, 43, 0.06) 0px 1px 2px 0px`; transition-property `transform, box-shadow` | **color**: `rgb(230, 2, 127)` → `rgb(196, 0, 108)` — deviation (a): #e6027f 17px text is 4.49:1 → `--pink-700` (5.89:1); the 2px border keeps #e6027f. TAD §8.3 (R20 rows, secondary-button text) |
| Primary button 'Record verdict' (row) | color `rgb(255, 255, 255)`; box-shadow `rgba(158, 0, 87, 0.12) 0px 1px 2px 0px, rgba(230, 2, 127, 0.12) 0px 3px 8px 0px`; padding-left `28px`; border-top-left-radius `999px`; font-size `17px`; line-height `normal` | **background-image**: `linear-gradient(rgb(236, 26, 140) 0%, rgb(230, 2, 127) 100%)` → `linear-gradient(rgb(196, 0, 108) 0%, rgb(158, 0, 87) 100%)` — deviation (a): white on #ec1a8c is 4.12:1 — TAD §8.3 (primary gradient, lightest stop) |
| Status pill | background-color `rgb(253, 241, 248)`; color `rgb(158, 0, 87)`; padding-left `10px`; border-top-left-radius `999px`; font-size `13px`; font-weight `700`; line-height `normal`; white-space `nowrap` | **match** |
| Score chip value | font-size `20px`; line-height `normal`; font-variant-numeric `normal`; color `rgb(43, 43, 43)` | **font-family**: `"Playfair Display", Georgia, "Times New Roman", serif` → `"Playfair Display", Georgia, Cambria, "Times New Roman", Times, serif` — deviation (c): same first family, Playfair Display; the fallback list is the CONTRACT token `--font-display` (`ds-tokens.css`), identical in both apps (ADR-060) |
| Row link | font-weight `700` | **color**: `rgb(230, 2, 127)` → `rgb(204, 0, 120)` — deviation (a): #e6027f link text is 4.49:1; the app's `--link-default` #cc0078 is 5.47:1 — TAD §8.3 (R20 rows, link text)<br>**min-height**: `0px` → `44px` — deviation (c): 44px minimum targets — the design's own non-negotiable 8 (`design_handoff_application_detail/README.md:22`) |

#### Individual applications (320px)

| Element | Equal computed values | Different computed values (design → built) and why |
|---|---|---|
| Score from / Score to at 320px | layout `stacked` | **match** |
| Page width at 320px | scrollWidth `320px` | **match** |

#### Application detail (390px)

| Element | Equal computed values | Different computed values (design → built) and why |
|---|---|---|
| Status pill shares its line with 'Review round' at 390px | pill line `alone` | **match** |

#### Verdict dialog (1280px)

| Element | Equal computed values | Different computed values (design → built) and why |
|---|---|---|
| Dialog surface | border-top-left-radius `20px`; padding-top `24px`; padding-left `24px`; width `520px`; box-shadow `rgba(43, 43, 43, 0.14) 0px 12px 32px 0px`; background-color `rgb(255, 255, 255)` | **match** |
| Dialog body block gap | title block to hint `16px` | **match** |
| Headings in the dialog (visible) | visible headings `1` | **match** |
| Eyebrow 'Record verdict' | font-size `13px`; font-weight `700`; letter-spacing `1.04px`; text-transform `uppercase` | **color**: `rgb(230, 2, 127)` → `rgb(196, 0, 108)` — deviation (a): #e6027f text is 4.49:1 on white — TAD §8.3 (eyebrow rows) |
| Dialog title h2 | font-size `24px`; line-height `normal`; font-weight `700`; color `rgb(43, 43, 43)` | **match** |
| Trustee-slot sentence | font-size `15px`; color `rgb(90, 90, 90)`; line-height `normal` | **match** |
| Choice card (Approve) | padding-top `14px`; padding-left `16px`; column-gap `10px`; border-top-left-radius `14px`; border-top-width `2px` | **background-color**: `rgb(255, 255, 255)` → `rgb(248, 247, 247)` — deviation (b): the kit preselects Approve; the source preselects nothing (Appendix B #17). Once checked, the card matches the kit's exactly — see 'Choice card (Approve) once checked'<br>**height**: `54px` → `50px` — reviewer decision: a consequence of the body-font decision, measured: the kit rendered with the app's body font gives 50px — the built value |
| Choice card (Defer, unchecked) | background-color `rgb(248, 247, 247)`; border-top-color `rgba(0, 0, 0, 0)`; box-shadow `none` | **match** |
| Choice card (Approve) once checked | background-color `rgb(255, 255, 255)`; border-top-color `rgb(230, 2, 127)`; border-top-width `2px`; box-shadow `rgba(43, 43, 43, 0.08) 0px 4px 14px 0px` | **match** |
| Radio control | width `18px`; height `18px`; opacity `1`; position `static`; accent-color `rgb(230, 2, 127)`; margin-top `0px` | **match** |
| Radio control (Defer) | accent-color `rgb(73, 52, 91)` | **match** |
| Choice text | font-weight `700`; color `rgb(43, 43, 43)`; padding-left `0px`; font-size `16px` | **match** |
| Notes label | font-size `15px`; color `rgb(43, 43, 43)`; font-weight `400` | **match** |
| Notes textarea text box | padding-top `12px`; padding-left `14px`; font-size `17px`; line-height `normal` | **match** |
| Notes box outer size (bordered element) | width `472px` | **height**: `95px` → `86px` — reviewer decision: a consequence of the body-font decision, measured: the kit's `rows={3}` box rendered with the app's body font is 86px — the built value |
| Notes textarea frame | border-top-width `1px`; border-top-color `rgb(224, 222, 222)`; border-top-left-radius `12px`; background-color `rgb(248, 247, 247)` | **match** |
| Save and the dismiss button on one row | — | **row**: `one row` → `two rows` — deviation (c): TAD §13.9 c2 (R18, accepted as-is): Save is rendered by `VerdictForm.tsx`, Close by `VerdictDialog.tsx`; the 'Close' label is Appendix B #19 (b)<br>**dismiss x**: `right of Save` → `below Save` — deviation (c): TAD §13.9 c2, as the row above |

#### Application detail (1280px)

| Element | Equal computed values | Different computed values (design → built) and why |
|---|---|---|
| Summary hero band | padding-top `32px`; padding-right `32px`; padding-bottom `32px`; padding-left `32px`; border-top-left-radius `20px`; background-color `rgba(0, 0, 0, 0)`; background-image `linear-gradient(135deg, rgb(237, 232, 241) 0%, rgb(253, 241, 248) 100%)`; box-shadow `rgba(43, 43, 43, 0.04) 0px 1px 2px 0px, rgba(43, 43, 43, 0.07) 0px 6px 20px 0px` | **match** |
| Hero heading h2 | font-size `32px`; line-height `normal`; color `rgb(43, 43, 43)` | **match** |
| Eyebrow 'The break' | font-size `13px`; font-weight `700`; line-height `normal`; color `rgb(73, 52, 91)`; letter-spacing `1.04px`; text-transform `uppercase` | **match** |
| Panel card ('The break') | padding-top `32px`; padding-right `32px`; padding-bottom `32px`; padding-left `32px`; border-top-left-radius `16px`; background-color `rgb(255, 255, 255)`; background-image `none`; box-shadow `rgba(43, 43, 43, 0.05) 0px 2px 4px 0px, rgba(43, 43, 43, 0.12) 0px 16px 40px 0px`; row-gap `20px` | **match** |
| Panel heading h2 | font-size `24px`; line-height `normal`; font-weight `700`; color `rgb(43, 43, 43)` | **match** |
| Hero fact chip | padding-top `8px`; padding-left `14px`; border-top-left-radius `12px`; background-color `rgba(255, 255, 255, 0.85)`; box-shadow `rgba(73, 52, 91, 0.08) 0px 1px 3px 0px` | **match** |
| Hero fact chip label | font-size `12px`; color `rgb(90, 90, 90)`; line-height `normal` | **match** |
| Score badge value | font-size `46px`; line-height `48.3px`; color `rgb(230, 2, 127)` | **match** |
| Status pill | background-color `rgb(253, 241, 248)`; color `rgb(158, 0, 87)`; padding-left `10px`; font-size `13px`; font-weight `700`; line-height `normal` | **match** |

#### Shell and Round overview (1280px)

| Element | Equal computed values | Different computed values (design → built) and why |
|---|---|---|
| --text-heading as a ds component resolves it | color `rgb(43, 43, 43)` | **match** |
| Text rendering on the app's text | -webkit-font-smoothing `antialiased` | **match** |
| Hero 'Opened' term | display `inline`; font-weight `700` | **match** |
| Hero 'Opened' line container | display `block` | **match** |

#### Round overview (390px)

| Element | Equal computed values | Different computed values (design → built) and why |
|---|---|---|
| Column axis label at 390px | overflow-wrap `normal`; min-width `auto`; flex-grow `1` | **match** |
| Round overview page width at 390px | overflow `0px` | **match** |

#### Group applications (390px)

| Element | Equal computed values | Different computed values (design → built) and why |
|---|---|---|
| Group avatar tile at 390px | flex-shrink `1`; flex-grow `0`; height `36px` | **match** |

#### Group detail (1280px)

| Element | Equal computed values | Different computed values (design → built) and why |
|---|---|---|
| Unsorted header label box (Circumstance score) | display `inline-flex`; text-align `center`; column-gap `6px` | **match** |
| Unsorted header label: right edge to cell edge | — | **right inset**: `38px` → `35px` — deviation (b): the label box now matches the kit's (inline-flex, centred, 6px gap — equal rows above). The 3px left is the column width, set by the table's auto layout from the cell content (ADR-061 data, not the kit's mock): measured, the kit rendered with the app's font draws the same 84px line in a 154px column against the build's 149px |
| Members-table row link | font-weight `700` | **color**: `rgb(230, 2, 127)` → `rgb(204, 0, 120)` — deviation (a): #e6027f link text is 4.49:1; the app's `--link-default` #cc0078 is 5.47:1 — TAD §8.3 (R20 rows, link text)<br>**min-height**: `0px` → `44px` — deviation (c): 44px minimum target, as the Group and Individual row links (`design_handoff_application_detail/README.md:22`, non-negotiable 8, extended to row-link buttons) |

#### Group applications (1280px)

| Element | Equal computed values | Different computed values (design → built) and why |
|---|---|---|
| Shared dates cell, GRP-014 | — | **text**: `Dates differ between members` → `5 Oct 2026 to 14 Dec 2026` — deviation (b): content from source: the app derives the members' shared span with `formatDateRange` (TAD §13.4 keeps the columns and their formatting); the kit's mock prints a fixed sentence |

#### Application detail (1280px)

| Element | Equal computed values | Different computed values (design → built) and why |
|---|---|---|
| Cost receipt first line | border-top-width `1px`; border-top-style `solid`; border-top-color `rgb(240, 238, 238)` | **margin-top**: `0px` → `-1px` — deviation (c): the kit pulls its first rule up 1px with a wrapper `<div style=marginTop:-1px>` round the lines (ApplicationDetail.jsx:39); the build's receipt is a `<dl>`, whose content model allows no wrapper of that kind, so the -1px sits on the first line itself. The rule it draws is equal (border rows above) |
| Hero row-2 chip block | align-items `normal`; flex-wrap `wrap` | **match** |
| Status pill | white-space `nowrap` | **match** |

#### Verdict dialog (390px)

| Element | Equal computed values | Different computed values (design → built) and why |
|---|---|---|
| Dialog surface at 390px | left gutter `16px`; right gutter `16px`; border-bottom-left-radius `20px` | **match** |

#### Not measured (hover, focus and motion states)

These are pointer, focus or motion states that the probe script does not drive. Their declarations were compared, and none is counted in the totals above.

| Element | Kit | Built | Result |
|---|---|---|---|
| Nav tab hover | grey-50 (`index.html:16`) | grey-50 | declared equal, not measured |
| Card hover lift | shadow 0 2px 4px …, 0 16px 40px …, translateY(-2px) (`index.html:10`) | same, off under `prefers-reduced-motion` | declared equal, not measured |
| Primary button hover | pink-600 → pink-700 (`index.html:19`) | pink-800 → #51002c | deviation (a), TAD §8.3 (R20 rows: 8.10:1 and 15.15:1) |
| Secondary hover | pink-50, shadow 0 2px 6px … (`index.html:21`) | same | declared equal, not measured |
| Button transitions | transform 120ms, box-shadow 200ms (`index.html:17`) | same, the background transition removed | declared equal, not measured |
| Focus ring | 3px pink-500, 2px offset (`index.html:22`) | 3px black, 2px offset | deviation (a), ADR-037 correction 3, TAD §8.3 |
| Table row hover | grey-50 (`index.html:13`) | grey-50 | declared equal, not measured |

#### Audit items: where each one landed

| Audit category | Count | Outcome |
|---|---|---|
| none | 34 | fixed; every one the probes cover now measures equal, apart from the rows listed as (c) or reviewer above |
| claimed-but-unrecorded | 15 | fixed: palette, pink #e6027f for graphics, member dots, Members chip, logo, primary hover list, native selects and radios, the second dialog heading. Accepted as (c) by R18 (TAD §13.9): bold signed-in name, Save/Cancel row, label and counter. Kept as (c): 44px row links. Recorded by R20 (TAD §8.3): link and secondary text, the hover stop |
| a / b / open-decision | 20 | kept and recorded above; the body font is your decision |

### Tool warnings triaged (C-TECH-055)

<a id="bundle"></a>

| Warning | Source step | Resolved / Accepted | Rationale if accepted |
|---|---|---|---|
| Vite "Some chunks are larger than 500 kB" — JS 845,809 bytes, CSS 148,639 bytes | `code-app-build-cards` | Accepted | CSS grew by the kit's 26,532-byte logo inlined as base64 (`?inline`, for App.tsx's A-BRAND-1 reason); JS shrank with Fluent's `Select` gone. Budgeted at ~3% headroom (871,100 / 152,800). Original triage: [trustee-portal-visual-refresh Dev Summary](docs/development/trustee-portal-visual-refresh-dev-summary.md#L2682) |
| `npm warn deprecated glob@10.5.0` | `code-app-install-cards` | Accepted | Dev-only, identical lockfile — [triaged here](docs/development/trustee-portal-visual-refresh-dev-summary.md#L2683) |
| `npm audit`: 3 moderate (GHSA-82fw-gwwq-j7x9, the vitest chain); exit 0 at `--audit-level=high` | `code-app-audit-cards` | Accepted | Same advisory, identical lockfile — [triaged here](docs/development/revitalise-grant-automation-dev-summary.md#L7515) |
| Repeated "Keyborg instance kN is being disposed incorrectly." on stderr | `code-app-unit-tests-cards` | Accepted | Fluent internal, production-guarded — [triaged here](docs/development/trustee-portal-visual-refresh-dev-summary.md#L2685) |
| `code-app-composition-root` REPORT lines (2 per app) | `code-app-composition-root` | Accepted | Pre-existing in the first app, reproduced by the copy |
| `npm warn deprecated glob@10.5.0` (first app) | `code-app-install` (`npm --prefix src/code-apps/trustee-review-portal ci`) | Accepted | The same dev/test-only transitive dependency as the card app's row above (`@vitest/coverage-v8` → `test-exclude` → `glob@10.5.0`, absent from `dist/`); the first app's lockfile is the one the parity gate holds byte-identical. Already triaged for this app — [trustee-portal-visual-refresh Dev Summary](docs/development/trustee-portal-visual-refresh-dev-summary.md#L2683) |
| Vite "Some chunks are larger than 500 kB" (first app) — JS 1,210,181 bytes (1,210.18 kB), CSS 77,641 bytes (77.64 kB) | `code-app-build` (`npm --prefix src/code-apps/trustee-review-portal run build`) | Accepted | Same warning, same contributor (`recharts@3.10.1` beside Fluent UI v9) as its standing triage — [trustee-portal-visual-refresh Dev Summary](docs/development/trustee-portal-visual-refresh-dev-summary.md#L2682). Within its declared budget (`src/code-apps/trustee-review-portal/bundle-budget.json`: max 1,241,000 / 79,500; the `code-app-bundle-budget` step passed). The +5,465 JS / +420 CSS bytes over that file's recorded measurement (1,204,716 / 77,221) are this feature's contract changes the first app shares (the ADR-065 parser, ADR-059 `visibility.ts`); its budget file was not re-measured in this docs-only revision |
| `pac solution pack` reports **17** root components "not defined in customizations", identical on both packs | `pack-managed`, `pack-unmanaged` | Accepted, pre-existing | The parent row records 14 ([trustee-portal-visual-refresh Dev Summary](docs/development/trustee-portal-visual-refresh-dev-summary.md#L2677)): 9 `EntityRelationship` and 5 `EnvironmentVariableDefinition` entries. **The 3 extra are `EnvironmentVariableDefinition` entries, not Code App components:** `rev_DocuSignAccountId`, `rev_DocuSignAcceptanceTemplateId` and `rev_SpoSiteUrl` — the root components added for wbs:3.2 and wbs:3.4 ([Solution.xml](src/solutions/RevitaliseGrantAutomation/Other/Solution.xml#L323), [L324](src/solutions/RevitaliseGrantAutomation/Other/Solution.xml#L324), [L326](src/solutions/RevitaliseGrantAutomation/Other/Solution.xml#L326)), whose definitions pack as root components without a customizations entry, the same shape as the five already accepted. Identified by diffing this build's pack output against `build/artifacts/trustee-portal-visual-refresh-20260901-2/build-run.log` (14, the parent's figure): the 14 are unchanged and the 3 are the only additions; `build/artifacts/revitalise-grant-automation-20260930-1` already shows the same 17, before this feature's build. Neither Code App is a solution component here (the card app has no `appId` yet) |

### Diagnostic components created and removed (C-TECH-056)

None. No environment was touched. The scratch probe scripts were copied into the app folder only for the run (`.measure.mjs`, `.shoot-app.mjs`, `.dbg.mjs`) and deleted after each run.

## 12. Work Items — close-out record (C-TECH-079)

Revision 3 reopened ten items whose implementation changed. Three of them had traced lines that no longer resolved: WI-0085, WI-0088 and WI-0097. The other seven had acceptance clauses whose behaviour this revision changed: WI-0059, WI-0092, WI-0096, WI-0098, WI-0099, WI-0102 and WI-0104. Eight were re-closed with fresh evidence dated 2026-10-01.

Revision 3.1, after TAD Revision 3.2:
- **WI-0085 and WI-0088 re-closed `built`** against pm-agent's amended clauses (kit palette, `markColor()`).
- **WI-0092, WI-0102 and WI-0103 reopened and re-closed**: the `layout.test.ts` tests their evidence traced no longer exist after the R19 rewrite, so they are re-traced to the accessibility assertions that replace them and to the 320/390/1280 visual spec. **WI-0092 and WI-0102 are now at two reopens each** — the escalation trigger; this dispatch already runs at the strategic tier.
- **WI-0086 and WI-0087 reopened** with the reason "acceptance clause [2] still names categoricalColor, superseded by R17 / TAD 3.2", for pm-agent to amend; I re-close them after that.
- **After pm-agent's amendment (2026-10-01): WI-0086 re-closed `built`** against amended clause [2] (`markColor()` in `charts.tsx`, the palette line) with no code change; **WI-0087 stays `reopened`**: its amended clause [2] is met, but unamended clause [0] still names the kit's teal `#14adbb` for the third series, which R17 / TAD §8.3 replace with `#009aa8` (2.72:1 fails 3:1) — the build is right and the clause needs pm-agent's amendment, so no code change. Scope check: exit 1, WI-0087 only.
- **After pm-agent amended WI-0087 clause [0] to `#009aa8` (2026-10-01): WI-0087 re-closed `built`**, no code change. Scope check over WI-0055..WI-0105: **exit 0**, all 51 built. Borderline status-pill dot confirmed `#14adbb` (`--rev-color-accent`) as WI-0058 [1] and WI-0094 [0] require — measured in Chromium on the list pill (`::before`, generated content) and the detail pill (`aria-hidden` span), both `rgb(20, 173, 187)`.

| Id | Type | External | Title | State | Reopens | Parent |
|---|---|---|---|---|---|---|
| WI-0055 | pbi | D2-01 | Display hint on layout rows and per-group partition [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0056 | pbi | D2-02 | Row order contract: group within sections, order test asserts order within each display group [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0057 | pbi | D2-03 | Summary hero: card, score badge, heading [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 1 | WI-0054 |
| WI-0058 | pbi | D2-04 | Summary hero: status pill (S0a) with tones [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 1 | WI-0054 |
| WI-0059 | pbi | D2-05 | Summary hero: fact chips rows (S0b, S1, S2, S4, S5, S6, S7) [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 1 | WI-0054 |
| WI-0060 | pbi | D2-06 | Fact tiles (default display) incl. absent-value state [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0061 | pbi | D2-07 | A3 conditions rendered as chips [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0062 | pbi | D2-08 | Cost receipt (D5-D10) [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0063 | pbi | D2-09 | Answer cards for redacted free text (withheld, released-empty, released) [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0064 | pbi | D2-10 | Current Circumstances: C1 score bar [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0065 | pbi | D2-11 | Current Circumstances: C2 0-10 life satisfaction scale [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0066 | pbi | D2-12 | Current Circumstances: C3-C12 answer list (likert) [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0067 | pbi | D2-13 | Financial Eligibility: restricted list (F1-F3) [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0068 | pbi | D2-14 | Panel card restyle [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 1 | WI-0054 |
| WI-0069 | pbi | D2-15 | Panel eyebrows, h2 and h3 sub-headings [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 1 | WI-0054 |
| WI-0070 | pbi | D2-16 | Staff recommendation and Verdict panels restyled [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0071 | pbi | D2-17 | Page order, block gap and page background [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0072 | pbi | D2-18 | Design tokens: purple and palette via existing token files [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0073 | pbi | D2-19 | Print rules for the redesigned blocks [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0074 | pbi | D2-20 | Accessibility of the redesigned blocks [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0075 | pbi | D2-21 | Existing contracts preserved: redaction, conditional rows, data-field and dl/dt/dd semantics [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0076 | pbi | D2-22 | Responsive behaviour and visual spec coverage (320 / 390 / 1280) [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0077 | pbi | D2-23 | Design 2.0 Code App: scaffold and build (new separate app, name per architect-agent TAD) [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0078 | pbi | D2-24 | Design 2.0 Code App: shell and navigation so the Application detail screen is reachable [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0079 | pbi | D2-25 | Design 2.0 Code App: sharing to the trustee role, packaging and push [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0080 | pbi | D2-26 | Round overview: page title and action row [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0081 | pbi | D2-27 | Round overview: round hero band [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0082 | pbi | D2-28 | Round overview: Figures of this round header and computed-on stamp [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0083 | pbi | D2-29 | Round overview: stat card panel and progress tiles (Round progress, Exceptional circumstances) [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0084 | pbi | D2-30 | Round overview: chart block with show/hide data table [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0085 | pbi | D2-31 | Round overview: horizontal category bars (Exceptional circumstance cited, Gender, Ethnic group) [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 1 | WI-0054 |
| WI-0086 | pbi | D2-32 | Round overview: vertical columns chart (Age range, Life satisfaction 0 to 10) [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 1 | WI-0054 |
| WI-0087 | pbi | D2-33 | Round overview: grouped columns chart (Wellbeing, last year) [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 1 | WI-0054 |
| WI-0088 | pbi | D2-34 | Round overview: applicant type donut [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 1 | WI-0054 |
| WI-0089 | pbi | D2-35 | Round overview: Who applied and Level of need card composition [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0090 | pbi | D2-36 | Round overview: financial position card and money tiles [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0091 | pbi | D2-37 | Applications list: screen head, action row and in-place verdict dialog wiring [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0092 | pbi | D2-38 | Applications list: filters card [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 2 | WI-0054 |
| WI-0093 | pbi | D2-39 | Applications list: applications table (header, sortable columns, rows) [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0094 | pbi | D2-40 | Shared: score chip and status pill [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0095 | pbi | D2-41 | Group applications: screen head, filters and print [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0096 | pbi | D2-42 | Group applications: groups table [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 1 | WI-0054 |
| WI-0097 | pbi | D2-43 | Group detail: hero band with group summary chips [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 1 | WI-0054 |
| WI-0098 | pbi | D2-44 | Group detail: members table and verdict dialog [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 1 | WI-0054 |
| WI-0099 | pbi | D2-45 | Header: sticky bar with logo and signed-in sentence [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 1 | WI-0054 |
| WI-0100 | pbi | D2-46 | Navigation bar: pill tabs with current-page state [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0101 | pbi | D2-47 | Page layout: main container, max width and block gap [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |
| WI-0102 | pbi | D2-48 | Shared: buttons (primary and secondary treatment) [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 2 | WI-0054 |
| WI-0103 | pbi | D2-49 | Shared: tables (row hover, card radius, horizontal scroll) [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 1 | WI-0054 |
| WI-0104 | pbi | D2-50 | Shared: verdict dialog and verdict choice cards [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 1 | WI-0054 |
| WI-0105 | pbi | D2-51 | Shared: stat tile row, state message and hero/fact-chip primitives [Design 2.0 Code App; UNBILLED, wbs:6.3] | built | 0 | WI-0054 |

Short of verified: 51 of 51 — WI-0055, WI-0056, WI-0057, WI-0058, WI-0059, WI-0060, WI-0061, WI-0062, WI-0063, WI-0064, WI-0065, WI-0066, WI-0067, WI-0068, WI-0069, WI-0070, WI-0071, WI-0072, WI-0073, WI-0074, WI-0075, WI-0076, WI-0077, WI-0078, WI-0079, WI-0080, WI-0081, WI-0082, WI-0083, WI-0084, WI-0085, WI-0086, WI-0087, WI-0088, WI-0089, WI-0090, WI-0091, WI-0092, WI-0093, WI-0094, WI-0095, WI-0096, WI-0097, WI-0098, WI-0099, WI-0100, WI-0101, WI-0102, WI-0103, WI-0104, WI-0105

| Item group | Test or gate command | Exit |
|---|---|---|
| all | `cd src/code-apps/trustee-review-portal-cards && npm run coverage` / `typecheck` / `lint` / `test:visual` / `build` | 0 |
| all | `python3 scripts/verify-code-app-bundle-budget.py src/code-apps/trustee-review-portal-cards` | 0 |
| all | `python3 scripts/verify-code-app-variant-parity.py src/code-apps/trustee-review-portal src/code-apps/trustee-review-portal-cards --config config/code-app-variant-parity.json` | 0 |
| all | `python3 scripts/verify-css-arithmetic.py`; `python3 scripts/run-source-gates.py config/revitalise-grant-automation-build.yml` | 0 |

Scope check: `python3 scripts/verify-work-items.py --check --scope WI-0055,…,WI-0105 --at-least built` → **exit 0**, all 51 built (re-run after the Revision 3.2 fixes: no evidence line lost; moved lines are notes only, so no item state moved).
Deferred: none
Out-of-scope evidence drift noted by the check: WI-0009 (`verified:dev`) — its needle is no longer in the first app's `CasePanels.tsx` (pre-existing; not touched).

### Hours proposal (for commercial-agent; UNBILLED)

| WBS | Billable | Actual effort, for the record | Evidence |
|---|---|---|---|
| 6.3 | **0 h** — unbilled by reviewer decision | Revision 1: 6.5 h; Revision 2: 7.5 h; Revision 3: 5.0 h (the audit's 49 fixes, the measuring script, this document); Revision 3.1: 1.0 h (the both-apps test rewrite, item evidence, this update); Revision 3.2: 1.5 h (the second audit's 10 fixes and 4 records, 15 new probes, this update) | these three dispatches, 2026-09-30 and 2026-10-01 |
| system | 0 h | Revision 1: 1.0 h; Revision 2: 0.5 h; Revision 3: 0 h | same |

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-1002 | `fidelity-inventory-match-asserted-not-measured` | rework | A fidelity row is a match only from equal computed values on both renders; a grep proves a declaration exists, not that it renders |
| IMP-1003 | `dispatch-brief-contradicts-approved-design` | friction | Before applying a fidelity fix, check the TAD's Appendix B and the item's acceptance for the value being replaced (resolved by R17 / TAD 3.2) |
| IMP-1004 | `test-rewrite-orphans-item-evidence` | friction | Before rewriting a test file, grep the item ledger for needles in it; a renamed test forces a reopen today (WI-0092, WI-0102 now at two) |
| IMP-1005 | `fidelity-probe-sampled-one-width-and-hardcoded-elements` | friction | Derive fidelity probes from the design's declarations and run each at every captured width; probe tokens through a consuming element |
| IMP-0986..IMP-1001 | (Revisions 1 and 2) | — | unchanged; see the improvement log |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`

---

## Code Review Checklist
- [x] All FR IDs covered (presentation only; no functional change)
- [x] No hardcoded secrets
- [x] Security controls from TAD §6 held by contract files (none changed in Revision 3)
- [x] TAD §12 items wired (unchanged)
- [x] Role assignments via group teams only (C-TECH-040)
- [x] No invented environment-specific id
- [x] Every guessed contract in §10 and marked `A-nnn` in source (A-CRD-5 added)
- [x] Ground truth: both renders measured; the kit's own global override (13px eyebrow) found by measurement
- [x] Every platform limit without a packer check has a gate (appId → P3; classification → P5; page overflow → the whole-app visual spec)
- [x] Verification levels in §11 are those executed
- [x] Scripts run on the CI runner's OS
- [x] Every tool warning triaged in §11; no diagnostic components
- [x] Accessibility: 44px targets, 4.5:1 text, no sideways scroll at 320px, headings unchanged as accessible names, native radios keep the group's keyboard model
- [x] Every carried work item is built or deferred (scope check exit 0)
- [x] Unit tests written

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`
