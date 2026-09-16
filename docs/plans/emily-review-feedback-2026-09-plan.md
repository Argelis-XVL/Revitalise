# Client Review Feedback — Triage Plan

**Feature slug:** `emily-review-feedback-2026-09`
**Produced by:** plan-agent (intake mode), 2026-09-11
**Revision 3**, 2026-09-16 — the walkthrough behind the two source emails has now been held. It
answers four of this plan's open questions, supersedes three of its designs, creates one conflict,
and adds seven items. See §2.

<!-- id-allocation: none -->

> **Sources:** adopted from `docs/Import/2026-09-07-08-emily-sheardown-review-feedback.md` (Emily
> Sheardown's two review emails) and ground-truthed against
> `docs/Import/2026-09-11-live-application-form-capture.md` (the live application form, fetched
> 2026-09-11).
> **Added in revision 3:** the *Grant Portal Feedback Run-Through* with Emily Sheardown,
> 2026-09-16. Captured in Granola and circulated by email the same day. **It is the discussion
> around the two source emails, not a fourth body of feedback** — which is why it mostly resolves
> this plan's open questions rather than adding to the pile.

> **This document triages. It authorises nothing.** Under `C-COM-002` work enters by WBS task id or
> by an approved change order. After revision 3, **four** items map to no accepted scope and go to
> `commercial-agent` before any delivery work starts.

---

## 1. The rule this document applies

**Rework of anything already built is quoted work, and draws on the relevant automation's
feedback/rework reserve.** A change-order decision is for genuinely **new capability** only.

Revision 1 applied a different and wrong rule — it read task 2.7's *"Adjust flow, views, and
Settings"*, noticed it does not say *forms*, and marked sixteen items `change-order-candidate`. The
reading was right and the conclusion was wrong: the WBS is a costed estimate with headroom, not an
exhaustive enumeration of permitted work. Tested against `contract/wbs.json` and confirmed — every
one of the 61 accepted tasks carries an hours range rather than a point figure, and seven of the
nine automations carry an explicit feedback, rework or iteration row.

**One gap, reported rather than smoothed over: A0 and A8 have no feedback or rework row at all.**
A0 delivered the grant administrator application's container, schema and forms under task 0.4; A8
delivers a payment capture form. Both are user-facing and neither has a reserve. Items that land on
A0 are marked so `commercial-agent` can see them as a set.

### How an item is routed to a reserve

The grant administrator app's form renders columns owned by different automations, so the reserve
follows **the automation that owns the data on that part of the form**, not the form itself:

| What the item touches | Reserve it draws on |
|---|---|
| Scoring, the score breakdown, status, eligibility flags and thresholds | **A2** — 2.6 / 2.7 |
| Fields captured by the intake: their labels, grouping and presence on the form | **A4** — 4.5 |
| The upstream WordPress form's own questions and conditional logic | **A1** — 1.2 / 1.4 / 1.5 |
| The trustee review portal's screens and decision form | **A6** — 6.7 / 6.8 |
| The round-statistics landing screen | **`wbs:6.9`** — change order CO-001 |
| Solution-level schema and client-facing documentation | **A0** — 0.4 / 0.6 / 0.8, *which carries no reserve* |

### And one principle the form capture handed us

**Where Emily asks for a rename, prefer the live form's own wording.** Her feedback repeatedly asks
our surfaces to match the vocabulary the applicant already met. That settled EF-08, EF-22 and EF-37
in revision 2, and the walkthrough extends it: the condition-and-care restructure is now specified
to the field, in the form's own order.

---

## 2. Revision 3 — what the 16 September walkthrough changed

**Task 2.6 is *"Walkthrough with Emily"*, and until 16 September it had produced its deliverable
without its activity.** Revision 2 recorded that Emily's second email *was* the feedback log,
arriving without the walkthrough. The walkthrough has now been held against that same log. **2.6 is
closeable on its own evidence rather than on a substitute**, which unblocks 2.7.

### 2a. Four open questions this plan asked — now answered

| Plan asked | Answer | Effect |
|---|---|---|
| **EF-05** — should **Defer** also require a note, or only Reject? | **Both.** Notes mandatory for defer *and* reject | Scope doubles; still `S`. `VerdictForm.tsx` renders the notes field with the label *Notes (optional)* and already carries Defer as a verdict value |
| **EF-20 / EF-21** — what does *Intake Review Note* actually capture? | **Answerable from the schema — Emily does not need to wait.** `rev_intakereviewnote`'s own description in `rev_applicant`'s sibling entity `rev_application/Entity.xml` states it: recorded by the intake flow when an incoming answer for a Choice column matches no configured option (FR-064) — the field, the raw value sent, and that no match was found. Empty when every mapped answer matched | Closes one of Xander's four walkthrough actions. **It also makes EF-21 a design error** — see §2b |
| **EF-04** — the Trustee Pack is not in this repository | Emily is re-sending it on the trustee-portal email thread | Dependency moves from *"request a copy"* to *"promised"* |
| **EF-12** — does *"wellbeing question 8, 9 and 10"* mean the three *last year* statements? | **Yes, and the schema settles it without needing her to confirm.** `rev_application` carries `rev_wellbeinganswer1` … `rev_wellbeinganswer10`, and the live form asks seven two-week statements followed by three last-year statements. 8, 9 and 10 are the last-year three | Removes an inference this plan refused to build on. Worth one confirming sentence in passing, not a blocking question |

### 2b. Three designs superseded

**1. EF-25 — the target word is *Threshold*, not *Low band*, and the scope is the whole app.**
The source email asked for *Knockout* → *Low band*. The walkthrough asks for *Knockout* →
**Threshold**, *"across the entire app"*. Revision 2's caution survives and matters more than
before: **change the label, never the Setting row's name.** The row is literally named
`KnockoutThreshold` in the seeded settings and the scoring flow looks it up by `rev_name` —
renaming the row breaks scoring silently, and breaks it per-environment, because
`dev-scoring-settings.json`, `test-settings.json` and `prd-settings.json` each hold their own copy.

Two things revision 2 did not have to consider, now that the word is *Threshold*:

- **The scope is wider than two places.** *Knockout* appears in the score-breakdown text, the
  Setting's display label, the grant administration sitemap, the `REV Admin` role definition,
  `ScoringInvariants.Tests.ps1`, two known-bad test fixtures, and `docs/training/casework-handbook.html`.
  The handbook is client-facing and must move with the label.
- **"Threshold" alone is ambiguous in this system, and that is a new risk.** At least three other
  thresholds exist — the income ceiling, the borderline band bounds, and the £500 exceptional-funding
  trigger of EF-31. Recommend **"Threshold score"** or **"Rejection threshold"** in user-visible
  text, confirmed by return, rather than shipping a word less specific than the one it replaces.

**2. EF-21 — the review section is five yes/no checkboxes plus one free-text field, and it is a
different field from the Intake Review Note.** Revision 2 proposed a *Review Note Category* choice
beside the existing free-text note. The walkthrough asks for something else: **up to five checkboxes
for common difficulty areas** (Emily's example: *"Location check complete: Yes/No"*), **plus one
free-text notes field**, as a new per-application review section.

This is not a refinement of EF-21 — it corrects it. Revision 2 assumed the Intake Review Note was
the caseworker's note and proposed categorising it. The schema shows it is written by the intake
flow to record a Choice-mapping failure. **Attaching a human review category to a machine-written
failure log would have put two unrelated meanings in one column.** The new section is new fields;
the Intake Review Note is untouched. Emily is sending the five items.

**3. EF-31 — the exceptional-funding check moves upstream to Alex, and changes owner.**
Revision 2 designed it as an automatic flag in the scoring flow (A2), with two thresholds — £500
for holiday/respite, £100 for day trips/activities — blocked by EF-32's *Other* break type. The
walkthrough reframes it: **if the amount requested exceeds £500 and exceptional funding was not
selected, the web form should block progression.** That is validation at the point of capture, not
a flag after the fact, and it belongs to Alex.

Two things to resolve, because the reframing lost detail rather than settling it:

- **The £100 day-trip threshold was not mentioned.** Whether it is dropped or simply was not
  discussed is unknown. Do not assume it is withdrawn.
- **An upstream block does not replace the downstream flag.** Applications already captured were
  captured without it, and a block on the form cannot reach them. Recommend building both: the form
  block for new submissions, and the A2 flag for the existing corpus.

If the £100 threshold is dropped, **EF-32 becomes moot**: a single >£500 rule has no *Other*
break-type problem to solve.

### 2c. One conflict the walkthrough created, and how to resolve it

**EF-07 and EF-24 make the score breakdown trustee-facing. The walkthrough moves it out of the
Trustee Portal.** Those cannot both be built as written.

- EF-07 / EF-24: rewrite the score breakdown so it reads *"I've been feeling optimistic about the
  future: response 1 = 5 points"*, show the score alone at the top of the portal and the expanded
  breakdown lower down.
- The walkthrough: the scoring-calculation text moves to **a separate audit column, not shown in
  the Trustee Portal**, and its job is to capture *the thresholds enforced at the time of scoring,
  for audit and challenge*.

**These are two different artefacts that one column — `rev_scorebreakdown` — is currently doing
both jobs for.** The resolution is to split it:

| Artefact | Audience | Content |
|---|---|---|
| **Score breakdown** (keep the column, rewrite the content) | Trustee, in the portal | Question text and answer label per question, per EF-07 / EF-24 |
| **Scoring audit trail** (new column, admin-only) | Grant admin, and any future challenge | Threshold values in force at the moment of scoring, the status derived, and the rule that produced it |

**The audit half is not bureaucracy, and the walkthrough supplied its own justification without
naming it.** `KnockoutThreshold`, `BorderlineBandLower`, `BorderlineBandUpper` and `IncomeCeiling`
are all seeded **PROVISIONAL** in the deployment settings, pending SDD **OQ-001, OQ-002 and
OQ-003** — and Emily is about to settle at least the income ceiling (EF-46). **The moment a
threshold changes, every application scored under the old one becomes inexplicable from its own
record.** An audit column written at scoring time is the only thing that keeps a rejected
application defensible after the rule that rejected it has moved. Build it before the thresholds
change, not after.

### 2d. Seven new items

EF-40 to EF-46, in §4.3. Two are substantial: **county** (EF-40) and **group applications in the
Trustee Portal** (EF-43).

---

## 3. Merges, and the traps in the sources

Three merges, each declared:

| Merged into | From | Why |
|---|---|---|
| **EF-02** | Source 1 opening (*"remove from the Trustees"*) + Source 1 comment 8 (*"Region shouldn't be visible for Trustees"*) | The same ask, stated twice within one email |
| **EF-01** | Source 1 opening (*"include this in the overall grant portal accessed by the grant admin"*) + Source 2 unlabelled item 5, first clause | Transcriber's note 2: one requirement, two surfaces |
| **EF-03** | Source 1 opening (*"a 'city' identifier using the postcode"*) + Source 2 unlabelled item 5, second clause | The same ask on two surfaces |

**Trap 1 — the auto-reject / auto-pass near-duplicate is not a duplicate, and one half is already
built.** An **Auto-rejected Applications** sub-area exists under **Casework** in the grant
administration sitemap, backed by the `AutoRejectedApplications` saved query. EF-15 is answerable by
showing Emily where it is. There is no equivalent for auto-pass, so EF-16 is real. **Confirmed again
at the walkthrough**, which also supplied the reason auto-pass needs its own bucket: those
applications still require a qualitative read of the free-text answers before the trustee decision.

**Trap 2 — Region and city are three separate items.** Hiding region from trustees (EF-02) is a
column-security change. Showing region to the grant admin (EF-01) is a form change against data
already readable. Deriving a city from a postcode (EF-03) is capability that does not exist.

**Trap 3 — one of Emily's items is two requests.** The means-tested-benefits re-order is ours
(EF-28); the suppression of income, employment status and savings on a Yes is Alex's and not built
(EF-28b).

**Trap 4 — NEW in revision 3. Removing Region and adding County are one decision, not two, and the
schema says so.** `rev_towncity`'s description on the Applicant entity records why county was never
collected:

> *"The applicant's town or city. Raw export column 22. **County/state (column 23) and country
> (column 25) are NOT collected: every applicant is UK-based and `rev_locationarea` already carries
> the region a trustee sees.**"*

**EF-02 removes exactly the field that justification rests on.** County was excluded because region
already served the purpose; the walkthrough removes region and asks for county in its place. This is
a recorded design decision being reversed by its own premise disappearing — not an oversight, and
not a requirement arriving from nowhere. Route EF-02 and EF-40 to `commercial-agent` and to design
**as one change**, or the trustee list spends a release with no location column at all.

That same description carries a second, cheaper finding: **county is raw export column 23.** It
exists in the source data and was dropped at intake by choice. For historic applications county may
be recoverable by re-reading the export, with no postcode lookup involved — materially smaller than
EF-03 / EF-41 for the backfill half of the problem. Check the export before assuming derivation is
the only route.

---

## 4. The items

**Size key.** `S` — a contained change to one surface. `M` — several surfaces, or one surface plus a
schema change. `L` — new capability with an external dependency. Sizes are relative shirt sizes for
triage only; hours belong to `commercial-agent` against `contract/wbs.json`, and this document
states none (`C-COM-008`).

**Δ** marks a row the 16 September walkthrough changed.

### 4.1 Source 1 — Trustee Review Portal (2026-09-07)

| Id | What Emily asked for | Surface | Resolution | Reserve | Proposed solution | Size | Depends on / conflicts with |
|---|---|---|---|---|---|---|---|
| **EF-01** | Region shown in the grant portal the grant admin uses | Grant admin app | `in-baseline` | **A4** — 4.5 | Region is already captured and readable by the grant admin as *Location Area* on the Applicant record. Surface it on the **Application** record, read-only, where casework happens | S | Bundle with EF-18, EF-38. **Δ Re-check against EF-40** — if county replaces region for trustees, confirm the grant admin still wants region rather than county |
| **EF-02 Δ** | Region must not be visible to trustees | Column security | `in-baseline` | **A6** — 6.8 | **A permissions change, not a UI change.** `rev_locationarea` is unsecured, so trustees can read it from any surface — app, view, export or API. Hiding the column in the portal would leave the data reachable. Add it to the `REV_TrusteeRestricted` profile, then drop the Region column from `ApplicationsTable` | S | **Reduces a contracted deliverable.** WBS 6.2 specifies the list screen as *"applications with score, **region**, dates, status"*. **Δ Now paired with EF-40** — see Trap 4. Also drop the region **filter** in `ApplicationFilters`, which revision 2 did not mention and which leaks the same values through its option list. Also check `rev_agerange`, unsecured on the same footing and not mentioned by Emily |
| **EF-03 Δ** | A city identifier derived from the postcode, because the typed city field is unreliable | Intake flow + schema | **`change-order-candidate`** | — | **No city derivation exists.** The city shown today is `rev_towncity`, the applicant's own typed answer — exactly the unreliable value Emily describes. Region *is* derived from postcode at intake via the `PostcodeRegionMap` setting, so the pattern exists, but that map holds regions, not settlements | **M** *(was L)* | **Δ Materially de-risked.** Emily is supplying her own postcode export with city, county and province, which removes the *"acquire a licensed external reference set"* blocker revision 2 treated as the whole problem. See EF-41 — the licence question does not disappear, it moves |
| **EF-04 Δ** | Mirror the current Trustee Pack's setup and wording | Trustee portal | `in-baseline` | **A6** — 6.8 | Re-label and re-order the detail screen to follow the pack the board already knows. **Δ The walkthrough specified the key structural change: the overall score sits high on the page, with the detailed questions below it for reference** — the same change as EF-07 | M | **Δ Dependency now promised, not merely requested.** Emily is re-sending the pack on the trustee-portal thread |
| **EF-05 Δ** | Notes compulsory for a rejection | Trustee portal | `in-baseline` | **A6** — 6.8 | Notes are optional today on all three verdicts — `VerdictForm` labels the field *Notes (optional)*. **Δ Require notes on Reject *and* Defer**, using the same inline validation the verdict radio already uses; leave Approve optional | S | **Δ Open question closed.** Revision 2 asked whether Defer should also require a note; the walkthrough answers yes |
| **EF-06** | *What is included in the anonymised narrative section?* | Trustee portal | `answer-only` | — | **Nothing today, by design.** The panel binds the redacted narrative column and nothing else. Narrative scrubbing (Automation #5) is deferred under exception `EX-003`, so the panel stays withheld until that automation is built | — | The answer doubles as a warning: `EX-003` clears only when Automation #5 lands *and* DPO sign-off arrives, before any live trustee demo |
| **EF-07 Δ** | Move the full wellbeing answers lower down, show the actual questions and answers, keep only the score out of 60 at the top | Trustee portal + scoring flow | `in-baseline` | **A6** — 6.8 and **A2** — 2.7 | Two halves: the flow writes the breakdown with **question text and the answer's label** instead of *"Wellbeing answer 3: response 2 = 4 points"* (A2); the portal shows the score alone at the top and the expanded breakdown lower down (A6) | M | **Same underlying change as EF-24.** **Δ Now conflicts with the audit-column ask — resolved by the split in §2c and EF-44.** Build EF-44 first; EF-07 and EF-24 then write to the trustee-facing half only |
| **EF-08** | *Holiday Details* → *Application Details* | Trustee portal | `in-baseline` | **A6** — 6.8 | Rename the panel. The live form's section 13 is already called *Application Details* | S | Settled without further input, per the §1 principle |
| **EF-09** | *Preferred Dates* → *Start* and *End Date* | Trustee portal | `in-baseline` | **A6** — 6.8 | Rename and split the single row into two | S | **Blocked, and the walkthrough did not unblock it.** Gap M-06 records that the form supplies one free-text provisional date, so the two date columns cannot be populated. Renaming now yields two permanently empty fields |
| **EF-10 Δ** | Helper, referee and contact details should not be in the Trustee Portal | Trustee portal + column security | `in-baseline` | **A6** — 6.8 | Two halves, one of them not cosmetic. The helper, referee and emergency-contact **names, emails and phone numbers** are already behind `REV_TrusteeRestricted` and render as withheld placeholders — the portal's generated restricted-field catalogue groups all eight under *"Helper, referee and emergency contact"*, which is exactly the panel Emily names. Removing it is presentation. **Helper Organisation and Helper Relationship are not in the profile and are readable by trustees today.** Secure those two, then remove the panel | S | A live disclosure, not a preference. **Δ Confirmed at the walkthrough**, which named emergency contact explicitly alongside helper and referee |
| **EF-11** | Remove *Days the round has been open* — not a representative figure | Landing screen | `in-baseline` | **`wbs:6.9`** — CO-001 | Remove the tile from `RoundStatistics` | S | **Δ Still open — the walkthrough did not settle it.** *Applications per day* is computed from the same day count Emily calls unrepresentative, so removing one and keeping the other is half a fix. Carry the question into the return email |
| **EF-12 Δ** | Add wording for the wellbeing question 8, 9 and 10 statistics, **and** the circumstance score | Landing screen | **split** — `in-baseline` + `change-order-candidate` | **`wbs:6.9`** / CO-001-A3 | **Wording half — in-baseline:** label the three last-year charts with their full question text. **Circumstance-score half — new:** there is no circumstance-score distribution, and CO-001's priced chart list does not include one | S / S | **Δ The "which questions" ambiguity is closed** — `rev_wellbeinganswer1`…`10` against the form's 7 + 3 structure makes 8, 9 and 10 the last-year three. Confirm in passing; do not hold the work for it |

### 4.2 Source 2 — Grant administrator application (2026-09-08)

| Id | What Emily asked for | Surface | Resolution | Reserve | Proposed solution | Size | Depends on / conflicts with |
|---|---|---|---|---|---|---|---|
| **EF-13** | A simple end-to-end process flow of how the process works | Documentation | `in-baseline` | **A0** — 0.6 / 0.8 *(no reserve)* | **A process flow already exists** — `docs/Import/Revitalise-Process-Flow-v0.1.html`, a July 2026 draft. Sendable today but stale: it says the application *"lands in SharePoint"*, which is not what was built. Refresh to as-built and re-issue | S | One of the items landing on A0, which has no feedback row |
| **EF-14** | Some sections show a locked symbol — will the grant admin receive all access? | Access model | `answer-only` | — | **Yes, with one deliberate exception.** The padlock marks a column-secured field; the grant admin role is a member of the profile that releases them. The exception is **bank and payment data**, behind a second profile the grant admin is deliberately excluded from | — | Worth stating as a control she benefits from, not a limitation |
| **EF-15** | Auto-reject cases added as a category under *Casework* | Grant admin app | `answer-only` | — | **Already built** — *Auto-rejected Applications* sits under Casework with its own saved view | — | Confirm this is what she meant |
| **EF-16 Δ** | Auto-pass cases added as a category under *Casework*, to check the free-text answers are sufficient | Grant admin app | `in-baseline` | **A2** — 2.7 | Add an *Auto-pass Applications* saved view and a Casework sub-area beside the existing three (Applications, Borderline — Awaiting Review, Under Review — Incomplete Scoring, Auto-rejected Applications) | S | **Δ Confirmed at the walkthrough, with the reason stated**: auto-pass still requires a qualitative text review before the trustee decision, so the bucket is a work queue, not just a filter |
| **EF-17** | A section at the end containing the full application | Grant admin app | `in-baseline` | **A4** — 4.5 | A read-only *Full Application* tab rendering every captured answer in the order the applicant met them | M | Overlaps EF-37 — both need the form's question text |
| **EF-18** | Include personal details in the application — name, address, email | Grant admin app | `in-baseline` | **A4** — 4.5 | Surface the applicant's identity fields on the Application record, read-only, via the existing link | S | Bundle with EF-01, EF-38. **Note the design intent traded off:** the Application record deliberately shows a pseudonymised reference. Putting names on it is safe *only* because column security, not form design, is the control. **Δ** For views specifically, Emily can already self-serve a full-name column — see §5a |
| **EF-19** | *Quality Monitoring — where are these recorded?* | Grant admin app | `answer-only` | — | **The form's final section is called Equality Monitoring** — gender and ethnic group. Both are on the Applicant record, both column-secured, both readable by the grant admin, and neither reaches scoring or eligibility | — | Confirm the reading with her |
| **EF-20 Δ** | *Intake Review Note — assuming I will have access to all of these?* | Grant admin app | `answer-only` | — | Yes — and **Δ the walkthrough showed the real question is what it contains, not who can read it.** It is written by the intake flow when a Choice answer arriving from the form matches no configured option: the field, the raw value, and that no match was found. Empty when every answer mapped | — | **Δ Closes a Xander action item outright.** It is a data-quality log, not a caseworker's note |
| **EF-21 Δ** | ~~Selectable categories in the Intake Review Note as well as free text~~ **Five yes/no review checkboxes plus one free-text note** | Grant admin app | `in-baseline` | **A4** — 4.5 | **Δ Superseded — see §2b.** Add a new per-application review section: up to five yes/no checkboxes for common difficulty areas (Emily's example, *"Location check complete: Yes/No"*) and one free-text notes field. **Do not attach these to `rev_intakereviewnote`**, which is machine-written | S | **Δ Needs the five items from Emily**, promised at the walkthrough. Routed to A4; A2's 2.7 is the defensible alternative if `commercial-agent` reads it as post-scoring triage |
| **EF-22** | Split the scoring into three sections: Life satisfaction / In the last 2 weeks… / In the last year… | Grant admin app | `in-baseline` | **A2** — 2.7 | **This is the form's own structure** — one 0–10 scale, seven two-week statements on a 5-point scale, three last-year statements on a 6-point scale | S | **Underlines a real data issue:** the three last-year questions use a different answer scale from the seven two-week questions (gap M-02) |
| **EF-23 Δ** | *What does "No Rounding was Applied" mean?* | Scoring flow | `answer-only` + `in-baseline` | **A2** — 2.7 *(for the removal)* | It means the score was already a whole number. **It is now the only message that can appear:** the branch for half-points existed for a *Not sure* answer, and *Not sure* is worth zero, so no fractional total is possible. Remove the sentence | S | **Δ Confirmed at the walkthrough**, which added the reason: the note described a manual override, not a system rounding rule. Fold the removal into EF-44's split |
| **EF-24** | Break the score breakdown down by question — *"I've been feeling optimistic about the future: response 1 = 5 points"* | Scoring flow | `in-baseline` | **A2** — 2.7 | Emily wrote the target format herself. Write the question text and the answer's label instead of a question number and a response number | S | **Same change as EF-07.** **Δ Sequenced after EF-44** |
| **EF-25 Δ** | ~~*Knockout* → *Low band*~~ **→ *Threshold*, across the entire app** | Scoring flow + Settings + docs | `in-baseline` | **A2** — 2.7 | **Δ Superseded — see §2b.** Change the word wherever a person sees it: score-breakdown text, Setting display label, sitemap, role definition, test fixtures, and `docs/training/casework-handbook.html` | S → **M** | **Change the label, never the Setting row's name.** The row is `KnockoutThreshold` and the flow looks it up by `rev_name` in all three environments. **Δ Recommend "Threshold score" over bare "Threshold"** — at least three other thresholds exist |
| **EF-26** | *What does the "Override" section show?* | Grant admin app | `answer-only` | — | It records a manual override of the automated outcome by the process owner: whether it was overridden, by whom, when, the reason, and the decision date — `rev_statusoverridden`, `rev_overriddenby`, `rev_overriddenon`, `rev_overridereason`, `rev_decisiondate` | — | **Δ Already answered by this plan before the walkthrough re-asked it.** Pair with EF-34, which increases how often an override will be needed |
| **EF-27 Δ** | An *action completed* record for safeguarding incidents | Grant admin app | `in-baseline` | **A0** — 0.4 *(no reserve)* | **Δ Now specified:** an *Action Completed* checkbox beside the existing `rev_safeguardingflag` and `rev_safeguardingnotes`, with the completion date **set automatically on tick so it cannot be backdated** | S | **Δ The auto-timestamp is a real design constraint, not a label.** A user-editable date column does not satisfy it — the value must be written by the platform (real-time workflow or business rule) and the column left read-only on the form. **Recommend also capturing *who* ticked it**: Emily's stated reason is record-keeping, and a safeguarding action with a date but no owner is weak evidence. Secure the new fields on the same basis as the existing ones |
| **EF-28 Δ** | Means-tested benefits moved to the front | Grant admin app | `in-baseline` | **A4** — 4.5 | **Δ Now specified to the exact order:** *Received means-tested benefits* → *Benefits provider* → *Income band* → *Income flag* (`rev_receivesbenefits`, `rev_benefitprovider`, `rev_incomeband`, `rev_incomeflag` — all four exist). Our app currently puts Income Band first | S | **Raises gap M-04:** if the four dependent questions are ever suppressed, an absent income band must be read as *qualifies on benefit status*, not as missing data |
| **EF-28b** | *"If they select yes they are not asked about income, employment status or savings"* | **Upstream WordPress form** | `external-dependency` | **A1** — 1.2 / 1.4 *(spec side)* | **This is not how the live form behaves.** The only field conditional on a Yes is the benefit provider. Emily is describing intended behaviour. Alex adds the conditional suppression; we specify it | S (ours) | Changes what an empty income band means — see EF-28 |
| **EF-29 Δ** | Income bands set as per the form | Schema + spec | `in-baseline` | **A1** — 1.4 *(decision)* · **A2** — 2.7 *(implementation)* | **Δ Reopened.** Revision 2 closed this from the form capture — four bands: Under £15,000 · £15,000–£25,000 · £25,000–£35,000 · Over £35,000. **The walkthrough has Emily sending the band list again**, and the `IncomeBandUpperBoundMap` setting still holds six options on £10,000 boundaries | S/M | **Δ Two sources now disagree and neither is confirmed authoritative.** Do not implement until Emily's list arrives and is reconciled against the 2026-09-11 capture. `NFR-019` is why this is cheap once settled: the map changes, the scoring flow does not |
| **EF-30** | Employment status as a dropdown *as per form* | Schema | `answer-only` | — | **Settled, and nothing needs to change.** The live form's five options are exactly what `rev_employmentstatus` holds, and `EmploymentStatusLabelMap` maps them | — | Verified against the form capture; the schema was right |
| **EF-31 Δ** | Automatic flag when the amount requested exceeds £500 (holidays/respite) or £100 (day trips/activities) **and** no exceptional funding request was made | **Δ Upstream form** + scoring flow | **Δ split** — `external-dependency` + `in-baseline` | **A1** *(form block)* · **A2** — 2.7 *(existing corpus)* | **Δ Reframed — see §2b.** The walkthrough asks for a **block on the web form** when the amount exceeds £500 and exceptional funding was not selected. Recommend building both: the form block for new submissions (Alex), and the A2 flag for applications already captured, which no form block can reach | M | **Δ Two details lost in the reframing, both to confirm:** whether the £100 day-trip threshold still applies, and whether EF-32 is still live. **If £100 is dropped, EF-32 is moot** |
| **EF-32 Δ** | *Unsure how "other" should be treated* | Business rule | `answer-only` | — | She has effectively answered it: the admin re-classifies. Proposal to confirm — *Other* takes **no automatic threshold** and is flagged for manual review | — | **Δ May be moot.** It exists only because two thresholds needed a break-type test. A single >£500 rule does not |
| **EF-33** | Costs and Funding moved into the *Break Details* section | Grant admin app | `in-baseline` | **A4** — 4.5 | Move the Costs and Funding section from the Eligibility & Finance tab to Break Details | S | Presentation only — no automation reads a field's tab |
| **EF-34 Δ** | A *No* to *previous funding more than 12 months ago* should be auto-rejected | Scoring flow | `in-baseline` | **A2** — 2.7 | **Δ Now stated as an explicit compound condition:** received funding before **is Yes** *and* more than 12 months ago **is No** → auto-reject. Both columns exist (`rev_receivedfundingbefore`, `rev_morethan12monthsago`) and **no automation reads either today** | S/M | **Conflicts with an open compliance decision.** Whether automatic rejection may stand without human review is open for the DPO under the Data (Use and Access) Act 2025 (rule BR-S10). **Δ The compound form makes this sharper, not safer** — it is a second fully automatic rejection path. Recommend routing the outcome to the process owner rather than closing the application until the DPO decides |
| **EF-35** | A new form question: carers confirm the person they support is over 18 | **Upstream WordPress form** | `external-dependency` | **A1** — 1.2 / 1.4 · **A4** — 4.2 | **Confirmed genuinely absent.** The live form has *"I confirm I am 18 years of age or over"* for the applicant and no equivalent for the person supported | S (ours) | Blocks the second half of EF-36 |
| **EF-36** | Show both age confirmations and the age range in the eligibility section | Grant admin app | `in-baseline` | **A4** — 4.5 | Surface the existing applicant confirmation and the derived age range in the eligibility section rather than under Consent | S | **Partly blocked by EF-35** |
| **EF-37 Δ** | Show the questions as worded on the form — she cannot tell which is which | **Δ Grant admin app + trustee portal** | `in-baseline` | **A4** — 4.5 **Δ and A6** — 6.8 | **Δ Now specified to the field and the order.** The walkthrough restructures the condition-and-care section: labels mirror the web form's wording; *"Support recipient condition profile"* means **a carer completing conditions on behalf of the person they support**; the care-support description merges into the same section; and the field order is **conditions/illnesses → brief disability description → care support details, including hours** | S → **M** | **Δ Now two surfaces, not one.** The walkthrough raised this against the Trustee Portal; the source email raised it against the admin app. Same wording, both places. Overlaps EF-17 |
| **EF-38** | Show whether the applicant is a disabled person, a carer, and so on | Grant admin app | `in-baseline` | **A4** — 4.5 | **No new question needed.** The form's *"Are you"* answer is stored as *Applicant Type* on the Applicant record. Surface it in Support Needs | S | Bundle with EF-01, EF-18 |
| **EF-39** | Remove the date and time stamps on consents | Grant admin app | `in-baseline` | **A4** — 4.5 | **Hide them from the form's layout; keep the columns.** They add nothing to a caseworker reading the record, and they are the charity's evidence of *when* each consent was given | S | **The one item where the recommendation is not to do exactly what was asked** — and the reviewer has agreed with that reading |

### 4.3 New in revision 3 — from the 16 September walkthrough

| Id | What Emily asked for | Surface | Resolution | Reserve | Proposed solution | Size | Depends on / conflicts with |
|---|---|---|---|---|---|---|---|
| **EF-40** | A **County** column, replacing Region in the trustee list | Schema + both portals | **`change-order-candidate`** | — | **The column does not exist** — the Applicant entity holds `rev_towncity`, `rev_postcode` and `rev_locationarea`, and no county. Add a county column, populate it at intake, and use it as the trustee list's location column in place of region | **M** | **See Trap 4 — this and EF-02 are one decision.** County was excluded by a recorded decision whose stated reason was that region already served the purpose. **Check the raw export first:** county is column 23 and may be recoverable for historic applications without any lookup |
| **EF-41** | Postcode → city/county lookup, from Emily's own export | Intake flow + reference data | **`change-order-candidate`** | — | **The route Emily prefers is Option 1** — load her export as a reference table and look up on the outward code, the same shape as the existing `PostcodeRegionMap`, which already proves the intake-side pattern. Option 2 (a live public postcode API) adds a runtime dependency and a per-call failure mode the intake flow does not have today | **M** | **Δ This replaces EF-03's licence blocker; it does not remove it.** Three things to establish before design: **(1) what Emily's list is derived from** — if it originates in Royal Mail PAF or the ONS Postcode Directory, the licence terms travel with the data, and arriving as a spreadsheet does not change them; **(2) what *province* means** in a UK export — there is no UK province, so it is either the four countries or something closer to the twelve regions already held; **(3) staleness** — a static list needs an owner and a refresh interval, which a live API would not |
| **EF-42** | A **Groups** bucket in the admin app, grouped by the linkage code | Grant admin app | `in-baseline` | **A4** — 4.5 | Add a *Group Applications* saved view and Casework sub-area, grouped on `rev_grouplinkage` — the admin-assigned code (e.g. GP5) the process owner sets by hand | S | **The column and its semantics already exist and are already relied on**: its own description records that *"the combined-amount check groups on this column"*. Keep it distinct from `rev_isgrouptrip`, which is the applicant's own claim and is not authoritative |
| **EF-43** | A **group applications table** in the Trustee Portal, above the individual list, with a group detail page | Trustee portal | **`change-order-candidate`** | — | A second table above the applications list, one row per group, opening a group detail page: grouped summary first (total amount, dates, individual requests), then the individual applications below. Emily is sending a group summary example to inform the layout | **L** | **The largest genuinely new item in this plan.** WBS 6.2 specifies a single list screen of *"applications with score, region, dates, status"* — a second entity-level table with its own detail route is a new screen, not a re-layout of an existing one. The walkthrough left the interaction open (expandable rows vs. a separate page), so **the design question is not settled and should not be priced as if it were** |
| **EF-44** | Move the scoring-calculation text to an **audit-only column**, out of the Trustee Portal | Scoring flow + schema | `in-baseline` | **A2** — 2.7 | **Split `rev_scorebreakdown` into two — see §2c.** A trustee-facing breakdown (question text and answer label, per EF-07 / EF-24) and a new admin-only audit column recording the threshold values in force at the moment of scoring, the status derived, and the rule that produced it | **M** | **Sequence before EF-07 and EF-24**, which otherwise write to a column about to change meaning. **Urgent for a reason the walkthrough did not state:** four thresholds are seeded PROVISIONAL pending OQ-001/002/003 and Emily is about to settle them (EF-46). Applications scored before that change are only defensible if the audit column exists first |
| **EF-45** | An **auto-reject reason** shown per application | Scoring flow + schema | `in-baseline` | **A2** — 2.7 | **Feasible, and cheaper than it sounds.** The flagging step already evaluates each rejection condition in order; write the deciding condition to a column as it does. Emily's question was whether it can be automatic — it can, because the flow knows the answer at the moment it sets the status | S | **Evaluate with EF-44 and EF-34**, not separately: all three write to the scoring flow's output, and EF-34 adds a second rejection path that makes a reason field more valuable. **Order matters** — if both the threshold and the 12-month rule reject an application, the reason must be deterministic, so fix the evaluation order explicitly rather than inheriting it |
| **EF-46** | Review and settle the scoring settings — borderline band, income ceiling | Settings | `answer-only` → **decision** | **A2** — 2.7 *(re-seed only)* | **Not a build item — a decision item, and it closes three open SDD questions.** `KnockoutThreshold` (20), `BorderlineBandLower` (21), `BorderlineBandUpper` (30) and `IncomeCeiling` (£25,000) are all seeded **PROVISIONAL** pending **OQ-001, OQ-002 and OQ-003**. Emily is reviewing the page and named the income ceiling as wrong | S | **Sequence this first, because it is free and it gates others.** Changing a settled value later invalidates scored applications (EF-44). **Re-seed all three environments together** — `dev-scoring-settings.json`, `test-settings.json` and `prd-settings.json` each hold their own copy, and the dev file's own README warns they are not read from one another at run time |

---

## 5. The three lists that need separate action

### 5a. Answerable by return email, at no build cost

**Thirteen items.** Three added in revision 3: **EF-20** (now a real answer, not just an access
confirmation), **EF-26** (which the walkthrough re-asked and this plan already answered), and the
full-name column.

| Id | The answer to send |
|---|---|
| **EF-06** | The anonymised narrative panel is empty today and stays empty until narrative scrubbing is built. That automation is deferred under a recorded, owned exception. **Say this before the trustee demo** — it is the item most likely to surprise the board |
| **EF-13** | A process flow exists as a July draft and can be sent today, with the caveat that it predates the build and describes the intake landing in SharePoint rather than Dataverse. Offer it as an interim and propose a refresh |
| **EF-14** | The padlock means the field is individually protected rather than open to everyone with app access. The grant admin can read all of them. The single deliberate exception is bank and payment data, visible only to the finance role |
| **EF-15** | Already built — *Auto-rejected Applications* sits under **Casework** alongside *Borderline* and *Under Review*. Send a screenshot rather than a sentence |
| **EF-19** | The form's final section is **Equality** Monitoring — gender and ethnic group. Both are protected, both visible to the grant admin, and neither is ever used in scoring or eligibility. Ask her to confirm that is what she meant |
| **EF-20** | **The Intake Review Note is written by the system, not by a person.** It records that an answer arriving from the web form did not match any of the options we hold for that question — the field, what was actually sent, and that no match was found. It is empty when everything mapped. **It is a data-quality alert, and the right response to a populated one is to check the form's option list against ours.** Her new review checkboxes (EF-21) are a separate, human-written section |
| **EF-23** | It means the score was already a whole number. It is now the only message that can appear, because the answer that used to produce a half point is worth zero. We will remove the sentence |
| **EF-26** | It records a manual override of the automated outcome: whether it was overridden, by whom, when, why, and the decision date. **This answers the walkthrough action item directly** — no investigation needed |
| **EF-30** | Employment status already matches the form exactly — the same five options, in the same order. Nothing to change |
| **EF-32** | Proposal to confirm: break type *Other* gets no automatic threshold and is flagged for manual review instead. **This may now be moot** — see the £100 question below |
| **EF-45** | Yes, an automatic auto-reject reason is feasible. The flow already knows which condition rejected the application at the moment it sets the status; it just does not write it down |
| **EF-18** | She can add a full name column to any view herself, without us — *Add Columns > Related > Applicant*. Worth sending as a short how-to, since it unblocks her immediately |
| **EF-40** | County does not exist as a field today, and the reason is on record: it was left out because region already gave trustees a location. Removing region is what makes county necessary — so the two are being handled as one change |

**Four questions to put to her in the same email**, because building on a guess would be worse than
asking:

- **EF-31 — does the £100 day-trip threshold still apply?** The walkthrough named only £500. If
  £100 is dropped, EF-32 disappears with it.
- **EF-11 — should *Applications per day* go as well?** It is computed from the same day count she
  calls unrepresentative. Asked in revision 2, still unanswered.
- **EF-41 — where did the postcode list come from?** If it derives from Royal Mail PAF or the ONS
  Postcode Directory, the licence terms travel with the data. And **what does *province* mean** —
  there is no UK province, so it is either the four countries or something closer to the regions we
  already hold.
- **EF-25 — is *"Threshold"* on its own clear enough?** At least three other thresholds exist in
  this system. *Threshold score* or *Rejection threshold* would say which one is meant.

### 5b. Change-order candidates — to `commercial-agent` before any delivery work (`C-COM-002`)

**Revision 3 takes this from one and a half items to four.** EF-03 shrinks; EF-40, EF-41 and EF-43
are new.

| Item | Why it is genuinely new | Size |
|---|---|---|
| **EF-40 — a County column** | The column does not exist, and its absence is a recorded design decision rather than an omission. **Take it to `commercial-agent` together with EF-02**, which is what makes it necessary | **M** |
| **EF-41 — postcode → city/county lookup** | Still new capability — a reference table, an intake-side lookup, and an owner for keeping it current. **But materially smaller than revision 2 assumed:** Emily supplying the data removes the *"acquire a licensed reference set"* half of the problem, leaving the provenance question | **M** *(was L)* |
| **EF-43 — group applications in the Trustee Portal** | A second entity-level table with its own detail route. WBS 6.2 specifies one list screen of applications. The interaction model is explicitly unsettled, so **price the design, not just the build** | **L** |
| **EF-12, second half — a circumstance-score distribution on the landing screen** | No circumstance-score distribution exists and CO-001's priced chart list does not name one. An amendment to CO-001, for which **CO-001-A1 and CO-001-A2 are the established precedent** | S |

**EF-42** (the Groups bucket in the admin app) is deliberately **not** on this list: a saved view and
a sitemap sub-area over a column that already exists is the same shape of work as EF-16, which is
in-baseline. Only the Trustee Portal half is new.

### 5c. External dependencies, with their owner

| Dependency | Owner | Blocks | State |
|---|---|---|---|
| **The postcode export** — city, county, province | Emily Sheardown | EF-03, EF-40, EF-41 | **Δ Promised 2026-09-16.** Provenance and licence unknown — ask on arrival, not after design |
| **The five review-checkbox items** | Emily Sheardown | EF-21 | **Δ Promised 2026-09-16** |
| **The income band options from the live form** | Emily Sheardown | EF-29 | **Δ Promised 2026-09-16, and this reopens a dependency revision 2 closed.** Reconcile against the 2026-09-11 form capture, which found four bands; our column holds six |
| **The current Trustee Pack** — layout and wording | Emily Sheardown | EF-04, EF-07 | **Δ Promised 2026-09-16** on the trustee-portal email thread |
| **A group application summary example** | Emily Sheardown | EF-43 | **Δ Promised 2026-09-16.** The layout cannot be designed without it |
| **A >£500 exceptional-funding block on the form** | Alex (website) | EF-31 | **Δ New.** Raised at the walkthrough as Xander's action to put to Alex |
| **Conditional suppression of income, employment and savings on a benefits Yes** | Alex (website) | EF-28b | **Not built.** The live form asks all three regardless |
| **A carer age-confirmation question on the form** | Alex (website) | EF-35, second half of EF-36 | **Confirmed absent** from the live form |
| **The scoring treatment of the income-band boundaries** | Emily + trustee board | EF-29 | How the income flag treats a boundary value stays a Revitalise decision |
| **OQ-001 / OQ-002 / OQ-003 — the threshold values** | Emily + trustee board | EF-46, and the value of EF-44 | **Δ In progress.** Emily is reviewing the scoring settings page. All four values are seeded PROVISIONAL today |
| **Structured break dates on the form** | Emily via Alex | EF-09 | Recorded as gap M-06 and **not settled by the walkthrough** |
| **DPO decision on automatic rejection** under the Data (Use and Access) Act 2025 | DPO via Emily | EF-34 | Open (rule BR-S10). **Δ More pressing** — EF-34 is now specified as a fully automatic compound rejection |

---

## 6. Notes for `commercial-agent` and `pm-agent`

**1. Task 2.6's activity has now been performed.** Revision 2 recorded that Emily's second email
*was* 2.6's feedback log, arriving without the walkthrough the task names. The walkthrough was held
on 16 September against that log. **2.6 closes on its own evidence, not on a substitute**, which
unblocks 2.7.

**2. The reserve model holds, with the same hole.** A0 and A8 carry no feedback or rework row.
Revision 3 adds a second A0 item — EF-27's safeguarding fields are now specified and still land
there. Nothing in Emily's feedback touches A8.

**3. Four change-order candidates, and two of them are one decision.** EF-02 (remove region) and
EF-40 (add county) must be priced and sequenced together: county was excluded on the express grounds
that region served the purpose, and removing region is what creates the need. Splitting them across
releases leaves the trustee list with no location column at all.

**4. EF-43 is the one item where the design is not settled enough to price.** The walkthrough left
the interaction open — expandable rows or a separate group page. Recommend a short design step
against Emily's promised example before a figure is put to it.

**5. Personal data — EF-41 changes the shape of this note, it does not remove it.** EF-21 (review
checkboxes), EF-27 (safeguarding action) and EF-36 (carer age confirmation) are new fields about
processing the charity already performs. **EF-03 / EF-40 / EF-41 remain different:** deriving a
settlement and a county from a postcode creates a new, more precise location attribute, for a
purpose Emily states plainly — *"allow us to be even more specific with our funders."* That is
funder reporting, not grant assessment. Emily supplying the data herself changes the licensing
question, **not the lawful-basis question**. The basis, the retention position and the
anonymised-statistics treatment are still to be settled in the design that follows the change order,
and must not be inherited from region's.

**6. `wbs:6.9` is not in `contract/wbs.json`.** The baseline holds 61 tasks and 6.9 is not among
them; it was created by change order CO-001. One statement in `contract/known-exceptions.json` —
that *"wbs:6.9 sits alongside 6.1-6.8 in contract/wbs.json"* — is not true of the file it names.
Reported, not fixed.

**7. Two defects neither Emily nor the walkthrough raised.** The live form's *hours of care per
week* list reads *9 hours or less · 10 – 19 · 20 – 34 · 35 – 59 · 50+* — the last two bands overlap
and *50+* sits below *35 – 59*. **Our `CareHoursBandLabelMap` reproduces it exactly**, defect
included, so an applicant caring 55 hours a week can land in either band. Raise it; do not silently
normalise it. Second: EF-02 removes the region **column**, and the region **filter** in
`ApplicationFilters` exposes the same values through its option list — revision 2 missed it.

**8. One commercial matter was raised at the walkthrough and is deliberately not recorded here.**
A third-party vendor overrun charge is disputed and a resolution meeting has been requested. **The
figure is not written into this repository** (`C-COM-004`, D-3) — it belongs in
`logs/commercial-events.jsonl` or a change-order record owned by `commercial-agent`, not in a
delivery plan. The monetary values that *do* appear in this document — £500, the income bands, the
income ceiling — are product configuration, not commercial terms, and have the same standing as the
seeded values in `provisioning/deploymentSettings/`.

**9. DocuSign message personalisation is a recorded deferral, not a gap.** The walkthrough confirmed
the template's subject line supports dynamic codes and the body does not, with personalised
messaging (*Dear [Name]*) planned for a later automation phase. `EX-006` / `EX-007` already scope
the DocuSign flows to DEV only pending Revitalise's own licence.

---

## 7. Recommended sequence

1. **Send the thirteen answers in §5a and the four questions beneath them this week.** Thirteen of
   forty-six items close at no build cost, and three of them (EF-06, EF-20, EF-26) are things Emily
   is currently waiting on. EF-20 and EF-26 close two of the four actions Xander took away from the
   walkthrough; EF-45 closes a third as an answer rather than an investigation.

2. **Settle EF-46 first, because it is free and everything downstream inherits it.** The borderline
   band, the knockout threshold and the income ceiling are seeded PROVISIONAL against
   OQ-001/002/003. Emily is already reviewing the page. Re-seed all three environment files together.

3. **Build EF-44 before EF-07, EF-23 and EF-24.** Splitting the score breakdown from the scoring
   audit trail has to happen before anything else rewrites that column — and before the thresholds
   settled in step 2 make previously scored applications unexplainable.

4. **Secure `rev_locationarea`, `rev_helperorganisation` and `rev_helperrelationship`** (EF-02,
   EF-10), and drop the region filter with the region column. These are the only items where the
   current state is a live disclosure rather than a preference, and they should not wait — **but
   sequence EF-02's column removal with EF-40**, or the trustee list loses location entirely.

5. **Close 2.6 against the walkthrough**, which unblocks 2.7, then run the A2 items as one pass:
   EF-16, EF-22, EF-23, EF-24, EF-25, EF-34, EF-45 — with EF-29 held for Emily's band list and
   EF-31 held for the £100 answer.

6. **Run the A4 form pass as one piece of work**, not twelve: EF-01, EF-17, EF-18, EF-21, EF-27,
   EF-28, EF-33, EF-36, EF-37, EF-38, EF-39 and EF-42 all touch the same form, and several touch the
   same section.

7. **Take the four change-order candidates to `commercial-agent`** — EF-40 and EF-02 as one
   decision, EF-41, EF-43, and EF-12's second half. EF-43 needs a design step first.

8. **Ask Alex for the three upstream changes** (EF-28b, EF-31's form block, EF-35) so they can be
   specified into A1's spec review while the A2 and A4 passes run.
