# DocuSign envelope feedback, reviewer turn 2026-10-02

**Class:** requirements. **Intaked by:** `pm-agent` (ledger intake only; design sits with `architect-agent`).

**Provenance.** The reviewer's turn of 2026-10-02 plus DocuSign feedback from Emily (Revitalise),
relayed in that turn and summarised here by lead-agent's handoff. This is NOT a verbatim
transcription of an email; the original message is not in the repository. Her contact details are
deliberately not recorded (personal data). **This file records what was asked. It is not an accepted
change to scope** (`C-COM-002`).

Target: wbs:3.2, workflow `REVAcceptanceCreateEnvelope`.

| Row | Ask |
|---|---|
| DS-01 | The Create Envelope flow fails: the single SendEnvelope action can no longer create, fill tabs and send. Reviewer asks to split it into create draft, then fill tabs, then send. |
| DS-02 | Applicant and referee tabs marked mandatory can be left empty and the envelope still completes. Emily reproduced this for both signers. |
| DS-03 | A referee invite can be forwarded and signed by anyone holding the link; the signer is recorded as the original referee. Needs recipient identity binding. Whether this fits wbs:3.2 or needs a change-order decision is pending architect-agent's research; not decided here. |
| DS-04 | The referee must not be able to reassign or change the signer. |
| DS-05 | Research and option: a different email message for signer 1 (applicant) and signer 2 (referee). |
