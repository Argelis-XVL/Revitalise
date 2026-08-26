# Solution Design Document — Revitalise Grant Application Automation

**Feature Slug:** revitalise-grant-automation
**Requested By:** Revitalise (Emily, process owner), design authored by Xander Lykopoulos / Argelis Consultancy
**Date:** 2026-08-09
**Status:** APPROVED · **Amendment A-01 PROPOSED 2026-08-13 — see below, NOT yet approved** ·
**Amendment A-02 APPROVED 2026-08-24 — see below** ·
**Amendment A-03 APPROVED 2026-08-25, Resolution continued the same day
(OQ-037 resolved, FR-061 reworded) — see below** ·
**Amendment A-04 MERGED IN 2026-08-26 — the application form field corrections, previously held
in a separate SDD, adopted here on their original approval of 2026-08-16 and renumbered to
FR-070+ / NFR-030+ / US-020+ / OQ-040+ — see below**

<!-- id-allocation: FR-001..FR-063, FR-070..FR-077, NFR-001..NFR-027, NFR-030..NFR-032, OQ-001..OQ-038, OQ-040..OQ-048, US-001..US-016, US-020..US-023 -->

---

> ## 📌 Amendment A-01 — PROPOSED, awaiting plan-agent and process-owner approval
>
> **Raised by:** development-agent, 2026-08-13, during the revision 0.8 fix cycle.
> **Status: PROPOSED. This amendment is NOT approved and nothing below it has been rewritten
> as though it were.** The body of this SDD is unchanged apart from three clearly marked
> annotations that point here (FR-013, its acceptance criterion, and §9 OQ-002).
>
> ### Why this is an amendment block and not an edit
>
> This SDD is `plan-agent`'s artefact and carries **Status: APPROVED**, gated on a human
> `APPROVED` per `agents/plan-agent.md` and `agents/WORKFLOW.md`. `agents/WORKFLOW.md` defines
> no procedure for amending an approved upstream document, and `development-agent` has no
> authority to re-issue one — so silently correcting the requirement text would have bypassed
> the plan gate and made an approved document say something no one approved. The evidence is
> recorded here instead, the original wording is left visible, and the amendment is routed for
> approval. **Requested action: `lead-agent` should route this to `plan-agent` to fold into a
> revision 0.6 of this SDD and re-gate it.**
>
> ### New evidence
>
> `docs/Import/Book(Sheet1).csv` (received 2026-08-13; windows-1252 encoded) contains **25 real
> applications**, each with the published *"Overall Current Circumstance Score (Out of 60, 60 as
> most severe)"* the process owner arrived at by hand and the **eleven answers** that produced
> it. This is the first ground truth for the scoring methodology; every previous statement about
> it in this SDD came from prose in the source documents.
>
> Reconstructing the score from the answers reproduces the published total **exactly on all 25
> rows**. The reconstruction is asserted permanently, against the shipped configuration rather
> than against a copy of it, by
> `src/tests/solutions/ScoringInvariants.Tests.ps1` → *"OQ-002 — the scoring configuration
> reproduces 25 REAL hand-scored applications exactly"*.
>
> **Total = (10 − life_satisfaction_raw) + Σ points(7 SWEMWBS answers) + Σ points(3 "last year" answers)**
> where `points = {1:5, 2:4, 3:3, 4:2, 5:1, 6:0.5}` and ordinal position 1 is the highest-need
> answer on both response scales.
>
> Three competing readings were tested against the same data and fail, so the direction is
> established rather than assumed: reversing the agreement scale reproduces 7 of 24 rows,
> removing the point inversion 3 of 24, and dropping the life-satisfaction inversion 4 of 24.
>
> ### What it resolves, and what it does not
>
> | Item | Effect |
> |---|---|
> | **OQ-002** — exact scoring methodology | **RESOLVED by evidence.** The inversion, the point mapping and the full answer set are now fixed and test-asserted. |
> | **FR-013** — as written, names only an agree/disagree scale | **PARTLY WRONG, and this is test-report D-009.** Corrected wording proposed below. |
> | **FR-022** — behaviour "to be confirmed under OQ-002" | **Behaviour confirmed and strengthened.** See below. |
> | **OQ-001** — knockout cut-off and borderline band | **STILL OPEN. This amendment does NOT resolve it** — see the note below, which matters. |
>
> #### ⚠️ OQ-001 is not resolved, and was mis-scoped in the request that led to this work
>
> This fix cycle was commissioned as "resolve OQ-001 (exact scoring weights)". **OQ-001 is not
> the scoring weights.** As written in §9 it asks *"Where should the knockout cut-off score sit,
> and how wide is the borderline band Emily reviews by hand?"* — the **scoring weights are
> OQ-002**. The CSV settles OQ-002 and cannot settle OQ-001: it contains scores and answers but
> **no accept/reject outcomes**, so there is nothing in it from which a cut-off could be
> inferred. OQ-001 remains a **board/Emily decision** and stays open. (The mix-up is traceable:
> comments added in revision 0.3 claim that settling the 0-to-60 range "unblocks SDD OQ-001 and
> OQ-002". Unblocking is not resolving, and only OQ-002 is now resolved.)
>
> **What the new evidence does change about OQ-001, and the board needs to know it:** the
> reachable floor of a fully answered application has moved **from 10 down to 5**. "Not sure" is
> worth 0.5 points, so ten "Not sure" answers plus maximum reported life satisfaction total 5.
> Any knockout threshold at or below 5 was previously unreachable and now is not.
>
> ### Two substantive findings behind the amendment
>
> **1. The ten generic wellbeing questions do not share one response scale.** The seven SWEMWBS
> items (*"…over the last 2 weeks"*) are answered **None of the time / Rarely / Some of the time
> / Often / All of the time**. The three *"Thinking about the last year, have you been able
> to…"* questions are answered **Strongly disagree / Disagree / Neutral / Agree / Strongly
> agree**. Across all 25 rows the two label sets are **disjoint apart from "Not sure"**. The
> ordinal values coincide, so **no score changes** — but the three questions had been storing
> and displaying frequency labels, which mislabelled the evidence a trustee reads.
>
> **2. "Not sure" is a real sixth answer worth 0.5 points, not an error.** The live form offers
> it. Row 25 answered "Not sure" to all ten questions and scored **9**: life-satisfaction raw 6
> contributes 10−6=4, leaving exactly 5 points across 10 answers — 0.5 each, no remainder. It
> had been unstorable, which is test-report **D-014** (a real applicant's submission could be
> accepted and then lost when the scoring flow threw). The correct remedy is to make it a valid
> scoreable answer, not to reject and flag it.
>
> ### Proposed replacement wording for FR-013
>
> > **FR-013** — The system SHALL convert each wellbeing response to its configured point value
> > by the response's **ordinal position**, WHEN calculating the circumstance score, SO THAT the
> > charity's agreed need criteria are applied identically to every application. The ten
> > wellbeing questions use **two response scales with a shared set of ordinal values**: the
> > seven SWEMWBS items use a frequency scale (1 = *None of the time* … 5 = *All of the time*)
> > and the three "last year" questions use an agreement scale (1 = *Strongly Disagree* … 5 =
> > *Strongly Agree*). Position 1 is the highest-need answer on both and SHALL score the
> > configured maximum, because every one of the ten questions is worded positively. A sixth
> > response, **"Not sure"**, is a valid answer on every one of the ten questions and SHALL
> > score **0.5 points**.
>
> **Proposed replacement acceptance criterion:** *Given a wellbeing answer at ordinal position 1
> — "None of the time" on a SWEMWBS item, or "Strongly Disagree" on a "last year" question —
> when the score is calculated, then it contributes the configured maximum points for that
> question; and given an answer of "Not sure", then it contributes 0.5 points.*
>
> ### One consequence requiring a decision, not a correction
>
> A total can now be **fractional** (an odd number of "Not sure" answers gives an X.5), while
> `rev_circumstancescore` is a whole-number column. Revision 0.8 **rounds half up**, in the
> applicant's favour, and records the exact unrounded total in the score breakdown. **The data
> does not determine this rule** — every published total in the CSV is a whole number and the
> one "Not sure" row is whole by coincidence — so it is a judgement call flagged for the
> reviewer in the Dev Summary revision 0.8, not a derived fact. The alternative is to store the
> score as a decimal.
>
> ### FR-022 — confirmed and strengthened
>
> FR-022's DERIVED behaviour is confirmed as correct and its implementation was **widened**: the
> withhold gate previously tested only whether an answer was *absent*, so an answer that was
> present but had no configured point value passed the gate and reached a cast that threw. It
> now withholds for an answer that is absent **or** not a key of the point map. No requirement
> text change is proposed — this is the implementation catching up with what FR-022 already says.

---

> ## 📌 Amendment A-02 — APPROVED 2026-08-24
>
> **Raised by:** plan-agent, 2026-08-24, INTAKE MODE (`skills/how-to-intake-external-documents.md`),
> at the reviewer's request (`feature:trustee-portal-visual-refresh`; WBS 6.1, 6.3, 6.5).
>
> **Status: APPROVED.** Cleared to proceed to architecture, relayed by lead-agent from the
> reviewer's response to this session's gate: *"APPROVED — Amendment A-02 is cleared to proceed
> to architecture."* The reviewer's answers to OQ-031 and OQ-032, and CO-001's approval for the
> separately tracked landing page, are folded in below under **Resolution — 2026-08-24**. Unlike
> Amendment A-01 — raised by an agent with no gate authority over this document, so left as
> unincorporated prose pending plan-agent re-issue — this amendment was written and is now closed
> by plan-agent, which holds that authority; the new content is edited directly into §3, §4, §5,
> §6 and §9, each edit point carrying a one-line pointer back to here for the audit trail.
>
> ### Why this session ran
>
> The reviewer supplied three externally authored documents on 2026-08-24 and asked for three
> things: (1) compare the application detail screen's field list (WBS 6.3) against a sample of
> the document the team currently produces for trustees, and name every difference; (2) record a
> landing screen ahead of the existing list/detail navigation as SDD scope (WBS 6.1) — but
> **not** the landing screen's statistics content, which no WBS 6 deliverable text (6.1–6.8)
> covers and which is a separate change-order decision at `commercial-agent` under
> `feature:trustee-portal-landing-page` (`C-COM-002`); (3) say whether the sample changes what
> WBS 6.5's print/PDF output should contain. A fourth item — full-width, brand-consistent
> rendering — is captured below as a new NFR for architect-agent to resolve technically.
>
> ### Source documents
>
> | Document | Received | Used for |
> |---|---|---|
> | `docs/Import/3. Round 4 - Individual Applications.pdf` | 2026-08-24 | Ground truth for the application-detail field-list comparison (Finding 1) — 62 individual application records in one fixed layout |
> | `docs/Import/Round 3 Stats.pptx` | 2026-08-24 | Confirms the landing-page request is round-level statistics (application counts, exceptional-circumstance mix, average funding requests, demographics) — cited only to justify the scope **boundary** in Finding 2, not adopted as content |
> | `docs/Import/Round 4.pptx` | 2026-08-24 | Same as above, plus funding-capacity figures |
> | `https://revitalise.org.uk` | consulted 2026-08-24 | Business-level brand/terminology context for NFR-026 only — no UI technology or component library is adopted from it |
>
> None of the three maps onto a fresh SDD written from scratch — they are a scoped amendment to
> specific, already-approved sections. The Adoption Report classifies the **touched subsections
> only**, and the gate output says so.
>
> ### Finding 1 — WBS 6.3 application detail screen: field-list comparison
>
> FR-035 currently reads *"…a per-application detail view showing the redacted narrative, the
> score breakdown, holiday details and the staff recommendation…"* The screen is
> `ApplicationDetailPage.tsx`, rendering four panels from `CasePanels.tsx`. Comparing every field
> on the sample PDF's application record against those four panels' bound columns — checked
> against the data contract in `types.ts` and the generated Dataverse model in
> `Rev_applicationsModel.ts` — gives:
>
> | PDF field | On the trustee screen today | Finding |
> |---|---|---|
> | Type of Break (e.g. "Holiday accommodation", "Respite care facility stay") | Not shown | **Gap, low-risk, fixed by this amendment.** [`rev_breaktype`](src/code-apps/trustee-review-portal/src/dataverse/repository.ts#L86) is already read into `ApplicationDetail.breakType` ([types.ts#L81](src/code-apps/trustee-review-portal/src/dataverse/types.ts#L81)), but [`HolidayPanel`](src/code-apps/trustee-review-portal/src/components/CasePanels.tsx#L67) never renders it, and [`BREAK_TYPE_LABELS`](src/code-apps/trustee-review-portal/src/dataverse/schema.ts#L229) is an empty object — the option set is still "a placeholder set" per its own code comment. Not identifying, not special-category: the applicant chose it themselves. **Added to FR-035 below.** |
> | Accommodation/Activity Cost, Travel Costs, Other Costs (itemised) | Only the aggregate "Total costs" | **✅ Resolved 2026-08-24 (OQ-031).** Reviewer: *"Yes, safe to show. It's a total requested funding for that grant round."* No itemisation — the itemised `rev_accommodationcost`/`rev_travelcost`/`rev_othercost` columns are **not** being added. FR-035 now names a single **total funding requested for the grant round, including any exceptional funding**, rather than the holiday's itemised cost. |
> | "Please briefly explain why you're unable to fund this break yourself" | Not shown, in any form | **Not read at all.** `rev_unabletofundexplanation` is a column distinct from the narrative pair (`rev_narrativeraw` / `rev_narrativeredacted`) and is not part of `ApplicationDetail`. Same class of free text as the narrative — see the **OQ-011** annotation below. |
> | Exceptional Circumstance (category + detail — "Severe financial hardship", "Carer breakdown/urgent need") and the exceptional funding amount | Not shown | **Not read at all.** `rev_exceptionalcircumstance`, `rev_exceptionalfundingdetail`, `rev_otherexceptionalcircumstance`, `rev_exceptionalfundingrequested` and `rev_additionalamountrequested` are not part of `ApplicationDetail`. Same redaction question — see the **OQ-011** annotation. |
> | Care provided (type, hours/week, description) | Not shown | **✅ Resolved 2026-08-24 (OQ-032) — safe to show.** `rev_careprovidedtype`, `rev_carehoursperweek`, `rev_careprovidedexample`, `rev_caresupportdescription` are not yet part of `ApplicationDetail`, so reading them in is new work for WBS 6.3 rework, not a relabelling. **Still open, and not blocking:** §7.1 names no classification row for these columns — recommend architect-agent add one at TAD stage now that visibility is decided. |
> | "Are you?" (disabled person / carer applying on behalf / carer applying for themselves) | Not shown | **✅ Resolved 2026-08-24 (OQ-032) — safe to show,** as applicant-type context. No column in the generated Dataverse model corresponds cleanly to this three-way category yet — `rev_needscaresupportpersonally` (boolean) and whether `rev_supportrecipientname` is populated are the closest candidates, and neither reproduces it exactly. How it is captured/derived is an architect-agent question at TAD stage; that the trustee is allowed to see it is now decided. |
> | Means-tested benefits, benefit provider, income band, savings over £6,000, employment status | Not shown | **Correctly excluded — not a gap.** [§7.1](docs/plans/revitalise-grant-automation-plan.md#L716) already classifies "benefit status" as special category, highest restriction, *"Never shown to trustees."* The PDF's Financial Eligibility section is consistent with the approved design boundary, not evidence against it. |
> | Condition/illness checklist, the "Brief Confirmation" health narrative, support-recipient condition profile | Not shown | **Correctly excluded — not a gap.** Special-category data per §7.1; FR-016 and FR-031 already keep it out of every trustee-facing view except through the still-deferred narrative-redaction pipeline. |
> | Helper / referee / emergency-contact names and contact details | Not shown | **Correctly excluded — not a gap.** FR-036. |
> | Score-breakdown detail (life satisfaction 0–10, the seven "last 2 weeks" answers, the three "last year" answers) | `ScorePanel` shows one free-text `rev_scorebreakdown` column | **Unverified, not a confirmed gap.** Whether that text reproduces the PDF's per-question table or only the arithmetic result cannot be told from the codebase alone — it depends on what Automation #2's scoring flow writes on a live record. Recommend architect-agent or test-agent check one real record before WBS 6.3 rework starts. |
>
> **Adopted FR-035 replacement wording**, incorporating the reviewer's OQ-031/OQ-032 answers —
> everything else in the table above that is not named here stays an open question (OQ-011
> remains open):
>
> > **FR-035** — The system SHALL provide a per-application detail view showing the redacted
> > narrative, the score breakdown, the type of break, the preferred dates, the break location,
> > the total funding requested for the grant round (including any exceptional funding
> > requested), the applicant-type context (disabled person / carer applying on behalf of a
> > disabled person / carer applying for themselves), the care-support context (type of care
> > provided, hours of support per week, and the care-support description), and the staff
> > recommendation, SO THAT trustees who prefer to read the case have the full anonymised
> > picture. *(Amendment A-02, adopted 2026-08-24. Adds "type of break", the applicant-type and
> > care-support context — both confirmed safe to show by the reviewer under OQ-032 — and
> > replaces "the total cost and the amount requested" with a single total-funding-requested
> > figure per the reviewer's OQ-031 answer, so no itemised cost breakdown is built.)*
>
> ### Finding 2 — WBS 6.1 navigation: a landing screen, not landing-page content
>
> WBS 6.1's own contracted deliverable text is *"App design + trustee role"* — designing the
> app's screens is exactly what this task already pays for, so restructuring navigation from
> list → detail (today) to **landing → overview/list (FR-034/WBS 6.2) → detail (FR-035/WBS
> 6.3)** needs no change order. **What the landing screen contains is a different question.** The
> reviewer separately wants it to carry round-level statistics — application counts,
> exceptional-circumstance mix, average funding requests — sourced from `Round 3 Stats.pptx` and
> `Round 4.pptx`. No deliverable text in `contract/wbs.json` automation 6 (6.1–6.8) names a
> statistics or summary screen, so that content is tracked separately as
> `feature:trustee-portal-landing-page`, routed to `commercial-agent` for a change-order decision
> (`C-COM-002`). **New FR-056 below covers the navigation shell only** — that a landing screen
> exists and where it leads — and says nothing about what is on it.
>
> ### Finding 3 — WBS 6.5 print/PDF: no separate content decision needed
>
> `ApplicationDetailPage.tsx`'s print button calls `window.print()` on the same DOM the four
> panels render (FR-039) — it does not assemble a separate export. So every field-list change
> above — the adopted FR-035 update, and whatever OQ-011 eventually resolves — reaches the
> print/PDF output automatically, with no separate WBS 6.5 requirement to write. The one
> structural difference worth recording: the real board pack batches many applications into one
> document (62, in the sample), while this portal's print option is per-application. That is
> already covered by FR-032/FR-033's per-application document and scheduled pack (Automation #5,
> still deferred per `EX-003`) — not a WBS 6.5 gap.
>
> ### Finding 4 — full-width, brand-consistent rendering (new NFR-026)
>
> Captured at business level only, per the reviewer's instruction: the app should read as a
> Revitalise product — full browser width rather than the platform's default constrained canvas,
> and visually consistent with `revitalise.org.uk`. No component library, design system or CSS
> approach is adopted here; that is architect-agent's decision at TAD stage. See NFR-026 in §5.
>
> ### Open questions raised or annotated
>
> New at the time this amendment was drafted: OQ-031 (itemised holiday costs), OQ-032
> (care-support context and applicant-type — visibility), **OQ-033** (design system for
> NFR-026, still open). Annotated with new evidence: **OQ-011** (the anonymisation-rules question
> now names two more free-text columns needing the same redaction decision as the main narrative
> — still open). OQ-031 and OQ-032 were resolved before this amendment closed; see below.
>
> ### Resolution — 2026-08-24
>
> The reviewer responded `APPROVED` to this amendment, with explicit answers to both open
> questions raised during drafting, relayed by lead-agent:
>
> - **OQ-031 (itemised holiday costs) — RESOLVED, safe to show.** Reviewer's own words: *"Yes,
>   safe to show. It's a total requested funding for that grant round."* Read literally: no
>   itemised accommodation/travel/other breakdown is built; FR-035 shows one total-funding-requested
>   figure instead, matching what is actually being asked for.
> - **OQ-032 (care-support context and applicant-type) — RESOLVED, also safe to show,** per the
>   reviewer's explicit follow-up confirming both OQ-031 and OQ-032 together. §7.1's classification
>   table still names no row for the care-support columns — that is a TAD-stage documentation
>   task for architect-agent, not a reason to withhold the reviewer's decision.
> - **OQ-033 (NFR-026 design system) stays open** — it was not part of this exchange and is
>   correctly architect-agent's decision, not the reviewer's, at TAD stage.
> - **OQ-011 stays open** — the redaction scope for `rev_unabletofundexplanation` and the
>   exceptional-circumstance free text was not addressed by this resolution and remains an
>   Automation #5 / DPO question.
>
> **Separately, CO-001 (`contract/change-orders/CO-001.md`) is APPROVED**, creating **WBS 6.9**
> ("Round-statistics landing screen", `depends_on: 6.1`) for the landing-page content this SDD
> has deliberately excluded throughout (§3, Finding 2). CO-001 also records the reviewer's answer
> to a separate open item raised during its own scoping — whether `Round 4.pptx`'s funding-capacity
> figures are safe to surface as-is — resolved: *"The Round 4 doc is indeed about grant fund
> numbers,"* i.e. the charity's own figures, safe to surface as shown. **That content is still not
> authored in this SDD** — CO-001 explicitly defers the landing page's own FR/NFR text and firm
> effort figure to a follow-up plan-agent dispatch for `feature:trustee-portal-landing-page`, which
> this session has not run. One reconciliation note for whoever runs that dispatch: as of this
> writing, `contract/wbs.json` does not yet list task `6.9` even though CO-001 records it as
> approved WBS placement — a gap between the change-order record and the generated WBS file worth
> closing before that dispatch cites it, not something this plan-agent session edits (`wbs.json`
> is pm-agent/commercial-agent's generated artefact, not plan-agent's).

---

> ## 📌 Amendment A-03 — APPROVED 2026-08-25
>
> **Raised by:** plan-agent, 2026-08-24, INTAKE MODE (`skills/how-to-intake-external-documents.md`),
> dispatched by commercial-agent per `contract/change-orders/CO-001.md`
> (`feature:trustee-portal-landing-page`; **WBS 6.9**, `depends_on: 6.1`).
>
> **Status: APPROVED.** Cleared to proceed to architecture, relayed by lead-agent from the
> reviewer's answers to all three items gating this amendment (round auto-scope, suppression
> threshold, funding-figure source) plus confirmation of the fourth (extra scope beyond CO-001's
> ROM) — folded in below under **Resolution — 2026-08-25**. This amendment authors the SDD
> content CO-001 deferred — FR/NFR text for the round-statistics landing screen. wbs.json still
> does not list task 6.9 as of this writing (carried forward from Amendment A-02's reconciliation
> note above; still true, still not this agent's file to edit).
>
> ### Why this session ran
>
> CO-001 (APPROVED 2026-08-24) created WBS 6.9 for a round-level statistics landing screen,
> positioned ahead of the existing applications list (WBS 6.2) per Amendment A-02's navigation
> shell (FR-056). CO-001 authorised the content *categories* — application counts, category/
> percentage breakdowns, funding figures, demographic and circumstance-score distributions — but
> explicitly deferred the FR/NFR text and firm effort figure to this dispatch. This amendment
> supplies that text, working directly from the two source decks rather than from CO-001's own
> summary of them.
>
> ### Source documents
>
> | Document | Received | Used for |
> |---|---|---|
> | `docs/Import/Round 3 Stats.pptx` | 2026-08-24 | Primary source — 6 slides, 6 embedded charts. An application-intake profile: received-count/rate, exceptional-circumstance mix, break-type/cost table, gender/ethnicity/age-range distributions (each charted against a "UK cared-for disabled adults and their carers" benchmark), the applicant-type split, and wellbeing-question/life-satisfaction distributions |
> | `docs/Import/Round 4.pptx` | 2026-08-24 | 3 slides, no embedded charts — numbers only. A **different shape** of content (Finding 1): a financial/impact summary — applications received, amount spent, people supported, grant-giving capacity, suggested maximum spend, monthly disbursement, remaining legacy-fund split |
>
> Both decks' final slide is the same "Overall Current Circumstance Score" methodology explainer
> already covered by FR-011–FR-013 (and Amendment A-01's still-pending correction to FR-013).
> **Not adopted as landing-screen content** — it explains how an existing score is calculated, it
> is not a round statistic, and repeating it here would double-cover ground A-01 already owns.
>
> ### Finding 1 — the two decks are not two instances of one shape
>
> The dispatch describes them as "presumably different rounds of the same shape." They are not.
> `Round 3 Stats.pptx` is an **application-intake profile** — who applied and what they asked for,
> all derivable from the Application entity already classified in §7.1/§7.2. `Round 4.pptx` is a
> **funding/impact summary** — money spent, people reached, capacity remaining — which reads as
> finance/board-reporting content, not application data, and several of its figures (grant-giving
> capacity, remaining legacy split) describe the charity's fund position generally rather than
> Round 4 specifically (Finding 3). Neither deck contains the other's content. A landing screen
> built to resemble both decks needs two different data sources, and for at least one of them,
> content that is not scoped to a single round at all.
>
> This SDD adopts the **union** of both decks' content, per CO-001's scope text, but records the
> shape mismatch as a real finding rather than smoothing it into one uniform metric list, and
> leaves the financial figures' provenance open (Finding 3) rather than assuming it.
>
> ### Finding 2 — round scoping: no selector, and no "Round" entity to select from
>
> The dispatch asks how a trustee is shown "that specific grant round." No `Round` (or similar)
> entity exists in the current data model.
> [Architecture §3.1](docs/architecture/revitalise-grant-automation-architecture.md#L317) and
> [`types.ts`](src/code-apps/trustee-review-portal/src/dataverse/types.ts#L60) both describe
> `rev_reviewround` as a free-text tag on the Application/Review rows, existing specifically to
> "scope trustee visibility to the current round" (FR-038) — the same mechanism the applications
> list (WBS 6.2, FR-034) already uses. No round-picker control exists anywhere in the built app;
> the `types.ts` comment ("drives the round selector") documents an intended future consumer of
> the field, not a component that exists today.
>
> Given that, the lowest-risk and lowest-effort reading — and the one that fits `CO-001`'s 5–8h
> ROM far better than building a new round-browsing UI — is that the landing screen needs no
> selector at all: it aggregates over exactly the application set FR-038/FR-034 already scope the
> signed-in trustee to, so "that round" is simply whichever round the trustee is currently
> authorised to review. **Recorded as FR-057 below.** The one case this does not resolve — a
> trustee authorised across more than one open round at once, which
> [`TrusteeRepository`'s own comment](src/code-apps/trustee-review-portal/src/dataverse/types.ts#L139)
> ("every application… across all rounds they can reach") suggests the data model at least allows
> — is recorded as **OQ-034**, not assumed away.
>
> ### Finding 3 — the funding/capacity figures' source and cadence are not established
>
> `Round 4.pptx` slide 2's "Grant-giving capacity increased £100k → £338k" and "Remaining legacy
> split: £55,844.30" describe the charity's overall fund position, not an event scoped to Round
> 4's application window — nothing pins them to "this round" the way an application count is.
> CO-001 already resolved that these figures are *safe to show* (the reviewer's "grant fund
> numbers" confirmation) — this finding is a different question CO-001 did not reach: what in
> this system, if anything, produces them. No entity in §7.2 owns a "grant-giving capacity" or
> "legacy split" figure; Bank Account and Payment data are finance-role-only under NFR-002, and
> it is not established whether these landing-screen figures are computed from those records or
> are a manually maintained finance snapshot supplied each round — which would make this input
> data, not derived data. Recorded as **OQ-036**.
>
> ### Finding 4 — small counts create a disclosure risk the content-safety approval didn't examine
>
> CO-001's approval that this content is "safe to surface" was a business judgement about
> categories of information, not about specific numbers. `Round 3 Stats.pptx` slide 2's own
> figures include an exceptional-circumstance category of **6** applicants ("Palliative care")
> out of 434 — small enough, combined with the region and date-range information a trustee
> already sees elsewhere in the portal (FR-034), to risk narrowing a rare category toward an
> identifiable individual. This is a standard small-cell disclosure-control gap, not a reason to
> withhold the category — **NFR-027 below** requires suppression or grouping below a threshold;
> the threshold itself is not decided (**OQ-035**).
>
> ### Open questions raised
>
> New: **OQ-034** (simultaneous multi-round trustee access), **OQ-035** (minimum cell size for
> category suppression), **OQ-036** (source/cadence of the funding-capacity figures), **OQ-037**
> (provenance and maintenance of the UK-benchmark demographic dataset), **OQ-038** (whether the
> full derived catalogue fits `CO-001`'s 5–8h ROM). All five are new in §9 below; none is
> resolved by this amendment.
>
> ### Resolution — 2026-08-25
>
> The reviewer answered all three items gating this amendment, plus confirmed a fourth, relayed
> by lead-agent:
>
> - **FR-057 (round auto-scope) — CONFIRMED as written, plus new information.** Reviewer's exact
>   words: *"for now its one round at a time. Once a month."* One grant round is open for trustee
>   review at a time, on a monthly cadence. FR-057 is updated below to record the cadence — new
>   information, not just a confirmation of the auto-scope design. **This also resolves OQ-034**
>   (simultaneous multi-round access) as **N/A**: with exactly one round open at a time, a trustee
>   is never authorised across two rounds at once, so no selector is needed. Closed with this
>   answer rather than left open separately.
> - **OQ-035 (minimum cell size / suppression threshold) — RESOLVED, and NFR-027 is withdrawn.**
>   Reviewer's exact words: *"no minimum group size. The whole point of the code app is for
>   trustees to review items and the column security profile scrubs aways personal information."*
>   This is an explicit reviewer risk-acceptance decision overriding NFR-027's proposed control,
>   not a silent removal — recorded in §7.1 and §9 with this rationale so it is traceable if a DPO
>   reviews this later. The reviewer's own reasoning is that the app's existing field-level
>   security profile is the control for personal-data exposure (the mechanism NFR-001/NFR-003
>   already rely on), not aggregate-level suppression, which was plan-agent's proposal and is now
>   stood down. NFR-027 is marked **WITHDRAWN** below rather than deleted, so the proposal and the
>   reason it was not adopted both stay on the record.
> - **OQ-036 (source of the funding/capacity figures) — PARTIALLY RESOLVED.** Reviewer's exact
>   words: *"at the moment everything is manual. Maybe have this land on the finance accessable
>   tables? Or an extra table that finance fills in these details."* Confirmed at business level:
>   these figures are finance-maintained, not derived from Application/Grant/Payment records.
>   FR-063 is updated below to say so. The reviewer raised two concrete mechanisms — extend an
>   existing finance-accessible table, or a new table finance fills in — and this SDD does not
>   choose between them: that is a schema/technology decision for architect-agent at TAD stage.
>   OQ-036 stays open at that narrower scope.
> - **OQ-038 (does the catalogue fit CO-001's ROM) — CONFIRMED extra scope.** Reviewer's exact
>   words: *"Yes, this is extra scope not delivered initially."* Hours for FR-057–FR-063 are
>   **not** covered by CO-001's original 5–8h ROM and are pending a separate commercial-agent
>   sizing pass / CO-001 amendment, dispatched independently by the reviewer. §10 below is updated
>   so it no longer implies the original figure still holds.
>
> **OQ-037** (UK-benchmark dataset provenance) was not part of this exchange and stayed open at
> this point, non-blocking — it gated FR-061's benchmark-comparison content specifically, not
> WBS 6.9's build as a whole. It was answered later the same day — see
> **Resolution (continued)** immediately below.
>
> With the three gating items answered, **this amendment is APPROVED.**
>
> ### Resolution (continued) — OQ-037, 2026-08-25
>
> A second reviewer exchange the same day, relayed by lead-agent after architect-agent's TAD for
> WBS 6.9 reached the same conclusion from the technical side, closes the one item the Resolution
> above left open.
>
> - **OQ-037 (UK-benchmark dataset provenance) — RESOLVED: there is no dataset, and FR-061's
>   benchmark-comparison clause is withdrawn.** Reviewer's exact words: *"there is no benchmark
>   dataset. This is personal knowledge of the trustees. So only showing the representation of
>   applications is enough."* Nobody ever sourced or owned a published UK
>   cared-for-disabled-adults-and-carers dataset — which is exactly what OQ-037 was asking about —
>   and the population context trustees compare against is their own knowledge, which does not
>   need restating on screen. **FR-061 is reworded below** to drop the comparison clause while
>   keeping the applicant distribution reporting (gender, ethnic-group, age-range and
>   applicant-type percentages) unchanged. §7.2's benchmark reference-data row is struck through,
>   and US-016 AC-5 loses its "compared against the UK benchmark" clause. Same treatment as
>   NFR-027 above: struck through and annotated, never silently deleted.
>
> **Two things this does *not* change.**
>
> First, the ethnic-group figure's own data gap. `rev_ethnicgroup` has never been collected by the
> charity and was deliberately never built, so FR-061's ethnicity distribution still has no source
> data. That is a different gap, raised independently by architect-agent's TAD at
> [§3.4](docs/architecture/trustee-portal-visual-refresh-architecture.md#L363) and risk
> [A-R24](docs/architecture/trustee-portal-visual-refresh-architecture.md#L924), and gated by
> **OQ-027** (is ethnic group actually captured at all). **Untouched by this amendment and still
> open** — resolving OQ-037 does not narrow it, because withdrawing the comparison does not
> conjure the figure being compared.
>
> Second, hours. FR-061 is now smaller than the catalogue commercial-agent's in-progress CO-001
> sizing pass was handed (OQ-038) — flagged in §10, not re-sized here.

---

> **Source:** adopted from `docs/Import/Revitalise-Automation-Solution-Design-v0.5.docx` on 2026-08-09 by plan-agent (intake mode).
> Original author: Xander Lykopoulos — Argelis Consultancy (v0.5 Draft, 14 July 2026).
> Read via a plain-text extraction of the same content. See Adoption Report in gate log.
>
> **Supporting sources** (received 2026-08-09, used for §1, §7, §8 and §9 only — no functional requirements were created from them beyond the cross-cutting retention/erasure behaviour they mandate):
> - `docs/Import/Revitalise-Process-Flow-v0.1.html` — Process Flow v0.1, July 2026 (Draft, for discussion)
> - `docs/Import/Revitalise-DPIA-v0.1.docx` — Data Protection Impact Assessment v0.1, 15 July 2026 (**Concept — for DPO review**)
> - `docs/Import/Revitalise-RoPA-v0.1.docx` — Record of Processing Activities v0.1, 15 July 2026 (**Concept — for DPO review**)
> - `docs/Import/Revitalise-Data-Governance-Framework-v0.2.docx` — Data Governance Framework v0.2, 15 July 2026 (Draft)
> - `docs/Import/Revitalise-Security-Model-v0.1.docx` — Security Model v0.1, 15 July 2026 (Draft) — used for business-level persona/role facts only
>
> **Deliberately not adopted into this SDD** (they belong to the architecture intake that follows):
> `docs/Import/Revitalise-Solution-Architecture-v0.4.docx`, `docs/Import/Revitalise-ALM-Runbook-v0.1.docx`, `docs/Import/Revitalise-Governance-Runbook-v0.1.docx`.

> ## 📌 Amendment A-04 — Application form field corrections, MERGED IN 2026-08-26
>
> **Raised by:** plan-agent, 2026-08-26, resolving the 19-identifier allocation collision reported
> by `scripts/verify-requirement-id-uniqueness.py` and recorded as defect **D-09** in
> `docs/tests/trustee-portal-visual-refresh-test-report.md`.
>
> **Status: ADOPTED on its original approval.** This amendment does not approve new requirements.
> It moves an existing, already-approved and already-delivered body of requirements into this
> document, which is now their single home. The requirements themselves are carried forward
> **verbatim**; only their identifiers changed.
>
> ### What was merged, and why it had to be
>
> The seven work items below were specified in a separate SDD,
> `docs/plans/revitalise-form-field-corrections-plan.md` (revision 1.4, approved 2026-08-16), and
> built, tested and deployed to DEV on 2026-08-17. That document declared its identifiers by
> **continuing this document's numbering** — FR-056 onward — on the stated grounds that "no
> identifier is reused". That was true on the day it was written.
>
> It stopped being true eight days later. Amendments A-02 and A-03 also continued this document's
> numbering, and independently allocated FR-056–FR-063, NFR-026–NFR-027, OQ-031–OQ-038 and US-016
> to the trustee-portal landing screen. **Nineteen identifiers came to mean two unrelated
> requirements each** — FR-062 was "care-hours band" in one document and "wellbeing distributions"
> in the other; NFR-027 was "record the necessity argument" in one and the withdrawn
> minimum-cell-size rule in the other. Neither document was wrong; neither read the other.
>
> **The root cause is structural, not clerical: a delta SDD that numbers itself by continuing its
> parent's sequence collides with that parent as soon as the parent grows.** The fix is therefore
> also structural — this document becomes the sole allocator of requirement identifiers for the
> grant-automation solution, which is already the pattern every other delta feature here follows
> (`trustee-portal-visual-refresh` and `trustee-portal-org-url-fix` have a TAD, a dev summary and a
> test report but no plan document of their own, and `revitalise-grant-record-plan.md` declares
> `id-allocation: none`). The form-field corrections were the only exception, and the collision is
> what that exception cost.
>
> ### Identifier remap — the authoritative mapping
>
> Old identifiers appear in the retired SDD, in
> `docs/architecture/revitalise-form-field-corrections-architecture.md`, in the dev summary, in the
> test report and in one Pester suite. All have been updated. This table is the record of what
> moved, so a stale citation found later can be resolved rather than guessed at.
>
> | Old (retired SDD) | New (this document) | Requirement |
> |---|---|---|
> | FR-056 | **FR-070** | Exceptional circumstance recorded as one of four categories |
> | FR-057 | **FR-071** | Applicant's own wording retained when "Other" is selected |
> | FR-058 | **FR-072** | Employment status recorded as one of five values |
> | ~~FR-059~~ | *not carried* | Legacy Yes/No handling — withdrawn at revision 1.1, superseded by FR-077. No identifier allocated, because the requirement has no force |
> | FR-060 | **FR-073** | Preferred contact method (multi-select) |
> | FR-061 | **FR-074** | Consent explanation retained |
> | FR-062 | **FR-075** | Hours of care recorded as one of five bands |
> | FR-063 | **FR-076** | Three carer columns not held until the form asks |
> | FR-064 | **FR-077** | Option-list drift surfaces as an exception, never a guessed value |
> | NFR-026 | **NFR-030** | Art. 6 / Art. 9 classification before build |
> | NFR-027 | **NFR-031** | Necessity argument recorded where an Art. 9 column is released to trustees |
> | NFR-028 | **NFR-032** | No option-set renumber once a record references it |
> | US-016 | **US-020** | The reason for an exceptional request survives to the decision |
> | US-017 | **US-021** | Inability to work is not recorded as simply "not working" |
> | US-018 | **US-022** | An applicant who asked for post is contacted by post |
> | US-019 | **US-023** | The caring load is on the record |
> | OQ-031 … OQ-039 | **OQ-040 … OQ-048** | In order, one-for-one |
>
> The new blocks start at FR-070, NFR-030, US-020 and OQ-040 — clear of **both** this document's
> used range and the retired SDD's, so no identifier ever means two things and no stale citation
> can silently resolve to the wrong requirement. The gaps (FR-064–069, NFR-028–029, US-017–019,
> OQ-039) are deliberate and are the visible signal that a renumbering happened here.
>
> The work-item ids **W1–W7** and the gate-decision ids **D-1–D-7** are carried forward unchanged.
> They are referenced from `Entity.xml` comments in the solution source and from the TAD, and this
> document uses neither token for anything else.
>
> ### Delivery status — this is a record of shipped work
>
> Unlike A-01 to A-03, these requirements were built before they were merged here. W1–W6 are
> present in the solution source (`rev_employmentstatus`, `rev_preferredcontactmethod` and
> `rev_consentexplanation` exist; `rev_currentlyworking` and the three carer columns survive only
> as dated removal comments in `rev_application/Entity.xml`), and FR-076 and FR-077 are asserted by
> `src/tests/solutions/IntakeContract.Tests.ps1`. Packaged as build #6 (`logs/build.log`, 2026-08-17
> 16:10) and deployed to DEV at **V3** (`logs/pipeline.log`, 2026-08-17 20:45 — schema delta, intake
> flow and forms verified live via a direct Web API query). Evidence sits in
> `docs/development/revitalise-grant-automation-dev-summary.md` and
> `docs/tests/revitalise-grant-automation-test-report.md`, not in this document.
>
> ⚠️ **V4 is not claimed and must not be inferred from this block.** Reaching it still requires a
> human open-and-save of the Application form and a trustee-role read that confirms D-1 hides the
> employment status and D-6 shows the exceptional-circumstance category. The test report at its
> revision 7 was written *before* the 20:45 deploy and correctly said the work was not yet imported;
> that sentence is a point-in-time record and has been left as written.
>
> ### Origin of the findings
>
> The grant application form is built and hosted on WordPress (Gravity Forms) by Alex; the Dataverse
> schema that receives it was built here. Nobody built both. This pass came from the reviewer
> opening both forms side by side and reading them, which produced seven findings — five of them new
> or contradicting what the repository believed. Two were **regressions introduced the same day** in
> commit `1faf2b4`, made in good faith from a visual check that read the wrong export column:
> `rev_exceptionalcircumstance` was converted from a Choice to a Boolean on the stated grounds that
> the live form asks Yes/No (it does not — raw export column **128** is the Yes/No question, already
> held by `rev_exceptionalfundingrequested`; column **129** is a separate four-option radio, and the
> two are adjacent in the export, which is how they came to be conflated); and
> `rev_carehoursperweek` was added as an integer against a question the form asks as five bands, so
> it could never be populated as built.
>
> ### Work items
>
> | # | Work item | Nature |
> |---|---|---|
> | **W1** | `rev_application.rev_exceptionalcircumstance` — revert Boolean → Choice; restore the option set with the four real values; **trustee-visible, not secured** (D-6) | Regression fix + reclassification |
> | **W2** | `rev_application.rev_currentlyworking` → **`rev_employmentstatus`** (D-7) — Boolean → Choice with the five values the live form already sends (D-3); **secure it** (D-1) | Regression fix + reclassification + rename |
> | **W3** | `rev_applicant.rev_preferredcontactmethod` — new multi-select Choice (Email / Phone / Post) | New column, closes part of M-09 |
> | **W4** | `rev_application.rev_consentexplanation` — new secured multi-line text | New column, closes part of M-09 |
> | **W5** | `rev_application.rev_carehoursperweek` — integer → Choice with the five bands at D-4 | Regression fix |
> | **W6** | Remove `rev_travellingwithcarer`, `rev_carername`, `rev_carersupport` — those three only (D-5) | Removal, closes part of M-10 |
> | **W7** | Cross-cutting: option-list drift must fail loudly, not silently | New rule (FR-077) |
>
> ### Decisions taken at the original plan gate — 2026-08-16
>
> | # | Decision | Effect |
> |---|---|---|
> | **D-1** | **Secure the employment column.** Released to the process owner and the service identity only, via `REV_TrusteeRestricted`. *Superseded in part by D-6 — originally covered both reclassified columns.* | Adds one `IsSecured=1` attribute and one `FieldPermission` entry. |
> | **D-2** | **No data exists in DEV.** | Settles **OQ-040**. Every delete-and-recreate and every option-set renumber in this pass is safe. This is the window; it closes at the first real application. |
> | **D-3** | **The live form already asks the employment question as five options.** | Settles **OQ-042**, and removes the external dependency on Alex for W2. Also means `form-validation-spec.md` §4 is stale — see **OQ-046**. |
> | **D-4** | **CORRECTED at revision 1.4.** Care-hours bands are `9 hours or less` / `10 – 19 hours` / `20 – 34 hours` / **`35 – 59 hours`** / `50+`. The band-four value agreed at revision 1.0 (`35 - 50 hours`) was itself the misreading — three independent re-fetches of the live form on 2026-08-16, one asking specifically for the raw radio-input markup, all returned "35 – 59 hours", and the reviewer confirmed this directly against the page. | Settles **OQ-043** a second time, in the opposite direction from the first pass. **Reopens V-10**: bands four and five overlap at 50–59 hours, exactly as the original validation spec flagged. |
> | **D-5** | **The removal is the three carer columns only.** | Settles **OQ-044**. `rev_supportrecipientname`, `rev_providerpreference`, `rev_applicant.rev_title` and `rev_privacynoticeacceptedon` stay, and remain open as M-10 items. |
> | **D-6** | **`rev_exceptionalcircumstance` stays trustee-visible — do not secure it.** The trustees have a reason to see it: they cannot judge a request for exceptional funding without knowing what the exceptional circumstance is. | Settles **OQ-047** by removing the gap rather than filling it. Reverses the exceptional-circumstance half of D-1. Raises **OQ-048** (DPIA/RoPA must record it). §7.1a shows this is the solution's *existing* rule, not an exception to it. |
> | **D-7** | **Rename the employment column to `rev_employmentstatus`** ("Employment Status") as part of its recreate. | Settles **OQ-041**. The intake payload field becomes `employment_status`. Free now only because D-2's window is empty. |
>
> ### Assumptions and dependencies carried forward
>
> **The destructive window (D-2).** Every type change in this pass was a delete-and-recreate of a
> live Dataverse attribute — Dataverse has no in-place Choice↔Boolean or int↔Choice conversion — and
> every option-set trim renumbers values. Both are safe only while no record references them. D-2
> confirmed nothing was at risk on 2026-08-16. **That assumption expires at the first real
> application**, which is why NFR-032 is written as a compliance requirement rather than a note.
>
> **V-10 stays open.** The live form's fourth care-hours band (`35 – 59 hours`) overlaps the fifth
> (`50+`) across ten whole hours. The option set was built as the five values the form actually
> sends, overlap included, because re-inventing a cleaner band would repeat in miniature the exact
> mistake this pass existed to fix — choosing what a value "should" be instead of recording what the
> form asks. This is FR-077's own principle applied to the charity's own form copy. V-10 belongs in
> the change request to Alex (V-01 … V-11) and is **not** resolved here.
>
> **Conflict with FR-003, unresolved.** FR-003 requires the form to "present carer questions only
> when the applicant has indicated they are travelling with a carer". W6 removed the columns those
> questions would write to. That is not a reason to keep empty columns the form has never asked for,
> but it does leave **FR-003 as a requirement with no implementation and no data destination**. This
> is recorded here, in FR-003's own document, which is the action the retired SDD said was owed to
> this one.
>
> ### Effort and contracted scope
>
> The retired SDD sized this pass at **M**. That figure is historical: the work is delivered, so the
> estimate has been superseded by actual delivery evidence and is not restated here (`C-COM-008`).
>
> ⚠️ **Commercial scope is not settled by this amendment and is not settled here.** These corrections
> followed a V4 review and no accepted WBS task names them as a deliverable. The requirements serve
> tasks **0.4** (Dataverse solution & table schema build), **0.5** (security roles & field-level
> security), **4.2** (field mapping document) and **4.3** (intake flow) in `contract/wbs.json`, but
> whether corrective rework after a review is covered by those tasks or is a change order is a
> `commercial-agent` decision under `C-COM-002`. **Flagged, deliberately not opened** — merging a
> document must not quietly decide a pricing question.

> ⚠️ **Reader's note.** The DPIA and RoPA that underpin §7 of this document are both at
> **"Concept draft — for DPO review"** status. They are not signed off. Three specific DPO
> decisions (OQ-004, OQ-005, OQ-006) gate build on the current design basis. This SDD may be
> approved as a statement of requirements, but build must not start on the field-level-security
> and 6-year-retention basis until those three decisions are recorded.

---

## 1. Business Context

Revitalise is a charity that awards respite-holiday grants to unpaid carers and the disabled
people they care for. The grant application process today runs across ten high-level steps and
consumes roughly **four hours of staff time per successful grant**, almost all of it carried by
one person — Emily, the process owner.

The cost is concentrated in manual data handling, not in decision-making:

- **60% of processing time is spent chasing applicants for missing information.** Applicants have
  a low average literacy level (around age-12 reading equivalent) and are applying while under
  strain, so forms arrive part-completed and each one generates several follow-up contacts.
- **Every application is scored by hand.** Emily converts wellbeing answers into a score out of 60,
  including an inverted scale on one question and Likert mapping on others.
- **Applications are moved between systems by hand.** Emily logs into the website, exports
  submissions to Excel and imports them into a master spreadsheet, in batches, creating delay
  between submission and assessment.
- **Trustee packs are anonymised by hand.** Before each monthly board cycle Emily strips names,
  contact details, addresses, ages and gender references, and scrubs free-text narratives where
  applicants refer to themselves, family members, places or clinicians. Find-and-replace misses
  indirect references such as "my husband John" or "our GP at the Riverside Practice". This takes
  three to four hours per cycle, twelve cycles a year.
- **Trustees receive a static mail-merged Word pack** plus a master spreadsheet. It is hard to
  navigate at 20+ applications, one trustee (Kevin) wants a stripped data-only view while others
  want the narrative, and decisions come back as scattered emails that Emily collates manually.
- **Acceptance forms are built in Canva, exported as PDF and emailed.** Dual signature is required
  (applicant plus referee or GP). Average return time is five days; some run to weeks.
- **Duplicate-grant checking is a manual email-address lookup.** Manageable at 68 cumulative
  grants; unreliable as volume grows across years.

The current run rate is 68 grants in roughly four months, against a planning assumption of ~200
grants per year. The process does not scale, and it carries a single-point-of-failure risk: the
master spreadsheet is effectively "Emily's laptop is the source of truth".

Alongside the efficiency problem there is a compliance problem. The process handles
**special-category health and disability data about people in vulnerable circumstances, at scale**,
plus bank details and financial hardship information. The manual anonymisation control depends on
one person doing a careful job under time pressure, and a single missed name in a trustee pack is a
personal-data breach. A DPIA is required under UK GDPR Article 35 for this processing.

---

## 2. Objectives

*(DERIVED — the source states outcomes and savings but does not list objectives explicitly.)*

1. **Cut staff handling time per successful grant from ~4 hours to under 1 hour**, releasing
   approximately 330 staff hours per year at ~200 grants/year.
2. **Prevent incomplete applications at source** rather than chasing them afterwards, targeting a
   60–70% reduction in incomplete submissions.
3. **Make assessment consistent and evidenced** by calculating the circumstance score
   automatically against criteria the charity controls, while keeping a human able to review and
   override every outcome.
4. **Replace manual anonymisation with a platform-enforced control** so that trustee review is
   anonymous by design, with human review of anything the automated redaction is unsure about.
5. **Give trustees one place to review cases and record decisions**, serving both the data-only
   and narrative-reading preferences from the same source, with an offline fallback so no trustee
   is excluded.
6. **Remove chasing from grant acceptance** by issuing pre-populated dual-signature acceptance
   documents with automatic reminders and escalation.
7. **Establish a single, governed system of record** with automatic retention and erasure, so no
   record depends on someone remembering to delete it, and remove the spreadsheet dependency.
8. **Keep the whole solution inside Revitalise's published data-protection position** — UK data
   residency, least privilege, documented lawful bases, and an auditable trail.
9. **Leave the solution maintainable by a non-developer** — thresholds, templates and mappings
   adjustable by Emily or a future administrator without code.

---

## 3. Scope

### In Scope

Seven automations, in the source's priority order:

| # | Automation | Business outcome |
|---|---|---|
| 1 | Form Validation & Completeness | Incomplete applications cannot be submitted |
| 2 | Scoring Engine | Circumstance score, status flags and daily summary calculated automatically |
| 3 | Acceptance Workflow (DocuSign) | Pre-populated dual-signature acceptance with reminders and escalation |
| 4 | Website → System-of-Record Intake | Submissions become records automatically, with a reference number |
| 5 | AI-Assisted Anonymisation & Trustee Pack Preparation | Free-text narratives redacted with human review of low-confidence cases |
| 6 | Trustee Review Portal | One place for trustees to review anonymised cases and record verdicts |
| 7 | Duplicate-Grant Check (QuickBooks) | Prior grants flagged before assessment |

Plus the cross-cutting behaviour mandated by the Data Governance Framework, DPIA and RoPA:

- Automated retention and deletion by outcome and trigger date, across every system holding a copy.
- On-demand right-to-erasure handling with legal-hold carve-outs.
- Subject access request fulfilment.
- Retention/erasure evidence logging.
- A 30-minute walkthrough with Emily per automation (included in the build effort).

**Trustee portal navigation (Amendment A-02, APPROVED, WBS 6.1).** The app's navigation is
landing → overview/list (FR-034, WBS 6.2) → detail (FR-035, WBS 6.3), replacing a direct
list → detail flow. This is in scope under WBS 6.1's existing "app design" deliverable text and
needed no change order. **The landing screen's content stays explicitly not in scope of this
SDD.** No WBS 6 deliverable text (6.1–6.8) covered a statistics screen, so that content was routed
as a change order — `CO-001` (`contract/change-orders/CO-001.md`), **APPROVED 2026-08-24**,
creating **WBS 6.9** (`depends_on: 6.1`) under `feature:trustee-portal-landing-page`. CO-001
resolves the change-order decision and the reviewer's separate question about surfacing
`Round 4.pptx`'s funding-capacity figures as-is; it does not itself write the landing page's
FR/NFR text or a firm effort figure, which CO-001 defers to a follow-up plan-agent dispatch for
that feature. Until that dispatch runs, the landing screen remains a navigation shell with no
committed content in this SDD.

**Landing screen content (Amendment A-03, APPROVED 2026-08-25, WBS 6.9).** The follow-up dispatch
above has now run. The landing screen's statistics content is committed scope as FR-057 to
FR-063 (new subsection under §4.F) — NFR-027 was proposed alongside them but is withdrawn by
reviewer decision, see §5 — working from the two source decks per CO-001's authorised content
categories. **Hours for this content are not yet fixed:** the reviewer confirmed it is extra
scope beyond CO-001's original 5–8h ROM (§10, OQ-038) and a revised sizing pass is in progress
with commercial-agent. See the amendment block near the top of this document for the full
findings and Resolution.

**Application form field corrections (Amendment A-04, MERGED IN 2026-08-26, delivered
2026-08-17).** Seven corrections to the Application and Applicant tables so that every column
corresponds to a question the live WordPress form actually asks, in the shape it asks it — two
regression fixes, one further shape correction, two new columns, three column removals, and a
cross-cutting rule that option-list drift must surface as an exception rather than a guessed value.
Committed scope as FR-070 to FR-077 (§4.I), NFR-030 to NFR-032 (§5) and US-020 to US-023 (§6).
These were approved and delivered under a separate SDD and are adopted here on that approval; see
the Amendment A-04 block near the top of this document for provenance, the identifier remap and the
open commercial-scope flag. **Not in scope of that pass, and still open:** the seven remaining gaps
in `docs/development/revitalise-grant-automation-form-validation-spec.md` §9 — M-01 (condition
profile: ten functional areas against eight condition types) in particular is a larger disagreement
than anything the pass touched and needs its own decision.

### Out of Scope

Carried over from the source, unchanged:

- **Payment process automation** (company card, provider payments) — involves financial controls
  and provider agreements, not technology.
- **Impact reporting automation** — already handled by Ian's existing dashboard.
- **Grants management system evaluation or replacement** — a separate decision if Revitalise
  outgrows the platform.
- **Formal staff training programme** — each automation includes a 30-minute walkthrough only.
- **Historical data migration** beyond the current application round. Migration of the current
  round is scoped inside Automation #4 setup.
- **Power BI dashboards** — dropped in v0.5; a possible later enhancement, not this scope.
- **Full QuickBooks API integration** for duplicate checking — the fallback cross-reference
  approach is in scope; full API integration is a later enhancement.

Out of scope for **this document** specifically (deliberate boundary, not a gap):

- Technical architecture, data model, table schemas, flow internals, security-role configuration
  and deployment topology — these belong to the Technical Architecture Document produced by the
  architect-agent from `docs/Import/Revitalise-Solution-Architecture-v0.4.docx`.
- Release and operations procedure — covered by the ALM Runbook and Governance Runbook.

---

## 4. Functional Requirements

Requirements are written at business/functional level. Where a requirement names an external
system a business user interacts with (Teams, DocuSign, QuickBooks) that naming is retained from
the source because it is part of the agreed business process; no data model or automation internals
are specified here.

### A. Application form validation & completeness (Automation #1)

| ID | Requirement | Priority |
|---|---|---|
| FR-001 | The system SHALL prevent submission of a grant application WHEN any mandatory field (full name, date of birth, postcode, financial situation, preferred holiday dates, provider preference) is empty, SO THAT incomplete applications are never created and staff time is not spent chasing them. | High |
| FR-002 | The system SHALL display plain-English, field-specific guidance and validation messages WHEN an applicant leaves a mandatory field empty or enters a value that fails validation, SO THAT applicants can correct their own answers without contacting the charity. | High |
| FR-003 | The system SHALL present financial detail questions only WHEN an income band has been selected, and carer questions only WHEN the applicant has indicated they are travelling with a carer, SO THAT applicants are not asked questions irrelevant to their circumstances. ⚠️ **The carer half of this requirement is UNIMPLEMENTED and has no data destination — recorded by Amendment A-04, 2026-08-26.** FR-076 removed `rev_travellingwithcarer`, `rev_carername` and `rev_carersupport`, because the live WordPress form has never asked those questions and the three columns had been empty since they were created. Removing empty columns the form does not feed was the right call (D-5), but it leaves this requirement's carer clause with nothing to conditionally reveal and nowhere to store an answer. **Not silently dropped and not withdrawn:** the requirement stands, and closing it needs either a form change requested of Alex (which would return the three columns) or a reviewer decision to withdraw the carer clause. The income-band half is unaffected. | Medium |
| FR-004 | The system SHALL display a completion-progress indicator throughout the application, SO THAT applicants can see how much remains and are less likely to abandon partway. | Medium |
| FR-005 | The system SHALL allow an applicant to save a partially completed application and resume it later, SO THAT applicants who need help mid-application do not lose their answers. | Medium |
| FR-006 | The system SHALL present a summary of all answers with a per-section edit option before final submission, SO THAT applicants can correct mistakes before the application enters the process. | Medium |

### B. Intake into the system of record (Automation #4)

| ID | Requirement | Priority |
|---|---|---|
| FR-007 | The system SHALL create a grant application record automatically WHEN an applicant submits the online application form, SO THAT no manual export-and-import step is required and assessment can begin immediately. | High |
| FR-008 | The system SHALL assign every new application a unique reference in the format `REV-YYYY-NNN` and record its submission timestamp WHEN the application record is created, SO THAT each application can be identified unambiguously in correspondence, reporting and audit. | High |
| FR-009 | The system SHALL notify the process owner via Microsoft Teams with the applicant name and application reference WHEN a new application record is created, SO THAT new applications are picked up without anyone polling the website. | Medium |
| FR-010 | The system SHALL record the failure and alert the process owner WHEN an incoming submission cannot be turned into an application record, SO THAT no application is silently lost. | High |

### C. Scoring engine (Automation #2)

| ID | Requirement | Priority |
|---|---|---|
| FR-011 | The system SHALL calculate a circumstance score out of 60 from the applicant's wellbeing answers WHEN an application record is created, SO THAT scoring is consistent and no longer performed by hand. | High |
| FR-012 | The system SHALL invert the applicant's reported feeling answer so that a lower reported feeling produces a higher score, WHEN calculating the circumstance score, SO THAT the score reflects need rather than positivity. | High |
| FR-013 | The system SHALL convert each Likert wellbeing response to its configured point value (Strongly Disagree = 5, Disagree = 4, Neutral = 3, Agree = 2, Strongly Agree = 1) WHEN calculating the circumstance score, SO THAT the charity's agreed need criteria are applied identically to every application. ⚠️ **This wording is now known to be incomplete — see Amendment A-01 (PROPOSED) at the top of this document, and test-report D-009.** The agree/disagree labels are correct for only **three** of the ten wellbeing questions; the other seven use a frequency scale, and a sixth response ("Not sure", 0.5 points) is missing entirely. Left as originally approved pending plan-agent re-issue; replacement wording is proposed in A-01. | High |
| FR-014 | The system SHALL set the application status to Auto-pass, Borderline or Auto-reject by comparing the circumstance score against the configured knockout threshold and borderline band WHEN the score has been calculated, SO THAT staff attention goes only to the cases that need human judgement. | High |
| FR-015 | The system SHALL evaluate the applicant's financial answers against the configured income ceiling and record the outcome as a separate eligibility flag WHEN an application is scored, SO THAT applications outside the financial eligibility criteria are identified independently of the circumstance score. | High |
| FR-016 | The system SHALL exclude disability data, health-condition data and the free-text narrative from the circumstance score calculation, SO THAT special-category data does not influence an automated outcome. | High |
| FR-017 | The system SHALL allow the process owner to change the knockout threshold, the borderline band and the income ceiling without any change to the automation logic, SO THAT the board can adjust criteria without developer involvement. | High |
| FR-018 | The system SHALL allow the process owner to override the automatically assigned status on any application and SHALL record that an override was made, WHEN the process owner disagrees with the automated outcome, SO THAT a named human remains accountable for every outcome. | High |
| FR-019 | The system SHALL route every application with status Borderline to the process owner for manual review before it progresses, SO THAT marginal cases receive human judgement rather than an automated verdict. | High |
| FR-020 | The system SHALL remove applications with status Auto-reject from the active working list into a separate rejected list WHEN the status is set, SO THAT the active list shows only applications requiring action. | Medium |
| FR-021 | The system SHALL send the process owner a daily summary stating how many applications were scored, how many were auto-rejected and how many are borderline awaiting review, SO THAT the process owner has oversight without opening the system. | Medium |
| FR-022 | The system SHALL withhold a final automated outcome and route the application to the process owner WHEN any answer required by the scoring methodology is absent, SO THAT incomplete data cannot produce a spurious automated rejection. *(DERIVED — see Interpretations; behaviour to be confirmed under OQ-002.)* | High |

### D. Duplicate-grant check (Automation #7)

| ID | Requirement | Priority |
|---|---|---|
| FR-023 | The system SHALL check each new application against the charity's historical grant payment records in QuickBooks WHEN the application record is created, SO THAT previously funded applicants are identified before assessment rather than after. | Medium |
| FR-024 | The system SHALL flag the application as a possible duplicate and record the prior grant reference, date and amount WHEN a match is found against the applicant's identifying details, SO THAT staff can investigate before a second grant is awarded. | Medium |
| FR-025 | The system SHALL record "no prior grants found" against the application WHEN the check completes without a match, SO THAT the check is evidenced as having run. | Low |

### E. Anonymisation and trustee pack preparation (Automation #5)

| ID | Requirement | Priority |
|---|---|---|
| FR-026 | The system SHALL produce a redacted copy of each free-text narrative in which detected personal identifiers are replaced with category labels (`[NAME]`, `[FAMILY MEMBER]`, `[GP PRACTICE]`, `[ADDRESS]`, `[PHONE]`) WHEN an application becomes eligible for trustee review, SO THAT trustees can weigh a real case without learning whose it is. | High |
| FR-027 | The system SHALL replace specific ages with an age band and specific locations with a region in all trustee-visible content, SO THAT an applicant cannot be identified from quasi-identifiers left in the text. | High |
| FR-028 | The system SHALL retain region, preferred dates, circumstance score, holiday preferences and general condition information in trustee-visible content WHEN redacting, SO THAT trustees keep the information they need to reach a funding decision. | High |
| FR-029 | The system SHALL flag a redacted narrative for manual review and SHALL withhold it from trustees WHEN the redaction confidence falls below the configured threshold (initially 85%), SO THAT no unreviewed low-confidence redaction reaches the board. | High |
| FR-030 | The system SHALL allow the process owner to review, correct and release a flagged redaction WHEN a narrative has been flagged, SO THAT a human confirms every uncertain redaction before disclosure to trustees. | High |
| FR-031 | The system SHALL make the original unredacted narrative readable only to the administrator role and the service identity, SO THAT raw special-category free-text is not disclosed beyond those who need it. | High |
| FR-032 | The system SHALL generate a per-application anonymised document containing the redacted narrative, score breakdown, holiday details and staff recommendation, SO THAT trustees who cannot use the review portal are not excluded from the decision. ⚠️ **Field list aligned with FR-035's adopted wording — see Amendment A-02, Finding 1 (top of this document).** | Medium |
| FR-033 | The system SHALL allow trustee-pack preparation to be run on demand by the process owner and SHALL also run it on a schedule ahead of each board meeting, SO THAT the pack is ready without anyone remembering to start it. | Medium |

### F. Trustee review portal (Automation #6)

| ID | Requirement | Priority |
|---|---|---|
| FR-034 | The system SHALL present trustees with a sortable and filterable summary list of the applications under review showing circumstance score, region, preferred dates and status, SO THAT a trustee who prefers a data-only view can work entirely from one screen. | High |
| FR-035 | The system SHALL provide a per-application detail view showing the redacted narrative, the score breakdown, the type of break, the preferred dates, the break location, the total funding requested for the grant round (including any exceptional funding requested), the applicant-type context, the care-support context, and the staff recommendation, SO THAT trustees who prefer to read the case have the full anonymised picture. ⚠️ **Updated by Amendment A-02, APPROVED 2026-08-24** — against the sample trustee document at `docs/Import/3. Round 4 - Individual Applications.pdf`, and incorporating the reviewer's answers to OQ-031 (total funding requested, not itemised costs) and OQ-032 (applicant-type and care-support context both confirmed safe to show). Full field-by-field comparison, and the one item still pending (OQ-011), are in Amendment A-02, Finding 1 and Resolution, at the top of this document. | High |
| FR-036 | The system SHALL withhold applicant identifying information from every trustee-facing view, SO THAT trustee review is anonymous by design rather than by manual preparation. | High |
| FR-037 | The system SHALL allow a trustee to record a verdict of Approve, Defer or Reject with optional notes against each application under review, SO THAT decisions are captured in structured form during the meeting instead of by email afterwards. | High |
| FR-038 | The system SHALL restrict trustee access to the applications that are eligible for review in the current round, SO THAT trustees do not see cases outside their remit. | High |
| FR-039 | The system SHALL provide a print or offline export of the trustee views, SO THAT trustees who prefer to read away from a screen are not disadvantaged. ⚠️ **Confirmed by Amendment A-02, Finding 3 — the print path reuses FR-035's on-screen field list unchanged, so no separate WBS 6.5 content decision is needed.** | Medium |
| FR-040 | The system SHALL apply the recorded trustee verdicts to the corresponding grant records and initiate the acceptance workflow for approved applications WHEN the process owner confirms "Finalise decisions" after the board meeting, SO THAT the meeting's outcome is enacted in one controlled, auditable step. | High |
| FR-056 | The system SHALL present a landing screen when a trustee opens the app, from which the trustee navigates to the applications summary list (FR-034) and, from there, to an individual application's detail (FR-035), SO THAT trustees have a clear starting point instead of landing directly inside case data. ⚠️ **New, Amendment A-02, APPROVED 2026-08-24 (numbered out of sequence — added at the end of the FR list, not renumbered into section F, to avoid disturbing already-cited FR ids elsewhere in this document and in the test report).** The landing screen's content beyond this navigation shell is out of scope — see §3, `CO-001` and `feature:trustee-portal-landing-page` (WBS 6.9). | High |

### F+. Round-statistics landing screen (Automation #6 extension — WBS 6.9, `feature:trustee-portal-landing-page`)

⚠️ **New subsection, Amendment A-03, APPROVED 2026-08-25.** Fills the content FR-056 deliberately
left out. Numbered out of sequence for the same reason FR-056 was — continuing from the highest
existing FR id rather than disturbing FR-001–FR-055's citations elsewhere in this document and the
test report. See the Amendment A-03 block near the top of this document for sourcing, findings and
the reviewer's Resolution.

| ID | Requirement | Priority |
|---|---|---|
| FR-057 | The system SHALL present the landing screen's statistics scoped to the single grant round the signed-in trustee is currently authorised to review under FR-038, WHEN the trustee opens the landing screen, SO THAT the figures always match the round the trustee is about to work in without a manual round selection. ✅ **CONFIRMED, Amendment A-03, Resolution 2026-08-25** — reviewer's exact words: *"for now its one round at a time. Once a month."* Exactly one grant round is open for trustee review at a time, on a monthly cadence; no round-selector requirement is written because at most one round is ever reachable by a trustee at once, not only because no selectable "Round" entity exists in the data model (Finding 2). **This closes OQ-034 as N/A** — simultaneous multi-round trustee access does not occur. | Medium |
| FR-058 | The system SHALL present the current round's total applications received, the date the round opened, and the average applications received per day, SO THAT trustees see how the round is progressing before opening the applications list. *(Amendment A-03, source: both decks' slide 2.)* | Medium |
| FR-059 | The system SHALL present, for the current round, the count of applications in each exceptional-circumstance category, the total and percentage of applications citing any exceptional circumstance, and the average exceptional-funding amount requested, SO THAT trustees see the round's need profile before reviewing individual cases. *(Amendment A-03, source: `Round 3 Stats.pptx` slide 2. No minimum-cell-size rule applies — see NFR-027, withdrawn by reviewer decision, Resolution 2026-08-25.)* | Medium |
| FR-060 | The system SHALL present, for the current round, a breakdown by type of break showing the number of applications, the average total holiday cost, the average grant amount requested (including exceptional funding), and the percentage of total cost represented by the requested grant amount, with a total row across all types, SO THAT trustees see what the round's applications are asking for and at what cost. *(Amendment A-03, source: `Round 3 Stats.pptx` slide 2. This is a round-wide average by break type, distinct from FR-035's per-application total-funding figure — OQ-031's resolution against itemised per-application costs does not need to be re-applied here.)* | Medium |
| FR-061 | The system SHALL present, for the current round, the applicant gender, ethnic-group, age-range and applicant-type (disabled person / carer applying on behalf of a disabled person / carer applying for themselves) distributions as percentages, SO THAT trustees can see who applied in this round before opening individual cases. *(Amendment A-03, source: `Round 3 Stats.pptx` slide 3/4 charts.)* ⚠️ **REWORDED, Amendment A-03 Resolution (continued), 2026-08-25 — the benchmark-comparison clause is withdrawn by reviewer decision, not silently dropped.** The original wording additionally required the gender, ethnic-group and age-range distributions to be *"shown alongside the corresponding published UK cared-for-disabled-adults-and-carers benchmark percentages, SO THAT trustees can see how representative the round's applicants are of the population the charity serves"*. No such dataset was ever sourced or owned, which architect-agent's TAD raised at TAD stage and which was already recorded here as OQ-037. Reviewer's exact words: *"there is no benchmark dataset. This is personal knowledge of the trustees. So only showing the representation of applications is enough."* Trustees hold the population context personally, so it is not restated on screen. **This closes OQ-037.** The applicant distributions themselves are unchanged and remain in scope. ⚠️ **Not touched by this amendment:** the ethnic-group figure has no source data at all, because the charity has never collected the field — a separate, still-open gap raised independently by architect-agent's TAD at [§3.4](docs/architecture/trustee-portal-visual-refresh-architecture.md#L363) and risk [A-R24](docs/architecture/trustee-portal-visual-refresh-architecture.md#L924), and gated by OQ-027, not by OQ-037. | Medium |
| FR-062 | The system SHALL present, for the current round, the distribution of applicant responses to the three "last year" wellbeing questions, the distribution of life-satisfaction scores (0–10), and the round's headline circumstance statistics (the proportion of carers providing high-hours care, the proportion reporting low life satisfaction, and the proportion unable to take a break when needed), SO THAT trustees see the round's overall level of need. *(Amendment A-03, source: `Round 3 Stats.pptx` slide 5 and its two charts. Excludes the scoring-methodology explainer repeated on both decks' final slide — see Amendment A-03's "Source documents" note.)* | Medium |
| FR-063 | The system SHALL present the round's financial position — the amount committed or spent to date, the number of people and individuals supported, and, where the round's applications include a group or multi-person grant, the number of people reached through it — alongside the charity's current grant-giving capacity, suggested maximum spend for the round, monthly disbursement amount, and remaining legacy-fund split, sourced from a finance-maintained record rather than derived from Application/Grant/Payment data, SO THAT trustees have the financial picture behind the applications they are reviewing. *(Amendment A-03, source: `Round 4.pptx` slide 2. ⚠️ **PARTIALLY RESOLVED, Resolution 2026-08-25** — reviewer's exact words: "at the moment everything is manual. Maybe have this land on the finance accessable tables? Or an extra table that finance fills in these details." Confirmed manual/finance-maintained at business level; which of the reviewer's two mechanisms — extending an existing finance-accessible table, or a new table finance fills in — is an architect-agent decision at TAD stage, not chosen here. The capacity, suggested-maximum-spend and legacy-split figures also describe the charity's overall fund position rather than an event scoped to this round specifically — see Finding 3.)* | Medium |

### G. Grant acceptance (Automation #3)

| ID | Requirement | Priority |
|---|---|---|
| FR-041 | The system SHALL create an acceptance document pre-populated with the applicant's name, grant amount, holiday provider, dates and conditions and route it for electronic signature via DocuSign WHEN an application status is set to Approved, SO THAT staff no longer build and email acceptance forms by hand. | High |
| FR-042 | The system SHALL route the acceptance document for two signatures in sequence — the applicant first, then the referee or GP — SO THAT the dual-signature requirement is satisfied without manual coordination. | High |
| FR-043 | The system SHALL send automatic signature reminders three days and seven days after issue WHEN an acceptance document remains unsigned, SO THAT the average five-day return time reduces without staff chasing. | High |
| FR-044 | The system SHALL notify the process owner with the applicant's details WHEN an acceptance document remains unsigned fourteen days after issue, SO THAT stalled acceptances are escalated rather than forgotten. | High |
| FR-045 | The system SHALL set the grant status to "Acceptance Signed" and link the completed signed document to the grant record WHEN both signatures have been received, SO THAT the signed evidence is filed automatically and remains auditable. | High |
| FR-046 | The system SHALL support a manual print-sign-scan acceptance route recorded against the grant record WHEN an applicant cannot sign electronically, SO THAT non-digital applicants are not excluded from receiving a grant. | Medium |
| FR-047 | The system SHALL issue acceptance documents for a batch of approved applications in a single run WHEN multiple grants are approved at one board meeting, SO THAT a full board round can be issued without per-application handling. | Medium |

### H. Retention, erasure and information rights (cross-cutting)

| ID | Requirement | Priority |
|---|---|---|
| FR-048 | The system SHALL delete the full application record and all records dependent on it automatically WHEN the retention period for its outcome has elapsed — six years from final payment date for a paid grant, twelve months from decision date for a rejected application, six months from last contact for a withdrawn or incomplete application — SO THAT personal data is not kept longer than Revitalise's published schedule allows. | High |
| FR-049 | The system SHALL delete or purge every linked copy held outside the system of record, including the signed acceptance document and the signature envelope, WHEN the parent record is deleted, SO THAT no copy of a deleted record survives. | High |
| FR-050 | The system SHALL retain the financial record required by the charity's finance policy WHEN the associated personal record is otherwise deleted, SO THAT the Charities Act 2011 financial-record duty is met. | High |
| FR-051 | The system SHALL locate and delete, on demand, all data held about a named individual — including any referee, helper, group member or emergency contact captured with their application — WHEN an erasure request is received and no legal hold applies, SO THAT the right to erasure under UK GDPR Article 17 can be honoured. | High |
| FR-052 | The system SHALL report to the requester which data cannot yet be deleted and why WHEN a legal-hold carve-out applies to an erasure request, SO THAT the response matches the published Privacy Notice. | High |
| FR-053 | The system SHALL produce a complete extract of the data held about a named individual WHEN a subject access request is received, SO THAT the charity can answer the request within the statutory period. | High |
| FR-054 | The system SHALL log every retention deletion run and every erasure action with the record reference, data type, date and rule applied, and SHALL hold no personal data in that log, SO THAT the charity can evidence compliance without creating a further copy of personal data. | High |
| FR-055 | The system SHALL retain irreversibly anonymised statistical records that carry no identifiers and cannot be linked back to a person indefinitely, SO THAT outcome reporting survives deletion of the underlying personal data. | Medium |

### I. Application form field corrections (cross-cutting — Amendment A-04, WBS 0.4 / 0.5 / 4.2 / 4.3)

⚠️ **New subsection, Amendment A-04, MERGED IN 2026-08-26.** These eight requirements were approved
on 2026-08-16 in a separate SDD and delivered to DEV on 2026-08-17. They are carried here verbatim
under new identifiers — see the Amendment A-04 block near the top of this document for the remap and
for why the merge was necessary. **Nothing in this subsection is new or newly approved.**

#### Exceptional circumstance (W1)

| ID | Requirement | Priority |
|---|---|---|
| FR-070 | The system SHALL record the applicant's exceptional circumstance as exactly one of **Palliative care**, **Carer breakdown or urgent need**, **Severe financial hardship**, or **Other (please specify)** WHEN an application carrying an exceptional funding request is submitted, SO THAT the reason for an above-normal request is on the record rather than only the fact of one. *(Amendment A-04; was FR-056 in the retired SDD.)* | High |
| FR-071 | The system SHALL retain the applicant's own wording of the circumstance WHEN the selected value is "Other (please specify)", SO THAT circumstances outside the four categories are not lost. *(Amendment A-04; was FR-057.)* | High |

#### Employment status (W2)

| ID | Requirement | Priority |
|---|---|---|
| FR-072 | The system SHALL record the applicant's employment status as exactly one of **Yes, full-time**, **Yes, part-time**, **No, unable to work due to disability/health/caring responsibilities**, **No, retired**, or **No, other reason** WHEN the applicant answers the employment question, SO THAT an inability to work caused by disability or caring is distinguishable from retirement and from choice, which is the distinction a needs-based grant decision turns on. *(Amendment A-04; was FR-058.)* | High |

> The retired SDD carried a **FR-059** for legacy Yes/No handling. It was **withdrawn at that
> document's revision 1.1** — D-3 established that the live form already sends the five values, so
> there was no legacy value stream to handle, and the general case is covered by FR-077, which is
> strictly stronger. **No identifier is allocated for it here**, because a withdrawn requirement has
> no force and allocating a number to it would put a fourth meaning into circulation.

#### Preferred contact method (W3)

| ID | Requirement | Priority |
|---|---|---|
| FR-073 | The system SHALL record every contact method the applicant selects — **Email**, **Phone**, **Post**, one or more — WHEN an application is submitted, SO THAT correspondence and grant offers reach applicants by a route they can actually use. *(Amendment A-04; was FR-060.)* | High |

#### Consent explanation (W4)

| ID | Requirement | Priority |
|---|---|---|
| FR-074 | The system SHALL retain the explanation an applicant gives alongside the applicant-consent declaration WHEN one is given, SO THAT the basis on which a third party is acting for the applicant is on the record and not only in the mind of whoever read the submission. *(Amendment A-04; was FR-061 — note that FR-061 in this document is A-03's applicant demographic distributions, an entirely different requirement.)* | Medium |

#### Hours of care provided (W5)

| ID | Requirement | Priority |
|---|---|---|
| FR-075 | The system SHALL record the hours of care the applicant provides each week as exactly one of the five bands the form offers, WHEN the applicant answers that question, SO THAT the caring load is captured in the form it is actually asked in rather than discarded for being unstorable. *(Amendment A-04; was FR-062. The five bands are at D-4; bands four and five overlap on the live form itself and the option set stores them as sent — see V-10 in the A-04 block.)* | High |

#### Removal of columns with no source (W6)

| ID | Requirement | Priority |
|---|---|---|
| FR-076 | The system SHALL NOT hold columns for whether a carer travels with the applicant, that carer's name, or the support that carer provides, UNTIL the application form asks those questions, SO THAT the schema does not assert it holds information it can never receive and staff do not read an empty field as a "no". *(Amendment A-04; was FR-063. Asserted by `src/tests/solutions/IntakeContract.Tests.ps1`. See the A-04 block on the resulting FR-003 conflict.)* | Medium |

#### Option-list drift (W7)

| ID | Requirement | Priority |
|---|---|---|
| FR-077 | The system SHALL leave a column empty and record the mismatch against the application WHEN an incoming answer does not match any value in that column's option list, and SHALL NOT map it to a nearest value, SO THAT divergence between the website form and the system of record surfaces as a visible exception rather than as quietly wrong data. *(Amendment A-04; was FR-064. Asserted by `src/tests/solutions/IntakeContract.Tests.ps1`.)* | High |

FR-077 is the requirement the whole correction pass argues for. Every finding in it existed for
weeks without anything noticing, because nothing was watching for it: the form changed to five
employment options at some point and the repository never found out. FR-077 is what would have told
us.

**Matching is normalised, not literal.** The comparison SHALL trim surrounding whitespace, collapse
internal runs of whitespace, and treat hyphen, en-dash and em-dash as equivalent before matching.
The care-hours bands are the live example — the source documents have already written them as
`10 – 19 hours` and `10- 19 hours`, and a literal comparison would reject every submission while
reporting a drift that does not exist. Case is also normalised. Nothing else is: a value that
differs by a word is a real mismatch and must be reported as one.

---

## 5. Non-Functional Requirements

| ID | Requirement | Category |
|---|---|---|
| NFR-001 | Special-category fields (health and disability condition profiles, "other condition" free-text, benefit status, ethnic group where captured) SHALL be readable only by the administrator role and the service identity. | Security |
| NFR-002 | Bank account and payment data SHALL be readable only by the finance role; the administrator role SHALL have no access to it (separation of duties). | Security |
| NFR-003 | Applicant, helper and support-recipient identifying attributes SHALL never be delivered to a trustee-facing view — the control SHALL be enforced by the platform, not by manual preparation. | Security |
| NFR-004 | Multi-factor authentication SHALL be enforced for every staff, trustee and service-identity sign-in. | Security |
| NFR-005 | Access to each environment SHALL be gated by membership of a named security group before any role permission applies. | Security |
| NFR-006 | Every connection to an external system SHALL be owned by a non-personal service identity, so access survives staff changes and is governed centrally. | Security |
| NFR-007 | Only the approved connector set SHALL be permitted; all other connectors SHALL be blocked in both the development and production environments. | Security |
| NFR-008 | The application-intake endpoint SHALL accept submissions only from the authenticated charity website. | Security |
| NFR-009 | 100% of processing, storage and backup SHALL remain in the UK region across every component, including the redaction service, signature service and finance system. Zero transfers outside the UK. Verified at environment setup. | Compliance |
| NFR-010 | Retention SHALL be enforced automatically by status and trigger date (6 years / 12 months / 6 months per FR-048), with the enforcement run occurring at least monthly; irreversibly anonymised statistics are retained indefinitely. No deletion SHALL depend on a person remembering to act. | Compliance |
| NFR-011 | The backup and point-in-time restore window SHALL sit within the retention period of the records it covers, and all backups SHALL remain in the UK region, so a deleted record cannot survive indefinitely inside a backup. | Compliance |
| NFR-012 | No personal data SHALL be written to operational logs; operational logging is limited to run status, error message and record reference. | Compliance |
| NFR-013 | Only the fields needed to assess, decide, pay and report on a grant SHALL be collected (data minimisation, UK GDPR Article 5(1)(c)). | Compliance |
| NFR-014 | Every create, update and delete on a record holding personal data SHALL be recorded with timestamp (UTC), actor, action, affected record identifier, and before/after values. | Audit |
| NFR-015 | Access to the trustee review view SHALL be logged, recording which user opened it and when. | Audit |
| NFR-016 | The retention and erasure evidence log SHALL be retained as a durable record and SHALL contain no personal data. | Audit |
| NFR-017 | Automated redaction with a confidence below 85% SHALL be routed to human review; the threshold SHALL be adjustable after launch without redesign. | Compliance |
| NFR-018 | 100% of Borderline scoring outcomes and 100% of low-confidence redactions SHALL receive human review before they progress or are disclosed. | Compliance |
| NFR-019 | The process owner SHALL be able to change scoring thresholds, the income ceiling, the redaction confidence threshold, document templates and field mappings without developer involvement and without changing automation logic. | Maintainability |
| NFR-020 | Applicant-facing guidance, labels and error messages SHALL be written for a reading age of approximately 12. | Usability |
| NFR-021 | The solution SHALL support approximately 200 applications per year with headroom to at least 250 per year, and a cumulative grant history of at least 300 records, without redesign. | Scalability |
| NFR-022 | **Performance / response-time thresholds — NOT SPECIFIED in any source document.** No page-load, flow-completion or intake-latency target is stated. See OQ-020. | Performance |
| NFR-023 | **Availability / uptime target — NOT SPECIFIED in any source document.** See OQ-021. | Availability |
| NFR-024 | **Accessibility standard — NOT NAMED in any source document.** No WCAG level or equivalent is committed to, despite an applicant population of disabled people and unpaid carers with low average literacy. See OQ-022. | Accessibility |
| NFR-025 | **Subject access and erasure response-time target — NOT SPECIFIED as an internal SLA.** The capability is designed (FR-051 to FR-053) but no turnaround commitment is recorded. See OQ-023. | Compliance |
| NFR-026 | The trustee review portal SHALL render at the full width of the browser viewport rather than the platform's default constrained canvas, and SHALL be visually consistent with Revitalise's public brand (typography, colour, tone — `revitalise.org.uk`) SO THAT the app reads as a Revitalise product to the trustees who use it. *(Added by Amendment A-02, 2026-08-24, at the reviewer's request. The design system, component library and CSS approach that deliver this are a technology decision for architect-agent at TAD stage — see OQ-033 — not specified here.)* | Usability |
| ~~NFR-027~~ | ~~Any round-statistic category presented on the landing screen (FR-059–FR-062) with fewer than a configured minimum number of applications SHALL be suppressed or grouped into a combined "Other/small categories" figure before display, SO THAT a rare category (e.g., an exceptional-circumstance type with a handful of applicants) cannot be used to narrow an anonymous aggregate toward an identifiable individual.~~ ⚠️ **WITHDRAWN, Amendment A-03 Resolution, 2026-08-25 — explicit reviewer risk-acceptance decision, not a silent removal.** Proposed by plan-agent (Finding 4) in response to a small-cell disclosure risk observed in the source data; the reviewer overrode it. Reviewer's exact words: *"no minimum group size. The whole point of the code app is for trustees to review items and the column security profile scrubs aways personal information."* The reviewer's own control is the app's existing field-level security profile (NFR-001/NFR-003), not aggregate suppression. Left struck through rather than deleted so the proposal and the reason it was not adopted are both on the record — see §7.1 and OQ-035 for the same decision. | Compliance |
| NFR-030 | Every column added or reshaped by the form-field correction pass SHALL be classified against UK GDPR Art. 6 / Art. 9 in §7.1a **before** it is built. Classification determines what must be *recorded*; it does not by itself determine what must be *secured* — securing is decided per column against necessity, under the rule at §7.1a. *(Amendment A-04; was NFR-026 in the retired SDD — note that NFR-026 in this document is A-02's full-width brand rendering.)* | Compliance |
| NFR-031 | Where an Art. 9 special-category column is deliberately released to trustees, the necessity argument SHALL be recorded in this SDD, in the column's own schema description, and in the DPIA and RoPA, and the free-text elaboration behind that column SHALL remain secured. Per **D-6** this applies to `rev_exceptionalcircumstance`. *(Amendment A-04; was NFR-027 — note that NFR-027 in this document is A-03's withdrawn minimum-cell-size rule. This requirement is in force; that one is not.)* | Compliance |
| NFR-032 | No option-set value SHALL be renumbered or removed once any application record references it. All option-set trimming and renumbering in the correction pass SHALL complete before the first real application is created. **D-2 confirmed this was satisfiable on 2026-08-16 and the pass completed on 2026-08-17.** *(Amendment A-04; was NFR-028.)* | Compliance |

> NFR-022 to NFR-025 are recorded as explicit gaps rather than invented thresholds. They must be
> answered before the test-agent can write verifiable test cases for those categories. NFR-026 is
> not a gap — it is specified at business level, with the technical means deferred to
> architect-agent, which is the ordinary SDD/TAD boundary rather than a missing requirement.
> NFR-027 is withdrawn, not a gap — the reviewer accepted the disclosure risk it was written to
> control (Amendment A-03 Resolution, 2026-08-25) rather than leaving a threshold unset.
> NFR-030 to NFR-032 arrive with Amendment A-04 and are in force. The retired SDD also carried an
> accessibility NFR, **withdrawn at its revision 1.2** — D-3 and D-4 established that the correction
> pass required no change to the public form, so it had no subject. It is not carried here. If
> OQ-046 surfaces a form change, an accessibility requirement returns with it, and NFR-024's
> unanswered standard (OQ-022) is the one it would have to be written against.

---

## 6. User Stories

### US-001: Submit a complete application first time
**As an** applicant (or a helper acting for one), **I want** the form to tell me what is missing as I
go, **so that** I can submit a complete application without a chain of follow-up emails.

**Acceptance Criteria:**
- Given a mandatory field is empty, when I try to submit, then submission is blocked and the field is identified. → FR-001
- Given I have left a mandatory field empty, when the message appears, then it is written in plain English and explains why the answer is needed. → FR-002
- Given I have not selected an income band, when I view the form, then the financial detail questions are not shown. → FR-003
- Given I am partway through, when I look at the form, then I can see how much of it remains. → FR-004
- Given I have answered every question, when I reach the end, then I see a summary of my answers and can edit any section before submitting. → FR-006

### US-002: Pause and come back
**As an** applicant who needs help from someone else to finish, **I want** to save my progress,
**so that** I do not have to start again.

**Acceptance Criteria:**
- Given I have partly completed the form, when I choose to save and continue later, then my answers are preserved and I can resume them. → FR-005
- Given I have resumed a saved application, when I complete it, then I see the same pre-submission summary and edit option as a single-sitting applicant. → FR-006

### US-003: Accept a grant without a printer
**As a** successful applicant, **I want** to sign my acceptance electronically, **so that** my grant
is confirmed quickly and I am not held up by post.

**Acceptance Criteria:**
- Given my application has been approved, when the decision is finalised, then I receive an acceptance document already filled in with my name, amount, provider and dates. → FR-041
- Given I have signed, when my signature is recorded, then the document is routed to my referee or GP for the second signature. → FR-042
- Given I have not signed, when three days and then seven days have passed, then I receive a reminder. → FR-043
- Given both signatures are complete, when the last one is received, then my grant record shows "Acceptance Signed" and the signed document is attached to it. → FR-045
- Given I cannot sign electronically, when I ask for a paper route, then a print-sign-scan acceptance can be recorded against my grant. → FR-046

### US-004: Know what is held about me and have it removed
**As an** applicant, **I want** to ask what data Revitalise holds about me and to have it deleted,
**so that** I stay in control of my personal and health information.

**Acceptance Criteria:**
- Given I make a subject access request, when the process owner actions it, then a complete extract of the data held about me can be produced. → FR-053
- Given I request erasure and no legal hold applies, when the request is actioned, then my data is deleted from the system of record and from every linked copy. → FR-051, FR-049
- Given part of my data is held under the six-year financial-record duty, when I request erasure, then I am told which data cannot yet be deleted and why. → FR-052, FR-050
- Given my record reaches the end of its retention period, when the retention run executes, then it is deleted without anyone requesting it. → FR-048

### US-005: Applications arrive by themselves
**As** Emily, the process owner, **I want** submissions to become records automatically,
**so that** I stop exporting spreadsheets and applications stop waiting in a queue.

**Acceptance Criteria:**
- Given an applicant submits the form, when the submission is received, then an application record exists without any manual step. → FR-007
- Given a new record is created, when I look at it, then it carries a unique `REV-YYYY-NNN` reference and its submission timestamp. → FR-008
- Given a new record is created, when it lands, then I receive a Teams notification with the applicant name and reference. → FR-009
- Given a submission fails to create a record, when the failure occurs, then it is recorded and I am alerted. → FR-010

### US-006: The score is calculated, but the judgement stays mine
**As** Emily, **I want** the circumstance score and status calculated automatically against criteria
I control, **so that** I only spend time on the cases that need a human.

**Acceptance Criteria:**
- Given a new application record, when it is created, then a circumstance score out of 60 is calculated from the wellbeing answers. → FR-011
- Given the applicant reported a low feeling score, when the score is calculated, then that answer contributes more points, not fewer. → FR-012
- Given a Likert answer of "Strongly Disagree", when the score is calculated, then it contributes the configured maximum points for that question. → FR-013 ⚠️ *Incomplete — "Strongly Disagree" is the position-1 answer on only three of the ten questions. Replacement criterion proposed in Amendment A-01.*
- Given the score is calculated, when it is compared to the threshold, then the application is flagged Auto-pass, Borderline or Auto-reject. → FR-014
- Given the applicant's finances exceed the income ceiling, when the application is scored, then a separate income eligibility flag is set. → FR-015
- Given an application contains health-condition data and a free-text narrative, when the score is calculated, then neither influences the score. → FR-016
- Given the board changes the cut-off, when I update the threshold, then the change takes effect without a developer editing anything. → FR-017
- Given I disagree with an automated status, when I override it, then the new status applies and the override is recorded. → FR-018
- Given an application is Borderline, when it is flagged, then it waits for my review before progressing. → FR-019
- Given applications were auto-rejected, when I open my active list, then they are not in it. → FR-020
- Given a day's applications have been scored, when the daily summary arrives, then it states how many were scored, auto-rejected and are awaiting my review. → FR-021
- Given a scored answer is missing, when the application is processed, then no final automated outcome is set and the case comes to me. → FR-022

### US-007: I stop anonymising by hand, but I keep the last word
**As** Emily, **I want** narratives redacted automatically with anything uncertain flagged to me,
**so that** I save three to four hours per board cycle without risking a missed name reaching a trustee.

**Acceptance Criteria:**
- Given an application becomes eligible for trustee review, when redaction runs, then personal identifiers in the free-text narrative are replaced with category labels. → FR-026
- Given a narrative mentions a specific age or place, when redaction runs, then they are generalised to an age band and a region. → FR-027
- Given redaction has run, when a trustee reads the case, then region, dates, score, holiday preferences and general condition information are still present. → FR-028
- Given redaction confidence is below the configured threshold, when the narrative is processed, then it is flagged to me and withheld from trustees. → FR-029
- Given a narrative is flagged, when I review and release it, then trustees can see it. → FR-030
- Given I need the original text, when I open the record, then I can read the unredacted narrative and no one outside the administrator role can. → FR-031
- Given the board meeting is approaching, when the schedule fires or I trigger it, then pack preparation runs. → FR-033

### US-008: Enact the board's decisions in one step
**As** Emily, **I want** to turn the meeting's verdicts into actions with one confirmation,
**so that** I stop collating decisions from emails and re-keying them.

**Acceptance Criteria:**
- Given trustees recorded verdicts during the meeting, when I confirm "Finalise decisions", then the verdicts are applied to the grant records. → FR-037, FR-040
- Given approved applications exist, when I finalise decisions, then acceptance documents are issued for them. → FR-040, FR-041
- Given fifteen grants were approved at one meeting, when I finalise decisions, then all fifteen are issued in the same run. → FR-047

### US-009: Chasing signatures is not my job
**As** Emily, **I want** reminders and escalation handled automatically, **so that** acceptances stop
sitting unsigned for weeks.

**Acceptance Criteria:**
- Given an acceptance is unsigned, when three and seven days pass, then reminders are sent without my involvement. → FR-043
- Given an acceptance is still unsigned after fourteen days, when the escalation triggers, then I am notified with the applicant's details. → FR-044
- Given both signatures arrive, when they complete, then the status and the signed document are filed automatically. → FR-045

### US-010: Catch a repeat grant before it is paid
**As** Emily, **I want** prior grants flagged automatically, **so that** duplicate awards are caught
as volumes grow beyond what I can remember.

**Acceptance Criteria:**
- Given a new application, when it is created, then it is checked against historical grant payments. → FR-023
- Given a prior grant is found, when the check completes, then the application is flagged as a possible duplicate with the prior grant's reference, date and amount. → FR-024
- Given no prior grant is found, when the check completes, then "no prior grants found" is recorded on the application. → FR-025

### US-011: Retention happens without me
**As** Emily, **I want** records deleted on schedule automatically, **so that** the charity's retention
promise does not depend on me remembering.

**Acceptance Criteria:**
- Given a rejected application reaches twelve months from its decision date, when the retention run executes, then the full record is deleted. → FR-048
- Given a grant record is deleted, when deletion completes, then the signed document and signature envelope copies are also removed. → FR-049
- Given a record is deleted, when the run completes, then the deletion is logged with the record reference, data type, date and rule, and the log holds no personal data. → FR-054
- Given anonymised statistics exist, when personal records are deleted, then the statistics remain available for reporting. → FR-055

### US-012: Review real cases without learning who they are
**As a** trustee, **I want** to read the anonymised case and record my verdict in one place,
**so that** I can decide properly without a static Word pack and without seeing personal identities.

**Acceptance Criteria:**
- Given I open the review view, when it loads, then I see the applications under review with score, region, dates and status, and can sort and filter them. → FR-034
- Given I select an application, when the detail opens, then I see the redacted narrative, score breakdown, holiday details and staff recommendation. → FR-035
- Given I am a trustee, when any view loads, then no applicant, helper or support-recipient identifying information is present anywhere in it. → FR-036, FR-031
- Given I have read a case, when I decide, then I can record Approve, Defer or Reject with optional notes. → FR-037
- Given applications outside the current round exist, when I open the review view, then they are not available to me. → FR-038
- Given I open the app, when it loads, then I land on a landing screen from which I reach the summary list and, from there, an individual case. → FR-056 *(Amendment A-02)*

### US-013: A stripped, data-only view
**As** Kevin, a trustee who works from the numbers, **I want** scores, region, dates and status only,
**so that** I can compare cases at a glance without reading narratives.

**Acceptance Criteria:**
- Given I prefer a data-only view, when I open the summary list, then I can review score, region, dates and status without opening a narrative. → FR-034
- Given I am working from the summary list, when I sort or filter it, then the ordering and filtering apply to all applications under review. → FR-034
- Given I use only the summary view, when I reach a decision, then I can record my verdict from there. → FR-037
- Given I want a copy to work from offline, when I export, then I get the same stripped content with no identifying information. → FR-039, FR-036

### US-014: An offline fallback so no trustee is excluded
**As a** trustee who cannot or will not use the portal, **I want** an anonymised document pack,
**so that** I can still take part in the decision.

**Acceptance Criteria:**
- Given pack preparation has run, when I request the fallback, then I receive a per-application anonymised document with the redacted narrative, score breakdown, holiday details and staff recommendation. → FR-032
- Given I have the document pack, when I read it, then it contains no applicant identifying information. → FR-032, FR-027
- Given I prefer to print from the portal, when I use the print option, then the same anonymised content is produced. → FR-039

### US-015: Finance sees payments, and nothing it does not need
**As** finance staff recording disbursements, **I want** access limited to bank and payment data,
**so that** I can do my job without handling applicants' health information.

**Acceptance Criteria:**
- Given I hold the finance role, when I open the solution, then I can reach bank account and payment records. → NFR-002
- Given I hold the finance role, when I open any application record, then the applicant's unredacted health narrative is not readable by me. → FR-031, NFR-001
- Given an application was flagged as a possible duplicate, when I prepare a disbursement, then the flag and the prior grant details are visible on the record. → FR-024
- Given a grant record reaches the end of its retention period, when deletion runs, then the financial record required by the finance policy is retained. → FR-050

### US-016: See how this round is going before opening a case
**As a** trustee, **I want** to see this round's headline statistics when I open the portal,
**so that** I understand the round's shape — how many applications, what kind of need, how much
funding — before I start reviewing individual cases. *(New, Amendment A-03, APPROVED
2026-08-25, WBS 6.9.)*

**Acceptance Criteria:**
- Given I have access to exactly one open round, when the landing screen loads, then it shows that round's statistics without asking me to select one. → FR-057
- Given I am on the landing screen, when it loads, then I see the round's total applications received and the average received per day. → FR-058
- Given I am on the landing screen, when I view it, then I see the round's exceptional-circumstance mix and the average exceptional funding requested. → FR-059
- Given I am on the landing screen, when I view the break-type breakdown, then I see the count, average cost and average grant requested for each type of break, with a total. → FR-060
- Given I am on the landing screen, when I view the demographic section, then I see the round's gender, ethnicity, age and applicant-type distributions. → FR-061 *(the "compared against the UK benchmark where one exists" clause was removed with FR-061's benchmark comparison — Amendment A-03 Resolution (continued), 2026-08-25)*
- Given I am on the landing screen, when I view the circumstance section, then I see the wellbeing and life-satisfaction distributions and the round's headline circumstance statistics. → FR-062
- Given I am on the landing screen, when I view the funding section, then I see the round's financial position and the charity's grant-giving capacity. → FR-063

### US-020: The reason for an exceptional request survives to the decision
*(Amendment A-04, approved 2026-08-16, delivered 2026-08-17. Was US-016 in the retired SDD — note
that US-016 in this document is A-03's round-statistics story.)*

**As a** trustee, **I want** to see which category of exceptional circumstance an applicant claims,
**so that** I can weigh a palliative-care request differently from a financial-hardship one instead
of being asked to approve an above-normal amount with no reason attached to it.

**Acceptance Criteria:**
- Given an application submitted with "Palliative care" selected, when the application record is created, then the exceptional circumstance column holds the value "Palliative care". → FR-070
- Given an application submitted with "Other (please specify)" selected and free text supplied, when the record is created, then the selection is stored and the applicant's own wording is stored in the secured `rev_otherexceptionalcircumstance`. → FR-071
- Given an application where the applicant made no exceptional funding request, when the record is created, then the exceptional circumstance column is empty and is distinguishable from any selected value. → FR-070
- Given a trustee opens the application, when the record renders, then the exceptional circumstance **category is visible** and the free-text elaboration behind it is **not** (D-6, §7.1a). → NFR-031

### US-021: An applicant who cannot work because of their disability is not recorded as simply "not working"
*(Amendment A-04. Was US-017.)*

**As a** process owner assessing need, **I want** the employment answer to distinguish inability to
work from retirement and from choice, **so that** an applicant whose disability prevents them
working is not assessed identically to one who has retired comfortably.

**Acceptance Criteria:**
- Given an applicant selects "No, unable to work due to disability/health/caring responsibilities", when the record is created, then that exact value is stored. → FR-072
- Given a submission arrives carrying a value outside the five, when the record is created, then the employment status is empty and the mismatch is recorded against the application. → FR-077
- Given the employment status is empty for either reason, when a staff member views the record, then it reads as unanswered and not as "No". → FR-072
- Given a trustee opens the application, when the record renders, then the employment status is not shown to them, in any surface (D-1). → NFR-001 *(the retired SDD traced this to its option-set renumbering rule, which is a different subject — see the correction note in Appendix A)*

### US-022: An applicant who asked to be contacted by post is contacted by post
*(Amendment A-04. Was US-018.)*

**As an** applicant without reliable email, **I want** the charity to hold the fact that I asked to
be contacted by post, **so that** the grant offer arrives somewhere I can read it.

**Acceptance Criteria:**
- Given an applicant ticks Post only, when the record is created, then the preferred contact method holds Post and the applicant record has no email address, and neither is treated as an error. → FR-073
- Given an applicant ticks both Email and Post, when the record is created, then both values are stored. → FR-073

### US-023: The caring load is on the record
*(Amendment A-04. Was US-019.)*

**As a** process owner, **I want** the hours of care an applicant provides each week to be stored,
**so that** the thing the charity exists to relieve is visible in the record rather than only in
the applicant's narrative.

**Acceptance Criteria:**
- Given an applicant selects "20 - 34 hours", when the record is created, then that band is stored. → FR-075
- Given an applicant selects a band, when the record is viewed, then the band label is shown, not a number. → FR-075

---

## 7. Compliance & Regulatory Considerations

### 7.0 Status of the underlying compliance artefacts — read this first

| Artefact | Version | Status | Consequence |
|---|---|---|---|
| Data Protection Impact Assessment | v0.1, 15 Jul 2026 | **Concept draft — for DPO review. NOT signed off.** Outcome and residual-risk acceptance left open; the sign-off table (DPO, controller, processor) is empty. | UK GDPR Art. 35 requires the DPIA to be completed before go-live. Its five closing actions (A1–A5) are unclosed. |
| Record of Processing Activities | v0.1, 15 Jul 2026 | **Concept draft — for DPO review. NOT signed off.** | The Art. 30 register is not yet the charity's own record; content must be transferred into Revitalise's RoPA template and confirmed. |
| Data Governance Framework | v0.2, 15 Jul 2026 | Draft | Retention and erasure policy is written but awaits the same DPO confirmations. |
| Security Model | v0.1, 15 Jul 2026 | Draft — "DPO sign-off is the gate on this model" | The trustee field-level-security control is explicitly gated on DPO sign-off. |
| Privacy Notice | updated 20 Feb 2026 | Published (Revitalise's own) | Source of the lawful bases and retention periods used throughout. |

Revitalise is the **data controller**. Argelis Consultancy is the **processor** and builder, acting
on Revitalise's instruction. AI Builder (redaction), DocuSign (signing) and QuickBooks Online
(financial record) act as sub-processors, all within the UK. The named service identity
`svc-grantautomation` owns the external connections; it is not a personal login.

### 7.1 Data classification (satisfies C-DOM-001 at plan level)

| Tier | Examples in this solution | Data subjects | Handling |
|---|---|---|---|
| **Special category (UK GDPR Art. 9)** | Applicant and support-recipient condition profiles; "other condition" free-text; health/disability free-text in the narrative; benefit status; ethnic group where captured | Applicants; cared-for / support-recipients | Highest restriction. Administrator role and service identity only. Never shown to trustees. Free-text redacted before trustee review. |
| **Personal (UK GDPR Art. 6)** | Name, address, postcode, email, phone, date of birth, bank details; helper, referee, group-member and emergency-contact identity | Applicants; helpers; referees; group members; emergency contacts | Restricted. Identity attributes hidden from trustees; bank details behind the finance role only. |
| **Pseudonymised** | Pseudonymised reference (e.g. `REV-A-00001`), age range, location area, costs, scores, redacted narrative | Applicants | Still personal data. Visible to trustees. Follows the parent record's retention clock. |
| **Anonymised** | Snapshot statistics: age range, location area, condition areas, outcome, amount — no identifiers, never linked back | None | Not personal data. May be kept indefinitely. |
| **Round-level aggregate** *(new, Amendment A-03, APPROVED 2026-08-25, WBS 6.9)* | Landing-screen statistics (FR-057–FR-063): application/exceptional-circumstance/break-type counts and percentages, cost and funding averages, demographic distribution percentages, wellbeing and score-distribution counts — computed **live** across the *current* round's Application and Review records; financial/capacity figures come from a separate finance-maintained record, not derived from Application/Grant/Payment data (OQ-036) | None directly identified | Materially lower restriction than the Pseudonymised detail screen above — no single application's data is shown. **Not the same tier as Anonymised above**, which covers only retained post-deletion snapshots (FR-055): these aggregates are computed live over current special-category and personal source data, so a small category count could in principle narrow toward an individual (§7's Amendment A-03, Finding 4). ⚠️ **No minimum-cell-size control is applied.** Plan-agent proposed one (NFR-027); the reviewer explicitly overrode it (Amendment A-03 Resolution, 2026-08-25 — *"no minimum group size. The whole point of the code app is for trustees to review items and the column security profile scrubs aways personal information"*), naming the app's existing field-level security profile (NFR-001/NFR-003) as the control for personal-data exposure instead. Recorded here as a risk-acceptance decision, not a silent gap — see OQ-035. |
| **Operational (non-personal)** | Flow error log, run history — run status, error messages, record references only | None | No personal data. Short operational retention, separate from the personal-data schedule. |

Trustees and finance/admin staff are themselves data subjects: tenant account identity, the verdict
a trustee records, and the audit trail of staff actions.

### 7.1a Per-column classification for the form field corrections (Amendment A-04, satisfies C-DOM-001 and NFR-030)

⚠️ **New subsection, Amendment A-04, MERGED IN 2026-08-26.** Carried verbatim from the retired SDD's
§7.1 and §7.4. Five of the seven work items are shape corrections to data already classified above
and already covered by §7.2's lawful bases; they need no new analysis and get none. **Two change a
classification**, and are the reason the original SDD escalated to strategic tier.

| Column | Before the pass | After the pass | Secured? |
|---|---|---|---|
| `rev_application.rev_exceptionalcircumstance` | Personal (Art. 6) — a Boolean "is there an exceptional circumstance" discloses nothing in itself | **Special category (Art. 9)** — "Palliative care" is health data about the applicant or someone they care for | **No — D-6.** Trustee-visible on necessity, see the securing rule below. Its free-text elaborations stay secured |
| Employment status (`rev_currentlyworking` → `rev_employmentstatus`) | Personal (Art. 6) — a Boolean "are you working" is ordinary financial circumstance, and its schema description said so | **Special category (Art. 9)** — "No, unable to work due to disability/health/caring responsibilities" is a disclosure of disability or health status | **Yes — D-1** |
| `rev_applicant.rev_preferredcontactmethod` (new) | — | Personal (Art. 6). A contact preference. Not special category, and it should not be secured — the people who need to know how to write to an applicant are exactly the people who correspond with them | No |
| `rev_application.rev_consentexplanation` (new) | — | **Special category (Art. 9)** — an explanation of why someone else is completing a form for an applicant will routinely name a health reason, on the same reasoning already applied to `rev_caresupportdescription` and `rev_otherconditionraw` | **Yes, from creation** — free text |
| `rev_application.rev_carehoursperweek` (reshaped) | Personal (Art. 6), not secured | Unchanged — a band of hours is a circumstance fact and exactly the fact trustees need | No |
| `rev_travellingwithcarer`, `rev_carername`, `rev_carersupport` (removed) | Personal / special category, two of the three secured | **Removed** | n/a |

The two classification changes are consequences of the reviewer's findings, not choices the design
makes. A Boolean that says "yes, something exceptional" is not health data. A value that says
"palliative care" is. The same column, reshaped, crosses the line.

**Lawful basis (satisfies C-DOM-002).** No new lawful basis is required. Every column sits inside a
grouping already covered by §7.2, taken from Revitalise's Privacy Notice of 20 February 2026:

| Column | Art. 6 basis | Art. 9 condition | Grouping in §7.2 |
|---|---|---|---|
| `rev_exceptionalcircumstance` | Necessary to assess and administer the grant | Art. 9(2)(b) social protection; 9(2)(h) health and social care | Application |
| Employment status | Necessary to assess and administer the grant | Art. 9(2)(b); 9(2)(h) | Application |
| `rev_preferredcontactmethod` | Necessary to administer the grant | n/a | Applicant (identity, contact) |
| `rev_consentexplanation` | Necessary to administer the application | Art. 9(2)(b); 9(2)(h) | Application / Helper acting for an applicant |
| `rev_carehoursperweek` | Necessary to assess the grant | n/a | Application |

**Data minimisation moves in both directions here, and that is deliberate.** *Added:* three answers
the form already collects and the applicant already gives — storing an answer already being collected
is not an increase in processing, and discarding it while continuing to ask for it is the worse
position, because the applicant has already borne the intrusion and the charity gets none of the
benefit. *Removed:* three columns holding nothing, two of them secured — a small minimisation gain
and a larger honesty gain, since `rev_carername` appeared on the form, carried a
`REV_TrusteeRestricted` entry, and would always have been empty. *Tightened:* one column moves behind
field-level security that was not behind it before (D-1).

#### The securing rule this solution actually implements — and why D-6 follows it

An earlier revision of the retired SDD asserted that securing `rev_exceptionalcircumstance` was "the
consistent position". **That was wrong, and the correction matters because the architecture carries
this rationale forward.** Reading `REV_TrusteeRestricted`'s real `AttributeName` entries — as opposed
to the columns merely mentioned in its comments — the implemented rule is:

> **Categorical answers are trustee-visible. Identity and free text are not.**

The evidence covers thirty-eight secured columns against every categorical answer in the schema:

| Trustee-visible today (not secured) | Secured today |
|---|---|
| `rev_conditionprofile`, `rev_supportrecipientconditionprofile` — **both special category** | `rev_otherconditionraw`, `rev_supportrecipientotherconditionraw` — the free text behind them |
| `rev_needscaresupportpersonally`, `rev_careprovidedtype`, `rev_carehoursperweek` | `rev_caresupportdescription`, `rev_othercareprovidedtype`, `rev_careprovidedexample` |
| `rev_significantcarecosts`, `rev_savingsover6000`, `rev_incomeband` | `rev_carecostsexplanation`, `rev_unabletofundexplanation` |
| `rev_exceptionalfundingrequested`, `rev_breaklocation` | `rev_exceptionalfundingdetail`, `rev_otherexceptionalcircumstance` |

The pattern holds in every row: trustees are given the *category* of a person's disability, care
need, financial position and requested break, and none of the *words* in which that person described
it, and none of their identity. `rev_conditionprofile` is the closest analogue to
`rev_exceptionalcircumstance` — Art. 9 health data, held as a category, trustee-visible by design,
with its "other" free text secured.

**D-6 puts `rev_exceptionalcircumstance` where that rule already puts it.** It is not an exception
carved out for convenience; securing it would have been the exception. The necessity argument is the
one the solution already accepted for `rev_breaklocation` — a trustee cannot judge a request for a
break without knowing where the break is, and cannot judge a request for **exceptional** funding
without knowing what the exceptional circumstance is. Two obligations attach, both in NFR-031:
`rev_otherexceptionalcircumstance` and `rev_exceptionalfundingdetail` **stay secured** (the rule only
works because both halves hold), and the DPIA and RoPA must record that trustees process this Art. 9
category — an amendment to an existing entry, since both already record it for the condition
profiles, but not automatic. That is **OQ-048**.

**The employment column is the genuine exception, and D-1 keeps it secured.** Under the rule above a
category would be visible, and its financial neighbours (`rev_incomeband`, `rev_savingsover6000`,
`rev_significantcarecosts`) all are. It differs because one of its five values — "No, unable to work
due to disability/health/caring responsibilities" — is a direct disability disclosure rather than a
financial fact, and nothing in the trustee's task requires it. The nearest precedent is
`rev_receivesbenefits`, secured for the same kind of reason. **This asymmetry is deliberate and is
written into the column's own schema description so the next reader does not "fix" it.**

**Consequences for the DPO decisions already open.** OQ-004 (is column security an acceptable trustee
control?) now covers one more column, not two — D-6 reduces this pass's reliance on that answer.
OQ-006 (six-year retention of health free-text) now covers `rev_consentexplanation`. Neither is
re-opened; both have their surface changed, and the DPO should be told rather than discover it later.

### 7.2 Lawful basis per data grouping (satisfies C-DOM-002)

The lawful bases are **Revitalise's own**, taken from its Privacy Notice (20 Feb 2026). This SDD
records them; it does not set them.

| Data grouping / entity | Personal data — Art. 6 basis | Special category — Art. 9 condition | Notes |
|---|---|---|---|
| Applicant (identity, contact, DOB) | Art. 6 — necessary to assess and administer the grant | n/a | Per Privacy Notice |
| Application (wellbeing and financial answers, circumstance score, narrative) | Art. 6 — necessary to assess and administer the grant | Art. 9(2)(b) social protection; Art. 9(2)(h) health and social care | Health free-text and disability data are processed to assess eligibility and need only; they do not feed the automated score |
| Support-recipient / cared-for person (identity where given, condition profile) | Art. 6 — necessary to assess the grant | Art. 9(2)(b) and 9(2)(h) | Condition profile visible to trustees; identity is not |
| Helper acting for an applicant (name, email, phone) | Art. 6 — necessary to administer the application | n/a | No special-category data |
| Referees, group members, emergency contacts | Art. 6 — necessary to administer and verify the application | n/a | In scope of erasure requests (FR-051) |
| Review (trustee verdict, notes, trustee identity) | Art. 6 — necessary to decide which grants to fund | n/a | Trustee identity is staff/officer processing |
| Grant (award, provider, dates, conditions, signed acceptance) | Art. 6 — necessary to administer and evidence the grant; retention under the Charities Act 2011 duty | n/a | Signed PDF retained with the record |
| Bank Account, Payment | Art. 6 — necessary to pay the grant and meet financial-record duties | n/a | Finance role only; administrator role has no access |
| Provider | **Not classified in any source document** | — | See OQ-026. Likely organisation data with named contacts; classification and basis must be settled at TAD stage |
| Anonymised Statistic snapshot | Not personal data — outside Art. 6 | n/a | No identifiers, not linkable |
| ~~UK demographic benchmark reference data~~ *(added by Amendment A-03, behind FR-061)* | ~~Not personal data — published third-party population statistics, not about any Revitalise data subject~~ | n/a | ⚠️ **WITHDRAWN, Amendment A-03 Resolution (continued), 2026-08-25.** FR-061's benchmark comparison is withdrawn — reviewer: *"there is no benchmark dataset. This is personal knowledge of the trustees."* No such dataset ever existed or enters the system, so there is nothing here to classify. Struck through rather than deleted so the row and the reason it went are both on the record. OQ-037 closed. |
| Finance-maintained round-financial record *(new, Amendment A-03, behind FR-063)* | Not personal data — aggregate charity-level figures (amount spent, capacity, legacy split); no applicant identity | n/a | Confirmed manual/finance-maintained, not derived from Application/Grant/Payment data (Resolution 2026-08-25). Storage mechanism — extend an existing finance table vs. a new one — is an architect-agent decision at TAD stage (OQ-036) |
| Error Log (operational) | Not personal data — outside Art. 6 | n/a | Run status, error message, record reference only |

### 7.3 UK GDPR obligations and how the design addresses them

| Article | Obligation | Position in this design |
|---|---|---|
| **Art. 5(1)(a)** lawfulness, fairness, transparency | Processing must be fair and explained | Applicants informed via the Privacy Notice (20 Feb 2026); no separate consultation planned |
| **Art. 5(1)(b)** purpose limitation | Use only for stated purposes | Data used only to assess, decide, pay and report; anonymised statistics carry no identifiers and cannot be linked back |
| **Art. 5(1)(c)** data minimisation | Collect only what is necessary | Only fields needed to assess and pay a grant are collected (NFR-013). Health free-text and disability data do not feed the automated score (FR-016) |
| **Art. 5(1)(e)** storage limitation | Keep no longer than necessary | Automated retention by status and trigger date (FR-048, NFR-010). ⚠️ Six-year retention of the health free-text is the open DPO decision OQ-006 |
| **Art. 5(1)(f)** integrity and confidentiality | Appropriate security | Least privilege, field-level restriction of identity columns, separation of duties on bank data, UK residency, connector restriction (NFR-001 to NFR-009) |
| **Art. 5(2)** accountability | Demonstrate compliance | Native field-change auditing of every create/update/delete (NFR-014); app-access logging (NFR-015); retention/erasure evidence log (FR-054, NFR-016) |
| **Art. 6** lawful basis | Documented per entity | §7.2 above |
| **Art. 9** special-category condition | Art. 9 condition required | Art. 9(2)(b) social protection and Art. 9(2)(h) health and social care, per the Privacy Notice |
| **Art. 15** right of access | SAR fulfilment | Complete extract producible for a named individual (FR-053). ⚠️ No internal response-time SLA recorded — OQ-023 |
| **Art. 17** right to erasure | Erasure path with carve-outs | On-demand erasure across the system of record and every linked copy including referees, helpers, group members and emergency contacts (FR-051); legal-hold carve-out disclosed to the requester (FR-052) |
| **Art. 30** records of processing | Art. 30(1) controller record and Art. 30(2) processor record | Both drafted in the RoPA v0.1 — **concept status, not confirmed**; published DPO contact details still outstanding (OQ-009) |
| **Art. 32** security of processing | Technical and organisational measures | Least privilege; field-level column restriction; separation of duties; MFA and Conditional Access; UK residency; connector policy; native auditing; automated retention and deletion |
| **Art. 35** DPIA | Required for high-risk processing | DPIA exists at v0.1 concept status. It is required here because the solution processes special-category health data about people in vulnerable circumstances, at scale, and uses automated processing to screen applications |

### 7.4 Data (Use and Access) Act 2025 — automated decision-making

The DUAA 2025 has been in force since 5 February 2026 and bears directly on this design.

The scoring flow calculates the circumstance score from the wellbeing answers, applies the knockout
threshold and income ceiling the process owner controls, and sets the status to auto-pass,
borderline or auto-reject. Disability data, health-condition data and the free-text narrative do
**not** feed the score. Emily does not re-score by hand; she reviews the borderline cases the flow
flags, can adjust the threshold, and can override any outcome. Trustees make the funding decision on
eligible applications.

**The open question is whether automatic rejection at the threshold, with that oversight and
override, meets Revitalise's automated-decision position under the DUAA 2025.** This is a DPO
decision (OQ-005). If a stronger form of human review is required before any rejection stands, the
design can route auto-reject outcomes through the process owner instead of closing them
automatically — a configuration change within the current design, not a rebuild. This SDD's
FR-014, FR-018, FR-019 and FR-022 are written so that either position can be adopted without
changing the requirement set.

### 7.5 Charities Act 2011 — retention duty

The six-year retention period on successful grants, including the health free-text, follows the
**Charities Act 2011 financial-record duty** as stated in Revitalise's Privacy Notice. This creates
a direct tension with Article 5(1)(c) minimisation, because the health free-text is retained for the
full six years alongside the financial record. The design allows the special-category free-text to
be redacted earlier if the DPO prefers tighter minimisation — a configuration change, not a rebuild.
That choice is DPO decision OQ-006. The financial record itself is retained under the finance policy
even where the personal record is otherwise deleted (FR-050), and erasure requests are answered with
an explicit statement of what is held under legal hold (FR-052).

### 7.6 Retention schedule (as adopted)

| Data / outcome | Trigger | Retention | Then |
|---|---|---|---|
| Successful grant — full record including health free-text | Status = Grant Paid, from final payment date | 6 years | Delete full record |
| Unsuccessful application | Status = Rejected, from decision date | 12 months | Delete full record |
| Withdrawn / incomplete | Status = Withdrawn / Incomplete, from last contact | 6 months | Delete full record |
| Monitoring & evaluation (pseudonymised) | Follows parent grant record | Same as record | Delete with record |
| Signed acceptance PDF | Attached to grant record | 6 years (with record) | Delete with record |
| Financial record (name, amount, date) | Status = Grant Paid | 6 years | Per finance policy |
| Irreversibly anonymised statistics | No identifiers; not linkable | Indefinite | Retain |
| Operational error log (non-personal) | Run completion | Short operational retention | Delete |

### 7.7 Risks to individuals (adopted from DPIA §6–§7)

| # | Risk to individuals | Inherent | Residual after designed controls |
|---|---|---|---|
| R1 | A trustee identifies an applicant from data that should be redacted (field-level security gap or incomplete redaction) | High | Low |
| R2 | Special-category health data exposed to someone without a need to see it (role misconfiguration) | High | Low |
| R3 | An applicant is wrongly rejected by the automated score without meaningful human review | High | **Medium — pending DPO confirmation (OQ-005)** |
| R4 | Health free-text kept longer than necessary on granted records (6-year retention) | Medium | **Medium — DPO decision open (OQ-006)** |
| R5 | Bank or payment details accessed by someone outside the finance role | Medium | Low |
| R6 | Data processed or stored outside the UK, breaching the residency commitment | Medium | Low |
| R7 | An erasure request is not honoured across every system holding a copy | Medium | Low |
| R8 | The service account is compromised, exposing the whole dataset through its broad access | Medium | Low |
| R9 | A leaver keeps access after their role ends | Medium | Low |

**Two risks remain at Medium and both are waiting on the DPO, not on the build.** R3 and R4 are the
gate-relevant compliance risks for this feature.

### 7.8 The three open DPO decisions — gate-relevant

These are DPIA §9 actions A1–A3, repeated identically in the Security Model §9, the Data Governance
Framework §8 and the RoPA §9. All four documents state that build must not proceed on the current
basis until they are recorded.

| Decision | What is being asked | Effect if answered differently |
|---|---|---|
| **A1 / OQ-004** | Confirm that field-level (column) security is an acceptable trustee control **in place of** the manual, single-key-holder anonymisation the documented process currently mandates | The automated control is stronger but *different*. If physical separation is required instead, the fallback is a separate trustee-facing store populated only with permitted fields and kept in sync — more to maintain, and a change the architect must design |
| **A2 / OQ-005** | Confirm that automatic rejection at the threshold, with the process owner's oversight and override, satisfies Revitalise's automated-decision position under the DUAA 2025 | If stronger human review is required, auto-reject outcomes route through the process owner rather than closing automatically — a configuration change, but it changes the process and the test set |
| **A3 / OQ-006** | Confirm that six-year retention of the health free-text on granted records is preferred over earlier minimisation | If earlier minimisation is preferred, the free-text is redacted before the six-year point — a configuration change, but it changes the retention requirement and its verification |

Two further DPIA closing actions are open: **A4** — confirm expected application volume and the
role-review cadence (process owner; OQ-007, OQ-008); and **A5** — verify UK residency and backup
arrangements at environment setup (builder / Wanstor; OQ-018, OQ-019).

### 7.9 Universal controls checklist (`skills/compliance-checklist.md` §1)

| Control | Status at plan stage |
|---|---|
| 1.1 Personal data identified and classified | ✅ §7.1 — four tiers plus operational; Provider entity unclassified (OQ-026) |
| 1.1 Lawful basis documented | ✅ §7.2 per entity |
| 1.1 Data minimisation | ✅ NFR-013, FR-016 |
| 1.1 Retention defined per entity; automated deletion | ✅ §7.6, FR-048, NFR-010. ⚠️ health free-text period is OQ-006 |
| 1.1 Personal data not written to logs | ✅ NFR-012 |
| 1.1 Encryption in transit / at rest | ➡️ Architecture-level; to be evidenced in the TAD |
| 1.1 SAR path exists | ✅ FR-053. ⚠️ no response-time SLA (OQ-023) |
| 1.1 Right-to-erasure path exists | ✅ FR-051, FR-052 |
| 1.1 Privacy impact assessed | ⚠️ DPIA exists at **concept draft** status — not signed off |
| 1.2 CRUD on sensitive entities logged | ✅ NFR-014 |
| 1.2 Log record content (timestamp, actor, action, entity, before/after) | ✅ NFR-014 |
| 1.2 Tamper-evident / append-only audit log | ➡️ Architecture-level (C-DOM-012, architect scope) |
| 1.2 Audit retention meets the longer of regulation or policy | ➡️ Architecture-level (C-DOM-013, architect scope) |
| 1.3 Least privilege | ✅ NFR-001 to NFR-003; three roles only |
| 1.3 Role assignments documented and reviewed | ⚠️ Documented; review cadence is **TBC** (OQ-008) |
| 1.3 Privileged actions require elevated authorisation | ➡️ Architecture-level (C-DOM-021, architect scope) |
| 1.3 MFA for privileged access | ✅ NFR-004; scoped Conditional Access exception for the service identity |
| 1.3 Session timeout | ➡️ Architecture-level; not stated in any source |
| 1.4 Change management via pipeline | ➡️ ALM Runbook (out of scope for this SDD) |
| 1.5 Dependency and supply chain | ➡️ Architecture / build stage |

> `knowledge/domain/compliance-requirements.md` is an unpopulated template in this repository, so no
> project-specific domain controls could be applied on top of the universal set. The compliance
> content above is drawn entirely from the source documents. See Adoption Report open items.

---

## 8. Assumptions & Dependencies

### Licensing and platform

1. Revitalise has, or will procure, an M365 Business Premium subscription.
2. Because the agreed data model is Dataverse (a premium data source), every person who uses an app
   over the custom tables needs a per-user premium entitlement: the maker/service account, plus a
   seat for Emily. Trustees are billed pay-as-you-go per active user per round.
3. The service account additionally needs a premium automation entitlement for the standalone
   scheduled and webhook automations (website intake, DocuSign, QuickBooks, retention helper) that
   run outside the app context.
4. Power BI Pro is **not** required — the trustee portal is a Dataverse app, not a Power BI report.
5. Automated redaction credits are expected to be covered by the credits bundled with each premium
   seat, **to be confirmed** — and confirmed before the 1 November 2026 seeded-credit change.
6. Recurring licence cost is roughly £750–1,000/year at list pricing, or about £370–500/year at
   nonprofit pricing. All licences are Revitalise's; none are carried by Argelis. Nonprofit
   eligibility (via TechSoup or a Microsoft partner) and the current M365 tier are to be confirmed
   before build. Figures were verified against Microsoft sources on 14 July 2026 and should be
   re-verified before procurement.
7. DocuSign is procured separately by Revitalise (from ~£8/user/month; standard plan sufficient)
   and must be in place before the acceptance workflow goes live.
8. Standard connectors (SharePoint, Outlook, Teams, HTTP, DocuSign, QuickBooks Online) carry no
   additional cost.

### External systems and third parties

9. The website form plugin exposes a webhook, a REST API, or structured email. Gravity Forms — the
   likely plugin — provides a REST API v2 and a Webhooks add-on, so no migration is needed. **If a
   different plugin without any of these is in use, migration adds 4–8 hours.**
10. Alex (website designer) is available to build the form to the supplied field-by-field
    specification and to implement the intake integration. Emily is to arrange the introduction.
11. The existing Canva acceptance form is available as the template to replicate.
12. QuickBooks Online is the edition in use and grant payments carry a searchable applicant
    identifier. Not yet confirmed — the design leads with the lower-effort cross-reference fallback
    for exactly this reason.
13. **WBS 0.3 — the service account and its scoped Conditional Access exception — is outstanding and
    currently waiting on Wanstor, Revitalise's IT provider.** This is the one dependency that is
    already late and it blocks the automations that run unattended. Wanstor has no access to grant
    data by design.

### Governance and people

14. **DPO sign-off on the three decisions in §7.8 is a precondition for build on the current design
    basis.** All four governance documents state this independently.
15. The DPIA and RoPA must be completed and signed by Revitalise as controller; Argelis's drafts are
    a processor's proposal, not the charity's record.
16. Emily is confirmed as process owner and the named DPO is current — to be confirmed before
    sign-off. A second processor (Jan) is under consideration and not yet assigned; a second staff
    seat would be needed if he also processes applications.
17. The scoring methodology and the anonymisation rules are confirmed by Emily before build begins.
18. The board decides the cut-off score and income ceiling. The design is configurable, so these can
    be set later without rework.
19. **Trustee adoption is a change-management risk, not a technical one.** Some trustees may resist
    moving from email attachments to a portal; the source expects at least one round of trustee
    feedback after the initial demo, and reconciling different trustees' expectations takes time.
    The offline document fallback (FR-032, FR-039) exists so that no trustee is excluded if adoption
    is partial.
20. Build effort assumes an **experienced Power Platform consultant**. A developer new to the
    platform should add 25–30%.
21. Build effort includes requirements clarification with Emily, build, client walkthrough, feedback
    processing, rework, and testing with real application data.
22. Annual savings projections assume ~200 grants/year. The current run rate (68 grants in ~4 months)
    suggests this is conservative.

### Companion artefacts already produced (context, not adopted into this SDD)

23. `docs/Import/Revitalise-Solution-Architecture-v0.4.docx` — feeds the architect-agent intake that
    runs after this SDD is approved.
24. `docs/Import/Revitalise-ALM-Runbook-v0.1.docx` — release and promotion procedure.
25. `docs/Import/Revitalise-Governance-Runbook-v0.1.docx` — role handover, review cadence,
    joiner-and-leaver procedure, operational failure monitoring.
26. `docs/Import/Revitalise-Security-Model-v0.1.docx` (WBS 0.5), `Revitalise-Data-Governance-Framework-v0.2.docx`,
    `Revitalise-DPIA-v0.1.docx` and `Revitalise-RoPA-v0.1.docx` (WBS 0.7) — the compliance set §7 draws on.
27. `Revitalise-WBS-Grant-Automation-v0.4.xlsx` — task-level breakdown with low/high hour estimates,
    dependencies and phasing. Referenced by the source but **not present in `docs/Import/`**; it is
    the basis of the §10 estimate and should be supplied.
28. `Grant Application Data Model v0.2` and Revitalise's Privacy Notice (20 February 2026) are
    referenced throughout the compliance set but are not in the repository.

---

## 9. Open Questions

Thirty open items were carried out of the source set. The volume is itself a signal: this design is
well documented but not yet decided, and six of these items sit with people outside the delivery
team.

| # | Question | Owner | Due |
|---|---|---|---|
| OQ-001 | Where should the knockout cut-off score sit, and how wide is the borderline band Emily reviews by hand? | Board / Emily | Before Automation #2 build |
| | ⚠️ **STILL OPEN.** Amendment A-01 does **not** resolve this, despite being commissioned as though it would — `Book(Sheet1).csv` holds scores and answers but no accept/reject outcomes, so no cut-off can be inferred from it. This is a board decision. **What did change:** the reachable floor of a fully answered application dropped from **10 to 5** (see A-01), so thresholds at or below 5 are now reachable where they were not. | | |
| OQ-002 | Confirm the exact scoring methodology: the feeling-scale inversion, the Likert point mapping, and the required behaviour when a scored answer is missing (see FR-022) | Emily | Before Automation #2 build |
| | ✅ **RESOLVED BY EVIDENCE — see Amendment A-01 (PROPOSED)** at the top of this document. 25 real hand-scored applications reproduce exactly under the recorded methodology, asserted permanently in `src/tests/solutions/ScoringInvariants.Tests.ps1`. Two corrections came with it: the ten wellbeing questions use **two** response scales, not one, and **"Not sure"** is a valid answer worth 0.5 points. Formal closure awaits plan-agent re-issue of FR-013. | | |
| OQ-003 | What is the income ceiling value, and does an income-only failure reject outright or flag for review? | Board / Emily | Before Automation #2 build |
| OQ-004 | **DPO decision (DPIA A1):** is field-level column security an acceptable trustee control in place of the manual, single-key-holder anonymisation? | DPO | **Before build starts** |
| OQ-005 | **DPO decision (DPIA A2):** does automatic rejection at the threshold, with oversight and override, satisfy Revitalise's automated-decision position under the DUAA 2025? | DPO | **Before build starts** |
| OQ-006 | **DPO decision (DPIA A3):** is six-year retention of the health free-text preferred over earlier minimisation? | DPO | **Before build starts** |
| OQ-007 | Confirm the expected number of applications per round and per year, so the scale of processing is on record (DPIA §2.2 TBC) | Emily | Before DPIA sign-off |
| OQ-008 | Confirm the role-membership review cadence — quarterly, or at the start of each panel round? | Emily / DPO | Before DPIA sign-off |
| OQ-009 | Confirm the published DPO contact details for the RoPA | Revitalise | Before RoPA finalisation |
| OQ-010 | Confirm the named DPO is current, that Emily is the accepted process owner, and whether a second processor (Jan) is assigned | Revitalise | Before sign-off |
| OQ-011 | Finalise the anonymisation rules: exactly which fields are stripped, which are generalised (age → band, location → region), and what stays | Emily / DPO | Before Automation #5 build |
| | **New evidence, Amendment A-02:** the sample trustee PDF and the Dataverse schema show at least two more free-text columns carrying the same class of content as the narrative — `rev_unabletofundexplanation` and `rev_exceptionalfundingdetail`/`rev_otherexceptionalcircumstance` — neither currently in the `rev_narrativeraw`/`rev_narrativeredacted` redaction pair. Recommend Automation #5's redaction scope explicitly cover them before build. | | |
| OQ-012 | Is the print-and-post route sufficient for applicants who cannot sign digitally, and who records the paper acceptance? | Emily | Before Automation #3 build |
| OQ-013 | Will all trustees move to the portal, or do some need the document pack for the first few cycles? | Emily / trustees | Before Automation #6 build |
| OQ-014 | Confirm the website form plugin (Gravity Forms assumed) and which integration method it exposes — webhook, REST pull, or structured email | Alex / Emily | Before Automation #4 build |
| OQ-015 | Confirm the QuickBooks edition (Online vs Desktop) and whether grant payment records carry a searchable applicant email or name | Revitalise finance | Before Automation #7 build |
| OQ-016 | Do TRIP (legacy) or Donorfy records also need to be checked for prior grants? | Emily | Before Automation #7 build |
| OQ-017 | Confirm redaction credit coverage under the bundled per-seat credits, nonprofit licensing eligibility, and the current M365 tier — before the 1 Nov 2026 seeded-credit change | Revitalise | Before build |
| OQ-018 | **WBS 0.3 — service account and scoped Conditional Access exception, outstanding with Wanstor.** When will it be delivered? | Wanstor | **Blocking; already outstanding** |
| OQ-019 | Does Revitalise run a third-party M365 backup tool, or rely on native platform backup alone? (DPIA A5) | Revitalise / Wanstor | At environment setup |
| OQ-020 | What performance / response-time thresholds apply? None are stated anywhere in the source set (NFR-022) | Emily / architect | Before test design |
| OQ-021 | What availability or uptime target applies, and are there periods (board cycle, application round) where downtime is unacceptable? (NFR-023) | Emily | Before test design |
| OQ-022 | **Which accessibility standard applies?** No standard is named in any source, despite an applicant population of disabled people and unpaid carers with a ~age-12 average reading level. WCAG 2.2 AA would be the conventional answer (NFR-024) | Revitalise / Emily | Before Automation #1 build |
| OQ-023 | What internal turnaround target applies to subject access and erasure requests? (NFR-025) | DPO / Emily | Before go-live |
| OQ-024 | Have trustees agreed to use the portal, and who owns that conversation? | Emily | Before Automation #6 build |
| OQ-025 | Is a second staff premium seat needed for Jan if he also processes applications? | Revitalise | Before procurement |
| OQ-026 | How is the Provider entity classified, and what is its lawful basis? No source document covers it (§7.2) | DPO / architect | At TAD stage |
| OQ-027 | Is ethnic group actually captured? Every source qualifies it as "where captured" — if it is not collected, the Art. 9 surface narrows | Emily / DPO | Before DPIA sign-off |
| OQ-028 | Confirm that no historical data migration beyond the current application round is required | Emily | Before Automation #4 build |
| OQ-029 | The project's own domain knowledge files (`knowledge/domain/overview.md`, `regulations.md`, `glossary.md`, `business-rules.md`) are unpopulated templates. Who populates them, and when? Until then every downstream agent works from the source documents alone | Lead / domain owner | Before architecture |
| OQ-030 | The DPIA outcome and residual-risk acceptance are not recorded and the sign-off table is empty. When will the DPIA be formally concluded? | DPO / Revitalise | **Before go-live (Art. 35)** |
| OQ-031 | Should the itemised holiday cost breakdown (accommodation/activity, travel, other) reach the trustee view, or is the total sufficient? *(Amendment A-02, WBS 6.3)* | Emily / trustees | Before WBS 6.3 rework |
| | ✅ **RESOLVED 2026-08-24.** Reviewer: *"Yes, safe to show. It's a total requested funding for that grant round."* No itemisation — FR-035 shows one total-funding-requested figure (including exceptional funding), not accommodation/travel/other broken out. | | |
| OQ-032 | Should care-support context (type of care, hours/week, description) reach the trustee view as circumstance evidence — and how should it be classified in §7.1, since no row there names it today? *(Amendment A-02, WBS 6.3)* | Emily / DPO | Before WBS 6.3 rework |
| | ✅ **RESOLVED 2026-08-24 — safe to show,** per the reviewer's confirmation covering both OQ-031 and OQ-032 together; this also settles the separate "applicant-type" gap noted in Amendment A-02, Finding 1. **Not yet closed:** §7.1 still names no classification row for the care-support columns — recommend architect-agent add one at TAD stage. | | |
| OQ-033 | Which design system or component library delivers NFR-026's full-width, brand-consistent rendering? *(Amendment A-02, WBS 6.1)* | architect-agent | Before WBS 6.1 finalisation |
| OQ-034 | Can a trustee ever be authorised to review more than one open grant round at the same time? If so, the landing screen (FR-057) needs a round selector; if not, the current auto-scoped design is sufficient. *(Amendment A-03, WBS 6.9)* | Emily | Before WBS 6.9 build |
| | ✅ **RESOLVED 2026-08-25 — N/A.** Reviewer: *"for now its one round at a time. Once a month."* Exactly one round is ever open for review, so no trustee is ever authorised across two at once. Closed together with FR-057. | | |
| OQ-035 | What is the minimum application count a category must have before it can be shown on the landing screen without suppression or grouping (NFR-027)? *(Amendment A-03, WBS 6.9)* | Emily / DPO | Before WBS 6.9 build |
| | ✅ **RESOLVED 2026-08-25 — no minimum, by explicit reviewer risk-acceptance.** Reviewer: *"no minimum group size. The whole point of the code app is for trustees to review items and the column security profile scrubs aways personal information."* NFR-027 (plan-agent's proposed control) is withdrawn, not silently dropped — see §5 and §7.1. The reviewer's named control is the app's existing field-level security profile, not aggregate suppression. | | |
| OQ-036 | What produces the "grant-giving capacity", "suggested maximum spend" and "remaining legacy split" figures (FR-063) — are they derived from Grant/Payment records in this system, or a manually maintained finance snapshot supplied each round? *(Amendment A-03, WBS 6.9)* | Emily / finance | Before WBS 6.9 build |
| | ⚠️ **PARTIALLY RESOLVED 2026-08-25.** Reviewer: *"at the moment everything is manual. Maybe have this land on the finance accessable tables? Or an extra table that finance fills in these details."* Confirmed manual/finance-maintained, not derived — FR-063 and §7.2 updated. **Still open, narrower scope:** which mechanism (extend an existing finance table vs. a new finance-input table) — for architect-agent at TAD stage. | architect-agent | Before WBS 6.9 TAD |
| OQ-037 | Where does the "UK cared-for disabled adults and their carers" benchmark dataset behind FR-061's demographic comparison come from, and who keeps it current? *(Amendment A-03, WBS 6.9)* | Emily | Non-blocking — gates FR-061's benchmark content only, not the rest of WBS 6.9 |
| | ✅ **RESOLVED 2026-08-25 — there is no dataset, and FR-061's benchmark-comparison clause is withdrawn.** Reviewer: *"there is no benchmark dataset. This is personal knowledge of the trustees. So only showing the representation of applications is enough."* FR-061 keeps the applicant distribution percentages and drops the comparison; §7.2's benchmark reference-data row is struck through; US-016 AC-5 loses its benchmark clause. See §4.F+ and the Amendment A-03 "Resolution (continued)" block. **Separate and still open:** the ethnic-group figure has no source data at all, because the field has never been collected — that is **OQ-027**, not this question, and this resolution does not narrow it. | | |
| OQ-038 | Does the full FR-057–FR-063 catalogue fit `CO-001`'s 5–8h ROM, or does the demographic-benchmark and wellbeing-distribution charting (FR-061, FR-062) need its own sizing? *(Amendment A-03, WBS 6.9)* | commercial-agent / architect-agent | Before WBS 6.9 build |
| | ✅ **CONFIRMED 2026-08-25 — extra scope.** Reviewer: *"Yes, this is extra scope not delivered initially."* Hours are **not** covered by CO-001's original 5–8h ROM. A revised sizing pass / CO-001 amendment is in progress with commercial-agent, dispatched separately by the reviewer — see §10. ⚠️ **Scope moved after this was confirmed:** FR-061 lost its benchmark-comparison half later the same day (OQ-037), so the catalogue being sized is smaller than the one this answer was given about. | | |
| OQ-040 | Does any environment hold application records with values in the columns being deleted and recreated? *(Amendment A-04, was OQ-031)* | Reviewer | Before the correction pass |
| | ✅ **RESOLVED 2026-08-16 — no, D-2.** No data in DEV, so every delete-and-recreate and every option-set renumber in the pass was safe. **This answer has an expiry:** it holds only until the first real application, which is why NFR-032 exists as a standing requirement rather than a note. | | |
| OQ-041 | Should the employment column come back as `rev_employmentstatus`? *(Amendment A-04, was OQ-032)* | Reviewer | Before the correction pass |
| | ✅ **RESOLVED 2026-08-16 — yes, D-7.** Renamed on recreate, display name "Employment Status"; the intake payload field became `employment_status`. Free only because D-2's window was empty. | | |
| OQ-042 | Will the live form ask the employment question as five options, and when? *(Amendment A-04, was OQ-033)* | Alex / reviewer | Before the correction pass |
| | ✅ **RESOLVED 2026-08-16 — it already does, D-3.** No form change was needed and no item joined the V-01 … V-11 change request on this account. W2 became a regression fix rather than an improvement: the Boolean was already wrong when written, not merely coarse. | | |
| OQ-043 | Confirm the care-hours band labels. *(Amendment A-04, was OQ-034)* | Reviewer | Before the correction pass |
| | ✅ **RESOLVED 2026-08-16 at revision 1.4 — D-4**, `9 hours or less` / `10 – 19 hours` / `20 – 34 hours` / `35 – 59 hours` / `50+`. Answered twice, the second time in the opposite direction: revision 1.0's "35 - 50 hours" reading was itself the error. ⚠️ **V-10's band overlap is real and stays open** — bands four and five overlap across 50–59 hours on the live form, and the option set stores them as sent rather than silently resolving it. V-10 belongs in the change request to Alex. | | |
| OQ-044 | Does the column removal extend beyond the three carer columns? *(Amendment A-04, was OQ-035)* | Reviewer | Before the correction pass |
| | ✅ **RESOLVED 2026-08-16 — no, D-5.** `rev_supportrecipientname`, `rev_providerpreference`, `rev_applicant.rev_title` and `rev_privacynoticeacceptedon` stay and remain open as M-10 items in the form-validation spec. | | |
| OQ-045 | Do the two reclassified columns become invisible to trustees? *(Amendment A-04, was OQ-036)* | Reviewer / DPO | Before the correction pass |
| | ✅ **RESOLVED 2026-08-16 — split, D-1 and D-6.** Employment status: yes, secured. Exceptional circumstance: no, trustee-visible on necessity. The reasoning for the asymmetry is at §7.1a. | | |
| OQ-046 | **Full re-verification of `docs/development/revitalise-grant-automation-form-validation-spec.md` §4 and §6 against the live form.** *(Amendment A-04, was OQ-037)* A targeted re-fetch on 2026-08-16 checked every field the seven work items touch, plus the disability, helper-routing, break-date, date-of-birth, referee, emergency-contact and provider-preference questions, and found them correct — reconfirming V-04 and M-10 along the way, and confirming that the referee, emergency-contact and provider-preference columns exist for a later stage of the process (FR-042/FR-051) rather than because intake should be asking and isn't. Two §4 rows were found stale and fixed as a side effect. **What it did not do:** work through §4's other ~65 rows, or re-verify §6's remaining option lists — condition profile, income bands, both wellbeing scales, break type, applicant type. *Recommendation: a targeted pass over just those five option lists.* | Reviewer / Alex | **Still open** — the untouched rows gate reliance on §4/§6; **M-01** and **M-02** are the highest-consequence of them |
| OQ-047 | What does a trustee see in place of the exceptional circumstance? *(Amendment A-04, was OQ-038)* | Reviewer / DPO | Before the correction pass |
| | ✅ **RESOLVED 2026-08-16 — the circumstance itself, D-6.** The gap is removed rather than filled. §7.1a shows this follows the solution's existing securing rule rather than excepting it. | | |
| OQ-048 | **Who amends the DPIA and RoPA to record that trustees process the exceptional-circumstance category, and when?** *(Amendment A-04, was OQ-039)* D-6 makes an Art. 9 column trustee-visible. Both documents already record the same arrangement for `rev_conditionprofile`, so this is an amendment to an existing entry and not a new disclosure — but NFR-031 requires it to be written down, not inferred. | DPO / Emily | **Still open** — before go-live, with the DPIA conclusion at OQ-030 |

---

## 10. Effort Estimate

**Size:** **L** by build effort (2–4 person-weeks) — **XL** as a delivery programme (four phases
across roughly twelve calendar weeks, seven components, three external integrations).
**Range:** **106–160 build hours** ≈ **14–21 person-days** (at 7.5 h/day) ≈ 2.7–4.0 person-weeks.
**Basis:** the source document's own bottom-up estimate, midpoint 133 hours, detailed at task level
in the accompanying WBS workbook (`Revitalise-WBS-Grant-Automation-v0.4.xlsx`, not present in
`docs/Import/`).

### Per-automation breakdown (source hours → T-shirt size)

| # | Automation | Source hours | Size | Notes |
|---|---|---|---|---|
| 1 | Form validation & completeness | 12–18 | S | Specification written for Alex, who builds; validation by the consultant |
| 2 | Scoring engine | 16–24 | S–M | Arithmetic is trivial; the data model, option sets, views and edge-case testing are not |
| 3 | Acceptance workflow (DocuSign) | 16–22 | S–M | Template replication plus external procurement dependency |
| 4 | Website → system-of-record intake | 10–16 | S | Foundation for #2, #3, #5, #6; build alongside #1 |
| 5 | AI-assisted anonymisation | 30–46 | M | Largest single item; human-in-the-loop step and threshold tuning drive the range |
| 6 | Trustee review portal | 14–20 | S–M | Expect at least one round of trustee feedback after the demo |
| 7 | Duplicate-grant check | 8–14 | S | Cross-reference fallback approach, not full API integration |
| | **Total** | **106–160** | **L** | |

### Phasing (adopted from the source)

| Phase | Automations | Hours | Size | Cumulative annual saving |
|---|---|---|---|---|
| Phase 1 (weeks 1–4) | #1 Form validation, #4 Intake, #2 Scoring | 38–58 | M | ~215 hours/year |
| Phase 2 (weeks 5–6) | #3 Acceptance workflow | 16–22 | S–M | ~255 hours/year |
| Phase 3 (weeks 7–12) | #5 Anonymisation, #6 Trustee portal | 44–66 | M–L | ~320 hours/year |
| Phase 4 (when needed) | #7 Duplicate check | 8–14 | S | ~330 hours/year |

### Assumptions behind the estimate

- Estimates include requirements clarification with Emily, build, client walkthrough, feedback
  processing, rework, and testing with real application data.
- They assume an **experienced Power Platform consultant**. A developer new to the platform adds
  25–30% (→ 133–208 hours).
- They assume the form plugin exposes a webhook, REST API or structured email. Plugin migration adds
  4–8 hours.
- The move to the Dataverse data model is build-cost-neutral to slightly faster, so these hours
  hold; it raises the recurring licence bill, not the build.
- Return: ~330 staff hours/year at ~200 grants/year — roughly 2.5× year-one ROI at the 133-hour
  midpoint, rising to ~410 hours/year (3.1×) at 250 grants/year.

### Estimate risks and uncertainty

⚠️ **The 106–160 hour range covers the seven automations only.** The governance and security
documents describe platform work that sits outside it and is not separately costed here: environment
setup and UK-residency verification (WBS 0.2), the service account and Conditional Access exception
(WBS 0.3), building the Dataverse tables to the data model (WBS 0.4), configuring the three security
roles and the field-level security profile (WBS 0.5), the connector policy, the retention bulk-delete
jobs and the cross-system retention/erasure helper flow (WBS 0.7). The source treats "Phase 0 setup"
as part of #2 and #4. **The architect should confirm whether that provisioning work is inside or
outside the range before the estimate is committed.**

⚠️ **Complexity multipliers from `skills/how-to-estimate-effort.md` that apply but are not visibly
priced into the source range:** strict regulatory compliance (1.25×), high security classification —
special-category health plus financial data (1.25×), unclear requirements (1.5×, and thirty open
questions remain), and integration with a not-yet-confirmed external system (1.5× for QuickBooks and
the form plugin). The source's ranges absorb ordinary variability and it explicitly removed
double-counted contingency in v0.4. Applied literally, these multipliers would push the upper bound
well past 160 hours. The recommended position is to hold 106–160 hours as the working estimate for an
experienced consultant on a confirmed design, and to **re-confirm it once OQ-002, OQ-004 to OQ-006,
OQ-014 and OQ-015 are closed.**

⚠️ **OQ-004, OQ-005 and OQ-006 must be resolved before this estimate can be confirmed.** Each
is described as a configuration change rather than a rebuild, so none should move the total
materially — but a different answer on OQ-004 (physical separation required instead of field-level
security) means a separate trustee-facing store kept in sync, which is a design change the architect
must size, not a configuration change.

⚠️ **Amendment A-02 (2026-08-24, now APPROVED) does not change the WBS 6 hours cited above.**
FR-056's navigation shell and FR-035's "type of break" and total-funding-requested wording are
believed to fit inside WBS 6.1's and 6.3's existing estimates — the underlying data is already
read into the app, and OQ-031's resolution specifically removed the itemised-cost work that would
not have fit. This is a belief, not a re-quote (`C-COM-008`). **FR-035's care-support and
applicant-type context (OQ-032, resolved safe to show) is different: it reads Dataverse columns
the app does not read today**, which is new build work not sized in WBS 6.3's original 3–5h. Not
sized here, and flagged for whoever picks up WBS 6.3 rework to confirm whether it fits the
existing task or needs its own change-order sizing alongside `CO-001`. The landing screen's
statistics **content** is covered by `CO-001` (WBS 6.9, `depends_on: 6.1`, a 5–8h ROM per that
document), whose firm figure is deferred to the follow-up SDD for `feature:trustee-portal-landing-page`.

⚠️ **Amendment A-03 (APPROVED 2026-08-25) derives FR-057 to FR-063 from the two source decks in
full, per the dispatch instruction to derive rather than assume — it does not pre-filter the
catalogue to fit an hours figure.** The catalogue spans six distinct statistical groupings, two
of which (FR-061's demographic distributions and FR-062's wellbeing/score-distribution
charts) are chart-visualisation work rather than a straight extension of WBS 6.2's existing list
query. ⚠️ **FR-061 is smaller than when that sentence was written** — its benchmark-comparison
half was withdrawn on 2026-08-25 (Amendment A-03 Resolution (continued), OQ-037), so there is
one series to chart per demographic distribution rather than two, and the in-progress sizing pass
should be sized against the reduced FR-061. **OQ-038 is now resolved: the reviewer confirmed this is extra scope** — *"Yes, this is
extra scope not delivered initially"* — so `CO-001`'s original 5–8h ROM does **not** cover
FR-057–FR-063 as approved here. A revised sizing pass / CO-001 amendment is in progress with
commercial-agent, dispatched separately by the reviewer; **hours for this feature are pending
that revision** and no figure — old or new — should be read as current until it lands
(`C-COM-008`).

---

## Appendix A — Traceability Matrix (FR → US)

Test cases are added by the test-agent; this matrix is the coverage baseline.

| FR | User story / acceptance criterion |
|---|---|
| FR-001 | US-001 AC-1 |
| FR-002 | US-001 AC-2 |
| FR-003 | US-001 AC-3 |
| FR-004 | US-001 AC-4 |
| FR-005 | US-002 AC-1 |
| FR-006 | US-001 AC-5, US-002 AC-2 |
| FR-007 | US-005 AC-1 |
| FR-008 | US-005 AC-2 |
| FR-009 | US-005 AC-3 |
| FR-010 | US-005 AC-4 |
| FR-011 | US-006 AC-1 |
| FR-012 | US-006 AC-2 |
| FR-013 | US-006 AC-3 |
| FR-014 | US-006 AC-4 |
| FR-015 | US-006 AC-5 |
| FR-016 | US-006 AC-6 |
| FR-017 | US-006 AC-7 |
| FR-018 | US-006 AC-8 |
| FR-019 | US-006 AC-9 |
| FR-020 | US-006 AC-10 |
| FR-021 | US-006 AC-11 |
| FR-022 | US-006 AC-12 |
| FR-023 | US-010 AC-1 |
| FR-024 | US-010 AC-2, US-015 AC-3 |
| FR-025 | US-010 AC-3 |
| FR-026 | US-007 AC-1 |
| FR-027 | US-007 AC-2, US-014 AC-2 |
| FR-028 | US-007 AC-3 |
| FR-029 | US-007 AC-4 |
| FR-030 | US-007 AC-5 |
| FR-031 | US-007 AC-6, US-012 AC-3, US-015 AC-2 |
| FR-032 | US-014 AC-1, AC-2 |
| FR-033 | US-007 AC-7 |
| FR-034 | US-012 AC-1, US-013 AC-1, AC-2 |
| FR-035 | US-012 AC-2 |
| FR-036 | US-012 AC-3, US-013 AC-4 |
| FR-037 | US-012 AC-4, US-013 AC-3, US-008 AC-1 |
| FR-038 | US-012 AC-5 |
| FR-039 | US-013 AC-4, US-014 AC-3 |
| FR-040 | US-008 AC-1, AC-2 |
| FR-041 | US-003 AC-1, US-008 AC-2 |
| FR-042 | US-003 AC-2 |
| FR-043 | US-003 AC-3, US-009 AC-1 |
| FR-044 | US-009 AC-2 |
| FR-045 | US-003 AC-4, US-009 AC-3 |
| FR-046 | US-003 AC-5 |
| FR-047 | US-008 AC-3 |
| FR-048 | US-004 AC-4, US-011 AC-1 |
| FR-049 | US-004 AC-2, US-011 AC-2 |
| FR-050 | US-004 AC-3, US-015 AC-4 |
| FR-051 | US-004 AC-2 |
| FR-052 | US-004 AC-3 |
| FR-053 | US-004 AC-1 |
| FR-054 | US-011 AC-3 |
| FR-055 | US-011 AC-4 |
| FR-056 | US-012 AC-6 *(Amendment A-02)* |
| FR-057 | US-016 AC-1 *(Amendment A-03)* |
| FR-058 | US-016 AC-2 *(Amendment A-03)* |
| FR-059 | US-016 AC-3 *(Amendment A-03)* |
| FR-060 | US-016 AC-4 *(Amendment A-03)* |
| FR-061 | US-016 AC-5 *(Amendment A-03)* |
| FR-062 | US-016 AC-6 *(Amendment A-03)* |
| FR-063 | US-016 AC-7 *(Amendment A-03)* |
| FR-070 | US-020 AC-1, AC-2, AC-3 *(Amendment A-04)* |
| FR-071 | US-020 AC-2 *(Amendment A-04)* |
| FR-072 | US-021 AC-1, AC-3 *(Amendment A-04)* |
| FR-073 | US-022 AC-1, AC-2 *(Amendment A-04)* |
| FR-074 | *(no user story — a record-keeping requirement, verified by schema and intake tests)* *(Amendment A-04)* |
| FR-075 | US-023 AC-1, AC-2 *(Amendment A-04)* |
| FR-076 | *(no user story — a removal, verified by absence; asserted in `IntakeContract.Tests.ps1`)* *(Amendment A-04)* |
| FR-077 | US-021 AC-2 *(Amendment A-04)* |

NFR-001 to NFR-003 are additionally exercised by US-012 AC-3 and US-015 AC-1, AC-2.
NFR-022 to NFR-025 have no acceptance criteria by design — they are recorded gaps (OQ-020 to OQ-023).
NFR-027 is withdrawn (Amendment A-03 Resolution, 2026-08-25) and carries no acceptance criteria.
NFR-030 is evidenced by the §7.1a classification table itself, not by a test.
NFR-031 is exercised by US-020 AC-4, which is testable in both directions — the category readable by
a trustee role, the free text behind it not.
NFR-032 has no acceptance criterion: it is a sequencing constraint, evidenced by the pass having
completed on 2026-08-17 while D-2's empty-data window was still open, not by a runtime assertion.

⚠️ **One mapping was corrected during the Amendment A-04 merge, rather than carried forward wrong.**
The retired SDD's appendix traced its NFR-028 (now NFR-032, the option-set renumbering rule) to its
US-017 AC-4 — the criterion asserting that a trustee-role read of the employment status returns no
value. Those are unrelated subjects; the renumbering rule says nothing about who may read a column.
That acceptance criterion belongs to **NFR-001**, this document's existing requirement that
special-category fields be readable only by the administrator role and the service identity, which
is what D-1 actually implements. **US-021 AC-4 → NFR-001.** No requirement text changed; a
traceability row that did not hold was repaired and is recorded here rather than fixed quietly.

---

## Approval
**Reviewed by:** Xander Lykopoulos  **Date:** 2026-08-10  **Response:** `APPROVED`
