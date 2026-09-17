# Client artefact delivery — Emily Sheardown, 16 September 2026

**Class:** requirements (the artefacts promised at the walkthrough, plus two lists in the mail body)
**Intaked by:** `plan-agent` — the same note applies as on
`2026-09-07-08-emily-sheardown-review-feedback.md`: `skills/how-to-intake-external-documents.md`
carries only SDD-shaped and TAD-shaped checklists and this matches neither (`IMP-0028` /
`IMP-0384`, class `input-type-with-no-owning-agent`).

**Author:** Emily Sheardown, Interim Partnerships and Volunteer Fundraising Manager,
Revitalise Respite Holidays (`esheardown@revitalise.org.uk`).

**Transcribed:** 2026-09-17, verbatim from the Outlook message named below. Emily's wording,
ordering and emphasis are preserved. Editorial insertions by the transcriber are in
`[square brackets]`.

> **This file records what the Client sent. It is NOT an accepted change to scope.** Under
> `C-COM-002` work enters by WBS task id or by a change-order decision.

**Why this file exists at all, and it is the point of the whole record.** The three attachments
were committed to `docs/Import/` and triaged; **the message body was not read**, so two of the
lists Emily wrote out in it were missed — the income bands were attributed to a spreadsheet sheet
instead, and the review-checkbox list was recorded as still outstanding when it is set out in full
below (`IMP-0739`). **An email that carries attachments also carries a body.**

---

## Source — "Re: Meeting notes"

| | |
|---|---|
| **Received** | 2026-09-16 20:25:16 UTC |
| **From** | Emily Sheardown |
| **To** | Xander Lykopoulos |
| **In reply to** | Xander Lykopoulos, 2026-09-16 16:43, "Meeting notes" — the circulated walkthrough record |
| **Internet message id** | `<CWLP265MB5404095AC4778A3592A0ADC98AB92@CWLP265MB5404.GBRP265.PROD.OUTLOOK.COM>` |
| **Attachments** | `Postcode Details.xlsx`, `2. Group Applications - Round 5.pdf`, one inline PNG |

The Round 4 individual trustee pack was **not** attached to this message — it was sent separately
on the trustee-portal thread, as the walkthrough agreed, and is in `docs/Import/` as
`3. Round 4 - Individual Applications.pdf`.

### Body (verbatim)

> Fantastic - thanks Xander.
>
> As promised please find the following attached and below:
>
> - Group application Trustee pack (same password as individual)
> - Postcode data
> - Income bands:
>
> | Approximate household income (before tax) |
> |---|
> | Under £15,000 per year |
> | £15,000 - £25,000 |
> | Over £35,000 |
> | £25,000 - £35,000 |
>
> - Common difficulty areas to include as 'tickboxes':
>
>   Sorry, slightly more than 5 but let me know if these are too many!
>
> - Location
> - Date
> - Amount
> - Exceptional Circumstance
> - Disability Information
> - Care Information
> - Group
> - Age
>
> Thanks again - any questions, please let me know.
>
> Best regards,
>
> Emily

---

## What this source delivers

Four of the five dependencies the 16 September walkthrough recorded against Emily. The fifth — the
Round 4 trustee pack — arrived on the trustee-portal thread.

| Delivered | Where in this source | Plan item |
|---|---|---|
| The postcode export | attachment `Postcode Details.xlsx`, sheet *Postcodes* | EF-03, EF-40, EF-41 |
| The group application summary example | attachment `2. Group Applications - Round 5.pdf` | EF-43 |
| **The income band options** | **the body table above**, and duplicated on the attachment's *Income Values* sheet | EF-29 |
| **The review checkbox items** | **the body list above — eight, not five** | EF-21 |

### Two things to note about the body lists, because neither is a plain hand-over

**1. The income band table is given out of order.** Emily lists *Over £35,000* third and
*£25,000 - £35,000* fourth. The *Income Values* sheet on the attachment repeats the same four
values in the same wrong order, so the two agree exactly — including the ordering slip. The bands
themselves match `docs/Import/2026-09-11-live-application-form-capture.md`. **Treat the set as
authoritative and the sequence as a typo**; display order is ours to set.

**2. The checkbox list is eight items and Emily asks whether that is too many.** The walkthrough
recorded *"up to 5 checkboxes"*; she has sent eight and written *"Sorry, slightly more than 5 but
let me know if these are too many!"* — **an open question addressed to us, not a specification.**
It needs an answer before the fields are built.

Her eight are not all the same kind of check. Read against the walkthrough's own example
(*"Location check complete: Yes/No"*), six are **completeness checks on data the applicant
supplied** and two are **classification checks**:

| Emily's item | What it appears to check | The plan item it touches |
|---|---|---|
| Location | the applicant's location is present and usable | EF-03, EF-40, EF-41 |
| Date | break dates are present and sane | EF-09 |
| Amount | the amount requested is present and within the standard maximum | EF-31 |
| Exceptional Circumstance | an above-maximum request carries its reason | EF-48 |
| Disability Information | the condition/disability free text is sufficient | EF-37 |
| Care Information | the care-support description is sufficient | EF-37 |
| Group | the application is correctly linked to its group | EF-42, EF-43 |
| Age | both age confirmations are satisfied | EF-35, EF-36 |
