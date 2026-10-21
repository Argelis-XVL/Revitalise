# REVFinanceCapturePayment-8F1C2A44-1013-4B7A-9E21-0A1B2C3D4E13.json - reasoning behind the shipped descriptions

Power Automate caps every `description` at 256 characters; the shipped ones keep the essential
fact and this file holds the reasoning, keyed by action name. Design: TAD rev 28 section 5.11,
ADR-081. Change order CO-010 (`wbs:8.6`, unbilled). Requirements FR-107 to FR-112, US-026.

## What the flow does

On every Added or Modified `rev_payment` it **recomputes**, never reacts: it reads the saved payment
again, the grant, the latest dated final payment on the grant and the application, then makes four
things match the payments that exist, in a fixed order: the grant's `rev_finalpaymentdate` and
`rev_status` (one write), then the application's `rev_status`. **It writes nothing to `rev_payment`
(amendment c, reviewer "4", 2026-10-20).** A write happens only where the current value differs from the target, so a
repeat save, a save of another payment and a run replayed from history write nothing (FR-109).

**Reviewer addition 2026-10-20 (relayed by lead-agent; the TAD and SDD text for it was still being
written when this was built):** the grant itself moves Acceptance Signed (3) to Paid (4) in the same
write as the date, and back on reversal. Any other grant status is left alone and reported, in the
same way as the application. The exact wording is the architect's; see Dev Summary "open items".

## Decisions worth knowing

* **Target date** is the latest date among final, not Cancelled, **dated** payments (OQ-057, OQ-058,
  answer 3). An undated final payment is not a final: no clock, and it is reported.
* **Grant status target:** final exists and grant at 3 gives 4; none exists and grant at 4 gives 3;
  otherwise unchanged. **Application target:** Approved (7) to Grant Paid (11) and back, otherwise
  unchanged.
* **The payment's Issued mark is not this flow's** (amendment c). A table-scope business rule on
  `rev_payment` (WI-0136, authored in the DEV designer and exported) sets Pending to Issued when Final is
  Yes, and refuses a final payment with no date. The flow reads the payment again by id and its target
  depends on Final, date and not-Cancelled only, never on Issued, so it computes the same result whether
  it reads Pending or Issued. `rev_paymentstatus` stays in the trigger filter on purpose: cancelling or
  un-cancelling a payment must recompute the grant. Unticking Final leaves the status as it is (OQ-059).
  *Previously read: a Pending-guarded `Write_the_payment_issued` last in the run, one extra no-op run
  (`A-CP-8`); removed because `NoTriggerLoop` rejects it.*
* **No grant linked:** the three reads run with an all-zero id and return nothing, so the flow has no
  branch for it and every write stays guarded. Reported only if the payment is final and not Cancelled.
* **Reasons** (one `Compose_reasons`, in words, with what to do): no grant; date changed while the
  application is at neither Approved nor Grant Paid; date changed while the grant is at neither 3 nor 4;
  final and undated; final and Cancelled (information only). Never an amount, bank detail, date or name.
* **Sent last:** the Warning alert to the process owner (`REV | Ops | Failure Alert`), then the Teams
  message to `rev_FinanceAlertUpn`. A blank value makes the Teams post fail: the writes are already made,
  the run takes the failure path and the process owner is told; finance is not.
* **Date shapes:** both days pass through `formatDateTime(coalesce(x, '1900-01-01'), 'yyyy-MM-dd')`
  inside an `if(empty(...))`, so a timestamp and a day string compare equal and nothing throws on null.
  The expression is safe whether `if()` evaluates one branch or both.
* **Run history:** the reads of secured finance columns and the Composes that hold their values secure
  inputs (and outputs for the reads); the trigger secures outputs.

## Open assumptions (Dev Summary section 10, markers in the descriptions)

`A-CP-1` message 4 fires for Added and Modified. `A-CP-2` four secured columns in
`filteringattributes`. `A-CP-3` DateOnly read and written as a day string. `A-CP-4` concurrency 1 on a row
trigger (remove it if the platform refuses). `A-CP-5` `rev_paymentstatus ne 4` returns Pending.
`A-CP-6` a null write clears a DateOnly column. `A-CP-7` the flow owner's secured reads and its grant-date write. `A-CP-8` WITHDRAWN (the flow no longer
writes the payment). `A-CP-9` the table-scope payment rule: date required and the Issued mark (not yet
authored, WI-0136; this flow reports an undated final payment as a backstop).

## Restart route

FR-111 forbids a background retry and there is none. Finance corrects the cause and saves again: a save that
changes none of the four trigger columns starts nothing, so the message says untick Final payment, save, tick
it, save. Both saves are safe.
