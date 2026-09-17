# Client Review Feedback — Triage Plan

**Feature slug:** `emily-review-feedback-2026-09`
**Produced by:** plan-agent (intake mode), 2026-09-11
**Revision 4**, 2026-09-17 — every artefact promised at the walkthrough has arrived, and one new
item comes from the reviewer rather than from Emily. They close **all five** outstanding external
dependencies, settle eight items outright, **contradict one of this plan's own findings**, and
expose a live defect in region derivation that nobody asked about. See §2e and §2f.

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
> **Added in revision 4:** the delivered artefacts and the message that carried them, all under
> `docs/Import/` — `2026-09-16-emily-sheardown-artefact-delivery.md` (Emily's covering mail,
> **which carries the income band list and the eight review checkboxes in its body**),
> `3. Round 4 - Individual Applications.pdf` (63 applications; the trustee pack as it is issued
> today), `2. Group Applications - Round 5.pdf` (12 applications across 5 groups; the group
> variant), and `Postcode Details.xlsx` (3,394 postcode districts, plus the income bands again on
> a second sheet). **The three files are not opinion — they are the current process and its live
> data**, which is why they settle arguments the emails and the walkthrough could only open.

> **This document triages. It authorises nothing.** Under `C-COM-002` work enters by WBS task id or
> by an approved change order. After revision 4 the change-order list still holds **four** items,
> but EF-43 is now designable and EF-41 has lost its licence blocker — see §5b.

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

## 2. What arrived after the two emails, and what it changed

*Subsections 2a–2d are revision 3 (the 16 September walkthrough). Subsections 2e–2k are revision 4
(the delivered artefacts and the message that carried them). Cross-references to §2b and §2c
elsewhere in this document point at the revision-3 subsections and are unchanged.*

### Revision 3 — the 16 September walkthrough

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
  trigger of EF-31. Revision 4 offered **"Threshold score"** or **"Rejection threshold"** rather
  than shipping a word less specific than the one it replaces.

  **Settled 2026-09-17: the word is "Threshold score."** Agreed by the reviewer on the plan itself.
  **That fixes our position, not Emily's** — she asked at the walkthrough for *Threshold*, so this
  departs from what she literally requested and still needs her assent. The §5a question changes
  shape rather than disappearing: we now propose one word instead of offering two.
  **"Rejection threshold" is rejected on a second ground worth recording** — under EF-34 a second,
  compound auto-rejection path is being added, so a label naming *rejection* would imply it covers
  both when it names only the score test.

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

  **Settled 2026-09-17: build both.** Agreed by the reviewer on the plan itself. Two consequences
  the recommendation only implied, now that it is a decision. **The two halves have different
  owners and must not be sequenced as one** — the form block is Alex's and waits on him; the A2
  flag is ours, sits in 2.7, and should not be held for it. And **the A2 flag is not throwaway
  scaffolding retired once the form blocks**: it is the only thing that can reach Round 4 and
  earlier, and §2k shows 14 of 63 already carry an exceptional amount. Size it as a permanent check
  over the existing corpus, not as a stopgap.

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

### Revision 4 — the delivered artefacts, and the message that carried them

**Five of the twelve external dependencies in §5c were promised on 16 September. All five have been
delivered**, four of them in one message — `2026-09-16-emily-sheardown-artefact-delivery.md`, now
transcribed into `docs/Import/`.

| Artefact | Dependency it discharges | What it actually is |
|---|---|---|
| `3. Round 4 - Individual Applications.pdf` | **The current Trustee Pack** (EF-04, EF-07) | 63 applications, Round 4, one pack per applicant. The document the board already knows. Sent separately on the trustee-portal thread |
| `2. Group Applications - Round 5.pdf` | **A group application summary example** (EF-43) | 12 applications across 5 groups, Round 5 |
| `Postcode Details.xlsx`, sheet *Postcodes* | **The postcode export** (EF-03, EF-40, EF-41) | 3,394 postcode districts → town/city, county, region, country |
| **The covering email body** — income band table | **The income band options** (EF-29) | Four bands, listed out in the message and duplicated on the attachment's *Income Values* sheet |
| **The covering email body** — tickbox list | **The review checkbox items** (EF-21) | **Eight items, not five** — and Emily asks whether eight is too many |

**Two of the five were written in the message body rather than attached, and this plan missed both
on its first pass** (`IMP-0739`). Revision 4's first draft attributed the income bands to a
spreadsheet sheet and recorded EF-21 as still outstanding. **Both were set out in the mail itself.**
The lesson is narrow and worth stating once: **an email that carries attachments also carries a
body**, and the body is where a client puts the things too small to be a file.

### 2e. The eight review checkboxes, and what they independently confirm

Emily's list, verbatim: **Location · Date · Amount · Exceptional Circumstance · Disability
Information · Care Information · Group · Age** — with *"Sorry, slightly more than 5 but let me know
if these are too many!"*

**The count is an open question addressed to us, not a specification.** The walkthrough said *"up to
5 checkboxes"*; she sent eight and asked. **Answer: eight is fine** — these are yes/no fields in one
section, and the cost difference between five and eight is negligible next to the cost of her
working around three missing ones. Say so rather than letting it sit.

**Settled 2026-09-17: build all eight.** Agreed by the reviewer on the plan itself. Two things
follow that the answer above did not say, and the second is a design constraint rather than a
preference.

- **This is schema, not layout.** Eight booleans plus the free-text note is **nine new columns on
  `rev_application`**, so EF-21 carries a schema change into the A4 pass and should be estimated as
  one. It is the largest single block of new columns in this plan.
- **Give every checkbox NO default value, and take the precedent from this solution's own schema.**
  A Dataverse two-option column defaulting to *No* makes *"not yet checked"* indistinguishable from
  *"checked, and the answer is no"* — which would defeat the purpose, because Emily's own example is
  *"Location check complete: Yes/No"* and an unreviewed application would read as reviewed-and-failing
  across all eight. `rev_isgrouptrip` already solves exactly this and says so in its own description:
  *"No default value, so 'not answered' stays distinguishable from 'No'."* Follow it.

**The more useful finding is what the list corroborates.** Emily wrote it from the difficulties she
actually hits reading applications. It was written without sight of this plan, and **seven of her
eight land on problems this plan had already identified from the data**:

| Emily's checkbox | What this plan independently found |
|---|---|
| **Location** | Region derives wrongly for five postcode areas (EF-49), and town/city is the applicant's own unreliable typing (EF-03) |
| **Date** | 60 of 63 packs carry two dates the form is recorded as unable to supply, and one group pack ends fourteen months before it starts (EF-09) |
| **Amount** | £500 is the standard maximum and 14 of 63 exceed it (EF-31) |
| **Exceptional Circumstance** | **The strongest corroboration in the list.** EF-48 was raised in this revision from the packs alone — 14 applications request above the maximum and the reason field is blank in all 63. Emily wants a checkbox for exactly that gap |
| **Disability Information** | The condition/care wording and ordering problem (EF-37) |
| **Care Information** | Same section; also the overlapping care-hours bands in `CareHoursBandLabelMap` (§6 note 7) |
| **Group** | Group linkage is free text, inconsistently formed, and one typo splits a group silently (EF-42) |
| **Age** | The carer age-confirmation question is absent from the form (EF-35), which blocks half of EF-36 |

**What the checklist is, corrected by the reviewer 2026-09-17: it is Emily's own mental check made
visible, run before an application goes to the trustees — and it is permanent.** Revision 4 read the
overlap above the wrong way round and concluded the boxes were temporary manual controls that should
retire as each underlying item landed. **They are not workarounds, so they retire with nothing.**
Fixing region derivation does not remove the need for a caseworker to confirm she has looked at the
location on this application; **the box records that a person checked, not that the data is good.**
The two live side by side, as the reviewer put it — the fixes reduce what the check finds, never the
need to perform it.

Three things follow, and the first is the reason the correction matters:

- **These are workflow fields, not data-quality flags.** Their subject is the caseworker's action, so
  they are never derivable, never back-fillable, and no improvement elsewhere in this plan makes one
  redundant.
- **It sharpens the no-default rule above from a nicety to the whole point.** If the box records that
  a person checked, then an unticked box must mean *nobody has looked yet*. A column defaulting to
  *No* would assert that Emily reviewed every application and found every one wanting.
- **It places the section exactly.** The checklist is what Emily runs immediately before releasing an
  application to the portal, and the control that does the releasing is `rev_eligibleforround`.
  **Both belong in the same place on the new Casework tab (EF-47), in that order** — check, then
  release.

**The corroboration in the table above still stands, for a different reason than revision 4 gave.**
It does not make the boxes disposable; it shows the checklist and the fixes are aimed at the same
risks from opposite ends, which is why the checklist keeps its value as assurance after the fixes
land.

**And it is a second, independent argument for EF-47.** Eight new yes/no fields plus a free-text note
is a substantial block. Putting it on the General tab beside the applicant's wellbeing answers is
what created the confusion Emily is asking us to remove.

### 2f. What the trustee packs settle — and the one thing they contradict

**The packs are the answer to "what should our surfaces look like", because they are what the
trustees read today.** Their structure, in order, is:

> **Summary** → **Application Details** → **About Applicant** → **Current Circumstances** →
> **Financial Eligibility**

Seven items are settled by that structure and its wording, at no further cost:

| Item | What the pack settles |
|---|---|
| **EF-04** | The dependency is **delivered**. Pack order is the list above; the **score sits in the Summary at the top** and the question detail sits in *Current Circumstances* well below it. That is exactly the layout EF-04 and EF-07 ask for — it can now be specified rather than guessed |
| **EF-07 / EF-24** | The target format is confirmed verbatim. The pack renders the wellbeing block as question text plus the **answer's own label** — *"I've been feeling optimistic about the future · None of the time"*. Emily's EF-24 example was quoting her own pack |
| **EF-12** | **Closed by document, not inference.** The pack groups the wellbeing questions under literal headings *"In the last 2 weeks…"* (seven statements) and *"In the last year…"* (three). Questions 8, 9 and 10 are the last-year three. No confirming sentence needed |
| **EF-22** | The three-way split Emily asked for **is the pack's own structure**: the 0–10 life-satisfaction question, then *In the last 2 weeks…*, then *In the last year…*. Build to the pack |
| **EF-37** | The condition-and-care order is confirmed: conditions/illnesses → disability description → care support → care hours. **But the two packs disagree on one label** — see the trap below |
| **EF-38** | *Applicant Type* has exactly three values in live data: *A disabled person* (38), *A carer applying on behalf of a disabled …* (14), *A carer applying for yourself* (11) |
| **EF-09** | **No longer blocked the way this plan recorded.** 60 of the 63 packs carry a **populated Start Date and End Date**, as two separate fields, in both the Summary and Application Details |

**Trap 5 — NEW. The two packs disagree with each other on a field label, so "use the form's own
wording" has two answers.** The same disability free-text field is labelled **"Brief Confirmation"**
in all 63 individual packs and **"Brief Description of Disability"** in all 12 group packs. EF-37's
governing principle (§1) says prefer the live form's wording — but here Emily's own documents
conflict, and only one of them can be the form's. **Ask which; do not pick.** *Brief Description of
Disability* is the recommendation: it describes the content, and *Brief Confirmation* confirms
nothing.

**Settled 2026-09-17: the label is "Brief Description of Disability."** Agreed by the reviewer on the
plan itself. **Checking it against the form first changed what the decision means, and turned up two
things worth more than the label.**

**Neither pack carries the form's wording, so §1's principle does not in fact decide this.** The live
form asks *"Please briefly describe how your disability affects you"* and names its section
*Disability Information (Applicant)*. The agreed label is the closer of the two to that section name,
so the pick is sound — but it is our own wording, not the applicant's, and should be recorded as
such rather than as an application of §1.

**The field always describes the disabled person — the route only changes who types it.** The form
phrases the question two ways, *"how your disability affects you"* and, on the carer route, *"how
their disability affects them"*, and the packs render both into one row. That is correct, not a
collapse: **there is one subject, the disabled person this application is about.** On the carer route
the carer is filling the form in on that person's behalf.

**Revision 4's first draft read this wrong and the reviewer corrected it, 2026-09-17.** It described
the group pack's entry as *"the partner's condition"* and concluded the field's subject changes with
the route. **There is no partner's-condition concept**; the entry is the disabled person's condition,
written by their carer. The subject is constant.

**And the correction carries a scope boundary that is worth having on record: the carer's own
disability and support needs are not recorded at all.** That is deliberate, and it explains a shape
that would otherwise look like an omission. It also sharpens two items elsewhere in this plan —
on the *carer applying for yourself* route, **the applicant is not the disabled person**, so the
disability, the condition profile and the age facts on the record all belong to someone who did not
apply. **That is exactly why EF-35 exists**, asking the form for a carer's confirmation that the
person they support is over 18, and why EF-36's second half is blocked behind it.

**Answered 2026-09-17, and it closes the last open point on EF-37: both routes land in the same
column.** The intake flow transforms both form fields into the Application table's columns, and the
narrative a carer writes lands in `rev_narrativeraw` exactly as the applicant's own does. **So there
is nothing to build for the two routes — one column, one field on the form, one label.**

**The deployed flow already matches that, which is worth stating because it means EF-37 needs no
automation work at all.** `REVIntakeWordPressToDataverse` binds `rev_narrativeraw` to a single
trigger key, `narrative_raw`, with no branch on route — one unconditional mapping. EF-37 is a form
and portal change only.

**One residual risk, and it belongs with Alex rather than in this item.** What the flow cannot do is
notice if the carer-route answer ever arrives under a *different* key: `rev_intakereviewnote` records
Choice-column mismatches (FR-064) and nothing else, **so a missing or renamed free-text key would be
dropped in silence.** Worth one line to Alex when the other upstream changes go over, not a blocker
here.

*(`rev_supportrecipientotherconditionraw` was never the carer-route equivalent — it is export
column 78 and explicitly a condition not covered by the standard list, a different question.)*

**EF-09's blocker is real, and revision 4 nearly talked itself out of it.** The plan recorded EF-09
as blocked by gap M-06 — *"the form supplies one free-text provisional date, so the two date columns
cannot be populated"*. Revision 4 offered *"either M-06 is wrong, or Emily splits the date by hand"*,
and a first pass on 17 September took the reviewer's note that **`rev_breakstart` and `rev_breakend`
exist** as proof of the first. **It is not, and the second reading is the correct one.** Checked
against source:

- The columns exist, and `REVIntakeWordPressToDataverse` declares `break_start` and `break_end` as
  two trigger fields bound straight to them. **Our half is built and waiting.**
- **But the live form asks one free-text box.** Field 75, *"Provisional date"*, help text
  *"e.g. 'July 2025' or 'Summer 2025'"* — free text by design (V-04). Nothing populates the two
  columns today.
- **An intake contract accepting a field is not evidence the form sends it.** The form-validation
  spec tracks that exact gap in its own M-10, *"accepted by the intake, never sent by the live
  form"*, and break dates fall in it.

**So M-06 stands, the dependency on Alex is real, and EF-09 stays blocked** — but the shape is
favourable: **columns, bindings and intake contract are all in place**, so the moment field 75
becomes two date pickers, EF-09 is the portal rename and nothing else.

**And the two dates in the packs are Emily's own.** 60 of 63 carry Start and End because she enters
them, from an export whose columns 117 and 118 one free-text answer cannot fill. **That is what makes
Group 101 — Start 1/10/2027, End 1/17/2026, fourteen months backwards — the useful finding**: an
unvalidated manual split, sitting in a document the board reads, and one more reason V-04 is worth
raising with Alex rather than living with.

### 2g. What the group pack settles — EF-43 is now designable

Revision 3 recorded EF-43 as *"the one item where the design is not settled enough to price"*. The
pack settles the content question completely and leaves only the interaction question open.

**The group pack is not a group document.** It is the individual pack, issued once per member, with
an identical group header block **repeated on every member's page**. Five groups, twelve members:

| Group code | Members | Group total cost | Group total requested | Per member |
|---|---|---|---|---|
| `101` | 2 | £1,200 | £1,000 | £500 |
| `RA` | 4 | £2,075 | £1,400 | £350 |
| `100` | 2 | £1,045 | £1,000 | £500 |
| `43` | 2 | £1,450.80 | £1,000 | £500 |
| `300` | 2 | £2,567 | £1,000 | £500 |

Four things follow, and all four are design input EF-43 did not have:

- **The group summary field list is fixed and small** — group code, member count, group total
  holiday/activity cost, group total amount requested, and the shared start and end dates. Nothing
  else appears at group level.
- **Group total requested = the sum of the members' individual requests**, in all five groups. It is
  derived, not entered, so the group row needs no new stored column.
- **The group pack omits *Current Circumstances* entirely** — 12 of 12. Emily's own group view
  already drops the per-question wellbeing detail and keeps only the headline score. **So the group
  detail page does not need the score breakdown**, which removes the largest piece of what a
  "group detail page" might have meant.
- **The repetition is the problem EF-43 exists to solve.** A group of four is published today as the
  same totals typed onto four pages. One row per group is the de-duplication of that.

**And the group linkage codes are free text, inconsistently formed** — `101`, `RA`, `100`, `43`,
`300`. EF-42 describes `rev_grouplinkage` as *"the admin-assigned code (e.g. GP5)"*; live data
carries no `GP` prefix and mixes numeric with alphabetic. Grouping on it will work — it is an exact
string match — but **it is one typo away from silently splitting a group**, and neither EF-42 nor
EF-43 currently proposes any validation. Raise it; do not normalise the existing values without
asking, because the code is how Emily finds the group.

**Decided 2026-09-17: it stays manual, and that is a scope call rather than an oversight.** The
reviewer's position is that linking groups properly — a groups table, generated codes, referential
integrity — is **scope creep against this engagement**, worth doing in a later version. So the
free-text code and the typo risk are **an accepted risk, owned and dated**, not an open defect.

Two things follow, and the second is the one that matters for what gets built now:

- **Nothing in EF-42 or EF-43 should quietly start fixing it.** A saved view and a Trustee Portal
  table both group on `rev_grouplinkage` as it stands. Adding validation, a lookup or a normalising
  rule inside either item would be building the deferred version by instalments.
- **But the risk does not disappear because the fix is deferred, and EF-43 is where it bites.** The
  admin-side bucket (EF-42) shows a mistyped code as its own one-member group, which Emily can see
  and correct. **A trustee-facing group table shows the board a group of four as a group of three**,
  with the fourth sitting in the individual list below. **Worth one line in EF-43's design step**: a
  group row that shows its member count, so a split group looks wrong at a glance rather than
  plausible. That is presentation, not validation, so it stays inside the accepted scope.

**And there is a cheap hygiene measure that is not scope creep:** Emily's own *Group* checkbox in
EF-21 is exactly the manual control for this — the caseworker confirming the application is linked
to the right group before it goes to the panel. **The deferral and the checklist were designed
independently and cover each other.**

### 2h. What the postcode file settles — and the live defect it exposed

The *Postcodes* sheet is **3,394 rows, one per postcode district, no duplicates and no blanks**,
keyed exactly the way `PostcodeRegionMap` is keyed today. Three of revision 3's open questions close:

- **Provenance (§5a question 3): it is not Royal Mail PAF or the ONS Postcode Directory.** Both of
  those carry alphanumeric outward codes and current district boundaries. This file has **zero**
  outward codes with a trailing letter and contains abolished districts (`AB1`). It is a hand-built
  or scraped list. **That largely answers the licence question and replaces it with a quality one.**
- **"Province" (§5a question 3, second half): the file has no province column.** Its columns are
  *County / Broad Area*, *Region* and *Country*, and *Country* holds exactly four values — England,
  Scotland, Wales, Northern Ireland. Province meant country.
- **EF-29 is settled and all three sources now agree.** Emily's mail body and the attachment's
  *Income Values* sheet both give **four** bands — Under £15,000 · £15,000–£25,000 · £25,000–£35,000
  · Over £35,000 — matching the 2026-09-11 form capture exactly. `IncomeBandUpperBoundMap` is what
  is wrong: it holds `{1:9999, 2:19999, 3:29999, 4:39999, 5:999999999, 6:-1}` — five bands on
  £10,000 boundaries plus a sixth option, *Prefer not to say*.

  **Replace the whole option set with Emily's four, and drop *Prefer not to say* with the rest**
  (reviewer, 2026-09-17: it does not exist). Revision 4 argued for keeping option 6, on the grounds
  that deleting a value some record might carry turns a deliberate "unknown" into an unmappable one.
  **That argument does not apply here, and the reason has a deadline attached.** The live form never
  offered *Prefer not to say*, so nothing can ever have sent it; the committed option sets were
  placeholders (`M-07`, `OPEN-20`); and **the only data in DEV and Acceptance is demo data** (§6
  note 13). M-07's own rule is that trimming an option set is safe **before** any application exists
  and unsafe after — **so the window is open now and closes the first time a real application is
  scored.** Re-seed the four bands and trim the option set in one pass, ahead of go-live.

**The defect nobody asked about: region derivation is wrong today for 125 of the 3,394 districts.**
Reconciling Emily's file against the seeded `PostcodeRegionMap` finds five postcode areas where our
live answer differs from hers:

| Area | Example | Emily's file | What we derive today |
|---|---|---|---|
| `BB` | Blackburn | North West | **West Midlands** |
| `CT` | Canterbury | South East | **Not known** |
| `HP` | Hemel Hempstead | South East | **Not known** |
| `PE` | Peterborough | East of England | **East Midlands** |
| `WD` | Watford | East of England | **London** |

**`BB` is the instructive one, because it is wrong rather than absent.** The map's documented rule is
*"longest prefix wins"*, and `BB` is not in the map — so a Blackburn postcode falls back to `B`,
Birmingham, and **a Blackburn applicant is shown to trustees as West Midlands.** The fallback that
exists to be safe is what manufactures the wrong answer; `CT` and `HP` merely fall through to *Not
known*, which is at least visibly missing. This is live in all three environments and affects
`rev_locationarea`, which feeds the round statistics and the funder reporting EF-03 is being asked
for in the first place.

**So loading Emily's file is not only new capability — it repairs an existing one.** That changes
EF-41's shape: part of it is a defect fix against a contracted deliverable, and only the city/county
lookup is genuinely new. `commercial-agent` should see the two halves separately.

**Two quality findings to put to Emily before this file is loaded, neither of them blocking:**

1. **Central London will not match.** The file holds `EC1`–`EC4`, `WC1`, `WC2`, `SW1` and no
   alphanumeric codes at all. Real central London postcodes are `EC1A`, `WC2H`, `SW1A`. **Every
   central-London applicant fails the lookup**, and on the current fallback pattern would fail
   *silently*. Whatever is built must record a miss, not swallow it — the `rev_intakereviewnote`
   pattern (§EF-20) is the precedent this system already has for that.
2. **"County" is not a county in 1,018 of 3,394 rows (30%).** The column is honestly named *County /
   Broad Area*, and for Scotland (583), Wales (249) and Northern Ireland (99) it simply repeats the
   country. A further 87 rows carry `North West`, which is a **region** name in a county column. And
   179 rows carry compound values — `East/West Sussex`, `Kent/East Sussex`, `Lancashire/Cumbria`.
   **For a Scottish applicant, replacing Region with County shows the trustee the identical word**,
   so EF-40 does not improve the trustee list for 30% of applicants, and compound values are not
   "more specific for our funders" (EF-03's stated purpose) either.

### 2h-bis. The ONS Open Geography Portal, checked 2026-09-17 — and what it settles about *county*

Raised by the reviewer against the two quality limits above: could the postcode lookup be synced
from, or checked against, the ONS Open Geography Portal instead? **Checked, and it changes EF-40's
design more than EF-41's.**

**What the ONS Postcode Directory (ONSPD) is, verified against ONS's own pages:**

| | |
|---|---|
| **Licence** | **Open Government Licence v3.0** — free reuse, commercial or private, no application |
| **Attribution** | Three lines required, all three: *Contains OS data © Crown copyright and database right [year]* · *Contains Royal Mail data © Royal Mail copyright and database right [year]* · *Source: Office for National Statistics licensed under the Open Government Licence v.3.0* |
| **Coverage** | Every UK postcode at **unit level** — ~1.8M live, ~2.7M including terminated |
| **Cadence** | **Quarterly**: February, May, August, November |
| **Carries** | Administrative, electoral, health and census geography — local authority, ward, county, LSOA/MSOA |

**It fixes the first quality limit outright.** ONSPD is unit-postcode level, so `EC1A`, `WC2H` and
`SW1A` are all in it. The central-London gap in Emily's file simply does not arise, and terminated
postcodes are included too — useful, because an applicant may give an old one.

**It does not fix the second, and that is the finding worth having: *county* is not a UK-wide
attribute at all.** ONSPD's county field carries **pseudo-codes** rather than values —
`S99999999` for Scotland, `W99999999` for Wales, and `E99999999` for **English unitary
authorities** — because the top administrative tier is a council area in Scotland, a unitary
authority in Wales, and a unitary authority in much of England. **So the authoritative source
declines to give a county for exactly the places Emily's file fills in with the country name.**

**Neither source is wrong; the question is.** Emily's file papers the hole over with *Scotland*;
ONSPD papers it over with a pseudo-code; **there is no county to give a Glasgow or a Bristol
applicant, because they are not in one.** EF-40 asks for a column that will be empty or
meaningless for a large minority of applicants however it is sourced.

**So the recommendation for EF-40 changes, and it is cheaper rather than dearer.** If the purpose
is Emily's stated one — *"be even more specific with our funders"* — the attribute that exists
**everywhere in the UK** is the **local authority**, which ONSPD carries for every postcode with no
pseudo-codes. **Propose local authority in place of county**, and put that to Emily with the reason
rather than building a column that is blank for Scotland, Wales and unitary England.

**Three things that argue for ONSPD over the spreadsheet, and one that argues against:**

- **Provenance becomes citable.** §2h left Emily's file's origin unknown; ONSPD's licence is
  explicit and the three attribution lines are a known obligation rather than an open question.
- **It has an owner and a cadence.** Quarterly releases replace *"a static list needs an owner and
  a refresh interval"* with a published schedule.
- **It unlocks LSOA**, and with it the deprivation indices — a materially stronger funder-reporting
  attribute than a town name. Worth raising separately; it is not in scope here.
- **Against: Northern Ireland is carved out.** BT postcodes need **a separate licence from Land
  and Property Services for commercial use** — not from ONS. Emily's file carries 99 BT districts,
  so this is live for a UK-wide charity and **whether a charity's use counts as commercial is
  Revitalise's question, not ours.** Put it to them before anything is built on ONSPD.

**Volume is the practical constraint, and it forces a real choice rather than a preference.** 1.8M
unit postcodes is not a Dataverse reference table. Two shapes, and they are not equivalent:

- **Derive a ~3,000-row outward-code table from ONSPD**, keeping the existing `PostcodeRegionMap`
  shape. Cheap, fixes EF-49 in the same pass — **but an outward code can span more than one local
  authority, so it re-introduces at the district level the imprecision ONSPD was adopted to remove.**
- **Look up the unit postcode**, which is accurate and needs the full file somewhere outside
  Dataverse plus a lookup at intake. More work, and the only shape that actually delivers accuracy.

**Naming the trade-off is the point: the cheap shape and the accurate shape are different builds,
and EF-41 is already a change-order candidate, so `commercial-agent` should price the one Revitalise
chooses rather than a blend.** Nothing here changes EF-49 — the five missing prefixes are a defect
fix and should not wait for any of this.

### 2i. What the live data contradicts — EF-28b was wrong

**This plan asserted that the form does not suppress income questions on a benefits Yes. Round 4's
own data shows it does, in 63 cases out of 63, with no exceptions.**

| Means-tested benefits | Income band | Working status | Savings | Count |
|---|---|---|---|---|
| **Yes** | blank | blank | blank | **57** |
| **No** | populated | populated | populated | **6** |

EF-28b currently reads: *"This is not how the live form behaves. The only field conditional on a Yes
is the benefit provider. Emily is describing intended behaviour."* That conclusion came from
`docs/Import/2026-09-11-live-application-form-capture.md`, and a static capture of an unanswered form
shows every question present whether or not a conditional would later hide it. **The capture was
read as evidence of behaviour when it is only evidence of markup.**

**Settled 2026-09-17: the suppression is live. When benefits are selected, income does not have to
be filled in** — confirmed by the reviewer against the form. So of the two readings revision 4
offered, it is the first: **EF-28b is already built, it is not Alex's to do, and there is nothing to
re-test.** The 2026-09-11 capture recorded markup and was read as behaviour; the 57 blank rows were
the form working as intended.

**And gap M-04 is no longer hypothetical — it is the majority case, with a wrong value already
being written.** An absent income band must be read as *qualifies on benefit status*, not as missing
data. **90% of Round 4 has no income band**, and the option set shows what that produces today:

| `rev_incomeflag` | Label | What it means |
|---|---|---|
| 1 | Within income ceiling | income was compared against `IncomeCeiling` and passed |
| 2 | Above income ceiling | compared, and failed |
| 3 | **Not stated — cannot assess** | **where all 57 benefits-Yes applications land today** |

**"Cannot assess" is the opposite of true for them.** They are the most clearly eligible applicants
in the round — receiving a means-tested benefit is itself the evidence — and the system records
that it could not tell. **Nine applications in ten carry a flag that misdescribes them**, and value 3
is meant for a real unknown, which it can no longer be if it is also the default outcome of the
commonest path.

**The fix, and it is small because the option set is where the problem is:**

1. **Add a fourth option to `rev_incomeflag` — *"Qualifies on means-tested benefits"*.**
2. **Evaluate benefits first.** `rev_receivesbenefits` = Yes → flag 4, and **do not read the income
   band at all**. Order matters: run the income test first and the blank band sends everything to 3,
   which is exactly today's behaviour.
3. **Income band set → compare against `IncomeCeiling` → flag 1 or 2**, unchanged.
4. **Neither → flag 3**, which becomes rare and meaningful again.

**Why a distinct value rather than folding it into 1, *Within income ceiling*.** Flag 1 asserts a
comparison that was never made, and a trustee or an auditor reading it would reasonably assume
income had been measured against the ceiling. Keeping the routes apart also answers a question
Emily's funders actually ask — **how many qualified on benefits versus on income** — and it matters
for EF-46: when the ceiling moves, applications that qualified on benefits are unaffected, which is
only visible if the two were never merged. Record the deciding rule in EF-44's audit column.

**Two sequencing points, both cheap now and not later.** Adding an option to `rev_incomeflag` is an
option-set change under the same `M-07` window as EF-29's trim — **safe while only demo data exists,
unsafe once real applications carry the values** (§6 note 13), so do both in one pass. And **the
evaluation order now matches the field order Emily asked for in EF-28** — benefits, provider, income
band, income flag — which is a good sign that the form's order and the flow's order agree.

**Scope:** a scoring-flow change plus one option-set value, so **A2 — 2.7**, alongside EF-46's
re-seed. Not a change order.

### 2j. What the packs tell us about the thresholds EF-46 is about to settle

EF-46 asks Emily to settle `KnockoutThreshold`, `BorderlineBandLower/Upper` and `IncomeCeiling`,
all seeded PROVISIONAL. **She can now be shown what the provisional values would have done to two
real rounds** — which is worth more to that decision than any description of the bands:

| | Round 4 (63 individual) | Round 5 (12 group) |
|---|---|---|
| Auto-reject (score ≤ 20) | **1 (2%)** | 0 |
| Borderline (21–30) | 11 (17%) | 1 (8%) |
| Auto-pass (> 30) | **51 (81%)** | 11 (92%) |

**Two consequences, and the second changes an item's meaning.**

The knockout threshold is barely triaging: at 20, one application in 63 is filtered. That is a
finding for Emily to react to, not for us to fix — but she should see it before she confirms the
value rather than after.

**And EF-16's auto-pass bucket is not an exception queue — it is 81% of the round.** EF-16 was
accepted on the walkthrough's reasoning that auto-passed applications still need a qualitative read
of the free-text answers. At the provisional threshold that means the bucket holds 51 of 63
applications, so it is the *main* casework queue, and a saved view with no further sub-division will
not organise the work. Size EF-16 against that number, and sequence it after EF-46.

### 2k. Exceptional funding — the schema is ready, the reason field is not being captured

EF-31 asks for a block when the amount requested exceeds £500 without an exceptional-funding
request. The packs show that rule is **already the operating practice**: 14 of 63 applications carry
an exceptional amount, and in 13 of those 14 the total is exactly **£500 + the exceptional amount**
(£99 to £3,000). £500 is the standard maximum and exceptional funding is the named mechanism for
exceeding it.

**This de-risks EF-31 substantially — no new columns are needed.** `rev_exceptionalfundingrequested`
(bit), `rev_additionalamountrequested` (money), `rev_exceptionalcircumstance` (picklist, four
options) and `rev_exceptionalfundingdetail` all exist on `rev_application` already. The A2 flag for
the existing corpus is a flow change against present data.

**But the pack exposes a governance gap nobody raised: *Exceptional Circumstance* is empty in all
63 packs, including the 14 that carry an amount.** The charity is granting above its standard
maximum — up to six times it — with no recorded category or reason reaching the trustees who decide.
Logged as **EF-48**.

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

**Trap 4 is resolved by decision, 2026-09-17: county goes into the existing `rev_locationarea`
column, and region comes off the Trustee Portal.** No new column. That is a real simplification —
EF-40 stops being *add a column* and becomes *change what one column holds*, which is rework against
a contracted deliverable rather than new capability, and `commercial-agent` should re-read it on
that basis rather than as the `M` change order revision 4 priced.

**Three consequences the decision inherits, and the second is the one that would otherwise be found
late.**

**1. `rev_locationarea` is a closed 13-value Choice, and county is not.** The option set is the
twelve regions plus *Not known*. County has no authoritative UK-wide list — §2h-bis found that even
ONS returns pseudo-codes for Scotland, Wales and unitary England — and Emily's file offers 52 values
including compounds like *East/West Sussex* and the country name where there is no county. **So the
column must either take a ~50-option list built from a source with known defects, or become free
text.** Free text cannot be charted or filtered cleanly, **which works against the stated purpose of
being more specific for funders.** Worth putting to Emily as the trade it is.

**2. The option set is shared, and changing it changes the statistics table too.**
`rev_anonymisedstatistic`'s own column description says it **"REUSES the existing `rev_locationarea`
global option set"**. **A global option set edited in place therefore changes the anonymised
statistics entity at the same time**, silently and without anyone touching that entity — and that is
the table funder reporting runs on. **Either give the statistics entity its own region option set
before the change, or accept that its historic rows are re-labelled as counties.** This is the
single thing most likely to be discovered after the fact.

**3. EF-02's security half stands, and is now definite. Trustees see no location at all.**
Confirmed by the reviewer 2026-09-17, against the walkthrough. Revision 4 tabled two readings and
took the wrong one as its working assumption — **county replaces region for the GRANT ADMIN, not in
the trustee list.** So:

- **Secure `rev_locationarea` behind `REV_TrusteeRestricted`**, which is EF-02 as originally
  recorded: a live disclosure, because the column is unsecured today and reachable from any surface,
  not just the one that displays it.
- **Remove the location column from the Trustee Portal outright**, and **the region filter in
  `ApplicationFilters` with it** — the filter leaks the same values through its option list.
- **The privacy rider dissolves.** County being narrower than region does not matter to a trustee
  view that shows neither; it stays relevant only to the grant admin surface, where it was never in
  doubt.
- **EF-01 resolves cleanly in the same move.** It asked whether the grant admin should see region or
  county once trustees lost theirs; the answer is county, in `rev_locationarea`, on the Application
  record. Admin sees location, trustees do not — one column, one audience.

**This reduces a contracted deliverable, and that is now definite rather than conditional.** WBS 6.2
specifies the trustee list screen as *"applications with score, **region**, dates, status"*. The
screen will ship without a location column at all, which `pm-agent` should record against 6.2 rather
than let it read as an omission later.

**One thing to confirm, because the instruction as stated is absolute and one surface sits just
outside it.** `rev_anonymisedstatistic` holds a region column — its own description says *"Region
only, no address"* — and it is **not secured**. If the landing screen charts a regional distribution,
**trustees see location in aggregate** while seeing none per application. That is almost certainly
the intent, since an anonymised statistics table exists precisely to make aggregate reporting safe,
**but it is not what "trustees don't see location at all" says.** Worth one sentence to settle it,
and it interacts with the shared option set above: if that set becomes counties, the aggregate
becomes a county distribution too.

**Trap 5 — NEW in revision 4. Emily's two packs use different labels for the same field, so
"follow the form's wording" has two answers.** Stated in full in §2f: the disability free-text field
is *"Brief Confirmation"* in all 63 individual packs and *"Brief Description of Disability"* in all
12 group packs. **The §1 principle cannot resolve this on its own** — it assumes the client's
documents agree, and here they do not. **Settled 2026-09-17 as *Brief Description of Disability***,
and checking it against the form showed §1 could not have decided it either way: neither pack carries
the form's own wording. The same check found that the one pack field is fed by two different form
questions depending on the applicant's route — see §2f.

---

## 4. The items

**Size key.** `S` — a contained change to one surface. `M` — several surfaces, or one surface plus a
schema change. `L` — new capability with an external dependency. Sizes are relative shirt sizes for
triage only; hours belong to `commercial-agent` against `contract/wbs.json`, and this document
states none (`C-COM-008`).

**Δ** marks a row the 16 September walkthrough changed. **Δ4** marks a row the three delivered
artefacts changed (revision 4).

### 4.1 Source 1 — Trustee Review Portal (2026-09-07)

| Id | What Emily asked for | Surface | Resolution | Reserve | Proposed solution | Size | Depends on / conflicts with |
|---|---|---|---|---|---|---|---|
| **EF-01** | Region shown in the grant portal the grant admin uses | Grant admin app | `in-baseline` | **A4** — 4.5 | Region is already captured and readable by the grant admin as *Location Area* on the Applicant record. Surface it on the **Application** record, read-only, where casework happens | S | Bundle with EF-18, EF-38. **Δ4 The re-check is answered:** the grant admin's column holds **county** (EF-40), and trustees see no location at all (EF-02). One column, one audience |
| **EF-02 Δ** | Region must not be visible to trustees | Column security | `in-baseline` | **A6** — 6.8 | **Δ4 Settled 2026-09-17: trustees see no location at all.** A permissions change, not a UI change — `rev_locationarea` is unsecured, so trustees can read it from any surface, not only the one that displays it. **Add it to `REV_TrusteeRestricted`, drop the location column from `ApplicationsTable`, and drop the region filter in `ApplicationFilters`** with it, or the filter keeps offering the values through its option list | S | **Δ4 A live disclosure again, and now definite** — revision 4 briefly tabled a reading where trustees saw county; they do not. **Reduces a contracted deliverable:** WBS 6.2 specifies the list screen as *"applications with score, **region**, dates, status"* and it ships with no location column — `pm-agent` should record that against 6.2. `rev_agerange` is unsecured on the same footing, still unmentioned by Emily. **Δ4 No longer sequenced behind EF-40** — one column, different audiences |
| **EF-03 Δ4** | A city identifier derived from the postcode, because the typed city field is unreliable | Intake flow + schema | **`change-order-candidate`** | — | **No city derivation exists.** The city shown today is `rev_towncity`, the applicant's own typed answer — exactly the unreliable value Emily describes. Region *is* derived from postcode at intake via the `PostcodeRegionMap` setting, so the pattern exists, but that map holds regions, not settlements. **Δ4 The file has arrived and carries a *Main Postal Town / City* column keyed on postcode district** — the lookup is now specifiable | **M** *(was L)* | **Δ4 Licence blocker effectively gone** — the file is neither PAF nor ONSPD (§2h). Replaced by two quality limits: no alphanumeric London codes, and a *County* column that is not a county in 30% of rows |
| **EF-04 Δ4** | Mirror the current Trustee Pack's setup and wording | Trustee portal | `in-baseline` | **A6** — 6.8 | Re-label and re-order the detail screen to follow the pack the board already knows. **Δ4 The pack has arrived and its order is now specified, not inferred:** Summary → Application Details → About Applicant → Current Circumstances → Financial Eligibility, with the score in the Summary at the top and the question detail well below it | M | **Δ4 Dependency DELIVERED** — `docs/Import/3. Round 4 - Individual Applications.pdf`. This item is ready to build |
| **EF-05 Δ** | Notes compulsory for a rejection | Trustee portal | `in-baseline` | **A6** — 6.8 | Notes are optional today on all three verdicts — `VerdictForm` labels the field *Notes (optional)*. **Δ Require notes on Reject *and* Defer**, using the same inline validation the verdict radio already uses; leave Approve optional | S | **Δ Open question closed.** Revision 2 asked whether Defer should also require a note; the walkthrough answers yes |
| **EF-06** | *What is included in the anonymised narrative section?* | Trustee portal | `answer-only` | — | **Nothing today, by design.** The panel binds the redacted narrative column and nothing else. Narrative scrubbing (Automation #5) is deferred under exception `EX-003`, so the panel stays withheld until that automation is built | — | The answer doubles as a warning: `EX-003` clears only when Automation #5 lands *and* DPO sign-off arrives, before any live trustee demo |
| **EF-07 Δ4** | Move the full wellbeing answers lower down, show the actual questions and answers, keep only the score out of 60 at the top | Trustee portal + scoring flow | `in-baseline` | **A6** — 6.8 and **A2** — 2.7 | Two halves: the flow writes the breakdown with **question text and the answer's label** instead of *"Wellbeing answer 3: response 2 = 4 points"* (A2); the portal shows the score alone at the top and the expanded breakdown lower down (A6). **Δ4 The pack confirms the exact target format** — *"I've been feeling optimistic about the future · None of the time"*. Emily's EF-24 example was quoting her own pack | M | **Same underlying change as EF-24.** **Δ Now conflicts with the audit-column ask — resolved by the split in §2c and EF-44.** Build EF-44 first; EF-07 and EF-24 then write to the trustee-facing half only. **Δ4 Note the two answer scales** — the seven two-week statements use *None of the time…*, the three last-year statements use *Strongly disagree…* (gap M-02, now evidenced) |
| **EF-08** | *Holiday Details* → *Application Details* | Trustee portal | `in-baseline` | **A6** — 6.8 | Rename the panel. The live form's section 13 is already called *Application Details* | S | Settled without further input, per the §1 principle |
| **EF-09 Δ4** | *Preferred Dates* → *Start* and *End Date* | Trustee portal | `in-baseline` | **A6** — 6.8 | Rename and split the single row into two | S | **Δ4 Still blocked, and the reading is now settled (§2f).** The columns and the intake bindings exist — **our half is built** — but the live form asks one free-text *Provisional date* (field 75, V-04), so nothing fills them. **The two dates in the packs are Emily's own manual entry.** Once field 75 becomes two date pickers this is a portal rename and nothing more |
| **EF-10 Δ** | Helper, referee and contact details should not be in the Trustee Portal | Trustee portal + column security | `in-baseline` | **A6** — 6.8 | Two halves, one of them not cosmetic. The helper, referee and emergency-contact **names, emails and phone numbers** are already behind `REV_TrusteeRestricted` and render as withheld placeholders — the portal's generated restricted-field catalogue groups all eight under *"Helper, referee and emergency contact"*, which is exactly the panel Emily names. Removing it is presentation. **Helper Organisation and Helper Relationship are not in the profile and are readable by trustees today.** Secure those two, then remove the panel | S | A live disclosure, not a preference. **Δ Confirmed at the walkthrough**, which named emergency contact explicitly alongside helper and referee |
| **EF-11** | Remove *Days the round has been open* — not a representative figure | Landing screen | `in-baseline` | **`wbs:6.9`** — CO-001 | Remove the tile from `RoundStatistics` | S | **Δ Still open — the walkthrough did not settle it.** *Applications per day* is computed from the same day count Emily calls unrepresentative, so removing one and keeping the other is half a fix. Carry the question into the return email |
| **EF-12 Δ4** | Add wording for the wellbeing question 8, 9 and 10 statistics, **and** the circumstance score | Landing screen | **split** — `in-baseline` + `change-order-candidate` | **`wbs:6.9`** / CO-001-A3 | **Wording half — in-baseline:** label the three last-year charts with their full question text, taken from the pack. **Circumstance-score half — new:** there is no circumstance-score distribution, and CO-001's priced chart list does not include one | S / S | **Δ4 Closed by document, not inference.** The pack groups the questions under literal headings *"In the last 2 weeks…"* (seven) and *"In the last year…"* (three). 8, 9 and 10 are the last-year three. **Drop the confirming question from the return email** |

### 4.2 Source 2 — Grant administrator application (2026-09-08)

| Id | What Emily asked for | Surface | Resolution | Reserve | Proposed solution | Size | Depends on / conflicts with |
|---|---|---|---|---|---|---|---|
| **EF-13** | A simple end-to-end process flow of how the process works | Documentation | `in-baseline` | **A0** — 0.6 / 0.8 *(no reserve)* | **A process flow already exists** — `docs/Import/Revitalise-Process-Flow-v0.1.html`, a July 2026 draft. Sendable today but stale: it says the application *"lands in SharePoint"*, which is not what was built. Refresh to as-built and re-issue | S | One of the items landing on A0, which has no feedback row |
| **EF-14** | Some sections show a locked symbol — will the grant admin receive all access? | Access model | `answer-only` | — | **Yes, with one deliberate exception.** The padlock marks a column-secured field; the grant admin role is a member of the profile that releases them. The exception is **bank and payment data**, behind a second profile the grant admin is deliberately excluded from | — | Worth stating as a control she benefits from, not a limitation |
| **EF-15** | Auto-reject cases added as a category under *Casework* | Grant admin app | `answer-only` | — | **Already built** — *Auto-rejected Applications* sits under Casework with its own saved view | — | Confirm this is what she meant |
| **EF-16 Δ4** | Auto-pass cases added as a category under *Casework*, to check the free-text answers are sufficient | Grant admin app | `in-baseline` | **A2** — 2.7 | Add an *Auto-pass Applications* saved view and a Casework sub-area beside the existing four (Applications, Borderline — Awaiting Review, Under Review — Incomplete Scoring, Auto-rejected Applications) | S | **Δ4 The bucket is 81% of the round, not an exception queue.** At the provisional threshold, Round 4 splits 1 auto-reject / 11 borderline / **51 auto-pass** (§2j). A flat saved view will not organise 51 applications needing a qualitative read. **Sequence after EF-46** and size against the real number |
| **EF-17 Δ4** | A section at the end containing the full application | Grant admin app | `in-baseline` | **A4** — 4.5 | **Δ4 Her ask is one sentence, and most of what follows was ours.** Verbatim, and the only time it is raised: *"Can we have a section at the end that contains the full application?"* (Source 2, 2026-09-08). The walkthrough never returned to it. **Ours, not hers:** *read-only*, *tab* — **she said section** — and **in the order the applicant met them**, which has no basis in anything she wrote. The reading of *the full application* as *every captured answer* is ours too, though it is hard to read another way | M | **Δ4 Two things to settle before this is built or sized.** **Section or tab?** She asked for a section at the end; the plan turned it into a tab, which is a structural choice that now sits beside EF-47's Casework tab and should be made deliberately. **And keep or drop the form ordering?** The rationale is real but constructed — EF-22 and EF-37 both ask for the form's own structure and wording, so form order is consistent with them — **it is simply not something she asked for.** Cheap to keep, so say it is ours. Overlaps EF-37 — both need the form's question text |
| **EF-18** | Include personal details in the application — name, address, email | Grant admin app | `in-baseline` | **A4** — 4.5 | Surface the applicant's identity fields on the Application record, read-only, via the existing link | S | Bundle with EF-01, EF-38. **Note the design intent traded off:** the Application record deliberately shows a pseudonymised reference. Putting names on it is safe *only* because column security, not form design, is the control. **Δ** For views specifically, Emily can already self-serve a full-name column — see §5a |
| **EF-19** | *Quality Monitoring — where are these recorded?* | Grant admin app | `answer-only` | — | **The form's final section is called Equality Monitoring** — gender and ethnic group. Both are on the Applicant record, both column-secured, both readable by the grant admin, and neither reaches scoring or eligibility | — | Confirm the reading with her |
| **EF-20 Δ** | *Intake Review Note — assuming I will have access to all of these?* | Grant admin app | `answer-only` | — | Yes — and **Δ the walkthrough showed the real question is what it contains, not who can read it.** It is written by the intake flow when a Choice answer arriving from the form matches no configured option: the field, the raw value, and that no match was found. Empty when every answer mapped | — | **Δ Closes a Xander action item outright.** It is a data-quality log, not a caseworker's note |
| **EF-21 Δ4** | ~~Selectable categories in the Intake Review Note as well as free text~~ **Yes/no review checkboxes plus one free-text note** | Grant admin app | `in-baseline` | **A4** — 4.5 | **Δ Superseded — see §2b.** A new per-application review section. **Do not attach these to `rev_intakereviewnote`**, which is machine-written. **Δ4 The items have arrived and there are eight, not five:** Location · Date · Amount · Exceptional Circumstance · Disability Information · Care Information · Group · Age. **They land on the new Casework tab (EF-47)** | S → **M** | **Δ4 Dependency DELIVERED** in the 16 September mail body. **Δ4 Settled 2026-09-17: build all eight** — tell Emily, she asked. **Nine new columns on `rev_application`, all with no default value** so *"not yet checked"* stays distinguishable from *"checked, no"* (§2e). **Δ4 What it is, per the reviewer 2026-09-17: Emily's own mental check made visible, run before an application goes to the trustees — a permanent workflow control, not a workaround** (§2e). No item elsewhere in this plan retires a box. **Place it immediately before `rev_eligibleforround` on the Casework tab** — check, then release |
| **EF-22 Δ4** | Split the scoring into three sections: Life satisfaction / In the last 2 weeks… / In the last year… | Grant admin app | `in-baseline` | **A2** — 2.7 | **This is the form's own structure** — one 0–10 scale, seven two-week statements on a 5-point scale, three last-year statements on a 6-point scale. **Δ4 And it is the trustee pack's structure too**, under those literal headings, so the same split serves both surfaces | S | **Underlines a real data issue:** the three last-year questions use a different answer scale from the seven two-week questions (gap M-02). **Δ4 Now evidenced** — *None of the time…* versus *Strongly disagree…* in the live packs |
| **EF-23 Δ** | *What does "No Rounding was Applied" mean?* | Scoring flow | `answer-only` + `in-baseline` | **A2** — 2.7 *(for the removal)* | It means the score was already a whole number. **It is now the only message that can appear:** the branch for half-points existed for a *Not sure* answer, and *Not sure* is worth zero, so no fractional total is possible. Remove the sentence | S | **Δ Confirmed at the walkthrough**, which added the reason: the note described a manual override, not a system rounding rule. Fold the removal into EF-44's split |
| **EF-24** | Break the score breakdown down by question — *"I've been feeling optimistic about the future: response 1 = 5 points"* | Scoring flow | `in-baseline` | **A2** — 2.7 | Emily wrote the target format herself. Write the question text and the answer's label instead of a question number and a response number | S | **Same change as EF-07.** **Δ Sequenced after EF-44** |
| **EF-25 Δ4** | ~~*Knockout* → *Low band*~~ ~~*→ Threshold*~~ **→ *Threshold score*, across the entire app** | Scoring flow + Settings + docs | `in-baseline` | **A2** — 2.7 | **Δ Superseded — see §2b.** Change the word wherever a person sees it: score-breakdown text, Setting display label, sitemap, role definition, test fixtures, and `docs/training/casework-handbook.html`. **Δ4 The word is settled: *Threshold score***, agreed by the reviewer 2026-09-17 | S → **M** | **Change the label, never the Setting row's name.** The row is `KnockoutThreshold` and the flow looks it up by `rev_name` in all three environments. **Δ4 Our position is settled, Emily's is not** — she asked for *Threshold*, so the departure still needs her assent (§5a). Build to *Threshold score* unless she objects |
| **EF-26** | *What does the "Override" section show?* | Grant admin app | `answer-only` | — | It records a manual override of the automated outcome by the process owner: whether it was overridden, by whom, when, the reason, and the decision date — `rev_statusoverridden`, `rev_overriddenby`, `rev_overriddenon`, `rev_overridereason`, `rev_decisiondate` | — | **Δ Already answered by this plan before the walkthrough re-asked it.** Pair with EF-34, which increases how often an override will be needed |
| **EF-27 Δ** | An *action completed* record for safeguarding incidents | Grant admin app | `in-baseline` | **A0** — 0.4 *(no reserve)* | **Δ Now specified:** an *Action Completed* checkbox beside the existing `rev_safeguardingflag` and `rev_safeguardingnotes`, with the completion date **set automatically on tick so it cannot be backdated** | S | **Δ The auto-timestamp is a real design constraint, not a label.** A user-editable date column does not satisfy it — the value must be written by the platform (real-time workflow or business rule) and the column left read-only on the form. **Recommend also capturing *who* ticked it**: Emily's stated reason is record-keeping, and a safeguarding action with a date but no owner is weak evidence. Secure the new fields on the same basis as the existing ones |
| **EF-28 Δ** | Means-tested benefits moved to the front | Grant admin app | `in-baseline` | **A4** — 4.5 | **Δ Now specified to the exact order:** *Received means-tested benefits* → *Benefits provider* → *Income band* → *Income flag* (`rev_receivesbenefits`, `rev_benefitprovider`, `rev_incomeband`, `rev_incomeflag` — all four exist). Our app currently puts Income Band first | S | **Raises gap M-04:** if the four dependent questions are ever suppressed, an absent income band must be read as *qualifies on benefit status*, not as missing data |
| **EF-28b Δ4** | *"If they select yes they are not asked about income, employment status or savings"* | **Upstream WordPress form** | **Δ4 `answer-only`** — already built | **A1** — 1.2 / 1.4 *(spec side)* | **Δ4 CONTRADICTED, then settled.** This plan said the form does not suppress. Round 4 shows **57 of 57 blank on a Yes, 6 of 6 populated on a No**, and the reviewer confirmed it against the form on 2026-09-17: **when benefits are selected, income does not have to be filled in.** Already built — **not Alex's, nothing to re-test** | S (ours) | **Δ4 Resolution changes to `answer-only`.** The consequence is EF-28's: **gap M-04 now has a designed fix** — a fourth `rev_incomeflag` option, *Qualifies on means-tested benefits*, evaluated before the income test (§2i). Without it 90% of applications carry *"Not stated — cannot assess"* |
| **EF-29 Δ4** | Income bands set as per the form | Schema + spec | `in-baseline` | **A1** — 1.4 *(decision)* · **A2** — 2.7 *(implementation)* | **Δ4 SETTLED — three sources now agree.** Emily's 16 September mail body lists **four** bands — Under £15,000 · £15,000–£25,000 · £25,000–£35,000 · Over £35,000 — duplicated on the attachment's *Income Values* sheet and matching the 2026-09-11 capture exactly. `IncomeBandUpperBoundMap`'s five bands on £10K boundaries are the outlier and are wrong | S/M | **Δ4 Dependency DELIVERED.** `NFR-019` holds for the bands: the map changes, the scoring flow does not. **Δ4 Trim the option set in the same pass**: drop *Prefer not to say* — the form never offered it, the committed sets were placeholders (`M-07`, `OPEN-20`), and with only demo data in DEV and ACC the trim is safe now and unsafe once a real application is scored (§2h). No migration question: there is nothing real to migrate. *Cosmetic:* both of Emily's copies list *Over £35,000* third — take the set as authoritative and the order as a slip |
| **EF-30** | Employment status as a dropdown *as per form* | Schema | `answer-only` | — | **Settled, and nothing needs to change.** The live form's five options are exactly what `rev_employmentstatus` holds, and `EmploymentStatusLabelMap` maps them | — | Verified against the form capture; the schema was right |
| **EF-31 Δ4** | Automatic flag when the amount requested exceeds £500 (holidays/respite) or £100 (day trips/activities) **and** no exceptional funding request was made | **Δ Upstream form** + scoring flow | **Δ split** — `external-dependency` + `in-baseline` | **A1** *(form block)* · **A2** — 2.7 *(existing corpus)* | **Δ Reframed — see §2b. Δ4 Build both — settled by the reviewer 2026-09-17:** the form block for new submissions (Alex), and the A2 flag for applications already captured, which no form block can reach. **Do not sequence the two halves together** — the A2 flag is ours and must not wait on Alex. **Δ4 The rule is already the operating practice** — 14 of 63 Round 4 applications carry an exceptional amount and in 13 the total is exactly £500 + that amount (§2k). £500 is the standard maximum; exceptional funding is the named mechanism for exceeding it | M | **Δ4 Materially de-risked — no new columns.** `rev_exceptionalfundingrequested`, `rev_additionalamountrequested`, `rev_exceptionalcircumstance` and `rev_exceptionalfundingdetail` all exist on `rev_application`. **Δ Two details still to confirm:** whether £100 still applies, and whether EF-32 is live. **If £100 is dropped, EF-32 is moot** |
| **EF-32 Δ** | *Unsure how "other" should be treated* | Business rule | `answer-only` | — | She has effectively answered it: the admin re-classifies. Proposal to confirm — *Other* takes **no automatic threshold** and is flagged for manual review | — | **Δ May be moot.** It exists only because two thresholds needed a break-type test. A single >£500 rule does not |
| **EF-33** | Costs and Funding moved into the *Break Details* section | Grant admin app | `in-baseline` | **A4** — 4.5 | Move the Costs and Funding section from the Eligibility & Finance tab to Break Details | S | Presentation only — no automation reads a field's tab |
| **EF-34 Δ** | A *No* to *previous funding more than 12 months ago* should be auto-rejected | Scoring flow | `in-baseline` | **A2** — 2.7 | **Δ Now stated as an explicit compound condition:** received funding before **is Yes** *and* more than 12 months ago **is No** → auto-reject. Both columns exist (`rev_receivedfundingbefore`, `rev_morethan12monthsago`) and **no automation reads either today** | S/M | **Conflicts with an open compliance decision.** Whether automatic rejection may stand without human review is open for the DPO under the Data (Use and Access) Act 2025 (rule BR-S10). **Δ The compound form makes this sharper, not safer** — it is a second fully automatic rejection path. Recommend routing the outcome to the process owner rather than closing the application until the DPO decides |
| **EF-35** | A new form question: carers confirm the person they support is over 18 | **Upstream WordPress form** | `external-dependency` | **A1** — 1.2 / 1.4 · **A4** — 4.2 | **Confirmed genuinely absent.** The live form has *"I confirm I am 18 years of age or over"* for the applicant and no equivalent for the person supported | S (ours) | Blocks the second half of EF-36 |
| **EF-36** | Show both age confirmations and the age range in the eligibility section | Grant admin app | `in-baseline` | **A4** — 4.5 | Surface the existing applicant confirmation and the derived age range in the eligibility section rather than under Consent | S | **Partly blocked by EF-35** |
| **EF-37 Δ4** | Show the questions as worded on the form — she cannot tell which is which | **Δ Grant admin app + trustee portal** | `in-baseline` | **A4** — 4.5 **Δ and A6** — 6.8 | **Δ Now specified to the field and the order.** Labels mirror the web form's wording; *"Support recipient condition profile"* means **a carer completing conditions on behalf of the person they support**; the care-support description merges into the same section; the field order is **conditions/illnesses → brief disability description → care support details, including hours**. **Δ4 The packs confirm that exact order** | S → **M** | **Δ Now two surfaces, not one.** Overlaps EF-17. **Δ4 Trap 5 — settled 2026-09-17 as *Brief Description of Disability*** (the packs disagreed; §2f). **Two things the check turned up:** neither pack carries the form's own wording, so this is our label rather than an application of §1; and **the field's subject is constant — the disabled person** — with the route changing only who types it (reviewer, 2026-09-17). **The carer's own disability and support needs are not recorded at all**, which is deliberate and is why EF-35 exists. **Δ4 Closed 2026-09-17: both routes land in `rev_narrativeraw`**, and the deployed intake flow already binds it from one trigger key with no route branch — **so EF-37 is a form and portal change with no automation work** |
| **EF-38 Δ4** | Show whether the applicant is a disabled person, a carer, and so on | Grant admin app | `in-baseline` | **A4** — 4.5 | **No new question needed.** The form's *"Are you"* answer is stored as *Applicant Type* on the Applicant record. Surface it in Support Needs | S | Bundle with EF-01, EF-18. **Δ4 Three values confirmed in live data** — *A disabled person* (38), *A carer applying on behalf of a disabled …* (14), *A carer applying for yourself* (11) |
| **EF-39** | Remove the date and time stamps on consents | Grant admin app | `in-baseline` | **A4** — 4.5 | **Hide them from the form's layout; keep the columns.** They add nothing to a caseworker reading the record, and they are the charity's evidence of *when* each consent was given | S | **The one item where the recommendation is not to do exactly what was asked** — and the reviewer has agreed with that reading |

### 4.3 New in revision 3 — from the 16 September walkthrough

| Id | What Emily asked for | Surface | Resolution | Reserve | Proposed solution | Size | Depends on / conflicts with |
|---|---|---|---|---|---|---|---|
| **EF-40 Δ4** | A **County** column, replacing Region in the trustee list | Schema + both portals | **`change-order-candidate`** | — | **The column does not exist** — the Applicant entity holds `rev_towncity`, `rev_postcode` and `rev_locationarea`, and no county. Add a county column, populate it at intake, and use it as the trustee list's location column in place of region | **M** | **See Trap 4 — this and EF-02 are one decision.** **Check the raw export first:** county is column 23 and may be recoverable for historic applications without any lookup. **Δ4 Settled 2026-09-17: county goes into the existing `rev_locationarea` column, for the GRANT ADMIN.** Trustees see no location at all (EF-02), so this is not a trustee-list column after all — **no new column, and no trustee-facing change.** Re-read it as rework, not a change order (§3). **Two riders:** the column is a closed 13-value Choice and county has no clean UK-wide list — ONS returns pseudo-codes for Scotland, Wales and unitary England (§2h-bis), so **local authority is the better attribute if funder reporting is the purpose**; and the option set is **shared with `rev_anonymisedstatistic`**, which changes with it |
| **EF-41 Δ4** | Postcode → city/county lookup, from Emily's own export | Intake flow + reference data | **`change-order-candidate`** | — | **The route Emily prefers is Option 1** — load her export as a reference table and look up on the outward code, the same shape as the existing `PostcodeRegionMap`. **Δ4 The file fits that shape exactly:** 3,394 rows, one per postcode district, no duplicates, no blanks | **M** | **Δ4 Dependency DELIVERED, and the three questions are answered — see §2h.** **(1) Provenance:** not PAF and not ONSPD — the file has zero alphanumeric outward codes and contains abolished districts, so it is hand-built or scraped. The licence question largely dissolves and becomes a quality question. **(2) *Province* meant *Country*** — four values, England/Scotland/Wales/NI. **(3) Staleness still applies** and still needs an owner. **Two new quality limits:** central London will not match at all (no `EC1A`/`WC2H`/`SW1A` — must record a miss, not swallow it), and the county caveat under EF-40. **Δ4 Split the pricing:** loading this file also *repairs* region derivation, which is a defect fix against a contracted deliverable, not new capability |
| **EF-42 Δ4** | A **Groups** bucket in the admin app, grouped by the linkage code | Grant admin app | `in-baseline` | **A4** — 4.5 | Add a *Group Applications* saved view and Casework sub-area, grouped on `rev_grouplinkage` — the admin-assigned code the process owner sets by hand | S | **The column and its semantics already exist and are already relied on**: its own description records that *"the combined-amount check groups on this column"*. Keep it distinct from `rev_isgrouptrip`, which is the applicant's own claim. **Δ4 The codes are free text and inconsistently formed** — Round 5 carries `101`, `RA`, `100`, `43`, `300`, with no `GP` prefix anywhere, so **one typo silently splits a group**. **Δ4 Decided 2026-09-17: it stays manual** — a groups table and generated codes are scope creep for this engagement and belong to a later version (§2g). **Accepted risk, owned and dated: build the view on the column as it stands and add no validation here**, or this item builds the deferred version by instalments. EF-21's *Group* checkbox is the interim control |
| **EF-43 Δ4** | A **group applications table** in the Trustee Portal, above the individual list, with a group detail page | Trustee portal | **`change-order-candidate`** | — | A second table above the applications list, one row per group, opening a group detail page. **Δ4 The content is now fully specified by the delivered example (§2g):** the group row carries group code, member count, group total holiday/activity cost, group total requested, and the shared start/end dates — nothing else. **Group total requested is the sum of the members' individual requests in all five groups, so it is derived, not stored** | **L** | **Still the largest genuinely new item.** WBS 6.2 specifies a single list screen, so a second entity-level table with its own detail route is a new screen. **Δ4 Dependency DELIVERED and the design is now mostly settled.** The group pack omits *Current Circumstances* in 12 of 12 — **so the group detail page does not need the score breakdown**, which removes the biggest unknown. Only the interaction model (expandable rows vs. separate page) is still open, and it is now a small question rather than an open-ended one. **Δ4 One line for the design step:** group linkage stays a manual free-text code by decision (§2g), and a mistyped one shows the board **a group of four as a group of three**. **Put the member count on the group row** so a split group looks wrong at a glance — presentation, not validation, so it stays inside the accepted scope |
| **EF-44** | Move the scoring-calculation text to an **audit-only column**, out of the Trustee Portal | Scoring flow + schema | `in-baseline` | **A2** — 2.7 | **Split `rev_scorebreakdown` into two — see §2c.** A trustee-facing breakdown (question text and answer label, per EF-07 / EF-24) and a new admin-only audit column recording the threshold values in force at the moment of scoring, the status derived, and the rule that produced it | **M** | **Sequence before EF-07 and EF-24**, which otherwise write to a column about to change meaning. **Urgent for a reason the walkthrough did not state:** four thresholds are seeded PROVISIONAL pending OQ-001/002/003 and Emily is about to settle them (EF-46). Applications scored before that change are only defensible if the audit column exists first |
| **EF-45** | An **auto-reject reason** shown per application | Scoring flow + schema | `in-baseline` | **A2** — 2.7 | **Feasible, and cheaper than it sounds.** The flagging step already evaluates each rejection condition in order; write the deciding condition to a column as it does. Emily's question was whether it can be automatic — it can, because the flow knows the answer at the moment it sets the status | S | **Evaluate with EF-44 and EF-34**, not separately: all three write to the scoring flow's output, and EF-34 adds a second rejection path that makes a reason field more valuable. **Order matters** — if both the threshold and the 12-month rule reject an application, the reason must be deterministic, so fix the evaluation order explicitly rather than inheriting it |
| **EF-46 Δ4** | Review and settle the scoring settings — borderline band, income ceiling | Settings | `answer-only` → **decision** | **A2** — 2.7 *(re-seed only)* | **Not a build item — a decision item, and it closes three open SDD questions.** `KnockoutThreshold` (20), `BorderlineBandLower` (21), `BorderlineBandUpper` (30) and `IncomeCeiling` (£25,000) are all seeded **PROVISIONAL** pending **OQ-001, OQ-002 and OQ-003**. **Δ4 Emily can now be shown what those values do to two real rounds** — Round 4 splits **1 auto-reject / 11 borderline / 51 auto-pass**, Round 5 groups **0 / 1 / 11** (§2j). At 20, the knockout threshold filters one application in 63 | S | **Sequence this first, because it is free and it gates others.** **Δ4 Send her §2j's Round 4 / Round 5 distribution with the settings page** — the applications she sees in the environment are demo data (§6 note 13), so the on-screen effect of a threshold is not evidence for choosing it. **Re-seed all three environments together** — `dev-scoring-settings.json`, `test-settings.json` and `prd-settings.json` each hold their own copy and are not read from one another at run time. **Δ4 Check `IncomeCeiling`'s use in the scoring flow before re-seeding:** 90% of Round 4 has no income band at all (§2i), so a ceiling test against a blank value is the majority path, not the exception |

### 4.4 New in revision 4

**EF-47 comes from the reviewer, not from Emily. EF-48 and EF-49 come from reading the delivered
documents against source — nobody raised either.** All three are marked so, because an item's origin
changes who confirms it.

| Id | What is asked for | Surface | Resolution | Reserve | Proposed solution | Size | Depends on / conflicts with |
|---|---|---|---|---|---|---|---|
| **EF-47** | **A separate tab on the Application form holding every case-work handling field**, to remove confusion for Emily | Grant admin app | `in-baseline` | **A4** — 4.5 | **Move the casework fields off the General tab onto a new *Casework* tab** — see the inventory below. The General tab currently does four jobs at once, and that is the confusion | **M** | **Raised by the reviewer, 2026-09-17.** Not standalone — it is the organising principle six existing items land on. Sequence it **first** in the A4 pass |
| **EF-48 Δ4** | An exceptional-funding request with no recorded reason | Grant admin app + upstream form | `answer-only` → **decision** | **A4** — 4.5 *(surface)* · **A1** *(capture)* | **Found in the packs, then confirmed by Emily without either side seeing the other.** *Exceptional Circumstance* is blank in all 63 Round 4 packs, including the 14 carrying an exceptional amount of £99–£3,000. `rev_exceptionalcircumstance` (a four-option picklist) and `rev_exceptionalfundingdetail` exist and are not reaching the trustees who decide | S | **Governance, not UI.** **Δ4 Emily's own checkbox list names *Exceptional Circumstance* as one of her eight difficulty areas** — so she hits this gap manually today, from the other direction and without sight of this plan. **Δ4 But the packs establish only that the reason does not reach the trustees, not that it is absent at source** — a blank field in a pack can equally be a template that never merged it. The §5a question stands and must be answered from the raw export or the live form: **DEV and Acceptance hold demo data and cannot settle it** (§6 note 13). **EF-21's checkbox is the interim control either way** |
| **EF-49** | Region is derived wrongly for five postcode areas | Intake flow + settings | `in-baseline` — **defect** | **A4** — 4.5 | **Found by reconciling Emily's postcode file against the seeded `PostcodeRegionMap` (§2h).** `BB` → West Midlands (should be North West), `PE` → East Midlands, `WD` → London, and `CT`/`HP` → *Not known*. 125 of 3,394 districts. `BB` is wrong rather than absent because the documented *"longest prefix wins"* rule falls back to `B` for Birmingham | S | **A live defect against a contracted deliverable, not new capability** — `rev_locationarea` feeds the trustee list, the round statistics and the funder reporting EF-03 exists to improve. Fixable today by adding the five prefixes, independently of EF-41. **Do not bundle it into EF-41's change order** |

#### EF-47 — what belongs on the Casework tab, and why the General tab is the confusion

The Application form's **General** tab currently carries five sections doing four unrelated jobs:
record identity, the applicant's own wellbeing answers, and three separate blocks of casework
handling. Nothing signals which fields Emily is meant to *read* and which she is meant to *write*.

**EF-20 is the proof this is a real problem, not a tidiness preference.** Emily asked what the
*Intake Review Note* was. It is a machine-written data-quality log — but it sits in the **Application**
section, framed exactly like a field a caseworker fills in. The form's layout produced the question.

**The dividing line: what the applicant submitted stays; what the charity records or derives moves.**

| Moves to **Casework** | From | Why |
|---|---|---|
| `rev_status` | General → Application | The charity's decision state |
| `rev_intakereviewnote` | General → Application | Machine-written data-quality log (EF-20) |
| `rev_circumstancescore`, `rev_scorebreakdown`, `rev_scoredon` | General → Scoring | Scoring **outputs**, not answers |
| `rev_statusoverridden`, `rev_overriddenby`, `rev_overriddenon`, `rev_overridereason`, `rev_decisiondate` | General → Override | Pure casework (EF-26) |
| `rev_eligibleforround`, `rev_reviewround` | General → Trustee Portal | Process routing the process owner sets |
| `rev_safeguardingflag`, `rev_safeguardingnotes` | General → Safeguarding | Casework, plus EF-27's new *Action Completed* |
| `rev_incomeflag` | Eligibility & Finance → Income | A derived eligibility flag, not an applicant answer |

| Stays where it is | Why |
|---|---|
| `rev_name`, `rev_applicantid`, `rev_sourcesubmissionid`, `rev_submittedon` | Record identity and provenance — the General tab's real job |
| `rev_feelingscaleanswer`, `rev_wellbeinganswer1`…`10` | **The applicant's own answers.** EF-22 splits these into three labelled sections, which only works once the machine outputs have left |
| Everything on Eligibility & Finance, Break Details, Support Needs, Helper & Referee, Consent, How Did You Hear | Applicant-submitted content |

**Four items in this plan land on the new tab, and one is made cheaper by it:**

- **EF-21** — the **eight** review checkboxes plus free-text note (Location, Date, Amount,
  Exceptional Circumstance, Disability Information, Care Information, Group, Age). This is where
  they belong, and §2b's warning holds: **they are new fields, not an extension of
  `rev_intakereviewnote`.** Eight yes/no fields plus a note is a block large enough that placing it
  on the General tab, beside the applicant's wellbeing answers, would deepen the very confusion
  EF-47 exists to remove. **Δ4 And it fixes the tab's internal order.** The checklist is what Emily
  runs immediately before releasing an application to the trustees, so it sits **directly above
  `rev_eligibleforround` and `rev_reviewround`** — check, then release. That pairing is the strongest
  argument in this plan for the Casework tab existing at all: today the check has nowhere to live and
  the release control sits on the General tab among the applicant's own answers.
- **EF-27** — the safeguarding *Action Completed* checkbox with its platform-set date.
- **EF-44** — the new admin-only scoring audit column.
- **EF-45** — the auto-reject reason.
- **EF-22** is made cheaper: splitting the wellbeing answers into three sections is simpler once
  `rev_circumstancescore` and `rev_scorebreakdown` are not sitting among them.

**Two things this is not.** It is not a security control — `rev_intakereviewnote` is already
`IsSecured=1` and moving a field between tabs changes no permission. And it is not the same as
**EF-17**'s *Full Application* tab: EF-17 is what the applicant said;
EF-47 is what the charity did. **They are complements, and building EF-47 first gives EF-17 a
coherent form to sit in** rather than a third overlapping view.

---

## 5. The three lists that need separate action

### 5a. Answerable by return email, at no build cost

**Fifteen items.** Three added in revision 3: **EF-20**, **EF-26** and the full-name column.
**Revision 4 adds EF-29** — the band list has arrived, so the answer is now *"received, and it
matches the form"* rather than a request.

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
| **EF-29** | **Received, and it matches.** Her four bands are exactly what the live form asks. Our own setting still has the older £10K/£20K/£30K/£40K+ brackets and will be corrected. Our own setting also carries a *Prefer not to say* option the form never offered, left over from the placeholder lists; we are removing it in the same change. Nothing to ask — just flagging it so the option list she sees matches her own |
| **EF-21** | **Eight is not too many — we are building all eight.** She asked, so answer it plainly rather than leaving her guessing. Two things worth adding: each box will start blank rather than pre-set to *No*, so an application she has not opened yet cannot be mistaken for one she checked and failed; and the section will sit directly before the control that releases an application to the trustees, so the checklist runs where she would naturally run it |

**Four questions to put to her in the same email**, because building on a guess would be worse than
asking. **EF-12's "which questions" and EF-41's provenance are answered by the delivered documents;
EF-37's label was settled on 17 September and never needs asking. EF-48 is the one wholly new
question, and EF-25 has become a recommendation rather than a choice:**

- **EF-31 — does the £100 day-trip threshold still apply?** The walkthrough named only £500. If
  £100 is dropped, EF-32 disappears with it.
- **EF-11 — should *Applications per day* go as well?** It is computed from the same day count she
  calls unrepresentative. Asked in revision 2, still unanswered.
- **EF-25 — we propose *"Threshold score"* rather than *Threshold*; any objection?** Not a choice
  to hand back: at least three other thresholds exist in this system, so the bare word would be
  less specific than the *Knockout* it replaces. Settled on our side 2026-09-17 — put it to her as
  a recommendation with the reason, not as a menu.
- **NEW, EF-48 — where is the reason for an exceptional-funding request recorded?** Fourteen Round 4
  applications ask for £99–£3,000 above the standard maximum and the *Exceptional Circumstance*
  field is blank in every pack. If it is captured somewhere else, we will surface it; if not, that
  is worth knowing before the next panel.

**Three things to tell her rather than ask**, all found in her own files:

- **EF-49 — we found a live defect in how region is worked out, by checking her postcode list
  against ours.** Blackburn postcodes are currently showing as West Midlands, and Canterbury and
  Hemel Hempstead as *Not known*. Five areas, being fixed. **Say this plainly** — it affects the
  location shown on the trustee list today.
- **EF-09 — her group pack has Group 101 running from 10 January 2027 to 17 January 2026**, an end
  date fourteen months before the start. The form only asks for one free-text date, so the Start
  and End on her packs are typed in by hand with nothing checking them. Worth fixing at the form,
  and her new *Date* checkbox catches it in the meantime.
- **EF-28b — the form already skips the income questions when someone is on means-tested
  benefits**, in all 57 Round 4 applications that answered Yes. Nothing to change there; what we
  are fixing is on our side, where those applications currently read *"income not stated —
  cannot assess"* when they are in fact the most clearly eligible in the round.

### 5b. Change-order candidates — to `commercial-agent` before any delivery work (`C-COM-002`)

**Still four items, but revision 4 changes what two of them are.** EF-43 is now designable, and
EF-41 has to be split before it is priced.

| Item | Why it is genuinely new | Size |
|---|---|---|
| **EF-40 — a County column** | The column does not exist, and its absence is a recorded design decision rather than an omission. **Take it to `commercial-agent` together with EF-02**, which is what makes it necessary. **Δ4 Price the question as well as the build:** for 30% of applicants Emily's county value repeats the country, so county would show the trustee the same word region did | **M** |
| **EF-41 — postcode → city/county lookup** | **Δ4 Split it before pricing.** Loading the file also *repairs* region derivation for five postcode areas (EF-49) — a defect fix against a contracted deliverable, not new capability. What remains new is the city/county lookup, its reference table, and an owner for keeping it current. **The provenance question is answered** (neither PAF nor ONSPD) and no longer blocks | **M**, part of it rework |
| **EF-43 — group applications in the Trustee Portal** | A second entity-level table with its own detail route. WBS 6.2 specifies one list screen of applications. **Δ4 Now priceable.** The delivered example fixes the group row's five fields, shows the group total is derived rather than stored, and — by omitting *Current Circumstances* in 12 of 12 — establishes that the group detail page needs no score breakdown. **Only the interaction model is still open**, so revision 3's *"price the design, not just the build"* becomes a short design step rather than an open-ended one | **L** |
| **EF-12, second half — a circumstance-score distribution on the landing screen** | No circumstance-score distribution exists and CO-001's priced chart list does not name one. An amendment to CO-001, for which **CO-001-A1 and CO-001-A2 are the established precedent** | S |

**EF-42** (the Groups bucket in the admin app) is deliberately **not** on this list: a saved view and
a sitemap sub-area over a column that already exists is the same shape of work as EF-16, which is
in-baseline. Only the Trustee Portal half is new.

**Nor are the two items revision 4 adds.** **EF-47** (the Casework tab) moves existing fields between
tabs on a form A4 already owns and adds no column — the same shape of work as EF-33. **EF-49** (wrong
region for five postcode areas) is a wrong value in a shipped deliverable, which is rework against
`rev_locationarea`, not new scope.

### 5c. External dependencies, with their owner

| Dependency | Owner | Blocks | State |
|---|---|---|---|
| **The postcode export** — city, county, province | Emily Sheardown | EF-03, EF-40, EF-41 | **Δ4 DELIVERED 2026-09-16** — `docs/Import/Postcode Details.xlsx`, sheet *Postcodes*. Provenance established as neither PAF nor ONSPD, so the licence question largely dissolves. **Replaced by two quality limits** — no alphanumeric London codes, and *County* is not a county in 30% of rows (§2h) |
| **The review-checkbox items** | Emily Sheardown | EF-21 | **Δ4 DELIVERED 2026-09-16** in the mail body, not as an attachment. **Eight items, not the five the walkthrough recorded**, and Emily asks whether eight is too many — that question is owed an answer (§2e) |
| **The income band options from the live form** | Emily Sheardown | EF-29 | **Δ4 DELIVERED 2026-09-16** — listed in the mail body and repeated on the postcode file's *Income Values* sheet. **Four bands, matching the 2026-09-11 capture exactly.** `IncomeBandUpperBoundMap`'s £10K/£20K/£30K/£40K+ brackets are what is wrong. Dependency closed |
| **The current Trustee Pack** — layout and wording | Emily Sheardown | EF-04, EF-07 | **Δ4 DELIVERED 2026-09-16** — `docs/Import/3. Round 4 - Individual Applications.pdf`, 63 applications. Section order, field labels and answer-label format all now specified rather than inferred |
| **A group application summary example** | Emily Sheardown | EF-43 | **Δ4 DELIVERED 2026-09-16** — `docs/Import/2. Group Applications - Round 5.pdf`, 12 applications across 5 groups. Content settled; only the interaction model is still open |
| **A >£500 exceptional-funding block on the form** | Alex (website) | EF-31 | **Δ New.** Raised at the walkthrough as Xander's action to put to Alex |
| ~~**Conditional suppression of income, employment and savings on a benefits Yes**~~ | ~~Alex (website)~~ | EF-28b | **Δ4 NOT A DEPENDENCY — already built.** Confirmed against the form 2026-09-17: when benefits are selected, income does not have to be filled in. 57 of 57 Round 4 applications agree. **The work it creates is ours, not Alex's** — gap M-04's income-flag fix (§2i) |
| **A carer age-confirmation question on the form** | Alex (website) | EF-35, second half of EF-36 | **Confirmed absent** from the live form |
| **The scoring treatment of the income-band boundaries** | Emily + trustee board | EF-29 | How the income flag treats a boundary value stays a Revitalise decision |
| **OQ-001 / OQ-002 / OQ-003 — the threshold values** | Emily + trustee board | EF-46, and the value of EF-44 | **Δ In progress.** Emily is reviewing the scoring settings page. All four values are seeded PROVISIONAL today |
| **Structured break dates on the form** | Emily via Alex | EF-09 | **Δ4 Confirmed real, after a first pass on 17 September wrongly struck it.** The columns, the intake bindings and the export's two date columns all exist; **the live form's field 75 is one free-text box** (V-04), so nothing fills them. **Add to Alex's list, and ask for end-after-start validation with it** — Group 101 runs fourteen months backwards |
| **DPO decision on automatic rejection** under the Data (Use and Access) Act 2025 | DPO via Emily | EF-34 | Open (rule BR-S10). **Δ More pressing** — EF-34 is now specified as a fully automatic compound rejection |

---

## 6. Notes for `commercial-agent` and `pm-agent`

**1. Task 2.6's activity has now been performed.** Revision 2 recorded that Emily's second email
*was* 2.6's feedback log, arriving without the walkthrough the task names. The walkthrough was held
on 16 September against that log. **2.6 closes on its own evidence, not on a substitute**, which
unblocks 2.7.

**2. The reserve model holds, with the same hole.** A0 and A8 carry no feedback or rework row.
Revision 3 adds a second A0 item — EF-27's safeguarding fields are now specified and still land
there. Nothing in Emily's feedback touches A8. **Revision 4 adds no A0 item:** EF-47 lands on A4's
4.5, which has a reserve.

**3. Four change-order candidates, and two of them are one decision.** EF-02 (remove region) and
EF-40 (add county) must be priced and sequenced together: county was excluded on the express grounds
that region served the purpose, and removing region is what creates the need. Splitting them across
releases leaves the trustee list with no location column at all.

**4. EF-43 is now settled enough to price, which revision 3 said it was not.** The example has
arrived. The group row's fields are fixed, the group total is derived rather than stored, and the
group pack's omission of *Current Circumstances* in 12 of 12 removes the score breakdown from the
group detail page. **Only the interaction model is open** — expandable rows or a separate page — so
the design step revision 3 asked for is now short and bounded rather than open-ended.

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

**10. Revision 4's own lesson, and it is about method rather than scope.** This plan asserted that
the live form does not suppress the income questions on a benefits Yes, on the authority of
`docs/Import/2026-09-11-live-application-form-capture.md`. **A static capture of an unanswered form
records markup, not behaviour** — every question is present whether or not a conditional would later
hide it — and 63 real submissions contradicted the assertion without a single exception. The same
caution applies to anything else that capture established by *absence* rather than by *presence*:
**EF-35's missing carer age-confirmation is the next claim resting on the same footing** and is worth
re-checking the same way. **Live output beats a form capture; a form capture beats an inference.**

**11. Three of revision 4's findings came from nobody's request**, and all three came from reading a
delivered document against source rather than against the feedback: the region-derivation defect
(EF-49), the exceptional-funding reason gap (EF-48), and the group-linkage code inconsistency
(EF-42). **Reconciling a client's own reference data against ours is cheap, and here it found a
live wrong answer in a shipped deliverable.** Worth repeating on the next reference file that
arrives, rather than loading it and moving on.

**EF-48 then got the strongest confirmation available**, and it is worth recording how: Emily's
review-checkbox list — written the same evening, without sight of this plan — names *Exceptional
Circumstance* as one of her eight recurring difficulties. **Two independent routes to the same
gap, one from the data and one from the person doing the work.** Where that happens, the finding
does not need putting to the client as a question; it needs building.

**12. Revision 4's first draft got a dependency wrong, and the mechanism is worth more than the
item.** It recorded EF-21 as the one promised artefact still outstanding, and attributed the income
bands to a spreadsheet sheet. Both lists were written out in the body of the same message that
carried the attachments. **Three files were committed to `docs/Import/` and triaged; the mail that
delivered them was not read** — and until this revision it existed nowhere in the repository, so
nothing could have caught the omission. It is now
`docs/Import/2026-09-16-emily-sheardown-artefact-delivery.md` and registered in the manifest
(`IMP-0739`). **A client's covering message is a source document. Intake it with its attachments,
not instead of them.**

**13. DEV and Acceptance hold demo data, stated by the reviewer 2026-09-17 — so no question about
real applications can be answered by looking at an environment.** Recorded here because it closes
the route a later reader would reach for first.

**Nothing in revision 4 rests on environment records, and that is worth stating rather than leaving
to be re-derived.** Every finding comes from one of three places: the delivered trustee packs
(§2f–§2k — the score distributions, the benefits suppression, the exceptional-funding arithmetic,
the label conflict), the client's own postcode file (§2h), or **seeded configuration** — which is
`PostcodeRegionMap` and the scoring settings in `provisioning/deploymentSettings/`, config that
ships rather than data that accumulates, so EF-49's region defect is unaffected.

Two consequences:

- **EF-48's open question cannot be closed from an environment.** Whether the exceptional-funding
  reason is captured at intake has to come from the raw export or the live form.
- **EF-46 is the one at real risk, because the temptation is strongest there.** Emily is reviewing
  the scoring settings page in an environment; the settings she sees are the real seeded values, but
  **every application they act on there is demo**. Judging a threshold by how many applications it
  catches on screen would be judging it against invented data. **That is precisely why §2j puts the
  Round 4 and Round 5 distributions in front of her** — the packs are the only real corpus either
  side has.

**And the same fact cuts the other way, which is the part worth acting on.** An empty system is not
only a limitation on evidence — it is **a window for the changes that are cheap now and expensive
later**, and it closes the first time a real application is scored:

- **Trim `rev_incomeband`'s option set** with EF-29's re-seed. `M-07`'s own rule is that trimming is
  safe before any application exists and unsafe after, because renumbering changes what historic
  records mean (§2h).
- **Build EF-44's scoring audit column before real scoring starts**, not after. Its whole purpose is
  to keep an application explicable once the thresholds that scored it have moved; adding it to a
  populated system means every earlier application is permanently without one.

**Both get harder on the same day. Sequence them ahead of go-live rather than treating each as its
own item's problem.**

---

## 7. Recommended sequence

*Revised at revision 4. Steps 1, 2 and 7 change; a new step 0 goes in front of everything.*

0. **Fix EF-49 this week, and tell Emily.** Five postcode areas derive the wrong region today and
   `BB` derives a confidently wrong one — Blackburn shows as West Midlands. It is five prefixes in
   `PostcodeRegionMap`, it is independent of EF-41's change order, and it is currently wrong on a
   surface the trustees read. **This is the only item in the plan that is a live wrong answer rather
   than a missing or awkward one.**

1. **Send the fifteen answers in §5a, the four questions beneath them, and the three statements
   after those.** Fifteen of forty-nine items close at no build cost, and three (EF-06, EF-20,
   EF-26) are things Emily is currently waiting on. **Three of revision 3's questions are gone** —
   EF-12's *"which questions"* and EF-41's provenance, answered by the delivered documents, and
   EF-25, which is now a recommendation rather than a choice. **EF-48 is the only wholly new one.**

2. **Settle EF-46 next, because it is free and everything downstream inherits it — and now show her
   the numbers.** The borderline band, the knockout threshold and the income ceiling are seeded
   PROVISIONAL against OQ-001/002/003. **Put §2j's distribution in front of her before she confirms
   anything:** at a threshold of 20, Round 4 filters one application in 63 and auto-passes 51. Fix
   EF-29's four income bands in the same pass — the band list has arrived and agrees with the form
   capture. Re-seed all three environment files together, and check `IncomeCeiling`'s use against
   the fact that 90% of Round 4 has no income band at all.

3. **Build EF-44 before EF-07, EF-23 and EF-24.** Splitting the score breakdown from the scoring
   audit trail has to happen before anything else rewrites that column — and before the thresholds
   settled in step 2 make previously scored applications unexplainable.

4. **Secure `rev_locationarea`, `rev_helperorganisation` and `rev_helperrelationship`** (EF-02,
   EF-10), and drop the location column and the region filter from the portal together. **Δ4
   Confirmed 2026-09-17: trustees see no location at all**, so this is a live disclosure to fix
   rather than a design question, and — unlike revision 4's reading — **it no longer waits on
   EF-40.** County lands in the same column for the grant admin, a different audience on a different
   surface, so the two can run independently.

5. **Close 2.6 against the walkthrough**, which unblocks 2.7, then run the A2 items as one pass:
   EF-16, EF-22, EF-23, EF-24, EF-25, EF-31, EF-34, EF-45. **EF-29 is no longer held** — the band
   list arrived — and **EF-31's A2 half is no longer held either**: "build both" is settled, so the
   `>£500 and no exceptional funding` flag over the existing corpus runs now. Only the £100 day-trip
   variant waits on Emily, and only the form block waits on Alex. Build EF-25 as *Threshold score*.

6. **Run the A4 form pass as one piece of work, and start it with EF-47.** EF-01, EF-17, EF-18,
   EF-21, EF-27, EF-28, EF-33, EF-36, EF-37, EF-38, EF-39, EF-42 and EF-47 all touch the same form.
   **Sequence EF-47 first within the pass** — the Casework tab is where EF-21's checkboxes, EF-27's
   safeguarding action, EF-44's audit column and EF-45's reason all land, and it makes EF-22's
   three-way split cheaper by moving the scoring outputs out of the way. Building it last means
   placing four sets of fields twice. **Nothing in this pass is waiting on Emily any more** — EF-21's
   eight checkboxes arrived on 16 September.

7. **Take the four change-order candidates to `commercial-agent`** — EF-40 and EF-02 as one
   decision, EF-41, EF-43, and EF-12's second half. **Revision 4 changes two of them:** EF-43 now
   has its example and needs only a short design step, and **EF-41 must be split** so the region
   defect it repairs is not priced as new capability.

8. **Ask Alex for four upstream changes, now that the list is settled.** EF-28b is off it — the
   suppression is already built. **EF-31's >£500 block**, **EF-35's carer age-confirmation**,
   **EF-09's structured break dates** (V-04, still real — field 75 is one free-text box) and, added
   with it, **validation that the end date follows the start**: Group 101 is published running
   fourteen months backwards. **EF-35 rests on the same form capture that EF-28b discredited**, so
   confirm it against the live form before raising it, not after.
