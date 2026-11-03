# Subject access requests and erasure requests: the process owner's procedure

**For:** the process owner (today Emily, `REV Admin`).
**Covers:** a request to see personal data (a subject access request, UK GDPR Article 15), a request to erase it
(Article 17), and the weekly retention summary.
**System:** REV Grant Administration and the three helper flows `REV | Retention | Retention & Erasure Helper`
(SAR extract, erasure, sweep).
**Design source:** technical architecture, sections 4.2 and 5.12 (`ADR-088`, `ADR-089`, `ADR-091`); change order CO-011
(`wbs:0.13`). The Governance Runbook section 7 points here.

---

## 1. Before anything: what kind of request is it?

| The person asks to... | It is | Go to |
|---|---|---|
| see what we hold about them, or get a copy | a subject access request | section 2 |
| have their data deleted | an erasure request | section 3 |
| both | two requests, recorded separately | section 2 first, then section 3 |

**Always answer the access request first** when both are asked. The erasure deletes what the extract has to show.

Revitalise sets its own target for answering. Until it does, the legal limit applies: one month from receiving the
request, extendable by two more months for a complex request if you tell the person within the first month.

---

## 2. A subject access request

### Step 1. Write it in the register

The register is a spreadsheet in the SAR folder. Add one line: request number, the applicant reference
(`REV-A-nnnnn`), the date received, and "identity not yet confirmed". Never write the request's content there.

### Step 2. Confirm who is asking

The system cannot check who a person is. You do, before anything else, as agreed with the Data Protection Officer:
compare what the person tells you with what the application holds, through a channel you trust (for example a call
to the phone number on record). **Also confirm that the email address on record is theirs:** the extract is
delivered to it. Write the date identity was confirmed in the register.

If the person is a **referee, helper, group member or emergency contact** rather than an applicant, go to step 7.

### Step 3. Start the SAR extract

1. In REV Grant Administration, open **Applicants** and select the applicant (one row).
2. Open the **Flow** menu and choose **REV | Retention | Retention & Erasure Helper (SAR extract)**.
3. Confirm the run.

The flow runs as the service account. It reads everything it can reach, including payments and bank details you
cannot see in the app, and writes **one file** to the SAR folder, with a copy of each signed document beside it. It changes nothing in any record.

### Step 4. Wait for the Teams message

You receive a Teams message: **"Subject access request extract ready"**, with the applicant reference and the file
name. It never shows the content. It also lists any part of the system that could not be read; each such part is
marked **Not read** in the file, with the reason. If no message arrives and you get a failure alert instead, run
step 3 again.

A moment later the flow tries to email the file and the signed documents (step 5). If it could not, you receive a
second message: **"Subject access request extract NOT emailed: use option A"**, with the reason and the name of
every file to send.

### Step 5. Deliver the extract

**Option B: the flow emails it, encrypted.** In an environment where protected sending is switched on (the setting
**SAR Protected Sender** holds the dedicated SAR mailbox's address), the flow emails **one message** to the email
address on record, from that mailbox, with the file **and a copy of every signed grant acceptance document** attached.
Revitalise's mail system encrypts every message from that mailbox, so the person opens it after signing in or
entering a one-time passcode. Nobody reads the file before it leaves: the details of other
people in the person's own application go with it, a risk the reviewer accepted (`A-R108`). If you got no "NOT
emailed" message, the Retention Log row for this request says **delivery: option B**. Write the date sent in the
register.

**Option A: you deliver it by hand.** The flow never sends the file unencrypted, and never sends only some of the
files. If the setting is empty, the applicant has no email on record, the files are too large to email together, or
the send failed, the flow sends nothing and does not try again, and you get the "NOT emailed" message. Then:

1. Open the file once in the SAR folder. It holds one section per store: the applicant, applications, reviews,
   grants, payments, bank accounts, the audit history, QuickBooks, the grants mailbox, the signed documents (saved
   beside the file) and short statements about AI Builder, Teams and the website.
2. **Other people's data.** The file includes the referee, helper, group members and emergency contact named in the
   person's own application, and the referee's statement. Remove what would adversely affect those people
   (Article 15(4)); the trustees' identities are already removed.
3. Send the file and the signed documents password-protected or by an encrypted route to the email address on
   record. Send the password by a separate channel (for example by phone).
4. Write the date sent in the register.

**When the setting is filled.** It is empty in every environment when the system is installed, so option A is where
everything starts. It is filled in an environment only after a test there has shown that a message from the SAR
mailbox arrives encrypted with every attachment opening, that nothing is sent when the setting is empty or the files
are over the limit, and where a copy of the sent message is
kept (`A-SAR-4`, `A-SAR-13`, `A-SAR-14`, `A-SAR-15`; `ADR-091`). Do not fill it yourself.

**Signed documents under option B.** The email carries the extract file and every signed-document copy the run saved
in the SAR folder, all in one message. Nothing more to send. *Previously read: "The email carries the extract file
only … until then, send them by the option A route."*

**When the files are too large to email.** Before sending, the flow adds up the size of the extract and the signed
documents and compares the total with the setting **SAR email attachment limit (MB)** (Settings, category *Data
retention and erasure*; 15 when installed). If the total is larger, or the setting is empty or not a whole number, or
a file's size could not be read, **nothing is emailed** and the "NOT emailed" message says the files are too large or
could not be checked, with the total. Deliver every file it names by option A. The Retention Log row records the
same, for example *"delivery: option A, not emailed, too large: 16.1 MB of files against a limit of 15 MB"*. Raise the
limit only after a test has shown that larger encrypted messages arrive; Revitalise's mail system accepts encrypted
messages up to about 25 MB, and attachments grow by about a third when sent.

**The encryption rule.** Revitalise's tenant administrator keeps a mail rule named *REV SAR extract — encrypt, do not
disable*. If it is ever switched off or changed, the flow cannot tell, and the next extract would leave unencrypted
(`A-R112`). Anyone changing mail rules must know this.

### Step 6. Delete the working copy and close the register

Once delivery is confirmed, delete the file and the signed-document copies from the SAR folder. Close the register
line: date sent, and whether an extension was used.

### Step 7. The cases the flow does not cover

| Situation | What to do |
|---|---|
| The requester is a referee, helper, group member or emergency contact | Find the applications by their name and email (Advanced find on Applications). Copy only the columns about the requester. Rare. |
| The QuickBooks copy itself is asked for (section 8 of the file says it was not read) | Ask Finance to export that payee's transactions from QuickBooks (until the QuickBooks connection exists, `wbs:7.1`). |
| Section 7 (audit history) says **Not read** | Ask the tenant administrator to export the audit history of the applicant's records. |
| Section 9 (grants mailbox) says **Not read** | Search the grants mailbox by hand for messages to or from the applicant's and the referee's addresses. |
| The person asks for the AI Builder copy of their text (live system only, kept at most 30 days) | Ask the tenant administrator to export it. Rare. |
| The website entry | The website keeps the entry the person submitted (its id is in the file). Tell the person it exists; Revitalise handles the website copy separately. |

---

## 3. An erasure request

### Step 1. Check before you start

- **Identity**, exactly as in section 2 step 2.
- **It really is an erasure request**, and whether an access request was also made (then section 2 first).
- **Your judgement on holds the flow cannot see.** If there is a legal claim, a dispute or
  any other reason you judge the records must be kept, do not run the erasure: record the reason and talk to the DPO. The flow
  checks one thing only, below. (The design leaves every other hold, such as a legal claim or a dispute, to you,
  `ADR-089` item 6.)

### Step 2. Start the erasure

1. In REV Grant Administration, open **Applicants** and select the applicant (one row only).
2. Open the **Flow** menu and choose **REV | Retention | Retention & Erasure Helper (erasure)**.
3. In the box, **type the applicant reference exactly** (for example `REV-A-00042`), then run it.

A wrong or missing reference, or more than one applicant selected, stops the run with nothing read or changed.

### Step 3. What happens next

**If a grant has no final payment recorded,** the run stops and erases nothing. The requester receives this email
from the grants mailbox, and you receive a Teams message naming the grant:

> Thank you for your request to erase the personal data Revitalise holds about you. We cannot erase it yet, because
> a grant we awarded you has not been fully paid. Once the final payment has been made and recorded, we will erase
> your data and write to you to confirm what was erased and what we must keep, why, and until when.

Run the erasure again after the final payment is recorded.

**Otherwise,** the flow records each record it is about to delete, deletes the signed acceptance documents and the
grants-mailbox messages, then deletes the applicant: the applications, reviews, grants, payments and bank accounts
go with it. It writes an anonymous Not Granted statistic first where a deferred application was never decided. The
requester then receives an email listing the application references erased and what is kept:

- the payment record in QuickBooks, until six years after the final payment, because charities must keep financial
  records; **Finance deletes it after that date** (the system cannot);
- the audit history of the changes, access-restricted, until six years after each change;
- a DocuSign envelope signed in the last 30 days, until DocuSign's retention setting deletes it;
- any AI Builder copy of their text, deleted automatically within 30 days;
- the website entry, which Revitalise handles separately.

The DPO's mailbox receives the references only, and you receive a Teams message.

### Step 4. After the run

- **DocuSign envelopes:** if the Teams message names grants with an envelope still in progress, void those envelopes
  by hand in DocuSign.
- **"The requester could NOT be emailed":** tell them by hand, using the wording above.
- **"The DPO was NOT emailed":** set the DPO's mailbox in **Settings**, category **Data retention and erasure**,
  key **Erasure notification email** (it reads "not set" until you do), then tell the DPO by hand.
- **A failure alert ("the erasure did not finish"):** run the erasure again. Anything already deleted is skipped.

Every step is recorded in the **Retention Log** (REV Grant Administration, Operations): what was deleted, when,
under which rule, and who started it. It holds references only, never the person's details.

---

## 4. The weekly retention summary

Every Monday you receive a Teams message from the retention sweep:

| It says | What to do |
|---|---|
| Coming due and logged | Nothing. These applications reach the end of their retention period before the next deletion job runs. |
| Deleted by the retention jobs and recorded | Nothing. Their signed documents have also been removed. |
| **Overdue**, with references | The deletion job has not deleted these 35 days after their date. Ask the tenant administrator to check the bulk-delete jobs. |
| **Stale open cases**, with references (first Monday of the month) | These applications are still open but the applicant has not been in touch for the set number of months (12 by default, setting **Stale open case months**). Close each as Withdrawn or Rejected if that is right, which starts its retention clock. The sweep never changes a status itself. |
| Stale open cases "not listed, because the setting is missing" | Check the **Stale open case months** setting holds a whole number. |
