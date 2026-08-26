# Risk Acceptance Record — Secure Outputs on two shipped flows

**Date:** 2026-08-25
**Recorded by:** improvement-agent, on the reviewer's decision
**Accepted by:** Xander Lykopoulos
**Finding disposed of:** the critical finding at [logs/improvement-log.jsonl#L317](logs/improvement-log.jsonl#L317)
**Exception opened:** [EX-004](contract/known-exceptions.json#L41)

This is **not** an improvement review. No clustering pass was run, no rule in `constraints/`,
`skills/`, `knowledge/` or `agents/` was touched, and nothing here needed `APPROVE IMPROVEMENTS`.
It records one reviewer risk-acceptance and the exception that now carries it. The file is
deliberately not named `*improvement-review*.md`, because it does not process a queue.

---

## Summary

Two already-shipped flows read personal-data rows without Secure Outputs, so those rows are
recorded in flow run history outside Dataverse's own column security. The reviewer accepted the
risk on the grounds that only the service account runs these flows and only they have access to
it, and that acceptance is now recorded against the finding and carried by a dated exception
expiring 2026-10-16.

One thing the reviewer has not yet seen: the gate the finding says would detect this **does not
exist on disk**, so the exception's expiry is currently the only control, and the queue still
blocks the two held builds.

---

## What was applied

1. **The reviewer's decision is recorded on the finding, dated and attributed, with their exact
   words** — [logs/improvement-log.jsonl#L317](logs/improvement-log.jsonl#L317).

   The entry now carries a `deferred_reason` and a `revisit_when`, which moves it from "nobody has
   looked at this" to "a person decided this". Their words are quoted verbatim inside it, with the
   reasoning stated: the sole identity running both flows is the provisioning service account, the
   sole person with access to that identity is the reviewer, so the population able to read the
   exposed run history is one person already entitled to the data.

2. **The gap is now an owned, dated exception** — [EX-004](contract/known-exceptions.json#L41).

   This is option (b) of what the finding itself proposed, which is what the reviewer chose. It
   carries an owner, a reason, a clearing action and an expiry, so it passes the validation that
   [C-COM-010](constraints/commercial/commercial-constraints.md#L53) requires, and
   [scripts/verify-wbs-chain.py](scripts/verify-wbs-chain.py#L202) now reports four accepted
   exceptions instead of three, with zero violations.

3. **The new check was deliberately not wired into the build as HARD** —
   [config/revitalise-grant-automation-build.yml](config/revitalise-grant-automation-build.yml) is
   untouched.

   This is the other half of option (b). Turning it on would fail every build over two flows that
   the trustee-portal work never touched, which is scope nobody has sized.

4. **What the re-verification found is logged** —
   [logs/improvement-log.jsonl#L319](logs/improvement-log.jsonl#L319).

   A new finding records that the gate does not exist and that the exposed surface is wider than
   the original finding states. It carries `corrects` against the original.

---

## Elements changed

| File | Change |
|---|---|
| [logs/improvement-log.jsonl#L317](logs/improvement-log.jsonl#L317) | `deferred_reason` + `revisit_when` added to the accepted finding |
| [contract/known-exceptions.json#L41](contract/known-exceptions.json#L41) | `EX-004` added; `_gate_scope_note` added at [#L53](contract/known-exceptions.json#L53) |
| [logs/improvement-log.jsonl#L319](logs/improvement-log.jsonl#L319) | one finding appended, correcting the accepted one |
| [logs/known-failure-modes.md](logs/known-failure-modes.md) | regenerated; `--check` exits 0 |
| [logs/state/wbs-state.json](logs/state/wbs-state.json) | regenerated — it was already stale against 12 files before this change, and the exception gate refuses to report over a stale cache |

Nothing in `constraints/`, `skills/`, `knowledge/`, `agents/` or `scripts/` was changed.

---

## What the re-verification found

The finding's **factual core is exactly right** and was confirmed independently against solution
source: six read actions across the two named flows carry no Secure Outputs setting. The risk the
reviewer accepted is real and correctly counted.

Three things about it are **wrong or incomplete**, which is why a second finding was logged:

**The gate does not exist.** The finding describes a Secure-Outputs check it added as "check 5" to
[scripts/verify-flow-definition-language.py](scripts/verify-flow-definition-language.py#L29). That
file is unmodified against `HEAD`, its own header declares **three** checks rather than the four
the finding credits it with, and the setting name it would look for appears nowhere under
`scripts/`. So no gate anywhere in this repository can currently see this gap, or confirm it fixed
later.

**The exposed surface is wider than reported.** Five *write* actions against the same personal-data
tables are also unprotected — three in the intake flow and two in the scoring flow — so eleven
actions across **three** flows are involved, not six across two. The third flow is not named in the
accepted finding or in the reviewer's decision.

**One flow does set it.** The round-statistics flow protects its read, which confirms the finding's
own conclusion that this control was applied by hand, flow by flow, with nothing enforcing it.

`EX-004`'s clearing action is written against this reality: the check must be **built** before it
can be wired in, and that is named as step 1 of two.

---

## What is still open

**The two held builds are still held.** Clearing the accepted finding removed the critical-severity
trigger, but logging what the re-verification found put the queue back to exactly ten unread
entries, which is the batch threshold in
[C-TECH-061](constraints/technology/technology-constraints.md#L131). The check the builds wait on
therefore still exits 1.

**The digest now carries a false statement.** [logs/known-failure-modes.md#L227](logs/known-failure-modes.md#L227)
renders the accepted finding's lesson verbatim, including its claim that the Secure-Outputs gate
exists, while the correction is capped out of its own section at
[#L473](logs/known-failure-modes.md#L473). Every agent that reads the digest is currently told a
gate exists that does not. Fixing this properly means changing the generator so a correction
surfaces beside what it corrects — a system change that needs `APPROVE IMPROVEMENTS`, so it was not
done here.

**Two unrelated entries are cited by an earlier review and carry no stamp.** The log check warns
about both. Stamping them is that review's business, not this record's, and doing it would move
them into a state that still counts toward the same threshold.

**This file now holds its first technology-gate exception.** `C-COM-010` is written for commercial
gates and its wording was not widened; the reasoning is recorded at
[contract/known-exceptions.json#L53](contract/known-exceptions.json#L53) as an altitude call for
the next review.

---

## What you need to decide

**ANSWERED 2026-08-25 — Do you also accept the newly logged finding for now, under the same
reasoning?** Yes. The reviewer replied *"My answer about the service account for the workflow
exposure still stands,"* extending the acceptance to the correcting finding. It is recorded as a
`deferred_reason` + `revisit_when` on that finding at
[logs/improvement-log.jsonl#L319](logs/improvement-log.jsonl#L319); the queue moved from ten unread
to nine and [scripts/verify-improvement-log.py](scripts/verify-improvement-log.py) now exits 0, so
the two held builds are released. `EX-004` was deliberately left untouched — see the still-open
question below. The acceptance covers the **exposure** (the instance half); the **class** half of
that finding's `proposed_change` — requiring an `evidence_grep` on any finding asserting it built a
named file — is not risk-accepted and still goes to the next improvement review.

Recording your acceptance on it would put the queue at nine unread and let both held builds run. It
is the same subject matter you just decided on — the missing gate is part of the gap you accepted —
but it is new information you have not seen, so it is not mine to defer on your behalf.

The alternative is a proper improvement review over the ten unread entries, which clears the
threshold proprly rather than by exception, and takes a session.

**STILL OPEN. Separately, and not blocking: do you want the five unprotected write actions added to
the exception's scope?**

Your decision covered the six reads that were reported to you. If the eventual change order is
meant to close the whole exposure rather than the reported part of it, `EX-004` should say eleven
actions across three flows now, while it is being written rather than at expiry.

---

Verified: the exception gate passes with 0 violations and 4 accepted exceptions; the digest
`--check` exits 0; the accepted finding no longer trips the critical-severity trigger; the six
reported violations were re-counted from solution source and match exactly.

Not verified: nothing was run against a live environment, so the actual run-history exposure was
not observed — the count comes from solution source. No Secure-Outputs gate was built or executed,
because none exists.
