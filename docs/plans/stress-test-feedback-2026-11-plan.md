# Stress-Test Feedback, Part 1 — Triage Plan

**Feature slug:** `stress-test-feedback-2026-11` (triage of `revitalise-grant-automation`)
**Produced by:** plan-agent, 2026-11-13, strategic tier (regulated data; more than three new open
questions), dispatched by lead-agent.
**Status:** APPROVED 2026-11-13 by Xander Lykopoulos, with changes (*"Approved with these
changes."*), relayed by lead-agent. Revision 2 applies those changes. Revision 1 classified the
all-time statistics as a change-order candidate and placed four rows on Automation 0 with no
reserve; the reviewer put all of them under feedback hours in the current WBS.

<!-- id-allocation: none -->

> **Source:** `docs/Import/2026-11-13-stress-test-feedback-part-1.md`: the reviewer's notes from the
> stress-test call with Emily (process owner and finance), checked against the transcript. 7 note rows
> and 13 "missing" rows. **More feedback will follow**, so this plan covers part 1 only.
>
> **Requirement text lives in the SDD, not here.** Amendment A-15 (APPROVED 2026-11-13) in
> `docs/plans/revitalise-grant-automation-plan.md` holds FR-120 to FR-126 in §4 and OQ-064 to OQ-068 in
> §9, and restates NFR-021. This document cites those ids and declares none of its own.
>
> **No hours and no money here** (`C-COM-004`, `C-COM-008`). Hours for the V2 rows are
> `commercial-agent`'s estimate.

---

## 1. Summary

The 20 rows become 22 here, because two carry a second, separate request (ST-05b, ST-12b). After
approval: **13 rows go to item intake under the current WBS's feedback hours (ST-13 and ST-15 were withdrawn by the reviewer), 3 go to a V2 estimate,
1 is parked (payments). The three questions meant for Emily were answered by the reviewer the same day, so none remains.** Some rows are client actions with no
build work; they are listed so they are not lost.

Two consequences reach beyond the rows:

1. **The real count is about 1,500 applications, not 730** (reviewer, at approval: 730 was an
   estimate). That is about 2,000 a year, so NFR-021 is restated with a 15,000-record ceiling, and
   architect-agent re-checks AI Builder credits (about twice the current estimate), the scrub review
   cards and the capacity check (A-15 Finding 7).
2. **All-time statistics come from the anonymised statistics table, which now records every
   application** (reviewer, OQ-066; design-document gate D4 (a)). Each application gets a Received
   record when it arrives, and an outcome record if the panel decides it. The Received record
   carries all five demographic and special-category fields, by the reviewer's ruling. Only the
   high-hours-care figure stays unavailable for all time.

---

## 2. How each row is classified

| Class | Meaning | What happens next |
|---|---|---|
| **(a)** change | The product must behave differently; SDD text changed | A-15 → architect-agent |
| **(b)** defect | Built behaviour falls short of an existing requirement or design | Fix under feedback hours |
| **(c)** documentation | Casework handbook content | Written, no build |
| **(d)** open question | Needs Emily's answer; a default applies until then | §5 |
| **(e)** client action or no build work | Someone does something; nothing is built | Tracked, not designed |
| **(f)** V2 or parked | Deliberately not now | V2 estimate, or parked |

**Reviewer's scope ruling at approval:** every class (a), (b) and (c) row is **feedback hours under the
current WBS**, including the all-time statistics, Total Cost, the Admin role and the handbook. None
needs a change order. The task each one is attributed to is `commercial-agent`'s; the column below
gives the nearest feedback task as a suggestion.

**The portal fixes start now** (reviewer decision 3), as rework under 6.8, without waiting for the
trustee walkthrough (6.7) that the dependency graph puts first. `pm-agent` records the early start.

---

## 3. The rows

**Size key** (relative, for triage only): **S** one surface; **M** several surfaces or one plus a rule
change; **L** new capability.

### 3.1 The reviewer's notes (7)

| Id | Row | Class | Ground truth | Resolution | Hours from | Size |
|---|---|---|---|---|---|---|
| **ST-01** | Care Support N/A | **(a)** | The web form shows the person-supported and type-of-care questions only to carers, and the care-support description only after a Yes. The Support Needs tab shows those fields empty. FR-084 forbids storing a default. | **FR-120**: show *Not asked* beside the empty field, store nothing | Feedback hours; suggested 4.5 | S |
| **ST-02** | Finance N/A when benefits = Yes | **(a)** | **Reviewer, at approval:** the web form skips *currently working*, household income, significant care costs and savings for benefit recipients. FR-103 already treats a blank savings answer as no rejection. | **FR-120** lists all four. OQ-064 answered | Feedback hours; suggested 4.5 | S |
| **ST-03** | Total Cost not editable | **(b)** + **(d)** | `rev_costs` is a plain money column described as the sum of the three cost lines, written once at intake and locked on the form while the lines stay editable. | **FR-121** (always the sum of its lines; OQ-068 answered) | Feedback hours | S |
| **ST-04** | Security role on Review table | **(b)** | `REV Admin` grants **Read only** on `rev_review`; the architecture document's role table gives the Admin role full create, read, update and delete on Review. Emily creates reviews by hand. | Fix the role. **FR-127** (TAD rev 39 D3, reviewer: *"yes, REV-admin role can create a review and add trustees. but not change their verdict and their notes. Other fields the process owner can edit"*): she creates and deletes reviews, names trustees and edits the other fields, but cannot change either verdict, either note or *Finalised On* (reviewer, same day: *"Emily can't edit finalised on. That is set by the finalise decisions workflow. it has a padlock. She is allowed to delete reviews."*) | Feedback hours | S |
| **ST-05** | DocuSign trigger → manual | **(a)** | The built envelope flow starts when *Finalise decisions* creates a grant row, before the referee details are filled in. | **FR-122**: Emily starts the DocuSign workflow herself, from the flow menu on one open grant **or** by selecting several grants together and sending them in one action (reviewer, 2026-11-13: *or selecting multiple grants at the same time and sending it to the docusign workflow.*). Each grant is checked on its own: no referee name or email, or already has an envelope, means skipped and reported, and the rest still send. FR-041 and FR-047 amended | Feedback hours; suggested 3.5 | M |
| **ST-05b** | Referee request email from *Finalise decisions* | **(f) V2** | New capability; no WBS task sends a referee request. | **V2 — estimate via commercial-agent** | V2 | M |
| **ST-06** | Casework handbook | **(c)** | `docs/training/casework-handbook.html` has no section on groups or on where settings live. | **Full revision of the handbook** against the solution as it stands in the repository, including the three sections: **creating a group** (the group reference, and that a typo splits a group); **where the scoring and narrative scrubbing settings are** (Settings, by the Category column); **creating a review**. Reviewer, 2026-11-13 (WI-0160): *"update the book in total based on what's on disc including the items listed in the table."* | Feedback hours | S |
| **ST-07** | Views on Review table | **(e)** | Emily's own action: one view per workflow stage. | She builds them as personal views | none | — |

### 3.2 Missing from the notes (13)

| Id | Row | Class | Ground truth | Resolution | Hours from | Size |
|---|---|---|---|---|---|---|
| **ST-08** | Portal visibility (item 1) | **(a)** + **(d)** | The trustee list filters on *Eligible for Round* = Yes only. No review is needed. | **FR-124** rewritten by TAD rev 39 D1 (reviewer: *"An open review in combination with the round field match, this closes when a review is closed with outcome: approved."*): listed when released, with an open review whose Round matches the open round, until that review is closed as Approved. **OQ-069 answered the same day:** open means *Finalised On* empty; once *Finalise Decisions* sets it, the application leaves the list whatever the outcome; with no round or two rounds open the list is empty and a warning is sent to REV Admin role holders | Rework, 6.8, **starts now** | S |
| **ST-09** | Admin sees the verdict button (item 2) | **(b)** | The verdict button is drawn on every row for every user. | **FR-125**; FR-116 amended. Low priority | Rework, 6.8, **starts now** | S |
| **ST-10** | Safeguard against releasing the wrong application (item 3) | **(a)** | Nothing stops *Eligible for Round* being set at any status. | **FR-123**: refuse the release unless the status is *Eligible for Panel* | Rework, 6.8, **starts now** | S |
| **ST-11** | Statistics scope: all time (item 4) | **(a)** + **(d)** | Every statistic is per round (FR-057). Retention deletes the live records, so all-time figures come from the anonymised statistics, which hold panel outcomes only (A-15 Finding 6). | **FR-126** as rewritten by TAD rev 39 D4 (a) (*"Go for option a"*): a Received record for every application at intake plus an outcome record per decision; All time read from those records alone, carrying all five demographic and special-category fields by the reviewer's ruling. FR-080 reads the Received records (D2). Hiding small groups on All time charts was REJECTED by the reviewer; whether that also lifts the five-application money rule is OQ-070. Trustees never read the anonymised table; the statistics flow publishes the figures | Feedback hours; suggested 6.8 | M |
| **ST-12** | Historical count (item 5) | **(e)** | **Answered at approval:** about 1,500 applications; 730 was the reviewer's estimate. OQ-067 answered; NFR-021 restated. | Seed the earlier-applications count (FR-082) as 1,500 minus what the system holds from its tracking start date, through the settings files, never by hand | `wbs:6.10` seed step | — |
| **ST-12b** | Historical demographics import | **(f) V2** | No task imports history; old special-category data would need its own classification and lawful basis. | **V2 — estimate via commercial-agent** | V2 | L |
| **ST-13** | Start date format (item 6) | **withdrawn** | — | **Withdrawn.** Reviewer, 2026-11-13 (WI-0164): *"can be dropped. this was my input error during the meeting."* | — | — |
| **ST-14** | Automating review creation (item 7) | **(f) V2** | Needs a table that stores the trustee rotation. | **V2 — estimate via commercial-agent** | V2 | L |
| **ST-15** | Narrative scrubbing tuning (item 8) | **(b)** + **(e)** | *"Friend"* is not on the client's Anonymisation Key, so changing it to *"person"* goes beyond FR-094; *they're*/*their* fall under FR-098. | **Withdrawn for now**, pending more testing by Emily. Reviewer, 2026-11-13 (WI-0165): *"can be dropped. Emily needs to test more with narrative scrubbing."* Cases she finds later come back as new feedback | — | — |
| **ST-16** | Test with realistic data (item 9) | **(e)** | **Reviewer decision at approval:** the realistic data is anonymised and deleted afterwards. | Emily sends anonymised, realistic applications through the web form; they are deleted afterwards (the erasure helper, mode 2, can do it and is tested by doing so) | 4.5 | — |
| **ST-17** | SAR workflows built, not yet tested (item 10) | **(e)** | Mode 3 is built under `CO-011`; the procedure is in `docs/training/subject-access-request-procedure.md`. | No build. Test owed: our run in DEV, then Emily's in ACC; can use ST-16's records | `CO-011` | — |
| **ST-18** | Payments (item 11) | **(f)** parked | Parked by the client. | Nothing planned | — | — |
| **ST-19** | Emily's step-by-step document (item 12) | **(e)** | Emily updates and sends it. | Check it against the handbook (ST-06) when it arrives | none | — |
| **ST-20** | Follow-up Wed 18 Nov, 16:00 CET / 15:00 UK (item 13) | **(e)** | Plus chat updates on the fixes. | Send §5's three questions before the call | none | — |

**ST-13 withdrawn (2026-11-13):** the reviewer confirmed the 15/12 versus 12/15 observation was his own
input error during the meeting, not a product behaviour. The earlier suspicion (a US date format
setting) is withdrawn with it.

---

## 4. Rows for item intake, the V2 estimate, and Emily

| List | Rows |
|---|---|
| **(i) Item intake, feedback hours under the current WBS** | ST-01 + ST-02 (one item, FR-120) · ST-03 (FR-121) · ST-04 (Admin role) · ST-05 (FR-122, with FR-041/FR-047) · ST-06 (handbook) · ST-08 + ST-10 (one item, FR-123/FR-124; starts now) · ST-09 (FR-125; starts now) · ST-11 (FR-126) · ST-12 (FR-082 seed) · ST-16 (anonymised test data) · ST-17 (SAR test) |
| **(ii) V2 estimate, via commercial-agent** | ST-05b referee request email · ST-12b historical demographics import · ST-14 automated review creation |
| **(iii) Open questions for Emily** | None. OQ-065 (*"Yes"*), OQ-066 (answered by the reviewer, source changed) and OQ-068 (*"No, its always the sum of its cost lines."*) were answered 2026-11-13 |

**One note for `pm-agent`:** task 3.7 tests *"approve 5 applications at once, verify all envelopes
created correctly"*. Under FR-122 as corrected, it tests Emily selecting five approved grants and
sending them to the workflow in one action, including one grant without referee details: four
envelopes are created with the correct data, the fifth is skipped and reported, and running it again
sends no duplicates. (The earlier note, that the test becomes five single sends, is withdrawn.)

---

## 5. Questions for Emily

**None remain.** The reviewer answered all three on 2026-11-13: trustees see an application only once
it has a review (OQ-065); the all-time figures come from an anonymised record kept for every
application, which is the reviewer's decision, not Emily's (OQ-066); Total Cost is always the sum of
its lines (OQ-068).

**Her actions, not questions:** the step-by-step document (ST-19); more testing of narrative
scrubbing (ST-15, withdrawn until then); review-table views (ST-07); and the anonymised realistic
test applications (ST-16).

**For the reviewer, not for Emily:** OQ-070, whether rejecting small-group hiding also lifts the
five-application rule on money averages. OQ-069 and the Finding 8 field decision are settled.

---

## 6. For architect-agent, `pm-agent` and `commercial-agent`

- **architect-agent:** FR-121's recalculation against the intake's single write. FR-122's trigger
  (a flow the process owner runs on the open grant) replaces the grant-created trigger. FR-124
  changes the list query. FR-126 as amended: one anonymised record per application, written at the
  panel decision or else at deletion or erasure; counting each application once without linking the
  record back to it; and the retention and erasure runs, which today write a record only for a
  deferred application. NFR-021's
  re-check at about 2,000 a year: AI Builder credits, scrub review cards, flow actions, capacity
  against 15,000. And the architecture document says trustee visibility needs both *Eligible for
  Round* and narrative release, while the list applies only the first; correct the wording when
  FR-124 is designed.
- **pm-agent:** item intake from §4 (i); record the early start of the 6.8 rows; the 3.7 knock-on.
- **commercial-agent:** attribute §4 (i) to feedback tasks; produce the V2 estimate for §4 (ii).
- **Not changed by this plan:** retention (§7.6), the no-auto-release rule for scrubbed narratives
  (A-11), the DocuSign template and signing order, and the paused register work.

---

## 7. Recommended order

1. Nothing to send Emily; the reviewer's Finding 8 decision gates part of ST-11 only.
2. ST-04 (role): small, and it unblocks her daily work.
3. ST-05 (send from one grant or several, with the per-grant checks) and ST-08/ST-10 (the release safeguard).
4. ST-01/02, ST-03 and ST-09.
5. ST-11 (the five Finding 8 fields wait for the reviewer's decision); ST-06 full handbook revision, checked against Emily's document when it arrives.
