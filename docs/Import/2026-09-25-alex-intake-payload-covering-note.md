# Website developer's covering note for the intake payload sample — 25 September 2026

**From:** Alex, the website developer (Revitalise's WordPress site)
**Accompanies:** `docs/Import/2026-09-25-website-intake-payload-sample.json`
**Received:** 2026-09-25. The reviewer (Xander Lykopoulos) pasted it into the delivery session.
Transcribed verbatim below. **No internet message id is available.** The text came as a paste,
not as a mail file, so this transcription is the only copy in the repository (`IMP-0739`: a covering
message is a source document in its own right).

It records what the sender says about the payload. It authorises nothing (`C-COM-002`).

---

> A few things to note:
> Keys are readable names instead of Gravity Forms field IDs. For example, 3.3 is now name_first and 5 is now email. The entry details keep their usual names (id, form_id, date_created, ip and so on). date_created is in UTC.
> Checkboxes send a list of the options that were ticked, such as ["Google search", "Friend or family member"], or [] if none were.
> Consent boxes send true or false.
> Survey questions send the answer text, such as "Often", instead of internal codes.
> Numbers and amounts are still sent as strings, such as "345".
> Layout-only items such as page breaks and section headings are no longer sent.
> Some keys are long for now because they're taken from the question text.
>
> A couple of questions:
> Questions the applicant never saw (conditional questions that were not relevant) are currently sent as empty values ("", [] or false). Would you rather we leave those keys out, or send them as null?

---

## What this settles, and what it does not (architect-agent, TAD rev 10)

| Statement | Effect on the design |
|---|---|
| Keys are readable names derived by the sender, and *"some keys are long for now"* | The key names are **expected to change**. `ADR-051` item 2 keeps them in one action only. Risk A-R62 changes from *possible* to *announced* |
| `date_created` is UTC | Settles the time-zone question. It is **still not used**, because it is form-generated (reviewer rule, rev 10), and FR-008 uses the flow's receipt time |
| Checkboxes send ticked labels, or `[]` | E2 from the sender for every multi-select, including the routes the sample left empty. It does **not** settle the label strings themselves (`A-INT-06` stays open) |
| Consent boxes send `true`/`false` | Matches the sample. A `false` on an unseen consent is treated as *not answered* (Appendix C §C.2) |
| Survey questions send answer text | Matches the sample. Settles the value shape for all eleven scored answers |
| Numbers are strings | Matches the sample |
| Unseen questions are sent as `""`, `[]` or `false` today, and may be omitted or sent as null instead | **Open by the sender's own question.** The design is built so the answer does not matter (`ADR-051` item 11, §C.2): absent, null, `""`, `[]` and false-on-an-unseen-question are all *not answered, nothing written* |
