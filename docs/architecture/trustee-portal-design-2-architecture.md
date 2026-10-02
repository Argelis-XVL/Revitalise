# Technical Architecture Document — Trustee Portal Design 2.0: a second Code App with the card-layout design on every screen

> **Source:** adopted from `Designsystem/Design-2.0/design_handoff_application_detail/README.md` and its
> `tokens/` and `reference/` folders on 2026-09-30 by architect-agent (intake mode).
> Original author: supplied design handoff, author not named in the drop. The Adoption Report is in the gate
> output of this dispatch.
>
> **Revision 2 source:** adopted from `Designsystem/Revitalise Design System (1)/ui_kits/trustee-review-portal/`
> (the seven `.jsx` files, `index.html` and `README.md`) on 2026-09-30 by architect-agent (intake mode). Exported by
> the reviewer from Claude Design. **There is no written handoff for these screens**: the JSX and the kit README are
> the whole spec, and their content (labels, figures, section list) predates today's fixes. So presentation comes
> from the design, and content, labels, data and every existing contract come from the current source (§13.0).

**Feature Slug:** `trustee-portal-design-2`
**WBS:** `6.3` (accepted task, `contract/wbs.json`). **UNBILLED by reviewer decision**, 2026-09-30 (`logs/routing.log`,
`[trustee-portal-design-2] NOTE — commercial`): the redesign goes beyond the contracted detail screen, the reviewer
chose "unbilled" over a change order under `C-COM-002`, and no hours from this feature are billable. No hours, fees
or dates are restated here (`C-COM-004`, `C-COM-008`).
**SDD Reference:** `docs/plans/revitalise-grant-automation-plan.md` — Amendments A-02 and A-05 (the trustee detail
screen, FR-035, FR-078, FR-079) and the Trustee Pack field map `docs/development/trustee-portal-pack-field-map.md`
(WI-0005). **No functional requirement changes.** The same rows, labels, redaction states and restricted rows are
shown; only presentation and the number of apps change. See §0.3 for why no SDD amendment is needed.
**Parent TAD:** `docs/architecture/trustee-portal-visual-refresh-architecture.md` (the existing trustee portal,
itself a delta over `docs/architecture/revitalise-grant-automation-architecture.md`). **This document is a delta
over that one.** Everything it settles — the data model, the three-state redaction rule (its §3.2.2), the FR-078
field catalogue (its §3.2.3, ADR-032), the design-system adoption and its contrast corrections (ADR-033 to ADR-037,
ADR-042), the security model (its §6) — holds for the new app unchanged and is not restated.
**Date:** 2026-09-30, revised 2026-09-30 (**Revision 2** — every other screen and the app shell; §0.4), revised
2026-09-30 (**Revision 3** — the reviewer's answers and one new requirement; §0.5), revised 2026-10-01 (**Revision 3.2** —
four reviewer decisions from Dev Summary Revision 3; §0.6)
**Status:** APPROVED — **Revision 3** (with the Revision 3.1 edit recording R15 and R16). Approved by the reviewer (session account Anna Southern), 2026-09-30: "Approved for development". Every ADR in this document is `Adopted`.
**Revision 3.2** (2026-10-01) records the reviewer's own answers R17 to R20 (§0.6) and stays APPROVED: it amends §5.3,
§8.3, §13.2, ADR-063 and Appendix B #27, and adds §13.9. It changes one contract test in both apps (`layout.test.ts`)
and no other file of the first app.
Revision 3 records R8 to R16, adopts ADR-062 to ADR-064 with the reviewer's
answers, adds ADR-065 (the round hero's application-share bar) and ADR-066 (card-only wording and how its tests
are split), §0.5, §13.7 and rows R-D2-12 to R-D2-14. **Changes one contract file pair**: the round-statistics
response parser reads one key the flow already emits (ADR-065). Changes no flow, table, column, role, privilege,
connector or data source.
Previously DRAFT — **Revision 2**. Not reviewed as a whole; the reviewer answered its three decisions (R8 to R10).
Adds §0.4, §2.3, §5.3, §8.3, §13, ADR-060 to ADR-064, rows R-D2-8 to R-D2-11 and Appendix B. Amends ADR-056 (by
ADR-060).
Previously APPROVED — **Revision 1**. Approved by the reviewer (session account Anna Southern), 2026-09-30: "Approved development".
**Reviewer decisions this document records (verbatim, session account Anna Southern, 2026-09-30, `logs/routing.log`):**

| # | Question | Answer |
|---|---|---|
| R1 | Row order (README non-negotiable 6) | "Yes the order was to get all fields in. If the fields are grouped in the same sections. It basically is the same only better readable. Maybe make this as a separate code app, so that the business can choose which one to keep." |
| R2 | New design copy (eyebrows, "Costs", "In their words", "Not visible to trustees", hero heading) | "Approve all" |
| R3 | S6 chip label | "Shortened label" |
| R4 | Withheld text on each answer card | "First sentence per card" |
| R5 | Separate app or in-app variant | "Just make a separate code app. is more clean" |
| R6 | Parity check, promotion order (Revision 1 gate) | "1. Yes separate copy and check 2. Business picks one before going live 3. Yes record it  Approved development" |
| R7 | Scope (Revision 2) | "I have downloaded the entire design from Claude Design. It's here: Designsystem/Revitalise Design System ... Check for the designs of the other screens and develop those too"; earlier: "The design contained new designs for all screens. Not just the application detail screen." |
| R8 | ADR-062, new copy on the other screens (Revision 2) | "Approve all (Recommended)" — including the computed sentences |
| R9 | ADR-063, Exceptional circumstance cited | "The designs bars are intentional. So use them. The bar from earlier today wasn't intentional, but an unwanted artifact" |
| R10 | ADR-064, design folder | "Keep both" |
| R11 | Computed-on stamp | "Design wording" |
| R12 | Hand-entered financial position | "Use the pill (Recommended)" |
| R13 | Round hero bar (new requirement) | "Show the total number of applications by counting the applications in the round and adding them to the seeded setting for historic applications predating the trustee portal. Then make the bar about the percentage of applications of the total number of applications." |
| R15 | ADR-065 total: this round + seeded prior count only? | "Yes that is exactly what it means" |
| R16 | The days figure in the Round progress headline | "No change it to x applications in the last xx days. Where the latter is number of days since the round was open till the day of review in case it is still open or until the day the round closed." |
| R17 | Chart palette (Dev Summary Revision 3) | "Design's palette (Recommended)" |
| R18 | Three contract-markup limits | "Accept as-is (Recommended)" |
| R19 | `layout.test.ts` | "Rewrite in both apps (Recommended)" |
| R20 | Three unrecorded colour substitutions | "Record them (Recommended)" |
| R14 | Lead defaults, recorded as defaults, not asked | Days-open tile out of the card app (WI-0012); skip link kept; signed-in name and trustee slot data-driven; nav order as `AppFrame.jsx` and WI-0052 |

**Model tier:** `strategic`, escalated by lead-agent under `config/models.yml` →
`agents.architect-agent.escalate_to_strategic_when` — *feature touches regulated data*. The screen renders A3
condition profiles (UK GDPR Art. 9), the F-section financial rows and the redacted free-text answers. Re-checked
after ground truth (see `skills/how-to-verify-a-platform-contract.md` → *re-check your own tier*): no further
trigger turned on. There is no new table, column, role, integration or cryptography.

---

## 0. What this document decides, and what it deliberately does not

### 0.1 Why a new document and not Revision 11 of the parent

`agents/architect-agent.md` step 1a says a new app is where a new document is right, and an area an approved TAD
already specifies is amended in place. This feature is both: a **new deliverable** (a second Code App, §2) that
renders an **already-specified screen**. It gets its own document for two reasons:

1. **It is designed to be deleted.** One of the two apps is retired when the business chooses (§9.4). As its own
   document, retiring it means marking this file `RETIRED`. As Revision 11 of a 4,700-line parent, it would mean
   reverting a revision whose text other revisions and the Dev Summary cite by section number.
2. **It changes nothing the parent decided.** Every contract the parent holds stays in force for both apps. The
   one pinned contract that changes (DOM row order, ADR-057) changes **only in the new app**. The parent's own
   screen keeps its contract exactly.

The parent is **not edited** by this dispatch.

### 0.2 The decisions

| ADR | Decision | Status |
|---|---|---|
| ADR-055 | Design 2.0 ships as a **second Code App**, `trustee-review-portal-cards`, in the same solution, beside the existing app | `Adopted` (reviewer R5) |
| ADR-056 | The second app is a **full copy** of the first, held to it by a **byte-parity build gate** with a short allow-list. It does not import the first app's source | `Adopted` (reviewer, 2026-09-30) |
| ADR-057 | In the second app only, each Pack section renders its rows **grouped by display type**. The contract becomes "Pack order *within each display group*". The layout spec and its test do not change | `Adopted` (reviewer R1) |
| ADR-058 | Presentation hints live in a **second-app-only map keyed by row id**, not on `DetailRow`, so the layout spec stays byte-identical in both apps | `Adopted` (reviewer, 2026-09-30) |
| ADR-059 | The withheld card shows the **first sentence** of `WITHHELD_EXPLANATION` through a new constant from which the full explanation is **composed**, in both apps. The S6 chip uses the shortened label and the full label is kept for assistive technology | `Adopted` (reviewer R3, R4) |

### 0.3 What this does not do

- **No SDD amendment.** The five sections, 45 Pack rows, labels, conditional rows, redaction states and restricted
  rows are unchanged. The new copy is presentation text approved by the reviewer (R2), not a requirement. Two apps
  showing the same data to the same persona is a delivery decision, not a functional one.
- **No schema, role, privilege, field-security or connector change.** §3 and §6 state the evidence.
- **No promotion out of DEV.** `EX-003` in `contract/known-exceptions.json` keeps the trustee portal in DEV with
  test data. That holds for the second app too. §9.3 says why **the choice must be made before the first
  promotion**.
- **No change to the other three screens.** The new app's round overview, group and list screens are the first
  app's, byte for byte (ADR-056). The design's `reference/AppFrame.jsx.txt` nav bar matches the existing
  `ADR-040` bar, and is not a change.
  **SUPERSEDED by Revision 2 (R7):** every screen and the app shell are now in scope. §0.4 and §13.

### 0.4 Revision 2 — the other screens, and what it decides

**What arrived.** The reviewer exported the whole design to `Designsystem/Revitalise Design System (1)/`. Its
`ui_kits/trustee-review-portal/` holds the Round overview, Applications list, Group applications, Group detail and
app shell, besides the detail screen Revision 1 already covers (its `Shared.jsx`, `AppFrame.jsx` and
`ApplicationDetail.jsx` are byte-identical to Design-2.0's `reference/` copies, measured with `cmp`).

**What it builds on.** The card app exists, and its detail screen is built
(`docs/development/trustee-portal-design-2-dev-summary.md`, DRAFT). Nothing in Revision 2 changes that screen,
redoes it, or moves its files.

| ADR | Decision | Status |
|---|---|---|
| ADR-060 | The parity check changes shape: every file is classified **contract** (must be byte-identical) or **presentation** (may differ), by glob, and a file in neither or both fails. **Contract tests stay identical**, so the first app's tests pin the card app's content and behaviour | `Adopted` (Revision 3 approval) |
| ADR-061 | Presentation comes from the design; content, labels, data and contracts come from the current source. Appendix B lists 27 differences, none adopted as a requirement **unless an ADR adopts it** (Revision 3: ADR-062, ADR-063, ADR-066 adopt nine) | `Adopted` (Revision 3 approval) |
| ADR-062 | **The design's new copy on the other screens is adopted**, including the computed sentences, each with its withheld, null, zero and threshold wording (§13.7) | `Adopted` (R8). Previously `Proposed`, recommending the sentences be left out |
| ADR-063 | **The design's labelled bars are drawn beside "Exceptional circumstance cited"**, one per category, proportional and labelled, with the table still always visible. The WI-0053 artefact stays impossible | `Adopted` (R9). Previously `Proposed`, recommending table-only |
| ADR-064 | **Both design-system folders stay where they are**; nothing moves | `Adopted` (R10). Previously `Proposed`, recommending replacement |

### 0.5 Revision 3 — the reviewer's answers, and one new requirement

| Answer | Where it lands |
|---|---|
| R8 — adopt all new copy | ADR-062 rewritten; §13.7 specifies every computed sentence's wording in each edge case |
| R9 — use the design's bars | ADR-063 rewritten, including how the bars differ from the WI-0053 artefact and which tests hold that |
| R10 — keep both folders | ADR-064 rewritten |
| R11 — "Computed on {date} at {time}" | ADR-066 (card-only wording) |
| R12 — the "Entered by hand" pill | ADR-066 |
| R13 — the round hero bar shows this round's share of all applications | **ADR-065**: the value already reaches the portal; only the app's response parser changes, in both apps |
| R14 — four lead defaults | §13.1, §13.2, ADR-066 |

### 0.6 Revision 3.2 — four reviewer decisions from the build (2026-10-01)

| Answer | Where it lands |
|---|---|
| R17 — the kit's chart palette | §8.3 (palette rows, each measured), §13.2 "Who applied", ADR-063 decision 3, Appendix B #27. **This reverses Revision 2's "marks keep `categoricalColor`".** The development brief that asked for the kit's palette came from lead-agent and contradicted the approved TAD; lead recorded that error in `logs/routing.log`. The reviewer's answer is what authorises the change |
| R18 — three contract-markup limits accepted | §13.9, as permitted deviations (c). No change to either app |
| R19 — `layout.test.ts` rewritten in both apps | §5.3: the one contract test changed in Revision 3.2, in both apps, in one commit |
| R20 — three colour substitutions recorded | §8.3, three rows with measured ratios |

**Today's fixes survive by mechanism, not by care** (§13.6): WI-0052's nav order is in `App.tsx` and
`App.test.tsx`; WI-0013's wording is in `domain/charts.ts` and `dataverse/schema.ts` and pinned by
`RoundStatisticsCharts.test.tsx`; WI-0053 is pinned by `DistributionChart.test.tsx`. All of them are **contract**
files under ADR-060.

---

## 1. Architecture Overview

Two Code Apps render the same Dataverse data to the same trustees. They differ in one screen.

| | `trustee-review-portal` (existing) | `trustee-review-portal-cards` (new) |
|---|---|---|
| Round overview, groups, applications list | as today | **identical source** (parity gate) |
| Application detail | one `<dl>` per section, DOM order = Pack order | Summary hero, fact tiles, cost receipt, answer cards, score bar, 0–10 scale, answer list, restricted list |
| Data read | 7 Dataverse entity sets, no secured column | the **same** 7, the same columns, the same client code |
| Redaction, restricted rows, visibility | `visibility.ts`, field catalogue, `isRowVisible` | the **same files**, byte-identical |
| Shared with | trustee group team, CanView | the same group team, CanView |

The business opens both, then keeps one (§9.4). Until then both are maintained, and ADR-056's gate is what stops
them drifting apart on anything except the detail screen.

---

## 2. Component Diagram

```
Designsystem/Design-2.0/design_handoff_application_detail/   (supplied, not shipped, §2.2)
            │ read by development-agent; values mapped to existing tokens (§8.2)
            ▼
src/code-apps/
 ├── trustee-review-portal/          appId 70869c95-…  (existing, unchanged except ADR-059's constant)
 │     src/domain/{applicationDetailLayout,visibility,fieldCatalogue,…}.ts
 │     src/dataverse/*  src/generated/*  src/components/ds/*  src/styles/{ds-tokens,brand,app.module}.css
 │
 └── trustee-review-portal-cards/    appId assigned by the platform on first push (A-TR-14)
       ├── everything above, byte-identical ───────────── verify-code-app-variant-parity.py (§5, HARD)
       └── allow-listed differences only:
             src/domain/applicationDetailDisplay.ts (+ test)          ADR-058
             src/components/detail/*  (SummaryHero, FactTiles, CostReceipt, AnswerCards,
                                       ScoreBar, LifeScale, AnswerList, RestrictedList)
             src/components/CasePanels.tsx (+ test)                    DetailSectionPanel dispatches by display
             src/pages/ApplicationDetailPage.tsx (+ test)              hero replaces the Summary panel; ADR-057 test
             src/styles/detail.module.css                              new, detail screen only
             src/styles/print.css (+ print.test.ts)                    data-print rules for the new blocks
             src/test/visual/application-detail-layout.visual.spec.ts  320 / 390 / 1280px incl. the new blocks
             power.config.json, bundle-budget.json, index.html          per-app identity and budget
            │
            ▼  npm run build → dist/ → pac code push --solutionName RevitaliseGrantAutomation
Solution RevitaliseGrantAutomation (DEV) — two componenttype-300 rows (A-TR-15)
            │
            ▼  shared CanView with the trustee group team (manual, §12)
```

### 2.1 WBS per component

| Component | WBS | Note |
|---|---|---|
| `src/code-apps/trustee-review-portal-cards/` | `6.3` (unbilled) | the detail screen is 6.3; the three copied screens are 6.1/6.2/6.9 deliverables already evidenced by the first app, and copying them is not new scope |
| Parity gate and its allow-list | `6.3` (unbilled) | exists only because of this feature |
| ADR-059 constant in `visibility.ts` (both apps) | `6.3` | no output change in the first app |
| Push and share steps (§12) | `6.5` pattern, unbilled | the same route the first app uses |

**No component serves no task.** The new app is not unquoted work: it is unbilled work on a quoted task, which
`C-COM-002` allows and the reviewer chose.

### 2.2 Supplied-asset intake — the four answers, measured 2026-09-30

`docs/reference/supplied-assets.md` requires these before anything is designed against a drop. Each is a
measurement, dated.

| Question | For `Designsystem/Design-2.0/`, measured 2026-09-30 |
|---|---|
| **Tracked?** | **No.** `git ls-files Designsystem/Design-2.0` returns 0; `git ls-files --others --exclude-standard` lists 9 files. Not ignored (`git check-ignore` exit 1), except `.DS_Store`, which `.gitignore` excludes. **When it is committed, the count in `docs/reference/supplied-assets.md` ("131 tracked files") must change to 140 in the same commit**, or `verify-derived-counts.py` reports the drift through registry row `designsystem-tracked-file-count` |
| **Does it ship?** | **No.** No file under `src/`, `config/`, `scripts/`, `provisioning/` or `.github/` references `Design-2.0` or `design_handoff` (grep, 0 hits). The reference files carry a `.jsx.txt` extension, which keeps them out of any bundler |
| **Read by any build step?** | **Yes, but it sees nothing in scope.** `design-source-coverage` (`scripts/verify-design-source-coverage.py`) scans every `Designsystem/` subdirectory on disk. It ran PASS today, "22 supplied subdirectory(ies), 1 matching a deliverable". **None of Design-2.0's three folders is one of those matches**, because the gate only covers a folder whose *name* equals a folder under `src/code-apps/`. This drop names its target in README prose, not in a folder name. Logged as a finding; this document cites all three anyway (below) |
| **Which agent owns intake?** | **architect-agent** (`ADR-034`, unchanged). pm-agent ran item intake from the same README in parallel |

**Full enumeration (`C-TECH-075`).** Every folder and file in the drop, and what this document does with it:

| Path | Files | Disposition |
|---|---|---|
| `Design-2.0/design_handoff_application_detail` | `README.md` | **Adopted** as the presentation spec, with the corrections in the Adoption Report |
| `design_handoff_application_detail/tokens` | `colors.css`, `spacing.css`, `typography.css`, `fonts.css` | **Mapped, not imported.** Every colour but one and every spacing value already exist in the app's `ds-tokens.css` / `brand.css` (§8.2). `fonts.css` is **not adopted**: it `@import`s Google Fonts, which `ADR-036` rejects; Playfair Display stays self-hosted (`ADR-042`) and the body font stays the Aptos stack |
| `design_handoff_application_detail/reference` | `ApplicationDetail.jsx.txt`, `Shared.jsx.txt`, `AppFrame.jsx.txt`, `index.html` | **Reference only**, per the README's own instruction and `ADR-034`: recreated as typed `.tsx` with CSS Modules. Inline styles, `window.*` globals and mock data are not carried over. `index.html` loads `../../_ds_bundle.js`, which is not in the drop, so it cannot run here |

### 2.3 Supplied-asset intake for the Revision 2 export — the four answers, measured 2026-09-30

| Question | For `Designsystem/Revitalise Design System (1)/`, measured 2026-09-30 |
|---|---|
| **Tracked?** | **No.** `git ls-files` returns 0; `git ls-files --others --exclude-standard` lists 145 files. Not ignored. It sits **beside** the tracked `Designsystem/Revitalise Design System/` (131 tracked files), which is unchanged |
| **Does it ship?** | **No.** Nothing under `src/`, `scripts/`, `config/` or `.github/` names `Design System (1)` (grep, 0 hits). `ds-tokens.test.ts` already fails any module under `src/` that imports from `Designsystem` |
| **Read by any build step?** | **Yes.** `design-source-coverage` now reports "43 supplied subdirectory(ies), 2 matching a deliverable", PASS. The second match is this export's `ui_kits/trustee-review-portal`. **It passes on a citation that was written for the tracked copy**, because the gate's needle is the last two path parts, and those are the same for both folders. So the PASS cannot tell which copy was read. This document cites `Revitalise Design System (1)/ui_kits/trustee-review-portal` by its full path |
| **Which agent owns intake?** | **architect-agent** (`ADR-034`). pm-agent cut items WI-0080 to WI-0105 from the same kit in parallel |

**What differs from the tracked copy** (`diff -rq`, 2026-09-30):

| Path | Change | Disposition |
|---|---|---|
| `ui_kits/trustee-review-portal/RoundOverview.jsx`, `ApplicationsList.jsx`, `TrusteePortalApp.jsx`, `index.html`, `README.md` | changed | **adopted as presentation** (§13); content not adopted (Appendix B) |
| `ui_kits/trustee-review-portal/AppFrame.jsx`, `ApplicationDetail.jsx` | changed | identical to Design-2.0's reference copies; already covered by Revision 1 |
| `ui_kits/trustee-review-portal/GroupScreens.jsx`, `Shared.jsx` | new | adopted as presentation (§13.4, §13.5, §13.1) |
| `design_handoff_application_detail/` | new | **byte-identical** to `Designsystem/Design-2.0/design_handoff_application_detail/` (`diff -rq`, empty). A duplicate |
| `_ds_bundle.js`, `_ds_manifest.json` | changed | the design tool's own bundle (51,838 → 115,602 bytes). Reference only, never loaded by the app |
| `github.md` | changed | the tool's sync note. **It says the export was made from branch `deploy-first-learning-and-item-closure` at `4eb731ee2a44`**, while the kit `README.md` says `main @ 638ce23`. The two provenance statements disagree; the content matches neither exactly (Appendix B #25) |
| `uploads/Item 6a - Revitalise Strategy.pptx` | changed | client strategy deck. Not read by this design |
| `uploads/Screenshot 2026-09-30 at 17.59.{22,32,40}.png` | new | reviewer screenshots of the running DEV portal. The one inspected (17.59.22) shows the WI-0053 pink rectangle over round aggregates, no personal data. The other two were not opened |

**Whether it should replace the tracked folder:** no. Both stay (R10, ADR-064). Previously recommended: yes.

---

## 3. Data Model — unchanged

**No table, column, option set, relationship or field-security change.** The new app reads exactly what the
first app reads, through byte-identical `src/dataverse/`, `src/generated/` and `src/domain/` files (ADR-056).

| Check | Evidence |
|---|---|
| Entity sets | `power.config.json` `databaseReferences` lists the same 7 data sources in both apps (parity gate check P3, §5) |
| Columns requested | `src/dataverse/schema.ts` is under parity; `no-secured-columns-in-code-app` runs over both folders (§5) |
| Data classification | unchanged; the parent TAD §3 classifies every column shown. A3 remains Art. 9, read only as the released option-set value, never a secured column |
| Retention, SAR, erasure | unchanged. A Code App stores no data of its own |
| Personal data on screen | the same rows as today. The Summary hero shows **no row the Summary panel does not**: S0a, S0b, S1–S7 |

`contract/tad-deferrals.json` is not touched: this document resolves no deferral.

---

## 4. Integration Design — unchanged

No new external touchpoint. Both apps call Dataverse through the same connector,
`shared_commondataserviceforapps`, with the same client code. The round-statistics request/result tables stay a
Dataverse-row path (parent ADR-038).

**Platform facts this design relies on, and how each is known:**

| Fact | Evidence | Status |
|---|---|---|
| A Code App is a solution component of type 300 | **E1**, 2026-09-30: `pac env fetch` on DEV's `solutioncomponent` joined to `RevitaliseGrantAutomation` returned exactly one type-300 row, objectid `70869c95-92e5-442f-b5b9-44b3d3e549f6`, the first app | **VERIFIED** |
| DEV holds exactly one Code App today | **E1**, 2026-09-30: `pac env fetch` on `canvasapp` returned one row, "REV Trustee Review Portal" | **VERIFIED** |
| `pa app init` and `pac code init` create a new app in the current directory; `pa app push -s` takes a solution GUID; `pac code push -s` takes a solution name | **E1**, `--help` of `pa` 1.0.0 and `pac` 2.4.1 on this machine, 2026-09-30 | **VERIFIED** (command surface only) |
| **A solution can hold two Code Apps** | **E4.** Nothing in either CLI's help limits it, and a type-300 component is a canvas-app record, which solutions hold many of. **Never observed** | **UNVERIFIED — A-TR-15** |
| A new app's `appId` is assigned by the platform on first push, not by `init` | **E3.** Inferred from this project's own history ("`appId: null` in power.config.json" before the first push, `config/revitalise-grant-automation-pipeline.yml`) | **UNVERIFIED — A-TR-14** |
| Neither CLI can delete a Code App | **E1**, `pa app --help` and `pac code` list no delete verb (2026-09-30). Deletion is a maker-portal action | **VERIFIED** (no CLI route) |
| Removing a component from the solution and importing the upgrade deletes it downstream | **E2** (standard managed-solution upgrade behaviour) | **UNVERIFIED — A-TR-17**. Not needed if §9.3's ordering is kept |

---

## 5. Build and gate design — the second app is a second set of steps

There is no Power Automate change. This section replaces the template's workflow section, because the build is
where this feature's real design work is.

### 5.1 Every per-app build step, and what happens to it

Enumerated from `config/revitalise-grant-automation-build.yml`'s own `steps:` block, not from memory (the rule in
`agents/architect-agent.md` → *An ADR that specifies expression-level mechanism enumerates the gates*).

| Step | Today | For the new app |
|---|---|---|
| `code-app-install`, `code-app-audit` | one app path | **duplicate** with the new path |
| `trustee-field-catalogue` | generator `--check` on the first app's `src/generated/trusteeRestrictedFieldCatalogue.ts` | **unchanged.** The new app's copy is held equal by the parity gate, so a regenerated catalogue that reaches one app only fails the build |
| `no-secured-columns-in-code-app` | first app only | **duplicate**, same `FieldSecurityProfiles.xml` argument. **Not optional**: it is the anonymisation control as a gate |
| `code-app-composition-root` | enumerates `src/code-apps/` | **unchanged**, covers the new app automatically |
| `code-app-data-sources` | first app only | **duplicate** |
| `design-source-coverage` | enumerates | **unchanged** (see §2.2 for what it cannot see) |
| `css-arithmetic` | check whether it walks all apps or one (development-agent) | the new blocks use `auto-fill` grids with absolute floors (`minmax(220px, …)`, `minmax(280px, …)`). **Check B will fire on them.** The fix is a container-relative floor, as the parent's Erratum 8.1 did, not an exemption |
| `code-app-typecheck`, `-lint`, `-unit-tests`, `-visual-tests`, `-build` | one app path | **duplicate** |
| `code-app-bundle-budget` | first app's `bundle-budget.json` | **duplicate** with the new app's own budget file, measured on its first build |
| `package-code-app` | copies `dist/` to `$ARTIFACT_DIR/code-app/` | **duplicate** to `$ARTIFACT_DIR/code-app-cards/`. The artifact directory name must differ, or the second copy overwrites the first |
| `verify-tad-coverage.py` | `--app-src` defaults to the first app | **add a second run** with `--app-src src/code-apps/trustee-review-portal-cards/src`. Assertion (e) reads status values the app synthesises, and the new status pill maps status labels to tones — that mapping must use the existing status enumeration |
| **NEW** `code-app-variant-parity` | — | **HARD**, placed immediately after the second `no-secured-columns-in-code-app`. §5.2 |

**Naming convention for removal:** every duplicated step's `name:` ends in `-cards`, and the parity step is named
for the pair. Retiring either app is then one grep over `-cards` (§9.4).

### 5.2 The parity gate (ADR-056)

`scripts/verify-code-app-variant-parity.py <app-a> <app-b> --allow config/code-app-variant-parity.json`

| Check | Asserts | Why |
|---|---|---|
| P1 | Every file under both apps, excluding `node_modules`, `dist`, `coverage`, `test-results`, has the **same sha256** in both, unless its path is on the allow-list | the redaction, catalogue, visibility and data-access contracts are held by *files*. If the file is identical, the contract is identical |
| P2 | A file present in one app only is on the allow-list | a new file is a divergence too |
| P3 | `power.config.json`: the `databaseReferences` data sources and `connectionReferences` connector ids are equal; the two `appId` values **differ** (a `null` in the new app passes until first push) | **The hazard this catches is a copied `power.config.json`.** A copy carries the first app's `appId`, and `pac code push` from the new folder would then **overwrite the live first app** |
| P4 | Every allow-list entry names a path, a reason and this document's ADR; an entry matching no file fails | an allow-list that outlives its files is how a gate stops meaning anything |

**Value comparison, not a phrase match.** It hashes bytes and compares two directory listings. It needs no
escape flag: the escape is an allow-list entry, which is a reviewed, committed change.

**Allow-list at creation** (the only legitimate differences):

```
src/domain/applicationDetailDisplay.ts            src/domain/applicationDetailDisplay.test.ts
src/components/detail/**                          src/styles/detail.module.css
src/components/CasePanels.tsx                     src/components/CasePanels.test.tsx
src/pages/ApplicationDetailPage.tsx               src/pages/ApplicationDetailPage.test.tsx
src/styles/print.css                              src/styles/print.test.ts
src/test/visual/application-detail-layout.visual.spec.ts
power.config.json   bundle-budget.json   index.html
```

**Deliberately NOT on it:** `applicationDetailLayout.ts` and its test (ADR-058), `visibility.ts`,
`fieldCatalogue.ts`, everything in `src/dataverse/` and `src/generated/`, `.power/`, `package.json`,
`package-lock.json`, `app.module.css`, `ds-tokens.css`, `brand.css`, `main.tsx`. `package.json` staying identical
keeps the dependency set and the `npm audit` result in lockstep; the `name` field being the same in two private
packages is harmless.

**`.power/` is copied, and `power.config.json` is re-initialised.** `.power/schemas/` is generated per data
source and is the same for the same 7 tables. `power.config.json` is created by `pa app init` in the new folder,
and its `databaseReferences` block then matches the first app's (check P3). It is never copied (A-TR-14).

### 5.3 Revision 2 — the parity check becomes a classification (ADR-060)

**Why the allow-list stops working.** Revision 1's allow-list names 14 differing paths out of about 150, and that is
reviewable. With every screen redesigned, `src/pages/*`, most of `src/components/*` and three stylesheets diverge:
an allow-list of 60-odd paths is no longer a statement of how the apps differ. It is a directory listing, and a new
behaviour-bearing file would be added to it without anyone noticing it is behaviour.

**What replaces it.** `config/code-app-variant-parity.json` gets two glob lists, and the gate one new check:

| Check | Asserts |
|---|---|
| P1 | every file matching **`contract`** has the same sha256 in both apps |
| P2 | a file present in one app only must match **`presentation`** |
| P3 | unchanged (`power.config.json` data sources and connectors equal; `appId`s differ) |
| P4 | every glob in either list names an ADR and a reason, and matches at least one file |
| **P5 (new)** | **every file in either app matches exactly one list.** A file in neither list fails; a file in both fails |

P5 keeps Revision 1's safety property: an unclassified file is still a failure, not a silent divergence. What
changes is that the decision is made **per kind of file**, once, instead of per path, every time.

**The classification** (starting point; development-agent refines the globs, and every change is an ADR-cited
config edit):

| `contract` — byte-identical | why |
|---|---|
| `src/domain/**` except card-only files, `src/dataverse/**`, `src/generated/**`, `src/hooks/**`, `src/app/**`, `.power/**` | data access, redaction, visibility, field catalogue, formatting, chart labels (WI-0013), chart colours (`categoricalColor`), list and group logic, verdict slots |
| `src/App.tsx`, `src/main.tsx`, `src/PowerProvider.tsx`, `src/theme.ts` | the shell's markup, nav order (WI-0052), skip link, composition root. **The shell is restyled through CSS only** (§13.1) |
| `src/components/ds/*.tsx` | the design-system components' markup: 44px targets, focus handling, label binding |
| `src/components/VerdictForm.tsx`, `VerdictSection.tsx`, `VerdictDialog.tsx` | the only write path; EF-05's mandatory note on Defer/Reject; Fluent's modal focus management |
| `src/styles/ds-tokens.css`, `src/styles/brand.css` | tokens, ADR-037's contrast corrections, ADR-036/042 fonts. New values go in card-only stylesheets |
| **every `*.test.ts(x)` except those listed under `presentation`** | **the first app's tests pin the card app's content and behaviour** (below) |
| `package.json`, `package-lock.json`, `tsconfig.json`, `vite.config.ts`, `vitest.config.ts`, `eslint.config.js`, `playwright.config.ts`, `src/test/harness.tsx`, `src/test/setup.ts` | one dependency set, one test setup |

| `presentation` — may differ | why |
|---|---|
| `src/pages/*.tsx` | page layout |
| `src/components/*.tsx` other than the three verdict files | panels, tables, charts, filters, finance panel, distribution chart |
| `src/components/detail/**`, `src/domain/applicationDetailDisplay.ts` and any new card-only presentation module (e.g. `src/domain/statusTone.ts`) | Revision 1's card components, and the status-tone map now shared by the detail, list and group screens |
| `src/styles/app.module.css`, `ds.module.css`, `detail.module.css`, `print.css`, any new `*.module.css` | the look |
| `src/test/visual/**`, `src/test/*harness-app.tsx`, `*-harness.html`, `index.html` | visual specs and their harnesses |
| the ADR-057/058 tests: `ApplicationDetailPage.test.tsx`, `CasePanels.test.tsx`, `applicationDetailDisplay.test.ts`, `print.test.ts` | Revision 1's authorised behaviour changes |
| `src/pages/LandingPage.freshness.test.tsx` (Revision 3, split out in both apps) and card-only tests such as `CategoryBars.test.tsx` | ADR-066's authorised wording; ADR-063's positive bar properties |
| `power.config.json`, `bundle-budget.json` | per-app identity (P3 still applies) |

**The load-bearing half is the test rule.** Page and component tests query by role, label and text:
`App.test.tsx` pins the nav order, `LandingPage.test.tsx` the section headings, `RoundStatisticsCharts.test.tsx`
the WI-0013 wording, `DistributionChart.test.tsx` WI-0053, `VerdictForm.test.tsx` EF-05, the list and group page
tests their captions, filters and "Record verdict" names, and `ds-tokens.test.ts` and `layout.test.ts` ADR-037's
corrections and ADR-041's grid floor **over the card app's own stylesheets**. Keeping them identical means the
redesign has to pass the first app's tests. That is the check that content did not change, and it is stronger than
reading two diffs.

**Revision 3.2 (R19, 2026-10-01): `layout.test.ts` is rewritten in both apps, in one commit, and stays `contract`.**
It was the case rule 1 below describes: the first app's copy asserted **layout values** (an 8px nav gap, nav-sized
button padding) which ADR-061 takes from the design in the card app, so the card app's copy had been classed
`presentation` under an ADR-061 entry that this section does not support. The rewrite asserts only the accessibility
properties both apps must share: 44px minimum targets, wrapping instead of horizontal scroll, container-relative grid
floors (ADR-041), and no fixed heights on text containers. Both copies are then byte-identical, the
`src/styles/layout.test.ts` entry is removed from the `presentation` list and from the `contract` glob's `except`,
and the parity gate holds it. **This is the one contract test changed in Revision 3.2, and the only first-app file it
touches.** Every value it stops asserting is still pinned where it belongs: the first app's by its own visual specs,
the card app's by its visual specs and style inventory.

**When a contract test fails on the card app**, there are two legitimate responses and one illegitimate one:

1. The test is asserting **structure** (a class name, a wrapper element) rather than content: make it assert
   content instead, **in both apps in one commit**. It stays identical.
2. The design **changes behaviour or content on purpose**: move the test to `presentation` with an entry naming the
   ADR in this document that authorises the change. Revision 3's only such case is `LandingPage.freshness.test.tsx`,
   split out under ADR-066; ADR-062 and ADR-063 needed none (their tests stay contract).
3. Not allowed: moving a test to `presentation` to make a red build green.

**Is byte parity still the right mechanism? Yes, narrowed.** The two alternatives Revision 1 rejected (import across
folders; a shared package) are rejected for the same reasons, and one of them now gets stronger. With most UI
divergent, the only shared things are the behaviour and data files, and those are exactly the files that should not
drift during a comparison the business is making on look alone.

---

## 6. Security Design — unchanged in model, one new sharing grant

**No role, privilege, field permission or Entra object changes.** Column security still decides what a trustee
*gets*; the app still asks for no secured column, and the gate proving that runs over both apps.

| Control | How it holds in the new app |
|---|---|
| No secured column is ever requested (FR-036, ADR-002, parent ADR-032) | `schema.ts` and the client are under parity; `no-secured-columns-in-code-app` runs over the new folder |
| Three-state redaction (parent §3.2.2) | `redactedTextState()` is the only decider; `visibility.ts` is under parity. `AnswerCards` is a new *look* for `withheld`, `released-empty` and `released`, and never reads a raw column. States stay `role="note"`, never alerts |
| Restricted rows (FR-078) | `RESTRICTED_VALUE_TEXT` in every restricted `<dd>` (visually hidden in the list, shown once below it); the field catalogue is under parity |
| Conditional rows D11a, A3a, A3b | `isRowVisible()`, under parity |
| Process owner runs the same code | unchanged: she is a profile member, so the gate matters for her exactly as it does in the first app |

### 6.1 Security Role & Group Mapping — one new app share

| Persona | Entra group → group team | Role | App access |
|---|---|---|---|
| Trustee | the existing trustee group team (DEV: the team the first app is shared with) | unchanged trustee role | **CanView on the new app** — new grant, same shape as the first app's (`C-TECH-040`: group team, never a user) |
| Process owner | unchanged | unchanged | CanView or CanEdit as for the first app |

**Sharing is a manual step with a human check.** `provisioning/dataverse/share-apps.ps1`'s code-app branch cannot
run on this Mac (the certificate-drive failure recorded against that script), and `pa app share` is scoped by its
own help to users and service principals, not groups. The first app's share was closed by the reviewer checking the
admin centre by hand, and the new app needs the same. §12.

---

## 7. Non-Functional Decisions

| NFR | Decision |
|---|---|
| Bundle size (`C-TECH-055`) | own `bundle-budget.json`, measured on first build. Expected close to the first app (same dependencies, a few more components, no new library) |
| No new dependency (`C-TECH-023`) | the design needs none; `package.json` is under parity, so one cannot slip in |
| Motion | the panel hover lift is **off**. The README makes it optional; it signals interactivity on a card that is not clickable, and would need a `prefers-reduced-motion` guard for no user benefit |
| Performance | no new query; the page makes the same reads |

---

## 8. Accessibility

### 8.1 What carries over

All eight properties the parent's §8.5 holds carry over through parity or through the tests the README lists:
one `<h2>` per section via `Panel`; `<h3>` for sub-blocks; `<dt>`/`<dd>` inside one `<dl>` (tiles are `<div>`s
wrapping a `<dt>`+`<dd>`, which is valid HTML); `data-field` on every row; 44px targets through `ds/Button`; no
horizontal scroll at 320px (the visual spec is extended to the new blocks at 320, 390 and 1280px); print as plain
black on white keyed on `data-print`; no `--text-muted` for text (`ADR-037`).

**The 0–10 scale** carries its value in text as well as colour: `role="img"` with `aria-label="Answer: N out of 10"`,
and the print rule prints the value as text.

### 8.2 Token mapping — measured, one new value, two corrections

Every colour in `tokens/colors.css` was compared with the app's stylesheets on 2026-09-30:

| Design value | In the app | Action |
|---|---|---|
| Purple `#49345b` | `--rev-color-secondary` in `brand.css` | **reuse** (lead-verified, re-measured) |
| Teal `#14adbb` | `--rev-color-accent` in `brand.css` | reuse, dot only |
| Pink 50/600/800, lavender 100/200, grey 50/100/200, ink 400/600/700/900 | `ds-tokens.css`, same names, same values | reuse |
| Spacing `--space-1` … `--space-24` | identical values | reuse |
| Teal tint `#e7f6f8` (Borderline pill background) and ink `#00505a` | **absent** | add **only** in `detail.module.css` as local custom properties. `brand.css` is under parity and gets nothing |
| Radii 14 / 16 / 20px, the two shadows | absent | local to `detail.module.css` |

**The README says "all the pairings below pass". Two do not.** Measured with the WCAG relative-luminance formula:

| Pairing | Colours | Ratio | Result |
|---|---|---|---|
| Verdict eyebrow text, 12px bold, as designed | `#e6027f` on `#ffffff` | **4.49:1** | **FAIL** (normal text needs 4.5) |
| C2 selected circle, 13px bold text, as designed | `#ffffff` on `#e6027f` | **4.49:1** | **FAIL** |
| Both, corrected to `--pink-700` (inherited `ADR-037` correction 1) | `#c4006c` on `#ffffff` | 5.89:1 | PASS |
| Hero score, 46px Playfair (large text, 3:1 floor) — no correction, keep the brand pink | `#e6027f` on `#ffffff` | 4.49:1 | PASS |

Every other pairing in the README passes, lowest 6.45:1 (`#5a5a5a` on `#f8f7f7`). The two corrections are not new
decisions. They are the correction the parent already made for exactly this colour pair, applied to two new uses.

### 8.3 Revision 2 — contrast on the other screens

Measured with the WCAG relative-luminance formula, 2026-09-30. Each correction is one ADR-037 already made for
the same colour pair, applied to a new use, so none is a new decision.

| Design element | Colours | Ratio | Result and correction |
|---|---|---|---|
| Nav bar selected tab, 15px bold text on the brand-pink fill | `#ffffff` on `#e6027f` | 4.49:1 | **FAIL**. Fill `--pink-700` |
| Primary button gradient, lightest stop | `#ffffff` on `#ec1a8c` | 4.12:1 | **FAIL**. Gradient runs `--pink-700` to `--pink-800` |
| The corrected fill and gradient start | `#ffffff` on `#c4006c` | 5.89:1 | PASS |
| Eyebrow text in brand pink on a card, 12px bold | `#e6027f` on `#ffffff` | 4.49:1 | **FAIL**. Eyebrows use `--pink-700` or the purple |
| Eyebrow text in brand pink on the grey page, e.g. "Round 5" | `#e6027f` on `#f8f7f7` | 4.20:1 | **FAIL**. Same correction |
| "Signed in as …" in `--text-muted` | `#8a8a8a` on `#ffffff` | 3.45:1 | **FAIL**, and ADR-037 correction 2 forbids `--text-muted` for text. Use `--ink-600` |
| Chart mark in `--pink-300`, as designed | `#f28cc6` on `#ffffff` | 2.25:1 | below WCAG 1.4.11's 3:1 for a graphic. **Replaced by `--pink-500`** in the kit palette (R17) |
| Chart mark in teal, as designed | `#14adbb` on `#ffffff` | 2.72:1 | below 3:1. **Replaced by the darker teal** already validated in `domain/charts.ts` (R17) |

**The card app's chart-mark palette (R17, 2026-10-01): the kit's five-step order, with two steps darkened.** Defined
in `src/cards/palette.ts` (presentation); the first app keeps `categoricalColor` unchanged. Each mark measured against
the white card (WCAG 1.4.11, 3:1 floor for a graphic):

| Step | Mark | Colours | Ratio | Result |
|---|---|---|---|---|
| 1 | brand pink | `#e6027f` on `#ffffff` | 4.49:1 | PASS (as text it fails; marks only) |
| 2 | purple | `#49345b` on `#ffffff` | 10.91:1 | PASS |
| 3 | darker teal, replacing the kit's lighter teal | `#009aa8` on `#ffffff` | 3.39:1 | PASS |
| 4 | `--pink-500`, replacing `--pink-300` | `#ec4ea3` on `#ffffff` | 3.40:1 | PASS |
| 5 | faded purple | `#6a5774` on `#ffffff` | 6.50:1 | PASS |
| 3, on the bar track | darker teal against the empty track | `#009aa8` on `#f0eeee` | 2.94:1 | below 3:1 at the fill's end. **Accepted**: every bar carries its category and value as visible text, the bar list is `aria-hidden`, and the table is the content, so the fill is not the only means of reading the value |
| 4, on the bar track | `--pink-500` against the empty track | `#ec4ea3` on `#f0eeee` | 2.94:1 | same |

The groups table's member dots keep the kit's four colours exactly, teal and `--pink-300` included: they are
`aria-hidden`, and the member count beside them is text, so 1.4.11 does not apply.

**Three further substitutions the build made, recorded (R20, 2026-10-01):**

| Element | Colours | Ratio | Result |
|---|---|---|---|
| Link text (row links), the app's `--link-default`, replacing the kit's brand pink | `#cc0078` on `#ffffff` | 5.47:1 | PASS |
| The same link text on the grey page | `#cc0078` on `#f8f7f7` | 5.12:1 | PASS |
| Secondary-button text `--pink-700`, replacing the kit's brand pink | `#c4006c` on `#ffffff` | 5.89:1 | PASS |
| The same text on the secondary hover fill `--pink-50` | `#c4006c` on `#fdf1f8` | 5.36:1 | PASS |
| Primary hover gradient, first stop `--pink-800`, with the button's text | `#ffffff` on `#9e0057` | 8.10:1 | PASS |
| Primary hover gradient, second stop `--brand-primary-active` (the kit's scale ends at `--pink-800`) | `#ffffff` on `#51002c` | 15.15:1 | PASS |
| Group code avatar and hero values, Playfair 36px+ in brand pink | `#e6027f` on `#ffffff` | 4.49:1 | PASS as large text (3:1) |

**Two further design properties are not adopted, both for accessibility:**

- **Focus ring.** The design's `.rv-btn:focus-visible` uses `--focus-ring` (pink-500). ADR-037 correction 3 keeps
  the app's black ring, because the pink ring fails 3:1 on three of the design system's own surfaces.
- **Form-control borders.** The design's filter controls have a 1.5px `--grey-200` border. ADR-037 correction 4
  says `--border-default` is not load-bearing on a form control, and `ds-tokens.test.ts` (contract) asserts the
  strong border on every input, textarea and select rule in `ds.module.css`. The card app keeps the strong border.

---

## 9. Deployment Topology

### 9.1 DEV

1. Build both apps (§5).
2. `pac code push --solutionName RevitaliseGrantAutomation` from each app folder (the first app's step is
   unchanged). For the new app's **first** push, run `pa app init` in its folder first; after the push, read the
   assigned `appId` back and commit `power.config.json` (A-TR-14).
3. Read DEV's `solutioncomponent` rows for the solution and expect **two** type-300 rows, one per `appId`
   (A-TR-15). If the new app is absent, add it through the maker portal's *Add existing component*, which
   `knowledge/technology/code-apps.md` records as the fallback.
4. Share with the trustee group team, CanView, and have it checked by a human (§12).
5. V4: a trustee opens both apps and reads the same application in each.

### 9.2 Pipeline entries

In `config/revitalise-grant-automation-pipeline.yml`, DEV `post_deploy` gets two entries beside the existing
ones: `operation: code-app-push` for the new folder, and its share step. Both carry `-cards` in their description
and the `wbs:6.3 unbilled` marker. **No TST/ACC or PRD entry is added** (§9.3).

### 9.3 Promotion — the choice comes first

`EX-003` keeps the portal in DEV. When it clears, **the business's choice must be made and the losing app removed
from the solution in DEV before the first promotion export.** Deleting a Code App from DEV before it has ever left
DEV is one maker-portal action. Deleting one that has travelled in a managed solution depends on upgrade-removal
behaviour nobody on this project has observed (A-TR-17), in two further environments. Recorded as risk R-D2-3.

**Reviewer decision, 2026-09-30 (session account Anna Southern):** "Business picks one before going live". So
the business picks one version, and the losing app is removed in DEV before the first promotion out of DEV.

### 9.4 Retiring the app the business does not choose

**The winner keeps the folder name `trustee-review-portal`.** That single rule is what makes retirement cheap,
because every hard-coded path in the repository points at that name: the evidence-map rules for 6.1, 6.2, 6.3 and
6.5, `verify-tad-coverage.py`'s default, the field-catalogue generator's output path, the bundle-budget registry
row, and every build step without `-cards`. The `appId` lives in `power.config.json`, not in the folder name, so a
rename keeps the app.

| Step | If the current layout is kept | If the card layout is kept |
|---|---|---|
| 1. Environment | maker portal: remove the cards app from the solution, delete it | same, for the first app (`70869c95-…`) |
| 2. Source | `git rm -r src/code-apps/trustee-review-portal-cards` | `git rm -r` the old folder, then `git mv …-cards …trustee-review-portal`; set `appDisplayName` |
| 3. Build config | delete every step whose name ends `-cards`, and the parity step | same, then rename nothing: the surviving steps already point at `trustee-review-portal` |
| 4. Parity | delete the script's config file; keep the script (it is generic) or delete it | same |
| 5. Pipeline | delete the two `-cards` post_deploy entries | delete them; update the first app's push/share prose that cites the old `appId` |
| 6. Evidence map | **no change** | **no change**, because the folder name survives |
| 7. Documents | mark this TAD `RETIRED` | this TAD becomes the detail-screen reference; ADR-057 becomes the order contract; mark the parent's detail-screen sections superseded by it |
| 8. Trustee links | none | **the app URL changes** (a new `appId`). Tell trustees; re-share is already in place |

The only irreducible cost of the card layout winning is step 8.

---

## 10. Architecture Decision Records

### ADR-055: Design 2.0 ships as a second Code App in the same solution
**Status:** `Adopted` (reviewer R5, 2026-09-30) · **Serves:** `wbs:6.3` (unbilled)

**Context.** The reviewer asked for the redesign as "a separate code app, so that the business can choose which one
to keep", then decided: "Just make a separate code app. is more clean". The alternative, a switchable detail page
inside the existing app, was not chosen.

**Decision.** A second Code App, folder `src/code-apps/trustee-review-portal-cards/`, display name
"REV Trustee Review Portal (Card layout)", pushed into `RevitaliseGrantAutomation` and shared with the same trustee
group team.

**Consequences.** (1) *Positive:* the existing app and its tests are untouched apart from ADR-059's constant;
choosing is a matter of opening two links; retiring either is §9.4. (2) *Negative:* every per-app build step runs
twice, and each Dataverse change must reach both apps until one is retired — ADR-056 makes that mechanical rather
than remembered. (3) *Negative:* two type-300 components in one solution has never been observed here (A-TR-15).
(4) *Neutral:* no data, role or connector changes, so the security posture is the first app's.

### ADR-056: The second app is a full copy held to the first by a byte-parity gate, not a shared-source import
**Status:** `Adopted` (reviewer, session account Anna Southern, 2026-09-30: "Yes separate copy and check") · **Serves:** `wbs:6.3`
**Amended by ADR-060 (Revision 2):** the allow-list becomes a contract/presentation classification. The copy, the byte comparison and P3 are unchanged.

**Context.** A second app needs the first app's domain, data access, generated services, `ds/` components and
tokens. Three ways to get them were considered:

| Option | Removal cost | Why not |
|---|---|---|
| (a) Import the first app's `src/` through a Vite/TS alias | **high if the cards app wins**: its imports point into the folder being deleted | every per-app gate scans one folder; code imported from outside it is scanned only by the other app's run — a control that holds by accident |
| (b) Extract a shared package under `src/code-apps/shared/` | medium | `code-app-composition-root` and `design-source-coverage` treat every folder under `src/code-apps/` as an app; it also moves a large part of the first app for a comparison that may end with no second app |
| **(c) Full copy + parity gate** | **lowest**: delete one folder (§9.4) | costs duplicated build time and a second test run |

**Decision.** (c). The second app is a copy. `verify-code-app-variant-parity.py` fails the build if any file
outside the allow-list differs, or if the two `appId`s are equal (§5.2).

**Consequences.** (1) The redaction, catalogue, visibility and no-secured-column contracts are identical **because
the files are identical**, which is stronger than two sets of tests agreeing. (2) A fix to shared code must be
committed to both folders in one change; the gate turns forgetting into a red build. (3) Build and test time for
the code-app steps roughly doubles until retirement. (4) The allow-list is the complete, reviewable statement of
how the apps differ.

### ADR-057: In the second app, rows are grouped by display type within each Pack section
**Status:** `Adopted` (reviewer R1, 2026-09-30) · **Serves:** `wbs:6.3`

**Context.** The README's option (a) keeps DOM order equal to Pack order; option (b) groups rows by display type
within a section and asserts order within each group. The reviewer chose grouping: "If the fields are grouped in
the same sections. It basically is the same only better readable."

**A correction to the brief and to the README.** Both name `applicationDetailLayout.test.ts` as the test that
changes. **It does not.** That test pins the *layout spec* (45 rows, Pack order, labels, sub-headings), and the
spec does not change (ADR-058). The test that pins **rendered DOM order** is the "renders every section's rows,
sub-headings and labels exactly as the spec lists them" case in `ApplicationDetailPage.test.tsx`.

**Decision.** In the new app only:
1. `applicationDetailLayout.ts` and `applicationDetailLayout.test.ts` stay byte-identical to the first app's.
2. `ApplicationDetailPage.test.tsx`'s DOM-order case is replaced by one that asserts, per section: (a) the set of
   rendered row ids equals the spec's visible rows, none missing and none extra; (b) within each display group,
   row ids appear in Pack order; (c) the display groups appear in a fixed order per section, taken from
   `applicationDetailDisplay.ts`; (d) the conditional rows D11a, A3a and A3b sit in the display group of their
   trigger row, immediately after it where both share a group.
3. D8 (Total Estimated Cost) stays in the cost receipt in Pack order: D5, D6, D7, **D8**, D9, D10.

**Consequences.** (1) The first app's contract is unchanged. (2) In the new app, the contract is weaker by exactly
one property — cross-group order — and the reviewer accepted that loss by name. Every row is still present,
labelled verbatim, and in its Pack section. (3) The existing conditional-row test (`D11a` directly after `D11`)
still holds, because D11 and D11a sit in different groups (fact / answer): that case must be rewritten as (d),
not deleted.

### ADR-058: Presentation hints live in a second-app-only map, not on `DetailRow`
**Status:** `Adopted` (covered by the reviewer's document approval, session account Anna Southern, 2026-09-30: "Approved development") · **Serves:** `wbs:6.3`

**Context.** The README proposes an optional `display` field on `DetailRow`. That would make
`applicationDetailLayout.ts` differ between the apps, and it is the file that holds the Pack contract.

**Decision.** `src/domain/applicationDetailDisplay.ts`, in the new app only, exports
`Readonly<Record<RowId, Display>>` and the per-section group order. `Display` is
`"fact" | "cost" | "costTotal" | "answer" | "scale" | "likert" | "restricted" | "score" | "status" | "chips"`. A row with no entry
renders as `"fact"`. Its test asserts: every key is a real row id; every redacted row maps to `"answer"`; every
restricted row maps to `"restricted"`; and rows whose spec cell is redacted or restricted can never be mapped to a
display that renders a raw value.

**Consequences.** (1) The layout file stays under parity, so the Pack contract is held in one place for both apps.
(2) The mapping cannot move a row across sections: it picks a display, not a position. (3) The last test assertion
is the one that matters: it stops a display hint from becoming a way to render a redacted row as a plain fact.

### ADR-059: The withheld card shows the first sentence; the S6 chip uses the shortened label
**Status:** `Adopted` (reviewer R3, R4, 2026-09-30) · **Serves:** `wbs:6.3`

**Decision.**
1. In `visibility.ts`, **in both apps**, add `WITHHELD_EXPLANATION_FIRST_SENTENCE = "This answer has not been
   released for trustee review yet."` and **compose** `WITHHELD_EXPLANATION` from it plus the existing remainder.
   The composed string is character-for-character today's. No new wording (R4).
2. Each withheld answer card shows `WITHHELD_HEADING` as its pill and `WITHHELD_EXPLANATION_FIRST_SENTENCE` below
   it. `released-empty` keeps `RELEASED_EMPTY_HEADING` and its full explanation.
3. The S6 chip's visible label is "Total requested inc. exceptional funding" (R3). The spec's full label,
   "Individual Total Amount Requesting Revitalise inc. Exceptional Funding", stays in the `<dt>` as visually hidden
   text, so assistive technology and the DOM-order test still see the Pack label.
4. New copy approved by R2 — the six eyebrows, "Costs", "In their words", "Not visible to trustees", "Score", and
   the hero heading "{score} out of 60 circumstance points" / "Not scored yet" — is presentation text in the new
   app's components. Eyebrows are `aria-hidden`. The three new sub-headings are real `<h3>`s rendered by the
   display components, **not** added to the layout spec, so the spec's "exactly one approved sub-heading" test is
   unaffected.

**Why the constant is composed, not duplicated.** Composing proves by construction that the short text is the
first sentence of the long one. A second literal could drift. Adding it to both apps keeps `visibility.ts` under
parity, and the first app's rendered output does not change (its tests pin the full string).

### ADR-060: The parity check classifies every file as contract or presentation, and contract tests stay identical
**Status:** `Adopted` (reviewer, session account Anna Southern, 2026-09-30: "Approved for development", Revision 3) · **Serves:** `wbs:6.3` · **Amends:** ADR-056

**Context.** Revision 2 redesigns every screen, so most page and component files diverge. Revision 1's per-path
allow-list would grow to 60-odd entries and stop saying anything (§5.3).

**Decision.**
1. `config/code-app-variant-parity.json` replaces `allow` with two glob lists, `contract` and `presentation`, each
   entry carrying an ADR and a reason. The Revision 1 entries move into `presentation` unchanged in meaning.
2. The gate gains P5: every file in either app matches exactly one list.
3. Every test file is `contract` unless an ADR in this document authorises the behaviour change it pins. Today that
   is only the four ADR-057/058 test files.
4. `App.tsx`, `ds/*.tsx`, the three verdict components, `ds-tokens.css` and `brand.css` are `contract`. The shell and
   the design-system components are restyled through the card app's own stylesheets only.

**Consequences.** (1) The redesign must pass the first app's page, component and stylesheet tests unchanged. That is
how content, labels, headings, captions, the nav order, WI-0013 and WI-0053 are held without anyone re-reading them.
(2) Some first-app tests assert structure (for example `DistributionChart.test.tsx`'s `.chartBar` selector). Where a
redesign breaks such an assertion without changing content, the test is rewritten to assert content in **both** apps
at once, which slightly improves the first app's tests too. (3) The config becomes shorter and each entry means
more. A wrong glob is now a larger mistake, and P4 (every glob matches something) and P5 (nothing unclassified) are
what catch it. (4) Retirement (§9.4) is unchanged: delete one folder, one config file and the `-cards` steps.

### ADR-061: Presentation from the design, content from the current source
**Status:** `Adopted` (reviewer, session account Anna Southern, 2026-09-30: "Approved for development", Revision 3) · **Serves:** `wbs:6.3`

**Context.** The kit's JSX is mock-data React. Its README says it mirrors `main @ 638ce23`, its `github.md` says
`4eb731ee2a44`, and its content matches neither exactly: it still labels the wellbeing series "Question 8/9/10"
(fixed today by WI-0013), draws bars beside "Exceptional circumstance cited" (removed today by WI-0053), and leaves
out three sections the current screen has.

**Decision.** For every screen: layout, colour, type, spacing, radii, shadows, chart shape and component styling
come from the kit. Every heading, label, caption, sentence, section, figure, empty state, status value and control
comes from the current source. Appendix B lists each difference found and its disposition, and none is a
requirement. A difference the reviewer wants adopted becomes an ADR here first (ADR-062, ADR-063).

**Consequences.** (1) The card app shows exactly the first app's information and behaviour, which is what makes
"the business chooses on look" a fair comparison. (2) Some of the design's appeal is its sentence headlines. Without
ADR-062 they are not shown, and the card screens will read slightly flatter than the mock-up.

### ADR-062: The design's new copy on the other screens is adopted, with an edge-case wording for every computed sentence
**Status:** `Adopted` (R8, 2026-09-30: "Approve all (Recommended)") · **Serves:** `wbs:6.3`
Previously `Proposed`, recommending that the fixed labels be adopted and the computed sentences left out.

**Context.** R2 covered the detail screen's new copy. The other screens add two kinds: **A**, fixed decorative labels
(eyebrows, "Entered by hand", "This round" / "Charity-wide", "Filter the round", "Applications in this group") and
**B**, sentences computed from data ("48 applications in 59 days", "1 in 4 applications cite an exceptional
circumstance", "Open from … to …", "£x requested together", "Round 5"). The reviewer adopted both.

**Decision.**
1. **A** renders as the kit shows it, `aria-hidden`.
2. **B** renders as each card's visible headline, with the wording in every edge case fixed in §13.7. Each
   sentence is `aria-hidden`, and the card's `<h2>` keeps the **existing plain heading as its accessible name**
   (visually hidden while a sentence is shown). Screen-reader users hear the headings they hear today. The figures the
   sentence restates are on the card as text in any case.
3. **Where a sentence cannot be stated truthfully** (its figure is null, withheld or its denominator is zero), no
   sentence is shown and the plain heading becomes visible. That is the empty-state wording: the existing heading,
   not a new phrase.

**Consequences.** (1) Contract tests that find headings by name (`LandingPage.test.tsx`, for example
`name: "Round progress"`) keep passing unchanged, because the accessible name does not change. (2) Every sentence has
a defined output for every input it can receive, so none can print "1 in Infinity", "NaN days" or a figure k = 5
withholds. (3) The Round progress headline reads "{n} applications in the last {d} days" (R16), with *d* computed
by the card app from the round's own dates (§13.7). Previously "{n} applications in {d} days", which restated the
flow's days figure that WI-0012 removes as a tile.

### ADR-063: The design's labelled bars are drawn beside "Exceptional circumstance cited"; the WI-0053 artefact stays impossible
**Status:** `Adopted` (R9, 2026-09-30: "The designs bars are intentional. So use them. The bar from earlier today
wasn't intentional, but an unwanted artifact") · **Serves:** `wbs:6.3`, WI-0053
Previously `Proposed`, recommending table-only.

**Context.** WI-0053 removed a solid, unlabelled pink rectangle that `DistributionChart` drew in SVG beside this
table. The kit draws something different: one labelled horizontal bar per category.

**Decision.** In the card app only:
1. The bars are a `visual` passed to `DistributionChart`, the route every other chart on this screen uses. They are
   **HTML elements, not SVG**: one list item per category, each with its category label and "{count} · {share}"
   as visible text, and a track with a fill whose width is that category's count over the largest count. A category
   with count 0 keeps its label, value and an empty track.
2. The table stays **always visible** beneath the bars (parent Revision 10; `LandingPage.test.tsx` asserts a table in
   the block). The kit's "Show the data table" toggle is not used for this block.
3. Fill colours come from the card app's kit palette, `markColor()` in `src/cards/palette.ts` (R17, §8.3), never the
   kit's `--pink-300` or its lighter teal. Previously `categoricalColor` (Revision 3). The bar
   list is `aria-hidden`; the table is the accessible content (ADR-029).

**What distinguishes the bars from the artefact, and what holds each property.**

| Property | WI-0053 artefact | The design's bars | Held by |
|---|---|---|---|
| Drawn by | `DistributionChart` itself, as SVG | a supplied `visual`, as HTML | `DistributionChart.test.tsx` "WI-0053: draws no bars of its own …" (**contract, unchanged**): no `svg`, `rect` or `.chartBar` from `DistributionChart` |
| Anywhere on the screen as SVG `rect.chartBar` | yes | never | `LandingPage.test.tsx` "WI-0053: … carries a table and no bar rectangle" (**contract, unchanged**): the block has a table and no `svg, rect, .chartBar` |
| Labelled | no | every bar has its category and value as text | **new card-only test** `src/components/CategoryBars.test.tsx` (presentation) |
| One per category | no, one block | exactly one per series category, in series order | same new test |
| Proportional | no, full width | width = count / max count; the largest is 100%, a zero is 0% | same new test, which also asserts no element in the block has a width with no label beside it |

**No contract test moves.** Revision 3's brief expected the two WI-0053 tests to move to `presentation`. Neither has
to: both assert the artefact's own mechanism (an SVG rect drawn by `DistributionChart`), and the design's bars do not
use it. They stay byte-identical in both apps, so the artefact still fails the build in either app, and the new test
adds the positive properties. **If development-agent draws the bars in SVG**, the `LandingPage.test.tsx` WI-0053 case
fails in the card app. The answer then is to draw them in HTML, not to move the test.

**Consequences.** (1) The card app shows the design's bars; the first app keeps table-only, unchanged. (2) The
artefact cannot come back in either app without a red build. (3) The bars duplicate the table visually, which the
parent's ADR-029 allows because the table stays the content.

### ADR-064: Both design-system folders stay where they are
**Status:** `Adopted` (R10, 2026-09-30: "Keep both") · **Serves:** `wbs:6.3`
Previously `Proposed`, recommending that the export replace the tracked folder.

**Decision.** No folder moves, is renamed or is deleted. `Designsystem/Revitalise Design System/` (tracked, 131 files)
and `Designsystem/Revitalise Design System (1)/` (untracked, 145 files) both stay, and so does
`Designsystem/Design-2.0/` (untracked, 9 files).

**Consequences.** (1) This document cites the (1) folder by its full path wherever it means that copy (§2.3), because
`design-source-coverage` cannot tell the two apart (R-D2-11 stays open). (2) Whoever commits either untracked folder
updates the "131 tracked files" count in `docs/reference/supplied-assets.md` in the same commit: 140 with
`Design-2.0/`, 285 with both.

### ADR-065: The round hero's bar shows this round's share of all applications, from a value the flow already emits
**Status:** `Adopted` (reviewer, session account Anna Southern, 2026-09-30: "Approved for development", Revision 3); new requirement R13 · **Serves:** `wbs:6.3`

**Context.** R13 replaces the kit's close-date progress bar: total = this round's applications + the seeded count of
historic applications from before the trustee portal; the bar = this round as a percentage of that total.

**Which setting, measured 2026-09-30.**
- The setting is **`RoundStatisticsHistoryPriorApplicationCount`** (`rev_setting`, Whole Number), documented in
  `provisioning/deploymentSettings/settings-rows.notes.md` as "the number of applications the charity received before
  `RoundStatisticsHistoryStartDate`". It is the only seeded count of pre-portal applications in the settings.
- **E1, live DEV read:** `RoundStatisticsHistoryPriorApplicationCount = 715`, `RoundStatisticsHistoryStartDate = 2026-09-24`.
  **This disagrees with the notes file**, which records the reviewer's 2026-09-19 seed as `0` and `2026-02-16`.
  Someone has re-seeded DEV since. Logged as a finding. The design takes the value from the response, never from
  either written figure.

**Does it already reach the portal? Yes, as far as the flow. The app does not read it yet.**
- **E1, solution source:** `REVPortalRoundStatistics`'s `Compose_response_body` includes
  `metrics.historicApplicationsByMonth`, which `Compose_historic_applications_by_month` assembles as
  `{trackingStartDate, priorApplicationCount, understatedTotal, months}`.
- **E1, live DEV:** the deployed flow's `clientdata` (modified 2026-09-30 18:04) contains `priorApplicationCount` and
  `Read_the_history_prior_count`.
- **E1, app source:** neither app's `dataverse/types.ts` or `dataverse/roundStatistics.ts` mentions
  `historicApplicationsByMonth`, `priorApplicationCount` or `understatedTotal` (grep, 0 hits). The key is in the
  response and is dropped by the parser.

**Decision.**
1. **No flow change and no response change.** `REVPortalRoundStatistics` is shared by both apps and stays as it is.
2. **One contract-file change, in both apps in one commit:** `dataverse/types.ts` gains
   `historicApplicationsByMonth: { priorApplicationCount: number | null; understatedTotal: boolean } | null` on the
   metrics type, and `dataverse/roundStatistics.ts` parses it with the same null-tolerant pattern as its other keys (a
   malformed or absent object is `null`, never an error). `roundStatistics.test.ts` (contract) gains the parse cases.
   **The first app parses the value and renders nothing new**, so its screens are unchanged. This is the only change
   Revision 3 makes to the first app, and parity requires it (the parser is contract).
3. **The bar, in the card app's round hero.** Let *n* = `applicationsReceived.count` (this round, as today) and
   *p* = `priorApplicationCount`. Total *T* = *n* + *p*. The bar's fill width = *n* / *T*, shown as a percentage with
   `formatPercentage`.

| Case | Bar | Text under the bar (the content; the bar is `aria-hidden`) |
|---|---|---|
| *n* and *p* present, `understatedTotal` false, *T* > 0 | fill *n*/*T* | "This round: {n} applications" · "All applications: {T}, including {p} from before the portal" · "{share} of all applications" |
| *p* = 0 (a legitimate seeded value) | full width | as above, with "including 0 from before the portal" |
| *p* null (setting row absent) or `understatedTotal` true | none | "This round: {n} applications" · "All applications: Not recorded" |
| `historicApplicationsByMonth` absent or malformed | none | as the row above |
| *n* null (`applicationsReceived` withheld or absent) | none | none; the hero shows its dates only |
| *T* = 0 | none | "This round: 0 applications" · "All applications: 0" |
| *n* = 1 | as normal | "This round: 1 application" |

**Consequences.** (1) With DEV's current seed, a round of *n* applications shows *n*/(*n* + 715). (2) **Confirmed by the reviewer (R15, "Yes that is exactly what it means"):** the total is this round plus the
seeded pre-portal count **only**. Applications from earlier rounds already in Dataverse are not included, and the
flow's `months` array is not used. Previously recorded as an interpretation to confirm at approval. (3) The "Not recorded" wording is the app's existing `NOT_RECORDED`, not new copy. The three
figure labels are new copy, written here and approved with this revision.

### ADR-066: Card-only wording and figure choices, and how the tests that pin them are split
**Status:** `Adopted` (reviewer, session account Anna Southern, 2026-09-30: "Approved for development", Revision 3); R11, R12, R14 · **Serves:** `wbs:6.3`

**Context.** Four answers change **content** in the card app only, and each is pinned by a first-app contract test:

| # | Change in the card app | Source | First-app contract test that pins today's form |
|---|---|---|---|
| 1 | Stamp reads "Computed on {date} at {time}" | R11 | `LandingPage.test.tsx`, describe "the two freshness statements (TAD §8.3)": `/round figures computed on 25 aug 2026, 13:05 utc/i` and three `/round figures computed on/i` matches |
| 2 | Hand-entered finance: the "Entered by hand" pill, then "These figures are as at {date}. The application figures above were computed just now." (no as-at date: "These figures carry no as-at date, so how current they are is not known from this screen. Ask the process owner before relying on them.") | R12 | the same describe: `/entered by hand and are as at 20 aug 2026/i` |
| 3 | The "Days the round has been open" tile is not shown | R14, WI-0012 | none (grep, 0 hits in tests) |
| 4 | Skip link, signed-in name, trustee-slot sentence, nav order | R14 | `App.test.tsx`, `VerdictForm.test.tsx` — **unchanged, these are defaults that keep today's behaviour** |

**Decision.**
1. **Split, do not move.** The first app's "two freshness statements (TAD §8.3)" describe block moves, verbatim,
   out of `LandingPage.test.tsx` into a new `src/pages/LandingPage.freshness.test.tsx`, in the first app. The card
   app gets its own `LandingPage.freshness.test.tsx` asserting its wording **and the same properties**: two distinct
   elements, the denominator line "over {n} applications received in this round" kept, both stamps printed.
   `LandingPage.freshness.test.tsx` is `presentation` (this ADR). `LandingPage.test.tsx` stays `contract` and
   identical, so every other Round overview assertion (headings, WI-0053, share-only, ethnicity, calendar) still
   binds the card app.
2. **The stamp's date and time** come from `formatDateTime`'s parts (date, then time with its "UTC" suffix, as
   today). If `computedOn` is null the stamp reads "Computed on Not recorded", as today's line would.
3. **The Days tile** is omitted from the card app's progress tiles (`RoundStatistics.tsx` is presentation). WI-0012 is
   `ready` and not built in the first app, which keeps the tile until that item is built there.
4. **Defaults kept:** the skip link, `Signed in as {fullName}.`, the slot sentence from `slots.ts` and the nav order
   are in contract files and do not change.

**Consequences.** (1) The split changes the first app's test layout but not one assertion, and the first app's
output is unchanged. (2) The card app's freshness wording is pinned by its own test, so it cannot drift either. (3)
While WI-0012 is unbuilt in the first app, the two apps differ by one tile, which the business should know when
comparing them.

---

## 11. Risks & Mitigations

| # | Risk | Likelihood | Mitigation |
|---|---|---|---|
| R-D2-1 | A copied `power.config.json` pushes over the live first app | medium, one mistake | parity check P3 fails the build when the two `appId`s are equal; §5.2 says to run `pa app init`, never copy |
| R-D2-2 | Shared code drifts between the apps during the comparison | high over weeks | parity gate (ADR-056) |
| R-D2-3 | Both apps get promoted and the loser must be removed from managed environments | low while `EX-003` holds | §9.3: choose and remove in DEV first |
| R-D2-4 | The second push does not land in the solution (knowledge file and live read disagree on whether push-by-name works, §12.2) | medium | §9.1 step 3 reads it back; *Add existing component* is the fallback |
| R-D2-5 | A display hint renders a redacted row as a plain value | low | ADR-058 test; `redactedTextState()` stays the only decider |
| R-D2-6 | `css-arithmetic` check B fails on the new grids | high | container-relative floors from the start (§5.1) |
| R-D2-7 | Trustees are confused by two apps | medium | a one-line app description on each; the business compares, not every trustee |
| R-D2-8 | A contract test is moved to `presentation` to get a build green, and content drifts | medium | ADR-060 rule 3; every presentation test entry must name an ADR in this document; review of the config diff |
| R-D2-9 | Contract tests that assert structure block a pure restyle | high | ADR-060 consequence 2: rewrite to assert content, in both apps, in one commit |
| R-D2-10 | The design's mock content leaks into the card app (a figure, a name, "Question 8") | medium | ADR-061; contract tests; Appendix B as the checklist |
| R-D2-11 | Two copies of the design system get cited inconsistently | medium, and it stays open (R10 keeps both) | full-path citations here; ADR-064 |
| R-D2-12 | The DEV seed of `RoundStatisticsHistoryPriorApplicationCount` (715) is not what TST/ACC or PRD will be seeded with, so the hero's share differs by environment | high | the bar reads the response, never a written figure; the settings notes are corrected by their owner (finding) |
| R-D2-13 | The bars in "Exceptional circumstance cited" are drawn in SVG, and the WI-0053 test goes red in the card app | medium | ADR-063: draw them in HTML; never move the test |
| R-D2-14 | A computed sentence prints a wrong claim for an input nobody listed | low | §13.7 lists every input case; a card-only test per sentence covers each row |

---

## 12. Provisioning & External Dependencies

| Item | Type | Tool / Script | Scope | Gate |
|---|---|---|---|---|
| New Code App record | Code App (type 300) | `pa app init` once, then `pac code push --solutionName RevitaliseGrantAutomation` | DEV, per-env `post_deploy` | §9.1 step 3 read-back |
| Solution membership fallback | solution component | maker portal *Add existing component* | DEV | same read-back |
| Share with trustee group team, CanView | app sharing | maker portal / admin centre; `share-apps.ps1` code branch cannot run on this Mac | DEV, per-env `post_deploy` | human V4 check of the role assignment, as for the first app |
| Settings entry | `dataverse.apps` entry, type `code`, the new `appId`, `shareWith` the trustee group | `provisioning/deploymentSettings/dev-settings.json` | DEV | written only after the real `appId` is read back — never an invented id |

### 12.1 Environment Prerequisites

**None new.** The "Power Apps code apps" product feature is already on in DEV (the first app pushes there). No
entity, option set, role or field-security profile is added (`C-TECH-050` has nothing to create).

### 12.2 Platform Contract Verification Plan

| Id | Component | Hand-authored? | Ground-truth method | Platform-assigned values | Verified at |
|---|---|---|---|---|---|
| A-TR-14 | New app's `appId` | no | after `pa app init`, read `power.config.json`; after first push, `pac code list` shows two apps with different ids | `appId` | OPEN |
| A-TR-15 | Two Code Apps in one solution | no | `pac env fetch` on `solutioncomponent` for the solution, `componenttype = 300`: expect 2 rows. The query used for this document is the method | component ids | OPEN — 1 row today (E1, 2026-09-30) |
| A-TR-16 | CanView share of the second app to a group team | no | human check in the admin centre, as the first app's share was closed | role assignment id | OPEN |
| A-TR-17 | Upgrade removal of a Code App downstream | no | not needed if §9.3 holds; else observe on TST/ACC | — | OPEN, avoidable |

**A contradiction this read found in the repository.** `knowledge/technology/code-apps.md`, in its deployment
section, says `pac code push --solutionName` "does not do what it says on this tenant" and that the pushed app's
`appId` was absent from the solution's components. Today's E1 read shows the first app **is** a component of
`RevitaliseGrantAutomation`, matching the pipeline config's 2026-08-23 record. Which is right for a *new* app is
exactly A-TR-15; §9.1 step 3 settles it on the first push. Logged as a finding for improvement-agent.

---

## 13. Revision 2 — the other screens and the app shell

### 13.0 How to read this section

Each screen lists **what changes** (presentation, from the kit) and **what must not** (content and behaviour, from
the source). The kit's inline styles are recreated in CSS Modules, never copied. Grid floors are container-relative
from the start (`css-arithmetic` check B, R-D2-6). Every heading above body size declares its own line-height
(check A). The hover lift stays off (§7). All mock figures and names in the kit are ignored.

**Where the code goes.** Page and component files are `presentation` (ADR-060) and may be restyled or given new
markup. `App.tsx`, `ds/*.tsx` and the three verdict components are `contract`, so their look changes through the card
app's stylesheets only.

### 13.1 App shell — header, nav bar, buttons, tables, stat tiles (`AppFrame.jsx`, `Shared.jsx`, `index.html`)

| Element | Changes (kit) | Must not change (source) |
|---|---|---|
| Page | `--grey-50` background; content column max 1200px, side padding `clamp(16px, 4vw, 48px)`, 24px between blocks | one `<h1>` per view, skip link |
| Header | white, sticky, soft shadow; logo 44px high | "Signed in as {fullName}." and the fallback sentence, from `App.tsx`. Text `--ink-600`, not `--text-muted` (§8.3) |
| Nav bar | white pill-shaped card, 6px padding, 4px gap; tabs 44px high, `0 18px`, 15px bold, pill radius; selected tab filled `--pink-700` with a soft shadow; hover `--grey-50` | **order Round overview, Group applications, Individual applications, then conditional Application detail** (WI-0052; `App.tsx` and `App.test.tsx`, both contract); `aria-current="page"` |
| Page title | Playfair `clamp(28px, 6vw, 44px)`, line-height 1.2 | its wording |
| Buttons (`ds/Button`) | primary: gradient `--pink-700` to `--pink-800`, soft shadow, hover one step darker; secondary: white, soft shadow, hover `--pink-50` | 44px minimum; black focus ring (§8.3); labels |
| Tables | card with 16px radius and horizontal scroll inside the card; header row `--grey-50`, 12px bold uppercase `.06em` `--ink-700`; row hover `--grey-50`; no border under the last row | native `<table>`, `<caption>` wording, `<th scope>`, `aria-sort`, sort behaviour |
| Stat tiles (`ds/StatTile`) | 14px radius, 28×6px coloured bar, value Playfair 40px, tinted backgrounds (`--pink-50`, `--lavender-100`, the teal tint) in turn | labels, values, the absent state |
| Definitions, state messages | tile grid as the detail screen's fact tiles; dashed lavender card for state messages | wording, `role` |
| Verdict dialog (`VerdictDialog`, `VerdictSection`, `VerdictForm`) | surface 20px radius; the three choices styled as cards (2px border in the choice's tone when checked, via `:has(:checked)`); notes box as the detail screen's | Fluent `Dialog` (focus trap, Escape), title "Record a verdict for {reference}", the trustee-slot sentence from `slots.ts`, **no preselected verdict** (only a saved one), **notes mandatory for Defer and Reject** (EF-05), "Close" |

### 13.2 Round overview (`RoundOverview.jsx`)

| Block | Changes (kit) | Must not change (source) |
|---|---|---|
| Title, round sentence, action row | spacing only | `<h1>` "Round overview — {roundName}", the FR-057 no-selector sentence, "Open the applications list", "Refresh figures" and its unchanging accessible name |
| "This round" | hero band: gradient `--lavender-100` to `--pink-50`, 20px radius; white 120px badge with the round key in Playfair; headline sentence (§13.7); Opened and Closed as a small definition list; **the application-share bar and its three figures (ADR-065)**, replacing the kit's close-date bar (R13) | accessible heading "This round"; the round key, Opened and Closed values and their formatting; **no Closed when there is none** (the calendar tests in `LandingPage.test.tsx` find "1 Aug 2026" and "Closed" as their own text) |
| "Figures of this round" + stamp | the stamp becomes a white pill beside the heading, reading "Computed on {date} at {time}" (R11, ADR-066); the denominator line stays beneath it | the live region and its announcements; the denominator "over {n} applications received in this round" |
| Every section | card: 16px radius, 32px padding, eyebrow (ADR-062 A), headline sentence where §13.7 gives one (ADR-062 B) | the existing heading as each `<h2>`'s accessible name, and section order |
| Round progress | stat tiles as §13.1; **two tiles, not three**: "Days the round has been open" is not shown (R14, WI-0012, ADR-066) | the other two figures and labels |
| Exceptional circumstances | definitions as fact tiles; hint line; **the design's labelled bars above the table** (R9, ADR-063) | the figures, "Not shown" for a withheld average, the hint sentence; **table always visible**; no `svg`, `rect` or `.chartBar` in the block |
| Type of break | card styling | **kept.** The kit leaves it out (Appendix B #5) |
| Who applied in this round | two-up grid; bar, column and donut shapes as the kit's `Bars`, `Columns`, `Donut` (Recharts `Bar` with rounded ends, `Pie` with an inner radius and the population in the centre) | **share-only, no counts** (parent Revision 8); the "Counted over N applications" line; tables behind "Show the data table" (Revision 9); ethnicity only when the response carries it; **colours from the kit palette** (`src/cards/palette.ts`, R17, §8.3; previously `categoricalColor`) |
| Level of need | grouped columns for the wellbeing comparison, columns for life satisfaction | **series names from `domain/charts.ts`** (WI-0013), never "Question 8/9/10"; the circumstance-score chart and the proportions **kept** (the kit leaves both out); response counts kept |
| Financial position | money tiles: value Playfair 26px, absent state dashed; two groups under "This round" / "Charity-wide" eyebrows; **the "Entered by hand" pill** before the as-at sentence (R12, ADR-066) | the eight labels, "(charity-wide)" suffixes, the as-at date and its null form's meaning |

### 13.3 Individual applications (`ApplicationsList.jsx`)

| Block | Changes (kit) | Must not change (source) |
|---|---|---|
| Title | spacing | "Applications under review" |
| Filters | white card, 16px radius; fields in a wrapping row; controls 44px, 12px radius, `--grey-50` fill | the five labels and their `htmlFor` binding, the options, "Clear filters", **the strong control border** (§8.3), filter logic (`listView.ts`, contract) |
| Print | spacing | "Print this list" and print behaviour |
| Table | §13.1 table; Circumstance score as a 56×6px bar (`aria-hidden`) plus the number in Playfair; Status as a pill toned by option value (the detail screen's tone map, moved to a shared card-only module); "None"/"Not recorded" circumstances in `--ink-600` | columns and their order, "Not scored", the caption sentences, row link names, "Record verdict" and its `aria-label`, sort |
| Empty and error states | state-message card | wording |

### 13.4 Group applications (`GroupScreens.jsx`, `GroupsList`)

| Block | Changes (kit) | Must not change (source) |
|---|---|---|
| Title, filters, print | as §13.3 | "Group applications", the same filters |
| Table | §13.1 table; a 36px avatar tile before the group code (its last two characters, `aria-hidden`); overlapping member dots (`aria-hidden`) before the member count; total in Playfair | columns, caption "{n} group(s) of linked applications.", link names, totals formatting |

### 13.5 Group detail (`GroupScreens.jsx`, `GroupDetail`)

| Block | Changes (kit) | Must not change (source) |
|---|---|---|
| Title | spacing | "Group {code}" |
| Group summary | hero band with a "Members" badge and the four facts as chips | heading "Group summary"; the four labels and values |
| Members | §13.3 table | fixed order, no sort, caption, the verdict route and its error toast |

### 13.6 Where today's fixes are held

| Fix | What it is | Held by | ADR-060 class |
|---|---|---|---|
| WI-0052 | nav order Round overview, Group applications, Individual applications | `App.tsx` markup; `App.test.tsx` "orders the bar with Round overview, Group applications, Individual applications" | contract (both) |
| WI-0013 | wellbeing series and circumstance-score wording | `domain/charts.ts`, `dataverse/schema.ts`; `RoundStatisticsCharts.test.tsx` "the placeholder wording … must not surface anywhere" | contract (source), contract (test) |
| WI-0053 | no bar beside "Exceptional circumstance cited" | `DistributionChart.test.tsx` "WI-0053: draws no bars of its own …"; `LandingPage.test.tsx` "WI-0053: … carries a table and no bar rectangle" | presentation (component), contract (both tests) |

The one fix whose **source** file is presentation is WI-0053, and both tests that pin it are contract, so the card
app's restyled chart must still draw no bar there. That is also why ADR-063 is a reviewer decision and not a
development choice.

### 13.7 The computed sentences (ADR-062 B) — wording in every case

Every sentence is visible and `aria-hidden`; the card's `<h2>` keeps the plain heading as its accessible name
(visually hidden while a sentence shows). **"Plain heading" in the table below means no sentence: the existing
heading is shown instead.** Numbers use `formatCount`, money `formatAmount`, dates `formatDate`, all as today.

| Card | Sentence | Inputs | Plain heading when | Other cases |
|---|---|---|---|---|
| This round (hero) | "Open from {opened} to {closed}" | `roundOpenedOn`, `roundClosedOn` | opened is null | closed null: "Open since {opened}" |
| Round progress | "{n} applications in the last {d} days" (R16) | `applicationsReceived.count`; *d* from `roundOpenedOn` and `roundClosedOn` (below) | *n* is null | *n* = 0: "No applications yet"; *n* = 1: "1 application in the last …"; *d* = 1: "… in the last day"; opened date null: "{n} applications in this round"; opened date after today: "{n} applications in this round" |
| Exceptional circumstances | "1 in {N} applications cite an exceptional circumstance" | `exceptionalFundingSummary.anyCount` (*a*), `.population` (*P*) | the summary is null, or *P* is null or 0 | *a* = 0: "No application cites an exceptional circumstance"; *a* = *P*: "Every application cites an exceptional circumstance"; otherwise *N* = *P*/*a* rounded to the nearest whole number, prefixed "About " when *P*/*a* is not a whole number (12 of 48 → "1 in 4"; 7 of 48 → "About 1 in 7"). **No k-threshold applies**: these two figures are not withheld today, and the one withheld figure on this card (the average, "Not shown") is never in the sentence |
| Who applied in this round | "The people behind the applications" | none | the card has no charts (it is not rendered today either) | — |
| Level of need | "How applicants have been feeling" | none | the card is not rendered | — |
| Financial position | "The round's financial position" | none | — | it is the existing heading, so no hidden copy is needed |
| Individual applications, Group applications | eyebrow "Round {name}" | the "Review round" filter's selected option | the filter shows "All rounds available to you" and the loaded rows span more than one round | exactly one round in the loaded rows: that round's name. **No new query** |
| Group detail (hero) | "{total} requested together" | `GroupSummary.totalRequested` | the total is null | 0: "£0.00 requested together" |

**How *d* is computed (R16).** *d* is the number of calendar days the round has been open, counted **inclusively**,
in UTC as `formatDate` already uses: from the date of `roundOpenedOn` to the end date, where the end date is
**today** while the round is open (no `roundClosedOn`, or a `roundClosedOn` later than today), and the date of
`roundClosedOn` once it has passed. So *d* = (end date − open date in whole days) + 1.

- **A round opened today reads 1, not 0**: "3 applications in the last day". Zero would read "in the last 0 days",
  which contradicts applications having arrived. Counting inclusively also matches how a person counts
  "1 Sep to 30 Sep" (30 days).
- Singular forms: "1 application", "the last day" (*d* = 1). Otherwise "applications" and "the last {d} days".
- **This is the card app's own computation**, in its presentation code, from the two dates the landing screen already
  reads directly. It does **not** use the flow's `applicationsPerDay.days`, which WI-0012 calls "not a representative
  figure" and removes as a tile. The two numbers can differ, and only this one is shown in the card app.
- The first app is unchanged: it shows no headline and keeps its Days tile until WI-0012 is built there.

### 13.9 Permitted deviations (c) — what the card app cannot express without changing a contract file (R18)

The build sorts every difference from the kit into (a) contrast substitution, (b) content kept from the source, or
(c) **cannot be expressed** without changing a contract file, which under ADR-060 would change the first app too. The
reviewer accepted these three (c) cases as they are (R18, "Accept as-is (Recommended)", 2026-10-01). They stay
`contract`; neither app changes.

| # | Kit shows | Card app shows | Why it cannot follow the kit | Contract file |
|---|---|---|---|---|
| c1 | the signed-in name in bold | the whole sentence at one weight | the name is inside one template string, so there is no element to embolden | `App.tsx` |
| c2 | "Save verdict" and "Cancel" on one row in the dialog | Save inside the verdict form, "Close" in the dialog's own action row | two components render the two controls | `VerdictForm.tsx`, `VerdictDialog.tsx` |
| c3 | "Notes (optional)", no counter | the "Your verdict *" label and the character counter | this is content as well as markup (EF-05's mandatory note on Defer/Reject, Appendix B #18) | `VerdictForm.tsx` |

Every value CSS can reach is matched (label size and colour, a left-aligned action row). If the business keeps the
card app and wants any of these, each is a both-apps contract change in its own dispatch.

## Appendix A — Requirement traceability

| Requirement | Where it is met | Change |
|---|---|---|
| FR-035, FR-079 (redacted free text, three states) | `visibility.ts` under parity; `AnswerCards` | presentation only |
| FR-078 (restricted rows, never requested) | field catalogue under parity; `RestrictedList`; gate over both apps | presentation only |
| FR-036 / NFR-003 (no identifying data) | `no-secured-columns-in-code-app` over both apps | none |
| WI-0005 (Pack rows, labels, sections) | layout spec and its test, byte-identical | none |
| WI-0005 (Pack order) | first app: DOM = Pack order. New app: Pack order within display group (ADR-057) | **new app only**, reviewer R1 |
| WI-0008 (Current Circumstances as three spaced sections) | 32px between blocks | carried |
| NFR-024 (WCAG 2.1 AA) | §8; two contrast corrections | two corrections |
| R13 (round hero share of all applications) | card app hero; parser reads `historicApplicationsByMonth.priorApplicationCount` and `understatedTotal` in both apps (ADR-065) | **new, card app only**; first app parses and does not render |

## Appendix B — Content differences between the Revision 2 kit and the current source (none is a requirement)

Found by reading the kit's seven `.jsx` files and its README against the first app's source, 2026-09-30.
"Keep source" means the card app shows what the first app shows.

| # | Screen | The kit shows | The source shows | Disposition |
|---|---|---|---|---|
| 1 | Shell | "Signed in as Emily Sheardown." in `--text-muted` | the signed-in user's name, or the fallback sentence | keep source; text `--ink-600` (§8.3) |
| 2 | Shell | nav order Round overview, Group applications, Individual applications | the same (WI-0052) | no difference |
| 3 | Round overview | wellbeing series "Question 8/9/10", "Wellbeing question 8, last year" | the question wording (WI-0013) | keep source |
| 4 | Round overview | labelled bars beside "Exceptional circumstance cited", table hidden behind a toggle | table only, always visible (WI-0053, parent Revision 10) | **bars ADOPTED** (R9, ADR-063), as labelled HTML bars; table stays always visible. Previously keep source |
| 5 | Round overview | no "Type of break" section | "Type of break" table | keep source |
| 6 | Round overview | no circumstance-score chart | "Circumstance score, 0 to 60" (EF-12) | keep source |
| 7 | Round overview | no FR-062 proportions under Level of need | the proportions definitions | keep source |
| 8 | Round overview | counts beside every "Who applied" bar | shares only (parent Revision 8) | keep source |
| 9 | Round overview | "Open from 1 Sep to 30 Sep 2026", a progress bar, "Round 5" badge | "This round" with Round, Opened and (if any) Closed | **sentence and badge ADOPTED** (R8, §13.7); the bar is **replaced** by the application-share bar (R13, ADR-065). Previously keep source text, bar decorative |
| 10 | Round overview | sentence headlines ("48 applications in 59 days", "1 in 4 applications cite…", "The people behind the applications", "How applicants have been feeling") | the section headings | **ADOPTED** (R8, §13.7), with the headings kept as accessible names. Previously keep source |
| 11 | All | eyebrows above headings | none | **ADOPTED** (R8, ADR-062 A) |
| 12 | Round overview | "Entered by hand" pill; "This round" / "Charity-wide" eyebrows over the tiles | the stamp sentence; one tile row | **pill and eyebrows ADOPTED** (R12, R8, ADR-066); the sentence drops "are entered by hand and". Previously keep source sentence |
| 13 | Round overview | "Computed on 30 Sep 2026 at 15:42" | "Round figures computed on {date and time}" | **design wording ADOPTED** (R11, ADR-066): "Computed on {date} at {time}". Previously keep source |
| 14 | List, groups | "Round 5" eyebrow over the title | no round on these screens | **ADOPTED** (R8) from the filter's round, no new query (§13.7). Previously not adopted |
| 15 | List, groups | "Filter the round" eyebrow | none | **ADOPTED** (R8, ADR-062 A) |
| 16 | List, groups | 1.5px `--grey-200` control border | the strong border (ADR-037 correction 4) | keep source |
| 17 | Verdict dialog | "Approve" preselected | the saved verdict, or nothing; "Choose Approve, Defer or Reject before saving." | keep source |
| 18 | Verdict dialog | "Notes (optional)" | notes mandatory for Defer and Reject (EF-05) | keep source |
| 19 | Verdict dialog | "Save verdict" / "Cancel" in the dialog; a plain `div role="dialog"` | the section's own save, "Close", a Fluent modal | keep source |
| 20 | Verdict dialog | "You are recording the Trustee 1 verdict." | the slot sentence from `slots.ts` | keep source |
| 21 | Group detail | hero heading "£x requested together" | "Group summary" | **ADOPTED** (R8, §13.7), "Group summary" kept as the accessible name. Previously keep source |
| 22 | Kit README | detail panels "Anonymised narrative, Condition and circumstance, Care-support description …" | the Pack's five sections (WI-0005) | keep source; Revision 1 already covers the detail screen |
| 23 | Kit README | tabs "Round overview, Applications list, Group applications" | "Individual applications" (WI-0052 rename) | keep source |
| 24 | All | mock figures, dates, references, statuses | live data | ignored |
| 25 | Provenance | README "main @ 638ce23"; `github.md` "4eb731ee2a44" | — | recorded (§2.3); content matches neither exactly |
| 26 | Shell | pink focus ring | black focus ring (ADR-037 correction 3) | keep source |
| 27 | Charts | `--pink-300` and teal marks | `categoricalColor` | **kit palette ADOPTED** (R17, 2026-10-01), with teal → `#009aa8` and `--pink-300` → `--pink-500` (§8.3). Previously keep source |

## Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Reviewer | Anna Southern (session account) | 2026-09-30 | APPROVED — "Approved development" (Revision 1; 21:40 turn, relayed by lead-agent) |
| Reviewer | Anna Southern (session account) | 2026-09-30 | APPROVED — "Approved for development" (Revision 3 and 3.1, relayed by lead-agent) |
