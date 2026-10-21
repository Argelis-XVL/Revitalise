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
FR-070+ / NFR-030+ / US-020+ / OQ-040+ — see below** ·
**Amendment A-05 APPROVED 2026-08-27 — the trustee detail screen carries every board-pack field;
Amendment A-02's three exclusions reversed and OQ-011 resolved by reviewer decision — see below** ·
**FR-059 and §7.1's Round-level aggregate row CORRECTED 2026-08-28, following TAD Revision 6
§6.3.5 / ADR-039 — the "no minimum-cell-size rule" / "no single application's data is shown"
premise was false for the four money-average measures (FR-059's average exceptional-funding
amount requested; FR-060's average holiday cost, average grant amount requested and percentage
of total cost), whose security basis does not exist on this platform for Money columns; the
reviewer set a `k = 5` minimum-population control for those four measures only — see below** ·
**Amendment A-06 APPROVED 2026-08-30 — FR-058's "average applications received per day" corrected
from a per-round to a cumulative, charity-wide figure since a fixed 16 Feb 2026 reference date
(`IMP-0507`) — see below** ·
**Amendment A-07 APPROVED 2026-09-19 — FR-058's per-day figure is superseded by an all-history,
month-by-month recompute with anomaly flagging (`CO-005`, `wbs:6.10`, resolving `IMP-0789`) — see
below** ·
**Amendment A-08 APPROVED 2026-09-25 — the website intake transfer rule and the answers it newly
stores (`wbs:4.1`, `4.2`, `4.3`, contracted rework; answering TAD rev 10 Appendix C §C.9; OQ-051 to OQ-053 answered) —
see below** ·
**Amendment A-09 APPROVED 2026-10-16 — Narrative Scrubbing follows the client's Anonymisation Key: gendered and relationship words become neutral ones, names become *They*, the redacted copy reads correctly and is spell-checked (`wbs:5.6`; spell-check under `CO-009`, approved unbilled); hosting in Switzerland and EU prompt processing accepted (NFR-009); OQ-054 to OQ-056 adopted at their defaults — see below** ·
**Amendment A-10 APPROVED 2026-10-19 (revision 2, after reviewer feedback) — Auto-reject extended to three financial eligibility rules (amount over the limit for the break type without an exceptional request, £100 or £500 by type; income above the ceiling for an applicant not on means-tested benefits; savings over £6,000), every rule's parameter a setting the process owner changes, every reason that fired written for Emily, the 12-month prior-funding rule written down as built (`wbs:2.4`, `2.7`; not billable) — see below** ·
**Amendment A-11 APPROVED 2026-10-19 — the process owner reviews and releases every redacted narrative, not only flagged ones, and nothing is released automatically; the confidence threshold becomes a flag for her attention (FR-029, FR-030, NFR-017, NFR-018, US-007 AC-4 and AC-5); the applicant's own name keeps `[NAME]` and a name right after a relationship word is dropped even when other people are named (FR-095) (`wbs:5.3`, `5.4`, `5.6`; no new ids; OQ-054 case (e) confirmed) — see below** ·
**Amendment A-12 APPROVED 2026-10-20 — recording the final payment starts the six-year retention clock: the grant's final payment date is set and the application moves to "Grant Paid" (FR-107 to FR-112, US-026; `wbs:8.6`, change order `CO-010`, scope accepted unbilled; OQ-057 and OQ-058 answered; **reviewer-directed revision 2026-10-20: a final payment must carry a payment date, and marking it final sets its status to Issued**, with OQ-059 raised and answered *"No. payment final means final."*; **second revision 2026-10-20: the grant's own status also moves to "Paid", FR-113, with OQ-060 raised and answered *"Keep default."***) — see below**

<!-- id-allocation: FR-001..FR-063, FR-070..FR-079, FR-080..FR-082, FR-083..FR-093, NFR-001..NFR-027, NFR-030..NFR-032, OQ-001..OQ-038, OQ-040..OQ-048, OQ-049..OQ-050, OQ-051..OQ-053, US-001..US-016, US-020..US-023, US-024, FR-094..FR-101, OQ-054..OQ-056, US-025, FR-102..FR-106, FR-107..FR-111, OQ-057..OQ-058, US-026, FR-112, OQ-059, FR-113, OQ-060 -->

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
> | Means-tested benefits, benefit provider, income band, savings over £6,000, employment status | Not shown | **Correctly excluded — not a gap.** §7.1 already classifies "benefit status" as special category, highest restriction, *"Never shown to trustees."* The PDF's Financial Eligibility section is consistent with the approved design boundary, not evidence against it. |
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
> [Architecture §3.1](docs/architecture/revitalise-grant-automation-architecture.md) and
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
> §3.4 of the trustee-portal-visual-refresh TAD and risk
> A-R24 of the same TAD, and gated by
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

---

> ## 📌 Amendment A-05 — APPROVED 2026-08-27
>
> **Raised by:** plan-agent, 2026-08-27, dispatched by lead-agent following a reviewer policy
> decision given in the same session (`feature:revitalise-grant-automation`; **WBS 6.3**).
>
> **Status: APPROVED.** The reviewer's instruction *is* the resolution — it was given in response
> to a report of Amendment A-02's exclusions and ended with the word *"Build"*. Following A-02's
> own precedent (OQ-031 and OQ-032 were raised and resolved in one pass because the answer arrived
> in the same session), this amendment does not re-ask a question the reviewer has already
> answered. The new content is edited directly into §4, §5, §6, §7 and §9, each edit point carrying
> a one-line pointer back to here.
>
> **Not a change order.** This extends the WBS 6.3 application-detail deliverable that A-02 already
> reworked; it adds fields to a screen the contract already pays for, and creates no new screen,
> table or automation. Same reasoning A-02 recorded for its own field additions (`C-COM-002`).
>
> ### Why this session ran
>
> Amendment A-02, Finding 1, compared the sample trustee board pack
> (`docs/Import/3. Round 4 - Individual Applications.pdf`) field-by-field against the trustee detail
> screen and marked three categories **"Correctly excluded — not a gap"**: the Financial Eligibility
> section, the condition/illness checklist with its health free text, and the helper / referee /
> emergency-contact block. It also left **OQ-011** open — the redaction scope for
> `rev_unabletofundexplanation` and the exceptional-circumstance free text.
>
> The reviewer has reversed all three exclusions and answered OQ-011, in these words:
>
> > *"Just add the following items: this is what currently been shared with them as well. […] The
> > same for the unresolved items for OQ011. All fields need to be in. All fields with free text
> > data will be scrubbed with AI. Identifying information will be protected by the security
> > profile. It's not something new we are building. the process is just being automated. Build."*
>
> Read literally and in order: add the three excluded categories; resolve OQ-011 the same way; and
> the stated basis for safety is that (a) trustees already receive this data in the printed board
> pack, so automating it creates no new audience, (b) free text goes through the same AI-redaction
> path the narrative already uses, and (c) genuinely identifying columns are held back by Dataverse
> column security regardless of what the app asks for.
>
> **Findings 1 and 2 below confirm (b) and (c) are technically correct as stated.** Finding 3
> records one thing the reviewer's framing does not cover, and Finding 4 one thing that is true but
> that the reviewer may not expect.
>
> ### Finding 1 — the reviewer's "protected by the security profile" claim is correct, column by column
>
> Every column named below was read directly from
> [`Entities/rev_application/Entity.xml`](src/solutions/RevitaliseGrantAutomation/Entities/rev_application/Entity.xml)
> and from the real `<AttributeName>` entries in
> [`Other/FieldSecurityProfiles.xml`](src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L106) —
> **not** from that file's comments, which is the mistake §7.1a records an earlier revision making.
> All of them sit on `rev_application`; A-02's guess that some might live on `rev_applicant` was
> wrong and is corrected here.
>
> `REV_TrusteeRestricted`'s own description is the control:
> *"Every persona that is not a member of this profile — including every trustee — receives no value
> for these columns from any surface: app, view, export or API."* Membership is applied per
> environment by
> [`ensure-column-security-profile-members.ps1`](provisioning/dataverse/ensure-column-security-profile-members.ps1),
> which adds the group teams **REV Admins and REV Service Accounts and nothing else**
> ([file header](src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L18)).
> Trustees are therefore non-members by construction, not by configuration that could drift.
>
> **Group A — already unsecured; binding them shows a real value, and no redaction is involved.**
> These nine carry `IsSecured=0` and are absent from both profiles. Two of them
> (`rev_conditionprofile`, `rev_supportrecipientconditionprofile`) are **Article 9 special-category
> data that is trustee-visible by design** — see Finding 3.
>
> `rev_incomeflag` · `rev_incomeband` · `rev_savingsover6000` · `rev_conditionprofile` ·
> `rev_supportrecipientconditionprofile` · `rev_helperorganisation` · `rev_helperrelationship` ·
> `rev_helperdeclarationconsent` · `rev_helperdeclarationconsentdate`
>
> **Group B — `IsSecured=1` and confirmed members of `REV_TrusteeRestricted`.** Binding these is
> safe because the platform returns no value to a trustee whatever the app asks for. Line numbers
> are the profile's actual `<AttributeName>` entries:
>
> | Column | `IsSecured` | `<AttributeName>` entry |
> |---|---|---|
> | `rev_receivesbenefits` | 1 | [L389](src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L389) |
> | `rev_benefitprovider` | 1 | [L398](src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L398) |
> | `rev_employmentstatus` | 1 | [L443](src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L443) |
> | `rev_helpername` | 1 | [L254](src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L254) |
> | `rev_helperemail` | 1 | [L263](src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L263) |
> | `rev_helperphone` | 1 | [L272](src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L272) |
> | `rev_refereename` | 1 | [L281](src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L281) |
> | `rev_refereeemail` | 1 | [L290](src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L290) |
> | `rev_refereephone` | 1 | [L299](src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L299) |
> | `rev_emergencycontactname` | 1 | [L308](src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L308) |
> | `rev_emergencycontactphone` | 1 | [L317](src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L317) |
>
> This is the same "second line of defence" position the solution already takes for `rev_applicant`'s
> secured columns. **It does not weaken FR-036 or NFR-003** — NFR-003 already requires the control to
> be *"enforced by the platform, not by manual preparation"*, which is exactly what this is. What
> changes is only where the boundary is enforced: previously the app also declined to ask, now the
> platform alone withholds. FR-078 below makes the resulting screen state a requirement rather than
> an accident.
>
> ### Finding 2 — the one place this is not a front-end change: five free-text columns have no redacted counterpart
>
> The reviewer's *"all fields with free text data will be scrubbed with AI"* describes a pipeline
> that exists in pattern but not yet in schema for these five columns. `rev_narrativeraw` has its
> twin `rev_narrativeredacted` (`IsSecured=0`, already wired), and the care-support trio has
> `rev_caresupportdescriptionredacted`, `rev_careprovidedexampleredacted` and
> `rev_othercareprovidedtyperedacted`. **These five have no counterpart at all:**
>
> `rev_unabletofundexplanation` · `rev_exceptionalfundingdetail` · `rev_otherexceptionalcircumstance` ·
> `rev_otherconditionraw` · `rev_supportrecipientotherconditionraw`
>
> All five are `IsSecured=1` and in `REV_TrusteeRestricted`, so nothing leaks today — a trustee
> simply sees nothing. But *"add all fields"* cannot be delivered for these five by binding a column;
> it needs new schema first, following the counterpart pattern above. **That is an architect-agent
> decision at TAD stage, not one this amendment makes** — it is recorded here so it is not silently
> dropped between "Build" and a front-end task. FR-079 below is the requirement it satisfies.
>
> Two notes for whoever designs it. First, four of the five are in
> [`special-category-register.yml`](constraints/domain/special-category-register.yml#L67); the fifth,
> `rev_unabletofundexplanation`, is not, and correctly so — it is secured financial free text under
> Article 6, not Article 9. Second, a redacted counterpart is **not** added to that register: the
> register's own note records that `rev_narrativeredacted` is deliberately unlisted because it *"is
> designed to no longer BE special-category data at all"*
> ([L193](constraints/domain/special-category-register.yml#L193)). Registering a new counterpart
> would make `C-DOM-031` demand `IsSecured=1` on a column whose whole purpose is to be readable.
>
> ### Finding 3 — §7.1's special-category row was already wrong, and this amendment must not inherit it
>
> §7.1 classifies *"Applicant and support-recipient condition profiles […] benefit status"* together
> at the highest tier and says **"Never shown to trustees."** That has been inaccurate for the
> condition profiles since before this amendment: `rev_conditionprofile` and
> `rev_supportrecipientconditionprofile` carry `IsSecured=0`, are absent from `REV_TrusteeRestricted`,
> and are trustee-visible **by design** under the rule §7.1a states explicitly —
> *"Categorical answers are trustee-visible. Identity and free text are not."*
>
> So §7.1 and §7.1a contradict each other, and §7.1a is the one that matches the schema. The
> reviewer's decision did not create this; it exposed it, because the reviewer's instruction relies
> on §7.1 being an accurate description of what trustees see. **§7.1 is corrected rather than
> deleted** — the underlying control is unchanged, only its description was wrong. Benefit status and
> employment status genuinely do remain undisclosed to trustees, and this amendment does not move
> them out of the profile.
>
> ### Finding 4 — what a trustee will actually see, which is less than the reviewer may expect
>
> Automation #5, the AI redaction itself, is **still deferred** — `EX-003` in
> [`known-exceptions.json`](contract/known-exceptions.json) records the reviewer's own decision to
> build the trustee portal ahead of it, and `rev_redactionreleased` is `false` for every record
> today. Consequently, on the day this amendment ships:
>
> - **Group A (nine columns) renders real values.** This is the visible substance of the change.
> - **Group B (eleven columns) renders a restricted state, never a value** — correct, and the intended
>   behaviour, but the trustee sees a labelled field with nothing in it.
> - **Every free-text column renders its withheld state**, including the narrative, which already
>   behaves this way. Nothing textual appears until Automation #5 ships.
>
> This is the status quo the existing narrative panel already lives with, and it is not a reason to
> withhold the schema and wiring work. It is recorded because *"all fields need to be in"* and *"all
> fields with free text data will be scrubbed with AI"* together could reasonably be read as
> expecting scrubbed text to appear on the screen, and it will not until Automation #5 is built.
>
> ### Finding 5 — the DPIA already anticipates this surface; two narrow amendments are still owed
>
> The reviewer's *"it's not something new we are building, the process is just being automated"* is
> supported by the DPIA more directly than expected. `docs/Import/Revitalise-DPIA-v0.1.docx` already
> describes the surface and the control in one sentence: *"Trustees review eligible applications
> through a dedicated app that hides identity by field-level security, and record a verdict."* The
> Code App is that app. **The trustee audience is not new, and the system surface is not new to the
> DPIA either.** OQ-048 makes the same point for the condition profiles: the DPIA and RoPA already
> record trustees processing that Article 9 category.
>
> Two things are genuinely owed, and neither blocks this amendment:
>
> 1. **The DPIA describes redaction as covering *"the free-text narrative"* — singular.** FR-079
>    extends it to five more columns. That widens what the DPIA describes and should be written into
>    it. Folded into **OQ-048**'s scope rather than raised as a new question, matching how §7.1a
>    handled OQ-004 and OQ-006 — the surface changes, the question is not re-opened, and the DPO is
>    told rather than left to discover it.
> 2. **The DPIA is a concept draft and is not signed off** (§7.0), and its own trustee-consultation
>    row reads `[TBC — confirm]`. This amendment increases the weight carried by column security,
>    because it is now the *only* barrier for eleven columns rather than the second of two. That
>    makes **OQ-004** (is column security an acceptable trustee control?) more load-bearing than it
>    was, not less. OQ-004 is already marked **"Before build starts"**; this does not change its
>    status, it raises its stakes.
>
> ### Adopted FR-035 replacement wording
>
> > **FR-035** — The system SHALL provide a per-application detail view showing the redacted
> > narrative, the score breakdown, the type of break, the preferred dates, the break location, the
> > total funding requested for the grant round (including any exceptional funding requested), the
> > applicant-type context, the care-support context, the staff recommendation, and — added by
> > Amendment A-05 — the **financial-eligibility context** (household income flag and band, savings
> > above the threshold, receipt of means-tested benefits, benefit provider, employment status, and
> > the redacted explanation of why the applicant cannot fund the break themselves), the **condition
> > context** (the applicant and support-recipient condition profiles, the redacted free-text
> > elaboration behind each, the exceptional-circumstance category and its redacted free-text
> > detail), and the **helper, referee and emergency-contact context** (helper organisation,
> > relationship, declaration consent and its date, and the helper, referee and emergency-contact
> > identity attributes), SO THAT trustees see in the portal the same case they receive today in the
> > printed board pack. Fields whose value is withheld by column security render per FR-078; free
> > text renders per FR-079.
>
> ### New requirements
>
> **FR-078** and **FR-079** are added to §4 (new subsection J). They exist because *"all fields need
> to be in"* has two consequences that no existing requirement covers: what the screen does with a
> field the platform refuses to populate, and what it does with free text that has no redacted
> counterpart yet.
>
> ### Resolution — 2026-08-27
>
> - **OQ-011 (anonymisation rules / redaction scope) — RESOLVED.** Reviewer's own words: *"All
>   fields need to be in. All fields with free text data will be scrubbed with AI. Identifying
>   information will be protected by the security profile."* Read literally: nothing is excluded from
>   the trustee view on classification grounds; every free-text column is redacted before it is shown
>   (FR-079); identity is held back by `REV_TrusteeRestricted` (FR-078). The question's other half —
>   generalisation, age → band and location → region — is unchanged and already carried by §7.1's
>   Pseudonymised tier, which names age range and location area as what trustees see.
> - **The three A-02 exclusions are reversed.** A-02's Finding 1 rows reading *"Correctly excluded —
>   not a gap"* for Financial Eligibility, the condition/health checklist and the helper / referee /
>   emergency-contact block are superseded by this amendment. They are left in place in A-02 rather
>   than edited, so the record shows what was decided and when it changed.
> - **OQ-048 gains scope** — it now also covers recording the widened redaction scope from FR-079 in
>   the DPIA and RoPA. Not re-opened, not a new question.
> - **OQ-004 is unchanged in status and heavier in consequence** — see Finding 5.

> ⚠️ **Reader's note.** The DPIA and RoPA that underpin §7 of this document are both at
> **"Concept draft — for DPO review"** status. They are not signed off. Three specific DPO
> decisions (OQ-004, OQ-005, OQ-006) gate build on the current design basis. This SDD may be
> approved as a statement of requirements, but build must not start on the field-level-security
> and 6-year-retention basis until those three decisions are recorded.

> ## 📌 Amendment A-06 — APPROVED 2026-08-30
>
> **Raised by:** lead-agent, 2026-08-30, recorded as `IMP-0507` in
> `logs/improvement-log.jsonl` (`class: platform-contract-guessed-not-groundtruthed`, `severity:
> rework`) — a delivered flow computation (`Compose_applications_per_day`, `wbs:6.9`) was built
> against the wrong metric definition. This corrects **what FR-058's "average applications
> received per day" means**, not the scope of FR-058 — `wbs:6.9` already covers FR-058 under
> `contract/change-orders/CO-001.md` (APPROVED), and this amendment does not add or remove hours.
>
> ### The correction
>
> Amendment A-03 (2026-08-25) and the TAD built against it both read FR-058 as a **per-round**
> figure: numerator the current round's own application count, denominator whole days since that
> round's own `rev_roundopenedon`
> ([TAD §3.5](docs/architecture/trustee-portal-visual-refresh-architecture.md),
> resolution recorded at
> [Appendix A, FR-058 row](docs/architecture/trustee-portal-visual-refresh-architecture.md)).
> Development delivered exactly that reading (`Compose_applications_per_day`, `wbs:6.9`).
>
> The reviewer's own words, given directly to lead-agent and not solicited by a gating question on
> this point, are a different metric: *"so it's the average of all applications in total, since the
> start of the grant giving charity wich is 16th of february 2026. So the start date is set and the
> end date keeps changing the the end date of the round."* Read literally: the numerator is the
> **cumulative total of all applications ever received**, counted from a single **fixed** reference
> date — **16 February 2026**, when the charity's grant-giving began — not from any one round's own
> open date. The denominator is whole elapsed days from that fixed date to **now**, recomputed live
> on every load — "the end date keeps changing" describes today's date advancing, not the round's
> close date. Nothing in this figure resets when a new round opens.
>
> This is what the two source decks' own numbers already showed and neither A-03 nor the TAD
> checked: `Round 3 Stats.pptx` slide 2 reads *"434 [applications] since 16th Feb, Average 6 per
> day"*; `Round 4.pptx` slide 2 reads *"717 Applications received, Average 6 per day"*. A per-round
> reading cannot produce the same ~6/day average against cumulative counts of 434 and then 717 —
> that pattern is only consistent with a running total over elapsed time since one fixed start. The
> decks alone were not treated as the source of this correction, because they show the result, not
> the reviewer's stated formula; the reviewer's words above are the citation.
>
> **FR-058 is reworded below** to state the fixed reference date and the cumulative, charity-wide
> count explicitly. §10 is unaffected — no new WBS scope, per CO-001 and `wbs:6.9`'s existing
> membership.
>
> ### Flagged for architect-agent — two items this amendment does not itself decide
>
> This SDD states what the figure means; how it is built is architect-agent's decision at TAD
> stage, same division of labour as A-03's Finding 3 / OQ-036 (FR-063's finance-figure mechanism):
>
> 1. **The fixed reference date (16 February 2026) needs a stored, entered fact, not a derived
>    one.** It is not any round's `rev_roundopenedon` and is not computable from existing data —
>    the same pattern `rev_roundopenedon` itself already established for a per-round start date,
>    but at charity scope rather than round scope.
> 2. **The existing `List_applications_in_round` query must not be repurposed for this metric.**
>    It is deliberately round-scoped and several other FR-058/FR-059/FR-061/FR-062 metrics (gender,
>    age, wellbeing and exceptional-circumstance distributions) depend on that scoping being
>    correct. This metric needs a separate, new all-time / cross-round application count; widening
>    the existing query's scope would silently change every other metric that reuses it.
>
> Neither item is a new open question requiring a further reviewer decision — the business meaning
> is now settled by this amendment's Resolution above. Both are TAD-stage build decisions, recorded
> here so architect-agent does not have to re-derive them from `IMP-0507`.

> ## 📌 Amendment A-07 — APPROVED 2026-09-19
>
> **Raised by:** plan-agent, 2026-09-19, dispatched by lead-agent to resolve `IMP-0789`
> (`class: unstated-architecture-decision-in-build-instruction`, `severity: rework`) —
> development-agent correctly stopped a `wbs:6.10` build dispatch rather than guess an aggregation
> mechanism, because `contract/change-orders/CO-005.md` states plainly, in its own Sizing basis
> section, that *"no FR text exists yet for this rescope."* This amendment gives that rescope FR
> text. **This does not restate or alter CO-005's hours** — §10 below cites the change order, per
> `C-COM-008`.
>
> ### What changes, at business level
>
> `CO-005` (APPROVED 2026-09-18, `wbs:6.10`, `depends_on: 6.1, 6.9`) rescopes the *Applications per
> day* figure FR-058 delivered under Amendment A-06 (a cumulative charity-wide average since a
> fixed reference date). The reviewer confirmed the tile stays but the calculation changes
> (`docs/plans/emily-review-feedback-2026-09-plan.md` lines 909–916, EF-11 Δ5): recompute from
> **all historic applications**, broken down **month by month**, with **anomaly flagging** against
> each month's own trailing six months, plus **two new settings** so historic totals are not
> silently understated by the gap between when the charity began giving grants and when this
> system began recording them. **FR-058's own "average per day" clause is superseded** by FR-080
> below; FR-058's other two figures (total applications received, round-open date) are unchanged.
>
> | New ID | Requirement | Supersedes / relates to |
> |---|---|---|
> | FR-080 | All-history, month-by-month applications recompute | Supersedes FR-058's per-day clause |
> | FR-081 | Anomaly flagging against the trailing six months | New |
> | FR-082 | Two `rev_setting` business facts backing FR-080 | New |
>
> ### FR-058's per-day clause — struck, not silently dropped
>
> FR-058 keeps the current round's total-applications-received figure and the round-open date. The
> "average applications received per day since the charity began grant-giving" clause — the
> subject of Amendment A-06's own correction eleven days ago — is **struck by this amendment** and
> replaced by FR-080's month-by-month recompute, which answers the same underlying question
> ("how is this round progressing against history") in the shape the reviewer asked for in EF-11.
> See the FR-058 row below for the marked text.
>
> ### Flagged for architect-agent — the aggregation mechanism, per the standing A-FLOW-08 precedent
>
> **This SDD does not choose how the month-by-month grouping and trailing-six-month comparison are
> computed. That is an architecture decision, routed to architect-agent, on this solution's own
> established precedent for exactly this class of problem:**
> `src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.notes.md`,
> assumption `A-FLOW-08` — *"the workflow definition language's math functions are exactly `add,
> div, max, min, mod, mul, pow, rand, range, sub`. There is no `sum()` over an array... Four
> mechanisms exist and none of them is a dev decision... Choosing between them is an architecture
> decision and it is routed to `architect-agent`."* `A-FLOW-08` itself was resolved at TAD Revision
> 6 / ADR-039 for a **fixed-size** grouping (five break types). FR-080/FR-081 are **one class
> harder**: a **variable-length, unbounded** grouping (every calendar month since a stored start
> date, growing every month) rather than a fixed five-way split, so ADR-039's specific mechanism is
> not assumed to carry over unexamined — architect-agent's TAD decides which of the same four
> candidate mechanisms (or another) fits a variable-length group-by, and records it as its own ADR.
> Also flagged for the same TAD pass, following the identical division of labour as Amendment
> A-06's own "Flagged for architect-agent" section and FR-063's OQ-036: the **technical key names**
> for FR-082's two new `rev_setting` rows (this document states the business fact each one must
> hold; naming the Dataverse column is the same TAD-stage decision that produced
> `RoundStatisticsStaleAfterSeconds` and `RoundStatisticsMoneyMeasureMinimumPopulation`).
>
> ### What this amendment does NOT settle — two new open questions, not guessed here
>
> 1. **The anomaly-flag threshold.** Neither CO-005 nor the EF-11 walkthrough gives "sudden spike
>    or drop" a number. This is a disclosure-shape decision the reviewer has made directly for
>    every comparable threshold in this document — `k = 5` for the four money measures (OQ-043,
>    TAD §0.9.1, *"this value is a disclosure control, not a tunable"*), the 85% redaction
>    confidence floor (FR-029), the 14-day escalation window (FR-044) — never inferred by a
>    modelling convention such as "2 standard deviations" or "±50% month-over-month," because what
>    counts as *sudden* to a board of trustees reading a chart is a business judgement, not a
>    statistical one, and a wrong default here produces a false alarm or a missed one on a live
>    board pack. **Raised as OQ-049 below rather than defaulted.**
> 2. **The two `rev_setting` rows' actual seed values** (the real date, and the real pre-system
>    count) are historic facts about the charity, not a design decision — nobody at architect-agent
>    or plan-agent can supply them. **Raised as OQ-050 below.**
>
> ### Addendum, 2026-09-19 — both open questions answered; OQ-049's answer reopens architecture
>
> **OQ-049 and OQ-050 are both ANSWERED** (see the ✅ rows at §9 and the restated FR-081/FR-082
> text above). OQ-050 closes cleanly: the two seed values are now known and simply await
> `development-agent` seeding them at `wbs:6.10`'s `post_deploy` step — no design work follows from it.
>
> **OQ-049 does not close as cleanly.** Its answer — a trailing-six-month-mean, 50%-deviation
> threshold, itself held as a *third* configurable `rev_setting` — is new requirement content, not
> merely a number filling in a blank the FR text already anticipated. TAD Revision 9 / ADR-049 was
> written before this answer existed: it designed FR-080's variable-length month-by-month grouping
> mechanism and named FR-082's two settings, but it does not name a threshold setting and does not
> design the mean/deviation comparison logic that must run inside FR-080's same Apply-to-each-over-months
> loop. **This is routed back to `architect-agent` for a further TAD pass — naming the new setting
> and extending §5.1.3's flow design — before `development-agent`'s `wbs:6.10` dispatch can encode
> FR-081's flagging rule.** This is the same "Flagged for architect-agent" division of labour this
> amendment already used above for FR-082's two settings; it was not anticipated for FR-081 only
> because FR-081's threshold was still an open question at the time TAD Revision 9 was written.

> ## 📌 Amendment A-08 — APPROVED 2026-09-25
>
> **Raised by:** plan-agent, 2026-09-25, dispatched by lead-agent on architect-agent's
> `CASCADE: SPEC_GAP` from TAD rev 10 Appendix C §C.9. **Contracted scope:** `wbs:4.1`, `4.2`,
> `4.3` — contracted rework, not a change order; the reviewer confirmed it in these words: *"Yes
> the rework falls in those tasks."* §10 is unaffected and restates no figure (`C-COM-008`).
>
> ### Why this session ran
>
> The website developer (Alex) replaced the intake contract with the form's native payload. One
> sample entry and his covering note are in `docs/Import/` (2026-09-25). Architect-agent mapped
> every key in TAD rev 10 Appendix C. It found six places where the design stores data, or stops
> storing it, and no requirement in this SDD says it should. This amendment writes those
> requirements. It decides no column, type, flow or security setting. Those remain the TAD's.
>
> ### The governing rule — the reviewer's words, verbatim
>
> > *"Keep all data that is actively requested from the user. If the form saves a date to a
> > separate field the user doesnt fill in, ditch it. Only transfer what is actually filled in by
> > the user of the form."* — Xander Lykopoulos, 2026-09-25
>
> Every new or amended requirement below states this rule. None reinterprets it. **One exception is
> recorded by the TAD (rev 10 `ADR-051` item 12, Appendix C §C.6) and not by the reviewer:** the
> form's entry id is kept, only as the technical duplicate key. FR-083 carries that exception
> openly, as an exception, so the reviewer's approval of this amendment is also the approval of it.
>
> ### What changes, at business level
>
> | ID | Requirement | §C.9 item | Supersedes / relates to |
> |---|---|---|---|
> | FR-083 | Store every applicant-entered answer, and nothing the form generates. Entry id is the one exception | 1 | **Amends FR-007** |
> | FR-084 | A question left blank, or not shown, stores nothing | 1 | Relates to FR-077, FR-022 |
> | FR-085 | Store how the applicant heard about Revitalise | 2 | New. The columns exist; nothing wrote them |
> | FR-086 | Store the applicant's Equality Act 2010 disability answer | 3 | New — **Art. 9** |
> | FR-087 | Store the carer-route Equality Act 2010 answer about the person supported | 3 | New — **Art. 9** |
> | FR-088 | Store the applicant's description of how their disability affects them | 3 | New — **Art. 9** |
> | FR-089 | Store the carer-route description of how the person supported is affected | 3 | New — **Art. 9** |
> | FR-090 | Store whether someone is helping complete the application | 4 | New |
> | FR-091 | Store the provisional break date exactly as written | 4 | **Amends FR-001**; relates to EF-09 / M-06 |
> | FR-092 | Store all three other-funding answers, including "awaiting decision" | 4 | Relates to FR-035 (not changed, see below) |
> | FR-093 | Middle name, name suffix and state/province: stored only if the form shows them | 6 | Conditional — OQ-053 |
> | FR-001, FR-027 | Reworded — no date of birth is collected | 5 | Corrected in place, originals kept |
> | US-024 | *Everything the applicant told us is on the record, and nothing else is* | — | Traces FR-083 to FR-093 |
>
> §7.1c classifies every newly stored answer, records the Art. 9 condition for the four
> special-category answers, and writes the DPIA line. §9 adds OQ-051 to OQ-053 and widens OQ-048.
>
> ### Findings that shaped the text
>
> **1. The Art. 9 condition is already recorded, so it is not raised as a question.** §7.2's
> *Application* grouping covers *"health free-text and disability data … processed to assess
> eligibility and need only"* under Art. 9(2)(b) and 9(2)(h). The *Support-recipient* grouping
> covers the same for the person supported. The four new answers are disability data about the
> same two people, asked for the same purpose: a grant for disabled people and their carers. They
> sit inside those groupings. No new Art. 9 condition is created, and none is needed. The DPIA and
> RoPA still have to *name* them, which is a recording task and not a new basis (§7.1c, OQ-048).
>
> **2. Trustee visibility of the four new answers is not left blank, and it is not guessed.**
> Earlier sources answer most of it. The trustee board pack Emily sends today
> (`docs/Import/3. Round 4 - Individual Applications.pdf`) prints, under *About Applicant*, both
> *"Do you or the person you support have a disability as defined by the Equality Act 2010?"* and
> the full *"Brief Confirmation"* text. Amendment A-02, Finding 1, listed that text as *"Correctly
> excluded"*. **Amendment A-05 reversed that exclusion**, on the reviewer's words *"All fields need
> to be in. All fields with free text data will be scrubbed with AI."* Applied to these answers,
> that gives the category shown as a value and the description shown only through a redacted
> counterpart (the ADR-027 / FR-079 pattern). **TAD rev 10 instead specifies all four as secured and
> none trustee-visible.** That is the safe position, and it is what holds until the reviewer
> answers. So OQ-051 asks the reviewer to confirm or replace a default drawn from A-05. It does
> not ask an open question, and it does not change FR-035 until answered. That follows
> `skills/how-to-write-requirements.md`: an open question omits the clause, it does not qualify it.
>
> **3. `docs/plans/emily-review-feedback-2026-09-plan.md` records EF-37 as needing *"no automation
> work at all"*, and that is not true.** It says the disability description *"lands in
> `rev_narrativeraw` exactly as the applicant's own does"*. The native payload shows `narrative_raw`
> is *"how this break would benefit you"* (TAD rev 10 Appendix C §C.1). The description
> (`brief_confirmation`) was discarded until rev 10, as spec gap M-09 had already recorded. So the
> pack row EF-37 relabels as *Brief Description of Disability* has no stored source until FR-088
> and FR-089 are built. **The reviewer's 2026-09-17 correction still stands.** One subject, the
> disabled person the application is about, whoever types the answer. FR-086 to FR-089 are written
> that way. Whether that is one column or two is the TAD's decision.
>
> **4. FR-001 names two fields the form does not collect, not one.** §C.9 item 5 names the date of
> birth. The same sentence also makes *provider preference* mandatory. The form has no such
> question (TAD rev 10 Appendix C §C.3), and OQ-046's 2026-08-16 re-fetch found the provider
> columns exist for a later stage of the process, not for intake. Both are corrected, and the
> second is marked as beyond §C.9's list.
>
> **5. The other-funding answer does not join FR-035.** §C.9 item 4 notes that
> `rev_otherfundingstatus` touches FR-035's financial-context list. The board pack carries no
> other-funding row, and A-05 grounded FR-035 in the board pack. So A-05's basis does not reach
> it. FR-092 stores the answer, and FR-035 is unchanged.
>
> ### Resolution — 2026-09-25
>
> **APPROVED by the reviewer, Xander Lykopoulos, 2026-09-25**, with all three open questions
> answered. This was relayed to plan-agent by lead-agent, which quoted the reviewer's turn in its
> own session. Plan-agent did not see that turn directly. The reviewer's words, verbatim:
>
> > *"Agreed on this: I recommend showing the two Yes/No answers as they are, and the two
> > descriptions only in redacted form, like the narrative.
> > Agreed on consent dates on submission receival
> > Agreed on the middle name, suffix and state/province
> > Approved for development"*
>
> | Question | Answer |
> |---|---|
> | OQ-051 | Trustees see the two Equality Act Yes/No answers as they are. They see the two disability descriptions only through redacted counterparts, following the ADR-027 narrative pattern (FR-079). FR-035 now includes all four |
> | OQ-052 | The consent-date fields hold the time the submission reached the system, meaning *"when this consent reached us"* |
> | OQ-053 | Middle name, suffix and state/province are treated as hidden. Nothing is stored and nothing is built until Alex confirms the form shows them. FR-093 stays conditional |

> ### Flagged for architect-agent — TAD-stage items this amendment does not decide
>
> 1. **OQ-051's default was confirmed on 2026-09-25, so the two Equality Act answers become Art. 9 columns released
>    to trustees.** They would sit beside `rev_conditionprofile`, which needs a `secured: exception`
>    under `C-DOM-031` and an NFR-031 necessity record. TAD rev 10 §C.8 currently specifies
>    `IsSecured=1`. The two descriptions would each need a redacted counterpart and Automation #5
>    scope (FR-079 pattern).
> 2. **`rev_otherhearaboutus`'s schema description says it is *"not personal … data"*.** Held on an
>    identified applicant's record, it is personal data (Art. 6, low sensitivity; §7.1c). Being
>    unsecured is consistent with the `rev_breaklocation` precedent. The description is not.
> 3. **`knowledge/domain/business-rules.md` BR-A04 still says the age range is derived from date of
>    birth.** That is recorded as an improvement finding for improvement-agent, which owns that
>    file.

---

> ## 📌 Amendment A-09 — APPROVED 2026-10-16
>
> **Raised by:** plan-agent, 2026-10-16, strategic tier, dispatched by lead-agent after the reviewer's
> 2026-10-14 and 2026-10-16 decisions on Narrative Scrubbing (Automation #5). **Contracted scope:**
> `wbs:5.6` (redaction rules adjusted from Emily's review) and `wbs:5.1` (which free-text fields are
> redacted). **One requirement, FR-099, depends on change order `CO-009`**, which is PROPOSED and not
> approved. This amendment records that dependency. It decides no billing and no task id
> (`C-COM-002`). §10 is unaffected and restates no figure (`C-COM-008`).
>
> ### Why this session ran
>
> On 2026-10-14 the client sent two spreadsheets: an **Anonymisation Key** (gendered and relationship
> words, and the neutral word each becomes) and **four anonymised examples** showing how Emily does it by
> hand. The reviewer said *"follow the key file"*. Development-agent wrote the rules and tests from them
> (Dev Summary Iteration 8; redaction rules v0.4 §10.1). Neither this SDD's FR-026 nor any other
> requirement says gendered words are replaced, names become *They*, or the text is spell-checked. This
> amendment writes those requirements. It decides no flow, prompt, model or column. Those are the TAD's,
> and architect-agent is revising the TAD on the same decisions in parallel.
>
> ### The reviewer's decisions — verbatim (Xander Lykopoulos, relayed by lead-agent)
>
> | Date | Subject | Words |
> |---|---|---|
> | 2026-10-14 | The key | *"1. follow the key file"* |
> | 2026-10-14, 2026-10-16 | Spelling | *"Yes also add spell checking and auto correct that for readability"*; *"This feature should be added to the design, because its a requirement that came up during the meeting with Emily."* |
> | 2026-10-16 | *him* and *hers* | *"Use the clients own examples"* |
> | 2026-10-16 | First names | *"Change to the clients key and examples"* |
> | 2026-10-16 | Words the key does not list | *"Yes, add words for these: grandmother, stepson, auntie, niece, nephew, mummy, lady, and the titles Mr, Mrs, Ms and Miss."* |
> | 2026-10-16 | A second word after *and* | *"This depends... if the second word that belongs to end is identifyable information than it also needs to change."* |
> | 2026-10-16 | Three questions with no redacted copy | *"don't have to be in the trustee portal. All fields in the trustee portal right now is what the trustees use to make their decisions on."* |
> | 2026-10-16 | Hosting in Switzerland, quoting Revitalise's legal office | *"Under UK GDPR, personal data does not necessarily have to be stored in the UK. Switzerland is recognised under the UK's adequacy regulations as providing an adequate level of protection for personal data, as confirmed in the ICO's guidance. So, from an international data transfer perspective, there is no issue with the Grant Application Solution being hosted in Switzerland simply because of its location."* |
> | 2026-10-16 | *Move data across regions* (AI prompts processed in the EU Data Boundary) | *"the move data accross regions options is on in both dev and acc. This is standard."* Then, confirming: *"Yes, the AI prompt processed in EU is agreed."* Then: *"Ah, the flex routing option is disabled on tenant level. Only EU handling"* Previously read: *"Flex routing is not decided"* |
>
> ### What changes, at business level
>
> | ID | Requirement | WBS | Supersedes / relates to |
> |---|---|---|---|
> | FR-026 | Adds `[EMAIL]`; a person's name follows FR-095 instead of always `[NAME]` | 5.6 | **Amends FR-026**, original kept |
> | FR-094 | Replace the key's gendered and relationship words with its neutral words | 5.6 | New |
> | FR-095 | A person's name becomes *They* / *them* / *their*, as in the client's examples | 5.6 | New; narrows FR-026's `[NAME]` |
> | FR-096 | Also replace grandmother, stepson, auntie, niece, nephew, mummy, lady, Mr, Mrs, Ms, Miss | 5.6 | New |
> | FR-097 | Each word joined by *and* is judged on its own | 5.6 | New |
> | FR-098 | Fix the grammar a replacement breaks, so the copy reads correctly | 5.6 | New |
> | FR-099 | Correct spelling and typing slips in the redacted copy, as a separate step | **`CO-009`** | New; commercial dependency |
> | FR-100 | A correction never changes a label or brings back a replaced word | 5.6 | New; guards FR-098, FR-099 |
> | FR-101 | A gendered word left in the redacted copy sends it to Emily's review | 5.6 | New; relates to FR-029, FR-030 |
> | NFR-009, NFR-011 | Storage and backup in the UK **or Switzerland**; AI prompt processing may be in the **EU Data Boundary**; nothing outside it | 0.2 | **Amends both**, originals kept. Depends on flex routing being off: **met**, stated by the reviewer 2026-10-16 (disabled at tenant level), not measured by an agent. Previously read: *"open reviewer decision, TAD `A-R92` / `A-NS-32`"* |
> | US-025 | *I stop taking gender out by hand* | — | Traces FR-094 to FR-101 |
>
> §7.0, §7.3 and §7.7 R6 follow NFR-009. §7.1c classifies two free-text answers that were never
> classified. §9 adds OQ-054 to OQ-056 and widens OQ-048.
>
> ### Findings that shaped the text
>
> **1. Where the key and the examples disagree, the examples win.** The reviewer answered the *him* and
> *hers* question with *"Use the clients own examples"*, and the names question with *"the clients key and
> examples"*. The examples write *him* as *them* where the key says *their*. So FR-094 follows the examples
> on every point they cover, and the key everywhere else. **The examples' grammar slips are not followed**
> (*they is*, *they needs*, *them mood*). The 2026-10-14 decision asked for readable text, and FR-098
> carries it.
>
> **2. The SDD was behind a decision already made.** The reviewer added `[EMAIL]` to FR-026's labels on
> 2026-10-06 (redaction rules decision D-3, *"Agreed"*), but FR-026 still listed five labels. It is
> corrected here rather than raised as a question.
>
> **3. The reviewer's *and* answer is about identifying words, so it does not settle verb agreement on its
> own, and it does not need to.** The question asked whether *"They receive PIP and requires care"* is
> acceptable. The answer says the second word changes when it identifies someone: *my wife and son*
> becomes *my partner and child* (FR-097). The verb is a different matter, and an earlier decision settles
> it: 2026-10-14 asked for the text to be corrected *"for readability"*, and `CO-009`'s own scope places
> grammar the replacement breaks in `wbs:5.6`. So FR-098 requires the second verb to agree. It is not
> raised again. Whether the TAD's mechanism can do it is the TAD's question.
>
> **4. Spelling and substitution grammar are two requirements, not one.** FR-098 fixes only what a
> replacement broke, and is contracted under `wbs:5.6`. FR-099 corrects the applicant's own spelling, which
> `CO-009` sizes as a separate step. Keeping them apart means FR-098 can be accepted while `CO-009` is still
> open. Both run on the redacted copy only. The stored original never changes (FR-031).
>
> **5. Names: the examples settle the common case and leave four cases open.** In the examples, the one
> person a narrative is about becomes *They* and the verb agrees. The examples never show two different
> people named in one text, a doctor's name, a name next to its relationship word (*my husband Derek*), or
> a title. FR-095 states the common case. OQ-054 gives a default for the other four, so FR-026 still says
> something correct for each of them. No real name from the examples is quoted in this SDD, because they
> may be real applications.
>
> **6. The three questions with no redacted copy get none, and two of them were never classified.** The
> reviewer ruled they need not reach the trustee portal, so FR-079 is not extended to them. Two of their
> answers, *source of additional funding* and *awaiting decision from*, are free text, unsecured
> (`IsSecured=0` in `Entities/rev_application/Entity.xml`, read 2026-10-16), and in none of §7.1a to §7.1c.
> §7.1c now classifies them. The third, *benefit provider*, is already secured and classified (§7.1b).
>
> **7. Residency: the requirement moves to where the solution already is.** All three environments are on
> `crm17.dynamics.com`, which Microsoft maps to Switzerland (measured 2026-10-05). **The entity extractor runs
> in Switzerland; AI prompts do not.** Per Microsoft Learn, as cited in TAD `ADR-075`, every prompt model in the
> Switzerland geography is *"GA (cross-geo)"*, and with *Move data across regions* allowed a Swiss environment's
> prompts are processed by Azure OpenAI in the EU Data Boundary. The reviewer says that setting is on in DEV
> and TST/ACC (*"This is standard."*), and agreed the EU processing: *"Yes, the AI prompt processed in EU is agreed."* Revitalise's legal office says Swiss hosting is no transfer problem under
> UK GDPR, because Switzerland holds UK adequacy. NFR-009 now requires storage and backup in the UK or
> Switzerland, allows prompt processing inside the EU Data Boundary, and allows nothing outside it. The EEA is
> also covered by UK adequacy regulations. That is context, **not verified by plan-agent**, and the legal
> office's statement names only Switzerland. **Flex routing**, which can process prompts outside the EU Data
> Boundary at peak load, has to be off for NFR-009 to hold. **It is off:** the reviewer, 2026-10-16,
> *"Ah, the flex routing option is disabled on tenant level. Only EU handling"*. That is the reviewer's statement, not an agent measurement. Previously read: *"Whether it is
> off is an open reviewer decision (TAD `A-R92`, `A-NS-32`), so NFR-009 records the dependency and decides
> nothing."* Each
> component's location still has to be verified and recorded; that has been done for the environments, and
> not yet for the signature and finance services. The DPIA and RoPA still say UK only, which is a recording
> task under OQ-048, not a new question.
>
> ### Resolution — 2026-10-16
>
> **APPROVED by the reviewer, Xander Lykopoulos, 2026-10-16**, relayed to plan-agent by lead-agent from the
> reviewer's own turn: *"Approved for requirements Amendment A-09"*. The reviewer was told that approval accepts the open questions' defaults unless
> changed, and changed none, so **OQ-054, OQ-055 and OQ-056 are adopted at their proposed defaults.** In the same
> turn: *"CO-009 Approved with unbilled tag. Features always expand a bit during development and this one is within reasonable limits."* `CO-009` is therefore approved and unbilled. commercial-agent records the billing; this SDD decides none.
>
> ### Flagged for architect-agent — TAD-stage items this amendment does not decide
>
> 1. **Where FR-094 to FR-101 run, and how.** TAD rev 21's neutral-term design was returned by the
>    reviewer as too large. This SDD names no mechanism. FR-098 requires a second verb after *and* to agree,
>    which rev 21's word-list design recorded as a limit it cannot meet.
> 2. **FR-099 is a separate step on the redacted copy only** (reviewer: *"I think it's better to keep it
>    separated"*). NFR-009 now allows prompt processing in the EU Data Boundary, which removes the residency block on
>    the prompt stage. Flex routing is disabled at tenant level (reviewer, 2026-10-16: *"Ah, the flex routing option is disabled on tenant level. Only EU handling"*), which bears on
>    TAD `A-R92` and `A-NS-32`. Previously read: *"provided flex routing is off (TAD `A-R92`, `A-NS-32`)"*.
> 3. **`rev_otherfundingsource` and `rev_awaitingdecisionfrom` are unsecured free text.** They are classified
>    Personal (Art. 6) in §7.1c on the `rev_breaklocation` precedent. Free text can carry health detail, so
>    whether to secure them is the TAD's call against C-DOM-001.
> 4. **The redaction rules' kinship word list is extendable by Emily** (rules §7c). Whether the new words of
>    FR-096 join that list or the fixed floor is the TAD's.

---

> ## 📌 Amendment A-10 — APPROVED 2026-10-19 (revision 2)
>
> **Raised by:** plan-agent, 2026-10-19, strategic tier (financial eligibility data), dispatched by
> lead-agent on the reviewer's request of the same day. **Revised the same day** on the reviewer's
> feedback (Xander Lykopoulos, 2026-10-19, relayed by lead-agent); see *Revision 2* below. **Contracted
> scope:** `wbs:2.4` (*"compare score to threshold from Settings, set status (Auto-pass/Borderline/Auto-reject),
> check income ceiling"*) and `wbs:2.7` (*"Adjust flow, views, and Settings based on Emily's feedback"*),
> per `contract/wbs.json`. The reviewer confirmed it is not billable beyond the contract and asked for it
> during the build of the scoring flow, so no change order is raised (`C-COM-002`). §10 is unaffected and
> restates no figure (`C-COM-008`).
>
> ### Revision 2 — what the reviewer's feedback changed (2026-10-19)
>
> | # | Change | Where |
> |---|---|---|
> | 1 | The override of Emily's EF-31 and EF-32 is a **reviewer decision**, not an open item | Finding 1 |
> | 2 | Amount limits split by break type: **£100** for Day trips or outings and Activity or Experience; **£500** for Holiday accommodation, Respite Care Facility stay and Other | FR-102, AC-14, examples 4, 14, 15 |
> | 3 | **Every** auto-reject rule's parameter is a setting the process owner changes without touching the flow. Where the form fixes the figure, the setting is an on/off switch | FR-017, FR-103, FR-104, Finding 8 |
> | 4 | The income rule applies only when the applicant does **not** receive means-tested benefits. **Employment status is not read** | FR-015, FR-016, examples 6 to 8, 16, 17, Findings 2 to 4 |
> | 5 | The employment-status carve-out and the approval line's sign-off for it are **withdrawn** | Finding 3, architect item 1, approval line |
> | 6 | Trustees never see the reason: **FR-106 and the securing item are withdrawn**, the classification rows stay | FR-106, AC-19, Finding 6, §7.1d, architect item 3 |
> | 7 | Round 4 impact re-run: **0 of 63** rejected on amount (was 5), **4 of 63** on income (was 0) | Findings 1 and 2 |
>
> Unchanged from revision 1, as the reviewer confirmed: savings over £6,000 rejects alone for every
> applicant, and a missing scored answer gives Under Review with no eligibility rule applied (FR-022).
>
> ### Why this session ran
>
> Today the scoring flow sets Auto-reject for two reasons only: a score at or below the knockout
> threshold, and funding from Revitalise within the last 12 months. The income check records a flag and
> rejects nothing. The amount requested, the type of break, the exceptional-funding tick and the savings
> answer are not read at all (read 2026-10-19 in
> `Workflows/REVScoringCalculateAndFlag-8F1C2A44-1002-4B7A-9E21-0A1B2C3D4E02.json`, actions
> `Derive_income_flag`, `Derive_status`, `Derive_autoreject_reason`). The reviewer wants three financial
> eligibility rules to reject as well, with every reason written where Emily reads it.
>
> ### The reviewer's decisions — verbatim (Xander Lykopoulos, 2026-10-19, relayed by lead-agent)
>
> | Subject | Words |
> |---|---|
> | The rule | *"Every one of the following SHALL set status Auto-reject (4) and write a plain-language reason into rev_autorejectreason (shown on the application main form), so the grant admin (Emily, process owner) does not have to hunt for why. When several rules fire, ALL reasons are listed, not just the first."* |
> | Amount (revision 2, in force) | *"That is correct. This overrides that decision."* Day trips or outings and Activity or Experience: over £100. Holiday accommodation, Respite Care Facility stay and Other: over £500. Over the limit (strictly greater) with exceptional funding not ticked: Auto-reject. Only `rev_amountrequested` is compared, not `rev_additionalamountrequested` (revision 1, unchanged). |
> | ~~Amount (revision 1)~~ | ~~*"rev_amountrequested > 500 GBP where rev_breaktype = 1 (Holiday accommodation) and rev_exceptionalfundingrequested is not ticked. For every other break type (2 Day trips, 3 Activity/Experience, 4 Respite Care Facility stay, 5 Other): rev_amountrequested > 100 GBP and exceptional funding not ticked."*~~ Superseded by revision 2 for break types 4 and 5. |
> | Income (revision 2, in force) | *"The flow should only look at income band when the applicant has not receiving means tested benefits. Employment status doesn't have to be checked."* |
> | ~~Income (revision 1)~~ | ~~*"applicant is employed (rev_employmentstatus 1 full-time or 2 part-time) AND income band is above the configured IncomeCeiling (25,000; bands 3 and 4) -> reject."*~~ Superseded by revision 2. |
> | Savings | *"rev_savingsover6000 = Yes rejects on its own, for every applicant regardless of employment or benefits."* Unchanged in revision 2. |
> | Prior funding, score | *"Funded before within 12 months (already built) -> reject, as today."* *"Score at or below KnockoutThreshold (already built) -> reject, as today."* |
> | Missing scored answer | Keep FR-022: Under Review, no automated outcome. The eligibility rules do not fire in that path. Unchanged in revision 2. |
> | Human check | Every auto-reject is checked by the grant admin, who agrees or overrides it (FR-018). |
> | Configurable (revision 2) | *"These thresholds should be in the settings table, so that the process owner can change them. Just like income ceiling is on the settings table. Do the same for the other auto-reject reasons."* |
> | Trustee exposure (revision 2) | *"Trustees don't see these fields in the portal. They don't have the link to the admin app, that app is not shared with their security role."* |
>
> ### What changes, at business level
>
> | ID | Requirement | WBS | Supersedes / relates to |
> |---|---|---|---|
> | FR-014 | Auto-reject when **any** of five rules applies; otherwise Borderline or Auto-pass by score, as today | 2.4 | **Amends FR-014**, original kept |
> | FR-015 | An applicant not on means-tested benefits whose income band is above the ceiling is rejected; the flag stays | 2.4 | **Amends FR-015**, original kept; answers half of OQ-003 |
> | FR-016 | No change: the income rule reads no disability, health or employment answer | 2.4 | **Annotates FR-016** (revision 1's employment scoping withdrawn) |
> | FR-017 | Every auto-reject rule's parameter is a setting Emily can change | 2.4, 2.7 | **Amends FR-017**, original kept |
> | FR-022 | No eligibility rule fires when a scored answer is missing | 2.4 | **Annotates FR-022** |
> | FR-102 | Amount requested over the limit for the break type, no exceptional request: reject | 2.7 | New |
> | FR-103 | Savings over £6,000: reject, while the rule is switched on | 2.4 | New |
> | FR-104 | Funded by Revitalise within the last 12 months: reject, while the rule is switched on. Built, never written down | 2.7 | New; records built behaviour |
> | FR-105 | Every reason that fired is written, in plain language, where Emily reads the case | 2.7 | New; widens the reason already built |
> | ~~FR-106~~ | ~~The reason text is shown to staff only, never to a trustee~~ **WITHDRAWN, revision 2** (reviewer ruling, Finding 6) | — | Identifier stays allocated, with no force |
> | US-006 | AC-4, AC-5 and AC-7 amended; AC-13 to AC-18 and AC-20 added; ~~AC-19~~ withdrawn | — | Traces the above |
>
> §7.1d classifies the reason text. §7.4 and OQ-005 widen the DPO's automated-decision question to the
> new reasons. OQ-003 is half answered. FR-020 and FR-021 are unchanged: every new reason sets Auto-reject,
> so those cases leave the active list and are counted in the daily summary as they are today.
>
> ### The rules on worked examples
>
> All examples use the default settings of Finding 8: knockout threshold 20, borderline band 21 to 30,
> income ceiling £25,000, both switches on. The knockout values are provisional in DEV and TST/ACC (OQ-001).
> *Not on benefits* means the applicant answered anything other than Yes to receiving means-tested benefits.
>
> | # | Application | Status | Reason text Emily reads |
> |---|---|---|---|
> | 1 | Holiday accommodation, £500 requested, no exceptional tick, score 45 | Auto-pass | *(empty)*. £500 is not over £500 |
> | 2 | Holiday accommodation, £650, no exceptional tick, score 45 | Auto-reject | *Amount requested £650.00 is over the £500 limit for Holiday accommodation, and no exceptional funding was requested.* |
> | 3 | Holiday accommodation, £650, exceptional ticked, additional amount £150, score 45 | Auto-pass | *(empty)*. The tick lifts the limit; the additional amount is never compared |
> | 4 | Respite Care Facility stay, £400, no exceptional tick, score 45 | Auto-pass | *(empty)*. £400 is within the £500 limit. *Revision 1 rejected this against £100.* |
> | 5 | Day trip, £100, no exceptional tick, score 25 | Borderline | *(empty)*. £100 is not over £100 |
> | 6 | Not on benefits, in work full-time, income £25,000 to £34,999, score 45 | Auto-reject | *The household income band (£25,000 to £34,999) is above the income ceiling of £25,000.* |
> | 7 | Not on benefits, retired, income over £35,000, score 45 | Auto-reject | *The household income band (Over £35,000) is above the income ceiling of £25,000.* Employment is not read. *Revision 1 passed this.* |
> | 8 | Not on benefits, income £15,000 to £24,999, score 45 | Auto-pass | *(empty)*. The band's top, £24,999, is within £25,000 |
> | 9 | Receives means-tested benefits, so the form asked no income, employment or savings question, score 45 | Auto-pass | *(empty)*. The income rule does not apply, and a blank savings answer is not a Yes |
> | 10 | Savings over £6,000 Yes, not on benefits, income under £15,000, score 45 | Auto-reject | *The applicant has savings over £6,000.* |
> | 11 | Savings Yes, Holiday accommodation £650 without tick, funded 8 months ago, score 18 | Auto-reject | Four lines, in this order: amount; savings; *Received funding from Revitalise before, and that previous funding was within the last 12 months.*; *Circumstance score 18 is at or below the auto-reject threshold (20).* |
> | 12 | Savings Yes, one wellbeing answer missing | Under Review | *(empty)*. FR-022 applies, and no eligibility rule fires |
> | 13 | Example 10, then Emily overrides to Eligible for Panel | Eligible for Panel | Unchanged: *The applicant has savings over £6,000.* Her override is recorded separately (FR-018) |
> | 14 | Respite Care Facility stay, £520, no exceptional tick, score 45 | Auto-reject | *Amount requested £520.00 is over the £500 limit for Respite Care Facility stay, and no exceptional funding was requested.* |
> | 15 | Activity or Experience, £120, no exceptional tick, score 45 | Auto-reject | *Amount requested £120.00 is over the £100 limit for Activity or Experience, and no exceptional funding was requested.* |
> | 16 | Not on benefits, no income band given, score 45 | Auto-pass | *(empty)*. The income flag records *not stated*, as it does today; a band that is not given is not above the ceiling |
> | 17 | Receives means-tested benefits, and an income band of Over £35,000 is on the record anyway, score 45 | Auto-pass | *(empty)*. The income rule does not apply to a benefits claimant |
> | 18 | Example 10, after Emily switches the savings rule off | Auto-pass | *(empty)*. A switched-off rule never applies and writes no reason |
> | 19 | Emily changes the Day trips or outings limit to £150; a £120 day trip, no exceptional tick, score 45 | Auto-pass | *(empty)*. No flow is edited |
>
> ### Findings that shaped the text
>
> **1. The amount limits override two earlier client positions, by reviewer decision.** Emily's September
> feedback set £500 for *"holidays/respite"* (`docs/plans/emily-review-feedback-2026-09-plan.md`, EF-31)
> and, confirmed 2026-09-18, *"Other takes no automatic threshold and is flagged for manual review"*
> (EF-32). Both were a flag, not a rejection. The reviewer ruled on 2026-10-19: *"That is correct. This
> overrides that decision."* Respite keeps EF-31's £500; Other now has a £500 limit; and going over it
> rejects. Measured on the Round 4 board pack (`docs/Import/3. Round 4 - Individual Applications.pdf`,
> 63 applications, re-read 2026-10-19): **0 of 63 would be auto-rejected on amount.** Every request above
> its limit carried an exceptional amount. The 3 respite stays (£400, £500, £500) and 2 Other (£500, £500)
> that revision 1's £100 limit rejected are all within £500, and the 3 day trips sit exactly on £100. The
> pack shows the exceptional amount, not the tick, so a blank amount was read as *not ticked*.
>
> **2. The income rule now rejects 4 of the 6 Round 4 applicants it can reach.** 57 of 63 receive
> means-tested benefits, so the income rule does not apply to them (and the live form asks them no income,
> employment or savings question, EF-28b). Of the other 6, 4 have a band above £25,000 and **4 of 63 are
> rejected on income**: one retired, and three who answered that they cannot work because of disability,
> health or caring. One of the four also answered savings Yes, so **1 of 63 is rejected on savings**, the same
> applicant. **In all, 4 of 63 are auto-rejected on financial grounds**, against 6 in revision 1. This is
> the rule as decided; it is recorded so approval is given with the numbers in view, not raised as a question.
>
> **3. WITHDRAWN, revision 2: the scoring flow does not read the employment status.** The reviewer
> decided employment status is not checked, so no carve-out in the special-category register is needed
> and C-DOM-030 holds as it stands today. Revision 1 read: ~~3. The income rule reads a special-category
> column, scoped so the health answer has no effect of its own. `rev_employmentstatus` is classified Art. 9
> (§7.1a, D-1), because one of its five answers is "No, unable to work due to disability/health/caring
> responsibilities". The column is barred from the scoring flow (C-DOM-030 in
> `constraints/domain/domain-constraints.md`). The rule only asks in work (answers 1 and 2) or not:
> answers 3, 4 and 5 and a blank all produce the same result. So the disability answer has no effect that
> retired or other reason would not also have. This needs a scoped carve-out in the special-category
> register, of the same kind already approved for benefit status (`rev_receivesbenefits`, reviewer
> sign-off 2026-09-18). Approving this amendment is that sign-off, and the approval line says so.~~
>
> **4. The income rule uses the existing income flag, which already takes benefits into account.** The flag
> records *qualifies on benefits* whenever the benefits answer is Yes, and *above the ceiling* only for
> anyone else whose band's top is above the ceiling; a band that is not given is recorded as *not stated*
> (read 2026-10-19, `Derive_income_flag`). So *"reject when the flag says above the ceiling"* is exactly the
> reviewer's rule: benefits Yes never rejects on income, and no band never rejects. The benefits answer is
> special category, and the scoring flow may read it only to set this flag (`rev_receivesbenefits` gate
> exception, reviewer sign-off 2026-09-18). Reading the flag keeps that exception's scope intact. The
> income reason therefore names only the band and the ceiling, never benefits or employment.
>
> **5. The 12-month prior-funding rule was built with no requirement behind it.** It came from Emily's
> feedback (EF-34, `wbs:2.7`) and is in the flow, but no FR in this SDD stated it. FR-104 writes it down
> as built. The reason column itself (EF-45) is built, on the main form's Casework tab, and holds one
> reason; FR-105 makes it hold all of them.
>
> **6. WITHDRAWN, revision 2: the reason text needs no securing, by reviewer ruling.** The reviewer ruled that trustees do not see these columns: *"They don't have the link to the admin app, that
> app is not shared with their security role."* Revision 2 also removed the cause: with employment not read,
> no reason repeats a secured answer (Finding 4). Checked 2026-10-19: neither trustee portal code app
> (`src/code-apps/trustee-review-portal`, `trustee-review-portal-cards`) names `rev_autorejectreason` or
> `rev_scoringaudit` in any screen or query; both appear only in the generated table models, which list
> every column of the table. The trustee role does read the application table, which the portal needs, so
> the ruling rests on no trustee surface showing the text. FR-106 is withdrawn; §7.1d keeps the rows.
> Revision 1 read: ~~6. The reason text repeats a secured answer in an unsecured column. Example 6's reason
> contains the employment answer, which trustees must never see (FR-078, D-1). `rev_autorejectreason` and
> `rev_scoringaudit` are both `IsSecured=0` (read 2026-10-19). An application Emily overrides into the
> panel round (example 13) carries its reason with it. FR-106 keeps the reason from trustees; §7.1d
> classifies the column. How it is secured is the TAD's.~~
>
> **7. The automated-decision question now covers financial rejections, and the reviewer has described a
> human check.** OQ-005 asked whether rejection *at the threshold* stands. It now also covers amount,
> income, savings and prior funding. The reviewer stated that Emily checks every auto-reject and agrees
> or overrides it. That is the stronger form §7.4 describes. Only an override leaves a record today; an
> agreement leaves none. OQ-005 stays the DPO's, and is re-dated to an event.
>
> **8. Every rule has a setting; where the form fixes the figure, the setting is an on/off switch.** The
> savings question is a Yes/No answer to *"over £6,000"* and the prior-funding question a Yes/No answer to
> *"more than 12 months ago"*. The flow never sees an amount or a date, so neither figure can be a setting:
> changing it means changing the form (BR-S11). What Emily can change for those two rules is whether they
> apply. The defaults follow the reviewer's decision that both reject.
>
> | Rule | What the process owner changes | Default |
> |---|---|---|
> | Amount (FR-102) | One limit per type of break | Holiday accommodation £500; Day trips or outings £100; Activity or Experience £100; Respite Care Facility stay £500; Other £500. Seeded in all three environments |
> | Income (FR-015) | The income ceiling, as today | £25,000 in DEV and TST/ACC; PRD per OQ-003 |
> | Savings (FR-103) | On or off | On |
> | Prior funding (FR-104) | On or off | On |
> | Score (FR-014) | The knockout threshold, as today | 20, provisional (OQ-001) |
>
> A missing setting stops the run with no outcome and alerts, as a missing setting does today.
>
> ### Resolution — 2026-10-19
>
> **APPROVED by the reviewer, Xander Lykopoulos, 2026-10-19**, revision 2, relayed to plan-agent by lead-agent
> from the reviewer's own turn: *"Approved"*. The approval covers the requirement text as revision 2 states it,
> the setting defaults of Finding 8 and the four worked-example sets the rules are written on. Three things it
> does not do:
>
> - It does not answer **OQ-003**'s remaining question. £25,000 for PRD still needs the board's confirmation;
>   PRD stays unseeded until then, and the event is the first PRD seed of the income ceiling.
> - It does not answer **OQ-005**. The DPO decision, now covering the amount, income, savings and prior-funding
>   rules, is still due before the first PRD deploy of the scoring flow carrying FR-102 to FR-105.
> - It authorises no read of `rev_employmentstatus`. Revision 2 reads no employment answer, so no
>   `gate_exception` is needed for it.
>
> The reviewer's statement that this work is inside `wbs:2.4` and `2.7` and not billable stands; commercial-agent
> records the billing. The TAD items below go to architect-agent.
>
> ### Flagged for architect-agent — TAD-stage items this amendment does not decide
>
> 1. **WITHDRAWN, revision 2: employment is not read.** Instead, **build the income rule on the income
>    flag's *above the ceiling* value**, not by reading the benefits answer again, so `rev_receivesbenefits`
>    stays inside its existing scoped gate exception (Finding 4). Revision 1 read: ~~The special-category
>    carve-out for `rev_employmentstatus` (Finding 3): a `gate_exception` in
>    `constraints/domain/special-category-register.yml` with its own build step, on the
>    `rev_receivesbenefits` precedent, so the scoring flow can read the column for the income rule only.~~
> 2. **How the settings are held** (FR-017, Finding 8): five amount limits by break type (five settings, or
>    one map) and two on/off switches. Either form meets FR-017. Seed the defaults in all three environments;
>    the reviewer gave every value. The flow's check on the number of setting rows it reads grows with them.
> 3. **WITHDRAWN, revision 2** (reviewer ruling, Finding 6). Revision 1 read: ~~Securing the reason text
>    (FR-106, §7.1d): `rev_autorejectreason`, and `rev_scoringaudit`, which repeats it, must be unreadable
>    by the trustee role.~~
> 4. **Reason length.** Five reasons fit in the column's 1,000 characters at the wording in the examples.
>    Confirm against the final wording.
> 5. **Re-scoring and override.** Example 13 requires an override to leave the reason in place. Whether a
>    later re-score rewrites it is the TAD's, so long as the text always matches the status in force.

---

> ## 📌 Amendment A-11 — APPROVED 2026-10-19
>
> **Raised by:** plan-agent, 2026-10-19, standard tier, dispatched by lead-agent after the reviewer approved TAD
> rev 25 (`ADR-078`) the same day and asked for the SDD to follow. **Contracted scope:** `wbs:5.3`, `5.4`
> and `5.6`. **No new ids:** FR-029, FR-030, FR-095, NFR-017, NFR-018 and US-007 AC-4 and AC-5 are amended in
> place, and two acceptance criteria join US-025. The id-allocation declaration above is unchanged.
>
> ### The reviewer's decision, verbatim
>
> *"All records should be checked by the process owner regardless. So, we don't need that setting at all."*
> (Xander Lykopoulos, 2026-10-19, relayed by lead-agent.) In the same turn he approved TAD rev 25.
>
> ### What changes, at business level
>
> | ID | Requirement | WBS | Supersedes / relates to |
> |---|---|---|---|
> | FR-030 | The process owner reviews and releases **every** redacted narrative, flagged or not; nothing is released automatically | 5.4 | **Amends FR-030**, original kept |
> | FR-029 | The confidence threshold flags a narrative for her attention; it no longer decides release | 5.3, 5.4 | **Amends FR-029**, original kept |
> | NFR-017, NFR-018 | Follow FR-029 and FR-030: every redaction is reviewed, and the threshold only orders her attention | 5.4 | **Amends both**, originals kept |
> | US-007 AC-4, AC-5 | Follow FR-029 and FR-030 | 5.4 | **Amends both**, originals kept |
> | FR-095 | The applicant's own name keeps `[NAME]`; a name right after a relationship word is dropped even when other people are named | 5.6 | **Amends FR-095**, original kept |
> | US-025 AC-11, AC-12 | One example each for the two FR-095 changes | 5.6 | New criteria |
>
> §1's scope table, the OQ-054 resolution row, Appendix A and the Approval section follow.
>
> ### Findings that shaped the text
>
> **1. The threshold keeps a job; it loses the one that made it a gate.** Under FR-029 as approved, a narrative
> above 85% could reach trustees without a person looking at it. The reviewer has ruled that no narrative does.
> The threshold stays, because it still tells Emily which narratives the redaction was least sure about, and the
> reviewer did not ask for it to go (*"we don't need that setting at all"* names the auto-release setting, which
> TAD rev 25 retires). NFR-019 still lets her change the threshold without a developer.
>
> **2. FR-030 is no longer a response to a flag.** It said *"WHEN a narrative has been flagged"*. It now applies
> to every redacted narrative. FR-079's withheld state therefore holds for every record until she releases it,
> as it already did for a record she had not released.
>
> **3. The applicant's own name was not covered, and the built rule had already handled it.** FR-095 says a name
> becomes *They*. For the writer's own name that is wrong: *I am Sam* would read *I am they*. The DEV run of
> 2026-10-19 produced exactly that. FR-095 now keeps `[NAME]` for a name the writer gives for themselves (*I am
> …*, *I'm …*, *my name is …*). TAD rev 25 `ADR-076`'s name rules already say so; this brings the SDD level with
> them, so the architecture is not ahead of the requirement.
>
> **4. The relationship word wins even when other people are named.** FR-095 said a name beside its relationship
> word is dropped, but its last sentence kept `[NAME]` for any name in a text with two or more people, so the
> two statements disagreed for *my husband Derek and my sister Ann*. The reviewer's 2026-10-16 ruling, *"the word
> husband is leading in this pattern"*, settles the order: the relationship rule comes first. This is a
> correction of a contradiction inside FR-095, not a new decision.
>
> **5. One default is stated for a case the decision leaves open (OQ-054, case (e)).** When the writer gives
> their own name and one **other** person is named, does that other person become *They*? **Default, applied
> until answered:** the writer's own name is not counted as another person, so the one other named person still
> becomes *They*. Example: *"I am Sam and Pat helps me"* becomes *"I am [NAME] and they help me"*. The
> alternative is to keep `[NAME]` for Pat because two names are present (*"I am [NAME] and [NAME] helps me"*). The default follows the direction of
> the reviewer's examples, where the one person a narrative is about becomes *They*. Whether the mechanism can
> tell the writer's name from another person's is the TAD's question, not this SDD's, as in A-09.
>
> **6. Emily's workload.** US-007 promises *"three to four hours per board cycle"* saved. Checking every
> narrative, rather than only flagged ones, spends some of it. The reviewer made the decision knowing it; the
> figure in §1 and US-007 is the original sizing and is **not restated or re-sized here**. Whether the saving
> still stands is for Emily's first live cycle to show.
>
> **7. Data and contract.** No column, access rule or lawful basis changes, so §7.1 and §7.1c stand (C-DOM-001,
> C-DOM-002). The check on every record adds a control rather than removing one. `wbs:5.4`'s flag and review view are
> still delivered, so no change order is raised here. Whether anything follows from the review step now covering
> every record is commercial-agent's to decide; this SDD decides none.
>
> ### Resolution
>
> **APPROVED 2026-10-19.** Xander Lykopoulos, relayed by lead-agent, verbatim: *"That is correct... the assumed default is the desired output. Approved."* Finding 5's default is therefore **confirmed, not assumed**: *"I am Sam and Pat helps me"* becomes *"I am [NAME] and they help me"*, with other people counted without the writer. OQ-054 case (e) is resolved. Wherever this amendment's text says PROPOSED, read APPROVED 2026-10-19.


> ## 📌 Amendment A-12 — APPROVED 2026-10-20
>
> **Raised by:** plan-agent, 2026-10-20, standard tier, dispatched by lead-agent. **Contracted scope:** `wbs:8.6`, a
> change-order task that exists only in `contract/change-orders/CO-010.md` (scope accepted **unbilled** by the
> reviewer on 2026-10-20, `CE-0021`, `EX-012`). `wbs:8.6` is not in `contract/wbs.json`. **New ids:** FR-107 to
> FR-111, US-026, OQ-057 and OQ-058, declared above. No existing requirement is amended; FR-048 and FR-050 already
> depend on the date this amendment makes someone write.
>
> ### The reviewer's decision, verbatim
>
> *"Yes, this flow needs to be build. 2- 4 hours of work on a new WBS 8.6. Non-billable. Because I thought this was
> already inlcuded."* (Xander Lykopoulos, 2026-10-20, relayed by lead-agent, as recorded in `CO-010`.) The decision
> accepts the scope and the size. It supplies no requirement text, and that is what this amendment adds.
>
> ### What changes, at business level
>
> | ID | Requirement | WBS | Supersedes / relates to |
> |---|---|---|---|
> | FR-107 | Recording a payment as the final payment sets the grant's final payment date | 8.6 | New; the start of FR-048's six-year period |
> | FR-108 | The same event moves the application to "Grant Paid" | 8.6 | New; the status §7.6 keys retention to |
> | FR-109 | A payment that is not final changes nothing, and saving the same payment again changes nothing | 8.6 | New |
> | FR-110 | Removing or correcting the final mark puts the grant and application back as they were | 8.6 | New |
> | FR-111 | A final payment that cannot be applied is reported, never dropped | 8.6 | New |
> | FR-112 | Marking a payment final sets its status to Issued | 8.6 | New, reviewer-directed revision 2026-10-20 |
> | FR-113 | The same event moves the grant's own status to "Paid" | 8.6 | New, reviewer-directed revision 2026-10-20 (second) |
>
> ### Findings that shaped the text
>
> **1. The gap is a compliance gap, not an automation gap.** FR-048 deletes a paid grant's full record six years
> from its final payment date, and §7.6 starts the period at status "Grant Paid". Finance's payment form (`wbs:8.3`,
> FR-150 to FR-154) records that a payment is final and tells nothing else. Today the date is written by no one, so
> for every paid grant the six years never begin, and the record is neither deleted when it should be nor, if a
> person forgets, protected for as long as the Charities Act 2011 duty requires. TAD §5.11 and risk A-R56 carry
> the same fact. This amendment is the requirement text those two were waiting for.
>
> **2. Which date starts the clock is a decision, and it is stated.** The regulation says *"from final payment
> date"* (`knowledge/domain/regulations.md`, retention schedule). A payment can be entered some days after it was
> made. FR-107 therefore uses the date the payment itself carries, not the day finance typed it in. OQ-057 holds
> the default for confirmation.
>
> **3. The wrong date errs in a known direction.** A date that is too early deletes a financial record before the
> duty allows. A date that is too late keeps personal data longer than the schedule allows. FR-109 therefore takes
> the **latest** final payment when a grant has more than one, and FR-110 clears the date rather than leaving a stale
> one, so a record is never left holding a date no payment supports.
>
> **4. A correction must be able to undo the start of the clock.** Finance ticks the final box by mistake. Without
> FR-110 the clock starts and the application reads "Grant Paid" for a grant still owed money. FR-110 reverses both
> effects, and only when no other final payment supports them.
>
> **5. The duplicate-payment re-check is excluded.** TAD §5.11 lists the check among three things this flow "would
> have" done: the second call site of FR-023, before a payment is issued. `CO-010` does not add it. Its
> verification stays with `wbs:8.5`. If it is wanted in this flow it needs a separate reviewer decision and a
> re-price. **Nothing in FR-107 to FR-111 performs it.**
>
> **6. The change order's other limits are kept.** FR-107 and FR-108 are the two writes `CO-010` names; FR-109 and
> FR-110 define when they do and do not happen; FR-111 is the logged-alert case `CO-010` allows. `CO-010` says the
> high end of its hours rises if a retry or missing-grant case needs more than a logged alert, and FR-111 stops at
> the alert for that reason. **FR-111 asks for no retry.** Hours are `CO-010`'s to cite; this SDD restates none.
>
> ### Open questions raised
>
> OQ-057 and OQ-058 in §9, each with a default and an example, each dated against the event that makes it
> load-bearing.
>
> ### Resolution
>
> **APPROVED 2026-10-20.** Xander Lykopoulos (relayed by lead-agent): *"Approved. OQ-057: Payment date. OQ-058: Correct.
> All payments marked final."* Both open questions are answered, both at their defaults, so FR-107 to FR-111 stand as
> written. Previously read: *"PROPOSED, awaiting review."* See the Approval section and OQ-057 and OQ-058 in §9.
>
> ### Reviewer-directed revision, 2026-10-20 (after the architect's TAD rev 28 / ADR-081 questions)
>
> **Recorded as approved. The gate is not re-opened.** The reviewer answered the architect's three decisions, verbatim
> (Xander Lykopoulos, relayed by lead-agent): *"1. Agreed. 2. For now use the same as the process owner Emily. At the
> moment that is a combined role. but in the future probably separated. During testing this can be set to Janine.
> 3. Make payment date required when final payment is set. The the flow can set the payment status to issued.
> APPROVED"*
>
> **Answer 3 changes two business rules approved above.**
>
> | | Previously read | Now reads |
> |---|---|---|
> | (a) FR-107, OQ-057 | *"If the payment carries no date, the day it is recorded is used."* | A payment cannot be saved as final on the Payment form without a payment date (an undated final payment from any other route is ignored and reported, FR-107, FR-111). The fallback is withdrawn, so no retention date ever rests on the day of typing. The date stays the payment's own date (AC-2 is unchanged). |
> | (b) new FR-112 | Marking final changed only the grant and the application. | Marking a Pending payment final also sets its status to Issued, in the same event. A new id was needed because no row in FR-107 to FR-111 owns the payment's own status. |
>
> **How (b) meets FR-110 and OQ-058.** (1) *Pending marked final* (OQ-058): still counts, and now becomes Issued, so
> finance no longer updates a second field; OQ-058's answer stands. (2) *Already Issued or Cleared:* left as it is, so
> the flow never moves a payment backwards from Cleared. (3) *Cancelled:* never counts as final, stays Cancelled and
> is reported under FR-111. (4) *Final mark removed, or payment cancelled (FR-110):* the grant and application are put
> back as before, but the payment's status is **not** reverted. The flow cannot know whether the money moved, so
> it never guesses. OQ-059 was raised because the reviewer's answer was silent on it, and is now answered: *"No. payment final means final."* The payment stays Issued.
>
> **Answers 1 and 2 are architecture-level and change no requirement.** The finance alert of FR-111 goes to the process
> owner (Emily, a combined role for now, likely to be separated later), and in testing to Janine. FR-111 already says
> "finance and the process owner" without naming a person; the TAD records who. Nothing else here depends on them.
>
> **New id and question.** FR-112 and OQ-059, declared above. OQ-059 is **resolved**: *"No. payment final means final."* (Previously read: *"pending"*, due before `wbs:8.6` development encodes FR-110's reversal.)
> No hours are restated; `CO-010` is unchanged and its limit on hours is still `CO-010`'s to cite.

### Second reviewer-directed revision, 2026-10-20: the grant's own status moves to "Paid"

**Recorded as approved. The gate is not re-opened; no conflict found with FR-107 to FR-112.** Reviewer (Xander Lykopoulos, relayed by lead-agent), verbatim: *"Obviously the final payment should change the grant status as well."* The architect had flagged this as outside `CO-010` (*"a paid grant's own status still reads Acceptance Signed"*). The reviewer has now put it in scope; it stays under `wbs:8.6`, `CO-010`, unbilled, and no hours are restated.

| | Previously read | Now reads |
|---|---|---|
| FR-113 (new) | A final payment changed the grant's date (FR-107), the application's status (FR-108) and the payment's status (FR-112). The grant's own status was not touched and read "Acceptance Signed" for ever. | The same event also moves the grant's own status from "Acceptance Signed" (3) to "Paid" (4). Any other grant status is left alone and reported under FR-111. FR-110's reversal returns a "Paid" grant to "Acceptance Signed". |

**Two statuses, not one.** The *application* status "Grant Paid" (FR-108) and the *grant* status "Paid" (FR-113) are separate fields. The grant statuses are 1 Awarded, 2 Acceptance Issued, 3 Acceptance Signed (2 and 3 are set by the acceptance flows, FR-045) and 4 Paid. Each rule runs on its own condition, so a Withdrawn application can still have its grant moved to Paid, and an Approved application can have its application moved while the grant is reported.

**No open question remains:** OQ-060 (a final payment recorded before the acceptance is signed) is resolved, *"Keep default."* New ids: FR-113, OQ-060, declared above. AC-16 to AC-19 are added to US-026.

**Amendment A-12, third reviewer-directed revision, decision "4" — Reviewed by:** Xander Lykopoulos  **Date:** 2026-10-20  **Response:** `APPROVED` (verbatim: *"4"*), relayed by lead-agent. The "date required when final" rule and the "Pending becomes Issued when final" behaviour move from the form-only rule and the flow into one table-level business rule on Payment that applies to every save (form, API, flow). Wording aligned: FR-107 (no undated final payment by any route; the form-only carve-out is removed, the flow's ignore-and-report may remain as defence), FR-112 (Pending becomes Issued in the same save; Cancelled, Issued and Cleared untouched; last-modified-by shows the person who saved), AC-12 (carve-out removed), AC-13 and AC-14 (clarified). AC-15 unchanged: removing the final mark still leaves Issued. The TAD is updated separately by architect-agent. No new ids, no hours restated; gate not re-opened.

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
| 5 | AI-Assisted Anonymisation & Trustee Pack Preparation | Free-text narratives redacted, each one reviewed and released by the process owner *(Amendment A-11; previously read: "human review of low-confidence cases")* |
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
  and provider agreements, not technology. *(Amendment A-12 narrows nothing here: it covers only what
  follows a payment finance has already recorded as final, FR-107 to FR-111. Paying a provider stays out.)*
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
| FR-001 | The system SHALL prevent submission of a grant application WHEN any mandatory field (full name, the applicant's confirmation that they are 18 or over, postcode, financial situation, preferred holiday dates) is empty, SO THAT incomplete applications are never created and staff time is not spent chasing them. *"Preferred holiday dates" is the form's free-text* Provisional date *question, stored as written (FR-091).* ⚠️ **CORRECTED, Amendment A-08 (APPROVED 2026-09-25).** Previously the list read ~~date of birth~~ and ~~provider preference~~. The live form asks for neither. It collects an 18-or-over confirmation and, separately, an optional age range, so the age band comes straight from the applicant and no date of birth is ever held (FR-027). There is no provider-preference question (TAD rev 10 Appendix C §C.3). OQ-046 found that column exists for a later stage of the process. The provider-preference correction goes beyond TAD §C.9's list. It is the same defect in the same sentence. | High |
| FR-002 | The system SHALL display plain-English, field-specific guidance and validation messages WHEN an applicant leaves a mandatory field empty or enters a value that fails validation, SO THAT applicants can correct their own answers without contacting the charity. | High |
| FR-003 | The system SHALL present financial detail questions only WHEN an income band has been selected, and carer questions only WHEN the applicant has indicated they are travelling with a carer, SO THAT applicants are not asked questions irrelevant to their circumstances. ⚠️ **The carer half of this requirement is UNIMPLEMENTED and has no data destination — recorded by Amendment A-04, 2026-08-26.** FR-076 removed `rev_travellingwithcarer`, `rev_carername` and `rev_carersupport`, because the live WordPress form has never asked those questions and the three columns had been empty since they were created. Removing empty columns the form does not feed was the right call (D-5), but it leaves this requirement's carer clause with nothing to conditionally reveal and nowhere to store an answer. **Not silently dropped and not withdrawn:** the requirement stands, and closing it needs either a form change requested of Alex (which would return the three columns) or a reviewer decision to withdraw the carer clause. The income-band half is unaffected. | Medium |
| FR-004 | The system SHALL display a completion-progress indicator throughout the application, SO THAT applicants can see how much remains and are less likely to abandon partway. | Medium |
| FR-005 | The system SHALL allow an applicant to save a partially completed application and resume it later, SO THAT applicants who need help mid-application do not lose their answers. | Medium |
| FR-006 | The system SHALL present a summary of all answers with a per-section edit option before final submission, SO THAT applicants can correct mistakes before the application enters the process. | Medium |

### B. Intake into the system of record (Automation #4)

| ID | Requirement | Priority |
|---|---|---|
| FR-007 | The system SHALL create a grant application record automatically WHEN an applicant submits the online application form, SO THAT no manual export-and-import step is required and assessment can begin immediately. ⚠️ **AMENDED, Amendment A-08 (APPROVED 2026-09-25): what the record contains is now governed by FR-083 and FR-084** (§4.K). The reviewer's rule: *"Keep all data that is actively requested from the user. If the form saves a date to a separate field the user doesnt fill in, ditch it. Only transfer what is actually filled in by the user of the form."* | High |
| FR-008 | The system SHALL assign every new application a unique reference in the format `REV-YYYY-NNN` and record its submission timestamp WHEN the application record is created, SO THAT each application can be identified unambiguously in correspondence, reporting and audit. | High |
| FR-009 | The system SHALL notify the process owner via Microsoft Teams with the applicant name and application reference WHEN a new application record is created, SO THAT new applications are picked up without anyone polling the website. | Medium |
| FR-010 | The system SHALL record the failure and alert the process owner WHEN an incoming submission cannot be turned into an application record, SO THAT no application is silently lost. | High |

### C. Scoring engine (Automation #2)

| ID | Requirement | Priority |
|---|---|---|
| FR-011 | The system SHALL calculate a circumstance score out of 60 from the applicant's wellbeing answers WHEN an application record is created, SO THAT scoring is consistent and no longer performed by hand. | High |
| FR-012 | The system SHALL invert the applicant's reported feeling answer so that a lower reported feeling produces a higher score, WHEN calculating the circumstance score, SO THAT the score reflects need rather than positivity. | High |
| FR-013 | The system SHALL convert each Likert wellbeing response to its configured point value (Strongly Disagree = 5, Disagree = 4, Neutral = 3, Agree = 2, Strongly Agree = 1) WHEN calculating the circumstance score, SO THAT the charity's agreed need criteria are applied identically to every application. ⚠️ **This wording is now known to be incomplete — see Amendment A-01 (PROPOSED) at the top of this document, and test-report D-009.** The agree/disagree labels are correct for only **three** of the ten wellbeing questions; the other seven use a frequency scale, and a sixth response ("Not sure", 0.5 points) is missing entirely. Left as originally approved pending plan-agent re-issue; replacement wording is proposed in A-01. | High |
| FR-014 | The system SHALL set the application status to Auto-reject WHEN one or more of these rules applies: the amount requested is over the limit for the type of break with no exceptional funding requested (FR-102); the applicant does not receive means-tested benefits and their income band is above the income ceiling (FR-015); the applicant has savings over £6,000 (FR-103); the applicant was funded by Revitalise within the last 12 months (FR-104); or the circumstance score is at or below the configured knockout threshold. A rule the process owner has switched off (FR-017) does not apply. Otherwise it SHALL set Borderline or Auto-pass by comparing the circumstance score against the configured borderline band. SO THAT staff attention goes only to the cases that need human judgement. None of these rules applies WHEN FR-022 withholds an automated outcome. ⚠️ **AMENDED, Amendment A-10 (APPROVED 2026-10-19, revision 2).** Reviewer, 2026-10-19: *"Every one of the following SHALL set status Auto-reject (4)"*. A rule that applies rejects whatever the score: savings Yes with a score of 45 is Auto-reject, not Auto-pass. The knockout and 12-month rules are unchanged; the 12-month rule was built (EF-34) before any FR stated it. Revision 1's income clause read *"the applicant is in work with an income band above the income ceiling"*; the reviewer withdrew the employment condition on 2026-10-19. Previously: *"The system SHALL set the application status to Auto-pass, Borderline or Auto-reject by comparing the circumstance score against the configured knockout threshold and borderline band WHEN the score has been calculated, SO THAT staff attention goes only to the cases that need human judgement."* | High |
| FR-015 | The system SHALL evaluate the applicant's financial answers against the configured income ceiling and record the outcome as a separate eligibility flag WHEN an application is scored, and SHALL set Auto-reject (FR-014) WHEN the flag records the income band as above the ceiling, SO THAT an applicant who does not receive means-tested benefits and whose household income is above the ceiling is rejected on that ground alone. A benefits Yes sets the flag to *qualifies on benefits*, so the income band is not looked at and the rule cannot reject. Any other benefits answer, a blank one included, means the band is compared. A band is above the ceiling when its top is above it: at a £25,000 ceiling, *£25,000 to £34,999* and *Over £35,000* are above, and *£15,000 to £24,999* is not. An applicant not on benefits who gave no income band is recorded as *not stated*, as the flag does today, and is not rejected (A-10 example 16). The employment status is not read. ⚠️ **AMENDED, Amendment A-10 (APPROVED 2026-10-19, revision 2).** Reviewer, 2026-10-19: *"The flow should only look at income band when the applicant has not receiving means tested benefits. Employment status doesn't have to be checked."* Answers the second half of OQ-003. The flag is kept as it is. Revision 1 also required the employment status to be *Yes, full-time* or *Yes, part-time*; that condition is withdrawn. Previously: *"The system SHALL evaluate the applicant's financial answers against the configured income ceiling and record the outcome as a separate eligibility flag WHEN an application is scored, SO THAT applications outside the financial eligibility criteria are identified independently of the circumstance score."* | High |
| FR-016 | The system SHALL exclude disability data, health-condition data and the free-text narrative from the circumstance score calculation, SO THAT special-category data does not influence an automated outcome. ⚠️ **Annotated, Amendment A-10 (APPROVED 2026-10-19, revision 2).** No auto-reject rule reads a disability, health or employment answer. The income rule reads the income flag, which uses the benefits answer only as the gate exception approved on 2026-09-18 allows (A-10 Finding 4). The score calculation is unchanged and still reads none of these columns. Revision 1's annotation, which let the income rule read the employment status as *in work or not*, is withdrawn with that condition. | High |
| FR-017 | The system SHALL allow the process owner to change, without any change to the automation logic: the knockout threshold, the borderline band, the income ceiling, the amount limit for each type of break (FR-102), and whether the savings rule (FR-103) and the prior-funding rule (FR-104) apply, SO THAT the board can adjust criteria without developer involvement. The £6,000 and 12-month figures are the form's own Yes/No questions, so they change only with the form (BR-S11); what the process owner changes for those two rules is whether they apply. Defaults: A-10 Finding 8. Example: Emily sets the Day trips or outings limit to £150; a £120 day trip with no exceptional request is then no longer rejected, and no flow is edited. Example: Emily switches the savings rule off; savings Yes with a score of 45 is then Auto-pass, with no reason. ⚠️ **AMENDED, Amendment A-10 (APPROVED 2026-10-19, revision 2).** Reviewer, 2026-10-19: *"These thresholds should be in the settings table, so that the process owner can change them. Just like income ceiling is on the settings table. Do the same for the other auto-reject reasons."* Revision 1 added only the two amount limits. Previously: *"change the knockout threshold, the borderline band and the income ceiling"*. | High |
| FR-018 | The system SHALL allow the process owner to override the automatically assigned status on any application and SHALL record that an override was made, WHEN the process owner disagrees with the automated outcome, SO THAT a named human remains accountable for every outcome. | High |
| FR-019 | The system SHALL route every application with status Borderline to the process owner for manual review before it progresses, SO THAT marginal cases receive human judgement rather than an automated verdict. | High |
| FR-020 | The system SHALL remove applications with status Auto-reject from the active working list into a separate rejected list WHEN the status is set, SO THAT the active list shows only applications requiring action. | Medium |
| FR-021 | The system SHALL send the process owner a daily summary stating how many applications were scored, how many were auto-rejected and how many are borderline awaiting review, SO THAT the process owner has oversight without opening the system. | Medium |
| FR-022 | The system SHALL withhold a final automated outcome and route the application to the process owner WHEN any answer required by the scoring methodology is absent, SO THAT incomplete data cannot produce a spurious automated rejection. *(DERIVED — see Interpretations; behaviour to be confirmed under OQ-002.)* ⚠️ **Annotated, Amendment A-10 (APPROVED 2026-10-19).** The status is Under Review and no Auto-reject rule of FR-014 applies, the eligibility rules included, so no reason is written (FR-105). Reviewer, 2026-10-19: keep today's behaviour. Example: savings Yes and one wellbeing answer missing gives Under Review with no reason. | High |
| FR-102 | The system SHALL set Auto-reject (FR-014) WHEN the amount requested from Revitalise is over the limit for the type of break and the applicant has not ticked the exceptional funding request: over £500 for *Holiday accommodation*, *Respite Care Facility stay* and *Other*; over £100 for *Day trips or outings* and *Activity or Experience*. Each limit is a setting (FR-017). *Over* means strictly greater: £500 and £100 themselves pass. Only the main amount requested is compared, never the additional (exceptional) amount. A blank amount or a blank type of break does not reject. SO THAT a request above the standard maximum that does not use the exceptional-funding route is rejected rather than passed to the panel. (New, Amendment A-10 (APPROVED 2026-10-19, revision 2). Reviewer, 2026-10-19: *"That is correct. This overrides that decision."* This overrides EF-31 and EF-32 by reviewer decision; see A-10 Finding 1. Revision 1 put *Respite Care Facility stay* and *Other* under the £100 limit.) | High |
| FR-103 | The system SHALL set Auto-reject (FR-014) WHEN the savings rule is switched on (FR-017, on by default) and the applicant has answered Yes to having savings over £6,000, whatever their employment, income or benefits, SO THAT an applicant with savings above the charity's limit is rejected on that ground alone. A blank answer, as the form leaves it for a benefits claimant, does not reject. (New, Amendment A-10 (APPROVED 2026-10-19, revision 2); unchanged in revision 2 except the switch. Reviewer: *"rev_savingsover6000 = Yes rejects on its own, for every applicant regardless of employment or benefits."* The £6,000 figure is the form's wording, not a setting: BR-S11. The switch is what the process owner can change, A-10 Finding 8.) | High |
| FR-104 | The system SHALL set Auto-reject (FR-014) WHEN the prior-funding rule is switched on (FR-017, on by default) and the applicant has received funding from Revitalise before and has answered No to that funding being more than 12 months ago, SO THAT the charity does not fund the same applicant twice within a year. (New, Amendment A-10 (APPROVED 2026-10-19, revision 2). The 12 months is the form's question, not a setting; the switch is what the process owner can change, A-10 Finding 8. Records the behaviour built under EF-34, `wbs:2.7`, which no FR stated. Reviewer: *"already built -> reject, as today"*.) | High |
| FR-105 | The system SHALL write a plain-language reason for every rule of FR-014 that applied, one per line and all of them, WHEN it sets Auto-reject, and SHALL show that text on the application's main record for staff, SO THAT Emily sees why without working it out. Reasons are listed in the order of FR-014's rule list: amount, income, savings, prior funding, score. Each names the values that decided it (A-10 worked examples 2, 6, 10, 11, 14). The income reason names the band and the ceiling only. A switched-off rule writes no reason. The text SHALL be empty for every other status. An override (FR-018) SHALL leave the text as it was, so the record shows both why the system rejected and who overrode it. (New, Amendment A-10, APPROVED 2026-10-19. Reviewer: *"When several rules fire, ALL reasons are listed, not just the first."* The single-reason column built under EF-45 is the starting point.) | High |
| ~~FR-106~~ | **WITHDRAWN, Amendment A-10 (APPROVED 2026-10-19, revision 2) — reviewer ruling, 2026-10-19:** *"Trustees don't see these fields in the portal. They don't have the link to the admin app, that app is not shared with their security role."* Checked 2026-10-19: no trustee portal screen or query names the reason columns (A-10 Finding 6). The identifier stays allocated, with no force. Revision 1 read: ~~The system SHALL NOT show the auto-reject reason text, or any record that repeats it, to a trustee in any surface, SO THAT an answer trustees must not see, such as the employment status (FR-078, D-1), does not reach them through the reason. (New, Amendment A-10, PROPOSED 2026-10-19; A-10 Finding 6, §7.1d.)~~ | — |

### D. Duplicate-grant check (Automation #7)

| ID | Requirement | Priority |
|---|---|---|
| FR-023 | The system SHALL check each new application against the charity's historical grant payment records in QuickBooks WHEN the application record is created, SO THAT previously funded applicants are identified before assessment rather than after. | Medium |
| FR-024 | The system SHALL flag the application as a possible duplicate and record the prior grant reference, date and amount WHEN a match is found against the applicant's identifying details, SO THAT staff can investigate before a second grant is awarded. | Medium |
| FR-025 | The system SHALL record "no prior grants found" against the application WHEN the check completes without a match, SO THAT the check is evidenced as having run. | Low |

### E. Anonymisation and trustee pack preparation (Automation #5)

| ID | Requirement | Priority |
|---|---|---|
| FR-026 | The system SHALL produce a redacted copy of each free-text narrative in which detected personal identifiers are replaced with category labels (`[NAME]`, `[FAMILY MEMBER]`, `[GP PRACTICE]`, `[ADDRESS]`, `[PHONE]`, `[EMAIL]`), except that a person's name is replaced as FR-095 states, WHEN an application becomes eligible for trustee review, SO THAT trustees can weigh a real case without learning whose it is. ⚠️ **AMENDED, Amendment A-09 (APPROVED 2026-10-16).** Two changes. `[EMAIL]` joins the labels, by the reviewer's 2026-10-06 decision D-3 (*"Agreed"*), which this SDD had not yet recorded. A person's name becomes *They*, *them* or *their* where FR-095 applies, by the reviewer's 2026-10-16 decision *"Change to the clients key and examples"*; `[NAME]` stays for the cases OQ-054 lists. Previously: *"replaced with category labels (`[NAME]`, `[FAMILY MEMBER]`, `[GP PRACTICE]`, `[ADDRESS]`, `[PHONE]`)"*. | High |
| FR-027 | The system SHALL present age only as the age band the applicant chose on the form, SHALL replace any specific age appearing in free text with an age band, and SHALL replace specific locations with a region, in all trustee-visible content, SO THAT an applicant cannot be identified from quasi-identifiers. ⚠️ **CORRECTED, Amendment A-08 (APPROVED 2026-09-25).** Previously *"replace specific ages with an age band"* treated a date of birth as the source of the band. The form collects no date of birth. It asks for the age range directly. An applicant who picks *"Prefer not to say"* has that answer recorded, and no band is inferred. The date-of-birth column stays empty (TAD rev 10 `ADR-051` item 9). The free-text and location halves are unchanged. | High |
| FR-028 | The system SHALL retain region, preferred dates, circumstance score, holiday preferences and general condition information in trustee-visible content WHEN redacting, SO THAT trustees keep the information they need to reach a funding decision. | High |
| FR-029 | The system SHALL flag a redacted narrative for the process owner's attention WHEN the redaction confidence falls below the configured threshold (initially 85%), SO THAT she sees which narratives the redaction was least sure about and can look at them first. The flag does not decide release: every narrative is reviewed and released under FR-030, flagged or not. ⚠️ **AMENDED, Amendment A-11 (PROPOSED 2026-10-19), on the reviewer's decision of the same day** (*"All records should be checked by the process owner regardless. So, we don't need that setting at all."*). Previously read: *"The system SHALL flag a redacted narrative for manual review and SHALL withhold it from trustees WHEN the redaction confidence falls below the configured threshold (initially 85%), SO THAT no unreviewed low-confidence redaction reaches the board."* | High |
| FR-030 | The system SHALL require the process owner to review, correct where needed and release every redacted narrative before a trustee can see it, WHEN a narrative has been redacted, and SHALL NOT release any narrative automatically, whatever its confidence, SO THAT a human confirms every redaction before disclosure to trustees. ⚠️ **AMENDED, Amendment A-11 (PROPOSED 2026-10-19), on the reviewer's decision of the same day** (*"All records should be checked by the process owner regardless."*). Previously read: *"The system SHALL allow the process owner to review, correct and release a flagged redaction WHEN a narrative has been flagged, SO THAT a human confirms every uncertain redaction before disclosure to trustees."* | High |
| FR-031 | The system SHALL make the original unredacted narrative readable only to the administrator role and the service identity, SO THAT raw special-category free-text is not disclosed beyond those who need it. | High |
| FR-032 | The system SHALL generate a per-application anonymised document containing the redacted narrative, score breakdown, holiday details and staff recommendation, SO THAT trustees who cannot use the review portal are not excluded from the decision. ⚠️ **Field list aligned with FR-035's adopted wording — see Amendment A-02, Finding 1 (top of this document).** | Medium |
| FR-033 | The system SHALL allow trustee-pack preparation to be run on demand by the process owner and SHALL also run it on a schedule ahead of each board meeting, SO THAT the pack is ready without anyone remembering to start it. | Medium |

### E+. Neutral wording, readability and spelling of the redacted copy (Amendment A-09 — `wbs:5.6`; FR-099 depends on `CO-009`)

⚠️ **New subsection, Amendment A-09, APPROVED 2026-10-16.** These requirements apply
to every redacted copy FR-026 and FR-079 produce. They replace what Emily does by hand today: she
strips *"gender references"* as well as names (§1). The source is the client's
`docs/Import/Anonymisation Key.xlsx` (sheet 1, rows 2 to 27) and its four worked examples in
`docs/Import/Anonymised Examples.xlsx`. Where the two disagree, the examples win (Amendment A-09,
Finding 1). The stored original is never changed by any of them (FR-031).

| ID | Requirement | Priority |
|---|---|---|
| FR-094 | The system SHALL replace, in the redacted copy, every gendered word and relationship word the client's Anonymisation Key lists with the neutral word it gives (*he* and *she* become *they*; *mum*, *dad*, *mother* and *father* become *parent*; *brother* and *sister* become *sibling*; *son* and *daughter* become *child*; *husband*, *wife*, *boyfriend* and *girlfriend* become *partner*; *man*, *woman*, *boy* and *girl* become *person*; *he's* and *she's* become *they're*), matching whole words only, in any capitalisation, and including the plural of each noun, WHEN the redacted copy is produced, SO THAT a trustee learns the relationship but not the gender. Where the key and the client's examples differ, the examples are followed: *him* becomes *them*; *her* becomes *their* before a noun and *them* elsewhere; *Mum* or *Dad* used as a name becomes *my parent*. *hers*, *his* standing alone, and the *-self* forms follow OQ-056. A word inside another word is never changed (*the*, *shelter*, *manage*). | High |
| FR-095 | The system SHALL replace a person's name in the redacted copy with *They*, *them* or *their*, whichever fits its place in the sentence, WHEN that person is the only person named in the text, the name is not the applicant's own, and the name does not follow a title such as *Dr*, SO THAT the copy reads the way the client's own examples do (*Sam relies on me* becomes *They rely on me*). The system SHALL keep `[NAME]` for the applicant's own name, a name the writer gives for themselves (*I am …*, *I'm …*, *my name is …*), and SHALL NOT turn it into *they* (*I am Sam* becomes *I am [NAME]*, not *I am they*). WHEN a name sits right after a relationship word, the system SHALL drop the name and keep only the relationship word, neutralised under FR-094 or FR-096 (*my husband Derek* becomes *my partner*), because the relationship word leads, **even when other people are named in the text**. Any other name in a text that names two or more people, or a name after a title such as *Dr*, keeps `[NAME]` (OQ-054). ⚠️ **AMENDED, Amendment A-11 (PROPOSED 2026-10-19)**, on the reviewer's TAD rev 25 approval and his 2026-10-16 ruling below. Two changes: the applicant's own name keeps `[NAME]`, and the relationship word leads even when other people are named. Previously read: *"The system SHALL replace a person's name in the redacted copy with *They*, *them* or *their*, whichever fits its place in the sentence, WHEN that person is the only person named in the text and the name does not follow a title such as *Dr*, SO THAT the copy reads the way the client's own examples do (*Sam relies on me* becomes *They rely on me*). WHEN a name sits next to the relationship word for the same person, the system SHALL drop the name and keep only the relationship word, neutralised under FR-094 or FR-096 (*my husband Derek* becomes *my partner*), because the relationship word leads. A name in a text that names two or more people, or after a title such as *Dr*, keeps `[NAME]` (OQ-054)."* ⚠️ **CORRECTED 2026-10-16 by the reviewer, after approval:** *"My husband Derek becoms partner. not family member. the word husband is leading in this pattern."* Previously read: *"… and it does not sit next to the relationship word for the same person … In the other cases the name keeps its FR-026 label (`[NAME]`, or `[FAMILY MEMBER]` in *my partner [FAMILY MEMBER]*); OQ-054 asks the reviewer to confirm or replace that default."* | High |
| FR-096 | The system SHALL also replace *grandmother*, *stepson*, *auntie*, *niece*, *nephew*, *mummy* and *lady*, and the titles *Mr*, *Mrs*, *Ms* and *Miss*, in the redacted copy WHEN the redacted copy is produced, SO THAT words the key does not list cannot give away a gender. **Default replacements, pending OQ-055:** *grandmother* becomes *grandparent*, *stepson* becomes *stepchild*, *mummy* becomes *parent*, *lady* becomes *person*, and *auntie*, *niece* and *nephew* become *relative*. A title is removed, and the name after it is treated under FR-095. The other-gender counterparts of these words are included on the same terms (OQ-055). | High |
| FR-097 | The system SHALL judge each word joined by *and*, *or* or a comma on its own, and SHALL replace a later word in that list WHEN it is itself a word FR-094 or FR-096 replaces, or an identifier FR-026 labels, SO THAT *my wife and son* becomes *my partner and child*, not *my partner and son*. Reviewer, 2026-10-16: *"if the second word that belongs to end is identifyable information than it also needs to change."* | High |
| FR-098 | The system SHALL correct the grammar that a replacement under FR-094 to FR-097 breaks, so the redacted copy reads correctly, WHEN a replacement changes a word the rest of the sentence depends on, SO THAT a trustee reads *they are*, not *they is*. This covers: the verb agreeing with *they* (*she relies* becomes *they rely*), including a second verb joined by *and* (*he receives PIP and requires care* becomes *they receive PIP and require care*); a name replaced under FR-095 (*Sam has* becomes *They have*); *her* as *their* or *them*; and capitals following the position in the sentence, not the replaced word. It SHALL NOT change any word the replacement did not affect. Correcting the applicant's own mistakes is FR-099. | High |
| FR-099 | The system SHALL correct spelling mistakes and obvious typing slips in the redacted copy, as a separate step that runs only on text that has already been redacted, WHEN a redacted copy is produced, SO THAT trustees can read the applicant's case easily. It SHALL correct only the misspelt or mistyped word. It SHALL NOT reword, reorder, add punctuation the applicant did not write, or change meaning. **Commercial dependency:** change order `CO-009`, **approved, unbilled** (reviewer, 2026-10-16: *"CO-009 Approved with unbilled tag. Features always expand a bit during development and this one is within reasonable limits."*). Billing is recorded by commercial-agent, not decided here. Previously read: *"(PROPOSED, not approved)"*. The reviewer placed this in the design on 2026-10-16 (*"a requirement that came up during the meeting with Emily"*). This SDD records the requirement, and decides neither its billing nor its task id. | Medium |
| FR-100 | The system SHALL keep every label, and every word written under FR-094 to FR-097, exactly as redaction wrote it when FR-098 or FR-099 corrects the text, and SHALL withhold the copy from trustees and flag it for manual review WHEN a correction would change or remove a label, bring back a word that was replaced, or add a word that corrects nothing, SO THAT making the text readable can never undo the anonymisation. | High |
| FR-101 | The system SHALL withhold a redacted copy from trustees and flag it for manual review WHEN a word that FR-094 or FR-096 replaces is still present in it, SO THAT a gendered word the scrub missed reaches Emily (FR-030) and not a trustee. | High |

**Not in scope, by reviewer decision of 2026-10-16.** The key's rows 37, 40 and 41 (*Benefit provider*,
*Please specify source of additional funding*, *Awaiting decision from*) get no redacted copy and are not
shown to trustees: *"don't have to be in the trustee portal. All fields in the trustee portal right now is
what the trustees use to make their decisions on."* FR-079 is not extended to them. The other twelve
questions in the key are the twelve columns FR-079 already covers (redaction rules v0.4 §2.1a). §7.1c
classifies the two answers that were unclassified.

### F. Trustee review portal (Automation #6)

| ID | Requirement | Priority |
|---|---|---|
| FR-034 | The system SHALL present trustees with a sortable and filterable summary list of the applications under review showing circumstance score, region, preferred dates and status, SO THAT a trustee who prefers a data-only view can work entirely from one screen. | High |
| FR-035 | The system SHALL provide a per-application detail view showing the redacted narrative, the score breakdown, the type of break, the preferred dates, the break location, the total funding requested for the grant round (including any exceptional funding requested), the applicant-type context, the care-support context, the staff recommendation, and — added by Amendment A-05 — the **financial-eligibility context** (household income flag and band, savings above the threshold, receipt of means-tested benefits, benefit provider, employment status, and the redacted explanation of why the applicant cannot fund the break themselves), the **condition context** (the applicant and support-recipient condition profiles, the redacted free-text elaboration behind each, the exceptional-circumstance category and its redacted free-text detail), and the **helper, referee and emergency-contact context** (helper organisation, relationship, declaration consent and its date, and the helper, referee and emergency-contact identity attributes), SO THAT trustees see in the portal the same case they receive today in the printed board pack. Fields whose value is withheld by column security render per FR-078; free text renders per FR-079. ⚠️ **Updated twice.** *Amendment A-02, APPROVED 2026-08-24* added the type of break, applicant-type and care-support context and the single total-funding figure (OQ-031, OQ-032). *Amendment A-05, APPROVED 2026-08-27* added the three groups above, reversing the three categories A-02 had recorded as "correctly excluded" and resolving OQ-011, on the reviewer's decision that trustees already receive this data in the printed board pack. Per-column classification and the security position for every added field are at §7.1b; the ground truth behind them is in Amendment A-05, Finding 1, at the top of this document. ⚠️ **Extended, Amendment A-08, APPROVED 2026-09-25 (OQ-051).** The condition context also includes the applicant's and the person supported's Equality Act 2010 answers (FR-086, FR-087), shown as values, and their disability descriptions (FR-088, FR-089), shown only through redacted counterparts under FR-079. Until Automation #5 produces those counterparts, the descriptions render withheld. | High |
| FR-036 | The system SHALL withhold applicant identifying information from every trustee-facing view, SO THAT trustee review is anonymous by design rather than by manual preparation. ⚠️ **Unchanged in force, clarified by Amendment A-05, 2026-08-27.** A-05 lets the trustee detail view *request* the secured helper, referee and emergency-contact identity columns; it does not disclose them. `REV_TrusteeRestricted` returns no value to a trustee from any surface, so the field renders as an explicit restricted state (FR-078) and no identifying information reaches the view. This is what NFR-003 already requires — the control enforced by the platform, not by manual preparation — and A-05 moves the whole of that enforcement to the platform layer rather than splitting it between the platform and the app's choice of columns. | High |
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
| FR-058 | The system SHALL present the current round's total applications received and the date the round opened, SO THAT trustees see how the round is progressing before opening the applications list. *(Amendment A-03, source: both decks' slide 2.)* ⚠️ **CORRECTED, Amendment A-06, 2026-08-30 (`IMP-0507`), then SUPERSEDED IN PART, Amendment A-07, 2026-09-19 (`CO-005`, `wbs:6.10`, resolving `IMP-0789`).** ~~The average applications received per day since the charity began grant-giving, computed as a cumulative charity-wide figure since a fixed 16 February 2026 reference date~~ is **struck** — that single figure is replaced by FR-080's all-history, month-by-month recompute with FR-081's anomaly flagging, per the reviewer's EF-11 rescope. The total applications received and the round-open-date fields are unchanged and remain per-round. | Medium |
| FR-059 | The system SHALL present, for the current round, the count of applications in each exceptional-circumstance category, the total and percentage of applications citing any exceptional circumstance, and the average exceptional-funding amount requested, SO THAT trustees see the round's need profile before reviewing individual cases. *(Amendment A-03, source: `Round 3 Stats.pptx` slide 2. No minimum-cell-size rule applies to the category counts and the percentage citing any exceptional circumstance — see NFR-027, withdrawn by reviewer decision, Resolution 2026-08-25. ⚠️ **CORRECTED, TAD Revision 6 §6.3.5 / ADR-039, 2026-08-28 — that withdrawal does not reach the average exceptional-funding amount requested.** A mean over a money column (`rev_additionalamountrequested`) is a different disclosure shape: at a population of one it is that applicant's exact funding request, not an aggregate, and NFR-027's withdrawal rested on the field-level security profile, which does not exist for this column — `IsSecured=0`, absent from `REV_TrusteeRestricted`, and a Money column's automatic `_base` twin cannot be secured at all (platform limitation). The figure is therefore withheld unless its own population is ≥ 5 — `k = 5`, the TAD's `RoundStatisticsMoneyMeasureMinimumPopulation` setting, answered by the reviewer 2026-08-28 — and renders as an absence below that threshold.)* | Medium |
| FR-060 | The system SHALL present, for the current round, a breakdown by type of break showing the number of applications, the average total holiday cost, the average grant amount requested (including exceptional funding), and the percentage of total cost represented by the requested grant amount, with a total row across all types, SO THAT trustees see what the round's applications are asking for and at what cost. *(Amendment A-03, source: `Round 3 Stats.pptx` slide 2. This is a round-wide average by break type, distinct from FR-035's per-application total-funding figure — OQ-031's resolution against itemised per-application costs does not need to be re-applied here.)* | Medium |
| FR-061 | The system SHALL present, for the current round, the applicant gender, ethnic-group, age-range and applicant-type (disabled person / carer applying on behalf of a disabled person / carer applying for themselves) distributions as percentages, SO THAT trustees can see who applied in this round before opening individual cases. *(Amendment A-03, source: `Round 3 Stats.pptx` slide 3/4 charts.)* ⚠️ **REWORDED, Amendment A-03 Resolution (continued), 2026-08-25 — the benchmark-comparison clause is withdrawn by reviewer decision, not silently dropped.** The original wording additionally required the gender, ethnic-group and age-range distributions to be *"shown alongside the corresponding published UK cared-for-disabled-adults-and-carers benchmark percentages, SO THAT trustees can see how representative the round's applicants are of the population the charity serves"*. No such dataset was ever sourced or owned, which architect-agent's TAD raised at TAD stage and which was already recorded here as OQ-037. Reviewer's exact words: *"there is no benchmark dataset. This is personal knowledge of the trustees. So only showing the representation of applications is enough."* Trustees hold the population context personally, so it is not restated on screen. **This closes OQ-037.** The applicant distributions themselves are unchanged and remain in scope. ⚠️ **Not touched by this amendment:** the ethnic-group figure has no source data at all, because the charity has never collected the field — a separate, still-open gap raised independently by architect-agent's TAD at §3.4 of the trustee-portal-visual-refresh TAD and risk A-R24 of the same TAD, and gated by OQ-027, not by OQ-037. | Medium |
| FR-062 | The system SHALL present, for the current round, the distribution of applicant responses to the three "last year" wellbeing questions, the distribution of life-satisfaction scores (0–10), and the round's headline circumstance statistics (the proportion of carers providing high-hours care, the proportion reporting low life satisfaction, and the proportion unable to take a break when needed), SO THAT trustees see the round's overall level of need. *(Amendment A-03, source: `Round 3 Stats.pptx` slide 5 and its two charts. Excludes the scoring-methodology explainer repeated on both decks' final slide — see Amendment A-03's "Source documents" note.)* | Medium |
| FR-063 | The system SHALL present the round's financial position — the amount committed or spent to date, the number of people and individuals supported, and, where the round's applications include a group or multi-person grant, the number of people reached through it — alongside the charity's current grant-giving capacity, suggested maximum spend for the round, monthly disbursement amount, and remaining legacy-fund split, sourced from a finance-maintained record rather than derived from Application/Grant/Payment data, SO THAT trustees have the financial picture behind the applications they are reviewing. *(Amendment A-03, source: `Round 4.pptx` slide 2. ⚠️ **PARTIALLY RESOLVED, Resolution 2026-08-25** — reviewer's exact words: "at the moment everything is manual. Maybe have this land on the finance accessable tables? Or an extra table that finance fills in these details." Confirmed manual/finance-maintained at business level; which of the reviewer's two mechanisms — extending an existing finance-accessible table, or a new table finance fills in — is an architect-agent decision at TAD stage, not chosen here. The capacity, suggested-maximum-spend and legacy-split figures also describe the charity's overall fund position rather than an event scoped to this round specifically — see Finding 3.)* | Medium |

### F++. Historic month-by-month applications recompute (Amendment A-07 — WBS 6.10, `feature:trustee-portal-landing-page`, `CO-005`)

⚠️ **New subsection, Amendment A-07, APPROVED 2026-09-19.** Replaces FR-058's struck per-day clause.
Numbered out of sequence for the same reason FR-056/FR-057 were — continuing from the highest
existing FR id rather than disturbing earlier citations. See the Amendment A-07 block near the top
of this document for sourcing and the items it deliberately does not settle.

| ID | Requirement | Priority |
|---|---|---|
| FR-080 | The system SHALL recompute the *Applications per day* figure from **all historic applications** rather than the current round or a single cumulative average, broken down **month by month** from the grant-applications tracking start date (FR-082) to the current month, SO THAT trustees see how application volume has moved over the charity's full history rather than one summary number. *(Amendment A-07, `CO-005`, `wbs:6.10`.)* The mechanism by which a variable-length, unbounded month-by-month grouping is computed is an architect-agent TAD decision — see the Amendment A-07 "Flagged for architect-agent" section — not chosen here. | Medium |
| FR-081 | The system SHALL flag any month in FR-080's breakdown whose application count deviates from its own trailing six-month mean by more than a threshold percentage, SO THAT trustees notice an unusual month without having to read every value in the series. *(Amendment A-07, `CO-005`, `wbs:6.10`.)* **OQ-049 ANSWERED, reviewer, 2026-09-19:** the threshold is held as a **third, configurable `rev_setting`** (not a hardcoded literal), so it can be tuned later without a redeploy — starting value **50%** deviation from the trailing six-month mean. ⚠️ **Not fully designed yet:** this setting's Dataverse column name and the mean/deviation comparison logic inside FR-080's month-by-month loop are architect-agent TAD decisions that TAD Revision 9 / ADR-049 did not make — ADR-049 designed FR-080's grouping mechanism and FR-082's two settings only, before this threshold was answered. A further architect-agent TAD pass is required to name this setting and extend §5.1.3's flow design before `development-agent` can build the flagging logic. Until that pass lands and the setting is seeded, FR-081 SHALL continue to render its fail-safe unflagged default, matching this SDD's existing convention for an unset `rev_setting`-backed control (§0.9.1 precedent, `RoundStatisticsMoneyMeasureMinimumPopulation`). | Medium |
| FR-082 | The system SHALL hold two business facts as settings, not code: (a) the date from which this system's application record is complete going forward (the "grant-applications tracking start date"), and (b) the count of applications the charity received before that date, SO THAT FR-080's historic totals are not silently understated by the gap between when the charity began giving grants and when this system began recording them. *(Amendment A-07, `CO-005`, `wbs:6.10`.)* **OQ-050 ANSWERED, reviewer, 2026-09-19:** 16 February 2026 is confirmed to be both the tracking-start date and the date the charity itself began operating as a grant-giving charity — matching Amendment A-06's existing reference date exactly, so there is no separate pre-system application history to account for. Seed values: **`RoundStatisticsHistoryStartDate = 2026-02-16`**, **`RoundStatisticsHistoryPriorApplicationCount = 0`**. (The reviewer separately confirmed 715 applications as today's live running total since 16 Feb 2026 — that is not a seed value and is not written to any setting.) The Dataverse column names above remain illustrative pending architect-agent's TAD naming decision (same class as `RoundStatisticsStaleAfterSeconds`); `development-agent` seeds these two now-known values at `wbs:6.10`'s `post_deploy` step once the TAD names the columns. Until seeded, FR-080 SHALL render its computed range without an understated-total warning rather than fail or show a wrong figure, the same fail-safe convention as FR-081. | Medium |

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

### J. Trustee detail screen — withheld values and free text (Amendment A-05, WBS 6.3)

⚠️ **New subsection, Amendment A-05, APPROVED 2026-08-27.** FR-035 now names every field on the
trustee board pack. Two consequences of *"all fields need to be in"* are covered by no existing
requirement: what the screen does with a field the platform refuses to populate, and what it does
with free text that has no redacted counterpart yet. See the Amendment A-05 block near the top of
this document for the per-column ground truth, and §7.1b for the classification.

| ID | Requirement | Priority |
|---|---|---|
| FR-078 | The system SHALL render a field whose value is withheld from the signed-in user by column security as an explicit restricted state that names the field, rather than as an empty value or by omitting the field, SO THAT a trustee can tell the difference between an answer the applicant did not give and an answer the trustee is not permitted to see. *(Amendment A-05. Applies to the eleven `REV_TrusteeRestricted` columns listed in Finding 1, Group B. The control itself is unchanged — this requirement governs only how its effect is presented, and it is the reason binding a secured column is safe rather than merely harmless.)* | High |
| FR-079 | The system SHALL present applicant free text in a trustee-facing view only through that column's redacted counterpart, and SHALL render the withheld state for that field until redaction has been released for the record, SO THAT extending the trustee view to further free-text columns cannot disclose unredacted text. *(Amendment A-05. Extends FR-031's treatment of `rev_narrativeraw` to `rev_unabletofundexplanation`, `rev_exceptionalfundingdetail`, `rev_otherexceptionalcircumstance`, `rev_otherconditionraw` and `rev_supportrecipientotherconditionraw` — none of which has a redacted counterpart column today. Creating those columns is new schema work for architect-agent at TAD stage, following the existing `rev_narrativeredacted` pattern; see Amendment A-05, Finding 2, including why a redacted counterpart must NOT be added to the special-category register. Until Automation #5 ships, every one of these renders withheld — `EX-003`.)* | High |

### K. What the intake stores from the website form (Amendment A-08, `wbs:4.1` / `4.2` / `4.3`)

⚠️ **New subsection, Amendment A-08, APPROVED 2026-09-25.** It answers TAD rev
10 Appendix C §C.9. Every requirement here applies one rule, the reviewer's, verbatim:

> *"Keep all data that is actively requested from the user. If the form saves a date to a separate
> field the user doesnt fill in, ditch it. Only transfer what is actually filled in by the user of
> the form."*

Classification of every answer below is at §7.1c. None of these answers feeds the circumstance
score (FR-016, `C-DOM-030`). OQ-051 was answered on 2026-09-25. The two Equality Act answers reach
trustees as values, and the two descriptions reach them only as redacted counterparts. That is
written into FR-035.

| ID | Requirement | Priority |
|---|---|---|
| FR-083 | The system SHALL store every answer the applicant enters on the online application form, and SHALL NOT store any value the form or its plugin produces without the applicant entering it, WHEN a submission is received, SO THAT the record holds what the applicant actually told the charity, and nothing is presented as though they had said it. *Values not stored include:* the form's entry and update timestamps, its entry status and flags, its payment fields, the source page, the IP address and browser, the form-calculated total cost, and hidden fields the form fills with a fixed value (country). **The single exception is the form's entry identifier.** It is kept only as the technical key that recognises a resubmitted entry (BR-A05), is shown to no one and is reported on by nothing. That exception is recorded by the TAD (rev 10 `ADR-051` item 12) and was not stated by the reviewer, so approving this amendment approves it. **Unaffected:** FR-008's reference and submission timestamp are the system's own record of when the submission arrived, and are never taken from the form's own date. The consent dates are OQ-052. *(Amends FR-007. TAD §C.9 item 1.)* | High |
| FR-084 | The system SHALL leave a field empty, and SHALL NOT write any default value in its place, WHEN the applicant left that question blank or was never shown it, whether the website leaves the answer out, sends it empty, or sends an unticked box from a page the applicant did not see, SO THAT an unanswered question is never recorded as a "No", a "none" or a declined consent. A box the applicant **was** shown and left unticked is an answer, and is kept. *(Follows from FR-083: "only transfer what is actually filled in". It sits alongside FR-077, where an answer that matches no option is left empty and noted, and FR-022, where a missing scored answer withholds the automated outcome. TAD §C.9 item 1.)* | High |
| FR-085 | The system SHALL record every option the applicant ticks in answer to *"How did you hear about us?"*, one or more, and SHALL retain the applicant's own wording WHEN they choose *"Other (please specify)"*, SO THAT the charity can see which routes bring applicants to it. *(The two fields have existed since 2026-08, built on the reviewer's instruction, and nothing has written to them. A referral-source reporting answer. It is not a funding criterion, is not scored, and is not named in FR-035. TAD §C.9 item 2.)* | Medium |
| FR-086 | The system SHALL record the applicant's Yes or No answer to *"Do you have a disability as defined by the Equality Act 2010?"* WHEN the applicant is shown and answers that question, SO THAT the disability the grant is assessed against is on the record in the applicant's own answer, not only implied by the condition profile. ⚠️ **Special category (Art. 9)**, §7.1c. *(TAD §C.9 item 3. Trustee visibility: OQ-051, answered 2026-09-25.)* | Medium |
| FR-087 | The system SHALL record the Yes or No answer to *"Does the person you support have a disability as defined by the Equality Act 2010?"* WHEN a carer applicant is shown and answers that question, SO THAT the same fact is on the record for the disabled person a carer's application is about. The subject is the disabled person, whoever types the answer. That is the reviewer's 2026-09-17 correction, recorded in the Emily review feedback plan, §2f. ⚠️ **Special category (Art. 9)**, §7.1c. *(TAD §C.9 item 3. Trustee visibility: OQ-051, answered 2026-09-25.)* | Medium |
| FR-088 | The system SHALL retain, as written, the applicant's own description of how their disability affects them (*"Please briefly describe how your disability affects you"*, optional on the form, up to 650 characters) WHEN one is given, SO THAT what the applicant chose to tell the charity about their disability is on the record rather than discarded. ⚠️ **Special category (Art. 9) free text**, §7.1c. This is the text the board pack prints as *Brief Confirmation*, relabelled *Brief Description of Disability* under EF-37. Until now it had no stored source (Amendment A-08, Finding 3). *(TAD §C.9 item 3. Trustee visibility: OQ-051, answered 2026-09-25.)* | Medium |
| FR-089 | The system SHALL retain, as written, a carer applicant's description of how the person they support is affected by their disability (*"Please briefly describe how their disability affects them"*, optional, up to 650 characters) WHEN one is given, SO THAT the same description is on the record for the disabled person a carer's application is about. ⚠️ **Special category (Art. 9) free text**, §7.1c. *(TAD §C.9 item 3. Trustee visibility: OQ-051, answered 2026-09-25.)* | Medium |
| FR-090 | The system SHALL record the applicant's Yes or No answer to *"Is someone helping you complete this application?"* WHEN the applicant is shown and answers that question, SO THAT the record shows whether a third party took part in the application. The form does not show this question on the *carer applying on behalf of a disabled person* route, so FR-084 leaves it empty there. Under FR-084, the helper-page consents count as answered only when this answer is Yes. *(TAD §C.9 item 4.)* | Medium |
| FR-091 | The system SHALL retain the applicant's answer to the *Provisional date* question exactly as written (for example *"July 2026"* or *"Summer 2026"*), and SHALL NOT convert it into a start or end date, WHEN one is given, SO THAT the applicant's stated timing is on the record without adding a precision they did not give. This is the *preferred holiday dates* of FR-001. The structured start and end date fields stay empty until the form asks for real dates (form-validation spec M-06 and V-04, EF-09). That follows FR-083, because nobody entered those dates. *(Relates to FR-001. TAD §C.9 item 4. Presenting this text in the trustee portal belongs to `wbs:6.3` / EF-09 and is not part of this amendment.)* | Medium |
| FR-092 | The system SHALL record the applicant's answer to *"Are you receiving funding from any other sources for this break?"* as exactly one of **Yes**, **No** or **Applied and awaiting decision**, WHEN the applicant answers it, SO THAT an applicant waiting on another funder's decision can be told apart from one with no other funding. *(This closes form-validation spec M-08 on the data side. FR-035 is unchanged: the board pack carries no other-funding row, so A-05's basis for FR-035 does not reach it. See Amendment A-08, Finding 5. TAD §C.9 item 4.)* | Medium |
| FR-093 | The system SHALL record the applicant's middle name, name suffix and address state or province WHEN, and only WHEN, the form shows those fields to the applicant and the applicant fills them in, SO THAT FR-083 applies to these three exactly as it does to every other field. The last check of the live page, on 2026-08-13, found all three hidden (form-validation spec §4, Page 2). The form has changed since, because the title sub-field now arrives, so that check is not conclusive. **Until Alex confirms they are shown (OQ-053), nothing is stored for them and no field is built.** ⚠️ **Conditional.** *(TAD §C.9 item 6.)* | Low |

### L. A final payment starts the retention clock (Amendment A-12 — `wbs:8.6`, `CO-010`)

⚠️ **New subsection, Amendment A-12, APPROVED 2026-10-20.** Finance records payments by hand
(`wbs:8.3`, FR-150 to FR-154). These requirements say what follows when finance records one as the
**final** payment against a grant. Scope accepted unbilled under `CO-010`. The pre-issue duplicate-payment
re-check (FR-023's second call site, `wbs:8.5`) is **excluded** and is not in any row below.

| ID | Requirement | Priority |
|---|---|---|
| FR-107 | The system SHALL record the date of the final payment on the grant WHEN finance records a payment as the final payment against that grant, SO THAT the six-year retention period in FR-048 has a start date. The date is the payment's own date (OQ-057), not the day it was entered, and the system SHALL NOT let a payment be saved as final without one, by any route (the Payment form, an API write or a flow), so there is no fallback date (the reviewer's intent: *"Make payment date required when final payment is set"*). WHEN the save is refused, the grant and the application are unchanged and the person saving is told a payment date is required. The flow's ignore-and-report safeguard (no date recorded, no clock started, "final payment has no date" reported under FR-111) MAY remain as defence in depth; it is no longer the rule for non-form routes. *(Revised 2026-10-20 on the reviewer's decision "4": one table-level rule on Payment applies to every save. Previously read: "form only; an undated final payment from any other route is ignored and reported".)* WHEN a grant has more than one payment recorded as final, the grant carries the latest of their dates. | High |
| FR-108 | The system SHALL move the grant's application to the status "Grant Paid" in the same event as FR-107, WHEN the application is at "Approved", SO THAT the retention schedule in §7.6, which starts at "Grant Paid", applies. WHEN the application is at any other status, the system SHALL leave the status as it is and report the case under FR-111. | High |
| FR-109 | The system SHALL change neither the grant nor the application WHEN a payment is not recorded as final, and SHALL leave both exactly as they are WHEN the same payment is saved again without a change to what makes it final, SO THAT recording an instalment, or saving twice, never moves the retention date. | High |
| FR-110 | The system SHALL withdraw the effect of FR-107 and FR-108 WHEN a payment that was recorded as final stops counting as final (the mark is removed, or the payment is cancelled), and SHALL record the corrected date WHEN the date of a final payment is corrected. Where another payment on the grant is still final, the grant carries the latest date among those payments. Where none is, the grant's final payment date is cleared and the application returns to "Approved" if it is still "Grant Paid"; an application whose status has since moved on is left as it is and reported under FR-111. The grant's own status is also withdrawn (FR-113). The payment's own status is not reverted (FR-112; OQ-059, answered: *"No. payment final means final."*). SO THAT a mistaken tick never leaves a grant with a retention clock running for a payment that is not final. | High |
| FR-111 | The system SHALL make a final payment that cannot be applied visible to finance and the process owner, with the payment, the grant and the reason, WHEN the payment is not linked to a grant, or the application is at a status FR-108 does not move, or the date cannot be recorded, SO THAT no retention date is silently missing. It SHALL NOT retry in the background: finance corrects the cause and saves the payment again, which FR-109 makes safe. | High |
| FR-112 | The system SHALL set a payment's status to Issued, at the moment the payment is saved as final and in that same save, WHEN its status is Pending, SO THAT a final payment does not need a second field updated by hand and is never seen as final and Pending. The payment's last-modified-by SHALL show the person who saved it, not a service account. This applies to every route that saves the payment (form, API, flow). It SHALL leave the status as it is WHEN it is already Issued or Cleared. A payment that is Cancelled does not count as final (FR-110): the status stays Cancelled and the case is reported under FR-111. The system SHALL NOT change the payment's status WHEN the final mark is later removed (FR-110): finance sets any status correction by hand (OQ-059). *(Added by the reviewer-directed revision of Amendment A-12, 2026-10-20; timing and last-modified-by aligned on the reviewer's decision "4", 2026-10-20. Previously read: "in the same event as FR-107", which put the change in the flow after the save.)* | High |
| FR-113 | The system SHALL move the grant's own status to "Paid" in the same event as FR-107, WHEN finance records a payment as final and the grant's status is "Acceptance Signed", SO THAT a paid grant no longer reads as one still awaiting payment. WHEN the grant is at Awarded or Acceptance Issued, or at any other status except "Paid", the system SHALL leave the grant's status as it is and report the case under FR-111 (OQ-060), in the run where the final payment date is written or cleared; it SHALL NOT move a grant that has not been signed to "Paid". WHEN the grant is already at "Paid" and the payment is saved again, the system SHALL change nothing and report nothing (FR-109), so a repeat save of a paid grant is silent. WHEN FR-110 withdraws the last final payment on the grant and the grant is at "Paid", the system SHALL return it to "Acceptance Signed"; a grant at any other status is left as it is and reported under FR-111. This rule mirrors FR-108 but depends only on the grant's status, never on the application's. *(Added by the second reviewer-directed revision of Amendment A-12, 2026-10-20: *"Obviously the final payment should change the grant status as well."*)* *(Wording aligned 2026-10-20 to the reviewer-approved, built design (TAD §5.11); not a new decision. Previously read: "Awarded, Acceptance Issued, Paid already, or anything else" reported, which read literally reports every repeat save of a paid grant and contradicts FR-109.)* | High |

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
| NFR-009 | 100% of storage and backup SHALL remain in the UK or in Switzerland across every component, including the redaction service, signature service and finance system, and processing SHALL take place there too, with one exception: AI prompt inference MAY be processed inside the EU Data Boundary. No personal data SHALL be processed or stored outside the UK, Switzerland and the EU Data Boundary, which requires the platform's flex-routing option for AI prompts to be off. Each component's location SHALL be verified at environment setup and recorded as evidence. ⚠️ **AMENDED, Amendment A-09 (APPROVED 2026-10-16; revised the same day before approval).** All three environments are hosted in Switzerland (`crm17.dynamics.com`, measured 2026-10-05). The entity extractor runs there. AI prompts in a Swiss environment are processed by Azure OpenAI in the EU Data Boundary when *Move data across regions* is allowed (Microsoft Learn, as cited in TAD `ADR-075`), and the reviewer says that setting is on in DEV and TST/ACC: *"This is standard."* **Decided by the reviewer, 2026-10-16:** *"Yes, the AI prompt processed in EU is agreed."* Revitalise's legal office, quoted by the reviewer on 2026-10-16: *"Switzerland is recognised under the UK's adequacy regulations as providing an adequate level of protection for personal data, as confirmed in the ICO's guidance. So, from an international data transfer perspective, there is no issue with the Grant Application Solution being hosted in Switzerland simply because of its location."* The EEA is also covered by UK adequacy regulations. That is context, not verified by plan-agent, and the legal office's statement names only Switzerland. **Dependency met:** flex routing, which can process prompts outside the EU Data Boundary at peak load, is disabled at tenant level. The reviewer stated this on 2026-10-16 (*"Ah, the flex routing option is disabled on tenant level. Only EU handling"*); no agent has measured it. Previously read: *"its state is an open reviewer decision (TAD `A-R92`, `A-NS-32`)"*. Location recorded for the environments, and flex routing recorded as off on the reviewer's statement; not yet recorded for the signature and finance services. Previously read: *"not yet for the signature and finance services, or for flex routing"*. Previously: *"100% of processing, storage and backup SHALL remain in the UK region … Zero transfers outside the UK. Verified at environment setup."* | Compliance |
| NFR-010 | Retention SHALL be enforced automatically by status and trigger date (6 years / 12 months / 6 months per FR-048), with the enforcement run occurring at least monthly; irreversibly anonymised statistics are retained indefinitely. No deletion SHALL depend on a person remembering to act. | Compliance |
| NFR-011 | The backup and point-in-time restore window SHALL sit within the retention period of the records it covers, and all backups SHALL remain in the UK or in Switzerland, so a deleted record cannot survive indefinitely inside a backup. ⚠️ **AMENDED, Amendment A-09 (APPROVED 2026-10-16)**, following NFR-009. Previously: *"remain in the UK region"*. | Compliance |
| NFR-012 | No personal data SHALL be written to operational logs; operational logging is limited to run status, error message and record reference. | Compliance |
| NFR-013 | Only the fields needed to assess, decide, pay and report on a grant SHALL be collected (data minimisation, UK GDPR Article 5(1)(c)). | Compliance |
| NFR-014 | Every create, update and delete on a record holding personal data SHALL be recorded with timestamp (UTC), actor, action, affected record identifier, and before/after values. | Audit |
| NFR-015 | Access to the trustee review view SHALL be logged, recording which user opened it and when. | Audit |
| NFR-016 | The retention and erasure evidence log SHALL be retained as a durable record and SHALL contain no personal data. | Audit |
| NFR-017 | Automated redaction with a confidence below 85% SHALL be flagged for the process owner's attention; the threshold SHALL be adjustable after launch without redesign. ⚠️ **AMENDED, Amendment A-11 (PROPOSED 2026-10-19).** Previously read: *"Automated redaction with a confidence below 85% SHALL be routed to human review; the threshold SHALL be adjustable after launch without redesign."* | Compliance |
| NFR-018 | 100% of Borderline scoring outcomes and 100% of redactions SHALL receive human review before they progress or are disclosed. ⚠️ **AMENDED, Amendment A-11 (PROPOSED 2026-10-19).** Previously read: *"100% of Borderline scoring outcomes and 100% of low-confidence redactions SHALL receive human review before they progress or are disclosed."* | Compliance |
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
- Given the score is calculated, when it is compared to the threshold, then the application is flagged Auto-pass, Borderline or Auto-reject. → FR-014 ⚠️ *Amended, Amendment A-10 (APPROVED 2026-10-19): and given any rule of FR-014 applies, then the status is Auto-reject whatever the score.*
- Given the applicant's finances exceed the income ceiling, when the application is scored, then a separate income eligibility flag is set. → FR-015 ⚠️ *Amended, Amendment A-10 (APPROVED 2026-10-19, revision 2): and given the applicant does not receive means-tested benefits and their income band is above the ceiling, then the status is Auto-reject whatever their employment; given they receive means-tested benefits, then the income band does not reject. Revision 1 rejected only an applicant in work; withdrawn.*
- Given an application contains health-condition data and a free-text narrative, when the score is calculated, then neither influences the score. → FR-016
- Given the board changes the cut-off, when I update the threshold, then the change takes effect without a developer editing anything. → FR-017 ⚠️ *Amended, Amendment A-10 (APPROVED 2026-10-19, revision 2): the same holds when I change the amount limit for any type of break, or switch the savings or prior-funding rule off (AC-20).*
- Given I disagree with an automated status, when I override it, then the new status applies and the override is recorded. → FR-018
- Given an application is Borderline, when it is flagged, then it waits for my review before progressing. → FR-019
- Given applications were auto-rejected, when I open my active list, then they are not in it. → FR-020
- Given a day's applications have been scored, when the daily summary arrives, then it states how many were scored, auto-rejected and are awaiting my review. → FR-021
- Given a scored answer is missing, when the application is processed, then no final automated outcome is set and the case comes to me. → FR-022
- Given a Holiday accommodation request of £650 with no exceptional funding ticked, when it is scored, then it is Auto-rejected; given £500, or £650 with exceptional funding ticked, then the amount does not reject it. → FR-102 *(AC-13, Amendment A-10)*
- Given a Day trips or outings or Activity or Experience request of £101 with no exceptional funding ticked, when it is scored, then it is Auto-rejected; given £100, then the amount does not reject it. Given a Respite Care Facility stay or Other request of £501 with no exceptional funding ticked, then it is Auto-rejected; given £500, then the amount does not reject it. → FR-102 *(AC-14, Amendment A-10, revision 2; revision 1 put Respite Care Facility stay and Other under £100)*
- Given the applicant answered Yes to savings over £6,000, when the application is scored, then it is Auto-rejected whatever the score, employment or benefits. → FR-103 *(AC-15, Amendment A-10)*
- Given the applicant was funded by Revitalise and not more than 12 months ago, when the application is scored, then it is Auto-rejected. → FR-104 *(AC-16, Amendment A-10)*
- Given an application to which three rules apply, when I open it, then I see all three reasons in plain language, each with the values that decided it. → FR-105 *(AC-17, Amendment A-10)*
- Given I override an auto-rejected application, when I open it again, then the reasons are still there beside my override. → FR-105, FR-018 *(AC-18, Amendment A-10)*
- ~~Given an overridden application reaches the panel round, when a trustee opens it in any surface, then no auto-reject reason is shown. → FR-106 *(AC-19, Amendment A-10)*~~ **WITHDRAWN with FR-106, revision 2** (reviewer ruling, 2026-10-19).
- Given I have switched the savings rule off, when an application with savings over £6,000 Yes and a score of 45 is scored, then it is Auto-pass and no savings reason is written; the same holds for the prior-funding rule. → FR-017, FR-103, FR-104 *(AC-20, Amendment A-10, revision 2)*

### US-007: I stop anonymising by hand, but I keep the last word
**As** Emily, **I want** narratives redacted automatically with anything uncertain flagged to me,
**so that** I save three to four hours per board cycle without risking a missed name reaching a trustee.

**Acceptance Criteria:**
- Given an application becomes eligible for trustee review, when redaction runs, then personal identifiers in the free-text narrative are replaced with category labels. → FR-026
- Given a narrative mentions a specific age or place, when redaction runs, then they are generalised to an age band and a region. → FR-027
- Given redaction has run, when a trustee reads the case, then region, dates, score, holiday preferences and general condition information are still present. → FR-028
- Given redaction confidence is below the configured threshold, when the narrative is processed, then it is flagged for my attention. → FR-029 ⚠️ *Amended, Amendment A-11 (PROPOSED 2026-10-19). Previously read: "… then it is flagged to me and withheld from trustees."*
- Given a narrative has been redacted, flagged or not, when I have not released it, then trustees cannot see it, and when I review and release it, then trustees can see it. → FR-030 ⚠️ *Amended, Amendment A-11 (PROPOSED 2026-10-19). Previously read: "Given a narrative is flagged, when I review and release it, then trustees can see it."*
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
- Given I select an application, when the detail opens, then I see the same fields I receive today in the printed board pack — financial eligibility, condition and circumstance, and the helper, referee and emergency-contact block. → FR-035 *(Amendment A-05; appended at the end of this list, not inserted beside the FR-035 criterion above, so the existing AC numbers this document and the test report already cite are not renumbered)*
- Given a field is one the security profile withholds from me, when the detail opens, then I see the field named and marked restricted rather than blank or absent, so I can tell it from a question the applicant did not answer. → FR-078 *(Amendment A-05)*
- Given a field holds the applicant's own free text, when the detail opens, then I see only its redacted version, and I see a withheld state until redaction has been released for that record. → FR-079 *(Amendment A-05)*

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
- Given I am on the landing screen, when it loads, then I see the round's total applications received and the date the round opened. → FR-058 *(its "average received per day" clause moved to FR-080/AC-8, Amendment A-07)*
- Given I am on the landing screen, when I view it, then I see the round's exceptional-circumstance mix and the average exceptional funding requested. → FR-059
- Given I am on the landing screen, when I view the break-type breakdown, then I see the count, average cost and average grant requested for each type of break, with a total. → FR-060
- Given I am on the landing screen, when I view the demographic section, then I see the round's gender, ethnicity, age and applicant-type distributions. → FR-061 *(the "compared against the UK benchmark where one exists" clause was removed with FR-061's benchmark comparison — Amendment A-03 Resolution (continued), 2026-08-25)*
- Given I am on the landing screen, when I view the circumstance section, then I see the wellbeing and life-satisfaction distributions and the round's headline circumstance statistics. → FR-062
- Given I am on the landing screen, when I view the funding section, then I see the round's financial position and the charity's grant-giving capacity. → FR-063
- Given I am on the landing screen, when I view the applications-per-day figure, then I see it broken down month by month across all historic applications, with any month flagged that spikes or drops against its own trailing six months. → FR-080, FR-081 *(Amendment A-07)*

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

### US-024: Everything the applicant told us is on the record, and nothing else is
*(Amendment A-08, APPROVED 2026-09-25.)*

**As a** process owner, **I want** every answer an applicant gives on the website form to be on
their application, and nothing the form produced by itself, **so that** I never have to go back to
the website for an answer, and I never mistake a value the form generated for something the
applicant told us.

**Acceptance Criteria:**
- Given a submission with every always-shown question answered, when the record is created, then every one of those answers is stored. → FR-083
- Given a submission, when the record is created, then none of the form's own timestamps, status flags, payment fields, source page, IP address, calculated total or fixed hidden values is stored, and the entry id is held only as the duplicate key. → FR-083
- Given a question the applicant was not shown, or left blank, whether the website leaves it out, sends it empty or sends an unticked box, when the record is created, then that field is empty and no default value is written. → FR-084
- Given an applicant ticks "Google search" and "Healthcare professional (GP, nurse, social worker)" for how they heard about us, when the record is created, then both options are stored. → FR-085
- Given an applicant answers "No" to the Equality Act 2010 question and writes a description of how their disability affects them, when the record is created, then the "No" and the description are both stored as given. → FR-086, FR-088
- Given a carer applicant answers the person-supported Equality Act question and writes their description, when the record is created, then both are stored for the person supported. → FR-087, FR-089
- Given any of the four answers above is stored, when the circumstance score is calculated, then none of them is read. → FR-016
- Given an applicant answers "No" to whether someone is helping them, when the record is created, then "No" is stored and the helper-page consents are left empty. → FR-090, FR-084
- Given an applicant writes "Summer 2026" as the provisional date, when the record is created, then "Summer 2026" is stored as written and no start or end date is filled in. → FR-091
- Given an applicant answers "Applied and awaiting decision from" for other funding, when the record is created, then that answer is stored as itself, not as Yes or No. → FR-092
- Given the form does not show the middle-name field, when a submission is received, then no middle name is stored. → FR-093

### US-025: I stop taking gender out by hand
*(Amendment A-09, APPROVED 2026-10-16.)*

**As** Emily, **I want** the redacted copy to use neutral words for people, the way my Anonymisation
Key and examples do, and to read correctly, **so that** I no longer strip gender references by hand
before each board cycle, and trustees read a case that makes sense.

**Acceptance Criteria:**
- Given a narrative says *"My mum helps me and she is up at night"*, when redaction runs, then the trustee reads *"My parent helps me and they are up at night"*. → FR-094, FR-098
- Given a narrative says *"I help her with her mood"*, when redaction runs, then the trustee reads *"I help them with their mood"*. → FR-094
- Given a narrative names one person, *"Sam relies on me"*, when redaction runs, then the trustee reads *"They rely on me"*. → FR-095, FR-098
- Given a narrative names two different people, when redaction runs, then neither name is shown and the two are not merged into one *they*. → FR-095, FR-026
- Given a narrative says *"my grandmother and Mrs Patel"*, when redaction runs, then no gendered word and no title is shown. → FR-096
- Given a narrative says *"my wife and son"*, when redaction runs, then the trustee reads *"my partner and child"*. → FR-097
- Given a narrative says *"He receives PIP and requires care"*, when redaction runs, then the trustee reads *"They receive PIP and require care"*. → FR-098
- Given a redacted copy contains a misspelt word, when the spelling step runs, then the trustee copy is spelt correctly, no other word has changed, and the stored original is unchanged. → FR-099, FR-031
- Given a correction would change a label or bring back a replaced word, when the correction runs, then the copy is withheld and flagged to me. → FR-100
- Given a gendered word is left in a redacted copy, when the copy is checked, then it is withheld and flagged to me. → FR-101
- Given a narrative says *"I am Sam and I need a break"*, when redaction runs, then the trustee reads *"I am [NAME] and I need a break"*, never *"I am they"*; the same holds for *"My name is Sam"*. → FR-095 *(AC-11, Amendment A-11, PROPOSED 2026-10-19)*
- Given a narrative names two people and one of them follows a relationship word, *"my husband Derek and my sister Ann help me"*, when redaction runs, then the trustee reads *"my partner and my sibling help me"*: each name after a relationship word is dropped and the word neutralised although two people are named. → FR-095, FR-094 *(AC-12, Amendment A-11, PROPOSED 2026-10-19)*

### US-026: Recording the last payment starts the clock for me
*(Amendment A-12, APPROVED 2026-10-20.)*

**As** finance staff recording a disbursement, **I want** marking a payment as the final one to start the grant's
retention period, **so that** I never have to remember a second step, and the process owner is not left with a paid
grant whose records have no deletion date.

**Acceptance Criteria:**
- Given a grant whose application is "Approved", when I record a payment dated 14 November 2026 as final, then the grant's final payment date is 14 November 2026 and the application reads "Grant Paid". → FR-107, FR-108
- Given I enter that payment on 18 November 2026, when it is saved, then the grant's final payment date is still 14 November 2026. → FR-107
- Given a grant already has two payments, when I record a third that is not final, then the grant's final payment date and the application's status are unchanged. → FR-109
- Given a payment already recorded as final, when I open it and save it again without changing it, then nothing about the grant or the application changes. → FR-109
- Given a grant carries two payments recorded as final, dated 14 November and 2 December 2026, when the grant's date is read, then it is 2 December 2026. → FR-107
- Given I ticked final by mistake on the only final payment, when I remove the mark, then the grant's final payment date is empty and the application reads "Approved" again. → FR-110
- Given a payment recorded as final is later cancelled and no other payment is final, when it is saved as cancelled, then the same reversal happens. → FR-110
- Given a payment recorded as final is dated 14 November and I correct its date to 12 November, when it is saved, then the grant's final payment date is 12 November. → FR-110
- Given I record a payment as final that is not linked to a grant, when it is saved, then no grant or application changes and finance and the process owner can see the payment and why it was not applied. → FR-111
- Given the application is "Withdrawn" when a final payment is recorded, when it is saved, then the status is unchanged, the grant's date is recorded, and the case is reported to finance and the process owner. → FR-108, FR-111
- Given a final payment is recorded, when the process owner looks at the pre-issue duplicate check, then nothing in this change has run it. → excluded; `wbs:8.5`, FR-023
- Given I tick final on a payment that has no payment date, when I try to save it, then it is not saved as final and I am told a payment date is required; the grant and the application are unchanged. Given the same undated final payment arrives by an API or any other route, then it is refused in the same way, no date is recorded, no clock starts and the application is unchanged. → FR-107 *(AC-12, revision 2026-10-20; carve-out for non-form routes removed on decision "4")*
- Given a Pending payment dated 14 November 2026, when I save it as final, then its status reads Issued as soon as it is saved, whichever route saved it, its last-modified-by shows me, the grant's final payment date is 14 November 2026 and the application reads "Grant Paid". → FR-112, FR-107, FR-108 *(AC-13; timing and last-modified-by added on decision "4")*
- Given a payment that is already Cleared, when I save it as final, then it stays Cleared, and so do Issued; a Cancelled payment stays Cancelled. → FR-112 *(AC-14)*
- Given a Pending payment saved as final (so Issued), when I remove the final mark, then the grant and application are put back as in AC-6 and the payment still reads Issued. → FR-110, FR-112, OQ-059 (answered: *"No. payment final means final."*) *(AC-15)*
- Given a grant at "Acceptance Signed" whose payment dated 14 November 2026 is saved as final, then the grant's own status reads "Paid", the grant's final payment date is 14 November 2026 and the application reads "Grant Paid". → FR-113, FR-107, FR-108 *(AC-16)*
- Given a grant at "Awarded" or "Acceptance Issued" when a final payment is saved, then the grant's status is unchanged and finance and the process owner see the payment, the grant and why its status was not moved. → FR-113, FR-111 *(AC-17)*
- Given the only final payment on a grant at "Paid" has its final mark removed, or is cancelled, then the grant returns to "Acceptance Signed". Given another payment is still final, then the grant stays "Paid". → FR-113, FR-110 *(AC-18)*
- Given a non-final payment is recorded, or a final payment is saved again unchanged, then the grant's status does not change. → FR-113, FR-109 *(AC-19)*

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
(financial record) act as sub-processors, storing data in the UK or Switzerland, with AI prompts processed in the EU Data Boundary (NFR-009, amended by Amendment A-09, APPROVED 2026-10-16, which depends on flex routing being off; previously *"all within the UK"*). The named service identity
`svc-grantautomation` owns the external connections; it is not a personal login.

### 7.1 Data classification (satisfies C-DOM-001 at plan level)

| Tier | Examples in this solution | Data subjects | Handling |
|---|---|---|---|
| **Special category (UK GDPR Art. 9)** | Applicant and support-recipient condition profiles; "other condition" free-text; health/disability free-text in the narrative; benefit status; employment status; exceptional-circumstance category; ethnic group where captured | Applicants; cared-for / support-recipients | Highest restriction **for the free text and for the columns held in `REV_TrusteeRestricted`** — administrator role and service identity only; no value is returned to a trustee from any surface. Free text is redacted before trustee review (FR-079). ⚠️ **CORRECTED, Amendment A-05, 2026-08-27 — the previous wording, "Never shown to trustees", was already inaccurate before this amendment and is not merely overtaken by it.** The *categorical* Art. 9 columns `rev_conditionprofile` and `rev_supportrecipientconditionprofile` carry `IsSecured=0`, are deliberately absent from `REV_TrusteeRestricted`, and are trustee-visible **by design** under the rule §7.1a states in full: *"Categorical answers are trustee-visible. Identity and free text are not."* `rev_exceptionalcircumstance` joined them by D-6. **Benefit status and employment status remain undisclosed to trustees** — they stay in the profile and A-05 does not move them — but the enforcement point is the platform's column security, not the app declining to query the column, so the field may now appear on the trustee screen in a restricted state (FR-078) with no value behind it. Per-column detail at §7.1b. |
| **Personal (UK GDPR Art. 6)** | Name, address, postcode, email, phone, date of birth, bank details; helper, referee, group-member and emergency-contact identity | Applicants; helpers; referees; group members; emergency contacts | Restricted. Identity attributes hidden from trustees; bank details behind the finance role only. ⚠️ **Clarified, Amendment A-05, 2026-08-27.** "Hidden from trustees" is enforced by `REV_TrusteeRestricted` returning no value — which is what FR-036 and NFR-003 already require of the platform — and not by the trustee app omitting the column from its query. From A-05 the trustee detail view requests the helper, referee and emergency-contact identity columns and renders them as a restricted state (FR-078); no value reaches the trustee. Per-column detail at §7.1b. |
| **Pseudonymised** | Pseudonymised reference (e.g. `REV-A-00001`), age range, location area, costs, scores, redacted narrative | Applicants | Still personal data. Visible to trustees. Follows the parent record's retention clock. |
| **Anonymised** | Snapshot statistics: age range, location area, condition areas, outcome, amount — no identifiers, never linked back | None | Not personal data. May be kept indefinitely. |
| **Round-level aggregate** *(new, Amendment A-03, APPROVED 2026-08-25, WBS 6.9)* | Landing-screen statistics (FR-057–FR-063): application/exceptional-circumstance/break-type counts and percentages, cost and funding averages, demographic distribution percentages, wellbeing and score-distribution counts — computed **live** across the *current* round's Application and Review records; financial/capacity figures come from a separate finance-maintained record, not derived from Application/Grant/Payment data (OQ-036) | None directly identified | Materially lower restriction than the Pseudonymised detail screen above — no single application's data is shown for the counts, percentages and distributions in this row. **Not the same tier as Anonymised above**, which covers only retained post-deletion snapshots (FR-055): these aggregates are computed live over current special-category and personal source data, so a small category count could in principle narrow toward an individual (§7's Amendment A-03, Finding 4). ⚠️ **No minimum-cell-size control is applied to those categorical counts, percentages and distributions.** Plan-agent proposed one (NFR-027); the reviewer explicitly overrode it (Amendment A-03 Resolution, 2026-08-25 — *"no minimum group size. The whole point of the code app is for trustees to review items and the column security profile scrubs aways personal information"*), naming the app's existing field-level security profile (NFR-001/NFR-003) as the control for personal-data exposure instead. Recorded here as a risk-acceptance decision, not a silent gap — see OQ-035. ⚠️ **CORRECTED, TAD Revision 6 §6.3.5 / ADR-039, 2026-08-28 — the *"cost and funding averages"* named in this row are a different case, and the reviewer's stated basis above does not reach them.** `rev_costs`, `rev_amountrequested` and `rev_additionalamountrequested` are all `IsSecured=0` and absent from `REV_TrusteeRestricted` — the field-level security profile this row credits with the exposure control **does not exist for these three columns**, and cannot: a Money column's automatic `_base` twin has `CanBeSecuredForRead=False`, a documented platform limitation. Without a floor, "no single application's data is shown" is **false** for the four money measures these three columns feed (FR-059's average exceptional-funding amount requested; FR-060's average holiday cost, average grant amount requested and percentage of total cost) — at a population of one, the "average" **is** that applicant's exact figure, to the penny, satisfying `C-DOM-001`'s requirement that the classification match the control actually implemented. **A `k = 5` minimum-population control now applies to these four measures only** (`RoundStatisticsMoneyMeasureMinimumPopulation`, answered by the reviewer 2026-08-28 against the TAD's own OQ-043 — distinct from this SDD's own OQ-043 at §9, a numbering coincidence between the two documents): each measure is withheld unless its own population is ≥ 5, which is what keeps "no single application's data is shown" true of them. The categorical decision at OQ-035 is unaffected. |
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

### 7.1b Per-column classification for the trustee detail screen (Amendment A-05, satisfies C-DOM-001 and NFR-030)

⚠️ **New subsection, Amendment A-05, APPROVED 2026-08-27.** FR-035 now surfaces every board-pack
field on the trustee detail screen, so every column it names is classified here before it is built.
Values were read from `Entities/rev_application/Entity.xml` and from the real `<AttributeName>`
entries in `Other/FieldSecurityProfiles.xml`; the working is in Amendment A-05, Finding 1. **No
column's classification, `IsSecured` value or profile membership is changed by this amendment** —
this table records what is already true and what a trustee consequently sees. It also closes the gap
A-02's Resolution left open, which noted that §7.1 named no classification row for the care-support
columns.

| Column | Classification | Secured / in `REV_TrusteeRestricted` | What a trustee sees |
|---|---|---|---|
| **Financial eligibility** | | | |
| `rev_incomeflag` | Personal (Art. 6) | No | The value |
| `rev_incomeband` | Personal (Art. 6) | No | The value |
| `rev_savingsover6000` | Personal (Art. 6) | No | The value |
| `rev_receivesbenefits` | **Special category (Art. 9)** — benefit status | Yes | Restricted state, no value (FR-078) |
| `rev_benefitprovider` | **Special category (Art. 9)** — benefit status | Yes | Restricted state, no value (FR-078) |
| `rev_employmentstatus` | **Special category (Art. 9)** — D-1, §7.1a | Yes | Restricted state, no value (FR-078) |
| `rev_unabletofundexplanation` | Personal (Art. 6) — secured financial free text. Correctly **not** in the special-category register | Yes | Withheld until redacted (FR-079); **no counterpart column exists yet** |
| **Condition and circumstance** | | | |
| `rev_conditionprofile` | **Special category (Art. 9)** | No — trustee-visible by design, §7.1a | The value |
| `rev_supportrecipientconditionprofile` | **Special category (Art. 9)** | No — trustee-visible by design, §7.1a | The value |
| `rev_exceptionalcircumstance` | **Special category (Art. 9)** — reclassified by A-04 | No — D-6, deliberately absent from the profile | The value |
| `rev_otherconditionraw` | **Special category (Art. 9)** — free text | Yes | Withheld until redacted (FR-079); **no counterpart yet** |
| `rev_supportrecipientotherconditionraw` | **Special category (Art. 9)** — free text | Yes | Withheld until redacted (FR-079); **no counterpart yet** |
| `rev_exceptionalfundingdetail` | **Special category (Art. 9)** — free text | Yes | Withheld until redacted (FR-079); **no counterpart yet** |
| `rev_otherexceptionalcircumstance` | **Special category (Art. 9)** — free text | Yes | Withheld until redacted (FR-079); **no counterpart yet** |
| `rev_narrativeraw` / `rev_narrativeredacted` | **Special category (Art. 9)** / redacted output | Yes / No | Unchanged — the counterpart exists and is already wired (FR-031) |
| **Helper, referee, emergency contact** | | | |
| `rev_helperorganisation` | Personal (Art. 6) | No | The value |
| `rev_helperrelationship` | Personal (Art. 6) | No | The value |
| `rev_helperdeclarationconsent` | Personal (Art. 6) | No | The value |
| `rev_helperdeclarationconsentdate` | Personal (Art. 6) | No | The value |
| `rev_helpername`, `rev_helperemail`, `rev_helperphone` | Personal (Art. 6) — identity | Yes | Restricted state, no value (FR-078) |
| `rev_refereename`, `rev_refereeemail`, `rev_refereephone` | Personal (Art. 6) — identity | Yes | Restricted state, no value (FR-078) |
| `rev_emergencycontactname`, `rev_emergencycontactphone` | Personal (Art. 6) — identity | Yes | Restricted state, no value (FR-078) |

**Lawful basis (satisfies C-DOM-002).** No new lawful basis is required and none is created. Every
column above sits inside a grouping §7.2 already covers, taken from Revitalise's Privacy Notice of
20 February 2026: the financial-eligibility and condition columns under **Application** (Art. 6
necessary to assess and administer the grant; Art. 9(2)(b) social protection and 9(2)(h) health and
social care); the support-recipient condition profile under **Support-recipient / cared-for person**;
the helper columns under **Helper acting for an applicant**; and the referee and emergency-contact
columns under **Referees, group members, emergency contacts**.

**Why no classification changes.** This amendment changes the *surface* on which existing data is
presented, not the data, its security or its basis. The nine unsecured columns were already
trustee-visible by design; the eleven secured columns remain undisclosed and the platform, not the
app, is what withholds them. The genuinely new work is the five redacted counterpart columns FR-079
requires, which do not yet exist — see Amendment A-05, Finding 2, and note that a redacted
counterpart is deliberately **not** added to `constraints/domain/special-category-register.yml`, on
the reasoning that file already records for `rev_narrativeredacted`.

### 7.1c Per-answer classification for the intake transfer rule (Amendment A-08, satisfies C-DOM-001, C-DOM-002 and NFR-030)

⚠️ **New subsection, Amendment A-08, APPROVED 2026-09-25.** It classifies every answer that FR-085
to FR-093 newly store, before any of them is built. The *Field* column names the TAD rev 10
Appendix C §C.8 column, for traceability only. The column design is the TAD's. Fields marked
*(exists)* were read from `Entities/rev_application/Entity.xml` on 2026-09-25. Every other field is
specified by the TAD and not yet built (`TD-010` / `TD-011`).

| Answer (FR) | Field | Classification | Secured, per TAD rev 10 | What a trustee sees |
|---|---|---|---|---|
| How did you hear about us (FR-085) | `rev_hearaboutus` *(exists)* | Personal (Art. 6), low sensitivity: a referral-source category on an identified applicant's record | No | Not on any trustee surface. FR-035 does not name it |
| Hear-about-us "other" wording (FR-085) | `rev_otherhearaboutus` *(exists)* | Personal (Art. 6), low sensitivity: a place or source name, the same kind of text as `rev_breaklocation` | No | Not on any trustee surface |
| Applicant's Equality Act answer (FR-086) | `rev_hasequalityactdisability` | **Special category (Art. 9)**: disability status | Yes; special-category register row. **TAD change owed:** trustee-visible under OQ-051 | The value (OQ-051, answered 2026-09-25) |
| Person supported's Equality Act answer (FR-087) | `rev_supportrecipienthasequalityactdisability` | **Special category (Art. 9)** | Yes; register row. **TAD change owed:** trustee-visible under OQ-051 | The value (OQ-051, answered 2026-09-25) |
| Applicant's disability description (FR-088) | `rev_disabilityimpactdescription` | **Special category (Art. 9)**: health free text | Yes; register row | Only the redacted counterpart, withheld until released (FR-079; OQ-051, answered 2026-09-25) |
| Person supported's disability description (FR-089) | `rev_supportrecipientdisabilityimpactdescription` | **Special category (Art. 9)**: health free text | Yes; register row | Only the redacted counterpart, withheld until released (FR-079; OQ-051, answered 2026-09-25) |
| Someone helping (FR-090) | `rev_someonehelping` | Personal (Art. 6): a fact about how the application was made | No | Not on any trustee surface |
| Provisional date (FR-091) | `rev_provisionaldate` | Personal (Art. 6): a break fact in the applicant's words, the same kind of text as `rev_breaklocation` | No | Not bound by this amendment (`wbs:6.3` / EF-09) |
| Other-funding status (FR-092) | `rev_otherfundingstatus` | Personal (Art. 6): a financial circumstance, the same kind as `rev_incomeband` | No | Not on any trustee surface. FR-035 unchanged |
| Source of additional funding (FR-092; *added by Amendment A-09*) | `rev_otherfundingsource` *(exists, `IsSecured=0`, read 2026-10-16)* | Personal (Art. 6): a financial circumstance in the applicant's words, usually a funder's name. Free text, so it can carry health or third-party detail | No, as built. **Flagged to architect-agent** (A-09 item 3) | Nothing. No redacted copy, by reviewer decision 2026-10-16 (§4 E+) |
| Awaiting decision from (FR-092; *added by Amendment A-09*) | `rev_awaitingdecisionfrom` *(exists, `IsSecured=0`, read 2026-10-16)* | Personal (Art. 6): the same kind of text as the row above | No, as built. **Flagged to architect-agent** (A-09 item 3) | Nothing. No redacted copy, by reviewer decision 2026-10-16 (§4 E+) |
| Middle name, suffix (FR-093, conditional) | `rev_middlename`, `rev_namesuffix` | Personal (Art. 6): identity | Yes, as identity (`REV_TrusteeRestricted`) | Restricted state, no value (FR-078), if bound |
| State or province (FR-093, conditional) | *none specified yet*; the TAD says it needs one if shown | Personal (Art. 6): address, so identity | Must follow the address columns | Nothing |

**What stops being stored, and why that changes no classification.** Under FR-083 the form's
generated values are not transferred (TAD rev 10 Appendix C §C.6). The date-of-birth column stays
empty, because the form does not ask for it (FR-001, FR-027). §7.1's *Personal* row lists *date of
birth* as an example of the tier. The tier is unchanged; this solution simply receives no value for
that example.

**The four special-category answers against the securing rule.** §7.1a's rule, *"Categorical
answers are trustee-visible. Identity and free text are not."*, puts the two Equality Act answers
with `rev_conditionprofile` and the two descriptions with `rev_otherconditionraw`. TAD rev 10 secures
all four. **OQ-051 was answered on 2026-09-25 in line with that rule.** The two Equality Act answers
are released to trustees, so the TAD must change them, and NFR-031's necessity record applies. The
necessity is the reviewer's A-05 basis: trustees already receive these answers in the printed board
pack. The two descriptions stay secured, and trustees see only their redacted counterparts.

**Lawful basis (satisfies C-DOM-002).** No new lawful basis is created, and none is needed. The
bases are Revitalise's own, from its Privacy Notice of 20 February 2026, as §7.2 records them.

| Answer | Art. 6 basis | Art. 9 condition | Grouping in §7.2 |
|---|---|---|---|
| Applicant's Equality Act answer and disability description | Necessary to assess and administer the grant | Art. 9(2)(b) social protection; 9(2)(h) health and social care | Application: *"disability data … processed to assess eligibility and need only"* |
| Person supported's Equality Act answer and disability description | Necessary to assess the grant | Art. 9(2)(b); 9(2)(h) | Support-recipient / cared-for person |
| Hear-about-us, someone helping, provisional date, other-funding status, source of additional funding and awaiting decision from *(last two: Amendment A-09)* | Necessary to assess and administer the grant | n/a | Application |
| Middle name, suffix, state or province | Necessary to assess and administer the grant | n/a | Applicant (identity, contact) |

**Why the Art. 9 condition is not raised as a question.** The four answers are disability data about
the two people §7.2 already covers, collected for the purpose it already states. What the existing
basis does **not** do on its own is put them in the DPIA and the RoPA. That is the line below.

**Data minimisation (NFR-013), stated plainly.** The reviewer's rule places the minimisation decision
on the **form**, which is the charity's decision about what to ask. The intake stores what was asked
and answered, and nothing else. This is the position §7.1a already took for A-04: *"storing an
answer already being collected is not an increase in processing, and discarding it while continuing
to ask for it is the worse position."* It reverses TAD rev 9's reading that not storing the Equality
Act and description answers was minimisation. The applicant was asked, so the answer is kept.

**DPIA line owed (OQ-048, widened).** Proposed wording for the DPIA's data inventory and the RoPA's
Art. 30(1)(c) categories. The DPO confirms or rewrites it:

> *Application, special category (Art. 9(2)(b) and 9(2)(h)): the applicant's answer to whether they
> have a disability as defined by the Equality Act 2010, and their own description of how that
> disability affects them; on the carer routes, the same answer and description for the person
> supported. Collected on the application form, stored as given, used to assess eligibility and
> need, never used in the automated score, held behind column-level security with auditing, and
> retained and erased with the application record. Trustee exposure: the Yes/No answers are shown to trustees;
> the descriptions are shown only after AI redaction and human release of the redacted text.* ⚠️ *Amended, Amendment A-11 (PROPOSED 2026-10-19). Previously read: "… human release of low-confidence results."*

### 7.1d Per-column classification for the auto-reject rules and reason (Amendment A-10, satisfies C-DOM-001 and C-DOM-002)

⚠️ **New subsection, Amendment A-10, APPROVED 2026-10-19.** Every column the new rules read is already
classified, and is restated here so the rules' inputs are in one place. The reason text is new content in
an existing column, and is classified here. Values read 2026-10-19 from `Entities/rev_application/Entity.xml`.
Lawful basis: all are Application financial answers or outputs, under §7.2's Application row (Art. 6,
necessary to assess the grant). No new basis is needed. **Revision 2:** the employment status is no longer
read, so revision 1's Art. 9(2)(b) basis for it is not needed here, and the reason text no longer repeats a
special-category answer (A-10 Finding 4).

| Column | Read by | Classification | Secured | What a trustee sees |
|---|---|---|---|---|
| `rev_amountrequested` | FR-102 | Personal (Art. 6) | No | The value (FR-035 total) |
| `rev_breaktype` | FR-102 | Personal (Art. 6) | No | The value |
| `rev_exceptionalfundingrequested` | FR-102 | Personal (Art. 6), §7.1a | No | The value |
| `rev_savingsover6000` | FR-103 | Personal (Art. 6), §7.1b | No | The value |
| `rev_incomeflag` (from `rev_incomeband` and, under its 2026-09-18 gate exception, `rev_receivesbenefits`) | FR-015 | Personal (Art. 6), §7.1b | No | The value |
| ~~`rev_employmentstatus`~~ | **Not read, revision 2** (reviewer, 2026-10-19). Revision 1: ~~FR-015, *in work or not* only~~ | Special category (Art. 9), §7.1a D-1 | Yes | Restricted state, no value (FR-078) |
| `rev_receivedfundingbefore`, `rev_morethan12monthsago` | FR-104 | Personal (Art. 6) | No | Unchanged by this amendment |
| `rev_autorejectreason` | written by FR-105 | **Personal (Art. 6), financial** (revision 2): names the amount and break type, the income band and ceiling, savings, prior funding and score; never employment, benefits, disability or health. Revision 1: ~~Special category (Art. 9), because the income reason repeats the employment answer~~ | No, and not required (revision 2) | **Nothing.** Shown only on the admin app's main form, which is not shared with the trustee role (reviewer ruling, 2026-10-19); no trustee portal screen or query names it (checked 2026-10-19) |
| `rev_scoringaudit` | repeats FR-105's text | **Personal (Art. 6), financial**, same reason (revision 2). Revision 1: ~~Special category (Art. 9), same reason~~ | No, and not required (revision 2) | **Nothing**, as above |

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
| **Art. 5(1)(f)** integrity and confidentiality | Appropriate security | Least privilege, field-level restriction of identity columns, separation of duties on bank data, storage in the UK or Switzerland, AI prompts in the EU Data Boundary, flex routing off (NFR-009, amended by A-09), connector restriction (NFR-001 to NFR-009) |
| **Art. 5(2)** accountability | Demonstrate compliance | Native field-change auditing of every create/update/delete (NFR-014); app-access logging (NFR-015); retention/erasure evidence log (FR-054, NFR-016) |
| **Art. 6** lawful basis | Documented per entity | §7.2 above |
| **Art. 9** special-category condition | Art. 9 condition required | Art. 9(2)(b) social protection and Art. 9(2)(h) health and social care, per the Privacy Notice |
| **Art. 15** right of access | SAR fulfilment | Complete extract producible for a named individual (FR-053). ⚠️ No internal response-time SLA recorded — OQ-023 |
| **Art. 17** right to erasure | Erasure path with carve-outs | On-demand erasure across the system of record and every linked copy including referees, helpers, group members and emergency contacts (FR-051); legal-hold carve-out disclosed to the requester (FR-052) |
| **Art. 30** records of processing | Art. 30(1) controller record and Art. 30(2) processor record | Both drafted in the RoPA v0.1 — **concept status, not confirmed**; published DPO contact details still outstanding (OQ-009) |
| **Art. 32** security of processing | Technical and organisational measures | Least privilege; field-level column restriction; separation of duties; MFA and Conditional Access; storage in the UK or Switzerland, AI prompts in the EU Data Boundary, flex routing off (NFR-009, amended by A-09); connector policy; native auditing; automated retention and deletion |
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

⚠️ **Amendment A-10 (APPROVED 2026-10-19) widens what is automated.** Auto-reject is now also set on
financial eligibility: the amount requested over the limit for the break type without an exceptional
request (FR-102), an applicant not on means-tested benefits with income above the ceiling (FR-015), savings over £6,000
(FR-103) and prior funding within 12 months (FR-104). None of them reads a disability, health or employment
answer (FR-016 annotation, revision 2). The reviewer stated on 2026-10-19 that Emily checks every auto-reject and agrees or
overrides it, with every reason in front of her (FR-105). That is the stronger form of review described
above. An override is recorded (FR-018); an agreement is not. OQ-005's scope is widened to match.

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
| R3 | An applicant is wrongly rejected by the automated score or, since Amendment A-10, by an automated financial eligibility rule, without meaningful human review | High | **Medium — pending DPO confirmation (OQ-005).** Emily checks every auto-reject with its reasons (reviewer, 2026-10-19; FR-105) |
| R4 | Health free-text kept longer than necessary on granted records (6-year retention) | Medium | **Medium — DPO decision open (OQ-006)** |
| R5 | Bank or payment details accessed by someone outside the finance role | Medium | Low |
| R6 | Data stored outside the UK and Switzerland, or processed outside them and the EU Data Boundary (for example, AI prompts under flex routing), breaching the residency commitment *(amended by Amendment A-09; previously "outside the UK")* | Medium | Low. Flex routing is disabled at tenant level (reviewer, 2026-10-16). Previously read: *"Low until flex routing is confirmed off (TAD `A-R92`)"* |
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
arrangements at environment setup (builder / Wanstor; OQ-018, OQ-019). ⚠️ **Amendment A-09:** the requirement A5 verifies is now *storage in the UK or Switzerland, AI prompts inside the EU Data Boundary, flex routing off* (NFR-009). The environments are verified as Swiss. Flex routing is off at tenant level, on the reviewer's statement of 2026-10-16 (*"Ah, the flex routing option is disabled on tenant level. Only EU handling"*), not an agent measurement. The signature and finance services are not yet verified. Previously read: *"The signature and finance services, and the flex-routing state, are not yet verified."*

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
| OQ-003 | What is the income ceiling value, and does an income-only failure reject outright or flag for review? | Board / Emily | The first PRD seed of the income ceiling by `provisioning/dataverse/seed-settings.ps1` *(re-dated by Amendment A-10; previously "Before Automation #2 build")* |
| | ⚠️ **HALF ANSWERED 2026-10-19, Amendment A-10 (APPROVED 2026-10-19).** *Reject or flag:* the reviewer decided an income-only failure rejects outright, **only when the applicant does not receive means-tested benefits** (FR-015, revision 2): *"The flow should only look at income band when the applicant has not receiving means tested benefits. Employment status doesn't have to be checked."* Revision 1's *"only when the applicant is in work"* is withdrawn. *The value:* the reviewer's revision 1 rule named £25,000, the value already seeded in DEV and TST/ACC. **Narrowed to:** confirm £25,000 as the board's value for PRD. **Default:** PRD stays unseeded until confirmed, as `provisioning/deploymentSettings/prd-settings.json` requires today. **Event:** the first PRD seed of the income ceiling by `provisioning/dataverse/seed-settings.ps1`. | | |
| OQ-004 | **DPO decision (DPIA A1):** is field-level column security an acceptable trustee control in place of the manual, single-key-holder anonymisation? | DPO | **Before build starts** |
| OQ-005 | **DPO decision (DPIA A2):** does automatic rejection at the threshold, with oversight and override, satisfy Revitalise's automated-decision position under the DUAA 2025? | DPO | Before the first PRD deploy of the scoring flow carrying FR-102 to FR-105 (`wbs:2.4`, `2.7`) *(re-dated by Amendment A-10; previously "Before build starts")* |
| | ⚠️ **SCOPE WIDENED, Amendment A-10 (APPROVED 2026-10-19). Not a new question.** The decision now also covers automatic rejection on the amount requested, income for an applicant not on means-tested benefits, savings, and prior funding (FR-015, FR-102 to FR-104). None reads a disability, health or employment answer (revision 2). **Default, as the reviewer described it on 2026-10-19:** Emily checks every auto-reject with all its reasons (FR-105) and agrees or overrides it (FR-018); only an override is recorded. **Event (also in the due column):** before the first PRD deploy of the scoring flow carrying FR-102 to FR-105 (`wbs:2.4`, `2.7`). | | |
| OQ-006 | **DPO decision (DPIA A3):** is six-year retention of the health free-text preferred over earlier minimisation? | DPO | **Before build starts** |
| OQ-007 | Confirm the expected number of applications per round and per year, so the scale of processing is on record (DPIA §2.2 TBC) | Emily | Before DPIA sign-off |
| OQ-008 | Confirm the role-membership review cadence — quarterly, or at the start of each panel round? | Emily / DPO | Before DPIA sign-off |
| OQ-009 | Confirm the published DPO contact details for the RoPA | Revitalise | Before RoPA finalisation |
| OQ-010 | Confirm the named DPO is current, that Emily is the accepted process owner, and whether a second processor (Jan) is assigned | Revitalise | Before sign-off |
| OQ-011 | Finalise the anonymisation rules: exactly which fields are stripped, which are generalised (age → band, location → region), and what stays | Emily / DPO | Before Automation #5 build |
| | **New evidence, Amendment A-02:** the sample trustee PDF and the Dataverse schema show at least two more free-text columns carrying the same class of content as the narrative — `rev_unabletofundexplanation` and `rev_exceptionalfundingdetail`/`rev_otherexceptionalcircumstance` — neither currently in the `rev_narrativeraw`/`rev_narrativeredacted` redaction pair. Recommend Automation #5's redaction scope explicitly cover them before build. | | |
| | ✅ **RESOLVED 2026-08-27 — Amendment A-05.** Reviewer's exact words: *"All fields need to be in. All fields with free text data will be scrubbed with AI. Identifying information will be protected by the security profile."* Read literally: **nothing is stripped from the trustee view on classification grounds** — every board-pack field is included (FR-035); **every free-text column is redacted before it is shown** (FR-079), which settles A-02's recommendation above and extends the redaction scope to five columns with no counterpart today; and **identity is held back by `REV_TrusteeRestricted`**, rendering as an explicit restricted state (FR-078). The question's remaining half — generalisation, age → band and location → region — is unchanged and already carried by §7.1's Pseudonymised tier, which names age range and location area as what trustees see. **Two consequences, neither re-opening this question:** the five redacted counterpart columns are new schema work for architect-agent (Amendment A-05, Finding 2), and the widened redaction scope must be written into the DPIA and RoPA (folded into OQ-048). | | |
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
| | ✅ **RESOLVED 2026-08-27 — yes, capture it.** Reviewer: *"that should be present as this gets filled in on the website form"* (confirmed: `docs/Import/Application Data Export(Sheet1).csv` column 150, "Ethnic group", real). `rev_ethnicgroup` added to `rev_applicant` — placement (`rev_applicant`, not `rev_application`) and column security matching `rev_gender` were proposed and approved together — secured under `REV_TrusteeRestricted`, option list ground-truthed from `Round 3 Stats.pptx`'s own "Ethnic Group" chart (six categories summing to exactly 1.0). Intake flow now maps `ethnic_group` to it. **Narrower and still open:** formal DPIA sign-off recording this Article 9 collection is Emily/DPO's own step (OQ-030), not satisfied by the schema change alone. Historical applications predating this column do not backfill. | | |
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
| | ⚠️ **SCOPE WIDENED, Amendment A-05, 2026-08-27 — not re-opened, and not a new question.** The same DPIA/RoPA amendment now also has to record the widened redaction scope FR-079 introduces. The DPIA describes redaction as covering *"the free-text narrative"* — singular; FR-079 extends it to five further free-text columns. **The trustee audience and the app surface are not new to the DPIA**, which already states *"Trustees review eligible applications through a dedicated app that hides identity by field-level security, and record a verdict"* — the Code App is that app, which supports the reviewer's own framing that the process is being automated rather than newly created. Handled the way §7.1a handled OQ-004 and OQ-006: the surface changes, the question stays open, and the DPO is told rather than left to discover it. | | |
| | ⚠️ **SCOPE WIDENED AGAIN, Amendment A-08 (APPROVED 2026-09-25). Not a new question.** The same DPIA and RoPA amendment must now also name four special-category answers the intake begins storing: the Equality Act 2010 answer and the disability description, for the applicant and for the person supported (FR-086 to FR-089). **No new Art. 9 condition is involved**, because §7.2's existing groupings cover them (§7.1c). Proposed wording is at §7.1c. **Event:** before the first PRD deploy that creates those four columns (`wbs:4.3`), because that is the first time real applicants' answers are held. | | |
| | ⚠️ **SCOPE WIDENED A THIRD TIME, Amendment A-09 (APPROVED 2026-10-16). Not a new question.** The same DPIA and RoPA amendment must now also record three things: the solution is hosted in Switzerland, on the UK adequacy basis Revitalise's legal office confirmed, and AI prompts are processed in the EU Data Boundary (NFR-009); the redacted copy is rewritten with neutral words for people (FR-094 to FR-098); and, if `CO-009` goes ahead, its spelling is corrected by a second model step that reads only redacted text (FR-099). No new lawful basis or Art. 9 condition is involved: the text is the same Application free text, used for the same purpose. **Event:** before the first PRD deploy of the scrubbing flow that writes neutral words (`wbs:5.6`). | | |
| OQ-049 | **What numeric definition of "sudden spike or drop" gates FR-081's anomaly flag?** *(Amendment A-07, `CO-005`, `wbs:6.10`)* Neither CO-005 nor the EF-11 walkthrough states a threshold, and this is a business judgement about what a board of trustees should be alerted to, not a modelling default plan-agent or architect-agent may pick — the same standing this document already gives `k = 5` (OQ-043, *"this value is a disclosure control, not a tunable"*). **Architecturally-derived default, per this document's own standing rule (§ "Every open question is dated against an EVENT"):** until answered, FR-081 flags no month — an unflagged screen is fail-safe and matches the existing convention for an unseeded `rev_setting`-backed control. | Reviewer | **Gates FR-081 only, not the rest of `wbs:6.10`** — before `development-agent`'s `wbs:6.10` dispatch encodes a flagging rule; FR-080's recompute and FR-082's settings can build and ship independently with FR-081 rendering its fail-safe unflagged state |
| | ✅ **RESOLVED 2026-09-19 — reviewer.** A month is flagged when it deviates from its own trailing six-month mean by more than a threshold, held as a **third, configurable `rev_setting`** (not a hardcoded literal), starting value **50%**. See FR-081 for the restated rule. **Not fully closed at architecture level:** TAD Revision 9 / ADR-049 designed FR-080's grouping mechanism and FR-082's two settings but did not design for this third setting or the mean/deviation comparison logic inside FR-080's month-by-month loop — routed back to architect-agent for a further TAD pass (naming the setting, extending §5.1.3's flow design), same division of labour as the original "Flagged for architect-agent" section above. | | |
| OQ-050 | **What are the actual seed values for FR-082's two new settings** — the date from which this system's application record is complete, and the count of applications the charity received before that date? *(Amendment A-07, `CO-005`, `wbs:6.10`)* These are historic facts about the charity's own grant-giving history, not derivable from any source in this repository or decidable by architect-agent at TAD stage — see also Amendment A-06's own 16 February 2026 reference date, which this answer should be checked against rather than assumed to match, since CO-005's framing ("this system started later than the charity itself did") implies the charity's own history may predate that date. | Emily / Reviewer | Before the `post_deploy` seeding step of `wbs:6.10`'s first environment deploy — FR-082 SHALL render its fail-safe unseeded state until then |
| | ✅ **RESOLVED 2026-09-19 — reviewer.** 16 February 2026 is confirmed to be **both** the tracking-start date **and** the date the charity itself began operating as a grant-giving charity — it matches Amendment A-06's existing reference date exactly, not an earlier one, so there is no separate pre-system application history to account for. Seed values: `RoundStatisticsHistoryStartDate = 2026-02-16`, `RoundStatisticsHistoryPriorApplicationCount = 0`. The reviewer separately noted 715 applications as today's live running total since 16 Feb 2026 — that confirms the feature measures something real, it is **not** a seed value and is not written to any setting. See FR-082 for the restated seed values. | | |
| OQ-051 | **What does a trustee see of the four new special-category answers** (FR-086 to FR-089): the value, a redacted counterpart, or nothing? *(Amendment A-08, TAD §C.9 item 3.)* **Default, drawn from the reviewer's own A-05 decision and not invented here:** the board pack trustees receive today prints the Equality Act answer and the full description text, and A-05 ruled *"All fields need to be in. All fields with free text data will be scrubbed with AI."* So the default is: **the two Equality Act answers shown as values**, beside the condition profile; **the two descriptions shown only through a redacted counterpart**, withheld until redaction is released (FR-079, the ADR-027 pattern). **Until this is answered, FR-035 is unchanged and none of the four reaches any trustee surface.** That is TAD rev 10's secured position, and it is the safe one. The answer sets how much Automation #5 work follows: two new redacted counterparts if the default is confirmed, none if not. | Reviewer | Before the `wbs:4.3` schema deploy to DEV creates the four columns, because the Equality Act answers' security setting is set at creation. At the latest, before any `wbs:5.x` or `wbs:6.3` dispatch binds them to a trustee surface |
| | ✅ **RESOLVED 2026-09-25 — Xander Lykopoulos (relayed by lead-agent):** *"I recommend showing the two Yes/No answers as they are, and the two descriptions only in redacted form, like the narrative."* The default is confirmed. Trustees see the two Equality Act answers as values, and the two descriptions only through redacted counterparts (FR-079, the ADR-027 pattern). FR-035 is amended to match. Owed to architect-agent: the Equality Act answers need `secured: exception` rows (C-DOM-031) and the NFR-031 record. Owed to Automation #5: two new redacted counterparts. | | |
| OQ-052 | **Do the consent-date fields keep the system's receipt time, or stay empty?** *(Amendment A-08, passed through from TAD rev 10 `ADR-051` item 12.)* The form sends each consent as ticked or not ticked, with no time. TAD rev 10 writes the moment the submission reached the system into each consent's date field whenever the consent is ticked. That is the same receipt time FR-008 already records as the submission timestamp. **Default, per the TAD:** keep it, read as *"when this consent reached us"*, not *"when the applicant ticked it"*. The rule's *"a date … the user doesnt fill in, ditch it"* is aimed at dates the form generates, and this one is the system's own. **Replace with:** leave the dates empty, because the applicant did not enter them. The receipt time then stays only as FR-008's submission timestamp. | Reviewer | Before development-agent's `wbs:4.3` dispatch encodes the rev 10 intake's consent-date expressions |
| | ✅ **RESOLVED 2026-09-25 — Xander Lykopoulos (relayed by lead-agent):** *"Agreed on consent dates on submission receival."* The consent-date fields hold the time the submission reached the system, meaning *"when this consent reached us"*. That is TAD rev 10's current design. | | |
| OQ-053 | **Does the live form show the middle-name, name-suffix and state/province fields?** *(Amendment A-08, FR-093. Asked of Alex as TAD rev 10 `ADR-011` question 8.)* **Default:** no. They were hidden at the last check, on 2026-08-13, so nothing is stored and no field is built. The title sub-field has been enabled since that check, so the form has changed and the old reading cannot be relied on. | Alex | Before development-agent's `wbs:4.3` dispatch builds the TAD's conditional columns (`TD-011`) |
| | ✅ **RESOLVED 2026-09-25 — Xander Lykopoulos (relayed by lead-agent):** *"Agreed on the middle name, suffix and state/province."* All three are treated as hidden. Nothing is stored and nothing is built until Alex confirms the form shows them. FR-093 stays conditional. | | |
| OQ-054 | **Which names keep a label instead of becoming *They*?** *(Amendment A-09, FR-095.)* The client's examples show one case: the one person a narrative is about becomes *They*. They never show the four cases below. **Default, applied until answered:** (a) two or more different people named in one text each keep `[NAME]`, so two people are not merged into one *they*; (b) a name after a title such as *Dr* keeps `[NAME]` (*Dr [NAME]*); (c) a name next to its relationship word keeps `[FAMILY MEMBER]` (*my partner [FAMILY MEMBER]*), the approved v0.4 behaviour; (d) a name inside a practice name stays `[GP PRACTICE]`. Confirm, or replace any of the four. | Reviewer / Emily | Before development-agent's `wbs:5.6` dispatch encodes FR-095's name rule |
| | ✅ **RESOLVED 2026-10-16 — default adopted.** Xander Lykopoulos (relayed by lead-agent): *"Approved for requirements Amendment A-09"*, having been told approval accepts the defaults unless changed; none was changed. The four default cases keep their labels as stated: two or more people each `[NAME]`; a name after a title such as *Dr* `[NAME]`; a name next to its relationship word is dropped and the relationship word neutralised (*my husband Derek* becomes *my partner*); a name inside a practice name `[GP PRACTICE]`. FR-095 stands as written. ⚠️ **CORRECTED 2026-10-16 by the reviewer, after approval, for case (c) only:** *"My husband Derek becoms partner. not family member. the word husband is leading in this pattern."* Previously read: *"a name next to its relationship word `[FAMILY MEMBER]`"*. **After this correction no case in this SDD produces `[FAMILY MEMBER]`:** FR-026 still lists the label, and the only place it could still apply, a family member in a text naming two or more people (case (a)), is labelled `[NAME]`. | | |
| | ⚠️ **AMENDED, Amendment A-11 (PROPOSED 2026-10-19). Case (c) is widened and a case (e) is added; nothing in (a), (b) or (d) changes.** (c): the name after a relationship word is dropped *even when other people are named*, so case (a) no longer applies to it (*my husband Derek and my sister Ann* becomes *my partner and my sibling*). (e), the applicant's own name (*I am Sam*) keeps `[NAME]` (FR-095). ✅ **Default for (e) CONFIRMED 2026-10-19 by the reviewer** (*"That is correct... the assumed default is the desired output. Approved."*): the writer's own name is not counted as another person, so the one other person named still becomes *They*. Input *"I am Sam and Pat helps me"*, output *"I am [NAME] and they help me"*. Previously read: *"Open default for (e), applied until answered … Confirm, or replace with …"*, due at Emily's first live review. | | |
| OQ-055 | **What do the newly added words become?** *(Amendment A-09, FR-096.)* The reviewer added the words but gave no replacements. **Default, modelled on the key's own categories:** *grandmother* to *grandparent*; *stepson* to *stepchild*; *mummy* to *parent*; *lady* to *person*; *auntie*, *niece* and *nephew* to *relative*; *Mr*, *Mrs*, *Ms* and *Miss* removed, with the name after them handled by FR-095. **Also by default:** the other-gender counterparts (*grandfather*, *grandson*, *granddaughter*, *stepdaughter*, *stepmother*, *stepfather*, *aunt*, *uncle*, *daddy*, *gentleman*) are replaced the same way, because a list with *grandmother* and not *grandfather* leaves the same kind of word in. Confirm or replace. | Reviewer / Emily | Before development-agent's `wbs:5.6` dispatch encodes the FR-096 word list |
| | ✅ **RESOLVED 2026-10-16 — default adopted.** Xander Lykopoulos (relayed by lead-agent): *"Approved for requirements Amendment A-09"*, having been told approval accepts the defaults unless changed; none was changed. *grandmother* to *grandparent*, *stepson* to *stepchild*, *mummy* to *parent*, *lady* to *person*, *auntie*, *niece* and *nephew* to *relative*; titles removed; the other-gender counterparts included. FR-096 stands as written. | | |
| OQ-056 | **What do *hers*, a standalone *his*, and *himself* / *herself* become?** *(Amendment A-09, FR-094.)* The key says *their* for *hers* and *themselves* for the *-self* forms. The examples have no *hers*, and write *themself*. **Default, applying the reviewer's rule that the examples win:** *hers* and a standalone *his* (*the choice is hers*) become *theirs*, because *their* cannot stand alone; *himself* and *herself* become *themself*, as the examples write it. Confirm or replace. | Reviewer / Emily | Before development-agent's `wbs:5.6` dispatch encodes FR-094's pronoun rules |
| | ✅ **RESOLVED 2026-10-16 — default adopted.** Xander Lykopoulos (relayed by lead-agent): *"Approved for requirements Amendment A-09"*, having been told approval accepts the defaults unless changed; none was changed. *hers* and a standalone *his* become *theirs*; *himself* and *herself* become *themself*. | | |
| OQ-057 | **Which date starts the six-year clock: the payment's own date, or the day finance recorded it?** *(Amendment A-12, FR-107.)* The regulation says *"from final payment date"*. **Default, applied until answered:** the date the payment itself carries. A payment dated 14 November 2026 and entered on 18 November starts the clock on 14 November. If the payment carries no date, the day it is recorded is used. *(Fallback withdrawn 2026-10-20: a final payment cannot be saved without a date; see the revision under Amendment A-12.)* Confirm or replace. | Reviewer / Revitalise finance | Before development-agent's `wbs:8.6` dispatch encodes FR-107's date rule |
| | ✅ **RESOLVED 2026-10-20 — default confirmed.** Xander Lykopoulos (relayed by lead-agent), approving Amendment A-12: *"Approved. OQ-057: Payment date."* The clock starts on the date the payment itself carries, not the day finance entered it. FR-107 stands as written. ~~The fallback to the day of recording applies only when the payment carries no date.~~ **Fallback withdrawn by the reviewer's later direction, 2026-10-20 (revision to A-12):** a payment cannot be marked final without a payment date. Previously read: *"the fallback to the day of recording applies only when the payment carries no date."* | | |
| OQ-058 | **Which payments count as final?** *(Amendment A-12, FR-107, FR-110.)* A payment's status is Pending, Issued, Cleared or Cancelled. The reviewer's scope names only the final mark. **Default, applied until answered:** every payment marked final counts except a Cancelled one, which counts as not final (FR-110). A Pending payment marked final therefore starts the clock; a Cancelled one does not, and one cancelled later withdraws it. The alternative, counting only Issued or Cleared payments, would make the clock wait for finance to update a second field. Confirm or replace. | Reviewer / Revitalise finance | Before development-agent's `wbs:8.6` dispatch encodes which payments count |
| | ✅ **RESOLVED 2026-10-20 — default confirmed.** Xander Lykopoulos (relayed by lead-agent), approving Amendment A-12: *"OQ-058: Correct. All payments marked final."* Any payment marked final counts whatever its status (Pending, Issued or Cleared), so a Pending payment marked final starts the clock. A Cancelled payment still counts as not final, under FR-110's existing cancellation rule, which the reviewer's answer does not change. FR-107 and FR-110 stand as written. *Revision 2026-10-20: a Pending payment marked final now also becomes Issued (FR-112).* | | |
| OQ-059 | **When finance removes the final mark from a payment the system set to Issued, does the payment go back to Pending?** *(Amendment A-12 revision, FR-112, FR-110.)* The reviewer's answer sets Issued on marking final and says nothing about unticking. **Default, applied until answered, following the direction of the decision (the flow does one thing for finance, never a second thing behind their back):** the status stays Issued and finance corrects it by hand if the money did not move. Example: a payment of 1,500.00 is Pending and finance ticks final, so it becomes Issued and the grant carries its date. Finance unticks it, the grant's date is cleared and the application returns to "Approved", and the payment still reads Issued. The system cannot know whether the money moved, so it does not guess. Confirm or replace. | Reviewer / Revitalise finance | Before development-agent's `wbs:8.6` dispatch encodes FR-110's reversal |
| | ✅ **RESOLVED 2026-10-20 — default confirmed.** Xander Lykopoulos, answering "should a payment the flow set to Issued go back to Pending when Final is unticked?": *"No. payment final means final."* The payment stays Issued when the final mark is removed; finance corrects it by hand if the money did not move. FR-110 and FR-112 already say this and stand as written; no requirement wording changes. The gate is not re-opened. | | |
| OQ-060 | **What happens when a final payment is recorded before the grant's acceptance is signed?** *(Amendment A-12 second revision, FR-113, FR-111.)* The reviewer's direction moves a grant to "Paid"; the acceptance flows set "Acceptance Issued" and "Acceptance Signed", so a payment can arrive while the grant is still at 1 or 2. **Default, applied until answered, mirroring FR-108 and following the direction of the decision (the flow never skips a step the grant has not reached):** the grant's status is left alone, the case is reported under FR-111, and the final payment date and the application's status are still handled by FR-107 and FR-108. Nothing is moved later by itself when the acceptance is signed. Example: a final payment of 1,500.00 dated 14 November 2026 is saved while the grant reads "Acceptance Issued". The grant keeps that status, finance and the process owner see "grant not at Acceptance Signed", and finance fixes the cause and saves the payment again. Confirm or replace. | Reviewer / Revitalise finance | Before development-agent's `wbs:8.6` dispatch encodes FR-113's condition |
| | ✅ **RESOLVED 2026-10-20 — default confirmed.** Xander Lykopoulos, answering OQ-060: *"OQ-60: Keep default."* A final payment recorded before the grant is at "Acceptance Signed" leaves the grant's status alone and is reported under FR-111. Signing the acceptance later does not move the grant to "Paid" by itself; the next save of any payment on that grant does (TAD A-R103). FR-113 stands as written; no requirement wording changes. The gate is not re-opened. Previously read: *"Confirm or replace."*, due before development-agent's `wbs:8.6` dispatch encodes FR-113's condition. | | |

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

⚠️ **Amendment A-07 (APPROVED 2026-09-19) adds FR-080–FR-082, WBS task `6.10`.** Hours are **not**
restated here — cite `contract/change-orders/CO-005.md` and `contract/wbs.json` (`C-COM-008`).
CO-005's own Sizing basis section states its figure is a **provisional ROM by analogy**, to be
re-opened now that this amendment gives the rescope FR text (its own standing instruction). That
re-opening is `commercial-agent`'s next step against `wbs:6.10`, not restated as a figure here.

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
| FR-014 | US-006 AC-4 · `wbs:2.4` *(amended, Amendment A-10)* |
| FR-015 | US-006 AC-5 · `wbs:2.4` *(amended, Amendment A-10)* |
| FR-016 | US-006 AC-6 *(annotated, Amendment A-10)* |
| FR-017 | US-006 AC-7, AC-20 · `wbs:2.4`, `2.7` *(amended, Amendment A-10)* |
| FR-018 | US-006 AC-8 |
| FR-019 | US-006 AC-9 |
| FR-020 | US-006 AC-10 |
| FR-021 | US-006 AC-11 |
| FR-022 | US-006 AC-12 *(annotated, Amendment A-10)* |
| FR-102 | US-006 AC-13, AC-14 · `wbs:2.7` *(Amendment A-10)* |
| FR-103 | US-006 AC-15, AC-20 · `wbs:2.4` *(Amendment A-10)* |
| FR-104 | US-006 AC-16, AC-20 · `wbs:2.7` *(Amendment A-10; built under EF-34)* |
| FR-105 | US-006 AC-17, AC-18 · `wbs:2.7` *(Amendment A-10; extends EF-45)* |
| ~~FR-106~~ | **WITHDRAWN, Amendment A-10 revision 2** (reviewer ruling). Was ~~US-006 AC-19 · `wbs:2.7`~~ |
| FR-023 | US-010 AC-1 |
| FR-024 | US-010 AC-2, US-015 AC-3 |
| FR-025 | US-010 AC-3 |
| FR-026 | US-007 AC-1, US-025 AC-4 · `wbs:5.6` *(amended, Amendment A-09)* |
| FR-027 | US-007 AC-2, US-014 AC-2 |
| FR-028 | US-007 AC-3 |
| FR-029 | US-007 AC-4 · `wbs:5.3`, `5.4` *(amended, Amendment A-11)* |
| FR-030 | US-007 AC-5 · `wbs:5.4` *(amended, Amendment A-11)* |
| FR-031 | US-007 AC-6, US-012 AC-3, US-015 AC-2 |
| FR-032 | US-014 AC-1, AC-2 |
| FR-033 | US-007 AC-7 |
| FR-034 | US-012 AC-1, US-013 AC-1, AC-2 |
| FR-035 | US-012 AC-2, AC-7 *(AC-7 added by Amendment A-05)* |
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
| FR-078 | US-012 AC-8 *(Amendment A-05)* |
| FR-079 | US-012 AC-9 *(Amendment A-05)* |
| FR-080 | US-016 AC-8 *(Amendment A-07)* |
| FR-081 | US-016 AC-8 *(Amendment A-07)* |
| FR-082 | *(no acceptance criterion — a settings/data requirement, verified by seeding and by FR-080/FR-081's fail-safe unseeded behaviour)* *(Amendment A-07)* |
| FR-083 | US-024 AC-1, AC-2 · `wbs:4.2`, `4.3` *(Amendment A-08)* |
| FR-084 | US-024 AC-3, AC-8 · `wbs:4.3` *(Amendment A-08)* |
| FR-085 | US-024 AC-4 · `wbs:4.2`, `4.3` *(Amendment A-08)* |
| FR-086 | US-024 AC-5, AC-7 · `wbs:4.2`, `4.3` *(Amendment A-08)* |
| FR-087 | US-024 AC-6, AC-7 · `wbs:4.2`, `4.3` *(Amendment A-08)* |
| FR-088 | US-024 AC-5, AC-7 · `wbs:4.2`, `4.3` *(Amendment A-08)* |
| FR-089 | US-024 AC-6, AC-7 · `wbs:4.2`, `4.3` *(Amendment A-08)* |
| FR-090 | US-024 AC-8 · `wbs:4.2`, `4.3` *(Amendment A-08)* |
| FR-091 | US-024 AC-9 · `wbs:4.2`, `4.3` *(Amendment A-08)* |
| FR-092 | US-024 AC-10 · `wbs:4.2`, `4.3` *(Amendment A-08)* |
| FR-093 | US-024 AC-11 · `wbs:4.1`, `4.2`, `4.3`. `4.1` covers confirming the plugin's field behaviour with Alex (OQ-053) *(Amendment A-08)* |
| FR-094 | US-025 AC-1, AC-2 · `wbs:5.6` *(Amendment A-09)* |
| FR-095 | US-025 AC-3, AC-4, AC-11, AC-12 · `wbs:5.6` *(Amendment A-09; OQ-054; amended, Amendment A-11)* |
| FR-096 | US-025 AC-5 · `wbs:5.6` *(Amendment A-09; OQ-055)* |
| FR-097 | US-025 AC-6 · `wbs:5.6` *(Amendment A-09)* |
| FR-098 | US-025 AC-1, AC-3, AC-7 · `wbs:5.6` *(Amendment A-09)* |
| FR-099 | US-025 AC-8 · **no task id yet: depends on `CO-009`** *(Amendment A-09)* |
| FR-100 | US-025 AC-9 · `wbs:5.6` *(Amendment A-09)* |
| FR-101 | US-025 AC-10 · `wbs:5.6`; extends FR-029 and FR-030 *(Amendment A-09)* |
| FR-107 | US-026 AC-1, AC-2, AC-5, AC-8, AC-12 · `wbs:8.6` *(Amendment A-12; `CO-010`, unbilled; OQ-057)* |
| FR-108 | US-026 AC-1, AC-10 · `wbs:8.6` *(Amendment A-12; `CO-010`)* |
| FR-109 | US-026 AC-3, AC-4, AC-19 · `wbs:8.6` *(Amendment A-12; `CO-010`)* |
| FR-110 | US-026 AC-6, AC-7, AC-8, AC-15, AC-18 · `wbs:8.6` *(Amendment A-12; `CO-010`; OQ-058)* |
| FR-111 | US-026 AC-9, AC-10, AC-17 · `wbs:8.6` *(Amendment A-12; `CO-010`)* |
| FR-112 | US-026 AC-13, AC-14, AC-15 · `wbs:8.6` *(Amendment A-12 revision, 2026-10-20; `CO-010`; OQ-059, resolved: "No. payment final means final.")* |
| FR-113 | US-026 AC-16, AC-17, AC-18, AC-19 · `wbs:8.6` *(Amendment A-12 second revision, 2026-10-20; `CO-010`; OQ-060, resolved: "Keep default.")* |

NFR-001 to NFR-003 are additionally exercised by US-012 AC-3 and US-015 AC-1, AC-2.
NFR-022 to NFR-025 have no acceptance criteria by design — they are recorded gaps (OQ-020 to OQ-023).
NFR-027 is withdrawn (Amendment A-03 Resolution, 2026-08-25) and carries no acceptance criteria.
NFR-030 is evidenced by the §7.1a classification table itself, not by a test.
NFR-031 is exercised by US-020 AC-4, which is testable in both directions — the category readable by
a trustee role, the free text behind it not.
NFR-009 and NFR-011, as amended by Amendment A-09, are evidenced by the recorded location of each
component, not by a test.
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

**Amendment A-08 — Reviewed by:** Xander Lykopoulos  **Date:** 2026-09-25  **Response:** `APPROVED`
(*"Approved for development"*). Relayed to plan-agent by lead-agent, quoting the reviewer's turn in its
own session. OQ-051, OQ-052 and OQ-053 were answered in the same turn; see the A-08 Resolution.

**Amendment A-09 — Reviewed by:** Xander Lykopoulos  **Date:** 2026-10-16  **Response:** `APPROVED` (*"Approved for requirements Amendment A-09"*). Relayed to plan-agent by lead-agent from the reviewer's own turn. Previously read: *"PROPOSED 2026-10-16, awaiting review … Response: pending"*. Approval covers FR-026 as amended, FR-094 to FR-101, NFR-009 and NFR-011 as amended, US-025, the two §7.1c rows, and the defaults in OQ-054 to OQ-056 until they are answered. It does not itself approve `CO-009`; the reviewer approved `CO-009` separately in the same turn, unbilled (*"CO-009 Approved with unbilled tag. Features always expand a bit during development and this one is within reasonable limits."*), and commercial-agent records that.

**Amendment A-11 — Reviewed by:** Xander Lykopoulos  **Date:** 2026-10-19  **Response:** `APPROVED` (*"That is correct... the assumed default is the desired output. Approved."*), relayed by lead-agent. Previously read: *"pending"*. The reviewer's earlier decision *"All records should be checked by the process owner regardless. So, we don't need that setting at all."* and his approval of TAD rev 25 are recorded in the amendment; neither was approval of this text; the approval above is. It covers FR-029, FR-030, FR-095, NFR-017 and NFR-018 as amended, US-007 AC-4 and AC-5 as amended, US-025 AC-11 and AC-12, the §1 scope row and §7.1c quote annotations, and the OQ-054 default for case (e).

**Amendment A-10 — Reviewed by:** Xander Lykopoulos  **Date:** 2026-10-19  **Response:** `APPROVED` (*"Approved"*), revision 2. Relayed to plan-agent by lead-agent from the reviewer's own turn. Revision 1 received reviewer feedback the same day, not approval. Previously read: *"Reviewed by: pending … Response: pending (revision 2, 2026-10-19)"*. Approval covers FR-014, FR-015 and FR-017 as amended, the FR-016 and FR-022 annotations, FR-102 to FR-105, the withdrawal of FR-106, US-006 AC-4, AC-5 and AC-7 as amended, AC-13 to AC-18 and AC-20, the withdrawal of AC-19, §7.1d, the setting defaults of A-10 Finding 8, the OQ-003 narrowing and the OQ-005 widening. It is not a sign-off for reading `rev_employmentstatus`: revision 2 reads no employment answer, and revision 1's sentence making approval that sign-off was withdrawn: ~~It would also be the reviewer's sign-off for the scoring flow to read `rev_employmentstatus` as in work or not for FR-015 only (A-10 Finding 3), the authority a `gate_exception` in `constraints/domain/special-category-register.yml` must name.~~ It does not answer OQ-003's remaining value question or OQ-005; both stay open against their events. It records the reviewer's statement that this work is inside `wbs:2.4` and `2.7` and not billable; commercial-agent records the billing.

**Amendment A-12 — Reviewed by:** Xander Lykopoulos  **Date:** 2026-10-20  **Response:** `APPROVED` (*"Approved"*), relayed to plan-agent by lead-agent from the reviewer's own turn. Previously read: *"Reviewed by: pending … Response: pending. Proposed 2026-10-20."* Approval covers FR-107 to FR-111, US-026 and the §1 out-of-scope note. OQ-057 (*"Payment date"*) and OQ-058 (*"Correct. All payments marked final."*) were answered in the same turn, both at their defaults. It does not itself approve any billing: `CO-010` is accepted unbilled (`CE-0021`) and commercial-agent records that.

**Amendment A-12, reviewer-directed revision — Reviewed by:** Xander Lykopoulos  **Date:** 2026-10-20  **Response:** `APPROVED`, relayed by lead-agent. Verbatim: *"1. Agreed. 2. For now use the same as the process owner Emily. At the moment that is a combined role. but in the future probably separated. During testing this can be set to Janine. 3. Make payment date required when final payment is set. The the flow can set the payment status to issued. APPROVED"* Previously read: FR-107 and OQ-057 *"If the payment carries no date, the day it is recorded is used"*. Approval covers FR-107 as revised and FR-112. OQ-059 is raised and open at its default.

**Amendment A-12, wording alignment — 2026-10-20 (not a new decision; gate not re-opened).** FR-107 said a payment *"SHALL NOT be saved as final"* without a date. Only a server-side block could guarantee that, and none is in scope. The reviewer-approved design (TAD rev 28, `ADR-081`, `A-R102`) enforces it with a business rule on the Payment main form, and for API or non-form writes the flow ignores an undated final payment (no clock starts) and reports "final payment has no date" under FR-111. FR-107 and AC-12 are reworded to say exactly that; the reviewer's intent, *"Make payment date required when final payment is set"*, is kept and quoted. FR-112's Cancelled-reporting clause is unchanged. OQ-059 stays open at its default.

**Amendment A-12, second reviewer-directed revision — Reviewed by:** Xander Lykopoulos  **Date:** 2026-10-20  **Response:** `APPROVED`, relayed by lead-agent. Verbatim: *"Obviously the final payment should change the grant status as well."* Approval covers FR-113 and AC-16 to AC-19. Previously read: the grant's own status was outside `CO-010` (architect-agent finding). OQ-059 is resolved (*"No. payment final means final."*); OQ-060 is raised and resolved at its default (*"Keep default."*, 2026-10-20). Previously read: "raised and open at its default." Gate not re-opened.
