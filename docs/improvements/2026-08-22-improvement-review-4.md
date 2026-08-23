# Improvement Review 12 — 2026-08-22

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 6 → 4 clusters (2 unread, 3 approved-not-applied, 1 constraint repair)
**Trigger:** reviewer decision on review 9's one open item, plus two new findings (one `blocker`)
**Gate:** `APPROVE IMPROVEMENTS`
**WBS:** `system`. The findings guard delivery tasks 6.1–6.5. No contracted task is claimed here.

**Status:** ~~AWAITING `APPROVE IMPROVEMENTS`.~~
**APPROVED and APPLIED 2026-08-22** — the reviewer's instruction carried the decision itself. See section 6.

---

## The headline

**The reviewer chose to narrow `C-TECH-064` rather than build the canary probe, and nothing is lost
by it.** The clause now names [verify-test-data.ps1](../../provisioning/dataverse/verify-test-data.ps1),
which already existed, already asserts exactly what the clause demands, and is the script that
caught the failure the clause was written for. The repository's first *unsatisfiable* HARD rule is
gone, and [verify-constraint-verifiers.py](../../scripts/verify-constraint-verifiers.py) now passes
on all 61 paths across 73 active rows.

**Two of the three "approved but never applied" items needed no implementation at all — they needed
checking.** `IMP-0166` asked for either a real role id or an owned exception; the role id had
already been substituted and declared, and the gate passes, so writing `EX-004` would have
documented a red gate that no longer exists. Its evidence needle had been pointing at the wrong
artefact all along.

**The blocker corrects a recommendation this system had been giving with confidence.** The standing
advice on *"Invalid organization URL 'null' provided"* was to raise a Microsoft support ticket
because every local cause was exhausted. They were not: passing `-u/--org-url` fixes it, and none
of the six findings in that diagnosis had tried it.

---

## 1. The reviewer's decision, and what it settled

> *Narrow `C-TECH-064`'s clause rather than build the canary probe. This should also close
> `IMP-0148` — confirm that before marking it APPLIED rather than assuming the two are identical.*

**Confirmed, and they are not identical.** The narrowing closes `IMP-0148` as an improvement item,
and two things it names remain open. Recording the split rather than letting an APPLIED status
imply more than it earned:

| | Settled by the narrowing | Still open |
|---|---|---|
| The **approval** — review 5's canary probe, its smoke-test wiring, the probe row | **Withdrawn** by reviewer decision. No artefact is owed, and the entry leaves the `approved-not-applied` state | — |
| The **admissible-evidence question** the finding raised | Answered: `verify-test-data.ps1` fails any seeded row whose `rev_scoredon` is empty | — |
| The finding's **own `proposed_change`** — seed one probe row, assert, *then* load the other eleven | — | **Not applied.** It is an efficiency gain (fail after 1 wasted row instead of 12), not a correctness gate, since `verify-test-data.ps1` fails the batch either way. Left as a delivery-script proposal |
| The **live defect** | — | **Unresolved.** The scoring flow did not fire for any of 12 rows in TST/ACC, and [the walkthrough report](../../docs/tests/acc-walkthrough-data-test-report.md#L55) still records 12 of 12 FAIL. It needs a human with maker access to TST/ACC, which no identity used by this project's scripts has. Not a rule change; improvement-agent cannot close it |

---

## 2. Clusters and promotion decisions

```
CLUSTER A: an unsatisfiable HARD constraint  (IMP-0184; instance IMP-0148)
Altitude:  INSTANCE, by reviewer decision, and the class fix already shipped. The class —
           declared-policy-not-mechanically-enforced, x4 — got its gate in review 9
           (verify-constraint-verifiers.py). What was left was the single row that gate
           was red on, and a red gate with one known cause is a repair, not a promotion.
Ladder row: "a platform law, or a third instance" was already spent; this is the cleanup.
Becomes:   C-TECH-064's flow-trigger clause names verify-test-data.ps1 instead of a script
           nobody wrote. The PRINCIPLE is untouched: metadata assertions (statecode, a
           callbackregistration's existence or createdon, subscriptionRequest/scope, runas)
           and Resubmit runs remain inadmissible.
Retires:   the canary-probe requirement, and with it review 5's items 1-3.
Cites:     IMP-0184, IMP-0148
Residual:  verify-test-data.ps1 is not wired into any pipeline `verification:` block, so it
           runs when somebody runs it. That is IMP-0174's rung (present but never executed),
           not this one, and verify-constraint-verifiers.py cannot see it — the script's own
           docstring says so. Named here rather than quietly fixed.
```

```
CLUSTER B: a tier nobody argued for  (IMP-0162)
Altitude:  CLASS on the read path. The instance is two missing YAML blocks; the class is that
           a missing escalation rule FAILS SILENTLY — the work runs on a cheaper model and
           nobody is told. Prose cannot fix a silent failure.
Ladder row: "a tool could catch it mechanically" + "the system's own memory failed".
Becomes:   the conditions themselves, plus a generate-subagents.py --check rule that fails
           when a sub_agent has no rationale, or declares neither escalate_to_strategic_when
           nor an explicit no_escalation_because.
Retires:   nothing.
Cites:     IMP-0162
Residual:  the check proves a tier was ARGUED, never that the argument is right. It cannot
           know that ADR-003 added an artefact type this agent owns — that judgement stays
           human. It found two further real gaps on its first run, which is the evidence it
           discriminates.
```

```
CLUSTER C: the org-url-null defect  (IMP-0208 blocker, IMP-0209)
Altitude:  INSTANCE → knowledge. Both are one root cause: the CLI passes the organisation URL
           through as null unless -u supplies it. No gate in this repository can reach a
           vendor CLI's argument resolution.
Ladder row: "one instance, but the cause is general and a human needs to know it".
Becomes:   code-apps.md's diagnostic step 2 becomes the confirmed fix; step 5 RETRACTS the
           escalate-to-Microsoft recommendation for this symptom; the "typed route is
           unreachable" conclusion is corrected in place.
Retires:   two standing recommendations, both wrong: "escalate to Microsoft support" and
           "the per-table typed route is closed in this environment".
Cites:     IMP-0208, IMP-0209, IMP-0191, IMP-0192, IMP-0161
Residual:  `pa connection list-datasets` / `list-tables` take no org-url flag and still fail,
           so that route stays closed — and their failure must not be read as a broken
           connection. Recorded in the file.
```

```
CLUSTER D: a placeholder that was already substituted  (IMP-0166)
Altitude:  NONE. No rule change, and saying so is the point.
Ladder row: the ladder's top row — "Nothing. It stays a log note."
Becomes:   a corrected evidence needle. The work was done before this review opened.
Retires:   the EX-004 proposal, unbuilt: an exception recording a deliberately-red gate would
           have documented a state that no longer exists.
Cites:     IMP-0166
Residual:  known-exceptions.json is still scoped in its _purpose to commercial gates, so a
           deliberately-red BUILD gate still has no home there. Review 7 judged that widening
           superseded and this review does not reopen it — but the gap is real and unowned.
```

---

## 3. Changes applied

| # | Type | Target | Change |
|---|---|---|---|
| 1 | constraint | [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) | Flow-trigger clause narrowed to name `verify-test-data.ps1`. Principle unchanged; canary probe withdrawn |
| 2 | config | [models.yml](../../config/models.yml#L246) | `frontend-agent` gains a rationale + 4 escalation conditions; `backend-agent` a rationale + 3; `automation-agent` a rationale + 1 more; `config-agent` an explicit `no_escalation_because` |
| 3 | script | [generate-subagents.py](../../scripts/generate-subagents.py#L280) | `--check` fails on a sub-agent with no rationale, or with neither escalation conditions nor a stated reason |
| 4 | knowledge | [code-apps.md](../../knowledge/technology/code-apps.md#L177) | `-u/--org-url` documented as the confirmed fix; the Microsoft-support recommendation retracted for this symptom; the per-table typed route corrected from "unreachable" |
| 5 | doc | [dev summary](../../docs/development/revitalise-grant-automation-dev-summary.md#L4861) | `A-TR-6`'s register row closed at E1 — it read as an open E4 guess while §11 asserted twice that no register change was needed |

**Constraint budget: 0 of 3 used.** One existing row narrowed; no new rule.

---

## 4. Retirements

**Three, and they are real retirements rather than a nil return.**

1. **The canary-probe requirement** in `C-TECH-064`, with review 5's items 1–3. Coverage is not
   lost: `verify-test-data.ps1` makes the same assertion, and it is the script that caught the
   defect the clause exists for.
2. **"Escalate to Microsoft support"** for `Invalid organization URL 'null'`. Retired because it was
   wrong, not because it was stale.
3. **"The per-table typed Dataverse route is unreachable in this environment."** Same root cause.

**The standing consolidation candidate is unchanged and again not taken** —
[C-TECH-001](../../constraints/technology/technology-constraints.md#L34),
[C-TECH-002](../../constraints/technology/technology-constraints.md#L35) and
[C-TECH-044](../../constraints/technology/technology-constraints.md#L86). The backlog is now small
enough that the next review has no excuse for deferring it again.

---

## 5. Findings left unprocessed

No silent caps.

| Finding(s) | Why not processed | What closes it |
|---|---|---|
| `IMP-0197`, `IMP-0205` | **Untouched by explicit instruction.** Review 11's item 2 stays held: whether `power.config.json`'s `environmentId`/`appId` is a `C-TECH-047` breach or a sanctioned exception is still *"not sure yet"*, and guessing it is what the item exists to prevent | the reviewer's answer to that one question |
| `IMP-0198` | Parked at review 10's gate | the keyword against that document |
| `IMP-0112`, `IMP-0152` | Standing deferrals, reasons unchanged | as recorded on each |

---

## 6. Applied

`APPROVE IMPROVEMENTS` received 2026-08-22 with the decision embedded in the instruction.

**Entries moved to APPLIED:** `IMP-0148`, `IMP-0162`, `IMP-0166`, `IMP-0184`, `IMP-0208`, `IMP-0209`
— six, each with an `evidence_grep` needle, as required for anything applied from review 8 onward.

**Entries rejected:** none.

**Two things found while applying, both reported rather than absorbed:**

The `generate-subagents.py` check found **two gaps beyond the one it was written for** —
`automation-agent` had no rationale and `config-agent` had neither conditions nor a stated reason.
Both filled.

`A-TR-6`'s register row still read as an open `E4` guess while §11 of the same document recorded
its closure twice and stated *"no register change needed"*. The narrative and the register had
drifted — `IMP-0140`'s class, one level up.

**Gate state after applying:** `verify-constraint-verifiers.py` PASS (61 paths, 73 rows) where it
was red on one; `generate-subagents.py --check` current at 18 files; `verify-toolchain-claims.py`
PASS (43 claims); log gate reports **0 unread and 0 approved-not-applied** for the first time.
